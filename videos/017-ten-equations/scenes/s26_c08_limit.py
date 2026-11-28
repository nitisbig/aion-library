"""c08_s02 · The limit (equation). Storyboard: plan/scene_plan.md § c08_s02. Layout L2.

Opens on c08_s01's last frame (the noisy scope trace and the receiver's reading), which gives way to a tilted
constellation plane: two signal levels, each with its cloud of received samples (seeded Gaussian noise, one σ for
all). 'pack': the two split into four, then sixteen, all inside the same peak amplitude, so the gaps shrink; 'blur':
the clouds overlap and every sample nearer another point than its own flashes as an error (computed). 'limit': the
capacity equation writes in the right column; 'wide': B lights with a band of frequencies; 'strong': S/N lights and
the capacity curve draws, with one computed point (20 MHz at 30 dB, 199 Mbit/s). 'rare': with coding the clouds
tighten and the errors vanish.
"""
import math

import numpy as np
from aion import *

import ch8
from beats import T
from kit import chapter_backdrop, P3, add_rail, glow, polyline, sans, smooth01, tint


def _carry(s, out):
    """c08_s01's last frame: grid, sent bits, the noisy trace, threshold, the reading with its two errors."""
    op = fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.6)
    m = s.manim(z=3, parallax=0.0, opacity=op)
    m.add(*[Line(P3(x, -1.9), P3(x, 2.05), stroke_color=tint(C.muted, 0.22), stroke_width=1.0)
            for x in np.linspace(ch8.SX0, ch8.SX1, len(ch8.BITS) + 1)],
          *[Line(P3(ch8.SX0, y), P3(ch8.SX1, y), stroke_color=tint(C.muted, 0.22), stroke_width=1.0)
            for y in (ch8.SY - ch8.SA, ch8.SY + ch8.SA)],
          *[sans(b, 24, C.muted).move_to(P3(ch8.SX0 + (j + 0.5) * ch8.slot_w(), 2.45)) for j, b in enumerate(ch8.BITS)],
          DashedLine(P3(ch8.SX0, ch8.SY), P3(ch8.SX1, ch8.SY), dash_length=0.12, stroke_color=C.muted, stroke_width=1.6),
          *[sans(str(d), 24, C.bad if w else C.text).move_to(P3(xc, -2.3)) for xc, d, w in ch8.decisions()],
          *[Circle(radius=0.24, stroke_color=C.bad, stroke_width=2.5).move_to(P3(xc, -2.3))
            for xc, d, w in ch8.decisions() if w],
          sans("noise", 26, C.noise).move_to(P3(ch8.SX1 - 0.5, -1.55)))
    x, y = ch8.trace(1.0)
    glow(s, C.shannon, z=5, k=0.35, parallax=0.0, opacity=op).add(polyline(list(zip(x, y)), C.shannon, 3.0))


