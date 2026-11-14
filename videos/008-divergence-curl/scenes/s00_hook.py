"""Intro · the hook. A stream of dust over the hero field's streak texture. Two places: at the source a tight
cluster of grains spreads apart (the camera pushes in), at the counter-clockwise vortex a second cluster curls into
an arm. They get their names, del-dot F in orange and del-cross F in green, which unfold into the rows of partial
derivatives everyone memorizes. On "the picture never quite shows up" they go grey and dissolve; the stream flows on."""
from aion import *

from beats import T
from shots import advect_table, curl_eq, div_eq, hero, hero_eyes, lic, tex
from sims import RATE, dust_layer, hero_dust

A, V = hero_eyes()                               # the source and the ccw vortex (true stagnation points)
E = "easy_ease"


def cluster(c, r, n=140):
    """n grains packed evenly in a disc (sunflower spiral): neighbours, before the flow pulls them apart."""
    k = np.arange(n) + 0.5
    rr = r * np.sqrt(k / n)
    th = k * np.pi * (3 - np.sqrt(5))
    return np.stack([c[0] + rr * np.cos(th), c[1] + rr * np.sin(th)], 1)


@scene(T.start, T.cut_preview)
def s00_hook(s):
    s.solid(C.bg, z=-200)

    # ── the stream: streak texture + dust, fading up from black ──
    k_in = keys((s.start, 0.0), (T.dust - 0.4, 0.0), (T.dust + 2.2, 1.0, E), lead=0)
    k_dim = keys((s.start, 1.0), (T.spreads - 0.6, 1.0), (T.spreads + 0.4, 0.55, E), (T.names - 0.4, 0.55),
                 (T.names + 1.0, 1.0, E), (T.formula - 0.3, 1.0), (T.formula + 0.9, 0.35, E), (T.never, 0.35),
                 (T.never + 1.2, 0.6, E), lead=0)
    lic(s, opacity=lambda t: 0.32 * k_in(t) * k_dim(t), gain=3.2, cell=0.032)
    dust = hero_dust(T.start, T.cut_ch1)
    s.add(dust_layer(dust, opacity=lambda t: k_in(t) * k_dim(t)))

    m = s.manim(z=4)

    # ── two places: faint rings ──
    rings = VGroup(Circle(radius=1.05, color=C.muted, stroke_width=C.thin).move_to([*A, 0]),
                   Circle(radius=1.05, color=C.muted, stroke_width=C.thin).move_to([*V, 0]))
    for r in rings:
        r.set_stroke(opacity=0.7)
    m.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.35), at=T.two_places, dur=1.2, ease=E)

    # ── "Here, the dust spreads apart": push in on the source, a dye drop blooms ──
    s.camera.frame(T.spreads - 0.6, center=tuple(A), zoom=1.55, dur=1.8)
    rel_a = (T.spreads - 0.2, T.whirlpool)
    at_a = advect_table(hero, cluster(A, 0.28), rel_a[0], rel_a[1], scale=RATE)
    ka = keys((s.start, 0.0), (rel_a[0], 0.0), (rel_a[0] + 0.5, 1.0), (T.turn - 1.4, 1.0), (T.turn - 0.4, 0.0),
              lead=0)
    s.add(PointsLayer(at_a, color=C.dust, size=5.0, glow=0.0, z=3, opacity=ka))

    # ── "here, the dust starts to turn": pan to the vortex, a second drop swirls ──
    s.camera.frame(T.turn - 0.9, center=tuple(V), zoom=1.55, dur=2.0)
    rel_v = (T.turn - 0.1, T.divergence)
    at_v = advect_table(hero, cluster(V + [0.55, 0.0], 0.24), rel_v[0], rel_v[1], scale=RATE)
    kv = keys((s.start, 0.0), (rel_v[0], 0.0), (rel_v[0] + 0.5, 1.0), (T.names + 0.6, 1.0), (T.names + 1.6, 0.0),
              lead=0)
    s.add(PointsLayer(at_v, color=C.dust, size=5.0, glow=0.0, z=3, opacity=kv))

    # ── "Those two motions have names": pull back, name each place ──
    s.camera.frame(T.names - 0.2, center=(0.0, 0.0), zoom=1.0, dur=2.0)
    sym_d = tex(r"\nabla\cdot", r"\mathbf{F}", size=82, colors={0: C.div}).move_to([*(A + [0, 1.6]), 0])
    sym_c = tex(r"\nabla\times", r"\mathbf{F}", size=82, colors={0: C.curl}).move_to([*(V + [0, -1.75]), 0])
    m.play(FadeIn(sym_d, shift=0.2 * UP), rings[0].animate.set_stroke(C.div, opacity=0.9), at=T.divergence, dur=0.8)
    m.play(FadeIn(sym_c, shift=0.2 * UP), rings[1].animate.set_stroke(C.curl, opacity=0.9), at=T.curl, dur=0.8)

    # ── "a row of partial derivatives": the names unfold into the formulas ──
    eq_d = div_eq(size=66).move_to([0, 1.15, 0])
    eq_c = curl_eq(size=66, nabla=True).move_to([0, -1.15, 0])
    eq_c.align_to(eq_d, LEFT)
    m.play(FadeOut(rings), at=T.partials, dur=0.8)
    m.play(ReplacementTransform(sym_d[0], eq_d[0]), ReplacementTransform(sym_d[1], eq_d[1]),
           ReplacementTransform(sym_c[0], eq_c[0]), ReplacementTransform(sym_c[1], eq_c[1]),
           at=T.partials + 0.5, dur=1.3, ease=E)
    m.play(LaggedStart(*[FadeIn(eq_d[i], shift=0.15 * LEFT) for i in (2, 3, 4, 5)], lag_ratio=0.3),
           at=T.formula, dur=1.6)
    m.play(LaggedStart(*[FadeIn(eq_c[i], shift=0.15 * LEFT) for i in (2, 3, 4, 5)], lag_ratio=0.3),
           at=T.formula + 1.7, dur=1.6)

    # ── "the picture never quite shows up": grey, then gone ──
    m.play(eq_d.animate.set_color(C.muted), eq_c.animate.set_color(C.muted), at=T.exam + 1.2, dur=1.4)
    m.play(FadeOut(eq_d, shift=0.25 * DOWN), FadeOut(eq_c, shift=0.25 * DOWN), at=T.never + 0.6, dur=1.2)
