"""c10_s03 · A map, not the world (payoff). Storyboard: plan/scene_plan.md § c10_s03. Layout L1.

Opens on c10_s02's last frame (the heat equation over Fourier's cooling bar), which gives way to the value surface
V(S, τ) from the Black–Scholes closed form (shaders/hill.frag mode 2, price across, time to expiry back), under a
slow orbit; at expiry its edge is the hockey stick (ch10.call). 'Nobel': tag. 'calmly': a calm price path rides the
surface towards expiry (a seeded GBM path). 'jump': a second path falls 30 % at once, leaves the surface, and the
surface flickers. 'map': the surface flattens into its contour map, seen from above, and the camera pulls back.
"""
import math

import numpy as np
from aion import *

import ch10
from ch7 import Cam, FOCAL
from beats import T
from kit import chapter_backdrop, P3, add_rail, glow, polyline, sans, smooth01, tag_under


def _carry(s, out):
    op = fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.8)
    heat = Eqn(r"\frac{\partial u}{\partial \tau}=\frac{\partial^2 u}{\partial x^2}",
               colors={r"\frac{\partial^2 u}{\partial x^2}": C.fourier})
    heat.scale(1.3).move_to(P3(0, 1.2))
    s.manim(z=50, parallax=0.0, opacity=op).add(
        heat, tag_under(heat, r"\frac{\partial^2 u}{\partial x^2}", "heat equation", C.fourier))
    t_on = float(T.c10_s02_bar_of_hot_metal) - 0.3
    s.manim(z=3, parallax=0.0).redraw(lambda t: ch10.hot_bar(t, t_on, op), during=(s.start, out + 0.9))