@scene(T.c08_s02, T.c08_s03)
def s26_c08_limit(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 8)
    t0 = float(s.start)
    t_pk, t_bl, t_li, t_wi, t_st, t_ra = (T.c08_s02_pack, T.c08_s02_blur, T.c08_s02_limit, T.c08_s02_wide,
                                          T.c08_s02_strong, T.c08_s02_rare)
    _carry(s, t0 + 0.25)
    add_rail(s, 8)

    # the constellation plane: 2 → 4 → 16 points inside one peak amplitude, one noise level
    t4, t16 = float(t_pk) - 0.1, float(t_pk) + 1.9
    yaw = lambda t: -0.10 + 0.2 * (t - t0) / 25.0                      # a slow turn of the plane
    shrink = lambda t: 1.0 - 0.45 * float(smooth01((t - float(t_ra) - 0.1) / 1.4))   # coding tightens the clouds

    def stage(t):
        """(M, the points now (moving from their parents while splitting))."""
        if t < t4:
            return 2, ch8.constellation(2)
        if t < t16:
            u = float(smooth01((t - t4) / 0.8))
            P, Q = ch8.constellation(4), ch8.constellation(2)
            par = Q[(P[:, 0] > 0).astype(int)]
            return 4, par + (P - par) * u
        u = float(smooth01((t - t16) / 1.0))
        P, Q = ch8.constellation(16), ch8.constellation(4)
        par = np.array([Q[np.argmin(((Q - p) ** 2).sum(1))] for p in P])
        return 16, par + (P - par) * u

    def rx(t):
        M, P = stage(t)
        _, unit, sent = ch8.samples(M)
        R = P[sent] + ch8.SIGMA * shrink(t) * unit
        near = np.argmin(((R[:, None, :] - ch8.constellation(M)[None]) ** 2).sum(-1), 1)
        return R, near != sent

    pl_op = fade(t0 + 0.4, dur=0.8)
    s.add(PointsLayer(lambda t: ch8.plane(rx(t)[0], yaw(t)), color=C.noise, size=2.2, glow=0.0, alpha=pl_op * 0.55,
                      additive=False, z=2, parallax=0.0))
    flash = lambda t: float(smooth01((t - float(t_bl) + 0.1) / 0.3)) * (1.0 + 0.6 * math.exp(-max(t - float(t_bl), 0) * 2.5))

    def errs(t):
        R, bad = rx(t)
        q = ch8.plane(R, yaw(t))
        return np.where(bad[:, None], q, 99.0)
    s.add(PointsLayer(errs, color=C.bad, size=2.8, glow=0.0, alpha=Track(lambda t: min(flash(t), 1.0) * float(pl_op(t))),
                      additive=False, z=2.5, parallax=0.0))

    def frame(t):
        a = float(pl_op(t))
        M, P = stage(t)
        L = 1.4
        ax = [ch8.plane(np.array([[-L, 0], [L, 0]]), yaw(t)), ch8.plane(np.array([[0, -L], [0, L]]), yaw(t))]
        g = VGroup(*[Line(P3(*a_[0]), P3(*a_[1]), stroke_color=tint(C.muted, 0.45), stroke_width=1.2,
                          stroke_opacity=a) for a_ in ax])
        g.add(*[Dot(P3(*q), radius=0.06, color=C.light, fill_opacity=a) for q in ch8.plane(P, yaw(t))])
        return g
    s.manim(z=3, parallax=0.0).redraw(frame, during=(t0 + 0.2, s.end))

    def count(t):
        M, _ = stage(t + 0.4)
        a = float(pl_op(t))
        return sans(f"{M} levels", 26, C.text).set_opacity(a).move_to(P3(ch8.CC[0], 2.35))
    s.manim(z=50, parallax=0.0).redraw(count, during=(t0 + 0.2, s.end))
    hud = s.manim(z=50, parallax=0.0)
    hud.play(FadeIn(sans("noise", 24, C.noise).move_to(P3(0.1, 0.55), aligned_edge=LEFT)), at=t0 + 1.0, dur=0.6)
    el = sans("errors", 24, C.bad).move_to(P3(0.1, 0.0), aligned_edge=LEFT)
    hud.play(FadeIn(el), at=t_bl + 0.2, dur=0.5)
    hud.play(FadeOut(el), at=t_ra + 1.0, dur=0.6)

    # the limit
    e = ch8.capacity_eqn()
    tc, tb, tsn = ch8.eqn_tags(e)
    hud.play(Write(e), at=t_li - 0.1, dur=1.2)
    hud.play(FadeIn(tc, shift=0.05 * UP), at=t_li + 0.9, dur=0.5)

    # wide: the band of frequencies
    ax, spec, br = ch8.band()
    bm = s.manim(z=4, parallax=0.0)
    hud.play(FadeIn(tb, shift=0.05 * UP), at=t_wi, dur=0.5)
    bm.play(FadeIn(ax), at=t_wi - 0.1, dur=0.5)
    bm.play(Create(spec), at=t_wi + 0.1, dur=0.8)
    bm.play(GrowFromCenter(br), at=t_wi + 0.6, dur=0.6)

    # strong: signal over noise, and the capacity curve it buys
    hud.play(FadeIn(tsn, shift=0.05 * UP), at=t_st, dur=0.5)
    bm.play(FadeIn(ch8.graph_axes()), at=t_st + 0.1, dur=0.6)
    t_cv = float(t_st) + 0.5
    glow(s, C.shannon, z=5, k=0.6, parallax=0.0).redraw(
        lambda t: polyline(ch8.curve_pts(max(float(smooth01((t - t_cv) / 1.8)), 0.01)), C.shannon, 3.0)
        if t > t_cv else VGroup(), during=(t_cv - 0.1, s.end))
    dot, guide, lab = ch8.marker()
    bm.play(Create(guide), at=t_cv + 1.9, dur=0.4)
    bm.play(FadeIn(dot, scale=0.5), at=t_cv + 2.1, dur=0.3)
    hud.play(FadeIn(lab, shift=0.05 * UP), at=t_cv + 2.2, dur=0.5)

    # rare: coding tightens the clouds, and the errors vanish
    hud.play(FadeIn(sans("coding", 24, C.text).move_to(P3(0.1, 0.0), aligned_edge=LEFT)), at=t_ra + 1.3, dur=0.5)
