# YouTube package: The Riemann Hypothesis, Visually Explained

Final file: `videos/014-riemann-hypothesis/out/riemann_hypothesis_4k30.mp4` (3840×2160, 30 fps, 16:20). It is being rendered on Kaggle.

The narration was recorded on 21 Nov 2026, while the checks were still running. Before you upload, re-read
math.mit.edu/~drew/grh and claymath.org. If anything has changed, update the "Status" line in the description. The
video's own wording ("as I record this") stays accurate either way.

---

## Title

**Recommended:** `The Riemann Hypothesis, Visually Explained (and the Claimed AI Proof)`

This title leads with the evergreen search term and still points to the news. The word "claimed" keeps it accurate:
the proof is not yet accepted, and Clay still lists the problem as unsolved.

Alternatives:

| Style | Title |
|---|---|
| Search-first | The Riemann Hypothesis, Visually Explained |
| Search-first | What Is the Riemann Hypothesis? Primes, Zeta and the Zeros |
| News-first | An AI-Assisted Proof of the Riemann Hypothesis? What's Actually Been Checked |
| News-first | The Riemann Hypothesis Has a Claimed Proof. Here's What It Says |
| Curiosity | The Primes Are Built From Waves |
| Curiosity | 175,000 Lean Files and a 167-Year-Old Problem |

Avoid titles like "AI Solved the Riemann Hypothesis" or "Riemann Hypothesis PROVEN". They overstate the status, they
contradict the video's last chapter, and they invite "misleading title" comments that hurt retention.

Thumbnail idea: on the left, the prime staircase in amber with smooth waves hugging it. On the right, a vertical line
of glowing zeros at ½. Between them a bold `ζ(s) = 0` with a small `proved?` underneath. Black background, crisp lines,
to match the video. A news variant: the 1859 paper page next to a grid of Lean file tiles, captioned `1859 → 2026`.

---

## Description (paste this)

```
The Riemann Hypothesis, Visually Explained (and the Claimed AI Proof)

On 20 November 2026, Levent Alpöge posted a four-page note saying he believes he has found a proof of the Riemann hypothesis, working with Anthropic's AI model Claude, backed by about 175,000 files of Lean code. To judge that claim, you need to know what the hypothesis says.

This video builds it from the ground up. The prime staircase is rebuilt from waves, one wave for each zero of the zeta function. Then: Euler's product, Riemann's complex spirals, domain coloring, analytic continuation, the critical line, and why ten trillion checked zeros still aren't a proof. Finally we go back to November and see what Lean checks, what it doesn't, and where things stand.

Status (21 Nov 2026): a claimed proof under independent checking. Every machine check that has finished has accepted it, and a few were still running. No human-readable paper exists yet. The Clay Institute lists the problem as unsolved and considers a solution only two years after publication and general acceptance.

Chapters
0:00 A claimed proof, November 2026
0:49 The prime staircase, rebuilt from waves
1:51 Primes: the atoms of arithmetic
2:48 Gauss and the prime number theorem
3:39 The zeta function
4:08 Euler's product: the primes inside zeta
4:35 Riemann 1859: complex inputs and spirals
5:12 Coloring the complex plane
5:43 Analytic continuation
6:22 Trivial zeros and the critical strip
7:11 The Riemann hypothesis
7:37 How we check ten trillion zeros
8:11 How the zeros build the primes
8:47 What a zero off the line would do
9:25 Why evidence isn't proof
10:38 42% of the zeros, after a century
11:03 A version that has been proved (Weil, Deligne)
11:36 What a proof would mean
12:32 August 2026: two thirds of the zeros
13:05 What Lean checks, and what it doesn't
14:12 The independent checks
15:08 Where things stand
15:44 Back to the staircase

Sources
Alpöge's note: https://alpo.ge/remark.pdf
Sutherland's verification page: https://math.mit.edu/~drew/grh/
Scientific American: https://www.scientificamerican.com/article/the-ai-riemann-hypothesis-proof-is-almost-certainly-true-independent-mathematicians-attest/
Alpöge & Furman, two thirds of zeros on the line: https://arxiv.org/abs/2608.13637
Lamzouri, independent proof: https://arxiv.org/abs/2609.02882
Rodgers & Tao, de Bruijn–Newman constant: https://arxiv.org/abs/1801.05914
Clay Mathematics Institute: https://www.claymath.org/millennium/riemann-hypothesis/
Riemann, 1859: https://en.wikipedia.org/wiki/On_the_Number_of_Primes_Less_Than_a_Given_Magnitude

Image credits
Levent Alpöge: photo Marlene Ruf, MFO, CC BY-SA 2.0 DE
André Weil: photo Konrad Jacobs, MFO, CC BY-SA 2.0 DE
Hugh Montgomery: photo Renate Schmid, MFO, CC BY-SA 2.0 DE
Freeman Dyson: photo by Flickr user ioerror, CC BY-SA 2.0
Kevin Buzzard: photo by Paula Buzzard, CC BY-SA 3.0
Andrew Sutherland: photo Ken Richardson (MIT, 2016), CC BY-SA 4.0
Other portraits and Riemann's 1859 paper: public domain, via Wikimedia Commons. Portraits are cropped and shown in grayscale.
Anthropic and Claude marks and the Clay Mathematics Institute logo are trademarks of their owners, shown for identification.

Every number on screen is computed from the mathematics or taken from the sources above.
Made with Manim, GPU shaders and Skia. Narration by ElevenLabs.

#riemannhypothesis #math #primes
```

Notes:
- Chapter starts are real scene cuts from `beats.py`. Some short scenes are merged into their neighbors (the 14 s map, the
  sieve, the noproduct/near-miss pair, Robin, Stepanov). The shortest chapter is 7:11–7:37 (26 s). All are over 10 s, and the
  first starts at 0:00, so YouTube will show them.
- The CC BY-SA photos require attribution. Keep the "Image credits" block even if you shorten the rest. The
  full list is in `credits.md`.
- The AI facts are worded the same way as the narration: "claimed", "believes", "checks under way". Keep that wording
  if you edit the description.
- A pinned comment works well for updates, e.g. "Update (date): Sutherland's page now shows …". You can edit it without
  touching the video.

### Tags

Riemann hypothesis, Riemann zeta function, zeta function zeros, prime numbers, prime number theorem, critical line,
analytic continuation, Euler product, domain coloring, complex analysis, number theory, millennium prize problem,
Levent Alpoge, Claude AI math, AI proof, Lean theorem prover, formal verification, math visualization, math animation,
Manim, 3Blue1Brown style

(≈ 400 characters, under YouTube's 500-character limit.)

### Category, language and settings

- Category: Education. Language: English. Captions: upload `assets/subtitles.srt` as English captions, so they are
  timed to the real narration.
- Altered or synthetic content: **Yes**. The narration voice is AI-generated (ElevenLabs), and YouTube asks creators to
  disclose realistic synthetic voices.
- Made for kids: No.
