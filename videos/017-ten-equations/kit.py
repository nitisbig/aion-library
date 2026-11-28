"""Shared screen language for video 017 (see design/design_sheet.md §2): text helpers, the feathered shade, name tags,
the bottom-left progress rail and the chapter card. Promoted from design/style_frames.py so scenes and frames agree.

No boards, boxes or counters; text never glows; glow only on graphics (`glow`). Colours are theme tokens only.

Example:
    from kit import *
    hud = add_rail(s, 1)                       # the progress rail for chapter 1, live for the whole scene
    m.add(name_tag("James Clerk Maxwell · 1865", C.maxwell))
"""
from __future__ import annotations

import numpy as np
from aion import *  # noqa: F403

from beats import T
from theme import CHAPTERS

XW, YH = 64 / 9, 4.0                         # half frame (world units)
SAFE = 0.71                                  # text-safe inset (96 px at 1080p)
X0, X1, Y0, Y1 = -XW + SAFE, XW - SAFE, -YH + SAFE, YH - SAFE
RAIL_Y, RAIL_X1 = Y0 - 0.01, X0 + 5.0        # progress rail: bottom-left, 5 u long
COL = (2.75, X1)                             # the open right column where equations float
RC = (COL[0] + COL[1]) / 2
CH_TITLES = ["Maxwell's equations", "Einstein's field equations", "Schrödinger's equation", "Navier--Stokes",
             "The Fourier transform", "Time dilation", "Gradient descent", "Shannon's capacity", "Bayes' theorem",
             "Black--Scholes"]
CH_NAMES = ["James Clerk Maxwell · 1865", "Albert Einstein · 1915", "Erwin Schrödinger · 1926",
            "Navier 1822 · Stokes 1845", "Joseph Fourier · 1807", "Albert Einstein · 1905",
            "Augustin-Louis Cauchy · 1847", "Claude Shannon · 1948", "Thomas Bayes · 1763",
            "Black · Scholes · Merton · 1973"]
CH_PORTRAITS = ["maxwell", "einstein_1921", "schrodinger", None, "fourier", "einstein_1905", "cauchy", "shannon",
                "bayes", None]


# ---------------------------------------------------------------------------------------------------- text
def _esc(s):
    return s.replace("$", r"\$").replace("%", r"\%").replace("&", r"\&").replace("Ø", r"\O{}").replace("ö", r"\"{o}")


def tex(s, size=48, color=None):
    """Maths in CM roman."""
    return MathTex(s, font_size=size, color=color or C.text)  # noqa: F405


def sans(s, size=28, color=None):
    """Key words, tags and axis names in CM sans."""
    return Tex(r"\textsf{" + _esc(s) + "}", font_size=size, color=color or C.text)  # noqa: F405


def caps(s, size=34, color=None):
    """Names, dates and titles in CM small caps."""
    return Tex(r"\textsc{" + _esc(s) + "}", font_size=size, color=color or C.text)  # noqa: F405


def P3(x, y):
    return np.array([float(x), float(y), 0.0])


# ---------------------------------------------------------------------------------------------------- colour
def _lin(h):
    c = np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _hex(lin):
    lin = np.clip(lin, 0, 1)
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in s)


def lin_rgb(color):
    """A hex token as a linear-light RGB array (for numpy rasters)."""
    return _lin(color)


def tint(color, a):
    """`color` at opacity `a` over black, mixed in linear light, as one solid hex."""
    return _hex(_lin(color) * a)


def mix(a, b, t):
    """Linear-light mix of two hex colours."""
    return _hex(_lin(a) * (1 - t) + _lin(b) * t)


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------------------------------------------- rasters
def sphere_rgba(color, n=360, light=(-0.5, 0.62, 0.6), ambient=0.06, emit=0.0):
    """A sphere lit from `light` (matte, linear-light shading) in a theme colour, antialiased edge, as RGBA uint8.
    `emit` > 0 adds a flat self-lit part (a star's disc).

    Example:
        s.add(ArrayLayer(sphere_rgba(C.mass), height=1.7, pos=(2.7, -0.5)))
    """
    c = (np.arange(n) + 0.5) / n * 2 - 1
    x, y = np.meshgrid(c, -c)
    r2 = x * x + y * y
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    L = np.asarray(light, float)
    L /= np.linalg.norm(L)
    lam = np.clip(x * L[0] + y * L[1] + nz * L[2], 0, 1)
    lin = _lin(color)[None, None, :] * np.clip(emit + (ambient + (1 - ambient) * lam[..., None]) ** 1.2, 0, 1)
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.clip(lin, 0, 1) ** (1 / 2.4) - 0.055)
    out = np.zeros((n, n, 4), np.uint8)
    out[..., :3] = (srgb * 255 + 0.5).astype(np.uint8)
    out[..., 3] = (np.clip((1 - np.sqrt(r2)) * n / 2, 0, 1) * 255).astype(np.uint8)
    return out


