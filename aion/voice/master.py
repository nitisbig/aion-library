"""Generate a video's narration: voiceover.md → audio.wav/mp3 + word cues.

    generate(find_video("004"))   # what `aion voice 004 --yes` runs

Chunks are decoded to PCM and concatenated there, never as MP3 bytes, because
MP3 encoder delay would shift every later word. Each chunk's offset is its
decoded sample count, so word times match the master audio exactly.
"""

from __future__ import annotations

import io
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from aion.project import VideoPaths
from aion.voice.align import words_from_alignment, write_subtitles, write_word_srt, write_words_json
from aion.voice.elevenlabs import VoiceSettings, is_cached, tts_with_timestamps
from aion.voice.pacing import Pacing, silences, snap_words, stretch
from aion.voice.script import chunk, lint, read_marked, read_script, read_sections

__all__ = ["VoicePlan", "plan", "generate", "decode_pcm"]

RATE = 44100


@dataclass
class VoicePlan:
    chunks: list[str]
    settings: VoiceSettings
    cached: list[bool]
    warnings: list[str]
    inserts: list = None            # [(base paragraph index it goes before, [(text, prev, next)], [cached])]

    @property
    def chars_to_bill(self) -> int:
        n = sum(len(c) for c, hit in zip(self.chunks, self.cached) if not hit)
        for _, parts, hits in self.inserts or []:
            n += sum(len(t) for (t, _, _), hit in zip(parts, hits) if not hit)
        return n


def _neighbours(chunks: list[str], i: int) -> tuple[str | None, str | None]:
    return (chunks[i - 1] if i else None, chunks[i + 1] if i + 1 < len(chunks) else None)


def plan(video: VideoPaths, script: Path | None = None) -> VoicePlan:
    marked = read_marked(script or video.dir / "voiceover.md")
    base = [p for p, _, ins in marked if not ins]
    chunks = chunk(base)                                  # the original narration: same chunks, same cache hits
    vs = VoiceSettings.load(video.dir / "voice.toml")
    cached = [is_cached(c, *_neighbours(chunks, i), vs) for i, c in enumerate(chunks)]
    inserts, n_base, i = [], 0, 0
    while i < len(marked):                                # each run of inserted paragraphs is synthesised alone
        if not marked[i][2]:
            n_base, i = n_base + 1, i + 1
            continue
        j = i
        while j < len(marked) and marked[j][2]:
            j += 1
        texts = chunk([p for p, _, _ in marked[i:j]])
        before = marked[i - 1][0] if i else None
        after = marked[j][0] if j < len(marked) else None
        parts = [(t, texts[k - 1] if k else before, texts[k + 1] if k + 1 < len(texts) else after)
                 for k, t in enumerate(texts)]
        inserts.append((n_base, parts, [is_cached(*part, vs) for part in parts]))
        i = j
    return VoicePlan(chunks, vs, cached, lint([p for p, _, _ in marked]), inserts)


def _splice(audio: np.ndarray, words: list, k: int, extra: np.ndarray, extra_words: list, rate: int = RATE):
    """Insert `extra` (with its words, timed from 0) before word k, cutting inside the real pause there."""
    from dataclasses import replace

    if k >= len(words):
        cut = len(audio)
    else:
        ends = [(a, b) for a, b in silences(audio, rate, min_len=0.08) if abs(b - words[k].start) < 0.25]
        t = 0.5 * sum(min(ends, key=lambda ab: abs(ab[1] - words[k].start))) if ends else \
            0.5 * (words[k - 1].end + words[k].start)
        cut = int(round(t * rate))
    fade = int(rate * 0.008)
    head, tail = audio[:cut].copy(), audio[cut:].copy()
    if len(head) > fade:
        head[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=audio.dtype)
    if len(tail) > fade:
        tail[:fade] *= np.linspace(0.0, 1.0, fade, dtype=audio.dtype)
    pad = np.zeros(int(rate * 0.3), audio.dtype)          # a breath on each side; the pacing pass widens it
    block = np.concatenate([pad, extra, pad])
    t0, dt = (cut + len(pad)) / rate, len(block) / rate
    mid = [replace(w, start=w.start + t0, end=w.end + t0) for w in extra_words]
    late = [replace(w, start=w.start + dt, end=w.end + dt) for w in words[k:]]
    return np.concatenate([head, block, tail]), words[:k] + mid + late


