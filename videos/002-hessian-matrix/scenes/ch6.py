"""Chapter 6 builders (scenes 21–24): why it matters.

Every scene rebuilds the previous scene's last frame from these builders. All numbers on
screen are computed and asserted here.
"""

from __future__ import annotations

import math

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Circle, DecimalNumber, Dot, Ellipse, ImageMobject,
                   Integer, Line, MathTex, RoundedRectangle, ValueTracker, VGroup, VMobject, always_redraw,
                   config, smooth)
from scipy.optimize import minimize

from aion import style as S
from aion.components.bend_gauge import BendGauge
from aion.components.matrix_grid import HessianGrid
from aion.components.surface_gl import height as surf_height
import shared as V
import ch2 as L2
import ch3 as L3

# ══ scene 21: a landscape of error ═══════════════════════════════════════════
_rng = np.random.default_rng(7)
LAND_G = [(1.1, -0.9, -2.6, 0.55)]                 # the deepest pit, then 15 seeded hills and pits
for _ in range(15):
    _r, _a = _rng.uniform(0.6, 4.0), _rng.uniform(0, 2 * math.pi)
    LAND_G.append((float(_r * math.cos(_a)), float(_r * math.sin(_a)),
                   float(_rng.choice([-1, 1]) * _rng.uniform(0.6, 1.6)), float(_rng.uniform(0.45, 0.95))))
LAND_SHAPE = dict(H=(1.0, 0.0, 1.0), w=(0.12, 1.0, 0.0, 0.0), gauss=LAND_G, zs=0.6, zclip=0.0)
LAND_R = 4.2


def land_z(x, y):
    return surf_height(LAND_SHAPE, x, y)


_g = np.linspace(-LAND_R, LAND_R, 421)
_X, _Y = np.meshgrid(_g, _g)
_Z = np.where(_X ** 2 + _Y ** 2 < LAND_R ** 2, land_z(_X, _Y), np.inf)
_k = np.unravel_index(np.argmin(_Z), _Z.shape)
_m = minimize(lambda p: float(land_z(p[0], p[1])), [_X[_k], _Y[_k]], method="Nelder-Mead",
              options=dict(xatol=1e-7, fatol=1e-10))
PIT = (float(_m.x[0]), float(_m.x[1]))
PIT_Z = float(land_z(*PIT))
assert PIT_Z <= _Z.min() + 1e-9                    # the glowing pit really is the lowest point
assert math.hypot(PIT[0] - 1.02, PIT[1] + 0.80) < 0.05

LAND_SPIN, LAND_DOLLY = 1.1, 0.07                  # deg/s orbit, units/s dolly: the slow fly-over


def land_rig(clk: ValueTracker, **kw) -> V.Rig:
    st = dict(**LAND_SHAPE, R=LAND_R, edge=0.78, yaw=145.0, pitch=32.0, dist=8.4, fov=38.0,
              target=(0.6, -0.5, -0.35), fog=0.03, grid=(0.2, 0.2), grid_step=0.35, contour=0.7,
              contour_step=0.16, zlo=-1.2, zhi=1.2, tint=0.0, opacity=0.0, slices=[], disc=None, **L2.LUMINOUS)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["yaw"] = lambda: r.val("yaw") + LAND_SPIN * clk.get_value()
    r.dyn["dist"] = lambda: r.val("dist") - LAND_DOLLY * clk.get_value()
    return r


def ring_at(plate, x: float, y: float, r: float = 0.2, color=S.TERRAIN_LINE):
    c = V.lit(Circle(radius=r), color, width=3, halo=12, opacity=0.2)
    return V.pin(c, plate, lambda: (x, y, float(plate.height(x, y)) + 0.01))


SETTLE_FROM = np.array([2.0, 0.1])


def settle_xy(k: float):
    """The ball's spiral into the pit, k ∈ [0, 1]."""
    ang = 3.0 * math.pi * k
    rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    off = (1 - k) * rot @ (SETTLE_FROM - np.array(PIT))
    return PIT[0] + off[0], PIT[1] + off[1]


def eyebrow() -> VGroup:
    a = V.hush(V.label("TRAINING A NEURAL NETWORK", 18, S.MUTED, weight="BOLD"))
    a.to_corner(UP + LEFT, buff=0.6)
    return a


def height_caption(eb) -> VGroup:
    return V.label("height = error", 30, S.TEXT).next_to(eb, DOWN, buff=0.22, aligned_edge=LEFT)


AXIS_HALF = 1.6


