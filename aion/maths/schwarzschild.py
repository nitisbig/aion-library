"""Light around a non-spinning black hole: the Schwarzschild photon orbit equation.

With u = 1/r and φ the angle around the mass, a ray of light obeys

    u'' + u = (3GM/c²) u² = (3/2) r_s u²,        r_s = 2GM/c²

Everything in this module is that one equation, solved numerically. Lengths are in whatever
unit you give `rs` in (default rs = 2, i.e. G = c = M = 1). `b` is the impact parameter: how far
off-centre the ray is aimed.

    from aion.maths import schwarzschild as S
    pts, fate = S.ray(b=6.0, rs=2.0, r_max=14)     # (N, 2) path arriving from −x, "escape"
    S.deflection(b=40.0)                           # exact bend angle in radians
    S.critical_b(2.0)                              # (3√3/2) r_s: the edge of the shadow
    S.flamm(r, rs=2.0)                             # funnel height (Flamm's paraboloid)
    tables = S.load_tables()                       # lookup tables for the GPU ray tracer

`rs=0` gives a perfectly straight line (u = sin φ / b), so a scene can ramp the mass on.
`validate()` checks the tables against DOP853, the √27 capture edge and the weak-field series.
"""

from __future__ import annotations

import numpy as np

G = 6.67430e-11
C_LIGHT = 2.99792458e8
M_SUN, R_SUN = 1.98847e30, 6.957e8
M_EARTH = 5.9722e24
ARCSEC = np.pi / 180.0 / 3600.0

# ── closed forms ───────────────────────────────────────────────────────────
def schwarzschild_radius(mass_kg: float) -> float:
    """r_s = 2GM/c² in metres (Earth: 8.87 mm, Sun: 2.95 km)."""
    return 2.0 * G * mass_kg / C_LIGHT**2


def escape_velocity(mass_kg: float, r: float) -> float:
    """√(2GM/r) in m/s."""
    return float(np.sqrt(2.0 * G * mass_kg / r))


def photon_sphere(rs: float = 2.0) -> float:
    """Radius of the circular light orbit: u'' = 0 ⇒ u = (3/2) r_s u² ⇒ r = 1.5 r_s."""
    return 1.5 * rs


def critical_b(rs: float = 2.0) -> float:
    """Impact parameter dividing escape from capture: (3√3/2) r_s ≈ 2.598 r_s (the shadow edge)."""
    return 1.5 * np.sqrt(3.0) * rs


def weak_deflection(b: float, rs: float = 2.0) -> float:
    """First-order bend 2 r_s / b = 4GM/(c² b), radians. The Newtonian value is half of this."""
    return 2.0 * rs / b


def flamm(r, rs: float = 2.0):
    """Height of Flamm's paraboloid, z = 2√(r_s (r − r_s)), zero inside the horizon."""
    r = np.asarray(r, dtype=float)
    return 2.0 * np.sqrt(np.maximum(rs * (r - rs), 0.0))


# ── one ray, any mass (fast RK4: fine to call every frame) ─────────────────
def orbit(b: float, rs: float = 2.0, phi_max: float = 6.0 * np.pi, h: float = 0.004):
    """Integrate u'' + u = (3/2) r_s u² from infinity (u = 0, u' = 1/b).

    Returns (phi, u, fate), fate in {"escape", "capture", "orbit"}. The last sample is the exact
    crossing of u = 0 (escape) or u = 1/r_s (capture)."""
    k = 1.5 * rs
    u_h = np.inf if rs <= 0 else 1.0 / rs
    n = int(np.ceil(phi_max / h))
    P, U = np.empty(n + 1), np.empty(n + 1)
    u, w, phi = 0.0, 1.0 / b, 0.0
    P[0] = U[0] = 0.0
    fate, m = "orbit", n + 1
    for i in range(1, n + 1):
        k1u, k1w = w, k * u * u - u
        ua, wa = u + 0.5 * h * k1u, w + 0.5 * h * k1w
        k2u, k2w = wa, k * ua * ua - ua
        ub, wb = u + 0.5 * h * k2u, w + 0.5 * h * k2w
        k3u, k3w = wb, k * ub * ub - ub
        uc, wc = u + h * k3u, w + h * k3w
        k4u, k4w = wc, k * uc * uc - uc
        un = u + h / 6.0 * (k1u + 2 * k2u + 2 * k3u + k4u)
        wn = w + h / 6.0 * (k1w + 2 * k2w + 2 * k3w + k4w)
        if un >= u_h:
            f = (u_h - u) / (un - u)
            P[i], U[i], fate, m = phi + f * h, u_h, "capture", i + 1
            break
        if un <= 0.0:
            f = u / (u - un)
            P[i], U[i], fate, m = phi + f * h, 0.0, "escape", i + 1
            break
        u, w, phi = un, wn, phi + h
        P[i], U[i] = phi, u
    return P[:m], U[:m], fate


