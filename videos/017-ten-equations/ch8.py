"""Chapter 8 (Shannon's channel capacity): shared geometry and maths for scenes s25–s27.

Everything plotted is computed: the scope trace is a square wave plus seeded, band-limited Gaussian noise, and each
received bit is decided at its slot centre against the threshold; the constellations are 2-, 4- and 16-point QAM
scaled to one peak amplitude with one noise level, so packing more points shrinks the gaps; the capacity curve is
B log2(1 + S/N); Voyager's candidates are weighed by Gaussian likelihoods of the received point.
"""
from __future__ import annotations

import math

import numpy as np
from aion import C
from manim import (DOWN, LEFT, RIGHT, UP, Arc, Circle, DashedLine, Dot, Line, Polygon, Rectangle, RoundedRectangle,
                   VGroup)

from kit import P3, polyline, sans, tex, tint

# ------------------------------------------------------------------------------ the cable (c07_s03 → c08_s01)
CABLE_BITS = "1011001110100101101100111010"
CABLE_Y, EMIT_X, BIT_W, SPEED, AMP = -0.35, -5.6, 0.42, 2.4, 0.32


def cable_t0():
    from beats import T
    return float(T.c07_s03_cables) + 0.5


def cable_noise(t):
    from beats import T
    from kit import smooth01
    return 0.075 * float(smooth01((t - float(T.c07_s03_noise) + 0.1) / 1.4))


def cable_wave(t, a=1.0):
    """The bit train leaving the emitter along the cable at time t, with the wire's noise (fresh each 1/30 s)."""
    t_c = cable_t0()
    front = min(EMIT_X + SPEED * (t - t_c), 7.4)
    if a < 0.01 or front <= EMIT_X + 0.02:
        return VGroup()
    xx = np.linspace(EMIT_X, front, max(int((front - EMIT_X) * 40), 2))
    k = np.floor((SPEED * (t - t_c) - (xx - EMIT_X)) / BIT_W).astype(int)
    yy = CABLE_Y + AMP * (2 * np.array([int(CABLE_BITS[i % len(CABLE_BITS)]) for i in k]) - 1)
    n = cable_noise(t)
    if n > 0:
        ph = np.floor(t * 30)
        yy = yy + n * (np.sin(xx * 23.1 + ph * 1.7) + 0.6 * np.sin(xx * 41.3 - ph * 2.9)
                       + 0.4 * np.sin(xx * 67.9 + ph * 4.1))
    return polyline(list(zip(xx, yy)), C.shannon, 3.0, a)


def cable_bits(t, a=1.0):
    """The bit labels riding over the train."""
    t_c = cable_t0()
    g = VGroup()
    for j in range(len(CABLE_BITS)):
        xc = EMIT_X + SPEED * (t - t_c) - (j + 0.5) * BIT_W
        if EMIT_X + 0.1 < xc < 7.0:
            g.add(sans(CABLE_BITS[j], 20, C.muted).set_opacity(a).move_to(P3(xc, CABLE_Y + AMP + 0.32)))
    return g


def cable_static(a=1.0):
    """The cable line and its emitter dot."""
    return (Line(P3(EMIT_X, CABLE_Y), P3(7.4, CABLE_Y), stroke_color=tint(C.muted, 0.5), stroke_width=1.4),
            Dot(P3(EMIT_X, CABLE_Y), radius=0.1, color=C.light))


# ----------------------------------------------------------------------------------------------- the scope (c08_s01)
BITS = "1011001110100101"
SX0, SX1, SY, SA = -5.6, 5.6, 0.15, 0.85           # trace x range, centre line, level amplitude
NOISE_SEED, NOISE_SD = 45, 0.5                      # σ in units of the amplitude


def slot_w():
    return (SX1 - SX0) / len(BITS)


def levels():
    return np.array([1.0 if b == "1" else -1.0 for b in BITS])


def scope_noise(n=900):
    """Band-limited Gaussian noise along the trace (seeded), unit σ in level units; and its x samples."""
    rng = np.random.default_rng(NOISE_SEED)
    raw = rng.normal(0, 1, n + 40)
    k = np.exp(-0.5 * (np.arange(-20, 21) / 2.2) ** 2)
    sm = np.convolve(raw, k / k.sum(), "same")[20:-20]
    sm = sm / sm.std()
    return np.linspace(SX0, SX1, n), sm


