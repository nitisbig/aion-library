"""s07: Lagrange's boast, no figures in the book, and the picture that was hiding under his algebra."""
from aion import *

from beats import T
from cards import card, pop
from shots import BEST, E, backdrop, contour_mobs, curtain, lab, mp, sc, tex, trail_mob, walker, words


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
    pic = VGroup(contour_mobs(), trail_mob(), walker(mp(BEST))).move_to(ORIGIN)
    m.play(LaggedStart(*[Create(c) for c in pic[0]], lag_ratio=0.06), at=T.pity + 1.0, dur=2.2, ease=E)
    m.play(Create(pic[1]), at=T.beautiful - 0.4, dur=1.5, ease=E)
    m.play(FadeIn(pic[2], scale=0.4), at=T.beautiful + 1.2, dur=0.5, ease="out_back")
    curtain(s)
