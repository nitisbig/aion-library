"""c04_s03 · Unsolved (payoff). Storyboard: plan/scene_plan.md § c04_s03. Layout L1.

The wake of c04_s02 gives way to three quick shots of where the equation runs: a cyclone's spiral bands over a
globe, the exact potential-flow streamlines round a wing section (Joukowski, Kutta condition; tracers move at the
true local speed), and pulsing flow in a vessel (Poiseuille profile, scaled by a heartbeat). On 'smooth' a vortex
tube twists tighter ('smooth forever?') and on 'million dollar' the prize tag shows. On 'Turbulence' a vorticity
field of swirls of every size zooms through eddies inside eddies; on 'pull' one probe point samples it and its
value draws as a jagged trace along the bottom, the bridge to Fourier.
"""
import math

import numpy as np
from aion import *
from scipy.ndimage import map_coordinates

import ch4
from beats import T
from kit import chapter_backdrop, P3, XW, YH, add_rail, caps, glow, lin_rgb, mix, polyline, sans, shade, smooth01, tag_under, tint

GC, GR = np.array([0.0, -0.15]), 2.55            # the globe
WING_S = 1.45                                    # screen units per wing unit
PIPE_A = 0.95                                    # the vessel's half width


def _srgb(lin):
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.maximum(lin, 0) ** (1 / 2.4) - 0.055)


def _rgba(lin, a):
    out = np.empty(a.shape + (4,), np.uint8)
    rgb = lin / np.maximum(a, 1e-4)[..., None]
    out[..., :3] = (np.clip(_srgb(np.clip(rgb, 0, 1)), 0, 1) * 255).astype(np.uint8)
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------ weather
def _cyclone(op, t0):
    n = 360
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)                                    # row 0 = top
    R = np.hypot(X, Y)
    disc = np.clip((1 - R) / 0.03, 0, 1)
    cx, cy = 0.18, 0.22
    r = np.hypot(X - cx, Y - cy)
    th = np.arctan2(Y - cy, X - cx)
    col = lin_rgb(mix(C.light, C.navier, 0.35))
    limb = np.sqrt(np.clip(1 - R * R, 0, 1)) ** 0.5               # dimmer toward the globe's edge

    def frame(t):
        a = float(op(t))
        u = t - t0
        arms = 0.5 + 0.5 * np.cos(2 * (th + 2.4 * np.log(r + 0.04)) + 0.9 * u)
        dens = arms ** 2.5 * np.exp(-r / 0.42) * (1 - np.exp(-(r / 0.05) ** 2)) * 1.4
        dens += 0.12 * (0.5 + 0.5 * np.cos(9 * Y + 2 * np.sin(4 * X) + 0.3 * u)) ** 4      # faint banding elsewhere
        v = np.clip(dens, 0, 1) * disc * limb * a
        return _rgba(v[..., None] * col * 0.9, v)
    return frame


def _globe():
    g = VGroup(Circle(radius=GR, stroke_color=C.ghost, stroke_width=1.8))
    for lat in (-50, -20, 10, 40, 65):
        y = GR * math.sin(math.radians(lat))
        w = GR * math.cos(math.radians(lat))
        g.add(Ellipse(width=2 * w, height=0.22 * w, stroke_color=C.ghost, stroke_width=1, stroke_opacity=0.5)
              .move_to(P3(0, y)))
    for k in (0.25, 0.6, 0.9):
        g.add(Ellipse(width=2 * GR * k, height=2 * GR, stroke_color=C.ghost, stroke_width=1, stroke_opacity=0.5))
    return g.move_to(P3(*GC))


# ------------------------------------------------------------------------------------------------ wing
def _wing_parts():
    wing, lines = ch4.joukowski()
    outline = Polygon(*[P3(*(WING_S * p)) for p in wing[::2]], stroke_color=C.light, stroke_width=2,
                      fill_color=C.card, fill_opacity=1)
    sl = VGroup(*[polyline([(WING_S * x, WING_S * y) for x, y, _ in ln[::3]], C.navier, 1.6, 0.35) for ln in lines])
    return outline, sl, lines


