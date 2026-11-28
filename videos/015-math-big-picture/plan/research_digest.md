# Research digest: the rules this video applies

Sources (the context folder `my context/` in the repo root):
- **PB** = `Aion Audience Retention Playbook.md` (22 numbered rules; `PB #n` below is its number)
- **ST** = `advanced-scene-type.md` (best engine per scene type)
- **TR** = `Sample Transcript.md` (a 3Blue1Brown Laplace-transform transcript, used as the tone reference)

Scenes in `scenes.yaml` cite these IDs in `retention_device` and `engine_reason`.

| ID | Rule, as applied here | Source | Where it shows up |
|---|---|---|---|
| **R1** | **Question first.** Pose the video's question within the first seconds, then let the visuals answer it. | PB #1 | Cold open: sticks on a floor give π. "Where is the circle hiding?" |
| **R2** | **Preview the result, unexplained.** Show the payoff early and promise to explain it. TR opens on the finished diagram ("a diagram that you and I are going to build up"). | PB #3, TR | Needles converging on π before any explanation. The full Map of Math is glimpsed in the intro. |
| **R3** | **Map in one sentence, no table of contents.** | PB #2 | The intro preview is one spoken sentence while the six nodes appear. |
| **R4** | **Wrong intuition first.** "You'd think X… but watch." | PB #4 | Constant width ⇒ circle? (Ch1). Some fraction must hit π (Ch2). Symmetry is about shape (Ch3). Area grows steadily (Ch5). Chance gives chaos (Ch6). |
| **R5** | **Keep the screen moving.** Something changes every few seconds, and the reason to watch is restated at each new idea. | PB #5 | No shot holds over ~6 s unless it's a planned silent beat, and nothing is static for more than 20 s (checked from beat times). |
| **R6** | **Show progress.** Earlier results stay visible in a corner. | PB #6 | A mini Map of Math (top right) at chapter openings and takeaways. Lit nodes accumulate. |
| **R7** | **One or two open loops; plant "this matters later" and pay it off; keep every promise.** | PB #7, #8, #18 | L1 sticks → π (cold open → Ch6/Ch7). L2 e, i, π "meet in one line" (Ch3 → Ch7). L3 the map's turn (intro → Ch3). Tracked in `loops:`. |
| **R8** | **Transform, don't cut.** Morph the same object across scenes. | PB #9 | The one circle persists from the cold open to the outro. Needles become the circle. The circle becomes a wheel, a dial, a rubber band, a ripple. |
| **R9** | **Switch mode every 60–90 s; re-hook at the midpoint.** | PB #10, #11 | A pattern interrupt (engine, scale, 2D→3D, question, camera) at least every 60 s. Ch4 opens with "we still owe you the sticks". |
| **R10** | **One new idea at a time; concrete before general.** TR keeps returning to one "friendly example" (cos t) before generalizing. | PB #12, #13, TR | Each chapter: a human example (leash, wheel, lock dial, rubber band, pond/pizza, coin) before any symbol. The circle is the friendly example. |
| **R11** | **Guide the eye.** One focal point, fixed color meanings, minimal on-screen text. | PB #14 | One color per pillar for the whole video. Key words (≤ 4) and equations only. ≤ 3 things move at once. |
| **R12** | **Pause and predict.** Let the viewer guess before the reveal. | PB #15 | Where does the wheel land (Ch2)? Which points are on the circle (Ch1)? What fraction of sticks cross (Ch6)? Each has a 1.5–2 s silent beat. |
| **R13** | **Small payoff per chapter, big payoff at the end; close each chapter with a 5–10 s visual callback; end on the payoff, then point to one next video.** | PB #16, #17, #19 | One-sentence takeaway spoken over the hero image collapsing into its node, then the map turn. The outro ends on "one connected landscape", then names one next video (007, Euler's identity). |
| **R14** | **Write for the ear; audio first; cut to length.** Short sentences, no filler, read aloud. TR's warmth ("you and I", honest asides about scope, "if there is only one fact you remember…") is used sparingly. | PB #20, #21, #22, TR | Lint for banned words. Spoken numbers. No music under dense parts. Every scene has to earn its place in the circle's story. |
| **R15** | **Right engine per scene type.** Manim runs the scene, labels, equations and timing. Taichi does heavy simulation. ModernGL does custom shaders. PyVista does meshes. The heavy engines render off-screen and are composited. | ST | Manim for geometry, equations and the map. PyVista for the torus and cup. Taichi only for the pond ripple. skia for thousands of needles. All composited in aion's GPU compositor. |

## Also binding (not in the context folder)
- **Look:** Classic: pure black, crisp lines, no glow, bloom, vignette or grain. Computer Modern (roman for maths, sans for key words, small caps for names and dates). Pillar colors come from the "Aion YouTube Design System First" hue tokens. Decided 2026-11-22.
- **Narration style** (saved feedback from 2026-11-21): calm and introductory, plain words. No em dashes and no stock AI phrases. History one line at a time (who, when, what). Every concept shown as a graphic, an equation and an animation.
- **aion production rules** (`CLAUDE.md`): timing comes from the narration's word cues. Every layer is a pure function of time. Math is computed, never eyeballed. RNG is seeded.
