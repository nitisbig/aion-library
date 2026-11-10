"""Audits: catch problems before a viewer (or a re-render) does.

    source(vid)    → hex colors in scenes, add_updater, Scene.play/wait, hard-coded at=<number>
    timing(vid)    → contiguity, cuts without real silence, scenes too short to read
    design(vid)    → per beat: text too small, outside the safe area, >3 things animating at once
    delivery(mp4)  → codec/pix_fmt/BT.709, A/V duration, loudness (−14 LUFS, −1 dBTP), black/frozen spans

Each returns a list of Finding(level, where, message).
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

__all__ = ["Finding", "source", "timing", "design", "delivery"]


@dataclass
class Finding:
    level: str      # "error" | "warn" | "info"
    where: str
    message: str

    def __str__(self):
        icon = {"error": "✘", "warn": "⚠", "info": "·"}[self.level]
        return f"{icon} {self.where}: {self.message}"


_RULES = [
    (re.compile(r"""["']#[0-9a-fA-F]{6}["']"""), "warn", "raw hex color: use a theme token (C.<role>)"),
    (re.compile(r"\.add_updater\("), "error", "add_updater is stateful: use m.drive()/m.redraw()"),
    (re.compile(r"self\.(play|wait)\("), "error", "Scene.play/wait don't exist in aion scenes: use m.play(at=...)"),
    (re.compile(r"\bat\s*=\s*\d+(\.\d+)?\b"), "warn", "hard-coded time: use a beat (T.name)"),
    (re.compile(r"np\.random\.(rand|randn|random|uniform|normal)\("), "warn", "unseeded RNG: use rng(seed)"),
]


def source(vid) -> list[Finding]:
    out = []
    for f in sorted(vid.paths.scenes.glob("*.py")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for rx, level, msg in _RULES:
                if rx.search(line):
                    out.append(Finding(level, f"{f.name}:{i}", msg))
    return out


def timing(vid) -> list[Finding]:
    out = []
    try:
        vid.check()
    except ValueError as e:
        out.append(Finding("error", "scenes", str(e)))
    try:
        from aion.cli.commands.beats import load_beats

        T = load_beats(vid.paths)
        for b in T:
            if b.soft:
                out.append(Finding("warn", f"beat {b.name}", "cut has no real silence nearby (audible jump?)"))
    except Exception as e:  # beats.py may not exist yet
        out.append(Finding("info", "beats", f"not checked ({e})"))
    for sd in vid.scenes:
        if sd.duration < 2.0:
            out.append(Finding("warn", sd.name, f"only {sd.duration:.2f}s long"))
    return out


def _mobjects_at(sd, t, size, fps):
    from aion.layers.manim import ManimLayer

    comp = sd.comp(size, fps)
    rc = comp.context(t)
    mobs, active = [], 0
    for layer in comp.layers:
        if isinstance(layer, ManimLayer):
            layer._ensure(rc)
            layer.advance(t)
            mobs += layer.mobjects()
            active += sum(1 for a, b in layer.windows if a <= t < b)
    return mobs, active


def design(vid, size=(1280, 720), fps=30, min_font_px_1080: float = 26) -> list[Finding]:
    """Checks at each scene's beats: tiny text, safe-area overflow, crowding."""
    from manim import Text, MathTex, Tex

    from aion.theme.tokens import current

    out = []
    try:
        from aion.cli.commands.beats import load_beats

        beats_all = list(load_beats(vid.paths))
    except Exception:
        beats_all = []
    th = current()
    fh = 8.0 if size[0] >= size[1] else 8.0 * size[1] / size[0]
    fw = fh * size[0] / size[1]
    m = th.margin
    for sd in vid.scenes:
        times = sorted({float(b) + 0.8 for b in beats_all if sd.start <= b < sd.end - 0.8} | {sd.end - 0.05})
        for t in times:
            mobs, active = _mobjects_at(sd, t, size, fps)
            if active > 3:
                out.append(Finding("warn", f"{sd.name}@{t:.1f}s", f"{active} animations at once (aim ≤ 3)"))
            for mob in mobs:
                for sub in mob.get_family():
                    if isinstance(sub, (Text, MathTex, Tex)) and sub.height > 0:
                        px = sub.height * 135   # 135 px per unit at 1080p
                        if isinstance(sub, Text) and 0 < px < min_font_px_1080 * 0.7 and len(sub.text) > 2:
                            out.append(Finding("warn", f"{sd.name}@{t:.1f}s", f"text {sub.text[:20]!r} is ~{px:.0f}px "
                                                                          f"tall at 1080p (hard to read on phones)"))
                (x0, y0, _), (x1, y1, _) = mob.get_corner([-1, -1, 0]), mob.get_corner([1, 1, 0])
                if x0 < -fw / 2 + m * 0.5 or x1 > fw / 2 - m * 0.5 or y0 < -fh / 2 + m * 0.5 or y1 > fh / 2 - m * 0.5:
                    if (x1 - x0) < fw * 0.95 and (y1 - y0) < fh * 0.95:   # ignore full-frame planes/grids
                        out.append(Finding("warn", f"{sd.name}@{t:.1f}s",
                                           f"{type(mob).__name__} crosses the safe margin"))
    return out


def _ff(args: list[str]) -> str:
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args, "-f", "null", "-"],
                          capture_output=True, text=True).stderr


