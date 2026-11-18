# Calculus Is Secretly Linear Algebra: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Spine: differentiation is a linear map on a space of functions, so most of calculus is linear algebra plus a limit.
     Cast (all verified with sympy/numpy, scratchpad verify.py, 2026-11-17; see research.md §6):
       cold open     f = e^x sin x;  d^100/dx^100 f = -2^50 e^x sin x
                     basis (e^x cos x, e^x sin x): D = [[1,1],[-1,1]] = root2 * (clockwise 45 deg turn), det 2, eig 1 +- i
                     100 steps: -4500 deg = 12.5 turns -> points backwards, length (root2)^100 = 2^50
       sampled D     forward difference (f(x+h) - f(x)) / h: -1 on the diagonal, +1 just right of it, / h
                     shown 8 x 8, then 1000 x 1000 heat map; D * samples(sin) ~ samples(cos)
       poly D        basis 1, x, x^2, x^3: [[0,1,0,0],[0,0,2,0],[0,0,0,3],[0,0,0,0]], rank 3, det 0, D^4 = 0
                     x^2 + 5 and x^2 - 2 both -> 2x
       rotation      basis (cos, sin): D = [[0,1],[-1,0]] (clockwise quarter turn), D^2 = -I, D^4 = I
       integral      D^-1 (0,1) = (-1/2, 1/2):  integral e^x sin x dx = 1/2 e^x (sin x - cos x) + C
       eigen         D e^(lambda x) = lambda e^(lambda x);  e^(2x) doubled, e^(-x) flipped
       spring        y'' + y = 0  ->  y = C1 cos x + C2 sin x  (null space of D^2 + 1, a plane)
       string        200 interior points, L = 1, (1, -2, 1) / dx^2, ends pinned:
                     eigenvalues -9.869, -39.475, -88.810 vs exact -(k pi)^2 = -9.870, -39.478, -88.826; modes = sin(k pi x)
       shift         e^(hD) p(x) = p(x + h) (exact for polynomials); fails for e^(-1/x^2) at 0
     Generate: uv run aion voice 010-calculus-is-linear-algebra --dry-run   then   uv run aion voice 010-calculus-is-linear-algebra -->

# INTRO

Here is a function. e to the x, times sine x.

Its first derivative takes one use of the product rule. The second takes two. So what is its hundredth derivative?

Grinding through the product rule a hundred times would fill pages. But the answer fits on one line. It's the same function, flipped upside down, and scaled up by two to the fiftieth.

And you can see why. Picture a flat plane. One direction means e to the x cosine x. The other means e to the x sine x. Our function is an arrow in that plane. Take its derivative, and the arrow turns by an eighth of a turn, and stretches by the square root of two. Every derivative does exactly the same thing.

A hundred eighth turns is twelve and a half full turns, so the arrow ends up pointing straight backwards. And it has been stretched by root two, a hundred times over. That's two to the fiftieth.

An operation that turns arrows and stretches them. That's not what calculus is supposed to look like. That's what a matrix does.

So here is the claim this video is going to earn. Taking a derivative is a linear map, the same kind of move a matrix makes. Once you see it that way, a surprising amount of calculus turns out to be linear algebra, plus one extra idea: the limit.

The plus C you were told never to forget is a null space. Sine and cosine cycle forever because the derivative is a rotation. e to the x is special because it is an eigenvector. And the notes a guitar string can play fall out of a matrix.

We'll start by turning a curve into a list of numbers, and end by listening to that string.

> [pause 3]

# CHAPTER 1: A function is a very long vector

Take a curve, say a sine wave. Forget the smooth line, and keep only its height at eight evenly spaced points. Eight numbers. Stack them in a column, and you have a vector in eight dimensions.

Sample it at fifty points, and the vector has fifty entries. At a thousand, the column is so tall that the dots blur back into a curve. That's how a computer stores a function: as a very long vector.

And functions behave like vectors. Add two curves, and you add their heights point by point, exactly the way you add two columns. Scale a curve by three, and every entry scales by three.

Now watch what the derivative does with that. The slope of a sum is the sum of the slopes. And the slope of three times a curve is three times the slope.

