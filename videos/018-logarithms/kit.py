"""Shared screen language for video 018 (design/design_sheet.md §4): text helpers, role-coloured TeX, the feathered
shade, accent glow, name tags, the bottom-left progress rail, the chapter card, the multiplication staircase, and the
skia / numpy rasters (Napier's page, wooden rules). Promoted from design/style_frames.py so scenes and frames agree.

No boards, boxes or counters; text never glows; glow only on graphics. Colours are theme tokens only.

Example:
    from kit import *
    add_rail(s, 1)
    m.add(ctex([("2", C.base), ("^{10}", C.steps), ("=", None), ("1024", C.value)], 56))
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from aion import *  # noqa: F403

from beats import T
from theme import CHAPTERS

XW, YH = 64 / 9, 4.0
SAFE = 0.71
X0, X1, Y0, Y1 = -XW + SAFE, XW - SAFE, -YH + SAFE, YH - SAFE
RAIL_Y, RAIL_X1 = Y0 - 0.01, X0 + 5.0
COL = (2.75, X1)
RC = (COL[0] + COL[1]) / 2
CH_TITLES = ["Counting multiplications", "Multiplication becomes addition", "The slide rule", "The curve",
             r"Why $e$", "A world in logarithms"]
CH_NUM = ["one", "two", "three", "four", "five", "six"]


# ---------------------------------------------------------------------------------------------------- text
def _esc(s):
    return s.replace("%", r"\%").replace("&", r"\&")


def tex(s, size=48, color=None):
    return MathTex(s, font_size=size, color=color or C.text)  # noqa: F405


def ctex(parts, size=48):
    """MathTex from (tex, colour) parts, each part in its role colour (None = C.text)."""
    m = MathTex(*[p for p, _ in parts], font_size=size)  # noqa: F405
    for sub, (_, c) in zip(m, parts):
        sub.set_color(c or C.text)  # noqa: F405
    return m


def sans(s, size=28, color=None):
    return Tex(r"\textsf{" + _esc(s) + "}", font_size=size, color=color or C.text)  # noqa: F405


def caps(s, size=34, color=None):
    return Tex(r"\textsc{" + _esc(s) + "}", font_size=size, color=color or C.text)  # noqa: F405


def P3(x, y):
    return np.array([float(x), float(y), 0.0])


def lin_rgb(h):
    c = np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _hex(lin):
    lin = np.clip(lin, 0, 1)
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in s)


def tint(color, a):
    """`color` at opacity `a` over black (linear light), as one solid hex."""
    return _hex(lin_rgb(color) * a)


def mix(a, b, t):
    return _hex(lin_rgb(a) * (1 - t) + lin_rgb(b) * t)


def smooth01(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3 - 2 * x)


def ramp(t, t0, dur):
    """0 → 1 smoothly over [t0, t0 + dur] (pure in t)."""
    return smooth01((t - float(t0)) / dur)


def fit(mob, width=COL[1] - COL[0]):
    if mob.width > width:
        mob.scale(width / mob.width)
    return mob


def polyline(pts, color, width=3.0, opacity=1.0, smooth=False):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)  # noqa: F405
    pp = [P3(*p) for p in pts]
    v.set_points_smoothly(pp) if smooth and len(pp) > 2 else v.set_points_as_corners(pp)
    return v


# ---------------------------------------------------------------------------------------------------- surfaces
def _smooth_arr(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def feather(rgba, left=0.0, right=0.0, top=0.0, bottom=0.0):
    """Fade a raster's alpha to 0 over the given fractions of its width/height (no hard raster edges)."""
    h, w = rgba.shape[:2]
    a = np.ones((h, w))
    xs, ys = np.linspace(0, 1, w)[None, :], np.linspace(0, 1, h)[:, None]
    if left:
        a = a * _smooth_arr(xs / left)
    if right:
        a = a * _smooth_arr((1 - xs) / right)
    if top:
        a = a * _smooth_arr(ys / top)
    if bottom:
        a = a * _smooth_arr((1 - ys) / bottom)
    out = rgba.copy()
    out[..., 3] = (out[..., 3] * a).astype(np.uint8)
    return out


