"""Every number video 018 speaks or plots, computed from the real maths and asserted in verify().

Run: uv run python videos/018-logarithms/logdata.py
"""
from __future__ import annotations

import math

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

# ---------------------------------------------------------------- c01 counting
DOUBLINGS = 10
CELLS = 2 ** DOUBLINGS                       # 1024
LOG2_6 = math.log2(6)                        # 2.585

# ---------------------------------------------------------------- c02 addition
POWERS_OF_TWO = [2 ** k for k in range(11)]  # table row, 1 … 1024
NAPIER_A, NAPIER_B = 8, 32                   # 2^3 · 2^5 = 2^8
NAPIER_PRODUCT = NAPIER_A * NAPIER_B         # 256
# Briggs lookup example (Mars-scale figures), rounded to the 4-place table shown on screen
BRIGGS_A, BRIGGS_B = 3.7124, 1.5236
BRIGGS_LOG_A = round(math.log10(BRIGGS_A), 4)
BRIGGS_LOG_B = round(math.log10(BRIGGS_B), 4)
BRIGGS_PRODUCT = BRIGGS_A * BRIGGS_B

# ---------------------------------------------------------------- c03 slide rule
LOG10_2 = math.log10(2)                      # 0.301, "nearly a third"
GUNTER_TICKS = {n: math.log10(n) for n in range(1, 11)}
SLIDE_EXAMPLES = [(2, 3), (3.5, 2.4)]
A_FREQS = [55 * 2 ** k for k in range(5)]    # 55 … 880 Hz

# ---------------------------------------------------------------- c04 curve
LOG10_MILLION, LOG10_BILLION = math.log10(1e6), math.log10(1e9)
STRETCH_10_TO_2 = 1 / math.log10(2)          # 3.32: log2 x = 3.32 log10 x


def digits(n: int) -> int:
    return math.floor(math.log10(n)) + 1


# ---------------------------------------------------------------- c05 area
def area(a: float, b: float) -> float:
    """Area under 1/t from a to b."""
    return quad(lambda t: 1 / t, a, b)[0]


A12, A13, A16, A36 = area(1, 2), area(1, 3), area(1, 6), area(3, 6)
E_FROM_AREA = brentq(lambda x: area(1, x) - 1, 2, 3, xtol=1e-12)
BERNOULLI_N = np.unique(np.logspace(0, 6, 61).astype(int))
BERNOULLI = (1 + 1 / BERNOULLI_N) ** BERNOULLI_N

# ---------------------------------------------------------------- c06 world
DB_STEP_POWER = 10 ** (10 / 10)              # +10 dB = ×10 power
POGSON = 100 ** (1 / 5)                      # 2.512 per magnitude
QUAKE_STEP_ENERGY = 10 ** 1.5                # 31.6 per magnitude
PH = {"lemon juice": 2.0, "coffee": 5.0, "water": 7.0, "baking soda": 9.0}
LEMON_VS_WATER = 10 ** (PH["water"] - PH["lemon juice"])  # 1e5

# Kepler's third law: semi-major axis (AU) and sidereal period (years), NASA planetary fact sheet
PLANETS = {
    "Mercury": (0.387, 0.2408), "Venus": (0.723, 0.6152), "Earth": (1.000, 1.0000),
    "Mars": (1.524, 1.8808), "Jupiter": (5.203, 11.862), "Saturn": (9.537, 29.457),
}
_a = np.log10([v[0] for v in PLANETS.values()])
_T = np.log10([v[1] for v in PLANETS.values()])
KEPLER_SLOPE, KEPLER_INTERCEPT = np.polyfit(_a, _T, 1)

# Atom to galaxy (metres)
SCALES = {"atom": 1.06e-10, "person": 1.7, "Earth": 1.2742e7, "Milky Way": 9.5e20}
SCALE_SPAN = math.log10(SCALES["Milky Way"] / SCALES["atom"])  # ≈ 31


