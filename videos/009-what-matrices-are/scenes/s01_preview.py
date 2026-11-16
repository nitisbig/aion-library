"""Preview: not a table you read, a move you make. Unexplained glimpses of what is coming: the hero move and back,
two moves stacking (shear then turn), space folding flat onto a line, two directions that refuse to turn, a circle
pulled into an ellipse by rotate-stretch-rotate, the two arrows that record it all, and the photo reassembling."""
from functools import lru_cache

from aion import *

from beats import T
from shots import (A, COLLAPSE, FRAME, I2, SHEAR, Mat, arrow, backdrop, finish, grid_lines, live, pt, rank_k, rot2)

E = "smooth"
O, U_ = (0.0, -0.3), 0.8                                # the grid s00 leaves behind


def proper_svd2(M):
    U, s, Vt = np.linalg.svd(M)
    for i in range(2):
        if U[0, i] < 0:
            U[:, i] *= -1
            Vt[i] *= -1
    if np.linalg.det(U) < 0:
        U[:, 1] *= -1
        Vt[1] *= -1
    return s, np.degrees(np.arctan2(U[1, 0], U[0, 0])), np.degrees(np.arctan2(Vt[1, 0], Vt[0, 0]))


S2, TH_U, TH_V = proper_svd2(A)
assert np.allclose(rot2(TH_U) @ np.diag(S2) @ rot2(TH_V), A)
EIG = [np.array([1.0, 1.0]), np.array([0.5, -1.0])]     # A's two directions (lambda 4 and 1)
assert all(abs(np.linalg.det(np.c_[A @ v, v])) < 1e-9 for v in EIG)


def segments():
    """(t0, t1, f(u) -> matrix, ease): the preview's moves; between them the last matrix holds."""
    R = lambda u: rot2(90 * u) @ SHEAR                  # noqa: E731
    lerp = lambda P, Q: (lambda u: P + u * (Q - P))     # noqa: E731
    sv = [T.three_motions - 1.6, T.three_motions - 0.5, T.three_motions + 0.6, T.three_motions + 1.7]
    return [
        (T.move_you_make + 0.7, T.move_you_make + 2.9, lerp(I2, A), E),
        (T.picking_up + 2.9, T.picking_up + 4.3, lerp(A, I2), E),
        (T.two_moves + 0.3, T.two_moves + 1.5, lerp(I2, SHEAR), E),
        (T.two_moves + 1.7, T.two_moves + 3.0, R, E),
        (T.two_moves + 3.2, T.flat + 0.1, lerp(R(1), I2), E),
        (T.flat + 0.4, T.flat + 1.9, lerp(I2, COLLAPSE), E),
        (T.flat + 2.9, T.flat + 4.0, lerp(COLLAPSE, I2), "out_back"),
        (T.untouched + 0.2, T.untouched + 1.7, lerp(I2, A), E),
        (T.untouched + 2.8, T.untouched + 3.9, lerp(A, I2), E),
        (sv[0], sv[1], lambda u: rot2(TH_V * u), E),
        (sv[1] + 0.1, sv[2], lambda u: np.diag(1 + u * (S2 - 1)) @ rot2(TH_V), E),
        (sv[2] + 0.1, sv[3], lambda u: rot2(TH_U * u) @ np.diag(S2) @ rot2(TH_V), E),
    ]


SEGS = segments()
EASED = [keys((a, 0.0), (b, 1.0, e), lead=0) for a, b, _, e in SEGS]


def M(t):
    out = I2
    for (a, _, f, _), u in zip(SEGS, EASED):
        if t >= a:
            out = f(u(t))
    return out


@lru_cache(maxsize=48)
def layers(k):
    return rank_k(k)