def trace(noise=1.0):
    """The received trace (screen x, y): square wave plus noise·σ."""
    x, nz = scope_noise()
    k = np.clip(((x - SX0) / slot_w()).astype(int), 0, len(BITS) - 1)
    return x, SY + SA * (levels()[k] + noise * NOISE_SD * nz)


def decisions():
    """For each bit: (slot centre x, decided bit, wrong?) from the full-noise trace sampled at the slot centre."""
    x, y = trace(1.0)
    out = []
    for j in range(len(BITS)):
        xc = SX0 + (j + 0.5) * slot_w()
        yc = float(np.interp(xc, x, y))
        d = 1 if yc > SY else 0
        out.append((xc, d, d != int(BITS[j])))
    return out


# ------------------------------------------------------------------------------------- constellations (c08_s02)
CC, CS, TILT = np.array([-2.75, -0.35]), 1.7, math.radians(24)   # centre, units per amplitude, plane tilt
SIGMA = 0.15                                                     # noise σ in amplitude units (one for all)
N_PER = 260


def constellation(M):
    """M-point QAM (M = 2, 4, 16) scaled so its largest coordinate is 1."""
    if M == 2:
        return np.array([[-1.0, 0.0], [1.0, 0.0]])
    lv = np.array([-1.0, 1.0]) if M == 4 else np.array([-3.0, -1.0, 1.0, 3.0]) / 3.0
    return np.array([(a, b) for b in lv[::-1] for a in lv])


def samples(M, seed=1708):
    """Received samples (N_PER per point) with Gaussian noise σ, which point was sent, and whether it is misread."""
    pts = constellation(M)
    rng = np.random.default_rng(seed + M)
    unit = rng.normal(0, 1, (len(pts) * N_PER, 2))
    sent = np.repeat(np.arange(len(pts)), N_PER)
    return pts, unit, sent


def received(M, scale=1.0):
    pts, unit, sent = samples(M)
    rx = pts[sent] + SIGMA * scale * unit
    near = np.argmin(((rx[:, None, :] - pts[None]) ** 2).sum(-1), 1)
    return rx, near != sent


def plane(ab, yaw=0.0):
    """Project points of the tilted constellation plane to the screen (a slow yaw about its normal)."""
    ab = np.atleast_2d(ab)
    c, s = math.cos(yaw), math.sin(yaw)
    a = c * ab[:, 0] - s * ab[:, 1]
    b = s * ab[:, 0] + c * ab[:, 1]
    return CC + CS * np.stack([a, b * math.cos(TILT)], 1)


# ------------------------------------------------------------------------------------------ the capacity curve
GX0, GX1, GY0, GY1 = 3.05, 6.25, -2.55, -0.75     # graph box in the right column
SN_MAX, CB_MAX = 1100.0, 11.0                      # linear S/N on x (so the logarithm shows), bit/s per Hz on y
BW_HZ, SNR_DB = 20e6, 30.0


def capacity(sn, bw=1.0):
    """Shannon's limit for a linear signal-to-noise ratio sn: bw · log2(1 + sn)."""
    return bw * np.log2(1 + np.asarray(sn, float))


def gpt(sn, cb):
    return np.array([GX0 + (GX1 - GX0) * sn / SN_MAX, GY0 + (GY1 - GY0) * cb / CB_MAX])


def graph_axes():
    ax = VGroup(Line(P3(GX0, GY0), P3(GX1 + 0.1, GY0), stroke_color=tint(C.muted, 0.7), stroke_width=1.6),
                Line(P3(GX0, GY0), P3(GX0, GY1 + 0.1), stroke_color=tint(C.muted, 0.7), stroke_width=1.6))
    lab = VGroup(sans("signal / noise", 20, C.muted).next_to(P3(GX1, GY0), DOWN, buff=0.14).align_to(P3(GX1, 0), RIGHT),
                 sans("Mbit/s", 20, C.muted).next_to(P3(GX0, GY1 + 0.1), UP, buff=0.1))
    return VGroup(ax, lab)


def capacity_eqn():
    from aion import Eqn
    from kit import RC
    e = Eqn(r"C=B\log_2\left(1+\frac{S}{N}\right)", colors={"C": C.shannon, "B": C.text, r"\frac{S}{N}": C.text})
    return e.scale(0.95).move_to(P3(RC, 2.35))


