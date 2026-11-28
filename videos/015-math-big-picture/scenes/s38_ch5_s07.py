"""ch5_s07 · Small changes, added up (sighting, takeaway, map turn).

On 'weather' a globe of latitude and longitude lines (C.circle) turns slowly with pressure contours (C.change) drawn on
it; on 'step by step' the contours step forward, tagged +1 h, +2 h, +3 h. On 'For a circle' the hero comes back: the
circle grows its thin ring, which unrolls into the strip below, 2πr long, and dA/dr = 2πr is written. The map returns
around the circle as Chapter 4 left it, the strip shrinks into Change at the bottom, which lights on 'Change'; on
'derivatives' the chords Space–Change and Quantity–Change draw, and the ring turns its sixth (240° → 300°).
"""
import math

import contourpy
import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, rgb255, tint, HUB_R, NODE_R, P3, map_state, node, node_xy, tex, the_circle, window, hub_at, turn_view

LIT = ("foundations", "quantity", "structure", "space")
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"))
NEW = (("space", "change"), ("quantity", "change"))
GC, GR, TILT = P3(0.0, -0.1), 2.5, math.radians(22)
DR = 0.2
STRIP_Y = -2.5

# the pressure field on a lon/lat grid: a few lows and highs drifting east
LON = np.linspace(-math.pi, math.pi, 181)
LAT = np.linspace(-1.35, 1.35, 91)
LL, PP = np.meshgrid(LON, LAT)
CENTRES = [(-2.4, 0.75, 1.0), (-0.9, 0.95, -1.0), (0.4, 0.6, 1.0), (1.7, 0.85, -1.0), (2.9, 0.5, 1.0),
           (-1.8, -0.7, -1.0), (0.9, -0.8, 1.0), (2.4, -0.6, -1.0), (-0.2, 0.15, -0.6)]


def field(step):
    z = np.zeros_like(LL)
    for lon0, lat0, a in CENTRES:
        lon = lon0 + 0.22 * step
        dl = np.angle(np.exp(1j * (LL - lon)))
        d2 = (dl * np.cos(PP)) ** 2 + (PP - lat0) ** 2
        z += a * np.exp(-d2 / 0.32)
    return z


def project(lon, lat, spin):
    """(lon, lat) → view (x, y) on the globe's disc and depth z (> 0 faces us)."""
    lp = lon + spin
    x, y, z = np.cos(lat) * np.sin(lp), np.sin(lat), np.cos(lat) * np.cos(lp)
    y2, z2 = y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT)
    return x, y2, z2


def runs(lon, lat, spin, color, width, op):
    x, y, z = project(np.asarray(lon), np.asarray(lat), spin)
    g, cur = VGroup(), []
    for xi, yi, zi in zip(x, y, z):
        if zi > 0.02:
            cur.append(GC + GR * P3(xi, yi))
        else:
            if len(cur) > 1:
                g.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=op).set_points_as_corners(cur))
            cur = []
    if len(cur) > 1:
        g.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=op).set_points_as_corners(cur))
    return g


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def layer(rho, u, base_pt, n=160):
    L = 2 * math.pi * rho
    s = np.linspace(-L / 2, L / 2, n)
    k = (1 - u) / rho
    if k < 1e-6:
        x, y = s, np.zeros_like(s)
    else:
        x, y = np.sin(k * s) / k, (1 - np.cos(k * s)) / k
    return np.stack([x, y, np.zeros_like(s)], -1) + base_pt