def shade(s, cx, cy, w, h, a=0.82, z=-1, **kw):
    """An invisible darkening under text that sits on a busy raster (soft superellipse; never a visible box)."""
    ppu = 40
    nx, ny = max(8, int(w * 1.4 * ppu)), max(8, int(h * 1.4 * ppu))
    xx, yy = np.linspace(-1.4, 1.4, nx)[None, :], np.linspace(-1.4, 1.4, ny)[:, None]
    d = (np.abs(xx) ** 4 + np.abs(yy) ** 4) ** 0.25
    img = np.zeros((ny, nx, 4), np.uint8)
    img[..., 3] = (a * _smooth_arr((1.4 - d) / 0.6) * 255).astype(np.uint8)
    return s.add(ArrayLayer(img, height=h * 1.4, pos=(cx, cy), z=z, **kw))  # noqa: F405


def glow(s, color, z=2, k=1.0, **kw):
    """A Manim layer whose shapes glow in `color` (graphic payoff elements only; never text)."""
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=C.glow_r)], **kw)  # noqa: F405


def name_tag(text, hue, at=None, edge=None):
    """A short hue rule over a small-caps name and year. No box. First mention only; fade it after ~4 s."""
    rule = Line(LEFT * 0.35, RIGHT * 0.35, stroke_color=hue, stroke_width=3)  # noqa: F405
    g = VGroup(rule, caps(text, 30, C.text)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)  # noqa: F405
    return g.move_to(at if at is not None else P3(X0, Y1), aligned_edge=edge if edge is not None else UL)  # noqa: F405


def show_tag(s, text, hue, when, dur=4.0, z=60, **kw):
    """Fade a name tag in landing on `when` and out `dur` seconds later (screen-locked); `at=` places it."""
    lay = s.manim(z=z, parallax=0.0, opacity=fade(when, dur=0.5, out=float(when) + dur, out_dur=0.6))  # noqa: F405
    lay.add(name_tag(text, hue, **kw))
    return lay


# ---------------------------------------------------------------------------------------------------- rail
def chapter_spans():
    """Start times of chapters 1..6 and the outro (7 values)."""
    return np.array([float(getattr(T, f"c{i:02d}_s01")) for i in range(1, 7)] + [float(T.out_s01)])


def _rail_geom(x0=X0, x1=RAIL_X1):
    st = chapter_spans()
    durs = np.diff(st)
    gap = 0.05
    span = (x1 - x0) - gap * 5
    xs, xa = [], x0
    for d in durs:
        xs.append((xa, xa + span * d / durs.sum()))
        xa = xs[-1][1] + gap
    return st, durs, xs


def rail_static(k, y=RAIL_Y):
    st, durs, xs = _rail_geom()
    g = VGroup()  # noqa: F405
    for i, (xa, xb) in enumerate(xs):
        hue = getattr(C, CHAPTERS[i])  # noqa: F405
        if i + 1 < k:
            g.add(Line(P3(xa, y), P3(xb, y), stroke_color=tint(hue, 0.5), stroke_width=2.5))  # noqa: F405
        else:
            g.add(Line(P3(xa, y), P3(xb, y), stroke_color=tint(C.muted, 0.45), stroke_width=1.5))  # noqa: F405
    g.add(caps(CH_TITLES[k - 1], 20, C.text).move_to(P3(X0, y + 0.17), aligned_edge=DL))  # noqa: F405
    return g


def rail_live(k, t, y=RAIL_Y):
    st, durs, xs = _rail_geom()
    i = k - 1
    xa, xb = xs[i]
    w = xb - xa
    hue = getattr(C, CHAPTERS[i])  # noqa: F405
    f = float(np.clip((t - st[i]) / durs[i], 0, 1))
    xf = xa + f * w
    g = VGroup()  # noqa: F405
    n_seg = 24
    for j in range(n_seg):
        a0, a1 = xa + (xf - xa) * j / n_seg, xa + (xf - xa) * (j + 1) / n_seg
        if a1 - a0 > 1e-4:
            g.add(Line(P3(a0, y), P3(a1, y), stroke_width=4,  # noqa: F405
                       stroke_color=tint(hue, 0.35 + 0.65 * ((j + 1) / n_seg) ** 2)))
    for sc in ("s02", "s03"):
        ts = float(getattr(T, f"c{k:02d}_{sc}"))
        xt = xa + w * (ts - st[i]) / durs[i]
        g.add(Line(P3(xt, y - 0.06), P3(xt, y + 0.06), stroke_color=hue if xt <= xf else C.muted,  # noqa: F405
                   stroke_width=1.5))
    g.add(Circle(radius=0.085, stroke_color=hue, stroke_width=1.5).move_to(P3(xf, y)),  # noqa: F405
          Dot(P3(xf, y), radius=0.04, color=C.text))  # noqa: F405
    return g


