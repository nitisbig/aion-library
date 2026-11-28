"""s30 status (P51-P52): officially still open. A Clay card, Unsolved, with its three rules (published, two years,
broadly accepted) unlit; a serious claim under examination (amber). Then the status ladder, built bottom-up: evidence
(10^13 zeros), theorem (>= 2/3 on the line, people + Lean; the proportion bar as its picture), proposed proof (RH, amber
outline; machine checks partly complete), understood and accepted (dotted, empty). Ends on black for the outro."""
from aion import *

from beats import T
from look import caps, lab, seen, tex
from status import chip, ring

RX0, RX1 = -5.6, 5.6
RH_, GAP = 1.0, 0.32
RY = [-2.85, -2.85 + (RH_ + GAP), -2.85 + 2 * (RH_ + GAP), -2.85 + 3 * (RH_ + GAP)]


def rung(i, name, color, dotted=False, dashed=False):
    r = Rectangle(width=RX1 - RX0, height=RH_, stroke_color=color, stroke_width=2.0).move_to([0, RY[i], 0])
    if dotted:
        r = DashedVMobject(r, num_dashes=120, dashed_ratio=0.3)
    elif dashed:
        r = DashedVMobject(r, num_dashes=70, dashed_ratio=0.6)
    t = lab(name, 28, color).move_to([RX0 + 0.25, RY[i], 0], aligned_edge=LEFT)
    return VGroup(r, t)


@scene(T.cut_status, T.cut_outro)
def s30_status(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_outro - 0.5, T.cut_outro - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)

    # ── officially, still open: the Clay card ──
    clay = caps("Clay Mathematics Institute", 34, C.ink)
    uns = lab("Unsolved", 72, C.text)
    rules = VGroup(*[chip(t, C.conj, size=26) for t in ("published", "2 years", "broadly accepted")])
    rules.arrange(RIGHT, buff=0.35)
    for c in rules:                                       # unlit: dim outline and text, never filled
        c.box.set_stroke(opacity=0.45)
        c[1].set_opacity(0.45)
    body = VGroup(clay, uns, rules).arrange(DOWN, buff=0.45).move_to([0, 0.7, 0])
    box = RoundedRectangle(width=body.width + 0.9, height=body.height + 0.7, corner_radius=0.12,
                           stroke_color=C.ink, stroke_width=1.6).move_to(body)
    w.play(Create(box), FadeIn(clay), at=T.ss_off, dur=0.6)
    h.play(FadeIn(uns, scale=0.95), at=T.ss_open - 0.2, dur=0.6)
    for c, at in zip(rules, (T.ss_published, T.ss_two, T.ss_broad)):
        h.play(FadeIn(c, shift=0.06 * UP), at=at, dur=0.5)
    st = lab("a serious claim, under examination", 30, C.claimed)
    sb = RoundedRectangle(width=st.width + 0.5, height=st.height + 0.36, corner_radius=0.1, stroke_color=C.claimed,
                          stroke_width=2.0)
    claim = VGroup(sb, st.move_to(sb)).move_to([0, -2.5, 0])
    h.play(Create(sb), FadeIn(st), at=T.ss_serious - 0.2, dur=0.7)

    # ── several kinds of results: the ladder, bottom-up ──
    go = T.ss_kinds - 0.7
    w.play(FadeOut(VGroup(box, clay)), at=go, dur=0.5, lead=0)
    h.play(FadeOut(VGroup(uns, rules, claim)), at=go, dur=0.5, lead=0)
    small = VGroup(caps("Clay", 24, C.ink), lab("Unsolved", 24, C.text)).arrange(RIGHT, buff=0.2)
    small.move_to([6.6 - small.width / 2, 3.3, 0])
    h.play(FadeIn(small), at=go + 0.4, dur=0.5, lead=0)
    rungs = [rung(0, "evidence", C.evidence), rung(1, "theorem", C.human),
             rung(2, "proposed proof", C.claimed, dashed=True), rung(3, "understood and accepted", C.conj, dotted=True)]
    for i, r in enumerate(rungs):
        w.play(Create(r[0]), FadeIn(r[1]), at=T.ss_kinds + 0.4 * i, dur=0.4, lead=0)

    ex = 0.2                                              # results start here, inside their rung
    r1 = VGroup(tex(r"10^{13}", size=34, color=C.zero), lab("zeros on the line", 26, C.text)).arrange(RIGHT, buff=0.2)
    r1.move_to([ex + r1.width / 2, RY[0], 0])
    h.play(FadeIn(r1, shift=0.8 * LEFT), at=T.ss_ten, dur=0.8)

    bar = Rectangle(width=2.4, height=0.3, stroke_color=C.muted, stroke_width=1.4)
    fill = Rectangle(width=1.6, height=0.26, stroke_width=0, fill_color=C.crit, fill_opacity=seen(0.75))
    fill.move_to(bar.get_left() + [0.8, 0, 0])
    r2 = VGroup(VGroup(bar, fill), tex(r"\ge\tfrac23", size=32, color=C.crit), lab("people + Lean", 26, C.text))
    r2.arrange(RIGHT, buff=0.25).move_to([ex + 0.0, RY[1], 0])
    r2.move_to([ex + r2.width / 2, RY[1], 0])
    h.play(FadeIn(r2, shift=0.8 * LEFT), at=T.ss_two3, dur=0.8)

    r3a = lab("the full hypothesis", 26, C.text)
    marks = VGroup(*[ring(d, r=0.1) for d in (True, True, True, False)]).arrange(RIGHT, buff=0.12)
    r3b = VGroup(lab("machine checks", 22, C.muted), marks).arrange(RIGHT, buff=0.2)
    r3 = VGroup(r3a, r3b).arrange(RIGHT, buff=0.45)
    r3.move_to([ex + r3.width / 2, RY[2], 0])
    h.play(FadeIn(r3a, shift=0.8 * LEFT), at=T.ss_full + 0.6, dur=0.8)
    h.play(FadeIn(r3b), at=T.ss_partly - 0.4, dur=0.6)

    top = rungs[3]
    w.play(Indicate(top[1], color=C.text, scale_factor=1.08), at=T.ss_last, dur=1.0)
    why = lab("why it works", 26, C.muted).move_to([ex + 1.0, RY[3], 0])
    h.play(FadeIn(why), at=T.ss_understand + 0.3, dur=0.6)
    begun = lab("barely begun", 22, C.muted).next_to(why, RIGHT, buff=0.5)
    h.play(FadeIn(begun), at=T.ss_understand + 1.6, dur=0.6)
