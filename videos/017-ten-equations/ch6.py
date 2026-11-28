"""Chapter 6 shared pieces: the light clock (at rest and moving at 0.6 c, platform frame), the right triangle one
zig makes, the two tick timelines, the γ numbers, the muon shower, and the lit Earth with the GPS orbits.
Every position follows from the light speed on screen being the same for both clocks.

Example:
    y = rest_y(t, T_REST); x, y = moving_photon(t, T_REF)
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from aion import C
from manim import (DOWN, LEFT, RIGHT, UP, Circle, DashedLine, Dot, Line, VGroup)

import eqdata
from beats import T
from kit import P3, _lin, lin_rgb, polyline, sans, tex, tint

V = 0.6                                  # the train's speed, in units of c
H = 3.0                                  # mirror gap (world units)
CY = 0.6                                 # clock centre height
YT, YB = CY + H / 2, CY - H / 2
TAU = 2.0                                # one bounce of the clock at rest (s on screen)
GAM = eqdata.gamma(V)                    # 1.25
TAU_M = TAU * GAM                        # one bounce of the moving clock, seen from the platform
CS = H / TAU                             # the speed of light on screen
U = V * CS                               # the train's speed on screen
DXH = U * TAU_M                          # how far the train moves during one bounce (2.25)
LX = -4.6                                # the clock at rest
X_START = -2.7                           # the moving clock when its photon leaves the bottom mirror
LEG = 2                                  # the zig pulled out into a triangle (bottom → top)
TRI = (X_START + LEG * DXH, X_START + (LEG + 1) * DXH)   # its x ends: (1.8, 4.05)

T_REF = float(T.c06_s01_train) + 0.2    # the moving clock's photon leaves its bottom mirror; the tick lines start
T_REST = T_REF - 3 * TAU                 # the rest clock's photon leaves its bottom mirror (at a mirror at T_REF too)
GROUND = YB - 0.62                       # the platform
MW = 0.42                                # mirror half width
XR, KX = -5.0, 0.6                       # tick timelines: x of T_REF, screen units per second
RY = (-2.2, -2.68)                       # rows: at rest, moving


def _tri(u):
    """Triangle wave 0→1→0 with period 2 (u in bounces): height fraction of the photon."""
    f = u % 2.0
    return f if f < 1 else 2 - f


def rest_y(t, t_ref=T_REST):
    """The photon of the clock at rest; it is on the bottom mirror at t_ref (and every 2 TAU after)."""
    return YB + H * _tri((t - t_ref) / TAU)


def rest_ticks(t, t_ref=T_REST):
    return max(int(math.floor((t - t_ref) / TAU)), 0)


def train_x(t, t_ref=T_REF):
    return X_START + U * (t - t_ref)


def moving_photon(t, t_ref=T_REF):
    u = (t - t_ref) / TAU_M
    return train_x(t, t_ref), YB + H * _tri(u)


def moving_ticks(t, t_ref=T_REF):
    return max(int(math.floor((t - t_ref) / TAU_M)), 0)


def zigzag(t, t_ref=T_REF, t_from=None):
    """The photon's path on the platform up to time t (vertices), from t_from (default t_ref)."""
    a = t_ref if t_from is None else t_from
    if t <= a:
        return []
    pts = [moving_photon(a, t_ref)]
    n0 = math.floor((a - t_ref) / TAU_M) + 1
    n1 = math.floor((t - t_ref) / TAU_M)
    for n in range(n0, n1 + 1):
        pts.append(moving_photon(t_ref + n * TAU_M, t_ref))
    pts.append(moving_photon(t, t_ref))
    return pts


# ------------------------------------------------------------------------------------------------ drawing
def mirrors(x, op=1.0):
    return VGroup(*[Line(P3(x - MW, y), P3(x + MW, y), stroke_color=C.frame, stroke_width=4, stroke_opacity=op)
                    for y in (YT + 0.05, YB - 0.05)])


