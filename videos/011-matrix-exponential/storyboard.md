# What the Matrix Exponential Actually Is: storyboard

**Status:** revision 2, audio generated and beats resolved (2026-11-17). Waiting for storyboard approval before scene code.
This revision adds a warm prologue (context, history, the problem,
applications), replaces the 3D die with the particle Earth, makes the pill the intro's problem and ch6's payoff,
and rewrites the narration in a more personal voice.

Audio: `assets/audio.wav` (877.84 s = **14:37**, 2,452 words, 6 chunks, 13,075 characters), generated
2026-11-17 with `aion voice` using the 004–010 voice at speed 0.92. Captions: `assets/subtitles.srt` (254 cues, two
lines of ≤ 42 characters, broken at sentences and clauses). Scene ranges below are the real cuts from `beats.py`.
The full beat table is in `beats.md` (`uv run aion beats 011-matrix-exponential --md`). Nothing is built until
this storyboard is approved.

Files:
- `voiceover.md`: the source of truth for every spoken word.
- `design.md`: the design sheet.
- `theme.py`: colors.
- `verify.py`: the math. Every number on screen is imported from its `CAST` or computed by it, and running it
  passes all checks (`uv run python videos/011-matrix-exponential/verify.py`).

Alt titles: *Matrix Exponential Explained Visually* · *How Do You Raise e to a Matrix?* ·
*Euler's Number Meets Linear Algebra*.

## The spine
**A matrix is a velocity. e to the matrix is the trip.** Every point v moves at velocity A v, and e^{tA} is where the
flow carries everything after time t. The prologue earns the question: things that change in proportion to
themselves give e^{kt}, and things that change *together* give ẋ = Ax, so the answer ought to be e^{tA}. The
chapters answer it. Ch6 brings the pill back and ends on the Earth turning under the viewer's feet. The outro closes
the loop back to Bernoulli.

Series continuity: 007 (e^{iπ} = −1) is the hook's twin. 008 (divergence) is the trace. 009 (matrices as moves,
eigenvectors) is assumed. 010 (e^{hD} = shift) is the outro's reach into infinite dimensions. Each callback is
≤ 10 s and carries a new visual. Nothing is re-taught.

**Not copying.** 3Blue1Brown's matrix-exponential lesson uses a Romeo-and-Juliet love system and a
Schrödinger-equation opening. We use neither. Our cast is coffee, Bernoulli's bank account and a pill; the
element-wise collapse and a half turn; a diagonal, a saddle, a spiral and a shear; two shears and a commutator loop;
and the spinning Earth.

