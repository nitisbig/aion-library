# What Lagrange Multipliers Actually Are: storyboard

**Status:** approved and built (2026-11-18). Audio generated: `assets/audio.wav`, 845.58 s = **14:06**, 2,393 words, 6 chunks,
12,847 characters. Scene times below are the storyboard estimates, and the exact ranges are in `beats.py`.

Alt titles: *Lagrange Multipliers, Visually Explained* · *Lagrange Multipliers: Intuition, Geometry & Examples* ·
*Lagrange Multipliers: The Intuition Nobody Shows You*.

Files: `voiceover.md` (every spoken word), `verify.py` (every number, 44 checks), `theme.py` (colors).

## The spine
**At the best point, the only way left to improve is the way you are forbidden to go, and λ is what that forbidden
direction is worth.** The intro asks Dido's question and promises that the mysterious number can be measured with a
stick. The chapters build the picture, then the method, then the meaning. The outro answers Dido: the rope is a
semicircle and λ is its radius.

## Promises tracked
| promise | made | paid |
|---|---|---|
| what shape should Dido's rope make | s01 | s28 |
| the highest point of the trail | s04 | s12, s13 |
| one arrow is forced to line up with another | s08 | s14 to s16 |
| the laws of heat | s06 | s25 |
| "you can measure it with a stick" | s08 | s28 |
| "hold on to that ten" | s19 | s23 |

