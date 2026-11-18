"""Shared building blocks for "What the Matrix Exponential Actually Is" (011).

Everything is a pure function of t, and every number comes from verify.py (`CAST`).
- text:    tex, words, sc (small caps), fmt
- plane:   arrow, rot2, plot, field_arrows, live, backdrop, finish
- flows:   disc_points, flow_layers (yellow particles + teal trails, exact X0 · expm(τA)ᵀ)
- prologue line art (C.frame strokes): cup, steam, coin, coin_stack, petri, rock, pill_shape, compartments,
           rooms_icon, circuit_icon, building_icon, satellite_icon, arm_icon, qwire_icon, lie_icon
- molecules: Molecules (seeded hop/clear times for the pill, same law as verify.py)
- globe:   globe_wire (a small turning wireframe Earth with its purple axis)
"""
from functools import lru_cache
from pathlib import Path

from scipy.linalg import expm

from aion import *
from verify import CAST, J

E = "easy_ease"
FRAME = (-7.3, -4.2, 7.3, 4.2)                      # a little past the 14.22 x 8 frame
HOOK = CAST["hook"]                                 # pi J
EW_HOOK = np.exp(HOOK)                              # the element-wise guess (det 0)
assert np.allclose(expm(HOOK), -np.eye(2)) and abs(np.linalg.det(EW_HOOK)) < 1e-12


