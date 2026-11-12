"""Ch4 · When the determinant is negative: swapped columns give -5, space is turned over, and the sign changes by
passing through zero."""
from aion import *

from beats import T
from shots import (A_MAIN, A_SWAP, FRAME, I2, Mat, backdrop, backing, basis_arrows, det2, finish, grid_lines,
                   lettered, live, matrix_panel, num, panel, pt, rail, span_area, tex, words)

E = "easy_ease"
G, UG = np.array([-6.3, -2.4]), 1.35                 # Ch3's drawing (the scene starts where Ch3 ended)
XE = 1.85                                            # Ch3's equals column
OB, UB = np.array([-0.4, -1.8]), 0.95                # the swap, on one full grid
R5, R10 = np.sqrt(5.0), np.sqrt(10.0)
AI, AJ = np.arctan2(1, 3), np.arctan2(2, 1)          # directions of (3, 1) and (1, 2)
OF, UF = np.array([-1.6, -1.0]), 1.0                 # the swing
GX, GY0, GS = 6.0, -0.2, 0.5                         # the determinant gauge: x, the y of zero, units per value


def ramp(t, a, b):
    """0 before a, 1 after b, smooth between."""
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def polar(r, a):
    return np.array([r * np.cos(a), r * np.sin(a)])


@scene(T.cut_ch4, T.cut_ch5)
def s04_sign(s):
    backdrop(s)
    old = s.manim(z=0)                                # Ch3's last frame, cleared at the start
    w = s.manim(z=1)                                  # grids
    pz = s.manim(z=1.5)                               # number line, side-by-side panels, the paper sheet, the summary
    a = s.manim(z=2)                                  # parallelograms
    r = s.manim(z=3)                                  # arrows
    hb = s.manim(z=5.5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)
    rail(hud, 4)
    t0 = T.cut_ch4

    # ── Ch3's last frame ──
    def P(x, y):
        return pt(G, UG, (x, y))
    o = P(0, 0)
    para = Polygon(o, P(3, 1), P(4, 3), P(1, 2), stroke_color=C.area, stroke_width=C.thin + 0.6,
                   fill_color=C.area, fill_opacity=0.3)
    rect = Polygon(o, P(4, 0), P(4, 3), P(0, 3), stroke_color=C.text, stroke_width=C.thin + 0.6, fill_opacity=0)
    ai = Arrow(o, P(3, 1), buff=0, color=C.ihat, stroke_width=C.stroke + 1, tip_length=0.26)
    aj = Arrow(o, P(1, 2), buff=0, color=C.jhat, stroke_width=C.stroke + 1, tip_length=0.26)
    braces = VGroup()
    for p0, p1, dirn, v, col in ((P(0, 0), P(3, 0), DOWN, "3", C.ihat), (P(3, 0), P(4, 0), DOWN, "1", C.jhat),
                                 (P(4, 0), P(4, 1), RIGHT, "1", C.ihat), (P(4, 1), P(4, 3), RIGHT, "2", C.jhat)):
        br = Brace(Line(p0, p1), dirn, buff=0.1, color=C.text)
        braces.add(br, tex(v, size=44, color=col).next_to(br, dirn, buff=0.1))
    M3 = Mat([["3", "1"], ["1", "2"]], colors=[C.ihat, C.jhat], size=56).move_to([4.6, 2.7, 0])
    r4 = lettered("=", "ad", "-bc", size=72).move_to([XE, 1.15, 0], aligned_edge=LEFT)
    dl = tex(r"\det", size=72)
    dl.move_to([XE - 0.25 - dl.width / 2, 1.15, 0])
    n1 = tex("=", "3", r"\cdot", "2", "-", "1", r"\cdot", "1", size=64,
             colors={1: C.ihat, 3: C.jhat, 5: C.jhat, 7: C.ihat}).move_to([XE, 0.0, 0], aligned_edge=LEFT)
    n2 = tex("=", "6", "-", "1", size=64).move_to([XE, -1.15, 0], aligned_edge=LEFT)
    n3 = tex("=", "5", size=80, colors={1: C.area}).move_to([XE, -2.35, 0], aligned_edge=LEFT)
    five = tex("5", size=96, color=C.area).move_to(P(2, 1.5)).set_stroke(C.bg, width=5, background=True)
    rest = VGroup(para, rect, ai, aj, braces, M3, r4[0], dl, n1, n2, n3, five)
    old.add(rest, r4[1], r4[2])
    old.play(FadeOut(rest), at=t0 + 0.15, dur=0.9, lead=0)

    # ── "a subtraction can fall below zero": ad − bc, centre stage, over a number line ──
    big = lettered("ad", "-bc", size=96).move_to([0, 1.45, 0])
    old.play(ReplacementTransform(VGroup(r4[1], r4[2]), big), at=t0 + 0.5, dur=1.2, lead=0)
    old.remove(big, at=T.below - 0.2)
    pz.add(big, at=T.below - 0.2)
    minus = big[1][0]
    pz.play(Indicate(minus, color=C.flip, scale_factor=1.8), at=T.below + 0.2, dur=1.0)

    NU, NY = 11 / 12, -1.0                            # number line: units per step, height

    def X(v):
        return np.array([v * NU, NY, 0.0])
    nl = VGroup(Line(X(-6.2), X(6.2), color=C.text, stroke_width=C.thin + 0.4))
    for k in range(-6, 7):
        hgt = 0.14 if k % 5 else 0.24
        nl.add(Line(X(k) + DOWN * hgt / 2, X(k) + UP * hgt / 2, color=C.text, stroke_width=C.thin + 0.4))
    for k in (-5, 0, 5):
        nl.add(tex(str(k), size=34, color=C.muted).next_to(X(k), DOWN, buff=0.28))
    tB = T.neg5 + 1.0                                 # the number line hands over to the grid
    pz.play(FadeIn(nl), at=T.below - 0.5, dur=0.8, lead=0)

    pos = Line(X(0), X(6.2), color=C.area, stroke_width=8, stroke_opacity=0.85)
    pos_tag = tex(r"\text{area}\,\geq 0", size=44, color=C.area).move_to([3.0 * NU, NY - 1.25, 0])
    pz.play(Create(pos), at=T.neg_area, dur=0.8)
    pz.play(FadeIn(pos_tag, shift=0.1 * UP), at=T.neg_area + 0.5, dur=0.6)

    vA = keys((t0, 5.0), (T.below + 0.3, 5.0), (T.neg_area + 0.1, 0.0, E), (T.neg5 - 0.4, 0.0),
              (T.neg5 + 0.7, -5.0, E), lead=0)

    def marker(t):
        v, k = vA(t), ramp(t, T.below - 0.5, T.below + 0.2) * (1 - ramp(t, tB - 0.25, tB + 0.3))
        col = C.area if v > 0.02 else C.flip if v < -0.02 else C.collapse
        p = X(v)
        tri = Polygon(p + [0, 0.14, 0], p + [-0.15, 0.42, 0], p + [0.15, 0.42, 0], stroke_width=0,
                      fill_color=col, fill_opacity=1)
        lab = tex(num(v), size=60, color=col).next_to(tri, UP, buff=0.14)
        return VGroup(tri, lab).set_opacity(k)
    hs = live(pz, marker, (T.below - 0.5, T.below + 0.2), (T.below + 0.3, T.neg_area + 0.1),
              (T.neg5 - 0.4, T.neg5 + 0.7), (tB - 0.25, tB + 0.3))
    pz.remove(hs[-1], at=tB + 0.35)
    pz.play(minus.animate.set_color(C.flip), at=T.neg5, dur=0.5)
    pz.play(FadeOut(VGroup(big, nl, pos, pos_tag)), at=tB - 0.25, dur=0.55, lead=0)

    # ── swap the columns: the grid is the same set of lines, only the arrows trade places ──
    gB = grid_lines(A_MAIN, OB, UB, FRAME, n=16)
    w.play(FadeIn(gB), at=tB + 0.1, dur=0.8, lead=0)

    def WB(v):
        return pt(OB, UB, v)
    pI = keys((t0, [R10, AI]), (T.i_j - 0.1, [R10, AI]), (T.i_j + 1.0, [R5, AJ], E), lead=0)
    pj = keys((t0, [R5, AJ]), (T.j_i - 0.5, [R5, AJ]), (T.j_i + 0.5, [R10, AI], E), lead=0)
    look_out = (T.look - 0.3, T.look + 0.3)

    def arrows_b(t):
        A = np.column_stack([polar(*pI(t)), polar(*pj(t))])
        k = ramp(t, tB + 0.5, tB + 1.1) * (1 - ramp(t, *look_out))
        ar = basis_arrows(A, OB, UB)
        return VGroup(ar[1], ar[0]).set_opacity(k)    # i-hat on top while the two overlap
    hs = live(r, arrows_b, (tB + 0.5, tB + 1.15), (T.i_j - 0.15, T.i_j + 1.05), (T.j_i - 0.55, T.j_i + 0.55),
              (look_out[0], look_out[1] + 0.05))
    r.remove(hs[-1], at=look_out[1] + 0.1)

    paraB = span_area(A_MAIN, OB, UB)
    lab5 = tex("5", size=80, color=C.area).move_to(WB((2, 1.5))).set_stroke(C.bg, width=5, background=True)
    a.play(FadeIn(paraB), FadeIn(lab5), at=tB + 1.0, dur=0.7, lead=0)
    a.play(FadeOut(VGroup(paraB, lab5)), at=T.swap, dur=0.5)

    outline = Polygon(*[WB(v) for v in ((0, 0), (1, 2), (4, 3), (3, 1))], stroke_color=C.text,
                      stroke_width=C.thin + 0.6, fill_color=C.area, fill_opacity=0)
    a.play(Create(outline), at=T.same_shape, dur=0.9)
    lab5b = lab5.copy()
    a.play(outline.animate.set_fill(opacity=0.3).set_stroke(C.area), FadeIn(lab5b, scale=1.2), at=T.same_area, dur=0.6)
    lab_n = tex("-5", size=80, color=C.flip).move_to(WB((2, 1.5))).set_stroke(C.bg, width=5, background=True)
    a.play(outline.animate.set_fill(C.flip, opacity=0.3).set_stroke(C.flip), FadeOut(lab5b), FadeIn(lab_n, scale=1.2),
           at=T.gives_neg + 0.3, dur=0.7)

    # the HUD: the matrix, its entries physically trade columns, then take the colour of the role they now play
    rd = tex(r"\det", "=", "-5", size=56, colors={2: C.flip})   # sized for -5; shows 5 first
    M, hats, back = matrix_panel([["3", "1"], ["1", "2"]], below=rd)
    rd5 = tex("5", size=56, color=C.area).move_to(rd[2], aligned_edge=LEFT)
    hb.play(FadeIn(back), at=tB + 0.5, dur=0.6, lead=0)
    hud.play(FadeIn(VGroup(M, hats, rd[0], rd[1], rd5)), at=tB + 0.6, dur=0.6, lead=0)
    hud.play(Swap(M.cols[0], M.cols[1]), at=T.swap + 0.1, dur=1.1)
    hud.play(FadeToColor(M.cols[1], C.ihat), at=T.i_j + 0.3, dur=0.6)
    hud.play(FadeToColor(M.cols[0], C.jhat), at=T.j_i + 0.3, dur=0.6)
    rd_n = rd[2]
    hud.play(FadeOut(rd5), FadeIn(rd_n, scale=1.3), at=T.gives_neg, dur=0.6)

    hb.play(FadeOut(back), at=look_out[0], dur=0.6, lead=0)
    hud.play(FadeOut(VGroup(M, hats, rd[0], rd[1], rd_n)), at=look_out[0], dur=0.6, lead=0)
    w.play(FadeOut(gB), at=look_out[0], dur=0.6, lead=0)
    a.play(FadeOut(VGroup(outline, lab_n)), at=look_out[0], dur=0.6, lead=0)

    # ── before and after, side by side: which way you turn from i-hat to reach j-hat ──
    def view(A, box, O, U, rows, val, col, turn_col):
        x0, y0, x1, y1 = box
        fr = panel(*box)
        gr = grid_lines(A, O, U, (x0 + 0.02, y0 + 0.02, x1 - 0.02, y1 - 0.02), n=14)
        sp = span_area(A, O, U)
        ar = basis_arrows(A, O, U, width=C.stroke)
        hi = tex(r"\hat{\imath}", size=40, color=C.ihat).next_to(ar[0].get_end(), RIGHT, buff=0.12)
        hj = tex(r"\hat{\jmath}", size=40, color=C.jhat).next_to(ar[1].get_end(), UP, buff=0.12)
        head = VGroup(tex(r"\det", size=44), Mat(rows, colors=[C.ihat, C.jhat], size=40), tex("=", size=44),
                      tex(val, size=48, color=col)).arrange(RIGHT, buff=0.18)
        hback = backing(head, pad=0.18)
        VGroup(head, hback).move_to([x0 + 0.3 + hback.width / 2, y1 - 0.3 - hback.height / 2, 0])
        a_i, a_j = np.arctan2(A[1, 0], A[0, 0]), np.arctan2(A[1, 1], A[0, 1])
        turn = Arc(radius=0.8 * U, start_angle=a_i, angle=a_j - a_i, arc_center=[*O, 0], color=turn_col,
                   stroke_width=C.stroke)
        turn.add_tip(tip_length=0.2, tip_width=0.2)
        return VGroup(fr, gr, sp, ar, hi, hj, hback, head), turn
    boxL, boxR = (-6.85, -3.35, -0.15, 3.35), (0.15, -3.35, 6.85, 3.35)
    vL, turnL = view(A_MAIN, boxL, np.array([-5.75, -2.6]), 0.9, [["3", "1"], ["1", "2"]], "5", C.area, C.area)
    vR, turnR = view(A_SWAP, boxR, np.array([1.25, -2.6]), 0.9, [["1", "3"], ["2", "1"]], "-5", C.flip, C.flip)
    pz.play(FadeIn(vL), FadeIn(vR), at=T.look - 0.1, dur=0.8, lead=0)
    pz.play(Create(turnL), at=T.left, dur=0.9)
    pz.play(Create(turnR), at=T.right, dur=0.9)
    pz.play(FadeOut(VGroup(vL, vR, turnL, turnR)), at=T.turned - 0.3, dur=0.6, lead=0)

    # ── a sheet of paper with an R on it, turned over onto its back ──
    SC, SW, SH = np.array([0.0, 0.1]), 7.2, 5.2
    sbox = (SC[0] - SW / 2, SC[1] - SH / 2, SC[0] + SW / 2, SC[1] + SH / 2)
    so, su = np.array([-2.5, -1.5]), 0.7
    sheet = VGroup(Rectangle(width=SW, height=SH, stroke_color=C.frame, stroke_width=C.thin, fill_color=C.bg2,
                             fill_opacity=1).move_to([*SC, 0]),
                   grid_lines(I2, so, su, (sbox[0] + 0.02, sbox[1] + 0.02, sbox[2] - 0.02, sbox[3] - 0.02), n=12),
                   basis_arrows(I2, so, su),
                   tex("R", size=300).move_to([1.35, 0.45, 0]))

    def turned(th):
        c, sn, D = np.cos(th), np.sin(th), 16.0

        def f(p):
            dx, dy = p[0] - SC[0], p[1] - SC[1]
            k = D / (D + dx * sn)                     # the far edge recedes
            return np.array([SC[0] + dx * c * k, SC[1] + dy * k, 0.0])
        return sheet.copy().apply_function(f)
    fl0, fl1 = T.paper + 0.4, T.paper + 2.6
    th = keys((fl0, 0.0), (fl1, PI, "in_out_sine"), lead=0)
    sheet0 = sheet.copy()
    pz.play(FadeIn(sheet0, scale=0.96), at=T.turned + 0.3, dur=0.6, lead=0)
    pz.remove(sheet0, at=fl0)
    h = pz.redraw(lambda t: turned(th(t)), during=(fl0, fl1))
    back_side = turned(PI)
    pz.add(back_side, at=fl1)
    pz.remove(h, at=fl1)
    pz.play(back_side[3].animate.set_color(C.flip), at=T.mirror, dur=0.6)
    pz.play(Indicate(back_side[3], color=C.flip, scale_factor=1.08), at=T.mirror + 0.6, dur=0.8)
    pz.play(FadeOut(back_side), at=T.sign - 0.4, dur=0.6, lead=0)

    # ── what the sign records: the size is the scaling, the sign is the flip ──
    eqE = tex(r"\det", "=", "-", "5", size=110, colors={2: C.flip, 3: C.area}).move_to([0, 0.9, 0])
    pz.play(Write(eqE), at=T.sign, dur=1.0)
    lab_size = tex(r"\text{area}\times 5", size=52, color=C.area).move_to([eqE[3].get_x() + 1.4, -1.0, 0])
    lab_flip = words("flipped", size=52, color=C.flip).move_to([eqE[2].get_x() - 1.6, -1.0, 0])
    ln_size = Line(eqE[3].get_bottom() + DOWN * 0.15, lab_size.get_top() + UP * 0.12, color=C.area,
                   stroke_width=C.thin + 0.4)
    ln_flip = Line(eqE[2].get_bottom() + DOWN * 0.3, lab_flip.get_top() + UP * 0.12, color=C.flip,
                   stroke_width=C.thin + 0.4)
    pz.play(Create(ln_size), FadeIn(lab_size, shift=0.1 * DOWN), at=T.size + 0.4, dur=0.7)
    pz.play(Create(ln_flip), FadeIn(lab_flip, shift=0.1 * DOWN), at=T.sign_flip, dur=0.7)
    pz.play(FadeOut(VGroup(eqE, lab_size, lab_flip, ln_size, ln_flip)), at=T.watch_sign - 0.35, dur=0.6, lead=0)

    # ── watch the sign change: j-hat swings through i-hat ──
    phi = keys((t0, AJ), (T.swing, AJ), (T.exact0, AI, "in_out_sine"), (T.exact0 + 0.5, AI),
               (T.other_side + 1.0, AI - np.pi / 4, "in_out_sine"), (T.doorway - 0.2, AI - np.pi / 4),
               (T.doorway + 1.8, AI, "in_out_sine"), lead=0)

    def AF(t):
        return np.column_stack([[3.0, 1.0], polar(R5, phi(t))])

    def kF(t):
        return ramp(t, T.watch_sign - 0.05, T.watch_sign + 0.75)
    fin = (T.watch_sign - 0.05, T.watch_sign + 0.8)
    sw = (fin, (T.swing - 0.05, T.exact0 + 0.02), (T.exact0 + 0.48, T.other_side + 1.02),
          (T.doorway - 0.22, T.doorway + 1.82))
    live(w, lambda t: grid_lines(AF(t), OF, UF, FRAME, n=16, opacity=kF(t)), *sw)
    live(r, lambda t: basis_arrows(AF(t), OF, UF).set_opacity(kF(t)), *sw)

    def area_f(t):
        A, k = AF(t), kF(t)
        d = det2(A)
        out = VGroup(span_area(A, OF, UF, opacity=0.3 * k).set_stroke(opacity=k))
        z = float(np.clip(1 - abs(d) / 0.6, 0, 1))
        if z > 0:                                     # near zero, the whole plane is one red line
            dirn = np.array([3.0, 1.0]) / R10
            seg = [pt(OF, UF, dirn * -9), pt(OF, UF, dirn * 9)]
            out.add(Line(*seg, color=C.collapse, stroke_width=6, stroke_opacity=z * k))
        return out
    live(a, area_f, *sw)
    orbit = DashedVMobject(Circle(radius=R5 * UF, color=C.faint, stroke_width=C.thin).move_to([*OF, 0]),
                           num_dashes=60)
    pz.play(Create(orbit), at=T.swing - 0.3, dur=0.8)

    # the gauge: a vertical number line, gold above zero, violet below
    def GY(v):
        return GY0 + v * GS
    gauge = VGroup(Line([GX, GY(-6.2), 0], [GX, GY(6.2), 0], color=C.text, stroke_width=C.thin + 0.4))
    for k in range(-6, 7):
        L = 0.24 if k % 5 == 0 else 0.13
        gauge.add(Line([GX - L / 2, GY(k), 0], [GX + L / 2, GY(k), 0], color=C.text, stroke_width=C.thin + 0.4))
    zero_tick = Line([GX - 0.3, GY(0), 0], [GX + 0.3, GY(0), 0], color=C.text, stroke_width=C.thin + 0.8)
    gauge.add(zero_tick)                              # the doorway: a longer tick at zero
    g_head = tex(r"\det", size=44).move_to([GX, GY(6.2) + 0.4, 0])
    gauge.add(g_head)
    gback = backing(VGroup(gauge, Line([GX - 1.05, 0, 0], [GX - 1.05, 0.01, 0]), Line([GX + 0.6, 0, 0], [GX + 0.6, 0.01, 0])), pad=0.2)
    hb.play(FadeIn(gback), at=T.watch_sign, dur=0.7, lead=0)
    hud.play(FadeIn(gauge), at=T.watch_sign + 0.1, dur=0.7, lead=0)

    def reading(t):
        d, k = det2(AF(t)), kF(t)
        col = C.area if d > 0.05 else C.flip if d < -0.05 else C.collapse
        y0, y1 = GY(0), GY(d)
        bar = Polygon([GX - 0.08, y0, 0], [GX + 0.08, y0, 0], [GX + 0.08, y1, 0], [GX - 0.08, y1, 0],
                      stroke_width=0, fill_color=col, fill_opacity=0.9)
        tick = Line([GX - 0.2, y1, 0], [GX + 0.2, y1, 0], color=col, stroke_width=C.stroke)
        val = tex(num(d), size=40, color=col)
        val.move_to([GX - 0.3 - val.width / 2, y1, 0])
        return VGroup(bar, tick, val).set_opacity(k)
    live(hud, reading, *sw)
    hud.play(Indicate(zero_tick, color=C.collapse, scale_factor=1.8), at=T.important, dur=1.0)

    finish(s)
