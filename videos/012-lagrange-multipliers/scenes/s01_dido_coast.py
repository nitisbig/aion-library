"""s01: one unbroken shot of Dido's galley, a growing wall of real images, then the ox hide becomes a rope on the beach."""
from aion import *

from beats import T
from cards import card, icon, photo_layer, tracked
from shots import E, backdrop, curtain, live
from story import story
from voyage import voyage

DIDO = [-5.25, 1.0, 0]
KING = [-2.3, 1.0, 0]


@scene(T.start, T.cut_question)
def s01_dido_coast(s):
    backdrop(s)
    s.add(FramesLayer(voyage(T.king - 0.2, T.king, T.strips), height=8.0, z=-20, during=[(T.start, T.strips + 0.5)]))
    hud = s.manim(z=20, parallax=0.0)

    # the years run backward in the evening sky
    glyphs = [MathTex(str(d), font_size=118, color=C.ink) for d in range(10)]
    step = max(g.width for g in glyphs) + 0.08
    era = {"AD": tracked("ad", 40, C.ink), "BC": tracked("bc", 40, C.gold)}
    roll = keys((T.start + 1.3, 2026.0), (T.queen - 1.75, -814.0), default_ease="smooth")
    seen = fade(T.start + 0.5, dur=0.7) * (1 - fade(T.queen - 0.6, dur=0.45))

    def years(t):
        y = int(round(float(roll(t))))
        row = VGroup(*[glyphs[int(ch)].copy().move_to([-5.75 + i * step, 3.15, 0]) for i, ch in enumerate(str(abs(y)).rjust(4)) if ch != " "])
        mark = era["BC" if y < 0 else "AD"].copy().move_to([-5.75 + 3.5 * step + 0.2, 2.9, 0], aligned_edge=LEFT)
        rule = Line([-6.2, 2.5, 0], [-2.7, 2.5, 0], color=C.gold, stroke_width=3)
        return VGroup(row, mark, rule).set_opacity(float(seen(t)))
    held = live(hud, years, (T.start + 0.5, T.queen - 0.1))
    hud.remove(held[-1], at=T.queen - 0.1)

    # only two images, each settling in slowly on its word and staying until the workbench rises
    dido = card("turner", "Dido", "J. M. W. Turner, 1815", h=1.9, tilt=0, pos=DIDO, photo=False)
    king = card("merian_deal", "The local king", r'Matth\"aus Merian, 1630', h=1.9, tilt=0, pos=KING, photo=False)
    hud.play(FadeIn(dido), at=T.queen + 0.1, dur=1.6, ease="smooth", lead=0)
    s.add(photo_layer("turner", dido, T.queen + 0.1))
    hud.play(FadeIn(king), at=T.king + 0.4, dur=1.6, ease="smooth", lead=0)
    s.add(photo_layer("merian_deal", king, T.king + 0.4))

    # the story so far, written along the water in small gold icons
    marks = [("crown", "queen", T.queen), ("anchor", "landfall", T.africa - 1.0), ("palm", "Africa", T.africa), ("king", "king", T.king + 0.4), ("gate", "city", T.king + 1.65), ("ox", "ox hide", T.hide + 1.0)]
    xs = np.linspace(-5.4, 5.4, len(marks))
    for i, (name, word, at) in enumerate(marks):
        art = icon(name, 0.66).move_to([xs[i], -2.98, 0])
        tag = tracked(word, 22, C.ink).move_to([xs[i], -3.56, 0])
        hud.play(Create(art), at=at, dur=0.8, ease=E, lead=0.05)
        hud.play(FadeIn(tag, shift=0.06 * UP), at=at + 0.25, dur=0.5, ease=E, lead=0)
        if i:
            hud.play(Create(Line([xs[i - 1] + 0.52, -2.98, 0], [xs[i] - 0.52, -2.98, 0], color=C.gold, stroke_width=2)), at=at - 0.35, dur=0.45, ease=E, lead=0)

    # the king's offer, set in the sky
    q1 = Tex(r"\textit{as much ground as she could surround}", font_size=41, color=C.ink).move_to([3.45, 3.3, 0])
    hud.play(FadeIn(q1, shift=0.12 * UP), at=T.joke + 1.65, dur=0.7, ease=E, lead=0)

    # the workbench rises over the voyage, and everything after it is painted in one layer
    s.add(FramesLayer(story(T), height=8.0, z=30, opacity=keys((T.strips - 0.95, 0.0), (T.strips - 0.15, 1.0)), during=[(T.strips - 0.95, T.cut_question)]))
    top = s.manim(z=40, parallax=0.0)

    def note(text, at, out, y=3.4, size=48, color=None):
        n = tracked(text, size, color or C.ink).move_to([0, y, 0])
        rule = Line([-n.width / 2, y - 0.42, 0], [n.width / 2, y - 0.42, 0], color=C.gold, stroke_width=2.5)
        top.play(FadeIn(n, shift=0.1 * UP), Create(rule), at=at, dur=0.6, ease=E, lead=0)
        top.play(FadeOut(n), FadeOut(rule), at=out - 0.35, dur=0.35, ease=E, lead=0)
    note("one ox hide", T.strips - 0.1, T.thread)
    note("thin as thread", T.thread, T.rope - 0.1)
    note("one enormous rope", T.rope, T.shore - 0.4)
    free = tracked("the sea guards this side", 34, C.foam).move_to([-0.7, -0.28, 0])
    top.play(FadeIn(free, shift=0.08 * UP), at=T.guard + 0.3, dur=0.6, ease=E, lead=0)
    q = Tex(r"\textit{what shape?}", font_size=76, color=C.ink).move_to([-0.7, -1.55, 0])
    top.play(FadeIn(q, shift=0.12 * UP), at=T.shape_q, dur=0.7, ease=E, lead=0)
    curtain(s, a=False)
