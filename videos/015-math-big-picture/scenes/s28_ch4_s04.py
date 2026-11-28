"""ch4_s04 · Corners, edges, faces (worked example).

On 'simpler' the header χ = V − E + F writes on the right. A 12-sided loop draws on the left; on 'corners' its twelve
corners pop while V ticks up to 12, on 'edges' its edges flash while E ticks to 12, on 'faces' F reads 0. On 'zero'
χ lands: 0. Each shape then shrinks into a small icon at the head of its row. 'Fill' fills the loop: 12 − 12 + 1 = 1.
A wireframe cube: 8 − 12 + 6 = 2. 'What about the donut?' The torus comes in as a 16 × 8 grid of squares; the three
counts land (128, 256, 128) and χ waits as a question mark until 'Zero again'. On 'different pieces' a cube comes
back with one face cut into four (13 − 20 + 9 = 2); it is stretched about, and the χ column holds.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, TOR_R, TOR_r, lin, surface_curve, tex, torus_xyz, window

OC = P3(-3.4, -0.2)                                          # where each shape is shown
TS = 1.7                                                     # torus: world units per object unit
TILT = -0.85
COLS = {"chi": 1.25, "=": 1.95, "V": 2.75, "-": 3.55, "E": 4.35, "+": 5.15, "F": 5.9}
HEAD_Y = 2.85
ROW_Y = (1.75, 0.85, -0.05, -0.95, -1.85)
ICON_X = 0.3


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def cube_xy(p):
    """A cube vertex (±1, ±1, ±1) seen turned 35° and tipped 24°: world offset from OC."""
    a, b = math.radians(35), math.radians(24)
    x, y, z = p
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
    return np.array([x, y, 0.0]) * 1.05, z


@scene(T.ch4_s04, T.ch4_s05)
def ch4_s04(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_si, t_lo, t_fi = float(T.ch4_s04_simpler), float(T.ch4_s04_loop), float(T.ch4_s04_fill)
    t_cu, t_do, t_ze, t_dp = (float(T.ch4_s04_cube), float(T.ch4_s04_donut), float(T.ch4_s04_zero_again),
                              float(T.ch4_s04_different_pieces))
    t_corn, t_edge, t_face = t_si + 2.82, t_si + 3.42, t_si + 4.42          # 'corners,' 'edges' 'faces,'
    t_add, t_away = t_si + 5.1, t_si + 6.8                                 # 'add up …' 'take away the edges'
    VC, EC, FC = C.circle, C.space, C.space
    out_t = t1 - 0.8

    # the header
    head = VGroup(*(tex(sym, 60, col).move_to(P3(COLS[k], HEAD_Y))
                    for k, sym, col in (("chi", r"\chi", C.text), ("=", "=", C.text), ("V", "V", VC),
                                        ("-", "-", C.text), ("E", "E", EC), ("+", "+", C.text), ("F", "F", FC))))
    rule = Line(P3(COLS["chi"] - 0.5, HEAD_Y - 0.5), P3(COLS["F"] + 0.5, HEAD_Y - 0.5), stroke_color=C.map_off,
                stroke_width=1.6)
    m.play(Write(head), at=t_si, dur=1.0)
    m.play(Create(rule), at=t_si + 0.6, dur=0.6)
    hV, hE, hF = head[2], head[4], head[6]

    table = VGroup()                                          # every cell, for the exit

    def cell(val, col, row, color, size=48, keep=True):
        c_ = tex(str(val), size, color).move_to(P3(COLS[col], ROW_Y[row]))
        if keep:
            table.add(c_)
        return c_

    def row_ops(row):
        g = VGroup(*(tex(sym, 44, C.muted).move_to(P3(COLS[k], ROW_Y[row])) for k, sym in
                     (("=", "="), ("-", "-"), ("+", "+"))))
        table.add(g)
        return g

    def tick(layer, col, row, n, a, b, color):
        """Count 1 … n in a cell between a and b, then hold n."""
        def f(t):
            k = max(1, min(n, int(1 + (n - 1) * (t - a) / (b - a))))
            return cell(k, col, row, color, keep=False)
        layer.redraw(window(f, a, b), during=(a, b + 0.05))
        layer.add(cell(n, col, row, color), at=b)

    def pulse(mob, at):
        m.play(Indicate(mob, color=mob.get_color(), scale_factor=1.25), at=at, dur=0.6)

    # the loop: twelve corners, twelve edges, no face
    gon = [OC + 1.8 * P3(math.cos(math.pi / 2 + 2 * math.pi * k / 12), math.sin(math.pi / 2 + 2 * math.pi * k / 12))
           for k in range(12)]
    poly = Polygon(*gon, stroke_color=EC, stroke_width=5, fill_color=FC, fill_opacity=0.0)
    dots = VGroup(*(Dot(p, radius=0.09, color=VC) for p in gon))
    m.play(Create(poly), at=t_si + 1.6, dur=0.9, ease="easy_ease")
    top.play(LaggedStart(*(GrowFromCenter(d) for d in dots), lag_ratio=0.25), at=t_corn, dur=0.6)
    pulse(hV, t_corn)
    tick(m, "V", 0, 12, t_corn, t_corn + 0.6, VC)
    m.play(poly.animate.set_stroke(width=10), at=t_edge, dur=0.3)
    m.play(poly.animate.set_stroke(width=5), at=t_edge + 0.45, dur=0.4)
    pulse(hE, t_edge)
    tick(m, "E", 0, 12, t_edge, t_edge + 0.7, EC)
    pulse(hF, t_face)
    m.add(ops0 := row_ops(0), at=t_face)
    m.play(FadeIn(cell(0, "F", 0, FC)), at=t_face, dur=0.4)
    pulse(hV, t_add + 0.3)
    pulse(hF, t_add + 1.1)
    pulse(hE, t_away)
    m.play(FadeIn(cell(0, "chi", 0, C.text), shift=0.1 * DOWN), at=t_lo + 0.7, dur=0.5)

    # icons at the head of each row
    def icon(mob, row):
        return mob.copy().scale(0.5 / max(mob.height, mob.width)).move_to(P3(ICON_X, ROW_Y[row]))

    # 'Fill': the face makes it one
    loop_icon = VGroup(poly, dots).copy()
    m.add(loop_icon, at=t_fi - 0.4)
    m.play(Transform(loop_icon, icon(VGroup(poly, dots), 0)), at=t_fi - 0.4, dur=0.6, ease="easy_ease")
    m.play(poly.animate.set_fill(opacity=0.18), at=t_fi + 0.4, dur=0.8)
    m.add(row_ops(1), at=t_fi + 0.4)
    m.play(LaggedStart(FadeIn(cell(12, "V", 1, VC)), FadeIn(cell(12, "E", 1, EC)), lag_ratio=0.4),
           at=t_fi + 0.5, dur=0.6)
    m.play(FadeIn(cell(1, "F", 1, FC), scale=1.3), at=t_fi + 1.55, dur=0.4)       # 'face'
    m.play(FadeIn(cell(1, "chi", 1, C.text), shift=0.1 * DOWN), at=t_fi + 2.2, dur=0.5)   # 'one'

    # the cube: 8 − 12 + 6
    m.play(Transform(poly, icon(poly.copy().set_fill(opacity=0.18), 1)), at=t_cu - 0.5, dur=0.6, ease="easy_ease")
    top.play(FadeOut(dots), at=t_cu - 0.5, dur=0.3)
    verts = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    proj = {v: cube_xy(v) for v in verts}
    edges = [(a, b) for a in verts for b in verts if a < b and sum(i != j for i, j in zip(a, b)) == 1]

    def cube(c=OC, k=1.0, split=False):
        g_f, g_e, g_v = VGroup(), VGroup(), VGroup()
        faces = []
        for ax in range(3):
            for sgn in (-1, 1):
                fv = [v for v in verts if v[ax] == sgn]
                n = [0, 0, 0]
                n[ax] = sgn
                _, nz = cube_xy(n)
                q = sorted(fv, key=lambda v: math.atan2(*(np.array(v, float)[[i for i in range(3) if i != ax]])))
                faces.append((nz, q, ax, sgn))
        for nz, q, ax, sgn in faces:
            if nz > 0:
                g_f.add(Polygon(*(c + k * proj[v][0] for v in q), stroke_width=0, fill_color=FC, fill_opacity=0.12))
        for a, b in edges:
            back = proj[a][1] < -0.2 and proj[b][1] < -0.2 or (proj[a][1] + proj[b][1]) / 2 < -0.45
            g_e.add(Line(c + k * proj[a][0], c + k * proj[b][0], stroke_color=EC, stroke_width=4,
                         stroke_opacity=0.35 if back else 1.0))
        for v in verts:
            g_v.add(Dot(c + k * proj[v][0], radius=0.08 * k ** 0.5, color=VC,
                        fill_opacity=0.45 if proj[v][1] < -0.5 else 1.0))
        return VGroup(g_f, g_e, g_v), faces

    cb, faces = cube()
    m.play(FadeIn(cb[0]), Create(cb[1]), at=t_cu - 0.15, dur=0.8, ease="easy_ease")
    top.play(LaggedStart(*(GrowFromCenter(d) for d in cb[2]), lag_ratio=0.12), at=t_cu + 0.2, dur=0.6)
    m.add(row_ops(2), at=t_cu + 0.2)
    m.play(LaggedStart(FadeIn(cell(8, "V", 2, VC)), FadeIn(cell(12, "E", 2, EC)), FadeIn(cell(6, "F", 2, FC)),
                       lag_ratio=0.35), at=t_cu + 0.2, dur=0.7)
    m.play(FadeIn(cell(2, "chi", 2, C.text), shift=0.1 * DOWN), at=t_cu + 0.65, dur=0.5)    # 'two'

    # 'donut?': a torus of 16 × 8 squares; predict, then zero again
    m.play(Transform(VGroup(cb[0], cb[1]), icon(VGroup(cb[0], cb[1]), 2)), at=t_do - 0.9, dur=0.6, ease="easy_ease")
    top.play(FadeOut(cb[2]), at=t_do - 0.9, dur=0.3)
    s.shader("solid.frag", z=1, u_c=(float(OC[0]), float(OC[1])), u_size=TS, u_tilt=TILT, u_spin=0.0, u_morph=1.0,
             u_amt=fade(t_do + 0.1, to=0.55, dur=0.6, out=t_dp - 0.9, out_dur=0.5), u_R=TOR_R, u_r=TOR_r,
             u_col=lin(EC))
    mesh = VGroup()
    vv = np.linspace(0, 2 * math.pi, 97)
    for k in range(16):
        u = 2 * math.pi * k / 16
        q = torus_xyz(u, vv)
        nrm = np.stack([np.cos(vv) * math.cos(u), np.cos(vv) * math.sin(u), np.sin(vv)], -1)
        mesh.add(surface_curve(q, nrm, OC, TS, TILT, 0.0, EC, width=2.4))
    uu = np.linspace(0, 2 * math.pi, 161)
    for j in range(8):
        v = 2 * math.pi * j / 8 + math.pi / 8
        q = torus_xyz(uu, v)
        nrm = np.stack([math.cos(v) * np.cos(uu), math.cos(v) * np.sin(uu), np.full_like(uu, math.sin(v))], -1)
        mesh.add(surface_curve(q, nrm, OC, TS, TILT, 0.0, EC, width=2.4))
    top.play(LaggedStart(*(Create(x_) for x_ in mesh), lag_ratio=0.04), at=t_do + 0.1, dur=1.2)
    m.add(row_ops(3), at=t_do + 0.6)
    m.play(LaggedStart(FadeIn(cell(128, "V", 3, VC)), FadeIn(cell(256, "E", 3, EC)), FadeIn(cell(128, "F", 3, FC)),
                       lag_ratio=0.35), at=t_do + 0.6, dur=0.8)
    q_mark = cell("?", "chi", 3, C.muted, keep=False)
    m.play(FadeIn(q_mark), at=t_do + 1.0, dur=0.4)
    zero = cell(0, "chi", 3, C.text)
    m.play(FadeOut(q_mark), FadeIn(zero, shift=0.1 * DOWN), at=t_ze, dur=0.5)

    # 'different pieces': a cube with one face cut into four; stretched about, χ holds
    t_c2 = t_dp - 1.4
    top.play(Transform(mesh, icon(mesh, 3).set_stroke(width=1.2)), at=t_c2, dur=0.6, ease="easy_ease")
    cb2, _ = cube()
    nz, q, ax, sgn = max(faces, key=lambda f: f[0])
    corners = [OC + proj[v][0] for v in q]
    mids = [(corners[i] + corners[(i + 1) % 4]) / 2 for i in range(4)]
    ctr = sum(corners) / 4
    cut = VGroup(*(Line(ctr, p, stroke_color=EC, stroke_width=4) for p in mids))
    new_v = VGroup(*(Dot(p, radius=0.08, color=VC) for p in mids + [ctr]))
    m.play(FadeIn(VGroup(cb2[0], cb2[1])), at=t_c2 + 0.5, dur=0.6)
    top.play(FadeIn(cb2[2]), at=t_c2 + 0.5, dur=0.6)
    m.play(LaggedStart(*(Create(x_) for x_ in cut), lag_ratio=0.2), at=t_dp, dur=0.6)
    top.play(LaggedStart(*(GrowFromCenter(d) for d in new_v), lag_ratio=0.15), at=t_dp + 0.2, dur=0.6)
    m.add(row_ops(4), at=t_dp + 0.4)
    m.play(LaggedStart(FadeIn(cell(13, "V", 4, VC)), FadeIn(cell(20, "E", 4, EC)), FadeIn(cell(9, "F", 4, FC)),
                       lag_ratio=0.35), at=t_dp + 0.4, dur=0.8)
    two = cell(2, "chi", 4, C.text)
    m.play(FadeIn(two, shift=0.1 * DOWN), at=t_dp + 1.1, dur=0.5)
    whole_m, whole_t = VGroup(cb2[0], cb2[1], cut), VGroup(cb2[2], new_v)
    mtx = np.array([[1.3, 0.25], [0.0, 0.8]])
    for lay, g in ((m, whole_m), (top, whole_t)):
        lay.play(ApplyMatrix(mtx, g, about_point=OC), at=t_dp + 1.3, dur=0.9, ease="easy_ease")
        lay.play(ApplyMatrix(np.linalg.inv(mtx), g, about_point=OC), at=t_dp + 2.4, dur=0.9, ease="easy_ease")

    # 'the count never changes': the χ column
    chis = VGroup(*(cell(v, "chi", r, C.text, keep=False) for r, v in enumerate((0, 1, 2, 0, 2))))
    box = SurroundingRectangle(chis, buff=0.22, color=C.text, stroke_width=2.2, corner_radius=0.1)
    m.play(Create(box), at=t_dp + 3.0, dur=0.7)

    # out
    m.play(FadeOut(VGroup(head, rule, table, box, loop_icon, poly, cb[0], cb[1], whole_m)), at=out_t, dur=0.6)
    top.play(FadeOut(VGroup(mesh, whole_t)), at=out_t, dur=0.6)