def ray(b: float, rs: float = 2.0, r_max: float = 14.0, r_out: float | None = None,
        phi_max: float = 6.0 * np.pi, h: float = 0.004):
    """Path of a ray arriving from −x, aimed `b` above the axis (negative b: below).

    Returns ((N, 2) points clipped to r ≤ r_max on the way in and r ≤ r_out on the way out, fate).

    Example:
        pts, fate = ray(5.3, rs=2.0, r_max=12)
    """
    r_out = r_max if r_out is None else r_out
    phi, u, fate = orbit(abs(b), rs, phi_max, h)
    i_peak = int(np.argmax(u))
    inc = np.arange(len(u)) <= i_peak
    keep = np.where(inc, u >= 1.0 / r_max, u >= 1.0 / r_out)
    if not keep.any():
        return np.zeros((0, 2)), fate
    i0, i1 = int(np.argmax(keep)), len(keep) - 1 - int(np.argmax(keep[::-1]))
    ph, uu = phi[i0:i1 + 1], u[i0:i1 + 1]

    def cross(i, j, target):                       # exact phase where u = target between samples
        f = (target - u[i]) / (u[j] - u[i])
        return phi[i] + f * (phi[j] - phi[i])

    if i0 > 0:
        ph, uu = np.r_[cross(i0 - 1, i0, 1.0 / r_max), ph], np.r_[1.0 / r_max, uu]
    if i1 < len(u) - 1:
        ph, uu = np.r_[ph, cross(i1, i1 + 1, 1.0 / r_out)], np.r_[uu, 1.0 / r_out]
    r = 1.0 / np.maximum(uu, 1e-12)
    return np.stack([-r * np.cos(ph), np.sign(b) * r * np.sin(ph)], 1), fate


def deflection(b: float, rs: float = 2.0) -> float:
    """Exact bend angle (radians) of an escaping ray: total swept angle − π. NaN if captured."""
    phi, _, fate = orbit(b, rs, phi_max=40.0 * np.pi)
    return float(phi[-1] - np.pi) if fate == "escape" else float("nan")


def sun_grazing_arcsec() -> float:
    """Bend of starlight grazing the Sun's limb, in arc seconds (≈ 1.75)."""
    return weak_deflection(R_SUN, schwarzschild_radius(M_SUN)) / ARCSEC


def geodesic_on_flamm(b: float, rs: float = 2.0, r_max: float = 14.0, h: float = 0.004):
    """Straightest path on Flamm's paraboloid (the *spatial* geometry only), from −x at offset b.

    On that surface u'² = (1 − r_s u)(1/b² − u²), so u'' + u = (3/2) r_s u² − r_s/(2b²).
    Returns (N, 3) points (x, y, z) with the funnel hanging downward (z ≤ 0, zero at r_max). In the
    weak field this bends by r_s/b; light bends by twice that, because time is curved too.

    Example:
        pts = geodesic_on_flamm(4.0, rs=2.0, r_max=12)
    """
    # in u: u'² = (1 − rs u)(1/b² − u²)  ⇒  u'' = −u + (3/2) rs u² − rs/(2 b²)
    n = int(np.ceil(4.0 * np.pi / h))
    u, ab = 1.0 / r_max, abs(b)
    w = np.sqrt(max((1.0 - rs * u) * (1.0 / ab**2 - u * u), 0.0))
    phi = np.arcsin(min(ab * u, 1.0))
    acc = lambda x: -x + 1.5 * rs * x * x - rs / (2.0 * ab * ab)      # noqa: E731
    P, U = [phi], [u]
    for _ in range(n):
        k1u, k1w = w, acc(u)
        k2u, k2w = w + 0.5 * h * k1w, acc(u + 0.5 * h * k1u)
        k3u, k3w = w + 0.5 * h * k2w, acc(u + 0.5 * h * k2u)
        k4u, k4w = w + h * k3w, acc(u + h * k3u)
        u += h / 6.0 * (k1u + 2 * k2u + 2 * k3u + k4u)
        w += h / 6.0 * (k1w + 2 * k2w + 2 * k3w + k4w)
        phi += h
        if u < 1.0 / r_max or u >= 1.0 / rs:
            break
        P.append(phi)
        U.append(u)
    P, r = np.array(P), 1.0 / np.array(U)
    return np.stack([-r * np.cos(P), np.sign(b) * r * np.sin(P), -(flamm(r_max, rs) - flamm(r, rs))], 1)


