"""Chapter 10 (Black–Scholes): shared geometry and maths for scenes s31–s33.

Everything plotted is computed: the payoff max(S − K, 0) with K = 100; risk-neutral GBM paths (sims.gbm_paths,
σ = 20 %, r = 3 %, seeded) and their histogram at expiry; a delta hedge rebalanced daily along one seeded path,
whose difference from the option's Black–Scholes value is what stays after the randomness cancels; and the value
surface V(S, τ) from the closed form, which shaders/hill.frag (mode 2) draws with the same formula.
"""
from __future__ import annotations

import math

import numpy as np
from aion import C
from scipy.stats import norm

from kit import P3, lin_rgb, mix, tint

K, R, SIGMA = 100.0, 0.03, 0.2


def call(S, tau):
    """Black–Scholes call value (K, r, σ above); tau → 0 gives max(S − K, 0)."""
    S, tau = np.asarray(S, float), np.maximum(np.asarray(tau, float), 1e-9)
    d1 = (np.log(S / K) + (R + 0.5 * SIGMA ** 2) * tau) / (SIGMA * np.sqrt(tau))
    d2 = d1 - SIGMA * np.sqrt(tau)
    return S * norm.cdf(d1) - K * np.exp(-R * tau) * norm.cdf(d2)


def delta(S, tau):
    tau = np.maximum(np.asarray(tau, float), 1e-9)
    d1 = (np.log(np.asarray(S, float) / K) + (R + 0.5 * SIGMA ** 2) * tau) / (SIGMA * np.sqrt(tau))
    return norm.cdf(d1)


# ------------------------------------------------------------------------------------------ the payoff (c10_s01)
PX0, PX1, PY0, PY1 = -4.6, 1.8, -2.35, 1.25            # payoff axes box: price at expiry 0 … 200 on x, value 0 … 100
S_MAX, V_MAX = 200.0, 100.0


def ppt(S, V):
    return np.array([PX0 + (PX1 - PX0) * S / S_MAX, PY0 + (PY1 - PY0) * V / V_MAX])


# ----------------------------------------------------------------------- the price chart (c09_s03 → c10_s02)
OX, TX, CY0, CY1 = -4.6, 1.6, -2.3, 2.2                 # price axis at OX, one year ahead at TX
P_LO, P_HI = 40.0, 200.0


def cy(S):
    return CY0 + (CY1 - CY0) * (np.asarray(S, float) - P_LO) / (P_HI - P_LO)


def cx(t):
    return OX + (TX - OX) * np.asarray(t, float)


def paths(n=2000):
    import sims
    return sims.gbm_paths(n)


PIX = 135                                              # px per unit at 1080p


def fan_rgba(n=2000):
    """All n paths as a density image over the chart box (additive: counts of densely sampled points, log scaled),
    in the chapter hue. Columns are time, so revealing columns left to right draws the fan as time passes."""
    t, S = paths(n)
    W, H = int((TX - OX) * PIX), int((CY1 - CY0) * PIX)
    tt = np.linspace(0, 1, len(t) * 4)
    acc = np.zeros((H, W))
    for k in range(S.shape[1]):
        s = np.interp(tt, t, S[:, k])
        x = ((cx(tt) - OX) / (TX - OX) * (W - 1)).astype(int)
        y = ((CY1 - cy(s)) / (CY1 - CY0) * (H - 1)).astype(int)
        ok = (y >= 0) & (y < H)
        np.add.at(acc, (y[ok], x[ok]), 1.0)
    a = np.log1p(acc) / np.log1p(np.percentile(acc[acc > 0], 99.5))
    a = np.clip(a, 0, 1)
    h = str(C.bs).lstrip("#")
    img = np.zeros((H, W, 4), np.uint8)
    img[..., :3] = [int(h[i:i + 2], 16) for i in (0, 2, 4)]       # sRGB, straight alpha
    img[..., 3] = (a * 0.9 * 255).astype(np.uint8)
    return img


