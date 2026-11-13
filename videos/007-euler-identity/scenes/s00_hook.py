"""Intro · the hook. The equation writes on, the −1 crosses over to give e^{iπ} + 1 = 0, the five constants pulse.
Then the wrong intuition: an exponent means repeated multiplication, e³ = e·e·e, so what is e multiplied by itself
iπ times? The chain breaks apart. "It is a picture": the unit circle draws on, one yellow point at 1."""
from aion import *

from beats import T
from shots import HERO_O, HERO_U, P, arrow, backdrop, ease, euler, glyphs, identity, live, panel, plane_grid, ramp

EQ = np.array([0.0, 0.35, 0.0])
TOP = np.array([0.0, 2.6, 0.0])                       # where the equation waits while the five panels play
PY, PW = -1.0, 2.5                                  # panel row: centre y, panel width (= height)
PX = (-5.3, -2.65, 0.0, 2.65, 5.3)                      # panel centres, in reading order: e, i, π, 1, 0
SHRINK = 0.7


def dim(g, k):
    """Scale every stroke and fill opacity in g by k (keeps translucent fills translucent)."""
    for mob in g.family_members_with_points():
        mob.set_stroke(opacity=mob.get_stroke_opacity() * k)
        mob.set_fill(opacity=mob.get_fill_opacity() * k)
    return g


def _pts(xy):
    return [[float(x), float(y), 0.0] for x, y in xy]


def g_e(c, u):
    """e: the curve e^x drawing on, a tangent riding it (slope = height)."""
    x0, x1, yb = c[0] - 1.0, c[0] + 0.95, c[1] - 0.85
    f = lambda x: yb + 0.1 * np.exp(1.5 * (x - x0))                     # noqa: E731
    a = ease(u, 0.0, 0.9)
    xs = np.linspace(x0, x0 + (x1 - x0) * max(a, 1e-3), 60)
    g = VGroup(Line([x0 - 0.05, yb, 0], [x1 + 0.05, yb, 0], color=C.faint, stroke_width=C.thin),
               VMobject(stroke_color=C.growth, stroke_width=C.stroke).set_points_smoothly(_pts(zip(xs, f(xs)))))
    if u > 0.9:
        x = x0 + 0.35 + 1.25 * (0.5 - 0.5 * np.cos(1.6 * (u - 0.9)))
        y, dy = f(x), 1.5 * (f(x) - yb)
        d = np.array([1.0, dy]) / np.hypot(1.0, dy)
        g.add(Line([x - 0.45 * d[0], y - 0.45 * d[1], 0], [x + 0.45 * d[0], y + 0.45 * d[1], 0],
                   color=C.text, stroke_width=C.thin + 0.4), Dot([x, y, 0], radius=0.05, color=C.growth))
    return g


def g_i(c, u):
    """i: a small plane, an arrow from 1 stepping round by quarter turns, a red arc for each turn."""
    o, r = np.array([c[0], c[1]]), 0.78
    box = (o[0] - 1.05, o[1] - 0.9, o[0] + 1.05, o[1] + 0.9)
    q = u / 1.1                                                       # one quarter turn every 1.1 s
    th = PI / 2 * (np.floor(q) + ease(q - np.floor(q), 0.1, 0.75))
    g = VGroup(plane_grid(o, r / 2, box=box, n=4, minor=1, opacity=0.45 * ramp(u, 0, 0.4)))
    a0 = PI / 2 * np.floor(q)
    if th - a0 > 0.02:
        g.add(Arc(radius=r, start_angle=a0, angle=th - a0, arc_center=[*o, 0], color=C.turn, stroke_width=C.stroke))
    g.add(arrow([*o, 0], [o[0] + r * np.cos(th), o[1] + r * np.sin(th), 0], C.point, tip=0.16))
    return g


