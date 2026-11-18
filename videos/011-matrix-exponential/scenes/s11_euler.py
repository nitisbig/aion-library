"""s11 euler (ch3): Bernoulli's trick for matrices. A short step of length t/n moves v by its velocity times the step:
v → (I + (t/n) A) v; n of them apply (I + (t/n) A)^n. For the half turn (A = J, t = π) four steps make a lopsided
square that spirals out to radius 2.61 (a straight step lands outside the curve); eight reach 1.77, thirty-two 1.17,
and in the limit the polygon lands on the circle: (I + tA/n)^n → e^{tA}. Radii from verify.euler."""
from aion import *

from beats import T
from shots import E, J, arrow, backdrop, backed, chapter_card, finish, lab, live, p3, poly, tex
from verify import euler

O, U = np.array([-1.5, -1.85]), 1.35                   # the plane's centre and unit
NS = [4, 8, 32, 1000]
RAD = {n: float(np.linalg.norm(euler(np.pi * J, n)[:, 0])) for n in NS}
assert abs(RAD[4] - 2.614) < 2e-3 and abs(RAD[8] - 1.775) < 2e-3 and abs(RAD[32] - 1.167) < 2e-3


def W(v):
    return O + U * np.asarray(v, float)


def path(n):
    S = np.eye(2) + np.pi * J / n
    pts, v = [np.array([1.0, 0.0])], np.array([1.0, 0.0])
    for _ in range(n):
        v = S @ v
        pts.append(v)
    return [W(p) for p in pts]


# inset: end radius against log2 n
IX0, IY0, IW, IH = 3.2, -1.5, 3.3, 2.4


def inset_pt(n, r):
    return np.array([IX0 + IW * (np.log2(n) - 2) / 8.5, IY0 + IH * (r - 1) / 1.7])


