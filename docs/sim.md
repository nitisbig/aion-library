# Simulations (Taichi, baked)

Physics runs **once** ahead of rendering and is stored in `.aion-cache/sim/*.npz`. Layers read
interpolated samples with `cache.at(t)`, so frames stay pure in `t` and parallel-safe. Taichi tries
Vulkan on the Radeon R4 first, then falls back to CPU.

```python
flow = bake(Particles(n=30000, flow=0.6, seed=1), s.start, s.end, rate=60)
s.add(PointsLayer(lambda t: flow.at(t)["pos"], values=lambda t: flow.at(t)["speed"], cmap="inferno"))
```
`bake(sim, start, end, rate=60)` caches by the sim's class source, its parameters, the time range and the rate. Change
any of them and it re-bakes with a progress bar. `cache.at(t)` returns a dict of arrays. Times outside the range clamp.

| sim | samples | notes |
|---|---|---|
| `Particles(n, flow, scale, gravity, drag, box, seed)` | `pos (n,2)`, `speed (n,)` | curl-noise flow; wraps in the frame box |
| `NBody(n, g, soft, radius, spin, dim, seed)` | `pos`, `vel` | leapfrog; `.energy()` for checks |
| `Wave2D(nx, ny, c, damping, drops, seed)` | `h (ny,nx)` | drops `(t_local, x_uv, y_uv, amp)`, CFL-safe substeps |
| `Heat2D(nx, ny, k, init, seed)` | `u (ny,nx)` | `init='spot'` or `'bars'` |
| `Springs(nx, ny, size, stiffness, gravity, wind, seed)` | `pos (nx·ny,2)` | cloth, top row pinned |

Times inside a sim (`drops`) are **local**: seconds since `start`. Write `T.drop - s.start`.

## Custom sims
```python
import numpy as np
from aion import Sim, bake

class Drop(Sim):
    fields = ("pos",)
    substeps = 4                       # steps per sample (raise for stiff systems)
    def setup(self):                   # constructor kwargs are attributes: Drop(g=9.8) → self.g
        self.x = np.zeros((1, 2)); self.v = np.zeros((1, 2))
    def step(self, dt):
        self.v[:, 1] -= self.g * dt; self.x += self.v * dt
    def sample(self):
        return {"pos": self.x.copy()}

cache = bake(Drop(g=9.8, seed=0), 0.0, 3.0)
```
`step` may use numpy or Taichi kernels. Do **not** add `from __future__ import annotations` to modules that
define Taichi kernels, because Taichi needs real annotation objects. Seed every RNG from `self.seed`.

## Showing fields and points
`FieldLayer(fn, cmap="diverging"|"inferno"|"viridis"|"ramp", vmin, vmax, contours=N, extent, center)`.
`PointsLayer(fn, values=, cmap=, color=, size=, glow=, additive=True)`. Both upload once per changed frame.
At 720p, 40k particles + field + cloth + bloom take ≈ 96 ms/frame on the R4.
