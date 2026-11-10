# ManimLayer: Manim as a score, not a script

`m = s.manim()` gives a transparent layer rendered by Manim's Cairo camera **inside aion's clock**.
You don't call `self.play` or `self.wait`. You write a *score*: events placed at absolute beat times.
Any frame can be evaluated directly, holds are deduplicated, and render chunks run in parallel.

```python
m = s.manim(z=0)
ax = Axes(x_range=[-3, 3], y_range=[-1, 9], x_length=8, y_length=5)
f = ax.plot(lambda x: x**2, color=C.fx)
m.add(ax)                                         # present from the scene start
m.play(Create(f), at=T.curve, dur=1.2)            # lands on the beat (starts lead earlier)
m.seq(at=T.eq).play(Write(eq)).wait(0.3).play(Indicate(eq.part("x")))
m.drive(dot, lambda d, t: d.move_to(ax.c2p(x(t), x(t)**2)), during=(T.slide, T.slide.end))
m.redraw(lambda t: ax.get_secant_slope_group(x(t), f, dx=h(t)), during=(T.a, T.b))
m.play(FadeOut(VGroup(ax, f)), at=T.cut2 - 0.6)
m.remove(ax, f, at=T.cut2)
```

| call | effect |
|---|---|
| `add(*mobs, at=-inf)` | add (exact time, no lead) |
| `remove(*mobs, at=)` | remove |
| `play(*anims, at=, dur=None, ease=None, lead=None) → end` | any Manim Animation: Transform, TransformMatchingTex, LaggedStart, `.animate`, Succession… `dur` defaults to the animation's run_time, `ease` to its rate_func |
| `seq(at=)` → `.play(...)`, `.wait(s)`, `.end` | chained plays, each starting when the previous ends (or at its own `at=`) |
| `drive(mob, fn(mob, t), during=)` | set state from t each frame (replaces updaters). Must be absolute: set positions, don't increment |
| `redraw(fn(t) → Mobject, during=)` | rebuild a mobject from t each frame (always_redraw replacement) |

## Rules
- **No `add_updater`, no `always_redraw`.** They carry state between frames and break random access.
  `aion audit --source` flags them.
- `drive`/`redraw` functions must be pure in `t`, so recompute positions from scratch every call.
- One built score evaluates **forward only** (`BackwardSeek` otherwise). Stills, chunks and workers each build
  a fresh score from the scene function, so any frame is still reachable directly.
- Put rarely changing things (grids, axes) and busy things in **separate layers** when a scene is heavy:
  the static layer is rasterized once and reused while it holds.
- Colors and sizes come from `C.*` tokens (`Eqn`, `Label`, `Title` in `aion.components` apply them).

## Equations
```python
eq = Eqn(r"f(x) = x^2", colors={"x": C.x, "f(x)": C.fx})
m.play(Write(eq), at=T.eq)
m.play(Indicate(eq.part("f(x)")), at=T.fx)
```
`colors` keys are isolated as their own submobjects so they can be indexed, colored and transformed.
`TransformMatchingTex` works between `Eqn`s that share keys.

## Escape hatch
The global Manim `config` is set by aion for the render size. Plain Manim scenes for experiments in
`lab/` should inherit `aion.progress.ProgressScene` and run with `uv run manim -ql …`.
