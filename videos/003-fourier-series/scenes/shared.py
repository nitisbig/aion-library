"""Shared paths, scene ranges, drawings and motifs for video 003 (Fourier series).

Every scene builds its own first frame from the builders here, so the last frame of
scene N and the first frame of scene N+1 come from the same code with the same
parameters: cuts are invisible without replaying earlier scenes.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arc, Circle, DashedVMobject, Line, MathTex,
                   ParametricFunction, Rectangle, RoundedRectangle, Square, TexTemplate, Text,
                   ValueTracker, VGroup, VMobject, config, smooth)

from aion import fourier as F
from aion import style as S
from aion.components.epicycle_gl import EpicyclePlate
from aion.drawings import treble_clef
from aion.narration import NarratedScene

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from beats import BEAN, CUT_FRAMES, FPS, ROUNDED_SQUARE  # noqa: E402  (single sources)

AUDIO = ROOT / "assets" / "audio.mp3"
SRT = ROOT / "assets" / "cue-per-word.srt"
BG = S.STAGE                                        # pure black

_TEX = TexTemplate()
_TEX.add_to_preamble(S.TEX_PREAMBLE)
config.tex_template = _TEX


def scene_range(n: int) -> tuple[float, float]:
    """(start, end) in absolute seconds of scene n (1-based), frame-exact."""
    return CUT_FRAMES[n - 1] / FPS, CUT_FRAMES[n] / FPS


def window(u0: float, u1: float, ease=smooth):
    """A rate function that only moves inside [u0, u1] of an animation."""
    def f(u):
        return ease(min(1.0, max(0.0, (u - u0) / (u1 - u0))))
    return f


class VideoScene(NarratedScene):
    AUDIO, SRT, BACKGROUND = AUDIO, SRT, BG

    def beat(self, key: str, *anims, rt: float = 0.8, after: float | None = None,
             lead: float = S.LEAD, rate=smooth, **kw):
        """Play `anims` so they start `lead` before the cue word `key`."""
        if rate is not None:                     # rate=None: each animation keeps its own rate_func
            kw["rate_func"] = rate
        self.play_at(self.t(key, after), *anims, lead=lead, run_time=rt, **kw)

    def get_moving_mobjects(self, *animations):
        """Return TOP-LEVEL mobjects, not Manim's flattened family list.

        Manim caches this list for a whole play()/wait() and draws exactly it each frame.
        Flattened, it would keep drawing children that `redraw` has since swapped out (a
        frozen double) and miss the new ones; top-level, families are re-read every frame."""
        flat = super().get_moving_mobjects(*animations)
        if not flat:
            return flat
        for i, m in enumerate(self.mobjects):
            if flat[0] in m.get_family():
                return self.mobjects[i:]
        return flat

    def get_moving_and_static_mobjects(self, animations):
        """Keep the cached moving list top-level (Manim flattens it here a second time)."""
        _, static = super().get_moving_and_static_mobjects(animations)
        return self.get_moving_mobjects(*animations), static

    def drive(self, tracker: ValueTracker, fn) -> ValueTracker:
        """Set `tracker` to fn(absolute audio time) on every frame (stateless, any frame renders alone)."""
        tracker.add_updater(lambda m, dt: m.set_value(fn(self.now)))   # dt: a time-based updater, so wait() never freezes the frame
        tracker.set_value(fn(self.now))
        self.add(tracker)
        return tracker


# Production pass 1 (2026-11-09): chapter eyebrows off; labels a weight heavier (Inter Light read
# thin and soft at phone size); every spinning circle carries its term (aion.components.term_label).
SHOW_EYEBROWS = False
TERM_LABELS = True


def label(text: str, size: float = 30, color=S.LABEL, **kw) -> Text:
    kw.setdefault("weight", "MEDIUM" if size < 34 else "NORMAL")   # Medium: crisper strokes at 1080p
    return Text(text, font=S.FONT, font_size=size, color=color, **kw)


# ── drawings (drawing units = Manim units) ──────────────────────────────────
CLEF_SCALE = 3.6                     # clef ≈ 6.4 units tall (of 8), centered on its balance point
SQUARE_HALF = 2.2                    # the intro square: side 4.4


@lru_cache(maxsize=1)
def clef_coeffs() -> dict[int, complex]:
    """201 circles, n = −100…100 (the S24 recipe: 1,000 dots, spin and average)."""
    return F.coefficients(CLEF_SCALE * treble_clef(1000), 100)


@lru_cache(maxsize=1)
def clef_terms() -> list[tuple[int, complex]]:
    return F.order_terms(clef_coeffs(), keep_zero_first=False)


@lru_cache(maxsize=1)
def square_coeffs() -> dict[int, complex]:
    """The square loop, n ≡ 1 (mod 4) only: 201 circles up to |n| = 401 (the rest are exactly 0)."""
    c = F.coefficients(F.square_loop(8192, SQUARE_HALF), 401)
    return {n: v for n, v in c.items() if n % 4 == 1}


def tween_order() -> list[int]:
    """One fixed chain order for the clef → square morph: by the larger of the two sizes."""
    a, b = clef_coeffs(), square_coeffs()
    ns = sorted(set(a) | set(b), key=lambda n: (-max(abs(a.get(n, 0)), abs(b.get(n, 0))), abs(n), -n))
    return [n for n in ns if n != 0]


def tween_terms(alpha: float) -> list[tuple[int, complex]]:
    """Coefficient-wise blend clef → square. The pen path morphs; the chain never reorders."""
    a, b = clef_coeffs(), square_coeffs()
    if alpha <= 0:
        return clef_terms()
    out = [(n, (1 - alpha) * a.get(n, 0) + alpha * b.get(n, 0)) for n in tween_order()]
    if alpha >= 1:
        out = [(n, c) for n, c in out if abs(c) > 1e-12]
    return out


def square_terms() -> list[tuple[int, complex]]:
    return tween_terms(1.0)


def bean_terms() -> list[tuple[int, complex]]:
    return F.order_terms(BEAN, keep_zero_first=True)


def bean_gallery() -> list[tuple[int, complex]]:
    """The Ch5 bean, centered (its speed-zero offset dropped) for the intro gallery."""
    return F.order_terms({n: c for n, c in BEAN.items() if n != 0}, keep_zero_first=False)


def corner_times(terms, k: int = 4000) -> np.ndarray:
    """Drawing times (loops) at which the square's pen is closest to each of its 4 corners."""
    t = np.arange(k) / k
    z = F.partial_sum(terms, t)
    corners = SQUARE_HALF * np.array([1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j])
    return np.array([t[np.argmin(np.abs(z - c))] for c in corners]), corners


