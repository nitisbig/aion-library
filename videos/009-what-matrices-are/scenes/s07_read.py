"""Ch3 · Reading a matrix like a map: predict the quarter turn from its columns, then three columns in 3D decode the
opening box, and a video game turns a lit die by multiplying its corners by one rotation matrix, fresh every frame."""
from aion import *

from beats import T
from shots import (FRAME, GENTLE, H3, I2, I3, O3, U3, QUARTER, Cam, Mat, arrow, backdrop, backing, die_height,
                   die_rgba, finish, fmt, grid_lines, live, pt, rot2, rot3z, tex)

O, U = O3, U3
E = "smooth"
COLS3 = lambda: (C.ihat, C.jhat, C.khat)


def hat_pos(M, j, off=0.42):
    """Label spot beside the tip of column j of the 2x2 M, off to the side away from the other arrow."""
    d = M[:, j] / max(np.linalg.norm(M[:, j]), 1e-9)
    side = np.array([d[1], -d[0]]) if j == 0 else np.array([-d[1], d[0]])
    return pt(O, U, M[:, j]) + np.array([*(off * side + 0.12 * d), 0])


def floor(cam, L, minor_op):
    """The z = 0 grid seen through `cam`: integer lines out to |k| <= L (outer lines fade), each 2L long."""
    out = VGroup()
    K = int(np.ceil(L)) + 1
    for ax in (0, 1):
        for k2 in range(-2 * K, 2 * K + 1):
            k = k2 / 2
            minor = k2 % 2 != 0
            op = float(np.clip(L - abs(k) + 1, 0, 1)) * (minor_op if minor else 1.0)
            if op < 0.02:
                continue
            a, b = np.zeros(3), np.zeros(3)
            a[ax], b[ax] = -L, L
            a[1 - ax] = b[1 - ax] = k
            col = C.grid_minor if minor else (C.axis if k == 0 else C.grid)
            w = C.thin * (0.7 if minor else (1.5 if k == 0 else 1.0))
            out.add(Line(cam.scr(a), cam.scr(b), color=col, stroke_width=w, stroke_opacity=op))
    return out


