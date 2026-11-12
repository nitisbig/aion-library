"""Taichi bakes: caching, interpolation, physics sanity, GPU drawing."""

import numpy as np
import pytest

from aion.sim.bake import Sim, bake


@pytest.fixture(autouse=True)
def _cache(tmp_path, monkeypatch):
    from aion import cache

    monkeypatch.setattr(cache, "CACHE", tmp_path / "cache")


class Fall(Sim):
    fields = ("y",)
    substeps = 10

    def setup(self):
        self.yv, self.v = np.array([0.0]), np.array([0.0])

    def step(self, dt):
        self.v -= 9.8 * dt
        self.yv += self.v * dt

    def sample(self):
        return {"y": self.yv.copy()}


def test_numpy_sim_bake_and_interp():
    c = bake(Fall(), 1.0, 2.0, rate=50)
    assert abs(c.at(2.0)["y"][0] + 4.9) < 0.02        # y = -g t²/2 after 1 s
    assert c.at(0.0)["y"][0] == 0.0                     # clamped before start
    mid = c.at(1.51)["y"][0]
    assert c.at(1.50)["y"][0] > mid > c.at(1.52)["y"][0]


def test_bake_is_cached(monkeypatch):
    bake(Fall(), 0, 0.5)
    called = []
    monkeypatch.setattr(Fall, "setup", lambda self: called.append(1))
    bake(Fall(), 0, 0.5)
    assert not called


def test_nbody_energy_drift():
    from aion.sim.builtin import NBody

    sim = NBody(n=64, seed=1)
    c = bake(sim, 0, 2.0, rate=30)
    e0 = sim.energy(c.data["pos"][0], c.data["vel"][0])
    e1 = sim.energy(c.data["pos"][-1], c.data["vel"][-1])
    assert abs(e1 - e0) / abs(e0) < 0.02


@pytest.mark.gpu
def test_points_and_field_layers_render():
    from aion.comp.comp import Comp
    from aion.layers.points import FieldLayer, PointsLayer
    from aion.sim.builtin import Particles, Wave2D

    p = bake(Particles(n=2000, seed=2), 0, 0.5, rate=30)
    w = bake(Wave2D(nx=64, ny=36), 0, 0.5, rate=30)
    comp = Comp((160, 90), fps=30, background="#000000")
    comp.add(FieldLayer(lambda t: w.at(t)["h"], cmap="diverging", vmin=-0.2, vmax=0.2))
    comp.add(PointsLayer(lambda t: p.at(t)["pos"], size=2))
    img = comp.frame(0.4)
    assert img.std() > 5


@pytest.mark.gpu
def test_points_non_additive_overlap_keeps_last_colour():
    """Many overlapping points with additive=False show the last point's colour instead of saturating."""
    from aion.comp.comp import Comp
    from aion.layers.points import PointsLayer

    n = 400
    pos = np.zeros((n, 2))
    vals = np.zeros(n)
    vals[-1] = 1.0                                     # the last point drawn is the far end of the ramp

    def frame(additive):
        comp = Comp((320, 180), fps=30, background="#000000")
        comp.add(PointsLayer(lambda t: pos, values=lambda t: vals, cmap="ramp", vmin=0, vmax=1, size=40, glow=0,
                             colors=("#2040ff", "#808080", "#ff4020"), additive=additive))
        return comp.frame(0.0)[90, 160].astype(float)
    over, add = frame(False), frame(True)
    assert over[0] > over[2]                           # red end on top, not summed blue
    assert add.min() > 200                             # additive saturates toward white
