"""c07_s02 · Step size (equation). Storyboard: plan/scene_plan.md § c07_s02. Layout L3 (one open stage).

Opens on c07_s01's last frame (the hill from above, the walker in the deeper valley, the rule), which fades as
three valleys f(x) = x² take its place. 'size': three balls run the same rule x ← x − η f′(x) from x = −2 with
η = 0.05, 0.4 and 1.1 (exact iterates, x ← (1 − 2η) x): 'slow' the first crawls, the second settles in a few steps,
and 'leap' the third jumps past the bottom, further each time, out of the valley. 'error': fourteen points (seeded),
a flat line, and on the right the line's error L(m, b) as a contour map over its slope m and shift b. 'fit': each
step downhill on that map turns and shifts the line (exact gradient steps, η = 0.12); the leftover gaps and the
error bar shrink; 'as small' it rests at the least-squares line.
"""
import math

import numpy as np
from aion import *

import ch7
from beats import T
from kit import chapter_backdrop, P3, add_rail, glow, mix, polyline, sans, smooth01, tag_under, tex, tint

ROWS = (2.05, 0.15, -1.75)                      # the three valleys
XC, SX, A2, DROP = -3.0, 0.8, 0.19, 0.7         # screen x of x = 0, units per x, curvature, valley depth



def vx(x, yc):
    return np.array([XC + SX * x, yc - DROP + A2 * x * x])


def ball_pos(xs, t, t_start, dt, hop=0.5):
    """Position on screen (and whether it has left the valley) of a ball whose k-th hop starts at t_start + k dt."""
    k = int(math.floor((t - t_start) / dt))
    if k < 0:
        return xs[0], 0.0, False
    k = min(k, len(xs) - 2)
    u = float(np.clip((t - t_start - k * dt) / hop, 0, 1))
    a, b = xs[k], xs[k + 1]
    x = a + (b - a) * (u * u * (3 - 2 * u))
    lift = (0.22 + 0.12 * abs(b - a)) * 4 * u * (1 - u)
    return x, lift, abs(b) > 3.0 and u > 0.6


def cols():
    return (tint(C.descent, 0.6), C.descent, mix(C.descent, C.light, 0.5))


def fit_at(t, t_fit, dt=0.2):
    """(m, b) and the number of steps taken at time t (each step eased over 0.15 s)."""
    P = ch7.fit_path()
    u = (t - t_fit) / dt
    if u <= 0:
        return P[0], 0
    k = min(int(u), len(P) - 2)
    f = float(smooth01(min((u - k) / 0.75, 1.0))) if int(u) < len(P) - 1 else 1.0
    return P[k] + (P[k + 1] - P[k]) * f, k + (1 if f > 0.5 else 0)


