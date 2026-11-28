"""Bake the ten live wall tiles (assets/tiles/T01.mp4 … T10.mp4): seamless loops of each chapter's own motion.

Render each 3 s window first (outro.LIVE; 720p30 drafts land in out/):
    uv run aion preview 017 <scene> --draft --range <a> <b>
then run from the repo root:
    uv run python videos/017-ten-equations/scripts/make_tile_clips.py

Each frame is cropped like the still tile (outro.KEYFRAMES: centre and width in world units), resized to 640 px,
feathered to black at its edges, given the hue rule under it, and padded like the PNG tiles. The last 0.5 s
crossfades into the first, so the clip loops without a jump. Black stands for transparent: the scenes draw the
tiles with blend='screen' over the black stage.
"""
import subprocess
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

FEATHER, RULE_H, RULE_W, XFADE = 22, 5, 0.3, 15


def frames(path):
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    w, h = map(int, info.strip().split(","))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def tile_frame(img, i):
    scene, t, cx, cy, w = outro.KEYFRAMES[i]
    H, W = img.shape[:2]
    ppu = W / (2 * 64 / 9)
    h = w * 9 / 16
    box = (int((cx - w / 2 + 64 / 9) * ppu), int((4 - cy - h / 2) * ppu),
           int((cx + w / 2 + 64 / 9) * ppu), int((4 - cy + h / 2) * ppu))
    pic = np.asarray(Image.fromarray(img).crop(box).resize((outro.PX_W, outro.PX_W * 9 // 16), Image.LANCZOS),
                     np.float32)
    ph, pw = pic.shape[:2]
    ramp = lambda n: np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / FEATHER, 0, 1)
    a = np.outer(ramp(ph), ramp(pw))
    a = (a * a * (3 - 2 * a))[..., None]
    gap = int(outro.RULE_GAP / outro.TW * outro.PX_W)
    out = np.zeros((outro.PAD + ph + gap + RULE_H + outro.PAD + 1, pw, 3), np.float32)   # +1: even height
    out[outro.PAD:outro.PAD + ph] = pic * a
    hue = str(getattr(C, CHAPTERS[i])).lstrip("#")
    y = outro.PAD + ph + gap
    out[y:y + RULE_H, :int(RULE_W * pw)] = [int(hue[k:k + 2], 16) for k in (0, 2, 4)]
    return out


def main():
    only = [int(a) - 1 for a in sys.argv[1:]] or range(10)
    for i in only:
        scene, a, b = outro.LIVE[i]
        src = HERE / f"out/draft_{scene}_{a:g}-{b:g}.mp4"
        F = np.stack([tile_frame(f, i) for f in frames(src)])
        n = len(F) - XFADE
        loop = F[:n].copy()
        for j in range(XFADE):                                   # the tail crossfades into the head
            w = j / XFADE
            loop[j] = F[j] * w + F[n + j] * (1 - w)
        dst = outro.TILE_DIR / f"T{i + 1:02d}.mp4"
        hh, ww = loop.shape[1:3]
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ww}x{hh}",
                              "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                              "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                              "-colorspace", "bt709", str(dst)], stdin=subprocess.PIPE)
        p.communicate(np.clip(loop, 0, 255).astype(np.uint8).tobytes())
        print(f"T{i + 1:02d}  {ww}x{hh}  {len(loop)} frames  ← {src.name}")


if __name__ == "__main__":
    main()
