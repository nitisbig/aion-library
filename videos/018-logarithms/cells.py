"""c01_s01's dividing cells: a seeded soft-body packing per generation (numpy relaxation, cached), drawn per frame
with skia. Generation k's cells are the two daughters of generation k-1's cells (2i, 2i+1), so a division is a pure
interpolation between two baked packings: daughters slide apart from their mother and shrink, pinching as they go.

Example:
    s.add(FramesLayer(cells_frame(gen_at), height=CELL_H, pos=CELL_C))
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

GENS = 10
SEED = 1801
CELL_C = (-2.0, 0.15)          # colony centre (world units)
CELL_W, CELL_H = 9.0, 8.0      # raster extent (world units)
PPU = 135                      # raster pixels per world unit (1:1 at 1080p)
R0, R10 = 0.9, 0.0964          # cell radius at generation 0 and 10 (colony radius 3.45 u at 1024 cells)
_CACHE = Path(__file__).resolve().parents[2] / ".aion-cache" / f"018_cells_{SEED}.npz"


def radius(g):
    return R0 * (R10 / R0) ** (g / GENS)


def _relax(p, r, iters=140, rng=None):
    n = len(p)
    for it in range(iters):
        if n > 1:
            d = p[:, None, :] - p[None, :, :]
            dist = np.sqrt((d ** 2).sum(-1)) + np.eye(n)
            ov = np.clip(2.04 * r - dist, 0, None) * (1 - np.eye(n))
            p = p + 0.5 * (d / dist[..., None] * ov[..., None]).sum(1)
        rad = np.hypot(p[:, 0], p[:, 1]) + 1e-9               # a gentle pull to the dish, only from outside it
        R = r * math.sqrt(n / 0.86)
        p = p - (0.08 * np.clip(rad - R, 0, None) / rad)[:, None] * p
    return p - p.mean(0)


def generations():
    """Positions (centre-relative, world units) of every generation: list of (2^g, 2) arrays."""
    if _CACHE.exists():
        z = np.load(_CACHE)
        return [z[f"g{g}"] for g in range(GENS + 1)]
    rng = np.random.default_rng(SEED)
    gens = [np.zeros((1, 2))]
    for g in range(1, GENS + 1):
        par = gens[-1]
        r = radius(g)
        ang = rng.uniform(0, 2 * math.pi, len(par))
        off = np.stack([np.cos(ang), np.sin(ang)], 1) * r * 0.98
        kids = np.empty((2 * len(par), 2))
        kids[0::2], kids[1::2] = par + off, par - off
        gens.append(_relax(kids, r))
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(_CACHE, **{f"g{g}": a for g, a in enumerate(gens)})
    return gens


def _ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def state(g_float, gens):
    """Centres and radii at a fractional generation: g_float = k-1+u is the division k at progress u."""
    if g_float <= 0:
        return gens[0], np.full(1, radius(0)), 0.0
    k = min(int(math.ceil(g_float)), GENS)
    u = _ease(g_float - (k - 1))
    par = np.repeat(gens[k - 1], 2, axis=0)
    pos = par + (gens[k] - par) * u
    r = radius(k - 1) * (1 - u) + radius(k) * u
    return pos, np.full(len(pos), r), u


def cells_frame(gen_at, color_hex, jiggle=0.012):
    """`frame(t)` for a FramesLayer: draw the colony at generation `gen_at(t)` (fractional)."""
    import skia
    gens = generations()
    W, H = int(CELL_W * PPU), int(CELL_H * PPU)
    rr, gg, bb = (int(color_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    rng = np.random.default_rng(SEED + 1)
    phase = rng.uniform(0, 2 * math.pi, (2 ** GENS, 2))

    def frame(t):
        g = float(gen_at(t))
        pos, r, u = state(g, gens)
        n = len(pos)
        wob = jiggle * np.sin(0.9 * t + phase[:n]) * min(1.0, r[0] / 0.2)
        px = (pos[:, 0] + wob[:, 0]) * PPU + W / 2
        py = H / 2 - (pos[:, 1] + wob[:, 1]) * PPU
        rp = r * PPU
        surf = skia.Surface(W, H)
        cv = surf.getCanvas()
        cv.clear(skia.ColorTRANSPARENT)
        fill = skia.Paint(Color=skia.Color(rr, gg, bb, 46), AntiAlias=True)
        rim = skia.Paint(Color=skia.Color(rr, gg, bb, 235), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                         StrokeWidth=float(max(1.4, rp[0] * 0.07)))
        nuc = skia.Paint(Color=skia.Color(rr, gg, bb, 120), AntiAlias=True)
        for x, y, q in zip(px, py, rp):
            cv.drawCircle(float(x), float(y), float(q), fill)
        for x, y, q in zip(px, py, rp):
            cv.drawCircle(float(x), float(y), float(q * 0.97), rim)
        nr = rp * 0.26 * (1 - 0.6 * math.sin(math.pi * u))     # the nucleus shrinks mid-division
        for x, y, q, s in zip(px, py, nr, rp):
            cv.drawCircle(float(x + 0.18 * s), float(y - 0.14 * s), float(q), nuc)
        return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    return frame


if __name__ == "__main__":
    gs = generations()
    print([len(g) for g in gs], "colony radius", float(np.hypot(*gs[-1].T).max() + radius(GENS)))
