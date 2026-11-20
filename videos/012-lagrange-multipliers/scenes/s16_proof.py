"""s16: the proof in three lines, each tied to an arrow at the best point on the slope, then the count: three equations, three unknowns."""
from aion import *

from beats import T
from ch1 import *

ALL = np.linspace(0, TAU, 360)
D = trail_tangent(BEST_S) / np.linalg.norm(trail_tangent(BEST_S))


@scene(T.cut_proof, T.cut_ch4)
def s16_proof(s):
    backdrop(s)
    cam = camera(
        (T.cut_proof, (-125, 70, 2.4, 0.4, -0.4, 30, BEST[0], BEST[1], BEST_H)),
        (T.proof + 1.2, (-105, 74, 3.2, 2.4, -0.6, 30, BEST[0], BEST[1], BEST_H)),
        (T.as_long, (-125, 72, 3.2, 2.4, -0.6, 30, BEST[0], BEST[1], BEST_H)),
        (T.count + 1.0, (-90, 89.5, 1.0, 2.6, -0.2, 400, 0, 0, 0)),
        (T.cut_ch4, (-90, 89.5, 0.9, 2.6, -0.2, 400, 0, 0, 0)),
    )
    dim = lambda t: ramp(t, T.count, T.algebra + 1.0)

    def frame(t):
        v = view().begin(cam(t))
        a = 1 - 0.85 * dim(t)
        mountain(v, 1.0, a)
        floor(v, 1.0, 0.55 * a)
        if a > 0.5:
            wires(v, 1.0, 0.2 * a)
            contours(v, 1.0, C.obj, 0.4 * a, 1.6)
        curve(v, np.column_stack(trail(ALL)), C.con, 6.0, a)
        fa = 1 - ramp(t, T.count - 0.3, T.count + 0.4)
        for at_, w, col, wd in ((T.path_r + 0.5, D * 0.9, C.tang, 6.0), (T.g_dot - 0.2, trail_grad(*BEST) * 0.9, C.con, 5.5), (T.f_dot - 0.2, hill_grad(*BEST) * 0.62, C.obj, 6.0)):
            g = ramp(t, at_, at_ + 0.6) * fa
            if g > 0.01:
                p0, p1 = up(BEST, w * g + 1e-3)
                v.arrow(p0, p1, col, width=wd, tip=0.22, alpha=fa)
        ra = ramp(t, T.both_p, T.both_p + 0.5) * fa
        if ra > 0.01:
            nrm = trail_grad(*BEST) / np.linalg.norm(trail_grad(*BEST))
            for nn in (nrm, -nrm):
                c0, c1 = up(BEST, D * 0.16)[1], up(BEST, (D + nn) * 0.16)[1]
                v.line([c0, c1, up(BEST, nn * 0.16)[1]], C.text, 2.4, ra)
        bead(v, BEST, r=0.09 * fa + 1e-3)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_proof, T.cut_ch4)]))
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, up(BEST, D * 0.9)[1], tex(r"\mathbf{r}'", size=50, color=C.tang), T.path_r + 0.8, T.count, off=(0.3, 0.25))
    pin(m, cam, up(BEST, trail_grad(*BEST) * 0.9)[1], tex(r"\nabla g", size=50, color=C.con), T.g_dot + 0.2, T.count, off=(0.35, 0.2))
    pin(m, cam, up(BEST, hill_grad(*BEST) * 0.62)[1], tex(r"\nabla f", size=50, color=C.obj), T.f_dot + 0.2, T.count, off=(-0.4, -0.25))
    h = s.manim(z=20, parallax=0.0)
    z = 44
    stack(h, [(tex(r"\mathbf{r}(t)", r"\ \text{on the trail}", size=z, colors={0: C.tang}), T.path_r + 0.5),
              (tex("g", r"(\mathbf{r}(t))=c", r"\;\Rightarrow\;", r"\nabla g", r"\cdot", r"\mathbf{r}'", "=0", size=z, colors={0: C.con, 3: C.con, 5: C.tang}), T.g_dot - 0.2),
              (tex(r"\tfrac{d}{dt}", "f", r"(\mathbf{r})=0", r"\;\Rightarrow\;", r"\nabla f", r"\cdot", r"\mathbf{r}'", "=0", size=z, colors={1: C.obj, 4: C.obj, 6: C.tang}), T.f_dot - 0.2),
              (tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=76, colors={0: C.obj, 2: C.lam, 3: C.con}), T.both_p + 1.2),
              (tex(r"\text{if }", r"\nabla g", r"\neq 0", size=38, colors={1: C.con}), T.as_long)], pos=(-6.75, 3.3), out=T.count - 0.3, gap=0.34)
    big = 64
    rows = [(tex("f_x", "=", r"\lambda", "g_x", size=big, colors={0: C.obj, 2: C.lam, 3: C.con}), T.two_eq),
            (tex("f_y", "=", r"\lambda", "g_y", size=big, colors={0: C.obj, 2: C.lam, 3: C.con}), T.two_eq + 0.4),
            (tex("g", "=", "c", size=big, colors={0: C.con, 2: C.con}), T.one_con)]
    stack(h, rows, pos=(-6.2, 2.4), gap=0.42)
    unk = backed(tex("x", ",", r"\;y", ",", r"\;\lambda", size=big, colors={4: C.lam}), 0.12, 0.85).move_to([-3.6, -1.9, 0])
    h.play(FadeIn(unk, shift=0.08 * UP), at=T.three + 0.2, dur=0.6, ease=E)
    cnt = backed(lab("3 equations, 3 unknowns", 34, C.text), 0.1, 0.85).move_to([-3.6, -3.0, 0])
    h.play(FadeIn(cnt, shift=0.08 * UP), at=T.algebra - 0.3, dur=0.6, ease=E)
    curtain(s, a=False, b=True)
