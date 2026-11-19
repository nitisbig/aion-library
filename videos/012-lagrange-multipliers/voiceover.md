# What Lagrange Multipliers Actually Are: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Voice: warm, curious, short sentences, concrete images before symbols. No equations on screen until ch1.
     Spine: at the best point, the only way left to improve is the way you are forbidden to go,
     and lambda is what that forbidden direction is worth.
     Promise made in the intro, paid in the outro: on Dido's beach, lambda is a length you can measure.
     Every number here is computed in verify.py (uv run python videos/012-lagrange-multipliers/verify.py).
     Sources for the history are listed in storyboard.md.
     Generate: uv run aion voice 012-lagrange-multipliers --dry-run   then   uv run aion voice 012-lagrange-multipliers -->

# INTRO

Nearly three thousand years ago, the story goes, a queen in exile named Dido landed on the coast of North Africa. She asked the local king for land to build a city. He offered her a joke: as much ground as she could surround with the hide of a single ox.

So she cut the hide into strips, thin as thread, and tied them into one enormous rope. Then she walked to the shore, because the sea would guard one side for free. Only one question was left. What shape should the rope make?

That is a very human question. Not, what is the best thing in the world? But, what is the best we can do with what we have? A fixed length of rope. A fixed budget. A bridge that must stand, using as little steel as possible.

Around sixteen thirty-six, Pierre de Fermat found a rule for the easier kind of problem, the kind where nothing holds you back. At the very top of a hill, the ground goes flat. Find the flat places, and you have found your candidates.

But limits break that rule. Imagine hiking a trail that loops around a mountain. The summit is right there, up the slope, but you have to stay on the path. So where on this path are you highest? Stand at that spot, and the ground is not flat at all. The mountain still rises beside you. You just can't go that way.

The person who cracked this was a young man from Turin. In seventeen fifty-five, at just nineteen, Joseph-Louis Lagrange wrote to Leonhard Euler, the leading mathematician of the age, with a new method for problems very much like Dido's. Thirty-three years later, in his masterpiece on mechanics, he worked out how machines balance when their parts hold each other back. And to each of those restrictions, he gave one extra unknown number.

We call those numbers Lagrange multipliers, and today they are everywhere. In the design of wings and bridges. In how economists value a budget. In how a network shares out its power, how machines learn to draw boundaries, and even in the laws of heat.

Lagrange was so confident in his algebra that the preface of that book makes a striking promise: no figures will be found in this book. Not one picture. Which is a pity, because underneath his algebra is one of the most beautiful pictures in mathematics.

So let's draw it. We'll see what happens at the highest point of that trail, why one arrow is forced to line up with another, how that picture becomes a method, and how the method solves real problems. And by the end, that mysterious extra number will turn into something surprisingly concrete. On Dido's beach, you can measure it with a stick.

# CH1 FREE AND CONSTRAINED

Let's turn the mountain into mathematics. Give every point on the map a height, f of x and y. This is the quantity we want to make as large as possible. We call it the objective.

With no limits, the search is easy to describe. Stand anywhere and ask which way is steepest uphill. That direction, with a length that says how steep, is the gradient of f. Follow it and you climb. You stop only when the arrow shrinks to nothing, when the gradient is zero. That is Fermat's flat ground.

Now add the trail. A trail is a rule about where you are allowed to be, and we can write that rule as an equation: some function g of x and y must equal a constant, c. Points that satisfy the rule are on the path. Everything else is forbidden.

Look at what that does. You had two directions of freedom, and now you have one: forward or back. Sometimes you can write the path as a formula and reduce everything to a single variable. But real constraints are tangled, and that substitution quickly becomes ugly or impossible. We want a way to find the answer without unrolling the trail.

# CH2 CONTOURS

So let's look at the mountain the way a hiker does: from above, on a map. Slice it at equal heights, and each slice leaves a contour line, a level curve of f. Walk along one contour and your height never changes.

That tells us something about the gradient. Moving along a contour gains nothing, so the uphill arrow has no part pointing along it. The gradient is always perpendicular to the contour beneath your feet.

Now walk the trail and watch the contours. Here, the trail cuts across them, one after another, and every crossing means you are climbing. Keep going. The crossings spread out. The climb is getting gentler. And then, at one special point, the trail stops crossing. It touches a contour, runs alongside it for an instant, and falls away.

That is the top, and it has to look like this. If the trail crossed the contour there, one direction would carry you higher, and you wouldn't be at the top.

Here is another way to see it. Start with a high contour, a small loop near the summit that doesn't reach the trail at all. Now lower the height. The loop swells outward until, at one moment, it first touches the path. That first touch is the highest point you can reach.

And here is the quiet insight. The trail is itself a contour. It is one level curve of g. So the whole problem is two families of curves, and the answer is where one curve from each family just kiss.

# CH3 THE GRADIENTS ALIGN

Two curves that kiss share a tangent line. Each curve's gradient is perpendicular to its own contour. So at that point, both gradients are perpendicular to the same line, and in the plane, that forces them to point along one common direction.

One arrow must be a multiple of the other. The gradient of f equals lambda times the gradient of g.

That Greek letter is the Lagrange multiplier. For now, it is just a stretch factor: how many times longer one arrow is than the other.

Let's feel why this has to be true. Walk the trail carrying the uphill arrow, and split it into two parts: one along the trail, and one straight across it. The part across the trail is useless, because it points somewhere you can't go. The part along the trail tells you to keep walking. As long as that part exists, you can still do better. You arrive at the best point exactly when it vanishes, and all that remains of the gradient points straight across the path.

