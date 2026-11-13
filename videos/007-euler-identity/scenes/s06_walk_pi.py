"""Ch3 (cont.) · The payoff. The circling field from s05 settles into one unit circle. e^{it}: walk along the unit
circle a distance t. Pause and predict: back at 1, a ? blinks at −1 through the silence. A full lap is 2π, so half
is π (the upper half stays green). The point walks π and lands on −1; the title becomes e^{iπ} = −1 with π flying
off the arc and −1 off the point. A half turn: the red half arc, and the Ch2 card pulses. "A picture can fool
you": the drawing goes dashed and two empty check slots open on the rail. Badge v = ix."""
from aion import *

from beats import T
from shots import (O3, U3, PLANT, arrow, backdrop, backing, badge, badges, ease, euler, exposure_layer, flow_alpha,
                   flow_layer, glyphs, live, plane_grid, plant, rail, ramp, tex, walker)

E = "easy_ease"
PI_LAB = 40 * DEGREES                                 # where the π label sits on the arc
LAND = dict(center=(-0.4, -0.3), zoom=1.08)


def P3(z):
    z = complex(z)
    return np.array([O3[0] + U3 * z.real, O3[1] + U3 * z.imag, 0.0])


def to_screen(p, c, z):
    return np.array([(p[0] - c[0]) * z, (p[1] - c[1]) * z, 0.0])