def sharpest_turn(z: np.ndarray, lower_half: bool = True) -> complex:
    """The sample where the drawing turns hardest (for camera push-ins)."""
    d = np.diff(np.append(z, z[0]))
    turn = np.abs(np.angle(d[1:] / d[:-1]))
    turn = np.append(turn, 0)
    if lower_half:
        turn[z.imag > np.median(z.imag)] = 0
    return complex(z[int(np.argmax(turn))])


# ── the opening chain: S01 and S02 share these numbers ─────────────────────
LOOP_S01 = scene_range(1)[1] - scene_range(1)[0]      # one clef loop = all of S01 (13.283 s)


def clef_state(t: float, **kw) -> dict:
    return {"terms": clef_terms(), "t": t, "ink_from": 0.0 if t <= 1 else t - 1.0, **kw}


# rim_vivid: one hue per circle (S.RIM_HUES); pen_glow / bloom kept low so the small circles stay crisp
S01_END = dict(zoom=1.0, rim_tint=1.0, rim_vivid=1.0, pen_glow=0.35, pen_alpha=1.0, sparks=0.6, bloom=0.85, sweep=None)


# ── motifs ─────────────────────────────────────────────────────────────────
RECIPE = r"c_n", r"=", r"\int_0^1", r"f(t)", r"\,e^{-2\pi i n t}", r"\,dt"
RECIPE_POS = np.array([3.55, 2.75, 0.0])              # S03 plants it here; S23 brings it back here


def recipe(size: float = 40, muted: bool = True) -> MathTex:
    m = MathTex(*RECIPE, font_size=size, color=S.LABEL)
    if muted:
        m.set_color(S.LABEL_MUTED).set_opacity(0.7)
    else:
        for i, c in ((0, S.STILL), (2, S.ARM), (3, S.INK), (4, S.BWD), (5, S.ARM)):
            m[i].set_color(c)
    return m


