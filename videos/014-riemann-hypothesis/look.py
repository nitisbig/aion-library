"""Shared building blocks for "The Riemann Hypothesis, Visually Explained" (014).

Everything is a pure function of t, and every plotted number comes from zmath.py (baked by bake.py, checked by
verify.py).
- text:       tex, lab (CM sans key words), caps (CM small caps), mono (CM typewriter), carded, pin, chapter_card
- staircase:  X, Y, P (the 0-100 plot), number_line, y_axis, prime_ticks, stair_mob, curve_mob, explicit(),
              wave_weights, R_GHOST
- line of zeros: ZX, zy, GAM, zero_line (the same line from the first frame to the last)
- series tower (s07, s08): partial, tower_grid, tower_mob, needle_mob, slider_mobs, knob_mob, series_eq,
  series_results; sieve colors: spf, sieve_color
- planes (s09, s10): s_xy, splane_mob, probe_mob, op_map, oplane_mob, spiral_mob, zeta_mark, clip_seg
- full plane (s10, s11): plane_grid, plane_xy, PANEL_BOX, FRAME_BOX, wheel_mob, band_key_mob
"""
from functools import lru_cache
from pathlib import Path

from aion import *
from zmath import primes_upto

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
EASE = "easy_ease"
SAFE_LEFT, SAFE_TOP = -6.65, 3.55                     # inside the 0.45 safe margin of the 14.22 x 8 frame
SAFE_RIGHT, SAFE_BOTTOM = 6.65, -3.55


def seen(a):
    """Layer alpha that LOOKS like `a` over black: aion composites in linear light, so alpha a reads as a^(1/2.2)."""
    return float(a) ** 2.2


