"""Procedural point-cloud tunnel. Taichi computes the geometry; the result is cached as out/tunnel_<hash>.npz.

    uv run python lab/2026-11-15-pointcloud-tunnel/tunnel.py        # build + stats

Tunnel runs along -Z (s = -z). Cross-section in cylindrical coords around a wandering centerline c(s):
    r(θ, s) = R0(s) · (1 + fbm(cosθ, sinθ, s))      x = cx(s) + r cosθ,  y = cy(s) + r sinθ,  z = -s
The bottom arc is flattened into a floor; the upper walls grow noisy foliage clumps (with depth, tinted green);
tree trunks line both sides; a density field cuts holes so the walls read as a fragmented LiDAR scan.
The same cx/cy/R0/floor_y formulas live in shaders/common.glsl (twist) and render.py (camera); keep them in sync.
"""


import hashlib
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

L_TUN = 115.0          # tunnel length (s from -6 to L_TUN-6)
N_SURF = 1_500_000     # surface samples before density rejection
N_DUST = 45_000        # volumetric particles
TRUNK_SPACING = 3.1
N_TRUNK = int(L_TUN / TRUNK_SPACING) + 2
SEED = 7

# kinds (attr.w)
WALL, FLOOR, TRUNK, DUST = 0.0, 1.0, 2.0, 3.0


# ── centerline (numpy twin of the taichi/glsl versions) ─────────────────────
def cx(s):
    return 1.8 * np.sin(0.045 * s) + 0.6 * np.sin(0.13 * s + 1.0)


def cy(s):
    return 0.5 * np.sin(0.07 * s + 2.0)


def R0(s):
    return 3.2 + 0.7 * np.sin(0.06 * s + 0.5)


def floor_y(s):
    return cy(s) - 0.55 * R0(s)