# ---------------------------------------------------------------- text
def tex(*parts, size=None, colors=None, color=None):
    """MathTex in the theme's text color; `colors` maps part index → color."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def words(text, size=None, color=None):
    """Plain words set in LaTeX (Computer Modern), so words and maths share one typeface."""
    return Tex(text, font_size=size or C.tex_size, color=color or C.text)


def sc(text, size=30, color=None):
    """Names and dates in CM small caps (the intro's history), in the `data` gray."""
    return Tex(r"\textsc{" + text + "}", font_size=size, color=color or C.data)


def lab(text, size=26, color=None):
    """Labels and units in CM sans: visibly a different voice from the maths (CM roman)."""
    return Tex(r"\textsf{" + text + "}", font_size=size, color=color or C.muted)


def key(text, size=34, color=None):
    """A key word in bold CM, for the few words that carry an idea on screen."""
    return Tex(r"\textbf{" + text + "}", font_size=size, color=color or C.text)


def heat_color(f):
    """Temperature ramp: 0 = room (cool blue) → violet → warm amber → 1 hot red (never through a muddy gray)."""
    f = float(np.clip(f, 0, 1))
    stops = [(0.0, C.cool), (0.33, "#b48cff"), (0.66, C.warm), (1.0, C.heat)]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if f <= b:
            return interpolate_color(ManimColor(ca), ManimColor(cb), (f - a) / (b - a))
    return ManimColor(C.heat)


# ---------------------------------------------------------------- plane helpers
def rot2(a):
    """2x2 rotation by `a` radians (counterclockwise)."""
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def p3(v):
    v = np.asarray(v, float)
    return np.array([v[0], v[1], 0.0])


def arrow(a, b, color, width=None, tip=0.24, opacity=1.0):
    """A crisp straight arrow between two world points (tip scaled down for short arrows)."""
    a, b = p3(a), p3(b)
    L = max(np.linalg.norm(b - a), 1e-6)
    return Arrow(a, b, buff=0, color=color, stroke_width=width or C.stroke, tip_length=min(tip, 0.4 * L),
                 max_tip_length_to_length_ratio=0.4, max_stroke_width_to_length_ratio=40).set_opacity(opacity)


def poly(pts, color, width=None, opacity=1.0, close=False):
    """A crisp polyline through 2D points."""
    P = np.array([p3(p) for p in pts])
    if close:
        P = np.vstack([P, P[:1]])
    return VMobject(stroke_color=color, stroke_width=width or C.stroke, stroke_opacity=opacity).set_points_as_corners(P)


def plot(f, x0, x1, origin, ux, uy, color, width=None, n=200, opacity=1.0):
    """The graph of y = f(x) on [x0, x1] as a polyline; graph point (x, y) sits at origin + (ux x, uy y)."""
    xs = np.linspace(x0, x1, n)
    ys = np.asarray(f(xs), float) * np.ones_like(xs)
    o = np.asarray(origin, float)
    return poly(np.stack([o[0] + ux * xs, o[1] + uy * ys], -1), color, width, opacity)


def mini_axes(origin, w, h, color=None, width=None):
    """Two thin axis lines (no numbers), for the prologue's small plots."""
    o = np.asarray(origin, float)
    col = color or C.muted
    return VGroup(Line(p3(o), p3(o + [w, 0]), color=col, stroke_width=width or C.thin),
                  Line(p3(o), p3(o + [0, h]), color=col, stroke_width=width or C.thin))


def field_arrows(A, center=(0, 0), unit=1.0, box=FRAME, spacing=0.75, opacity=1.0, grow=1.0, skip=0.35):
    """The velocity field A v as short orange arrows on a lattice, log-compressed so the far field stays calm.

    `grow` (0–1) scales every arrow (fade-in growth); lattice points within `skip` of the centre are left out.
    """
    A = np.asarray(A, float)
    c = np.asarray(center, float)
    out = VGroup()
    xs = np.arange(np.ceil((box[0] - c[0]) / spacing), np.floor((box[2] - c[0]) / spacing) + 1) * spacing
    ys = np.arange(np.ceil((box[1] - c[1]) / spacing), np.floor((box[3] - c[1]) / spacing) + 1) * spacing
    for x in xs:
        for y in ys:
            v = np.array([x, y]) / unit
            if np.linalg.norm(v * unit) < skip:
                continue
            d = A @ v
            n = np.linalg.norm(d)
            if n < 1e-9:
                continue
            L = min(0.6, 0.55 * np.log1p(n) / np.log(2)) * grow
            if L < 0.03:
                continue
            a = c + v * unit
            out.add(arrow(a, a + d / n * L, C.gen, width=C.thin + 0.6, tip=0.13, opacity=opacity))
    return out


def dim(mob, a):
    """Fade a drawing to opacity `a` without filling outlines (set_opacity would fill closed line art)."""
    for sub in mob.get_family():
        if isinstance(sub, VMobject):
            sub.set_stroke(opacity=a * sub.get_stroke_opacity())
            if sub.get_fill_opacity() > 0:
                sub.set_fill(opacity=a * sub.get_fill_opacity())
    return mob


def live(m, fn, *windows):
    """Rebuild `fn(t)` every frame inside each (start, end) window and hold it still in between."""
    merged = []
    for a, b in sorted(windows):
        if merged and a <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    hs = []
    for a, b in merged:
        if hs:
            m.remove(hs[-1], at=a)
        hs.append(m.redraw(fn, during=(a, b)))
    return hs


def backdrop(s):
    s.solid(C.bg, z=-200)


def finish(s):
    """Frame finish from the theme (Classic sets every term to zero, so this adds nothing)."""
    fx = []
    if C.bloom > 0:
        fx.append(Bloom(C.bloom, threshold=0.8))
    if C.vignette > 0 or C.grain > 0:
        fx.append(Lens(vignette=C.vignette, grain=C.grain))
    if fx:
        s.fx(*fx)


# ---------------------------------------------------------------- flows: particles + trails
@lru_cache(maxsize=None)
def disc_points(n=4000, radius=3.6, seed=3, center=(0.0, 0.0)):
    """n seeded points spread evenly (area-uniform) over a disc."""
    g = rng(seed)
    r = radius * np.sqrt(g.random(n))
    a = 2 * np.pi * g.random(n)
    return np.stack([center[0] + r * np.cos(a), center[1] + r * np.sin(a)], -1)


def flow_layers(s, X0, A, tau, alpha=1.0, trail=8, dt=0.04, size=2.6, z=2, unit=1.0, center=(0.0, 0.0), **kw):
    """Yellow particles X0 · expm(τ(t) A)ᵀ plus `trail` teal ghosts at τ(t − kΔ): streaks only while they move.

    `tau` is a Track (flow time), `alpha` a Track or number. Positions are exact for a constant A; extra keyword
    arguments (start, end, ...) go to every PointsLayer.
    """
    A = np.asarray(A, float)
    X0 = np.asarray(X0, float)
    c = np.asarray(center, float)
    tau = track(tau)
    al = track(alpha)

    def at(lag):
        def pos(t):
            M = expm(float(tau(t - lag)) * A)
            return c + unit * (X0 @ M.T)
        return pos

    for k in range(trail, 0, -1):
        s.add(PointsLayer(at(k * dt), color=C.flow, size=size * (1 - 0.5 * k / trail), glow=0.0,
                          alpha=al * (0.55 * (1 - k / (trail + 1))), additive=False, z=z, **kw))
    s.add(PointsLayer(at(0.0), color=C.vec, size=size, glow=0.0, alpha=al, additive=False, z=z + 0.1, **kw))


def clip_vec(o, v, box):
    """Shorten the arrow o → o + v so it stays inside box; returns (end, clipped?)."""
    o, v = np.asarray(o, float), np.asarray(v, float)
    s = 1.0
    for i, (lo, hi) in enumerate(((box[0], box[2]), (box[1], box[3]))):
        e = o[i] + v[i]
        if e > hi:
            s = min(s, (hi - o[i]) / v[i])
        elif e < lo:
            s = min(s, (lo - o[i]) / v[i])
    return o + s * v, s < 1.0


# the plane panel shared by s04 (the wrong guess) and the start of s05 (the real answer)
PLANE_BOX = (0.4, -3.7, 6.9, 3.7)
PLANE_C = np.array([3.65, 0.0])


# ---------------------------------------------------------------- prologue line art (C.frame, thin, crisp)
def cup(center=(0, 0), w=1.6, h=1.4):
    """A coffee cup: tapered body, handle, saucer and the coffee's surface line."""
    c = np.asarray(center, float)
    W = C.thin + 0.6
    body = poly([c + [-w / 2, h / 2], c + [-w * 0.4, -h / 2], c + [w * 0.4, -h / 2], c + [w / 2, h / 2]], C.frame, W)
    rim = Line(p3(c + [-w / 2, h / 2]), p3(c + [w / 2, h / 2]), color=C.frame, stroke_width=W)
    surf = Line(p3(c + [-w * 0.47, h * 0.36]), p3(c + [w * 0.47, h * 0.36]), color=C.frame, stroke_width=C.thin,
                stroke_opacity=0.6)
    handle = Arc(radius=h * 0.26, start_angle=-PI / 2, angle=PI, color=C.frame, stroke_width=W).move_to(
        p3(c + [w * 0.52, h * 0.05]))
    saucer = Line(p3(c + [-w * 0.75, -h / 2 - 0.08]), p3(c + [w * 0.75, -h / 2 - 0.08]), color=C.frame,
                  stroke_width=W)
    return VGroup(body, rim, surf, handle, saucer)


def cup_liquid(center=(0, 0), w=1.6, h=1.4, color=None, opacity=0.85):
    """The coffee inside the cup (filled to the surface line), coloured by its temperature."""
    c = np.asarray(center, float)
    top = h * 0.36
    f = (top + h / 2) / h                                    # fraction of the height that is filled
    xt = w / 2 - (w / 2 - w * 0.4) * (1 - f)                 # body half-width at the surface (linear taper)
    pts = [c + [-w * 0.4 + 0.04, -h / 2 + 0.04], c + [w * 0.4 - 0.04, -h / 2 + 0.04], c + [xt * 0.97, top],
           c + [-xt * 0.97, top]]
    return Polygon(*[p3(p) for p in pts], stroke_width=0, fill_color=color or C.heat, fill_opacity=opacity)


def thermometer(base, height, frac, color, width=0.24):
    """A thermometer: bulb at `base`, tube `height` tall, liquid filled to `frac` (0–1) in `color`."""
    b = np.asarray(base, float)
    r = width * 1.15
    W = C.thin + 0.6
    tube = RoundedRectangle(width=width, height=height, corner_radius=width / 2, color=C.frame,
                            stroke_width=W).move_to(p3(b + [0, r * 0.6 + height / 2]))
    bulb = Circle(radius=r, color=C.frame, stroke_width=W).move_to(p3(b))
    liq_h = max(frac, 0.0) * (height - width) + r * 0.6
    liq = VGroup(Circle(radius=r * 0.72, stroke_width=0, fill_color=color, fill_opacity=1).move_to(p3(b)),
                 Rectangle(width=width * 0.5, height=liq_h, stroke_width=0, fill_color=color, fill_opacity=1)
                 .move_to(p3(b + [0, liq_h / 2])))
    return VGroup(liq, tube, bulb)


def steam(center, t, heat=1.0, h=1.4, w=1.6, color=None):
    """Three wavy steam strokes rising off the cup (pure in t); `heat` 0–1 thins them as it cools."""
    c = np.asarray(center, float)
    out = VGroup()
    for k, dx in enumerate((-0.3, 0.0, 0.3)):
        ys = np.linspace(0, 1.1 * heat + 0.15, 30)
        xs = dx * w / 1.6 + 0.09 * np.sin(5.5 * ys - 2.6 * t + 1.7 * k) * (0.4 + ys)
        pts = np.stack([c[0] + xs, c[1] + h / 2 + 0.15 + ys], -1)
        out.add(poly(pts, color or C.frame, C.thin + 0.3, opacity=0.65 * heat))
    return out


def coin(center=(0, 0), r=0.32, flat=0.32, color=None):
    """One coin seen slightly from above (an ellipse with an edge)."""
    c = np.asarray(center, float)
    col = color or C.frame
    top = Ellipse(width=2 * r, height=2 * r * flat, color=col, stroke_width=C.thin + 0.4).move_to(p3(c))
    edge = VGroup(Line(p3(c + [-r, 0]), p3(c + [-r, -0.08]), color=col, stroke_width=C.thin + 0.4),
                  Line(p3(c + [r, 0]), p3(c + [r, -0.08]), color=col, stroke_width=C.thin + 0.4))
    return VGroup(top, edge)


def coin_stack(base, n, r=0.32, step=0.11, flat=0.32, color=None):
    """A stack of n coins: the front rim of each coin (a lower half-ellipse), the two sides, and the top face."""
    n = max(int(n), 0)
    if n == 0:
        return VGroup()
    b = np.asarray(base, float)
    W = C.thin + 0.4
    out = VGroup()
    a = np.linspace(PI, 2 * PI, 24)
    for k in range(n):
        y = b[1] + k * step - 0.08
        out.add(poly(np.stack([b[0] + r * np.cos(a), y + r * flat * np.sin(a)], -1), (color or C.frame), W))
    top = b[1] + (n - 1) * step
    out.add(Ellipse(width=2 * r, height=2 * r * flat, color=(color or C.frame), stroke_width=W).move_to(p3([b[0], top])))
    for d in (-1, 1):
        out.add(Line(p3([b[0] + d * r, b[1] - 0.08]), p3([b[0] + d * r, top]), color=(color or C.frame), stroke_width=W))
    return out


def petri(center=(0, 0), r=1.05, color=None):
    c = p3(center)
    col = color or C.frame
    return VGroup(Circle(radius=r, color=col, stroke_width=C.thin + 0.4).move_to(c),
                  Circle(radius=r * 0.93, color=col, stroke_width=C.thin, stroke_opacity=0.5).move_to(c))


ROCK = np.array([[-1.0, -0.35], [-0.8, 0.35], [-0.25, 0.62], [0.35, 0.55], [0.95, 0.2], [1.0, -0.3],
                 [0.55, -0.6], [-0.4, -0.62]])


def rock(center=(0, 0), s=1.0, color=None):
    return poly(np.asarray(center) + s * ROCK, color or C.frame, C.thin + 0.6, close=True)


def inside_poly(P, pts):
    """Even-odd point-in-polygon test, vectorised over pts (n, 2)."""
    x, y = pts[:, 0], pts[:, 1]
    ins = np.zeros(len(pts), bool)
    for i in range(len(P)):
        (x1, y1), (x2, y2) = P[i], P[(i + 1) % len(P)]
        cross = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        ins ^= cross
    return ins


def pill_shape(center=(0, 0), L=0.7, r=0.17, angle=0.5):
    """A capsule outline with its seam."""
    c = np.asarray(center, float)
    a = np.linspace(-PI / 2, PI / 2, 16)
    right = np.stack([L / 2 + r * np.cos(a), r * np.sin(a)], -1)
    left = np.stack([-L / 2 - r * np.cos(a), -r * np.sin(a)], -1)
    R = rot2(angle)
    P = np.vstack([right, left]) @ R.T + c
    seam = np.array([[0, -r], [0, r]]) @ R.T + c
    return VGroup(poly(P, C.dose, C.thin + 0.6, close=True), poly(seam, C.dose, C.thin, opacity=0.7))


# the two compartments of the pill story: a stomach pouch above, a bloodstream loop below
STOMACH_C, BLOOD_C = np.array([-4.3, 1.35]), np.array([-4.3, -1.65])
BLOOD_RX, BLOOD_RY, BLOOD_W = 1.75, 0.85, 0.42      # loop centre-line radii and channel width


def stomach_outline(c=STOMACH_C):
    a = np.linspace(0, 2 * PI, 80)
    r = 1.0 + 0.12 * np.cos(2 * a + 0.6) - 0.08 * np.sin(3 * a)
    pts = np.stack([1.45 * r * np.cos(a), 0.95 * r * np.sin(a)], -1) + c
    return pts


def blood_loop(c=BLOOD_C):
    a = np.linspace(0, 2 * PI, 120)
    outer = np.stack([(BLOOD_RX + BLOOD_W / 2) * np.cos(a), (BLOOD_RY + BLOOD_W / 2) * np.sin(a)], -1) + c
    inner = np.stack([(BLOOD_RX - BLOOD_W / 2) * np.cos(a), (BLOOD_RY - BLOOD_W / 2) * np.sin(a)], -1) + c
    return outer, inner


def compartments():
    """Stomach pouch, bloodstream loop and the short duct between them (line art)."""
    W = C.thin + 0.6
    st = poly(stomach_outline(), C.dose, W, close=True)
    o, i = blood_loop()
    loop = VGroup(poly(o, C.flow, W, close=True), poly(i, C.flow, W, close=True))
    top = STOMACH_C + [0, -0.95]
    bot = BLOOD_C + [0, BLOOD_RY + BLOOD_W / 2]
    duct = VGroup(Line(p3(top + [-0.12, 0]), p3(bot + [-0.12, 0]), color=C.frame, stroke_width=W),
                  Line(p3(top + [0.12, 0]), p3(bot + [0.12, 0]), color=C.frame, stroke_width=W))
    return VGroup(st, loop, duct)


class Molecules:
    """The pill's molecules: each has a seeded absorption time ~ Exp(k_a) and clearance time ~ Exp(k_e) after it.

    Same law as verify.py (2,000 such molecules track e^{tA} within 2%). `pos(t)` gives the yellow dots in the body
    (cleared ones are parked off screen so N stays fixed): in the stomach before absorption, a 0.4 s hop down the duct, then drifting round the blood loop.
    `t0` is when the pill lands; `sec_per_hour` maps model hours to screen seconds.
    """

    def __init__(self, n=400, seed=11, t0=0.0, sec_per_hour=1.2):
        Pm = CAST["pill"]
        self.ka, self.ke = -Pm[0, 0], -Pm[1, 1]
        g = rng(seed)
        self.t_abs = g.exponential(1 / self.ka, n)
        self.t_clr = self.t_abs + g.exponential(1 / self.ke, n)
        self.t0, self.k = t0, sec_per_hour
        P = stomach_outline()
        cand = STOMACH_C + (g.random((4 * n, 2)) - 0.5) * [2.6, 1.6]
        self.home = cand[inside_poly(P, cand)][:n] * 0.92 + STOMACH_C * 0.08
        self.phase = 2 * np.pi * g.random(n)
        self.lane = (g.random(n) - 0.5) * BLOOD_W * 0.6
        self.speed = 0.5 + 1.0 * g.random(n)            # rad/s round the loop, so they spread out

    def hours(self, t):
        return max(0.0, (t - self.t0) / self.k)

    def pos(self, t):
        h = self.hours(t)
        n = len(self.home)
        out = self.home.copy()
        absorbed = self.t_abs < h
        alive = self.t_clr > h
        # hop: 0.4 s screen time from the stomach bottom, down the duct, into the loop's top
        since = (h - self.t_abs) * self.k                     # screen seconds since absorption
        top = STOMACH_C + [0, -0.95]
        entry = BLOOD_C + [0, BLOOD_RY]
        u = np.clip(since / 0.4, 0, 1)
        u = u * u * (3 - 2 * u)
        u1, u2 = np.clip(2 * u, 0, 1)[:, None], np.clip(2 * u - 1, 0, 1)[:, None]
        hop = np.where(u[:, None] < 0.5, (1 - u1) * self.home + u1 * top, (1 - u2) * top + u2 * entry)
        ang = np.pi / 2 + self.speed * np.maximum(since - 0.4, 0) * np.sign(self.phase - np.pi)
        ring = BLOOD_C + np.stack([(BLOOD_RX + self.lane) * np.cos(ang), (BLOOD_RY + self.lane) * np.sin(ang)], -1)
        out = np.where(absorbed[:, None], np.where((since < 0.4)[:, None], hop, ring), out)
        out[~alive] = 99.0                                   # cleared: parked far off screen (constant N)
        return out

    def counts(self, t):
        h = self.hours(t)
        return int(np.sum(self.t_abs >= h)), int(np.sum((self.t_abs < h) & (self.t_clr > h)))

    @staticmethod
    def blood_fraction(hours):
        """The exact e^{tA} blood level (the teal curve), for comparison with the dots."""
        Pm = CAST["pill"]
        return np.array([(expm(h * Pm) @ [1.0, 0.0])[1] for h in np.atleast_1d(hours)])


# small icons (≤ 12 strokes each) for "rooms, circuits, buildings" and "today"
def rooms_icon(c, s=0.55, color=None):
    col = color or C.frame
    c = np.asarray(c, float)
    W = C.thin + 0.4
    house = poly([c + s * np.array(p) for p in ((-1.2, -0.7), (-1.2, 0.4), (1.2, 0.4), (1.2, -0.7))], col, W, close=True)
    wall = Line(p3(c + s * np.array([0, -0.7])), p3(c + s * np.array([0, 0.4])), color=col, stroke_width=W)
    heat = arrow(c + s * np.array([-0.55, -0.15]), c + s * np.array([0.55, -0.15]), C.gen, width=C.thin + 0.4, tip=0.12)
    return VGroup(house, wall, heat)


def circuit_icon(c, s=0.55, color=None):
    col = color or C.frame
    c = np.asarray(c, float)
    W = C.thin + 0.4
    loop = poly([c + s * np.array(p) for p in ((-1.1, -0.6), (-1.1, 0.6), (1.1, 0.6), (1.1, -0.6))], col, W, close=True)
    zig = poly([c + s * np.array([-0.45 + 0.15 * k, 0.6 + (0.15 if k % 2 else -0.15) * (0 < k < 6)]) for k in range(7)],
               col, W)
    cap = VGroup(Line(p3(c + s * np.array([1.0, -0.12])), p3(c + s * np.array([1.2, -0.12])), color=col, stroke_width=W + 1),
                 Line(p3(c + s * np.array([1.0, 0.12])), p3(c + s * np.array([1.2, 0.12])), color=col, stroke_width=W + 1))
    gap = Line(p3(c + s * np.array([1.1, -0.12])), p3(c + s * np.array([1.1, 0.12])), color=C.bg, stroke_width=W + 2)
    return VGroup(loop, gap, cap, zig)


def building_icon(c, s=0.55, sway=0.0, floors=4, color=None):
    """A tall building as a stack of floors; `sway` bends it like a cantilever (tip offset in units of s)."""
    col = color or C.frame
    c = np.asarray(c, float)
    W = C.thin + 0.4
    H = 0.62 * floors
    base = c + s * np.array([0, -H / 2])
    ys = np.linspace(0, H, floors + 1)
    off = sway * (ys / H) ** 2                        # cantilever: the top moves most
    L = [base + s * np.array([-0.45 + o, y]) for o, y in zip(off, ys)]
    R = [base + s * np.array([0.45 + o, y]) for o, y in zip(off, ys)]
    out = VGroup(poly(L, col, W), poly(R, col, W))
    for k in range(1, floors + 1):
        out.add(Line(p3(L[k]), p3(R[k]), color=col, stroke_width=W if k == floors else C.thin))
    out.add(Line(p3(base + s * np.array([-0.9, 0])), p3(base + s * np.array([0.9, 0])), color=col, stroke_width=W))
    return out


def satellite_icon(c, s=0.5):
    c = np.asarray(c, float)
    W = C.thin + 0.4
    box = Square(side_length=0.6 * s, color=C.frame, stroke_width=W).move_to(p3(c))
    panels = VGroup(*[Rectangle(width=0.9 * s, height=0.42 * s, color=C.frame, stroke_width=W).move_to(p3(c + [d * 0.85 * s, 0]))
                      for d in (-1, 1)])
    arms = VGroup(*[Line(p3(c + [d * 0.3 * s, 0]), p3(c + [d * 0.4 * s, 0]), color=C.frame, stroke_width=W) for d in (-1, 1)])
    dish = Arc(radius=0.18 * s, start_angle=PI / 4, angle=PI, color=C.frame, stroke_width=W).move_to(p3(c + [0, 0.42 * s]))
    return VGroup(box, panels, arms, dish)


def arm_icon(c, s=0.5, a1=0.9, a2=-0.7):
    c = np.asarray(c, float)
    W = C.thin + 0.6
    base = c + s * np.array([-0.4, -0.7])
    j1 = base + s * 1.1 * np.array([np.cos(a1), np.sin(a1)])
    j2 = j1 + s * 0.95 * np.array([np.cos(a1 + a2), np.sin(a1 + a2)])
    return VGroup(Line(p3(base + s * np.array([-0.35, 0])), p3(base + s * np.array([0.35, 0])), color=C.frame, stroke_width=W),
                  poly([base, j1, j2], C.frame, W),
                  *[Circle(radius=0.07 * s / 0.5, color=C.frame, stroke_width=C.thin).move_to(p3(q)) for q in (base, j1)],
                  poly([j2 + rot2(a1 + a2) @ (s * np.array([0.15, 0.12])), j2, j2 + rot2(a1 + a2) @ (s * np.array([0.15, -0.12]))],
                       C.frame, C.thin + 0.2))


def qwire_icon(c, s=0.5):
    c = np.asarray(c, float)
    W = C.thin + 0.4
    wires = VGroup(*[Line(p3(c + s * np.array([-1.1, y])), p3(c + s * np.array([1.1, y])), color=C.frame, stroke_width=W)
                     for y in (-0.35, 0.35)])
    gate = Square(side_length=0.5 * s, color=C.frame, stroke_width=W, fill_color=C.bg, fill_opacity=1).move_to(p3(c + s * np.array([-0.35, 0.35])))
    ctrl = VGroup(Dot(p3(c + s * np.array([0.45, 0.35])), radius=0.05, color=C.frame),
                  Line(p3(c + s * np.array([0.45, 0.35])), p3(c + s * np.array([0.45, -0.35])), color=C.frame, stroke_width=W),
                  Circle(radius=0.12 * s / 0.5, color=C.frame, stroke_width=W).move_to(p3(c + s * np.array([0.45, -0.35]))))
    ket = tex(r"|\psi\rangle", size=24, color=C.frame).next_to(p3(c + s * np.array([-1.1, 0])), LEFT, buff=0.08)
    return VGroup(wires, gate, ctrl, ket)


def lie_icon(c, s=0.6):
    """An infinitesimal arrow becoming a finite arc: an orange tangent at the start, a teal arc carrying it on."""
    c = np.asarray(c, float)
    arc = Arc(radius=s, start_angle=-PI / 2, angle=1.5 * PI, arc_center=p3(c), color=C.flow,
              stroke_width=C.thin + 0.8)
    base = c + [0, -s]
    return VGroup(arc, arrow(base, base + [0.75 * s, 0], C.gen, width=C.thin + 1.2, tip=0.16))


def pill_curve_icon(c, s=0.55):
    """The blood-level curve as a tiny teal plot (axes muted)."""
    c = np.asarray(c, float)
    o = c + s * np.array([-1.1, -0.6])
    hrs = np.linspace(0, 12, 60)
    b = Molecules.blood_fraction(hrs)
    pts = np.stack([o[0] + s * 2.2 * hrs / 12, o[1] + s * 1.6 * b / 0.63], -1)
    return VGroup(mini_axes(o, 2.2 * s, 1.3 * s), poly(pts, C.flow, C.thin + 0.6))


# ---------------------------------------------------------------- the globe (small wireframe; s05 map frame)
def _project(P, R=1.0, center=(0, 0), view_elev=0.35):
    """Orthographic view from slightly above the equator: (x, y, z) → screen (x, y) and depth (towards viewer)."""
    ce, se = np.cos(view_elev), np.sin(view_elev)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    # world z is the spin axis before tilt; viewer looks along -y'
    y2 = y * ce - z * se
    z2 = y * se + z * ce
    return np.stack([center[0] + R * x, center[1] + R * z2], -1), -y2


def globe_wire(center, R, theta, tilt=None, op=1.0, n_mer=12, n_par=5):
    """A wireframe globe turned by `theta` about its tilted axis: meridians and parallels, front bright and back
    dim, plus the purple axis. Rotation is expm(θK) for the unit axis (as in verify.py)."""
    tilt = CAST["tilt"] if tilt is None else tilt
    n = np.array([np.sin(tilt), 0.0, np.cos(tilt)])
    K = np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])
    Rm = expm(theta * K)
    # body frame: axis = body z, tilted by `tilt` about world y
    Ty = np.array([[np.cos(tilt), 0, np.sin(tilt)], [0, 1, 0], [-np.sin(tilt), 0, np.cos(tilt)]])
    curves = []
    a = np.linspace(0, 2 * PI, 72)
    for k in range(n_mer):
        lon = 2 * PI * k / n_mer
        lat = np.linspace(-PI / 2, PI / 2, 36)
        curves.append(np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], -1))
    for k in range(1, n_par + 1):
        lat = -PI / 2 + PI * k / (n_par + 1)
        curves.append(np.stack([np.cos(lat) * np.cos(a), np.cos(lat) * np.sin(a), np.full_like(a, np.sin(lat))], -1))
    out = VGroup()
    for cpts in curves:
        P = cpts @ Ty.T @ Rm.T
        xy, depth = _project(P, R, center)
        front = depth > 0
        for mask, o in ((front, 0.75), (~front, 0.18)):
            idx = np.where(mask)[0]
            if len(idx) < 2:
                continue
            runs = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)
            for r in runs:
                if len(r) >= 2:
                    out.add(poly(xy[r], C.globe, C.thin, opacity=o * op))
    ax = np.array([-1.35 * n, 1.35 * n])
    axy, _ = _project(ax, R, center)
    out.add(Line(p3(axy[0]), p3(axy[1]), color=C.eigen, stroke_width=C.thin + 0.8, stroke_opacity=op))
    return out


