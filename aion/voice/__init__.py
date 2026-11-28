"""aion.voice: ElevenLabs narration → audio + word-level cues (cached per chunk or per scene) + captions."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "VoiceSettings": "elevenlabs",
    "read_scenes": "script",
    "write_subtitles": "align", "write_vtt": "align", "check_subtitles": "align",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
