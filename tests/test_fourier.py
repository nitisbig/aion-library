"""Checks aion.fourier against the closed forms the video states on screen."""

import numpy as np
import pytest

from aion import fourier as F


def test_square_wave_gibbs():
    for n in (10, 50, 200, 1000):
        assert 1.178 < F.gibbs_peak(n) < 1.183
    assert abs((F.gibbs_peak(1000) - 1) / 2 - 0.0895) < 2e-4      # 8.95 % of the jump


def test_square_wave_first_radius():
    (n, r), *_ = F.square_wave_radii(4)
    assert n == 1 and abs(r - 4 / np.pi) < 1e-12 and abs(r - 1.273) < 1e-3


def test_square_loop_coefficients():
    c = F.coefficients(F.square_loop(4096), 40)
    nonzero = {n for n, v in c.items() if abs(v) > 1e-6}
    assert nonzero and all(n % 4 == 1 for n in nonzero)
    assert abs(c[1].real - 1.14632) < 1e-4
    for n in (-3, 5, -7, 9, -11):
        assert abs(abs(c[n]) - abs(c[1]) / n**2) < 1e-3
    assert c[-3].real < 0 and c[5].real < 0 and c[-7].real > 0


def test_rounded_square_spin_average():
    rs = {1: 1.0, -3: -1 / 9}
    z = F.partial_sum(rs, np.arange(1000) / 1000)
    for k, want in ((1, 1), (-3, -1 / 9), (2, 0), (0, 0), (3, 0)):
        assert abs(F.spin_average(z, k) - want) < 1e-12


def test_fft_matches_spin_average_and_reconstructs():
    rng = np.random.default_rng(3)
    true = {n: complex(*rng.normal(size=2)) / (1 + n * n) for n in range(-6, 7)}
    z = F.partial_sum(true, np.arange(256) / 256)
    c = F.coefficients(z, 6)
    for n in true:
        assert abs(c[n] - true[n]) < 1e-12
        assert abs(F.spin_average(z, n) - true[n]) < 1e-12
    t = np.linspace(0, 1, 37)
    assert np.allclose(F.partial_sum(c, t), F.partial_sum(true, t))


def test_chain_ends_at_pen_and_frame_freezes():
    c = {0: 0.5j, 1: 1.0, -1: 0.3, 2: 0.2j}
    for t in (0.0, 0.13, 0.71):
        j = F.chain_points(F.order_terms(c), t)
        assert abs(j[-1] - F.partial_sum(c, t)) < 1e-12
        # turned backward once, the speed-1 arm never moves
        assert abs(F.chain_points([(1, 1.0)], t, frame=1)[-1] - 1.0) < 1e-12


def test_order_terms():
    c = {0: 0.1, 1: 1.0, -1: 0.5, 2: 0.7, -2: 0.01}
    assert [n for n, _ in F.order_terms(c)] == [0, 1, 2, -1, -2]
    assert [n for n, _ in F.order_terms(c, "speed")] == [0, 1, -1, 2, -2]


def test_resample_and_bridge():
    sq = F.square_loop(400)
    r = F.resample(sq, 80)            # corners land on samples
    steps = np.abs(np.diff(np.append(r, r[0])))
    assert np.allclose(steps, 0.1, atol=1e-9)                     # perimeter 8 / 80
    inner = 0.3 * F.square_loop(40) + 0.2
    path = F.bridge([inner, sq])
    assert len(path) == len(sq) + len(inner) + 2


def test_heat_ring_mode_decay():
    th = np.pi / 2
    u0 = F.heat_ring(th, 0.0, n_terms=2000)
    assert abs(u0 - 1) < 1e-3
    # mode 3 fades 9× as fast as mode 1
    a1 = np.exp(-1 * 1 * 0.1)
    a3 = np.exp(-1 * 9 * 0.1)
    assert abs(np.log(a3) / np.log(a1) - 9) < 1e-12


def test_too_few_samples():
    with pytest.raises(ValueError):
        F.coefficients(np.zeros(10), 5)
