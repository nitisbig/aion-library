"""Chapter 7 shared pieces: the camera that shaders/hill.frag ray-marches through (so Manim marks land on the
surface), the two landscapes, the walker's exact descent, the three step sizes, the line fit and the swarm.

Example:
    cam = Cam(target=(0, 0, 1), yaw=1.9, pitch=0.6, dist=8)
    xy = cam.project(np.array([[x, y, ZS * loss(x, y)]]))
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from aion import C, Track
from manim import VGroup

import sims as sm
from beats import T
from kit import P3, lin_rgb, mix, polyline, tint

ZS = 1.2                                   # height scale of the hill (sims.loss)
ZS_R = 0.8                                 # height scale of the rugged landscape
FOCAL = 4 / math.tan(math.radians(22.5))   # 45° vertical field of view


def loss(x, y):
    return sm.loss(x, y)


def rugged(x, y):
    """The wide landscape of c07_s03 (same formula as hill.frag mode 1): many valleys of different depths."""
    return (0.025 * (x * x + y * y) + 0.45 * np.sin(0.9 * x + 0.3) * np.sin(0.8 * y - 0.5)
            + 0.25 * np.sin(1.7 * x - 1.1 * y + 1.0) + 0.15 * np.cos(2.6 * x + 1.9 * y)
            + 0.1 * np.sin(3.7 * y - 0.6 * x + 2.0))


def rugged_grad(x, y, h=1e-4):
    return ((rugged(x + h, y) - rugged(x - h, y)) / (2 * h), (rugged(x, y + h) - rugged(x, y - h)) / (2 * h))


# ------------------------------------------------------------------------------------------------ camera
@dataclass
class Cam:
    """Pinhole camera orbiting `target`: yaw = direction (in the ground plane) from target to eye, pitch = angle
    above the ground, dist = eye distance. `off` shifts the picture on screen (the optical centre)."""
    target: tuple = (0.0, 0.0, 0.0)
    yaw: float = 0.0
    pitch: float = 0.5
    dist: float = 8.0
    f: float = FOCAL
    off: tuple = (0.0, 0.0)

    def basis(self):
        tg = np.asarray(self.target, float)
        cp = math.cos(self.pitch)
        eye = tg + self.dist * np.array([cp * math.cos(self.yaw), cp * math.sin(self.yaw), math.sin(self.pitch)])
        fwd = tg - eye
        fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0.0, 0.0, 1.0])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        return eye, fwd, right, up

    def project(self, P):
        """World points (N, 3) → screen (N, 2) in world units; points behind the camera get nan."""
        eye, fwd, right, up = self.basis()
        d = np.atleast_2d(np.asarray(P, float)) - eye
        z = d @ fwd
        z = np.where(z > 1e-3, z, np.nan)
        return np.c_[self.f * (d @ right) / z + self.off[0], self.f * (d @ up) / z + self.off[1]]


def lerp_cam(a: Cam, b: Cam, u: float) -> Cam:
    u = float(u)
    yaw = a.yaw + (b.yaw - a.yaw) * u
    return Cam(tuple(np.asarray(a.target) + (np.asarray(b.target) - np.asarray(a.target)) * u), yaw,
               a.pitch + (b.pitch - a.pitch) * u, a.dist * (b.dist / a.dist) ** u, a.f + (b.f - a.f) * u,
               tuple(np.asarray(a.off) + (np.asarray(b.off) - np.asarray(a.off)) * u))


def hill_uniforms(cam_fn, mode=0, opacity=1.0, fog=0.0, walker=(0.0, 0.0), fr=1.2):
    """Keyword arguments for s.shader('hill.frag', …): the camera, colours and fog as Tracks of t."""
    def tr(f):
        return f if callable(f) else (lambda t, v=f: v)
    basis = lambda i: Track(lambda t: tuple(float(v) for v in cam_fn(t).basis()[i]))
    fw = tr(walker)
    return dict(u_eye=basis(0), u_fwd=basis(1), u_right=basis(2), u_up=basis(3),
                u_f=Track(lambda t: float(cam_fn(t).f)), u_off=Track(lambda t: tuple(map(float, cam_fn(t).off))),
                u_mode=float(mode), u_zs=ZS if mode == 0 else ZS_R, u_dom=3.5 if mode == 0 else 6.0,
                u_fog=Track(lambda t: float(tr(fog)(t))), u_walker=Track(lambda t: tuple(map(float, fw(t)))),
                u_fr=float(fr), u_lo=tuple(map(float, lin_rgb(tint(C.descent, 0.06 if mode == 0 else 0.03)))),
                u_hi=tuple(map(float, lin_rgb(mix(C.descent, C.light, 0.45) if mode == 0 else tint(C.descent, 0.62)))),
                u_contour=0.12 if mode == 0 else 0.1, u_opacity=Track(lambda t: float(tr(opacity)(t))))


def on_hill(xy, lift=0.02):
    xy = np.atleast_2d(xy)
    return np.c_[xy, ZS * loss(xy[:, 0], xy[:, 1]) + lift]


def on_rugged(xy, lift=0.02):
    xy = np.atleast_2d(xy)
    return np.c_[xy, ZS_R * rugged(xy[:, 0], xy[:, 1]) + lift]


# ------------------------------------------------------------------------------------------------ the walker
PATH = sm.descent_path()                   # θ ← θ − η ∇L(θ), η = 0.25, from (−0.9, 2.6): 30 exact iterates
FOG_STEPS = 8                              # steps taken in the fog (one per STEP_DT), the rest after it lifts
STEP_DT, FAST_DT, HOP = 0.5, 0.11, 0.3


def step_times():
    """When each step k = 1..30 starts: slow in the fog from 'step', quick once the fog lifts."""
    t1 = float(T.c07_s01_step) + 0.15
    ts = [t1 + STEP_DT * k for k in range(FOG_STEPS)]
    t2 = float(T.c07_s01_gradient_descent) + 0.9
    ts += [t2 + FAST_DT * k for k in range(len(PATH) - 1 - FOG_STEPS)]
    return np.array(ts)


def walker_xy(t):
    ts = step_times()
    k = int(np.searchsorted(ts, t, side="right"))            # steps started
    if k == 0:
        return PATH[0].copy(), 0
    dt = STEP_DT if k <= FOG_STEPS else FAST_DT
    u = min((t - ts[k - 1]) / min(HOP, 0.9 * dt), 1.0)
    u = u * u * (3 - 2 * u)
    return PATH[k - 1] + (PATH[k] - PATH[k - 1]) * u, k


def trail(t, n_sub=6):
    """The walker's path on the ground so far, sampled along each straight step."""
    p, k = walker_xy(t)
    pts = [PATH[0]]
    for j in range(1, k):
        a, b = PATH[j - 1], PATH[j]
        pts += [a + (b - a) * s for s in np.linspace(0, 1, n_sub)[1:]]
    if k >= 1:
        a = PATH[k - 1]
        pts += [a + (p - a) * s for s in np.linspace(0, 1, n_sub)[1:]]
    return np.array(pts)


