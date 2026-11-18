"""s23 earth (ch6): the most beautiful case, happening to you right now. The particle Earth (Natural Earth land on a
steel-blue shell) spins about its tilted axis; every point moves at right angles to both the axis and its position,
ṙ = Ω n × r (a cross product). Near the equator you are carried at about 1670 km/h (2π · 6378 km / 23.93 h); at a pole
you just turn on the spot (the camera looks down the axis)."""
from aion import *

import ch6
from ch6 import facing_lon
from beats import T
from shots import (AXIS_N, arrow, backdrop, backed, body_to_world, finish, globe_layers, gproj,
                   lab, latlon, live, p3, sphere_curve, tex)
from verify import EARTH_R_KM, SIDEREAL_S

V_EQ = 2 * np.pi * EARTH_R_KM / (SIDEREAL_S / 3600)  # km/h at the equator
assert 1665 < V_EQ < 1680


def world(t, body):
    return np.asarray(body) @ body_to_world(ch6.theta(t)).T


@scene(T.cut_earth, T.cut_K)
def s23_earth(s):
    backdrop(s)
    m = s.manim(z=3)
    g_op = keys((T.cut_earth, 0.0), (T.cut_earth + 0.8, 1.0), lead=0)
    globe_layers(s, ch6.theta, ch6.center, ch6.radius, ch6.pole, alpha=g_op, z=1, start=T.cut_earth, end=T.cut_K)

    # ── axis and equator ──
    eq_body = np.array([latlon(0, L) for L in np.linspace(0, 360, 145)])
    a_op = keys((T.earth - 0.2, 0.0), (T.earth + 0.6, 1.0), lead=0)
    pulse = keys((T.equator, 0.0), (T.equator + 0.4, 1.0), (T.equator + 1.4, 0.0), lead=0)

    def frame(t):
        c, R, pl = ch6.center(t), ch6.radius(t), ch6.pole(t)
        op = float(a_op(t))
        ax, _ = gproj(np.array([-1.3 * AXIS_N, 1.3 * AXIS_N]), c, R, pl)
        out = VGroup(Line(p3(ax[0]), p3(ax[1]), color=C.eigen, stroke_width=C.stroke, stroke_opacity=op))
        out.add(sphere_curve(world(t, eq_body), c, R, pl, C.flow, C.stroke + 2.5 * float(pulse(t)), op=op))
        return out
    live(m, frame, (T.earth - 0.2, T.cut_K))

    # ── every point moves at right angles to the axis and to its position ──
    lat_lon = [(la, lo) for la in (-60, -40, -20, 0, 20, 40, 60) for lo in range(0, 360, 30)]
    lattice = np.array([latlon(la, lo) for la, lo in lat_lon])
    v_op = keys((T.right_angle - 0.2, 0.0), (T.right_angle + 0.8, 1.0), (T.pole - 0.6, 1.0), (T.pole + 0.2, 0.0),
                lead=0)

    def velocities(t):
        c, R, pl = ch6.center(t), ch6.radius(t), ch6.pole(t)
        op = float(v_op(t))
        W = world(t, lattice)
        tips = W + 0.32 * np.cross(AXIS_N, W)
        a, d = gproj(W, c, R, pl)
        b, _ = gproj(tips, c, R, pl)
        out = VGroup()
        for i in np.where(d > 0.08)[0]:
            if np.linalg.norm(b[i] - a[i]) > 0.06:
                out.add(arrow(a[i], b[i], C.gen, width=C.thin + 1.0, tip=0.13, opacity=op * min(1.0, 3 * d[i])))
        return out
    live(m, velocities, (T.right_angle - 0.2, T.pole + 0.25))

    # ── that's a cross product: n, r and n × r at one point ──
    L_c = facing_lon(28, T.cross + 1.5) + 18
    P_c = latlon(28, L_c)
    c_op = keys((T.cross - 0.3, 0.0), (T.cross + 0.3, 1.0), (T.equator - 0.3, 1.0), (T.equator + 0.2, 0.0), lead=0)

    def cross(t):
        c, R, pl = ch6.center(t), ch6.radius(t), ch6.pole(t)
        op = float(c_op(t))
        r = world(t, P_c)
        nr = np.cross(AXIS_N, r)
        (o, q, qn, qv), _ = gproj(np.array([0 * r, r, r + 0.45 * AXIS_N, r + 0.55 * nr]), c, R, pl)
        lbl = lambda tx, col, at: backed(tex(tx, size=36, color=col), buff=0.04).move_to(p3(at)).set_opacity(op)
        return VGroup(arrow(o, q, C.vec, width=C.stroke + 1, opacity=op), arrow(q, qn, C.eigen, width=C.stroke + 1, opacity=op),
                      arrow(q, qv, C.gen, width=C.stroke + 1.5, opacity=op),
                      lbl(r"\mathbf r", C.vec, (o + q) / 2 + [-0.25, 0.2]), lbl(r"\mathbf n", C.eigen, qn + [0, 0.3]),
                      lbl(r"\mathbf n\times\mathbf r", C.gen, qv + (qv - q) / max(np.linalg.norm(qv - q), 1e-6) * 0.6))
    live(m, cross, (T.cross - 0.3, T.equator + 0.25))
    law = backed(tex(r"\dot{\mathbf r}", "=", r"\Omega\,", r"\mathbf n", r"\times", r"\mathbf r", size=50,
                     colors={0: C.gen, 3: C.eigen, 5: C.vec})).move_to([-4.7, 3.2, 0])
    m.play(FadeIn(law, shift=0.1 * DOWN), at=T.cross + 0.5, dur=0.6)

    # ── near the equator: you, at about 1670 km/h ──
    L_y = facing_lon(0, T.equator + 1.0) - 25
    y_op = keys((T.equator - 0.1, 0.0), (T.equator + 0.4, 1.0), (T.pole - 0.5, 1.0), (T.pole, 0.0), lead=0)

    def you(t):
        c, R, pl = ch6.center(t), ch6.radius(t), ch6.pole(t)
        op = float(y_op(t))
        trail = np.array([latlon(0, L_y - k) for k in np.linspace(40, 0, 30)])
        (q,), _ = gproj(world(t, latlon(0, L_y))[None], c, R, pl)
        return VGroup(sphere_curve(world(t, trail), c, R, pl, C.flow, C.stroke + 1.5, op=op),
                      Dot(p3(q), radius=0.11, color=C.vec).set_opacity(op),
                      backed(lab("you", 26, C.vec), buff=0.04).move_to(p3(q + [0, 0.42])).set_opacity(op))
    live(m, you, (T.equator - 0.1, T.pole + 0.05))
    kmh = backed(tex(r"\approx 1670\ \mathrm{km/h}", size=46, color=C.flow)).move_to([5.0, -0.9, 0])
    m.play(FadeIn(kmh, shift=0.1 * LEFT), at=T.km + 0.2, dur=0.6)
    m.play(FadeOut(kmh), at=T.pole - 0.4, dur=0.4)

    # ── at a pole: look down the axis; the pole turns on the spot ──
    p_op = keys((T.pole + 0.9, 0.0), (T.pole + 1.4, 1.0), (T.cut_K - 0.3, 1.0), (T.cut_K, 0.0), lead=0)

    def pole_pt(t):
        c, R, pl = ch6.center(t), ch6.radius(t), ch6.pole(t)
        op = float(p_op(t))
        (q, e), _ = gproj(world(t, np.array([latlon(90, 0), latlon(80, 0)])), c, R, pl)
        return VGroup(Line(p3(q), p3(q + 1.4 * (e - q)), color=C.vec, stroke_width=C.stroke + 1, stroke_opacity=op),
                      Dot(p3(q), radius=0.12, color=C.vec).set_opacity(op))
    live(m, pole_pt, (T.pole + 0.9, T.cut_K))
    pt = backed(lab("the pole: turning on the spot", 28, C.vec)).move_to([4.6, -3.3, 0])
    m.play(FadeIn(pt), at=T.pole + 1.4, dur=0.5)
    m.play(FadeOut(VGroup(pt, law)), at=T.cut_K - 0.4, dur=0.4)
    finish(s)
