# The Riemann Hypothesis, Visually Explained: voiceover (v2)
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the pauses that cuts snap to.

     Voice: calm, plain, first-person documentary. Explain before naming; one idea per paragraph; concrete
     example first (60, 211, 89 to 97, height 7005). The picture explains, the narration names what we see.
     No equation is read symbol by symbol except the value "pi squared over six".
     Banned (AI-sounding): astonishing, remarkable, extraordinary, stunning, profound, delve, journey, tapestry,
     unlock, crucial, "here's the thing", "in fact", "at its heart", "this is where", "and yet", em dashes,
     stacked rhetorical questions, three-beat slogan endings.

     Spine: the primes are built from waves, one per zeta zero; the hypothesis says every wave grows as slowly as
     possible. The news opens the video, the maths gives the viewer what they need to judge it, and CH7 judges it.

     Promises (made → paid):
       judge the claim yourself (INTRO → CH7) · waves from points on one line (INTRO → CH4)
       the sieve comes back (CH1 → CH2 Euler product) · the one fact about zeros (CH1 → CH4)
       how far apart can they get (CH1 → CH4 von Koch) · the clock-arithmetic version (CH5 → CH7 Stepanov)
       Riemann "put aside the search" (CH3 → OUTRO)

     Every number is computed or sourced in verify.py; every fact has a row in research.md.
     CH7 sits last, in its own paragraphs, so a status update re-bills only those chunks.
     Re-check research.md A7 to A19 right before voicing (Sutherland's page changes as checks finish).
     Pronunciation to check by ear: Alpöge, de la Vallée Poussin, Eratosthenes, Lamzouri, Deligne, Lehmer, Stepanov.
     2,731 words. Voiced 2026-11-21: 979.6 s (16:20) including the 1.5 s lead-in and 3 s tail. The three paragraphs once marked optional
     (speculation, Robin, Stepanov: 158 words, about 56 s) stay in, decided 2026-11-21.

     Generate: uv run aion voice 014-riemann-hypothesis --dry-run   then   uv run aion voice 014-riemann-hypothesis -->

# INTRO

On November the twentieth, twenty twenty-six, Levent Alpöge, a mathematician at the AI company Anthropic, posted a four-page note. In it, he writes that he believes he has found a proof of the Riemann hypothesis, working with the company's AI model, Claude.

Instead of a paper, the note links to about a hundred and seventy-five thousand files in Lean, a language in which a computer checks every step of a proof. As I record this, those checks are still under way.

The Riemann hypothesis has been open since eighteen fifty-nine. It carries a million-dollar prize, and many mathematicians consider it the most important open problem in pure mathematics.

To judge the claim, we need to know what the hypothesis says. That starts with the prime numbers.

These are the primes below a hundred, the numbers above one that can only be divided evenly by one and themselves. Count them as you go, and the count climbs like a staircase, one step per prime, at places no simple rule predicts.

Here is a smooth curve that follows the overall trend, but has no steps. Now I'll add a single wave to it. Then five, then thirty, then a hundred. With each batch, the curve hugs the staircase more closely, until it turns a corner at every prime.

Each wave comes from one point, drawn on the right. These points are zeros of something called the Riemann zeta function, and every one we used sits on the same vertical line. The Riemann hypothesis says that all of them do, all infinitely many.

That takes some unpacking: the zeta function, its zeros, why the hypothesis is so hard to prove, and what a proof would mean. Then we'll come back to November, so you can judge for yourself what has been established, and what hasn't.

# CH1 THE PRIMES

Every whole number above one can be built by multiplying primes, in only one way. Sixty is two times two times three times five, and apart from the order, there's no other way to build it. The primes are the atoms of arithmetic.

More than two thousand years ago, Euclid showed that the primes never run out. Multiply any list of them and add one. Dividing by any prime on the list leaves a remainder of one, so the result's prime factors are all new.

Finding them is mechanical. Write out the numbers up to a hundred, keep two, and cross out its other multiples. Do the same for three, five and seven, and what survives are the primes. This is the sieve of Eratosthenes, and it will come back in a different form.

Predicting them is another matter. Some come in close pairs, like eleven and thirteen, while after eighty-nine, seven numbers go by with no prime at all.

Over long stretches, though, there's a pattern. Around seventeen ninety-two, a teenage Carl Friedrich Gauss noticed in tables of primes that a number near x is prime with a chance of about one over the natural log of x. Near a million, that's about one in fourteen.

Adding up those chances gives a smooth curve, the logarithmic integral. At a million, it's within two tenths of a percent of the true count. In eighteen ninety-six, Jacques Hadamard and Charles de la Vallée Poussin each proved that the ratio of the two goes to one: the prime number theorem. Both proofs used the zeta function, and both needed one fact about where its zeros can't be.

Still, the staircase never matches the curve exactly. How far apart can they get? That question is what the Riemann hypothesis is about.

# CH2 THE ZETA FUNCTION

Here's the function. Pick a number s, and add up one, plus one over two to the s, plus one over three to the s, and so on forever. The total is zeta of s.

A sum like this only has a value if its running total settles down. When s is one, it doesn't: the total grows without limit. When s is two, it settles, and in seventeen thirty-four Leonhard Euler found the value: pi squared over six.

Euler also found the link to the primes. Multiply the sum by one minus one over two to the s, and every term with an even number cancels. Multiply by one minus one over three to the s, and the remaining multiples of three cancel. It's the sieve again. Do this for every prime, and only the one is left. So a sum over all whole numbers equals a product over the primes, and zeta carries information about every prime.

In eighteen fifty-nine, Bernhard Riemann took the next step, in a nine-page paper, the only one he ever published on number theory. He let s be a complex number: a point in a plane, where the real part says how far right it sits, and the imaginary part says how high.

Then each term becomes an arrow. The real part of s sets its length, and the imaginary part turns it, by an angle that grows with the logarithm of n. Laid end to end, the arrows curl into a spiral, and when the real part is more than one, the spiral closes in on a single point: zeta of s.

The outputs are complex too, so a graph would need four dimensions. Instead, we color the plane: each point gets a hue for the direction of zeta's value there, and bands that mark its size. Where all the colors meet, the value is zero. That's all a zero is: an input where the output is exactly zero.

This is zeta where the sum works. Left of the line where the real part is one, the arrows don't shrink fast enough, and the spiral never closes.

A simpler sum has the same problem. One plus x plus x squared, and so on, only adds up when x is between minus one and one. There it equals one over one minus x, and that expression works for every x except one. The formula keeps going where the sum stops.

Functions like zeta, smooth in the complex sense, are rigid: know one on any small patch of the plane, and there's at most one way to extend it. Riemann found the extension of zeta to the whole plane, except the point one, and a symmetry linking its value at s to its value at one minus s, called the functional equation.

# CH3 THE ZEROS

So where is zeta zero? The functional equation contains a sine, and that sine makes zeta zero at minus two, minus four, minus six, and every negative even number. These are the trivial zeros, and they're well understood.

Every other zero lies in a vertical band between real part zero and real part one, called the critical strip. Its center line, where the real part is exactly one half, is the critical line.

Moving up the line, the first zero is at a height of about fourteen, then twenty-one, twenty-five, thirty, thirty-three and thirty-eight. Each one is exactly on the line. Zeta's symmetries mirror the zeros across this line, so a zero off it would come with a partner. No such pair has ever been found.

Riemann's private notes show he computed the first few zeros by hand. In his paper, he wrote that it's very likely all of them lie on this line, and that after a few quick attempts, he had put aside the search for a proof. That's the Riemann hypothesis: every nontrivial zero has real part one half. David Hilbert put it on his famous list of problems in nineteen hundred, and in two thousand it became a Millennium Prize Problem.

How can anyone know a zero is exactly on the line, not just very near it? Along the line, zeta can be turned into a real-valued wave, Hardy's Z function, and every time it crosses zero, there's a zero exactly on the line. If the crossings match a separate count of all the zeros below some height, every one of them is on the line.

Alan Turing ran some of the first checks like this on an electronic computer, in the early nineteen fifties. Since then it's been done for the first ten trillion zeros, and every one is on the line.

# CH4 HOW THE ZEROS BUILD THE PRIMES

Now the waves from the opening make sense. In the same paper, Riemann wrote down an exact formula for the prime-counting staircase: a smooth part, plus one wave for each zero.

A zero's height sets how fast its wave wiggles. Its real part sets how fast the wave grows. For a zero with real part one half, the wave's size grows roughly like the square root of x.

The fact the prime number theorem needed was that no zero has real part one. That's enough to make all the waves together grow more slowly than the count itself. The hypothesis asks for much more.

Suppose one zero sat off the line, at real part point eight. Its wave would grow like x to the point eight, faster than all the others, and over long ranges it would pull the staircase far away from the curve.

If every zero is on the line, that never happens, and the gap stays below roughly the square root of x times its logarithm. In nineteen oh one, Helge von Koch showed the reverse too: if the gap always stays that small, the hypothesis is true. And since zeros come in mirrored pairs, one half is the smallest the largest real part could be. So the hypothesis says the primes stay as close to the curve as they possibly can.

# CH5 WHY IT IS SO HARD

If ten trillion zeros are on the line, why isn't that a proof? Because there are infinitely many, and in number theory a pattern can hold for a very long time and then fail. The prime count stays below the logarithmic integral for every number anyone has checked, but in nineteen fourteen John Littlewood proved that the order flips infinitely often. The first flip lies somewhere past ten quintillion, possibly as far out as a number with over three hundred digits.

The zeros also sit where the original sum stops working. Where the sum works, the product over primes shows at once that zeta can't be zero. Inside the strip, that product no longer converges.

And the zeros come close to breaking the rule. In nineteen fifty-six, Derrick Lehmer found two zeros near height seven thousand and five, about twenty-four times closer together than usual. Between them, the Z wave climbs only four thousandths above zero before turning back. If it had turned back just short of zero, the two zeros would have had to leave the line as a mirror pair. In twenty eighteen, Brad Rodgers and Terence Tao proved a precise version of this idea: if the hypothesis is true, it's true with no room to spare.

Progress has also been slow. One measure is the fraction of zeros proven to lie on the line. Hardy showed in nineteen fourteen that infinitely many do, and from nineteen forty-two to twenty twenty, the proven fraction crept from a sliver to five twelfths, just under forty-two percent. Even a hundred percent wouldn't be enough: in an infinite set, a hundred percent can still leave out infinitely many.

Finally, a version of the hypothesis has been proved, and it shows what's missing. Take an equation like this one and count its solutions in clock arithmetic, where numbers wrap around at a prime p. The count never strays from p by more than twice the square root of p, the same square-root behavior the hypothesis predicts for the primes. André Weil proved bounds like this for all curves in the nineteen forties, and Pierre Deligne a far more general version in nineteen seventy-four. Their proofs use geometry with no known counterpart for the whole numbers.

# CH6 WHAT SOLVING IT WOULD MEAN

Solving it means one of two things: a proof that covers every zero at once, including the ones no computer will ever reach, or a single zero off the line, which would disprove it.

A proof would make the gap bound a theorem, and turn a great many results that begin with "assume the Riemann hypothesis" into unconditional ones, about the gaps between primes and much else. Some results need a stronger version, the generalized Riemann hypothesis, which makes the same claim for a family of related functions. A proof wouldn't break encryption, though. Knowing how the primes are spread out doesn't tell you how to factor a large number.

Some ideas go further. In the nineteen seventies, Hugh Montgomery and Freeman Dyson noticed that the gaps between zeros seem to follow the same statistics as energy levels in heavy atomic nuclei. Some see a hint of a hidden physical system. That's speculation, and a proof wouldn't settle it.

# CH7 BACK TO NOVEMBER

Back to this year. In August, Anthropic announced that an unreleased research version of Claude had found a proof raising the proven fraction from five twelfths to two thirds. Alpöge and his Anthropic colleague Ralph Furman checked it and wrote it up. Brian Conrey and Dan Goldston, experts on exactly this problem, examined it, and it was checked in Lean. A few weeks later, Youness Lamzouri posted a simpler, independent proof. Anthropic said it didn't expect these methods to lead to the full hypothesis.

Then came November. Here's what Lean actually checks. Definitions, statements and proofs are all written as code, and a small program called the kernel checks that each step follows from earlier ones, back to a few basic axioms. If the kernel accepts a proof, a broken step is very unlikely.

What the kernel can't tell you is whether the final statement means what you think it means. Kevin Buzzard, a mathematician at Imperial College London, says it's the first question to ask of any Lean proof. Here is the main statement, and four more theorems extend it to a family called Dirichlet L-functions. The main one uses the definition of zeta from Mathlib, a large shared library of Lean mathematics, so part of the job is confirming the definitions.

One test avoids that definition. In nineteen eighty-four, Guy Robin showed the hypothesis is equivalent to an inequality about sums of divisors, for every number past five thousand and forty, with no zeta in it at all. The proof has been joined to a separate formalization of Robin's result, and that combination is being checked too.

So far, Andrew Sutherland at MIT has rebuilt all hundred and seventy-five thousand files and run them through several independent checkers. Every check that has finished has accepted the proof, and he told Scientific American that the chance anything is fishy is approximately zero. A few of the slowest were still running when I recorded this.

There's no human-readable paper yet. Alpöge writes that the argument is very long at the moment, and that he's presenting it before having mastered much of the mathematics around it. By his account, he steered the search, and Claude far outpaced him near the finish line.

He calls the argument a descendant of a method Sergei Stepanov found in the late nineteen sixties for the clock-arithmetic version. That method needs functions that vanish many times over at each solution, which takes something like derivatives, and whole numbers have no obvious derivative. The new argument, he writes, finds a stand-in.

Officially, the problem is still open. The Clay Institute considers a solution only after it has been published, has stood for two years, and has been broadly accepted. Until then, this is a serious claim under examination.

So we have several different kinds of results. Ten trillion zeros on the line is evidence. Two thirds is a theorem, checked by people and by machine. The full hypothesis has a proposed proof, with machine checks partly complete. The last stage, people understanding why it works, has barely begun.

# OUTRO

Let's go back to the staircase. Riemann found that the primes, irregular as they look, are built exactly from waves, one for each zero of a single function. If every zero is on the critical line, every wave grows as slowly as it can, and the primes never stray far from the smooth curve.

In eighteen fifty-nine, Riemann put the search for a proof aside. If this claim holds, that search ended a hundred and sixty-seven years later, with a proof that mathematicians are only beginning to read.
