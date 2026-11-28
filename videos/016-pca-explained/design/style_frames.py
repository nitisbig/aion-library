"""Style frames for video 016, "PCA Explained Visually": stills at 1920x1080, rendered through aion.

    uv run python videos/016-pca-explained/design/style_frames.py         # all → design/style_frames/*.png
    uv run python videos/016-pca-explained/design/style_frames.py 3 7     # only frames 3 and 7

Each frame is an `@scene(0, 10)` rendered with `sd.comp((1920, 1080), 30).frame(t, ...)`, so it goes through the same
theme, LaTeX, Manim rasteriser and GPU compositor as the video. Every value comes from pcadata.py (seeded, numpy).
One process per frame (2 cores, little RAM).

    1 in_s01   the lamp, the sculpture and its best shadow (pyvista, real cast shadow); shadow board in the rail
    2 in_s03   1,797 digits in two numbers, coloured by class, numerals at centroids; PCA title lockup
    3 ch1_s03  L2: variance squares, spread bars along height, arm span and the diagonal; rail B_cloud
    4 ch2_s02  L3: most spread vs closest fit, one point's right triangle with squares; PC1 glow
    5 ch3_s02  L2: signed deviation rectangles and the 2x2 covariance matrix; rail B_dial, B_varu
    6 ch4_s01  L2: a fan of arrows under C, the two eigenvectors stay on their lines (glow); Cv = λv
    7 ch5_s03  L2: eigen-digits, a 3 rebuilt with k = 1 … 64; rail B_recipe, B_scree
    8 ch6_s02  L3: a rolled sheet and its flat PCA shadow, layers mixed
    9          reference → design/components.png: layouts L1-L4 with rail geometry, chapter card, type scale, palette
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

DESIGN = Path(__file__).resolve().parent
VIDEO = DESIGN.parent
REPO = VIDEO.parent.parent
OUT = DESIGN / "style_frames"
sys.path.insert(0, str(VIDEO))

W, H, FPS, T_STILL = 1920, 1080, 30, 5.0
PX = 135.0                          # px per world unit at 1080p
XW, YH = 64 / 9, 4.0                # half frame (world units)
SAFE = 0.71                         # text-safe inset (96 px)
X0, X1, Y0, Y1 = -XW + SAFE, XW - SAFE, -YH + SAFE, YH - SAFE   # the safe box: -6.40..6.40, -3.29..3.29
GAP = 0.25
STAGE_L2 = (X0, Y0, 2.30, Y1)       # L2 main stage
RAIL = (2.55, Y0, X1, Y1)           # L2 rail: three slots
SLOT_GAP = 0.2
LEFT_L3, RIGHT_L3 = (X0, -3.0, -GAP / 2, 3.0), (GAP / 2, -3.0, X1, 3.0)
FILL, DIM = 0.12, 0.35

NAMES_OUT = {1: "01_in_shadow", 2: "02_in_digit_map", 3: "03_ch1_spread", 4: "04_ch2_two_views",
             5: "05_ch3_inside_C", 6: "06_ch4_eigen", 7: "07_ch5_rebuild", 8: "08_ch6_curved",
             9: "../components"}


# ------------------------------------------------------------------------------------------------ setup
def _import_aion():
    """Activate video 016's theme and pull aion's names (Manim included) into this module."""
    from aion.render.project import load_video

    load_video("016", (W, H), FPS, only=["__none__"])           # theme on, no scenes imported
    import aion
    from aion.components.linalg import Mat, brackets, grid_lines, panel
    from aion.render import scenes as scene_mod

    import pcadata

    g = globals()
    for k in aion.__all__:
        g.setdefault(k, getattr(aion, k))
    g.update(grid_lines=grid_lines, panel=panel, Mat=Mat, brackets=brackets, scene_mod=scene_mod, pd=pcadata)


# ---------------------------------------------------------------------------------------------- helpers
def tex(s, size=48, color=None):
    return MathTex(s, font_size=size, color=color or C.text)  # noqa: F821


def sans(s, size=30, color=None):
    return Tex(r"\textsf{" + s + "}", font_size=size, color=color or C.text)  # noqa: F821


def caps(s, size=34, color=None):
    return Tex(r"\textsc{" + s + "}", font_size=size, color=color or C.text)  # noqa: F821


def P3(x, y):
    return np.array([float(x), float(y), 0.0])  # noqa: F821


def rgb255(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tint(color, a):
    """`color` at opacity `a` over black, mixed in linear light, as one solid hex (fills that must hide what's under)."""
    c = np.array(rgb255(color)) / 255.0  # noqa: F821
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4) * a  # noqa: F821
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)  # noqa: F821
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in srgb)


def backed(mob, pad=0.06):
    bg = Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_width=0, fill_color=C.bg,  # noqa: F821
                   fill_opacity=1.0).move_to(mob.get_center())
    return VGroup(bg, mob)  # noqa: F821


def dim(mob, k=DIM):
    for sm in mob.family_members_with_points():
        sm.set_stroke(opacity=sm.get_stroke_opacity() * k, family=False)
        sm.set_fill(opacity=sm.get_fill_opacity() * k, family=False)
    return mob