def plane(M, center=PLANE_C, unit=1.0, box=PLANE_BOX, opacity=1.0, basis=True, n=10):
    """The Classic grid moved by M, with the two basis arrows (green î, red ĵ) clipped to the box."""
    M = np.asarray(M, float)
    g = VGroup(grid_lines(M, center=center, unit=unit, box=box, n=n, opacity=opacity))
    if basis:
        for j, col in ((0, C.ihat), (1, C.jhat)):
            end, cut = clip_vec(center, unit * M[:, j], box)
            if cut:
                g.add(Line(p3(center), p3(end), color=col, stroke_width=C.stroke + 1, stroke_opacity=opacity))
            else:
                g.add(arrow(center, end, col, width=C.stroke + 1, opacity=opacity))
    return g


def backed(mob, buff=0.14, opacity=0.96):
    """A label on a black card, so it stays legible over grids, fields and particles."""
    return VGroup(BackgroundRectangle(mob, color=C.bg, fill_opacity=opacity, buff=buff), mob)


PORTRAITS = Path(__file__).parent / "assets" / "portraits"


def portrait(s, who, center, height, opacity=1.0, z=3, **kw):
    """A public-domain portrait (assets/portraits/<who>.png, 4:5 warm duotone) as an image layer, plus its thin
    frame (returned, for a ManimLayer). `opacity`, `pos`, `scale` may be Tracks."""
    c = np.asarray(center, float)
    s.image(PORTRAITS / f"{who}.png", height=height, pos=(float(c[0]), float(c[1])), opacity=opacity, z=z, **kw)
    return Rectangle(width=height * 0.8 + 0.06, height=height + 0.06, stroke_color=C.frame,
                     stroke_width=C.thin).move_to(p3(c))


