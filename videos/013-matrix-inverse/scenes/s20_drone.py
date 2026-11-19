"""s20 drone: one landmark, two names. In the drone's own steps it is (2, 1); on the map it is (3, 4). D translates one way, D^-1 the other."""
from aion import *

from beats import T
from film3 import frame
from shots import EASE, chapter_card, lab, tex, thread


@scene(T.cut_drone, T.cut_camera)
def s20_drone(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_drone, T.cut_camera)], z=0))
    mb = s.manim(z=4, parallax=0.0)                   # the plate behind the readouts
    m = s.manim(z=5, parallax=0.0)                    # readouts
    mh = s.manim(z=8, parallax=0.0)                   # the chapter card

    chapter_card(mh, tex(r"C^{-1}", size=104, color=C.back), "The way back at work", T.cut_drone, T.observers + 0.05)

    plate = Rectangle(width=3.9, height=7.1, stroke_color=C.frame, stroke_width=1.6, fill_color=C.bg, fill_opacity=0.96).move_to([4.7, 0, 0])
    mb.play(FadeIn(plate), at=T.steps + 1.2, dur=0.5)

    x = 4.75
    t_drone = lab("drone", size=36, color=C.cam).move_to([x, 2.65, 0])
    v_drone = tex(r"(2,\,1)", size=70, color=C.cam).move_to([x, 1.9, 0])
    t_map = lab("map", size=36).move_to([x, -1.5, 0])
    v_map = tex(r"(3,\,4)", size=70, color=C.vec).move_to([x, -2.3, 0])
    m.play(FadeIn(t_drone), FadeIn(v_drone, shift=0.06 * DOWN), at=T.steps + 1.65, dur=0.5)

    # ── D carries the drone's words onto the map ──
    down = thread((4.4, 1.32), (3.9, 0.0), (4.4, -1.1), C.fwd)
    d = tex("D", size=64, color=C.fwd).move_to([3.4, 0.1, 0])
    m.play(FadeIn(d), at=T.axes, dur=0.5)
    m.play(Create(down.path), at=T.axes + 1.0, dur=1.0, ease=EASE)
    m.play(FadeIn(down.head), at=T.axes + 1.9, dur=0.15, lead=0)
    m.play(FadeIn(t_map), FadeIn(v_map, shift=0.06 * DOWN), at=T.axes + 2.0, dur=0.5)

    # ── and D inverse carries the map back ──
    up = thread((5.1, -1.1), (5.6, 0.0), (5.1, 1.32), C.back)
    d_inv = tex(r"D^{-1}", size=56, color=C.back).move_to([6.02, 0.1, 0])
    m.play(FadeIn(d_inv), at=T.inv_map, dur=0.5)
    m.play(Create(up.path), at=T.inv_map + 0.65, dur=1.0, ease=EASE)
    m.play(FadeIn(up.head), at=T.inv_map + 1.55, dur=0.15, lead=0)
    m.play(Indicate(v_drone, color=C.cam, scale_factor=1.12), at=T.pov, dur=0.9)
    s.solid(C.bg, z=50, opacity=key(T.cut_camera - 0.42, 0.0, 1.0, dur=0.4, lead=0))