def eqn_tags(e):
    from kit import tag_under
    return (tag_under(e, "C", "capacity", C.shannon), tag_under(e, "B", "width", C.muted),
            tag_under(e, r"\frac{S}{N}", "signal / noise", C.muted))


BAND_Y, BAND_X = 0.2, (3.05, 6.25)
BAND_LO, BAND_HI = 3.95, 5.35


def band():
    """A frequency axis with the channel's band (a flat-topped spectrum) and a brace marking its width B."""
    from manim import BraceBetweenPoints
    ax = Line(P3(BAND_X[0], BAND_Y), P3(BAND_X[1], BAND_Y), stroke_color=tint(C.muted, 0.7), stroke_width=1.6)
    xs = np.linspace(BAND_LO - 0.35, BAND_HI + 0.35, 120)
    edge = lambda x: 1 / (1 + np.exp(-(x) / 0.06))
    ys = BAND_Y + 0.6 * edge(xs - BAND_LO) * edge(BAND_HI - xs)
    spec = polyline(list(zip(xs, ys)), C.shannon, 2.4)
    br = BraceBetweenPoints(P3(BAND_LO, BAND_Y + 0.68), P3(BAND_HI, BAND_Y + 0.68), direction=UP, buff=0.04,
                            color=C.muted).set_stroke(width=0)
    lab = tex("B", 30, C.text).next_to(br, UP, buff=0.06)
    fq = sans("frequency", 18, C.muted).next_to(P3(BAND_X[1], BAND_Y), DOWN, buff=0.1).align_to(P3(BAND_X[1], 0), RIGHT)
    return VGroup(ax, fq), spec, VGroup(br, lab)


def curve_pts(u=1.0):
    sn = SN_MAX * np.linspace(0, 1, 200) ** 2 * u                    # dense near 0, where it bends
    return [tuple(gpt(d, c)) for d, c in zip(sn, capacity(sn))]


def marker():
    """20 MHz at 30 dB: the computed capacity, on the curve."""
    sn = 10 ** (SNR_DB / 10)
    mbit = float(capacity(sn, BW_HZ)) / 1e6
    p = gpt(sn, float(capacity(sn)))
    dot = Dot(P3(*p), radius=0.07, color=C.light)
    guide = DashedLine(P3(p[0], GY0), P3(*p), dash_length=0.08, stroke_color=tint(C.muted, 0.7), stroke_width=1.4)
    val = sans(f"{mbit:.0f} Mbit/s", 24, C.shannon).next_to(P3(p[0] - 0.15, p[1] - 0.35), DOWN + LEFT, buff=0.0)
    sub = sans(f"{BW_HZ / 1e6:.0f} MHz · {SNR_DB:.0f} dB", 18, C.muted).next_to(val, DOWN, buff=0.08, aligned_edge=RIGHT)
    return dot, guide, VGroup(val, sub)


# ---------------------------------------------------------------------------------------------- Voyager (c08_s03)
VOY = np.array([-4.7, 1.55])
DISH = np.array([4.55, -1.75])
STAR_N = 520


def stars(seed=1977):
    """Seeded stars: screen x, y in a wide box and a depth layer (0 far … 2 near)."""
    rng = np.random.default_rng(seed)
    xy = np.stack([rng.uniform(-9.5, 9.5, STAR_N), rng.uniform(-4.6, 4.6, STAR_N)], 1)
    layer = rng.choice(3, STAR_N, p=(0.55, 0.3, 0.15))
    return xy, layer


def voyager(scale=0.55):
    """Line art: the high-gain dish (seen at an angle), the bus, the magnetometer boom and the RTG boom."""
    dish = VGroup(Arc(radius=0.62, start_angle=math.radians(200), angle=math.radians(140), stroke_width=2.4),
                  Line(LEFT * 0.58 + DOWN * 0.21, RIGHT * 0.58 + DOWN * 0.21, stroke_width=1.6))
    dish.shift(UP * 0.62)
    bus = Polygon(*[0.26 * np.array([math.cos(a), 0.6 * math.sin(a), 0]) for a in np.linspace(0, 2 * math.pi, 11)[:-1]],
                  stroke_width=2.0)
    bus.shift(DOWN * 0.08)
    boom = Line(RIGHT * 0.22, RIGHT * 1.7 + DOWN * 0.42, stroke_width=1.4)
    rtg = VGroup(Line(LEFT * 0.22, LEFT * 1.0 + DOWN * 0.35, stroke_width=1.8),
                 Rectangle(width=0.22, height=0.12, stroke_width=1.6).move_to(LEFT * 1.05 + DOWN * 0.37))
    feed = Line(UP * 0.42, UP * 0.85, stroke_width=1.4)
    g = VGroup(dish, bus, boom, rtg, feed).set_stroke(color=C.light)
    return g.scale(scale)


