"""Shared paths, scene ranges, rigs and motifs for video 002 (the Hessian matrix).

Every scene builds its own first frame from the builders here, so the last frame
of scene N and the first frame of scene N+1 come from the same code with the same
parameters: cuts are invisible without replaying earlier scenes.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Axes, Circle, Dot, Line, ManimColor, MathTex, VMobject,
                   Text, ValueTracker, VGroup, interpolate_color, smooth,
                   there_and_back, UpdateFromAlphaFunc)

from aion import style as S
from aion.components.surface_gl import SurfacePlate, slice_line, tangent_disc
from aion.narration import NarratedScene

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from beats import CUT_FRAMES, FPS  # noqa: E402  (single source of the scene cuts)

AUDIO = ROOT / "assets" / "audio.mp3"
SRT = ROOT / "assets" / "cue-per-word.srt"
BG = "#000000"                       # pure black for this video (user decision)


def scene_range(n: int) -> tuple[float, float]:
    """(start, end) in absolute seconds of scene number n (1-based), frame-exact."""
    return CUT_FRAMES[n - 1] / FPS, CUT_FRAMES[n] / FPS


class VideoScene(NarratedScene):
    AUDIO, SRT, BACKGROUND = AUDIO, SRT, BG

    def beat(self, key: str, *anims, rt: float = 0.8, after: float | None = None,
             lead: float = S.LEAD, rate=smooth, **kw):
        """Play `anims` so they start `lead` before the cue word `key`."""
        self.play_at(self.t(key, after), *anims, lead=lead, run_time=rt, rate_func=rate, **kw)

    def run_clock(self, *trackers: ValueTracker, rate: float = 1.0):
        """Advance trackers with real time (fog drift, slow camera moves)."""
        # Step by the renderer's clock, not by dt: Manim skips updaters during cached plays
        # but still advances renderer.time, so dt-driven clocks fall behind by the cached time.
        def ticker(last=[self.renderer.time]):
            def tick(m, dt, r=rate):
                now = self.renderer.time
                if now > last[0]:
                    m.increment_value(r * (now - last[0]))
                    last[0] = now
            return tick
        for tr in trackers:
            tr.add_updater(ticker([self.renderer.time]))
            self.add(tr)


# ── Rig: every surface parameter as a ValueTracker ────────────────────
class Rig:
    """State for a SurfacePlate. Numbers and number-tuples become ValueTrackers,
    anything else (slices, disc, gauss) is stored as a value or a zero-arg callable."""

    def __init__(self, **state):
        self.vt: dict = {}
        self.dyn: dict = {}
        self.set(**state)

    @staticmethod
    def _is_num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def set(self, **kw) -> "Rig":
        for k, v in kw.items():
            if self._is_num(v):
                if k in self.vt:
                    self.vt[k].set_value(v)
                else:
                    self.vt[k] = ValueTracker(float(v))
            elif isinstance(v, tuple) and v and all(self._is_num(x) for x in v):
                if k in self.vt:
                    for t, x in zip(self.vt[k], v):
                        t.set_value(x)
                else:
                    self.vt[k] = tuple(ValueTracker(float(x)) for x in v)
            else:
                self.dyn[k] = v
        return self

    def __getitem__(self, k):
        return self.vt[k]

    def val(self, k):
        t = self.vt[k]
        return tuple(x.get_value() for x in t) if isinstance(t, tuple) else t.get_value()

    def state(self) -> dict:
        s = {k: self.val(k) for k in self.vt}
        for k, v in self.dyn.items():
            s[k] = v() if callable(v) else v
        return s

    def to(self, **kw) -> list:
        """Animations that move trackers to new values: self.play(*rig.to(yaw=-20))."""
        out = []
        for k, v in kw.items():
            t = self.vt[k]
            if isinstance(t, tuple):
                out += [ti.animate.set_value(vi) for ti, vi in zip(t, v)]
            else:
                out.append(t.animate.set_value(v))
        return out

    def trackers(self) -> list:
        out = []
        for t in self.vt.values():
            out += list(t) if isinstance(t, tuple) else [t]
        return out

    def plate(self, **kw) -> SurfacePlate:
        return SurfacePlate(self.state, **kw)


# ── surfaces used in the video (H as (a, b, c) = [[a, b], [b, c]]) ─────
H_DOME, H_BOWL, H_SADDLE = (-2.0, 0.0, -2.0), (2.0, 0.0, 2.0), (2.0, 0.0, -2.0)
H_PUZZLE = (2.0, 3.0, 2.0)
H_TWIST = (0.0, 1.0, 0.0)

# Faraway hills that make the foggy plain read as a landscape (seeded, far from 0).
_rng = np.random.default_rng(2)
FAR_HILLS = [(float(r * math.cos(a)), float(r * math.sin(a)), float(h), float(s))
             for r, a, h, s in zip(_rng.uniform(5.5, 9.0, 9), _rng.uniform(0, 2 * math.pi, 9),
                                   _rng.uniform(6.0, 14.0, 9), _rng.uniform(1.2, 2.2, 9))]

FOG_COL = "#4A5468"


def fog_rig(H=(0.0, 0.0, 0.0), **kw) -> Rig:
    """The foggy hill (intro, Ch5 return, outro). Camera looks east (+x)."""
    st = dict(H=H, w=(1.0, 1.0, 0.0, 0.0), gauss=FAR_HILLS, zs=0.11, zclip=1.5,
              R=10.0, edge=0.8, yaw=183.0, pitch=13.0, dist=6.6, fov=40.0,
              target=(0.0, 0.0, 0.35), fog=0.11, fog_height=0.8, sky=0.9,
              fog_color=FOG_COL, zlo=-2.0, zhi=2.0, grid=(0.10, 0.10), time=0.0,
              contour=0.0, contour_step=0.25, tint=0.0, opacity=1.0,
              disc_a=0.0, slices=[], disc=None)
    st.update(kw)
    rig = Rig(**st)
    rig.dyn["disc"] = lambda: tangent_disc(0, 0, 0.45, rig.val("disc_a")) if rig.val("disc_a") > 0.003 else None
    return rig


def puzzle_rig(**kw) -> Rig:
    """The puzzle surface x² + 3xy + y² as first seen in the intro."""
    st = dict(H=H_PUZZLE, zs=0.3, zclip=1.6, R=2.6, edge=0.72, yaw=-58.0, pitch=30.0,
              dist=8.5, fov=38.0, target=(0.0, 0.0, 0.0), fog=0.02, sky=0.0,
              grid=(0.18, 0.18), contour=0.0, contour_step=0.2, tint=0.0, opacity=1.0,
              zlo=-1.5, zhi=1.5, time=0.0, slices=[], disc=None,
              # luminous look (as ch2.LUMINOUS_PANEL; the plate is a viewport, so glow only)
              lum=1.0, bloom=0.4, fog_color=S.STAGE)
    st.update(kw)
    return Rig(**st)


# ── motifs ───────────────────────────────────────────────────────────
def walker(radius: float = 0.075, color=S.GRAD) -> VGroup:
    """The yellow 'you are here' dot with a soft glow (concentric translucent discs)."""
    g = VGroup(*[Circle(radius=radius * f, stroke_width=0).set_fill(color, o)
                 for f, o in ((3.2, 0.06), (2.3, 0.10), (1.6, 0.18))])
    return VGroup(g, Dot(radius=radius, color=color))


def pin(mob, plate: SurfacePlate, xyz_fn, offset=ORIGIN):
    """Keep `mob` centred on the projection of world point xyz_fn() (+ screen offset)."""
    mob.add_updater(lambda m: m.move_to(plate.project(*xyz_fn()) + np.array(offset)))
    return mob


def on_surface(plate: SurfacePlate, x, y, lift: float = 0.0):
    """xyz_fn for pin(): a point lying on the surface."""
    def fn():
        xx, yy = (x() if callable(x) else x), (y() if callable(y) else y)
        return xx, yy, float(plate.height(xx, yy)) + lift
    return fn


def label(text: str, size: float = 30, color=S.TEXT, **kw) -> Text:
    return Text(text, font=S.FONT, font_size=size, color=color, **kw)


def tex(*parts, size: float = 44, colors: dict | None = None) -> MathTex:
    m = MathTex(*parts, font_size=size, color=S.TEXT)
    for i, c in (colors or {}).items():
        m[i].set_color(c)
    return m


# ── Ch1 axes and the hand-off tangent line (end of intro → start of Ch1) ──
CH1_X, CH1_Y = (-3, 3, 1), (-0.5, 4.5, 1)
CH1_XL, CH1_YL = 8.4, 5.6
CH1_ORIGIN = np.array([0.0, -2.35, 0.0])
X0_HANDOFF = 1.0                      # the tangent point (1, 1), slope 2


def graph_grid(ax: Axes) -> VGroup:
    """Major lines at every tick, minor lines halfway, clipped to the axes' box."""
    (x0, x1, dx), (y0, y1, dy) = ax.x_range[:3], ax.y_range[:3]
    g = VGroup()
    for step, col, w, op in ((dx / 2, S.GRID_MINOR, 1.0, 0.9), (dx, S.GRID_MAJOR, 1.2, 1.0)):
        n0, n1 = math.ceil(x0 / step - 1e-9), math.floor(x1 / step + 1e-9)
        for i in range(n0, n1 + 1):
            g.add(Line(ax.c2p(i * step, y0), ax.c2p(i * step, y1)).set_stroke(col, w, opacity=op))
    for step, col, w, op in ((dy / 2, S.GRID_MINOR, 1.0, 0.9), (dy, S.GRID_MAJOR, 1.2, 1.0)):
        n0, n1 = math.ceil(y0 / step - 1e-9), math.floor(y1 / step + 1e-9)
        for i in range(n0, n1 + 1):
            g.add(Line(ax.c2p(x0, i * step), ax.c2p(x1, i * step)).set_stroke(col, w, opacity=op))
    return g


