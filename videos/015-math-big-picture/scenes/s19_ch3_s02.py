"""ch3_s02 · Moves you can combine (the lock dial).

The circle from the hook slides left and grows into the dial of a combination lock: forty ticks, a zero mark and a
pointer. On 'thirty' the pointer turns 30° and a violet arc records it; on 'forty-five' a second arc carries on to
75°, and on 'seventy-five' the two arcs merge into one while 30° + 45° = 75° assembles. On 'undone' a reverse arc
takes the pointer back to zero (75° + (−75°) = 0°); on 'alone' it rests there, tagged 0°. On 'combine', 'undo' and
'nothing' three key words line up and fold into the small-caps word 'group', with 'algebra' under it.
"""
import math

from aion import *

from beats import T
from hud import progress
from kit import P3, caps, sans, tex, the_circle, window

CI_C, CI_R = P3(3.3, 0.0), 1.45          # where ch3_s01 left the circle
DC, RD = P3(-2.8, -0.1), 2.15
XC = 3.4


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ramp(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if t <= tb:
            return va + (vb - va) * ss((t - ta) / (tb - ta))
    return keys[-1][1]


def at_deg(r, deg):
    a = math.radians(90 + deg)
    return DC + r * P3(math.cos(a), math.sin(a))


@scene(T.ch3_s02, T.ch3_s03)
def ch3_s02(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_lock, t_30, t_45 = float(T.ch3_s02_lock), float(T.ch3_s02_thirty), float(T.ch3_s02_forty_five)
    t_75, t_un, t_al, t_gr = (float(T.ch3_s02_seventy_five), float(T.ch3_s02_undone), float(T.ch3_s02_alone),
                              float(T.ch3_s02_group))
    V = C.structure

    # the circle becomes the dial
    ci = the_circle(CI_R).move_to(CI_C)
    m.add(ci)
    dial = the_circle(RD).move_to(DC)
    m.play(Transform(ci, dial), at=t0 + 0.6, dur=1.4, ease="easy_ease")
    ticks = VGroup()
    for k in range(40):
        a = math.radians(90 + 9 * k)
        L = 0.32 if k % 5 == 0 else 0.17
        ticks.add(Line(DC + (RD - L) * P3(math.cos(a), math.sin(a)), DC + (RD - 0.04) * P3(math.cos(a), math.sin(a)),
                       stroke_color=C.text if k % 5 == 0 else C.muted, stroke_width=2.4 if k % 5 == 0 else 1.6))
    zero = tex("0", 34, C.text).move_to(at_deg(RD + 0.35, 0))
    m.play(LaggedStart(*(FadeIn(x_) for x_ in ticks), lag_ratio=0.02), FadeIn(zero), at=t_lock - 0.9, dur=1.0)

    hand_keys = [(t_30, 0.0), (t_30 + 0.8, 30.0), (t_45 + 0.05, 30.0), (t_45 + 0.95, 75.0), (t_un + 0.2, 75.0),
                 (t_un + 1.4, 0.0)]

    def hand(t):
        d = ramp(t, hand_keys)
        g = VGroup(Line(DC, at_deg(RD - 0.45, d), stroke_color=C.text, stroke_width=4),
                      Triangle(fill_color=C.text, fill_opacity=1, stroke_width=0).scale(0.1).rotate(math.radians(d))
                      .move_to(at_deg(RD - 0.45, d)),
                      Dot(DC, radius=0.09, color=C.text))
        f = 1 - ss((t - float(s.end) + 0.7) / 0.6)
        if f < 1:
            g.set_stroke(opacity=f)
            g.set_fill(opacity=f)
        return g

    h0 = hand(t_lock - 0.5)
    m.play(FadeIn(h0), at=t_lock - 0.5, dur=0.4)
    m.remove(h0, at=t_lock)
    top.redraw(window(hand, t_lock, float(s.end)), during=(t_lock, float(s.end)))

    # the arcs: 30, then 45 more; they merge into 75
    def arc(r, a0, a1, col=V, w=6):
        return Arc(radius=r, start_angle=math.radians(90 + a0), angle=math.radians(a1 - a0), arc_center=DC,
                   stroke_color=col, stroke_width=w)

    a30 = arc(1.0, 0, 30)
    a45 = arc(1.3, 30, 75)
    m.play(Create(a30), at=t_30, dur=0.8)
    m.play(Create(a45), at=t_45 + 0.05, dur=0.9)
    a75 = arc(1.15, 0, 75)
    m.play(ReplacementTransform(VGroup(a30, a45), a75), at=t_75 - 0.2, dur=0.8, ease="easy_ease")

    E1 = MathTex(r"30^\circ", r"+45^\circ", r"=75^\circ", font_size=52, color=C.text).move_to(P3(XC, 1.9))
    E1[2].set_color(V)
    m.play(Write(E1[0]), at=t_30 + 0.2, dur=0.5)
    m.play(Write(E1[1]), at=t_45 + 0.2, dur=0.5)
    m.play(Write(E1[2]), at=t_75, dur=0.6)

    # undone: a reverse arc back to zero; at rest, the turn of zero
    back = arc(1.55, 75, 0, C.muted, 3).add_tip(tip_length=0.18, tip_width=0.16)
    m.play(Create(back), at=t_un + 0.2, dur=1.2)
    E2 = MathTex(r"75^\circ", r"+(-75^\circ)", r"=0^\circ", font_size=52, color=C.text).move_to(P3(XC, 0.85))
    m.play(Write(E2), at=t_un + 0.6, dur=1.0)
    m.play(E1.animate.set_opacity(0.4), FadeOut(a75), at=t_un + 0.6, dur=0.5)
    tag0 = tex(r"0^\circ", 36, V).move_to(at_deg(RD + 0.35, 0) + P3(0.75, 0.05))
    m.play(FadeIn(tag0, shift=0.06 * LEFT), Indicate(zero, color=V), at=t_al, dur=0.6)

    # combine, undo, do nothing → group
    kws = VGroup(sans("combine", 34, C.text), sans("undo", 34, C.text), sans("do nothing", 34, C.text))
    kws.arrange(RIGHT, buff=0.55).move_to(P3(XC, -0.85))
    for k_, tt in zip(kws, (t_gr - 4.05, t_gr - 3.7, t_gr - 1.9)):     # 'combine', 'undo', 'does nothing'

        m.play(FadeIn(k_, shift=0.08 * UP), at=tt, dur=0.45)
    grp = caps("group", 64, V).move_to(P3(XC, -0.85))
    m.play(ReplacementTransform(kws, grp), at=t_gr - 0.1, dur=0.8, ease="easy_ease")
    alg = sans("algebra", 32, C.muted).next_to(grp, DOWN, buff=0.35)
    m.play(FadeIn(alg, shift=0.06 * UP), at=t_gr + 3.0, dur=0.5)
    m.play(FadeOut(VGroup(ci, ticks, zero, back, E1, E2, tag0, grp, alg)), at=float(s.end) - 0.7, dur=0.6)
