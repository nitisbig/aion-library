"""Style frames for video 018, "What Logarithms Actually Are": stills at 1920x1080, rendered through aion.

    uv run python videos/018-logarithms/design/style_frames.py          # all → design/style_frames/*.png
    uv run python videos/018-logarithms/design/style_frames.py 3 7      # only frames 3 and 7

Each frame is an `@scene(0, 10)` rendered with `sd.comp((1920, 1080), 60).frame(t, ...)`: the same theme, LaTeX,
Manim rasteriser and GPU compositor as the video. Every number comes from logdata.py. One process per frame.

Screen language (no boards, no boxes): each frame is one open composition on black. Equations float in open space,
coloured by role (base amber · steps periwinkle · value magenta · natural mint). Text over a busy raster sits on a
feathered shade (an invisible darkening). Chapter progress is the bottom-left rail. Glow only on graphics, never text.

     1 in_s01   Napier's page; π × e worked as log + log (the + glows)
     2 c01_s01  the colony of 1024 cells; 10 divisions; 2¹⁰ = 1024
     3 c01_s02  the multiplication staircase (the motif); 2¹⁰ = 1024 ⇔ log₂ 1024 = 10
     4 c02_s03  worked example: the digits of 2¹⁰⁰ by the power rule
     5 c03_s02  the slide rule computing 2 × 3 = 6; log 2 + log 3 = log 6
     6 c04_s01  the mirror: 2ˣ and log₂ x across y = x on the blue grid
     7 c05_s03  the area under 1/x reaching 1 at e
     8 c06_s01  sound rings and the decibel ruler; 90 dB vs 60 dB
     9 c06_s03  Kepler's planets on log-log axes: slope 3/2
    10 out_s01  the recap staircase, one step per chapter
    11          reference → design/components.png: rail, name tag, chapter card, type scale, palette
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

W, H, FPS, T_STILL = 1920, 1080, 60, 5.0
PX = 135.0
XW, YH = 64 / 9, 4.0
SAFE = 0.71
X0, X1, Y0, Y1 = -XW + SAFE, XW - SAFE, -YH + SAFE, YH - SAFE
RAIL_Y, RAIL_X1 = Y0 - 0.01, X0 + 5.0
COL = (2.75, X1)

NAMES_OUT = {1: "01_in_napier", 2: "02_c01_cells", 3: "03_c01_staircase", 4: "04_c02_digits", 5: "05_c03_slide_rule",
             6: "06_c04_mirror", 7: "07_c05_area_e", 8: "08_c06_decibels", 9: "09_c06_kepler", 10: "10_out_recap",
             11: "../components"}
CH_TITLES = ["Counting multiplications", "Multiplication becomes addition", "The slide rule", "The curve", r"Why $e$",
             "A world in logarithms"]


# ------------------------------------------------------------------------------------------------ setup
def _import_aion():
    from aion.render.project import load_video

    load_video("018", (W, H), FPS, only=["__none__"])
    import aion
    from aion.render import scenes as scene_mod

    import beats
    import logdata
    from theme import CHAPTERS

    g = globals()
    for k in aion.__all__:
        g.setdefault(k, getattr(aion, k))
    g.update(scene_mod=scene_mod, ld=logdata, CHAPTERS=CHAPTERS, T=beats.T)


# ---------------------------------------------------------------------------------------------- helpers
def _esc(s):
    return s.replace("%", r"\%").replace("&", r"\&")


def tex(s, size=48, color=None):
    return MathTex(s, font_size=size, color=color or C.text)  # noqa: F821


def ctex(parts, size=48):
    """MathTex built from (tex, colour) parts, each part its own colour."""
    m = MathTex(*[p for p, _ in parts], font_size=size)  # noqa: F821
    for sub, (_, c) in zip(m, parts):
        sub.set_color(c or C.text)  # noqa: F821
    return m


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
    return _hex(_lin(color) * a)


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def feather(rgba, left=0.0, right=0.0, top=0.0, bottom=0.0):
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
    """Invisible darkening under text on a busy raster (soft superellipse alpha, never a visible rectangle)."""
    ppu = 40
    nx, ny = max(8, int(w * 1.4 * ppu)), max(8, int(h * 1.4 * ppu))
    xx, yy = np.linspace(-1.4, 1.4, nx)[None, :], np.linspace(-1.4, 1.4, ny)[:, None]
    d = (np.abs(xx) ** 4 + np.abs(yy) ** 4) ** 0.25
    img = np.zeros((ny, nx, 4), np.uint8)
    img[..., 3] = (a * _smooth((1.4 - d) / 0.6) * 255).astype(np.uint8)
    s.add(ArrayLayer(img, height=h * 1.4, pos=(cx, cy), z=z))  # noqa: F821


def glow(s, color, z=2, k=1.0):
    """A Manim layer whose shapes glow (graphic payoff elements only; never text)."""
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=C.glow_r)])  # noqa: F821


def polyline(pts, color, width=3.0, opacity=1.0):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)  # noqa: F821
    v.set_points_smoothly([P3(*p) for p in pts]) if len(pts) > 2 else v.set_points_as_corners([P3(*p) for p in pts])
    return v


def fit(mob, width=COL[1] - COL[0]):
    if mob.width > width:
        mob.scale(width / mob.width)
    return mob


def name_tag(text, hue, at=None, edge=None):
    """A short hue rule over a small-caps name and year. No box. First appearance only, then fades."""
    rule = Line(LEFT * 0.35, RIGHT * 0.35, stroke_color=hue, stroke_width=3)  # noqa: F821
    g = VGroup(rule, caps(text, 30, C.text)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)  # noqa: F821
    return g.move_to(at if at is not None else P3(X0, Y1), aligned_edge=edge if edge is not None else UL)  # noqa: F821


def _chapter_spans():
    return np.array([float(getattr(T, f"c{i:02d}_s01")) for i in range(1, 7)] + [float(T.out_s01)])  # noqa: F821


def rail(k, t, y=RAIL_Y, x0=X0, x1=RAIL_X1, label=True):
    """The progress rail: six segments bottom-left, each as long as its chapter's audio. Past: hue at 50 %; future:
    a muted ghost; current: a comet fill, scene ticks, a light head in a hue ring, the chapter title in small caps."""
    st = _chapter_spans()
    durs = np.diff(st)
    gap = 0.05
    span = (x1 - x0) - gap * 5
    g = VGroup()  # noqa: F821
    xa = x0
    for i in range(6):
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
            n_seg = 24
            for j in range(n_seg):
                a0, a1 = xa + (xf - xa) * j / n_seg, xa + (xf - xa) * (j + 1) / n_seg
                if a1 - a0 > 1e-4:
                    g.add(Line(P3(a0, y), P3(a1, y), stroke_width=4,  # noqa: F821
                               stroke_color=tint(hue, 0.35 + 0.65 * ((j + 1) / n_seg) ** 2)))
            for sc in ("s02", "s03"):
                ts = float(getattr(T, f"c{k:02d}_{sc}"))  # noqa: F821
                xt = xa + w * (ts - st[i]) / durs[i]
                g.add(Line(P3(xt, y - 0.06), P3(xt, y + 0.06), stroke_color=hue if xt <= xf else C.muted,  # noqa: F821
                           stroke_width=1.5))
            g.add(Circle(radius=0.085, stroke_color=hue, stroke_width=1.5).move_to(P3(xf, y)),  # noqa: F821
                  Dot(P3(xf, y), radius=0.04, color=C.text))  # noqa: F821
            if label:
                g.add(caps(CH_TITLES[i], 20, C.text).move_to(P3(x0, y + 0.17), aligned_edge=DL))  # noqa: F821
        xa = xb + gap
    return g


def plane(ox, oy, u, xr, yr, minor=True):
    """The Classic grid: dim minor lines, bright blue integer lines, white axes; origin at (ox, oy), u world units."""
    g = VGroup()  # noqa: F821
    X = lambda x: ox + u * x  # noqa: E731
    Y = lambda y: oy + u * y  # noqa: E731
    if minor:
        for x in np.arange(xr[0], xr[1] + 1e-9, 0.5):
            g.add(Line(P3(X(x), Y(yr[0])), P3(X(x), Y(yr[1])), stroke_color=C.grid_minor, stroke_width=1))  # noqa: F821
        for y in np.arange(yr[0], yr[1] + 1e-9, 0.5):
            g.add(Line(P3(X(xr[0]), Y(y)), P3(X(xr[1]), Y(y)), stroke_color=C.grid_minor, stroke_width=1))  # noqa: F821
    for x in range(math.ceil(xr[0]), math.floor(xr[1]) + 1):
        g.add(Line(P3(X(x), Y(yr[0])), P3(X(x), Y(yr[1])), stroke_color=C.grid, stroke_width=1.6))  # noqa: F821
    for y in range(math.ceil(yr[0]), math.floor(yr[1]) + 1):
        g.add(Line(P3(X(xr[0]), Y(y)), P3(X(xr[1]), Y(y)), stroke_color=C.grid, stroke_width=1.6))  # noqa: F821
    g.add(Line(P3(X(xr[0]), oy), P3(X(xr[1]), oy), stroke_color=C.axis, stroke_width=2.4),  # noqa: F821
          Line(P3(ox, Y(yr[0])), P3(ox, Y(yr[1])), stroke_color=C.axis, stroke_width=2.4))  # noqa: F821
    return g, X, Y


def staircase(n, x0, y0, sw, sh, base=2, show=None, label_size=30, risers=True, axis=True):
    """The motif: n+1 treads (levels 0…n) of width sw, rising sh per step from (x0, y0). The value b^k sits on tread
    k (value); a ×b tag sits beside each riser (base); the left axis counts the steps, so height = the logarithm
    (steps). `show` limits which levels get a value label."""
    g = VGroup()  # noqa: F821
    pts = [(x0, y0)]
    for k in range(n + 1):
        y = y0 + k * sh
        pts.append((x0 + (k + 1) * sw, y))
        if k < n:
            pts.append((x0 + (k + 1) * sw, y + sh))
    g.add(polyline_corners(pts, C.text, 3))  # noqa: F821
    g.add(Line(P3(x0 - 0.1, y0), P3(x0 + (n + 1) * sw + 0.2, y0), stroke_color=C.muted, stroke_width=1.2))  # noqa: F821
    for k in range(n + 1):
        y = y0 + k * sh
        if show is None or k in show:
            v = base ** k
            g.add(tex(str(v), label_size * (1.0 if v < 100 else 0.86), C.value)  # noqa: F821
                  .move_to(P3(x0 + (k + 0.5) * sw, y + 0.08), aligned_edge=DOWN))
        if risers and k < n:
            g.add(tex(rf"\times{base}", 19, C.base)  # noqa: F821
                  .move_to(P3(x0 + (k + 1) * sw + 0.07, y + sh / 2), aligned_edge=LEFT))
    if axis:
        ax = x0 - 0.35
        g.add(Line(P3(ax, y0), P3(ax, y0 + n * sh), stroke_color=C.steps, stroke_width=2))  # noqa: F821
        for k in range(n + 1):
            g.add(Line(P3(ax - 0.07, y0 + k * sh), P3(ax + 0.07, y0 + k * sh), stroke_color=C.steps, stroke_width=2))  # noqa: F821
            if show is None or k in show:
                g.add(tex(str(k), label_size * 0.72, C.steps).next_to(P3(ax - 0.07, y0 + k * sh), LEFT, buff=0.08))  # noqa: F821
    return g


def polyline_corners(pts, color, width=3.0, opacity=1.0):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)  # noqa: F821
    v.set_points_as_corners([P3(*p) for p in pts])
    return v


def skia_rgba(w, h, draw):
    import skia
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    draw(cv, skia)
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def _hexc(skia, h, a=255):
    r, g, b = (int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return skia.Color(r, g, b, a)


def paper_page(w=900, h=1200, seed=1614):
    """Napier's page: warm paper with fibre noise, two ruled columns of seven-figure numbers (a texture)."""
    rng = np.random.default_rng(seed)
    nums = [(f"{int(rng.integers(1_000_000, 9_999_999)):07d}", f"{int(rng.integers(1_000_000, 9_999_999)):07d}")
            for _ in range(38)]

    def draw(cv, skia):
        cv.drawRect(skia.Rect(0, 0, w, h), skia.Paint(Color=_hexc(skia, C.paper)))  # noqa: F821
        ink = skia.Paint(Color=skia.Color(58, 44, 30, 210), AntiAlias=True)
        rule = skia.Paint(Color=skia.Color(58, 44, 30, 150), StrokeWidth=1.6, Style=skia.Paint.kStroke_Style)
        font = skia.Font(skia.Typeface("serif"), 24)
        cv.drawLine(70, 110, w - 70, 110, rule)
        cv.drawLine(w / 2, 120, w / 2, h - 80, rule)
        cv.drawString("LOGARITHMORUM", w / 2 - 150, 80, skia.Font(skia.Typeface("serif"), 34), ink)
        for i, (a, b) in enumerate(nums):
            y = 160 + i * 27
            cv.drawString(f"{i:2d}", 80, y, font, ink)
            cv.drawString(a, 160, y, font, ink)
            cv.drawString(b, w / 2 + 80, y, font, ink)
            cv.drawString(f"{(i * 37) % 60:02d}", w - 130, y, font, ink)

    img = skia_rgba(w, h, draw).astype(np.float32)
    from scipy.ndimage import gaussian_filter
    fib = gaussian_filter(rng.standard_normal((h, w)), (0.6, 6)) * 0.9 + gaussian_filter(rng.standard_normal((h, w)), 18) * 4
    fib = 1 + 0.06 * fib / (np.abs(fib).max() + 1e-9) * 3
    vign = 1 - 0.35 * (np.hypot(np.linspace(-1, 1, w)[None], np.linspace(-1, 1, h)[:, None]) / 1.41) ** 2
    img[..., :3] = np.clip(img[..., :3] * (fib * vign)[..., None], 0, 255)
    return feather(img.astype(np.uint8), 0.08, 0.08, 0.06, 0.06)