def hairline(ax: Axes) -> Axes:
    """Axes on a deep-blue grid: crisp silver axis lines, no numbers (the curve is the subject)."""
    ax.set_stroke(S.TERRAIN_LINE, 1.5, opacity=0.7)
    ax.add_to_back(graph_grid(ax))
    return ax


def panel(width: float, height: float, **_) -> VGroup:
    """Replaces the glass UI cards: a soft dark scrim (no border) with four thin corner marks."""
    from manim import RoundedRectangle
    scrim = RoundedRectangle(width=width, height=height, corner_radius=0.14).set_fill(S.STAGE, 0.55)
    scrim.set_stroke(width=0)
    marks = VGroup()
    L = min(0.24, 0.12 * min(width, height))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cpt = np.array([sx * width / 2, sy * height / 2, 0.0])
            marks.add(VMobject().set_points_as_corners([cpt - np.array([sx * L, 0, 0]), cpt,
                                                        cpt - np.array([0, sy * L, 0])]))
    marks.set_stroke(S.TERRAIN_LINE, 1.4, opacity=0.45)
    return VGroup(scrim, marks)


def hush(mob):
    """Text the redesign removed (uppercase eyebrows): kept in place for layout, never shown."""
    return mob.set_opacity(0.0)


LINE_SCALE = 0.62          # all lit() strokes are thinner than their call sites ask (crisp look)


