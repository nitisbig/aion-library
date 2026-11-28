"""Check video 017's palette and export its design tokens to design/tokens.json.

    uv run python videos/017-ten-equations/scripts/export_tokens.py           # check, print, write json
    uv run python videos/017-ten-equations/scripts/export_tokens.py --check   # check only; exit 1 on a failure

Checks
- WCAG 2.x contrast on the stage (#000): text colors >= 4.5:1, graphics-only tokens >= 3:1.
- Color-blind separation of each GROUP (theme.GROUPS, the colours that share a frame in one chapter): CIEDE2000
  between every pair >= 20 in normal vision and >= 10 under simulated deuteranopia, protanopia and tritanopia
  (Machado, Oliveira & Fernandes 2009, severity 1, in linear RGB).
- The ten chapter hues: >= 15 in normal vision (reported only under CVD; the tile numbers carry the chapter there).
The colour-science helpers are copied from video 015's export_tokens.py (CIEDE2000 checked against Sharma 2005).
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

from theme import CHAPTERS, GROUPS, theme  # noqa: E402

STAGE = "#000000"
TEXT_MIN, GRAPHIC_MIN = 4.5, 3.0
DE_NORMAL_MIN, DE_CVD_MIN, DE_DIGITS_MIN = 20.0, 10.0, 15.0
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



TEXT_ROLES = ("text", "muted") + CHAPTERS + ("e_field", "charge_p", "charge_n", "data", "noise", "ill", "positive",
                                          "prior", "payoff", "bad")
GRAPHIC_ROLES = ("light", "mass", "grid", "axis", "frame", "grid_minor")


def col(name: str) -> str:
    v = getattr(theme, name, None)
    return v if v is not None else theme.roles[name]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    _self_test()
    fails = []
    print("contrast on #000")
    for r in TEXT_ROLES + GRAPHIC_ROLES:
        if r == "grid_minor":
            continue
        c = contrast(col(r))
        need = TEXT_MIN if r in TEXT_ROLES else GRAPHIC_MIN
        if c < need:
            fails.append(f"contrast {r} {c:.2f} < {need}")
        print(f"  {'✔' if c >= need else '✘'} {r:<10} {col(r)}  {c:5.2f}  (min {need})")
    groups = {}
    for g, roles in GROUPS.items():
        sep = separation({r: col(r) for r in roles})
        groups[g] = {k: round(v[0], 1) for k, v in sep.items()}
        ok = passes(sep)
        print(f"  {'✔' if ok else '✘'} {g:<18} " + "  ".join(f"{k} {v[0]:5.1f} ({v[1]}/{v[2]})" for k, v in sep.items()))
        if not ok:
            fails.append(f"group {g} fails the colour-blind check: {groups[g]}")
    csep = separation({r: col(r) for r in CHAPTERS})
    print("chapter hues (min CIEDE2000):", {k: (round(v[0], 1), v[1], v[2]) for k, v in csep.items()})
    if csep["normal"][0] < DE_DIGITS_MIN:
        fails.append(f"chapter hues too close in normal vision: {csep['normal']}")
    tokens = {
        "video": "017-ten-equations",
        "stage": {"bg": STAGE, "frame_px": [3840, 2160], "fps": 30, "world_units": [14.222, 8.0],
                  "px_per_unit_1080p": 135, "margin_u": theme.margin, "safe_inset_u": 0.71},
        "chapters": [{"tile": i + 1, "role": r, "hex": col(r)} for i, r in enumerate(CHAPTERS)],
        "color": [{"role": r, "hex": col(r), "contrast": round(contrast(col(r)), 2),
                   "use": "text" if r in TEXT_ROLES else "graphic"} for r in TEXT_ROLES + GRAPHIC_ROLES],
        "separation": {"groups": groups, "chapters": {k: round(v[0], 1) for k, v in csep.items()}},
        "glow": {"strength": theme.glow, "radius_px_1080p": theme.glow_r},
    }
    if not a.check:
        out = VIDEO / "design" / "tokens.json"
        out.write_text(json.dumps(tokens, indent=1, ensure_ascii=False) + "\n")
        print("wrote", out.relative_to(VIDEO.parent.parent))
    for f in fails:
        print("✘", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
