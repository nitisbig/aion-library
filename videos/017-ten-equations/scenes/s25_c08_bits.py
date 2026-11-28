"""c08_s01 · Bits and noise (hook). Storyboard: plan/scene_plan.md § c08_s01. Layout L1.

Opens on c07_s03's last frame (the noisy bit train on its cable), which gives way to the chapter card. 'Shannon':
name tag. 'bit': a coin flips between 1 and 0. 'song': a note, a photograph and a page of text, each dissolving into
rows of bits (seeded). 'wire': the bits become a clean square wave on a scope (ch8.BITS above it). 'noise': seeded,
band-limited Gaussian noise adds live and the trace frays; the receiver samples each slot against the threshold,
and the two bits it reads wrongly are marked (ch8.decisions, computed from the trace).
"""
import math

import numpy as np
from aion import *

import ch8
from beats import T
from kit import P3, add_rail, chapter_card, glow, glimpse, polyline, sans, smooth01, tex, tint

ICON_X, ICON_Y = (-4.0, 0.0, 4.0), 0.75
SENT_Y, READ_Y = 2.45, -2.3


def _carry(s, out):
    t_end = float(s.start) - 0.01
    op = fade(t_end - 5, dur=0.1, out=out, out_dur=0.6)
    glow(s, C.shannon, z=8, k=0.3, parallax=0.0, opacity=op).add(ch8.cable_wave(t_end))
    line, emit = ch8.cable_static()
    s.manim(z=7, parallax=0.0, opacity=op).add(line, ch8.cable_bits(t_end),
                                               sans("noise", 24, C.noise).move_to(P3(3.6, ch8.CABLE_Y - ch8.AMP - 0.5)))
    glow(s, C.descent, z=9, k=0.8, parallax=0.0, opacity=op).add(emit)


def note():
    head = lambda x, y: Ellipse(width=0.42, height=0.3, fill_opacity=1, stroke_width=0).rotate(0.4).move_to([x, y, 0])
    g = VGroup(head(-0.35, -0.55), head(0.45, -0.4),
               Line([-0.16, -0.5, 0], [-0.16, 0.6, 0], stroke_width=3.2),
               Line([0.64, -0.35, 0], [0.64, 0.75, 0], stroke_width=3.2),
               Polygon([-0.16, 0.6, 0], [0.64, 0.75, 0], [0.64, 0.55, 0], [-0.16, 0.4, 0], fill_opacity=1,
                       stroke_width=0))
    return g.set_color(C.light)


def photo():
    fr = Rectangle(width=1.5, height=1.1, stroke_width=2.4)
    hills = Polygon([-0.75, -0.55, 0], [-0.25, 0.05, 0], [0.05, -0.2, 0], [0.4, 0.2, 0], [0.75, -0.2, 0],
                    [0.75, -0.55, 0], stroke_width=2.0)
    sun = Circle(radius=0.13, stroke_width=2.0).move_to([-0.35, 0.28, 0])
    return VGroup(fr, hills, sun).set_stroke(color=C.light)


def page():
    pg = Polygon([-0.55, 0.75, 0], [0.3, 0.75, 0], [0.55, 0.5, 0], [0.55, -0.75, 0], [-0.55, -0.75, 0],
                 stroke_width=2.4)
    lines = VGroup(*[Line([-0.38, y, 0], [0.38 - (0.25 if k % 3 == 2 else 0), y, 0], stroke_width=1.6)
                     for k, y in enumerate(np.linspace(0.42, -0.5, 6))])
    return VGroup(pg, lines).set_stroke(color=C.light)


def bit_block(seed, rows=5, cols=8):
    rng = np.random.default_rng(seed)
    b = rng.integers(0, 2, (rows, cols))
    return VGroup(*[VGroup(*[sans(str(v), 22, C.shannon) for v in r]).arrange(RIGHT, buff=0.12) for r in b]) \
        .arrange(DOWN, buff=0.1)


