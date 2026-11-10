"""Ch3 shared pieces: Fourier's hot ring (S11–S13).

The ring and the bar are one object: a tube along a curve that "unrolls" with arc length
preserved (v = 0 ring, v = 1 straight bar), anchored at the front point. Temperature lives
on the arc parameter ψ ∈ [−π, π] (ψ < 0 is the left half), so it stays attached to the
metal while the ring bends and unrolls.

Temperature model (exact): the square start u(ψ) = Σ_{odd n} (4/πn) sin(n·(−ψ)), hot on
the left, cold on the right; each mode decays as e^{−n² τ} in heat-time τ.
Colors: HEAT_RAMP (ice indigo → violet → ember → white-hot), Ch3 only.
"""

from __future__ import annotations

import numpy as np
from manim import ManimColor

from aion import style as S
from aion.components.mesh_gl import MeshPlate, rgb, ribbon_mesh, tube_mesh

R = 1.45                     # ring radius (world units); unrolled length 2πR ≈ 9.1
TUBE = 0.16                  # tube radius
CROWN_BASE = 0.78            # crown baseline height above the ring plane
CROWN_H = 0.55               # crown height per unit temperature
NT = 100                     # odd modes in the square start
M = 360                      # samples around the ring
PSI = np.linspace(-np.pi, np.pi, M)
CAM = dict(yaw=-90.0, pitch=26.0, dist=9.6, target=(0.0, 0.0, 0.25), fov=38.0)
_RAMP = np.array([rgb(c) for c in S.HEAT_RAMP])
METAL = rgb("#2C313A")


def ramp(T) -> np.ndarray:
    """Temperature T ∈ [−1, 1] → HEAT_RAMP color (−1 ice indigo, +1 white-hot)."""
    p = np.clip((np.asarray(T, float) + 1) / 2, 0, 1) * 2.35          # +1 is ember going white, not pure white
    i = np.minimum(p.astype(int), 2)
    f = (p - i)[..., None]
    return _RAMP[i] * (1 - f) + _RAMP[i + 1] * f


def modes(psi, tau=0.0, n_terms: int = NT, only: int | None = None, smooth: bool = True) -> np.ndarray:
    """Temperature after heat-time tau (tau = 0: the square start). only=n keeps one mode.

    smooth: Lanczos σ-factors on the partial sum, so the drawn start is a clean square
    (the Gibbs ripple belongs to Ch2's story, not to a temperature profile)."""
    psi = np.asarray(psi, float)
    out = np.zeros_like(psi)
    ns = [only] if only else range(1, 2 * n_terms, 2)
    for n in ns:
        sig = np.sinc(n / (2 * n_terms)) if (smooth and not only) else 1.0
        out += 4 / (np.pi * n) * sig * np.exp(-n * n * tau) * np.sin(-n * psi)
    return out


SQUARE = modes(PSI)


def centerline(psi, v: float = 0.0, center=(0.0, 0.0, 0.0), scale: float = 1.0) -> np.ndarray:
    """Points of the ring (v = 0) … bar (v = 1) at arc parameter psi, world coords."""
    s = R * np.asarray(psi, float)
    if v >= 0.999:
        x, y = s, np.full_like(s, -R)
    else:
        rho = R / (1 - v)
        x, y = rho * np.sin(s / rho), -R + rho * (1 - np.cos(s / rho))
    c = np.asarray(center, float)
    return c + scale * np.column_stack([x, y, np.zeros_like(x)])


def ring_parts(T, *, v=0.0, center=(0.0, 0.0, 0.0), scale=1.0, heat_vis=1.0, crown=0.0, crown_u=None,
               ghost_u=None, ghost_op=0.0, op=1.0, gain=1.0):
    """(meshes, glass) for one ring: metal tube glowing by temperature T (M,), and its crown."""
    p = centerline(PSI, v, center, scale)
    T = np.asarray(T, float)
    glow = ramp(T) * (0.1 + 0.6 * np.minimum(np.abs(T), 1) ** 0.8)[:, None] * heat_vis
    closed = v < 0.02
    meshes = [tube_mesh(p, TUBE * scale, METAL * op, emit=glow * op, closed=closed, sides=20)]
    glass = []
    if crown > 0:
        u = T if crown_u is None else crown_u
        base = p + np.array([0, 0, CROWN_BASE * scale])
        top = base + np.column_stack([0 * u, 0 * u, CROWN_H * gain * scale * u * crown])
        glass.append(ribbon_mesh(base, top, ramp(u), alpha_bottom=0.0, alpha_top=0.45 * crown * op))
        glass.append(tube_mesh(top, 0.022 * scale, np.zeros(3), emit=rgb(S.INK) * 1.1 * crown * op,
                               closed=closed, sides=8, alpha=1.0))
    if ghost_u is not None and ghost_op > 0:
        base = p + np.array([0, 0, CROWN_BASE * scale])
        top = base + np.column_stack([0 * ghost_u, 0 * ghost_u, CROWN_H * scale * ghost_u])
        glass.append(tube_mesh(top, 0.03 * scale, np.zeros(3), emit=rgb(S.LABEL) * 0.7 * ghost_op,
                               closed=closed, sides=8, alpha=1.0))
    return meshes, glass