# ---------------------------------------------------------------- text
def tex(*parts, size=None, color=None, colors=None):
    """Maths in CM roman; `colors` maps part index to color."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def lab(text, size=34, color=None):
    """A key word in CM sans."""
    return Tex(r"\textsf{" + text + "}", font_size=size, color=color or C.text)


def caps(text, size=56, color=None):
    """A name or a date in CM small caps."""
    return Tex(r"\textsc{" + text + "}", font_size=size, color=color or C.text)


def mono(text, size=28, color=None):
    """Code in CM typewriter."""
    return Tex(r"\texttt{" + text + "}", font_size=size, color=color or C.text)


def carded(mob, buff=0.1, opacity=0.92):
    """A label on a black card, so it stays legible over curves."""
    return VGroup(BackgroundRectangle(mob, color=C.bg, fill_opacity=opacity, buff=buff), mob)


def pin(mob, top=SAFE_TOP, left=SAFE_LEFT):
    """Place a mobject by its top-left corner."""
    return mob.move_to([left + mob.width / 2, top - mob.height / 2, 0])


def chapter_card(m, at, symbol, name, out, color=None, extra=None):
    """The chapter card in the section gap (design.md §8): the key symbol at 96 px over a rule and the chapter name
    in small caps. Appears at `at` (the cut), leaves at `out`. `extra` is placed right of the symbol."""
    sym = symbol if isinstance(symbol, Mobject) else tex(symbol, size=96, color=color or C.text)
    head = VGroup(sym, extra).arrange(RIGHT, buff=0.45) if extra is not None else sym
    rule = Line([-1.9, 0, 0], [1.9, 0, 0], color=C.muted, stroke_width=1.6)
    title = caps(name, size=48)
    card = VGroup(head, rule, title).arrange(DOWN, buff=0.34).move_to(ORIGIN)
    m.play(FadeIn(head), FadeIn(title), at=at + 0.05, dur=0.3, lead=0)
    m.play(Create(rule), at=at + 0.1, dur=0.6, ease=EASE, lead=0)
    m.play(FadeOut(card), at=out, dur=0.4, lead=0)
    m.remove(card, at=out + 0.45)
    return card


# ---------------------------------------------------------------- the staircase plot (s02, s16, s31)
PX0, PX1 = -6.2, 3.6                                  # Manim x of x = 0 and x = 100
PY0, PSC = -3.1, 0.236                                # Manim y of a count of 0, and units per count
PRIMES = [int(p) for p in primes_upto(100)]           # the 25 primes below 100


def X(x):
    return PX0 + (PX1 - PX0) * np.asarray(x, float) / 100.0


def Y(n):
    return PY0 + PSC * np.asarray(n, float)


def P(x, n, y0=PY0):
    return np.array([float(X(x)), y0 + PSC * float(n), 0.0])


@lru_cache(maxsize=1)
def explicit():
    """assets/explicit.npz (bake.py): x (4000 samples on [1.6, 100]), pi, base = R(x) + small terms, waves (100, 4000)."""
    d = np.load(ASSETS / "explicit.npz")
    return {k: d[k].astype(np.float64) for k in d.files}


def number_line(y=0.0, labels=(0, 20, 40, 60, 80, 100)):
    """The 0-100 number line: a white axis, a faint tick at every whole number, longer ticks every ten."""
    axis = Line([X(0) - 0.05, y, 0], [X(100) + 0.12, y, 0], color=C.axis, stroke_width=2.0)
    minor = VGroup(*[Line([X(k), y - 0.05, 0], [X(k), y + 0.05, 0], color=C.muted, stroke_width=1.0,
                          stroke_opacity=0.55) for k in range(1, 101) if k % 10])
    major = VGroup(*[Line([X(k), y - 0.09, 0], [X(k), y + 0.09, 0], color=C.muted, stroke_width=1.6)
                     for k in range(10, 101, 10)])
    nums = VGroup(*[tex(str(k), size=28, color=C.muted).move_to([X(k), y - 0.34, 0]) for k in labels])
    g = VGroup(axis, minor, major, nums)
    g.axis, g.nums = axis, nums
    return g


def prime_ticks(y=0.0, half=0.15):
    """A gold tick at each prime below 100."""
    return VGroup(*[Line([X(p), y - half, 0], [X(p), y + half, 0], color=C.prime, stroke_width=3.2) for p in PRIMES])


def y_axis(top=26.6, labels=(10, 20)):
    axis = Line([X(0), Y(0), 0], [X(0), Y(top), 0], color=C.axis, stroke_width=2.0)
    ticks = VGroup(*[Line([X(0) - 0.07, Y(k), 0], [X(0) + 0.07, Y(k), 0], color=C.muted, stroke_width=1.6)
                     for k in range(5, int(top) + 1, 5)])
    nums = VGroup(*[tex(str(k), size=28, color=C.muted).move_to([X(0) - 0.32, Y(k), 0]) for k in labels])
    return VGroup(axis, ticks, nums)


def stair_points(xc):
    """The staircase pi(x) from 0 to xc as corner points."""
    pts, n = [P(0, 0)], 0
    for p in PRIMES:
        if p > xc:
            break
        pts += [P(p, n), P(p, n + 1)]
        n += 1
    pts.append(P(max(xc, 1e-3), n))
    return pts, n


def stair_mob(xc=100.0, width=3.4, opacity=1.0):
    pts, _ = stair_points(xc)
    v = VMobject(color=C.prime, stroke_width=width, stroke_opacity=opacity)
    v.set_points_as_corners(pts)
    return v


def curve_mob(y, xs=None, color=None, width=2.6, opacity=1.0, xmax=None, xmin=2.0):
    """A sampled curve of counts y(x) through the plot from x = 2 (the first step); `xmax` clips it on the right."""
    xs = explicit()["x"] if xs is None else xs
    keep = (xs >= xmin) & (xs <= (np.inf if xmax is None else xmax))
    xs, y = xs[keep], y[keep]
    if len(xs) < 2:
        return VGroup()
    v = VMobject(color=color or C.zero, stroke_width=width, stroke_opacity=opacity)
    v.set_points_as_corners(np.column_stack([X(xs), Y(y), np.zeros_like(xs)]))
    return v


def wave_weights(t, starts, dur=0.5, soft=6.0, xs=None):
    """How much of each wave is in at time t: a front sweeps x from left to right in `dur` seconds after each start,
    with a soft edge `soft` wide (design.md §5: waves add in left to right). Returns (K, N) weights."""
    xs = explicit()["x"] if xs is None else xs
    u = np.clip((t - np.asarray(starts, float)) / dur, 0.0, 1.0)
    u = u * u * (3 - 2 * u)                                                    # smoothstep
    front = -soft + (100.0 + 2 * soft) * u
    w = np.clip((front[:, None] - xs[None, :]) / soft, 0.0, 1.0)
    return w * w * (3 - 2 * w)


def batch_starts(beats, sizes, stagger=0.015, lead=None):
    """Start times for wave batches: batch i (sizes[i] waves) starts on beats[i] - lead, 15 ms apart."""
    lead = C.lead if lead is None else lead
    out = []
    for b, n in zip(beats, sizes):
        out += [float(b) - lead + stagger * j for j in range(n)]
    return np.array(out)


# ---------------------------------------------------------------- the line of zeros (s01, s02, s13, s16, s31)
ZX, ZY0, ZS = 5.6, -3.5, 0.03                         # Manim x of the line; y of height 0; units per unit of height
ZTOP = 3.72                                           # top of the line until "all infinitely many" (s02)
GAM = np.load(ASSETS / "zeros.npy")                   # heights of the first 649 zeros, 14.1347...
R_DOT = 0.027


def zy(g):
    return ZY0 + ZS * np.asarray(g, float)


def zero_line(top=ZTOP, lit=None, scale=None, dim=0.1, line_opacity=0.75, width=2.0, x=ZX):
    """The green line with a pink dot at every zero below `top`. `lit[k]` in [0, 1] raises dot k from `dim` to full;
    `scale[k]` scales its radius. Parts: .line, .dots"""
    line = Line([x, ZY0, 0], [x, top, 0], color=C.crit, stroke_width=width, stroke_opacity=line_opacity)
    dots = VGroup()
    for k, g in enumerate(GAM):
        y = float(zy(g))
        if y > top - 0.02:
            break
        a = dim + (1 - dim) * (float(lit[k]) if lit is not None and k < len(lit) else 0.0)
        r = R_DOT * (float(scale[k]) if scale is not None and k < len(scale) else 1.0)
        dots.add(Dot([x, y, 0], radius=r, color=C.zero, fill_opacity=a, stroke_width=0))
    g = VGroup(line, dots)
    g.line, g.dots = line, dots
    return g


TOP_INF = 4.7                                         # the line runs out of the frame after s02's "infinitely many"


def staircase_frame(n_waves=100, ghost_opacity=0.12):
    """The plot as s02 leaves it: axes, prime ticks, the staircase, R(x) dimmed, and the curve rebuilt from
    `n_waves` zero pairs. Parts: .axes, .ticks, .yaxis, .stair, .ghost, .pink"""
    E = explicit()
    nl, ticks, ya = number_line(PY0), prime_ticks(PY0), y_axis()
    stair = stair_mob(100.0)
    ghost = curve_mob(E["base"], color=C.smooth, opacity=ghost_opacity)
    pink = curve_mob(E["base"] + E["waves"][:n_waves].sum(axis=0), color=C.zero)
    g = VGroup(nl, ya, ticks, stair, ghost, pink)
    g.axes, g.yaxis, g.ticks, g.stair, g.ghost, g.pink = nl, ya, ticks, stair, ghost, pink
    return g


def zero_line_lit(**kw):
    """The line of zeros as s02 leaves it: every dot lit, the line running out of the top of the frame."""
    return zero_line(top=TOP_INF, lit=np.ones(len(GAM)), **kw)


# ---------------------------------------------------------------- the critical strip beside the line (s16, s17)
STRIP = (ZX - 0.75, ZX + 0.75)                        # Manim x of Re s = 0 and Re s = 1; the line of zeros is Re s = 1/2


def re_x(sigma):
    """Manim x of real part sigma inside the strip."""
    return STRIP[0] + (STRIP[1] - STRIP[0]) * float(sigma)


def strip_mobs():
    """The critical strip around the line of zeros: fill, Re s = 0 (green, faint), Re s = 1 (white), and their labels.
    Parts: .fill, .re0, .re1, .n0, .n1"""
    fill = Rectangle(width=STRIP[1] - STRIP[0], height=8.4, stroke_width=0, fill_color=C.crit, fill_opacity=seen(0.14))
    fill.move_to([ZX, 0.7, 0])
    re0 = Line([STRIP[0], -3.5, 0], [STRIP[0], 4.9, 0], color=C.crit, stroke_width=1.4, stroke_opacity=0.6)
    re1 = Line([STRIP[1], -3.5, 0], [STRIP[1], 4.9, 0], color=C.text, stroke_width=2.2)
    n0 = tex("0", size=28, color=C.muted).move_to([STRIP[0] + 0.14, -3.36, 0])
    n1 = tex("1", size=28, color=C.text).move_to([STRIP[1] + 0.14, -3.36, 0])
    g = VGroup(fill, re0, re1, n0, n1)
    g.fill, g.re0, g.re1, g.n0, g.n1 = fill, re0, re1, n0, n1
    return g


def ghost_ring(x, y, dashed=False, color=None, r=0.09):
    """A hypothetical zero: an outline only (rogue), dashed for its mirror twin. Never filled."""
    c = Circle(radius=r, color=color or C.rogue, stroke_width=2.6).move_to([x, y, 0])
    return DashedVMobject(c, num_dashes=8, dashed_ratio=0.55) if dashed else c


def live(m, fn, *windows):
    """Rebuild fn(t) every frame inside each window; hold it still in between."""
    held = []
    for a, b in windows:
        if held:
            m.remove(held[-1], at=a)
        held.append(m.redraw(fn, during=(a, b)))
    return held


def smooth01(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def bump(u):
    """0 → 1 → 0 over u in [0, 1]."""
    return np.sin(np.pi * np.clip(u, 0.0, 1.0))


# ── s07, s08: zeta(s) as a tower of terms 1/n^s ──
TX, TW, TB, TSC = -4.3, 1.3, -3.1, 1.2               # tower centre x, width, floor y, Manim units per unit of total
GX0, GX1 = TX - 0.95, TX + 1.75                       # the gridlines' span
SL0, SL1, SLY = 0.6, 4.6, 0.3                         # the s slider: x of s = 1 and of s = 2, and its height
N_EXACT, N_BLOCKS = 10_000, 60                        # terms summed exactly; terms drawn one by one (then one tail)
N_END = 1e12                                          # s07 ends on 10^12 terms at s = 2 (s08 opens on that frame)
_NS = np.arange(1, N_EXACT + 1, dtype=float)


def partial(N, s):
    """S_N(s) = sum_{n <= N} n^-s for real N >= 0 (past N_EXACT by the midpoint rule, error < 1e-9)."""
    k = int(min(N, N_EXACT))
    head = float(np.sum(_NS[:k] ** -s))
    if N <= N_EXACT:
        return head
    a, b = N_EXACT + 0.5, N + 0.5
    return head + (np.log(b / a) if abs(s - 1) < 1e-9 else (b ** (1 - s) - a ** (1 - s)) / (1 - s))


def sx(s):
    return SL0 + (SL1 - SL0) * (float(s) - 1.0)


def tower_grid():
    """Faint gridlines at totals 1-5, their numbers, and the floor. Parts: .lines, .nums, .floor."""
    lines = VGroup(*[Line([GX0, TB + TSC * k, 0], [GX1, TB + TSC * k, 0], color=C.faint, stroke_width=1.4)
                     for k in range(1, 6)])
    nums = VGroup(*[tex(str(k), size=28, color=C.muted).move_to([GX0 - 0.25, TB + TSC * k, 0]) for k in range(1, 6)])
    floor_ = Line([GX0, TB, 0], [GX1, TB, 0], color=C.axis, stroke_width=2.0)
    g = VGroup(lines, nums, floor_)
    g.lines, g.nums, g.floor = lines, nums, floor_
    return g


def tower_mob(N, s):
    """Blocks of height 1/n^s for n <= N (shades alternate), then one tail block for the rest. Parts: .blocks, .tail."""
    blocks, tail = VGroup(), VGroup()
    y = TB
    for n in range(1, min(int(np.ceil(N)), N_BLOCKS) + 1):
        hgt = TSC * n ** -s * min(1.0, N - (n - 1))
        if hgt <= 1e-4 or y > 4.3:
            break
        gap = min(0.014, 0.25 * hgt)
        r = Rectangle(width=TW, height=max(hgt - gap, 1e-4), stroke_width=0, fill_color=C.zeta,
                      fill_opacity=0.95 if n % 2 else seen(0.55))
        r.move_to([TX, y + (hgt - gap) / 2, 0])
        blocks.add(r)
        y += hgt
    if N > N_BLOCKS and y < 4.3:
        top = min(TB + TSC * partial(N, s), 4.4)
        r = Rectangle(width=TW, height=max(top - y, 1e-4), stroke_width=0, fill_color=C.zeta, fill_opacity=seen(0.75))
        tail.add(r.move_to([TX, (y + top) / 2, 0]))
    g = VGroup(blocks, tail)
    g.blocks, g.tail = blocks, tail
    return g


def needle_mob(N, s):
    """The running total: a short needle at the tower's top and its value (capped below the frame's top)."""
    tot = partial(N, s)
    y = min(TB + TSC * tot, 3.3)
    line = Line([TX + TW / 2, y, 0], [TX + TW / 2 + 0.55, y, 0], color=C.text, stroke_width=2.4)
    val = DecimalNumber(tot, num_decimal_places=3, font_size=34, color=C.text)
    val.next_to(line, RIGHT, buff=0.12)
    return VGroup(line, val)


def slider_mobs():
    """The s slider's track and its end marks 1 and 2. Parts: .track, .ends."""
    track = Line([SL0, SLY, 0], [SL1, SLY, 0], color=C.muted, stroke_width=2.0)
    ends = VGroup(tex("1", size=30, color=C.muted).move_to([SL0, SLY - 0.35, 0]),
                  tex("2", size=30, color=C.muted).move_to([SL1, SLY - 0.35, 0]),
                  Line([SL0, SLY - 0.08, 0], [SL0, SLY + 0.08, 0], color=C.muted, stroke_width=2),
                  Line([SL1, SLY - 0.08, 0], [SL1, SLY + 0.08, 0], color=C.muted, stroke_width=2))
    g = VGroup(track, ends)
    g.track, g.ends = track, ends
    return g


