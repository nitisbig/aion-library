"""c04_s02 · Three pushes (equation). Storyboard: plan/scene_plan.md § c04_s02. Composition: design frame 06.

The parcel from c04_s01 sits in a field of flow arrows; Navier–Stokes writes across the top and each force term
lights with its own picture: 'carried' (the parcel drifts with the flow, leaving a streak), 'pressure' (a dim
high-to-low pressure field and arrows pushing the parcel from high to low), 'sticky' (a column of arrows through the
parcel smooths toward its neighbours' speeds; the profile is the exact viscous solution, a Gaussian spreading with
σ = √(2νt)). On 'obstacle' the stage becomes the vortex street behind a cylinder (ch4.street, lattice Boltzmann),
and the camera drifts along the wake.
"""
import math

import numpy as np
from aion import *
from scipy.ndimage import gaussian_filter1d

import ch4
from beats import T
from kit import chapter_backdrop, P3, X1, XW, Y0, add_rail, glow, lin_rgb, polyline, sans, smooth01, tag_under, tint

PC = np.array([-1.2, -0.85])                     # where the parcel settles on the stage
SIDE = 1.0
ROWS = np.linspace(-2.55, 0.85, 5)
COLS = np.linspace(-5.6, 5.6, 9)


def flow(x, y):
    """The stage's gentle flow (left to right, slightly wavy)."""
    return 0.55 + 0.08 * np.sin(0.9 * y + 0.4), 0.12 * np.sin(0.6 * x)


def _grid(op, p, col):
    """Flow arrows, leaving room round the parcel at p (and its whole column once `col`)."""
    g = VGroup()
    for y in ROWS:
        for x in COLS:
            if abs(x - p[0]) < 0.9 and (col or abs(y - p[1]) < 0.9):
                continue
            u, v = flow(x, y)
            g.add(Arrow(P3(x - u * 0.45, y - v * 0.45), P3(x + u * 0.45, y + v * 0.45), buff=0, stroke_width=2,
                        color=C.muted, tip_length=0.11, max_tip_length_to_length_ratio=0.3).set_opacity(op))
    return g


