"""Camera path and every animated quantity as a function of t (seconds, 0–30)."""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

DURATION = 30.0


def ss(a, b, t):
    x = np.clip((t - a) / (b - a), 0.0, 1.0)
    return x * x * (3 - 2 * x)


def sss(a, b, t):
    x = np.clip((t - a) / (b - a), 0.0, 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)


def sph(az_deg, R, h):
    a = np.radians(az_deg)
    return np.array([R * np.sin(a), h, R * np.cos(a)])


def _keys():
    P, T, F = [], [], []          # (t, pos), (t, target), (t, fov)

    def key(t, pos, tgt, fov=None):
        P.append((t, *pos)); T.append((t, *tgt))
        if fov is not None:
            F.append((t, fov))

    # 1–2: from far above, push in and descend in a 60° orbit while the city trains
    for t in np.arange(0.0, 8.51, 0.5):
        u = t / 8.5
        e = u * u * (3 - 2 * u)
        az = 80 - 68 * e ** 1.3
        R = 1150 * (380 / 1150) ** (e ** 1.1)
        h = 860 * (200 / 860) ** (e ** 1.15)
        key(t, sph(az, R, h), (0, 30 + 10 * e, 0), 34 + 8 * e)
    # 3: dive onto the avenue, slow glide, whip, slow glide
    key(9.6, (0, 46, 302), (0, 16, 160), 48)
    key(10.5, (0, 12.5, 262), (0, 10, 150), 52)
    key(12.0, (0.6, 9.0, 238), (0, 9.5, 120), 52)
    key(12.6, (0.4, 9.0, 222), (0, 10, 110))
    key(13.2, (-0.6, 9.5, 176), (0, 12, 60))
    key(13.8, (0, 10.5, 136), (0, 20, 20), 54)
    key(15.0, (0.3, 12, 112), (0, 32, 0))
    key(16.5, (0, 14.5, 94), (0, 46, 0), 50)
    # 4: enter the plaza, then rise and orbit the hero tower inside the ring of towers (plaza r = 56 m)
    key(17.1, sph(-3, 72, 17), (0, 52, 0), 49)
    for t in np.arange(17.6, 22.01, 0.4):
        u = (t - 17.1) / 4.9
        e = u * u * (3 - 2 * u)
        key(t, sph(-6 - 112 * e, 72 - 26 * np.sqrt(np.clip(u * 1.6, 0, 1)), 17 + 136 * e ** 1.15),
            (0, 52 + 102 * e, 0), 49 - 5 * e)
    # 5: slow push into the facade corner while the scan passes
    for t in np.arange(22.4, 26.01, 0.4):
        u = (t - 22.0) / 4.0
        key(t, sph(-118 - 17 * u, 46 - 20 * (u * u * (3 - 2 * u)) ** 0.8, 153 + 5 * u),
            (-6 * u, 154 + 2 * u, -6 * u), 44 - 4 * u)
    # 6: exponential pull-back while the city dissolves
    for t in np.arange(26.4, 30.01, 0.4):
        u = (t - 26.0) / 4.0
        e = 1 - (1 - u) ** 2.2
        key(t, sph(-135 - 30 * e, 26 * (1500 / 26) ** e, 158 + 900 * e ** 1.4), (-6 * (1 - e), 156 - 110 * e, -6 * (1 - e)),
            40 - 4 * e)
    P, T, F = np.array(P), np.array(T), np.array(F)
    return (PchipInterpolator(P[:, 0], P[:, 1:]), PchipInterpolator(T[:, 0], T[:, 1:]),
            PchipInterpolator(F[:, 0], F[:, 1]))


POS, TGT, FOV = _keys()


def roll(t):
    # banking on the whip
    return 0.06 * np.sin(np.pi * np.clip((t - 12.3) / 2.0, 0, 1)) - 0.03 * ss(16.5, 20, t) + 0.03 * ss(20, 26, t)


def camera(t):
    t = float(np.clip(t, 0, DURATION))
    pos = POS(t)
    tgt = TGT(t)
    fwd = tgt - pos
    dist = np.linalg.norm(fwd)
    fwd /= dist
    right = np.cross(fwd, [0, 1.0, 0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    r = roll(t)
    right, up = right * np.cos(r) + up * np.sin(r), up * np.cos(r) - right * np.sin(r)
    # focus: the target, except a rack from a near lamp to the tower at the start of shot 4
    # focus comes from the depth buffer (autofocus in render.py) except during the rack:
    # a near street lamp first, then release to the tower
    rack = float(ss(16.4, 16.8, t) * (1 - ss(17.3, 18.3, t)))
    return dict(pos=pos, fwd=fwd, right=right, up=up, fov=np.radians(float(FOV(t))), focus=float(dist), dist=dist,
                rack=rack, rack_focus=24.0)


# simulation time: slows to ~15 % while the scan passes (shot 5)
_tg = np.linspace(0, DURATION, 6001)
_rate = 1.0 - 0.85 * ss(21.6, 22.6, _tg) * (1 - ss(25.4, 26.4, _tg))
_tau = np.concatenate([[0], np.cumsum((_rate[1:] + _rate[:-1]) / 2 * np.diff(_tg))])


def tau(t):
    return float(np.interp(t, _tg, _tau))


def speed(t, dt=1 / 60):
    """Forward camera speed relative to the distance of nearby geometry (1/s): drives the zoom streaks."""
    a, b = POS(max(t - dt, 0)), POS(min(t + dt, DURATION))
    v = (b - a) / (2 * dt)
    c = camera(t)
    return float(max(v @ c["fwd"], 0) / (max(c["pos"][1], 0.0) + 20.0))   # nearby geometry ~ height above ground


def events(t):
    # 2: training reveal. A wave expands from the plaza; inside it, Gaussians appear (densify) and sharpen
    reveal_r = -60 + 640 * sss(3.3, 8.6, t)
    seed_vis = ss(0.2, 2.6, t)
    # 5: horizontal scan plane descending past the camera
    scan_y = 214 - 100 * sss(22.3, 25.7, t)
    scan_amt = ss(22.1, 22.6, t) * (1 - ss(25.5, 26.0, t))
    # 6: dissolve from the outside in
    diss_r = 760 - 700 * sss(26.2, 29.6, t)
    sp = speed(t)
    zoom = float(np.clip((sp - 0.3) * 0.022, 0, 0.035))
    return dict(reveal_r=reveal_r, seed_vis=seed_vis, scan_y=scan_y, scan_amt=scan_amt, scan_w=11.0,
                diss_r=diss_r, tau=tau(t), zoom=zoom, ca=0.0025 + 0.5 * zoom,
                dof_k=0.003 + 0.013 * (1 - ss(1.5, 4.0, t)) - 0.0018 * ss(9.0, 10.0, t) * (1 - ss(16.0, 16.4, t))
                + 0.004 * ss(16.3, 16.6, t) * (1 - ss(18.0, 18.8, t)),
                bloom=0.5 + 0.35 * np.exp(-((t - 6.2) / 1.6) ** 2),
                fade=ss(0.0, 1.0, t) * (1 - ss(29.1, 30.0, t)))


if __name__ == "__main__":
    for t in np.arange(0, 30.01, 1.0):
        c = camera(t)
        e = events(t)
        print(f"t={t:5.1f} pos={np.round(c['pos'], 1)} fov={np.degrees(c['fov']):4.1f} focus={c['focus']:6.1f} "
              f"spd={speed(t):5.2f} zoom={e['zoom']:.3f} τ={e['tau']:5.2f}")
