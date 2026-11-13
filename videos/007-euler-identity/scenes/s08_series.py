"""Ch5 · The infinite sum. e^x = 1 + x + x²/2 + x³/6 + ⋯ = Σ xⁿ/n!. Plug in iπ and lay each term as an arrow, tip
to tail: 1 right, π up, π²/2 ≈ 4.93 left, π³/6 down, then right, up… each a quarter turn more (small red turn
marks; teal for horizontal steps, purple for vertical). The steps grow, then a bar chart of πⁿ/n! shows the
factorials win, and the path spirals in; a magnifier (8×) shows it closing on −1. Finally the teal steps slide onto
the real axis and sum to −1 = cos π, the purple ones onto the imaginary axis and cancel to 0 = sin π. Badge Σ."""
import math

from aion import *

from beats import T
from shots import (arrow, backdrop, backing, badge, badges, ease, live, panel, plane_grid, rail, ramp, tex)

E = "easy_ease"
O = (1.0, -1.05)                                      # world point of 0 (unit 1)
NT = 18
TERMS = np.array([(1j * PI) ** k / math.factorial(k) for k in range(NT)])
S = np.concatenate([[0], np.cumsum(TERMS)])           # S[k] = sum of the first k terms
VIEW = dict(center=(-0.5, -0.3), zoom=0.92)
MAG_C, MAG_S, MAG_K = np.array([4.75, -0.75, 0]), 3.0, 8.0     # the magnifier: centre, side (HUD), zoom


def W(z):
    z = complex(z)
    return np.array([O[0] + z.real, O[1] + z.imag, 0.0])


def col(k):
    return C.cos if k % 2 == 0 else C.sin


def to_screen(p):
    c, z = VIEW["center"], VIEW["zoom"]
    return np.array([(p[0] - c[0]) * z, (p[1] - c[1]) * z, 0.0])


def clip_seg(a, b, h):
    """Clip segment a→b (2D) to the square |x|,|y| ≤ h. Returns (a', b') or None (Liang–Barsky)."""
    d = b - a
    lo, hi = 0.0, 1.0
    for p, q in ((-d[0], a[0] + h), (d[0], h - a[0]), (-d[1], a[1] + h), (d[1], h - a[1])):
        if abs(p) < 1e-12:
            if q < 0:
                return None
            continue
        r = q / p
        if p < 0:
            lo = max(lo, r)
        else:
            hi = min(hi, r)
    if lo > hi:
        return None
    return a + lo * d, a + hi * d


