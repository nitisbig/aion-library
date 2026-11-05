"""Chapter 3 layout (scenes 09–12): the slopes × directions table that becomes the Hessian.

Every scene rebuilds the previous scene's last frame from these builders, so the
table, its labels and entries land on identical pixels across cuts.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, MathTex, VGroup

from aion import style as S
from aion.components.matrix_grid import HessianGrid
from aion.components.surface_gl import slice_line, tangent_disc

import shared as V
import ch2 as L2

CELL, GAP = 1.45, 0.18
TABLE_C = np.array([-2.75, -0.7, 0.0])         # grid centre while the inset is up (09)
CORNER_C, CORNER_S = np.array([5.0, 2.45, 0.0]), 0.58   # grid centre / scale beside the xy surface (10)
MID_C = np.array([0.35, 0.2, 0.0])             # grid centre once the inset is gone (11)
ENTRY_COL = {"xx": S.HX, "yy": S.HY, "xy": S.TWIST, "yx": S.TWIST}
ENTRY_AT = {"xx": (0, 0), "xy": (0, 1), "yx": (1, 0), "yy": (1, 1)}

# the inset of scene 09: the ch2 saddle, an x slice (smiles) and a y slice (frowns)
INSET_C, INSET_W, INSET_H = np.array([3.75, -0.35, 0.0]), 5.9, 5.0


def entry(name: str, size: float = 54) -> MathTex:
    return MathTex(f"f_{{{name}}}", font_size=size, color=ENTRY_COL[name])


def table():
    """(group, grid, rows, cols) at TABLE_C, scale 1, cells dim and empty.

    cols[0] is "move in" + x (the caption spans both columns), cols[1] is y."""
    grid = glass(HessianGrid(cell=CELL, gap=GAP, center=TABLE_C, tint_scale=TINT))
    for b in grid.boxes:
        b.set_stroke(opacity=0.3)
    step = CELL + GAP
    rows = VGroup(MathTex(r"\frac{\partial f}{\partial x}", font_size=52, color=S.HX),
                  MathTex(r"\frac{\partial f}{\partial y}", font_size=52, color=S.HY))
    for i, r in enumerate(rows):
        r.move_to(TABLE_C + LEFT * (step + 0.4) + UP * (0.5 - i) * step, aligned_edge=RIGHT)
    top = TABLE_C + UP * (step + 0.3)
    xs = [MathTex(v, font_size=50, color=c).move_to(top + RIGHT * (j - 0.5) * step)
          for j, (v, c) in enumerate((("x", S.HX), ("y", S.HY)))]
    move_in = V.label("move in", 28, S.MUTED).move_to(top + UP * 0.5)
    cols = VGroup(VGroup(move_in, xs[0]), xs[1])
    return VGroup(grid, rows, cols), grid, rows, cols


TINT = 0.4                                     # glass cells: colour fills at 40% of the old strength


def glass(grid):
    """Design-system glass cells: stage-raised body, silver hairline rim."""
    for b in grid.boxes:
        b.set_stroke(S.TERRAIN_LINE, 1.6, opacity=0.55).set_fill(S.STAGE_RAISED, 1.0)
    return grid


def lit(box):
    """The 'lit' look of an empty cell (scene 09 'four second derivatives'). Works on .animate too."""
    return box.set_stroke(S.TERRAIN_LINE, 2.2, opacity=0.9).set_fill(S.GLASS_TOP, 1.0)


def placement(group, grid, s_from: float, s_to: float, at) -> tuple[float, np.ndarray]:
    """(scale factor, group centre) that puts the grid's centre at `at` with absolute scale s_to.

    Use as `group.scale(k).move_to(c)` or `group.animate.scale(k).move_to(c)`."""
    d = (grid.boxes.get_center() - group.get_center()) / s_from
    return s_to / s_from, np.array(at, float) - s_to * d


def fill_static(grid, name: str, size: float = 54):
    i, j = ENTRY_AT[name]
    grid.fill(i, j, entry(name, size))
    box = grid.cells[i][j]
    box.set_fill(ENTRY_COL[name], 0.3 * TINT).set_stroke(ENTRY_COL[name], 2.5, opacity=1.0)


def s09_end():
    """Scene 09's last table: lit cells, f_xx and f_yy filled."""
    g, grid, rows, cols = table()
    for b in grid.boxes:
        lit(b)
    fill_static(grid, "xx")
    fill_static(grid, "yy")
    return g, grid, rows, cols


