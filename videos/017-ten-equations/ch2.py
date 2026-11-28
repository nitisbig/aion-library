"""Chapter 2 shared pieces: the rubber-sheet picture of curved spacetime (c02_s01 and c02_s02), the precessing orbit,
and the inspiral of two black holes with the gravitational waves it sends out (c02_s03). Everything is a pure
function of absolute time.

The sheet is drawn as a grid seen in perspective by `project`, through one chapter-wide view `view(t)` (azimuth
orbit, elevation, scale, centre), so the two scenes join without a cut. Its depth is the weak-field Schwarzschild
potential, (1 − g_tt)/2 = GM/(r c²), softened inside the Sun. The marble follows a Schwarzschild geodesic,
u'' + u = M/h² + 3Mu² (u = 1/r), with M exaggerated so the orbit visibly precesses.

Example:
    from ch2 import view, sheet, sun_screen
    s.manim(z=-5).redraw(lambda t: sheet(t)[0], during=(a, b))
"""
import math
from functools import lru_cache

import numpy as np
from aion import *  # noqa: F403

from beats import T
from kit import P3, polyline, smooth01

# ------------------------------------------------------------------------------------------------ the sheet
HALF = 4.6                       # sheet half-size (sheet units)
N_LINES = 19
SOFT = 0.85                      # softening length inside the Sun
WELL = 1.75                      # depth at the centre once the Sun has settled
SUN_R = 0.62
D_PERSP = 13.0


def _ease(t, a, dur):
    return float(smooth01((t - float(a)) / dur))


def amount(t):
    """How far the sheet has sunk: 0 (flat) → 1, as the Sun settles on 'bends'."""
    return _ease(t, T.c02_s01_bends - 0.1, 2.2)


def depth(r, amt):
    """Sheet height: −WELL·amt·a/√(r² + a²), the GM/r well softened inside the Sun (a = SOFT)."""
    return -WELL * amt * SOFT / np.sqrt(r * r + SOFT * SOFT)


def view(t):
    """(azimuth, elevation, scale, cx, cy): a slow orbit; a low look along the orbit on 'straightest'; then the
    sheet drifts left and shrinks to make room for the equation (c02_s02)."""
    az = math.radians(-28.0 + 2.6 * (t - float(T.c02_s01_einstein)))
    el = 27.0 - 14.0 * _ease(t, T.c02_s01_straightest - 0.2, 2.2) + 11.0 * _ease(t, T.c02_s02 + 0.2, 1.8)
    u = _ease(t, T.c02_s02 + 0.2, 1.8)
    k = 0.98 - 0.27 * u
    cx, cy = 0.0 - 2.35 * u, -0.2 + 0.15 * u
    return az, math.radians(el), k, cx, cy


def project(x, y, z, v):
    """Sheet point(s) → screen (X, Y) and depth d (positive away from the viewer)."""
    az, el, k, cx, cy = v
    ca, sa = math.cos(az), math.sin(az)
    xr, yr = x * ca - y * sa, x * sa + y * ca
    se, ce = math.sin(el), math.cos(el)
    d = yr * ce - z * se
    p = D_PERSP / (D_PERSP + d)
    return cx + k * p * xr, cy + k * p * (yr * se + z * ce), d


def sun_z(t):
    """The Sun's centre height: dropped in from above on 'bends', resting part-sunk in the well."""
    rest = float(depth(0.0, amount(t))) + SUN_R * 0.55
    drop = _ease(t, T.c02_s01_bends - 0.6, 1.9)
    return (1 - drop) * 3.2 + drop * rest


def sun_screen(t):
    """Screen centre and diameter of the Sun sphere."""
    v = view(t)
    X, Y, d = project(0.0, 0.0, sun_z(t), v)
    return (float(X), float(Y)), 2 * SUN_R * v[2] * D_PERSP / (D_PERSP + float(d))


