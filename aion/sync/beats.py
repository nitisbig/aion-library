"""Named beats resolved from the narration: the single source of timing for a video.

    # videos/004-eigen/beats.py
    from aion import beats, cut, end, w
    T = beats(
        grid="imagine a grid",            # start of the phrase
        vector="this arrow",              # searched AFTER the previous beat
        lam=w("lambda", offset=-0.1),     # nudged
        done=end("its own span"),         # END of the phrase
        cut2=cut("its own span", "now watch"),   # scene boundary inside the real silence
    )
    T.grid, T.vector.end, T.cut2, T.duration, T.cuts

Beats are floats (seconds), so `at=T.grid` and `T.grid + 0.5` both work.
Resolution is ordered, so repeated words resolve to the right occurrence.
The SRT and audio are found from the calling file's video folder.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from pathlib import Path

from aion.core.time import FrameGrid
from aion.sync.cue import Cue

__all__ = ["Beat", "Beats", "beats", "w", "end", "cut", "sec", "Spec"]


class Beat(float):
    """A time in seconds that remembers which words it came from.

    Example:
        T.grid, T.grid.end, T.grid.text      # start s, end s, matched words
    """

    name: str
    end: float
    text: str
    soft: bool

    def __new__(cls, t: float, name: str = "", end: float | None = None, text: str = "", soft: bool = False):
        b = super().__new__(cls, t)
        b.name, b.end, b.text, b.soft = name, float(t if end is None else end), text, soft
        return b

    def __repr__(self):
        return f"Beat({self.name}={float(self):.3f}s{' ~' if self.soft else ''})"


@dataclass(frozen=True)
class Spec:
    kind: str                # "start" | "end" | "cut" | "time"
    text: str = ""
    text2: str = ""
    offset: float = 0.0
    nth: int = 1
    t: float = 0.0


def w(text: str, offset: float = 0.0, nth: int = 1) -> Spec:
    """Start of phrase `text` (+offset). `nth` skips earlier matches after the cursor.

    Example:
        grid=w("grid", offset=-0.2, nth=2)
    """
    return Spec("start", text, offset=offset, nth=nth)


def end(text: str, offset: float = 0.0, nth: int = 1) -> Spec:
    """End of phrase `text` (+offset).

    Example:
        done=end("for every vector")
    """
    return Spec("end", text, offset=offset, nth=nth)


def cut(before: str, after: str, offset: float = 0.0) -> Spec:
    """Scene boundary between the end of `before` and the start of `after`, placed in
    the middle of the real audio silence there and snapped to the frame grid.
    `offset` moves it within that silence (+ gives the earlier scene more of the pause);
    it is clamped to stay between the two words.

    Example:
        cut1=cut("every vector", "now consider")
        cut2=cut("its span", "now watch", offset=2.0)   # most of a long pause stays with the scene before
    """
    return Spec("cut", before, after, offset=offset)


def sec(t: float) -> Spec:
    """An explicit time in seconds (avoid: prefer words).

    Example:
        intro_hold=sec(2.0)
    """
    return Spec("time", t=float(t))


@dataclass
class Beats:
    """Resolved beat table. Attribute access: `T.name`. Also `T.start`, `T.end`, `T.cuts`.

    Example:
        T = beats(grid="imagine a grid"); print(T.markdown())
    """

    items: dict[str, Beat]
    duration: float
    fps: float = 60
    cue: Cue | None = field(default=None, repr=False)
    source: str = ""

    def __getattr__(self, name: str) -> Beat:
        items = self.__dict__.get("items", {})
        if name in items:
            return items[name]
        if name == "start":
            return Beat(0.0, "start")
        if name == "end":
            return Beat(self.duration, "end")
        near = difflib.get_close_matches(name, list(items), n=3)
        raise AttributeError(f"no beat {name!r}" + (f"; did you mean {near}?" if near else ""))

    def __getitem__(self, name: str) -> Beat:
        return getattr(self, name)

    def __iter__(self):
        return iter(self.items.values())

    @property
    def cuts(self) -> list[Beat]:
        """[start, every cut beat in order, end]: consecutive pairs are scene ranges."""
        cs = sorted((b for b in self.items.values() if b.name in self._cut_names), key=float)
        return [Beat(0.0, "start")] + cs + [Beat(self.duration, "end")]

    @property
    def _cut_names(self) -> set[str]:
        return self.__dict__.setdefault("_cuts", set())

    def ranges(self) -> list[tuple[Beat, Beat]]:
        c = self.cuts
        return list(zip(c, c[1:]))

    def table(self) -> list[tuple[str, float, float, str]]:
        return [(b.name, float(b), b.end, b.text) for b in sorted(self.items.values(), key=float)]

    def markdown(self) -> str:
        rows = ["| beat | time | end | words |", "|---|---|---|---|"]
        for name, t, e, text in self.table():
            mark = " ✂" if name in self._cut_names else ""
            rows.append(f"| {name}{mark} | {t:.2f} | {e:.2f} | {text} |")
        return "\n".join(rows)

    def cache_key(self):
        return [self.duration, self.fps, [(b.name, round(float(b), 4)) for b in self.items.values()]]


def cut_time(end_before: float, start_after: float, sil: list[tuple[float, float]],
             grid: FrameGrid, slack: float = 0.25) -> tuple[float, bool]:
    """Pick the cut instant: middle of the longest silence near the word boundary.
    Returns (time, soft) where soft=True means no real silence was found."""
    lo, hi = end_before - slack, max(start_after, end_before) + slack
    best, best_len = None, 0.0
    for a, b in sil:
        a2, b2 = max(a, lo), min(b, hi)
        if b2 - a2 > best_len:
            best, best_len = (a2 + b2) / 2, b2 - a2
    if best is not None:
        return grid.snap(best), False
    mid = (end_before + start_after) / 2 if start_after > end_before else start_after - 0.02
    return grid.snap(mid), True


def beats(_cue: Cue | str | Path | None = None, *, fps: float = 60, audio: str | Path | None = None,
          _video=None, **specs: str | Spec) -> Beats:
    """Resolve named beats in order. See module docstring.

    Example:
        T = beats(grid="imagine a grid", cut2=cut("its span", "now watch"))
    """
    from aion.project import video_of_caller

    video = _video
    if isinstance(_cue, Cue):
        cue = _cue
    else:
        if _cue is None:
            video = video or video_of_caller(2)
            src = video.srt
            if src is None:
                raise FileNotFoundError(f"no cue-per-word.srt / words.json in {video.assets}")
            audio = audio or video.audio
        else:
            src = Path(_cue)
        cue = Cue.load(src)
    grid = FrameGrid(fps)

    duration = cue.duration
    sil: list[tuple[float, float]] = []
    if audio is not None and Path(audio).exists():
        from aion.sync.silence import audio_duration, silences

        duration = audio_duration(audio)
        sil = silences(audio)

    items: dict[str, Beat] = {}
    cut_names: set[str] = set()
    pos = 0.0
    for name, spec in specs.items():
        spec = Spec("start", spec) if isinstance(spec, str) else spec
        try:
            if spec.kind == "time":
                b = Beat(spec.t, name, spec.t, f"@{spec.t:.2f}s")
            elif spec.kind == "cut":
                i, j = cue.find(spec.text, pos)
                k, m = cue.find(spec.text2, cue.words[i].start + 1e-4)
                eb, sa = cue.words[j - 1].end, cue.words[k].start
                t, soft = cut_time(eb, sa, sil, grid)
                if spec.offset:
                    t = grid.snap(min(max(t + spec.offset, eb + 0.05), max(sa - 0.05, eb + 0.05)))
                b = Beat(t, name, t, f"{spec.text} ✂ {spec.text2}", soft)
                cut_names.add(name)
                pos = cue.words[k].start
            else:
                i, j = cue.find(spec.text, pos, spec.nth)
                t0, t1 = cue.words[i].start, cue.words[j - 1].end
                t = (t1 if spec.kind == "end" else t0) + spec.offset
                b = Beat(t, name, t1 + spec.offset, spec.text)
                pos = t0 + 1e-4
        except KeyError as e:
            raise KeyError(f"beat {name!r}: {e.args[0]}") from None
        items[name] = b
    out = Beats(items, duration, fps, cue, str(video.dir) if video else "")
    out.__dict__["_cuts"] = cut_names
    return out
