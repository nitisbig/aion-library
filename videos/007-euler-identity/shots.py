"""Shared building blocks for the Euler video: colored equations, the plane, the circle walk, panels, the rail.

The look is Classic: crisp unglowed vector lines on black, a bright integer grid over a dim half-step grid,
Computer Modern for all text. Colors are roles from theme.py: e = growth, i = turn, pi = arc, the moving point = point.
"""
from pathlib import Path

from aion import *

FRAME = (-7.3, -4.2, 7.3, 4.2)              # a little past the 14.22 x 8 frame, so grid lines run off screen
HERO_O, HERO_U = (0.0, 0.6), 2.1            # the intro's unit circle: centre and radius (Manim units)
HERO_EQ = (0.0, -2.75)                      # where e^{iπ} = −1 sits under it
CHAPTERS = ["What $e$ really is", "What $i$ really does", "Growth turned sideways", "Compounding a turn",
            "The infinite sum", "The whole circle"]


def ramp(t, a, b):
    """Smoothstep from 0 at t=a to 1 at t=b (for redraw functions)."""
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def ease(t, a, b):
    """Smoother (quintic) 0 → 1 between a and b: a calmer start and landing than `ramp`."""
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * u * (u * (6 * u - 15) + 10)


def tex(*parts, size=None, color=None, colors=None):
    """MathTex in the theme's text color; `colors` maps part index → color."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def glyphs(src, colors=None, size=None, n=None):
    """One MathTex whose GLYPHS are colored by index: `colors` = {glyph index: color}. `g[k]` is glyph k.

    Glyph indexing avoids splitting a superscript across MathTex parts (unbalanced braces).
    `n` asserts the glyph count so a TeX change cannot silently shift the colors.
    """
    t = MathTex(src, font_size=size or C.tex_size, color=C.text)
    g = t[0]
    if n is not None and len(g) != n:
        raise ValueError(f"{src!r}: {len(g)} glyphs, expected {n}")
    for k, col in (colors or {}).items():
        g[k].set_color(col)
    return g


def euler(size=None):
    """e^{iπ} = −1, glyphs [e, i, π, =, −, 1] in their role colors."""
    return glyphs(r"e^{i\pi}=-1", {0: C.growth, 1: C.turn, 2: C.arc, 4: C.point, 5: C.point}, size, n=6)


def identity(size=None):
    """e^{iπ} + 1 = 0, glyphs [e, i, π, +, 1, =, 0]."""
    return glyphs(r"e^{i\pi}+1=0", {0: C.growth, 1: C.turn, 2: C.arc}, size, n=7)


def words(text, size=None, color=None):
    """Plain words set in LaTeX (Computer Modern), so text and maths share one typeface."""
    return Tex(text, font_size=size or C.tex_size, color=color or C.text)


def P(origin, unit, z):
    """World point of the complex number z on a plane with this origin (x, y) and unit."""
    z = complex(z)
    return np.array([origin[0] + unit * z.real, origin[1] + unit * z.imag, 0.0])


def _clip(p, d, box):
    """Clip the infinite line p + s*d to the box (x0, y0, x1, y1). Returns two end points or None."""
    x0, y0, x1, y1 = box
    lo, hi = -np.inf, np.inf
    for pc, dc, a, b in ((p[0], d[0], x0, x1), (p[1], d[1], y0, y1)):
        if abs(dc) < 1e-12:
            if pc < a or pc > b:
                return None
            continue
        s0, s1 = sorted(((a - pc) / dc, (b - pc) / dc))
        lo, hi = max(lo, s0), min(hi, s1)
    if lo >= hi:
        return None
    return p + lo * d, p + hi * d


def plane_grid(origin, unit, box=FRAME, turn=0.0, n=12, minor=2, opacity=1.0, width=None, axes=True, color=None):
    """The complex plane's grid turned by `turn` radians about `origin` (multiplying by e^{i turn}), clipped to box.

    Integer lines in C.grid, half-step lines in C.grid_minor, the two axes in C.axis. `color` gives a one-color
    reference grid (no minor lines).
    """
    c = np.asarray(origin, float)[:2]
    R = np.array([[np.cos(turn), -np.sin(turn)], [np.sin(turn), np.cos(turn)]])
    w = width or C.thin
    sub = 1 if color else max(1, minor)
    dim, major, axis = VGroup(), VGroup(), VGroup()
    for k_dir in (0, 1):
        d = R[:, k_dir] * unit
        step = R[:, 1 - k_dir] * unit / sub
        for k in range(-n * sub, n * sub + 1):
            seg = _clip(c + k * step, d, box)
            if seg is None:
                continue
            a, b = [*seg[0], 0], [*seg[1], 0]
            if axes and k == 0:
                axis.add(Line(a, b, color=color or C.axis, stroke_width=w * 1.4, stroke_opacity=opacity))
            elif k % sub == 0:
                major.add(Line(a, b, color=color or C.grid, stroke_width=w, stroke_opacity=opacity))
            else:
                dim.add(Line(a, b, color=C.grid_minor, stroke_width=w * 0.7, stroke_opacity=opacity))
    return VGroup(dim, major, axis)


def arrow(a, b, color, width=None, tip=0.24):
    """A crisp arrow that keeps a sensible tip at any length."""
    L = max(np.linalg.norm(np.asarray(b) - np.asarray(a)), 1e-6)
    return Arrow(a, b, buff=0, color=color, stroke_width=width or C.stroke, tip_length=min(tip, 0.45 * L),
                 max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=40)


def arc_path(origin, unit, th0, th1, color, width=None, opacity=1.0):
    """The unit-circle arc from angle th0 to th1 (radians), on a plane with this origin and unit."""
    if abs(th1 - th0) < 1e-4:
        return VGroup()
    return Arc(radius=unit, start_angle=th0, angle=th1 - th0, arc_center=[*origin, 0], color=color,
               stroke_width=width or C.stroke, stroke_opacity=opacity)


def walker(origin, unit, th, k=1.0, arc=True, radius=True):
    """The point e^{i th} on the circle: the green arc walked so far, the yellow radius, the yellow dot."""
    g = VGroup()
    if arc:
        g.add(arc_path(origin, unit, 0.0, th, C.arc, width=C.stroke + 1.5, opacity=k))
    p = P(origin, unit, np.exp(1j * th))
    if radius:
        g.add(Line([*origin, 0], p, color=C.point, stroke_width=C.stroke, stroke_opacity=0.9 * k))
    g.add(Dot(p, radius=0.09, color=C.point).set_opacity(k))
    return g


def backing(mob, pad=0.25):
    """An opaque black panel with a thin border behind HUD content, so it reads cleanly over the plane."""
    return Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_color=C.frame,
                     stroke_width=C.thin * 0.8, fill_color=C.bg, fill_opacity=1.0).move_to(mob)


def panel(cx, cy, w, h):
    """A framed panel centred at (cx, cy): black inside, thin light border."""
    return Rectangle(width=w, height=h, stroke_color=C.frame, stroke_width=C.thin,
                     fill_color=C.bg, fill_opacity=1.0).move_to([cx, cy, 0])


def live(m, fn, *windows):
    """Rebuild `fn(t)` every frame inside each (start, end) window and hold it still in between.

    Only the moving windows are re-rasterized, so long holds stay free. Returns the handles.
    """
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


def rail_ticks(k):
    """Progress rail, bottom-left: six chapter ticks, chapters before k done (muted), k lit, later faint."""
    g = VGroup()
    for i in range(len(CHAPTERS)):
        col = C.text if i + 1 == k else (C.muted if i + 1 < k else C.faint)
        g.add(Line(ORIGIN, RIGHT * 0.26, color=col, stroke_width=3))
    g.arrange(RIGHT, buff=0.09)
    g.move_to([-7.11 + C.margin, -4 + C.margin, 0], aligned_edge=LEFT)
    return g


def rail(m, k):
    """Add the progress rail for chapter k (visible from the scene start)."""
    g = rail_ticks(k)
    m.add(g)
    return g


BANK_O, BANK_UX, BANK_UY = (-6.0, -2.9), 6.6, 1.9      # Ch1 money-vs-time axes: origin (world), units
I_POS = (0.0, 1.05)                         # where the red i hovers at the end of Ch1 and starts Ch2


def bank_pt(t, y):
    """World point of (year t, balance y) on the Ch1 axes."""
    return np.array([BANK_O[0] + BANK_UX * t, BANK_O[1] + BANK_UY * y, 0.0])


def graph_axes(o, ux, uy, t0, t1, ymax, xticks=(), yticks=(), opacity=1.0, tlab="t", ylab=r"\$"):
    """Crisp axes for a graph: the t axis from t0 to t1 and the y axis from 0 to ymax, with origin `o` (world)
    and units ux, uy. Small ticks; numbers only at the ticks listed."""
    g = VGroup()
    w = C.thin * 1.2
    X = lambda t: o[0] + ux * t                       # noqa: E731
    Y = lambda y: o[1] + uy * y                       # noqa: E731
    g.add(Line([X(t0), Y(0), 0], [X(t1) + 0.25, Y(0), 0], color=C.axis, stroke_width=w, stroke_opacity=opacity))
    g.add(Line([X(0), Y(0), 0], [X(0), Y(ymax) + 0.2, 0], color=C.axis, stroke_width=w, stroke_opacity=opacity))
    for t in xticks:
        g.add(Line([X(t), Y(0) - 0.08, 0], [X(t), Y(0) + 0.08, 0], color=C.axis, stroke_width=w,
                   stroke_opacity=opacity))
        g.add(MathTex(f"{t:g}", font_size=30, color=C.muted).move_to([X(t), Y(0) - 0.32, 0]).set_opacity(opacity))
    for y in yticks:
        g.add(Line([X(0) - 0.08, Y(y), 0], [X(0) + 0.08, Y(y), 0], color=C.axis, stroke_width=w,
                   stroke_opacity=opacity))
        g.add(MathTex(f"{y:g}", font_size=30, color=C.muted).move_to([X(0) - 0.42, Y(y), 0]).set_opacity(opacity))
    if tlab:
        g.add(MathTex(tlab, font_size=36, color=C.text).move_to([X(t1) + 0.5, Y(0), 0]).set_opacity(opacity))
    if ylab:
        g.add(MathTex(ylab, font_size=36, color=C.text).move_to([X(0), Y(ymax) + 0.5, 0]).set_opacity(opacity))
    return g


ICONS = Path(__file__).parent / "assets" / "icons"


def icon(name, height, color=None, width=None):
    """A line-art SVG icon from assets/icons, recolored to a theme color with crisp unfilled strokes."""
    m = SVGMobject(str(ICONS / f"{name}.svg"))
    m.set_fill(opacity=0).set_stroke(color or C.text, width=width or C.thin + 1, opacity=1)
    return m.set(height=height)


def coin(radius=0.22, color=None):
    """A gold coin: the coin.svg rim with a TeX dollar sign."""
    col = color or C.growth
    ring = icon("coin", 2 * radius, col, width=C.thin + 0.6)
    sign = MathTex(r"\$", font_size=radius * 120, color=col).move_to(ring)
    return VGroup(ring, sign)


def calendar(n, height=0.9, k=1.0):
    """A year as 12 month cells (4 x 3) with the payment months marked in gold. n = payments a year (1, 2, 4, 12);
    n > 12 fills every cell with a fine grid of days."""
    w_, h_ = height * 1.15, height
    g = VGroup(Rectangle(width=w_, height=h_, stroke_color=C.text, stroke_width=C.thin + 0.4, stroke_opacity=k))
    band = 0.2 * h_
    g.add(Rectangle(width=w_, height=band, stroke_width=0, fill_color=C.text, fill_opacity=0.85 * k)
          .move_to([0, h_ / 2 - band / 2, 0]))
    for x in (-0.25 * w_, 0.25 * w_):                 # the two binder rings
        g.add(Line([x, h_ / 2 - 0.02, 0], [x, h_ / 2 + 0.08, 0], color=C.text, stroke_width=C.thin + 1,
                   stroke_opacity=k))
    cw, ch = w_ / 4, (h_ - band) / 3
    paid = set(range(12)) if n >= 12 else {12 // n * (j + 1) - 1 for j in range(n)}
    for m_ in range(12):
        cx = -w_ / 2 + cw * (m_ % 4 + 0.5)
        cy = h_ / 2 - band - ch * (m_ // 4 + 0.5)
        if m_ in paid and n <= 12:
            g.add(Square(side_length=min(cw, ch) * 0.62, stroke_width=0, fill_color=C.growth,
                         fill_opacity=0.95 * k).move_to([cx, cy, 0]))
        elif n > 12:
            for a in range(3):
                for b in range(3):
                    g.add(Dot([cx + (a - 1) * cw * 0.26, cy + (b - 1) * ch * 0.26, 0], radius=0.012 * height / 0.9,
                              color=C.growth).set_opacity(0.95 * k))
        else:
            g.add(Square(side_length=min(cw, ch) * 0.62, stroke_color=C.faint, stroke_width=C.thin,
                         stroke_opacity=k).move_to([cx, cy, 0]))
    return g


def stopwatch(angle, height=0.9, k=1.0):
    """A stopwatch, hand at `angle` (radians, clockwise from 12): the clock of continuous compounding."""
    r = height * 0.4
    g = VGroup(Circle(radius=r, color=C.text, stroke_width=C.thin + 0.8).set_stroke(opacity=k))
    g.add(Line([0, r, 0], [0, r + 0.08, 0], color=C.text, stroke_width=C.thin + 2, stroke_opacity=k))
    g.add(Line([-0.07, r + 0.1, 0], [0.07, r + 0.1, 0], color=C.text, stroke_width=C.thin + 2, stroke_opacity=k))
    for j in range(12):
        a = j * TAU / 12
        g.add(Line([0.82 * r * np.sin(a), 0.82 * r * np.cos(a), 0], [0.94 * r * np.sin(a), 0.94 * r * np.cos(a), 0],
                   color=C.muted, stroke_width=C.thin, stroke_opacity=k))
    if angle > 1e-3:
        g.add(AnnularSector(inner_radius=0, outer_radius=0.72 * r, angle=-angle, start_angle=PI / 2,
                            fill_color=C.growth, fill_opacity=0.25 * k, stroke_width=0))
    g.add(Line(ORIGIN, [0.75 * r * np.sin(angle), 0.75 * r * np.cos(angle), 0], color=C.growth,
               stroke_width=C.thin + 1.2, stroke_opacity=k))
    return g


def badge(k):
    """Chapter k's badge: a small formula that stays on the rail for the rest of the video (k = 1..6)."""
    src = {1: (r"v=x", {0: C.vel, 2: C.growth}),
           2: (r"\times i=\circlearrowleft", {1: C.turn, 3: C.turn}),
           3: (r"v=ix", {0: C.vel, 2: C.turn, 3: C.point}),
           4: (r"(1+\tfrac{i\pi}{n})^n", {3: C.turn, 4: C.arc}),
           5: (r"\textstyle\sum", {}),
           6: (r"\cos+i\sin", {0: C.cos, 1: C.cos, 2: C.cos, 4: C.turn, 5: C.sin, 6: C.sin, 7: C.sin})}[k]
    g = glyphs(src[0], src[1], size=30)
    g.move_to([-7.11 + C.margin, -3.1, 0], aligned_edge=LEFT).shift(RIGHT * (1.15 * (k - 1) + (0.35 if k >= 5 else 0)))
    return g


