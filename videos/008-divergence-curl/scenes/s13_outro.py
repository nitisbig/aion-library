"""Outro · back to the stream. The rail steps away and the opening shot returns: streak texture and dust over the
hero field. The divergence map paints in under it and the first of the opening's two places lands on the warm
spot; the curl map crossfades in and the second lands on the green swirl. The two badges gather into the lesson:
del-dot F with its drop of dye, del-cross F with its paddle wheel, and, added up, only the boundary integrals are
left. The grey formulas from the hook return and take their colors, the dye and the wheel beside them. Last, the
next video: the divergence of a gradient, the Laplacian, and a fade to black."""
from aion import *

from beats import T
from shots import (BADGES, badge, curl_eq, dim, div_eq, dye_poly, hero_curl, hero_div, hero_eyes, lic, oiint,
                   paddle, rail, rail_dust, sample_grid, spin_glyph, tex)
from sims import dust_layer, hero_dust

A, V = hero_eyes()
E = "easy_ease"
FULL = (14.4, 8.2)


def dye_icon(c, r=0.42):
    th = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    d = dye_poly(np.stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)], 1), C.div, opacity=0.15)
    return d.set_stroke(width=C.stroke)


def wheel_icon(c, angle=np.pi / 4, r=0.42):
    c = np.asarray(c, float)
    return VGroup(paddle(c, angle, radius=r, color=C.dust, width=3), spin_glyph(c, r * 1.5, +1, C.curl))


