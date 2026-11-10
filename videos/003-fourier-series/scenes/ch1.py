"""Ch1 shared machine: one circle, its arm, the height track and the scrolling wave.

S04, S05, S06 (end) and S07 (start) all draw the same circle from the same clock, so
every cut between them matches by construction. Everything is a pure function of the
absolute audio time `now` plus a few animated settings (size r, speed n, start φ).

Clock: the arm rests pointing right, eases up to one turn per 4 s on "turning steadily",
and is phased so the tip is at the top exactly on the first "up".
"""

from __future__ import annotations

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arc, Arrow, DashedLine, Dot, Ellipse, Line, ValueTracker,
                   VGroup, VMobject)

from aion import style as S
from aion.sync import Cue
import shared as V

CUE = Cue.load(V.SRT)
S04_START = V.scene_range(4)[0]

CX = np.array([-4.0, 0.0, 0.0])        # circle center (S03 leaves the circle here)
R0 = V.ONE_R                           # 1.2: the unit circle of Ch1
X0, X_END = -1.8, 6.4                  # height track x, right end of the time axis
V_SCROLL = 1.0                         # wave scroll speed (units per second): 4 units per turn
OMEGA = 2 * np.pi / 4.0                # one turn per 4 s

T_SPIN = CUE.at("turning steadily", after=S04_START) - S.LEAD
T_UP = CUE.at("up", after=CUE.at("how high its tip is", after=S04_START))
# ease-in length chosen so the resting arm points exactly right (angle 0)
RAMP = 2 * (T_UP - T_SPIN - 5.0)
assert 0.2 < RAMP < 1.6, RAMP
T_TRAIL = CUE.at("trail", after=T_UP) - S.LEAD


def g(t: float | np.ndarray):
    """Turned time: 0 before T_SPIN, a quadratic ease of length RAMP, then linear."""
    t = np.asarray(t, float)
    x = t - T_SPIN
    return np.where(x <= 0, 0.0, np.where(x < RAMP, x * x / (2 * RAMP), x - RAMP / 2))


def base_angle(t):
    return np.pi / 2 + OMEGA * (g(t) - g(T_UP))


def angle(t, n: float = 1.0, phi: float = 0.0, Tn: float = 0.0):
    """Arm angle for speed n (anchored at Tn so changing n never makes the arm jump)."""
    a = base_angle(Tn)
    return n * (base_angle(t) - a) + a + phi


# ── states: what each scene starts from / ends on ─────────────────────────
SETTINGS = ("master", "r", "n", "phi", "tilt", "grow",
            "circle_op", "arm_op", "conn_op", "track_op", "axis_op", "trail_op", "ghost_op",
            "gr", "gn", "gphi")
S04_START_STATE = dict(master=1.0, r=R0, n=1.0, phi=0.0, tilt=1.0, grow=0.0,
                       circle_op=1.0, arm_op=0.0, conn_op=0.0, track_op=0.0, axis_op=0.0, trail_op=1.0,
                       ghost_op=0.0, gr=R0, gn=1.0, gphi=0.0, Tn=None)
S04_END = {**S04_START_STATE, "grow": 1.0, "arm_op": 1.0, "circle_op": 0.4, "conn_op": 1.0,
           "track_op": 1.0, "axis_op": 1.0, "trail_op": 1.0}
SPEED_KEY = "its speed"                # S05: the speed change is anchored on this word


def t_speed() -> float:
    return CUE.at(SPEED_KEY, after=V.scene_range(5)[0]) - S.LEAD


S05_END = {**S04_END, "r": 1.5 * R0, "n": 2.0, "phi": np.pi / 2, "Tn": None}   # Tn filled by t_speed()
FLAT = {**S04_END}                     # the plain sine picture S06 ends on and S07 starts from