def wood(w, h, seed=1622):
    """A boxwood rule body: warm gradient with fine grain, a thin bevel line top and bottom."""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    base = np.array([196, 160, 104], np.float32)[None, :] * (0.82 + 0.18 * np.sin(np.pi * y))   # (h, 3)
    from scipy.ndimage import gaussian_filter
    grain = gaussian_filter(rng.standard_normal((h, w)), (0.8, 40))
    grain = grain / (np.abs(grain).max() + 1e-9)
    img = np.clip(base[:, None, :] * (1 + 0.10 * grain)[..., None], 0, 255)
    rgba = np.dstack([img, np.full((h, w), 255, np.float32)]).astype(np.uint8)
    rgba[:2, :, :3] = 235
    rgba[-2:, :, :3] = 90
    return feather(rgba, 0.015, 0.015, 0, 0)


# ------------------------------------------------------------------------------------------------ frames
def f1(s, m):
    """in_s01 at 'into an addition': Napier's page in depth; π × e collapses into log + log."""
    page = paper_page()
    dim = page.copy()
    dim[..., :3] = (dim[..., :3] * 0.55).astype(np.uint8)
    s.add(ArrayLayer(dim, height=7.4, pos=(-3.6, 0.0), z=-5))  # noqa: F821
    back = page.copy()
    back[..., :3] = (back[..., :3] * 0.25).astype(np.uint8)
    s.add(ArrayLayer(back, height=6.2, pos=(-5.9, 0.5), z=-6))  # noqa: F821
    a, b = math.pi, math.e
    la, lb = math.log10(a), math.log10(b)
    shade(s, 2.9, -0.1, 6.4, 4.6, a=0.9)
    top = ctex([(f"{a:.7f}", C.value), (r"\times", None), (f"{b:.7f}", C.value)], 46)  # noqa: F821
    mid = ctex([(f"{la:.7f}", C.steps), (r"\;+\;", None), (f"{lb:.7f}", C.steps), ("=", None), (f"{la + lb:.7f}", C.steps)], 44)  # noqa: F821
    res = ctex([(f"{a * b:.7f}", C.value)], 52)  # noqa: F821
    top.move_to(P3(2.9, 1.9))
    mid.move_to(P3(2.9, 0.1))
    res.move_to(P3(2.9, -1.8))
    m.add(top, mid, res)
    for x0, x1 in ((top[0], mid[0]), (top[2], mid[2])):
        m.add(Arrow(x0.get_bottom() + DOWN * 0.1, x1.get_top() + UP * 0.1, buff=0, stroke_width=2.5,  # noqa: F821
                    color=C.muted, max_tip_length_to_length_ratio=0.12))  # noqa: F821
    m.add(Arrow(mid[4].get_bottom() + DOWN * 0.1, res.get_top() + UP * 0.1, buff=0, stroke_width=2.5,  # noqa: F821
                color=C.muted, max_tip_length_to_length_ratio=0.12))  # noqa: F821
    m.add(sans("look up", 20, C.muted).next_to(mid, UP, buff=0.75).shift(RIGHT * 0.15))  # noqa: F821
    m.add(sans("look back", 20, C.muted).next_to(res, UP, buff=0.42).shift(RIGHT * 1.5))  # noqa: F821
    glow(s, C.text, z=3, k=1.1).add(Circle(radius=0.26, stroke_color=C.text, stroke_width=2).move_to(mid[1]))  # noqa: F821
    m.add(name_tag("John Napier · 1614", C.base, at=P3(0.9, Y1)))  # noqa: F821
    m.add(tex(r"a\times b\ \longrightarrow\ \log a+\log b", 34, C.muted).move_to(P3(2.9, -3.0)))  # noqa: F821