@scene(T.cut_ch3, T.cut_binom)
def s11_euler(s):
    backdrop(s)
    m = s.manim(z=2)
    chapter_card(m, 3, "Building the series out of tiny steps", r"\sum \tfrac{A^k}{k!}", T.cut_ch3)

    # ── the exact flow: half a circle from (1, 0) to (−1, 0) ──
    t0 = T.cut_ch3 + 2.9
    axes = VGroup(Line(p3(W((-3.0, 0))), p3(W((3.0, 0))), color=C.muted, stroke_width=C.thin),
                  Line(p3(W((0, -0.3))), p3(W((0, 2.4))), color=C.muted, stroke_width=C.thin))
    circ = Arc(radius=U, start_angle=0, angle=PI, arc_center=p3(O), color=C.flow, stroke_width=C.stroke)
    v0 = Dot(p3(W((1, 0))), radius=0.09, color=C.vec)
    goal = Circle(radius=0.13, color=C.flow, stroke_width=C.thin + 0.6).move_to(p3(W((-1, 0))))
    m.play(Create(axes), at=t0, dur=0.7)
    m.play(Create(circ), FadeIn(v0), at=t0 + 0.6, dur=1.4, ease=E)
    m.play(FadeIn(goal), at=t0 + 1.8, dur=0.4)
    vlab = backed(tex(r"\mathbf v", size=38, color=C.vec), buff=0.04).next_to(v0, DR, buff=0.05)
    m.play(FadeIn(vlab), at=t0 + 1.8, dur=0.4)

    # ── one short step: v moves by its velocity times t/n ──
    rule = tex(r"\mathbf v", r"\;\to\;", r"\mathbf v", "+", r"\tfrac{t}{n}", r"A\mathbf v", size=50,
               colors={0: C.vec, 2: C.vec, 4: C.flow, 5: C.gen}).move_to([-1.2, 3.2, 0])
    m.play(FadeIn(rule, shift=0.1 * DOWN), at=T.short_step + 0.6, dur=0.7)
    stp = arrow(W((1, 0)), W((1, np.pi / 4)), C.gen, width=C.stroke + 1)
    stp_l = backed(tex(r"\tfrac{t}{n}A\mathbf v", size=34, color=C.gen), buff=0.04).next_to(stp, RIGHT, buff=0.1)
    m.play(GrowArrow(stp), FadeIn(stp_l), at=T.short_step + 2.4, dur=0.7)
    rule2 = tex(r"\mathbf v", r"\;\to\;", r"\left(I+\tfrac{t}{n}A\right)", r"\mathbf v", size=50,
                colors={0: C.vec, 2: C.money, 3: C.vec}).move_to(rule)
    m.play(TransformMatchingTex(rule, rule2), at=T.new_point + 0.6, dur=0.9)
    rule3 = tex(r"\mathbf v", r"\;\to\;", r"\left(I+\tfrac{t}{n}A\right)^{n}", r"\mathbf v", size=50,
                colors={0: C.vec, 2: C.money, 3: C.vec}).move_to(rule)
    m.play(TransformMatchingTex(rule2, rule3), at=T.nth_power + 0.2, dur=0.8)
    m.play(FadeOut(VGroup(stp, stp_l, vlab)), at=T.nth_power, dur=0.4)

    # ── polygons: 4, 8, 32, 1000 steps ──
    ats = {4: T.four + 0.3, 8: T.eight + 0.1, 32: T.thirty_two + 0.2, 1000: T.limit3 + 0.2}
    durs = {4: 2.4, 8: 1.4, 32: 1.2, 1000: 1.0}
    gh_at = {4: T.eight - 0.2, 8: T.thirty_two, 32: T.limit3}
    nlab = None
    drawn = VGroup()
    ins_dots = VGroup()
    for n in NS:
        pts = path(n)
        pl = poly(pts, C.vec if n < 1000 else C.flow, C.stroke if n < 32 else C.stroke - 0.5)
        end = Dot(p3(pts[-1]), radius=0.08, color=C.vec)
        m.play(Create(pl, rate_func=linear), at=ats[n], dur=durs[n])
        m.add(end, at=ats[n] + durs[n] - 0.1)
        drawn.add(pl)
        if n == 1000:
            drawn.add(end)
        lbl = VGroup(tex("n", "=", size=40, colors={0: C.money}), Integer(n, font_size=40, color=C.money)).arrange(
            RIGHT, buff=0.12)
        rl = VGroup(lab("end radius", 24, C.muted), DecimalNumber(RAD[n], num_decimal_places=2, font_size=38,
                                                                  color=C.vec)).arrange(RIGHT, buff=0.2)
        blk = VGroup(lbl, rl).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([4.6, 2.75, 0])
        if nlab is None:
            m.play(FadeIn(blk), at=ats[n], dur=0.4)
        else:
            m.play(FadeOut(nlab), FadeIn(blk), at=ats[n], dur=0.4)
        nlab = blk
        d = Dot(p3(inset_pt(n, RAD[n])), radius=0.07, color=C.vec)
        ins_dots.add(d)
        m.play(FadeIn(d, scale=0.5), at=ats[n] + durs[n], dur=0.3)
        if n in gh_at:
            m.play(pl.animate.set_stroke(color=C.wrong, opacity=0.45, width=C.thin + 0.4), FadeOut(end),
                   at=gh_at[n], dur=0.5)

    # the inset: end radius against n (log axis), the circle's radius as a dashed line
    ia = VGroup(Line(p3((IX0, IY0)), p3((IX0 + IW, IY0)), color=C.muted, stroke_width=C.thin),
                Line(p3((IX0, IY0)), p3((IX0, IY0 + IH)), color=C.muted, stroke_width=C.thin),
                DashedLine(p3(inset_pt(4, 1.0)), p3(inset_pt(1000, 1.0)), color=C.flow, stroke_width=C.thin + 0.4,
                           dash_length=0.08),
                lab("n", 24, C.money).move_to(p3((IX0 + IW + 0.25, IY0))),
                lab("radius", 24, C.muted).move_to(p3((IX0, IY0 + IH + 0.25))),
                *[lab(str(n), 20, C.muted).move_to(p3(inset_pt(n, 1.0) + [0, -0.55])) for n in NS],
                tex("1", size=26, color=C.flow).move_to(p3((IX0 - 0.22, IY0))))
    m.play(FadeIn(ia), at=T.four, dur=0.6)

    c_op = keys((T.cut_binom - 0.4, 0.7), (T.cut_binom - 0.05, 0.0), lead=0)

    def conn(t):
        k = sum(1 for n in NS if t >= ats[n] + durs[n] + 0.3)
        return poly([inset_pt(n, RAD[n]) for n in NS[:k]], C.vec, C.thin + 0.4, opacity=float(c_op(t))) if k > 1 \
            else VGroup()
    live(m, conn, (T.four, T.cut_binom))

    # zoom onto one step: the straight step lands outside the curve
    q = path(4)[1]
    s.camera.frame(at=T.outside, center=tuple(((W((1, 0)) + q) / 2)), zoom=2.2, dur=1.0)
    s.camera.frame(at=T.outside + 2.4, center=(0.0, 0.0), zoom=1.0, dur=1.0)

    # ── the limit ──
    lim = tex(r"\left(I+\tfrac{t}{n}A\right)^{n}", r"\;\longrightarrow\;", r"e^{tA}", size=50,
              colors={0: C.money, 2: C.flow}).move_to(rule3)
    m.play(FadeOut(rule3, shift=0.1 * UP), FadeIn(lim, shift=0.1 * UP), at=T.limit3 + 1.2, dur=0.7)
    m.play(FadeOut(VGroup(lim, nlab, axes, circ, v0, goal, ia, ins_dots, drawn)),
           at=T.cut_binom - 0.4, dur=0.5)
    finish(s)
