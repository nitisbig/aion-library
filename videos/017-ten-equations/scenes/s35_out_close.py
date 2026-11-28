"""out_s02 · Last line (close). Storyboard: plan/scene_plan.md § out_s02. Layout L4.

Opens on out_s01's last frame: the 5x2 wall, every tile lit, names and equations under it, 'Ten equations · 1763 –
1973' above. 'Fourier': tile T5 lifts and Fourier's hot bar from the opening cools inside it (sims.heat_bar,
exact), glowing. 'larger': the names leave, the wall pulls back into the upper third and dims to 40 %, and the title
lockup settles above it; the lower two thirds stay clear for the end screen through 'Thanks' and the 6 s hold.
"""
from aion import *

import ch10
import outro as O
from beats import T
from kit import P3, caps, glow, smooth01


@scene(T.out_s02, T.end)
def s35_out_close(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_fo, t_la = float(T.out_s02_fourier), float(T.out_s02_larger)

    back = lambda t: float(smooth01((t - t_la) / 2.2))                         # the pull-back on 'larger'
    K_END, DY_END, ROW_END = 0.42, 2.0, 0.37                                  # pulled back: rows close up
    lift5 = lambda t: float(smooth01((t - t_fo + 0.2) / 0.7)) * (1 - float(smooth01((t - t_la + 0.9) / 0.7)))

    def place(i):
        def f(t):
            x, y = O.wall(i)
            b = back(t)
            k = 1 - (1 - K_END) * b
            g = 1 + 0.12 * lift5(t) if i == 4 else 1.0
            ye = DY_END + (ROW_END if i < 5 else -ROW_END)
            return x * k, y + (ye - y) * b, k * g, 0.0
        return f
    w_op = Track(lambda t: 1.0 - 0.6 * back(t))
    for i in range(10):
        O.tile_layer(s, i, place(i), w_op, z=5 + (3 if i == 4 else 0))

    # out_s01's labels and closing line, leaving before the pull-back
    lab = s.manim(z=50, parallax=0.0, opacity=fade(t0 - 5, dur=0.1, out=t_la - 0.3, out_dur=0.6))
    lab.add(VGroup(*[O.wall_labels(i) for i in range(10)]), caps("Ten equations · 1763 – 1973", 36, C.text)
            .move_to(P3(0, 3.2)))

    # Fourier: his bar, cooling inside tile T5
    x5, y5 = O.wall(4)
    yc = y5 + O.pic_dy()                                                          # the picture's centre
    b_op = fade(t_fo + 0.1, dur=0.6, out=t_la - 0.6, out_dur=0.6)
    s.manim(z=10, parallax=0.0, opacity=b_op).add(
        Rectangle(width=O.TW * 1.12, height=O.TH * 1.12, stroke_width=0, fill_color=C.bg, fill_opacity=1.0)
        .move_to(P3(x5, yc)))

    def bar(t, cells):
        g = ch10.hot_bar(t, t_fo + 0.2, b_op, cells=cells, curve=not cells)
        if not len(g):
            return g
        g.scale(O.TW * 1.12 * 0.8 / 6.4, about_point=P3(0, -0.95)).shift(P3(x5, yc) - P3(0, -0.95))
        return g
    s.manim(z=11, parallax=0.0).redraw(lambda t: bar(t, True), during=(t_fo, t_la))
    glow(s, C.fourier, z=11.5, k=0.4, parallax=0.0).redraw(lambda t: bar(t, False), during=(t_fo, t_la))

    # the title lockup over the dimmed wall
    hud = s.manim(z=50, parallax=0.0)
    hud.play(FadeIn(caps("10 Equations That Run the Modern World", 40, C.text).move_to(P3(0, 3.3)),
                    shift=0.08 * DOWN), at=t_la + 0.9, dur=1.0)