def _cells_raster(n=1024, w=1500, h=1050, seed=1801):
    """1024 cells packed in a dish (Vogel spiral + jitter): lime membrane rim, dim interior."""
    rng = np.random.default_rng(seed)
    k = np.arange(n) + 0.5
    rr = np.sqrt(k / n)
    th = k * math.pi * (3 - math.sqrt(5))
    R = 0.46 * h
    cx, cy = w / 2 + R * rr * np.cos(th) + rng.normal(0, 2.0, n), h / 2 + R * rr * np.sin(th) + rng.normal(0, 2.0, n)
    rad = R * math.sqrt(1 / n) * 0.93 * (1 + rng.normal(0, 0.05, n))
    img = np.zeros((h, w), np.float32)
    rim = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    for x, y, r in zip(cx, cy, rad):
        x0, x1, y0, y1 = int(x - r - 3), int(x + r + 4), int(y - r - 3), int(y + r + 4)
        d = np.hypot(xx[y0:y1, x0:x1] - x, yy[y0:y1, x0:x1] - y)
        img[y0:y1, x0:x1] = np.maximum(img[y0:y1, x0:x1], np.clip(r - d, 0, 1) * 0.22 * (1 - 0.5 * d / r))
        rim[y0:y1, x0:x1] = np.maximum(rim[y0:y1, x0:x1], np.clip(1.6 - np.abs(d - r + 1.2), 0, 1))
        nd = np.hypot(xx[y0:y1, x0:x1] - x - r * 0.2, yy[y0:y1, x0:x1] - y + r * 0.15)
        img[y0:y1, x0:x1] = np.maximum(img[y0:y1, x0:x1], np.clip(r * 0.28 - nd, 0, 1) * 0.45)
    col = _lin(C.cell)  # noqa: F821
    lin = img[..., None] * col + rim[..., None] * col * 0.95
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
    a = np.clip(np.maximum(img * 3, rim), 0, 1)
    return np.dstack([np.clip(srgb * 255, 0, 255), a * 255]).astype(np.uint8)


