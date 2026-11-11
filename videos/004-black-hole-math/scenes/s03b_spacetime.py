"""s03b deeper look 1 (undergraduate): spacetime. A map with r across and t up; colour = clock rate;
light cones tip toward the mass (ingoing Eddington–Finkelstein), and the metric, set to zero for light,
leads to the light-path equation. Casual viewers are told they can coast for a minute."""
from aion import *
from aion.comp.comp import hex_to_linear
from aion.maths import schwarzschild as S

from beats import T
from shots import breathe, funnel_icon, glow_fx, starfield

X0, KR = -5.9, 1.95                                   # screen x of r = 0, and frame units per r_s (c = 1: same for t)
LO, HI = np.array([X0, -3.25]), np.array([6.55, 3.25])
A, B = T.cut_deep1, T.cut_ch3
FLOW = Clock(rate=1.0, start=A)
MAP_ON = fade(T.dp_colour - 0.3, dur=1.6, lead=0) * (1.0 - 0.62 * key(T.dp_metric - 0.9, 0.0, 1.0, dur=1.0, lead=0)) * \
    (1.0 - key(T.dp_set + 0.4, 0.0, 1.0, dur=1.2, lead=0))
INK = 1.0 - key(T.dp_set + 0.4, 0.0, 1.0, dur=1.0, lead=0)        # everything drawn on the map


def X(r):
    return X0 + KR * r


def v_out(r):
    """Outgoing light, dr/dt, in ingoing Eddington–Finkelstein coordinates (r in r_s, c = 1)."""
    return (r - 1.0) / (r + 1.0)


def cone(r, y, h=0.82, op=1.0, fill=0.12):
    """The future light cone of the event (r, y): inward edge at 45°, outward edge slowed by the mass."""
    p = np.array([X(r), y, 0.0])
    a, b = p + h * np.array([-1.0, 1.0, 0.0]), p + h * np.array([v_out(r), 1.0, 0.0])
    return VGroup(Polygon(p, a, b, stroke_width=0, fill_color=C.light, fill_opacity=fill * op),
                  Line(p, a, color=C.light, stroke_width=C.thin + 1, stroke_opacity=op),
                  Line(p, b, color=C.light, stroke_width=C.thin + 1, stroke_opacity=op),
                  Dot(p, radius=0.045, color=C.text, fill_opacity=op))


