"""Ch4 · One move after another: shear, then rotate. Following i-hat and j-hat through both moves gives the columns of
the combined matrix, and writing that out in numbers is the row-times-column rule."""
from aion import *

from beats import T
from shots import (FRAME, I2, QUARTER, SHEAR, Mat, arrow, backdrop, backing, basis_arrows, finish, grid_lines, hat_at,
                   live, pt, rot2, tex)

O, U = (1.9, -1.9), 1.1
E = "smooth"
RS = QUARTER @ SHEAR                                   # [[0,-1],[1,1]]


@scene(T.cut_ch4, T.cut_order)
def s08_compose(s):
    backdrop(s)
    ghost = s.manim(z=0)
    m = s.manim(z=1)                                   # the grid
    g = s.manim(z=3)                                   # i-hat, j-hat, ghosts of the in-between spots
    lab = s.manim(z=4)
    veil = s.manim(z=4.5)                              # dims the grid for the derivation
    hb = s.manim(z=4.9, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)

    # ── the score: u1 = how far the shear has gone, u2 = how far the turn has gone; M = R(u2) S(u1) ──
    a0 = T.shear_rot + 0.2; a1 = a0 + 1.6             # shear the plane
    b0 = T.shear_rot + 1.75; b1 = b0 + 1.6            # and then rotate it
    c0 = T.follow + 0.3; c1 = c0 + 1.2                # back to rest: follow the arrows one at a time
    d0 = T.ihat_stays + 0.4; d1 = d0 + 1.4            # the shear leaves i-hat ...
    e0 = T.sends_up - 0.35; e1 = e0 + 1.5             # ... the turn sends it up
    f0 = T.diag - 1.3; f1 = f0 + 0.9                  # back to rest
    g0 = T.diag - 0.1; g1 = g0 + 1.4                  # the shear tips j-hat onto the diagonal
    h0 = T.up_left - 1.9; h1 = h0 + 1.9               # the turn carries the diagonal up and left
    u1 = keys((a0, 0.0), (a1, 1.0, E), (c0, 1.0), (c1, 0.0, E), (d0, 0.0), (d1, 1.0, E), (f0, 1.0), (f1, 0.0, E),
              (g0, 0.0), (g1, 1.0, E), lead=0)
    u2 = keys((b0, 0.0), (b1, 1.0, E), (c0, 1.0), (c1, 0.0, E), (e0, 0.0), (e1, 1.0, E), (f0, 1.0), (f1, 0.0, E),
              (h0, 0.0), (h1, 1.0, E), lead=0)

    def M(t):
        return rot2(90 * u2(t)) @ (I2 + u1(t) * (SHEAR - I2))
    wins = [(a0, b1), (c0, c1), (d0, d1), (e0, e1), (f0, f1), (g0, g1), (h0, h1)]

    # ── the grid draws on, then the two arrows ──
    base = grid_lines(I2, O, U, FRAME)
    o3 = pt(O, U, (0, 0))

    def dist(ln):
        d = ln.get_end() - ln.get_start()
        return float(np.linalg.norm(np.cross(d, o3 - ln.get_start())) / np.linalg.norm(d))
    dim, major, axis = base
    t_in = T.cut_ch4 + 0.25
    m.play(LaggedStart(*[Create(ln) for ln in sorted(dim, key=dist)], lag_ratio=0.02), at=t_in, dur=1.4)
    m.play(LaggedStart(*[Create(ln) for ln in sorted(major, key=dist)], lag_ratio=0.04), at=t_in + 0.2, dur=1.4)
    m.play(LaggedStart(*[Create(ln) for ln in axis], lag_ratio=0.3), at=t_in + 0.4, dur=1.0)
    m.remove(base, *dim, *major, *axis, at=a0)
    live(m, lambda t: grid_lines(M(t), O, U, FRAME), *wins)
    ghost.add(grid_lines(I2, O, U, FRAME, color=C.ghost, axes=False), at=a0)

    a_in = basis_arrows(I2, O, U)
    g.play(GrowArrow(a_in[0]), GrowArrow(a_in[1]), at=t_in + 1.2, dur=0.8)
    g.remove(*a_in, at=a0)
    live(g, lambda t: basis_arrows(M(t), O, U), *wins)
    li = tex(r"\hat{\imath}", size=52, color=C.ihat).move_to(hat_at(I2, 0, O, U))
    lj = tex(r"\hat{\jmath}", size=52, color=C.jhat).move_to(hat_at(I2, 1, O, U))
    lab.play(FadeIn(li), FadeIn(lj), at=t_in + 1.6, dur=0.5)
    for a, b in wins:
        lab.drive(li, lambda mob, t: mob.move_to(hat_at(M(t), 0, O, U)), during=(a, b))
        lab.drive(lj, lambda mob, t: mob.move_to(hat_at(M(t), 1, O, U)), during=(a, b))

    # ── the queue: R written on the left of S, because it acts second; then "= its own matrix" ──
    R_m, S_m = Mat(QUARTER, size=44, h_buff=0.85, v_buff=0.7), Mat(SHEAR, size=44, h_buff=0.85, v_buff=0.7)
    C_m = Mat(RS, size=44, h_buff=0.85, v_buff=0.7)
    eq = tex("=")
    row = VGroup(R_m, S_m, eq, C_m).arrange(RIGHT, buff=0.3)
    row.move_to([-7.11 + C.margin + 0.35 + row.width / 2, 2.35, 0])
    lR = tex("R", size=40).next_to(R_m, UP, buff=0.22)
    lS = tex("S", size=40).next_to(S_m, UP, buff=0.22).match_y(lR)
    lC = tex("RS", size=40).next_to(C_m, UP, buff=0.22).match_y(lR)
    panel_q = backing(VGroup(row, lR), pad=0.28)
    hb.play(FadeIn(panel_q), at=a0, dur=0.5)
    hud.play(FadeIn(VGroup(S_m, lS), shift=0.15 * DOWN), at=a0 + 0.1, dur=0.6)
    hud.play(FadeIn(VGroup(R_m, lR), shift=0.15 * DOWN), at=b0 + 0.1, dur=0.6)
    hud.play(FadeIn(eq), Create(C_m.br), FadeIn(lC), at=T.own_matrix + 0.35, dur=0.7)

    # ── i-hat's column ──
    lab.play(Indicate(li, color=C.ihat, scale_factor=1.3), at=T.ihat_stays + 1.0, dur=0.8)
    for j, (show, fly) in enumerate(((e1 + 0.05, T.col1 + 0.7), (h1 + 0.05, T.col2 + 0.6))):
        c = RS[:, j]
        col = (C.ihat, C.jhat)[j]
        tag = tex("(", str(int(c[0])), ",", str(int(c[1])), ")", size=38, colors={1: col, 3: col})
        tag.move_to(hat_at(RS, j, O, U, off=1.0))
        hud.play(FadeIn(tag, scale=0.8), at=show, dur=0.4, lead=0)
        hud.play(ReplacementTransform(tag[1], C_m.cell(0, j)), ReplacementTransform(tag[3], C_m.cell(1, j)),
                 FadeOut(VGroup(tag[0], tag[2], tag[4])), at=fly, dur=0.8, ease=E)

    # j-hat's stop on the diagonal stays behind as a ghost
    diag_ghost = arrow(o3, pt(O, U, (1, 1)), C.jhat, width=C.stroke, opacity=0.35)
    diag_line = DashedLine(pt(O, U, (-2.2, -2.2)), pt(O, U, (2.2, 2.2)), dash_length=0.12, color=C.jhat,
                           stroke_width=C.thin, stroke_opacity=0.5)
    g.play(FadeIn(diag_ghost), Create(diag_line), at=g1 + 0.05, dur=0.6, lead=0)
    g.play(FadeOut(VGroup(diag_ghost, diag_line)), at=T.col2 + 0.4, dur=0.6)

    # ── what we just did: each column of S pushed through R ──
    dimmer = Rectangle(width=16, height=10, stroke_width=0, fill_color=C.bg, fill_opacity=0.93)
    veil.play(FadeIn(dimmer), at=T.look + 0.2, dur=0.8)
    hud.play(Indicate(C_m, color=C.text, scale_factor=1.08), at=T.look + 0.3, dur=0.8)

    def push(j):
        cs = SHEAR[:, j]
        out = RS[:, j]
        col = (C.ihat, C.jhat)[j]
        v = Mat([[cs[0]], [cs[1]]], colors=[col], size=44, v_buff=0.7)
        r = Mat([[out[0]], [out[1]]], colors=[col], size=44, v_buff=0.7)
        return VGroup(tex("R", size=48), v, tex("="), r).arrange(RIGHT, buff=0.22)
    p1, p2 = push(0), push(1)
    pushes = VGroup(p1, p2).arrange(RIGHT, buff=1.4).move_to([0, 0.15, 0])
    hud.play(FadeIn(p1[0]), TransformFromCopy(S_m.cols[0], p1[1].cols[0]), FadeIn(p1[1].br),
             at=T.pushed + 0.35, dur=0.8, ease=E)
    hud.play(FadeIn(p1[2:]), at=T.pushed + 1.6, dur=0.5)
    hud.play(FadeIn(p2[0]), TransformFromCopy(S_m.cols[1], p2[1].cols[0]), FadeIn(p2[1].br),
             at=T.pushed + 2.3, dur=0.8, ease=E)
    hud.play(FadeIn(p2[2:]), at=T.pushed + 3.0, dur=0.5)

    # ── written out in numbers: the row-times-column rule (grey bookkeeping, then coloured by column) ──
    cells = [[r"0\cdot 1 + (-1)\cdot 0", r"0\cdot 1 + (-1)\cdot 1"], [r"1\cdot 1 + 0\cdot 0", r"1\cdot 1 + 0\cdot 1"]]
    Rx = Mat(QUARTER, colors=C.text, size=40, h_buff=0.8, v_buff=0.66)
    Sx = Mat(SHEAR, size=40, h_buff=0.8, v_buff=0.66)
    Ex = Mat(cells, size=40, h_buff=3.3, v_buff=0.66)
    expand = VGroup(Rx, Sx, tex("="), Ex).arrange(RIGHT, buff=0.25).move_to([0, -2.0, 0])
    grey = expand.copy().set_color(C.muted)
    for br in (grey[0].br, grey[1].br, grey[3].br):
        br.set_color(C.text)
    hud.play(FadeIn(grey, shift=0.15 * UP), at=T.row_col - 1.9, dur=0.8)
    hud.play(FadeIn(expand), at=T.row_col + 0.3, dur=0.9)
    hud.remove(grey, at=T.row_col + 1.3)
    hud.play(Indicate(Ex.cols[0], color=C.ihat, scale_factor=1.06), at=T.row_col + 1.4, dur=0.8)
    hud.play(Indicate(Ex.cols[1], color=C.jhat, scale_factor=1.06), at=T.row_col + 2.2, dur=0.8)

    # ── clear for s09 ──
    t_out = T.written + 1.4
    hud.play(FadeOut(VGroup(row, lR, lS, lC, pushes, expand)), at=t_out, dur=0.6)
    hb.play(FadeOut(panel_q), at=t_out, dur=0.6)
    veil.play(dimmer.animate.set_fill(opacity=1.0), at=t_out, dur=0.6)
    lab.play(FadeOut(VGroup(li, lj)), at=t_out, dur=0.6)
    finish(s)
