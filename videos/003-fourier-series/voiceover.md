What you're looking at is a chain of circles. Each one rides on the edge of the one before, spinning at its own steady speed. [pause] Follow the tip of the very last circle, and it draws a treble clef. [pause]

Here's what I find strange about this. A circle is about the roundest thing there is. No corners, no straight edges. And yet the right circles can draw sharp turns, even a square with four perfect corners. [pause]

So how does something that only goes round draw a corner? [pause]

The answer is something called a Fourier series, named after Joseph Fourier, who found it about two hundred years ago while studying, of all things, heat. And it makes a bold claim. Almost any loop you could draw can be built out of spinning circles. [pause]

Think of a chord on a piano. You hear one sound, but it's really a few notes played together. A Fourier series lets you take a shape and pick out the circles inside it. [pause]

By the end, you and I will have a recipe that finds the circles for any drawing. I'll put it on screen now, just so you'll recognize it later. [pause]

As with anything new, it's best to start easy. So let's begin with a single circle. [pause]

Picture an arrow pinned at the center, turning steadily. For now, ignore everything except how high its tip is. Up, down, up, down. [pause] Now let time move to the right, and let that height leave a trail. [pause]

What you get is a sine wave. It's the simplest wave there is, and really, it's just a circle seen from the side. [pause]

A spinning circle has only three settings. There's its size. A bigger circle makes a taller wave. [pause] There's its speed. Spin twice as fast, and the wave wiggles twice as often. [pause] And there's where it starts. Start the arrow a quarter turn ahead, and the whole wave slides over. [pause] Size, speed, and starting point. That's everything one circle can do. [pause]

There's another view I really like. Slide the circle forward through time, and its tip traces out a spring. From the side, the spring looks like a sine wave. From above, it looks like its twin, the cosine. Two shadows of one turning motion. [pause]

One circle gives you one smooth wave. So let's add a second. [pause]

Put a smaller circle on the tip of the first, and let it spin three times as fast. Now the tip rides on two motions at once, so its height is the first height plus the second. [pause] The wave picks up a little ripple. [pause]

Now let's be more deliberate. Make the first circle a little taller than the wave we're aiming for. The second spins three times as fast, at one third the size. The next, five times as fast, at one fifth. Then seven times, at one seventh. [pause]

Before I keep going, take a moment to guess. What do you think this is turning into? [pause]

Watch the top flatten out, and the sides get steeper. Here it is with ten circles... fifty... two hundred. [pause] It's a square wave. Flat on top, flat on the bottom, with straight walls in between. Smooth circles, adding up to sharp corners. [pause]

But look closely at a corner. Right before every jump, there's a small spike. Add more circles, and the spike gets thinner, but it never gets any shorter. It stays at about nine percent of the jump. [pause] This is called the Gibbs phenomenon, and it's telling us something. Sharp corners are expensive. [pause]

Now you might be wondering why anyone would build waves out of circles in the first place. The short answer is heat. [pause]

In eighteen oh seven, Fourier was trying to describe how heat spreads through a solid. Take a metal ring, heat one half with a flame, cool the other half with ice, and let it go. [pause] Hot on one side, cold on the other. Unroll the ring, and that's our square wave. [pause]

Fourier's move was to break the temperature into simple waves. One that goes around the ring once, one that goes around three times, then five, and so on. [pause] Each of those waves does something very simple. It keeps its shape, and it just fades. And the wigglier the wave, the faster it fades. Three times the wiggles, nine times as fast. [pause] So the sharp edges melt away first, the ring settles into one gentle wave, and then into an even warmth. [pause]

But for this to work, any starting temperature, even one with sudden jumps, had to be a sum of smooth waves. Some of the best mathematicians of his day didn't buy it. [pause] Well, you and I just watched it happen. [pause]

Now let's bring all this back to our drawing. [pause]

So far, we've only watched the height of the tip. But it also moves left and right. So let's use both, and let the tip draw right on the page. [pause]

This picture is actually very old. Nearly two thousand years ago, astronomers tracked the planets with circles riding on circles. They were wrong about how the sky works. But they were right about the circles. With enough of them, you can follow almost any path. [pause]

On a page, direction matters. A circle can turn counterclockwise, which we'll call a positive speed, or clockwise, a negative speed. A circle with speed zero doesn't turn at all. It just sets where the drawing sits. [pause]

