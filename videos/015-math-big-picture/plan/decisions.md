# Decisions log, video 015 (Phase 1)

Every choice that departs from the brief, or that the brief left open. **Review** marks the ones you should look at
before Phase 2. Rule IDs (R1–R15) are in `research_digest.md`.

## Process and files

| ID | Decision | Why |
|---|---|---|
| D1 | The brief's `project/` folder is `videos/015-math-big-picture/`. aion's own files (`voiceover.md`, `beats.py`, `theme.py`, `voice.toml`, `storyboard.md`) sit beside the brief's folders and are generated from `plan/scenes.yaml`. | One source of truth, and the video still runs through `aion still / preview / render / audit`. |
| D2 | `scenes.yaml` follows the brief's schema and adds `arc_step`, `duration_source`, `pause_after_s`, `interrupt` and `map_update` per scene, plus top-level `video`, `pillars`, `chapters`, `loops` and `map_edges`. | The checks (loops planted before paid, interrupts, map progress) need them. |
| D3 | `ruamel.yaml` added as a dependency. | `timing.py` rewrites `duration_s` without losing the file's comments and layout. |
| D4 | Scene files will be `scenes/sNN_<id>.py` (e.g. `s07_ch1_s02.py`), one `@scene` per `scenes.yaml` entry. | aion imports `scenes/s*.py` in name order. |

## Look and design

| ID | Decision | Why |
|---|---|---|
| D5 | **Classic finish with Design System colors** (your choice, 2026-11-22): pure black, crisp lines, no bloom, glow, vignette or grain; Computer Modern roman for maths, sans for key words, small caps for names, dates and chapter cards. The pillar colors are the DS hue tokens. | The DS asks for glow and grain; your later feedback asked for the crisp Classic look. This keeps both the channel's colors and the Classic finish. |
| D6 | Pillar colors: Foundations blue, Quantity gold, Structure violet, Space teal, Change orange, Uncertainty pink; the recurring circle is warm white; unlit map parts are dim slate. Each keeps its color for the whole video. | One color per math object (CLAUDE.md). Pillars also differ by ring position and glyph, so color is never the only cue. Details: `theme.py`, `design/design_sheet.md`. |
| D7 | The alert red appears once: the contradiction in the square-root-of-two proof (ch2_s04). | A color used once stays loud. |
| D8 | Takeaway card: at most four key words and one equation. | R11: minimal on-screen text. |
| D9 | The transit-map scene (ch4_s06) uses a made-up network with no real line names, colors or branding. Only Harry Beck and the year are named. | Avoids reproducing the actual Underground map. |

## Story