def g_pi(c, u):
    """π: a circle of diameter 1 rolls along the ground; its rim unrolls into a green length π."""
    d = 0.6
    rr = d / 2
    x0, yb = c[0] - 0.95, c[1] - 0.45
    phi = 2 * PI * ease(u, 0.3, 2.3)                                  # one full turn
    cx = x0 + rr * phi
    g = VGroup(Line([x0 - 0.1, yb, 0], [x0 + PI * d + 0.1, yb, 0], color=C.faint, stroke_width=C.thin))
    if phi > 1e-3:
        g.add(Line([x0, yb, 0], [cx, yb, 0], color=C.arc, stroke_width=C.stroke + 1))
    g.add(Circle(radius=rr, color=C.text, stroke_width=C.thin + 0.6).move_to([cx, yb + rr, 0]))
    if phi < 2 * PI - 1e-3:                                           # the part of the rim not yet unrolled
        g.add(Arc(radius=rr, start_angle=-PI / 2 - phi, angle=-(2 * PI - phi), arc_center=[cx, yb + rr, 0],
                  color=C.arc, stroke_width=C.stroke + 1))
    g.add(Line([x0, yb - 0.08, 0], [x0, yb + 0.08, 0], color=C.arc, stroke_width=C.thin + 0.6))
    if u > 2.3:
        k = ramp(u, 2.3, 2.6)
        g.add(Line([x0 + PI * d, yb - 0.08, 0], [x0 + PI * d, yb + 0.08, 0], color=C.arc,
                   stroke_width=C.thin + 0.6, stroke_opacity=k))
    return g


def g_one(c, u):
    """1: the unit step along a number line, then the unit square standing on it."""
    s_ = 1.1
    x0, yb = c[0] - s_ / 2, c[1] - 0.65
    a = ease(u, 0.1, 0.8)
    b = ease(u, 0.9, 1.6)
    g = VGroup(Line([x0 - 0.35, yb, 0], [x0 + s_ + 0.35, yb, 0], color=C.faint, stroke_width=C.thin))
    for x in (x0, x0 + s_):
        g.add(Line([x, yb - 0.07, 0], [x, yb + 0.07, 0], color=C.muted, stroke_width=C.thin))
    if a > 1e-3:
        g.add(arrow([x0, yb, 0], [x0 + s_ * a, yb, 0], C.text, width=C.stroke, tip=0.14))
    if b > 1e-3:
        g.add(Polygon(*_pts([(x0, yb), (x0 + s_, yb), (x0 + s_, yb + s_ * b), (x0, yb + s_ * b)]),
                      stroke_color=C.text, stroke_width=C.thin + 0.4, fill_color=C.text, fill_opacity=0.07))
    return g


def g_zero(c, u):
    """0: a wave sliding past the axis; every crossing of zero is marked, the balance point it swings through."""
    x0, x1, y0 = c[0] - 1.0, c[0] + 1.0, c[1]
    a = ease(u, 0.0, 0.7)
    xs = np.linspace(x0, x0 + (x1 - x0) * max(a, 1e-3), 80)
    k, ph = 2 * PI / 1.0, 1.4 * u
    ys = y0 + 0.55 * np.sin(k * (xs - x0) - ph)
    g = VGroup(Line([x0 - 0.05, y0, 0], [x1 + 0.05, y0, 0], color=C.muted, stroke_width=C.thin),
               VMobject(stroke_color=C.cos, stroke_width=C.stroke).set_points_smoothly(_pts(zip(xs, ys))))
    for n in range(-1, 4):                                            # zeros: k (x - x0) - ph = n π
        x = x0 + (n * PI + ph) / k
        if x0 <= x <= x0 + (x1 - x0) * a:
            g.add(Dot([x, y0, 0], radius=0.05, color=C.text))
    return g


