"""c01_s03 · Light (payoff). Storyboard: plan/scene_plan.md § c01_s03.

Starts where c01_s02 ends: the B rings around the capacitor gap and the four laws in the column. The rings become a
chain of alternating E and B loops (each changing field makes the next), which unrolls into a travelling E ⊥ B wave
drawn in oblique 3D; the view turns from nearly side-on to three-quarter as it goes. The column condenses, and
c = 1/√(μ₀ε₀) is computed from the SI constants (eqdata) and matches the speed of light. On "radio" a dipole antenna
radiates (the analytic Hertzian-dipole field, animated through its phase) and a log-wavelength ruler slides from
visible light to radio and WiFi. On "straight lines" everything clears for one ray of light; on "heavy" a mass
appears below its path (chapter 2 bends it).
"""
import math

import numpy as np
from aion import *

import eqdata as eq
import sims as sm
from beats import T
from ch1 import SC, gap_rings, laws, ring, underline_dEdt
from kit import chapter_backdrop, P3, RC, XW, YH, add_rail, sphere_rgba, polyline, sans, shade, smooth01, tex, tint

AX0, AX1, AY = -4.75, 2.05, SC[1]                 # the wave's axis
K = 2 * np.pi / 2.25                              # wave number (world units)
V = 1.4                                           # drawn wave speed (front and crests move together)
ANT = (AX0 - 0.95, AY)                            # the antenna, at the wave's source
RAY_Y = 0.95
XS = np.linspace(AX0, AX1, 420)


# ------------------------------------------------------------------------------------------------ chain → wave
def _chain_links():
    """Alternating B (upright) and E (flat) loops along the axis, ordered outwards from the stage centre."""
    links = []
    for j in range(-1, 3):
        links.append(("B", SC[0] + 1.5 * j))
    for j in range(-2, 3):
        links.append(("E", SC[0] + 1.5 * j + 0.75))
    links = [l for l in links if -4.6 < l[1] < 2.0]
    return sorted(links, key=lambda l: abs(l[1] - SC[0]))


LINKS = _chain_links()


def _chain(t, op_out):
    t0 = float(T.c01_s03) + 0.25
    t4 = float(T.c01_s02_changing_electric)
    g = VGroup()
    for i, (kind, x) in enumerate(LINKS):
        a = float(smooth01((t - t0 - 0.2 * i) / 0.35)) * op_out
        if a < 0.01:
            continue
        if kind == "B":
            g.add(ring(x, AY, 0.36, 1.55, C.b_field, 1.6 * (t - t4), a))
        else:
            g.add(ring(x, AY, 1.55, 0.36, C.e_field, 1.6 * (t - t4) + np.pi / 2, a))
    return g


def _view(t):
    """Projection of (x, y, z) → screen: turns from near side-on to three-quarter (a camera orbit without 3D)."""
    u = float(smooth01((t - float(T.c01_s03_feed_each_other)) / 6.5))
    return 0.12 + (0.55 - 0.12) * u, 0.10 + (0.42 - 0.10) * u


def _wave_values(t):
    tau = t - float(T.c01_s03_feed_each_other) - 0.2
    xf = AX0 + V * max(tau, 0.0)
    env = smooth01((xf - XS) / 0.5)
    val = np.sin(K * (XS - xf)) * env * 1.05
    return xf, val


