"""c05_s03 · Everywhere (payoff). Storyboard: plan/scene_plan.md § c05_s03. Layout L1.

Opens on c05_s02's last frame (the finished π), which fades as a short melody's spectrogram rises as ridge lines
(STFT computed in ch5.spectrogram), turning slowly. 'photographs': Fourier's portrait rebuilt from the largest 1 %,
5 % and 20 % of its DCT numbers. 'MRI': the frequencies a scanner measures (the 2D transform of the Shepp–Logan
slice) rebuild the slice as more of them are used, low ones first. 'keep time': a wave whose crests are counted;
'atoms': its source is an atom, and a strontium clock counts 429 228 004 229 873 waves of its light each second.
'same rate': two identical clocks, ticking together.
"""
import math

import numpy as np
from aion import *

import ch5
import sims as sm
from beats import T
from kit import chapter_backdrop, COL, P3, RC, X1, add_rail, fit, glow, lin_rgb, mix, polyline, sans, smooth01, tag_under, tex

C0 = np.array([-2.2, -0.1])
CAM, ZM = np.array([C0[0] + 0.3, C0[1]]), 1.15    # where c05_s02's camera push ended
SX0, SX1, SY0, SH = COL[0] + 0.15, COL[1], -1.35, 1.75


def _rgba(lin, a):
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.maximum(lin, 0) ** (1 / 2.4) - 0.055)
    out = np.empty(a.shape + (4,), np.uint8)
    out[..., :3] = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return out


def _carry(s):
    t0 = float(s.start)
    op = fade(t0 - 5, dur=0.1, out=t0 + 0.05, out_dur=0.6)
    sp = lambda z: P3(*((C0 + [z.real, z.imag] - CAM) * ZM))
    full = ch5.pi_trace(1.0)
    glow(s, C.fourier, z=3, k=0.8, parallax=0.0, opacity=op).add(
        VMobject(stroke_color=C.fourier, stroke_width=4.4).set_points_as_corners([sp(z) for z in full]))
    fr, co = ch5.pi_terms()
    joints = sm.epicycles(fr, co, 0.0)
    g = VGroup()
    for i in range(1, 34):
        r = abs(co[i - 1])
        if r > 0.02:
            g.add(Circle(radius=r * ZM, stroke_color=C.muted, stroke_width=1.0, stroke_opacity=0.55).move_to(sp(joints[i - 1])))
        g.add(Line(sp(joints[i - 1]), sp(joints[i]), stroke_color=mix(C.fourier, C.light, 0.35), stroke_width=1.8))
    g.add(Dot(sp(joints[-1]), radius=0.06, color=C.light))
    hud = s.manim(z=50, parallax=0.0, opacity=op)
    hud.add(g)
    Ft, ft, ex = r"F(\omega)", r"f(t)", r"e^{-i\omega t}"
    e = Eqn(r"F(\omega)=\int f(t)\,e^{-i\omega t}\,dt", colors={Ft: C.fourier, ft: C.fourier, ex: C.data})
    fit(e.scale(0.85)).move_to(P3(RC, 2.45))
    hud.add(e, tag_under(e, ft, "signal", C.fourier), tag_under(e, ex, "test wave", C.data),
            tag_under(e, Ft, "total", C.fourier))
    ks = np.arange(-18, 19)
    mags = np.array([np.abs(co[fr == k][0]) if (fr == k).any() else 0 for k in ks])
    hud.add(*[Line(P3(SX0 + (SX1 - SX0) * (k + 18) / 36, SY0), P3(SX0 + (SX1 - SX0) * (k + 18) / 36,
                                                                  SY0 + SH * v / mags.max()),
                   stroke_color=C.fourier, stroke_width=3.2) for k, v in zip(ks, mags)],
            Line(P3(SX0, SY0), P3(SX1, SY0), stroke_color=C.muted, stroke_width=1.2),
            sans("frequency", 20, C.muted).move_to(P3(SX1, SY0 - 0.5), aligned_edge=UR))


# ------------------------------------------------------------------------------------------------ music
def _ridges(t, t_on, op):
    a = float(op(t))
    g = VGroup()
    if a < 0.01:
        return g
    ts, fr, S = ch5.spectrogram()
    rows = np.linspace(0, len(ts) - 1, 42).astype(int)
    n = len(rows)
    spin = math.sin(0.35 * (t - t_on))
    dx, dy, W, H = 0.055 + 0.04 * spin, 0.085, 7.4, 1.25
    xf = np.linspace(0, 1, S.shape[1])
    for r in range(n - 1, -1, -1):                              # back rows first, so nearer ones hide them
        grow = float(smooth01((t - t_on - 0.035 * (n - 1 - r)) / 0.6))
        if grow <= 0:
            continue
        x0, y0 = -4.9 + r * dx - 0.9, -2.55 + r * dy
        h = S[rows[n - 1 - r]] ** 0.6 * grow
        pts = [P3(x0 + W * x, y0 + H * v) for x, v in zip(xf, h)]
        depth = 1 - 0.55 * r / n
        poly = Polygon(P3(x0, y0), *pts, P3(x0 + W, y0), stroke_color=C.fourier, stroke_width=1.8,
                       stroke_opacity=a * depth, fill_color=C.bg, fill_opacity=a)
        g.add(poly)
    return g


