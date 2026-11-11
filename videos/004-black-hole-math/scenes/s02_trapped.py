"""s02 chapter 1: can light be trapped? Escape velocity → set it to c → the Schwarzschild radius.
Plants the Newtonian light-bending answer that is wrong by exactly two (paid off in chapter 3)."""
from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import breathe, glow_fx, photons

P0, R0 = np.array([0.0, -9.7, 0.0]), 7.0          # the planet as a big limb at the bottom of the frame
P1, R1 = np.array([-3.7, -0.5, 0.0]), 1.6         # the planet as a whole ball, once the formula appears


def throw(f, n=400):
    """Radial throw at f × escape speed (units: R = 1, v_esc = 1). Returns r(τ), τ ∈ [0, 1]."""
    gm, r, v, dt, out = 0.5, 1.0, f, 2e-3, [1.0]
    while len(out) < 200000:
        v += -gm / r**2 * dt
        r += v * dt
        if r <= 1.0 or r > 2.4:
            break
        out.append(r)
    out = np.array(out + [max(r, 1.0)])
    return np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(out)), out)


def frac_colors(eq, tex, picks):
    """Colour single glyphs inside an isolated fraction (isolating them in TeX would break \\frac)."""
    part = eq.part(tex)
    for i, col in picks.items():
        part[i].set_color(col)
    return eq


