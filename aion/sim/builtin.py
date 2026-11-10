"""Built-in simulations (Taichi kernels; Vulkan on the R4, CPU fallback).

    NBody(n=300, g=1.0)              gravitating bodies (leapfrog)          fields: pos, vel
    Particles(n=20000, flow=0.6)     curl-noise flow + gravity + drag       fields: pos, speed
    Wave2D(nx=256, ny=144, c=1.0)    wave equation on a grid (drops)        fields: h
    Heat2D(nx=256, ny=144, k=0.2)    diffusion on a grid                    fields: u
    Springs(nx=24, ny=16)            mass-spring cloth, pinned top row      fields: pos

Positions are in Manim units (frame ≈ 14.2 × 8), ready for PointsLayer.
"""

# no `from __future__ import annotations`: Taichi needs real annotation objects

import numpy as np

from aion.sim.bake import Sim

__all__ = ["NBody", "Particles", "Wave2D", "Heat2D", "Springs", "ti_init"]

_TI = {"ready": False}


def ti_init(arch: str = "auto"):
    """Initialise Taichi once (vulkan → cpu). Returns the taichi module."""
    import taichi as ti

    if not _TI["ready"]:
        archs = {"vulkan": [ti.vulkan], "cpu": [ti.cpu], "auto": [ti.vulkan, ti.cpu]}[arch]
        for a in archs:
            try:
                ti.init(arch=a, log_level=ti.ERROR, random_seed=0, offline_cache=True)
                break
            except Exception:
                continue
        _TI["ready"] = True
    return ti


class NBody(Sim):
    """Softened Newtonian gravity in 2D (or 3D with dim=3), leapfrog integrator.

    Example:
        sky = bake(NBody(n=400, seed=2), s.start, s.end)
        s.add(PointsLayer(lambda t: sky.at(t)["pos"], additive=True, glow=0.8))
    """

    fields = ("pos", "vel")
    substeps = 8

    def __init__(self, n: int = 256, g: float = 0.6, soft: float = 0.08, radius: float = 3.0, spin: float = 0.6,
                 dim: int = 2, seed: int = 0):
        super().__init__(seed, n=n, g=g, soft=soft, radius=radius, spin=spin, dim=dim)

    def setup(self):
        ti = ti_init()
        rng = np.random.default_rng(self.seed)
        r = self.radius * np.sqrt(rng.random(self.n))
        a = rng.random(self.n) * 2 * np.pi
        p = np.zeros((self.n, self.dim), np.float32)
        p[:, 0], p[:, 1] = r * np.cos(a), r * np.sin(a)
        v = np.zeros_like(p)
        v[:, 0], v[:, 1] = -np.sin(a) * self.spin * np.sqrt(r), np.cos(a) * self.spin * np.sqrt(r)
        self.x = ti.Vector.field(self.dim, ti.f32, self.n)
        self.v = ti.Vector.field(self.dim, ti.f32, self.n)
        self.f = ti.Vector.field(self.dim, ti.f32, self.n)
        self.x.from_numpy(p)
        self.v.from_numpy(v)
        n, g, eps2 = self.n, self.g / self.n, self.soft ** 2
        x, vv, f = self.x, self.v, self.f

        @ti.kernel
        def forces():
            for i in range(n):
                acc = ti.Vector.zero(ti.f32, x.n)
                for j in range(n):
                    d = x[j] - x[i]
                    acc += g * d / (d.norm_sqr() + eps2) ** 1.5
                f[i] = acc

        @ti.kernel
        def kick(dt: ti.f32):
            for i in range(n):
                vv[i] += f[i] * dt

        @ti.kernel
        def drift(dt: ti.f32):
            for i in range(n):
                x[i] += vv[i] * dt

        self._forces, self._kick, self._drift = forces, kick, drift
        forces()

    def step(self, dt):
        self._kick(dt * 0.5)
        self._drift(dt)
        self._forces()
        self._kick(dt * 0.5)

    def sample(self):
        return {"pos": self.x.to_numpy(), "vel": self.v.to_numpy()}

    def energy(self, pos, vel) -> float:
        """Total energy (for drift checks)."""
        g = self.g / self.n
        ke = 0.5 * (vel ** 2).sum()
        d = pos[:, None, :] - pos[None, :, :]
        r = np.sqrt((d ** 2).sum(-1) + self.soft ** 2)
        pe = -0.5 * g * (1 / r).sum() + 0.5 * g * self.n / self.soft
        return float(ke + pe)