def inset_rig(clk, sx, sy, **kw) -> V.Rig:
    st = dict(H=V.H_SADDLE, zs=0.32, zclip=0.0, R=1.55, edge=0.74, yaw=-60.0, pitch=27.0, dist=6.4,
              fov=34.0, target=(0.0, 0.0, 0.0), fog=0.02, grid=(0.25, 0.25), grid_step=0.35,
              zlo=-0.8, zhi=0.8, opacity=1.0, slices=[], disc=None, **L2.LUMINOUS_PANEL)
    st.update(kw)
    r = V.Rig(**st)
    r.dyn["yaw"] = lambda: r.val("yaw") + 5.0 * clk.get_value()
    r.dyn["slices"] = lambda: [s for s in (
        slice_line(0, color=S.HX, line=sx.get_value(), plane=0.35 * sx.get_value()) if sx.get_value() > 0.003 else None,
        slice_line(90, color=S.HY, line=sy.get_value(), plane=0.35 * sy.get_value()) if sy.get_value() > 0.003 else None)
        if s is not None]
    return r


# scene 10: the twist surface z = xy, set right of the readout column
XY_C, XY_W, XY_H = np.array([1.6, -0.2, 0.0]), 10.6, 7.6
STEP_N = 0.6                                    # the walker's step north


def xy_rig(**kw) -> V.Rig:
    st = dict(H=V.H_TWIST, zs=0.38, zclip=0.0, R=1.6, edge=0.76, yaw=-78.0, pitch=30.0, dist=8.0,
              fov=30.0, target=(0.0, 0.1, 0.0), fog=0.02, grid=(0.22, 0.22), grid_step=0.4,
              zlo=-1.0, zhi=1.0, opacity=1.0, slices=[], disc=None, **L2.LUMINOUS_PANEL)
    st.update(kw)
    return V.Rig(**st)


READ_X, READ_Y = -5.75, (0.55, -0.55, -1.65)   # readout column (gauge centre x, row ys)


def inset_gauge(plate, axis: str):
    """Bend gauge floating over the end of the inset's x (smile, +2) or y (frown, −2) slice."""
    from aion.components.bend_gauge import BendGauge
    k, (x, y) = (2.0, (1.2, 0.0)) if axis == "x" else (-2.0, (0.0, 1.2))
    g = BendGauge(k, width=0.95, stroke=8)
    g.add_updater(lambda m: m.place(plate.surface_point(x, y) + UP * 0.55))
    return g


# ── scene 10 ────────────────────────────────────────────────────────────────
TWIST_AT = np.array([5.15, 1.22, 0.0])         # the twist ribbon's first home: under the corner table, above the rulings
XY_SPIN = 0.5                                  # degrees of yaw per second on the xy surface


def s10_table():
    """Scene 10's table: f_xx, f_yy, f_xy filled, f_yx faint violet, parked in the corner."""
    g, grid, rows, cols = s09_end()
    fill_static(grid, "xy")
    grid.cells[1][0].set_fill(S.TWIST, 0.12 * TINT).set_stroke(S.TWIST, 2.5, opacity=1.0)
    k, c = placement(g, grid, 1.0, CORNER_S, CORNER_C)
    g.scale(k).move_to(c)
    return g, grid, rows, cols


def ruling_ext(y: float, R: float = 1.6) -> float:
    """Half-length of the ruling at height y that stays inside the surface's rounded edge."""
    return 0.97 * R * max(0.0, 1 - (abs(y) / (0.97 * R)) ** 4) ** 0.25


RULING_YS = np.linspace(-1.4, 1.4, 9)


def xy_rulings(plate, show, h0, hp, hn):
    """Straight lines y = const on z = xy (their slope is y): the surface's rulings.

    show: overall opacity tracker; h0 / hp / hn: highlight trackers for y = 0, y > 0, y < 0."""
    from manim import Line, ManimColor, always_redraw, interpolate_color

    def make():
        g = VGroup()
        a = show.get_value()
        for y in RULING_YS:
            hl, col = (h0, S.TEXT) if abs(y) < 1e-9 else (hp, S.GRAD) if y > 0 else (hn, S.GRAD)
            k = hl.get_value()
            e = ruling_ext(y)
            pa = plate.project(-e, y, float(plate.height(-e, y)) + 0.01)
            pb = plate.project(e, y, float(plate.height(e, y)) + 0.01)
            c = interpolate_color(ManimColor(S.TERRAIN_LINE), ManimColor(col), k)
            g.add(Line(pa, pb, stroke_width=2.5 + 2.5 * k, color=c).set_opacity(a * (0.55 + 0.45 * k)))
        return g
    return always_redraw(make)