def add_rail(s, k, opacity=1.0, z=80, busy=False):
    """Chapter k's progress rail as a screen-locked layer, live for the whole scene. `busy` lays a shade under it."""
    if busy:
        shade(s, (X0 + RAIL_X1) / 2, RAIL_Y + 0.12, RAIL_X1 - X0 + 0.3, 0.55, a=0.75, z=z - 1, parallax=0.0,
              opacity=opacity)
    hud = s.manim(z=z, parallax=0.0, opacity=opacity)
    hud.add(rail_static(k))
    hud.redraw(lambda t: rail_live(k, t), during=(s.start, s.end))
    return hud


def chapter_card(s, k, at, out, z=90):
    """The chapter card on black: title in small caps 48, a 3.2 u rule in the chapter hue, 'chapter n' in small caps
    24 muted, and a three-step staircase vignette in the hue. Fades in landing on `at`, out landing on `out`;
    a slow push-in 1.03 → 1.0. Screen-locked."""
    hue = getattr(C, CHAPTERS[k - 1])  # noqa: F405
    op = fade(at, dur=0.5, out=out, out_dur=0.5)  # noqa: F405
    title = caps(CH_TITLES[k - 1], 48, C.text)
    rule = Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=hue, stroke_width=3)  # noqa: F405
    sub = caps(f"chapter {CH_NUM[k - 1]}", 24, C.muted)
    card = VGroup(title, rule, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.22)  # noqa: F405
    rule.align_to(title, LEFT)
    vig = VGroup()  # noqa: F405
    sw, sh = 0.42, 0.3
    pts = [(0, 0)]
    for j in range(3):
        pts += [(j * sw, (j + 1) * sh), ((j + 1) * sw, (j + 1) * sh)]
    vig.add(polyline(pts, hue, 2.5))
    grp = VGroup(vig, card).arrange(RIGHT, buff=0.55, aligned_edge=DOWN).move_to(P3(0, 0.15))  # noqa: F405
    lay = s.manim(z=z, parallax=0.0, opacity=op)
    a0, a1 = float(at) - 0.5, float(out) + 0.1
    lay.redraw(lambda t: grp.copy().scale(1.03 - 0.03 * ramp(t, a0, a1 - a0), about_point=P3(0, 0.15)),
               during=(max(a0, float(s.start)), min(a1, float(s.end))))
    return lay


# ---------------------------------------------------------------------------------------------------- staircase
def stair_points(n, x0, y0, sw, sh):
    """Corner points of the staircase: tread k spans [x0 + k·sw, x0 + (k+1)·sw] at height y0 + k·sh."""
    pts = [(x0, y0)]
    for k in range(n + 1):
        y = y0 + k * sh
        pts.append((x0 + (k + 1) * sw, y))
        if k < n:
            pts.append((x0 + (k + 1) * sw, y + sh))
    return pts


