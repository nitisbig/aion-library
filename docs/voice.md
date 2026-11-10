# Voice (ElevenLabs)

`aion voice <video>` turns `voiceover.md` into narration plus word-level timing in one step.

**Setup:** put the key in the repo-root `.env` (gitignored): `ELEVENLABS_API_KEY=…`. `aion doctor` only
reports whether it is present and never prints it.

```bash
uv run aion voice 004 --dry-run     # chunks, cache hits, billable characters. Free
uv run aion voice 004               # asks before spending credits (--yes to skip)
```

Outputs in `assets/`:

| file | content |
|---|---|
| `audio.wav` | master, 44.1 kHz, loudness-normalised (−16 LUFS, `--loudness 0` = off) |
| `audio.mp3` | 192 kbps copy |
| `cue-per-word.srt` | one word per cue, `HH:MM:SS,mmm`: what `beats()` reads |
| `words.json` | same words with float times |
| `subtitles.srt` | readable captions (≤ 42 chars per line) for YouTube |

## How it works
- The script is cleaned (headings, `>` notes, HTML comments and emphasis are stripped), linted, and split into chunks
  of at most 2500 characters at paragraph boundaries.
- Each chunk calls `/v1/text-to-speech/{voice}/with-timestamps` with `previous_text` / `next_text` for
  natural prosody across chunks. 429/5xx errors are retried. The key is redacted in any error text.
- Every chunk is cached by its text, voice, model, settings and neighbours. Editing a paragraph re-bills its chunk and
  the chunks right before and after it (their context changed). Everything else is a cache hit.
- Chunks are decoded to PCM and joined there. Word offsets come from **decoded sample counts**, so there is
  no MP3 encoder-delay drift.

## voice.toml
```toml
voice_id = "s3TPKV1kjDlVtZbl4Ksh"
model_id = "eleven_v4"
output_format = "mp3_44100_128"
seed = 7
[settings]
stability = 0.5
similarity_boost = 0.75
speed = 1.0
```

## Writing for the ear
Short sentences. Name the thing before you use the symbol. Put a paragraph break where a scene should
cut, since paragraph pauses become the real silences that `cut()` snaps to. Spell out symbols the TTS might
misread ("x squared", not "x^2").
