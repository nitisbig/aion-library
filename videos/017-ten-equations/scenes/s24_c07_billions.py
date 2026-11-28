"""c07_s03 · Billions of knobs (payoff). Storyboard: plan/scene_plan.md § c07_s03. Layout L1.

Opens on c07_s02's last frame (the fitted line and its error map), which gives way to a wide rugged landscape
(shaders/hill.frag mode 1, ch7.rugged) under a slow crane. 'billions': the knob count runs from 2 to a billion and
1600 walkers are scattered over the ground. 'directions': a burst of directions from one point, far more than the
two a hill has. 'rule': the same rule writes again and every walker follows it (ch7.swarm: exact gradient steps,
seeded, with a little noise that dies away), pouring into the valleys below it. 'cables': the landscape leaves,
and the deepest walker sends its answer out along a cable as a train of bits; 'noise' frays it.
"""
import math

import numpy as np
from aion import *

import ch7
import ch8
from beats import T
from kit import chapter_backdrop, P3, RC, X0, Y1, add_rail, glow, mix, polyline, sans, smooth01, tag_under, tex, tint



def cam_at(t):
    u = (t - float(T.c07_s03)) / (float(T.c07_s03_cables) - float(T.c07_s03))
    return ch7.Cam(target=(0.0, 0.2, 0.0), yaw=-2.15 + 0.5 * u, pitch=math.radians(38 + 6 * u), dist=16.5 - 2.0 * u,
                   off=(0.0, -0.35))


def _visible(cam, P3d):
    """Hide walkers behind a ridge: sample the sight line and test it against the ground."""
    eye = cam.basis()[0]
    s = np.linspace(0.08, 0.94, 12)[None, :, None]
    Q = eye[None, None, :] + (P3d[:, None, :] - eye[None, None, :]) * s
    h = ch7.ZS_R * ch7.rugged(Q[..., 0], Q[..., 1])
    return ~(Q[..., 2] < h - 0.03).any(1)


def _carry(s, out):
    """c07_s02's last frame: points, fitted line and gaps, the error map with its path and ring, the error bar."""
    prev = ch7
    t = float(s.start)
    op = fade(t - 5, dur=0.1, out=out, out_dur=0.8)
    x, y = ch7.fit_data()
    mm, bb = ch7.fit_path()[-1]
    m = s.manim(z=6, opacity=op)
    m.add(Line(P3(*prev.sc(-2.6, 0)), P3(*prev.sc(2.6, 0)), stroke_color=tint(C.muted, 0.6), stroke_width=1.4),
          Line(P3(*prev.sc(0, -1.6)), P3(*prev.sc(0, 2.4)), stroke_color=tint(C.muted, 0.6), stroke_width=1.4),
          *[Line(P3(*prev.sc(a, b)), P3(*prev.sc(a, mm * a + bb)), stroke_color=C.muted, stroke_width=1.6,
                 stroke_opacity=0.8) for a, b in zip(x, y)],
          *[Dot(P3(*prev.sc(a, b)), radius=0.07, color=C.data) for a, b in zip(x, y)],
          prev.contours(), tex("m", 32, C.muted).move_to(P3((prev.MAP[0] + prev.MAP[1]) / 2, prev.MAP[2] - 0.32)),
          tex("b", 32, C.muted).move_to(P3(prev.MAP[0] - 0.3, (prev.MAP[2] + prev.MAP[3]) / 2)),
          Circle(radius=0.2, stroke_color=mix(C.descent, C.light, 0.5), stroke_width=2).move_to(P3(*prev.mp(mm, bb))))
    L0 = float(ch7.fit_loss(*ch7.fit_path()[0]))
    h = prev.BAR_H * float(ch7.fit_loss(mm, bb)) / L0
    m.add(Rectangle(width=0.22, height=max(h, 0.01), stroke_width=0, fill_color=C.descent, fill_opacity=1)
          .move_to(P3(prev.BAR_X, prev.BAR_Y0 + h / 2)),
          tex("L", 28, C.descent).move_to(P3(prev.BAR_X, prev.BAR_Y0 - 0.28)))
    xs = np.linspace(-2.6, 2.6, 200)
    ys = mm * xs + bb
    k = (ys > -1.8) & (ys < 2.6)
    glow(s, C.descent, z=7, k=1.1, opacity=op).add(
        polyline([tuple(prev.sc(a, b)) for a, b in zip(xs[k], ys[k])], C.descent, 4))
    P = ch7.fit_path()
    pc = mix(C.descent, C.light, 0.5)
    glow(s, C.descent, z=8, k=0.6, opacity=op).add(
        polyline([tuple(prev.mp(*q)) for q in P], pc, 2, 0.8),
        *[Dot(P3(*prev.mp(*q)), radius=0.035, color=pc, fill_opacity=0.8) for q in P[:-1]],
        Dot(P3(*prev.mp(*P[-1])), radius=0.08, color=pc))
    L = Eqn(r"L(m,b)=\frac{1}{n}\sum_i\,(y_i-m\,x_i-b)^2", colors={"L(m,b)": C.descent})
    L.scale(0.8).move_to(P3((prev.MAP[0] + prev.MAP[1]) / 2, 2.25))
    s.manim(z=50, parallax=0.0, opacity=op).add(L, tag_under(L, "L(m,b)", "error", C.descent))