# ---------------------------------------------------------------------------------------------------- layers
def shade(s, cx, cy, w, h, a=0.82, z=-1, **kw):
    """An invisible darkening under text that sits on a busy picture: black, soft superellipse alpha.
    Full strength over the inner 80 % of (w, h), gone by 140 %. Never a visible rectangle."""
    ppu = 40
    nx, ny = max(8, int(w * 1.4 * ppu)), max(8, int(h * 1.4 * ppu))
    xx, yy = np.linspace(-1.4, 1.4, nx)[None, :], np.linspace(-1.4, 1.4, ny)[:, None]
    d = (np.abs(xx) ** 4 + np.abs(yy) ** 4) ** 0.25
    al = a * smooth01((1.4 - d) / 0.6)
    img = np.zeros((ny, nx, 4), np.uint8)
    img[..., 3] = (al * 255).astype(np.uint8)
    return s.add(ArrayLayer(img, height=h * 1.4, pos=(cx, cy), z=z, **kw))  # noqa: F405


def glow(s, color, z=2, k=1.0, **kw):
    """A Manim layer whose shapes glow in `color`: accent glow on graphic payoff elements only, never text."""
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=C.glow_r)], **kw)  # noqa: F405


def polyline(pts, color, width=3.0, opacity=1.0):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)  # noqa: F405
    v.set_points_as_corners([P3(*p) for p in pts])
    return v


def smooth_curve(pts, color, width=3.0, opacity=1.0):
    v = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)  # noqa: F405
    v.set_points_smoothly([P3(*p) for p in pts])
    return v


def fit(mob, width=COL[1] - COL[0]):
    """Scale `mob` down (never up) to `width`."""
    if mob.width > width:
        mob.scale(width / mob.width)
    return mob


_METRICS = {}


def _sans_metrics(size):
    if size not in _METRICS:
        hx, hg, hH = (sans(c, size).height for c in ("x", "g", "H"))
        _METRICS[size] = (hH, hg - hx)
    return _METRICS[size]


def tag_under(eqn, part, text, color=None, buff=0.16, size=22):
    """A key-word tag centred under one term of an Eqn; tags of one equation share a typographic baseline."""
    p = eqn.part(part)
    lab = sans(text, size, color or C.muted)  # noqa: F405
    cap, depth = _sans_metrics(size)
    base = eqn.get_bottom()[1] - buff - cap
    bottom = base - (depth if any(ch in text for ch in "gjpqy") else 0.0)
    return lab.move_to(P3(p.get_center()[0], bottom), aligned_edge=DOWN)  # noqa: F405


def name_tag(text, hue, at=None, edge=None):
    """A short rule in the chapter hue over a small-caps name and year, top-left by default. No box behind it."""
    rule = Line(LEFT * 0.35, RIGHT * 0.35, stroke_color=hue, stroke_width=3)  # noqa: F405
    g = VGroup(rule, caps(text, 30, C.text)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)  # noqa: F405
    return g.move_to(at if at is not None else P3(X0, Y1), aligned_edge=edge if edge is not None else UL)  # noqa: F405


# ---------------------------------------------------------------------------------------------------- rail
def chapter_spans():
    """Start times of chapters 1..10 and the outro (11 values)."""
    return np.array([float(getattr(T, f"c{i:02d}_s01")) for i in range(1, 11)] + [float(T.out_s01)])


def _rail_geom(x0=X0, x1=RAIL_X1):
    st = chapter_spans()
    durs = np.diff(st)
    gap = 0.05
    span = (x1 - x0) - gap * 9
    xs, xa = [], x0
    for d in durs:
        xs.append((xa, xa + span * d / durs.sum()))
        xa = xs[-1][1] + gap
    return st, durs, xs


def rail_static(k, y=RAIL_Y):
    """The parts of the rail that hold still during chapter k: past segments (hue at 50 %), future ghosts, the
    current chapter's ghost track and its title in small caps above the left end."""
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
    """The moving part: a fill brightening towards the head (a comet), scene ticks, and the head itself."""
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
            g.add(Line(P3(a0, y), P3(a1, y), stroke_color=tint(hue, 0.35 + 0.65 * ((j + 1) / n_seg) ** 2),  # noqa: F405
                       stroke_width=4))
    for sc in ("s02", "s03"):
        ts = float(getattr(T, f"c{k:02d}_{sc}"))
        xt = xa + w * (ts - st[i]) / durs[i]
        g.add(Line(P3(xt, y - 0.06), P3(xt, y + 0.06), stroke_color=hue if xt <= xf else C.muted,  # noqa: F405
                   stroke_width=1.5))
    g.add(Circle(radius=0.085, stroke_color=hue, stroke_width=1.5).move_to(P3(xf, y)),  # noqa: F405
          Dot(P3(xf, y), radius=0.04, color=C.light))  # noqa: F405
    return g


