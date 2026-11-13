"""Ch6 (cont.) · Special values and the whole plane. On the intro's circle the point lands on i (θ = π/2), −1
(θ = π) and back on 1 (θ = 2π), each label stamping in; e^{iπ} = −1 builds under it. Then the hero callback:
multiplying by e^{iθ} turns the entire plane, so the domain-colored plane, its grid and a fan of arrows turn
together (ghosts and red arcs marking the turn), first a little, then half a turn on "e to the i pi". Move the 1
across: e^{iπ} + 1 = 0, and the five constants light one by one."""
from aion import *

from beats import T
from shots import (HERO_O, HERO_U, P, backdrop, backing, badges, euler, identity, live, plane_grid, rail,
                   ramp, tex, walker)

E = "easy_ease"
O, U = HERO_O, HERO_U
EQ_AT = (0.0, -2.22)                                  # above the rail's badge row


def W(z):
    return P(O, U, z)


@scene(T.cut_identity, T.cut_outro)
def s11_identity(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)
    m = s.manim(z=2)
    hb = s.manim(z=3, parallax=0.0)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 6)
    badges(hud, 6)
    kin = (t0 + 0.1, t0 + 1.0)
    end_out = (T.cut_outro - 1.0, T.cut_outro - 0.2)

    # ── "Now try a few special values." ──
    th = keys((t0, 0.0), (T.th_half + 0.2, 0.0), (T.land_i - 0.2, PI / 2, E), (T.th_pi + 0.3, PI / 2),
              (T.land_neg1 - 0.2, PI, E), (T.th_2pi + 0.3, PI), (T.back_at_one - 0.2, TAU, E), lead=0)
    walk_out = (T.mult_theta - 0.3, T.mult_theta + 0.5)
    turn = keys((t0, 0.0), (T.entire + 0.2, 0.0), (T.entire + 2.4, 0.8, E), (T.half_all + 0.1, 0.8),
                (T.half_all + 2.3, PI, E), lead=0)
    kplane = (T.not_just - 0.2, T.not_just + 1.2)

    def stage(t):
        k = ramp(t, *kin) * (1 - ramp(t, *end_out))
        g = plane_grid(O, U / 2, turn=turn(t), n=10, minor=1, opacity=(0.4 + 0.15 * ramp(t, *kplane)) * k)
        g.add(Circle(radius=U, color=C.ghost, stroke_width=C.thin + 0.6).move_to([*O, 0])
              .set_stroke(opacity=k * (1 - ramp(t, *walk_out))))
        return g
    live(bg, stage, kin, (T.entire + 0.2, T.entire + 2.4), (T.half_all + 0.1, T.half_all + 2.3), kplane,
         walk_out, end_out)

    def walk(t):
        k = ramp(t, *kin) * (1 - ramp(t, *walk_out))
        if k < 0.005:
            return VGroup()
        return walker(O, U, th(t), k=k)
    live(m, walk, kin, (T.th_half + 0.2, T.land_i - 0.2), (T.th_pi + 0.3, T.land_neg1 - 0.2),
         (T.th_2pi + 0.3, T.back_at_one - 0.2), walk_out)

    # the landings: each value stamps in
    stamps = []
    for val, angle_lab, at_, pos, apos in (
            (("i", C.turn), r"\tfrac{\pi}{2}", T.land_i, W(1.22j), W(0.62 * np.exp(1j * PI / 4))),
            (("-1", C.point), r"\pi", T.land_neg1, W(-1.3), W(1.2 * np.exp(1j * 3 * PI / 4))),
            (("1", C.text), r"2\pi", T.back_at_one, W(1.25), W(1.25 * np.exp(-1j * PI / 4)))):
        lab = MathTex(val[0], font_size=56, color=val[1]).move_to(pos)
        alab = MathTex(angle_lab, font_size=44, color=C.arc).move_to(apos)
        m.play(FadeIn(lab, scale=0.3), at=at_ - 0.1, dur=0.6, ease="out_back")
        m.play(FadeIn(alab, scale=0.5), at=at_ + 0.2, dur=0.5)
        stamps.append(VGroup(lab, alab))
    m.play(FadeOut(stamps[0][1]), at=T.th_pi + 0.2, dur=0.4)
    m.play(FadeOut(stamps[1][1]), at=T.th_2pi + 0.2, dur=0.4)
    m.play(FadeOut(VGroup(stamps[0][0], stamps[1][0], *stamps[2])), at=walk_out[0], dur=0.6)

    eq = euler(size=96).move_to([*EQ_AT, 0])
    eb = backing(eq, pad=0.18)
    hb.play(FadeIn(eb), at=T.land_neg1 + 0.4, dur=0.5)
    hud.play(FadeIn(eq, shift=0.15 * UP), at=T.land_neg1 + 0.6, dur=0.8)

    # ── "And multiplying by e to the i theta does not just move one point. It turns the entire plane by theta." ──
    s.shader("plane.frag", z=0, u_origin=O, u_unit=U, u_theta=turn, u_sat=0.6, u_value=0.8,
             u_opacity=fade(kplane[1], to=0.42, dur=1.4, out=end_out[1], out_dur=0.8))
    mul = VGroup(tex(r"\times e^{i\theta}", size=60), tex(r"\theta", "=", size=46)).arrange(DOWN, aligned_edge=LEFT,
                                                                                            buff=0.3)
    mul[0][0][1].set_color(C.growth)
    mul[0][0][2].set_color(C.turn)
    mul[0][0][3].set_color(C.arc)
    mul[1][0].set_color(C.arc)
    mul.move_to([-5.2, 2.6, 0])

    def readout(t):
        k = ramp(t, T.mult_theta + 0.2, T.mult_theta + 0.8) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return VGroup()
        return DecimalNumber(turn(t), num_decimal_places=2, font_size=46, color=C.arc).next_to(mul[1], RIGHT,
                                                                                            buff=0.15).set_opacity(k)
    mb = backing(VGroup(mul, mul[1].copy().shift(1.3 * RIGHT)), pad=0.22)
    hb.play(FadeIn(mb), at=T.mult_theta + 0.2, dur=0.6)
    hud.play(FadeIn(mul, shift=0.1 * DOWN), at=T.mult_theta + 0.2, dur=0.6)
    live(hud, readout, (T.mult_theta + 0.2, T.mult_theta + 0.8), (T.entire + 0.2, T.entire + 2.4),
         (T.half_all + 0.1, T.half_all + 2.3), end_out)

    zs = [r * np.exp(1j * a) for r, a in zip((1.25, 1.85, 1.25, 1.85, 1.25, 1.85, 1.25, 1.85),
                                             np.radians([15, 60, 105, 150, 195, 240, 285, 330]))]
    fan_in = (T.not_just + 0.2, T.not_just + 1.0)

    def fan(t):
        g = VGroup()
        k = ramp(t, *fan_in) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return g
        p_ = turn(t)
        for z in zs:
            r, a = abs(z), np.angle(z)
            if p_ > 0.02:
                g.add(Arrow(W(0), W(z), buff=0, color=C.ghost, stroke_width=C.thin + 1, tip_length=0.18)
                      .set_opacity(0.8 * k))
                g.add(Arc(radius=r * U, start_angle=a, angle=p_, arc_center=[*O, 0], color=C.turn,
                          stroke_width=C.thin + 0.6, stroke_opacity=0.75 * k))
            g.add(Arrow(W(0), W(z * np.exp(1j * p_)), buff=0, color=C.point, stroke_width=C.stroke,
                        tip_length=0.22).set_opacity(k))
        return g
    live(m, fan, fan_in, (T.entire + 0.2, T.entire + 2.4), (T.half_all + 0.1, T.half_all + 2.3), end_out)

    # ── "e to the i pi turns everything by half a turn." ──
    hud.play(Indicate(eq[:3], color=None, scale_factor=1.2), at=T.half_all + 0.3, dur=0.9)

    # ── "Move the one across, and you get the famous form. e to the i pi, plus one, equals zero." ──
    idn = identity(size=96).move_to([*EQ_AT, 0])
    eb2 = backing(idn, pad=0.18)
    hb.play(ReplacementTransform(eb, eb2), at=T.move_one + 0.2, dur=1.2)
    hud.play(ReplacementTransform(eq[0], idn[0]), ReplacementTransform(eq[1], idn[1]), ReplacementTransform(eq[2], idn[2]),
             ReplacementTransform(eq[3], idn[5]), ReplacementTransform(eq[4], idn[3]),
             ReplacementTransform(eq[5], idn[4], path_arc=-PI * 0.8), at=T.move_one + 0.2, dur=1.4, ease=E)
    hud.play(FadeIn(idn[6], scale=1.4), at=T.move_one + 1.3, dur=0.6)
    s.camera.push(T.famous, zoom=1.05, dur=3.0)
    for j, g_ in enumerate((idn[0], idn[1], idn[2], idn[4], idn[6])):            # the five constants
        hud.play(Indicate(g_, color=None, scale_factor=1.35), at=T.final_eq + 0.1 + 0.42 * j, dur=0.6)
    hb.play(FadeOut(mb), at=end_out[0], dur=0.6)
    hud.play(FadeOut(mul), at=end_out[0], dur=0.6)
