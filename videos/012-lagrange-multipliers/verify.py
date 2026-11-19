"""Every number spoken or shown in video 012 is computed and checked here.

Run: uv run python videos/012-lagrange-multipliers/verify.py
Scenes import CAST from this file instead of retyping values.
"""
import json
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import brentq, minimize_scalar

from world import TRAIL_A, TRAIL_B, hill, hill_grad, trail, trail_grad

CAST = {}
checks = 0


def ok(name, cond):
    global checks
    assert bool(cond), f"FAILED: {name}"
    checks += 1
    print(f"  ok  {name}")


def section(title):
    print(f"\n{title}")


x, y, z, lam, mu, L, c = sp.symbols("x y z lambda mu L c", real=True)

# ---------------------------------------------------------------- the trail on the hill (intro, ch1 to ch3)
section("hill and trail")


def height_on_trail(s):
    return hill(*trail(s))


grid = np.linspace(0, 2 * np.pi, 7201)
vals = height_on_trail(grid)
idx = [i for i in range(1, len(grid) - 1) if vals[i] > vals[i - 1] and vals[i] > vals[i + 1]]
idx_min = [i for i in range(1, len(grid) - 1) if vals[i] < vals[i - 1] and vals[i] < vals[i + 1]]
stations = []
for i in idx:
    r = minimize_scalar(lambda s: -height_on_trail(s), bounds=(grid[i - 1], grid[i + 1]), method="bounded", options={"xatol": 1e-10})
    stations.append(("max", r.x))
for i in idx_min:
    r = minimize_scalar(height_on_trail, bounds=(grid[i - 1], grid[i + 1]), method="bounded", options={"xatol": 1e-10})
    stations.append(("min", r.x))
for kind, s in stations:
    p = trail(s)
    gf, gg = hill_grad(*p), trail_grad(*p)
    cross = gf[0] * gg[1] - gf[1] * gg[0]
    ok(f"grad f parallel to grad g at trail {kind} s={s:.4f} (cross={cross:.1e})", abs(cross) < 1e-5)
best = max((s for k, s in stations if k == "max"), key=height_on_trail)
p = trail(best)
summit = minimize_scalar(lambda v: -hill(0.8 * v, 0.6 * v), bounds=(0.5, 1.5), method="bounded").x
ok("the summit lies inside the trail, off the path", (0.8 * summit / TRAIL_A) ** 2 + (0.6 * summit / TRAIL_B) ** 2 < 1)
ok("grad f is NOT zero at the trail's high point", np.linalg.norm(hill_grad(*p)) > 0.1)
CAST["trail_best"] = (float(p[0]), float(p[1]))
CAST["trail_best_s"] = float(best)
CAST["trail_stations"] = [(k, float(s), float(height_on_trail(s))) for k, s in sorted(stations, key=lambda q: q[1])]
CAST["summit"] = (float(0.8 * summit), float(0.6 * summit))
CAST["trail_lambda"] = float(hill_grad(*p)[0] / trail_grad(*p)[0])

# ---------------------------------------------------------------- example 1: the rope against the shore
section("fence: maximize x y with 2x + y = L")
f, g = x * y, 2 * x + y
sol = sp.solve([sp.diff(f, x) - lam * sp.diff(g, x), sp.diff(f, y) - lam * sp.diff(g, y), g - L], [x, y, lam], dict=True)[0]
ok("x = L/4", sol[x] == L / 4)
ok("y = L/2", sol[y] == L / 2)
ok("lambda = L/4", sol[lam] == L / 4)
A = sp.simplify(f.subs(sol))
ok("A = L^2/8", A == L**2 / 8)
ok("dA/dL = lambda", sp.simplify(sp.diff(A, L) - sol[lam]) == 0)
ok("L=40: x=10, y=20, A=200, lambda=10", (sol[x].subs(L, 40), sol[y].subs(L, 40), A.subs(L, 40), sol[lam].subs(L, 40)) == (10, 20, 200, 10))
ok("L=41: A = 210.125 (gain 10.125, about lambda)", A.subs(L, 41) == sp.Rational(1681, 8))
CAST["fence"] = dict(L=40, x=10, y=20, A=200, lam=10, A41=210.125)