class Particles(Sim):
    """Many particles advected by curl noise + gravity + drag, wrapped in the frame box.

    Example:
        flow = bake(Particles(n=30000, flow=0.6, seed=1), s.start, s.end)
        s.add(PointsLayer(lambda t: flow.at(t)["pos"], values=lambda t: flow.at(t)["speed"], cmap="inferno"))
    """

    fields = ("pos", "speed")
    substeps = 2

    def __init__(self, n: int = 20000, flow: float = 0.6, scale: float = 0.35, gravity: float = 0.0,
                 drag: float = 0.6, box=(7.1, 4.0), seed: int = 0):
        super().__init__(seed, n=n, flow=flow, scale=scale, gravity=gravity, drag=drag, box=tuple(box))

    def setup(self):
        ti = ti_init()
        rng = np.random.default_rng(self.seed)
        bx, by = self.box
        p = np.stack([rng.uniform(-bx, bx, self.n), rng.uniform(-by, by, self.n)], 1).astype(np.float32)
        self.x = ti.Vector.field(2, ti.f32, self.n)
        self.v = ti.Vector.field(2, ti.f32, self.n)
        self.x.from_numpy(p)
        self.v.from_numpy(np.zeros_like(p))
        self.time = ti.field(ti.f32, ())
        n, flow, sc, grav, drag = self.n, self.flow, self.scale, self.gravity, self.drag
        x, v, tm = self.x, self.v, self.time

        @ti.func
        def pot(q, t):
            return ti.sin(q.x * 1.3 + t * 0.4) * ti.cos(q.y * 1.7 - t * 0.3) + 0.5 * ti.sin((q.x + q.y) * 2.1 + t)

        @ti.kernel
        def step(dt: ti.f32):
            t = tm[None]
            for i in range(n):
                q = x[i] * sc
                e = 1e-3
                dpx = (pot(q + ti.Vector([e, 0.0]), t) - pot(q - ti.Vector([e, 0.0]), t)) / (2 * e)
                dpy = (pot(q + ti.Vector([0.0, e]), t) - pot(q - ti.Vector([0.0, e]), t)) / (2 * e)
                target = flow * ti.Vector([dpy, -dpx]) + ti.Vector([0.0, -grav])
                v[i] += (target - v[i]) * ti.min(1.0, drag * dt * 10)
                x[i] += v[i] * dt
                if x[i].x > bx: x[i].x -= 2 * bx
                if x[i].x < -bx: x[i].x += 2 * bx
                if x[i].y > by: x[i].y -= 2 * by
                if x[i].y < -by: x[i].y += 2 * by
            tm[None] = t + dt

        self._step = step

    def step(self, dt):
        self._step(dt)

    def sample(self):
        v = self.v.to_numpy()
        return {"pos": self.x.to_numpy(), "speed": np.linalg.norm(v, axis=1)}


class _Grid(Sim):
    def __init__(self, nx=256, ny=144, seed=0, **kw):
        super().__init__(seed, nx=nx, ny=ny, **kw)


class Wave2D(_Grid):
    """Damped wave equation; `drops` = [(t, x_uv, y_uv, amp)] pluck the surface.

    Example:
        waves = bake(Wave2D(drops=[(T.drop - s.start, 0.5, 0.5, 1.0)]), s.start, s.end)
        s.add(FieldLayer(lambda t: waves.at(t)["h"], cmap="diverging", vmin=-0.2, vmax=0.2))
    """

    fields = ("h",)
    substeps = 6

    def __init__(self, nx=256, ny=144, c: float = 0.45, damping: float = 0.15, drops=((0.0, 0.5, 0.5, 1.0),),
                 seed: int = 0):
        super().__init__(nx, ny, seed, c=c, damping=damping, drops=tuple(map(tuple, drops)))

    def setup(self):
        ti = ti_init()
        self.h = ti.field(ti.f32, (self.nx, self.ny))
        self.hp = ti.field(ti.f32, (self.nx, self.ny))
        self.hn = ti.field(ti.f32, (self.nx, self.ny))
        self.t, self._done = 0.0, set()
        nx, ny, c, damp = self.nx, self.ny, self.c, self.damping
        h, hp, hn = self.h, self.hp, self.hn

        @ti.kernel
        def step(dt: ti.f32):
            k = (c * dt * nx) ** 2
            for i, j in h:
                if 0 < i < nx - 1 and 0 < j < ny - 1:
                    lap = h[i + 1, j] + h[i - 1, j] + h[i, j + 1] + h[i, j - 1] - 4 * h[i, j]
                    hn[i, j] = (2 * h[i, j] - hp[i, j] * (1 - damp * dt) + k * lap) / (1 + damp * dt)
                else:
                    hn[i, j] = 0.0
            for i, j in h:
                hp[i, j] = h[i, j]
                h[i, j] = hn[i, j]

        @ti.kernel
        def drop(cx: ti.f32, cy: ti.f32, amp: ti.f32):
            for i, j in h:
                d2 = (i - cx) ** 2 + (j - cy) ** 2
                bump = amp * ti.exp(-d2 / 18.0)
                h[i, j] += bump      # displaced at rest: add to both time levels
                hp[i, j] += bump

        self._step, self._drop = step, drop

    def step(self, dt):
        for k, (t, x, y, a) in enumerate(self.drops):
            if k not in self._done and self.t >= t:
                self._drop(x * self.nx, y * self.ny, a)
                self._done.add(k)
        # CFL: c·dt/dx must stay below 1/√2 in 2D; subdivide the step to keep it ≤ 0.5
        n = max(1, int(np.ceil(self.c * dt * max(self.nx, self.ny) / 0.5)))
        for _ in range(n):
            self._step(dt / n)
        self.t += dt

    def sample(self):
        return {"h": self.h.to_numpy().T}   # (ny, nx), row 0 = bottom


