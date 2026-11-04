"""The physical scenario: a 25 M☉ red supergiant → fallback supernova → 6 M☉ black hole.

Every number the scene shows (the clock, shell sizes, the shock's position, the photosphere's
temperature, the black hole's shadow) comes from here. CGS units unless a name says otherwise.
`python astro.py` prints the key numbers and runs the checks (they also run on import).

Model choices (representative, not a stellar-evolution code):
  * pre-supernova onion: shell radii and masses typical of a 25 M☉ (ZAMS) model at collapse
    (Woosley, Heger & Weaver 2002 scale); uniform density inside each shell
  * core collapse: pressureless free fall (the cycloid r = r0 cos²η) with an effective mass
    tuned so the iron core reaches the bounce radius in the simulated ≈ 0.3 s. Plain free fall
    with the real mass would take ~0.13 s; pressure support slows it ~2×, which the check bounds
  * shock: stalled at ≈150 km until revival at +0.3 s, then the Matzner & McKee (1999) speed
    v = 0.794 (E/m)^½ (ρ r³ / m)^−0.19, capped at 0.1 c, integrated to the surface → breakout time
  * fallback: toy accretion Ṁ = Ṁ0 / (1 + t/τ) onto the proto-neutron star until it passes
    M_max = 2.3 M☉ → black hole; it keeps growing to the final 6 M☉ over hours
  * ejecta: homologous free expansion at v = √(10E / 3M_ej); the photosphere follows a type II-P
    temperature curve (hot early, a ≈6000 K hydrogen-recombination plateau to ~110 d)
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

G = 6.674e-8
C = 2.998e10
MSUN = 1.989e33
RSUN = 6.957e10
KM = 1e5
DAY = 86400.0
YR = 3.156e7
LY = 9.461e17

# ── progenitor ────────────────────────────────────────────────────────────────
M_ZAMS = 25.0
M_PRESN = 18.0                 # after winds
R_STAR = 900.0 * RSUN          # red supergiant ≈ 6.3e8 km ≈ 4.2 AU
T_EFF = 3600.0                 # K

# onion shells: name, outer radius (cm), enclosed mass at that radius (M☉), display colour (linear RGB)
SHELLS = [
    ("Fe",       1.5e3 * KM, 1.80, (0.78, 0.78, 0.84)),
    ("Si-S",     4.0e3 * KM, 2.30, (0.30, 0.58, 1.00)),
    ("O-Ne-Mg",  2.0e4 * KM, 4.50, (0.30, 0.92, 0.50)),
    ("C-O",      6.0e4 * KM, 6.00, (1.00, 0.86, 0.30)),
    ("He",       7.0e5 * KM, 8.00, (1.00, 0.52, 0.16)),
    ("H",        R_STAR,     M_PRESN, (0.85, 0.16, 0.08)),
]
R_SHELL = np.array([s[1] for s in SHELLS])
M_SHELL = np.array([s[2] for s in SHELLS]) * MSUN


def enclosed_mass(r):
    """M(<r) with uniform density inside each shell."""
    r = np.asarray(r, float)
    r_in = np.concatenate([[0.0], R_SHELL[:-1]])
    m_in = np.concatenate([[0.0], M_SHELL[:-1]])
    i = np.clip(np.searchsorted(R_SHELL, r), 0, len(SHELLS) - 1)
    f = (r**3 - r_in[i] ** 3) / (R_SHELL[i] ** 3 - r_in[i] ** 3)
    return m_in[i] + np.clip(f, 0, 1) * (M_SHELL[i] - m_in[i])


def density(r):
    r = np.asarray(r, float)
    r_in = np.concatenate([[0.0], R_SHELL[:-1]])
    m_in = np.concatenate([[0.0], M_SHELL[:-1]])
    i = np.clip(np.searchsorted(R_SHELL, r), 0, len(SHELLS) - 1)
    return (M_SHELL[i] - m_in[i]) / (4 / 3 * np.pi * (R_SHELL[i] ** 3 - r_in[i] ** 3))


# ── pre-collapse countdown ──────────────────────────────────────────────────────
T_SI_BURN = 1.0 * DAY          # silicon burning lasts ≈ 1 day for a 25 M☉ star: the clock starts here

# ── core collapse ─────────────────────────────────────────────────────────────
T_COLLAPSE = 0.30              # s, instability → bounce (simulations)
R_FE = SHELLS[0][1]
M_FE = SHELLS[0][2] * MSUN
R_BOUNCE = 30.0 * KM           # proto-neutron star radius at bounce
RHO_NUC = 2.7e14


def _cycloid_time(r_over_r0):
    """Free-fall time in units of √(r0³ / 2GM) to fall from r0 to r (cycloid)."""
    eta = np.arccos(np.sqrt(np.clip(r_over_r0, 0.0, 1.0)))
    return eta + np.sin(eta) * np.cos(eta)


# effective mass so the iron core's edge reaches R_BOUNCE in exactly T_COLLAPSE
M_EFF = R_FE**3 / (2 * G) * (_cycloid_time(R_BOUNCE / R_FE) / T_COLLAPSE) ** 2
T_FF_REAL = np.pi / 2 * np.sqrt(R_FE**3 / (2 * G * M_FE))      # true free fall (pressureless)


def infall_radius(r0, T):
    """Radius at time T (s, ≤ 0 is before bounce) of the mass shell that started at r0.

    Every shell falls on its own cycloid under its enclosed mass, scaled by the same pressure
    factor as the iron core; the core stops at R_BOUNCE (bounce)."""
    r0 = np.asarray(r0, float)
    t = np.clip(T + T_COLLAPSE, 0.0, None)
    m = np.maximum(enclosed_mass(r0), M_FE) * (M_EFF / M_FE)
    unit = np.sqrt(r0**3 / (2 * G * m))
    tau = np.minimum(t / unit, np.pi / 2 - 1e-9)
    # invert t = η + sin η cos η by Newton iterations (monotone on [0, π/2])
    eta = np.full_like(tau, 0.5) if np.ndim(tau) else np.array(0.5)
    for _ in range(40):
        f = eta + np.sin(eta) * np.cos(eta) - tau
        eta = np.clip(eta - f / (2 * np.cos(eta) ** 2 + 1e-12), 0.0, np.pi / 2)
    return np.maximum(r0 * np.cos(eta) ** 2, R_BOUNCE * (r0 / R_FE))


def core_radius(T):
    """Iron core (→ proto-neutron star) radius."""
    if T < 0:
        return float(infall_radius(R_FE, T))
    return float(R_BOUNCE * (0.5 + 0.5 * np.exp(-T / 0.8)))      # PNS contracts 30 → 15 km


# ── shock ─────────────────────────────────────────────────────────────────────
E_EXP = 1.0e51
R_STALL = 150.0 * KM
T_REVIVE = 0.30                # s after bounce
V_CAP = 0.1 * C


def _v_mm(r):
    m = np.maximum(enclosed_mass(r) - enclosed_mass(R_STALL), 0.05 * MSUN)
    return np.minimum(0.794 * np.sqrt(E_EXP / m) * (density(r) * r**3 / m) ** -0.19, V_CAP)


def _shock_track():
    sol = solve_ivp(lambda t, y: [_v_mm(np.exp(y[0])) / np.exp(y[0])], (0.0, 1e7), [np.log(R_STALL)],
                    events=lambda t, y: y[0] - np.log(R_STAR), rtol=1e-8, atol=1e-10, dense_output=True,
                    max_step=1e4)
    return sol, float(sol.t_events[0][0])


_SHOCK, _T_PROP = _shock_track()
T_BREAKOUT = T_REVIVE + _T_PROP


def shock_radius(T):
    """Shock radius (cm) at time T after bounce."""
    if T <= 0:
        return 0.0
    if T < 0.012:                                   # bounce shock moves out to the stall radius
        return R_BOUNCE + (R_STALL - R_BOUNCE) * (T / 0.012) ** 0.5
    if T < T_REVIVE:
        return R_STALL
    if T >= T_BREAKOUT:
        return R_STAR
    return float(np.exp(_SHOCK.sol(T - T_REVIVE)[0]))


# ── fallback → black hole ───────────────────────────────────────────────────────
M_PNS0 = 1.6 * MSUN
M_MAX_NS = 2.3 * MSUN
MDOT0 = 0.8 * MSUN             # g/s
TAU_FB = 0.6


def pns_mass(T):
    return M_PNS0 + MDOT0 * TAU_FB * np.log1p(max(T, 0.0) / TAU_FB)


T_BH = TAU_FB * np.expm1((M_MAX_NS - M_PNS0) / (MDOT0 * TAU_FB))
M_BH_BIRTH = M_MAX_NS
M_BH = 6.0 * MSUN              # after the fallback is done
M_EJ = M_PRESN * MSUN - M_BH


def r_grav(M):
    return G * M / C**2        # cm: GM/c², the unit of the ray tracer


def shadow_radius(M):
    return np.sqrt(27.0) * r_grav(M)


# black-hole birth ringdown (l = 2, n = 0 Schwarzschild quasinormal mode)
F_RINGDOWN = 0.3737 / (2 * np.pi * G * M_BH_BIRTH / C**3)
TAU_RINGDOWN = (G * M_BH_BIRTH / C**3) / 0.0890

# ── neutrinos ───────────────────────────────────────────────────────────────────
E_NU = 3e53
T_NU_DIFFUSION = 10.0          # s: the burst would last this long; the black hole cuts it at T_BH

# ── ejecta and photosphere ───────────────────────────────────────────────────────
V_EJ = np.sqrt(10 * E_EXP / (3 * M_EJ))
T_PLATEAU_END = 110 * DAY
T_NEBULAR = 220 * DAY
T_END = 300 * YR               # ≈ the age of Cassiopeia A


def ejecta_radius(T):
    if T <= T_BREAKOUT:
        return R_STAR
    return R_STAR + V_EJ * (T - T_BREAKOUT)


def photosphere_temperature(T):
    """Type II-P-like: breakout flash (≳10⁵ K), cooling ∝ t^−0.55, a 6000 K plateau, then cooling."""
    t = max(T - T_BREAKOUT, 1.0)
    T_cool = 1.2e5 * (1.0 + t / 1.5e3) ** -0.42
    T_ph = max(T_cool, 6000.0)
    if T - T_BREAKOUT > T_PLATEAU_END:
        T_ph = 6000.0 * ((T - T_BREAKOUT) / T_PLATEAU_END) ** -0.6
    return float(T_ph)


def photosphere_opacity(T):
    """1 while optically thick; falls through the end of the plateau into the nebular phase."""
    x = (np.log(max(T - T_BREAKOUT, 1.0)) - np.log(T_PLATEAU_END)) / (np.log(T_NEBULAR) - np.log(T_PLATEAU_END))
    return float(1.0 - np.clip(x, 0.0, 1.0) ** 1.5)


def remnant_glow(T):
    """Reverse-shock heating lights the knots up over decades (Cas A-like at a few hundred years)."""
    x = (np.log10(max(T, 1.0)) - np.log10(3 * YR)) / (np.log10(150 * YR) - np.log10(3 * YR))
    return float(np.clip(x, 0.0, 1.0) ** 1.3)


# ── gravitational-wave sweep across the background (observed at T = (|p| + |p − cam|)/c) ──
NEB_DIST_LY = (14.0, 42.0, 70.0)
PULSAR_DIST_LY = 26.0
STAR_DIST_LY = (3.0, 140.0)    # log-uniform for the near star layer


def check():
    out = {}
    # the free-fall order of magnitude brackets the simulated collapse time
    assert 0.08 < T_FF_REAL < T_COLLAPSE < 4 * T_FF_REAL, T_FF_REAL
    # the cycloid hits the bounce radius exactly at T = 0, and is monotone
    rs = [core_radius(t) for t in np.linspace(-T_COLLAPSE, -1e-6, 50)]
    assert np.all(np.diff(rs) <= 1e-6) and abs(core_radius(-1e-9) - R_BOUNCE) / R_BOUNCE < 0.02, rs[-1]
    assert abs(core_radius(-T_COLLAPSE) - R_FE) / R_FE < 1e-6
    # bounce: the mean density of the core inside ~30 km approaches nuclear (the 0.6 M☉ homologous
    # inner core, ~12 km across, is at ≈ ρ_nuc and stiffens: that is the bounce)
    rho_b = M_FE / (4 / 3 * np.pi * R_BOUNCE**3)
    rho_inner = 0.6 * MSUN / (4 / 3 * np.pi * (12 * KM) ** 3)
    assert 0.05 * RHO_NUC < rho_b < RHO_NUC < 2 * rho_inner < 4 * RHO_NUC, (rho_b, rho_inner)
    # shell masses are monotone and add up to the pre-SN mass
    assert np.all(np.diff(M_SHELL) > 0) and abs(enclosed_mass(R_STAR) - M_PRESN * MSUN) < 1e-6 * MSUN
    # breakout between half a day and a few days (RSG)
    assert 0.5 * DAY < T_BREAKOUT < 4 * DAY, T_BREAKOUT / DAY
    # shock radius continuous and monotone
    ts = np.geomspace(1e-3, T_BREAKOUT, 400)
    rr = np.array([shock_radius(t) for t in ts])
    assert np.all(np.diff(rr) >= -1e-3 * rr[:-1]), "shock not monotone"
    # black hole forms within seconds
    assert 0.5 < T_BH < 4.0, T_BH
    assert abs(pns_mass(T_BH) - M_MAX_NS) < 1e-6 * MSUN
    # ejecta speed in the observed range for type II supernovae
    assert 2.5e8 < V_EJ < 1e9, V_EJ
    # ringdown: kHz, sub-millisecond damping
    assert 1e3 < F_RINGDOWN < 2e4 and TAU_RINGDOWN < 1e-3
    out.update(
        t_ff_real_s=T_FF_REAL, bounce_density=rho_b, t_breakout_d=T_BREAKOUT / DAY, t_bh_s=T_BH,
        v_ej_kms=V_EJ / KM, r_remnant_pc=ejecta_radius(T_END) / 3.086e18,
        r_shadow_birth_km=shadow_radius(M_BH_BIRTH) / KM, r_g_final_km=r_grav(M_BH) / KM,
        ringdown_kHz=F_RINGDOWN / 1e3, ringdown_tau_ms=TAU_RINGDOWN * 1e3,
        shock_at_1s_km=shock_radius(1.0) / KM, shock_at_1h_Rsun=shock_radius(3600.0) / RSUN,
    )
    return out


INFO = check()

if __name__ == "__main__":
    for k, v in INFO.items():
        print(f"{k:>22s}  {v:.4g}")
    for T in (-T_COLLAPSE, -0.2, -0.1, -0.03, -0.005, 0.0):
        print(f"core r(T={T:+.3f}s) = {core_radius(T) / KM:8.1f} km")
    for T in (0.5, 1, 2, 10, 60, 600, 3600, 6 * 3600, T_BREAKOUT):
        print(f"shock r(T={T:9.1f}s) = {shock_radius(T) / KM:10.3g} km")
    for d in (0.01, 1, 5, 20, 60, 110, 150, 250):
        T = T_BREAKOUT + d * DAY
        print(f"photosphere +{d:6.2f} d: {photosphere_temperature(T):8.0f} K  opacity {photosphere_opacity(T):.2f}")
