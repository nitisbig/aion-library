"""Blackbody colour table: Planck spectrum → CIE 1931 XYZ → linear sRGB, normalised to Y = 1.

CIE colour-matching functions use the multi-lobe Gaussian fit of Wyman, Sloan & Shirley
(JCGT 2013), which is accurate to a few percent and avoids shipping tabulated data.
"""

from __future__ import annotations

import numpy as np

T_MIN, T_MAX, N_T = 800.0, 40000.0, 256

_H, _C, _K = 6.62607015e-34, 2.99792458e8, 1.380649e-23
_XYZ2RGB = np.array([[3.2406, -1.5372, -0.4986],
                     [-0.9689, 1.8758, 0.0415],
                     [0.0557, -0.2040, 1.0570]])


def _g(lam, mu, s1, s2):
    s = np.where(lam < mu, s1, s2)
    return np.exp(-0.5 * ((lam - mu) / s) ** 2)


def cmf(lam):
    x = 1.056 * _g(lam, 599.8, 37.9, 31.0) + 0.362 * _g(lam, 442.0, 16.0, 26.7) - 0.065 * _g(lam, 501.1, 20.4, 26.2)
    y = 0.821 * _g(lam, 568.8, 46.9, 40.5) + 0.286 * _g(lam, 530.9, 16.3, 31.1)
    z = 1.217 * _g(lam, 437.0, 11.8, 36.0) + 0.681 * _g(lam, 459.0, 26.0, 13.8)
    return np.stack([x, y, z], -1)


def rgb(T):
    """Linear-sRGB chromaticity of a blackbody at temperature T (K), with luminance Y = 1."""
    lam = np.linspace(360.0, 830.0, 471)
    lm = lam * 1e-9
    planck = 1.0 / (lm**5 * (np.exp(_H * _C / (lm * _K * np.atleast_1d(T)[:, None])) - 1.0))
    xyz = planck @ cmf(lam)
    xyz /= xyz[:, 1:2]
    return np.maximum(xyz @ _XYZ2RGB.T, 0.0)


def table():
    """(N_T, 3) float32, indexed linearly in log T between T_MIN and T_MAX."""
    T = np.exp(np.linspace(np.log(T_MIN), np.log(T_MAX), N_T))
    return rgb(T).astype(np.float32)


if __name__ == "__main__":
    for T in (1500, 3000, 5800, 6500, 10000, 20000):
        print(T, np.round(rgb(T)[0], 3))
