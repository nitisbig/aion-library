"""Reference cards: small framed images that pop up on the word that names them, with a shared type lockup."""
from pathlib import Path

from aion import *

from shots import E, lab, sc

CARDS = Path(__file__).parent / "assets" / "photos" / "cards"


def tracked(text, size=40, color=None):
    """Small caps with open letterspacing, the title face of the intro."""
    spaced = r"\,".join("~" if ch == " " else ch for ch in text)
    return Tex(r"\textsc{" + spaced + "}", font_size=size, color=color or C.ink)


def card(key, title, sub=None, h=2.5, tilt=0.0, pos=ORIGIN, photo=True):
    """A framed image on a dark mat with a gold rule, a tracked title and an optional source line.

    With photo=False the picture is left out and its place kept, for a slow fade with photo_layer.
    """
    img = ImageMobject(str(CARDS / f"{key}.jpg")).set_height(h)
    if not photo:
        img = Rectangle(width=img.width, height=img.height, stroke_width=0, fill_opacity=0)
    name = tracked(title, 34, C.ink)
    w = img.width
    if name.width > w:
        name.scale_to_fit_width(w)
    rule = Line(LEFT * w / 2, RIGHT * w / 2, color=C.gold, stroke_width=3).next_to(img, DOWN, buff=0.14)
    name.next_to(rule, DOWN, buff=0.13)
    parts = [rule, name]
    if sub:
        sl = lab(sub, 22, C.muted)
        if sl.width > w:
            sl.scale_to_fit_width(w)
        parts.append(sl.next_to(name, DOWN, buff=0.09))
    body = Group(img, *parts)
    mat = Rectangle(width=body.width + 0.34, height=body.height + 0.34, fill_color=C.bg, fill_opacity=1, stroke_color=C.gold, stroke_width=2).move_to(body)
    shade = mat.copy().set_stroke(width=0).set_fill(C.bg, 0.42).shift(0.13 * RIGHT + 0.13 * DOWN)
    out = Group(shade, mat, body)
    out.rotate(tilt * DEGREES).move_to(pos)
    out.window = img
    return out


def photo_layer(key, c, at, dur=1.6, z=21):
    """The picture for a card made with photo=False, fading in cleanly as its own full-frame layer."""
    from PIL import Image

    box = c.window
    w, h = round(box.width * 135), round(box.height * 135)
    x, y = round(960 + 135 * box.get_center()[0] - w / 2), round(540 - 135 * box.get_center()[1] - h / 2)
    rgba = np.zeros((1080, 1920, 4), np.uint8)
    rgba[y:y + h, x:x + w, :3] = np.asarray(Image.open(CARDS / f"{key}.jpg").convert("RGB").resize((w, h), Image.LANCZOS))
    rgba[y:y + h, x:x + w, 3] = 255
    return ArrayLayer(rgba, height=8.0, z=z, opacity=fade(at, dur=dur))


def icon(name, h=0.62, color=None):
    """A gold line icon drawn for this video (assets/svg)."""
    g = SVGMobject(str(CARDS.parent.parent / "svg" / f"{name}.svg")).set_height(h)
    return g.set_fill(opacity=0).set_stroke(color or C.gold, 2.6, 1)


def twisted(path, w=7, dashes=46):
    """A twisted rope for small diagrams: a dark edge, a bright core and diagonal strands."""
    edge = path.copy().set_stroke(interpolate_color(ManimColor(C.con), ManimColor(C.bg), 0.62), w + 3.5)
    core = path.copy().set_stroke(C.con, w)
    strand = DashedVMobject(path.copy().set_stroke(interpolate_color(ManimColor(C.con), ManimColor(C.bg), 0.5), w * 0.75), num_dashes=dashes, dashed_ratio=0.3)
    return VGroup(edge, core, strand)


def pop(m, c, at, out=None, dur=0.75):
    """The card rises gently on its word and stays."""
    m.play(GrowFromCenter(c), at=at, dur=dur, ease=E, lead=0.05)
    if out is not None:
        m.play(ShrinkToCenter(c), at=out - 0.28, dur=0.28, ease=E, lead=0)
    return c


def panel(x, y, w, h, accent):
    """A dark panel with a colored top edge, used for the intro's small multiples."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.1, fill_color=interpolate_color(ManimColor(C.bg), ManimColor(accent), 0.09), fill_opacity=1, stroke_color=interpolate_color(ManimColor(C.bg), ManimColor(accent), 0.45), stroke_width=1.6).move_to([x, y, 0])
    edge = Line([x - w / 2 + 0.14, y + h / 2, 0], [x + w / 2 - 0.14, y + h / 2, 0], color=accent, stroke_width=5)
    return VGroup(box, edge)
