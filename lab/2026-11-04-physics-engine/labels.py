"""LaTeX labels and equations → one RGBA atlas (premultiplied sRGB), cached in out/labels_<hash>.npz.

MathTex typesets each label (TinyTeX via `import aion`), and its Bézier outlines are filled with skia,
so the glyphs are real Computer Modern and the terms are colour-coded exactly like the arrows.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# semantic colours (shared with timeline.py)
COL = dict(
    F="#FC6255", v="#58C4DD", a="#F4D35E", p="#83C167", K="#58C4DD", U="#B48CFF", Q="#FF9A4D",
    ball="#FFE7C2", text="#ECEFF4", muted="#9AA5B1", dark="#0B0D12",
)

# key → list of (tex part, colour key)
LABELS = {
    "F": [(r"\vec F", "F")],
    "-F": [(r"-\vec F", "F")],
    "v": [(r"\vec v", "v")],
    "a": [(r"\vec a", "a")],
    "p": [(r"\vec p", "p")],
    "N": [(r"\vec N", "F")],
    "drag": [(r"-b\vec v", "F")],
    "m": [("m", "dark")],
    "2m": [("2m", "dark")],
    "K": [("K", "K")], "U": [("U", "U")], "Q": [("Q", "Q")],
    # one small equation per act
    "eq1": [(r"\vec F", "F"), (r"= 0 \;\;\Rightarrow\;\;", "text"), (r"\vec v", "v"), (r"=\text{const}", "text")],
    "eq2": [(r"\vec F", "F"), ("=", "text"), ("m", "text"), (r"\vec a", "a")],
    "eq3": [(r"\vec F", "F"), ("=", "text"), ("m", "text"), (r"\vec g", "a")],
    "eq4": [(r"\vec F", "F"), (r"= -k\,\vec x", "text")],
    "eq5": [("K", "K"), ("+", "text"), ("U", "U"), ("+", "text"), ("Q", "Q"), (r"=\text{const}", "text")],
    "eq6": [(r"\textstyle\sum", "text"), (r"\vec p", "p"), (r"=\text{const}", "text")],
    "eq7": [(r"F", "F"), (r"= \dfrac{GMm}{r^2}", "text")],
    "eq8": [(r"|\delta(t)| \approx |\delta_0|\, e^{\lambda t}", "text")],
}
PX_PER_UNIT = 220            # raster scale (px per Manim unit); MathTex "F" ≈ 0.5 units tall
PAD = 8


def _key():
    h = hashlib.sha1(Path(__file__).read_bytes())
    return h.hexdigest()[:12]


def _raster(parts):
    import skia
    from manim import MathTex, ManimColor
    m = MathTex(*[p for p, _ in parts])
    for sub, (_, ck) in zip(m.submobjects, parts):
        sub.set_color(ManimColor(COL[ck]))
    x0, y0 = m.get_corner([-1, 1, 0])[:2]
    w = int(np.ceil(m.width * PX_PER_UNIT)) + 2 * PAD
    h = int(np.ceil(m.height * PX_PER_UNIT)) + 2 * PAD
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    for vm in m.family_members_with_points():
        col = vm.get_fill_color().to_hex()
        paint = skia.Paint(AntiAlias=True, Color=skia.Color(*[int(col[i:i + 2], 16) for i in (1, 3, 5)]))
        path = skia.Path()
        for sp in vm.get_subpaths():
            q = (sp[:, :2] - [x0, y0]) * [PX_PER_UNIT, -PX_PER_UNIT] + PAD
            path.moveTo(*q[0])
            for k in range(0, len(q) - 3, 4):
                path.cubicTo(*q[k + 1], *q[k + 2], *q[k + 3])
            path.close()
        cv.drawPath(path, paint)
    img = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)   # premultiplied RGBA
    return np.ascontiguousarray(img), (m.width, m.height)


def build():
    """Returns (atlas uint8 RGBA premultiplied, table: key → dict(uv0, uv1, w, h) in Manim units)."""
    OUT.mkdir(exist_ok=True)
    path = OUT / f"labels_{_key()}.npz"
    if path.exists():
        z = np.load(path)
        return z["atlas"], json.loads(str(z["table"]))
    import aion  # noqa: F401  (TinyTeX on PATH)
    imgs = {k: _raster(v) for k, v in LABELS.items()}
    W = 2048
    x = y = row_h = 0
    pos = {}
    for k, (im, _) in sorted(imgs.items(), key=lambda kv: -kv[1][0].shape[0]):
        h, w = im.shape[:2]
        if x + w > W:
            x, y, row_h = 0, y + row_h, 0
        pos[k] = (x, y); x += w; row_h = max(row_h, h)
    H = y + row_h
    atlas = np.zeros((H, W, 4), np.uint8)
    table = {}
    for k, (im, (mw, mh)) in imgs.items():
        px, py = pos[k]
        h, w = im.shape[:2]
        atlas[py:py + h, px:px + w] = im
        # uv with GL's bottom-up rows: the atlas is flipped on upload
        table[k] = dict(uv0=(px / W, 1 - (py + h) / H), uv1=((px + w) / W, 1 - py / H),
                        w=w / PX_PER_UNIT, h=h / PX_PER_UNIT)
    for old in OUT.glob("labels_*.npz"):
        old.unlink()
    np.savez_compressed(path, atlas=atlas, table=json.dumps(table))
    return atlas, table


if __name__ == "__main__":
    from PIL import Image
    a, t = build()
    Image.fromarray(a).save(OUT / "labels_atlas.png")
    print(a.shape, list(t))
