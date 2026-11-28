# The Riemann Hypothesis, Visually Explained: storyboard (v2)

**Status:** voiced and cut on 2026-11-21 (16:20, 31 scenes); no scenes built yet.
- Script: `voiceover.md` v2, 54 paragraphs, 2,731 words. Voiced 2026-11-21: `assets/audio.wav` runs **16:20**
  (979.6 s, with a 1.5 s lead-in and a 3 s tail). The three scenes once marked optional (s24, s27, s29) stay in (decided
  2026-11-21). Editing a paragraph re-bills only its voice chunk (`uv run aion voice 014-riemann-hypothesis --dry-run`
  shows which).
- Scene times below are the real ones: the 30 cuts in `beats.py`, resolved on the voiced audio (table at the end of
  the production notes; `uv run aion beats 014-riemann-hypothesis --md` regenerates it).
- Companion files: `research.md` (every fact; codes such as A7 and M9 point to its rows), `verify.py` (every number on
  screen or spoken), `design.md` + `out/design/*.png` (the look), `theme.py` (colors), `zmath.py` (the maths behind
  every plot).

Alt titles: *The Riemann Hypothesis, Visually Explained (and What AI Just Changed)* · *The Primes Are Made of Waves* ·
*A Claimed Proof of the Riemann Hypothesis, Explained From Scratch*.

## The spine
**The primes are built from waves, one per zeta zero. The hypothesis says every wave grows as slowly as possible.**
The news opens the video (a claimed proof, 20 Nov 2026). The maths gives the viewer what they need to judge it. The
last chapter judges it with the viewer, carefully. The first and last frames are the same image: a line of zeros
climbing out of the frame.

Tone: calm, first-person, introductory. Every concept appears as a picture first, then as an equation that is
color-matched to the picture, then moves. History comes as short ink-colored cards (name, year), never as a lecture.

## Chapter structure
| # | chapter | scenes | time | small payoff |
|---|---|---|---|---|
| 0 | Intro: the claim, the staircase, the waves | s01–s03 | 0:00–1:52 | the waves snap onto the staircase; every source sits on one line |
| 1 | The primes | s04–s06 | 1:52–3:40 | 211 misses every comb; PNT; "how far apart can they get?" |
| 2 | The zeta function | s07–s11 | 3:40–6:23 | the sieve inside ζ; the spiral; the colors flow left |
| 3 | The zeros | s12–s15 | 6:23–8:11 | the flight up the critical line; RH stated; crossings = zeros |
| 4 | How the zeros build the primes | s16–s17 | 8:11–9:26 | the opening explained; the off-line blow-up |
| 5 | Why it is so hard | s18–s22 | 9:26–11:36 | 10³¹⁶; the Lehmer near-miss; stuck at 5/12; the proved finite-field version |
| 6 | What solving it would mean | s23–s24 | 11:36–12:33 | proof vs one counterexample; what changes, what doesn't |
| 7 | Back to November | s25–s30 | 12:33–15:45 | 5/12 → 2/3; what Lean checks; the status ladder |
| 8 | Outro | s31 | 15:45–16:20 | staircase and line together; the 1859 callback |

**Chapter cards** sit in the 1.5 s `section_gap`: the last frame holds, fades over 0.4 s, and a symbol card shows for
1.2 s (96 px symbol, chapter name in small caps): `2, 3, 5, 7, 11, …` (prime) · `\zeta(s)` (zeta) · `\zeta(s)=0` ·
`\pi(x)` beside pink dots · `10^{13} < \infty` · `\forall\rho:\ \mathrm{Re}\,\rho=\tfrac12` · `20 · XI · 2026` with an
amber outline `RH?`.

**Mode switches** (a new kind of picture every 30–60 s): news cards → number line and staircase → factor trees and
combs → grid sieve → log zoom → bar tower → bars falling out → portrait and plane → arrows and spiral → color field →
wavefront → flight → manuscript and timeline → wave and count → explicit waves → drag → 300-digit log flight → magnified
near-miss → progress bar → finite-field grid → theorem shelf → histogram → code → divisor plot → checklist → ladder →
reprise.