@scene(T.c10_s03, T.out_s01)
def s33_c10_map(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 10, last=True)
    t0 = float(s.start)
    t_mk, t_nb, t_ca, t_ju, t_mp = (T.c10_s03_market, T.c10_s03_nobel, T.c10_s03_calmly, T.c10_s03_jump,
                                    T.c10_s03_map)
    _carry(s, t0 + 0.3)
    add_rail(s, 10, busy=True)
    hud = s.manim(z=50, parallax=0.0)

    # the camera: a slow orbit, then (on 'map') straight down and pulling back
    t_fl = float(t_mp) - 0.2
    flat = lambda t: float(smooth01((t - t_fl) / 1.4))
    back = lambda t: float(smooth01((t - t_fl - 0.9) / 2.4))

    def cam(t):
        u = (t - t0) / (t_fl - t0)
        f = flat(t)
        yaw = (-2.05 + 0.45 * u) * (1 - f) + (-math.pi / 2) * f
        pitch = math.radians(35 + 3 * u) * (1 - f) + math.radians(89.5) * f
        dist = (13.8 - 1.0 * u) * (1 - f) + 10.5 * f
        dist *= 1 + 2.2 * back(t)
        return Cam(target=(0.0, 0.0, 0.85 * (1 - f)), yaw=yaw, pitch=pitch, dist=dist, f=FOCAL,
                   off=(-0.4 * (1 - f), 0.45 * (1 - f)))

    zs = lambda t: 1.0 - flat(t)
    flick = lambda t: 1.0 - 0.45 * (0.5 + 0.5 * math.sin((t - float(t_ju)) * 40)) * \
        float(fade(t_ju, dur=0.05, out=t_ju + 0.7, out_dur=0.3)(t))
    s_op = Track(lambda t: float(fade(t0 + 0.4, dur=1.2)(t)) * flick(t))
    unif = ch10.surf_uniforms(cam, zs, s_op)
    unif["u_dom"] = 3.3                                    # draw a little past the expiry edge, so it is not faded
    s.shader("hill.frag", z=0, parallax=0.0, animated=True, **unif)

    # at expiry, the edge of the surface is the hockey stick
    Sx = np.linspace(ch10.surf_S(-3.0), ch10.surf_S(3.0), 120)
    e_op = fade(t_mk - 0.3, dur=0.8, out=t_mp - 0.4, out_dur=0.5)

    def edge(t):
        a = float(e_op(t))
        if a < 0.01:
            return VGroup()
        q = cam(t).project(ch10.on_surface(Sx, 1e-4, zs(t), lift=0.02))
        return polyline([tuple(v) for v in q if not np.isnan(v).any()], C.payoff, 3.2, a)
    glow(s, C.payoff, z=4, k=0.7, parallax=0.0).redraw(edge, during=(t_mk - 0.4, t_mp))

    def labels(t):
        a = float(fade(t_mk + 0.2, dur=0.6, out=t_mp - 0.4, out_dur=0.5)(t))
        if a < 0.01:
            return VGroup()
        c = cam(t)
        p1 = c.project(ch10.on_surface(np.array([205.0]), 1e-4, zs(t)))[0]
        p2 = c.project(np.array([[-3.45, 0.0, 0.0]]))[0]
        p3 = c.project(ch10.on_surface(np.array([175.0]), 1e-4, zs(t)))[0]
        return VGroup(sans("price", 22, C.muted).move_to(P3(*(p1 + np.array([0.45, -0.1])))),
                      sans("time left", 22, C.muted).move_to(P3(*(p2 + np.array([-0.55, -0.1])))),
                      sans("at expiry", 22, C.payoff).move_to(P3(*(p3 + np.array([0.95, -0.3]))))).set_opacity(a)
    s.manim(z=50, parallax=0.0).redraw(labels, during=(t_mk, t_mp))
    lab = s.manim(z=50, parallax=0.0, opacity=fade(t0, dur=0.1, out=t_mp - 0.4, out_dur=0.5))
    lab.play(FadeIn(sans("option value", 26, C.bs).move_to(P3(3.9, 2.6))), at=t_mk + 0.4, dur=0.6)

    # calmly: a path riding the surface to expiry; jump: one that falls off it
    tt, S = ch10.paths(12)
    j = int(np.argmin([abs(S[-1, k] - 140) + 100 * (S[:, k].min() < 60) for k in range(S.shape[1])]))
    calm = S[:, j]
    cut = int(0.45 * (len(tt) - 1))
    jumpy = np.where(np.arange(len(tt)) >= cut, calm * 0.68, calm)              # a 32 % fall in an instant
    tau = 1 - tt
    p_op = fade(t_ca - 0.2, dur=0.4, out=t_mp - 0.4, out_dur=0.5)

    RIDE = 2.0

    def ride(path, t_start, color, t, lift=0.05):
        u = float(np.clip((t - t_start) / RIDE, 0, 1))                # linear, so the fall lands on its beat
        k = max(int(u * (len(tt) - 1)), 1)
        q = cam(t).project(ch10.on_surface(path[:k + 1], tau[:k + 1], zs(t), lift=lift))
        return q

    def calm_path(t):
        a = float(p_op(t))
        if a < 0.01 or t < float(t_ca) - 0.1:
            return VGroup()
        q = ride(calm, float(t_ca) - 0.1, C.light, t)
        return VGroup(polyline([tuple(v) for v in q], C.light, 2.6, a), Dot(P3(*q[-1]), radius=0.06, color=C.light,
                                                                              fill_opacity=a))
    glow(s, C.light, z=5, k=0.6, parallax=0.0).redraw(calm_path, during=(t_ca - 0.3, t_mp))

    def jump_path(t):
        a = float(fade(t_ju - 0.45 * RIDE, dur=0.3, out=t_mp - 0.4, out_dur=0.5)(t))
        if a < 0.01:
            return VGroup()
        q = ride(jumpy, float(t_ju) - 0.45 * RIDE, C.bad, t)
        g = VGroup()
        if len(q) <= cut + 1:
            g.add(polyline([tuple(v) for v in q], C.bad, 2.6, a))
        else:
            g.add(polyline([tuple(v) for v in q[:cut]], C.bad, 2.6, a),
                  DashedLine(P3(*q[cut - 1]), P3(*q[cut]), dash_length=0.08, stroke_color=C.bad, stroke_width=2.2,
                             stroke_opacity=a),
                  polyline([tuple(v) for v in q[cut:]], C.bad, 2.6, a))
        g.add(Dot(P3(*q[-1]), radius=0.06, color=C.bad, fill_opacity=a))
        return g
    glow(s, C.bad, z=5.5, k=0.6, parallax=0.0).redraw(jump_path, during=(t_ju - 1.1, t_mp))

    def jump_tag(t):
        a = float(fade(t_ju + 0.1, dur=0.3, out=t_mp - 0.4, out_dur=0.5)(t))
        if a < 0.01:
            return VGroup()
        q = cam(t).project(ch10.on_surface(jumpy[cut:cut + 1], tau[cut:cut + 1], zs(t)))[0]
        return sans("jump", 24, C.bad).set_opacity(a).move_to(P3(*(q + np.array([-0.75, -0.2]))))
    s.manim(z=50, parallax=0.0).redraw(jump_tag, during=(t_ju, t_mp))
    lab.play(FadeIn(sans("calm", 24, C.light).move_to(P3(3.9, 2.1))), at=t_ca + 0.6, dur=0.5)
