# The Riemann Hypothesis, Visually Explained: design sheet (v2)

Rendered reference: `out/design/design_1.png` (palette, type, motion), `design_2.png` (look frames for the spine: the
staircase rebuilt from 30 zero pairs, ζ domain coloring with the strip and zeros, the partial-sum spiral, Hardy's Z with
its crossings, off-line growth, the status ladder) and `design_3.png` (the v2 shots: the news open, Euclid's combs, the
Lehmer near-miss, the clock-arithmetic grid and scatter, the Euler-product paths, Robin's plot). All frames are computed
from the real maths. Rebuild with `uv run python videos/014-riemann-hypothesis/design_sheet.py`. The sheet uses
matplotlib's bundled Computer Modern for speed; production frames use Manim + LaTeX with the same tokens.

The look is the channel's **Classic** style: pure black, crisp unglowed lines, Computer Modern for every glyph,
symbols and key words only. No bloom, glow, blur, vignette or grain. The "After Effects" quality comes from precise
motion, continuity, parallax depth and holds, not from effects.

## Signature ideas
1. **The staircase and its waves.** π(x) is the hero object of the second and the last scene. The waves that rebuild
   it are pink because each one *is* a zero seen another way.
2. **The line of zeros is the first and last frame.** A thin green line with pink dots climbing out of the frame opens
   the video, unexplained. It becomes the source of the waves, the critical line, the axis of Hardy's Z, the line two
   zeros nearly leave at height 7005, and the closing image.
3. **Color as data.** Domain coloring is the only full-spectrum element, and hue there *means* the argument. Every
   other object keeps one fixed color, so the viewer can always tell "data" from "label".
4. **Same color, same idea.** The sieve colors of 2, 3, 5, 7 return as the combs in Euclid's proof and as the bars
   that fall out of ζ in the Euler product. The proportion bar of chapter 5 is the bar that jumps in chapter 7.
5. **Status is drawn, not just said.** Proven solid, conditional tagged, conjecture dashed, claimed outlined in amber.

**Signature shots** (each gets a hold of 1.5–2.5 s): the waves snapping onto the staircase (s02) · 211 missing every
comb (s04) · the sieve replayed inside ζ (s08) · the spiral closing on ζ(s) (s09) · the colors flowing left (s11) · the
flight up the critical line (s13) · Z's crossings pinging the zeros (s15) · the off-line drag (s17) · the zoom-out to
10³¹⁶ (s18) · the Lehmer near-miss under a two-scale magnifier (s20) · 669 primes inside the ±1 band (s22) · the jump from
5/12 to 2/3 (s25) · the Lean definition mapped onto the maths (s26) · 5040 as the last point above Robin's line (s27) ·
the status ladder's empty top rung (s30) · the reprise (s31).

## 1. Palette (`theme.py`; scenes use `C.<role>` only)
| role | hex | object | rule |
|---|---|---|---|
| `bg` | `#000000` | background | pure black |
| `grid` / `grid_minor` / `axis` | BASE | the complex plane | bright blue integer grid, dim minor grid, white axes |
| `prime` | `#ffd166` | primes: ticks, sieve survivors, factor-tree leaves, every staircase step | gold = "a prime" everywhere |
| `smooth` | `#4dd0e1` | li(x) and R(x) | the smooth model |
| `approx` | `#5b8fa3` | Gauss's density 1/ln x and x/ln x | a dimmer cousin of smooth |
| `gap` | `#fc6255` | π(x) − li(x); prime-free runs | |
| `bound` | `#c8c8c8` | the RH envelope √x log x / 8π (dashed); Robin's e^γ line (solid) | |
| `zero` | `#ff4fa3` | a nontrivial zero **and** its wave; the Z wave | one object, two views |
| `trivial` | `#8fa3b8` | the trivial zeros and the sine that makes them | cool slate: "not the mystery" |
| `crit` | `#9be564` | the critical line; the strip fill at 12% opacity | |
| `s_in` | `#6cb6ff` | the input s, the probe point, the arrows n^{−s} | |
| `zeta` | `#b78cf2` | ζ: symbol, spiral of partial sums, output point, partial-product paths | |
| `rogue` | `#ff9f1c` | a hypothetical off-line zero and its runaway wave | always labeled "what if" / "hypothetical" |
| `sieve2/3/5/7` | `#f78c6b` `#83c167` `#58c4dd` `#c792ea` | each sieving prime: combs (s04), grid (s05), Euler product (s08) | |
| `ffield` | `#cdb4db` | solutions of y² = x³ + x + 1 mod p (s22, s29) | never on screen with `sieve7` |
| `lean` | `#5cd0b3` | Lean code, kernel ticks, the file wall | machine checking |
| `ai` | `#e8a87c` | the AI as an actor (the 2026 bar segment, chips) | a neutral warm tone, no brand colors |
| `human` | `#f4efe0` | people as actors (chips, the "understood" rung) | |
| `evidence` / `claimed` / `conj` | `#8fa3b8` `#f2b544` `#a0a0a0` | status-ladder rungs | |
| `ink` | `#e8e4d8` | history: duotone portraits, the 1859 page, names and dates; Robin's points | |

**Epistemic line grammar** (used everywhere a claim appears):
- **proven:** solid stroke.
- **conditional on RH (or GRH):** solid stroke plus a small sans `if RH` / `if GRH` tag.
- **conjecture or speculation:** dashed stroke.
- **claimed:** amber outline, never filled. Nothing on screen says "proved" about the 20 Nov claim.
- **schematic** (the log axis past 10⁶ in s18, the synthetic rogue wave in s17): dashed and labeled.

## 2. Typography (all Computer Modern via LaTeX)
| voice | face | size at 1080p | used for |
|---|---|---|---|
| maths | CM roman | hero 72–96, working 48 | ζ(s), the product, ρ = ½ + iγ, Re(s) = ½ |
| key words | CM sans (`\textsf`) | 34, never under 28 | `critical line`, `trivial`, `if RH`, `claimed`, `running` |
| names and dates | CM small caps (`\textsc`) | 32–64 | `B. Riemann · 1859`, `D. H. Lehmer · 1956`, chapter cards |
| code | CM typewriter (`\texttt`) | 26–30 | the Mathlib `RiemannHypothesis` definition (s26) |

- Never a sentence on screen. A tag is at most three words; an attribution chip at most six.
- Numbers are exact where possible: `5/12`, `2/3`, `10¹³`, `175,187`, `0.0377`. No decimals for the 2026 bound.
- No logos and no screenshots of the note, of Sutherland's page or of news sites. Names appear as plain small caps.

## 3. Equation styling and reveals
- No equation is read aloud. Narration describes; the symbol confirms. Every equation is color-matched to its picture.
- `\zeta(s)=\sum 1/n^s` grows out of the bar tower (s07); each bar's label slides into the sum.
- The Euler product assembles from knockouts (s08): each `(1-p^{-s})` factor is born from a falling row in its sieve
  color, then turns white when the product is complete.
- `n^{-s}=n^{-\sigma}e^{-it\ln n}` is split in two colors, `length` and `angle`, each driven by its own slider (s09).
- The functional equation writes on with `\sin(\pi s/2)` highlighted (s11), the factor that makes the trivial zeros (s12).
- `Re(s) = ½` is written *onto* the critical line (s13).
- The explicit formula is shown once, gently (s16), with Σ_ρ in pink; then `x^\rho=x^{1/2}e^{i\gamma\ln x}` splits into
  `growth` and `wiggle`.
- The Lean definition (s26) is shown verbatim and mapped part by part onto the maths with colored leader lines.

## 4. Complex-plane visualization
- **Domain coloring** (`shaders/zeta_domain.frag`, reference `zmath.domain_rgb`):
  - hue = arg f(s), with saturation 0.85;
  - brightness = (1 − e^{−3|f|})^0.6, so zeros are black pinwheels;
  - log₂ bands at 22% contrast mark each doubling of |f|;
  - `u_func` selects the lesson functions z, z − 1, 1/z or ζ (s10);
  - `u_reveal`: a soft wavefront at σ = r(t) for continuation (s11), grayscale left of the front; at σ = 1 it keeps
    the left half black (s10);
  - `u_dim` fades the plane to a backdrop (s19, s31).
- **The critical strip**: `crit` fill at 12% between σ = 0 and 1; a 2 px `crit` line at σ = ½.
- **Zeros**: white 2 px rings when first named (s13), pink dots once the link to waves is made (s16).
- **The pole at s = 1**: a small white ×, never labeled.
- **Scale**: σ ∈ [−7, 4], t ∈ [−2, 40] fits the overview with the camera at 0.5×. The flight (s13) is a camera move.
- The v1 |ζ| landscape (PyVista) is **dropped** in v2: Hardy's Z with its crossings (s15) shows "zeros exactly on the
  line" more directly and in 2D.

## 5. Motion language
- Moves use `easy_ease` (1.2–2.0 s), fades use `smooth` (0.6 s). No `out_back` pops.
- **Waves add in** (s02, s16): each new wave draws left to right in 0.5 s while its zero dot lights. Batches stagger at
  15 ms.
- **Knockouts** (s05, s08): staggered 20–30 ms per cell, one prime per spoken word.
- **Spirals** draw tip to tail at 12 arrows/s, slowing as they converge (s09); the wandering product path (s19) never
  slows.
- **Log zooms** (s06 to 10⁶, s18 to 10³¹⁶): x-range interpolated in log space, ease in-out, 4–5 s.
- **The magnifier** (s20): a circular lens opens over 1 s; both inset scales are labeled (`t ×200`, `Z ×1000`); at full scale the bump is invisible, which is the point.
- **What-if moves** (s13, s17, s20): a ghost in `rogue` moves off, then snaps back; the real object never changes.
- At most three things move at once. Holds of 1.5–2.5 s after every signature shot.

## 6. Camera (2.5D, `s.camera`)
- Static by default. Dolly-ins (≤ 1.25×) on payoffs only.
- The **flight** up the critical line (s13) is the only long move; its height is keyed to the beats of the spoken zeros.
- Pull-backs: s01 (one tile → 175,187 tiles), s31 (the staircase into the plane).
- Parallax: the plane at 1, equations and tags at 0 (HUD); the s31 backdrop at 0.6.
- No shake, no roll, no zoom blur.

## 7. Lighting
- v2 has no lit 3D object. Light is expressed through color and line weight.

## 8. Transitions
- **Within a chapter**: continuity transforms only (the staircase, the sieve grid, the line of zeros, the proportion bar,
  the lilac grid and the tile wall carry across scenes).
- **Between chapters**: the 1.5 s `section_gap`. The last frame holds, fades to black over 0.4 s, and a symbol card
  appears (the key symbol at 96 px, held 1.2 s, with the chapter name in small caps).

| chapter | card |
|---|---|
| 1 The primes | `2, 3, 5, 7, 11, …` in `prime` |
| 2 The zeta function | `\zeta(s)` in `zeta` |
| 3 The zeros | `\zeta(s) = 0` |
| 4 How the zeros build the primes | `\pi(x)` beside the pink dots |
| 5 Why it is so hard | `10^{13} < \infty` |
| 6 What solving it would mean | `\forall\rho:\ \mathrm{Re}\,\rho=\tfrac12` |
| 7 Back to November | `20 · XI · 2026` with an amber outline `RH?` |

- **Progress corner**: a top-right stack (30 px, muted) collects `\zeta(s)`, `\prod_p`, `Re(s)=½`, the pink dots and the
  planted `Re(s)=1: ≠ 0` (s06 → s16). It shows only on chapter-opening frames.

## 9. Audio
- Narration: ElevenLabs, the same voice and settings as 011–013 (`voice.toml`), normalized to −16 LUFS.
- No music under chapters 1–6. An optional low pad, 28 dB under the voice, in the intro and the last minute.

## 10. Render plan per tool
| tool | used for | scenes |
|---|---|---|
| Manim (`s.manim()`) | staircases, waves, trees, combs, sieve, bars, spirals, equations, timelines, plots, ladder, Lean code | all |
| moderngl GLSL `shaders/zeta_domain.frag` | domain coloring lessons and ζ, the reveal wipe, the strip, backdrops | s10–s13, s19, s31 |
| numpy (`zmath.py`) → baked `.npz` | explicit-formula waves, π and li, Z(t), the Lehmer zoom, point counts, product paths, σ(n), spacings | s02, s06, s15–s22, s24, s27 |
| skia-python → `ArrayLayer` | the 175,187-tile wall, duotone portrait and 1859 page, the notes card | s01, s09, s14, s28, s31 |
| mpmath | ground truth in `verify.py` only (too slow for frames on this machine) | — |
| PyVista, Taichi | not needed in v2 | — |

**Shader validation gate** (the first implementation task): sample `zeta_domain.frag` (float32) at 1,000 points of
the frame and compare the hue with `zmath.domain_rgb` (float64). Pass if the hue error is < 2° everywhere outside a
0.02-radius disk around each zero. If it fails, fall back to numpy frames → `ArrayLayer` (cached per frame).