@scene(T.cut_read, T.cut_ch4)
def s07_read(s):
    backdrop(s)
    gout = T.game_turn - 0.45                         # the 3D board fades out here, the die fades in
    gone = keys((gout, 1.0), (gout + 0.6, 0.0), lead=0)
    ghost = s.manim(z=0)
    m = s.manim(z=1, opacity=gone)                    # 2D grid, then the 3D floor and lattice
    ga = s.manim(z=1.5, opacity=gone)                 # basis arrows (2D, then 3D)
    s_die = 2                                         # the lit die (FramesLayer) sits at z=2
    g = s.manim(z=3)                                  # the die's corner dots
    lab = s.manim(z=4)                                # hats
    hb = s.manim(z=4.9, parallax=0.0)                 # panels behind the HUD
    hud = s.manim(z=5, parallax=0.0)                  # matrices

    # ── the 2D score: back to rest after s06, then (after the pause) a quarter turn ──
    r0, r1 = T.cut_read + 0.15, T.cut_read + 1.45
    q0, q1 = T.quarter - 0.15, T.quarter + 1.65
    reset = keys((r0, GENTLE), (r1, I2, E), lead=0)
    turn = keys((q0, 0.0), (q1, 90.0, E), lead=0)

    def M2(t):
        return reset(t) if t < q0 else rot2(turn(t))
    gh = grid_lines(I2, O, U, FRAME, color=C.ghost, axes=False)    # s06's ghost, hidden once the grid is back
    ghost.add(gh)
    ghost.remove(gh, at=r1)
    g_in, a_in = grid_lines(GENTLE, O, U, FRAME), basis_arrows2(GENTLE)   # s06's last frame
    m.add(g_in)
    ga.add(a_in)
    m.remove(g_in, at=r0)
    ga.remove(a_in, at=r0)
    grid2 = live(m, lambda t: grid_lines(M2(t), O, U, FRAME), (r0, r1), (q0, q1))
    arr2 = live(ga, lambda t: basis_arrows2(M2(t)), (r0, r1), (q0, q1))
    li = tex(r"\hat{\imath}", size=56, color=C.ihat).move_to(hat_pos(GENTLE, 0))
    lj = tex(r"\hat{\jmath}", size=56, color=C.jhat).move_to(hat_pos(GENTLE, 1))
    lab.add(li, lj)
    for a, b in ((r0, r1), (q0, q1)):
        lab.drive(li, lambda mob, t: mob.move_to(hat_pos(M2(t), 0)), during=(a, b))
        lab.drive(lj, lambda mob, t: mob.move_to(hat_pos(M2(t), 1)), during=(a, b))

    # ── try this one: read the columns before anything moves ──
    Q = Mat(QUARTER, size=56)
    hint_i = arrow([0, -0.3, 0], [0, 0.3, 0], C.ihat, width=C.stroke, tip=0.2).set_opacity(0.75)
    hint_j = arrow([0.3, 0, 0], [-0.3, 0, 0], C.jhat, width=C.stroke, tip=0.2).set_opacity(0.75)
    hint_i.next_to(Q.cols[0], DOWN, buff=0.55)
    hint_j.next_to(Q.cols[1], DOWN, buff=0.55).match_y(hint_i)
    box = VGroup(Q, hint_i, hint_j)
    box.move_to([-7.11 + C.margin + 0.3 + box.width / 2, 1.9, 0])
    qb = backing(box, pad=0.3)
    s1, s2 = Q.col_box(0, C.ihat), Q.col_box(1, C.jhat)
    hb.play(FadeIn(qb), at=T.try_this, dur=0.5)
    hud.play(Create(Q.br), at=T.try_this + 0.2, dur=0.6)
    hud.play(Write(Q.cols[0]), Write(Q.cols[1]), at=T.try_this + 0.5, dur=0.8)
    hud.play(FadeIn(s1), at=T.col1_says + 0.4, dur=0.5)
    hud.play(GrowArrow(hint_i), at=T.up + 0.6, dur=0.6)
    hud.play(FadeOut(s1), FadeIn(s2), at=T.col2_says + 0.3, dur=0.5)
    hud.play(GrowArrow(hint_j), at=T.left + 0.8, dur=0.6)
    hud.play(FadeOut(s2), at=T.predict, dur=0.6)
    # [pause 2.5]: the frame holds; the grid waits untouched until "It turns"
    hud.play(Indicate(hint_i, color=C.ihat, scale_factor=1.3), Indicate(hint_j, color=C.jhat, scale_factor=1.3),
             at=q1 + 0.2, dur=0.8)

    # ── 2D → 3D: the turned plane is the flat floor seen from above (az 90); the camera tips down ──
    p0, p1 = T.three_dims - 0.15, T.three_dims + 2.25
    tip = keys((p0, 0.0), (p1, 1.0, "easy_ease"), lead=0)
    AZ, EL, CO, CU = -30.0, 22.0, np.array([0.9, -0.7]), 1.75

    def cam_at(t):
        u = tip(t)
        return Cam(90 + (AZ - 90) * u, 90 + (EL - 90) * u, origin=(1 - u) * np.array(O) + u * CO,
                   unit=(1 - u) * U + u * CU)
    cam3 = cam_at(p1)
    hud.play(FadeOut(VGroup(Q, hint_i, hint_j)), at=p0 - 0.45, dur=0.5)
    hb.play(FadeOut(qb), at=p0 - 0.45, dur=0.5)
    lab.play(FadeOut(VGroup(li, lj)), at=p0 - 0.2, dur=0.4)
    m.remove(grid2[-1], at=p0)
    ga.remove(arr2[-1], at=p0)

    def arrows3(cam, M, which=(0, 1, 2)):
        o = cam.scr(np.zeros(3))
        return VGroup(*[arrow(o, cam.scr(M[:, j]), COLS3()[j], width=C.stroke + 1) for j in which])
    fl = live(m, lambda t: floor(cam_at(t), 10 - 9 * tip(t), max(0.0, 1 - 3 * tip(t))), (p0, p1))
    ar = live(ga, lambda t: arrows3(cam_at(t), I3, (0, 1)), (p0, p1))

    # three arrows, three columns: k-hat rises and the floor becomes a lattice
    k0 = T.three_cols + 0.2
    lat0 = lattice3(cam3, I3)
    m.play(FadeIn(lat0), at=k0, dur=1.0)
    m.play(FadeOut(fl[-1]), at=k0, dur=1.0)
    ga.remove(ar[-1], at=k0)
    base3 = arrows3(cam3, I3)
    ga.add(base3[0], base3[1], at=k0)
    ga.play(GrowArrow(base3[2]), at=k0, dur=0.8)

    def hat3_pos(cam, M, j):
        off = (np.array([0.25, -0.35, 0]), np.array([0.35, 0.2, 0]), np.array([-0.38, 0.12, 0]))[j]
        return cam.scr(M[:, j]) + off
    h3 = [tex(x, size=50, color=c) for x, c in zip((r"\hat{\imath}", r"\hat{\jmath}", r"\hat{k}"), COLS3())]
    for j, hj in enumerate(h3):
        hj.move_to(hat3_pos(cam3, I3, j))
        lab.play(FadeIn(hj, scale=0.8), at=k0 + 0.3 + 0.25 * j, dur=0.5, ease="out_back")

    # ── decode the box: each column of H flies out to its arrow ──
    Hm = Mat(H3, size=48, h_buff=0.85, v_buff=0.7).move_to([-5.15, 2.0, 0])
    hbk = backing(Hm, pad=0.3)
    hb.play(FadeIn(hbk), at=T.decode, dur=0.5)
    hud.play(FadeIn(Hm), at=T.decode + 0.15, dur=0.7)

    def partial(k):                                   # columns 0..k-1 have landed
        M = I3.copy()
        M[:, :k] = H3[:, :k]
        return M
    flights = [T.col1_3d + 1.2, T.col2_3d + 0.55, T.khat + 0.25]
    frames = []
    for j, tf in enumerate(flights):
        frames += [(tf - 0.15, partial(j)), (tf + 0.85, partial(j + 1), E)]
    Marr = keys(*frames, lead=0)
    ga.remove(*base3, at=flights[0] - 0.15)
    a3 = live(ga, lambda t: arrows3(cam3, Marr(t)), *[(tf - 0.15, tf + 0.85) for tf in flights])
    for j, tf in enumerate(flights):
        hud.play(Indicate(Hm.cols[j], color=COLS3()[j], scale_factor=1.15), at=tf - 0.6, dur=0.6)
        tag = Hm.cols[j].copy().scale(0.62).move_to(hat3_pos(cam3, H3, j) + np.array([0.55, 0.1, 0]))
        hud.play(TransformFromCopy(Hm.cols[j], tag), at=tf, dur=0.85, ease=E)
        hud.play(FadeOut(tag), at=tf + 1.5, dur=0.6)
        lab.drive(h3[j], lambda mob, t, j=j: mob.move_to(hat3_pos(cam3, Marr(t), j)), during=(tf - 0.15, tf + 0.85))

    # nine numbers, three arrows: the lattice follows (the opening move, now readable)
    n0, n1 = T.nine_three - 0.15, T.nine_three + 2.1
    Ml = keys((n0, I3), (n1, H3, E), lead=0)
    hud.play(Indicate(Hm, color=C.text, scale_factor=1.06), at=T.nine_three, dur=0.8)
    m.remove(lat0, at=n0)
    lt = live(m, lambda t: lattice3(cam3, Ml(t)), (n0, n1))

    # ── a video game: every corner of the die times one rotation matrix, fresh each frame ──
    m.remove(lt[-1], at=gout + 0.6)
    ga.remove(a3[-1], at=gout + 0.6)
    hud.play(FadeOut(Hm), at=gout, dur=0.5)
    hb.play(FadeOut(hbk), at=gout, dur=0.5)
    lab.play(FadeOut(VGroup(*h3)), at=gout, dur=0.5)

    g0 = T.game_turn + 0.35
    omega, ramp = 34.0, 1.2

    def theta(t):
        u = max(0.0, t - g0)
        return omega * (u * u / (2 * ramp) if u < ramp else u - ramp / 2)
    DC, DU, DAZ, DEL = np.array([2.3, -0.45]), 1.35, -35.0, 24.0
    dcam = Cam(DAZ, DEL, origin=DC, unit=DU)
    s.add(FramesLayer(lambda t: die_rgba(rot3z(theta(t)), az=DAZ, el=DEL, size=960),
                      height=die_height(DU), pos=tuple(DC), z=s_die, start=T.game_turn - 0.2,
                      opacity=fade(T.game_turn + 0.15, dur=0.6), during=[(g0, T.cut_ch4)]))

    corners = [np.array([x, y, z]) * 0.896 for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]

    def corner_dots(t):
        R = rot3z(theta(t))
        eye = dcam.eye()
        out = VGroup()
        for c in corners:
            if not any((R @ (np.sign(c[i]) * np.eye(3)[i])) @ eye > 0.22 for i in range(3)):
                continue                                   # all three faces at this corner look away
            out.add(Dot(dcam.scr(R @ c), radius=0.075, color=C.vec, stroke_color=C.bg, stroke_width=2.5))
        return out
    dd = corner_dots(g0)
    g.play(LaggedStart(*[FadeIn(d, scale=2.0) for d in dd], lag_ratio=0.12), at=T.corners + 0.4, dur=1.0)
    g.remove(*dd, at=T.corners + 1.25)
    live(g, corner_dots, (T.corners + 1.25, T.cut_ch4))

    # the matrix, recomputed every tick
    tick, t_first = 0.5, T.same_matrix + 0.3
    times = np.arange(t_first, T.cut_ch4 + 1e-6, tick)
    panel_ref = Mat(np.round(rot3z(-147.0), 2), size=40, h_buff=1.25, v_buff=0.66)
    th_ref = tex(r"\theta = ", r"000^\circ", size=40)
    block = VGroup(th_ref, panel_ref).arrange(DOWN, buff=0.35)
    block.move_to([-7.11 + C.margin + 0.3 + block.width / 2, 1.7, 0])
    hb.play(FadeIn(backing(block, pad=0.3)), at=T.same_matrix, dur=0.5)
    for k, tk in enumerate(times):
        th = theta(tk)
        R = rot3z(th)
        mk = Mat([[fmt(round(x, 2)) for x in row] for row in R], size=40, h_buff=1.25, v_buff=0.66).move_to(panel_ref)
        thk = tex(r"\theta = ", f"{int(round(th)) % 360}^\\circ", size=40).move_to(th_ref, aligned_edge=LEFT)
        frame_k = VGroup(thk, mk)
        if k == 0:
            hud.play(FadeIn(frame_k), at=tk, dur=0.4)
        else:
            hud.add(frame_k, at=tk - 0.15)
        if k + 1 < len(times):
            hud.remove(frame_k, at=times[k + 1] - 0.15)
    finish(s)


def basis_arrows2(M):
    return VGroup(*[arrow(pt(O, U, (0, 0)), pt(O, U, M[:, j]), c, width=C.stroke + 1)
                    for j, c in ((0, C.ihat), (1, C.jhat))])


def lattice3(cam, M):
    from shots import lattice
    return lattice(cam, M, n=1, box=2.4)
