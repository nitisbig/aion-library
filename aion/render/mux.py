"""Concatenate chunk files and mux the master audio; verify durations."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

__all__ = ["concat", "mux_audio", "probe_durations"]


def concat(files: list[Path], out: Path) -> Path:
    """Stream-copy concat (all chunks share codec settings)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    lst = out.with_suffix(".concat.txt")
    lst.write_text("".join(f"file '{Path(f).resolve()}'\n" for f in files))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(out)], check=True)
    lst.unlink()
    return out


def mux_audio(video: Path, audio: Path | None, out: Path, start: float = 0.0, duration: float | None = None,
              bitrate: str = "320k") -> Path:
    """Video stream copied, audio sliced to [start, start+duration] and AAC-encoded."""
    if audio is None:
        Path(video).replace(out)
        return out
    dur = duration if duration is not None else probe_durations(video)["video"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-ss", f"{start:.6f}",
                    "-t", f"{dur:.6f}", "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", bitrate, "-movflags", "+faststart", str(out)], check=True)
    return out


def probe_durations(path: Path) -> dict:
    """{'video': s, 'audio': s|None, 'frames': n, 'fps': f} via ffprobe."""
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,duration,nb_frames,r_frame_rate", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    out = {"video": None, "audio": None, "frames": None, "fps": None}
    for s in json.loads(p.stdout)["streams"]:
        if s["codec_type"] == "video":
            out["video"] = float(s.get("duration", 0))
            out["frames"] = int(s.get("nb_frames", 0) or 0)
            n, d = s.get("r_frame_rate", "0/1").split("/")
            out["fps"] = float(n) / float(d) if float(d) else None
        elif s["codec_type"] == "audio":
            out["audio"] = float(s.get("duration", 0))
    return out