@scene(T.c04_s02, T.c04_s03)
def s14_c04_terms(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 4)
    add_rail(s, 4, busy=True)
    t_add, t_car, t_pr, t_vis, t_obs, t_oth = (T.c04_s02_adds_up, T.c04_s02_carries, T.c04_s02_pressure,
                                               T.c04_s02_viscosity, T.c04_s02_obstacle, T.c04_s02_other)
    t0 = float(s.start)
    hud = s.manim(z=50, parallax=0.0)

    # the parcel: from the centre of c04_s01's last frame to its place on the stage, then carried
    def ppos(t):
        u = float(smooth01((t - t0 - 0.2) / 1.6))
        p = PC * u
        c = float(smooth01((t - float(t_car)) / 1.4))
        return p + np.array([1.5 * c, 0.0])

    def parcel(t):
        p = ppos(t)
        sz = SIDE
        op = 1 - float(smooth01((t - float(t_obs) + 0.6) / 0.5))
        return Square(sz, stroke_color=C.navier, stroke_width=2.8, stroke_opacity=op, fill_color=C.navier,
                      fill_opacity=0.18 * op).move_to(P3(*p))
    glow(s, C.navier, z=8, k=0.45).redraw(parcel, during=(s.start, t_obs))
    g_op = fade(t_add - 0.2, dur=0.8, out=t_obs - 0.6, out_dur=0.5)
    s.manim(z=4).redraw(lambda t: _grid(float(g_op(t)), ppos(t), t > float(t_vis) - 0.2), during=(t_add - 0.4, t_obs))

    # Navier–Stokes across the top (screen-locked, frame 06)
    adv, pr, vis = r"\mathbf u\cdot\nabla\mathbf u", r"-\nabla p", r"\mu\nabla^2\mathbf u"
    e = Eqn(r"\rho\Big(\frac{\partial\mathbf u}{\partial t}+\mathbf u\cdot\nabla\mathbf u\Big)=-\nabla p+\mu\nabla^2\mathbf u+\mathbf f",
            colors={adv: C.text, pr: C.text, vis: C.text})
    e.scale(0.82).move_to(P3(0.55, 2.6))
    hud.play(Write(e), at=t_add, dur=1.6)
    inc = VGroup(Eqn(r"\nabla\cdot\mathbf u=0").scale(0.62), sans("no gaps", 20, C.muted)).arrange(RIGHT, buff=0.25)
    inc.move_to(P3(X1, 1.62), aligned_edge=RIGHT)
    hud.play(FadeIn(inc), at=t_add + 1.8, dur=0.6)
    for part, word, col, at in ((adv, "carried", C.navier, t_car), (pr, "pressure", C.charge_p, t_pr),
                                (vis, "sticky", C.light, t_vis)):
        hud.play(e.part(part).animate.set_color(col), at=at, dur=0.4)
        hud.play(FadeIn(tag_under(e, part, word, col, 0.1), shift=0.06 * UP), at=at + 0.1, dur=0.5)

    # carried: a streak behind the parcel
    def streak(t):
        a, b = float(t_car), min(t, float(t_pr) + 2.0)
        if b <= a + 0.02:
            return VGroup()
        ts = np.linspace(a, b, 40)
        pts = [ppos(x) for x in ts]
        op = 1 - float(smooth01((t - float(t_vis) + 0.3) / 0.5))
        return polyline(pts, C.navier, 3, 0.8 * op)
    s.manim(z=7).redraw(streak, during=(t_car, t_vis + 0.4))

    # pressure: high on the left, low on the right; the push goes from high to low
    ext = (2 * XW, 3.6)
    xs = np.linspace(-XW, XW, 240)
    ys = np.linspace(-1.8, 1.8, 60)
    X, Y = np.meshgrid(xs, ys)
    pf = (0.5 - 0.5 * np.tanh((X - 0.3) / 2.2)) * np.clip((1.8 - np.abs(Y)) / 0.6, 0, 1)
    p_op = fade(t_pr - 0.1, dur=0.8, out=t_vis - 0.3, out_dur=0.6)
    s.add(FieldLayer(lambda t: pf, cmap="ramp", colors=(C.bg, C.bg, tint(C.charge_p, 0.035)), vmin=0, vmax=1,
                     extent=ext, center=(0, -0.85), z=-10, opacity=p_op, start=t_pr - 0.3, end=t_vis + 0.6))
    pm = s.manim(z=9)
    hl = VGroup(sans("high pressure", 24, C.charge_p).move_to(P3(-4.9, 1.2)), sans("low", 24, C.muted).move_to(P3(3.9, 1.2)))

    def push(t):
        p = ppos(t)
        op = float(p_op(t))
        g = VGroup()
        for dy in (-0.3, 0, 0.3):
            g.add(Arrow(P3(p[0] - 1.5, p[1] + dy), P3(p[0] - 0.55, p[1] + dy), buff=0, stroke_width=4,
                        color=C.charge_p, tip_length=0.16).set_opacity(op))
        return g
    pm.redraw(push, during=(t_pr, t_vis + 0.4))
    pm.play(FadeIn(hl), at=t_pr + 0.3, dur=0.5)
    pm.play(FadeOut(hl), at=t_vis - 0.3, dur=0.5)

    # sticky: a column of arrows through the parcel; their speeds spread like heat (Gaussian, σ = √(2νt))
    n = 9
    yy = np.linspace(-2.6, 0.9, n)
    u0 = np.array([0.35, 0.9, 0.3, 1.2, 1.6, 0.4, 1.0, 0.25, 0.7])     # jagged neighbours; the parcel is row 4
    v_op = fade(t_vis - 0.1, dur=0.5, out=t_obs - 0.6, out_dur=0.5)

    def sticky(t):
        tau = max(t - float(t_vis) - 0.6, 0.0)
        sig = math.sqrt(2 * 0.35 * tau)
        u = gaussian_filter1d(u0, sig, mode="nearest") if sig > 1e-3 else u0
        x = ppos(t)[0]
        op = float(v_op(t))
        g = VGroup()
        for y, ui in zip(yy, u):
            g.add(Arrow(P3(x - 0.8, y), P3(x - 0.8 + 1.0 * ui, y), buff=0, stroke_width=3.2, color=C.light,
                        tip_length=0.14, max_tip_length_to_length_ratio=0.3).set_opacity(op))
        return g
    s.manim(z=10).redraw(sticky, during=(t_vis - 0.2, t_obs))

    # obstacle: the vortex street behind a cylinder
    d = ch4.street()
    h, cyl, r = ch4.street_geom(d)
    s_op = fade(t_obs - 0.4, dur=1.0)
    s.add(FramesLayer(ch4.street_frames(d, float(t_obs) - 0.6), height=h, pos=(0, -0.45), z=-2, opacity=s_op,
                      during=[(t_obs - 0.5, s.end)]))
    cm = s.manim(z=3)
    cm.play(FadeIn(Circle(radius=r, stroke_color=C.ghost, stroke_width=1.6, fill_color=C.card, fill_opacity=1)
                   .move_to(P3(*cyl))), at=t_obs - 0.2, dur=0.6)
    hud.play(FadeOut(VGroup(inc)), at=t_obs - 0.4, dur=0.5)
    s.camera.frame(t_obs + 1.6, center=(1.6, -0.2), zoom=1.12, dur=3.8)
