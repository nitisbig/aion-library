"""Ch1 · a field of arrows. One point, one arrow. The arrow could mean anything: it swings to a gust of wind, to the
pull of a planet, to the push away from a charge. "Do that at every point": the arrow copies outward in a ring wave
until the hero field fills the frame. "A weather map": a coastline draws under the arrows and a few towns light up
with their own arrows. "To write it down": the camera pushes into one arrow, which splits into its horizontal part
P (teal) and vertical part Q (purple); the point slides and both parts change with it ("both depend on where you
are"). Then F(x, y) = (P(x, y), Q(x, y)) builds term by term."""
from aion import *

from beats import T
from shots import arrow, dim, ease, field_arrows, grid_plane, hero, live, ramp, tex

E = "easy_ease"
P0 = np.array([1.7, 0.75])                       # the first point
SC = 0.55                                         # arrow scale for the hero field (world units per unit of F)
BOX = (-7.4, -4.2, 7.4, 4.2)
STEP = 0.6


def F(p):
    P, Q = hero(np.array(p[0]), np.array(p[1]))
    return np.array([float(P), float(Q)])


def vec(p, scale=SC, maxlen=0.9 * STEP):
    """The displayed arrow vector at p: same squash as field_arrows, so the single arrow matches the field."""
    v = F(p) * scale
    L = np.linalg.norm(v)
    return v if L < 1e-6 else v / L * maxlen * np.tanh(L / maxlen)


def coast(seed=4):
    """A smooth closed coastline (a wobbly ellipse, deterministic) for the weather-map beat."""
    th = np.linspace(0, 2 * np.pi, 240, endpoint=False)
    rng = np.random.default_rng(seed)
    r = 1.0 + sum(rng.uniform(-0.08, 0.08) * np.cos(k * th + rng.uniform(0, 6.3)) for k in range(2, 9))
    pts = np.stack([-0.4 + 5.6 * r * np.cos(th), -0.3 + 2.9 * r * np.sin(th)], 1)
    return VMobject(stroke_color=C.muted, stroke_width=C.thin + 0.5).set_points_smoothly(
        [[x, y, 0] for x, y in np.vstack([pts, pts[:1]])])


