# 010 — "Calculus Is Secretly Linear Algebra": research and content plan

**Mode:** production, phase 0 (research). **Status:** waiting for topic approval; no storyboard or voiceover yet.
Every formula below was checked with sympy/numpy (`verify.py` checks listed in §6).

---

## 1. What the channel data says (CSV, 2026-09-25 → 2026-11-16)

| video | views | avg view | subs / 1k views | CTR |
|---|---|---|---|---|
| Why e Is Everywhere | 114,115 | 0.8 min (16%) | 7.9 | 4.07% |
| Laplace: "Turns Calculus Into Algebra" | 48,891 | 1.0 min (14%) | **12.0** | 3.83% |
| Jacobian | 47,473 | 1.0 min (8%) | 9.9 | 5.46% |
| Fourier Transform | 29,673 | 1.2 min (10%) | 11.5 | 3.31% |
| SVD | 28,595 | 1.0 min (11%) | 10.9 | 4.78% |
| Taylor: "Turns Any Function Into a Polynomial" (Nov 3) | 24,381 | 1.3 min (9%) | 7.9 | 5.37% |
| Determinant (Nov 12, 5 days old) | 13,739 | 1.2 min (15%) | 8.2 | 5.58% |
| Hessian | 6,387 | 0.9 min (9%) | 5.9 | 4.72% |
| Chain rule | 8,679 | 0.7 min (9%) | 5.3 | 5.06% |

What this means for 010:

1. **The winners are "hidden connection / reframe" titles** in the linear-algebra and calculus cluster
   (Laplace, Jacobian, SVD, Taylor, Determinant). "Calculus is secretly linear algebra" sits right at the
   intersection of the two clusters that work. Good fit.
2. **Plain topic titles underperform** (Chain rule, Partial derivatives, Hessian). The idea needs a *claim*, not a topic name.
3. **Retention is the channel's weak spot.** Average view duration is about 1 minute on every video, whatever its
   length. The first 60 s decides this video. The cold open must pay off something concrete inside a minute.