Now the proof, in three lines. Describe your walk as a path r of t, with velocity r prime. You stay on the trail, so g never changes, and the chain rule says the gradient of g dot r prime is zero. At the top, your height has stopped changing, so the gradient of f dot r prime is zero too. Both gradients are perpendicular to the same velocity, so as long as the gradient of g isn't zero, one is a multiple of the other.

Count what we have. Two equations from the arrows, one from the constraint. Three unknowns: x, y and lambda. The picture has become algebra.

# CH4 THE LAGRANGIAN

Lagrange packed all of this into a single function. Take the objective and subtract lambda times the constraint: L equals f minus lambda times g minus c.

Set its derivatives with respect to x and y to zero, and you get the arrow equations. Set its derivative with respect to lambda to zero, and out comes the constraint itself. A restricted problem has become an unrestricted one, with one more variable. Fermat's flat ground has returned, in a higher dimension.

But be careful. That flat point is not a peak of L. Take the smallest possible example: maximize minus x squared, with x forced to equal one. Plot L over x and lambda, and the solution sits on a saddle, rising one way and falling the other. You can't simply climb to it. You have to solve for it.

# CH5 WORKED EXAMPLES

Let's put this to work on Dido's beach. Take forty meters of rope, a straight shore, and for now, a rectangular plot. Two sides of length x leave the shore, and one side of length y runs along it. We want to maximize the area, x y, while two x plus y equals forty.

The gradient of the area is y, x. The gradient of the rope is two, one. So y equals two lambda, and x equals lambda. Put those into the constraint, and four lambda equals forty. Lambda is ten. The plot is ten meters deep, twenty wide, and encloses two hundred square meters. Hold on to that ten. We will need it.

Next, a case where the picture earns its keep. Find the extremes of x squared y on the circle x squared plus y squared equals three. The arrow equations are two x y equals two lambda x, and x squared equals two lambda y.

The first one splits in two. Either x is zero, or lambda equals y. If lambda equals y, then x squared is two y squared, so y is plus or minus one, and x is plus or minus root two. If x is zero, then y is plus or minus root three, and lambda is zero.

That is six candidates, and six places where a contour kisses the circle. Walk around, and f reads two, zero, two, minus two, zero, minus two. The maximum is two. The minimum is minus two. The two zeros are only local turning points. The equations never tell you which is which. They hand you every tangency, and you compare.

# CH6 HIGHER DIMENSIONS

Nothing here depends on living on a flat map. In three dimensions, level curves become level surfaces. Suppose we want the point on the plane x plus two y plus two z equals nine that is closest to the origin. The level surfaces of distance are spheres. Inflate a sphere until it just touches the plane. At that touch, the two surfaces share a tangent plane, their gradients align, and the equation is exactly the same. The point is one, two, two, at a distance of three.

Now add a second constraint. A cylinder and a tilted plane cut out an ellipse, and we want its highest point. We are back on a one-dimensional trail, but now it is floating in space, and at every point a whole plane of directions is perpendicular to it.

So the gradient of f no longer has to line up with a single arrow. It only has to lie in the plane spanned by the two constraint gradients. The gradient of f equals lambda times the gradient of g, plus mu times the gradient of h. Every constraint gets its own multiplier.

# CH7 WHAT LAMBDA IS

So what is this number, really? Go back to the rope. Lambda was ten. Now add one more meter of rope, and solve again. The best area climbs from two hundred to about two hundred and ten. Ten more square meters, for one more meter of rope.

That is no coincidence. As the constraint loosens, the best point slides, and the chain rule shows that the best value changes at exactly rate lambda. The multiplier is the exchange rate between the constraint and the objective.

Economists call it a shadow price. It is what one more unit of budget, or steel, or machine time would be worth to you, even though nobody ever posted that price.

In physics, the same number is a force. A bead rests at the bottom of a hoop. Gravity pulls it down and the hoop pushes back. Minimize the bead's energy on the hoop, and lambda times the gradient of g is exactly that push. A constraint, physically, is something pushing back. That is the world where Lagrange first found these numbers.

And then the deepest example. Take a box of gas, with its molecules sharing a fixed amount of energy. Of all the ways to share it, the overwhelmingly likely one has the highest entropy. So maximize entropy, with the total probability fixed and the average energy fixed. Two constraints, two multipliers. Out falls Boltzmann's law: the chance of a state with energy E is proportional to e to the minus beta E.

Beta is the multiplier on energy. It is the price of energy, measured in entropy. And physicists have a name for one over that price: temperature.

# CH8 THE FINE PRINT

The method does come with fine print. We assumed the gradient of g isn't zero. The curve y squared equals x cubed has a sharp cusp at the origin, and the smallest x on that curve is right at the cusp. But there the gradient of g vanishes, and no multiple of zero can equal the gradient of f. The equations have no solution at all, and they miss the answer completely. So always check the sharp points by hand.

Also, tangency only makes a point a candidate. And if the trail runs off to infinity, there may be no best point to find.

Real limits are often inequalities too: spend at most this much. William Karush worked that out in his master's thesis in nineteen thirty-nine, and Harold Kuhn and Albert Tucker, unaware of his work, reached the same result in nineteen fifty-one. The idea is lovely. A limit you aren't pressing against has a price of zero.

# OUTRO

Let's go back to the beach, and let the rope take any shape it likes. Apply the same idea along the whole rope, with one multiplier for the entire curve, and the answer says the rope must bend by the same amount everywhere. That is a circle. Against a straight shore, a semicircle.

Forty meters of rope now encloses about two hundred and fifty-five square meters, more than a quarter better than the rectangle.

And the multiplier? It is the radius. Each extra meter of rope buys as many square meters as the radius is long, about twelve point seven. Lay a stick from the center to the rope, and you are holding lambda in your hands.

At the best point, the only way left to improve is the way you are forbidden to go. Lagrange's number tells you exactly what that forbidden direction is worth.
