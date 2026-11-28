"""Chapter 7's shared pieces (s01, s25-s28, s30, s31): attribution and status chips, the Buzzard card (docked top right
s26-s28) and the wall of 175,187 Lean files (one tile per file, 419 per row; research.md A7)."""
from types import SimpleNamespace

from aion import *

from look import caps, lab, seen, tex

N_FILES, PER_ROW = 175_187, 419
TILE, GAP = 6, 1                               # pixels per tile and per gap in the wall image


def ring(done, color=None, r=0.11):
    """A check ring: filled with a tick when done, an open three-quarter ring while still running."""
    color = color or C.lean
    if done:
        c = Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=1.0)
        tick = VMobject(stroke_color=C.bg, stroke_width=2.6).set_points_as_corners(
            [[-0.5 * r, 0.0, 0], [-0.12 * r, -0.4 * r, 0], [0.55 * r, 0.42 * r, 0]])
        return VGroup(c, tick)
    return Arc(radius=r, start_angle=PI / 2, angle=1.5 * PI, stroke_color=color, stroke_width=2.4)


def chip(text, color, size=24, mark=None):
    """A key fact in a rounded outline of its actor's color; `mark` (a mobject) sits at the right."""
    t = text if isinstance(text, Mobject) else lab(text, size, C.text)
    dot = Dot(radius=0.06, color=color)
    row = VGroup(dot, t) if mark is None else VGroup(dot, t, mark)
    row.arrange(RIGHT, buff=0.18)
    box = RoundedRectangle(width=row.width + 0.36, height=max(row.height, 0.3) + 0.24, corner_radius=0.1,
                           stroke_color=color, stroke_width=1.6).move_to(row)
    g = VGroup(box, row)
    g.box, g.text = box, t
    return g


def buzzard_card(rows=1, robin=False):
    """K. Buzzard's first question about any Lean proof, docked top right. Parts .head .rows .box"""
    head = caps(r"K. Buzzard $\cdot$ Imperial", 26, C.ink)
    r1 = VGroup(tex("1", size=26, color=C.muted), lab("does the statement mean RH?", 22, C.text), ring(False))
    r1.arrange(RIGHT, buff=0.18)
    body = VGroup(head, r1)
    if robin:
        rb = VGroup(lab("+ Robin cross-check", 20, C.muted), ring(False, r=0.09)).arrange(RIGHT, buff=0.14)
        body.add(rb)
    body.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    box = RoundedRectangle(width=body.width + 0.4, height=body.height + 0.3, corner_radius=0.1,
                           stroke_color=C.human, stroke_width=1.4)
    box.move_to(body)
    g = VGroup(box, body)
    g.move_to([6.65 - g.width / 2, 3.55 - g.height / 2, 0])
    g.head, g.box = head, box
    return g


def wall_rgba(color=None, n=N_FILES, per=PER_ROW, px=None):
    """The wall image: n square tiles, `per` to a row, filled from the top-left. RGBA uint8, transparent gaps.
    `px` box-filters it down to that many pixels across (no moire when the tiles are smaller than a pixel)."""
    img = _wall(color, n, per)
    if px:
        from PIL import Image
        im = Image.fromarray(img, "RGBA").resize((px, round(px * img.shape[0] / img.shape[1])), Image.BOX)
        img = np.asarray(im)
    return img


def _wall(color, n, per):
    rows = -(-n // per)
    step = TILE + GAP
    img = np.zeros((rows * step + GAP, per * step + GAP, 4), np.uint8)
    rgb = np.array([int((color or C.lean).lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)
    full = n // per
    for r in range(rows):
        k = per if r < full else n - full * per
        y = GAP + r * step
        for c in range(k):
            x = GAP + c * step
            img[y:y + TILE, x:x + TILE, :3] = rgb
            img[y:y + TILE, x:x + TILE, 3] = 255
    return img


def wall_tile_xy(k, height):
    """World position (relative to the wall's centre) of tile k when the wall image is `height` units tall."""
    rows = -(-N_FILES // PER_ROW)
    step = TILE + GAP
    H = rows * step + GAP
    W = PER_ROW * step + GAP
    u = height / H
    r, c = divmod(k, PER_ROW)
    return np.array([(GAP + c * step + TILE / 2 - W / 2) * u, (H / 2 - GAP - r * step - TILE / 2) * u])