# ------------------------------------------------------------------------------------------------ photo
def _photo_frames(t1, op):
    imgs, alpha = ch5.dct_photo()
    stages = [imgs[0.01], imgs[0.05], imgs[0.2]]
    col = lin_rgb(C.light)

    def frame(t):
        k = (t - t1) / 0.9
        i = int(np.clip(math.floor(k), 0, 2))
        f = float(smooth01((k - math.floor(k)) / 0.35)) if 0 <= k < 2 else 0.0
        g = stages[i] if i == 2 or k < 0 else stages[i] * (1 - f) + stages[i + 1] * f
        lin = (g ** 2.2)[..., None] * col
        return _rgba(lin, alpha * float(op(t)))
    return frame


# ------------------------------------------------------------------------------------------------ MRI
def _kspace_rgba(op):
    K = np.log1p(np.abs(ch5.kspace()))
    K = (K / K.max()) ** 1.6
    col = lin_rgb(C.fourier)

    def frame(t):
        a = K * float(op(t))
        return _rgba(np.ones_like(a)[..., None] * col, a)
    return frame


def _mri_frames(t1, op):
    col = lin_rgb(C.light)

    def frame(t):
        u = float(np.clip((t - t1) / 3.2, 0, 1))
        frac = 0.015 * (1 / 0.015) ** u
        img = ch5.mri_rebuild(frac)
        a = np.clip(img * 1.4, 0, 1) * float(op(t))
        return _rgba(np.ones_like(a)[..., None] * col, a)
    return frame


