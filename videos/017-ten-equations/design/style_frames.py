"""Style frames for video 017, "10 Equations That Run the Modern World": stills at 1920x1080, rendered through aion.

    uv run python videos/017-ten-equations/design/style_frames.py          # all → design/style_frames/*.png
    uv run python videos/017-ten-equations/design/style_frames.py 3 7      # only frames 3 and 7

Each frame is an `@scene(0, 10)` rendered with `sd.comp((1920, 1080), 30).frame(t, ...)`: the same theme, LaTeX, Manim
rasteriser and GPU compositor as the video. Every curve and field comes from sims.py / eqdata.py (seeded numpy).
One process per frame (2 cores, little RAM). Frames 2 (the wall) and 13 (the carousel) are built from the chapter
frames' PNGs, so they render last.

Screen language (no boards, no boxes): every frame is one full-bleed composition. The simulation owns the frame;
equations float in its open space; text over a busy simulation sits on a feathered shade (an invisible darkening, never
a rectangle). Chapter progress is the top rail (`rail`), not a counter. Glow is for graphics only, never text.

     1 in_s01   Fourier's hot bar, the heat equation, the temperature splitting into cosine modes in depth
     2 in_s02   the wall: ten live windows with hue rules, names and years; the 1763 → 1973 timeline
     3 c01_s03  dipole radiation filling the frame, the E ⊥ B wave in oblique 3D; the four laws and c = 1/√(μ₀ε₀)
     4 c02_s03  the ray-traced black hole (BlackHoleLayer); the field equations as shape = matter
     5 c03_s02  a wave packet as a phase-coloured helix tunnelling through a wall; iħ∂ψ/∂t = Ĥψ, P = |ψ|²
     6 c04_s02  lattice-Boltzmann vortex street behind a cylinder; Navier–Stokes with tagged terms
     7 c05_s02  epicycles drawing π; the spectrum and the Fourier transform
     8 c06_s01  a light clock at rest and one moving at 0.6c, the triangle; Δt′ = Δt/√(1−v²/c²)
     9 c07_s01  gradient descent on a lit 3D loss surface (pyvista); the update rule and the falling error
    10 c08_s02  a 16-point constellation with noise clouds on a tilted plane; C = B log₂(1+S/N), capacity curve
    11 c09_s01  1,000 people, 10 ill, 9 + 89 positives; the 98 positives, 9 %, Bayes' rule
    12 c10_s02  2,000 random price paths fanning into a bell; Black–Scholes and its heat-equation form
    13 out_s01  the ten windows on a carousel, linked in story order
    14          reference → design/components.png: progress rail, chapter card, type scale, palette
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np

DESIGN = Path(__file__).resolve().parent
VIDEO = DESIGN.parent
REPO = VIDEO.parent.parent
OUT = DESIGN / "style_frames"
sys.path.insert(0, str(VIDEO))

W, H, FPS, T_STILL = 1920, 1080, 30, 5.0
PX = 135.0                          # px per world unit at 1080p
XW, YH = 64 / 9, 4.0                # half frame (world units)
SAFE = 0.71                         # text-safe inset (96 px)
X0, X1, Y0, Y1 = -XW + SAFE, XW - SAFE, -YH + SAFE, YH - SAFE   # safe box: -6.40..6.40, -3.29..3.29
RAIL_Y, RAIL_X1 = Y0 - 0.01, X0 + 5.0   # the progress rail: bottom-left corner, 5 u long, on the safe box's bottom edge
COL = (2.75, X1)                  # the open column at the right where equations float in most chapters

NAMES_OUT = {1: "01_in_heat_bar", 2: "02_in_wall", 3: "03_c01_light", 4: "04_c02_black_hole", 5: "05_c03_tunnel",
             6: "06_c04_vortex", 7: "07_c05_epicycles", 8: "08_c06_light_clock", 9: "09_c07_descent",
             10: "10_c08_constellation", 11: "11_c09_test", 12: "12_c10_paths", 13: "13_out_web",
             14: "../components"}
CHAPTER_FRAMES = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]          # window W1 … W10
TILE_NAMES = ["Maxwell", "Einstein", "Schrödinger", "Navier–Stokes", "Fourier", "Time dilation", "Gradient descent",
              "Shannon", "Bayes", "Black–Scholes"]
TILE_YEARS = [1865, 1915, 1926, 1845, 1822, 1905, 1847, 1948, 1763, 1973]
CH_TITLES = ["Maxwell's equations", "Einstein's field equations", "Schrödinger's equation", "Navier--Stokes",
             "The Fourier transform", "Time dilation", "Gradient descent", "Shannon's capacity", "Bayes' theorem",
             "Black--Scholes"]


# ------------------------------------------------------------------------------------------------ setup
def _import_aion():
    """Activate video 017's theme and pull aion's names (Manim included) and the beats into this module."""
    from aion.render.project import load_video

    load_video("017", (W, H), FPS, only=["__none__"])           # theme on, no scenes imported
    import aion
    from aion.render import scenes as scene_mod

    import beats
    import eqdata
    import sims
    from theme import CHAPTERS

    g = globals()
    for k in aion.__all__:
        g.setdefault(k, getattr(aion, k))
    g.update(scene_mod=scene_mod, eq=eqdata, sm=sims, CHAPTERS=CHAPTERS, T=beats.T)


# ---------------------------------------------------------------------------------------------- helpers
def _esc(s):
    return s.replace("%", r"\%").replace("&", r"\&")


def tex(s, size=48, color=None):
    return MathTex(s, font_size=size, color=color or C.text)  # noqa: F821


def sans(s, size=28, color=None):
    return Tex(r"\textsf{" + _esc(s) + "}", font_size=size, color=color or C.text)  # noqa: F821


def caps(s, size=34, color=None):
    return Tex(r"\textsc{" + _esc(s) + "}", font_size=size, color=color or C.text)  # noqa: F821


def P3(x, y):
    return np.array([float(x), float(y), 0.0])


def _lin(h):
    c = np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _hex(lin):
    lin = np.clip(lin, 0, 1)
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in s)


def tint(color, a):
    """`color` at opacity `a` over black, mixed in linear light, as one solid hex."""
    return _hex(_lin(color) * a)


def mix(a, b, t):
    """Linear-light mix of two hex colours."""
    return _hex(_lin(a) * (1 - t) + _lin(b) * t)


def heat_ramp(v):
    """0 → black, 0.55 → the Fourier hue, 1 → near white (a heated metal ramp in the chapter's hue)."""
    v = float(np.clip(v, 0, 1))
    if v < 0.55:
        return tint(C.fourier, (v / 0.55) ** 1.4)  # noqa: F821
    return mix(C.fourier, "#FFF4E8", (v - 0.55) / 0.45)  # noqa: F821


def phase_color(a, L=0.80, Cc=0.13):
    """Domain-colouring hue for a complex phase `a` (radians), from an OKLCH wheel (even lightness)."""
    h = math.degrees(a) % 360
    aa, bb = Cc * math.cos(math.radians(h)), Cc * math.sin(math.radians(h))
    l_, m_, s_ = L + 0.3963377774 * aa + 0.2158037573 * bb, L - 0.1055613458 * aa - 0.0638541728 * bb, \
        L - 0.0894841775 * aa - 1.2914855480 * bb
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = np.array([4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
                    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                    -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s])
    return _hex(lin)


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def rgba_of(img_rgb, alpha=None):
    a = np.full(img_rgb.shape[:2], 255, np.uint8) if alpha is None else alpha
    return np.dstack([img_rgb[..., :3], a])


def feather(rgba, left=0.0, right=0.0, top=0.0, bottom=0.0):
    """Fade a raster's alpha to 0 over the given fractions of its width/height (no hard raster edges on screen)."""
    h, w = rgba.shape[:2]
    a = np.ones((h, w))
    xs, ys = np.linspace(0, 1, w)[None, :], np.linspace(0, 1, h)[:, None]
    if left:
        a = a * _smooth(xs / left)
    if right:
        a = a * _smooth((1 - xs) / right)
    if top:
        a = a * _smooth(ys / top)
    if bottom:
        a = a * _smooth((1 - ys) / bottom)
    out = rgba.copy()
    out[..., 3] = (out[..., 3] * a).astype(np.uint8)
    return out


def shade(s, cx, cy, w, h, a=0.82, z=-1):
    """An invisible darkening under text that sits on a busy simulation: black with a soft superellipse alpha.
    Full strength over the inner 80 % of (w, h), gone by 140 %. Never a visible rectangle."""
    ppu = 40
    nx, ny = max(8, int(w * 1.4 * ppu)), max(8, int(h * 1.4 * ppu))
    xx, yy = np.linspace(-1.4, 1.4, nx)[None, :], np.linspace(-1.4, 1.4, ny)[:, None]
    d = (np.abs(xx) ** 4 + np.abs(yy) ** 4) ** 0.25
    al = a * _smooth((1.4 - d) / 0.6)
    img = np.zeros((ny, nx, 4), np.uint8)
    img[..., 3] = (al * 255).astype(np.uint8)
    s.add(ArrayLayer(img, height=h * 1.4, pos=(cx, cy), z=z))  # noqa: F821


def glow(s, color, z=2, k=1.0):
    """A Manim layer whose shapes glow in `color` (accent glow on graphic payoff elements only; never text)."""
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=C.glow_r)])  # noqa: F821


