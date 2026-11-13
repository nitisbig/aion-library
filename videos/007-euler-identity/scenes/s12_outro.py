"""Outro · Read it one last time. The equation from s11 rises and turns back into e^{iπ} = −1. The six chapter
badges lift off the rail into a row; each lights as it is named (growth, quarter turn, sideways, the circle), the
Ch2 card returns on "what negative one means", and the bank, the sum and the picture each get a check. Then the
row dissolves into one unit circle and the point makes its last slow half walk onto −1. Last, a framed teaser:
a chain of turning arrows (aion.maths.fourier) draws a heart: where we go next. Fade to black."""
from aion import *
from aion.maths.fourier import centered, chain_points, coefficients, order_terms, partial_sum, resample

from beats import T
from shots import backdrop, backing, badge, ease, euler, identity, live, plant, rail, ramp, tex

E = "easy_ease"
EQ_AT = (0.0, -2.22)                                  # where s11 left e^{iπ} + 1 = 0
TOP = (0.0, 2.9)
ROW_Y = 0.75


def heart_terms(n=15):
    s = np.linspace(0, TAU, 400, endpoint=False)
    z = 16 * np.sin(s) ** 3 + 1j * (13 * np.cos(s) - 5 * np.cos(2 * s) - 2 * np.cos(3 * s) - np.cos(4 * s))
    z = centered(resample(z, 256)) / 17.0
    return order_terms(coefficients(z, n), "size")


