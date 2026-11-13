"""Ch2 (cont.) · The quarter turn. "What action, done twice, gives a half turn?" (×? ×? = ×(−1)). Two stretches
only stretch further (×2 ×2 = ×4 ≠ ×(−1)). A quarter turn, done twice, lays the line flat again, reversed: the ?s
become quarter-turn arrows. The line becomes the plane (the grid draws outward from 0 over a faint color wheel,
the camera moves in), arrows point every way, and i is the quarter turn: 1 → i → −1 → −i → 1 with red quarter
arcs. i·i = −1. Then multiplying by i turns the whole plane: grid, color wheel and a fan of arrows rotate 90°
together, ghosts marking where they were. Badge ×i = ↺."""
from aion import *

from beats import T
from shots import (NLY, PLANT, action_row, backdrop, backing, badge, badges, dashed_arc, ease, glyphs, live,
                   numline, plane_grid, plant, rail, ramp, ruler, tex)

E = "easy_ease"
O = (0.0, NLY)
BOX = (-7.6, -4.4, 7.6, 4.4)


def at_angle(r, a):
    return np.array([O[0] + r * np.cos(a), O[1] + r * np.sin(a), 0.0])


@scene(T.cut_quarter, T.cut_ch3)
def s04_quarter(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)                                 # grid
    m = s.manim(z=2)                                  # line, arrows, arcs
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 2)
    badges(hud, 1)
    end_out = (T.cut_ch3 - 0.9, T.cut_ch3 - 0.2)

    # the state Ch2 left: the action row (×(−1) lit) and the plant
    row = action_row()
    for j, tok in enumerate(row):
        tok.set_opacity(1.0 if j == 2 else 0.35)
    row[2].scale(1.15)
    pl = plant()
    hud.add(row, pl, at=t0)
    hud.play(FadeOut(row, shift=0.15 * UP), at=T.question - 0.3, dur=0.6)

    # ── "What action, done twice, gives a half turn?" ──
    eq = tex(r"\times\,?", r"\times\,?", "=", r"\times(-1)", size=64)
    eq[0][1].set_color(C.turn)
    eq[1][1].set_color(C.turn)
    eq[3][2:4].set_color(C.point)
    eq.arrange(RIGHT, buff=0.3).move_to([-0.6, 2.95, 0])
    back = backing(eq, pad=0.25)
    hud.play(FadeIn(back), FadeIn(eq[0], shift=0.1 * DOWN), at=T.twice - 0.1, dur=0.5)
    hud.play(FadeIn(eq[1], shift=0.1 * DOWN), at=T.twice + 0.6, dur=0.5)
    hud.play(FadeIn(eq[2:], shift=0.1 * DOWN), at=T.twice + 1.4, dur=0.6)
    hud.play(Indicate(pl, color=None, scale_factor=1.1), at=T.twice + 1.9, dur=0.8)

    # ── "Not a stretch. Two stretches only stretch further." ──
    ns = tex(r"\times2", r"\times2", "=", r"\times4", r"\neq", r"\times(-1)", size=46, color=C.muted)
    ns[5][2:4].set_color(C.point)
    ns.arrange(RIGHT, buff=0.18).move_to([-0.6, 1.95, 0])
    hud.play(FadeIn(ns[0]), at=T.not_stretch + 0.2, dur=0.5)
    hud.play(FadeIn(ns[1]), at=T.further + 0.1, dur=0.5)
    hud.play(FadeIn(ns[2:]), at=T.further + 0.9, dur=0.6)
    hud.play(FadeOut(ns), at=T.quarter - 0.2, dur=0.5)

    S = keys((t0, 1.0), (T.not_stretch + 0.1, 1.0), (T.not_stretch + 1.1, 2.0, E),
             (T.further + 0.1, 2.0), (T.further + 1.1, 4.0, E), (T.quarter - 0.45, 4.0), (T.quarter + 0.2, 1.0, E),
             lead=0)
    # ── "But a quarter turn, done twice, is a half turn." ──
    q1 = (T.quarter + 0.3, T.quarter + 1.6)
    q2 = (T.quarter + 2.0, T.quarter + 3.3)
    R = keys((t0, 0.0), (q1[0], 0.0), (q1[1], PI / 2, E), (q2[0], PI / 2), (q2[1], PI, E),
             (T.plane - 0.06, PI), (T.plane - 0.05, 0.0, "linear"), lead=0)   # π ≡ 0: the dots are symmetric
    line_out = (T.plane + 1.4, T.plane + 2.2)
    rul_out = (T.plane, T.plane + 0.8)

    def line(t):
        k = 1 - ramp(t, *line_out)
        kd = 1 - ramp(t, T.plane + 0.9, T.plane + 1.6)
        g = VGroup(ruler(1 - ramp(t, *rul_out)),
                   numline(S(t), R(t), k=k, dot_k=lambda x: kd, ghost=0.7 * min(1.0, abs(S(t) - 1.0) * 4)))
        kt = 0.6 * ramp(t, q1[0] - 0.2, q1[0]) * (1 - ramp(t, T.plane - 0.6, T.plane - 0.1))
        for x in (3, -3):
            a0 = 0.0 if x > 0 else PI
            g.add(dashed_arc(O, 3, a0, a0 + R(t) if t < T.plane - 0.06 else a0 + PI, C.turn, kt))
        return g
    live(m, line, (t0, t0 + 0.05), (T.not_stretch, q2[1] + 0.05), (T.plane - 0.6, line_out[1]))

    # the ?s become quarter turns, one per quarter
    qs = [MathTex(r"\circlearrowleft", font_size=64, color=C.turn).move_to(eq[j][1]) for j in (0, 1)]
    hud.play(ReplacementTransform(eq[0][1], qs[0]), at=q1[1] - 0.2, dur=0.6)
    hud.play(ReplacementTransform(eq[1][1], qs[1]), at=q2[1] - 0.2, dur=0.6)
    hud.play(Indicate(pl, color=None, scale_factor=1.1), at=q2[1] + 0.3, dur=0.8)

    # ── "So let the line become a plane, where numbers can point in any direction." ──
    s.camera.frame(T.plane + 0.2, center=(0.0, -0.55), zoom=1.6, dur=2.2)
    grow = (T.plane, T.plane + 2.6)
    turn = (T.whole + 0.4, T.ninety + 0.6)
    psi = keys((t0, 0.0), (turn[0], 0.0), (turn[1], PI / 2, E), lead=0)

    def grid(t):
        k = 0.6 * ramp(t, grow[0], grow[0] + 1.0) * (1 - ramp(t, *end_out))
        r = 0.3 + 9.0 * ease(t, *grow)
        box = (max(BOX[0], -r), max(BOX[1], O[1] - r), min(BOX[2], r), min(BOX[3], O[1] + r))
        return plane_grid(O, 1.0, box=box, turn=psi(t), n=12, minor=2, opacity=k)
    live(bg, grid, grow, turn, end_out)
    s.shader("plane.frag", z=0, u_origin=O, u_unit=1.0, u_theta=psi, u_sat=0.55, u_value=0.7,
             u_opacity=fade(T.plane + 0.8, to=0.22, dur=1.5, out=end_out[0], out_dur=0.7))

    fan_a = np.radians([20, 70, 125, 160, 210, 255, 320])

    def anyway(t):
        g = VGroup()
        for j, a in enumerate(fan_a):
            k = ramp(t, T.any_dir - 0.4 + 0.1 * j, T.any_dir + 0.0 + 0.1 * j) * (1 - ramp(t, T.i_quarter,
                                                                                        T.i_quarter + 0.6))
            if k > 0.005:
                g.add(Arrow([*O, 0], at_angle(1.3, a), buff=0, color=C.point, stroke_width=C.stroke,
                            tip_length=0.16).set_opacity(k))
        return g
    live(m, anyway, (T.any_dir - 0.4, T.any_dir + 0.7), (T.i_quarter, T.i_quarter + 0.6))

    # ── "i is the quarter turn": the ?s, now quarter turns, become i ──
    i_s = [MathTex("i", font_size=64, color=C.turn).move_to(eq[j][1]) for j in (0, 1)]
    hud.play(ReplacementTransform(qs[0], i_s[0]), ReplacementTransform(qs[1], i_s[1]), at=T.i_quarter + 0.3,
             dur=0.7)

    # ── "One goes to i … i goes to negative one … down to negative i, and then back to one." ──
    steps = [T.one_i, T.i_neg1, T.neg_i, T.back_one]
    phi = keys((t0, 0.0), *[f for j, b in enumerate(steps)
                            for f in ((b + 0.1, j * PI / 2), (b + 1.2, (j + 1) * PI / 2, E))], lead=0)
    cyc_out = (T.whole - 1.6, T.whole - 0.9)
    labs = [("1", C.text, 0.0, T.one_i - 0.6), ("i", C.turn, PI / 2, T.one_i + 1.0),
            ("-1", C.point, PI, T.i_neg1 + 1.0), ("-i", C.turn, 3 * PI / 2, T.neg_i + 1.0)]
    pulse = (T.two_quarters, T.two_quarters + 1.3)

    def cycle(t):
        ko = 1 - ramp(t, *cyc_out)
        g = VGroup()
        kc = ramp(t, T.plane + 2.0, T.plane + 2.8) * ko
        if kc < 0.005:
            return g
        g.add(Circle(radius=1.0, color=C.ghost, stroke_width=C.thin).move_to([*O, 0]).set_stroke(opacity=kc))
        f = phi(t)
        bump = np.sin(np.pi * np.clip((t - pulse[0]) / (pulse[1] - pulse[0]), 0, 1))
        for j in range(4):
            a = min(f, (j + 1) * PI / 2) - j * PI / 2
            if a > 0.06:
                w = C.stroke + (2.5 * bump if j < 2 else 0)
                arc = Arc(radius=1.0, start_angle=j * PI / 2, angle=a, arc_center=[*O, 0], color=C.turn,
                          stroke_width=w, stroke_opacity=ko)
                arc.add_tip(tip_length=0.14, tip_width=0.14)
                arc.tip.set_fill(C.turn, opacity=ko).set_stroke(opacity=ko)
                g.add(arc)
        for txt, col, a, t_in in labs:
            kl = ramp(t, t_in, t_in + 0.4) * ko
            if kl > 0.01:
                g.add(MathTex(txt, font_size=34, color=col).move_to(at_angle(1.38, a)).set_opacity(kl))
        ka = ramp(t, T.one_i - 0.8, T.one_i - 0.3) * ko
        if ka > 0.005:
            g.add(Arrow([*O, 0], at_angle(1.0, f), buff=0, color=C.point, stroke_width=C.stroke, tip_length=0.16)
                  .set_opacity(ka))
        return g
    live(m, cycle, (T.plane + 2.0, T.plane + 2.8), (T.one_i - 0.8, T.back_one + 1.4), pulse, cyc_out)

    # ── "i times i is negative one … two quarter turns make a half turn." ──
    ii = glyphs(r"i\cdot i=-1", {0: C.turn, 2: C.turn, 4: C.point, 5: C.point}, size=72, n=6).move_to(eq)
    back2 = backing(ii, pad=0.25)
    hud.play(FadeOut(VGroup(eq[0][0], i_s[0], eq[1][0], i_s[1], eq[2], eq[3], back), shift=0.25 * UP),
             at=T.ii + 0.1, dur=0.6)
    hud.play(FadeIn(VGroup(back2, ii), shift=0.25 * UP), at=T.ii + 0.6, dur=0.7)
    hud.play(Indicate(pl, color=None, scale_factor=1.12), at=T.two_quarters + 1.0, dur=0.8)

    # ── "And multiplying by i turns the whole plane. Every arrow, rotated ninety degrees." ──
    s.camera.frame(T.whole - 1.4, center=(0.0, 0.0), zoom=1.0, dur=1.4)
    zs = [r * np.exp(1j * a) for r, a in zip((1.6, 2.3, 1.6, 2.3, 1.6, 2.3, 1.6, 2.3),
                                             np.radians([10, 55, 100, 145, 190, 235, 280, 325]))]

    def fan(t):
        g = VGroup()
        k = ramp(t, T.whole - 0.5, T.whole + 0.2) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return g
        p_ = psi(t)
        for z in zs:
            r, a = abs(z), np.angle(z)
            if p_ > 0.02:
                g.add(Arrow([*O, 0], at_angle(r, a), buff=0, color=C.ghost, stroke_width=C.thin + 1,
                            tip_length=0.18).set_opacity(k))
                g.add(Arc(radius=r, start_angle=a, angle=p_, arc_center=[*O, 0], color=C.turn,
                          stroke_width=C.thin + 0.6, stroke_opacity=0.7 * k))
            g.add(Arrow([*O, 0], at_angle(r, a + p_), buff=0, color=C.point, stroke_width=C.stroke,
                        tip_length=0.2).set_opacity(k))
        return g
    live(m, fan, (T.whole - 0.5, T.whole + 0.2), turn, end_out)

    hud.play(ReplacementTransform(ii, badge(2)), FadeOut(back2), at=T.cut_ch3 - 1.05, dur=0.8, ease=E)
    hud.play(FadeOut(pl), at=T.cut_ch3 - 0.9, dur=0.6)