@scene(T.c08_s01, T.c08_s02)
def s25_c08_bits(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_sh, t_bi, t_so, t_wi, t_no = (T.c08_s01_shannon, T.c08_s01_bit, T.c08_s01_song, T.c08_s01_wire,
                                    T.c08_s01_noise)
    _carry(s, t0 + 0.25)
    chapter_card(s, 8, at=t0 + 0.6, out=t_sh + 0.5)
    add_rail(s, 8, opacity=fade(t0 + 0.4, dur=0.8))
    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "shannon", t_sh + 0.7, C.shannon)

    # the bit: a coin that flips between 1 and 0
    c_op = fade(t_bi - 0.25, dur=0.5, out=t_so - 0.3, out_dur=0.5)
    FLIP = 0.9

    def flip(t):
        """(opacity, horizontal squash, face) of the coin at time t."""
        u = max(t - float(t_bi) - 0.3, 0.0) / FLIP
        k, f = int(u), u - int(u)
        sx = abs(math.cos(math.pi * f / 0.35)) if f < 0.35 else 1.0
        face = "1" if (k + (1 if f >= 0.175 else 0)) % 2 == 0 else "0"
        return float(c_op(t)), max(sx, 0.04), face

    def ring(t):
        a, sx, _ = flip(t)
        if a < 0.01:
            return VGroup()
        return Circle(radius=0.95, stroke_color=C.shannon, stroke_width=4, stroke_opacity=a, fill_opacity=0) \
            .move_to(P3(0, 0.45)).stretch(sx, 0)

    def face(t):                                                       # the digit: text, so no glow
        a, sx, f = flip(t)
        if a < 0.01:
            return VGroup()
        return tex(f, 110, C.text).move_to(P3(0, 0.45)).stretch(sx, 0).set_fill(opacity=a)
    glow(s, C.shannon, z=5, k=0.6, parallax=0.0).redraw(ring, during=(t_bi - 0.4, t_so + 0.4))
    s.manim(z=6, parallax=0.0).redraw(face, during=(t_bi - 0.4, t_so + 0.4))
    lab = VGroup(sans("bit", 34, C.shannon), sans("yes or no", 22, C.muted)).arrange(DOWN, buff=0.14) \
        .move_to(P3(0, -1.25))
    m = s.manim(z=6)
    m.play(FadeIn(lab, shift=0.05 * UP), at=t_bi + 0.1, dur=0.5)
    m.play(FadeOut(lab), at=t_so - 0.3, dur=0.5)

    # a song, a photograph, a page of text: all of them bits
    icons = [note(), photo(), page()]
    blocks = [bit_block(1948 + k) for k in range(3)]
    for k, (ic, bl, x) in enumerate(zip(icons, blocks, ICON_X)):
        ic.move_to(P3(x, ICON_Y))
        bl.move_to(P3(x, ICON_Y))
        m.play(FadeIn(ic, scale=0.9), at=t_so - 0.1 + 0.55 * k, dur=0.5)
        m.play(FadeOut(ic, scale=0.85), at=t_so + 2.6 + 0.25 * k, dur=0.6)
        m.play(FadeIn(bl, lag_ratio=0.02), at=t_so + 2.7 + 0.25 * k, dur=0.9)
        m.play(FadeOut(bl), at=t_wi - 0.5, dur=0.5)

    # the wire: the bits become a square wave on a scope
    w_op = fade(t_wi - 0.2, dur=0.5)
    sc = s.manim(z=3, opacity=w_op)
    grid = VGroup(*[Line(P3(x, -1.9), P3(x, 2.05), stroke_color=tint(C.muted, 0.22), stroke_width=1.0)
                    for x in np.linspace(ch8.SX0, ch8.SX1, len(ch8.BITS) + 1)],
                  *[Line(P3(ch8.SX0, y), P3(ch8.SX1, y), stroke_color=tint(C.muted, 0.22), stroke_width=1.0)
                    for y in (ch8.SY - ch8.SA, ch8.SY + ch8.SA)])
    sc.add(grid)
    sent = VGroup(*[sans(b, 24, C.muted).move_to(P3(ch8.SX0 + (j + 0.5) * ch8.slot_w(), SENT_Y))
                    for j, b in enumerate(ch8.BITS)])
    m.play(FadeIn(sent, lag_ratio=0.05), at=t_wi - 0.1, dur=1.0)
    t_draw = float(t_wi) - 0.05
    nz = lambda t: float(smooth01((t - float(t_no) + 0.1) / 0.9))

    def wave(t):
        front = ch8.SX0 + (t - t_draw) * 8.5
        if front <= ch8.SX0 + 0.02:
            return VGroup()
        x, y = ch8.trace(nz(t))
        k = x <= front
        return polyline(list(zip(x[k], y[k])), C.shannon, 3.0, float(w_op(t)))
    glow(s, C.shannon, z=5, k=0.35, parallax=0.0).redraw(wave, during=(t_wi - 0.3, s.end))

    # noise, and the receiver's reading
    hud.play(FadeIn(sans("noise", 26, C.noise).move_to(P3(ch8.SX1 - 0.5, -1.55)), shift=0.05 * UP), at=t_no, dur=0.5)
    thr = DashedLine(P3(ch8.SX0, ch8.SY), P3(ch8.SX1, ch8.SY), dash_length=0.12, stroke_color=C.muted,
                     stroke_width=1.6)
    m.play(Create(thr), at=t_no + 0.55, dur=0.5)
    read = VGroup()
    for xc, d, wrong in ch8.decisions():
        read.add(sans(str(d), 24, C.bad if wrong else C.text).move_to(P3(xc, READ_Y)))
    m.play(FadeIn(read, lag_ratio=0.04), at=t_no + 0.75, dur=0.7)
    marks = VGroup(*[Circle(radius=0.24, stroke_color=C.bad, stroke_width=2.5).move_to(P3(xc, READ_Y))
                     for xc, d, wrong in ch8.decisions() if wrong])
    m.play(Create(marks), at=t_no + 1.25, dur=0.4)
