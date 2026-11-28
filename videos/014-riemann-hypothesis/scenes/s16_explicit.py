"""s16 explicit (P31-P33): chapter 4 opens on the s02 frame, and the explicit formula names its parts. One wave is
isolated: Re x^rho = sqrt(x) cos(gamma ln x) for the first zero, inside the dashed envelope +-sqrt(x). A gamma slider
raises the zero and the wave wiggles faster. Then the strip appears around the line of zeros, and the line Re s = 1
carries the one fact the prime number theorem needed: no zeros there."""
from aion import *

from beats import T
from look import (EASE, GAM, STRIP, ZX, X, carded, chapter_card, lab, pin, seen, staircase_frame, strip_mobs, tex,
                  zero_line_lit, zy)

A_WAVE, Y_WAVE = 0.2, -0.3                 # the isolated wave: Manim units per unit of Re x^rho, and its axis
G1 = float(GAM[0])                         # 14.1347...
G_TOP = 30.0                               # the slider raises the zero this far


def wave_points(gamma, n=1600):
    """Re x^rho = sqrt(x) cos(gamma ln x) for rho = 1/2 + i gamma, on x in [1, 100], as panel points."""
    x = np.linspace(1.0, 100.0, n)
    y = np.sqrt(x) * np.cos(gamma * np.log(x))
    return np.column_stack([X(x), Y_WAVE + A_WAVE * y, np.zeros(n)])


def wave_mob(gamma, color=None, width=2.8):
    v = VMobject(color=color or C.zero, stroke_width=width)
    v.set_points_as_corners(wave_points(gamma))
    return v


def envelope(sign):
    x = np.linspace(1.0, 100.0, 400)
    v = VMobject(color=C.bound, stroke_width=2.0)
    v.set_points_as_corners(np.column_stack([X(x), Y_WAVE + sign * A_WAVE * np.sqrt(x), np.zeros_like(x)]))
    return DashedVMobject(v, num_dashes=60, dashed_ratio=0.55)