def f2(s, m):
    """c01_s01 at 'ten divisions': the dish of 1024 cells; the tally and the count; 2¹⁰ = 1024."""
    s.add(ArrayLayer(_cells_raster(), height=7.0, pos=(-2.0, 0.35), z=0))  # noqa: F821
    x = 4.55
    m.add(tex("10", 96, C.steps).move_to(P3(x, 1.7)), sans("divisions", 24, C.muted).move_to(P3(x, 0.95)))  # noqa: F821
    m.add(tex("1024", 96, C.value).move_to(P3(x, -0.2)), sans("cells", 24, C.muted).move_to(P3(x, -0.95)))  # noqa: F821
    m.add(ctex([("2", C.base), ("^{10}", C.steps), ("=", None), ("1024", C.value)], 56).move_to(P3(x, -2.3)))  # noqa: F821
    m.add(rail(1, float(T.c01_s01) + 18))  # noqa: F821


def f3(s, m):
    """c01_s02 at 'logarithm': the staircase climbs to 1024; the definition both ways in the column."""
    n, x0, y0, sw, sh = 10, -5.75, -2.5, 0.7, 0.52
    m.add(staircase(n, x0, y0, sw, sh, label_size=28))
    m.add(sans("steps", 22, C.steps).move_to(P3(x0 - 0.62, y0 + n * sh + 0.45)))  # noqa: F821
    e1 = ctex([("2", C.base), ("^{10}", C.steps), ("=", None), ("1024", C.value)], 64)  # noqa: F821
    e2 = ctex([(r"\log_{", None), ("2", C.base), ("}", None), ("1024", C.value), ("=", None), ("10", C.steps)], 64)  # noqa: F821
    iff = tex(r"\Updownarrow", 48, C.muted)  # noqa: F821
    col = VGroup(e1, iff, e2).arrange(DOWN, buff=0.35).move_to(P3(4.6, 0.6))  # noqa: F821
    m.add(col)
    legend = VGroup(*[VGroup(Dot(radius=0.06, color=c), sans(w, 20, C.muted)).arrange(RIGHT, buff=0.15)  # noqa: F821
                      for c, w in ((C.base, "base"), (C.steps, "steps = log"), (C.value, "value"))])  # noqa: F821
    m.add(legend.arrange(RIGHT, buff=0.4).move_to(P3(4.6, -1.35)))
    m.add(rail(1, float(T.c01_s02) + 20))  # noqa: F821


def f4(s, m):
    """c02_s03 at 'thirty one digits': the power rule counting the digits of 2¹⁰⁰."""
    twos = VGroup(*[tex("2", 30, C.base) for _ in range(46)]).arrange(RIGHT, buff=0.13)  # noqa: F821
    twos.move_to(P3(X0, 3.05), aligned_edge=LEFT)
    for i, t in enumerate(twos):
        t.set_opacity(float(np.clip(1.15 - i / 40, 0.1, 1)))
    m.add(twos, sans("× 100", 22, C.muted).next_to(twos, RIGHT, buff=0.1).shift(LEFT * 1.1 + DOWN * 0.45))  # noqa: F821
    q = ctex([(r"\text{digits of }", C.muted), ("2", C.base), ("^{100}", C.steps), (r"\,?", C.muted)], 44)  # noqa: F821
    m.add(q.move_to(P3(X0, 2.15), aligned_edge=LEFT))
    e1 = ctex([(r"\log_{10}", None), ("2", C.base), ("^{100}", C.steps), ("=", None), ("100", C.steps),  # noqa: F821
               (r"\cdot\log_{10}", None), ("2", C.base)], 52)
    e2 = ctex([(r"\approx 100\times 0.30103", None), ("=", None), ("30.103", C.steps)], 52)  # noqa: F821
    VGroup(e1, e2).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(P3(X0, 0.75), aligned_edge=LEFT)  # noqa: F821
    m.add(e1, e2)
    # the decade ruler 10^30 .. 10^31 with the marker at 30.103
    rx0, rx1, ry = X0 + 0.2, X0 + 8.2, -0.95
    m.add(Line(P3(rx0, ry), P3(rx1, ry), stroke_color=C.ruler, stroke_width=2.5))  # noqa: F821
    for j in range(1, 11):
        x = rx0 + (rx1 - rx0) * math.log10(j)
        m.add(Line(P3(x, ry), P3(x, ry + (0.22 if j in (1, 10) else 0.12)), stroke_color=C.ruler, stroke_width=2))  # noqa: F821
    m.add(tex(r"10^{30}", 30, C.value).next_to(P3(rx0, ry), DOWN, buff=0.15),  # noqa: F821
          tex(r"10^{31}", 30, C.value).next_to(P3(rx1, ry), DOWN, buff=0.15))  # noqa: F821
    xm = rx0 + (rx1 - rx0) * (ld.TWO_100_LOG - 30)  # noqa: F821
    glow(s, C.value, z=3).add(Triangle(color=C.value, fill_opacity=1, stroke_width=0).scale(0.1)  # noqa: F821
                                .rotate(math.pi).move_to(P3(xm, ry + 0.22)))
    m.add(tex(r"2^{100}", 30, C.value).move_to(P3(xm, ry + 0.58)))  # noqa: F821
    digits = str(ld.TWO_100)  # noqa: F821
    num = tex(digits, 46, C.value).move_to(P3(X0, -2.35), aligned_edge=LEFT)  # noqa: F821
    m.add(num)
    m.add(Line(num.get_corner(DL) + DOWN * 0.12, num.get_corner(DR) + DOWN * 0.12, stroke_color=C.steps,  # noqa: F821
               stroke_width=2.5))
    m.add(sans("31 digits", 26, C.steps).next_to(num, RIGHT, buff=0.35))  # noqa: F821
    m.add(rail(2, float(T.c02_s03) + 22))  # noqa: F821