def _chapter_spans():
    starts = [float(getattr(T, f"c{i:02d}_s01")) for i in range(1, 11)] + [float(T.out_s01)]  # noqa: F821
    return np.array(starts)


def rail(k, t, y=RAIL_Y, x0=X0, x1=RAIL_X1, label=True):
    """The progress rail: ten segments in the bottom-left corner, each as long as its chapter's narration.

    Past chapters: a 2.5 px line in their hue at 50 %. Future: a 1.5 px ghost line. The current chapter: a ghost track,
    a 4 px fill brightening towards the head, scene ticks, a white head in a hue ring, and the chapter's name in small
    caps just above the rail's left end. Never boxed, never glowing; it is the only UI element in the video.
    """
    st = _chapter_spans()
    durs = np.diff(st)
    gap = 0.05
    span = (x1 - x0) - gap * 9
    g = VGroup()  # noqa: F821
    xa = x0
    for i in range(10):
        w = span * durs[i] / durs.sum()
        xb = xa + w
        hue = getattr(C, CHAPTERS[i])  # noqa: F821
        if i + 1 < k:
            g.add(Line(P3(xa, y), P3(xb, y), stroke_color=tint(hue, 0.5), stroke_width=2.5))  # noqa: F821
        elif i + 1 > k:
            g.add(Line(P3(xa, y), P3(xb, y), stroke_color=tint(C.muted, 0.45), stroke_width=1.5))  # noqa: F821
        else:
            f = float(np.clip((t - st[i]) / durs[i], 0, 1))
            xf = xa + f * w
            g.add(Line(P3(xa, y), P3(xb, y), stroke_color=tint(C.muted, 0.45), stroke_width=1.5))  # noqa: F821
            n_seg = 24                                        # the fill brightens towards the head (a comet)
            for j in range(n_seg):
                a0, a1 = xa + (xf - xa) * j / n_seg, xa + (xf - xa) * (j + 1) / n_seg
                if a1 - a0 > 1e-4:
                    g.add(Line(P3(a0, y), P3(a1, y), stroke_color=tint(hue, 0.35 + 0.65 * ((j + 1) / n_seg) ** 2),  # noqa: F821
                               stroke_width=4))
            for sc in ("s02", "s03"):
                ts = float(getattr(T, f"c{k:02d}_{sc}"))  # noqa: F821
                xt = xa + w * (ts - st[i]) / durs[i]
                g.add(Line(P3(xt, y - 0.06), P3(xt, y + 0.06), stroke_color=hue if xt <= xf else C.muted,  # noqa: F821
                           stroke_width=1.5))
            g.add(Circle(radius=0.085, stroke_color=hue, stroke_width=1.5).move_to(P3(xf, y)),  # noqa: F821
                  Dot(P3(xf, y), radius=0.04, color=C.light))  # noqa: F821
            if label:
                g.add(caps(CH_TITLES[i], 20, C.text).move_to(P3(x0, y + 0.17), aligned_edge=DL))  # noqa: F821
        xa = xb + gap
    return g


def name_tag(text, hue, at=None, edge=None):
    """Lower third: a short rule in the chapter hue over a small-caps name and year. No box behind it."""
    rule = Line(LEFT * 0.35, RIGHT * 0.35, stroke_color=hue, stroke_width=3)  # noqa: F821
    g = VGroup(rule, caps(text, 30, C.text)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)  # noqa: F821
    return g.move_to(at if at is not None else P3(X0, Y1), aligned_edge=edge if edge is not None else UL)  # noqa: F821


_METRICS = {}


def _sans_metrics(size):
    """(cap height, descender depth) of CM sans at `size`, measured once."""
    if size not in _METRICS:
        hx, hg, hH = (sans(c, size).height for c in ("x", "g", "H"))
        _METRICS[size] = (hH, hg - hx)
    return _METRICS[size]


def tag_under(eqn, part, text, color=None, buff=0.16, size=22):
    """A key-word tag centred under one term of an Eqn. All tags of one equation share a typographic baseline."""
    p = eqn.part(part)
    lab = sans(text, size, color or C.muted)  # noqa: F821
    cap, depth = _sans_metrics(size)
    base = eqn.get_bottom()[1] - buff - cap
    bottom = base - (depth if any(ch in text for ch in "gjpqy") else 0.0)
    return lab.move_to(P3(p.get_center()[0], bottom), aligned_edge=DOWN)  # noqa: F821


def fit(mob, width=COL[1] - COL[0]):
    """Scale `mob` down (never up) to `width`."""
    if mob.width > width:
        mob.scale(width / mob.width)
    return mob


def legend(rows, size=30):
    """Term → key word rows (used when tags under a long equation would collide)."""
    g = VGroup(*[VGroup(tex(term, size, col), sans(word, 22, C.muted)).arrange(RIGHT, buff=0.22)  # noqa: F821
                 for term, col, word in rows])
    g.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    for row in g:                                   # align the key words in one column
        row[1].set_x(g.get_left()[0] + max(r[0].width for r in g) + 0.22 + row[1].width / 2)
    return g


def polyline(pts, color, width=3.0, opacity=1.0):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)  # noqa: F821
    v.set_points_as_corners([P3(*p) for p in pts])
    return v


def axes2(x0, y0, x1, y1):
    """Two bare axis lines (no frame)."""
    return VGroup(Line(P3(x0, y0), P3(x1, y0), stroke_color=C.muted, stroke_width=1.2),  # noqa: F821
                  Line(P3(x0, y0), P3(x0, y1), stroke_color=C.muted, stroke_width=1.2))  # noqa: F821


RC = (COL[0] + COL[1]) / 2                  # centre x of the right column


