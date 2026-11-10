"""ElevenLabs text-to-speech with character timestamps (HTTP via requests).

Each chunk is cached by sha(text, previous/next text, voice, model, format,
settings), so re-running after editing one paragraph only pays for the chunks
whose text (or neighbours) changed. The API key comes from ELEVENLABS_API_KEY
(environment or the repo's .env) and is never logged.
"""

from __future__ import annotations

import base64
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from aion import cache
from aion._env import secret

__all__ = ["VoiceSettings", "tts_with_timestamps", "is_cached", "API"]

API = "https://api.elevenlabs.io/v1"


@dataclass(frozen=True)
class VoiceSettings:
    """Voice/model choice. Override per video in `videos/<slug>/voice.toml`.

    Example:
        VoiceSettings(voice_id="s3TPKV1kjDlVtZbl4Ksh", model_id="eleven_v4")
    """

    voice_id: str = "s3TPKV1kjDlVtZbl4Ksh"
    model_id: str = "eleven_v4"
    output_format: str = "mp3_44100_128"
    stitch: bool = True                         # send previous_text / next_text
    seed: int | None = 7
    settings: dict = field(default_factory=dict)  # stability, similarity_boost, style, speed...

    @classmethod
    def load(cls, path: Path | None) -> "VoiceSettings":
        if path is None or not path.exists():
            return cls()
        import tomllib

        data = tomllib.loads(path.read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def cache_key(self):
        return asdict(self)


def _request_body(text: str, prev: str | None, nxt: str | None, vs: VoiceSettings) -> dict:
    body: dict = {"text": text, "model_id": vs.model_id}
    if vs.stitch:
        if prev:
            body["previous_text"] = prev
        if nxt:
            body["next_text"] = nxt
    if vs.settings:
        body["voice_settings"] = dict(vs.settings)
    if vs.seed is not None:
        body["seed"] = vs.seed
    return body


def _key(text, prev, nxt, vs):
    return [text, prev if vs.stitch else None, nxt if vs.stitch else None, vs]


def is_cached(text: str, prev: str | None, nxt: str | None, vs: VoiceSettings) -> bool:
    return cache.path("tts", cache.key(_key(text, prev, nxt, vs)), ".json").exists()


def tts_with_timestamps(text: str, prev: str | None, nxt: str | None, vs: VoiceSettings,
                        retries: int = 4, timeout: float = 180) -> tuple[bytes, dict]:
    """(audio bytes, alignment {characters, character_start_times_seconds, character_end_times_seconds})."""

    def make(tmp: Path):
        import requests

        api_key = secret("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set (add it to the repo's .env)")
        url = f"{API}/text-to-speech/{vs.voice_id}/with-timestamps"
        delay = 2.0
        for attempt in range(retries + 1):
            r = requests.post(url, params={"output_format": vs.output_format},
                              headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                              json=_request_body(text, prev, nxt, vs), timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                align = data.get("alignment") or data.get("normalized_alignment")
                if not data.get("audio_base64") or not align:
                    raise RuntimeError("ElevenLabs response missing audio or alignment")
                tmp.write_text(json.dumps({"audio_base64": data["audio_base64"], "alignment": align}))
                return
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            detail = r.text[:300].replace(api_key, "***")
            raise RuntimeError(f"ElevenLabs HTTP {r.status_code}: {detail}")

    p = cache.get_or_make("tts", _key(text, prev, nxt, vs), make, ".json")
    data = json.loads(p.read_text())
    return base64.b64decode(data["audio_base64"]), data["alignment"]