@scene(T.cut_walk, T.cut_ch4)
def s06_walk_pi(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=2)
    m = s.manim(z=3)
    hb = s.manim(z=4, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)
    rail(hud, 3)
    badges(hud, 2)
    end_out = (T.cut_ch4 - 0.9, T.cut_ch4 - 0.2)

    # the field from s05 keeps circling, then fades as the camera returns
    settle = (t0 + 0.3, T.meaning + 0.4)
    s.camera.push(t0, zoom=0.82, dur=0.05, lead=0)
    s.camera.push(settle[0] + 0.2, zoom=1.0, dur=1.8, lead=0)
    s.add(flow_layer(flow_alpha(), fade(t0, to=1.0, dur=0.01, out=settle[1], out_dur=settle[1] - settle[0])))
    s.add(exposure_layer(fade(t0, to=0.4, dur=0.01, out=settle[1] - 0.4, out_dur=1.2)))

    # HUD carried over: v = ix (top left) and e^{it} (top centre)
    vix = glyphs(r"v=ix", {0: C.vel, 2: C.turn, 3: C.point}, size=58, n=4).move_to([-5.2, 2.95, 0])
    vback = backing(vix, pad=0.2)
    eit = glyphs(r"e^{it}", {0: C.growth, 1: C.turn, 2: C.arc}, size=96, n=3).move_to([0, 2.95, 0])
    eback = backing(eit, pad=0.22)
    hb.add(vback, eback, at=t0)
    hud.add(vix, eit, at=t0)

    def stage(t):                                     # the plane and a faint unit circle
        k = 1 - 0.6 * ramp(t, T.fool, T.fool + 0.8)
        k *= 1 - ramp(t, *end_out)
        g = plane_grid(O3, U3 / 2, box=(-9.6, -5.6, 9.6, 5.6), n=16, minor=1, opacity=0.45 * k)
        kc = ramp(t, settle[0], settle[1]) * (1 - ramp(t, T.fool, T.fool + 0.6)) * (1 - ramp(t, *end_out))
        g.add(Circle(radius=U3, color=C.ghost, stroke_width=C.thin + 0.5).move_to([*O3, 0]).set_stroke(opacity=kc))
        return g
    live(bg, stage, (t0, settle[1]), (T.fool, T.fool + 0.8), end_out)

    # ── "Walk along the unit circle, a distance t." · "pause and predict" (back to 1) · the walk to π ──
    th = keys((t0, 0.0), (T.walk + 0.2, 0.0), (T.dist_t + 0.8, 1.25, E), (T.predict - 0.1, 1.25),
              (T.predict + 1.1, 0.0, E), (T.after_pi + 0.1, 0.0), (T.lands_neg1 + 0.6, PI, "in_out_sine"), lead=0)
    w_in = (T.meaning - 0.2, T.meaning + 0.4)

    def walk(t):
        k = ramp(t, *w_in) * (1 - ramp(t, T.fool, T.fool + 0.6) * 0.55) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return VGroup()
        return walker(O3, U3, th(t), k=k)
    live(m, walk, w_in, (T.walk + 0.2, T.predict + 1.1), (T.after_pi + 0.1, T.lands_neg1 + 0.6),
         (T.fool, T.fool + 0.6), end_out)

    kr_in, kr_hold = (T.walk, T.walk + 0.5), (T.predict + 1.1, T.predict + 1.6)

    def readout(t):                                   # t, the distance walked
        k = ramp(t, *kr_in) * (1 - ramp(t, *kr_hold)) + ramp(t, T.after_pi - 0.3, T.after_pi + 0.2) * \
            (1 - ramp(t, T.eq_pay - 0.2, T.eq_pay + 0.3))
        if k < 0.005:
            return VGroup()
        row = VGroup(tex("t", "=", size=44, colors={0: C.arc}),
                     DecimalNumber(th(t), num_decimal_places=2, font_size=44, color=C.arc)).arrange(RIGHT, buff=0.15)
        row.move_to([-6.6, 1.95, 0], aligned_edge=UL)
        return VGroup(backing(row, pad=0.18), row).set_opacity(k)
    live(hb, readout, (kr_in[0], kr_hold[1]), (T.after_pi - 0.3, T.lands_neg1 + 0.6), (T.eq_pay - 0.2, T.eq_pay + 0.3))

    # ── "How far do we have to walk to reach negative one?" a ? blinks at −1 through the silence ──
    q_in, q_out = (T.how_far - 0.3, T.how_far + 0.3), (T.lands_neg1 - 0.3, T.lands_neg1 + 0.2)

    def ask(t):
        k = ramp(t, *q_in) * (1 - ramp(t, *q_out))
        if k < 0.005:
            return VGroup()
        b = 0.65 + 0.35 * np.cos(TAU * (t - q_in[1]) / 1.4)
        p = P3(-1)
        return VGroup(Circle(radius=0.16, color=C.point, stroke_width=C.thin + 1).move_to(p).set_stroke(opacity=k),
                      MathTex("?", font_size=64, color=C.point).move_to(p + [-0.5, 0.45, 0]).set_opacity(k * b))
    live(m, ask, (q_in[0], q_out[1]))

    # ── "Halfway around a circle of radius one." the radius, 1 ──
    r_k = (T.halfway + 0.2, T.halfway + 0.7)
    rl = MathTex("1", font_size=40, color=C.text).move_to(P3(0.5) + [0, -0.32, 0])
    m.play(FadeIn(rl), at=r_k[1], dur=0.5)
    m.play(FadeOut(rl), at=T.two_pi + 0.2, dur=0.5)

    # ── "The full way around is two pi. So halfway, is pi." ──
    lap = (T.two_pi + 0.1, T.two_pi + 1.6)
    half = (T.halfway_pi + 0.1, T.halfway_pi + 0.8)
    lap_out = (T.after_pi - 0.2, T.after_pi + 0.4)

    def tape(t):
        a = TAU * ease(t, *lap)
        k = 1 - ramp(t, *lap_out)
        if a < 0.02 or k < 0.005:
            return VGroup()
        lo = 1 - 0.85 * ramp(t, *half)
        g = VGroup(Arc(radius=U3, start_angle=0, angle=min(a, PI), arc_center=[*O3, 0], color=C.arc,
                       stroke_width=C.stroke + 2, stroke_opacity=k))
        if a > PI:
            g.add(Arc(radius=U3, start_angle=PI, angle=a - PI, arc_center=[*O3, 0], color=C.arc,
                      stroke_width=C.stroke + 2, stroke_opacity=k * lo))
        k2 = ramp(t, lap[1] - 0.2, lap[1] + 0.3) * (1 - ramp(t, *half))
        if k2 > 0.01:
            g.add(MathTex(r"2\pi", font_size=50, color=C.arc).move_to(P3(1.32 * np.exp(-0.8j))).set_opacity(k2 * k))
        return g
    live(m, tape, lap, half, lap_out)
    pi_lab = MathTex(r"\pi", font_size=60, color=C.arc).move_to(P3(1.22 * np.exp(1j * PI_LAB)))
    m.play(FadeIn(pi_lab, scale=1.4), at=half[0] + 0.2, dur=0.6)

    # ── "After walking a distance pi, the point lands on negative one." ──
    s.camera.frame(T.lands_neg1 - 0.2, dur=1.6, **LAND)
    ring = Circle(radius=0.16, color=C.point, stroke_width=C.thin + 1.5).move_to(P3(-1))
    m.play(FadeIn(ring, scale=0.5), at=T.lands_neg1 + 0.55, dur=0.2)
    m.play(FadeOut(ring, scale=3.0), at=T.lands_neg1 + 0.85, dur=0.8)

    # ── "e to the i pi equals negative one." π flies off the arc, −1 off the point ──
    eq = euler(size=96).move_to([0, 2.95, 0])
    eback2 = backing(eq, pad=0.22)
    src_pi = to_screen(pi_lab.get_center(), LAND["center"], LAND["zoom"])
    src_m1 = to_screen(P3(-1), LAND["center"], LAND["zoom"])
    hb.play(ReplacementTransform(eback, eback2), at=T.eq_pay - 0.1, dur=0.6)
    hud.play(ReplacementTransform(eit[0], eq[0]), ReplacementTransform(eit[1], eq[1]), FadeOut(eit[2]),
             at=T.eq_pay - 0.1, dur=0.6)
    hud.play(FadeIn(eq[2], target_position=src_pi, scale=0.6), at=T.eq_pay + 0.6, dur=0.8, ease=E)
    hud.play(FadeIn(eq[3:], target_position=src_m1, scale=0.6), at=T.eq_pay + 1.4, dur=0.9, ease=E)

    # ── "A half turn. Which is exactly what we said negative one is." ──
    harc = Arc(radius=0.5 * U3, start_angle=0, angle=PI, arc_center=[*O3, 0], color=C.turn, stroke_width=C.stroke + 1)
    harc.add_tip(tip_length=0.2, tip_width=0.2)
    m.play(Create(harc), at=T.half_pay + 0.1, dur=0.9, ease=E)
    pl = plant()
    hud.play(FadeIn(pl, shift=0.15 * DOWN), at=T.half_pay - 0.3, dur=0.6)
    hud.play(Indicate(pl, color=None, scale_factor=1.15), at=T.exactly + 0.5, dur=0.9)
    m.play(Indicate(harc, color=None, scale_factor=1.08), at=T.exactly + 0.5, dur=0.9)

    # ── "That is the picture. But a picture can fool you. So let us check it, twice, using nothing but arithmetic." ──
    s.camera.frame(T.the_picture, center=(0.0, 0.0), zoom=1.0, dur=1.4)
    dashed = DashedVMobject(Circle(radius=U3, color=C.muted, stroke_width=C.thin + 1).move_to([*O3, 0]),
                            num_dashes=60, dashed_ratio=0.5)
    m.play(Create(dashed), at=T.fool + 0.1, dur=1.0)
    m.play(FadeOut(VGroup(harc, pi_lab)), at=T.fool + 0.1, dur=0.6)
    slots = VGroup(*[DashedVMobject(RoundedRectangle(width=1.0, height=0.46, corner_radius=0.06, color=C.muted,
                                                     stroke_width=C.thin + 0.6), num_dashes=22)
                     .move_to(badge(k)).align_to(badge(k), LEFT).shift(0.08 * LEFT) for k in (4, 5)])
    hud.play(LaggedStart(*[Create(x) for x in slots], lag_ratio=0.4), at=T.check + 0.4, dur=1.2)
    hud.play(Indicate(slots, color=C.text, scale_factor=1.08), at=T.arithmetic + 0.3, dur=0.8)

    # badge v = ix; the stage clears for Ch4 (the slots and the equation stay with the rail and the story)
    hud.play(ReplacementTransform(vix, badge(3)), at=T.cut_ch4 - 1.05, dur=0.8, ease=E)
    hb.play(FadeOut(vback), at=T.cut_ch4 - 1.05, dur=0.5)
    hud.play(FadeOut(VGroup(eq, pl)), at=end_out[0], dur=0.6)
    hb.play(FadeOut(eback2), at=end_out[0], dur=0.6)
    m.play(FadeOut(dashed), at=end_out[0], dur=0.6)
