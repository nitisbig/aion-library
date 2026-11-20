"""s12: walk the trail over the contours. Each crossing is a climb; the crossings spread out; at the top the trail only touches a contour."""
from aion import *

from beats import T
from ch1 import *

LV0 = 2.0
LOOP = walk_loop(LV0)
LC = LOOP.mean(axis=0)
STEPS = [BEST_H - 0.1 * k for k in range(1, 16)]
SS = np.linspace(LOW_S, BEST_S + 0.9, 3000)
HH = hill(*trail(SS))
CROSS = [(float(SS[i]), lv) for lv in STEPS for i in np.where(np.diff(np.sign(HH - lv)) != 0)[0] if SS[i] < BEST_S]
ALL = np.linspace(0, TAU, 360)


def higher_side():
    """+1 or -1: which way along the trail would climb if a contour crossed the trail at the top."""
    d = trail_tangent(BEST_S)
    d = d / np.linalg.norm(d)
    n = hill_grad(*BEST)
    c, sn = np.cos(0.6), np.sin(0.6)
    e = np.array([c * d[0] - sn * d[1], sn * d[0] + c * d[1]])
    mn = np.array([-e[1], e[0]])
    mn = mn if mn @ n > 0 else -mn
    return 1.0 if d @ mn > 0 else -1.0


SG = higher_side()
HIGH = np.array([*trail(BEST_S + SG * 0.42), 0.0])
HIGH[2] = hill(*HIGH[:2])


@scene(T.cut_walk, T.cut_swell)
def s12_walk(s):
    backdrop(s)
    w_s = keys((T.cross - 0.4, LOW_S), (T.spread, BEST_S - 0.72), (T.special + 0.6, BEST_S - 0.06, "linear"), (T.touches + 0.7, BEST_S + 0.22), (T.falls + 0.9, BEST_S + 0.72), (T.is_top - 0.1, BEST_S))
    wpos = lambda t: np.array(trail(float(w_s(t))))
    near = (-90, 89.5, 2.2, 0.0, -0.2, 400, LC[0], LC[1], LV0)
    whole = (-90, 89.5, 1.15, 0.0, -0.05, 400, 0, 0, 0)
    best = (-90, 89.5, 2.5, 0.0, -0.3, 400, BEST[0], BEST[1], BEST_H)
    chase = (-25, 48, 1.4, 0.0, -0.6, 26, 0, 0, 0)
    fw = lambda t: (win(t, T.cross - 1.2, T.special + 1.0, 1.4, 1.4), [*wpos(t), hill(*wpos(t))])
    cam = camera(
        (T.cut_walk, near),
        (T.walk + 1.8, whole),
        (T.cross - 0.6, whole),
        (T.cross + 1.0, chase),
        (T.gentler, (-50, 50, 1.4, 0.0, -0.6, 26, 0, 0, 0)),
        (T.special + 0.2, (-65, 52, 1.5, 0.0, -0.6, 26, 0, 0, 0)),
        (T.touches - 0.3, best),
        (T.if_cross + 4.0, best),
        (T.cut_swell, whole),
        follow=fw,
    )

    def frame(t):
        v = view().begin(cam(t))
        mountain(v)
        floor(v)
        wires(v, 1.0, 0.2)
        fade_lv = 1 - ramp(t, T.cut_walk, T.cut_walk + 0.7)
        if fade_lv > 0.01:
            level(v, LV0, C.you, 5.0, fade_lv)
        for lv in STEPS:
            level(v, lv, C.obj, 2.2, 0.75)
        curve(v, np.column_stack(trail(ALL)), C.con, 6.0, ramp(t, T.cut_walk, T.walk + 0.6))
        ka = ramp(t, T.touches - 0.2, T.touches + 0.6)
        if ka > 0.01:
            level(v, BEST_H, C.text, 5.5, ka)
        u = float(w_s(t))
        for s_i, lv in CROSS:
            if u >= s_i or t > T.falls:
                pulse = max(0.0, 1.0 - abs(u - s_i) / 0.08) if t < T.falls else 0.0
                p = lift(np.atleast_2d(trail(s_i)), 1.0, 0.05)[0]
                v.dot(p, C.obj, 0.06 + 0.06 * pulse, ring=C.bg)
        # the counterfactual: a contour that crossed here
        xa = win(t, T.if_cross + 0.1, T.cut_swell - 0.4, 0.5, 0.6)
        if xa > 0.01:
            d = trail_tangent(BEST_S)
            d = d / np.linalg.norm(d)
            n = hill_grad(*BEST)
            n = n / np.linalg.norm(n)
            c, sn = np.cos(0.6), np.sin(0.6)
            e = np.array([c * d[0] - sn * d[1], sn * d[0] + c * d[1]])
            z = BEST_H + 0.05
            L = 1.3 * ramp(t, T.if_cross + 0.1, T.if_cross + 0.8)
            v.line([[*(BEST - L * e), z], [*(BEST + L * e), z]], C.wrong, 5.0, xa)
            mn = np.array([-e[1], e[0]])
            mn = mn if mn @ n > 0 else -mn
            sg = 1.0 if d @ mn > 0 else -1.0
            ga = xa * ramp(t, T.if_cross + 1.4, T.if_cross + 2.0)
            if ga > 0.01:
                ss = BEST_S + sg * np.linspace(0.06, 0.38, 20)
                P = lift(np.column_stack(trail(ss)), 1.0, 0.08)
                v.line(P[:-1], C.wrong, 5.0, ga)
                v.arrow(P[-3], P[-1], C.wrong, width=5.0, tip=0.2, alpha=ga)
        bead(v, wpos(t), r=0.11)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_walk, T.cut_swell)]))
    m = s.manim(z=5, parallax=0.0)
    wp = lambda t: [*wpos(t), hill(*wpos(t))]
    pin(m, cam, wp, backed(lab("each crossing: you climb", 30, C.obj), 0.1, 0.85), T.cross + 1.2, T.keep + 0.4, off=(0.0, -0.65))
    pin(m, cam, wp, backed(lab("crossings spread out", 30, C.obj), 0.1, 0.85), T.spread + 0.2, T.special, off=(-2.4, 0.25))
    pin(m, cam, wp, backed(lab("gentler", 30, C.text), 0.1, 0.85), T.gentler + 0.1, T.special, off=(-2.4, -0.25))
    tp = [*BEST, BEST_H]
    pin(m, cam, tp, backed(lab("it only touches", 32, C.text), 0.1, 0.85), T.touches + 0.5, T.is_top, off=(1.9, 0.5))
    pin(m, cam, tp, backed(lab("the top", 36, C.you), 0.1, 0.85), T.is_top, T.if_cross, off=(1.5, 0.5))
    pin(m, cam, HIGH, backed(lab("higher", 32, C.wrong), 0.1, 0.85), T.if_cross + 1.8, T.cut_swell - 0.4, off=(0.75, 0.45))
    h = s.manim(z=20, parallax=0.0)
    headline(h, lab("if the trail crossed here, it would not be the top", 30, C.wrong), T.if_cross + 0.3, T.cut_swell - 0.4)
    curtain(s, a=False, b=False)
