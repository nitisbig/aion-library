"""The flight path: one continuous shot from deep space down to the edge of the black hole's shadow.

Pure numpy/scipy. Distances are in M (the hole's shadow has radius √27 ≈ 5.2 M, the disk spans 6–19 M).
The move ends 21 M from the centre, skimming the disk, then zooms into the shadow until the frame is
black: that black is what the quote card sits on, and what video 004 fades up from.
"""
import numpy as np
from scipy.interpolate import PchipInterpolator

FLIGHT = 14.6                  # the frame is black from here on (s)
SKY_CENTER = (84.0, 2.0)       # same sky as video 004: the galactic centre sits behind the hole in 004's framing
DISK_RATE, DISK_T0 = 4.0, 20.0

_K = [0.0, 4.0, 7.5, 10.5, 12.8, FLIGHT]
# far → near in log distance, fastest in the dive. Never start beyond ~1990 M: the tracer's tables stop at
# impact parameter 2000 M. Never end inside 20 M: they stop there too.
_ld = PchipInterpolator(_K, np.log([1500.0, 900.0, 420.0, 110.0, 27.0, 21.0]))
# a 150° orbit: the whole sky slides behind the hole, and the disk turns under the camera at the end
_az = PchipInterpolator(_K, [-146.0, -112.0, -72.0, -38.0, -10.0, 6.0])
# high above the disk plane, a dive that levels out 5° above it (2 M over the gas), then a look down into the hole
_inc = PchipInterpolator([0.0, 5.0, 8.0, 10.5, 12.6, FLIGHT], [52.5, 55.0, 62.0, 77.0, 85.0, 79.0])
# wide in the dive (speed), then a long lens into the shadow (falling)
_fov = PchipInterpolator([0.0, 9.0, 12.6, FLIGHT], [36.0, 36.0, 52.0, 20.0])


def _s(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * u * (u * (6 * u - 15) + 10)                 # smootherstep


def pose(t):
    """Camera at time t: dist, inclination, azimuth, yaw, pitch, roll, fov."""
    t = float(np.clip(t, 0.0, FLIGHT))
    look = 1.0 - _s((t + 2.2) / 7.2)                           # opens looking away from the hole, already panning
    near = _s((t - 9.0) / 3.5)                                 # buffeting grows as the camera nears the disk
    shake = 0.16 * near * np.array([np.sin(7.1 * t) + 0.6 * np.sin(12.7 * t + 1.0),
                                    np.sin(8.3 * t + 2.0) + 0.6 * np.sin(14.9 * t)])
    return dict(dist=float(np.exp(_ld(t))), inclination=float(_inc(t)), azimuth=float(_az(t)),
                yaw=float(-50.0 * look + shake[0]), pitch=float(5.0 * look + shake[1]),
                roll=float(-15.0 * look + 11.0 * np.sin(np.pi * np.clip((t - 8.0) / 6.0, 0, 1)) ** 2),
                fov=float(_fov(t)))


def _rot(v, axis, ang):
    axis = axis / np.linalg.norm(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


def basis(t):
    """Camera position and (right, up, forward) at time t. Same construction as aion's camera_basis."""
    c = pose(t)
    inc, az, roll, yaw, pitch = np.radians([c["inclination"], c["azimuth"], c["roll"], c["yaw"], c["pitch"]])
    pos = c["dist"] * np.array([np.sin(inc) * np.cos(az), np.cos(inc), np.sin(inc) * np.sin(az)])
    fwd = -pos / np.linalg.norm(pos)
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    fwd, right = _rot(fwd, up, -yaw), _rot(right, up, -yaw)
    fwd = _rot(fwd, right, pitch)
    up = np.cross(right, fwd)
    cr, sr = np.cos(roll), np.sin(roll)
    return pos, cr * right + sr * up, -sr * right + cr * up, fwd


def sky_dir(t, x=0.0, y=0.0):
    """Direction on the sky that sits at screen offset (x right, y up; tangent units, 0.32 = top edge at
    fov 36°) at time t, with its screen-aligned tangents: where to put an object so it is framed then."""
    _, right, up, fwd = basis(t)
    d = fwd + x * right + y * up
    d /= np.linalg.norm(d)
    t1 = right - np.dot(right, d) * d
    t1 /= np.linalg.norm(t1)
    return d, t1, np.cross(d, t1)


def hole_dir(t):
    """Direction on the sky exactly behind the hole at time t (an object here is lensed into an Einstein ring)."""
    pos = basis(t)[0]
    return -pos / np.linalg.norm(pos)