def readouts():
    """Scene 10's three readouts: f_xx = 0 (flat), f_yy = 0 (flat), f_xy = 1 (ribbon)."""
    from aion.components.bend_gauge import BendGauge, TwistGauge
    rows = VGroup()
    for (name, val), y in zip((("xx", "0"), ("yy", "0"), ("xy", "1")), READ_Y):
        if name == "xy":
            icon = TwistGauge(1.0, width=0.95).move_to([READ_X, y, 0])
        else:
            icon = BendGauge(0.0, width=0.95, stroke=7).place(np.array([READ_X, y, 0])).clear_updaters()
        t = MathTex(f"f_{{{name}}}", "=", val, font_size=46, color=S.TEXT)
        t[0].set_color(ENTRY_COL[name])
        t.move_to([READ_X + 0.75, y, 0], aligned_edge=LEFT)
        rows.add(VGroup(icon, t))
    return rows


def zxy_label() -> MathTex:
    m = MathTex("z", "=", "x", "y", font_size=54, color=S.TEXT)
    m[2].set_color(S.HX)
    m[3].set_color(S.HY)
    return m.move_to([-5.2, 2.75, 0])


# ── scene 11 ────────────────────────────────────────────────────────────────
HC = np.array([0.6, 0.15, 0.0])               # the finished matrix's centre
TIGHT = 0.06                                   # gap between cells once they become a matrix


def tight_center(i: int, j: int, at=HC) -> np.ndarray:
    step = CELL + TIGHT
    return np.array(at, float) + (j - 0.5) * step * RIGHT + (0.5 - i) * step * UP


def h_label(grid) -> MathTex:
    return MathTex("H", "=", font_size=64, color=S.TEXT).next_to(grid.brackets, LEFT, buff=0.3)


def diagonal(grid, clear: float = 0.6):
    """The mirror line, corner to corner, broken around the two diagonal entries."""
    from manim import DashedLine
    a = grid.cells[0][0].get_corner(UP + LEFT) + np.array([-0.25, 0.25, 0])
    b = grid.cells[1][1].get_corner(DOWN + RIGHT) + np.array([0.25, -0.25, 0])
    u = (b - a) / np.linalg.norm(b - a)
    cuts = sorted(float((grid.cells[i][i].get_center() - a) @ u) for i in range(2))
    spans = [(0.0, cuts[0] - clear), (cuts[0] + clear, cuts[1] - clear), (cuts[1] + clear, float(np.linalg.norm(b - a)))]
    return VGroup(*[DashedLine(a + u * s0, a + u * s1, dash_length=0.1, color=S.MUTED, stroke_width=3)
                    for s0, s1 in spans if s1 - s0 > 0.05]).set_opacity(0.8)


def s11_end():
    """Scene 11's last frame: H = [f_xx f_xy; f_yx f_yy], tight, bracketed, with the diagonal."""
    grid = glass(HessianGrid(cell=CELL, gap=TIGHT, center=HC, tint_scale=TINT))
    for name in ("xx", "xy", "yx", "yy"):
        fill_static(grid, name)
    grid.show_brackets()
    return grid, h_label(grid), diagonal(grid)


def tag_spot(box) -> np.ndarray:
    """Where a symbolic entry parks as a small corner tag (scene 12)."""
    return box.get_corner(UP + LEFT) + np.array([0.3, -0.22, 0])


TAG_S = 0.42


# ── scene 12's last frame (scene 13 starts on it) ──────────────────────────
S12_LEFT_C = np.array([-3.4, -0.3, 0.0])     # matrix centre beside the puzzle flashback
S12_PLATE = dict(width=6.6, height=5.4, center=np.array([3.3, -0.45, 0.0]))
PUZZLE_KW = dict(contour=0.8, contour_step=0.15)
S12_NUMS = (((0, 0), "2", S.HX), ((0, 1), "3", S.TWIST), ((1, 0), "3", S.TWIST), ((1, 1), "2", S.HY))


def puzzle_f() -> MathTex:
    f = MathTex("f", "=", "x^2", "+", "3xy", "+", "y^2", font_size=62, color=S.TEXT)
    f[2].set_color(S.HX)
    f[4].set_color(S.TWIST)
    f[6].set_color(S.HY)
    return f.move_to(UP * 2.85)


def s12_end():
    """(mat, grid, nums, halo): the numeric Hessian with corner tags and its gold halo, at S12_LEFT_C."""
    from manim import Group
    from aion.components.glow import glow_halo
    grid, hl, _ = s11_end()
    for i in range(2):
        for j in range(2):
            grid.entries[i][j].scale(TAG_S).move_to(tag_spot(grid.cells[i][j]))
    nums = {}
    for (i, j), s, c in S12_NUMS:
        nums[(i, j)] = MathTex(s, font_size=76, color=c).move_to(grid.cells[i][j])
        grid.add(nums[(i, j)])
    halo = glow_halo(VGroup(*nums.values(), grid.brackets), S.GRAD, core_alpha=0.35, bloom_alpha=0.3)
    mat = VGroup(grid, hl)
    Group(mat, halo).shift(S12_LEFT_C - HC)
    return mat, grid, nums, halo
