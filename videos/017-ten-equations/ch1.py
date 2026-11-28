"""Chapter 1 shared pieces: the field-texture weights of the c01_s01 stage, so c01_s02 can open on exactly the
filings frame c01_s01 ends on.

Example:
    from ch1 import field_weights, filings_rgba
    s.add(ArrayLayer(filings_rgba(), height=8.0, z=-10))
"""
import math

import numpy as np
from aion import *  # noqa: F403

import sims as sm
from beats import T
from kit import COL, P3, lin_rgb, mix, sans, smooth01, tex

SC = np.array([-2.1, 0.05])                      # chapter-1 stage centre, left of the equation column
FILINGS = dict(L=11, phases=1, density=0.03, seed=1702)


def grid(ny, nx):
    xs = (np.arange(nx) + 0.5) / nx * (128 / 9) - 64 / 9
    ys = 4.0 - (np.arange(ny) + 0.5) / ny * 8.0
    return np.meshgrid(xs, ys)


def field_weights(ny, nx):
    """Linear-light colour weights (ny, nx, 3) of the E texture, the flowing B texture and the filings."""
    X, Y = grid(ny, nx)
    cx, cy = sm.CHARGE_POS
    mx, my = sm.MAGNET_POS
    r_e = np.hypot(X - cx, Y - cy)
    d_b = np.hypot(np.clip(np.abs(X - mx) - sm.MAGNET_HALF, 0, None), Y - my)
    edge = (smooth01((64 / 9 - np.abs(X)) / 0.9) * smooth01((4.0 - np.abs(Y)) / 0.6))[..., None]
    a_e = (smooth01((3.9 - r_e) / 2.8) * 0.75)[..., None] * lin_rgb(C.e_field)
    a_b = (smooth01((3.5 - d_b) / 2.6) * 0.75)[..., None] * lin_rgb(C.b_field)
    a_f = (smooth01((2.7 - d_b) / 2.0) * 0.9)[..., None] * lin_rgb(mix(C.b_field, C.light, 0.45))
    return tuple(np.asarray(a * edge, np.float32) for a in (a_e, a_b, a_f))


def filings_tex():
    return ((sm.lic(sm.magnet_field, **FILINGS)[0].astype(np.float32) / 255.0) ** 1.8)[..., None]


def to_rgba(lin):
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
    out = np.empty(lin.shape[:2] + (4,), np.uint8)
    out[..., :3] = (srgb * 255 + 0.5).astype(np.uint8)
    out[..., 3] = 255
    return out


def filings_rgba():
    """The iron-filings picture alone (the last frame of c01_s01 once the E texture has faded)."""
    F = filings_tex()
    _, _, a_f = field_weights(*F.shape[:2])
    return to_rgba(F * a_f)


# ------------------------------------------------------------------------------------------------ the four laws
def laws():
    """The four laws as MathTex pieces, coloured like the things they describe; one shared scale fits the column."""
    E, B, Q, J = C.e_field, C.b_field, C.charge_p, C.light
    specs = [
        ([r"\nabla\cdot", r"\mathbf E", "=", r"\rho", r"/\varepsilon_0"], {1: E, 3: Q}, "spread", E),
        ([r"\nabla\cdot", r"\mathbf B", "=0"], {1: B}, "loops", B),
        ([r"\nabla\times", r"\mathbf E", "=-", r"\frac{\partial\mathbf B}{\partial t}"], {1: E, 3: B}, "swirl", E),
        ([r"\nabla\times", r"\mathbf B", "=", r"\mu_0", r"\mathbf J", "+", r"\mu_0\varepsilon_0",
          r"\frac{\partial\mathbf E}{\partial t}"], {1: B, 4: J, 7: E}, "swirl", B),
    ]
    eqs = []
    for parts, cols, _, _ in specs:
        e = MathTex(*parts, font_size=46, color=C.text)
        for i, c in cols.items():
            e[i].set_color(c)
        eqs.append(e)
    k = min(1.0, (COL[1] - COL[0]) / max(e.width for e in eqs))
    rows = []
    for i, (e, (_, _, word, hue)) in enumerate(zip(eqs, specs)):
        e.scale(k).move_to(P3(COL[0], 2.2 - 1.42 * i), aligned_edge=LEFT)
        tag = sans(word, 22, hue).next_to(e, DOWN, buff=0.14, aligned_edge=LEFT)
        rows.append((e, tag))
    return rows


