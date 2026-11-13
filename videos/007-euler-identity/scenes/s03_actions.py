"""Ch2 · Numbers as actions. The red i from Ch1 is not a number that cannot exist (√−1 struck through) but an
action: it joins a row ×2, ×½, ×(−1), ×i. A number line with dots at −3…3 is stretched by ×2 and squeezed by ×½
(ghosts keep the starting places). ×(−1) is shown as a turn, not a flip: 3 travels a dashed red semicircle to −3,
−2 travels the lower one to 2, then the whole line swings half a turn through the plane. Planted top right:
×(−1) = a half turn."""
from aion import *

from beats import T
from shots import (I_POS, NLY, action_row, backdrop, badges, chapter_card, dashed_arc, ease, live, numline, plant,
                   rail, ramp, ruler, tex)

E = "easy_ease"
O = (0.0, NLY)


@scene(T.cut_ch2, T.cut_quarter)
def s03_actions(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)                                 # the line, its hops and trails, under the row
    m = s.manim(z=2)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 2)
    badges(hud, 1)

    # ── "Now for i.": the red i from Ch1 rises; the chapter card ──
    i_ = tex("i", size=110, color=C.turn).move_to([*I_POS, 0])
    m.add(i_, at=t0)
    m.play(i_.animate.move_to([0, 2.1, 0]), at=t0 + 0.35, dur=0.9, ease=E, lead=0)
    chapter_card(m, 2, t0 + 0.4, T.cannot - 1.0)

    # ── "Forget the idea that i is a number that cannot exist." ──
    tail = tex(r"=\sqrt{-1}", size=110).set_color(C.muted)
    pos_i = np.array([-1.35, 0.4, 0])
    tail.next_to(pos_i, RIGHT, buff=0.35)
    m.play(i_.animate.move_to(pos_i), at=T.cannot - 0.6, dur=0.8, ease=E)
    m.play(FadeIn(tail, shift=0.15 * LEFT), at=T.cannot - 0.2, dur=0.6)
    strike = Line([pos_i[0] - 0.4, 0.25, 0], [tail.get_right()[0] + 0.2, 0.55, 0], color=C.text,
                  stroke_width=C.stroke)
    m.play(Create(strike), at=T.cannot + 0.45, dur=0.5)
    m.play(FadeOut(VGroup(tail, strike)), at=T.actions - 0.6, dur=0.5)

    # ── "Instead, think of numbers as actions.": the i joins a row of actions ──
    row = action_row()
    m.play(ReplacementTransform(i_, row[3][1]), at=T.actions + 0.1, dur=0.9, ease=E)
    m.play(LaggedStart(*[FadeIn(g, shift=0.1 * DOWN) for g in [*row[:3], row[3][0]]], lag_ratio=0.18),
           at=T.actions + 0.3, dur=1.0)
    m.play(row.animate.set_opacity(0.35), at=T.line, dur=0.6)

    def light(tok, a, b=None):
        m.play(tok.animate.set_opacity(1.0).scale(1.15), at=a, dur=0.45)
        if b is not None:
            m.play(tok.animate.set_opacity(0.35).scale(1 / 1.15), at=b, dur=0.45)
    light(row[0], T.times2 - 0.25, T.half_sq - 0.75)
    light(row[1], T.half_sq - 0.3, T.neg - 0.5)
    light(row[2], T.neg - 0.05)

    # ── "Lay every number out on a line." ──
    show = (T.line - 0.1, T.line + 0.9)
    S = keys((t0, 1.0), (T.stretches - 0.1, 1.0), (T.stretches + 1.3, 2.0, E),
             (T.half_sq - 1.2, 2.0), (T.half_sq - 0.4, 1.0, E),
             (T.half_sq + 0.1, 1.0), (T.half_sq + 1.3, 0.5, E),
             (T.neg - 0.6, 0.5), (T.neg + 0.4, 1.0, E), lead=0)
    R = keys((t0, 0.0), (T.swings - 0.2, 0.0), (T.swings + 1.8, PI, "in_out_sine"), lead=0)
    lab_out = (T.matter, T.matter + 0.7)

    def line(t):
        k = ramp(t, *show)
        s_ = S(t)
        return VGroup(ruler(k), numline(
            s_, R(t), k=k, half=0.2 + 15.8 * ease(t, *show),
            dot_k=lambda x: ramp(t, T.line + 0.3 + 0.1 * abs(x), T.line + 0.7 + 0.1 * abs(x)),
            lab_k=ramp(t, T.line + 0.6, T.line + 1.2) * (1 - ramp(t, *lab_out)),
            ghost=0.7 * min(1.0, abs(s_ - 1.0) * 4)))
    live(bg, line, (show[0], T.line + 1.6), (T.stretches - 0.2, T.neg + 0.5), (T.swings - 0.3, T.swings + 1.9),
         lab_out)

    # ── "Three goes to negative three. Negative two goes to two.": each travels half a turn ──
    hops = ((3, (T.three + 0.25, T.three + 1.55)), (-2, (T.neg2 + 0.1, T.neg2 + 1.4)))
    gone = (T.swings - 0.4, T.swings)

    def hop(t):
        g = VGroup()
        for x, (a, b) in hops:
            k = ramp(t, a - 0.3, a) * (1 - ramp(t, *gone))
            if k < 0.005:
                continue
            a0 = 0.0 if x > 0 else PI
            ang = a0 + PI * ease(t, a, b)
            r = abs(x)
            g.add(dashed_arc(O, r, a0, ang, C.turn, k))
            g.add(Dot([O[0] + r * np.cos(ang), O[1] + r * np.sin(ang), 0], radius=0.11, color=C.point).set_opacity(k))
            kl = ramp(t, b - 0.2, b + 0.2) * k
            if kl > 0.01:
                g.add(MathTex(str(-x), font_size=28, color=C.point).move_to([-x, NLY - 0.38, 0]).set_opacity(kl))
        return g
    live(bg, hop, (hops[0][1][0] - 0.3, hops[1][1][1] + 0.25), gone)

    # ── "Every number swings to the other side of zero.": the line turns half a turn through the plane ──
    tr_in = (T.swings - 0.25, T.swings + 0.1)

    def trails(t):
        k = 0.6 * ramp(t, *tr_in) * (1 - ramp(t, *lab_out))
        g = VGroup()
        for x in (-3, -2, -1, 1, 2, 3):
            a0 = 0.0 if x > 0 else PI
            g.add(dashed_arc(O, abs(x), a0, a0 + R(t), C.turn, k))
        return g
    live(bg, trails, (tr_in[0], T.swings + 1.9), lab_out)

    # ── "It is a half turn." ──
    harc = Arc(radius=0.7, start_angle=0, angle=PI, arc_center=[*O, 0], color=C.turn, stroke_width=C.stroke + 1)
    harc.add_tip(tip_length=0.2, tip_width=0.2)
    m.play(Create(harc), at=T.half_turn + 0.1, dur=0.9, ease=E)

    # ── "Remember that. Negative one is a half turn. It is going to matter.": planted top right ──
    pl = plant()
    m.play(FadeIn(pl[0]), TransformFromCopy(row[2], pl[1][0]), FadeIn(pl[1][1]),
           TransformFromCopy(harc, pl[1][2][0]), FadeIn(pl[1][2][1]), at=T.plant + 0.3, dur=1.1, ease=E)
    m.play(Indicate(pl, color=None, scale_factor=1.12), at=T.matter, dur=0.8)
    m.play(FadeOut(harc), at=T.matter + 0.2, dur=0.6)
