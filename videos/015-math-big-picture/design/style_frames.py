"""Style frames for video 015, "Fundamentals of Math: The Big Picture": 8 stills at 1920×1080, rendered through aion.

    uv run python videos/015-math-big-picture/design/style_frames.py         # all → design/style_frames/*.png + refs
    uv run python videos/015-math-big-picture/design/style_frames.py 3 7     # only frames 3 and 7

Each frame is an `@scene(0, 10)` rendered with `sd.comp((1920, 1080), 30).frame(t, round(t * 30))`, so it goes through
the same theme, LaTeX, Manim rasteriser and GPU compositor as the video. Every value on screen is computed here
(numpy): Buffon's needles from one seeded stream (seed 1777; row k is throw k for any n), the fractions near π,
e^{iθ} on the unit circle, V − E + F from the drawn meshes, Archimedes' rings. One process per frame (2 cores,
< 1 GB free RAM); a frame takes 5–15 s.

    1 cold open    last line: needles slide to the centre in angle order, two pens trace THE circle; HUD 2N/H = 3.1416
    2 Ch1          C = {(x, y) : x² + y² = 25}: (3, 4) on (joins the set), (2, 4) inside, (4, 4) outside
    3 Ch2          π in a gap between fractions (22/7, then 355/113 under a ×7 500 zoom); the inscribed square, side √2
    4 Ch3          e^{iπ/3} · e^{iπ/6} = e^{iπ/2} = i as rotation arcs on the unit circle; key-idea panel
    5 Ch4          a PyVista torus with its two loops beside the V − E + F counts
    6 Ch5          Archimedes' rings unrolling into a triangle; takeaway bar with dA/dr = 2πr
    7 Ch6          the floor (skia), throws as points (θ, x) under x ≤ sin θ, P = 2/π, the estimate converging to π
    8 Ch7          the fully lit map: all fifteen chords, e^{iπ} + 1 = 0 at the hub
    9, 10          references (design/components_card.png, design/components.png): the chapter card, the furniture
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

DESIGN = Path(__file__).resolve().parent
VIDEO = DESIGN.parent
REPO = VIDEO.parent.parent
OUT = DESIGN / "style_frames"
sys.path.insert(0, str(VIDEO))

W, H, FPS, T_STILL = 1920, 1080, 30, 5.0
PX = 135.0                      # px per world unit at 1080p
XW, YH = 64 / 9, 4.0            # half frame (world units)
SAFE = 0.71                     # text-safe inset (DS safe-margin, 96 px)
MAP_R, NODE_R, HUB_R = 2.75, 0.4, 1.375  # hub = R/2: skip-one chords touch it
FILL, REGION, DIM = 0.06, 0.1, 0.3  # set tints, a shaded region, old lines (linear-light compositing)
MINI_C, MINI_R = (6.05, 3.0), 0.3
BOARD = 0.6                     # floorboard spacing = needle length (Buffon with l = d)
SEED = 1777                     # the needle stream (Buffon's year)

NAMES_OUT = {1: "01_cold_open", 2: "02_ch1_set", 3: "03_ch2_pi_gap", 4: "04_ch3_rotation", 5: "05_ch4_torus",
             6: "06_ch5_rings", 7: "07_ch6_needles", 8: "08_map_lit",
             9: "../components_card", 10: "../components"}   # references, kept outside style_frames/


# ------------------------------------------------------------------------------------------------ setup
def _import_aion():
    """Activate video 015's theme and pull aion's names (Manim included) into this module."""
    from aion.render.project import load_video

    load_video("015", (W, H), FPS, only=["__none__"])           # theme on, no scenes imported
    import aion
    from aion.components.linalg import grid_lines, panel
    from aion.render import scenes as scene_mod

    import theme as th

    g = globals()
    for k in aion.__all__:
        g.setdefault(k, getattr(aion, k))
    g.update(grid_lines=grid_lines, panel=panel, scene_mod=scene_mod, PILLARS=th.PILLARS, GLYPHS=th.GLYPHS,
             NAMES=th.NAMES)


# ---------------------------------------------------------------------------------------------- helpers
def tex(s, size=48, color=None):
    return MathTex(s, font_size=size, color=color or C.text)  # noqa: F821


def sans(s, size=32, color=None):
    return Tex(r"\textsf{" + s + "}", font_size=size, color=color or C.text)  # noqa: F821


def caps(s, size=32, color=None):
    return Tex(r"\textsc{" + s + "}", font_size=size, color=color or C.text)  # noqa: F821


def P3(x, y):
    return np.array([float(x), float(y), 0.0])  # noqa: F821


def hue(p):
    return getattr(C, p)  # noqa: F821


def rgb255(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tint(color, a):
    """`color` at opacity `a` over black, mixed in linear light (as aion composites layers), as one solid hex.

    Use it for a tinted disk that must also hide what lies under it. Inside one Manim layer Cairo blends in sRGB, so a
    translucent fill over another shape of the same layer comes out far darker (about 11× at a = 0.06) than the same
    fill over the stage, which aion blends in linear light.
    """
    c = np.array(rgb255(color)) / 255.0  # noqa: F821
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4) * a  # noqa: F821
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)  # noqa: F821
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in srgb)


def node_xy(k, R=MAP_R, turn=0.0, c=(0.0, 0.0)):
    """Map node k (PILLARS order) on a ring of radius R; Foundations at 6 o'clock, then clockwise; `turn` in degrees."""
    a = math.radians(-90 - 60 * k + turn)
    return P3(c[0] + R * math.cos(a), c[1] + R * math.sin(a))


def gradient_line(a, b, ca, cb, width=2.4, opacity=0.85):
    ln = Line(a, b, stroke_width=width)  # noqa: F821
    ln.set_stroke(color=[ca, cb], width=width, opacity=opacity)
    d = (b - a) / np.linalg.norm(b - a)  # noqa: F821
    ln.set_sheen_direction(d)
    return ln