@scene(T.cut_ch1, T.cut_flow)
def s02_arrows(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=2)
    # the field lives on its own layer so its dimming is one track (weather map, zoom, equation)
    k_field = keys((s.start, 1.0), (T.weather - 0.2, 1.0), (T.weather + 0.6, 0.3, E), (T.write, 0.3),
                   (T.write + 1.0, 0.18, E), (T.F_eq + 0.6, 0.18), (T.F_eq + 1.6, 0.55, E), lead=0)
    mf = s.manim(z=1, opacity=k_field)
    grid = grid_plane()
    m.play(Create(grid, lag_ratio=0.01), at=s.start + 0.6, dur=1.2, ease=E)

    # ── "Pick a point in the plane, and attach an arrow to it" ──
    dot = Dot([*P0, 0], radius=0.07, color=C.dust)
    m.play(FadeIn(dot, scale=0.3), at=T.point, dur=0.5, ease="out_back")
    v0 = vec(P0)
    # "could mean anything": the same arrow swings to a gust, a planet's pull, a charge's push, then back
    planet = Circle(radius=0.32, color=C.muted, stroke_width=C.thin).move_to([P0[0] + 0.2, P0[1] - 2.0, 0])
    charge = VGroup(Circle(radius=0.25, color=C.efield, stroke_width=C.thin),
                    tex("+", size=34, color=C.efield)).move_to([P0[0] - 1.3, P0[1] - 0.8, 0])
    away = (P0 - np.array(charge.get_center()[:2])) / np.linalg.norm(P0 - np.array(charge.get_center()[:2]))
    states = [(T.attach, 2.4 * v0), (T.wind, np.array([0.95, 0.12])), (T.gravity, np.array([0.08, -0.75])),
              (T.charge + 0.3, 0.7 * away), (T.every_point - 0.5, v0)]
    vt = keys((s.start, 2.4 * v0), *[(t, v, E) for t, v in states], dur=0.7)
    grow = (T.attach - 0.15, T.attach + 0.55)

    def one(t):
        k = ease(t, *grow)
        v = np.asarray(vt(t), float) * max(k, 0.02)
        return arrow(P0, P0 + v, C.field, width=C.stroke, tip=0.2)
    h_one = live(m, one, (grow[0], T.every_point + 0.4))
    m.play(FadeIn(planet, scale=0.6), at=T.gravity - 0.1, dur=0.5)
    m.play(FadeOut(planet), FadeIn(charge, scale=0.6), at=T.charge + 0.2, dur=0.5)
    m.play(FadeOut(charge), at=T.every_point - 0.6, dur=0.5)

    # ── "Do that at every point": a ring wave of arrows from the first one ──
    cells = [(x, y) for x in np.arange(BOX[0] + STEP / 2, BOX[2], STEP) for y in np.arange(BOX[1] + STEP / 2, BOX[3], STEP)]
    cells.sort(key=lambda c: np.hypot(c[0] - P0[0], c[1] - P0[1]))
    wave0 = T.every_point + 0.3
    d_max = np.hypot(c[0] - P0[0], c[1] - P0[1]) if (c := cells[-1]) else 1.0
    span = 2.4                                    # seconds for the wave to reach the farthest corner

    def field_wave(t, k_all=1.0):
        g = VGroup()
        for (x, y) in cells:
            d = np.hypot(x - P0[0], y - P0[1])
            k = ease(t, wave0 + span * d / d_max, wave0 + span * d / d_max + 0.45)
            if k <= 0.01:
                continue
            v = vec((x, y)) * k
            L = np.linalg.norm(v)
            if L < 1e-3:
                continue
            p = np.array([x, y]) - v / 2
            op = (0.45 + 0.55 * min(L / (0.9 * STEP), 1.0)) * k_all
            g.add(arrow(p, p + v, C.field, width=2.2, tip=0.12, opacity=op))
        return g
    live(mf, field_wave, (wave0, wave0 + span + 0.5))
    m.remove(dot, at=wave0 + 0.2)
    m.remove(h_one[-1], at=wave0 + 0.3)
    full = field_wave(wave0 + span + 1.0)
    mf.add(full, at=wave0 + span + 0.5)

    # ── "A weather map of the wind": a coastline under the arrows, towns light up ──
    land = coast()
    m.play(Create(land), at=T.weather, dur=1.6, ease=E)
    towns = [(-3.9, 1.2), (-1.6, -1.6), (0.9, 1.5), (2.6, -0.9), (-0.4, 0.1), (3.9, 0.9)]
    town_g = VGroup()
    for p in towns:
        v = vec(p)
        town_g.add(VGroup(Dot([*p, 0], radius=0.06, color=C.dust), arrow(p, np.array(p) + v * 1.5, C.field,
                                                                          width=C.stroke, tip=0.16)))
    m.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in town_g], lag_ratio=0.25), at=T.town, dur=2.2)

    # ── "To write it down": push into one arrow; it splits into P (teal) and Q (purple) ──
    m.play(FadeOut(land), FadeOut(town_g), at=T.write - 0.4, dur=0.8)
    BIG = 3.0
    zoom_c = P0 + vec(P0) * BIG * 0.5
    s.camera.frame(T.write, center=tuple(zoom_c), zoom=1.9, dur=1.6)
    path = keys((s.start, P0), (T.depend - 0.1, P0), (T.depend + 0.9, P0 + np.array([-0.55, 0.35]), E),
                (T.F_eq - 0.6, P0 + np.array([-0.55, 0.35])), (T.F_eq + 0.3, P0, E), lead=0)
    kp = (T.call_P - 0.2, T.call_P + 0.5)
    kq = (T.call_Q - 0.2, T.call_Q + 0.5)
    kd = (T.two_parts - 0.1, T.two_parts + 0.5)
    k_out = (T.F_eq + 0.6, T.F_eq + 1.4)

    def parts(t):
        p = np.asarray(path(t), float)
        v = vec(p) * BIG * ease(t, T.write - 0.2, T.write + 0.8)
        kk = 1 - ramp(t, *k_out)
        g = VGroup(Dot([*p, 0], radius=0.05, color=C.dust).set_opacity(kk),
                   arrow(p, p + v, C.field, width=C.stroke, tip=0.16, opacity=kk))
        a_d = ramp(t, *kd) * kk
        if a_d > 0.01:                            # dashed guides of the two parts
            g.add(DashedLine([*p, 0], [p[0] + v[0], p[1], 0], color=C.muted, stroke_width=1.6, dash_length=0.06)
                  .set_stroke(opacity=0.8 * a_d * (1 - ramp(t, *kp))))
            g.add(DashedLine([p[0] + v[0], p[1], 0], [*(p + v), 0], color=C.muted, stroke_width=1.6,
                             dash_length=0.06).set_stroke(opacity=0.8 * a_d * (1 - ramp(t, *kq))))
        a_p = ramp(t, *kp) * kk
        if a_p > 0.01:
            g.add(arrow(p, (p[0] + v[0], p[1]), C.xpart, width=C.stroke, tip=0.14, opacity=a_p))
            oy = -0.2 * np.sign(v[1]) if abs(v[1]) > 1e-3 else -0.2
            g.add(tex("P", size=30, color=C.xpart).move_to([p[0] + v[0] / 2, p[1] + oy, 0]).set_opacity(a_p))
        a_q = ramp(t, *kq) * kk
        if a_q > 0.01:
            g.add(arrow((p[0] + v[0], p[1]), p + v, C.ypart, width=C.stroke, tip=0.14, opacity=a_q))
            ox = 0.22 * np.sign(v[0]) if abs(v[0]) > 1e-3 else 0.22
            g.add(tex("Q", size=30, color=C.ypart).move_to([p[0] + v[0] + ox, p[1] + v[1] / 2, 0]).set_opacity(a_q))
        return g
    h_parts = live(m, parts, (T.write - 0.2, T.call_Q + 0.6), (T.depend - 0.2, T.depend + 1.0), (T.F_eq - 0.7, k_out[1] + 0.1))

    m.remove(h_parts[-1], at=k_out[1] + 0.2)

    # ── "So the field is F of x y equals P of x y, Q of x y" ──
    s.camera.frame(T.F_eq - 0.4, center=(0.0, 0.0), zoom=1.0, dur=1.6)
    eq = tex(r"\mathbf{F}(x,y)", "=", r"\big(", "P(x,y)", ",", r"\;Q(x,y)", r"\big)", size=60,
             colors={3: C.xpart, 5: C.ypart})
    back = Rectangle(width=eq.width + 0.8, height=eq.height + 0.5, stroke_color=C.frame, stroke_width=C.thin,
                     fill_color=C.bg, fill_opacity=1.0)
    VGroup(back, eq).move_to([0, 2.9, 0])
    m.play(FadeIn(back), at=T.F_eq + 0.5, dur=0.6)
    m.play(LaggedStart(FadeIn(eq[0:2]), FadeIn(eq[2]), FadeIn(eq[3], shift=0.1 * UP), FadeIn(eq[4]),
                       FadeIn(eq[5], shift=0.1 * UP), FadeIn(eq[6]), lag_ratio=0.35), at=T.F_eq + 0.8, dur=2.4)
    m.play(FadeOut(VGroup(back, eq), shift=0.2 * UP), at=T.cut_flow - 0.9, dur=0.7)
