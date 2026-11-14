"""Ch2 · is stuff leaving? The source panel grows out of the rail to fill the stage. A disc of dye drops in and is
carried by the exact flow (matrix exponential); a ghost outline keeps its start, and a readout A/A0 ticks from
1.00 to 2.72 (e^{2t} at t = 1/2). The whirl: the disc swings round the centre, the readout never moves. The saddle:
the disc is pulled sideways and squeezed; it freezes for the guess (readout "?"), then thins into a long ellipse
while the readout holds 1.00. Then the definition: del-dot F = (1/A) dA/dt, and three small drops play +, - and 0."""
from aion import *

from beats import T
from shots import (BADGES, CAST, CAST_NAMES, RAIL, RAIL_S, cast_arrows, cast_layer, cast_panel, cast_points, dim,
                   dye_poly, ease, flow_linear, panel, ramp, stage, tex)

E = "easy_ease"
SC_C = np.array([0.75, 0.1])                     # the stage panel (world)
W = 7.0
K = W / 4.4                                      # world units per field unit (field half-size 2.2)
RO = np.array([5.5, 0.3])                       # readout


def circle_pts(c, r, n=200):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)], 1)


def to_world(p, c=SC_C, k=K):
    return np.asarray(c) + k * np.asarray(p)


@scene(T.cut_ch2, T.cut_flux)
def s04_blob(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:1])

    # which cast member is on stage, and when
    acts = [("source", T.first_q, T.in_whirl), ("whirl", T.in_whirl, T.now_saddle),
            ("saddle", T.now_saddle, T.measures)]
    grow = (T.first_q + 0.2, T.first_q + 1.7)    # the source panel grows out of the rail
    leave = (T.measures - 0.5, T.measures + 0.4)

    # active-member highlight on the rail
    hl = Rectangle(width=RAIL_S + 0.12, height=RAIL_S + 0.12, stroke_color=C.boundary, stroke_width=C.stroke)
    hl.move_to([*RAIL[0], 0])
    m.play(Create(hl), at=T.first_q, dur=0.6)
    m.play(hl.animate.move_to([*RAIL[1], 0]), at=T.in_whirl, dur=0.7, ease=E)
    m.play(hl.animate.move_to([*RAIL[2], 0]), at=T.now_saddle, dur=0.7, ease=E)
    m.play(FadeOut(hl), at=leave[0], dur=0.6)

    # ── the stage panel: grows from the rail, then holds; members swap inside it ──
    def growing(t):
        u = ease(t, *grow)
        c = np.array(RAIL[0]) + (SC_C - np.array(RAIL[0])) * u
        return cast_panel("source", c, RAIL_S + (W - RAIL_S) * u, width=1.2 + 0.8 * u)
    h = m.redraw(growing, during=grow)
    m.remove(h, at=grow[1])
    frame = panel(*SC_C, W, W)
    frame.set_fill(opacity=0)
    m.add(frame, at=grow[1])
    m.play(FadeOut(frame), at=leave[0], dur=0.8)
    for i, (nm, a, b) in enumerate(acts):
        arr = cast_arrows(nm, SC_C, W, width=2.0)
        if i == 0:
            m.add(arr, at=grow[1])
        else:
            m.play(FadeIn(arr, lag_ratio=0.01), at=a + 0.2, dur=0.8)
        m.play(FadeOut(arr), at=(b - 0.5 if i < 2 else leave[0]), dur=0.6)
        # grains of the member on stage (dimmer than the dye)
        u = (lambda t: ease(t, *grow)) if i == 0 else (lambda t: 1.0)
        cen = (lambda t, u=u: tuple(np.array(RAIL[0]) + (SC_C - np.array(RAIL[0])) * u(t)))
        scl = (lambda t, u=u: (RAIL_S + (W - RAIL_S) * u(t)) / 4.4)
        k_in = (grow[0], grow[0] + 0.01) if i == 0 else (a + 0.2, a + 1.0)
        k_out = (b - 0.5, b + 0.1) if i < 2 else leave
        k = keys((s.start, 0.0), (k_in[0], 0.0), (k_in[1], 0.4, E), (k_out[0], 0.4), (k_out[1], 0.0, E), lead=0)
        s.add(cast_layer(cast_points(nm, n=600, seed=5), cen, scl, opacity=k, z=3, size=2.4))

    # ── the dye: one disc per member, carried exactly; tau = flow time ──
    r0 = 0.5
    p_src = circle_pts((0.0, 0.0), r0)
    p_whl = circle_pts((1.0, 0.3), 0.45)
    p_sad = circle_pts((0.0, 0.0), r0)
    tau_src = lambda t: 0.5 * ramp(t, T.in_source + 0.8, T.tripled + 0.4)
    tau_whl = lambda t: 2.2 * ramp(t, T.in_whirl + 0.9, T.same + 1.5)
    tau_sad = lambda t: 0.35 * ramp(t, T.pulled - 0.2, T.guess - 0.3) + 0.8 * ramp(t, T.neither + 0.1, T.ellipse + 1.6)

    def drop(t):
        g = VGroup()
        for (nm, a, b), p0, tau in zip(acts, (p_src, p_whl, p_sad), (tau_src, tau_whl, tau_sad)):
            k_in = (T.dye, T.dye + 0.6) if nm == "source" else (a + 0.6, a + 1.2)
            k_out = (b - 0.6, b - 0.1) if nm != "saddle" else leave
            k = ease(t, *k_in) * (1 - ramp(t, *k_out))
            if k <= 0.01:
                continue
            pts = to_world(flow_linear(CAST[nm], p0, tau(t)))
            if nm == "source" and t < k_in[1]:          # the drop lands: a quick scale-in about its centre
                pts = SC_C + (pts - SC_C) * (0.3 + 0.7 * ease(t, *k_in))
            ghost = DashedVMobject(Polygon(*[[*q, 0] for q in to_world(p0)], color=C.muted, stroke_width=C.thin),
                                   num_dashes=40)
            ka = ramp(t, T.area, T.area + 0.6) if nm == "source" else 1.0
            g.add(dim(ghost, k * ka * 0.8))
            g.add(dye_poly(pts, C.div, opacity=0.16 * k).set_stroke(opacity=k, width=C.stroke))
        return g
    m.redraw(drop, during=(T.dye, leave[1] + 0.05))

    # ── the readout: A / A0 ──
    def area_ratio(t):
        if t < T.in_whirl - 0.3:
            return float(np.exp(2 * tau_src(t)))
        return 1.0                                    # whirl and saddle: exactly 1 (det exp(At) = e^{t tr A} = 1)

    lab = tex(r"A", "/", r"A_0", size=46, colors={0: C.div}).move_to([RO[0], RO[1] + 0.75, 0])
    ro_in = (T.area, T.area + 0.6)
    pulse = (T.stays_put - 0.1, T.stays_put + 1.1)

    def readout(t):
        k = ease(t, *ro_in) * (1 - ramp(t, *leave))
        if T.guess - 0.2 < t < T.neither + 0.1:
            val = tex("?", size=72, color=C.boundary)
        else:
            val = DecimalNumber(area_ratio(t), num_decimal_places=2, font_size=72, color=C.text)
        bump = 1 + 0.18 * np.sin(np.pi * ramp(t, *pulse)) if pulse[0] < t < pulse[1] else 1.0
        val.move_to([RO[0], RO[1] - 0.15, 0]).scale(bump)
        if bump > 1.001:
            val.set_color(C.boundary)
        return VGroup(lab.copy(), Line([RO[0] - 0.9, RO[1] + 0.32, 0], [RO[0] + 0.9, RO[1] + 0.32, 0],
                                       color=C.frame, stroke_width=C.thin), val).set_opacity(k)
    m.redraw(readout, during=(ro_in[0], leave[1] + 0.05))

    # ── the definition, and three drops: grows (+), shrinks (-), only rearranged (0) ──
    eq = tex(r"\nabla\cdot", r"\mathbf{F}", "=", r"\frac{1}{A}", r"\frac{dA}{dt}", size=64, colors={0: C.div})
    eq.move_to([0.75, 2.6, 0])
    m.play(FadeIn(eq[0:2], shift=0.15 * DOWN), at=T.measures + 0.5, dur=0.8)
    m.play(FadeIn(eq[2:], shift=0.15 * LEFT, lag_ratio=0.25), at=T.swelling, dur=1.2)

    xs = (-1.7, 0.75, 3.2)
    y0 = -0.35
    trio = [(np.eye(2) * 0.5, C.div, "+", T.positive), (-np.eye(2) * 0.5, C.sink, "-", T.negative),
            (CAST["saddle"] * 0.8, C.text, "0", T.zero)]
    out = (T.cut_flux - 0.9, T.cut_flux - 0.2)

    def drops(t):
        g = VGroup()
        for x, (A, col, _, at) in zip(xs, trio):
            k = ease(t, T.measures + 1.2 + 0.25 * xs.index(x), T.measures + 1.9 + 0.25 * xs.index(x)) * (1 - ramp(t, *out))
            if k <= 0.01:
                continue
            pts = flow_linear(A, circle_pts((0, 0), 0.55), ramp(t, at, at + 1.6)) + np.array([x, y0])
            g.add(dye_poly(pts, col, opacity=0.2 * k).set_stroke(opacity=k, width=C.stroke))
        return g
    m.redraw(drops, during=(T.measures + 1.2, out[1] + 0.05))
    signs = VGroup()
    for x, (_, col, sym, at) in zip(xs, trio):
        sg = tex(sym, size=64, color=col).move_to([x, -2.3, 0])
        m.play(FadeIn(sg, scale=0.5), at=at, dur=0.5, ease="out_back")
        signs.add(sg)
    m.play(FadeOut(signs), FadeOut(eq), at=out[0], dur=0.7)