def map_of_math(lit=(), links=(), turn=0.0, c=(0.0, 0.0), R=MAP_R, nr=NODE_R, glyphs=True, labels=True,
                hub=None, glyph_size=44, label_size=32):
    """The Map of Math: a track, six nodes, lit links (ring arcs between neighbours, chords otherwise), an optional hub.

    lit: pillars whose node is lit (glyph and name shown in its hue). links: (p, q) pairs drawn as two-hue gradients.
    """
    g = VGroup()  # noqa: F821
    links = {tuple(sorted((PILLARS.index(p), PILLARS.index(q)))) for p, q in links}  # noqa: F821
    trim = math.degrees(2 * math.asin((nr + 0.05) / (2 * R)))
    for k in range(6):
        k2 = (k + 1) % 6
        a1 = -90 - 60 * k + turn
        arc = Arc(radius=R, start_angle=math.radians(a1 - trim), angle=-math.radians(60 - 2 * trim),  # noqa: F821
                  arc_center=P3(*c))
        if tuple(sorted((k, k2))) in links:
            p, q = PILLARS[k], PILLARS[k2]  # noqa: F821
            arc.set_stroke(color=[hue(p), hue(q)], width=2.4, opacity=0.9)
            arc.set_sheen_direction((node_xy(k2, R, turn, c) - node_xy(k, R, turn, c)))
        else:
            arc.set_stroke(C.map_off, width=1.6)  # noqa: F821
        g.add(arc)
    for i, j in sorted(links):
        if (j - i) % 6 in (1, 5):
            continue
        a, b = node_xy(i, R, turn, c), node_xy(j, R, turn, c)
        d = (b - a) / np.linalg.norm(b - a)  # noqa: F821
        g.add(gradient_line(a + d * (nr + 0.05), b - d * (nr + 0.05), hue(PILLARS[i]), hue(PILLARS[j])))  # noqa: F821
    if hub is not None:
        g.add(hub)
    for k, p in enumerate(PILLARS):  # noqa: F821
        pos = node_xy(k, R, turn, c)
        on = p in lit
        g.add(Circle(radius=nr, stroke_color=hue(p) if on else C.map_off, stroke_width=3.0 if on else 2.0,  # noqa: F821
                     fill_color=tint(hue(p), FILL) if on else C.bg, fill_opacity=1.0).move_to(pos))  # noqa: F821
        if on and glyphs:
            gl = tex(GLYPHS[p], glyph_size, hue(p))  # noqa: F821
            if gl.width > 1.5 * nr:
                gl.scale_to_fit_width(1.5 * nr)
            g.add(gl.move_to(pos))
        if on and labels:
            lab = caps(NAMES[p], label_size, hue(p))  # noqa: F821
            a = math.radians(-90 - 60 * k + turn)
            if abs(math.sin(a)) > 0.9:                      # 12 and 6 o'clock: beside the node, clear of the track
                up = math.sin(a) > 0
                lab.move_to(pos + RIGHT * (nr + 0.08) + (UP if up else DOWN) * 0.55 * nr,  # noqa: F821
                            aligned_edge=LEFT + (DOWN if up else UP))  # noqa: F821
            else:                                           # the four side nodes: straight out, left or right
                d = RIGHT if math.cos(a) > 0 else LEFT  # noqa: F821
                lab.next_to(pos + d * nr, d, buff=0.16)
            g.add(lab)
    return g


def minimap(lit, current, c=MINI_C, r=MINI_R):
    """Progress mini-map (top-right): the ring turned so the current pillar sits at 6 o'clock; dots only, no glyphs."""
    k0 = PILLARS.index(current)  # noqa: F821
    g = VGroup(Circle(radius=r, stroke_color=C.map_off, stroke_width=1.6).move_to(P3(*c)))  # noqa: F821
    for k, p in enumerate(PILLARS):  # noqa: F821
        pos = node_xy(k, r, 60 * k0, c)
        if p in lit:
            g.add(Dot(pos, radius=0.062, color=hue(p)))  # noqa: F821
        else:
            g.add(Dot(pos, radius=0.045, color=C.map_off))  # noqa: F821
    g.add(Circle(radius=0.125, stroke_color=hue(current), stroke_width=2.2).move_to(node_xy(k0, r, 60 * k0, c)))  # noqa: F821
    return g


def lower_third(name, year):
    """Small-caps lower third, `name · year`, on the safe margin bottom-left, with a short muted rule above."""
    t = Tex(r"\textsc{" + name + r"}\enspace$\cdot$\enspace\textsc{" + year + "}", font_size=34, color=C.text)  # noqa: F821
    t.move_to(P3(-XW + SAFE, -YH + SAFE), aligned_edge=LEFT + DOWN)  # noqa: F821
    a = t.get_corner(UL) + UP * 0.16  # noqa: F821
    rule = Line(a, a + RIGHT * 0.9, stroke_color=C.muted, stroke_width=2.0)  # noqa: F821
    return VGroup(rule, t)  # noqa: F821


def tracker(lit=("change", "structure", "quantity")):
    """The e · i · π tracker (loop L2, Ch3 to Ch7): three small rings top-left on the safe margin. A slot shows its
    glyph in the pillar hue once it is met; an empty slot is a map_off ring."""
    g = VGroup()  # noqa: F821
    for j, (glyph, p) in enumerate((("e", "change"), ("i", "structure"), (r"\pi", "quantity"))):
        c = P3(-XW + SAFE + 0.25 + 0.66 * j, YH - SAFE - 0.25)
        on = p in lit
        g.add(Circle(radius=0.25, stroke_color=hue(p) if on else C.map_off, stroke_width=2.2,  # noqa: F821
                     fill_color=C.bg, fill_opacity=1.0).move_to(c))  # noqa: F821
        if on:
            g.add(tex(glyph, 36, hue(p)).move_to(c))
    return g


def backed(mob, pad=0.06):
    """A label with a black backing so grid lines never cut through its glyphs."""
    bg = Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_width=0, fill_color=C.bg,  # noqa: F821
                   fill_opacity=1.0).move_to(mob.get_center())
    return VGroup(bg, mob)  # noqa: F821


def dim(mob, k=None):
    """Old lines and rows: scale every stroke and fill opacity by k (default DIM). Never deletes, never refills."""
    k = DIM if k is None else k
    for sm in mob.family_members_with_points():
        so, fo = sm.get_stroke_opacity(), sm.get_fill_opacity()
        sm.set_stroke(opacity=so * k, family=False)
        sm.set_fill(opacity=fo * k, family=False)
    return mob


def buffon(n, seed=SEED):
    """Buffon trials with needle length = board spacing = 1: distance x of the centre to the nearest line, angle θ."""
    u = np.random.default_rng(seed).random((n, 2))  # noqa: F821  (row k is throw k for every n: a true stream)
    x, th = 0.5 * u[:, 0], np.pi * u[:, 1]  # noqa: F821
    return x, th, x <= 0.5 * np.sin(th)  # noqa: F821


def skia_canvas(box, draw):
    """Draw with skia into a transparent RGBA array covering world box (x0, y0, x1, y1); returns an ArrayLayer kw set."""
    import skia

    x0, y0, x1, y1 = box
    w, h = int(round((x1 - x0) * PX)), int(round((y1 - y0) * PX))
    surf = skia.Surface(w, h)
    canvas = surf.getCanvas()
    canvas.clear(skia.ColorTRANSPARENT)

    def T(x, y):
        return (x - x0) * PX, (y1 - y) * PX

    draw(skia, canvas, T)
    # premultiplied straight from skia: un-premultiplying faint strokes would quantise their colour
    rgba = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    return dict(rgba=rgba, height=y1 - y0, pos=((x0 + x1) / 2, (y0 + y1) / 2), premultiplied=True)


def stroke_paint(skia, color, alpha=1.0, width=3.0):
    r, g, b = rgb255(color)
    return skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                      StrokeCap=skia.Paint.kRound_Cap, Color=skia.Color(r, g, b, int(round(255 * alpha))))


def crosses(cy, th, d=BOARD):
    """Does a needle of length d centred at height cy (boards at multiples of d) cross a line?"""
    half = 0.5 * d * np.abs(np.sin(th))  # noqa: F821
    return np.floor((cy - half) / d) != np.floor((cy + half) / d)  # noqa: F821


