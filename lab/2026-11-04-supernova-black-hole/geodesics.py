"""Schwarzschild photon geodesics → lookup tables for the GPU ray tracer.

Units G = c = M = 1. With u = 1/r, a photon of impact parameter b obeys the orbit equation

    d²u/dφ² = 3u² − u,        u(0) = 0, u'(0) = 1/b      (arriving from infinity)

Because the metric is spherically symmetric, every photon stays in a plane through the
hole, and its whole path depends on b alone. We solve this once for every b and store:

    LUT_U   [b, φ]  u along the path, from infinity, for φ ∈ [0, PHI_MAX]
                    (after capture u climbs past 0.5; after escape u goes negative)
    LUT_PHC [b, uc] φ at which the incoming branch reaches u = uc (where the camera sits)
    PHI_END [b]     φ where the photon is captured (u = 1/2, b < √27) or escapes (u → 0)

`python geodesics.py` builds, validates and caches the tables.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = HERE / "out" / "lut_cache.npz"

B_C = np.sqrt(27.0)          # critical impact parameter = shadow edge
R_PHOTON = 3.0               # photon sphere
R_ISCO = 6.0                 # innermost stable circular orbit
R_HORIZON = 2.0

NB = 6144                    # samples in b (dense near √27)
NPHI = 2048                  # samples in φ
PHI_MAX = 4.0 * np.pi        # enough for the primary, secondary and tertiary disk images
NU = 256                     # samples of camera u, at u = U_CMAX·s² (dense for far cameras)
U_CMAX = 1.0 / 20.0          # camera never closer than r = 20
B_MIN, B_MAX = 1e-3, 2000.0  # 2000: the intro starts with the camera at r = 3000
EPS = 0.01                   # b mapping: b = B_C + EPS·sinh(y), y uniform
Y0 = float(np.arcsinh((B_MIN - B_C) / EPS))
Y1 = float(np.arcsinh((B_MAX - B_C) / EPS))
PHI_END_ORBIT = 2.0 * PHI_MAX  # sentinel: still orbiting at PHI_MAX


def b_grid() -> np.ndarray:
    return B_C + EPS * np.sinh(np.linspace(Y0, Y1, NB))


def orbit_rhs(u, w):
    return w, 3.0 * u * u - u


# ── LUT_U and PHI_END: vectorised RK4 over all b at once ─────────────────────
def build_u_table(substeps: int = 8):
    b = b_grid()
    h = PHI_MAX / ((NPHI - 1) * substeps)
    u = np.zeros(NB)
    w = 1.0 / b
    alive = np.ones(NB, bool)
    status = np.zeros(NB, np.int8)          # 0 orbiting, 1 captured, 2 escaped
    phi_end = np.full(NB, PHI_END_ORBIT)
    w_end = np.zeros(NB)
    U = np.zeros((NPHI, NB))
    phi = 0.0
    for j in range(1, NPHI):
        for _ in range(substeps):
            k1u, k1w = orbit_rhs(u, w)
            k2u, k2w = orbit_rhs(u + 0.5 * h * k1u, w + 0.5 * h * k1w)
            k3u, k3w = orbit_rhs(u + 0.5 * h * k2u, w + 0.5 * h * k2w)
            k4u, k4w = orbit_rhs(u + h * k3u, w + h * k3w)
            un = u + h / 6.0 * (k1u + 2 * k2u + 2 * k3u + k4u)
            wn = w + h / 6.0 * (k1w + 2 * k2w + 2 * k3w + k4w)
            cap = alive & (un >= 0.5)
            esc = alive & (un < 0.0)
            with np.errstate(divide="ignore", invalid="ignore"):
                fc = (0.5 - u) / (un - u)
                fe = u / (u - un)
            phi_end = np.where(cap, phi + h * fc, phi_end)
            phi_end = np.where(esc, phi + h * fe, phi_end)
            w_end = np.where(esc, wn, w_end)
            status[cap], status[esc] = 1, 2
            alive &= ~(cap | esc)
            u = np.where(alive, un, u)
            w = np.where(alive, wn, w)
            phi += h
        U[j] = u
    phis = np.linspace(0.0, PHI_MAX, NPHI)[:, None]
    past = phis > phi_end[None, :]
    cap_fill = 0.5 + (phis - phi_end[None, :])
    esc_fill = np.maximum(w_end[None, :] * (phis - phi_end[None, :]), -1.0)
    U = np.where(past & (status == 1)[None, :], cap_fill, U)
    U = np.where(past & (status == 2)[None, :], esc_fill, U)
    return b, U.astype(np.float32), phi_end.astype(np.float32), status


# ── LUT_PHC: φ on the incoming branch, by quadrature in u ───────────────────
def u_cam_grid() -> np.ndarray:
    return U_CMAX * np.linspace(0.0, 1.0, NU) ** 2


def build_phc_table(n_gauss: int = 24):
    """φ_c(b, uc) = ∫₀^uc du / √(1/b² − u² + 2u³)  (incoming branch, before periapsis).

    Gauss–Legendre in x = u/uc for every (b, uc). Beyond 0.98 of the turning point the camera
    can't see that b (α ≈ 90°, outside any frame we use), so the value is frozen there."""
    b = b_grid()
    uc = u_cam_grid()
    # turning point u_t(b): smallest root of 1/b² − u² + 2u³ in (0, 1/3); none for b < √27
    lo, hi = np.zeros(NB), np.full(NB, 1.0 / 3.0)
    R = lambda u: 1.0 / b**2 - u**2 + 2.0 * u**3          # noqa: E731
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        neg = R(mid) <= 0
        hi = np.where(neg, mid, hi)
        lo = np.where(neg, lo, mid)
    u_lim = np.where(b > B_C, 0.98 * lo, np.inf)
    x, w = np.polynomial.legendre.leggauss(n_gauss)
    x, w = 0.5 * (x + 1.0), 0.5 * w
    out = np.zeros((NU, NB))
    for j, u in enumerate(uc):
        ue = np.minimum(u, u_lim)                          # (NB,)
        uu = ue[None, :] * x[:, None]
        f = 1.0 / np.sqrt(1.0 / b[None, :] ** 2 - uu**2 + 2.0 * uu**3)
        out[j] = ue * (w @ f)
    return out.astype(np.float32)