# ----------------------------------------------------------------------------------------------- frames
def f1(s, m):
    """in_s01 at 'smooth waves': the hot bar, the heat equation, its temperature split into cosine modes in depth."""
    xs = np.linspace(0, 1, 320)
    u, modes = sm.heat_bar(xs, 0.0035)  # noqa: F821
    un = u / u.max()
    bx0, bx1, by, bh = -5.4, 5.4, -2.75, 0.42
    X = lambda x: bx0 + (bx1 - bx0) * x  # noqa: E731
    seg = (bx1 - bx0) / len(xs)
    bar = VGroup(*[Rectangle(width=seg * 1.04, height=bh, stroke_width=0, fill_color=heat_ramp(v), fill_opacity=1)  # noqa: F821
                   .move_to(P3(X(x), by)) for x, v in zip(xs, un)])
    m.add(bar)
    for yy in (by - bh / 2, by + bh / 2):                       # the metal's edges, so the cold end still reads
        m.add(Line(P3(bx0, yy), P3(bx1, yy), stroke_color=C.roles["ghost"], stroke_width=1.2))  # noqa: F821
    hot = VGroup(*[Rectangle(width=seg * 1.04, height=bh, stroke_width=0, fill_color=heat_ramp(v),  # noqa: F821
                             fill_opacity=float(np.clip((v - 0.35) / 0.5, 0, 1)) ** 2).move_to(P3(X(x), by))
                   for x, v in zip(xs, un) if v > 0.35])
    glow(s, C.fourier, z=1, k=0.8).add(hot)  # noqa: F821
    base, amp = -2.25, 1.15
    m.add(polyline([(X(x), base + amp * v) for x, v in zip(xs, un)], C.fourier, 4))  # noqa: F821
    m.add(sans("temperature", 22, C.muted).move_to(P3(bx1, base + 0.22), aligned_edge=DR))  # noqa: F821
    # the first five cosine modes floating in depth (2.5D): a ghost baseline each, back ones dimmer, offset up-right
    px0, px1 = bx0 + 0.6, 4.0
    for j, n in enumerate(range(1, 6)):
        dx, dy = 0.30 * j, 0.66 * j
        y0 = -0.75 + dy
        col = mix(C.fourier, "#FFFFFF", 0.12 * j)  # noqa: F821
        m.add(Line(P3(px0 + dx, y0), P3(px1 + dx, y0), stroke_color=C.roles["ghost"], stroke_width=1.0))  # noqa: F821
        mv = modes[n] / np.abs(modes[n]).max()
        m.add(polyline([(px0 + dx + (px1 - px0) * x, y0 + 0.24 * v) for x, v in zip(xs, mv)], col, 3.0, 1 - 0.13 * j))
        m.add(tex(rf"n={n}", 24, C.muted).move_to(P3(px1 + 0.15 + dx, y0), aligned_edge=LEFT))  # noqa: F821
    m.add(tex(r"\textstyle\sum", 44, C.muted).move_to(P3(px0 - 0.5, 0.57)))  # noqa: F821
    e = Eqn(r"\frac{\partial u}{\partial t} = \alpha\,\frac{\partial^2 u}{\partial x^2}", colors={"u": C.fourier})  # noqa: F821
    m.add(e.move_to(P3(0.9, 3.0)))
    m.add(name_tag("Joseph Fourier · 1822", C.fourier))  # noqa: F821


def f2(s, m):
    """in_s02 at 'wire': the wall of ten live windows (no frames), each with a hue rule, name and year; the timeline."""
    from PIL import Image
    tw, gx = 2.38, 0.22
    th = tw * 9 / 16
    rows = [1.75, -0.85]
    for i, n in enumerate(CHAPTER_FRAMES):  # noqa: F821
        r, c = divmod(i, 5)
        cx = -2 * (tw + gx) + c * (tw + gx)
        cy = rows[r]
        img = Image.open(OUT / f"{NAMES_OUT[n]}.png").convert("RGB").resize((480, 270), Image.LANCZOS)
        s.add(ArrayLayer(rgba_of(np.asarray(img)), height=th, pos=(cx, cy), z=0))  # noqa: F821
        hue = getattr(C, CHAPTERS[i])  # noqa: F821
        m.add(Line(P3(cx - tw / 2, cy - th / 2 - 0.08), P3(cx + tw / 2, cy - th / 2 - 0.08), stroke_color=hue,  # noqa: F821
                   stroke_width=3))
        base = cy - th / 2 - 0.40                     # shared baseline: small caps have no descenders, accents rise
        m.add(caps(TILE_NAMES[i], 24).move_to(P3(cx, base), aligned_edge=DOWN),  # noqa: F821
              sans(str(TILE_YEARS[i]), 20, C.muted).move_to(P3(cx, base - 0.08), aligned_edge=UP))  # noqa: F821
    ty, ta, tb = -3.05, -5.6, 5.6
    yr = lambda y: ta + (tb - ta) * (y - 1750) / (1990 - 1750)  # noqa: E731
    m.add(Line(P3(ta, ty), P3(tb, ty), stroke_color=C.muted, stroke_width=1.4))  # noqa: F821
    for i, y in enumerate(TILE_YEARS):
        m.add(Dot(P3(yr(y), ty), radius=0.055, color=getattr(C, CHAPTERS[i])))  # noqa: F821
    for y in (1763, 1973):
        m.add(sans(str(y), 20, C.muted).next_to(P3(yr(y), ty), DOWN, buff=0.12))  # noqa: F821


