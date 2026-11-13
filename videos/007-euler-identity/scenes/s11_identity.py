"""Ch6 (cont.) · Special values and the whole plane. On the intro's circle the point lands on i (θ = π/2), −1
(θ = π) and back on 1 (θ = 2π), each label stamping in; e^{iπ} = −1 builds under it. Then the hero callback:
multiplying by e^{iθ} turns the entire plane, so the domain-colored plane, its grid and a fan of arrows turn
together (ghosts and red arcs marking the turn), first a little, then half a turn on "e to the i pi". Move the 1
across: e^{iπ} + 1 = 0, and the five constants light one by one.

The plane is the 3D one from s04 (shots3d): it opens flat on the intro's hero frame, tilts away for the special
values (the walk floats just above it, the labels stand up as billboards), cranes low for the turns, and rises
back to the flat hero frame for the famous form."""
from aion import *

from beats import T
from shots import (HERO_O, HERO_U, P, arrow, backdrop, backing, badges, euler, identity, live, rail, ramp, tex,
                   walker)
from shots3d import F0, TOP, Cam3, plane_uniforms

E = "easy_ease"
S_ = "in_out_sine"
O, U = HERO_O, HERO_U
EQ_AT = (0.0, -2.22)                                  # above the rail's badge row


def W(z):
    return P(O, U, z)


