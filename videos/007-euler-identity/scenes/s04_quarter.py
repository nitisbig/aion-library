"""Ch2 (cont.) · The quarter turn. "What action, done twice, gives a half turn?" (×? ×? = ×(−1)). Two stretches
only stretch further (×2 ×2 = ×4 ≠ ×(−1)). A quarter turn, done twice, lays the line flat again, reversed: the ?s
become quarter-turn arrows. The line becomes the plane (the grid draws outward from 0 over a faint color wheel,
the camera moves in), arrows point every way, and i is the quarter turn: 1 → i → −1 → −i → 1 with red quarter
arcs. i·i = −1. Then multiplying by i turns the whole plane: grid, color wheel and a fan of arrows rotate 90°
together, ghosts marking where they were. Badge ×i = ↺.

From "let the line become a plane" the plane is 3D (shots3d): the flat number line tilts away into a perspective
plane that unrolls outward from 0 (plane3d.frag), the camera drifts slowly round it, arrows float just above it
with crisp shadows, and on "turns the whole plane" it cranes to a low hero angle for the 90° turn, then rises."""
from aion import *

from beats import T
from shots import (NLY, PLANT, action_row, arrow, backdrop, backing, badge, badges, dashed_arc, glyphs, live,
                   numline, plant, rail, ramp, ruler, tex)
from shots3d import F0, TOP, Cam3, plane_uniforms

E = "easy_ease"
S_ = "in_out_sine"
O = (0.0, NLY)


def at_angle(r, a):
    return np.array([O[0] + r * np.cos(a), O[1] + r * np.sin(a), 0.0])


