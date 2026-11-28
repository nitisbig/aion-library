"""s28 checks (P48-P49): what has been checked, by whom, and what's missing. A. Sutherland (MIT) rebuilt every file:
the wall of 175,187 tiles returns. The Buzzard card grows into his four questions, each answered from Sutherland's page
(research.md A9, A16; stamped 21 Nov 2026, 09:30 UTC): finished checks ticked, running ones open. His quote to
Scientific American. Then: no human-readable paper yet (a dashed, empty page), and, per Alpoge's note, who did what.
Ends on black."""
from aion import *

from beats import T
from media_assets import portrait_card
from look import caps, lab, seen, tex
from status import buzzard_card, chip, ring, wall_rgba

PX0, PX1 = -1.0, 6.65                          # the checklist panel


def check_row(k, question, answers):
    """Question k, then its answers: (text, done) pairs, each with its ring."""
    q = VGroup(tex(str(k), size=26, color=C.muted), lab(question, 24, C.text)).arrange(RIGHT, buff=0.2)
    parts = []
    for text, done in answers:
        rg = ring(done, r=0.09)
        parts.append(VGroup(rg) if text is None else VGroup(lab(text, 20, C.muted), rg).arrange(RIGHT, buff=0.1))
        parts[-1].ring = rg
    a = VGroup(*parts).arrange(RIGHT, buff=0.18)
    row = VGroup(q, a).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    a.shift(0.36 * RIGHT)
    row.q, row.a = q, a
    return row


@scene(T.cut_checks, T.cut_stepanov)
def s28_checks(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_stepanov - 0.5, T.cut_stepanov - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)
    bz = s.manim(z=7, parallax=0.0, opacity=fade)
    card = buzzard_card(robin=True)
    bz.add(card)
    out = T.ck_nopaper - 0.5

    # ── Sutherland rebuilt all 175,187 files: the wall ──
    who = caps(r"A. Sutherland $\cdot$ MIT", 26, C.ink)
    who.move_to([-4.55 + who.width / 2, 3.15, 0])
    portrait_card(s, h, "sutherland", None, T.ck_so + 0.4, out + 0.6, (-5.55, 2.6), height=1.6)
    h.play(FadeIn(who, shift=0.06 * DOWN), at=T.ck_so + 0.5, dur=0.5)
    wall_op = keys((T.ck_rebuilt - 0.2, 0.0), (T.ck_rebuilt + 0.8, seen(0.85)), (out, seen(0.85)), (out + 0.6, 0.0),
                   lead=0)
    s.add(ArrayLayer(wall_rgba(px=1200), height=4.4, pos=(-3.95, -0.55), z=1, parallax=0.0, opacity=wall_op))
    cnt = lab("175,187 files", 26, C.lean)
    cnt.move_to([-4.55 + cnt.width / 2, 2.3, 0])
    h.play(FadeIn(cnt), at=T.ck_files, dur=0.5)

    # ── Buzzard's four questions, answered from Sutherland's page ──
    rows = VGroup(
        check_row(1, "does the statement mean RH?", [("Mathlib definition", False), ("Robin cross-check", False)]),
        check_row(2, "does it compile?", [("175,187 / 175,187 files", True)]),
        check_row(3, "does it prove that statement?", [("statement compare", True), ("comparator", False)]),
        check_row(4, "no kernel bug?", [("four independent checkers", True), (None, True), (None, True),
                                        (None, False)]),
    ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
    head = caps(r"K. Buzzard $\cdot$ four questions", 26, C.ink)
    stamp = lab(r"as of 21 Nov 2026, 09:30 UTC", 20, C.muted)
    body = VGroup(head, rows, stamp).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
    box = RoundedRectangle(width=PX1 - PX0, height=body.height + 0.4, corner_radius=0.1, stroke_color=C.human,
                           stroke_width=1.4)
    panel = VGroup(box, body)
    box.move_to([(PX0 + PX1) / 2, 3.55 - box.height / 2, 0])
    body.move_to([PX0 + 0.25 + body.width / 2, box.get_y(), 0])
    grow = T.ck_several - 0.9
    bz.play(ReplacementTransform(card[0], box), ReplacementTransform(card[1][0], head),
            FadeOut(VGroup(*card[1][1:])), at=grow, dur=0.7, lead=0)
    for i, r in enumerate(rows):
        bz.play(FadeIn(r.q, shift=0.06 * RIGHT), FadeIn(r.a, shift=0.06 * RIGHT), at=T.ck_several + 0.4 * i,
                dur=0.4, lead=0)
    bz.play(FadeIn(stamp), at=T.ck_few, dur=0.5)
    done = VGroup(*[p.ring for r in rows for p in r.a if isinstance(p.ring, VGroup)])
    open_ = VGroup(*[p.ring for r in rows for p in r.a if not isinstance(p.ring, VGroup)])
    bz.play(*[Indicate(m, color=C.lean, scale_factor=1.3) for m in done], at=T.ck_accepted, dur=0.9)
    bz.play(*[Indicate(m, color=C.text, scale_factor=1.3) for m in open_], at=T.ck_running - 0.2, dur=0.9)

    # ── "approximately zero" ──
    qt = VGroup(lab(r"``the chance that anything is fishy here is approximately zero''", 24, C.text),
                caps(r"A. Sutherland $\cdot$ Scientific American, 20 Nov", 22, C.ink))
    qt.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
    qbox = RoundedRectangle(width=qt.width + 0.4, height=qt.height + 0.3, corner_radius=0.1, stroke_color=C.human,
                            stroke_width=1.4).move_to(qt)
    quote = VGroup(qbox, qt).move_to([(PX0 + PX1) / 2, -2.55, 0])
    h.play(FadeIn(quote, shift=0.06 * UP), at=T.ck_fishy, dur=0.6)

    # ── no human-readable paper yet ──
    bz.play(FadeOut(panel), at=out, dur=0.6, lead=0)
    h.play(FadeOut(VGroup(who, cnt, quote)), at=out, dur=0.6, lead=0)
    page = DashedVMobject(Rectangle(width=2.7, height=3.6, stroke_color=C.muted, stroke_width=2.0), num_dashes=60,
                          dashed_ratio=0.55).move_to([-3.6, 0.2, 0])
    pl = lab("no human-readable paper yet", 30, C.text).next_to(page, DOWN, buff=0.3)
    w.play(Create(page), at=T.ck_nopaper, dur=0.8)
    h.play(FadeIn(pl), at=T.ck_nopaper + 0.5, dur=0.5)
    per = caps(r"per L. Alp\"oge's note", 26, C.ink).move_to([2.9, 2.2, 0])
    n1 = chip("the argument: very long, for now", C.human)
    n2 = chip("shared before mastering the maths around it", C.human)
    n3 = chip("he steered the search", C.human)
    n4 = chip("Claude far outpaced him near the finish line", C.ai)
    ys = [1.35, 0.6, -0.55, -1.3]
    for c, y in zip((n1, n2, n3, n4), ys):
        c.move_to([0.4 + c.width / 2, y, 0])
    h.play(FadeIn(per), at=T.ck_long - 0.6, dur=0.5)
    h.play(FadeIn(n1, shift=0.06 * RIGHT), at=T.ck_long, dur=0.5)
    h.play(FadeIn(n2, shift=0.06 * RIGHT), at=T.ck_presenting, dur=0.5)
    h.play(FadeIn(n3, shift=0.06 * RIGHT), at=T.ck_steered, dur=0.6)
    h.play(FadeIn(n4, shift=0.06 * RIGHT), at=T.ck_outpaced, dur=0.6)
