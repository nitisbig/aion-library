"""s27 beyond (outro): the idea doesn't stop at matrices. Left, the last video's callback: put the derivative in the
exponent and e^{h d/dx} slides a whole graph sideways, f(x) → f(x + h). Right, quantum mechanics: a state moves forward
in time by e^{−iHt/ħ}, a phase ribbon (Re and Im) advancing, with energy H playing the part of the matrix."""
from aion import *

from beats import T
from shots import E, backdrop, finish, lab, live, p3, panel, plot, tex

LB = (-6.95, -2.75, -0.2, 2.45)
RB = (0.2, -2.75, 6.95, 2.45)
LO, RO = np.array([-3.575, -1.35]), np.array([3.575, -0.15])


def f(x):
    return 1.6 * np.exp(-((x - 0.6) ** 2) / 0.5) + 0.7 * np.exp(-((x + 0.9) ** 2) / 0.25)


@scene(T.cut_beyond, T.cut_bookend)
def s27_beyond(s):
    backdrop(s)
    m = s.manim(z=2)
    fl, fr = panel(*LB, fill=False), panel(*RB, fill=False)
    m.play(Create(fl), Create(fr), at=T.beyond + 0.2, dur=0.8)

    # ── left: e^{h d/dx} slides the graph ──
    tl = lab("last video", 26, C.muted).move_to([(LB[0] + LB[2]) / 2, LB[3] + 0.32, 0])
    fx = tex(r"e^{h\frac{d}{dx}}", r"f(x)", "=", r"f(x+h)", size=46, colors={1: C.vec, 3: C.vec}).move_to(
        [(LB[0] + LB[2]) / 2, LB[1] - 0.6, 0])
    for k in range(1, 5):
        fx[0][k].set_color(C.gen)
    ax = Line(p3(LO + [-3.1, 0]), p3(LO + [3.1, 0]), color=C.muted, stroke_width=C.thin)
    ghost = plot(f, -3.0, 3.0, LO, 1.0, 1.0, C.vec, width=C.thin + 0.4, opacity=0.35)
    m.play(FadeIn(tl), Create(ax), Create(ghost), at=T.last_video + 0.2, dur=0.8)
    m.play(FadeIn(fx, shift=0.1 * UP), at=T.last_video + 1.2, dur=0.7)
    h = keys((T.slid - 0.4, 0.0), (T.slid + 2.2, 1.5, E), lead=0)
    op = keys((T.last_video + 0.2, 0.0), (T.last_video + 0.9, 1.0), (T.cut_bookend - 0.4, 1.0), (T.cut_bookend - 0.05, 0.0),
              lead=0)
    live(m, lambda t: plot(lambda x: f(x + float(h(t))), -3.0, 3.0, LO, 1.0, 1.0, C.vec, width=C.stroke + 0.5,
                           opacity=float(op(t))),
         (T.last_video + 0.2, T.last_video + 0.95), (T.slid - 0.4, T.slid + 2.25), (T.cut_bookend - 0.4, T.cut_bookend))

    # ── right: e^{−iHt/ħ} advances a quantum state ──
    tr = lab("quantum mechanics", 26, C.muted).move_to([(RB[0] + RB[2]) / 2, RB[3] + 0.32, 0])
    qx = tex(r"\psi(t)", "=", r"e^{-iHt/\hbar}", r"\,\psi(0)", size=46, colors={0: C.flow, 3: C.flow}).move_to(
        [(RB[0] + RB[2]) / 2, RB[1] - 0.6, 0])
    qx[2][3].set_color(C.gen)
    w_op = keys((T.quantum + 0.2, 0.0), (T.quantum + 0.9, 1.0), (T.cut_bookend - 0.4, 1.0), (T.cut_bookend - 0.05, 0.0),
                lead=0)
    k0, om = 5.0, 3.2

    def ribbon(t):
        u = t - T.quantum
        a = float(w_op(t))
        env = lambda x: 1.15 * np.exp(-((x + 1.9 - 0.33 * u) ** 2) / 1.3)
        re = plot(lambda x: env(x) * np.cos(k0 * x - om * u), -3.1, 3.1, RO, 1.0, 1.0, C.flow, width=C.stroke, n=300,
                  opacity=a)
        im = plot(lambda x: env(x) * np.sin(k0 * x - om * u), -3.1, 3.1, RO, 1.0, 1.0, C.eigen, width=C.thin + 0.6, n=300,
                  opacity=0.8 * a)
        return VGroup(Line(p3(RO + [-3.1, 0]), p3(RO + [3.1, 0]), color=C.muted, stroke_width=C.thin,
                           stroke_opacity=a), im, re)
    live(m, ribbon, (T.quantum + 0.2, T.cut_bookend))
    keyl = VGroup(lab("Re", 22, C.flow), lab("Im", 22, C.eigen)).arrange(RIGHT, buff=0.3).move_to(
        [RB[2] - 0.7, RB[3] - 0.35, 0])
    m.play(FadeIn(tr), FadeIn(keyl), at=T.quantum + 0.2, dur=0.6)
    m.play(FadeIn(qx, shift=0.1 * UP), at=T.quantum + 1.6, dur=0.7)
    hb = VGroup(tex("H", size=40, color=C.gen), lab("energy", 24, C.gen)).arrange(RIGHT, buff=0.15)
    hb.move_to([RB[2] - 1.0, RB[1] + 0.4, 0])
    m.play(Indicate(qx[2][3], color=C.gen, scale_factor=1.6), FadeIn(hb), at=T.energy + 0.2, dur=0.8)
    m.play(FadeOut(VGroup(fl, fr, tl, fx, ax, ghost, tr, qx, keyl, hb)), at=T.cut_bookend - 0.4, dur=0.4)
    finish(s)