YAW0 = math.atan2(-(PATH[1] - PATH[0])[1], -(PATH[1] - PATH[0])[0])   # the camera behind the walker


def fog_cam(t):
    """c07_s01's camera: low behind the walker in the fog, then craned up to the whole hill (left of the column)."""
    from kit import smooth01
    w, _ = walker_xy(t)
    h = ZS * float(loss(*w))
    near = Cam(target=(w[0], w[1], h + 0.15), yaw=YAW0, pitch=math.radians(50), dist=3.0, off=(0.0, -0.6))
    far = Cam(target=(0.15, 0.35, 0.85), yaw=YAW0 + 0.25, pitch=math.radians(44), dist=10.2, off=(-2.35, -0.35))
    u = float(smooth01((t - float(T.c07_s01_gradient_descent) + 0.2) / 2.6))
    return lerp_cam(near, far, u)


# ------------------------------------------------------------------------------------------------ step sizes
ETAS = (0.05, 0.4, 1.1)                    # on f(x) = x²: x ← (1 − 2η) x: crawl, settle, overshoot and diverge
X_START = -2.0


def iterates(eta, n=40):
    x = [X_START]
    for _ in range(n):
        x.append(x[-1] - eta * 2 * x[-1])
    return np.array(x)


# ------------------------------------------------------------------------------------------------ the line fit
@lru_cache(maxsize=1)
def fit_data(n=14, seed=1847):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-2.2, 2.2, n))
    y = 0.75 * x + 0.4 + rng.normal(0, 0.35, n)
    return x, y


