"""c06_s03 · GPS (payoff). Storyboard: plan/scene_plan.md § c06_s03. Layout L2.

Opens on c06_s02's last frame (the muon columns), which gives way to a lit Earth turning under the camera with the
six GPS orbital planes (55°, 60° apart, at the true radius: 26 562 km, 4.17 Earth radii) and their satellites.
'seven': one satellite's clock is marked and the speed term, −7.2 μs a day, writes in the right column. 'gravity':
its height, 20 200 km, and 'forty five' the gravity term +45.7 in the Einstein hue (chapter two returns), then the
net +38.5 (eqdata.gps_drift, first order). 'drift': the camera falls to a street map, where the phone's pin slides
11.5 km in a day, the distance light covers in 38.5 μs. 'next word': the pin snaps back, and the same phone
suggests the next word. 'downhill': the map gives way to the contour lines of chapter 7's hill, and a walker appears
near its top (sims.descent_path's start).
"""
import math

import numpy as np
from aion import *

import ch6
import eqdata
import sims as sm
from beats import T
from kit import chapter_backdrop, glimpse, COL, P3, RC, add_rail, fit, glow, mix, polyline, sans, shade, smooth01, tag_under, tex, tint

HI = (0, 0)                                      # the satellite whose clock we follow
GPS = eqdata.gps_drift()


def _carry(s, out):
    """c06_s02's last frame: the muon columns with their ground hits, braces and counts, and the γ formula."""
    t0 = float(s.start)
    op = fade(t0 - 5, dur=0.1, out=out, out_dur=0.6)
    m = s.manim(z=6, opacity=op)
    m.add(ch6.muon_axes(), ch6.muon_heads(), *ch6.muon_braces(), ch6.ground_counts(t0, ch6.MU_ON))
    m.add(ch6.muon_column(t0, ch6.MU_ON, False))
    glow(s, C.dilation, z=7, k=0.5, opacity=op).add(ch6.muon_column(t0, ch6.MU_ON, True))
    e, tags = ch6.gamma_eqn()
    s.manim(z=50, parallax=0.0, opacity=op).add(e, tags)


def _sat(t):
    pl, k = HI
    u = ch6.SAT_RATE * t + 2 * math.pi * k / ch6.N_SAT + 0.7 * pl
    sx, sy, d = ch6._view(ch6.orbit_point(pl, u), ch6.AZ_RATE * t)
    return np.array([ch6.EC[0] + sx, ch6.EC[1] + sy]), d


def _drift(t, t_a, t_b, t_back):
    """The pin's error in km: 0 → 11.5 between t_a and t_b, then back to 0 at t_back."""
    up = float(smooth01((t - t_a) / (t_b - t_a)))
    down = float(smooth01((t - t_back) / 0.5))
    return GPS["range_error_km"] * up * (1 - down), up