def _tracers(lines, op, rate=0.9, gap=0.9):
    def draw(t):
        a = float(op(t))
        g = VGroup()
        if a < 0.01:
            return g
        for k, ln in enumerate(lines):
            T_ = ln[-1, 2]
            for q in np.arange(0, T_, gap):
                tau = (q + rate * t + 0.37 * k * k) % T_
                x = np.interp(tau, ln[:, 2], ln[:, 0])
                y = np.interp(tau, ln[:, 2], ln[:, 1])
                g.add(Dot(P3(WING_S * x, WING_S * y), radius=0.028, color=C.navier, fill_opacity=a))
        return g
    return draw


# ------------------------------------------------------------------------------------------------ vessel
def _pulse(t):
    """A heartbeat-shaped flow rate, 72 per minute."""
    ph = (t % (60 / 72)) / (60 / 72)
    return 0.25 + 0.75 * np.exp(-((ph - 0.18) / 0.09) ** 2)


_TG = np.arange(0, 40, 0.005)
_I = np.cumsum(_pulse(_TG)) * 0.005                              # ∫ pulse dt


def _vessel(op, t0):
    rng = np.random.default_rng(1845)
    x0 = rng.uniform(-5, 5, 140)
    y0 = rng.uniform(-0.88, 0.88, 140) * PIPE_A
    prof_x = -3.2

    def draw(t):
        a = float(op(t))
        g = VGroup()
        if a < 0.01:
            return g
        I = float(np.interp(t - t0, _TG, _I))
        umax = 1.6
        x = (x0 + 5 + umax * (1 - (y0 / PIPE_A) ** 2) * I) % 10 - 5
        for xi, yi in zip(x, y0):
            g.add(Dot(P3(xi, yi), radius=0.03, color=C.navier, fill_opacity=a))
        p = float(_pulse(t - t0))
        ys = np.linspace(-PIPE_A * 0.9, PIPE_A * 0.9, 9)
        for y in ys:
            L = 0.9 * p * (1 - (y / PIPE_A) ** 2)
            if L > 0.06:
                g.add(Arrow(P3(prof_x, y), P3(prof_x + L, y), buff=0, stroke_width=2.6, color=C.light,
                            tip_length=0.11, max_tip_length_to_length_ratio=0.3).set_opacity(a))
        yy = np.linspace(-PIPE_A, PIPE_A, 40)
        g.add(polyline([(prof_x + 0.9 * p * (1 - (y / PIPE_A) ** 2), y) for y in yy], C.light, 1.6, 0.6 * a))
        return g
    return draw


# ------------------------------------------------------------------------------------------------ vortex tube
def _tube(t, t0, op, front):
    """A vortex tube drawn as 14 vortex lines on its surface, twisting tighter and pinching with time."""
    a = float(op(t))
    g = VGroup()
    if a < 0.01:
        return g
    u = float(smooth01((t - t0) / 5.5))
    xs = np.linspace(-4.2, 4.2, 180)
    k = 0.5 + 1.3 * u
    r = 0.85 * (1 - 0.55 * u * np.exp(-(xs / 1.4) ** 2))
    yc = 0.25 * np.sin(xs / 2.2) + 0.1
    spin = 0.8 * (t - t0)
    for j in range(10):
        ph = 2 * np.pi * j / 10 + k * xs * (1 + 0.8 * u * np.exp(-(xs / 1.4) ** 2)) + spin
        y = yc + r * np.cos(ph)
        z = r * np.sin(ph)
        sx = xs + 0.28 * z
        seg_front = z > 0
        pts = np.stack([sx, y], 1)
        # split into runs on the requested side
        mask = seg_front if front else ~seg_front
        run = []
        for p, m in zip(pts, mask):
            if m:
                run.append(p)
            elif len(run) > 1:
                g.add(polyline(run, C.navier, 2.0 if front else 1.2, a * (1.0 if front else 0.3)))
                run = []
            else:
                run = []
        if len(run) > 1:
            g.add(polyline(run, C.navier, 2.0 if front else 1.2, a * (1.0 if front else 0.3)))
    return g


