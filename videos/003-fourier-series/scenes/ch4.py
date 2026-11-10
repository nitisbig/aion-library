"""Ch4 shared pieces: waves become drawings (S14–S18).

Everything is a pure function of absolute time: the chapter clocks are integrated rate
curves (`Clock`), so any frame renders alone and every cut matches by construction.
Chains are drawn in Manim, in the Ch1/Ch2 look: rims colored by speed sign (FWD +,
BWD −, STILL 0), silver arrow arms, a gold pen, gold ink.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from manim import Arc, Arrow, Circle, DashedLine, DashedVMobject, Dot, Line, MathTex, VGroup, VMobject

from aion import style as S
from aion.sync import Cue
import shared as V
import ch3 as H

TAU = 2 * np.pi
S14, S15, S16, S17, S18 = (V.scene_range(n) for n in (14, 15, 16, 17, 18))


@lru_cache(maxsize=1)
def _cue() -> Cue:
    return Cue.load(V.SRT)


def cue(key: str, scene: tuple[float, float], after: float | None = None) -> float:
    """Animation start for a cue word (word start − LEAD), searched from the scene start."""
    return _cue().at(key, after=scene[0] - 0.05 if after is None else after) - S.LEAD


class Clock:
    """∫ rate dt, where the rate eases (smoothstep) between levels: knots = [(t_start, ease_s, new_rate)…]."""

    def __init__(self, knots, t0: float, t1: float, dt: float = 1 / 600):
        self.t = np.arange(t0, t1 + dt, dt)
        r = np.zeros_like(self.t)
        rate = 0.0
        for ts, d, new in knots:
            u = np.clip((self.t - ts) / d, 0, 1)
            r = np.where(self.t >= ts, rate + (new - rate) * u * u * (3 - 2 * u), r)
            rate = new
        self.c = np.concatenate([[0.0], np.cumsum((r[1:] + r[:-1]) / 2 * dt)])

    def __call__(self, t):
        return np.interp(t, self.t, self.c)


def color_of(n: int):
    return S.FWD if n > 0 else (S.BWD if n < 0 else S.STILL)


def to3(z) -> np.ndarray:
    z = complex(z)
    return np.array([z.real, z.imag, 0.0])


def arm(a, b, op: float = 1.0, color=S.ARM, width: float = 3):
    if abs(b - a) < 0.05 or op <= 0:
        return VMobject()
    return Arrow(to3(a), to3(b), buff=0, color=color, stroke_width=width, tip_length=0.16,
                 max_tip_length_to_length_ratio=0.25, max_stroke_width_to_length_ratio=20).set_opacity(op)


def pen(z, op: float = 1.0):
    p = to3(z)
    return VGroup(Dot(p, radius=0.17, color=S.INK).set_opacity(0.22 * op), Dot(p, radius=0.07, color=S.INK).set_opacity(op))


def chain(vecs, origin=0j, rim_op=1.0, arm_op=1.0, pen_op=1.0, colors=None, rim_w: float = 3.0,
          ns=None, label_op: float | None = None, label_size: float = 28, label_angles=None):
    """Circles + arms for a list of arm vectors (complex, already rotated). Returns (mobject, pen point).

    ns: the circles' speeds; when given, each circle carries its term c_n e^{2πint} (term_label)."""
    from aion.components.term_label import exp_parts, labels
    g = VGroup()
    p = complex(origin)
    items = []
    for k, v in enumerate(vecs):
        r = abs(v)
        col = colors[k] if colors else S.FWD
        if ns is not None and k < len(ns):
            if label_angles:
                ang = label_angles[k]
            else:                                   # point away from the chain's root (less crowding)
                d = p - complex(origin)
                ang = float(np.degrees(np.angle(d))) if abs(d) > 0.05 else 125.0
            items.append((p, r, exp_parts(ns[k], col), col, ang))
        if rim_op > 0 and r > 0.01:
            g.add(Circle(radius=r, color=col, stroke_width=rim_w).move_to(to3(p)).set_stroke(opacity=min(1.0, S.RIM_BOOST * rim_op)))
        if arm_op > 0:
            g.add(Dot(to3(p), radius=0.045, color=S.ARM).set_opacity(arm_op))
        g.add(arm(p, p + v, arm_op))
        p = p + v
    if pen_op > 0:
        g.add(pen(p, pen_op))
    if items and V.TERM_LABELS:
        g.add(labels(items, op=min(1.0, 2.5 * rim_op) if label_op is None else label_op, size=label_size, min_r=0.28))
    return g, p


