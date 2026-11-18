"""Ch4: the derivative is a rotation. In the plane with cos along one axis and sin along the other, 2 cos x + sin x is
the arrow (2, 1). D sends cos to −sin and sin to cos: both basis arrows turn a quarter turn clockwise, so D is the
rotation [[0, 1], [−1, 0]] and (2, 1) goes to (1, −2) = cos x − 2 sin x. Two turns point backwards (D² = −I), four come
home (D⁴ = I): sin, cos, −sin, −cos, the same quarter turn as i² = −1."""
from aion import *

from beats import T
from shots import chapter_header, D_TRIG, Mat, arrow, backdrop, finish, grid_lines, live, plot, pt, rot2, tex

E = "easy_ease"
PO, PU = (-2.4, -0.6), 1.5                               # the (cos, sin) plane
BOX = (-6.9, -3.9, 2.2, 2.6)
GO, GUX, GUY = (3.7, 2.0), 0.42, 0.32                    # the small graph, top right
RX = 5.0                                                 # the right-hand column's centre x
MIX = np.array([2.0, 1.0])

# D on (cos, sin) is a clockwise quarter turn; check it and the mixed arrow
assert np.allclose(D_TRIG, rot2(-90)) and np.allclose(D_TRIG @ D_TRIG, -np.eye(2))
assert np.allclose(np.linalg.matrix_power(D_TRIG, 4), np.eye(2)) and np.allclose(D_TRIG @ MIX, [1, -2])

RING = [((0, 1), r"\sin x", "b2"), ((1, 0), r"\cos x", "b1"), ((0, -1), r"-\sin x", "b2"), ((-1, 0), r"-\cos x", "b1")]


def ring_label(k, size=36):
    d, s_, role = RING[k]
    d = np.array(d, float)
    off = {(0, 1): (0.62, 0.22), (1, 0): (0.62, 0.3), (0, -1): (0.75, -0.22), (-1, 0): (-0.72, 0.3)}[tuple(int(v) for v in d)]
    return tex(s_, size=size, color=getattr(C, role)).move_to(pt(PO, PU, d) + np.array([*off, 0]))  # off the axes


def turns(t_list, start=0.0):
    """Angle track: a quarter turn clockwise at each (t0, t1)."""
    kf = [(t_list[0][0] - 1.0, start)]
    a = start
    for t0, t1 in t_list:
        kf += [(t0, a), (t1, a - 90.0, E)]
        a -= 90.0
    return keys(*kf, lead=0)