**History, as narrated** (checked 2026-11-17):
- Jacob Bernoulli, 1683: compound interest leads to e ([AMSI](https://amsi.org.au/ESA_Senior_Years/SeniorTopic3/3h/3h_4history.html)).
- Euler named the number e (1727–31).
- Laguerre, 1867: the exponential of a matrix as a power series
  ([Higham](https://nhigham.com/2020/05/28/what-is-the-matrix-exponential/)).
- Peano, 1888: series for systems of linear differential equations
  ([Peano–Baker series](https://arxiv.org/html/1011.1775v3)).
- Lie, 1870s–1890s: continuous transformation groups built from infinitesimal generators
  ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Lie/)).

The narration makes no stronger claims than these.

## Promises tracked (playbook rule 18)
| promise | made | paid |
|---|---|---|
| what e to a matrix means | s02 (the question) | s09 (definition), s26 (restated) |
| the pill: how much is in your blood | s02 | s21–s22 |
| why e^{πJ} = −I, "the same fact" as e^{iπ} = −1 | s05 | s10 |
| "a familiar rule of exponents will break" (open loop) | s05 | s18–s20 |
| "finish with the whole planet turning" | s05 | s23–s25 |
| the three faces: flow, steps, series | s07 | s08–s13 |
| why element-wise is wrong | s04 | s13, s14 |
| the spiral splits into shrink × turn | s16 | s20 |
| applications: flight software, robots, circuits, drug dosing, quantum computers | s03 | drug dosing s21–s22, rotation s25, quantum s27, circuits s02 (by analogy). Flight software and robots stay a mention: the Earth stands in for every rigid rotation. |

## Retention map
- 0:00–0:15 an everyday image, not a formula: the coffee. The question arrives at about 1:38 ("e raised to the power
  of a matrix… means nothing at all"). This intentionally trades playbook rule 1 for warmth, but the coffee curve and
  the four-way merge keep the screen moving every 2–3 s.
- About 1:48, history with a moving timeline (mode switch). About 2:28, the wrong guess crushes
  the plane (rule 4). About 2:38, the half turn as a visual answer before any explanation (rule 3). About
  3:01, the open loop and the map in one sentence (rules 7 and 2).
- Pause-and-predict: s10 ("where will the grid be after π?"), s17 ("what happens to the shear's area?").
- Midpoint payoff at about 7:53 (the series, and why element-wise fails). Re-hook at about 10:10 "the rule that
  breaks" (rule 11).
- Mode switches every 60–90 s: story → history → visual → build → derivation → gallery → surprise → application →
  3D → reflection.
- Each chapter closes on a held visual, never a spoken recap (rule 17).

## Chapter structure (14:37)

| # | chapter | range | scenes | mode | payoff |
|---|---|---|---|---|---|
| 0 | Intro: coffee to e to a matrix | 0:00–3:13 | s00–s05 | story → history → wrong guess → visual answer | the half turn |
| 1 | Growth that feeds on itself | 3:13–4:26 | s06–s07 | 1D visual | e is a stretch factor of a flow |
| 2 | A matrix as a velocity | 4:26–6:03 | s08–s10 | build, predict | e^{tA} = the trip; e^{πJ} = −I |
| 3 | The series out of tiny steps | 6:03–8:07 | s11–s13 | derivation | e^{A} = Σ A^k/k! |
| 4 | Directions, spirals, shears | 8:07–10:09 | s14–s17 | gallery, predict | det e^{A} = e^{tr A} |
| 5 | The rule that breaks | 10:09–11:46 | s18–s20 | surprise (re-hook) | the commutator, seen as a loop |
| 6 | Back to the pill, and the planet | 11:46–13:33 | s21–s25 | application, 3D | the pill curve; Rodrigues |
| 7 | Outro | 13:33–14:37 | s26–s28 | reflection | "how things move / where they go" |

## Scene breakdown

The ¶ column gives paragraph numbers within that section of `voiceover.md`.

| scene | chapter | ¶ | range (length) | what changes |
|---|---|---|---|---|
| `s00_prologue` | Intro | 1–2 | 0:00–0:34 (35 s) | coffee, coins, bacteria, rock → one e^{kt} |
| `s01_bernoulli` | Intro | 3 | 0:34–0:58 (24 s) | 1683 compounding → the ceiling e |
| `s02_tangled` | Intro | 4–6 | 0:58–1:48 (49 s) | pill, molecules, ẋ = Ax, e^{tA}? |
| `s03_history` | Intro | 7 | 1:48–2:14 (26 s) | timeline Laguerre/Peano/Lie → today's uses |
| `s04_wrong_guess` | Intro | 8 | 2:14–2:33 (19 s) | element-wise crushes the plane |
| `s05_half_turn` | Intro | 9–11 | 2:33–3:13 (41 s) | the half turn; the tease; line → globe |
| `s06_line_flow` | Growth that feeds on itself | 1–3 | 3:13–3:54 (41 s) | number-line flow, e as stretch, e^{rt} |
| `s07_steps` | Growth that feeds on itself | 4–5 | 3:54–4:26 (31 s) | n steps → e, the series, three faces |
| `s08_field` | A matrix as a velocity | 1–2 | 4:26–4:50 (24 s) | line → plane, Av arrows |
| `s09_grid_flow` | A matrix as a velocity | 3–4 | 4:50–5:27 (37 s) | the grid flows and stays a grid; definition |
| `s10_columns` | A matrix as a velocity | 5–7 | 5:27–6:03 (36 s) | cos/sin columns; predict; −I |
| `s11_euler` | The series out of tiny steps | 1–3 | 6:03–6:41 (38 s) | (I + tA/n)^n polygons → circle |
| `s12_binomial` | The series out of tiny steps | 4–5 | 6:41–7:23 (42 s) | choosing steps → 1/k!; the series |
| `s13_terms` | The series out of tiny steps | 6–8 | 7:23–8:07 (44 s) | tip-to-tail spiral, bars, element-wise fails |
| `s14_diagonal` | Directions, spirals, shears | 1–2 | 8:07–8:35 (28 s) | two number lines; zeros stay zero |
| `s15_saddle` | Directions, spirals, shears | 3 | 8:35–9:01 (26 s) | eigenlines, curved paths |
| `s16_spiral_shear` | Directions, spirals, shears | 4–5 | 9:01–9:36 (34 s) | complex eigenvalues; series stops |
| `s17_trace` | Directions, spirals, shears | 6–7 | 9:36–10:09 (34 s) | area patch; predict; det = e^{tr} |
| `s18_three_shapes` | The rule that breaks | 1–2 | 10:09–10:46 (37 s) | three parallelograms |
| `s19_series_gap` | The rule that breaks | 3 | 10:46–11:08 (22 s) | second-order terms; commutator |
| `s20_loop` | The rule that breaks | 4–5 | 11:08–11:46 (38 s) | loop that doesn't close; parking; spiral splits |
| `s21_pill_matrix` | Back to the pill, and the planet | 1 | 11:46–12:09 (23 s) | compartments → plane → one line |
| `s22_pill_curve` | Back to the pill, and the planet | 2 | 12:09–12:24 (15 s) | molecules vs e^{tA}; the blood curve |
| `s23_earth` | Back to the pill, and the planet | 3 | 12:24–12:45 (22 s) | particle Earth, n × r, 1670 km/h |
| `s24_cross_matrix` | Back to the pill, and the planet | 4 | 12:45–12:59 (14 s) | the cross product as K |
| `s25_rodrigues` | Back to the pill, and the planet | 5 | 12:59–13:33 (34 s) | series folds; one turn → I |
| `s26_meaning` | Outro | 1–2 | 13:33–14:01 (27 s) | velocity / trip; the facts ring |
| `s27_beyond` | Outro | 3 | 14:01–14:18 (18 s) | shift and quantum panels |
| `s28_bookend` | Outro | 4 | 14:18–14:37 (19 s) | Bernoulli → pill → planet → A / e^A |

---

## INTRO: from a cup of coffee to e to a matrix

The intro is a short story before it's a lesson. It goes from everyday things changing, to Bernoulli, to things that
change together, to the audacious e^{tA}, to its history and modern uses, to the wrong guess, to the half turn. The
line-art prologue sets the warm tone. The matrix and plane arrive only after the viewer has a reason to want them.

### s00_prologue · 0:00.0–0:34.9 (35 s) · ¶1–2
- **Purpose.** Start from lived experience: "how fast it changes depends on how much there is". Show that one rule
  lives in four worlds.
- **Visual.**
  - Black. A white line-art coffee cup draws itself at centre-left, with three steam strokes rising and thinning.
    To its right, a small temperature plot draws (thin white axes, no numbers): a teal curve falls fast and then
    slowly toward a dashed "room" line, as if losing interest.
  - On "the hotter it is": a vertical orange velocity tick sits on the curve and shrinks as the gap shrinks. It's
    the first orange arrow of the video, quietly introducing "rate".
  - On "That rule turns up everywhere": the frame splits into four thin `C.frame` panels:
    - coffee (the existing cup and curve);
    - a coin stack growing, each new coin a little faster (rising teal curve);
    - a petri dish where yellow dots split in two at seeded times (doubling curve);
    - a rock with yellow dots blinking out at seeded exponential times (decay curve).
  - On "one equation": each panel's curve lifts out and the four slide to the centre and overlay. After normalizing
    their axes (rising curves stay, falling curves mirror), they merge into the same shape. `\dot x = kx` writes
    above it, then `x(t) = e^{kt}x_0` below it (`e^{kt}` teal, `x_0` yellow).
- **Tech.** Manim line art and plots. `PointsLayer` for the bacteria and atoms, with seeded event times (numpy) so
  the dots are a pure function of t.
- **Animation.**
  - Each drawing is a 1.0 s `Create`. Panels slide out of the cup's frame, staggered 0.2 s.
  - The curve merge is a 1.5 s easy_ease. Coins drop with a 0.25 s ease.
  - At most three movers: curve, steam, one panel.
- **On screen.** Cup, steam, curves, panels, `\dot x = kx`, `x(t)=e^{kt}x_0`.
- **Narration.** "Leave a cup of coffee on your desk…" → "…one answer: e to the k t."

### s01_bernoulli · 0:34.9–0:58.6 (24 s) · ¶3
- **Purpose.** The history of e, told as a person asking a question.
- **Visual.**
  - The merged curve shrinks to the top-left corner. Centre: `\textsc{Jacob Bernoulli} \cdot 1683` writes in
    CM small caps (`data`, 30 px).
  - A single line-art coin. Below it, a horizontal balance bar starts at 1 and grows to 2 on "a hundred percent a
    year" (n = 1).
  - On "twice a year": the bar splits into 2 steps → 2.25. Monthly gives 12 steps → 2.613. On "every instant": the
    steps blur into a smooth teal fill → 2.718…
  - The bar meets a dashed ceiling line. The value readout ticks (`data`), and a table on the right fills
    (n, (1 + 1/n)^n) for n = 1, 2, 12, 365, ∞.
  - On "Euler later gave that number its letter": `\textsc{Euler}` fades in small under the ceiling, and the letter
    `e` (teal, 72 px) writes onto the ceiling line.
- **Tech.** Manim. Values come from `verify` (`(1 + 1/n)**n`).
- **Animation.** Steps use `steps(n)` easing. The table fills 0.3 s per row. The ceiling stays fixed throughout.
- **Optional.** Public-domain portraits of Bernoulli and Euler as small framed engravings. Downloading them needs your
  OK; the default is names only.
- **On screen.** Name and date, coin, balance bar, table, ceiling, `e`.
- **Narration.** "People found that answer by following money…" → "…its letter: e."

### s02_tangled · 0:58.6–1:48.1 (49 s) · ¶4–6
- **Purpose.** The real problem: things change *together*. This scene earns the matrix and the question.
- **Visual.**
  - A pill (line art) drops into a minimal two-compartment drawing: a stomach (rounded pouch) above a bloodstream
    (a loop). About 400 yellow molecule dots start in the stomach.
  - On "seeps into your blood": dots hop one by one into the loop (seeded hop times). On "clears it out": dots in
    the loop fade at their own seeded times. Two orange flow arrows label the rates, `k_a` (stomach → blood) and
    `k_e` (blood → out).
  - Small readouts count the stomach and blood dots. A teal blood-level curve begins to draw at the right: it rises,
    then bends.
  - On "Two amounts, tangled together": the two readouts become a column vector `\begin{bmatrix}s\\b\end{bmatrix}`
    (yellow).
  - On "Heat moving between rooms…": three tiny icons flick in along the bottom, about 1 s each: two rooms with a
    wall, an RLC loop, a two-storey frame swaying. Each shows its own tiny state column.
  - On "one shape of equation": the pill system's equation writes as
    `\frac{d}{dt}\begin{bmatrix}s\\b\end{bmatrix} = \begin{bmatrix}-k_a&0\\k_a&-k_e\end{bmatrix}
    \begin{bmatrix}s\\b\end{bmatrix}` (matrix orange). It then collapses to `\dot{\mathbf x} = A\mathbf x`.
  - On "Next to the one-number version": `\dot x = kx \Rightarrow x = e^{kt}x_0` slides in above it, aligned. The
    analogy fills in below, `\dot{\mathbf x} = A\mathbf x \Rightarrow \mathbf x = e^{tA}\mathbf x_0`, and the
    `e^{tA}` pulses.
  - On "a grid of numbers times": the `A` in the exponent unfolds into its 2×2 grid of entries, sitting absurdly up
    in the exponent. A white `?` appears beside it. Hold.
- **Tech.** Manim line art and equations. `PointsLayer` molecules with seeded Exp(k_a), Exp(k_e) times from
  `CAST["pill"]` (k_a = 1/h, k_e = 1/4 h). Screen time runs at 1 h per 3 s.
- **Animation.** Molecules move on short eased hops (0.4 s). Equations write in term groups.
- **On screen.** Pill, compartments, molecules, `k_a`, `k_e`, blood curve, icons, the ODE pair, unfolded `e^{A}`, `?`.
- **Narration.** "But real things rarely change alone…" → "…a grid of numbers times."

### s03_history · 1:48.1–2:14.4 (26 s) · ¶7
- **Purpose.** Show that this is real, old and useful: history and applications, felt as a journey through time.
- **Visual.**
  - A thin white timeline runs left to right. The camera trucks along it, with parallax against a faint background
    grid. Ticks land as named, each with a date (CM numerals) and the person's key object (no captions):
    - 1683, `(1+\tfrac1n)^n` (small, ghosted, already seen);
    - 1867, `\textsc{Laguerre}`, `e^{A} = I + A + \tfrac{A^2}{2!} + \cdots`;
    - 1888, `\textsc{Peano}`, `\dot{\mathbf x} = A\mathbf x`;
    - 1870s–1890s, `\textsc{Lie}`, a small curved-arrow icon (an infinitesimal arrow becoming a finite arc).
  - On "Today": the timeline ends in a row of five line-art icons that draw one per word: a satellite, a robot arm,
    a circuit, the pill's blood curve (teal) and a quantum-circuit wire with a box. Each icon's matrix symbol fades
    beneath it.
- **Tech.** Manim, plus a camera truck (`s.camera.pan` with parallax layers).
- **Animation.** A 9 s truck, easy_ease at both ends. Ticks fade in 0.4 s on their beats. Icons are a 0.6 s
  `Create`, staggered.
- **On screen.** Timeline, dates, names, the series, `\dot{\mathbf x}=A\mathbf x`, icons.
- **Narration.** "Mathematicians wrote it down anyway…" → "…and quantum computers."

### s04_wrong_guess · 2:14.4–2:33.1 (19 s) · ¶8
- **Purpose.** Let the viewer's own first guess fail visibly (rule 4).
- **Visual.**
  - The icons clear. The hero `e^{\begin{bmatrix}0&-\pi\\\pi&0\end{bmatrix}}` sits centred (96 px, orange entries).
  - On "each entry on its own": each entry gets its own `e^{\,\cdot}`, giving
    `\begin{bmatrix}e^0&e^{-\pi}\\e^{\pi}&e^0\end{bmatrix}`. The entries tick to `[[1, 0.04],[23.14, 1]]` in gray
    (`wrong`). The equation slides to the top-left third.
  - The Classic grid draws in from the centre with î and ĵ. The grid transforms by the gray matrix: it shears hard
    and **folds onto one steep line** (det 0). Ghost copies of the grid lines pile onto the line, and a small
    `\det = 0` appears in gray. Hold 1 s.
- **Tech.** Manim (`Eqn`, `Mat`, `TransformMatchingTex`, `ApplyMatrix` on a `grid_lines` group). Values come from
  `verify.ew(CAST["hook"])`.
- **Animation.** The entries write with a 0.1 s stagger. The grid collapse is a 2.0 s easy_ease, landing on "single
  line".
- **On screen.** The hero exponent, the element-wise matrix, grid, î ĵ, `\det = 0`.
- **Narration.** "So what does it mean?…" → "…it isn't this."

### s05_half_turn · 2:33.1–3:13.7 (41 s) · ¶9–11 (+ 2.5 s pause)
- **Purpose.** Show the true answer before explaining it (rule 3). Plant "matrix = motion". The open loop and the
  map.
- **Visual.**
  - The crushed grid rewinds (0.8 s) and the gray matrix fades. A faint field of orange arrows (A v for A = πJ)
    grows out from the centre. About 4,000 seeded yellow particles fill a disc, with teal trails.
  - On "swings around": the particles **and the grid** flow counterclockwise over 3.2 s of screen time and land
    exactly upside down. î points left and ĵ points down.
  - `e^{A} = -I` writes. On "different outfit": `e^{i\pi} = -1` appears in muted gray beside it, with the `=` signs
    aligned.
  - On "a velocity for every point": the field brightens, and the particles keep circling slowly.
  - On "is going to break": `e^{A+B} \ne e^{A}e^{B}` flashes small in the corner (pink `≠`) and fades. It's a
    tease, not explained.
  - On the map line: everything clears to a short white number line at the left. A thin line draws from it to a
    small particle globe at the right, which is already slowly turning. Hold through the pause, then fade.
- **Tech.** Manim (grid, arrows, equations) + `PointsLayer` with `X0 @ expm(τ·A).T`, τ a `Clock` keyed to the beat.
  Trails are 8 ghost layers. The globe thumbnail is the s23 renderer at small scale.
- **Animation.** The grid's rotation uses the same Clock as the particles, so they never drift apart. Gentle push,
  1.0 → 1.06, across the swing.
- **On screen.** `e^{A} = -I`, `e^{i\pi} = -1`, field, particles, grid, the `≠` tease, number line → globe.
- **Narration.** "The real answer is far nicer…" → "…the whole planet turning under your feet."

---

## CHAPTER 1: Growth that feeds on itself

### s06_line_flow · 3:13.7–3:54.9 (41 s) · ¶1–3
- **Purpose.** Re-see e^{x} as the result of a flow. This is the 1D version of the whole video.
- **Visual.**
  - Symbol card `e^{rt}`. A horizontal number line from −4 to 6, with white ticks and CM numerals. Orange velocity
    arrows sit on the line, length ∝ position (log-compressed); zero has none. Yellow dots sit at −1, 0.5, 1 and 2.
  - On "Press play": a teal `t` counter runs 0.00 → 1.00 and the dots slide: 1 → e (a teal `e` tick appears),
    2 → 2e, −1 → −e. Ghost starting dots stay behind, joined to the moved dots by thin teal arcs.
  - On "stretch": the line's tick marks stretch by e around 0.
  - On "Speed the flow up by r": an orange `r` slider appears. At r = 2 the arrows double. At r = −1 they flip
    inward and the dots sink to 0, while the coffee curve ghosts in the corner for 2 s.
  - Readout: `x(t) = e^{rt}x_0`.
- **Tech.** Manim. Dots use `m.drive` with `x0·exp(r(t)·τ(t))`. Arrows use `m.redraw` from r(t).
- **Animation.** Flow time is linear. r changes are `key(...)` easy_ease over 1.2 s.
- **On screen.** Number line, arrows, dots, `t`, `e`, `r`, `x(t)=e^{rt}x_0`, coffee ghost.
- **Narration.** "Let's go back to the simplest case…" → "…like the coffee's extra heat."

### s07_steps · 3:54.9–4:26.3 (31 s) · ¶4–5
- **Purpose.** Plant the other two faces, steps and series, which ch3 generalizes.
- **Visual.**
  - Back to r = 1, with one dot at 1. The second above the line splits into n ticks. The dot hops n times, each
    hop `×(1 + 1/n)`. Its landing values (2, 2.25, … 2.718) echo Bernoulli's table, which ghosts in at the right for
    1 s. The hops get finer until they become a slide.
  - `\lim_{n\to\infty}(1+\tfrac{x}{n})^n` transforms into `1 + x + \tfrac{x^2}{2!} + \tfrac{x^3}{3!} + \cdots`.
  - On "three faces": three framed icons line up (flowing line, hop staircase, series). They slide to the top-right
    as the first progress stack.
- **Tech.** Manim.
- **On screen.** Hops, the limit, the series, three icons.
- **Narration.** "You can also build that flow…" → "…All three make the jump to matrices."

---

## CHAPTER 2: A matrix as a velocity

### s08_field · 4:26.3–4:50.6 (24 s) · ¶1–2
- **Purpose.** The central picture: A as a velocity field.
- **Visual.**
  - Symbol card `A\mathbf{v}`. Continuity: the number line becomes the x-axis. A vertical axis grows out of zero,
    and the Classic grid fills the plane.
  - A yellow `v` appears at (2, 1), and an orange `Av` grows from its tip. `\dot{\mathbf v} = A\mathbf v` writes.
  - `A = [[0,−1],[1,0]]` appears. î lands on ĵ and ĵ lands on −î, each shown with a quarter-turn arc.
  - On "As a velocity": arrows fill the lattice from the centre outward (staggered by distance), and six yellow dots
    begin to circle silently.
- **Tech.** Manim + `PointsLayer` (exact flow).
- **On screen.** Grid, `v`, `Av`, `\dot{\mathbf v}=A\mathbf v`, A, field, dots.
- **Narration.** "Now add a dimension…" → "…the line joining it to the center."

### s09_grid_flow · 4:50.6–5:27.7 (37 s) · ¶3–4
- **Purpose.** See why the flow is a matrix, then give the definition.
- **Visual.**
  - A brighter copy of the grid (white, 60%) drops in over the static grid and rides the flow. Highlights land on
    "straight" (one line), "parallel" (two lines) and "evenly spaced" (the tick spacing).
  - On "their sum": yellow points p, q and p + q with a thin parallelogram. All three flow, and the parallelogram
    stays a parallelogram.
  - On "e to the t A": `e^{tA}` writes in teal, with teal arrows from each starting ghost to the current point.
  - On "A is the velocity…": `A` sits over an orange arrow icon and `e^{tA}` over a teal path icon.
- **Tech.** Manim (the moving grid via `m.drive` with `expm(τA)`) + about 4,000 particles at 40% underneath.
- **On screen.** Moving grid, p, q, p + q, `e^{tA}`, the velocity/trip icons.
- **Narration.** "Now drop in a whole grid…" → "…e to the t A is the trip."

### s10_columns · 5:27.7–6:03.5 (36 s) · ¶5–7 (+ 2.5 s pause)
- **Purpose.** Read the numbers off the picture. The hook's payoff through a prediction.
- **Visual.**
  - î and ĵ ride the flow, tracing green and red arcs. On the right,
    `e^{tA} = [[\cos t, -\sin t],[\sin t, \cos t]]`, with green and red columns and live values ticking under a `t`
    readout.
  - On the question: the flow freezes and a dashed ghost circle marks the half-way point. Hold for the pause, with
    nothing moving except a 2% idle breath on the particles.
  - The flow resumes to t = π: î lands at (−1, 0) and ĵ at (0, −1). The matrix ticks to `[[−1,0],[0,−1]]`, then
    `-I`, then `e^{\pi J} = -I` with `e^{i\pi}=-1` (muted) beside it.
  - Dolly 1.0 → 1.12. Hold 1.5 s, then fade (chapter close).
- **Tech.** Manim + PointsLayer. Freezes use `Clock(rate=keys(...))`. This scene names the matrix J.
- **On screen.** î ĵ arcs, the cos/sin matrix, `t`, `-I`, `e^{\pi J}=-I`, `e^{i\pi}=-1`.
- **Narration.** "Its numbers are easy to read…" → "…nothing more mysterious than a half turn."

---

## CHAPTER 3: Building the series out of tiny steps

### s11_euler · 6:03.5–6:41.7 (38 s) · ¶1–3
- **Purpose.** Compounding for matrices: the polygon converges to the flow.
- **Visual.**
  - Symbol card `\sum A^k/k!`. The thin teal exact half-circle runs from (1, 0) to (−1, 0).
  - `\mathbf v \to (I + \tfrac{t}{n}A)\mathbf v` writes.
  - n = 4: four yellow tangent segments end at radius 2.61, spiralling out. They stay as a gray ghost. Then n = 8
    (1.77), n = 32 (1.17) and n = 1000 (on the circle). An inset plots end radius against n (log axis).
  - On "a straight step always lands a little outside": the camera pushes 2.2× onto one step and pulls back.
  - `(I + \tfrac{t}{n}A)^n \to e^{tA}`.
- **Tech.** Manim polylines from `verify.euler`.
- **On screen.** Circle, polygons, step rule, inset, limit.
- **Narration.** "Pictures are lovely…" → "…the error disappears."

### s12_binomial · 6:41.7–7:23.4 (42 s) · ¶4–5
- **Purpose.** Where 1/k! comes from: repeated transformations, counted.
- **Visual.**
  - A row of 12 step slots, each `I` by default. Selected slots become `\tfrac{t}{n}A` (orange).
  - One orange slot sweeps across all 12, giving `tA`. Pairs flicker, counted as `\binom{n}{2}\approx\tfrac{n^2}{2}`,
    giving `\tfrac{t^2A^2}{2}`. Three slots: six tiny permutations fan out and merge into one, and `3! = 6` appears.
  - The hero series writes (84 px): `e^{A} = I + A + \frac{A^2}{2!} + \frac{A^3}{3!} + \cdots`. It sits above its
    muted scalar twin, aligned term by term, with an `I` ↔ `1` pulse.
  - The camera pans from the slots up to the equation column.
- **Tech.** Manim.
- **On screen.** Slots, binomials, the series and its twin.
- **Narration.** "Now expand that power…" → "…the identity in place of one."

### s13_terms · 7:23.4–8:07.6 (44 s) · ¶6–8
- **Purpose.** Matrix powers as repeated transformations, convergence, and why element-wise fails.
- **Visual.**
  - A = πJ and v = (1, 0). The terms go tip to tail on a steady cadence: `v`, `Av` (π, up), `A²v/2!` (4.93, left),
    `A³v/3!` (5.17, down), and so on. A teal partial-sum dot jumps to each tip.
  - The camera pulls back to 0.8× for the big early terms, then dollies in to 1.4× as the spiral closes onto a teal
    ghost at (−1, 0).
  - An inset bar chart shows π^k/k! for k = 0…11, rising to k = 3 and then collapsing. The top-left entry's partial
    sums tick: 1, 1, −3.93, … −1.00.
  - On "never stood a chance": a split view. Left, `A^2` as a row·column product, with a highlight showing one entry
    built from a whole row and column. Right, in gray, each entry squared alone. A gray `≠` sits between them. Then
    the s04 crush replays as a 1 s thumbnail and fades (chapter close).
- **Tech.** Manim (bars from `verify`). Camera via `s.camera.frame`.
- **On screen.** Arrows, partial-sum dot, target ghost, bars, partial-sum entry, A² row·column.
- **Narration.** "Those powers are matrix powers…" → "…every entry with every other one."

---

## CHAPTER 4: Directions, spirals, and shears

One persistent arrow field morphs between the matrices (`key(T.x, A_prev, A_next)`). Particles reset at each case
with a 0.4 s crossfade, since their positions are exact only for a constant A.

### s14_diagonal · 8:07.6–8:35.7 (28 s) · ¶1–2
- **Visual.**
  - Symbol card `\lambda`. The field morphs to `diag(1, −1/2)`. The axes highlight as two ch1 number lines, and the
    particles stretch out sideways and flatten vertically.
  - `e^{tD} = [[e^{t}, 0],[0, e^{-t/2}]]` (teal). On "The zeros stay zero": the zeros pulse white, and the gray
    element-wise ghost below shows ones in their place.
- **Tech.** Manim + PointsLayer.
- **Narration.** "Some matrices are easy…" → "…would have made them ones."

### s15_saddle · 8:35.7–9:02.0 (26 s) · ¶3
- **Visual.**
  - The saddle `[[1/2, 1],[1, 1/2]]`. Purple eigenlines lie along (1, 1) with `λ = 3/2` and along (1, −1) with
    `λ = −1/2`.
  - Dots on each line slide along it. Then about 3,000 particles trace curved paths (16-ghost trails).
  - One particle decomposes into its two eigen-components (purple dashed parallelogram), and each component scales
    separately.
  - `e^{tA} = P\,\mathrm{diag}(e^{3t/2}, e^{-t/2})\,P^{-1}`.
- **Tech.** Manim + PointsLayer. The eigen data comes from `verify`.
- **Narration.** "Most matrices aren't diagonal…" → "…in each direction."

### s16_spiral_shear · 9:02.0–9:36.4 (34 s) · ¶4–5
- **Visual.**
  - The spiral `[[−1/4, −1],[1, −1/4]]`: particles wind inward. `-\tfrac14 \pm i` appears, with its real part
    underlined in amber (a shrinking-circle icon) and its imaginary part in purple (a turning arc), each lighting
    as spoken.
  - Then the shear N: arrows horizontal, growing with height, and particles sliding in rows. `N^2 = 0` writes, and
    the series truncates: every term after the second fades to 0, leaving `e^{tN} = [[1, t],[0, 1]]` with t ticking.
- **Tech.** Manim + PointsLayer.
- **Narration.** "What if the eigenvalues are complex?…" → "…the identity plus t N."

### s17_trace · 9:36.4–10:09.9 (34 s) · ¶6–7 (+ 2 s pause)
- **Visual.**
  - Two panels, spiral and shear. An amber blob patch drops into each, with a live area readout (shoelace formula).
  - Spiral: the patch winds in, reading `e^{-t/2}`.
  - Shear: the flow freezes for the pause. Then the patch leans dramatically, but its readout stays `1.00`.
  - `\det e^{A} = e^{\operatorname{tr}A}` writes. Then `\operatorname{tr}A = \nabla\cdot(A\mathbf v)` with a 008
    thumbnail (≤ 3 s). `tr = 0` chips sit under rotation and shear.
- **Tech.** Manim polygons flowed with `expm`.
- **Narration.** "One last pattern ties them together…" → "…they never change area."

---

## CHAPTER 5: The rule that breaks (midpoint re-hook)

### s18_three_shapes · 10:09.9–10:46.5 (37 s) · ¶1–2
- **Visual.**
  - Symbol card `[A,B]`. `e^{a+b} = e^{a}e^{b}` writes, then its matrix version with a `?`, which is the s05 tease
    returning.
  - The orange shear N carries over, and a blue vertical shear B appears beside it.
  - Three framed panels each start from the unit square (î green, ĵ red edges):
    - **A then B** → `[[1,1],[1,2]]`, labelled `e^{B}e^{A}` (maps apply right to left);
    - **B then A** → `[[2,1],[1,1]]`, labelled `e^{A}e^{B}`;
    - **both at once** → `[[\cosh 1,\sinh 1],[\sinh 1,\cosh 1]]`, labelled `e^{A+B}`.
  - All three run at once over 2.5 s. Their outlines then overlay in the centre, and `\det = 1` chips sit under all
    three.
- **Tech.** Manim (shapes flowed with `expm`, matrices from `verify`). The camera pans from the equation into the
  panels.
- **Narration.** "For ordinary numbers…" → "…they're genuinely different."

### s19_series_gap · 10:46.5–11:08.8 (22 s) · ¶3
- **Visual.**
  - Two expansions stack: `e^{A}e^{B} = I + A + B + \tfrac{A^2}{2} + AB + \tfrac{B^2}{2} + \cdots` and
    `e^{A+B} = \cdots + \tfrac{AB + BA}{2} + \cdots`.
  - Matching terms dim pair by pair until only `AB` and `\tfrac{AB+BA}{2}` remain. These resolve into
    `\tfrac12(AB - BA)`, then `[A,B] = AB - BA` (pink) = `[[1,0],[0,−1]]`.
- **Tech.** Manim (`TransformMatchingTex`).
- **Narration.** "The series says why…" → "…is called the commutator."

### s20_loop · 11:08.8–11:46.4 (38 s) · ¶4–5
- **Visual.**
  - A yellow square outline and 1,500 particles go through four legs, each 1.2 s with its active field shown: A,
    then B, then −A, then −B (s = 0.35).
  - The square doesn't return, and a pink gap opens. The camera dollies 2.5× onto the gap, showing the leftover
    squash in x and stretch in y, with the pink `[B,A]` field faint underneath. The camera pulls back.
  - On "parallel park": a top-down line-art car drives, steers, reverses and steers back, ending shifted sideways
    (≤ 5 s).
  - On "the old rule survives": the s16 spiral returns. Its matrix splits into `-\tfrac14 I + J`, with
    `[-\tfrac14 I, J] = 0` (pink zero), then `e^{t(-\frac14 I + J)} = e^{-t/4}e^{tJ}`. Hold (chapter close).
- **Tech.** Manim + PointsLayer (a piecewise exact flow). The numbers come from `verify`.
- **Narration.** "And you can watch it…" → "…a shrink, times a rotation."

---

## CHAPTER 6: Back to the pill, and the planet

### s21_pill_matrix · 11:46.4–12:09.3 (23 s) · ¶1
- **Purpose.** Pay off the intro's problem in one line.
- **Visual.**
  - Symbol card `e^{tA}\mathbf x_0`. The s02 drawing returns exactly (pill, stomach, bloodstream, molecules), now
    with the plane beside it: stomach amount on the horizontal axis, blood amount on the vertical axis.
  - The orange velocity field of `[[-1, 0],[1, -1/4]]` draws on that plane.
  - On "a steady rate" and "in proportion": the matching matrix entries pulse (−k_a, then k_a, then −k_e).
  - On "one line": `\mathbf x(t) = e^{tA}\mathbf x_0` (hero, teal and yellow), and the state dot starts at (1, 0).
- **Tech.** Manim + `PointsLayer` (the state dot and its trail are exact).
- **Narration.** "Now, back to that pill…" → "…times the starting state."

### s22_pill_curve · 12:09.3–12:24.0 (15 s) · ¶2
- **Visual.**
  - Molecules hop and fade as in s02, while the state dot curves through the plane, from (1, 0) toward the origin,
    bulging up into blood first.
  - Below, the blood level b(t) draws as a teal curve over 12 h (1 h per 1.5 s). It peaks at 1.85 h, marked with a
    thin tick and no number, then fades.
  - Overlaid on the curve, the molecule count (yellow, slightly noisy) tracks it closely.
  - On "the two eigenvalues": `\lambda = -1, -\tfrac14` (purple) appear. The rising flank lights with −1 (absorb)
    and the long tail with −1/4 (clear). Hold on the full curve.
- **Tech.** Seeded molecule times from `verify` (2,000 molecules track e^{tA} within 2%; 400 shown).
- **Narration.** "Each molecule makes its own random hop…" → "…how fast you clear."

### s23_earth · 12:24.0–12:45.8 (22 s) · ¶3
- **Purpose.** The emotional peak: the 3D rotation, and it's happening to the viewer.
- **Visual.**
  - The intro's last frame (number line → globe) returns, and the camera flies into the globe: the particle Earth
    fills the frame. Continents are bone dots on a steel-blue shell, with a graticule, a purple tilted axis and a
    teal equator.
  - The planet turns (Clock). On "every point moves at right angles": orange velocity arrows bloom on the lattice,
    longest at the equator and vanishing toward the poles.
  - On "That's a cross product": at one surface point, `\mathbf n` (purple), `\mathbf r` (yellow) and
    `\mathbf n \times \mathbf r` (orange) draw, with a small right-angle mark.
  - On "near the equator": the yellow "you" dot at 45° N leaves a short teal trail. The equator ring pulses, and
    `\approx 1670\ \mathrm{km/h}` appears beside it.
  - On "At a pole": the camera tilts to look down the axis. The pole point spins in place with no arrow.
- **Tech.** numpy Fibonacci sphere + land mask → perspective projection → `PointsLayer` (back hemisphere dimmed).
  Manim draws the axis, arrows and labels, projected by the same camera. The rotation is `expm(θK)`.
- **Animation.** Spin is linear (screen time 1 turn per 12 s). The camera drifts 4°/s in longitude.
- **On screen.** Globe, axis, equator, arrows, n r n×r, "you" dot, 1670 km/h.
- **Narration.** "Now the most beautiful case…" → "…just turn on the spot."

### s24_cross_matrix · 12:45.8–12:59.5 (14 s) · ¶4
- **Visual.** The globe moves to the left half and keeps turning. On the right,
  `\mathbf n \times \mathbf r = \begin{bmatrix}0&-n_z&n_y\\n_z&0&-n_x\\-n_y&n_x&0\end{bmatrix}\mathbf r` writes.
  The zero diagonal pulses, then each ± pair flashes together. `K` names the matrix (orange). Then
  `\dot{\mathbf r} = \Omega K\mathbf r`.
- **Tech.** Manim + the globe layer.
- **Narration.** "That cross product is a matrix…" → "…times its position."

### s25_rodrigues · 12:59.5–13:33.7 (34 s) · ¶5
- **Visual.**
  - `K^3 = -K` (hero).
  - The series `e^{\theta K}` writes to θ⁵, and its terms sort into two rows. The odd powers sit beside K and gather
    `\theta - \tfrac{\theta^3}{3!} + \tfrac{\theta^5}{5!}` into `\sin\theta`. The even powers sit beside K² and
    gather `\tfrac{\theta^2}{2!} - \tfrac{\theta^4}{4!}` into `1 - \cos\theta`.
  - The result: `e^{\theta K} = I + \sin\theta\,K + (1-\cos\theta)\,K^2`. A live θ readout (teal) follows the
    globe's spin.
  - On "one full turn": θ runs to 2π. `\sin` and `1-\cos` tick to 0, the formula collapses to `I`, and the globe is
    back exactly where it started (the "you" dot lands on its starting ghost). Dolly 1.0 → 1.1. Hold 2 s, then fade
    (chapter close).
- **Tech.** Manim (`TransformMatchingTex` for the sorting) + the globe layer. Checks in `verify`: e^{2πK} = I, and
  Rodrigues holds at three angles.
- **Narration.** "Exponentiate it…" → "…all that's left is the identity."

---

## OUTRO

### s26_meaning · 13:33.7–14:01.0 (27 s) · ¶1–2
- **Visual.**
  - The rotation field from s05 returns with sparse, calm particles. Centred: `A` (orange) → `e^{tA}` (teal), with
    a velocity arrow under A and a trip path under e^{tA}.
  - As each fact is spoken, its symbol card slides into a ring: the series, the eigen-decomposition,
    `\det e^{A}=e^{\operatorname{tr}A}`, and `e^{A+B}\ne e^{A}e^{B}`. It's a visual index; nothing new is derived.
- **Narration.** "So what is the matrix exponential, really?" → "…isn't the same as both at once."

### s27_beyond · 14:01.0–14:18.5 (18 s) · ¶3
- **Visual.** Two framed panels.
  - Left (010's callback, 3 s of it): a curve slides sideways, with `e^{h\,\frac{d}{dx}}f(x) = f(x+h)` and the
    generator `\tfrac{d}{dx}` in orange.
  - Right: a complex-phase ribbon advancing (Re and Im as two thin curves), with `e^{-iHt/\hbar}` and `H` in orange.
- **Narration.** "The idea doesn't even stop at matrices…" → "…energy playing the part of the matrix."

### s28_bookend · 14:18.5–14:37.8 (19 s) · ¶4
- **Visual.**
  - Bernoulli's coin and dashed ceiling reappear small at the left. On "the medicine in your blood", "a turning
    planet" and "a quantum computer", three tiles light in a row: the blood curve, the turning globe and the
    quantum wire.
  - On the last two sentences, everything fades except the video's opening typography: `A` on the left, `e^{A}`
    on the right, and the field flowing between them. Hold through the 3 s tail. End-card space is reserved at the
    bottom right.
- **Narration.** "Bernoulli wanted to know…" → "…tells you where they go."

---

## Implementation plan (chapter by chapter, after approval)
0. **Shared helpers first.**
   - Promote `Mat`, `panel` and `grid_lines` (used in 006, 009 and 010) into `aion/components`, with EXPORTS, a
     docstring, a test and `aion docs --build`.
   - Add a video-local `shots.py` with `field(A_track)`, `flow_points(A, X0, clock, trails=8)`,
     `patch(A, pts, clock)`, `molecules(seed, ka, ke)`, `earth(θ_track, cam)` and the line-art set.
   - Ask before downloading the Natural Earth land mask, about 150 KB. (Optional: portraits of Bernoulli and Euler.)
   - Render `design_sheet.py` as a PNG for sign-off: palette, type, line art, field, matrix style, globe.
1. Build the intro (s00–s05) first: it sets the video's identity. Make stills at every beat before any preview.
2. Then ch1 → ch6 → outro, one chapter per approval round: `aion still` at each beat → `aion audit --design` →
   `aion preview`.
3. Explore the LIC backdrop in `lab/2026-11-xx-lic-flow/` before ch2 (two variants, off and faint). Keep it only if
   it stays crisp.
4. Final: `aion render 011 --bg`, then `aion audit 011 --delivery`.
