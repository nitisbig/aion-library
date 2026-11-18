"""s06 line flow (ch1): e^x seen sideways. Every point x on the number line moves with velocity x (orange arrows);
run that motion for one second and every point is multiplied by e: 1 → e, 2 → 2e, −1 → −e, 0 stays. e is the
stretch of one second of this flow. Speed it up by r and t seconds stretch by e^{rt}; make r negative and the line
drains toward zero, like the coffee's extra heat."""
from aion import *

from beats import T
from shots import E, backdrop, backed, chapter_card, finish, heat_color, lab, live, p3, plot, tex

LY, LU, LX0 = -0.7, 1.12, -1.4                        # the line's height, unit, and where 0 sits
XS = [-1.0, 0.0, 1.0, 2.0]                            # the four marked points
ARROW_X = [x / 2 for x in range(-7, 12) if x != 0]   # arrow lattice (every half unit, inside the line)


def X(x):
    return np.array([LX0 + LU * x, LY])


@scene(T.cut_ch1, T.cut_steps)
def s06_line_flow(s):
    backdrop(s)
    m0 = s.manim(z=0)
    m = s.manim(z=2)
    chapter_card(m, 1, "Growth that feeds on itself", r"e^{rt}", T.cut_ch1)

    # ── the number line ──
    line = NumberLine(x_range=[-4, 6, 1], length=10 * LU, color=C.text, stroke_width=C.thin + 0.6,
                      include_tip=False, tick_size=0.07).move_to(p3(X(1.0)))
    nums = VGroup(*[tex(str(k), size=30, color=C.muted).move_to(p3(X(k) + [0, -0.42])) for k in range(-4, 7)])
    m.play(Create(line), FadeIn(nums, lag_ratio=0.05), at=T.sideways, dur=1.2, ease=E)

    # ── the flow: log-stretch L(t) and rate r(t) ──
    t_p0, t_p1 = T.play + 0.6, T.play + 2.6           # one unit of flow time, played over two seconds
    t_n0, t_n1 = T.negative + 1.4, T.negative + 4.2
    L = keys((t_p0, 0.0), (t_p1, 1.0, "linear"), (T.speed_r + 0.1, 1.0), (T.speed_r + 1.0, 0.0, E),
             (t_n0, 0.0), (t_n1, -2.0, "linear"), lead=0)
    r = keys((T.speed_r + 1.4, 1.0), (T.speed_r + 2.6, 2.0, E), (T.negative - 0.2, 2.0), (T.negative + 1.0, -1.0, E),
             lead=0)
    a_op = keys((T.vel_eq - 0.2, 0.0), (T.vel_eq + 0.8, 1.0), (T.cut_steps - 0.6, 1.0), (T.cut_steps - 0.1, 0.0),
                lead=0)

    def arrows(t):
        rr, a = float(r(t)), float(a_op(t))
        out = VGroup()
        for x in ARROW_X:
            v = rr * x
            if abs(v) < 1e-6 or a < 0.01:
                continue
            Ln = np.sign(v) * 0.46 * LU * np.tanh(abs(v) / 2.2)     # grows with speed, never reaches the next arrow
            p = X(x) + [0, 0.42]
            out.add(Arrow(p3(p), p3(p + [Ln, 0]), buff=0, color=C.gen, stroke_width=C.stroke - 0.5,
                          tip_length=min(0.16, 0.45 * abs(Ln)), max_tip_length_to_length_ratio=0.45,
                          max_stroke_width_to_length_ratio=40).set_opacity(a))
        return out
    live(m0, arrows, (T.vel_eq - 0.2, T.vel_eq + 0.85), (T.speed_r + 1.4, T.speed_r + 2.65),
         (T.negative - 0.2, T.negative + 1.05), (T.cut_steps - 0.6, T.cut_steps - 0.05))

    # ── the rule, at the top ──
    rule = tex(r"\dot x", "=", r"x", size=64, colors={0: C.gen, 2: C.vec}).move_to([0, 2.85, 0])
    m.play(FadeIn(rule, shift=0.1 * DOWN), at=T.vel_eq + 0.4, dur=0.7)

    # ── the marked points and their speeds ──
    appear = {2.0: T.at_two, -1.0: T.at_minus_one, 0.0: T.zero_put, 1.0: T.play - 0.6}
    d_op = {x: keys((appear[x] - 0.1, 0.0), (appear[x] + 0.4, 1.0), (T.cut_steps - 0.6, 1.0),
                    (T.cut_steps - 0.1, 0.0), lead=0) for x in XS}

    def dots(t):
        k = np.exp(float(L(t)))
        out = VGroup()
        for x in XS:
            a = float(d_op[x](t))
            if a < 0.01:
                continue
            if x == 0:
                out.add(Circle(radius=0.11, color=C.text, stroke_width=C.stroke).move_to(p3(X(0))).set_stroke(opacity=a))
            else:
                out.add(Dot(p3(X(x * k)), radius=0.11, color=C.vec).set_opacity(a))
        return out
    live(m0, dots, *[(appear[x] - 0.1, appear[x] + 0.45) for x in XS], (t_p0, t_p1 + 0.05),
         (T.speed_r + 0.1, T.speed_r + 1.05), (t_n0, t_n1 + 0.05), (T.cut_steps - 0.6, T.cut_steps - 0.05))
    speeds = {}
    for x, at in ((2.0, T.at_two), (-1.0, T.at_minus_one), (0.0, T.zero_put)):
        lbl = tex(r"\dot x", "=", f"{int(x)}", size=36, colors={0: C.gen, 2: C.gen})
        lbl.move_to(p3(X(x) + [0, 1.75 if x == 0 else 1.15]))
        lbl = backed(lbl, buff=0.06)
        speeds[x] = lbl
        m.play(FadeIn(lbl, shift=0.1 * DOWN), at=at + 0.5, dur=0.5)
    m.play(FadeOut(VGroup(*speeds.values())), at=T.play - 0.3, dur=0.5)

    # ── press play for one second ──
    clock = VGroup(tex("t", "=", size=44, colors={0: C.flow}), DecimalNumber(0, num_decimal_places=2, font_size=44,
                                                                             color=C.flow)).arrange(RIGHT, buff=0.15)
    clock.move_to([4.6, 2.85, 0])
    m.add(clock, at=T.play + 0.1)
    m.drive(clock, lambda c, t: c[1].set_value(float(np.clip(L(t), 0, 1))), during=(T.play + 0.1, t_p1 + 0.05))
    m.play(FadeIn(clock), at=T.play + 0.2, dur=0.4)
    ghosts = VGroup(*[Dot(p3(X(x)), radius=0.11, color=C.vec).set_opacity(0.3) for x in XS if x != 0])
    m.add(ghosts, at=t_p0)

    arc_op = keys((T.speed_r - 0.15, 1.0), (T.speed_r + 0.35, 0.0), lead=0)

    def arcs(t):
        k = np.exp(float(np.clip(L(t), 0, 1)))
        a_ = float(arc_op(t))
        out = VGroup()
        for x in XS:
            if x == 0 or k < 1.001:
                continue
            a, b = X(x), X(x * k)
            out.add(ArcBetweenPoints(p3(a + [0, 0.14]), p3(b + [0, 0.14]), angle=-0.9 * np.sign(x) if x > 0 else 0.9,
                                     color=C.flow, stroke_width=C.thin + 0.6).set_stroke(opacity=a_))
        return out
    live(m, arcs, (t_p0, t_p1 + 0.05), (T.speed_r - 0.15, T.speed_r + 0.4))
    e_t = VGroup(Line(p3(X(np.e) + [0, -0.12]), p3(X(np.e) + [0, 0.12]), color=C.flow, stroke_width=C.stroke),
                 tex("e", size=40, color=C.flow).move_to(p3(X(np.e) + [0, -0.85])))
    e2_t = tex("2e", size=40, color=C.flow).move_to(p3(X(2 * np.e) + [0, -0.85]))
    me_t = tex("-e", size=40, color=C.flow).move_to(p3(X(-np.e) + [0, -0.85]))
    m.play(FadeIn(e_t, shift=0.1 * UP), at=T.lands_e + 0.2, dur=0.5)
    m.play(FadeIn(e2_t, shift=0.1 * UP), FadeIn(me_t, shift=0.1 * UP), at=T.two_e + 0.3, dur=0.5)

    # ── the same factor for everyone: e is the stretch ──
    times = VGroup(*[backed(tex(r"\times e", size=34, color=C.flow), buff=0.05).move_to(
        p3((X(x) + X(x * np.e)) / 2 + [0, 0.95 if x > 0 else -1.55 + 2.1])) for x in (1.0, 2.0, -1.0)])
    m.play(LaggedStart(*[FadeIn(tm, scale=0.8) for tm in times], lag_ratio=0.25), at=T.two_e + 1.9, dur=1.0)
    stretch = tex(r"x_0", r"\;\longmapsto\;", r"e", r"\,x_0", size=56, colors={0: C.vec, 2: C.flow, 3: C.vec})
    stretch.move_to([0, 1.75, 0])
    m.play(FadeIn(stretch, shift=0.1 * DOWN), at=T.stretch + 0.4, dur=0.7)

    # ── speed it up by r: e^{rt} ──
    fade_old = VGroup(times, ghosts, e2_t, me_t, stretch, clock)
    m.play(FadeOut(fade_old), at=T.speed_r - 0.1, dur=0.5)
    rule2 = tex(r"\dot x", "=", r"r", r"\,x", size=64, colors={0: C.gen, 2: C.gen, 3: C.vec}).move_to(rule)
    m.play(TransformMatchingTex(rule, rule2), at=T.speed_r + 0.3, dur=0.8)
    rr = VGroup(tex("r", "=", size=44, colors={0: C.gen}), DecimalNumber(1.0, num_decimal_places=1, font_size=44,
                                                                         color=C.gen)).arrange(RIGHT, buff=0.15)
    rr.move_to([4.6, 2.85, 0])
    m.add(rr, at=T.speed_r + 1.0)
    m.play(FadeIn(rr), at=T.speed_r + 1.1, dur=0.4)
    m.drive(rr, lambda c, t: c[1].set_value(float(r(t))), during=(T.speed_r + 1.2, T.negative + 1.1))
    sol = tex(r"x(t)", "=", r"e^{rt}", r"\,x_0", size=56, colors={0: C.vec, 2: C.flow, 3: C.vec})
    sol[2][1].set_color(C.gen)
    sol.move_to([0, 1.75, 0])
    m.play(FadeIn(sol, shift=0.1 * DOWN), at=T.speed_r + 3.0, dur=0.7)

    # ── r negative: the line drains toward zero, like the coffee's extra heat ──
    CO, CWd, CHt = np.array([-6.4, 1.45]), 2.0, 1.15
    coffee = VGroup(plot(lambda u: np.exp(-u), 0, 4, CO, CWd / 4, CHt, C.heat, width=C.stroke - 0.5),
                    Line(p3(CO), p3(CO + [CWd, 0]), color=C.muted, stroke_width=C.thin),
                    Line(p3(CO), p3(CO + [0, CHt * 1.05]), color=C.muted, stroke_width=C.thin),
                    lab("coffee", 24, C.heat).move_to(p3(CO + [CWd / 2, CHt + 0.3])))
    coffee[0].set_stroke(color=[C.cool, C.warm, C.heat])
    m.play(FadeIn(coffee, shift=0.1 * RIGHT), at=T.negative + 2.3, dur=0.6)
    m.play(FadeOut(coffee), at=T.cut_steps - 0.9, dur=0.5)
    m.play(FadeOut(VGroup(rule2, rr, sol)), at=T.cut_steps - 0.4, dur=0.5)   # the line and e stay for s07
    finish(s)
