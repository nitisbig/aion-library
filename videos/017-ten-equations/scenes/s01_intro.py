"""in_s01 · A bar of hot metal (hook). Storyboard: plan/scene_plan.md § in_s01. Layout L1.

A dark stage; a metal bar lies across the lower third. 'heat': one end glows and heat spreads along it (the exact
cosine-series solution, sims.heat_bar, the same bar Fourier's chapter and the outro return to). 'equation': the heat
equation writes, with Fourier's name tag. 'smooth waves': the temperature curve lifts off the bar and splits into its
first five cosine waves, stacked in depth, each fading at its own rate (exp(−(nπ)²t)). 'music', 'photographs',
'inside': the waves give way to three things they now run: a chord's waveform, Fourier's portrait rebuilt from 5 % of
its frequencies, an MRI slice rebuilt from its k-space. 'Equations often': the whole picture shrinks into one tile
(T5) and the other nine tiles fade up around it, still dim.
"""
import math

import numpy as np
from aion import *

import ch5
import ch10
import intro as I
import outro as O
import sims as sm
from beats import T
from kit import P3, glow, lin_rgb, name_tag, polyline, sans, smooth01, tex

XS = np.linspace(0, 1, 160)
BX0, BX1, BY, BH = -3.2, 3.2, -1.9, 0.42
U0 = sm.heat_bar(XS, 0.0005, n_modes=40)[0].max()
TOP = 2.55                                                  # the equation's height


def _rgba(lin, a):
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.maximum(lin, 0) ** (1 / 2.4) - 0.055)
    out = np.empty(a.shape + (4,), np.uint8)
    out[..., :3] = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return out


def shr_pts(P, k):
    return P * k


def _embers(t, t_he, n=70, seed=1807):
    """Sparks rising off the hot end: each lives LIFE seconds on a loop, born on the bar near x = 0.1, drifting up
    and swaying. Points not alive are parked far off screen."""
    rng = np.random.default_rng(seed)
    LIFE = 2.2
    ph = rng.uniform(0, LIFE, n)
    x0 = BX0 + (BX1 - BX0) * rng.normal(0.1, 0.05, n)
    vy, sw, fr = rng.uniform(0.35, 0.75, n), rng.uniform(0.05, 0.18, n), rng.uniform(1.0, 2.4, n)
    age = (t - t_he + ph) % LIFE
    born = (t - t_he + ph) >= LIFE * 0.999
    x = x0 + sw * np.sin(fr * age * 2 * np.pi + ph * 3) + 0.08 * age
    y = BY + BH / 2 + vy * age
    P = np.c_[x, y]
    P[~born | (age > LIFE * 0.95)] = (99.0, 99.0)
    return P


def _portrait():
    """Fourier's engraving (already toned in his hue, feathered: the chapter-card portrait). Returns (linear RGB,
    alpha), rows top-first."""
    from pathlib import Path

    from PIL import Image
    im = np.asarray(Image.open(Path(__file__).resolve().parents[1] / "assets/images/portraits/fourier.png")
                    .convert("RGBA")).astype(np.float32) / 255
    rgb = np.where(im[..., :3] <= 0.04045, im[..., :3] / 12.92, ((im[..., :3] + 0.055) / 1.055) ** 2.4)
    return rgb, im[..., 3]


def _year_digits(size=130):
    return [tex(str(d), size, C.text) for d in range(10)]