def rounded_square(R: float = 1.5, center=ORIGIN, color=S.INK, width: float = 4) -> ParametricFunction:
    """z = R(e^{2πit} − (1/9) e^{−2πi·3t}): the two-circle friendly example."""
    c = np.array(center, float)

    def f(t):
        z = F.partial_sum(ROUNDED_SQUARE, t)
        return c + R * np.array([z.real, z.imag, 0.0])
    return ParametricFunction(f, t_range=(0, 1, 1 / 400), color=color, stroke_width=width)


def heat_ring(center=ORIGIN, rx: float = 2.2, ry: float = 0.85, width: float = 22, segments: int = 240) -> VGroup:
    """Teaser ring: half ember, half ice (HEAT_RAMP), as a lit ellipse of thick arcs.
    Stands in for the S11 HeatRingPlate render until that plate exists."""
    lo, mid, hot, white = S.HEAT_RAMP
    from manim import interpolate_color, ManimColor
    ring = VGroup()
    th = np.linspace(0, 2 * np.pi, segments + 1)
    c = np.array(center, float)
    for a0, a1 in zip(th[:-1], th[1:]):
        m = (a0 + a1) / 2
        u = 0.5 + 0.5 * np.tanh(4 * np.sin(m))          # 1 on the hot half (top), 0 on the cold half
        col = interpolate_color(ManimColor(lo), ManimColor(mid), u * 2) if u < 0.5 else \
            interpolate_color(ManimColor(hot), ManimColor(white), (u - 0.5) * 1.4)
        front = 0.55 + 0.45 * (np.sin(m - np.pi / 2) * -1 + 1) / 2   # nearer half brighter
        seg = Line(c + [rx * np.cos(a0), ry * np.sin(a0), 0], c + [rx * np.cos(a1), ry * np.sin(a1), 0],
                   stroke_width=width, color=col).set_stroke(opacity=front)
        ring.add(seg)
    glow = ring.copy().set_stroke(width=width * 2.6, opacity=0.12)
    return VGroup(glow, ring)


WHITE_KEYS = "CDEFGABC"


def piano(center=DOWN * 2.4, key_w: float = 0.62, key_h: float = 2.0) -> VGroup:
    """Line-art octave: 8 white keys C…C, 5 black keys. Returns VGroup(whites, blacks)."""
    whites = VGroup(*[RoundedRectangle(corner_radius=0.05, width=key_w, height=key_h)
                      .set_stroke(S.ARM, 1.6, 0.7).set_fill(S.STAGE_RAISED, 1)
                      for _ in WHITE_KEYS]).arrange(RIGHT, buff=0.04)
    blacks = VGroup()
    for i in (0, 1, 3, 4, 5):                          # after C, D, F, G, A
        b = RoundedRectangle(corner_radius=0.04, width=key_w * 0.58, height=key_h * 0.6)
        b.set_stroke(S.ARM, 1.4, 0.55).set_fill(S.STAGE, 1)
        b.move_to(whites[i].get_right() * [1, 0, 0] + whites[i].get_top() * [0, 1, 0], aligned_edge=UP)
        blacks.add(b)
    g = VGroup(whites, blacks).move_to(center)
    return g


# C4 E4 G4: display spatial frequencies proportional to the real pitches
CHORD_HZ = (261.63, 329.63, 392.00)


def note_wave(hz: float, center=ORIGIN, x_half: float = 5.6, amp: float = 0.32,
              color=S.ARM, width: float = 2.5) -> ParametricFunction:
    k = 2 * np.pi * 3.0 * hz / CHORD_HZ[0] / x_half      # C spans 6 cycles across the stage
    c = np.array(center, float)
    return ParametricFunction(lambda x: c + [x, amp * np.sin(k * x), 0], t_range=(-x_half, x_half, 0.01),
                              color=color, stroke_width=width)


def chord_wave(center=ORIGIN, x_half: float = 5.6, amp: float = 0.32, color=S.INK, width: float = 3.5):
    c = np.array(center, float)
    ks = [2 * np.pi * 3.0 * hz / CHORD_HZ[0] / x_half for hz in CHORD_HZ]
    return ParametricFunction(lambda x: c + [x, amp * sum(np.sin(k * x) for k in ks), 0],
                              t_range=(-x_half, x_half, 0.005), color=color, stroke_width=width)


