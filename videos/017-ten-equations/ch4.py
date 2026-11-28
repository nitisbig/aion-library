"""Chapter 4 shared pieces: baked fluids (numpy, seeded, cached in .aion-cache/017) and the analytic pictures.

    coffee()        stable fluids (Stam) in a round cup: a stirred flow, cream poured in, parcels carried along
    street()        lattice-Boltzmann flow past a cylinder (sims.lbm), recorded as a time series once shedding is steady
    joukowski()     potential flow round a Joukowski wing section with the Kutta condition (exact streamlines)
    turb_tile()     swirls of every size (a seeded vortex gas, radius halving per octave) for an endless zoom

Example:
    d = coffee(); dye = dye_at(d, 12.0)
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

import sims as sm
from aion import C
from kit import XW, YH, _lin, lin_rgb
from scipy.ndimage import map_coordinates

# ------------------------------------------------------------------------------------------------ the cup
CUP_N, CUP_R = 256, 0.94                         # grid over [-1, 1]², the cup's inner radius
CUP_FPS, CUP_SUB = 30, 2


def _sample(f, x, y):
    """Bilinear sample of a grid over [-1, 1]² (row 0 = y = −1) at world points."""
    from scipy.ndimage import map_coordinates
    n = f.shape[0]
    return map_coordinates(f, [(y + 1) * (n - 1) / 2, (x + 1) * (n - 1) / 2], order=1, mode="nearest")


@lru_cache(maxsize=1)
def coffee(dur=22.6, pour=1.73, pour_len=1.6, seed_at=11.15, seed=1822, ver=2):
    """Bake the cup. Times are seconds from the scene start. Returns dict(dye[f, n, n] uint8, parcels[f, k, 5, 2],
    vel[f, k, 2]) at CUP_FPS; parcels are 6×6 small squares (4 corners + centre) released at `seed_at`."""
    from scipy.ndimage import map_coordinates
    path = sm.CACHE / f"coffee_{CUP_N}_{dur}_{pour}_{pour_len}_{seed_at}_{seed}_v{ver}.npz"
    if path.exists():
        return dict(np.load(path))
    n, h = CUP_N, 2.0 / (CUP_N - 1)
    g = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(g, g)
    R = np.hypot(X, Y)
    inside = R < CUP_R
    rng = np.random.default_rng(seed)
    # the stir: a slow overall turn, faster near the middle, plus a few seeded eddies so it never repeats
    om = 1.6 * np.exp(-(R / 0.55) ** 2) + 0.35
    u, v = -om * Y, om * X
    for _ in range(6):
        cx, cy = rng.uniform(-0.55, 0.55, 2)
        s = rng.choice([-1, 1]) * rng.uniform(1.5, 2.6)
        d2 = (X - cx) ** 2 + (Y - cy) ** 2
        e = s * np.exp(-d2 / 0.03)
        u, v = u - e * (Y - cy), v + e * (X - cx)
    u *= inside
    v *= inside
    dye = np.zeros((n, n))
    dt = 1.0 / (CUP_FPS * CUP_SUB)
    frames = int(round(dur * CUP_FPS)) + 1
    I, J = np.mgrid[0:n, 0:n].astype(np.float64)
    src = (0.5, 0.42)

    pw = [np.zeros((n, n))]

    def project(u, v):
        div = np.zeros_like(u)
        div[1:-1, 1:-1] = (u[1:-1, 2:] - u[1:-1, :-2] + v[2:, 1:-1] - v[:-2, 1:-1]) / (2 * h)
        p = pw[0]                                                     # warm start from the last solve
        for _ in range(60):
            p[1:-1, 1:-1] = (p[1:-1, 2:] + p[1:-1, :-2] + p[2:, 1:-1] + p[:-2, 1:-1] - h * h * div[1:-1, 1:-1]) / 4
            p[~inside] = p[~inside] * 0                                  # crude wall; flow is kept inside below
        pw[0] = p
        u = u.copy()
        v = v.copy()
        u[1:-1, 1:-1] -= (p[1:-1, 2:] - p[1:-1, :-2]) / (2 * h)
        v[1:-1, 1:-1] -= (p[2:, 1:-1] - p[:-2, 1:-1]) / (2 * h)
        return u * inside, v * inside

    u, v = project(u, v)
    e0 = float((u * u + v * v).sum())
    # parcels: a 6×6 grid of small squares (corners + centre)
    side = 0.11
    cs = np.linspace(-0.5, 0.5, 6)
    cen = np.array([(x, y) for y in cs for x in cs])
    offs = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1], [0, 0]]) * side / 2
    P = cen[:, None, :] + offs[None]
    out_dye = np.zeros((frames, n, n), np.uint8)
    out_p = np.zeros((frames, len(cen), 5, 2), np.float32)
    out_v = np.zeros((frames, len(cen), 2), np.float32)
    for f in range(frames):
        t = f / CUP_FPS
        out_dye[f] = (np.clip(dye, 0, 1) * 255).astype(np.uint8)
        if t >= seed_at:
            out_p[f] = P
            out_v[f, :, 0] = _sample(u, P[:, 4, 0], P[:, 4, 1])
            out_v[f, :, 1] = _sample(v, P[:, 4, 0], P[:, 4, 1])
        for _ in range(CUP_SUB):
            ts = t + _ * dt
            if t >= seed_at:                                         # RK2 on the parcels
                flat = P.reshape(-1, 2)
                k1 = np.stack([_sample(u, *flat.T), _sample(v, *flat.T)], 1)
                mid = flat + 0.5 * dt * k1
                k2 = np.stack([_sample(u, *mid.T), _sample(v, *mid.T)], 1)
                P = (flat + dt * k2).reshape(P.shape)
            if pour <= ts < pour + pour_len:                          # cream pours in at one spot near the rim
                blob = np.exp(-((X - src[0]) ** 2 + (Y - src[1]) ** 2) / 0.006)
                dye = np.maximum(dye, blob)
            bx, by = J - u * dt / h, I - v * dt / h
            u2 = map_coordinates(u, [by, bx], order=1, mode="nearest")
            v2 = map_coordinates(v, [by, bx], order=1, mode="nearest")
            dye = np.clip(map_coordinates(dye, [by, bx], order=3, mode="nearest"), 0, 1) * inside
            u, v = project(u2, v2)
            # the spoon keeps stirring: hold the kinetic energy on a slow decay (the grid's numerical loss would
            # otherwise stop the cup within seconds); the flow's shape is left to the solver
            k = math.sqrt(e0 * 0.93 ** ts / max(float((u * u + v * v).sum()), 1e-12))
            u, v = u * k, v * k
    out = {"dye": out_dye, "parcels": out_p, "vel": out_v}
    sm.CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **out)
    return out


def cup_frame(d, t):
    """Frame index (float) for scene-relative time t."""
    return float(np.clip(t * CUP_FPS, 0, len(d["dye"]) - 1.001))


def lerp_frames(a, x):
    i = int(x)
    f = x - i
    return a[i] * (1 - f) + a[min(i + 1, len(a) - 1)] * f


# ------------------------------------------------------------------------------------------------ vortex street
@lru_cache(maxsize=1)
def street(nx=420, ny=150, warm=14000, rec=200, every=16, u_in=0.08, radius=13.0, re=150.0, seed=1704):
    """Flow past a cylinder (D2Q9 BGK, same model as sims.lbm_vortex), warmed until shedding is steady, then
    `rec` snapshots of vorticity and dye every `every` steps (row 0 = bottom). Cached."""
    from scipy.ndimage import map_coordinates
    path = sm.CACHE / f"street_{nx}_{ny}_{warm}_{rec}_{every}_{u_in}_{radius}_{re}_{seed}.npz"
    if path.exists():
        return dict(np.load(path))
    E, W, OPP, feq_ = sm._E, sm._W, sm._OPP, sm._feq
    nu = u_in * 2 * radius / re
    tau = 3 * nu + 0.5
    cx, cy = nx // 5, ny // 2
    Y, X = np.mgrid[0:ny, 0:nx]
    mask = (X - cx) ** 2 + (Y - cy) ** 2 < radius ** 2
    rng = np.random.default_rng(seed)
    ux = np.full((ny, nx), u_in)
    uy = 0.01 * u_in * np.sin(2 * np.pi * Y / ny) * (1 + 0.1 * rng.standard_normal((ny, nx)))
    rho = np.ones((ny, nx))
    f = feq_(rho, ux, uy)
    dye = np.zeros((ny, nx))
    src_y = cy + np.array([-2.2, -1.1, 0, 1.1, 2.2]) * radius * 0.55
    vort_out = np.zeros((rec, ny, nx), np.float16)
    dye_out = np.zeros((rec, ny, nx), np.float16)
    total = warm + rec * every
    for it in range(total):
        rho = f.sum(0)
        ux = (f * E[:, 0, None, None]).sum(0) / rho
        uy = (f * E[:, 1, None, None]).sum(0) / rho
        ux[:, 0], uy[:, 0], rho[:, 0] = u_in, 0.0, 1.0
        ux[mask], uy[mask] = 0.0, 0.0
        feq = feq_(rho, ux, uy)
        f += (feq - f) / tau
        f[:, :, 0] = feq[:, :, 0]
        fb = f[:, mask]
        for i in range(9):
            f[i] = np.roll(np.roll(f[i], E[i, 0], axis=1), E[i, 1], axis=0)
        f[:, mask] = fb[OPP]
        f[:, :, -1] = f[:, :, -2]
        if it % 4 == 0:
            dye = map_coordinates(dye, [Y - uy * 4, X - ux * 4], order=1, mode="nearest")
            for sy in src_y:
                dye[int(round(sy)) - 1:int(round(sy)) + 2, 2:8] = 1.0
            dye[mask] = 0.0
        if it >= warm and (it - warm) % every == 0:
            k = (it - warm) // every
            v = np.gradient(uy, axis=1) - np.gradient(ux, axis=0)
            v[mask] = 0
            vort_out[k], dye_out[k] = v, dye
        if it % 1000 == 0:
            print(f"street {it}/{total}", flush=True)
    out = {"vort": vort_out, "dye": dye_out, "mask": mask.astype(np.uint8),
           "params": np.array([nx, ny, cx, cy, radius, every])}
    np.savez_compressed(path, **out)
    return out


def street_rgba(d, x, r0=14, k=None, vmax=None):
    """Snapshot x (float index) as RGBA: vorticity charge_n ↔ black ↔ navier (6 % dead zone) plus faint dye smoke."""
    from aion import C
    vort = lerp_frames(d["vort"], x).astype(np.float32)[r0:-r0]
    dye = lerp_frames(d["dye"], x).astype(np.float32)[r0:-r0]
    mask = d["mask"][r0:-r0].astype(bool)
    vmax = vmax or float(np.percentile(np.abs(d["vort"][-1].astype(np.float32)[r0:-r0][~mask]), 98.5))
    w = np.clip(vort / vmax, -1, 1)
    a = np.clip((np.abs(w) - 0.06) / 0.94, 0, 1) ** 0.85
    rgb = np.where(w[..., None] > 0, a[..., None] * _lin(C.navier), a[..., None] * _lin(C.charge_n)) * 0.85
    rgb = rgb + (np.clip(dye, 0, 1) ** 1.6)[..., None] * _lin(C.light) * 0.22
    rgb[mask] = 0
    return np.clip(rgb, 0, 1)


def street_frames(d, t_on, rate=27.0, scale=2):
    """FramesLayer source: the street played from scene time t_on at `rate` snapshots/s, feathered top and bottom."""
    from scipy.ndimage import zoom
    def frame(t):
        x = float(np.clip((t - t_on) * rate, 0, len(d["vort"]) - 1.001))
        rgb = street_rgba(d, x)
        rgb = np.clip(zoom(rgb, (scale, scale, 1), order=1), 0, 1)[::-1]
        srgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - 0.055)
        h = srgb.shape[0]
        fe = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (0.08 * h), 0, 1)[:, None]
        out = np.empty(srgb.shape[:2] + (4,), np.uint8)
        out[..., :3] = (srgb * 255).astype(np.uint8)
        out[..., 3] = (fe * 255).astype(np.uint8)
        return out
    return frame


def street_geom(d, r0=14, cy_world=-0.45):
    """(raster height, cylinder centre, cylinder radius) on screen for a full-width street centred at cy_world."""
    from kit import XW
    p = d["params"]
    nx, ny = int(p[0]), int(p[1]) - 2 * r0
    ext_w = 2 * XW
    ext_h = ext_w * ny / nx
    cx = -XW + ext_w * p[2] / nx
    cy = cy_world - ext_h / 2 + ext_h * (p[3] - r0) / ny
    return ext_h, (cx, cy), ext_w * p[4] / nx


# ------------------------------------------------------------------------------------------------ a wing
def joukowski(alpha=math.radians(6), mu=(-0.08, 0.06), n_lines=13, span=(-3.2, 3.6), spacing=0.13):
    """Joukowski wing section and its exact streamlines (potential flow, Kutta condition), in units of chord≈4.

    The circle |ζ − μ| = a with a = |1 − μ| maps to the wing by z = ζ + 1/ζ. Complex potential in the ζ plane:
    w = U(ζ' e^{−iα} + a² e^{iα}/ζ') + iΓ/(2π) log ζ', ζ' = ζ − μ, Γ = 4π U a sin(α + β) puts the rear stagnation
    point on the trailing edge. Streamlines are level sets of Im w, traced numerically in ζ and mapped to z.
    Returns (wing outline (N, 2), [streamline (M, 3) as x, y, travel time, …])."""
    mu = complex(*mu)
    a = abs(1 - mu)
    beta = math.asin(-mu.imag / a) if abs(mu.imag) < a else 0.0
    gam = 4 * math.pi * a * math.sin(alpha + beta)

    def w(z):
        zp = z - mu
        return zp * np.exp(-1j * alpha) + a * a * np.exp(1j * alpha) / zp + 1j * gam / (2 * np.pi) * np.log(zp)

    def dw(z):
        zp = z - mu
        return np.exp(-1j * alpha) - a * a * np.exp(1j * alpha) / zp ** 2 + 1j * gam / (2 * np.pi) / zp
    th = np.linspace(0, 2 * np.pi, 400)
    circ = mu + a * np.exp(1j * th)
    wing = circ + 1 / circ
    lines = []
    for k in range(-(n_lines // 2), n_lines // 2 + 1):
        z = complex(span[0], k * spacing * 2 + 0.05)
        pts, tt = [], 0.0
        for _ in range(3000):                                   # follow the velocity, conj(dw/dz), in small steps
            zeta = _inv_jouk(z, mu, a)
            W = dw(zeta) / (1 - 1 / zeta ** 2)
            vel = np.conj(W)
            pts.append((z.real, z.imag, tt))
            if z.real > span[1]:
                break
            z = z + vel / max(abs(vel), 1e-6) * 0.02
            tt += 0.02 / max(abs(vel), 1e-6)
        lines.append(np.array(pts))
    return np.stack([wing.real, wing.imag], 1), lines


def _inv_jouk(z, mu, a):
    r = np.sqrt(z * z - 4 + 0j)
    c1, c2 = (z + r) / 2, (z - r) / 2
    return c1 if abs(c1 - mu) >= abs(c2 - mu) else c2


# ------------------------------------------------------------------------------------------------ turbulence
@lru_cache(maxsize=1)
def turb_tile(n=512, seed=1845, octaves=5):
    """A periodic tile of swirls of every size: a seeded gas of eddies whose radius halves and whose count
    quadruples per octave (same coverage at each scale), each drawn as a two-armed spiral of rolled-up vorticity
    turning with its sign. Unit rms, row 0 bottom. An illustration of the eddy cascade, not a solved flow."""
    rng = np.random.default_rng(seed)
    w = np.zeros((n, n), np.float32)
    for j in range(octaves):
        r = 0.11 * n / 2 ** j
        m = int(round(r * 3))
        oy, ox = np.mgrid[-m:m + 1, -m:m + 1]
        rr = np.hypot(ox, oy) + 1e-3
        th = np.arctan2(oy, ox)
        env = np.exp(-(rr / r) ** 2)
        spirals = {sg: (env * (0.35 + 0.65 * (0.5 + 0.5 * np.cos(2 * th - sg * 7 * np.log(rr / r))) ** 2)).astype(np.float32)
                   for sg in (-1, 1)}
        for _ in range(4 * 4 ** j):
            cy, cx = rng.integers(0, n, 2)
            sg = int(rng.choice([-1, 1]))
            sgn = sg * rng.uniform(0.7, 1.2)
            patch = spirals[sg]
            iy = (cy + oy[:, 0]) % n
            ix = (cx + ox[0]) % n
            w[np.ix_(iy, ix)] += sgn * patch
    return w / w.std()


def _srgb(lin):
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.maximum(lin, 0) ** (1 / 2.4) - 0.055)


def _rgba(lin, a):
    out = np.empty(a.shape + (4,), np.uint8)
    rgb = lin / np.maximum(a, 1e-4)[..., None]
    out[..., :3] = (np.clip(_srgb(np.clip(rgb, 0, 1)), 0, 1) * 255).astype(np.uint8)
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return out


NXT, NYT = 480, 270


def turb_value(px, py, t, t0):
    """The zooming field at screen points (the swirl tile, three octaves cross-faded so the zoom never ends)."""
    tile = turb_tile()
    n = tile.shape[0]
    s = 0.42 * max(t - t0, 0.0)
    f = s % 1.0
    drift = np.array([0.35, 0.12]) * (t - t0)
    out = 0
    for j in range(3):
        z = 2.0 ** (j + f)
        w = math.sin(math.pi * (j + f) / 3) ** 2
        cx = (px / z + drift[0]) * 38
        cy = (py / z + drift[1]) * 38
        out = out + w * map_coordinates(tile, [cy % n, cx % n], order=1, mode="wrap")
    return out / 1.6


def turb_frames(op, t0):
    xs = np.linspace(-XW, XW, NXT)
    ys = np.linspace(YH, -YH, NYT)                               # row 0 = top
    PX, PY = np.meshgrid(xs, ys)
    pos, neg = lin_rgb(C.navier), lin_rgb(C.charge_n)

    def frame(t):
        w = np.clip(turb_value(PX.ravel(), PY.ravel(), t, t0).reshape(NYT, NXT) / 3.4, -1, 1)
        a = np.clip((np.abs(w) - 0.06) / 0.94, 0, 1) ** 0.9 * float(op(t))
        lin = np.where(w[..., None] > 0, pos, neg) * a[..., None] * 0.8
        return _rgba(lin, a)
    return frame


PROBE = (0.0, 0.6)                               # c04_s03's probe point and trace (y, x0, x1), screen units
TRACE = (-2.45, -5.2, 5.2)


@lru_cache(maxsize=2)
def probe_trace(t0, t_a, t_b, n=520):
    """(times, values) the probe reads from the zooming field, normalised to ±1."""
    ts = np.linspace(t_a, t_b, n)
    v = np.array([turb_value(np.array([PROBE[0]]), np.array([PROBE[1]]), x, t0)[0] for x in ts])
    return ts, v / max(np.abs(v).max(), 1e-6)
