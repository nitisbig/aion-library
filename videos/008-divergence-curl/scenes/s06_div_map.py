"""Ch2 · the divergence map, and the lamp. The hero stream returns; a scan line paints the divergence of every point
(orange where positive, blue where negative). The two blobs get their signs, and the dust agrees: a cluster spreads
over the warm spot, a ring of grains closes in over the cool one. Then one more flow on black: the lamp, arrows
pointing out and shrinking. "So the divergence must be positive. Right?" The scan line runs again and lights a
single point. Circles of radius r and 2r: the edge doubles, the arrows halve, 2 x 1/2 = 1, the flux is 2 pi through
both. The lamp shrinks into a tile parked top right (the plant, paid off in Ch4), and the del-dot F badge drops."""
from aion import *

from beats import T
from shots import (BADGES, HERO_SRC, _eye, advect_table, arrow, badge, ease, field_arrows, hero, hero_div, hero_eyes,
                   lamp, lic, live, ramp, sample_grid, stage, tex)
from sims import RATE, dust_layer, hero_dust

E = "easy_ease"
FULL = (14.4, 8.2)
RES = (320, 180)
A, _ = hero_eyes()
SINK = np.array(_eye(HERO_SRC[1][0]))
LC = np.array([0.9, -0.2])                      # the lamp
R1, R2 = 1.3, 2.6
XS = np.linspace(-FULL[0] / 2, FULL[0] / 2, RES[0])


def scan(D, t0, dur=1.8, soft=0.5):
    """A field sampler that reveals D left to right (a scan line moving from x=-7.6 to 7.6 over `dur`)."""
    def f(t):
        xw = -7.6 + 15.2 * ramp(t, t0, t0 + dur)
        mask = np.clip((xw - XS) / soft, 0.0, 1.0)
        return D * mask[None, :]
    return f


def scan_line(m, t0, dur=1.8):
    def line(t):
        xw = -7.6 + 15.2 * ramp(t, t0, t0 + dur)
        k = np.sin(np.pi * np.clip((t - t0) / dur, 0, 1))
        return Line([xw, -4.3, 0], [xw, 4.3, 0], color=C.div, stroke_width=C.thin + 0.5).set_stroke(opacity=0.8 * k)
    h = live(m, line, (t0, t0 + dur + 0.05))
    m.remove(h[-1], at=t0 + dur + 0.1)


def sign_tag(c, sym, col):
    return VGroup(Circle(radius=0.34, stroke_color=col, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1.0),
                  tex(sym, size=56, color=C.text)).move_to([*c, 0])