# ── hand-off into Ch1 ──────────────────────────────────────────────────────
ONE_R = 1.2
ONE_CENTER = LEFT * 4


def one_circle(center=ONE_CENTER, r: float = ONE_R) -> Circle:
    return Circle(radius=r, color=S.FWD, stroke_width=3).move_to(center)


# ── small helpers used from Ch1 on ─────────────────────────────────────────
def redraw(fn):
    """always_redraw with a dt updater (plain always_redraw freezes during wait()).

    The result is a holder whose only child is replaced every frame. (`become()` would
    align differently shaped mobjects by padding them, and the padding nests deeper
    every frame until Python's recursion limit.)"""
    from manim import Group, Mobject
    holder = Group() if not isinstance(fn(), VMobject) else VGroup()

    def upd(h, dt):
        h.submobjects = [fn()]          # (VideoScene.get_moving_mobjects keeps the new child drawn)
    upd(holder, 0)
    holder.add_updater(upd)
    return holder


def eyebrow(text: str):
    """Chapter eyebrow, top-left (e.g. "01 · ONE CIRCLE")."""
    from manim import UL
    if not SHOW_EYEBROWS:
        return VGroup()
    return label(text, 20, S.LABEL_MUTED, weight="BOLD").to_corner(UL, buff=0.55)


# ── equation labels on spinning circles ────────────────────────────────────
def plate_labels(plate, state: dict, terms, count: int = 3, op: float = 1.0, size: float = 28,
                 min_r: float = 0.3, tint: bool = True, vivid: bool = False) -> VGroup:
    """Terms of the `count` biggest circles of an EpicyclePlate chain, pinned to its rims on screen."""
    from aion.components.term_label import exp_parts, labels
    if not TERM_LABELS or op <= 0:
        return VGroup()
    J = plate.joints(state)
    items = []
    for k, (n, c) in enumerate(list(terms)[:count]):
        p0 = plate.project(J[k])
        p1 = plate.project(J[k] + abs(c))
        r = float(np.hypot(*(p1 - p0)[:2]))
        col = (S.FWD if n > 0 else S.BWD if n < 0 else S.STILL) if tint else S.ARM
        if vivid:                                       # the label wears its own circle's hue
            col = S.RIM_HUES[k % len(S.RIM_HUES)]
        items.append((complex(p0[0], p0[1]), r, exp_parts(n, col), col))
    return labels(items, op=op, size=size, min_r=min_r)


# ── more loops for the S02 gallery (FFT of a sampled outline, like the clef) ─
def _loop_terms(z: np.ndarray, N: int = 40) -> list[tuple[int, complex]]:
    z = F.resample(np.append(z, z[0]), 1000)
    z = z - z.mean()
    z = z / np.abs(z).max()
    return [(n, c) for n, c in F.order_terms(F.coefficients(z, N), keep_zero_first=False) if abs(c) > 1e-9]


@lru_cache(maxsize=1)
def star_terms() -> list[tuple[int, complex]]:
    """A five-point star (outer 1, inner 0.42), traced once."""
    k = np.arange(10)
    r = np.where(k % 2 == 0, 1.0, 0.42)
    return _loop_terms(r * np.exp(1j * (np.pi / 2 + np.pi * k / 5)))


