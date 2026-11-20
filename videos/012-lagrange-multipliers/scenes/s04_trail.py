"""s04: the trail around the mountain. At the trail's highest point the ground still rises, and you can't go that way."""
from aion import *

from beats import T
from draw3d import Cam
from ch1 import backed, pin
from shots import BEST, BEST_S, E, LOW_S, SUMMIT, backdrop, curtain, draw_mountain, lab, live, p3, seen, surf, trail, view, hill_grad


def camera(t, t0, t1):
    u = (t - t0) / (t1 - t0)
    return Cam(az=-74 + 24 * u, el=34 - 4 * u, zoom=1.08, center=(0.1, -1.0))


@scene(T.cut_trail, T.cut_lagrange)
def s04_trail(s):
    backdrop(s)
    t0, t1 = float(s.start), float(s.end)
    draw = keys((T.hike, 0.0), (T.summit - 0.3, 1.0))
    walk = keys((T.stay - 0.4, LOW_S), (T.stand - 0.1, BEST_S))
    ss = np.linspace(0, 2 * np.pi, 320)
    show_walker = fade(T.stay - 0.2, dur=0.4)
    grow = key(T.not_flat + 0.5, 0.0, 1.0, dur=0.9, ease=E)
    d = hill_grad(*BEST)
    d = d / np.linalg.norm(d)
    path_xy = BEST[None, :] + np.linspace(0, 0.82, 30)[:, None] * d[None, :]

    def frame(t):
        cam = camera(t, t0, t1)
        v = view().begin(cam)
        draw_mountain(v, contour_alpha=0.35)
        P = surf(*trail(ss[: max(2, int(float(draw(t)) * len(ss)))]))
        v.line(P, C.con, 6.0, visible=seen(P, cam))
        peak = surf(*SUMMIT, lift=0.06)
        if t >= float(T.summit) - 0.3:
            v.dot(peak, C.wrong, 0.11, ring=C.bg)
        a = float(show_walker(t))
        if a > 0.02:
            g = float(grow(t))
            if g > 0.01:
                q = surf(path_xy[:, 0][: max(2, int(g * 30))], path_xy[:, 1][: max(2, int(g * 30))], lift=0.05)
                v.line(q[:-1], C.text, 5.0)
                v.arrow(q[-2], q[-1], C.text, 5.0, tip=0.3)
            v.dot(surf(*trail(float(walk(t)))), C.you, 0.12, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-10))
    hud = s.manim(z=10)

    def peak_tag(t):
        xy, _ = camera(t, t0, t1).frame(surf(*SUMMIT, lift=0.06))
        return lab("summit", 32, C.wrong).move_to(p3(xy) + [0, 0.5, 0])
    live(hud, peak_tag, (T.summit, T.cut_lagrange))
    tip = surf(*path_xy[-1], lift=0.05)
    cam_t = lambda t: camera(t, t0, t1)
    pin(hud, cam_t, tip, backed(lab("still rising", 34, C.text), 0.1, 0.85), T.rises, T.cut_lagrange - 0.05, off=(1.45, 0.25))
    pin(hud, cam_t, tip, backed(lab("off limits", 34, C.wrong), 0.1, 0.85), T.cant, T.cut_lagrange - 0.05, off=(1.45, -0.25))
    curtain(s)