@scene(T.cut_outro, T.end)
def s13_outro(s):
    s.solid(C.bg, z=-200)

    # ── the rail steps away; the stream from the opening returns ──
    k_rail = keys((s.start, 1.0), (T.back - 0.6, 1.0), (T.back + 0.8, 0.0, E), lead=0)
    mr = s.manim(z=6, opacity=k_rail)
    rail(mr, s.start)
    rail_dust(s, s.start, opacity=k_rail)
    k_s = keys((s.start, 0.0), (T.back - 0.6, 0.0), (T.back + 1.6, 1.0, E), (T.div_asks - 0.3, 1.0),
               (T.div_asks + 1.0, 0.22, E), (T.next_ - 0.5, 0.22), (T.next_ + 0.8, 0.18, E), (T.end - 3.2, 0.18),
               (T.end - 0.8, 0.0, E), lead=0)
    lic(s, opacity=lambda t: 0.32 * k_s(t), gain=3.2, cell=0.032)
    dust = hero_dust(s.start, T.end)
    s.add(dust_layer(dust, opacity=k_s))

    # ── the two maps ──
    k_div = keys((s.start, 0.0), (T.div_map - 0.2, 0.0), (T.div_map + 1.4, 0.8, E), (T.here_curl - 0.3, 0.8),
                 (T.here_curl + 0.9, 0.0, E), lead=0)
    k_curl = keys((s.start, 0.0), (T.here_curl - 0.3, 0.0), (T.here_curl + 0.9, 0.8, E), (T.div_asks - 0.4, 0.8),
                  (T.div_asks + 0.8, 0.0, E), lead=0)
    s.add(FieldLayer(lambda t: sample_grid(hero_div, (0, 0), FULL), cmap="diverging", vmin=-2.2, vmax=2.2,
                     extent=FULL, colors=(C.sink, C.bg, C.div), animated=False, z=-20, opacity=k_div))
    s.add(FieldLayer(lambda t: sample_grid(hero_curl, (0, 0), FULL), cmap="diverging", vmin=-2.2, vmax=2.2,
                     extent=FULL, colors=(C.cw, C.bg, C.curl), animated=False, z=-20, opacity=k_curl))

    m = s.manim(z=4)
    # the badges stay put while the rail leaves; two of them become the lesson
    bF, bD, bC = (badge(i, f) for i, f in enumerate(BADGES[:3]))
    for fr in (bD[0], bC[0]):
        fr.set_fill(opacity=0.0)                # hollow, so a fading frame never covers its symbol
    for mob in (bF, bD[0], bC[0], bD[1], bC[1]):
        m.add(mob, at=s.start)
    m.play(FadeOut(bF), FadeOut(bD[0]), FadeOut(bC[0]), at=T.back - 0.2, dur=0.8)

    # ── the opening's two places, now readable ──
    ring_a = Circle(radius=1.05, color=C.div, stroke_width=C.stroke).move_to([*A, 0])
    ring_v = Circle(radius=1.05, color=C.curl, stroke_width=C.stroke).move_to([*V, 0])
    m.play(Create(ring_a), at=T.warm_spot - 0.3, dur=1.0, ease=E)
    m.play(Create(ring_v), at=T.green_swirl - 0.3, dur=1.0, ease=E)
    m.play(FadeOut(ring_a), FadeOut(ring_v), at=T.div_asks - 0.4, dur=0.7)

    # ── the lesson: two questions, and what adding them up leaves ──
    y1, y2 = 1.75, -0.45
    dl = tex(r"\nabla\cdot", r"\mathbf{F}", size=80, colors={0: C.div}).move_to([-3.4, y1, 0])
    cl = tex(r"\nabla\times", r"\mathbf{F}", size=80, colors={0: C.curl}).move_to([-3.4, y2, 0])
    m.play(ReplacementTransform(bD[1], dl), at=T.div_asks - 0.1, dur=1.1, ease=E)
    dye = dye_icon((-1.0, y1))
    m.play(FadeIn(dye, scale=0.4), at=T.div_asks + 1.1, dur=0.7, ease="out_back")
    dye_big = dye_icon((-1.0, y1), r=0.62)
    m.play(Transform(dye, dye_big), at=T.div_asks + 2.0, dur=1.6, ease=E)      # it swells: stuff leaving
    m.play(ReplacementTransform(bC[1], cl), at=T.curl_asks - 0.1, dur=1.1, ease=E)
    wc = np.array([-1.0, y2])
    t_wh = (T.curl_asks + 1.0, T.memorized - 0.3)

    def spinning(t):
        k = min(1.0, max(0.0, (t - t_wh[0]) / 0.6)) * (1.0 - min(1.0, max(0.0, (t - t_wh[1]) / 0.6)))
        g = wheel_icon(wc, np.pi / 4 + 0.9 * (t - t_wh[0]))
        return dim(g, k)
    m.redraw(spinning, during=(t_wh[0], t_wh[1] + 0.65))

    arr1 = Arrow([0.0, y1, 0], [1.3, y1, 0], buff=0, color=C.muted, stroke_width=C.stroke, tip_length=0.2)
    arr2 = Arrow([0.0, y2, 0], [1.3, y2, 0], buff=0, color=C.muted, stroke_width=C.stroke, tip_length=0.2)
    sd = oiint(r"\mathbf{F}\cdot\mathbf{n}\,dS", size=62, color=C.boundary, rest_color=C.text)
    sd.move_to([3.4, y1, 0])
    sc = tex(r"\oint", r"\mathbf{F}\cdot d\mathbf{r}", size=62, colors={0: C.boundary}).move_to([3.4, y2, 0])
    m.play(GrowArrow(arr1), GrowArrow(arr2), at=T.either + 0.2, dur=0.7)
    m.play(FadeIn(sd, shift=0.15 * LEFT), FadeIn(sc, shift=0.15 * LEFT), at=T.only_bound - 0.1, dur=0.9)
    lesson = VGroup(dl, cl, dye, arr1, arr2, sd, sc)
    m.play(FadeOut(lesson), at=T.memorized - 0.3, dur=0.7)

    # ── the grey formulas from the hook come back, and take their colors ──
    eq_d = div_eq(size=66).move_to([-0.9, 1.6, 0])
    eq_c = curl_eq(size=66, nabla=True).move_to([-0.9, -0.5, 0])
    eq_c.align_to(eq_d, LEFT)
    gd, gc = eq_d.copy().set_color(C.muted), eq_c.copy().set_color(C.muted)
    m.play(FadeIn(gd, shift=0.15 * DOWN), FadeIn(gc, shift=0.15 * DOWN), at=T.memorized + 0.4, dur=0.9)
    m.play(ReplacementTransform(gd, eq_d), ReplacementTransform(gc, eq_c), at=T.symbols - 2.2, dur=1.6, ease=E)
    d2 = dye_icon((eq_d.get_right()[0] + 1.1, 1.6), r=0.5)
    w2 = wheel_icon((eq_c.get_right()[0] + 1.2, -0.5), r=0.45)
    m.play(FadeIn(d2, scale=0.4), at=T.symbols - 0.6, dur=0.6, ease="out_back")
    m.play(FadeIn(w2, scale=0.4), at=T.symbols - 0.1, dur=0.6, ease="out_back")
    m.play(FadeOut(VGroup(eq_d, eq_c, d2, w2)), at=T.next_ - 0.4, dur=0.7)

    # ── next time: the divergence of a gradient ──
    lap = tex(r"\nabla\cdot", r"\nabla", "f", "=", r"\nabla^2", "f", size=86, colors={0: C.div})
    lap.move_to([0, 0.1, 0])
    m.play(FadeIn(lap[0:3], shift=0.15 * RIGHT), at=T.next_ + 1.2, dur=0.9)
    m.play(FadeIn(lap[3:], shift=0.15 * LEFT), at=T.laplacian, dur=0.9)
    m.play(FadeOut(lap), at=T.end - 2.4, dur=1.6)