@scene(T.cut_ch1, T.cut_ch2)
def s02_trapped(s):
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim()

    # the single ray from the intro leaves
    ray0 = Line([-7.4, -3.2, 0], [7.4, -3.2, 0], color=C.light, stroke_width=C.stroke)
    glow.add(ray0)
    glow.play(FadeOut(ray0), at=T.cut_ch1 + 0.6, dur=1.0)

    breathe(s, T.trapped, T.cut_ch2)

    # ── A: throw a ball ──────────────────────────────────────────────────
    planet = Circle(radius=R0, stroke_color=C.grid, stroke_width=C.stroke, fill_color=C.faint, fill_opacity=0.35)
    planet.move_to(P0)
    m.play(FadeIn(planet, shift=0.4 * UP), at=T.trapped + 0.6, dur=1.0)

    throws = [(-13.0, 0.47, T.ball, 2.1), (0.0, 0.63, T.faster, 3.2), (13.0, 1.0, T.never - 1.3, 2.6)]
    last_line = None
    for ang, f, t0, dur in throws:
        prof = throw(f)
        d = np.array([np.sin(np.radians(ang)), np.cos(np.radians(ang)), 0.0])
        pos = lambda t, t0=t0, dur=dur, prof=prof, d=d: P0 + R0 * d * float(      # noqa: E731
            np.interp(np.clip((t - t0) / dur, 0, 1), np.linspace(0, 1, len(prof)), prof))
        ball = Dot(radius=0.11, color=C.text).move_to(pos(t0))
        m.add(ball, at=t0)
        m.drive(ball, lambda b, t, pos=pos: b.move_to(pos(t)), during=(t0, t0 + dur))
        trail = m.redraw(lambda t, pos=pos, t0=t0: Line(pos(t0), pos(t) + 1e-3 * UP, color=C.newton,
                                                         stroke_width=C.thin), during=(t0, t0 + dur))
        m.remove(trail, at=t0 + dur)
        if f < 1.0:
            m.remove(ball, at=t0 + dur)
        else:
            last_line = Line(pos(t0), pos(t0 + dur), color=C.newton, stroke_width=C.thin)
            m.add(last_line, at=t0 + dur)
            m.remove(ball, at=t0 + dur)
    name = Label("escape velocity", color=C.text).move_to([4.4, 1.3, 0])
    val = Label("11.2 km/s", color=C.muted).next_to(name, DOWN, buff=0.25)
    m.play(FadeIn(name, shift=0.2 * UP), at=T.escape_v, dur=0.7)
    m.play(FadeIn(val, shift=0.2 * UP), at=T.eleven, dur=0.7)
    m.play(FadeOut(name), FadeOut(val), FadeOut(last_line), at=T.formula - 0.9, dur=0.7)

    # ── B: the formula, then squeeze the mass ────────────────────────────
    m.play(planet.animate.scale(R1 / R0).move_to(P1), at=T.formula - 0.3, dur=1.5, ease="easy_ease")
    eq_v = Eqn(r"v_{\text{esc}} = \sqrt{\frac{2GM}{r}}", colors={r"\sqrt{\frac{2GM}{r}}": C.text}, size=64)
    eq_v.move_to([3.2, 0.5, 0])
    root = eq_v.part(r"\sqrt{\frac{2GM}{r}}")
    m.play(Write(eq_v), at=T.formula + 0.5, dur=1.4)

    t_sq0, t_sq1 = T.squeeze, T.reaches_c + 0.6                    # the squeeze, eased
    u_sq = key(t_sq0, 0.0, 1.0, dur=t_sq1 - t_sq0, ease="easy_ease", lead=0)
    r_earth, rs_earth = 6.371e6, S.schwarzschild_radius(S.M_EARTH)
    rad = lambda t: R1 * (0.085 / R1) ** float(u_sq(t))            # noqa: E731  drawn radius
    phys = lambda t: r_earth * (rs_earth / r_earth) ** float(u_sq(t))   # noqa: E731  metres
    m.drive(planet, lambda p, t: p.scale_to_fit_width(2 * rad(t)).move_to(P1), during=(t_sq0, t_sq1))

    arm_dir = np.array([np.cos(0.6), np.sin(0.6), 0.0])
    arm = m.redraw(lambda t: Line(P1, P1 + max(rad(t), 0.02) * arm_dir, color=C.text, stroke_width=C.thin),
                   during=(T.formula + 3.0, t_sq1))
    r_lab = Eqn("r", size=44)
    m.add(r_lab.move_to(P1 + (R1 + 0.35) * arm_dir), at=T.formula + 4.6)
    m.drive(r_lab, lambda o, t: o.move_to(P1 + (rad(t) + 0.35) * arm_dir), during=(t_sq0, t_sq1))
    M_lab = Eqn("M", colors={"M": C.mass}, size=44).move_to(P1 + [-0.55, -0.35, 0])
    m.play(FadeIn(M_lab), at=T.formula + 2.6, dur=0.6)
    m.play(Indicate(M_lab, color=C.mass, scale_factor=1.35), at=T.more_mass, dur=0.9)
    m.play(Indicate(r_lab, color=C.text, scale_factor=1.35), at=T.more_mass + 1.6, dur=0.9)
    m.play(Indicate(root, color=C.text, scale_factor=1.08), at=T.more_mass + 2.6, dur=0.9)
    m.play(FadeOut(M_lab), at=T.squeeze - 0.2, dur=0.5)

    def speed(t):
        v = S.escape_velocity(S.M_EARTH, phys(t)) / 1000.0
        num = DecimalNumber(min(v, S.C_LIGHT / 1000.0), num_decimal_places=0, group_with_commas=True,
                            font_size=C.tex_size, color=C.text)
        unit = Label("km/s", color=C.muted).next_to(num, RIGHT, buff=0.2).align_to(num, DOWN)
        return VGroup(num, unit).move_to([3.2, -1.25, 0])
    readout = m.redraw(speed, during=(T.squeeze - 0.8, t_sq1 + 0.45))
    m.remove(readout, at=t_sq1 + 0.45)                              # 299,792 km/s … which is c
    eq_c = Eqn(r"v_{\text{esc}} = c", colors={"c": C.light}, size=56).move_to([3.2, -1.25, 0])
    m.play(FadeIn(eq_c, shift=0.15 * UP), at=t_sq1 + 0.45, dur=0.45, lead=0)

    # ── C: set v = c, solve for r ────────────────────────────────────────
    eq_set = Eqn(r"\sqrt{\frac{2GM}{r}} = c", colors={r"\sqrt{\frac{2GM}{r}}": C.text, "c": C.light}, size=64)
    eq_set.move_to([3.2, 0.5, 0])
    m.play(TransformMatchingShapes(VGroup(eq_v, eq_c), eq_set), at=T.set_equal + 0.3, dur=1.3)
    m.remove(arm, at=T.set_equal)
    m.play(FadeOut(r_lab), FadeOut(planet), at=T.rs - 1.2, dur=0.7)

    F = r"\frac{2GM}{c^2}"
    eq_rs = frac_colors(Eqn(r"r_s = " + F, colors={"r_s": C.horizon, F: C.text}, size=84), F,
                        {2: C.mass, 4: C.light})
    eq_rs.move_to([0, 0.3, 0])
    m.play(TransformMatchingShapes(eq_set, eq_rs), at=T.rs, dur=1.4, ease="easy_ease")
    m.play(Indicate(eq_rs.part("r_s"), color=C.horizon, scale_factor=1.5), at=T.schwarzschild, dur=1.0)

    # ── D: Earth → 9 mm, Sun → 3 km ──────────────────────────────────────
    m.play(eq_rs.animate.scale(0.62).move_to([0, 2.75, 0]), at=T.nine_mm - 2.2, dur=1.0)

    def body(x, name, size_txt, t_in, t_num, t_squash, small):
        c = np.array([x, -0.55, 0.0])
        ball = Circle(radius=1.25, stroke_color=C.text, stroke_width=C.thin + 1, fill_color=C.faint,
                      fill_opacity=0.35).move_to(c)
        lab = Label(name, color=C.muted).move_to(c + [0, -1.85, 0])
        hole = Circle(radius=small, stroke_color=C.horizon, stroke_width=C.thin + 1, fill_color=C.bg,
                      fill_opacity=1.0).move_to(c)
        size = Label(size_txt, color=C.horizon).move_to(c + [0, 1.75, 0])
        m.play(FadeIn(ball, scale=0.9), FadeIn(lab), at=t_in, dur=0.7)
        m.play(FadeIn(size, shift=0.15 * UP), at=t_num, dur=0.6)
        m.play(ReplacementTransform(ball, hole), at=t_squash, dur=1.3, ease="easy_ease")
        return VGroup(lab, hole, size)

    earth = body(-3.4, "Earth", "9 mm", T.nine_mm - 1.7, T.nine_mm, T.marble - 0.2, 0.09)
    sun = body(3.4, "Sun", "3 km", T.three_km - 1.1, T.three_km, T.three_km + 0.5, 0.17)
    m.play(FadeOut(earth), FadeOut(sun), at=T.three_km + 1.9, dur=0.6)

    # ── E: inside its own r_s → black hole, the edge of no return ────────
    ctr = np.array([0.0, -0.75, 0.0])
    rim = DashedVMobject(Circle(radius=1.15, color=C.horizon, stroke_width=C.thin + 1), num_dashes=40).move_to(ctr)
    rim_lab = Eqn("r_s", colors={"r_s": C.horizon}, size=44).move_to(ctr + [1.15 * 0.78 + 0.45, 1.15 * 0.78 + 0.2, 0])
    star = Circle(radius=2.3, stroke_color=C.text, stroke_width=C.thin + 1, fill_color=C.faint, fill_opacity=0.35)
    star.move_to(ctr)
    m.play(FadeIn(star), FadeIn(rim), FadeIn(rim_lab), at=T.three_km + 2.6, dur=0.7)
    m.play(star.animate.scale(0.8 / 2.3), at=T.three_km + 3.3, dur=2.6, ease="easy_ease")
    hole = Circle(radius=1.15, stroke_color=C.horizon, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1.0)
    hole.move_to(ctr)
    m.play(FadeOut(star), FadeOut(rim), FadeIn(hole), at=T.edge - 2.3, dur=0.8)

    # light started inside heads outward and comes back: no way out
    photon = Dot(radius=0.07, color=C.light).move_to(ctr)
    t_p0, t_p1 = T.edge - 0.9, T.problem - 0.5

    def bounce(d, t):
        u = np.clip((t - t_p0) / (t_p1 - t_p0), 0, 1)
        k = min(int(u * 3), 2)
        a = [0.5, 2.3, 4.1][k]
        rho = 1.02 * np.sin(np.pi * (u * 3 - k)) ** 0.8
        d.move_to(ctr + rho * np.array([np.cos(a), np.sin(a), 0.0]))
    glow.add(photon, at=t_p0)
    glow.drive(photon, bounce, during=(t_p0, t_p1))
    glow.play(FadeOut(photon), at=t_p1, dur=0.3)
    m.play(FadeOut(hole), FadeOut(rim_lab), at=T.problem - 0.3, dur=0.7)

    # ── F: the problem: light is not a thrown ball ───────────────────────
    badge = eq_rs.animate.scale(0.5).to_corner(UR, buff=C.margin + 0.1)   # .animate targets are relative to the original size
    m.play(badge, at=T.problem - 0.3, dur=1.0)

    a0, a1 = np.array([-5.2, -1.6, 0.0]), np.array([-1.6, -1.6, 0.0])
    arc_pt = lambda u: a0 + (a1 - a0) * u + 2.6 * 4 * u * (1 - u) * UP          # noqa: E731
    t_b0, t_b1 = T.problem + 0.4, T.no_mass - 0.3
    ub = lambda t: float(np.clip((t - t_b0) / (t_b1 - t_b0), 0, 1))              # noqa: E731
    ball = Dot(radius=0.11, color=C.text).move_to(a0)
    m.add(ball, at=t_b0)
    m.drive(ball, lambda d, t: d.move_to(arc_pt(ub(t))), during=(t_b0, t_b1))
    arc_trail = m.redraw(lambda t: VMobject(stroke_color=C.newton, stroke_width=C.thin).set_points_as_corners(
        [arc_pt(u) for u in np.linspace(0, max(ub(t), 1e-3), 40)]), during=(t_b0, t_b1))
    m_ball = Eqn("m > 0", size=44).move_to([-3.4, -2.3, 0])
    m.play(FadeIn(m_ball), at=t_b0 + 0.6, dur=0.5)
    phot = Dot(radius=0.09, color=C.light).move_to([2.6, 0.2, 0])
    glow.play(FadeIn(phot, scale=0.5), at=T.no_mass, dur=0.5)
    m_light = Eqn("m = 0", size=44).move_to([2.6, -0.6, 0])
    m.play(FadeIn(m_light, shift=0.15 * UP), at=T.no_mass + 0.35, dur=0.5)
    m.remove(arc_trail, at=T.should_bend - 3.7)
    m.play(FadeOut(ball), FadeOut(m_ball), FadeOut(m_light), at=T.should_bend - 4.2, dur=0.6)
    glow.play(FadeOut(phot), at=T.should_bend - 4.2, dur=0.6)

    # the thrown-ball answer for a passing ray: half of the true bend (computed, not sketched)
    rs_d, b_d, c2 = 0.7, 1.9, np.array([-0.4, -1.5, 0.0])
    pts, _ = S.ray(b_d, rs=0.5 * rs_d, r_max=8.5)                   # half the coupling = Newtonian deflection
    pts = pts[(np.abs(pts[:, 0] + c2[0]) < 7.3) & (pts[:, 1] + c2[1] < 4.2)]
    newton = VMobject(stroke_color=C.newton, stroke_width=C.stroke)
    newton.set_points_as_corners([[x + c2[0], y + c2[1], 0.0] for x, y in pts])
    mass = Dot(radius=0.2, color=C.mass).move_to(c2)
    straight = DashedLine([pts[0, 0] + c2[0], b_d + c2[1], 0], [6.9, b_d + c2[1], 0], color=C.muted,
                          stroke_width=C.thin, stroke_opacity=0.7)
    m.play(FadeIn(mass, scale=0.5), at=T.should_bend - 3.4, dur=0.6)
    m.play(Create(straight), at=T.should_bend - 2.6, dur=1.0)
    m.play(Create(newton), at=T.should_bend - 1.2, dur=2.0, ease="easy_ease")
    photons(glow, [p + c2 for p in np.column_stack([pts, np.zeros(len(pts))])], T.should_bend + 0.9, T.remember + 2.3)
    tag = Eqn(r"\times\,2\ ?", size=64).move_to([4.6, -0.2, 0])
    m.play(FadeIn(tag, scale=1.3), at=T.factor_two + 0.7, dur=0.6, ease="out_back")
    m.play(Indicate(tag, color=C.text, scale_factor=1.25), at=T.remember, dur=0.9)
    # the deflection angle between the straight path and the thrown-ball path
    d_out = pts[-1] - pts[-2]
    bend = float(np.arctan2(d_out[1], d_out[0]))
    wedge = Arc(radius=2.3, start_angle=0.0, angle=bend, arc_center=[c2[0], b_d + c2[1], 0], color=C.newton,
                stroke_width=C.thin + 1)
    m.play(Create(wedge), at=T.should_bend + 1.3, dur=0.8)
    # park the picture in the corner: it comes back in chapter 3
    icon = VGroup(mass, straight, newton, wedge)
    m.play(icon.animate.scale(0.34).to_corner(DR, buff=C.margin + 0.15),
           tag.animate.scale(0.6).move_to([5.75, -1.75, 0]), at=T.remember + 2.4, dur=1.2, ease="easy_ease")
