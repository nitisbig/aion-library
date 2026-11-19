"""s09: the mountain becomes a function. Heights are f(x, y), the gradient points uphill, and climbing ends where it vanishes."""
from aion import *

from beats import T
from classic import *


def ascent(start, steps=2600, h=0.008):
    P = [np.array(start, float)]
    for _ in range(steps):
        g = hill_grad(*P[-1])
        n = np.linalg.norm(g)
        if n < 1e-4:
            break
        P.append(P[-1] + h * g / max(n, 0.35))
    return np.array(P)


@scene(T.cut_ch1, T.cut_constraint)
def s09_objective(s):
    stage(s, with_trail=False, at=T.fxy + 0.3)
    tilt = keys((T.give, 0.0), (T.fxy + 0.8, 1.0), default_ease=E)

    def frame(t):
        drift = (float(T.give) - min(t, float(T.give))) * 1.1
        v = view().begin(lerp_cam(float(tilt(t)), (POSE_3D[0] + drift, *POSE_3D[1:]), POSE_MAP))
        draw_mountain(v, contour_alpha=0.6)
        ground(v)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch1, T.fxy + 1.6)], opacity=key(T.fxy + 0.9, 1.0, 0.0, dur=0.7)))
    progress(s, 1, "Free and constrained")
    m = s.manim(z=1)
    field = grad_field()
    m.play(FadeIn(field, lag_ratio=0.01), at=T.no_limit, dur=1.2, ease=E)
    m.play(field.animate.set_opacity(0.2), at=T.steepest + 0.3, dur=0.7, ease=E)
    P = ascent((1.75, -1.7))
    prog = keys((T.follow - 0.2, 0.0), (T.grad_zero + 0.6, 1.0), default_ease=E)
    show = fade(T.steepest - 0.1, dur=0.5)

    def climber(t):
        i = int(float(prog(t)) * (len(P) - 1))
        q = P[i]
        g = hill_grad(*q)
        a = float(show(t))
        out = VGroup()
        if i > 6:
            out.add(poly([mp(p) for p in P[: i + 1][:: max(1, i // 120)]], C.you, 4.5, a))
        if np.linalg.norm(g) > 0.04:
            out.add(arrow(mp(q), mp(q) + p3(g * 1.05), C.obj, tip=0.28).set_opacity(a))
        out.add(walker(mp(q)).set_opacity(a))
        return out
    live(m, climber, (T.steepest - 0.1, T.grad_zero + 0.7))
    flag = icon("flag", 0.82, C.text).move_to(mp(SUMMIT) + np.array([0.28, 0.42, 0]))
    m.play(Create(flag), at=T.grad_zero + 0.55, dur=0.8, ease=E)
    board(hud(s), [(tex("f", "(x,y)", size=64, colors={0: C.obj}), T.fxy), (lab("objective", 30, C.obj), T.objective),
                   (tex(r"\nabla f", size=64, color=C.obj), T.grad_name), (lab("steepest way up", 30, C.text), T.grad_name + 0.3),
                   (tex(r"\nabla f", "=", "0", size=64, colors={0: C.obj}), T.grad_zero), (lab("flat ground", 30, C.tang), T.flat_again)])
    curtain(s, a=True, b=False)
