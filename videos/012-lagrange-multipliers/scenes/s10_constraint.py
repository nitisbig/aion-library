"""s10: the constraint. The trail is an equation, everything off it is forbidden, and freedom drops from two directions to one."""
from aion import *

from beats import T
from classic import *


def forbidden_rgba():
    W, H = 1920, 1080
    X, Y = np.meshgrid((np.arange(W) + 0.5) / 135 - 64 / 9, 4 - (np.arange(H) + 0.5) / 135)
    mx, my = (X - MAPC[0]) / U, (Y - MAPC[1]) / U
    keep = np.clip((np.abs(np.hypot(mx / TRAIL_A, my / TRAIL_B) - 1.0) - 0.05) / 0.015, 0, 1)
    stripe = np.mod((X + Y) * 3.0, 1.0) < 0.1
    col = np.where(stripe[..., None], rgb(C.wrong), rgb(C.bg))
    return (np.clip(np.dstack([col, keep * np.where(stripe, 0.9, 0.62)]), 0, 1) * 255).astype(np.uint8)


@scene(T.cut_constraint, T.cut_ch2)
def s10_constraint(s):
    stage(s, with_trail=False)
    s.add(ArrayLayer(forbidden_rgba(), height=8.0, z=-5, opacity=keys((T.forbid - 0.1, 0.0), (T.forbid + 0.8, 1.0), (T.look, 1.0), (T.look + 0.9, 0.0))))
    progress(s, 1)
    m = s.manim(z=1)
    m.play(Create(trail_mob()), at=T.add_trail, dur=1.9, ease=E)
    w_s = keys((T.on_path - 0.2, 2.2), (T.forbid, 3.6), default_ease=E)
    live(m, lambda t: walker(mp(*trail(float(w_s(t))))), (T.on_path - 0.2, T.forbid + 0.1))
    no = backed(lab("forbidden", 40, C.wrong)).move_to([-5.0, -1.5, 0])
    m.play(FadeIn(no), at=T.forbid + 0.1, dur=0.6, ease=E)
    m.play(FadeOut(no), at=T.look, dur=0.6, ease=E)
    s0 = 3.6
    c = mp(*trail(s0))
    tg = trail_tangent(s0)
    tg = tg / np.linalg.norm(tg)
    nr = np.array([-tg[1], tg[0]])
    dot = walker(c)
    four = [arrow(c, c + p3(d) * 1.1, C.text, tip=0.26) for d in (tg, -tg, nr, -nr)]
    m.play(FadeIn(dot), *[GrowArrow(a) for a in four], at=T.two_dir, dur=0.7, ease=E)
    m.play(FadeOut(four[2]), FadeOut(four[3]), four[0].animate.set_color(C.tang), four[1].animate.set_color(C.tang), at=T.one_dir, dur=0.8, ease=E)
    m.play(FadeOut(VGroup(four[0], four[1], dot)), at=T.formula - 0.3, dur=0.6, ease=E, lead=0)
    h = hud(s)
    board(h, [(tex("g", "(x,y)", "=", "c", size=60, colors={0: C.con, 3: C.con}), T.g_eq)])
    box = inset(h, (5.15, 1.75), 3.1, 2.5, T.two_dir - 0.35, out=T.formula - 0.3)
    two, one = tex("2", size=120, color=C.text).move_to([5.15, 2.05, 0]), tex("1", size=120, color=C.tang).move_to([5.15, 2.05, 0])
    what = lab("freedom", 30, C.text).move_to([5.15, 0.95, 0])
    h.play(FadeIn(two, shift=0.1 * UP), FadeIn(what), at=T.two_dir + 0.2, dur=0.6, ease=E)
    h.play(FadeOut(two, shift=0.12 * UP), FadeIn(one, shift=0.12 * UP), at=T.one_dir, dur=0.8, ease=E)
    h.play(FadeOut(VGroup(one, what)), at=T.formula - 0.3, dur=0.4, ease=E, lead=0)
    sub = tex(r"f(a\cos s,\ b\sin s)", size=44, color=C.text)
    bx = board(h, [(sub, T.formula + 0.3)], ([6.85, 3.32, 0], UR))
    ss = np.linspace(0, 1, 420)
    knot = poly([[5.1 + 1.45 * np.sin(3 * TAU * u + 0.5), -1.5 + 1.15 * np.sin(4 * TAU * u)] for u in ss], C.con, 5)
    h.play(Create(knot), at=T.tangled + 0.1, dur=2.0, ease=E)
    cross = Line(sub.get_corner(DL) + [-0.1, -0.05, 0], sub.get_corner(UR) + [0.1, 0.05, 0], color=C.wrong, stroke_width=5)
    h.play(Create(cross), at=T.tangled + 2.8, dur=0.5, ease=E)
    curtain(s, a=False, b=True)
