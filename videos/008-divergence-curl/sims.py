"""Dust carried by the hero field: a baked particle sim (RK4, respawn with a soft fade in and out).

The hero field is analytic (shots.hero), so the sim is plain numpy RK4: a few thousand grains at 30 Hz bake in
seconds, cached by aion's `bake`. Positions are exact integrals of F (scaled by RATE); each grain lives a random
span, fading in and out, then respawns somewhere uniform in the frame, so sinks never pile up and sources never
empty.

    dust = hero_dust(T.start, T.cut_ch1)
    s.add(dust_layer(dust))
"""
import numpy as np

from aion import C, PointsLayer, Sim, bake
from shots import hero

RATE = 0.6                  # flow time scale: dust speed is RATE * |F| (calm, readable)
BOX = (7.5, 4.4)            # spawn box half-size (a little past the frame, so edges never empty)


class FlowSim(Sim):
    """Grains advected through shots.hero with RK4; samples `pos` (n, 2) float32 and `alpha` (n,) float32."""
    fields = ("pos", "alpha")
    substeps = 2

    def setup(self):
        self.rng = np.random.default_rng(self.seed)
        n = self.n
        self.p = self._spawn(n)
        self.life = self.rng.uniform(self.life_lo, self.life_hi, n)
        self.age = self.rng.uniform(0.0, 1.0, n) * self.life              # staggered, so nothing pops at t = 0

    def _spawn(self, k):
        return self.rng.uniform([-BOX[0], -BOX[1]], [BOX[0], BOX[1]], (k, 2))

    def _f(self, p):
        P, Q = hero(p[:, 0], p[:, 1])
        return RATE * np.stack([P, Q], 1)

    def step(self, dt):
        p = self.p
        k1 = self._f(p)
        k2 = self._f(p + dt / 2 * k1)
        k3 = self._f(p + dt / 2 * k2)
        k4 = self._f(p + dt * k3)
        self.p = p + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        self.age += dt
        dead = (self.age > self.life) | (np.abs(self.p[:, 0]) > BOX[0] + 0.3) | (np.abs(self.p[:, 1]) > BOX[1] + 0.3)
        if dead.any():
            k = int(dead.sum())
            self.p[dead] = self._spawn(k)
            self.age[dead] = 0.0
            self.life[dead] = self.rng.uniform(self.life_lo, self.life_hi, k)

    def sample(self):
        fade = np.minimum(1.0, np.minimum(self.age / 0.8, (self.life - self.age) / 0.8))
        return {"pos": self.p.astype(np.float32), "alpha": np.clip(fade, 0, 1).astype(np.float32)}


def hero_dust(start, end, n=3000, seed=8):
    """Bake the hero dust over [start, end] (30 samples a second; cached)."""
    return bake(FlowSim(n=n, life_lo=4.0, life_hi=9.0, seed=seed), start, end, rate=30, name="hero_dust")


def dust_layer(cache, opacity=1.0, z=2, size=2.2):
    """Crisp white grains: additive points, brightness = each grain's fade (no glow)."""
    return PointsLayer(lambda t: cache.at(t)["pos"], values=lambda t: cache.at(t)["alpha"], cmap="ramp",
                       colors=(C.bg, C.dust, C.dust), size=size, glow=0.0, z=z, opacity=opacity)
