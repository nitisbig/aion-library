# Why e^(iπ) = −1, Explained Visually: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Spine: e is growth (velocity = position), i is a quarter turn, pi is a distance.
     Running numbers: (1+1/n)^n = 2, 2.25, 2.4414, 2.6130, 2.7146 -> e = 2.71828.
     (1+i*pi/n)^n: n=1 -> 1+3.14i, n=2 -> -1.47+3.14i, n -> infinity -> -1.
     Series |terms| pi^n/n!: 1, 3.14, 4.93, 5.17, 4.06, 2.55, 1.34, 0.60 ...
     Generate: uv run aion voice 007-euler-identity --dry-run   then   uv run aion voice 007-euler-identity -->

# INTRO

e to the i pi equals negative one.

You have probably seen it written another way. e to the i pi, plus one, equals zero. Five of the most important numbers in mathematics, in one short line. People call it the most beautiful equation ever written.

But read it slowly, and it stops making sense. e is about two point seven. Raising a number to a power means multiplying it by itself. So what would it mean to multiply e by itself i pi times? An imaginary number of times?

You might expect the answer to be a clever trick with symbols. It is not. It is a picture.

e is a story about growth. i is a story about turning. And pi is a distance. Put them together, and you get a point walking around a circle, until it lands exactly on negative one.

By the end of this video, you will not need to memorize this equation. You will see it.

We will start with one dollar in a bank, and end with a half turn of the whole plane.

> [pause 3]

# CHAPTER 1: What e really is

First, we need to see e for what it really is. Not a decimal. A kind of growth.

Imagine a bank that pays one hundred percent interest per year. Put in one dollar, and after a year, you have two.

Now a better bank pays half that interest every six months. After six months, you have one dollar fifty. Then that whole amount earns interest. You end the year with two twenty five.

Pay it four times a year, and you get about two forty four. Every month, two sixty one. Every single day, two seventy one.

Keep splitting the year finer and finer, and the total does not run off to infinity. It settles on one number. Two point seven one eight. That number is e.

Here is what makes it special. When interest is paid continuously, your money grows at a rate equal to the money you have. Hold one dollar, and you gain one dollar per year. Hold two, and you gain two.

Draw it as a graph, and you get e to the t. At every point, the slope of the curve equals its height.

Or picture it as motion. A point on a line, whose velocity is always equal to its position. The farther it gets, the faster it runs.

Hold on to that sentence. Velocity equals position. It is the heart of e. And we are about to change just one word of it.

# CHAPTER 2: What i really does

Now for i. Forget the idea that i is a number that cannot exist. Instead, think of numbers as actions.

Lay every number out on a line. Multiplying by two is an action. It stretches the line, pushing everything twice as far from zero. Multiplying by one half squeezes it.

And multiplying by negative one? Three goes to negative three. Negative two goes to two. Every number swings to the other side of zero. It is a half turn.

Remember that. Negative one is a half turn. It is going to matter.

Now here is the question that i answers. What action, done twice, gives a half turn?

Not a stretch. Two stretches only stretch further. But a quarter turn, done twice, is a half turn.

So let the line become a plane, where numbers can point in any direction. i is the quarter turn. One goes to i, straight up. i goes to negative one. Negative one goes down to negative i, and then back to one.

i times i is negative one. Not as a rule to memorize, but because two quarter turns make a half turn.

And multiplying by i turns the whole plane. Every arrow, rotated ninety degrees.

# CHAPTER 3: Growth turned sideways

Now we can read e to the i t.

Remember the rule for e to the t. Velocity equals position. For e to the i t, the rule picks up a single i. Velocity equals i times position.

And we know what i does. It turns an arrow by a quarter turn. So the velocity is always the position, turned ninety degrees.

Let us watch. Start at one, on the real line. The position arrow points right. So the velocity points straight up.

The point moves up. As it moves, its position arrow tilts, so the velocity tilts too. Always at a right angle. Always pushing sideways, never outward.

