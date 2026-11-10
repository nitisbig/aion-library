"""aion.voice: ElevenLabs narration → audio + word-level cues (cached per chunk)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "VoiceSettings": "elevenlabs",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
