# Voice (ElevenLabs)

`aion voice <video>` turns `voiceover.md` into narration plus word-level timing in one step.

**Setup:** put the key in the repo-root `.env` (gitignored): `ELEVENLABS_API_KEY=…`. `aion doctor` only
reports whether it is present and never prints it.

```bash
uv run aion voice 004 --dry-run                 # chunks or scenes, cache hits, billable characters. Free
uv run aion voice 004                           # asks before spending credits (--yes to skip)
uv run aion voice 015 --scene s07_ripple        # scene chunking: re-request one scene with its current neighbours
uv run aion voice 015 --retake s07_ripple       # scene chunking: a new take of one scene (new seed)
```

Outputs in `assets/`:

| file | content |
|---|---|
| `audio.wav` | master, 44.1 kHz, loudness-normalised (−16 LUFS, `--loudness 0` = off) |
| `audio.mp3` | 192 kbps copy |
| `cue-per-word.srt` | one word per cue, `HH:MM:SS,mmm`: what `beats()` reads |
| `words.json` | same words with float times |
| `subtitles.srt` | readable captions for YouTube: ≤ 42 characters per line, ≤ 2 lines, 1–6 s on screen |
| `subtitles.vtt` | the same captions as WebVTT |
| `scenes.json` | scene chunking only: `[{id, start, end, speech_start, speech_end, first_word, last_word, first_index, last_index}]` on the final timeline |

## How it works
- The script is cleaned (headings, `>` notes, HTML comments, emphasis and inline `[pause N]` are stripped), linted,
  and split into requests. By default (`chunking = "pack"`) paragraphs are packed into chunks of at most
  2500 characters. With `chunking = "scene"` each scene is one request (see below).
- Each request calls `/v1/text-to-speech/{voice}/with-timestamps` with `previous_text` / `next_text` for
  natural prosody across requests. 429/5xx errors are retried. The key is redacted in any error text.
- Every request is cached by its text, voice, model, settings, seed and neighbours. In pack mode, editing a paragraph
  re-bills its chunk and the chunks right before and after it (their context changed). Everything else is a cache hit.
- Requests are decoded to PCM and joined there. Word offsets come from **decoded sample counts**, so there is
  no MP3 encoder-delay drift.
- The free pacing pass (`[pacing]`) then snaps cues to real speech onsets and widens pauses. Changing it, or any
  pause mark, never re-bills.

## Scene chunking (one request per scene)
Put `chunking = "scene"` in `voice.toml` and a marker before each scene's paragraphs:

```markdown
<!-- scene: s01_cold_open -->
Sticks rain onto a floor of boards. [pause 0.8s] Where is the circle hiding?

<!-- scene: s02_question -->
...
```

- A scene is the paragraphs after its marker, joined by blank lines, and it is sent as one request. `previous_text` and
  `next_text` are the whole neighbouring scenes. Every paragraph must follow a marker, and each id is used once. A
  marker with no narration after it is reported by the dry run and gets no audio.
