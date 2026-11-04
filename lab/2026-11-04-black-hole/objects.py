"""Extra celestial objects for the "O" looks: nebulae, a supernova, distant galaxies, a pulsar fly-by.

Everything except the pulsar sits on the sky sphere ("at infinity") and is drawn in the ray tracer
from the exact lensed exit direction, so the hole lenses it correctly. The pulsar is a 3D object
near the flight path in act 1 (r ≳ 300M from the hole; the lensing there is < 1°, ignored).

Placements are derived from the camera path, so each object lands where it should in frame.
"""

from __future__ import annotations

import numpy as np

import timeline as TL


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def _screen_dir(t, x, y):
    """Sky direction that appears at normalised screen position (x, y) ∈ [-1, 1] at time t."""
    pos, right, up, fwd, fov = TL.camera(t)
    th = np.tan(fov / 2)
    return _unit(fwd + x * th * 16 / 9 * right + y * th * up)


def _rotate(v, axis, ang):
    axis = _unit(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


# ── nebulae: centre direction, angular radius (rad), colour A, colour B, brightness, seed ──
# colours are linear RGB: Hα red, O III teal, S II magenta
H_ALPHA, O_III, S_II = (1.0, 0.16, 0.22), (0.12, 0.72, 0.85), (0.85, 0.22, 0.75)


def nebulae():
    behind = -TL.camera(TL.INTRO + 5.5)[0]                      # behind the hole at the shadow reveal
    n1 = _rotate(_unit(behind), [0, 1, 0], np.radians(4.0))     # slightly off-axis → asymmetric arcs
    n2 = _screen_dir(1.5, -0.55, -0.25)                          # seen during the travel, lower left
    n3 = _rotate(_unit(-TL.camera(33.6)[0]), [1, 0, 0], np.radians(16.0))   # behind the face-on view
    return [
        (n1, np.radians(10.0), H_ALPHA, O_III, 0.075, 3.1),
        (n2, np.radians(15.0), O_III, S_II, 0.09, 8.7),
        (n3, np.radians(11.0), S_II, H_ALPHA, 0.07, 5.3),
    ]


# ── supernova: direction, explosion time ──
SN_T = 5.6


def supernova_dir():
    return _screen_dir(SN_T, 0.48, 0.36)                         # upper right of frame


def supernova_light(t):
    """Light curve: fast rise, exponential decay with a long faint tail; cools from 16000 K to 5000 K."""
    age = t - SN_T
    if age < 0:
        return 0.0, 16000.0, 0.0
    rise = min(age / 0.15, 1.0) ** 2
    I = rise * (np.exp(-age / 1.3) + 0.06 * np.exp(-age / 9.0))
    T = 5000.0 + 11000.0 * np.exp(-age / 1.6)
    return float(I), float(T), float(age)


# ── pulsar (neutron star) fly-by in act 1 ──
NS_T = 8.6                     # time the camera passes it


def pulsar():
    pos, right, up, fwd, _ = TL.camera(NS_T)
    r = np.linalg.norm(pos)
    P = pos + right * 0.075 * r + up * 0.03 * r
    # spin axis at 35° from the line of sight at t ≈ 6 s, magnetic axis 35° from spin:
    # once per turn a beam sweeps across the camera (the lighthouse flash)
    v = _unit(TL.camera(6.0)[0] - P)
    perp = _unit(np.cross(v, [0.0, 1.0, 0.0]))
    spin = _rotate(v, perp, np.radians(35.0))
    m0 = _rotate(spin, np.cross(spin, perp), np.radians(35.0))
    return P, spin, m0


NS_PERIOD = 1.15               # s per turn (time-compressed, like the rest of the flight)


def pulsar_beam(t, spin, m0):
    return _rotate(m0, spin, 2 * np.pi * t / NS_PERIOD)


def params(t):
    I, T, age = supernova_light(t)
    from timeline import ramp
    return {
        "sn_I": I, "sn_T": T, "sn_age": age,
        "ns": ramp(t, 2.2, 3.6) * (1.0 - ramp(t, 9.6, 10.8)),
        "objects": ramp(t, 0.0, 1.5) * (1.0 - ramp(t - TL.INTRO, 27.9, 29.3)),
    }