def board(box, tag=None):
    """A framed board (Classic panel) with an optional key-word tag inside its top-left corner."""
    g = VGroup(panel(*box))  # noqa: F821
    if tag:
        g.add(sans(tag, 24, C.muted).move_to(P3(box[0] + 0.16, box[3] - 0.16), aligned_edge=UL))  # noqa: F821
    return g


def slot(i):
    """Rail slot i (0 top … 2 bottom) of the L2 rail."""
    x0, y0, x1, y1 = RAIL
    h = (y1 - y0 - 2 * SLOT_GAP) / 3
    top = y1 - i * (h + SLOT_GAP)
    return (x0, top - h, x1, top)


def rail_board(i, content, tag):
    """A finished result pinned in rail slot i: its board, its tag, its content scaled to fit under the tag."""
    box = slot(i)
    b = board(box, tag)
    w, h = box[2] - box[0] - 0.4, box[3] - box[1] - 0.55
    content.scale(min(w / content.width, h / content.height, 1.0))
    content.move_to(P3((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - 0.12))
    return VGroup(b, content)  # noqa: F821


def empty_slot(i):
    x0, y0, x1, y1 = slot(i)
    r = DashedVMobject(Rectangle(width=x1 - x0, height=y1 - y0), num_dashes=40)  # noqa: F821
    return r.set_stroke(C.roles["ghost"] if hasattr(C, "roles") else "#2b2b2b", 1.6).move_to(P3((x0 + x1) / 2, (y0 + y1) / 2))  # noqa: F821


class Plane2:
    """A centred data plane: world position of a data point (cm deviations) at `scale` units per cm about `c`."""

    def __init__(self, c, scale):
        self.c, self.k = np.asarray(c, float), scale  # noqa: F821

    def p(self, x, y):
        return P3(self.c[0] + self.k * x, self.c[1] + self.k * y)

    def grid(self, box, step_cm=10, minor=2):
        return grid_lines(np.eye(2), self.c, self.k * step_cm, box, n=16, minor=minor)  # noqa: F821


def glow(s, color, z=2, k=1.0):
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=C.glow_r)])  # noqa: F821


def people():
    P = pd.people2()  # noqa: F821
    V = P.V.copy()
    if V[1, 1] < 0:                                    # PC2 positive = arms long for one's height
        V[:, 1] *= -1
    return P, P.Xc, V


def dots(pts, color, r=0.055, opacity=1.0):
    return VGroup(*[Dot(p, radius=r, color=color, fill_opacity=opacity) for p in pts])  # noqa: F821


def heat_tile(vals, size, cmap="div", vmax=None):
    """An 8x8 array as crisp squares: cmap 'grey' (0..16) or 'div' (C.data negative, black, C.spread positive)."""
    g = VGroup()  # noqa: F821
    a = np.asarray(vals, float).reshape(8, 8)  # noqa: F821
    cell = size / 8
    vmax = vmax or (16.0 if cmap == "grey" else np.abs(a).max())  # noqa: F821
    for r in range(8):
        for c in range(8):
            v = a[r, c]
            if cmap == "grey":
                g_ = int(round(255 * min(max(v / vmax, 0), 1)))
                col = f"#{g_:02X}{g_:02X}{g_:02X}"
            else:
                col = tint(C.spread if v > 0 else C.data, min(abs(v) / vmax, 1.0))
            g.add(Square(side_length=cell, stroke_width=0, fill_color=col, fill_opacity=1.0)  # noqa: F821
                  .move_to(P3((c - 3.5) * cell, (3.5 - r) * cell)))
    frame = Square(side_length=size, stroke_color=C.roles["frame"], stroke_width=1.4, fill_opacity=0)  # noqa: F821
    return VGroup(g, frame)  # noqa: F821


# ----------------------------------------------------------------------------------------------- frames
SHADOW = {}


def shadow_render(px_w=1920, px_h=1080):
    """PyVista off-screen: the sculpture as lit spheres in front of a wall, a warm spot lamp, real cast shadows.

    The sculpture is turned so its top principal plane faces the lamp: the shadow shows three clusters and a spiral.
    """
    import pyvista as pv

    S = pd.sculpture()  # noqa: F821
    Q = pd.pca(S)  # noqa: F821
    pts = (S - Q.mu) @ Q.V[:, [0, 2, 1]] * 0.5 + np.array([0.0, 0.0, 0.25])  # noqa: F821  PC1→x, PC2→z, PC3→y
    pv.OFF_SCREEN = True
    pl = pv.Plotter(off_screen=True, window_size=(px_w, px_h), lighting="none")
    pl.set_background("black")
    sph = pv.Sphere(radius=0.04, theta_resolution=14, phi_resolution=14)
    pl.add_mesh(pv.PolyData(pts).glyph(geom=sph, scale=False, orient=False), color=C.data, smooth_shading=True,
                ambient=0.12, diffuse=0.85, specular=0.45, specular_power=40)
    pl.add_mesh(pv.Plane(center=(0.6, 2.2, 0.25), direction=(0, -1, 0), i_size=30, j_size=30), color="#A89F8E",
                ambient=0.0, diffuse=0.95)
    pl.add_light(pv.Light(position=(-6.0, -7.5, 1.2), focal_point=(0.0, 0.0, 0.25), color=C.lamp, intensity=1.25,
                          positional=True, cone_angle=20, exponent=8, light_type="scene light"))
    pl.add_light(pv.Light(position=(-6, -4, 5), focal_point=(0, 0, 0), color="#9FB8D8", intensity=0.12,
                          light_type="scene light"))
    pl.enable_shadows()
    pl.camera_position = [(1.6, -8.2, 1.4), (1.05, 1.2, 0.2), (0, 0, 1)]
    pl.camera.view_angle = 30
    SHADOW["rgb"] = pl.screenshot(return_img=True)
    pl.close()
    SHADOW["xy"] = (S - Q.mu) @ Q.V[:, :2]


