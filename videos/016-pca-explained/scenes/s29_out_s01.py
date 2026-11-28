"""out_s01 · The boards (L1, six boards).

The six results of the video come back side by side, dim, and each lights as it is named: the centred cloud
('cloud of points'), the dial of shadow spreads ('spreads the shadows'), the matrix C ('symmetric matrix'), the
cloud with its eigenvectors ('eigenvectors'), the scree ('how much each one keeps'), and the 3 rebuilt from 20 of
its 64 numbers ('handful'). A gold frame flashes on the board being named. Everything clears for the shadow.
"""
import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (DIGIT_I, GAP, P3, PHI1, X0, X1, Y0, Y1, board, c_matrix, dial, dots, eq_centre, fit_into,
                 grey_tiles, mean_ring, people_v, scree, sans, tex, udir)


def box6(i):
    w, h = (X1 - X0 - 2 * GAP) / 3, (Y1 - Y0 - GAP) / 2
    c, r = i % 3, i // 3
    x0, y1 = X0 + c * (w + GAP), Y1 - r * (h + GAP)
    return (x0, y1 - h, x0 + w, y1)


@scene(T.out_s01, T.out_s02)
def out_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    beats = [float(T.out_s01_cloud_of_points), float(T.out_s01_spreads_the_shadows), float(T.out_s01_symmetric_matrix),
             float(T.out_s01_eigenvectors), float(T.out_s01_how_much_each_one_ke), float(T.out_s01_handful)]
    P, V = people_v()
    Xc = P.Xc
    D = pd.digits_pca()
    X, _ = pd.digits()
    k = 0.045

    def cloud(extra=()):
        g = VGroup(dots([P3(*(k * q)) for q in Xc], C.data, r=0.04), mean_ring(P3(0, 0), 0.07), *extra)
        return g

    def axes():
        return [Line(P3(*(-1.5 * udir(PHI1))), P3(*(1.5 * udir(PHI1))), stroke_color=C.pc1, stroke_width=4),
                Line(P3(*(-0.6 * udir(PHI1 + 90))), P3(*(0.6 * udir(PHI1 + 90))), stroke_color=C.pc2, stroke_width=4)]

    cells, fr = grey_tiles(X[DIGIT_I], 1.6)
    rc, rfr = grey_tiles(np.clip(D.reconstruct(X[DIGIT_I], 20), 0, 16), 1.6)
    contents = [
        ("cloud", VGroup(cloud(), eq_centre(34)).arrange(DOWN, buff=0.3)),
        ("shadows", dial((0, 0), 1.15, PHI1, (0, 180), tip_col=C.pc1)),
        ("matrix", c_matrix(44)),
        ("eigenvectors", VGroup(cloud(axes()), Eqn(r"C\,v = \lambda\,v", colors={r"C": C.spread, r"\lambda": C.spread},
                                                    size=36)).arrange(DOWN, buff=0.3)),
        ("keep", scree((0, 0, 3.4, 2.0))),
        ("compress", VGroup(VGroup(cells, fr), Eqn(r"64 \to 20", size=36), VGroup(rc, rfr)).arrange(RIGHT, buff=0.3)),
    ]
    base = keys((t0, 0.0), (t0 + 0.3, 0.0), (t0 + 1.2, 0.35))
    end = keys((t0, 1.0), (t1 - 0.9, 1.0), (t1 - 0.1, 0.0))
    for i, (tag, mob) in enumerate(contents):
        b = box6(i)
        at = beats[i]
        lit = keys((t0, 0.0), (at - 0.3, 0.0), (at + 0.3, 0.65), (beats[i + 1] - 0.3 if i < 5 else t1, 0.65),
                   (beats[i + 1] + 0.3 if i < 5 else t1 + 1, 0.15))
        lay = s.manim(z=1, opacity=(base + lit) * end)
        lay.add(board(b, tag), fit_into(mob, b, pad=0.3, top=0.45))
        hl = s.manim(z=2, opacity=end)
        r = Rectangle(width=b[2] - b[0], height=b[3] - b[1], stroke_color=C.pc1, stroke_width=3)
        r.move_to(P3((b[0] + b[2]) / 2, (b[1] + b[3]) / 2))
        hl.play(Create(r), at=at - 0.1, dur=0.5)
        hl.play(FadeOut(r), at=(beats[i + 1] - 0.4) if i < 5 else t1 - 1.0, dur=0.4)