@scene(T.cut_outro, T.end)
def s12_outro(s):
    backdrop(s)
    t0 = s.start
    m = s.manim(z=2)
    hb = s.manim(z=3, parallax=0.0)
    hud = s.manim(z=4, parallax=0.0)
    rl = rail(hud, 6)
    bs = [badge(k) for k in range(1, 7)]
    hud.add(*bs, at=t0)
    black = (T.end - 2.6, T.end - 0.6)

    # the equation, as s11 left it; it rises and reads as e^{iπ} = −1 again
    idn = identity(size=96).move_to([*EQ_AT, 0])
    eb = backing(idn, pad=0.18)
    hb.add(eb, at=t0)
    hud.add(idn, at=t0)
    eq = euler(size=96).move_to([*TOP, 0])
    eb2 = backing(eq, pad=0.18)
    up = T.one_last - 0.6
    hb.play(ReplacementTransform(eb, eb2), at=up, dur=1.4, ease=E)
    hud.play(ReplacementTransform(idn[0], eq[0]), ReplacementTransform(idn[1], eq[1]),
             ReplacementTransform(idn[2], eq[2]), ReplacementTransform(idn[5], eq[3]),
             ReplacementTransform(idn[3], eq[4]), ReplacementTransform(idn[4], eq[5], path_arc=PI * 0.8),
             FadeOut(idn[6]), at=up, dur=1.4, ease=E)

    # ── the badges lift into a row ──
    tgt = VGroup(*[b.copy().scale(1.6) for b in bs]).arrange(RIGHT, buff=0.6).move_to([0, ROW_Y, 0])
    lift = T.one_last + 0.4
    hold = T.one_last + 2.3
    hud.remove(*bs, at=lift)
    gone = T.o_eq - 0.2
    lit = {0: T.o_growth, 1: T.o_quarter, 2: T.o_sideways, 5: T.o_circle, 3: T.agree - 1.6, 4: T.agree - 1.6}

    def row(t):                                       # each badge dims, then lights on its word; then they gather
        g = VGroup()
        u = ease(t, gone, gone + 1.0)
        if u > 0.995:
            return g
        for j, b in enumerate(tgt):
            a = lit[j]
            k = 1.0 - 0.7 * ramp(t, hold, hold + 0.5) + 0.7 * ramp(t, a, a + 0.4)
            bump = 0.15 * np.sin(np.pi * np.clip((t - a - 0.3) / 0.7, 0, 1))
            v = ease(t, lift + 0.15 * j, lift + 0.15 * j + 1.1)          # off the rail, into the row
            c0 = (1 - v) * bs[j].get_center() + v * b.get_center()
            c = (1 - u) * c0 + u * np.array([0, -0.4, 0])
            sc = (1 - v) / 1.6 + v
            g.add(b.copy().scale(sc * (1 + bump) * (1 - 0.7 * u)).move_to(c).set_opacity(k * (1 - u)))
        return g
    live(hud, row, (lift, gone + 1.0))
    for j, gl in ((0, 0), (1, 1)):
        hud.play(Indicate(eq[gl], color=None, scale_factor=1.35), at=lit[j] + 0.1, dur=0.7)
    hud.play(Indicate(eq[2], color=None, scale_factor=1.35), at=T.o_dist + 0.1, dur=0.7)     # π is the distance

    # "a half turn is exactly what negative one means": the Ch2 card
    pl = plant().scale(1.25).move_to([0, -1.05, 0])
    hud.play(FadeIn(pl, shift=0.15 * UP), at=T.o_half + 0.2, dur=0.6)
    hud.play(Indicate(pl, color=None, scale_factor=1.12), at=T.o_neg1 + 0.2, dur=0.8)
    hud.play(Indicate(eq[4:], color=None, scale_factor=1.3), at=T.o_neg1 + 0.4, dur=0.7)

    # "The bank, the infinite sum, and the picture all agree.": checks under 4, 5 and 3
    checks = VGroup()
    for j in (3, 4, 2):
        c = tgt[j].get_bottom() + [0, -0.38, 0]
        checks.add(VMobject(stroke_color=C.arc, stroke_width=C.stroke + 1).set_points_as_corners(
            [c + [-0.16, 0.0, 0], c + [-0.04, -0.13, 0], c + [0.2, 0.17, 0]]))
    hud.play(LaggedStart(*[Create(c) for c in checks], lag_ratio=0.35), at=T.agree - 0.9, dur=1.2)

    # ── "e to the i pi equals negative one.": the row dissolves into one circle; the last half walk ──
    hud.play(FadeOut(checks), FadeOut(pl, shift=0.2 * DOWN), at=gone, dur=0.8)
    hud.play(Indicate(eq, color=None, scale_factor=1.08), at=T.o_eq + 0.2, dur=0.9)
    walk = (T.o_eq + 1.0, T.o_half_turn + 0.25)
    slide = (T.next_video + 0.1, T.next_video + 1.5)
    kc = (T.o_eq + 0.2, T.o_eq + 1.0)

    def circle(t):
        k = ramp(t, *kc) * (1 - ramp(t, *black))
        if k < 0.005:
            return VGroup()
        u = ease(t, *slide)
        c = np.array([-3.7 * u, -0.45 * (1 - u) - 0.35 * u, 0.0])
        R = 1.85 - 0.35 * u
        th = PI * ease(t, *walk)
        p = c + R * np.array([np.cos(th), np.sin(th), 0])
        g = VGroup(Line(c + [-R - 0.5, 0, 0], c + [R + 0.5, 0, 0], color=C.ghost, stroke_width=C.thin,
                        stroke_opacity=k),
                   Circle(radius=R, color=C.text, stroke_width=C.thin + 0.6).move_to(c).set_stroke(opacity=0.5 * k))
        if th > 0.02:
            g.add(Arc(radius=R, start_angle=0, angle=th, arc_center=c, color=C.arc, stroke_width=C.stroke + 2,
                      stroke_opacity=k))
        kh = ramp(t, T.o_half_turn - 0.1, T.o_half_turn + 0.7)
        if kh > 0.01:                                 # the half turn
            arc = Arc(radius=0.45 * R, start_angle=0, angle=PI * kh, arc_center=c, color=C.turn,
                      stroke_width=C.stroke, stroke_opacity=k)
            if kh > 0.3:
                arc.add_tip(tip_length=0.16, tip_width=0.16)
                arc.tip.set_fill(C.turn, opacity=k)
            g.add(arc)
            g.add(MathTex("-1", font_size=44, color=C.point).move_to(c + [-R - 0.45, 0.3, 0]).set_opacity(k * kh))
        g.add(Line(c, p, color=C.point, stroke_width=C.stroke, stroke_opacity=0.9 * k))
        g.add(Dot(p, radius=0.1, color=C.point).set_opacity(k))
        return g
    live(m, circle, kc, walk, (T.o_half_turn - 0.1, T.o_half_turn + 0.7), slide, black)

    # ── "…many of these turning arrows added together… the Fourier series…" a framed teaser ──
    terms = heart_terms(15)
    PC, PW_, PH_ = np.array([3.25, -0.35, 0]), 5.2, 4.3
    SC = 1.45
    draw = (T.next_video + 1.3, T.going_next + 0.6)
    kf = (T.next_video + 0.6, T.next_video + 1.3)

    def teaser(t):
        k = ramp(t, *kf) * (1 - ramp(t, *black))
        if k < 0.005:
            return VGroup()
        g = VGroup(Rectangle(width=PW_, height=PH_, stroke_color=C.frame, stroke_width=C.thin, fill_color=C.bg,
                             fill_opacity=k).move_to(PC).set_stroke(opacity=k))
        tau = 0.999 * ease(t, *draw) if t < draw[1] else 0.999
        cz = PC + [0, -0.25, 0]

        def Wz(z):
            return cz + SC * np.array([z.real, z.imag, 0])
        if tau > 0.002:
            ts = np.linspace(0, tau, max(4, int(tau * 300)))
            path = partial_sum(terms, ts)
            g.add(VMobject(stroke_color=C.point, stroke_width=C.stroke + 1, stroke_opacity=k)
                  .set_points_smoothly([Wz(z) for z in path]))
        joints = chain_points(terms, tau)
        ka = k * (1 - 0.6 * ramp(t, draw[1] - 0.6, draw[1]))
        for (n, cn), a, b in zip(terms, joints[:-1], joints[1:]):
            r = abs(cn) * SC
            if r > 0.02:
                g.add(Circle(radius=r, color=C.ghost, stroke_width=C.thin * 0.8).move_to(Wz(a))
                      .set_stroke(opacity=0.8 * ka))
            if r > 0.01:
                g.add(Line(Wz(a), Wz(b), color=C.turn if n != 0 else C.muted, stroke_width=C.thin + 0.8,
                           stroke_opacity=ka))
        g.add(Dot(Wz(joints[-1]), radius=0.05, color=C.point).set_opacity(k))
        lab = tex(r"\sum", r"c_n", r"e^{int}", size=40)
        lab[2][1].set_color(C.turn)
        lab[0].set_color(C.muted)
        g.add(lab.move_to(PC + [0, PH_ / 2 - 0.42, 0]).set_opacity(k))
        return g
    live(m, teaser, kf, draw, black)

    # fade to black
    hud.play(FadeOut(VGroup(eq, *rl)), at=black[0], dur=black[1] - black[0])
    hb.play(FadeOut(eb2), at=black[0], dur=black[1] - black[0])
