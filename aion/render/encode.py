"""ffmpeg encoders fed raw RGB frames on stdin.

    with Encoder("out/s01.mp4", (1920, 1080), 60, codec="final") as enc:
        enc.write(rgb_uint8)

Presets:
- "final":   libx264 CRF 16, yuv420p, BT.709 tagged + converted (YouTube-safe)
- "preview": h264_vaapi on the Radeon R4 if available, else libx264 ultrafast
- "ffv1":    lossless RGBA intermediates (layer caches)
- "png":     image sequence (pattern path, e.g. frames/%05d.png)
"""

from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

__all__ = ["Encoder", "vaapi_available"]

BT709 = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]


@lru_cache(maxsize=1)
def vaapi_available() -> bool:
    if not os.path.exists("/dev/dri/renderD128") or not shutil.which("ffmpeg"):
        return False
    try:
        p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-vaapi_device", "/dev/dri/renderD128",
                            "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.1", "-vf", "format=nv12,hwupload",
                            "-c:v", "h264_vaapi", "-f", "null", "-"], capture_output=True, timeout=20)
        return p.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


class Encoder:
    """Stream RGB(A) frames into ffmpeg (x264 final / ultrafast preview / ffv1 / png), optionally muxing audio.

    Example:
        with Encoder("out.mp4", (1280, 720), 30, codec="preview") as enc:
            for i in range(90): enc.write(comp.frame(i / 30, i))
    """
    def __init__(self, path: str | Path, size: tuple[int, int], fps: float, codec: str = "final",
                 alpha: bool = False, crf: int = 16, audio: str | Path | None = None,
                 audio_offset: float = 0.0, duration: float | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.size, self.fps, self.alpha = size, fps, alpha
        w, h = size
        pix = "rgba" if alpha else "rgb24"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", pix,
               "-s", f"{w}x{h}", "-r", f"{fps:g}", "-i", "-"]
        vaapi = codec == "preview" and vaapi_available()
        if vaapi:
            cmd[1:1] = ["-vaapi_device", "/dev/dri/renderD128"]
        if audio is not None:
            cmd += ["-ss", f"{audio_offset:.6f}", "-i", str(audio)]
        if codec == "final":
            cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264",
                    "-preset", "slow", "-crf", str(crf), "-tune", "animation", *BT709]
        elif codec == "preview":
            if vaapi:
                cmd += ["-vf", "scale=out_color_matrix=bt709,format=nv12,hwupload", "-c:v", "h264_vaapi",
                        "-qp", "24", *BT709]
            else:
                cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264",
                        "-preset", "ultrafast", "-crf", "23", *BT709]
        elif codec == "ffv1":
            cmd += ["-c:v", "ffv1", "-level", "3", "-pix_fmt", "rgba" if alpha else "bgr0"]
        elif codec == "png":
            cmd += ["-c:v", "png"]
        else:
            raise ValueError(f"unknown codec {codec!r}")
        if audio is not None:
            cmd += ["-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k"]
            if duration is not None:
                cmd += ["-t", f"{duration:.6f}"]
        cmd += ["-movflags", "+faststart"] if self.path.suffix in (".mp4", ".mov") else []
        cmd.append(str(self.path))
        self.cmd = cmd
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.frames = 0

    def write(self, frame: np.ndarray) -> None:
        assert frame.dtype == np.uint8 and frame.shape[:2] == (self.size[1], self.size[0]), frame.shape
        try:
            self.proc.stdin.write(np.ascontiguousarray(frame).tobytes())
        except BrokenPipeError:
            raise RuntimeError(f"ffmpeg died: {self.proc.stderr.read().decode()[-800:]}") from None
        self.frames += 1

    def close(self) -> Path:
        self.proc.stdin.close()
        err = self.proc.stderr.read().decode()
        if self.proc.wait() != 0:
            raise RuntimeError(f"ffmpeg failed ({' '.join(self.cmd[:12])} ...):\n{err[-1500:]}")
        return self.path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self.close()
        else:
            self.proc.kill()
