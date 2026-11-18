"""s26 meaning (outro): so what is the matrix exponential, really? Over the calm rotation flow: A is a velocity, a rule
for how every point moves right now; e^{tA} is where everything ends up once that motion has run. Then a visual index of
the facts (nothing new derived): the series computes it, the eigenvectors give its directions, the trace gives its
change in volume, and order matters."""
from aion import *

from beats import T
from shots import (E, J, arrow, backdrop, backed, disc_points, field_arrows, finish, flow_layers, lab, p3, tex)


@scene(T.cut_outro, T.cut_beyond)
def s26_meaning(s):
    backdrop(s)
    mf = s.manim(z=0)
    m = s.manim(z=4)

    # ── the calm rotation flow underneath ──
    field = field_arrows(J, spacing=0.9, opacity=0.3)
    mf.play(FadeIn(field), at=T.cut_outro + 0.3, dur=1.0)
    mf.play(FadeOut(field), at=T.cut_beyond - 0.5, dur=0.5)
    tau = Clock(rate=0.22, start=T.cut_outro + 0.3)
    al = keys((T.cut_outro + 0.3, 0.0), (T.cut_outro + 1.3, 0.35), (T.cut_beyond - 0.6, 0.35), (T.cut_beyond - 0.1, 0.0),
              lead=0)
    flow_layers(s, disc_points(700, 4.6, seed=23), J, tau, alpha=al, trail=8, size=2.2, z=1, start=T.cut_outro,
                end=T.cut_beyond)

    # ── A is the velocity; e^{tA} is the trip ──
    A = tex("A", size=110, color=C.gen).move_to([-2.4, 0.35, 0])
    eA = tex(r"e^{tA}", size=110, color=C.flow).move_to([2.4, 0.45, 0])
    eA[0][2].set_color(C.gen)
    mid = Arrow(p3((-1.3, 0.35)), p3((0.9, 0.35)), buff=0, color=C.muted, stroke_width=C.stroke, tip_length=0.22)
    v_ic = arrow((-3.0, -0.95), (-1.8, -0.95), C.gen, width=C.stroke + 1.5)
    v_t = lab("how it moves now", 26, C.gen).move_to([-2.4, -1.45, 0])
    path = ArcBetweenPoints(p3((1.7, -1.1)), p3((3.1, -0.8)), angle=-1.4, color=C.flow, stroke_width=C.stroke + 1)
    path.add_tip(tip_length=0.18, tip_width=0.18)
    t_t = lab("where it ends up", 26, C.flow).move_to([2.4, -1.45, 0])
    core = VGroup(A, eA, mid, v_ic, v_t, path, t_t)
    card = BackgroundRectangle(core, color=C.bg, fill_opacity=0.85, buff=0.3)
    m.play(FadeIn(card), FadeIn(A, scale=0.9), at=T.read_velocity + 0.2, dur=0.7)
    m.play(GrowArrow(v_ic), FadeIn(v_t), at=T.read_velocity + 1.2, dur=0.6)
    m.play(GrowArrow(mid), FadeIn(eA, shift=0.15 * RIGHT), at=T.trip_again + 0.2, dur=0.8, ease=E)
    m.play(Create(path), FadeIn(t_t), at=T.trip_again + 1.3, dur=0.7)

    # ── the visual index: four cards slide into a ring ──
    facts = [
        (T.series_o, (-4.55, 2.75), LEFT + UP, r"I + A + \tfrac{A^2}{2!} + \cdots", "the series", C.gen),
        (T.eig_o, (4.55, 2.75), RIGHT + UP, r"P\,e^{t\Lambda}P^{-1}", "eigen-directions", C.eigen),
        (T.trace_o, (-4.55, -2.85), LEFT + DOWN, r"\det e^{A} = e^{\operatorname{tr}A}", "change in volume", C.area),
        (T.order_o, (4.55, -2.85), RIGHT + DOWN, r"e^{A+B} \ne e^{A}e^{B}", "order matters", C.comm),
    ]
    cards = VGroup()
    for at, (x, y), d, f, w, col in facts:
        c = VGroup(tex(f, size=42, color=C.text), lab(w, 24, col)).arrange(DOWN, buff=0.18)
        fr = SurroundingRectangle(c, color=col, buff=0.2, stroke_width=C.thin + 0.6)
        g = VGroup(BackgroundRectangle(fr, color=C.bg, fill_opacity=0.92, buff=0.0), fr, c).move_to([x, y, 0])
        cards.add(g)
        m.play(FadeIn(g, shift=-0.4 * d), at=at + 0.2, dur=0.7, ease=E)
    m.play(FadeOut(VGroup(card, core, cards)), at=T.cut_beyond - 0.45, dur=0.45)
    finish(s)