@scene(T.c07_s03, T.c08_s01)
def s24_c07_billions(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 7, last=True)
    t0 = float(s.start)
    t_bi, t_di, t_ru, t_ca, t_no = (T.c07_s03_billions, T.c07_s03_directions, T.c07_s03_rule, T.c07_s03_cables,
                                    T.c07_s03_noise)
    _carry(s, t0 + 0.25)
    add_rail(s, 7, busy=True)

    # the wide landscape
    land_op = fade(t0 + 0.5, dur=1.4, out=t_ca - 0.1, out_dur=1.1)
    s.shader("hill.frag", z=0, parallax=0.0, animated=True,
             **ch7.hill_uniforms(cam_at, mode=1, opacity=land_op, fog=0.0, walker=(0.0, 0.0), fr=1.0))

    # billions of knobs
    hud = s.manim(z=50, parallax=0.0)

    def knobs(t):
        u = float(smooth01((t - float(t_bi) - 0.2) / 1.8))
        n = int(round(2 * (1e9 / 2) ** u))
        n = 1_000_000_000 if u >= 1 else n
        a = float(fade(t_bi - 0.2, dur=0.5, out=t_ca - 0.4, out_dur=0.6)(t))
        return VGroup(sans(f"{n:,}".replace(",", " "), 40, C.descent), sans("knobs", 24, C.muted)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(P3(X0, Y1), aligned_edge=UL).set_opacity(a)
    hud.redraw(knobs, during=(t_bi - 0.4, t_ca + 0.4))

    # the walkers, scattered, then pouring downhill
    t_r = float(t_ru) + 0.2
    sw_a = fade(t_bi + 0.3, dur=1.0, out=t_ca - 0.1, out_dur=1.1)

    def swarm_xy(t):
        cam = cam_at(t)
        xy = ch7.swarm_at(max(t - t_r, 0.0) * 24.0)
        P = ch7.on_rugged(xy, lift=0.04)
        q = cam.project(P)
        vis = _visible(cam, P) & ~np.isnan(q).any(1)
        return np.where(vis[:, None], q, 99.0)
    s.add(PointsLayer(swarm_xy, color=C.light, size=2.4, glow=0.3, alpha=sw_a, z=3, parallax=0.0))

    # billions of directions: far more ways to step than the two a hill has
    rng = np.random.default_rng(7)
    ang = rng.uniform(0, 2 * np.pi, 180)
    ln = rng.uniform(0.4, 2.3, 180) * rng.uniform(0.35, 1.0, 180)
    d_op = fade(t_di - 0.2, dur=0.6, out=t_ru + 0.8, out_dur=0.6)

    def burst(t):
        a = float(d_op(t))
        if a < 0.01:
            return VGroup()
        c = cam_at(t).project(ch7.on_rugged(np.array([[0.4, 0.9]]), lift=0.1))[0]
        g = float(smooth01((t - float(t_di) + 0.2) / 0.9))
        return VGroup(*[Line(P3(*c), P3(*(c + g * l * np.array([math.cos(q), 0.62 * math.sin(q)]))),
                             stroke_color=C.descent, stroke_width=1.2, stroke_opacity=a * 0.55)
                        for q, l in zip(ang, ln)], Dot(P3(*c), radius=0.07, color=C.light, fill_opacity=a))
    glow(s, C.descent, z=4, k=0.4, parallax=0.0).redraw(burst, during=(t_di - 0.4, t_ru + 1.6))

    # the same rule
    e = Eqn(r"\theta\leftarrow\theta-\eta\,\nabla L(\theta)", colors={r"\nabla L": C.descent, r"\eta": C.text})
    e.scale(0.95).move_to(P3(RC, 2.85))
    hud.play(FadeIn(e, shift=0.06 * DOWN), at=t_ru - 0.1, dur=0.7)
    hud.play(FadeOut(e), at=t_ca - 0.4, dur=0.6)

    # cables: the answer leaves as bits, and the wire adds noise (ch8.cable_*: chapter 8 opens on this frame)
    w_op = fade(t_ca + 0.3, dur=0.6)
    glow(s, C.shannon, z=8, k=0.3, parallax=0.0).redraw(lambda t: ch8.cable_wave(t, float(w_op(t))),
                                                       during=(t_ca, s.end))
    line, emit = ch8.cable_static()
    s.manim(z=7, parallax=0.0, opacity=w_op).add(line)
    glow(s, C.descent, z=9, k=0.8, parallax=0.0, opacity=w_op).add(emit)
    s.manim(z=9, parallax=0.0).redraw(lambda t: ch8.cable_bits(t, float(w_op(t))), during=(t_ca, s.end))
    nl = sans("noise", 24, C.noise).move_to(P3(3.6, ch8.CABLE_Y - ch8.AMP - 0.5))
    hud.play(FadeIn(nl), at=t_no + 0.3, dur=0.5)