# ---------------------------------------------------------------- example 2: x^2 y on the circle
section("circle: extremes of x^2 y on x^2 + y^2 = 3")
f, g = x**2 * y, x**2 + y**2
sols = sp.solve([sp.diff(f, x) - lam * sp.diff(g, x), sp.diff(f, y) - lam * sp.diff(g, y), g - 3], [x, y, lam], dict=True)
ok("exactly six critical points", len(sols) == 6)
values = sorted(f.subs(s) for s in sols)
ok("values are -2, -2, 0, 0, 2, 2", values == [-2, -2, 0, 0, 2, 2])
for s in sols:
    if s[x] == 0:
        ok(f"lambda = 0 at (0, {s[y]})", s[lam] == 0)
    else:
        ok(f"lambda = y at ({s[x]}, {s[y]})", s[lam] == s[y])
th = np.linspace(0, 2 * np.pi, 72001)[:-1]
fv = (3 * np.cos(th) ** 2) * (np.sqrt(3) * np.sin(th))
turning = np.sum(np.sign(np.roll(fv, -1) - fv) != np.sign(fv - np.roll(fv, 1)))
ok("walking the circle, f turns around exactly six times", turning == 6)
CAST["circle"] = dict(r2=3, max=2, min=-2, pts=[(float(s[x]), float(s[y]), float(s[lam])) for s in sols])

# ---------------------------------------------------------------- 3D, one constraint: sphere meets plane
section("plane: nearest point to the origin on x + 2y + 2z = 9")
f, g = x**2 + y**2 + z**2, x + 2 * y + 2 * z
sol = sp.solve([sp.diff(f, v) - lam * sp.diff(g, v) for v in (x, y, z)] + [g - c], [x, y, z, lam], dict=True)[0]
at9 = {k: v.subs(c, 9) for k, v in sol.items()}
ok("point = (1, 2, 2)", (at9[x], at9[y], at9[z]) == (1, 2, 2))
ok("lambda = 2", at9[lam] == 2)
ok("distance = 3", sp.sqrt(f.subs(at9)) == 3)
ok("d f*/d c = lambda", sp.simplify(sp.diff(f.subs(sol), c) - sol[lam]) == 0)
CAST["plane"] = dict(p=(1, 2, 2), lam=2, dist=3)

# ---------------------------------------------------------------- 3D, two constraints: tilted ellipse on a cylinder
section("ellipse: highest point of x^2 + y^2 = 1 and 3x + 4y + 5z = 10")
f, g, h = z, x**2 + y**2, 3 * x + 4 * y + 5 * z
sols = sp.solve([sp.diff(f, v) - lam * sp.diff(g, v) - mu * sp.diff(h, v) for v in (x, y, z)] + [g - 1, h - 10], [x, y, z, lam, mu], dict=True)
ok("two critical points", len(sols) == 2)
top = max(sols, key=lambda s: s[z])
low = min(sols, key=lambda s: s[z])
ok("top = (-3/5, -4/5, 3)", (top[x], top[y], top[z]) == (sp.Rational(-3, 5), sp.Rational(-4, 5), 3))
ok("bottom = (3/5, 4/5, 1)", (low[x], low[y], low[z]) == (sp.Rational(3, 5), sp.Rational(4, 5), 1))
ok("at the top lambda = 1/2, mu = 1/5", (top[lam], top[mu]) == (sp.Rational(1, 2), sp.Rational(1, 5)))
CAST["ellipse"] = dict(top=(-0.6, -0.8, 3.0), low=(0.6, 0.8, 1.0), lam=0.5, mu=0.2)

# ---------------------------------------------------------------- the Lagrangian is a saddle
section("Lagrangian: -x^2 with x = 1")
Lag = -(x**2) - lam * (x - 1)
sol = sp.solve([sp.diff(Lag, x), sp.diff(Lag, lam)], [x, lam], dict=True)[0]
ok("stationary at x = 1, lambda = -2", (sol[x], sol[lam]) == (1, -2))
H = sp.hessian(Lag, (x, lam))
ok("Hessian determinant -1, so a saddle", H.det() == -1)
ok("d L / d lambda = 0 is the constraint", sp.diff(Lag, lam) == 1 - x)
CAST["saddle"] = dict(x=1, lam=-2)