def floor_axes(plate) -> VGroup:
    """The two input axes through the pit (x red, y green), redrawn as the camera moves."""
    def axis(u, col):
        ln = V.lit(Line(LEFT, RIGHT), col, width=3, halo=10, opacity=0.18)

        def upd(m):
            p0 = plate.project(PIT[0] - AXIS_HALF * u[0], PIT[1] - AXIS_HALF * u[1], PIT_Z)
            p1 = plate.project(PIT[0] + AXIS_HALF * u[0], PIT[1] + AXIS_HALF * u[1], PIT_Z)
            m.put_start_and_end_on(p0, p1)
        ln.add_updater(upd)
        upd(ln)
        return ln
    return VGroup(axis((1, 0), S.HX), axis((0, 1), S.HY))


_frng = np.random.default_rng(11)
FAN_N = 200
FAN = [(float(a), float(l), c, float(o)) for a, l, c, o in zip(
    _frng.uniform(0, 2 * math.pi, FAN_N), _frng.uniform(0.5, 3.4, FAN_N),
    _frng.choice([S.HX, S.HY, S.TWIST, S.TERRAIN_LINE, S.TERRAIN_LINE], FAN_N), _frng.uniform(0.18, 0.5, FAN_N))]


def fan(plate, g: ValueTracker):
    """'Not two dimensions but millions': a burst of faint axis lines from the pit."""
    def make():
        k = g.get_value()
        if k < 0.01:
            return VGroup()
        c = plate.project(*PIT, PIT_Z)
        out = VGroup()
        for a, l, col, o in FAN:
            d = np.array([math.cos(a), math.sin(a), 0.0])
            out.add(Line(c, c + d * l * k).set_stroke(col, 1.3, opacity=o))
        return out
    return always_redraw(make)


def s21_end(clk: ValueTracker) -> dict:
    rig = land_rig(clk, opacity=1.0)
    plate = rig.plate()
    ring = ring_at(plate, *PIT)
    ball = V.walker()
    V.pin(ball, plate, lambda: (*PIT, PIT_Z + 0.03))
    eb = eyebrow()
    cap = height_caption(eb)
    axes = floor_axes(plate)
    g = ValueTracker(1.0)
    for m in (ring, ball):                       # placed now, so the first frame matches scene 21
        m.update()
    return dict(rig=rig, plate=plate, ring=ring, ball=ball, eb=eb, cap=cap, axes=axes, g=g, fan=fan(plate, g))


# ══ scene 22: gradient descent zigzags ═════════════════════════════════════════
MAP_U = 1.05
MAP_C = np.array([0.0, -0.55, 0.0])
LEVELS = (0.4, 1.2, 2.5, 4.2, 6.4, 9.0, 12.5, 17.0, 22.5)
START = (3.0, 1.0)
NARROW = (2.0, 20.0)                               # f = x² + 10y²: H = diag(2, 20)
ROUND = (2.0, 2.0)                                 # f = x² + y²:   H = diag(2, 2)


def m2p(x, y) -> np.ndarray:
    return MAP_C + MAP_U * np.array([x, y, 0.0])


def contours(lams) -> VGroup:
    """Exact level sets ½(λ₁x² + λ₂y²) = c, i.e. ellipses with half-axes √(2c/λ)."""
    g = VGroup()
    for i, c in enumerate(LEVELS):
        a, b = math.sqrt(2 * c / lams[0]), math.sqrt(2 * c / lams[1])
        e = Ellipse(width=2 * a * MAP_U, height=2 * b * MAP_U).move_to(MAP_C)
        V.lit(e, S.TERRAIN_LINE, width=1.6, halo=8, opacity=0.06)
        e.set_stroke(opacity=0.62 - 0.035 * i)
        g.add(e)
    return g


def gd(lams, step: float, p0=START, eps: float = 0.05):
    pts = [np.array(p0, float)]
    while np.hypot(*pts[-1]) > eps:
        p = pts[-1]
        pts.append(p - step * np.array([lams[0] * p[0], lams[1] * p[1]]))
        assert len(pts) < 200
    return pts


ROUND_STEP, NARROW_STEP = 0.15, 0.09
ROUND_PTS = gd(ROUND, ROUND_STEP)
NARROW_PTS = gd(NARROW, NARROW_STEP)
assert len(ROUND_PTS) - 1 == 12
assert len(NARROW_PTS) - 1 == 21                   # "21 steps"
assert np.allclose([p[0] for p in V.gd_path()], [p[0] for p in NARROW_PTS])   # same path as the plan
assert all(NARROW_PTS[i][1] * NARROW_PTS[i + 1][1] < 0 for i in range(20))    # every step overshoots
KAPPA = NARROW[1] / NARROW[0]
assert KAPPA == 10

