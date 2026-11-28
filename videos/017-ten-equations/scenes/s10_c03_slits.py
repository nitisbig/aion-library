"""c03_s01 · Dots and stripes (hook). Storyboard: plan/scene_plan.md § c03_s01. Layout L1.

Opens on c02_s03's last frame (the hydrogen atom), which gives way to the chapter card. The apparatus in side view
(gun, two-slit wall, screen edge-on) with the screen also shown turned to face us on the right. Electrons are fired
one at a time: each crosses as a blip and lands as one dot; then thousands land and stripes appear. The landing
heights are sampled from the two-slit intensity (ch3.slit_intensity, seeded), and the wave drawn on 'waves' is the
same two-slit wave, so its bright fringes meet the screen exactly where the stripes are.
"""
import numpy as np
from aion import *

import ch3
from beats import T
from kit import P3, add_rail, chapter_card, lin_rgb, polyline, sans, tint

PANEL = (1.75, 5.65)                             # the face-on screen, x-range (y as the side view)
PPU = 80


def _count(t):
    """Electrons landed by time t: one at a time from 'single dot', then a flood from 'thousands'."""
    t1, t2 = float(T.c03_s01_single_dot) - 0.1, float(T.c03_s01_thousands)
    if t < t1:
        return 0
    if t < t2:
        return 1 + int((t - t1) / 0.65)
    u = t - t2
    return min(len(ch3.hits()[0]), 1 + int((t2 - t1) / 0.65) + int(18 * u + 260 * u * u))


def _panel_frames():
    ys, us = ch3.hits()
    w = PANEL[1] - PANEL[0]
    nx, ny = int(w * PPU), int(2 * ch3.SCREEN_H * PPU)
    px = np.clip((0.06 + 0.88 * us) * nx, 0, nx - 1).astype(np.int32)
    py = np.clip((ch3.SCREEN_H - ys) * PPU, 0, ny - 1).astype(np.int32)
    col = lin_rgb(C.schrod)

    def frame(t):
        n = _count(t)
        acc = np.zeros(ny * nx, np.float32)
        if n:
            np.add.at(acc, py[:n] * nx + px[:n], 1.0)
        a = acc.reshape(ny, nx)
        a = a + 0.6 * (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) \
            + 0.3 * (np.roll(a, (1, 1), (0, 1)) + np.roll(a, (1, -1), (0, 1)) + np.roll(a, (-1, 1), (0, 1))
                     + np.roll(a, (-1, -1), (0, 1)))
        v = 1 - np.exp(-a * 1.6)
        out = np.zeros((ny, nx, 4), np.uint8)
        lin = v[..., None] * col[None, None, :]
        srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
        out[..., :3] = (srgb * 255).astype(np.uint8)
        out[..., 3] = (v * 255).astype(np.uint8)
        return out
    return frame


def _blips(t):
    """The first few electrons crossing, gun → slits → screen, each as a small dot (pure in t)."""
    ys, _ = ch3.hits()
    t1 = float(T.c03_s01_single_dot) - 0.1
    g = VGroup()
    for i in range(6):
        land = t1 + 0.65 * i
        u = (t - (land - 0.9)) / 0.9
        if not 0 <= u <= 1:
            continue
        x = ch3.GUN_X + (ch3.SCREEN_X - ch3.GUN_X) * u
        yw = ch3.SLIT_Y if ys[i] > 0 else -ch3.SLIT_Y
        uw = (ch3.WALL_X - ch3.GUN_X) / (ch3.SCREEN_X - ch3.GUN_X)
        y = yw * (u / uw) if u < uw else yw + (ys[i] - yw) * (u - uw) / (1 - uw)
        g.add(Dot(P3(x, y), radius=0.05, color=C.schrod))
    return g


def _apparatus():
    gun = VGroup(Rectangle(width=0.7, height=0.4, stroke_color=C.muted, stroke_width=2).move_to(P3(ch3.GUN_X - 0.3, 0)),
                 Line(P3(ch3.GUN_X + 0.05, 0), P3(ch3.GUN_X + 0.2, 0), stroke_color=C.muted, stroke_width=2))
    w, a = ch3.WALL_X, ch3.SLIT_A / 2
    segs = [(-2.9, -ch3.SLIT_Y - a), (-ch3.SLIT_Y + a, ch3.SLIT_Y - a), (ch3.SLIT_Y + a, 2.9)]
    wall = VGroup(*[Line(P3(w, y0), P3(w, y1), stroke_color=C.text, stroke_width=5) for y0, y1 in segs])
    screen = Line(P3(ch3.SCREEN_X, -ch3.SCREEN_H), P3(ch3.SCREEN_X, ch3.SCREEN_H), stroke_color=C.muted, stroke_width=4)
    # the same screen turned to face us (faint lines join its edges)
    face = Rectangle(width=PANEL[1] - PANEL[0], height=2 * ch3.SCREEN_H, stroke_color=C.ghost, stroke_width=1.5) \
        .move_to(P3(sum(PANEL) / 2, 0))
    join = VGroup(*[DashedLine(P3(ch3.SCREEN_X + 0.05, s * ch3.SCREEN_H), P3(PANEL[0], s * ch3.SCREEN_H),
                               stroke_color=C.ghost, stroke_width=1.2, dash_length=0.08) for s in (1, -1)])
    labs = VGroup(sans("electrons", 22, C.muted).move_to(P3(ch3.GUN_X - 0.3, -0.5)),
                  sans("two slits", 22, C.muted).move_to(P3(w, 3.15)),
                  sans("screen", 22, C.muted).move_to(P3(sum(PANEL) / 2, -3.0)))
    return gun, wall, screen, face, join, labs