def f1(s, m):
    """in_s01 + rail preview: the best shadow on the wall; the same shadow pinned crisp in the rail."""
    rgba = np.dstack([SHADOW["rgb"], np.full(SHADOW["rgb"].shape[:2], 255, np.uint8)])  # noqa: F821
    s.add(ArrayLayer(rgba, height=8.0, z=-10))  # noqa: F821
    xy = SHADOW["xy"]
    box = slot(2)
    b = board(box, "best shadow")
    k = min((box[2] - box[0] - 0.5) / np.ptp(xy[:, 0]), (box[3] - box[1] - 0.6) / np.ptp(xy[:, 1]))  # noqa: F821
    c = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - 0.12])  # noqa: F821
    pts = [P3(*(c + k * (p - xy.mean(0)))) for p in xy]
    m.add(b)
    glow(s, C.mean, z=3, k=0.25).add(dots(pts, C.mean, r=0.012))


def f2(s, m):
    """in_s03: the digit map, every class lit, numerals at centroids, the title lockup."""
    D = pd.digits_pca()  # noqa: F821
    _, y = pd.digits()  # noqa: F821
    Z = D.Z[:, :2] * np.array([1, -1])  # noqa: F821
    box = (-5.6, -1.55, 5.6, Y1)
    k = min((box[2] - box[0]) / np.ptp(Z[:, 0]), (box[3] - box[1]) / np.ptp(Z[:, 1]))  # noqa: F821
    c = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2])  # noqa: F821
    W2 = c + k * (Z - (Z.max(0) + Z.min(0)) / 2)
    for d in range(10):
        pos = W2[y == d]
        s.add(PointsLayer(lambda t, pos=pos: pos, color=getattr(C, f"d{d}"), size=5.5, glow=0.25, z=1,  # noqa: F821
                          additive=False))
    top = s.manim(z=3)
    for d in range(10):
        cen = np.median(W2[y == d], 0)  # noqa: F821
        lab = tex(str(d), 44, getattr(C, f"d{d}")).move_to(P3(*cen))
        top.add(Circle(radius=0.27, stroke_color=getattr(C, f"d{d}"), stroke_width=2.2, fill_color=C.bg,  # noqa: F821
                       fill_opacity=0.85).move_to(P3(*cen)), lab)
    title = sans(r"\textbf{PCA}", 64)
    sub = caps("principal component analysis", 34, C.muted)
    lock = VGroup(title, sub).arrange(DOWN, buff=0.18).move_to(P3(0, -2.55))  # noqa: F821
    m.add(lock)
    m.add(tex(r"\mathbb{R}^{64}\;\to\;\mathbb{R}^{2}", 36, C.muted).move_to(P3(X1 - 0.9, Y0 + 0.2)))


