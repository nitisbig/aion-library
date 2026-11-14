"""Ch3 · is stuff turning? The whirl grows out of the rail. A tiny paddle wheel drops in, pinned so it can only
spin; it turns counter-clockwise at curl/2 (exactly as fast as the grains go round), and two more wheels elsewhere
turn in step. The river: every arrow points right, faster on top. A wheel sits still through the guess, then turns
clockwise; the push on its top vane is longer than on its bottom one. The drain: arrows circle, but a pinned wheel
does not turn, and a floating wheel rides all the way round while staying upright (ghosts mark the path, a Ferris
wheel). Then the three cases side by side (+, -, 0), and one wheel comes forward: curl is how fast it would turn."""
from aion import *

from beats import T
from shots import (BADGES, CAST, RAIL, RAIL_S, arrow, cast_arrows, cast_layer, cast_panel, cast_points, dim, ease,
                   panel, panel_arrows, paddle, ramp, spin_glyph, stage, tex)

E = "easy_ease"
SC_C = np.array([0.75, 0.1])
W = 7.0
K = W / 4.4                                      # world units per field unit
RATE = 0.5                                       # flow time per second (matches the cast grains)
RIV_C, RIV_RATE = 2.4, 0.6                       # river (y + c, 0); its own flow rate (faster, so the wheel reads)
WR = 0.55                                        # wheel radius (world)


def world(p):
    return SC_C + K * np.asarray(p)


def spin_angle(t, t0, omega, ramp_in=1.0):
    """Angle of a wheel that starts turning at t0 with angular speed omega (rad/s), easing in over ramp_in s."""
    if t <= t0:
        return 0.0
    u = t - t0
    return omega * (u - ramp_in / 2 if u > ramp_in else u * u / (2 * ramp_in))


def river(x, y):
    return (y + RIV_C, 0.0 * x)


def drain(x, y, a=0.25):
    r2 = x * x + y * y + a * a
    return (-y / r2, x / r2)


def river_points(n=500, seed=11):
    rng = np.random.default_rng(seed)
    p0 = rng.uniform(-2.2, 2.2, (n, 2))

    def local(t):
        x = np.mod(p0[:, 0] + (p0[:, 1] + RIV_C) * RIV_RATE * t + 2.2, 4.4) - 2.2
        a = np.clip(np.minimum(2.2 - np.abs(x), 0.4) / 0.4, 0, 1)
        return np.stack([x, p0[:, 1]], 1), a.astype(np.float32)
    return local


def drain_points(n=500, seed=12):
    rng = np.random.default_rng(seed)
    r = np.sqrt(rng.uniform(0.35 ** 2, 2.6 ** 2, n))
    th = rng.uniform(0, 2 * np.pi, n)

    def local(t):
        a = th + RATE * t / (r * r + 0.0625)
        pos = np.stack([r * np.cos(a), r * np.sin(a)], 1)
        inside = (np.abs(pos[:, 0]) < 2.13) & (np.abs(pos[:, 1]) < 2.13)
        return pos, inside.astype(np.float32)
    return local