def staircase(n, x0, y0, sw, sh, base=2, show=None, label_size=30, risers=True, axis=True, values=None,
              value_color=None, upto=None):
    """The motif: n+1 treads (levels 0…n), rising sh per step from (x0, y0). Tread k carries its value (C.value),
    each riser a ×base tag (C.base), and a left axis counts the steps (C.steps), so height = the logarithm.
    `values` overrides the tread labels; `show` limits which levels are labelled; `upto` draws only levels ≤ upto.
    Returns a VGroup with named parts: .path, .vals, .tags, .axis."""
    upto = n if upto is None else upto
    g = VGroup()  # noqa: F405
    pts = stair_points(upto, x0, y0, sw, sh)
    g.path = polyline(pts, C.text, 3)  # noqa: F405
    g.floor = Line(P3(x0 - 0.1, y0), P3(x0 + (n + 1) * sw + 0.2, y0), stroke_color=C.muted, stroke_width=1.2)  # noqa: F405
    g.vals, g.tags, g.axis = VGroup(), VGroup(), VGroup()  # noqa: F405
    for k in range(upto + 1):
        y = y0 + k * sh
        if show is None or k in show:
            v = values[k] if values is not None else base ** k
            lab = v if isinstance(v, str) else str(v)
            size = label_size * (1.0 if len(lab) < 3 else 0.86)
            g.vals.add(tex(lab, size, value_color or C.value).move_to(P3(x0 + (k + 0.5) * sw, y + 0.08),  # noqa: F405
                                                                      aligned_edge=DOWN))  # noqa: F405
        if risers and k < upto:
            g.tags.add(tex(rf"\times{base}", label_size * 0.64, C.base)  # noqa: F405
                       .move_to(P3(x0 + (k + 1) * sw + 0.07, y + sh / 2), aligned_edge=LEFT))  # noqa: F405
    if axis:
        ax = x0 - 0.35
        g.axis.add(Line(P3(ax, y0), P3(ax, y0 + upto * sh), stroke_color=C.steps, stroke_width=2))  # noqa: F405
        for k in range(upto + 1):
            g.axis.add(Line(P3(ax - 0.07, y0 + k * sh), P3(ax + 0.07, y0 + k * sh), stroke_color=C.steps,  # noqa: F405
                            stroke_width=2))
            if show is None or k in show:
                g.axis.add(tex(str(k), label_size * 0.72, C.steps).next_to(P3(ax - 0.07, y0 + k * sh), LEFT,  # noqa: F405
                                                                          buff=0.08))
    g.add(g.floor, g.path, g.vals, g.tags, g.axis)
    return g


# ---------------------------------------------------------------------------------------------------- rasters
def skia_rgba(w, h, draw):
    import skia
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    draw(cv, skia)
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def _skc(skia, h, a=255):
    r, g, b = (int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return skia.Color(r, g, b, a)


def paper_page(w=900, h=1200, seed=1614, dim=1.0, res=1.0):
    """Napier's page: warm paper with fibre noise, two ruled columns of seven-figure numbers (a texture, not text).
    `res` scales the raster (and everything drawn on it) for crisp close-ups; the layout is the same at any res.

    Example:
        ArrayLayer(paper_page(seed=1614, res=1.6), height=6.0)
    """
    rng = np.random.default_rng(seed)
    nums = [(f"{int(rng.integers(1_000_000, 9_999_999)):07d}", f"{int(rng.integers(1_000_000, 9_999_999)):07d}")
            for _ in range(38)]
    k = res
    W, H = int(round(w * k)), int(round(h * k))

    def draw(cv, skia):
        cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=_skc(skia, C.paper)))  # noqa: F405
        ink = skia.Paint(Color=skia.Color(52, 38, 26, 225), AntiAlias=True)
        rule = skia.Paint(Color=skia.Color(52, 38, 26, 160), StrokeWidth=1.6 * k, Style=skia.Paint.kStroke_Style,
                          AntiAlias=True)
        font = skia.Font(skia.Typeface("serif"), 24 * k)
        cv.drawLine(70 * k, 110 * k, W - 70 * k, 110 * k, rule)
        cv.drawLine(W / 2, 120 * k, W / 2, H - 80 * k, rule)
        cv.drawString("LOGARITHMORUM", W / 2 - 150 * k, 80 * k, skia.Font(skia.Typeface("serif"), 34 * k), ink)
        for i, (a, b) in enumerate(nums):
            y = (160 + i * 27) * k
            cv.drawString(f"{i:2d}", 80 * k, y, font, ink)
            cv.drawString(a, 160 * k, y, font, ink)
            cv.drawString(b, W / 2 + 80 * k, y, font, ink)
            cv.drawString(f"{(i * 37) % 60:02d}", W - 130 * k, y, font, ink)

    img = skia_rgba(W, H, draw).astype(np.float32)
    from scipy.ndimage import gaussian_filter
    fib = gaussian_filter(rng.standard_normal((H, W)), (0.6 * k, 6 * k)) * 0.9 + \
        gaussian_filter(rng.standard_normal((H, W)), 18 * k) * 4
    fib = 1 + 0.14 * fib / (np.abs(fib).max() + 1e-9)
    vign = 1 - 0.30 * (np.hypot(np.linspace(-1, 1, W)[None], np.linspace(-1, 1, H)[:, None]) / 1.41) ** 2
    img[..., :3] = np.clip(img[..., :3] * (fib * vign * dim)[..., None], 0, 255)
    return feather(img.astype(np.uint8), 0.03, 0.03, 0.025, 0.025)


