"""s04 the wrong guess: raise e to each entry. For A = [[0, −π], [π, 0]] that gives [[1, e^−π], [e^π, 1]] ≈
[[1, 0.04], [23.14, 1]], whose columns are parallel (det 0): used to move the plane, it folds every point onto one steep
line. Whatever solves x' = Ax, it is not this."""
from aion import *

from beats import T
from shots import EW_HOOK, HOOK, E, PLANE_BOX, PLANE_C, backdrop, finish, lab, live, panel, plane, tex

LX = -4.0                                              # the left column's centre
assert abs(np.linalg.det(EW_HOOK)) < 1e-12 and abs(EW_HOOK[1, 0] - 23.14) < 0.01


def grid_at(u):
    """The plane moved by (1 − u) I + u · ew(A): the identity folding into the element-wise guess."""
    return (1 - u) * np.eye(2) + u * EW_HOOK


@scene(T.cut_guess, T.cut_half)
def s04_wrong_guess(s):
    backdrop(s)
    m0 = s.manim(z=0)
    m = s.manim(z=1)

    # ── so what does it mean? ──
    eA = tex(r"e^{A}", size=72)
    eA[0][1].set_color(C.gen)
    eA.move_to([LX - 2.0, 2.55, 0])
    q = tex(r"\overset{?}{=}", size=60, color=C.muted).next_to(eA, RIGHT, buff=0.3)
    m.play(FadeIn(eA, scale=0.9), at=T.what_mean, dur=0.6)

    # ── the obvious guess: e to each entry ──
    guess = Mat([[r"e^{a}", r"e^{b}"], [r"e^{c}", r"e^{d}"]], colors=C.text, size=44, h_buff=1.05, v_buff=0.8)
    for row in guess.cells:
        for c in row:
            c[0][1].set_color(C.gen)
    guess.next_to(q, RIGHT, buff=0.3)
    m.play(FadeIn(q), FadeIn(guess, shift=0.1 * LEFT), at=T.each_entry + 0.3, dur=0.7)

    # ── a small matrix with pi and minus pi off the diagonal ──
    A_lab = tex("A", "=", size=52, colors={0: C.gen})
    A_mat = Mat([["0", r"-\pi"], [r"\pi", "0"]], colors=C.gen, size=48, h_buff=1.05, v_buff=0.8)
    A_row = VGroup(A_lab, A_mat).arrange(RIGHT, buff=0.25).move_to([LX, 0.2, 0])
    m.play(FadeIn(A_row, shift=0.1 * UP), at=T.small_matrix + 0.6, dur=0.7)

    # ── exponentiate every entry ──
    ex = Mat([[r"e^{0}", r"e^{-\pi}"], [r"e^{\pi}", r"e^{0}"]], colors=C.text, size=44, h_buff=1.15, v_buff=0.8)
    num = Mat(EW_HOOK, colors=C.wrong, size=44, h_buff=1.3, v_buff=0.8, places=2)
    arrow_d = tex(r"\Downarrow", size=44, color=C.muted).move_to([LX, -1.0, 0])
    ex.move_to([LX, -2.35, 0])
    num.move_to(ex)
    ebe = lab("entry by entry", 24, C.wrong).next_to(arrow_d, RIGHT, buff=0.25)
    m.play(FadeIn(arrow_d), FadeIn(ebe), TransformFromCopy(A_mat, ex), at=T.exponentiate, dur=0.9, ease=E)
    m.play(ReplacementTransform(ex, num), at=T.exponentiate + 1.2, dur=0.8, ease=E)

    # ── use it to move the plane: everything folds onto one line ──
    fr = panel(*PLANE_BOX, fill=False)
    t_a, t_b = T.move_plane + 0.6, T.flattened + 0.3
    fold = keys((t_a, 0.0), (t_b, 1.0, "easy_ease"), lead=0)
    op = keys((T.move_plane - 0.3, 0.0), (T.move_plane + 0.3, 1.0), lead=0)
    m.play(Create(fr), at=T.move_plane - 0.2, dur=0.6)
    live(m0, lambda t: plane(grid_at(float(fold(t))), opacity=float(op(t))), (T.move_plane - 0.3, t_b + 0.05))

    det = tex(r"\det", "=", "0", size=44, colors={0: C.muted, 1: C.muted, 2: C.area}).next_to(num, RIGHT, buff=0.3)
    m.play(FadeIn(det, shift=0.1 * LEFT), at=T.flattened + 0.5, dur=0.6)

    # ── whatever solves those equations, it isn't this ──
    strike = VGroup(*[Line(mob.get_corner(DL) + 0.1 * (DL), mob.get_corner(UR) + 0.1 * UR, color=C.wrong,
                           stroke_width=C.stroke) for mob in (guess,)])
    m.play(Create(strike), VGroup(*guess.cols).animate.set_fill(opacity=0.4), guess.br.animate.set_stroke(opacity=0.4), at=T.isnt + 0.4, dur=0.6)
    # hand off: only the panel and the folded plane cross the cut (s05 unfolds them)
    m.play(FadeOut(VGroup(eA, q, guess, strike, A_row, arrow_d, ebe, num, det)), at=T.cut_half - 0.4, dur=0.5)
    finish(s)
