# What Matrix Inverses Actually Mean: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Voice: calm, curious, plain words. Show the numbers, don't read them. Concrete picture first, symbol after.
     Spine: an inverse is every thread of a move, walked backward. A way back exists exactly when the move forgot nothing.
     Open loop: one shadow cannot be undone (s02) -> many shadows can (s24-s25).
     Budget: keep this script below 9,500 billable characters (check with the dry run).
     Every number here is computed in verify.py:  uv run python videos/013-matrix-inverse/verify.py
     Generate: uv run aion voice 013-matrix-inverse --dry-run   then   uv run aion voice 013-matrix-inverse -->

# INTRO

<!-- s01 cold_open -->
Take a key, and lay it on a flat grid.

Now pick up the whole plane. Lean it to one side. Pull it upward. Lean it again, and once more.

Four moves, and together they make a single matrix.

So here's the question. Can we put it back?

We can. One more matrix, one smooth motion, and every point returns to exactly where it started. That second matrix is called the inverse.

<!-- s02 the_crush -->
Now try a matrix that looks almost the same. Only its second column is different.

The plane falls flat. The whole key is now a streak on a single line.

Put this one back.

There's nothing to hold on to. This streak could have come from this key. Or this one, with a tooth flipped. Four teeth, each pointing up or down: that's sixteen different keys, and all sixteen leave exactly the same mark.

It's a shadow, and one shadow can't tell you which key cast it.

<!-- s03 promise -->
Why can one matrix be undone, when its near twin can't? The answer decides how a video game draws its world, how a drone reads a map, how a computer solves an equation, and whether a blurred picture can be made sharp again.

And by the end, we'll do something that sounds impossible. We'll rebuild this key from nothing but its shadows.

# CHAPTER 1: The way back

<!-- s04 simple_moves -->
A matrix is a move. Its columns say where the two basic arrows land, and the rest of the plane follows them.

Some moves are easy to undo. Turn the plane, and the way back turns it the same amount in the other direction. Stretch it, and the way back shrinks it. Slide each row sideways, like pushing a deck of cards, and the way back pushes the deck the other way.

<!-- s05 wrong_rule -->
That stretch suggests a shortcut. Two became a half, and three became a third. So maybe you just flip every number upside down.

But the sliding deck has a zero in it, and zero can't be flipped, yet we undid that move by changing a single sign. And the matrix that crushed our key has no zeros at all. So the numbers, read one at a time, won't tell us. We have to watch what the whole matrix does to space.

<!-- s06 threads -->
Follow one point as the plane moves, and draw a thread from where it started to where it landed. Now do the same for every other point.

That web of threads is the move. The way back is the same web, walked in the opposite direction. That's what an inverse is. Every thread, reversed.

<!-- s07 identity -->
Go out along the threads and come back, and every point ends up where it began. The round trip, taken as one move, does nothing at all.

Doing nothing has a matrix too. Its columns leave both arrows at home. We call it the identity, and it behaves like the number one: multiply by it, and nothing changes.

So the inverse is the matrix that, applied after A, leaves you with the identity. Take the way back first, and the threads haven't changed, so everyone still gets home. Either order gives the identity.

# CHAPTER 2: Rewind

<!-- s08 rewind -->
Most moves come in stages. Say we lean the plane, then give it a quarter turn. How do we get back?

Undo the lean, then undo the turn, and the grid doesn't come home. The turn happened last, so it has to come off first. Undo the turn, then the lean, and everything lines up.

It works like a film played backward. The inverse of a chain is the inverse of each link, in reverse order. So if a complicated move can be broken into simple ones, we can rewind it, one simple move at a time.

# CHAPTER 3: Finding the way back

<!-- s09 four_moves -->
Let's do that for the matrix that bent our key, using only slides and stretches.

The first slide pulls one arrow upright. A second slide drops it onto the axis, exactly where it belongs.

The other arrow is standing four times too tall, so we squash the plane to a quarter of its height.

One last slide straightens it. Four moves, and the key is home.

<!-- s10 recording -->
But we never wrote the inverse down as a single matrix. So let's play the same four moves on a second grid, one that starts untouched. As the bent grid straightens out, the straight grid bends, keeping a record of every step.

When the first grid reaches the identity, the second has become the inverse.

If you've learned row reduction, those two blocks of numbers side by side are these two grids. One rewinds, and the other records.

<!-- s11 check -->
Let's check it. Multiply the inverse by the original, and the fractions cancel, leaving ones on the diagonal and zeros everywhere else.

You may also recognize those four moves. They're the same four that bent the key at the start, played backward.

