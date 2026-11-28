"""in_s05 · Pearson, Hotelling, and the road map.

L3: the forty people. Left, Pearson 1901: the line closest to the cloud (its perpendicular gaps in pink). Right,
Hotelling 1933: the direction of most spread (an arrow, the points' shadows on it). On 'same answer' the two
slide together and coincide exactly (it is the same line, PC1 from pcadata), and it turns gold.
Then the six chapters as tiles along a gentle arc, each a small preview, lit on its words. On 'map of digits'
the tiles step down and the digit map returns above them (loop L1 kept open).
"""
import numpy as np
from aion import *

from beats import T
from kit import (LEFT_L3, RIGHT_L3, P3, board, box_c, caps, dim, dots, glow_layer, sans, smoothstep, tex)

SC = 0.07                                   # world units per cm


@scene(T.in_s05, T.ch1_s01)
def in_s05(s):
    import pcadata as pd
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_kp, t_hh, t_sa = float(T.in_s05_karl_pearson), float(T.in_s05_harold_hotelling), float(T.in_s05_same_answer)
    t_tiles = [float(T.in_s05_cloud_of_points), float(T.in_s05_best_direction), float(T.in_s05_one_matrix),
               float(T.in_s05_eigenvectors), float(T.in_s05_cutting_the_dimensio), float(T.in_s05_breaks)]
    t_map = float(T.in_s05_map_of_digits)
    t_pc = t_hh + 5.1                                  # 'principal components'
    t_clear = t_tiles[0] - 1.8

    P = pd.people2()
    Xc, u = P.Xc, P.V[:, 0]
    nrm = np.array([-u[1], u[0]])
    c0 = P3(0, -0.35)
    cl, cr = P3(box_c(LEFT_L3)[0], -0.35), P3(box_c(RIGHT_L3)[0], -0.35)

    def at(c, v):
        return c + P3(*(SC * np.asarray(v)))

    def mover(g, path):
        """Drive group g so its anchor (a point it carries, at the group's build centre) follows path(t)."""
        anc = Dot(g.get_center(), radius=0.001, fill_opacity=0.0)
        g.add(anc)
        return lambda mob, t: mob.shift(path(t) - anc.get_center())

    def glide(a0, a1, ta, tb, ease=smoothstep):
        def f(t):
            return a0 + (a1 - a0) * float(ease((t - ta) / (tb - ta)))
        return f

    clear = keys((t0, 1.0), (t_clear - 0.15, 1.0), (t_clear + 0.45, 0.0))
    m = s.manim(z=1, opacity=clear)
    gl_ = s.manim(z=1.1, opacity=clear)
    gr_ = s.manim(z=1.2, opacity=clear)

    # ---- Pearson: the closest line (built centred; glides left, then back to centre on 'same answer')
    cloud = dots([at(c0, p) for p in Xc], C.data, r=0.05)
    gl_.play(FadeIn(cloud, lag_ratio=0.03), at=t0 + 0.8, dur=1.4)
    bl, br = board(LEFT_L3), board(RIGHT_L3)
    nameL = VGroup(caps("Karl Pearson", 34), sans("1901", 26, C.muted)).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
    nameL.move_to(P3(box_c(LEFT_L3)[0], 2.45))
    m.play(FadeIn(bl), at=t_kp - 0.5, dur=0.6)
    m.play(FadeIn(nameL, shift=0.1 * UP), at=t_kp, dur=0.6)
    lineL = Line(at(c0, -34 * u), at(c0, 34 * u), stroke_color=C.probe, stroke_width=3)
    proj = (Xc @ u)[:, None] * u
    gaps = VGroup(*[Line(at(c0, a), at(c0, b), stroke_color=C.residual, stroke_width=2.2) for a, b in zip(Xc, proj)])
    gL = VGroup(cloud, lineL, gaps)
    pathL = lambda t: glide(c0, cl, t_kp - 0.45, t_kp + 0.7)(t) if t < t_sa - 0.5 else glide(cl, c0, t_sa - 0.15, t_sa + 1.05)(t)
    gl_.drive(gL, mover(gL, pathL), during=(t_kp - 0.5, t_sa + 1.1))
    gl_.play(Create(lineL), at=t_kp + 1.6, dur=0.9)
    gl_.play(LaggedStart(*[Create(g) for g in gaps], lag_ratio=0.05), at=t_kp + 2.6, dur=1.6)

    # ---- Hotelling: the direction of most spread (built on the right; glides to centre)
    cloudR = dots([at(cr, p) for p in Xc], C.data, r=0.05)
    nameR = VGroup(caps("Harold Hotelling", 34), sans("1933", 26, C.muted)).arrange(RIGHT, buff=0.3,
                                                                                    aligned_edge=DOWN)
    nameR.move_to(P3(box_c(RIGHT_L3)[0], 2.45))
    m.play(FadeIn(br), at=t_hh - 0.5, dur=0.6)
    gr_.play(FadeIn(cloudR), at=t_hh, dur=0.8)
    m.play(FadeIn(nameR, shift=0.1 * UP), at=t_hh, dur=0.8)
    arrow = Arrow(at(cr, -30 * u), at(cr, 30 * u), buff=0, stroke_color=C.probe, stroke_width=3, tip_length=0.18,
                  max_tip_length_to_length_ratio=0.1)
    shadows = VGroup(*[Circle(radius=0.045, stroke_color=C.data, stroke_width=2).move_to(at(cr, q)) for q in proj])
    gr_.play(GrowArrow(arrow), at=t_hh + 1.8, dur=0.9)
    gr_.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in shadows], lag_ratio=0.04), at=t_hh + 2.8, dur=1.4)
    gr_.play(cloudR.animate.set_opacity(0.4), at=t_hh + 3.2, dur=0.8)
    gR = VGroup(cloudR, arrow, shadows)
    gr_.drive(gR, mover(gR, glide(cr, c0, t_sa - 0.15, t_sa + 1.05)), during=(t_sa - 0.2, t_sa + 1.1))

    # ---- the same answer: they coincide, and the line turns gold
    m.play(FadeOut(bl), FadeOut(br), at=t_sa - 0.3, dur=0.5)
    lit = glow_layer(s, z=2, color=C.pc1, k=0.45, opacity=clear)
    gold = Line(at(c0, -34 * u), at(c0, 34 * u), stroke_color=C.pc1, stroke_width=4)
    lit.play(Create(gold), at=t_sa + 1.3, dur=0.8)

    # ---- the road map: six tiles on a gentle arc, lit on their words
    W_, H_, GAP_ = 1.9, 1.62, 0.2
    xs = (np.arange(6) - 2.5) * (W_ + GAP_)
    ys = 0.25 + 0.28 * (1 - ((np.arange(6) - 2.5) / 2.5) ** 2)
    words = ("cloud", "direction", "matrix", "eigenvectors", "cutting", "limits")
    tl = s.manim(z=1, opacity=keys((t0, 1.0), (t_map, 1.0), (t_map + 1.0, 0.55), (t1 - 0.6, 0.55), (t1 - 0.05, 0.0)))
    all_tiles = VGroup()
    k_ = 0.016
    for i in range(6):
        box = (xs[i] - W_ / 2, ys[i] - H_ / 2, xs[i] + W_ / 2, ys[i] + H_ / 2)
        cc = P3(xs[i], ys[i] - 0.12)
        g = VGroup(board(box))
        if i == 0:
            g.add(dots([cc + P3(*(k_ * p)) for p in Xc], C.data, r=0.03))
        elif i == 1:
            g.add(dots([cc + P3(*(k_ * p)) for p in Xc], C.data, r=0.03, opacity=0.6),
                  Line(cc + P3(*(-30 * k_ * u)), cc + P3(*(30 * k_ * u)), stroke_color=C.pc1, stroke_width=3))
        elif i == 2:
            g.add(tex(r"\begin{bmatrix} %d & %d \\ %d & %d \end{bmatrix}" % tuple(np.round(P.C.ravel()).astype(int)),
                      30, C.spread).move_to(cc))
        elif i == 3:
            for a in np.linspace(0, np.pi, 9, endpoint=False):
                v = np.array([np.cos(a), np.sin(a)])
                g.add(Arrow(cc, cc + P3(*(0.5 * v)), buff=0, stroke_width=2, stroke_color=C.muted, tip_length=0.08))
            for v, col in ((P.V[:, 0], C.pc1), (P.V[:, 1], C.pc2)):
                g.add(Arrow(cc, cc + P3(*(0.6 * v)), buff=0, stroke_width=3.4, stroke_color=col, tip_length=0.12))
        elif i == 4:
            D = pd.digits_pca()
            for j, sh in enumerate(D.share[:10]):
                hgt = 0.95 * sh / D.share[0]
                g.add(Rectangle(width=0.1, height=hgt, stroke_width=0, fill_color=C.spread, fill_opacity=1)
                      .move_to(cc + P3(-0.6 + 0.13 * j, -0.45 + hgt / 2)))
        else:
            th = np.linspace(1.5 * np.pi, 4.5 * np.pi, 120)
            g.add(VMobject(stroke_color=C.residual, stroke_width=2.6).set_points_smoothly(
                [cc + P3(0.028 * t * np.cos(t), 0.028 * t * np.sin(t)) for t in th]))
        dim(g, 0.3)
        tl.play(FadeIn(g, shift=0.1 * UP), at=t_tiles[0] - 0.6 + 0.12 * i, dur=0.6)
        bright = g.copy()
        dim(bright, 1 / 0.3)
        tl.play(Transform(g, bright), at=t_tiles[i], dur=0.5)
        all_tiles.add(g)
    tl.drive(all_tiles, mover(all_tiles, glide(all_tiles.get_center(), all_tiles.get_center() + P3(0, -1.95),
                                               t_map - 0.15, t_map + 0.85)), during=(t_map - 0.2, t_map + 0.9))

    # ---- 'that map of digits': it returns above the tiles
    D = pd.digits_pca()
    X, y = pd.digits()
    Z = D.Z[:, :2] * np.array([1, -1])
    box = (-2.3, -0.45, 2.3, 3.25)
    kk = min((box[2] - box[0]) / np.ptp(Z[:, 0]), (box[3] - box[1]) / np.ptp(Z[:, 1]))
    mc = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2])
    W2 = mc + kk * (Z - (Z.max(0) + Z.min(0)) / 2)
    on = keys((t_map - 0.2, 0.0), (t_map + 0.6, 1.0), (t1 - 0.6, 1.0), (t1 - 0.05, 0.0))
    num = s.manim(z=3, opacity=on)
    for d in range(10):
        pos = W2[y == d]
        s.add(PointsLayer(lambda t, pos=pos: pos, color=getattr(C, f"d{d}"), size=3.6, glow=0.25, additive=False,
                          z=2, opacity=on, start=t_map - 0.3))
        cen = np.median(pos, 0)
        num.add(VGroup(Circle(radius=0.18, stroke_color=getattr(C, f"d{d}"), stroke_width=1.8, fill_color=C.bg,
                              fill_opacity=1.0), tex(str(d), 30, getattr(C, f"d{d}"))).move_to(P3(*cen)))