def f3(s, m):
    """c01_s03 at 'speed of light': dipole radiation fills the frame; the E ⊥ B wave flies out; laws and c at right."""
    ox, oy = -5.55, 1.15
    B = sm.dipole_field(int(2 * XW * 60), int(2 * YH * 60), extent=(2 * XW, 2 * YH), k=3.0, origin=(ox, oy))  # noqa: F821
    s.add(FieldLayer(lambda t: np.abs(B) ** 2, cmap="ramp", colors=(C.bg, C.bg, tint(C.b_field, 0.09)),  # noqa: F821
                     vmin=0, vmax=1, extent=(2 * XW, 2 * YH), center=(0, 0), z=-3))
    m.add(Line(P3(ox, oy - 0.45), P3(ox, oy + 0.45), stroke_color=C.light, stroke_width=4))  # noqa: F821
    for yy, col, sg in ((oy + 0.55, C.charge_p, "+"), (oy - 0.55, C.charge_n, "-")):  # noqa: F821
        m.add(Circle(radius=0.14, stroke_width=0, fill_color=col, fill_opacity=1).move_to(P3(ox, yy)),  # noqa: F821
              tex(sg, 30, C.bg).move_to(P3(ox, yy)))  # noqa: F821
    # the travelling wave in oblique 3D: x along the axis, E along y, B along z (towards the viewer, down-left)
    ax0, ax1, ay0 = -4.75, 2.05, -1.05
    proj = lambda x, y, z: (x - 0.55 * z, ay0 + y - 0.42 * z)  # noqa: E731
    xs = np.linspace(ax0, ax1, 460)
    Ey, Bz = sm.em_wave(xs - ax0, 0.0, k=2 * np.pi / 2.25, amp=1.05)  # noqa: F821
    m.add(Arrow(P3(*proj(ax0 - 0.2, 0, 0)), P3(*proj(ax1 + 0.35, 0, 0)), buff=0, stroke_width=2.2, color=C.muted,  # noqa: F821
                max_tip_length_to_length_ratio=0.03))
    m.add(VGroup(*[Line(P3(*proj(x, 0, 0)), P3(*proj(x, 0, b)), stroke_color=C.b_field, stroke_width=1.3,  # noqa: F821
                        stroke_opacity=0.55) for x, b in zip(xs[::12], Bz[::12])]),
          VGroup(*[Line(P3(*proj(x, 0, 0)), P3(*proj(x, e, 0)), stroke_color=C.e_field, stroke_width=1.3,  # noqa: F821
                        stroke_opacity=0.55) for x, e in zip(xs[::12], Ey[::12])]))
    m.add(polyline([proj(x, 0, b) for x, b in zip(xs, Bz)], C.b_field, 3.6))  # noqa: F821
    m.add(polyline([proj(x, e, 0) for x, e in zip(xs, Ey)], C.e_field, 3.6))  # noqa: F821
    pk = int(np.argmax(Ey[:120]))
    m.add(tex(r"\mathbf E", 40, C.e_field).move_to(P3(*proj(xs[pk], 1.38, 0))))  # noqa: F821
    m.add(tex(r"\mathbf B", 40, C.b_field).move_to(P3(*proj(xs[int(np.argmax(Bz[:120]))], 0, 1.45))))  # noqa: F821
    m.add(tex("c", 36, C.muted).move_to(P3(*proj(ax1 + 0.6, 0.0, 0))))  # noqa: F821
    # the four laws float at the top right; c below them
    cols = {r"\mathbf E": C.e_field, r"\mathbf B": C.b_field, r"\rho": C.charge_p}  # noqa: F821
    laws = VGroup(*[Eqn(t, colors=cols).scale(0.58) for t in (  # noqa: F821
        r"\nabla\cdot\mathbf E=\rho/\varepsilon_0", r"\nabla\cdot\mathbf B=0",
        r"\nabla\times\mathbf E=-\partial_t\mathbf B", r"\nabla\times\mathbf B=\mu_0\mathbf J+\mu_0\varepsilon_0\,\partial_t\mathbf E")]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
    fit(laws, 3.7).move_to(P3(RC + 0.05, 2.05))
    shade(s, laws.get_center()[0], laws.get_center()[1], laws.width + 0.5, laws.height + 0.4)
    m.add(laws)
    ce = Eqn(r"c=\frac{1}{\sqrt{\mu_0\varepsilon_0}}", colors={r"\mu_0": C.b_field, r"\varepsilon_0": C.e_field})  # noqa: F821
    val = eq.c_from_maxwell()  # noqa: F821
    cg = VGroup(ce.scale(0.95), tex(rf"\approx {val / 1e8:.3f}\times10^{{8}}\ \mathrm{{m/s}}", 32),  # noqa: F821
                sans("speed of light", 26, C.light)).arrange(DOWN, buff=0.22).move_to(P3(RC + 0.25, -1.75))  # noqa: F821
    shade(s, cg.get_center()[0], cg.get_center()[1], cg.width + 0.5, cg.height + 0.4)
    m.add(cg)
    m.add(name_tag("James Clerk Maxwell · 1865", C.maxwell))  # noqa: F821
    m.add(rail(1, float(T.c01_s03_speed_of_light)))  # noqa: F821


def f4(s, m):
    """c02_s03 at 'black hole': the ray-traced black hole; the field equations as shape = matter."""
    s.add(BlackHoleLayer(dist=24.0, inclination=81.0, azimuth=18.0, fov=38.0, z=-10))  # noqa: F821
    e = Eqn(r"G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}\,T_{\mu\nu}",  # noqa: F821
            colors={r"G_{\mu\nu}": C.einstein, r"T_{\mu\nu}": C.light})  # noqa: F821
    e.scale(0.95).move_to(P3(0.3, -1.7))
    g = VGroup(e, tag_under(e, r"G_{\mu\nu}", "shape", C.einstein, size=24),  # noqa: F821
               tag_under(e, r"T_{\mu\nu}", "matter", C.light, size=24))  # noqa: F821
    shade(s, 0, g.get_center()[1], g.width + 1.2, g.height + 0.6, a=0.88)
    m.add(g)
    nt = name_tag("Albert Einstein · 1915", C.einstein)  # noqa: F821
    shade(s, nt.get_center()[0], nt.get_center()[1], nt.width + 0.4, nt.height + 0.3, a=0.7)
    m.add(nt)
    shade(s, (X0 + RAIL_X1) / 2, RAIL_Y + 0.12, RAIL_X1 - X0 + 0.4, 0.6, a=0.8)   # the rail over the disk
    m.add(rail(2, float(T.c02_s03_black_hole)))  # noqa: F821


def f5(s, m):
    """c03_s02 at 'tunnelling': ψ as a phase-coloured helix across the frame; the wall a faint slab; |ψ|² below."""
    x, psi, V = sm.schrodinger_1d(18.0)  # noqa: F821
    win = (x > -24) & (x < 24)
    x, psi = x[win], psi[win]
    xa, xb = -6.3, 6.3
    X = lambda v: xa + (xb - xa) * (v + 24) / 48  # noqa: E731
    yax, amp = 0.95, 1.2 / np.abs(psi).max()
    proj = lambda xx, re, im: (X(xx) - 0.45 * im * amp, yax + re * amp - 0.32 * im * amp)  # noqa: E731
    m.add(Line(P3(xa, yax), P3(xb, yax), stroke_color=C.roles["ghost"], stroke_width=1.2))  # noqa: F821
    wall_w = (xb - xa) * 1.4 / 48
    m.add(Rectangle(width=wall_w, height=4.75, stroke_width=0, fill_color=C.muted, fill_opacity=0.10)  # noqa: F821
          .move_to(P3(X(0), -0.4)))
    m.add(sans("wall", 22, C.muted).move_to(P3(X(0), 2.2)))  # noqa: F821
    segs, trans = VGroup(), VGroup()  # noqa: F821
    for i in range(0, len(x) - 1):
        a, b = psi[i], psi[i + 1]
        if abs(a) < 0.004:
            continue
        ln = Line(P3(*proj(x[i], a.real, a.imag)), P3(*proj(x[i + 1], b.real, b.imag)),  # noqa: F821
                  stroke_color=phase_color(np.angle(a)), stroke_width=3.2)
        (trans if x[i] > 0.8 else segs).add(ln)
    m.add(segs)
    glow(s, C.schrod, z=3, k=0.4).add(trans)  # noqa: F821
    yb = -2.45
    p2 = np.abs(psi) ** 2
    k2 = 1.1 / p2.max()
    pts = [P3(X(xx), yb + k2 * v) for xx, v in zip(x[::3], p2[::3])]
    m.add(Polygon(P3(X(x[0]), yb), *pts, P3(X(x[-1]), yb), stroke_width=0, fill_color=C.schrod, fill_opacity=0.28),  # noqa: F821
          polyline([(X(xx), yb + k2 * v) for xx, v in zip(x[::3], p2[::3])], C.schrod, 2.6),
          Line(P3(xa, yb), P3(xb, yb), stroke_color=C.roles["ghost"], stroke_width=1.2))  # noqa: F821
    tr = x > 0.8
    frac = float(np.trapezoid(p2[tr], x[tr]))
    xc = float(np.trapezoid(x[tr] * p2[tr], x[tr]) / frac)
    m.add(sans(f"{frac * 100:.0f}%", 28, C.schrod).move_to(P3(X(xc), yb + k2 * p2[tr].max() + 0.3)))  # noqa: F821
    e = Eqn(r"i\hbar\,\partial_t\psi=\hat H\psi", colors={r"\psi": C.schrod, r"\partial_t": C.text, r"\hat H": C.text})  # noqa: F821
    e.scale(0.85).move_to(P3(RC + 0.6, 2.7))
    m.add(e, tag_under(e, r"\partial_t", "change"), tag_under(e, r"\hat H", "energy"))  # noqa: F821
    p = Eqn(r"P=|\psi|^2", colors={r"\psi": C.schrod}).scale(0.8)  # noqa: F821
    m.add(VGroup(p, sans("chance", 22, C.muted)).arrange(DOWN, buff=0.12).move_to(P3(5.55, -0.75)))  # noqa: F821
    wheel = VGroup(*[Line(P3(0, 0), P3(0.26 * math.cos(a), 0.26 * math.sin(a)), stroke_width=4,  # noqa: F821
                          stroke_color=phase_color(a)) for a in np.linspace(0, 2 * np.pi, 48, endpoint=False)])
    m.add(VGroup(wheel, sans("phase", 22, C.muted)).arrange(RIGHT, buff=0.18).move_to(P3(X1, Y0 + 0.2), aligned_edge=RIGHT))  # noqa: F821
    m.add(name_tag("Erwin Schrödinger · 1926", C.schrod))  # noqa: F821
    m.add(rail(3, float(T.c03_s02_tunnelling)))  # noqa: F821


def _vortex_rgba(vort, dye, mask, out_w=1920):
    """Vorticity (magenta ↔ teal through black) with the dye added as a faint white smoke, composed in linear light."""
    from scipy.ndimage import zoom
    k = out_w / vort.shape[1]
    w = zoom(vort, k, order=3)
    dy = np.clip(zoom(dye, k, order=1), 0, 1)
    mk = zoom(mask.astype(float), k, order=1) > 0.5
    vmax = np.percentile(np.abs(vort[~mask.astype(bool)]), 98.5)
    x = np.clip(w / vmax, -1, 1)
    a = np.clip((np.abs(x) - 0.06) / 0.94, 0, 1) ** 0.85       # free stream stays black
    pos, neg = _lin(C.navier), _lin(C.charge_n)  # noqa: F821
    rgb = np.where(x[..., None] > 0, a[..., None] * pos, a[..., None] * neg) * 0.85
    rgb = rgb + (dy ** 1.6)[..., None] * _lin(C.light) * 0.22  # noqa: F821
    rgb[mk] = 0
    rgb = np.clip(rgb, 0, 1)
    srgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)
    img = (srgb[::-1] * 255).round().astype(np.uint8)          # row 0 = top for the raster
    return feather(rgba_of(img), top=0.08, bottom=0.08)