4. Revenue per 1k views jumps on videos after ~Oct 30 (monetization start), so RPM can't be compared across videos yet.
5. **Overlap warning:** the Laplace video's title already promises "turns calculus into algebra". 010 must
   explain *why* that trick worked (it's diagonalization), not repeat it.

## 2. What already exists (so we don't duplicate it)

| source | what it covers | what it leaves open |
|---|---|---|
| 3Blue1Brown, *Abstract vector spaces* (Essence of LA ch. 16, 2016) | functions as vectors, linearity of d/dx, the derivative matrix on polynomials (1, x, x², …) | stops there. No null space / +C, no rotation, no eigenfunctions, no differential equations, no numerics |
| MIT 18.S096 *Matrix Calculus* (Edelman & Johnson), "Derivatives as linear operators" | the derivative of f at a point as a linear map; Jacobians; matrix-valued functions | a lecture course, not visual; aimed at ML/grad students |
| Michael Penn, high-order derivative via linear algebra | f⁽³⁰³⁰⁾(0) of e^{2x} sin 3x by diagonalizing D on a 2-D span | blackboard algebra, one problem; no picture of *why* |
| Gilbert Strang (Lex Fridman clip, his DE & LA course) | "linear algebra is flat, calculus is curved" | not a visual explainer |
| Our own channel | matrices (009), determinant (006), eigenvectors, SVD, Jacobian, Hessian, Taylor, Fourier, Laplace, e, Euler identity | the **thread that connects them** has never been shown |

**The gap:** nobody has made a visual video that goes past "d/dx is a matrix on polynomials" into what that
buys you: +C as a null space, derivative as a rotation, e^x as an eigenvector, ODEs as linear systems, and the
string's harmonics falling out of a matrix. That is the unique angle.

## 3. The thesis (stated precisely, so the title isn't misleading)

The title is a hook. The video says the precise claim out loud in the intro and in the outro:

> **Differentiation is a linear map on a space of functions.** Once you see that, most of calculus is
> linear algebra *plus a limit*. The facts you memorized (+C, why e^x is special, why sine waves, why
> Taylor series work) are linear-algebra facts in disguise.

Two meanings of "derivative is linear" exist, and the video keeps them separate:
- **(a)** the operator d/dx, taking whole functions to functions, is linear. *This video.*
- **(b)** the derivative of a nonlinear f at a point is the best linear approximation (a Jacobian). *Already covered by the Jacobian video, one-line callback only.*

## 4. Proposed content plan (≈ 12–14 min)

Each chapter has one new idea, one visual, and one "aha". Callbacks to older videos are ≤ 10 s each, with new visuals.

### Cold open (0:00–0:50): the 100th derivative in one glance
- Question on screen: what is the 100th derivative of **e^x sin x**? (Grinding product rule 100 times is hopeless.)
- Answer: **−2⁵⁰ e^x sin x**. Show it as an arrow in a plane whose axes are e^x cos x and e^x sin x: each derivative
  turns it 45° and stretches it by √2. 100 turns = 4500° = 12½ revolutions → it points backwards, length 2⁵⁰.
- "That only works because the derivative is secretly a matrix." Payoff inside 50 s, matched to the retention data.
- Ours, not Penn's: a different function and a visual-rotation explanation rather than diagonalization algebra.

### Ch1: A function is a very long vector (≈ 1:30)
- Sample a curve at 8, then 50, then 1000 points → a column of numbers. Adding functions = adding vectors, scaling = scaling.
- The test for linearity, shown on two curves: (f + g)′ = f′ + g′ and (cf)′ = c·f′. That's the whole definition of a matrix's behavior (callback to 009: "a machine that moves space").
- Honest note: this is a picture, not the definition. Function space is infinite-dimensional.

### Ch2: The derivative matrix, literally (≈ 2:00)
- On sampled functions, slope ≈ (f(x+h) − f(x))/h. Write that for every sample at once → a **band matrix**
  (−1 on the diagonal, +1 next to it, over h). Show it as a 1000×1000 heat-map with a thin bright band.
- Multiply the matrix by sin's column → cos's column comes out. Real numerics, computed live.
- Small case: on polynomials of degree ≤ 3 the matrix is 4×4 with 1, 2, 3 above the diagonal
  (the 3B1B picture, shown briefly and credited as the standard example, then moved past).
- This is how computers actually do calculus (finite differences in every physics simulation).

### Ch3: Why "+C" exists: the null space (≈ 1:45) — **new, key insight**
- That matrix squashes something to zero: constants. Its null space is a line of constants (callback to 006: det = 0, the squash).
- So D has no inverse. Integration = "solve D·F = f", and like any singular system, the answer is
  **one particular solution + anything in the null space**. That is exactly the +C.
- The polynomial matrix is nilpotent: D⁴ = 0 on cubics. "Differentiate enough times and everything dies."

### Ch4: The derivative is a rotation (≈ 2:00)
- On the plane spanned by cos and sin, D is the 90° rotation matrix [[0, 1], [−1, 0]] (with basis order cos, sin).
- D² = −I: "differentiate twice, flip the sign". That's why sin″ = −sin and why springs and waves oscillate.
  D⁴ = I: the famous sin → cos → −sin → −cos cycle is four quarter-turns (callback to 007, i as a rotation).
- Return to the cold open: on e^x cos x, e^x sin x, D is rotate-45° and scale-√2. Integration = the inverse matrix:
  ∫e^x sin x dx = ½e^x(sin x − cos x) in one 2×2 inverse, no integration by parts. (Allowed because this D is invertible on this plane: det = 2.)

### Ch5: The eigenvectors of the derivative (≈ 2:30) — **the unifying payoff, midpoint re-hook**
- Predict: which function does D only stretch, never turn? Answer: **e^{λx}**, with eigenvalue λ.
  That's the real reason e is everywhere (callback to the top video, one line).
- Differential equations become linear algebra: y″ + y = 0 means "y is in the null space of D² + I".
  Its solutions form a **2-D plane** (c₁ cos x + c₂ sin x): superposition is just "null spaces are subspaces".
- **Why Fourier and Laplace work** (the thread through the channel, ≤ 20 s total): they rewrite a function in the
  eigenbasis of D, where differentiating is just multiplying by a number (iω or s). "Turning calculus into algebra" = diagonalizing.

### Ch6: A guitar string is an eigenvector problem (≈ 2:00) — **showpiece visual**
- Take the second-derivative band matrix (1, −2, 1) for a string pinned at both ends. Ask the computer for its eigenvectors.
- Out come the **sine-shaped harmonics**, and the eigenvalues match −(kπ/L)² (checked: −9.869 vs −9.870 at N = 200).
- Animate the modes vibrating, then a plucked string as a sum of them. The overtones of a note are eigenvectors of a matrix.

### Ch7: Taylor's theorem is a matrix exponential (≈ 1:15) — optional climax
- e^{hD} (the series I + hD + h²D²/2! + …) applied to f gives f(x + h). **The exponential of the derivative is a shift.**
- Callback to the Taylor video: the series you learned *is* this matrix exponential.
- Caveat on screen: true for analytic functions (polynomials, e^x, sin…), fails for functions like e^{−1/x²}.

### Outro: where the analogy breaks (≈ 0:45) — honesty, builds trust
- Function spaces are infinite-dimensional: D is not a finite matrix, it has no determinant, and on all functions
  *every* number λ is an eigenvalue. Making this rigorous is functional analysis (the math of quantum mechanics, where operators are observables).
- Calculus = linear algebra + limits. The limit is the part linear algebra can't do for you.

## 5. Accuracy checklist (things that would be wrong or misleading if said loosely)

| claim | correct version |
|---|---|
| "The derivative is a matrix" | Only on a finite-dimensional space (polynomials of degree ≤ n, a span like {e^x cos x, e^x sin x}) or on sampled data. In general it's a linear *operator*. |
| "Integration is the inverse of D" | D isn't invertible (null space = constants). Integration is a *right* inverse: D(∫f) = f, but ∫(Df) = f + C. |
| "e^x is the eigenvector of D" | e^{λx} for every λ. On polynomials D has no eigenvectors except constants (it's nilpotent); e^x isn't a polynomial. |
| Rotation matrix for D on {cos, sin} | Columns are D(cos) = −sin and D(sin) = cos → [[0, 1], [−1, 0]] in basis order (cos, sin). Watch the sign when animating. |
| e^{hD} f = f(x+h) | Analytic functions only; counterexample e^{−1/x²} at 0. |
| Finite-difference matrix | An approximation with error O(h) (forward) or O(h²) (central). Say "approximately" on screen. |
| String eigenvalues | Discrete matrix eigenvalues approach −(kπ/L)² as N grows; low modes match well, high modes don't. Show low modes only. |
| "Calculus is linear algebra" | Hyperbole in the title, stated precisely in the intro and outro (§3). |

## 6. Verified (sympy/numpy, 2026-11-17)
- D on {1, x, x², x³}: 4×4, rank 3, D⁴ = 0.
- e^{hD}p(x) = p(x + h) for a cubic.
- On {e^x cos x, e^x sin x}: D = [[1, 1], [−1, 1]], det 2, eigenvalues 1 ± i; D⁻¹ gives ∫e^x sin x = ½e^x(sin x − cos x).
- d¹⁰⁰/dx¹⁰⁰ (e^x sin x) = −2⁵⁰ e^x sin x.
- On {cos, sin}: D = [[0, 1], [−1, 0]], D⁴ = I.
- y″ + y = 0 → C₁ sin x + C₂ cos x.
- 200-point second-difference matrix: lowest eigenvalues −9.869, −39.475, −88.810 vs exact −9.870, −39.478, −88.826; mode 1 matches sin(πx) exactly.
- Penn's problem: f⁽³⁰³⁰⁾(0) of e^{2x} sin 3x = Im((2+3i)³⁰³⁰). (Context only, not used in the video.)

## 7. Title and thumbnail candidates

| title | note |
|---|---|
| **Calculus Is Secretly Linear Algebra** | the user's idea; clear claim; fits the "hidden connection" pattern |
| The Derivative Is Secretly a Matrix | more concrete, easier to picture on a thumbnail |
| Why +C Exists (It's a Null Space) | strong curiosity hook, narrower |
| The 100th Derivative in One Glance | cold-open hook; good for a Short cut-down |

Thumbnail: `d/dx =` next to a glowing band matrix, or the sin/cos arrow rotating. Crisp black style.

## 8. Not repeating ourselves

- No re-explaining matrices, determinants, eigenvectors, Taylor or Fourier from scratch. Each gets ≤ 10 s, and the new visual does the work.
- New visuals for aion: function-as-column-of-samples, band-matrix heat-map multiplying a curve, a "function plane" with cos/sin (or e^x cos/e^x sin) as axes, null-space line of constants, and a vibrating-string mode stack (numpy eigenvectors → Manim).
- Short cut-downs: the cold open (100th derivative) and "+C is a null space" each stand alone as a 60 s Short.

## 9. Open decisions

1. Length: full plan ≈ 14 min. Dropping Ch7 (Taylor = e^{hD}) gives ≈ 12.5 min.
2. Title: "Calculus Is Secretly Linear Algebra" vs "The Derivative Is Secretly a Matrix".
3. Cold open: 100th derivative (recommended) vs "why +C exists".

## Sources
- 3Blue1Brown, Abstract vector spaces: https://3blue1brown.com/lessons/abstract-vector-spaces
- MIT 18.S096 Matrix Calculus, lecture notes: https://ocw.mit.edu/courses/18-s096-matrix-calculus-for-machine-learning-and-beyond-january-iap-2023/pages/lecture-notes-and-readings/
- MIT 18.S096, Derivatives as linear operators: https://rosetta.to/u/mitocw/lecture-1-part-2-derivatives-as-linear-operators
- Michael Penn's problem, summarized: https://graysoncroom.github.io/blog/posts/solving-calculus-problems-with-linear-algebra
- Penn video listing: https://classcentral.com/course/youtube-an-amazingly-powerful-tool-solving-a-calculus-problem-using-linear-algebra-167727
- Strang, Linear Algebra vs Calculus: https://rosetta.to/u/lexfridman/gilbert-strang-linear-algebra-vs-calculus
- Eigenfunctions of d/dx (Cambridge IA notes): https://dec41.user.srcf.net/h/IA_M/differential_equations/4_1