def dish(scale=1.0):
    """Line art of a ground station: a parabolic dish aimed up and to the left (towards Voyager) on a pedestal."""
    w = np.array([-0.82, 0.57])                                  # the dish's axis
    n = np.array([-w[1], w[0]])
    u = np.linspace(-1, 1, 60)
    bowl = [tuple(w * 0.42 * v * v + n * 0.78 * v) for v in u]
    rim_a, rim_b = w * 0.42 + n * 0.78, w * 0.42 - n * 0.78
    focus = w * 0.36                                             # the true focus: 1 / (4a), a = 0.42 / 0.78²
    feed = VGroup(*[Line(P3(*r), P3(*focus), stroke_color=C.light, stroke_width=1.4) for r in (rim_a, rim_b)],
                  Dot(P3(*focus), radius=0.045, color=C.light))
    ped = VGroup(Line(P3(0.0, 0.0), P3(0.25, -0.95), stroke_color=C.light, stroke_width=2.2),
                 Line(P3(-0.1, -0.95), P3(0.6, -0.95), stroke_color=C.light, stroke_width=2.2))
    return VGroup(polyline(bowl, C.light, 2.6), feed, ped).scale(scale)


def router():
    """Line art: a WiFi router with two antennas."""
    body = RoundedRectangle(width=1.1, height=0.32, corner_radius=0.08, stroke_width=2.2)
    ants = VGroup(Line(LEFT * 0.35 + UP * 0.16, LEFT * 0.45 + UP * 0.72, stroke_width=2.2),
                  Line(RIGHT * 0.35 + UP * 0.16, RIGHT * 0.45 + UP * 0.72, stroke_width=2.2))
    leds = VGroup(*[Dot(LEFT * 0.3 + RIGHT * 0.15 * k, radius=0.025) for k in range(5)])
    return VGroup(body, ants, leds)


def tower():
    """Line art: a lattice mobile mast with three panel antennas."""
    h = 1.9
    legs = VGroup(Line(LEFT * 0.42 + DOWN * h / 2, UP * h / 2 + LEFT * 0.08, stroke_width=2.0),
                  Line(RIGHT * 0.42 + DOWN * h / 2, UP * h / 2 + RIGHT * 0.08, stroke_width=2.0))
    rungs = VGroup()
    for k in range(5):
        y0, y1 = -h / 2 + k * h / 5, -h / 2 + (k + 1) * h / 5
        w0, w1 = 0.42 - 0.34 * k / 5, 0.42 - 0.34 * (k + 1) / 5
        rungs.add(Line(LEFT * w0 + UP * y0, RIGHT * w1 + UP * y1, stroke_width=1.2),
                  Line(RIGHT * w0 + UP * y0, LEFT * w1 + UP * y1, stroke_width=1.2))
    panels = VGroup(*[Rectangle(width=0.1, height=0.36, stroke_width=1.8).move_to(UP * (h / 2 - 0.1) + RIGHT * dx)
                      for dx in (-0.2, 0.0, 0.2)])
    return VGroup(legs, rungs, panels)


def waves(n=3, r0=0.25, dr=0.2, angle=math.radians(80)):
    """Concentric arcs facing up: a radio signal."""
    return VGroup(*[Arc(radius=r0 + k * dr, start_angle=math.pi / 2 - angle / 2, angle=angle, stroke_width=2.2)
                    for k in range(n)])


# ------------------------------------------------------------------------------------------ most likely (c08_s03)
RC_C, RC_S = np.array([-1.0, 0.25]), 1.25          # the received constellation: centre, units per amplitude
RX = np.array([0.18, 0.42])                         # the received point, in amplitude units
RX_SD = 0.62                                        # its noise σ (the signal arrives faint)


def likelihoods():
    """P(candidate | received) for the four QPSK candidates, equal priors, Gaussian noise."""
    pts = constellation(4)
    ll = np.exp(-((pts - RX) ** 2).sum(1) / (2 * RX_SD ** 2))
    return pts, ll / ll.sum()


def rc(ab):
    return RC_C + RC_S * np.asarray(ab)
