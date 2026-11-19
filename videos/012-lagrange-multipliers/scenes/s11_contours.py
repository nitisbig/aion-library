"""s11: slice the mountain into level curves, lay them on the map, and see that the gradient always crosses them at a right angle."""
from aion import *

from beats import T
from classic import *


@scene(T.cut_ch2, T.cut_walk)
def s11_contours(s):
    stage(s, with_trail=False, at=T.walk_c - 0.2)
    z = keys((T.slice_ - 0.3, 0.35), (T.contour + 1.1, 2.75))
    tilt = keys((T.contour + 1.3, 0.0), (T.walk_c - 0.5, 1.0), default_ease=E)

    def frame(t):
        v = view().begin(lerp_cam(float(tilt(t)), POSE_3D, POSE_MAP))
        h = float(z(t))
        draw_mountain(v, contour_alpha=0.75, below=h)
        ground(v)
        if h < 2.74:
            for p in ring_at(h):
                v.line(p, C.text, 4.5, visible=seen(p, v.cam))
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-10, during=[(T.cut_ch2, T.walk_c)], opacity=key(T.walk_c - 0.1, 1.0, 0.0, dur=0.6)))
    progress(s, 2, "Contours")
    m = s.manim(z=2)
    loop = max(contour_paths(float(LEVELS[3])), key=len)[::2]
    u = keys((T.walk_c + 0.2, 0.0), (T.perp + 3.0, 0.72))

    def rover(t):
        q = loop[int(float(u(t)) * (len(loop) - 1))]
        g = hill_grad(*q)
        out = VGroup(walker(mp(q)))
        if t >= float(T.no_gain) - 0.2:
            a = mp(q)
            n = g / np.linalg.norm(g)
            d = np.array([-n[1], n[0]])
            out.add(arrow(a, a + p3(n) * 1.25, C.obj, tip=0.28))
            if t >= float(T.perp) - 0.2:
                r = 0.22
                out.add(poly([a + p3(d) * r, a + p3(d + n) * r, a + p3(n) * r], C.text, 3), poly([a - p3(d) * 1.0, a + p3(d) * 1.0], C.tang, 4))
        return out
    live(m, rover, (T.walk_c + 0.2, T.cut_walk))
    board(hud(s), [(lab("level curve", 32, C.obj), T.walk_c), (tex("f", "=", r"\text{const}", size=56, colors={0: C.obj}), T.walk_c),
                   (tex(r"\nabla f", r"\perp", r"\text{contour}", size=48, colors={0: C.obj}), T.perp)])
    curtain(s, a=True, b=False)