@scene(T.cut_ch4, T.cut_inverse)
def s08_rotation(s):
    backdrop(s)
    m0 = s.manim(z=0)
    m = s.manim(z=1)
    chapter_header(m, 4, T.cut_ch4)                     # chapter badge row + title (fills the cut)

    tq = T.quarter
    later = [(T.twice + 0.2, T.twice + 1.4), (T.full_turn + 0.2, T.full_turn + 1.2),
             (T.full_turn + 1.4, T.full_turn + 2.4)]
    ca = turns([(T.cos_swings + 0.2, T.cos_swings + 1.4)] + later)
    sa = turns([(T.sin_swings + 0.2, T.sin_swings + 1.4)] + later)
    ga = turns([(tq + 0.1, tq + 1.7)] + later)
    gop = keys((T.change_blocks - 0.3, 0.0), (T.change_blocks + 0.7, 1.0), lead=0)
    aop = keys((T.cos_sin - 0.2, 0.0), (T.cos_sin + 0.5, 1.0), lead=0)
    mop = keys((T.mix - 0.2, 0.0), (T.mix + 0.6, 1.0), (T.old_facts - 0.2, 1.0), (T.old_facts + 0.4, 0.0), lead=0)
    gh = keys((T.old_facts + 0.2, 0.0), (T.old_facts + 0.8, 1.0), (later[-1][1], 1.0), (later[-1][1] + 0.6, 0.0),
              lead=0)
    z0 = pt(PO, 1.0, (0, 0))

    def stage(t):
        g = float(ga(t))
        out = VGroup(grid_lines(rot2(g), PO, PU, BOX, n=8, opacity=0.6 * float(gop(t))))
        h = float(gh(t))
        if h > 0.01:                                   # where cos and sin started, for comparison
            for d in ((1, 0), (0, 1)):
                out.add(arrow(z0, pt(PO, PU, d), C.ghost, width=C.stroke, opacity=0.6 * h))
        mo = float(mop(t))
        if mo > 0.01:
            u = float(np.clip(-g / 90.0, 0, 1))
            out.add(arrow(z0, pt(PO, PU, rot2(g) @ MIX), interpolate_color(ManimColor(C.fn), ManimColor(C.dfn), u), width=C.stroke + 1.5,
                          opacity=mo))
        a = float(aop(t))
        if a > 0.01:
            for ang, col in ((float(ca(t)), C.b1), (float(sa(t)) + 90.0, C.b2)):
                out.add(arrow(z0, pt(PO, PU, rot2(ang) @ [1.0, 0.0]), col, width=C.stroke + 1.5, opacity=a))
        return out
    live(m0, stage, (T.change_blocks - 0.3, T.change_blocks + 0.7), (T.cos_sin - 0.2, T.cos_sin + 0.5),
         (T.mix - 0.2, T.mix + 0.6), (T.cos_swings + 0.2, T.cos_swings + 1.4), (T.sin_swings + 0.2, T.sin_swings + 1.4),
         (tq + 0.1, tq + 1.7), (T.old_facts - 0.2, T.old_facts + 0.8), *later, (later[-1][1], later[-1][1] + 0.6))

    # ── cos and sin: the two axes ──
    rl = [ring_label(k) for k in range(4)]
    m.play(FadeIn(rl[0]), FadeIn(rl[1]), at=T.cos_sin + 0.1, dur=0.6)

    # ── a mix is an arrow: 2 cos x + sin x = (2, 1), with its graph ──
    tip = pt(PO, PU, MIX)
    ml = tex(r"2\cos x + \sin x", size=36, color=C.fn).next_to(tip, UP, buff=0.15)
    gax = VGroup(Line(pt(GO, 1, (-0.1, 0)), pt(GO, 1, (GUX * 2 * np.pi + 0.1, 0)), color=C.axis, stroke_width=C.thin),
                 Line(pt(GO, 1, (0, -0.85)), pt(GO, 1, (0, 0.85)), color=C.axis, stroke_width=C.thin))
    g1 = plot(lambda x: 2 * np.cos(x) + np.sin(x), 0, 2 * np.pi, GO, GUX, GUY, C.fn)
    m.play(FadeIn(ml), FadeIn(gax), Create(g1), at=T.mix + 0.4, dur=1.0)
    # a dot glides along the small graph (the function the arrow stands for)
    t_a, t_q, t_b, t_e = T.mix + 1.6, T.quarter, T.quarter + 2.4, T.old_facts - 0.2
    gop_ = keys((t_a, 0.0), (t_a + 0.5, 1.0), (t_q - 0.4, 1.0), (t_q, 0.0), (t_b, 0.0), (t_b + 0.5, 1.0), (t_e, 1.0),
                (t_e + 0.4, 0.0), lead=0)

    def glide(t):
        x = 2 * np.pi * (((t - t_a) / 7.0) % 1.0)
        y = (2 * np.cos(x) + np.sin(x)) if t < t_q + 1.0 else (np.cos(x) - 2 * np.sin(x))
        col = C.fn if t < t_q + 1.0 else C.dfn
        return Dot(pt(GO, 1, (GUX * x, GUY * y)), radius=0.07, color=col).set_opacity(float(gop_(t)))
    m.redraw(glide, during=(t_a, t_e + 0.4))

    # ── cos' = −sin, sin' = cos ──
    e1 = tex(r"(\cos x)'", r"=", r"-\sin x", size=40, colors={0: C.b1, 2: C.b2}).move_to([RX, 0.45, 0])
    e2 = tex(r"(\sin x)'", r"=", r"\cos x", size=40, colors={0: C.b2, 2: C.b1}).move_to([RX, -0.45, 0])
    e2.align_to(e1, LEFT)
    m.play(FadeIn(e1, shift=0.1 * UP), at=T.cos_deriv, dur=0.6)
    m.play(FadeIn(e2, shift=0.1 * UP), at=T.sin_deriv, dur=0.6)

    # ── where does the cos arrow go? pause and predict ──
    m.play(Indicate(rl[1], color=C.b1, scale_factor=1.3), at=T.where_go + 0.6, dur=0.9)
    q = tex("?", size=64, color=C.muted).move_to(pt(PO, PU, (0.75, -0.75)))
    m.play(FadeIn(q), at=T.predict1 + 0.6, dur=0.5)
    m.play(FadeOut(q), at=T.cos_swings - 0.2, dur=0.4)

    # ── cos swings down to −sin; sin swings right to cos ──
    m.play(FadeIn(rl[2]), Indicate(e1[2], color=C.b2), at=T.cos_swings + 1.3, dur=0.6)
    m.play(Indicate(rl[1], color=C.b1, scale_factor=1.2), Indicate(e2[2], color=C.b1), at=T.sin_swings + 1.3, dur=0.6)

    # ── both turn a quarter: the whole plane turns, (2, 1) → (1, −2) ──
    tip2 = pt(PO, PU, D_TRIG @ MIX)
    ml2 = tex(r"\cos x - 2\sin x", size=36, color=C.dfn).next_to(tip2, RIGHT, buff=0.15)
    g2 = plot(lambda x: np.cos(x) - 2 * np.sin(x), 0, 2 * np.pi, GO, GUX, GUY, C.dfn)
    m.play(FadeOut(ml), at=tq, dur=0.3)
    m.play(FadeIn(ml2), ReplacementTransform(g1, g2), at=tq + 1.5, dur=0.8)

    # ── on this plane, D is a rotation ──
    tr = T.rotation
    Dm = Mat(D_TRIG.astype(int), size=52, h_buff=0.9, v_buff=0.72)
    dl = tex(r"D", r"=", size=52, colors={0: C.op})
    dg = VGroup(dl, Dm).arrange(RIGHT, buff=0.25).move_to([RX, 0.0, 0])
    m.play(FadeOut(VGroup(e1, e2)), at=tr - 0.5, dur=0.4)
    m.play(FadeIn(dg), at=tr, dur=0.7)

    # ── twice: every arrow points backwards ──
    m.play(FadeOut(VGroup(ml2, gax, g2)), at=T.old_facts - 0.2, dur=0.5)
    m.play(dg.animate.move_to([RX, 1.6, 0]), at=T.old_facts + 0.3, dur=0.8, ease=E)
    m.play(FadeIn(rl[3]), at=later[0][1] - 0.1, dur=0.5)
    d2 = tex(r"D^2", r"=", r"-I", size=48, colors={0: C.op}).move_to([RX - 0.2, -0.3, 0])
    m.play(FadeIn(d2, shift=0.1 * UP), at=T.minus_sine + 0.2, dur=0.6)
    m.play(Indicate(rl[2], color=C.b2, scale_factor=1.25), at=T.minus_sine + 1.3, dur=0.8)

    # ── four: a full turn home; sin, cos, −sin, −cos ──
    d4 = tex(r"D^4", r"=", r"I", size=48, colors={0: C.op}).next_to(d2, DOWN, buff=0.5, aligned_edge=LEFT)
    m.play(FadeIn(d4, shift=0.1 * UP), at=later[-1][1] + 0.1, dur=0.6)
    for k in range(4):
        m.play(Indicate(rl[k], color=getattr(C, RING[k][2]), scale_factor=1.3), at=T.cycle + 0.78 * k, dur=0.7)

    # ── the same quarter turn as i² = −1 ──
    ii = tex(r"i^2", r"=", r"-1", size=48).next_to(d4, DOWN, buff=0.5, aligned_edge=LEFT)
    m.play(FadeIn(ii, shift=0.1 * UP), Indicate(d2, color=C.op, scale_factor=1.1), at=T.i_squared + 0.4, dur=0.8)
    m.play(FadeOut(VGroup(dg, d2, d4, ii)), at=T.cut_inverse - 0.6, dur=0.5)
    finish(s)