@lru_cache(maxsize=8)
def _sheet_cached(t, op):
    v = view(t)
    amt = amount(t)
    _, _, d_sun = project(0.0, 0.0, sun_z(t), v)
    back, front = VGroup(), VGroup()
    s = np.linspace(-HALF, HALF, 97)
    for i, c in enumerate(np.linspace(-HALF, HALF, N_LINES)):
        major = i % 2 == 0
        col, w = (C.grid, 1.7) if major else (C.grid_minor, 1.1)
        for xs, ys in ((s, np.full_like(s, c)), (np.full_like(s, c), s)):
            r = np.hypot(xs, ys)
            X, Y, d = project(xs, ys, depth(r, amt), v)
            fade = smooth01((HALF - r) / 1.7)
            for j in range(0, len(s) - 1, 8):                     # short runs so the rim can fade out
                sl = slice(j, j + 9)
                a = float(fade[sl].mean()) * op * (1.0 if major else 0.8)
                if a < 0.02:
                    continue
                seg = polyline(list(zip(X[sl], Y[sl])), col, w, a)
                (front if d[sl].mean() < d_sun else back).add(seg)
    return back, front


def sheet(t, op=1.0):
    """(back, front): the grid split by whether it lies behind or in front of the Sun's centre."""
    return _sheet_cached(round(float(t), 4), round(float(op), 3))


# ------------------------------------------------------------------------------------------------ the orbit
M_ORB, P_ORB, E_ORB = 0.055, 2.25, 0.34        # exaggerated mass, semi-latus rectum, eccentricity (sheet units)
SEC_PER_UNIT = 0.045                            # screen seconds per unit of coordinate time


@lru_cache(maxsize=1)
def _orbit_table():
    """Integrate u'' = M/h² − u + 3Mu² in φ (RK4), starting at aphelion; t(φ) from dt/dφ = r²/h."""
    h = math.sqrt(P_ORB * M_ORB)
    n, phi_max = 12000, 9 * 2 * math.pi
    dphi = phi_max / n

    def f(u, w):
        return w, M_ORB / h ** 2 - u + 3 * M_ORB * u * u

    u, w = (1 - E_ORB) / P_ORB, 0.0
    us = np.empty(n + 1)
    us[0] = u
    for i in range(n):
        k1 = f(u, w)
        k2 = f(u + dphi / 2 * k1[0], w + dphi / 2 * k1[1])
        k3 = f(u + dphi / 2 * k2[0], w + dphi / 2 * k2[1])
        k4 = f(u + dphi * k3[0], w + dphi * k3[1])
        u += dphi / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        w += dphi / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        us[i + 1] = u
    phi = np.linspace(0, phi_max, n + 1)
    r = 1 / us
    tc = np.concatenate([[0.0], np.cumsum((r[:-1] ** 2 + r[1:] ** 2) / 2 * dphi / h)])
    return phi, r, tc * SEC_PER_UNIT


def precession_deg():
    """Perihelion advance per orbit of the drawn orbit (degrees), ≈ 6πM²/h² for small M."""
    phi, r, _ = _orbit_table()
    peri = [phi[i] for i in range(1, len(r) - 1) if r[i] < r[i - 1] and r[i] <= r[i + 1]]
    return math.degrees(peri[1] - peri[0]) - 360.0


def orbit_t0():
    return float(T.c02_s01_curve) - 2.6


def marble_xy(t):
    """Marble position on the sheet at time t (seconds since it appears), angle offset so it enters at the front."""
    phi, r, tc = _orbit_table()
    tau = max(t - orbit_t0(), 0.0)
    ph = float(np.interp(tau, tc, phi))
    rr = float(np.interp(tau, tc, r))
    a = ph + math.radians(200)
    return rr * math.cos(a), rr * math.sin(a)


def orbit_path(t, span):
    """Sheet points of the marble's path over the last `span` seconds (for the trail)."""
    t0 = max(orbit_t0(), t - span)
    ts = np.linspace(t0, t, max(2, int((t - t0) * 40)))
    return np.array([marble_xy(u) for u in ts])