@scene(T.cut_explicit, T.cut_offline)
def s16_explicit(s):
    s.solid(C.bg, z=-200)
    up = (T.opening - C.lead, T.opening + 0.85)                       # the s02 frame fades back up
    dim = (T.height - C.lead, T.height + 0.45)                        # everything but one wave dims to 15%
    back = (T.together - C.lead, T.together + 0.65)
    low = seen(0.25)
    plot_op = keys((up[0], 0.0), (up[1], 1.0), (dim[0], 1.0), (dim[1], low), (back[0], low), (back[1], 1.0), lead=0)
    wp = s.manim(z=2, opacity=plot_op)                                # the staircase plot
    wz = s.manim(z=3, opacity=keys((up[0], 0.0), (up[1], 1.0), lead=0))   # the line of zeros and the strip
    wv = s.manim(z=4)                                                 # the isolated wave
    h = s.manim(z=6, parallax=0.0)                                    # formulas and tags
    card = s.manim(z=8, parallax=0.0)

    # ── chapter card: pi(x) beside the pink dots ──
    mini = VGroup(Line([0, -0.62, 0], [0, 0.66, 0], color=C.crit, stroke_width=2.4),
                  *[Dot([0, (g - 27.0) * 0.048, 0], radius=0.05, color=C.zero) for g in GAM[:8]])
    chapter_card(card, T.cut_explicit, r"\pi(x)", "How the zeros build the primes", out=T.opening - 0.1,
                 color=C.prime, extra=mini)

    # ── the s02 frame, now with names ──
    frame = staircase_frame()
    wp.add(frame)
    zl = zero_line_lit()
    zeros_tag = lab("zeros", 30, C.zero)
    zeros_tag.move_to([ZX + 0.16 + zeros_tag.width / 2, float(zy(G1)) - 0.02, 0])
    wz.add(zl, zeros_tag)

    formula = tex(r"\pi(x)", r"=", r"R(x)", r"-", r"\sum\nolimits_\rho R(x^\rho)", size=46,
                  colors={0: C.prime, 2: C.smooth, 4: C.zero})
    small = lab("+ small terms", 30, C.muted)
    top = VGroup(formula, small).arrange(RIGHT, buff=0.25)
    pin(top, top=3.55, left=-5.9)
    h.play(Write(formula), at=T.exact, dur=2.0)
    h.play(FadeIn(small), at=T.exact + 1.6, dur=0.6, lead=0)
    h.play(Indicate(formula[2], color=C.smooth, scale_factor=1.15), at=T.smooth_part + 0.3, dur=0.9)
    wp.play(frame.ghost.animate.set_stroke(opacity=1.0), at=T.smooth_part + 0.3, dur=0.5)
    wp.play(frame.ghost.animate.set_stroke(opacity=0.12), at=T.one_wave, dur=0.6)
    h.play(Indicate(formula[4], color=C.zero, scale_factor=1.1), at=T.one_wave + 0.2, dur=0.9)
    rho = tex(r"\rho=\tfrac12+i\gamma", size=34, color=C.zero)
    rho.move_to([ZX - 0.16 - rho.width / 2, -2.55, 0])
    wz.play(FadeIn(rho, shift=0.1 * RIGHT), at=T.one_wave + 0.2, dur=0.6)

    # ── one zero, one wave: x^rho = x^(1/2) e^(i gamma ln x) ──
    eq = tex(r"x^\rho", r"=", r"x^{1/2}", r"\,e^{i\gamma\ln x}", size=44, colors={0: C.zero, 2: C.bound, 3: C.zero})
    pin(eq, top=2.6, left=-5.9)
    growth = lab("growth", 28, C.bound).next_to(eq[2], DOWN, buff=0.2)
    wiggle = lab("wiggle", 28, C.zero).next_to(eq[3], DOWN, buff=0.2)
    h.play(Write(eq), at=T.height + 0.3, dur=1.0)
    wz.play(FadeOut(rho), at=T.height, dur=0.4)
    re_x = tex(r"\mathrm{Re}\,x^\rho", size=34, color=C.zero)
    pin(re_x, top=0.95, left=-5.9)

    gam = keys((T.wiggles - 1.3, G1), (T.wiggles + 0.2, G_TOP, EASE), (T.real_part + 0.1, G_TOP),
               (T.real_part + 1.3, G1, EASE), lead=0)
    slide = (T.wiggles - 1.3, T.real_part + 1.3)
    axis = Line([X(0), Y_WAVE, 0], [X(100) + 0.1, Y_WAVE, 0], color=C.muted, stroke_width=1.6)
    first = wave_mob(G1)
    wv.play(Create(axis), at=T.height, dur=0.6)
    wv.play(Create(first), at=T.height + 0.25, dur=1.2, ease="smooth", lead=0)
    wv.play(FadeIn(re_x), at=T.height + 1.0, dur=0.5, lead=0)
    wv.remove(first, at=slide[0])
    live_wave = wv.redraw(lambda t: wave_mob(float(gam(t))), during=slide)

    def ring(t):
        g = float(gam(t))
        y = float(zy(g))
        r = Circle(radius=0.085, color=C.text, stroke_width=2.2).move_to([ZX, y, 0])
        head = tex(r"\gamma=", size=30)
        val = DecimalNumber(g, num_decimal_places=2, font_size=30, color=C.text)
        val.next_to(head, RIGHT, buff=0.1).set_y(head[0][1].get_y())
        lab_ = VGroup(head, val)
        lab_.move_to([ZX - 0.2 - lab_.width / 2, y, 0])
        return VGroup(r, carded(lab_, buff=0.06))

    ring0 = ring(slide[0])
    wz.play(FadeIn(ring0), at=T.height + 0.25, dur=0.5)
    wz.remove(ring0, at=slide[0])
    live_ring = wz.redraw(ring, during=slide)
    h.play(FadeIn(wiggle, shift=0.08 * UP), at=T.wiggles - 0.9, dur=0.5)
    h.play(FadeIn(growth, shift=0.08 * UP), at=T.grows, dur=0.5)
    h.play(Indicate(eq[2], color=C.bound, scale_factor=1.2), at=T.one_half + 0.3, dur=0.9)
    env = VGroup(envelope(1), envelope(-1))
    root = tex(r"\pm\sqrt{x}", size=34, color=C.bound)
    root.move_to([X(100) + 0.2 + root.width / 2, Y_WAVE + A_WAVE * 10.0 - 0.05, 0])
    wv.play(Create(env[0]), Create(env[1]), at=T.sqrt_x, dur=1.0)
    wv.play(FadeIn(root), at=T.sqrt_x + 0.6, dur=0.5, lead=0)

    # ── the prime number theorem needed one fact: no zero on Re s = 1 ──
    wv.play(*[FadeOut(mob) for mob in (axis, env, root, live_wave, re_x)], at=T.pnt_needed, dur=0.6)
    h.play(FadeOut(VGroup(eq, growth, wiggle)), at=T.pnt_needed, dur=0.6)
    wz.play(FadeOut(live_ring), at=T.pnt_needed, dur=0.5)

    st = strip_mobs()
    fill, re0, re1, n0, n1 = st.fill, st.re0, st.re1, st.n0, st.n1
    wz.play(FadeOut(zeros_tag), FadeIn(fill), Create(re0), at=T.pnt_needed + 0.4, dur=0.8)
    wz.play(Create(re1), FadeIn(n0), FadeIn(n1), at=T.pnt_needed + 0.9, dur=0.8)
    fact = tex(r"\zeta(1+it)\neq0", size=40)
    nz = lab("no zeros on Re $s=1$", 30, C.text)
    tag = VGroup(fact, nz).arrange(DOWN, buff=0.18, aligned_edge=RIGHT)
    tag.move_to([STRIP[0] - 0.3 - tag.width / 2, 0.55, 0])
    h.play(FadeIn(tag, shift=0.1 * RIGHT), at=T.no_re1, dur=0.6)
    wz.play(re1.animate.set_stroke(width=4.5), at=T.no_re1 + 0.2, dur=0.5)
    wz.play(re1.animate.set_stroke(width=2.2), at=T.no_re1 + 1.0, dur=0.6, lead=0)

    # ── together the waves grow more slowly than the count; the hypothesis asks for much more ──
    h.play(tag.animate.set_opacity(0.45), at=T.much_more, dur=0.6)
    wz.play(zl.line.animate.set_stroke(width=4.0, opacity=1.0), at=T.much_more + 0.4, dur=0.7)