def decode_pcm(data: bytes, rate: int = RATE) -> np.ndarray:
    """Any encoded audio bytes → mono float32 at `rate`."""
    import av

    out = []
    with av.open(io.BytesIO(data)) as f:
        res = av.AudioResampler(format="flt", layout="mono", rate=rate)
        for frame in f.decode(f.streams.audio[0]):
            out.extend(r.to_ndarray().reshape(-1) for r in res.resample(frame))
        out.extend(r.to_ndarray().reshape(-1) for r in res.resample(None))
    return np.concatenate(out) if out else np.zeros(0, np.float32)


def _write_wav(x: np.ndarray, path: Path, rate: int = RATE) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(pcm.tobytes())


def _loudnorm(src: Path, dst: Path, target: float = -16.0) -> None:
    """Two-pass linear EBU R128 normalisation (no timing change)."""
    import json as _json

    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af",
                            f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = _json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=11:linear=true:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", af, "-ar", str(RATE),
                    "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)


def _pace(audio: np.ndarray, words: list, sections: list[tuple[str, bool]], pacing: Pacing):
    """Apply voice.toml [pacing]: snap cues to speech onsets, then widen paragraph / section pauses."""
    sil = silences(audio, RATE)
    info: dict = {}
    if pacing.snap:
        words, info["cues_snapped"] = snap_words(words, sil)
    breaks, k = [], 0
    for text, section in sections:                     # k = index of the paragraph's first word
        if k:
            breaks.append((k, pacing.section_gap if section else pacing.paragraph_gap))
        k += len(text.split())
    if k != len(words):                                # alignment and script disagree: don't guess
        info["pacing_skipped"] = f"script has {k} words, alignment {len(words)}"
        breaks = []
    n0 = len(audio)
    audio, words, info["seconds_added"] = stretch(audio, words, RATE, breaks, pacing.lead_in,
                                                   silences(audio, RATE, min_len=0.08), pacing.tail)
    info["breaks"] = len(breaks)
    info["duration_added"] = (len(audio) - n0) / RATE
    return audio, words, info


def generate(video: VideoPaths, script: Path | None = None, loudness: float | None = -16.0,
             progress: bool = True) -> dict:
    """Run TTS for every chunk (cached), then write assets/{audio.wav, audio.mp3,
    cue-per-word.srt, words.json, subtitles.srt}. Returns a summary dict."""
    from aion.progress import Progress

    vp = plan(video, script)
    words, pcm, offset = [], [], 0
    bar = Progress(f"{video.slug}-voice", len(vp.chunks), unit="chunk", disable=not progress)
    try:
        for i, text in enumerate(vp.chunks):
            audio, align = tts_with_timestamps(text, *_neighbours(vp.chunks, i), vp.settings)
            x = decode_pcm(audio)
            words += words_from_alignment(align, offset / RATE)
            pcm.append(x)
            offset += len(x)
            bar.update()
    finally:
        bar.close(video.assets)

    audio = np.concatenate(pcm)
    base_words = [len(p.split()) for p, _, ins in read_marked(script or video.dir / "voiceover.md") if not ins]
    for n_base, parts, _ in reversed(vp.inserts or []):   # last first, so earlier word indices stay valid
        xs, xw, off = [], [], 0
        for part in parts:
            a, align = tts_with_timestamps(*part, vp.settings)
            x = decode_pcm(a)
            xw += words_from_alignment(align, off / RATE)
            xs.append(x)
            off += len(x)
        audio, words = _splice(audio, words, sum(base_words[:n_base]), np.concatenate(xs), xw)
    offset = len(audio)
    pacing = Pacing.load(video.dir / "voice.toml")
    paced = {}
    if pacing.active and words:
        audio, words, paced = _pace(audio, words, read_sections(script or video.dir / "voiceover.md"), pacing)
        offset = len(audio)

    assets = video.assets
    assets.mkdir(exist_ok=True)
    raw = assets / ".audio.raw.wav"
    _write_wav(audio, raw)
    wav = assets / "audio.wav"
    if loudness is not None:
        _loudnorm(raw, wav, loudness)
        raw.unlink()
    else:
        raw.replace(wav)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame",
                    "-b:a", "192k", str(assets / "audio.mp3")], check=True)
    write_word_srt(words, assets / "cue-per-word.srt")
    write_words_json(words, assets / "words.json")
    write_subtitles(words, assets / "subtitles.srt")
    return {"chunks": len(vp.chunks), "words": len(words), "duration": offset / RATE,
            "billed_chars": vp.chars_to_bill, "warnings": vp.warnings, **paced}
