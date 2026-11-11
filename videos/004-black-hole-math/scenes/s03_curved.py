"""s03 chapter 2: light goes straight; mass changes what straight means.
A flat grid sinks into Flamm's paraboloid (exact), two geodesics on it bend, then we look from above."""
from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import badge_newton, badge_rs, breathe, brief, glow_fx, photons, readout, starfield

RS, RG = 0.6, 6.0                      # funnel: Schwarzschild radius and grid half-size (world units)
AZ0, D, S0 = 0.52, 30.0, 0.54          # view: azimuth (rad), perspective distance, world → frame scale
SINK = key(T.mass_in + 0.9, 0.0, 1.0, dur=4.6, ease="easy_ease", lead=0)
ELEV = key(T.above - 0.3, 31.0, 90.0, dur=3.2, ease="easy_ease", lead=0)       # degrees above the sheet
Z_RIM = float(S.flamm(RG, RS))


def height(x, y, t):
    """Flamm's paraboloid hanging below the rim, scaled by the sink amount (0 = flat sheet)."""
    r = np.hypot(x, y)
    return float(SINK(t)) * (S.flamm(np.maximum(r, RS), RS) - Z_RIM)


def project(p, t):
    """World (N, 3) → frame (N, 3). Perspective camera looking at the origin from elevation ELEV(t)."""
    p = np.atleast_2d(np.asarray(p, float))
    el = np.radians(float(ELEV(t)))
    az = AZ0 * (90.0 - float(ELEV(t))) / 59.0                        # the sheet squares up as we rise above it
    c, s_ = np.cos(az), np.sin(az)
    x, y, z = c * p[:, 0] - s_ * p[:, 1], s_ * p[:, 0] + c * p[:, 1], p[:, 2]
    ys = y * np.sin(el) + z * np.cos(el)
    depth = y * np.cos(el) - z * np.sin(el)
    k = (S0 - 0.07 * (float(ELEV(t)) - 31.0) / 59.0) * D / (D + depth)   # a little smaller from above: clears the labels
    lift = 0.75 * np.cos(el) * float(SINK(t)) - 0.1                  # keep the funnel centred while it hangs down
    return np.stack([k * x, k * ys + lift, np.zeros(len(x))], 1)


def polyline(pts3, t, **kw):
    return VMobject(**kw).set_points_as_corners(project(pts3, t))


def grid(t, opacity):
    g = VGroup()
    u = np.linspace(-RG, RG, 97)
    for c in np.arange(-RG, RG + 1e-6, 1.0):
        for line in (np.stack([u, np.full_like(u, c)], 1), np.stack([np.full_like(u, c), u], 1)):
            keep = np.hypot(line[:, 0], line[:, 1]) >= RS * (1.0 if SINK(t) > 0.02 else 0.0)
            idx = np.where(keep)[0]
            for seg in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):       # the line through the throat splits
                if len(seg) > 1:
                    q = line[seg]
                    p3 = np.column_stack([q, height(q[:, 0], q[:, 1], t)])
                    g.add(polyline(p3, t, stroke_color=C.grid, stroke_width=C.thin, stroke_opacity=opacity))
    if SINK(t) > 0.02:
        a = np.linspace(0, TAU, 60)
        ring = np.column_stack([RS * np.cos(a), RS * np.sin(a), np.full(60, height(RS, 0.0, t))])
        g.add(polyline(ring, t, stroke_color=C.grid, stroke_width=C.thin + 1, stroke_opacity=opacity))
    return g