@scene(T.c07_s02, T.c07_s03)
def s23_c07_step_size(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 7)
    add_rail(s, 7)
    t0 = float(s.start)
    t_sz, t_sl, t_lp, t_er, t_fi, t_as = (T.c07_s02_size, T.c07_s02_slow, T.c07_s02_leap, T.c07_s02_error,
                                          T.c07_s02_fit, T.c07_s02_as_small)

    # c07_s01's last frame: the hill from above, the walker in the valley, the rule
    t_end = float(t0) - 0.01
    out = fade(t0 - 5, dur=0.1, out=t0 + 0.2, out_dur=0.8)
    cam = lambda t: ch7.fog_cam(t_end)
    s.shader("hill.frag", z=0, parallax=0.0, animated=False,
             **ch7.hill_uniforms(cam, mode=0, opacity=out, fog=0.0, walker=(0.0, 0.0), fr=1.0))
    c_end = ch7.fog_cam(t_end)
    q = c_end.project(ch7.on_hill(ch7.trail(t_end), lift=0.03))
    car = s.manim(z=4, parallax=0.0, opacity=out)
    car.add(polyline([tuple(v) for v in q], C.light, 2.6, 0.85))
    glow(s, C.light, z=6, k=0.9, parallax=0.0, opacity=out).add(
        Dot(P3(*c_end.project(ch7.on_hill(ch7.walker_xy(t_end)[0], lift=0.05))[0]), radius=0.09, color=C.light))
    from kit import RC
    e = Eqn(r"\theta\leftarrow\theta-\eta\,\nabla L(\theta)", colors={r"\nabla L": C.descent, r"\eta": C.text})
    e.scale(1.05).move_to(P3(RC, 1.55))
    tags = VGroup(tag_under(e, r"\eta", "position", C.muted).align_to(e, LEFT),
                  tag_under(e, r"\eta", "step size", C.muted).align_to(e.part(r"\eta"), RIGHT).shift(0.12 * RIGHT),
                  tag_under(e, r"\nabla L", "slope", C.descent))
    s.manim(z=50, parallax=0.0, opacity=out).add(e, tags)

    # three valleys, three step sizes
    r_op = fade(t_sz - 0.3, dur=0.6, out=t_er - 0.3, out_dur=0.6)
    m = s.manim(z=3, opacity=r_op)
    labels = (("too small", r"\eta=0.05"), ("about right", r"\eta=0.4"), ("too large", r"\eta=1.1"))
    for yc, (w, et), c in zip(ROWS, labels, cols()):
        xs = np.linspace(-3.0, 3.0, 120)
        m.add(polyline([tuple(vx(x, yc)) for x in xs], C.muted, 2.0),
              VGroup(sans(w, 24, c), tex(et, 28, C.muted)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
              .move_to(P3(XC + SX * 3.0 + 0.45, yc - 0.15), aligned_edge=LEFT))
    starts = (float(t_sz) + 1.6, float(t_sz) + 1.6, float(t_lp) - 0.7)
    dts = (0.55, 0.55, 0.62)

    def balls(t):
        a = float(r_op(t))
        g = VGroup()
        if a < 0.01:
            return g
        for yc, eta, c, t1, dt in zip(ROWS, ch7.ETAS, cols(), starts, dts):
            xs = ch7.iterates(eta)
            x, lift, gone = ball_pos(xs, t, t1, dt)
            if abs(x) > 3.6:
                continue
            p = vx(x, yc) + np.array([0, 0.11 + lift])
            fall = 1.0 - (float(smooth01((abs(x) - 3.0) / 0.5)) if abs(x) > 3.0 else 0.0)
            g.add(Dot(P3(*p), radius=0.11, color=c, fill_opacity=a * fall))
        return g
    glow(s, C.descent, z=5, k=0.6).redraw(balls, during=(t_sz - 0.4, t_er + 0.4))

    # the computer's hill: a line's error
    f_op = fade(t_er - 0.1, dur=0.7)
    x, y = ch7.fit_data()
    pts = VGroup(*[Dot(P3(*ch7.sc(a, b)), radius=0.07, color=C.data) for a, b in zip(x, y)])
    ax = VGroup(Line(P3(*ch7.sc(-2.6, 0)), P3(*ch7.sc(2.6, 0)), stroke_color=tint(C.muted, 0.6), stroke_width=1.4),
                Line(P3(*ch7.sc(0, -1.6)), P3(*ch7.sc(0, 2.4)), stroke_color=tint(C.muted, 0.6), stroke_width=1.4))
    fm = s.manim(z=6)
    fm.play(FadeIn(ax), at=t_er - 0.1, dur=0.6)
    fm.play(FadeIn(pts, lag_ratio=0.08), at=t_er, dur=1.0)
    t_fit = float(t_fi) + 0.15

    def line(t):
        (mm, bb), _ = fit_at(t, t_fit)
        a = float(f_op(t))
        xs = np.linspace(-2.6, 2.6, 200)
        ys = mm * xs + bb
        keep = (ys > -1.8) & (ys < 2.6)                       # stay inside the scatter's own space (clear of the rail)
        if keep.sum() < 2:
            return VGroup()
        return polyline([tuple(ch7.sc(a_, b_)) for a_, b_ in zip(xs[keep], ys[keep])], C.descent, 4, a)
    glow(s, C.descent, z=7, k=1.1).redraw(line, during=(t_er - 0.2, s.end))

    def gaps(t):
        (mm, bb), _ = fit_at(t, t_fit)
        a = float(f_op(t))
        return VGroup(*[Line(P3(*ch7.sc(xi, yi)), P3(*ch7.sc(xi, float(np.clip(mm * xi + bb, -1.8, 2.6)))),
                             stroke_color=C.muted, stroke_width=1.6,
                             stroke_opacity=0.8 * a) for xi, yi in zip(x, y)])
    s.manim(z=5).redraw(gaps, during=(t_er - 0.2, s.end))

    # the error, over the line's slope and shift (its path in a pale descent hue: C.data dots share the frame)
    PATH_C = mix(C.descent, C.light, 0.5)
    cm = s.manim(z=6, opacity=fade(t_er + 0.3, dur=0.8))
    x0, x1, y0, y1 = ch7.MAP
    cm.add(ch7.contours(), tex("m", 32, C.muted).move_to(P3((x0 + x1) / 2, y0 - 0.32)),
           tex("b", 32, C.muted).move_to(P3(x0 - 0.3, (y0 + y1) / 2)))
    L = Eqn(r"L(m,b)=\frac{1}{n}\sum_i\,(y_i-m\,x_i-b)^2", colors={"L(m,b)": C.descent})
    L.scale(0.8).move_to(P3((x0 + x1) / 2, 2.25))
    hud = s.manim(z=50, parallax=0.0)
    hud.play(Write(L), at=t_er + 0.5, dur=1.2)
    hud.play(FadeIn(tag_under(L, "L(m,b)", "error", C.descent), shift=0.05 * UP), at=t_er + 1.4, dur=0.5)

    def walk(t):
        P = ch7.fit_path()
        (mm, bb), k = fit_at(t, t_fit)
        a = float(fade(t_fi - 0.4, dur=0.5)(t))
        q = [tuple(ch7.mp(*P[j])) for j in range(k)] + [tuple(ch7.mp(mm, bb))]
        g = VGroup()
        if len(q) > 1:
            g.add(polyline(q, PATH_C, 2, 0.8 * a))
        g.add(*[Dot(P3(*v), radius=0.035, color=PATH_C, fill_opacity=0.8 * a) for v in q[:-1]])
        g.add(Dot(P3(*ch7.mp(mm, bb)), radius=0.08, color=PATH_C, fill_opacity=a))
        return g
    glow(s, C.descent, z=8, k=0.6).redraw(walk, during=(t_fi - 0.5, s.end))

    # the error as a bar
    L0 = float(ch7.fit_loss(*ch7.fit_path()[0]))

    def bar(t):
        (mm, bb), _ = fit_at(t, t_fit)
        a = float(f_op(t))
        h = ch7.BAR_H * float(ch7.fit_loss(mm, bb)) / L0
        return VGroup(Rectangle(width=0.22, height=max(h, 0.01), stroke_width=0, fill_color=C.descent, fill_opacity=a)
                      .move_to(P3(ch7.BAR_X, ch7.BAR_Y0 + h / 2)),
                      tex("L", 28, C.descent).set_opacity(a).move_to(P3(ch7.BAR_X, ch7.BAR_Y0 - 0.28)))
    s.manim(z=6).redraw(bar, during=(t_er - 0.2, s.end))
    ring = Circle(radius=0.2, stroke_color=PATH_C, stroke_width=2).move_to(P3(*ch7.mp(*ch7.fit_path()[-1])))
    hud.play(Create(ring), at=t_as + 0.1, dur=0.6)
    assert np.allclose(ch7.fit_path()[-1], ch7.least_squares()[::1], atol=0.03), (ch7.fit_path()[-1], ch7.least_squares())
