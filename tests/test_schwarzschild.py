"""Checks aion.maths.schwarzschild against the numbers the black-hole video states on screen."""

import numpy as np

from aion.maths import schwarzschild as S


def test_radii_said_out_loud():
    assert abs(S.schwarzschild_radius(S.M_EARTH) - 8.87e-3) < 2e-5        # "nine millimetres"
    assert abs(S.schwarzschild_radius(S.M_SUN) - 2953.0) < 2.0            # "three kilometres"
    assert abs(S.escape_velocity(S.M_EARTH, 6.371e6) - 11186.0) < 10.0    # "eleven kilometres every second"
    rs = S.schwarzschild_radius(S.M_SUN)
    assert abs(S.escape_velocity(S.M_SUN, rs) - S.C_LIGHT) < 1e-3         # v_esc(r_s) = c


def test_sun_grazing_ray():
    a = S.sun_grazing_arcsec()
    assert abs(a - 1.751) < 2e-3                                          # "one point seven five arc seconds"
    assert abs(0.02 / (a * S.ARCSEC) - 2356.0) < 5.0                      # a 2 cm coin at about 2.4 km


def test_straight_line_without_mass():
    phi, u, fate = S.orbit(3.0, rs=0.0)
    assert fate == "escape" and abs(phi[-1] - np.pi) < 1e-9
    assert np.max(abs(u - np.sin(phi) / 3.0)) < 1e-9                      # u = sin φ / b
    pts, _ = S.ray(3.0, rs=0.0, r_max=10)
    assert np.max(abs(pts[:, 1] - 3.0)) < 1e-5                            # y = b all the way


def test_three_fates_and_critical_aim():
    bc = S.critical_b(2.0)
    assert abs(bc - np.sqrt(27.0)) < 1e-12 and abs(bc / 2.0 - 2.598) < 1e-3
    assert S.photon_sphere(2.0) == 3.0
    assert S.orbit(bc + 0.01)[2] == "escape" and S.orbit(bc - 0.01)[2] == "capture"
    phi, u, _ = S.orbit(bc + 1e-6, phi_max=4 * np.pi)                     # hugs r = 1.5 r_s for a while
    assert np.sum(abs(u - 1 / 3) < 1e-3) * 0.004 > 2.0


def test_deflection_matches_weak_field_series():
    for b in (40.0, 200.0):
        x = 1 / b
        series = 4 * x + 15 * np.pi / 4 * x**2 + 128 / 3 * x**3 + 3465 * np.pi / 64 * x**4
        assert abs(S.deflection(b) - series) < 2e-5
    assert abs(S.deflection(1e4, rs=2.0) / S.weak_deflection(1e4) - 1) < 1e-3


def test_ray_matches_reference_integrator():
    sol = S.trace_exact(6.0)
    phi, u, _ = S.orbit(6.0)
    m = phi <= sol.t[-1]
    assert np.max(abs(sol.sol(phi[m])[0] - u[m])) < 1e-8
    pts, fate = S.ray(-6.0, r_max=12)
    assert fate == "escape" and pts[0, 0] < 0 and pts[0, 1] < 0
    assert abs(np.hypot(*pts[0]) - 12) < 1e-6 and abs(np.hypot(*pts[-1]) - 12) < 1e-6


def test_flamm_geodesic_bends_half_as_much_as_light():
    b, rs = 400.0, 2.0
    g = S.geodesic_on_flamm(b, rs, r_max=40000.0, h=0.002)
    d_in, d_out = g[1, :2] - g[0, :2], g[-1, :2] - g[-2, :2]
    bend = abs(np.arctan2(d_out[1], d_out[0]) - np.arctan2(d_in[1], d_in[0]))
    assert abs(bend / (rs / b) - 1) < 0.05
    assert S.flamm(2.0) == 0.0 and abs(S.flamm(10.0) - 8.0) < 1e-12


def test_tables_validate():
    b, U, phi_end, status, PHC = S.load_tables()
    info = S.validate(b, U, phi_end, status, PHC)
    assert info["max_table_error"] < 1e-6
    T = S.blackbody_table()
    assert T.shape == (S.N_T, 3) and T[0, 0] > T[0, 2] and T[-1, 2] > T[-1, 0]   # cool = red, hot = blue
