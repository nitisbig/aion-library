"""Baked data for 014's scenes (computed once from zmath; checked against it here).

    uv run python videos/014-riemann-hypothesis/bake.py            # writes assets/*.npz

explicit.npz (s02, s16, s31): the prime staircase and Riemann's explicit formula on x ∈ [1.6, 100]:
    x, pi (π(x)), base (R(x) − 1/ln x + arctan(π/ln x)/π), waves[k] (the pair ρ_k, ρ̄_k), gammas.
error.npz (s17): the real error π(x) − li(x) on x ∈ (0, 10⁸] (3,000 even steps, segmented sieve), Schoenfeld's RH
    envelope √x ln x / 8π, and a hypothetical: the first zero moved off the line to 0.8 + 14.13i (its mirror twin at
    0.2 + 14.13i comes with it), as the change it would make to π(x).
"""
import sys
from pathlib import Path

import numpy as np
from scipy.special import exp1

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from zmath import mobius_upto, pi_explicit, prime_pi, riemann_R, wave  # noqa: E402

ASSETS = HERE / "assets"


def ei(z):
    """Ei(z) for complex z off the real axis: −E1(−z) ± iπ (sign of Im z). Checked against mpmath in `check_ei`."""
    z = np.asarray(z, dtype=complex)
    return -exp1(-z) + 1j * np.pi * np.sign(z.imag)


def check_ei():
    import mpmath as mp

    rng = np.random.default_rng(14)
    z = rng.uniform(-20, 20, 400) + 1j * rng.uniform(-300, 300, 400)
    ref = np.array([complex(mp.ei(complex(v))) for v in z])
    err = np.max(np.abs(ei(z) - ref) / np.maximum(1, np.abs(ref)))
    assert err < 1e-9, err
    return err


def wave_fast(x, gamma, sigma=0.5, terms=6):
    """Same as zmath.wave (−2 Re Σ μ(n)/n · Ei(ρ ln x / n)), vectorized with scipy."""
    x = np.asarray(x, dtype=float)
    mu = mobius_upto(terms)
    rho = sigma + 1j * gamma
    out = np.zeros_like(x)
    for n in range(1, terms + 1):
        if mu[n]:
            out += -2 * mu[n] / n * ei(rho * np.log(x) / n).real
    return out


def bake_explicit(n_zeros=100, samples=4000):
    gammas = np.load(ASSETS / "zeros.npy")[:n_zeros]
    x = np.linspace(1.6, 100.0, samples)
    base = riemann_R(x) - 1 / np.log(x) + np.arctan(np.pi / np.log(x)) / np.pi
    waves = np.stack([wave_fast(x, g) for g in gammas]).astype(np.float32)
    # the fast waves must match zmath's mpmath version, and the sum must match pi_explicit
    xs = np.array([10.5, 30.5, 50.5, 97.5])
    for g in gammas[:3]:
        assert np.max(np.abs(wave_fast(xs, g) - wave(xs, g))) < 1e-9
    assert np.max(np.abs(np.interp(xs, x, base + waves[:30].sum(0)) - pi_explicit(xs, gammas[:30]))) < 2e-3
    pi = prime_pi(x).astype(np.float32)
    mids = np.arange(2, 100) + 0.5                       # error of the 100-pair curve halfway between integers
    err = np.max(np.abs(np.interp(mids, x, base + waves.sum(0)) - prime_pi(mids)))
    np.savez_compressed(ASSETS / "explicit.npz", x=x.astype(np.float32), pi=pi, base=base.astype(np.float32),
                        waves=waves, gammas=gammas.astype(np.float32))
    print(f"explicit.npz: {n_zeros} waves × {samples} samples; |error| at half-integers with all {n_zeros}: {err:.3f}")


