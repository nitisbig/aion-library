"""Chapter 3 shared pieces: the double slit (the same two-slit wave makes the stripes and the dots), the baked
tunnelling packet, and hydrogen orbitals as point clouds sampled from |ψ_nlm|². Pure functions of time; RNGs seeded.

Example:
    from ch3 import slit_intensity, hits, psi_at, orbital_points
"""
import math
from functools import lru_cache

import numpy as np
from aion import C  # noqa: F401

import sims as sm
from kit import P3, _hex, lin_rgb, polyline

# ------------------------------------------------------------------------------------------------ colour
def phase_color(a, L=0.80, Cc=0.13):
    """Domain-colouring hue for a complex phase `a` (radians), from an OKLCH wheel (even lightness)."""
    h = math.degrees(a) % 360
    aa, bb = Cc * math.cos(math.radians(h)), Cc * math.sin(math.radians(h))
    l_, m_, s_ = L + 0.3963377774 * aa + 0.2158037573 * bb, L - 0.1055613458 * aa - 0.0638541728 * bb, \
        L - 0.0894841775 * aa - 1.2914855480 * bb
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = np.array([4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                    -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s])
    return _hex(lin)


# ------------------------------------------------------------------------------------------------ double slit
GUN_X, WALL_X, SCREEN_X = -6.0, -3.0, 0.6        # side view (world units)
SLIT_Y, SLIT_A = 0.45, 0.22                      # slit centres ±SLIT_Y, slit width
LAM = 0.15                                       # drawn wavelength: fringe spacing λL/d ≈ 0.6
SCREEN_H = 2.6                                   # the screen spans y ∈ [−2.6, 2.6]


def slit_intensity(y):
    """Fraunhofer two-slit pattern on the screen: cos²(π d sinθ/λ) · sinc²(π a sinθ/λ)."""
    L = SCREEN_X - WALL_X
    s = np.asarray(y) / np.hypot(L, y)
    beta = np.pi * SLIT_A * s / LAM
    return np.cos(np.pi * 2 * SLIT_Y * s / LAM) ** 2 * np.sinc(beta / np.pi) ** 2


@lru_cache(maxsize=1)
def hits(n=6000, seed=1926):
    """Seeded landing heights sampled from slit_intensity (rejection), plus a random across-screen coordinate."""
    rng = np.random.default_rng(seed)
    ys = []
    while len(ys) < n:
        y = rng.uniform(-SCREEN_H, SCREEN_H, 4 * n)
        keep = rng.uniform(0, 1, 4 * n) < slit_intensity(y)
        ys.extend(y[keep].tolist())
    return np.array(ys[:n]), rng.uniform(0, 1, n)


def slit_wave(X, Y, t, omega=6.0):
    """Re ψ of the drawn wave: a plane wave up to the wall, then two cylindrical wavelets from the slits."""
    k = 2 * np.pi / LAM
    out = np.zeros_like(X)
    left = X < WALL_X
    out[left] = np.cos(k * (X[left] - GUN_X) - omega * t)
    right = (X >= WALL_X) & (X <= SCREEN_X)
    psi = 0
    for sy in (SLIT_Y, -SLIT_Y):
        r = np.hypot(X[right] - WALL_X, Y[right] - sy) + 1e-3
        psi = psi + np.exp(1j * (k * (r + WALL_X - GUN_X) - omega * t)) / np.sqrt(1 + 4 * r)
    out[right] = np.real(psi) * 1.2
    return out


# ------------------------------------------------------------------------------------------------ tunnelling
WIN = (-30.0, 18.0)                              # the x-window shown


@lru_cache(maxsize=1)
def _psi_table(tmax=15.0, step=0.05):
    """ψ(x, τ) on the window, sampled every `step` of sim time, by one split-step run (cached on disk)."""
    path = sm.CACHE / f"psi_table_{tmax}_{step}.npz"
    if path.exists():
        d = np.load(path)
        return d["x"], d["psi"], step
    n, L, dt = 4096, 160.0, 0.01
    x = (np.arange(n) - n / 2) * (L / n)
    p = 2 * np.pi * np.fft.fftfreq(n, d=L / n)
    V = np.where(np.abs(x) < 1.4 / 2, 2.6, 0.0)
    psi = np.exp(-((x + 22.0) ** 2) / (4 * 3.0 ** 2) + 1j * 2.0 * x)
    psi /= np.sqrt(np.trapezoid(np.abs(psi) ** 2, x))
    half_v, kin = np.exp(-0.5j * V * dt), np.exp(-0.5j * p ** 2 * dt)
    win = (x >= WIN[0]) & (x <= WIN[1])
    per = int(round(step / dt))
    out = [psi[win].copy()]
    for _ in range(int(round(tmax / step))):
        for _ in range(per):
            psi = half_v * np.fft.ifft(kin * np.fft.fft(half_v * psi))
        out.append(psi[win].copy())
    sm.CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, x=x[win], psi=np.array(out, np.complex64))
    return x[win], np.array(out, np.complex64), step


def psi_at(tau):
    """(x, ψ) at sim time τ (linear interpolation between baked samples). Same physics as sims.schrodinger_1d."""
    x, tab, step = _psi_table()
    p = float(np.clip(tau / step, 0, len(tab) - 1.001))
    i, f = int(p), p - int(p)
    return x, tab[i] * (1 - f) + tab[i + 1] * f


XA, XB, YAX, YB = -6.3, 6.3, 0.95, -2.45            # the helix axis and the |ψ|² baseline on screen


def wave_x(v):
    """Sim x → screen x across the frame."""
    return XA + (XB - XA) * (v - WIN[0]) / (WIN[1] - WIN[0])


_PSI0 = None


