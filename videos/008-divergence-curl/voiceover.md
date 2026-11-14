# Divergence and Curl, Finally Explained Visually: voiceover
<!-- Lines starting with # or > and HTML comments are notes, not spoken.
     One paragraph per idea; paragraph breaks become the real pauses that cuts snap to.
     Spine: two questions about any point in a flow. Is stuff leaving? (divergence) Is stuff turning? (curl)
     Cast (all verified with sympy, scratch check.py):
       source (x, y)          div 2   curl 0     dye area e^(2t): 2.72 at t = 0.5
       whirl  (-y, x)         div 0   curl 2     wheel turns at curl/2 = 1 rad/s everywhere
       saddle (x, -y)         div 0   curl 0     dye stretches 1.65 x 0.61, area 1.00
       river  (y + c, 0)      div 0   curl -1    visuals shift by c so every arrow points right
       drain  (-y, x)/r^2     div 0   curl 0 (r != 0), circulation 2 pi around the centre
       lamp   (x, y)/r^2      div 0 (r != 0), flux 2 pi through every circle; 3D (x,y,z)/r^3 -> 4 pi
     Generate: uv run aion voice 008-divergence-curl --dry-run   then   uv run aion voice 008-divergence-curl -->

# INTRO

Drop a pinch of dust into a moving stream, and keep your eyes on two places.

Here, the dust spreads apart. Grains that started as neighbors drift away from each other, as if water were welling up from somewhere underneath.

And here, the dust starts to turn. The little cloud swings around, as if it caught the edge of a whirlpool.

Those two motions have names. The first is divergence. The second is curl.

Most of us meet them as a row of partial derivatives. Partial P, partial x, plus partial Q, partial y. You learn the pattern, you get the right answers on the exam, and the picture never quite shows up.

So let's put the picture first. Each of these is really a question you can ask about any single point in a flow. Is stuff leaving this point? And is stuff turning around it?

Answer the first question everywhere, and you get a map of where the flow is born and where it disappears. Answer the second, and you find every hidden spin, even in places where the arrows look perfectly straight.

Then something nice happens when you add up all those tiny answers. Two of the biggest theorems in calculus fall out, almost for free.

We will start with arrows on a page, and end with the four equations behind every radio, every motor, and every beam of light.

> [pause 3]

# CHAPTER 1: A field of arrows

Pick a point in the plane, and attach an arrow to it. The arrow could mean anything. The speed of the wind, the pull of gravity, the push of an electric charge.

Do that at every point, and you have a vector field. A rule that hands each location its own arrow.

A weather map of the wind is exactly this. Every town gets an arrow, telling you which way the air is moving there, and how fast.

To write it down, split each arrow into two parts. How far it points to the right, we call P. How far it points up, we call Q. Both depend on where you are. So the field is F of x y equals P of x y, Q of x y.

Arrows alone are hard to read. So let them carry something. Sprinkle dust everywhere, and let each grain move along the arrow underneath it.

Now the field is a flow. The arrows give the velocity of the water at each point, and the dust shows you where the water goes.

Three flows will keep us company. In the first, every arrow points away from the center. Call it the source. In the second, every arrow points around the center. Call it the whirl. And in the third, water comes in from above and below, and leaves to the left and right. That one is a saddle.

Keep an eye on the saddle. It is going to fool us in a minute.

# CHAPTER 2: Is stuff leaving?

Here is the first question. Drop a small circle of dye into the flow, and ask what happens to its area.

In the source, every grain runs away from every other. The circle grows. Before long, its area has nearly tripled.

In the whirl, the circle swings around the center, but it never gets bigger or smaller. Its area stays exactly the same.

Now the saddle. The dye gets pulled out sideways and squeezed from above and below. Before you watch, make a guess. Does the area grow, or shrink?

> [pause 2]

It does neither. The circle stretches into a long, thin ellipse. It looks dramatic. But it gets longer exactly as fast as it gets thinner, and the area stays put.

That is what divergence measures. Not how wild the flow looks. Only how fast a tiny drop is swelling, compared to its size. Positive means the drop grows. Negative means it shrinks. Zero means the flow only rearranges it.

To turn that into a formula, shrink the drop to a tiny square, and count the water crossing its edges. Whatever flows out, minus whatever flows in.

Start with the left and right edges. Only the sideways part of the arrows, P, carries water across them. If P is a little bigger on the right edge than on the left, more leaves than enters. That difference, divided by the width of the square, is the partial derivative of P with respect to x.

The top and bottom edges work the same way, with the upward part, Q. More leaving through the top than entering through the bottom gives partial Q, partial y.

Add the two, and that is the divergence. Del dot F equals partial P partial x, plus partial Q partial y.

Check it on our three flows. The source gives one plus one. Two. The whirl gives zero plus zero. And the saddle gives one, minus one. Zero. The formula sees exactly what the dye showed us.

Now do it at every point, and color the plane. Warm where the divergence is positive, cool where it is negative. The warm spots are sources, where the flow comes from. The cool spots are sinks, where it drains away. And the dust agrees. It spreads out over the warm patches, and crowds together over the cool ones.

One more flow, and this one matters later. The arrows all point away from the center again, but they shrink as you move outward, like light fading from a lamp.