@scene(T.cut_ch5, T.cut_ch6)
def s08_series(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)
    m = s.manim(z=2)
    hb = s.manim(z=3, parallax=0.0)                   # HUD backings, under the HUD text
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 5)
    badges(hud, 4)
    slot = DashedVMobject(RoundedRectangle(width=1.0, height=0.46, corner_radius=0.06, color=C.muted,
                                           stroke_width=C.thin + 0.6), num_dashes=22)
    slot.move_to(badge(5)).align_to(badge(5), LEFT).shift(0.08 * LEFT)
    hud.add(slot, at=t0)

    # ── "There is a second way to compute e to the x. An infinite sum. One, plus x, plus x squared over two…" ──
    X = tex("e^{x}", "=", "1", "+", "x", "+", r"\tfrac{x^{2}}{2}", "+", r"\tfrac{x^{3}}{6}", "+", r"\cdots",
            size=60).move_to([-0.9, 0.6, 0])
    X[0][0].set_color(C.growth)
    hud.play(FadeIn(X[0:2], shift=0.1 * UP), at=T.second_way + 0.4, dur=0.6)
    for j, b in ((2, T.inf_sum + 1.2), (4, T.plus_x), (6, T.x2), (8, T.x3), (10, T.so_on)):
        hud.play(FadeIn(X[j - 1:j + 1] if j > 2 else X[j], shift=0.1 * UP), at=b, dur=0.5)
    gen = VGroup(tex("=", size=60), tex(r"\sum", r"\tfrac{x^{n}}{n!}", size=60)).arrange(RIGHT, buff=0.25)
    gen.next_to(X, RIGHT, buff=0.25)
    hud.play(FadeIn(gen, shift=0.1 * LEFT), at=T.nfact - 0.6, dur=0.7)
    hud.play(Indicate(gen[1][1], color=None, scale_factor=1.2), at=T.nfact + 0.4, dur=0.7)

    # ── "Plug in i pi": x → iπ, and the formula rises to the top ──
    Y = tex(r"e^{i\pi}", "=", "1", "+", r"i\pi", "+", r"\tfrac{(i\pi)^{2}}{2}", "+", r"\tfrac{(i\pi)^{3}}{6}", "+",
            r"\cdots", size=50).move_to([0, 3.3, 0])
    Y[0][0].set_color(C.growth)
    for part, idx in ((0, (1, 2)), (4, (0, 1)), (6, (1, 2)), (8, (1, 2))):
        Y[part][idx[0]].set_color(C.turn)
        Y[part][idx[1]].set_color(C.arc)
    yback = backing(Y, pad=0.16)
    hud.play(FadeOut(gen), at=T.plug - 0.2, dur=0.4)
    hud.play(*[ReplacementTransform(X[j], Y[j]) for j in range(11)], at=T.plug, dur=1.2, ease=E)
    hb.play(FadeIn(yback), at=T.plug + 0.9, dur=0.4)
    bars = VGroup(*[Line(Y[j].get_corner(DL) + [0, -0.1, 0], Y[j].get_corner(DR) + [0, -0.1, 0], color=col(k),
                         stroke_width=4) for k, j in enumerate((2, 4, 6, 8))])

    # the plane
    s.camera.frame(t0, center=(0.6, -0.4), zoom=1.0, dur=0.05)
    kp = (T.arrows - 0.4, T.arrows + 0.6)

    def stage(t):
        k = ramp(t, *kp) * (1 - 0.5 * ramp(t, T.horizontal - 0.4, T.horizontal + 0.4))
        return plane_grid(O, 1.0, box=(-9, -5.5, 9, 5.5), n=14, minor=2, opacity=0.32 * k)
    live(bg, stage, kp, (T.horizontal - 0.4, T.horizontal + 0.4))

    # ── the arrows, tip to tail ──
    sched = [(T.step_right - 0.3, 0.8), (T.up_pi - 0.2, 0.9), (T.left - 0.1, 1.0), (T.down - 0.15, 0.6),
             (T.right - 0.1, 0.5), (T.up - 0.1, 0.5), (T.each + 0.2, 0.5), (T.each + 1.0, 0.45)]
    sched += [(T.shrink2 + 0.1 + 0.25 * j, 0.3) for j in range(NT - len(sched))]
    for k in range(4):
        hud.play(Create(bars[k]), at=sched[k][0] + 0.2, dur=0.5)
    slide_h = (T.horizontal + 0.2, T.horizontal + 1.8)
    slide_v = (T.vertical + 0.1, T.vertical + 1.7)

    def ladder(k):                                    # where step k lands when the axes collect it
        if k % 2 == 0:
            h0 = sum(TERMS[j].real for j in range(0, k, 2))
            y = -0.22 * (1 + k // 2)
            return W(h0 + 1j * y), W(h0 + TERMS[k].real + 1j * y)
        v0 = sum(TERMS[j].imag for j in range(1, k, 2))
        x = 0.22 * (1 + k // 2)
        return W(x + 1j * v0), W(x + 1j * (v0 + TERMS[k].imag))

    def steps(t):
        g = VGroup()
        ks = ramp(t, *kp)
        # the ghost of the whole spiral once the steps leave it
        kgh = ramp(t, slide_h[0], slide_h[0] + 0.5)
        if kgh > 0.01:
            g.add(VMobject(stroke_color=C.ghost, stroke_width=C.thin, stroke_opacity=kgh)
                  .set_points_as_corners([W(z) for z in S[:NT + 1]]))
        for k, (a, d) in enumerate(sched):
            p = ease(t, a, a + d)
            if p <= 0:
                break
            a0, a1 = W(S[k]), W(S[k] + p * TERMS[k])
            u = ease(t, *(slide_h if k % 2 == 0 else slide_v))
            if u > 0:
                b0, b1 = ladder(k)
                a0, a1 = (1 - u) * a0 + u * b0, (1 - u) * a1 + u * b1
            g.add(arrow(a0, a1, col(k), width=C.stroke if k < 8 else C.stroke - 1,
                        tip=0.24 if k < 6 else 0.16).set_opacity(ks))
        kh = ramp(t, slide_h[1] - 0.3, slide_h[1] + 0.2) * (1 - ramp(t, T.cut_ch6 - 0.9, T.cut_ch6 - 0.3))
        if kh > 0.01:                                 # where each family ends: −1 and 0
            g.add(Dot(W(-1), radius=0.08, color=C.point).set_opacity(kh))
            g.add(MathTex("-1", font_size=40, color=C.point).move_to(W(-1) + [-0.15, 0.4, 0]).set_opacity(kh))
        kz = ramp(t, slide_v[1] - 0.3, slide_v[1] + 0.2) * (1 - ramp(t, T.cut_ch6 - 0.9, T.cut_ch6 - 0.3))
        if kz > 0.01:
            g.add(Dot(W(0), radius=0.08, color=C.sin).set_opacity(kz))
            g.add(MathTex("0", font_size=40, color=C.sin).move_to(W(0) + [-0.35, 0.35, 0]).set_opacity(kz))
        return g
    live(m, steps, kp, (sched[0][0], sched[7][0] + sched[7][1]), (sched[8][0], sched[-1][0] + sched[-1][1]),
         slide_h, slide_v, (slide_h[1] - 0.3, slide_h[1] + 0.2), (slide_v[1] - 0.3, slide_v[1] + 0.2),
         (T.cut_ch6 - 0.9, T.cut_ch6 - 0.3))

    # turn marks: each step turns a quarter more than the last
    tk = (T.shrink2 - 0.6, T.shrink2)
    for k in range(1, 6):
        mk = Arc(radius=0.24, start_angle=(k - 1) * PI / 2, angle=PI / 2, arc_center=W(S[k]), color=C.turn,
                 stroke_width=C.thin + 1)
        mk.add_tip(tip_length=0.1, tip_width=0.1)
        m.play(Create(mk), at=sched[k][0] + 0.05, dur=0.4)
        m.play(FadeOut(mk), at=tk[0], dur=0.5)

    # sizes of the first steps
    labs = [MathTex("1", font_size=34, color=C.cos).move_to(W(0.5) + [0, -0.3, 0]),
            MathTex(r"\pi", font_size=40, color=C.sin).move_to(W(1 + 1.57j) + [0.35, 0, 0]),
            MathTex(r"\tfrac{\pi^{2}}{2}\approx4.93", font_size=36, color=C.cos).move_to(W(-1.47 + 3.14j) +
                                                                                          [0, 0.42, 0]),
            MathTex(r"\tfrac{\pi^{3}}{6}", font_size=36, color=C.sin).move_to(W(-3.93 + 0.55j) + [-0.5, 0, 0])]
    labs[2][0][:5].set_color(C.cos)
    for k, lab in enumerate(labs):
        if k == 2:
            m.play(FadeIn(lab[0][:5]), at=T.pi2 + 0.1, dur=0.5)
            m.play(FadeIn(lab[0][5:]), at=T.v49, dur=0.5)
        else:
            m.play(FadeIn(lab), at=sched[k][0] + sched[k][1] - 0.2, dur=0.5)
    m.play(FadeOut(VGroup(*labs)), at=T.grow + 0.8, dur=0.6)

    # ── "At first, the steps grow, and the path swings far away." the camera pulls back ──
    s.camera.frame(T.pi2 - 0.3, dur=2.2, **VIEW)

    # ── "But the factorials grow faster than any power of pi." a bar chart of the step sizes ──
    bc = np.array([-5.1, 0.15, 0])
    bw, bh = 3.1, 2.9
    fac = (T.factorials - 0.3, T.factorials + 2.6)
    fac_out = (T.one_point, T.one_point + 0.6)

    def chart(t):
        k = ramp(t, fac[0], fac[0] + 0.5) * (1 - ramp(t, *fac_out))
        if k < 0.005:
            return VGroup()
        g = VGroup(backing(Rectangle(width=bw, height=bh), pad=0).move_to(bc).set_opacity(k)
                   .set_stroke(opacity=0.8 * k))
        x0, y0 = bc[0] - bw / 2 + 0.3, bc[1] - bh / 2 + 0.35
        g.add(Line([x0, y0, 0], [x0 + bw - 0.5, y0, 0], color=C.axis, stroke_width=C.thin, stroke_opacity=k))
        g.add(MathTex(r"\tfrac{\pi^{n}}{n!}", font_size=34, color=C.text).move_to([x0 + 0.55, y0 + bh - 0.75, 0])
              .set_opacity(k))
        g.add(MathTex("n", font_size=28, color=C.muted).move_to([x0 + bw - 0.35, y0 - 0.2, 0]).set_opacity(k))
        for n in range(13):
            hn = abs(TERMS[n]) * 0.36 * ease(t, fac[0] + 0.18 * n, fac[0] + 0.18 * n + 0.4)
            if hn > 0.002:
                g.add(Rectangle(width=0.14, height=hn, stroke_width=0, fill_color=col(n), fill_opacity=0.9 * k)
                      .move_to([x0 + 0.2 + 0.2 * n, y0 + hn / 2, 0]))
        return g
    live(hud, chart, fac, fac_out)

    # ── "…closer and closer to one point." a magnifier on −1 ──
    mag = (T.one_point - 0.4, T.one_point + 0.8)
    mag_out = (T.horizontal - 0.5, T.horizontal)
    h = MAG_S / 2 / MAG_K                              # half side of the world square

    def magnifier(t):
        k = ramp(t, *mag) * (1 - ramp(t, *mag_out))
        if k < 0.005:
            return VGroup()
        sc = to_screen(W(-1))
        r = h * VIEW["zoom"]
        g = VGroup(Square(2 * r, color=C.point, stroke_width=C.thin + 0.6).move_to(sc).set_stroke(opacity=k))
        for cx, cy in ((-1, 1), (-1, -1)):
            g.add(Line(sc + [r, cy * r, 0], MAG_C + [-MAG_S / 2, cy * MAG_S / 2, 0], color=C.point,
                       stroke_width=C.thin, stroke_opacity=0.5 * k))
        g.add(backing(Square(MAG_S), pad=0).move_to(MAG_C).set_stroke(C.point, opacity=k).set_opacity(k)
              .set_stroke(opacity=k))
        hh = MAG_S / 2

        def inset(z):
            d = (complex(z) - (-1)) * MAG_K
            return np.array([d.real, d.imag])
        # axes through −1 inside the inset
        g.add(Line(MAG_C + [-hh, 0, 0], MAG_C + [hh, 0, 0], color=C.axis, stroke_width=C.thin, stroke_opacity=0.6 * k))
        for kk in range(6, NT):
            p = ease(t, sched[kk][0], sched[kk][0] + sched[kk][1])
            if p <= 0:
                break
            seg = clip_seg(inset(S[kk]), inset(S[kk] + p * TERMS[kk]), hh - 0.02)
            if seg is None:
                continue
            a_, b_ = MAG_C + [*seg[0], 0], MAG_C + [*seg[1], 0]
            if np.linalg.norm(b_ - a_) > 0.01:
                g.add(arrow(a_, b_, col(kk), width=C.stroke, tip=0.18).set_opacity(k))
        g.add(Dot(MAG_C, radius=0.06, color=C.point).set_opacity(k))
        g.add(MathTex("-1", font_size=34, color=C.point).move_to(MAG_C + [0.0, -0.45, 0]).set_opacity(k))
        g.add(MathTex(r"\times 8", font_size=28, color=C.muted).move_to(MAG_C + [hh - 0.4, hh - 0.3, 0])
              .set_opacity(k))
        return g
    live(hud, magnifier, mag, (mag[1], sched[-1][0] + sched[-1][1]), mag_out)

    # ── "Negative one, again." ──
    ring = Circle(radius=0.13, color=C.point, stroke_width=C.thin + 1.5).move_to(W(-1))
    m1 = MathTex("-1", font_size=40, color=C.point).move_to(W(-1) + [-0.2, -0.45, 0])
    m.play(FadeIn(m1, scale=1.3), at=T.again - 0.3, dur=0.5)
    m.play(FadeIn(ring, scale=0.5), at=T.again - 0.3, dur=0.2)
    m.play(FadeOut(ring, scale=3.0), at=T.again, dur=0.8)
    hud.play(Indicate(Y[0], color=None, scale_factor=1.25), at=T.again, dur=0.8)

    # ── "the horizontal steps … cosine of pi. The vertical steps … sine of pi. Which is zero." ──
    cs = tex(r"\cos\pi", "=", "-1", size=52, colors={0: C.cos, 2: C.point}).move_to([-4.9, 1.6, 0])
    sn = tex(r"\sin\pi", "=", "0", size=52, colors={0: C.sin}).next_to(cs, DOWN, buff=0.35, aligned_edge=LEFT)
    cback = backing(VGroup(cs, sn), pad=0.2)
    hb.play(FadeIn(cback), at=T.cos_pi - 0.2, dur=0.6)
    hud.play(FadeIn(cs[0], shift=0.1 * UP), at=T.cos_pi - 0.2, dur=0.6)
    hud.play(FadeIn(cs[1:], shift=0.1 * UP), at=T.cos_pi + 0.6, dur=0.5)
    hud.play(FadeIn(sn[0], shift=0.1 * UP), at=T.sin_pi - 0.2, dur=0.5)
    hud.play(FadeIn(sn[1:], shift=0.1 * UP), at=T.zero, dur=0.5)

    # badge Σ into the second check slot
    hud.play(ReplacementTransform(VGroup(Y, bars), badge(5)), FadeOut(slot), at=T.cut_ch6 - 1.3,
             dur=0.9, ease=E)
    hud.play(FadeOut(VGroup(cs, sn)), at=T.cut_ch6 - 0.9, dur=0.6)
    hb.play(FadeOut(VGroup(cback, yback)), at=T.cut_ch6 - 1.2, dur=0.6)
    m.play(FadeOut(m1), at=T.horizontal, dur=0.5)
