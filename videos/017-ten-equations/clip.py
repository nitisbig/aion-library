"""Play a baked video file as a FramesLayer source: `FramesLayer(Clip(path), ...)` (from video 012), and
`LoopClip`, which plays a seamless loop forever (the live wall tiles, assets/tiles/T01.mp4 …).

Frames are decoded by one persistent ffmpeg pipe that reads forward, so a scene rendered in order costs one decode
per frame. A jump backward (or far forward) restarts the pipe with an accurate seek. Times outside the clip hold the
first or last frame. The pipe is opened lazily and dropped on pickling, so each render worker opens its own.

Example:
    s.add(FramesLayer(Clip(VIDEO / "assets/voyage_pc.mp4"), height=8.0, z=-20, during=[(T.start, T.strips + 0.5)]))
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np


class Clip:
    def __init__(self, path: str | Path, offset: float = 0.0):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path} is missing: bake it first (scripts/make_tile_clips.py)")
        info = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
             "stream=width,height,r_frame_rate,nb_read_packets", "-of", "json", str(self.path)],
            capture_output=True, check=True, text=True).stdout)["streams"][0]
        num, den = info["r_frame_rate"].split("/")
        self.fps = float(num) / float(den)
        self.w, self.h, self.n = int(info["width"]), int(info["height"]), int(info["nb_read_packets"])
        self.offset = offset
        self._proc = None
        self._k = -1
        self._img = None

    def __getstate__(self):
        d = dict(self.__dict__)
        d.update(_proc=None, _k=-1, _img=None)
        return d

    def _open(self, k):
        self.close()
        self._proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", f"{k / self.fps:.6f}", "-i", str(self.path), "-f", "rawvideo",
             "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
        self._k = k - 1

    def _next(self):
        size = self.w * self.h * 4
        buf = self._proc.stdout.read(size)
        if len(buf) < size:                          # ran off the end: hold what we have
            return self._img
        self._k += 1
        self._img = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 4)
        return self._img

    def __call__(self, t: float) -> np.ndarray:
        k = int(np.clip(round((t - self.offset) * self.fps), 0, self.n - 1))
        if k == self._k and self._img is not None:
            return self._img
        if self._proc is None or k < self._k or k > self._k + 90:
            self._open(k)
        while self._k < k:
            before = self._k
            self._next()
            if self._k == before:                    # end of stream
                break
        return self._img

    def close(self):
        if self._proc is not None:
            self._proc.kill()
            self._proc.wait()
            self._proc = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


class LoopClip(Clip):
    """A clip baked to loop seamlessly: time wraps modulo its length; `offset` sets the phase.

    Example:
        s.add(FramesLayer(LoopClip(TILE_DIR / "T01.mp4", offset=0.4), height=1.37, blend="screen"))
    """

    def __call__(self, t: float) -> np.ndarray:
        k = int(round((t - self.offset) * self.fps)) % self.n
        if k == self._k and self._img is not None:
            return self._img
        if self._proc is None or k < self._k or k > self._k + 90:
            self._open(k)
        while self._k < k:
            before = self._k
            self._next()
            if self._k == before:
                break
        return self._img