def path(z: np.ndarray, color=S.INK, width: float = 3.5, op: float = 1.0) -> VMobject:
    z = np.asarray(z, complex)
    if len(z) < 2 or op <= 0:
        return VMobject()
    return VMobject().set_points_as_corners(np.column_stack([z.real, z.imag, 0 * z.real])).set_stroke(color, width, op)


# ── S14: the two-circle chain, its two projections, then ink ───────────────
CC = complex(*H.SEED_CENTER[:2])          # chain center = where S13 left the circle
TERMS14 = [(1, 1j * H.SEED_R), (3, 0.3j)]  # arm 1 points up at t = 0 (the S13 seed)
X0, X_END = -1.8, 6.4                      # the height wave (as in Ch1)
Y0, Y_END = CC.imag - 2.0, -3.9            # the left-right wave runs down from here
V_SCROLL = 1.0


@lru_cache(maxsize=1)
def clock14() -> Clock:
    return Clock([(cue("height of the tip", S14), 1.0, 0.25), (cue("use both", S14), 0.8, 0.5)],
                 S14[0] - 30, S16[1] + 5)


def z14(c, r2: float = 1.0):
    """Pen offset (complex) at chain clock c (loops)."""
    c = np.asarray(c, float)
    (n1, a1), (n3, a3) = TERMS14
    return a1 * np.exp(1j * TAU * n1 * c) + r2 * a3 * np.exp(1j * TAU * n3 * c)


def vecs14(c, r2=1.0):
    (n1, a1), (n3, a3) = TERMS14
    return [a1 * np.exp(1j * TAU * n1 * c), r2 * a3 * np.exp(1j * TAU * n3 * c)]


def ink14(now: float, t_ink: float, op: float = 1.0, loops: float = 1.0) -> VMobject:
    """Gold ink drawn since t_ink (at most `loops` loops back)."""
    clk = clock14()
    c1 = float(clk(now))
    c0 = max(float(clk(t_ink)), c1 - loops)
    if c1 - c0 < 1e-4:
        return VMobject()
    c = np.linspace(c0, c1, max(2, int(900 * (c1 - c0))))
    return path(CC + z14(c), op=op)


# ── S15: Mars from Earth (real orbit sizes and periods, time compressed) ────
SKY_C = 0j                  # Earth's place on screen
SKY_K = 1.3                 # screen units per AU
A_MARS, P_MARS = 1.5237, 1.8808   # AU, years
W_E, W_M = TAU, TAU / P_MARS


@lru_cache(maxsize=1)
def years() -> Clock:
    """Sky clock in years: runs from "astronomers", eases to a stop on "almost any path"."""
    return Clock([(cue("astronomers", S15), 0.8, 0.7), (cue("almost any path", S15), 1.4, 0.0)],
                 S15[0] - 5, S17[1])


@lru_cache(maxsize=1)
def sky_phases() -> tuple[float, float]:
    """Phases putting an opposition (center of a retrograde loop) at the top, mid-aside."""
    y_opp = float(years()(cue("circles riding on circles", S15) + 2.0))
    alpha = np.pi / 2
    return alpha - W_E * y_opp, alpha - W_M * y_opp


def earth_helio(y):
    pe, _ = sky_phases()
    return np.exp(1j * (W_E * np.asarray(y, float) + pe))


