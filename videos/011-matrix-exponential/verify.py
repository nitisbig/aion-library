"""Every number this video shows, computed (never typed). Run: uv run python videos/011-matrix-exponential/verify.py

Scenes import CAST from here at build time, so the screen and this check can never disagree.
"""
from math import comb, factorial

import numpy as np
from scipy.linalg import expm

PI = np.pi
I2 = np.eye(2)
J = np.array([[0.0, -1.0], [1.0, 0.0]])          # quarter-turn generator (counterclockwise), J @ J = -I
N = np.array([[0.0, 1.0], [0.0, 0.0]])            # horizontal shear generator, N @ N = 0
B = np.array([[0.0, 0.0], [1.0, 0.0]])            # vertical shear generator (ch5 partner of N)

CAST = dict(
    hook=PI * J,                                  # e^(pi J) = -I
    diag=np.diag([1.0, -0.5]),                    # ch4: stretch x, squash y
    saddle=np.array([[0.5, 1.0], [1.0, 0.5]]),    # ch4: eigenvalues 1.5, -0.5 on the diagonals
    spiral=np.array([[-0.25, -1.0], [1.0, -0.25]]),  # ch4/ch5: shrink + turn, eigenvalues -0.25 +- i
    shear=N,
    pill=np.array([[-1.0, 0.0], [1.0, -0.25]]),   # intro/ch6: (stomach, blood); absorb k_a = 1/h, clear k_e = 0.25/h
    tilt=np.radians(23.44),                       # ch6: Earth's axis drawn tilted from screen-vertical
)
EARTH_R_KM = 6378.137                             # equatorial radius
SIDEREAL_S = 86164.0905                           # one turn relative to the stars


def ew(a):
    """Element-wise exponential (the wrong guess)."""
    return np.exp(a)


def series(a, k):
    """Partial sum I + A + ... + A^k / k!."""
    s, term = np.eye(len(a)), np.eye(len(a))
    for j in range(1, k + 1):
        term = term @ a / j
        s = s + term
    return s


def euler(a, n):
    """n compounding steps (I + A/n)^n."""
    return np.linalg.matrix_power(np.eye(len(a)) + a / n, n)


def cross(n):
    return np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])


def check(name, cond):
    print(("  ok  " if cond else "  !!  ") + name)
    assert cond, name


