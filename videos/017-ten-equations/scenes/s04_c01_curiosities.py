"""c01_s01 · Two curiosities (hook). Storyboard: plan/scene_plan.md § c01_s01.

The chapter card, then one open stage: a charged sphere lifting paper scraps (left) and a bar magnet pulling a nail
(right). They drift together into Ørsted's experiment: a wire over a compass; the current switches on and the needle
swings. Then the two return with their fields made visible as flowing line-integral-convolution textures (computed
from Coulomb's law and the magnet's two poles), and the magnet's field sharpens into iron filings as the camera pushes in.
"""
import math

import numpy as np
from aion import *

import sims as sm
from ch1 import _magnet, _nail, field_weights, filings_tex, to_rgba
from beats import T
from kit import P3, X0, Y1, add_rail, caps, chapter_card, lin_rgb, mix, glimpse, smooth01, tex, tint

CX, CY = sm.CHARGE_POS
MX, MY = sm.MAGNET_POS
WIRE_X = 0.4                     # Ørsted's wire runs north–south (up the screen) over the compass
COMPASS = (WIRE_X, 0.55)


# ------------------------------------------------------------------------------------------------ field textures
def _field_frames():
    """The flowing E and B textures and the static filings, composed per frame into one opaque RGBA raster."""
    E = sm.lic(sm.charge_field)                                         # (12, ny, nx) uint8, row 0 = top
    B = sm.lic(sm.magnet_field)
    filings = filings_tex()
    a_e, a_b, a_f = field_weights(*E.shape[1:])
    w_f = fade(T.c01_s01_iron_filings, dur=1.6)
    w_eo = fade(T.c01_s02 - 1.3, dur=1.0)                               # E leaves before the cut: c01_s02 opens on filings
    period = 2.4                                                        # seconds per flow cycle

    def tex_at(stack, t):
        p = (t / period * stack.shape[0]) % stack.shape[0]
        i, f = int(p), p - int(p)
        a = stack[i].astype(np.float32) * (1 - f) + stack[(i + 1) % stack.shape[0]].astype(np.float32) * f
        return ((a / 255.0) ** 2.4)[..., None]                          # dark ground, bright filaments

    def frame(t):
        wf = float(w_f(t))
        we = (1 - 0.45 * wf) * (1 - float(w_eo(t)))
        return to_rgba(we * tex_at(E, t) * a_e + (1 - wf) * tex_at(B, t) * a_b + wf * filings * a_f)

    return frame


# ------------------------------------------------------------------------------------------------ props
def _sphere():
    body = Circle(radius=0.55, stroke_width=0, fill_color=C.charge_p, fill_opacity=1).move_to(P3(CX, CY))
    hi = Circle(radius=0.2, stroke_width=0, fill_color=mix(C.charge_p, C.light, 0.45), fill_opacity=0.55) \
        .move_to(P3(CX - 0.18, CY + 0.2))
    return VGroup(body, hi, tex("+", 44, C.bg).move_to(P3(CX, CY)))


SCRAPS = [(-4.55, 0.0), (-4.1, 0.7), (-3.65, -0.4), (-3.2, 0.3), (-2.75, -0.2), (-2.3, 0.5), (-1.95, 0.1)]


def _scrap_state(i, t):
    """Scrap i: lies on the table, then lifts onto the sphere's lower surface (pure in t)."""
    x0, a0 = SCRAPS[i]
    y0 = -1.55
    ang = -1.25 + 2.5 * i / (len(SCRAPS) - 1)                     # where it lands on the sphere (around the bottom)
    x1, y1 = CX + 0.62 * math.sin(ang), CY - 0.62 * math.cos(ang)
    t0 = float(T.c01_s01_electricity) + 0.35 + 0.16 * i
    u = smooth01((t - t0) / 1.3)
    u = u * u * (3 - 2 * u)                                         # slow start, snaps on
    hop = 0.25 * math.sin(math.pi * u)
    return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + hop, a0 * (1 - u) + ang * u


