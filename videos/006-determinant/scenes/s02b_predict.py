"""Ch2 (cont.) · Test it (a 2-by-3 stretch, det 6), then predict a shear (det 1: base and height never change)."""
from aion import *

from beats import T
from shots import (A_MAIN, A_SCALE, A_SHEAR, FRAME, I2, Mat, backing, backdrop, basis_arrows, det2, finish,
                   grid_lines, live, matrix_panel, num, pt, rail, span_area, tex)

E = "easy_ease"
O2, U2 = np.array([0.0, -0.2]), 0.55                 # where Ch2's first half ended
O3, U3 = np.array([-0.9, -2.3]), 1.4                 # framing for the two experiments
X2 = np.diag([2.0, 1.0])                             # halfway: stretched sideways only


def shear(k):
    return np.array([[1.0, k], [0.0, 1.0]])


def ramp(t, a, b):
    """0 before a, 1 after b, smooth between."""
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


@scene(T.cut_test, T.cut_ch3)
def s02b_predict(s):
    backdrop(s)
    ghost = s.manim(z=0)
    m = s.manim(z=1)
    ar = s.manim(z=2)                                 # the square and its number
    sh = s.manim(z=3)                                 # cells, braces, cut pieces
    g = s.manim(z=4)
    hb = s.manim(z=5.5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)
    rail(hud, 2)

    t0 = T.cut_test
    w_in = (t0, t0 + 1.4)                             # leave Ch2's first half: grid to rest, new framing
    w_x = (T.scale2 - 0.25, T.scale2 + 0.95)          # two sideways
    w_y = (T.scale3 - 0.2, T.scale3 + 0.95)           # three upward
    w_back = (T.predict - 0.6, T.predict + 0.6)       # back to rest for the shear
    w_sh = (T.slides - 0.25, T.slides + 1.3)          # the top slides right
    lean = (T.base_height + 0.6, T.base_height + 3.6)  # leans back and forth between fixed base and height
    w_out = (T.cut_ch3 - 1.45, T.cut_ch3 - 0.05)      # relax for Ch3
    S1, Sm = shear(1.0), shear(-0.5)
    Mg = keys((w_in[0], A_MAIN), (w_in[1], I2, E), (w_x[0], I2), (w_x[1], X2, E), (w_y[0], X2), (w_y[1], A_SCALE, E),
              (w_back[0], A_SCALE), (w_back[1], I2, E), (w_sh[0], I2), (w_sh[1], S1, E),
              (lean[0], S1), (lean[0] + 1.5, Sm, "in_out_sine"), (lean[1], S1, "in_out_sine"),
              (w_out[0], S1), (w_out[1], I2, E), lead=0)
    Og = keys((w_in[0], O2), (w_in[1], O3, E), lead=0)
    Ug = keys((w_in[0], U2), (w_in[1], U3, E), lead=0)

    def W(v, t):
        return pt(Og(t), Ug(t), Mg(t) @ np.asarray(v, float))

    moving = (w_in, w_x, w_y, w_back, w_sh, lean, w_out)
    live(m, lambda t: grid_lines(Mg(t), Og(t), Ug(t), FRAME, n=16), *moving)
    live(ghost, lambda t: grid_lines(I2, Og(t), Ug(t), FRAME, n=16, color=C.ghost, axes=False), w_in)
    on = (w_in[1] + 0.1, w_in[1] + 0.6)               # arrows and square arrive once the grid has settled
    g_on = lambda t: ramp(t, *on)                     # noqa: E731
    live(g, lambda t: basis_arrows(Mg(t), Og(t), Ug(t)).set_opacity(g_on(t)), on, *moving[1:])

    # ── the square and its number: the live value, then "?" while we predict, then "1" ──
    p0, d0 = T.predict - 0.6, T.det1 - 0.3
    cut_at = T.no_area - 0.2                          # the live square hands over to two cut pieces here

    def area(t):
        k = g_on(t)
        M = Mg(t)
        out = VGroup(span_area(M, Og(t), Ug(t), opacity=0.3 * k).set_stroke(opacity=k))
        c = W((0.5, 0.5), t)
        for txt, a in ((num(det2(M)), 1 - ramp(t, p0, p0 + 0.3)),
                       ("?", ramp(t, p0 + 0.3, p0 + 0.6) * (1 - ramp(t, d0, d0 + 0.25))),
                       ("1", ramp(t, d0 + 0.25, d0 + 0.5))):
            if a * k > 0.003:
                out.add(tex(txt, size=72, color=C.area).move_to(c).set_opacity(a * k))
        return out
    hs = live(ar, area, on, w_x, w_y, (p0, p0 + 0.65), w_back, w_sh, (d0, d0 + 0.55), lean)
    ar.remove(hs[-1], at=cut_at)

    # ── the HUD: the stretch matrix with its determinant underneath ──
    rd_a = tex(r"\det", "=", "6", size=56, colors={2: C.area})
    Ma, hats, back = matrix_panel([["2", "0"], ["0", "3"]], below=rd_a)
    Mb = Mat([["1", "1"], ["0", "1"]], colors=[C.ihat, C.jhat], size=64).move_to(Ma)
    v_q = tex("?", size=56, color=C.area).move_to(rd_a[2])
    v_1 = tex("1", size=56, color=C.area).move_to(rd_a[2])
    hb.play(FadeIn(back), at=w_in[1] + 0.7, dur=0.6, lead=0)
    hud.play(FadeIn(VGroup(Ma, hats)), at=w_in[1] + 0.8, dur=0.6, lead=0)
    hud.play(Write(rd_a), at=T.det6, dur=0.8)
    hud.play(FadeOut(Ma, shift=0.1 * LEFT), FadeIn(Mb, shift=0.1 * LEFT), at=T.predict, dur=0.7)
    hud.play(FadeOut(rd_a[2]), FadeIn(v_q, scale=1.3), at=T.predict + 0.2, dur=0.5)
    hud.play(FadeOut(v_q), FadeIn(v_1, scale=1.3), at=T.det1, dur=0.5)

    # ── two by three: the six unit cells inside the rectangle, counted one after another ──
    cells = VGroup()
    for j in range(3):
        for i in range(2):
            corners = [pt(O3, U3, np.array(c, float)) for c in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            cells.add(Polygon(*corners, stroke_color=C.text, stroke_width=C.stroke - 1, fill_color=C.area,
                              fill_opacity=0.35))
    sh.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.35), at=T.two_by_three - 0.2, dur=1.6)
    sh.play(FadeOut(cells), at=T.det6 + 1.3, dur=0.6)

    # ── base and height: a brace under the base, a brace beside the height, a dashed line holding the top ──
    base = Line(pt(O3, U3, (0, 0)), pt(O3, U3, (1, 0)))
    b_br = Brace(base, DOWN, buff=0.12, color=C.text)
    b_lb = tex("1", size=44).next_to(b_br, DOWN, buff=0.1)
    xh = 2.45
    hgt = Line(pt(O3, U3, (xh, 0)), pt(O3, U3, (xh, 1)))
    h_br = Brace(hgt, RIGHT, buff=0.08, color=C.text)
    h_lb = tex("1", size=44).next_to(h_br, RIGHT, buff=0.1)
    top = DashedLine(pt(O3, U3, (-0.9, 1)), pt(O3, U3, (xh, 1)), color=C.text, stroke_width=C.thin, dash_length=0.12)
    bot = DashedLine(pt(O3, U3, (1, 0)), pt(O3, U3, (xh, 0)), color=C.text, stroke_width=C.thin, dash_length=0.12)
    sh.play(GrowFromCenter(b_br), FadeIn(b_lb), at=T.base_height, dur=0.6)
    sh.play(Create(top), Create(bot), GrowFromCenter(h_br), FadeIn(h_lb), at=T.base_height + 0.5, dur=0.7)
    sh.play(FadeOut(VGroup(b_br, b_lb, top, bot, h_br, h_lb)), at=cut_at, dur=0.5)

    # ── not a drop of area: cut the right-hand triangle off and slide it into the gap ──
    P = lambda v: pt(O3, U3, v)                       # noqa: E731  (the frame is at rest here, sheared by S1)
    left = Polygon(P((0, 0)), P((1, 0)), P((1, 1)), stroke_color=C.area, stroke_width=C.thin + 0.6,
                   fill_color=C.area, fill_opacity=0.3)
    right = Polygon(P((1, 0)), P((2, 1)), P((1, 1)), stroke_color=C.area, stroke_width=C.thin + 0.6,
                    fill_color=C.area, fill_opacity=0.3)
    one = tex("1", size=72, color=C.area).move_to(P((1, 0.5)))
    knife = DashedLine(P((1, -0.25)), P((1, 1.25)), color=C.text, stroke_width=C.thin + 0.5, dash_length=0.1)
    sh.add(left, right, one, at=cut_at)
    sh.play(Create(knife), at=T.no_area, dur=0.5)
    sh.play(right.animate.set_fill(opacity=0.55), at=T.no_area + 0.45, dur=0.3)
    sh.play(right.animate.shift(P((-1, 0)) - P((0, 0))).set_fill(opacity=0.3), one.animate.move_to(P((0.5, 0.5))),
            at=T.no_area + 1.5, dur=1.1)
    sh.play(FadeOut(knife), at=T.no_area + 1.7, dur=0.4)
    whole = Polygon(P((0, 0)), P((1, 0)), P((1, 1)), P((0, 1)), stroke_color=C.area, stroke_width=C.thin + 0.6,
                    fill_color=C.area, fill_opacity=0.3)
    sh.add(whole, at=T.no_area + 2.7)                 # one square again: the seam disappears
    sh.remove(left, right, at=T.no_area + 2.7)

    # ── carried over from the first half: det [3 1; 1 2] = 5, cleared as the grid relaxes ──
    big = VGroup(tex(r"\det", size=72), Mat([["3", "1"], ["1", "2"]], colors=[C.ihat, C.jhat], size=72),
                 tex("=", size=72), tex("5", size=80, color=C.area)).arrange(RIGHT, buff=0.3).move_to([0, 0.3, 0])
    bigback = backing(big, pad=0.45)
    hb.add(bigback)
    hud.add(big)
    hb.play(FadeOut(bigback), at=t0 + 0.25, dur=0.6, lead=0)
    hud.play(FadeOut(big), at=t0 + 0.25, dur=0.6, lead=0)

    finish(s)
