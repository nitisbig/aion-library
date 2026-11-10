"""Chunked, resumable, optionally parallel rendering of a video's scenes.

    render(load_video("004"), quality="final", workers=1)

Frames are split per scene into chunks (default 2 s). Each chunk is encoded to
`out/.chunks/<quality>/` under a name that includes a hash of every input
(video sources, aion version, settings), so an interrupted render resumes and
an edit re-renders only the scenes whose inputs changed. Chunks are then
concatenated (stream copy) and muxed with the master audio.
"""

from __future__ import annotations

import math
import multiprocessing as mp
import os
import queue as _queue
import time
from dataclasses import dataclass
from pathlib import Path

from aion import cache
from aion.progress import Progress

__all__ = ["Chunk", "plan_chunks", "render", "render_scene_frames"]


@dataclass(frozen=True)
class Chunk:
    scene: str
    f0: int
    f1: int
    path: Path

    @property
    def frames(self) -> int:
        return self.f1 - self.f0


def _frame_range(sd, fps: float) -> tuple[int, int]:
    return round(sd.start * fps), round(sd.end * fps)


def plan_chunks(vid, size, fps, codec: str, scenes: list[str] | None = None,
                time_range: tuple[float, float] | None = None, chunk_sec: float = 2.0,
                tag: str = "") -> list[Chunk]:
    src = vid.source_hash()
    d = vid.paths.out / ".chunks" / (tag or f"{min(size)}p{fps:g}-{codec}{'-v' if size[1] > size[0] else ''}")
    d.mkdir(parents=True, exist_ok=True)
    per = max(1, round(chunk_sec * fps))
    out = []
    for sd in vid.scenes:
        if scenes and not any(sd.name == s or sd.name.startswith(s) for s in scenes):
            continue
        a, b = _frame_range(sd, fps)
        if time_range:
            a, b = max(a, math.floor(time_range[0] * fps)), min(b, math.ceil(time_range[1] * fps))
        if b <= a:
            continue
        k = cache.key(src, sd.name, size, fps, codec)
        # chunk grid anchored at the scene start so chunks stay stable when a range is requested
        s0 = round(sd.start * fps)
        g0 = s0 + ((a - s0) // per) * per
        for f in range(g0, b, per):
            f0, f1 = max(f, a), min(f + per, b, round(sd.end * fps))
            if f1 > f0:
                out.append(Chunk(sd.name, f0, f1, d / f"{sd.name}_{f0:06d}_{f1:06d}_{k}.mp4"))
    return out


# ── worker side ──────────────────────────────────────────────────────────────
_W: dict = {}


def _worker_init(slug_dir: str, size, fps):
    os.environ.setdefault("EGL_PLATFORM", "surfaceless")
    from aion.render.project import load_video

    _W["vid"] = load_video(Path(slug_dir), size, fps)
    _W["size"], _W["fps"] = tuple(size), fps


def _render_run(args):
    """Render a contiguous run of chunks of one scene (forward only)."""
    scene_name, chunks, codec, q = args
    from aion.render.encode import Encoder

    vid, size, fps = _W["vid"], _W["size"], _W["fps"]
    sd = vid.scene(scene_name)
    comp = sd.comp(size, fps)
    done = []
    for ch in chunks:
        tmp = ch.path.with_name(f".{ch.path.stem}.{os.getpid()}.tmp.mp4")
        with Encoder(tmp, size, fps, codec=codec) as enc:
            for k in range(ch.f0, ch.f1):
                enc.write(comp.frame(max(k / fps, sd.start), k))   # a cut off the fps grid can sample just before the scene starts
                if q is not None:
                    q.put(1)
        os.replace(tmp, ch.path)
        done.append(str(ch.path))
    return done


def _runs(chunks: list[Chunk], workers: int) -> list[tuple[str, list[Chunk]]]:
    """Group missing chunks into contiguous per-scene runs, split for load balance."""
    runs: list[tuple[str, list[Chunk]]] = []
    for ch in chunks:
        if runs and runs[-1][0] == ch.scene and runs[-1][1][-1].f1 == ch.f0:
            runs[-1][1].append(ch)
        else:
            runs.append((ch.scene, [ch]))
    if workers > 1:
        total = sum(c.frames for c in chunks)
        target = max(1, total // (workers * 2))
        split = []
        for name, lst in runs:
            cur = []
            for c in lst:
                cur.append(c)
                if sum(x.frames for x in cur) >= target:
                    split.append((name, cur))
                    cur = []
            if cur:
                split.append((name, cur))
        runs = split
    return runs


def render(vid, size, fps, codec: str = "final", scenes=None, time_range=None, workers: int = 1,
           chunk_sec: float = 2.0, tag: str = "", name: str | None = None) -> list[Chunk]:
    """Render all needed chunks (skipping existing ones). Returns the ordered chunk list."""
    chunks = plan_chunks(vid, size, fps, codec, scenes, time_range, chunk_sec, tag)
    missing = [c for c in chunks if not c.path.exists()]
    total = sum(c.frames for c in chunks)
    cached = total - sum(c.frames for c in missing)
    bar = Progress(name or f"{vid.slug}@{size[1]}p{fps:g}", total, initial=cached)
    ok = False
    try:
        runs = _runs(missing, workers)
        if workers <= 1 or len(runs) <= 1:
            _W.update(vid=vid, size=tuple(size), fps=fps)
            for scene_name, lst in runs:
                bar.note(scene_name)
                _render_run((scene_name, lst, codec, _BarQ(bar)))
        else:
            ctx = mp.get_context("spawn")
            with ctx.Manager() as mgr:
                q = mgr.Queue()
                with ctx.Pool(workers, _worker_init, (str(vid.paths.dir), tuple(size), fps)) as pool:
                    res = pool.map_async(_render_run, [(n, lst, codec, q) for n, lst in runs])
                    while not res.ready():
                        _drain(q, bar)
                        time.sleep(0.2)
                    _drain(q, bar)
                    res.get()
        ok = True
    finally:
        bar.close(vid.paths.out, ok=ok)
    return chunks


class _BarQ:
    def __init__(self, bar):
        self.bar = bar

    def put(self, n):
        self.bar.update(n)


def _drain(q, bar):
    while True:
        try:
            bar.update(q.get_nowait())
        except _queue.Empty:
            return


def render_scene_frames(vid, scene_name: str, times: list[float], size, fps, alpha: bool = False):
    """Render specific frames of one scene (forward order), returning uint8 arrays."""
    sd = vid.scene(scene_name)
    comp = sd.comp(size, fps)
    return [comp.frame(t, round(t * fps), alpha=alpha) for t in sorted(times)]