def f5(s, m):
    """c03_s02 at 'six': the slide rule set to 2 × 3; the cursor; log 2 + log 3 = log 6."""
    L, xl = 10.2, -6.0
    body_h = 0.95
    lo_y, up_y = -1.0, -1.0 + body_h + 0.02
    off = L * math.log10(2)
    s.add(ArrayLayer(wood(1600, 150), height=body_h, pos=(xl + L / 2, lo_y), z=-2))  # noqa: F821
    s.add(ArrayLayer(wood(1600, 150, seed=1623), height=body_h, pos=(xl + off + L / 2, up_y), z=-2))  # noqa: F821
    ink = "#2A1E12"

    def scale(x0, yb, up):
        sgn = -1 if up else 1
        edge = yb + sgn * body_h / 2
        for v in [1 + i / 10 for i in range(10)] + [2 + i / 5 for i in range(0, 15)] + list(range(5, 11)) + \
                 [5.5, 6.5, 7.5, 8.5, 9.5]:
            x = x0 + L * math.log10(v)
            if x > XW + 0.2:
                continue
            major = abs(v - round(v)) < 1e-9
            ln = 0.30 if major else (0.18 if abs(v * 2 - round(v * 2)) < 1e-9 else 0.11)
            m.add(Line(P3(x, edge), P3(x, edge - sgn * ln), stroke_color=ink, stroke_width=2 if major else 1.2))  # noqa: F821
            if major:
                iv = int(round(v))
                hit = False
                dx = 0.14 if iv == 1 else (-0.18 if iv == 10 else (0.17 if hit else 0.0))
                m.add(tex(str(iv), 30 if hit else 26, C.value if hit else ink)  # noqa: F821
                      .move_to(P3(x + dx, edge - sgn * 0.5)))

    scale(xl, lo_y, up=False)
    scale(xl + off, up_y, up=True)
    xc = xl + L * math.log10(6)
    glow(s, C.ruler, z=3, k=0.6).add(Line(P3(xc, up_y + body_h / 2 + 0.15), P3(xc, lo_y - body_h / 2 - 0.15),  # noqa: F821
                                          stroke_color=C.ruler, stroke_width=1.6))
    m.add(tex("3", 40, C.value).move_to(P3(xc + 0.28, up_y + body_h / 2 + 0.3)),  # noqa: F821
          tex("6", 40, C.value).move_to(P3(xc + 0.28, lo_y - body_h / 2 - 0.3)))  # noqa: F821
    by = lo_y - body_h / 2 - 0.75
    x2 = xl + off
    m.add(Line(P3(xl, by), P3(x2, by), stroke_color=C.steps, stroke_width=7),  # noqa: F821
          Line(P3(x2, by), P3(xc, by), stroke_color=tint(C.steps, 0.6), stroke_width=7))  # noqa: F821
    m.add(tex(r"\log 2", 30, C.steps).next_to(P3((xl + x2) / 2, by), DOWN, buff=0.15),  # noqa: F821
          tex(r"\log 3", 30, C.steps).next_to(P3((x2 + xc) / 2, by), DOWN, buff=0.15))  # noqa: F821
    e = ctex([(r"\log ", None), ("2", C.value), ("+", None), (r"\log ", None), ("3", C.value), ("=", None),  # noqa: F821
              (r"\log ", None), ("6", C.value)], 60)
    m.add(e.move_to(P3(2.6, 2.55)))
    m.add(ctex([("2", C.value), (r"\times", None), ("3", C.value), ("=", None), ("6", C.value)], 44)  # noqa: F821
          .move_to(P3(2.6, 1.6)))
    m.add(rail(3, float(T.c03_s02) + 10))  # noqa: F821


