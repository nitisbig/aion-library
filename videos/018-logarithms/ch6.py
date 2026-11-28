"""Chapter six's shared drawings: the sound-ring raster, the wireframe ground with a seismic ripple, small line
drawings (glass, atom, person, Earth, galaxy) and the even-step ruler.

Example:
    s.add(FramesLayer(rings_frame(level), height=6.4, pos=(-3.2, 0.0), z=-2))
"""
import math

import numpy as np
from aion import *  # noqa: F403

from kit import P3, feather, lin_rgb, polyline, tex, tint


def rings_frame(gain, color):
    """Expanding rings from a point source; `gain(t)` in [0, 1] sets the brightness (tone-mapped, never clips)."""
    w, h = 640, 640
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot(xx - 0.5 * w, yy - 0.5 * h) / h
    col = lin_rgb(color)
    env = np.exp(-r * 2.2) * np.clip((r - 0.012) / 0.03, 0, 1)

    def frame(t):
        g = gain(t)
        wave = 0.5 + 0.5 * np.cos(2 * math.pi * (r * 9.0 - 0.9 * t))
        I = (wave ** 6) * env * (0.25 + 1.5 * g)
        lin = I[..., None] * col + np.exp(-r * 30)[..., None] * col
        lin = lin / (1 + lin)  * 1.6                                   # soft tone map
        srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
        al = np.clip(I * 1.6 + np.exp(-r * 30), 0, 1)
        return feather(np.dstack([np.clip(srgb * 255, 0, 255), al * 255]).astype(np.uint8), 0.12, 0.12, 0.12, 0.12)
    return frame


def ground(t, amp, t_start, cx=-2.7, cy=-0.6, n=17, color=None):
    """A wireframe ground patch seen from above at an angle; a decaying ring wave runs out from the centre."""
    color = color or C.quake  # noqa: F405
    us = np.linspace(-1, 1, 48)

    def proj(gx, gy):
        r = np.hypot(gx, gy)
        age = max(t - t_start, 0.0)
        front = 0.55 * age
        z = amp * np.exp(-1.2 * r) * np.sin(9 * (r - front)) * np.clip((front - r) / 0.3, 0, 1)
        sc = 1 - 0.28 * gy
        return cx + 2.9 * gx * sc, cy + 1.25 * gy + 0.9 * z

    g = VGroup()  # noqa: F405
    for k, v in enumerate(np.linspace(-1, 1, n)):
        fade = 0.85 - 0.5 * (v + 1) / 2
        x, y = proj(us, np.full_like(us, v))
        g.add(polyline(list(zip(x, y)), tint(color, fade), 1.6))
        x, y = proj(np.full_like(us, v), us)
        g.add(polyline(list(zip(x, y)), tint(color, 0.55), 1.2))
    return g


def glass(liquid, h=0.8, w=0.5):
    """A tumbler in line drawing, filled two thirds with `liquid`."""
    tl, tr, bl, br = P3(-w / 2, h / 2), P3(w / 2, h / 2), P3(-0.4 * w, -h / 2), P3(0.4 * w, -h / 2)
    fill_h = 0.62 * h
    f = fill_h / h
    lt = P3(-0.4 * w - 0.1 * w * f, -h / 2 + fill_h)
    rt = P3(0.4 * w + 0.1 * w * f, -h / 2 + fill_h)
    return VGroup(Polygon(bl, br, rt, lt, stroke_width=0, fill_color=liquid, fill_opacity=0.55),  # noqa: F405
                  VMobject(stroke_color=C.ruler, stroke_width=2).set_points_as_corners([tl, bl, br, tr]))  # noqa: F405


def atom():
    return VGroup(Dot(P3(0, 0), radius=0.07, color=C.ruler),  # noqa: F405
                  *[Ellipse(width=0.9, height=0.3, stroke_color=C.ruler, stroke_width=1.5).rotate(k * PI / 3)  # noqa: F405
                    for k in range(3)])


def person():
    c = C.ruler  # noqa: F405
    return VGroup(Circle(radius=0.11, stroke_color=c, stroke_width=2).move_to(P3(0, 0.42)),  # noqa: F405
                  Line(P3(0, 0.31), P3(0, -0.12), stroke_color=c, stroke_width=2),  # noqa: F405
                  Line(P3(-0.2, 0.15), P3(0.2, 0.15), stroke_color=c, stroke_width=2),  # noqa: F405
                  Line(P3(0, -0.12), P3(-0.14, -0.45), stroke_color=c, stroke_width=2),  # noqa: F405
                  Line(P3(0, -0.12), P3(0.14, -0.45), stroke_color=c, stroke_width=2))  # noqa: F405


def earth():
    c = C.ruler  # noqa: F405
    return VGroup(Circle(radius=0.38, stroke_color=c, stroke_width=2),  # noqa: F405
                  Ellipse(width=0.76, height=0.24, stroke_color=tint(c, 0.5), stroke_width=1.2),  # noqa: F405
                  Line(P3(0, -0.38), P3(0, 0.38), stroke_color=tint(c, 0.5), stroke_width=1.2))  # noqa: F405


def galaxy(seed=1806):
    rng = np.random.default_rng(seed)
    pts = []
    for arm in range(2):
        for i in range(90):
            th = 0.25 + i * 0.06
            rr = 0.06 * math.exp(0.22 * th * 1.6)
            ang = th + arm * PI  # noqa: F405
            pts.append((rr * math.cos(ang) + rng.normal(0, 0.025), 0.55 * rr * math.sin(ang) + rng.normal(0, 0.02)))
    return VGroup(*[Dot(P3(px, py), radius=0.018, color=C.star, fill_opacity=0.85) for px, py in pts],  # noqa: F405
                  Dot(P3(0, 0), radius=0.07, color=C.star))  # noqa: F405


def vruler(x, y_of, values, label_color=None, side=LEFT, size=24):  # noqa: F405
    """A vertical ruler at x with ticks at y_of(v) for each value, labels on `side`."""
    g = VGroup(Line(P3(x, y_of(values[0])), P3(x, y_of(values[-1])), stroke_color=C.ruler, stroke_width=2.5))  # noqa: F405
    for v in values:
        p = P3(x, y_of(v))
        g.add(Line(p, p + side * 0.14, stroke_color=C.ruler, stroke_width=2),  # noqa: F405
              tex(str(v), size, label_color or C.ruler).next_to(p + side * 0.14, side, buff=0.08))  # noqa: F405
    return g
