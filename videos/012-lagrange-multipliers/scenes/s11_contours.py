"""s11: a plane slices the mountain at equal heights and leaves contour rings. Walking one ring keeps your height, so the gradient is perpendicular to it."""
from aion import *

from beats import T
from ch1 import *

LV = 2.0                                    # the contour we walk
LOOP = walk_loop(LV)
LC = LOOP.mean(axis=0)


@scene(T.cut_ch2, T.cut_walk)
def s11_contours(s):
    backdrop(s)
    top = (-90, 89.5, 1.15, 0.0, -0.05, 400, 0, 0, 0)
    near = (-90, 89.5, 2.2, 0.0, -0.2, 400, LC[0], LC[1], LV)
    cam = camera(
        (T.cut_ch2, (-44, 40, 1.08, 0.1, -0.9, 26, 0, 0, 0)),
        (T.slice_, (-58, 22, 1.12, 0.0, -0.6, 26, 0, 0, 0.6)),
        (T.contour + 0.8, (-70, 26, 1.12, 0.0, -0.6, 26, 0, 0, 0.6)),
        (T.walk_c - 0.4, top),
        (T.walk_c + 1.8, (-120, 32, 1.9, 0.0, -0.4, 26, LC[0], LC[1], LV)),
        (T.no_gain - 0.2, (-140, 34, 1.9, 0.0, -0.4, 26, LC[0], LC[1], LV)),
        (T.no_gain + 1.8, near),
        (T.cut_walk, near),
    )
    sweep = lambda t: 0.1 + 2.85 * ramp(t, T.slice_ + 0.2, T.contour + 1.0)
    u = lambda t: 0.0 + 0.9 * ramp(t, T.walk_c + 0.1, T.cut_walk - 0.2)

    def walker_at(t):
        return LOOP[int(u(t) * (len(LOOP) - 1)) % len(LOOP)]

    def frame(t):
        v = view().begin(cam(t))
        pa = win(t, T.slice_, T.contour + 1.4, 0.5, 0.5)
        h = sweep(t)
        sa = win(t, T.walk_c + 0.2, T.tells + 0.4, 0.6, 0.7)
        if pa > 0.01:
            slab_under(v, h, pa)
        if sa > 0.01:
            slab_under(v, LV, sa, half=2.3, center=LC)
        mountain(v, tint=glass(h, pa, v.cam) if pa > 0.01 else (glass(LV, sa, v.cam, 2.3, LC) if sa > 0.01 else None))
        floor(v)
        wires(v, 1.0, 0.22)
        # the slicing plane, and the rings it leaves behind
        for lv in LEVELS:
            a = float(np.clip((h - lv) / 0.15, 0, 1))
            if a > 0.01:
                level(v, lv, C.obj, 3.0, 0.9 * a * (1 - 0.5 * ramp(t, T.walk_c, T.walk_c + 0.8)))
        if pa > 0.01:
            level(v, h, C.text, 5.0, pa)
            slab_edge(v, h, pa)
        # walk one contour: the height never changes
        wa = win(t, T.walk_c - 0.2, T.cut_walk + 0.5, 0.6, 0.3)
        if wa > 0.01:
            level(v, LV, C.you, 5.0, wa)
            if sa > 0.01:
                slab_edge(v, LV, sa, half=2.3, center=LC)
            q = walker_at(t)
            # the gradient and the contour's direction at the walker
            ga = win(t, T.no_gain - 0.3, T.cut_walk + 0.5, 0.6, 0.3)
            if ga > 0.01:
                i = int(u(t) * (len(LOOP) - 1)) % len(LOOP)
                d = LOOP[(i + 4) % len(LOOP)] - LOOP[(i - 4) % len(LOOP)]
                d = d / np.linalg.norm(d)
                z = LV + 0.05
                v.line([[*(q - 0.9 * d), z], [*(q + 0.9 * d), z]], C.tang, 4.5, ga)
                g = hill_grad(*q)
                n = g / np.linalg.norm(g)
                v.arrow([*q, z], grad_tip(q, 0.95 * ramp(t, T.no_gain - 0.3, T.no_gain + 0.5) + 1e-3), C.obj, width=6.0, tip=0.22, alpha=ga)
                ra = ga * ramp(t, T.perp - 0.2, T.perp + 0.4)
                if ra > 0.01:
                    r = 0.2
                    v.line([[*(q + r * d), z], [*(q + r * d + r * n), z + 0.02], [*(q + r * n), z + 0.03]], C.text, 3.0, ra)
            bead(v, q, r=0.1 * wa + 1e-3)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch2, T.cut_walk)]))
    title(s, "Chapter 2  ·  contours", T.cut_ch2 + 0.3, hold=3.4)
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, lambda t: [3.8, 3.8, sweep(t)], tex("f", "=", r"\text{const}", size=46, colors={0: C.obj}), T.slice_ + 0.6, T.contour + 1.3, off=(0.2, 0.35))
    far = [x for x in ring(LEVELS[2])[0] if x[1] < -1.0 and abs(x[0]) < 1.5][0]
    pin(m, cam, [*far, LEVELS[2]], lab("contour line", 32, C.obj), T.contour, T.walk_c, off=(0.0, -0.45))
    pin(m, cam, [*far, LEVELS[2]], lab("a level curve of f", 28, C.obj), T.contour + 1.0, T.walk_c, off=(0.0, -0.9))
    wq = lambda t: [*LOOP[int(0.9 * ramp(t, T.walk_c + 0.1, T.cut_walk - 0.2) * (len(LOOP) - 1)) % len(LOOP)], LV]
    pin(m, cam, wq, backed(lab("height never changes", 30, C.you), 0.1, 0.85), T.walk_c + 1.6, T.no_gain - 0.2, off=(0.0, -0.6))
    pin(m, cam, wq, tex(r"\nabla f", size=52, color=C.obj), T.no_gain + 0.6, T.cut_walk - 0.05, off=(0.75, 0.75))
    h = s.manim(z=20, parallax=0.0)
    headline(h, VGroup(lab("along the contour, no gain", 32, C.tang)), T.no_gain + 1.2, T.perp - 0.3)
    headline(h, tex(r"\nabla f", r"\ \perp\ ", r"\text{contour}", size=60, colors={0: C.obj, 2: C.tang}), T.perp, T.cut_walk - 0.05)
    curtain(s, a=True, b=False)