class OneCircle:
    """The Ch1 picture. `now` is a callable returning absolute audio time."""

    def __init__(self, scene, state: dict):
        self.scene = scene
        self.v = {k: ValueTracker(float(state[k])) for k in SETTINGS}
        self.Tn = state["Tn"] if state.get("Tn") is not None else t_speed()
        self.trail_from = state.get("trail_from", T_TRAIL)
        self.arc_op = ValueTracker(0.0)
        scene.add(*self.v.values(), self.arc_op)
        R = V.redraw
        self.circle = R(self._circle)
        self.ghost = R(lambda: self._wave(ghost=True))
        self.trail = R(self._wave)
        self.axis = R(self._axis)
        self.track = R(self._track)
        self.conn = R(self._conn)
        self.arc = R(self._arc)
        self.arm = R(self._arm)
        self.marker = R(self._marker)
        self.pen = R(self._pen)
        self.group = VGroup(self.circle, self.axis, self.track, self.ghost, self.trail, self.conn,
                            self.arc, self.arm, self.marker, self.pen)
        scene.add(self.group)

    # values
    def __getitem__(self, k):
        return self.v[k].get_value()

    def op(self, k: str) -> float:
        return self[k] * self["master"]

    def a(self, t=None):
        t = self.scene.now if t is None else t
        return angle(t, self["n"], self["phi"], self.Tn)

    def tip(self) -> np.ndarray:
        r, a = self["r"], self.a()
        return CX + r * np.array([self["tilt"] * np.cos(a), np.sin(a), 0.0])

    def height(self) -> float:
        return self["r"] * np.sin(self.a())

    # pieces
    def _circle(self):
        r, k = self["r"], max(self["tilt"], 1e-3)
        e = Ellipse(width=2 * r * k, height=2 * r, color=S.FWD, stroke_width=3).move_to(CX)
        e.set_stroke(opacity=min(1.0, S.RIM_BOOST * self.op("circle_op")))
        hub = Dot(CX, radius=0.045, color=S.ARM).set_opacity(self.op("arm_op"))
        return VGroup(e, hub, self._term(r))

    def _term(self, r):
        """The circle's equation beside it: sin t for the plain circle, r sin(nt + φ) once it is tuned."""
        from aion.components.term_label import labels
        op = self["master"] * min(1.0, 3 * self["circle_op"]) * min(1.0, self["tilt"] * 2)
        if not V.TERM_LABELS or op <= 0 or r < 0.2:
            return VGroup()
        plain = abs(self["n"] - 1) < 1e-3 and abs(self["phi"]) < 1e-3 and abs(r - R0) < 1e-3
        tex = r"\sin t" if plain else r"r\,\sin(n t+\varphi)"
        return labels([(complex(CX[0], CX[1]), r, tex, S.FWD, 128.0)], op=op, size=30)

    def _arm(self):
        g_ = self["grow"]
        if g_ <= 0.01 or self.op("arm_op") <= 0:
            return VMobject()
        end = CX + g_ * (self.tip() - CX)
        if np.linalg.norm(end - CX) < 0.05:
            return VMobject()
        ar = Arrow(CX, end, buff=0, color=S.ARM, stroke_width=3, tip_length=0.16,
                   max_tip_length_to_length_ratio=0.25, max_stroke_width_to_length_ratio=20)
        return ar.set_opacity(self.op("arm_op"))

    def _pen(self):
        op = self.op("arm_op") * min(1.0, self["grow"] ** 4)
        p = self.tip()
        return VGroup(Dot(p, radius=0.17, color=S.INK).set_opacity(0.22 * op),
                      Dot(p, radius=0.07, color=S.INK).set_opacity(op))

    def _track(self):
        r = self["r"]
        return Line([X0, -r, 0], [X0, r, 0], color=S.ARM, stroke_width=1.5).set_stroke(
            opacity=0.45 * self.op("track_op"))

    def _marker(self):
        op = self.op("track_op")
        p = np.array([X0, self.height(), 0])
        return VGroup(Dot(p, radius=0.17, color=S.INK).set_opacity(0.22 * op),
                      Dot(p, radius=0.07, color=S.INK).set_opacity(op))

    def _conn(self):
        p, q = self.tip(), np.array([X0, self.height(), 0])
        if self.op("conn_op") <= 0 or abs(q[0] - p[0]) < 0.1:
            return VMobject()
        return DashedLine(p, q, dash_length=0.08, color=S.ARM, stroke_width=1.5).set_stroke(
            opacity=0.55 * self.op("conn_op"))

    def _axis(self):
        """axis_op is how much of the axis has drawn (left to right)."""
        f = self["axis_op"]
        if f <= 0.002:
            return VMobject()
        return Line([X0, 0, 0], [X0 + f * (X_END - X0), 0, 0], color=S.ARM, stroke_width=1.2).set_stroke(
            opacity=0.4 * self["master"])

    def _arc(self):
        """Violet head-start arc (S05): from where the arm would be without φ to where it is."""
        phi, op = self["phi"], self.arc_op.get_value() * self["master"]
        if op <= 0 or phi < 0.02:
            return VMobject()
        a1 = self.a()
        return Arc(radius=0.45 * self["r"], start_angle=a1 - phi, angle=phi, arc_center=CX,
                   color=S.PHASE, stroke_width=4).set_stroke(opacity=op)

    def _wave(self, ghost: bool = False):
        op = self.op("ghost_op") if ghost else self.op("trail_op")
        now = self.scene.now
        head = min(X_END, X0 + V_SCROLL * (now - self.trail_from))
        if op <= 0 or head <= X0 + 0.01:
            return VMobject()
        x = np.linspace(X0, head, max(2, int(90 * (head - X0))))
        tau = now - (x - X0) / V_SCROLL
        if ghost:
            y = self["gr"] * np.sin(angle(tau, self["gn"], self["gphi"], self.Tn))
        else:
            y = self["r"] * np.sin(angle(tau, self["n"], self["phi"], self.Tn))
        m = VMobject().set_points_smoothly(np.column_stack([x, y, np.zeros_like(x)]))
        if ghost:
            return m.set_stroke(S.INK, 2.2, 0.28 * op)
        return m.set_stroke(S.INK, 3.5, op)

    # helpers
    def to(self, **kw):
        """Animations that move settings to new values."""
        return [self.v[k].animate.set_value(v) for k, v in kw.items()]

    def set(self, **kw):
        for k, v in kw.items():
            self.v[k].set_value(v)

    def track_ends(self):
        r = self["r"]
        return np.array([X0, r, 0]), np.array([X0, -r, 0])


LABEL_POS = np.array([2.3, 2.75, 0.0])


def formula(pos=LABEL_POS):
    """r sin(n t + φ): r silver, n blue, φ violet, the rest gold (S05 end, S06 start)."""
    from manim import MathTex
    f = MathTex("r", r"\sin(", "n", "t", "+", r"\varphi", ")", font_size=52, color=S.INK).move_to(pos)
    for i, c in ((0, S.ARM), (2, S.FWD), (5, S.PHASE)):
        f[i].set_color(c)
    return f