def expiry_hist(n=2000, bins=40):
    """Histogram of prices at expiry (counts, bin edges) over [P_LO, P_HI]."""
    _, S = paths(n)
    return np.histogram(S[-1], bins=bins, range=(P_LO, P_HI))


def lognormal_pdf(S, S0=100.0, T=1.0):
    m = math.log(S0) + (R - 0.5 * SIGMA ** 2) * T
    s = SIGMA * math.sqrt(T)
    S = np.asarray(S, float)
    return np.exp(-(np.log(S) - m) ** 2 / (2 * s * s)) / (S * s * math.sqrt(2 * math.pi))


# ---------------------------------------------------------------------------------------------- the hedge
def hedge(seed=1973, steps=252, S0=100.0):
    """One seeded price path; the option's value along it; a portfolio of Δ shares plus cash, rebalanced daily,
    started at the option's price. Returns t, S, option value, portfolio value."""
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    z = rng.standard_normal(steps)
    S = S0 * np.exp(np.concatenate([[0], np.cumsum((R - 0.5 * SIGMA ** 2) * dt + SIGMA * math.sqrt(dt) * z)]))
    t = np.linspace(0, 1, steps + 1)
    V = call(S, 1 - t)
    port = np.zeros_like(S)
    port[0] = V[0]
    d = delta(S[0], 1.0)
    cash = V[0] - d * S[0]
    for i in range(1, steps + 1):
        cash *= math.exp(R * dt)
        port[i] = d * S[i] + cash
        d = delta(S[i], 1 - t[i]) if i < steps else d
        cash = port[i] - d * S[i]
    return t, S, V, port


# ------------------------------------------------------------------------------- the value surface (c10_s03)
def surf_S(x):
    return 120.0 + 80.0 * np.asarray(x, float) / 3.0


def surf_x(S):
    return (np.asarray(S, float) - 120.0) * 3.0 / 80.0


def surf_tau(y):
    return np.maximum((np.asarray(y, float) + 3.0) / 6.0, 1e-4)


def surf_y(tau):
    return np.asarray(tau, float) * 6.0 - 3.0


def surface(x, y):
    """Height of the value surface at (x, y) before the height scale: V / 40 (as in hill.frag mode 2)."""
    return call(surf_S(x), surf_tau(y)) / 40.0


def surf_uniforms(cam_fn, zs, opacity):
    """Keyword arguments for s.shader('hill.frag', …) in mode 2."""
    from aion import Track

    def tr(f):
        return f if callable(f) else (lambda t, v=f: v)
    basis = lambda i: Track(lambda t: tuple(float(v) for v in cam_fn(t).basis()[i]))
    return dict(u_eye=basis(0), u_fwd=basis(1), u_right=basis(2), u_up=basis(3),
                u_f=Track(lambda t: float(cam_fn(t).f)), u_off=Track(lambda t: tuple(map(float, cam_fn(t).off))),
                u_mode=2.0, u_zs=Track(lambda t: float(tr(zs)(t))), u_dom=3.0, u_fog=0.0, u_walker=(0.0, 0.0),
                u_fr=1.0, u_lo=tuple(map(float, lin_rgb(tint(C.bs, 0.05)))),
                u_hi=tuple(map(float, lin_rgb(mix(C.bs, C.light, 0.35)))), u_contour=0.2,
                u_opacity=Track(lambda t: float(tr(opacity)(t))))


def on_surface(S, tau, zs, lift=0.03):
    S, tau = np.broadcast_arrays(np.atleast_1d(np.asarray(S, float)), np.atleast_1d(np.asarray(tau, float)))
    x, y = surf_x(S), surf_y(tau)
    return np.c_[x, y, zs * surface(x, y) + lift]


FEW, FEW_TRAVEL = 40, 10.0                            # the first paths, drawn as lines while the narration asks


