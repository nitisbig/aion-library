"""s15: carry the uphill arrow along the trail and split it. Its along-the-trail part is what is left to gain, and it dies at the best point."""
from aion import *

from beats import T
from classic import *

K = 1.05


def parts(s_):
    q = np.array(trail(s_))
    g = hill_grad(*q)
    d = trail_tangent(s_)
    d = d / np.linalg.norm(d)
    along = (g @ d) * d
    return q, g, along, g - along


@scene(T.cut_compass, T.cut_proof)
def s15_compass(s):
    stage(s)
    progress(s, 3)
    m = s.manim(z=2)
    h = hud(s)
    w = keys((T.carry, LOW_S + 0.75), (T.arrive + 0.5, BEST_S), default_ease="linear")
    split = fade(T.split + 0.4, dur=0.6)
    amax = max(np.linalg.norm(parts(u)[1]) for u in np.linspace(LOW_S + 0.75, BEST_S, 120))
    x0, L = 3.75, 2.8

    def bar(y, value, color):
        return Rectangle(width=max(L * value, 0.001), height=0.3, fill_color=color, fill_opacity=1, stroke_width=0).move_to([x0 + L * value / 2, y, 0])

    def arrows(t):
        q, g, along, across = parts(float(w(t)))
        c = mp(q)
        a = float(split(t))
        out = VGroup(arrow(c, c + p3(g) * K, C.obj, tip=0.28).set_opacity(1 - 0.72 * a))
        if a > 0.01:
            if np.linalg.norm(along) > 0.03:
                out.add(arrow(c, c + p3(along) * K, C.tang, tip=0.26).set_opacity(a))
            out.add(arrow(c, c + p3(across) * K, C.text, tip=0.26).set_opacity(a))
        return out.add(walker(c))
    live(m, arrows, (T.carry - 0.5, T.cut_proof))
    inset(h, (5.15, 0.0), 3.4, 3.9, T.split + 0.3)

    def bars(t):
        _, _, along, across = parts(float(w(t)))
        a = float(split(t))
        return VGroup(bar(0.95, float(np.linalg.norm(along)) / amax, C.tang).set_opacity(a), bar(-0.75, float(np.linalg.norm(across)) / amax, C.text).set_opacity(a))
    live(h, bars, (T.split + 0.4, T.cut_proof))
    ln, lx = lab("along", 30, C.tang).move_to([5.15, 1.45, 0]), lab("across", 30, C.text).move_to([5.15, -0.25, 0])
    frames = VGroup(*[Rectangle(width=L, height=0.3, stroke_color=C.frame, stroke_width=C.thin).move_to([x0 + L / 2, y, 0]) for y in (0.95, -0.75)])
    h.play(FadeIn(ln), FadeIn(lx), FadeIn(frames), at=T.split + 0.5, dur=0.6, ease=E)
    no = lab("off limits", 26, C.muted).move_to([5.15, -1.3, 0])
    h.play(FadeIn(no), at=T.across + 0.4, dur=0.5)
    go = lab("room to climb", 26, C.tang).move_to([5.15, 0.4, 0])
    h.play(FadeIn(go), at=T.better - 0.2, dur=0.5)
    h.play(FadeOut(go), at=T.arrive + 0.2, dur=0.4)
    zero = tex(r"\text{along}", "=", "0", size=40, colors={0: C.tang}).move_to([5.15, 0.4, 0])
    h.play(FadeIn(zero, scale=0.8), at=T.arrive + 0.8, dur=0.5, ease="out_back")
    curtain(s, a=True, b=False)
