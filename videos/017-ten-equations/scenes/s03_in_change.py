"""in_s03 · Sentences about change (roadmap). Storyboard: plan/scene_plan.md § in_s03. Layout L4.

Opens on in_s02's last frame: the whole wall lit, names and years, the timeline. 'symbols': the timeline leaves and
each tile's equation writes under its name. 'plain words': T1's equation turns into the sentence it says ("fields
make waves") and back. 'lead into': link arcs draw tile to tile in chapter order, T1 → T10, each in the hue of the tile
it reaches, settling to grey behind the head; 'stock market': the chain reaches T10 and it pulses. 'begin with
light': the labels and links clear, the progress rail draws in, and the view dives into T1 (the other tiles slide
off past it) until its picture fills the frame, then fades for chapter one's card.
"""
import numpy as np
from aion import *

import intro as I
import outro as O
from beats import T
from kit import P3, add_rail, caps, glow, mix, polyline, sans
from theme import CHAPTERS


@scene(T.in_s03, T.c01_s01)
def s03_in_change(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_sy, t_pw, t_li, t_sm, t_bw = (float(T.in_s03_symbols), float(T.in_s03_plain_words), float(T.in_s03_lead_into),
                                    float(T.in_s03_stock_market), float(T.in_s03_begin_with_light))
    t_end = float(s.end)
    out = fade(t0 - 5, dur=0.1, out=t_end - 0.55, out_dur=0.45)               # everything fades for the card

    # the tiles; T10 pulses when the chain reaches it; T1 swaps to its full-resolution picture in the dive
    def t10_pulse(t):
        x = (t - t_sm - 0.1) / 0.8
        return 0.0 if x <= 0 or x >= 1 else float(np.sin(np.pi * x)) ** 2
    hi = lambda t: I.ease(t, t_bw + 0.6, t_bw + 1.1)
    for i in range(10):
        if i == 0:
            op = Track(lambda t: float(out(t)) * (1 - hi(t)))
        else:
            op = out
        O.tile_layer(s, i, lambda t, i=i: I.tile_place(i, t, grow=1 + (0.06 * t10_pulse(t) if i == 9 else 0.0)), op,
                     z=1)

    def hi_place(t):
        x, y, z = I.to_screen(I.pic_centre(0), t)
        return (x, y), z
    s.add(ArrayLayer(_hi_rgba(), height=O.TH, parallax=0.0,
                     pos=Track(lambda t: tuple(map(float, hi_place(t)[0]))), scale=Track(lambda t: float(hi_place(t)[1])),
                     z=2, opacity=Track(lambda t: float(out(t)) * hi(t)), start=t_bw + 0.5, end=t_end))

    # names (carried), then the equations under them
    lab_op = fade(t0 - 5, dur=0.1, out=t_bw + 0.05, out_dur=0.4)
    lab = s.manim(z=20, opacity=lab_op)
    labs = [O.wall_labels(i) for i in range(10)]
    lab.add(VGroup(*[l[0] for l in labs]))
    for i in range(10):
        lab.play(Write(labs[i][1]), at=t_sy + 0.2 + 0.2 * i, dur=1.0)

    # plain words: T1's equation says a sentence
    phrase = sans("fields make waves", 24, C.text).move_to(labs[0][1], aligned_edge=LEFT)
    back = labs[0][1].copy()
    lab.play(FadeTransform(labs[0][1], phrase), at=t_pw + 0.1, dur=0.7)
    lab.play(FadeTransform(phrase, back), at=t_li - 0.6, dur=0.6)

    # the timeline leaves as the equations arrive
    tl = VGroup(Line(P3(I.TL_X0, I.TL_Y), P3(I.TL_X1, I.TL_Y), stroke_color=C.ghost, stroke_width=1.5),
                caps("1763", 20, C.muted).next_to(P3(I.TL_X0, I.TL_Y), LEFT, buff=0.15),
                caps("1973", 20, C.muted).next_to(P3(I.TL_X1, I.TL_Y), RIGHT, buff=0.15))
    for i in range(10):
        x = I.tl_x(I.YEARS[i])
        tl.add(Line(P3(x, I.TL_Y - 0.1), P3(x, I.TL_Y + 0.1), stroke_color=getattr(C, CHAPTERS[i]), stroke_width=3))
    s.manim(z=20, opacity=fade(t0 - 5, dur=0.1, out=t_sy - 0.2, out_dur=0.6)).add(tl)

    # the chain: T1 → T10
    step = (t_sm - t_li) / 9
    paths = [I.link_pts(i) for i in range(9)]

    def chain(t):
        a = float(lab_op(t))
        g = VGroup()
        if a < 0.01:
            return g
        for i in range(9):
            ta = t_li + step * i
            u = I.ease(t, ta, ta + step * 1.1)
            if u <= 0:
                break
            k = max(int(u * (len(paths[i]) - 1)), 1)
            hue = getattr(C, CHAPTERS[i + 1])
            col = mix(hue, C.muted, 0.75 * I.ease(t, ta + step * 1.6, ta + step * 3.0))
            g.add(polyline([tuple(p) for p in paths[i][:k + 1]], col, 2.4, a))
        return g
    s.manim(z=25).redraw(chain, during=(t_li - 0.1, t_bw + 0.6))

    # a bright head travels the front of each arc as it draws
    def heads(t):
        a = float(lab_op(t))
        g = VGroup()
        for i in range(9):
            ta = t_li + step * i
            u = I.ease(t, ta, ta + step * 1.1)
            if u <= 0 or u >= 1 or a < 0.01:
                continue
            hue = getattr(C, CHAPTERS[i + 1])
            p = paths[i][int(u * (len(paths[i]) - 1))]
            g.add(Dot(P3(*p), radius=0.05, color=hue).set_opacity(a * float(np.sin(np.pi * u)) ** 0.5))
        return g
    glow(s, C.light, z=26, k=0.9).redraw(heads, during=(t_li - 0.1, t_sm + 0.5))

    # stock market: a ripple leaves T10
    def ripple(t):
        x = (t - t_sm - 0.1) / 1.2
        if x <= 0 or x >= 1:
            return VGroup()
        cx, cy = I.pic_centre(9)
        r = O.TH * (0.5 + 0.45 * x)
        c = Circle(radius=r, stroke_color=C.bs, stroke_width=2.5 * (1 - x) + 0.5, stroke_opacity=(1 - x) ** 3)
        return I.apply_view(c.move_to(P3(cx, cy)), t)
    glow(s, C.bs, z=24, k=0.6).redraw(ripple, during=(t_sm, t_sm + 1.4))

    # the dive: a radial whoosh at its fastest
    s.fx(ZoomBlur(amount=pulse(t_bw + 1.1, 0.07, dur=1.4)))

    # begin with light: the rail draws in (it carries on into chapter one)
    add_rail(s, 1, opacity=fade(t_bw + 0.1, dur=0.8))


def _hi_rgba():
    from PIL import Image
    return np.asarray(Image.open(O.TILE_DIR / "T01_hi.png").convert("RGBA"))