def _wave(t, op, width=3.4, glow=False):
    """E (vertical plane) and B (horizontal plane, drawn receding) in phase, travelling along +x at speed V."""
    g = VGroup()
    if op < 0.01:
        return g
    px, py = _view(t)
    xf, val = _wave_values(t)
    proj = lambda x, y, z: (x - px * z, AY + y - py * z)  # noqa: E731
    live = XS <= max(xf, AX0 + 0.02)
    xs, v = XS[live], val[live]
    if len(xs) < 3:
        return g
    if not glow:
        g.add(Line(P3(*proj(AX0 - 0.3, 0, 0)), P3(*proj(AX1 + 0.3, 0, 0)), stroke_color=C.muted, stroke_width=2,
                   stroke_opacity=op))
        for x, b in zip(xs[::10], v[::10]):
            g.add(Line(P3(*proj(x, 0, 0)), P3(*proj(x, 0, b)), stroke_color=C.b_field, stroke_width=1.3,
                       stroke_opacity=0.5 * op),
                  Line(P3(*proj(x, 0, 0)), P3(*proj(x, b, 0)), stroke_color=C.e_field, stroke_width=1.3,
                       stroke_opacity=0.5 * op))
    g.add(polyline([proj(x, 0, b) for x, b in zip(xs, v)], C.b_field, width, op),
          polyline([proj(x, b, 0) for x, b in zip(xs, v)], C.e_field, width, op))
    if not glow:
        la = op * float(smooth01((t - float(T.c01_s03_feed_each_other) - 1.2) / 0.6)) \
             * (1 - float(smooth01((t - float(T.c01_s03_radio) + 0.6) / 0.5)))
        g.add(tex(r"\mathbf E", 36, C.e_field).set_opacity(la).move_to(P3(*proj(AX0 - 0.35, 1.0, 0))),
              tex(r"\mathbf B", 36, C.b_field).set_opacity(la).move_to(P3(*proj(AX0 - 0.35, 0, 1.15))),
              tex("c", 32, C.muted).set_opacity(la).move_to(P3(*proj(AX1 + 0.6, 0, 0))))
    return g


# ------------------------------------------------------------------------------------------------ antenna, ruler
def _antenna(t, op):
    s = math.cos(3.6 * (t - float(T.c01_s03_radio)))
    top, bot = (C.charge_p, C.charge_n) if s >= 0 else (C.charge_n, C.charge_p)
    r = 0.07 + 0.08 * abs(s)
    return VGroup(Line(P3(ANT[0], ANT[1] - 0.5), P3(ANT[0], ANT[1] + 0.5), stroke_color=C.light, stroke_width=4,
                       stroke_opacity=op),
                  Circle(radius=r, stroke_width=0, fill_color=top, fill_opacity=op).move_to(P3(ANT[0], ANT[1] + 0.6)),
                  Circle(radius=r, stroke_width=0, fill_color=bot, fill_opacity=op).move_to(P3(ANT[0], ANT[1] - 0.6)))


BANDS = [("radio", 3, 0), ("microwave", 0, -3), ("infrared", -3, -6.15), ("visible", -6.15, -6.4),
         ("UV", -6.4, -8), ("X-ray", -8, -11), ("gamma", -11, -12)]      # log10 of wavelength in metres
RUL_Y, RUL_X0, RUL_X1 = 2.75, -6.0, 1.8


def _rx(L):
    return RUL_X0 + (3 - L) / 15 * (RUL_X1 - RUL_X0)


def _ruler():
    bars, labs, lit = VGroup(), VGroup(), VGroup()
    for name, a, b in BANDS:
        xa, xb = _rx(a) + 0.015, _rx(b) - 0.015
        col = C.light if name == "visible" else tint(C.muted, 0.5)
        bars.add(Rectangle(width=xb - xa, height=0.11, stroke_width=0, fill_color=col, fill_opacity=1)
                 .move_to(P3((xa + xb) / 2, RUL_Y)))
        if name in ("radio", "microwave"):
            lit.add(Rectangle(width=xb - xa, height=0.11, stroke_width=0, fill_color=C.maxwell, fill_opacity=1)
                    .move_to(P3((xa + xb) / 2, RUL_Y)))
        labs.add(sans(name, 17, C.light if name == "visible" else C.muted).move_to(P3((_rx(a) + _rx(b)) / 2,
                                                                                         RUL_Y - 0.24)))
    return bars, labs, lit


