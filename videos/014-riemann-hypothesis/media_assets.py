"""Downloaded images for the intro (assets/web/, fetched 2026-11-22 with the user's OK). Sources and licenses:

  anthropic_logo.svg     Wikimedia Commons "Anthropic logo.svg", public domain (text logo)
  claude_symbol.svg      Wikimedia Commons "Claude AI symbol.svg", CC0
  alpoge_2024_mfo.jpg    Wikimedia Commons "Levent Alpöge 2024 MFO.jpg", photo Marlene Ruf (MFO), CC BY-SA 2.0 de
                         -> credited in the video description (credits.md)
  riemann_1859.pdf       Wikimedia Commons, Monatsberichte der Berliner Akademie, Nov 1859, public domain
  riemann_portrait.jpeg  Wikimedia Commons "Georg Friedrich Bernhard Riemann.jpeg", public domain
  clay_logo.svg          Wikimedia Commons "Clay Mathematics Institute CMI Logo.svg", public domain
  alpoge_remark.pdf      alpo.ge/remark.pdf, L. Alpoge's four-page note (20 Nov 2026); author's copyright. Shown only as
                         small, unreadable page thumbnails (a preview), with one sentence highlighted

Each loader returns an RGBA uint8 array for ArrayLayer, or a Manim mobject for the SVGs."""
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
WEB = HERE / "assets" / "web"
RENDER = HERE / "assets" / "web_render"

NOTE_CLAIM = ((144, 93, 465, 104), (129, 104, 179, 115))   # "I believe I have, working with Claude, discovered a
                                                           # proof of the Riemann Hypothesis." on page 1 at 70 dpi


def _rgba(im):
    return np.asarray(im.convert("RGBA"), dtype=np.uint8).copy()


def _round(a, r):
    """Round the corners of an RGBA array (radius r px), anti-aliased."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    cx = np.clip(xx, r, w - r)
    cy = np.clip(yy, r, h - r)
    d = np.hypot(xx - cx, yy - cy)
    m = np.clip(r - d + 0.5, 0.0, 1.0)
    a = a.copy()
    a[..., 3] = (a[..., 3] * m).astype(np.uint8)
    return a


@lru_cache(None)
def alpoge():
    """Head and shoulders, cropped from the 400x267 MFO photo (165x232 px)."""
    im = Image.open(WEB / "alpoge_2024_mfo.jpg").crop((180, 35, 345, 267))
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    return _round(_rgba(im), 18)


@lru_cache(None)
def riemann():
    """The public-domain engraving, cropped to head and shoulders."""
    im = Image.open(WEB / "riemann_portrait.jpeg").convert("L").crop((70, 40, 840, 986))
    return _round(_rgba(im), 24)


@lru_cache(None)
def paper_1859(page=1):
    """Page `page` of the 1859 Monatsberichte reprint, rendered at 150 dpi."""
    png = RENDER / f"r1859-{page}.png"
    if not png.exists():
        RENDER.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", "150", "-f", str(page), "-l", str(page), "-png",
                        str(WEB / "riemann_1859.pdf"), str(RENDER / "r1859")], check=True)
    return _round(_rgba(Image.open(png)), 10)


@lru_cache(None)
def note_page(page, angle=0.0, highlight=None):
    """Page `page` (1-4) of the note as a 70 dpi thumbnail (595x770), rotated by `angle` degrees. `highlight`, an
    (r, g, b) in 0..1, marks the claim sentence on page 1 like a highlighter. Returns (rgba, height_factor): the
    rotated image grows, so scale ArrayLayer heights by height_factor."""
    png = RENDER / f"note-{page}.png"
    if not png.exists():
        RENDER.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", "70", "-png", str(WEB / "alpoge_remark.pdf"), str(RENDER / "note")], check=True)
    im = Image.open(png).convert("RGBA")
    h0 = im.height
    if highlight is not None:
        a = np.asarray(im).astype(float)
        col = np.array(highlight, float) * 255
        for x0, y0, x1, y1 in NOTE_CLAIM:
            reg = a[y0:y1, x0:x1, :3]
            a[y0:y1, x0:x1, :3] = reg * (0.45 + 0.55 * col / 255)          # multiply: ink stays dark, paper turns amber
        im = Image.fromarray(a.astype(np.uint8), "RGBA")
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    return _rgba(im), im.height / h0


def aspect(a):
    """Width / height of an RGBA array."""
    return a.shape[1] / a.shape[0]


def svg_logo(name, height, color=None):
    """An SVG logo as a Manim mobject of the given height; `color` recolors every part (None keeps the file's fill)."""
    from manim import SVGMobject
    m = SVGMobject(str(WEB / name), height=height)
    if color is not None:
        m.set_fill(color, opacity=1.0).set_stroke(width=0)
    return m


# ───────────────────────────────────────────────────────────────── portraits (assets/web/people, LICENSES.txt)
PEOPLE = WEB / "people"
# file, face centre (x, y as fractions), crop width (fraction of image width). Every crop is 4:5.
CROPS = {
    "euclid": ("euclid.jpg", 0.45, 0.24, 0.80),
    "eratosthenes": ("eratosthenes.png", 0.50, 0.48, 0.72),
    "gauss": ("gauss.jpg", 0.50, 0.30, 0.72),
    "hadamard": ("hadamard.jpg", 0.50, 0.50, 1.00),
    "dlvp": ("dlvp.jpg", 0.50, 0.42, 0.85),
    "euler": ("euler.png", 0.50, 0.42, 0.95),
    "hilbert": ("hilbert.jpg", 0.50, 0.46, 0.95),
    "hardy": ("hardy.jpg", 0.47, 0.30, 0.55),
    "turing": ("turing.jpg", 0.50, 0.42, 0.90),
    "vonkoch": ("vonkoch.jpg", 0.50, 0.42, 0.95),
    "littlewood": ("littlewood.png", 0.50, 0.50, 0.74),
    "lehmer": ("lehmer.jpg", 0.50, 0.42, 0.85),
    "weil": ("weil.jpg", 0.24, 0.17, 0.38),
    "deligne": ("deligne.jpg", 0.45, 0.42, 0.90),
    "montgomery": ("montgomery.jpg", 0.50, 0.42, 0.46),
    "dyson": ("dyson.jpg", 0.55, 0.36, 0.80),
    "buzzard": ("buzzard.jpg", 0.46, 0.30, 0.86),
    "sutherland": ("sutherland.jpg", 0.53, 0.33, 0.44),
    "alpoge": ("../alpoge_2024_mfo.jpg", 0.66, 0.42, 0.42),
    "riemann": ("../riemann_portrait.jpeg", 0.50, 0.42, 0.86),
}


@lru_cache(None)
def portrait(key, gray=True):
    """A 4:5 head-and-shoulders crop with rounded corners, grayscale by default so every face shares one look.
    Example: ArrayLayer(portrait("euler"), height=2.4, pos=(4, 1))"""
    f, cx, cy, wf = CROPS[key]
    im = Image.open(PEOPLE / f).convert("RGB")
    W, H = im.size
    w = wf * W
    h = 1.25 * w
    if h > H:
        h, w = H, H / 1.25
    x0 = min(max(cx * W - w / 2, 0), W - w)
    y0 = min(max(cy * H - h / 2, 0), H - h)
    im = im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h)))
    if gray:
        im = im.convert("L")
    tw = max(480, im.width)
    im = im.resize((tw, int(tw * 1.25)), Image.LANCZOS)
    return _round(_rgba(im), int(tw * 0.04))


