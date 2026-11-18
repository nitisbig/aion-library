"""s25 rodrigues (ch6): exponentiate it. K³ = −K, so the series folds: odd powers collapse onto ±K, even ones onto ±K²,
and the sine and cosine series appear on their own: e^{θK} = I + sin θ K + (1 − cos θ) K² (Rodrigues' rotation
formula; every 3D rotation comes from such a matrix). A live θ follows the globe's spin; after one full turn θ = 2π,
sin and 1 − cos tick to zero and only the identity is left: the "you" dot lands on its starting ghost."""
from aion import *
from scipy.linalg import expm

import ch6
from beats import T
from ch6 import facing_lon, globe_frame
from shots import (K_AXIS, SPIN_RATE, backdrop, backed, body_to_world, finish, globe_layers, gproj, lab, latlon, live,
                   p3, sc, tex)

K = K_AXIS
assert np.allclose(K @ K @ K, -K)
for th in (0.7, 2.0, 4.5):
    assert np.allclose(expm(th * K), np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K)
assert np.allclose(expm(2 * np.pi * K), np.eye(3))

T_R0 = T.identity_back + 0.4 - 2 * np.pi / SPIN_RATE   # the readout's θ = 0: it reaches 2π on "identity"


def theta_r(t):
    return float(np.clip((t - T_R0) * SPIN_RATE, 0.0, 2 * np.pi))


