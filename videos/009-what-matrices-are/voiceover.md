# What Matrices Actually Are: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Spine: a matrix looks like a table, but it is a move you make to space; its columns record where the axes land.
     Cast (all verified with sympy/numpy, scratch check.py, 2026-11-16):
       hook box      [[2,1,0],[0,1,1],[1,0,1]]      det 3, columns (2,0,1) (1,1,0) (0,1,1)
       arrow         (2, 1) = 2 i-hat + 1 j-hat
       quarter turn  [[0,-1],[1,0]]                  i-hat -> up, j-hat -> left (counterclockwise)
       shear         [[1,1],[0,1]];  rotate after shear R Sh = [[0,-1],[1,1]];  Sh R = [[1,-1],[1,0]] (different)
       die           opposite faces sum to 7; +x 3, +y 2, +z 1. Quarter turns x-then-y: 4 on top; y-then-x: 2 on top.
                     y-then-x = [[0,0,1],[1,0,0],[0,1,0]]: a 120 degree turn about (1,1,1), eigenvalue 1 (Ch6 payoff)
       hero A        [[3,1],[2,2]]   det 4   lambda 4 on (1,1), lambda 1 on (1,-2)   inverse (1/4)[[2,-1],[-2,3]]
                     SVD: rotate -30.1 deg, stretch 4.131 and 0.968, rotate +41.4 deg
       collapse      [[2,1],[2,1]]   det 0   null space along (1,-2), column space along (1,1)
       2D solve      A x = (5,6)  ->  x = (1,2)
       3 equations   x + y + z = 4,  x - y + 2z = 1,  2x + y - z = 3   det 7, solution (1,2,1)
                     singular variant row3 = row1 + row2: rhs 5 -> a line of solutions, rhs 6 -> none
       spirals       one matrix (no bend): 67% at best; matrices + tanh bends 2-16-16-1: 100%
       PageRank      7 pages, damping 0.85: C .368, A .204, B .178, G .097, F .063, E .048, D .042;
                     B and D each have one incoming link, B's comes from C -> about 4x the rank
       photo SVD     480 x 480; 30 layers use 30 x 961 / 230400 = 12.5% of the numbers ("about an eighth")
     Generate: uv run aion voice 009-what-matrices-are --dry-run   then   uv run aion voice 009-what-matrices-are -->

# INTRO

Nine numbers, arranged in a box.

It might be the most useful object in all of mathematics. It also looks like the most boring.

But give it something to act on, and it comes alive. Each column becomes an arrow. Space itself tilts, stretches, and folds, and anything living in that space goes along for the ride.

Every photo on your phone is, underneath, a grid of numbers like this one. Every frame of a video game is drawn with them. One of them helped Google rank the entire web. And a modern neural network is, for the most part, a very long stack of them.

And yet, most of us first meet matrices as bookkeeping. Rows and columns, and a strange rule for multiplying them that you practice, use on an exam, and quietly forget.

The rule works. It just hides what a matrix actually is.

So here is the claim this video is going to earn. A matrix is not a table you read. It is a move you make. A way of picking up all of space, and setting it down somewhere new.

Once you see it that way, the strange rules stop being strange. Multiplying two matrices means doing one move, and then another. Some moves crush space flat, and can never be undone. Some leave a few special directions untouched. And every one of them, however messy its numbers look, is built from three simple motions.

We'll start with two arrows on a flat grid, and end by taking a photograph apart, one stretch at a time.

> [pause 3]

# CHAPTER 1: Nine numbers in a box

First, the plain facts. A matrix is a rectangle of numbers. We give its size as rows, then columns, so this one is two by three. And every entry has an address: which row it sits in, and which column.

Because it's so plain, a matrix can hold almost anything. Take three equations that share the same three unknowns. Strip away the letters, keep only the numbers in front of them, and what's left is a matrix. Remember these three equations. We'll come back and solve them.

Or take a picture. This one is a single frame from a moment ago. Zoom in far enough and it breaks into tiny squares, and each square is just a number for how bright it is. A black and white picture is a matrix with hundreds of rows and hundreds of columns. Keep this one in mind, too.

So a matrix can be a table. But that leaves a strange question. A table of exam grades can't rotate anything. A list of prices can't tilt a die. So how did nine numbers, at the start of this video, pick up a whole space and turn it?

To answer that, we have to stop reading the numbers, and start watching what they do.

# CHAPTER 2: A machine that moves space

Picture a flat grid, and an arrow starting from its center. That arrow is a vector, and you can describe it by where its tip sits. Two steps over, one step up.

Now imagine a machine. You feed it an arrow, and it hands you back a different arrow. Arrow in, arrow out.

Watching one arrow at a time gets slow. So let's feed the machine every arrow at once. Every point on the grid slides to its new home, and the grid lines travel with them.