Those two rules are the entire definition of a linear map. They are exactly the rules every matrix obeys. So if functions are vectors, and the derivative respects adding and scaling, the derivative should be a matrix. Let's build it.

# CHAPTER 2: The derivative, as a matrix

The slope at a point is roughly the rise to the next point, divided by the step. Next height, minus this height, over the gap between them.

Now write that down for every point at once. Each row of the matrix looks at two neighbors: minus one on the diagonal, plus one just to its right, and zeros everywhere else. Then divide everything by the step.

Zoom out to a thousand points, and the matrix has a million entries. Almost all of them are zero. What's left is one thin, bright band down the diagonal.

Now multiply. Feed it the column for sine x, and a new column comes out. Plot it back as a curve, and it's cosine x. The computer just took a derivative, and all it did was multiply a matrix by a vector. Physics simulations and weather models do calculus in exactly this spirit, with enormous, mostly empty matrices.

That matrix is an approximation, and it gets better as the points get closer. But for some functions you don't need an approximation at all. Take the polynomials up to x cubed. Every one of them is a mix of four building blocks: one, x, x squared, and x cubed. So a cubic is really just four numbers.

The derivative sends one to zero, x to one, x squared to two x, and x cubed to three x squared. Write where each building block lands as a column, and you get an exact four by four matrix, with one, two, three sitting just above the diagonal. Multiply it by the four numbers of any cubic, and out come the four numbers of its derivative. No limits. No approximation. Calculus, done entirely by a matrix.

# CHAPTER 3: Why plus C exists

Look at the first column of this matrix. It's all zeros. Feed it a constant, and it returns nothing at all.

In the language of matrices, a whole direction gets crushed to zero. Every constant function, five, minus two, a million, lands on the same point. That direction is called the null space.

And a matrix that crushes a direction can never be undone. Its determinant is zero. Once two inputs land on the same output, there is no way to tell which one you started from. x squared plus five, and x squared minus two, both have derivative two x.

So think about what integration really asks. Find a function whose derivative is this one. That is solving a matrix equation: D times F equals f. And linear algebra already knows what the answer to a crushed system looks like. One particular solution, plus anything at all from the null space.

Here, the null space is the constants. That's the plus C. It isn't a rule to memorize, or a way to lose marks on an exam. It's the null space of the derivative, showing up exactly where linear algebra says it must.

This matrix has one more odd habit. Each time you apply it, every coefficient slides one slot up, and the top one falls off the end. Apply it four times, and every cubic is gone. Differentiate a polynomial enough times, and nothing is left.

# CHAPTER 4: The derivative is a rotation

Let's change the building blocks. Instead of powers of x, take just two functions, cosine and sine. Every mix of them, like two cosine x plus sine x, is an arrow in a plane, with cosine along one axis and sine along the other.

Cosine's derivative is minus sine. Sine's derivative is cosine. So where does the cosine arrow go when you differentiate it? Pause and predict.

> [pause 2.5]

Cosine, pointing right, swings down to point at minus sine. Sine, pointing up, swings right to point at cosine. Both arrows turn a quarter turn, the same way. On this plane, the derivative is a rotation.

Now the old facts read differently. Differentiate twice, and every arrow has turned halfway around and points backwards. That's why the second derivative of sine is minus sine. Four derivatives make a full turn and bring you home, which is why sine, cosine, minus sine, minus cosine cycle forever. It's the same quarter turn that makes i squared equal minus one.

And this is the secret behind the opening. Swap in e to the x cosine x, and e to the x sine x. Now each derivative turns by an eighth of a turn, and stretches by root two. Unlike the polynomial matrix, this one crushes nothing. Its determinant is two, so it can be undone.

That gives a trick you might not have seen. The integral of e to the x sine x usually takes integration by parts, twice, and a bit of algebra. Here, it is just the inverse matrix: turn back by an eighth of a turn, and shrink by root two. Out comes one half e to the x, times sine x minus cosine x. Differentiate that, and you get e to the x sine x right back. Add the plus C, and you're done.

# CHAPTER 5: The eigenvectors of the derivative