A push that is always sideways can never bring you closer, or carry you farther away. So the point stays exactly one unit from the center. It traces a circle.

And how fast does it go? The velocity has the same length as the position. One. So the point walks around the circle at one unit of distance, per unit of time.

Let the whole plane follow the same rule. Ordinary growth sends every point flying outward. Turn the growth part of the way, and the points spiral. Turn it all the way, to i, and every point circles forever.

So e to the i t has a simple meaning. Walk along the unit circle, a distance t.

Now, pause and predict. We start at one. How far do we have to walk to reach negative one?

> [pause 2]

Halfway around a circle of radius one. The full way around is two pi. So halfway, is pi.

After walking a distance pi, the point lands on negative one. e to the i pi equals negative one. A half turn. Which is exactly what we said negative one is.

That is the picture. But a picture can fool you. So let us check it, twice, using nothing but arithmetic.

# CHAPTER 4: Compounding a turn

Go back to the bank. e came from compounding. One plus one over n, raised to the n. So e to the i pi should come from compounding i pi. One plus i pi over n, raised to the n.

Start crude. Let n be one. One plus i pi. That is a point far up and to the right. Nowhere near negative one.

Let n be two. Multiplying by one plus i pi over two turns the plane a little, and stretches it a little. Do that twice, and we land up here.

Four steps. Each one a smaller turn, and a smaller stretch. The path begins to bend.

Eight steps. Sixteen. A hundred. The stretches shrink toward nothing. The turns add up closer and closer to a half turn. And the path hugs the unit circle, sliding into its final spot.

Negative one.

Compounding a rate of growth gives e. Compounding a rate of turning gives a walk around the circle.

# CHAPTER 5: The infinite sum

There is a second way to compute e to the x. An infinite sum. One, plus x, plus x squared over two, plus x cubed over six, and so on. Each term is x to the n, over n factorial.

Plug in i pi, and treat each term as an arrow, laid tip to tail.

The first term is one. A step to the right.

The second is i pi. The i turns it a quarter turn, so we step straight up, a distance pi.

The third has i squared, which turns twice. So it points left. Pi squared over two. About four point nine.

The next turns again, and points down. Then right. Then up. Each new step turns one more quarter.

At first, the steps grow, and the path swings far away. But the factorials grow faster than any power of pi. Soon the steps shrink, and the path spirals inward, closer and closer to one point.

Negative one, again.

And look at the horizontal steps. Together, they add up to the cosine of pi. The vertical steps add up to the sine of pi. Which is zero.

# CHAPTER 6: The whole circle

Pi was never special. Walk any distance theta, and you land somewhere on the circle.

How far right are you? That is the cosine of theta. How far up? The sine of theta. So e to the i theta equals cosine theta, plus i times sine theta. This is Euler's formula.

Now let time run, and spread the walk out along a third direction. The point traces a spiral, a helix. Look from the side, and you see a sine wave. Look from below, a cosine wave. Look head on, and it collapses back into the circle.

This is why circles hide inside so much of physics and engineering. Springs, alternating current, sound. Wherever something oscillates, there is often a turning arrow underneath.

Now try a few special values. Theta equals pi over two, a quarter of the way around, and you land on i. Theta equals pi, halfway, and you land on negative one. Theta equals two pi, all the way around, and you are back at one.

And multiplying by e to the i theta does not just move one point. It turns the entire plane by theta. e to the i pi turns everything by half a turn.

Move the one across, and you get the famous form. e to the i pi, plus one, equals zero.

# OUTRO

So let us read the equation one last time.

e is growth whose rate equals its size. i is a quarter turn. Put them together, and the growth turns sideways. Instead of running away, the point walks around a circle, at speed one.

Pi is the distance. Walk pi, and you have gone halfway around. And a half turn is exactly what negative one means.

The bank, the infinite sum, and the picture all agree.

e to the i pi equals negative one. Not a coincidence of symbols. A half turn.

If you want to see what happens when many of these turning arrows are added together, that is the Fourier series, and that is where we are going next.
