"""s21 pill matrix (ch6): back to the pill. One number for the stomach (s, across), one for the blood (b, up): a state
plane beside the s02 body drawing. The stomach empties at a steady rate (−k_a), the blood gains what it loses (+k_a)
and is cleared in proportion (−k_e): A = [[−1, 0], [1, −1/4]] per hour, whose velocity field draws on the plane. The
whole story in one line: x(t) = e^{tA} x₀, with the state dot at (1, 0)."""
from aion import *

import ch6
from beats import T
from ch6 import PO2, PU, hero, pill_field, pill_matrix, plane_axes
from shots import E, Molecules, backdrop, backed, chapter_card, compartments, finish, p3, tex


@scene(T.cut_ch6, T.cut_curve)
def s21_pill_matrix(s):
    backdrop(s)
    mf = s.manim(z=1)
    m = s.manim(z=3)
    chapter_card(m, 6, "Back to the pill, and the planet", r"e^{tA}\mathbf x_0", T.cut_ch6)

    # ── the s02 body returns, molecules waiting in the stomach ──
    t_b = T.cut_ch6 + 2.8
    body = compartments()
    m.play(Create(body), at=t_b, dur=1.0, ease=E)
    mol = Molecules(n=400, seed=11, t0=1e9, sec_per_hour=ch6.SEC_PER_HOUR)
    op = keys((t_b + 0.5, 0.0), (t_b + 1.0, 1.0), lead=0)
    s.add(PointsLayer(mol.pos, color=C.vec, size=3.2, glow=0.0, alpha=op, additive=False, z=2, start=t_b + 0.4))

    # ── one number for the stomach, one for the blood ──
    ax = plane_axes()
    m.play(Create(ax[0]), FadeIn(ax[1]), at=T.stomach_num - 0.2, dur=0.8, ease=E)
    m.play(FadeIn(ax[2], shift=0.1 * UP), at=T.stomach_num + 0.3, dur=0.5)
    m.play(FadeIn(ax[3], shift=0.1 * UP), at=T.stomach_num + 1.9, dur=0.5)

    # ── the matrix: entries pulse as the story says them ──
    M = pill_matrix()
    m.play(FadeIn(M[:2], shift=0.1 * DOWN), at=T.empties - 0.6, dur=0.6)
    for at, (i, j) in ((T.empties + 0.3, (0, 0)), (T.gains + 0.3, (1, 0)), (T.proportion + 0.4, (1, 1))):
        m.play(Indicate(M[1].cell(i, j), color=C.text, scale_factor=1.4), at=at, dur=0.8)
    m.play(FadeIn(M[2:]), at=T.as_matrix - 0.2, dur=0.5)

    # ── as a velocity field on the state plane ──
    field = pill_field()
    order = sorted(field, key=lambda a: -a.get_start()[0])
    mf.play(LaggedStart(*[GrowArrow(a) for a in order], lag_ratio=0.02), at=T.as_matrix + 0.3, dur=1.4)

    # ── one line ──
    h = hero()
    m.play(Write(h), at=T.one_line + 0.2, dur=1.2)
    x0 = Dot(p3(PO2 + [PU, 0]), radius=0.11, color=C.vec)
    x0l = backed(tex(r"\mathbf x_0", size=36, color=C.vec), buff=0.04).next_to(x0, UP, buff=0.12)
    m.play(FadeIn(x0, scale=0.5), FadeIn(x0l), at=T.one_line + 1.6, dur=0.5)
    finish(s)
