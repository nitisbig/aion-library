"""Classical mechanics hobby piece: the physics engine.

Everything on screen comes from here. Each act is integrated with a small deterministic engine and
checked against the analytic answer (the asserts in `check()`). The results are sampled on a 1200 Hz
global grid and cached in out/sim.npz, keyed by this file's hash.

    uv run python lab/2026-11-04-physics-engine/physics.py        # simulate + run every check

Units: world units (the frame is ~8 tall at zoom 1), seconds, mass of the ball = 1.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

FS = 1200                       # global sample rate (Hz)
SUB = 10                        # integrator substeps per sample → dt = 1/12000 s
DT = 1.0 / (FS * SUB)
DURATION = 60.0
N = int(round(DURATION * FS)) + 1
T = np.arange(N) / FS

# ── scene parameters ────────────────────────────────────────────────────────
R = 0.24                        # ball radius (mass 1). Disc area ∝ mass → the 2m twin has radius √2·R
X0, Y0 = -5.2, 0.7              # where the spark ignites
T_SPARK = 0.4
V0 = 1.0                        # act 1: constant velocity
T_SPLIT0, T_SPLIT1 = 4.5, 5.2   # the 2m twin separates (visual only: same x, same v)
TWIN_DY = -2.1
T_F0, T_F1 = 5.4, 10.8          # act 2: constant applied force on both
F_APP = 0.45
T_G = 12.6                      # act 3: gravity on
G = 6.0
Y_FLOOR = -3.0
E_REST = 0.7                    # coefficient of restitution
V_STICK = 0.55                  # a bounce slower than this settles into rolling
T_SPRING = 20.0                 # act 4: the ball meets the spring (wall placed to make this exact)
L0 = 2.6                        # spring rest length
OMEGA = 2.32                    # √(k/m)
K = OMEGA ** 2
ZETA = 0.11                     # act 5: air drag (damping ratio) on during [T_D0, T_D1)
T_D0, T_D1 = 31.0, 34.6
C_DRAG = 2 * ZETA * OMEGA
CHAIN_N = 4                     # act 6: a row of equal masses
CHAIN_GAP = 0.35
CHAIN_LEAD = 0.9                # seconds from release to the first contact
K_CONTACT = 1500.0              # linear contact spring (contact lasts π/√(2k) ≈ 0.057 s)
T_EDGE = 40.5                   # act 7: the floor vanishes under the last ball → orbit
T_ORBIT = 6.0
ECC = 0.4
N_ORBITS = 2
T_PEND = T_EDGE + N_ORBITS * T_ORBIT   # act 8: the star becomes a pivot (52.5 s)
DP_DELTA = 1e-2                 # twin pendulums: outer-angle offsets ±δ (0.57°)
DP_L1 = 0.6                     # inner arm as a fraction of the ball's distance from the pivot

BODY_NAMES = ["hero", "twin", *[f"c{i}" for i in range(1, CHAIN_N + 1)],
              *[f"pin{k}" for k in range(3)], *[f"pout{k}" for k in range(3)]]
FORCES = ["app", "grav", "normal", "spring", "drag", "contact", "star"]


class Body:
    def __init__(self, name):
        self.name = name
        self.p = np.full((N, 2), np.nan)
        self.v = np.full((N, 2), np.nan)
        self.F = {k: np.zeros((N, 2)) for k in FORCES}


def idx(t):
    return int(round(t * FS))


# ── acts 1–3: constant-force motion with exact floor events ─────────────────
def run_kinematic(hero, twin, events):
    """Uniform force fields → the exact constant-acceleration step x += v·dt + ½a·dt², v += a·dt."""
    x = np.array([X0 - V0 * T_SPARK, Y0]); v = np.array([V0, 0.0])
    xt = x.copy(); vt = v.copy()
    rolling = False
    i_end = idx(T_SPRING)
    for i in range(i_end + 1):
        t = i / FS
        hero.p[i], hero.v[i] = x, v
        if t < T_G + 1.0:
            dy = TWIN_DY * smoothstep((t - T_SPLIT0) / (T_SPLIT1 - T_SPLIT0))
            twin.p[i], twin.v[i] = xt + [0.0, dy], vt
        app = F_APP if T_F0 <= t < T_F1 else 0.0
        hero.F["app"][i] = [app, 0.0]
        twin.F["app"][i] = [app, 0.0]
        if t >= T_G:
            hero.F["grav"][i] = [0.0, -G]
            if rolling:
                hero.F["normal"][i] = [0.0, G]
        if i == i_end:
            break
        for sub in range(SUB):
            ts = t + sub * DT
            tm = ts + 0.5 * DT                     # forces are piecewise constant on aligned steps
            a = np.array([F_APP if T_F0 <= tm < T_F1 else 0.0, -G if (tm >= T_G and not rolling) else 0.0])
            at = np.array([0.5 * a[0], 0.0])        # twin: same force, twice the mass
            xt, vt = xt + vt * DT + 0.5 * at * DT ** 2, vt + at * DT
            nx, nv = x + v * DT + 0.5 * a * DT ** 2, v + a * DT
            if not rolling and nx[1] < Y_FLOOR + R:
                # exact impact time inside the step: y + vy·τ + ½ay·τ² = floor
                aa, bb, cc = 0.5 * a[1], v[1], x[1] - (Y_FLOOR + R)
                tau = (-bb - np.sqrt(bb * bb - 4 * aa * cc)) / (2 * aa)
                xi, vi = x + v * tau + 0.5 * a * tau ** 2, v + a * tau
                events.append(("bounce", ts + tau, xi[0], -vi[1]))
                vi[1] = -E_REST * vi[1]
                if vi[1] < V_STICK:
                    vi[1] = 0.0; rolling = True
                    events.append(("roll", ts + tau, xi[0], 0.0))
                a2 = np.array([a[0], 0.0 if rolling else -G])
                rest = DT - tau
                nx, nv = xi + vi * rest + 0.5 * a2 * rest ** 2, vi + a2 * rest
            x, v = nx, nv
    return x, v


# ── acts 4–5: spring + drag (RK4) ───────────────────────────────────────────
def run_spring(hero, x_eq, x, v, events):
    """1D along x on the floor. Spring force −k(x − x_eq); drag −c·v during [T_D0, T_D1)."""
    def acc(t, X, V):
        c = C_DRAG if T_D0 <= t < T_D1 else 0.0
        return -K * (X - x_eq) - c * V

    X, V = x[0] - x_eq + x_eq, v[0]
    y = x[1]
    Q = 0.0
    i = idx(T_SPRING)
    energy = []
    released = None
    while released is None:
        t = i / FS
        c = C_DRAG if T_D0 <= t < T_D1 else 0.0
        hero.p[i], hero.v[i] = [X, y], [V, 0.0]
        hero.F["spring"][i] = [-K * (X - x_eq), 0.0]
        hero.F["drag"][i] = [-c * V, 0.0]
        hero.F["grav"][i] = [0.0, -G]; hero.F["normal"][i] = [0.0, G]
        energy.append((t, 0.5 * V * V, 0.5 * K * (X - x_eq) ** 2, Q))
        for s in range(SUB):
            ts = t + s * DT
            # RK4 on (X, V) and the heat Q = ∫ c·v² dt
            def f(tt, XX, VV):
                cc = C_DRAG if T_D0 <= tt < T_D1 else 0.0
                return VV, acc(tt, XX, VV), cc * VV * VV
            # drag switches on aligned sample boundaries, so evaluate c at the step midpoint
            tm = ts + 0.5 * DT
            g = lambda XX, VV: f(tm, XX, VV)  # noqa: E731
            k1 = g(X, V); k2 = g(X + 0.5 * DT * k1[0], V + 0.5 * DT * k1[1])
            k3 = g(X + 0.5 * DT * k2[0], V + 0.5 * DT * k2[1]); k4 = g(X + DT * k3[0], V + DT * k3[1])
            nX = X + DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            nV = V + DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            Q += DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
            if ts >= T_D1 + 0.15 and X >= x_eq > nX and nV < 0:
                # release exactly at the equilibrium crossing (spring force 0): interpolate in-step
                tau = (X - x_eq) / (X - nX) * DT
                released = (ts + tau, x_eq, nV)
                break
            X, V = nX, nV
        i += 1
    t_rel, x_rel, v_rel = released
    events.append(("release", t_rel, x_rel, v_rel))
    return t_rel, np.array([x_rel, y]), v_rel, np.array(energy)


# ── act 6: collisions through a row of equal masses (Verlet, contact springs) ─
def run_chain(bodies, t_rel, x_rel, v_rel, events):
    y = x_rel[1]
    xc1 = x_rel[0] - 2 * R - abs(v_rel) * CHAIN_LEAD
    X = np.array([x_rel[0], *[xc1 - k * (2 * R + CHAIN_GAP) for k in range(CHAIN_N)]])
    V = np.array([v_rel, *[0.0] * CHAIN_N])
    # advance from the (off-grid) release instant to the next grid sample at constant velocity
    i = int(np.ceil(t_rel * FS - 1e-9))
    X = X + V * (i / FS - t_rel)

    def forces(X):
        F = np.zeros_like(X)
        d = X[:-1] - X[1:]                     # body k is to the right of body k+1
        ov = np.maximum(2 * R - d, 0.0)
        F[:-1] += K_CONTACT * ov; F[1:] -= K_CONTACT * ov
        return F, ov

    names = ["hero", *[f"c{k}" for k in range(1, CHAIN_N + 1)]]
    # the row sits at rest from when it appears (act 5) until the ball arrives
    for k, nm in enumerate(names[1:], 1):
        b = bodies[nm]
        j0 = idx(T_D0)
        b.p[j0:i] = [X[k], y]; b.v[j0:i] = 0.0
    P0, E0 = V.sum(), 0.5 * (V * V).sum()
    Fc, ov = forces(X)
    in_contact = np.zeros(CHAIN_N, bool)
    i_end = idx(T_PEND)
    while i <= i_end:
        t = i / FS
        for k, nm in enumerate(names):
            b = bodies[nm]
            b.p[i], b.v[i] = [X[k], y], [V[k], 0.0]
            b.F["contact"][i] = [Fc[k], 0.0]
            b.F["grav"][i] = [0.0, -G]; b.F["normal"][i] = [0.0, G]
        if t >= T_EDGE:                         # the last ball leaves: the orbit takes over (run_orbit)
            break
        for _ in range(SUB):
            V = V + 0.5 * DT * Fc
            X = X + DT * V
            Fc, ov = forces(X)
            V = V + 0.5 * DT * Fc
            now = ov > 0
            for k in np.nonzero(now & ~in_contact)[0]:
                events.append(("contact", t, X[k] - R, k))
            in_contact = now
        i += 1
    P1, E1 = V.sum(), 0.5 * (V * V).sum()
    return X, V, (P0, P1, E0, E1)


# ── act 7: Kepler orbit around a star (Verlet) ─────────────────────────────
def orbit_params(v):
    """Apoapsis distance and GM for an orbit of period T_ORBIT and eccentricity ECC, entered at
    apoapsis with speed v perpendicular to the radius (the floor's last ball rolls off horizontally)."""
    r_a = T_ORBIT * v / (2 * np.pi * np.sqrt((1 - ECC) / (1 + ECC) ** 3))
    gm = v * v * r_a / (1 - ECC)
    return r_a, gm


def run_orbit(body, p0, v0):
    speed = abs(v0[0])
    r_a, gm = orbit_params(speed)
    star = p0 - [0.0, r_a]
    x, v = p0.astype(float).copy(), v0.astype(float).copy()
    acc = lambda x: -gm * (x - star) / np.linalg.norm(x - star) ** 3  # noqa: E731
    a = acc(x)
    i, i_end = idx(T_EDGE), idx(T_PEND)
    while True:
        body.p[i], body.v[i] = x, v
        body.F["star"][i] = a
        if i == i_end:
            break
        for _ in range(SUB):
            v = v + 0.5 * DT * a; x = x + DT * v; a = acc(x); v = v + 0.5 * DT * a
        i += 1
    return star, r_a, gm, x, v


# ── act 8: double pendulum ×3 (RK4, vectorised over the copies) ────────────
def dp_deriv(th1, th2, w1, w2, L1, L2, g, m1=1.0, m2=1.0):
    d = th1 - th2
    den = 2 * m1 + m2 - m2 * np.cos(2 * d)
    a1 = (-g * (2 * m1 + m2) * np.sin(th1) - m2 * g * np.sin(th1 - 2 * th2)
          - 2 * np.sin(d) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * np.cos(d))) / (L1 * den)
    a2 = (2 * np.sin(d) * (w1 * w1 * L1 * (m1 + m2) + g * (m1 + m2) * np.cos(th1)
                           + w2 * w2 * L2 * m2 * np.cos(d))) / (L2 * den)
    return w1, w2, a1, a2