@scene(T.c06_s03, T.c07_s01)
def s21_c06_gps(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 6, last=True)
    add_rail(s, 6, busy=True)
    t0 = float(s.start)
    t_gp, t_sv, t_gr, t_ff, t_dr, t_nw, t_dh = (T.c06_s03_gps, T.c06_s03_seven, T.c06_s03_gravity,
                                                T.c06_s03_forty_five, T.c06_s03_drift, T.c06_s03_next_word,
                                                T.c06_s03_downhill)
    # a GPS Block IIF satellite (NASA, public domain), in the open column before the drift terms write there
    glimpse(s, "photo:gps.jpg", t_gp + 0.2, C.dilation, dur=min(4.0, float(t_sv) - float(t_gp) - 1.0), h=2.0,
            at_xy=(RC, 1.9))
    _carry(s, t0 + 0.2)

    # Earth, the six orbital planes, the satellites
    dive = float(t_dr) - 1.9
    e_op = fade(t_gp - 0.3, dur=1.0, out=dive + 0.9, out_dur=0.6)
    s.add(FramesLayer(ch6.earth_frame(e_op), height=2 * ch6.ER, pos=tuple(ch6.EC), z=2,
                      during=[(t_gp - 0.5, dive + 1.6)]))
    o_op = fade(t_gp - 0.3, dur=1.0, out=dive + 0.15, out_dur=0.4)     # the orbits leave before the camera falls
    s.manim(z=3).redraw(lambda t: ch6.orbits(t, float(o_op(t)))[0], during=(t_gp - 0.5, dive + 0.8))
    glow(s, C.light, z=4, k=0.7).redraw(lambda t: ch6.orbits(t, float(o_op(t)))[1], during=(t_gp - 0.5, dive + 0.8))
    lab = sans("GPS", 26, C.dilation).move_to(P3(ch6.EC[0] + ch6.ORB + 0.3, ch6.EC[1] - 1.6), aligned_edge=LEFT)
    m = s.manim(z=10)
    m.play(FadeIn(lab), at=t_gp + 0.6, dur=0.5)
    m.play(FadeOut(lab), at=t_sv - 0.8, dur=0.5)

    # one satellite's clock, and how high it sits
    h_op = fade(t_sv - 0.2, dur=0.5, out=dive + 0.15, out_dur=0.4)

    def marked(t):
        a = float(h_op(t))
        p, d = _sat(t)
        if a < 0.01 or d > 0:
            return VGroup()
        return VGroup(Circle(radius=0.16, stroke_color=C.light, stroke_width=2, stroke_opacity=a).move_to(P3(*p)),
                      sans("clock", 22, C.light).set_stroke(C.bg, 6, background=True).set_opacity(a).next_to(P3(*p), UR, buff=0.12))
    s.manim(z=11).redraw(marked, during=(t_sv - 0.4, dive + 1.1))
    up_op = fade(t_gr - 0.1, dur=0.5, out=t_ff + 1.6, out_dur=0.5)

    def height(t):
        a = float(up_op(t))
        p, d = _sat(t)
        if a < 0.01 or d > 0:
            return VGroup()
        v = p - ch6.EC
        u = v / np.linalg.norm(v)
        a0 = ch6.EC + u * ch6.ER
        ln = DashedLine(P3(*a0), P3(*(p - u * 0.17)), stroke_color=C.einstein, stroke_width=2, dash_length=0.08)
        mid = (a0 + p) / 2 + np.array([-u[1], u[0]]) * 0.32
        txt = sans(f"{round((eqdata.GPS_RADIUS - eqdata.R_EARTH) / 1e5) * 100:,} km up".replace(",", " "), 22, C.einstein)
        txt.set_stroke(C.bg, 7, background=True)                    # a black edge, so the orbits pass behind it
        return VGroup(ln.set_opacity(a), txt.move_to(P3(*mid)).set_opacity(a))
    s.manim(z=11).redraw(height, during=(t_gr - 0.3, t_ff + 2.2))

    # the tally, a day at a time, in the right column
    hud = s.manim(z=50, parallax=0.0)
    sp, gr, net, un = (f"{GPS['speed_us']:.1f}", f"+{GPS['gravity_us']:.1f}", f"=+{GPS['net_us']:.1f}",
                       r"\ \mu\mathrm{s}")
    e = Eqn(sp + gr + net + un, colors={sp: C.dilation, gr: C.einstein, net: C.light, un: C.muted})
    fit(e.scale(0.95), COL[1] - COL[0]).move_to(P3(RC, 0.55))
    head = sans("clock gain per day", 22, C.muted).move_to(P3(RC, 1.35))
    t_sp, t_g, t_n = (tag_under(e, sp, "speed", C.dilation), tag_under(e, gr, "gravity", C.einstein),
                      tag_under(e, net, "net", C.light))
    hud.play(FadeIn(head), at=t_sv - 0.3, dur=0.5)
    hud.play(FadeIn(VGroup(e.part(sp), t_sp), shift=0.06 * UP), at=t_sv + 0.3, dur=0.6)
    hud.play(FadeIn(VGroup(e.part(gr), t_g), shift=0.06 * UP), at=t_ff - 0.1, dur=0.6)
    hud.play(FadeIn(VGroup(e.part(net), e.part(un), t_n), shift=0.06 * UP), at=t_ff + 1.4, dur=0.7)
    tally = VGroup(head, e, t_sp, t_g, t_n)
    hud.play(FadeOut(tally), at=t_nw - 0.4, dur=0.5)
    assert abs(GPS["speed_us"] + 7.2) < 0.05 and abs(GPS["gravity_us"] - 45.7) < 0.05 and abs(GPS["net_us"] - 38.5) < 0.05

    # drift: down to the street, where the pin slides away
    s.camera.frame(dive, center=tuple(ch6.EC), zoom=6.0, dur=1.6)
    mp_op = fade(dive + 0.9, dur=0.8, out=t_dh - 0.1, out_dur=0.7)
    dim = lambda t: 1 - 0.6 * float(smooth01((t - float(t_nw) + 0.2) / 0.5))
    x0, x1, y0, y1 = ch6.MAP_BOX
    s.add(ArrayLayer(ch6.map_rgba(), height=y1 - y0, pos=((x0 + x1) / 2, (y0 + y1) / 2), z=1, parallax=0.0,
                     opacity=lambda t: float(mp_op(t)) * dim(t)))
    t_a, t_b, t_back = float(t_dr) - 0.2, float(t_dr) + 3.6, float(t_nw) - 0.1

    def pins(t):
        a = float(mp_op(t))
        km, _ = _drift(t, t_a, t_b, t_back)
        p = ch6.PIN0 + ch6.PIN_DIR * km * ch6.KM
        a0 = a * float(smooth01((t - t_a) / 0.4)) * (1 - float(smooth01((t - t_back) / 0.4)))
        return VGroup(ch6.pin(ch6.PIN0, C.light, a0, hollow=True), ch6.pin(p, C.dilation, a))
    glow(s, C.dilation, z=8, k=0.6, parallax=0.0).redraw(pins, during=(dive + 0.8, t_dh + 0.6))

    def ruler(t):
        a = float(mp_op(t))
        km, up = _drift(t, t_a, t_b, t_back)
        g = VGroup()
        if km < 0.05 or a < 0.01:
            return g
        q0 = ch6.PIN0
        q1 = q0 + ch6.PIN_DIR * km * ch6.KM
        nrm = np.array([-ch6.PIN_DIR[1], ch6.PIN_DIR[0]])
        off = -0.45 * nrm
        g.add(Line(P3(*(q0 + off)), P3(*(q1 + off)), stroke_color=C.dilation, stroke_width=2.4, stroke_opacity=a))
        for k in range(int(km) + 1):
            q = q0 + ch6.PIN_DIR * k * ch6.KM + off
            h = 0.12 if k % 5 else 0.2
            g.add(Line(P3(*(q - nrm * h / 2)), P3(*(q + nrm * h / 2)), stroke_color=C.dilation, stroke_width=1.8,
                       stroke_opacity=a))
        mid = (q0 + q1) / 2 + off - 0.42 * nrm
        hours = 24 * up
        g.add(VGroup(sans(f"{km:.1f} km", 30, C.dilation), sans(f"after {hours:.0f} h", 22, C.muted))
              .arrange(RIGHT, buff=0.25, aligned_edge=DOWN).move_to(P3(*mid)).set_opacity(a))
        return g
    s.manim(z=9, parallax=0.0).redraw(ruler, during=(t_dr - 0.4, t_dh + 0.6))

    def pin_words(t):
        a = float(mp_op(t))
        km, _ = _drift(t, t_a, t_b, t_back)
        a0 = a * float(smooth01((t - t_a - 0.3) / 0.4)) * (1 - float(smooth01((t - t_back) / 0.4)))
        p = ch6.PIN0 + ch6.PIN_DIR * km * ch6.KM
        return VGroup(sans("you", 22, C.light).next_to(P3(*ch6.PIN0) + UP * 0.42, LEFT, buff=0.3).set_opacity(a0),
                      sans("GPS", 22, C.dilation).next_to(P3(*p) + UP * 0.42, RIGHT, buff=0.3).set_opacity(a0))
    s.manim(z=10, parallax=0.0).redraw(pin_words, during=(t_dr - 0.4, t_nw + 0.4))

    # the next word: the same phone, predicting
    w_op = fade(t_nw - 0.1, dur=0.5, out=t_dh - 0.1, out_dur=0.6)
    words = VGroup(sans("see you", 34, C.light), Line(ORIGIN, UP * 0.42, stroke_color=C.light, stroke_width=2))
    words.arrange(RIGHT, buff=0.08)
    sug = VGroup(*[sans(w, 28, c) for w, c in (("soon", C.descent), ("later", C.muted), ("tomorrow", C.muted))])
    sug.arrange(RIGHT, buff=0.75)
    bars = VGroup(*[Line(P3(0, -0.18), P3(0, 0.18), stroke_color=C.ghost, stroke_width=1.6)
                    .move_to((a.get_right() + b.get_left()) / 2) for a, b in zip(sug[:-1], sug[1:])])
    phone = VGroup(words, VGroup(sug, bars)).arrange(DOWN, buff=0.45).move_to(P3(-2.1, 0.2))
    shade(s, -2.1, 0.2, phone.width + 1.2, phone.height + 0.9, a=0.85, z=11, parallax=0.0, opacity=w_op)
    s.manim(z=12, parallax=0.0, opacity=w_op).add(phone)

    # downhill: the contour lines of the next chapter's hill, and a walker at its top
    cs = ch6.loss_contours()
    lv = np.array([c[0] for c in cs])
    t_c = float(t_dh) - 0.3

    def contours(t):
        g = VGroup()
        for (l, pts) in cs:
            k = (l - lv.min()) / (lv.max() - lv.min())
            a = float(smooth01((t - t_c - 0.6 * k) / 0.5))
            if a > 0.01:
                g.add(polyline(pts, mix(C.descent, C.light, 0.25 * (1 - k)), 1.6, a * (0.85 - 0.45 * k)))
        return g
    s.manim(z=13, parallax=0.0).redraw(contours, during=(t_c - 0.1, s.end))
    start = sm.descent_path()[0] * ch6.LS                    # the walker stands at the top; c07_s01 walks it

    def walker(t):
        a = float(smooth01((t - t_c - 0.5) / 0.5))
        return Dot(P3(*start), radius=0.08, color=C.light, fill_opacity=a) if a > 0.01 else VGroup()
    glow(s, C.descent, z=14, k=0.7, parallax=0.0).redraw(walker, during=(t_c + 0.2, s.end))