def add_rail(s, k, opacity=1.0, z=60, busy=False):
    """Add chapter k's progress rail to scene `s` as a screen-locked (parallax 0) layer, live for the whole scene.
    `busy=True` lays an invisible shade under it, for scenes where a full-bleed picture runs behind the rail."""
    if busy:
        shade(s, (X0 + RAIL_X1) / 2, RAIL_Y + 0.12, RAIL_X1 - X0 + 0.3, 0.55, a=0.75, z=z - 1, parallax=0.0,
              opacity=opacity)
    hud = s.manim(z=z, parallax=0.0, opacity=opacity)
    hud.add(rail_static(k))
    hud.redraw(lambda t: rail_live(k, t), during=(s.start, s.end))
    return hud


# ---------------------------------------------------------------------------------------------------- chapter card
def chapter_card(s, k, at, out, z=70):
    """The chapter card on black: portrait (duotoned, feathered; if public domain) beside the title in small caps,
    a rule in the hue, and the name and year. Fades in landing on `at`, out landing on `out`. Screen-locked."""
    from pathlib import Path

    from PIL import Image
    hue = getattr(C, CHAPTERS[k - 1])  # noqa: F405
    op = fade(at, out=out, dur=0.5)  # noqa: F405
    title = caps(CH_TITLES[k - 1].replace("--", "–").title().replace("'S", "'s"), 48, C.text)
    rule = Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=hue, stroke_width=3)  # noqa: F405
    who = caps(CH_NAMES[k - 1], 24, C.muted)  # noqa: F405
    card = VGroup(title, rule, who).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # noqa: F405
    portrait = CH_PORTRAITS[k - 1]
    if portrait:
        img = np.asarray(Image.open(Path(__file__).parent / f"assets/images/portraits/{portrait}.png"))
        ph = 2.4
        pw, gap = ph * img.shape[1] / img.shape[0], 0.35
        left = -(pw + gap + card.width) / 2                    # portrait + text, centred as one group
        s.add(ArrayLayer(img, height=ph, pos=(left + pw / 2, 0.15), z=z, parallax=0.0, opacity=op))  # noqa: F405
        card.move_to(P3(left + pw + gap, 0.15), aligned_edge=LEFT)
    else:
        card.move_to(P3(0, 0.15))
    s.manim(z=z + 1, parallax=0.0, opacity=op).add(card)
    backdrop(s, k, opacity=fade(float(out) + 0.2, dur=1.6))  # noqa: F405   the chapter's backdrop comes up
    return card


# ---------------------------------------------------------------------------------------------------- glimpses
GLIMPSE_H = 2.5                              # portrait height in the corner (world units; the frame is 8 tall)
_IMG = {}


def _load_lin(name):
    """An image as (linear RGB float32, alpha float32), rows top-first, cached. `name` is a portrait key
    (assets/images/portraits/<key>.png, already duotoned and feathered) or 'photo:<file>' (assets/images/photos/src,
    feathered here: the natural colours kept, the edges falling to black)."""
    from pathlib import Path

    from PIL import Image
    if name in _IMG:
        return _IMG[name]
    root = Path(__file__).parent / "assets/images"
    if name.startswith("photo:"):
        im = Image.open(root / "photos/src" / name[6:]).convert("RGB")
        if im.height > 900:
            im = im.resize((round(im.width * 900 / im.height), 900), Image.LANCZOS)
        rgb = np.asarray(im, np.float32) / 255
        h, w = rgb.shape[:2]
        ramp = lambda n, f: np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / (f * n), 0, 1)
        a = np.outer(ramp(h, 0.12), ramp(w, 0.12 * h / w))
        a = a * a * (3 - 2 * a)
    else:
        im = np.asarray(Image.open(root / f"portraits/{name}.png").convert("RGBA"), np.float32) / 255
        rgb, a = im[..., :3], im[..., 3]
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4).astype(np.float32)
    _IMG[name] = (lin, a.astype(np.float32))
    return _IMG[name]


def _to_rgba8(lin, a):
    srgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.maximum(lin, 0) ** (1 / 2.4) - 0.055)
    out = np.empty(a.shape + (4,), np.uint8)
    out[..., :3] = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return out