def f6(s, m):
    """c04_s01 at 'swaps': 2ˣ reflected across y = x into log₂ x on the Classic grid."""
    ox, oy, u = -5.7, -2.5, 0.62
    g, X, Y = plane(ox, oy, u, (-1, 9.2), (-0.4, 9.2))
    m.add(g)
    for i in range(0, 10, 2):
        m.add(tex(str(i), 20, C.muted).next_to(P3(X(i), oy), DOWN, buff=0.08) if i else VMobject())  # noqa: F821
    m.add(DashedLine(P3(X(-0.4), Y(-0.4)), P3(X(9.0), Y(9.0)), stroke_color=C.muted, stroke_width=2, dash_length=0.1))  # noqa: F821
    xs = np.linspace(-1, math.log2(9.1), 200)
    m.add(polyline([(X(x), Y(2 ** x)) for x in xs], C.value, 4))
    xl = np.linspace(0.8, 9.1, 300)
    m.add(polyline([(X(x), Y(math.log2(x))) for x in xl], C.steps, 4))
    tr = glow(s, C.text, z=3, k=0.6)
    for x in (0.0, 1.0, 2.0, 2.6, 3.0):
        p, q = P3(X(x), Y(2 ** x)), P3(X(2 ** x), Y(x))
        tr.add(DashedLine(p, q, stroke_color=C.text, stroke_width=1.6, dash_length=0.06, stroke_opacity=0.7))  # noqa: F821
    m.add(Dot(P3(X(3), Y(8)), radius=0.08, color=C.value), Dot(P3(X(8), Y(3)), radius=0.08, color=C.steps))  # noqa: F821
    m.add(tex("(3,8)", 28, C.value).next_to(P3(X(3), Y(8)), LEFT, buff=0.15),  # noqa: F821
          tex("(8,3)", 28, C.steps).next_to(P3(X(8), Y(3)), DOWN + RIGHT, buff=0.1))  # noqa: F821
    m.add(tex("y=2^x", 34, C.value).next_to(P3(X(2.55), Y(6.0)), LEFT, buff=0.15),  # noqa: F821
          tex(r"y=\log_2 x", 34, C.steps).move_to(P3(X(6.6), Y(1.7))),  # noqa: F821
          tex("y=x", 26, C.muted).move_to(P3(X(8.2), Y(8.9))))  # noqa: F821
    e = ctex([("y=2^x", C.value), (r"\ \longleftrightarrow\ ", None), (r"y=\log_2 x", C.steps)], 50)  # noqa: F821
    m.add(fit(e, 4.2).move_to(P3(3.95, 2.6)))
    m.add(sans("swap x and y", 24, C.muted).move_to(P3(3.95, 1.85)))  # noqa: F821
    m.add(rail(4, float(T.c04_s01) + 18))  # noqa: F821


