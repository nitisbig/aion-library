"""s01 intro: replace with the storyboard's first section."""
from aion import *

from beats import T


@scene(T.start, T.end)        # change T.end to T.cut1 once beats.py defines cuts
def s01_intro(s):
    s.gradient(C.bg2, C.bg, radius=9)
    m = s.manim()
    title = Text("{{title}}", font=C.display_font, font_size=C.title_size, color=C.text)
    m.play(FadeIn(title, shift=0.3 * UP), at=T.start + 0.5, dur=C.fade)
    m.play(FadeOut(title), at=T.end - 1.0, dur=C.fade)
    s.fx(Vignette(C.vignette))
