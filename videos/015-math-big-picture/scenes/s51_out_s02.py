"""out_s02 · What to watch next (question, end card).

The emblem from out_s01 lets go of its ring and leaves THE circle. On 'question' the question comes up in two lines of
CM sans while the circle rests below it. On 'next video' the end card: the circle moves to the top, 'Next' in small
caps over a frame holding e^{iπ} + 1 = 0 in pillar colors (the next video, on Euler's identity); on 'Subscribe' a
slot for the end-screen button; on 'I give ideas' the line interactive app · igiveideas.com. Everything holds to the
end of the audio for YouTube's end-screen elements.
"""
import math

from aion import *

from beats import T
from kit import window, glow_layer, HUB_R, P3, PILLARS, caps, map_state, sans, the_circle

EDGES = tuple((PILLARS[i], PILLARS[j]) for i in range(6) for j in range(i + 1, 6))
EMBLEM = 0.5


@scene(T.out_s02, T.end)
def out_s02(s):
    s.solid(C.bg, z=-200)
    lnk, disc_l, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-0.5), glow_layer(s, z=0, color=C.circle, k=0.8), \
        s.manim(z=1)
    lit = glow_layer(s, z=0.8, k=0.7)                         # the end card's lit frame and its travelling light
    t0, t1 = float(s.start), float(s.end)
    t_q, t_nx, t_sub, t_ig = float(T.out_s02_question), float(T.out_s02_next_video), float(
        T.out_s02_subscribe), float(T.out_s02_i_give_ideas)

    links, nodes = map_state(0, lit=PILLARS, edges=EDGES)
    ring = VGroup(links, nodes).scale(EMBLEM, about_point=ORIGIN)
    circ = the_circle(HUB_R * EMBLEM)                         # the lit rim; a crisp black disc under it hides the chords
    disc = Circle(radius=HUB_R * EMBLEM, stroke_width=0, fill_color=C.bg, fill_opacity=1.0)
    lnk.add(ring)
    m.add(circ)
    disc_l.add(disc)
    lnk.play(FadeOut(ring), at=t0 + 0.2, dur=0.8)

    # the question
    q = VGroup(sans("Which branch felt most like the math you met in school?", 38, C.text),
               sans("Which felt least like it?", 38, C.text)).arrange(DOWN, buff=0.32).move_to(P3(0, 2.2))
    m.play(circ.animate.scale(1.6).move_to(P3(0, -1.1)), at=t_q - 0.4, dur=1.0, ease="easy_ease")
    disc_l.play(disc.animate.scale(1.6).move_to(P3(0, -1.1)), at=t_q - 0.4, dur=1.0, ease="easy_ease")
    top.play(FadeIn(q[0], shift=0.06 * UP), at=t_q, dur=0.6)
    top.play(FadeIn(q[1], shift=0.06 * UP), at=t_q + 5.0, dur=0.6)
    top.play(FadeOut(q), at=t_nx - 1.0, dur=0.5)

    # the end card
    m.play(circ.animate.scale(0.72).move_to(P3(0, 2.15)), at=t_nx - 0.8, dur=1.0, ease="easy_ease")
    disc_l.play(disc.animate.scale(0.72).move_to(P3(0, 2.15)), at=t_nx - 0.8, dur=1.0, ease="easy_ease")
    frame = RoundedRectangle(width=5.2, height=2.9, corner_radius=0.14, stroke_width=2.6)
    frame.set_stroke(color=[C.change, C.structure, C.quantity, C.foundations])
    frame.move_to(P3(-3.2, -0.9))
    nxt = caps("Next", 34, C.text).next_to(frame, UP, buff=0.18).align_to(frame, LEFT)
    idn = MathTex(r"e^{i\pi}", "+", "1", "=", "0", font_size=64, color=C.text).move_to(frame)
    for k_, c_ in ((0, C.change), (1, C.structure), (2, C.quantity)):
        idn[0][k_].set_color(c_)
    idn[2].set_color(C.foundations)
    idn[4].set_color(C.foundations)
    lit.play(Create(frame), at=t_nx - 0.2, dur=0.7)
    top.play(FadeIn(nxt), at=t_nx - 0.2, dur=0.7)
    r_e = disc.copy().scale(0.72).width / 2                 # the emblem ends at 0.72x (each .animate starts from the build state)
    t_l = t_nx + 0.6

    def lights(t):
        # a spark running round the frame, and a bright arc travelling round the emblem
        f = min(1.0, (t - t_l) / 0.6)
        u = ((t - t_l) / 7.0) % 1.0
        g = VGroup()
        for k in range(6):
            p = frame.point_from_proportion((u - 0.006 * k) % 1.0)
            g.add(Dot(p, radius=0.06 - 0.007 * k, color=C.text).set_opacity(f * (1 - k / 6)))
        turns = (t - t_l) / 4.5                                  # one pillar colour per turn of the sweep
        a = 2 * math.pi * turns
        col = getattr(C, PILLARS[int(turns) % 6])
        for k in range(6):
            g.add(Arc(radius=r_e, start_angle=a - 0.14 * k, angle=0.15, arc_center=P3(0, 2.15), stroke_color=col,
                      stroke_width=6, stroke_opacity=f * (1 - k / 6)))
        return g

    lit.redraw(window(lights, t_l, t1 + 1.0), during=(t_l, t1))
    top.play(Write(idn), at=t_nx + 0.6, dur=1.0)
    slot = RoundedRectangle(width=4.0, height=1.2, corner_radius=0.6, stroke_color=C.map_off, stroke_width=2.2)
    slot.move_to(P3(3.6, -0.9))
    sub = sans("subscribe", 34, C.muted).move_to(slot)
    top.play(Create(slot), FadeIn(sub), at=t_sub - 0.2, dur=0.6)
    app = sans(r"interactive app \textperiodcentered\ igiveideas.com", 32, C.muted).move_to(P3(0, -3.05))
    top.play(FadeIn(app, shift=0.06 * UP), at=t_ig - 0.3, dur=0.6)