@scene(T.ch5_s07, T.ch6_s01)
def ch5_s07(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, nd, m, top = glow_layer(s, z=-2, k=0.55), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_we, t_fc, t_int = float(T.ch5_s07_weather), float(T.ch5_s07_for_a_circle), float(T.ch5_s07_integrals)
    t_steps = (t_we + 4.44, t_we + 5.04, t_we + 5.72)                       # 'worked' 'step' 'step'
    t_edge, t_ch, t_der = t_fc + 3.29, t_fc + 5.07, t_fc + 6.49             # 'own edge' 'Change' 'derivatives'
    Ch = C.change
    g_out = t_fc - 0.9

    # the globe, its contours stepping forward
    def step_at(t):
        return sum(ss((t - ts) / 0.45) for ts in t_steps)

    def globe(t):
        f = ss((t - t0 - 0.1) / 0.7) * (1 - ss((t - g_out) / 0.6))
        if f <= 0:
            return VGroup()
        spin = 0.5 + 0.06 * (t - t0)
        g = VGroup(Circle(radius=GR, stroke_color=C.circle, stroke_width=1.6, stroke_opacity=0.4 * f).move_to(GC))
        for lat in np.radians([-60, -30, 0, 30, 60]):
            g.add(runs(np.linspace(-math.pi, math.pi, 181), np.full(181, lat), spin, C.circle, 1.1, 0.22 * f))
        for lon in np.radians(np.arange(-180, 180, 30)):
            g.add(runs(np.full(91, lon), np.linspace(-math.pi / 2, math.pi / 2, 91), spin, C.circle, 1.1, 0.22 * f))
        return g

    def contours(t):
        f = ss((t - t0 - 0.1) / 0.7) * (1 - ss((t - g_out) / 0.6))
        c = ss((t - t_we + 0.1) / 0.8) * f
        g = VGroup()
        if c > 0:
            spin = 0.5 + 0.06 * (t - t0)
            gen = contourpy.contour_generator(LON, LAT, field(step_at(t)))
            for lev in (-0.55, -0.3, 0.3, 0.55, 0.8):
                for ln in gen.lines(lev):
                    g.add(runs(ln[:, 0], ln[:, 1], spin, Ch, 2.6 if abs(lev) > 0.5 else 1.8, c))
        return g

    # the planet itself: a lit sphere painted with the same pressure field (highs warm, lows cool)
    NP = 360
    half = GR * 1.14
    ax_ = np.linspace(-half, half, NP)
    XX, YY = np.meshgrid(ax_ / GR, -ax_ / GR)
    R2 = XX ** 2 + YY ** 2
    inside = R2 < 1
    ZZ = np.sqrt(np.clip(1 - R2, 0, 1))
    yv = YY * math.cos(TILT) + ZZ * math.sin(TILT)                     # undo the tilt
    zv = -YY * math.sin(TILT) + ZZ * math.cos(TILT)
    LATP = np.arcsin(np.clip(yv, -1, 1))
    LP = np.arctan2(XX, zv)
    Lv = np.array([-0.5, 0.55, 0.67])
    Lv = Lv / np.linalg.norm(Lv)
    Hv = Lv + np.array([0, 0, 1.0])
    Hv = Hv / np.linalg.norm(Hv)
    dif = np.clip(XX * Lv[0] + YY * Lv[1] + ZZ * Lv[2], 0, 1)
    spec = np.clip(XX * Hv[0] + YY * Hv[1] + ZZ * Hv[2], 0, 1) ** 40
    rim = (1 - ZZ) ** 3
    rr_ = np.sqrt(R2)
    halo = np.exp(-np.clip(rr_ - 1, 0, None) / 0.035) * (rr_ >= 1)           # thin atmosphere outside the limb

    def rgbf(c_):
        return np.array(rgb255(c_), np.float32) / 255.0

    ocean, warm, cool = rgbf(tint(C.foundations, 0.035)), rgbf(tint(Ch, 0.32)), rgbf(tint(C.foundations, 0.22))
    air, sun = rgbf(tint(C.foundations, 0.7)), rgbf(C.circle)

    def planet(t):
        f = ss((t - t0 - 0.1) / 0.7) * (1 - ss((t - g_out) / 0.6))
        c = ss((t - t_we + 0.1) / 0.8)
        spin = 0.5 + 0.06 * (t - t0)
        lon = np.angle(np.exp(1j * (LP - spin)))
        fz = field(step_at(t))
        i_lon = np.clip(((lon + math.pi) / (2 * math.pi) * 180).astype(int), 0, 180)
        i_lat = np.clip(((LATP + 1.35) / 2.7 * 90).astype(int), 0, 90)
        pz = np.clip(fz[i_lat, i_lon], -1, 1) * c
        alb = (ocean[None, None] + np.clip(pz, 0, 1)[..., None] * warm[None, None]
               + np.clip(-pz, 0, 1)[..., None] * cool[None, None])
        col = alb * (0.12 + 0.95 * dif)[..., None] + sun[None, None] * (0.55 * spec)[..., None] \
            + air[None, None] * (0.55 * rim)[..., None]
        col = np.where(inside[..., None], col, air[None, None] * (0.6 * halo)[..., None])
        a = np.where(inside, 1.0, 0.6 * halo) * f
        out = np.empty((NP, NP, 4), np.uint8)
        out[..., :3] = (np.clip(col, 0, 1) * a[..., None] * 255).astype(np.uint8)
        out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
        return out

    s.add(FramesLayer(planet, height=2 * half, pos=tuple(GC[:2]), during=[(t0, g_out + 0.7)], premultiplied=True,
                      z=-0.5))
    m.redraw(window(globe, t0, g_out + 0.65), during=(t0, g_out + 0.7))
    glow_layer(s, z=0.3, color=Ch, k=0.8).redraw(window(contours, t0, g_out + 0.65), during=(t0, g_out + 0.7))

    def hours(t):
        n = int(round(step_at(t)))
        f = ss((t - t_steps[0] + 0.3) / 0.3) * (1 - ss((t - g_out) / 0.5))
        if n < 1 or f <= 0:
            return VGroup()
        return tex(rf"+{n}\ \mathrm{{h}}", 48, Ch).move_to(P3(4.6, 2.4)).set_opacity(f)

    top.redraw(window(hours, t_steps[0] - 0.3, g_out + 0.55), during=(t_steps[0] - 0.3, g_out + 0.6))

    # 'For a circle': the hero, its ring unrolled into the strip
    circ = the_circle(HUB_R)
    m.play(Create(circ), at=t_fc - 0.4, dur=0.8, ease="easy_ease")
    t_g, t_u = t_fc + 0.4, t_fc + 1.2
    sp = node_xy(4, turn=240)

    def ring(t):
        g, u = ss((t - t_g) / 0.6), ss((t - t_u) / 1.6)
        w = ss((t - t_edge - 0.9) / 0.9)                                  # then into Change
        if g <= 0:
            return VGroup()
        if u <= 0:
            return VGroup(Annulus(inner_radius=HUB_R, outer_radius=HUB_R + DR * g, fill_color=Ch, fill_opacity=0.55,
                                  stroke_color=Ch, stroke_width=2))
        ua = ss(min(1.0, 1.7 * u))
        b_in = (1 - ua) * P3(0, -HUB_R) + ua * P3(0, STRIP_Y)
        b_out = (1 - ua) * P3(0, -HUB_R - DR) + ua * P3(0, STRIP_Y - DR)
        inner, outer = layer(HUB_R, u, b_in), layer(HUB_R + DR, u, b_out)
        pts = np.vstack([inner, outer[::-1]])
        if w > 0:                                                         # shrink into the node
            pts = (1 - w) * pts + w * (sp + (pts - pts.mean(0)) * 0.04)
        poly = Polygon(*pts, fill_color=Ch, fill_opacity=0.55 * (1 - w), stroke_color=Ch, stroke_width=2,
                       stroke_opacity=1 - w)
        return VGroup(poly)

    top.redraw(window(ring, t_g, t_ch + 0.1), during=(t_g, t_ch + 0.15))
    rate = MathTex(r"\frac{dA}{dr}", "=", r"2\pi r", font_size=54, color=C.text)
    rate[0].set_color(Ch)
    rate[2].set_color(C.circle)
    rate.move_to(P3(5.1, 2.65))
    m.play(Write(rate), at=t_edge - 0.4, dur=0.8)
    m.play(FadeOut(rate), at=t_der - 0.4, dur=0.5)

    # the map returns around the circle; Change lights; two chords
    links, nodes = map_state(240, lit=LIT, edges=EDGES)
    hub = hub_at(240)
    t_map = t_edge + 0.5
    lnk.play(FadeIn(links), at=t_map, dur=0.8)
    nd.play(LaggedStart(*(GrowFromCenter(n_) for n_ in nodes), lag_ratio=0.06), at=t_map, dur=0.9)
    m.add(hub, at=t_map)
    m.remove(circ, at=t_map)
    nd.play(Transform(nodes[4], node(4, lit=True, turn=240)), at=t_ch, dur=0.5)
    ping = Circle(radius=0.4, stroke_color=Ch, stroke_width=3).move_to(sp)
    top.play(ping.animate.scale(2.2).set_stroke(opacity=0), at=t_ch + 0.05, dur=0.8)
    top.remove(ping, at=t_ch + 0.9)
    new_edges = map_state(240, edges=NEW)[0][1]
    lnk.play(LaggedStart(*(Create(e_) for e_ in new_edges), lag_ratio=0.4), at=t_der - 0.2, dur=0.9)

    # the signature turn, 240° → 300°
    t_turn = t_int - 0.4
    turn_d = t1 - 0.05 - t_turn
    lit = LIT + ("change",)

    def deg(t):
        return 240 + 60 * ss((t - t_turn + 0.15) / turn_d)

    def TV(t):
        return turn_view((t - t_turn + 0.15) / turn_d, 50, 0)

    def ring_at(t):
        return map_state(deg(t), lit=lit, view=TV(t))[1]

    def links_at(t):
        return map_state(deg(t), edges=EDGES + NEW, view=TV(t))[0]

    lnk.remove(links, *new_edges, at=t_turn - 0.15)               # Create added each chord on its own
    nd.remove(*nodes, at=t_turn - 0.15)
    nd.redraw(window(ring_at, t_turn - 0.15, t1), during=(t_turn - 0.15, t1))
    m.remove(hub, at=t_turn - 0.15)
    m.redraw(window(lambda t: hub_at(deg(t), TV(t)), t_turn - 0.15, t1), during=(t_turn - 0.15, t1))
    lnk.redraw(window(links_at, t_turn - 0.15, t1), during=(t_turn - 0.15, t1))