@scene(T.cut_ch3, T.cut_circ)
def s07_paddle(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:2], tile=True)

    grow = (T.second_q - 0.2, T.second_q + 1.3)
    acts = [("whirl", grow[0], T.river), ("river", T.river, T.drain - 0.6), ("drain", T.drain - 0.6, T.so_curl)]
    hl = Rectangle(width=RAIL_S + 0.12, height=RAIL_S + 0.12, stroke_color=C.boundary, stroke_width=C.stroke)
    hl.move_to([*RAIL[1], 0])
    m.play(Create(hl), at=T.second_q - 0.4, dur=0.5)
    m.play(FadeOut(hl), at=T.river - 0.4, dur=0.5)

    # ── the stage: the whirl grows from the rail; river and drain swap in ──
    def growing(t):
        u = ease(t, *grow)
        c = np.array(RAIL[1]) + (SC_C - np.array(RAIL[1])) * u
        return cast_panel("whirl", c, RAIL_S + (W - RAIL_S) * u, width=1.2 + 0.8 * u)
    h = m.redraw(growing, during=grow)
    m.remove(h, at=grow[1])
    frame = panel(*SC_C, W, W).set_fill(opacity=0)
    m.add(frame, at=grow[1])
    m.play(FadeOut(frame), at=T.so_curl - 0.5, dur=0.6)
    fields = {"whirl": cast_arrows("whirl", SC_C, W, width=2.0),
              "river": panel_arrows(river, SC_C, W, scale=0.16, width=2.0),
              "drain": panel_arrows(drain, SC_C, W, scale=0.5, width=2.0)}
    m.add(fields["whirl"], at=grow[1])
    for nm, a, b in acts:
        if nm != "whirl":
            m.play(FadeIn(fields[nm], lag_ratio=0.01), at=a + 0.3, dur=0.9)
        m.play(FadeOut(fields[nm]), at=b - 0.5, dur=0.6)
    # grains
    u = lambda t: ease(t, *grow)
    cen = lambda t: tuple(np.array(RAIL[1]) + (SC_C - np.array(RAIL[1])) * u(t))
    scl = lambda t: (RAIL_S + (W - RAIL_S) * u(t)) / 4.4
    k_w = keys((s.start, 0.0), (grow[0], 0.0), (grow[0] + 0.01, 0.35), (T.river - 0.5, 0.35), (T.river + 0.1, 0.0),
               lead=0)
    s.add(cast_layer(cast_points("whirl", n=600, seed=5), cen, scl, opacity=k_w, z=3, size=2.4))
    k_r = keys((s.start, 0.0), (T.river + 0.3, 0.0), (T.river + 1.2, 0.35), (T.drain - 1.1, 0.35), (T.drain - 0.5, 0.0),
               lead=0)
    s.add(cast_layer(river_points(), tuple(SC_C), K, opacity=k_r, z=3, size=2.4))
    k_d = keys((s.start, 0.0), (T.drain - 0.3, 0.0), (T.drain + 0.6, 0.35), (T.so_curl - 0.5, 0.35),
               (T.so_curl + 0.1, 0.0), lead=0)
    s.add(cast_layer(drain_points(), tuple(SC_C), K, opacity=k_d, z=3, size=2.4))

    # ── the whirl: one wheel drops in, pinned; it turns at curl / 2; two more turn in step ──
    om_w = 0.5 * 2.0 * RATE                     # curl = 2, flow rate RATE  ->  0.5 rad/s, same as the grains
    w_spots = [world((-0.75, 0.55)), world((1.0, -0.9)), world((0.7, 1.2))]
    t_spin = T.whirl_turns - 0.2
    w_out = (T.river - 0.6, T.river - 0.1)

    def whirl_wheels(t):
        g = VGroup()
        for i, c in enumerate(w_spots):
            t_in = T.paddle if i == 0 else T.same_rate + 0.3 * i
            k = ease(t, t_in, t_in + 0.6) * (1 - ramp(t, *w_out))
            if k <= 0.01:
                continue
            drop = 0.6 * (1 - ease(t, t_in, t_in + 0.6))
            cc = c + np.array([0, drop])
            wheel = paddle(cc, np.pi / 4 + spin_angle(t, t_spin, om_w), radius=WR, color=C.dust, width=3)
            g.add(dim(wheel, k))
            kg = ramp(t, T.whirl_turns, T.whirl_turns + 0.6) * k
            if kg > 0.01:
                g.add(dim(spin_glyph(cc, WR + 0.25, +1, C.curl), kg))
        return g
    m.redraw(whirl_wheels, during=(T.paddle, w_out[1] + 0.05))
    pin = Dot([*w_spots[0], 0], radius=0.05, color=C.boundary)
    m.play(FadeIn(pin, scale=0.3), at=T.pinned, dur=0.4)
    m.play(FadeOut(pin), at=w_out[0], dur=0.4)

    # ── the river: a wheel sits still through the guess, then turns clockwise ──
    rc = world((0.0, 0.0))
    om_r = -0.5 * 1.0 * RIV_RATE               # curl = -1
    t_r = T.it_does - 0.1
    r_in, r_out = (T.will_spin - 1.6, T.will_spin - 1.0), (T.drain - 1.1, T.drain - 0.6)

    def river_wheel(t):
        k = ease(t, *r_in) * (1 - ramp(t, *r_out))
        g = VGroup(paddle(rc, np.pi / 4 + spin_angle(t, t_r, om_r), radius=WR, color=C.dust, width=3))
        kg = ramp(t, T.it_does + 0.2, T.it_does + 0.8)
        if kg > 0.01:
            g.add(dim(spin_glyph(rc, WR + 0.25, -1, C.cw), kg))
        kp = ramp(t, T.top_pushed - 0.1, T.top_pushed + 0.5) * (1 - ramp(t, T.still_spin, T.still_spin + 0.6))
        if kp > 0.01:                          # the pushes on the top and bottom vanes
            for sgn in (+1, -1):
                y = sgn * (WR + 0.08) / K
                v = (y + RIV_C) * 0.42
                p = rc + np.array([-v / 2, sgn * (WR + 0.08)])
                g.add(arrow(p, p + np.array([v, 0]), C.field, width=C.stroke + 1, tip=0.18, opacity=kp))
        return dim(g, k)
    m.redraw(river_wheel, during=(r_in[0], r_out[1] + 0.05))
    q = tex("?", size=64, color=C.boundary).move_to([*(rc + np.array([1.1, 0.9])), 0])
    m.play(FadeIn(q, scale=0.5), at=T.will_spin + 0.6, dur=0.5, ease="out_back")
    m.play(FadeOut(q), at=T.it_does - 0.2, dur=0.4)

    # ── the drain: a pinned wheel does not turn; a floating wheel stays upright all the way round ──
    pc = world((1.55, -1.0))
    fr = 1.0                                   # float radius (field units)
    om_o = RATE / (fr * fr + 0.0625)           # its orbit speed (rad/s)
    t_f = T.float_ + 0.3
    d_out = (T.so_curl - 0.5, T.so_curl + 0.1)

    def drain_wheels(t):
        g = VGroup()
        kp = ease(t, T.pin - 0.2, T.pin + 0.4) * (1 - ramp(t, *d_out))
        if kp > 0.01:
            g.add(dim(VGroup(paddle(pc, np.pi / 4, radius=WR, color=C.dust, width=3),
                             Dot([*pc, 0], radius=0.05, color=C.boundary)), kp))
        kf = ease(t, T.float_ - 0.3, T.float_ + 0.3) * (1 - ramp(t, *d_out))
        if kf > 0.01:
            phi0 = np.radians(150)
            phi = phi0 + om_o * max(0.0, t - t_f)
            # ghosts every 40 degrees along the path already travelled (upright copies)
            for gphi in np.arange(phi0, phi - 0.3, np.radians(40)):
                gc = world((fr * np.cos(gphi), fr * np.sin(gphi)))
                g.add(dim(paddle(gc, np.pi / 4, radius=WR * 0.8, color=C.muted, width=2), 0.45 * kf))
            c = world((fr * np.cos(phi), fr * np.sin(phi)))
            g.add(dim(paddle(c, np.pi / 4, radius=WR, color=C.dust, width=3), kf))
        return g
    m.redraw(drain_wheels, during=(T.pin - 0.2, d_out[1] + 0.05))

    # ── side by side: whirl (+), river (-), drain (0) ──
    xs = (-2.75, 0.95, 4.6)
    trio = [("whirl", lambda x, y: (-y, x), 0.2, om_w, +1, C.curl, "+"),
            ("river", river, 0.13, om_r, -1, C.cw, "-"),
            ("drain", drain, 0.4, 0.0, 0, C.text, "0")]
    pw = 3.1
    tri_in, tri_out = (T.so_curl + 0.2, T.so_curl + 1.4), (T.tiny_wheel - 0.3, T.tiny_wheel + 0.4)
    boxes = VGroup()
    for x, (nm, Fn, sc, om, sg, col, sym) in zip(xs, trio):
        boxes.add(VGroup(panel(x, 0.3, pw, pw), panel_arrows(Fn, (x, 0.3), pw, scale=sc, width=1.4),
                         tex(sym, size=60, color=col).move_to([x, 0.3 - pw / 2 - 0.5, 0])))
    m.play(LaggedStart(*[FadeIn(b, shift=0.3 * UP) for b in boxes], lag_ratio=0.2), at=tri_in[0], dur=1.2, ease=E)
    m.play(FadeOut(boxes), at=tri_out[0], dur=0.6)

    def trio_wheels(t):
        g = VGroup()
        k = ramp(t, tri_in[0] + 0.4, tri_in[1]) * (1 - ramp(t, *tri_out))
        for x, (_, _, _, om, sg, col, _) in zip(xs, trio):
            c = np.array([x, 0.3])
            g.add(paddle(c, np.pi / 4 + spin_angle(t, tri_in[0], om), radius=0.45, color=C.dust, width=3))
            if sg != 0:
                g.add(spin_glyph(c, 0.68, sg, col))
        return dim(g, k)
    m.redraw(trio_wheels, during=(tri_in[0], tri_out[1] + 0.05))

    # ── "whether a tiny wheel, sitting right here, would turn. And how fast." ──
    hero_c = np.array([0.9, 0.1])

    def one(t):
        k = ease(t, T.tiny_wheel, T.tiny_wheel + 0.9)
        r = 0.45 + 0.75 * ease(t, T.tiny_wheel, T.tiny_wheel + 1.4)
        om = 0.5 + 1.1 * ease(t, T.how_fast, T.how_fast + 0.8)
        ang = np.pi / 4 + 0.5 * (t - T.tiny_wheel) + (om - 0.5) * max(0.0, t - T.how_fast) * 0.6
        g = VGroup(paddle(hero_c, ang, radius=r, color=C.dust, width=3.5),
                   spin_glyph(hero_c, r + 0.35, +1, C.curl))
        return dim(g, k)
    m.redraw(one, during=(T.tiny_wheel, T.cut_circ + 0.05))
