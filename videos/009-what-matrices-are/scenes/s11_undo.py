"""Ch5 · The moves you can't undo (1/3): the hero A plays, then plays backwards; that reverse is A inverse and
A⁻¹A = I. The unit square's area grows by 4: the determinant. What if it were zero?"""
from aion import *

from beats import T
from shots import (A, FRAME, I2, O5, U5, Mat, backdrop, backing, basis_arrows, finish, grid_lines, live, pt, rail,
                   tex, unit_square)

E = "smooth"
PTS = np.array([(1, 1), (-1, 1), (1, -1), (2, 0), (0, 2)], float)   # a few points that ride out and back


@scene(T.cut_ch5, T.cut_collapse)
def s11_undo(s):
    backdrop(s)
    ghost = s.manim(z=0)
    m = s.manim(z=1)
    sq = s.manim(z=2)                                  # the unit square and its area readout
    g = s.manim(z=3)
    hb = s.manim(z=4.9, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)
    rail(hud, 4)

    # ── the score: forward, backward, forward + backward, then forward with the square, then rest ──
    f0 = T.tilts_grid + 0.2; f1 = f0 + 2.0
    b0 = T.reverse + 0.2; b1 = b0 + 2.0
    p0 = T.home - 0.1; p1 = p0 + 1.4                   # "do the move ..."
    q0 = p1 + 0.15; q1 = q0 + 1.5                      # "... then the inverse"
    s0 = T.square + 1.6; s1 = s0 + 2.0                 # the square during the move
    z0 = T.zero_q - 2.0; z1 = z0 + 1.4                 # back to rest for s12
    u = keys((f0, 0.0), (f1, 1.0, E), (b0, 1.0), (b1, 0.0, E), (p0, 0.0), (p1, 1.0, E), (q0, 1.0), (q1, 0.0, E),
             (s0, 0.0), (s1, 1.0, E), (z0, 1.0), (z1, 0.0, E), lead=0)

    def M(t):
        return I2 + u(t) * (A - I2)
    wins = [(f0, f1), (b0, b1), (p0, p1), (q0, q1), (s0, s1), (z0, z1)]

    base = grid_lines(I2, O5, U5, FRAME)
    m.play(FadeIn(base), at=T.cut_ch5 + 0.3, dur=0.8)
    m.remove(base, at=f0)
    live(m, lambda t: grid_lines(M(t), O5, U5, FRAME), *wins)
    ghost.add(grid_lines(I2, O5, U5, FRAME, color=C.ghost, axes=False), at=f0)
    a0 = basis_arrows(I2, O5, U5)
    g.play(FadeIn(a0), at=T.cut_ch5 + 0.6, dur=0.6)
    g.remove(a0, at=f0)

    dot_op = keys((T.square, 1.0), (T.square + 0.6, 0.0), lead=0)       # the riders leave when the square arrives

    def riders(t):
        Mt = M(t)
        o = dot_op(t)
        dots = [Dot(pt(O5, U5, Mt @ p), radius=0.08, color=C.vec).set_opacity(o) for p in PTS] if o > 0.01 else []
        return VGroup(basis_arrows(Mt, O5, U5), *dots)
    dots0 = VGroup(*[Dot(pt(O5, U5, p), radius=0.08, color=C.vec) for p in PTS])
    g.play(LaggedStart(*[FadeIn(d, scale=2) for d in dots0], lag_ratio=0.1), at=T.tilts_grid - 0.5, dur=0.6)
    g.remove(dots0, *dots0, at=f0)
    live(g, riders, *wins, (T.square, T.square + 0.6))
    home = VGroup(*[Circle(radius=0.16, color=C.vec, stroke_width=2).move_to(pt(O5, U5, p)) for p in PTS])
    g.play(LaggedStart(*[Create(c) for c in home], lag_ratio=0.08), at=q1 + 0.05, dur=0.5, lead=0)
    g.play(FadeOut(home), at=q1 + 1.2, dur=0.5, lead=0)

    # ── the panel: A, its inverse, A⁻¹A = I, det A = 4 ──
    Am = Mat(A, size=44, h_buff=0.85, v_buff=0.7)
    lA = tex("A", "=", size=48)
    rowA = VGroup(lA, Am).arrange(RIGHT, buff=0.2)
    inv = Mat([["2", "-1"], ["-2", "3"]], size=44, h_buff=0.85, v_buff=0.7)
    rowI = VGroup(tex("A^{-1}", "=", size=48), tex(r"\tfrac{1}{4}", size=48), inv).arrange(RIGHT, buff=0.18)
    prod = tex("A^{-1}", "A", "=", "I", size=56)
    det = tex(r"\det", "A", "=", "4", size=56, colors={3: C.area})
    stack = VGroup(rowA, rowI, prod, det).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
    stack.move_to([-7.11 + C.margin + 0.35 + stack.width / 2, 3.55 - C.margin - stack.height / 2, 0])
    panel = backing(stack, pad=0.28)
    hb.play(FadeIn(panel), at=T.hero, dur=0.5)
    hud.play(FadeIn(rowA, shift=0.15 * DOWN), at=T.hero + 0.2, dur=0.7)
    hud.play(FadeIn(rowI[0]), at=T.inverse - 0.2, dur=0.5)
    hud.play(FadeIn(rowI[1:], shift=0.15 * LEFT), at=T.inverse + 0.3, dur=0.7)
    hud.play(FadeIn(prod[:2]), at=T.identity - 2.1, dur=0.5)
    hud.play(FadeIn(prod[2:]), at=T.identity + 0.1, dur=0.6)

    # ── the unit square: its area goes 1 → 4 during the move ──
    sq0 = unit_square(I2)
    sq.play(FadeIn(sq0), at=T.square + 0.5, dur=0.6)
    sq.remove(sq0, at=s0)

    def square_now(t):
        Mt = M(t)
        val = float(np.linalg.det(Mt))
        poly = unit_square(Mt)
        num = DecimalNumber(val, num_decimal_places=1, font_size=40, color=C.text).move_to(poly.get_center())
        return VGroup(poly, num)
    sq.redraw(square_now, during=(s0, z1))
    hud.play(FadeIn(det[:3]), at=T.determinant + 0.3, dur=0.5)
    hud.play(FadeIn(det[3], scale=1.4), at=T.determinant + 0.7, dur=0.5, ease="out_back")

    # a pointer to video 006 (symbols only): a little card with the parallelogram and det
    card_sh = Polygon(*[np.array([x, y, 0]) for x, y in ((0, 0), (0.75, 0.25), (1.0, 0.85), (0.25, 0.6))],
                      stroke_color=C.area, stroke_width=2.5, fill_color=C.area, fill_opacity=0.3)
    card = VGroup(card_sh, tex(r"\det", size=40)).arrange(RIGHT, buff=0.3)
    card_box = SurroundingRectangle(card, buff=0.25, color=C.frame, stroke_width=1.5, fill_color=C.bg, fill_opacity=1)
    cardg = VGroup(card_box, card).move_to([5.3, -2.7, 0])
    hud.play(FadeIn(cardg, shift=0.2 * LEFT), at=T.own_video, dur=0.6)
    hud.play(FadeOut(cardg), at=T.own_video + 3.2, dur=0.6)

    # ── what if it were zero? ──
    q = tex(r"\det", "=", "0", "?", size=56, colors={2: C.null})
    q.move_to(det, aligned_edge=LEFT)
    hud.play(FadeOut(det, shift=0.15 * UP), FadeIn(q, shift=0.15 * UP), at=T.zero_q + 0.8, dur=0.6)
    finish(s)
