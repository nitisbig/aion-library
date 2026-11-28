"""in_s04 · The plan. The camera brings the map back to the centre; THE circle brightens and a ring of light runs round
it. On each clause (what it is, how big, how it turns, what shape, how it grows, chance) a spoke of light leaves the
circle in that branch's hue and runs out to its place on the ring; the node opens there and its glyph is written in,
then the spoke settles to a faint trace. On 'lights up' all six spokes and nodes pulse together, then settle unlit,
waiting for their chapters.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import map_deco, HUB_R, NODE_R, P3, PILLARS, hue, map_lines, node, node_xy, the_circle

CAM_C, CAM_Z = (3.6, 0.0), 0.8


@scene(T.in_s04, T.in_s05)
def in_s04(s):
    s.solid(C.bg, z=-200)
    s.camera.base.update(x=CAM_C[0], y=CAM_C[1], zoom=CAM_Z)
    s.camera.frame(T.in_s04 + 0.55, center=(0.0, 0.0), zoom=1.0, dur=1.6)
    mp, sp, nd, m = s.manim(z=-3), s.manim(z=-2), s.manim(z=-1), s.manim(z=0)
    mp.add(map_deco(), map_lines(color=C.map_off, width=1.8, opacity=0.75))
    circle = the_circle(fill_color=C.bg, fill_opacity=1.0)
    m.add(circle)

    # 'one circle': it brightens, and a short arc of light runs once round it
    t_one = float(T.in_s04_one_circle)
    m.play(circle.animate(rate_func=there_and_back).set_stroke(width=8.5), at=t_one, dur=1.1)
    run = Arc(radius=HUB_R, start_angle=-math.pi / 2, angle=0.9, stroke_color=C.text, stroke_width=9)
    m.play(Rotate(run, -2 * math.pi, about_point=ORIGIN), at=t_one, dur=1.4, ease="easy_ease")
    m.add(run, at=t_one - 0.15)
    m.remove(run, at=t_one + 1.3)

    lit = [node(k, lit=True) for k in range(6)]
    beats_ = [T.in_s04_what_it_is, T.in_s04_how_big, T.in_s04_how_it_turns, T.in_s04_what_shape,
              T.in_s04_how_it_grows, T.in_s04_chance]
    spokes = []
    for k, (g, b) in enumerate(zip(lit, beats_)):
        q = node_xy(k)
        u = q / np.linalg.norm(q)
        a, z = u * (HUB_R + 0.04), q - u * (NODE_R + 0.03)
        spoke = Line(a, z, stroke_color=hue(PILLARS[k]), stroke_width=4)
        spark = Dot(a, radius=0.07, color=hue(PILLARS[k]))
        spokes.append(spoke)
        sp.play(Create(spoke), MoveAlongPath(spark, Line(a, z)), at=b - 0.25, dur=0.4, ease="in_out_cubic")
        sp.add(spark, at=b - 0.4)
        sp.remove(spark, at=b + 0.15)
        sp.play(spoke.animate.set_stroke(width=1.6, opacity=0.35), at=b + 0.5, dur=0.6)
        ring, glyph, label = VGroup(g[0], g[1], g[2]), g[3], g[4]
        nd.play(GrowFromCenter(ring), at=b + 0.05, dur=0.4, ease="out_back")
        nd.play(Write(glyph), at=b + 0.15, dur=0.5)
        nd.play(FadeIn(label, shift=0.08 * UP), at=b + 0.25, dur=0.4)

    # 'lights up': one pulse of every spoke and node together, then they settle unlit
    t1 = float(T.in_s04_lights_up)
    sp.play(*(sk.animate(rate_func=there_and_back).set_stroke(width=4.5, opacity=1.0) for sk in spokes), at=t1,
            dur=0.7)
    nd.play(*(g.animate(rate_func=there_and_back).scale(1.14) for g in lit), at=t1, dur=0.7)
    off = [node(k, lit=False) for k in range(6)]
    nd.play(*(Transform(g[i], o[i]) for g, o in zip(lit, off) for i in range(3)), *(FadeOut(VGroup(g[3], g[4])) for g in lit),
            at=t1 + 0.8, dur=0.8)
    sp.play(*(FadeOut(sk) for sk in spokes), at=t1 + 0.8, dur=0.8)