def few_paths(t, t_start, a=1.0):
    """The first FEW paths, grown to time u = (t − t_start) / FEW_TRAVEL of the year."""
    from manim import VGroup

    from kit import polyline
    u = float(np.clip((t - t_start) / FEW_TRAVEL, 0, 1))
    g = VGroup()
    if a < 0.01 or u <= 0:
        return g
    tt, S = paths(FEW)
    k = max(int(u * (len(tt) - 1)), 1)
    for j in range(FEW):
        g.add(polyline(list(zip(cx(tt[:k + 1]), cy(S[:k + 1, j]))), C.bs, 1.2, 0.45 * a))
    return g


def chart_axes():
    """The price chart: price up the left, time to a year from now, and today's price."""
    from manim import DOWN, LEFT, RIGHT, UP, DashedLine, Dot, Line, VGroup

    from kit import sans
    today = P3(OX, float(cy(100.0)))
    return VGroup(Line(P3(OX, CY0), P3(OX, CY1 + 0.1), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
                  Line(P3(OX, CY0), P3(TX + 0.3, CY0), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
                  sans("price", 22, C.muted).next_to(P3(OX, CY1 + 0.1), UP, buff=0.1),
                  sans("time", 22, C.muted).next_to(P3(TX + 0.3, CY0), RIGHT, buff=0.12),
                  DashedLine(P3(TX, CY0), P3(TX, CY1), dash_length=0.08, stroke_color=tint(C.muted, 0.5),
                             stroke_width=1.2),
                  sans("a year from now", 20, C.muted).next_to(P3(TX, CY0), DOWN, buff=0.15),
                  Dot(today, radius=0.07, color=C.light), sans("today", 20, C.text).next_to(today, LEFT, buff=0.15))


# ------------------------------------------------------------------------------------- Fourier's bar (callback)
def bar_group(xs, un, a, bx0=-3.2, bx1=3.2, by=-1.9, bh=0.42, curve=1.0, cells=True):
    """Fourier's bar drawn from a temperature profile `un` (0..1) at positions xs: heated cells, the bar's two edges,
    and the temperature curve above it (opacity × `curve`). `cells=False` gives the curve alone, so it can sit in a
    glow layer without the cold (black) cells glowing too."""
    from manim import Line, Rectangle, VGroup

    from ch5 import heat_ramp
    from kit import polyline
    g = VGroup()
    if a < 0.01:
        return g
    seg = (bx1 - bx0) / len(xs)
    for x, v in (zip(xs, un) if cells else ()):
        g.add(Rectangle(width=seg * 1.05, height=bh, stroke_width=0, fill_color=heat_ramp(v, C.fourier, C.light),
                        fill_opacity=a).move_to(P3(bx0 + (bx1 - bx0) * x, by)))
    for yy in ((by - bh / 2, by + bh / 2) if cells else ()):
        g.add(Line(P3(bx0, yy), P3(bx1, yy), stroke_color=C.ghost, stroke_width=1.2, stroke_opacity=a))
    if curve * a > 0.01:
        g.add(polyline([(bx0 + (bx1 - bx0) * x, by + 0.5 + 1.6 * v) for x, v in zip(xs, un)], C.fourier, 3.5,
                       a * curve))
    return g


def hot_bar(t, t_on, op, cells=True, curve=True):
    """Fourier's hot bar cooling (as in c05_s01): the exact cosine-series solution u(x, t)."""
    import sims
    a = float(op(t))
    xs = np.linspace(0, 1, 160)
    if a < 0.01:
        return bar_group(xs, xs, 0.0)
    th = 0.0005 + 0.006 * max(t - t_on, 0.0)
    u, _ = sims.heat_bar(xs, th, n_modes=40)
    u0, _ = sims.heat_bar(xs, 0.0005, n_modes=40)
    return bar_group(xs, u / u0.max(), a, bx0=-3.2, bx1=3.2, by=-1.9, bh=0.42, curve=float(curve), cells=cells)