def _exit(t):
    """0 → 1 as the two curiosities drift towards the centre and fade, giving way to Ørsted's rig."""
    return float(smooth01((t - (float(T.c01_s01_rsted) - 0.15)) / 0.9))


def _scraps(t, settled=False):
    v = 0.0 if settled else _exit(t)
    g = VGroup()
    for i in range(len(SCRAPS)):
        x, y, a = _scrap_state(i, float(T.c01_s01_rsted) if settled else t)
        g.add(Rectangle(width=0.17, height=0.1, stroke_width=0, fill_color=C.data, fill_opacity=0.9 * (1 - v))
              .rotate(a).move_to(P3(x + 1.4 * v, y)))
    return g


def _needle(theta, op=1.0):
    """Compass needle at angle theta from north (radians, clockwise positive), north half in the charge hue."""
    L, W = 0.72, 0.11
    north = Polygon(P3(0, L), P3(W, 0), P3(-W, 0), stroke_width=0, fill_color=C.charge_p, fill_opacity=op)
    south = Polygon(P3(0, -L), P3(W, 0), P3(-W, 0), stroke_width=0, fill_color=C.light, fill_opacity=op * 0.85)
    pin = Dot(ORIGIN, radius=0.045, color=C.bg, fill_opacity=op)
    return VGroup(north, south, pin).rotate(-theta, about_point=ORIGIN).shift(P3(*COMPASS))


def _theta(t):
    """The needle swings to 68° and settles: a damped oscillation that starts when the current switches on."""
    t0 = float(T.c01_s01_twitch) - 0.1
    if t < t0:
        return 0.0
    u = t - t0
    return math.radians(68) * (1 - math.exp(-u / 0.8) * math.cos(4.6 * u))