def _marker(t):
    u = float(smooth01((t - float(T.c01_s03_signal) + 0.1) / 1.4))
    x = _rx(-6.27) + (_rx(-0.92) - _rx(-6.27)) * u                     # visible light → WiFi (12 cm)
    tri = Triangle(stroke_width=0, fill_color=C.light, fill_opacity=1).scale(0.07).rotate(np.pi)
    return tri.move_to(P3(x, RUL_Y + 0.17))


# ------------------------------------------------------------------------------------------------ the scene
@scene(T.c01_s03, T.c02_s01)
def s06_c01_light(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 1, last=True)
    add_rail(s, 1)
    t_feed, t_empty, t_speed, t_light = (T.c01_s03_feed_each_other, T.c01_s03_empty_space, T.c01_s03_its_speed,
                                         T.c01_s03_speed_of_light)
    t_radio, t_signal, t_straight, t_heavy = (T.c01_s03_radio, T.c01_s03_signal, T.c01_s03_straight_lines,
                                              T.c01_s03_heavy)
    clear = t_straight - 0.9                                            # everything leaves for the single ray
    op_main = fade(s.start - 2, dur=0.1, out=clear, out_dur=0.8)

    hud = s.manim(z=50, parallax=0.0)

    # the column as c01_s02 left it; then the two swirl laws step forward
    col = s.manim(z=20, parallax=0.0)
    rows = laws()
    for i in range(3):
        VGroup(*rows[i]).set_opacity(0.42)
    under = underline_dEdt(rows[3][0])
    col.add(*[VGroup(*r) for r in rows], under)
    col.play(VGroup(*rows[0], *rows[1]).animate.set_opacity(0.22), VGroup(*rows[2]).animate.set_opacity(1.0),
             at=t_feed, dur=0.6)
    # 'empty space': the stack condenses to the top of the column (the frame-03 layout)
    tgt = VGroup(*[r[0].copy().set_opacity(0.85) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    tgt.scale_to_fit_width(3.0).move_to(P3(RC + 0.1, 1.95))
    col.play(*[Transform(rows[i][0], tgt[i]) for i in range(4)], Transform(under, underline_dEdt(tgt[3])),
             FadeOut(VGroup(*[r[1] for r in rows])), at=t_empty, dur=1.2)
    shade(s, tgt.get_center()[0], tgt.get_center()[1], tgt.width + 0.5, tgt.height + 0.4, z=15, parallax=0.0,
          opacity=fade(t_radio - 0.2, dur=0.8, out=clear, out_dur=0.8))

    # c from μ0 and ε0, computed; it is the speed of light
    ce = Eqn(r"c=\frac{1}{\sqrt{\mu_0\varepsilon_0}}", colors={r"\mu_0": C.b_field, r"\varepsilon_0": C.e_field})
    val = eq.c_from_maxwell()
    num = tex(rf"\approx {val / 1e8:.3f}\times10^{{8}}\ \mathrm{{m/s}}", 32)
    sol = sans("speed of light", 26, C.light)
    cg = VGroup(ce.scale(0.95), num, sol).arrange(DOWN, buff=0.22).move_to(P3(RC + 0.2, -1.6))
    shade(s, cg.get_center()[0], cg.get_center()[1], cg.width + 0.5, cg.height + 0.4, z=15, parallax=0.0,
          opacity=fade(t_radio - 0.2, dur=0.8, out=clear, out_dur=0.8))
    col.play(Write(ce), at=t_speed, dur=1.0)
    col.play(FadeIn(num, shift=0.08 * UP), at=t_light - 0.55, dur=0.6)
    col.play(FadeIn(sol, shift=0.08 * UP), at=t_light, dur=0.5)
    col.play(FadeOut(VGroup(*[r[0] for r in rows], under, cg)), at=clear, dur=0.8)

    # the gap rings hand over to a chain of loops, which unrolls into the wave
    chain_out = fade(s.start - 2, dur=0.1, out=t_feed + 0.6, out_dur=1.2)
    s.manim(z=6).redraw(lambda t: gap_rings(t, 1.0 - float(smooth01((t - float(s.start) - 0.2) / 0.8))),
                        during=(s.start, s.start + 1.4))
    s.manim(z=6).redraw(lambda t: _chain(t, float(chain_out(t))), during=(s.start, t_feed + 2.2))
    s.manim(z=5).redraw(lambda t: _wave(t, float(op_main(t))), during=(t_feed - 0.3, clear + 1.0))
    lit = pulse(t_light, amp=0.9, dur=1.8)
    s.manim(z=7, fx=[Glow(C.light, strength=C.glow * 1.3, radius=C.glow_r)]) \
        .redraw(lambda t: _wave(t, float(lit(t)), width=3.0, glow=True), during=(t_light - 1.0, t_light + 1.2))

    # radio: a dipole antenna radiating (Hertzian dipole, B_z), widening the picture
    ext = (2 * XW + 1.4, 2 * YH + 0.8)
    nx, ny = int(ext[0] * 42), int(ext[1] * 42)
    s.add(FieldLayer(lambda t: sm.dipole_field(nx, ny, extent=ext, k=3.0, phase=4.2 * (t - float(t_radio)),
                                               origin=ANT) ** 2,
                     cmap="ramp", colors=(C.bg, C.bg, tint(C.b_field, 0.16)), vmin=0, vmax=1, extent=ext,
                     z=-3, opacity=fade(t_radio - 0.2, dur=1.0, out=clear, out_dur=0.8),
                     start=t_radio - 0.5, end=clear + 1.0))
    ant_op = fade(t_radio - 0.2, dur=0.6, out=clear, out_dur=0.8)
    s.manim(z=8).redraw(lambda t: _antenna(t, float(ant_op(t))), during=(t_radio - 0.5, clear + 1.0))
    s.camera.frame(t_radio - 0.2, center=(-0.25, 0.1), zoom=0.95, dur=2.5)

    # the spectrum: light is one sliver; radio and WiFi are the same wave, longer
    bars, labs, band_lit = _ruler()
    ru = s.manim(z=30, parallax=0.0)
    ru.play(FadeIn(VGroup(bars, labs)), at=t_radio + 0.5, dur=0.7)
    ru.play(FadeIn(band_lit), at=t_signal + 0.4, dur=0.8)
    ru.play(FadeOut(VGroup(bars, labs, band_lit)), at=clear, dur=0.8)
    mk_op = fade(t_radio + 0.5, dur=0.7, out=clear, out_dur=0.8)
    s.manim(z=31, parallax=0.0).redraw(lambda t: _marker(t).set_opacity(float(mk_op(t))),
                                       during=(t_radio + 0.2, clear + 1.0))

    # straight lines: one ray crosses the empty frame; then something heavy sits below its path
    s.camera.frame(clear, center=(0, 0), zoom=1.0, dur=1.2)
    t_ray = float(t_straight) - 0.35

    def ray(t):
        xh = min(-XW - 0.4 + 11.0 * (t - t_ray), XW + 0.4)
        g = VGroup()
        if xh <= -XW - 0.39:
            return g
        g.add(Line(P3(-XW - 0.4, RAY_Y), P3(xh, RAY_Y), stroke_color=C.light, stroke_width=2.4))
        if xh < XW + 0.3:
            g.add(Dot(P3(xh, RAY_Y), radius=0.06, color=C.light))
        return g
    s.manim(z=10, fx=[Glow(C.light, strength=C.glow * 0.55, radius=C.glow_r)]).redraw(ray, during=(t_ray, s.end))
    s.add(ArrayLayer(sphere_rgba(C.mass), height=1.75, pos=(2.7, -0.5), z=4, opacity=fade(t_heavy - 0.3, dur=1.2)))