@scene(T.c05_s03, T.c06_s01)
def s18_c05_everywhere(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 5, last=True)
    add_rail(s, 5)
    t_mu, t_ph, t_mr, t_kt, t_at, t_sr = (T.c05_s03_music, T.c05_s03_photographs, T.c05_s03_mri, T.c05_s03_keep_time,
                                          T.c05_s03_atoms, T.c05_s03_same_rate)
    _carry(s)
    lab = lambda w: sans(w, 26, C.muted).move_to(P3(0, -3.05))
    m = s.manim(z=10)

    # music: a melody's spectrogram as ridges
    op_m = fade(t_mu - 0.1, dur=0.5, out=t_ph - 0.4, out_dur=0.4)
    glow(s, C.fourier, z=4, k=0.3).redraw(lambda t: _ridges(t, float(t_mu) - 0.1, op_m), during=(t_mu - 0.5, t_ph))
    ml = VGroup(lab("music"), sans("time", 20, C.muted).move_to(P3(-6.25, -0.9)),
                sans("pitch", 20, C.muted).move_to(P3(1.5, -2.85)))
    s.manim(z=11, opacity=fade(t_mu + 0.6, dur=0.5, out=t_ph - 0.4, out_dur=0.4)).add(ml)

    # photographs: fewer numbers than pixels
    op_p = fade(t_ph - 0.3, dur=0.4, out=t_mr - 0.35, out_dur=0.35)
    s.add(FramesLayer(_photo_frames(float(t_ph) - 0.2, op_p), height=4.2, pos=(-0.6, 0.2), z=4,
                      during=[(t_ph - 0.4, t_mr)]))

    def pct(t):
        k = int(np.clip((t - float(t_ph) + 0.2) / 0.9, 0, 2))
        a = float(op_p(t))
        g = VGroup(sans(["1%", "5%", "20%"][k], 40, C.fourier), sans("of the numbers kept", 22, C.muted)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(P3(1.6, 0.3), aligned_edge=LEFT)
        return g.set_opacity(a)
    s.manim(z=11).redraw(pct, during=(t_ph - 0.4, t_mr))
    s.manim(z=11, opacity=op_p).add(lab("photos"))

    # MRI: measured frequencies → the slice
    op_r = fade(t_mr - 0.3, dur=0.4, out=t_kt - 0.45, out_dur=0.4)
    s.add(FramesLayer(_kspace_rgba(op_r), height=3.4, pos=(-2.7, 0.25), z=4, during=[(t_mr - 0.4, t_kt)]))
    s.add(FramesLayer(_mri_frames(float(t_mr) + 0.3, op_r), height=3.4, pos=(2.7, 0.25), z=4,
                      during=[(t_mr - 0.4, t_kt)]))

    def ring(t):
        u = float(np.clip((t - float(t_mr) - 0.3) / 3.2, 0, 1))
        frac = 0.015 * (1 / 0.015) ** u
        return Circle(radius=1.7 * min(frac, 1.0), stroke_color=C.light, stroke_width=1.6,
                      stroke_opacity=0.8 * float(op_r(t))).move_to(P3(-2.7, 0.25))
    s.manim(z=6).redraw(ring, during=(t_mr - 0.4, t_kt))
    mr = VGroup(lab("MRI"), sans("measured frequencies", 22, C.muted).move_to(P3(-2.7, -1.85)),
                sans("the slice", 22, C.muted).move_to(P3(2.7, -1.85)),
                Arrow(P3(-0.75, 0.25), P3(0.75, 0.25), buff=0, stroke_width=2.5, color=C.muted, tip_length=0.15),
                tex(r"F^{-1}", 30, C.muted).move_to(P3(0, 0.62)))
    s.manim(z=11, opacity=op_r).add(mr)

    # keep time: count the waves
    op_k = fade(t_kt - 0.3, dur=0.5, out=t_sr - 0.35, out_dur=0.35)
    lam, c = 1.1, 1.5
    tk = float(t_kt)
    src = lambda t: -6.2 + 0.9 * float(smooth01((t - float(t_at) + 0.2) / 0.6))

    def wave(t):
        a = float(op_k(t))
        x0 = src(t)
        xs = np.linspace(x0, 6.2, 500)
        front = x0 + 50
        y = 0.35 + 0.55 * np.sin(2 * np.pi / lam * (xs - c * (t - tk)))
        return polyline(list(zip(xs, y)), C.fourier, 3.0, a) if a > 0.01 and front > x0 else VGroup()
    glow(s, C.fourier, z=5, k=0.5).redraw(wave, during=(t_kt - 0.4, t_sr))
    gate = Line(P3(0, -0.45), P3(0, 1.15), stroke_color=C.light, stroke_width=2)

    def counter(t):
        a = float(op_k(t))
        n = max(int(c * (t - tk) / lam), 0)
        return VGroup(sans(f"{n}", 40, C.fourier), sans("waves counted", 22, C.muted)) \
            .arrange(RIGHT, buff=0.2).move_to(P3(0, 1.75)).set_opacity(a)
    s.manim(z=11).redraw(counter, during=(t_kt - 0.4, t_sr))
    s.manim(z=11, opacity=op_k).add(gate)
    atom = VGroup(Dot(radius=0.07, color=C.light),
                  Ellipse(width=0.9, height=0.34, stroke_color=C.data, stroke_width=1.6),
                  Ellipse(width=0.9, height=0.34, stroke_color=C.data, stroke_width=1.6).rotate(PI / 3),
                  Ellipse(width=0.9, height=0.34, stroke_color=C.data, stroke_width=1.6).rotate(-PI / 3)) \
        .move_to(P3(-5.75, 0.35))
    at = s.manim(z=12, opacity=op_k)
    at.play(FadeIn(atom, scale=0.8), at=t_at - 0.1, dur=0.6)
    sr = VGroup(sans("429 228 004 229 873", 34, C.fourier), sans("waves of strontium light per second", 22,
                                                                  C.muted)).arrange(DOWN, buff=0.14).move_to(P3(0, -1.55))
    at.play(FadeIn(sr, shift=0.06 * UP), at=t_at + 0.5, dur=0.6)

    # same rate? two identical clocks
    op_c = fade(t_sr - 0.3, dur=0.5)

    def clocks(t):
        a = float(op_c(t))
        g = VGroup()
        k = math.floor((t - float(t_sr)) / 1.0)
        for x in (-2.6, 2.6):
            face = VGroup(Circle(radius=1.15, stroke_color=C.light, stroke_width=2.4, stroke_opacity=a).move_to(P3(x, 0.2)))
            for j in range(12):
                ang = 2 * math.pi * j / 12
                face.add(Line(P3(x + 1.0 * math.sin(ang), 0.2 + 1.0 * math.cos(ang)),
                              P3(x + 1.12 * math.sin(ang), 0.2 + 1.12 * math.cos(ang)),
                              stroke_color=C.muted, stroke_width=1.6, stroke_opacity=a))
            ang = 2 * math.pi * (k + 8) / 60
            face.add(Line(P3(x, 0.2), P3(x + 0.95 * math.sin(ang), 0.2 + 0.95 * math.cos(ang)),
                          stroke_color=C.fourier, stroke_width=3, stroke_opacity=a),
                     Dot(P3(x, 0.2), radius=0.05, color=C.light, fill_opacity=a))
            g.add(face)
        return g
    s.manim(z=8).redraw(clocks, during=(t_sr - 0.4, s.end))