def knob_mob(s):
    v = float(s)
    dot = Dot([sx(v), SLY, 0], radius=0.11, color=C.s_in)
    head = tex(r"s=", size=36, color=C.s_in)
    val = DecimalNumber(v, num_decimal_places=2, font_size=36, color=C.s_in)
    val.next_to(head, RIGHT, buff=0.1).set_y(head[0][1].get_y())
    return VGroup(dot, VGroup(head, val).move_to([sx(v), SLY + 0.48, 0]))


def series_eq():
    """zeta(s) = 1 + 1/2^s + 1/3^s + ... = sum 1/n^s, top right (s07; s08 takes it apart)."""
    eq = tex(r"\zeta(s)", r"=", r"1", r"+\frac{1}{2^s}", r"+\frac{1}{3^s}", r"+\cdots", r"=\sum_{n\ge1}\frac{1}{n^s}",
             size=46, colors={0: C.zeta})
    return pin(eq, top=3.55, left=-1.0)


def series_results():
    """s07's results. Parts: .r1 (s = 1: inf), .r2 (s = 2: pi^2/6), .euler, .lim (dashed line at pi^2/6), .pi6."""
    r1 = tex(r"s=1", r":\ \infty", size=40, colors={0: C.s_in})
    r2 = tex(r"s=2", r":\ \frac{\pi^2}{6}", size=40, colors={0: C.s_in})
    pin(r1, top=-0.75, left=SL0)
    pin(r2, top=-1.6, left=SL0)
    euler = caps(r"L. Euler $\cdot$ 1734", 34, C.ink)
    euler.move_to([SL0 + 2.35 + euler.width / 2, r2.get_center()[1], 0])
    y_lim = TB + TSC * np.pi ** 2 / 6
    lim = DashedLine([GX0, y_lim, 0], [TX + TW / 2, y_lim, 0], color=C.text, stroke_width=2.0, dash_length=0.1)
    pi6 = tex(r"\frac{\pi^2}{6}", size=40)
    pi6.move_to([TX + TW / 2 + 0.67 + pi6.width / 2, y_lim + 0.66, 0])
    g = VGroup(r1, r2, euler, lim, pi6)
    g.r1, g.r2, g.euler, g.lim, g.pi6 = r1, r2, euler, lim, pi6
    return g