Most machines would tangle the grid into a mess. The ones that matrices describe follow three rules. Straight lines stay straight. Evenly spaced lines stay evenly spaced. And the center stays where it is. Moves like these are called linear.

Inside those rules, there's a surprising amount of freedom. You can rotate the whole plane. You can stretch it, more in one direction than the other. You can shear it, sliding each row a little further than the one below, like a deck of cards. You can flip it, as if in a mirror. You can even squash it flat, onto a single line.

What you can't do is bend the grid lines into curves, or drag the whole plane away from its center.

And all of this carries over to three dimensions. A die can be turned, stretched, sheared, and flattened, and the grid of space moves right along with it, cell for cell.

So that's the machine. But where do the numbers come in?

# CHAPTER 3: The columns are the whole story

This is the idea that everything else in this video grows out of.

Look at two special arrows. One step to the right, called i hat. And one step up, called j hat. Every other arrow can be built out of these two. Our arrow from before is two copies of i hat, plus one copy of j hat.

Now apply a move. Because the grid lines stay parallel and evenly spaced, that recipe survives. The new arrow is still two copies of wherever i hat landed, plus one copy of wherever j hat landed.

Think about how much that gives you. To know where every single point in the plane goes, you only need to follow two arrows.

So write down where they land. Where i hat lands becomes the first column. Where j hat lands becomes the second. Those two columns are the matrix. Nothing more, nothing less.

And multiplying a matrix by a vector is just that recipe, written in numbers. Scale the first column by the vector's first number. Scale the second column by its second number. Add the two. That's where the arrow lands.

Which means you can now read a matrix the way you'd read a map. Try this one. Its first column says i hat lands pointing straight up. Its second says j hat lands pointing left. Before the grid moves, what do you think it does?

> [pause 2.5]

It turns the whole plane a quarter turn, counterclockwise.

Three dimensions work exactly the same way, with three arrows and three columns. So now we can decode the box from the very beginning. The first column is where i hat goes. The second, j hat. The third is where k hat goes, the arrow pointing up. Nine numbers. Three arrows.

This is how a video game turns a character. The character is built from thousands of corner points, and every one of them gets multiplied by the same small matrix, fresh for every frame.

# CHAPTER 4: One move after another

What happens if you make one move, and then another? Shear the plane, and then rotate it.

The grid still ends up straight, evenly spaced, and centered. So the combined motion is itself a single move, and it has its own matrix. To find it, we just follow i hat and j hat.

The shear leaves i hat where it is, and then the rotation sends it straight up. That's the first column of the combined move. The shear tips j hat onto the diagonal, and the rotation carries that diagonal up and to the left. That's the second column.

Look at what we just did. To get each column of the result, we pushed a column of the first matrix through the second one. Write that out with numbers, and out comes the row times column rule from the start of the video. Nobody invented that rule to torture students. It's simply what two moves in a row look like, written down.

We write the rotation on the left, because it acts second, the same way you'd write f of g of x. Which raises a fair question. Does the order matter? If you rotate first and shear second, do you end up in the same place?

> [pause 2.5]

You don't. The two grids land in different places. And real objects agree. Turn a die a quarter turn forward, and then a quarter turn to the side. Now start over, and do it in the other order. A different face ends up on top.

With matrices, the order is part of the move.

This idea, stacking moves, is the heart of a neural network. Each layer takes a list of numbers, multiplies it by a matrix, shifts it a little, and then bends the result, squashing the largest values.

That bend matters more than it looks. Without it, ten layers of matrices would multiply together into just one matrix, a single straight move. And no single straight move can untangle these two spirals.

With the bends, each layer folds space a little. Fold by fold, the spirals pull apart, until the two colors can be cleanly told apart.

Every move we've made so far could be played backwards. But that isn't always possible.

# CHAPTER 5: The moves you can't undo

Here's the matrix we'll carry through the rest of the video. It tilts and stretches the grid. To undo it, you play the move in reverse, and that reverse move has a matrix of its own, called the inverse. Do the move, then the inverse, and every point comes home. Together they make the move that does nothing at all, the identity.

Now watch the little unit square during the move. Its area grows by a factor of four. That one number, the stretch in area, is called the determinant. It has a whole video of its own.

For now, one question matters. What happens when that number is zero?

Then the area becomes nothing. The whole plane gets squashed onto a single line.

And something is lost. Look at these different points. They all land on exactly the same spot. Once they're there, nothing can tell them apart again, so no move can undo it.

One entire line of points gets crushed into the center itself. That line is called the null space. And everything that survives lands on the output line, called the column space: every place the move can reach.

You've seen this happen. A shadow is exactly this kind of move. Sunlight flattens a three dimensional die onto the ground, and every point along a single ray of light ends up on the same spot of shadow. The direction of the light is the null space. That's why you can't rebuild the die from its shadow alone. A photograph does something similar, which is why depth in a single photo has to be inferred from clues, never read off directly.

