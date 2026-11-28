"""Every number spoken or shown in video 014 is computed or sourced and checked here.

Run: uv run python videos/014-riemann-hypothesis/verify.py   (from the repo root)
Writes assets/cast.json (numbers the scenes import) and assets/zeros.npy (zero ordinates up to height 1000).
Sourced constants (not computable) carry their source and the date checked; see research.md.
"""
import json
from pathlib import Path

import mpmath as mp
import numpy as np

from zmath import (N_count, hardy_Z, li, pi_explicit, prime_pi, primes_upto, riemann_R, theta, zeta,
                   zeros_upto)

HERE = Path(__file__).parent
CAST = {}
checks = 0


def ok(name, cond):
    global checks
    assert bool(cond), f"FAILED: {name}"
    checks += 1
    print(f"  ok  {name}")


def section(title):
    print(f"\n{title}")


mp.mp.dps = 30

# ---------------------------------------------------------------- ζ reference vs mpmath
section("zeta: float64 reference vs mpmath")
pts = np.array([2, 3 + 4j, 0.5 + 14.134725j, 0.5 + 100j, 0.25 + 30j, 0.9 + 60j, -1, -3.5 + 2j, -8 + 20j,
                0.5 + 500j, 1.5 + 999j, 0.1 + 0.1j])
mine = zeta(pts)
for s, z in zip(pts, mine):
    ref = complex(mp.zeta(complex(s)))
    err = abs(z - ref) / max(1, abs(ref))
    ok(f"zeta({s}) rel err {err:.1e}", err < 1e-9)
ok("Basel: zeta(2) = pi^2/6", abs(zeta(np.array([2 + 0j]))[0] - np.pi ** 2 / 6) < 1e-12)
ok("zeta(-1) = -1/12 by continuation", abs(zeta(np.array([-1 + 0j]))[0] + 1 / 12) < 1e-12)
for n in (2, 4, 6, 8, 10):
    ok(f"trivial zero at -{n}", abs(zeta(np.array([-n + 0j]))[0]) < 1e-12)
CAST["basel"] = float(np.pi ** 2 / 6)

# functional-equation mirror symmetry of |ξ|: zeros come in mirror pairs about Re = 1/2
sig = np.array([0.3 + 21.0j, 0.7 + 21.0j])
ok("conjugate symmetry zeta(conj s) = conj zeta(s)",
   abs(zeta(np.array([0.3 - 21j]))[0] - np.conj(zeta(np.array([0.3 + 21j]))[0])) < 1e-10)

# ---------------------------------------------------------------- zeros on the line
section("nontrivial zeros (sign changes of Hardy's Z)")
g = zeros_upto(1000.0)
ref_first = [float(mp.im(mp.zetazero(n))) for n in range(1, 6)]
for n, r in enumerate(ref_first, 1):
    ok(f"zero #{n} at 1/2 + {g[n-1]:.6f} i (mpmath {r:.6f})", abs(g[n - 1] - r) < 1e-8)
N1000 = int(round(N_count(1000.0) - 0.0))
ok(f"found {len(g)} zeros up to height 1000; Riemann–von Mangoldt predicts ≈ {N_count(1000.0):.2f}",
   abs(len(g) - N_count(1000.0)) < 2)
ok("count up to 1000 is 649 (known)", len(g) == 649)
ok("first zero ≈ 14.1347", abs(g[0] - 14.134725141734693) < 1e-9)
ok("|zeta| at the first five zeros < 1e-9", np.all(np.abs(zeta(0.5 + 1j * g[:5])) < 1e-9))
np.save(HERE / "assets" / "zeros.npy", g)
CAST["zeros_first10"] = [round(float(x), 6) for x in g[:10]]
CAST["zeros_upto_1000"] = len(g)
gaps = np.diff(g)
CAST["min_gap_upto_1000"] = float(gaps.min())

# ---------------------------------------------------------------- primes, gaps, PNT
section("primes and the prime number theorem")
P = primes_upto(2_000_000)
ok("25 primes below 100", prime_pi(100) == 25)
ok("168 primes below 1000", prime_pi(1000) == 168)
ok("78,498 primes below one million", prime_pi(1_000_000) == 78498)
p100 = P[P < 100]
gap = np.diff(p100)
ok("largest gap below 100 is 8, from 89 to 97", gap.max() == 8 and p100[np.argmax(gap)] == 89)
p1000 = P[P < 1000]
g1000 = np.diff(p1000)
ok("largest gap below 1000 is 20, from 887 to 907", g1000.max() == 20 and p1000[np.argmax(g1000)] == 887)
CAST["twins_below_100"] = int(np.sum(gap == 2))
for x in (1e3, 1e6):
    r1 = prime_pi(x) / (x / np.log(x))
    r2 = prime_pi(x) / li(x)
    print(f"       x={x:.0e}: pi={prime_pi(x)}, x/ln x ratio {r1:.4f}, li ratio {r2:.5f}")