# ── sieve colors (s04, s05, s08): a composite takes the color of its smallest prime factor; primes turn gold ──
def spf(n):
    """Smallest prime factor of n >= 2."""
    for p in range(2, int(n ** 0.5) + 1):
        if n % p == 0:
            return p
    return n


def sieve_color(p):
    return {2: C.sieve2, 3: C.sieve3, 5: C.sieve5, 7: C.sieve7}.get(p, C.prime)


# ── s09, s10: the s-plane (input, left panel) and the output plane (right panel) where each term n^-s is an arrow ──
SP_O = np.array([-5.65, -2.6, 0.0])                   # s = 0 in the s-plane panel
SP_K = 0.72                                           # Manim units per unit of s
SP_SIG, SP_T = (-1.0, 3.0), (-0.5, 7.0)               # the panel's ranges of sigma and t
OP_O = np.array([-0.6, -1.1, 0.0])                    # output 0, at rest
OP_U = 5.0                                            # Manim units per unit of output, at rest
OP_BOX = (-2.9, 6.5, -3.45, 2.15)                     # the output panel (x0, x1, y0, y1); its drawing is clipped to it
OP_Q, OP_K = np.array([2.0, -0.5, 0.0]), 3.0          # the push puts zeta(s) here, magnified 3x
S_SPIRAL = 1.4 + 6.0j                                 # the probe's last stop


@lru_cache(maxsize=1)
def zeta_spiral():
    from zmath import zeta
    return complex(zeta(S_SPIRAL))                    # 0.89936 + 0.21724i (mpmath agrees)


def s_xy(s):
    return SP_O + SP_K * np.array([np.real(s), np.imag(s), 0.0])


def splane_mob():
    """The s-plane panel: unit grid, axes, ticks 1 2 and 2 4 6, Re and Im. Parts: .grid, .axes, .ticks."""
    (a0, a1), (b0, b1) = SP_SIG, SP_T
    grid = VGroup(*[Line(s_xy(complex(a, b0)), s_xy(complex(a, b1)), color=C.grid_minor, stroke_width=1.2)
                    for a in range(int(a0), int(a1) + 1) if a != 0],
                  *[Line(s_xy(complex(a0, b)), s_xy(complex(a1, b)), color=C.grid_minor, stroke_width=1.2)
                    for b in range(1, int(b1) + 1)])
    axes = VGroup(Line(s_xy(complex(a0, 0)), s_xy(complex(a1, 0)), color=C.axis, stroke_width=2.0),
                  Line(s_xy(complex(0, b0)), s_xy(complex(0, b1)), color=C.axis, stroke_width=2.0))
    ticks = VGroup(*[tex(str(a), size=26, color=C.muted).move_to(s_xy(complex(a, 0)) + [0.0, -0.26, 0]) for a in (1, 2)],
                   *[tex(str(b), size=26, color=C.muted).move_to(s_xy(complex(0, b)) + [-0.24, 0.0, 0]) for b in (2, 4, 6)],
                   tex(r"\mathrm{Re}", size=26, color=C.muted).move_to(s_xy(complex(a1, 0)) + [-0.05, 0.25, 0]),
                   tex(r"\mathrm{Im}", size=26, color=C.muted).move_to(s_xy(complex(0, b1)) + [0.32, -0.05, 0]))
    g = VGroup(grid, axes, ticks)
    g.grid, g.axes, g.ticks = grid, axes, ticks
    return g


def probe_mob(s, sig=1.0, tt=1.0, to_xy=None):
    """The probe s (dot and label), with dashed projections to the axes labeled sigma and t (opacities sig, tt).
    to_xy maps s to the screen (default: the s09 panel)."""
    to_xy = to_xy or s_xy
    p = to_xy(s)
    g = VGroup()
    foot, side = to_xy(complex(np.real(s), 0)), to_xy(complex(0, np.imag(s)))
    sig = sig * min(1.0, abs(np.real(s)) / 0.4)          # a projection fades out as it shrinks to nothing
    tt = tt * min(1.0, abs(np.imag(s)) / 0.4)
    if sig > 0.01 and np.linalg.norm(p - foot) > 0.08:
        g.add(DashedLine(p, foot, color=C.s_in, stroke_width=1.8, dash_length=0.07).set_opacity(sig),
              tex(r"\sigma", size=30, color=C.s_in).move_to(foot + [0.0, -0.58, 0]).set_opacity(sig))
    if tt > 0.01 and np.linalg.norm(p - side) > 0.08:
        g.add(DashedLine(p, side, color=C.s_in, stroke_width=1.8, dash_length=0.07).set_opacity(tt),
              tex(r"t", size=30, color=C.s_in).move_to(side + [0.24, 0.25, 0]).set_opacity(tt))
    g.add(Dot(p, radius=0.08, color=C.s_in), tex("s", size=32, color=C.s_in).move_to(p + [0.22, 0.24, 0]))
    return g