def underline_dEdt(e4):
    """Maxwell's own term, ∂E/∂t, underlined in the E hue (text never glows)."""
    return Line(e4[7].get_corner(DL) + 0.07 * DOWN, e4[7].get_corner(DR) + 0.07 * DOWN, stroke_color=C.e_field,
                stroke_width=3)


# ------------------------------------------------------------------------------------------------ rings
def head(p, d, color, size=0.13, op=1.0):
    """A small filled arrowhead at p pointing along d."""
    d = np.asarray(d, float) / (np.hypot(*d) + 1e-12)
    n = np.array([-d[1], d[0]])
    p = np.asarray(p, float)
    pts = [p + d * size * 0.6, p - d * size * 0.5 + n * size * 0.45, p - d * size * 0.5 - n * size * 0.45]
    return Polygon(*[P3(*q) for q in pts], stroke_width=0, fill_color=color, fill_opacity=op)


def ring(xc, yc, w, h, color, ph, op, n=2, size=0.14, width=2.6):
    """A field loop seen at an angle (an ellipse) with `n` arrowheads circulating by phase `ph`."""
    g = VGroup(Ellipse(width=w, height=h, stroke_color=color, stroke_width=width, stroke_opacity=op)
               .move_to(P3(xc, yc)))
    for k in range(n):
        th = ph + 2 * np.pi * k / n
        p = np.array([xc + w / 2 * math.sin(th), yc + h / 2 * math.cos(th)])
        d = np.array([w / 2 * math.cos(th), -h / 2 * math.sin(th)])
        g.add(head(p, d, color, size=size, op=op))
    return g


def gap_rings(t, op):
    """The B rings around a charging capacitor's empty gap (c01_s02's last picture, c01_s03's first)."""
    t4 = float(T.c01_s02_changing_electric)
    a = op * float(smooth01((t - t4 - 0.9) / 0.9))
    g = VGroup()
    if a < 0.01:
        return g
    for h, w in ((2.3, 1.0), (3.0, 0.7)):
        g.add(ring(SC[0], SC[1], 0.42, h, C.b_field, 1.6 * (t - t4), a * w))
    return g


# the stage props shared by c01_s01 and c01_s02
def _magnet():
    w, h = 2 * sm.MAGNET_HALF, 0.44
    s_half = Rectangle(width=w / 2, height=h, stroke_width=0, fill_color=C.mass, fill_opacity=1) \
        .move_to(P3(sm.MAGNET_POS[0] - w / 4, sm.MAGNET_POS[1]))
    n_half = Rectangle(width=w / 2, height=h, stroke_width=0, fill_color=C.b_field, fill_opacity=1) \
        .move_to(P3(sm.MAGNET_POS[0] + w / 4, sm.MAGNET_POS[1]))
    return VGroup(s_half, n_half, tex("S", 30, C.bg).move_to(P3(sm.MAGNET_POS[0] - w / 4, sm.MAGNET_POS[1])),
                  tex("N", 30, C.bg).move_to(P3(sm.MAGNET_POS[0] + w / 4, sm.MAGNET_POS[1])))


def _nail(x, y, ang):
    shaft = Line(LEFT * 0.42, RIGHT * 0.42, stroke_color=C.mass, stroke_width=5)
    head = Line(UP * 0.09, DOWN * 0.09, stroke_color=C.mass, stroke_width=7).move_to(RIGHT * 0.42)
    tip = Polygon(LEFT * 0.42 + UP * 0.03, LEFT * 0.42 + DOWN * 0.03, LEFT * 0.54, stroke_width=0,
                  fill_color=C.mass, fill_opacity=1)
    return VGroup(shaft, head, tip).rotate(ang, about_point=ORIGIN).move_to(P3(x, y))