# Newton: p − H⁻¹∇f lands exactly on the minimum of a quadratic
_p = np.array(START)
_newton = _p - np.linalg.solve(np.diag(NARROW), np.diag(NARROW) @ _p)
assert np.allclose(_newton, 0)


def path_pos(pts, s: float) -> np.ndarray:
    k = int(min(max(math.floor(s), 0), len(pts) - 2))
    f = smooth(min(max(s - k, 0.0), 1.0))
    p = pts[k] + (pts[k + 1] - pts[k]) * f
    return m2p(*p)


def path_mob(pts, s: ValueTracker, op: ValueTracker | None = None):
    """The path walked so far: gold polyline with a dot at each step."""
    def make():
        v = s.get_value()
        if v <= 0.01:
            return VGroup()
        o = 1.0 if op is None else op.get_value()
        k = int(min(math.floor(v), len(pts) - 1))
        corners = [m2p(*p) for p in pts[:k + 1]]
        if v < len(pts) - 1:
            corners.append(path_pos(pts, v))
        ln = VMobject().set_points_as_corners(corners).set_stroke(S.GRAD, 2.2, opacity=0.85 * o)
        dots = VGroup(*[Dot(m2p(*p), radius=0.035, color=S.GRAD).set_opacity(0.9 * o) for p in pts[1:k + 1]])
        return VGroup(ln, dots)
    return always_redraw(make)


def grad_arrow() -> Arrow:
    g = np.array([ROUND[0] * START[0], ROUND[1] * START[1]])
    tip = np.array(START) - ROUND_STEP * g          # the first step lands on the arrow's tip
    assert np.allclose(tip, ROUND_PTS[1])
    a = Arrow(m2p(*START), m2p(*tip), buff=0.0, stroke_width=5, max_tip_length_to_length_ratio=0.25,
              color=S.GRAD)
    return a


ROW1_Y, ROW2_Y, ROW_X, COUNT_X = -2.9, -3.42, -6.35, -2.75


def gd_label():
    return V.label("gradient descent", 26, S.TEXT).move_to([ROW_X, ROW1_Y, 0], aligned_edge=LEFT)


def count_label(n: int, y: float, color) -> VGroup:
    """'21 steps' in Inter: the number in colour, the word muted, left-aligned at COUNT_X."""
    num = V.label(str(n), 26, color, weight="MEDIUM")
    word = V.label("step" if n == 1 else "steps", 26, S.MUTED)
    g = VGroup(num, word).arrange(RIGHT, buff=0.14, aligned_edge=DOWN)
    return g.move_to([COUNT_X, y, 0], aligned_edge=LEFT)


def gd_counter(s: ValueTracker, o: ValueTracker):
    """Redrawn every frame, so it fades through `o`, never FadeIn/FadeOut."""
    return always_redraw(lambda: count_label(int(min(math.floor(s.get_value() + 1e-6), 21)), ROW1_Y, S.GRAD)
                         .set_opacity(o.get_value()))


H_C = np.array([-4.55, 2.6, 0.0])


def h_matrix() -> VGroup:
    """H = [[2, 0], [0, 20]] as a small glass grid (entries placed, not animated)."""
    g = L3.glass(HessianGrid(cell=0.5, gap=0.06, center=H_C, tint_scale=L3.TINT))
    g.show_brackets()
    g.brackets.set_stroke(width=2.5)
    for (i, j), (t, c) in zip(((0, 0), (0, 1), (1, 0), (1, 1)),
                              (("2", S.HX), ("0", S.TWIST), ("0", S.TWIST), ("20", S.HY))):
        g.fill(i, j, MathTex(t, font_size=30, color=c))
    lab = MathTex("H", "=", font_size=40, color=S.TEXT).next_to(g.brackets, LEFT, buff=0.18)
    return VGroup(lab, g)


GAUGE_X = (-1.55, 1.05)
GAUGE_Y = 2.95


