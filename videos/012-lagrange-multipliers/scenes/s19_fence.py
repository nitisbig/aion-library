"""s19: the first worked example. Forty meters of rope, a rectangular plot, and lambda comes out equal to ten."""
from aion import *

from beats import T
from classic import *

CX = -1.5


@scene(T.cut_ch5, T.cut_circle)
def s19_fence(s):
    backdrop(s)
    g = s.manim(z=0)
    shore(g, CX)
    progress(s, 5, "Worked examples")
    d = keys((T.rect, 5.5), (T.plot10, 5.5), (T.plot10 + 1.2, 10.0), default_ease=E)
    show = fade(T.forty - 0.2, dur=0.6)
    live(g, lambda t: patch(rect_rope(float(d(t)), 40 - 2 * float(d(t)), CX), float(show(t))), (T.forty - 0.2, T.plot10 + 1.3))

    def side_tags(t):
        dd = float(d(t))
        w = (40 - 2 * dd) * BU / 2
        out = VGroup()
        if t >= float(T.sides_x):
            out.add(backed(tex("x", size=46, color=C.text), 0.06).move_to([CX - w - 0.42, SHORE - dd * BU / 2, 0]))
        if t >= float(T.side_y):
            out.add(backed(tex("y", size=46, color=C.text), 0.06).move_to([CX, SHORE - dd * BU - 0.42, 0]))
        return out
    live(g, side_tags, (T.sides_x, T.plot10 + 1.3))
    m = s.manim(z=2)
    m.play(FadeIn(backed(lab("40 m of rope", 32, C.con)).move_to([CX, -2.9, 0])), at=T.forty, dur=0.5)
    m.play(FadeIn(backed(lab("10 m by 20 m", 32, C.text)).move_to([CX, -1.5, 0])), at=T.plot10 + 1.1, dur=0.5)
    m.play(FadeIn(tex("200", r"\text{ m}^2", size=64, colors={0: C.area, 1: C.area}).move_to([CX, 0.7, 0]), scale=0.8), at=T.area200, dur=0.6, ease="out_back")
    h = hud(s)
    z = 40
    box = board(h, [(tex(r"\max\;", "xy", size=z, colors={1: C.obj}), T.maximize), (tex("2x+y", "=", "40", size=z, colors={0: C.con, 2: C.con}), T.maximize + 2.2), (tex(r"\nabla f", "=(y,x)", size=z, colors={0: C.obj}), T.grad_a),
                    (tex(r"\nabla g", "=(2,1)", size=z, colors={0: C.con}), T.grad_r), (tex("y=2", r"\lambda", r",\ x=", r"\lambda", size=z, colors={1: C.lam, 3: C.lam}), T.y_lam), (tex("4", r"\lambda", "=40", size=z, colors={1: C.lam}), T.four)], "ur")
    ans = tex(r"\lambda", "=", "10", size=84, colors={0: C.lam, 2: C.lam})
    b2 = board(h, [(ans, T.lam10)], "dr")
    h.play(Create(SurroundingRectangle(ans, color=C.lam, buff=0.12, stroke_width=3)), at=T.hold, dur=0.6, ease=E)
    curtain(s)
