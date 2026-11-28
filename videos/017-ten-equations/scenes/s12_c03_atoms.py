"""c03_s03 · Atoms (payoff). Storyboard: plan/scene_plan.md § c03_s03. Layout L1.

Opens on c03_s02's last frame (the packet through the wall), which fades. Around a nucleus the wave settles into
fixed shapes: hydrogen orbitals 1s, 2p, 3d as point clouds sampled from |ψ_nℓm|² (ch3.orbital_points), turning, the
sign of ψ in two hues. On 'chemistry' two 1s atoms meet and their clouds merge into the H₂ bonding orbital
(ch3.bond_points). On 'Lasers' three line icons. On 'swirls' the cloud starts to flow in seeded vortices and on
'larger' it smears into dye in the chapter-4 hue, the bridge to Navier–Stokes.
"""
import math

import numpy as np
from aion import *

import ch3
from beats import T
from kit import chapter_backdrop, P3, RC, X1, Y0, add_rail, glow, sans, smooth01, tag_under, tex

from atoms import B_SC, CY, YH
from atoms import frames as _frames


def _carry(s):
    """c03_s02's last frame (τ = 15), fading out as the scene opens."""
    t0 = float(s.start)
    op = fade(t0 - 5, dur=0.1, out=t0 + 0.1, out_dur=0.7)
    s.manim(z=6, opacity=op).add(ch3.helix(15.0, 0))
    glow(s, C.schrod, z=7, k=0.4, opacity=op).add(ch3.helix(15.0, 1))
    m = s.manim(z=5, opacity=op)
    m.add(ch3.prob(15.0, 1.0))
    m.add(Line(P3(ch3.XA, ch3.YAX), P3(ch3.XB, ch3.YAX), stroke_color=C.ghost, stroke_width=1.2),
          Line(P3(ch3.XA, ch3.YB), P3(ch3.XB, ch3.YB), stroke_color=C.ghost, stroke_width=1.2))
    wall_w = (ch3.XB - ch3.XA) * 1.4 / (ch3.WIN[1] - ch3.WIN[0])
    m.add(Rectangle(width=wall_w, height=4.75, stroke_width=0, fill_color=C.muted, fill_opacity=0.12)
          .move_to(P3(ch3.wave_x(0), -0.4)), sans("wall", 22, C.muted).move_to(P3(ch3.wave_x(0), 2.6)))
    e = Eqn(r"i\hbar\,\partial_t\psi=\hat H\psi", colors={r"\psi": C.schrod, r"\partial_t": C.schrod,
                                                          r"\hat H": C.schrod})
    e.scale(0.85).move_to(P3(RC + 0.6, 2.7))
    m.add(e, tag_under(e, r"\partial_t", "change", C.schrod), tag_under(e, r"\hat H", "energy", C.schrod))
    p = Eqn(r"P=|\psi|^2", colors={r"\psi": C.schrod}).scale(0.8)
    m.add(VGroup(p, sans("chance", 22, C.schrod)).arrange(DOWN, buff=0.12).move_to(P3(5.55, -0.75)))
    wheel = VGroup(*[Line(P3(0, 0), P3(0.26 * math.cos(a), 0.26 * math.sin(a)), stroke_width=4,
                          stroke_color=ch3.phase_color(a)) for a in np.linspace(0, 2 * np.pi, 48, endpoint=False)])
    m.add(VGroup(wheel, sans("phase", 22, C.muted)).arrange(RIGHT, buff=0.18).move_to(P3(X1, Y0 + 0.2),
                                                                                      aligned_edge=RIGHT))
    x, psi = ch3.psi_at(15.0)
    q = np.abs(psi) ** 2
    tr = x > 0.8
    frac = float(np.trapezoid(q[tr], x[tr]))
    xc = float(np.trapezoid(x[tr] * q[tr], x[tr]) / frac)
    m.add(sans(f"{frac * 100:.0f}%", 28, C.schrod).move_to(P3(ch3.wave_x(xc), ch3.YB + ch3.K2 * q[tr].max() + 0.3)))
    return op


def _icons():
    mu = C.muted
    laser = VGroup(Rectangle(width=0.62, height=0.26, stroke_color=mu, stroke_width=2),
                   Line(P3(0.31, 0), P3(0.36, 0), stroke_color=mu, stroke_width=2))
    beam = Line(P3(0.38, 0), P3(1.05, 0), stroke_color=C.schrod, stroke_width=3)
    laser = VGroup(laser, beam).move_to(ORIGIN)
    body = Square(0.5, stroke_color=mu, stroke_width=2)
    core = Square(0.2, stroke_color=C.schrod, stroke_width=2)
    pins = VGroup()
    for k in (-0.15, 0, 0.15):
        for a, b in (((k, 0.25), (k, 0.36)), ((k, -0.25), (k, -0.36)), ((0.25, k), (0.36, k)), ((-0.25, k), (-0.36, k))):
            pins.add(Line(P3(*a), P3(*b), stroke_color=mu, stroke_width=2))
    chip = VGroup(body, core, pins)
    mri = VGroup(Circle(radius=0.34, stroke_color=mu, stroke_width=5), Circle(radius=0.17, stroke_color=C.schrod,
                                                                            stroke_width=2),
                 Line(P3(-0.5, -0.1), P3(0.5, -0.1), stroke_color=mu, stroke_width=2))
    out = []
    for icon, word, x in ((laser, "lasers", -2.6), (chip, "chips", 0.0), (mri, "MRI", 2.6)):
        icon.move_to(P3(x, -2.2))
        out.append(VGroup(icon, sans(word, 22, C.muted).move_to(P3(x, -2.82))))
    return out