def glimpse(s, keys, at, hue, dur=3.8, h=GLIMPSE_H, at_xy=None, z=66):
    """A few seconds' glimpse of who (or what) the scene is about, in place of a text name tag: the image(s) rise
    into the top-left corner (or centred on `at_xy`), one slow band of light sweeps across them, a short rule in the
    hue draws under them, and they fade after `dur` seconds. No text, no frame. `keys`: portrait keys or
    'photo:<file>' (see _load_lin), side by side.

    Example:
        glimpse(s, "maxwell", T.c01_s02_maxwell, C.maxwell)
        glimpse(s, ["navier", "stokes"], T.c04_s01_navier, C.navier)
    """
    keys = [keys] if isinstance(keys, str) else list(keys)
    at = float(at)
    t1 = min(at + dur, float(s.end) - 0.7)                   # never past the scene's end
    gap = 0.12
    ws = [h * _load_lin(k)[0].shape[1] / _load_lin(k)[0].shape[0] for k in keys]
    W = sum(ws) + gap * (len(keys) - 1)
    if at_xy is None:
        x0, yc = X0, Y1 - h / 2
    else:
        x0, yc = at_xy[0] - W / 2, at_xy[1]
    rise = lambda t: 1 - float(smooth01(min(max((t - at + 0.15) / 0.8, 0.0), 1.0)))  # noqa: F405
    op = fade(at - 0.15, dur=0.55, out=t1, out_dur=0.6)  # noqa: F405
    push = lambda t: 1.0 + 0.045 * min(max((t - at) / (dur + 0.6), 0.0), 1.0)
    x = x0
    for k, w in zip(keys, ws):
        lin, a = _load_lin(k)
        H_, W_ = a.shape
        yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
        u = (0.75 * xx / W_ + 0.25 * yy / H_).astype(np.float32)

        def frame(t, lin=lin, a=a, u=u):
            p = -0.3 + 1.6 * min(max((t - at - 0.2) / 1.6, 0.0), 1.0)
            band = np.exp(-((u - p) / 0.09) ** 2)
            return _to_rgba8(lin * (1 + 0.8 * band[..., None]), a)

        cx = x + w / 2
        s.add(FramesLayer(frame, height=h, z=z, parallax=0.0,  # noqa: F405
                          pos=Track(lambda t, cx=cx: (cx, yc - 0.3 * rise(t))),  # noqa: F405
                          scale=Track(push), opacity=op, start=at - 0.2, end=min(t1 + 0.7, float(s.end))))  # noqa: F405
        x += w + gap

    def rule(t):
        u = float(smooth01(min(max((t - at - 0.25) / 0.7, 0.0), 1.0)))  # noqa: F405
        a = float(op(t))
        if u <= 0 or a < 0.01:
            return VGroup()  # noqa: F405
        y = yc - h / 2 - 0.12 - 0.3 * rise(t)
        return Line(P3(x0, y), P3(x0 + 0.7 * u, y), stroke_color=hue, stroke_width=3,  # noqa: F405
                    stroke_opacity=a)
    s.manim(z=z + 0.5, parallax=0.0).redraw(rule, during=(at - 0.2, min(t1 + 0.7, float(s.end))))


# ---------------------------------------------------------------------------------------------------- backdrops
BACKDROP_LEVEL = 0.03                        # peak line brightness, linear light (about 19 % sRGB grey at most)


def chapter_backdrop(s, k, last=False):
    """The backdrop in a chapter's second or third scene: steady (it is pure in time, so it runs on across the cut);
    the chapter's last scene fades it out over its final second, before the next chapter's card."""
    out = float(s.end) - 1.0 if last else float(s.end) + 10.0
    return backdrop(s, k, opacity=fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.9))  # noqa: F405


def backdrop(s, k, opacity=1.0, level=BACKDROP_LEVEL, z=-150):
    """Chapter k's full-frame backdrop (shaders/backdrop.frag): a faint, moving motif of its physics in its hue,
    edge to edge, darker in the middle of the frame. Sits just above the black solid, so full-bleed pictures cover it.

    Example:
        backdrop(s, 1, opacity=fade(T.c01_s01 + 2.0, dur=1.5))
    """
    hue = getattr(C, CHAPTERS[k - 1])  # noqa: F405
    op = opacity if callable(opacity) else (lambda t, o=float(opacity): o)
    return s.shader("backdrop.frag", z=z, parallax=0.0, animated=True, scale_res=0.5, u_mode=float(k),
                    u_hue=tuple(map(float, lin_rgb(hue))), u_level=float(level),
                    u_opacity=Track(lambda t: float(op(t))))  # noqa: F405