# ---------------------------------------------------------------- worked examples (tutorial)
LOG3_81 = round(math.log(81, 3))                               # try-it-yourself: 4
TWO_100 = 2 ** 100                                             # 1267650600228229401496703205376
TWO_100_LOG = 100 * math.log10(2)                              # 30.103
SOLVE_2X_10 = 1 / math.log10(2)                                # 2^x = 10 → 3.3219
GROWTH_RATE = 0.07
DOUBLING_T = math.log(2) / GROWTH_RATE                         # 9.90 years (continuous)
CONCERT_RATIO = 10 ** ((90 - 60) / 10)                         # 1000× power
QUAKE_7_VS_5 = QUAKE_STEP_ENERGY ** 2                          # ≈ 1000× energy


def verify() -> None:
    assert CELLS == 1024 and math.log2(CELLS) == 10
    assert abs(LOG2_6 - 2.585) < 5e-4 and 2 < LOG2_6 < 3
    assert NAPIER_PRODUCT == 256 == 2 ** (3 + 5)
    assert abs(BRIGGS_LOG_A + BRIGGS_LOG_B - math.log10(BRIGGS_PRODUCT)) < 2e-4
    assert abs(LOG10_2 - 0.301) < 1e-3 and 0.29 < LOG10_2 < 1 / 3          # "nearly a third"
    assert abs(math.log10(2) + math.log10(3) - math.log10(6)) < 1e-12
    assert abs(3.5 * 2.4 - 8.4) < 1e-12
    assert A_FREQS == [55, 110, 220, 440, 880]
    assert round(LOG10_MILLION) == 6 and round(LOG10_BILLION) == 9
    assert digits(10 ** 9) == 10                                              # log is within one of digit count
    assert abs(STRETCH_10_TO_2 - 3.32) < 5e-3
    assert abs(A12 + A13 - A16) < 1e-9 and abs(A36 - A12) < 1e-9
    assert abs(A12 - 0.693) < 5e-4 and abs(A13 - 1.099) < 5e-4 and abs(A16 - 1.792) < 5e-4
    assert abs(E_FROM_AREA - math.e) < 1e-9 and f"{E_FROM_AREA:.5f}" == "2.71828"
    assert BERNOULLI[0] == 2 and abs(BERNOULLI[-1] - math.e) < 2e-6 and np.all(np.diff(BERNOULLI) > 0)
    assert DB_STEP_POWER == 10
    assert abs(POGSON - 2.512) < 1e-3 and abs(POGSON ** 5 - 100) < 1e-9
    assert abs(QUAKE_STEP_ENERGY - 31.6) < 0.05                               # "about thirty two times"
    assert LEMON_VS_WATER == 1e5                                              # "a hundred thousand"
    assert abs(KEPLER_SLOPE - 1.5) < 2e-3                                     # "three steps for every two"
    assert round(SCALE_SPAN) == 31
    assert 3 ** LOG3_81 == 81 and LOG3_81 == 4
    assert len(str(TWO_100)) == 31 and str(TWO_100) == "1267650600228229401496703205376"
    assert abs(TWO_100_LOG - 30.103) < 1e-3 and 10 ** 30 < TWO_100 < 10 ** 31
    assert abs(2 ** SOLVE_2X_10 - 10) < 1e-9 and abs(SOLVE_2X_10 - 3.32) < 5e-3
    assert abs(DOUBLING_T - 9.9) < 0.01 and abs(math.exp(GROWTH_RATE * DOUBLING_T) - 2) < 1e-12
    assert abs(CONCERT_RATIO - 1000) < 1e-9
    assert abs(QUAKE_7_VS_5 - 1000) < 1e-6                                            # "thirty one powers of ten"


if __name__ == "__main__":
    verify()
    print(f"ok · log2 6 = {LOG2_6:.4f} · e (area) = {E_FROM_AREA:.10f} · Kepler slope = {KEPLER_SLOPE:.4f} · "
          f"span = {SCALE_SPAN:.2f} decades · Briggs {BRIGGS_LOG_A}+{BRIGGS_LOG_B} → {BRIGGS_PRODUCT:.4f}")