PAGE_ROW = lambda i: (160 + i * 27) / 1200  # noqa: E731  row i's baseline as a fraction of the page height, from the top


def wood(w, h, seed=1622):
    """A boxwood rule body: warm gradient with fine grain, a thin bevel line top and bottom."""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    base = np.array([196, 160, 104], np.float32)[None, :] * (0.82 + 0.18 * np.sin(np.pi * y))
    from scipy.ndimage import gaussian_filter
    grain = gaussian_filter(rng.standard_normal((h, w)), (0.8, 40))
    grain = grain / (np.abs(grain).max() + 1e-9)
    img = np.clip(base[:, None, :] * (1 + 0.10 * grain)[..., None], 0, 255)
    rgba = np.dstack([img, np.full((h, w), 255, np.float32)]).astype(np.uint8)
    rgba[:2, :, :3] = 235
    rgba[-2:, :, :3] = 90
    return feather(rgba, 0.015, 0.015, 0, 0)


RULE_INK = "#2A1E12"   # engraving on boxwood (a raster ink, not a screen colour)


def log_scale_marks(x0, L, edge, up, label_size=26, vmax=10, ink=RULE_INK, skip=()):
    """Engraved ticks and numbers of a 1…10 log scale of length L starting at x0, hanging from `edge`
    (down into the rule if `up` is False, up into it if True)."""
    sgn = -1 if up else 1
    g = VGroup()  # noqa: F405
    vals = [1 + i / 10 for i in range(10)] + [2 + i / 5 for i in range(0, 15)] + list(range(5, 11)) + \
        [5.5, 6.5, 7.5, 8.5, 9.5]
    for v in sorted(set(round(v, 3) for v in vals)):
        if v > vmax + 1e-9:
            continue
        x = x0 + L * math.log10(v)
        major = abs(v - round(v)) < 1e-9
        ln = 0.30 if major else (0.18 if abs(v * 2 - round(v * 2)) < 1e-9 else 0.11)
        g.add(Line(P3(x, edge), P3(x, edge - sgn * ln), stroke_color=ink, stroke_width=2 if major else 1.2))  # noqa: F405
        if major and int(round(v)) not in skip:
            iv = int(round(v))
            dx = 0.14 if iv == 1 else (-0.18 if iv == 10 else 0.0)
            g.add(tex(str(iv), label_size, ink).move_to(P3(x + dx, edge - sgn * 0.5)))  # noqa: F405
    return g


def log_mark():
    """The word log as the intro writes it (centre of the frame); in_s02 carries it on and parks it top-left."""
    return tex(r"\log", 110, C.text).move_to(P3(0, 0.25))