# ----------------------------------------------------------------------------------------------- frames
def floor_layout(n, box, seed=SEED + 1):
    """Place the first n throws of the needle stream on a floor inside box: same (x, θ) as the maths, so a needle
    crosses on screen exactly when x ≤ ½ sin θ. Placement (which board, which side, how far along) has its own seed."""
    x0, y0, x1, y1 = box
    xs, th, hit = buffon(n)
    rg = np.random.default_rng(seed)
    lines_y = np.arange(math.ceil(y0 / BOARD) * BOARD, y1 + 1e-9, BOARD)
    k = rg.integers(0, len(lines_y), n)
    side = rg.choice((-1.0, 1.0), n)
    cx = rg.uniform(x0, x1, n)
    cy = lines_y[k] + side * xs * BOARD                     # x is in board units (d = 1) → world
    return cx, cy, th, hit, lines_y


def f1(s, m):
    """Cold open, last line: every needle slides to the centre keeping its angle; the tips trace the circle.

    Needles leave in order of angle, so the two tips of each needle land at θ and θ + π: two pens draw the circle
    in half a turn. On the way each needle stretches from the board width to the circle's diameter; once it lands
    it fades, so only a short fan of recent needles trails each pen. The HUD stops where the seeded stream first
    reads 3.1416 (throw 30 331).
    """
    n_lock = 30_331                                          # the stream first reads 2N/H = 3.1416 here (checked)
    _, _, h_all = buffon(n_lock)
    hits = int(h_all.sum())
    est = 2 * n_lock / hits
    assert f"{est:.4f}" == "3.1416", est

    # HUD readout first (the floor is masked under it): CM sans, tabular figures (CM digits share one width)
    def row(label, value, size=34, vcol=None):
        t = Tex(r"\makebox[5.3em][l]{\textsf{" + label + "}}", r"\makebox[3.6em][r]{\textsf{" + value + "}}",
                font_size=size, color=C.text)
        t[0].set_color(C.muted)
        t[1].set_color(vcol or C.text)
        return t

    def grouped(n):
        return f"{n:,}".replace(",", r"\,")

    hud = VGroup(row("throws", grouped(n_lock)), row("crossings", grouped(hits)),
                 row("2N\\,/\\,H", f"{est:.4f}", vcol=C.quantity))
    x_left, base0, step = -XW + SAFE, YH - SAFE - 0.26, 0.52   # rows sit on fixed baselines (digits' bottoms)
    for k, r_ in enumerate(hud):
        r_.shift(P3(x_left - r_.get_left()[0], base0 - k * step - r_[1].get_bottom()[1]))
    pi = tex(r"\approx \pi", 40, C.quantity).next_to(hud[2], RIGHT, buff=0.2)
    pi.shift(UP * (hud[2][1].get_bottom()[1] - pi[0][-1].get_bottom()[1]))
    readout = VGroup(hud, pi)
    hx0, hy0 = readout.get_corner(DL)[:2]
    hx1, hy1 = readout.get_corner(UR)[:2]

    box = (-XW - 0.4, -YH - 0.4, XW + 0.4, YH + 0.4)
    n_show = 420                                             # a sample of the floor; the scene throws thousands
    cx, cy, th, hit, lines_y = floor_layout(n_show, box)
    sweep = 0.84 * np.pi                                     # directions already gathered: θ < sweep
    band = 0.1 * np.pi                                       # needles in flight: sweep ≤ θ < sweep + band
    tail = 0.3 * np.pi                                       # a landed needle fades out over this much sweep
    L0, L1 = BOARD, 2 * HUB_R
    r, g, b = rgb255(C.uncertainty)

    def draw(skia, cv, T):
        crack = stroke_paint(skia, C.map_off, 0.4, 2.0)      # the floor, dimmed to 40 % at 'no circle'
        for y in lines_y:
            cv.drawLine(*T(box[0], y), *T(box[2], y), crack)
        for i in np.argsort(-th):                            # late needles first, so the gathered ones sit on top
            t, x, y, c = th[i], cx[i], cy[i], hit[i]
            a_floor = 0.42 if c else 0.24                    # crossing needles a little brighter
            if t >= sweep + band:                            # still on the floor
                e, a_tip = 0.0, a_floor
            elif t >= sweep:                                 # in flight
                f = 1 - (t - sweep) / band
                e = f * f * (3 - 2 * f)
                a_tip = a_floor + (0.75 - a_floor) * e
            else:                                            # landed: fades out behind the pens, smoothly to 0
                q = (sweep - t) / tail
                if q >= 1:
                    continue
                e, a_tip = 1.0, 0.85 * (1 - q) ** 2
            px, py = x * (1 - e), y * (1 - e)
            half = 0.5 * (L0 + (L1 - L0) * e ** 3)            # stretches late, as it arrives
            dx, dy = half * math.cos(t), half * math.sin(t)
            p0, p1 = T(px - dx, py - dy), T(px + dx, py + dy)
            mid = a_tip * (1 - 0.97 * e)                     # the middle fades as the needle reaches the centre
            paint = stroke_paint(skia, C.uncertainty, 1.0, 3.0)
            paint.setShader(skia.GradientShader.MakeLinear(
                [skia.Point(*p0), skia.Point(*p1)],
                [skia.Color(r, g, b, int(255 * a_tip)), skia.Color(r, g, b, int(255 * mid)),
                 skia.Color(r, g, b, int(255 * a_tip))], [0.0, 0.5, 1.0]))
            cv.drawLine(*p0, *p1, paint)

    kw = skia_canvas(box, draw)
    yy, xx = np.mgrid[0:kw["rgba"].shape[0], 0:kw["rgba"].shape[1]]
    wx, wy = box[0] + xx / PX, box[3] - yy / PX              # world coordinates of each pixel
    pad, soft = 0.14, 0.45                                   # clear under the HUD, soft edge around it
    ddx = np.maximum(np.maximum(hx0 - pad - wx, wx - hx1 - pad), 0)
    ddy = np.maximum(np.maximum(hy0 - pad - wy, wy - hy1 - pad), 0)
    k_ = np.clip(np.hypot(ddx, ddy) / soft, 0, 1)
    kw["rgba"] = (kw["rgba"] * (k_ * k_ * (3 - 2 * k_))[..., None]).astype(np.uint8)   # premultiplied: all four
    s.add(ArrayLayer(kw.pop("rgba"), z=-2, **kw))

    # the circle so far: two arcs, from θ = 0 and from θ = π, each swept through `sweep`; a pen at each front
    m.add(map_of_math(lit=(), glyphs=False, labels=False))
    for a0 in (0.0, np.pi):
        m.add(Arc(radius=HUB_R, start_angle=a0, angle=sweep, stroke_color=C.circle, stroke_width=5))
        m.add(Dot(P3(HUB_R * math.cos(a0 + sweep), HUB_R * math.sin(a0 + sweep)), radius=0.075, color=C.circle))
    m.add(readout)


