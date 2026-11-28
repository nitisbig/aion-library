"""s17 offline (P34-P35): what if one zero left the line? A ghost of the first zero is dragged to real part 0.8 (its
mirror twin comes with it at 0.2), and the change it would make, added to the real error pi(x) - li(x) up to 10^8
(assets/error.npz), swings far from the curve. It snaps back; the real error stays inside Schoenfeld's envelope
(if RH). Von Koch: the converse holds too. Mirrored pairs: the largest real part can't go below 1/2."""
from functools import lru_cache

from aion import *

from beats import T
from look import (ASSETS, EASE, GAM, ZX, caps, ghost_ring, lab, pin, re_x, smooth01, staircase_frame, strip_mobs,
                  tex, zero_line_lit, zy)

EX0, EX1 = -6.2, 3.2                       # Manim x of 0 and of 10^8
EY, EBOT, ETOP = -0.2, -3.15, 2.45         # the zero line (pi = li), the bottom axis, the top of the y-axis
SY0 = 2.9 / 20000                          # Manim units per unit of error while the hypothetical is on screen
SY1 = 2.8 / 7400                           # after it snaps back: the envelope fills the plot
Y_PAIR = 0.3                               # height of the mirrored pair in the strip (s17's last idea)


@lru_cache(maxsize=1)
def data():
    d = np.load(ASSETS / "error.npz")
    return {k: d[k] for k in d.files}


def ex(x):
    return EX0 + (EX1 - EX0) * np.asarray(x, float) / 1e8


def err_mob(y, sy, color, width=2.6, xmax=None):
    x = data()["x"]
    keep = x <= (1e8 if xmax is None else xmax)
    if keep.sum() < 2:
        return VGroup()
    v = VMobject(color=color, stroke_width=width)
    v.set_points_as_corners(np.column_stack([ex(x[keep]), EY + sy * np.asarray(y)[keep], np.zeros(keep.sum())]))
    return v


def envelope_mob(sign, sy):
    D = data()
    keep = D["x"] >= 2657
    v = VMobject(color=C.bound, stroke_width=2.2)
    v.set_points_as_corners(np.column_stack([ex(D["x"][keep]), EY + sign * sy * D["env"][keep], np.zeros(keep.sum())]))
    return DashedVMobject(v, num_dashes=56, dashed_ratio=0.55)