def chapter_card(m, num, title, symbol, t0, hold=2.7, color=None):
    """The beat of black at a chapter cut: "chapter n" (sans), the title (small caps) and the chapter's symbol card,
    centred; in at t0, out by t0 + hold (before the chapter's first visual)."""
    sym = MathTex(symbol, font_size=110, color=color or C.flow)
    card = VGroup(lab(f"chapter {num}", 28, C.muted), Tex(r"\textsc{" + title + "}", font_size=46, color=C.text),
                  sym).arrange(DOWN, buff=0.35)
    rule = Line(p3((-2.2, 0)), p3((2.2, 0)), color=C.muted, stroke_width=C.thin).next_to(card[1], DOWN, buff=0.18)
    card.add(rule)
    card.move_to(ORIGIN)
    m.play(FadeIn(card[0], shift=0.1 * UP), FadeIn(card[1], shift=0.1 * UP), Create(rule), at=t0 + 0.25, dur=0.6)
    m.play(FadeIn(sym, scale=0.85), at=t0 + 0.6, dur=0.7)
    m.play(FadeOut(card, shift=0.1 * UP), at=t0 + hold - 0.4, dur=0.5)
    return card


# ---------------------------------------------------------------- ch4: the plane on the left, the numbers on the right
PC4 = np.array([-2.35, 0.0])                       # plane centre
BOX4 = (-7.3, -4.2, 2.3, 4.2)                      # plane box (the panel covers the rest)
PAN4 = (2.25, -3.85, 7.05, 3.85)                   # the numbers panel
PX4 = (PAN4[0] + PAN4[2]) / 2