ok("li(x) beats x/ln x at one million", abs(prime_pi(1e6) / li(1e6) - 1) < abs(prime_pi(1e6) / (1e6 / np.log(1e6)) - 1))
CAST["pnt_1e6"] = {"pi": 78498, "x_over_ln": float(1e6 / np.log(1e6)), "li": float(li(1e6))}

# Gauss's density: about 1 in ln x numbers near x are prime
x0 = 1_000_000
dens = (prime_pi(x0 + 50_000) - prime_pi(x0 - 50_000)) / 100_000
ok(f"density near a million {dens:.4f} ≈ 1/ln(1e6) = {1/np.log(x0):.4f}", abs(dens * np.log(x0) - 1) < 0.03)

# ---------------------------------------------------------------- error terms (s05, s13, s15)
section("the error pi(x) - li(x)")
xs = np.arange(2, 1_000_001, dtype=float)
err = prime_pi(xs) - li(xs)
ok("pi(x) < li(x) for every 2 < x ≤ 10^6 (Littlewood: this flips eventually)", np.all(err[xs > 2] < 0))
xs2 = xs[xs >= 2657]
bound = np.sqrt(xs2) * np.log(xs2) / (8 * np.pi)
ok("Schoenfeld envelope (assuming RH) holds for 2657 ≤ x ≤ 10^6", np.all(np.abs(prime_pi(xs2) - li(xs2)) < bound))
CAST["schoenfeld_from"] = 2657

# ---------------------------------------------------------------- explicit formula (s01, s14)
section("the explicit formula: waves rebuild the staircase")
x_mid = np.arange(2.5, 100, 1.0)  # half-integers: never on a prime
truth = prime_pi(x_mid)
R_only = pi_explicit(x_mid, [])
e0 = np.max(np.abs(R_only - truth))
recon = {}
for k in (1, 5, 30, 100, 200):
    est = pi_explicit(x_mid, g[:k])
    recon[k] = float(np.max(np.abs(est - truth)))
    print(f"       {k:>3} zero pairs: max |error| on half-integers below 100 = {recon[k]:.3f}")
ok(f"the smooth curve alone misses steps by up to {e0:.2f}", e0 > 0.8)
ok("errors shrink as zeros are added", recon[200] < recon[100] < recon[30] < recon[5] < e0)
ok("100 zero pairs round to the exact count at every half-integer below 100", recon[100] < 0.3)
CAST["explicit_errors"] = {"R": float(e0), **{str(k): v for k, v in recon.items()}}

# moving a zero off the line (s15): its wave grows like x^sigma
xs3 = np.array([1e2, 1e4, 1e6, 1e8])
CAST["offline_growth"] = {"sqrt": [float(v) for v in xs3 ** 0.5], "x08": [float(v) for v in xs3 ** 0.8]}
ok("an off-line zero at sigma=0.8 outgrows the sqrt envelope by 10^6", 1e6 ** 0.8 > 1e6 ** 0.5 * np.log(1e6))

# ---------------------------------------------------------------- the image of the critical line (s12)
section("zeta along the critical line")
t = np.linspace(0, 40, 4001)
w = zeta(0.5 + 1j * t)
ok("the curve zeta(1/2+it) passes within 1e-2 of 0 near each zero below 40",
   all(np.min(np.abs(w[np.abs(t - z) < 0.02])) < 1e-2 for z in g[g < 40]))
ok("Z(t) is real-valued and changes sign at the first zero",
   hardy_Z(np.array([14.0]))[0] * hardy_Z(np.array([14.3]))[0] < 0)

ok("spoken heights: fourteen, twenty-one, twenty-five, thirty, thirty-three, thirty-eight",
   [int(round(x)) for x in g[:6]] == [14, 21, 25, 30, 33, 38])
ok("li(10^6) is within two tenths of a percent of pi(10^6)", abs(prime_pi(1e6) / li(1e6) - 1) < 0.002)


# ---------------------------------------------------------------- the atoms (s04)
section("unique factorization and Euclid's argument (s04)")


def factor(n):
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    return out + ([n] if n > 1 else [])


ok("60 = 2·2·3·5", factor(60) == [2, 2, 3, 5])
ok("both factor trees of 60 end in the same leaves", sorted(factor(6) + factor(10)) == sorted(factor(4) + factor(15)))
ok("2·3·5·7 + 1 = 211, which is prime", 2 * 3 * 5 * 7 + 1 == 211 and factor(211) == [211])
ok("211 leaves remainder 1 when divided by 2, 3, 5 and 7", all(211 % p == 1 for p in (2, 3, 5, 7)))
ok("2·3·5·7·11·13 + 1 = 30031 = 59·509: not prime, and both factors are new",
   2 * 3 * 5 * 7 * 11 * 13 + 1 == 30031 and factor(30031) == [59, 509])