## History as narrated (checked 2026-11-18)
- Dido and the ox hide are a **legend**, and the script says "the story goes". Carthage's founding is dated to the ninth
  century BC. ([Dido's Problem, arXiv 2301.02917](https://arxiv.org/pdf/2301.02917))
- Fermat's maxima and minima method circulated around 1636. ([Adequality](https://en.wikipedia.org/wiki/Adequality))
- Lagrange, 19, wrote to Euler on 12 August 1755 with an analytic method for isoperimetric problems.
  ([New World Encyclopedia](https://www.newworldencyclopedia.org/entry/Joseph-Louis_Lagrange))
- *Mécanique analytique*, 1788: the preface says no figures will be found in the book.
  ([MacTutor](https://mathshistory.st-andrews.ac.uk/Extras/Lagrange_Analytical_Mechanics/))
- The multipliers arose in statics, for equilibrium under constraints.
  ([Bussotti 2003](https://link.springer.com/article/10.1023/A:1023952102705))
- Karush 1939, Kuhn and Tucker 1951, working independently. ([William Karush](https://en.wikipedia.org/wiki/William_Karush))

## Color and type
One color per object for the whole video (`theme.py`): **f and ∇f amber**, **g, ∇g, the trail and the rope cyan**,
**λ pink**, the walker yellow, tangents green, the Lagrangian blue. Black background, crisp lines, no glow. Computer
Modern throughout: maths in roman, labels in sans, names and dates in small caps. Key words only on screen.

## Scenes

### Intro: a documentary that turns into mathematics (0:00 to 2:50, no equations)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s01 dido_coast | 0:00 | Dido lands, the ox hide, the rope | One unbroken dusk shot of a Phoenician galley reaching Africa (`voyage.py`). Real images pop up as small cards on the words that name them (`cards.py`, `assets/photos/CREDITS.md`), while the years roll back to 814 BC in the sky. The engraved hide becomes the animated hide, which is sliced into one rope that runs to the shore. | skia, real images, Manim |
| s02 question | 0:33 | "What shape?", best with what we have | Camera rises to a top view. The rope tries a square, a triangle and an arc while an area bar moves. The rope then morphs into a budget bar and a bridge truss: same question, new worlds. | Manim, skia |
| s03 fermat | 0:55 | Fermat's flat ground | Ink curve on black, name and date in small caps. A tangent rides up the curve and flattens at the top. | Manim |
| s04 trail | 1:10 | The trail around the mountain | The 3D mountain orbits slowly with a cyan trail around it. The walker stops at the trail's high point, and an arrow shows the slope still rising toward the unreachable summit. | skia 3D |
| s05 lagrange | 1:35 | Turin, Euler, 1755 to 1788 | Moving timeline with portrait cards of Lagrange and Euler and a letter flying between them. A pulley machine balances, and each restriction lights up with one pink "?". | Manim, skia |
| s06 everywhere | 2:05 | Wings, budgets, networks, boundaries, heat | Five line-art panels on the beat, each carrying the same pink "?". | skia |
| s07 no_figures | 2:20 | "No figures will be found" | A page of dense algebra. The symbols drift apart and resolve into crisp contour lines, the picture Lagrange left out. | Manim |
| s08 preview | 2:35 | What we will see | Four quick cuts: the kiss, the arrows, the equations, the examples. It ends on a stick lying on the sand. | Manim |

### Ch1: free and constrained (2:50 to 4:00)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s09 objective | 2:50 | f, gradient, flat ground | The mountain tilts down into a height map, showing that the map and the surface are one object. A gradient field appears, and the walker follows it to the summit as its arrow shrinks to zero. | skia 3D to Manim |
| s10 constraint | 3:15 | g = c, one direction left | The trail is drawn and everything off it dims. Two freedom arrows collapse into one. The attempt to unroll the trail tangles, motivating a better idea. | Manim |

### Ch2: contours (4:00 to 5:32)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s11 contours | 4:00 | Slices, gradient ⟂ contour | Horizontal planes slice the mountain and the rings drop onto the map. An arrow pinned to a moving point stays perpendicular to the contour. | skia 3D, Manim |
| s12 walk | 4:30 | Crossings slow, then the touch | The walker moves along the trail and each contour crossing ticks. The ticks spread out and stop at the kiss, so viewers see the top arrive. | Manim |
| s13 swell | 5:00 | The loop swells, two families | A contour swells from the summit until its first touch. The trail then reveals its sibling level curves of g, giving two families of curves. | Manim |

### Ch3: the gradients align (5:32 to 7:14)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s14 align | 5:32 | Shared tangent, ∇f = λ∇g | Zoom into the kiss. The tangent line appears, both gradients grow from it, and the equation assembles in matching colors. | Manim |
| s15 compass | 6:00 | Along and across | The walker carries ∇f, split live into its along and across parts. A green bar for the along part shrinks to zero exactly at the best point. This is the core intuition. | Manim |
| s16 proof | 6:30 | Three-line proof, count equations | Each line is tied to the arrow it describes, with velocity r′ on the trail. It ends with three equations and three unknowns. | Manim |

### Ch4: the Lagrangian (7:14 to 8:04)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s17 lagrangian | 7:14 | L = f − λ(g − c) | Each partial derivative flies out of L and lands on the equation it reproduces. | Manim |
| s18 saddle | 7:40 | The flat point is a saddle | The surface of L over (x, λ) with the point (1, −2) marked, rising one way and falling the other. | skia 3D |

### Ch5: worked examples (8:04 to 9:42)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s19 fence | 8:04 | 40 m of rope, λ = 10 | Top view of the beach beside the live solution: 10 by 20, area 200. λ = 10 is pinned in the corner for later. | Manim |
| s20 circle | 8:50 | x²y on the circle, six candidates | Contours of x²y around the circle with six kisses lighting up. A strip below unrolls f around the circle and reads 2, 0, 2, −2, 0, −2. | Manim |

### Ch6: higher dimensions (9:42 to 10:49)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s21 sphere | 9:42 | Sphere inflates to the plane | A sphere grows until it touches the plane at (1, 2, 2), with the normals aligned. | skia 3D |
| s22 ellipse | 10:10 | Two constraints, ∇f in a plane | A cylinder and a tilted plane cut an ellipse. At its top, a translucent plane spanned by ∇g and ∇h visibly contains ∇f. | skia 3D, Manim overlay |

### Ch7: what λ is (10:49 to 12:27)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s23 price | 10:49 | One more meter buys ten | The pinned λ = 10 returns. The rope grows by a meter, the plot grows, and the gain reads about 10 square meters. The tag "shadow price" appears. | Manim |
| s24 force | 11:20 | The hoop pushes back | A bead on a hoop with gravity and the hoop's force as equal and opposite arrows. | Manim |
| s25 boltzmann | 11:40 | Gas, entropy, temperature | Simulated gas molecules beside a histogram that settles onto e^(−βE). It ends on β = 1/T. | exact bouncing particles (PointsLayer), Manim |

### Ch8: the fine print (12:27 to 13:22)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s26 cusp | 12:27 | The cusp defeats the equations | The curve y² = x³ with ∇f at the cusp and ∇g shrinking to nothing as the point arrives. | Manim |
| s27 inequality | 12:55 | Karush, Kuhn, Tucker | A wall moves away from the walker and λ's dial falls to zero the moment the limit stops pressing. | Manim |

### Outro (13:22 to 14:14)
| scene | time | narration | visual, and why it explains | tools |
|---|---|---|---|---|
| s28 semicircle | 13:22 | The rope relaxes, λ is the radius | Back on the dusk beach. The rectangle relaxes into a semicircle and the area climbs from 200 to 255. A pink stick is laid from the center to the rope: λ, about 12.7 m. The final line plays over the coast. | skia, Manim, 2.5D camera |

## Rendering notes
- 3D scenes use a small skia painter (`draw3d.py`) instead of PyVista: crisper lines and far less memory on this machine.
- The gas in s25 is exact bouncing motion in closed form, so no Taichi bake is needed.

## Credits required
The harbor photo in s01 is CC BY 3.0: credit Citizen59 in the video description. Full list: `assets/photos/CREDITS.md`.

## Open decisions
1. The pasted brief ended mid-sentence at "Level curves, level surfaces, and their". Anything after that is not reflected here.