@lru_cache(None)
def papyrus():
    """P. Oxy. I 29, the oldest surviving fragment of Euclid's Elements (public domain)."""
    return _round(_rgba(Image.open(PEOPLE / "papyrus_euclid.jpg")), 14)


def portrait_card(s, h, key, name, at, out, pos, height=2.3, z=5, name_size=28, color=None, side="below"):
    """Show a portrait at `pos` (centre) from `at` to `out`, with a thin outline and its name in small caps (`side`
    "below", "right" or "left"; name=None for none). `h` is a Manim layer for the outline and name. Returns the
    VGroup (outline, name) already scored.
    Example: portrait_card(s, h, "euler", r"L. Euler $\\cdot$ 1734", T.e_euler, T.e_out, (4.6, 0.8))"""
    from aion import ArrayLayer, FadeIn, FadeOut, RoundedRectangle, VGroup, keys, C, UP, DOWN, LEFT, RIGHT
    from look import caps
    w = height / 1.25
    op = keys((at - 0.15, 0.0), (at + 0.45, 1.0), (out - 0.45, 1.0), (out, 0.0), lead=0)
    s.add(ArrayLayer(portrait(key), height=height, pos=pos, z=z, parallax=0.0, opacity=op))
    frame = portrait_frame(pos, height)
    g = VGroup(frame)
    anims = [FadeIn(frame)]
    if name:
        nm = caps(name, name_size, color or C.ink)
        if side == "below":
            nm.next_to(frame, DOWN, buff=0.18)
        else:
            nm.next_to(frame, RIGHT if side == "right" else LEFT, buff=0.25).align_to(frame, DOWN)
        g.add(nm)
        anims.append(FadeIn(nm, shift=0.05 * UP))
    h.play(*anims, at=at + 0.1, dur=0.5, lead=0)
    h.play(FadeOut(g), at=out - 0.45, dur=0.45, lead=0)
    return g


def portrait_frame(pos, height):
    """The thin outline that portrait_card draws around a portrait."""
    from aion import RoundedRectangle, C
    w = height / 1.25
    return RoundedRectangle(width=w, height=height, corner_radius=w * 0.04, stroke_color=C.muted, stroke_width=1.2,
                            stroke_opacity=0.8, fill_opacity=0.0).move_to([pos[0], pos[1], 0])


def euler_pos(res):
    """Where Euler's portrait sits in s07/s08: right of the "L. Euler 1734" caption, raised."""
    return (5.85, -0.95)


@lru_cache(None)
def paper_page_thumb(page, dpi=60):
    """Page `page` (1-9) of Riemann's 1859 paper as a small thumbnail (rounded corners)."""
    png = RENDER / f"r1859t-{page}.png"
    if not png.exists():
        RENDER.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile",
                        str(WEB / "riemann_1859.pdf"), str(RENDER / f"r1859t-{page}")], check=True)
    return _round(_rgba(Image.open(png)), 6)