ok("after 89, the seven numbers 90-96 are all composite", all(len(factor(n)) > 1 for n in range(90, 97)))
CAST["euclid"] = {"product_2357": 210, "plus_one": 211, "next": 30031, "next_factors": [59, 509]}

# ---------------------------------------------------------------- the Euler product's domain (s19)
section("the product over primes settles where the sum works, and wanders in the strip (s19)")
pr = P[P < 100_000].astype(float)


def partial_products(s):
    return np.cumprod(1.0 / (1.0 - pr ** (-s)))


right = partial_products(2 + 5j)
ok("at s = 2+5i, the product over primes below 10^5 matches zeta to 1e-5",
   abs(right[-1] - zeta(np.array([2 + 5j]))[0]) < 1e-5)
inside = partial_products(0.5 + 20j)
tail = np.abs(np.log(inside[pr > 1e4]))
ok(f"at s = 1/2+20i, |log| of the partial products still swings by {np.ptp(tail):.2f} between 10^4 and 10^5",
   np.ptp(tail) > 0.3)

# ---------------------------------------------------------------- Lehmer's near-miss (s20)
section("Lehmer's near-miss near height 7005 (s20)")
from scipy.optimize import brentq  # noqa: E402

tl = np.arange(7004.9, 7005.3, 0.0005)
zl = hardy_Z(tl)
cross = np.where(np.sign(zl[:-1]) != np.sign(zl[1:]))[0]
roots = [brentq(lambda u: float(hardy_Z(np.array([u]))[0]), tl[i], tl[i + 1], xtol=1e-12) for i in cross]
pair = [r for r in roots if 7005.0 < r < 7005.2]
ok("exactly two crossings between 7005.0 and 7005.2", len(pair) == 2)
a, b = pair
ref = [float(mp.im(mp.zetazero(n))) for n in (6709, 6710)]
ok(f"they are zeros #6709 and #6710 ({a:.6f}, {b:.6f}; mpmath {ref[0]:.6f}, {ref[1]:.6f})",
   abs(a - ref[0]) < 1e-6 and abs(b - ref[1]) < 1e-6)
mean_gap = 2 * np.pi / np.log(a / (2 * np.pi))
ok(f"gap {b - a:.4f} vs average {mean_gap:.4f}: about 24 times closer ({mean_gap / (b - a):.2f})",
   23.0 < mean_gap / (b - a) < 24.5)
tb = np.linspace(a, b, 4001)
zb = hardy_Z(tb)
peak = zb[np.argmax(np.abs(zb))]
ok(f"between them Z climbs only {peak:+.5f} above zero ('four thousandths')", 0.0035 < peak < 0.0045)
CAST["lehmer"] = {"zeros": [a, b], "gap": b - a, "mean_gap": float(mean_gap), "peak": float(peak)}

# ---------------------------------------------------------------- the clock-arithmetic version (s22)
section("y^2 = x^3 + x + 1 in clock arithmetic: |A_p - p| ≤ 2 sqrt(p) (s22)")


def affine_count(p):
    sq = np.zeros(p, dtype=np.int64)
    np.add.at(sq, (np.arange(p, dtype=np.int64) ** 2) % p, 1)
    x = np.arange(p, dtype=np.int64)
    return int(sq[(x ** 3 + x + 1) % p].sum())


ok("p = 101: 104 solutions", affine_count(101) == 104)
good = [int(p) for p in P[P < 5000] if p not in (2, 31)]  # discriminant -16·31: bad reduction at 2 and 31
ratios = np.array([(affine_count(p) - p) / (2 * np.sqrt(p)) for p in good])
ok(f"every one of the {len(good)} good primes below 5000 obeys the bound (max {np.abs(ratios).max():.4f})",
   np.all(np.abs(ratios) <= 1))
ok("the two bad primes obey it too (2 and 31)", all(abs(affine_count(p) - p) <= 2 * np.sqrt(p) for p in (2, 31)))
CAST["hasse"] = {"p101": 104, "primes_checked": len(good) + 2, "max_ratio": float(np.abs(ratios).max())}

# ---------------------------------------------------------------- Robin's criterion (s27)
section("Robin's inequality sigma(n) < e^gamma n ln ln n for n > 5040 (s27)")
NR = 1_000_000
sig = np.zeros(NR + 1, dtype=np.int64)
for d in range(1, NR + 1):
    sig[d::d] += d
eg = float(mp.exp(mp.euler))
nn = np.arange(3, NR + 1)
above = nn[sig[3:] >= eg * nn * np.log(np.log(nn))]
ok(f"sigma(5040) = {sig[5040]} exceeds e^gamma·5040·ln ln 5040 = {eg * 5040 * np.log(np.log(5040)):.1f}",
   sig[5040] == 19344 and sig[5040] > eg * 5040 * np.log(np.log(5040)))