class Heat2D(_Grid):
    """Explicit heat diffusion from an initial hot pattern (`init`: 'spot' | 'bars').

    Example:
        heat = bake(Heat2D(init="bars", k=0.3), s.start, s.end)
        s.add(FieldLayer(lambda t: heat.at(t)["u"], cmap="inferno"))
    """

    fields = ("u",)
    substeps = 8

    def __init__(self, nx=256, ny=144, k: float = 0.2, init: str = "spot", seed: int = 0):
        super().__init__(nx, ny, seed, k=k, init=init)

    def setup(self):
        ti = ti_init()
        yy, xx = np.mgrid[0:self.ny, 0:self.nx]
        if self.init == "bars":
            u0 = ((xx // (self.nx // 8)) % 2).astype(np.float32)
        else:
            u0 = np.exp(-((xx - self.nx / 2) ** 2 + (yy - self.ny / 2) ** 2) / (0.02 * self.nx ** 2)).astype(np.float32)
        self.u = ti.field(ti.f32, (self.nx, self.ny))
        self.un = ti.field(ti.f32, (self.nx, self.ny))
        self.u.from_numpy(u0.T.copy())
        nx, ny, kk = self.nx, self.ny, self.k
        u, un = self.u, self.un

        @ti.kernel
        def step(dt: ti.f32):
            a = ti.min(kk * dt * nx * nx / 100.0, 0.24)
            for i, j in u:
                l = u[ti.max(i - 1, 0), j] + u[ti.min(i + 1, nx - 1), j] + u[i, ti.max(j - 1, 0)] + \
                    u[i, ti.min(j + 1, ny - 1)] - 4 * u[i, j]
                un[i, j] = u[i, j] + a * l
            for i, j in u:
                u[i, j] = un[i, j]

        self._step = step

    def step(self, dt):
        self._step(dt)

    def sample(self):
        return {"u": self.u.to_numpy().T}


class Springs(Sim):
    """Mass-spring cloth (structural + shear springs), Verlet, top row pinned, wind gusts.

    Example:
        cloth = bake(Springs(wind=2.0), s.start, s.end)
        s.add(PointsLayer(lambda t: cloth.at(t)["pos"], size=4))
    """

    fields = ("pos",)
    substeps = 12

    def __init__(self, nx: int = 24, ny: int = 16, size=(6.0, 4.0), stiffness: float = 900.0, gravity: float = 4.0,
                 wind: float = 1.2, seed: int = 0):
        super().__init__(seed, nx=nx, ny=ny, size=tuple(size), stiffness=stiffness, gravity=gravity, wind=wind)

    def setup(self):
        ti = ti_init()
        nx, ny = self.nx, self.ny
        w, h = self.size
        gx, gy = np.meshgrid(np.linspace(-w / 2, w / 2, nx), np.linspace(h / 2, -h / 2, ny))
        p = np.stack([gx.ravel(), gy.ravel()], 1).astype(np.float32) + np.array([0, 1.0], np.float32)
        self.x = ti.Vector.field(2, ti.f32, nx * ny)
        self.xp = ti.Vector.field(2, ti.f32, nx * ny)
        self.x.from_numpy(p)
        self.xp.from_numpy(p)
        self.time = ti.field(ti.f32, ())
        self.f = ti.Vector.field(2, ti.f32, nx * ny)
        rest = float(w / (nx - 1))
        ks, grav, wind = float(self.stiffness), float(self.gravity), float(self.wind)
        x, xp, tm, f = self.x, self.xp, self.time, self.f

        @ti.kernel
        def step(dt: ti.f32):
            t = tm[None]
            for idx in range(nx * ny):                       # forces (reads x only)
                i, j = idx % nx, idx // nx
                acc = ti.Vector([wind * (0.6 + 0.4 * ti.sin(t * 1.7 + i * 0.3)), -grav])
                for k in ti.static(range(8)):
                    di = ti.static([1, -1, 0, 0, 1, -1, 1, -1][k])
                    dj = ti.static([0, 0, 1, -1, 1, -1, -1, 1][k])
                    ii, jj = i + di, j + dj
                    if 0 <= ii < nx and 0 <= jj < ny:
                        d = x[jj * nx + ii] - x[idx]
                        L = rest * ti.static([1.0, 1.0, 1.0, 1.0, 1.41421356, 1.41421356, 1.41421356, 1.41421356][k])
                        acc += ks * (d.norm() - L) * d.normalized()
                f[idx] = acc
            for idx in range(nx * ny):                       # Verlet integrate, top row pinned
                if idx >= nx:
                    vel = (x[idx] - xp[idx]) * 0.995
                    xp[idx] = x[idx]
                    x[idx] = x[idx] + vel + f[idx] * dt * dt
            tm[None] = t + dt

        self._step = step

    def step(self, dt):
        self._step(dt)

    def sample(self):
        return {"pos": self.x.to_numpy()}
