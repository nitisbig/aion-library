"""s17: one function holds everything. Each partial derivative of the Lagrangian returns one of the three equations."""
from aion import *

from beats import T
from classic import *


@scene(T.cut_ch4, T.cut_saddle)
def s17_lagrangian(s):
    backdrop(s)
    progress(s, 4, "The Lagrangian")
    m = s.manim(z=0)
    L = tex(r"\mathcal{L}", "(x,y,", r"\lambda", ")", "=", "f", "-", r"\lambda", "(", "g", "-", "c", ")", size=92,
            colors={0: C.lag, 2: C.lam, 5: C.obj, 7: C.lam, 9: C.con, 11: C.con}).move_to([0, 2.15, 0])
    m.play(Write(L[:5]), at=T.packed + 0.6, dur=0.9)
    m.play(FadeIn(L[5]), at=T.subtract - 0.8, dur=0.4)
    m.play(FadeIn(L[6:8]), at=T.subtract, dur=0.5)
    m.play(FadeIn(L[8:]), at=T.subtract + 1.3, dur=0.6)
    xs = [-4.5, 0.0, 4.5]
    tops = [tex(r"\partial_x", r"\mathcal{L}", "=0", size=58, colors={1: C.lag}), tex(r"\partial_y", r"\mathcal{L}", "=0", size=58, colors={1: C.lag}), tex(r"\partial_\lambda", r"\mathcal{L}", "=0", size=58, colors={0: C.lam, 1: C.lag})]
    ends = [tex("f_x", "=", r"\lambda", "g_x", size=64, colors={0: C.obj, 2: C.lam, 3: C.con}), tex("f_y", "=", r"\lambda", "g_y", size=64, colors={0: C.obj, 2: C.lam, 3: C.con}), tex("g", "=", "c", size=64, colors={0: C.con, 2: C.con})]
    for i, x in enumerate(xs):
        tops[i].move_to([x, 0.45, 0])
        ends[i].move_to([x, -1.2, 0])
    arrows = [arrow([x, 0.05, 0], [x, -0.72, 0], C.muted, width=3.5, tip=0.2) for x in xs]
    for i in (0, 1):
        m.play(FadeIn(tops[i], shift=0.1 * DOWN), at=T.d_xy + 0.3 + 0.55 * i, dur=0.5)
        m.play(GrowArrow(arrows[i]), FadeIn(ends[i], shift=0.1 * DOWN), at=T.arrow_eqs + 0.4 * i, dur=0.5)
    m.play(FadeIn(tops[2], shift=0.1 * DOWN), at=T.d_lam + 0.5, dur=0.5)
    m.play(GrowArrow(arrows[2]), FadeIn(ends[2], shift=0.1 * DOWN), at=T.out_con, dur=0.5)
    flat = tex(r"\nabla", r"\mathcal{L}", "=", "0", size=80, colors={1: C.lag}).move_to([-0.8, -2.85, 0])
    m.play(FadeIn(flat, shift=0.1 * UP), at=T.restricted + 1.2, dur=0.7)
    m.play(FadeIn(lab("flat ground", 32, C.tang).next_to(flat, RIGHT, buff=0.5)), at=T.returned, dur=0.5)
    curtain(s)
