"""c02_s02 · The equation. Storyboard: plan/scene_plan.md § c02_s02. Layout L2.

The sheet from c02_s01 drifts to the left stage and keeps orbiting (one chapter-wide view, ch2.view). The field
equations write into the right column; the left side (shape) lights in the chapter hue, the right side (matter) in
the light token. On Wheeler's line two arrows loop between the halves. On 'eclipse' the stage turns to the 1919
eclipse: the Moon covers the Sun, and the stars around it move outward from where they were, by the deflection
GR predicts, 1.75″·R☉/b (aion.maths.schwarzschild), drawn 400× larger.
"""
import numpy as np
from aion import *
from aion.maths import schwarzschild as S

import ch2
from beats import T
from kit import chapter_backdrop, COL, P3, RC, add_rail, glimpse, sans, shade, sphere_rgba, tex

SCN = np.array([-2.35, 0.2])                     # eclipse: the Sun's centre on the stage
RS = 0.55                                        # its radius on screen
EXAG = 400.0
SUN_ARCSEC = 959.6                               # the Sun's angular radius seen from Earth (″)


def _stars():
    """Seeded field stars around the Sun: position, distance (in solar radii) and size."""
    rng = np.random.default_rng(1919)
    out = []
    while len(out) < 38:
        d = rng.uniform(1.5, 4.5) * RS
        a = rng.uniform(0, 2 * np.pi)
        p = SCN + d * np.array([np.cos(a), np.sin(a)])
        if abs(p[1] - SCN[1]) < 2.25 and p[0] < 0.35 and p[0] > -6.0:
            out.append((p, d / RS, rng.uniform(0.022, 0.045)))
    return out


def _shift_units(b):
    """GR's bend for a ray passing b solar radii from the Sun's centre, as a shift on screen (×EXAG)."""
    return S.sun_grazing_arcsec() / b * EXAG / SUN_ARCSEC * RS