def _hex(c) -> str:
    return ManimColor(c).to_hex().upper()


def lit(mob, color=None, width: float = 4, halo: float = 16, opacity: float = 0.13):
    """Crisp stroke with a tight edge glow (no blurry shadow). Neutral (silver) lines get
    the cyan → lavender sheen; semantic colours get a slight lift toward white along the
    line. The glow is part of the mobject's own stroke data, so it survives Transform."""
    c = color or mob.get_stroke_color()
    w = width * LINE_SCALE
    if _hex(c) == _hex(S.TERRAIN_LINE):
        cols = [S.CURVE_A, S.CURVE_B]
    else:
        cols = [c, interpolate_color(ManimColor(c), ManimColor("#FFFFFF"), 0.28)]
    mob.set_stroke(cols, w)
    mob.set_stroke(cols, w * 2.2, opacity=min(opacity, 0.12) * 0.7, background=True)
    return mob


def ch1_axes() -> Axes:
    ax = Axes(x_range=CH1_X, y_range=CH1_Y, x_length=CH1_XL, y_length=CH1_YL, tips=False,
              axis_config={"include_ticks": True, "tick_size": 0.06})
    ax.shift(CH1_ORIGIN - ax.c2p(0, 0))
    return hairline(ax)


def tangent_line(ax: Axes, f, df, x0: float, half: float = 1.15, color=S.GRAD, width: float = 5) -> Line:
    """Tangent to y = f(x) at x0, `half` x-units each side, in the axes' coordinates."""
    y0, m = f(x0), df(x0)
    return lit(Line(ax.c2p(x0 - half, y0 - m * half), ax.c2p(x0 + half, y0 + m * half)), color, width)