def _view(u):
    zc = u * zeta_spiral()
    q = (OP_O + OP_U * np.array([zc.real, zc.imag, 0.0])) * (1 - u) + OP_Q * u
    return zc, q, OP_U * OP_K ** u


def op_map(z, u=0.0):
    """Output-plane points z → screen; u in [0, 1] pushes in on zeta(S_SPIRAL)."""
    zc, q, sc = _view(u)
    d = sc * (np.asarray(z, complex) - zc)
    return np.stack([q[0] + d.real, q[1] + d.imag, np.zeros(np.shape(d))], axis=-1)


def clip_seg(p, q, box=OP_BOX):
    """Liang-Barsky: the part of segment pq inside box, as (p', q', q_inside), or None."""
    x0, x1, y0, y1 = box
    d = q - p
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-d[0], p[0] - x0), (d[0], x1 - p[0]), (-d[1], p[1] - y0), (d[1], y1 - p[1])):
        if abs(pk) < 1e-12:
            if qk < 0:
                return None
        elif pk < 0:
            t0 = max(t0, qk / pk)
        else:
            t1 = min(t1, qk / pk)
    if t0 > t1:
        return None
    return p + t0 * d, p + t1 * d, t1 >= 1.0


def oplane_mob(u=0.0, step=0.2):
    """The output plane's grid (every 0.2) and axes, clipped to its panel, under the push u."""
    x0, x1, y0, y1 = OP_BOX
    zc, q, sc = _view(u)
    grid, axes = VGroup(), VGroup()
    for k, (lo, hi, c0, c) in enumerate(((x0, x1, q[0], zc.real), (y0, y1, q[1], zc.imag))):
        a_lo, a_hi = c + (lo - c0) / sc, c + (hi - c0) / sc
        for a in np.arange(np.ceil(a_lo / step) * step, a_hi, step):
            v = c0 + sc * (a - c)
            ends = ([v, y0, 0], [v, y1, 0]) if k == 0 else ([x0, v, 0], [x1, v, 0])
            if abs(a) < 1e-9:
                axes.add(Line(*ends, color=C.axis, stroke_width=2.0))
            else:
                grid.add(Line(*ends, color=C.grid_minor, stroke_width=1.2))
    one = op_map(1.0, u)
    ticks = VGroup()
    if x0 + 0.2 < one[0] < x1 - 0.2 and y0 + 0.4 < one[1] < y1:
        ticks.add(tex("1", size=26, color=C.muted).move_to(one + [0.12, -0.28, 0]))
    g = VGroup(grid, axes, ticks)
    g.grid, g.axes, g.ticks = grid, axes, ticks
    return g


def spiral_mob(s, N, u=0.0, v=1.0, n_tips=12, dot=True, to_xy=None, box=OP_BOX, scale=1.0):
    """The terms n^-s for n <= N as arrows (N may be fractional: the last one grows). v = 0: all from 0, a fan;
    v = 1: tip to tail, through the partial sums. Past n_tips arrows, the chain is one polyline. Clipped to box.
    to_xy maps output values to the screen (default: the s09 output panel under the push u); scale thins strokes."""
    f = to_xy or (lambda z: op_map(z, u))
    N = float(N)
    n_full = int(np.floor(N))
    k = n_full + (1 if N - n_full > 1e-6 else 0)
    if k == 0:
        return VGroup()
    n = np.arange(1, k + 1, dtype=float)
    terms = n ** (-complex(s))
    if k > n_full:
        terms[-1] *= N - n_full
    S = np.concatenate([[0], np.cumsum(terms)])
    P0, P1 = f(v * S[:-1]), f(v * S[:-1] + terms)
    g = VGroup()
    for i in range(min(k, n_tips)):
        c = clip_seg(P0[i], P1[i], box)
        if c is None:
            continue
        a, b, inside = c
        L = float(np.linalg.norm(b - a))
        if L < 1e-3:
            continue
        w = max(1.6, 3.2 - 0.12 * i) * scale
        if inside and L > 0.12 * scale:
            g.add(Arrow(a, b, buff=0, color=C.zeta, stroke_width=w, tip_length=min(0.2 * scale, 0.32 * L),
                        max_tip_length_to_length_ratio=0.5, max_stroke_width_to_length_ratio=1000))
        else:
            g.add(Line(a, b, color=C.zeta, stroke_width=w))
    if k > n_tips:                                      # v = 1 here: the chain only grows past n_tips after the fan
        pts = f(S[n_tips:])
        x0, x1, y0, y1 = box
        ok = (pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1)
        cuts = np.flatnonzero(np.diff(ok.astype(int))) + 1
        for run, keep in zip(np.split(pts, cuts), np.split(ok, cuts)):
            if keep[0] and len(run) > 1:
                g.add(VMobject(stroke_color=C.zeta, stroke_width=1.6 * scale).set_points_as_corners(run))
    end = f(S[-1])
    x0, x1, y0, y1 = box
    if dot and v > 0.99 and x0 < end[0] < x1 and y0 < end[1] < y1:
        g.add(Dot(end, radius=0.045 * max(scale, 0.7), color=C.text))
    return g


def zeta_mark(u=1.0):
    """zeta(1.4 + 6i): a purple dot in a white ring."""
    p = op_map(zeta_spiral(), u)
    return VGroup(Circle(radius=0.2, color=C.text, stroke_width=2.0).move_to(p), Dot(p, radius=0.07, color=C.zeta))


