"""Every animated quantity as a pure function of screen time s (seconds), so any frame renders alone.

Two clocks:
    s  screen time, 0 … 30 s
    T  physical time relative to core bounce (s), from astro.py, shown in the HUD

T(s) is a monotone PCHIP through event keys in y = asinh(T / 0.05 s), so it is log-like far from the
bounce (fast forward) and linear near it (slow motion). Every key is a physical event time.

Camera: always looks at the star's centre from direction n(s), at distance D(s) (km). D is built
from physics where it matters: it rides the shock (3.2 R_sh) and then the ejecta (6 R_ej).
All lengths go to the GPU divided by D, so 18 decades of zoom never lose float precision.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

import astro as A

DURATION = 30.0
TAU0 = 0.05                     # s: the asinh clock's linear-to-log scale

# ── screen beats (s) ──────────────────────────────────────────────────────────
# Everything is seen from outside: the collapse happens unseen inside a calm star; the viewer sees
# the neutrino burst and the gravitational ripples leave it, then two days later the breakout.
S_ONSET = 5.0                    # collapse begins (hidden)
S_BOUNCE = 6.5
S_BH = 8.0
S_BREAKOUT = 12.8
S_REMNANT = 23.0                 # clock lands at 300 yr; the dive to the hole begins

_KEYS = [
    (-5.0, -24 * A.DAY),         # lead-in key (off screen) so the opening rate isn't an endpoint artefact
    (0.0, -A.T_SI_BURN),
    (S_ONSET, -A.T_COLLAPSE),
    (S_BOUNCE, 0.0),
    (S_BH, A.T_BH),
    (S_BREAKOUT, A.T_BREAKOUT),
    (S_REMNANT, A.T_END),
    (DURATION, A.T_END),         # flat in y: the fast-forward decelerates smoothly to a stop
]
_S = np.array([k[0] for k in _KEYS])
_Y = np.arcsinh(np.array([k[1] for k in _KEYS]) / TAU0)
_CLOCK = PchipInterpolator(_S, _Y)


def T_of(s):
    """Physical time (s) at screen time s. After the landing the clock runs in real time (×1)."""
    s = float(np.clip(s, 0.0, DURATION))
    T = float(TAU0 * np.sinh(_CLOCK(s)))
    if s > S_REMNANT:
        T = A.T_END + (s - S_REMNANT)
    return T


def rate_of(s, h=1e-3):
    """Clock rate dT/ds (how many physical seconds pass per screen second)."""
    a, b = max(s - h, 0.0), min(s + h, DURATION)
    return max((T_of(b) - T_of(a)) / (b - a), 1.0 if s > S_REMNANT else 0.0)


# ── easing ────────────────────────────────────────────────────────────────────
def smoother(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


def ramp(s, a, b, ease=smoother):
    return float(ease((s - a) / (b - a)))


def lerp(a, b, w):
    return a + (b - a) * w


# ── camera distance D(s) in km ────────────────────────────────────────────────
KM = A.KM
RS_KM = A.R_STAR / KM
D_END = 45.0 * A.r_grav(A.M_BH) / KM      # 45 M from the hole
D_FINAL = 40.0 * A.r_grav(A.M_BH) / KM

# approach keys (s, D / R_star): wide → slow push → close, grazing the limb while the shock travels
_APPROACH = np.array([[0.0, 4.6], [S_BOUNCE, 3.3], [S_BH + 1.5, 2.9], [11.6, 1.75], [S_BREAKOUT, 1.62], [30.0, 1.5]])
_APPROACH_I = PchipInterpolator(_APPROACH[:, 0], np.log(_APPROACH[:, 1]))


def _logD_parts(s):
    T = T_of(s)
    L = {}
    L["approach"] = float(_APPROACH_I(min(s, 30.0))) + np.log(RS_KM)
    # pushed back by the blast: just ahead of the photosphere, then easing out to a 6 R_ej framing
    L["ejecta"] = np.log(lerp(1.72, 6.0, ramp(s, S_BREAKOUT, S_BREAKOUT + 3.8)) * A.ejecta_radius(T) / KM)
    r_end = 6.0 * A.ejecta_radius(A.T_END) / KM
    L["plunge"] = lerp(np.log(r_end), np.log(D_END), ramp(s, S_REMNANT, 28.3))
    L["settle"] = lerp(np.log(D_END), np.log(D_FINAL), ramp(s, 28.3, DURATION))
    return L


# (segment, blend-in window): each segment takes over from the previous one across its window
_SEGMENTS = [("approach", None), ("ejecta", (S_BREAKOUT - 0.05, S_BREAKOUT + 0.35)),
             ("plunge", (S_REMNANT, S_REMNANT + 0.01)), ("settle", (28.3, 28.31))]


def log_distance(s):
    L = _logD_parts(s)
    v = L["approach"]
    for name, win in _SEGMENTS[1:]:
        v = lerp(v, L[name], ramp(s, *win))
    return float(v)


def distance_km(s):
    return float(np.exp(log_distance(s)))


# ── camera orientation: orbit (azimuth, elevation) + look offsets (yaw, pitch) ────
VFOV = np.radians(36.0)
# s, azimuth°, elevation°, yaw°, pitch°   (yaw/pitch turn the view off the centre: the limb shot)
_ORIENT = np.array([
    [0.0,   -24.0,  9.0,   0.0,  0.0],
    [S_BOUNCE, -10.0, 6.0, 0.0,  0.0],
    [S_BH + 1.6, -2.0, 4.0, 0.0, 0.0],
    [11.8,    10.0,  2.0,  27.0, 7.0],
    [S_BREAKOUT, 13.0, 1.5, 29.0, 7.5],
    [S_BREAKOUT + 1.8, 18.0, 2.5, 0.0, 0.0],
    [S_REMNANT, 30.0, 5.0,  0.0,  0.0],
    [27.5,    40.0,  4.5,  0.0,  0.0],
    [DURATION, 58.0, 4.0,  0.0,  0.0],
])
_ORIENT_I = PchipInterpolator(_ORIENT[:, 0], np.radians(_ORIENT[:, 1:]), axis=0)


def _rot(v, axis, ang):
    axis = axis / np.linalg.norm(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


def camera(s):
    """Unit direction of the camera from the centre, and its right/up/forward basis."""
    az, el, yaw, pitch = _ORIENT_I(float(np.clip(s, 0.0, DURATION)))
    n = np.array([np.cos(el) * np.sin(az), np.sin(el), np.cos(el) * np.cos(az)])
    upw = np.array([0.0, 1.0, 0.0])
    fwd = -n
    right = np.cross(fwd, upw); right /= np.linalg.norm(right)
    fwd = _rot(fwd, upw, -yaw)
    right = np.cross(fwd, upw); right /= np.linalg.norm(right)
    fwd = _rot(fwd, right, pitch)
    up = np.cross(right, fwd)
    return n, right, up, fwd, VFOV


def screen_dir(s, x, y):
    """Sky direction that appears at screen position (x, y) ∈ [-1, 1] at time s."""
    n, right, up, fwd, fov = camera(s)
    th = np.tan(fov / 2)
    v = fwd + x * th * 16 / 9 * right + y * th * up
    return v / np.linalg.norm(v)


# ── scene parameters ──────────────────────────────────────────────────────────
def params(s):
    T = T_of(s)
    D = distance_km(s) * KM          # cm
    P = {"s": s, "T": T, "D_km": D / KM}
    # cut-away: the octant facing the camera is carved from the surface to the centre
    P["cut"] = 1e30                  # no cut-away: the star is only ever seen from outside
    # shells (outer radii), collapsing in free fall before bounce
    if T < 0:
        radii = [A.infall_radius(r0, T) for r0 in A.R_SHELL]
    else:
        radii = [A.infall_radius(r0, -1e-9) for r0 in A.R_SHELL]
        radii[0] = A.core_radius(T)
    radii[-1] = A.R_STAR
    P["shells"] = [r / D for r in radii]
    P["Rs"] = A.R_STAR / D
    # core: 0 iron, 1 proto-neutron star, 2 black hole
    if T < 0:
        P["core_mode"], P["core"] = 0.0, A.core_radius(T) / D
    elif T < A.T_BH:
        P["core_mode"], P["core"] = 1.0, A.core_radius(T) / D
    else:
        P["core_mode"], P["core"] = 2.0, 0.0
    M_bh = min(A.pns_mass(T), A.M_BH) if T >= A.T_BH else 0.0
    P["shadow"] = 0.0                # hidden inside the star; the lens pass draws it at the end
    P["core"], P["core_mode"] = 0.0, 0.0
    # core heat: compression brightens the falling iron; the bounce flash; the PNS glow
    P["core_heat"] = 1.0 + 6.0 * ramp(T, -0.03, 0.0) if T < 0 else 1.0
    P["bounce_flash"] = 0.0
    # shock
    P["shock"] = A.shock_radius(T) / D if T > 0 else 0.0
    P["stalled"] = 1.0 if 0.012 < T < A.T_REVIVE else 0.0
    P["sasi_amp"] = 0.16 * ramp(T, 0.02, 0.12) * (1.0 - ramp(T, A.T_REVIVE - 0.05, A.T_REVIVE + 0.1))
    P["sasi_phase"] = 2 * np.pi * T / 0.040 if T > 0 else 0.0     # SASI period ≈ 40 ms
    P["post_shock"] = ramp(T, 0.0, 0.01) if T > 0 else 0.0
    P["star_on"] = 1.0 - ramp(s - S_BREAKOUT, 0.15, 0.45)       # hidden inside the opaque ejecta by then
    # surface
    P["Teff"] = A.T_EFF
    bo = s - S_BREAKOUT
    P["flash"] = (ramp(bo, -0.12, 0.0) * np.exp(-max(bo, 0.0) / 0.35)) if bo > -0.12 else 0.0
    # ejecta photosphere and remnant
    if T > A.T_BREAKOUT:
        P["ej"] = A.ejecta_radius(T) / D
        P["ej_T"] = A.photosphere_temperature(T)
        P["ej_op"] = A.photosphere_opacity(T) * ramp(bo, 0.0, 0.25)
        # surface brightness rises with temperature (∝ T^4 tamed for display)
        P["ej_I"] = (P["ej_T"] / 6000.0) ** 1.6
    else:
        P["ej"], P["ej_T"], P["ej_op"], P["ej_I"] = 0.0, 6000.0, 0.0, 0.0
    P["blast"] = float(np.exp(-(s - S_BREAKOUT) / 1.4)) * ramp(s, S_BREAKOUT, S_BREAKOUT + 0.15) if s > S_BREAKOUT else 0.0
    t_after = max(T - A.T_BREAKOUT, 0.0)
    nebular = ramp(np.log10(max(t_after, 1.0)), np.log10(80 * A.DAY), np.log10(160 * A.DAY))
    nebular *= 1.0 - ramp(np.log10(max(t_after, 1.0)), np.log10(1.5 * A.YR), np.log10(8 * A.YR))
    P["rem"] = A.ejecta_radius(T) / D if T > A.T_BREAKOUT else 0.0
    P["rem_neb"] = 0.9 * nebular
    P["rem_glow"] = A.remnant_glow(T) * (1.0 - 0.9 * ramp(s, S_REMNANT + 0.3, S_REMNANT + 2.1))    # dim from inside: stars stay readable
    # once the camera is inside the remnant, it is "at infinity" for the tracer
    # neutrino streaks (screen time window = bounce → black hole birth)
    P["nu_on"] = 1.0 if S_BOUNCE <= s < S_BH + 2.5 else 0.0
    # lensing: from the dive into the remnant on (sub-pixel before)
    P["lens"] = 1.0 if s > S_REMNANT else 0.0
    P["rcM"] = D / A.r_grav(A.M_BH)
    # background objects
    P["sky"] = 1.0
    P["pulsar"] = ramp(s, 0.3, 1.8) * (1.0 - ramp(s, S_REMNANT + 1.5, S_REMNANT + 2.5))
    P["T_yr"] = T / A.YR
    # exposure (a hand-keyed "auto exposure", like a camera operator riding the iris)
    P["exposure"] = exposure(s)
    P["fade"] = ramp(s, 0.0, 0.8) * (1.0 - ramp(s, DURATION - 0.7, DURATION))
    return P


_EXPO = np.array([
    [0.0, 1.00], [S_BH + 1.5, 1.00], [11.6, 0.95], [S_BREAKOUT - 0.1, 0.95], [S_BREAKOUT + 0.4, 0.22],
    [S_BREAKOUT + 1.8, 0.35], [16.5, 0.55], [19.0, 0.85], [S_REMNANT, 1.10], [26.0, 1.30], [30.0, 1.30],
])
_EXPO_I = PchipInterpolator(_EXPO[:, 0], np.log(_EXPO[:, 1]))


def exposure(s):
    return float(np.exp(_EXPO_I(np.clip(s, 0.0, DURATION))))


# ── gravitational-wave rings (screen-space, stylised speed): bounce and black-hole birth ──
GW_RINGS = [  # emission time, amplitude, ring speed (tan units / s), packet width
    (S_BOUNCE, 0.020, 1.0, 0.07),
    (S_BH, 0.045, 0.85, 0.09),
]


def gw_rings(s):
    out = []
    for s0, amp, v, w in GW_RINGS:
        age = s - s0
        if 0.0 <= age < 2.2:
            out.append((v * age, amp * (1.0 - ramp(age, 1.2, 2.2)) * ramp(age, 0.0, 0.08), w))
        else:
            out.append((0.0, 0.0, w))
    return out


if __name__ == "__main__":
    for s in (0, 2, 5, 7, 9, 10, 10.5, 10.9, 11, 11.5, 12.3, 13.3, 14, 15, 17, 19, 20, 22, 24.5, 26, 28.3, 30):
        T, D = T_of(s), distance_km(s)
        print(f"s={s:5.1f}  T={T:+.4g} s  rate=×{rate_of(s):.3g}  D={D:.4g} km  "
              f"shock/D={A.shock_radius(T) * 1 / (D * KM) if T > 0 else 0:.3g}")
