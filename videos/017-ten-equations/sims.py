"""Simulations and computed pictures for video 017 (numpy, seeded, deterministic).

Every curve or field the video shows is computed here, never drawn by eye. The style frames use these now; the
scenes will bake time series from the same functions (or Taichi ports of them, same parameters).

    heat_bar        1D heat equation on an insulated bar, solved exactly as a cosine (Fourier) series      in_s01, c10
    dipole_field    the radiating field of an oscillating electric dipole (near + far terms)                c01_s03
    em_wave         E and B of a plane wave along x                                                         c01_s03
    schrodinger_1d  split-step Fourier solution of a wave packet hitting a barrier (hbar = m = 1)            c03_s02
    lbm_vortex      lattice-Boltzmann (D2Q9) flow past a cylinder → vortex street; cached .npz              c04_s02
    fourier_path    epicycle coefficients of a closed outline (FFT)                                         c05_s02
    loss_surface    a two-valley loss and exact gradient-descent iterates                                   c07
    qam16           a 16-point constellation with seeded Gaussian noise                                     c08_s02
    bayes_people    the 1,000 people of the test example (who is ill, who tests positive), seeded          c09_s01
    gbm_paths       geometric Brownian price paths                                                          c10_s02

Example:
    x = np.linspace(0, 1, 400); u, modes = heat_bar(x, 0.01)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

CACHE = Path(__file__).resolve().parents[2] / ".aion-cache" / "017"


# ------------------------------------------------------------------------------------------------- heat (Fourier)
def heat_bar(x: np.ndarray, t: float, alpha: float = 1.0, n_modes: int = 60, x_hot: float = 0.1, width: float = 0.07):
    """Temperature u(x, t) on an insulated bar [0, 1] that starts with a hot spot near x_hot.

    Exact solution: u = a0 + sum_n a_n cos(n pi x) exp(-alpha (n pi)^2 t), with a_n from the initial profile.
    Returns (u, modes) where modes[n] is the n-th term (n = 0 … n_modes-1) at time t.
    """
    xs = np.linspace(0, 1, 4001)
    u0 = np.exp(-((xs - x_hot) / width) ** 2)
    modes = []
    for n in range(n_modes):
        basis = np.cos(n * np.pi * xs)
        a = np.trapezoid(u0 * basis, xs) * (1 if n == 0 else 2)
        modes.append(a * np.cos(n * np.pi * x) * np.exp(-alpha * (n * np.pi) ** 2 * t))
    modes = np.array(modes)
    return modes.sum(0), modes


# ------------------------------------------------------------------------------------------------- Maxwell
def dipole_field(nx: int, ny: int, extent=(8.7, 6.6), k: float = 2.4, phase: float = 0.0, origin=(0.0, 0.0)):
    """Out-of-plane magnetic field B_z of an electric dipole along y oscillating at `origin` (Hertzian dipole).

    B_z ∝ sin(theta) [ k cos(kr - phase) / r - sin(kr - phase) / r^2 ] (theta from the dipole axis). Returned
    multiplied by r so the far field keeps an even brightness, normalised to [-1, 1]. Row 0 = bottom. `origin` is
    relative to the centre of the extent.
    """
    xs = np.linspace(-extent[0] / 2, extent[0] / 2, nx) - origin[0]
    ys = np.linspace(-extent[1] / 2, extent[1] / 2, ny) - origin[1]
    X, Y = np.meshgrid(xs, ys)
    r = np.hypot(X, Y) + 1e-6
    sin_t = np.abs(X) / r * np.sign(X)
    b = sin_t * (k * np.cos(k * r - phase) / r - np.sin(k * r - phase) / r ** 2)
    b *= np.minimum(r, 3.0)
    b[r < 0.25] = 0.0
    return b / np.abs(b).max()


def point_charges(X: np.ndarray, Y: np.ndarray, charges):
    """Coulomb field of point charges [(x, y, q), …] on a grid: (Fx, Fy) ∝ Σ q r̂ / r². Also the field of bar-magnet
    poles (a magnet = +q at its N end, −q at its S end), which is exact outside the magnet for a long thin bar."""
    fx, fy = np.zeros_like(X), np.zeros_like(X)
    for x0, y0, q in charges:
        dx, dy = X - x0, Y - y0
        r3 = (dx * dx + dy * dy + 1e-4) ** 1.5
        fx += q * dx / r3
        fy += q * dy / r3
    return fx, fy


def field_line(charges, start, step: float = 0.02, n: int = 4000, sign: float = 1.0, stop=None, box=(7.2, 4.1)):
    """Trace one field line from `start` along +F (sign=1) or −F with RK2. Stops at a sink (r < 0.12), outside `box`,
    or when `stop(p)` is true. Returns an (m, 2) array."""
    p = np.array(start, float)
    pts = [p.copy()]

    def f(q):
        fx, fy = point_charges(np.array(q[0]), np.array(q[1]), charges)
        v = np.array([float(fx), float(fy)]) * sign
        return v / (np.hypot(*v) + 1e-12)

    for _ in range(n):
        mid = p + 0.5 * step * f(p)
        p = p + step * f(mid)
        pts.append(p.copy())
        if abs(p[0]) > box[0] or abs(p[1]) > box[1] or (stop is not None and stop(p)):
            break
        if min(np.hypot(p[0] - x0, p[1] - y0) for x0, y0, q in charges if q * sign < 0) < 0.12 \
                if any(q * sign < 0 for *_, q in charges) else False:
            break
    return np.array(pts)


def lic(field, extent=(128 / 9, 8.0), ppu: float = 90.0, L: int = 22, phases: int = 12, wavelength: float = 9.0,
        density: float = 1.0, seed: int = 1701, blur: float = 0.6):
    """Line-integral convolution of seeded noise along a vector field: the 'iron filings' picture of a field.

    `field(X, Y) -> (Fx, Fy)` in world units over a frame of `extent` centred at 0. Each pixel averages noise along its
    streamline (±L steps of one pixel). With `phases` > 1 the kernel carries a travelling ripple (Cabral & Leedom's
    animated LIC), so cycling the phases makes the texture flow along the field. `density` < 1 uses sparse noise
    (short streaks, like filings). Returns uint8 (phases, ny, nx), row 0 = top. Cached in .aion-cache/017.
    """
    nx, ny = int(round(extent[0] * ppu)), int(round(extent[1] * ppu))
    key = f"lic_{getattr(field, '__name__', 'f')}_{nx}x{ny}_{L}_{phases}_{wavelength}_{density}_{seed}_{blur}"
    path = CACHE / f"{key}.npz"
    if path.exists():
        return np.load(path)["img"]
    from scipy import ndimage as ndi
    rng = np.random.default_rng(seed)
    noise = rng.random((ny, nx)).astype(np.float32)
    if density < 1.0:
        noise = (noise < density).astype(np.float32)
    elif blur:
        noise = ndi.gaussian_filter(noise, blur).astype(np.float32)
    xs = (np.arange(nx) + 0.5) / ppu - extent[0] / 2
    ys = extent[1] / 2 - (np.arange(ny) + 0.5) / ppu            # row 0 = top
    X, Y = np.meshgrid(xs.astype(np.float32), ys.astype(np.float32))
    fx, fy = field(X, Y)
    mag = np.hypot(fx, fy) + 1e-12
    ux, uy = (fx / mag).astype(np.float32), (-fy / mag).astype(np.float32)   # pixel rows grow downwards
    del X, Y, fx, fy, mag
    s = np.arange(-L, L + 1)
    hann = 0.5 * (1 + np.cos(np.pi * s / (L + 1)))
    ph = 2 * np.pi * np.arange(phases) / phases
    w = hann[None, :] * (0.5 * (1 + np.sin(2 * np.pi * s[None, :] / wavelength - ph[:, None])) if phases > 1 else 1.0)
    acc = np.zeros((phases, ny, nx), np.float32)
    acc += w[:, L, None, None] * noise[None]
    for direction in (1, -1):
        px, py = np.meshgrid(np.arange(nx, dtype=np.float32) + 0.5, np.arange(ny, dtype=np.float32) + 0.5)
        for k in range(1, L + 1):
            ix = np.clip(px.astype(np.int32), 0, nx - 1)
            iy = np.clip(py.astype(np.int32), 0, ny - 1)
            px += direction * 0.8 * ux[iy, ix]
            py += direction * 0.8 * uy[iy, ix]
            ix = np.clip(px.astype(np.int32), 0, nx - 1)
            iy = np.clip(py.astype(np.int32), 0, ny - 1)
            sample = noise[iy, ix]
            for p in range(phases):
                acc[p] += w[p, L + direction * k] * sample
    acc /= w.sum(1)[:, None, None]
    lo, hi = np.percentile(acc[0], [1, 99.5])
    img = (np.clip((acc - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, img=img)
    return img


# the chapter-1 stage: a charge left of centre, a bar magnet right of centre (positions shared with the scene)
CHARGE_POS = (-3.3, 0.25)
MAGNET_POS, MAGNET_HALF = (3.3, 0.25), 0.95


def charge_field(X, Y):
    """E of one positive point charge at CHARGE_POS."""
    return point_charges(X, Y, [(*CHARGE_POS, 1.0)])


def magnet_field(X, Y):
    """B of the bar magnet at MAGNET_POS (N pole on the right), modelled by its two poles."""
    mx, my = MAGNET_POS
    return point_charges(X, Y, [(mx + MAGNET_HALF, my, 1.0), (mx - MAGNET_HALF, my, -1.0)])


def em_wave(x: np.ndarray, t: float = 0.0, k: float = 2 * np.pi / 2.4, amp: float = 1.0):
    """A plane wave along x: E along y and B along z, in phase, |E| = c|B| (drawn at equal height)."""
    ph = k * x - 2.0 * t
    return amp * np.sin(ph), amp * np.sin(ph)


# ------------------------------------------------------------------------------------------------- Schrödinger
def schrodinger_1d(t: float, n: int = 4096, L: float = 160.0, x0: float = -22.0, k0: float = 2.0, sigma: float = 3.0,
                   v0: float = 2.6, width: float = 1.4, dt: float = 0.01):
    """psi(x, t) for a Gaussian packet hitting a square barrier, by split-step Fourier (hbar = m = 1).

    Energy k0^2/2 = 2.0 < v0 = 2.6: classically the packet must bounce; about 14 % tunnels through by t = 14.
    Returns x, psi, V.
    """
    x = (np.arange(n) - n / 2) * (L / n)
    p = 2 * np.pi * np.fft.fftfreq(n, d=L / n)
    V = np.where(np.abs(x) < width / 2, v0, 0.0)
    psi = np.exp(-((x - x0) ** 2) / (4 * sigma ** 2) + 1j * k0 * x)
    psi /= np.sqrt(np.trapezoid(np.abs(psi) ** 2, x))
    half_v = np.exp(-0.5j * V * dt)
    kin = np.exp(-0.5j * p ** 2 * dt)
    for _ in range(int(round(t / dt))):
        psi = half_v * np.fft.ifft(kin * np.fft.fft(half_v * psi))
    return x, psi, V


# ------------------------------------------------------------------------------------------------- Navier–Stokes
_E = np.array([[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]])
_W = np.array([4 / 9] + [1 / 9] * 4 + [1 / 36] * 4)
_OPP = [0, 3, 4, 1, 2, 7, 8, 5, 6]


def _feq(rho, ux, uy):
    cu = 3 * (_E[:, 0, None, None] * ux + _E[:, 1, None, None] * uy)
    usq = 1.5 * (ux ** 2 + uy ** 2)
    return rho * _W[:, None, None] * (1 + cu + 0.5 * cu ** 2 - usq)


def lbm_vortex(nx: int = 420, ny: int = 150, steps: int = 16000, u_in: float = 0.08, radius: float = 13.0,
               re: float = 150.0, dye_every: int = 4, seed: int = 1704, keep_last: int = 0):
    """Flow past a cylinder (D2Q9 BGK lattice Boltzmann). Returns dict(vort, ux, uy, dye, mask), row 0 = bottom.

    Re = u_in * D / nu. Periodic top/bottom, equilibrium inlet, copy outlet, bounce-back cylinder; a seeded small
    transverse kick breaks the symmetry so shedding starts. A passive dye (five streaks released upstream) is
    advected semi-Lagrangian every `dye_every` steps. Cached by parameters in .aion-cache/017/.
    """
    from scipy.ndimage import map_coordinates

    key = f"lbm_{nx}_{ny}_{steps}_{u_in}_{radius}_{re}_{dye_every}_{seed}.npz"
    path = CACHE / key
    if path.exists():
        return dict(np.load(path))
    nu = u_in * 2 * radius / re
    tau = 3 * nu + 0.5
    cx, cy = nx // 5, ny // 2
    Y, X = np.mgrid[0:ny, 0:nx]
    mask = (X - cx) ** 2 + (Y - cy) ** 2 < radius ** 2
    rng = np.random.default_rng(seed)
    ux = np.full((ny, nx), u_in)
    uy = 0.01 * u_in * np.sin(2 * np.pi * Y / ny) * (1 + 0.1 * rng.standard_normal((ny, nx)))
    rho = np.ones((ny, nx))
    f = _feq(rho, ux, uy)
    dye = np.zeros((ny, nx))
    src_y = cy + np.array([-2.2, -1.1, 0, 1.1, 2.2]) * radius * 0.55
    for it in range(steps):
        rho = f.sum(0)
        ux = (f * _E[:, 0, None, None]).sum(0) / rho
        uy = (f * _E[:, 1, None, None]).sum(0) / rho
        ux[:, 0], uy[:, 0], rho[:, 0] = u_in, 0.0, 1.0
        ux[mask], uy[mask] = 0.0, 0.0
        feq = _feq(rho, ux, uy)
        f += (feq - f) / tau
        f[:, :, 0] = feq[:, :, 0]
        fb = f[:, mask]
        for i in range(9):
            f[i] = np.roll(np.roll(f[i], _E[i, 0], axis=1), _E[i, 1], axis=0)
        f[:, mask] = fb[_OPP]
        f[:, :, -1] = f[:, :, -2]
        if it % dye_every == 0:
            dye = map_coordinates(dye, [Y - uy * dye_every, X - ux * dye_every], order=1, mode="nearest")
            for sy in src_y:
                dye[int(round(sy)) - 1:int(round(sy)) + 2, 2:8] = 1.0
            dye[mask] = 0.0
    vort = (np.gradient(uy, axis=1) - np.gradient(ux, axis=0))
    vort[mask] = 0.0
    out = {"vort": vort, "ux": ux, "uy": uy, "dye": dye, "mask": mask.astype(np.uint8),
           "params": np.array([nx, ny, steps, u_in, radius, re, cx, cy])}
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **out)
    return out


# ------------------------------------------------------------------------------------------------- Fourier
def fourier_path(points: np.ndarray, n_terms: int = 80):
    """Epicycle terms of a closed 2D outline: returns (freqs, coeffs) sorted by |coeff|, largest first.

    The outline z(s), s in [0, 1), is resampled uniformly by arc length; c_k = mean(z e^{-2 pi i k s}).
    Re-summing the n_terms circles traces the outline.
    """
    p = np.asarray(points, float)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(np.vstack([p, p[:1]]), axis=0).T))]
    s = np.linspace(0, seg[-1], 1024, endpoint=False)
    closed = np.vstack([p, p[:1]])
    z = np.interp(s, seg, closed[:, 0]) + 1j * np.interp(s, seg, closed[:, 1])
    c = np.fft.fft(z) / len(z)
    k = np.fft.fftfreq(len(z), 1 / len(z)).astype(int)
    order = np.argsort(-np.abs(c))[:n_terms]
    return k[order], c[order]


def epicycles(freqs, coeffs, s: float):
    """Arm joints of the epicycle chain at phase s in [0, 1) (complex positions, starting at 0)."""
    terms = coeffs * np.exp(2j * np.pi * freqs * s)
    return np.r_[0, np.cumsum(terms)]


# ------------------------------------------------------------------------------------------------- gradient descent
def loss(x, y):
    """A smooth landscape with a deep valley and a shallower one (a stand-in for a model's error)."""
    return (1.2 - 1.0 * np.exp(-((x - 1.0) ** 2 + (y - 0.4) ** 2) / 2.4)
            - 0.55 * np.exp(-((x + 1.5) ** 2 + (y + 1.2) ** 2) / 1.0) + 0.08 * (x ** 2 + y ** 2))


def loss_grad(x, y, h: float = 1e-5):
    return ((loss(x + h, y) - loss(x - h, y)) / (2 * h), (loss(x, y + h) - loss(x, y - h)) / (2 * h))


def descent_path(start=(-0.9, 2.6), eta: float = 0.25, steps: int = 30):
    """Exact iterates of theta <- theta - eta * grad L(theta)."""
    p = [np.array(start, float)]
    for _ in range(steps):
        g = np.array(loss_grad(*p[-1]))
        p.append(p[-1] - eta * g)
    return np.array(p)


# ------------------------------------------------------------------------------------------------- Shannon
def qam16(n_per: int = 500, snr_db: float = 16.0, seed: int = 1708):
    """16-QAM points (levels ±1, ±3) and received samples with complex Gaussian noise at the given Es/N0."""
    rng = np.random.default_rng(seed)
    lv = np.array([-3, -1, 1, 3], float)
    pts = np.array([(a, b) for a in lv for b in lv])
    es = np.mean((pts ** 2).sum(1))
    sigma = np.sqrt(es / 10 ** (snr_db / 10) / 2)
    rx = np.repeat(pts, n_per, 0) + rng.normal(0, sigma, (len(pts) * n_per, 2))
    sent = np.repeat(np.arange(16), n_per)
    nearest = np.argmin(((rx[:, None, :] - pts[None]) ** 2).sum(-1), 1)
    return pts, rx, sent, nearest != sent


# ------------------------------------------------------------------------------------------------- Bayes
def bayes_people(seed: int = 1709):
    """1,000 people: 10 ill (9 test positive), 990 healthy (89 test positive). Returns (ill, positive) bool arrays."""
    rng = np.random.default_rng(seed)
    ill = np.zeros(1000, bool)
    ill[:10] = True
    pos = np.zeros(1000, bool)
    pos[:9] = True
    pos[10 + rng.choice(990, 89, replace=False)] = True
    return ill, pos


# ------------------------------------------------------------------------------------------------- Black–Scholes
def gbm_paths(n: int = 2000, steps: int = 252, s0: float = 100.0, r: float = 0.03, sigma: float = 0.2,
              T: float = 1.0, seed: int = 1710):
    """Risk-neutral geometric Brownian motion paths: (steps+1, n) prices on a time grid (t, paths)."""
    rng = np.random.default_rng(seed)
    dt = T / steps
    z = rng.standard_normal((steps, n))
    logs = np.cumsum((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z, 0)
    return np.linspace(0, T, steps + 1), s0 * np.exp(np.vstack([np.zeros(n), logs]))


if __name__ == "__main__":
    x = np.array([0.1, 0.5, 1.0])
    u, m = heat_bar(x, 0.0)
    assert abs(u[0] - 1.0) < 0.01 and abs(u[1]) < 1e-3, u    # the series rebuilds the initial hot spot
    xs, psi, V = schrodinger_1d(0.0)
    assert abs(np.trapezoid(abs(psi) ** 2, xs) - 1) < 1e-6
    xs, psi, V = schrodinger_1d(14.0)
    trans = np.trapezoid(abs(psi[xs > 1]) ** 2, xs[xs > 1])
    print(f"tunnelled fraction at t=14: {trans:.3f}")
    p = descent_path()
    assert loss(*p[-1]) < loss(*p[0])
    pts, rx, sent, err = qam16()
    print(f"16-QAM symbol error rate at 16 dB: {err.mean():.3f}")
    ill, pos = bayes_people()
    assert (ill & pos).sum() == 9 and (~ill & pos).sum() == 89
    t, S = gbm_paths(200)
    print(f"GBM mean at T: {S[-1].mean():.1f} (expected {100 * np.exp(0.03):.1f})")
    print("sims ok")