def ground(op=1.0):
    return Line(P3(-7.2, GROUND), P3(7.2, GROUND), stroke_color=tint(C.muted, 0.6), stroke_width=1.6,
                stroke_opacity=op)


def train(t, op=1.0):
    """The carriage under the moving clock: a floor, two wheels that roll (spokes turn with the distance)."""
    x = train_x(t)
    g = VGroup(mirrors(x, op),
               Line(P3(x - 0.85, YB - 0.3), P3(x + 0.85, YB - 0.3), stroke_color=C.muted, stroke_width=2.4,
                    stroke_opacity=op))
    r = 0.15
    ang = -(x - X_START) / r
    for dx in (-0.55, 0.55):
        c = P3(x + dx, GROUND + r)
        g.add(Circle(radius=r, stroke_color=C.muted, stroke_width=1.8, stroke_opacity=op).move_to(c))
        for k in range(2):
            a = ang + k * math.pi / 2
            g.add(Line(c - r * np.array([math.cos(a), math.sin(a), 0]), c + r * np.array([math.cos(a), math.sin(a), 0]),
                       stroke_color=C.muted, stroke_width=1.2, stroke_opacity=op))
    return g


def flash(x, y, age, color, op=1.0):
    """A tick: a small ring opening on the mirror the photon just hit (age in s)."""
    if not 0 <= age < 0.45:
        return VGroup()
    k = age / 0.45
    return Circle(radius=0.08 + 0.32 * k, stroke_color=color, stroke_width=2.2, stroke_opacity=op * (1 - k) ** 1.5) \
        .move_to(P3(x, y))


def bounce_flashes(t, t_ref, tau, xfun, color, op=1.0):
    """Flashes on each mirror hit of a clock whose photon leaves the bottom at t_ref, one bounce per tau."""
    n = math.floor((t - t_ref) / tau)
    g = VGroup()
    for k in (n, n - 1):
        if k < 1:
            continue
        tk = t_ref + k * tau
        g.add(flash(xfun(tk), YB if k % 2 == 0 else YT, t - tk, color, op))
    return g


def triangle(hyp_op=1.0):
    """The zig LEG pulled out as a right triangle: hypotenuse c Δt′ (the moving clock's light), the vertical leg
    c Δt (the same height the light climbs in the clock at rest), the base v Δt′ (how far the train moved)."""
    x0, x1 = TRI
    hyp = Line(P3(x0, YB), P3(x1, YT), stroke_color=C.dilation, stroke_width=5, stroke_opacity=hyp_op)
    vert = DashedLine(P3(x1, YB), P3(x1, YT), stroke_color=C.light, stroke_width=2.4, dash_length=0.09)
    base = Line(P3(x0, YB), P3(x1, YB), stroke_color=C.muted, stroke_width=2.6)
    sq = VGroup(Line(P3(x1 - 0.2, YB), P3(x1 - 0.2, YB + 0.2), stroke_color=C.muted, stroke_width=1.6),
                Line(P3(x1 - 0.2, YB + 0.2), P3(x1, YB + 0.2), stroke_color=C.muted, stroke_width=1.6))
    l_h = tex(r"c\,\Delta t'", 36, C.dilation).move_to(P3((x0 + x1) / 2 - 0.55, CY + 0.25))
    l_v = tex(r"c\,\Delta t", 36, C.light).next_to(P3(x1, CY), RIGHT, buff=0.14)
    l_b = tex(r"v\,\Delta t'", 36, C.muted).next_to(P3((x0 + x1) / 2, YB), DOWN, buff=0.16)
    return {"hyp": hyp, "vert": vert, "base": VGroup(base, sq), "labels": VGroup(l_h, l_v, l_b)}


def tick_x(t):
    return XR + KX * (t - T_REF)


