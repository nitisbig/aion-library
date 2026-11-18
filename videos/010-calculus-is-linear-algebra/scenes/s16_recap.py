"""Outro (cont.): the picture holds. One line per chapter, each lit as it is spoken: +C is the null space, D on
(cos, sin) is a quarter turn, e^x is an eigenvector, the string's first mode, and the thesis:
calculus = linear algebra + lim, with the eight samples blurring into a curve on "plus a limit". Right third left
empty for the end screen."""
from aion import *

from beats import T
from shots import D_TRIG, Mat, backdrop, finish, header_row, plot, pt, samples, tex

LX = -5.45                                               # the recap lines' left edge (right third stays empty)
YS = [2.9, 1.75, 0.6, -0.55]


@scene(T.cut_recap, T.end)
def s16_recap(s):
    backdrop(s)
    m = s.manim(z=1)

    rows = [
        tex(r"+C", r"=", r"\text{null}(D)", size=48, colors={0: C.null, 2: C.op}),
        VGroup(tex(r"D", r"\big|_{\cos,\,\sin}", r"=", size=48, colors={0: C.op}),
               Mat(D_TRIG.astype(int), size=34, h_buff=0.6, v_buff=0.5)).arrange(RIGHT, buff=0.2),
        tex(r"D", r"\,e^x", r"=", r"1", r"\cdot", r"e^x", size=48, colors={0: C.op, 1: C.eigen, 3: C.eigen, 5: C.eigen}),
        tex(r"D^2", r"v", r"=", r"\lambda", r"v", size=48, colors={0: C.op, 1: C.eigen, 3: C.eigen, 4: C.eigen}),
    ]
    for r, y in zip(rows, YS):
        r.move_to([LX + r.width / 2, y, 0])
    # the string's first mode beside its line
    mode = plot(lambda x: np.sin(np.pi * x), 0, 1, (rows[3].get_right()[0] + 0.5, YS[3] - 0.2), 2.2, 0.45, C.eigen)
    times = [T.r_plus_c - 0.2, T.r_rotation - 0.1, T.r_eigen, T.r_string]
    # the seven chapter badges arrive; four of them fly down beside the lines they stand for
    row = header_row(0)
    m.play(LaggedStart(*[FadeIn(b, shift=0.1 * DOWN) for b in row], lag_ratio=0.07), at=T.cut_recap + 0.1, dur=0.9)
    m.play(FadeOut(VGroup(row[0], row[1], row[6]), shift=0.1 * UP), at=T.r_plus_c - 0.7, dur=0.5)
    for j, (r, tk) in enumerate(zip(rows, times)):
        b = row[j + 2]
        m.play(b.animate.scale(0.85).move_to([LX - 0.6, YS[j], 0]), at=tk - 0.55, dur=0.8, ease="easy_ease")
        m.play(FadeIn(r, shift=0.15 * RIGHT), at=tk, dur=0.6)
    m.play(Create(mode), at=T.r_string + 0.8, dur=0.8)

    # ── calculus = linear algebra + lim ──
    th = tex(r"\text{calculus}", r"=", r"\text{linear algebra}", r"+", r"\lim", size=60,
             colors={0: C.fn, 2: C.op, 4: C.shift})
    th.move_to([LX + th.width / 2, -2.2, 0])
    m.play(FadeIn(th[0:3], shift=0.1 * UP), at=T.r_thesis, dur=0.8)
    # eight samples under it blur into a curve on "plus a limit"
    GO, GUX, GUY = (LX + 0.1, -3.35), 1.0, 0.35
    d8 = VGroup(*[Dot(pt(GO, 1, (GUX * x, GUY * np.sin(x))), radius=0.05, color=C.fn) for x in samples(8)])
    cv = plot(np.sin, 0, 2 * np.pi, GO, GUX, GUY, C.fn, width=C.stroke - 0.5)
    m.play(FadeIn(th[3:5], shift=0.1 * UP), FadeIn(d8), at=T.r_limit - 0.7, dur=0.6)
    m.play(FadeOut(d8), Create(cv), at=T.r_limit - 0.1, dur=1.0)
    m.play(Indicate(th[4], color=C.shift, scale_factor=1.2), at=T.r_limit + 0.6, dur=0.8)
    finish(s)
