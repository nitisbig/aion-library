"""Chapter three's shared slide rule: two boxwood scales (skia wood, Manim engraving) whose upper scale slides by a
pure function of t. c03_s01 builds them, c03_s02 slides them.

Example:
    up = slide_rule(s, lambda t: OFF2 * ramp(t, T.x, 1.5))
"""
import math

from aion import *  # noqa: F403

from kit import RULE_INK, log_scale_marks, soft_shadow, tex, wood_body

L, XL, BH = 10.2, -5.1, 0.85
LO = -0.55
UP = LO + BH + 0.02
OFF2 = L * math.log10(2)


def xpos(v, off=0.0):
    """World x of the number v on a scale (shifted by off)."""
    return XL + off + L * math.log10(v)


def slide_rule(s, off=lambda t: 0.0, opacity=1.0, upper_opacity=None, z=0):
    """Lower (fixed) and upper (sliding) rules. Returns (lower marks, upper marks) Manim groups."""
    uo = opacity if upper_opacity is None else upper_opacity
    sh, shh = soft_shadow(L + 0.7, BH)
    s.add(ArrayLayer(sh, height=shh, pos=(XL + L / 2 + 0.06, LO - 0.11), z=z - 3, opacity=opacity))  # noqa: F405
    s.add(ArrayLayer(wood_body(L, BH)[0], height=BH, pos=(XL + L / 2, LO), z=z - 2, opacity=opacity))  # noqa: F405
    s.add(ArrayLayer(sh, height=shh, z=z - 1.9, opacity=Track(lambda t: 0.8 * float(uo(t) if callable(uo) else uo)),  # noqa: F405
                     pos=Track(lambda t: (XL + L / 2 + float(off(t)) + 0.06, UP - 0.11))))  # noqa: F405
    s.add(ArrayLayer(wood_body(L, BH, seed=1623)[0], height=BH, z=z - 1.8, opacity=uo,  # noqa: F405
                     pos=Track(lambda t: (XL + L / 2 + float(off(t)), UP))))  # noqa: F405
    m = s.manim(z=z, opacity=opacity)
    lower = log_scale_marks(XL, L, LO + BH / 2, up=False, label_size=24)
    m.add(lower)
    mu = s.manim(z=z, opacity=uo)
    upper = log_scale_marks(XL, L, UP - BH / 2, up=True, label_size=24)
    c0 = upper.get_center()
    mu.add(upper)
    mu.drive(upper, lambda g, t: g.move_to(c0 + RIGHT * float(off(t))), during=(float(s.start), float(s.end)))  # noqa: F405
    return lower, upper