def tick_rows(t, op=1.0, op_m=1.0):
    """The two clocks' ticks laid on one time line from the moment both photons leave their bottom mirrors."""
    g = VGroup()
    if op < 0.01:
        return g
    xe = tick_x(t)
    for y, tau, col, a in ((RY[0], TAU, C.light, op), (RY[1], TAU_M, C.dilation, op * op_m)):
        if a < 0.01:
            continue
        g.add(Line(P3(XR, y), P3(max(xe, XR + 1e-3), y), stroke_color=tint(col, 0.45), stroke_width=1.4,
                   stroke_opacity=a))
        n = int((t - T_REF) // tau)
        for k in range(0, n + 1):
            x = tick_x(T_REF + k * tau)
            grow = min((t - T_REF - k * tau) / 0.2, 1.0)
            g.add(Line(P3(x, y - 0.13 * grow), P3(x, y + 0.13 * grow), stroke_color=col, stroke_width=3,
                       stroke_opacity=a))
    return g


def row_labels():
    return VGroup(sans("at rest", 22, C.light).move_to(P3(XR - 0.25, RY[0]), aligned_edge=RIGHT),
                  sans("moving", 22, C.dilation).move_to(P3(XR - 0.25, RY[1]), aligned_edge=RIGHT))


def row_counts(t):
    n_r = int((t - T_REF) // TAU)
    n_m = int((t - T_REF) // TAU_M)
    xe = tick_x(t) + 0.35
    return VGroup(sans(f"{n_r} ticks", 22, C.light).move_to(P3(xe, RY[0]), aligned_edge=LEFT),
                  sans(f"{n_m} ticks", 22, C.dilation).move_to(P3(xe, RY[1]), aligned_edge=LEFT))


# ------------------------------------------------------------------------------------------------ γ curve
GX0, GX1, GY0, GKY = -5.6, 1.6, -2.35, 0.6          # γ graph: x of v/c = 0 and 1, y of γ = 0, units per γ
GMAX = 8.0


def g_pt(beta, gam):
    return P3(GX0 + (GX1 - GX0) * beta, GY0 + GKY * gam)


def everyday_gamma_minus_one():
    """γ − 1 for the ISS (7.66 km/s), the fastest of car, jet, ISS: about 3e-10."""
    b = 7_660.0 / eqdata.C
    return 0.5 * b * b + 0.375 * b ** 4           # series: exact γ − 1 loses digits in double precision


# ------------------------------------------------------------------------------------------------ muons
MU = eqdata.muon()                                 # γ 10.0, 655 m → 6.6 km
MU_N, MU_V = 90, 4.6                               # muons per column; screen fall speed (km per second)
MX = (-4.2, -1.0)                                  # the two columns: clocks unslowed / slowed
MU_ON = float(T.c06_s02_muons) + 0.45              # the first muon is born
MY0, MKY = -2.15, 0.30                             # y of the ground, units per km (15 km → 2.35)


@lru_cache(maxsize=1)
def muon_draw(t_on):
    """Seeded shower (same muons in both columns): spawn time, height (km), x offset and decay distance (km)
    without and with time dilation, d = −ln(u)·mean (the same random clock, run 10× slower)."""
    rng = np.random.default_rng(1905)
    ts = t_on + np.sort(rng.uniform(0, 4.2, MU_N))
    h0 = rng.uniform(13.6, 15.0, MU_N)
    dx = rng.uniform(-0.85, 0.85, MU_N)
    u = rng.uniform(1e-6, 1, MU_N)
    d0 = -np.log(u) * MU["no_dilation_m"] / 1e3
    return ts, h0, dx, d0, d0 * MU["gamma"]


def muon_state(t, t_on, slowed):
    """Per muon: y on screen (nan before its birth), alive?, decay age (s, or −1), landed?"""
    ts, h0, dx, d0, d1 = muon_draw(t_on)
    d = d1 if slowed else d0
    fall = np.maximum(t - ts, 0) * MU_V
    born = t >= ts
    t_end = ts + np.minimum(d, h0) / MU_V
    landed = born & (h0 <= d) & (t >= t_end)
    decayed = born & (h0 > d) & (t >= t_end)
    alive = born & (t < t_end)
    h = np.where(alive, h0 - fall, np.where(landed, 0.0, h0 - d))
    return MY0 + MKY * h, alive, np.where(decayed, t - t_end, -1.0), landed


def muon_column(t, t_on, slowed, op=1.0):
    ts, h0, dx, d0, d1 = muon_draw(t_on)
    y, alive, age, landed = muon_state(t, t_on, slowed)
    col = C.dilation if slowed else C.muted
    cx = MX[1] if slowed else MX[0]
    g = VGroup()
    if op < 0.01:
        return g
    for i in range(MU_N):
        x = cx + dx[i]
        if alive[i]:
            g.add(Line(P3(x, y[i] + 0.22), P3(x, y[i]), stroke_color=col, stroke_width=1.6, stroke_opacity=0.45 * op),
                  Dot(P3(x, y[i]), radius=0.035, color=col, fill_opacity=op))
        elif 0 <= age[i] < 0.5:
            k = age[i] / 0.5
            g.add(Circle(radius=0.04 + 0.16 * k, stroke_color=C.light if not slowed else col, stroke_width=1.6,
                         stroke_opacity=op * (1 - k)).move_to(P3(x, y[i])))
        elif landed[i]:
            g.add(Dot(P3(x, MY0 + 0.03), radius=0.04, color=C.dilation, fill_opacity=op))
    return g


def muon_landed(t, t_on, slowed):
    return int(muon_state(t, t_on, slowed)[3].sum())


def muon_heads():
    y = MY0 + MKY * 15.6 + 0.35
    return VGroup(sans("normal clocks", 24, C.muted).move_to(P3(MX[0], y)),
                  sans("slowed clocks", 24, C.dilation).move_to(P3(MX[1], y)))


def _brace(x, km, color):
    y1, y0 = MY0 + MKY * 15, MY0 + MKY * (15 - km)
    return VGroup(Line(P3(x, y1), P3(x, y0), stroke_color=color, stroke_width=2),
                  Line(P3(x - 0.08, y1), P3(x + 0.08, y1), stroke_color=color, stroke_width=2),
                  Line(P3(x - 0.08, y0), P3(x + 0.08, y0), stroke_color=color, stroke_width=2))


def muon_braces():
    """How far a muon gets on average from its birth: (brace, label) without and with the slowed clock."""
    b0 = _brace(MX[0] + 1.1, MU["no_dilation_m"] / 1e3, C.muted)
    l0 = sans(f"{MU['no_dilation_m'] / 1e3:.2f} km", 22, C.muted).next_to(b0, RIGHT, buff=0.12)
    b1 = _brace(MX[1] + 1.1, MU["with_dilation_m"] / 1e3, C.dilation)
    l1 = VGroup(sans(f"{MU['with_dilation_m'] / 1e3:.1f} km", 22, C.dilation),
                tex(rf"\gamma={MU['gamma']:.0f}", 26, C.dilation)).arrange(DOWN, aligned_edge=LEFT, buff=0.1) \
        .next_to(b1, RIGHT, buff=0.12)
    return VGroup(b0, l0), VGroup(b1, l1)


def ground_counts(t, t_on):
    return VGroup(sans(f"{muon_landed(t, t_on, True)} land", 22, C.dilation).move_to(P3(MX[1], MY0 - 0.4)),
                  sans("none land", 22, C.muted).move_to(P3(MX[0], MY0 - 0.4)))


def gamma_eqn():
    """Δt′ = Δt / √(1 − v²/c²) in the right column, with its two tags."""
    from aion import Eqn
    from kit import RC, tag_under
    e = Eqn(r"\Delta t'=\frac{\Delta t}{\sqrt{1-v^2/c^2}}", colors={r"\Delta t'": C.dilation, r"\Delta t": C.light})
    e.scale(0.95).move_to(P3(RC, 0.05))
    tags = VGroup(tag_under(e, r"\Delta t'", "moving", C.dilation, size=22),
                  tag_under(e, r"\Delta t", "how much slower", C.muted, size=22))   # the fraction's centre line
    return e, tags


def muon_axes(op=1.0):
    g = VGroup(Line(P3(-6.2, MY0), P3(0.7, MY0), stroke_color=C.axis, stroke_width=2, stroke_opacity=op),
               Line(P3(-6.2, MY0), P3(-6.2, MY0 + MKY * 15.6), stroke_color=C.axis, stroke_width=1.6,
                    stroke_opacity=op))
    for km in (0, 5, 10, 15):
        y = MY0 + MKY * km
        g.add(Line(P3(-6.28, y), P3(-6.12, y), stroke_color=C.axis, stroke_width=1.6, stroke_opacity=op),
              sans(f"{km}", 20, C.muted).set_opacity(op).move_to(P3(-6.4, y), aligned_edge=RIGHT))
    g.add(sans("km", 20, C.muted).set_opacity(op).move_to(P3(-6.2, MY0 + MKY * 15.6 + 0.25)))
    return g


# ------------------------------------------------------------------------------------------------ Earth + GPS
EC = np.array([-2.35, 0.05])                       # Earth's centre on screen
ER = 0.74                                          # Earth's radius on screen
ORB = eqdata.GPS_RADIUS / eqdata.R_EARTH * ER      # the GPS orbit radius on screen (true ratio 4.17)
ELEV = math.radians(17.0)                          # camera elevation
INC = math.radians(55.0)                           # GPS orbital planes: 55°, six of them, 60° apart
N_SAT = 4
SAT_RATE = 2 * math.pi / 40.0                      # one orbit per 40 s on screen
AZ_RATE = 0.05                                     # slow camera orbit (rad/s)


def _view(p, az):
    """World (Earth-centred, z = north) → screen offset (x, y) and depth (> 0 is behind Earth's centre)."""
    x, y, z = p
    ca, sa = math.cos(az), math.sin(az)
    x, y = ca * x - sa * y, sa * x + ca * y
    ce, se = math.cos(ELEV), math.sin(ELEV)
    return x, z * ce + y * se, y * ce - z * se


def orbit_point(plane, u):
    om = plane * math.pi / 3
    ci, si = math.cos(INC), math.sin(INC)
    x, y, z = math.cos(u), math.sin(u) * ci, math.sin(u) * si
    co, so = math.cos(om), math.sin(om)
    return np.array([co * x - so * y, so * x + co * y, z]) * ORB


def orbits(t, op=1.0, hi=None):
    """The six planes and their satellites, hidden behind Earth's disc, the far half dimmer. `hi` = (plane, slot) of
    the satellite to mark."""
    az = AZ_RATE * t
    g, sats = VGroup(), VGroup()
    if op < 0.01:
        return g, sats, None
    for pl in range(6):
        segs, seg, side = [], [], None                           # runs of visible points on one side (near/far)
        for u in np.linspace(0, 2 * math.pi, 145):
            sx, sy, d = _view(orbit_point(pl, u), az)
            hidden = d > 0 and sx * sx + sy * sy < ER * ER
            s_ = d > 0
            if hidden or (side is not None and s_ != side):
                if len(seg) > 1:
                    segs.append((side, seg))
                seg = [] if hidden else seg[-1:]
            if not hidden:
                seg.append((EC[0] + sx, EC[1] + sy))
                side = s_
        if len(seg) > 1:
            segs.append((side, seg))
        for far, sg in segs:
            g.add(polyline(sg, C.dilation, 1.4, op * (0.3 if far else 0.75)))
    hp = None
    for pl in range(6):
        for k in range(N_SAT):
            u = SAT_RATE * t + 2 * math.pi * k / N_SAT + 0.7 * pl
            sx, sy, d = _view(orbit_point(pl, u), az)
            if d > 0 and sx * sx + sy * sy < ER * ER:
                continue
            p = P3(EC[0] + sx, EC[1] + sy)
            sats.add(Dot(p, radius=0.05 if d <= 0 else 0.04, color=C.light, fill_opacity=op * (1 if d <= 0 else 0.6)))
            if hi == (pl, k):
                hp = p
    return g, sats, hp


def earth_frame(op_fn, n=300, spin=0.12):
    """The lit Earth as an RGBA raster: a matte sphere in a deep blue (the dilation hue, dimmed), latitude and
    longitude lines turning with Earth and the camera, a soft terminator from a light at upper left."""
    c = (np.arange(n) + 0.5) / n * 2 - 1
    sx, sy = np.meshgrid(c, -c)
    r2 = sx * sx + sy * sy
    inside = r2 < 1
    d = -np.sqrt(np.clip(1 - r2, 0, 1))                       # the near surface
    ce, se = math.cos(ELEV), math.sin(ELEV)
    yv = sy * se + d * ce
    zw = sy * ce - d * se
    L = np.array([-0.55, 0.45, -0.7])                         # light (screen x, y, toward viewer = −depth)
    L /= np.linalg.norm(L)
    lam = np.clip(sx * L[0] + sy * L[1] + (-d) * (-L[2]), 0, 1)
    base = _lin(tint(C.dilation, 0.55))
    line_col = _lin(C.dilation)
    lat = np.degrees(np.arcsin(np.clip(zw, -1, 1)))
    edge = np.clip((1 - np.sqrt(r2)) * n / 2, 0, 1)

    def frame(t):
        a = float(op_fn(t))
        az = AZ_RATE * t
        ca, sa = math.cos(-az), math.sin(-az)
        xw, yw = ca * sx - sa * yv, sa * sx + ca * yv
        lon = np.degrees(np.arctan2(yw, xw) - spin * t)
        d_lat = np.abs((lat + 15) % 30 - 15)                     # degrees to the nearest 30° line
        d_lon = np.abs((lon + 15) % 30 - 15) * np.cos(np.radians(lat))
        grid = np.clip(np.exp(-(d_lat / 1.1) ** 2) + np.exp(-(d_lon / 1.1) ** 2), 0, 1) * 0.6
        shade = 0.07 + 0.93 * lam ** 1.1
        lin = (base[None, None, :] * (1 - grid[..., None]) + line_col[None, None, :] * grid[..., None]) * shade[..., None]
        srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
        out = np.zeros((n, n, 4), np.uint8)
        out[..., :3] = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)
        out[..., 3] = (edge * inside * a * 255).astype(np.uint8)
        return out
    return frame


# ------------------------------------------------------------------------------------------------ the map
KM = 6.6 / eqdata.gps_drift()["range_error_km"]          # screen units per km: the day's 11.5 km spans 6.6 units
MAP_BOX = (-7.2, 2.6, -4.0, 4.0)                         # x0, x1, y0, y1 (the right column stays clear)


@lru_cache(maxsize=1)
def map_rgba(ppu=110, seed=1905):
    """A made-up street plan (seeded) as an RGBA raster over MAP_BOX: blocks of about 0.5 km, a few long avenues,
    a river; feathered to nothing at the right and at the frame edges, so it is never a panel."""
    from PIL import Image, ImageDraw
    x0, x1, y0, y1 = MAP_BOX
    ss = 2
    W, H_ = int((x1 - x0) * ppu), int((y1 - y0) * ppu)
    rng = np.random.default_rng(seed)
    layers = []
    def px(p):
        return ((p[0] - x0) * ppu * ss, (y1 - p[1]) * ppu * ss)

    def canvas():
        im = Image.new("L", (W * ss, H_ * ss), 0)
        return im, ImageDraw.Draw(im)
    minor, dm = canvas()
    major, dM = canvas()
    river, dr = canvas()
    step = 0.5 * KM
    for x in np.arange(x0, x1, step):
        xx = x + rng.normal(0, 0.03)
        (dM if rng.random() < 0.12 else dm).line([px((xx, y0)), px((xx, y1))], fill=255, width=ss * 1)
    for y in np.arange(y0, y1, step):
        yy = y + rng.normal(0, 0.03)
        (dM if rng.random() < 0.12 else dm).line([px((x0, yy)), px((x1, yy))], fill=255, width=ss * 1)
    for k in range(3):
        yb, sl = rng.uniform(-2.8, 2.8), rng.uniform(-0.45, 0.45)
        xs = np.linspace(x0, x1, 60)
        dM.line([px((x, yb + sl * (x + 2.3) + 0.2 * np.sin(0.7 * x + k))) for x in xs], fill=255, width=ss * 2)
    xs = np.linspace(x0, x1, 240)
    dr.line([px((x, -2.35 + 0.5 * np.sin(0.45 * x + 0.6) + 0.16 * np.sin(1.3 * x))) for x in xs], fill=255,
            width=ss * 9)
    a = [np.asarray(im.resize((W, H_), Image.LANCZOS), np.float32) / 255 for im in (minor, major, river)]
    cols = [lin_rgb(C.muted) * 0.16, lin_rgb(C.muted) * 0.45, lin_rgb(C.dilation) * 0.22]
    alpha = np.clip(a[0] * 0.18 + a[1] * 0.5 + a[2] * 0.3, 0, 1)
    lin = sum(ai[..., None] * c for ai, c in zip(a, cols))
    xs = np.linspace(x0, x1, W)[None, :]
    ys = np.linspace(y1, y0, H_)[:, None]
    feather = np.clip((x1 - 0.2 - xs) / 1.8, 0, 1) * np.clip((xs - x0) / 0.8, 0, 1) * \
        np.clip((y1 - np.abs(ys)) / 0.8, 0, 1)
    feather = feather * feather * (3 - 2 * feather)
    rgb = lin / np.maximum(alpha, 1e-4)[..., None]
    srgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.clip(rgb, 0, 1) ** (1 / 2.4) - 0.055)
    out = np.zeros((H_, W, 4), np.uint8)
    out[..., :3] = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)
    out[..., 3] = (np.clip(alpha * feather * 1.6, 0, 1) * 255).astype(np.uint8)
    return out