Now, about those three equations from the start. Solving them is really a question about a move. Some matrix moves space, and we know where an arrow ended up. Which arrow was sent there?

In two dimensions, each equation is a line, and the answer is where the lines cross. Seen as a move, it's the one arrow that lands exactly on the target.

With three unknowns, each equation becomes a flat plane in space, and three planes usually meet at a single point. That point is the solution.

But if the determinant is zero, space has been flattened. Then the planes either share infinitely many points, or they miss each other entirely, and there's no answer at all. Either way, you can't simply run the move backwards. That's what a zero determinant has been warning you about all along.

# CHAPTER 6: The directions that don't turn

Back to our running example. This time, watch single arrows instead of the whole grid. Most arrows get knocked off their own line. They come out pointing somewhere new.

But sweep around the circle, and watch closely. Here, the output lines up with the input. This arrow only gets stretched, by a factor of four. And here's another one. This one isn't stretched at all.

These special directions are called eigenvectors, and how much each one stretches is its eigenvalue. They're the skeleton of the move. Along them, a complicated matrix behaves like plain multiplication by a single number.

A quick test. Take a rotation of the flat plane. Which arrows stay on their own line?

> [pause 2.5]

None of them. Every arrow turns. But in three dimensions, it's different. Remember the die, turned one way and then the other? Those two quarter turns combine into a single turn, about a tilted axis. Arrows along that axis don't move at all. Every rotation in space has an axis like this. The axis is an eigenvector, with an eigenvalue of one.

Eigenvectors also tell you where things are heading. Take a cloud of points, and apply the same matrix again, and again. Each time, the direction with the biggest stretch wins a little more. After just a few rounds, the whole cloud has lined up along it.

Apply a matrix over and over, and everything drifts toward its strongest eigenvector. That simple fact once organized the entire web.

Here's a tiny web of seven pages, and thousands of imaginary readers clicking links at random. Every so often, a reader gets bored and jumps to a random page instead.

Each round of clicks is one multiplication by a matrix that shuffles readers between pages. Run it, and the crowd settles. Some pages end up holding far more readers than others, and it doesn't matter where everyone started.

That settled crowd is an eigenvector of the click matrix, with an eigenvalue of one. The shuffle no longer changes it. This was the idea behind Google's PageRank. And look at these two pages. Each has just one incoming link. But one of those links comes from the most popular page, and that makes it count for far more.

# CHAPTER 7: A rotation, a stretch, and a rotation

There's one more thing to see, and it's the deepest idea in this video.

Draw a circle of arrows, and apply our matrix. The circle becomes an ellipse. That's no accident. Every matrix like this one turns a circle into an ellipse.

An ellipse has a longest direction and a shortest one, at right angles to each other. Follow them back, and you find two input arrows, also at right angles, that land exactly on those axes.

So here's what the matrix really does, in three steps. First, rotate, so those two input arrows line up with the grid. Then stretch along the grid, more in one direction than the other. Then rotate again, into the final position. Rotate, stretch, rotate. Sometimes one of those turns includes a mirror flip, but that's the whole story.

This is called the singular value decomposition, and the amounts of stretch are called singular values. It works for every matrix, of any shape or size. In three dimensions, a sphere becomes an ellipsoid with three perpendicular axes. However messy the numbers, the move underneath is always this simple.

Now, remember the picture from the beginning, the grid of brightness values? It's a matrix too, so it has this same structure. Two rotations, and a list of stretches, from biggest to smallest.

Each stretch contributes one layer to the picture. And each layer is about as simple as an image can be: a single column of numbers, times a single row. Here's the biggest layer on its own. Just a soft blur. Add the second, and the third. By ten, you can make out the die. By thirty, it's close to the original.

Thirty layers out of hundreds, using about an eighth of the numbers. The small stretches were mostly fine detail, and noise.

This is a classic way to compress images, and the same idea finds the patterns hiding in huge tables of measurements.

So the table and the machine were never two different things. A grid of numbers is a move. And its biggest stretches are what matter most.

# OUTRO

Let's look at that box of nine numbers one last time.

Its columns are where the axes land. Multiplying it by another matrix means one move after another. Its determinant tells you how much volume grows, and whether the move can be undone. Its eigenvectors are the directions it leaves on their own line. And underneath it all, it's a rotation, a stretch, and another rotation.

One last thought. These nine numbers aren't really the move itself. They're what the move looks like from where we're standing, measured along our own choice of i hat, j hat, and k hat. Pick three different arrows, and the very same move gets nine different numbers.

The numbers change. The move doesn't.

If you'd like to see one of those numbers up close, the determinant, that video is right here. Thanks for watching.
