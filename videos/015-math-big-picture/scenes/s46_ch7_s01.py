"""ch7_s01 · Six turns later (Chapter 7 hook).

The map as Chapter 6 left it: back at 0°, all six nodes lit. Inside the hub the card 'How it connects' (small caps)
comes and goes; on 'Six turns' a violet ring of six ticks sweeps once round inside the hub and 6 × 60° = 0° writes:
the group of turns is back at the start. On 'never' every lit chord brightens once. As each link is named its chord
pulses and the hub names its two ends: statistics / calculus (Change–Uncertainty), cryptography / whole numbers
(Quantity–Structure), physics / symmetry (Structure–Space). On 'definitions' three new chords draw from Foundations
to Space, Change and Uncertainty.
"""
import math

from aion import *

from beats import T
from hud import progress
from kit import glow_layer, HUB_R, P3, PILLARS, caps, hue, map_state, sans, tex, the_circle

ALL = PILLARS
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"), ("space", "change"), ("quantity", "change"), ("change", "uncertainty"),
         ("space", "uncertainty"), ("quantity", "uncertainty"))
NEW = (("foundations", "space"), ("foundations", "change"), ("foundations", "uncertainty"))


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def edge_line(e, width=8.0):
    ln = map_state(0, edges=(e,))[0][1][0].copy()
    return ln.set_stroke(width=width)


@scene(T.ch7_s01, T.ch7_s02)
def ch7_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_six, t_nev, t_st = float(T.ch7_s01_six_turns), float(T.ch7_s01_never), float(T.ch7_s01_statistics)
    t_se, t_ph, t_df = float(T.ch7_s01_secure), float(T.ch7_s01_physics), float(T.ch7_s01_definitions)

    links, nodes = map_state(0, lit=ALL, edges=EDGES)
    hub = the_circle(fill_color=C.bg, fill_opacity=1.0)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)

    # the card, inside the hub
    card = VGroup(caps("How it", 38, C.text), caps("connects", 38, C.text)).arrange(DOWN, buff=0.14)
    top.play(FadeIn(card, scale=0.9), at=t0 + 0.15, dur=0.5)
    top.play(FadeOut(card, scale=0.9), at=t_six - 0.5, dur=0.4)

    # 'Six turns': six ticks, one sweep, back at the start
    rr = 1.16
    ticks = VGroup(*(Line(rr * 0.86 * P3(math.cos(a), math.sin(a)), rr * 1.14 * P3(math.cos(a), math.sin(a)),
                          stroke_color=C.structure, stroke_width=3) for a in [-math.pi / 2 - k * math.pi / 3
                                                                                for k in range(6)]))
    sweep = Arc(radius=rr, start_angle=-math.pi / 2, angle=-2 * math.pi + 1e-3, stroke_color=C.structure,
                stroke_width=4)
    top.play(LaggedStart(*(GrowFromCenter(t_) for t_ in ticks), lag_ratio=0.15), at=t_six - 0.2, dur=0.8)
    top.play(Create(sweep), at=t_six + 0.4, dur=1.8, ease="easy_ease")
    eq = tex(r"6 \times 60^\circ = 0^\circ", 24, C.structure)
    top.play(FadeIn(eq, shift=0.06 * UP), at=t_six + 2.3, dur=0.5)
    top.play(FadeOut(VGroup(ticks, sweep, eq)), at=t_nev - 1.2, dur=0.5)

    # 'never': every lit chord brightens once
    flash = VGroup(*(edge_line(e, 6.0) for e in EDGES))
    lnk.play(FadeIn(flash), at=t_nev - 0.1, dur=0.35)
    lnk.play(FadeOut(flash), at=t_nev + 0.5, dur=0.8)

    # each link named: the chord pulses, the hub names its two ends
    def pair(a, ca, b, cb, size=30):
        return VGroup(sans(a, size, ca), tex(r"\updownarrow", 30, C.muted), sans(b, size, cb)).arrange(DOWN, buff=0.1)

    named = ((t_st, ("change", "uncertainty"), pair("statistics", C.uncertainty, "calculus", C.change)),
             (t_se, ("quantity", "structure"), pair("cryptography", C.structure, "whole numbers", C.quantity, 28)),
             (t_ph, ("structure", "space"), pair("physics", C.space, "symmetry", C.structure)))
    ends = [t_se - 0.5, t_ph - 0.5, t_df - 1.2]
    for (tb, e, words), te in zip(named, ends):
        ln = edge_line(e)
        lnk.play(FadeIn(ln), at=tb - 0.1, dur=0.35)
        lnk.play(FadeOut(ln), at=tb + 1.2, dur=0.8)
        top.play(FadeIn(words, shift=0.06 * UP), at=tb - 0.05, dur=0.4)
        top.play(FadeOut(words), at=te, dur=0.35)

    # 'definitions': three new chords from Foundations
    under = sans("definitions", 32, C.foundations)
    top.play(FadeIn(under, shift=0.06 * UP), at=t_df - 0.4, dur=0.4)
    new_edges = map_state(0, edges=NEW)[0][1]
    lnk.play(LaggedStart(*(Create(e_) for e_ in new_edges), lag_ratio=0.3), at=t_df - 0.2, dur=1.1)
    top.play(FadeOut(under), at=t1 - 0.5, dur=0.4)