ok("the inequality holds for every n from 5041 to 10^6", above.max() == 5040)
ok("26 exceptions from 3 to 5040 (the known list)", len(above) == 26)
CAST["robin"] = {"e_gamma": eg, "sigma_5040": 19344, "last_exception": 5040}

# ---------------------------------------------------------------- 100% is not all (s21)
section("density vs all (s21)")
ok("squares are 10% of 1..100 and 1% of 1..10,000", 10 / 100 == 0.10 and 100 / 10_000 == 0.01)

# ---------------------------------------------------------------- sourced constants (research.md has the links)
section("sourced constants")
SOURCED = {
    "riemann_year": 1859,
    "riemann_pages": 9,                      # Wikipedia, On the Number of Primes… (checked 2026-11-21)
    "years_open": 2026 - 1859,
    "euler_product_year": 1737,              # Wikipedia, Prime number theorem ("as early as 1737")
    "basel_year": 1734,                      # Wikipedia, Basel problem
    "gauss_years": "1792 or 1793",           # Wikipedia, Prime number theorem (his 1849 recollection)
    "pnt_year": 1896,                        # Hadamard; de la Vallée Poussin
    "hardy_year": 1914, "selberg_year": 1942, "levinson_year": 1974, "conrey_year": 1989,
    "przz_year": 2020, "przz_fraction": "5/12",
    "claude_bound_announced": "2026-08-10",  # anthropic.com/research/riemann-zeta
    "claude_bound_post": "41.6% -> 67.2%",
    "alpoge_furman": "≥ 2/3 simple and on the line; 0.6725 with the Montgomery–Taylor window",  # arXiv 2608.13637
    "lamzouri": "> 67.25%",                  # arXiv 2609.02882
    "zeros_checked": "10^13",                # claymath.org (Gourdon 2004)
    "platt_trudgian_height": "3e12",         # arXiv 2004.09765
    "rh_claim_date": "2026-11-20",
    "lean_files": 175_187, "lean_declarations": 1_468_418,       # math.mit.edu/~drew/grh (2026-11-21 09:30 UTC)
    "lean_archive_bytes": 239_275_554, "lean_export_bytes": 61_570_595_788,
    "clay_prize_usd": 1_000_000, "clay_wait_years": 2,           # Clay Millennium Prize rules
    # v2 history (research.md M16-M26, H1-H3)
    "euclid": "c. 300 BC (Elements IX.20)", "gauss_born": 1777, "riemann_notes_siegel": 1932,
    "hilbert_year": 1900, "clay_year": 2000, "turing": "computed 1950, published 1953",
    "von_koch_year": 1901, "schoenfeld_year": 1976, "littlewood_year": 1914,
    "no_flip_below": "1e19 (Büthe 2015)", "flip_before": "1.4e316 (Saouter–Demichel 2010)",
    "lehmer_year": 1956, "newman_year": 1976, "rodgers_tao_year": 2018,
    "hasse_year": 1933, "weil": "1940 note, 1948 proof", "deligne_year": 1974, "stepanov_year": 1969,
    "cramer_year": 1920, "miller_year": 1976, "robin_year": 1984, "lagarias_year": 2002, "montgomery_year": 1973,
    "lamzouri_posted": "2026-09-02", "alpoge_note_pages": 4,
    "sutherland_status": "2026-11-21 09:30 UTC: compile, leanchecker, nanoda, con-leche, lean4lean pass; "
                         "comparator and default/paranoid kernel replays running; Robin/Lagarias combination: "
                         "nanoda and con-leche accept, comparator running",
}
ok("2026 - 1859 = 167 years", SOURCED["years_open"] == 167)
ok("Gauss was a teenager in 1792 (born 1777)", 13 <= 1792 - SOURCED["gauss_born"] <= 19)
ok("a crossing before 1.4e316: a number with more than three hundred digits", len(str(14 * 10 ** 315)) > 300)
ok("ten quintillion is 10^19", 10 * 10 ** 18 == 10 ** 19)
ok("5/12 is just under 42%", 41 < 5 / 12 * 100 < 42)
ok("5/12 rounds to 41.7%", round(5 / 12 * 100, 1) == 41.7)
ok("2/3 rounds to 66.7%", round(2 / 3 * 100, 1) == 66.7)
ok("export is 'more than 61.5 GB'", SOURCED["lean_export_bytes"] > 61.5e9)
CAST["sourced"] = SOURCED

(HERE / "assets").mkdir(exist_ok=True)
(HERE / "assets" / "cast.json").write_text(json.dumps(CAST, indent=1))
print(f"\n{checks} checks passed. Wrote assets/cast.json and assets/zeros.npy")