# ── lookup tables for the GPU ray tracer (units G = c = M = 1, r_s = 2) ────
B_C = float(np.sqrt(27.0))
NB, NPHI, NU = 6144, 2048, 256
PHI_MAX = 4.0 * np.pi            # enough for primary, secondary and tertiary disk images
U_CMAX = 1.0 / 20.0              # camera never closer than r = 20
B_MIN, B_MAX = 1e-3, 2000.0
EPS = 0.01                       # b = B_C + EPS·sinh(y), y uniform: dense near the critical curve
Y0 = float(np.arcsinh((B_MIN - B_C) / EPS))
Y1 = float(np.arcsinh((B_MAX - B_C) / EPS))
PHI_END_ORBIT = 2.0 * PHI_MAX    # sentinel: still orbiting at PHI_MAX


def b_grid() -> np.ndarray:
    return B_C + EPS * np.sinh(np.linspace(Y0, Y1, NB))


def u_cam_grid() -> np.ndarray:
    return U_CMAX * np.linspace(0.0, 1.0, NU) ** 2


def build_u_table(substeps: int = 8):
    """U[φ, b] along every path from infinity, plus φ_end[b] and status (1 captured, 2 escaped)."""
    b = b_grid()
    h = PHI_MAX / ((NPHI - 1) * substeps)
    u, w = np.zeros(NB), 1.0 / b
    alive = np.ones(NB, bool)
    status = np.zeros(NB, np.int8)
    phi_end = np.full(NB, PHI_END_ORBIT)
    w_end = np.zeros(NB)
    U = np.zeros((NPHI, NB))
    phi = 0.0
    f = lambda u, w: (w, 3.0 * u * u - u)                               # noqa: E731
    for j in range(1, NPHI):
        for _ in range(substeps):
            k1u, k1w = f(u, w)
            k2u, k2w = f(u + 0.5 * h * k1u, w + 0.5 * h * k1w)
            k3u, k3w = f(u + 0.5 * h * k2u, w + 0.5 * h * k2w)
            k4u, k4w = f(u + h * k3u, w + h * k3w)
            un = u + h / 6.0 * (k1u + 2 * k2u + 2 * k3u + k4u)
            wn = w + h / 6.0 * (k1w + 2 * k2w + 2 * k3w + k4w)
            cap, esc = alive & (un >= 0.5), alive & (un < 0.0)
            with np.errstate(divide="ignore", invalid="ignore"):
                fc, fe = (0.5 - u) / (un - u), u / (u - un)
            phi_end = np.where(cap, phi + h * fc, phi_end)
            phi_end = np.where(esc, phi + h * fe, phi_end)
            w_end = np.where(esc, wn, w_end)
            status[cap], status[esc] = 1, 2
            alive &= ~(cap | esc)
            u, w = np.where(alive, un, u), np.where(alive, wn, w)
            phi += h
        U[j] = u
    phis = np.linspace(0.0, PHI_MAX, NPHI)[:, None]
    past = phis > phi_end[None, :]
    U = np.where(past & (status == 1)[None, :], 0.5 + (phis - phi_end[None, :]), U)
    U = np.where(past & (status == 2)[None, :], np.maximum(w_end[None, :] * (phis - phi_end[None, :]), -1.0), U)
    return b, U.astype(np.float32), phi_end.astype(np.float32), status


def build_phc_table(n_gauss: int = 24):
    """φ_c(b, u_cam) = ∫₀^u_cam du / √(1/b² − u² + 2u³): phase at which the incoming ray reaches the camera."""
    b, uc = b_grid(), u_cam_grid()
    lo, hi = np.zeros(NB), np.full(NB, 1.0 / 3.0)
    for _ in range(80):                                   # turning point: smallest root in (0, 1/3)
        mid = 0.5 * (lo + hi)
        neg = (1.0 / b**2 - mid**2 + 2.0 * mid**3) <= 0
        hi, lo = np.where(neg, mid, hi), np.where(neg, lo, mid)
    u_lim = np.where(b > B_C, 0.98 * lo, np.inf)
    x, w = np.polynomial.legendre.leggauss(n_gauss)
    x, w = 0.5 * (x + 1.0), 0.5 * w
    out = np.zeros((NU, NB))
    for j, u in enumerate(uc):
        ue = np.minimum(u, u_lim)
        uu = ue[None, :] * x[:, None]
        out[j] = ue * (w @ (1.0 / np.sqrt(1.0 / b[None, :] ** 2 - uu**2 + 2.0 * uu**3)))
    return out.astype(np.float32)