def f6(s, m):
    """c04_s02 at 'pressure': the vortex street behind a cylinder (lattice Boltzmann), Navier–Stokes with tags."""
    d = sm.lbm_vortex()  # noqa: F821
    r0 = 14                                                   # crop the channel walls' boundary layers
    vort, dye, mask = (d[k][r0:-r0] for k in ("vort", "dye", "mask"))
    mask = mask.astype(bool)
    nx, ny = vort.shape[1], vort.shape[0]
    ext_w = 2 * XW
    ext_h = ext_w * ny / nx
    cy_world = -0.45
    s.add(ArrayLayer(_vortex_rgba(vort, dye, mask), height=ext_h, pos=(0, cy_world), z=-2))  # noqa: F821
    p = d["params"]
    cxw = -XW + ext_w * p[6] / nx
    cyw = cy_world - ext_h / 2 + ext_h * (p[7] - r0) / ny
    m.add(Circle(radius=ext_w * p[4] / nx, stroke_color=C.roles["frame"], stroke_width=1.6, fill_color=C.card,  # noqa: F821
                 fill_opacity=1).move_to(P3(cxw, cyw)))
    e = Eqn(r"\rho\Big(\frac{\partial\mathbf u}{\partial t}+\mathbf u\cdot\nabla\mathbf u\Big)=-\nabla p+\mu\nabla^2\mathbf u+\mathbf f",  # noqa: F821
            colors={r"\mathbf u\cdot\nabla\mathbf u": C.navier, r"-\nabla p": C.charge_p, r"\mu\nabla^2\mathbf u": C.light})  # noqa: F821
    e.scale(0.82).move_to(P3(0.55, 2.6))
    m.add(e, tag_under(e, r"\mathbf u\cdot\nabla\mathbf u", "carried", C.navier, 0.1),  # noqa: F821
          tag_under(e, r"-\nabla p", "pressure", C.charge_p, 0.1),  # noqa: F821
          tag_under(e, r"\mu\nabla^2\mathbf u", "sticky", C.light, 0.1))  # noqa: F821
    m.add(name_tag("Navier 1822 · Stokes 1845", C.navier, at=P3(X1, Y0), edge=DR))  # noqa: F821
    m.add(rail(4, float(T.c04_s02_pressure)))  # noqa: F821


def _pi_outline(height=5.0):
    g = MathTex(r"\pi").family_members_with_points()[0]  # noqa: F821
    pts = np.array([g.point_from_proportion(a) for a in np.linspace(0, 1, 700, endpoint=False)])[:, :2]
    pts -= pts.mean(0)
    return pts * (height / np.ptp(pts[:, 1]))


def f7(s, m):
    """c05_s02 at 'circles': epicycles drawing π across the left of the frame; spectrum and transform float at right."""
    pts = _pi_outline(4.6)
    fr, co = sm.fourier_path(pts, 90)  # noqa: F821
    c0 = np.array([-1.85, 0.1])
    ph = 0.68
    full = np.array([sm.epicycles(fr, co, s_)[-1] for s_ in np.linspace(0, 1, 600)])  # noqa: F821
    drawn = np.array([sm.epicycles(fr, co, s_)[-1] for s_ in np.linspace(0, ph, 420)])  # noqa: F821
    m.add(polyline([(c0[0] + z.real, c0[1] + z.imag) for z in full], C.roles["ghost"], 1.4))  # noqa: F821
    joints = sm.epicycles(fr, co, ph)  # noqa: F821
    circles, arms = VGroup(), VGroup()  # noqa: F821
    for i in range(1, 34):
        a, b = joints[i - 1], joints[i]
        r = abs(co[i - 1])
        if r > 0.02:
            circles.add(Circle(radius=r, stroke_color=C.muted, stroke_width=1.0, stroke_opacity=0.55)  # noqa: F821
                        .move_to(P3(c0[0] + a.real, c0[1] + a.imag)))
        arms.add(Line(P3(c0[0] + a.real, c0[1] + a.imag), P3(c0[0] + b.real, c0[1] + b.imag),  # noqa: F821
                      stroke_color=mix(C.fourier, "#FFFFFF", 0.35), stroke_width=1.8))  # noqa: F821
    m.add(circles, arms)
    glow(s, C.fourier, z=3, k=0.8).add(polyline([(c0[0] + z.real, c0[1] + z.imag) for z in drawn], C.fourier, 4.4))  # noqa: F821
    tip = joints[-1]
    m.add(Dot(P3(c0[0] + tip.real, c0[1] + tip.imag), radius=0.06, color=C.light))  # noqa: F821
    # spectrum: bare stems on a baseline
    ks = np.arange(-18, 19)
    mags = np.array([np.abs(co[fr == k][0]) if (fr == k).any() else 0 for k in ks])
    bx0, bx1, by0 = COL[0] + 0.1, COL[1], 0.85
    for k, v in zip(ks, mags):
        xk = bx0 + (bx1 - bx0) * (k + 18) / 36
        m.add(Line(P3(xk, by0), P3(xk, by0 + 1.75 * v / mags.max()), stroke_color=C.fourier, stroke_width=3.2))  # noqa: F821
    m.add(Line(P3(bx0, by0), P3(bx1, by0), stroke_color=C.muted, stroke_width=1.2))  # noqa: F821
    m.add(sans("frequency", 20, C.muted).move_to(P3(bx1, by0 - 0.18), aligned_edge=UR))  # noqa: F821
    e = Eqn(r"F(\omega)=\int f(t)\,e^{-i\omega t}\,dt", colors={r"f(t)": C.fourier, r"F(\omega)": C.fourier,  # noqa: F821
                                                               r"e^{-i\omega t}": C.text, r"\int": C.text})  # noqa: F821
    fit(e.scale(0.82)).move_to(P3(RC, -1.0))
    lg = legend([(r"f(t)", C.fourier, "the signal"), (r"e^{-i\omega t}", C.text, "a test wave"),  # noqa: F821
                 (r"F(\omega)", C.fourier, "how much of it")])  # noqa: F821
    m.add(e, lg.move_to(P3(RC, -2.3)))
    m.add(name_tag("Joseph Fourier · 1807", C.fourier))  # noqa: F821
    m.add(rail(5, float(T.c05_s02) + 8))  # noqa: F821


def f8(s, m):
    """c06_s01 at 'slowly': a light clock at rest and the same clock moving at 0.6c, on one stage; the formula."""
    v, h = 0.6, 3.0
    hyp = h / math.sqrt(1 - v * v)
    dxh = v * hyp
    yt, yb = 0.8 + h / 2, 0.8 - h / 2

    def mirrors(x, op=1.0):
        return VGroup(*[Line(P3(x - 0.42, y), P3(x + 0.42, y), stroke_color=C.roles["frame"], stroke_width=4,  # noqa: F821
                             stroke_opacity=op) for y in (yt + 0.05, yb - 0.05)])
    lx = -4.6
    m.add(mirrors(lx), Line(P3(lx, yb), P3(lx, yt), stroke_color=C.dilation, stroke_width=3))  # noqa: F821
    glow(s, C.light, z=3, k=1.0).add(Dot(P3(lx, yt - 0.9), radius=0.08, color=C.light))  # noqa: F821
    xs = [-0.45, -0.45 + dxh, -0.45 + 2 * dxh]
    for i, x in enumerate(xs):
        m.add(mirrors(x, 1.0 if i == 1 else 0.35))
    m.add(polyline([(xs[0], yb), (xs[1], yt), (xs[2], yb)], C.dilation, 3))  # noqa: F821
    glow(s, C.light, z=3, k=1.0).add(Dot(P3(xs[1] + 0.55 * dxh, yt - 0.55 * h), radius=0.08, color=C.light))  # noqa: F821
    m.add(DashedLine(P3(xs[1], yb), P3(xs[1], yt), stroke_color=C.muted, stroke_width=2, dash_length=0.08))  # noqa: F821
    m.add(Line(P3(xs[0], yb), P3(xs[1], yb), stroke_color=C.muted, stroke_width=2))  # noqa: F821
    m.add(tex(r"c\,\Delta t", 32, C.muted).next_to(P3(xs[1], 0.8), RIGHT, buff=0.1))  # noqa: F821
    m.add(tex(r"v\,\Delta t'", 32, C.muted).next_to(P3((xs[0] + xs[1]) / 2, yb), DOWN, buff=0.14))  # noqa: F821
    m.add(tex(r"c\,\Delta t'", 32, C.dilation).move_to(P3((xs[0] + xs[1]) / 2 - 0.5, 1.0)))  # noqa: F821
    ay = yt + 0.5
    m.add(Arrow(P3(xs[0], ay), P3(xs[0] + 1.6, ay), buff=0, stroke_width=3, color=C.muted,  # noqa: F821
                max_tip_length_to_length_ratio=0.15),
          tex(r"v = 0.6\,c", 28, C.muted).move_to(P3(xs[0] + 1.8, ay), aligned_edge=LEFT))  # noqa: F821
    m.add(VGroup(sans("at rest", 24), sans("ticks: 10", 22, C.muted)).arrange(DOWN, buff=0.1)  # noqa: F821
          .move_to(P3(lx, yb - 0.75)))
    m.add(VGroup(sans("moving", 24), sans(f"ticks: {10 * math.sqrt(1 - v * v):.0f}", 22, C.muted))  # noqa: F821
          .arrange(DOWN, buff=0.1).move_to(P3(xs[2] + 1.05, yb + 0.35), aligned_edge=LEFT))
    e = Eqn(r"\Delta t'=\frac{\Delta t}{\sqrt{1-v^2/c^2}}", colors={r"\Delta t'": C.dilation})  # noqa: F821
    m.add(e.scale(0.82).move_to(P3(1.8, -2.55)))
    m.add(name_tag("Albert Einstein · 1905", C.dilation))  # noqa: F821
    m.add(rail(6, float(T.c06_s01) + 8))  # noqa: F821


