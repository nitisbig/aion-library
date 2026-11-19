"""s13: lower a high contour until it first touches the trail. Then the trail reveals itself as one level curve of g."""
from aion import *

from beats import T
from classic import *


@scene(T.cut_swell, T.cut_ch3)
def s13_swell(s):
    stage(s, contours=False)
    progress(s, 2)
    s.manim(z=-15).add(contour_mobs(opacity=0.22))
    m = s.manim(z=2)
    h_ = hud(s)
    h = keys((T.high_c, 2.85), (T.lower, 2.85), (T.first_t, BEST_H))
    show = fade(T.high_c - 0.2, dur=0.5)
    live(m, lambda t: VGroup(*[poly([mp(q) for q in p[::2]], C.obj, 5, float(show(t))) for p in loops_at(float(h(t)))]), (T.high_c - 0.2, T.first_t + 0.1))
    inset(h_, (-5.2, 2.75), 3.1, 1.5, T.lower - 0.9)
    live(h_, lambda t: tex("f", "=", f"{float(h(t)):.2f}", size=56, colors={0: C.obj}).move_to([-5.2, 2.75, 0]), (T.lower - 0.8, T.first_t + 0.1))
    m.play(FadeIn(walker(mp(BEST)), scale=0.3), at=T.first_t, dur=0.5, ease="out_back")
    tag = backed(lab("first touch", 34, C.you)).move_to(mp(BEST) + [2.6, 0.2, 0])
    m.play(FadeIn(tag), at=T.that_touch, dur=0.5)
    m.play(FadeOut(tag), at=T.insight, dur=0.5)
    th = np.linspace(0, TAU, 160)
    fam = VGroup(*[poly([mp(TRAIL_A * k * np.cos(a), TRAIL_B * k * np.sin(a)) for a in th], C.con, 2.2, 0.8) for k in (0.42, 0.7, 1.12)])
    m.play(Indicate(trail_mob(8), color=C.con, scale_factor=1.0), at=T.itself, dur=1.2)
    m.play(LaggedStart(*[Create(c) for c in fam], lag_ratio=0.3), at=T.families, dur=1.5, ease=E)
    board(h_, [(tex("g", "=", "c", size=60, colors={0: C.con, 2: C.con}), T.level_g), (lab("two families", 30, C.text), T.families + 0.3)], "ur")
    curtain(s, a=False, b=False)