def prime_counts(xs, top=10**8, seg=10**7):
    """π(x) at each integer x in xs (sorted), by a segmented sieve of Eratosthenes up to `top`."""
    xs = np.asarray(xs, dtype=np.int64)
    r = int(top ** 0.5) + 1
    small = np.ones(r + 1, bool)
    small[:2] = False
    for p in range(2, int(r ** 0.5) + 1):
        if small[p]:
            small[p * p::p] = False
    base = np.nonzero(small)[0]
    out = np.zeros(len(xs), np.int64)
    count, j = 0, 0
    for lo in range(0, top + 1, seg):
        hi = min(lo + seg, top + 1)
        sieve = np.ones(hi - lo, bool)
        if lo == 0:
            sieve[:2] = False
        for p in base:
            if p * p >= hi:
                break
            start = max(p * p, -(-lo // p) * p)
            sieve[start - lo::p] = False
        csum = np.cumsum(sieve)
        while j < len(xs) and xs[j] < hi:
            out[j] = count + csum[xs[j] - lo]
            j += 1
        count += int(csum[-1])
    return out


def bake_error(top=10**8, n=3000):
    from scipy.special import expi
    x = np.linspace(top / n, top, n).round().astype(np.int64)
    x = np.concatenate([[2, 10, 100, 1000, 2657, 10**4, 10**5, 10**6, 10**7], x])
    x = np.unique(x)
    pi = prime_counts(x, top)
    assert pi[np.searchsorted(x, 10**6)] == 78498 and pi[np.searchsorted(x, 10**8)] == 5761455
    li = expi(np.log(x.astype(float)))
    err = pi - li
    env = np.sqrt(x) * np.log(x) / (8 * np.pi)
    ok = x >= 2657
    assert np.all(np.abs(err[ok]) < env[ok]), "Schoenfeld's envelope must hold on the samples"
    g1 = float(np.load(ASSETS / "zeros.npy")[0])
    xf = x.astype(float)
    hyp = wave_fast(xf, g1, 0.8) + wave_fast(xf, g1, 0.2) - wave_fast(xf, g1, 0.5)
    np.savez_compressed(ASSETS / "error.npz", x=xf, pi=pi, li=li, err=err, env=env, hyp=hyp, gamma=g1)
    k = np.searchsorted(x, 10**8)
    print(f"error.npz: {len(x)} points to {top:.0e}; err(1e8) = {err[k]:.1f}, envelope {env[k]:.0f}, "
          f"hypothetical swing max {np.abs(hyp).max():.0f}; max |err|/env for x >= 2657: {np.max(np.abs(err[ok]) / env[ok]):.2f}")


def gaudin(s, m=40):
    """GUE nearest-neighbour spacing density p(s) = E''(s), E(s) = det(I - K_sine on [0, s]) (Gaudin), by Gauss-Legendre
    quadrature of the Fredholm determinant (Bornemann 2010) and a central second difference."""
    x0, w0 = np.polynomial.legendre.leggauss(m)

    def E(a):
        if a <= 0:
            return 1.0
        x, w = a / 2 * (x0 + 1), a / 2 * w0
        d = x[:, None] - x[None, :]
        K = np.sinc(d)                          # sin(pi d) / (pi d)
        return np.linalg.det(np.eye(m) - np.sqrt(w[:, None] * w[None, :]) * K)

    h = 1e-3
    return np.array([(E(v + h) - 2 * E(v) + E(v - h)) / h ** 2 if v > h else 0.0 for v in s])


def bake_spacing(T=5450.0, step=0.02):
    """spacing.npz (s24): every zero up to height T (sign changes of Z), the normalized gaps
    (g_{n+1} - g_n) ln(g_n / 2 pi) / 2 pi (mean 1), and Gaudin's GUE spacing density on [0, 3.2]."""
    from zmath import N_count, zeros_upto
    g = zeros_upto(T, step=step)
    n_smooth = float(N_count(T))
    assert abs(len(g) - n_smooth) < 3, (len(g), n_smooth)        # S(T) is small at this height: none missed
    gaps = np.diff(g) * np.log(g[:-1] / (2 * np.pi)) / (2 * np.pi)
    s = np.linspace(0, 3.2, 161)
    p = gaudin(s)
    assert abs(np.trapezoid(p, s) - 1) < 2e-3 and abs(np.trapezoid(s * p, s) - 1) < 5e-3
    np.savez(ASSETS / "spacing.npz", gammas=g, gaps=gaps, s=s, p=p)
    print(f"spacing.npz: {len(g)} zeros up to {T} (smooth count {n_smooth:.1f}), mean gap {gaps.mean():.4f}")


if __name__ == "__main__":
    import sys as _sys
    jobs = _sys.argv[1:] or ["explicit", "error"]
    if "explicit" in jobs:
        print(f"Ei vs mpmath: max relative error {check_ei():.1e}")
        bake_explicit()
    if "error" in jobs:
        bake_error()
    if "spacing" in jobs:
        bake_spacing()
