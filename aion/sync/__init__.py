"""aion.sync: narration timing (word cues, named beats, silences, scene cuts)."""

from aion._lazy import lazy

EXPORTS: dict[str, str] = {
    "Cue": "cue", "Word": "cue", "Cursor": "cue", "norm": "cue",
    "beats": "beats", "Beats": "beats", "Beat": "beats", "w": "beats", "end": "beats",
    "cut": "beats", "sec": "beats",
    "silences": "silence", "audio_duration": "silence", "load_audio": "silence",
    "check_contiguous": "cuts", "suggest_cuts": "cuts",
}
__getattr__, __dir__, __all__ = lazy(__name__, EXPORTS)