def badges(m, upto):
    """Add the badges of chapters 1..upto, visible from the scene start."""
    gs = [badge(k) for k in range(1, upto + 1)]
    if gs:
        m.add(*gs)
    return gs


def chapter_card(m, k, t_in, t_out):
    """A quiet chapter card in Computer Modern: a small 'Chapter k' over the title."""
    num = words(f"Chapter {k}", size=30, color=C.muted)
    name = words(CHAPTERS[k - 1], size=72)
    g = VGroup(num, name).arrange(DOWN, buff=0.32)
    m.play(FadeIn(num, shift=0.12 * UP), at=t_in, dur=0.6, lead=0)
    m.play(FadeIn(name, shift=0.12 * UP), at=t_in + 0.25, dur=0.8, lead=0)
    m.play(FadeOut(g), at=t_out, dur=0.6)
    m.remove(g, at=t_out + 0.1)
    return g


def backdrop(s):
    """Flat background in C.bg."""
    s.solid(C.bg, z=-200)


# ── Ch2: numbers as actions ──
NLY = -0.9                                  # the Ch2 number line's height; 0 sits at x = 0 (later the plane's origin)
PLANT = (5.2, 2.85)                        # the planted "×(−1) = half turn" card, top right


def ruler(k=1.0):
    """The fixed reference ticks and integers −7..7 under the Ch2 number line (the line itself moves)."""
    g = VGroup()
    if k < 0.005:
        return g
    for n in range(-7, 8):
        g.add(Line([n, NLY - 0.08, 0], [n, NLY + 0.08, 0], color=C.axis, stroke_width=C.thin, stroke_opacity=k))
        g.add(MathTex(str(n), font_size=28, color=C.muted).move_to([n, NLY - 0.38, 0]).set_opacity(k))
    return g


