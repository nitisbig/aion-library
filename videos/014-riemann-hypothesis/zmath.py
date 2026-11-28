"""Fast float64 maths for video 014: zeta, Hardy's Z, zeros, prime counting, the explicit formula.

Every function is vectorized numpy and checked against mpmath in verify.py.
Scenes, the design sheet and the bakes import from here, never retyping numbers.

Example:
    from zmath import zeta, zeros_upto, prime_pi
    zeta(np.array([0.5 + 14.134725j]))   # ≈ 0
"""
from functools import lru_cache
from math import factorial

import numpy as np
from scipy.special import bernoulli, expi, loggamma

_B = bernoulli(40)


def _zeta_em(s, N=None, M=12):
    """Euler–Maclaurin ζ(s) for Re(s) ≥ ~0 (s ≠ 1). Accurate to ~1e-12 for |Im s| ≤ 2πN/3."""
    s = np.asarray(s, dtype=complex)
    if N is None:
        N = int(max(30, np.max(np.abs(s.imag)) / np.pi + 30)) if s.size else 30
    n = np.arange(1, N, dtype=float)
    flat = s.reshape(-1)
    out = np.empty_like(flat)
    logn = np.log(n)
    chunk = max(1, int(2_000_000 // N))  # keep the outer product near 32 MB
    for i0 in range(0, flat.size, chunk):
        ss = flat[i0:i0 + chunk]
        head = np.exp(-np.outer(ss, logn)).sum(axis=1)
        Ns = np.exp(-ss * np.log(N))
        tail = N * Ns / (ss - 1) + 0.5 * Ns
        term = ss * Ns / N  # s · N^{-s-1}
        acc = np.zeros_like(ss)
        for k in range(1, M + 1):
            acc += _B[2 * k] / factorial(2 * k) * term
            term = term * (ss + 2 * k - 1) * (ss + 2 * k) / (N * N)
        out[i0:i0 + chunk] = head + tail + acc
    return out.reshape(s.shape)


def zeta(s):
    """ζ(s) on the whole plane (s ≠ 1): Euler–Maclaurin for Re ≥ 1/2, functional equation below.

    Example:
        zeta(np.array([2.0 + 0j]))  # π²/6
    """
    s = np.asarray(s, dtype=complex)
    out = np.empty_like(s)
    right = s.real >= 0.5
    if right.any():
        out[right] = _zeta_em(s[right])
    if (~right).any():
        sl = s[~right]
        z1 = _zeta_em(1 - sl)
        # ζ(s) = 2^s π^{s-1} sin(πs/2) Γ(1-s) ζ(1-s); computed in logs to survive large |t|
        logf = sl * np.log(2) + (sl - 1) * np.log(np.pi) + loggamma(1 - sl)
        out[~right] = np.exp(logf) * np.sin(np.pi * sl / 2) * z1
    return out


def theta(t):
    """Riemann–Siegel theta: θ(t) = Im log Γ(1/4 + it/2) − (t/2) log π."""
    t = np.asarray(t, dtype=float)
    return loggamma(0.25 + 0.5j * t).imag - 0.5 * t * np.log(np.pi)


def hardy_Z(t):
    """Hardy's Z(t) = e^{iθ(t)} ζ(1/2 + it): real, and its sign changes are the zeros on the line."""
    t = np.asarray(t, dtype=float)
    return (np.exp(1j * theta(t)) * zeta(0.5 + 1j * t)).real


def N_count(T):
    """Riemann–von Mangoldt smooth count θ(T)/π + 1 (the number of zeros up to height T, up to S(T))."""
    return theta(T) / np.pi + 1


@lru_cache(maxsize=4)
def zeros_upto(T, step=0.02):
    """Ordinates γ of the nontrivial zeros 1/2 + iγ with 0 < γ ≤ T (sign changes of Z, Brent-refined)."""
    from scipy.optimize import brentq

    ts = np.arange(10.0, T + step, step)
    Z = hardy_Z(ts)
    idx = np.nonzero(np.sign(Z[:-1]) != np.sign(Z[1:]))[0]
    f = lambda x: float(hardy_Z(np.array([x]))[0])
    return np.array([brentq(f, ts[i], ts[i + 1], xtol=1e-12) for i in idx])


def primes_upto(n):
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    return np.nonzero(sieve)[0]


def prime_pi(x, _cache={}):
    """π(x) for an array of real x ≤ cached limit."""
    x = np.asarray(x, dtype=float)
    lim = int(np.max(x)) + 1
    if _cache.get("lim", 0) < lim:
        _cache["p"], _cache["lim"] = primes_upto(lim), lim
    return np.searchsorted(_cache["p"], x, side="right")


def li(x):
    """Logarithmic integral li(x) = Ei(log x)."""
    return expi(np.log(np.asarray(x, dtype=float)))


def mobius_upto(n):
    mu = np.ones(n + 1, dtype=int)
    for p in primes_upto(n):
        mu[p::p] *= -1
        mu[p * p::p * p] = 0
    return mu


def riemann_R(x, terms=60):
    """Riemann's R(x) = Σ μ(n)/n · li(x^{1/n}), the smooth part of the staircase."""
    x = np.asarray(x, dtype=float)
    mu = mobius_upto(terms)
    out = np.zeros_like(x)
    for n in range(1, terms + 1):
        if mu[n]:
            out += mu[n] / n * li(x ** (1.0 / n))
    return out


def _ei_complex(z):
    """Ei(z) for complex z with Im z ≠ 0, via mpmath (exact branch); vectorized by loop."""
    import mpmath as mp

    return np.array([complex(mp.ei(complex(v))) for v in np.ravel(z)]).reshape(np.shape(z))


def wave(x, gamma, sigma=0.5, terms=6):
    """The contribution of one conjugate pair ρ = σ ± iγ to π(x): −2 Re Σ μ(n)/n · Ei(ρ log x / n).

    Example:
        wave(np.array([50.5]), 14.134725)
    """
    x = np.asarray(x, dtype=float)
    mu = mobius_upto(terms)
    rho = sigma + 1j * gamma
    out = np.zeros_like(x)
    for n in range(1, terms + 1):
        if mu[n]:
            out += -2 * mu[n] / n * _ei_complex(rho * np.log(x) / n).real
    return out


def pi_explicit(x, gammas, terms=6):
    """Riemann's explicit formula, truncated: R(x) − Σ_ρ R(x^ρ) − 1/ln x + arctan(π/ln x)/π.

    The last two terms are the trivial zeros' small contribution. Used for the s01/s14 staircase.
    """
    x = np.asarray(x, dtype=float)
    out = riemann_R(x) - 1 / np.log(x) + np.arctan(np.pi / np.log(x)) / np.pi
    for g in gammas:
        out = out + wave(x, g, terms=terms)
    return out


def domain_rgb(w, sat=0.85):
    """Domain coloring used by the design sheet and as the shader's reference: hue = arg, log₂ rings."""
    from matplotlib.colors import hsv_to_rgb

    r = np.abs(w)
    hue = (np.angle(w) / (2 * np.pi)) % 1.0
    ring = np.mod(np.log2(np.maximum(r, 1e-12)), 1.0)
    shade = 0.78 + 0.22 * ring
    val = shade * (1 - np.exp(-3 * r)) ** 0.6
    hsv = np.stack([hue, np.full_like(hue, sat), np.clip(val, 0, 1)], axis=-1)
    return hsv_to_rgb(hsv)
