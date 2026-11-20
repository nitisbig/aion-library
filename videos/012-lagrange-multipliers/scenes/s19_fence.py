"""s19: the first worked example on Dido's beach, in 3D. Forty meters of rope, a rectangular plot whose area stands up as a block, and lambda comes out equal to ten."""
from aion import *

from beats import T
from ch1 import *

from beach3d import AH, M, SH, block, corners, sand_and_sea


@scene(T.cut_ch5, T.cut_circle)
def s19_fence(s):
    backdrop(s)
    top = (-90, 89.5, 1.0, 0.0, -0.3, 400, 0, 0.6, 0)
    tilt = (-62, 34, 1.05, 0.0, -1.0, 30, 0, 0.8, 0.6)
    cam = camera(
        (T.cut_ch5, top),
        (T.maximize - 0.2, top),
        (T.maximize + 1.6, tilt),
        (T.plot10, (-78, 30, 1.05, 0.0, -1.0, 30, 0, 0.8, 0.8)),
        (T.cut_circle, (-100, 30, 1.05, 0.0, -1.0, 30, 0, 0.8, 0.8)),
    )
    d = keys((T.rect, 5.5), (T.maximize + 0.6, 5.5), (T.maximize + 2.6, 15.0), (T.maximize + 4.6, 7.0), (T.plot10, 7.0), (T.plot10 + 1.4, 10.0), default_ease=E)
    show = lambda t: ramp(t, T.forty - 0.2, T.forty + 0.5)
    lift = lambda t: ramp(t, T.maximize, T.maximize + 1.2)

    def frame(t):
        v = view().begin(cam(t))
        sand_and_sea(v)
        a = show(t)
        if a > 0.01:
            dd = float(d(t))
            P = corners(dd)
            block(v, dd, a * lift(t)) if lift(t) > 0.01 else block(v, dd, 0.0)
            if lift(t) < 0.01:
                X, Y = np.meshgrid([P[0, 0], P[2, 0]], [P[1, 1], P[0, 1]])
                v.mesh(X, Y, np.zeros_like(X) + 0.005, C.area, alpha=0.3 * a, shade=False)
            v.line(np.column_stack([P, np.full(4, 0.02)]), C.con, 6.0, a)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch5, T.cut_circle)]))
    title(s, "Chapter 5  ·  worked examples", T.cut_ch5 + 0.3, hold=3.0)
    m = s.manim(z=5, parallax=0.0)
    dd = lambda t: float(d(t))
    pin(m, cam, lambda t: [corners(dd(t))[0, 0], SH - dd(t) * M / 2, 0.0], backed(tex("x", size=46, color=C.text), 0.06, 0.85), T.sides_x, T.cut_circle - 0.05, off=(-0.35, 0.0))
    pin(m, cam, lambda t: [0.0, SH - dd(t) * M, 0.0], backed(tex("y", size=46, color=C.text), 0.06, 0.85), T.side_y, T.cut_circle - 0.05, off=(0.0, -0.35))
    pin(m, cam, [0.0, SH - 5.5 * M - 1.0, 0.0], backed(lab("40 m of rope", 32, C.con), 0.1, 0.85), T.forty, T.maximize, off=(0.0, 0.0))
    pin(m, cam, [0.0, SH - 0.5, 0.0], backed(lab("the sea", 28, C.con), 0.1, 0.85), T.forty + 0.6, T.rect + 1.5, off=(0.0, 1.0))
    pin(m, cam, lambda t: [0.0, SH - dd(t) * M / 2, dd(t) * (40 - 2 * dd(t)) * AH], backed(lab("area", 30, C.area), 0.1, 0.85), T.maximize + 1.0, T.area200 - 0.2, off=(0.0, 0.45))
    pin(m, cam, [0.0, SH - 1.0, 200 * AH], backed(tex("200", r"\text{ m}^2", size=60, colors={0: C.area, 1: C.area}), 0.1, 0.85), T.area200, T.cut_circle - 0.05, off=(0.0, 0.6))
    pin(m, cam, [0.0, SH - 2.0, 0.0], backed(lab("10 m deep, 20 m wide", 30, C.text), 0.1, 0.85), T.plot10 + 1.2, T.cut_circle - 0.05, off=(0.0, -1.05))
    h = s.manim(z=20, parallax=0.0)
    z = 42
    stack(h, [(tex(r"\max\;", "xy", size=z, colors={1: C.area}), T.maximize), (tex("2x+y", "=", "40", size=z, colors={0: C.con, 2: C.con}), T.maximize + 2.2),
              (tex(r"\nabla f", "=(y,x)", size=z, colors={0: C.obj}), T.grad_a), (tex(r"\nabla g", "=(2,1)", size=z, colors={0: C.con}), T.grad_r),
              (tex("y=2", r"\lambda", r",\ \ x=", r"\lambda", size=z, colors={1: C.lam, 3: C.lam}), T.y_lam), (tex("4", r"\lambda", "=40", size=z, colors={1: C.lam}), T.four)],
          pos=(6.75, 3.3), edge=UR, gap=0.2)
    ans = tex(r"\lambda", "=", "10", size=96, colors={0: C.lam, 2: C.lam}).move_to([4.9, -0.6, 0])
    h.play(FadeIn(backed(ans, 0.14, 0.85), scale=0.8), at=T.lam10, dur=0.6, ease="out_back")
    h.play(Create(SurroundingRectangle(ans, color=C.lam, buff=0.18, stroke_width=4)), at=T.hold, dur=0.6, ease=E)
    curtain(s, a=True, b=True)
