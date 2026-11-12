"""Ch7 · The payoff: det(AB) = det(A) det(B). The algebra fills a page; the picture needs none: ×5, then ×2, is ×10."""
import sympy as sp

from aion import *

from beats import T
from shots import (A_MAIN, FRAME, I2, Mat, backdrop, backing, basis_arrows, det2, finish, grid_lines, live, num, pt,
                   rail, span_area, tex)

E = "easy_ease"
O6, U6 = np.array([0.6, -1.1]), 0.9                  # Ch6's top-down view
A30 = np.column_stack([[-2.0, 0, 0], [1.0, 1, 0], [-1.0, 1, 0]])
CUBE = np.array([(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
FACES = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]
O7, U7 = np.array([0.4, -3.3]), 0.6                  # framing for the two matrices
B = np.array([[1.0, 1.0], [0.0, 2.0]])               # det 2
BA = B @ A_MAIN                                      # [[4, 3], [2, 4]]: det 10


def ramp(t, a, b):
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def page_rows():
    """The real algebra for det(AB) with letters, expanded and refactored by sympy."""
    a, b, c, d, e, f, g, h = sp.symbols("a b c d e f g h")
    A, Bm = sp.Matrix([[a, b], [c, d]]), sp.Matrix([[e, f], [g, h]])
    P = A * Bm
    L = sp.latex
    p00p11, p01p10 = sp.expand(P[0, 0] * P[1, 1]), sp.expand(P[0, 1] * P[1, 0])
    return [r"AB = " + L(P).replace(r"\left[", r"\begin{bmatrix}", 1).replace(r"\begin{matrix}", "", 1)
            .replace(r"\end{matrix}\right]", r"\end{bmatrix}", 1),
            rf"\det(AB) = ({L(P[0, 0])})({L(P[1, 1])}) - ({L(P[0, 1])})({L(P[1, 0])})",
            rf"= {L(p00p11)}",
            rf"\qquad - ({L(p01p10)})",
            rf"= {L(sp.expand(P.det()))}",
            r"= a d (e h - f g) - b c (e h - f g)",
            rf"= {L(sp.factor(P.det()))}",
            r"= \det(A)\,\det(B)"]


@scene(T.cut_ch7, T.cut_outro)
def s07_product(s):
    backdrop(s)
    old = s.manim(z=0.5)                              # Ch6's last frame
    m = s.manim(z=1)                                  # grid
    ar = s.manim(z=2)                                 # the square and its number
    g = s.manim(z=3)                                  # arrows
    pg = s.manim(z=4)                                 # the page of algebra
    hb = s.manim(z=5.5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)
    rail(hud, 7)
    t0 = T.cut_ch7

    # ── Ch6's last frame: the top-down floor and the red, flattened box with its mirrored R ──
    def S(p):
        return np.array([O6[0] + U6 * p[0], O6[1] + U6 * p[1], 0.0])
    floor = VGroup()
    for k in range(-9, 10):
        for a_, b_ in (((k, -9), (k, 9)), ((-9, k), (9, k))):
            ax = k == 0
            floor.add(Line(S(a_), S(b_), color=C.axis if ax else C.grid, stroke_width=C.thin * (1.5 if ax else 1.0),
                           stroke_opacity=1.0 if ax else 0.55))
    corners = [A30 @ c for c in CUBE]
    flat = VGroup(*[Polygon(*[S(corners[i]) for i in f_], stroke_color=C.collapse, stroke_width=C.thin + 0.6,
                            fill_color=C.collapse, fill_opacity=0.22) for f_ in FACES])
    R = tex("R", size=200)
    rx0, ry0 = R.get_corner(DL)[:2]
    rw, rh = R.width, R.height
    c1, c2 = A30[:, 0], A30[:, 1]
    R.apply_function(lambda p: S((0.2 + 0.6 * (p[0] - rx0) / rw) * c1 + (0.15 + 0.7 * (p[1] - ry0) / rh) * c2))
    R.set_fill(C.text, opacity=1).set_stroke(width=0)
    arrows6 = VGroup(*[Arrow(S((0, 0)), S(A30[:2, k]), buff=0, color=col, stroke_width=C.stroke + 1, tip_length=0.24,
                             max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=40)
                       for k, col in enumerate((C.ihat, C.jhat, C.khat))])
    old.add(floor, flat, R, arrows6)
    old.play(FadeOut(VGroup(flat, R, arrows6)), at=t0 + 0.1, dur=0.8, lead=0)
    old.play(FadeOut(floor), at=t0 + 0.6, dur=1.0, lead=0)

    # ── one score for the matrix: A, then B after it; then both again, one after the other; then back to rest ──
    w_a = (T.by5 - 1.3, T.by5 + 0.2)
    w_b = (T.another + 0.2, T.by2 + 0.5)
    w_rest = (T.both - 0.1, T.both + 0.8)
    w_a2 = (T.both + 0.9, T.both + 1.6)
    w_b2 = (T.both + 1.6, T.by10 - 0.1)
    w_out = (T.nothing + 1.0, T.cut_outro - 0.15)
    Mg = keys((t0, I2), (w_a[0], I2), (w_a[1], A_MAIN, E), (w_b[0], A_MAIN), (w_b[1], BA, E), (w_rest[0], BA),
              (w_rest[1], I2, E), (w_a2[0], I2), (w_a2[1], A_MAIN, E), (w_b2[1], BA, E), (w_out[0], BA),
              (w_out[1], I2, E), lead=0)
    g_in = (t0 + 0.6, t0 + 1.6)
    live(m, lambda t: grid_lines(Mg(t), O7, U7, FRAME, n=20, opacity=ramp(t, *g_in)),
         *[(a_, b_ + 0.1) for a_, b_ in (g_in, w_a, w_b, w_rest, (w_a2[0], w_b2[1]), w_out)])

    sq_on = (T.as_picture + 0.6, T.as_picture + 1.3)

    def square(t):
        k = ramp(t, *sq_on)
        M = Mg(t)
        out = VGroup(span_area(M, O7, U7, opacity=0.3 * k).set_stroke(opacity=k))
        c = pt(O7, U7, M @ np.array([0.5, 0.5]))
        lab = tex(num(det2(M)), size=60 if det2(M) > 2 else 44, color=C.area).move_to(c)
        out.add(lab.set_stroke(C.bg, width=5, background=True).set_opacity(k * (1 - ramp(t, w_out[0], w_out[0] + 0.5))))
        return out
    moving = tuple((a_, b_ + 0.1) for a_, b_ in (sq_on, w_a, w_b, w_rest, (w_a2[0], w_b2[1]), w_out))   # settle
    live(ar, square, *moving)
    live(g, lambda t: basis_arrows(Mg(t), O7, U7).set_opacity(ramp(t, *sq_on)), *moving)

    # ── the rule, at the top ──
    rule = tex(r"\det(AB)", "=", r"\det(A)", r"\,\det(B)", size=72).move_to([0.6, 3.15, 0])
    under = VGroup(*[tex(v, size=56, color=C.area).next_to(rule[i], DOWN, buff=0.25)
                     for v, i in (("10", 0), ("5", 2), ("2", 3))])
    rback = backing(VGroup(rule, under), pad=0.25)    # room for the numbers that arrive under the terms
    hb.play(FadeIn(rback), at=T.product - 0.3, dur=0.5)
    hud.play(Write(rule[0]), at=T.product, dur=1.0)
    hud.play(Write(VGroup(rule[1], rule[2], rule[3])), at=T.is_product, dur=1.2)

    # ── "prove it with algebra, and you will fill a page" ──
    rows = VGroup(*[MathTex(r_, font_size=34, color=C.muted) for r_ in page_rows()])
    y = 1.85
    for r_ in rows:
        r_.move_to([-6.6 + r_.width / 2, y - r_.height / 2, 0])
        y -= r_.height + 0.24
    pback = Rectangle(width=14.4, height=6.4, stroke_width=0, fill_color=C.bg, fill_opacity=1.0).move_to([0, -1.2, 0])
    pg.play(FadeIn(pback), at=T.page - 1.4, dur=0.4)
    pg.play(LaggedStart(*[Write(r_) for r_ in rows], lag_ratio=0.45), at=T.page - 1.2, dur=3.0)
    pg.play(FadeOut(rows, shift=2.5 * LEFT), FadeOut(pback), at=T.as_picture - 0.1, dur=0.8)

    # ── the counter: 1 → 5 → 10 ──
    cnt = tex("1", r"\xrightarrow{\;A\;}", "5", r"\xrightarrow{\;B\;}", "10", size=56,
              colors={0: C.area, 2: C.area, 4: C.area})
    cnt.move_to([-4.3, 0.75, 0])
    prod = tex("5", r"\times", "2", "=", "10", size=56, colors={0: C.area, 2: C.area, 4: C.area})
    prod.next_to(cnt, DOWN, buff=0.45)
    cback = backing(VGroup(cnt, prod), pad=0.3)
    hb.play(FadeIn(cback), at=T.as_picture + 0.6, dur=0.5)
    hud.play(FadeIn(cnt[0]), at=T.as_picture + 0.8, dur=0.5)
    hud.play(GrowFromEdge(cnt[1], LEFT), at=T.by5 - 1.2, dur=0.6)
    hud.play(FadeIn(cnt[2], scale=1.3), at=T.by5, dur=0.5)
    hud.play(GrowFromEdge(cnt[3], LEFT), at=T.another + 0.2, dur=0.6)
    hud.play(FadeIn(cnt[4], scale=1.3), at=T.by2 + 0.3, dur=0.5)
    hud.play(Write(prod), at=T.by10, dur=0.9)

    # ── the rule again, now with the numbers under each term ──
    under.set_stroke(C.bg, width=5, background=True)
    hud.play(LaggedStart(*[FadeIn(u_, shift=0.1 * DOWN) for u_ in under], lag_ratio=0.3), at=T.of_course - 0.2,
             dur=1.0)
    hud.play(Indicate(rule, color=C.area, scale_factor=1.0), at=T.nothing + 0.2, dur=1.0)

    # ── out: everything rests, the square is area one again ──
    hb.play(FadeOut(VGroup(rback, cback)), at=w_out[0], dur=0.8, lead=0)
    hud.play(FadeOut(VGroup(rule, under, cnt, prod)), at=w_out[0], dur=0.8, lead=0)

    finish(s)
