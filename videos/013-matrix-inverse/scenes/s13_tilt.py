"""s13 tilt: the second column of A leans toward the first. The plane thins on the left while the inverse on the right has to stretch by
10, 100, then 1000. The tilt holds on the nearly flat moment, then the columns line up and the inverse is gone."""
from aion import *

from beats import T
from film2 import TILT as tr, frame, stretch
from shots import carded, chapter_card, lab, live, panel, readout, tex

BL, BR = (-6.6, -2.5, -0.2, 3.3), (0.2, -2.5, 6.6, 3.3)

@scene(T.cut_tilt, T.cut_many)
def s13_tilt(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_tilt, T.cut_many)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # frames and labels
    mn = s.manim(z=6, parallax=0.0)                   # the live numbers
    mh = s.manim(z=8, parallax=0.0)                   # the chapter card

    # ── chapter card ──
    chapter_card(mh, tex(r"\det A", "=", "0", size=104, colors={0: C.det, 2: C.det}), "What can't come back", T.cut_tilt, T.tilt - 1.0)
    run = (T.tilt - 0.8, T.x1000 + 0.85)
    last = (T.line_up, T.line_up + 0.75)

    # ── frames, names and the numbers ──
    frames = VGroup(panel(*BL, fill=False), panel(*BR, fill=False))
    names = VGroup(carded(tex("A", size=58, color=C.fwd).move_to([BL[0] + 0.48, BL[3] - 0.46, 0]), buff=0.08),
                   carded(tex(r"A^{-1}", size=58, color=C.back).move_to([BR[0] + 0.62, BR[3] - 0.5, 0]), buff=0.08))
    m.play(FadeIn(frames), FadeIn(names), at=T.tilt - 0.75, dur=0.7)

    y = -3.05
    d_lab = tex(r"\det A", "=", size=56, colors={0: C.det}).move_to([-4.7, y, 0])
    x_lab = lab("stretch", size=38, color=C.back).move_to([1.75, y, 0])
    times = tex(r"\times", size=56, color=C.back).move_to([3.05, y, 0])
    m.play(FadeIn(d_lab), FadeIn(x_lab), FadeIn(times), at=T.tilt - 0.4, dur=0.6)

    def numbers(t):
        c = float(tr(t))
        g = VGroup(readout(f"{4 * (1 - c):.3f}", -3.55, y, color=C.det))
        if c < 0.99999:
            g.add(readout(str(int(round(stretch(c)))), 3.42, y, color=C.back))
        return g
    live(mn, numbers, (T.tilt - 0.4, T.tilt + 0.1), run, last)

    # ── hold on the nearly flat moment ──
    ring = SurroundingRectangle(VGroup(times, readout("1000", 3.42, y)), color=C.home, buff=0.16, stroke_width=2.6)
    m.play(Create(ring), at=T.keep, dur=0.6)
    m.play(FadeOut(ring), at=T.line_up - 0.3, dur=0.4)

    # ── the columns line up ──
    inf = tex(r"\infty", size=72, color=C.back).move_to([3.85, y, 0])
    m.play(FadeIn(inf, scale=1.2), at=T.line_up + 0.65, dur=0.4)
    m.play(Indicate(d_lab[0], color=C.det, scale_factor=1.15), at=T.det_zero + 0.3, dur=0.9)
    m.play(Indicate(inf, color=C.back, scale_factor=1.3), at=T.infinity, dur=0.9)
    s.solid(C.bg, z=50, opacity=key(T.cut_many - 0.42, 0.0, 1.0, dur=0.4, lead=0))