def f3(s, m):
    """ch1_s03 (L2): squares on height gaps, spread bars, the diagonal beats both; rail B_cloud."""
    P, Xc, V = people()
    st = STAGE_L2
    pl = Plane2(((st[0] + st[2]) / 2 + 0.2, (st[1] + st[3]) / 2 - 0.1), 0.105)
    m.add(board(st, None))
    m.add(pl.grid((st[0] + 0.05, st[1] + 0.05, st[2] - 0.05, st[3] - 0.05), step_cm=10))
    m.add(backed(sans("height", 26, C.muted)).move_to(pl.p(26, -2.2)))
    m.add(backed(sans("arm span", 26, C.muted)).move_to(pl.p(7.5, 29.5)))
    cand = [i for i in np.argsort(Xc[:, 1]) if 5 < abs(Xc[i, 0]) < 13]  # noqa: F821  moderate gaps
    pick = cand[:: max(1, len(cand) // 5)][:5]
    sq = VGroup()  # noqa: F821
    for i in pick:
        x, yv = Xc[i]
        side = abs(x) * pl.k
        r = Square(side_length=side, stroke_color=C.spread, stroke_width=2.0, fill_color=C.spread,  # noqa: F821
                   fill_opacity=0.10)
        r.move_to(pl.p(x / 2, yv) + UP * side / 2 * (1 if yv >= 0 else -1))  # noqa: F821
        sq.add(r, Line(pl.p(0, yv), pl.p(x, yv), stroke_color=C.spread, stroke_width=2.2))  # noqa: F821
    m.add(sq)
    m.add(dots([pl.p(*p) for p in Xc], C.data))
    m.add(Circle(radius=0.09, stroke_color=C.mean, stroke_width=3).move_to(pl.p(0, 0)))  # noqa: F821
    # spread bars: ±1 sd along height, arm span, and the diagonal (u = (1,1)/√2)
    sd_h, sd_a = math.sqrt(P.C[0, 0]), math.sqrt(P.C[1, 1])
    sd_d = math.sqrt(float(P.var_along(np.array([math.pi / 4]))[0]))  # noqa: F821
    y_bar = -27.0
    m.add(Line(pl.p(-sd_h, y_bar), pl.p(sd_h, y_bar), stroke_color=C.spread, stroke_width=7))  # noqa: F821
    m.add(Line(pl.p(-31, -sd_a), pl.p(-31, sd_a), stroke_color=C.spread, stroke_width=7))  # noqa: F821
    u = np.array([1, 1]) / math.sqrt(2)  # noqa: F821
    gl = glow(s, C.spread, z=3)
    gl.add(Line(pl.p(*(-sd_d * u)), pl.p(*(sd_d * u)), stroke_color=C.spread, stroke_width=7))  # noqa: F821
    m.add(DashedLine(pl.p(*(-30 * u)), pl.p(*(30 * u)), stroke_color=C.muted, stroke_width=1.6, dash_length=0.1))  # noqa: F821
    eq = Eqn(r"\sigma^2 = \tfrac{1}{n}\sum_i \left(x_i-\mu\right)^2", colors={r"\sigma^2": C.spread, r"\mu": C.mean})  # noqa: F821
    m.add(backed(eq.scale(0.72), 0.1).move_to(P3(st[0] + 0.2, st[1] + 0.2), aligned_edge=DL))  # noqa: F821
    # rail
    mini = VGroup(dots([P3(*(p * 0.06)) for p in Xc], C.data, r=0.045),  # noqa: F821
                  Circle(radius=0.07, stroke_color=C.mean, stroke_width=2.5),  # noqa: F821
                  tex(r"\tilde x = x-\mu", 36).shift(DOWN * 1.35))  # noqa: F821
    m.add(rail_board(0, mini, "centre"))


def f4(s, m):
    """ch2_s02 (L3): most spread vs closest fit; one point's right triangle with squares on all sides."""
    P, Xc, V = people()
    u = V[:, 0]
    nrm = np.array([-u[1], u[0]])  # noqa: F821
    for box, tag, mode in ((LEFT_L3, "most spread", "shadow"), (RIGHT_L3, "closest fit", "gap")):
        m.add(board(box, tag))
        pl = Plane2(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - 0.1), 0.118)
        line = Line(pl.p(*(-30 * u)), pl.p(*(30 * u)), stroke_color=C.pc1, stroke_width=4)  # noqa: F821
        glow(s, C.pc1, z=2, k=0.45).add(line)
        proj = (Xc @ u)[:, None] * u
        if mode == "shadow":
            m.add(VGroup(*[Line(pl.p(*a), pl.p(*b), stroke_color=C.muted, stroke_width=1.0, stroke_opacity=0.5)  # noqa: F821
                           for a, b in zip(Xc, proj)]))
            m.add(VGroup(*[Circle(radius=0.045, stroke_color=C.data, stroke_width=2).move_to(pl.p(*q)) for q in proj]))  # noqa: F821
            m.add(dots([pl.p(*p) for p in Xc], C.data, opacity=0.45))
        else:
            m.add(VGroup(*[Line(pl.p(*a), pl.p(*b), stroke_color=C.residual, stroke_width=2.4)  # noqa: F821
                           for a, b in zip(Xc, proj)]))
            m.add(dots([pl.p(*p) for p in Xc], C.data))
        if mode == "shadow":
            sh, gp = Xc @ u, np.abs(Xc @ nrm)
            i = int(np.argmax(gp * (sh > 9) * (sh < 18)))  # a point with a long shadow and a visible gap
            x, q = Xc[i], proj[i]
            O = pl.p(0, 0)
            A, B = pl.p(*q), pl.p(*x)
            def sq_on(p1, p2, color, other):
                """Square on side p1-p2, on the side away from the triangle's third vertex `other`."""
                d = p2 - p1
                n3 = np.array([-d[1], d[0], 0.0])  # noqa: F821
                if np.dot(n3, other - p1) > 0:  # noqa: F821
                    n3 = -n3
                return Polygon(p1, p2, p2 + n3, p1 + n3, stroke_color=color, stroke_width=2.2,  # noqa: F821
                               fill_color=tint(color, 0.18), fill_opacity=1.0)
            hyp = sq_on(O, B, C.mean, A).set_fill(opacity=0)
            m.add(hyp, sq_on(O, A, C.pc1, B), sq_on(A, B, C.residual, O))
            m.add(Line(O, B, stroke_color=C.mean, stroke_width=3.5),  # noqa: F821
                  Line(O, A, stroke_color=C.pc1, stroke_width=5), Line(A, B, stroke_color=C.residual, stroke_width=4),  # noqa: F821
                  RightAngle(Line(A, O), Line(A, B), length=0.14, stroke_color=C.text, stroke_width=1.6),  # noqa: F821
                  Dot(B, radius=0.07, color=C.data))  # noqa: F821
    eq = Eqn(r"\lVert \tilde x\rVert^2 = (\tilde x\cdot u)^2 + d^2",  # noqa: F821
             colors={r"\lVert \tilde x\rVert^2": C.mean, r"(\tilde x\cdot u)^2": C.pc1, r"d^2": C.residual})
    m.add(backed(eq, 0.1).move_to(P3(0, Y0 - 0.15)))


def dial_curve(P, c, r):
    th = np.linspace(0, 2 * math.pi, 361)  # noqa: F821
    v = P.var_along(th)
    rr = r * v / v.max()
    return VMobject(stroke_color=C.spread, stroke_width=3).set_points_smoothly(  # noqa: F821
        [P3(c[0] + a * math.cos(t), c[1] + a * math.sin(t)) for a, t in zip(rr, th)])


def f5(s, m):
    """ch3_s02 (L2): signed deviation rectangles in four quadrants, and the covariance matrix; rail B_dial, B_varu."""
    P, Xc, V = people()
    st = STAGE_L2
    m.add(board(st, None))
    pl = Plane2((st[0] + 2.55, (st[1] + st[3]) / 2 - 0.1), 0.092)
    box = (st[0] + 0.05, st[1] + 0.05, st[0] + 5.1, st[3] - 0.05)
    m.add(pl.grid(box, step_cm=10))
    for x, yv in Xc:
        pos = x * yv > 0
        col = C.spread if pos else C.residual
        m.add(Polygon(pl.p(0, 0), pl.p(x, 0), pl.p(x, yv), pl.p(0, yv), stroke_color=col, stroke_width=1.0,  # noqa: F821
                      stroke_opacity=0.7, fill_color=col, fill_opacity=0.07))
    m.add(dots([pl.p(*p) for p in Xc], C.data))
    m.add(backed(tex(r"+", 40, C.spread)).move_to(pl.p(21, 24)), backed(tex(r"+", 40, C.spread)).move_to(pl.p(-21, -24)),
          backed(tex(r"-", 40, C.residual)).move_to(pl.p(21, -24)), backed(tex(r"-", 40, C.residual)).move_to(pl.p(-21, 24)))
    vals = [[P.C[0, 0], P.C[0, 1]], [P.C[1, 0], P.C[1, 1]]]
    M = Mat([[f"{v:.1f}" for v in row] for row in vals], colors=C.spread, size=40, h_buff=1.3)  # noqa: F821
    lhs = tex(r"C =", 44)
    grp = VGroup(lhs, M).arrange(RIGHT, buff=0.22)  # noqa: F821
    grp.scale(min(1.0, 3.2 / grp.width)).move_to(P3((st[0] + 5.1 + st[2]) / 2, 1.25))
    m.add(grp)
    hl = SurroundingRectangle(VGroup(M.entries[1], M.entries[2]) if hasattr(M, "entries") else M,  # noqa: F821
                              color=C.spread, stroke_width=1.6, buff=0.08)
    eq = Eqn(r"\sigma_{ha} = \tfrac{1}{n}\sum_i \tilde h_i\,\tilde a_i", colors={r"\sigma_{ha}": C.spread}).scale(0.72)  # noqa: F821
    eq.next_to(grp, DOWN, buff=0.7)
    m.add(eq)
    m.add(backed(sans("height", 24, C.muted)).move_to(pl.p(21, -3)), backed(sans("arm span", 24, C.muted)).move_to(pl.p(-8.5, 31)))
    # rail: the dial and the objective
    m.add(rail_board(0, VGroup(dial_curve(P, (0, 0), 1.0), Dot(ORIGIN, radius=0.03, color=C.mean)), "spread vs angle"))  # noqa: F821
    m.add(rail_board(1, tex(r"\max_{\lVert u\rVert=1}\ \tfrac{1}{n}\sum_i(\tilde x_i\cdot u)^2", 40), "objective"))
    m.add(rail_board(2, tex(r"u^\top C\,u", 56, C.text), "one matrix"))
    _ = hl


def f6(s, m):
    """ch4_s01 (L2): a fan of unit arrows and where C sends them; the two eigenvectors stay on their lines."""
    P, Xc, V = people()
    st = STAGE_L2
    m.add(board(st, None))
    c = np.array([(st[0] + st[2]) / 2 - 1.35, -0.15])  # noqa: F821
    R, L1 = 1.1, 2.9
    m.add(grid_lines(np.eye(2), c, 1.0, (st[0] + 0.05, st[1] + 0.05, st[2] - 2.75, st[3] - 0.05), n=16, minor=2,  # noqa: F821
                     opacity=0.55))
    m.add(Circle(radius=R, stroke_color=C.probe, stroke_width=1.4, stroke_opacity=0.5).move_to(P3(*c)))  # noqa: F821
    Cn = P.C / P.lam[0] * L1
    for k in range(24):
        t = 2 * math.pi * k / 24
        uu = np.array([math.cos(t), math.sin(t)])  # noqa: F821
        if min(abs(uu @ V[:, 0]), abs(uu @ V[:, 1])) > 0.995:
            continue
        cu = Cn @ uu
        m.add(Arrow(P3(*c), P3(*(c + R * uu)), buff=0, stroke_width=2.5, color=C.probe, max_tip_length_to_length_ratio=0.12)  # noqa: F821
              .set_opacity(0.35))
        m.add(Arrow(P3(*c), P3(*(c + cu)), buff=0, stroke_width=3, color=C.probe, max_tip_length_to_length_ratio=0.08))  # noqa: F821
    gl = glow(s, C.pc1, z=3)
    for j, col in ((0, C.pc1), (1, C.pc2)):
        v = V[:, j]
        lam = P.lam[j] / P.lam[0] * L1
        m.add(Line(P3(*(c - 3.4 * v)), P3(*(c + 3.4 * v)), stroke_color=col, stroke_width=1.6, stroke_opacity=0.6))  # noqa: F821
        tgt = gl if j == 0 else glow(s, C.pc2, z=3)
        m.add(Arrow(P3(*c), P3(*(c + R * v)), buff=0, stroke_width=3, color=col,  # noqa: F821
                    max_tip_length_to_length_ratio=0.12).set_opacity(0.45))
        for sgn in (1, -1):
            tgt.add(Arrow(P3(*c), P3(*(c + sgn * lam * v)), buff=0, stroke_width=6, color=col,  # noqa: F821
                          max_tip_length_to_length_ratio=0.12 if j == 0 else 0.45))
    m.add(backed(tex(r"v_1", 40, C.pc1)).move_to(P3(*(c + (L1 + 0.35) * V[:, 0]))))
    m.add(backed(tex(r"v_2", 40, C.pc2)).move_to(P3(*(c + (R + 0.3) * V[:, 1]))))
    eq = Eqn(r"C\,v = \lambda\,v", colors={"v": C.pc1, r"\lambda": C.spread}).scale(1.0)  # noqa: F821
    m.add(backed(eq, 0.1).move_to(P3(st[2] - 1.3, 2.4)))
    lam_t = VGroup(tex(rf"\lambda_1 = {P.lam[0]:.1f}", 34, C.spread), tex(rf"\lambda_2 = {P.lam[1]:.1f}", 34, C.spread))  # noqa: F821
    m.add(lam_t.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(P3(st[2] - 1.3, 1.25)))  # noqa: F821
    Mm = Mat([[f"{v:.1f}" for v in row] for row in P.C], colors=C.spread, size=40, h_buff=1.55)  # noqa: F821
    m.add(rail_board(0, VGroup(tex("C =", 44), Mm).arrange(RIGHT, buff=0.2), "covariance"))  # noqa: F821
    m.add(rail_board(1, VGroup(dial_curve(P, (0, 0), 1.0)), "spread vs angle"))  # noqa: F821


def f7(s, m):
    """ch5_s03 (L2): the first eigen-digits, the mean digit, a 3 rebuilt with k components; rail recipe + scree."""
    D = pd.digits_pca()  # noqa: F821
    X, y = pd.digits()  # noqa: F821
    st = STAGE_L2
    m.add(board(st, None))
    row = VGroup(*[heat_tile(D.V[:, j], 0.8) for j in range(7)]).arrange(RIGHT, buff=0.2)  # noqa: F821
    row.move_to(P3((st[0] + st[2]) / 2, 2.2))
    m.add(row)
    for j, t in enumerate(row):
        m.add(tex(rf"v_{{{j + 1}}}", 28, C.pc1 if j == 0 else (C.pc2 if j == 1 else C.muted)).next_to(t, DOWN, buff=0.1))
    eq = Eqn(r"x \approx \mu + \sum_{j\le k} z_j\,v_j", colors={r"\mu": C.mean, "z_j": C.text, "v_j": C.pc1}).scale(1.0)  # noqa: F821
    m.add(backed(eq, 0.08).move_to(P3((st[0] + st[2]) / 2, 0.45)))
    x3 = X[np.where(y == 3)[0][0]]  # noqa: F821
    ks = (1, 3, 5, 10, 20, 64)
    tiles = VGroup()  # noqa: F821
    for k in ks:
        t = heat_tile(np.clip(D.reconstruct(x3, k), 0, 16), 0.92, "grey")  # noqa: F821
        lab = sans(f"k = {k}", 26, C.muted).next_to(t, DOWN, buff=0.14)
        tiles.add(VGroup(t, lab))  # noqa: F821
    tiles.arrange(RIGHT, buff=0.2)
    orig = VGroup(heat_tile(x3, 0.92, "grey"), sans("original", 26, C.muted))  # noqa: F821
    orig[1].next_to(orig[0], DOWN, buff=0.14)
    orig.next_to(tiles, RIGHT, buff=0.5)
    sep = Line(orig[0].get_corner(UL) + LEFT * 0.25, orig[0].get_corner(DL) + LEFT * 0.25,  # noqa: F821
               stroke_color=C.muted, stroke_width=1.2)
    VGroup(tiles, orig, sep).move_to(P3((st[0] + st[2]) / 2, -1.55))  # noqa: F821
    m.add(tiles, orig, sep)
    mean_t = VGroup(heat_tile(D.mu, 0.86, "grey"), tex(r"\mu", 30, C.mean))  # noqa: F821
    mean_t[1].next_to(mean_t[0], DOWN, buff=0.1)
    mean_t.next_to(row, LEFT, buff=0.32)
    _ = mean_t
    # rail: recipe, scree
    steps = VGroup(*[VGroup(sans(a, 26, C.muted), tex(b, 30)).arrange(RIGHT, buff=0.25) for a, b in (  # noqa: F821
        ("centre", r"\tilde X = X-\mu"), ("covariance", r"C=\tfrac1n\tilde X^{\top}\tilde X"),
        ("eigenvectors", r"Cv_j=\lambda_j v_j"), ("sort", r"\lambda_1\ge\lambda_2\ge\dots"),
        ("project", r"z = V_k^{\top}\tilde x"))]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    m.add(rail_board(0, steps, "recipe"))
    sh = D.share
    bars = VGroup(*[Rectangle(width=0.05, height=max(sh[j] * 9, 0.002), stroke_width=0, fill_color=C.spread,  # noqa: F821
                              fill_opacity=0.9).move_to(P3(0.065 * j, sh[j] * 4.5)) for j in range(64)])
    cum = np.cumsum(sh)  # noqa: F821
    curve = VMobject(stroke_color=C.pc1, stroke_width=2.5).set_points_as_corners(  # noqa: F821
        [P3(0.065 * j, cum[j] * 1.9) for j in range(64)])
    k90 = pd.k_for(sh, 0.9)  # noqa: F821
    line90 = DashedLine(P3(-0.05, 0.9 * 1.9), P3(64 * 0.065, 0.9 * 1.9), stroke_color=C.muted, stroke_width=1.2,  # noqa: F821
                        dash_length=0.05)
    mark = VGroup(Dot(P3(0.065 * (k90 - 1), cum[k90 - 1] * 1.9), radius=0.04, color=C.pc1),  # noqa: F821
                  sans(f"{k90}", 22, C.pc1).next_to(P3(0.065 * (k90 - 1), cum[k90 - 1] * 1.9), UP, buff=0.08))
    m.add(rail_board(1, VGroup(bars, curve, line90, mark), "kept"))


def f8(s, m):
    """ch6_s02 (L3): a rolled sheet (seen at an angle) and its PCA shadow, where the layers mix."""
    Xr, tcol = pd.swiss_roll()  # noqa: F821
    Q = pd.pca(Xr)  # noqa: F821
    for box, tag in ((LEFT_L3, "rolled sheet"), (RIGHT_L3, "flat shadow")):
        m.add(board(box, tag))
    from scipy.spatial.transform import Rotation
    Rm = Rotation.from_euler("zx", [-62, 24], degrees=True).as_matrix()
    v = (Xr - Xr.mean(0)) @ Rm.T
    order = np.argsort(v[:, 2])  # noqa: F821
    def place(xy, box):
        k = min((box[2] - box[0] - 0.8) / np.ptp(xy[:, 0]), (box[3] - box[1] - 0.9) / np.ptp(xy[:, 1]))  # noqa: F821
        c = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - 0.1])  # noqa: F821
        return c + k * (xy - (xy.max(0) + xy.min(0)) / 2)
    L = place(v[order, :2], LEFT_L3)
    Rr = place(Q.Z[:, :2], RIGHT_L3)
    cols = (C.pc2, C.data, C.pc1)
    s.add(PointsLayer(lambda t: L, values=lambda t: tcol[order], cmap="ramp", colors=cols, size=5.0, glow=0.15,  # noqa: F821
                      z=1, additive=False))
    s.add(PointsLayer(lambda t: Rr, values=lambda t: tcol, cmap="ramp", colors=cols, size=5.0, glow=0.15, z=1,  # noqa: F821
                      additive=False))
    tags = VGroup(*[sans(t, 26, C.muted) for t in ("kernel PCA", "t-SNE", "UMAP")]).arrange(RIGHT, buff=0.5)  # noqa: F821
    m.add(tags.move_to(P3(0, Y0 - 0.2)))
    # two points far apart along the sheet that land side by side
    a = int(np.argmin(np.abs(tcol - 0.15) + 0.02 * np.abs(Xr[:, 1] - 5)))  # noqa: F821
    d = np.linalg.norm(Q.Z[:, :2] - Q.Z[a, :2], axis=1) + 50 * (np.abs(tcol - tcol[a]) < 0.45)  # noqa: F821
    b = int(np.argmin(d))
    inv = np.empty_like(order)
    inv[order] = np.arange(len(order))  # noqa: F821
    for i in (a, b):
        m.add(Circle(radius=0.12, stroke_color=C.text, stroke_width=2.2).move_to(P3(*Rr[i])))  # noqa: F821
        m.add(Circle(radius=0.12, stroke_color=C.text, stroke_width=2.2).move_to(P3(*L[inv[i]])))  # noqa: F821


