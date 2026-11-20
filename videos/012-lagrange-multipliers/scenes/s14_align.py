"""s14: zoom into the kiss on the flat map. Both gradients stand on the same tangent line, so one is a multiple of the other: grad f = lambda grad g."""
from aion import *

from beats import T
from ch1 import *

LAM = CAST["trail_lambda"]
K = 0.62
ALL = np.linspace(0, TAU, 360)
D = trail_tangent(BEST_S) / np.linalg.norm(trail_tangent(BEST_S))
GF, GG = hill_grad(*BEST), trail_grad(*BEST)
NG = GG / np.linalg.norm(GG)


@scene(T.cut_ch3, T.cut_compass)
def s14_align(s):
    backdrop(s)
    whole = (-90, 89.5, 1.15, 0.0, -0.05, 400, 0, 0, 0)
    zoom = (-90, 89.5, 2.7, 0.6, -0.2, 400, BEST[0], BEST[1], 0)
    tilt = (-125, 52, 2.5, 0.6, -0.3, 30, BEST[0], BEST[1], 0)
    cam = camera(
        (T.cut_ch3, whole),
        (T.share + 1.6, zoom),
        (T.multiple, zoom),
        (T.grad_eq + 1.4, tilt),
        (T.longer, (-145, 48, 2.5, 0.6, -0.3, 30, BEST[0], BEST[1], 0)),
        (T.cut_compass, (-25, 48, 1.4, 0.0, -0.6, 26, 0, 0, 0)),
    )
    rise = lambda t: ramp(t, T.longer + 0.6, T.cut_compass - 0.1)
    k_lam = lambda t: 1.0 + (LAM - 1.0) * ramp(t, T.stretch + 0.3, T.longer + 0.9)

    def frame(t):
        v = view().begin(cam(t))
        k = rise(t)
        mountain(v, k, k)
        floor(v, k)
        if k < 0.99:
            for lv, paths in [(lv, ring(lv)) for lv in LEVELS]:
                for p in paths:
                    v.line(np.column_stack([p, np.full(len(p), lv * k + 0.01)]), C.obj, 2.0, 0.35 * (1 - k))
        level(v, BEST_H, C.text, 5.0, 1.0, z=None if k > 0.5 else BEST_H * k + 0.02)
        curve(v, np.column_stack(trail(ALL)), C.con, 6.0, 1.0, k=k, dz=0.03)
        z = BEST_H * k + 0.04
        b = np.array([*BEST, z])
        fa = 1 - ramp(t, T.longer + 0.6, T.longer + 1.4)
        ta = ramp(t, T.share + 1.6, T.share + 2.4) * fa
        if ta > 0.01:
            v.line([b - np.array([*D, 0]) * 1.6, b + np.array([*D, 0]) * 1.6], C.tang, 4.0, ta)
        ga = ramp(t, T.each, T.each + 0.6) * fa
        if ga > 0.01:
            v.arrow(b, b + np.array([*GF, 0]) * K, C.obj, width=6.0, tip=0.22, alpha=ga)
        ca = ramp(t, T.each + 1.0, T.each + 1.6) * fa
        if ca > 0.01:
            v.arrow(b, b + np.array([*GG, 0]) * K, C.con, width=5.0, tip=0.2, alpha=ca)
        ra = ramp(t, T.both, T.both + 0.5) * fa
        if ra > 0.01:
            r = 0.16
            for nn in (NG, -NG):
                v.line([b + np.array([*(D * r), 0]), b + np.array([*((D + nn) * r), 0]), b + np.array([*(nn * r), 0])], C.text, 2.4, ra)
        da = ramp(t, T.common, T.common + 0.7) * fa
        if da > 0.01:
            for j in range(-14, 14):
                if j % 2 == 0:
                    v.line([b + np.array([*(NG * 0.12 * j), 0]), b + np.array([*(NG * 0.12 * (j + 1)), 0])], C.text, 2.0, da)
        la = win(t, T.stretch + 0.2, T.longer + 1.3, 0.4, 0.5)
        kl = k_lam(t)
        if la > 0.01 and abs(kl) > 0.05:
            v.arrow(b + np.array([0, 0, 0.02]), b + np.array([*GG, 0.02]) * np.array([K * kl, K * kl, 1]), C.lam, width=3.0, tip=0.15, alpha=la)
        v.dot(b, C.you, 0.08, ring=C.bg)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_ch3, T.cut_compass)]))
    title(s, "Chapter 3  ·  the gradients align", T.cut_ch3 + 0.3, hold=3.0)
    m = s.manim(z=5, parallax=0.0)
    b0 = np.array([*BEST, 0.04])
    pin(m, cam, b0 + np.array([*D, 0]) * 1.6, backed(lab("shared tangent", 30, C.tang), 0.1, 0.85), T.share + 2.0, T.longer + 1.0, off=(0.0, 0.4))
    pin(m, cam, b0 + np.array([*GF, 0]) * K, tex(r"\nabla f", size=54, color=C.obj), T.each + 0.3, T.longer + 1.0, off=(-0.25, -0.4))
    pin(m, cam, b0 + np.array([*GG, 0]) * K, tex(r"\nabla g", size=54, color=C.con), T.each + 1.3, T.longer + 1.0, off=(0.35, 0.3))
    pin(m, cam, b0 - np.array([*NG, 0]) * 1.65, backed(lab("one common direction", 28, C.text), 0.1, 0.85), T.common + 0.5, T.multiple + 1.5, off=(0.0, -0.35))
    h = s.manim(z=20, parallax=0.0)
    eq = tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=96, colors={0: C.obj, 2: C.lam, 3: C.con}).move_to([0, 3.0, 0])
    plate = backed(eq, 0.16, 0.85)
    h.play(FadeIn(plate, shift=0.1 * DOWN), at=T.grad_eq - 0.1, dur=0.7, ease=E)
    h.play(Indicate(eq[2], color=C.lam, scale_factor=1.3), at=T.greek + 0.2, dur=0.9)
    name = backed(lab("the Lagrange multiplier", 32, C.lam), 0.1, 0.85).move_to([0, 1.95, 0])
    h.play(FadeIn(name, shift=0.06 * UP), at=T.greek + 0.4, dur=0.5, ease=E)
    h.play(FadeOut(name), at=T.stretch - 0.1, dur=0.4, ease=E, lead=0)
    fac = backed(lab("a stretch factor", 32, C.lam), 0.1, 0.85).move_to([0, 1.95, 0])
    h.play(FadeIn(fac, shift=0.06 * UP), at=T.stretch + 0.1, dur=0.5, ease=E)
    h.play(FadeOut(fac), at=T.longer + 0.6, dur=0.4, ease=E, lead=0)
    val = backed(tex(r"\lambda", r"\approx", f"{LAM:.2f}", size=56, colors={0: C.lam}), 0.1, 0.85).move_to([0, 1.95, 0])
    h.play(FadeIn(val, shift=0.06 * UP), at=T.longer + 0.7, dur=0.5, ease=E)
    h.play(FadeOut(VGroup(plate, val)), at=T.cut_compass - 0.6, dur=0.5, ease=E, lead=0)
    curtain(s, a=False, b=False)