@scene(T.cut_identity, T.cut_outro)
def s11_identity(s):
    backdrop(s)
    t0 = s.start
    glow = keys((t0, 0.0), (t0 + 1.0, 1.0), (T.cut_outro - 1.0, 1.0), (T.cut_outro - 0.2, 0.0), lead=0)
    m = s.manim(z=2, fx=[Glow(strength=0.45 * glow, radius=3)])
    s.fx(Bloom(strength=0.4 * glow, threshold=0.72, radius=5))
    hb = s.manim(z=3, parallax=0.0)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 6)
    badges(hud, 6)
    kin = (t0 + 0.1, t0 + 1.0)
    end_out = (T.cut_outro - 1.0, T.cut_outro - 0.2)
    span = (t0, T.cut_outro)                          # the camera never quite rests: every overlay is live

    # ── the camera: the flat hero frame → tilted for the values → low for the turns → flat again ──
    tilt = (T.special_vals - 0.3, T.th_half + 0.6)
    drift = T.back_at_one + 0.5
    low = (T.mult_theta + 0.2, T.entire + 0.2)
    rise = (T.move_one + 0.2, T.famous + 1.2)
    deg = np.radians
    cam = Cam3(
        yaw=keys((t0, 0.0), (tilt[0], 0.0), (tilt[1], deg(-14), E), (drift, deg(10), S_), (low[1], deg(-16), E),
                 (rise[0], deg(-26), S_), (rise[1], 0.0, E), lead=0),
        pitch=keys((t0, TOP), (tilt[0], TOP), (tilt[1], deg(56), E), (drift, deg(52), S_), (low[0], deg(52)),
                   (low[1], deg(28), E), (rise[0], deg(25), S_), (rise[1], TOP, E), lead=0),
        dist=keys((t0, F0), (tilt[0], F0), (tilt[1], 10.0, E), (drift, 9.6, S_), (low[0], 9.6), (low[1], 10.6, E),
                  (rise[0], 10.6), (rise[1], 1.25 * F0, E), lead=0),
        tx=O[0], ty=O[1], sx=O[0], fog=8.0,
        sy=keys((t0, O[1]), (tilt[0], O[1]), (tilt[1], 0.5, E), (low[0], 0.5), (low[1], 0.15, E),
                (rise[0], 0.15), (rise[1], O[1], E), lead=0))

    # ── "Now try a few special values." ──
    th = keys((t0, 0.0), (T.th_half + 0.2, 0.0), (T.land_i - 0.2, PI / 2, E), (T.th_pi + 0.3, PI / 2),
              (T.land_neg1 - 0.2, PI, E), (T.th_2pi + 0.3, PI), (T.back_at_one - 0.2, TAU, E), lead=0)
    walk_out = (T.mult_theta - 0.3, T.mult_theta + 0.5)
    turn = keys((t0, 0.0), (T.entire + 0.2, 0.0), (T.entire + 2.4, 0.8, E), (T.half_all + 0.1, 0.8),
                (T.half_all + 2.3, PI, E), lead=0)
    kplane = (T.not_just - 0.2, T.not_just + 1.2)
    s.shader("plane3d.frag", z=0, **cam.uniforms(),
             **plane_uniforms(O, U, U / 2, theta=turn, sat=0.6, value=0.8,
                              lines=keys((t0, 0.0), (kin[0], 0.0), (kin[1], 0.9), (end_out[0], 0.9),
                                         (end_out[1], 0.0), lead=0),
                              colors=keys((t0, 0.0), (kin[0], 0.0), (kin[1] + 0.6, 0.24), (kplane[0], 0.24),
                                          (kplane[1] + 1.0, 0.6, E), (end_out[0], 0.6), (end_out[1], 0.0), lead=0)))

    def walk(t):
        k = ramp(t, *kin) * (1 - ramp(t, *walk_out))
        if k < 0.005:
            return VGroup()
        v = cam(t)
        circ = Circle(radius=U, color=C.text, stroke_width=C.thin + 0.6).move_to([*O, 0]).set_stroke(opacity=0.5 * k)
        return VGroup(v.flat(circ), v.lift(walker(O, U, th(t), k=k), h=0.08, shadow=0.55 * k))
    live(m, walk, span)

    # the landings: each value stamps in, standing up off the plane
    def pop(t, a):
        u = np.clip((t - a) / 0.6, 0.0, 1.0)
        c1 = 1.70158
        return 0.3 + 0.7 * (1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2)
    stamps = (("i", C.turn, r"\tfrac{\pi}{2}", T.land_i, 1.22j, 0.62 * np.exp(1j * PI / 4), T.th_pi + 0.2),
              ("-1", C.point, r"\pi", T.land_neg1, -1.3, 1.2 * np.exp(1j * 3 * PI / 4), T.th_2pi + 0.2),
              ("1", C.text, r"2\pi", T.back_at_one, 1.3, 0.62 * np.exp(1j * PI / 4), walk_out[0]))
    texs = [(MathTex(v_, font_size=56, color=c_), MathTex(al, font_size=44, color=C.arc)) for v_, c_, al, *_ in stamps]

    def labels(t):
        g = VGroup()
        v = cam(t)
        for (lab, alab), (_, _, _, at_, z, za, a_out) in zip(texs, stamps):
            kv = ramp(t, at_ - 0.1, at_ + 0.3) * (1 - ramp(t, walk_out[0], walk_out[0] + 0.6))
            if kv > 0.01:
                p = W(z)
                g.add(v.bill(lab.copy().scale(pop(t, at_ - 0.1)).set_opacity(kv), p[:2], h=0.25))
            ka = ramp(t, at_ + 0.2, at_ + 0.7) * (1 - ramp(t, a_out, a_out + 0.4))
            if ka > 0.01:
                p = W(za)
                g.add(v.bill(alab.copy().set_opacity(ka), p[:2], h=0.1))
        return g
    live(m, labels, (T.land_i - 0.2, walk_out[0] + 0.7))

    eq = euler(size=96).move_to([*EQ_AT, 0])
    eb = backing(eq, pad=0.18)
    hb.play(FadeIn(eb), at=T.land_neg1 + 0.4, dur=0.5)
    hud.play(FadeIn(eq, shift=0.15 * UP), at=T.land_neg1 + 0.6, dur=0.8)

    # ── "And multiplying by e to the i theta does not just move one point. It turns the entire plane by theta." ──
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
    axis_k = (T.entire + 0.0, T.half_all + 2.8)

    def fan(t):
        g = VGroup()
        k = ramp(t, *fan_in) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return g
        v = cam(t)
        p_ = turn(t)
        kx = ramp(t, axis_k[0], axis_k[0] + 0.6) * (1 - ramp(t, axis_k[1] - 0.5, axis_k[1])) * k
        if kx > 0.005:                                # the axis the plane turns about
            g.add(v.post(O, 2.6, C.muted, opacity=0.8 * kx))
        for z in zs:
            r, a = abs(z), np.angle(z)
            if p_ > 0.02:
                g.add(v.flat(arrow(W(0), W(z), C.ghost, width=C.thin + 1, tip=0.18).set_opacity(0.8 * k)))
                g.add(v.lift(Arc(radius=r * U, start_angle=a, angle=p_, arc_center=[*O, 0], color=C.turn,
                                 stroke_width=C.thin + 0.6, stroke_opacity=0.75 * k), h=0.05, shadow=0.4 * k))
            a3 = arrow(W(0), W(z * np.exp(1j * p_)), C.point, tip=0.22).set_opacity(k)
            g.add(v.lift(a3, h=0.12, shadow=0.55 * k))
        return g
    live(m, fan, (fan_in[0], end_out[1]))

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