def delivery(mp4: Path, audio_duration: float | None = None, target_lufs: float = -14.0) -> list[Finding]:
    out = []
    p = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(mp4)],
                       capture_output=True, text=True)
    streams = json.loads(p.stdout or "{}").get("streams", [])
    v = next((s for s in streams if s["codec_type"] == "video"), None)
    a = next((s for s in streams if s["codec_type"] == "audio"), None)
    if not v:
        return [Finding("error", mp4.name, "no video stream")]
    if v.get("pix_fmt") != "yuv420p":
        out.append(Finding("error", "video", f"pix_fmt {v.get('pix_fmt')} (YouTube wants yuv420p)"))
    if v.get("color_space") != "bt709":
        out.append(Finding("warn", "video", f"color space {v.get('color_space')} (tag bt709)"))
    if not a:
        out.append(Finding("error", "audio", "no audio stream"))
    else:
        dv, da = float(v.get("duration", 0)), float(a.get("duration", 0))
        n, d = v.get("r_frame_rate", "60/1").split("/")
        frame = float(d) / float(n)
        if abs(dv - da) > frame + 0.03:
            out.append(Finding("error", "sync", f"video {dv:.3f}s vs audio {da:.3f}s"))
        if audio_duration and abs(dv - audio_duration) > frame + 1e-3:
            out.append(Finding("error", "duration", f"video {dv:.3f}s vs narration {audio_duration:.3f}s"))
        log = _ff(["-i", str(mp4), "-map", "0:a", "-af", "ebur128=peak=true"])
        mi = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
        mp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)
        if mi:
            lufs = float(mi[-1])
            lvl = "info" if abs(lufs - target_lufs) <= 2 else "warn"
            out.append(Finding(lvl, "loudness", f"{lufs:.1f} LUFS integrated (target {target_lufs})"))
        if mp and float(mp[-1]) > -1.0:
            out.append(Finding("warn", "loudness", f"true peak {float(mp[-1]):.1f} dBTP (> −1)"))
    log = _ff(["-i", str(mp4), "-map", "0:v", "-vf", "blackdetect=d=0.5:pix_th=0.06,freezedetect=n=0.001:d=4"])
    for m_ in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", log):
        out.append(Finding("warn", "black", f"black frames {float(m_.group(1)):.2f}–{float(m_.group(2)):.2f}s"))
    for m_ in re.finditer(r"freeze_start: ([\d.]+)", log):
        out.append(Finding("info", "freeze", f"no motion for ≥4 s from {float(m_.group(1)):.2f}s (intended hold?)"))
    return out