def plane(ox, oy, u, xr, yr, minor=True):
    """The Classic grid: dim minor lines, bright blue integer lines, white axes; origin at (ox, oy), u world units per
    unit. Returns (VGroup, X, Y) where X, Y map graph coordinates to world coordinates."""
    g = VGroup()  # noqa: F405
    X = lambda x: ox + u * x  # noqa: E731
    Y = lambda y: oy + u * y  # noqa: E731
    if minor:
        for x in np.arange(xr[0], xr[1] + 1e-9, 0.5):
            g.add(Line(P3(X(x), Y(yr[0])), P3(X(x), Y(yr[1])), stroke_color=C.grid_minor, stroke_width=1))  # noqa: F405
        for y in np.arange(yr[0], yr[1] + 1e-9, 0.5):
            g.add(Line(P3(X(xr[0]), Y(y)), P3(X(xr[1]), Y(y)), stroke_color=C.grid_minor, stroke_width=1))  # noqa: F405
    for x in range(math.ceil(xr[0]), math.floor(xr[1]) + 1):
        g.add(Line(P3(X(x), Y(yr[0])), P3(X(x), Y(yr[1])), stroke_color=C.grid, stroke_width=1.6))  # noqa: F405
    for y in range(math.ceil(yr[0]), math.floor(yr[1]) + 1):
        g.add(Line(P3(X(xr[0]), Y(y)), P3(X(xr[1]), Y(y)), stroke_color=C.grid, stroke_width=1.6))  # noqa: F405
    g.add(Line(P3(X(xr[0]), oy), P3(X(xr[1]), oy), stroke_color=C.axis, stroke_width=2.4),  # noqa: F405
          Line(P3(ox, Y(yr[0])), P3(ox, Y(yr[1])), stroke_color=C.axis, stroke_width=2.4))  # noqa: F405
    return g, X, Y


def mirror_point(x, y, th):
    """(x, y) rotated by th about the line y = x (a 3D flip seen from the front): th = π swaps x and y."""
    a, b = (x + y) / math.sqrt(2), (x - y) / math.sqrt(2) * math.cos(th)
    return (a + b) / math.sqrt(2), (a - b) / math.sqrt(2)


_WORDS = None


def word_at(word, after):
    """Start time of the first spoken `word` at or after `after` (assets/words.json, the narration's own cues)."""
    global _WORDS
    if _WORDS is None:
        import json
        from pathlib import Path
        w = json.loads((Path(__file__).parent / "assets/words.json").read_text())
        _WORDS = [(x["text"].strip(".,;:?!").lower(), float(x["start"]), float(x["end"]))
                  for x in (w["words"] if isinstance(w, dict) else w)]
    for t, st, _ in _WORDS:
        if t == word.lower() and st >= float(after) - 1e-6:
            return st
    raise KeyError(f"{word!r} after {after}")


def silence(cut):
    """(end of the last word before `cut`, start of the first word after it): the pause a scene cut sits in."""
    word_at("the", 0) if _WORDS is None else None
    c = float(cut)
    before = max(e for _, st, e in _WORDS if st < c)
    after = min(st for _, st, _ in _WORDS if st >= c)
    return before, after


def chapter_break(s, k, cut):
    """The pause before chapter k: the frame darkens under the rail, the chapter card shows, and the next chapter's
    picture starts from black. Call it in both scenes that meet at `cut` (it is pure in t, so it runs across the cut)."""
    te, tw = silence(cut)
    s.add(Solid(C.bg, z=79, opacity=fade(te + 0.35, dur=0.5, out=tw + 0.3, out_dur=0.4)))  # noqa: F405
    chapter_card(s, k, at=te + 0.8, out=tw - 0.05)


def wood_body(length, height, seed=1622, pad=0.35):
    """Wood raster for a rule whose 1…10 scale is `length` long: the body runs `pad` past each end.
    Returns (rgba, body length); centre the layer at the scale's midpoint."""
    w = length + 2 * pad
    return wood(int(round(140 * w / height)), 140, seed=seed), w


def soft_shadow(w, h, blur=0.12, a=0.8, ppu=60):
    """A soft dark alpha blob the size of a w × h (world units) object, for a drop shadow under a raster layer.
    Returns (rgba, layer height): the raster is padded by 3·blur on every side, so use that height for the layer."""
    from scipy.ndimage import gaussian_filter
    pad = 3 * blur
    W, H = int(round((w + 2 * pad) * ppu)), int(round((h + 2 * pad) * ppu))
    al = np.zeros((H, W), np.float32)
    p = int(round(pad * ppu))
    al[p:H - p, p:W - p] = 1
    al = gaussian_filter(al, blur * ppu) * a
    img = np.zeros((H, W, 4), np.uint8)
    img[..., 3] = (al * 255).astype(np.uint8)
    return img, h + 2 * pad