@scene(T.cut_map, T.cut_ch3)
def s06_div_map(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:1])
    reset = (T.one_more - 0.3, T.one_more + 0.5)

    # ── the hero stream returns ──
    k_st = keys((s.start, 0.0), (s.start + 0.2, 0.0), (s.start + 1.8, 1.0, E), (T.color_plane, 1.0),
                (T.color_plane + 1.5, 0.55, E), (T.agrees - 0.2, 0.55), (T.agrees + 0.8, 1.0, E), (reset[0], 1.0),
                (reset[1], 0.0, E), lead=0)
    lic(s, opacity=lambda t: 0.26 * k_st(t), gain=3.2, cell=0.032)
    s.add(dust_layer(hero_dust(T.cut_map, T.cut_ch3), opacity=k_st))

    # ── "color the plane": a scan line paints the divergence ──
    D = sample_grid(hero_div, (0, 0), FULL, res=RES)
    k_map = keys((s.start, 0.85), (T.agrees - 0.2, 0.85), (T.agrees + 0.8, 0.45, E), (reset[0], 0.45),
                 (reset[1], 0.0, E), lead=0)
    s.add(FieldLayer(scan(D, T.color_plane), cmap="diverging", vmin=-2.2, vmax=2.2, extent=FULL,
                     colors=(C.sink, C.bg, C.div), animated=True, z=-20, opacity=k_map))
    scan_line(m, T.color_plane)
    tag_p = sign_tag(HERO_SRC[0][0], "+", C.div)
    tag_m = sign_tag(HERO_SRC[1][0], "-", C.sink)
    m.play(FadeIn(tag_p, scale=0.5), at=T.sources, dur=0.6, ease="out_back")
    m.play(FadeIn(tag_m, scale=0.5), at=T.sinks, dur=0.6, ease="out_back")
    m.play(FadeOut(tag_p), FadeOut(tag_m), at=T.agrees - 0.3, dur=0.6)

    # ── "the dust agrees": a cluster spreads over the warm spot, a ring closes in over the cool one ──
    k_ = np.arange(140) + 0.5
    disc = np.stack([A[0] + 0.3 * np.sqrt(k_ / 140) * np.cos(k_ * 2.39996), A[1] + 0.3 * np.sqrt(k_ / 140) * np.sin(k_ * 2.39996)], 1)
    w1 = (T.spreads_warm - 0.4, reset[1])
    at1 = advect_table(hero, disc, w1[0], w1[1], scale=RATE)
    s.add(PointsLayer(at1, color=C.dust, size=5.0, glow=0.0, z=3,
                      opacity=keys((s.start, 0.0), (w1[0], 0.0), (w1[0] + 0.5, 1.0), (reset[0], 1.0), (reset[1], 0.0),
                                   lead=0)))
    th = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    ring = np.stack([SINK[0] + 1.4 * np.cos(th), SINK[1] + 1.4 * np.sin(th)], 1)
    w2 = (T.crowds - 0.4, reset[1])
    at2 = advect_table(hero, ring, w2[0], w2[1], scale=RATE)
    s.add(PointsLayer(at2, color=C.dust, size=5.0, glow=0.0, z=3,
                      opacity=keys((s.start, 0.0), (w2[0], 0.0), (w2[0] + 0.5, 1.0), (reset[0], 1.0), (reset[1], 0.0),
                                   lead=0)))

    # ── one more flow: the lamp, on black ──
    k_l = keys((s.start, 0.0), (T.matters - 0.2, 0.0), (T.matters + 0.01, 1.0), (T.circle - 0.2, 1.0),
               (T.circle + 0.8, 0.3, E), (T.hold - 0.3, 0.3), (T.hold + 0.5, 1.0, E), lead=0)
    ml = s.manim(z=2, opacity=k_l)
    arrows = field_arrows(lamp, (-4.9, -4.2, 6.9, 3.9), step=0.6, scale=0.6, width=2.0, origin=tuple(LC))
    order = sorted(arrows, key=lambda a: np.linalg.norm(a.get_center()[:2] - LC))
    ml.play(LaggedStart(*[GrowArrow(a) for a in order], lag_ratio=0.006), at=T.matters, dur=2.6)
    dot = Dot([*LC, 0], radius=0.08, color=C.dust)
    ml.play(FadeIn(dot, scale=0.3), at=T.lamp, dur=0.5)

    # "must be positive. Right?"
    q = tex(r"\nabla\cdot", r"\mathbf{F}", ">", "0", size=60, colors={0: C.div})
    qm = tex("?", size=60, color=C.boundary)
    VGroup(q, qm).arrange(RIGHT, buff=0.25).move_to([4.7, 3.25, 0])
    back = BackgroundRectangle(VGroup(q, qm), color=C.bg, fill_opacity=1.0, buff=0.2)
    m.play(FadeIn(back), FadeIn(q, shift=0.1 * DOWN), at=T.must + 0.3, dur=0.8)
    m.play(FadeIn(qm, scale=0.5), at=T.right_q, dur=0.5, ease="out_back")

    # "the map stays dark… except the single point": the scan runs again; only the centre lights
    # (the map of the lamp is black everywhere; only the centre lights, crisply, as the scan line crosses it)
    ts = np.linspace(T.dark, T.dark + 2.0, 400)
    t_pass = float(ts[np.argmax(-7.6 + 15.2 * np.array([ramp(t, T.dark, T.dark + 2.0) for t in ts]) >= LC[0])])
    hot = Dot([*LC, 0], radius=0.17, color=C.div)
    m.add(hot, at=t_pass)
    m.play(FadeOut(hot), at=T.hold - 0.3, dur=0.5)
    top = dot.copy()                               # keep the white lamp dot above the orange disc
    m.add(top, at=t_pass)
    m.play(FadeOut(top), at=T.hold - 0.3, dur=0.5)
    scan_line(m, T.dark, dur=2.0)
    eq0 = tex(r"\nabla\cdot", r"\mathbf{F}", "=", "0", size=60, colors={0: C.div}).move_to(q, aligned_edge=LEFT)
    m.play(ReplacementTransform(q[2], eq0[2]), FadeOut(qm), ReplacementTransform(q[3], eq0[3]),
           at=T.dark + 1.2, dur=0.8)
    ring_pt = Circle(radius=0.28, color=C.div, stroke_width=C.stroke).move_to([*LC, 0])
    m.play(Create(ring_pt), at=T.except_pt, dur=0.6)
    m.play(FadeOut(ring_pt), at=T.circle - 0.4, dur=0.5)

    # ── circles r and 2r: the edge doubles, the arrows halve ──
    c1 = Circle(radius=R1, color=C.boundary, stroke_width=C.stroke).move_to([*LC, 0])
    c2 = Circle(radius=R2, color=C.boundary, stroke_width=C.stroke).move_to([*LC, 0])
    ang = np.radians(-45)
    u = np.array([np.cos(ang), np.sin(ang)])
    rad1 = VGroup(Line([*LC, 0], [*(LC + R1 * u), 0], color=C.muted, stroke_width=C.thin),
                  tex("r", size=40, color=C.muted).move_to([*(LC + 0.55 * R1 * u + np.array([0.2, 0.2])), 0]))
    ang2 = np.radians(-135)
    u2 = np.array([np.cos(ang2), np.sin(ang2)])
    rad2 = VGroup(Line([*LC, 0], [*(LC + R2 * u2), 0], color=C.muted, stroke_width=C.thin),
                  tex("2r", size=40, color=C.muted).move_to([*(LC + 0.7 * R2 * u2 + np.array([-0.25, 0.25])), 0]))
    m.play(Create(c1), FadeIn(rad1), at=T.circle, dur=1.0, ease=E)
    m.play(Create(c2), FadeIn(rad2), at=T.twice, dur=1.2, ease=E)
    m.play(c2.animate.set_stroke(width=C.stroke + 3), at=T.edge_long, dur=0.5)
    m.play(c2.animate.set_stroke(width=C.stroke), at=T.edge_long + 1.0, dur=0.5)

    def rays(R):
        g = VGroup()
        for a in np.arange(8) * np.pi / 4 + np.pi / 8:
            d = np.array([np.cos(a), np.sin(a)])
            g.add(arrow(LC + R * d, LC + R * d + 1.2 * d / R, C.field, width=C.stroke + 0.5, tip=0.16))
        return g
    ry1, ry2 = rays(R1), rays(R2)
    m.play(LaggedStart(*[GrowArrow(a) for a in ry1], lag_ratio=0.06), at=T.half - 1.2, dur=0.9)
    m.play(LaggedStart(*[GrowArrow(a) for a in ry2], lag_ratio=0.06), at=T.half, dur=0.9)
    cancel = tex(r"2", r"\times", r"\tfrac{1}{2}", "=", "1", size=56, colors={0: C.boundary, 2: C.field})
    cancel.move_to([5.4, 1.4, 0])
    m.play(FadeIn(cancel[0], shift=0.1 * LEFT), at=T.edge_long + 0.4, dur=0.5)
    m.play(FadeIn(cancel[1:3], shift=0.1 * LEFT), at=T.half + 0.4, dur=0.5)
    m.play(FadeIn(cancel[3:], shift=0.1 * LEFT), at=T.cancel + 0.3, dur=0.6)
    flux1 = tex(r"2\pi", size=46, color=C.boundary).move_to([*(LC + np.array([0.0, -R1 + 0.38])), 0])
    flux2 = tex(r"2\pi", size=46, color=C.boundary).move_to([*(LC + np.array([0.0, -R2 + 0.38])), 0])
    phi = tex(r"\text{flux}", "=", r"2\pi", size=50, colors={2: C.boundary}).move_to([5.4, 0.4, 0])
    m.play(FadeIn(flux1, scale=0.6), FadeIn(flux2, scale=0.6), FadeIn(phi, shift=0.1 * UP), at=T.every_circle,
           dur=0.8, ease="out_back")
    m.play(hot.animate.scale(1.8), at=T.one_point, dur=0.5, ease=E)
    m.play(hot.animate.scale(1 / 1.8), at=T.one_point + 0.6, dur=0.5, ease=E)

    # ── "hold on to that": the lamp shrinks into a tile, parked top right; the del-dot F badge drops ──
    extras = VGroup(c1, c2, rad1, rad2, ry1, ry2, cancel, flux1, flux2, phi, back, q[0:2], eq0[2:])
    m.play(FadeOut(extras), at=T.hold - 0.3, dur=0.6)
    tile_c = np.array([6.15, 3.2])
    k_t = 0.11
    ml.play(VGroup(arrows, dot).animate.scale(k_t, about_point=[*LC, 0]).shift([*(tile_c - LC), 0]),
            at=T.hold + 0.4, dur=1.3, ease=E)
    tile = Rectangle(width=1.35, height=1.0, stroke_color=C.frame, stroke_width=C.thin * 0.8).move_to([*tile_c, 0])
    m.play(Create(tile), at=T.hold + 1.5, dur=0.5)
    b = badge(1, BADGES[1])
    m.play(FadeIn(b, shift=0.6 * DOWN), at=T.comes_back, dur=0.6, ease="out_back")
