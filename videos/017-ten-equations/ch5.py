"""Chapter 5 shared pieces: the chord and its spectrum, square-wave partial sums, the π epicycles, a melody's
spectrogram, a photo rebuilt from a few DCT numbers, and an MRI phantom rebuilt from its frequencies. All computed.

Example:
    f = chord(t); F = spectrum(np.linspace(200, 450, 400))
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

from kit import mix

NOTES = (261.63, 329.63, 392.00)                 # C4, E4, G4 (Hz)
WIN = 0.05                                       # the chord window drawn on screen (s)


def hann(t, T=WIN):
    return np.sin(np.pi * np.clip(t / T, 0, 1)) ** 2


def chord(t, parts=(0, 1, 2), env=True):
    """The three notes added (t in seconds from the window start), a smooth Hann envelope so the sound starts and
    stops softly (the same envelope the transform below sees)."""
    y = sum(np.sin(2 * np.pi * NOTES[i] * t) for i in parts)
    return y * hann(t) if env else y


@lru_cache(maxsize=1)
def _tgrid(n=6000):
    return np.linspace(0, WIN, n)


def transform(f_hz):
    """|F(ω)| = |∫ f(t) e^{−iωt} dt| of the windowed chord at the given frequencies (Hz), peak normalised to 1."""
    t = _tgrid()
    f = chord(t)
    F = np.abs(np.trapezoid(f[None, :] * np.exp(-2j * np.pi * np.atleast_1d(f_hz)[:, None] * t[None, :]), t, axis=1))
    return F / _peak()


@lru_cache(maxsize=1)
def _peak():
    t = _tgrid()
    f = chord(t)
    return float(np.abs(np.trapezoid(f * np.exp(-2j * np.pi * NOTES[0] * t), t)))


def square_sum(x, n_terms):
    """Partial Fourier sum of a square wave: (4/π) Σ_{k odd} sin(kx)/k over the first n_terms odd k."""
    k = 2 * np.arange(n_terms) + 1
    return 4 / np.pi * (np.sin(np.outer(x, k)) / k).sum(1)


# ------------------------------------------------------------------------------------------------ π epicycles
@lru_cache(maxsize=1)
def pi_terms(height=3.7, n_terms=90):
    """Epicycle terms (freqs, coeffs) of the outline of a π glyph (sims.fourier_path), centred, `height` tall."""
    from manim import MathTex

    import sims as sm
    g = MathTex(r"\pi").family_members_with_points()[0]
    pts = np.array([g.point_from_proportion(a) for a in np.linspace(0, 1, 700, endpoint=False)])[:, :2]
    pts -= pts.mean(0)
    pts *= height / np.ptp(pts[:, 1])
    return sm.fourier_path(pts, n_terms)


def pi_trace(phase, n=600):
    import sims as sm
    fr, co = pi_terms()
    return np.array([sm.epicycles(fr, co, s)[-1] for s in np.linspace(0, phase, max(int(n * phase), 2))])


# ------------------------------------------------------------------------------------------------ melody
@lru_cache(maxsize=1)
def spectrogram(sr=8000, nfft=512, hop=96, fmax=1100.0):
    """STFT magnitude of a short synthesised melody (piano-like: harmonics 1, ½, ¼ with an exponential decay).
    Returns (times (s), freqs (Hz), |S| normalised, rows = time)."""
    seq = [(261.63, 0.3), (293.66, 0.3), (329.63, 0.3), (392.0, 0.45), (329.63, 0.3), (293.66, 0.3),
           (261.63, 0.3), (196.0, 0.6)]
    out = []
    for f0, d in seq:
        t = np.arange(int(sr * d)) / sr
        env = np.exp(-t / 0.22) * np.minimum(t / 0.008, 1)
        out.append(env * sum(a * np.sin(2 * np.pi * f0 * h * t) for h, a in ((1, 1), (2, 0.5), (3, 0.25))))
    x = np.concatenate(out)
    w = np.hanning(nfft)
    frames = [x[i:i + nfft] * w for i in range(0, len(x) - nfft, hop)]
    S = np.abs(np.fft.rfft(frames, axis=1))
    fr = np.fft.rfftfreq(nfft, 1 / sr)
    keep = fr <= fmax
    S = S[:, keep]
    return np.arange(len(frames)) * hop / sr, fr[keep], S / S.max()


# ------------------------------------------------------------------------------------------------ photo (DCT)
@lru_cache(maxsize=1)
def dct_photo(fracs=(0.01, 0.05, 0.2), size=(240, 300)):
    """Fourier's portrait (grey), rebuilt from the largest `frac` of its 2D DCT coefficients. Returns
    ({frac: grey image 0..1}, alpha), rows top-first."""
    from PIL import Image
    from scipy.fft import dctn, idctn
    im = Image.open(Path(__file__).parent / "assets/images/portraits/fourier.png").convert("RGBA").resize(size)
    a = np.asarray(im).astype(np.float32) / 255
    grey = a[..., :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    C = dctn(grey, norm="ortho")
    mags = np.sort(np.abs(C).ravel())[::-1]
    out = {}
    for fr in fracs:
        th = mags[max(int(fr * mags.size) - 1, 0)]
        out[fr] = np.clip(idctn(np.where(np.abs(C) >= th, C, 0), norm="ortho"), 0, 1)
    return out, a[..., 3]


# ------------------------------------------------------------------------------------------------ MRI
_SL = [(1.0, .69, .92, 0, 0, 0), (-.8, .6624, .874, 0, -.0184, 0), (-.2, .11, .31, .22, 0, -18),
       (-.2, .16, .41, -.22, 0, 18), (.1, .21, .25, 0, .35, 0), (.1, .046, .046, 0, .1, 0),
       (.1, .046, .046, 0, -.1, 0), (.1, .046, .023, -.08, -.605, 0), (.1, .023, .023, 0, -.606, 0),
       (.1, .023, .046, .06, -.605, 0)]


@lru_cache(maxsize=1)
def phantom(n=256):
    """The (modified) Shepp–Logan head phantom, the standard test slice for MRI and CT reconstruction."""
    c = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(c, -c)
    P = np.zeros((n, n))
    for A, a, b, x0, y0, phi in _SL:
        p = np.radians(phi)
        xr = (X - x0) * np.cos(p) + (Y - y0) * np.sin(p)
        yr = -(X - x0) * np.sin(p) + (Y - y0) * np.cos(p)
        P[(xr / a) ** 2 + (yr / b) ** 2 <= 1] += A
    return P


@lru_cache(maxsize=1)
def kspace():
    """What the scanner measures: the slice's 2D Fourier transform (centred)."""
    return np.fft.fftshift(np.fft.fft2(phantom()))


def mri_rebuild(frac):
    """The slice rebuilt from the k-space samples within radius `frac` of the centre (the low frequencies first)."""
    K = kspace()
    n = K.shape[0]
    c = np.arange(n) - n / 2
    R = np.hypot(*np.meshgrid(c, c)) / (n / 2)
    img = np.abs(np.fft.ifft2(np.fft.ifftshift(K * (R <= frac))))
    return np.clip(img / 1.0, 0, 1)


def heat_ramp(v, fourier, light):
    """0 → black, 0.55 → the Fourier hue, 1 → near white (heated metal in the chapter's hue)."""
    from kit import tint
    v = float(np.clip(v, 0, 1))
    if v < 0.55:
        return tint(fourier, (v / 0.55) ** 1.4)
    return mix(fourier, light, (v - 0.55) / 0.45)
