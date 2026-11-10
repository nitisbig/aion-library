"""Ch6 shared pieces: drawing anything (S24–S27).

The clef chain is the intro's own (shared.clef_terms: 201 coefficients from the S24 recipe,
c₀ = 0 because the clef is centered, so the chain is exactly 200 circles). It sits at
CLEF_AT, scaled by CLEF_K, from S24's strip to S26. S25's counter, clock, zoom and camera
are pure functions of time, so S26 can pick up the pull-back mid-move.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from manim import Dot, Line, MathTex, VGroup, VMobject

from aion import fourier as F
from aion import style as S
import shared as V
import ch4 as C4
from ch4 import TAU, cue, to3, path

S24, S25, S26, S27 = (V.scene_range(n) for n in (24, 25, 26, 27))
CLEF_AT = complex(-2.6, -0.3)
CLEF_K = 0.8


@lru_cache(maxsize=1)
def clef_terms():
    """The 200 nonzero circles, biggest first."""
    return [(n, c) for n, c in V.clef_terms() if abs(c) > 1e-9]


def clef_z(t, n_terms: int = 200):
    return CLEF_AT + CLEF_K * F.partial_sum(dict(clef_terms()[:n_terms]), t)


@lru_cache(maxsize=1)
def clef_outline_pts() -> np.ndarray:
    return clef_z(np.linspace(0, 1, 4000))


def clef_outline(op: float = 0.35, color=S.ARM, width: float = 2.0) -> VMobject:
    z = clef_outline_pts()
    return path(np.append(z, z[0]), color, width, op)


# ── S24: the strip of 201 bars ─────────────────────────────────────────────
STRIP_X0, STRIP_X1, STRIP_Y, STRIP_H = 0.55, 6.55, -2.55, 2.7


@lru_cache(maxsize=1)
def coeff_list():
    """All 201 (n, c_n), n = −100…100 (speed order on the strip)."""
    c = V.clef_coeffs()
    return [(n, c[n]) for n in range(-100, 101)]


def bar_height(c) -> float:
    cmax = max(abs(v) for _, v in coeff_list())
    return STRIP_H * abs(c) / cmax


def strip_x(i: int, count: int = 201) -> float:
    return STRIP_X0 + (STRIP_X1 - STRIP_X0) * i / (count - 1)


def bar(n: int, c, x: float, width: float = 2.0) -> Line:
    h = max(bar_height(c), 0.004)
    return Line([x, STRIP_Y, 0], [x, STRIP_Y + h, 0], color=C4.color_of(n), stroke_width=width)


@lru_cache(maxsize=1)
def size_rank() -> dict:
    """n → rank by size (0 = biggest), the chain order."""
    order = sorted(coeff_list(), key=lambda nc: (-abs(nc[1]), abs(nc[0]), -nc[0]))
    return {n: i for i, (n, _) in enumerate(order)}


def clef_dots(n_dots: int = 1000) -> np.ndarray:
    """The 1,000 dots (the recipe's samples), screen coords."""
    from aion.drawings import treble_clef
    z = V.CLEF_SCALE * treble_clef(n_dots)
    return CLEF_AT + CLEF_K * z


# ── S25: counter, loop clock, zoom ─────────────────────────────────────────
@lru_cache(maxsize=1)
def s25_times() -> dict:
    T = {k: cue(key, S25) for k, key in (("one", "one circle"), ("five", "five"), ("twenty", "twenty"),
                                          ("two", "two hundred"), ("close", "up close"))}
    T["off"] = cue("the others", S25)
    return T


@lru_cache(maxsize=1)
def loop_clock() -> C4.Clock:
    """Drawing time in loops: one loop per counter step (1.6 s; 3 s for 200), then a crawl for the dive."""
    T = s25_times()
    e = 0.15
    k = []
    for key, dur in (("one", 1.6), ("five", 1.6), ("twenty", 1.6)):
        k += [(T[key], e, 1 / (dur - e)), (T[key] + dur - e, e, 0.0)]
    k += [(T["two"], e, 1 / 3.0), (T["close"], 1.6, 0.004)]
    return C4.Clock(k, S24[0], S27[1])


def n_circles(now: float) -> int:
    T = s25_times()
    if now < T["one"]:
        return 200
    if now < T["five"]:
        return 1
    if now < T["twenty"]:
        return 5
    if now < T["two"]:
        return 20
    if T["off"] + 0.1 <= now < T["off"] + 1.1:
        return 150                         # the last 50 circles off
    return 200


def ink_from(now: float):
    T = s25_times()
    t = float(loop_clock()(now))
    for key, start in (("two", 3.0), ("twenty", 2.0), ("five", 1.0), ("one", 0.0)):
        if now >= T[key]:
            return max(start, t - 1.0)
    return None                            # before "one circle": no ink


def _smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def zoom_amount(now: float) -> float:
    """0 → 1: the dive (on "up close", 1.6 s) and the pull-back (after the toggle, 1.3 s, into S26)."""
    T = s25_times()
    return float(_smooth((now - T["close"]) / 1.6) - _smooth((now - T["off"] - 1.15) / 1.3))


def s25_state(now: float, **kw) -> dict:
    """EpicyclePlate state for S24's end … S26's start."""
    T = s25_times()
    t = float(loop_clock()(now))
    terms = [(n, CLEF_K * c) for n, c in clef_terms()[:n_circles(now)]]
    u = zoom_amount(now)
    s = {"terms": terms, "origin": CLEF_AT, "t": t, "ink_from": ink_from(now), "rim_tint": 1.0,
         "sparks": float(_smooth((now - T["two"]) / 0.6)), "zoom": 1.0 + 39.0 * u, "ink_samples": 12000}
    if u > 0:                              # the pen's screen offset shrinks smoothly to 0 (always in view)
        pen = CLEF_AT + CLEF_K * F.partial_sum(dict(clef_terms()), t)
        s["cam"] = pen - (1 - u) * pen / s["zoom"]
    return {**s, **kw}


# ── S26: three panels ──────────────────────────────────────────────────────
PANEL_X = (-4.45, 0.0, 4.45)
P_TOP_Y, P_BASE_Y, P_BAR_H = 1.55, -2.7, 2.2
P_DX = 0.4


def panel_bar(cx: float, pos: int, h: float, color) -> Line:
    x = cx - 1.6 + (pos - 1) * P_DX
    return Line([x, P_BASE_Y, 0], [x, P_BASE_Y + P_BAR_H * h, 0], color=color, stroke_width=6)


def panel_axis(cx: float, op: float = 0.5) -> Line:
    return Line([cx - 1.85, P_BASE_Y, 0], [cx + 1.85, P_BASE_Y, 0], color=S.ARM, stroke_width=1.5).set_stroke(opacity=op)


def panel_frac(cx: float, pos: int, h: float, tex: str, color) -> MathTex:
    x = cx - 1.6 + (pos - 1) * P_DX
    return MathTex(tex, font_size=40, color=color).move_to([x, P_BASE_Y + P_BAR_H * h + 0.45, 0])


# panel contents (all computed): bar heights are |cₙ| / |c₁|
def wave_bars():
    """Square wave (aion.fourier.square_wave_radii): 1/n at odd n."""
    r = F.square_wave_radii(5)
    return [(n, rn / r[0][1], S.FWD) for n, rn in r]


def loop_bars():
    """The intro square (shared.square_coeffs): 1/n² at n = 1, −3, 5, −7, 9."""
    c = V.square_coeffs()
    return [(abs(n), abs(c[n] / c[1]), C4.color_of(n)) for n in (1, -3, 5, -7, 9)]


OVAL = {1: 1.0, 2: 0.25, -3: 0.06}


def oval_bars():
    return [(abs(n), abs(c), C4.color_of(n)) for n, c in OVAL.items()]


def panel_drawing(i: int, op: float = 1.0) -> VGroup:
    """Panel i's picture at (PANEL_X[i], P_TOP_Y): 0 square wave, 1 square loop, 2 smooth oval."""
    cx, cy = PANEL_X[i], P_TOP_Y
    g = VGroup()
    if i == 0:
        x = np.linspace(-1.75, 1.75, 1200)
        th = TAU * (x + 1.75) / 1.75                      # two periods across the panel
        sq = np.sign(np.sin(th))
        g.add(path(cx + x + 1j * (cy + 0.8 * sq), S.ARM, 1.5, 0.45 * op),
              path(cx + x + 1j * (cy + 0.8 * F.square_wave(th, 5)), S.INK, 3.0, op))
    elif i == 1:
        c = V.square_coeffs()
        k = 0.95 / abs(c[1])
        t = np.linspace(0, 1, 1500)
        z = F.partial_sum({n: c[n] for n in (1, -3, 5, -7, 9)}, t)
        sq = k * V.SQUARE_HALF * F.square_loop(400, 1.0)
        g.add(path(np.append(cx + 1j * cy + sq, cx + 1j * cy + sq[0]), S.ARM, 1.5, 0.45 * op),
              path(cx + 1j * cy + k * z, S.INK, 3.0, op))
    else:
        t = np.linspace(0, 1, 1200)
        z = 0.95 * F.partial_sum(OVAL, t)
        g.add(path(cx + 1j * cy + z, S.INK, 3.0, op))
    return g


def panel_bars(i: int) -> list:
    rows = (wave_bars, loop_bars, oval_bars)[i]()
    return [panel_bar(PANEL_X[i], pos, h, col) for pos, h, col in rows]


PANEL_FRACS = {0: [(3, r"\frac{1}{3}"), (5, r"\frac{1}{5}")], 1: [(3, r"\frac{1}{9}"), (5, r"\frac{1}{25}")]}


def panel_labels(i: int) -> list:
    rows = {pos: h for pos, h, _ in (wave_bars, loop_bars, oval_bars)[i]()}
    return [panel_frac(PANEL_X[i], pos, rows[pos], tex, S.LABEL) for pos, tex in PANEL_FRACS.get(i, [])]


def panel(i: int) -> VGroup:
    """Panel i complete (S26's end picture): drawing, axis, bars, fractions."""
    return VGroup(panel_drawing(i), panel_axis(PANEL_X[i]), VGroup(*panel_bars(i)), VGroup(*panel_labels(i)))


# ── S27: two voices, one fundamental; a photo kept from its big circles ───
VOICES = {   # harmonic amplitudes (same fundamental): a soft voice, a bright bowed string
    "singer": [1.0, 0.55, 0.30, 0.12, 0.06, 0.03, 0.0, 0.0],
    "violin": [1.0, 0.85, 0.66, 0.56, 0.44, 0.36, 0.26, 0.19],
}
VOICE_Y = {"singer": 1.25, "violin": -1.25}
WAVE_X0, WAVE_X1, WAVE_AMP = -5.6, 1.0, 0.75
VSTRIP_X0, VSTRIP_DX, VSTRIP_H = 2.7, 0.42, 1.05


def voice_phases(name: str) -> np.ndarray:
    rng = np.random.default_rng({"singer": 2701, "violin": 2702}[name])
    return rng.uniform(0, TAU, len(VOICES[name]))


def voice_wave(name: str, op: float = 1.0, periods: float = 3.0) -> VMobject:
    a, ph = np.array(VOICES[name]), voice_phases(name)
    x = np.linspace(WAVE_X0, WAVE_X1, 1600)
    u = periods * (x - WAVE_X0) / (WAVE_X1 - WAVE_X0)
    y = sum(ak * np.sin(TAU * (k + 1) * u + p) for k, (ak, p) in enumerate(zip(a, ph)))
    y = WAVE_AMP * y / np.abs(y).max()
    return path(x + 1j * (VOICE_Y[name] + y), S.INK, 3.0, op)


def voice_bars(name: str) -> list:
    base = VOICE_Y[name] - 0.55
    return [Line([VSTRIP_X0 + k * VSTRIP_DX, base, 0], [VSTRIP_X0 + k * VSTRIP_DX, base + VSTRIP_H * max(a, 0.004), 0],
                 color=S.FWD, stroke_width=7) for k, a in enumerate(VOICES[name])]


def voice_axis(name: str) -> Line:
    base = VOICE_Y[name] - 0.55
    return Line([VSTRIP_X0 - 0.25, base, 0], [VSTRIP_X0 + 7 * VSTRIP_DX + 0.25, base, 0], color=S.ARM,
                stroke_width=1.5).set_stroke(opacity=0.5)


IMG_N, BLOCK, KEEP = 128, 8, 0.10


@lru_cache(maxsize=1)
def photo() -> np.ndarray:
    """The clef as a 128-px grayscale picture (0…1): this video's own drawing, rasterized."""
    from PIL import Image, ImageDraw, ImageFilter
    z = clef_outline_pts()
    z = z - complex((z.real.max() + z.real.min()) / 2, (z.imag.max() + z.imag.min()) / 2)
    z = z / ((z.imag.max() - z.imag.min()) * 1.12)
    W = IMG_N * 4
    pts = [(W / 2 + W * p.real, W / 2 - W * p.imag) for p in z]
    im = Image.new("L", (W, W), 0)
    ImageDraw.Draw(im).line(pts + [pts[0]], fill=255, width=14, joint="curve")
    im = im.filter(ImageFilter.GaussianBlur(3)).resize((IMG_N, IMG_N), Image.LANCZOS)
    return np.asarray(im, float) / 255.0


def _blocks(a: np.ndarray) -> np.ndarray:
    n = IMG_N // BLOCK
    return a.reshape(n, BLOCK, n, BLOCK).swapaxes(1, 2)


@lru_cache(maxsize=1)
def photo_dct() -> np.ndarray:
    from scipy.fft import dctn
    return dctn(_blocks(photo()), axes=(2, 3), norm="ortho")


@lru_cache(maxsize=1)
def keep_threshold() -> float:
    c = np.abs(photo_dct()).ravel()
    return float(np.sort(c)[::-1][int(KEEP * c.size) - 1])


@lru_cache(maxsize=1)
def photo_kept() -> np.ndarray:
    """The picture rebuilt from its biggest 10 % of block-DCT coefficients (scipy.fft.idctn)."""
    from scipy.fft import idctn
    d = photo_dct()
    d = np.where(np.abs(d) >= keep_threshold(), d, 0.0)
    b = idctn(d, axes=(2, 3), norm="ortho")
    return np.clip(b.swapaxes(1, 2).reshape(IMG_N, IMG_N), 0, 1)


def busy_block() -> tuple:
    """The block with the most detail (the one whose bars we show)."""
    e = (photo_dct() ** 2).sum(axis=(2, 3)) - photo_dct()[:, :, 0, 0] ** 2
    return np.unravel_index(int(np.argmax(e)), e.shape)


def tinted(a: np.ndarray) -> np.ndarray:
    from manim import ManimColor
    rgb = np.array(ManimColor(S.INK).to_rgb())
    img = (a[..., None] * rgb[None, None, :] * 255).astype(np.uint8)
    return np.concatenate([img, np.full(a.shape + (1,), 255, np.uint8)], axis=2)
