"""Intro · the preview. The stream from the hook carries on. "A question you can ask any single point": a probe dot,
then the two questions as symbols (outward orange arrows: del-dot F = ?; a green turn: del-cross F = ?). Then four
match-cut shots, each landing on its words, none explained yet: the divergence map paints in under the flow ("a map
of where the flow is born"), the curl map and a paddle wheel turning in the vortex ("every hidden spin"), a river of
straight arrows that still turns a wheel ("perfectly straight"), a cube of little cubes with flux leaving it ("add up
all those tiny answers") beside a wire loop whose soap film bulges ("two of the biggest theorems"). Then the map:
one arrow on a page, and Maxwell's four equations, ghosted, held through the pause (paid off in Ch5)."""
from aion import *

from beats import T
from shots import (arrow, dim, ease, field_arrows, hero_curl, hero_div, hero_eyes, lic, live,
                   maxwell, ortho, paddle, ramp, sample_grid, spin_glyph, tex)
from sims import RATE, dust_layer, hero_dust

A, V = hero_eyes()
E = "easy_ease"
PROBE = np.array([0.4, -0.5])
FULL = (14.4, 8.2)


def cube_shot(t, az, k_arrows, center=(0.0, 0.0), scale=1.05, el=np.radians(24)):
    """A cube cut into 3 x 3 x 3 little cubes (visible faces only) with flux arrows leaving every outer face cell."""
    proj = ortho(az, el, scale=scale, center=center)
    g = VGroup()
    ticks = np.linspace(-1, 1, 4)
    for n in np.vstack([np.eye(3), -np.eye(3)]):
        if proj.depth(n) <= 0.02:
            continue
        u, v = [e for e in np.eye(3) if abs(e @ n) < 0.5]
        for a in ticks:
            edge = abs(a) > 0.99
            col, w = (C.boundary, C.thin + 1.2) if edge else (C.muted, C.thin * 0.7)
            g.add(Line(proj(n + a * u - v), proj(n + a * u + v), color=col, stroke_width=w))
            g.add(Line(proj(n + a * v - u), proj(n + a * v + u), color=col, stroke_width=w))
    if k_arrows > 0.01:
        cells = (-2 / 3, 0.0, 2 / 3)
        i = 0
        for n in np.vstack([np.eye(3), -np.eye(3)]):
            if proj.depth(n) <= 0.02:
                continue
            u, v = [e for e in np.eye(3) if abs(e @ n) < 0.5]
            for a in cells:
                for b in cells:
                    k = np.clip(k_arrows * 1.6 - 0.04 * i, 0, 1)
                    i += 1
                    if k <= 0.01:
                        continue
                    p = n + a * u + b * v
                    g.add(arrow(proj(p), proj(p + 0.55 * k * n), C.div, width=2.4, tip=0.11))
    return g


def film_shot(t, h, center=(3.3, -0.35), R=1.7, az=np.radians(-28), el=np.radians(22), k=1.0):
    """A wire loop (radius R) and the soap film across it: z = h (1 - r^2 / R^2), drawn as rings and meridians."""
    proj = ortho(az, el, scale=1.0, center=center)
    g = VGroup()
    th = np.linspace(0, 2 * np.pi, 97)
    for rr in (0.25, 0.5, 0.75):
        r = rr * R
        pts = [proj([r * np.cos(a), r * np.sin(a), h * (1 - rr * rr)]) for a in th]
        g.add(VMobject(stroke_color=C.curl, stroke_width=C.thin * 0.8, stroke_opacity=0.6 * k)
              .set_points_as_corners(pts))
    rs = np.linspace(0, 1, 25)
    for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):
        pts = [proj([r * R * np.cos(a), r * R * np.sin(a), h * (1 - r * r)]) for r in rs]
        g.add(VMobject(stroke_color=C.curl, stroke_width=C.thin * 0.8, stroke_opacity=0.6 * k)
              .set_points_as_corners(pts))
    wire = [proj([R * np.cos(a), R * np.sin(a), 0.0]) for a in th]
    g.add(VMobject(stroke_color=C.boundary, stroke_width=C.stroke + 1, stroke_opacity=k).set_points_as_corners(wire))
    return g


