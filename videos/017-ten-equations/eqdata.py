"""Every number video 017 says or shows, computed from the physics (run `uv run python videos/017-ten-equations/eqdata.py`).

Scenes and style frames import these values; `verify()` asserts the rounded figures used in the narration.
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------- constants (CODATA 2018 / IERS)
C = 299_792_458.0                  # m/s
MU0 = 1.25663706212e-6             # N/A^2
EPS0 = 8.8541878128e-12            # F/m
GM_EARTH = 3.986004418e14          # m^3/s^2
R_EARTH = 6_371_000.0              # m (mean)
GPS_RADIUS = 26_561_750.0          # m (semi-major axis of the GPS orbit, ~20,200 km altitude)
DAY = 86_400.0


def c_from_maxwell() -> float:
    """Ch 1: the wave speed that falls out of Maxwell's equations, 1/sqrt(mu0 eps0)."""
    return 1.0 / math.sqrt(MU0 * EPS0)


def gamma(v_over_c: float) -> float:
    """Ch 6: the time-dilation factor 1/sqrt(1 - v^2/c^2)."""
    return 1.0 / math.sqrt(1.0 - v_over_c ** 2)


def gps_drift() -> dict:
    """Ch 6: GPS clock rates against a clock on the ground, microseconds per day (first order, ignores Earth's spin)."""
    v = math.sqrt(GM_EARTH / GPS_RADIUS)
    speed = -0.5 * v ** 2 / C ** 2 * DAY * 1e6
    gravity = GM_EARTH * (1 / R_EARTH - 1 / GPS_RADIUS) / C ** 2 * DAY * 1e6
    net = speed + gravity
    return {"v_km_s": v / 1e3, "speed_us": speed, "gravity_us": gravity, "net_us": net,
            "range_error_km": net * 1e-6 * C / 1e3}


def muon(v_over_c: float = 0.995, tau_us: float = 2.197) -> dict:
    """Ch 6: mean distance a muon covers before decaying, without and with time dilation."""
    d0 = v_over_c * C * tau_us * 1e-6
    return {"no_dilation_m": d0, "with_dilation_m": d0 * gamma(v_over_c), "gamma": gamma(v_over_c)}


def bayes_test(n: int = 1000, prevalence: float = 0.01, sensitivity: float = 0.90, false_pos: float = 0.09) -> dict:
    """Ch 9: the medical-test example with whole people."""
    ill = round(n * prevalence)
    true_pos = round(ill * sensitivity)
    healthy = n - ill
    false_pos_n = round(healthy * false_pos)
    p = true_pos / (true_pos + false_pos_n)
    return {"ill": ill, "true_pos": true_pos, "healthy": healthy, "false_pos": false_pos_n,
            "p_ill_given_pos": p, "one_in": 1 / p, "exact": prevalence * sensitivity /
            (prevalence * sensitivity + (1 - prevalence) * false_pos)}


def shannon(bandwidth_hz: float, snr: float) -> float:
    """Ch 8: channel capacity C = B log2(1 + S/N), bits per second."""
    return bandwidth_hz * math.log2(1 + snr)


def option_payoff(price: float, strike: float = 100.0) -> float:
    """Ch 10: value at expiry of the right to buy at `strike`."""
    return max(price - strike, 0.0)


def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Ch 10: the closed-form value of a European call (solution of the Black-Scholes equation)."""
    if T <= 0:
        return max(S - K, 0.0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))  # noqa: E731
    return S * N(d1) - K * math.exp(-r * T) * N(d2)


# ---------------------------------------------------------------- facts stated in the narration (sources in plan)
FACTS = {
    "maxwell_year": 1865, "einstein_gr_year": 1915, "eclipse_year": 1919, "ligo_year": 2015,
    "schrodinger_year": 1926, "fourier_year": 1807, "special_relativity_year": 1905, "cauchy_year": 1847,
    "shannon_year": 1948, "bayes_published": 1763, "af447_found": 2011, "black_scholes_year": 1973,
    "nobel_year": 1997, "millennium_prize_usd": 1_000_000,
    "light_bending_arcsec": 1.75, "mercury_arcsec_per_century": 43,
    "voyager1_km_late_2026": 25.6e9,      # ~171 AU; narration says "more than twenty four billion kilometres"
    "voyager_tx_watts": 22.4,             # narration: "about twenty watts"
    "ligo_strain": 1.0e-21, "ligo_arm_m": 4000.0, "proton_diameter_m": 1.7e-15,
}


def verify() -> None:
    """Assert every rounded figure the narration speaks."""
    c = c_from_maxwell()
    assert abs(c - C) / C < 1e-9, c
    g = gps_drift()
    assert 7.0 < -g["speed_us"] < 7.4, g                  # "about seven millionths of a second a day"
    assert 45.0 < g["gravity_us"] < 46.0, g               # "about forty five millionths"
    assert 38.0 < g["net_us"] < 39.0, g
    assert g["range_error_km"] > 10, g                    # "more than ten kilometres every day"
    mu = muon()
    assert mu["no_dilation_m"] < 700 and mu["with_dilation_m"] > 6000, mu
    b = bayes_test()
    assert (b["ill"], b["true_pos"], b["false_pos"]) == (10, 9, 89), b   # "ten are ill, nine test positive … eighty nine"
    assert 10.5 < b["one_in"] < 11.5, b                   # "about one in eleven"
    wifi = shannon(20e6, 1000)                            # a 20 MHz channel at 30 dB
    assert 195e6 < wifi < 205e6, wifi                     # shown on screen as ~200 Mbit/s
    assert option_payoff(150) == 50 and option_payoff(80) == 0   # "climbs to one fifty … worth fifty"
    ligo = FACTS["ligo_strain"] * FACTS["ligo_arm_m"]
    assert ligo < FACTS["proton_diameter_m"] / 100        # "smaller than a hundredth of a proton"
    assert FACTS["voyager1_km_late_2026"] > 24e9
    assert 2026 - FACTS["black_scholes_year"] < 60 and 2026 - FACTS["bayes_published"] > 200  # "about fifty" / "over two hundred"


if __name__ == "__main__":
    verify()
    g, mu, b = gps_drift(), muon(), bayes_test()
    print(f"c = {c_from_maxwell():.6e} m/s")
    print(f"GPS: v = {g['v_km_s']:.2f} km/s, speed {g['speed_us']:+.2f} us/day, gravity {g['gravity_us']:+.2f}, "
          f"net {g['net_us']:+.2f} us/day -> {g['range_error_km']:.1f} km/day")
    print(f"muon: gamma {mu['gamma']:.1f}, {mu['no_dilation_m']:.0f} m -> {mu['with_dilation_m'] / 1e3:.1f} km")
    print(f"Bayes: {b['true_pos']} true + {b['false_pos']} false positives -> {b['p_ill_given_pos']:.1%} (1 in {b['one_in']:.1f})")
    print(f"Shannon 20 MHz @ 30 dB: {shannon(20e6, 1000) / 1e6:.0f} Mbit/s")
    print(f"BS call S=K=100, T=1, r=3%, sigma=20%: {black_scholes_call(100, 100, 1, 0.03, 0.2):.2f}")
    print("verify() passed")
