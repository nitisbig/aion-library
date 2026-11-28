"""Build the ten wall tiles (assets/tiles/T01.png … T10.png) from 1080p stills of each chapter's key frame.

Render the stills first (one per outro.KEYFRAMES entry):
    uv run aion still 017 <scene> --final --at <time>
then run from the repo root:
    uv run python videos/017-ten-equations/scripts/make_tiles.py [--sheet out.png]

Each tile: a 16:9 crop of the still (centre and width from KEYFRAMES, world units), resized to 640 px, its edges
feathered into transparency (no border), and a short rule in the chapter hue under its left edge.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from aion.theme.tokens import activate  # noqa: E402
from theme import CHAPTERS, theme  # noqa: E402

activate(theme)
from aion import C  # noqa: E402

import outro  # noqa: E402

FEATHER = 22          # px at tile size
RULE_H, RULE_W = 5, 0.3
HI = (0,)             # tiles also saved at native resolution (T01: the intro dives into it)


def build(i, hi=False):
    """Tile i at PX_W wide, or (hi) at the still's native resolution with no hue rule (for the intro's dive)."""
    scene, t, cx, cy, w = outro.KEYFRAMES[i]
    src = Image.open(HERE / f"out/stills/{scene}@{t:07.2f}.png").convert("RGB")
    W, H = src.size
    ppu = W / (2 * 64 / 9)
    h = w * 9 / 16
    box = (int((cx - w / 2 + 64 / 9) * ppu), int((4 - cy - h / 2) * ppu),
           int((cx + w / 2 + 64 / 9) * ppu), int((4 - cy + h / 2) * ppu))
    crop = src.crop(box)
    if not hi:
        crop = crop.resize((outro.PX_W, outro.PX_W * 9 // 16), Image.LANCZOS)
    pic = np.asarray(crop).astype(np.float32)
    ph, pw = pic.shape[:2]
    fe = FEATHER * pw / outro.PX_W
    ramp = lambda n: np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / fe, 0, 1)
    a = np.outer(ramp(ph), ramp(pw))
    a = a * a * (3 - 2 * a)
    if hi:
        out = np.zeros((ph, pw, 4), np.uint8)
        out[..., :3] = pic.astype(np.uint8)
        out[..., 3] = (a * 255).astype(np.uint8)
        return out
    gap = int(outro.RULE_GAP / outro.TW * outro.PX_W)
    out = np.zeros((ph + gap + RULE_H, pw, 4), np.uint8)
    out[:ph, :, :3] = pic.astype(np.uint8)
    out[:ph, :, 3] = (a * 255).astype(np.uint8)
    hue = str(getattr(C, CHAPTERS[i])).lstrip("#")
    out[ph + gap:, :int(RULE_W * pw), :3] = [int(hue[k:k + 2], 16) for k in (0, 2, 4)]
    out[ph + gap:, :int(RULE_W * pw), 3] = 255
    pad = np.zeros((outro.PAD, pw, 4), np.uint8)               # transparent rows: a scaled tile's edge samples
    return np.concatenate([pad, out, pad], axis=0)             # never wrap the hue rule round to the top


def main():
    outro.TILE_DIR.mkdir(parents=True, exist_ok=True)
    tiles = []
    for i in range(10):
        img = build(i)
        Image.fromarray(img).save(outro.TILE_DIR / f"T{i + 1:02d}.png")
        tiles.append(img)
        print(f"T{i + 1:02d}  {img.shape[1]}x{img.shape[0]}")
    for i in HI:
        Image.fromarray(build(i, hi=True)).save(outro.TILE_DIR / f"T{i + 1:02d}_hi.png")
    if "--sheet" in sys.argv:
        rows = [np.concatenate(tiles[r * 5:(r + 1) * 5], axis=1) for r in range(2)]
        sheet = np.concatenate(rows, axis=0)
        bg = np.zeros_like(sheet[..., :3], np.float32)
        al = sheet[..., 3:4] / 255.0
        Image.fromarray((sheet[..., :3] * al + bg * (1 - al)).astype(np.uint8)).save(sys.argv[sys.argv.index("--sheet") + 1])


if __name__ == "__main__":
    main()