def trace_exact(b: float, phi_max: float = PHI_MAX, max_step: float = 0.004):
    """DOP853 reference solution (units M = 1). Returns the scipy solution object (dense output)."""
    from scipy.integrate import solve_ivp

    def cap(_, y):
        return y[0] - 0.5
    cap.terminal = True

    def esc(phi, y):
        return 1.0 if (phi < 1e-6 or y[1] > 0) else y[0]
    esc.terminal, esc.direction = True, -1

    return solve_ivp(lambda _, y: [y[1], 3 * y[0] ** 2 - y[0]], (0.0, phi_max), [0.0, 1.0 / b],
                     method="DOP853", rtol=1e-11, atol=1e-13, events=[cap, esc],
                     max_step=max_step, dense_output=True)


def validate(b, U, phi_end, status, PHC) -> dict:
    """Assert the tables against independent references; returns the measured errors."""
    from scipy.integrate import quad

    phis = np.linspace(0.0, PHI_MAX, NPHI)
    b_cap, b_esc = b[status == 1].max(), b[status == 2].min()
    assert b_cap < B_C < b_esc and b_esc - b_cap < 1e-3, (b_cap, b_esc)
    worst = 0.0
    for bi in (0.5, 3.0, 5.15, 5.25, 8.0, 20.0, 50.0):
        k = int(np.argmin(abs(b - bi)))
        sol = trace_exact(float(b[k]))
        m = phis <= sol.t[-1]
        worst = max(worst, float(np.max(abs(sol.sol(phis[m])[0] - U[m, k]))))
    assert worst < 1e-6, worst
    for bi in (40.0, 60.0, 400.0, 1500.0):                # weak-field series
        k = int(np.argmin(abs(b - bi)))
        x = 1 / b[k]
        pred = 4 * x + 15 * np.pi / 4 * x**2 + 128 / 3 * x**3 + 3465 * np.pi / 64 * x**4
        assert abs(phi_end[k] - np.pi - pred) < 2e-5, (bi, phi_end[k] - np.pi, pred)
    ucg = u_cam_grid()
    for bi, uc in ((5.3, 1 / 30), (12.0, 1 / 22), (2.0, 1 / 21), (800.0, 1 / 3000), (30.0, 1 / 400)):
        k, j = int(np.argmin(abs(b - bi))), int(np.argmin(abs(ucg - uc)))
        ref = quad(lambda x: 1 / np.sqrt(1 / b[k] ** 2 - x * x + 2 * x**3), 0, ucg[j], epsabs=1e-13)[0]
        assert abs(ref - PHC[j, k]) < 1e-6, (bi, ref, PHC[j, k])
    k = int(np.argmin(abs(b - 7.0)))
    assert abs(np.interp(PHC[NU - 1, k], phis, U[:, k]) - U_CMAX) < 1e-5
    return {"b_capture_edge": (float(b_cap), float(b_esc)), "max_table_error": worst}


def load_tables(rebuild: bool = False):
    """(b, U, phi_end, status, PHC), built once (≈20 s), validated, cached in `.aion-cache/schwarzschild/`.

    Example:
        b, U, phi_end, status, PHC = load_tables()
    """
    from aion._env import CACHE

    path = CACHE / "schwarzschild" / f"lut_{NB}x{NPHI}x{NU}.npz"
    if path.exists() and not rebuild:
        z = np.load(path)
        return z["b"], z["U"], z["phi_end"], z["status"], z["PHC"]
    b, U, phi_end, status = build_u_table()
    PHC = build_phc_table()
    validate(b, U, phi_end, status, PHC)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, b=b, U=U, phi_end=phi_end, status=status, PHC=PHC)
    return b, U, phi_end, status, PHC


# ── blackbody colour (Planck → CIE 1931 → linear sRGB), for the disk ───────
T_MIN, T_MAX, N_T = 800.0, 40000.0, 256
_XYZ2RGB = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])


def _lobe(lam, mu, s1, s2):
    return np.exp(-0.5 * ((lam - mu) / np.where(lam < mu, s1, s2)) ** 2)


