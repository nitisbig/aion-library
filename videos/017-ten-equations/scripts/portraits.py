"""Chapter-card portraits for video 017: crop, level, duotone in the chapter hue, feather into black.

Reads the public-domain originals in assets/images/portraits/src/ (see CREDITS.md there) and writes
assets/images/portraits/<key>.png: 640 x 800 RGBA (4:5, about the card's 600 px height at 4K), straight alpha,
ready for ArrayLayer. Deterministic: same sources, same output.

Every portrait stays positive. Three background treatments:
  dark    dark-background photos: the soft superellipse vignette only.
  studio  light grey studio photos: a tight crop so the face fills the card, and a radial darkening of the tones
          around the face before tone mapping, so the grey wall falls to black (skin and wall share a tone, so a
          cutout would bite into the face).
  paper   engravings on white paper: the paper is grown from the top and side edges over smooth near-white pixels
          and cut away; the engraved subject keeps its tones and falls to black.

    uv run python videos/017-ten-equations/scripts/portraits.py            # all
    uv run python videos/017-ten-equations/scripts/portraits.py maxwell    # one
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

VIDEO = Path(__file__).resolve().parents[1]
SRC = VIDEO / "assets/images/portraits/src"
OUT = VIDEO / "assets/images/portraits"
sys.path.insert(0, str(VIDEO))
from theme import theme as C  # noqa: E402

OW, OH = 640, 800

# key: (source, chapter hue, face centre x, crop centre y, crop height (fractions of the source), background)
PORTRAITS = {
    "maxwell":       ("maxwell.jpg",       "maxwell",  0.49, 0.47, 0.86, "dark"),
    "einstein_1921": ("einstein_1921.jpg", "einstein", 0.56, 0.36, 0.44, "dark"),
    "schrodinger":   ("schrodinger.jpg",   "schrod",   0.50, 0.47, 0.76, "studio"),
    "stokes":        ("stokes.jpg",        "navier",   0.49, 0.37, 0.62, "dark"),
    "fourier":       ("fourier.jpg",       "fourier",  0.50, 0.38, 0.62, "paper"),
    "einstein_1905": ("einstein_1905.jpg", "dilation", 0.50, 0.44, 0.64, "studio"),
    "cauchy":        ("cauchy.jpg",        "descent",  0.51, 0.27, 0.40, "paper"),
    "shannon":       ("shannon.jpg",       "shannon",  0.50, 0.37, 0.64, "studio"),
    "newton":        ("newton.jpg",        "mass",     0.47, 0.30, 0.52, "dark"),
    "oersted":       ("oersted.jpg",       "maxwell",  0.48, 0.48, 0.96, "paper"),
    "navier":        ("navier.jpg",        "navier",   0.50, 0.42, 0.80, "dark"),
    "bayes":         ("bayes.gif",         "bayes",    0.50, 0.40, 0.80, "paper"),
}


def _lin(hexstr: str) -> np.ndarray:
    c = np.array([int(hexstr[i:i + 2], 16) for i in (1, 3, 5)], np.float64) / 255
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _smooth(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def crop(im: Image.Image, cx: float, cy: float, h: float) -> Image.Image:
    """A 4:5 crop of height h (fraction of the source height) centred at (cx, cy), clamped inside the image."""
    W, H = im.size
    ch = min(h * H, H, W * 5 / 4)
    cw = ch * 4 / 5
    x0 = min(max(cx * W - cw / 2, 0), W - cw)
    y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((OW, OH), Image.LANCZOS)


def cutout(g: np.ndarray) -> np.ndarray:
    """Subject mask in [0, 1] for a light, plain background (g: sRGB luminance in [0, 1], OH x OW)."""
    from scipy import ndimage as ndi
    gs = ndi.gaussian_filter(g, 4.0)                # closes gaps in engraved outlines and stipple
    grad = np.hypot(ndi.sobel(gs, 0), ndi.sobel(gs, 1))
    border = np.concatenate([gs[:12].ravel(), gs[:, :12].ravel(), gs[:, -12:].ravel()])
    b = np.median(border)
    cand = (np.abs(gs - b) < 0.13) & (grad < 0.35) & (gs > 0.7)    # paper only: near-white
    lab, _ = ndi.label(cand)
    edge = np.unique(np.concatenate([lab[0], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    bg = ndi.binary_opening(bg, iterations=3)
    subj = ndi.binary_fill_holes(~bg)
    lab, n = ndi.label(subj)
    if n > 1:                                       # keep the largest piece: the person
        sizes = ndi.sum(subj, lab, range(1, n + 1))
        subj = lab == (1 + int(np.argmax(sizes)))
    subj = ndi.binary_erosion(subj, iterations=2)
    return np.clip(ndi.gaussian_filter(subj.astype(np.float64), 3.0) * 1.15, 0, 1)


def duotone(gray: np.ndarray, hue: str, mask: np.ndarray | None, gamma: float = 1.15) -> np.ndarray:
    """Luminance in [0, 1] -> linear RGB: black -> the hue -> a pale tint of it (never pure white)."""
    sample = gray[mask > 0.5] if mask is not None and (mask > 0.5).any() else gray
    lo, hi = np.percentile(sample, [1, 99.5])        # level on the subject, not on the background
    v = np.clip((gray - lo) / max(hi - lo, 1e-6), 0, 1)
    v = v ** gamma
    h = _lin(hue)
    pale = h * 0.45 + 0.55 * np.array([0.92, 0.93, 0.95])
    a = np.clip(v / 0.6, 0, 1)[..., None]           # shadows → hue
    b = np.clip((v - 0.6) / 0.4, 0, 1)[..., None]   # highlights → pale
    return (h * 0.85 * a) * (1 - b) + pale * b


def surround(strength: float = 0.85) -> np.ndarray:
    """Radial darkening for studio photos: 1 over the face (upper middle), falling towards the edges."""
    yy, xx = np.mgrid[0:OH, 0:OW]
    u = (xx + 0.5) / OW * 2 - 1
    w = ((yy + 0.5) / OH * 2 - 1 + 0.12) * 0.9      # centred a little above the middle, where the face sits
    r = np.hypot(u / 0.72, w / 0.95)
    return 1 - strength * _smooth((r - 0.55) / 0.5)


def feather_alpha() -> np.ndarray:
    """Soft superellipse vignette: opaque in the middle, gone at the edges (stronger at the bottom and sides)."""
    yy, xx = np.mgrid[0:OH, 0:OW]
    u = (xx + 0.5) / OW * 2 - 1
    w = (yy + 0.5) / OH * 2 - 1
    w = np.where(w > 0, w * 1.12, w * 0.95)         # bottom (shoulders) fades a little earlier
    d = (np.abs(u) ** 3 + np.abs(w) ** 3) ** (1 / 3)
    return _smooth((1.0 - d) / 0.42)


def build(key: str) -> Path:
    src, hue, cx, cy, h, bgmode = PORTRAITS[key]
    im = crop(Image.open(SRC / src).convert("L"), cx, cy, h)
    g = np.asarray(im, np.float64) / 255
    mask = cutout(g) if bgmode == "paper" else None
    lin = g ** 2.2
    if bgmode == "studio":
        sample = lin[surround() > 0.99]            # level on the face region before darkening the wall
        lo, hi = np.percentile(sample, [1, 99.5])
        lin = np.clip((lin - lo) / max(hi - lo, 1e-6), 0, 1) * surround()
    rgb = duotone(lin, getattr(C, hue), mask, 1.45 if bgmode == "studio" else 1.15)  # tone-map in linear light
    srgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.clip(rgb, 0, 1) ** (1 / 2.4) - 0.055)
    alpha = feather_alpha() * (mask if mask is not None else 1.0)
    rgba = np.dstack([srgb, alpha])
    out = OUT / f"{key}.png"
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(out)
    return out


if __name__ == "__main__":
    for k in sys.argv[1:] or PORTRAITS:
        print(build(k).relative_to(VIDEO))