def _scales():
    global _PSI0
    if _PSI0 is None:
        _PSI0 = psi_at(0.0)[1]
    return 1.2 / float(np.abs(_PSI0).max()), 1.1 / float((np.abs(_PSI0) ** 2).max())


def __getattr__(name):
    if name == "K2":
        return _scales()[1]
    raise AttributeError(name)


def helix(tau, part):
    """ψ(x, τ) as a phase-coloured helix: the part before the wall's far side (part=0) or beyond it (part=1)."""
    from manim import Line, VGroup
    amp = _scales()[0]
    x, psi = psi_at(tau)

    def proj(xx, z):
        return wave_x(xx) - 0.45 * z.imag * amp, YAX + z.real * amp - 0.32 * z.imag * amp
    g = VGroup()
    for i in range(0, len(x) - 2, 2):
        a, b = psi[i], psi[i + 2]
        if min(abs(a), abs(b)) < 0.012 or (x[i] > 0.8) != bool(part):
            continue
        g.add(Line(P3(*proj(x[i], a)), P3(*proj(x[i + 2], b)), stroke_color=phase_color(float(np.angle(a))),
                   stroke_width=3.2))
    return g


def prob(tau, op, color=None):
    """|ψ|² filled under the helix, on the baseline YB."""
    from manim import Polygon, VGroup
    color = color or C.schrod
    if op < 0.01:
        return VGroup()
    k2 = _scales()[1]
    x, psi = psi_at(tau)
    p2 = np.abs(psi) ** 2
    pts = [(wave_x(xx), YB + k2 * v) for xx, v in zip(x[::3], p2[::3])]
    fill = Polygon(P3(wave_x(x[0]), YB), *[P3(*p) for p in pts], P3(wave_x(x[-1]), YB), stroke_width=0,
                   fill_color=color, fill_opacity=0.28 * op)
    return VGroup(fill, polyline(pts, color, 2.6, op))


# ------------------------------------------------------------------------------------------------ orbitals
def _density(kind, x, y, z):
    r = np.sqrt(x * x + y * y + z * z) + 1e-9
    ct = z / r
    if kind == "1s":
        return np.exp(-2 * r), np.ones_like(r)
    if kind == "2p":
        return r * r * np.exp(-r) * ct * ct, np.sign(ct)
    if kind == "3d":
        ang = 3 * ct * ct - 1
        return r ** 4 * np.exp(-2 * r / 3) * ang * ang, np.sign(ang)
    raise ValueError(kind)


@lru_cache(maxsize=8)
def orbital_points(kind, n=30000, box=None, seed=1926):
    """Points sampled from |ψ|² of a hydrogen orbital (Bohr radii), with the sign of ψ, by rejection sampling."""
    box = box or {"1s": 3.0, "2p": 9.0, "3d": 18.0}[kind]
    rng = np.random.default_rng(seed + hash(kind) % 1000)
    xs, ss = [], []
    probe = rng.uniform(-box, box, (200000, 3))
    dmax = _density(kind, *probe.T)[0].max() * 1.05
    while sum(len(a) for a in xs) < n:
        p = rng.uniform(-box, box, (200000, 3))
        d, sg = _density(kind, *p.T)
        keep = rng.uniform(0, dmax, len(p)) < d
        xs.append(p[keep])
        ss.append(sg[keep])
    return np.concatenate(xs)[:n].astype(np.float32), np.concatenate(ss)[:n].astype(np.float32)


@lru_cache(maxsize=2)
def bond_points(n=30000, half=0.7, seed=1927):
    """H₂ bonding orbital, |e^(−r_A) + e^(−r_B)|², nuclei at z = ±half (Bohr radii)."""
    rng = np.random.default_rng(seed)
    out = []
    while sum(len(a) for a in out) < n:
        p = rng.uniform(-4, 4, (200000, 3))
        ra = np.linalg.norm(p - [0, 0, half], axis=1)
        rb = np.linalg.norm(p + [0, 0, half], axis=1)
        d = (np.exp(-ra) + np.exp(-rb)) ** 2
        keep = rng.uniform(0, 4.0, len(p)) < d
        out.append(p[keep])
    return np.concatenate(out)[:n].astype(np.float32)


def splat(img, X, Y, w, color, ppu, origin):
    """Add points (world X, Y) with weights w into a linear-light float image (row 0 = top)."""
    ny, nx = img.shape[:2]
    px = ((X - origin[0]) * ppu + nx / 2).astype(np.int32)
    py = (ny / 2 - (Y - origin[1]) * ppu).astype(np.int32)
    ok = (px >= 0) & (px < nx) & (py >= 0) & (py < ny)
    acc = np.zeros(ny * nx, np.float32)
    np.add.at(acc, py[ok] * nx + px[ok], w[ok] if np.ndim(w) else w)
    img += acc.reshape(ny, nx)[..., None] * lin_rgb(color)[None, None, :].astype(np.float32)


def cloud_rgba(n=220):
    """Hydrogen 1s probability density, |ψ|² ∝ e^(−2r/a₀), as a soft disc in the chapter-3 hue."""
    c = (np.arange(n) + 0.5) / n * 2 - 1
    x, y = np.meshgrid(c, c)
    r = np.hypot(x, y) * 5.0                                    # the disc spans 5 Bohr radii
    dens = np.exp(-2 * r)
    lin = lin_rgb(C.schrod)[None, None, :] * np.ones((n, n, 1))
    rgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
    out = np.zeros((n, n, 4), np.uint8)
    out[..., :3] = (rgb * 255).astype(np.uint8)
    out[..., 3] = (np.clip(dens ** 0.6, 0, 1) * 255 * (np.hypot(x, y) < 1)).astype(np.uint8)
    return out