# ---------------------------------------------------------------- lambda as force: the bead at the bottom of a hoop
section("bead on a hoop: minimize m g y on x^2 + y^2 = R^2")
m, G, R = sp.symbols("m g_0 R", positive=True)
U, g = m * G * y, x**2 + y**2
at = {x: 0, y: -R}
l = sp.solve(sp.diff(U, y).subs(at) - lam * sp.diff(g, y).subs(at), lam)[0]
force = l * sp.Matrix([sp.diff(g, x), sp.diff(g, y)]).subs(at)
ok("hoop force = lambda grad g = (0, m g), straight up", list(force) == [0, m * G])
ok("hoop force plus gravity is zero", sp.simplify(force[1] - sp.diff(U, y)) == 0)

# ---------------------------------------------------------------- lambda as temperature: maximum entropy
section("Boltzmann: maximize entropy with fixed mean energy")
E = np.array([0.0, 1.0, 2.0])


def dist(beta):
    w = np.exp(-beta * E)
    return w / w.sum()


def beta_for(U_):
    return brentq(lambda b: dist(b) @ E - U_, -50, 50, xtol=1e-13)


def entropy(p):
    return float(-(p * np.log(p)).sum())


U0, dU = 0.6, 1e-5
b0 = beta_for(U0)
dS = (entropy(dist(beta_for(U0 + dU))) - entropy(dist(beta_for(U0 - dU)))) / (2 * dU)
ok(f"beta = dS/dU = {b0:.5f}", abs(dS - b0) < 1e-6)
p0 = dist(b0)
rng = np.random.default_rng(12)
n1, n2 = np.ones(3), E - E.mean()
best_neighbour = -np.inf
for _ in range(2000):
    # project onto the directions that keep both total probability and mean energy
    d = rng.normal(size=3)
    d = d - (d @ n1) / (n1 @ n1) * n1 - (d @ n2) / (n2 @ n2) * n2
    q = p0 + rng.uniform(0.001, 0.1) * d / np.linalg.norm(d)
    ok_q = abs(q.sum() - 1) < 1e-12 and abs(q @ E - U0) < 1e-9 and (q > 0).all()
    assert ok_q
    best_neighbour = max(best_neighbour, entropy(q))
ok("no feasible neighbour has more entropy", best_neighbour < entropy(p0))
CAST["boltzmann"] = dict(E=E.tolist(), U=U0, beta=float(b0), p=p0.tolist())

# ---------------------------------------------------------------- where the method fails: the cusp
section("cusp: minimize x on y^2 = x^3")
f, g = x, y**2 - x**3
grad_g0 = [sp.diff(g, v).subs({x: 0, y: 0}) for v in (x, y)]
ok("grad g = 0 at the cusp", grad_g0 == [0, 0])
ok("grad f = (1, 0), so no lambda exists", [sp.diff(f, v) for v in (x, y)] == [1, 0])
sys = [sp.diff(f, x) - lam * sp.diff(g, x), sp.diff(f, y) - lam * sp.diff(g, y), g]
ok("the Lagrange system has no real solution at all", sp.solve(sys, [x, y, lam], dict=True) == [])
ys = np.linspace(-5, 5, 2001)
xs = np.cbrt(ys**2)
ok("x = y^(2/3) >= 0 on the curve, with x = 0 only at the origin", (xs >= 0).all() and xs[1000] == 0 and (np.delete(xs, 1000) > 0).all())

# ---------------------------------------------------------------- outro: Dido's semicircle
section("Dido: semicircle against a straight shore")
r = sp.symbols("r", positive=True)
Ld = sp.pi * r
Ad = sp.pi * r**2 / 2
ok("dA/dL = r", sp.simplify(sp.diff(Ad, r) / sp.diff(Ld, r) - r) == 0)
semi = float((40 / sp.pi) ** 2 * sp.pi / 2)
ok(f"40 m of rope: semicircle {semi:.1f} beats the best rectangle 200", semi > 200)
ok("radius 12.7 m, area 254.6 m^2", abs(40 / np.pi - 12.732) < 1e-3 and abs(semi - 254.648) < 1e-3)
CAST["dido"] = dict(L=40, r=40 / np.pi, A=semi, gain=semi / 200 - 1)

if __name__ == "__main__":
    print(f"\nall {checks} checks passed")
    Path(__file__).with_name("cast.json").write_text(json.dumps(CAST, indent=1))
    for k, v in CAST.items():
        print(f"{k}: {v}")
