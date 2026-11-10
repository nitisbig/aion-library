"""Outro shared pieces (S28–S30).

S28's four recap cards are live miniatures of the chapters. Every motion is a pure function of
absolute time (rates start on their cue words), so S29 starts from S28's last frame by calling
the same functions. Speeds and sizes are the real ones: the square wave's 4/(πn), the intro
square's c₁ and c₋₃ = −c₁/9, and the bean (beats.BEAN) turned backward once per loop, so its
speed-one arm stands still at arg c₁.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from manim import Circle, DashedVMobject, Line, RoundedRectangle, VGroup, VMobject

from aion import fourier as F
from aion import style as S
import shared as V
import ch4 as C4
import ch5 as C5
from ch4 import TAU, cue, path, to3

S28, S29, S30 = (V.scene_range(n) for n in (28, 29, 30))

CARD_W, CARD_H, CARD_Y = 3.0, 2.5, 0.65
CARD_X = (-4.95, -1.65, 1.65, 4.95)
RECIPE_AT = np.array([0.0, -2.35, 0.0])


@lru_cache(maxsize=1)
def T() -> dict:
    keys = (("wave", "simplest wave"), ("size", "size"), ("speed", "a speed"), ("start", "starting point"),
            ("stack", "stack circles"), ("sizes", "right sizes"), ("sharp", "sharp corners"),
            ("insight", "fouriers insight"), ("two", "two directions"), ("spin", "spin the drawing backward"),
            ("still", "stands still"), ("look", "looking for"))
    out, after = {}, None
    for k, key in keys:
        out[k] = cue(key, S28, after)
        after = out[k] + S.LEAD + 0.01
    return out


def center(i: int) -> complex:
    return complex(CARD_X[i], CARD_Y)


def card_frame(i: int, op: float = 1.0, color=S.LIGHT, width: float = 2.0) -> RoundedRectangle:
    return RoundedRectangle(corner_radius=0.22, width=CARD_W, height=CARD_H, color=color,
                            stroke_width=width).move_to(to3(center(i))).set_stroke(opacity=op)


def _since(now: float, t0: float, rate: float, ease: float = 0.6) -> float:
    """Loops turned since t0 at `rate` loops/s, with a smooth start (integral of an eased rate)."""
    u = now - t0
    if u <= 0:
        return 0.0
    if u < ease:
        x = u / ease
        return rate * ease * (x ** 3 - 0.5 * x ** 4)          # ∫ smoothstep
    return rate * (u - ease / 2)


# ── card 1: one circle, the simplest wave ──────────────────────────────────
R1, RATE1, K_WAVE = 0.42, 0.45, 2.2


def card1(now: float, op: float) -> VGroup:
    if op <= 0:
        return VGroup()
    c = center(0) + complex(-0.95, 0.2)
    L = _since(now, T()["wave"], RATE1)
    tip = c + R1 * np.exp(1j * TAU * L)
    x0, x1 = c.real + 0.65, center(0).real + 1.35
    x = np.linspace(x0, x1, 300)
    y = c.imag + R1 * np.sin(TAU * L - K_WAVE * (x - x0))
    g = VGroup(Circle(radius=R1, color=S.ARM, stroke_width=2).move_to(to3(c)).set_stroke(opacity=0.7 * op),
               C4.arm(c, tip, op), path(x + 1j * y, S.INK, 2.6, op),
               Line(to3(tip), to3(complex(x0, tip.imag)), color=S.ARM, stroke_width=1.2).set_stroke(opacity=0.4 * op),
               C4.pen(complex(x0, tip.imag), op))
    return g


def chips(vis: tuple, op: float = 1.0) -> VGroup:
    """'size', 'speed', 'start' under card 1 (vis: three opacities)."""
    g = VGroup()
    for k, (word, col) in enumerate((("size", S.LABEL), ("speed", S.FWD), ("start", S.PHASE))):
        if vis[k] > 0:
            g.add(V.label(word, 20, col).move_to(to3(center(0) + complex(-0.95 + 0.95 * k, -0.8)))
                  .set_opacity(vis[k] * op))
    return g


# ── card 2: stacked circles build the square wave ──────────────────────────
RATE2, SCALE2, N2 = 0.3, 0.27, 12


def n_terms2(now: float) -> float:
    """2 circles from "stack circles", growing to 12 between "right sizes" and "sharp corners"."""
    u = np.clip((now - T()["sizes"]) / (T()["sharp"] + 0.4 - T()["sizes"]), 0, 1)
    return 2 + (N2 - 2) * u * u * (3 - 2 * u)


def card2(now: float, op: float) -> VGroup:
    if op <= 0:
        return VGroup()
    c = center(1) + complex(-0.62, 0.2)
    L = _since(now, T()["stack"], RATE2)
    nf = n_terms2(now)
    ns = np.arange(1, 2 * N2, 2)
    w = np.clip(nf - np.arange(N2), 0, 1)                    # each new circle grows in
    r = SCALE2 * 4 / (np.pi * ns) * w
    vs = [rk * np.exp(1j * TAU * n * L) for n, rk in zip(ns, r) if rk > 1e-4]
    ch, tip = C4.chain(vs, c, rim_op=0.5 * op, arm_op=0.9 * op, pen_op=0.0,
                       colors=[S.FWD] * len(vs), rim_w=1.4)
    x0, x1 = c.real + 0.55, center(1).real + 1.35
    x = np.linspace(x0, x1, 500)
    ph = TAU * L - K_WAVE * (x - x0) * 0.8
    y = c.imag + sum(rk * np.sin(n * ph) for n, rk in zip(ns, r))
    return VGroup(ch, path(x + 1j * y, S.INK, 2.6, op),
                  Line(to3(tip), to3(complex(x0, tip.imag)), color=S.ARM, stroke_width=1.2).set_stroke(opacity=0.4 * op),
                  C4.pen(complex(x0, tip.imag), op))


# ── card 3: two directions: the rounded square ─────────────────────────────
RATE3 = 0.3


@lru_cache(maxsize=1)
def rs3():
    c = V.square_coeffs()
    k = 0.62 / abs(c[1])
    return [(1, k * c[1]), (-3, k * c[-3])], k


def card3_ghost(op: float) -> VMobject:
    _, k = rs3()
    sq = center(2) + k * V.SQUARE_HALF * F.square_loop(400, 1.0)
    return DashedVMobject(path(np.append(sq, sq[0]), S.ARM, 1.5, 0.5 * op), num_dashes=40)


def card3(now: float, op: float) -> VGroup:
    if op <= 0:
        return VGroup()
    terms, _ = rs3()
    L = _since(now, T()["two"], RATE3)
    vs = [c * np.exp(1j * TAU * n * L) for n, c in terms]
    ch, tip = C4.chain(vs, center(2), rim_op=0.6 * op, arm_op=op, pen_op=op, colors=[S.FWD, S.BWD], rim_w=1.6)
    s = np.linspace(max(0.0, L - 1.0), L, 400)
    z = center(2) + sum(c * np.exp(1j * TAU * n * s) for n, c in terms)
    return VGroup(path(z, S.INK, 2.6, op) if L > 0.002 else VMobject(), ch)


# ── card 4: spin the drawing backward; the speed-one arm stands still ─────
RATE4, SCALE4 = 0.3, 0.5


@lru_cache(maxsize=1)
def bean4():
    terms = C5.bean_terms_size()                              # speed 1 first
    t = np.linspace(0, 1, 800)
    z = SCALE4 * sum(c * np.exp(1j * TAU * n * t) for n, c in terms)
    off = -0.5 * (z.real.max() + z.real.min()) - 0.5j * (z.imag.max() + z.imag.min())
    return terms, off


def card4(now: float, op: float, glow: float = 0.0) -> VGroup:
    """The bean and its chain in the frame turned backward once per loop (rotate the world by −2πL)."""
    if op <= 0:
        return VGroup()
    terms, off = bean4()
    L = _since(now, T()["spin"], RATE4)
    rot = np.exp(-1j * TAU * L)
    root = center(3) + off
    t = np.linspace(0, 1, 800)
    z = root + rot * SCALE4 * sum(c * np.exp(1j * TAU * n * t) for n, c in terms)
    vs = [rot * SCALE4 * c * np.exp(1j * TAU * n * L) for n, c in terms]
    cols = [S.STILL] + [S.ARM] * (len(vs) - 1)
    ch, _ = C4.chain(vs, root, rim_op=0.35 * op, arm_op=0.8 * op, pen_op=op, colors=cols, rim_w=1.2)
    g = VGroup(path(np.append(z, z[0]), S.INK, 2.2, 0.75 * op), ch,
               C4.arm(root, root + vs[0], op, color=S.STILL, width=3.5 + 4 * glow),
               C5.frame_ring(TAU * L, op, center(3), 1.1))
    return g


# ── S29: a sound that never repeats; the speeds melt into a band ───────────
NR_Y, NR_X0, NR_X1 = 1.35, -6.2, 6.2
NR_FREQ = (1.0, np.sqrt(2.0), np.pi / 2, np.e / 1.9, np.sqrt(7.0) / 1.3)


@lru_cache(maxsize=1)
def _nr_env():
    rng = np.random.default_rng(2901)
    return rng.uniform(0, TAU, len(NR_FREQ)), rng.uniform(0.5, 1.0, len(NR_FREQ))


def never_wave(now: float, t0: float, op: float = 1.0, speed: float = 1.6) -> VMobject:
    """Incommensurate frequencies under a slow envelope: no period, scrolling left from t0."""
    if op <= 0:
        return VMobject()
    ph, amp = _nr_env()
    x = np.linspace(NR_X0, NR_X1, 1400)
    s = 2.2 * x + speed * 2.2 * (now - t0)
    y = sum(a * np.sin(f * s + p) for f, a, p in zip(NR_FREQ, amp, ph))
    env = 0.6 + 0.4 * np.sin(0.23 * s + 1.0) * np.sin(0.071 * s + 0.4)
    y = 0.75 * env * y / 3.2
    return path(x + 1j * (NR_Y + y), S.INK, 3.0, op)


BAND_Y, BAND_H, BAND_X = -1.9, 1.7, 5.4      # speeds −5…5 across ±BAND_X


def spectrum(w: np.ndarray) -> np.ndarray:
    """A smooth, made-up but continuous spectrum for the never-repeating sound (peaks at its frequencies)."""
    out = 0.12 * np.exp(-(w / 4.5) ** 2)
    for f, a in zip(NR_FREQ, _nr_env()[1]):
        out = out + a * np.exp(-((np.abs(w) - 2.2 * f) / 0.55) ** 2)
    return out / out.max()


def band(m: float, op: float = 1.0) -> VGroup:
    """m = 0: integer bars at −5…5; m → 1: ever more bars, thicker, melting into one glowing band."""
    if op <= 0:
        return VGroup()
    n = int(round(11 + (2 ** (7 * m) - 1) * 10))
    w = np.linspace(-5, 5, n) if m > 0 else np.arange(-5, 6, dtype=float)
    h = BAND_H * spectrum(w)
    g = VGroup()
    sw = 6 + 20 * m
    bar_op = op * (1 - np.clip((m - 0.75) / 0.25, 0, 1) * 0.6)
    for wk, hk in zip(w, h):
        col = S.FWD if wk > 1e-9 else (S.BWD if wk < -1e-9 else S.STILL)
        x = BAND_X * wk / 5
        g.add(Line([x, BAND_Y, 0], [x, BAND_Y + max(hk, 0.01), 0], color=col, stroke_width=sw)
              .set_stroke(opacity=bar_op))
    f = np.clip((m - 0.6) / 0.4, 0, 1)
    if f > 0:
        ww = np.linspace(-5, 5, 600)
        for sgn, col in ((-1, S.BWD), (1, S.FWD)):
            sel = ww * sgn >= 0
            xs, hs = BAND_X * ww[sel] / 5, BAND_H * spectrum(ww[sel])
            pts = np.concatenate([[xs[0] + 1j * BAND_Y], xs + 1j * (BAND_Y + hs), [xs[-1] + 1j * BAND_Y]])
            g.add(VMobject().set_points_as_corners([to3(p) for p in pts]).set_fill(col, 0.55 * f * op)
                  .set_stroke(col, 2.5, f * op))
    g.add(Line([-BAND_X - 0.3, BAND_Y, 0], [BAND_X + 0.3, BAND_Y, 0], color=S.ARM, stroke_width=1.5)
          .set_stroke(opacity=0.5 * op))
    return g
