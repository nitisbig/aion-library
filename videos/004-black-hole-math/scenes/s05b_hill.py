"""s05b deeper look 2 (undergraduate): why exactly three fates. The radial motion of light is a ball on a
landscape, V(r) = (1 − r_s/r)/r², whose single peak sits at the photon sphere. The ball's level is 1/b²:
below the peak it turns back (escape), at the peak it balances (orbit), above it rolls over (capture)."""
from scipy.optimize import brentq

from aion import *
from aion.maths import schwarzschild as S

from beats import T
from shots import breathe, glow_fx, ray_path, readout, starfield

A, B = T.cut_deep2, T.cut_ready
X0, KX, Y0, KV = -5.7, 1.5, -2.7, 21.5                 # r = 1 r_s sits at X0; V is scaled by KV
R_FAR, BC = 7.0, S.critical_b(1.0)
V = lambda r: (1.0 - 1.0 / r) / r**2                    # noqa: E731  r in r_s; peak 4/27 at r = 1.5
PX = lambda r: X0 + KX * (r - 1.0)                      # noqa: E731
PY = lambda v: Y0 + KV * v                              # noqa: E731
B_LOW, B_HIGH = 4.0, 2.35                               # a wide aim, and one inside the critical aim
R_TURN = brentq(lambda r: V(r) - 1.0 / B_LOW**2, 1.5, R_FAR)

# the aim, as a function of time: wide → exactly critical → too close
B_T = keys((A, B_LOW), (T.hp_higher - 2.0, B_LOW), (T.hp_higher - 0.3, BC), (T.hp_clears - 1.5, BC),
           (T.hp_clears - 0.4, B_HIGH), (T.hp_one - 0.2, B_HIGH), (T.hp_sets - 0.6, BC), default_ease="easy_ease")
RUNS = [  # (start, end, kind, aim, fate colour token)
    (T.hp_comes + 1.6, T.hp_escapes + 1.6, "escape", B_LOW, "light"),
    (T.hp_higher - 0.2, T.hp_clears - 1.6, "orbit", BC * (1 + 1e-9), "ring"),
    (T.hp_clears - 0.6, T.hp_captured + 0.5, "capture", B_HIGH, "bad"),
]


def r_of(kind, u):
    """Where the ball is along the landscape, for progress u ∈ [0, 1] of its run."""
    if kind == "escape":                                # up to the turning point (70 % in), then back out
        if u < 0.7:
            k = u / 0.7
            return R_TURN + (R_FAR - R_TURN) * (1 - k) ** 2.2
        k = (u - 0.7) / 0.3
        return R_TURN + (R_FAR - R_TURN) * k ** 2
    if kind == "orbit":                                 # creeps onto the summit and stays
        return 1.5 + (R_FAR - 1.5) * np.exp(-6.5 * u)
    k = u * u * (3 - 2 * u)                             # capture: over the top and down into the hole
    return R_FAR + (1.0 - R_FAR) * k