@scene(T.cut_quarter, T.cut_ch3)
def s04_quarter(s):
    backdrop(s)
    t0 = s.start
    glow = keys((t0, 0.0), (T.plane, 0.0), (T.plane + 2.0, 1.0, E), (T.cut_ch3 - 0.9, 1.0), (T.cut_ch3, 0.0), lead=0)
    m = s.manim(z=2, fx=[Glow(strength=0.45 * glow, radius=3)])     # line, arrows, arcs (a soft halo in 3D)
    s.fx(Bloom(strength=0.4 * glow, threshold=0.72, radius=5))
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
    line_out = (T.plane + 2.0, T.plane + 3.0)
    rul_out = (T.plane + 1.2, T.plane + 2.4)

    # ── the 3D camera: flat (identity) until the plane, then it tilts away, drifts, cranes, rises ──
    hero = (T.whole - 1.4, T.whole + 0.4)
    rise = (T.ninety + 0.9, T.cut_ch3)
    tilt = (T.plane + 0.15, T.plane + 3.2)
    cam = Cam3(
        yaw=keys((t0, 0.0), (tilt[0], 0.0), (tilt[1], np.radians(-16), E), (hero[0], np.radians(10), S_),
                 (hero[1], np.radians(18), E), (rise[0], np.radians(24), S_), (rise[1], 0.0, E), lead=0),
        pitch=keys((t0, TOP), (tilt[0], TOP), (tilt[1], np.radians(40), E), (hero[0], np.radians(36), S_),
                   (hero[1], np.radians(29), E), (rise[0], np.radians(29)), (rise[1], np.radians(70), E), lead=0),
        dist=keys((t0, F0), (tilt[0], F0), (tilt[1], 7.4, E), (hero[0], 7.0, S_), (hero[1], 8.6, E),
                  (rise[0], 8.6), (rise[1], 12.0, E), lead=0),
        tx=0.0, ty=O[1], fog=6.0,
        sx=0.0, sy=keys((t0, O[1]), (tilt[0], O[1]), (tilt[1], -0.75, E), (hero[0], -0.75),
                        (hero[1], -1.0, E), lead=0))
    v3 = (T.plane - 0.05, T.cut_ch3)                  # from here every overlay is drawn through the camera

    def line(t):
        k = 1 - ramp(t, *line_out)
        kd = 1 - ramp(t, T.plane + 1.6, T.plane + 2.6)
        g = VGroup(ruler(1 - ramp(t, *rul_out)),
                   numline(S(t), R(t), k=k, dot_k=lambda x: kd, ghost=0.7 * min(1.0, abs(S(t) - 1.0) * 4)))
        kt = 0.6 * ramp(t, q1[0] - 0.2, q1[0]) * (1 - ramp(t, T.plane - 0.6, T.plane - 0.1))
        for x in (3, -3):
            a0 = 0.0 if x > 0 else PI
            g.add(dashed_arc(O, 3, a0, a0 + R(t) if t < T.plane - 0.06 else a0 + PI, C.turn, kt))
        if t >= v3[0] and len(g):
            cam(t).flat(g, smooth=2)
        return g
    live(m, line, (t0, t0 + 0.05), (T.not_stretch, q2[1] + 0.05), (T.plane - 0.6, line_out[1]))

    # the ?s become quarter turns, one per quarter
    qs = [MathTex(r"\circlearrowleft", font_size=64, color=C.turn).move_to(eq[j][1]) for j in (0, 1)]
    hud.play(ReplacementTransform(eq[0][1], qs[0]), at=q1[1] - 0.2, dur=0.6)
    hud.play(ReplacementTransform(eq[1][1], qs[1]), at=q2[1] - 0.2, dur=0.6)
    hud.play(Indicate(pl, color=None, scale_factor=1.1), at=q2[1] + 0.3, dur=0.8)

    # ── "So let the line become a plane, where numbers can point in any direction." ──
    # the plane unrolls outward from 0 as the camera tilts away: grid first, then the color wheel under it
    turn = (T.whole + 0.4, T.ninety + 0.6)
    psi = keys((t0, 0.0), (turn[0], 0.0), (turn[1], PI / 2, E), lead=0)
    reveal = keys((t0, 0.0), (T.plane + 0.1, 0.0), (T.plane + 3.4, 16.0, "in_cubic"), lead=0)
    s.shader("plane3d.frag", z=0, **cam.uniforms(),
             **plane_uniforms(O, 1.0, 1.0, theta=psi, reveal=reveal, sat=0.55, value=0.75,
                              edge=fade(T.plane + 0.1, to=0.9, dur=0.3, out=T.plane + 2.6, out_dur=0.8),
                              lines=fade(T.plane - 0.05, to=1.0, dur=0.4, out=end_out[0], out_dur=0.8),
                              colors=fade(T.plane + 1.2, to=0.58, dur=1.8, out=end_out[0], out_dur=0.8)))

    def lifted(v, z, w=None, tip=0.16, h=0.07, k=1.0, color=None, shadow=0.55):
        """A yellow arrow 0 → z (plane units), floating at height h with its shadow on the plane."""
        a = arrow([*O, 0], [O[0] + z.real, O[1] + z.imag, 0], color or C.point, width=w or C.stroke, tip=tip)
        return v.lift(a.set_opacity(k), h=h, shadow=shadow * k)

    fan_a = np.radians([20, 70, 125, 160, 210, 255, 320])

    def anyway(t):
        g = VGroup()
        v = cam(t)
        for j, a in enumerate(fan_a):
            k = ramp(t, T.any_dir - 0.4 + 0.1 * j, T.any_dir + 0.0 + 0.1 * j) * (1 - ramp(t, T.i_quarter,
                                                                                        T.i_quarter + 0.6))
            if k > 0.005:
                g.add(lifted(v, 1.3 * np.exp(1j * a), k=k))
        return g
    live(m, anyway, (T.any_dir - 0.4, T.i_quarter + 0.6))

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
        v = cam(t)
        g.add(v.flat(Circle(radius=1.0, color=C.text, stroke_width=C.thin).move_to([*O, 0])
                     .set_stroke(opacity=0.45 * kc)))
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
                g.add(v.lift(arc, h=0.04, shadow=0.5 * ko))
        for txt, col, a, t_in in labs:
            kl = ramp(t, t_in, t_in + 0.4) * ko
            if kl > 0.01:
                p = (O[0] + 1.6 * np.cos(a), O[1] + 1.6 * np.sin(a))
                g.add(v.bill(MathTex(txt, font_size=32, color=col).set_opacity(kl), p, h=0.3, lo=0.9))
        ka = ramp(t, T.one_i - 0.8, T.one_i - 0.3) * ko
        if ka > 0.005:
            g.add(lifted(v, np.exp(1j * f), k=ka, h=0.09))
        return g
    live(m, cycle, (T.plane + 2.0, cyc_out[1]))

    # ── "i times i is negative one … two quarter turns make a half turn." ──
    ii = glyphs(r"i\cdot i=-1", {0: C.turn, 2: C.turn, 4: C.point, 5: C.point}, size=72, n=6).move_to(eq)
    back2 = backing(ii, pad=0.25)
    hud.play(FadeOut(VGroup(eq[0][0], i_s[0], eq[1][0], i_s[1], eq[2], eq[3], back), shift=0.25 * UP),
             at=T.ii + 0.1, dur=0.6)
    hud.play(FadeIn(VGroup(back2, ii), shift=0.25 * UP), at=T.ii + 0.6, dur=0.7)
    hud.play(Indicate(pl, color=None, scale_factor=1.12), at=T.two_quarters + 1.0, dur=0.8)

    # ── "And multiplying by i turns the whole plane. Every arrow, rotated ninety degrees." ──
    # the camera cranes low; grid, colors and a floating fan turn 90° together about a vertical axis at 0
    zs = [r * np.exp(1j * a) for r, a in zip((1.6, 2.3, 1.6, 2.3, 1.6, 2.3, 1.6, 2.3),
                                             np.radians([10, 55, 100, 145, 190, 235, 280, 325]))]

    def fan(t):
        g = VGroup()
        k = ramp(t, T.whole - 0.5, T.whole + 0.2) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return g
        v = cam(t)
        p_ = psi(t)
        kx = ramp(t, turn[0] - 0.4, turn[0] + 0.2) * (1 - ramp(t, turn[1] + 0.2, turn[1] + 0.9)) * k
        if kx > 0.005:                                # the axis the plane turns about
            g.add(v.post(O, 1.6, C.muted, opacity=0.8 * kx))
        for z in zs:
            r, a = abs(z), np.angle(z)
            if p_ > 0.02:
                g.add(v.flat(arrow([*O, 0], [O[0] + z.real, O[1] + z.imag, 0], C.ghost, width=C.thin + 1,
                                   tip=0.18).set_opacity(k)))
                g.add(v.lift(Arc(radius=r, start_angle=a, angle=p_, arc_center=[*O, 0], color=C.turn,
                                 stroke_width=C.thin + 0.6, stroke_opacity=0.75 * k), h=0.04, shadow=0.4 * k))
            g.add(lifted(v, z * np.exp(1j * p_), tip=0.2, k=k, h=0.1))
        return g
    live(m, fan, (T.whole - 0.5, end_out[1]))

    hud.play(ReplacementTransform(ii, badge(2)), FadeOut(back2), at=T.cut_ch3 - 1.05, dur=0.8, ease=E)
    hud.play(FadeOut(pl), at=T.cut_ch3 - 0.9, dur=0.6)