def gauges() -> VGroup:
    """Bend gauges for λ = 2 and λ = 20 (curvature ∝ λ: the gain keeps the ratio honest)."""
    out = VGroup()
    for x, lam, col, sub in zip(GAUGE_X, NARROW, (S.HX, S.HY), ("1", "2")):
        gg = BendGauge(lam, width=1.3, gain=0.035, max_c=0.8, stroke=6).place([x, GAUGE_Y, 0])
        t = MathTex(r"\lambda_" + sub, "=", f"{int(lam)}", font_size=34, color=S.TEXT)
        t[2].set_color(S.SMILE)
        t.move_to([x, GAUGE_Y - 0.72, 0])
        out.add(VGroup(gg, t))
    return out


def map_axes() -> VGroup:
    """The floor of the trough (x, red) and the steep direction across it (y, green)."""
    x = V.lit(Line(m2p(-4.85, 0), m2p(4.85, 0)), S.HX, width=2.5, halo=10, opacity=0.14).set_stroke(opacity=0.7)
    y = V.lit(Line(m2p(0, -1.62), m2p(0, 1.62)), S.HY, width=2.5, halo=10, opacity=0.14).set_stroke(opacity=0.7)
    return VGroup(x, y)


RATIO_C = np.array([4.55, 2.85, 0.0])


def ratio() -> tuple[MathTex, VGroup]:
    m = MathTex(r"{\lambda_2 \over \lambda_1}", "=", r"{20 \over 2}", "=", "10", font_size=40, color=S.TEXT)
    m[4].set_color(S.GRAD)
    m.move_to(RATIO_C)
    lab = V.label("condition number", 22, S.MUTED).next_to(m, DOWN, buff=0.28)
    return m, lab


def s22_end() -> dict:
    cont = contours(NARROW)
    s = ValueTracker(21.0)
    path = path_mob(NARROW_PTS, s)
    ball = V.walker().move_to(path_pos(NARROW_PTS, 21.0))
    hm = h_matrix()
    gs = gauges()
    ax = map_axes()
    rt, rl = ratio()
    gl = gd_label()
    co = ValueTracker(1.0)
    cnt = gd_counter(s, co)
    return dict(co=co, cont=cont, s=s, path=path, ball=ball, hm=hm, gs=gs, ax=ax, ratio=rt, rlab=rl, gl=gl, cnt=cnt)


# ══ scene 23: one Newton jump, and a trillion numbers ═════════════════════════
INSET = dict(width=8.6, height=2.6, center=np.array([1.95, 2.45, 0.0]))
BOWL_ZS = 0.05


def bowl_rig(**kw) -> V.Rig:
    st = dict(H=(2.0, 0.0, 20.0), w=(1.0, 0.0, 0.0, 0.0), zs=BOWL_ZS, zclip=1.0, R=3.5, edge=0.8,
              yaw=-90.0, pitch=24.0, dist=7.2, fov=30.0, target=(0.0, 0.0, 0.4), fog=0.02,
              grid=(0.25, 0.25), grid_step=0.35, contour=0.6, contour_step=0.12, zlo=-1.0, zhi=1.0,
              tint=0.0, opacity=0.0, slices=[], disc=None, **L2.LUMINOUS_PANEL)
    st.update(kw)
    return V.Rig(**st)


def newton_arc():
    from manim import ArcBetweenPoints
    a = ArcBetweenPoints(m2p(*START), m2p(0, 0), angle=-1.1)
    return V.lit(a, S.LIGHT, width=3.5, halo=14, opacity=0.18)


def newton_label():
    return V.label("Newton's method", 26, S.TEXT).move_to([ROW_X, ROW2_Y, 0], aligned_edge=LEFT)


def newton_count() -> VGroup:
    return count_label(1, ROW2_Y, S.LIGHT)


# The mosaic: the 2×2 grid is the centre of a million-by-million grid of the same cells.
MOS_C = np.array([-2.2, 0.0, 0.0])
MOS_PITCH0 = 1.38                                   # screen units per cell when it matches the 2×2 grid
MOS_PITCH1 = 0.085
CELL_FRAC = 0.5 / 0.56                              # HessianGrid(cell=0.5, gap=0.06)
MOS_R = 4.0


def grid_at_mosaic(hm: VGroup) -> VGroup:
    """Where scene 23 parks the 2×2 grid: centred on MOS_C with pitch MOS_PITCH0."""
    g = hm[1]
    k = MOS_PITCH0 / (0.5 + 0.06)
    return g.copy().scale(k).move_to(MOS_C)


def _rgb(hexs):
    h = hexs.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


