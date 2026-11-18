"""s16 spiral and shear (ch4). The spiral [[−1/4, −1], [1, −1/4]] has eigenvalues −1/4 ± i: the real part sets how fast
things shrink, the imaginary part how fast they turn; complex eigenvalues are how a real flow rotates. The shear N
has too few eigenvectors: its velocity is horizontal and grows with height; N² = 0, so the series stops after two
terms and e^{tN} = I + tN = [[1, t], [0, 1]]."""
from aion import *

from beats import T
from shots import (BOX4, PC4, PX4, E, backdrop, cycles, disc_points, field_arrows, finish, flow_layers, lab, p3,
                   stage4, tex)
from verify import CAST, N

SP = CAST["spiral"]


@scene(T.cut_spiral, T.cut_trace)
def s16_spiral_shear(s):
    backdrop(s)
    mg = s.manim(z=0)
    mf = s.manim(z=1)
    m = s.manim(z=4)
    mp = s.manim(z=5)
    g, pan = stage4(mg, mp)

    # ── the spiral ──
    Am = VGroup(tex("A", "=", size=44, colors={0: C.gen}),
                Mat([[r"-\tfrac14", "-1"], ["1", r"-\tfrac14"]], colors=C.gen, size=38, h_buff=1.1, v_buff=0.8)
                ).arrange(RIGHT, buff=0.2).move_to([PX4, 2.75, 0])
    mp.play(FadeIn(Am, shift=0.1 * DOWN), at=T.complex_eig + 0.3, dur=0.6)
    f_sp = field_arrows(SP, center=PC4, box=BOX4, spacing=0.75)
    mf.play(FadeIn(f_sp, lag_ratio=0.004), at=T.complex_eig + 0.5, dur=1.2)
    lam = tex(r"\lambda", "=", r"-\tfrac14", r"\pm", "i", size=52, colors={0: C.eigen}).move_to([PX4, 1.05, 0])
    mp.play(FadeIn(lam, shift=0.1 * DOWN), at=T.complex_eig + 3.2, dur=0.6)

    t_sp = (T.spiral - 0.6, T.not_enough - 0.2)
    tau = keys((t_sp[0], 0.0), (t_sp[1], 5.0, "linear"), lead=0)
    al = keys((t_sp[0], 0.0), (t_sp[0] + 0.6, 0.75), (t_sp[1] - 0.5, 0.75), (t_sp[1], 0.0), lead=0)
    flow_layers(s, disc_points(3200, 5.2, seed=13), SP, tau, alpha=al, trail=10, size=2.2, z=2, center=PC4,
                start=t_sp[0], end=t_sp[1])

    # real part: shrink (amber); imaginary part: turn (purple)
    ul_r = Line(lam[2].get_corner(DL) + 0.08 * DOWN, lam[2].get_corner(DR) + 0.08 * DOWN, color=C.warm,
                stroke_width=C.stroke)
    ul_i = Line(lam[4].get_corner(DL) + 0.08 * DOWN + 0.05 * LEFT, lam[4].get_corner(DR) + 0.08 * DOWN + 0.05 * RIGHT,
                color=C.eigen, stroke_width=C.stroke)
    ic_r = VGroup(Circle(radius=0.36, color=C.warm, stroke_width=C.thin + 0.4, stroke_opacity=0.5),
                  Circle(radius=0.18, color=C.warm, stroke_width=C.stroke),
                  *[Arrow(p3(0.62 * d), p3(0.28 * d), buff=0, color=C.warm, stroke_width=C.thin + 0.6, tip_length=0.1)
                    for d in (np.array([1, 0]), np.array([-1, 0]), np.array([0, 1]), np.array([0, -1]))])
    ic_i = Arc(radius=0.36, start_angle=-0.4, angle=4.2, color=C.eigen, stroke_width=C.stroke).add_tip(
        tip_length=0.14, tip_width=0.14)
    row_r = VGroup(ic_r, lab("shrink", 26, C.warm)).arrange(RIGHT, buff=0.25)
    row_i = VGroup(ic_i, lab("turn", 26, C.eigen)).arrange(RIGHT, buff=0.25)
    VGroup(row_r, row_i).arrange(RIGHT, buff=0.6).move_to([PX4, -0.4, 0])
    mp.play(Create(ul_r), FadeIn(row_r, shift=0.1 * UP), lam[2].animate.set_color(C.warm), at=T.real_part + 0.2, dur=0.6)
    mp.play(Create(ul_i), FadeIn(row_i, shift=0.1 * UP), lam[4].animate.set_color(C.eigen), at=T.imag_part + 0.2,
            dur=0.6)
    rot = lab("complex eigenvalues: rotation", 24, C.text).move_to([PX4, -1.6, 0])
    mp.play(FadeIn(rot), at=T.rotates + 0.4, dur=0.5)
    spiral_bits = VGroup(Am, lam, ul_r, ul_i, row_r, row_i, rot)
    mp.play(FadeOut(spiral_bits), at=T.not_enough - 0.2, dur=0.5)
    mf.play(FadeOut(f_sp), at=T.not_enough - 0.2, dur=0.5)

    # ── the shear ──
    Nm = VGroup(tex("N", "=", size=44, colors={0: C.gen}),
                Mat([["0", "1"], ["0", "0"]], colors=C.gen, size=40, h_buff=0.95, v_buff=0.8)).arrange(
        RIGHT, buff=0.2).move_to([PX4, 2.75, 0])
    mp.play(FadeIn(Nm, shift=0.1 * DOWN), at=T.shear, dur=0.6)
    f_n = field_arrows(N, center=PC4, box=BOX4, spacing=0.75)
    mf.play(FadeIn(f_n, lag_ratio=0.004), at=T.shear + 0.3, dur=1.0)
    tn, an = cycles(T.horizontal + 0.4, T.cut_trace - 0.3, 4.2, 2.0)
    flow_layers(s, disc_points(2500, 4.2, seed=17), N, tn, alpha=an * 0.75, trail=10, size=2.2, z=2, center=PC4,
                start=T.horizontal, end=T.cut_trace)
    hint = lab("faster with height", 24, C.gen).move_to(p3(PC4 + [2.6, 3.55]))
    hint_bg = BackgroundRectangle(hint, color=C.bg, fill_opacity=0.9, buff=0.08)
    m.play(FadeIn(VGroup(hint_bg, hint)), at=T.horizontal + 0.8, dur=0.5)
    m.play(FadeOut(VGroup(hint_bg, hint)), at=T.square_zero, dur=0.5)

    n2 = tex(r"N^2", "=", "0", size=50, colors={0: C.gen, 2: C.text}).move_to([PX4, 1.45, 0])
    mp.play(FadeIn(n2, shift=0.1 * DOWN), at=T.square_zero + 0.3, dur=0.6)
    ser = tex(r"e^{tN}", "=", "I", "+", "tN", "+", r"\tfrac{t^2N^2}{2!}", "+", r"\cdots", size=34,
              colors={0: C.flow, 4: C.gen, 6: C.gen}).move_to([PX4, 0.25, 0])
    mp.play(FadeIn(ser), at=T.square_zero + 1.5, dur=0.6)
    zero = tex("0", size=34, color=C.wrong).move_to(ser[6])
    mp.play(VGroup(*ser[5:]).animate.set_color(C.wrong).set_opacity(0.45), FadeIn(zero, shift=0.1 * DOWN),
            ser[6].animate.set_opacity(0.0), at=T.square_zero + 2.6, dur=0.6)
    eN = VGroup(tex(r"e^{tN}", "=", size=44, colors={0: C.flow}),
                Mat([["1", "t"], ["0", "1"]], colors=C.flow, size=40, h_buff=0.95, v_buff=0.8)).arrange(
        RIGHT, buff=0.2).move_to([PX4, -1.45, 0])
    mp.play(FadeIn(eN, shift=0.1 * DOWN), at=T.eNt + 0.2, dur=0.6)
    tt = VGroup(tex("t", "=", size=36, colors={0: C.flow}),
                DecimalNumber(0, num_decimal_places=2, font_size=36, color=C.flow)).arrange(RIGHT, buff=0.12)
    tt.move_to([PX4, -2.75, 0])
    mp.play(FadeIn(tt), at=T.eNt + 0.6, dur=0.4)
    mp.drive(tt, lambda c, t: c[1].set_value(float(tn(t))), during=(T.eNt + 0.6, T.cut_trace - 0.3))

    # chapter-part close: everything fades (s17 sets up two panels)
    mp.play(FadeOut(VGroup(Nm, n2, ser, zero, eN, tt, pan)), at=T.cut_trace - 0.4, dur=0.5)
    mf.play(FadeOut(f_n), at=T.cut_trace - 0.4, dur=0.5)
    mg.play(FadeOut(g), at=T.cut_trace - 0.4, dur=0.5)
    finish(s)