<!-- s12 det_emerges -->
And there's something hiding in that list. A slide never changes area. So all of the shrinking came from that single squash, down to a quarter.

Four is exactly how much the original matrix grew every area. It's the determinant.

Run the same steps with letters in place of numbers, and out comes the recipe for any two by two matrix. Swap these two, negate those two, and divide by the determinant.

Which should make you a little uneasy. What happens when there's nothing to divide by?

# CHAPTER 4: What can't come back

<!-- s13 tilt -->
Take our matrix, and slowly tilt its second column toward the first. The plane grows thinner, the determinant falls, and the inverse has to work harder. To reopen a plane this thin, it has to stretch by a factor of ten. Then a hundred. Then a thousand.

Keep this nearly flat moment in mind. It's going to matter.

When the two columns finally line up, the plane is flat, the determinant is zero, and the inverse has run off to infinity.

<!-- s14 many_to_one -->
Pick one spot on the line, and ask which points landed there. The threads come in from an entire line of points. These are the rays that cast our shadow.

A way back would have to send this one spot to all of those points at once, and a matrix gives each input just one answer.

<!-- s15 columns -->
You can read this in the columns. Here, the first column is exactly twice the second, so the second adds nothing new. We say the columns are linearly dependent. And that relationship is the crushed arrow itself: one of the first, minus two of the second, makes nothing.

<!-- s16 one_fact -->
So these are one fact, seen from four sides. The columns depend on each other. The area drops to zero. A whole direction disappears. And there is no way back. If any one of these is true, all of them are.

# CHAPTER 5: Who landed here?

<!-- s17 powders -->
Undoing a matrix is also what it means to solve an equation.

Say you're mixing two powders. A scoop of the first has three grams of protein and two of fibre. A scoop of the second has one of protein and two of fibre. Those are the columns of our matrix. Give it a number of scoops, and it tells you what you get.

Usually, though, the question runs the other way. You need seven grams of protein and six of fibre. How many scoops is that?

<!-- s18 solve -->
Geometrically, that asks which point landed on this target. And we know the way back. Apply the inverse, follow the thread home, and there's the answer: two scoops of the first, one of the second.

Every linear system asks the same thing. You know where something ended up, and you want to know where it started.

<!-- s19 weak -->
Now swap in a second powder that's exactly half as strong as the first. Every mix you can make falls on a single line. Ask for something off that line, and no recipe exists. Ask for something on it, and there are endless recipes.

No answer, or too many. Those are the two ways a system fails, and both are the collapse we just saw.

# CHAPTER 6: The way back at work

<!-- s20 drone -->
Two observers can describe the same place in different ways. To a drone with its own tilted grid, this landmark is two steps ahead and one to the side. The matrix built from the drone's axes translates that onto the map, and its inverse translates the map back into the drone's point of view.

<!-- s21 camera -->
A video game does this for every frame. The camera is placed in the world by a matrix, and to find out what it sees, the game applies the inverse of that matrix to everything else. As far as the computer is concerned, you never walk forward. The world gets carried backward, past you.

<!-- s22 blur -->
Now here's a picture, smeared by a shaking camera. Each blurred pixel is an average of its neighbours, and averages are exactly what a matrix computes. This blur has an inverse. Apply it, and every edge comes back.

<!-- s23 noise -->
But remember that nearly flat plane. Blur squeezes the finest detail almost to nothing, so the inverse has to stretch it by an enormous amount. Add a trace of noise, too faint to see, and it gets stretched too, until the picture is buried.

So a matrix can have an inverse, and that inverse can still be useless. Real deblurring stops short, and undoes only the directions that survived.

# CHAPTER 7: Shadows

<!-- s24 second_shadow -->
Which brings us back to the key, and the shadow we couldn't undo.

From one shadow, that's still true. But nothing stops us from taking another. Turn the light, and a tooth that could have pointed either way now falls in a different place. Each new shadow adds new equations, and fewer and fewer keys can fit them all.

<!-- s25 ct_reconstruct -->
Two shadows. Four. Sixteen. A blur at first, then an outline. With enough angles, the combined matrix no longer forgets anything, and here's the key, teeth and all, rebuilt from shadows alone.

This is how a CT scanner sees inside your body. It records shadows from hundreds of angles, then solves for what must have cast them.

<!-- s26 outro -->
Every matrix moves space. The inverse asks what that move forgot.

If it forgot nothing, every point still has a thread leading back to where it began, and the way home exists. If it forgot something, that part is gone, and no amount of algebra will bring it back. All you can do is go and look again, from somewhere new.