# ── exact reference integrator (validation + overlay rays) ──────────────────
def trace_exact(b: float, phi_max: float = PHI_MAX, r_escape: float | None = None,
                max_step: float = 0.004):
    """DOP853 solution of the orbit equation from infinity. Returns (phi, u) samples
    ending at capture (u = 1/2), escape (u = 0, or r = r_escape on the way out) or phi_max."""
    from scipy.integrate import solve_ivp

    def rhs(_, y):
        return [y[1], 3 * y[0] ** 2 - y[0]]

    def ev_cap(_, y):
        return y[0] - 0.5
    ev_cap.terminal = True

    def ev_esc(phi, y):
        if phi < 1e-6 or y[1] > 0:
            return 1.0
        return y[0] - (0.0 if r_escape is None else 1.0 / r_escape)
    ev_esc.terminal = True
    ev_esc.direction = -1

    sol = solve_ivp(rhs, (0.0, phi_max), [0.0, 1.0 / b], method="DOP853", rtol=1e-11,
                    atol=1e-13, events=[ev_cap, ev_esc], max_step=max_step, dense_output=True)
    return sol


def beam_rays(bs, r_max: float, r_out: float | None = None):
    """Photon paths for a parallel beam arriving from −x, one per impact parameter
    (sign of b = side of the hole). Returns a list of (N, 2) arrays in the ray plane,
    clipped to r ≤ r_max on the way in and r ≤ r_out on the way out, ending at the horizon or on escape."""
    r_out = r_max if r_out is None else r_out
    rays = []
    for b in bs:
        ab = abs(b)
        sol = trace_exact(ab, phi_max=8 * np.pi, r_escape=r_out, max_step=0.002)
        phi = sol.t
        u = sol.y[0]
        keep = u > 1.0 / (r_max * 1.02)
        # incoming start: interpolate the exact crossing of r_max
        phi_in = phi[np.argmax(keep)]
        phis = np.concatenate([[phi_in], phi[keep]])
        us = np.concatenate([[sol.sol(phi_in)[0]], u[keep]])
        r = 1.0 / np.maximum(us, 1e-9)
        x = -r * np.cos(phis)                     # arrive from −x
        y = np.sign(b) * r * np.sin(phis)
        pts = np.stack([x, y], 1)
        # resample to roughly uniform arc length
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg)])
        n = max(int(s[-1] / 0.05), 8)
        si = np.linspace(0, s[-1], n)
        rays.append(np.stack([np.interp(si, s, pts[:, 0]), np.interp(si, s, pts[:, 1])], 1))
    return rays