@scene(A, B)
def s03b_spacetime(s):
    starfield(s, opacity=1.0 - 0.7 * fade(T.dp_colour, dur=1.5, lead=0))
    breathe(s, A + 2.0, B, zoom=1.03)
    s.shader("spacetime.frag", z=-20, u_amt=MAP_ON, u_x0=X0, u_k=KR, u_flow=FLOW, u_lo=LO, u_hi=HI,
             u_fast=hex_to_linear(C.time_fast), u_mid=hex_to_linear(C.time_mid), u_slow=hex_to_linear(C.time_slow))
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim(z=3)

    # the picture chapter 2 ended on leaves; a one-minute ring shows how long the detour lasts
    pts, _ = S.ray(1.6, rs=0.22, r_max=9.0)
    pts = pts[np.abs(pts[:, 0]) < 7.4]
    old_ray = VMobject(stroke_color=C.light, stroke_width=C.stroke).set_points_as_corners([[x, y - 0.1, 0] for x, y in pts])
    old_mass = Dot(radius=0.2, color=C.mass).move_to([0, -0.1, 0])
    glow.add(old_ray)
    m.add(old_mass)
    glow.play(FadeOut(old_ray), at=A + 0.5, dur=0.9)
    m.play(FadeOut(old_mass), at=A + 0.5, dur=0.9)

    def timer(t):
        u = float(np.clip((t - T.dp_deeper) / (B - 1.5 - T.dp_deeper), 0.0, 1.0))
        op = float(fade(T.dp_deeper, dur=0.6, out=B - 1.2, lead=0)(t))
        c = np.array([6.25, 3.3, 0.0])
        return VGroup(Circle(radius=0.26, color=C.faint, stroke_width=C.thin + 1, stroke_opacity=op).move_to(c),
                      Arc(radius=0.26, start_angle=PI / 2, angle=-TAU * (1 - u) - 1e-3, arc_center=c, color=C.text,
                          stroke_width=C.thin + 1, stroke_opacity=op))
    m.redraw(timer, during=(T.dp_deeper - 0.2, B))

    # curved space … and curved time: the funnel meets a clock
    icon = funnel_icon().scale(2.2).move_to([-3.3, 0.1, 0])
    m.play(FadeIn(icon, shift=0.2 * UP), at=T.dp_space - 0.4, dur=0.8)

    def clock(c, rad, rate, t, op=1.0, color=None):
        col = color or C.text
        a = PI / 2 - TAU * 0.45 * rate * (t - A)
        g = VGroup(Circle(radius=rad, color=col, stroke_width=C.thin + 1, stroke_opacity=op).move_to(c),
                   Line(c, c + 0.78 * rad * np.array([np.cos(a), np.sin(a), 0]), color=col, stroke_width=C.thin + 1,
                        stroke_opacity=op),
                   Dot(c, radius=0.04, color=col, fill_opacity=op))
        for k in range(12):
            d = np.array([np.cos(k * TAU / 12), np.sin(k * TAU / 12), 0])
            g.add(Line(c + 0.86 * rad * d, c + rad * d, color=col, stroke_width=C.thin, stroke_opacity=0.7 * op))
        return g
    big = np.array([3.2, 0.1, 0.0])
    m.redraw(lambda t: clock(big, 1.15, 1.0, t, float(fade(T.dp_time - 0.3, dur=0.7, out=T.dp_map - 0.3, lead=0)(t))),
             during=(T.dp_time - 0.4, T.dp_map + 0.4))
    weave = Eqn("+", size=80).move_to([0, 0.1, 0])
    m.play(FadeIn(weave, scale=0.5), at=T.dp_time + 2.0, dur=0.5)
    m.play(FadeOut(icon), FadeOut(weave), at=T.dp_map - 0.4, dur=0.6)

    # ── the map: distance across, time upward; a point is an event ──────
    ax_r = Arrow([X0, -3.25, 0], [6.6, -3.25, 0], buff=0, color=C.muted, stroke_width=C.thin + 1, tip_length=0.2)
    ax_t = Arrow([X0, -3.25, 0], [X0, 3.45, 0], buff=0, color=C.muted, stroke_width=C.thin + 1, tip_length=0.2)
    lab_r = Eqn("r", size=44).move_to([6.35, -2.85, 0])
    lab_t = Eqn("t", size=44).move_to([X0 + 0.35, 3.25, 0])
    mass_line = Line([X0, -3.25, 0], [X0, 3.3, 0], color=C.mass, stroke_width=C.stroke + 2)
    m.play(Create(ax_r), FadeIn(lab_r), at=T.dp_across - 0.5, dur=0.8)
    m.play(Create(ax_t), FadeIn(lab_t), at=T.dp_upward - 0.2, dur=0.8)
    glow.play(Create(mass_line), at=T.dp_across + 0.2, dur=0.8)
    ev = np.array([X(4.2), -1.35, 0.0])
    cross = VGroup(DashedLine([ev[0], -3.25, 0], ev, color=C.muted, stroke_width=C.thin),
                   DashedLine([X0, ev[1], 0], ev, color=C.muted, stroke_width=C.thin))
    ev_dot = Dot(ev, radius=0.08, color=C.text)
    m.play(FadeIn(ev_dot, scale=3.0), Create(cross), at=T.dp_event - 0.3, dur=0.7)
    m.play(FadeOut(cross), at=T.dp_cone - 0.7, dur=0.5)

    # a flash of light traces a cone
    def first_cone(t):
        u = float(np.clip((t - T.dp_cone + 0.3) / 1.4, 0.0, 1.0))
        u = u * u * (3 - 2 * u)
        big_h = 1.5 - 0.68 * float(key(T.dp_upright - 0.5, 0.0, 1.0, dur=0.9, lead=0)(t))      # then it joins the field
        return cone(4.2, -1.35, h=max(big_h * u, 1e-3), op=float(INK(t)))
    glow.redraw(first_cone, during=(T.dp_cone - 0.3, T.dp_set + 1.6))
    m.play(FadeOut(ev_dot), at=T.dp_upright, dur=0.5)

    # cones everywhere: upright far away, tipping toward the mass, falling in past the horizon
    rows = [-2.9, -1.35, 0.2, 1.75]
    cols = [5.3, 4.2, 3.1, 2.25, 1.6, 1.0, 0.5]
    appear = {5.3: T.dp_upright - 0.3, 4.2: T.dp_upright, 3.1: T.dp_upright + 0.3, 2.25: T.dp_tip - 0.3,
              1.6: T.dp_tip + 0.2, 1.0: T.dp_at_rs - 0.2, 0.5: T.dp_inward - 0.4}

    def field(t):
        g = VGroup()
        for r in cols:
            for i, y in enumerate(rows):
                if r == 4.2 and i == 1:
                    continue
                u = float(np.clip((t - appear[r] - 0.12 * i) / 0.6, 0.0, 1.0))
                if u > 0:
                    g.add(cone(r, y, h=0.82 * (0.4 + 0.6 * u), op=u * float(INK(t))))
        return g
    glow.redraw(field, during=(T.dp_upright - 0.4, T.dp_set + 1.6))

    # clocks at three distances: the colour is how fast they run
    spots = [(5.0, C.time_fast), (2.1, C.time_mid), (1.18, C.time_slow)]
    m.redraw(lambda t: VGroup(*[clock(np.array([X(r), 2.95, 0.0]), 0.3, float(np.sqrt(1 - 1 / r)), t,
                                      float(fade(T.dp_colour + 0.6 + 0.5 * i, dur=0.6, lead=0)(t) * INK(t)), col)
                                for i, (r, col) in enumerate(spots)]), during=(T.dp_colour, T.dp_set + 1.6))
    rate_far = Eqn(r"\sqrt{1 - r_s/r}", colors={"r_s": C.horizon}, size=40).move_to([X(3.5), 2.95, 0])
    m.play(FadeIn(rate_far, shift=0.15 * UP), at=T.dp_slow - 0.2, dur=0.6)
    m.play(FadeOut(rate_far), at=T.dp_at_rs - 0.5, dur=0.5)

    # the Schwarzschild radius: the outward edge stands straight up; light aimed outward only hovers
    hz = DashedLine([X(1.0), -3.25, 0], [X(1.0), 3.3, 0], color=C.horizon, stroke_width=C.thin + 1)
    hz_lab = Eqn("r_s", colors={"r_s": C.horizon}, size=44).move_to([X(1.0) + 0.38, -2.9, 0])
    m.play(Create(hz), FadeIn(hz_lab), at=T.dp_at_rs, dur=0.9)
    hover = Dot(radius=0.07, color=C.text)
    glow.add(hover.move_to([X(1.0), -2.9, 0]), at=T.dp_hovers - 0.4)
    glow.drive(hover, lambda d, t: d.move_to([X(1.0), -2.9 + 1.5 * (t - T.dp_hovers + 0.4), 0]).set_opacity(float(INK(t))),
               during=(T.dp_hovers - 0.4, T.dp_inward + 1.6))
    glow.remove(hover, at=T.dp_inward + 1.6)
    faller = Dot(radius=0.07, color=C.text)
    glow.add(faller.move_to([X(0.8), -1.35, 0]), at=T.dp_inward)
    glow.drive(faller, lambda d, t: d.move_to([X(0.8) - 0.55 * (t - T.dp_inward), -1.35 + 1.1 * (t - T.dp_inward), 0])
               .set_opacity(float(INK(t) * (t - T.dp_inward < 2.4))), during=(T.dp_inward, T.dp_inward + 2.5))
    glow.remove(faller, at=T.dp_inward + 2.5)

    # ── the metric: the separation between two nearby events; zero for light ──
    back = s.manim(z=2.6)
    plate = RoundedRectangle(width=11.8, height=3.5, corner_radius=0.25, stroke_width=0, fill_color=C.bg, fill_opacity=0.93)
    plate.move_to([0.4, -0.95, 0])
    back.play(FadeIn(plate), at=T.dp_metric - 0.9, dur=0.8)
    back.play(FadeOut(plate), at=T.dp_set + 0.4, dur=0.8)
    G1, G2 = r"\left(1 - \frac{r_s}{r}\right)", r"\frac{dr^2}{1 - r_s/r}"
    metric = Eqn(r"ds^2 = -" + G1 + r"c^2 dt^2 + " + G2 + r" + r^2 d\varphi^2",
                 colors={"ds^2": C.light, G1: C.time_fast, G2: C.time_mid}, size=54).move_to([0.4, -0.2, 0])
    m.play(Write(metric), at=T.dp_metric - 0.5, dur=1.8)
    m.play(Indicate(metric.part("ds^2"), color=C.light, scale_factor=1.3), at=T.dp_sep, dur=1.0)
    zero = Eqn(r"ds^2 = 0", colors={"ds^2": C.light}, size=64).move_to([0.4, -1.95, 0])
    m.play(FadeIn(zero, shift=0.2 * UP), at=T.dp_zero - 0.5, dur=0.7)

    # set it to zero, follow the light round the mass … one short equation
    FR = r"\frac{3GM}{c^2}"
    eq = Eqn(r"u'' + u = " + FR + r"\,u^2", colors={"u": C.light, FR: C.mass}, size=84).move_to([0, 0.2, 0])
    m.play(FadeOut(ax_r), FadeOut(ax_t), FadeOut(lab_r), FadeOut(lab_t), FadeOut(hz), FadeOut(hz_lab), at=T.dp_set + 0.4,
           dur=0.9)
    glow.play(FadeOut(mass_line), at=T.dp_set + 0.4, dur=0.9)
    m.play(metric.animate.scale(0.6).move_to([0, 2.6, 0]), zero.animate.scale(0.7).move_to([0, 1.55, 0]),
           at=T.dp_set + 0.3, dur=1.1, ease="easy_ease")
    arrow = Arrow([0, 1.2, 0], [0, 0.95, 0], buff=0, color=C.muted, stroke_width=C.thin + 1, tip_length=0.18)
    m.play(GrowArrow(arrow), at=T.dp_calc - 0.3, dur=0.6)
    halo = s.manim(fx=[glow_fx(C.mass, 1.4, 1.4)], z=1, opacity=pulse(T.dp_eq + 0.6, 1.0, dur=2.4))
    m.play(Write(eq), at=T.dp_eq - 0.8, dur=1.5)
    halo.add(eq.copy(), at=T.dp_eq - 0.6)

    # back to the picture chapter 3 starts from
    m.play(FadeOut(metric), FadeOut(zero), FadeOut(arrow), FadeOut(eq), at=B - 1.7, dur=0.7)
    new_ray = old_ray.copy()
    new_mass = old_mass.copy()
    glow.play(Create(new_ray), at=B - 1.2, dur=1.1, lead=0)
    m.play(FadeIn(new_mass), at=B - 1.2, dur=0.8, lead=0)