def _build_surface(u):
    import taichi as ti
    ti.init(arch=ti.cpu, cpu_max_num_threads=2, log_level=ti.WARN, offline_cache=True)
    vec3 = ti.math.vec3
    TAU = 6.283185307

    @ti.func
    def h3(p):
        return ti.math.fract(ti.sin(p.x * 127.1 + p.y * 311.7 + p.z * 74.7) * 43758.5453)

    @ti.func
    def vnoise(p):
        i = ti.floor(p)
        f = p - i
        w = f * f * (3.0 - 2.0 * f)
        a = ti.math.mix(h3(i), h3(i + vec3(1, 0, 0)), w.x)
        b = ti.math.mix(h3(i + vec3(0, 1, 0)), h3(i + vec3(1, 1, 0)), w.x)
        c = ti.math.mix(h3(i + vec3(0, 0, 1)), h3(i + vec3(1, 0, 1)), w.x)
        d = ti.math.mix(h3(i + vec3(0, 1, 1)), h3(i + vec3(1, 1, 1)), w.x)
        return ti.math.mix(ti.math.mix(a, b, w.y), ti.math.mix(c, d, w.y), w.z)

    @ti.func
    def fbm(p):
        v, a, tot = 0.0, 0.5, 0.0
        q = p
        for _ in ti.static(range(4)):
            v += a * vnoise(q)
            tot += a
            q = q * 2.03 + vec3(17.1, 9.2, 3.7)
            a *= 0.5
        return v / tot

    @ti.func
    def sstep(e0, e1, x):
        t = ti.math.clamp((x - e0) / (e1 - e0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    @ti.func
    def tcx(s):
        return 1.8 * ti.sin(0.045 * s) + 0.6 * ti.sin(0.13 * s + 1.0)

    @ti.func
    def tcy(s):
        return 0.5 * ti.sin(0.07 * s + 2.0)

    @ti.func
    def tR0(s):
        return 3.2 + 0.7 * ti.sin(0.06 * s + 0.5)

    @ti.kernel
    def gen(u: ti.types.ndarray(dtype=ti.f32, ndim=2), out: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i in range(u.shape[0]):
            u0, u1, u2, u3, u4, u5, u6 = u[i, 0], u[i, 1], u[i, 2], u[i, 3], u[i, 4], u[i, 5], u[i, 6]
            pos = vec3(0.0)
            nrm = vec3(0.0, 1.0, 0.0)
            alb, grn, size, kind, keep = 0.4, 0.0, 1.0, 0.0, 1.0
            if u6 < 0.075:
                # ── tree trunk (vertical cylinder at the tunnel side, flared root, lean, a few branches)
                k = ti.floor(u1 * N_TRUNK)
                kv = vec3(k, 0.0, 0.0)
                sk = k * TRUNK_SPACING - 6.0 + (h3(kv + vec3(0, 1, 0)) - 0.5) * 1.6
                side = 1.0 if h3(kv + vec3(0, 2, 0)) > 0.5 else -1.0
                if h3(kv + vec3(0, 3, 0)) < 0.3:
                    keep = 0.0
                base = vec3(tcx(sk) + side * tR0(sk) * (0.72 + 0.12 * h3(kv + vec3(0, 5, 0))),
                            tcy(sk) - 0.55 * tR0(sk), -sk)
                hgt = tR0(sk) * (1.15 + 0.3 * h3(kv + vec3(0, 6, 0)))
                lean = -side * (0.25 + 0.4 * h3(kv + vec3(0, 7, 0)))
                rt = 0.11 + 0.09 * h3(kv + vec3(0, 4, 0))
                if u5 < 0.22:
                    # branch: from trunk height 45–90% arcing inward/up over the path
                    t0 = 0.45 + 0.45 * h3(kv + vec3(ti.floor(u4 * 3.0), 8, 0))
                    j = ti.floor(u4 * 3.0)
                    ang = TAU * h3(kv + vec3(j, 9, 0))
                    st = vec3(base.x + lean * t0, base.y + hgt * t0, base.z)
                    d = ti.math.normalize(vec3(-side * 0.8, 0.55, ti.cos(ang) * 0.6))
                    bl = 0.8 + 1.4 * h3(kv + vec3(j, 10, 0))
                    tt = u2
                    c = st + d * bl * tt + vec3(0, -0.25 * tt * tt * bl, 0)
                    br = rt * 0.45 * (1.0 - 0.7 * tt)
                    a2 = TAU * u3
                    o = vec3(ti.cos(a2), ti.sin(a2), 0.0)
                    pos = c + o * br
                    nrm = o
                else:
                    t = u2
                    flare = 1.0 + 1.6 * ti.exp(-9.0 * t)
                    a = TAU * u3
                    o = vec3(ti.cos(a), 0.0, ti.sin(a))
                    rr = rt * flare * (1.0 + 0.25 * (fbm(vec3(a * 1.5, t * 6.0, k)) - 0.5))
                    pos = vec3(base.x + lean * t * t, base.y + hgt * t, base.z) + o * rr
                    nrm = o
                    if t > 0.97:
                        keep = 0.0
                alb = 0.55 + 0.25 * vnoise(pos * 5.0)
                grn = 0.12
                kind = 2.0
            else:
                s = u0 * L_TUN - 6.0
                th = TAU * u1
                c, sn = ti.cos(th), ti.sin(th)
                n1 = fbm(vec3(c * 1.4, sn * 1.4, s * 0.12))
                n2 = fbm(vec3(c * 4.3, sn * 4.3, s * 0.45) + 5.0)
                r0 = tR0(s)
                r = r0 * (1.0 + 0.5 * (n1 - 0.5) + 0.16 * (n2 - 0.5))
                upper = sstep(-0.15, 0.45, sn)
                fol = upper * sstep(0.42, 0.66, fbm(vec3(c * 2.6, sn * 2.6, s * 0.33) + 11.0))
                r -= fol * (0.2 + 1.5 * u4 * u4)                     # foliage has depth (hangs inward)
                ccx, ccy = tcx(s), tcy(s)
                x = ccx + r * c
                y = ccy + r * sn
                fy = ccy - 0.55 * r0
                d = fbm(vec3(c * 2.2, sn * 2.2, s * 0.22) + 31.0)
                if y < fy + 0.04:
                    # floor: bottom arc flattened; brighter, smoother path in the middle
                    lat = ti.abs(x - ccx)
                    bump = 0.18 * (fbm(vec3(x * 0.9, s * 0.9, 3.0)) - 0.5) + 0.04 * (vnoise(vec3(x * 9, s * 9, 1)) - 0.5)
                    y = fy + bump * sstep(0.6, 2.0, lat) + 0.015 * (vnoise(vec3(x * 14, s * 14, 2)) - 0.5)
                    path = 1.0 - sstep(0.7, 1.6, lat + 0.5 * (n2 - 0.5))
                    kind = 1.0
                    alb = 0.38 + 0.5 * path + 0.15 * (n2 - 0.5)
                    keep = 0.5 + 0.5 * sstep(0.2, 0.5, d) if path < 0.5 else 1.0
                    keep *= 0.75   # floor arc is compressed → too dense otherwise
                    nrm = vec3(0.0, 1.0, 0.0)
                else:
                    kind = 0.0
                    alb = 0.28 + 0.35 * n2
                    keep = sstep(0.32, 0.56, d) * (0.85 + 0.15 * fol) + 0.12 * fol
                    nrm = vec3(-c, -sn, 0.0)
                    grn = fol * (0.6 + 0.4 * n1)
                pos = vec3(x, y, -s)
            if u5 > 0.9965:
                size, alb = 2.4, alb * 2.6   # sparkle: brighter, larger square
            if u[i, 3] > keep and kind != 2.0:
                keep = 0.0
            elif kind != 2.0:
                keep = 1.0
            out[i, 0], out[i, 1], out[i, 2] = pos.x, pos.y, pos.z
            out[i, 3], out[i, 4], out[i, 5] = nrm.x, nrm.y, nrm.z
            out[i, 6], out[i, 7], out[i, 8], out[i, 9] = alb, grn, size, kind
            out[i, 10] = keep

    out = np.zeros((len(u), 11), np.float32)
    gen(u, out)
    ti.reset()
    return out


def _build_dust(rng):
    n = N_DUST
    s = rng.uniform(-6, L_TUN - 6, n)
    th = rng.uniform(0, 2 * np.pi, n)
    rr = np.sqrt(rng.uniform(0, 1, n)) * R0(s) * 0.85
    x = cx(s) + rr * np.cos(th)
    y = np.maximum(cy(s) + rr * np.sin(th), floor_y(s) + 0.1)
    size = rng.choice([1.0, 1.6, 2.4, 3.4], n, p=[0.55, 0.25, 0.14, 0.06]) * rng.uniform(0.85, 1.15, n)
    alb = rng.uniform(0.5, 1.3, n)
    out = np.zeros((n, 11), np.float32)
    out[:, 0], out[:, 1], out[:, 2] = x, y, -s
    out[:, 6], out[:, 8], out[:, 9], out[:, 10] = alb, size, DUST, 1
    out[:, 7] = rng.uniform(0, 1, n)   # phase for drift
    return out


def _build_rails():
    """Perspective floor lines along the tunnel, as GL_LINES pairs: (x, y, z, s, lane)."""
    offs = np.arange(-11, 12) * 0.24
    ss = np.arange(-6, L_TUN - 6, 0.5)
    segs = []
    for j, o in enumerate(offs):
        x = cx(ss) + o
        y = floor_y(ss) + 0.012
        pts = np.c_[x, y, -ss, ss, np.full_like(ss, j)]
        seg = np.stack([pts[:-1], pts[1:]], 1).reshape(-1, 5)
        segs.append(seg)
    return np.concatenate(segs).astype(np.float32)


def build():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    u = rng.uniform(0, 1, (N_SURF, 7)).astype(np.float32)
    surf = _build_surface(u)
    surf = surf[surf[:, 10] > 0.5]
    dust = _build_dust(rng)
    rails = _build_rails()
    print(f"surface {len(surf):,} pts  dust {len(dust):,}  rail segs {len(rails) // 2:,}  ({time.time() - t0:.1f}s)")
    for k, name in [(WALL, "wall"), (FLOOR, "floor"), (TRUNK, "trunk")]:
        print(f"  {name:6s} {(surf[:, 9] == k).sum():,}")
    return dict(surf=surf[:, :10].copy(), dust=dust[:, :10].copy(), rails=rails)


def cached():
    key = hashlib.sha1((HERE / "tunnel.py").read_bytes()).hexdigest()[:10]
    path = OUT / f"tunnel_{key}.npz"
    if path.exists():
        z = np.load(path)
        return {k: z[k] for k in z.files}
    P = build()
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("tunnel_*.npz"):
        old.unlink()
    np.savez(path, **P)
    return P


if __name__ == "__main__":
    cached()