Everything points outward. So the divergence must be positive. Right?

> [pause 2]

The map stays dark. Everywhere, except the single point at the center. Look at a circle around it. Make the circle twice as wide, and its edge is twice as long. But the arrows out there are half as long. The two effects cancel, so the same amount of water crosses every circle. Nothing is created out here. All of it comes from that one point.

Hold on to that. It comes back.

# CHAPTER 3: Is stuff turning?

Now the second question. This time, drop in a tiny paddle wheel, pinned in place so it can only spin.

In the whirl, it turns. Steadily, counterclockwise, at the same rate no matter where you put it.

Now a river. Every arrow points straight to the right. But the water near the top moves faster than the water near the bottom. Will the wheel spin?

> [pause 2]

It does. The top paddles get pushed harder than the bottom ones, so the wheel turns clockwise. Straight arrows, and still a spin.

The reverse can happen too. Here is a drain. The arrows go around in circles, faster near the middle. Pin a wheel anywhere away from the center, and it does not turn. Let it float with the water, and it travels all the way around the drain, but stays upright, like a car on a Ferris wheel. The fast water on the inside and the slow water on the outside balance out perfectly.

So curl is not about whether the arrows go in circles. It is about whether a tiny wheel, sitting right here, would turn. And how fast.

To measure it, walk once around a tiny square, counterclockwise, and add up how much the flow pushes you along the way. That total is called the circulation.

Along the bottom edge you walk to the right, so the sideways part, P, helps you. Along the top you walk to the left, so P works against you. If P is bigger on top, you lose more than you gain. That difference becomes minus partial P, partial y.

On the right edge you walk up, and on the left edge you walk down. So the upward part, Q, gives you partial Q, partial x.

Put them together. The curl is partial Q partial x, minus partial P partial y. Circulation, per unit of area.

Check it. The whirl gives one, minus negative one. Two. The river gives zero, minus one. Negative one. Clockwise, just like the wheel. The source and the saddle give zero. No spin at all.

In three dimensions, a wheel can tilt. So the curl becomes a vector. It points along the axle that makes the wheel spin fastest, and the right hand rule picks the direction. Curl your fingers with the spin, and your thumb points along the curl.

Our flat curl was only one piece of that vector. The piece pointing straight up, out of the page.

There is a famous shorthand for all of this. Write del as a list of three derivatives. Partial x, partial y, partial z. Take its dot product with F, and you get the divergence. Take its cross product, and you get the curl. It is a memory trick, not a meaning. The meaning is the drop of dye, and the paddle wheel.

# CHAPTER 4: Adding up the little pieces

So far, everything has been tiny. Now let's zoom out.

Take a whole region, and cut it into small squares. Each square has its own outflow. Its divergence, times its area.

Look at two neighboring squares. Whatever leaves the first through their shared edge enters the second. Out for one, in for the other. Add them, and that edge cancels.

That happens on every inside edge. Every single one cancels. The only edges left are the ones on the outer boundary.

So adding up the divergence inside a region gives you exactly the flow out through its boundary. In three dimensions, the squares become little cubes, and the boundary becomes a closed surface. This is the divergence theorem.

And now the lamp from earlier pays off. In three dimensions, its arrows fade with the square of the distance. The same amount crosses every sphere around the center, so every bit of divergence sits at that one point. That is exactly how the electric field of a point charge behaves.

Curl adds up the same way. Give each small square its own little loop of circulation. Where two squares meet, their loops run along the shared edge in opposite directions. They cancel again.

Only the outer loop survives. The total curl inside equals the circulation around the edge. That is Green's theorem.

Lift it into space, and the region can be any surface stretched across a loop of wire, like a soap film. Push the film out into a bubble, and the answer does not change. Only the wire matters. This is Stokes' theorem.

Two theorems, one idea. Add up the tiny answers inside, and everything cancels except the edge.

# CHAPTER 5: Where they live

Now, those four equations from the beginning. They are Maxwell's equations, and you can read them now.

Del dot E equals rho over epsilon naught. Electric charges are the sources and sinks of the electric field.

Del dot B equals zero. The magnetic field has no sources at all. Its lines never start or end. They only loop back.

Del cross E equals minus the rate of change of B. A changing magnetic field stirs up an electric whirl. Spin a magnet near a coil of wire, and that whirl pushes a current around it. That is how most of our electricity is made.

Del cross B equals mu naught J, plus a term for a changing electric field. Currents wrap themselves in magnetic whirls. And together, the last two equations let a changing E make B, and a changing B make E, so the pair can travel on its own. That is light.

The same two questions show up far from electricity. Water barely compresses, so its flow has zero divergence. And a hurricane, seen from space, is a giant patch of curl.

# OUTRO

Let's go back to the stream we started with.

Here is the divergence map, laid over the flow. The place where the dust spread apart sits right on a warm spot. And here is the curl. The place where the dust started turning is this green swirl.

Divergence asks how much is leaving a point, per unit of area. Curl asks how much is turning around it. Add up either one over a region, and only the boundary is left.

The formulas you memorized were never the point. They are the drop of dye and the paddle wheel, written in symbols.

Next time, we will take the divergence of a gradient. It is called the Laplacian, and it is hiding inside heat, sound, and almost every equation in physics.
