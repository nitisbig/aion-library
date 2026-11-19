"""s12: walk the trail. The trail crosses contours while it climbs, and at the top it stops crossing and only touches one."""
from aion import *

from beats import T
from classic import *


@scene(T.cut_walk, T.cut_swell)
def s12_walk(s):
    stage(s)
    progress(s, 2)
    m = s.manim(z=2)
    h_ = hud(s)
    w_s = keys((T.cross - 0.4, LOW_S), (T.spread, BEST_S - 0.72), (T.special + 0.6, BEST_S - 0.06, "linear"), (T.touches + 0.7, BEST_S + 0.22), (T.falls + 0.9, BEST_S + 0.72), (T.is_top - 0.1, BEST_S))
    x0, x1, y0, y1 = 3.75, 6.55, -1.45, 1.0
    S0, S1, H0, H1 = LOW_S, BEST_S + 0.85, 0.2, 2.2
    def gx(u): return x0 + (x1 - x0) * (u - S0) / (S1 - S0)
    def gy(h): return y0 + (y1 - y0) * (h - H0) / (H1 - H0)
    inset(h_, (5.15, -0.1), 3.4, 3.5, T.walk - 0.1)
    title = lab("height", 30, C.obj).move_to([5.15, 1.35, 0])
    axes = VGroup(Line([x0, y0, 0], [x1, y0, 0], color=C.axis, stroke_width=2.5), Line([x0, y0, 0], [x0, y1, 0], color=C.axis, stroke_width=2.5))
    lv = VGroup(*[DashedLine([x0, gy(L), 0], [x1, gy(L), 0], color=C.obj, stroke_width=1.5, stroke_opacity=0.5, dash_length=0.07) for L in LEVELS if H0 <= L <= H1])
    h_.play(FadeIn(axes), FadeIn(title), FadeIn(lv), at=T.walk + 0.6, dur=0.7, ease=E)
    ss = np.linspace(S0, S1, 420)
    hh = hill(*trail(ss))

    def graph(t):
        u = float(w_s(t))
        far = float(max(u, LOW_S)) if t < float(T.falls) else BEST_S + 0.72
        n = max(2, int(np.searchsorted(ss, far)))
        return VGroup(poly(np.column_stack([gx(ss[:n]), gy(hh[:n])]), C.obj, 4.5), Dot([gx(u), gy(float(hill(*trail(u)))), 0], radius=0.09, color=C.you))
    live(h_, graph, (T.walk + 0.7, T.cut_swell))
    live(m, lambda t: walker(mp(*trail(float(w_s(t))))), (T.cut_walk, T.cut_swell))
    kiss = VGroup(*[poly([mp(q) for q in p[::2]], C.text, 4.5) for p in contour_paths(float(BEST_H))])
    m.play(Create(kiss), at=T.touches, dur=0.9, ease=E)
    top = backed(lab("the top", 32, C.you)).move_to(mp(BEST) + [1.5, 0.45, 0])
    m.play(FadeIn(top, shift=0.08 * UP), at=T.is_top, dur=0.5)
    d = trail_tangent(BEST_S)
    d = d / np.linalg.norm(d)
    n = hill_grad(*BEST)
    n = n / np.linalg.norm(n)
    c = mp(BEST)
    bad = poly([c - p3(d * 0.6 + n * 0.9), c + p3(d * 0.6 + n * 0.9)], C.wrong, 5)
    up = arrow(c + p3(d * 0.3 + n * 0.45), c + p3(d * 0.3 + n * 1.5), C.wrong, tip=0.26)
    hi = backed(lab("higher", 30, C.wrong)).move_to(c + p3(d * 0.3 + n * 1.5) + [0.2, -1.0, 0])
    m.play(Create(bad), at=T.if_cross + 0.2, dur=0.5, ease=E)
    m.play(GrowArrow(up), FadeIn(hi), at=T.if_cross + 1.5, dur=0.5)
    m.play(FadeOut(VGroup(bad, up, hi)), at=T.cut_swell - 0.5, dur=0.4)
    curtain(s, a=False, b=False)