@scene(A, B)
def s05b_hill(s):
    starfield(s)
    breathe(s, A + 2.0, B, zoom=1.03)
    glow = s.manim(fx=[glow_fx()], z=2)
    m = s.manim(z=3)

    # what chapter 4 left on screen fades: the shadow and the hole
    hc0 = np.array([0.3, -0.3, 0.0])
    old = VGroup(Circle(radius=BC * 0.55, color=C.shadow, stroke_width=C.thin + 1).move_to(hc0),
                 DashedVMobject(Circle(radius=0.55, color=C.horizon, stroke_width=C.thin + 1), num_dashes=28).move_to(hc0))
    m.add(old)
    m.play(FadeOut(old, scale=0.8), at=A + 0.4, dur=1.0)

    def timer(t):
        u = float(np.clip((t - T.hp_why) / (B - 1.2 - T.hp_why), 0.0, 1.0))
        op = float(fade(T.hp_why - 1.2, dur=0.6, out=B - 1.0, lead=0)(t))
        c = np.array([6.25, 3.3, 0.0])
        return VGroup(Circle(radius=0.26, color=C.faint, stroke_width=C.thin + 1, stroke_opacity=op).move_to(c),
                      Arc(radius=0.26, start_angle=PI / 2, angle=-TAU * (1 - u) - 1e-3, arc_center=c, color=C.text,
                          stroke_width=C.thin + 1, stroke_opacity=op))
    m.redraw(timer, during=(T.hp_why - 1.3, B))

    # ── the landscape: colour runs from the capture side, over the summit, out to the escape side ──
    rr = np.linspace(1.0, R_FAR + 0.25, 150)
    palette = [ManimColor(C.bad), ManimColor(C.ring), ManimColor(C.time_mid), ManimColor(C.grid)]

    def tint(r):
        x = np.clip([(r - 1.0) / 0.5, (r - 1.5) / 1.6, (r - 3.1) / 3.5], 0, 1)
        if r < 1.5:
            return interpolate_color(palette[0], palette[1], x[0])
        return interpolate_color(palette[1], palette[2], x[1]) if r < 3.1 else \
            interpolate_color(palette[2], palette[3], x[2])
    t_land = T.hp_ball - 0.6
    grow = key(t_land, 0.0, 1.0, dur=3.0, ease="easy_ease", lead=0)
    land_on = 1.0 - key(B - 1.0, 0.0, 1.0, dur=0.8, lead=0)

    def land(t):
        g, k, op = VGroup(), float(grow(t)), float(land_on(t))
        n = max(int(k * (len(rr) - 1)), 1)
        for i in range(n):                              # revealed from the hole outward
            a, b = rr[i], rr[i + 1]
            g.add(Polygon([PX(a), Y0, 0], [PX(a), PY(V(a)), 0], [PX(b), PY(V(b)), 0], [PX(b), Y0, 0], stroke_width=0,
                          fill_color=tint(0.5 * (a + b)), fill_opacity=0.55 * op))
        g.add(VMobject(stroke_color=C.text, stroke_width=C.thin + 1, stroke_opacity=op).set_points_as_corners(
            [[PX(r), PY(V(r)), 0] for r in rr[: n + 1]]))
        return g
    m.redraw(land, during=(t_land, B))
    base = Line([X0 - 1.2, Y0, 0], [PX(R_FAR + 0.25), Y0, 0], color=C.muted, stroke_width=C.thin)
    hole = VGroup(Rectangle(width=1.2, height=4.4, stroke_width=0, fill_color=C.bg, fill_opacity=1.0)
                  .move_to([X0 - 0.6, Y0 + 2.2, 0]),
                  Line([X0, Y0, 0], [X0, Y0 + 4.4, 0], color=C.horizon, stroke_width=C.stroke))
    hole_lab = Eqn("r_s", colors={"r_s": C.horizon}, size=40).move_to([X0, Y0 - 0.4, 0])
    ax_lab = Eqn("r", size=40).move_to([PX(R_FAR + 0.25) + 0.3, Y0, 0])
    m.play(Create(base), FadeIn(hole), FadeIn(hole_lab), FadeIn(ax_lab), at=t_land, dur=0.9)
    law = Eqn(r"V(r) = \frac{1}{r^2}\left(1 - \frac{r_s}{r}\right)", colors={"r_s": C.horizon}, size=50)
    law.move_to([-1.6, 2.75, 0])
    m.play(Write(law), at=T.hp_height - 0.3, dur=1.4)

    # the single peak sits exactly at the photon sphere
    peak = np.array([PX(1.5), PY(V(1.5)), 0.0])
    peak_line = DashedLine([peak[0], Y0, 0], peak, color=C.ring, stroke_width=C.thin + 1)
    peak_lab = Eqn(r"1.5\,r_s", colors={"r_s": C.horizon, "1.5": C.ring}, size=40).move_to([peak[0] + 0.15, Y0 - 0.4, 0])
    peak_dot = Dot(peak, radius=0.07, color=C.ring)
    m.play(FadeIn(peak_dot, scale=3.0), at=T.hp_peak, dur=0.6)
    m.play(Create(peak_line), FadeIn(peak_lab), at=T.hp_at_ps - 0.3, dur=0.8)
    m.play(hole_lab.animate.shift(0.45 * LEFT), at=T.hp_at_ps - 0.3, dur=0.6)

    # ── the ball's level is set by the aim: 1/b², with b read out live ──
    lvl_on = fade(T.hp_comes + 0.6, dur=0.7, lead=0) * land_on

    def level(t):
        b, op = float(B_T(t)), float(lvl_on(t))
        y = PY(1.0 / b**2)
        col = C.light if b > BC * 1.002 else (C.bad if b < BC * 0.998 else C.ring)
        line = DashedLine([X0, y, 0], [PX(R_FAR + 0.25), y, 0], color=col, stroke_width=C.thin + 1, stroke_opacity=op)
        tag = VGroup(Eqn("b", size=40), Eqn("=", size=40), readout(b, "", decimals=2, size=0.95),
                     Eqn("r_s", colors={"r_s": C.horizon}, size=40)).arrange(RIGHT, buff=0.14)
        tag.set_opacity(op).move_to([PX(5.0), y + 0.36, 0])
        return VGroup(line, tag)
    m.redraw(level, during=(T.hp_comes + 0.5, B))

    # ── three runs: the ball on the hill, and the same ray drawn round the hole ──
    ic, ik = np.array([4.85, 1.35, 0.0]), 0.27
    inset = VGroup(Circle(radius=ik, stroke_color=C.horizon, stroke_width=C.thin + 1, fill_color=C.bg, fill_opacity=1)
                   .move_to(ic), Circle(radius=1.5 * ik, color=C.ring, stroke_width=C.thin, stroke_opacity=0.6).move_to(ic))
    m.play(FadeIn(inset), at=T.hp_comes + 0.8, dur=0.7)
    m.play(FadeOut(inset), FadeOut(law), FadeOut(peak_line), FadeOut(peak_lab), FadeOut(peak_dot), FadeOut(base),
           FadeOut(hole), FadeOut(hole_lab), FadeOut(ax_lab), at=B - 1.0, dur=0.8)
    for t0, t1, kind, aim, role in RUNS:
        pts, _ = ray_path(aim, ic, ik, r_far=11.0, half=(1.8, 1.45))
        col = getattr(C, role)
        hold = T.hp_one + 2.6 if kind != "orbit" else T.hp_clears - 1.5       # how long this run's ray stays

        def ball(t, t0=t0, t1=t1, kind=kind):
            u = float(np.clip((t - t0) / (t1 - t0), 0.0, 1.0))
            r = float(r_of(kind, u))
            p = np.array([PX(r), PY(V(r)) + 0.13, 0.0])
            if kind == "orbit":
                p[0] += 0.035 * np.sin(5.0 * t) * float(u > 0.85)             # it trembles on the summit
            op = float(np.clip((t - t0) / 0.3, 0, 1) * (1.0 - np.clip((t - t1) / 0.4, 0, 1)))
            if kind == "capture":
                op *= float(np.clip((r - 1.0) / 0.12, 0, 1))                   # swallowed at the horizon
            return Dot(p, radius=0.13, color=C.text, fill_opacity=op)
        hb = glow.redraw(ball, during=(t0, t1 + 0.5))
        glow.remove(hb, at=t1 + 0.5)

        def ray(t, t0=t0, t1=t1, pts=pts, col=col, kind=kind, hold=hold):
            u = float(np.clip((t - t0) / (t1 - t0), 0.0, 1.0))
            u = min(u / 0.7, 1.0) if kind == "escape" else u                   # the ray is done when the ball turns
            op = float(1.0 - np.clip((t - hold) / 0.6, 0, 1)) * float(land_on(t))
            return VMobject(stroke_color=col, stroke_width=C.thin + 1, stroke_opacity=op) \
                .set_points_as_corners(pts[: max(int(u * len(pts)), 2)])
        hr = m.redraw(ray, during=(t0, hold + 0.7))
        m.remove(hr, at=hold + 0.7)

    # one hill, three outcomes; the height of the peak is what sets 2.6
    fates = VGroup(Label("escapes", color=C.light), Label("orbits", color=C.ring), Label("captured", color=C.bad))
    fates.arrange(RIGHT, buff=0.4).scale(0.75).move_to([4.7, -0.45, 0])
    for lab, tt in zip(fates, (T.hp_escapes, T.hp_orbit, T.hp_captured)):
        m.play(FadeIn(lab, shift=0.12 * UP), at=tt, dur=0.5)
    m.play(FadeOut(fates), at=B - 1.0, dur=0.8)
    m.play(Indicate(peak_dot, color=C.ring, scale_factor=3.0), at=T.hp_sets, dur=1.0)