def handoff_tangent() -> VGroup:
    """Last frame of the intro = first frame of Ch1: a short dim arc of y = x²
    around (1, 1) with its yellow tangent line and point."""
    ax = ch1_axes()
    arc = lit(ax.plot(lambda x: x * x, x_range=[0.45, 1.55]), S.TERRAIN_LINE)
    tl = tangent_line(ax, lambda x: x * x, lambda x: 2 * x, X0_HANDOFF, half=0.8)
    dot = Dot(ax.c2p(X0_HANDOFF, X0_HANDOFF ** 2), radius=0.07, color=S.GRAD)
    return VGroup(arc, tl, dot)


def set_walker_alpha(me: VGroup, a: float) -> VGroup:
    """Fade the walker without flattening its glow (VGroup.set_opacity would)."""
    for circ, o in zip(me[0], (0.06, 0.10, 0.18)):
        circ.set_fill(opacity=o * a)
    me[1].set_opacity(a)
    return me


# ── scene 01 → 02 hand-off: the fog rig exactly as scene 01 leaves it ─────
FOG_YAW_RATE, FOG_DOLLY = 0.18, 0.006


def fog_end_of_s01() -> dict:
    T = scene_range(1)[1] - scene_range(1)[0]
    return dict(H=H_SADDLE, dist=6.6, pitch=24.0, contour=1.0, tint=0.8, disc_a=0.4,
                fog=0.05, time=T, clk=T)


def gd_path(x0=3.0, y0=1.0, step=0.09, eps=0.05):
    """Gradient descent on f = x² + 10y² (H = diag(2, 20)), as in Ch6."""
    pts = [(x0, y0)]
    x, y = x0, y0
    while math.hypot(x, y) > eps:
        x, y = x - step * 2 * x, y - step * 20 * y
        pts.append((x, y))
    return pts


def fog_drift(rig: Rig, clk: ValueTracker) -> Rig:
    """Slow dolly-in and orbit layered on top of the beat-driven dist/yaw."""
    base_dist = rig["dist"]
    rig.dyn["dist"] = lambda: base_dist.get_value() * (1.0 - FOG_DOLLY * clk.get_value())
    rig.dyn["yaw"] = lambda: rig.val("yaw") + FOG_YAW_RATE * clk.get_value()
    return rig


# ── Intro (chapter 0) redesign: the luminous mountain (TerrainPlate) ─────────
# Black stage; the walker's ground is crisp line geometry (the math), the range
# around it is moonlit point-cloud dust (the world). The camera stands in an open
# valley on the −x side looking east (+x), so "ahead" = +x and "sideways" = ±y.
from aion.components.terrain_gl import TerrainPlate  # noqa: E402

DISC_R = 0.36


