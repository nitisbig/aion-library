"""s05 chapter 4: three fates of a light ray. Slide the aim inward: bend → U-turn → loop → orbit → capture.
The circular orbit falls out of the equation in one line (r = 1.5 r_s); the dividing aim is 2.6 r_s."""
from functools import lru_cache

from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import badge_eq, breathe, glow_fx

HC, K = np.array([0.3, -0.3, 0.0]), 0.55                  # hole centre on screen; one r_s in frame units
BC = S.critical_b(1.0)                                    # 2.598 r_s
# aim distances (in r_s) solved by bisection on the exact deflection: 90°, 180°, 360°
B90, B180, B360 = 3.0837833825, 2.6784793154, 2.6013402014
B_T = keys((T.cut_ch4, 4.6), (T.closer - 0.2, 4.6), (T.ninety + 0.3, B90), (T.ninety + 1.5, B90),
           (T.home - 0.6, B180), (T.loop - 1.9, B180), (T.loop + 0.5, B360), (T.circles - 1.3, B360),
           (T.circles + 0.4, BC * (1 + 1e-9)), default_ease="easy_ease")


def scr(xy):
    xy = np.atleast_2d(xy)
    return np.column_stack([HC[0] + K * xy[:, 0], HC[1] + K * xy[:, 1], np.zeros(len(xy))])


@lru_cache(maxsize=2048)
def path(b, r_out=14.0, hug=False):
    """Screen polyline of the ray aimed b (r_s) off-centre, clipped to the frame."""
    sgn, ab = np.sign(b), abs(b)
    ph, u, fate = S.orbit(ab, 1.0, phi_max=10 * PI)
    keep = u > 1.0 / 14.0
    if hug or (0 < ab / BC - 1 < 1e-5):                   # the orbiting ray: stop while it is still circling
        on = np.where(np.abs(u - 2 / 3) < 0.004)[0]
        if len(on):
            keep &= ph <= ph[on[0]] + 2.2 * TAU
            keep &= np.arange(len(u)) <= on[-1]
    i_peak = int(np.argmax(u))
    keep &= (np.arange(len(u)) <= i_peak) | (u > 1.0 / r_out)
    r = 1.0 / np.maximum(u[keep], 1e-9)
    p = scr(np.column_stack([-r * np.cos(ph[keep]), sgn * r * np.sin(ph[keep])]))
    ok = (np.abs(p[:, 0]) < 7.4) & (np.abs(p[:, 1]) < 4.3)
    return p[ok], fate


def poly(p, color, width=None, opacity=1.0):
    return VMobject(stroke_color=color, stroke_width=width or C.stroke, stroke_opacity=opacity) \
        .set_points_as_corners(p if len(p) > 1 else [HC, HC + 1e-3 * UP])