def f2(s, m):
    """Ch1 Foundations: the circle as a set; three test points split the plane into inside, on and outside."""
    pc, u, rad = P3(-3.85, -0.2), 0.5, 5
    m.add(grid_lines(np.eye(2), center=(pc[0], pc[1]), unit=u, box=(-6.62, -3.35, -0.75, 3.05), n=12, minor=2))
    m.add(Circle(radius=rad * u, stroke_width=0, fill_color=C.foundations, fill_opacity=FILL).move_to(pc))
    m.add(Circle(radius=rad * u, stroke_color=C.circle, stroke_width=5).move_to(pc))
    m.add(backed(tex("5", 32, C.muted)).next_to(pc + u * P3(rad, 0), DR, buff=0.08))
    m.add(backed(tex("5", 32, C.muted)).next_to(pc + u * P3(0, rad), UL, buff=0.08))
    for (a, b), side, buff in (((3, 4), UP, 0.42), ((2, 4), LEFT, 0.14), ((4, 4), RIGHT, 0.14)):
        p = pc + u * P3(a, b)
        col = C.foundations if a * a + b * b == rad * rad else C.text   # the verdict: only 'on' joins the set C
        m.add(Dot(p, radius=0.09, color=col, stroke_color=C.bg, stroke_width=2.5))
        m.add(backed(tex(f"({a},{b})", 34, col), 0.04).next_to(p, side, buff=buff))
    m.add(backed(sans("inside", 30, C.text)).move_to(pc + u * P3(-1.4, -2.6)))
    m.add(backed(sans("on", 30, C.circle)).move_to(pc + u * 5.75 * P3(math.cos(2.15), math.sin(2.15))))
    m.add(backed(sans("outside", 30, C.text)).move_to(P3(-1.75, -2.95)))

    hero = Eqn(r"C = \{\,(x,y) : x^2+y^2=25\,\}", size=52,
               colors={"C": C.circle, r"\{": C.foundations, r"\}": C.foundations, ":": C.foundations,
                       "x^2+y^2=25": C.circle})
    left = -0.3
    hero.move_to(P3(left, 1.45), aligned_edge=LEFT)
    m.add(hero)
    rows = [(r"(3,4)", r"\in", r"3^2+4^2 = 25"), (r"(2,4)", r"\notin", r"2^2+4^2 = 20 < 25"),
            (r"(4,4)", r"\notin", r"4^2+4^2 = 32 > 25")]
    for i, (pt, rel, chk) in enumerate(rows):
        e = Eqn(pt + r"\;" + rel + r"\;C \qquad " + chk, size=40,
                colors={pt: C.foundations if rel == r"\in" else C.text, rel: C.foundations, "C": C.circle})
        e.move_to(P3(left + 0.05, 0.15 - 1.0 * i), aligned_edge=LEFT)
        if i < len(rows) - 1:
            dim(e)                                          # old lines dim, never deleted
        m.add(e)
    m.add(minimap({"foundations"}, "foundations"))


def f3(s, m):
    """Ch2 Quantity: π sits in a gap between fractions; even 355/113 misses. The square in the circle has side √2."""
    from fractions import Fraction

    # left: the unit circle with its inscribed square
    oc, R = P3(-4.75, 0.55), 1.55
    m.add(Circle(radius=R, stroke_color=C.circle, stroke_width=5).move_to(oc))
    sq = [oc + R * P3(math.cos(a), math.sin(a)) for a in np.radians([45, 135, 225, 315])]
    m.add(Polygon(*sq, stroke_color=C.quantity, stroke_width=4, fill_opacity=0))
    m.add(Line(oc, sq[0], stroke_color=C.text, stroke_width=2.4), Dot(oc, radius=0.05, color=C.text))
    m.add(tex("1", 36).move_to((oc + sq[0]) / 2 + P3(0.22, -0.2)))
    m.add(tex(r"\sqrt{2}", 40, C.quantity).next_to((sq[0] + sq[1]) / 2, DOWN, buff=0.14))
    sub = Eqn(r"\sqrt{2} \neq \frac{p}{q}", size=48, colors={r"\sqrt{2}": C.quantity})
    m.add(sub.move_to(oc + P3(0, -2.45)))

    # right: two number lines, the second a ×7500 zoom around π
    xa, xb = -1.45, 6.05

    def line(y, lo, hi, qmax, tick_h):
        X = lambda v: xa + (v - lo) / (hi - lo) * (xb - xa)  # noqa: E731
        g = VGroup(Line(P3(xa, y), P3(xb, y), stroke_color=C.text, stroke_width=2.4))
        fr = sorted({Fraction(p, q) for q in range(1, qmax + 1)
                     for p in range(math.ceil(lo * q), math.floor(hi * q) + 1) if lo <= p / q <= hi})
        for f in fr:                                        # tick height falls with the denominator
            h = tick_h * min(1.0, 0.3 + 0.7 * math.sqrt(7 / f.denominator))
            g.add(Line(P3(X(float(f)), y), P3(X(float(f)), y + h), stroke_color=C.text, stroke_width=2.0))
        return g, X, fr

    def pi_mark(X, y):
        x = X(math.pi)
        return VGroup(Line(P3(x, y - 0.24), P3(x, y + 0.24), stroke_color=C.quantity, stroke_width=4.5),
                      tex(r"\pi", 44, C.quantity).next_to(P3(x, y - 0.24), DOWN, buff=0.1))

    y1, lo1, hi1 = 1.25, 3.13, 3.15
    g1, X1, fr1 = line(y1, lo1, hi1, 40, 0.3)
    m.add(g1, pi_mark(X1, y1))
    for v in (3.13, 3.14, 3.15):
        m.add(Line(P3(X1(v), y1 - 0.13), P3(X1(v), y1), stroke_color=C.muted, stroke_width=2.0))
        m.add(tex(f"{v:.2f}", 30, C.muted).next_to(P3(X1(v), y1 - 0.13), DOWN, buff=0.1))
    m.add(tex(r"q \le 40", 30, C.muted).next_to(P3(xa, y1 + 0.08), LEFT, buff=0.22))
    x227 = X1(22 / 7)
    m.add(tex(r"\tfrac{22}{7}", 36).next_to(P3(x227, y1 + 0.3), UP, buff=0.1))

    c2, w2 = (math.pi + 355 / 113) / 2, (hi1 - lo1) / 7500
    y2 = -1.75
    g2, X2, fr2 = line(y2, c2 - w2 / 2, c2 + w2 / 2, 120, 0.3)
    assert fr2 == [Fraction(355, 113)], fr2                 # nothing else with q ≤ 120 comes this close
    m.add(g2, pi_mark(X2, y2))
    x355 = X2(355 / 113)
    m.add(tex(r"\tfrac{355}{113}", 36).next_to(P3(x355, y2 + 0.3), UP, buff=0.1))
    m.add(tex(r"q \le 120", 30, C.muted).next_to(P3(xa, y2 + 0.08), LEFT, buff=0.22))
    xp = X1(math.pi)                                        # the lens: π's neighbourhood → the zoomed line
    for xe in (xa, xb):
        m.add(DashedLine(P3(xp, y1 - 0.72), P3(xe, y2 + 0.42), dash_length=0.08, stroke_color=C.muted,
                         stroke_width=1.6, stroke_opacity=0.8))
    m.add(tex(r"\times 7500", 30, C.muted).move_to(P3(5.7, -0.45)))
    m.add(lower_third("Zu Chongzhi", "c. 480"))
    m.add(minimap({"foundations", "quantity"}, "quantity"))