@scene(T.cut_preview, T.cut_ch1)
def s01_preview(s):
    backdrop(s)
    assert np.allclose(M(T.cut_ch1), A)
    t_out = T.photograph - 0.2
    stage_op = keys((t_out, 1.0), (t_out + 0.7, 0.0), lead=0)
    m = s.manim(z=1, opacity=stage_op)
    hud = s.manim(z=5, parallax=0.0)

    # ── a table you read? No: a move you make ──
    Ag = Mat(A.astype(int), colors=C.muted, size=60, h_buff=0.85, v_buff=0.7)
    Ag.move_to([-7.11 + C.margin + 0.35 + Ag.width / 2, 3.55 - C.margin - Ag.height / 2, 0])
    Ac = Mat(A.astype(int), size=60, h_buff=0.85, v_buff=0.7).move_to(Ag)
    hud.play(FadeIn(Ag, shift=0.1 * DOWN), at=T.not_table - 0.1, dur=0.6)
    hud.play(FadeOut(Ag), FadeIn(Ac), at=T.move_you_make + 0.2, dur=0.6)
    hud.play(FadeOut(Ac), at=T.strange - 0.2, dur=0.5)

    # the live stage: the grid under M(t), the two arrows, plus whatever each glimpse needs
    z = pt(O, U_, (0, 0))
    circ = np.array([[np.cos(a), np.sin(a)] for a in np.linspace(0, 2 * np.pi, 97)])
    hat_op = keys((T.claim + 0.6, 0.0), (T.claim + 1.4, 1.0), lead=0)
    hat_w = keys((T.two_arrows + 0.1, 0.0), (T.two_arrows + 0.5, 1.0), (T.two_arrows + 1.7, 1.0),
                 (T.two_arrows + 2.3, 0.0), lead=0)
    null_op = keys((T.flat + 1.4, 0.0), (T.flat + 1.9, 1.0), (T.flat + 2.6, 1.0), (T.flat + 3.0, 0.0), lead=0)
    eig_op = keys((T.untouched - 0.3, 0.0), (T.untouched + 0.2, 1.0), (T.untouched + 2.6, 1.0),
                  (T.untouched + 3.2, 0.0), lead=0)
    cir_op = keys((T.three_motions - 2.1, 0.0), (T.three_motions - 1.6, 1.0), lead=0)

    def stage(t):
        Mt = M(t)
        out = VGroup(grid_lines(Mt, O, U_, FRAME, opacity=0.6))
        no = null_op(t)
        if no > 0.01:                                   # everything on this line lands on the origin
            d = np.array([1.0, -2.0]) / np.sqrt(5)
            out.add(Line(pt(O, U_, -6 * d), pt(O, U_, 6 * d), color=C.null, stroke_width=C.stroke + 1,
                         stroke_opacity=no))
        eo = eig_op(t)
        if eo > 0.01:
            for v in EIG:
                d = v / np.linalg.norm(v)
                out.add(Line(pt(O, U_, -9 * d), pt(O, U_, 9 * d), color=C.eigen, stroke_width=C.thin,
                             stroke_opacity=0.5 * eo))
                out.add(arrow(z, pt(O, U_, Mt @ v), C.eigen, width=C.stroke + 1, opacity=eo))
        co = cir_op(t)
        if co > 0.01:
            out.add(VMobject(stroke_color=C.sigma, stroke_width=C.stroke + 0.5, stroke_opacity=co)
                    .set_points_as_corners([pt(O, U_, Mt @ p) for p in circ]))
        ho = hat_op(t)
        if ho > 0.01:
            w = C.stroke + 1 + 2.5 * hat_w(t)
            for j, col in ((0, C.ihat), (1, C.jhat)):
                out.add(arrow(z, pt(O, U_, Mt[:, j]), col, width=w, opacity=ho))
        return out
    m.add(grid_lines(I2, O, U_, FRAME, opacity=0.6), at=T.cut_preview)
    wins = [(T.claim + 0.6, T.claim + 1.4), (T.flat + 1.4, T.flat + 3.0), (T.untouched - 0.3, T.untouched + 3.2),
            (T.three_motions - 2.1, T.three_motions - 1.6), (T.two_arrows + 0.1, T.two_arrows + 2.3)]
    wins += [(a, b) for a, b, _, _ in SEGS]
    live(m, stage, *wins)

    # ── and a photograph, reassembling layer by layer ──
    ticks = [T.photograph + 0.5 + 0.07 * i for i in range(40)]
    PH = 5.6

    def canvas(t):
        k = int(np.searchsorted(ticks, t, side="right"))
        return layers(max(k, 1))
    s.add(FramesLayer(canvas, height=PH, pos=(0.0, 0.0), z=2, start=t_out, during=[(ticks[0] - 0.01, ticks[-1] + 0.01)],
                      opacity=keys((ticks[0] - 0.1, 0.0), (ticks[0] + 0.3, 1.0), (T.cut_ch1 - 0.8, 1.0),
                                   (T.cut_ch1 - 0.1, 0.0), lead=0)))
    fr = Rectangle(width=PH, height=PH, stroke_color=C.frame, stroke_width=C.thin)
    hud.play(FadeIn(fr), at=ticks[0] - 0.1, dur=0.4)
    hud.play(FadeOut(fr), at=T.cut_ch1 - 0.8, dur=0.7)
    finish(s)