def s_formula():
    """s = sigma + it, top left (s09, s10)."""
    s_eq = tex(r"s", r"=", r"\sigma", r"+i", r"t", size=46, colors={0: C.s_in, 2: C.s_in, 4: C.s_in})
    return pin(s_eq, top=3.5, left=-6.4)


def term_formula():
    """1/n^s = n^-sigma e^(-i theta), theta = t ln n, labeled length and angle. Parts: .term, .ang, .length, .angle."""
    term = tex(r"\frac{1}{n^s}", r"=", r"n^{-\sigma}", r"\,e^{-i\theta}", size=44)
    ang = tex(r"\theta", r"=", r"t", r"\ln n", size=40)
    row = VGroup(term, ang).arrange(RIGHT, buff=0.8)
    ang.align_to(term[1], DOWN).shift(0.04 * DOWN)
    pin(row, top=3.55, left=-2.4)
    length = lab("length", 28, C.muted).next_to(term[2], DOWN, buff=0.18)
    angle = lab("angle", 28, C.muted).next_to(ang, DOWN, buff=0.18)
    g = VGroup(term, ang, length, angle)
    g.term, g.ang, g.length, g.angle = term, ang, length, angle
    return g


def re_gt1_mobs():
    """The half-plane Re s > 1 in the s-plane panel: tint, dashed edge, label. Parts: .half, .line, .label."""
    (a0, a1), (b0, b1) = SP_SIG, SP_T
    lo, hi = s_xy(complex(1.0, b0)), s_xy(complex(a1, b1))
    half = Rectangle(width=hi[0] - lo[0], height=hi[1] - lo[1], stroke_width=0, fill_color=C.s_in,
                     fill_opacity=seen(0.12)).move_to((lo + hi) / 2)
    line = DashedLine(s_xy(complex(1.0, b0)), s_xy(complex(1.0, b1)), color=C.s_in, stroke_width=2.0, dash_length=0.1)
    label = tex(r"\mathrm{Re}\,s>1", size=26, color=C.s_in).move_to(s_xy(complex(2.25, 3.3)))
    g = VGroup(half, line, label)
    g.half, g.line, g.label = half, line, label
    return g


def zeta_label(u=1.0):
    """zeta(1.4 + 6i) ~ 0.90 + 0.22i, right of the spiral, with a thin leader. Parts: .leader, .card."""
    v = zeta_spiral()
    p = op_map(v, u)
    card = carded(VGroup(tex(r"\zeta(1.4+6i)", size=34, color=C.zeta),
                         tex(r"\approx %.2f+%.2fi" % (v.real, v.imag), size=34)).arrange(DOWN, buff=0.12,
                                                                                         aligned_edge=LEFT))
    card.move_to([4.15 + card.width / 2, p[1], 0])
    leader = Line(p + [0.24, 0, 0], [4.05, p[1], 0], color=C.muted, stroke_width=1.4)
    g = VGroup(leader, card)
    g.leader, g.card = leader, card
    return g


# ── s10, s11: the whole s-plane, colored by shaders/zeta_domain.frag underneath a redrawn grid ──
FRAME_BOX = (-7.2, 7.2, -4.1, 4.1)
PANEL_BOX = (float(s_xy(SP_SIG[0])[0]), float(s_xy(SP_SIG[1])[0]), float(s_xy(1j * SP_T[0])[1]),
             float(s_xy(1j * SP_T[1])[1]))                 # the s09 panel, as a clip box


def plane_xy(s, O, U):
    """s → screen, with s = 0 at O and U Manim units per 1."""
    s = np.asarray(s, complex)
    return np.stack([O[0] + U * s.real, O[1] + U * s.imag, np.zeros(np.shape(s))], axis=-1)


def plane_grid(O, U, box=FRAME_BOX, mix=0.0):
    """Unit gridlines and the axes of the s-plane (s = 0 at O, U units per 1), clipped to box. mix = 0 is the s09
    panel's look (blue minor lines); mix = 1 is the look over color (faint white lines, softer axes)."""
    x0, x1, y0, y1 = box
    minor = interpolate_color(ManimColor(C.grid_minor), ManimColor(C.text), mix)
    m_op, a_op = 1.0 + (0.22 - 1.0) * mix, 1.0 + (0.6 - 1.0) * mix
    grid, axes = VGroup(), VGroup()
    eps = 1e-6
    for k, (lo, hi, o) in enumerate(((x0, x1, O[0]), (y0, y1, O[1]))):
        for a in range(int(np.ceil((lo - o) / U - eps)), int(np.floor((hi - o) / U + eps)) + 1):
            v = o + U * a
            ends = ([v, y0, 0], [v, y1, 0]) if k == 0 else ([x0, v, 0], [x1, v, 0])
            if a == 0:
                axes.add(Line(*ends, color=C.axis, stroke_width=2.0, stroke_opacity=a_op))
            else:
                grid.add(Line(*ends, color=minor, stroke_width=1.2, stroke_opacity=m_op))
    g = VGroup(grid, axes)
    g.grid, g.axes = grid, axes
    return g


def wheel_mob(r0=0.2, r1=0.48, n=72):
    """The hue key: direction of f(s) → color, as in the shader (zmath.domain_rgb, |f| = 1.4)."""
    from zmath import domain_rgb
    secs = VGroup()
    for k in range(n):
        a0 = TAU * k / n
        rgb = np.asarray(domain_rgb(np.array([1.4 * np.exp(1j * (a0 + PI / n))]))).reshape(-1)[:3]
        secs.add(AnnularSector(inner_radius=r0, outer_radius=r1, angle=TAU / n + 0.004, start_angle=a0,
                               fill_color=ManimColor.from_rgb(rgb), fill_opacity=1.0, stroke_width=0))
    return secs


def band_key_mob(width=2.6, height=0.3, lo=-1.0, hi=4.0, n=100):
    """The size key: |f| from 2^lo to 2^hi at a fixed direction; the brightness steps at every doubling."""
    from zmath import domain_rgb
    xs = np.linspace(lo, hi, n + 1)
    mid = (xs[:-1] + xs[1:]) / 2
    rgb = np.asarray(domain_rgb(2.0 ** mid + 0j)).reshape(n, -1)[:, :3]
    strip = VGroup(*[Rectangle(width=width / n + 0.003, height=height, stroke_width=0,
                               fill_color=ManimColor.from_rgb(c), fill_opacity=1.0) for c in rgb]).arrange(RIGHT, buff=0)
    ticks = VGroup()
    for e in range(int(np.ceil(lo)), int(hi) + 1):
        if e < 0:
            continue
        x = strip.get_left()[0] + width * (e - lo) / (hi - lo)
        ticks.add(tex(str(2 ** e), size=24, color=C.muted).move_to([x, strip.get_bottom()[1] - 0.2, 0]))
    g = VGroup(strip, ticks)
    g.strip, g.ticks = strip, ticks
    return g


