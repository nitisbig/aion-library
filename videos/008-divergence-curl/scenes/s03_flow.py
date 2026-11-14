"""Ch1 · let the arrows carry something. The field from s02 stays. "Sprinkle dust": grains rain in and follow the
arrows while the streak texture fades in behind and the arrows step back. One grain is picked out; it carries its
own arrow, F at that grain, which is its velocity ("the dust shows the flow"), and it leaves a trail. "Some company":
three framed panels slide in and each fills, as it is named, with its field and grains moved by the exact flow:
source (spreads), whirl (turns), saddle (squeezes in, stretches out). "Keep an eye on the saddle" pulses its
frame. "It will fool you": the panels shrink and dock as the cast rail at the left edge, and an F badge drops in."""
from aion import *

from beats import T
from shots import (BADGES, CAST_NAMES, PANEL_W, PANEL_X, PANEL_Y, RAIL, RAIL_S, advect_table, arrow, badge, cast_arrows,
                   cast_layer, cast_panel, cast_points, dim, ease, grid_plane, hero, lic, live, panel, ramp, tex, words)
from sims import RATE, dust_layer, hero_dust

E = "easy_ease"
SC = 0.55                                         # same arrows as s02
BOX = (-7.4, -4.2, 7.4, 4.2)
STEP = 0.6
G0 = (-2.0, 0.0)                                  # the picked grain (sweeps toward the sink)


def vec(p, scale=SC, maxlen=0.9 * STEP):
    P, Q = hero(np.array(p[0]), np.array(p[1]))
    v = np.array([float(P), float(Q)]) * scale
    L = np.linalg.norm(v)
    return v if L < 1e-6 else v / L * maxlen * np.tanh(L / maxlen)


def hero_field():
    """The s02 field, arrow for arrow (same cells, squash and opacity)."""
    g = VGroup()
    for x in np.arange(BOX[0] + STEP / 2, BOX[2], STEP):
        for y in np.arange(BOX[1] + STEP / 2, BOX[3], STEP):
            v = vec((x, y))
            L = np.linalg.norm(v)
            if L < 1e-3:
                continue
            p = np.array([x, y]) - v / 2
            g.add(arrow(p, p + v, C.field, width=2.2, tip=0.12, opacity=0.45 + 0.55 * min(L / (0.9 * STEP), 1.0)))
    return g