@scene(T.cut_ch4, T.cut_deep2)
def s05_fates(s):
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim(z=3)
    eq_badge = badge_eq()                                   # the equation returns when it is needed
    m.play(FadeIn(eq_badge, shift=0.2 * DOWN), at=T.where - 1.7, dur=0.7)
    m.play(FadeOut(eq_badge), at=T.perfect_circle + 1.2, dur=0.6)
    breathe(s, T.cut_ch4 + 2.0, T.cut_deep2)

    # the black hole left at the end of chapter 3 moves to the centre
    hole = Circle(radius=0.34, stroke_color=C.horizon, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1.0)
    hole.move_to([-1.2, -1.55, 0])
    m.add(hole)
    m.play(hole.animate.scale(K / 0.34).move_to(HC), at=T.cut_ch4 + 0.2, dur=1.3, ease="easy_ease")

    # ── one ray; its aim slides inward ───────────────────────────────────
    t_draw0, t_main1 = T.far_ray - 1.6, T.photon_sphere + 3.2
    main_op = 1.0 - key(t_main1 - 0.9, 0.0, 1.0, dur=0.9, lead=0)

    def main(t):
        p, _ = path(round(float(B_T(t)), 9))
        u = float(np.clip((t - t_draw0) / 3.0, 0.0, 1.0))
        u = u * u * (3 - 2 * u)
        return poly(p[: max(int(u * len(p)), 2)], C.light, opacity=float(main_op(t)))
    ray = glow.redraw(main, during=(t_draw0, t_main1))
    glow.remove(ray, at=t_main1)

    # where it was aimed: the straight line it would have followed
    def aim(t):
        y = HC[1] + K * float(B_T(t))
        op = float(fade(T.closer - 1.0, dur=0.6, out=T.guess - 0.6, lead=0)(t))
        return DashedLine([-7.0, y, 0], [6.6, y, 0], color=C.muted, stroke_width=C.thin, stroke_opacity=0.6 * op)
    aim_line = m.redraw(aim, during=(T.closer - 1.0, T.guess))
    m.remove(aim_line, at=T.guess)

    # pause and predict
    q = Eqn("?", size=140).move_to([4.6, 0.2, 0])
    m.play(FadeIn(q, scale=0.6), at=T.guess + 1.3, dur=0.6, ease="out_back")
    m.play(FadeOut(q, scale=1.3), at=T.circles - 1.4, dur=0.5)

    # it circles: a photon running round and round at r = 1.5 r_s
    runner = Dot(radius=0.09, color=C.text)
    t_r0, t_r1 = T.circles + 0.5, T.three_fates - 1.2
    glow.add(runner, at=t_r0)
    glow.drive(runner, lambda d, t: d.move_to(HC + 1.5 * K * np.array(
        [np.cos(1.9 * (t - t_r0) + 2.0), -np.sin(1.9 * (t - t_r0) + 2.0), 0.0])), during=(t_r0, t_r1))
    glow.play(FadeOut(runner), at=t_r1, dur=0.5)

    # ── the equation tells us where: on a circle u'' = 0 ─────────────────
    FR = r"\frac{3GM}{c^2}"
    ax = 4.55
    eA = Eqn(r"u'' + u = " + FR + r"\,u^2", colors={"u": C.light, FR: C.mass}, size=50).move_to([ax, 1.15, 0])
    m.play(TransformFromCopy(eq_badge, eA), at=T.where - 0.4, dur=1.1, ease="easy_ease")
    upp = VGroup(*eA.family_members_with_points()[:3])              # the three glyphs of u''
    strike = Line(upp.get_corner(DL) + 0.08 * DL, upp.get_corner(UR) + 0.08 * UR, color=C.bad, stroke_width=C.stroke)
    m.play(Create(strike), at=T.cross_out, dur=0.5)
    eB = Eqn(r"u = " + FR + r"\,u^2", colors={"u": C.light, FR: C.mass}, size=50).move_to([ax, -0.1, 0])
    m.play(FadeIn(eB, shift=0.2 * DOWN), at=T.cross_out + 1.5, dur=0.7)
    eC = Eqn(r"r = " + FR + r" = 1.5\,r_s", colors={"r_s": C.horizon, FR: C.mass, "1.5": C.ring}, size=50)
    eC.move_to([ax, -1.35, 0])
    m.play(FadeIn(eC, shift=0.2 * DOWN), at=T.one_and_half - 0.9, dur=0.7)
    m.play(Indicate(eC.part("1.5"), color=C.ring, scale_factor=1.4), at=T.one_and_half, dur=0.9)

    sphere = Circle(radius=1.5 * K, color=C.ring, stroke_width=C.thin + 1).move_to(HC)
    ps_name = Label("photon sphere", color=C.ring).move_to([ax, -2.3, 0])
    m.play(Create(sphere), FadeIn(ps_name, shift=0.15 * UP), at=T.photon_sphere - 0.3, dur=1.0)
    m.play(FadeOut(eA), FadeOut(strike), FadeOut(eB), at=T.photon_sphere + 2.0, dur=0.7)
    m.play(eC.animate.move_to([ax, 1.0, 0]), ps_name.animate.move_to([ax, 1.85, 0]), at=T.photon_sphere + 2.6, dur=0.9)

    # ── unstable: a hair outside spirals away, a hair inside spirals in ──
    def grow(b, t0, dur, t_out):
        p, _ = path(b)
        def f(t):
            u = float(np.clip((t - t0) / dur, 0.0, 1.0))
            return poly(p[: max(int(u * len(p)), 2)], C.light,
                        opacity=float(1.0 - key(t_out, 0.0, 1.0, dur=0.7, lead=0)(t)))
        h = glow.redraw(f, during=(t0, t_out + 0.8))
        glow.remove(h, at=t_out + 0.8)
    grow(BC * (1 + 3e-4), T.outside - 1.0, 3.0, T.three_fates - 1.9)
    grow(BC * (1 - 3e-4), T.inside - 0.4, 2.8, T.three_fates - 1.9)
    m.play(FadeOut(eC), FadeOut(ps_name), at=T.three_fates - 1.9, dur=0.7)

    # ── three fates: a whole fan of rays, coloured by what happens to them ──
    esc_b = [4.9, 4.1, 3.5, 3.05, 2.75]
    cap_b = [2.3, 1.8, 1.25, 0.7, 0.2]
    fan_out = T.cut_deep2 - 1.3

    def fan(bs, color, t0, lag, r_out=6.5, hug=False, t_gone=fan_out, dim=True):
        g = VGroup()
        for b in bs:
            for sg in (1, -1):
                p, _ = path(sg * b, r_out, hug)
                p = p[np.abs(p[:, 1] - HC[1]) < 2.75]            # stay clear of the badges along the top
                g.add(poly(p, color, width=C.thin + 1))
        m.play(LaggedStart(*[Create(x) for x in g], lag_ratio=lag), at=t0, dur=1.6)
        if dim:                                                 # step back when the shadow takes the stage
            m.play(g.animate.set_stroke(opacity=0.3), at=T.bigger - 0.6, dur=1.0)
        m.play(FadeOut(g), at=t_gone, dur=0.8)
        return g
    fan(esc_b, C.light, T.escapes - 0.3, 0.12)
    fan([BC * (1 + 1e-9)], C.ring, T.orbits - 0.2, 0.0, hug=True)
    fan(cap_b, C.bad, T.captured - 0.3, 0.12, t_gone=T.bigger - 0.6, dim=False)
    names = VGroup(Label("escapes", color=C.light), Label("orbits", color=C.ring), Label("captured", color=C.bad))
    names.arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([5.3, 1.2, 0])
    for lab, tt in zip(names, (T.escapes, T.orbits, T.captured)):
        m.play(FadeIn(lab, shift=0.15 * RIGHT), at=tt, dur=0.5)

    # what decides: how far off-centre it was aimed. The dividing line is 2.6 r_s
    x_b = -6.2
    axis = DashedLine([-7.0, HC[1], 0], [HC[0] - K, HC[1], 0], color=C.muted, stroke_width=C.thin, stroke_opacity=0.6)
    brace = DoubleArrow([x_b, HC[1], 0], [x_b, HC[1] + K * BC, 0], buff=0.0, color=C.shadow, stroke_width=C.thin + 1,
                        tip_length=0.16)
    b_lab = Eqn("b", size=46).set_color(C.shadow).next_to(brace, RIGHT, buff=0.15)
    m.play(Create(axis), GrowFromCenter(brace), FadeIn(b_lab), at=T.two_point_six - 4.6, dur=0.9)
    b_val = Eqn(r"b = 2.6\,r_s", colors={"r_s": C.horizon}, size=46).next_to(brace, RIGHT, buff=0.15)
    b_val[0].set_color(C.shadow)
    m.play(ReplacementTransform(b_lab, b_val), at=T.two_point_six, dur=0.7)
    edge = Circle(radius=BC * K, color=C.shadow, stroke_width=C.thin + 1).move_to(HC)
    m.play(Create(edge), at=T.two_point_six + 1.4, dur=1.4, ease="easy_ease")

    # the dark region is bigger than the hole itself
    dark = Circle(radius=BC * K, stroke_width=0, fill_color=C.bg, fill_opacity=1.0).move_to(HC)
    back = s.manim(z=2.5)                                      # above the rays, below the labels
    back.play(FadeIn(dark), at=T.bigger - 0.6, dur=1.0)
    inner = DashedVMobject(Circle(radius=K, color=C.horizon, stroke_width=C.thin + 1), num_dashes=28).move_to(HC)
    m.play(FadeOut(hole), FadeOut(sphere), FadeIn(inner), at=T.bigger - 0.6, dur=1.0)
    sizes = VGroup(Label("shadow", color=C.shadow), Label("hole", color=C.horizon))
    sizes[0].move_to(HC + [0, BC * K + 0.35, 0])
    sizes[1].move_to(HC)
    m.play(FadeIn(sizes), at=T.bigger, dur=0.6)

    # one equation, three fates → hand over to chapter 5
    m.play(FadeOut(names), FadeOut(axis), FadeOut(brace), FadeOut(b_val), FadeOut(sizes), at=fan_out, dur=0.8)
    # (the hand-over to chapter 5 now happens in s05c, after the deeper look at the potential hill)
