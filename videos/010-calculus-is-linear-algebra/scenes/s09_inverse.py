"""Ch4 (cont.): the hook explained, and an integral by inverse matrix. On (e^x cos x, e^x sin x) the derivative turns
by an eighth of a turn and stretches by √2: D = [[1, 1], [−1, 1]], det 2, nothing crushed, so it can be undone.
D⁻¹ = ½[[1, −1], [1, 1]] turns back and shrinks: D⁻¹(0, 1) = (−½, ½), i.e. ∫e^x sin x dx = ½e^x(sin x − cos x) + C;
one forward turn brings it back to (0, 1)."""
import sympy as sp

from aion import *

from beats import T
from shots import D_EXP, Mat, arrow, backdrop, finish, grid_lines, live, pt, rot2, tex

E = "easy_ease"
PO, PU = (-2.4, -0.6), 1.5                               # the plane, as s08 left it
BOX = (-6.9, -3.9, 2.2, 2.6)
RX = 5.0
D_INV = np.linalg.inv(D_EXP)
F = np.array([0.0, 1.0])                                 # f = e^x sin x
G = D_INV @ F                                            # its antiderivative's coordinates
assert np.isclose(np.linalg.det(D_EXP), 2) and np.allclose(D_INV, 0.5 * np.array([[1, -1], [1, 1]]))
assert np.allclose(G, [-0.5, 0.5]) and np.allclose(D_EXP @ G, F)
_x = sp.symbols("x")
assert sp.simplify(sp.diff(sp.exp(_x) * (sp.sin(_x) - sp.cos(_x)) / 2, _x) - sp.exp(_x) * sp.sin(_x)) == 0


def fwd(u):
    """From I (u = 0) to D (u = 1): turn clockwise by u/8 of a turn, stretch towards √2."""
    return (1 + (np.sqrt(2) - 1) * u) * rot2(-45 * u)


def back(u):
    """From I (u = 0) to D⁻¹ (u = 1): turn back by u/8 of a turn, shrink towards 1/√2."""
    return (1 + (1 / np.sqrt(2) - 1) * u) * rot2(45 * u)


assert np.allclose(fwd(1), D_EXP) and np.allclose(back(1), D_INV)


def ring(d, s_, col, size=36):
    off = {(0, 1): (0.62, 0.22), (1, 0): (0.62, 0.3), (0, -1): (0.75, -0.22), (-1, 0): (-0.72, 0.3)}[d]
    return tex(s_, size=size, color=col).move_to(pt(PO, PU, d) + np.array([*off, 0]))