def cycles(t0, t1, period, tmax, fade=0.5):
    """A looping flow time for growing flows: τ ramps 0 → tmax every `period` seconds inside [t0, t1], with an
    alpha that fades out before each reset and back in after it. Returns (tau, alpha) Tracks."""
    def tau(t):
        if t < t0:
            return 0.0
        u = min(t, t1) - t0
        return tmax * ((u % period) / period)

    def alpha(t):
        if t < t0 or t > t1:
            return 0.0
        u = (t - t0) % period
        return float(np.clip(min(u / fade, (period - u) / fade, (t1 - t) / fade), 0.0, 1.0))
    return Track(tau, active=[(t0, t1)]), Track(alpha, active=[(t0, t1)])


def stage4(mg, mp, t_in=None):
    """The ch4 plane grid (on mg, under the particles) and the numbers panel (on mp, over them); held, or faded in
    at t_in."""
    g = grid_lines(np.eye(2), tuple(PC4), 1.0, BOX4, n=12)
    pan = panel(*PAN4)
    if t_in is None:
        mg.add(g)
        mp.add(pan)
    else:
        mg.play(FadeIn(g), at=t_in, dur=0.8)
        mp.play(FadeIn(pan), at=t_in, dur=0.8)
    return g, pan


# ---------------------------------------------------------------- ch6: the particle Earth
_LAND_DIR = Path(__file__).parent / "assets" / "land"
TILT = CAST["tilt"]
AXIS_N = np.array([np.sin(TILT), 0.0, np.cos(TILT)])        # the spin axis, tilted from screen-vertical
K_AXIS = np.array([[0, -AXIS_N[2], AXIS_N[1]], [AXIS_N[2], 0, -AXIS_N[0]], [-AXIS_N[1], AXIS_N[0], 0]])
_TY = np.array([[np.cos(TILT), 0, np.sin(TILT)], [0, 1, 0], [-np.sin(TILT), 0, np.cos(TILT)]])
SPIN_RATE = 2 * PI / 12.0                                  # screen time: one turn every 12 s
THETA0 = np.radians(-110.0)                                # Africa and Europe face the viewer at the start
_ELEV = 0.35


