"""s21 camera: from outside, the camera walks up the street. Then the outside view locks to the camera, and it is the town that slides backward,
which is what the game really computes: the inverse of the camera's matrix, applied to everything else."""
from aion import *

from beats import T
from film3 import frame
from shots import EASE, lab, p3, panel, tex, varrow
from stage import SS
from world import town_rgba

W, H = 6.3, 6.3 * 468 / 894
CL, CR = np.array([-3.3, 0.45]), np.array([3.3, 0.45])
RATE = 0.6                                            # the walk, slowed so the town can be read


def box(c):
    return (c[0] - W / 2, c[1] - H / 2, c[0] + W / 2, c[1] + H / 2)


@scene(T.cut_camera, T.cut_blur)
def s21_camera(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_camera, T.cut_blur)], z=0))
    m = s.manim(z=5, parallax=0.0)                    # frames and symbols

    def walked(t):
        return RATE * max(0.0, t - T.cut_camera)

    # ── what the camera sees ──
    s.add(FramesLayer(lambda t: town_rgba(walked(t), W=894 * SS, H=468 * SS), height=H, pos=(CR[0], CR[1]), during=[(T.cut_camera, T.cut_blur)],
                      opacity=fade(T.cut_camera + 0.05, dur=0.5), z=2))

    frames = VGroup(panel(*box(CL), fill=False), panel(*box(CR), fill=False))
    m.play(FadeIn(frames), at=T.cut_camera + 0.05, dur=0.5, lead=0)
    y_tag = CL[1] - H / 2 - 0.38
    m.play(FadeIn(lab("outside", size=34).move_to([CL[0], y_tag, 0])), FadeIn(lab("what it sees", size=34).move_to([CR[0], y_tag, 0])), at=T.game2, dur=0.5)

    # ── the camera's matrix, and its inverse ──
    y_sym = -2.72
    c_sym = VGroup(tex("C", size=64, color=C.cam), lab("camera", size=36)).arrange(RIGHT, buff=0.3).move_to([CL[0], y_sym, 0])
    m.play(FadeIn(c_sym), at=T.placed, dur=0.5)
    inv = VGroup(tex(r"C^{-1}", size=64, color=C.back), lab("world", size=36)).arrange(RIGHT, buff=0.3).move_to([CR[0], y_sym, 0])
    m.play(FadeIn(inv), at=T.applies, dur=0.5)

    # ── you never walk: the world is carried past you ──
    m.play(FadeOut(c_sym), at=T.never_walk - 0.3, dur=0.4)
    back = varrow((-1.5, y_sym), (-5.1, y_sym), C.back, width=6.0, tip=0.36)
    m.play(GrowFromPoint(back, p3((-1.5, y_sym))), at=T.carried, dur=0.9, ease=EASE)
    m.play(Indicate(inv[0], color=C.back, scale_factor=1.15), at=T.carried + 0.3, dur=0.9)
    s.solid(C.bg, z=50, opacity=key(T.cut_blur - 0.42, 0.0, 1.0, dur=0.4, lead=0))
