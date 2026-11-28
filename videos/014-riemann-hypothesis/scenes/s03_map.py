"""s03 map (P08): the roadmap. The s02 frame (the staircase rebuilt from 100 waves, and the line of zeros) shrinks into
the top-left corner and stays there as the promise. Five small icons slide into a row and each lights as it is named:
zeta(s), a pinwheel (a zero), a wave that nearly touches zero (why it's hard), a theorem card tagged 'if RH' (what a
proof would mean), and the amber '20 Nov' outline. Then a fade to black for chapter 1's card."""
from aion import *

from beats import T
from look import (TOP_INF, ZX, GAM, carded, lab, pin, staircase_frame, tex, wheel_mob, zero_line, zy)

ROW_Y, GAPX = -0.35, 2.55
DIM = 0.1                                    # linear light: 0.1 reads as about a third


def icon_zeta():
    return tex(r"\zeta(s)", size=64, color=C.zeta)


def icon_pinwheel():
    w = wheel_mob(r0=0.03, r1=0.5, n=72)
    return VGroup(w, Dot(radius=0.06, color=C.zero).move_to(w))


def icon_nearmiss():
    xs = np.linspace(-0.8, 0.8, 160)
    ys = 0.04 + 0.42 * np.sin(np.pi * xs / 0.8) ** 2                      # dips that stop just short of zero
    ax = Line([-0.85, 0, 0], [0.85, 0, 0], color=C.muted, stroke_width=1.6)
    v = VMobject(color=C.zero, stroke_width=3.0)
    v.set_points_smoothly(np.column_stack([xs, ys, 0 * xs]))
    return VGroup(ax, v).shift(0.2 * DOWN)


def icon_theorem():
    card = Rectangle(width=1.3, height=1.0, stroke_color=C.text, stroke_width=1.8)
    lines = VGroup(*[Line([0, 0, 0], [w, 0, 0], color=C.muted, stroke_width=1.6) for w in (0.9, 0.7, 0.85)])
    lines.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to(card).shift(0.08 * UP)
    tag = lab("if RH", 22, C.text).next_to(card, DOWN, buff=0.1, aligned_edge=RIGHT)
    return VGroup(card, lines, tag)


def icon_nov():
    box = RoundedRectangle(width=1.5, height=0.75, corner_radius=0.12, stroke_color=C.claimed, stroke_width=2.4)
    return VGroup(box, lab("20 Nov", 28, C.claimed).move_to(box))


def faded(m, k):
    """Scale every part's fill and stroke opacity by k (set_opacity would fill open curves)."""
    for sm in m.family_members_with_points():
        sm.set_fill(opacity=sm.get_fill_opacity() * k)
        sm.set_stroke(opacity=sm.get_stroke_opacity() * k)
    return m


@scene(T.cut_map, T.cut_atoms)
def s03_map(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_atoms - 0.5, T.cut_atoms - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    old = s.manim(z=2, parallax=0.0, opacity=fade)
    ic = s.manim(z=6, parallax=0.0, opacity=fade)

    # ── s02's last frame ──
    frame = staircase_frame()
    zl = zero_line(top=TOP_INF, lit=np.ones(len(GAM)), line_opacity=1.0, width=3.2)
    zeros_tag = lab("zeros", 30, C.zero)
    zeros_tag.move_to([ZX + 0.16 + zeros_tag.width / 2, float(zy(GAM[0])) - 0.02, 0])
    defn = tex(r"\pi(x)", r"=\#\{", r"p", r"\le x\}", size=44, colors={0: C.prime, 2: C.prime})
    pin(defn, top=3.5, left=-5.9)
    tally = tex(r"\pi(100)", r"=25", size=40, colors={0: C.prime})
    pin(tally, top=2.78, left=-5.9)
    count = tex(r"1", r"\to 5", r"\to 30", r"\to 100", size=40, color=C.zero)
    row = VGroup(lab("waves", 34, C.zero), count).arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
    pin(row, top=2.05, left=-5.9)
    old.add(zl, zeros_tag, frame, defn, tally, row)

    # ── that takes some unpacking: the promise shrinks into the corner ──
    old.play(FadeOut(VGroup(defn, tally, row, zeros_tag)), at=T.cut_map + 0.5, dur=0.4, lead=0)
    small = VGroup(zl, frame)
    target = small.copy().scale(0.3)
    target.move_to([-6.55 + target.width / 2, 3.6 - target.height / 2, 0])
    for sm in target.family_members_with_points():
        sm.set_stroke(width=sm.get_stroke_width() * 0.5)
    faded(target, 0.6)
    old.play(Transform(small, target), at=T.cut_map + 0.6, dur=1.2, lead=0)

    # ── five icons slide in, dim; each lights as it is named ──
    icons = [icon_zeta(), icon_pinwheel(), icon_nearmiss(), icon_theorem(), icon_nov()]
    words = [T.m_zeta + 0.14, T.m_zeros + 0.13, T.m_hard, T.m_mean + 0.16, T.m_nov + 0.24]   # on the key word
    for k, m in enumerate(icons):
        m.move_to([(k - 2) * GAPX, ROW_Y, 0])
    dimmed = VGroup(*[faded(m.copy(), DIM) for m in icons])
    ic.play(LaggedStart(*[FadeIn(m, shift=0.4 * LEFT) for m in dimmed], lag_ratio=0.12), at=T.cut_map + 1.2, dur=1.0,
            lead=0)
    for m, d, at in zip(icons, dimmed, words):
        ic.play(FadeIn(m, scale=1.08), at=at, dur=0.5)
        ic.remove(d, at=at + 0.5)
