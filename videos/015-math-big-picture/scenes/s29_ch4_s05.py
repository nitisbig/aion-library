"""ch4_s05 · Coffee mug, donut (sighting).

On 'coffee mug' a shaded mug (raymarched, shaders/solid.frag) fades in, turning slowly until its handle faces us. On
'Squash' the cup sinks into its handle while the handle grows into a ring: a donut with one hole, which then turns a
little to show its depth. On 'Both' it slides right, a mug comes back on the left, and χ = 0 lands under each. On
'same shape' an equals sign joins them. Then a long strand of DNA draws across the frame; on 'tangle' it ties itself
into a knot (over and under crossings drawn with gaps), and on 'untangle' it slips free again.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, caps, lin, sans, tex, window

MC, MS = P3(0.0, 0.35), 1.5                    # the mug: centre and world units per object unit
TILT = -1.25
SLIDE = 3.0
RING_R, RING_r = 0.62, 0.26


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ the strand
N = 640
S_ = np.linspace(0.0, 1.0, N)
A, B = 0.3, 0.7                               # the part of the strand that ties into the knot


def trefoil(t):
    return np.stack([np.sin(t) + 2 * np.sin(2 * t), np.cos(t) - 2 * np.cos(2 * t), -np.sin(3 * t)], -1)


def strand_free(phase=0.0):
    x = -5.6 + 11.2 * S_
    y = -0.35 + 0.28 * np.sin(4 * math.pi * S_ + phase)
    return np.stack([x, y, np.zeros_like(x)], -1)


def strand_knot():
    out = np.zeros((N, 3))
    c, k = np.array([0.0, 0.2, 0.0]), 0.72
    t0, t1 = 2 * math.pi - 0.15, 0.15
    mid = (S_ >= A) & (S_ <= B)
    t = t0 + (t1 - t0) * (S_[mid] - A) / (B - A)
    out[mid] = c + k * trefoil(t)
    p0, p1 = c + k * trefoil(np.array([t0]))[0], c + k * trefoil(np.array([t1]))[0]
    L, R = np.array([-5.6, -0.35, 0.0]), np.array([5.6, -0.35, 0.0])
    lo, hi = S_ < A, S_ > B
    out[lo] = L + np.outer(S_[lo] / A, p0 - L)
    out[hi] = p1 + np.outer((S_[hi] - B) / (1 - B), R - p1)
    out[lo, 2] = p0[2] * S_[lo] / A                                     # the tails ease into the knot's depth
    out[hi, 2] = p1[2] * (1 - (S_[hi] - B) / (1 - B))
    return out


KNOT = strand_knot()


def draw_strand(p, color, width=7.0, opacity=1.0, gap=0.2):
    """A strand seen from above: where it passes under another part of itself it breaks, so crossings read."""
    xy = p[:, :2]
    d = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=-1)
    idx = np.arange(len(p))
    near = (d < gap) & (np.abs(idx[:, None] - idx[None, :]) > 12)
    under = (near & (p[None, :, 2] > p[:, None, 2] + 0.02)).any(1)
    g = VGroup()
    run = []
    for i in range(len(p)):
        if under[i]:
            if len(run) > 8:                                         # no slivers between gaps
                g.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
                      .set_points_as_corners([P3(*q[:2]) for q in run]))
            run = []
        else:
            run.append(p[i])
    if len(run) > 8:
        g.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
              .set_points_as_corners([P3(*q[:2]) for q in run]))
    return g


@scene(T.ch4_s05, T.ch4_s06)
def ch4_s05(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=2)
    t0, t1 = float(s.start), float(s.end)
    t_mug, t_sq, t_ze, t_dna = (float(T.ch4_s05_coffee_mug), float(T.ch4_s05_squash), float(T.ch4_s05_zero),
                                float(T.ch4_s05_dna))
    t_both, t_same, t_bio = t_ze - 1.11, t_ze + 2.68, t_ze + 4.56          # 'Both' 'same shape' 'Biologists'
    t_tan, t_unt = t_dna + 0.68, t_dna + 1.56                              # 'tangle' 'untangle'
    S = C.space
    t_out = t_bio - 0.4

    # the mug, turning until its handle faces us; then squashed into its handle
    spin = keys((t_mug - 0.3, -0.7), (t_sq + 0.1, 0.0), (t_sq + 3.3, 0.0), (t_both - 0.4, 0.55))
    morph = ramp(t_sq + 0.2, t_sq + 3.2, 0.0, 1.0, ease="easy_ease")
    dx = ramp(t_both - 0.4, t_both + 0.5, 0.0, SLIDE, ease="easy_ease")
    s.shader("solid.frag", z=1, u_c=(float(MC[0]), float(MC[1])), u_size=MS, u_tilt=TILT, u_spin=spin, u_morph=morph,
             u_amt=fade(t_mug, dur=0.8, out=t_out + 0.6, out_dur=0.6), u_R=RING_R, u_r=RING_r, u_col=lin(S),
             u_mode=1.0, u_dx=dx)
    # 'Both': a mug comes back on the left
    s.shader("solid.frag", z=1, u_c=(float(MC[0]) - SLIDE, float(MC[1])), u_size=MS, u_tilt=TILT,
             u_spin=ramp(t_both, t_out, -0.25, -0.55), u_morph=0.0,
             u_amt=fade(t_both + 0.3, dur=0.7, out=t_out + 0.6, out_dur=0.6), u_R=RING_R, u_r=RING_r, u_col=lin(S),
             u_mode=1.0, u_dx=0.0)

    tags = VGroup(*(tex(r"\chi = 0", 52, C.text).move_to(P3(MC[0] + dx_, -1.85)) for dx_ in (-SLIDE, SLIDE)))
    m.play(LaggedStart(*(FadeIn(t_, shift=0.1 * UP) for t_ in tags), lag_ratio=0.3), at=t_ze - 0.1, dur=0.8)
    eq = tex("=", 90, C.text).move_to(MC)
    same = caps("same shape", 56, S).move_to(P3(0, 3.05))
    m.play(FadeIn(eq, scale=0.6), at=t_same - 0.1, dur=0.5)
    m.play(FadeIn(same, shift=0.1 * DOWN), at=t_same, dur=0.6)
    m.play(FadeOut(VGroup(tags, eq, same)), at=t_out, dur=0.6)

    # DNA: a long strand that tangles into a knot and slips free
    t_d0 = t_bio + 0.5
    free = strand_free()

    def strand(t):
        if t < t_tan - 0.1:
            u = ss((t - t_d0) / 1.4)                                     # draws in from the left
            n = max(2, int(u * N))
            ph = 0.6 * (t - t_d0)
            p = strand_free(ph)[:n]
        else:
            ph = 0.6 * (t_tan - 0.1 - t_d0)
            k = ss((t - t_tan + 0.1) / 0.9) * (1 - ss((t - t_unt) / 1.0))
            p = (1 - k) * strand_free(ph + 0.6 * max(0.0, t - t_unt)) + k * KNOT
        f = 1 - ss((t - (t1 - 0.7)) / 0.6)
        return draw_strand(p, S, opacity=f)

    top.redraw(window(strand, t_d0, t1 - 0.05), during=(t_d0, t1))
    dna = sans("DNA", 34, C.muted).move_to(P3(-5.2, 0.55))
    m.play(FadeIn(dna), at=t_dna - 0.1, dur=0.5)
    m.play(FadeOut(dna), at=t1 - 0.7, dur=0.5)