def mars_helio(y):
    _, pm = sky_phases()
    return A_MARS * np.exp(1j * (W_M * np.asarray(y, float) + pm))


def sky_point(y, s: float = 0.0):
    """Screen point of Mars at sky-time y. s = 0: seen from Earth; s = 1: from the Sun."""
    return SKY_C + SKY_K * (mars_helio(y) - earth_helio(y) + s * earth_helio(y))


@lru_cache(maxsize=1)
def stars() -> VGroup:
    rng = np.random.default_rng(1807)
    n = 240
    x, y = rng.uniform(-7.1, 7.1, n), rng.uniform(-3.95, 3.95, n)
    r = 0.006 + 0.022 * rng.random(n) ** 3
    a = 0.25 + 0.6 * rng.random(n)
    return VGroup(*[Dot([x[i], y[i], 0], radius=r[i], color=S.LABEL).set_opacity(a[i]) for i in range(n)])


# ── S16: three speeds ──────────────────────────────────────────────────────
SLOTS16 = [complex(-4.3, 0.35), complex(0.0, 0.35), complex(4.3, 0.35)]
R16 = 1.1


def slot(center, r=R16, color=S.ARM, op: float = 0.35, n_dash: int = 40):
    return DashedVMobject(Circle(radius=r, color=color, stroke_width=2), num_dashes=n_dash).move_to(
        to3(center)).set_stroke(opacity=op)


def turn_arrow(center, r, sign: int, color):
    """A short curved arrow outside the rim showing the turning direction."""
    a0, a1 = (np.pi * 0.2, np.pi * 0.45) if sign > 0 else (np.pi * 0.8, np.pi * 0.55)
    arc = Arc(radius=r + 0.28, start_angle=a0, angle=a1 - a0, arc_center=to3(center), color=color, stroke_width=3)
    arc.add_tip(tip_length=0.16, tip_width=0.16)
    return arc


def rounded_loop(center, size: float, color=S.INK, width: float = 3.0):
    """The friendly example's path, small (the gold loop the green arm carries)."""
    t = np.linspace(0, 1, 400)
    return path(complex(center) + size * (np.exp(1j * TAU * t) - np.exp(-1j * TAU * 3 * t) / 9), color, width)


# ── S17: the friendly example, at the intro square's own size ──────────────
C1 = complex(V.square_coeffs()[1])          # 2.5219: the intro square's first circle
C3 = complex(V.square_coeffs()[-3])         # −0.2802 = −C1/9 (checked in beats.verify_math)
FRIEND = [(1, C1), (-3, C3)]


@lru_cache(maxsize=1)
def big_clock() -> Clock:
    """The big circle alone: exactly one turn, "turning forward once", stopping on "one ninth"."""
    t0, t1 = cue("turning", S17), cue("one ninth", S17)
    # one smooth turn over [t0, t1]: rate = smoothstep bump scaled to integrate to 1
    d = (t1 - t0) / 2
    return Clock([(t0, d, 1 / d), (t0 + d, d, 0.0)], S17[0] - 5, S18[1] + 5)


@lru_cache(maxsize=1)
def friend_clock() -> Clock:
    """Both circles together, from "backward": one loop per 4 s."""
    return Clock([(cue("backward", S17), 1.0, 0.25)], S17[0] - 5, S18[1] + 5)


def friend_vecs(now: float, r2: float = 1.0):
    """Arm vectors (big, small) at absolute time `now`."""
    b = float(big_clock()(now))
    c = float(friend_clock()(now))
    return [C1 * np.exp(1j * TAU * (b + c)), r2 * C3 * np.exp(-1j * TAU * 3 * c)]


def friend_ink(now: float, origin=0j, scale: float = 1.0, op: float = 1.0, width: float = 3.5) -> VMobject:
    c1 = float(friend_clock()(now))
    c0 = max(0.0, c1 - 1.0)
    if c1 - c0 < 1e-4:
        return VMobject()
    c = np.linspace(c0, c1, max(2, int(1200 * (c1 - c0))))
    z = C1 * np.exp(1j * TAU * c) + C3 * np.exp(-1j * TAU * 3 * c)
    return path(complex(origin) + scale * z, op=op, width=width)


