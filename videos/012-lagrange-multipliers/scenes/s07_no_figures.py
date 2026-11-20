"""s07: Lagrange's boast, no figures in the book, and the picture that was hiding under his algebra."""
from aion import *

from beats import T
from cards import card, pop
from ch1 import bead, camera, contours, curve, floor, mountain, ramp, trail
from shots import view, BEST, E, backdrop, contour_mobs, curtain, lab, mp, sc, tex, trail_mob, walker, words


@scene(T.cut_nofig, T.cut_preview)
def s07_no_figures(s):
    backdrop(s)
    m = s.manim(z=0)
    page = Rectangle(width=5.0, height=7.0, stroke_color=C.frame, stroke_width=C.thin + 0.6).move_to([-3.6, 0, 0])
    head = sc("M\\'ecanique analytique", 34, C.ink).move_to([-3.6, 3.05, 0])
    rows = [r"\frac{d}{dt}\frac{\partial T}{\partial \dot q}-\frac{\partial T}{\partial q}+\frac{\partial V}{\partial q}=0",
            r"\delta V+\lambda\,\delta L+\mu\,\delta M=0", r"P\,dp+Q\,dq+R\,dr=0",
            r"L=0,\quad M=0,\quad N=0", r"\sum m\left(\frac{d^2x}{dt^2}\delta x+\frac{d^2y}{dt^2}\delta y\right)=0",
            r"T=\tfrac12\sum m\,(\dot x^2+\dot y^2+\dot z^2)"]
    alg = VGroup(*[tex(r, size=30, color=C.ink) for r in rows]).arrange(DOWN, buff=0.42).move_to([-3.6, -0.25, 0])
    m.play(FadeIn(page), FadeIn(head), at=T.confident, dur=0.7)
    m.play(LaggedStart(*[FadeIn(r, shift=0.08 * UP) for r in alg], lag_ratio=0.18), at=T.confident + 0.7, dur=2.2)
    quote = words(r"\textit{``No figures will be}\\ \textit{found in this book.''}", 54, C.text).move_to([3.5, 1.1, 0])
    m.play(FadeIn(quote, shift=0.1 * UP), at=T.nofig - 0.2, dur=0.7)
    empty = DashedVMobject(Rectangle(width=2.6, height=1.65, color=C.muted, stroke_width=3), num_dashes=26).move_to([2.2, -1.85, 0])
    cross = VGroup(Line([1.15, -2.45, 0], [3.25, -1.25, 0], color=C.wrong, stroke_width=4), Line([1.15, -1.25, 0], [3.25, -2.45, 0], color=C.wrong, stroke_width=4))
    face = card("lagrange", "Lagrange", "1788", h=1.75, tilt=1.5, pos=[5.35, -1.75, 0])
    pop(m, face, T.nofig + 1.0)
    m.play(Create(empty), Create(cross), at=T.not_one, dur=0.6, ease=E)
    gone = Group(page, head, alg, quote, face, empty, cross)
    m.play(FadeOut(gone, shift=0.1 * DOWN), at=T.pity + 0.2, dur=0.9)
    # the picture he left out: contours on a map, which rise into the mountain
    ALL = np.linspace(0, TAU, 360)
    top = (-90, 89.5, 0.95, 0.0, 0.0, 400, 0.0, 0.0, 0.0)
    cam = camera((T.pity, top), (T.beautiful - 0.6, top), (T.beautiful + 1.4, (-70, 36, 1.05, 0.1, -0.9, 26, 0, 0, 0)), (T.cut_preview, (-64, 33, 1.08, 0.1, -1.0, 26, 0, 0, 0)))
    rise = lambda t: ramp(t, T.beautiful - 0.6, T.beautiful + 1.2)

    def pic(t):
        v = view().begin(cam(t))
        k = rise(t)
        a = ramp(t, T.pity + 0.9, T.pity + 2.6)
        floor(v, k, 0.5 * a)
        mountain(v, k, min(1.0, 2.2 * k))
        contours(v, k, C.obj, a * (1 - k) + 0.01, 2.4)
        if k > 0.02:
            contours(v, k, None, 0.55 * k)
        ta = ramp(t, T.beautiful - 0.4, T.beautiful + 1.1)
        if ta > 0.01:
            n = max(2, int(len(ALL) * ta))
            curve(v, np.column_stack(trail(ALL[:n])), C.con, 6.0, 1.0, k)
        if t > float(T.beautiful) + 1.1:
            bead(v, BEST, k)
        return v.rgba()
    s.add(FramesLayer(pic, height=8.0, z=-5, during=[(T.pity, T.cut_preview)]))
    curtain(s)
