"""Check video 015's palette and export its design tokens to design/tokens.json (DS list shape).

    uv run python videos/015-math-big-picture/scripts/export_tokens.py           # check, print tables, write json
    uv run python videos/015-math-big-picture/scripts/export_tokens.py --check   # check only; exit 1 on a failure

Checks
- WCAG 2.x contrast on the stage (#000): every text color at least 4.5:1; graphics-only tokens at least 3:1
  (WCAG 1.4.11). Also printed: a text color dimmed to opacity 0.4 (old equation lines), composited in linear
  light the way aion's compositor does it.
- Color-blind separation of the six pillar hues: CIEDE2000 between every pair, at least 20 in normal vision and at
  least 10 under simulated deuteranopia, protanopia and tritanopia (Machado, Oliveira & Fernandes 2009, severity 1,
  applied in linear RGB as colorspacious does). The circle's warm white must also stay 10 apart from every pillar.
- Each pillar's distance (CIEDE2000) from the Design System hue it comes from. The DS hues as given fail the CVD
  check, and so does every set of six DS hues, so theme.py keeps each pillar in its DS hue family with the smallest
  change that passes (search: scipy differential evolution over L*, C*, h per pillar; at most 4.0).
If a pillar check fails, the script tries every single swap to an unused Design System hue and prints the ones that
pass, widest margin first. theme.py stays the only source of truth: apply a change there and run this again.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parent
sys.path.insert(0, str(VIDEO))

from theme import GLYPHS, PILLARS, theme  # noqa: E402

DS_NAME = "Aion YouTube Design System First"
DS_URL = "https://claude.ai/artifact/UjKmD2Ly4RSgWq3opzcMPs"
DS_HUES = {  # project/tokens.json, color tokens hue-* (stage theme)
    "hue-red": "#FF5A4E", "hue-orange": "#FF9F3D", "hue-gold": "#FFD17E", "hue-lime": "#A6E35A",
    "hue-teal": "#36D6B0", "hue-cyan": "#22D3EE", "hue-blue": "#5FB6FF", "hue-violet": "#B58CFF",
    "hue-pink": "#FF6FA8", "hue-magenta": "#FF3D9A",
}
STAGE = "#000000"
TEXT_MIN, GRAPHIC_MIN = 4.5, 3.0
DE_NORMAL_MIN, DE_CVD_MIN = 20.0, 10.0
DIM = 0.3  # opacity of an old, dimmed equation line (opacity-dim)
DS_FAMILY = {"foundations": "hue-blue", "quantity": "hue-gold", "structure": "hue-violet", "space": "hue-teal",
             "change": "hue-orange", "uncertainty": "hue-pink", "alert": "hue-red"}
DS_SHIFT_MAX = 4.5  # largest CIEDE2000 step a pillar may take from its DS hue

# --------------------------------------------------------------------------------------------- colour science
MACHADO = {  # Machado et al. 2009, severity 1.0; rows act on linear RGB
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}
SRGB_TO_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750],
                        [0.0193339, 0.1191920, 0.9503041]])
D65 = np.array([0.95047, 1.0, 1.08883])


def hex_rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def to_linear(c: np.ndarray) -> np.ndarray:
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


def luminance(h: str, alpha: float = 1.0) -> float:
    """WCAG relative luminance; `alpha` composites the color over black in linear light (aion's compositor)."""
    return float(alpha * np.dot([0.2126, 0.7152, 0.0722], to_linear(hex_rgb(h))))


def contrast(fg: str, bg: str = STAGE, alpha: float = 1.0) -> float:
    a, b = luminance(fg, alpha), luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def simulate(h: str, cvd: str | None) -> np.ndarray:
    """Linear RGB of `h` as seen with the given deficiency (None = normal vision), clipped to the gamut."""
    lin = to_linear(hex_rgb(h))
    return lin if cvd is None else np.clip(MACHADO[cvd] @ lin, 0.0, 1.0)


def lab(lin: np.ndarray) -> np.ndarray:
    xyz = SRGB_TO_XYZ @ lin / D65
    d = 6 / 29
    f = np.where(xyz > d ** 3, np.cbrt(xyz), xyz / (3 * d * d) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def ciede2000(lab1, lab2) -> float:
    """CIEDE2000 colour difference (Sharma, Wu & Dalal 2005), kL = kC = kH = 1."""
    L1, a1, b1 = (float(v) for v in lab1)
    L2, a2, b2 = (float(v) for v in lab2)
    cb = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(cb ** 7 / (cb ** 7 + 25.0 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0
    dlp, dcp = L2 - L1, c2p - c1p
    if c1p * c2p == 0:
        dhp = 0.0
    else:
        dhp = h2p - h1p
        dhp = dhp - 360 if dhp > 180 else dhp + 360 if dhp < -180 else dhp
    dHp = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp / 2))
    lbp, cbp = (L1 + L2) / 2, (c1p + c2p) / 2
    if c1p * c2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dtheta = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    rc = 2 * math.sqrt(cbp ** 7 / (cbp ** 7 + 25.0 ** 7))
    sl = 1 + 0.015 * (lbp - 50) ** 2 / math.sqrt(20 + (lbp - 50) ** 2)
    sc, sh = 1 + 0.045 * cbp, 1 + 0.015 * cbp * t
    rt = -math.sin(math.radians(2 * dtheta)) * rc
    return math.sqrt((dlp / sl) ** 2 + (dcp / sc) ** 2 + (dHp / sh) ** 2 + rt * (dcp / sc) * (dHp / sh))


def _self_test() -> None:
    """Pairs from Sharma et al. 2005, table 1, and a sanity check of the CVD matrices (white stays white)."""
    cases = [((50, 2.6772, -79.7751), (50, 0, -82.7485), 2.0425), ((50, 0, 0), (50, -1, 2), 2.3669),
             ((50, 2.49, -0.001), (50, -2.49, 0.0009), 7.1792),
             ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644),
             ((22.7233, 20.0904, -46.6940), (23.0331, 14.9730, -42.5619), 2.0373),
             ((2.0776, 0.0795, -1.1350), (0.9033, -0.0636, -0.5514), 0.9082)]
    for x, y, want in cases:
        got = ciede2000(x, y)
        assert abs(got - want) < 1e-4, (x, y, got, want)
    for m in MACHADO.values():
        assert np.allclose(m.sum(axis=1), 1.0, atol=1e-5)
    assert abs(contrast("#FFFFFF") - 21.0) < 1e-9


CONDITIONS = (("normal", None), ("deutan", "deutan"), ("protan", "protan"), ("tritan", "tritan"))


def separation(hexes: dict[str, str]) -> dict[str, tuple[float, str, str]]:
    """Min pairwise CIEDE2000 per vision condition → (value, name_a, name_b)."""
    out = {}
    for cond, cvd in CONDITIONS:
        labs = {k: lab(simulate(v, cvd)) for k, v in hexes.items()}
        best = (1e9, "", "")
        for a, b in itertools.combinations(hexes, 2):
            d = ciede2000(labs[a], labs[b])
            best = min(best, (d, a, b))
        out[cond] = best
    return out


def pair_table(hexes: dict[str, str]) -> list[dict]:
    rows = []
    for a, b in itertools.combinations(hexes, 2):
        row = {"pair": f"{a}/{b}"}
        for cond, cvd in CONDITIONS:
            row[cond] = round(ciede2000(lab(simulate(hexes[a], cvd)), lab(simulate(hexes[b], cvd))), 1)
        rows.append(row)
    return rows


def passes(sep) -> bool:
    return sep["normal"][0] >= DE_NORMAL_MIN and all(sep[c][0] >= DE_CVD_MIN for c in ("deutan", "protan", "tritan"))


def margin(sep) -> float:
    return min(sep["normal"][0] - DE_NORMAL_MIN, *(sep[c][0] - DE_CVD_MIN for c in ("deutan", "protan", "tritan")))


def search_swaps(hexes: dict[str, str]) -> list[tuple[float, str, str, str]]:
    """Every single swap of a pillar to an unused DS hue (red is reserved for `alert`) that passes."""
    used = {v.upper() for v in hexes.values()}
    free = {k: v for k, v in DS_HUES.items() if v.upper() not in used and k != "hue-red"}
    hits = []
    for pillar in hexes:
        for name, value in free.items():
            trial = dict(hexes, **{pillar: value})
            sep = separation(trial)
            if passes(sep):
                hits.append((margin(sep), pillar, name, value))
    return sorted(hits, reverse=True)


# ----------------------------------------------------------------------------------------------------- tokens
def ds_ref(h: str) -> str | None:
    return next((k for k, v in DS_HUES.items() if v.upper() == h.upper()), None)


COLOR_USAGE = {
    "bg": ("graphic", "The stage in every frame. Pure black; no gradient, texture, vignette or grain."),
    "text": ("text", "Primary text, operators, digits and brackets in equations, results."),
    "muted": ("text", "Secondary labels, tick numbers, axis names, HUD labels, a parked tracker glyph."),
    "faint": ("decorative", "The solid fill of Hamilton's flat stone-grey card (ch3_s07); otherwise unused "
                              "(map_off does its jobs). Never text; only C.text and C.muted sit on it."),
    "grid": ("graphic", "Classic plane: unit grid lines (BASE)."),
    "grid_minor": ("decorative", "Classic plane: minor grid lines (BASE)."),
    "axis": ("graphic", "Classic plane: axes (BASE)."),
    "frame": ("graphic", "The thin border of a framed panel (`panel`) and of the key-idea frame."),
    "foundations": ("text", "Foundations pillar (Ch1): sets, logic, the glyph ∈, braces of set-builder notation, "
                            "the inside-set tint at opacity-fill. Map node 0 (6 o'clock)."),
    "quantity": ("text", "Quantity pillar (Ch2): π whenever π is the quantity (the locked estimate, the width "
                         "tick π, the π of 2/π), 22/7, 355/113, the inscribed square and √2. Map node 1."),
    "structure": ("text", "Structure pillar (Ch3): rotations e^{iθ}, their arcs, the group C6 (the map's own turns), "
                          "quaternions. Map node 2."),
    "space": ("text", "Space pillar (Ch4): χ = V − E + F, the torus wireframe, rubber-band shapes, the Tube map, "
                      "the (θ, x) rectangle of Ch6. Map node 3 (12 o'clock)."),
    "change": ("text", "Change pillar (Ch5): d/dr, the rings and their unrolled strips, slopes, the sine arch of Ch6 "
                       "and its area, e. Map node 4."),
    "uncertainty": ("text", "Uncertainty pillar (Ch6): P, the needles (crossing ones at full strength), the dots of "
                            "the throws, running shares and estimates. Map node 5."),
    "circle": ("text", "THE recurring circle of every chapter: the needle-tip trace, x² + y² = 25, the unit circle, "
                       "the two loops on the torus, the outer ring of the unrolled disk, the hub of the map. "
                       "Warm white so it is never confused with plain text."),
    "map_off": ("graphic", "Unlit map: the ring track, unlit node rings, unlit chords, unlit mini-map dots, empty "
                           "tracker slots; the floorboard cracks under the needles. Graphics only, never text."),
    "alert": ("text", "The video's one contradiction (Ch2, ch2_s04): the clash 'p even, q even' struck through. "
                      "Used once, never decoration."),
}


def color_tokens() -> list[dict]:
    out = [{"name": "stage", "value": {"stage": STAGE}, "usage": "Alias of bg (DS name)."}]
    for name, (kind, usage) in COLOR_USAGE.items():
        h = getattr(theme, name)
        tok = {"name": name, "value": {"stage": h.upper()}, "usage": usage, "kind": kind}
        fam = DS_FAMILY.get(name)
        if fam:
            d = ciede2000(lab(simulate(h, None)), lab(simulate(DS_HUES[fam], None)))
            tok["ds"] = {"token": fam, "value": DS_HUES[fam], "de2000": round(d, 1)}
            tok["usage"] = f"{usage} DS {fam} {DS_HUES[fam]}" + (f", tuned by ΔE00 {d:.1f}." if d > 0.05 else ".")
        out.append(tok)
    return out


FS = "font_size (Manim) ≈ cap height in px at 1080p: 28 → 27 px, 48 → 46 px, 72 → 69 px (measured)."
TYPE_TOKENS = [
    {"name": "math-hero", "value": {"face": "CM roman", "tex": "MathTex / Eqn", "font_size": "72–96"},
     "usage": "The one hero equation of a beat: x² + y² = 25, dA/dr = 2πr, e^{iπ} + 1 = 0. One per frame."},
    {"name": "math-working", "value": {"face": "CM roman", "tex": "MathTex / Eqn", "font_size": 48},
     "usage": "Working maths: equation stacks, the worked example of each chapter, counts."},
    {"name": "math-label", "value": {"face": "CM roman", "tex": "MathTex", "font_size": "34–40", "min": 28},
     "usage": "Point and tick labels inside a plot: (3, 4), 22/7, π/3. Never under 28."},
    {"name": "glyph", "value": {"face": "CM roman", "tex": "MathTex", "font_size": 44},
     "usage": "Map-node key glyphs: " + "  ".join(GLYPHS.values()) + ". Drawn in the pillar hue once lit; "
              "36 in the tracker, 96 on a chapter card."},
    {"name": "label", "value": {"face": "CM sans", "tex": r"\textsf{}", "font_size": "30–34", "min": 28},
     "usage": "Key words and tags (inside, on, outside, rule), axis words, the takeaway words. Four words at most."},
    {"name": "caps-name", "value": {"face": "CM small caps", "tex": r"\textsc{}", "font_size": "32–36"},
     "usage": "Lower thirds (G. Cantor · 1874) at 34, pillar names beside map nodes (32)."},
    {"name": "caps-card", "value": {"face": "CM small caps", "tex": r"\textsc{}", "font_size": "64–80"},
     "usage": "Chapter card title (the pillar name), the video title."},
    {"name": "caps-eyebrow", "value": {"face": "CM small caps", "tex": r"\textsc{}", "font_size": "28–30"},
     "usage": "The key-idea eyebrow (28, C.muted); a small header over a card or panel."},
    {"name": "readout", "value": {"face": "CM sans digits", "tex": r"\textsf{} in \makebox columns",
                                  "font_size": "34 (HUD) – 48 (subject)"},
     "usage": "Live counters and HUDs (throws, crossings, 2N / H). CM digits share one width (tabular), so counters "
              "never jitter; thousands split by a thin space (30 331)."},
]

U = 135.0  # px per world unit at 1080p (frame height 8 units)


def _sp(name, units, usage):
    return {"name": name, "value": {"units": units, "px_1080": round(units * U)}, "usage": usage}


SPACING_TOKENS = [
    _sp("space-1", 0.06, "Value to its unit, tick to its number."),
    _sp("space-2", 0.12, "Dot to its label, chip padding."),
    _sp("space-3", 0.18, "Equation to its tag; line gap in an equation stack is space-6."),
    _sp("space-4", 0.24, "Inner padding of the key-idea frame and the takeaway."),
    _sp("space-6", 0.36, "Between lines of an equation stack; between panels of a split view."),
    _sp("space-8", 0.48, "Between a chapter-card title and its glyph."),
    _sp("margin", float(theme.margin), "BASE edge margin: nothing drawn closer to the frame edge."),
    _sp("safe-margin", 0.71, "Title-safe inset for text and HUD (DS safe-margin, 96 px). Lower thirds sit on it."),
    _sp("map-radius", 2.75, "Map of Math: ring radius (node centres). Centre (0, 0)."),
    _sp("node-radius", 0.4, "Map node disk radius; the glyph sits inside at `glyph` size (≤ 1.5 × radius wide)."),
    _sp("hub-radius", 1.375, "The hub circle = THE circle: inscribed in the hexagram of skip-one chords "
                             "(= map-radius / 2). The cold open's needle tips trace it."),
    _sp("minimap-radius", 0.3, "Mini-map ring radius, top-right; lit dots 0.062, unlit 0.045, current ringed 0.125."),
    {"name": "minimap-centre", "value": {"units": [6.05, 3.0], "px_1080": [1777, 135]},
     "usage": "Mini-map centre (world units / px from top-left). Inside safe-margin on both edges."},
    _sp("tracker-slot", 0.25, "e · i · π tracker slot radius (Ch3–Ch7); slots 0.66 apart from the top-left safe corner."),
    _sp("board", 0.6, "Floorboard spacing = needle length (Buffon with l = d). Seed 1777, placement seed 1778."),
]

STROKE_TOKENS = [
    {"name": "hairline", "value": {"stroke_width": 1.0, "px_1080": 1.35}, "usage": "Minor grid."},
    {"name": "thin", "value": {"stroke_width": float(theme.thin), "px_1080": round(theme.thin * 1.35, 1)},
     "usage": "Ticks, unlit chords, panel frames, the map track."},
    {"name": "chord", "value": {"stroke_width": 2.4, "px_1080": 3.2}, "usage": "Lit chords of the map (two-hue gradient)."},
    {"name": "node", "value": {"stroke_width": 3.0, "px_1080": 4.1}, "usage": "Lit map node rings (unlit rings 2.0, map_off)."},
    {"name": "curve", "value": {"stroke_width": float(theme.stroke), "px_1080": round(theme.stroke * 1.35, 1)},
     "usage": "Curves, arcs, square, rings, plotted estimates (BASE stroke)."},
    {"name": "hero", "value": {"stroke_width": 5.0, "px_1080": 6.8}, "usage": "THE circle, whenever it is the subject."},
    {"name": "needle", "value": {"px_1080": "3.0 (skia)"},
     "usage": "Needles drawn with skia (round caps); floorboard cracks 2 px in map_off."},
]

OPACITY_TOKENS = [
    {"name": "opacity-fill", "value": 0.06, "usage": "Set tints: the inside of the circle (Ch1), overlapping disks, a lit "
                                                     "node's disk; the plan's '15 percent' disk (ch4_s03). aion composites layers in linear light: 0.06 already "
                                                     "reads as a clear tint. Over another shape of the same Manim layer "
                                                     "Cairo blends in sRGB (about 11× darker), so a tinted disk that must "
                                                     "hide what is under it uses the solid colour tint(hue, 0.06) at "
                                                     "opacity 1 (style_frames.py)."},
    {"name": "opacity-region", "value": 0.1, "usage": "The one shaded region a beat is about: the area under the sine "
                                                      "arch (Ch6; the plan's '30 percent')."},
    {"name": "opacity-ghost", "value": 0.25, "usage": "Ghost of a previous state, residue of a morph."},
    {"name": "opacity-dim", "value": DIM, "usage": "Old equation lines (dimmed, never deleted), dots outside a region, "
                                                    "needles that miss; the plan's 'older lines dimming to 40 percent' "
                                                    "(ch2_s04). In linear light 0.4 still reads bright; at 0.3 a line "
                                                    "reads clearly dimmed and white text keeps 7:1."},
    {"name": "opacity-floor", "value": 0.4, "usage": "The cold-open floor (cracks and resting needles) after 'no circle' (the plan's 'dims to 40%')."},
    {"name": "opacity-chord", "value": 0.85, "usage": "Lit chords of the map (a lit ring arc between neighbours: 0.9)."},
]

MOTION_TOKENS = [
    {"name": "lead", "value": {"s": float(theme.lead)}, "usage": "Motion lands on the beat and starts this early."},
    {"name": "micro", "value": {"s": 0.3, "ease": "smooth"}, "usage": "Fades, highlights, a tag in or out."},
    {"name": "standard", "value": {"s": 0.8, "ease": "easy_ease"},
     "usage": "Moves, transforms, an equation term arriving, a dot sliding to its place."},
    {"name": "hero", "value": {"s": "1.5–2.5", "ease": "easy_ease"},
     "usage": "Signature moves: the needles sliding into the circle, the map turn, rings unrolling, a node opening."},
    {"name": "stagger", "value": {"s": 0.05}, "usage": "Between members of a group: needles, rings, terms, nodes."},
    {"name": "hold", "value": {"s": "1.5–2.5"}, "usage": "Hold after every signature shot before the next change."},
    {"name": "map-turn", "value": {"deg": 60, "s": 1.8, "ease": "easy_ease"},
     "usage": "The ring turns counter-clockwise by one sixth so the next pillar arrives at 6 o'clock."},
    {"name": "push", "value": {"max_zoom": 1.15, "s": "2–3", "ease": "easy_ease"},
     "usage": "Camera push-ins on payoffs only; never more than 1.15×."},
    {"name": "banned", "value": ["linear", "out_back", "out_elastic", "spring pops", "shake", "ZoomBlur", "wipes"],
     "usage": "Never used for motion. Counters change value per frame (no tween)."},
]


# --------------------------------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="check only, do not write design/tokens.json")
    args = ap.parse_args()
    _self_test()

    ok = True
    print(f"\nWCAG contrast on {STAGE}  (text ≥ {TEXT_MIN}:1, graphics ≥ {GRAPHIC_MIN}:1; dim = opacity {DIM})")
    print(f"{'token':<13} {'hex':<9} {'kind':<11} {'ratio':>6} {'dim':>6}  result")
    contrast_rows = []
    for name, (kind, _) in COLOR_USAGE.items():
        if name == "bg":
            continue
        h = getattr(theme, name).upper()
        r, rd = contrast(h), contrast(h, alpha=DIM)
        need = TEXT_MIN if kind == "text" else GRAPHIC_MIN if kind == "graphic" else 0.0
        good = r >= need
        ok &= good
        res = "pass" if good else "FAIL"
        if kind == "decorative":
            res = "decorative (no minimum)"
        print(f"{name:<13} {h:<9} {kind:<11} {r:>6.2f} {rd:>6.2f}  {res}")
        contrast_rows.append({"token": name, "hex": h, "kind": kind, "ratio": round(r, 2), "dim_ratio": round(rd, 2),
                              "min": need, "pass": good})

    pillars = {p: getattr(theme, p).upper() for p in PILLARS}
    sep = separation(pillars)
    print(f"\nPillar separation, CIEDE2000 (normal ≥ {DE_NORMAL_MIN:g}; deutan/protan/tritan ≥ {DE_CVD_MIN:g})")
    rows = pair_table(pillars)
    print(f"{'pair':<26}" + "".join(f"{c:>8}" for c, _ in CONDITIONS))
    for row in rows:
        flags = "".join(f"{row[c]:>7.1f}{'*' if row[c] < (DE_NORMAL_MIN if c == 'normal' else DE_CVD_MIN) else ' '}"
                        for c, _ in CONDITIONS)
        print(f"{row['pair']:<26}{flags}")
    print(f"{'minimum':<26}" + "".join(f"{sep[c][0]:>7.1f} " for c, _ in CONDITIONS))
    for c, _ in CONDITIONS:
        print(f"  {c:<7} min {sep[c][0]:5.1f}  ({sep[c][1]} / {sep[c][2]})")
    sep_ok = passes(sep)
    ok &= sep_ok
    print("pillar separation:", "pass" if sep_ok else "FAIL  (* marks a pair under its minimum)")
    swaps = []
    if not sep_ok:
        swaps = search_swaps(pillars)
        print("single DS-hue swaps that pass (margin, pillar → hue):")
        for m_, p, n, v in swaps[:8] or []:
            print(f"  {m_:+5.1f}  {p} → {n} {v}")
        if not swaps:
            print("  none: a two-hue swap or a lightness change is needed")

    print(f"\nTHE circle against every pillar (CIEDE2000; at least {DE_CVD_MIN:g} in every condition)")
    print(f"{'pair':<26}" + "".join(f"{c:>8}" for c, _ in CONDITIONS))
    circle_rows = []
    for p in PILLARS:
        vals = {c: round(ciede2000(lab(simulate(theme.circle, cvd)), lab(simulate(pillars[p], cvd))), 1)
                for c, cvd in CONDITIONS}
        good = min(vals.values()) >= DE_CVD_MIN
        ok &= good
        circle_rows.append({"pair": f"circle/{p}", **vals, "pass": good})
        print(f"{'circle/' + p:<26}" + "".join(f"{vals[c]:>8.1f}" for c, _ in CONDITIONS) + ("" if good else "  FAIL"))

    print(f"\nDistance from the Design System hue (CIEDE2000, normal vision; at most {DS_SHIFT_MAX:g})")
    shift_rows = []
    for p in (*PILLARS, "alert"):
        fam, h = DS_FAMILY[p], getattr(theme, p).upper()
        d = ciede2000(lab(simulate(h, None)), lab(simulate(DS_HUES[fam], None)))
        good = d <= DS_SHIFT_MAX
        ok &= good
        shift_rows.append({"token": p, "hex": h, "ds": fam, "ds_hex": DS_HUES[fam], "de2000": round(d, 1),
                           "pass": good})
        print(f"  {p:<12} {h}  from {fam:<11} {DS_HUES[fam]}  ΔE00 {d:4.1f}  {'pass' if good else 'FAIL'}")

    extra = {"circle": theme.circle, "text": theme.text, "grid": BASE_GRID, "alert": theme.alert,
             "map_off": theme.map_off}
    neighbours = [("circle", "text"), ("grid", "foundations"), ("alert", "change"), ("alert", "uncertainty"),
                  ("map_off", "foundations")]
    print("\nNeighbour pairs (information; these never carry meaning alone):")
    neigh_rows = []
    for a, b in neighbours:
        ha, hb = extra.get(a) or pillars[a], extra.get(b) or pillars[b]
        vals = {c: round(ciede2000(lab(simulate(ha, cvd)), lab(simulate(hb, cvd))), 1) for c, cvd in CONDITIONS}
        neigh_rows.append({"pair": f"{a}/{b}", **vals})
        print(f"  {a + '/' + b:<24}" + "".join(f"{vals[c]:>8.1f}" for c, _ in CONDITIONS))

    if not args.check:
        out = VIDEO / "design" / "tokens.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        doc = {
            "name": "015 Fundamentals of Math: The Big Picture",
            "version": 1,
            "extends": {"look": "aion BASE (Classic)", "hues": f"{DS_NAME} ({DS_URL})"},
            "note": "World units: frame height 8 = 1080 px (1 unit = 135 px). " + FS,
            "color": {"themes": [{"id": "stage", "name": "Stage"}], "tokens": color_tokens()},
            "type": {"families": {"roman": "Computer Modern Roman (LaTeX)", "sans": r"Computer Modern Sans (\textsf)",
                                  "caps": r"Computer Modern small caps (\textsc)"},
                     "tokens": TYPE_TOKENS},
            "spacing": {"tokens": SPACING_TOKENS},
            "stroke": {"note": "Manim stroke_width; 1 stroke_width ≈ 1.35 px at 1080p.", "tokens": STROKE_TOKENS},
            "opacity": {"tokens": OPACITY_TOKENS},
            "motion": {"tokens": MOTION_TOKENS},
            "map": {"order": list(PILLARS), "glyphs": GLYPHS,
                    "angles_deg": {p: -90 - 60 * k for k, p in enumerate(PILLARS)},
                    "note": "Foundations at 6 o'clock, then clockwise. Each chapter turns the ring +60° "
                            "(counter-clockwise) so the next pillar arrives at 6 o'clock."},
            "checks": {"contrast": contrast_rows,
                       "pillar_separation": {"method": "CIEDE2000; CVD by Machado et al. 2009, severity 1",
                                             "min_normal": DE_NORMAL_MIN, "min_cvd": DE_CVD_MIN,
                                             "minimum": {c: {"de": round(v[0], 1), "pair": [v[1], v[2]]}
                                                         for c, v in sep.items()},
                                             "pairs": rows, "pass": sep_ok,
                                             "swaps": [{"margin": round(m_, 1), "pillar": p, "to": n, "hex": v}
                                                       for m_, p, n, v in swaps[:8]]},
                       "circle": circle_rows, "ds_shift": shift_rows,
                       "neighbours": neigh_rows, "pass": bool(ok)},
        }
        out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        print(f"\nwrote {out.relative_to(VIDEO.parent.parent)}")
    print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
    return 0 if ok else 1


BASE_GRID = theme.grid

if __name__ == "__main__":
    sys.exit(main())