class Mosaic(ImageMobject):
    """A full-frame procedural grid of glass cells, rendered with numpy each frame.

    pitch: screen units per cell; alpha: overall; band: 0 → all cells, 1 → only the
    diagonal band |i − j| ≤ 2 stays lit (the pieces real methods estimate)."""

    def __init__(self, pitch: ValueTracker, alpha: ValueTracker, band: ValueTracker):
        W, H = config.pixel_width, config.pixel_height
        super().__init__(np.zeros((H, W, 4), np.uint8))
        self.stretch_to_fit_width(config.frame_width).stretch_to_fit_height(config.frame_height).move_to(ORIGIN)
        fw, fh = config.frame_width, config.frame_height
        xs = (np.arange(W) + 0.5) / W * fw - fw / 2
        ys = fh / 2 - (np.arange(H) + 0.5) / H * fh
        self._X, self._Y = np.meshgrid(xs, ys)
        self._ppu = W / fw
        d = np.hypot(self._X - MOS_C[0], self._Y - MOS_C[1])
        t = np.clip((MOS_R - d) / (MOS_R * 0.55), 0, 1)
        self._fall = t * t * (3 - 2 * t)
        self.pitch, self.alpha, self.band = pitch, alpha, band
        self._shape = (H, W)
        self._draw()
        self.add_updater(lambda m: m._draw())

    def _draw(self):
        a_all = self.alpha.get_value()
        H, W = self._shape
        if a_all <= 0.002:
            self.pixel_array = np.zeros((H, W, 4), np.uint8)
            return self
        s = self.pitch() if callable(self.pitch) else self.pitch.get_value()
        u = (self._X - MOS_C[0]) / s
        v = (MOS_C[1] - self._Y) / s
        j, i = np.floor(u), np.floor(v)
        fu, fv = u - j - 0.5, v - i - 0.5
        h, r = 0.5 * CELL_FRAC, 0.16 * CELL_FRAC
        qx, qy = np.abs(fu) - (h - r), np.abs(fv) - (h - r)
        d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
        dpx = d * s * self._ppu
        inside = np.clip(0.5 - dpx, 0, 1)
        rim = np.clip(1.0 - np.abs(dpx + 0.6) / 0.9, 0, 1)
        hsh = np.modf(np.abs(np.sin(i * 12.9898 + j * 78.233) * 43758.5453))[0]
        val = 0.15 + 0.85 * hsh ** 3
        bnd = self.band.get_value()
        on = (np.abs(i - j) <= 2).astype(float)
        lit = 1.0 - 0.85 * bnd * (1 - on)
        boost = 1.0 + 0.9 * bnd * on
        tl, body = _rgb(S.TERRAIN_LINE), _rgb(S.STAGE_RAISED)
        col = (inside[..., None] * (body + 0.07 * val[..., None] * tl)
               + (0.55 * rim * boost)[..., None] * tl) * lit[..., None]
        cellpx = s * self._ppu
        if cellpx < 5.0:                              # tiny cells: blend toward the cell average
            t = min((5.0 - cellpx) / 3.5, 1.0)
            avg = (CELL_FRAC ** 2 * (body + 0.07 * val[..., None] * tl)
                   + (min(1.0, 4 * CELL_FRAC / max(cellpx, 0.5)) * 0.55 * boost * 0.35)[..., None] * tl) \
                * lit[..., None]
            col = col * (1 - t) + avg * t
        a = self._fall * a_all
        rgba = np.empty((H, W, 4), np.uint8)
        rgba[..., :3] = np.clip(col * 255, 0, 255).astype(np.uint8)
        rgba[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
        self.pixel_array = rgba
        return self


def mosaic_pitch(e: float) -> float:
    """e ∈ [0, 1] → pitch, exponential between the 2×2 grid and the far mosaic."""
    return MOS_PITCH0 * (MOS_PITCH1 / MOS_PITCH0) ** e


SIDE_X = 4.25


def million() -> MathTex:
    return MathTex(r"10^6", r"\times", r"10^6", font_size=44, color=S.TEXT).move_to([SIDE_X, 1.05, 0])


TRILLION = 10 ** 12
assert (10 ** 6) ** 2 == TRILLION


def trillion(e: ValueTracker, o: ValueTracker | None = None) -> VGroup:
    """Counter that rolls from 4 (the 2×2 grid) up to 10¹², log-uniformly with e ∈ [0, 1].
    Its digit count changes as it rolls, so it fades through `o` (an updater), never FadeIn."""
    n = DecimalNumber(4, num_decimal_places=0, group_with_commas=True, font_size=40, color=S.GRAD)
    lab = V.label("numbers", 24, S.MUTED).move_to([SIDE_X, -0.68, 0])

    def upd(m):
        m.set_value(round(4 * (TRILLION / 4) ** e.get_value()))
        m.move_to([SIDE_X, 0.0, 0])
        if o is not None:
            m.set_opacity(o.get_value())
            lab.set_opacity(o.get_value())
    n.add_updater(upd)
    upd(n)
    return VGroup(n, lab)


def s23_end() -> dict:
    p, a, b, e = ValueTracker(1.0), ValueTracker(1.0), ValueTracker(1.0), ValueTracker(1.0)
    mos = Mosaic(lambda: mosaic_pitch(p.get_value()), a, b)
    return dict(mos=mos, pitch=p, alpha=a, band=b, e=e, mil=million(), tri=trillion(e))


# ══ scene 24: most flat points are saddles ═════════════════════════════════════
N_ROWS, K_MAX = 12, 100
_srng = np.random.default_rng(0)
SIGNS = _srng.choice([1, -1], size=(N_ROWS, K_MAX))        # each eigenvalue's sign: a coin flip (intuition)
VALLEY = lambda k: [bool(np.all(SIGNS[r, :k] > 0)) for r in range(N_ROWS)]     # noqa: E731
PEAK = lambda k: [bool(np.all(SIGNS[r, :k] < 0)) for r in range(N_ROWS)]       # noqa: E731
assert sum(VALLEY(2)) == 3                                  # small landscapes: valleys are common
assert sum(VALLEY(10)) == 0 and sum(PEAK(10)) == 0          # ten dimensions: every row is a saddle
assert sum(VALLEY(100)) == 0
HI_ROW = 5                                                  # the row the narration singles out
ROW_Y0, ROW_DY, ROW_X0 = 2.6, 0.47, -0.55
TAG_X = 3.0


def spacing(k: int) -> float:
    return 0.34 if k <= 10 else 0.058


def dot_r(k: int) -> float:
    return 0.075 if k <= 10 else 0.024


def dot_pos(r: int, j: int, k: int) -> np.ndarray:
    return np.array([ROW_X0 + (j - (k - 1) / 2) * spacing(k), ROW_Y0 - r * ROW_DY, 0.0])


def row_dots(r: int, k: int, j0: int = 0) -> VGroup:
    return VGroup(*[Dot(dot_pos(r, j, k), radius=dot_r(k), color=S.SMILE if SIGNS[r, j] > 0 else S.FROWN)
                    for j in range(j0, k)])


def valley_ring(r: int, k: int) -> RoundedRectangle:
    w = (k - 1) * spacing(k) + 0.42
    box = RoundedRectangle(width=w, height=0.34, corner_radius=0.17).move_to([ROW_X0, ROW_Y0 - r * ROW_DY, 0])
    return V.lit(box, S.SMILE, width=2, halo=10, opacity=0.12)


def saddle_tags() -> VGroup:
    return VGroup(*[V.label("saddle", 20, S.MUTED).move_to([TAG_X, ROW_Y0 - r * ROW_DY, 0], aligned_edge=LEFT)
                    for r in range(N_ROWS)])


def requirement() -> MathTex:
    m = MathTex(r"\text{valley:}\quad", r"\lambda_1,\ \lambda_2,\ \dots,\ \lambda_n", "> 0",
                font_size=36, color=S.TEXT)
    m[1].set_color(S.SMILE)
    return m.move_to([ROW_X0, -3.4, 0])


def caveat():
    return V.label("intuition, not a proof", 20, S.MUTED).to_corner(DOWN + RIGHT, buff=0.55)


SADDLE_VIEW = dict(yaw=-62.0, pitch=30.0, dist=8.4, target=(0.0, 0.0, 0.0))


def saddle_rig(**kw) -> V.Rig:
    st = dict(SADDLE_VIEW, opacity=0.0, contour=0.6, contour_step=0.2, tint=1.0)
    st.update(kw)
    return V.puzzle_rig(H=V.H_SADDLE, **st)


ROLL_TO = 1.9                                      # the ball rolls off along +y (the frown direction)


def roll_xyz(plate, s: float):
    y = ROLL_TO * s * s
    return 0.0, y, float(plate.height(0.0, y)) + 0.03


def s24_end() -> dict:
    rig = saddle_rig(opacity=1.0)
    plate = rig.plate()
    ball = V.walker()
    V.pin(ball, plate, lambda: roll_xyz(plate, 1.0))
    return dict(rig=rig, plate=plate, ball=ball)