@scene(T.cut_preview, T.cut_ch1)
def s01_preview(s):
    s.solid(C.bg, z=-200)

    # ── the stream carries on; it steps back for the maps, then leaves for the montage ──
    k_stream = keys((s.start, 1.0), (T.map - 0.3, 1.0), (T.map + 0.9, 0.55, E), (T.straight - 0.5, 0.55),
                    (T.straight + 0.3, 0.0, E), lead=0)
    lic(s, opacity=lambda t: 0.32 * k_stream(t), gain=3.2, cell=0.032)
    dust = hero_dust(T.start, T.cut_ch1)
    s.add(dust_layer(dust, opacity=k_stream))

    # ── the two maps (painted in on "map", crossfaded on "spin") ──
    k_div = keys((s.start, 0.0), (T.map - 0.2, 0.0), (T.map + 1.4, 0.8, E), (T.spin - 0.4, 0.8), (T.spin + 0.8, 0.0, E),
                 lead=0)
    k_curl = keys((s.start, 0.0), (T.spin - 0.4, 0.0), (T.spin + 0.8, 0.8, E), (T.straight - 0.5, 0.8),
                  (T.straight + 0.3, 0.0, E), lead=0)
    s.add(FieldLayer(lambda t: sample_grid(hero_div, (0, 0), FULL), cmap="diverging", vmin=-2.2, vmax=2.2,
                     extent=FULL, colors=(C.sink, C.bg, C.div), animated=False, z=-20, opacity=k_div))
    s.add(FieldLayer(lambda t: sample_grid(hero_curl, (0, 0), FULL), cmap="diverging", vmin=-2.2, vmax=2.2,
                     extent=FULL, colors=(C.cw, C.bg, C.curl), animated=False, z=-20, opacity=k_curl))

    m = s.manim(z=4)

    # ── "a question you can ask about any single point": a probe, then the two questions ──
    probe = VGroup(Dot([*PROBE, 0], radius=0.07, color=C.dust),
                   Circle(radius=0.22, color=C.dust, stroke_width=C.thin).move_to([*PROBE, 0]))
    m.play(FadeIn(probe, scale=0.4), at=T.question, dur=0.6, ease="out_back")
    out = VGroup(*[arrow(PROBE + 0.32 * d, PROBE + 0.8 * d, C.div, width=3.2, tip=0.14)
                   for d in (np.array([np.cos(a), np.sin(a)]) for a in np.arange(4) * PI / 2 + PI / 4)])
    q_div = tex(r"\nabla\cdot", r"\mathbf{F}", "=", "?", size=54, colors={0: C.div}).next_to(probe, LEFT, buff=1.0)
    m.play(LaggedStart(*[GrowArrow(a) for a in out], lag_ratio=0.12), FadeIn(q_div, shift=0.15 * RIGHT),
           at=T.leaving, dur=0.9)
    turn = spin_glyph(PROBE, 0.55, +1, C.curl)
    q_curl = tex(r"\nabla\times", r"\mathbf{F}", "=", "?", size=54, colors={0: C.curl}).next_to(probe, RIGHT, buff=1.0)
    m.play(Create(turn), FadeIn(q_curl, shift=0.15 * LEFT), out.animate.set_opacity(0.35), at=T.turning, dur=0.9)
    m.play(FadeOut(VGroup(probe, out, turn, q_div, q_curl)), at=T.map - 0.4, dur=0.7)

    # ── "every hidden spin": a paddle wheel drops into the vortex and turns at curl / 2 ──
    w_in = (T.spin - 0.1, T.spin + 0.6)
    omega = 0.5 * float(hero_curl(*V)) * RATE

    def wheel_v(t):
        k = ease(t, *w_in) * (1 - ramp(t, T.straight - 0.5, T.straight + 0.1))
        return dim(VGroup(paddle(V, omega * (t - w_in[0]), radius=0.55 * max(k, 0.02), color=C.dust, width=3),
                          spin_glyph(V, 0.8 * max(k, 0.02), +1, C.curl)), k)
    live(m, wheel_v, (w_in[0], T.straight + 0.15))

    # ── "perfectly straight": a river; straight arrows, and still the wheel turns (clockwise) ──
    riv = field_arrows(lambda x, y: (y + 4.6, 0.0 * x), (-7.4, -4.2, 7.4, 4.2), step=0.62, scale=0.16, width=2.0)
    k_r = (T.straight - 0.2, T.straight + 0.5, T.add_up - 1.3, T.add_up - 0.6)
    m.play(FadeIn(riv, lag_ratio=0.02), at=k_r[1], dur=0.8)
    m.play(FadeOut(riv), at=k_r[3] - 0.1, dur=0.6)

    def wheel_r(t):
        k = ramp(t, k_r[0] + 0.3, k_r[1] + 0.3) * (1 - ramp(t, k_r[2], k_r[3]))
        return dim(VGroup(paddle((0.0, 0.0), -0.9 * (t - k_r[0]), radius=0.6, color=C.cw, width=3.5),
                          spin_glyph((0.0, 0.0), 0.85, -1, C.cw)), k)
    live(m, wheel_r, (k_r[0], k_r[3] + 0.05))

    # ── "add up all those tiny answers": a cube of little cubes, flux leaving every face; then the soap film ──
    c_in, c_out = T.add_up - 0.15, T.arrows_page - 0.2
    slide = (T.theorems - 0.3, T.theorems + 1.1)
    az = lambda t: np.radians(-48) + 0.045 * (t - c_in)

    def cube(t):
        k = ramp(t, c_in, c_in + 0.7) * (1 - ramp(t, c_out, c_out + 0.6))
        u = ease(t, *slide)
        g = cube_shot(t, az(t), ease(t, T.add_up, T.add_up + 1.6), center=(-3.3 * u, 0.0), scale=1.15 - 0.1 * u)
        return dim(g, k) if k < 0.999 else g
    live(m, cube, (c_in, c_out + 0.65))

    bulge = (T.theorems + 0.9, T.theorems + 3.0)

    def film(t):
        k = ramp(t, slide[0] + 0.3, slide[1]) * (1 - ramp(t, c_out, c_out + 0.6))
        h = 0.05 + 1.0 * ease(t, *bulge)
        return film_shot(t, h, k=k)
    live(m, film, (slide[0] + 0.3, c_out + 0.65))

    # ── "start with arrows on a page, and end with the four equations…" ──
    one = arrow((-0.9, -0.35), (0.9, 0.45), C.field, width=C.stroke + 1, tip=0.26)
    m.play(GrowArrow(one), at=T.arrows_page + 0.4, dur=0.8, ease=E)
    mx = maxwell(size=50)
    grid = VGroup(VGroup(mx[0], mx[1]).arrange(RIGHT, buff=1.6), VGroup(mx[2], mx[3]).arrange(RIGHT, buff=1.2))
    grid.arrange(DOWN, buff=0.9).move_to([0, -0.1, 0])
    m.play(FadeOut(one, scale=0.6), at=T.four_eq - 0.2, dur=0.6)
    m.play(LaggedStart(*[FadeIn(e, shift=0.15 * UP) for e in mx], lag_ratio=0.25), at=T.four_eq + 0.3, dur=1.8)
    m.play(mx.animate.set_opacity(0.38), at=T.light + 2.0, dur=1.4)
    m.play(FadeOut(mx), at=T.cut_ch1 - 1.0, dur=0.8)
