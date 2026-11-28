"""Outro (out_s01, out_s02): the ten tiles, as a helix of cards and then as the 5x2 wall.

A tile is one chapter's key frame (a 1080p still of its own scene, cropped to 16:9 and feathered), with a rule in the
chapter hue under it. scripts/make_tiles.py renders them into assets/tiles/T01.png … T10.png; `tile_rgba(i)` loads them.

Cards are billboards on a rising ring, seen by a pinhole camera (`helix(i, t_rot, pitch)` → screen position and
scale), so the ten pictures stay upright and legible while the ring turns. The wall is five by two (`wall(i)`).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from ch7 import FOCAL

HERE = Path(__file__).parent
TILE_DIR = HERE / "assets/tiles"

# key frame per chapter: (scene, time in s, crop centre x, crop centre y, crop width), crop in world units
KEYFRAMES = [
    ("s06_c01_light", 165.02, -1.9, -0.1, 8.0),
    ("s09_c02_black_hole", 232.64, 0.0, 0.0, 8.8),
    ("s10_c03_slits", 273.76, -1.0, 0.2, 10.0),
    ("s14_c04_terms", 370.00, -1.0, -0.8, 8.0),
    ("s17_c05_sieve", 445.60, -1.1, -0.1, 7.4),
    ("s19_c06_light_clock", 493.24, -2.6, 0.5, 7.0),
    ("s24_c07_billions", 599.06, 0.0, 0.0, 9.0),
    ("s26_c08_limit", 658.74, -3.0, 0.0, 6.2),
    ("s28_c09_test", 698.06, -1.8, 0.3, 7.5),
    ("s32_c10_cancel", 800.88, -1.55, 0.0, 7.9),
]
# the live loops: a 3 s window of each chapter's own motion (scripts/make_tile_clips.py)
LIVE = [("s06_c01_light", 163.5, 166.5), ("s09_c02_black_hole", 231.0, 234.0), ("s10_c03_slits", 272.5, 275.5),
        ("s14_c04_terms", 368.5, 371.5), ("s17_c05_sieve", 442.0, 445.0), ("s19_c06_light_clock", 491.5, 494.5),
        ("s24_c07_billions", 598.0, 601.0), ("s26_c08_limit", 657.5, 660.5), ("s28_c09_test", 696.5, 699.5),
        ("s32_c10_cancel", 798.0, 801.0)]
NAMES = ["Maxwell · 1865", "Einstein · 1915", "Schrödinger · 1926", "Navier–Stokes · 1845", "Fourier · 1807",
         "Einstein · 1905", "Cauchy · 1847", "Shannon · 1948", "Bayes · 1763", "Black–Scholes · 1973"]
EQS = [r"\nabla\times\mathbf{B}=\mu_0\mathbf{J}+\mu_0\varepsilon_0\frac{\partial\mathbf{E}}{\partial t}",
       r"G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}",
       r"i\hbar\,\frac{\partial\psi}{\partial t}=\hat H\psi",
       r"\rho\left(\frac{\partial\mathbf{u}}{\partial t}+\mathbf{u}\cdot\nabla\mathbf{u}\right)"
       r"=-\nabla p+\mu\nabla^2\mathbf{u}+\mathbf{f}",
       r"F(\omega)=\int f(t)\,e^{-i\omega t}\,dt",
       r"\Delta t'=\frac{\Delta t}{\sqrt{1-v^2/c^2}}",
       r"\theta\leftarrow\theta-\eta\,\nabla L(\theta)",
       r"C=B\log_2\left(1+\frac{S}{N}\right)",
       r"P(A\mid B)=\frac{P(B\mid A)\,P(A)}{P(B)}",
       r"\frac{\partial V}{\partial t}+\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}+rS\frac{\partial V}{\partial S}"
       r"-rV=0"]

TW = 2.3                                   # tile width on the wall (world units); 16:9 picture
TH = TW * 9 / 16
RULE_GAP = 0.06                            # the hue rule sits this far under the picture (baked into the PNG)
PX_W = 640                                 # tile picture width in px
PAD = 3                                    # transparent rows above and below each tile image (px)


def tile_rgba(i):
    from PIL import Image
    return np.asarray(Image.open(TILE_DIR / f"T{i + 1:02d}.png").convert("RGBA"))


def tile_height():
    """World height of the whole tile image (padding, picture, gap, rule) when the picture is TW wide."""
    img = tile_rgba(0)
    return TW * img.shape[0] / img.shape[1]


def pic_dy():
    """How far the picture's centre sits above the tile image's centre."""
    return tile_height() / 2 - TW * PAD / PX_W - TH / 2


# ------------------------------------------------------------------------------------------------ the helix
R_RING, D_CAM, Y_SPAN = 4.3, 12.5, 3.3     # ring radius, camera distance, rise from T1 to T10
CARD = 0.8                                # card size on the ring, relative to a wall tile


def ring_point(i, t_rot):
    """3D centre of card i: angle around the ring (T1 at the front-left, going round), rising with i."""
    th = math.radians(-120 + 36 * i) + t_rot
    return np.array([R_RING * math.sin(th), -Y_SPAN / 2 + Y_SPAN * i / 9, R_RING * math.cos(th)])


def project(P, pitch, lift=0.0):
    """Pinhole camera at distance D_CAM, raised by `pitch`, looking at (0, lift, 0). Returns (x, y, scale, depth)."""
    X, Y, Z = P[0], P[1] - lift, P[2]
    cp, sp = math.cos(pitch), math.sin(pitch)
    up = Y * cp - Z * sp
    depth = D_CAM - (Z * cp + Y * sp)
    k = FOCAL / depth
    return X * k, up * k, k, depth


Y_SHIFT = 0.35                             # the ring sits a little above centre
SX = 1.3                                  # the ring is stretched sideways to use the 16:9 frame


def helix(i, t_rot, pitch, lift=0.0):
    """Screen (x, y), card scale (1 = a wall tile) and depth of card i."""
    x, y, k, d = project(ring_point(i, t_rot), pitch, lift)
    return x * SX, y + Y_SHIFT, CARD * D_CAM / d, d


def arc_pts(i, t_rot, pitch, lift=0.0, n=40):
    """Screen points of the arc from card i to card i+1: from under one card to under the next, bowing outwards."""
    a, b = ring_point(i, t_rot), ring_point(i + 1, t_rot)
    drop = np.array([0.0, -0.5, 0.0])
    out = []
    for u in np.linspace(0, 1, n):
        p = (1 - u) * a + u * b
        r = np.hypot(p[0], p[2])
        bow = 1 + 0.08 * math.sin(math.pi * u)
        q = np.array([p[0] / r * R_RING * bow, p[1], p[2] / r * R_RING * bow]) + drop
        x, y, _, _ = project(q, pitch, lift)
        out.append((x * SX, y + Y_SHIFT))
    return out


# ------------------------------------------------------------------------------------------------- the wall
WX = [-5.1, -2.55, 0.0, 2.55, 5.1]
WY = [1.55, -1.35]


def wall(i):
    return WX[i % 5], WY[i // 5]


def tile_layer(s, i, place, opacity, during=None, z=0.0, live=True):
    """Tile i, screen-locked; place(t) → (x, y, scale, depth). Live (the default, when assets/tiles/Tnn.mp4 is baked):
    its chapter's own motion, looping, drawn with blend='screen' so its black reads as transparent. Otherwise the
    still PNG. Draw order `z` is fixed (layers cannot reorder over time), so pass a nearer card a higher z."""
    from aion import ArrayLayer, FramesLayer, Track
    kw = dict(start=during[0], end=during[1]) if during else {}
    common = dict(parallax=0.0, pos=Track(lambda t: tuple(map(float, place(t)[:2]))),
                  scale=Track(lambda t: float(place(t)[2])), z=float(z), opacity=opacity, **kw)
    mp4 = TILE_DIR / f"T{i + 1:02d}.mp4"
    if live and mp4.exists():
        from clip import LoopClip
        clip = LoopClip(mp4, offset=0.37 * i)                      # out of phase, so the wall never pulses as one
        return s.add(FramesLayer(clip, height=TW * clip.h / clip.w, blend="screen", **common))
    img = tile_rgba(i)
    return s.add(ArrayLayer(img, height=TW * img.shape[0] / img.shape[1], **common))


def wall_labels(i):
    """Under wall tile i: the name and year in small caps, then the equation, both left-aligned to the hue rule."""
    from manim import DOWN, LEFT, UL, VGroup

    from kit import P3, caps, tex
    x, y = wall(i)
    h = tile_height() - 2 * TW * PAD / PX_W
    name = caps(NAMES[i], 20)
    if name.width > TW - 0.1:
        name.scale_to_fit_width(TW - 0.1)
    name.move_to(P3(x - TW / 2, y - h / 2 - 0.1), aligned_edge=UL)
    eq = tex(EQS[i], 24)
    if eq.width > TW - 0.1:
        eq.scale_to_fit_width(TW - 0.1)
    eq.next_to(name, DOWN, buff=0.14, aligned_edge=LEFT)
    return VGroup(name, eq)