@scene(T.cut_rod, T.cut_outro)
def s25_rodrigues(s):
    backdrop(s)
    m = s.manim(z=3)
    g_op = keys((T.cut_outro - 0.5, 1.0), (T.cut_outro - 0.05, 0.0), lead=0)
    globe_layers(s, ch6.theta, ch6.center, ch6.radius, ch6.pole, alpha=g_op, z=1, start=T.cut_rod, end=T.cut_outro)
    live(m, lambda t: globe_frame(t, float(g_op(t))), (T.cut_rod, T.cut_outro))

    # ── K³ = −K ──
    k3 = tex(r"K^3", "=", r"-K", size=60, colors={0: C.gen, 2: C.gen}).move_to([-4.85, -1.75, 0])
    m.play(FadeIn(k3, scale=0.9), at=T.K3 + 0.2, dur=0.6)

    # ── the series ──
    ser = tex(r"e^{\theta K}", "=", "I", "+", r"\theta K", "+", r"\tfrac{\theta^2}{2!}K^2", "+",
              r"\tfrac{\theta^3}{3!}K^3", "+", r"\tfrac{\theta^4}{4!}K^4", "+", r"\tfrac{\theta^5}{5!}K^5", "+", r"\cdots",
              size=36, colors={0: C.flow}).move_to([2.25, 3.15, 0])
    m.play(Write(ser), at=T.folds + 0.1, dur=1.6)
    odd_i, even_i = (4, 8, 12), (6, 10)
    row1 = tex(r"K", r"\left(\theta - \tfrac{\theta^3}{3!} + \tfrac{\theta^5}{5!} - \cdots\right)", size=40,
               colors={0: C.gen}).move_to([2.25, 1.95, 0])
    row2 = tex(r"K^2", r"\left(\tfrac{\theta^2}{2!} - \tfrac{\theta^4}{4!} + \cdots\right)", size=40,
               colors={0: C.eigen}).move_to([2.25, 0.15, 0])
    m.play(*[ser[i].animate.set_color(C.gen) for i in odd_i], at=T.odd, dur=0.4)
    m.play(TransformFromCopy(VGroup(*[ser[i] for i in odd_i]), row1), at=T.odd + 0.5, dur=1.0)
    m.play(*[ser[i].animate.set_color(C.eigen) for i in even_i], at=T.even - 0.1, dur=0.4)
    m.play(TransformFromCopy(VGroup(*[ser[i] for i in even_i]), row2), at=T.even + 0.4, dur=1.0)

    # the sine and cosine series appear on their own
    s1 = tex(r"\sin\theta", size=40, color=C.flow).next_to(row1[1], DOWN, buff=0.12)
    s2 = tex(r"1-\cos\theta", size=40, color=C.flow).next_to(row2[1], DOWN, buff=0.12)
    b1 = Brace(row1[1], DOWN, buff=0.04, color=C.flow)
    b2 = Brace(row2[1], DOWN, buff=0.04, color=C.flow)
    s1.next_to(b1, DOWN, buff=0.06)
    s2.next_to(b2, DOWN, buff=0.06)
    m.play(FadeIn(b1), FadeIn(s1), at=T.sin_cos + 0.1, dur=0.5)
    m.play(FadeIn(b2), FadeIn(s2), at=T.sin_cos + 0.7, dur=0.5)

    # ── Rodrigues' rotation formula ──
    rod = tex(r"e^{\theta K}", "=", "I", "+", r"\sin\theta", r"\,K", "+", r"(1-\cos\theta)", r"\,K^2", size=50,
              colors={0: C.flow, 4: C.flow, 5: C.gen, 7: C.flow, 8: C.eigen}).move_to([2.25, -1.6, 0])
    frame = SurroundingRectangle(rod, color=C.flow, buff=0.2, stroke_width=C.thin + 0.6)
    m.play(VGroup(ser, row1, row2, b1, b2, s1, s2).animate.set_opacity(0.3), at=T.rodrigues - 0.2, dur=0.5)
    m.play(Write(rod), at=T.rodrigues + 0.2, dur=1.4)
    m.play(Create(frame), at=T.rodrigues + 1.7, dur=0.6)
    name = sc("Rodrigues' rotation formula", 30).next_to(frame, DOWN, buff=0.22)
    m.play(FadeIn(name, shift=0.08 * UP), at=T.rodrigues_name + 0.4, dur=0.6)
    er = lab("every rotation in 3D", 24, C.muted).next_to(name, DOWN, buff=0.12)
    m.play(FadeIn(er), at=T.every_rot + 0.4, dur=0.5)

    # ── a live θ, and one full turn ──
    def readout(t):
        th = theta_r(t)
        sn, cs = np.sin(th), 1 - np.cos(th)
        fix = lambda v: 0.0 if abs(v) < 0.005 else v
        row = VGroup(VGroup(tex(r"\theta", "=", size=38, colors={0: C.flow}),
                            DecimalNumber(th, num_decimal_places=2, font_size=38, color=C.flow)).arrange(RIGHT, buff=0.12),
                     VGroup(tex(r"\sin\theta", "=", size=34, colors={0: C.flow}),
                            DecimalNumber(fix(sn), num_decimal_places=2, font_size=34, color=C.text)).arrange(RIGHT, buff=0.12),
                     VGroup(tex(r"1-\cos\theta", "=", size=34, colors={0: C.flow}),
                            DecimalNumber(fix(cs), num_decimal_places=2, font_size=34, color=C.text)).arrange(RIGHT, buff=0.12)
                     ).arrange(RIGHT, buff=0.6).move_to([2.25, 2.45 - 5.85, 0])
        return row.set_opacity(float(r_op(t)))
    r_op = keys((T.full_turn - 2.4, 0.0), (T.full_turn - 1.8, 1.0), (T.cut_outro - 0.5, 1.0), (T.cut_outro - 0.05, 0.0),
                lead=0)
    live(m, readout, (T.full_turn - 2.4, T.cut_outro))
    m.play(FadeOut(VGroup(name, er)), at=T.full_turn - 2.6, dur=0.4)

    # the "you" dot and its starting ghost
    L_y = facing_lon(0, T_R0) - 30

    def you_at(t):
        c, R, pl = ch6.center(t), ch6.radius(t), ch6.pole(t)
        (q,), d = gproj((latlon(0, L_y) @ body_to_world(ch6.theta(t)).T)[None], c, R, pl)
        return q, d[0]
    ghost_q, _ = you_at(T_R0)
    y_op = keys((T_R0 - 0.5, 0.0), (T_R0, 1.0), (T.cut_outro - 0.5, 1.0), (T.cut_outro - 0.05, 0.0), lead=0)

    def you(t):
        q, d = you_at(t)
        op = float(y_op(t))
        return VGroup(Circle(radius=0.13, color=C.vec, stroke_width=C.thin + 0.6).move_to(p3(ghost_q)).set_stroke(
            opacity=0.6 * op), Dot(p3(q), radius=0.1, color=C.vec).set_opacity(op * (1.0 if d > 0 else 0.25)))
    live(m, you, (T_R0 - 0.5, T.cut_outro))

    # only the identity is left
    fin = backed(tex(r"e^{2\pi K}", "=", "I", size=56, colors={0: C.flow})).move_to([-4.85, -3.1, 0])
    m.play(FadeIn(fin, shift=0.1 * UP), Indicate(rod[2], color=C.text, scale_factor=1.4), at=T.identity_back + 0.6,
           dur=0.7)
    s.camera.push(at=T.full_turn, zoom=1.05, dur=4.0)
    m.play(FadeOut(VGroup(k3, ser, row1, row2, b1, b2, s1, s2, rod, frame, fin)), at=T.cut_outro - 0.45, dur=0.45)
    finish(s)