@lru_cache(maxsize=None)
def land_points():
    return np.load(_LAND_DIR / "land_pts.npy").astype(float), np.load(_LAND_DIR / "ocean_pts.npy").astype(float)


def spin_theta(t, t0):
    """The globe's spin angle at time t (linear, starting at t0)."""
    return THETA0 + SPIN_RATE * (t - t0)


def body_to_world(theta):
    """Body frame (z = north) → world: tilt the axis to AXIS_N, then turn by θ about it (expm(θK), Rodrigues)."""
    return expm(theta * K_AXIS) @ _TY


def view_basis(pole=0.0):
    """Screen right, up and toward-viewer vectors; pole = 1 looks straight down the spin axis."""
    d0 = np.array([0.0, -np.cos(_ELEV), np.sin(_ELEV)])
    up0 = np.array([0.0, np.sin(_ELEV), np.cos(_ELEV)])
    tw = (1 - pole) * d0 + pole * AXIS_N
    tw /= np.linalg.norm(tw)
    up = up0 - (up0 @ tw) * tw
    up /= np.linalg.norm(up)
    return np.cross(up, tw), up, tw


def gproj(P, center, R, pole=0.0):
    """World points (…, 3) on the unit sphere scale → screen (…, 2) and depth (> 0 faces the viewer)."""
    rt, up, tw = view_basis(pole)
    P = np.asarray(P, float)
    c = np.asarray(center, float)
    return np.stack([c[0] + R * (P @ rt), c[1] + R * (P @ up)], -1), P @ tw