## Promises tracked
| promise | made | paid |
|---|---|---|
| "you can judge for yourself what has been established" | s01, s03 | s25–s30 |
| "each wave comes from one point … the same vertical line" | s02 | s13 (it's the critical line), s16 (why waves), s17 (why the line matters) |
| the sieve "will come back in a different form" | s05 | s08 (the Euler product knocks out the same colors) |
| "one fact about where its zeros can't be" | s06 | s16 (no zero on Re = 1) |
| "how far apart can they get?" | s06 | s17 (√x ln x envelope; von Koch) |
| the clock-arithmetic version | s22 | s29 (the claimed argument descends from Stepanov's method) |
| Riemann "put aside the search for a proof" | s14 | s31 |

## Continuity spine (the same objects, never redrawn)
- **The line of zeros**: s01 (unexplained, first frame) → s02 (each dot sources a wave) → s13 (the critical line) → s15
  (crossings ping its dots) → s16–s17 → s20 (two dots split off in the near-miss) → s23 (∀ vs ∃) → s31 (last frame).
- **The staircase π(x)**: s02 → s06 (zoom out to 10⁶) → s16 → s17 (as π − li) → s31.
- **Sieve colors**: s04 (the combs of multiples) → s05 (grid knockouts) → s08 (bars falling out of ζ).
- **The proportion bar**: s21 (creeps to 5/12) → s25 (jumps to 2/3) → s30 (a rung of the ladder).
- **The Z wave**: s15 (crossings = zeros) → s20 (magnified at height 7005).
- **The lilac grid of solutions mod p**: s22 → s29.
- **The tile wall of 175,187 files**: s01 → s28 → s31 (faint).
- **The 1859 quote card**: s14 → s31.

## Concept → graphic · equation · animation
Every math idea in the script, with the picture that carries it, the symbol that confirms it (color-matched), and the
motion that makes it happen.

| concept | scene | graphic | equation | animation |
|---|---|---|---|---|
| prime-counting staircase | s02 | gold ticks become a staircase | `\pi(x)=\#\{p\le x\}` | a cursor sweeps right; each tick lifts one step |
| waves rebuild the primes | s02, s16 | pink waves summed onto the cyan curve | `\pi(x)\approx R(x)-\sum_\rho R(x^\rho)` | batches of 1, 5, 30, 100 blend in; each lights its zero |
| unique factorization | s04 | two different factor trees of 60, same leaves | `60=2^2\cdot3\cdot5` | both trees grow; leaves merge into one sorted row |
| infinitely many primes (Euclid) | s04 | combs of multiples of 2, 3, 5, 7; 210 hits all; 211 hits none | `2\cdot3\cdot5\cdot7+1=211`, `211\equiv1 \pmod p`; `30031=59\cdot509` | a cursor stops at 210 (four teeth flash), steps to 211 (none) |
| sieve of Eratosthenes | s05 | 10 × 10 grid, knockouts in each prime's color | legend chips `2 3 5 7` | color sweeps, one prime at a time; survivors turn gold |
| prime gaps | s05 | brackets over twins; a red run 90–96 | `97-89=8` | bracket slides; run outlines |
| prime density (Gauss) | s06 | block counts vs a curve | `\Pr(n\text{ prime})\approx 1/\ln n` | bars rise to meet `1/\ln x` |
| logarithmic integral | s06 | area under 1/ln t accumulating | `\mathrm{li}(x)=\int_2^x dt/\ln t` | area fills; its running total traces li |
| prime number theorem | s06 | ratio π/li on a log axis | `\pi(x)/\mathrm{li}(x)\to1` | ratio curve flattens onto 1 |
| the error | s06, s17 | red band between staircase and curve | `\pi(x)-\mathrm{li}(x)` | a ruler measures it; `?` |
| series and convergence | s07 | tower of bars with a running-total needle | `\zeta(s)=\sum n^{-s}`; `\sum 1/n=\infty`; `\sum 1/n^2=\pi^2/6` | dial s from 1 to 2; the tower stops settling or settles |
| Euler product | s08 | the same bars falling out in sieve colors | `\zeta(s)\prod_p(1-p^{-s})=1` | knockouts replay the sieve; factors assemble; the equation flips |
| complex numbers | s09 | plane, probe point, projections | `s=\sigma+it` | probe slides; projections follow |
| one term as an arrow | s09 | arrow with length and angle | `n^{-s}=n^{-\sigma}e^{-it\ln n}` | σ slider changes lengths only; t slider changes angles only |
| partial sums as a spiral | s09 | arrows tip to tail | `\zeta(s)=\lim_N\sum_{n\le N}n^{-s}` | the chain curls and closes on the ζ(s) dot |
| domain coloring | s10 | colored plane + color wheel + band key | hue `=\arg f`, bands `=\log_2|f|` | crossfade `z` → `z-1` → `1/z` → ζ |
| a zero | s10 | a pinwheel | `f(z_0)=0` | zoom into the point where all colors meet |
| where the sum fails | s10 | right half colored, left half black; an open spiral | `\sum n^{-s}` diverges for `\mathrm{Re}\,s\le1` | probe dragged left; spiral never closes |
| analytic continuation | s11 | inset: partial sums vs `1/(1-x)`; main: colors flow left | `1+x+x^2+\cdots=\frac1{1-x}` | partial sums settle or explode; a wavefront carries the colors left |
| rigidity | s11 | a small patch pulses, then decides the rest | (said in words) | patch pulse, then the flow |
| functional equation | s11 | dashed arc linking s and 1 − s through ½ | `\zeta(s)=2^s\pi^{s-1}\sin(\tfrac{\pi s}2)\Gamma(1-s)\zeta(1-s)` | arc draws; the sine glows |
| trivial zeros | s12 | sine under the axis aligned with pinwheels | `\sin(\pi s/2)=0` at `s=-2,-4,\dots` | dashed links drop from sine zeros to pinwheels |
| critical strip and line | s13 | green band, green line | `0<\mathrm{Re}\,s<1`, `\mathrm{Re}\,s=\tfrac12` | fill, then the line draws |
| the first zeros | s13 | pinwheels ringed on the line | `\rho=\tfrac12+i\gamma`, `\gamma_1=14.1347\ldots` | camera flight; each zero lands on its spoken number |
| mirror symmetry | s13, s17 | a ghost off-line zero and its twin | `\rho\leftrightarrow1-\bar\rho` | ghost drags off; twin appears |
| the hypothesis | s14 | boxed statement over the line | `\zeta(\rho)=0,\ 0<\mathrm{Re}\,\rho<1\Rightarrow\mathrm{Re}\,\rho=\tfrac12` | writes on; the line glows |
| Hardy's Z | s15 | a real wave under the line | `Z(t)=e^{i\theta(t)}\zeta(\tfrac12+it)\in\mathbb R` | each crossing pings a pinwheel above it |
| counting zeros | s15 | crossing staircase vs smooth count | `N(T)\approx\frac{T}{2\pi}\ln\frac{T}{2\pi e}+\frac78` | the two staircases agree |
| what a zero does to its wave | s16 | one wave in a dashed envelope | `x^\rho=x^{1/2}e^{i\gamma\ln x}` | γ slider: faster wiggle; envelope ±√x |
| no zero on Re = 1 | s16 | the line Re = 1 marked | `\zeta(1+it)\ne0` | the planted line glows |
| an off-line zero | s17 | one wave ballooning | `|x^\rho|=x^{\mathrm{Re}\,\rho}` | drag the zero to 0.8; its wave escapes the envelope |
| the RH error bound | s17 | dashed envelope around the error | `|\pi(x)-\mathrm{li}(x)|<\frac{\sqrt x\ln x}{8\pi}` `if RH` | the real error stays inside to 10⁶ |
| von Koch's equivalence | s17 | two-way arrow | `\mathrm{RH}\iff\pi(x)=\mathrm{li}(x)+O(\sqrt x\ln x)` | the arrow draws both ways |
| the smallest possible error | s17 | mirrored pairs | `\Theta=\sup\mathrm{Re}\,\rho\ge\tfrac12` | a slider stops at ½ |
| evidence vs proof | s18 | a tiny bracket on an endless line; a log axis to 10³¹⁶ | `\pi(x)-\mathrm{li}(x)` changes sign infinitely often | zoom out over 300 orders of magnitude |
| where the product works | s19 | lit half-plane; settling vs wandering paths | `\prod_p(1-p^{-s})^{-1}` for `\mathrm{Re}\,s>1` | the probe crosses into the strip |
| near-miss | s20 | Z magnified near t = 7005 (≈ ×200 in t, ×1,000 in Z) | gap `0.0377` vs mean `0.8955`; peak `0.004` | zoom; a ghost shift breaks the two crossings |
| no room to spare | s20 | a slider against a wall | `\mathrm{RH}\iff\Lambda\le0`, `\Lambda\ge0` | the slider bumps at 0 |
| proportion of zeros | s21 | progress bar | `>0`, `1/3`, `2/5`, `5/12` | fill creeps, then freezes |
| 100% ≠ all | s21 | perfect squares among whole numbers | `\lfloor\sqrt N\rfloor/N\to0` | N grows, the fraction falls, the squares keep coming |
| clock arithmetic | s22 | a clock face with p hours | `a\equiv b\pmod p` | the hand wraps past p |
| counting solutions mod p | s22 | lilac dots on a p × p grid; a scatter for all p < 5000 | `|A_p-p|\le2\sqrt p` | points populate; every scatter point lands inside ±1 |
| proof vs counterexample | s23 | a bracket over the whole line vs one rogue dot | `\forall\rho` vs `\exists\rho` | side by side |
| conditional results | s23 | a shelf of theorem cards tagged `if RH` / `if GRH` | Cramér's gap bound | tags fade under "unconditional" |
| GRH | s23 | many faint critical lines | `L(s,\chi)=\sum\chi(n)n^{-s}` | the lines fan out |
| zero spacing (speculation) | s24 | histogram vs a dashed curve | `GUE` prediction | bars rise to meet the dashed curve |
| a formal proof | s26 | chain of steps down to three axioms | the Lean definition of `RiemannHypothesis` | the kernel ticks each step |
| statement fidelity | s26 | code mapped to the maths | `riemannZeta s = 0` ↔ `\zeta(s)=0` … | mapping lines draw part by part |
| Robin's criterion | s27 | σ(n)/(n ln ln n) under the line e^γ | `\sigma(n)<e^\gamma n\ln\ln n\ (n>5040)` | points stream; 5040 is the last one above |
| multiplicity | s29 | graphs touching the axis | `f(a)=f'(a)=\cdots=0` | morph between orders 1, 2, 3 |

## Epistemic grammar (design.md §1)
proven = solid · conditional = solid + `if RH` / `if GRH` tag · conjecture = dashed · **claimed = amber outline, never
filled**. Nothing on screen says "proved" about the 20 Nov claim. AI statements are always attributed to a person or a
paper.

---

## Scenes

Each scene lists: **⏱** duration · **?** narrative purpose · **👁** visual · **⚙** technology · **🎬** animation ·
**▣** on-screen elements · **🎙** narration (voiceover paragraphs) · **📚** references · **∑** concept → graphic ·
equation · animation (repeated from the table so each scene card stands alone).

### Intro

#### s01 news (0:00–0:50, ≈ 50 s)
- **?** Hook with the news, stated exactly. Stakes. The promise that the viewer will be able to judge it.
- **👁** First frame: black, with a thin green vertical line at the right third and pink dots climbing it out of the top of
  the frame, unlabeled (the line of zeros, planted). Left: a small-caps date types on, then a plain card
  `L. Alpöge · Anthropic` and the claim in an **amber outline** (`claimed: a proof of the Riemann hypothesis`). No logos,
  no screenshots of the note or of news sites. On "files in Lean" the card dissolves into one teal tile; the camera pulls
  back to a wall of exactly 175,187 tiles (one per file, 419 per row). On "still under way" a thin row of check rings sits
  under the wall, some filled, some open. On P03 two chips: `1859` and `$1,000,000`. On "prime numbers" the wall collapses
  into one gold dot, which drops onto a number line (match cut into s02).
- **⚙** skia-python renders the tile wall at 4K → `ArrayLayer`, camera zoom. Manim for text, the line and dots.
- **🎬** The line of zeros fades in during the 1.5 s lead-in. Date at "November the twentieth". The amber outline draws
  (0.8 s) at "proof of the Riemann hypothesis" and is never filled. Pull-back 4 s `easy_ease`. Chips 0.5 s each. Collapse
  1.2 s.
- **▣** `20 · XI · 2026` · `L. Alpöge · Anthropic` · `Claude` · amber `claimed` · `175,187 Lean files` · `checks running`
  · `1859` · `$1,000,000`.
- **🎙** P01–P04.
- **📚** A7, A8, A9, A12, M1.
- **∑** No maths yet; the line of zeros is a visual question.

#### s02 staircase (0:50–1:37, ≈ 48 s)
- **?** The hook proper: the primes look lawless, waves rebuild them, and every wave's source sits on one line.
- **👁** Gold ticks land on a number line 0–100 at the 25 primes. The line tilts into the x-axis of a plot and the gold
  staircase rises out of the ticks. A cyan smooth curve R(x) follows the trend, with no corners. Pink waves are added: 1,
  5, 30, 100 zero pairs. The curve wobbles, sharpens and turns a corner at every prime. The s01 line of zeros is now the
  source: each wave lights its dot (14.13, 21.02, 25.01, …). Final hold: staircase, curve on it, line of dots.
- **⚙** `zmath.pi_explicit` baked for k = 0, 1, 5, 30, 100 (x ∈ [1, 100], 4,000 samples) to `assets/explicit.npz`.
  Manim `m.redraw` draws the curve as a pure function of time, interpolating between k levels.
- **🎬** Ticks land with a 40 ms stagger; a counter beside the staircase climbs to 25. Staircase draws 2 s `smooth`. Each
  wave batch blends 1.5 s `easy_ease` on "single", "five", "thirty", "a hundred" while its dots light bottom to top.
  Camera push 1.0 → 1.12× on "turns a corner"; 2 s hold. On "same vertical line" the dots brighten together. On
  "infinitely many" the line extends past the top of the frame.
- **▣** `\pi(x)` (gold) · `R(x)` (cyan, small) · `waves: 1 → 5 → 30 → 100` · `25 primes`.
- **🎙** P05–P07.
- **📚** verify.py explicit-formula checks (max error 0.90 → 0.25 at 100 pairs); M12.
- **∑** staircase → gold steps from ticks · `\pi(x)=\#\{p\le x\}` · cursor lifts a step per tick. Waves → pink
  waves on the cyan curve · formula withheld until s16 · batches blend in, each lighting its zero.

#### s03 map (1:37–1:52, ≈ 15 s)
- **?** Roadmap, and the promise restated.
- **👁** The s02 frame shrinks into the top-left corner. Five small icons slide into a row, each lighting as it's named:
  `\zeta(s)`, a pinwheel, a near-miss wave, a theorem card with an `if RH` tag, and the amber `20 Nov` outline. The progress
  corner (design.md §8) starts collecting symbols from here.
- **⚙** Manim.
- **🎬** Icons 0.5 s each on their words, then the chapter card `1 · The primes`.
- **▣** icons only.
- **🎙** P08.
- **📚** —
- **∑** —

### CH1 The primes

#### s04 atoms (1:52–2:22, ≈ 30 s)
- **?** Primes are the building blocks (unique factorization); Euclid's proof that they never run out.
- **👁** (a) 60 splits as a factor tree 6 · 10 → 2 · 3 · 2 · 5; beside it a second tree 4 · 15 → 2 · 2 · 3 · 5. Both sets
  of gold leaves slide down into the same sorted row. (b) A number line 0–220 carrying four combs: the multiples of 2, 3,
  5 and 7, drawn as teeth in the sieve colors. At 210 = 2·3·5·7 all four combs have a tooth. At 211 none does. Under it,
  remainder chips: `211 = 105·2 + 1`, `70·3 + 1`, `42·5 + 1`, `30·7 + 1`. (c) The general case: `2·3·5·7·11·13 + 1 =
  30031 = 59 · 509`, both factors new. The point is that the product + 1 need not be prime; its factors are new.
- **⚙** Manim (`MathTex`, trees as `VGroup`s, `NumberLine` with tick combs).
- **🎬** Trees grow top-down, 0.6 s per level, staggered; leaves merge 1 s on "only one way". Combs draw left to right
  (0.4 s each, staggered by prime). A white cursor slides to 210 (all four teeth flash), steps to 211 (nothing), hold
  1.5 s. Chips at "remainder of one". The 30031 card on "all new".
- **▣** `60=2\cdot2\cdot3\cdot5` (gold leaves) · `2\cdot3\cdot5\cdot7+1=211` · remainder chips ·
  `30031=59\cdot509` · `Euclid · c. 300 BC`.
- **🎙** P09–P10.
- **📚** M16 (unique factorization), M17 (Euclid); verify.py (211 prime, 30031 = 59 · 509, 60 = 2²·3·5).
- **∑** unique factorization → two trees, same leaves · `60=2^2\cdot3\cdot5` · leaves merge. Infinitely many primes →
  combs of multiples · `p_1\cdots p_k+1\equiv1\pmod{p_i}` · the cursor at 210 hits every comb, 211 misses all.

#### s05 sieve (2:22–2:49, ≈ 27 s)
- **?** How primes are found (planting the sieve for s08); irregular up close.
- **👁** A 10 × 10 grid of 1–100 (1 dimmed). Multiples of 2 (not 2 itself) fade to `sieve2`, then 3, 5 and 7 in their
  colors; survivors turn gold. On P12: brackets over 11·13 (others faint: 17·19, 29·31, 41·43, 59·61, 71·73), and cells
  90–96 outlined in `gap` red.
- **⚙** Manim.
- **🎬** Knockouts sweep with a 30 ms stagger per cell, one prime per spoken word. Survivors pulse once. Brackets 0.5 s;
  red outline on "eighty-nine".
- **▣** legend chips `2 3 5 7` · `11, 13` · `89 → 97`.
- **🎙** P11–P12.
- **📚** verify.py (π(100) = 25, twins below 100, the 89 → 97 gap).
- **∑** sieve → grid knockouts · legend chips · color sweep per prime. Gaps → brackets and a red run · `97-89=8` ·
  bracket slides.

#### s06 pnt (2:49–3:40, ≈ 51 s)
- **?** Order at large scale: density, li(x), the prime number theorem, and the planted question: how big is the gap?
- **👁** The grid collapses into the staircase; the camera zooms out on a log x-axis from 100 to 10⁶ and the staircase
  turns smooth-looking. Density panel: the fraction of primes in blocks of 10,000 as bars, against the curve 1/ln x
  (`approx`). `C. F. Gauss · 1792` card (aged 15). li(x) (cyan) appears as the accumulated area under 1/ln t. The ratio
  π(x)/li(x) on log x approaches 1 (0.99835 at 10⁶). Cards `J. Hadamard` and `C. de la Vallée Poussin`, `1896`. On "one
  fact about where its zeros can't be", a tiny `\mathrm{Re}(s)=1` line drifts into the progress corner (planted for s16).
  On P15: zoom into a stretch near 10⁵; the gap between staircase and li fills red; a ruler with `?` measures it.
- **⚙** Manim; π(x) and li(x) baked from `zmath` to `assets/pnt.npz` (log grid, 10 to 10⁶).
- **🎬** Zoom-out 4 s `easy_ease` (x-range interpolated in log space). Bars grow with an 80 ms stagger. Area fill 2 s;
  ratio curve 2 s. Cards 0.6 s. Red fill 1 s on "never matches"; ruler and `?` on "How far apart"; hold 2 s.
- **▣** `\Pr(n\text{ prime})\approx1/\ln n` · `\mathrm{li}(x)=\int_2^x\frac{dt}{\ln t}` · `\pi(10^6)=78{,}498` ·
  `\mathrm{li}(10^6)\approx78{,}628` · `\pi(x)/\mathrm{li}(x)\to1` (`1896`) · `\pi(x)-\mathrm{li}(x)=\ ?`
- **🎙** P13–P15.
- **📚** M5, M6; verify.py (π(10⁶), li ratio 0.99835, density 1/13.8).
- **∑** density → bars vs curve · `\Pr\approx1/\ln n` · bars rise to meet it. li → area · `\int dt/\ln t` · area
  accumulates into the curve. PNT → ratio plot · `\pi/\mathrm{li}\to1` · the curve flattens onto 1. Gap → red band ·
  `\pi-\mathrm{li}=?` · ruler.

### CH2 The zeta function

#### s07 series (3:40–4:08, ≈ 28 s)
- **?** ζ(s) as a sum; what it means for a sum to have a value; Euler and π²/6.
- **👁** Bars of height 1/n^s stack into a tower; a needle tracks the running total; a dial shows s. At s = 1 the tower
  climbs past every gridline (`∞`). The dial turns to s = 2 and the tower settles on a dashed line at π²/6 ≈ 1.645.
  `L. Euler · 1734`.
- **⚙** Manim; s is a Track driving `m.redraw`.
- **🎬** Terms appear one per 0.12 s, accelerating. Dial 1 → 2 on "When s is two" (1.5 s); hold on π²/6.
- **▣** `\zeta(s)=1+\frac1{2^s}+\frac1{3^s}+\cdots=\sum_{n\ge1}\frac1{n^s}` · `s=1:\ \infty` · `s=2:\ \frac{\pi^2}{6}`.
- **🎙** P16–P17.
- **📚** M4; verify.py (Basel).
- **∑** series and convergence → tower and needle · `\sum1/n=\infty`, `\sum1/n^2=\pi^2/6` · the dial decides whether
  it settles.

#### s08 euler (4:08–4:36, ≈ 27 s)
- **?** The Euler product: the sieve hides inside ζ, which is why ζ knows the primes.
- **👁** The tower's terms lie in a row, bars labeled n. "× (1 − 1/2^s)": every even bar drops out in `sieve2`, the same
  color as in the sieve. "× (1 − 1/3^s)": the remaining multiples of 3 drop in `sieve3`. Then 5, 7, … until only bar `1`
  remains. The factors stack on the left; the equation flips to the product, and the factors turn white when it's complete.
  The s05 grid sits small in a corner, its knockouts replaying in sync.
- **⚙** Manim (`TransformMatchingTex` for the flip).
- **🎬** Each knockout 0.8 s with a 20 ms stagger, on "two", "three", "every prime". Hold on `= 1` for 1 s; flip 1.5 s;
  hold 2 s.
- **▣** `\zeta(s)(1-2^{-s})(1-3^{-s})(1-5^{-s})\cdots=1` → `\zeta(s)=\prod_p\frac1{1-p^{-s}}` (tag `Re(s) > 1`).
- **🎙** P18.
- **📚** M3.
- **∑** Euler product → bars falling out in sieve colors · `\zeta(s)\prod_p(1-p^{-s})=1` · the knockouts replay the
  sieve and the factors assemble.

#### s09 complex (4:36–5:12, ≈ 37 s)
- **?** Riemann's move to complex s; ζ as a spiral of arrows.
- **👁** History: a public-domain portrait of Riemann (ink duotone) beside the first page of the 1859 paper (public
  domain), `B. Riemann · 1859 · 9 pp.`, `his only paper on number theory`. Then the plane (Classic grid), a probe
  s = σ + it (`s_in`) with dashed projections. The arrows n^{−s}, n = 1 … N, chain tip to tail. The formula
  `n^{-s}=n^{-\sigma}e^{-it\ln n}` is color-split: n^{−σ} labeled `length`, t ln n labeled `angle`. Moving σ only
  changes lengths; moving t only turns the arrows, each by t ln n. At s = 1.4 + 6i the chain curls into a spiral that
  closes on the purple ζ(s) dot.
- **⚙** Manim; arrows from numpy each frame (`m.redraw`); skia duotone → `ArrayLayer` for the portrait and the page.
- **🎬** Portrait and page 0.6 s, gone after 6 s. Probe on "complex number". First five arrows on "arrow". σ slider
  1.4 → 2.0 → 1.4 on "length"; t slider 0 → 6 on "turns". 200 arrows draw at 12 per second, slowing; the ζ(s) dot lands
  with a ring; hold 1.5 s.
- **▣** `s=\sigma+it` · the color-split formula · `\zeta(1.4+6i)` at the dot.
- **🎙** P19–P20.
- **📚** M1; Wikimedia Commons public-domain images (credit in `assets/photos/CREDITS.md`).
- **∑** complex number → plane and probe · `s=\sigma+it` · projections follow the probe. One term → an arrow ·
  `n^{-\sigma}e^{-it\ln n}` · the two sliders separate length from angle. Partial sums → a spiral ·
  `\lim_N\sum_{n\le N}n^{-s}` · the chain closes on ζ(s).

#### s10 coloring (5:12–5:43, ≈ 31 s)
- **?** How to see a complex function; what a zero looks like; ζ so far only exists right of Re = 1.
- **👁** A color wheel legend (hue = direction of the output) and a band key (each band = a doubling of size). f(z) = z:
  one pinwheel at 0 where all colors meet. f(z) = z − 1: the pinwheel moves to 1. f(z) = 1/z: the colors run the other way
  (a pole). Then ζ, colored only for Re > 1, with the left half black. The s09 probe rides on the color; dragged left past
  Re = 1, its spiral never closes (dashed, endless).
- **⚙** `shaders/zeta_domain.frag` (`u_func` picks z, z − 1, 1/z or ζ; `u_reveal` at σ = 1 keeps the left black) + Manim
  overlays.
- **🎬** 1 s crossfades on "hue", "bands", "colors meet"; zoom into the pinwheel on "exactly zero". ζ wipes in from the
  right (2 s) on "This is zeta"; probe drag 2 s on "Left of the line".
- **▣** wheel `\arg f` · bands `1, 2, 4, …` · `z`, `z-1`, `1/z`, `\zeta(s)` · dashed `\mathrm{Re}(s)=1` · `no value`.
- **🎙** P21–P22.
- **📚** design.md §4; the shader validation gate (design.md §10).
- **∑** domain coloring → colored plane + legend · hue `=\arg f`, bands `=\log_2|f|` · `z → z−1 → 1/z`. A zero →
  pinwheel · `f(z_0)=0` · zoom in. Divergence → black half, open spiral · `\sum n^{-s}` diverges for `\mathrm{Re}\,s\le1`
  · probe dragged left.

#### s11 continuation (5:43–6:23, ≈ 40 s)
- **?** A formula can outlive its sum; rigidity; Riemann's extension; the functional equation.
- **👁** Inset (left): a real line −2 … 2. Partial sums of 1 + x + x² + … at a few x settle inside (−1, 1) (green ticks)
  and blow up outside (red). The graph of 1/(1 − x) (cyan) matches inside and carries on outside, except at the asymptote
  x = 1. Main: back to the ζ plane. A small square patch at Re > 1 pulses ("rigid"). Then the colors flow left as a
  wavefront across Re = 1 and fill the whole plane, with a white × at s = 1. Then the symmetry: a dashed arc links s
  and 1 − s through ½, and the functional equation writes on with sin(πs/2) highlighted.
- **⚙** Manim inset; `zeta_domain.frag` with `u_reveal` moving the front from σ = 1 to σ = −7 (left of the front in
  grayscale); Manim for the equation and arc.
- **🎬** Inset sums n = 1 → 20 over 3 s; 1/(1 − x) draws 1.5 s on "one over one minus x". Patch pulse on "small patch".
  The wavefront takes 6 s `easy_ease` on "the whole plane" (a signature shot). Arc 1 s on "symmetry"; equation 2 s; the
  sine glows for 2 s.
- **▣** `1+x+x^2+\cdots=\frac1{1-x}\ (|x|<1)` · `x\neq1` · `\zeta(s)=2^s\pi^{s-1}\sin(\tfrac{\pi s}2)\Gamma(1-s)\zeta(1-s)`
  · `s\leftrightarrow1-s`.
- **🎙** P23–P24.
- **📚** M1; verify.py (ζ vs mpmath including σ < 0; ζ(−1) = −1/12).
- **∑** continuation → partial sums vs 1/(1 − x), colors flowing left · `\sum x^n=\frac1{1-x}` · settle or explode, then
  the wavefront. Rigidity → a patch decides the rest · in words · pulse, then flow. Functional equation → mirror arc ·
  the full equation, sine highlighted · arc draws, sine glows.

### CH3 The zeros

#### s12 trivial (6:23–6:39, ≈ 16 s)
- **?** Where the trivial zeros come from.
- **👁** Along the negative real axis, the graph of sin(πs/2) (`trivial`) sits under the plane; its zeros at −2, −4, −6
  line up with pinwheels, which get `trivial` rings and the tag `trivial`.
- **⚙** shader + Manim.
- **🎬** Sine draws 1.5 s; dashed links drop to the pinwheels with a 0.3 s stagger on "minus two, minus four, minus six".
- **▣** `\sin(\pi s/2)=0` at `s=-2,-4,-6,\dots` · `trivial`.
- **🎙** P25.
- **📚** M1.
- **∑** trivial zeros → sine aligned with pinwheels · `\sin(\pi s/2)=0\Rightarrow\zeta(-2k)=0` · links drop.

#### s13 strip (6:39–7:12, ≈ 33 s)
- **?** Where the other zeros live; the line; the first zeros; mirror symmetry.
- **👁** The band 0 < Re < 1 fills with `crit` at 12%; the line Re = ½ draws. **The flight:** the camera flies up the
  line past pinwheels at 14.13, 21.02, 25.01, 30.42, 32.94 and 37.59, each ringed white and labeled as it lands. Then a
  "what if": a ghost zero (`rogue`, dashed ring) slides off to 0.8 + 40i and its twin appears at 0.2 + 40i, joined by a
  dashed arc. Both fade.
- **⚙** `zeta_domain.frag` + `s.camera`; Manim rings and labels. The ghost pair is an overlay only.
- **🎬** Fill 1 s on "critical strip"; line 1.2 s on "critical line". Flight 9 s `easy_ease`, with the camera's height
  keyed to beats so each zero arrives on its spoken number. Ghost pair 1.5 s on "come with a partner".
- **▣** `0<\mathrm{Re}(s)<1` · `\mathrm{Re}(s)=\tfrac12` · `\rho=\tfrac12+i\gamma` · `14.1347`, `21.0220`, `25.0109`,
  `30.4249`, `32.9351`, `37.5862` · `\rho\leftrightarrow1-\bar\rho`.
- **🎙** P26–P27.
- **📚** verify.py (first zeros); M12.
- **∑** strip and line → green band and line · `0<\mathrm{Re}\,s<1`, `\mathrm{Re}\,s=\tfrac12` · fill, draw. Zeros →
  ringed pinwheels · `\rho=\tfrac12+i\gamma` · the flight. Symmetry → ghost pair · `\rho\leftrightarrow1-\bar\rho` ·
  drag off, twin appears.

#### s14 riemann (7:12–7:37, ≈ 26 s)
- **?** The hypothesis stated, with its history: Riemann's notes, "very likely", Hilbert, the Clay prize.
- **👁** An ink card: `Riemann's notes · studied by C. L. Siegel, 1932` (a public-domain scan of a page from the
  Nachlass if a clean one exists, otherwise a plain card). The 1859 quote writes on in German with an English line
  under it: `es ist sehr wahrscheinlich, dass alle Wurzeln reell sind` / `very likely all the roots are real` (his
  form of "all on the line"). On "put aside" the card literally slides aside. The boxed statement writes on over the line
  of zeros. A timeline: `1859` → `1900 · D. Hilbert · problem 8` → `2000 · Clay · $1M` → `2026`.
- **⚙** Manim; skia → `ArrayLayer` for any scan.
- **🎬** Notes card 0.6 s; quote 1.5 s on "very likely"; slide-aside 0.8 s on "put aside". Statement 2 s on "That's the
  Riemann hypothesis", hold 2 s, the line glows. Timeline markers drop on their years.
- **▣** quote + translation · the boxed statement · `D. Hilbert · 1900` · `Clay · 2000 · $1,000,000`.
- **🎙** P28.
- **📚** M1, M2, M14, A12, H1 (Hilbert 1900), H2 (Clay 2000).
- **∑** the hypothesis → boxed statement over the line ·
  `\zeta(\rho)=0,\ 0<\mathrm{Re}\,\rho<1\Rightarrow\mathrm{Re}\,\rho=\tfrac12` · writes on; the line glows.

#### s15 checking (7:37–8:11, ≈ 34 s)
- **?** How anyone knows a zero is exactly on the line; Turing; ten trillion.
- **👁** The plane rotates 90° so the critical line runs left to right along the top (t ∈ [0, 60]). Below it, the graph of
  Z(t) over the same t. Every crossing of Z pings a vertical link up to a pinwheel: two views of one zero, both pink.
  Then a staircase of crossings against the smooth count (cyan); they agree. `A. Turing · 1950s`. A counter rolls to
  `10,000,000,000,000 zeros · all on the line`.
- **⚙** Manim; Z(t) and θ(t) baked from `zmath` (`assets/zline.npz`); the shader strip above.
- **🎬** Rotation 2 s. Z draws left to right over 4 s; pings 0.3 s at each crossing. Count steps rise with the pings; the
  smooth count draws on "a separate count". The two coincide on "every one of them". Turing card 0.6 s. Counter 3 s.
- **▣** `Z(t)=e^{i\theta(t)}\zeta(\tfrac12+it)\in\mathbb R` · `N(T)\approx\frac{T}{2\pi}\ln\frac{T}{2\pi e}+\frac78` ·
  `A. Turing · 1950s` · `10^{13}`.
- **🎙** P29–P30.
- **📚** verify.py (649 zeros up to 1000 by sign changes, matching N(T)); M12; H3 (Turing).
- **∑** Hardy's Z → a real wave under the line · `Z(t)\in\mathbb R` · crossings ping pinwheels. Counting →
  two staircases · `N(T)` · they agree.

### CH4 How the zeros build the primes

#### s16 explicit (8:11–8:47, ≈ 36 s)
- **?** Pay off the opening: the explicit formula, and what a zero's height and real part do.
- **👁** The s02 frame fades up exactly, but now each wave carries its zero's label. The formula writes on with Σ_ρ in
  pink. One wave is isolated (others dim to 15%): R(x^ρ) for ρ = ½ + 14.13i inside a dashed envelope ±√x, with
  `x^\rho=x^{1/2}e^{i\gamma\ln x}` color-split (`growth` | `wiggle`). A γ slider raises the zero: the wave wiggles faster.
  On P33 the planted `Re(s) = 1` line returns from the progress corner beside the strip, tagged `no zeros`.
- **⚙** Manim; `assets/explicit.npz`.
- **🎬** Match-cut fade 1 s. Formula 2 s on "exact formula". Isolation on "A zero's height"; γ slider 14 → 30. Envelope
  draws on "square root of x". The Re = 1 line glows on "no zero has real part one".
- **▣** `\pi(x)\approx R(x)-\sum_\rho R(x^\rho)` (`+ small terms`) · `x^\rho=x^{1/2}e^{i\gamma\ln x}` ·
  `\zeta(1+it)\neq0`.
- **🎙** P31–P33.
- **📚** verify.py (explicit formula); M6.
- **∑** explicit formula → waves summing to the staircase · `R(x)-\sum R(x^\rho)` · the opening replays with labels.
  One zero's wave → wave in an envelope · `x^{1/2}e^{i\gamma\ln x}` · γ slider and envelope.

#### s17 offline (8:47–9:26, ≈ 39 s)
- **?** Why the line matters: one off-line zero would blow up the error; RH means the smallest possible error.
- **👁** Right: a plane inset where one zero (`rogue`) is dragged from ½ to 0.8 and its twin appears at 0.2 (dashed).
  Main: the real error π(x) − li(x) (red) on a log axis to 10⁶, wiggling inside the dashed envelope ±√x ln x / 8π. The
  rogue's wave (orange, labeled `hypothetical`) grows like x^0.8 and leaves the envelope, dragging the error out. The zero
  snaps back; the envelope holds. Then `H. von Koch · 1901` with a two-way arrow. Last, the mirror argument: a slider for
  the largest real part Θ can move down only to ½.
- **⚙** Manim; real error baked; the rogue wave is synthetic (c · x^0.8 cos(γ ln x)) and labeled as such.
- **🎬** Drag 2 s on "Suppose"; growth 3 s on "x to the point eight"; escape on "far away". Snap back 1 s on "never
  happens". Envelope draws on "square root of x times its logarithm". The arrow draws both ways on "the reverse". Θ slider
  1.5 s. Hold 2 s on "as close to the curve as they possibly can".
- **▣** `\rho=0.8+i\gamma` (hypothetical) · `x^{0.8}` vs `x^{1/2}` ·
  `|\pi(x)-\mathrm{li}(x)|<\frac1{8\pi}\sqrt x\ln x` with `if RH, x ≥ 2657 (Schoenfeld 1976)` ·
  `\mathrm{RH}\iff\pi(x)=\mathrm{li}(x)+O(\sqrt x\ln x)` · `\Theta\ge\tfrac12`.
- **🎙** P34–P35.
- **📚** M7, M8; verify.py (Schoenfeld envelope to 10⁶; off-line growth).
- **∑** off-line growth → one wave ballooning · `|x^\rho|=x^{\mathrm{Re}\,\rho}` · drag the zero right. The bound →
  dashed envelope · Schoenfeld (`if RH`) · the real error stays inside. Equivalence → two-way arrow · von Koch · draws
  both ways. Smallest error → mirrored pair · `\Theta\ge\tfrac12` · the slider stops at ½.

### CH5 Why it is so hard

#### s18 littlewood (9:26–9:53, ≈ 28 s)
- **?** Evidence isn't proof: patterns can fail very far out.
- **👁** The line of zeros with a tiny bracket at its base, `10¹³ checked`, against the line rising into darkness. Then
  li(x) − π(x) on a log axis: real data to 10⁶ (always positive), then the axis compresses: a tick at 10¹⁹ (`checked: no
  flip`), dashed beyond (schematic, labeled), a marker at 1.4 × 10³¹⁶ (`a flip happens before here`).
  `J. E. Littlewood · 1914`.
- **⚙** Manim; real data from `zmath` to 10⁶; the region beyond 10⁶ is drawn schematically and labeled as such.
- **🎬** Bracket on "ten trillion"; the line extends on "infinitely many". Plot draws to 10⁶; zoom-out 5 s across 300
  orders of magnitude; the 10³¹⁶ marker lands on "three hundred digits".
- **▣** `\mathrm{li}(x)>\pi(x)` for all checked `x` · `\pi(x)-\mathrm{li}(x)` changes sign infinitely often ·
  `10^{19}` · `1.4\times10^{316}`.
- **🎙** P36.
- **📚** M9; verify.py (π < li to 10⁶).
- **∑** evidence vs proof → tiny bracket, log flight · sign changes infinitely often · zoom out over 300 orders.

#### s19 noproduct (9:53–10:06, ≈ 12 s)
- **?** The best tool, the Euler product, stops working exactly where the zeros are.
- **👁** The plane, dimmed. The half-plane Re > 1 lit and tagged `∏ converges ⇒ ζ ≠ 0`. A probe at 2 + 5i: the path of
  partial products settles (`zeta`). The probe slides into the strip to ½ + 20i: the path wanders and never settles
  (dashed); the strip is tagged `∏ diverges`.
- **⚙** Manim over the shader at `u_dim`; partial products over primes up to 10⁴ from `zmath`.
- **🎬** Path settles 2 s; the probe slides 1.5 s on "Inside the strip"; the path wanders 3 s.
- **▣** `\prod_p(1-p^{-s})^{-1}` with `\mathrm{Re}(s)>1` · `diverges`.
- **🎙** P37.
- **📚** M3.
- **∑** where the product works → lit half-plane, settling vs wandering paths · `\prod_p(1-p^{-s})^{-1}` for
  `\mathrm{Re}\,s>1` · the probe crosses into the strip.

#### s20 nearmiss (10:06–10:38, ≈ 33 s)
- **?** The zeros come close to failing; if RH is true, it's barely true.
- **👁** Z(t) for t ∈ [6995, 7015]: ordinary crossings about 0.9 apart. A magnifier opens on t ≈ 7005.035–7005.13 (≈ ×200 in t; Z rescaled ≈ ×1,000 so ±0.01 fills it):
  two crossings 0.0377 apart, with the wave climbing only to +0.004 between them. A ruler: `0.0377` vs average `0.8955`
  → `≈ 24× closer`. "What if": a ghost copy of the wave (`rogue`) lowered by 0.005 no longer reaches zero; the two
  crossings vanish, and in an inset plane two pinwheels leave the line as a mirror pair. Restore. Then a slider `Λ`
  against a wall at 0: `RH ⟺ Λ ≤ 0`, then `Λ ≥ 0 (Rodgers & Tao 2018)`, so `RH ⟺ Λ = 0`.
- **⚙** Manim; Z(t) baked at high resolution near 7005 (`assets/lehmer.npz`), checked against mpmath zeros #6709 and
  #6710 in verify.py.
- **🎬** Zoom 3 s on "near height seven thousand and five". Ruler 1 s on "twenty-four times". Peak marker on "four
  thousandths". Ghost shift 2 s on "If it had turned back"; the pinwheels split 1.5 s; restore 1 s. Λ slider 2 s; it bumps
  the wall on "no room to spare".
- **▣** `\gamma_{6709}\approx7005.0629`, `\gamma_{6710}\approx7005.1006` · `0.0377` vs `0.8955` ·
  `\max Z\approx0.004` · `D. H. Lehmer · 1956` · `\mathrm{RH}\iff\Lambda\le0` · `\Lambda\ge0` · `B. Rodgers & T. Tao ·
  2018`.
- **🎙** P38.
- **📚** M18 (Lehmer 1956), M19 (Newman 1976, Rodgers–Tao 2018); verify.py (Lehmer pair).
- **∑** near-miss → magnified peak · gap ratio, peak height · zoom, ghost shift breaks the crossings. No room to spare
  → slider against a wall · `\mathrm{RH}\iff\Lambda=0` · bumps at 0.

#### s21 progress (10:38–11:03, ≈ 25 s)
- **?** The proportion record, and why even 100% wouldn't be enough.
- **👁** A horizontal bar `zeros proven on the line`, 0 → 1. Markers: `Hardy 1914: infinitely many` at the left edge,
  `Selberg 1942: > 0`, `Levinson 1974: 1/3`, `Conrey 1989: 2/5`, `Pratt–Robles–Zaharescu–Zeindler 2020: 5/12`. The fill
  creeps and freezes at 5/12. Then "100% ≠ all": whole numbers as dots with the perfect squares in pink; as N grows
  (100 → 10,000) the fraction of squares falls (10% → 1%) while the squares keep coming. So the non-squares are 100% of
  all numbers, and they still leave out infinitely many.
- **⚙** Manim.
- **🎬** Fill steps 0.6 s per marker; 1 s hold at 5/12. N grows over 3 s with a falling counter.
- **▣** the dated fractions (exact) · `\lfloor\sqrt N\rfloor/N\to0` · `100% ≠ all`.
- **🎙** P39.
- **📚** M10, M11, M15.
- **∑** proportion → progress bar · `>0, 1/3, 2/5, 5/12` · creeping fill. 100% ≠ all → squares among integers ·
  `\sqrt N/N\to0` · N grows, the fraction falls, squares keep coming.

#### s22 cousin (11:03–11:36, ≈ 33 s)
- **?** A version that has been proved, and what it has that the whole numbers lack.
- **👁** `y^2=x^3+x+1` writes on. A clock face with 7 hours shows wrap-around for a moment. Then the 101 × 101 grid of
  pairs (x, y) mod 101: the 104 solutions appear as lilac dots (`ffield`), symmetric about the middle row. A gauge shows
  `p ± 2√p` with the count's needle near the center. Then a scatter of (A_p − p) / 2√p for all 669 primes below 5000:
  every point inside two dashed lines at ±1. Cards: `H. Hasse · 1933` (this kind of curve), `A. Weil · 1940s` (all
  curves), `P. Deligne · 1974` (the general case). Last, a split frame: `clock arithmetic: geometry` (solid) vs `whole
  numbers: ?` (empty).
- **⚙** Manim; counts from numpy (`assets/hasse.npz`).
- **🎬** Clock 2 s on "wrap around". Points populate row by row (20 ms stagger) on "count its solutions". The needle
  settles on "never strays". Scatter builds left to right in 2 s on "square-root behavior". Cards 0.6 s each. Split 1 s on
  "no known counterpart".
- **▣** `y^2\equiv x^3+x+1\pmod p` · `p=101:\ A_p=104` · `|A_p-p|\le2\sqrt p` · the three cards.
- **🎙** P40.
- **📚** M20 (Hasse), M21 (Weil), M22 (Deligne); verify.py (Hasse bound for every prime below 5000).
- **∑** clock arithmetic → clock face · `a\equiv b\pmod p` · the hand wraps. Counting solutions → lilac dots and a
  scatter · `|A_p-p|\le2\sqrt p` · points populate; every scatter point lands inside ±1.

### CH6 What solving it would mean

#### s23 meaning (11:36–12:14, ≈ 38 s)
- **?** What a resolution looks like, what it would change, and what it wouldn't.
- **👁** The line of zeros rising out of frame. Side by side: a solid green bracket covering the whole line,
  `\forall\rho:\ \mathrm{Re}\,\rho=\tfrac12` (proof), and a single rogue dot off the line,
  `\exists\rho:\ \mathrm{Re}\,\rho\ne\tfrac12` (counterexample). Then a shelf of theorem cards with tags: `prime gaps
  \le C\sqrt p\ln p` (`if RH`, Cramér 1920), the Schoenfeld bound (`if RH`), `fast primality test` (`if GRH`, Miller
  1976). On "unconditional" the `if RH` tags fade to show what a proof would do (marked `if proved`). GRH: faint copies
  of the critical line fan out, one per L-function. Encryption: `N = p × q` with a struck-through arrow from `RH` to
  `factor N`.
- **⚙** Manim.
- **🎬** Bracket 1.5 s; rogue dot 0.5 s. Cards slide onto the shelf (0.3 s stagger); tags fade 1 s. Lines fan out 1 s.
  Struck arrow on "wouldn't break encryption".
- **▣** `\forall` / `\exists` statements · the cards and tags · `L(s,\chi)=\sum\chi(n)n^{-s}` · `N=p\times q`.
- **🎙** P41–P42.
- **📚** research rule 5 (Miller needs GRH); M8; M23 (Cramér 1920); M24 (Miller 1976).
- **∑** proof vs counterexample → bracket vs rogue dot · `\forall` vs `\exists` · side by side. Conditional results →
  shelf of tagged cards · Cramér's gap bound · tags fade. GRH → many critical lines · `L(s,\chi)` · the lines fan out.

#### s24 spacing (12:14–12:33, ≈ 19 s)
- **?** A famous speculation, labeled as one.
- **👁** A histogram of normalized gaps between consecutive zeros (first ~5,000 zeros) against the random-matrix (GUE)
  prediction, drawn **dashed** (conjecture grammar). Cards `H. Montgomery · 1973`, `F. Dyson`. A faint stack of
  horizontal lines (energy levels). Tag `speculation`.
- **⚙** Manim; spacings from `zmath.zeros_upto` (bake once, `assets/spacing.npz`).
- **🎬** Bars rise 2 s; the dashed curve draws 1 s; tag 0.5 s.
- **▣** `GUE` · `conjecture` · `speculation`.
- **🎙** P43.
- **📚** M13.
- **∑** zero spacing → histogram vs dashed curve · GUE prediction · bars rise to meet a dashed curve.

### CH7 Back to November

#### s25 august (12:33–13:05, ≈ 33 s)
- **?** The August 2026 result, who checked what, and Anthropic's own caveat.
- **👁** The s21 bar returns frozen at 5/12. A new marker `Aug 2026` (`ai`) and the fill jumps to 2/3, labeled
  `≥ 2/3 simple and on the line`. Chips appear under it: `found by Claude (research version)` (ai) ·
  `checked, written up: L. Alpöge, R. Furman` (human) · `examined: B. Conrey, D. Goldston` (human) · `Lean ✓` (lean) ·
  `independent proof: Y. Lamzouri · Sep 2026` (human). Then a plain gray card: `Anthropic: not expected to lead to RH`.
- **⚙** Manim.
- **🎬** The jump takes 1.2 s `easy_ease` on "five twelfths to two thirds", the bar's biggest move; hold 1.5 s. Chips 0.4 s
  each on their names. Caveat card on "didn't expect".
- **▣** `5/12 → 2/3` · `arXiv 2608.13637` · `arXiv 2609.02882` · chips.
- **🎙** P44.
- **📚** A1–A5.
- **∑** reuses the proportion bar.

#### s26 lean (13:05–13:52, ≈ 47 s)
- **?** What a Lean check guarantees, and the gap it leaves: does the statement say what we mean?
- **👁** A proof as a chain of boxes, each pointing back to earlier ones, down to three axiom boxes (`propext`,
  `Classical.choice`, `Quot.sound`). A small teal box (the kernel) walks the chain and ticks each step. Then the Mathlib
  definition, verbatim, in CM typewriter:
  `def RiemannHypothesis : Prop := ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1), s.re = 1 / 2`
  Color-coded mapping lines tie each part to the maths: `riemannZeta s = 0` ↔ ζ(s) = 0 (zeta), `¬∃ n, s = −2(n+1)` ↔ not
  a trivial zero (trivial), `s ≠ 1` ↔ the pole, `s.re = 1/2` ↔ Re(s) = ½ (crit). `riemannZeta` gets an arrow to a box
  `defined in Mathlib`. A second chip: `+ 4 theorems: Dirichlet L-functions`. On Buzzard's line a card docks top right:
  `K. Buzzard · Imperial` over one row, `1  does the statement mean RH?` (open ring). It stays through s28.
- **⚙** Manim (`\texttt` via LaTeX with escaped symbols, or `Text` with CM typewriter).
- **🎬** Chain builds 2 s; ticks travel bottom-up 3 s on "each step follows". Code types on 2 s on "means what you think".
  Mapping lines 0.3 s stagger. The Buzzard card slides in 0.6 s on "first question". The Mathlib box pulses on
  "confirming the definitions".
- **▣** axiom names · the definition · mapping labels · `+ 4 theorems: Dirichlet L-functions` · the Buzzard card.
- **🎙** P45–P46.
- **📚** A8, A10, A16, A18 (Buzzard's four questions).
- **∑** formal proof → chain of steps down to axioms · the Lean definition · kernel ticks. Statement fidelity → code
  mapped to maths · `RiemannHypothesis` · mapping lines.

#### s27 robin (13:52–14:13, ≈ 20 s)
- **?** A check of the proof's meaning that doesn't use the zeta definition at all.
- **👁** For n from 3 to 10⁵ (log axis): points σ(n)/(n ln ln n) (`ink`) under a solid line at e^γ ≈ 1.781 (`bound`).
  The record-setters approach the line; the last point above it is n = 5040 (labeled, σ(5040) = 19,344). Every point
  after it stays below. The statement: `\sigma(n)<e^\gamma n\ln\ln n` for all `n>5040` `\iff\mathrm{RH}` (G. Robin
  1984). A chip: `proof + Robin formalization: being checked` (lean, open ring); the Buzzard card's row 1 gains
  `+ Robin cross-check ◌`.
- **⚙** Manim; σ(n) by a numpy sieve (`assets/robin.npz`; verify.py checks to 10⁶).
- **🎬** Points stream left to right over 3 s; the 5040 marker on "five thousand and forty"; hold; chip on "checked too".
- **▣** `\sigma(n)=\sum_{d\mid n}d` · `e^\gamma\approx1.781` · `n=5040` · `G. Robin · 1984`.
- **🎙** P47.
- **📚** M25 (Robin 1984); A16 (Sutherland: Robin and Lagarias criteria combined with the proof); verify.py (Robin).
- **∑** Robin's criterion → divisor-sum points under a line · `\sigma(n)<e^\gamma n\ln\ln n` · 5040 is the last point
  above.

#### s28 checks (14:13–14:48, ≈ 36 s)
- **?** What has actually been checked and by whom; what's missing; who did what.
- **👁** The s01 tile wall returns. The Buzzard card grows into his four questions, each answered from Sutherland's
  page (`A. Sutherland · MIT`): `1 statement means RH?` → `Mathlib definition · Robin cross-check ◌`;
  `2 compiles?` → `175,187 / 175,187 files ✓`; `3 proves that statement?` → `statement compare ✓ · comparator ◌`;
  `4 no kernel bug?` → `nanoda ✓ con-leche ✓ lean4lean ✓ · Lean replays ◌`. On "approximately zero", a quote card:
  `chance anything is fishy: "approximately zero"` · `A. Sutherland · Scientific American, 20 Nov` (human). The panel
  carries the timestamp `as of 21 Nov 2026, 09:30 UTC` (**update at the final check**, research.md A9). Then a dashed empty
  page outline: `no human-readable paper yet`. Two attribution chips, labeled `per L. Alpöge's note`: `steered the search`
  (human) and `far outpaced him near the finish line` (ai).
- **⚙** skia tile wall (reused) + Manim.
- **🎬** Rows tick in 0.4 s each on "several independent checkers"; open rings turn slowly (one turn per 4 s). Quote card 0.6 s on "approximately zero". Page outline
  on "no human-readable paper". Chips 0.6 s on "steered" and "outpaced".
- **▣** as listed.
- **🎙** P48–P49.
- **📚** A7, A9, A15, A17 (the Sutherland quote), A18 (the four questions).
- **∑** — (status, not maths).

#### s29 stepanov (14:48–15:09, ≈ 20 s)
- **?** Where the claimed idea comes from, tied back to the clock-arithmetic version.
- **👁** The s22 lilac grid returns briefly. A one-variable picture of "vanishing many times": a curve crossing the axis
  (order 1), touching it (order 2), flattening through it (order 3), tagged `f = 0`, `f′ = 0`, `f″ = 0`. Then whole
  numbers as dots on a line with `d/dn ?`. Last, a dashed box in **amber outline**: `stand-in (claimed)`.
- **⚙** Manim.
- **🎬** Grid 0.6 s; the curve morphs between orders over 1.5 s; the dots and question on "no obvious derivative"; the
  amber box on "finds a stand-in".
- **▣** `S. Stepanov · 1969` · `f(a)=f'(a)=\cdots=f^{(m-1)}(a)=0` · `\frac{d}{dn}\ ?` · amber `stand-in (claimed)`.
- **🎙** P50.
- **📚** M26 (Stepanov's method), A15 (the note: "a descendant of Stepanov's").
- **∑** multiplicity → graphs touching the axis · `f=f'=\cdots=0` · morph between orders 1, 2, 3.

#### s30 status (15:09–15:45, ≈ 36 s)
- **?** The official status, and the kinds of results side by side.
- **👁** A Clay card: `Unsolved`, with three unlit rule chips: `published`, `2 years`, `broadly accepted`. Then the status
  ladder (design sheet 2): `evidence` (10¹³ zeros) → `theorem` (≥ 2/3; people + Lean) → `proposed proof, machine
  checks partly complete` (RH, amber outline) → `understood and accepted` (empty, dotted). Each result slides onto its
  rung.
- **⚙** Manim.
- **🎬** Clay card 0.6 s; the chips stay unlit; hold 1.5 s on "still open". Rungs build bottom-up 0.4 s each; results
  slide 0.8 s on their words; hold 2 s on the empty top rung.
- **▣** as listed.
- **🎙** P51–P52.
- **📚** A12, M12, A4, A9.
- **∑** — (reuses the proportion bar as a rung).

### Outro

#### s31 outro (15:45–16:20, ≈ 35 s)
- **?** Payoff: the primes are waves from zeros; the 1859 callback.
- **👁** The s02 frame returns exactly: staircase, curve on it, the line of zeros. The camera pulls back until the line
  becomes the critical line in a dim ζ coloring behind everything (`u_dim` 0.35). On "eighteen fifty-nine" the s14 quote
  card returns, small, in ink. On "only beginning to read" the tile wall shows faintly, and the line of zeros extends up
  past the frame: the s01 first frame again. Fade to black.
- **⚙** Manim + `zeta_domain.frag` backdrop at parallax 0.6.
- **🎬** Pull-back 10 s `easy_ease`; card 0.6 s; final hold 3 s (`tail`).
- **▣** minimal: `1859`, `2026`.
- **🎙** P53–P54.
- **📚** M1, A7.
- **∑** — (the opening, now fully explained).

---

## Production notes
- **Before voicing:** re-fetch Sutherland's page (math.mit.edu/~drew/grh), the arXiv listings and Clay; update
  research.md A7–A19 and any narration in P44–P52 that changed; skim the Lean Zulip thread and the news for anything newer. Those paragraphs are in the last voice chunks, so an edit
  re-bills only them.
- **Pronunciation check** after voicing: Alpöge, de la Vallée Poussin, Eratosthenes, Lamzouri, Deligne, Lehmer, Stepanov.
- **Independent review:** this script was drafted with Claude, the model named in chapter 7. Have a mathematician outside
  Anthropic read P44–P52 and s25–s30 before release.
- **s24, s27 and s29** are kept (2026-11-21). If the runtime ever has to come down, they are still the clean cuts:
  nothing else depends on them (s22 stands without s29's callback).
- **Bakes** (once, in `assets/`): `explicit.npz` (s02, s16), `pnt.npz` (s06, s17, s18), `zline.npz` (s15),
  `lehmer.npz` (s20), `hasse.npz` (s22, s29), `spacing.npz` (s24), `robin.npz` (s27), `euler_paths.npz` (s19).
- **Implementation order** (chapter by chapter): shader validation gate (design.md §10) → s02 + s16 (the spine) → CH2–3
  (the shader scenes) → CH1 → CH4–5 → CH6–7 → s01, s31.
- **Risks:** shader precision above t ≈ 40 isn't needed (the flight stops at 38; s20 uses the Z graph, not the shader).
  Public-domain images need clean scans; if a Nachlass scan isn't clearly public domain, s14 uses a plain card.

### Scene cuts on the real audio (`aion beats`, 2026-11-21)
| beat | time | end | words |
|---|---|---|---|
| cut_staircase ✂ | 49.68 | 49.68 | with the prime numbers. ✂ These are the primes |
| cut_map ✂ | 97.32 | 97.32 | all infinitely many. ✂ That takes some unpacking |
| cut_atoms ✂ | 111.92 | 111.92 | and what hasn't. ✂ Every whole number above one |
| cut_sieve ✂ | 141.63 | 141.63 | factors are all new. ✂ Finding them is mechanical |
| cut_pnt ✂ | 168.65 | 168.65 | no prime at all. ✂ Over long stretches |
| cut_series ✂ | 219.85 | 219.85 | the Riemann hypothesis is about. ✂ Here's the function |
| cut_euler ✂ | 248.32 | 248.32 | pi squared over six. ✂ Euler also found the link |
| cut_complex ✂ | 275.57 | 275.57 | information about every prime. ✂ In eighteen fifty-nine |
| cut_coloring ✂ | 312.20 | 312.20 | single point: zeta of s. ✂ The outputs are complex too |
| cut_continuation ✂ | 343.02 | 343.02 | the spiral never closes. ✂ A simpler sum |
| cut_trivial ✂ | 382.90 | 382.90 | called the functional equation. ✂ So where is zeta zero |
| cut_strip ✂ | 398.93 | 398.93 | they're well understood. ✂ Every other zero lies |
| cut_riemann ✂ | 431.55 | 431.55 | has ever been found. ✂ Riemann's private notes |
| cut_checking ✂ | 457.45 | 457.45 | a Millennium Prize Problem. ✂ How can anyone know |
| cut_explicit ✂ | 491.33 | 491.33 | every one is on the line. ✂ Now the waves from the opening |
| cut_offline ✂ | 527.13 | 527.13 | asks for much more. ✂ Suppose one zero sat off |
| cut_littlewood ✂ | 565.65 | 565.65 | as they possibly can. ✂ If ten trillion zeros |
| cut_noproduct ✂ | 593.48 | 593.48 | over three hundred digits. ✂ The zeros also sit |
| cut_nearmiss ✂ | 605.77 | 605.77 | no longer converges. ✂ And the zeros come close |
| cut_progress ✂ | 638.32 | 638.32 | no room to spare. ✂ Progress has also been slow |
| cut_cousin ✂ | 663.22 | 663.22 | leave out infinitely many. ✂ Finally, a version |
| cut_meaning ✂ | 696.18 | 696.18 | for the whole numbers. ✂ Solving it means |
| cut_spacing ✂ | 733.87 | 733.87 | factor a large number. ✂ Some ideas go further |
| cut_august ✂ | 752.63 | 752.63 | proof wouldn't settle it. ✂ Back to this year |
| cut_lean ✂ | 785.18 | 785.18 | to the full hypothesis. ✂ Then came November |
| cut_robin ✂ | 832.30 | 832.30 | confirming the definitions. ✂ One test avoids |
| cut_checks ✂ | 852.53 | 852.53 | is being checked too. ✂ So far, Andrew Sutherland |
| cut_stepanov ✂ | 888.40 | 888.40 | near the finish line. ✂ He calls the argument |
| cut_status ✂ | 908.80 | 908.80 | finds a stand-in. ✂ Officially, the problem |
| cut_outro ✂ | 944.50 | 944.50 | has barely begun. ✂ Let's go back to the staircase |

30 cuts, 31 scenes, audio 979.56 s.
