"""in_s01 · Patterns, not chores (the video's first scene).

1. Worksheets of sums hang at three depths; the camera drifts through them (2.5D parallax) and answers write in.
2. 'something else': the sheets blow apart; their figures scatter as points and settle on 'patterns' into a sunflower
   spiral (phyllotaxis: point k at radius c·sqrt(k), angle k·137.5°).
3. Three objects that share one shape, side by side: a pond ripple (outgoing damped ring packets, computed per frame, shown as a
   contoured field), a spoked wheel rolling on a scrolling road while a rim point traces a cycloid, a ticking clock.
4. 'one shape': the circle in each is drawn over it; 'stripped': the three circles fly to the centre and become THE
   circle while the objects dissolve. Title lockup in the pause.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import HUB_R, P3, caps, dim, sans, tex, the_circle, tint, window

R0 = 1.25                                   # each object's circle
TILES = {"pond": P3(-4.4, 0.3), "wheel": P3(0.0, 0.3), "clock": P3(4.4, 0.3)}
GOLD = math.radians(137.50776)
N_PTS = 610

PROBLEMS = [
    ("37 + 48", "85"), ("12 \\times 7", "84"), ("3x + 5 = 17", "x = 4"), ("\\tfrac12 + \\tfrac13", "\\tfrac56"),
    ("2^{10}", "1024"), ("\\sqrt{144}", "12"), ("0.25 \\times 16", "4"), ("(x+2)(x-3)", "x^2 - x - 6"),
    ("96 \\div 8", "12"), ("15\\% \\text{ of } 80", "12"), ("7^2 - 5^2", "24"), ("2x - 9 = 3", "x = 6"),
    ("4.5 + 2.75", "7.25"), ("\\tfrac34 \\times 12", "9"), ("19 \\times 21", "399"), ("x^2 = 49", "x = \\pm 7"),
    ("625 \\div 25", "25"), ("3^4", "81"),
]
# (depth layer, centre, tilt): far sheets first
SHEETS = [(0, (-4.6, 1.2), 0.06), (0, (0.4, 1.9), -0.04), (0, (4.9, 1.0), 0.05),
          (1, (-2.6, -0.6), -0.05), (1, (2.9, -0.4), 0.04),
          (2, (-5.3, -1.6), 0.03), (2, (0.2, -1.2), -0.02), (2, (5.4, -1.9), -0.05)]
DEPTH = {0: (0.55, 0.42), 1: (0.78, 0.68), 2: (1.0, 1.0)}           # parallax, brightness


def sheet(k, centre, tilt):
    """A worksheet: a page outline, a header and six problems with blanks. Returns (group, answers)."""
    w, h = 3.1, 3.9
    page = Rectangle(width=w, height=h, stroke_color=C.map_off, stroke_width=1.6, fill_color=C.bg, fill_opacity=1)
    head = VGroup(sans("worksheet", 24, C.muted), Line(ORIGIN, RIGHT * 1.0, stroke_color=C.map_off, stroke_width=1.2))
    head.arrange(RIGHT, buff=0.25).move_to(page.get_top() + DOWN * 0.38)
    rows, answers = VGroup(), VGroup()
    for j in range(6):
        q, a = PROBLEMS[(k * 5 + j * 7) % len(PROBLEMS)]
        prob = tex(rf"{j + 1}.\; {q} =", 30, C.muted)
        prob.move_to(page.get_left() + RIGHT * 0.25 + UP * (h / 2 - 0.95 - 0.5 * j), aligned_edge=LEFT)
        blank = Line(ORIGIN, RIGHT * 0.7, stroke_color=C.map_off, stroke_width=1.2).next_to(prob, RIGHT, buff=0.12)
        blank.shift(DOWN * (blank.get_y() - prob.get_bottom()[1]))
        ans = tex(a, 30, C.text).next_to(blank, UP, buff=0.04)
        rows.add(prob, blank)
        answers.add(ans)
    g = VGroup(page, head, rows)
    VGroup(g, answers).rotate(tilt).move_to(P3(*centre))
    return g, answers


def phyllotaxis(n=N_PTS, r_max=3.0):
    k = np.arange(n)
    r = r_max * np.sqrt((k + 0.5) / n)
    return np.c_[r * np.cos(k * GOLD), r * np.sin(k * GOLD)]


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


@scene(T.in_s01, T.in_s02)
def in_s01(s):
    s.solid(C.bg, z=-200)
    t_else, t_pat = float(T.in_s01_something_else), float(T.in_s01_patterns)
    t_rip, t_whl, t_clk = float(T.in_s01_ripple), float(T.in_s01_wheel), float(T.in_s01_clock)
    t_one, t_str = float(T.in_s01_one_shape), float(T.in_s01_stripped)

    # ---- 1. worksheets in depth; the camera drifts through them, then pulls back as they blow apart
    s.camera.push(s.start + 0.4, zoom=1.16, dur=t_else - s.start - 0.6, ease="smooth", lead=0)
    s.camera.push(t_else, zoom=1.0, dur=1.6, ease="easy_ease")
    layers = {d: s.manim(z=-10 + d, parallax=DEPTH[d][0]) for d in DEPTH}
    all_answers, sheets = [], []
    for k, (d, c, tilt) in enumerate(SHEETS):
        g, ans = sheet(k, c, tilt)
        dim(g, DEPTH[d][1])
        dim(ans, DEPTH[d][1])
        L = layers[d]
        L.play(FadeIn(g, shift=0.15 * UP), at=s.start + 0.5 + 0.18 * k, dur=1.2, lead=0)
        if d > 0:
            all_answers += [(L, a) for a in ans[:4]]
        sheets.append((L, g, ans, np.array(c)))
    for j, (L, a) in enumerate(all_answers):
        L.play(Write(a), at=T.in_s01_solve + 0.17 * j, dur=0.45)
    for L, g, ans, c in sheets:                                   # blown outward, turning, gone
        out = c / max(np.linalg.norm(c), 0.4)
        L.play(VGroup(g, ans).animate.shift(P3(*(4.5 * out))).rotate(0.35 * np.sign(out[0] + 1e-3)).set_opacity(0),
               at=t_else + 0.2, dur=1.3, ease="in_cubic")
        L.remove(g, ans, at=t_else + 1.6)

    # ---- 2. figures scatter as points and settle into the sunflower spiral on 'patterns'
    rg = np.random.default_rng(15)
    src = np.vstack([np.array(c) + rg.uniform([-1.3, -1.7], [1.3, 1.5], (N_PTS // len(SHEETS) + 1, 2))
                     for _, c, _ in SHEETS])[:N_PTS]
    scat = src * 1.6 + rg.normal(0, 0.6, src.shape)
    spiral = phyllotaxis()
    order = np.argsort(np.linalg.norm(spiral, axis=1))
    spiral = spiral[np.argsort(order)]                            # nearest-first stagger by final radius
    lag = np.linalg.norm(spiral, axis=1) / 3.0 * 0.6
    t_a, t_b = t_else + 0.25, t_pat - 1.6

    def pts(t):
        f1 = smooth((t - t_a) / 1.2)
        f2 = smooth((t - t_b - lag) / 1.4)[:, None]
        p = src + (scat - src) * f1
        return p + (spiral - p) * f2

    radius_v = np.linalg.norm(spiral, axis=1) / 3.0
    on = fade(t_a, dur=0.4, out=t_rip + 0.3, out_dur=0.7)
    s.add(PointsLayer(pts, values=lambda t: radius_v, colors=(C.foundations, C.circle, C.quantity), cmap="diverging",
                      vmin=0.0, vmax=1.0,
                      size=4.2, glow=0.0, additive=False, opacity=on, z=-4, start=t_a - 0.1, end=t_rip + 1.2))

    # ---- 3a. the pond: a drop on still water (damped wave equation), shown as contoured crests and troughs
    side = 3.3
    n_g = 256
    yy, xx = np.mgrid[0:n_g, 0:n_g]
    rr = np.hypot(xx - (n_g - 1) / 2, yy - (n_g - 1) / 2) / (n_g / 2) * (side / 2)    # world units from the drop
    pond_mask = 1 - smooth((rr - 1.3) / 0.32)
    drops = [t_rip + 0.15 + 1.25 * j for j in range(5)]
    c_w, lam = 0.55, 0.34                                        # wave speed (units/s) and wavelength

    def pond(t):
        """Outgoing ring packets, one per drop: a Gaussian envelope riding at r = c·(t − t0), cos(2π(r − ct)/λ),
        amplitude falling as 1/sqrt(r) (energy spreading on a 2D surface) and with age (damping)."""
        h = np.zeros_like(rr)
        for j, t0 in enumerate(drops):
            age = t - t0
            if age <= 0:
                continue
            front = c_w * age
            env = np.exp(-((rr - front + 0.35) / 0.42) ** 2) * (rr < front)
            h += (0.9 - 0.1 * j) * env * np.cos(2 * np.pi * (rr - front) / lam) / np.sqrt(0.35 + rr) * np.exp(-0.35 * age)
        h = np.sign(h) * np.abs(h) ** 2.2 * 2.0                 # sharpen crests and troughs into thin rings
        return (h * pond_mask).astype(np.float32)

    pond_on = fade(t_rip, dur=0.5, out=t_str + 0.15, out_dur=0.6)
    s.add(FieldLayer(pond, cmap="diverging", vmin=-0.6, vmax=0.6,
                     colors=(tint(C.foundations, 0.9), C.bg, C.circle), contours=0, extent=(side, side),
                     center=tuple(TILES["pond"][:2]), opacity=pond_on, z=-3, start=t_rip - 0.2, end=t_str + 0.9))
    m = s.manim(z=0)
    labels = VGroup(*(sans(w_, 28, C.muted).move_to(TILES[w_] + DOWN * (R0 + 0.55)) for w_ in TILES))
    m.play(FadeIn(labels[0], shift=0.08 * UP), at=t_rip + 0.3, dur=0.5)

    # ---- 3b. the wheel rolls: road scrolls left, a rim point traces a cycloid
    wc = TILES["wheel"]
    om = 1.6                                                       # rad/s, clockwise: rolling to the right
    road_y = wc[1] - R0 - 0.03
    x_lo, x_hi = wc[0] - 2.0, wc[0] + 2.0

    def phi(t):
        return -om * (t - t_whl)

    def wheel(t):
        a = phi(t)
        g = VGroup()
        g.add(Circle(radius=R0 - 0.045, stroke_color=C.muted, stroke_width=7).move_to(wc))       # tyre
        g.add(Circle(radius=R0 - 0.13, stroke_color=C.text, stroke_width=1.8).move_to(wc))      # rim
        for j in range(24):                                     # tangential lacing from two hub flanges
            q = a + 2 * math.pi * j / 24
            dq = 0.55 if j % 2 else -0.55
            h0 = wc + 0.17 * P3(math.cos(q), math.sin(q))
            h1 = wc + (R0 - 0.14) * P3(math.cos(q + dq), math.sin(q + dq))
            g.add(Line(h0, h1, stroke_color=C.text, stroke_width=1.1, stroke_opacity=0.75))
        g.add(Circle(radius=0.19, stroke_color=C.text, stroke_width=2.4, fill_color=C.bg, fill_opacity=1).move_to(wc))
        g.add(Dot(wc, radius=0.06, color=C.text))
        v = om * (R0 - 0.0)                                       # road speed = ω R (rolling without slipping)
        off = (v * (t - t_whl)) % 0.5
        g.add(Line(P3(x_lo, road_y), P3(x_hi, road_y), stroke_color=C.map_off, stroke_width=2))
        for x in np.arange(x_lo - off, x_hi, 0.5):              # road marks scroll left
            x0, x1 = max(x, x_lo), min(x + 0.22, x_hi)
            if x1 > x0:
                g.add(Line(P3(x0, road_y - 0.12), P3(x1, road_y - 0.12), stroke_color=C.map_off, stroke_width=2))
        # the cycloid: where the marked rim point has been, carried along with the road
        taus = np.linspace(max(t_whl, t - 4.0), t, 90)
        if t - t_whl > 0.05:
            ang = -math.pi / 2 + phi(taus)
            px = wc[0] + R0 * np.cos(ang) - v * (t - taus)
            py = wc[1] + R0 * np.sin(ang)
            keep = px >= x_lo
            if keep.sum() > 2:
                path = [P3(x, y) for x, y in zip(px[keep], py[keep])]
                g.add(VMobject(stroke_color=C.change, stroke_width=2.6).set_points_as_corners(path))
        pa = -math.pi / 2 + phi(t)
        g.add(Dot(wc + R0 * P3(math.cos(pa), math.sin(pa)), radius=0.075, color=C.change))
        return g

    # ---- 3c. the clock: dial, numerals, ticking hands
    cc = TILES["clock"]
    numerals = [tex(str(n), 26, C.text) for n in range(1, 13)]

    def clock(t):
        g = VGroup(Circle(radius=R0, stroke_color=C.text, stroke_width=3.2).move_to(cc),
                   Circle(radius=R0 - 0.09, stroke_color=C.map_off, stroke_width=1.2).move_to(cc))
        for k in range(60):
            q = math.pi / 2 - 2 * math.pi * k / 60
            u = P3(math.cos(q), math.sin(q))
            L = 0.17 if k % 5 == 0 else 0.07
            g.add(Line(cc + (R0 - 0.12 - L) * u, cc + (R0 - 0.12) * u, stroke_color=C.text if k % 5 == 0 else C.muted,
                       stroke_width=2.4 if k % 5 == 0 else 1.0))
        for n in range(12):
            q = math.pi / 2 - 2 * math.pi * (n + 1) / 12
            g.add(numerals[n].copy().move_to(cc + (R0 - 0.52) * P3(math.cos(q), math.sin(q))))
        el = t - t_clk
        sec = 23 + math.floor(el) + smooth((el % 1.0) / 0.12)          # the second hand ticks
        mins = 10 + 2.0 * el / 60 * 60 / 60 * 6
        hrs = 10 + mins / 60
        for val, per, L, wdt, col in ((hrs, 12, 0.6, 4.0, C.text), (mins, 60, 0.92, 2.8, C.text),
                                      (sec, 60, 1.0, 1.4, C.uncertainty)):
            q = math.pi / 2 - 2 * math.pi * val / per
            u = P3(math.cos(q), math.sin(q))
            g.add(Line(cc - 0.14 * u, cc + L * u, stroke_color=col, stroke_width=wdt))
        g.add(Dot(cc, radius=0.055, color=C.uncertainty))
        return g

    w_on = fade(t_whl, dur=0.5)
    c_on = fade(t_clk, dur=0.5)
    end_live = t_str - 0.15
    m.redraw(window(lambda t: dim(wheel(t), float(w_on(t))), t_whl - 0.2, end_live), during=(t_whl - 0.2, end_live + 0.05))
    m.redraw(window(lambda t: dim(clock(t), float(c_on(t))), t_clk - 0.2, end_live), during=(t_clk - 0.2, end_live + 0.05))
    m.play(FadeIn(labels[1], shift=0.08 * UP), at=t_whl + 0.3, dur=0.5)
    m.play(FadeIn(labels[2], shift=0.08 * UP), at=t_clk + 0.3, dur=0.5)

    # ---- 4. 'one shape': the circle in each object; 'stripped': they merge into THE circle
    rings = [the_circle(R0).move_to(TILES[w_]) for w_ in TILES]
    for j, r in enumerate(rings):
        m.play(Create(r), at=t_one + 0.18 * j, dur=0.7, ease="easy_ease")
    w_last, c_last = wheel(end_live), clock(end_live)
    m.add(w_last, c_last, at=end_live)
    hub = the_circle(fill_color=C.bg, fill_opacity=0.0)
    m.play(*(Transform(r, hub.copy()) for r in rings), FadeOut(w_last, scale=0.85), FadeOut(c_last, scale=0.85),
           FadeOut(labels), at=t_str, dur=1.4, ease="easy_ease")
    m.remove(*rings[1:], at=t_str + 1.4)
    title = VGroup(caps("Fundamentals of Math", 64), sans("the big picture", 36, C.muted)).arrange(DOWN, buff=0.26)
    title.move_to(P3(0, -2.55))
    m.play(FadeIn(title, shift=0.1 * UP), at=t_str + 1.6, dur=0.7)
    m.play(FadeOut(title), at=s.end - 0.45, dur=0.45)
