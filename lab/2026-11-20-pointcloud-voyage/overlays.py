"""Point-cloud panels floating in the evening air: the year, Dido, the king, the joke and the ox hide.

Each panel is a set of kind-7 points in its own units (height 1, centred), with the pixel colour, a random scatter
direction (nrm) for the assemble and disperse, and a per-point stagger (p2). PANELS gives where (screen NDC and
depth in view space) and when; render.py turns that into per-frame uniforms. Beats are 012's.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "videos/012-lagrange-multipliers/assets/photos/cards"
LM = Path.home() / ".pytinytex/.TinyTeX/texmf-dist/fonts/opentype/public/lm"
QUEEN, KING, JOKE, HIDE, STRIPS = 4.68, 9.50, 12.27, 15.90, 18.60

# id: (kind, source, sx, sy, depth, height as a fraction of the frame, t_in, t_out, yaw)
PANELS = [
    ("text", ("caps", "814 bc", "#ffd9a8"), -0.72, 0.82, 10.0, 0.07, 0.9, 4.2, 0.10),
    ("figure", "queen", -0.72, 0.56, 10.0, 0.26, QUEEN + 0.1, STRIPS - 0.3, 0.14),
    ("text", ("caps", "dido", "#ffe9c9"), -0.72, 0.27, 10.0, 0.034, QUEEN + 0.5, STRIPS - 0.3, 0.14),
    ("figure", "king", -0.24, 0.56, 10.0, 0.26, KING + 0.4, STRIPS - 0.3, 0.06),
    ("text", ("caps", "the king", "#ffe9c9"), -0.24, 0.27, 10.0, 0.034, KING + 0.8, STRIPS - 0.3, 0.06),
    ("text", ("italic", "as much ground as she could surround", "#ffe9c9"), 0.36, 0.88, 10.0, 0.05, JOKE + 1.65, STRIPS - 0.3, -0.05),
    ("figure", "hide", 0.62, 0.56, 10.0, 0.26, HIDE + 0.2, STRIPS - 0.3, -0.12),
    ("text", ("caps", "one ox hide", "#ffe9c9"), 0.62, 0.27, 10.0, 0.034, HIDE + 0.6, STRIPS - 0.3, -0.12),
]


def _lin(a):
    return (np.asarray(a, float) / 255.0) ** 2.2


def _hex(h):
    h = h.lstrip("#")
    return _lin([int(h[i:i + 2], 16) for i in (0, 2, 4)])


def image_points(key, rows=260, r=None):
    im = Image.open(CARDS / f"{key}.jpg").convert("RGB")
    a = im.width / im.height
    cols = int(rows * a)
    px = np.asarray(im.resize((cols, rows), Image.LANCZOS), float)
    yy, xx = np.mgrid[0:rows, 0:cols]
    u = (xx + r.uniform(-0.45, 0.45, xx.shape)) / rows - a / 2
    v = 0.5 - (yy + r.uniform(-0.45, 0.45, yy.shape)) / rows
    col = _lin(px.reshape(-1, 3)) * 1.15 + 0.012
    P = np.column_stack([u.ravel(), v.ravel(), r.normal(0, 0.004, u.size)])
    area = np.full(len(P), 1.0 / rows**2)
    # a thin gold frame, a little outside the picture
    m = 5000
    s = r.uniform(0, 1, m)
    side = r.integers(0, 4, m)
    pad = 0.035
    W2, H2 = a / 2 + pad, 0.5 + pad
    fx = np.where(side < 2, -W2 + 2 * W2 * s, np.where(side == 2, -W2, W2))
    fy = np.where(side == 0, -H2, np.where(side == 1, H2, -H2 + 2 * H2 * s))
    F = np.column_stack([fx, fy, np.zeros(m)]) + r.normal(0, 0.003, (m, 3)) * [1, 1, 0]
    P = np.vstack([P, F])
    col = np.vstack([col, np.tile(_hex("#ffc24a") * 1.6, (m, 1))])
    area = np.concatenate([area, np.full(m, 4 * (W2 + H2) * 0.006 / m)])
    return P, col, area


def figure_points(key, rows=300, r=None):
    """A drawn bust (figures.py) sampled into points; transparent pixels are dropped."""
    import figures
    im = getattr(figures, key)().resize((rows, rows), Image.LANCZOS)
    px = np.asarray(im, float)
    yy, xx = np.nonzero(px[..., 3] > 90)
    rgb = px[yy, xx, :3] * (255.0 / np.maximum(px[yy, xx, 3:4], 1.0))
    u = (xx + r.uniform(-0.45, 0.45, len(xx))) / rows - 0.5
    v = 0.5 - (yy + r.uniform(-0.45, 0.45, len(yy))) / rows
    P = np.column_stack([u, v, r.normal(0, 0.004, len(u))])
    return P, _lin(np.clip(rgb, 0, 255)) * 1.1 + 0.01, np.full(len(P), 1.0 / rows**2)


def text_points(style, text, color, r=None):
    font = {"caps": "lmromancaps10-regular.otf", "italic": "lmroman10-italic.otf"}[style]
    f = ImageFont.truetype(str(LM / font), 150)
    if style == "caps":
        text = " ".join(text)                      # open letterspacing, like the intro's tracked caps
    x0, y0, x1, y1 = f.getbbox(text)
    im = Image.new("L", (x1 - x0 + 20, y1 - y0 + 20), 0)
    ImageDraw.Draw(im).text((10 - x0, 10 - y0), text, font=f, fill=255)
    m = np.asarray(im, float) / 255.0
    H = m.shape[0]
    yy, xx = np.nonzero(m > 0.35)
    keep = r.uniform(0, 1, len(xx)) < 0.9
    yy, xx = yy[keep], xx[keep]
    u = (xx + r.uniform(-0.5, 0.5, len(xx))) / H - m.shape[1] / H / 2
    v = 0.5 - (yy + r.uniform(-0.5, 0.5, len(yy))) / H
    P = np.column_stack([u, v, np.zeros(len(u))])
    col = np.tile(_hex(color) * 1.5, (len(P), 1))
    return P, col, np.full(len(P), 1.0 / H**2 / 0.9)


def build(rows_fn):
    r = np.random.default_rng(77)
    out = []
    for i, (kind, src, *_rest) in enumerate(PANELS):
        P, col, area = (image_points(src, r=r) if kind == "image" else
                        figure_points(src, r=r) if kind == "figure" else text_points(*src, r=r))
        d = r.normal(0, 1, (len(P), 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        out.append(rows_fn(P, d, col, 7, area, i, r.uniform(0, 1, len(P))))
    return np.concatenate(out)