def main():
    np.set_printoptions(precision=4, suppress=True)
    A = CAST["hook"]
    print("INTRO / hook: A = pi J")
    print("  e^A =\n", expm(A))
    check("e^(pi J) = -I", np.allclose(expm(A), -I2))
    print("  element-wise exp(A) =\n", ew(A), "  det =", np.linalg.det(ew(A)))
    check("element-wise exp of pi J is singular (det 0)", abs(np.linalg.det(ew(A))) < 1e-12)
    print("  element-wise exp(0) =\n", ew(np.zeros((2, 2))), " true e^0 = I")
    check("e^0 = I", np.allclose(expm(np.zeros((2, 2))), I2))

    print("\nCH1 compounding (1 + 1/n)^n")
    for n in (1, 2, 4, 12, 365, 10**6):
        print(f"  n={n:>7}: {(1 + 1 / n) ** n:.6f}")

    print("\nCH2 rotation flow e^(tJ) = [[cos t, -sin t], [sin t, cos t]]")
    for t in (0.5, PI / 2, PI):
        R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        check(f"e^({t:.3f} J) is rotation by t", np.allclose(expm(t * J), R))

    print("\nCH3 Euler compounding (I + pi J / n)^n -> -I; length (1 + pi^2/n^2)^(n/2)")
    for n in (4, 8, 32, 1000):
        M = euler(A, n)
        print(f"  n={n:>5}: image of (1,0) = {M[:, 0]}, length {np.linalg.norm(M[:, 0]):.4f}")
    print("  binomial weight C(n,k)/n^k vs 1/k! (n = 1000):",
          [f"{comb(1000, k) / 1000**k:.5f} vs {1 / factorial(k):.5f}" for k in (2, 3, 4)])
    print("  series term sizes pi^k / k!:", [round(PI**k / factorial(k), 3) for k in range(12)])
    print("  partial sums, top-left entry:", [round(series(A, k)[0, 0], 4) for k in range(12)])
    check("series to k=20 equals expm", np.allclose(series(A, 20), expm(A)))
    v = np.array([1.0, 0.0])
    terms = [np.linalg.matrix_power(A, k) @ v / factorial(k) for k in range(8)]
    print("  tip-to-tail terms on v = (1,0):", [tuple(np.round(x, 3)) for x in terms])

    print("\nCH4 special cases")
    D = CAST["diag"]
    check("diagonal: e^D = diag(e^d)", np.allclose(expm(D), np.diag(np.exp(np.diag(D)))))
    print("  element-wise exp(diag) =\n", ew(D), "(off-diagonal 0 -> 1, wrong)")
    S = CAST["saddle"]
    w, P = np.linalg.eigh(S)
    print("  saddle eigenvalues", w, "eigenvectors (cols)\n", P)
    check("saddle: e^S = P e^L P^-1", np.allclose(expm(S), P @ np.diag(np.exp(w)) @ P.T))
    Sp = CAST["spiral"]
    print("  spiral eigenvalues", np.linalg.eigvals(Sp))
    t = 2.0
    check("spiral: e^(tA) = e^(-0.25 t) R(t)", np.allclose(expm(t * Sp), np.exp(-0.25 * t) * expm(t * J)))
    check("shear: N^2 = 0", np.allclose(N @ N, 0))
    check("shear: e^(tN) = I + tN", np.allclose(expm(1.5 * N), I2 + 1.5 * N))
    for M_, nm in ((Sp, "spiral"), (S, "saddle"), (N, "shear"), (CAST["pill"], "pill")):
        for t in (1.0, 3.0):
            check(f"det e^(tA) = e^(t tr A)  [{nm}, t={t}]",
                  np.isclose(np.linalg.det(expm(t * M_)), np.exp(t * np.trace(M_))))
    print("  spiral: area after t = 4 is e^(-0.5*4) =", round(np.exp(-2.0), 4))

    print("\nCH5 non-commutativity, A = N (horizontal shear), B (vertical shear)")
    eA, eB, eAB = expm(N), expm(B), expm(N + B)
    print("  e^A e^B =\n", eA @ eB)
    print("  e^B e^A =\n", eB @ eA)
    print("  e^(A+B) =\n", eAB, " (= [[cosh 1, sinh 1], [sinh 1, cosh 1]])")
    check("e^(A+B) = cosh/sinh", np.allclose(eAB, [[np.cosh(1), np.sinh(1)], [np.sinh(1), np.cosh(1)]]))
    check("all three differ", not np.allclose(eA @ eB, eAB) and not np.allclose(eB @ eA, eAB))
    check("all three have det 1 (trace 0)", all(np.isclose(np.linalg.det(M_), 1) for M_ in (eA @ eB, eB @ eA, eAB)))
    C_ = N @ B - B @ N
    print("  commutator AB - BA =\n", C_)
    print("  'A then B' on screen is the product e^B e^A (maps apply right to left)")
    for s in (0.3, 0.1, 0.03):
        loop = expm(-s * B) @ expm(-s * N) @ expm(s * B) @ expm(s * N)   # time order: A, B, -A, -B
        err = np.abs(loop - (I2 - s * s * C_)).max()
        print(f"  loop A,B,-A,-B with s={s}: deviation from I = {np.round(loop - I2, 5).tolist()}, "
              f"vs -s^2[A,B] = s^2[B,A] error {err:.2e}")
        assert err < 2 * s**3
    print("  -> the loop squashes x and stretches y by ~s^2: a stretch neither shear contains")
    check("commuting pair: e^(-0.25I + J) = e^(-0.25 I) e^J",
          np.allclose(expm(-0.25 * I2 + J), np.exp(-0.25) * expm(J)))

    print("\nCH6 pill: d/dt (s, b) = [[-ka, 0], [ka, -ke]] (s, b), start (1, 0)")
    Pm = CAST["pill"]
    ka, ke = -Pm[0, 0], -Pm[1, 1]
    print("  eigenvalues", np.linalg.eigvals(Pm), "= -k_a, -k_e")
    t_peak = np.log(ka / ke) / (ka - ke)
    blood = lambda t: (expm(t * Pm) @ [1.0, 0.0])[1]
    bateman = lambda t: ka / (ka - ke) * (np.exp(-ke * t) - np.exp(-ka * t))
    check("e^(tA) matches the Bateman curve", all(np.isclose(blood(t), bateman(t)) for t in (0.5, 1.85, 3, 8)))
    print(f"  peak at t = {t_peak:.3f} h, blood fraction {blood(t_peak):.3f}; at 3 h {blood(3):.3f}; at 12 h {blood(12):.3f}")
    from scipy.integrate import solve_ivp
    sol = solve_ivp(lambda t, y: Pm @ y, (0, 12), [1.0, 0.0], t_eval=[3.0, 12.0], rtol=1e-11, atol=1e-12)
    check("e^(tA) x0 matches an ODE solver at t = 3, 12",
          np.allclose(sol.y.T, [expm(3 * Pm) @ [1, 0], expm(12 * Pm) @ [1, 0]], atol=1e-7))
    g = np.random.default_rng(11)
    n_mol = 2000
    t_abs = g.exponential(1 / ka, n_mol)
    t_clr = t_abs + g.exponential(1 / ke, n_mol)
    frac = lambda t: np.mean((t_abs <= t) & (t_clr > t))
    dev = max(abs(frac(t) - blood(t)) for t in np.linspace(0, 12, 49))
    print(f"  {n_mol} seeded molecules (seed 11) vs e^(tA): max deviation {dev:.3f}")
    check("molecule crowd follows e^(tA) within 4%", dev < 0.04)

    print("\nCH6 Earth: K = [n]x, velocity = Omega K r")
    n = np.array([0.0, np.sin(CAST["tilt"]), np.cos(CAST["tilt"])])
    K = cross(n)
    check("K r = n x r", np.allclose(K @ [0.3, -0.7, 0.2], np.cross(n, [0.3, -0.7, 0.2])))
    check("K^3 = -K", np.allclose(K @ K @ K, -K))
    for th in (0.7, 2.0, 4.0):
        rod = np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K
        check(f"Rodrigues at theta = {th}: e^(theta K) = I + sin K + (1 - cos) K^2", np.allclose(expm(th * K), rod))
        check(f"  ...is a rotation (orthogonal, det 1)", np.allclose(rod.T @ rod, np.eye(3)) and np.isclose(np.linalg.det(rod), 1))
    check("axis is fixed (eigenvector, lambda = 1)", np.allclose(expm(1.3 * K) @ n, n))
    check("one full turn: e^(2 pi K) = I", np.allclose(expm(2 * PI * K), np.eye(3)))
    v_eq = 2 * PI * EARTH_R_KM / SIDEREAL_S * 3600
    print(f"  equator speed {v_eq:.1f} km/h; at latitude 45 deg {v_eq * np.cos(np.radians(45)):.1f} km/h")
    check("equator speed is more than 1600 km/h", v_eq > 1600)
    print("  spacecraft: two small turns about different axes don't commute")
    Kx, Ky = cross([1, 0, 0]), cross([0, 1, 0])
    gap = np.abs(expm(0.5 * Kx) @ expm(0.5 * Ky) - expm(0.5 * Ky) @ expm(0.5 * Kx)).max()
    check(f"rotation order matters (max entry gap {gap:.3f})", gap > 0.1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