@scene(T.cut_inverse, T.cut_ch5)
def s09_inverse(s):
    backdrop(s)
    m0 = s.manim(z=0)
    m = s.manim(z=1)
    t0 = T.cut_inverse
    z0 = pt(PO, 1.0, (0, 0))

    u1 = keys((T.eighth + 0.2, 0.0), (T.eighth + 1.8, 1.0, E), (T.trick + 0.2, 1.0), (T.trick + 1.4, 0.0, E), lead=0)
    u2 = keys((T.turn_back, 0.0), (T.turn_back + 1.6, 1.0, E), (T.check + 0.3, 1.0), (T.check + 1.6, 0.0, E), lead=0)
    bop = keys((T.swap_in + 0.6, 1.0), (T.swap_in + 1.4, 0.0), lead=0)             # s08's cos / sin arrows leave
    fop = keys((T.swap_in + 1.2, 0.0), (T.swap_in + 1.9, 1.0), (T.cut_ch5 - 0.75, 1.0), (T.cut_ch5 - 0.15, 0.0),
               lead=0)
    gop = keys((T.cut_ch5 - 0.75, 1.0), (T.cut_ch5 - 0.15, 0.0), lead=0)

    def stage(t):
        M = fwd(float(u1(t))) @ back(float(u2(t)))
        out = VGroup(grid_lines(M, PO, PU, BOX, n=8, opacity=0.6 * float(gop(t))))
        b = float(bop(t))
        if b > 0.01:
            for d, col in (((1, 0), C.b1), ((0, 1), C.b2)):
                out.add(arrow(z0, pt(PO, PU, d), col, width=C.stroke + 1.5, opacity=b))
        f = float(fop(t))
        if f > 0.01:
            out.add(arrow(z0, pt(PO, PU, M @ F), C.fn, width=C.stroke + 1.5, opacity=f))
        return out
    live(m0, stage, (t0, t0 + 0.05), (T.swap_in + 0.6, T.swap_in + 1.9), (T.eighth + 0.2, T.eighth + 1.8),
         (T.trick + 0.2, T.trick + 1.4), (T.turn_back, T.turn_back + 1.6), (T.check + 0.3, T.check + 1.6),
         (T.cut_ch5 - 0.75, T.cut_ch5 - 0.15))

    # s08's labels; the two negatives leave, cos and sin become e^x cos x and e^x sin x
    old = [ring((0, 1), r"\sin x", C.b2), ring((1, 0), r"\cos x", C.b1), ring((0, -1), r"-\sin x", C.b2),
           ring((-1, 0), r"-\cos x", C.b1)]
    m.add(*old, at=t0)
    m.play(FadeOut(old[2]), FadeOut(old[3]), at=T.secret + 0.3, dur=0.6)
    ls = tex(r"e^x\sin x", size=36, color=C.b2).next_to(pt(PO, PU, (0, 1.95)), RIGHT, buff=0.15)  # axis ends
    lc = tex(r"e^x\cos x", size=36, color=C.b1).next_to(pt(PO, PU, (2.55, 0)), UP, buff=0.15).shift(0.5 * LEFT)
    m.play(ReplacementTransform(old[0], ls), ReplacementTransform(old[1], lc), at=T.swap_in + 0.2, dur=1.0)

    # ── each derivative: an eighth of a turn, stretched by √2 ──
    Dm = Mat(D_EXP.astype(int), size=52, h_buff=0.9, v_buff=0.72)
    dl = tex(r"D", r"=", size=52, colors={0: C.op})
    dg = VGroup(dl, Dm).arrange(RIGHT, buff=0.25).move_to([RX, 1.2, 0])
    m.play(FadeIn(dg), at=T.eighth + 0.6, dur=0.7)
    turn = tex(r"\tfrac18\text{ turn}", r"\;\times\sqrt2", size=36, color=C.muted).next_to(dg, DOWN, buff=0.35)
    m.play(FadeIn(turn), at=T.eighth + 1.6, dur=0.6)

    # ── nothing crushed: det 2, so it can be undone ──
    det = tex(r"\det D", r"=", r"2", size=46, colors={2: C.dfn}).next_to(turn, DOWN, buff=0.45)
    was = tex(r"\det D_{\text{poly}}", r"=", r"0", size=34, colors={0: C.muted, 1: C.muted, 2: C.null})
    was.next_to(det, DOWN, buff=0.35)
    m.play(FadeIn(was, shift=0.1 * UP), at=T.crushes_nothing + 0.2, dur=0.5)
    m.play(FadeIn(det, shift=0.1 * UP), at=T.det_two, dur=0.6)

    # ── the integral, usually by parts twice ──
    line = tex(r"\int e^x\sin x\,dx", r"=", r"\tfrac12 e^x(", r"\sin x", r"-", r"\cos x", r")", r"+", r"C",
               size=48, colors={0: C.fn, 3: C.b2, 5: C.b1, 8: C.null}).move_to([0, 3.1, 0])
    m.play(FadeOut(VGroup(turn, was)), FadeIn(line[0], shift=0.1 * DOWN), at=T.trick + 0.5, dur=0.7)
    parts = tex(r"\text{by parts}", r"\times 2", size=38, color=C.muted).move_to([RX, -2.4, 0])
    m.play(FadeIn(parts), at=T.by_parts, dur=0.5)
    strike = Line(parts.get_corner(DL) + 0.08 * DL, parts.get_corner(UR) + 0.08 * UR, color=C.text,
                  stroke_width=C.stroke)
    m.play(Create(strike), at=T.inverse - 0.3, dur=0.4)

    # ── just the inverse: turn back an eighth, shrink by √2 ──
    Di = Mat([["1", "-1"], ["1", "1"]], size=52, h_buff=0.9, v_buff=0.72)
    dil = tex(r"D^{-1}", r"=", r"\tfrac12", size=52, colors={0: C.op})
    dig = VGroup(dil, Di).arrange(RIGHT, buff=0.2)
    dig.move_to([min(RX, 6.55 - dig.width / 2), dg.get_center()[1], 0])
    m.play(ReplacementTransform(dg, dig), FadeOut(VGroup(det, parts, strike)), at=T.inverse + 0.3, dur=0.8)
    # read the coordinates off the arrow: (−½, ½)
    tip = pt(PO, PU, G)
    dx = DashedLine(tip, pt(PO, PU, (G[0], 0)), color=C.b1, stroke_width=C.thin * 1.5, dash_length=0.08)
    dy = DashedLine(tip, pt(PO, PU, (0, G[1])), color=C.b2, stroke_width=C.thin * 1.5, dash_length=0.08)
    cx = tex(r"-\tfrac12", size=42, color=C.b1).next_to(pt(PO, PU, (G[0], 0)), DOWN, buff=0.15)
    cy = tex(r"\tfrac12", size=42, color=C.b2).next_to(pt(PO, PU, (0, G[1])), RIGHT, buff=0.15)
    tr = T.turn_back + 1.7
    m.play(Create(dx), Create(dy), FadeIn(cx), FadeIn(cy), at=tr, dur=0.7)

    # ── out comes ½ e^x (sin x − cos x) ──
    to = T.out_comes
    m.play(FadeIn(line[1]), TransformFromCopy(VGroup(cx, cy), VGroup(*line[2:7])), at=to, dur=1.1)

    # ── differentiate it: one forward turn, back to e^x sin x ──
    m.play(FadeOut(VGroup(dx, dy, cx, cy)), at=T.check, dur=0.4)
    ok = tex(r"\checkmark", size=48, color=C.dfn).move_to(pt(PO, PU, F) + np.array([-0.45, 0.25, 0]))
    m.play(FadeIn(ok, scale=0.6), at=T.check + 1.7, dur=0.5)

    # ── add the plus C ──
    m.play(FadeIn(line[7]), FadeIn(line[8], shift=0.2 * DOWN), at=T.plus_c2 + 0.2, dur=0.6)
    m.play(FadeOut(VGroup(line, dig, ok, ls, lc)), at=T.cut_ch5 - 0.75, dur=0.6)
    finish(s)