def numline(S, R, k=1.0, half=16.0, xs=range(-3, 4), dot_k=None, lab_k=0.0, ghost=0.0):
    """The number line acted on by a stretch S and a turn R (radians) about 0: the line, its dots at xs (moved to
    S·x·e^{iR}), optional labels of where each dot started (faded while the line is not flat), and faint ghosts
    at the starting places."""
    g = VGroup()
    if k < 0.005:
        return g
    o = np.array([0.0, NLY, 0.0])
    u = np.array([np.cos(R), np.sin(R), 0.0])
    g.add(Line(o - half * u, o + half * u, color=C.axis, stroke_width=C.thin * 1.6, stroke_opacity=k))
    if ghost > 0.005:
        for x in xs:
            g.add(Dot(o + [x, 0, 0], radius=0.07, color=C.ghost).set_opacity(k * ghost))
    lk = lab_k * abs(np.cos(R)) ** 4
    for x in xs:
        dk = k * (dot_k(x) if dot_k else 1.0)
        if dk < 0.005:
            continue
        p = o + S * x * u
        g.add(Dot(p, radius=0.085, color=C.text).set_opacity(dk))
        if lk > 0.01:
            g.add(MathTex(str(x), font_size=30, color=C.text).move_to(p + [0, 0.36, 0]).set_opacity(dk * lk))
    return g