def terrain_rig(**kw) -> Rig:
    st = dict(H=(0.0, 0.0, 0.0), zs=0.35, win=1.9, zclip=0.0, wm=1.0, edge=60.0,
              yaw=212.0, pitch=26.0, dist=15.0, fov=40.0, target=(0.0, 0.0, 0.45),
              contour=1.0, cstep=0.12, grid=0.22, gstep=0.5, gridR=3.5, reveal=0.0,
              tint=0.0, fog=0.08, fognear=3.0, mist=0.6, haze=0.25, dots=1.0,
              opacity=0.0, time=0.0, disc_a=0.0, disc_r=0.0, gold=0.0, ping_r=0.0, ping_a=0.0,
              fwd=0.0, side=0.0, xs=0.0, ys=0.0, splat=0.0, form=1.0, lift=0.0, aurora=0.0,
              gal=1.0, paint=0.0, paintR=3.5)
    st.update(kw)
    rig = Rig(**st)
    rig.dyn["disc"] = lambda: (0.0, 0.0, rig.val("disc_r"), rig.val("disc_a"))
    rig.dyn["disc_color"] = lambda: interpolate_color(ManimColor(S.TEXT), ManimColor(S.GRAD), rig.val("gold"))
    rig.dyn["ping"] = lambda: (rig.val("ping_r"), rig.val("ping_a"))
    rig.dyn["slices"] = lambda: [(0.0, rig.val("fwd"), S.SMILE, 2.4), (90.0, rig.val("side"), S.FROWN, 2.4),
                                 (0.0, rig.val("xs"), S.HX, 2.6), (90.0, rig.val("ys"), S.HY, 2.6)]
    return rig


YAW_DRIFT = 0.3                      # deg/s of slow orbit under the whole intro


def pulse(mob, change):
    """Go to `change(copy)` and back. The there-and-back lives inside the update function,
    so a beat's play-level rate_func (which overrides per-animation rates) can't break it."""
    a0, a1 = mob.copy(), change(mob.copy())
    return UpdateFromAlphaFunc(mob, lambda m, a: m.interpolate(a0, a1, there_and_back(a)))


def window(u0: float, u1: float, ease=smooth):
    """Rate function that runs `ease` over the fraction [u0, u1] of an animation."""
    return lambda u: ease(min(1.0, max(0.0, (u - u0) / (u1 - u0))))


def intro_rig(clk: ValueTracker, **kw) -> Rig:
    """terrain_rig whose yaw keeps drifting slowly with the scene clock `clk`."""
    rig = terrain_rig(**kw)
    rig.dyn["yaw"] = lambda: rig.val("yaw") + YAW_DRIFT * clk.get_value()
    return rig


SPLATS = 120_000                     # Gaussian splats in the intro's mountain range (0 = none)
# the intro world: splat mountains that condense in place, a parametric gradient ground,
# aurora-tinted lines, the old
# moonlit dust turned down so the splats carry the range
SPLAT_LOOK = dict(splat=1.0, aurora=1.0, dots=0.35, gal=0.0, paint=0.42)


def terrain_plate(rig: Rig, splats: int = 0) -> TerrainPlate:
    return TerrainPlate(rig.state, splats=splats)


# Scene 01's last frame = scene 02's first frame (built from these numbers in both).
S01_END = dict(H=H_SADDLE, opacity=1.0, reveal=60.0, dist=7.0, pitch=22.0, yaw=215.0,
               target=(0.0, 0.0, 0.3), fog=0.06, fognear=3.0, mist=0.5, haze=0.25,
               contour=1.0, grid=0.35, tint=1.0, disc_a=0.6, disc_r=DISC_R, gold=0.0, form=1.0, **SPLAT_LOOK)

# The puzzle surface x² + 3xy + y² as the luminous plate shows it (scene 02).
PUZZLE_VIEW = dict(H=H_PUZZLE, zs=0.3, win=40.0, zclip=1.6, wm=0.0, edge=2.7,
                   yaw=302.0, pitch=30.0, dist=8.5, target=(0.0, 0.0, 0.0),
                   cstep=0.15, gstep=0.3, grid=0.35, gridR=40.0, tint=0.0,
                   fog=0.0, mist=0.2, haze=0.0, disc_a=0.0, paintR=3.2)


def glass_grid(cell: float = 1.15, center=ORIGIN):
    """HessianGrid in the design system's glass style (stage-raised body, silver rim)."""
    from aion.components.matrix_grid import HessianGrid
    g = HessianGrid(cell=cell, center=center, stroke=S.TERRAIN_LINE)
    for b in g.boxes:
        b.set_fill(S.STAGE_RAISED, 0.92).set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.55)
    return g
