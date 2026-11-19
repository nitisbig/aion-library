"""s16 one fact: columns, area, a direction and the way back, each failing on its own phrase. Then all four reopen together and fail
together on the same frame, because they are one fact."""
from aion import *

from beats import T
from film2 import CX16 as CX, CY16 as CY, H16 as H, MOMENTS as moments, frame
from shots import lab, tex

TAGS = ("columns", "area", "direction", "way back")


@scene(T.cut_fact, T.cut_powders)
def s16_one_fact(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_fact, T.cut_powders)], z=0))
    m = s.manim(z=5, parallax=0.0)

    # ── the four names, and the arrows that tie them together ──
    for word, cx, b in zip(TAGS, CX, moments):
        tag = lab(word, size=38).move_to([cx, CY - H / 2 - 0.45, 0])
        tag.shift((CY - H / 2 - 0.58 - tag.family_members_with_points()[-1].get_bottom()[1]) * UP)   # all four share one baseline
        m.play(FadeIn(tag, shift=0.06 * UP), at=b, dur=0.5)
    ties = VGroup(*[tex(r"\Leftrightarrow", size=40).move_to([(CX[i] + CX[i + 1]) / 2, CY, 0]) for i in range(3)])
    cards = VGroup(*[BackgroundRectangle(t_, color=C.bg, fill_opacity=0.9, buff=0.06) for t_ in ties])
    m.play(FadeIn(cards), FadeIn(ties), at=T.if_any - 0.1, dur=0.6)
    s.solid(C.bg, z=50, opacity=key(T.cut_powders - 0.42, 0.0, 1.0, dur=0.4, lead=0))
