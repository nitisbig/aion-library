"""Ch2 shared machine: stacked circles building the square wave (S07–S10).

Everything about the chain is a pure function of absolute audio time:
  • the clock c(t): real time, slowed to a crawl on "take a moment to guess", eased back
    up as S09 starts, and eased to a full stop as S10 starts (the zoom needs a still wave);
  • the circles: circle k has speed n = 2k+1 and size a_k·g_k(t), where g_k is its
    arrival (0→1). The first four arrive on their words (S07–S08); from S09 on, N(t)
    circles are present, locked to "ten", "fifty", "two hundred".
The wave on screen is always drawn from the current circles (it reshapes in place, as
in Ch1), so every cut matches by construction.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from manim import (LEFT, Arrow, Circle, DashedLine, DashedVMobject, Dot, Line, VGroup, VMobject)

from aion import style as S
import shared as V
import ch1 as C1

CUE = C1.CUE
CX, X0, X_END, V_SCROLL, R0 = C1.CX, C1.X0, C1.X_END, C1.V_SCROLL, C1.R0
S07, S08, S09, S10 = (V.scene_range(k) for k in (7, 8, 9, 10))
H = 1.0                                   # target height of the square wave (S08's hairlines)
A1 = 4 / np.pi * H                        # first circle of the square wave: "a little taller"
K = 200                                   # circles at most
NS = 2 * np.arange(K) + 1                 # speeds 1, 3, 5, …, 399
L = S.LEAD


def at(key, scene):
    return CUE.at(key, after=scene[0] - 0.05) - L


def _sm(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def ramp(t, t0, d):
    return _sm((t - t0) / d)


# ── times (absolute, cue-derived) ──────────────────────────────────────────
T_SMALL = at("smaller circle", S07)
T_DELIB = at("deliberate", S08)
T_TALL = at("a little taller", S08)
T_THREE = at("three times as fast", S08)
T_FIVE = at("five times as fast", S08)
T_SEVEN = at("seven times", S08)
T_GUESS = at("take a moment to guess", S08)
T_FLAT = at("top flatten", S09)
T_TEN, T_FIFTY, T_200 = at("ten circles", S09), at("fifty", S09), at("two hundred", S09)
T_STOP = S10[0]


# ── the clock ──────────────────────────────────────────────────────────────
def rate(t):
    t = np.asarray(t, float)
    slow = 1 - 0.85 * ramp(t, T_GUESS, 0.4) * (1 - ramp(t, S09[0], T_FLAT - S09[0]))
    return slow * (1 - ramp(t, T_STOP, 1.3))


_T0, _DT = 120.0, 1e-3
_GRID = _T0 + np.arange(int((215 - _T0) / _DT) + 1) * _DT
_CUM = _T0 + np.concatenate([[0.0], np.cumsum((rate(_GRID[:-1]) + rate(_GRID[1:])) / 2 * _DT)])


def clock(t):
    """Chapter clock: equals t before the guess pause."""
    return np.interp(t, _GRID, _CUM)


def theta(t):
    """Angle of the speed-1 circle at absolute time t (continues Ch1's arm exactly)."""
    return C1.base_angle(clock(t))


# ── the circles ────────────────────────────────────────────────────────────
def n_circles(t: float) -> float:
    """How many circles are present (fractional while one arrives)."""
    if t < S09[0]:
        return 4.0
    # each spoken number holds for a moment before the next climb starts
    keys = [(S09[0], 4.0), (T_TEN, 10.0), (T_TEN + 0.45, 10.0), (T_FIFTY, 50.0), (T_FIFTY + 0.4, 50.0),
            (T_200, 200.0)]
    for (ta, na), (tb, nb) in zip(keys, keys[1:]):
        if t < tb:
            return na + (nb - na) * float(_sm((t - ta) / (tb - ta)))
    return 200.0


def amps(t: float) -> np.ndarray:
    """Current radius of every circle (0 for circles not there yet)."""
    a = np.zeros(K)
    # circle 1: R0 (Ch1) → H on "deliberate" → 4/π·H on "a little taller"
    a[0] = R0 + (H - R0) * ramp(t, T_DELIB, 0.8) + (A1 - H) * ramp(t, T_TALL, 0.6)
    # circle 2: S07's R0/3 arrives, leaves on "deliberate", returns as A1/3
    if t < T_THREE - 0.01:
        a[1] = R0 / 3 * ramp(t, T_SMALL, 0.7) * (1 - ramp(t, T_DELIB, 0.8))
    else:
        a[1] = A1 / 3 * ramp(t, T_THREE, 0.7)
    a[2] = A1 / 5 * ramp(t, T_FIVE, 0.7)
    a[3] = A1 / 7 * ramp(t, T_SEVEN, 0.7)
    N = n_circles(t)
    k = np.arange(4, K)
    a[4:] = A1 / NS[4:] * np.clip(N - k, 0.0, 1.0)
    return a


def square_sum(theta_arr, a) -> np.ndarray:
    """Σ a_k sin(n_k θ) for an array of angles (only circles that are present)."""
    idx = np.nonzero(a > 1e-9)[0]
    out = np.zeros_like(np.asarray(theta_arr, float))
    for k in idx:
        out += a[k] * np.sin(NS[k] * theta_arr)
    return out


def joints(t: float) -> np.ndarray:
    """Chain joints (complex, Manim coords): origin, after circle 1, …, pen."""
    a = amps(t)
    th = theta(t)
    steps = a * np.exp(1j * NS * th)
    return complex(CX[0], CX[1]) + np.concatenate([[0], np.cumsum(steps)])


def p3(z):
    return np.array([z.real, z.imag, 0.0])


def ideal_square(theta_arr):
    return H * np.sign(np.sin(theta_arr))


def gibbs_peak_height(n_terms: int) -> float:
    """Height of the overshoot crest, relative to H, for the first n_terms circles."""
    from aion import fourier as F
    return float(F.gibbs_peak(n_terms))


# ── the picture ────────────────────────────────────────────────────────────
OPS = ("master", "rim_op", "arm_op", "conn_op", "track_op", "axis_op", "trail_op", "ghost_op",
       "dash_op", "bar1_op", "bar2_op", "hair_op", "sq_op", "tops", "bottoms", "walls", "strip_op",
       "frac_op")
S07_START = dict(master=1.0, rim_op=0.4, arm_op=1.0, conn_op=1.0, track_op=1.0, axis_op=1.0,
                 trail_op=1.0, ghost_op=0.0, dash_op=0.0, bar1_op=0.0, bar2_op=0.0, hair_op=0.0,
                 sq_op=0.0, tops=0.0, bottoms=0.0, walls=0.0, strip_op=0.0, frac_op=0.0)
S07_END = {**S07_START, "ghost_op": 1.0}
S08_END = {**S07_START, "hair_op": 1.0, "strip_op": 1.0, "frac_op": 1.0}

# spectrum strip (bottom right): bar for speed n at x = SX + n·w
SX, SY, SW, SH = 2.6, -3.35, 3.6, 0.75


class Stack:
    """Stacked-circle picture for Ch2. Manim draws circles ≤ 4; S09 adds an EpicyclePlate."""

    def __init__(self, scene, state: dict, manim_circles: int = 4):
        self.scene = scene
        self.v = {k: _tracker(state.get(k, 0.0)) for k in OPS}
        self.mc = manim_circles
        scene.add(*self.v.values())
        R = V.redraw
        self.parts = VGroup(R(self._axis), R(self._hair), R(self._track), R(self._rims), R(self._dash),
                            R(self._ghost), R(self._wave), R(self._square), R(self._conn), R(self._bars),
                            R(self._arms), R(self._marker), R(self._pen), R(self._strip))
        scene.add(self.parts)

    def __getitem__(self, k):
        return self.v[k].get_value()

    def op(self, k):
        return self[k] * self["master"]

    def to(self, **kw):
        return [self.v[k].animate.set_value(v) for k, v in kw.items()]

    @property
    def now(self):
        return self.scene.now

    def taus(self, x):
        return clock(self.now) - (x - X0) / V_SCROLL

    def xs(self, dense: float = 90):
        return np.linspace(X0, X_END, int(dense * (X_END - X0)))

    def height(self):
        return float(joints(self.now)[-1].imag)

    # pieces ---------------------------------------------------------------
    def _rims(self):
        op = self.op("rim_op")
        if op <= 0:
            return VMobject()
        a, J = amps(self.now), joints(self.now)
        g = VGroup()
        for k in range(self.mc):
            if a[k] > 0.01:
                g.add(Circle(radius=a[k], color=S.FWD, stroke_width=3).move_to(p3(J[k])).set_stroke(opacity=min(1.0, S.RIM_BOOST * op)))
        hub = Dot(p3(J[0]), radius=0.045, color=S.ARM).set_opacity(self.op("arm_op"))
        return VGroup(g, hub, self._terms(a, J, min(1.0, 3 * op)))

    def _terms(self, a, J, op):
        """Each circle's sine term: 1/n sin nt (relative), 4/(nπ) sin nt once the wave is the square wave's."""
        from aion.components.term_label import label, sin_tex
        if not V.TERM_LABELS or op <= 0:
            return VGroup()
        true = self.now >= T_TALL
        items = []
        for k in range(min(self.mc, 3)):
            n = int(NS[k])
            if true:
                amp = r"\tfrac{4}{\pi}" if n == 1 else rf"\tfrac{{4}}{{{n}\pi}}"
            else:
                amp = "" if n == 1 else rf"\tfrac{{1}}{{{n}}}"
            if a[k] < 0.08:
                continue
            m = label(sin_tex(n, amp), [0, 0, 0], size=28, color=S.LABEL, op=op * min(1.0, a[k] / 0.25))
            m.move_to([J[0].real - 0.95, J[0].imag - a[0] - 0.45 - 0.58 * k, 0], aligned_edge=LEFT)   # a column under the stack
            items.append(m)
        return VGroup(*items)

    def _arms(self):
        op = self.op("arm_op")
        if op <= 0:
            return VMobject()
        a, J = amps(self.now), joints(self.now)
        g = VGroup()
        for k in range(self.mc):
            if a[k] > 0.05:
                tl = 0.16 if k == 0 else 0.11
                g.add(Arrow(p3(J[k]), p3(J[k + 1]), buff=0, color=S.ARM, stroke_width=3 if k == 0 else 2.2,
                            tip_length=tl, max_tip_length_to_length_ratio=0.25,
                            max_stroke_width_to_length_ratio=20).set_opacity(op))
        return g

    def _pen(self):
        op = self.op("conn_op") if self["conn_op"] > 0 else self.op("arm_op")
        p = p3(joints(self.now)[-1])
        return VGroup(Dot(p, radius=0.17, color=S.INK).set_opacity(0.22 * op),
                      Dot(p, radius=0.07, color=S.INK).set_opacity(op))

    def _track(self):
        r = float(min(amps(self.now).sum(), 1.45))       # the tip can reach this high
        return Line([X0, -r, 0], [X0, r, 0], color=S.ARM, stroke_width=1.5).set_stroke(
            opacity=0.45 * self.op("track_op"))

    def _marker(self):
        op = self.op("track_op")
        p = np.array([X0, self.height(), 0])
        return VGroup(Dot(p, radius=0.17, color=S.INK).set_opacity(0.22 * op),
                      Dot(p, radius=0.07, color=S.INK).set_opacity(op))

    def _conn(self):
        p, q = p3(joints(self.now)[-1]), np.array([X0, self.height(), 0])
        if self["conn_op"] <= 0 or abs(q[0] - p[0]) < 0.1:
            return VMobject()
        return DashedLine(p, q, dash_length=0.08, color=S.ARM, stroke_width=1.5).set_stroke(
            opacity=0.55 * self.op("conn_op"))

    def _axis(self):
        return Line([X0, 0, 0], [X_END, 0, 0], color=S.ARM, stroke_width=1.2).set_stroke(
            opacity=0.4 * self.op("axis_op"))

    def _hair(self):
        op = self.op("hair_op")
        if op <= 0:
            return VMobject()
        return VGroup(*[DashedLine([X0, y, 0], [X_END, y, 0], dash_length=0.1, color=S.ARM, stroke_width=1.2)
                        .set_stroke(opacity=0.35 * op) for y in (H, -H)])

    def _wave(self):
        op = self.op("trail_op")
        if op <= 0:
            return VMobject()
        x = self.xs(120 if n_circles(self.now) < 20 else 420)
        y = square_sum(theta_tau(self.taus(x)), amps(self.now))
        return VMobject().set_points_as_corners(np.column_stack([x, y, 0 * x])).set_stroke(S.INK, 3.5, op)

    def _ghost(self):
        """S07: the plain one-circle sine, left as a dim reference."""
        op = self.op("ghost_op")
        if op <= 0:
            return VMobject()
        x = self.xs()
        y = R0 * np.sin(theta_tau(self.taus(x)))
        return VMobject().set_points_smoothly(np.column_stack([x, y, 0 * x])).set_stroke(S.INK, 2.2, 0.28 * op)

    def _square(self):
        """S09: the ideal square wave (dashed ghost) plus flash highlights on tops/bottoms/walls."""
        op = self.op("sq_op")
        if op <= 0:
            return VMobject()
        x = self.xs(400)
        y = ideal_square(theta_tau(self.taus(x)))
        jump = np.nonzero(np.diff(y) != 0)[0]
        pts = [[x[0], y[0], 0]]
        for j in jump:
            xm = (x[j] + x[j + 1]) / 2
            pts += [[xm, y[j], 0], [xm, y[j + 1], 0]]
        pts.append([x[-1], y[-1], 0])
        pts = np.array(pts, float)
        # drawn over the gold trace: thin white dashes show the ideal shape it is hugging
        g = VGroup(DashedVMobject(VMobject().set_points_as_corners(pts), num_dashes=110)
                   .set_stroke(S.LABEL, 1.6, 0.6 * op))
        for key, test in (("tops", lambda a, b: a[1] > 0 and b[1] > 0),
                          ("bottoms", lambda a, b: a[1] < 0 and b[1] < 0),
                          ("walls", lambda a, b: a[0] == b[0])):
            f = self[key] * self["master"]
            if f > 0:
                for a, b in zip(pts[:-1], pts[1:]):
                    if test(a, b) and np.linalg.norm(b - a) > 1e-3:
                        g.add(Line(a, b, color=S.LABEL, stroke_width=14).set_stroke(opacity=0.18 * f),
                              Line(a, b, color=S.LABEL, stroke_width=5).set_stroke(opacity=0.95 * f))
        return g

    def _dash(self):
        """S07: dashed empty circle riding the tip, before the second circle exists."""
        op = self.op("dash_op")
        if op <= 0:
            return VMobject()
        J = joints(self.now)
        return DashedVMobject(Circle(radius=R0 / 3).move_to(p3(J[1])), num_dashes=18).set_stroke(
            S.ARM, 2, 0.8 * op)

    def _bars(self):
        """S07: the first height (silver) and the second stacked on it (blue), beside the track."""
        o1, o2 = self.op("bar1_op"), self.op("bar2_op")
        if o1 <= 0 and o2 <= 0:
            return VMobject()
        J = joints(self.now)
        h1, h2 = J[1].imag - J[0].imag, J[2].imag - J[1].imag
        x = X0 - 0.22
        g = VGroup()
        if o1 > 0:
            g.add(Line([x, 0, 0], [x, h1, 0], color=S.ARM, stroke_width=7).set_stroke(opacity=o1))
        if o2 > 0 and abs(h2) > 1e-3:
            g.add(Line([x, h1, 0], [x, h1 + h2, 0], color=S.FWD, stroke_width=7).set_stroke(opacity=o2))
        return g

    def _strip(self):
        """The list of circles: one blue bar per speed, height ∝ size (first appearance of the strip)."""
        op = self.op("strip_op")
        if op <= 0:
            return VMobject()
        a = amps(self.now)
        N = n_circles(self.now)
        w = SW / (max(7.0, 2 * N - 1) + 1)
        g = VGroup(Line([SX, SY, 0], [SX + SW, SY, 0], color=S.ARM, stroke_width=1).set_stroke(opacity=0.4 * op))
        bw = float(np.clip(0.55 * w * 70, 0.6, 9))
        for k in np.nonzero(a > 1e-4)[0]:
            x = SX + NS[k] * w
            hgt = SH * a[k] / A1
            g.add(Line([x, SY, 0], [x, SY + hgt, 0], color=S.FWD, stroke_width=bw).set_stroke(opacity=op))
        return g

    def bar_top(self, k: int) -> np.ndarray:
        """Where circle k's bar ends (for the ⅓, ⅕, 1/7 labels), using S08's spacing."""
        w = SW / 8
        return np.array([SX + NS[k] * w, SY + SH / NS[k], 0])


def theta_tau(taus):
    return C1.base_angle(taus)


def _tracker(v):
    from manim import ValueTracker
    return ValueTracker(float(v))


FRACS = (r"1", r"\tfrac{1}{3}", r"\tfrac{1}{5}", r"\tfrac{1}{7}")


def frac_labels(m: Stack) -> VGroup:
    """The 1, ⅓, ⅕, 1/7 labels over the first four bars (S08 spacing)."""
    from manim import UP, MathTex
    return VGroup(*[MathTex(f, font_size=32, color=S.FWD).next_to(m.bar_top(k), UP, buff=0.12)
                    for k, f in enumerate(FRACS)])


# ── S09/S10 pieces ─────────────────────────────────────────────────────────
def make_plate(scene, op):
    """The 10–200 circle chain on the GPU (rims + arms only; Manim keeps the pen and wave)."""
    def state():
        a = amps(scene.now)
        idx = np.nonzero(a > 1e-5)[0]
        o = op.get_value()
        return {"terms": [(int(NS[k]), complex(a[k])) for k in idx], "t": float(theta(scene.now) / (2 * np.pi)),
                "origin": complex(CX[0], CX[1]), "ink_from": None, "pen_alpha": 0.0, "sparks": 0.0,
                "rim_alpha": o, "arm_alpha": o, "opacity": 1.0 if o > 0 else 0.0, "vignette": 0.0, "grain": 0.0}
    p = V.EpicyclePlate(state)
    scene.add(p)
    return p


COUNTER_POS = np.array([6.35, 3.35, 0.0])


def counter(scene, op):
    """Live circle count, top-right: lands on 10, 50, 200 with the words."""
    from manim import RIGHT
    def build():
        o = op.get_value()
        if o <= 0:
            return VMobject()
        n = int(round(n_circles(scene.now)))
        num = V.label(f"{n}", 40, S.LABEL, weight="MEDIUM").set_opacity(o)
        word = V.label("circles", 22, S.LABEL_MUTED).set_opacity(o)
        from manim import DOWN
        g = VGroup(num, word).arrange(RIGHT, buff=0.15, aligned_edge=DOWN)
        return g.move_to(COUNTER_POS, aligned_edge=RIGHT)
    return V.redraw(build)


S09_END = {**S07_START, "rim_op": 0.0, "arm_op": 0.0, "hair_op": 1.0, "strip_op": 1.0, "sq_op": 1.0}


def corner_marker(pos=np.array([6.3, 3.35, 0.0]), size: float = 0.32):
    """Small red corner glyph (S10 → S26): 'sharp corners are expensive'."""
    pts = [pos + np.array([-size, 0, 0]), pos, pos + np.array([0, -size, 0])]
    return VGroup(VMobject().set_points_as_corners(pts).set_stroke(S.SPIKE, 3.5),
                  Dot(pos, radius=0.06, color=S.SPIKE))


def final_wave():
    """The 200-circle square wave exactly as S10 leaves it (clock stopped, no axis)."""
    c = float(clock(S10[1]))
    x = np.linspace(X0, X_END, 3000)
    y = square_sum(theta_tau(c - (x - X0) / V_SCROLL), A1 / NS)
    return VMobject().set_points_as_corners(np.column_stack([x, y, 0 * x])).set_stroke(S.INK, 3.5, 1.0)
