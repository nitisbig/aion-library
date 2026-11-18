# 010 refinement pass (proposal, 2026-11-17)

Measured on the current previews (4 fps scan): **27.5 s of black screen** (9 gaps at chapter boundaries, up to 4.3 s)
and **109 s of frozen frames** (holds ≥ 4 s with no motion at all, longest 12.75 s). Style stays Classic (black, crisp,
CM, symbols and key words only, no glow, no captions). "Calm" means: every hold keeps a slow, purposeful motion; nothing
pops; at most ~3 things change at once.

## A. Chapter transitions and a persistent chapter rail (fills all 9 black gaps)
- Seven small symbol badges, one per chapter: `f → [⋮]`, a band, `+C`, `↻`, `λ`, a string arch, `e^{hD}`.
- At each chapter cut, instead of black: the chapter number and its title in key words (e.g. `3  ·  why + C exists`)
  rise in the centre with that chapter's badge; ~2 s; then the badge shrinks into a thin rail at the top right, where
  the finished chapters' badges sit dimmed and the current one lit.
- s16's recap gathers the seven badges into its column (the storyboard's original plan).

## B. Replace every freeze ≥ 5 s with slow, meaningful motion
| at | scene | now | refinement |
|---|---|---|---|
| 209.6 (12.8 s) | s04 band → cos | static | a slow scan line runs down the 1000 × 1000 band, lighting one row; the two samples it reads light on the sine, and the output bar lights on the cos curve |
| 476.9 (8.5 s) | s10 predict | `D f = λ f ?` alone | faint candidate curves drift through slowly behind the question |
| 502.9, 514.4 | s10 e^{λx} | static panels | a dot rides each curve with its tangent: the slope visibly equals λ × height |
| 294.0 (6.5 s) | s06 det 0 | static | x² + C family slides up and down onto the same 2x |
| 676.5 (7 s) | s14 e^{hD} | static series | the terms light one by one, each paired with D, D², D³ |
| 365.2, 330.7, 562.6, 711.0, 743.7, 59.0 | various | static | slow ambient motion: tracer dots on curves, the infinite column scrolling, λ entries pulsing in turn |

## C. Composition
- Framed panels (thin light border, the reference look) for side-by-side views: s10's candidates, s12's close-up,
  s13's mode stack vs the plucked string, s14's two graphs.
- Re-balance left-heavy frames (s07 cascade, s12) and keep the recap's right third clear for the end screen.

## D. Motion polish
- Entrances staggered with one easing family; checks/crosses scale in; every exit is a fade or a transform, never a cut.
- Continuity transforms at the within-chapter scene joins that still fade (s05→s06 matrix, s10→s11 eˣ → the plane).

Cost: A touches every scene start/end plus a shared helper in `shots.py`; B–D are per scene. Each pass ends with stills,
the pacing scan re-run (target: 0 s black, no freeze > 5 s) and a preview.
