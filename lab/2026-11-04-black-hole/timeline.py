"""Every animated quantity as a pure function of t (seconds), so any frame renders on its own.

Three acts:
    0–15 s   travel: fly in from r = 3000M through dust and passing stars; lensing grows
    15–45 s  the black hole (the original 30 s piece, shifted by INTRO)
    44–58 s  spacetime: the exact Flamm's paraboloid draws on, sinks into a well, matter falls in

Camera: spherical coordinates around the hole (y = disk axis, inclination 90° = edge-on), a look-at
target on the y axis, and yaw/pitch offsets from the look-at direction, for the travelling shots.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

INTRO = 15.0
MAIN_END = INTRO + 30.0
DURATION = 58.0
TIME_SCALE = 15.0            # M of coordinate time per second → ISCO period ≈ 6 s
R_IN, R_OUT = 6.0, 19.0      # disk: ISCO to outer edge
T_ALIGN = INTRO + 2.9        # the hero star passes exactly behind the hole

# Flamm's paraboloid: z(r) = √(8M(r − 2M)), drawn for 2 ≤ r ≤ GRID_R
GRID_R = 40.0
H_RIM = float(np.sqrt(8.0 * (GRID_R - 2.0)))

# t, r (M), inclination°, azimuth°, roll°, vfov°, yaw°, pitch°, target y
CAM_KEYS = np.array([
    # act 1: travel
    [0.0,  3000.0, 66.0, -100.0, -12.0, 40.0, 10.0,  3.5, 0.0],
    [5.0,  1150.0, 73.0,  -72.0,  -6.0, 38.5,  6.0,  2.0, 0.0],
    [10.0,  330.0, 80.0,  -50.0,  -2.5, 37.0,  2.5,  0.8, 0.0],
    [15.0,   80.0, 86.0,  -34.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    # act 2: the black hole (original keys + INTRO)
    [19.5,   60.0, 85.5,   -4.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    [24.0,   35.0, 84.0,    8.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    [30.0,   32.0, 83.0,   22.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    [33.6,   50.0, 30.0,   58.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    [37.0,   31.0, 77.0,   90.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    [41.4,   28.0, 81.0,  104.0,   5.0, 36.0,  0.0,  0.0, 0.0],
    [43.0,   30.0, 82.0,  110.0,   2.0, 36.0,  0.0,  0.0, 0.0],
    # act 3: spacetime grid (rise to an oblique 3D view, orbit, push toward the throat)
    [45.0,   40.0, 76.0,  118.0,   0.0, 36.0,  0.0,  0.0, 0.0],
    [47.5,   62.0, 60.0,  134.0,   0.0, 38.0,  0.0,  0.0, -3.0],
    [51.0,   74.0, 56.0,  160.0,  -3.0, 38.0,  0.0,  0.0, -8.0],
    [54.5,   58.0, 69.0,  200.0,  -5.0, 38.0,  0.0,  0.0, -8.0],
    [58.0,   40.0, 63.0,  226.0,  -2.0, 38.0,  0.0,  0.0, -7.0],
])
_K = CAM_KEYS.copy()
_K[:, 1] = np.log(_K[:, 1])                    # interpolate distance in log space (constant feel of speed)
_CAM = PchipInterpolator(_K[:, 0], _K[:, 1:], axis=0)


def smoother(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


def ramp(t, a, b, ease=smoother):
    return float(ease((t - a) / (b - a)))


def ease_out_cubic(x):
    x = np.clip(x, 0.0, 1.0)
    return 1 - (1 - x) ** 3


def _rot(v, axis, ang):
    axis = axis / np.linalg.norm(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


def camera(t):
    """Position, orthonormal basis (right, up, forward) and vertical fov (rad)."""
    lr, inc, az, roll, fov, yaw, pitch, ty = _CAM(np.clip(t, 0.0, DURATION))
    r = np.exp(lr)
    inc, az, roll, yaw, pitch = np.radians([inc, az, roll, yaw, pitch])
    pos = r * np.array([np.sin(inc) * np.cos(az), np.cos(inc), np.sin(inc) * np.sin(az)])
    fwd = np.array([0.0, ty, 0.0]) - pos
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    fwd = _rot(fwd, up, -yaw)                       # look off to the side (hole drifts right of centre)
    right = _rot(right, up, -yaw)
    fwd = _rot(fwd, right, pitch)
    up = np.cross(right, fwd)
    c, s = np.cos(roll), np.sin(roll)
    right, up = c * right + s * up, -s * right + c * up
    return pos, right, up, fwd, np.radians(fov)


def hero_star_dir():
    """Direction of a star exactly behind the hole as seen from the camera at T_ALIGN."""
    pos = camera(T_ALIGN)[0]
    return -pos / np.linalg.norm(pos)


def params(t):
    """All scalar uniforms at time t."""
    p = {}
    m = t - INTRO                                   # act-2 local time (the original 30 s timeline)
    # ── act 1: travel ──
    p["dust"] = ramp(t, 0.0, 1.2) * (1.0 - ramp(t, 11.5, 14.0))
    # ── stars: present through the travel, drain at the end of act 2 ──
    p["stars"] = ramp(t, 0.0, 1.5) * (1.0 - ramp(m, 27.9, 29.3))
    p["hero"] = ramp(m, 0.6, 1.8) * (1.0 - ramp(m, 8.0, 10.0))
    # ── photon ring (artistic emission placed exactly at b = √27) ──
    flash = np.exp(-max(m - 7.5, 0.0) * 2.2) * (m >= 7.3) * ramp(m, 7.3, 7.5)
    ring = 0.55 * ramp(m, 7.35, 8.6) + 1.3 * flash
    ring *= 1.0 - 0.45 * ramp(m, 10.0, 12.0)
    ring += 0.5 * ramp(m, 22.2, 23.2) * (1.0 - ramp(m, 25.8, 26.8))
    ring += 0.9 * ramp(m, 28.4, 29.1)
    ring *= 1.0 - ramp(m, 29.7, 30.7)               # hands over to the grid's photon sphere
    p["ring"] = ring
    p["ring_w"] = 0.06 + 0.07 * np.exp(-max(m - 7.5, 0.0) * 3.0) * (m >= 7.3)
    p["sweep"] = ramp(m, 7.45, 8.9, ease_out_cubic) if 7.3 < m < 9.6 else -1.0
    p["sweep_amp"] = 1.0 - ramp(m, 8.7, 9.6)
    # ── accretion disk ──
    p["gas"] = ramp(m, 8.4, 10.6)
    p["front"] = 6.0 + (R_OUT + 8.0 - 6.0) * (1.0 - ramp(m, 9.2, 13.6, ease_out_cubic))
    p["ignite"] = ramp(m, 9.2, 9.9)
    p["disk"] = 1.0 - 0.84 * ramp(m, 22.2, 23.3) * (1.0 - ramp(m, 25.9, 26.8))
    p["drain"] = R_OUT + 1.0 - (R_OUT + 1.0 - 5.0) * ramp(m, 27.2, 28.9)
    p["tau"] = m * TIME_SCALE
    # ── geodesic overlay ──
    p["ov_reveal"] = ramp(m, 22.5, 25.2, lambda x: np.clip(x, 0, 1))
    p["ov_alpha"] = ramp(m, 22.4, 22.9) * (1.0 - ramp(m, 25.6, 26.7))
    # ── act 3: spacetime grid ──
    p["grid"] = ramp(t, 44.4, 44.8) * (1.0 - ramp(t, 57.0, 58.0))
    p["sink"] = ramp(t, 48.8, 52.2)                 # flat sheet → Flamm's paraboloid
    p["pulse"] = ramp(t, 51.5, 53.0)
    p["bh_on"] = t < MAIN_END + 0.6                 # ray-traced pass not needed once only the grid is left
    p["exposure_k"] = 1.0 + 0.25 * ramp(m, 26.0, 26.8) * (1.0 - ramp(m, 27.2, 28.0))
    p["fade"] = ramp(t, 0.0, 0.4) * (1.0 - ramp(t, 57.6, 58.0))
    return p


OVERLAY_T = INTRO + 24.0     # the beam diagram faces the camera at this moment


def overlay_basis():
    pos, right, up, fwd, _ = camera(OVERLAY_T)
    return right, up