def dp_energy(th1, th2, w1, w2, L1, L2, g):
    y1 = -L1 * np.cos(th1); y2 = y1 - L2 * np.cos(th2)
    kin = 0.5 * L1 ** 2 * w1 ** 2 + 0.5 * (L1 ** 2 * w1 ** 2 + L2 ** 2 * w2 ** 2
                                           + 2 * L1 * L2 * w1 * w2 * np.cos(th1 - th2))
    return kin + g * (y1 + y2)


def run_pendulum(bodies, pivot, p, v):
    rel = p - pivot
    r = np.linalg.norm(rel)
    th = np.arctan2(rel[0], -rel[1])                       # angle from the downward vertical
    w = (rel[0] * v[1] - rel[1] * v[0]) / (r * r)          # matches the orbit's angular velocity
    L1 = DP_L1 * r; L2 = r - L1
    th1 = np.full(3, th); th2 = th + np.array([0.0, DP_DELTA, -DP_DELTA])
    w1 = np.full(3, w); w2 = np.full(3, w)
    i = idx(T_PEND)
    e0 = dp_energy(th1, th2, w1, w2, L1, L2, G)
    seps = []
    h = DT * 2                                             # 1/6000 s
    while True:
        t = i / FS
        p1 = pivot + np.stack([L1 * np.sin(th1), -L1 * np.cos(th1)], 1)
        p2 = p1 + np.stack([L2 * np.sin(th2), -L2 * np.cos(th2)], 1)
        v1 = np.stack([L1 * np.cos(th1) * w1, L1 * np.sin(th1) * w1], 1)
        v2 = v1 + np.stack([L2 * np.cos(th2) * w2, L2 * np.sin(th2) * w2], 1)
        for k in range(3):
            bodies[f"pin{k}"].p[i], bodies[f"pin{k}"].v[i] = p1[k], v1[k]
            bodies[f"pout{k}"].p[i], bodies[f"pout{k}"].v[i] = p2[k], v2[k]
            bodies[f"pout{k}"].F["grav"][i] = [0.0, -G]
        seps.append((t, np.linalg.norm(p2[1] - p2[0]), np.linalg.norm(p2[2] - p2[0])))
        if i == N - 1:
            break
        for _ in range(SUB // 2):
            s = (th1, th2, w1, w2)
            k1 = dp_deriv(*s, L1, L2, G)
            k2 = dp_deriv(*[a + 0.5 * h * b for a, b in zip(s, k1)], L1, L2, G)
            k3 = dp_deriv(*[a + 0.5 * h * b for a, b in zip(s, k2)], L1, L2, G)
            k4 = dp_deriv(*[a + h * b for a, b in zip(s, k3)], L1, L2, G)
            th1, th2, w1, w2 = [a + h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
                                for a, b1, b2, b3, b4 in zip(s, k1, k2, k3, k4)]
        i += 1
    e1 = dp_energy(th1, th2, w1, w2, L1, L2, G)
    return L1, L2, np.array(seps), (e0, e1)


def smoothstep(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


# ── driver ─────────────────────────────────────────────────────────────────
def simulate():
    bodies = {nm: Body(nm) for nm in BODY_NAMES}
    events = []
    hero, twin = bodies["hero"], bodies["twin"]
    x, v = run_kinematic(hero, twin, events)
    x_c = x[0] + R                               # the spring's tip, where the ball touches it at T_SPRING
    x_eq = x_c - R
    t_rel, x_rel, v_rel, energy = run_spring(hero, x_eq, x, v, events)
    Xc, Vc, chain_cons = run_chain(bodies, t_rel, x_rel, v_rel, events)
    last = bodies[f"c{CHAIN_N}"]
    i_edge = idx(T_EDGE)
    star, r_a, gm, xo, vo = run_orbit(last, last.p[i_edge].copy(), last.v[i_edge].copy())
    L1, L2, seps, dp_e = run_pendulum(bodies, star, xo, vo)

    meta = dict(x_c=x_c, x_eq=x_eq, x_wall=x_c + L0, t_rel=t_rel, v_rel=v_rel, star=star, r_a=r_a, gm=gm,
                L1=L1, L2=L2, x_edge=last.p[i_edge][0], amp=v[0] / OMEGA,
                chain_cons=np.array(chain_cons), dp_e=np.array(dp_e))
    data = {"meta_" + k: np.asarray(val) for k, val in meta.items()}
    for nm, b in bodies.items():
        data[f"{nm}_p"] = b.p.astype("f8"); data[f"{nm}_v"] = b.v.astype("f8")
        for f in FORCES:
            if np.any(b.F[f]):
                data[f"{nm}_F_{f}"] = b.F[f]
    data["energy"] = energy
    data["seps"] = seps
    ev = [(k, t, a, b) for k, t, a, b in events]
    data["ev_kind"] = np.array([e[0] for e in ev])
    data["ev"] = np.array([e[1:] for e in ev], float)
    return data


def _key():
    return hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]


def load():
    OUT.mkdir(exist_ok=True)
    path = OUT / f"sim_{_key()}.npz"
    if not path.exists():
        for old in OUT.glob("sim_*.npz"):
            old.unlink()
        np.savez_compressed(path, **simulate())
    return dict(np.load(path))


# ── the checks: each act against its analytic answer ───────────────────────
def check(d, verbose=True):
    say = print if verbose else (lambda *a: None)
    hp, hv = d["hero_p"], d["hero_v"]

    # act 1: constant velocity
    i0, i1 = idx(T_SPARK), idx(T_F0)
    assert np.allclose(hv[i0:i1, 0], V0, atol=1e-12)
    # act 2: constant acceleration → strobe gaps (every 0.5 s) form an arithmetic progression with
    # common difference a·Δt², and the 2m twin's extra displacement is exactly half the ball's
    ts = T_F0 + 0.5 * np.arange(11)
    xs = np.array([hp[idx(t), 0] for t in ts]); gaps = np.diff(xs)
    assert np.allclose(np.diff(gaps), F_APP * 0.25, atol=1e-9), np.diff(gaps)
    tp = d["twin_p"]
    ext_h = hp[idx(T_F1), 0] - hp[idx(T_F0), 0] - V0 * (T_F1 - T_F0)
    ext_t = tp[idx(T_F1), 0] - tp[idx(T_F0), 0] - V0 * (T_F1 - T_F0)
    assert abs(ext_t / ext_h - 0.5) < 1e-9
    say(f"act 2  strobe gap step {np.diff(gaps).mean():.6f} (= a·Δt² = {F_APP * 0.25})  twin/ball = {ext_t / ext_h:.9f}")

    # act 3: projectile. The first flight is y = y0 − ½g(t−t_g)² exactly; the horizontal speed is constant;
    # each bounce leaves with e× the impact speed, so apex heights fall by e²
    kinds, ev = d["ev_kind"], d["ev"]
    b = ev[kinds == "bounce"]
    t_hit = T_G + np.sqrt(2 * (Y0 - Y_FLOOR - R) / G)
    assert abs(b[0, 0] - t_hit) < 1e-9, (b[0, 0], t_hit)
    tt = np.arange(idx(T_G), idx(b[0, 0])) / FS
    assert np.allclose(hp[idx(T_G):idx(b[0, 0]), 1], Y0 - 0.5 * G * (tt - T_G) ** 2, atol=1e-9)
    vx3 = hv[idx(T_G):idx(T_SPRING), 0]
    assert np.ptp(vx3) < 1e-12
    ratios = b[1:, 2] / b[:-1, 2]
    assert np.allclose(ratios, E_REST, atol=1e-9), ratios
    say(f"act 3  first impact t={b[0, 0]:.6f} (analytic {t_hit:.6f})  {len(b)} bounces, speed ratio {ratios.mean():.9f}")

    # act 4: SHM. x − x_eq = A·sin(ω(t−t_s)), A = v/ω, until the drag switches on
    m = {k[5:]: d[k] for k in d if k.startswith("meta_")}
    x_eq = float(m["x_eq"]); v_in = vx3[-1]; A = v_in / OMEGA
    tt = np.arange(idx(T_SPRING), idx(T_D0)) / FS
    err = np.abs(hp[idx(T_SPRING):idx(T_D0), 0] - x_eq - A * np.sin(OMEGA * (tt - T_SPRING))).max()
    assert err < 1e-6, err
    E = d["energy"]
    tot = E[:, 1] + E[:, 2] + E[:, 3]
    pre = E[:, 0] < T_D0
    assert np.ptp(tot[pre]) / tot[0] < 1e-6
    say(f"act 4  |x − A sin ωt| max {err:.2e} over {(T_D0 - T_SPRING) * OMEGA / (2 * np.pi):.1f} periods, A={A:.4f}")

    # act 5: damping. Amplitude envelope e^(−ζω t) and K + U + Q conserved (Q = work done by drag)
    assert np.ptp(tot) / tot[0] < 1e-6, np.ptp(tot) / tot[0]
    # exact underdamped solution from the state at T_D0:
    # x(τ) = e^(−ζωτ)·(x0·cos ω_d τ + (v0 + ζω x0)/ω_d · sin ω_d τ)
    j0, j1 = idx(T_D0), idx(T_D1)
    x0, v0 = hp[j0, 0] - x_eq, hv[j0, 0]
    wd = OMEGA * np.sqrt(1 - ZETA ** 2)
    tau = np.arange(j1 - j0) / FS
    xa = np.exp(-ZETA * OMEGA * tau) * (x0 * np.cos(wd * tau) + (v0 + ZETA * OMEGA * x0) / wd * np.sin(wd * tau))
    err5 = np.abs(hp[j0:j1, 0] - x_eq - xa).max()
    assert err5 < 1e-6, err5
    say(f"act 5  |x − damped analytic| {err5:.1e}  K+U+Q drift {np.ptp(tot) / tot[0]:.2e}  heat at release {E[-1, 3]:.4f}  "
        f"release v={float(m['v_rel']):+.4f} at t={float(m['t_rel']):.4f}")

    # act 6: elastic collisions. Momentum exact (pairwise forces), KE back to its value, last ball exits at v_in
    P0, P1, E0, E1 = m["chain_cons"]
    assert abs(P1 - P0) < 1e-9 and abs(E1 / E0 - 1) < 1e-4, (P0, P1, E0, E1)
    vlast = d[f"c{CHAIN_N}_v"][idx(T_EDGE) - 1, 0]
    assert abs(vlast / float(m["v_rel"]) - 1) < 2e-3, vlast
    say(f"act 6  Δp={P1 - P0:.1e}  KE ratio {E1 / E0:.6f}  last ball v={vlast:+.4f}")

    # act 7: Kepler. Energy and angular momentum conserved; the orbit closes; equal times sweep equal areas
    op, ov = d[f"c{CHAIN_N}_p"], d[f"c{CHAIN_N}_v"]
    star, gm = m["star"], float(m["gm"])
    s = slice(idx(T_EDGE), idx(T_PEND) + 1)
    r = op[s] - star; w = ov[s]
    eps = 0.5 * (w ** 2).sum(1) - gm / np.linalg.norm(r, axis=1)
    Lz = r[:, 0] * w[:, 1] - r[:, 1] * w[:, 0]
    assert np.ptp(eps) / abs(eps[0]) < 1e-6 and np.ptp(Lz) / Lz[0] < 1e-9
    close = np.linalg.norm(op[idx(T_EDGE + T_ORBIT)] - op[idx(T_EDGE)])
    assert close < 1e-3, close
    areas = []
    for k in range(6):
        a0, a1 = idx(T_EDGE + k * T_ORBIT / 6), idx(T_EDGE + (k + 1) * T_ORBIT / 6)
        q = op[a0:a1 + 1] - star
        areas.append(0.5 * np.sum(q[:-1, 0] * q[1:, 1] - q[1:, 0] * q[:-1, 1]))
    areas = np.array(areas)
    assert np.ptp(areas) / areas.mean() < 1e-4, areas
    say(f"act 7  r_a={float(m['r_a']):.4f} GM={gm:.4f}  energy drift {np.ptp(eps) / abs(eps[0]):.1e}  "
        f"closure {close:.1e}  wedge areas equal to {np.ptp(areas) / areas.mean():.1e}")

    # act 8: double pendulum. Energy conserved; the twins diverge exponentially
    e0, e1 = m["dp_e"]
    assert np.max(np.abs(e1 - e0)) / np.abs(e0).max() < 1e-6, (e0, e1)
    sp = d["seps"]
    grow = sp[:, 1] > 0
    j = np.argmax(sp[:, 1] > 0.3) if np.any(sp[:, 1] > 0.3) else -1
    lo = (sp[:, 1] > 1e-3) & (sp[:, 1] < 0.1)
    lam = np.polyfit(sp[lo, 0], np.log(sp[lo, 1]), 1)[0] if lo.sum() > 10 else float("nan")
    say(f"act 8  energy drift {np.max(np.abs(e1 - e0)):.1e}  twins split > 0.3 at t={sp[j, 0]:.2f}s  "
        f"λ ≈ {lam:.2f}/s ({grow.sum()} samples)")
    return True


if __name__ == "__main__":
    import time
    t0 = time.time()
    d = load()
    print(f"simulated / loaded in {time.time() - t0:.1f}s")
    check(d)