def f4(s, m):
    """Ch3 Structure: multiplying unit complex numbers adds their angles."""
    oc, u = P3(-3.15, -0.6), 2.4
    m.add(grid_lines(np.eye(2), center=(oc[0], oc[1]), unit=u / 2, box=(-6.62, -3.55, 0.2, 2.5), n=8, minor=2))
    m.add(Circle(radius=u, stroke_color=C.circle, stroke_width=5).move_to(oc))
    for k in range(6):                                      # the sixth turns: one map turn each
        d = P3(math.cos(k * np.pi / 3), math.sin(k * np.pi / 3))
        m.add(Line(oc + d * (u - 0.11), oc + d * (u + 0.11), stroke_color=C.structure, stroke_width=3))
    a1, a2 = np.pi / 3, np.pi / 2
    m.add(Arc(radius=u, start_angle=0.0, angle=a1 - 0.03, arc_center=oc, stroke_color=C.structure, stroke_width=10))
    m.add(Arc(radius=u, start_angle=a1 + 0.03, angle=a2 - a1 - 0.03, arc_center=oc, stroke_color=C.structure,
              stroke_width=10))
    m.add(Arc(radius=0.6, start_angle=0.0, angle=a1, arc_center=oc, stroke_color=C.structure, stroke_width=3))
    m.add(Arc(radius=0.85, start_angle=a1, angle=a2 - a1, arc_center=oc, stroke_color=C.structure, stroke_width=3))
    m.add(backed(tex(r"\tfrac{\pi}{3}", 34, C.structure)).move_to(oc + 0.98 * P3(math.cos(a1 / 2), math.sin(a1 / 2))))
    m.add(backed(tex(r"\tfrac{\pi}{6}", 34, C.structure)).move_to(oc + 1.22 * P3(math.cos(1.33), math.sin(1.33))))
    z = [np.exp(0j), np.exp(1j * a1), np.exp(1j * a2)]
    for k, w in enumerate(z):
        p = oc + u * P3(w.real, w.imag)
        m.add(Line(oc, p, stroke_color=C.text, stroke_width=2.2))
        m.add(Dot(p, radius=0.09, color=C.text if k == 0 else C.structure))
    m.add(backed(tex("1", 36)).next_to(oc + u * P3(1, 0), DR, buff=0.1))
    m.add(backed(tex(r"e^{i\pi/3}", 38, C.structure)).next_to(oc + u * P3(z[1].real, z[1].imag), UR, buff=0.1))
    m.add(backed(tex("i", 38, C.structure)).next_to(oc + u * P3(0, 1), UL, buff=0.12))

    hero = Eqn(r"e^{i\pi/3}\cdot e^{i\pi/6} = e^{i\pi/2} = i", size=52,
               colors={r"e^{i\pi/3}": C.structure, r"e^{i\pi/6}": C.structure, r"e^{i\pi/2}": C.structure,
                       "= i": C.text})
    hero[-1][-1].set_color(C.structure)
    hero.move_to(P3(3.55, 1.55))
    m.add(hero)
    m.add(dim(tex(r"\tfrac{\pi}{3}+\tfrac{\pi}{6}=\tfrac{\pi}{2}", 44)).move_to(P3(3.55, 0.45)))
    x0, y0, x1, y1 = 0.95, -3.1, 6.4, -0.6
    m.add(panel(x0, y0, x1, y1))
    m.add(caps("key idea", 28, C.muted).move_to(P3(x0 + 0.25, y1 - 0.3), aligned_edge=LEFT))
    key = Eqn(r"e^{ia}\,e^{ib} = e^{i(a+b)}", size=48,
              colors={r"e^{ia}": C.structure, r"e^{ib}": C.structure, r"e^{i(a+b)}": C.structure})
    m.add(key.move_to(P3((x0 + x1) / 2, y1 - 1.05)))
    m.add(sans("multiplying adds angles", 32).move_to(P3((x0 + x1) / 2, y0 + 0.5)))
    m.add(tracker(), minimap({"foundations", "quantity", "structure"}, "structure"))


TORUS = {}


def torus_render(px_w=900, px_h=660, ss=2):
    """PyVista off-screen: a translucent torus, its iso-curve mesh (teal) and its two loops (warm white)."""
    import pyvista as pv
    from PIL import Image

    R, r, nu, nv = 1.0, 0.42, 16, 8
    pv.OFF_SCREEN = True
    pl = pv.Plotter(off_screen=True, window_size=(px_w * ss, px_h * ss))
    pl.set_background("black")
    pl.enable_depth_peeling(number_of_peels=8)

    def surf(u, v, grow=1.0):
        return np.stack([(R + grow * r * np.cos(v)) * np.cos(u), (R + grow * r * np.cos(v)) * np.sin(u),
                         grow * r * np.sin(v)], -1)

    smooth = pv.ParametricTorus(ringradius=R, crosssectionradius=r, u_res=120, v_res=60, w_res=60)
    pl.add_mesh(smooth, color=C.space, opacity=0.14, smooth_shading=True, ambient=0.3, diffuse=0.5, specular=0.08)
    tt = np.linspace(0, 2 * np.pi, 241)
    for i in range(nu):                                     # meridians (around the tube)
        pts = surf(np.full_like(tt, 2 * np.pi * i / nu), tt, 1.004)
        pl.add_mesh(pv.lines_from_points(pts), color=C.space, line_width=1.6 * ss, ambient=1.0, diffuse=0.0)
    for j in range(nv):                                     # parallels (around the hole)
        pts = surf(tt, np.full_like(tt, 2 * np.pi * j / nv), 1.004)
        pl.add_mesh(pv.lines_from_points(pts), color=C.space, line_width=1.6 * ss, ambient=1.0, diffuse=0.0)
    ua, vb = np.radians(-62), np.pi / 2
    loop_a = surf(np.full_like(tt, ua), tt, 1.02)
    loop_b = surf(tt, np.full_like(tt, vb), 1.02)
    for pts in (loop_a, loop_b):
        pl.add_mesh(pv.Spline(pts, 400).tube(radius=0.022), color=C.circle, ambient=0.85, diffuse=0.25,
                    specular=0.0)
    pl.camera_position = [(0.0, -3.85, 2.69), (0.0, 0.0, -0.12), (0.0, 0.0, 1.0)]
    pl.camera.view_angle = 30
    img = pl.screenshot(return_img=True, transparent_background=True)

    def project(p):
        ren = pl.renderer
        ren.SetWorldPoint(*p, 1.0)
        ren.WorldToDisplay()
        x, y, _ = ren.GetDisplayPoint()
        return x / ss, px_h - y / ss

    anchors = {"a": project(loop_a[0]), "b": project(loop_b[60])}
    pl.close()
    a = img.astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]                               # premultiply before the downsample
    a[:3], a[-3:], a[:, :3], a[:, -3:] = 0, 0, 0, 0             # no stray rows at the border
    im = Image.fromarray((a * 255).round().astype(np.uint8), "RGBA").resize((px_w, px_h), Image.LANCZOS)
    ys, xs = np.nonzero(np.asarray(im)[..., 3] > 8)
    print(f"torus bbox x {xs.min()}..{xs.max()} of {px_w}, y {ys.min()}..{ys.max()} of {px_h}")
    # the mesh the counts come from: nu × nv quads, edges counted from the face list
    faces = [(i * nv + j, ((i + 1) % nu) * nv + j, ((i + 1) % nu) * nv + (j + 1) % nv, i * nv + (j + 1) % nv)
             for i in range(nu) for j in range(nv)]
    edges = {tuple(sorted((f[k], f[(k + 1) % 4]))) for f in faces for k in range(4)}
    TORUS.update(rgba=np.asarray(im), anchors=anchors, VEF=(nu * nv, len(edges), len(faces)), size=(px_w, px_h))


