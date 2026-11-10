"""Closed drawings for epicycle chains, as complex samples z(t), t = k/n.

    z = treble_clef(1000)        # one continuous line, centered (c₀ = 0), max |z| = 1

Glyph outlines come from installed fonts through fontTools, flattened to polylines.
Several contours (a glyph's outside and its holes) are joined into one loop by
`fourier.bridge`, which walks over to each hole and back along the same short line.
"""

from __future__ import annotations

from functools import lru_cache

from pathlib import Path

import numpy as np

from . import fourier as F

_SYS_NOTO = Path("/usr/share/fonts/truetype/noto/NotoMusic-Regular.ttf")
# SIL OFL; the system copy if present, else the one shipped in aion/assets/fonts (cloud renders)
NOTO_MUSIC = str(_SYS_NOTO if _SYS_NOTO.exists() else Path(__file__).parent / "assets" / "fonts" / "NotoMusic-Regular.ttf")
G_CLEF = 0x1D11E


def _flatten(ops, steps: int = 24) -> list[np.ndarray]:
    contours, cur = [], []
    for op, args in ops:
        if op == "moveTo":
            cur = [complex(*args[0])]
        elif op == "lineTo":
            cur.append(complex(*args[0]))
        elif op == "qCurveTo":                 # TrueType: implied on-curve points between offs
            pts = [complex(*a) if a is not None else None for a in args]
            offs, end = pts[:-1], pts[-1] if pts[-1] is not None else cur[0]
            ons = [cur[-1]] + [(a + b) / 2 for a, b in zip(offs, offs[1:])] + [end]
            for k, c in enumerate(offs):
                a, b = ons[k], ons[k + 1]
                for s in np.linspace(0, 1, steps)[1:]:
                    cur.append((1 - s) ** 2 * a + 2 * (1 - s) * s * c + s * s * b)
        elif op == "curveTo":
            a = cur[-1]
            c1, c2, b = (complex(*x) for x in args)
            for s in np.linspace(0, 1, steps)[1:]:
                cur.append((1 - s) ** 3 * a + 3 * (1 - s) ** 2 * s * c1 + 3 * (1 - s) * s * s * c2 + s ** 3 * b)
        elif op in ("closePath", "endPath"):
            contours.append(np.array(cur))
            cur = []
    return contours


def glyph_contours(font_path: str, codepoint: int) -> list[np.ndarray]:
    """Every contour of a glyph, in font units (y up)."""
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    pen = RecordingPen()
    font.getGlyphSet()[font.getBestCmap()[codepoint]].draw(pen)
    return _flatten(pen.value)


def normalized(z: np.ndarray) -> np.ndarray:
    """Centered on its balance point (c₀ = 0) and scaled so max |z| = 1."""
    z = F.centered(z)
    return z / np.abs(z).max()


@lru_cache(maxsize=4)
def treble_clef(n: int = 1000) -> np.ndarray:
    """The G clef from Noto Music as one bridged loop: n samples, even arc length."""
    path = F.bridge(glyph_contours(NOTO_MUSIC, G_CLEF))
    return normalized(F.resample(path, n))


# ── one-line drawings from an image (contours of blurred brightness, joined into one tour) ─
def _contours(g: np.ndarray, sigma: float, levels, min_len: float) -> list[np.ndarray]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy import ndimage
    fig = plt.figure()
    cs = fig.add_subplot().contour(ndimage.gaussian_filter(g, sigma), levels=list(levels))
    plt.close(fig)
    out = []
    for lv in cs.allsegs:
        for p in lv:
            if len(p) > 2 and np.sum(np.hypot(*np.diff(p, axis=0).T)) > min_len:
                out.append(p[:, 0] - 1j * p[:, 1])          # image y points down
    return out


def tour(contours: list[np.ndarray]) -> np.ndarray:
    """Join contours into one line: greedy nearest neighbour; a closed contour is entered at
    its nearest point and traced all the way round, an open one from its nearer end."""
    left = list(contours)
    start = max(range(len(left)), key=lambda i: left[i].imag.max())      # the topmost contour first
    path = [left.pop(start)]
    while left:
        here = path[-1][-1]
        best = None
        for i, c in enumerate(left):
            closed = abs(c[0] - c[-1]) < 2.0
            if closed:
                j = int(np.argmin(np.abs(c - here)))
                d = abs(c[j] - here)
            else:
                j = 0 if abs(c[0] - here) <= abs(c[-1] - here) else -1
                d = abs(c[j] - here)
            if best is None or d < best[0]:
                best = (d, i, j, closed)
        _, i, j, closed = best
        c = left.pop(i)
        c = np.roll(c, -j) if closed else (c if j == 0 else c[::-1])
        path.append(np.append(c, c[0]) if closed else c)
    return np.concatenate(path)


def portrait_line(src: str, crop=(70, 80, 900, 1110), width: int = 420, split: float = 0.47,
                  head=(1.8, (0.3, 0.5, 0.68), 25.0), body=(3.5, (0.3, 0.6), 40.0)) -> np.ndarray:
    """A portrait as one continuous line (complex points, centered, max |z| = 1).

    Above `split` (fraction of the height) the detailed contour set (face, hair); below it a
    sparser one (clothes), so the face reads and the coat stays calm. Each set is
    (gaussian sigma px, brightness levels, min contour length px).

    After a call, `portrait_line.frame` holds the pixel → drawing map (center_px, scale_px, size_px,
    crop), so the source image can be laid exactly under the line: z = (x − i·y − center_px) / scale_px."""
    from PIL import Image
    im = Image.open(src).convert("L").crop(crop)
    im = im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)
    g = np.asarray(im, float) / 255
    H = g.shape[0]
    hc = [c for c in _contours(g, *head) if -c.imag.mean() < split * H]
    bc = [c for c in _contours(g, *body) if -c.imag.mean() >= split * H]
    z = tour(hc + bc)
    c0 = 0.5 * complex(z.real.max() + z.real.min(), z.imag.max() + z.imag.min())
    m = np.abs(z - c0).max()
    portrait_line.frame = {"center_px": c0, "scale_px": m, "size_px": (g.shape[1], g.shape[0]), "crop": crop}
    return (z - c0) / m
