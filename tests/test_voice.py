"""voice pipeline against a mocked ElevenLabs endpoint (no network, no credits)."""

import base64
import subprocess

import numpy as np
import pytest

from aion.project import VideoPaths
from aion.sync.cue import Cue
from aion.sync.silence import audio_duration
from aion.voice import master
from aion.voice.align import words_from_alignment
from aion.voice.script import chunk, lint, read_script

SCRIPT = """# Title (note, not spoken)

Imagine a grid of lines. This arrow *stretches*.

<!-- director note -->
Now watch the arrow again, and notice the 2 axes.
"""


def fake_mp3(text: str, tmp_path) -> tuple[bytes, dict]:
    dur = 0.06 * len(text)
    out = tmp_path / f"{abs(hash(text))}.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"sine=f=220:d={dur}:sample_rate=44100", "-c:a", "libmp3lame", "-b:a", "128k", str(out)],
                   check=True)
    ts = np.linspace(0, dur, len(text) + 1)
    return out.read_bytes(), {"characters": list(text), "character_start_times_seconds": ts[:-1].tolist(),
                              "character_end_times_seconds": ts[1:].tolist()}


class FakeResp:
    def __init__(self, audio, align):
        self.status_code = 200
        self._d = {"audio_base64": base64.b64encode(audio).decode(), "alignment": align}

    def json(self):
        return self._d


def test_script_parsing_and_lint(tmp_path):
    p = tmp_path / "v.md"
    p.write_text(SCRIPT)
    paras = read_script(p)
    assert paras == ["Imagine a grid of lines. This arrow stretches.",
                     "Now watch the arrow again, and notice the 2 axes."]
    assert any("digits" in w for w in lint(paras))
    assert chunk(paras, max_chars=60) == paras and len(chunk(paras)) == 1


def test_words_from_alignment_keeps_punctuation():
    text = "Hi there, you."
    ws = words_from_alignment({"characters": list(text), "character_start_times_seconds": list(range(len(text))),
                               "character_end_times_seconds": [i + 1 for i in range(len(text))]}, offset=10)
    assert [w.text for w in ws] == ["Hi", "there,", "you."] and ws[1].start == 13 and ws[1].end == 19


def test_generate_end_to_end(tmp_path, monkeypatch):
    from aion import cache

    monkeypatch.setattr(cache, "CACHE", tmp_path / "cache")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    calls = []

    def post(url, params, headers, json, timeout):
        calls.append(json)
        assert headers["xi-api-key"] == "test-key" and "with-timestamps" in url
        return FakeResp(*fake_mp3(json["text"], tmp_path))

    import requests
    monkeypatch.setattr(requests, "post", post)
    monkeypatch.setattr("aion.voice.script.MAX_CHARS", 60)
    monkeypatch.setattr("aion.voice.master.chunk", lambda paras: chunk(paras, 60))

    vdir = tmp_path / "v"
    (vdir / "assets").mkdir(parents=True)
    (vdir / "voiceover.md").write_text(SCRIPT)
    r = master.generate(VideoPaths(vdir), loudness=None, progress=False)
    assert len(calls) == 2 and calls[1]["previous_text"].startswith("Imagine")

    cue = Cue.load(vdir / "assets" / "cue-per-word.srt")
    srt_lines = (vdir / "assets" / "cue-per-word.srt").read_text().strip().split("\n\n")
    assert len(srt_lines) == len(cue) == r["words"] == 18
    assert all(len(b.splitlines()[2].split()) == 1 for b in srt_lines)       # one word per cue
    # chunk 2's first word starts exactly at chunk 1's decoded length
    first2 = cue.words[8]
    assert first2.text == "Now"
    chunk1 = master.decode_pcm(fake_mp3(read_script(vdir / "voiceover.md")[0], tmp_path)[0])
    assert abs(first2.start - len(chunk1) / master.RATE) < 1e-3
    wav = audio_duration(vdir / "assets" / "audio.wav")
    assert abs(wav - r["duration"]) < 1e-6 and abs(audio_duration(vdir / "assets" / "audio.mp3") - wav) < 1 / 60

    # second run: fully cached, no HTTP
    master.generate(VideoPaths(vdir), loudness=None, progress=False)
    assert len(calls) == 2


@pytest.mark.live
def test_live_elevenlabs_smoke(tmp_path):
    """Spends ~60 characters of credit. Run explicitly: pytest -m live"""
    from aion.voice.elevenlabs import VoiceSettings, tts_with_timestamps

    audio, align = tts_with_timestamps("Imagine a grid of lines. This arrow stretches.", None, None, VoiceSettings())
    words = words_from_alignment(align)
    assert [w.text for w in words][:2] == ["Imagine", "a"] and len(master.decode_pcm(audio)) > 44100
