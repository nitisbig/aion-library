# The Math That Shows You a Black Hole: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Generate: uv run aion voice 004-black-hole-math --dry-run   then   uv run aion voice 004-black-hole-math -->

# COLD OPEN (cinematic black hole, about twenty seconds)

This is a black hole.

Nobody painted it. Nobody photographed it.

Every point of light you see was placed there by a calculation.

# INTRO

And the whole picture comes from one equation. A single line of math, that tells a ray of light where to go.

By the end of this video, you will be able to read that equation. And you will know why this image looks the way it does.

Because it is stranger than it seems. Look at this bright arc, curving over the top. You would think it is a second ring of gas, standing upright behind the hole. It is not. There is only one flat disk here, and you are seeing it in a way that should be impossible.

To understand how, we will start with a single ray of light, and end by building this image, one pixel at a time.

# CHAPTER 1: Can light be trapped?

Let us begin with a simpler question. Can light be trapped?

Throw a ball upward, and it falls back. Throw it faster, and it climbs higher before it returns. But there is a speed at which it never returns at all. That is the escape velocity. For the Earth, it is about eleven kilometres every second.

The formula is short. The escape velocity depends on the mass you are leaving, and on how far you are from its centre. More mass, or less distance, and you need more speed.

So here is a thought, first written down in seventeen eighty three. Squeeze a mass into a smaller and smaller ball. The escape velocity at its surface keeps rising. At some point, it reaches the speed of light.

Set the escape velocity equal to the speed of light, solve for the radius, and you get this. Two times G times the mass, divided by the speed of light squared. It is called the Schwarzschild radius.

For the Earth, that radius is nine millimetres. The whole planet, pressed into a marble. For the Sun, it is three kilometres.

Anything squeezed inside its own Schwarzschild radius is a black hole. And that sphere is the edge of no return.

But this argument has a problem. It treats light like a thrown ball, and light has no mass. If you push the same reasoning further, and ask how much a passing ray of light should bend, you do get an answer. And that answer is wrong, by a factor of exactly two. Remember that number. It comes back.

To get it right, we need a better idea of what gravity is.

# CHAPTER 2: Straight lines in curved space

Here is the idea. Light always travels in a straight line. Always. Gravity does not pull on it.

What gravity does, is change what straight means.

Picture a flat sheet, with a grid drawn on it. On this sheet, a straight line is exactly what you expect. Two lines that start side by side, stay side by side forever.

Now put a mass in the middle. The sheet is no longer flat. Near the mass, distances stretch. And this funnel is not a cartoon. Its shape is computed. It is the real geometry of a slice of space around a star.

Send two rays across this surface. Each one goes as straight as it possibly can. It never turns left, and it never turns right. And yet, the paths bend toward the mass.

Nothing pulled on them. The space they moved through was curved, so the straightest possible path was a curve.

Now look from directly above. This is the picture we will use from here on. A mass at the centre, and a ray of light, bending as it passes.

So the question becomes precise. Exactly what curve does the light follow?

# CHAPTER 3: The equation

To describe the path, we need two numbers for each point on it. The angle around the mass, called phi. And the distance from the mass, called r.

There is one trick that makes everything simpler. Instead of the distance, we track one divided by the distance. Call it u. When the light is far away, u is almost zero. When it comes close, u grows.

First, take the mass away completely. The light goes perfectly straight. And if you plot u against the angle, that straight line becomes a pure sine wave. It rises as the light approaches, peaks at the closest point, and falls again.

A sine wave obeys a famous little equation. Its second derivative, plus itself, equals zero. So this is the equation of a straight line. U double prime, plus u, equals zero.

Now bring the mass back. Einstein's theory changes this equation in exactly one place. The zero on the right becomes a new term. Three times G times the mass, over the speed of light squared, times u squared.

That is it. That is the equation behind every black hole image.

Look at what the new term does. It contains u squared. Far from the mass, u is tiny, and u squared is far tinier, so the term does nothing, and the light goes straight. Only close to the mass does it wake up, and bend the path inward.

Let us test it. A ray of starlight, just grazing the edge of the Sun. The equation says it bends by one point seven five arc seconds. That is the width of a small coin, seen from two kilometres away.

And it is exactly twice what the thrown ball argument predicted. In nineteen nineteen, astronomers measured it during a solar eclipse. The stars near the Sun had shifted, by just this amount.

So the equation works for a gentle bend. But the Sun is far larger than its Schwarzschild radius. What happens when we aim the light at something much smaller, and pass much closer?

# CHAPTER 4: Three fates of a light ray

Here is a black hole, and a ray of light passing far from it. It bends a little, and moves on.

Aim closer. The bend grows. Ninety degrees. Then more than that. The light swings around the back of the hole, and heads home the way it came.

Closer still, and the ray makes a full loop before it escapes.

Before we go on, make a guess. If we keep aiming closer, what is the last thing the light does before it falls in?

It does this. It circles. There is one exact distance at which light can orbit a black hole, around and around.

And our equation tells us where. On a perfect circle, the distance never changes. So u never changes, and its second derivative is zero. Cross that term out. What remains is simple algebra, and it gives a radius of one and a half times the Schwarzschild radius.

This is the photon sphere. A shell of orbiting light.

The orbit is unstable, like a pencil balanced on its tip. A ray that arrives the slightest bit outside, spirals away. The slightest bit inside, and it spirals in, and is gone.

So every ray has one of three fates. It escapes, it orbits, or it is captured. And what decides its fate, is how far off centre it was aimed. The dividing line sits at about two point six times the Schwarzschild radius.

That number matters. It means the dark region is bigger than the hole itself. Any light aimed inside that circle never comes back out.

We now have everything we need. One equation, and three fates. Let us build the picture.

# CHAPTER 5: Building the image

Put a camera near the black hole. Each pixel of its image looks out in one direction. And for each pixel, we ask one question. What light arrives from there?

To answer, we run the light backwards. Start a ray at the pixel, send it out from the camera, and let the equation bend it. Then we see where it ends up.

Some rays fall into the hole. No light can come from there, so those pixels stay black. Together they form the shadow, and its edge is that dividing line from before.

Some rays escape to the distant stars. But they arrive bent, so the pixel shows a star from a different part of the sky. Around the hole, the whole sky is stretched, and wrapped into rings.

Now add the disk. A flat, thin ring of glowing gas, circling the hole.

Rays that hit the front of the disk give this bright band across the middle. Nothing surprising yet.

But follow a ray that leaves the camera aimed just above the hole. It bends over the top, comes down behind, and lands on the far side of the disk. So above the hole, you see the back of the disk, lifted into view.

That is the arc from the beginning. Not a second ring. The same disk, seen over the top of the hole. And beneath it, the underside, seen from below.

Hugging the shadow is one more line, thin and sharp. That is light that circled the photon sphere, before escaping toward us.

And one side is brighter than the other. The gas on that side is rushing toward the camera, at a large fraction of the speed of light. And motion toward you makes light brighter.

Every feature has a reason now.

# OUTRO

In twenty nineteen, a telescope the size of the Earth took a real picture of a black hole, fifty five million light years away. It showed a dark shadow, wrapped in a ring of bent light. Just as the equation said.

So here is what a picture of a black hole really is. It is a map of where straight lines go, in a space that is curved.

A speed limit gave us the radius. Curved space gave us the idea. One extra term gave us the path. And the path gave us the picture.

One thing we left out. Real black holes spin, and a spinning hole drags space around with it. The shadow becomes lopsided. That is a story for the next video.