| ID | Decision | Why |
|---|---|---|
| D10 | **Needles-first cold open:** sticks rain, the estimate converges to pi, then "where is the circle hiding?" by about 10 s. The needles then swing to the center and their tips trace the circle. | R1 (question first) and R2 (payoff shown unexplained). The circle the video follows is born from the open loop. |
| D11 | **Map of Math as a ring of six nodes around the circle.** It turns 60 degrees at each chapter boundary, so the next chapter's node always arrives at the bottom. After six turns (end of Ch6) it is back where it started. | One signature transition (R8). The turns are themselves math: Ch3 pays them off as the cyclic group of order six, and Ch7 opens on the sixth turn bringing the map home. |
| D12 | **Open loops:** L1 sticks to pi (cold open to Ch6 and Ch7), L2 "e, i and pi will meet" (Ch3 to Ch7), L3 "the map turns by the same amount" (intro to Ch3, with a small "all six by the end" promise paid in Ch7). Midpoint re-hook at ch4_s01. | R7 and R9. The brief asks for at least two loops, each paid off. |
| D13 | **Takeaways:** each chapter ends with one spoken sentence over a 5–10 s visual callback (the hero image shrinking into its node), then the map turn in a 3 s silence. | The brief asks for a one-sentence takeaway; PB #17 asks for a visual callback. This does both. |
| D14 | **Review: master format.** The brief asks for a 3840x2160 60 fps master. That is about 90,000 4K frames on a 2-core laptop with an integrated GPU, likely several days of rendering. Options: 4K60 as briefed, 4K30, or 1080p60 (the channel's usual). Decide before Phase 2; Phase 1 plans everything resolution-independent. | Feasibility on this machine. |
| D15 | **Review: outro order** follows the brief: recap, payoff image, reflective question, then one next video (007, Euler's identity) and the CTA. PB #19 would end on the payoff, so the payoff image (the whole circle) stays on screen under the question and the end card. | The brief's required contents, with R13's "end on the payoff" kept visually. |
| D34 | **Cold open removed (your request, Phase 2).** The video now opens on in_s01 (worksheets → sunflower spiral → pond, wheel, clock → THE circle and the title). D10's needles first appear in in_s05 on "those sticks on the floor": the map slides left, a board floor fills with needles and 2N/H settles on 3.1416. L1 is planted there and still paid off in Ch6 and Ch7. Re-voicing billed nothing; runtime 23:51. | You asked to drop the first 22 s; the sticks line needed a picture to refer to. |
| D32 | **Quantity proves that the square root of two is not a fraction** (the side of the square inside the unit circle) and cites Lambert (1761) for pi. | The brief asks why pi can't be a fraction; Lambert's proof is far too long for the format, while the root-two proof shows the method (proof by contradiction) in 45 s. |
| D16 | Euler's identity is Ch7's hub, and video 007 (`007-euler-identity`) is the one next video named. | It is the single line where e (change), i (structure) and pi (quantity) meet, and the channel already has that video. |
| D17 | **Review: CTA wording.** The narration says "Subscribe so you don't miss it, and to play with these ideas yourself, try the interactive app at I give ideas dot com"; the end card shows `interactive app · igiveideas.com`. Confirm the address, that the app is live, and the wording. | The brief names the interactive app as optional. Spoken URLs are easy to mishear. |

## Narration and voice

| ID | Decision | Why |
|---|---|---|
| D18 | Voice: the channel voice `s3TPKV1kjDlVtZbl4Ksh` on `eleven_v4` (as in 004–014). | Consistency across videos. |
| D19 | **Name test instead of a speed test** (your choice, 2026-11-22). The planned test voiced one scene at three speeds, but ElevenLabs' docs say eleven_v4 ignores `voice_settings.speed`, so three speeds would have bought three near-identical reads. Instead ch3_s05 (Euler, Hamilton) and ch6_s05 (Buffon, Lazzarini, Zu Chongzhi) were voiced at the final settings (791 characters) to check names by ear and measure the rate: 178 and 145 wpm of speech. Those takes are reused by the full run. `speed = 0.90` stays in `voice.toml` only as part of the cache key. | The brief's 130–145 wpm is an overall rate, reached with planned silences and sentence length, not with the speed setting. |
| D20 | **Pace (measured).** The voiced script is 3,434 words and runs **24:13** (1,453.3 s): 142 wpm overall, 153 wpm inside scenes, with planned silences between scenes and at chapter turns. That is inside the brief's 22–28 min window and 130–145 wpm, so no silences were widened and no words added. Chapters run within 25 s of their targets except the intro (2:14 vs 2:35) and Ch7 (1:49 vs 2:00). | Hard minimum 22:00, window 22–28 min, 130–145 wpm overall. |
| D21 | Per-scene audio comes from the aion voice extension: one TTS request per scene (`chunking = "scene"`), neighbor text sent for stitching, `[pause N]` marks cut from the TTS text and inserted afterwards by the free pacing pass, retakes with a new seed. | Required per-scene files and alignment JSON, without re-billing neighbors when one scene changes. |
| D22 | Spoken text never reads an equation symbol by symbol. In worked examples the screen shows the arithmetic and the voice gives the verdict ("the first passes the test exactly"). | Brief: the voice never duplicates the picture. |
| D23 | History comes one line at a time (who, when, what), shown as a small-caps lower third. | Saved narration feedback (2026-11-21). |
| D24 | **Review: Lazzarini (ch6_s05).** The narration says his 1901 result was "suspiciously good", that it equals Zu Chongzhi's fraction exactly, and that "his numbers suggest he chose when to stop". This follows Badger's 1994 analysis and stops short of calling it fraud. | A careful claim about a real person. |
| D25 | Subtitles show the script's spelling. Pronunciation aliases change only the TTS text. | Captions should read like the script. See `script/pronunciation.md`. |
| D33 | **Six pauses fixed (your OK, 2026-11-22).** In six places the voice ran two sentences together, so the scripted pause had no real silence to widen and the pacing pass used to skip it: ch2_s04 "…not a fraction. / Numbers like this…", ch5_s05 "…inner edge. / Make the nudge…", ch6_s07 "…we've seen. / So let's see…", ch7_s01 "…whole numbers. / Physics…", ch7_s03 "…can reach. / No single branch…" (1.2 s) and out_s02 "…piece by piece. / Subscribe…". aion's `stretch()` now cuts at the quietest 10 ms in the 0.35 s before the word, with 8 ms fades, when there is no silence. Re-running `aion voice 015` billed nothing and added the missing 3.6 s; the six silences now measure 0.30–1.28 s, and no clicks show at their edges. | Found by measuring the master audio against the script's pause marks. |

## Engines (R15)

| ID | Decision | Why |
|---|---|---|
| D26 | **Manim** for geometry, equations, number lines, rotations, counters, graphs and the Map of Math. The brief's rubric puts the map in ModernGL for its glow; the Classic look (D5) has no glow, so nodes light by filling with their color and Manim draws them. | Crisp vectors and TeX, scored to the word cues. |
| D27 | **numpy + skia** for the needles, where the brief's rubric suggests Taichi. Throws are independent samples with no interaction, so numpy draws them (seeded) and skia renders thousands of segments per frame. | Simplest engine that hits the look. |
| D28 | **Taichi** only for the pond ripple (ch5_s01, `Wave2D`). | The one real PDE in the video. |
| D29 | **PyVista** for the shaded torus, its mesh, and the mug-to-donut morph (ch4_s03–s05). The circle-to-square squash stays 2D in Manim (the rubric lists it under PyVista). | Meshes and shading. No 3D engine elsewhere: the gimbal rings and cube are projected in numpy. |
| D30 | **aion's GPU compositor** instead of the brief's ProRes or PNG passes; **FFmpeg** for encoding, muxing and loudness. | The aion pipeline renders layer stacks in one pass and audits delivery. |

## Sound

| ID | Decision | Why |
|---|---|---|
| D31 | No music in Phase 1; each scene has an `sfx_music` note. A quiet pad is suggested only under the intro title and from "landscape" to the end. | No music under dense parts (R14). Choosing music waits for the edit. |
