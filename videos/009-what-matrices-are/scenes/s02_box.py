"""Ch1 · Nine numbers in a box (1/2): the plain facts. A rectangle of numbers, its size (rows, then columns: 2 × 3),
every entry's address (row 2, column 3: a₂₃). It can hold anything: three equations lose their letters and what is
left is a matrix of coefficients plus a column of right-hand sides, parked in the corner for chapter 5."""
from aion import *

from beats import T
from shots import Mat, backdrop, finish, parked_system, system_mats, tex

E = "smooth"
M23 = [[4, -1, 7], [0, 2, 5]]
# the three equations, term by term: (coefficient shown, letter) and the sign before each later term
TERMS = [[("", "x"), ("", "y"), ("", "z")], [("", "x"), ("", "y"), ("2", "z")], [("2", "x"), ("", "y"), ("", "z")]]
OPS = [["+", "+"], ["-", "+"], ["+", "-"]]
RHS_S = ["4", "1", "3"]


@scene(T.cut_ch1, T.cut_photo)
def s02_box(s):
    backdrop(s)
    hb = s.manim(z=4.9, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)

    # ── a rectangle of numbers ──
    box = Mat(M23, colors=C.data, size=72, h_buff=1.35, v_buff=1.0).move_to([0, 0.3, 0])
    hud.play(FadeIn(box.br, scale=0.95), at=T.plain + 1.2, dur=0.7)
    hud.play(LaggedStart(*[FadeIn(box.cell(i, j), scale=0.9) for i in range(2) for j in range(3)], lag_ratio=0.12),
             at=T.rectangle + 0.2, dur=1.0)

    def band(mobs):
        return SurroundingRectangle(VGroup(*mobs), buff=0.16, stroke_color=C.frame, stroke_width=1.5,
                                    fill_color=C.data, fill_opacity=0.08)
    rows = [band([box.cell(i, j) for j in range(3)]) for i in range(2)]
    cols = [band([box.cell(i, j) for i in range(2)]) for j in range(3)]
    t_rows = T.rectangle + 2.6                          # "... as rows,"
    for i, b in enumerate(rows):
        hud.play(FadeIn(b), at=t_rows + 0.3 * i, dur=0.3)
        hud.play(FadeOut(b), at=t_rows + 0.3 * i + 0.45, dur=0.3)
    n_r = tex("2", size=56, color=C.muted).next_to(box.br, LEFT, buff=0.45)
    hud.play(FadeIn(n_r, shift=0.15 * RIGHT), at=t_rows + 0.5, dur=0.4)
    t_cols = T.two_by_three - 1.25                      # "... then columns,"
    for j, b in enumerate(cols):
        hud.play(FadeIn(b), at=t_cols + 0.25 * j, dur=0.25)
        hud.play(FadeOut(b), at=t_cols + 0.25 * j + 0.4, dur=0.25)
    n_c = tex("3", size=56, color=C.muted).next_to(box.br, DOWN, buff=0.35)
    hud.play(FadeIn(n_c, shift=0.15 * UP), at=t_cols + 0.6, dur=0.4)
    size = tex("2", r"\times", "3", size=64).next_to(box.br, UP, buff=0.5)
    hud.play(FadeIn(size[0]), at=T.two_by_three, dur=0.4)
    hud.play(FadeIn(size[1]), FadeIn(size[2]), at=T.two_by_three + 0.4, dur=0.4)
    hud.play(FadeOut(n_r), FadeOut(n_c), at=T.two_by_three + 0.9, dur=0.5)

    # ── every entry has an address ──
    tgt = box.cell(1, 2)
    hud.play(Indicate(tgt, color=C.text, scale_factor=1.3), at=T.address + 0.4, dur=0.8)
    rb, cb = band([box.cell(1, j) for j in range(3)]), band([box.cell(i, 2) for i in range(2)])
    hud.play(FadeIn(rb), at=T.which_row + 0.1, dur=0.4)
    hud.play(FadeIn(cb), at=T.which_col + 0.1, dur=0.4)
    addr = tex("a_{23}", "=", "5", size=60).next_to(box.br, RIGHT, buff=0.55).set_y(tgt.get_y())
    hud.play(FadeIn(addr, scale=0.6), at=T.which_col + 0.6, dur=0.6, ease="out_back")
    hud.play(FadeOut(VGroup(box, rb, cb, size, addr)), at=T.anything - 0.6, dur=0.6)

    # ── three equations; strip the letters and what's left is a matrix ──
    final = system_mats(60).move_to([0, 0.2, 0])
    cm, rm = final
    X0, DX, Y0, DY = -3.4, 2.15, 1.15, 0.95
    letters, ops, left, empty, rhs = VGroup(), VGroup(), [], [], VGroup()
    for i in range(3):
        y = Y0 - i * DY
        for j, (c, v) in enumerate(TERMS[i]):
            term = tex(c or r"\,", v, size=60, colors={0: C.data, 1: C.vec})
            term.shift([X0 + j * DX + 0.2 - term[1].get_x(), y - term[1].get_y(), 0])
            lt = term[1]
            letters.add(lt)
            piece = VGroup()
            if j > 0:
                op = tex(OPS[i][j - 1], size=60).move_to([X0 + (j - 0.5) * DX + 0.1, y, 0])
                (piece if OPS[i][j - 1] == "-" else ops).add(op)
            if c:
                piece.add(term[0])
            (left.append((piece, cm.cell(i, j))) if len(piece) else empty.append(cm.cell(i, j)))
        eqsign = tex("=", size=60).move_to([X0 + 2 * DX + 1.05, y, 0])
        r = tex(RHS_S[i], size=60, color=C.target).move_to([X0 + 2 * DX + 1.85, y, 0])
        ops.add(eqsign)
        rhs.add(r)
    whole = VGroup(letters, ops, rhs, *[p for p, _ in left])
    shift = np.array([0.0, 0.2 - whole.get_y(), 0])
    for mob in (letters, ops, rhs, *[p for p, _ in left]):
        mob.shift(shift)
    rows_v = [VGroup(*[mb for mb in [*letters, *ops, *rhs, *[p for p, _ in left]]
                       if abs(mb.get_y() - (Y0 - i * DY + shift[1])) < 0.3]) for i in range(3)]
    hud.play(LaggedStart(*[FadeIn(r, shift=0.1 * DOWN) for r in rows_v], lag_ratio=0.25), at=T.three_eq + 0.2,
             dur=1.4)
    hud.play(*[Indicate(lt, color=C.vec, scale_factor=1.2) for lt in letters], at=T.three_eq + 2.0, dur=0.8)
    hud.play(*[FadeOut(lt, shift=0.3 * UP) for lt in letters], at=T.strip + 0.2, dur=0.7)
    hud.play(FadeOut(ops), at=T.strip + 1.4, dur=0.5)
    hud.play(LaggedStart(*[ReplacementTransform(p, c) for p, c in left], lag_ratio=0.05),
             LaggedStart(*[ReplacementTransform(r, rm.cell(i, 0)) for i, r in enumerate(rhs)], lag_ratio=0.05),
             at=T.whats_left - 0.5, dur=1.0, ease=E)
    hud.play(*[FadeIn(c) for c in empty], at=T.whats_left - 0.1, dur=0.5)
    hud.play(FadeIn(cm.br), FadeIn(rm.br), at=T.whats_left + 0.2, dur=0.6)

    # remember them: parked at the lower left (s03 keeps them there)
    pk, pg = parked_system()
    hud.play(Transform(final, pg), at=T.remember_eq + 0.3, dur=1.1, ease=E)
    hb.play(FadeIn(pk), at=T.remember_eq + 1.2, dur=0.4)
    finish(s)