def latlon(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def globe_layers(s, theta, center, R, pole=None, alpha=1.0, z=1, **kw):
    """The particle Earth: bone land dots over a sparser steel-blue ocean shell, front bright, back dim.

    `theta`, `center`, `R`, `pole` are callables of t (screen time); positions are exact projections, so Manim
    overlays drawn with gproj(...) sit on the same globe."""
    land, sea = land_points()
    pole = pole or (lambda t: 0.0)
    al = track(alpha)

    def pts(src, front):
        def fn(t):
            W = src @ body_to_world(float(theta(t))).T
            xy, d = gproj(W, center(t), float(R(t)), float(pole(t)))
            keep = d > 0 if front else d <= 0
            return np.where(keep[:, None], xy, 99.0)
        return fn
    s.add(PointsLayer(pts(sea, False), color=C.globe, size=1.6, glow=0.0, alpha=al * 0.12, additive=False, z=z, **kw))
    s.add(PointsLayer(pts(land, False), color=C.land, size=1.8, glow=0.0, alpha=al * 0.12, additive=False, z=z + 0.01,
                      **kw))
    s.add(PointsLayer(pts(sea, True), color=C.globe, size=2.0, glow=0.0, alpha=al * 0.7, additive=False, z=z + 0.02,
                      **kw))
    s.add(PointsLayer(pts(land, True), color=C.land, size=2.6, glow=0.0, alpha=al, additive=False, z=z + 0.03, **kw))


def sphere_curve(points, center, R, pole, color, width, op=1.0, back=0.2):
    """A curve on the globe (world points), front part bright, back part dim."""
    xy, d = gproj(points, center, R, pole)
    out = VGroup()
    for mask, o in ((d > 0, op), (d <= 0, op * back)):
        idx = np.where(mask)[0]
        if len(idx) < 2:
            continue
        for r in np.split(idx, np.where(np.diff(idx) != 1)[0] + 1):
            if len(r) >= 2:
                out.add(poly(xy[r], color, width, opacity=o))
    return out
