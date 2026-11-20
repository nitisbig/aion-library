"""s01: one unbroken point-cloud shot of Dido's galley with the queen, the king and the ox hide, then the hide becomes a rope on the beach."""
from aion import *

from pathlib import Path

from beats import T
from cards import tracked
from clip import Clip
from shots import E, backdrop, curtain
from story import story

VOYAGE = Path(__file__).resolve().parents[1] / "assets/voyage_pc.mp4"


@scene(T.start, T.cut_question)
def s01_dido_coast(s):
    backdrop(s)
    # the voyage is a baked point-cloud shot (pointcloud/render.py): it carries its own titles, the queen, the king,
    # the joke and the ox hide, all timed to the same beats
    s.add(FramesLayer(Clip(VOYAGE), height=8.0, z=-20, during=[(T.start, T.strips + 0.5)]))

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