@scene(T.c03_s03, T.c04_s01)
def s12_c03_atoms(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 3, last=True)
    add_rail(s, 3)
    t_n, t_sh, t_ch = T.c03_s03_nucleus, T.c03_s03_shapes, T.c03_s03_chemistry
    t_las, t_sw, t_lg = T.c03_s03_lasers, T.c03_s03_swirls, T.c03_s03_larger
    _carry(s)
    hud = s.manim(z=50, parallax=0.0)
    leg = VGroup(Dot(radius=0.07, color=C.schrod), tex(r"\psi>0", 30, C.muted), Dot(radius=0.07, color=C.e_field),
                 tex(r"\psi<0", 30, C.muted)).arrange(RIGHT, buff=0.14)
    leg[2].shift(0.2 * RIGHT)
    leg[3].shift(0.2 * RIGHT)
    leg.move_to(P3(X1, Y0 + 0.2), aligned_edge=RIGHT)
    hud.play(FadeIn(leg), at=t_sh + 0.6, dur=0.6)
    hud.play(FadeOut(leg), at=t_ch - 1.6, dur=0.6)

    # the clouds (one additive raster for all of them)
    s.add(FramesLayer(_frames(), height=2 * YH, pos=(0, 0), z=4, during=[(t_n - 0.3, s.end)]))

    # nuclei
    def nuclei(t):
        go = lambda a, d=1.2: float(smooth01((t - float(a)) / d))
        merge = go(float(t_ch) - 1.6, 0.8)
        op = go(float(t_n) - 0.2, 0.5) * (1 - go(float(t_sw) - 0.4, 0.8))
        g = VGroup()
        if merge < 1:
            x1 = -4.2 * go(float(t_sh) - 0.1, 1.3)
            pts = [(x1, 1.0)] + [(0.0, go(float(t_sh) + 0.1)), (4.2, go(float(t_sh) + 0.7))]
            for x, a in pts:
                g.add(Dot(P3(x, CY), radius=0.04, color=C.light, fill_opacity=op * a * (1 - merge)))
        if merge > 0:
            d = 2.3 + (0.7 * B_SC - 2.3) * go(float(t_ch) - 0.7, 1.0)
            for x in (d, -d):
                g.add(Dot(P3(x, CY), radius=0.04, color=C.light, fill_opacity=op * merge))
        return g
    glow(s, C.light, z=8, k=1.0).redraw(nuclei, during=(t_n - 0.4, t_sw + 0.6))

    # shapes: the three lowest kinds, named
    m = s.manim(z=10)
    labs = [sans(k, 26, C.muted).move_to(P3(x, -1.75)) for k, x in (("1s", -4.2), ("2p", 0.0), ("3d", 4.2))]
    m.play(FadeIn(labs[0]), at=t_sh + 0.6, dur=0.5)
    m.play(FadeIn(labs[1]), at=t_sh + 0.9, dur=0.5)
    m.play(FadeIn(labs[2]), at=t_sh + 1.4, dur=0.5)
    m.play(FadeOut(VGroup(*labs)), at=t_ch - 1.6, dur=0.6)
    e = Eqn(r"\psi_{n\ell m}(r,\theta,\phi)", colors={r"\psi": C.schrod}).scale(0.85).move_to(P3(RC + 0.6, 2.7))
    m.play(FadeIn(e, shift=0.06 * UP), at=t_sh + 0.2, dur=0.7)
    m.play(FadeOut(e), at=t_ch - 1.6, dur=0.6)

    # chemistry: two atoms share one cloud
    bond = sans("one shared cloud: a bond", 24, C.text).move_to(P3(0, -2.35))
    m.play(FadeIn(bond, shift=0.06 * UP), at=t_ch + 0.6, dur=0.6)
    m.play(FadeOut(bond), at=t_las - 0.3, dur=0.4)

    # lasers, chips, MRI
    icons = _icons()
    for i, ic in enumerate(icons):
        m.play(FadeIn(ic, shift=0.1 * UP), at=t_las + 0.55 * i, dur=0.6)
    m.play(FadeOut(VGroup(*icons)), at=t_sw - 0.6, dur=0.6)