def f9(s, m):
    """Reference sheet: layouts L1-L4 (rail geometry), a chapter card, the type scale, the palette."""
    sc = 0.235
    def mini(box, ox, oy):
        x0, y0, x1, y1 = box
        return Rectangle(width=(x1 - x0) * sc, height=(y1 - y0) * sc, stroke_color=C.roles["frame"], stroke_width=1.4,  # noqa: F821
                         fill_opacity=0).move_to(P3(ox + (x0 + x1) / 2 * sc, oy + (y0 + y1) / 2 * sc))
    frame_box = (-XW, -YH, XW, YH)
    specs = {
        "L1 stage": [(X0, Y0, X1, Y1)],
        "L2 stage + rail": [STAGE_L2, slot(0), slot(1), slot(2)],
        "L3 split": [LEFT_L3, RIGHT_L3],
        "L4 grid": [(X0, 0.1, -0.125, Y1), (0.125, 0.1, X1, Y1), (X0, Y0, -0.125, -0.1), (0.125, Y0, X1, -0.1)],
    }
    for n, (name, boxes) in enumerate(specs.items()):
        ox, oy = -5.15 + (n % 2) * 3.75, 1.95 - (n // 2) * 2.35
        f = Rectangle(width=2 * XW * sc, height=2 * YH * sc, stroke_color=C.muted, stroke_width=1,  # noqa: F821
                      fill_color=C.roles["bg2"] if hasattr(C, "roles") and "bg2" in C.roles else "#161616",
                      fill_opacity=1).move_to(P3(ox, oy))
        m.add(f, *[mini(b, ox, oy) for b in boxes])
        m.add(sans(name, 22, C.muted).next_to(f, UP, buff=0.08))
    _ = frame_box
    # chapter card
    cx, cy = 3.45, 1.35
    card = VGroup(sans("chapter two", 26, C.muted), caps("The Best Direction", 50),  # noqa: F821
                  Line(LEFT * 1.4, RIGHT * 1.4, stroke_color=C.pc1, stroke_width=3)).arrange(DOWN, buff=0.22)  # noqa: F821
    cf = Rectangle(width=6.0, height=3.4, stroke_color=C.muted, stroke_width=1).move_to(P3(cx, cy))  # noqa: F821
    card.move_to(P3(cx, cy + 0.15))
    strip = dim(dial_curve(pd.people2(), (0, 0), 0.25).move_to(P3(cx, cy - 1.35)), 0.5)  # noqa: F821
    m.add(cf, card, strip, sans("carry-over strip", 18, C.muted).next_to(strip, RIGHT, buff=0.2))
    # type scale
    ty = VGroup(  # noqa: F821
        VGroup(tex(r"u^\top C\,u", 48), sans("maths: CM roman 44-56", 22, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
        VGroup(sans("arm span", 30), sans("key words: CM sans 24-30", 22, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
        VGroup(caps("Karl Pearson · 1901", 34), sans("names, dates, cards: small caps", 22, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(P3(-3.35, -2.95))
    m.add(ty)
    roles = ("data", "mean", "probe", "pc1", "pc2", "pc3", "residual", "spread")
    sw = VGroup(*[VGroup(Square(side_length=0.34, stroke_width=0, fill_color=getattr(C, r), fill_opacity=1),  # noqa: F821
                         sans(r, 20, C.muted)).arrange(DOWN, buff=0.08) for r in roles]).arrange(RIGHT, buff=0.22)
    dg = VGroup(*[VGroup(Square(side_length=0.26, stroke_width=0, fill_color=getattr(C, f"d{d}"), fill_opacity=1),  # noqa: F821
                         tex(str(d), 24, getattr(C, f"d{d}"))).arrange(DOWN, buff=0.06) for d in range(10)]).arrange(RIGHT, buff=0.14)
    pal = VGroup(sw, dg).arrange(DOWN, buff=0.25).move_to(P3(3.45, -2.6))  # noqa: F821
    m.add(pal)


FRAMES = {1: f1, 2: f2, 3: f3, 4: f4, 5: f5, 6: f6, 7: f7, 8: f8, 9: f9}


# ------------------------------------------------------------------------------------------------- main
def render(n: int) -> Path:
    from PIL import Image

    _import_aion()
    if n == 1:
        shadow_render()                                   # VTK before aion's GL context exists

    @scene(0.0, 10.0)  # noqa: F821
    def style_frame(s):
        s.solid(C.bg, z=-200)  # noqa: F821
        FRAMES[n](s, s.manim())

    sd = scene_mod.REGISTRY[-1]  # noqa: F821
    OUT.mkdir(parents=True, exist_ok=True)
    path = (OUT / f"{NAMES_OUT[n]}.png").resolve()
    Image.fromarray(sd.comp((W, H), FPS).frame(T_STILL, round(T_STILL * FPS))).save(path)
    print(path.relative_to(REPO))
    return path


if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(FRAMES)
    if len(want) == 1:
        render(want[0])
    else:
        for k in want:                                    # one process per frame keeps memory low
            subprocess.run([sys.executable, __file__, str(k)], check=True, cwd=REPO)