def piano(n_white, kw=60, h=240, seed=88):
    """A keyboard raster that starts on A: ivory white keys with a soft top-to-bottom shade and thin separators,
    glossy black keys (A#, C#, D#, F#, G#) at 60 % height. Width n_white·kw px; centre the layer on the keys."""
    def draw(cv, skia):
        W = n_white * kw
        ivory = skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, 0), skia.Point(0, h)], [skia.Color(214, 204, 184), skia.Color(240, 233, 216)]))
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, h), ivory)
        sep = skia.Paint(Color=skia.Color(120, 110, 96), StrokeWidth=2, AntiAlias=True)
        for i in range(1, n_white):
            cv.drawLine(i * kw, 0, i * kw, h, sep)
        edge = skia.Paint(Color=skia.Color(150, 138, 118), StrokeWidth=3, Style=skia.Paint.kStroke_Style)
        cv.drawRect(skia.Rect.MakeXYWH(1.5, 1.5, W - 3, h - 3), edge)
        lip = skia.Paint(Color=skia.Color(255, 250, 238, 140))
        cv.drawRect(skia.Rect.MakeXYWH(0, h - 10, W, 6), lip)
        pattern = [1, 0, 1, 1, 0, 1, 1]
        for i in range(n_white - 1):
            if not pattern[i % 7]:
                continue
            bw, bh = kw * 0.58, h * 0.6
            x = (i + 1) * kw - bw / 2
            body = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
                [skia.Point(0, 0), skia.Point(0, bh)], [skia.Color(18, 16, 15), skia.Color(52, 48, 44)]))
            cv.drawRoundRect(skia.Rect.MakeXYWH(x, -4, bw, bh + 4), 4, 4, body)
            gloss = skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, 38))
            cv.drawRoundRect(skia.Rect.MakeXYWH(x + bw * 0.18, 4, bw * 0.22, bh * 0.8), 3, 3, gloss)
    return skia_rgba(n_white * kw, h, draw)


def portrait(path, ppu=150, height=3.0, mat=0.07, tone=0.85):
    """A historical portrait as a print: sepia duotone (ink → paper, mixed `tone` with the original), a cream mat of
    `mat` × height on every side with a thin ink rule round the picture, and a soft vignette. Returns the RGBA raster
    for a layer `height` world units tall (the mat included)."""
    from PIL import Image
    from scipy.ndimage import gaussian_filter
    img = Image.open(Path(__file__).resolve().parent / path).convert("RGB")
    H = int(round(height * ppu))
    m = int(round(mat * H))
    ih = H - 2 * m
    iw = int(round(img.width * ih / img.height))
    src = np.asarray(img.resize((iw, ih), Image.LANCZOS), np.float32) / 255
    lum = (src @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    ink, paper = np.array([40, 30, 22], np.float32) / 255, np.array([236, 222, 194], np.float32) / 255
    duo = ink + (paper - ink) * lum
    pic = tone * duo + (1 - tone) * src
    yy, xx = np.mgrid[0:ih, 0:iw]
    r = np.hypot((xx - iw / 2) / (iw / 2), (yy - ih / 2) / (ih / 2))
    pic *= (1 - 0.22 * np.clip(r - 0.55, 0, 1))[..., None]
    W = iw + 2 * m
    out = np.empty((H, W, 3), np.float32)
    out[:] = np.array([224, 210, 182], np.float32) / 255 * (0.97 + 0.03 * gaussian_filter(
        np.random.default_rng(7).standard_normal((H, W)), 2)[..., None])
    out[m:m + ih, m:m + iw] = pic
    k = max(1, H // 260)
    for a, b in ((m - 2 * k, m - k), (m + ih + k, m + ih + 2 * k)):
        out[a:b, m - 2 * k:m + iw + 2 * k] = ink
    for a, b in ((m - 2 * k, m - k), (m + iw + k, m + iw + 2 * k)):
        out[m - 2 * k:m + ih + 2 * k, a:b] = ink
    rgba = np.dstack([np.clip(out * 255, 0, 255), np.full((H, W), 255, np.float32)]).astype(np.uint8)
    return rgba