@scene(T.c03_s01, T.c03_s02)
def s10_c03_slits(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_el, t_one, t_k, t_wave, t_part = (T.c03_s01_electrons, T.c03_s01_single_dot, T.c03_s01_thousands,
                                        T.c03_s01_waves, T.c03_s01_particle)
    # c02_s03's last frame: the hydrogen atom, filling the view (camera zoomed 9×)
    leave = fade(t0 - 5, dur=0.1, out=t0 + 0.3, out_dur=0.5)
    s.add(ArrayLayer(ch3.cloud_rgba(), height=0.34 * 9.0, pos=(0, 0), z=6, parallax=0.0, opacity=leave))
    s.manim(z=7, parallax=0.0, opacity=leave, fx=[Glow(C.light, strength=C.glow * 1.4, radius=C.glow_r)]) \
        .add(Dot(ORIGIN, radius=0.035 * 0.4 * 9.0 / 3, color=C.light))
    chapter_card(s, 3, at=t0 + 0.35, out=t_el - 0.1)
    add_rail(s, 3, opacity=fade(t0 + 0.35, dur=0.8), busy=True)

    gun, wall, screen, face, join, labs = _apparatus()
    m = s.manim(z=5)
    m.play(FadeIn(VGroup(gun, wall, screen)), at=t_el + 0.1, dur=0.8)
    m.play(FadeIn(VGroup(face, join)), at=t_el + 0.5, dur=0.8)
    m.play(FadeIn(labs), at=t_el + 0.8, dur=0.6)
    m.play(FadeOut(labs[0]), at=t_wave - 0.6, dur=0.5)

    s.manim(z=7).redraw(_blips, during=(t_one - 1.2, t_k + 0.4))
    s.add(FramesLayer(_panel_frames(), height=2 * ch3.SCREEN_H, pos=(sum(PANEL) / 2, 0), z=4, opacity=fade(t_one - 1, dur=0.1, out=s.end - 0.45, out_dur=0.45),
                      fx=[Glow(C.schrod, strength=C.glow * 0.3, radius=C.glow_r)], during=[(t_one - 0.3, s.end)]))

    # the expected pattern, traced along the panel's right edge once the stripes are clear
    yy = np.linspace(-ch3.SCREEN_H, ch3.SCREEN_H, 400)
    prof = polyline([(PANEL[1] + 0.05 + 0.55 * v, y) for y, v in zip(yy, ch3.slit_intensity(yy))], C.schrod, 2.2)
    m.play(Create(prof), at=t_k + 2.6, dur=1.6)
    m.play(FadeOut(VGroup(gun, wall, screen, face, join, labs[1:], prof)), at=s.end - 0.45, dur=0.45)

    # waves: the two-slit wave, faint, behind the apparatus
    nx, ny = int((ch3.SCREEN_X - ch3.GUN_X + 0.4) * 60), int(2 * 2.9 * 60)
    xs = np.linspace(ch3.GUN_X - 0.2, ch3.SCREEN_X + 0.2, nx)
    ys = np.linspace(-2.9, 2.9, ny)
    X, Y = np.meshgrid(xs, ys)
    ext = (xs[-1] - xs[0], ys[-1] - ys[0])
    wave_op = fade(t_wave - 0.2, dur=1.0, out=t_part - 0.3, out_dur=0.5)
    win = (np.clip((2.9 - np.abs(Y)) / 0.7, 0, 1) * np.clip((X - xs[0]) / 0.8, 0, 1)) ** 1.5
    s.add(FieldLayer(lambda t: ch3.slit_wave(X, Y, t) * win, cmap="diverging",
                     colors=(tint(C.schrod, 0.04), C.bg, tint(C.schrod, 0.34)), vmin=-1.3, vmax=1.3, extent=ext,
                     center=((xs[0] + xs[-1]) / 2, 0.0), z=-10, opacity=wave_op, start=t_wave - 0.6, end=s.end))

    # lands as a particle: the wave is gone; one electron lands as a single bright dot
    yhit = 0.0
    flash = pulse(t_part, amp=1.0, dur=1.0)
    s.manim(z=8, fx=[Glow(C.light, strength=C.glow * 1.6, radius=C.glow_r)]).redraw(
        lambda t: Dot(P3(ch3.SCREEN_X, yhit), radius=0.08, color=C.light, fill_opacity=float(flash(t))),
        during=(float(t_part) - 0.6, s.end))