# ------------------------------------------------------------------------------------------------ turbulence
@scene(T.c04_s03, T.c05_s01)
def s15_c04_unsolved(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 4, last=True)
    add_rail(s, 4, busy=True)
    t0 = float(s.start)
    t_we, t_wi, t_he, t_sm, t_mi, t_tu, t_pu = (T.c04_s03_weather, T.c04_s03_wings, T.c04_s03_heart, T.c04_s03_smooth,
                                                T.c04_s03_million_dollar, T.c04_s03_turbulence, T.c04_s03_pull)

    # c04_s02's wake, continuing as it fades
    d = ch4.street()
    h, cyl, r = ch4.street_geom(d)
    op_st = fade(t0 - 5, dur=0.1, out=t0 + 0.05, out_dur=0.55)
    cam, zm = np.array([1.6, -0.2]), 1.12                         # where c04_s02's camera drift ended
    sp = lambda p: tuple((np.asarray(p) - cam) * zm)
    s.add(FramesLayer(ch4.street_frames(d, float(T.c04_s02_obstacle) - 0.6), height=h * zm, pos=sp((0, -0.45)), z=-2,
                      opacity=op_st, parallax=0.0, during=[(s.start, t0 + 1.0)]))
    s.manim(z=3, opacity=op_st, parallax=0.0).add(Circle(radius=r * zm, stroke_color=C.ghost, stroke_width=1.6,
                                                          fill_color=C.card, fill_opacity=1).move_to(P3(*sp(cyl))))
    hud = s.manim(z=50, parallax=0.0)
    e = Eqn(r"\rho\Big(\frac{\partial\mathbf u}{\partial t}+\mathbf u\cdot\nabla\mathbf u\Big)=-\nabla p+\mu\nabla^2\mathbf u+\mathbf f",
            colors={r"\mathbf u\cdot\nabla\mathbf u": C.navier, r"-\nabla p": C.charge_p, r"\mu\nabla^2\mathbf u": C.light})
    e.scale(0.82).move_to(P3(0.55, 2.6))
    tags = VGroup(tag_under(e, r"\mathbf u\cdot\nabla\mathbf u", "carried", C.navier, 0.1),
                  tag_under(e, r"-\nabla p", "pressure", C.charge_p, 0.1),
                  tag_under(e, r"\mu\nabla^2\mathbf u", "sticky", C.light, 0.1))
    hud.add(e, tags)
    hud.play(FadeOut(VGroup(e, tags)), at=t0, dur=0.5)

    lab = lambda w: sans(w, 26, C.muted).move_to(P3(0, -3.05))
    m = s.manim(z=10)

    # weather
    op_w = fade(t0 + 0.45, dur=0.6, out=t_wi - 0.3, out_dur=0.4)
    s.add(FramesLayer(_cyclone(op_w, float(t_we)), height=2 * GR, pos=tuple(GC), z=2, during=[(t_we - 0.6, t_wi + 0.2)]))
    gl = _globe()
    s.manim(z=3, opacity=op_w).add(gl)
    s.manim(z=10, opacity=op_w).add(lab("weather"))

    # wings
    op_g = fade(t_wi - 0.3, dur=0.5, out=t_he - 0.3, out_dur=0.4)
    outline, sl, lines = _wing_parts()
    s.manim(z=4, opacity=op_g).add(sl)
    glow(s, C.navier, z=5, k=0.5).redraw(_tracers(lines, op_g), during=(t_wi - 0.4, t_he + 0.2))
    s.manim(z=6, opacity=op_g).add(outline, lab("wings"))

    # heart: blood pulsing through a vessel
    op_h = fade(t_he - 0.3, dur=0.5, out=t_sm - 0.4, out_dur=0.4)
    walls = VGroup(*[Line(P3(-5.2, y), P3(5.2, y), stroke_color=C.light, stroke_width=2.5) for y in (PIPE_A, -PIPE_A)])
    s.manim(z=6, opacity=op_h).add(walls, lab("blood in a vessel"))
    s.manim(z=5).redraw(_vessel(op_h, float(t_he)), during=(t_he - 0.4, t_sm + 0.1))

    # smooth forever? a vortex tube twisting tighter
    op_t = fade(t_sm - 0.3, dur=0.6, out=t_tu - 0.4, out_dur=0.5)
    s.manim(z=4).redraw(lambda t: _tube(t, float(t_sm), op_t, False), during=(t_sm - 0.4, t_tu + 0.2))
    glow(s, C.navier, z=5, k=0.3).redraw(lambda t: _tube(t, float(t_sm), op_t, True), during=(t_sm - 0.4, t_tu + 0.2))
    q = sans("smooth forever?", 30, C.text).move_to(P3(0, 2.1))
    prize = VGroup(Line(LEFT * 0.35, RIGHT * 0.35, stroke_color=C.navier, stroke_width=3),
                   caps("Millennium Prize · 2000", 30, C.text)).arrange(DOWN, buff=0.12).move_to(P3(0, -2.2))
    m.play(FadeIn(q, shift=0.08 * UP), at=t_sm + 0.4, dur=0.6)
    m.play(FadeIn(prize, shift=0.08 * UP), at=t_mi, dur=0.6)
    m.play(FadeOut(VGroup(q, prize)), at=t_tu - 0.4, dur=0.5)

    # turbulence: eddies inside eddies
    def op_u(t):                                                 # in on 'Turbulence', dimmed under the trace
        return float(smooth01((t - float(t_tu) + 0.4) / 0.8)) * (1 - 0.65 * float(smooth01((t - float(t_pu) - 0.2) / 1.5)))
    s.add(FramesLayer(ch4.turb_frames(op_u, float(t_tu)), height=2 * YH, pos=(0, 0), z=-5, parallax=0.0,
                      during=[(t_tu - 0.5, s.end)]))

    # pull it apart: one probe point, its value over time
    PR = ch4.PROBE
    y_tr, x_a, x_b = ch4.TRACE
    t_a, t_b = float(t_pu), float(s.end) - 0.4
    shade(s, 0.0, y_tr, 11.2, 1.3, a=0.85, z=6, parallax=0.0, opacity=fade(t_pu, dur=0.6))
    pr_op = fade(t_pu - 0.2, dur=0.5)
    glow(s, C.light, z=9, k=1.2, parallax=0.0).redraw(
        lambda t: Dot(P3(*PR), radius=0.07, color=C.light, fill_opacity=float(pr_op(t))), during=(t_pu - 0.3, s.end))
    ts_all, vals = ch4.probe_trace(float(t_tu), t_a, t_b)

    def trace(t):
        k = int(np.searchsorted(ts_all, t))
        if k < 2:
            return VGroup()
        xs = x_a + (x_b - x_a) * (ts_all[:k] - t_a) / (t_b - t_a)
        return polyline(list(zip(xs, y_tr + 0.5 * vals[:k])), C.navier, 2.4)
    glow(s, C.navier, z=8, k=0.4, parallax=0.0).redraw(trace, during=(t_pu, s.end))
    tl = s.manim(z=9, parallax=0.0)
    tl.play(FadeIn(sans("one point, over time", 22, C.muted).move_to(P3(x_a + 1.25, y_tr + 0.82))), at=t_pu + 0.5, dur=0.6)
    tl.play(FadeIn(Line(P3(x_a, y_tr), P3(x_b, y_tr), stroke_color=C.ghost, stroke_width=1.2)), at=t_pu, dur=0.5)