def square_ghost(origin=0j, scale: float = 1.0, op: float = 0.5):
    h = V.SQUARE_HALF * scale
    o = complex(origin)
    pts = [o + h * complex(a, b) for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1), (1, 1))]
    m = VMobject().set_points_as_corners([to3(p) for p in pts]).set_stroke(S.INK, 2.5)
    return DashedVMobject(m, num_dashes=48).set_stroke(opacity=op)


INSET_AT, INSET_K, INSET_N = complex(5.25, -1.95), 0.48, 24


def square_inset(lit: float = 0.0, op: float = 1.0) -> VGroup:
    """The intro's square chain at t = 0, small: its first 24 circles and its square; `lit` lights the first two."""
    terms = V.square_terms()[:INSET_N]
    sq = path(INSET_AT + INSET_K * V.SQUARE_HALF * np.array([1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j, 1 + 1j]),
              S.INK, 2.0, 0.55 * op)
    rims, arms_ = VGroup(), VGroup()
    p = INSET_AT
    for k, (n, c) in enumerate(terms):
        v = INSET_K * c
        first = k < 2
        rim_op = (0.22 + (0.78 * lit if first else -0.12 * lit)) * op
        col = color_of(n) if first else S.ARM
        rims.add(Circle(radius=abs(v), color=col, stroke_width=2.5 if first else 1.5)
                 .move_to(to3(p)).set_stroke(opacity=min(1.0, S.RIM_BOOST * max(rim_op, 0.0))))
        arms_.add(Line(to3(p), to3(p + v), color=S.ARM, stroke_width=1.5)
                  .set_stroke(opacity=(0.5 + (0.5 * lit if first else -0.3 * lit)) * op))
        p = p + v
    return VGroup(sq, rims, arms_, pen(p, 0.8 * op))


# ── S18: the speed rack ────────────────────────────────────────────────────
RACK_Y, RACK_DX, RACK_R = -1.75, 1.18, 0.42
RACK_N = 5                                 # speeds −5…5
KNOB_ANGLE = np.deg2rad(40)


def rack_x(n: int) -> float:
    return n * RACK_DX


def rack_slot(n: int, op: float = 1.0) -> VGroup:
    c = complex(rack_x(n), RACK_Y)
    return slot(c, RACK_R, color_of(n), 0.55 * op, n_dash=22)


def rack_label(n: int) -> MathTex:
    txt = "0" if n == 0 else (f"{n}" if n > 0 else f"-{-n}")
    return MathTex(txt, font_size=34, color=color_of(n)).move_to([rack_x(n), RACK_Y - RACK_R - 0.38, 0])


def rack_knob(n: int, op: float = 1.0) -> VGroup:
    c = complex(rack_x(n), RACK_Y)
    tip = c + RACK_R * np.exp(1j * KNOB_ANGLE)
    return VGroup(Line(to3(c), to3(tip), color=S.ARM, stroke_width=1.5).set_stroke(opacity=0.45 * op),
                  Circle(radius=0.055, color=S.ARM, stroke_width=1.5).move_to(to3(tip)).set_stroke(opacity=0.6 * op))


def rack_tick(n: int, op: float = 1.0) -> VMobject:
    c = complex(rack_x(n), RACK_Y)
    return Arc(radius=0.2, start_angle=0, angle=KNOB_ANGLE, arc_center=to3(c), color=S.PHASE,
               stroke_width=2).set_stroke(opacity=0.7 * op)


def dashed_h(y, x0, x1, op):
    return DashedLine([x0, y, 0], [x1, y, 0], dash_length=0.08, color=S.ARM, stroke_width=1.5).set_stroke(opacity=op)
