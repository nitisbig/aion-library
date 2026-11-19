"""s23 noise: the blur squeezes fine detail almost to nothing, so its inverse must stretch that detail enormously, and any trace of noise goes with
it. Real deblurring stops short: a cutoff drops the directions that barely survived, and a clean die comes back."""
from aion import *

from beats import T
from deblur import buried_rgba, rescue_rgba, smear_rgba, worst_stretch
from film3 import frame
from shots import EASE, carded, grid_lines, lab, panel, tex, tilt

PIC, PH = (-3.55, 0.0), 5.4
X0, X1, BASE, TALL = 0.85, 6.3, -2.35, 3.6
STEPS_B, STEPS_R = 30, 40


@scene(T.cut_noise, T.cut_second)
def s23_noise(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_noise, T.cut_second)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # frames and tags

    # ── the picture: blur again, bury it, rescue it ──
    smear = key(T.cut_noise + 0.15, 1.0, 49.0, dur=1.0, ease=EASE)
    bury = key(T.noise + 2.5, 0.0, 1.0, dur=1.8, ease=EASE)
    cut = key(T.stops + 0.35, 0.0, 1.0, dur=2.0, ease=EASE)

    def picture(t):
        if float(cut(t)) > 0:
            return rescue_rgba(int(round(float(cut(t)) * STEPS_R)))
        if t >= T.noise:
            return buried_rgba(int(round(float(bury(t)) * STEPS_B)))
        return smear_rgba(float(smear(t)))
    s.add(FramesLayer(picture, height=PH, pos=PIC, during=[(T.cut_noise, T.cut_second)], z=1))
    m.add(panel(PIC[0] - PH / 2, PIC[1] - PH / 2, PIC[0] + PH / 2, PIC[1] + PH / 2, fill=False), at=T.cut_noise)

    # ── remember the nearly flat plane ──
    cen, u = np.array([3.55, 0.0]), 0.5
    box = (X0, -2.2, X1, 2.2)
    flat = VGroup(grid_lines(tilt(0.999), center=cen, unit=u, box=box, n=5, minor=1), panel(*box, fill=False),
                  carded(tex(r"\times 1000", size=56, color=C.back).move_to([X1 - 1.05, -1.65, 0]), buff=0.08))
    m.play(FadeIn(flat), at=T.remember + 0.1, dur=0.5)
    m.play(FadeOut(flat), at=T.squeezes - 0.5, dur=0.4)

    m.add(panel(0.55, -2.95, 6.65, 2.1, fill=False), at=T.squeezes - 0.1)

    y_tag = 2.5
    t_sq = lab("squeezed", size=36, color=C.fwd).move_to([X0 + 0.85, y_tag, 0])
    m.play(FadeIn(t_sq), at=T.squeezes, dur=0.5)
    t_st = VGroup(lab("stretched", size=36, color=C.back), tex(rf"\times {worst_stretch():.0f}", size=52, color=C.back)).arrange(RIGHT, buff=0.26).move_to([X1 - 1.5, y_tag, 0])
    m.play(FadeIn(t_st), at=T.enormous, dur=0.5)

    # ── a trace of noise ──
    y_pic = -3.05
    t_noise = lab("+ noise", size=36, color=C.null).move_to([PIC[0], y_pic, 0])
    t_use = lab("useless", size=38, color=C.null).move_to([PIC[0], y_pic, 0])
    m.play(FadeIn(t_noise), at=T.noise, dur=0.5)
    m.play(FadeOut(t_noise), at=T.useless - 0.6, dur=0.4)
    m.play(FadeIn(t_use), at=T.useless - 0.2, dur=0.5)
    m.play(FadeOut(t_use), at=T.stops, dur=0.4)

    # ── stop short ──
    t_cut = lab("cutoff", size=36).move_to([X1 - 0.7, -1.95, 0])
    m.play(FadeIn(t_cut), at=T.stops + 1.5, dur=0.5)
    s.solid(C.bg, z=50, opacity=key(T.cut_second - 0.42, 0.0, 1.0, dur=0.4, lead=0))