@lru_cache(maxsize=1)
def heart_terms() -> list[tuple[int, complex]]:
    """The classic heart curve x = 16 sin³t, y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t."""
    t = np.linspace(0, 2 * np.pi, 2000, endpoint=False)
    z = 16 * np.sin(t) ** 3 + 1j * (13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    return _loop_terms(z)


# ── circle art for the S02 gallery wall (top row): curves computed, then FFT (or exact) ─
@lru_cache(maxsize=1)
def butterfly_terms() -> list[tuple[int, complex]]:
    """Fay's butterfly: r = e^{cos t} − 2 cos 4t − sin⁵(t/12), t ∈ [0, 12π]."""
    t = np.linspace(0, 12 * np.pi, 6000, endpoint=False)
    r = np.exp(np.cos(t)) - 2 * np.cos(4 * t) - np.sin(t / 12) ** 5
    return _loop_terms(r * np.sin(t) + 1j * r * np.cos(t), N=70)


@lru_cache(maxsize=1)
def fish_terms() -> list[tuple[int, complex]]:
    """The fish curve x = cos t − sin²t/√2, y = cos t · sin t."""
    t = np.linspace(0, 2 * np.pi, 2000, endpoint=False)
    return _loop_terms(np.cos(t) - np.sin(t) ** 2 / np.sqrt(2) + 1j * np.cos(t) * np.sin(t), N=30)


@lru_cache(maxsize=1)
def infinity_terms() -> list[tuple[int, complex]]:
    """Bernoulli's lemniscate (∞): x = cos t / (1 + sin²t), y = sin t cos t / (1 + sin²t)."""
    t = np.linspace(0, 2 * np.pi, 2000, endpoint=False)
    d = 1 + np.sin(t) ** 2
    return _loop_terms((np.cos(t) + 1j * np.sin(t) * np.cos(t)) / d, N=25)


def rose_terms() -> list[tuple[int, complex]]:
    """Five-petal rose r = cos 5θ, θ = πt: exactly two circles, ½e^{2πi·3t} + ½e^{−2πi·2t}."""
    return [(3, 0.5 + 0j), (-2, 0.5 + 0j)]


def spiro_terms() -> list[tuple[int, complex]]:
    """A spirograph loop: three exact circles (speeds 1, −6, 8)."""
    return [(1, 0.62 + 0j), (-6, 0.3 + 0j), (8, 0.08 + 0j)]


# ── the cold-open preview (S00): Fourier's portrait drawn by 601 circles ───
PORTRAIT_N = 300                                         # speeds −300…300 (601 circles)


PORTRAIT_SRC = ROOT / "assets" / "images" / "fourier_portrait.jpg"


@lru_cache(maxsize=1)
def portrait_terms() -> list[tuple[int, complex]]:
    """Boilly's engraving of Fourier (public domain) as one line, then its 601 coefficients.

    Lanczos σ-factors (sinc(n/(N+1))) soften the highest speeds, so the line flows instead of
    jittering; the face keeps its shape."""
    from aion.drawings import portrait_line
    z = portrait_line(str(PORTRAIT_SRC))
    z = F.resample(np.append(z, z[0]), 8192)
    c = F.coefficients(z, PORTRAIT_N)
    c = {n: v * np.sinc(n / (PORTRAIT_N + 1)) for n, v in c.items()}
    return [(n, v) for n, v in F.order_terms(c, keep_zero_first=False) if abs(v) > 1e-9]


@lru_cache(maxsize=1)
def portrait_images():
    """The engraving laid exactly under the line drawing, in two looks, as RGBA arrays:
    gold (the engraving's dark strokes as gold light on black) and real (the original, its paper
    melting into black through an oval vignette). Returns (gold, real, center, width) with center
    and width in the line drawing's normalized units (before the scene's scale/offset)."""
    from PIL import Image
    from manim import color_to_rgb
    from aion.drawings import portrait_line
    portrait_terms()
    fr = portrait_line.frame
    im = Image.open(PORTRAIT_SRC).convert("RGB").crop(fr["crop"])
    w, h = fr["size_px"]
    big = im.resize((w * 2, h * 2), Image.LANCZOS)                  # 2× the contour grid: crisp at 1080p
    rgb = np.asarray(big, float) / 255
    H, W = rgb.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (0.5 * W), (yy - H * 0.45) / (0.47 * H))   # fades out inside the frame
    oval = np.clip((1.0 - r) / 0.22, 0, 1) ** 1.5                   # soft cameo edge
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    ink = np.clip((0.88 - lum) / 0.7, 0, 1) ** 1.2                  # dark engraving strokes → light
    gold = np.zeros((H, W, 4))
    gold[..., :3] = np.asarray(color_to_rgb(S.INK)) * ink[..., None]
    gold[..., 3] = ink * oval
    real = np.zeros((H, W, 4))
    real[..., :3] = rgb
    real[..., 3] = oval
    to8 = lambda a: (np.clip(a, 0, 1) * 255).astype(np.uint8)
    center = (complex(w / 2, -h / 2) - fr["center_px"]) / fr["scale_px"]
    return to8(gold), to8(real), center, w / fr["scale_px"]