@scene(T.cut_flow, T.cut_ch2)
def s03_flow(s):
    s.solid(C.bg, z=-200)
    gone = (T.company - 0.4, T.company + 0.6)     # the hero stage leaves for the cast panels

    # ── the field from s02 (0.55), lifts on "carry", steps back when the dust arrives ──
    k_field = keys((s.start, 0.55), (T.carry - 0.3, 0.55), (T.carry + 0.6, 0.85, E), (T.sprinkle, 0.85),
                   (T.sprinkle + 1.4, 0.28, E), (gone[0], 0.28), (gone[1], 0.0, E), lead=0)
    mf = s.manim(z=1, opacity=k_field)
    mf.add(hero_field(), at=s.start)
    k_grid = keys((s.start, 1.0), (gone[0], 1.0), (gone[1], 0.0, E), lead=0)
    mg = s.manim(z=0, opacity=k_grid)
    mg.add(grid_plane(), at=s.start)

    # ── "sprinkle some dust": grains rain in and ride the arrows; the streak texture comes up behind ──
    k_dust = keys((s.start, 0.0), (T.sprinkle - 0.2, 0.0), (T.sprinkle + 1.6, 1.0, E), (gone[0], 1.0),
                  (gone[1], 0.0, E), lead=0)
    lic(s, opacity=lambda t: 0.26 * k_dust(t), gain=3.2, cell=0.032)
    s.add(dust_layer(hero_dust(T.cut_flow, T.cut_ch2), opacity=k_dust))

    m = s.manim(z=4)

    # ── "F is its velocity": one grain picked out, carrying its own arrow; then its trail ──
    g_in, g_out = T.is_flow + 0.6, T.company - 0.3
    at_g = advect_table(hero, [G0], g_in, g_out, scale=RATE)
    k_g = (g_in, g_in + 0.6, g_out - 0.7, g_out)
    tr = (T.dust_shows - 0.2, g_out)

    def grain(t):
        k = ease(t, k_g[0], k_g[1]) * (1 - ramp(t, k_g[2], k_g[3]))
        p = at_g(t)[0]
        g = VGroup()
        if t > tr[0]:                             # the trail: where the grain has been
            ts = np.linspace(tr[0], t, max(2, int((t - tr[0]) * 30)))
            pts = [[*at_g(u)[0], 0] for u in ts]
            if len(pts) > 2:
                g.add(VMobject(stroke_color=C.dust, stroke_width=C.thin + 0.6, stroke_opacity=0.75 * k)
                      .set_points_smoothly(pts))
        ka = ease(t, T.velocity - 0.2, T.velocity + 0.6) * k
        if ka > 0.01:                             # its velocity: F at the grain, drawn big
            v = vec(p, scale=1.3 * SC, maxlen=1.4)
            g.add(arrow(p, p + v * ka, C.field, width=C.stroke, tip=0.2, opacity=k))
        g.add(Circle(radius=0.17, color=C.dust, stroke_width=C.thin).move_to([*p, 0]).set_stroke(opacity=0.9 * k))
        g.add(Dot([*p, 0], radius=0.065, color=C.dust).set_opacity(k))
        return g
    h_g = live(m, grain, (k_g[0], k_g[3] + 0.05))
    m.remove(h_g[-1], at=k_g[3] + 0.1)
    def flab(t):                                  # the F label rides the tip of the grain's arrow
        p = at_g(t)[0]
        k = ease(t, T.velocity + 0.2, T.velocity + 0.8) * (1 - ramp(t, T.dust_shows + 0.4, T.dust_shows + 1.0))
        v = vec(p, scale=1.3 * SC, maxlen=1.4)
        n = np.array([-v[1], v[0]]) / max(np.linalg.norm(v), 1e-6)
        return tex(r"\mathbf{F}", size=44, color=C.field).move_to([*(p + v + 0.32 * n), 0]).set_opacity(k)
    h_l = live(m, flab, (T.velocity + 0.2, T.dust_shows + 1.05))
    m.remove(h_l[-1], at=T.dust_shows + 1.1)

    # ── "some company": three panels slide in; each fills with its field as it is named ──
    dock = (T.fool - 0.1, T.fool + 1.2)
    centers = [(x, PANEL_Y) for x in PANEL_X]
    frames = VGroup(*[panel(cx, cy, PANEL_W, PANEL_W) for cx, cy in centers])
    m.play(LaggedStart(*[FadeIn(f, shift=0.35 * UP) for f in frames], lag_ratio=0.25), at=T.company + 0.2, dur=1.4,
           ease=E)
    fills = {"source": T.away, "whirl": T.around, "saddle": T.saddle_in}
    names = {"source": T.name_source, "whirl": T.whirl, "saddle": T.saddle}
    arrows, labels = VGroup(), VGroup()
    for i, nm in enumerate(CAST_NAMES):
        c = centers[i]
        a = cast_arrows(nm, c, PANEL_W)
        order = sorted(a, key=lambda ar: np.hypot(*(ar.get_center()[:2] - np.array(c))))
        m.play(LaggedStart(*[GrowArrow(ar) for ar in order], lag_ratio=0.03), at=fills[nm], dur=1.6, ease=E)
        arrows.add(a)
        lab = words(nm, size=36, color=C.muted).move_to([c[0], c[1] - PANEL_W / 2 - 0.4, 0])
        m.play(FadeIn(lab, shift=0.12 * UP), at=names[nm], dur=0.6, ease="out_back")
        labels.add(lab)
        # grains moved by the exact flow; they ride the panel when it docks
        u = lambda t, i=i: ease(t, dock[0] + 0.3 * i, dock[1] + 0.3 * i)
        cen = lambda t, c=c, i=i, u=u: (c[0] + (RAIL[i][0] - c[0]) * u(t), c[1] + (RAIL[i][1] - c[1]) * u(t))
        scl = lambda t, u=u: (PANEL_W + (RAIL_S - PANEL_W) * u(t)) / 4.4
        k_d = keys((s.start, 0.0), (fills[nm] + 0.4, 0.0), (fills[nm] + 1.6, 1.0, E), lead=0)
        s.add(cast_layer(cast_points(nm), cen, scl, opacity=lambda t, k=k_d, u=u: k(t) * (1 - 0.45 * u(t)), z=5))

    # ── "keep an eye on the saddle": its frame pulses ──
    m.play(frames[2].animate.set_stroke(C.boundary, width=C.stroke), at=T.keep_eye, dur=0.5, ease=E)
    m.play(frames[2].animate.set_stroke(C.frame, width=C.thin), at=T.keep_eye + 0.9, dur=0.6, ease=E)

    # ── "it will fool you": the panels shrink and dock as the cast rail; the F badge drops in ──
    m.play(FadeOut(labels), at=dock[0] - 0.2, dur=0.5)
    for mob in [*frames, *[ar for a in arrows for ar in a]]:
        m.remove(mob, at=dock[0])

    def docking(t):
        g = VGroup()
        for i, nm in enumerate(CAST_NAMES):
            u = ease(t, dock[0] + 0.3 * i, dock[1] + 0.3 * i)    # staggered, so the panels never cross
            c = (centers[i][0] + (RAIL[i][0] - centers[i][0]) * u, centers[i][1] + (RAIL[i][1] - centers[i][1]) * u)
            w = PANEL_W + (RAIL_S - PANEL_W) * u
            g.add(cast_panel(nm, c, w, width=1.8 - 0.6 * u))
        return g
    live(m, docking, (dock[0], dock[1] + 0.65))
    b = badge(0, BADGES[0])
    m.play(FadeIn(b, shift=0.6 * DOWN), at=T.fool + 1.35, dur=0.55, ease="out_back")