@scene(T.c02_s02, T.c02_s03)
def s08_c02_equation(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 2)
    add_rail(s, 2, busy=True)
    t_ecl, t_pred = T.c02_s02_eclipse, T.c02_s02_predicted

    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "photo:eclipse_1919.jpg", t_ecl + 0.1, C.einstein, dur=4.2)   # the real 1919 plate

    # the sheet keeps going on the left stage, then makes way for the eclipse
    op_sheet = fade(s.start - 5, dur=0.1, out=t_ecl - 0.4, out_dur=1.0)
    s.manim(z=-6).redraw(lambda t: ch2.sheet(t, float(op_sheet(t)))[0], during=(s.start, t_ecl + 1.0))
    s.manim(z=-2).redraw(lambda t: ch2.sheet(t, float(op_sheet(t)))[1], during=(s.start, t_ecl + 1.0))
    s.add(ArrayLayer(sphere_rgba(C.mass), height=1.0, pos=lambda t: ch2.sun_screen(t)[0],
                     scale=lambda t: ch2.sun_screen(t)[1], z=-4, opacity=op_sheet, end=t_ecl + 1.0))
    s.manim(z=-5).redraw(lambda t: ch2.marble(t, float(op_sheet(t)), True), during=(s.start, t_ecl + 1.0))
    s.manim(z=-1).redraw(lambda t: ch2.marble(t, float(op_sheet(t)), False), during=(s.start, t_ecl + 1.0))

    # the field equations: shape = matter
    col = s.manim(z=20, parallax=0.0)
    G, L, Tm = r"G_{\mu\nu}", r"\Lambda g_{\mu\nu}", r"T_{\mu\nu}"
    e = Eqn(r"G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}\,T_{\mu\nu}", colors={G: C.text, L: C.text, Tm: C.text})
    e.scale_to_fit_width(COL[1] - COL[0]).move_to(P3(RC, 0.55))
    left = VGroup(e.part(G), e.part(L))
    y_tag = e.get_bottom()[1] - 0.32
    t_shape = sans("shape", 24, C.einstein).move_to(P3(left.get_center()[0], y_tag))
    t_matter = sans("matter", 24, C.light).move_to(P3(e.part(Tm).get_center()[0], y_tag))
    col.play(Write(e), at=T.c02_s02_single_line, dur=1.4)
    col.play(left.animate.set_color(C.einstein), at=T.c02_s02_shape, dur=0.5)
    col.play(FadeIn(t_shape, shift=0.08 * UP), at=T.c02_s02_shape + 0.2, dur=0.5)
    col.play(e.part(Tm).animate.set_color(C.light), at=T.c02_s02_matter_and_energy, dur=0.5)
    col.play(FadeIn(t_matter, shift=0.08 * UP), at=T.c02_s02_matter_and_energy + 0.2, dur=0.5)

    # Wheeler: matter tells spacetime how to curve; spacetime tells matter how to move
    top_a = e.part(Tm).get_top() + 0.18 * UP
    top_b = left.get_top() + 0.18 * UP
    arc1 = CurvedArrow(top_a, top_b, angle=0.9, color=C.light, stroke_width=2.6, tip_length=0.16)
    lab1 = sans("curve", 22, C.light).next_to(arc1, UP, buff=0.08)
    bot_a = P3(left.get_center()[0], y_tag - 0.25)
    bot_b = P3(e.part(Tm).get_center()[0], y_tag - 0.25)
    arc2 = CurvedArrow(bot_a, bot_b, angle=0.9, color=C.einstein, stroke_width=2.6, tip_length=0.16)
    lab2 = sans("move", 22, C.einstein).next_to(arc2, DOWN, buff=0.08)
    t_w = T.c02_s02_wheeler
    col.play(Create(arc1), at=t_w + 1.3, dur=0.8)
    col.play(FadeIn(lab1), at=t_w + 1.8, dur=0.4)
    col.play(Create(arc2), at=t_w + 3.3, dur=0.8)
    col.play(FadeIn(lab2), at=t_w + 3.8, dur=0.4)

    # 1919: the Moon covers the Sun; the stars beside it appear moved outward
    sun = Circle(radius=RS, stroke_width=0, fill_color=C.light, fill_opacity=1).move_to(P3(*SCN))
    sg = s.manim(z=2, fx=[Glow(C.light, strength=C.glow * 1.2, radius=C.glow_r)])
    sg.play(FadeIn(sun), at=t_ecl - 0.4, dur=0.8)
    sg.play(FadeOut(sun), at=t_ecl + 2.7, dur=0.5)                 # covered: only the corona is left
    moon = Circle(radius=RS * 1.01, stroke_width=0, fill_color=C.bg, fill_opacity=1).move_to(P3(SCN[0] - 3.2, SCN[1]))
    mm = s.manim(z=3)
    mm.add(moon)
    mm.play(moon.animate(rate_func=rate_functions.ease_out_cubic).move_to(P3(*SCN)), at=t_ecl + 1.2, dur=1.6)
    corona = VGroup(Circle(radius=RS * 1.04, stroke_color=C.light, stroke_width=3),
                    Circle(radius=RS * 1.18, stroke_color=C.light, stroke_width=1.5, stroke_opacity=0.35)) \
        .move_to(P3(*SCN))
    cg = s.manim(z=4, fx=[Glow(C.light, strength=C.glow * 0.6, radius=C.glow_r)])
    cg.play(FadeIn(corona), at=t_ecl + 1.0, dur=0.9)

    stars = _stars()
    st = s.manim(z=1)
    t_move = float(t_ecl) + 3.0

    def star_field(t):
        a = float(smooth(np.clip((t - float(t_ecl) + 0.2) / 0.8, 0, 1)))
        u = float(smooth(np.clip((t - t_move) / 1.8, 0, 1)))
        g = VGroup()
        for p, b, r in stars:
            out = (p - SCN) / np.linalg.norm(p - SCN)
            q = p + out * _shift_units(b) * u
            if u > 0:
                g.add(Circle(radius=0.07, stroke_color=C.muted, stroke_width=1.3, stroke_opacity=a * min(1, 3 * u))
                      .move_to(P3(*p)))
            g.add(Dot(P3(*q), radius=r, color=C.light, fill_opacity=a))
        return g
    st.redraw(star_field, during=(t_ecl - 0.5, s.end))

    val = S.sun_grazing_arcsec()
    lab = VGroup(tex(rf"{val:.2f}''", 30, C.einstein), sans("at the Sun's edge", 22, C.muted)) \
        .arrange(RIGHT, buff=0.14).move_to(P3(SCN[0] + RS + 0.35, SCN[1] - RS - 0.45), aligned_edge=LEFT)
    note = sans(f"shifts drawn {int(EXAG)} times larger", 20, C.muted).move_to(P3(SCN[0], SCN[1] - 2.45))
    shade(s, lab.get_center()[0], lab.get_center()[1], lab.width + 0.5, lab.height + 0.35, a=0.95, z=5,
          opacity=fade(t_pred))
    tg = s.manim(z=6)
    tg.play(FadeIn(note), at=t_move, dur=0.6)
    tg.play(FadeIn(lab, shift=0.08 * UP), at=t_pred, dur=0.6)

    # a slow push into the eclipse
    s.camera.frame(t_ecl + 0.6, center=(SCN[0] + 0.5, SCN[1]), zoom=1.12, dur=4.0)