@scene(T.c01_s01, T.c01_s02)
def s04_c01_curiosities(s):
    s.solid(C.bg, z=-200)
    chapter_card(s, 1, at=T.c01_s01 + 0.4, out=T.c01_s01_electricity - 0.6)
    add_rail(s, 1, busy=True)                                         # drawn in by the intro; carries on

    # the two fields, flowing (appear on "field")
    s.add(FramesLayer(_field_frames(), height=8.0, z=-10, opacity=fade(T.c01_s01_field, dur=1.4),
                      during=[(T.c01_s01_field - 1.0, T.c01_s02)]))

    m = s.manim(z=5)
    table = Line(P3(-5.0, -1.62), P3(-1.6, -1.62), stroke_color=C.ghost, stroke_width=2)
    sphere = _sphere()
    left = VGroup(table, sphere)
    magnet = _magnet()

    # electricity: the sphere; scraps lift onto it
    m.play(FadeIn(left, shift=0.15 * UP), at=T.c01_s01_electricity, dur=0.7)
    m.redraw(_scraps, during=(T.c01_s01_electricity, T.c01_s01_rsted + 1.0))
    # magnetism: the magnet; the nail slides in, turning to lie along the field
    m.play(FadeIn(magnet, shift=0.15 * UP), at=T.c01_s01_magnetism, dur=0.7)

    def nail(t):
        t0 = float(T.c01_s01_magnetism) + 0.5
        u = smooth01((t - t0) / 1.6) ** 2                         # accelerates as the pull grows
        x = 5.95 + (MX + sm.MAGNET_HALF + 0.56 - 5.95) * u
        y = -0.95 + (MY + 0.95) * u
        v = _exit(t)
        op = float(fade(T.c01_s01_magnetism, dur=0.7)(t)) * (1 - v)
        g = _nail(x - 1.4 * v, y, math.radians(35) * (1 - u))
        return g.set_opacity(op)
    m.redraw(nail, during=(T.c01_s01_magnetism - 0.5, T.c01_s01_rsted + 1.0))

    # Ørsted: the two drift together and give way to a wire over a compass
    m.play(FadeOut(left, shift=1.4 * RIGHT), FadeOut(magnet, shift=1.4 * LEFT), at=T.c01_s01_rsted, dur=0.9)
    rose = VGroup(Circle(radius=0.95, stroke_color=C.muted, stroke_width=2).move_to(P3(*COMPASS)),
                  *[Line(P3(COMPASS[0] + 0.82 * math.sin(a), COMPASS[1] + 0.82 * math.cos(a)),
                         P3(COMPASS[0] + 0.95 * math.sin(a), COMPASS[1] + 0.95 * math.cos(a)),
                         stroke_color=C.muted, stroke_width=2) for a in np.arange(0, 2 * math.pi, math.pi / 4)],
                  caps("n", 22, C.muted).move_to(P3(COMPASS[0] + 0.24, COMPASS[1] + 1.14)))
    wire = Line(P3(WIRE_X, -2.15), P3(WIRE_X, 3.0), stroke_color=C.mass, stroke_width=6)
    batt = VGroup(Line(P3(WIRE_X - 0.42, -2.15), P3(WIRE_X + 0.42, -2.15), stroke_color=C.light, stroke_width=4),
                  Line(P3(WIRE_X - 0.22, -2.35), P3(WIRE_X + 0.22, -2.35), stroke_color=C.light, stroke_width=9),
                  Line(P3(WIRE_X, -2.35), P3(WIRE_X, -2.95), stroke_color=C.mass, stroke_width=6))
    rig = VGroup(rose, batt)
    m.play(FadeIn(rig), at=T.c01_s01_rsted + 0.45, dur=0.8)
    w = s.manim(z=7)                                               # the wire passes over the compass
    w.play(FadeIn(wire), at=T.c01_s01_rsted + 0.45, dur=0.8)
    w.play(wire.animate.set_stroke(color=mix(C.mass, C.light, 0.6)), at=T.c01_s01_twitch - 0.1, dur=0.25)
    rig_op = fade(T.c01_s01_rsted + 0.45, dur=0.8, out=T.c01_s01_field, out_dur=0.8)
    m.redraw(lambda t: _needle(_theta(t), float(rig_op(t))), during=(T.c01_s01_rsted, T.c01_s01_field + 1.3))
    # the current: charges drifting up the wire (glowing dots)
    cur = s.manim(z=8, fx=[Glow(C.light, strength=C.glow * 0.6, radius=C.glow_r)])

    def current(t):
        t0 = float(T.c01_s01_twitch) - 0.1
        op = float(smooth01((t - t0) / 0.3)) * float(rig_op(t))
        n, y0, y1 = 9, -2.1, 3.0
        g = VGroup()
        for i in range(n):
            y = y0 + ((t - t0) * 0.9 + i * (y1 - y0) / n) % (y1 - y0)
            g.add(Dot(P3(WIRE_X, y), radius=0.035, color=C.light, fill_opacity=op))
        return g
    cur.redraw(current, during=(T.c01_s01_twitch - 0.2, T.c01_s01_field + 1.3))
    w.play(FadeOut(wire), at=T.c01_s01_field, dur=0.8)
    m.play(FadeOut(rig), at=T.c01_s01_field, dur=0.8)
    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "oersted", T.c01_s01_rsted + 0.3, C.maxwell)

    # field: the charge and the magnet return, their fields flowing around them
    sphere2 = VGroup(_sphere(), _scraps(0.0, settled=True))
    magnet2 = VGroup(_magnet(), _nail(MX + sm.MAGNET_HALF + 0.56, MY, 0.0))
    m.play(FadeIn(sphere2), FadeIn(magnet2), at=T.c01_s01_field + 0.2, dur=1.0)

    # iron filings: the magnet's field sharpens into filings; push in on the magnet
    s.camera.frame(T.c01_s01_iron_filings, center=(MX - 0.2, MY), zoom=1.5, dur=2.4)
