# Recipes: concept → technique

Pick the cheapest technique that makes the idea visible.

| concept | technique | layers |
|---|---|---|
| linear map / matrix | `ApplyMatrix` on `NumberPlane` + basis arrows; matrix as `key(T.x, I, A)` for shaders | manim |
| eigenvectors | as above + lines along eigenvectors that stay put while the plane shears; `Indicate` on λ | manim |
| derivative | secant → tangent with `redraw(lambda t: secant(h(t)))`, `h = key(T.limit, 1, 0.01)`, camera `push` into the point | manim + camera |
| integral / area | `ax.get_riemann_rectangles` via `redraw` with dx from a Track, then `get_area` | manim |
| Fourier series | `aion.maths.fourier` coefficients → epicycles via `drive`; trail via `redraw` of a computed path | manim + Glow |
| complex functions | `layers/domain_coloring.frag` with `u_theta`/`u_unit` tracks + Manim grid overlay | shader + manim |
| gradient descent | height field shader (or `FieldLayer` of f) + contours + a dot whose path is precomputed with numpy | field + manim |
| heat / wave PDE | `bake(Heat2D/Wave2D)` → `FieldLayer(contours=…)`, with the equation in Manim | sim + field |
| gravity / orbits | `bake(NBody)` → `PointsLayer(additive, glow)` + Bloom | sim + points |
| phase space / flows | `bake(Particles)` or numpy RK4 trajectories → `PointsLayer(values=speed, cmap)` | points |
| convolution | two `ax.plot`s, the sliding one via `drive`, the product area via `redraw`, result traced live | manim |
| neural network | `VGroup` of nodes/edges; activations as edge opacity `drive`; Glow on active path | manim + Glow |
| probability / sampling | seeded `rng(seed)` samples → `PointsLayer`; histogram bars `redraw`n from counts up to t | points + manim |

## Patterns
- **Limit process:** drive the parameter with `key(T.x, a, b, ease="easy_ease")` or `Clock` and redraw
  the construction from it. Pair it with a camera push towards the point where things converge.
- **"Notice this":** `pulse(T.notice)` on a Glow strength, or `Indicate`, plus a dim on everything else
  (`opacity=key(T.notice, 1, 0.35)` on the other layer).
- **Equation ↔ picture link:** same `C.*` color for a term and its object; `Indicate` both on the same beat.
- **Reveal complexity gradually:** add layers on successive beats; never show the final picture first.
