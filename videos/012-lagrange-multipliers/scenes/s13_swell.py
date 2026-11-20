"""s13: lower a slicing plane from the summit until its contour first touches the trail. Then the trail turns out to be a level curve of g, and both families lie flat on the map."""
from aion import *

from beats import T
from ch1 import *

HC = 1.45                                   # the bowl's height at g = c (as in s10)
ALL = np.linspace(0, TAU, 360)
GK = (0.45, 0.72, 1.0, 1.22)                # the g family: levels as radii of the ellipse


def ellipse(r):
    return np.column_stack([TRAIL_A * r * np.cos(ALL), TRAIL_B * r * np.sin(ALL)])


@scene(T.cut_swell, T.cut_ch3)
def s13_swell(s):
    backdrop(s)
    whole = (-90, 89.5, 1.15, 0.0, -0.05, 400, 0, 0, 0)
    side = (-62, 22, 1.18, 0.0, -0.4, 26, 0, 0, 0.9)
    touch = (-150, 30, 2.1, 0.0, -0.3, 26, BEST[0], BEST[1], BEST_H)
    cam = camera(
        (T.cut_swell, whole),
        (T.high_c, side),
        (T.first_t - 0.4, (-75, 24, 1.18, 0.0, -0.4, 26, 0, 0, 0.9)),
        (T.that_touch + 0.4, touch),
        (T.insight - 0.2, touch),
        (T.itself + 0.6, (-62, 30, 1.12, 0.0, -0.6, 26, 0, 0, 0.5)),
        (T.level_g + 2.4, (-70, 36, 1.12, 0.0, -0.6, 26, 0, 0, 0.5)),
        (T.families + 1.6, whole),
        (T.cut_ch3, whole),
    )
    h_c = lambda t: 2.9 - (2.9 - BEST_H) * ramp(t, T.lower, T.first_t)
    ghost = lambda t: ramp(t, T.itself - 0.2, T.itself + 1.0)
    flatten = lambda t: ramp(t, T.families - 0.2, T.families + 1.6)

    def frame(t):
        v = view().begin(cam(t))
        gh, fl = ghost(t), flatten(t)
        ma = 1.0 - 0.88 * gh - 0.12 * fl
        pa = win(t, T.high_c - 0.3, T.insight + 0.6, 0.6, 0.8)
        if pa > 0.01:
            slab_under(v, h_c(t), pa)
        mountain(v, 1.0, ma, tint=glass(h_c(t), pa, v.cam) if pa > 0.01 else None)
        floor(v, 1.0 - max(gh, fl))
        if ma > 0.5:
            wires(v, 1.0, 0.2 * ma)
        # the f family: faint at first, laid flat at the end
        fa = 0.35 + 0.5 * fl
        if fl < 0.01:
            contours(v, 1.0, C.obj, 0.35, 1.8)
        else:
            for lv, paths in [(lv, ring(lv)) for lv in LEVELS]:
                for p in paths:
                    v.line(np.column_stack([p, np.full(len(p), lv * (1 - fl) + 0.01)]), C.obj, 2.6, fa)
        # the slicing plane lowered from the summit
        if pa > 0.01:
            h = h_c(t)
            slab_edge(v, h, pa)
            level(v, h, C.obj, 6.0, pa)
        # the trail: on the mountain, then on the bowl of g, then flat on the map
        bz = HC * (1 - fl)
        tz = hill(*ellipse(1.0).T) + 0.04
        z = tz + (bz + 0.03 - tz) * gh
        z = z * (1 - fl) + 0.02 * fl
        P = np.column_stack([ellipse(1.0), z])
        v.line(P, C.con, 6.5, visible=seen_k(P, v.cam, 1.0) if gh < 0.5 else None)
        # the bowl of g and its level curves
        ba = win(t, T.itself - 0.1, T.families + 1.2, 0.9, 1.2)
        if ba > 0.01:
            r, th = np.meshgrid(np.linspace(0, 1.22, 24), np.linspace(0, TAU, 73))
            v.mesh(TRAIL_A * r * np.cos(th), TRAIL_B * r * np.sin(th), HC * r**2, C.con, alpha=0.3 * ba, ambient=0.45)
        for i, k in enumerate(GK):
            if k == 1.0:
                continue
            ka = ramp(t, T.level_g + 0.3 + 0.4 * i, T.level_g + 0.9 + 0.4 * i)
            if ka > 0.01:
                v.line(np.column_stack([ellipse(k), np.full(len(ALL), HC * k**2 * (1 - fl) + 0.02)]), C.con, 3.0, 0.9 * ka)
        # the touch
        ta = win(t, T.first_t - 0.1, T.cut_ch3 + 1.0, 0.4, 0.3)
        if ta > 0.01:
            zb = BEST_H * (1 - fl) + 0.05 if gh < 0.5 else (HC * (1 - fl) + 0.05)
            kiss = ramp(t, T.kiss, T.kiss + 0.6)
            if kiss > 0.01:
                level(v, BEST_H, C.text, 6.0, kiss, z=0.03)
                d = trail_tangent(BEST_S)
                d = d / np.linalg.norm(d)
                v.line([[*(BEST - 1.1 * d), 0.05], [*(BEST + 1.1 * d), 0.05]], C.tang, 4.0, kiss)
            v.dot([*BEST, zb], C.you, 0.11, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_swell, T.cut_ch3)]))
    m = s.manim(z=5, parallax=0.0)
    pin(m, cam, lambda t: [3.8, 3.8, h_c(t)], tex("f", "=", "h", size=50, colors={0: C.obj}), T.high_c + 0.2, T.first_t + 0.6, off=(0.3, 0.35))
    pin(m, cam, lambda t: [0.79, -0.6, h_c(t)], backed(lab("lower the height", 30, C.text), 0.1, 0.85), T.lower, T.first_t - 0.3, off=(0.0, -0.4))
    pin(m, cam, [*BEST, BEST_H], backed(lab("first touch", 34, C.you), 0.1, 0.85), T.first_t + 0.3, T.insight, off=(0.0, 0.6))
    pin(m, cam, [*BEST, BEST_H], backed(lab("the highest you can reach", 28, C.text), 0.1, 0.85), T.that_touch + 0.4, T.insight, off=(0.0, -0.6))
    pin(m, cam, [TRAIL_A, 0.0, HC], tex("g", "=", "c", size=54, colors={0: C.con, 2: C.con}), T.itself + 1.0, T.families + 1.0, off=(0.7, 0.2))
    pin(m, cam, [0, -TRAIL_B * 1.22, HC * 1.22**2], lab("level curves of g", 30, C.con), T.level_g + 0.4, T.families + 1.0, off=(0.0, -0.5))
    h = s.manim(z=20, parallax=0.0)
    headline(h, lab("the trail is a contour too", 34, C.con), T.itself - 0.2, T.level_g + 2.4)
    two = VGroup(tex("f", size=54, color=C.obj), lab("contours", 30, C.obj), lab("and", 30, C.text), tex("g", size=54, color=C.con), lab("contours", 30, C.con)).arrange(RIGHT, buff=0.22)
    headline(h, two, T.families + 0.8, T.cut_ch3 - 0.3)
    pin(m, cam, [*BEST, 0.0], lab("they kiss", 34, C.you), T.kiss + 0.3, T.cut_ch3 - 0.05, off=(1.6, 0.35))
    curtain(s, a=False, b=True)