def vef_polygon(n, filled):
    edges = {tuple(sorted((k, (k + 1) % n))) for k in range(n)}
    return n, len(edges), 1 if filled else 0


def vef_cube():
    import itertools
    V = list(itertools.product((0, 1), repeat=3))
    E = [(a, b) for a, b in itertools.combinations(V, 2) if sum(x != y for x, y in zip(a, b)) == 1]
    F = [(ax, side) for ax in range(3) for side in (0, 1)]
    return len(V), len(E), len(F)


def f5(s, m):
    """Ch4 Space: V − E + F does not care about shape, only about holes."""
    pw, ph = TORUS["size"]
    hgt = ph / PX
    cx, cy = -3.3, -0.35
    s.add(ArrayLayer(TORUS["rgba"], height=hgt, pos=(cx, cy), premultiplied=True, z=-1))

    def world(px):
        return P3(cx + (px[0] - pw / 2) / PX, cy + (ph / 2 - px[1]) / PX)

    m.add(tex("a", 40, C.circle).next_to(world(TORUS["anchors"]["a"]), RIGHT, buff=0.18))
    m.add(tex("b", 40, C.circle).next_to(world(TORUS["anchors"]["b"]), UP, buff=0.16))

    m.add(Eqn(r"\chi = V - E + F", size=52, colors={r"\chi": C.space}).move_to(P3(3.45, 2.2)))
    rows = [("loop", vef_polygon(12, False)), ("disk", vef_polygon(12, True)), ("cube", vef_cube()),
            ("torus", TORUS["VEF"])]
    cols = (1.75, 3.3, 4.2, 5.1, 6.0)
    y0, dy = 1.35, 0.78
    for j, hname in enumerate(("V", "E", "F")):
        m.add(tex(hname, 40, C.muted).move_to(P3(cols[j + 1], y0)))
    m.add(tex(r"\chi", 40, C.space).move_to(P3(cols[4], y0)))
    m.add(Line(P3(0.35, y0 - 0.36), P3(6.4, y0 - 0.36), stroke_color=C.muted, stroke_width=1.6))
    ic = 0.75
    icons = [Circle(radius=0.2, stroke_color=C.circle, stroke_width=3),
             Circle(radius=0.2, stroke_color=C.circle, stroke_width=3, fill_color=C.space, fill_opacity=0.25)]
    cube = Square(0.3, stroke_color=C.space, stroke_width=2.5)
    back = cube.copy().shift(P3(0.12, 0.1))
    icons.append(VGroup(cube, back, *(Line(cube.get_vertices()[k], back.get_vertices()[k], stroke_color=C.space,
                                           stroke_width=2.5) for k in range(4))))
    icons.append(VGroup())
    for i, (name, (V, E, F)) in enumerate(rows):
        y = y0 - dy * (i + 1)
        row = VGroup(icons[i].move_to(P3(ic, y)), sans(name, 32).move_to(P3(cols[0], y)),
                     *(tex(str(v), 40).move_to(P3(cols[k + 1], y)) for k, v in enumerate((V, E, F))),
                     tex(str(V - E + F), 44, C.space).move_to(P3(cols[4], y)))
        if i < len(rows) - 1:
            dim(row)
        m.add(row)
    m.add(tracker(), minimap({"foundations", "quantity", "structure", "space"}, "space"))