@scene(T.cut_ch2, T.cut_ch3)
def s03_curved(s):
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim()
    brief(m, badge_rs(), T.cut_ch2 + 2.6)                 # chapter 1's results leave: a clean stage
    brief(m, badge_newton(), T.cut_ch2 + 2.6)
    breathe(s, T.cut_ch2 + 3.5, T.cut_ch3)
    starfield(s)

    # ── light goes straight. Always. Gravity does not pull on it ─────────
    ray = Line([-7.4, 0.7, 0], [7.4, 0.7, 0], color=C.light, stroke_width=C.stroke)
    glow.play(Create(ray), at=T.straight - 0.9, dur=2.0, ease="easy_ease")
    runner = Dot(radius=0.1, color=C.text)
    glow.add(runner.move_to([-7.4, 0.7, 0]), at=T.always - 0.2)
    glow.drive(runner, lambda d, t: d.move_to([-7.4 + 14.8 * np.clip((t - T.always + 0.2) / 1.5, 0, 1), 0.7, 0]),
               during=(T.always - 0.2, T.always + 1.3))
    glow.remove(runner, at=T.always + 1.3)
    mass0 = Dot(radius=0.22, color=C.mass).move_to([0, -1.5, 0])
    pull = Arrow([0, 0.55, 0], [0, -1.15, 0], buff=0.0, color=C.newton, stroke_width=C.stroke,
                 max_tip_length_to_length_ratio=0.16)
    cross = Cross(pull, stroke_color=C.bad, stroke_width=C.stroke, scale_factor=0.55)
    m.play(FadeIn(mass0, scale=0.5), at=T.always + 1.0, dur=0.5)
    m.play(GrowArrow(pull), at=T.always + 1.5, dur=0.6)
    m.play(Create(cross), at=T.always + 2.4, dur=0.4)
    m.play(FadeOut(pull), FadeOut(cross), FadeOut(mass0), at=T.means - 0.4, dur=0.7)
    glow.play(FadeOut(ray), at=T.means + 1.0, dur=0.8)

    # ── a flat sheet with a grid; then a mass; the sheet sinks into the funnel ──
    t_in, t_out = T.sheet - 0.4, T.what_curve - 1.2
    g_op = fade(t_in, dur=1.4, lead=0) * (1.0 - 0.55 * key(T.above + 1.6, 0.0, 1.0, dur=2.0, lead=0)) * \
        (1.0 - key(t_out, 0.0, 1.0, dur=1.2, lead=0))
    m.redraw(lambda t: grid(t, float(g_op(t))), during=(t_in, t_out + 1.3))

    # two straight lines on the flat sheet stay side by side
    def flat_line(y0, t0):
        def f(t):
            u = np.clip((t - t0) / 1.8, 0.0, 1.0)
            u = u * u * (3 - 2 * u)
            x = np.linspace(-RG, -RG + 2 * RG * max(u, 1e-3), 30)
            return polyline(np.column_stack([x, np.full(30, y0), np.zeros(30)]), t, stroke_color=C.light,
                            stroke_width=C.stroke, stroke_opacity=float(1.0 - key(T.mass_in - 1.2, 0, 1, dur=0.8, lead=0)(t)))
        h = glow.redraw(f, during=(t0, T.mass_in - 0.3))
        glow.remove(h, at=T.mass_in - 0.3)
    flat_line(1.7, T.sheet + 3.4)
    flat_line(-1.7, T.side_by_side - 1.3)

    # the distance between them, measured live as a gauge slides along: it never changes
    t_g0, t_g1 = T.side_by_side + 0.5, T.mass_in - 1.3

    def gauge(t):
        op = float(fade(t_g0, dur=0.5, out=t_g1, lead=0)(t))
        x = 4.2 * np.sin(1.1 * (t - t_g0) - 1.2)
        a, b = project([x, 1.7, 0], t)[0], project([x, -1.7, 0], t)[0]
        bar = VGroup(Line(a, b, color=C.text, stroke_width=C.thin + 1, stroke_opacity=op),
                     Dot(a, radius=0.06, color=C.text, fill_opacity=op), Dot(b, radius=0.06, color=C.text, fill_opacity=op))
        num = VGroup(Eqn("d", size=40), Eqn("=", size=40), readout(3.40, "", decimals=2)).arrange(RIGHT, buff=0.15)
        num.set_opacity(op).move_to((a + b) / 2 + [0.95, 0.25, 0])
        return VGroup(bar, num)
    h_g = m.redraw(gauge, during=(t_g0 - 0.6, t_g1 + 0.1))
    m.remove(h_g, at=t_g1 + 0.1)

    star = Dot(radius=0.17, color=C.mass)
    m.add(star, at=T.mass_in - 0.1)
    m.drive(star, lambda d, t: d.move_to(project([0, 0, height(RS, 0, t)], t)[0]).set_opacity(
        float(key(T.mass_in - 0.1, 0, 1, dur=0.5, lead=0)(t) * (1.0 - key(T.above + 3.6, 0.0, 1.0, dur=0.8, lead=0)(t)))),
        during=(T.mass_in - 0.1, T.picture2d + 0.6))

    # "near the mass, distances stretch": a ruler slides inward; one step in r costs more and more real length
    t_r0, t_r1 = T.stretch - 1.4, T.computed - 0.5
    r_probe = key(t_r0 + 0.4, 5.4, 0.72, dur=3.6, ease="easy_ease", lead=0)
    ang = np.radians(205.0)
    law = Eqn(r"\frac{dl}{dr} = \frac{1}{\sqrt{1 - r_s/r}}", colors={"r_s": C.horizon}, size=44)
    law.move_to([-4.6, -2.95, 0])
    m.play(FadeIn(law, shift=0.15 * UP), at=t_r0, dur=0.6)
    m.play(FadeOut(law), at=t_r1, dur=0.5)

    def ruler(t):
        op = float(fade(t_r0 + 0.2, dur=0.5, out=t_r1, lead=0)(t))
        r = float(r_probe(t))
        rr = np.linspace(r, r + 0.9, 10)
        seg = np.column_stack([rr * np.cos(ang), rr * np.sin(ang), [height(q * np.cos(ang), q * np.sin(ang), t) for q in rr]])
        tick = VGroup(polyline(seg, t, stroke_color=C.text, stroke_width=C.stroke + 2, stroke_opacity=op),
                      Dot(project(seg[0], t)[0], radius=0.07, color=C.text, fill_opacity=op),
                      Dot(project(seg[-1], t)[0], radius=0.07, color=C.text, fill_opacity=op))
        val = readout(1.0 / np.sqrt(1.0 - RS / (r + 0.45)), "", decimals=2, size=1.0)
        val.set_opacity(op).next_to(law, RIGHT, buff=0.3)
        eq_sign = Eqn("=", size=44).set_opacity(op).next_to(law, RIGHT, buff=0.3)
        val.next_to(eq_sign, RIGHT, buff=0.2)
        return VGroup(tick, eq_sign, val)
    h_r = m.redraw(ruler, during=(t_r0, t_r1 + 0.6))
    m.remove(h_r, at=t_r1 + 0.6)

    shape = Eqn(r"z = 2\sqrt{r_s\,(r - r_s)}", colors={"z": C.text}, size=50).move_to([-4.3, -3.0, 0])
    m.play(FadeIn(shape, shift=0.2 * UP), at=T.computed, dur=0.8)
    m.play(FadeOut(shape), at=T.two_rays - 0.9, dur=0.7)

    # ── two rays, each as straight as it can be on this surface ──────────
    for b0 in (2.3, -2.3):
        g3 = S.geodesic_on_flamm(b0, RS, r_max=7.4)
        g3 = g3[(np.abs(g3[:, 0]) <= RG) & (np.abs(g3[:, 1]) <= RG)]
        r3 = np.hypot(g3[:, 0], g3[:, 1])

        def geo(t, g3=g3, r3=r3):
            u = np.clip((t - T.two_rays) / (T.bend + 0.6 - T.two_rays), 0.0, 1.0)
            n = max(int(u * len(g3)), 2)
            p3 = np.column_stack([g3[:n, :2], float(SINK(t)) * (S.flamm(r3[:n], RS) - Z_RIM)])
            return polyline(p3, t, stroke_color=C.light, stroke_width=C.stroke,
                            stroke_opacity=float(1.0 - key(T.picture2d - 1.3, 0, 1, dur=0.9, lead=0)(t)))
        h = glow.redraw(geo, during=(T.two_rays, T.picture2d - 0.3))
        glow.remove(h, at=T.picture2d - 0.3)

        # the heading of the path, measured as it goes: it never steers, yet the number climbs
        head = np.unwrap(np.arctan2(np.gradient(g3[:, 1]), np.gradient(g3[:, 0])))
        turn = np.degrees(np.abs(head - head[0]))

        def bend(t, g3=g3, r3=r3, turn=turn, b0=b0):
            u = np.clip((t - T.two_rays) / (T.bend + 0.6 - T.two_rays), 0.0, 1.0)
            n = min(max(int(u * len(g3)), 2), len(g3)) - 1
            op = float(fade(T.two_rays + 0.3, dur=0.5, out=T.picture2d - 1.3, lead=0)(t))
            p = project([g3[n, 0], g3[n, 1], float(SINK(t)) * (S.flamm(r3[n], RS) - Z_RIM)], t)[0]
            dot = Dot(p, radius=0.07, color=C.text, fill_opacity=op)
            if b0 < 0:                                       # one readout is enough: the two paths mirror each other
                return VGroup(dot)
            tag = DecimalNumber(float(turn[n]), num_decimal_places=1, unit=r"^{\circ}", font_size=C.tex_size * 0.8,
                                color=C.text)
            tag.set_opacity(op).move_to(p + [0.0, 0.42, 0])
            return VGroup(dot, tag)
        hb = m.redraw(bend, during=(T.two_rays, T.picture2d - 0.3))
        m.remove(hb, at=T.picture2d - 0.3)

    # ── from directly above: the 2D picture used from here on ────────────
    mass = Dot(radius=0.2, color=C.mass).move_to([0, -0.1, 0])
    m.play(FadeIn(mass), at=T.above + 3.6, dur=0.8)
    pts, _ = S.ray(1.6, rs=0.22, r_max=9.0)                          # the true light path (not the sheet's geodesic)
    pts = pts[np.abs(pts[:, 0]) < 7.4]
    light = VMobject(stroke_color=C.light, stroke_width=C.stroke)
    light.set_points_as_corners([[x, y - 0.1, 0.0] for x, y in pts])
    glow.play(Create(light), at=T.picture2d + 0.3, dur=2.6, ease="easy_ease")
    photons(glow, light.get_all_points()[::3], T.picture2d + 2.9, T.cut_ch3)
