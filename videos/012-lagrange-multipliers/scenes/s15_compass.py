"""s15: carry the uphill arrow along the trail and split it in the slope's own plane. The along-the-trail part is what is left to gain, and it dies at the best point."""
from aion import *

from beats import T
from ch1 import *

K = 1.3
ALL = np.linspace(0, TAU, 360)


def parts(s_):
    q = np.array(trail(s_))
    g = hill_grad(*q)
    d = trail_tangent(s_)
    d = d / np.linalg.norm(d)
    along = (g @ d) * d
    return q, g, along, g - along


@scene(T.cut_compass, T.cut_proof)
def s15_compass(s):
    backdrop(s)
    s0 = LOW_S + 0.75
    w = lambda t: s0 + (BEST_S - s0) * ramp(t, T.carry, T.arrive + 0.5) if t < T.arrive + 0.5 else BEST_S
    wq = lambda t: np.array(trail(w(t)))
    best = (-115, 70, 2.4, 0.4, -0.4, 30, BEST[0], BEST[1], BEST_H)
    cam = camera(
        (T.cut_compass, (-25, 48, 1.4, 0.0, -0.6, 26, 0, 0, 0)),
        (T.carry + 1.0, (-40, 64, 1.9, 0.0, -0.5, 26, 0, 0, 0)),
        (T.across, (-55, 66, 1.9, 0.0, -0.5, 26, 0, 0, 0)),
        (T.better, (-75, 68, 1.9, 0.0, -0.5, 26, 0, 0, 0)),
        (T.arrive + 0.6, best),
        (T.cut_proof, (-125, 70, 2.4, 0.4, -0.4, 30, BEST[0], BEST[1], BEST_H)),
        follow=lambda t: (win(t, T.carry - 0.6, T.arrive + 0.5, 1.4, 1.4), [*wq(t), hill(*wq(t))]),
    )
    split = lambda t: ramp(t, T.split + 0.4, T.split + 1.1)

    def frame(t):
        v = view().begin(cam(t))
        mountain(v)
        floor(v)
        wires(v, 1.0, 0.2)
        contours(v, 1.0, C.obj, 0.45, 1.6)
        curve(v, np.column_stack(trail(ALL)), C.con, 6.0)
        q, g, along, across = parts(w(t))
        a = split(t)
        on = ramp(t, T.carry - 0.4, T.carry + 0.3)
        p0, p1 = up(q, g * K)
        v.arrow(p0, p1, C.obj, width=6.0, tip=0.22, alpha=on * (1 - 0.7 * a))
        if a > 0.01:
            if np.linalg.norm(along) > 0.02:
                p0, p1 = up(q, along * K)
                v.arrow(p0, p1, C.tang, width=6.0, tip=0.22, alpha=a)
            p0, p1 = up(q, across * K)
            v.arrow(p0, p1, C.text, width=5.0, tip=0.2, alpha=a)
            gp = up(q, g * K)[1]
            for e in (up(q, along * K)[1], up(q, across * K)[1]):
                for j in range(8):
                    if j % 2 == 0:
                        v.line([e + (gp - e) * j / 8, e + (gp - e) * (j + 1) / 8], C.muted, 1.6, 0.8 * a)
        bead(v, q, r=0.1)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_compass, T.cut_proof)]))
    m = s.manim(z=5, parallax=0.0)
    tip_along = lambda t: up(parts(w(t))[0], parts(w(t))[2] * K)[1]
    tip_across = lambda t: up(parts(w(t))[0], parts(w(t))[3] * K)[1]
    tip_g = lambda t: up(parts(w(t))[0], parts(w(t))[1] * K)[1]
    pin(m, cam, tip_g, tex(r"\nabla f", size=50, color=C.obj), T.carry + 0.4, T.split + 0.6, off=(0.35, 0.3))
    pin(m, cam, tip_across, backed(lab("across: off limits", 28, C.text), 0.1, 0.85), T.across + 0.2, T.cut_proof - 0.05, off=(0.0, 0.45))
    pin(m, cam, tip_along, backed(lab("along: room to climb", 28, C.tang), 0.1, 0.85), T.along_p + 0.2, T.arrive + 0.2, off=(0.0, -0.45))
    h = s.manim(z=20, parallax=0.0)
    headline(h, backed(tex(r"\text{along}", "=", "0", size=64, colors={0: C.tang}), 0.14, 0.85), T.arrive + 0.6, T.cut_proof - 0.2)
    headline(h, backed(lab("all that is left points straight across the path", 30, C.text), 0.1, 0.85), T.remains + 0.2, T.cut_proof - 0.2, y=2.55)
    curtain(s, a=False, b=False)