def dashed_arc(center, r, a0, a1, color, k=1.0, width=None):
    """A dashed arc of radius r from angle a0 to a1: the path a turned point travels."""
    if abs(a1 - a0) < 0.03 or k < 0.005:
        return VGroup()
    arc = Arc(radius=r, start_angle=a0, angle=a1 - a0, arc_center=[*center, 0], color=color,
              stroke_width=width or C.thin + 0.8, stroke_opacity=k)
    return DashedVMobject(arc, num_dashes=max(3, int(abs(a1 - a0) * r * 4)), dashed_ratio=0.55)


def action_row():
    """The four actions, top centre: ×2, ×½, ×(−1), ×i."""
    toks = [glyphs(r"\times 2", size=58, n=2), glyphs(r"\times\tfrac{1}{2}", size=58, n=4),
            glyphs(r"\times(-1)", {2: C.point, 3: C.point}, size=58, n=5), glyphs(r"\times i", {1: C.turn}, size=58, n=2)]
    return VGroup(*toks).arrange(RIGHT, buff=0.9).move_to([-0.9, 2.8, 0])


def plant():
    """The planted card: ×(−1) = a half-turn arrow. Returns VGroup(box, VGroup(×(−1), =, arc))."""
    a = glyphs(r"\times(-1)", {2: C.point, 3: C.point}, size=44, n=5)
    arc = Arc(radius=0.27, start_angle=0, angle=PI, color=C.turn, stroke_width=C.stroke)
    arc.add_tip(tip_length=0.14, tip_width=0.14)
    row = VGroup(a, tex("=", size=44), VGroup(arc, Dot(radius=0.035, color=C.muted).move_to(arc.get_arc_center())))
    row.arrange(RIGHT, buff=0.22)
    box = backing(row, pad=0.2)
    return VGroup(box, row).move_to([*PLANT, 0])


