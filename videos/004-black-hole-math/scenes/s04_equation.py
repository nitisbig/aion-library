"""s04 chapter 3: the equation. u = 1/r; a straight line is u'' + u = 0; Einstein adds one term.
Test on the Sun: 1.75 arc seconds, exactly twice the thrown-ball answer (pays off chapter 1's plant)."""
from functools import lru_cache

from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import badge_newton, breathe, glow_fx, photons

B = 1.6                                                   # impact parameter of the ray we follow (world units)
LC, LK = np.array([-3.6, -0.15, 0.0]), 0.72               # ray panel: centre and scale once it has moved left
PO, PW, PH, PHI_END = np.array([1.6, -0.7, 0.0]), 4.5, 2.25, 3.75   # plot: origin, width, height for u·b = 1
EQ_POS = np.array([-2.7, -2.8, 0.0])

t_mv = T.cut_ch3 + 0.5                                    # the picture from chapter 2 slides left
MOVE = key(t_mv, 0.0, 1.0, dur=2.4, ease="easy_ease", lead=0)
RS = keys((T.cut_ch3, 0.22), (T.mass_away + 0.3, 0.22), (T.mass_away + 2.0, 0.0), (T.new_term, 0.0),
          (T.new_term + 4.6, 0.30), default_ease="easy_ease")
t_sw0, t_sw1 = T.sine - 2.6, T.peaks + 2.3                # the sweep that traces the plot
PHI = keys((T.phi - 2.2, 0.45), (T.phi, 1.0), (T.far - 1.4, 1.0), (T.far, 0.32), (T.close - 1.2, 0.32),
           (T.close + 0.4, PI / 2), (T.mass_away + 2.4, PI / 2), (t_sw0, 0.12), (T.peaks, PI / 2), (t_sw1, 3.02),
           (T.tiny - 1.2, 3.02), (T.tiny - 1.19, 0.3), (T.wakes - 1.6, 0.3), (T.wakes + 0.9, 1.75),
           default_ease="easy_ease")
PROBE_ON = fade(T.phi - 2.4, dur=0.6, out=T.famous - 1.0, lead=0) + fade(T.tiny - 1.1, dur=0.6, out=T.test - 0.4, lead=0)
PANEL_ON = 1.0 - key(T.test - 0.9, 0.0, 1.0, dur=0.8, lead=0)


@lru_cache(maxsize=512)
def _orbit(rs):
    return S.orbit(B, rs, phi_max=2 * PI)


def orbit(t):
    return _orbit(round(float(RS(t)), 4))


def to_screen(xy, t):
    u = float(MOVE(t))
    c = np.array([0.0, -0.1, 0.0]) * (1 - u) + LC * u
    k = 1.0 + (LK - 1.0) * u
    xy = np.atleast_2d(xy)
    return np.column_stack([c[0] + k * xy[:, 0], c[1] + k * xy[:, 1], np.zeros(len(xy))])


def at_phi(phi, t):
    """World position of the light at angle phi (it comes in from −x)."""
    ph, u, _ = orbit(t)
    r = 1.0 / max(float(np.interp(phi, ph, u)), 1e-6)
    return np.array([-r * np.cos(phi), r * np.sin(phi)])


def ray_mob(t):
    ph, u, _ = orbit(t)
    keep = u > 1.0 / 14.0
    r = 1.0 / u[keep]
    scr = to_screen(np.column_stack([-r * np.cos(ph[keep]), r * np.sin(ph[keep])]), t)
    xmax = 7.4 + (-0.35 - 7.4) * float(MOVE(t))
    scr = scr[(scr[:, 0] > -7.4) & (scr[:, 0] < xmax) & (np.abs(scr[:, 1]) < 4.2)]
    return VMobject(stroke_color=C.light, stroke_width=C.stroke, stroke_opacity=float(PANEL_ON(t))) \
        .set_points_as_corners(scr)


def in_panel(p):
    """Is a screen point inside the ray panel? (the probe hides while the light is far outside it)"""
    return -7.2 < p[0] < -0.45 and abs(p[1]) < 3.6


def plot_xy(phi, ub):
    return PO + np.array([PW * phi / PHI_END, PH * ub, 0.0])