# ── s10's zeta view, shared with s11: framing D, the Re s = 1 line, the probe and the partial-sums inset ──
ZGEO = ((-1.8, -3.2), 0.8)                   # s = 0 at (-1.8, -3.2), 0.8 units per 1: sigma -6.6..11.1, t -1..9
S_LEFT = 0.6 + 6.0j                          # where s10 drags the probe, past Re s = 1
INSET = (2.95, 6.6, -3.55, -0.4)             # the partial-sums inset (x0, x1, y0, y1)
IK, ZC = 0.6, 0.85 + 0.33j                   # its scale, and the output value at its centre


def to_d(z):
    return plane_xy(z, *ZGEO)


def to_inset(z):
    c = np.array([(INSET[0] + INSET[1]) / 2, (INSET[2] + INSET[3]) / 2])
    d = IK * (np.asarray(z, complex) - ZC)
    return np.stack([c[0] + d.real, c[1] + d.imag, np.zeros(np.shape(d))], axis=-1)


def re1_mobs():
    """The dashed line Re s = 1 in framing D, with its carded label. Parts .line .label."""
    line = DashedLine(to_d(complex(1, -1.2)), to_d(complex(1, 9.2)), color=C.text, stroke_width=2.4, dash_length=0.12)
    label = carded(tex(r"\mathrm{Re}\,s=1", size=32), buff=0.08)
    label.move_to(to_d(complex(1, 8.2)) + [label.width / 2 + 0.15, 0, 0])
    g = VGroup(line, label)
    g.line, g.label = line, label
    return g


def inset_mobs():
    """The inset's frame and caption. Parts .frame .cap; .box is the clip box for the spiral."""
    frame = Rectangle(width=INSET[1] - INSET[0], height=INSET[3] - INSET[2], stroke_color=C.faint, stroke_width=1.4,
                      fill_color=C.bg, fill_opacity=1.0)
    frame.move_to([(INSET[0] + INSET[1]) / 2, (INSET[2] + INSET[3]) / 2, 0])
    cap = lab("partial sums", 24, C.muted).move_to([INSET[0] + 0.95, INSET[3] - 0.24, 0])
    g = VGroup(frame, cap)
    g.frame, g.cap = frame, cap
    g.box = (INSET[0] + 0.05, INSET[1] - 0.05, INSET[2] + 0.05, INSET[3] - 0.45)
    return g


def inset_spiral(s, N):
    return spiral_mob(s, N, to_xy=to_inset, box=inset_mobs().box, scale=0.75, n_tips=8)


def zeta_tag():
    z = tex(r"\zeta(s)", r"=", r"\sum n^{-s}", size=40, colors={0: C.zeta})
    pin(z, top=3.5, left=-6.4)
    return z


# ── s11's end frame, shared with s12: framing E (centred on 1/2), the pole, the symmetry s <-> 1 - s, the equation ──
ZGEO_E = ((-0.4, -0.3), 0.8)                 # s = 1/2 at the centre: sigma -8.4..9.4, t -4.6..5.4
S_SYM = 2.5 + 2.5j                           # the point s whose partner 1 - s is shown


def to_e(z):
    return plane_xy(z, *ZGEO_E)


def pole_mob(O, U, label=True):
    """The pole of zeta at s = 1: a white cross, with a carded 's = 1'."""
    p = plane_xy(1.0 + 0j, O, U)
    d = 0.13
    x = VGroup(Line(p + [-d, -d, 0], p + [d, d, 0]), Line(p + [-d, d, 0], p + [d, -d, 0]))
    x.set_stroke(C.text, width=3.2)
    if not label:
        return x
    tag = carded(tex(r"s=1", size=28), buff=0.06).move_to(p + [0.55, 0.3, 0])
    return VGroup(x, tag)


def sym_mobs():
    """s and 1 - s in framing E, joined through 1/2 by a dashed line. Parts .line .half .s .s1"""
    a, b, h = to_e(S_SYM), to_e(1 - S_SYM), to_e(0.5 + 0j)
    line = DashedLine(a, b, color=C.text, stroke_width=2.0, dash_length=0.1)
    half = VGroup(Dot(h, radius=0.06, color=C.text), carded(tex(r"\tfrac12", size=30), buff=0.04).move_to(h + [-0.32, 0.12, 0]))
    s = VGroup(Dot(a, radius=0.09, color=C.s_in), carded(tex("s", size=36, color=C.s_in), buff=0.05).move_to(a + [0.27, 0.27, 0]))
    s1 = VGroup(Dot(b, radius=0.09, color=C.s_in), carded(tex(r"1-s", size=36, color=C.s_in), buff=0.05).move_to(b + [-0.55, -0.2, 0]))
    g = VGroup(line, half, s, s1)
    g.line, g.half, g.s, g.s1 = line, half, s, s1
    return g


def feq_mob():
    """The functional equation on a black card, pinned top left. Parts: [card, eq]; eq[3] is the sine."""
    eq = tex(r"\zeta(s)", r"=", r"2^s\pi^{s-1}", r"\sin\!\left(\tfrac{\pi s}{2}\right)", r"\Gamma(1-s)",
             r"\zeta(1-s)", size=40, colors={0: C.zeta, 5: C.zeta})
    pin(eq, top=3.55, left=-6.4)
    card = BackgroundRectangle(eq, color=C.bg, fill_opacity=1.0, buff=0.16)
    g = VGroup(card, eq)
    g.card, g.eq = card, eq
    return g


# ── s12's trivial zeros (framing E), shared with s13: the sine band under the plane, links, rings, tags ──
TRIV = (-2, -4, -6, -8)
SIN_Y, SIN_A = -3.25, 0.5                    # the sine's axis and amplitude in the band
TRIV_GAIN = 150.0                            # u_gain that lifts the dark left half-plane, so its pinwheels show