# ── Ch3: growth turned sideways ──
O3, U3 = (0.0, -0.3), 1.9                   # the Ch3 plane: origin (world) and unit (the unit circle's radius)
FLOW_N, FLOW_W = 5000, 0.7                  # flow field: points, and how fast each one's clock runs (rad/s)


def flow_alpha():
    """The flow field's growth direction a = e^{iα}: α = 0 (outward), π/4 (spirals), π/2 (= i, circles)."""
    from beats import T
    return keys((0.0, 0.0), (T.spiral - 0.9, 0.0), (T.spiral + 0.3, PI / 4, "easy_ease"),
                (T.all_way - 0.2, PI / 4), (T.all_way + 0.9, PI / 2, "easy_ease"), lead=0)


def flow_layer(alpha, opacity):
    """~5k points flowing under dz/dt = a·z, a = e^{iα(t)}. Each point runs its own clock τ (period 2π); over one
    period its radius goes r0·e^{(τ−π)cos α} and its angle turns by (τ−π)·sin α: the exact solution for a frozen a.
    At α = π/2 every radius is constant and the period wrap is invisible (a full turn)."""
    g = rng(31)
    r0 = 9.0 * np.sqrt(g.uniform(0.0004, 1.0, FLOW_N))
    ph0 = g.uniform(0, TAU, FLOW_N)
    tau0 = g.uniform(0, TAU, FLOW_N)

    def pos(t):
        a = alpha(t)
        tau = np.mod(tau0 + FLOW_W * t, TAU) - PI
        r = r0 * np.exp(tau * np.cos(a))
        th = ph0 + tau * np.sin(a)
        return np.column_stack([O3[0] + r * np.cos(th), O3[1] + r * np.sin(th)])

    def val(t):
        return np.full(FLOW_N, alpha(t) / (PI / 2))
    return PointsLayer(pos, values=val, cmap="diverging", colors=(C.growth, C.turn, C.turn), vmin=0.0, vmax=1.0, size=3.0,
                       glow=0.0, additive=False, opacity=opacity, z=1)