DESC = {}
DESC_BOX = (-XW, -YH, 3.0, YH)          # the surface raster covers the left two thirds, full height


def descent_render(px_w, px_h):
    """PyVista off-screen: the lit loss surface with the descent path (before aion's GL context exists)."""
    import pyvista as pv
    from matplotlib.colors import LinearSegmentedColormap
    from theme import theme as T_

    g = np.linspace(-3, 3, 220)
    Xg, Yg = np.meshgrid(g, g)
    Z = sm.loss(Xg, Yg)  # noqa: F821
    zs = 1.2
    grid = pv.StructuredGrid(Xg, Yg, Z * zs)
    grid["h"] = Z.ravel(order="F")
    cmap = LinearSegmentedColormap.from_list("d", [tint(T_.descent, 0.04), tint(T_.descent, 0.25), T_.descent, "#E9FFF2"])
    p = sm.descent_path()  # noqa: F821
    pz = sm.loss(p[:, 0], p[:, 1]) * zs + 0.03  # noqa: F821
    pv.OFF_SCREEN = True
    pl = pv.Plotter(off_screen=True, window_size=(px_w, px_h))
    pl.set_background("black")
    pl.add_mesh(grid, scalars="h", cmap=cmap, smooth_shading=True, specular=0.3, specular_power=25, show_scalar_bar=False,
                ambient=0.2)
    cont = grid.contour(12, scalars="h")
    cont.points[:, 2] += 0.015                                   # lift off the surface (no z-fighting)
    pl.add_mesh(cont, color="#000000", line_width=1.4, opacity=0.55)
    pl.add_mesh(pv.lines_from_points(np.c_[p, pz]).tube(radius=0.03), color=T_.light, ambient=0.6)
    sph = pv.Sphere(radius=0.055)
    pl.add_mesh(pv.PolyData(np.c_[p[::3], pz[::3]]).glyph(geom=sph, scale=False, orient=False), color=T_.light, ambient=0.5)
    pl.add_mesh(pv.Sphere(radius=0.12, center=(p[-1, 0], p[-1, 1], pz[-1] + 0.05)), color=T_.light, ambient=0.8)
    pl.camera_position = [(-7.3, -8.6, 8.6), (0.3, 0.0, 2.0), (0, 0, 1)]
    pl.camera.view_angle = 30
    DESC["rgb"] = pl.screenshot(return_img=True)
    pl.close()


def f9(s, m):
    """c07_s01 at 'gradient descent': the lit loss surface fills the left; the update rule and the error at right."""
    bw, bh = DESC_BOX[2] - DESC_BOX[0], DESC_BOX[3] - DESC_BOX[1]
    img = feather(rgba_of(DESC["rgb"]), right=0.12, bottom=0.06, top=0.04)
    s.add(ArrayLayer(img, height=bh, pos=((DESC_BOX[0] + DESC_BOX[2]) / 2, 0.0), z=-1))  # noqa: F821
    e = Eqn(r"\theta\leftarrow\theta-\eta\,\nabla L(\theta)", colors={r"\nabla L": C.descent, r"\eta": C.light})  # noqa: F821
    fit(e.scale(0.9)).move_to(P3(RC + 0.15, 2.45))
    lg = legend([(r"\theta", C.text, "the knobs"), (r"\eta", C.light, "step size"), (r"\nabla L", C.descent, "slope")])  # noqa: F821
    m.add(e, lg.move_to(P3(RC + 0.15, 1.2)))
    p = sm.descent_path()  # noqa: F821
    Ls = sm.loss(p[:, 0], p[:, 1])  # noqa: F821
    gx0, gx1, gy0, gy1 = COL[0] + 0.45, COL[1], -2.85, -0.6
    m.add(sans("error", 22, C.muted).move_to(P3(gx0, gy1 + 0.3), aligned_edge=LEFT), axes2(gx0, gy0, gx1, gy1))  # noqa: F821
    lo, hi = Ls.min(), Ls.max()
    pts = [(gx0 + (gx1 - gx0) * i / (len(Ls) - 1), gy0 + 0.1 + (gy1 - gy0 - 0.2) * (v - lo) / (hi - lo)) for i, v in enumerate(Ls)]
    m.add(polyline(pts, C.descent, 3), VGroup(*[Dot(P3(*q), radius=0.03, color=C.light) for q in pts[::3]]))  # noqa: F821
    m.add(sans("steps", 20, C.muted).move_to(P3(gx1, gy0 - 0.18), aligned_edge=UR))  # noqa: F821
    nt = name_tag("Augustin-Louis Cauchy · 1847", C.descent)  # noqa: F821
    shade(s, nt.get_center()[0], nt.get_center()[1], nt.width + 0.4, nt.height + 0.3, a=0.75)
    m.add(nt)
    shade(s, (X0 + RAIL_X1) / 2, RAIL_Y + 0.12, RAIL_X1 - X0 + 0.4, 0.6, a=0.8)
    m.add(rail(7, float(T.c07_s01) + 8))  # noqa: F821


def f10(s, m):
    """c08_s02 at 'strong': 16 points with noise clouds on a tilted plane at left; capacity and its curve at right."""
    pts, rx, sent, err = sm.qam16(n_per=650, snr_db=15.0)  # noqa: F821
    c0 = np.array([-2.15, -0.15])
    k = 0.72

    def proj(a, b):
        return np.stack([c0[0] + k * a + 0.32 * k * b, c0[1] + 0.52 * k * b], -1)
    for lv in (-4, -2, 0, 2, 4):
        m.add(Line(P3(*proj(-4.2, lv)), P3(*proj(4.2, lv)), stroke_color=C.roles["ghost"], stroke_width=1.1),  # noqa: F821
              Line(P3(*proj(lv, -4.2)), P3(*proj(lv, 4.2)), stroke_color=C.roles["ghost"], stroke_width=1.1))  # noqa: F821
    R = proj(rx[:, 0], rx[:, 1])
    s.add(PointsLayer(lambda t: R[~err], color=C.noise, size=2.8, glow=0.0, alpha=0.55, z=1, additive=False))  # noqa: F821
    s.add(PointsLayer(lambda t: R[err], color=C.light, size=4.2, glow=0.0, alpha=1.0, z=1, additive=False))  # noqa: F821
    glow(s, C.shannon, z=3, k=0.8).add(VGroup(*[Dot(P3(*proj(a, b)), radius=0.075, color=C.shannon) for a, b in pts]))  # noqa: F821
    e = Eqn(r"C=B\log_2\!\left(1+\frac{S}{N}\right)", colors={r"S": C.shannon, r"N": C.noise, r"C": C.shannon, "B": C.text})  # noqa: F821
    fit(e.scale(0.88)).move_to(P3(RC + 0.1, 2.45))
    lg = legend([("B", C.text, "bandwidth"), (r"S/N", C.shannon, "signal over noise")], 28)  # noqa: F821
    m.add(e, lg.move_to(P3(RC + 0.1, 1.2)))
    gx0, gx1, gy0, gy1 = COL[0] + 0.45, COL[1], -2.75, -0.45
    db = np.linspace(0, 40, 200)
    cap = np.log2(1 + 10 ** (db / 10))
    m.add(axes2(gx0, gy0, gx1, gy1))
    X = lambda d_: gx0 + (gx1 - gx0) * d_ / 40  # noqa: E731
    Y = lambda c_: gy0 + (gy1 - gy0) * c_ / cap.max()  # noqa: E731
    m.add(polyline([(X(d_), Y(c_)) for d_, c_ in zip(db, cap)], C.shannon, 3))  # noqa: F821
    c30 = math.log2(1 + 1000)
    m.add(Dot(P3(X(30), Y(c30)), radius=0.06, color=C.light))  # noqa: F821
    m.add(sans(f"{eq.shannon(20e6, 1000) / 1e6:.0f} Mbit/s", 22, C.light).next_to(P3(X(30), Y(c30)), UL, buff=0.1))  # noqa: F821
    m.add(sans("Mbit/s at 20 MHz", 20, C.muted).move_to(P3(gx0 - 0.05, gy1 + 0.22), aligned_edge=LEFT))  # noqa: F821
    m.add(sans("S/N (dB)", 20, C.muted).move_to(P3(gx1, gy0 - 0.2), aligned_edge=UR))  # noqa: F821
    m.add(name_tag("Claude Shannon · 1948", C.shannon))  # noqa: F821
    m.add(rail(8, float(T.c08_s02) + 8))  # noqa: F821