PIN0 = np.array([-4.9, 0.75])                            # where the phone really is
PIN_DIR = np.array([math.cos(math.radians(-10)), math.sin(math.radians(-10))])


def pin(p, color, op=1.0, hollow=False):
    """A map pin whose tip sits on p."""
    x, y = p
    head = Circle(radius=0.17, stroke_color=color, stroke_width=3, fill_color=color if not hollow else C.bg,
                  fill_opacity=op if not hollow else op, stroke_opacity=op).move_to(P3(x, y + 0.42))
    tip = VGroup(Line(P3(x - 0.13, y + 0.31), P3(x, y), stroke_color=color, stroke_width=3, stroke_opacity=op),
                 Line(P3(x + 0.13, y + 0.31), P3(x, y), stroke_color=color, stroke_width=3, stroke_opacity=op))
    return VGroup(tip, head)


# ------------------------------------------------------------------------------------------------ the next hill
LS = 1.05                                                # screen units per loss-landscape unit (sims.loss)


@lru_cache(maxsize=1)
def loss_contours(levels=14):
    """Contour lines of sims.loss over [−3, 3]² in screen units (the hill of chapter 7), low to high."""
    import contourpy
    import sims as sm
    g = np.linspace(-3, 3, 241)
    X, Y = np.meshgrid(g, g)
    Z = sm.loss(X, Y)
    gen = contourpy.contour_generator(X, Y, Z)
    out = []
    for lv in np.linspace(Z.min() + 0.03, Z.max() - 0.05, 3 * levels):
        for ln in gen.lines(lv):
            if len(ln) > 8 and np.allclose(ln[0], ln[-1]):          # closed loops only: no lines cut by the box
                out.append((lv, ln * LS))
    keep = sorted({l for l, _ in out})
    keep = set(keep[::max(len(keep) // levels, 1)])
    out = [(l, ln) for l, ln in out if l in keep]
    return out