def fit_loss(m, b):
    """L(m, b) = (1/n) Σ (y_i − m x_i − b)², for arrays m, b of any (matching) shape."""
    x, y = fit_data()
    m, b = np.asarray(m, float), np.asarray(b, float)
    r = y.reshape((1,) * m.ndim + (-1,)) - m[..., None] * x - b[..., None]
    return (r * r).mean(-1)


@lru_cache(maxsize=1)
def fit_path(m0=0.0, b0=-1.5, eta=0.12, steps=26):
    x, y = fit_data()
    p = [np.array([m0, b0])]
    for _ in range(steps):
        m, b = p[-1]
        r = y - m * x - b
        g = np.array([-2 * (x * r).mean(), -2 * r.mean()])
        p.append(p[-1] - eta * g)
    return np.array(p)


def least_squares():
    x, y = fit_data()
    return np.polyfit(x, y, 1)                                  # (m*, b*)


# ------------------------------------------------------------------------------------------------ the swarm
SW_N = 1600


@lru_cache(maxsize=1)
def swarm(steps=140, eta=0.09, seed=2026):
    """Seeded descenders on the rugged landscape: positions (steps+1, N, 2), each one walking downhill with a
    little noise that dies away, so they pour into whichever valley is below them."""
    rng = np.random.default_rng(seed)
    p = rng.uniform(-5.6, 5.6, (SW_N, 2))
    out = [p.copy()]
    for k in range(steps):
        gx, gy = rugged_grad(p[:, 0], p[:, 1])
        noise = rng.normal(0, 0.05 * math.exp(-k / 30), p.shape)
        p = np.clip(p - eta * np.c_[gx, gy] + noise, -5.9, 5.9)
        out.append(p.copy())
    return np.array(out)


def swarm_at(u):
    """Swarm positions after u steps (fractional, interpolated)."""
    S = swarm()
    u = float(np.clip(u, 0, len(S) - 1.001))
    k = int(u)
    f = u - k
    return S[k] * (1 - f) + S[k + 1] * f


# ------------------------------------------------------------------------------------------------ the fit, on screen
SC0, SCK, SCY = np.array([-3.2, -0.44]), 1.1, 0.4   # scatter: screen of (0, 0), units per data unit
MAP = (1.4, 5.4, -2.9, 0.9)                     # contour map box (x0, x1, y0, y1)
MR, BR = (-1.9, 3.1), (-3.4, 2.6)               # its m and b ranges
BAR_X, BAR_Y0, BAR_H = 0.45, -2.6, 3.0


def sc(x, y):
    return SC0 + SCK * np.array([x, y - SCY])


def mp(m, b):
    x0, x1, y0, y1 = MAP
    return np.array([x0 + (x1 - x0) * (m - MR[0]) / (MR[1] - MR[0]), y0 + (y1 - y0) * (b - BR[0]) / (BR[1] - BR[0])])


def contours():
    """The error map: whole rings of L(m, b) that fit the open space right of the scatter."""
    import contourpy
    m = np.linspace(MR[0] - 1.5, MR[1] + 1.5, 260)              # wider than the map, so outer rings close
    b = np.linspace(BR[0] - 1.8, BR[1] + 1.8, 260)
    M, B = np.meshgrid(m, b)
    Z = fit_loss(M, B)
    gen = contourpy.contour_generator(M, B, Z)
    lo = float(Z.min())
    g = VGroup()
    levels = lo + 0.03 * (1.55 ** np.arange(14))
    for i, lv in enumerate(levels):
        for ln in gen.lines(lv):
            q = np.array([mp(*v) for v in ln])
            inside = q[:, 0].min() > 0.95 and q[:, 0].max() < 6.4 and q[:, 1].min() > -3.25 and q[:, 1].max() < 1.35
            if len(ln) > 3 and np.allclose(ln[0], ln[-1]) and inside:   # whole rings that fit the open space
                k = i / (len(levels) - 1)
                g.add(polyline([tuple(v) for v in q], mix(mix(C.descent, C.light, 0.35), C.descent, k),
                               1.5, 0.9 - 0.5 * k))
    return g
