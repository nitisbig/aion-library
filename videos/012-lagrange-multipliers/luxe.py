"""The finish shared by Chapter 2 onward: painted backgrounds, the framed stage, chapter lockups, cased arrows and tracked captions."""
from functools import lru_cache

import skia

from aion import *
import shots as _s
from atlas import atlas_rgba, ramp, trail_art
from cards import tracked, twisted
from coast import _col, _mix
from draw3d import rgb
from shots import BOX, SHORE, poly
from story import top_beach_image
from voyage import paint

W, H = 1920, 1080
EDGE = 960 + 135 * BOX[2]
NUMBER = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


@lru_cache(maxsize=1)
def study_rgba():
    """A deep evening ground with faint stars and a navigator's graticule."""
    sf = skia.Surface(W, H)
    cv = sf.getCanvas()
    sky = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [_col(_mix(C.indigo, C.plum, 0.25)), _col(_mix(C.indigo, C.bg, 0.72))], [0.0, 1.0])
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sky))
    warm = skia.GradientShader.MakeRadial(skia.Point(520, 1080), 900, [_col(C.tyrian, 0.3), _col(C.tyrian, 0.0)], [0.0, 1.0])
    cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=warm))
    for x in range(0, W, 90):
        cv.drawLine(x, 0, x, H, paint(_col(C.gold, 0.045), 1))
    for y in range(0, H, 90):
        cv.drawLine(0, y, W, y, paint(_col(C.gold, 0.045), 1))
    r = rng(31)
    for x, y, a in zip(r.uniform(0, W, 170), r.uniform(0, H, 170), r.uniform(0.12, 0.6, 170)):
        cv.drawCircle(x, y, float(r.uniform(0.8, 1.9)), paint(_col(C.foam, float(a))))
    return sf.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()


def study(s):
    """The painted ground behind every scene that is not on the map or the beach."""
    _s.backdrop(s)
    s.add(ArrayLayer(study_rgba(), height=8.0, z=-100, parallax=0.0))


