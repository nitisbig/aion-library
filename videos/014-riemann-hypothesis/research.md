# The Riemann Hypothesis, Visually Explained: research reference sheet

**Checked:** 2026-11-21 (one day after the Alpöge announcement). **Re-check every row tagged `claimed` or
`under verification` (A7–A19) right before voicing and again right before the final render.**

Status tags: **established** (accepted theorem or historical fact) · **computed** (we compute it in `verify.py`) ·
**conditional** (proved assuming RH) · **conjecture** (believed, unproved) · **claimed** (announced, not
independently accepted) · **under verification** (checks running).

Every number on screen or spoken comes from `verify.py` (73 checks, about 2 min; run
`uv run python videos/014-riemann-hypothesis/verify.py` from the repo root).

## 1. Corrections to the original brief
| Brief | What the sources say | What the video says |
|---|---|---|
| Claude raised the bound "from 41.6% to 67.2%" | Anthropic's post gives exactly those figures. The paper (Alpöge & Furman, arXiv 2608.13637) proves **at least two thirds of zeros are simple *and* on the line**, and 0.6725 with the Montgomery–Taylor window. The previous record was 5/12 ≈ 41.7% (Pratt–Robles–Zaharescu–Zeindler). The post rounds it to 41.6%. | Spoken: "from five twelfths to two thirds" (P44) and "five twelfths, just under forty-two percent" (P39). On screen: `5/12` → `2/3` and `≥ 2/3 simple and on the line`, no decimals |
| "Claude's improvement" | The paper's comment says the proof was "discovered autonomously by Claude (Anthropic)" and "verified and communicated by the listed authors". The post says "an unreleased research version of Claude". Conrey and Goldston examined the paper. A Lean formalization passes `comparator`. | "an unreleased research version of Claude had found a proof … Alpöge and … Furman checked it and wrote it up. Conrey and Goldston … examined it, and it was checked in Lean" |
| "17-million-line Lean formalization" | **No source gives a line count.** Verified: 175,187 Lean 4 files, a 239 MB archive and a 61.5 GB exported proof. The 1,468,418 declarations are con-leche's total for the whole export, which includes Mathlib and Lean core. | The file count only |
| "proposed proof of the full RH" | Alpöge's note claims RH and GRH; Sutherland's page: "'GRH' here means Dirichlet L-functions only". The note expects the extended RH "with more time". | "four more theorems extend it to a family called Dirichlet L-functions" (P46) |

