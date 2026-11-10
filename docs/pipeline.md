# Pipeline: from script to delivered video

```
voiceover.md ──aion voice──▶ assets/audio.wav, audio.mp3, cue-per-word.srt, words.json, subtitles.srt
                                     │
           aion plan / aion beats ◀──┘   phrases, silences, suggested cut(...) lines
                                     │
beats.py  T = beats(name="phrase", cut1=cut("a", "b"), …)    absolute seconds, resolved in order
storyboard.md  (user approves)       one section per scene, beats per section
scenes/sNN_*.py  @scene(T.cutA, T.cutB) def sNN(s): layers + score + camera + fx
                                     │
aion still --at <beat>  → look → fix → aion preview → aion render --bg → aion status
                                     │
out/final.mp4  (chunks concatenated + audio muxed, duration = audio ±1 frame)
aion audit <v> --delivery           codec, bt709, A/V sync, loudness, black/frozen spans
```

## Steps
1. `uv run aion new 004-eigen --title "Eigenvectors"` scaffolds `videos/004-eigen/`.
2. Write `voiceover.md` (plain paragraphs; `#` headings, `>` notes and `<!-- -->` are stripped).
   `aion voice 004 --dry-run` shows chunks, cache hits and billable characters. Then run `aion voice 004`,
   which asks before spending credits. If audio comes from elsewhere instead, drop `audio.mp3` +
   `cue-per-word.srt` (one word per cue) into `assets/`.
3. `aion plan 004` prints phrases, real silences and suggested `cut("…", "…")` scene boundaries.
4. Write `beats.py` (see `docs/timing.md`), then `aion beats 004 --md` to paste the table into the storyboard.
5. Write `storyboard.md`: per scene its range, narration, visual idea (why it explains), beats, transitions,
   layers. **Get approval before building long scenes.**
6. Write `scenes/sNN_name.py`, one `@scene` per storyboard section. Scenes must tile `[T.start, T.end)`
   exactly (`aion audit --timing` checks this).
7. `aion still 004 s02_stretch --at stretch --at lam+0.5`, then view the PNGs in `out/stills/`.
8. `aion preview 004 [scene]` (480p15 + audio) to check sync by ear.
9. `aion render 004 --bg` (1080p60 by default), then `aion status` for the ETA.
10. `aion audit 004 --delivery` and fix anything marked ✘.

## Refs
A video can be named by full slug, number prefix (`004`) or path. Commands run from the repo root.