def f11(s, m):
    """c09_s01 at 'one in eleven': 1,000 people at left (10 ill); the 98 positives, 9 %, Bayes' rule at right."""
    ill, pos = sm.bayes_people()  # noqa: F821
    sp = 0.16
    ib = [P3(X0 + 0.1 + (i % 2) * sp, 0.6 - (i // 2) * sp) for i in range(10)]
    hb_cols = 45
    hx0, hy0 = X0 + 0.85, 2.05
    hb = [P3(hx0 + (j % hb_cols) * sp, hy0 - (j // hb_cols) * sp) for j in range(990)]
    s.add(PointsLayer(lambda t: np.array(hb)[:, :2], color=C.muted, size=5.0, glow=0.0, alpha=0.9, z=1, additive=False))  # noqa: F821
    s.add(PointsLayer(lambda t: np.array(ib)[:, :2], color=C.ill, size=6.0, glow=0.0, alpha=1.0, z=1, additive=False))  # noqa: F821
    rings = VGroup(*[Circle(radius=0.068, stroke_color=C.positive, stroke_width=1.6).move_to(p)  # noqa: F821
                     for p, q in zip(ib, pos[:10]) if q])
    rings.add(*[Circle(radius=0.068, stroke_color=C.positive, stroke_width=1.6).move_to(p)  # noqa: F821
                for p, q in zip(hb, pos[10:]) if q])
    m.add(rings)
    m.add(sans("ill", 22, C.ill).next_to(VGroup(*[Dot(p) for p in ib]), UP, buff=0.18))  # noqa: F821
    m.add(sans("healthy", 22, C.muted).move_to(P3(hx0 - 0.05, hy0 + 0.3), aligned_edge=LEFT))  # noqa: F821
    cols = 14
    bx0, by0 = COL[0] + 0.45, 2.3
    blk = [(P3(bx0 + (i % cols) * 0.19, by0 - (i // cols) * 0.19), i < 9) for i in range(98)]
    s.add(PointsLayer(lambda t: np.array([p[:2] for p, a in blk if a]), color=C.ill, size=6.0, glow=0, z=1, additive=False))  # noqa: F821
    s.add(PointsLayer(lambda t: np.array([p[:2] for p, a in blk if not a]), color=C.muted, size=5.0, glow=0, z=1,  # noqa: F821
                      additive=False))
    m.add(VGroup(*[Circle(radius=0.075, stroke_color=C.positive, stroke_width=1.5).move_to(p) for p, _ in blk]))  # noqa: F821
    m.add(sans("all positives", 22, C.positive).move_to(P3(bx0 - 0.05, by0 + 0.3), aligned_edge=LEFT))  # noqa: F821
    b = eq.bayes_test()  # noqa: F821
    frac = tex(rf"\frac{{{b['true_pos']}}}{{{b['true_pos']}+{b['false_pos']}}}\approx {b['p_ill_given_pos'] * 100:.0f}\%",
               40)
    m.add(frac.move_to(P3(RC + 0.1, -0.2)))
    e = Eqn(r"P(A\mid B)=\frac{P(B\mid A)\,P(A)}{P(B)}", colors={r"P(A\mid B)": C.bayes, r"P(A)": C.prior})  # noqa: F821
    fit(e.scale(0.72)).move_to(P3(RC + 0.1, -1.75))
    m.add(e, tag_under(e, r"P(A)", "before", C.prior, 0.12), tag_under(e, r"P(A\mid B)", "after", C.bayes, 0.12))  # noqa: F821
    m.add(name_tag("Thomas Bayes · 1763", C.bayes))  # noqa: F821
    m.add(rail(9, float(T.c09_s01) + 8))  # noqa: F821


def _paths_raster(t, S, box, smin, smax, px_per_u=PX):
    """Skia: thin translucent price paths, additive-looking build-up, as an RGBA array covering `box`."""
    import skia
    from theme import theme as T_

    w, h = int((box[2] - box[0]) * px_per_u), int((box[3] - box[1]) * px_per_u)
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    r, g, b = (int(T_.bs.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    paint = skia.Paint(AntiAlias=True, StrokeWidth=1.0, Style=skia.Paint.kStroke_Style, Color=skia.Color(r, g, b, 16))
    xs = (t / t[-1]) * (w - 1)
    for j in range(S.shape[1]):
        ys = (1 - (np.clip(S[:, j], smin, smax) - smin) / (smax - smin)) * (h - 1)
        path = skia.Path()
        path.moveTo(xs[0], ys[0])
        for xx, yy in zip(xs[1::2], ys[1::2]):
            path.lineTo(xx, yy)
        cv.drawPath(path, paint)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


def f12(s, m):
    """c10_s02 at 'heat equation': 2,000 random price paths fanning into a bell; Black–Scholes → the heat equation."""
    t, S = sm.gbm_paths()  # noqa: F821
    smin, smax = 45.0, 185.0
    pb = (X0 + 0.55, -2.55, 2.15, 1.3)
    s.add(ArrayLayer(_paths_raster(t, S, pb, smin, smax), height=pb[3] - pb[1],  # noqa: F821
                     pos=((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2), z=0))
    Y = lambda v: pb[1] + (pb[3] - pb[1]) * (v - smin) / (smax - smin)  # noqa: E731
    m.add(axes2(pb[0], pb[1], pb[2], pb[3]))
    m.add(DashedLine(P3(pb[0], Y(100)), P3(pb[2] + 1.65, Y(100)), stroke_color=C.muted, stroke_width=1.4, dash_length=0.08))  # noqa: F821
    m.add(sans("strike", 20, C.muted).next_to(P3(pb[0], Y(100)), LEFT, buff=0.1))  # noqa: F821
    m.add(sans("one year", 20, C.muted).move_to(P3(pb[2], pb[1] - 0.2), aligned_edge=UR))  # noqa: F821
    hb, edges = np.histogram(S[-1], bins=34, range=(smin, smax))
    hx0 = pb[2] + 0.12
    k = 1.45 / hb.max()
    for c_, e0, e1 in zip(hb, edges[:-1], edges[1:]):
        m.add(Rectangle(width=max(c_ * k, 0.001), height=Y(e1) - Y(e0) - 0.01, stroke_width=0, fill_color=C.bs,  # noqa: F821
                        fill_opacity=0.75).move_to(P3(hx0 + c_ * k / 2, (Y(e0) + Y(e1)) / 2)))
    pay = [(hx0 + 1.6 + 0.012 * max(v - 100, 0), Y(v)) for v in np.linspace(smin, smax, 60)]
    glow(s, C.payoff, z=3, k=0.6).add(polyline(pay, C.payoff, 3.4))  # noqa: F821
    m.add(sans("payoff", 20, C.payoff).move_to(P3(hx0 + 1.75, Y(172)), aligned_edge=LEFT))  # noqa: F821
    e = Eqn(r"\frac{\partial V}{\partial t}+\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}+rS\frac{\partial V}{\partial S}-rV=0",  # noqa: F821
            colors={r"\frac{\partial V}{\partial t}": C.bs, r"\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}": C.bs,
                    r"rS\frac{\partial V}{\partial S}": C.text, r"rV": C.text})
    e.scale(0.72).move_to(P3(2.05, 2.5))
    m.add(e, tag_under(e, r"\frac{\partial V}{\partial t}", "time", buff=0.1),  # noqa: F821
          tag_under(e, r"\tfrac12\sigma^2S^2\frac{\partial^2V}{\partial S^2}", "wobble", buff=0.1),
          tag_under(e, r"rS\frac{\partial V}{\partial S}", "drift", buff=0.1), tag_under(e, r"rV", "interest", buff=0.1))
    he = Eqn(r"\frac{\partial u}{\partial \tau}=\frac{\partial^2 u}{\partial x^2}",  # noqa: F821
             colors={r"\partial u": C.fourier, r"\partial^2 u": C.fourier})  # noqa: F821
    m.add(VGroup(sans("heat equation", 22, C.fourier), he.scale(0.78)).arrange(DOWN, buff=0.14)  # noqa: F821
          .move_to(P3(X1, Y0 + 0.05), aligned_edge=DR))
    m.add(name_tag("Black · Scholes · Merton · 1973", C.bs))  # noqa: F821
    m.add(rail(10, float(T.c10_s02) + 8))  # noqa: F821


def f13(s, m):
    """out_s01 at 'markets': the ten windows on a carousel in depth (no frames), linked in story order."""
    from PIL import Image
    orbit = lambda u: (4.75 * math.cos(u), -0.15 - 1.75 * math.sin(u))  # noqa: E731
    ang = [math.radians(-90 + 36 * i + 18) for i in range(10)]
    for i in range(9):                                             # links, each in the destination's hue, behind
        pts = [orbit(u) for u in np.linspace(ang[i], ang[i + 1], 40)]
        glow(s, getattr(C, CHAPTERS[i + 1]), z=1, k=0.7).add(polyline(pts, getattr(C, CHAPTERS[i + 1]), 3))  # noqa: F821
    cards = []
    for i, n in enumerate(CHAPTER_FRAMES):  # noqa: F821
        x, y = orbit(ang[i])
        d = math.sin(ang[i])                                       # +1 near (bottom of the orbit), -1 far (top)
        cards.append((i, n, x, y, 0.78 + 0.3 * d, d))
    for i, n, x, y, sc, d in sorted(cards, key=lambda c: c[5]):
        img = Image.open(OUT / f"{NAMES_OUT[n]}.png").convert("RGB").resize((480, 270), Image.LANCZOS)
        a = np.asarray(img).astype(np.float32) * (0.45 + 0.55 * (d + 1) / 2)
        w, h = 2.3 * sc, 2.3 * sc * 9 / 16
        z = 5 + d * 4
        s.add(ArrayLayer(feather(rgba_of(a.astype(np.uint8)), 0.04, 0.04, 0.04, 0.04), height=h, pos=(x, y), z=z))  # noqa: F821
        s.manim(z=z + 0.1).add(Line(P3(x - w / 2, y - h / 2 - 0.06), P3(x + w / 2, y - h / 2 - 0.06),  # noqa: F821
                                    stroke_color=getattr(C, CHAPTERS[i]), stroke_width=2.5))  # noqa: F821
    # the still centre of the ring: the line the narration lands on ("Ten equations, written over … two hundred years")
    m.add(VGroup(caps("Ten equations", 44), sans("1763 – 1973", 24, C.muted)).arrange(DOWN, buff=0.22)  # noqa: F821
          .move_to(P3(0, -0.15)))


def f14(s, m):
    """Reference sheet: the progress rail in three states, the chapter card, the type scale, the palette."""
    m.add(sans("progress rail (bottom-left, true size)", 20, C.muted).move_to(P3(X0, 3.3), aligned_edge=LEFT))  # noqa: F821
    st = _chapter_spans()
    for y, k, f in ((2.6, 1, 0.12), (1.95, 4, 0.55), (1.3, 10, 0.97)):
        m.add(rail(k, st[k - 1] + f * (st[k] - st[k - 1]), y=y))
    # chapter card: a feathered duotone portrait (placeholder) fading into black, the title, the hue rule
    cy = -0.4
    from PIL import Image
    face = np.asarray(Image.open(VIDEO / "assets/images/portraits/maxwell.png"))   # scripts/portraits.py
    s.add(ArrayLayer(face, height=2.2, pos=(-5.2, cy), z=0))  # noqa: F821
    card = VGroup(caps("Maxwell's Equations", 48), Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=C.maxwell, stroke_width=3),  # noqa: F821
                  caps("James Clerk Maxwell · 1865", 24, C.muted)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # noqa: F821
    card[1].align_to(card[0], LEFT)
    m.add(card.move_to(P3(-4.2, cy), aligned_edge=LEFT))
    m.add(sans("chapter card", 20, C.muted).move_to(P3(X0, 0.65), aligned_edge=LEFT))  # noqa: F821
    ty = VGroup(  # noqa: F821
        VGroup(tex(r"i\hbar\,\partial_t\psi=\hat H\psi", 40), sans("maths: CM roman", 18, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
        VGroup(sans("pressure", 26), sans("key words: CM sans", 18, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
        VGroup(caps("Claude Shannon · 1948", 28), sans("names, titles: small caps", 18, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(P3(X0, -2.75), aligned_edge=LEFT)
    m.add(ty)
    chips = VGroup(*[VGroup(Square(side_length=0.34, stroke_width=0, fill_color=getattr(C, r), fill_opacity=1),  # noqa: F821
                            sans(str(i + 1), 18, getattr(C, r))).arrange(DOWN, buff=0.05)  # noqa: F821
                     for i, r in enumerate(CHAPTERS)]).arrange(RIGHT, buff=0.14)  # noqa: F821
    roles = ("e_field", "b_field", "charge_p", "charge_n", "light", "mass", "data", "noise", "ill", "positive", "prior",
             "payoff", "bad")
    rchips = VGroup(*[VGroup(Square(side_length=0.24, stroke_width=0, fill_color=getattr(C, r), fill_opacity=1),  # noqa: F821
                             sans(r.replace("_", r"\_"), 13, C.muted)).arrange(DOWN, buff=0.05)  # noqa: F821
                      for r in roles]).arrange(RIGHT, buff=0.09)
    pal = VGroup(sans("chapter hues", 18, C.muted), chips, sans("roles", 18, C.muted), rchips).arrange(  # noqa: F821
        DOWN, aligned_edge=LEFT, buff=0.12).move_to(P3(X1, -1.9), aligned_edge=RIGHT)
    m.add(pal)


FRAMES = {1: f1, 2: f2, 3: f3, 4: f4, 5: f5, 6: f6, 7: f7, 8: f8, 9: f9, 10: f10, 11: f11, 12: f12, 13: f13, 14: f14}
PRE = {9: lambda: descent_render(int((DESC_BOX[2] - DESC_BOX[0]) * PX), int((DESC_BOX[3] - DESC_BOX[1]) * PX))}


# ------------------------------------------------------------------------------------------------- main
def render(n: int) -> Path:
    from PIL import Image

    _import_aion()
    if n in PRE:
        PRE[n]()                                          # VTK before aion's GL context exists

    @scene(0.0, 10.0)  # noqa: F821
    def style_frame(s):
        s.solid(C.bg, z=-200)  # noqa: F821
        FRAMES[n](s, s.manim())

    sd = scene_mod.REGISTRY[-1]  # noqa: F821
    OUT.mkdir(parents=True, exist_ok=True)
    path = (OUT / f"{NAMES_OUT[n]}.png").resolve()
    Image.fromarray(sd.comp((W, H), FPS).frame(T_STILL, round(T_STILL * FPS))).save(path)
    print(path.relative_to(REPO))
    return path


ORDER = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 2, 13, 14]

if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or ORDER
    if len(want) == 1:
        render(want[0])
    else:
        for k in want:                                    # one process per frame keeps memory low
            subprocess.run([sys.executable, __file__, str(k)], check=True, cwd=REPO)