def five_constants(m, idn):
    """The equation steps up; five framed panels (e, i, π, 1, 0) pop in, each with a living graph, then fold back."""
    up = (T.five - 0.55, T.five + 0.2)
    m.play(idn.animate.scale(SHRINK).move_to(TOP), at=up[1], dur=up[1] - up[0], ease="easy_ease")
    order = ((0, g_e), (1, g_i), (2, g_pi), (4, g_one), (6, g_zero))
    t_pop = [T.five + 0.45 + 0.42 * k for k in range(5)]              # "of the most important numbers"
    fold = T.beautiful - 1.15                                         # "People call it…"
    for k, ((gi, fn), cx, tp) in enumerate(zip(order, PX, t_pop)):
        c = np.array([cx, PY])
        box = panel(cx, PY, PW, PW)
        m.play(FadeIn(box, scale=0.9), at=tp, dur=0.45, ease="out_back")
        lab = idn[gi].copy().scale(0.62).move_to([cx, PY + PW / 2 + 0.42, 0])
        m.play(TransformFromCopy(idn[gi], lab), at=tp + 0.1, dur=0.6, ease="easy_ease")
        win = (tp + 0.15, fold + 0.15 * k + 0.6)
        out = (fold + 0.15 * k, fold + 0.15 * k + 0.55)

        def draw(t, fn=fn, c=c, t0=win[0], out=out):
            g = fn(c, t - t0)
            return dim(g, 1 - ramp(t, *out)) if t > out[0] else g
        live(m, draw, win)
        m.play(FadeOut(lab, target_position=TOP + (idn[gi].get_center() - EQ) * SHRINK, scale=0.6), FadeOut(box),
               at=out[1], dur=out[1] - out[0], lead=out[1] - out[0])
    # "in one short line": the line is drawn under the equation and the five constants answer together
    ul = Line(LEFT, RIGHT, color=C.muted, stroke_width=C.thin + 0.4)
    ul.set_width(idn.width * SHRINK + 0.3).move_to(TOP + DOWN * 0.62)
    m.play(Create(ul), at=T.five + 3.3, dur=0.9, ease="easy_ease")
    m.play(LaggedStart(*[Indicate(idn[i], color=idn[i].get_color(), scale_factor=1.3) for i in (0, 1, 2, 4, 6)],
                       lag_ratio=0.18), at=T.five + 3.5, dur=1.2)
    m.play(FadeOut(ul), at=fold + 0.6, dur=0.5)
    m.play(idn.animate.scale(1 / SHRINK).move_to(EQ), at=T.beautiful + 0.2, dur=1.1, ease="easy_ease")