@lru_cache(maxsize=1)
def panel_rgba():
    """The equation panel on the right and a gold map frame around the picture on the left."""
    rgba = np.zeros((H, W, 4), np.uint8)
    x = int(EDGE)
    v = (np.arange(H) / H)[:, None, None]
    col = rgb(C.indigo) * (0.5 - 0.42 * v) + rgb(C.bg) * (0.5 + 0.42 * v)
    rgba[:, x:, :3] = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    rgba[:, x:, 3] = 255
    sf = skia.Surface(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    cv = sf.getCanvas()
    m = 16
    cv.drawRect(skia.Rect(m, m, EDGE - m, H - m), paint(_col(C.gold), 2.4))
    cv.drawRect(skia.Rect(m + 8, m + 8, EDGE - m - 8, H - m - 8), paint(_col(C.gold, 0.5), 1))
    for px in np.arange(m + 60, EDGE - m, 60):
        cv.drawLine(px, m, px, m + 8, paint(_col(C.gold), 1.6))
        cv.drawLine(px, H - m - 8, px, H - m, paint(_col(C.gold), 1.6))
    for py in np.arange(m + 60, H - m, 60):
        cv.drawLine(m, py, m + 8, py, paint(_col(C.gold), 1.6))
        cv.drawLine(EDGE - m - 8, py, EDGE - m, py, paint(_col(C.gold), 1.6))
    cv.drawLine(EDGE, 0, EDGE, H, paint(_col(C.gold), 3))
    sf.flushAndSubmit()
    return rgba


def side_panel(s, z=4):
    """Screen-locked equation panel, so it holds still while the picture moves."""
    s.add(ArrayLayer(panel_rgba(), height=8.0, z=z, parallax=0.0))


def stage(s, contours=True, with_trail=True):
    """The relief map every map scene shares, with the trail already drawn."""
    _s.backdrop(s)
    s.add(ArrayLayer(atlas_rgba(contours), height=8.0, z=-20))
    base = s.manim(z=0)
    if with_trail:
        base.add(trail_art())
    return base


def chapter(s, n, name, at, hold=4.2):
    """The chapter lockup from Chapter 1, on a dark plate in the top corner."""
    m = s.manim(z=30, parallax=0.0)
    num = tracked(f"chapter {NUMBER[n]}", 24, C.gold)
    title = Tex(r"\textit{" + name + "}", font_size=46, color=C.ink)
    rule = Line(ORIGIN, RIGHT * max(title.width, num.width), color=C.gold, stroke_width=3)
    body = VGroup(num, rule, title).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    plate = BackgroundRectangle(body, color=C.bg, fill_opacity=0.84, buff=0.2)
    lock = VGroup(plate, body).move_to([-6.82, 3.72, 0], aligned_edge=UL)
    m.play(FadeIn(plate), FadeIn(num, shift=0.08 * UP), Create(rule), at=at + 0.15, dur=0.8, ease=_s.E, lead=0)
    m.play(FadeIn(title, shift=0.1 * UP), at=at + 0.4, dur=0.8, ease=_s.E, lead=0)
    m.play(FadeOut(lock), at=at + hold, dur=0.6, ease=_s.E, lead=0)


def lab(text, size=28, color=None):
    """A caption in tracked small caps. Text with math or symbols falls back to italics."""
    size = max(24, size * 0.76)
    if "$" in text or "\\" in text:
        out = Tex(r"\textit{" + text + "}", font_size=size * 1.3, color=color or C.ink)
    else:
        out = tracked(text, size, color or C.ink)
    return out.scale_to_fit_width(5.7) if out.width > 5.7 else out


def arrow(a, b, color, width=None, tip=0.26, opacity=1.0):
    """An arrow with a dark casing, so it reads on the painted map."""
    w = width or C.stroke + 1
    top = _s.arrow(a, b, color, width=w, tip=tip, opacity=opacity)
    case = top.copy().set_stroke(C.bg, w + 4, opacity)
    case.tip.set_fill(C.bg, opacity).set_stroke(C.bg, 5, opacity)
    return VGroup(case, top)


def grow(a):
    """Animations that grow a cased arrow."""
    return [GrowArrow(a[0]), GrowArrow(a[1])]


def walker(p):
    """The walker: a yellow bead inside a thin ring."""
    q = _s.p3(p)
    return VGroup(Circle(radius=0.23, color=C.you, stroke_width=2.4).move_to(q), Dot(q, radius=0.15, color=C.bg), Dot(q, radius=0.105, color=C.you))


def rope(P, width=6, opacity=1.0):
    """Dido's rope, twisted, along a polyline."""
    return twisted(poly(P, C.con, width, opacity), width, max(24, int(np.linalg.norm(np.diff(np.asarray(P), axis=0), axis=1).sum() * 7)))


@lru_cache(maxsize=1)
def beach_rgba():
    """The painted shore seen from above."""
    return top_beach_image(float(SHORE)).toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType).copy()


def beach(s, z=-5, opacity=1.0):
    s.add(ArrayLayer(beach_rgba(), height=8.0, z=z, opacity=opacity))


def relief(fn, origin, unit, levels):
    """Filled height bands of fn over the left of the frame, as an RGBA picture."""
    xs = (np.arange(W) + 0.5) / 135 - 64 / 9
    ys = 4 - (np.arange(H) + 0.5) / 135
    X, Y = np.meshgrid(xs, ys)
    idx = np.digitize(fn((X - origin[0]) / unit, (Y - origin[1]) / unit), levels)
    col = ramp(idx / len(levels), [C.indigo, _mix(C.indigo, C.plum, 0.55), C.plum, _mix(C.plum, C.dusk, 0.5), _mix(C.dusk, C.obj, 0.45), C.obj])
    return (np.clip(np.dstack([col, np.ones((H, W))]), 0, 1) * 255).astype(np.uint8)
