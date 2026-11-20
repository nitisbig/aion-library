"""s17: one function holds everything. Each partial derivative of the Lagrangian hands back one of the three equations, and its flat point is Fermat's flat ground again."""
from aion import *

from beats import T
from ch1 import *

ALL = np.linspace(0, TAU, 360)


@scene(T.cut_ch4, T.cut_saddle)
def s17_lagrangian(s):
    backdrop(s)
    cam = camera(
        (T.cut_ch4, (-90, 70, 0.95, 0.0, -1.6, 26, 0, 0, 0)),
        (T.restricted, (-30, 34, 0.95, 0.0, -1.9, 26, 0, 0, 0)),
        (T.returned + 0.6, (-60, 18, 1.5, 0.0, -2.9, 30, SUMMIT[0], SUMMIT[1], 2.4)),
        (T.cut_saddle, (-70, 16, 1.5, 0.0, -2.9, 30, SUMMIT[0], SUMMIT[1], 2.4)),
    )
    glow = lambda t: ramp(t, T.restricted + 1.0, T.returned)

    def frame(t):
        v = view().begin(cam(t))
        a = 0.28 + 0.5 * glow(t)
        mountain(v, 1.0, a)
        floor(v, 1.0, 0.35)
        curve(v, np.column_stack(trail(ALL)), C.con, 5.0, 0.5)
        fa = ramp(t, T.returned - 0.2, T.returned + 0.8)
        if fa > 0.01:
            zt = hill(*SUMMIT) + 0.02
            ss = np.linspace(-1.2, 1.2, 7)
            X, Y = np.meshgrid(SUMMIT[0] + ss, SUMMIT[1] + ss)
            v.mesh(X, Y, np.full_like(X, zt), C.tang, alpha=0.32 * fa, shade=False)
            for c in ss[::2]:
                v.line([[SUMMIT[0] + c, SUMMIT[1] - 1.2, zt], [SUMMIT[0] + c, SUMMIT[1] + 1.2, zt]], C.tang, 1.4, 0.8 * fa)
                v.line([[SUMMIT[0] - 1.2, SUMMIT[1] + c, zt], [SUMMIT[0] + 1.2, SUMMIT[1] + c, zt]], C.tang, 1.4, 0.8 * fa)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch4, T.cut_saddle)]))
    title(s, "Chapter 4  ·  the Lagrangian", T.cut_ch4 + 0.3, hold=3.0)
    m = s.manim(z=5, parallax=0.0)
    L = tex(r"\mathcal{L}", "(x,y,", r"\lambda", ")", "=", "f", "-", r"\lambda", "(", "g", "-", "c", ")", size=96,
            colors={0: C.lag, 2: C.lam, 5: C.obj, 7: C.lam, 9: C.con, 11: C.con}).move_to([0, 2.05, 0])
    plate = BackgroundRectangle(L, color=C.bg, fill_opacity=0.82, buff=0.18)
    m.play(FadeIn(plate), Write(L[:5]), at=T.packed + 0.6, dur=0.9)
    m.play(FadeIn(L[5], shift=0.3 * DOWN), at=T.subtract - 0.8, dur=0.5, ease=E)
    m.play(FadeIn(L[6:8], shift=0.3 * DOWN), at=T.subtract, dur=0.5, ease=E)
    m.play(FadeIn(L[8:], shift=0.3 * DOWN), at=T.subtract + 1.3, dur=0.6, ease=E)
    xs = [-4.5, 0.0, 4.5]
    tops = [tex(r"\partial_x", r"\mathcal{L}", "=0", size=58, colors={1: C.lag}), tex(r"\partial_y", r"\mathcal{L}", "=0", size=58, colors={1: C.lag}), tex(r"\partial_\lambda", r"\mathcal{L}", "=0", size=58, colors={0: C.lam, 1: C.lag})]
    ends = [tex("f_x", "=", r"\lambda", "g_x", size=64, colors={0: C.obj, 2: C.lam, 3: C.con}), tex("f_y", "=", r"\lambda", "g_y", size=64, colors={0: C.obj, 2: C.lam, 3: C.con}), tex("g", "=", "c", size=64, colors={0: C.con, 2: C.con})]
    for i, x in enumerate(xs):
        tops[i].move_to([x, 0.55, 0])
        ends[i].move_to([x, -1.05, 0])
    arrows = [arrow([x, 0.15, 0], [x, -0.6, 0], C.muted, width=3.5, tip=0.2) for x in xs]
    for i in (0, 1):
        m.play(FadeIn(backed(tops[i], 0.1, 0.82), shift=0.15 * DOWN), at=T.d_xy + 0.3 + 0.55 * i, dur=0.5)
        m.play(GrowArrow(arrows[i]), FadeIn(backed(ends[i], 0.1, 0.82), shift=0.15 * DOWN), at=T.arrow_eqs + 0.4 * i, dur=0.5)
    m.play(Indicate(L[5], color=C.obj, scale_factor=1.25), Indicate(L[9], color=C.con, scale_factor=1.25), at=T.arrow_eqs + 0.2, dur=1.0)
    m.play(FadeIn(backed(tops[2], 0.1, 0.82), shift=0.15 * DOWN), at=T.d_lam + 0.5, dur=0.5)
    m.play(Indicate(L[8:], color=C.con, scale_factor=1.15), at=T.d_lam + 0.9, dur=1.0)
    m.play(GrowArrow(arrows[2]), FadeIn(backed(ends[2], 0.1, 0.82), shift=0.15 * DOWN), at=T.out_con, dur=0.5)
    rest = VGroup(*tops, *ends, *arrows)
    m.play(FadeOut(rest, shift=0.2 * UP), at=T.restricted + 0.6, dur=0.6, ease=E, lead=0)
    flat = backed(tex(r"\nabla", r"\mathcal{L}", "=", "0", size=84, colors={1: C.lag}), 0.14, 0.82).move_to([0, 0.5, 0])
    m.play(FadeIn(flat, shift=0.1 * UP), at=T.restricted + 1.2, dur=0.7)
    m.play(FadeIn(backed(lab("one more variable, no constraint", 30, C.text), 0.1, 0.82).move_to([0, -0.45, 0])), at=T.restricted + 2.2, dur=0.5)
    pin(m, cam, [*SUMMIT, hill(*SUMMIT) + 0.05], backed(lab("flat ground, in a higher dimension", 30, C.tang), 0.1, 0.82), T.returned + 0.3, T.cut_saddle - 0.05, off=(0.0, 0.7))
    curtain(s, a=True, b=True)
