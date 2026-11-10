"""Lab check 3: 20k seeded sparks shed by a moving pen, curl-noise drift, cooling fade (Taichi)."""
import sys, time
import numpy as np
import taichi as ti

arch = sys.argv[1] if len(sys.argv) > 1 else "gpu"
ti.init(arch=getattr(ti, arch), random_seed=7, log_level=ti.ERROR)
print("taichi backend:", ti.lang.impl.current_cfg().arch)
N = 20_000
pos = ti.Vector.field(2, ti.f32, N); vel = ti.Vector.field(2, ti.f32, N); age = ti.field(ti.f32, N)
LIFE = 1.6


@ti.func
def curl(p, t):
    # analytic curl of a sum of sines: divergence-free swirl, cheap and deterministic
    a = ti.sin(1.7 * p.y + 0.6 * t) + 0.5 * ti.sin(3.1 * p.y - 1.3 * p.x + t)
    b = ti.sin(1.9 * p.x - 0.4 * t) + 0.5 * ti.sin(2.7 * p.x + 1.1 * p.y - t)
    return ti.Vector([a, -b])


@ti.kernel
def step(dt: ti.f32, t: ti.f32, px: ti.f32, py: ti.f32, emit_lo: ti.i32, emit_n: ti.i32):
    for i in pos:
        k = (i - emit_lo + N) % N
        if k < emit_n:                                   # respawn a ring-buffer slice at the pen
            pos[i] = ti.Vector([px, py]) + ti.Vector([ti.random() - 0.5, ti.random() - 0.5]) * 0.02
            vel[i] = ti.Vector([ti.random() - 0.5, ti.random() - 0.5]) * 0.8
            age[i] = 0.0
        elif age[i] < LIFE:
            vel[i] = vel[i] * 0.96 + curl(pos[i], t) * 0.35 * dt
            pos[i] += vel[i] * dt
            age[i] += dt


for i in range(N): age[i] = 99.0
emit, ptr, dt = 200, 0, 1 / 60
for k in range(30): step(dt, k * dt, 0.0, 0.0, ptr, emit); ptr = (ptr + emit) % N   # warm-up / JIT
ti.sync()
a = time.perf_counter()
for k in range(240):
    th = k * dt * 2.0
    step(dt, k * dt, 2 * np.cos(th), 2 * np.sin(th), ptr, emit); ptr = (ptr + emit) % N
    P = pos.to_numpy(); A = age.to_numpy()
ti.sync()
per = (time.perf_counter() - a) / 240
print(f"{N} particles: {1000*per:.2f} ms/step incl. readback")

# quick still: additive splat of the live particles, cooling gold → ember → gone
from PIL import Image
W, H = 960, 540
img = np.zeros((H, W, 3))
live = A < LIFE
x = (P[live, 0] / 3 * H / 2 + W / 2).astype(int); y = (H / 2 - P[live, 1] / 3 * H / 2).astype(int)
f = 1 - A[live] / LIFE
col = np.stack([np.ones_like(f), 0.55 + 0.3 * f, 0.15 + 0.1 * f], 1) * (f ** 1.5)[:, None] * 0.6
ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
np.add.at(img, (y[ok], x[ok]), col[ok])
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save("lab/2026-11-09-epicycles/taichi_sparks.png")
