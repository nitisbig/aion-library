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
from aion.voice.script import chunk, lint, read_script

__all__ = ["VoicePlan", "plan", "generate", "decode_pcm"]

RATE = 44100


@dataclass
class VoicePlan:
    chunks: list[str]
    settings: VoiceSettings
    cached: list[bool]
    warnings: list[str]

    @property
    def chars_to_bill(self) -> int:
        return sum(len(c) for c, hit in zip(self.chunks, self.cached) if not hit)


def _neighbours(chunks: list[str], i: int) -> tuple[str | None, str | None]:
    return (chunks[i - 1] if i else None, chunks[i + 1] if i + 1 < len(chunks) else None)


def plan(video: VideoPaths, script: Path | None = None) -> VoicePlan:
    paras = read_script(script or video.dir / "voiceover.md")
    chunks = chunk(paras)
    vs = VoiceSettings.load(video.dir / "voice.toml")
    cached = [is_cached(c, *_neighbours(chunks, i), vs) for i, c in enumerate(chunks)]
    return VoicePlan(chunks, vs, cached, lint(paras))


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

    assets = video.assets
    assets.mkdir(exist_ok=True)
    raw = assets / ".audio.raw.wav"
    _write_wav(np.concatenate(pcm), raw)
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
            "billed_chars": vp.chars_to_bill, "warnings": vp.warnings}