def _odometer(Y, D, centre, scale, pitch=None):
    """The year Y (a float) as rolling digits: each place turns over only while the place below it rolls past 9."""
    g = VGroup()
    w = (pitch or D[0].width * 1.05) * scale
    h = D[0].height * 1.35 * scale
    for i, p in enumerate((1000, 100, 10, 1)):
        lower = Y % p
        f = (Y % 1.0) if p == 1 else max(0.0, lower - (p - 1))
        d = int(Y // p) % 10
        x = centre[0] + (i - 1.5) * w
        cur = D[d].copy().scale(scale).move_to(P3(x, centre[1] + f * h)).set_opacity(1 - f)
        nxt = D[(d + 1) % 10].copy().scale(scale).move_to(P3(x, centre[1] - (1 - f) * h)).set_opacity(f)
        g.add(cur, nxt)
    return g


def _opening(s, t_st, t_jo, t_md, t_eq, t_sw):
    """0 s → the bar: the year rolls back two hundred years, lands on 1807 and flies into Fourier's name tag while
    his engraving develops out of the dark (darkest lines first), then steps aside for the bar."""
    D = _year_digits()
    tag = name_tag("Joseph Fourier · 1807", C.fourier)
    yr_txt = tag[1]
    t_roll = t_st - 0.1
    t_fly0, t_fly1 = t_jo - 0.35, t_jo + 0.55
    tag_op = fade(t_fly1 - 0.25, dur=0.4, out=t_sw - 1.0, out_dur=0.8)
    glyphs = yr_txt[0][-4:]                                              # the tag's own "1807"
    end_c = VGroup(*glyphs).get_center()[:2]
    end_s = glyphs[2].height / D[0].height
    pitch0 = D[0].width * 1.05
    pitch1 = (glyphs[3].get_center()[0] - glyphs[0].get_center()[0]) / 3 / end_s

    def year(t):
        u = I.ease(t, t_roll, t_roll + 2.3)
        Y = 2026.0 - 219.0 * (1 - (1 - u) ** 3) if u < 1 else 1807.0
        f = I.ease(t, t_fly0, t_fly1)
        a = I.ease(t, t_roll - 0.6, t_roll) * (1 - I.ease(t, t_fly1 - 0.3, t_fly1 + 0.05))
        if a < 0.01:
            return VGroup()
        c = np.array([0.0, 0.25]) * (1 - f) + end_c * f
        return _fade_group(_odometer(Y, D, c, 1 + (end_s - 1) * f, pitch0 + (pitch1 - pitch0) * f), a)
    s.manim(z=60, parallax=0.0).redraw(year, during=(t_roll - 0.7, t_fly1 + 0.2))
    s.manim(z=60, parallax=0.0, opacity=tag_op).add(tag)

    # the engraving develops: a soft diagonal sweep, its exposure rising like a print in the tray
    rgb, alpha = _portrait()
    H, W = alpha.shape
    yy, xx = np.mgrid[0:H, 0:W]
    diag = (xx / W + yy / H) / 2
    p_in = lambda t: I.ease(t, t_jo - 0.1, t_jo + 2.0)
    p_out = fade(t_jo - 1, dur=0.1, out=t_sw - 0.9, out_dur=0.9)

    def frame(t):
        u = p_in(t)
        m = np.clip((1.5 * u - diag) / 0.3, 0, 1)
        expo = 0.25 + 0.75 * u ** 0.7
        return _rgba(rgb * expo, m * alpha * float(p_out(t)))

    def p_pos(t):
        v = I.ease(t, t_md - 0.2, t_md + 1.2)
        return (0.0 * (1 - v) - 4.75 * v, 0.2 * (1 - v) + 0.55 * v)
    s.add(FramesLayer(frame, height=4.6, z=2, parallax=0.0, pos=Track(p_pos),
                      scale=Track(lambda t: (1.0 + 0.04 * I.ease(t, t_jo, t_md)) * (1 - 0.32 * I.ease(t, t_md - 0.2,
                                                                                                  t_md + 1.2))),
                      during=[(t_jo - 0.1, t_sw + 0.1)]))


def _fade_group(g, a):
    for m in g:
        m.set_opacity(m.get_fill_opacity() * a)
    return g


@scene(T.start, T.in_s02)
def s01_intro(s):
    s.solid(C.bg, z=-200)
    t_st, t_he, t_eq, t_sw = (float(T.in_s01_two_hundred_years_ag), float(T.in_s01_heat), float(T.in_s01_equation),
                              float(T.in_s01_smooth_waves))
    t_mu, t_ph, t_in, t_of = (float(T.in_s01_music), float(T.in_s01_photographs), float(T.in_s01_inside),
                              float(T.in_s01_equations_often))

    # everything shrinks into T5 on 'Equations often'
    k = lambda t: 1 - (1 - I.K_SHRINK) * I.ease(t, t_of + 0.1, t_of + 1.9)
    t_jo, t_md = float(T.in_s01_joseph), float(T.in_s01_modest)
    c_op = fade(t_md + 0.2, dur=1.0, out=t_of + 1.5, out_dur=0.7)

    def shr(mob, t):
        return mob.scale(k(t), about_point=ORIGIN)

    _opening(s, t_st, t_jo, t_md, t_eq, t_sw)

    # the heat: off until 'heat', then spreading slowly, faster once the waves are out
    def th(t):
        return 0.0005 + 0.0005 * float(np.clip(t - t_he, 0, t_sw - t_he)) + 0.0015 * max(t - t_sw, 0.0)
    amp = lambda t: I.ease(t, t_he - 0.1, t_he + 1.1)

    def bar(t, cells):
        a = float(c_op(t))
        un = sm.heat_bar(XS, th(t), n_modes=40)[0] / U0 * amp(t)
        cv = amp(t) * (1 - I.ease(t, t_sw + 0.2, t_sw + 1.0))
        g = ch10.bar_group(XS, un, a, BX0, BX1, BY, BH, curve=0.0 if cells else cv, cells=cells)
        if cells and a > 0.01:
            for x in (BX0, BX1):
                g.add(Line(P3(x, BY - BH / 2), P3(x, BY + BH / 2), stroke_color=C.ghost, stroke_width=1.2,
                           stroke_opacity=a))
        return shr(g, t)
    s.manim(z=3).redraw(lambda t: bar(t, True), during=(s.start, t_of + 2.4))
    glow(s, C.fourier, z=3.5, k=0.5).redraw(lambda t: bar(t, False), during=(t_he - 0.2, t_sw + 1.2))

    # the chord's waveform (where the five waves flow on 'music')
    VY, VH = 0.55, 2.0
    tt = np.linspace(0, ch5.WIN, 600)
    wave = ch5.chord(tt)
    wave = wave / np.abs(wave).max()
    w_pts = [(-5.9 + 3.0 * u, VY + 0.75 * v) for u, v in zip(np.linspace(0, 1, len(tt)), wave)]
    WX = np.interp(XS, np.linspace(0, 1, len(w_pts)), [p[0] for p in w_pts])
    WY = np.interp(XS, np.linspace(0, 1, len(w_pts)), [p[1] for p in w_pts])

    # the equation, and Fourier
    eq = Eqn(r"\frac{\partial u}{\partial t}=\alpha\,\frac{\partial^2 u}{\partial x^2}",
             colors={r"\frac{\partial^2 u}{\partial x^2}": C.fourier})
    eq.scale(1.15).move_to(P3(0, TOP))
    e_on = lambda t: I.ease(t, t_eq - 0.1, t_eq + 1.3)

    def eq_draw(t):
        a = float(c_op(t)) * e_on(t)
        if a < 0.01:
            return VGroup()
        return shr(eq.copy().set_opacity(a), t)
    s.manim(z=10).redraw(eq_draw, during=(t_eq - 0.2, t_of + 2.4))

    # smooth waves: the curve splits into its first five cosine waves, stacked in depth
    t_wo = t_mu - 0.3                                                     # the waves leave for the vignettes

    # (on 'music' the five waves flow together into the chord's waveform: waves added make a sound)
    def modes(t):
        g = VGroup()
        m = I.ease(t, t_wo - 0.2, t_wo + 0.9)                              # the flow into the waveform
        for n in range(1, 6):
            lift = I.ease(t, t_sw + 0.15 * (n - 1), t_sw + 1.1 + 0.15 * (n - 1))
            a = (1 - 0.12 * (n - 1)) * float(smooth01(lift / 0.3)) * (1 - I.ease(m, 0.75, 1.0))
            if a < 0.01:
                continue
            A = 0.28 * math.exp(-(n * math.pi) ** 2 * (th(t) - th(t_sw)))
            y = (BY + 0.5) + ((-0.95 + 0.5 * (n - 1)) - (BY + 0.5)) * lift
            sc, dx = 1 - 0.06 * (n - 1), 0.22 * (n - 1)
            px = (BX0 + (BX1 - BX0) * XS) * sc + dx
            py = y + A * np.cos(n * math.pi * XS)
            px, py = px + (WX - px) * m, py + (WY - py) * m
            g.add(polyline(list(zip(px, py)), C.fourier, 2.6, a))
        return shr(g, t)
    glow(s, C.fourier, z=4, k=0.5).redraw(modes, during=(t_sw - 0.1, t_wo + 1.0))

    # embers off the hot end while it is hottest
    em_a = Track(lambda t: float(c_op(t)) * amp(t) * (1 - I.ease(t, t_sw - 0.6, t_sw + 0.6)))
    s.add(PointsLayer(lambda t: shr_pts(_embers(t, t_he), k(t)), color=C.fourier, size=1.6, glow=0.6, alpha=em_a,
                      additive=True, z=4.5))

    # music, photographs, inside
    lab = lambda w, x: sans(w, 24, C.muted).move_to(P3(x, VY - VH / 2 - 0.3))

    def music(t):
        a = float(c_op(t)) * I.ease(t, t_wo + 0.55, t_wo + 0.95)
        if a < 0.01:
            return VGroup()
        return shr(VGroup(polyline(w_pts, C.fourier, 2.0, a)), t)
    glow(s, C.fourier, z=5, k=0.4).redraw(music, during=(t_mu - 0.2, t_of + 2.4))

    imgs, alpha = ch5.dct_photo()
    stages = [imgs[0.01], imgs[0.05], imgs[0.2]]
    col = lin_rgb(C.light)
    p_op = fade(t_ph - 0.15, dur=0.5)

    def photo(t):
        q = (t - t_ph) / 0.8
        i = int(np.clip(math.floor(q), 0, 2))
        f = float(smooth01((q - math.floor(q)) / 0.35)) if 0 <= q < 2 else 0.0
        g = stages[i] if i == 2 or q < 0 else stages[i] * (1 - f) + stages[i + 1] * f
        return _rgba((g ** 2.2)[..., None] * col, alpha * float(p_op(t)) * float(c_op(t)))
    pos_of = lambda x: Track(lambda t: (x * k(t), VY * k(t)))
    s.add(FramesLayer(photo, height=VH, pos=pos_of(0.0), scale=Track(k), z=5, during=[(t_ph - 0.2, t_of + 2.4)]))

    m_op = fade(t_in - 0.15, dur=0.5)

    def mri(t):
        u = float(np.clip((t - t_in) / 2.2, 0, 1))
        img = ch5.mri_rebuild(0.015 * (1 / 0.015) ** u)
        return _rgba(np.ones_like(img)[..., None] * col, np.clip(img * 1.4, 0, 1) * float(m_op(t)) * float(c_op(t)))
    s.add(FramesLayer(mri, height=VH, pos=pos_of(4.4), scale=Track(k), z=5, during=[(t_in - 0.2, t_of + 2.4)]))

    def labels(t):
        a = float(c_op(t))
        g = VGroup()
        for w, x, tb in (("music", -4.4, t_mu), ("photographs", 0.0, t_ph), ("medical scans", 4.4, t_in)):
            u = I.ease(t, tb, tb + 0.6)
            if u > 0 and a > 0.01:
                g.add(lab(w, x).set_opacity(a * u))
        return shr(g, t)
    s.manim(z=10).redraw(labels, during=(t_mu - 0.1, t_of + 2.4))

    # the wall: T5 takes over from the shrunken picture, and the other nine fade up, dim
    for i in range(10):
        if i == 4:
            op = fade(t_of + 1.3, dur=0.8)
        else:
            op = Track(lambda t, i=i: 0.25 * I.ease(t, t_of + 1.6 + 0.12 * i, t_of + 2.8 + 0.12 * i))
        O.tile_layer(s, i, lambda t, i=i: I.tile_place(i, t), op, z=1)