def trivial_mobs():
    """Parts: .band (black strip + top rule), .curve (sin(pi s / 2) for sigma -8.45..-1), .nums, .links, .rings,
    .sin_eq, .then, .tag. Each zero's link, ring and number share an index with TRIV."""
    ex = lambda v: ZGEO_E[0][0] + ZGEO_E[1] * v                                 # noqa: E731
    ry = ZGEO_E[0][1]
    rect = Rectangle(width=14.6, height=1.7, stroke_width=0, fill_color=C.bg, fill_opacity=1.0).move_to([0, -3.3, 0])
    rule = Line([-7.3, -2.45, 0], [7.3, -2.45, 0], color=C.faint, stroke_width=1.2)
    band = VGroup(rect, rule)
    sig = np.linspace(-8.45, -1.0, 240)
    curve = VMobject(color=C.trivial, stroke_width=3.0)
    curve.set_points_smoothly(np.column_stack([ex(sig), SIN_Y + SIN_A * np.sin(np.pi * sig / 2), np.zeros_like(sig)]))
    axis = Line([ex(-8.6), SIN_Y, 0], [ex(-0.8), SIN_Y, 0], color=C.muted, stroke_width=1.4)
    nums = VGroup(*[carded(tex(str(v), size=26), buff=0.04).move_to([ex(v), ry - 0.5, 0]) for v in TRIV])
    links = VGroup(*[DashedLine([ex(v), SIN_Y, 0], [ex(v), ry - 0.75, 0], color=C.text, stroke_width=2.2,
                                dash_length=0.08) for v in TRIV])
    rings = VGroup(*[VGroup(Circle(radius=0.17, color=C.bg, stroke_width=7.0), Circle(radius=0.17, color=C.trivial,
                                                                                   stroke_width=3.4)).move_to([ex(v), ry, 0])
                     for v in TRIV])
    sin_eq = tex(r"\sin\!\left(\tfrac{\pi s}{2}\right)", r"=0", size=34, colors={0: C.trivial})
    sin_eq.move_to([0.6 + sin_eq.width / 2, -2.95, 0])
    then = tex(r"\Rightarrow\ \zeta(-2)=\zeta(-4)=\cdots=0", size=30)
    then.next_to(sin_eq, DOWN, buff=0.22, aligned_edge=LEFT)
    tag = carded(lab("trivial zeros", 30, C.trivial), buff=0.08).move_to([ex(-5), ry + 0.62, 0])
    g = VGroup(band, axis, curve, nums, links, rings, sin_eq, then, tag)
    g.band, g.axis, g.curve, g.nums, g.links, g.rings = band, axis, curve, nums, links, rings
    g.sin_eq, g.then, g.tag = sin_eq, then, tag
    return g


# ── s13: the critical strip and the flight up the critical line (shared with s14) ──
FLY_U, FLY_XC = 1.6, 0.8                     # units per 1 during the flight; screen x of Re s = 1/2
GHOST = 0.8 + 39.2j                          # s13's hypothetical off-line zero (between the 6th and 7th zeros)


def view_O(xc, tc, U):
    """The origin O for a view with Re s = 1/2 at screen x = xc and height tc at screen y = 0."""
    return (xc - 0.5 * U, -tc * U)


def strip_overlay(O, U, fill=1.0, line=1.0, lit=(), crit_w=3.0):
    """The strip 0 < Re s < 1 (crit fill, Re 0 faint green, Re 1 white), the critical line, and white rings with
    carded heights on the first len(lit) zeros (lit[k] = opacity). Parts .fill .edges .line .rings"""
    x0, x1, xh = O[0], O[0] + U, O[0] + 0.5 * U
    f = Rectangle(width=U, height=8.6, stroke_width=0, fill_color=C.crit, fill_opacity=0.18 * fill).move_to(
        [(x0 + x1) / 2, 0, 0])
    edges = VGroup(Line([x0, -4.3, 0], [x0, 4.3, 0], color=C.crit, stroke_width=1.4, stroke_opacity=0.6 * fill),
                   Line([x1, -4.3, 0], [x1, 4.3, 0], color=C.text, stroke_width=2.2, stroke_opacity=fill))
    ln = Line([xh, -4.3, 0], [xh, 4.3, 0], color=C.crit, stroke_width=crit_w, stroke_opacity=line)
    rings = VGroup()
    for k, a in enumerate(lit):
        if a <= 0.0:
            continue
        y = O[1] + U * float(GAM[k])
        if not -4.6 < y < 4.6:
            continue
        p = np.array([xh, y, 0.0])
        r = VGroup(Circle(radius=0.2, color=C.bg, stroke_width=7.0, stroke_opacity=a),
                   Circle(radius=0.2, color=C.text, stroke_width=3.0, stroke_opacity=a)).move_to(p)
        lab_ = tex("%.4f" % float(GAM[k]), size=30)
        card = VGroup(BackgroundRectangle(lab_, color=C.bg, fill_opacity=a, buff=0.06), lab_.set_opacity(a))
        card.move_to([x1 + 0.25 + card.width / 2, y, 0])
        rings.add(VGroup(r, card))
    g = VGroup(f, edges, ln, rings)
    g.fill, g.edges, g.line, g.rings = f, edges, ln, rings
    return g


def strip_tags():
    """s13's HUD: strip, line and the zeros' form, stacked top left on a black card. Parts .strip .line .rho .card"""
    a = VGroup(tex(r"0<\mathrm{Re}\,s<1", size=36), lab("critical strip", 28, C.crit)).arrange(RIGHT, buff=0.3)
    b = VGroup(tex(r"\mathrm{Re}\,s=\tfrac12", size=36), lab("critical line", 28, C.crit)).arrange(RIGHT, buff=0.3)
    c = VGroup(tex(r"\rho=\tfrac12+i\gamma", size=36, color=C.zero), lab("each zero", 28, C.muted)).arrange(RIGHT, buff=0.3)
    col = VGroup(a, b, c).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
    pin(col, top=3.55, left=-6.4)
    card = BackgroundRectangle(col, color=C.bg, fill_opacity=1.0, buff=0.18)
    g = VGroup(card, col)
    g.card, g.strip, g.line, g.rho = card, a, b, c
    return g
