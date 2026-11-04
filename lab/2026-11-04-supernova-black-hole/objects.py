"""Background objects on the sky (at infinity), placed from the camera path so each lands in frame.

The sky is lensed exactly in the last shot (sky.frag), so whatever sits behind the hole at the end
becomes arcs and an Einstein ring. Distances (light years) only matter for the gravitational-wave
sweep: an object at distance d is seen to ripple at T ≈ 2d/c.
"""

from __future__ import annotations

import numpy as np

import astro as A
import timeline as TL


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def _rotate(v, axis, ang):
    axis = _unit(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


H_ALPHA, O_III, S_II = (1.0, 0.16, 0.22), (0.12, 0.72, 0.85), (0.85, 0.22, 0.75)


def nebulae():
    behind_end = -TL.camera(TL.DURATION)[0]
    up_end = TL.camera(TL.DURATION)[2]
    n1 = _rotate(behind_end, up_end, np.radians(8.0))            # just off the hole's axis at the end
    n2 = TL.screen_dir(1.0, -0.60, -0.32)                        # opening shot, lower left
    n3 = TL.screen_dir(18.0, 0.62, 0.50)                         # remnant shot, upper right
    return [
        (n1, np.radians(5.0), H_ALPHA, O_III, 0.070, 0.31),
        (n2, np.radians(12.0), O_III, S_II, 0.075, 0.67),
        (n3, np.radians(8.0), S_II, H_ALPHA, 0.070, 0.13),
    ]


def galactic_frame():
    """Band through the backgrounds of both the first and the last shot, bulge off to the side."""
    a, b = -TL.camera(0.0)[0], -TL.camera(TL.DURATION)[0]
    pole = _unit(np.cross(a, b))
    pole = _rotate(pole, a + b, np.radians(28.0))                # tilt the band across the frame
    gc = TL.screen_dir(18.0, -0.85, 0.15)
    gc = _unit(gc - np.dot(gc, pole) * pole)
    return pole, gc


def globular():
    return TL.screen_dir(0.0, 0.52, 0.66), np.radians(0.35)


# ── pulsar: a background neutron star, rendered as a small volumetric object at a fixed direction ──
PULSAR_DIR = TL.screen_dir(1.0, -0.64, 0.52)
PULSAR_PERIOD = 1.25            # screen seconds per turn (stylised: real pulsars spin in ms – s)


def pulsar_axes():
    v = -PULSAR_DIR                                               # from the pulsar toward the camera
    perp = _unit(np.cross(v, [0.0, 1.0, 0.0]))
    spin = _rotate(v, perp, np.radians(35.0))
    m0 = _rotate(spin, np.cross(spin, perp), np.radians(35.0))
    return spin, m0


def pulsar_beam(s, spin, m0):
    return _rotate(m0, spin, 2 * np.pi * s / PULSAR_PERIOD)


def gw_packet(T_yr, tau_yr, amp):
    """The same h₊ packet the sky shader uses (stylised width in log time)."""
    if T_yr <= 0:
        return 0.0
    x = np.log(T_yr / tau_yr) / 0.10
    if abs(x) > 4:
        return 0.0
    return float(amp * np.exp(-0.5 * x * x) * np.sin(2.6 * x))


def pulsar_dir(s, amp):
    """Direction of the pulsar, displaced by the wave when it passes (T ≈ 2d/c)."""
    T_yr = TL.T_of(s) / A.YR
    h = gw_packet(T_yr, 2 * A.PULSAR_DIST_LY, amp)
    if h == 0.0:
        return PULSAR_DIR
    n, right, up, fwd, _ = TL.camera(s)
    q = np.array([PULSAR_DIR @ right, PULSAR_DIR @ up]) / (PULSAR_DIR @ fwd)
    ps = 0.6
    R = np.array([[np.cos(ps), -np.sin(ps)], [np.sin(ps), np.cos(ps)]])
    qr = R.T @ q
    qr = qr + 0.5 * h * np.array([qr[0], -qr[1]])
    q = R @ qr
    return _unit(fwd + q[0] * right + q[1] * up)