## 2. AI developments (2026)
| # | Fact | Status | Source |
|---|---|---|---|
| A1 | 10 Aug 2026: Anthropic post "Learning more about Claude's mathematical capabilities". "An unreleased research version of Claude has improved on a longstanding lower bound… from 41.6% to 67.2%." Updated 13 Aug with a revised paper. | established (that it was announced) | https://www.anthropic.com/research/riemann-zeta |
| A2 | Same post: "We don't expect that the techniques Claude used will lead to proving the Riemann hypothesis." | established (quote) | same |
| A3 | Validation: Levent Alpöge and Ralph Furman (Anthropic) studied and validated it. Brian Conrey and Dan Goldston examined it. Lean repo `anthropics/zeta-23-lean` passes `comparator`. Not journal-refereed as of this check. | established (process); result = theorem with machine check, not yet peer-reviewed in print | same; https://arxiv.org/abs/2608.13637 |
| A4 | Paper: Alpöge & Furman, "More than two thirds of the zeta zeros are simple and on the critical line", arXiv 2608.13637, v1 13 Aug 2026, v2 19 Aug. ≥ 2/3 simple and on the line, ≥ 5/6 distinct, 0.6725 / 0.8362 with the Montgomery–Taylor window. Previous records 5/12 and 0.6603. | established preprint, Lean-checked | https://arxiv.org/abs/2608.13637 |
| A5 | Lamzouri, arXiv 2609.02882 (2 Sep 2026): a new, simpler proof: > 67.25% simple and on the line, ≥ 83.62% distinct, ≥ 88.76% simple or on the line. It credits the Claude proof and calls it "technically intricate". | established preprint (independent human route) | https://arxiv.org/abs/2609.02882 |
| A6 | Cobeli & Zaharescu, arXiv 2610.23467 (16 Oct 2026): > 8/9 of zeros are simple **or** on the line. A different quantity, not involving AI. Not used. | preprint | https://arxiv.org/abs/2610.23467 |
| A7 | 20 Nov 2026: Levent Alpöge posts a four-page note: "I believe I have, working with Claude, discovered a proof of the Riemann Hypothesis." It extends to GRH and he expects the extended RH "with more time". "Claude and I have also formalized the arguments without assumptions." He chose "to only present Lean". | **claimed** | https://alpo.ge/remark.pdf (read 2026-11-21 via pdftotext); Scientific American (J. Howlett, 20 Nov 2026) |
| A8 | Archive: 14 parts (`alpo.ge/lean.tar.gz.part01` … `part14`, linked from the note's footnote 1; mirror github.com/Deicyde/riemann-hypothesis), 175,187 Lean 4 files, Lean v4.33.1 + Mathlib v4.33.1, 239,275,554 bytes, export 61,570,595,788 bytes. The five headline theorems use only `propext`, `Classical.choice`, `Quot.sound`; Mathlib files match the official cache. | established (facts about the files) | https://math.mit.edu/~drew/grh/ (updated 2026-11-21 09:30 UTC) |
| A9 | Andrew Sutherland (MIT), "checks run with Claude Code" on cloud machines. As of 09:30 UTC 21 Nov: all 175,187 modules compile; leanchecker 175,187/175,187; nanoda accepts; con-leche master accepts; con-leche `--compare` accepts all five theorems; lean4lean passes (5 modules needed a raised limit). **Running:** `lake comparator` (statement comparison and axiom check already passed in one run; kernels in progress) and the Lean default and paranoid kernel replays of the export. **Re-checked later on 21 Nov:** page still stamped 09:30 UTC; the same runs in progress (comparator on the main proof and on the Robin combination, the Lean default and paranoid replays). Caveats the page lists: built on unsandboxed cloud machines by calling `lean` directly, not `lake build`; per-file .olean hashes depend on the build path; the export hasn't been compared with a sandboxed build's export. | **under verification** | same |
| A10 | Headline Lean statement = Mathlib's definition: `def RiemannHypothesis : Prop := ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1), s.re = 1 / 2`. Sutherland: a pass relies on "Mathlib's definitions being what they are intended to be". Four further theorems include the statement for all Dirichlet L-functions. (Mathlib is Apache-2.0, so the definition can be shown verbatim.) | established (the statement text) | same |
| A11 | Expert reactions (SciAm): Sutherland: "There is much work to be done to understand the mathematical details." Pasten: "something like a Rosetta Stone" if correct. Pagano: conditional, based on a first high-level scan. Not used in narration. | quotes | Scientific American, 20 Nov 2026 |
| A12 | Clay Mathematics Institute lists RH as **Unsolved**. Rules: publication in a qualifying outlet, then ≥ 2 years, then general acceptance. Clay does not accept direct submissions. $1M per problem. | established | https://www.claymath.org/millennium/riemann-hypothesis/ ; Millennium Prize rules PDF |
| A13 | Wikipedia mentions OpenAI manuscripts (Oct 2026) on zero-free regions. **Not confirmed from a primary source, so not used.** | unverified | — |
| A14 | The note on length and understanding: the argument "is incredibly long at the moment"; he is presenting "a complete argument before having mastered a massive neighbourhood around its mathematics"; he intends "to write it properly". Used in P49 as paraphrase. | **claimed** (the author's own account) | https://alpo.ge/remark.pdf |
| A15 | The note on who did what and where it came from: "I guided us to the right situation analogous to that toy setting"; "Claude far outpaced me near the finish line"; "This argument is a descendant of Stepanov's", whose argument resolves "Riemann over function fields" using multiplicity, which "is hard to find over the integers, corresponding to something like differentiating whole numbers". Its rough timeline (which it says Claude provided) runs 6 Oct → 16 Nov 2026. Used in P49–P50 as paraphrase. | **claimed** (the author's own account) | same |
| A16 | Sutherland's page: as a check independent of Mathlib's zeta definition, the proof was combined with "an independent formalization of Robin's and Lagarias's criteria". On that combination (09:30 UTC): nanoda accepts, con-leche master accepts (1,472,825 declarations), con-leche `--compare` accepts, `lake comparator` running; `Robin1984` alone passes comparator. Used in P47 as "joined to a separate formalization … being checked". | **under verification** | https://math.mit.edu/~drew/grh/ |
| A17 | Scientific American (C. Moskowitz, 20 Nov 2026), headline "The AI Riemann hypothesis proof is almost certainly true, independent mathematicians attest" (the magazine's framing; not used). Sutherland: "Honestly the chance that anything is fishy here is approximately zero." Buzzard, on the Lean Zulip: "We still await a successful comparator run." Used in P48 (Sutherland, attributed) and on the s28 quote card. | quotes | https://www.scientificamerican.com/article/the-ai-riemann-hypothesis-proof-is-almost-certainly-true-independent-mathematicians-attest/ |
| A18 | K. Buzzard, "…and the proof is checked in Lean", Xena blog, 12 Nov 2026: a general guide (it predates the claim and doesn't mention it) with four questions for any "checked in Lean" claim: (1) does the Lean statement match the informal one; (2) does the code compile; (3) does it prove the theorem as stated (`lake comparator`); (4) does it exploit a kernel bug (`lake comparator --paranoid`). Used in P46 ("the first question to ask of any Lean proof") and as the s26–s28 checklist. | established (what he wrote) | https://xenaproject.wordpress.com/2026/11/12/and-the-proof-is-checked-in-lean/ |
| A19 | Other reactions, 20 Nov, on X (via OfficeChai): E. Glazer: the formal statement "is in fact GRH" (agrees with A10: RH plus four Dirichlet theorems); T. Bloom: Lean experts are investigating, follow the Lean Zulip. Some aggregator sites repeat "17 million lines": still unsourced, still not used. None of this is in the narration. | secondary | https://officechai.com/ai/how-mathematicians-have-reacted-to-claimed-riemann-hypothesis-proof-by-anthropics-levent-alpoge/ |

## 3. Mathematics and history
| # | Fact | Status | Source |
|---|---|---|---|
| M1 | Riemann, "Ueber die Anzahl der Primzahlen unter einer gegebenen Grösse", Monatsberichte, Berlin Academy, Nov 1859, 9 pages, his only paper on number theory. "…es ist sehr wahrscheinlich, dass alle Wurzeln reell sind. … ich habe indess die Aufsuchung desselben nach einigen flüchtigen vergeblichen Versuchen vorläufig bei Seite gelassen" ("after some fleeting, vain attempts, put aside the search", said of ξ, whose roots are real exactly when RH holds). Also contains the continuation, the functional equation and the explicit formula. | established | https://en.wikipedia.org/wiki/On_the_Number_of_Primes_Less_Than_a_Given_Magnitude |
| M2 | Siegel (1932) found Riemann's own zero computations in his unpublished papers (the Riemann–Siegel formula). | established | https://en.wikipedia.org/wiki/Riemann%E2%80%93Siegel_formula |
| M3 | Euler used ζ(s) for real s "as early as 1737", and the product over primes dates from there. The product converges (absolutely) only for Re s > 1. | established | https://en.wikipedia.org/wiki/Prime_number_theorem ; https://en.wikipedia.org/wiki/Euler_product |
| M4 | Basel problem: ζ(2) = π²/6, solved by Euler in 1734, announced 1735. | established, computed | https://en.wikipedia.org/wiki/Basel_problem |
| M5 | Gauss considered prime density "in the year 1792 or 1793", aged 15 or 16 (his 1849 recollection). Legendre conjectured in 1797 or 1798. | established | https://en.wikipedia.org/wiki/Prime_number_theorem |
| M6 | PNT proved independently by Hadamard and de la Vallée Poussin, 1896. The key step is that ζ has no zeros on Re(s) = 1. | established | same |
| M7 | von Koch 1901: RH ⇔ π(x) = li(x) + O(√x log x). | established | same; https://en.wikipedia.org/wiki/Riemann_hypothesis |
| M8 | Schoenfeld 1976 (Math. Comp. 30): assuming RH, \|π(x) − li(x)\| < √x log x / (8π) for x ≥ 2657. | conditional, computed for x ≤ 10⁶ | https://en.wikipedia.org/wiki/Prime-counting_function |
| M9 | Littlewood 1914: π(x) − li(x) changes sign infinitely often. No crossing below 10¹⁹ (Büthe 2015). A crossing exists near 1.397 × 10³¹⁶ (Saouter–Demichel 2010), so the first one lies between. | established | https://en.wikipedia.org/wiki/Skewes%27s_number |
| M10 | Hardy 1914: infinitely many zeros on the critical line. | established | https://en.wikipedia.org/wiki/Riemann_zeta_function |
| M11 | Selberg 1942: a positive proportion. Levinson 1974: one third. Conrey 1989: two fifths. Pratt–Robles–Zaharescu–Zeindler 2020: 5/12. | established | https://en.wikipedia.org/wiki/Riemann_hypothesis ; https://arxiv.org/abs/1802.10521 |
| M12 | First 10¹³ zeros are on the line (Gourdon & Demichel 2004). Clay: "checked for the first 10,000,000,000,000 solutions". Platt & Trudgian: every zero with 0 < γ ≤ 3·10¹² is on the line (arXiv 2020). | established | claymath.org; https://arxiv.org/abs/2004.09765 |
| M13 | Montgomery 1973 pair correlation; Dyson pointed out the match with random Hermitian matrices (GUE), also used for heavy-nucleus energy levels; Odlyzko's numerics (1987). Hilbert–Pólya idea of a hidden operator. | conjecture (with strong numerical support) | https://en.wikipedia.org/wiki/Montgomery%27s_pair_correlation_conjecture |
| M14 | RH is part of Hilbert's eighth problem. "Many consider it to be the most important unsolved problem in pure mathematics." | established | https://en.wikipedia.org/wiki/Riemann_hypothesis |
| M15 | A density statement ("100% of zeros") still allows infinitely many exceptions, which is why proportion results, however large, don't settle RH. The squares among the whole numbers are the screen example (density 0, infinitely many). | established (elementary), computed | — |
| M16 | Fundamental theorem of arithmetic: every integer > 1 is a product of primes, uniquely up to order. | established, computed (60) | https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic |
| M17 | Euclid's theorem (Elements IX.20, c. 300 BC): multiply a finite list of primes and add 1; its prime factors are not on the list. The product + 1 need not be prime (30031 = 59 · 509). | established, computed | https://en.wikipedia.org/wiki/Euclid%27s_theorem |
| M18 | Lehmer 1956 (Acta Math. 95): two zeros near t ≈ 7005.06 and 7005.10, so close that Z barely changes sign between them ("Lehmer's phenomenon"). | established, computed (zeros #6709, #6710) | https://en.wikipedia.org/wiki/Z_function |
| M19 | de Bruijn–Newman constant Λ: RH ⇔ Λ ≤ 0. Newman (1976) conjectured Λ ≥ 0 ("if true, only barely so"). Rodgers & Tao proved Λ ≥ 0 (arXiv 1801.05914, Jan 2018; Forum Math. Pi 2020). So RH ⇔ Λ = 0. | established | https://en.wikipedia.org/wiki/De_Bruijn%E2%80%93Newman_constant ; https://arxiv.org/abs/1801.05914 |
| M20 | Hasse (announced 1933, proof 1936): for an elliptic curve over 𝔽ₚ, \|N_p − (p + 1)\| ≤ 2√p (N_p counts projective points; the affine count A_p = N_p − 1 satisfies \|A_p − p\| ≤ 2√p). | established, computed (all primes < 5000 for y² = x³ + x + 1) | https://en.wikipedia.org/wiki/Hasse%27s_theorem_on_elliptic_curves |
| M21 | Weil: RH for all curves over finite fields (announced 1940, proof 1948). | established | https://en.wikipedia.org/wiki/Weil_conjectures |
| M22 | Deligne 1974 ("La conjecture de Weil. I", Publ. Math. IHÉS 43): the RH part of the Weil conjectures for all smooth projective varieties. | established | same |
| M23 | Cramér 1920: assuming RH, p_{n+1} − p_n = O(√p_n log p_n). | conditional | https://en.wikipedia.org/wiki/Prime_gap |
| M24 | Miller 1976: a deterministic polynomial-time primality test, correct assuming GRH. | conditional (on GRH, not RH) | https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test |
| M25 | Robin 1984: RH ⇔ σ(n) < e^γ n ln ln n for every n > 5040. Lagarias 2002: RH ⇔ σ(n) ≤ H_n + e^{H_n} ln H_n for every n ≥ 1. | established (equivalences), computed (Robin to 10⁶) | https://en.wikipedia.org/wiki/Divisor_function#Growth_rate |
| M26 | Stepanov's method (1969): an elementary proof of the RH bound for curves over finite fields, using an auxiliary polynomial that vanishes to high multiplicity at every point; extended to all curves by Bombieri (Séminaire Bourbaki 1973, "Counting points on curves over finite fields, d'après S. A. Stepanov"). | established | https://en.wikipedia.org/wiki/Weil_conjectures ; Bombieri, Sém. Bourbaki exp. 430 |
| H1 | Hilbert presented his problems at the International Congress of Mathematicians, Paris, August 1900; RH is part of problem 8 (M14). | established | https://en.wikipedia.org/wiki/Hilbert%27s_problems |
| H2 | The Clay Millennium Prize Problems were announced on 24 May 2000 in Paris; seven problems, $1M each. | established | https://www.claymath.org/millennium-problems/ |
| H3 | Turing computed zeros on the Manchester Mark 1 (1950; published 1953, "Some calculations of the Riemann zeta-function") and introduced the method that certifies every zero up to a height is on the line. | established | https://en.wikipedia.org/wiki/Riemann_hypothesis#Numerical_calculations |

## 4. Computed in verify.py
First zeros 14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178 (spoken as 14, 21, 25, 30, 33, 38). There
are 649 zeros up to height 1000. ζ(−1) = −1/12. Trivial zeros at −2, −4, … π(100) = 25, π(1000) = 168,
π(10⁶) = 78,498; li(10⁶) is within 0.17%. The largest gap below 100 is 89 → 97, and below 1000 it is 887 → 907.
π(x) < li(x) for all 2 < x ≤ 10⁶. The Schoenfeld envelope holds for 2657 ≤ x ≤ 10⁶. The explicit formula with 100 zero
pairs is within 0.25 of the true count at every half-integer below 100. 60 = 2·2·3·5; 211 is prime and ≡ 1 mod 2, 3, 5,
7; 30031 = 59 · 509. The product over primes below 10⁵ matches ζ(2 + 5i) to 1e-5 and keeps swinging at ½ + 20i. The
Lehmer pair is zeros #6709 and #6710 (7005.062866, 7005.100565): gap 0.0377 vs average 0.8955 (23.75×), and Z peaks
at +0.00397 between them. y² = x³ + x + 1 has 104 solutions mod 101, and every prime below 5000 satisfies
\|A_p − p\| ≤ 2√p (max ratio 0.9917). σ(5040) = 19,344 > 19,237.1, and Robin's inequality holds for every n from
5041 to 10⁶ (26 exceptions from 3 to 5040).

## 5. Framing rules for the script
1. Every 2026 AI claim is attributed to a person or paper, never "AI proved".
2. Proportion results are never conflated with RH. M15 is said out loud.
3. The 20 Nov claim is always "claimed" or "a proposed proof", with "checks still running at the time of recording".
4. Lean checks that every step follows from the definitions. It does not check that the definitions say what we
   mean, nor does it give understanding. A human-readable argument and community scrutiny are still to come.
5. Deterministic primality testing (Miller) is conditional on GRH, not RH. The script says "Some results need a
   stronger version, the generalized Riemann hypothesis".
6. Conflict of interest: this script was drafted with Claude, the model named in the claims. The AI chapter
   should be read by an independent mathematician before release.
7. The note is paraphrased, not quoted at length. On screen, its content appears only as short chips labeled
   `per L. Alpöge's note`. The Stepanov paragraph says "he describes" and "he writes": it reports the author's
   account, not an established fact about the proof.
8. The Robin paragraph says the combination "is being checked", because comparator was still running on it. Update
   the wording if that check finishes before voicing.
9. Expert quotes come with name, outlet and date, and in pairs: confidence in the machine checks (Sutherland) sits next to the open
   question about the statement (Buzzard). Headlines are never quoted as findings.