# ── validation ──────────────────────────────────────────────────────────────
def validate(b, U, phi_end, status, PHC):
    from scipy.integrate import quad

    phis = np.linspace(0.0, PHI_MAX, NPHI)
    # 1) capture threshold sits at √27
    cap = status == 1
    b_last_cap, b_first_esc = b[cap].max(), b[status == 2].min()   # between: still orbiting at PHI_MAX
    assert b_last_cap < B_C < b_first_esc and b_first_esc - b_last_cap < 1e-3, (b_last_cap, b_first_esc)
    # 2) table vs exact DOP853
    worst = 0.0
    for bi in (0.5, 3.0, 5.15, 5.25, 8.0, 20.0, 50.0):
        k = int(np.argmin(abs(b - bi)))
        sol = trace_exact(float(b[k]))
        m = phis <= sol.t[-1]
        worst = max(worst, float(np.max(abs(sol.sol(phis[m])[0] - U[m, k]))))
    assert worst < 1e-6, worst
    # 3) weak-field deflection: δ = 4/b + 15π/4b² + 128/3b³ + 3465π/64b⁴ + O(b⁻⁵)
    for bi in (40.0, 60.0, 400.0, 1500.0):
        k = int(np.argmin(abs(b - bi)))
        delta = phi_end[k] - np.pi
        x = 1 / b[k]
        pred = 4 * x + 15 * np.pi / 4 * x**2 + 128 / 3 * x**3 + 3465 * np.pi / 64 * x**4
        assert abs(delta - pred) < 2e-5, (bi, delta, pred)
    # 4) camera-phase table vs adaptive quadrature (including a far camera, as in the intro)
    ucg_all = u_cam_grid()
    for bi, uc in ((5.3, 1 / 30), (12.0, 1 / 22), (2.0, 1 / 21), (800.0, 1 / 3000), (30.0, 1 / 400)):
        k = int(np.argmin(abs(b - bi)))
        j = int(np.argmin(abs(ucg_all - uc)))
        ucg = ucg_all[j]
        ref = quad(lambda x: 1 / np.sqrt(1 / b[k] ** 2 - x * x + 2 * x**3), 0, ucg, epsabs=1e-13)[0]
        assert abs(ref - PHC[j, k]) < 1e-6, (bi, ref, PHC[j, k])
    # 5) the two tables agree: u(b, φ_c(b, uc)) = uc
    k = int(np.argmin(abs(b - 7.0)))
    j = NU - 1
    uu = np.interp(PHC[j, k], phis, U[:, k])
    assert abs(uu - U_CMAX) < 1e-5, uu
    return {"b_capture_edge": (float(b_last_cap), float(b_first_esc)), "max_table_error": worst}


def load_tables(rebuild: bool = False):
    if CACHE.exists() and not rebuild:
        z = np.load(CACHE)
        return z["b"], z["U"], z["phi_end"], z["status"], z["PHC"]
    b, U, phi_end, status = build_u_table()
    PHC = build_phc_table()
    info = validate(b, U, phi_end, status, PHC)
    print("geodesic tables validated:", info)
    CACHE.parent.mkdir(exist_ok=True)
    np.savez(CACHE, b=b, U=U, phi_end=phi_end, status=status, PHC=PHC)
    return b, U, phi_end, status, PHC


if __name__ == "__main__":
    import time
    t0 = time.time()
    load_tables(rebuild=True)
    print(f"built in {time.time() - t0:.1f}s → {CACHE}")
