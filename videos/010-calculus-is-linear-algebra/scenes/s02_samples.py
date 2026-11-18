"""Ch1: a function is a very long vector. The string from the intro becomes a sine wave; keep its height at 8 points
and stack them in a column (a vector in R^8); then 50 points, then 1000, where the samples blur back into the curve
and the column's bars merge into the curve's own shape, turned on its side."""
from aion import *

from beats import T
from shots import (chapter_header, COL_H, COL_X, GO1, GUX1, GUY1, SL, SO, backdrop, bar_column, col_brackets, comb, finish, fmt, plot,
                   pt, samples, tex)

CY = -0.2                                                    # the column's centre y


def cell_y(k, n):
    return CY + COL_H / 2 - COL_H * (k + 0.5) / n


def dim_label(n):
    return tex(r"\in", rf"\mathbb{{R}}^{{{n}}}", size=44, colors={1: C.fn}).next_to([COL_X + 0.6, CY, 0], RIGHT, buff=0.25)


@scene(T.cut_ch1, T.cut_linear)
def s02_samples(s):
    backdrop(s)
    m = s.manim(z=1)
    chapter_header(m, 1, T.cut_ch1)                     # chapter badge row + title (fills the cut)
    t0 = T.cut_ch1

    # ── the flat string becomes a sine wave ──
    flat = Line(pt(SO, 1, (-SL, 0)), pt(SO, 1, (SL, 0)), color=C.string, stroke_width=C.stroke)
    pins = VGroup(*[Dot(pt(SO, 1, (sx * SL, 0)), radius=0.07, color=C.string) for sx in (-1, 1)])
    m.add(flat, pins, at=t0)
    axis = Line(pt(GO1, 1, (-0.25, 0)), pt(GO1, 1, (GUX1 * 2 * np.pi + 0.3, 0)), color=C.axis, stroke_width=C.thin)
    curve = plot(np.sin, 0, 2 * np.pi, GO1, GUX1, GUY1, C.fn, n=200)
    m.play(FadeOut(pins), FadeIn(axis), Transform(flat, curve), at=T.curve, dur=1.4, ease="easy_ease")
    m.remove(flat, at=T.curve + 1.5)
    m.add(curve, at=T.curve + 1.5)

    # ── keep only its height at eight points ──
    x8 = samples(8)
    y8 = np.sin(x8)
    sticks8 = VGroup(*[Line(pt(GO1, 1, (GUX1 * x, 0)), pt(GO1, 1, (GUX1 * x, GUY1 * y)), color=C.fn,
                            stroke_width=C.thin) for x, y in zip(x8, y8)])
    dots8 = VGroup(*[Dot(pt(GO1, 1, (GUX1 * x, GUY1 * y)), radius=0.075, color=C.fn) for x, y in zip(x8, y8)])
    m.play(LaggedStart(*[AnimationGroup(Create(sk), FadeIn(d, scale=0.5)) for sk, d in zip(sticks8, dots8)],
                       lag_ratio=0.15), at=T.eight, dur=1.4)
    m.play(curve.animate.set_stroke(opacity=0.15), at=T.eight + 1.4, dur=0.7)

    # ── stack them in a column ──
    cells = VGroup(*[tex(fmt(round(y, 2)), size=30, color=C.fn).move_to([COL_X, cell_y(k, 8), 0])
                     for k, y in enumerate(y8)])
    br = col_brackets(COL_X, CY, width=1.35)
    m.play(FadeIn(br), at=T.stack - 0.1, dur=0.5)
    m.play(LaggedStart(*[TransformFromCopy(d, c) for d, c in zip(dots8, cells)], lag_ratio=0.12),
           at=T.stack + 0.1, dur=1.6)
    r8 = dim_label(8)
    m.play(FadeIn(r8, shift=0.1 * LEFT), at=T.eight_dims + 0.6, dur=0.6)

    # ── fifty points ──
    x50, y50 = samples(50), np.sin(samples(50))
    sk50 = comb(x50, y50, GO1, GUX1, GUY1, C.fn, width=C.thin * 0.9)
    dots50 = VGroup(*[Dot(pt(GO1, 1, (GUX1 * x, GUY1 * y)), radius=0.04, color=C.fn) for x, y in zip(x50, y50)])
    bars50 = bar_column(y50, COL_X, CY, width=2.2)
    r50 = dim_label(50)
    t5 = T.fifty
    m.play(FadeOut(VGroup(sticks8, dots8)), FadeIn(sk50), FadeIn(dots50), at=t5 + 0.2, dur=0.9)
    m.play(FadeOut(cells), FadeIn(bars50), ReplacementTransform(r8, r50), at=t5 + 0.5, dur=0.9)

    # ── a thousand: the dots blur back into a curve ──
    x1k, y1k = samples(1000), np.sin(samples(1000))
    sk1k = comb(x1k, y1k, GO1, GUX1, GUY1, C.fn, width=0.6, opacity=0.55)
    bars1k = bar_column(y1k, COL_X, CY, width=0.6)
    r1k = dim_label(1000)
    t1 = T.thousand
    m.play(FadeOut(VGroup(sk50, dots50)), FadeIn(sk1k), at=t1 + 0.1, dur=0.9)
    m.play(FadeOut(bars50), FadeIn(bars1k), ReplacementTransform(r50, r1k), at=t1 + 0.4, dur=0.9)
    m.play(FadeOut(sk1k), curve.animate.set_stroke(opacity=1.0), at=T.blur + 0.3, dur=1.0)
    m.play(Indicate(VGroup(br, bars1k), color=C.fn, scale_factor=1.04), at=T.computer_stores + 1.4, dur=1.0)
    finish(s)