def blackbody_rgb(T):
    """Linear-sRGB colour of a blackbody at T kelvin, luminance 1 (CMF fit: Wyman, Sloan & Shirley 2013)."""
    lam = np.linspace(360.0, 830.0, 471)
    lm = lam * 1e-9
    planck = 1.0 / (lm**5 * (np.exp(6.62607015e-34 * C_LIGHT / (lm * 1.380649e-23 * np.atleast_1d(T)[:, None])) - 1.0))
    cmf = np.stack([
        1.056 * _lobe(lam, 599.8, 37.9, 31.0) + 0.362 * _lobe(lam, 442.0, 16.0, 26.7) - 0.065 * _lobe(lam, 501.1, 20.4, 26.2),
        0.821 * _lobe(lam, 568.8, 46.9, 40.5) + 0.286 * _lobe(lam, 530.9, 16.3, 31.1),
        1.217 * _lobe(lam, 437.0, 11.8, 36.0) + 0.681 * _lobe(lam, 459.0, 26.0, 13.8)], -1)
    xyz = planck @ cmf
    return np.maximum((xyz / xyz[:, 1:2]) @ _XYZ2RGB.T, 0.0)


def blackbody_table() -> np.ndarray:
    """(N_T, 3) float32, indexed linearly in log T between T_MIN and T_MAX."""
    return blackbody_rgb(np.exp(np.linspace(np.log(T_MIN), np.log(T_MAX), N_T))).astype(np.float32)


# ── where a ring of the disk appears on screen (Luminet's construction) ────
def disk_image(r_disk: float, cam_pos, right, up, fwd, fov_deg: float = 36.0, order: int = 0,
               n: int = 361, frame_h: float = 8.0) -> np.ndarray:
    """Screen curve (n, 2), in frame units, of the circle r = r_disk in the disk plane (y = 0).

    `order` 0 is the direct image (its upper half is the *far* side, lifted over the hole), 1 the
    image that wraps underneath. Points the camera cannot see are NaN. Units M = 1; the camera
    basis is the one `aion.layers.blackhole.camera_basis` returns.

    Example:
        pts = disk_image(19.0, pos, right, up, fwd, fov_deg=36, order=0)
    """
    b, U, phi_end, _, PHC = load_tables()
    pos = np.asarray(cam_pos, float)
    rc = float(np.linalg.norm(pos))
    e1 = pos / rc
    a1 = np.cross([0.0, 1.0, 0.0], e1)
    a1 /= np.linalg.norm(a1)
    a2 = np.cross(e1, a1)
    j = np.sqrt((1.0 / rc) / U_CMAX) * (NU - 1)                      # camera-u axis is sampled at U_CMAX·s²
    j0 = int(np.clip(np.floor(j), 0, NU - 2))
    phc = PHC[j0] + (j - j0) * (PHC[j0 + 1] - PHC[j0])              # (NB,)
    cols = np.arange(NB)
    th = np.tan(np.radians(fov_deg) / 2.0)
    out = np.full((n, 2), np.nan)
    for i, al in enumerate(np.linspace(0.0, 2.0 * np.pi, n)):
        e2 = np.cos(al) * a1 + np.sin(al) * a2
        psi = np.mod(np.arctan2(-e1[1], e2[1]), np.pi) + order * np.pi
        phi = phc + psi
        x = np.clip(phi / PHI_MAX * (NPHI - 1), 0, NPHI - 1.001)
        k = np.floor(x).astype(int)
        u = U[k, cols] + (x - k) * (U[k + 1, cols] - U[k, cols])
        ok = (phi < phi_end) & (phi < PHI_MAX) & (u > 1e-4)
        f = np.where(ok, 1.0 / np.maximum(u, 1e-4) - r_disk, np.nan)
        s = np.where(ok[:-1] & ok[1:] & (f[:-1] <= 0) & (f[1:] > 0))[0]
        if len(s) == 0:
            continue
        m = s[0]
        bb = b[m] + (b[m + 1] - b[m]) * (-f[m]) / (f[m + 1] - f[m])
        sin_a = bb * np.sqrt(1.0 - 2.0 / rc) / rc
        if sin_a >= 1.0:
            continue
        d = -np.sqrt(1.0 - sin_a**2) * e1 + sin_a * e2
        z = float(d @ np.asarray(fwd))
        if z > 1e-6:
            out[i] = (d @ np.asarray(right)) / z / th * frame_h / 2, (d @ np.asarray(up)) / z / th * frame_h / 2
    return out