@scene(T.cut_offline, T.cut_littlewood)
def s17_offline(s):
    s.solid(C.bg, z=-200)
    old = s.manim(z=2, opacity=keys((T.suppose - C.lead, 1.0), (T.suppose + 0.45, 0.0), lead=0))   # s16's plot leaves
    bye = keys((T.cut_littlewood - 0.5, 1.0), (T.cut_littlewood - 0.05, 0.0), lead=0)   # chapter 5 opens on black
    wp = s.manim(z=3, opacity=bye)                      # the error plot
    wz = s.manim(z=4, opacity=bye)                      # the strip, the line of zeros, the ghost zeros
    h = s.manim(z=6, parallax=0.0, opacity=bye)         # formulas and tags
    D = data()

    # ── s16's last frame, then the error plot takes its place ──
    old.add(staircase_frame())
    f16 = tex(r"\pi(x)", r"=", r"R(x)", r"-", r"\sum\nolimits_\rho R(x^\rho)", size=46,
              colors={0: C.prime, 2: C.smooth, 4: C.zero})
    pin(VGroup(f16, lab("+ small terms", 30, C.muted)).arrange(RIGHT, buff=0.25), top=3.55, left=-5.9)
    old.add(f16)
    st = strip_mobs()
    zl = zero_line_lit(width=4.0, line_opacity=1.0)
    wz.add(st, zl)
    wz.play(zl.line.animate.set_stroke(width=2.0, opacity=0.75), at=T.suppose, dur=0.6)

    axis0 = Line([EX0, EY, 0], [EX1 + 0.12, EY, 0], color=C.muted, stroke_width=1.6)
    yax = Line([EX0, EBOT, 0], [EX0, ETOP, 0], color=C.axis, stroke_width=2.0)
    bottom = Line([EX0, EBOT, 0], [EX1, EBOT, 0], color=C.axis, stroke_width=2.0)
    ticks = VGroup(*[Line([ex(v), EBOT - 0.07, 0], [ex(v), EBOT + 0.07, 0], color=C.muted, stroke_width=1.6)
                     for v in (2.5e7, 5e7, 7.5e7, 1e8)])
    nums = VGroup(tex("0", size=28, color=C.muted).move_to([EX0, EBOT - 0.25, 0]),
                  tex(r"5\cdot10^7", size=28, color=C.muted).move_to([ex(5e7), EBOT - 0.27, 0]),
                  tex(r"10^8", size=28, color=C.muted).move_to([EX1, EBOT - 0.27, 0]))
    ylab = tex(r"\pi(x)-\mathrm{li}(x)", size=32, color=C.gap)
    pin(ylab, top=1.55, left=-5.9)
    frame = VGroup(yax, bottom, ticks, nums, axis0)
    wp.play(FadeIn(frame), at=T.suppose + 0.25, dur=0.7, lead=0)
    sy = key(T.gap_stays, SY0, SY1, dur=1.3, ease=EASE)
    rescale = (T.gap_stays - C.lead, T.gap_stays - C.lead + 1.3)
    real0 = err_mob(D["err"], SY0, C.gap)
    wp.play(Create(real0), FadeIn(ylab), at=T.suppose + 0.6, dur=1.0, lead=0)
    wp.remove(real0, at=rescale[0])
    wp.redraw(lambda t: err_mob(D["err"], float(sy(t)), C.gap), during=rescale)

    # ── a ghost of the first zero moves off the line to 0.8; its mirror twin comes with it ──
    y1 = float(zy(GAM[0]))
    pos = key(T.eight, 0.5, 0.8, dur=2.0, ease=EASE)          # lands on "point eight"
    back = key(T.never, 1.0, 0.0, dur=1.0, ease=EASE)         # snaps back on "never happens"
    drag = (T.eight - C.lead - 2.0 + 0.0, T.eight - C.lead + 2.0)
    snap = (T.never - C.lead, T.never - C.lead + 1.0)

    def ghosts(t):
        a = 0.5 + (float(pos(t)) - 0.5) * float(back(t))
        if abs(a - 0.5) < 1e-3:
            return VGroup()
        return VGroup(ghost_ring(re_x(a), y1), ghost_ring(re_x(1 - a), y1, dashed=True))

    gh = wz.redraw(ghosts, during=(drag[0], snap[1]))
    rho = tex(r"\rho=0.8+i\gamma", size=34, color=C.rogue)
    hyp_tag = lab("hypothetical", 28, C.rogue)
    rogue_tags = VGroup(rho, hyp_tag).arrange(DOWN, buff=0.14, aligned_edge=RIGHT)
    rogue_tags.move_to([4.7 - rogue_tags.width / 2, 3.12, 0])
    h.play(FadeIn(rogue_tags, shift=0.08 * DOWN), at=T.eight + 0.3, dur=0.6)

    # ── its wave grows like x^0.8 and pulls the count far from the curve ──
    hyp = D["err"] + D["hyp"]
    grow = key(T.grow08 + 0.3, 0.0, 1e8, dur=3.2, ease="in_out_sine")
    grow_win = (T.grow08 + 0.3 - C.lead, T.grow08 + 0.3 - C.lead + 3.2)
    amp = key(T.never, 1.0, 0.0, dur=1.0, ease=EASE)
    grown = wp.redraw(lambda t: err_mob(hyp, SY0, C.rogue, xmax=float(grow(t))), during=grow_win)
    wp.remove(grown, at=snap[0])
    held = wp.redraw(lambda t: err_mob(D["err"] + float(amp(t)) * D["hyp"], SY0, C.rogue), during=snap)
    wp.remove(held, at=snap[1])
    x08 = tex(r"x^{0.8}", size=36, color=C.rogue)
    x08.move_to([ex(0.62e8), EY + SY0 * 15500, 0])
    h.play(FadeIn(x08), at=T.grow08 + 1.6, dur=0.6)
    h.play(FadeOut(x08), FadeOut(rogue_tags), at=T.never, dur=0.6)

    # ── if every zero is on the line: the gap stays inside sqrt(x) ln x / 8 pi (Schoenfeld, if RH) ──
    env = VGroup(envelope_mob(1, SY1), envelope_mob(-1, SY1))
    wp.play(Create(env[0]), Create(env[1]), at=T.root_log, dur=1.2)
    if_rh = lab("if RH", 28, C.bound)
    if_rh.move_to([EX1 + 0.15 + if_rh.width / 2, EY + SY1 * float(data()["env"][-1]), 0])
    wp.play(FadeIn(if_rh), at=T.root_log + 1.0, dur=0.5, lead=0)
    bound = tex(r"|\pi(x)-\mathrm{li}(x)|", r"<", r"\frac{\sqrt{x}\,\ln x}{8\pi}", size=40, colors={0: C.gap, 2: C.bound})
    pin(bound, top=3.55, left=-5.9)
    cond = VGroup(lab("if RH", 28, C.text), tex(r"x\ge2657", size=30, color=C.muted),
                  caps(r"L. Schoenfeld $\cdot$ 1976", 30, C.ink)).arrange(RIGHT, buff=0.32)
    pin(cond, top=bound.get_bottom()[1] - 0.18, left=-5.9)
    h.play(Write(bound), at=T.root_log + 0.4, dur=1.0)
    h.play(FadeIn(cond), at=T.root_log + 1.2, dur=0.6, lead=0)

    # ── von Koch, 1901: and the reverse ──
    rh = tex(r"\mathrm{RH}", size=40)
    rhs = tex(r"\pi(x)=\mathrm{li}(x)+O(\sqrt{x}\,\ln x)", size=40)
    row = VGroup(rh, Line(ORIGIN, RIGHT * 1.1), rhs).arrange(RIGHT, buff=0.22)
    pin(row, top=3.55, left=-5.9)
    a0, a1 = row[1].get_start(), row[1].get_end()
    fwd = Arrow(a0, a1, buff=0, color=C.text, stroke_width=3, max_tip_length_to_length_ratio=0.25)
    rev = Arrow(a1, a0, buff=0, color=C.text, stroke_width=3, max_tip_length_to_length_ratio=0.25)
    koch = caps(r"H. von Koch $\cdot$ 1901", 32, C.ink)
    pin(koch, top=row.get_bottom()[1] - 0.2, left=-5.9)
    h.play(FadeOut(bound), FadeOut(cond), at=T.koch - 0.1, dur=0.5)
    h.play(FadeIn(rh), FadeIn(rhs), FadeIn(koch), at=T.koch + 0.4, dur=0.6)
    h.play(GrowArrow(fwd), at=T.koch + 0.9, dur=0.6, lead=0)
    h.play(GrowArrow(rev), at=T.reverse, dur=0.6)

    # ── mirrored pairs: the largest real part can't go below one half ──
    a = key(T.smallest, 0.9, 0.5, dur=1.6, ease=EASE)
    pair = (T.mirrored - C.lead, T.smallest - C.lead + 1.6)

    def mirror(t):
        v = float(a(t))
        r, l = ghost_ring(re_x(v), Y_PAIR), ghost_ring(re_x(1 - v), Y_PAIR, dashed=True)
        link = DashedLine([re_x(1 - v), Y_PAIR, 0], [re_x(v), Y_PAIR, 0], color=C.rogue, stroke_width=1.6,
                          dash_length=0.06) if v - 0.5 > 0.06 else VGroup()
        th = tex(r"\Theta", size=30, color=C.rogue).move_to([re_x(v), Y_PAIR + 0.3, 0])
        return VGroup(link, r, l, th)

    m0 = mirror(pair[0])
    wz.play(FadeIn(m0), at=T.mirrored - 0.3, dur=0.5)
    wz.remove(m0, at=pair[0])
    held_pair = wz.redraw(mirror, during=pair)
    theta = tex(r"\Theta", r"\ge", r"\tfrac12", size=40, colors={0: C.rogue})
    theta.move_to([4.7 - theta.width / 2, Y_PAIR, 0])
    h.play(FadeIn(theta, shift=0.08 * LEFT), at=T.smallest + 1.2, dur=0.6)

    # ── the primes stay as close to the curve as they possibly can ──
    wz.play(FadeOut(held_pair), at=T.close_as - 0.6, dur=0.6)
    wp.play(Indicate(env, color=C.text, scale_factor=1.0), at=T.close_as, dur=1.2)