def f7(s, m):
    """c05_s03 at 'the number e': the area under 1/x reaches exactly 1 at x = e."""
    ox, oy, u = -6.0, -2.4, 1.2
    g, X, Y = plane(ox, oy, u, (-0.3, 5.6), (-0.2, 4.6))
    m.add(g)
    for i in range(1, 6):
        m.add(tex(str(i), 22, C.muted).next_to(P3(X(i), oy), DOWN, buff=0.08))  # noqa: F821
    e = ld.E_FROM_AREA  # noqa: F821
    xs = np.linspace(1, e, 120)
    region = Polygon(*[P3(X(x), Y(1 / x)) for x in xs], P3(X(e), Y(0)), P3(X(1), Y(0)),  # noqa: F821
                     stroke_width=0, fill_color=C.area, fill_opacity=0.32)  # noqa: F821
    m.add(region)
    xh = np.linspace(0.22, 5.6, 300)
    m.add(polyline([(X(x), Y(1 / x)) for x in xh], C.text, 3.5))
    gl = glow(s, C.natural, z=3, k=1.0)  # noqa: F821
    gl.add(polyline([(X(x), Y(1 / x)) for x in xs], C.natural, 4))  # noqa: F821
    gl.add(Line(P3(X(e), Y(0)), P3(X(e), Y(1 / e)), stroke_color=C.natural, stroke_width=3))  # noqa: F821
    gl.add(Dot(P3(X(e), Y(0)), radius=0.085, color=C.natural))  # noqa: F821
    m.add(Line(P3(X(1), Y(0)), P3(X(1), Y(1)), stroke_color=tint(C.natural, 0.6), stroke_width=2))  # noqa: F821
    m.add(tex(r"y=\frac1x", 34, C.text).move_to(P3(X(1.35), Y(2.4))))  # noqa: F821
    m.add(tex("e", 40, C.natural).next_to(P3(X(e), Y(0)), UR, buff=0.12))  # noqa: F821
    ro = ctex([(r"\text{area}=", C.muted), ("1.000", C.steps)], 40).move_to(P3(X(3.9), Y(1.15)))  # noqa: F821
    m.add(ro, Line(ro.get_left() + LEFT * 0.1, P3(X(1.9), Y(0.3)), stroke_color=C.muted, stroke_width=1.5))  # noqa: F821
    col = VGroup(  # noqa: F821
        ctex([("e", C.natural), (r"\approx 2.71828", None)], 56),  # noqa: F821
        ctex([(r"\ln", C.natural), (" x", None), ("=", None), (r"\int_1^x\frac{dt}{t}", C.area)], 52),  # noqa: F821
        ctex([(r"\ln", C.natural), (" e", C.natural), ("=", None), ("1", C.steps)], 52),  # noqa: F821
        ctex([(r"\frac{d}{dx}", None), (r"\ln", C.natural), (r" x=\frac1x", None)], 52),  # noqa: F821
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to(P3(4.4, 0.75))
    m.add(col)
    m.add(rail(5, float(T.c05_s03) + 14))  # noqa: F821


def _rings(w=1500, h=1080, cx=0.42, cy=0.5):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot(xx - cx * w, yy - cy * h) / h
    wave = 0.5 + 0.5 * np.cos(2 * math.pi * (r * 9.0 - 0.3))
    env = np.exp(-r * 1.6) * _smooth((r - 0.012) / 0.03)
    I = (wave ** 6) * env
    col = _lin(C.sound)  # noqa: F821
    lin = I[..., None] * col * 1.2 + np.exp(-r * 30)[..., None] * col
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
    a = np.clip(I * 1.6 + np.exp(-r * 30), 0, 1)
    return feather(np.dstack([np.clip(srgb * 255, 0, 255), a * 255]).astype(np.uint8), 0.0, 0.25, 0.08, 0.08)


def f8(s, m):
    """c06_s01 at 'thousand times': sound rings; the decibel ruler; 90 dB vs 60 dB = three ×10 steps."""
    s.add(ArrayLayer(_rings(), height=8.0, pos=(-3.6, 0.0), z=-2))  # noqa: F821
    rx, y30, du = 0.9, -2.55, 0.08   # world units per dB
    Yd = lambda d: y30 + (d - 30) * du  # noqa: E731
    m.add(Line(P3(rx, Yd(30)), P3(rx, Yd(100)), stroke_color=C.ruler, stroke_width=2.5))  # noqa: F821
    for d in range(30, 101, 10):
        m.add(Line(P3(rx - 0.14, Yd(d)), P3(rx, Yd(d)), stroke_color=C.ruler, stroke_width=2),  # noqa: F821
              tex(str(d), 24, C.ruler).next_to(P3(rx - 0.14, Yd(d)), LEFT, buff=0.1))  # noqa: F821
    m.add(tex(r"\mathrm{dB}", 26, C.muted).move_to(P3(rx - 0.4, Yd(100) + 0.35)))  # noqa: F821
    for d, word in ((60, "conversation"), (90, "concert")):
        m.add(Dot(P3(rx, Yd(d)), radius=0.08, color=C.value),  # noqa: F821
              sans(word, 22, C.value).move_to(P3(rx + 1.0, Yd(d)), aligned_edge=LEFT))  # noqa: F821
    for k in range(3):
        a, b = Yd(60 + 10 * k), Yd(70 + 10 * k)
        m.add(ArcBetweenPoints(P3(rx + 0.12, a + 0.03), P3(rx + 0.12, b - 0.03), angle=-1.6,  # noqa: F821
                               stroke_color=C.base, stroke_width=2.5),
              tex(r"\times10", 22, C.base).move_to(P3(rx + 0.62, (a + b) / 2)))  # noqa: F821
    col = VGroup(  # noqa: F821
        ctex([("L", C.steps), (r"=10\log_{10}", None), (r"\frac{P}{P_0}", C.value)], 48),  # noqa: F821
        ctex([(r"90-60=", None), ("30", C.steps), (r"\ \mathrm{dB}", None)], 44),  # noqa: F821
        ctex([(r"10\times10\times10=", C.base), ("1000", C.value), (r"\times", None)], 44),  # noqa: F821
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
    m.add(fit(col, 3.1).move_to(P3(4.95, 0.9)))
    m.add(rail(6, float(T.c06_s01) + 20))  # noqa: F821


def f9(s, m):
    """c06_s03 at 'three steps for every two': Kepler's planets fall on a line of slope 3/2 on log-log axes."""
    ox, oy, u = -4.6, -0.775, 2.3
    xr, yr = (-0.5, 1.1), (-0.75, 1.6)
    X = lambda x: ox + u * x  # noqa: E731
    Y = lambda y: oy + u * y  # noqa: E731
    g = VGroup()  # noqa: F821
    for x in np.arange(-0.5, 1.11, 0.25):
        g.add(Line(P3(X(x), Y(yr[0])), P3(X(x), Y(yr[1])), stroke_color=C.grid_minor, stroke_width=1))  # noqa: F821
    for y in np.arange(-0.75, 1.61, 0.25):
        g.add(Line(P3(X(xr[0]), Y(y)), P3(X(xr[1]), Y(y)), stroke_color=C.grid_minor, stroke_width=1))  # noqa: F821
    for x in (0, 1):
        g.add(Line(P3(X(x), Y(yr[0])), P3(X(x), Y(yr[1])), stroke_color=C.grid, stroke_width=1.6))  # noqa: F821
    for y in (0, 1):
        g.add(Line(P3(X(xr[0]), Y(y)), P3(X(xr[1]), Y(y)), stroke_color=C.grid, stroke_width=1.6))  # noqa: F821
    m.add(g)
    m.add(Line(P3(X(xr[0]), Y(yr[0])), P3(X(xr[1]), Y(yr[0])), stroke_color=C.axis, stroke_width=2.2),  # noqa: F821
          Line(P3(X(xr[0]), Y(yr[0])), P3(X(xr[0]), Y(yr[1])), stroke_color=C.axis, stroke_width=2.2))  # noqa: F821
    for v, lab in ((0.1, "0.1"), (1, "1"), (10, "10")):
        lv = math.log10(v)
        if xr[0] <= lv <= xr[1]:
            m.add(tex(lab, 22, C.muted).next_to(P3(X(lv), Y(yr[0])), DOWN, buff=0.1))  # noqa: F821
        if yr[0] <= lv <= yr[1]:
            m.add(tex(lab, 22, C.muted).next_to(P3(X(xr[0]), Y(lv)), LEFT, buff=0.1))  # noqa: F821
    m.add(sans("distance (AU)", 22, C.muted).next_to(P3(X(xr[1]), Y(yr[0])), RIGHT, buff=0.15))  # noqa: F821
    m.add(sans("orbit time (years)", 22, C.muted).next_to(P3(X(xr[0]), Y(yr[1])), UP, buff=0.12)  # noqa: F821
          .align_to(P3(X(xr[0]) - 0.3, 0), LEFT))
    k, c = ld.KEPLER_SLOPE, ld.KEPLER_INTERCEPT  # noqa: F821
    m.add(Line(P3(X(-0.48), Y(k * -0.48 + c)), P3(X(1.08), Y(k * 1.08 + c)), stroke_color=C.steps, stroke_width=3))  # noqa: F821
    pts = glow(s, C.planet, z=3, k=0.8)  # noqa: F821
    for name, (a, T_) in ld.PLANETS.items():  # noqa: F821
        p = P3(X(math.log10(a)), Y(math.log10(T_)))
        pts.add(Dot(p, radius=0.09, color=C.planet))  # noqa: F821
        m.add(sans(name, 20, C.planet).next_to(p, UL if name != "Mercury" else UR, buff=0.08))  # noqa: F821
    ax, bx = 0.25, 0.75
    pa, pb, pc = P3(X(ax), Y(k * ax + c)), P3(X(bx), Y(k * ax + c)), P3(X(bx), Y(k * bx + c))
    m.add(Line(pa, pb, stroke_color=C.steps, stroke_width=2.5), Line(pb, pc, stroke_color=C.value, stroke_width=2.5))  # noqa: F821
    m.add(tex("2", 30, C.steps).next_to((pa + pb) / 2, DOWN, buff=0.1),  # noqa: F821
          tex("3", 30, C.value).next_to((pb + pc) / 2, RIGHT, buff=0.1))  # noqa: F821
    col = VGroup(  # noqa: F821
        ctex([("T", C.value), ("^2", None), (r"\propto", None), ("a", C.steps), ("^3", None)], 54),  # noqa: F821
        tex(r"\Downarrow", 40, C.muted),  # noqa: F821
        ctex([(r"\log T", C.value), ("=", None), (r"\tfrac32", C.text), (r"\log a", C.steps), ("+c", None)], 54),  # noqa: F821
        sans(f"fitted slope {k:.3f}", 22, C.muted),  # noqa: F821
    ).arrange(DOWN, buff=0.3).move_to(P3(3.4, 0.3))
    m.add(col)
    m.add(name_tag("Kepler · 1619", C.ch_world, at=P3(X1, Y1), edge=UR))  # noqa: F821
    m.add(rail(6, float(T.c06_s03) + 14))  # noqa: F821


def f10(s, m):
    """out_s01 at 'galaxies': six steps, one per chapter, each in its hue, with a key word and its equation."""
    words = ["count", "add", "ruler", "mirror", "e", "scales"]
    eqs = [r"\log_2 8=3", r"\log ab=\log a+\log b", r"\log2+\log3=\log6", r"y=\log_2 x", r"\ln e=1",
           r"\log T=\tfrac32\log a+c"]
    x0, y0, sw, sh = -6.0, -3.0, 2.05, 1.0
    pts = [(x0, y0)]
    for k in range(6):
        pts += [(x0 + k * sw, y0 + (k + 1) * sh), (x0 + (k + 1) * sw, y0 + (k + 1) * sh)]
    for k in range(6):
        hue = getattr(C, CHAPTERS[k])  # noqa: F821
        seg = [pts[2 * k], pts[2 * k + 1], pts[2 * k + 2]]
        (glow(s, hue, z=2, k=0.7) if k == 5 else m).add(polyline_corners(seg, hue, 4))
        tx = x0 + (k + 0.5) * sw
        ty = y0 + (k + 1) * sh
        m.add((tex("e", 34, hue) if words[k] == "e" else sans(words[k], 26, hue)).move_to(P3(tx, ty + 0.3)))  # noqa: F821
        m.add(fit(tex(eqs[k], 26, C.muted), sw - 0.45).move_to(P3(tx + 0.12, ty - 0.32)))  # noqa: F821
    m.add(caps("What logarithms actually are", 30, C.muted).move_to(P3(X1, Y0 + 0.1), aligned_edge=DR))  # noqa: F821


def f11(s, m):
    """Reference sheet: rail states, name tag, chapter card, type scale, palette."""
    m.add(sans("progress rail (bottom-left, true size)", 20, C.muted).move_to(P3(X0, 3.3), aligned_edge=LEFT))  # noqa: F821
    st = _chapter_spans()
    for y, k, f in ((2.6, 1, 0.15), (1.95, 3, 0.55), (1.3, 6, 0.95)):
        m.add(rail(k, st[k - 1] + f * (st[k] - st[k - 1]), y=y))
    m.add(sans("name tag (first mention, fades after 4 s)", 20, C.muted).move_to(P3(1.2, 3.3), aligned_edge=LEFT))  # noqa: F821
    m.add(name_tag("John Napier · 1614", C.base, at=P3(1.2, 2.85)))  # noqa: F821
    cy = -0.35
    m.add(sans("chapter card", 20, C.muted).move_to(P3(X0, 0.55), aligned_edge=LEFT))  # noqa: F821
    card = VGroup(caps(r"Why $e$", 48), Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=C.ch_e, stroke_width=3),  # noqa: F821
                  caps("chapter five", 24, C.muted)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # noqa: F821
    card[1].align_to(card[0], LEFT)
    m.add(card.move_to(P3(X0, cy), aligned_edge=LEFT))
    m.add(staircase(3, -2.2, cy - 0.7, 0.55, 0.42, show={0, 1, 2, 3}, label_size=22))
    ty = VGroup(  # noqa: F821
        VGroup(ctex([(r"\log_{", None), ("2", C.base), ("}", None), ("8", C.value), ("=", None), ("3", C.steps)], 44),  # noqa: F821
               sans("maths: CM roman, coloured by role", 18, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
        VGroup(sans("steps up", 26), sans("key words: CM sans", 18, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
        VGroup(caps("Counting multiplications", 28), sans("names, titles: small caps", 18, C.muted)).arrange(RIGHT, buff=0.3),  # noqa: F821
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(P3(X0, -2.65), aligned_edge=LEFT)
    m.add(ty)

    def chips(roles, size):
        return VGroup(*[VGroup(Square(side_length=size, stroke_width=0, fill_color=getattr(C, r), fill_opacity=1),  # noqa: F821
                               sans(r.replace("_", r"\_"), 13, C.muted)).arrange(DOWN, buff=0.05)  # noqa: F821
                        for r in roles]).arrange(RIGHT, buff=0.12)
    pal = VGroup(sans("roles of a logarithm", 18, C.muted), chips(("base", "steps", "value", "natural"), 0.42),  # noqa: F821
                 sans("objects", 18, C.muted),  # noqa: F821
                 chips(("ruler", "paper", "cell", "sound", "star", "quake", "acid", "planet"), 0.28),
                 sans("chapter hues (rail, card, tags)", 18, C.muted), chips(CHAPTERS, 0.28)).arrange(  # noqa: F821
        DOWN, aligned_edge=LEFT, buff=0.12).move_to(P3(X1, -1.2), aligned_edge=RIGHT)
    m.add(pal)


FRAMES = {1: f1, 2: f2, 3: f3, 4: f4, 5: f5, 6: f6, 7: f7, 8: f8, 9: f9, 10: f10, 11: f11}


def render(n: int) -> Path:
    from PIL import Image

    _import_aion()

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


if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(FRAMES)
    if len(want) == 1:
        render(want[0])
    else:
        for k in want:
            subprocess.run([sys.executable, __file__, str(k)], check=True, cwd=REPO)