def f6(s, m):
    """Ch5 Change: thin rings unroll into strips; stacked, they make Archimedes' triangle of area πR²."""
    R, N = 1.45, 12
    xc, yb = -1.75, -0.95
    oc = P3(xc, yb + R)
    w = R / N
    sw = w * PX / 1.35 * 0.86                               # stroke width that fills 86 % of a ring
    done, f = 4, 0.75                                       # 4 outer rings flat; the next one is uncurling
    for k in range(N):
        r = (k + 0.5) * w
        y = yb + R - r
        L = 2 * np.pi * r
        op = 0.6 if k % 2 else 1.0                           # two tints of C.change, alternating
        if k >= N - done:                                   # flat strip, as long as its ring
            m.add(Rectangle(width=L, height=w * 0.86, stroke_width=0, fill_color=C.change,
                            fill_opacity=op).move_to(P3(xc, y)))
        elif k == N - done - 1:                             # uncurling: same length, smaller curvature
            rho = r / (1 - f)
            half = L / (2 * rho)
            m.add(Arc(radius=rho, start_angle=-np.pi / 2 - half, angle=2 * half, arc_center=P3(xc, y + rho),
                      stroke_color=C.change, stroke_width=sw, stroke_opacity=op))
        else:
            m.add(Circle(radius=r, stroke_color=C.change, stroke_width=sw, stroke_opacity=op).move_to(oc))
    m.add(Line(P3(xc - np.pi * R, yb - w * 0.43), P3(xc + np.pi * R, yb - w * 0.43), stroke_color=C.circle,
               stroke_width=4))
    tri = Polygon(P3(xc - np.pi * R, yb), P3(xc + np.pi * R, yb), P3(xc, yb + R)).set_stroke(C.text, 2.0, 0.6)
    m.add(DashedVMobject(tri, num_dashes=90))
    m.add(DashedLine(oc, P3(xc, yb), dash_length=0.08, stroke_color=C.text, stroke_width=2))
    m.add(DashedLine(oc, oc + LEFT * R, dash_length=0.08, stroke_color=C.text, stroke_width=2))
    m.add(tex("R", 38).next_to(oc + LEFT * (R - 0.22), UP, buff=0.1))
    m.add(tex(r"2\pi R", 40, C.circle).next_to(P3(xc + np.pi * R * 0.62, yb - w * 0.43), DOWN, buff=0.16))
    work = VGroup(Eqn(r"A = \tfrac12\,(2\pi R)\,R", size=44, colors={"A": C.change, r"2\pi R": C.circle}),
                  Eqn(r"= \pi R^2", size=44)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    work[1].shift(RIGHT * 0.4)
    m.add(work.move_to(P3(4.75, 0.35)))
    # takeaway: at most four key words and one equation, over the callback visual
    words = sans("area grows by circumference", 34)
    eq = Eqn(r"\frac{dA}{dr} = 2\pi r", size=48, colors={r"\frac{dA}{dr}": C.change, r"2\pi r": C.circle})
    bar = VGroup(words, Line(UP * 0.42, DOWN * 0.42, stroke_color=C.muted, stroke_width=2), eq)
    bar.arrange(RIGHT, buff=0.45).move_to(P3(0, -YH + SAFE + 0.5))
    m.add(Line(bar.get_corner(UL) + P3(-0.2, 0.22), bar.get_corner(UR) + P3(0.2, 0.22), stroke_color=C.muted,
               stroke_width=1.6))
    m.add(bar)
    m.add(tracker(), minimap({"foundations", "quantity", "structure", "space", "change"}, "change"))


def f7(s, m):
    """Ch6 Uncertainty: each throw is a point (θ, x); it crosses iff x ≤ sin θ (x in half-board widths), so P = 2/π.

    Colours follow the plan: the rectangle of possibilities is Space, the sine arch and its area are Change, the
    width π is Quantity, the throws are Uncertainty. The floor is a window of the cold open's floor (same stream).
    """
    # left: the floor
    fb = (-6.62, -2.55, -0.95, 2.5)
    cx, cy, th, hit, lines_y = floor_layout(150, fb)
    lines_y = lines_y[(lines_y >= fb[1]) & (lines_y <= fb[3])]
    keep = (cx > fb[0] + 0.32) & (cx < fb[2] - 0.32) & (cy > fb[1] + 0.32) & (cy < fb[3] - 0.32)

    def draw(skia, cv, T):
        crack = stroke_paint(skia, C.map_off, 1.0, 2.0)
        for y in lines_y:
            cv.drawLine(*T(fb[0], y), *T(fb[2], y), crack)
        for crossing in (False, True):                       # crossing needles on top, full strength
            for x, y, t, h, k in zip(cx, cy, th, hit, keep):
                if k and h == crossing:
                    dx, dy = 0.5 * BOARD * math.cos(t), 0.5 * BOARD * math.sin(t)
                    cv.drawLine(*T(x - dx, y - dy), *T(x + dx, y + dy),
                                stroke_paint(skia, C.uncertainty, 1.0 if h else 0.32, 3.0))

    kw = skia_canvas(fb, draw)
    s.add(ArrayLayer(kw.pop("rgba"), z=-1, **kw))

    # right top: the rectangle of possibilities, θ ∈ [0, π] across, x ∈ [0, 1] up (half-board widths)
    ox, oy, sx, sy = 0.2, 0.75, 3.2 / np.pi, 1.5
    to = lambda a, b: P3(ox + a * sx, oy + b * sy)  # noqa: E731
    tt = np.linspace(0, np.pi, 181)
    arch = [to(a, math.sin(a)) for a in tt]
    m.add(Polygon(*arch, stroke_width=0, fill_color=C.change, fill_opacity=REGION))
    m.add(Rectangle(width=np.pi * sx, height=sy, stroke_color=C.space, stroke_width=2.4).move_to(to(np.pi / 2, 0.5)))
    xs, ths, hits = buffon(400)
    for under in (False, True):
        for a, b, h in zip(ths, 2 * xs, hits):
            if h == under:
                d = Dot(to(a, b), radius=0.032, color=C.uncertainty)
                m.add(d if h else dim(d))
    m.add(VMobject(stroke_color=C.change, stroke_width=4).set_points_smoothly(arch))
    m.add(tex("0", 30, C.muted).next_to(to(0, 0), DOWN, buff=0.12))
    m.add(tex(r"\theta", 32, C.muted).next_to(to(np.pi / 2, 0), DOWN, buff=0.12))
    m.add(Line(to(np.pi, 0), to(np.pi, 0) + DOWN * 0.12, stroke_color=C.quantity, stroke_width=4))
    m.add(tex(r"\pi", 36, C.quantity).next_to(to(np.pi, 0) + DOWN * 0.12, DOWN, buff=0.06))
    m.add(tex("1", 30, C.muted).next_to(to(0, 1), LEFT, buff=0.12))
    m.add(tex("x", 32, C.muted).next_to(to(0, 0.5), LEFT, buff=0.12))
    m.add(Eqn(r"x \le \sin\theta", size=34, colors={r"\sin\theta": C.change}).next_to(to(np.pi / 2, 1), UP, buff=0.14))
    pe = Eqn(r"P = \frac{2}{\pi}", size=52, colors={"P": C.uncertainty, r"\pi": C.quantity})
    pe.move_to(P3(3.95, 1.75), aligned_edge=LEFT)
    approx = tex(r"\approx 0.6366", 38).next_to(pe, DOWN, buff=0.3, aligned_edge=LEFT)
    m.add(pe, approx)

    # right bottom: the running estimate 2N / H against N (log), converging to π
    N = 100_000
    _, _, hall = buffon(N)
    n = np.unique(np.round(np.logspace(1, 5, 600)).astype(int))
    est = 2 * n / np.maximum(np.cumsum(hall)[n - 1], 1)
    px0, px1, base, top, lo, hi = 0.2, 5.45, -2.2, -0.55, 2.7, 3.6
    Y = lambda v: base + (v - lo) / (hi - lo) * (top - base)  # noqa: E731
    Xn = lambda nn: px0 + (math.log10(nn) - 1) / 4 * (px1 - px0)  # noqa: E731
    m.add(Line(P3(px0, base), P3(px1, base), stroke_color=C.text, stroke_width=2))
    for e in range(1, 6):
        m.add(Line(P3(Xn(10 ** e), base), P3(Xn(10 ** e), base - 0.1), stroke_color=C.muted, stroke_width=2))
        m.add(tex(f"10^{e}", 28, C.muted).next_to(P3(Xn(10 ** e), base - 0.1), DOWN, buff=0.06))
    m.add(tex("N", 32, C.muted).next_to(P3(px1, base), RIGHT, buff=0.15))
    m.add(DashedLine(P3(px0, Y(math.pi)), P3(px1, Y(math.pi)), dash_length=0.1, stroke_color=C.quantity,
                     stroke_width=2.4))
    m.add(tex(r"\pi", 36, C.quantity).next_to(P3(px1, Y(math.pi)), RIGHT, buff=0.15))
    ok_ = (est > lo) & (est < hi)
    pts = [P3(Xn(a), Y(b)) for a, b in zip(n[ok_], est[ok_])]
    m.add(VMobject(stroke_color=C.uncertainty, stroke_width=3.2).set_points_as_corners(pts))
    m.add(Dot(pts[-1], radius=0.07, color=C.uncertainty))
    m.add(sans(r"2N\,/\,H", 30, C.muted).move_to(P3(px0, top + 0.22), aligned_edge=DL))

    m.add(lower_third("G.-L. Leclerc, Comte de Buffon", "1777"))
    m.add(tracker(), minimap(set(PILLARS), "uncertainty"))


def f8(s, m):
    """Ch7: the map fully lit; e, i, π, 1 and 0 meet at the hub."""
    import itertools

    hub = VGroup(Circle(radius=HUB_R, stroke_color=C.circle, stroke_width=5, fill_color=C.bg, fill_opacity=1.0))
    eq = MathTex("e", "^{i", r"\pi}", "+", "1", "=", "0", font_size=50)
    for i, col in {0: C.change, 1: C.structure, 2: C.quantity, 4: C.foundations, 6: C.foundations}.items():
        eq[i].set_color(col)
    hub.add(eq.move_to(ORIGIN))
    m.add(map_of_math(lit=set(PILLARS), links=list(itertools.combinations(PILLARS, 2)), hub=hub))


def chapter_card(pillar, field, glyph_size=96, c=(0.0, 0.0)):
    """Chapter card: the pillar's node, scaled up, carries its glyph; the name in small caps (80) and the field in
    CM sans (36) sit under it. The node opens from 6 o'clock and shrinks back into it afterwards."""
    ring = Circle(radius=0.78, stroke_color=hue(pillar), stroke_width=3.0, fill_color=tint(hue(pillar), FILL),  # noqa: F821
                  fill_opacity=1.0).move_to(P3(c[0], c[1] + 1.05))
    gl = tex(GLYPHS[pillar], glyph_size, hue(pillar)).move_to(ring.get_center())  # noqa: F821
    if gl.width > 1.25:
        gl.scale_to_fit_width(1.25)
    name = caps(NAMES[pillar], 80).move_to(P3(c[0], c[1] - 0.55))  # noqa: F821
    sub = sans(field, 36, C.muted).next_to(name, DOWN, buff=0.34)  # noqa: F821
    return VGroup(ring, gl, name, sub)  # noqa: F821


def f9(s, m):
    """Reference: the Ch6 chapter card. The 6 o'clock node grows into it while the map fades out (the map returns
    when the card shrinks back into the node); nothing else shares the frame."""
    m.add(chapter_card("uncertainty", "probability and statistics"))


def f10(s, m):
    """Reference: the furniture at true size: lower third, tracker, nodes and a chord, key idea, mini-map, takeaway."""
    def cap(text, x, y):
        return sans(text, 28, C.muted).move_to(P3(x, y), aligned_edge=LEFT)

    x0, kx0, kx1 = -XW + SAFE, 0.6, 6.4
    # left column: lower third, tracker, nodes
    m.add(cap("lower third (bottom-left, on the safe inset)", x0, 3.05))
    lt = lower_third("G. Cantor", "1874")
    m.add(lt.shift(P3(0, 2.05 - lt.get_bottom()[1])))
    m.add(cap(r"e\,$\cdot$\,i\,$\cdot$\,$\pi$ tracker (top-left, Ch3--Ch7): empty, parked", x0, 1.4))
    m.add(tracker(lit=()).shift(P3(0, 0.75 - (YH - SAFE - 0.25))), tracker().shift(P3(2.3, 0.75 - (YH - SAFE - 0.25))))
    m.add(cap("map nodes: unlit, lit, lit with its name; a lit chord", x0, -0.25))
    pa, pb, pc = P3(x0 + 0.4, -1.05), P3(x0 + 1.9, -1.05), P3(x0 + 3.4, -1.05)
    m.add(gradient_line(pb + RIGHT * (NODE_R + 0.05), pc + LEFT * (NODE_R + 0.05), C.space, C.change))
    m.add(Circle(radius=NODE_R, stroke_color=C.map_off, stroke_width=2.0, fill_color=C.bg, fill_opacity=1).move_to(pa))
    for pos, pil in ((pb, "space"), (pc, "change")):
        m.add(Circle(radius=NODE_R, stroke_color=hue(pil), stroke_width=3.0, fill_color=tint(hue(pil), FILL),
                     fill_opacity=1.0).move_to(pos))
        gl = tex(GLYPHS[pil], 44, hue(pil)).move_to(pos)
        if gl.width > 1.5 * NODE_R:
            gl.scale_to_fit_width(1.5 * NODE_R)
        m.add(gl)
    m.add(caps(NAMES["change"], 32, C.change).next_to(pc + RIGHT * NODE_R, RIGHT, buff=0.16))
    # right column: key idea, mini-map states
    ky0, ky1 = 0.45, 2.75
    m.add(cap("key-idea panel (aion panel; eyebrow in small caps)", kx0, 3.05))
    m.add(panel(kx0, ky0, kx1, ky1))
    m.add(caps("key idea", 28, C.muted).move_to(P3(kx0 + 0.25, ky1 - 0.3), aligned_edge=LEFT))
    m.add(Eqn(r"\chi = V - E + F", size=48, colors={r"\chi": C.space}).move_to(P3((kx0 + kx1) / 2, ky1 - 1.05)))
    m.add(sans("counts holes, not shape", 32).move_to(P3((kx0 + kx1) / 2, ky0 + 0.45)))
    m.add(cap("mini-map (top-right): Ch1, Ch3, Ch6", kx0, -0.25))
    for j, (lit, cur) in enumerate(((("foundations",), "foundations"),
                                    (("foundations", "quantity", "structure"), "structure"),
                                    (tuple(PILLARS), "uncertainty"))):  # noqa: F821
        m.add(minimap(set(lit), cur, c=(kx0 + 0.45 + 1.2 * j, -1.05)))
    # bottom: the takeaway where it really sits
    m.add(cap(r"takeaway ($\le$ 4 key words + one equation), centred on the bottom band", x0, -1.72))
    words = sans("area grows by circumference", 34)
    eq = Eqn(r"\frac{dA}{dr} = 2\pi r", size=48, colors={r"\frac{dA}{dr}": C.change, r"2\pi r": C.circle})
    bar = VGroup(words, Line(UP * 0.42, DOWN * 0.42, stroke_color=C.muted, stroke_width=2), eq)
    bar.arrange(RIGHT, buff=0.45).move_to(P3(0, -YH + SAFE + 0.5))
    m.add(Line(bar.get_corner(UL) + P3(-0.2, 0.22), bar.get_corner(UR) + P3(0.2, 0.22), stroke_color=C.muted,
               stroke_width=1.6), bar)

FRAMES = {1: f1, 2: f2, 3: f3, 4: f4, 5: f5, 6: f6, 7: f7, 8: f8, 9: f9, 10: f10}


# ------------------------------------------------------------------------------------------------- main
def render(n: int) -> Path:
    from PIL import Image

    _import_aion()
    if n == 5:
        torus_render()                                    # VTK before aion's GL context exists

    @scene(0.0, 10.0)  # noqa: F821
    def style_frame(s):
        s.solid(C.bg, z=-200)  # noqa: F821
        FRAMES[n](s, s.manim())

    sd = scene_mod.REGISTRY[-1]  # noqa: F821
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{NAMES_OUT[n]}.png"
    Image.fromarray(sd.comp((W, H), FPS).frame(T_STILL, round(T_STILL * FPS))).save(path)
    print(path.resolve().relative_to(REPO))
    return path


if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(FRAMES)   # 1–8 style frames, 9–10 references
    if len(want) == 1:
        render(want[0])
    else:
        for k in want:                                    # one process per frame keeps memory low
            subprocess.run([sys.executable, __file__, str(k)], check=True, cwd=REPO)