@scene(T.cut_ch3, T.cut_ch4)
def s04_equation(s):
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim()
    newton_badge = badge_newton()                          # returns just before its payoff
    m.play(FadeIn(newton_badge, shift=0.2 * UP), at=T.twice - 3.4, dur=0.7)
    breathe(s, T.cut_ch3 + 3.5, T.cut_ch4)

    # ── the ray picture (continues from chapter 2), with a probe that reads φ and r ──
    t_panel = (T.cut_ch3, T.test)
    ray = glow.redraw(ray_mob, during=t_panel)
    glow.remove(ray, at=T.test)

    mass = Dot(radius=0.2, color=C.mass)
    mass_op = (1.0 - key(T.mass_away, 0.0, 1.0, dur=1.2, lead=0)) + key(T.mass_back - 0.3, 0.0, 1.0, dur=0.8, lead=0)
    m.add(mass)
    m.drive(mass, lambda d, t: d.move_to(to_screen([0, 0], t)[0]).set_opacity(float(mass_op(t) * PANEL_ON(t))),
            during=t_panel)

    def probe(t):
        op = float(np.clip(PROBE_ON(t), 0, 1) * PANEL_ON(t))
        phi = float(PHI(t))
        o, p = to_screen([0, 0], t)[0], to_screen(at_phi(phi, t), t)[0]
        op *= float(in_panel(p))
        if op < 1e-3:
            return VGroup()
        g = VGroup(Line(o, p, color=C.text, stroke_width=C.thin + 1, stroke_opacity=op),
                   Line(o, o + 1.6 * LEFT, color=C.muted, stroke_width=C.thin, stroke_opacity=0.8 * op),
                   Arc(radius=0.55, start_angle=PI, angle=-phi, arc_center=o, color=C.text, stroke_width=C.thin + 1,
                       stroke_opacity=op))
        return g
    m.redraw(probe, during=(T.phi - 2.5, T.test))
    head = Dot(radius=0.09, color=C.text)
    glow.add(head, at=T.phi - 2.5)

    def place_head(d, t):
        p = to_screen(at_phi(float(PHI(t)), t), t)[0]
        d.move_to(p if in_panel(p) else to_screen([0, 0], t)[0])        # hidden: park it inside the frame
        d.set_opacity(float(np.clip(PROBE_ON(t), 0, 1) * PANEL_ON(t) * in_panel(p)))
    glow.drive(head, place_head, during=(T.phi - 2.5, T.test))

    phi_lab, r_lab = Eqn(r"\varphi", size=46), Eqn("r", size=46)
    lab_op = fade(T.phi, dur=0.5, out=T.famous - 1.0, lead=0)

    def place_phi(o, t):
        c, phi = to_screen([0, 0], t)[0], float(PHI(t))
        a = PI - phi / 2
        p = to_screen(at_phi(phi, t), t)[0]
        o.move_to(c + 0.95 * np.array([np.cos(a), np.sin(a), 0])).set_opacity(float(lab_op(t) * in_panel(p)))

    def place_r(o, t):
        c, p = to_screen([0, 0], t)[0], to_screen(at_phi(float(PHI(t)), t), t)[0]
        d = (p - c) / max(np.linalg.norm(p - c), 1e-6)
        n = np.array([d[1], -d[0], 0.0])
        o.move_to(c + 0.62 * (p - c) + 0.3 * n).set_opacity(
            float(fade(T.r, dur=0.5, out=T.famous - 1.0, lead=0)(t) * in_panel(p)))
    m.add(phi_lab, r_lab, at=T.phi - 0.2)
    m.drive(phi_lab, place_phi, during=(T.phi - 0.2, T.famous))
    m.drive(r_lab, place_r, during=(T.phi - 0.2, T.famous))

    # ── the trick: u = 1/r, shown as a bar that shares the plot's vertical scale ──
    u_def = Eqn(r"u = \frac{1}{r}", colors={"u": C.light}, size=60).move_to([3.6, 1.6, 0])
    m.play(Write(u_def), at=T.trick + 2.6, dur=1.6)
    m.play(u_def.animate.scale(0.7).move_to([0.45, 2.55, 0]), at=T.mass_away + 2.6, dur=1.0)

    def ub(t):                                              # u·b at the probe: 1 at closest approach when M = 0
        ph, u, _ = orbit(t)
        return B * float(np.interp(float(PHI(t)), ph, u))

    def bar(x, val, col, on):
        def f(t):
            h = max(PH * val(t), 0.01)
            return Rectangle(width=0.3, height=h, stroke_width=0, fill_color=col,
                             fill_opacity=float(np.clip(on(t), 0, 1) * PANEL_ON(t))).move_to(PO + [x, h / 2, 0])
        return f
    u_bar_on = fade(T.u + 0.3, dur=0.5, out=T.mass_away + 2.2, lead=0) + fade(T.u_squared + 0.6, dur=0.5, lead=0)
    m.redraw(bar(-1.55, ub, C.light, u_bar_on), during=(T.u, T.test))
    u_name = Eqn("u", colors={"u": C.light}, size=40).move_to(PO + [-1.55, -0.32, 0])
    m.add(u_name, at=T.u + 0.3)
    m.drive(u_name, lambda o, t: o.set_opacity(float(np.clip(u_bar_on(t), 0, 1) * PANEL_ON(t))), during=(T.u, T.test))

    # ── no mass: the straight line is a sine wave in u(φ) ────────────────
    axes = VGroup(Line(PO, PO + [PW + 0.25, 0, 0], color=C.muted, stroke_width=C.thin),
                  Line(PO, PO + [0, PH * 1.22, 0], color=C.muted, stroke_width=C.thin))
    ax_phi = Eqn(r"\varphi", size=40).move_to(PO + [PW + 0.45, 0, 0])
    ax_u = Eqn("u", colors={"u": C.light}, size=40).move_to(PO + [0, PH * 1.22 + 0.3, 0])
    m.play(Create(axes), FadeIn(ax_phi), FadeIn(ax_u), at=T.sine - 3.7, dur=0.9)

    def curve(t):
        ph, u, _ = orbit(t)
        lim = float(PHI(t)) if t < t_sw1 else 1e9
        k = (ph <= lim) & (ph <= PHI_END)
        if k.sum() < 2:
            k[:2] = True
        return VMobject(stroke_color=C.light, stroke_width=C.stroke, stroke_opacity=float(PANEL_ON(t))) \
            .set_points_as_corners([plot_xy(a, B * b) for a, b in zip(ph[k][::4], u[k][::4])])
    glow.redraw(curve, during=(t_sw0, T.test))
    cursor = Dot(radius=0.08, color=C.text)
    glow.add(cursor, at=t_sw0)
    glow.drive(cursor, lambda d, t: d.move_to(plot_xy(float(PHI(t)), ub(t))).set_opacity(
        float(np.clip(PROBE_ON(t), 0, 1) * PANEL_ON(t))), during=(t_sw0, T.test))
    sine = Eqn(r"u \propto \sin\varphi", colors={"u": C.light}, size=44).move_to([3.7, 2.2, 0])
    m.play(FadeIn(sine, shift=0.15 * UP), at=T.sine + 0.3, dur=0.6)
    # when the mass returns, the pure sine stays behind as a dashed ghost
    ghost = DashedVMobject(VMobject(stroke_color=C.muted, stroke_width=C.thin).set_points_as_corners(
        [plot_xy(a, np.sin(a)) for a in np.linspace(0, PI, 60)]), num_dashes=40)
    m.play(FadeIn(ghost), FadeOut(sine), at=T.new_term - 0.4, dur=0.6)

    # ── the equation of a straight line, then Einstein's one extra term ──
    eq0 = Eqn(r"u'' + u = 0", colors={"u": C.light}, size=76).move_to(EQ_POS)
    FR = r"\frac{3GM}{c^2}"
    eq1 = Eqn(r"u'' + u = " + FR + r"\,u^2", colors={"u": C.light, FR: C.mass}, size=76)
    eq1.move_to(EQ_POS).align_to(eq0, LEFT)
    m.play(Write(eq0), at=T.famous + 1.9, dur=3.2, lead=0)
    m.play(Indicate(eq0, color=C.text, scale_factor=1.06), at=T.straight_eq, dur=1.0)
    zero = eq0[-1][-1]
    m.play(Indicate(zero, color=C.mass, scale_factor=1.6), at=T.one_place, dur=1.1)
    m.play(TransformMatchingShapes(eq0, eq1), at=T.new_term - 0.5, dur=1.5, ease="easy_ease")
    halo = s.manim(fx=[glow_fx(C.mass, 1.6, 1.4)], z=1, opacity=pulse(T.that_is_it + 0.6, 1.0, dur=2.6))
    halo_eq = eq1.copy()
    halo.add(halo_eq, at=T.that_is_it - 1.0)
    halo.remove(halo_eq, at=T.that_is_it + 2.6)
    m.play(Indicate(eq1.part("u", -1), color=C.light, scale_factor=1.5), at=T.u_squared, dur=1.0)

    # the new term, on the same scale as u: nothing far away, it wakes up close in
    def term(t):
        return 1.5 * float(RS(t)) * (ub(t) / B) ** 2 * B
    t_bar_on = fade(T.u_squared + 0.6, dur=0.5, lead=0)
    m.redraw(bar(-0.85, term, C.mass, t_bar_on), during=(T.u_squared, T.test))
    t_name = Eqn(r"u^2", size=40).set_color(C.mass).move_to(PO + [-0.85, -0.32, 0])
    m.add(t_name, at=T.u_squared + 0.6)
    m.drive(t_name, lambda o, t: o.set_opacity(float(np.clip(t_bar_on(t), 0, 1) * PANEL_ON(t))),
            during=(T.u_squared, T.test))
    m.play(FadeOut(axes), FadeOut(ax_phi), FadeOut(ax_u), FadeOut(ghost), FadeOut(u_def), at=T.test - 0.9, dur=0.8)

    # the equation becomes the badge that stays for the rest of the video
    m.play(eq1.animate.scale(0.5).move_to([0.9, 3.15, 0]), at=T.test - 0.3, dur=1.1, ease="easy_ease")
    m.play(FadeOut(eq1), at=T.sun + 0.6, dur=0.8)             # the stage clears for the Sun

    # ── test it: starlight grazing the Sun ───────────────────────────────
    sc, sr = np.array([-1.2, -1.55, 0.0]), 1.45
    sun = Circle(radius=sr, stroke_color=C.mass, stroke_width=C.thin + 1, fill_color=C.mass, fill_opacity=0.9)
    sun.move_to(sc)
    sun_fx = s.manim(fx=[glow_fx(C.mass, 1.5, 2.2)], z=-1)
    sun_fx.play(FadeIn(sun, scale=0.9), at=T.test + 0.2, dur=0.9)
    bg, rs_show = sr * 1.04, 0.105                          # grazing path, bend exaggerated ≈ 8° (real: 1.75″)

    def bent(rs_):
        p, _ = S.ray(bg, rs=rs_, r_max=9.5)
        p = p[(p[:, 0] + sc[0] > -6.6) & (p[:, 0] + sc[0] < 6.6)]
        return np.column_stack([p[:, 0] + sc[0], p[:, 1] + sc[1], np.zeros(len(p))])
    gr = bent(rs_show)
    star_ray = VMobject(stroke_color=C.light, stroke_width=C.stroke).set_points_as_corners(gr)
    glow.play(Create(star_ray), at=T.sun - 0.8, dur=2.2, ease="easy_ease")
    y0 = gr[0, 1]
    straight = DashedLine([sc[0], y0, 0], [6.6, y0, 0], color=C.muted, stroke_width=C.thin, stroke_opacity=0.7)
    m.play(Create(straight), at=T.arcsec - 1.4, dur=0.8)
    d_out = gr[-1] - gr[-2]
    wedge = Arc(radius=3.4, start_angle=0.0, angle=float(np.arctan2(d_out[1], d_out[0])), arc_center=[sc[0], y0, 0],
                color=C.light, stroke_width=C.thin + 1)
    m.play(Create(wedge), at=T.arcsec - 0.5, dur=0.6)
    val = S.sun_grazing_arcsec()

    def count(t):
        v = val * float(key(T.arcsec - 0.3, 0.0, 1.0, dur=1.5, ease="out_cubic", lead=0)(t))
        num = DecimalNumber(v, num_decimal_places=2, font_size=C.tex_size * 1.25, color=C.light)
        unit = Label("arc seconds", color=C.muted).next_to(num, RIGHT, buff=0.25).align_to(num, DOWN)
        return VGroup(num, unit).move_to([3.9, 1.5, 0], aligned_edge=LEFT).shift(1.6 * LEFT)
    reading = m.redraw(count, during=(T.arcsec - 0.3, T.arcsec + 1.4))
    photons(glow, gr, T.sun + 1.6, T.aim_closer + 2.4)

    # payoff: the thrown-ball ray from chapter 1 comes back, bending exactly half as much
    half = VMobject(stroke_color=C.newton, stroke_width=C.stroke).set_points_as_corners(bent(0.5 * rs_show))
    m.play(FadeOut(newton_badge, shift=0.3 * UP), at=T.twice - 0.9, dur=0.7)
    m.play(Create(half), at=T.twice - 0.5, dur=1.6, ease="easy_ease")
    half_val = VGroup(DecimalNumber(val / 2, num_decimal_places=2, font_size=C.tex_size, color=C.newton))
    half_val.add(Label("thrown ball", color=C.newton).next_to(half_val[0], RIGHT, buff=0.25).align_to(half_val[0], DOWN))
    half_val.move_to([2.3, 0.75, 0], aligned_edge=LEFT)
    times2 = Eqn(r"\times\,2", size=60).move_to([1.35, 1.12, 0])
    m.play(FadeIn(half_val, shift=0.15 * UP), at=T.twice + 0.4, dur=0.6)
    m.play(FadeIn(times2, scale=1.3), at=T.twice + 1.3, dur=0.5, ease="out_back")

    # 1919: the eclipse, and the star that appears shifted
    moon = Circle(radius=sr * 0.985, stroke_width=0, fill_color=C.bg, fill_opacity=1.0).move_to(sc)
    year = Label("1919", color=C.text).move_to([-5.6, 2.3, 0])
    m.play(FadeIn(year, shift=0.15 * UP), at=T.eclipse, dur=0.6)
    m.play(FadeIn(moon), at=T.eclipse + 1.0, dur=1.4)          # on the plain layer: the Sun's glow stays as a corona
    d_in = (gr[-1] - gr[-2]) / np.linalg.norm(gr[-1] - gr[-2])
    seen = DashedLine(gr[-1], gr[-1] - 12.4 * d_in, color=C.light, stroke_width=C.thin, stroke_opacity=0.8)
    apparent = Dot(radius=0.09, color=C.light).move_to(gr[-1] - 12.4 * d_in)
    true_star = Dot(radius=0.09, color=C.text).move_to(gr[0])
    glow.play(FadeIn(true_star), at=T.sun - 0.9, dur=0.4)
    m.play(Create(seen), at=T.shifted - 1.2, dur=1.2)
    glow.play(FadeIn(apparent, scale=0.4), at=T.shifted, dur=0.5)

    # the Sun is far larger than its own r_s: aim at something much smaller
    t_c = T.aim_closer - 6.6
    m.play(FadeOut(year), FadeOut(seen), FadeOut(straight), FadeOut(wedge), FadeOut(half), FadeOut(half_val),
           FadeOut(times2), at=t_c, dur=0.8)
    m.remove(reading, at=t_c + 0.05)
    glow.play(FadeOut(apparent), FadeOut(true_star), at=t_c, dur=0.8)
    core = Dot(radius=0.05, color=C.horizon).move_to(sc)
    core_lab = VGroup(Eqn("r_s", colors={"r_s": C.horizon}, size=44), Label("= 3 km", color=C.horizon))
    core_lab.arrange(RIGHT, buff=0.2).move_to(sc + [3.3, -1.0, 0])
    leader = Line(sc + [0.12, -0.04, 0], core_lab.get_left() + 0.15 * LEFT, color=C.horizon, stroke_width=C.thin)
    m.play(FadeIn(core, scale=3.0), Create(leader), FadeIn(core_lab), at=T.aim_closer - 3.0, dur=0.7)
    hole = Circle(radius=0.34, stroke_color=C.horizon, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1.0)
    hole.move_to(sc)
    sun_fx.play(FadeOut(sun), at=T.aim_closer + 0.4, dur=1.2)
    m.play(FadeOut(core_lab), FadeOut(leader), ReplacementTransform(core, hole), at=T.aim_closer + 0.4, dur=1.4,
           ease="easy_ease")
    m.remove(moon, at=T.aim_closer + 0.4)
    glow.play(FadeOut(star_ray), at=T.aim_closer + 2.6, dur=1.0)