In linear algebra, the most revealing question you can ask a matrix is this. Which directions does it leave alone? Which vectors does it only stretch, and never turn?

So ask the derivative. Which function comes back from differentiation as just a multiple of itself? Pause and predict.

> [pause 2.5]

Not sine. The derivative turns it into cosine. Not x squared. It loses a power. The answer is e to the x. Its derivative is itself. And e to the two x comes back doubled. e to the minus x comes back flipped. Every function e to the lambda x is an eigenvector of the derivative, with eigenvalue lambda.

That's the deepest reason e shows up everywhere. Whenever something changes at a rate proportional to itself, money, populations, radioactive atoms, it is asking for an eigenvector of the derivative. And only one family of functions answers.

Differential equations become linear algebra too. Take y double prime plus y equals zero, the equation of a spring. Read it as an operator: D squared plus one sends y to zero. So its solutions are exactly the null space of that operator. A null space is always flat, and this one is a plane: every mix of cosine and sine. Two numbers pick out one solution, and that's why a spring needs two starting conditions, where it begins and how fast it's moving.

It also explains a trick from earlier on this channel. The Fourier and Laplace transforms rewrite a function as a mix of exponentials. In that basis, the derivative's own eigenbasis, differentiating stops being calculus. Each piece just gets multiplied by its own number. That is what turning calculus into algebra really means. It's diagonalizing the derivative.

# CHAPTER 6: A guitar string is an eigenvector problem

Let's put the matrix to work on something you can hear.

A guitar string is pinned at both ends. Where it bends more sharply, it gets pulled back harder. And how sharply a curve bends is its second derivative.

So build the second derivative as a matrix. Two hundred points along the string. Each row takes a point's two neighbors, and subtracts twice the point itself. One, minus two, one. Pin both ends at zero.

Now ask the computer the question linear algebra loves most. What are this matrix's eigenvectors? Which shapes does it only scale?

Out come these. A single arch. Two arches. Three. Smooth sine waves, each fitting a whole number of half waves between the pins. Nobody typed in a sine. They fell out of a grid of ones and minus twos. And their eigenvalues match the exact answer, minus k pi squared, to three digits.

Each eigenvector is a way the string can vibrate in place, keeping its shape and only growing and shrinking. Its eigenvalue sets how fast. The second shape vibrates twice as fast as the first, one octave up. The third, three times as fast.

Pluck the string, and its shape is a mix of these eigenvectors, each ringing at its own speed. That mix is the sound of the note. The overtones you hear are the eigenvectors of a matrix.

# CHAPTER 7: The exponential of the derivative

One last move. For numbers, e to the x is one, plus x, plus x squared over two, and so on. That same series works for matrices. So what happens if you put the derivative itself in the exponent?

e to the h D is one, plus h times the derivative, plus h squared over two times the second derivative, and on and on. Apply it to a function, and you get f, plus h f prime, plus h squared over two f double prime. That's the Taylor series. And the Taylor series adds up to f, evaluated at x plus h.

So the exponential of the derivative is a shift. It slides the whole graph sideways by h. Tiny changes, added up, become one big move.

One honest asterisk. This only works for functions whose Taylor series actually adds back up to them, like polynomials, e to the x, and sine. There are smooth functions where it fails. e to the minus one over x squared is perfectly smooth, yet every one of its derivatives at zero is zero, so its Taylor series there is just zero.

# OUTRO: Where the analogy breaks

So, is calculus secretly linear algebra? Mostly, yes. But the honest answer has a second half.

A real function has a value at every point, not just a thousand. It's a vector with infinitely many entries, and infinity changes the rules. The derivative is no longer a finite matrix, and it has no determinant. On the space of all smooth functions, every number is an eigenvalue, because e to the lambda x works for any lambda. And getting from a thousand points to every point takes a limit. That's the part linear algebra can't do for you.

Making all of this rigorous is a field of its own, called functional analysis. It's the mathematics underneath quantum mechanics, where every quantity you can measure is an operator, just like the derivative.

But the picture holds. Plus C is a null space. Sine and cosine are a rotation. e to the x is an eigenvector. A guitar string is an eigenvector problem. Calculus is linear algebra, plus a limit.
