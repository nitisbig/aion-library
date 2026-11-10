"""Simulation baking: run a sim once, cache every sample, read it back as a pure f(t).

    sim = NBody(n=400, seed=3)                       # any Sim subclass
    cache = bake(sim, start=T.a, end=T.b, rate=60)   # cached .npz (re-runs only if code/params change)
    cache.at(t)["pos"]                               # (n, 2|3) interpolated at time t

Write your own: subclass Sim, set `fields`, implement `setup()` and `step(dt)`
(numpy or Taichi), and `sample()` returning {field: array}. Determinism comes
from `seed`; physics substeps come from `substeps` per output sample.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from aion import cache
from aion.progress import Progress

__all__ = ["Sim", "SimCache", "bake"]


class Sim:
    """Base simulation. Params are constructor kwargs (stored for the cache key).

    Example:
        class Drop(Sim):
            fields = ("pos",)
            def setup(self): self.x = np.zeros((1, 2)); self.v = np.zeros((1, 2))
            def step(self, dt): self.v[:, 1] -= 9.8 * dt; self.x += self.v * dt
            def sample(self): return {"pos": self.x.copy()}
    """

    fields: tuple[str, ...] = ()
    substeps: int = 4

    def __init__(self, seed: int = 0, **params):
        self.seed = seed
        self.params = params
        for k, v in params.items():
            setattr(self, k, v)

    def setup(self) -> None:
        raise NotImplementedError

    def step(self, dt: float) -> None:
        raise NotImplementedError

    def sample(self) -> dict[str, np.ndarray]:
        raise NotImplementedError

    def cache_key(self):
        src = inspect.getsource(type(self)) if not type(self).__module__.startswith("scenes_") else \
            Path(inspect.getfile(type(self))).read_text()
        return [type(self).__name__, src, self.seed, self.params, self.substeps]


@dataclass
class SimCache:
    """Baked samples: arrays shaped (n_samples, ...) on a regular time grid.

    Example:
        h = waves.at(T.drop + 0.5)["h"]
    """

    data: dict[str, np.ndarray]
    start: float
    rate: float

    @property
    def end(self) -> float:
        n = len(next(iter(self.data.values())))
        return self.start + (n - 1) / self.rate

    def at(self, t: float) -> dict[str, np.ndarray]:
        """Linear interpolation between samples; clamped outside [start, end]."""
        n = len(next(iter(self.data.values())))
        x = min(max((t - self.start) * self.rate, 0.0), n - 1)
        i = int(np.floor(x))
        j = min(i + 1, n - 1)
        u = x - i
        return {k: (v[i] if u < 1e-9 or i == j else (1 - u) * v[i].astype(np.float32) + u * v[j])
                for k, v in self.data.items()}

    def __getitem__(self, k):
        return self.data[k]


def bake(sim: Sim, start: float, end: float, rate: float = 60, name: str | None = None) -> SimCache:
    """Run `sim` from `start` to `end`, sampling `rate` times per second (cached).

    Example:
        flow = bake(Particles(n=30000, seed=1), s.start, s.end)
    """
    n = int(round((end - start) * rate)) + 1

    def make(tmp: Path):
        np.random.seed(sim.seed)
        sim.setup()
        dt = 1.0 / (rate * sim.substeps)
        out: dict[str, list] = {f: [] for f in sim.fields}
        with Progress(name or f"bake-{type(sim).__name__}", n, unit="smp") as bar:
            for k in range(n):
                if k:
                    for _ in range(sim.substeps):
                        sim.step(dt)
                s = sim.sample()
                for f in sim.fields:
                    out[f].append(np.asarray(s[f]))
                bar.update()
        with open(tmp, "wb") as fh:
            np.savez_compressed(fh, **{f: np.stack(v).astype(np.float32) for f, v in out.items()})

    p = cache.get_or_make("sim", [sim, round(start, 6), round(end, 6), rate], make, ".npz")
    with np.load(p) as z:
        data = {k: z[k] for k in z.files}
    return SimCache(data, start, rate)