- Each take is exported next to `assets/`. `audio/scenes/<id>.mp3` holds the returned bytes.
  `audio/alignment/<id>.json` holds the characters with start and end times, the words with clip-local times (in the
  script's spelling, with `said` when an alias changed it), the duration from decoded samples, and the request:
  model, voice, settings, seed, take, and the shas of the text, previous text and next text.
- **Pinning.** `audio/manifest.json` records each scene's exact request, including its neighbours' text, and its
  place on the timeline. While a scene's own text is unchanged, its recorded neighbours and seed are reused. Editing
  one scene therefore bills only that scene, even though its neighbours' context changed. Changed scenes, and scenes
  named with `--scene`, are requested with their current neighbours. Changing the voice, model, output format,
  settings or base seed re-requests every scene.
- **Retakes.** `--retake ID` (repeatable) requests that scene again with its current neighbours and seed =
  `seed + take` (take 1, 2, …). Old takes stay in the cache, and the manifest pins the newest one.
- **Cache prunes cost nothing.** When a pinned request is missing from the cache, but `audio/scenes/<id>.mp3` and its
  alignment JSON hold exactly that take (shas checked), the take is restored from them for free. The dry run marks it
  `restore`.
- The dry run lists every scene with its characters and status: `cached`, `restore` or `BILL`, plus the reason
  (new, text changed, retake N with its seed, --scene, settings changed, or a pinned scene whose neighbour changed).
- `aion voice` writes `assets/scenes.json` (also in the manifest). Scenes tile the audio, and each boundary sits
  halfway through the silence between two scenes. `first_index` / `last_index` index `words.json`.

## Writing the script
- **Inline pauses:** `[pause 0.8s]` or `[pause 2]` inside a paragraph adds that much silence before the next word. The
  mark never reaches the TTS. The pacing pass cuts the silence into the real pause there, so put it after punctuation,
  where the voice stops anyway. The lint warns when it doesn't. If the voice ran straight on (no real silence), the
  cut goes at the quietest 10 ms in the 0.35 s before the word, faded out and back in, so the pause is never lost. A paragraph that holds only `[pause N]` adds to the
  silence before the next paragraph.
- **`> [pause N]` lines** between paragraphs ask for N more seconds before the next paragraph.
- **`> [insert]` … `> [/insert]`** (pack mode) wraps text added after the narration was generated. It is synthesised
  alone and spliced in, so nothing already paid for is re-billed. Scene chunking doesn't need it: edit the scene.
- Square brackets that aren't a pause are sent to the TTS, where eleven_v4 reads them as audio tags
  (`[whispers]`). The lint lists them.

## voice.toml
```toml
voice_id = "s3TPKV1kjDlVtZbl4Ksh"
model_id = "eleven_v4"
output_format = "mp3_44100_128"
seed = 7                      # base seed; a retake uses seed + take
chunking = "scene"            # one request per <!-- scene: id --> block (default "pack")
[settings]
stability = 0.5
similarity_boost = 0.75
[aliases]                     # TTS spelling of single words; cues and captions keep the script's spelling
Buffon = "Boo-fon"            # also covers "Buffon's"; exact, case-sensitive match; one word on each side
[lint]
banned = ["crucial", "in fact", "—"]   # every hit is reported (case-insensitive, whole words)
[pacing]                      # free: applied to cached audio, never re-bills (aion/voice/pacing.py)
snap = true
lead_in = 1.5
paragraph_gap = 0.5
section_gap = 1.5
tail = 3.0
```

None of `chunking`, `[aliases]`, `[lint]` or `[pacing]` is part of the request cache key. `[lint]` and `[pacing]`
never re-bill. An alias changes the text that is sent, and switching `chunking` changes every request.

## Captions
`subtitles.srt` and `subtitles.vtt` come from one search. Captions break at sentence ends and commas rather than after
"the" or "of", never span a paragraph pause, and hold at most 2 lines of 42 characters. A final pass makes the limits
hard: a cue on screen longer than 6 s is split at its best phrase break, and one shorter than 1 s is extended into the
free time around it, merged with a neighbour, or as a last resort given a little of a neighbour's time.
`check_subtitles` lists every violation, so an empty list means the file passes:

```python
from aion.voice import check_subtitles, read_scenes
problems = check_subtitles("videos/015-math-big-picture/assets/subtitles.srt")    # [] = passes
scenes = read_scenes("videos/015-math-big-picture/voiceover.md")                 # [(id, [Para, ...]), ...]
```

## ElevenLabs notes (docs checked 2026-11-22)
- **eleven_v4 ignores `voice_settings.speed`** (the API range is 0.7–1.2, default 1.0), and `style` isn't available
  on v4 either. The settings are still part of the cache key, so changing `speed` re-bills without changing the
  read. Control pace with pauses, `[pacing]` and sentence length instead.
- `previous_text` / `next_text` are supported on the with-timestamps endpoint. The only model excluded from request
  stitching is eleven_v3. `previous_request_ids` (at most 3, each at most 2 h old) would override the text fields.
  aion uses the text fields because they stay valid for cached and pinned requests.
- `seed` is an integer in 0–4294967295, best effort: "Determinism is not guaranteed". The cache, or an exported
  take, is the only exact copy of a take.
- v4 allows up to 100,000 characters per request and doesn't support SSML `<break>` tags. That's why `[pause N]` is
  stripped and applied in post. Text normalization is on by default, but write numbers as words anyway.

## Writing for the ear
Short sentences. Name the thing before you use the symbol. Put a paragraph break where a scene should
cut, since paragraph pauses become the real silences that `cut()` snaps to. Spell out symbols the TTS might
misread ("x squared", not "x^2").