def marble(t, op, behind):
    """The marble (in front of or behind the Sun, so it can pass behind it) and its fading trail."""
    g = VGroup()
    if op < 0.01:
        return g
    v = view(t)
    amt = amount(t)
    x, y = marble_xy(t)
    r = math.hypot(x, y)
    X, Y, d = project(x, y, float(depth(r, amt)) + 0.11, v)
    _, _, d_sun = project(0.0, 0.0, sun_z(t), v)
    if (d > d_sun) != behind:
        return g
    path = orbit_path(t, 2.6)
    if len(path) > 2:
        rr = np.hypot(path[:, 0], path[:, 1])
        PX, PY, _ = project(path[:, 0], path[:, 1], depth(rr, amt) + 0.02, v)
        n = len(path)
        for j in range(0, n - 1, 6):
            a = op * 0.85 * ((j + 6) / n) ** 1.6
            g.add(polyline(list(zip(PX[j:j + 7], PY[j:j + 7])), C.einstein, 2.4, a))
    rad = 0.11 * v[2] * D_PERSP / (D_PERSP + d)
    g.add(Circle(radius=rad, stroke_width=0, fill_color=C.einstein, fill_opacity=op).move_to(P3(X, Y)),
          Circle(radius=rad * 0.38, stroke_width=0, fill_color=C.light, fill_opacity=0.55 * op)
          .move_to(P3(X - rad * 0.3, Y + rad * 0.3)))
    return g


# ------------------------------------------------------------------------------------------------ the inspiral
def merge_time():
    return float(T.c02_s03_merging) + 0.25


TAU0, W0, A0 = 4.0, 2 * math.pi * 0.42, 0.95    # at τ = 4 s: orbital angular speed (rad/s), separation (units)
TAU_MIN = 0.05


def orbital_phase(t):
    """Newtonian chirp: ω ∝ τ^(−3/8), so Φ(τ) = −(8/5)·ω₀·τ₀^(3/8)·τ^(5/8) with τ = t_merge − t."""
    tau = max(merge_time() - t, TAU_MIN)
    return -(8 / 5) * W0 * TAU0 ** 0.375 * tau ** 0.625


def separation(t):
    tau = max(merge_time() - t, TAU_MIN)
    return A0 * (tau / TAU0) ** 0.25


def strain(t):
    """h(t): amplitude ∝ τ^(−1/4) at twice the orbital phase; after the merger a short ringdown."""
    tm = merge_time()
    if t < tm:
        tau = max(tm - t, TAU_MIN)
        return (tau / TAU0) ** -0.25 * math.cos(2 * orbital_phase(t))
    amp = (TAU_MIN / TAU0) ** -0.25
    wr = 2 * W0 * (TAU_MIN / TAU0) ** -0.375 * 1.25
    return amp * math.exp(-(t - tm) / 0.16) * math.cos(2 * orbital_phase(tm) + wr * (t - tm))


def ripple_field(X, Y, t, center=(0.0, 0.0), speed=2.4):
    """Face-on quadrupole wave h₊ ∝ A(t_r)·cos 2(θ − Φ(t_r)) at retarded time t_r = t − r/v, falling off as 1/r
    (softened), normalised to about ±1 near the source."""
    dx, dy = X - center[0], Y - center[1]
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    tr = t - r / speed
    tm = merge_time()
    tau = np.maximum(tm - tr, TAU_MIN)
    ph = -(8 / 5) * W0 * TAU0 ** 0.375 * tau ** 0.625
    amp = (tau / TAU0) ** -0.25
    after = tr >= tm
    if after.any():
        amp_m = (TAU_MIN / TAU0) ** -0.25
        wr = W0 * (TAU_MIN / TAU0) ** -0.375 * 1.25
        ph = np.where(after, orbital_phase(tm) + wr * (tr - tm), ph)
        amp = np.where(after, amp_m * np.exp(-(tr - tm) / 0.16), amp)
    h = amp * np.cos(2 * (th - ph)) / (1 + 0.55 * r)
    return h / (TAU_MIN / TAU0) ** -0.25 * 2.2


def strain_trace(t, x0, x1, y, h_amp, t0, t1, color, width=2.6):
    """The detector's strain drawn left to right over [t0, t1], up to time t."""
    te = min(t, t1)
    if te <= t0:
        return VGroup()
    ts = np.linspace(t0, te, max(2, int((te - t0) * 160)))
    hmax = (TAU_MIN / TAU0) ** -0.25
    pts = [(x0 + (x1 - x0) * (u - t0) / (t1 - t0), y + h_amp * strain(u) / hmax) for u in ts]
    return polyline(pts, color, width)