@scene(T.start, T.cut_preview)
def s00_hook(s):
    backdrop(s)
    m = s.manim()

    # ── "e to the i pi equals negative one" : glyph by glyph, each on its word ──
    eq = euler(size=150).move_to(EQ)
    e_, i_, pi_, eqs, minus, one = eq
    m.play(FadeIn(e_, scale=1.3), at=T.eq, dur=0.5)
    m.play(FadeIn(i_, scale=1.3), at=T.eq + 0.48, dur=0.4)            # "i"
    m.play(FadeIn(pi_, scale=1.3), at=T.eq + 0.72, dur=0.45)          # "pi"
    m.play(FadeIn(eqs), at=T.eq + 1.12, dur=0.4)                      # "equals"
    m.play(FadeIn(VGroup(minus, one), scale=1.3), at=T.neg1, dur=0.5)

    # ── "e to the i pi, plus one, equals zero": the −1 crosses the equals sign ──
    idn = identity(size=150).move_to(EQ)
    m.play(ReplacementTransform(e_, idn[0]), ReplacementTransform(i_, idn[1]), ReplacementTransform(pi_, idn[2]),
           ReplacementTransform(eqs, idn[5]),
           ReplacementTransform(minus, idn[3], path_arc=-PI / 2), ReplacementTransform(one, idn[4], path_arc=-PI / 2),
           at=T.plus_one, dur=1.1, ease="easy_ease")
    m.play(FadeIn(idn[6], scale=1.3), at=T.plus_one + 1.2, dur=0.5)   # "zero"

    # ── "Five of the most important numbers in mathematics": each constant gets its own living graph ──
    five_constants(m, idn)
    s.camera.push(T.beautiful, zoom=1.07, dur=2.6)                    # "the most beautiful equation"
    s.camera.push(T.slowly, zoom=1.0, dur=1.6)

    # ── "But read it slowly, and it stops making sense": the colour drains ──
    m.play(idn.animate.set_color(C.faint), at=T.slowly + 0.4, dur=1.4)

    # ── "e is about two point seven" ──
    e_row = glyphs(r"e=2.71828\ldots", {0: C.growth}, size=96, n=12).move_to([0, 2.05, 0])
    m.play(TransformFromCopy(idn[0], e_row[0]), at=T.two_seven - 0.55, dur=1.0)
    m.play(FadeOut(idn, shift=0.35 * DOWN), at=T.two_seven - 0.3, dur=0.9)
    m.play(LaggedStart(*[FadeIn(g, shift=0.1 * LEFT) for g in e_row[1:]], lag_ratio=0.12),
           at=T.two_seven + 0.35, dur=1.0)

    # ── "Raising a number to a power means multiplying it by itself": e³ = e·e·e ──
    pw = glyphs(r"e^3=e\cdot e\cdot e", {0: C.growth, 3: C.growth, 5: C.growth, 7: C.growth}, size=120, n=8)
    pw.move_to([0, -0.45, 0])
    m.play(FadeIn(pw[0]), FadeIn(pw[1], shift=0.15 * UP), at=T.power + 1.2, dur=0.6)          # "a power"
    m.play(FadeIn(pw[2]), at=T.power + 1.8, dur=0.3)
    m.play(LaggedStart(*[FadeIn(g, shift=0.12 * RIGHT) for g in pw[3:]], lag_ratio=0.22),
           at=T.power + 2.15, dur=1.1)                                                       # "multiplying it by itself"
    br = Brace(pw[3:], DOWN, buff=0.18, color=C.muted)
    n3 = MathTex("3", font_size=64, color=C.text).next_to(br, DOWN, buff=0.15)
    m.play(GrowFromCenter(br), FadeIn(n3), at=T.power + 3.0, dur=0.6)

    # ── "So what would it mean to multiply e by itself i pi times?" ──
    pw2 = glyphs(r"e^{i\pi}=e\cdot e\cdot e\cdots", {0: C.growth, 1: C.turn, 2: C.arc, 4: C.growth, 6: C.growth,
                                                      8: C.growth}, size=120)
    pw2.move_to(pw).align_to(pw, LEFT)
    br2 = Brace(pw2[4:], DOWN, buff=0.18, color=C.muted)
    ipq = glyphs(r"i\pi\,?", {0: C.turn, 1: C.arc}, size=64).next_to(br2, DOWN, buff=0.15)
    t_ipi = T.times + 0.75                                                                   # "i pi times?"
    m.play(ReplacementTransform(pw[0], pw2[0]), ReplacementTransform(pw[1], VGroup(pw2[1], pw2[2])),
           *[ReplacementTransform(pw[k], pw2[k + 1]) for k in range(2, 8)],
           FadeIn(pw2[9:], shift=0.12 * RIGHT), ReplacementTransform(br, br2), ReplacementTransform(n3, ipq),
           at=t_ipi, dur=0.9, ease="easy_ease")
    m.play(Wiggle(pw2[4:], scale_value=1.04, rotation_angle=0.025 * TAU), at=T.times + 1.5, dur=0.9)

    # ── "An imaginary number of times?": the chain comes apart ──
    rng = np.random.default_rng(7)
    links = list(pw2[4:]) + [br2]
    drift = [FadeOut(g, shift=rng.uniform(-0.5, 0.5) * RIGHT + rng.uniform(-0.7, -0.2) * UP,
                     rate_func=rate_functions.ease_in_cubic) for g in links]
    m.play(LaggedStart(*drift, lag_ratio=0.12), at=T.imaginary + 0.6, dur=2.0, lead=0)
    m.play(VGroup(pw2[:4], ipq, e_row).animate.set_color(C.faint), at=T.imaginary + 0.6, dur=1.2, lead=0)

    # ── "...a clever trick with symbols. It is not.": the symbols leave ──
    m.play(FadeOut(VGroup(pw2[:4], ipq, e_row), shift=0.2 * UP), at=T.not_, dur=0.9)

    # ── "It is a picture.": the unit circle, one point at 1 ──
    ax = VGroup(Line(P(HERO_O, HERO_U, -1.7), P(HERO_O, HERO_U, 1.7), color=C.ghost, stroke_width=C.thin),
                Line(P(HERO_O, HERO_U, -1.25j), P(HERO_O, HERO_U, 1.25j), color=C.ghost, stroke_width=C.thin))
    circ = Circle(radius=HERO_U, color=C.text, stroke_width=C.thin + 1).move_to([*HERO_O, 0]).rotate(0.0)
    dot = Dot(P(HERO_O, HERO_U, 1), radius=0.09, color=C.point)
    m.play(Create(ax), at=T.picture - 0.2, dur=0.8)
    m.play(Create(circ), at=T.picture + 0.15, dur=1.2, ease="easy_ease")
    m.play(FadeIn(dot, scale=2.0), at=T.picture + 1.1, dur=0.4)