def exposure_layer(opacity):
    """A long exposure of the circling field (skia): faint red streaks along circles about the origin."""
    import skia
    box = (-9.6, -5.6, 9.6, 5.6)
    ppu = 100
    W, H = int((box[2] - box[0]) * ppu), int((box[3] - box[1]) * ppu)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.clear(skia.Color4f(0, 0, 0, 0))
    r_, g_, b_ = (int(C.turn[k:k + 2], 16) for k in (1, 3, 5))
    rg = rng(7)
    cx, cy = (O3[0] - box[0]) * ppu, (box[3] - O3[1]) * ppu
    for _ in range(520):
        r = 9.5 * np.sqrt(rg.uniform(0.002, 1.0)) * ppu
        a1 = rg.uniform(0, TAU)
        n = 12
        for j in range(n):                            # a streak fading toward its tail
            p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.6,
                           Color=skia.Color(r_, g_, b_, int(110 * (j + 1) / n)))
            sweep = 1.1 / n
            start = -np.degrees(a1 - 1.1 + j * sweep)  # y down: angles flip
            path = skia.Path()
            path.addArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), start, -np.degrees(sweep))
            cv.drawPath(path, p)
    rgba = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return ArrayLayer(rgba, height=box[3] - box[1], pos=((box[0] + box[2]) / 2, (box[1] + box[3]) / 2),
                      opacity=opacity, z=0)


def right_angle(p, d1, d2, size=0.2, color=None, k=1.0):
    """A small right-angle mark at p between unit directions d1 and d2."""
    p = np.asarray(p, float)
    a, b = np.array([*d1[:2], 0.0]) * size, np.array([*d2[:2], 0.0]) * size
    return VMobject(stroke_color=color or C.text, stroke_width=C.thin + 0.4, stroke_opacity=k).set_points_as_corners(
        [p + a, p + a + b, p + b])
