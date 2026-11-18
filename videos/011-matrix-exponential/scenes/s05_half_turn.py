"""s05 the half turn: the folded plane unfolds and the real answer plays. A = πJ is a velocity field (orange arrows,
every point moving at A v); run that motion for one unit of time and every point swings to the opposite side: e^A = −I,
the same fact as e^{iπ} = −1. The picture to keep: a matrix is a motion, e^A is where the motion leaves everything.
Then a tease (e^{A+B} ≠ e^A e^B) and the map: a single number line now, the whole turning planet at the end."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import (EW_HOOK, HOOK, E, PLANE_BOX, PLANE_C, arrow, backdrop, backed, disc_points, field_arrows, finish,
                   flow_layers, globe_wire, lab, live, p3, panel, plane, tex, words)

R_DISC = 3.35
V = np.array([2.3, 1.05])                            # the white arrow followed through the first run
P = np.array([2.0, 1.25])                             # the marked point in the second run


@scene(T.cut_half, T.cut_ch1)
def s05_half_turn(s):
    backdrop(s)
    m0 = s.manim(z=0)                                 # the plane (rebuilt while it moves)
    mf = s.manim(z=1)                                 # the velocity field
    m = s.manim(z=4)                                  # labels, arrows, the map

    # ── unfold the wrong guess, then let the plane take the whole frame ──
    t_u0, t_u1 = T.real + 0.1, T.real + 1.4
    unfold = keys((t_u0, 1.0), (t_u1, 0.0, E), lead=0)
    slide = keys((t_u1, 0.0), (t_u1 + 1.1, 1.0, E), lead=0)
    run1 = (T.swings + 0.2, T.half + 0.3)
    run2 = (T.ends_up + 0.1, T.ends_up + 3.1)
    tau = keys((run1[0], 0.0), (run1[1], 1.0, E), (run2[0], 1.0), (run2[1], 2.0, E), lead=0)
    g_op = keys((t_u1, 1.0), (t_u1 + 1.1, 0.55), (T.start_line - 0.9, 0.55), (T.start_line - 0.2, 0.0), lead=0)

    def grid(t):
        u, sl = float(unfold(t)), float(slide(t))
        M = (1 - u) * expm(float(tau(t)) * HOOK) + u * EW_HOOK
        c = (1 - sl) * PLANE_C
        box = tuple((1 - sl) * np.array(PLANE_BOX) + sl * np.array((-7.4, -4.3, 7.4, 4.3)))
        return plane(M, center=c, box=box, opacity=float(g_op(t)), n=12)
    live(m0, grid, (T.cut_half, t_u1 + 1.15), run1, run2, (T.start_line - 0.9, T.start_line - 0.15))
    fr = panel(*PLANE_BOX, fill=False)
    m.add(fr)
    m.play(FadeOut(fr), at=t_u1 + 0.4, dur=0.7)

    # ── the velocity field of A = πJ ──
    field = field_arrows(HOOK, box=(-7.3, -4.2, 7.3, 4.2), spacing=0.75)
    mf.play(LaggedStart(*[GrowArrow(a) for a in field], lag_ratio=0.004), at=T.real + 2.6, dur=1.2)

    # ── particles: a disc of points that the motion carries ──
    X0 = disc_points(1800, R_DISC, seed=3)
    p_op = keys((T.minus_i - 1.2, 0.0), (T.minus_i - 0.4, 1.0), (T.start_line - 0.9, 1.0), (T.start_line - 0.2, 0.0),
                lead=0)
    flow_layers(s, X0, HOOK, tau, alpha=p_op, size=2.5, z=2, start=T.minus_i - 1.3, end=T.start_line)

    # ── e^A = −I ──
    A_m = VGroup(tex("A", "=", size=40, colors={0: C.gen}),
                 Mat([["0", r"-\pi"], [r"\pi", "0"]], colors=C.gen, size=36, h_buff=0.9, v_buff=0.66)).arrange(
        RIGHT, buff=0.2).move_to([-5.35, 1.35, 0])
    res = tex(r"e^{A}", "=", "-I", size=60)
    res[0][1].set_color(C.gen)
    res.move_to([-5.35, 2.85, 0])
    A_m, res = backed(A_m), backed(res)
    m.play(FadeIn(A_m), at=T.real + 2.8, dur=0.7)
    m.play(FadeIn(res, shift=0.1 * UP), at=T.minus_i, dur=0.8)

    # ── every point swings to the opposite side: follow one ──
    def v_arrow(t):
        R = expm(float(tau(t)) * HOOK)
        return arrow((0, 0), R @ V, C.text, width=C.stroke + 1.5)
    v_op = keys((T.swings - 0.8, 0.0), (T.swings - 0.3, 1.0), (T.outfit + 3.6, 1.0), (T.outfit + 4.2, 0.0), lead=0)
    hv = m.redraw(lambda t: v_arrow(t).set_opacity(float(v_op(t))), during=(T.swings - 0.8, T.outfit + 4.25))
    m.remove(hv, at=T.outfit + 4.3)
    vl = backed(tex(r"\mathbf v", size=44).next_to(p3(V), UR, buff=0.08), buff=0.08)
    ghost = arrow((0, 0), V, C.text, width=C.stroke, opacity=0.35)
    m.play(FadeIn(vl), at=T.swings - 0.3, dur=0.4)
    m.play(FadeOut(vl), at=run1[0] + 0.3, dur=0.3)
    mvl = backed(tex(r"-\mathbf v", size=44).next_to(p3(-V), DL, buff=0.08), buff=0.08)
    m.play(FadeIn(ghost), FadeIn(mvl), at=T.half, dur=0.5)
    s.camera.push(at=run1[0], zoom=1.06, dur=3.2)

    # ── the same fact in a different outfit ──
    euler = backed(tex(r"e^{i\pi}", "=", "-1", size=60, color=C.muted).move_to([5.35, 2.85, 0]))
    m.play(FadeIn(euler, shift=0.1 * LEFT), at=T.outfit + 0.6, dur=0.7)
    m.play(FadeOut(VGroup(ghost, mvl)), at=T.outfit + 3.6, dur=0.6)

    # ── the picture: a matrix is a motion (a velocity for every point) ──
    m.play(FadeOut(VGroup(euler, A_m)), FadeOut(res), at=T.picture, dur=0.6)
    mf.play(*[a.animate.set_stroke(width=C.thin + 1.6).set_opacity(1.0) for a in field], at=T.motion + 0.3, dur=0.5)
    mf.play(*[a.animate.set_stroke(width=C.thin + 0.6) for a in field], at=T.motion + 1.4, dur=0.6)

    def marker(t):
        R = expm((float(tau(t)) - 1.0) * HOOK)
        q = R @ P
        vel = HOOK @ q
        d = vel / np.linalg.norm(vel)
        return VGroup(arrow(q, q + 1.0 * d, C.gen, width=C.stroke + 2), Dot(p3(q), radius=0.1, color=C.text))
    mk_win = (T.motion + 1.0, run2[1] + 0.05)
    mk_op = keys((mk_win[0], 0.0), (mk_win[0] + 0.5, 1.0), (T.start_line - 0.9, 1.0), (T.start_line - 0.3, 0.0),
                 lead=0)
    live(m, lambda t: marker(t).set_opacity(float(mk_op(t))), (mk_win[0], mk_win[0] + 0.55), run2,
         (T.start_line - 0.9, T.start_line - 0.25))
    av = tex(r"A\mathbf v", size=44, colors={}).move_to(p3(P + [1.45, 0.95]))
    av[0][0].set_color(C.gen)
    av = backed(av, buff=0.08)
    vf = backed(lab("a velocity for every point", 30, C.gen)).move_to([4.6, 3.35, 0])
    m.play(FadeIn(vf, shift=0.1 * DOWN), at=T.motion + 0.3, dur=0.6)
    m.play(FadeOut(vf), at=T.breaks, dur=0.5)
    m.play(FadeIn(av), at=T.motion + 1.6, dur=0.5)
    m.play(FadeOut(av), at=run2[0], dur=0.3)

    # ── e^A is where everything ends up once that motion has run ──
    def trace(t):
        a = np.linspace(0, max(float(tau(t)) - 1.0, 1e-3), 80)
        pts = np.array([expm(x * HOOK) @ P for x in a])
        return VMobject(stroke_color=C.flow, stroke_width=C.stroke, stroke_opacity=float(mk_op(t))).set_points_smoothly(
            [p3(q) for q in pts])
    live(m, trace, run2, (T.start_line - 0.9, T.start_line - 0.25))
    eav = tex(r"e^{A}\mathbf v", size=48).next_to(p3(-P), LEFT, buff=0.35)
    eav[0][1].set_color(C.gen)
    eav = backed(eav, buff=0.08)
    m.play(FadeIn(eav, shift=0.1 * DOWN), at=run2[1] + 0.2, dur=0.6)

    # ── and one familiar rule is going to break ──
    tease = tex(r"e^{A+B}", r"\ne", r"e^{A}e^{B}", size=48, colors={1: C.comm}).move_to([4.9, -3.2, 0])
    tease = backed(tease)
    m.play(FadeIn(tease, scale=0.9), at=T.breaks + 0.3, dur=0.6)
    m.play(Indicate(tease[1][1], color=C.comm, scale_factor=1.4), at=T.breaks + 1.2, dur=0.7)

    # ── the map: a single number line now, the whole planet at the end ──
    m.play(FadeOut(VGroup(eav, tease)), at=T.start_line - 0.7, dur=0.6)
    mf.play(FadeOut(field), at=T.start_line - 0.7, dur=0.6)
    s.camera.push(at=T.start_line - 0.5, zoom=1.0, dur=0.8)
    NL0, NLU = np.array([-6.3, 0.0]), 0.95
    line = NumberLine(x_range=[0, 6, 1], length=6 * NLU, color=C.muted, stroke_width=C.thin + 0.4,
                      include_tip=False, tick_size=0.06).move_to(p3(NL0 + [3 * NLU, 0]))
    m.play(Create(line), at=T.start_line, dur=0.9)
    st_tag = lab("start", 30, C.vec).next_to(line, DOWN, buff=0.45)
    fin_tag = lab("finish", 30, C.globe).move_to([3.9, -2.55, 0])
    m.play(FadeIn(st_tag, shift=0.1 * UP), at=T.start_line + 0.5, dur=0.5)
    m.play(FadeIn(fin_tag, shift=0.1 * UP), at=T.planet + 0.6, dur=0.5)
    k = np.log(5.4) / max(T.cut_ch1 - T.start_line - 1.5, 1.0)

    def walker(t):
        x = np.exp(k * max(t - T.start_line - 0.8, 0.0))
        q = NL0 + [NLU * x, 0]
        return VGroup(arrow(q + [0, 0.32], q + [0, 0.32] + [0.45 * k * x * NLU + 0.05, 0], C.gen, width=C.stroke,
                            tip=0.14), Dot(p3(q), radius=0.1, color=C.vec))
    m.redraw(walker, during=(T.start_line + 0.5, T.cut_ch1))
    spin = Clock(start=T.planet)
    gop = keys((T.planet - 0.2, 0.0), (T.planet + 0.6, 1.0), lead=0)
    m.redraw(lambda t: globe_wire((3.9, 0.0), 1.9, 0.45 * float(spin(t)), op=float(gop(t))),
             during=(T.planet - 0.2, T.cut_ch1))
    finish(s)