# ── stateless particles (flame on the hot half, frost on the cold half) ─────
def _hash(i, k):
    x = np.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - np.floor(x)


def particles(now, t_on, t_off, kind: str, v=0.0, center=(0.0, 0.0, 0.0), scale=1.0):
    """Point sprites (xyz, rgba, size_px). Born at a fixed rate in [t_on, t_off], then they age out."""
    rate, life = (900.0, 0.8) if kind == "flame" else (420.0, 1.5)
    if now < t_on:
        return np.zeros((0, 3)), np.zeros((0, 4)), np.zeros(0)
    i0 = max(0, int(np.floor((now - t_on - life) * rate)))
    i1 = int(np.floor((min(now, t_off) - t_on) * rate))
    if i1 < i0:
        return np.zeros((0, 3)), np.zeros((0, 4)), np.zeros(0)
    i = np.arange(i0, i1 + 1, dtype=float)
    age = now - (t_on + i / rate)
    keep = (age >= 0) & (age < life)
    i, age = i[keep], age[keep]
    h1, h2, h3 = _hash(i, 1), _hash(i, 2), _hash(i, 3)
    f = age / life
    if kind == "flame":
        psi = -np.pi + 0.06 + h1 * (np.pi - 0.12)          # left half
        base = centerline(psi, v, center, scale)
        out = (base - np.asarray(center)) / (np.linalg.norm(base - np.asarray(center), axis=1, keepdims=True) + 1e-9)
        xyz = base + scale * (np.column_stack([0 * f, 0 * f, TUBE + 0.95 * age + 0.25 * age ** 2])
                              + out * ((h2 - 0.5) * 0.3 + 0.06 * np.sin(9 * age + 6 * h3))[:, None])
        col = np.where(f[:, None] < 0.35, ramp(np.ones_like(f))[:, :] * 1.0, ramp(np.full_like(f, 0.55)))
        a = (1 - f) ** 1.3 * (0.55 + 0.45 * h3)
        size = (16 - 8 * f) * (0.7 + 0.6 * h2)
    else:
        psi = 0.06 + h1 * (np.pi - 0.12)                    # right half
        base = centerline(psi, v, center, scale)
        out = (base - np.asarray(center)) / (np.linalg.norm(base - np.asarray(center), axis=1, keepdims=True) + 1e-9)
        xyz = base + scale * (out * (TUBE + 0.32 * age * (0.4 + h2))[:, None]
                              + np.column_stack([0 * f, 0 * f, 0.18 * np.sin(2.5 * age + 6 * h3) + 0.12 * h2]))
        col = np.tile(rgb("#CFE6FF"), (len(f), 1)) * (1 - f[:, None]) + ramp(-np.ones_like(f)) * f[:, None]
        a = np.sin(np.pi * f) * (0.35 + 0.65 * (h3 > 0.7))
        size = 5 + 5 * h2
    rgba = np.column_stack([col, a])
    return xyz.astype(float), rgba.astype(float), size.astype(float)


# ── S13 → S14 hand-off: one circle with its arm, back on the drawing stage ──
SEED_CENTER = np.array([-4.0, 0.6, 0.0])   # leaves room below for S14's left-right wave
SEED_R = 1.2


def drawing_seed():
    """The picture S13 ends on and S14 starts from: circle (FWD), hub, arm (ARM) pointing up, pen (INK)."""
    from manim import Arrow, Circle, Dot, VGroup
    tip = SEED_CENTER + np.array([0.0, SEED_R, 0.0])
    circle = Circle(radius=SEED_R, color=S.FWD, stroke_width=3).move_to(SEED_CENTER)
    arm = Arrow(SEED_CENTER, tip, buff=0, color=S.ARM, stroke_width=3, tip_length=0.16,
                max_tip_length_to_length_ratio=0.25, max_stroke_width_to_length_ratio=20)
    hub = Dot(SEED_CENTER, radius=0.045, color=S.ARM)
    pen = VGroup(Dot(tip, radius=0.17, color=S.INK).set_opacity(0.22), Dot(tip, radius=0.07, color=S.INK))
    return VGroup(circle, hub, arm, pen)