Here's a friendly example we'll keep coming back to. Take a big circle turning forward once, and add a small one, one ninth the size, turning backward three times as fast. [pause] The tip traces out a rounded square. [pause] And the square from the beginning? Its first two circles are exactly these. [pause]

In general, we line up circles of every whole number speed. Zero, one, minus one, two, minus two, and so on. Each has two settings left to choose, its size and its starting angle. [pause]

So here's the real question. If I hand you a drawing, how do you find the size and starting angle of every circle? [pause]

Let's warm up with the easiest circle, speed zero. [pause]

It never moves, so it should sit at the center of the drawing. But what does center even mean, for a squiggly shape like this? [pause]

Here's a natural answer. Spread dots along the path, evenly in time, and average all their positions. That average is the balance point of the drawing, and it's exactly where the speed zero circle sits. [pause] That's because every other circle spins all the way around, and a full turn averages out to nothing. [pause]

That gives us the key idea. Things that spin average out to zero. Things that stand still don't. [pause]

Now, the speed one circle spins, so the average can't see it. Unless we can make it stand still. [pause]

Here's the trick. As the pen goes around, turn the whole drawing backward, one full turn per loop. The speed one circle was turning forward once, and now it's also turned backward once, so it stops. [pause] Every other circle is still spinning, so when we average, they all wash out. What's left is the speed one circle, frozen in place. [pause]

As a sanity check, let's try our rounded square, where we know the answer. Turn it backward once and average, and the balance point lands right on the tip of the big circle. [pause] Turn it forward three times, and it finds the small circle, one ninth the size, just as it should. [pause] Try speed two, and the average falls to zero. There's no circle there. [pause]

If you hold on to just one idea from this video, make it this one. To find any circle, spin the drawing against it, and take the average. [pause]

Now we can read the line from the beginning. C n equals the integral from zero to one, of f of t, times e to the minus two pi i n t, d t. [pause] It looks dense, but it's really just two steps. F of t is the pen's position at time t. Multiplying by e to the minus two pi i n t turns the drawing backward, n times per loop. If you saw our video on complex numbers, that's just a point turning around a circle. [pause] Then the integral from zero to one takes the average over one trip around. [pause] Spin, then average. That's all it says. [pause]

So let's give it a real test. [pause]

Here's our treble clef, as one continuous line. We place a thousand dots along it, and for every speed from minus one hundred to one hundred, we spin and average. Out come two hundred and one circles. Sort them from biggest to smallest, and chain them tip to tail. [pause]

With one circle, we get a loop. With five, a rough blob. By twenty, you can start to see it. [pause] And with two hundred, the circles trace the clef almost perfectly. [pause] Up close, even the tiniest circles are adding detail the others can't. [pause]

Remember how I said sharp corners are expensive? Smooth curves come from the first few circles. Sharp turns need all the rest. [pause] When the pen jumps, like in the square wave, the circles shrink slowly. One third, one fifth. When the pen only turns a corner, like our square, they shrink much faster. One ninth, one twenty fifth. [pause] The smoother the shape, the fewer circles it takes. [pause]

That's why this idea shows up everywhere. Think back to the piano chord. A sound is a wave, so it has circles too. A singer and a violin playing the same note spin their slowest circle at the same speed. It's the faster circles on top that make them sound different. [pause] And your phone uses a cousin of this idea to shrink photos and music, keeping the big circles and dropping the tiny ones you won't notice. [pause]

So let's step back and look at what we've built. [pause]

One spinning circle gives you the simplest wave, with a size, a speed, and a starting point. [pause]

Stack circles tip to tail, and their motions add up. With the right sizes and speeds, smooth circles can build sharp corners. [pause]

Fourier's insight was that almost any repeating shape can be built this way. And once the tip moves in two directions, those waves become drawings. [pause]

To find the circles, you spin the drawing backward and take the average. Whatever stands still is the circle you were looking for. [pause]

There's one thing we quietly assumed, though. Our drawings repeat. The pen always comes back to where it started. [pause] What about a sound that never repeats? Then you need circles of every possible speed, not just whole numbers. That's the Fourier transform, and it's where we'll go next. [pause]

For now, let's watch it one more time. Just circles, going round. [pause]

Thanks for watching.
