"""'What Is Time?': a point-cloud journey, synced to the narration. moderngl headless on the Radeon R4.

    uv run python lab/2026-11-15-what-is-time/render.py still --at q heart now place sink frames arrow why --height 540
    uv run python lab/2026-11-15-what-is-time/render.py video --height 540 --fps 30        # preview (no audio mux)
    uv run python lab/2026-11-15-what-is-time/render.py video --height 1080 --fps 30       # final, muxed with audio

Every frame is a pure function of absolute audio time t. All times come from beats.py (word cues).
Chapters (each its own world + camera; neighbours crossfade by dissolving / condensing):
  DARK   particles appear one by one in darkness; a title made of dust; a heartbeat wave; a green dusk light
  ROAD   the tunnel of time: the past is fixed and solid, the future an unformed flickering cloud, now a bright edge
  FABRIC stacked space-grids woven by rising time threads; one slice = a 'when'; one node = an event
  BEND   a space-grid sheet ripples, then sinks into a gravity well; clocks tick at their true relative rates;
         an orbiting satellite; planes of simultaneity sweep at different angles
  BLOCK  a stack of landscapes, one per moment; a moving 'now' that stops: every slice equally real
  ARROW  an ordered crystal diffuses into disorder, its stars burn out, and everything streams one way
  END    the dust field drifts, then freezes; one moment-sweep; particles go out; one remains; dark
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G  # noqa: E402
try:
    from beats import T  # noqa: E402
    DURATION = float(T.duration)
    B = {k: float(v) for k, v in T.items.items()}
except ImportError:            # standalone (Kaggle): beats frozen by `render.py freeze`
    import json
    _bj = json.loads((HERE / "beats.json").read_text())
    DURATION, B = float(_bj["duration"]), {k: float(v) for k, v in _bj["beats"].items()}

OUT = HERE / "out"
SH = HERE / "shaders"


# ── helpers ─────────────────────────────────────────────────────────────────
def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return float(t * t * (3 - 2 * t))


def env(t, a, b, fin=1.0, fout=1.0):
    return ss(a, a + fin, t) * (1 - ss(b - fout, b, t))


def mix(a, b, k):
    return np.asarray(a, float) * (1 - k) + np.asarray(b, float) * k


def look(pos, tgt, roll=0.0, fov=55.0):
    pos = np.asarray(pos, float)
    f = np.asarray(tgt, float) - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    r, u = np.cos(roll) * r + np.sin(roll) * u, -np.sin(roll) * r + np.cos(roll) * u
    return dict(pos=pos, fwd=f, right=r, up=u, fov=fov)


def yawed(f, a):
    c, s = np.cos(a), np.sin(a)
    return np.array([c * f[0] - s * f[2], f[1], s * f[0] + c * f[2]])


def integrate(fn, t0, t1, n=6000):
    tg = np.linspace(t0, t1, n)
    v = np.array([fn(x) for x in tg])
    cum = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(tg))])
    return lambda t: float(np.interp(t, tg, cum))


# ── chapter windows ─────────────────────────────────────────────────────────
W_DARK = (0.0, B["c_road"] + 1.6)
W_ROAD = (B["c_road"] - 1.0, B["c_fabric"] + 0.9)
W_FABRIC = (B["c_fabric"] - 0.2, B["c_bend"] + 1.4)
W_BEND = (B["c_bend"] - 0.8, B["c_block"] + 1.4)
W_BLOCK = (B["c_block"] - 0.8, B["c_arrow"] + 1.4)
W_ARROW = (B["c_arrow"] - 0.8, B["c_end"] + 1.8)
W_END = (B["c_end"] - 1.0, DURATION + 1)


def condense(t, w, fin=2.8, fout=2.0):
    """1 = formed. Condenses from dust at the window start, dissolves at its end."""
    return ss(w[0], w[0] + fin, t) * (1 - ss(w[1] - fout, w[1], t))


# ── DARK ────────────────────────────────────────────────────────────────────
def cam_dark(t):
    p = np.array([0.25 * np.sin(0.06 * t), 0.08 * np.sin(0.09 * t), -0.11 * t])
    tg = p + np.array([0.6 * np.sin(0.04 * t + 0.4), 0.15 * np.sin(0.05 * t), -10])
    return look(p, tg, roll=0.03 * np.sin(0.07 * t))


def dark(t):
    cam = cam_dark(t)
    reveal = 0.06 * ss(0.4, 4.6, t) + 0.94 * ss(4.4, 16.5, t) ** 0.9
    h = B["heart"]
    tb = h if t < h + 0.36 else h + 0.36
    beat = max(t - tb, 0.0)
    amp = (1.0 if tb == h else 0.7) * np.exp(-beat * 0.9) * (t > h)
    ev = B["evening"]
    gl = 0.15 + 1.4 * ss(ev - 0.3, ev + 0.9, t) * (1 - ss(ev + 1.2, ev + 5.0, t))
    w = env(t, *W_DARK, fin=0.01, fout=1.6)
    form = 1 - ss(B["slips"] - 0.2, W_DARK[1], t)
    draws = [dict(set="dust", mode=0, gain=1.0, cap=0.9, world=0.011, fade=w, form=form, scat=30.0,
                  scatO=cam["pos"] + cam["fwd"] * 6, fog=0.018, fogNear=0.3,
                  P0=(reveal, beat * 9.0, amp, 0), P1=(0, 0, -7, 0), P3=(-1, 0, 0, 0),
                  glight=(2.5, 1.2, -11.0), glightI=gl)]
    q = B["q"]
    tw = env(t, q - 0.6, B["feel"] + 2.6, fin=0.1, fout=1.8)
    if tw > 0:
        tf = ss(q - 0.6, q + 1.0, t) * (1 - ss(B["feel"] + 0.4, B["feel"] + 2.6, t))
        draws.append(dict(set="title", mode=1, gain=1.0, cap=0.045, fade=tw, form=tf, scat=9.0,
                          scatO=(0, 0, -8), fog=0.0, fogNear=0.2, glight=(0, 0, -7.5), glightI=0.25 * tf))
    return cam, draws


# ── ROAD ────────────────────────────────────────────────────────────────────
def road_speed(t):
    v = 1.4 + 1.2 * ss(B["c_road"], B["road"], t)
    v -= 1.9 * ss(B["between"] - 1.0, B["now"], t)
    v += 3.8 * ss(B["now"] + 0.8, B["c_fabric"] + 0.6, t)
    return v


_S_ROAD = integrate(road_speed, W_ROAD[0], W_ROAD[1] + 1)


def s_road(t):
    return -4.0 + _S_ROAD(t)


def road_gap(t):
    return 3.4 - 3.2 * ss(B["now"] + 0.6, B["c_fabric"] + 0.3, t)


def cam_road(t):
    s = s_road(t)
    bob = 0.05 * np.sin(1.3 * t)
    p = np.array([G.tcx(s) + 0.1 * np.sin(0.4 * t), G.tcy(s) - 0.25 + bob, -s])
    s2 = s + 7
    f = np.array([G.tcx(s2), G.tcy(s2) - 0.2, -s2]) - p
    f /= np.linalg.norm(f)
    a = np.radians(168) * (ss(B["behind"] - 0.4, B["past"] + 1.6, t) - ss(B["ahead"] - 0.6, B["open"] + 0.8, t))
    f = yawed(f, a)
    return look(p, p + f, roll=0.05 * np.sin(0.3 * t) + 0.12 * np.sin(a))


def road(t):
    cam = cam_road(t)
    s = s_road(t)
    snow = s + road_gap(t)
    flare = 0.5 + 1.6 * ss(B["between"], B["now"] + 0.2, t)
    w = env(t, *W_ROAD, fin=0.6, fout=0.8)
    form = ss(W_ROAD[0], W_ROAD[0] + 3.2, t)
    lc = np.array([G.tcx(snow), G.tcy(snow), -snow])
    common = dict(mode=2, fade=w, form=form, scat=14.0, scatO=cam["pos"], fog=0.095, fogNear=0.5,
                  P0=(snow, 0, flare, 22.0), glight=tuple(lc), glightI=0.9 + 1.2 * ss(B["between"], B["now"], t))
    return cam, [dict(set="tunnel", gain=1.0, area=0.006, cap=1.0, **common),
                 dict(set="tunnel", lines=True, gain=1.0, cap=0.07, **common)]


# ── FABRIC ──────────────────────────────────────────────────────────────────
def cam_fabric(t):
    t0 = W_FABRIC[0]
    k = ss(t0, B["einstein"] + 4.0, t)
    k2 = ss(B["four"] - 0.5, W_FABRIC[1], t)
    ang = 0.35 + 0.045 * (t - t0)
    r = 4.0 + 22.0 * k + 14 * k2
    h = 0.8 + 3.6 * k + 12 * k2
    p = np.array([r * np.sin(ang), h, r * np.cos(ang)])
    tg = np.array([0.0, 0.0 - 1.0 * k2, 0.0])
    return look(p, tg, roll=0.04 * np.sin(0.2 * t))


def fabric(t):
    cam = cam_fabric(t)
    grow = 1.08 * ss(B["einstein"] - 0.5, B["woven"] + 3.0, t)
    when = ss(B["when"] - 0.3, B["when"] + 0.8, t) * (1 - ss(B["four"] + 0.5, B["four"] + 2.5, t))
    age = t - B["place"] if t > B["place"] - 0.1 else -1.0
    w = env(t, *W_FABRIC, fin=0.5, fout=1.4)
    form = condense(t, W_FABRIC, fin=3.0, fout=2.0)
    ev = (2.0, 0.0, -2.0)
    common = dict(mode=3, fade=w, form=form, scat=12.0, scatO=(0, 0, 0), fog=0.022, fogNear=0.5,
                  P0=(grow, 3.0, when, 1.0), P1=(*ev, age), glight=ev, glightI=0.6 * (age > 0) * np.exp(-max(age, 0) * 0.4))
    return cam, [dict(set="fabric", gain=1.0, cap=0.32, **common),
                 dict(set="fabric", lines=True, gain=1.0, cap=0.065, **common)]


# ── BEND ────────────────────────────────────────────────────────────────────
W0 = 2.0 * np.pi / 1.7          # stationary clock: one turn per 1.7 s
GAMMA = 1 / np.sqrt(1 - 0.9 ** 2)  # moving clock at 0.9 c


def well_k(t):
    return ss(B["sink"] - 0.3, B["sink"] + 2.6, t)


def well_depth(x, z, t):
    return well_k(t) * 8.5 / np.sqrt(1 + (x * x + z * z) / 2.5)


def grav_rate(r):
    """Clock rate deep in the well: sqrt(1 - rs/r) with rs = 1.25 (illustrative units)."""
    return np.sqrt(max(1 - 1.25 / max(r, 1.3), 0.02))


def clock_B_x(t):
    return -17 + 8.5 * (t - B["fast"])


def clock_C_r(t):
    return mix(9.0, 1.7, ss(B["sink"] + 0.2, B["runs"] + 0.6, t))


SAT_R = 9.0


def sat_angle(t):
    return 0.55 * (t - B["sats"]) + 0.5


_EACH_R = np.array([2.2, 3.0, 4.2, 5.5, 7.0, 9.0, 12.0, 15.0])
_EACH_A = np.radians([200, 250, 150, 300, 110, 30, 340, 70])
_PH = {}


def _phase(name, rate, t0):
    if name not in _PH:
        _PH[name] = integrate(rate, t0, W_BEND[1] + 1, 4000)
    return _PH[name]


def clocks(t):
    """12 clocks: (center xyz, phase) and (alpha, radius, ring brightness)."""
    C = np.zeros((12, 4), np.float32)
    C2 = np.zeros((12, 4), np.float32)

    def put(i, x, z, ph, a, R=0.85, lift=1.4, rb=1.0):
        C[i] = (x, -well_depth(x, z, t) + lift, z, ph)
        C2[i] = (a, R, rb, 0)

    t0 = B["fast"] - 0.6
    a0 = env(t, t0, B["nonow"] + 0.5, fin=0.6, fout=1.0)
    put(0, -5.0, 6.0, W0 * (t - t0), a0)
    if B["fast"] - 0.6 < t < B["sink"] + 1.5:
        a1 = env(t, B["fast"] - 0.5, B["sink"] + 1.5, fin=0.5, fout=1.2)
        put(1, clock_B_x(t), 1.0, W0 / GAMMA * (t - t0), a1)
    tc = B["sink"] - 0.4
    phC = _phase("C", lambda x: W0 * grav_rate(clock_C_r(x)), tc)
    r = clock_C_r(t)
    put(2, r * np.cos(0.9), r * np.sin(0.9), phC(t), env(t, tc, B["nonow"] + 0.5, fin=0.5, fout=1.0))
    ts = B["sats"] - 0.5
    sa = sat_angle(t)
    put(3, SAT_R * np.cos(sa), SAT_R * np.sin(sa), _phase("S", lambda x: W0 * grav_rate(SAT_R) * 0.995, ts)(t),
        env(t, ts, B["nonow"] + 0.5, fin=0.5, fout=1.0), R=0.6, lift=0.9)
    te = B["each"] - 0.3
    for j, (rr, aa) in enumerate(zip(_EACH_R, _EACH_A)):
        aa2 = aa + 0.08 * (t - te) / max(rr, 1)
        ph = W0 * grav_rate(rr) * (t - te) + j * 0.9
        put(4 + j, rr * np.cos(aa2), rr * np.sin(aa2), ph, env(t, te + 0.12 * j, W_BEND[1], fin=0.6, fout=1.4),
            R=0.55, lift=0.8)
    return C, C2


def cam_bend(t):
    k1 = ss(B["sink"] - 0.5, B["sink"] + 3.0, t)
    k2 = ss(B["sats"] - 0.8, B["sats"] + 2.0, t)
    k3 = ss(B["nonow"] - 0.6, B["nonow"] + 1.4, t)
    k4 = ss(B["each"] - 0.5, B["each"] + 2.5, t)
    p = mix([1.0, 6.5, 19.0], [3.0, 4.2, 15.5], k1)
    p = mix(p, [0.0, 15.0, 19.0], k2)
    p = mix(p, [0.0, 22.0, 24.0], k3)
    p = mix(p, [6.0, 10.0, 15.0], k4)
    ang = 0.03 * (t - W_BEND[0])
    c, s = np.cos(ang), np.sin(ang)
    p = np.array([c * p[0] - s * p[2], p[1], s * p[0] + c * p[2]])
    tg = mix([0, 0.0, 1.0], [0, -3.8, 0], k1)
    tg = mix(tg, [0, -2.0, 0], k3)
    return look(p, tg, roll=0.03 * np.sin(0.15 * t))


def bend(t):
    cam = cam_bend(t)
    wk = well_k(t)
    rip = env(t, B["bends"] - 0.2, B["fast"] + 1.5, fin=0.5, fout=2.0)
    planes = []
    for j, (ang, dt) in enumerate([(0.25, 0.0), (1.25, 0.45), (2.35, 0.9)]):
        t0 = B["nonow"] + dt
        d = -30 + 13.0 * (t - t0)
        planes.append((ang, d, 1.3 * env(t, t0, t0 + 4.6, fin=0.4, fout=1.0), 0))
    sat_on = env(t, B["sats"] - 0.5, B["nonow"] + 0.5, fin=0.6, fout=1.0)
    C, C2 = clocks(t)
    w = env(t, *W_BEND, fin=0.5, fout=1.4)
    form = condense(t, W_BEND, fin=3.0, fout=2.0)
    common = dict(mode=4, fade=w, form=form, scat=12.0, scatO=(0, 0, 0), fog=0.02, fogNear=0.5,
                  P0=(0.0, 0.0, wk, 0.6 * wk), P1=(rip, max(t - B["bends"], 0), SAT_R if sat_on > 0.01 else 0.0, sat_angle(t)),
                  P2=planes[0], P3=planes[1], P4=planes[2], clk=C, clk2=C2,
                  glight=(0, -8.5 * wk + 1.5, 0), glightI=1.2 * wk)
    return cam, [dict(set="well", gain=1.0, cap=0.45, **common),
                 dict(set="well", lines=True, gain=1.0, cap=0.07, **common)]


# ── BLOCK ───────────────────────────────────────────────────────────────────
def block_spacing(t):
    return 1.15 + 0.75 * ss(B["frames"] - 0.6, B["frames"] + 2.2, t)


def cam_block(t):
    k1 = ss(W_BLOCK[0], B["block"] + 1.0, t)
    k2 = ss(B["simply"] - 0.5, B["frames"] + 2.0, t)
    top = 17 * block_spacing(t)
    p = mix([7.0, 2.6, 9.0], [17.0, 15.0, 24.0], k1)
    p = mix(p, [27.0, top * 0.95 + 4.0, 21.0], k2)
    tg = mix([0, 0.6, 0], [0, 8.0, 0], k1)
    tg = mix(tg, [0, top * 0.45, 0], k2)
    ang = 0.025 * (t - W_BLOCK[0])
    c, s = np.cos(ang), np.sin(ang)
    p = np.array([c * p[0] - s * p[2], p[1], s * p[0] + c * p[2]])
    return look(p, tg, roll=0.02 * np.sin(0.2 * t))


def block(t):
    cam = cam_block(t)
    built = 0.6 + 17.6 * ss(W_BLOCK[0] + 0.5, B["block"] + 0.5, t) ** 0.9
    nowk = (t - B["further"]) * 2.4
    nowk = min(nowk, 17.0) if t < B["passes"] else nowk
    inten = env(t, B["further"] - 0.3, B["passes"] + 1.6, fin=0.6, fout=1.6)
    alleq = ss(B["passes"] + 0.2, B["passes"] + 2.2, t)
    w = env(t, *W_BLOCK, fin=0.5, fout=1.4)
    form = condense(t, W_BLOCK, fin=2.6, fout=2.0)
    sp = block_spacing(t)
    common = dict(mode=5, fade=w, form=form, scat=10.0, scatO=(0, 8, 0), fog=0.02, fogNear=0.5,
                  P0=(0, nowk % 18.0, inten, alleq), P1=(sp, built, 0, 0),
                  glight=(0, (nowk % 18.0) * sp + 0.5, 0), glightI=0.8 * inten * (1 - alleq))
    return cam, [dict(set="block", gain=1.0, area=0.00055, cap=0.5, **common),
                 dict(set="block", lines=True, gain=1.0, cap=0.05, **common)]


# ── ARROW ───────────────────────────────────────────────────────────────────
def cam_arrow(t):
    k = ss(B["arrow"] - 0.8, B["oneway"] + 2.0, t)
    ang = 0.6 + 0.05 * (t - W_ARROW[0])
    p0 = np.array([12.5 * np.sin(ang), 1.6, 12.5 * np.cos(ang)])
    p = mix(p0, [9.0, 2.0, 21.0], k)
    tg = mix([0, 0, 0], [13.0, 0.0, 0.0], k)
    return look(p, tg, roll=0.03 * np.sin(0.2 * t))


def arrow(t):
    cam = cam_arrow(t)
    sig = 0.75 * np.sqrt(max(t - B["order"], 0.0)) * ss(B["order"] - 0.2, B["order"] + 0.6, t)
    tA = max(t - B["arrow"] + 0.3, 0.0)
    drift = 2.2 * tA * tA
    cool = ss(B["coffee"] - 0.2, B["coffee"] + 3.0, t)
    burnt = 1.02 * ss(B["stars"] - 0.1, B["stars"] + 2.6, t)
    w = env(t, *W_ARROW, fin=0.5, fout=1.8)
    form = condense(t, W_ARROW, fin=2.8, fout=1.6)
    return cam, [dict(set="crystal", mode=6, gain=1.0, cap=0.13, fade=w, form=form, scat=10.0, scatO=(0, 0, 0),
                      fog=0.02, fogNear=0.5, P0=(sig, drift, cool, burnt), P1=(0.12 * (t - W_ARROW[0]), 0, 0, 0),
                      glight=(0, 0, 0), glightI=1.6 * (1 - cool))]


# ── END ─────────────────────────────────────────────────────────────────────
def end_flow_speed(t):
    return 0.9 * (1 - ss(B["bring"] - 0.2, B["bring"] + 1.4, t))


_FLOW = integrate(end_flow_speed, W_END[0], DURATION + 1)


def cam_end(t):
    k = t - W_END[0]
    p = np.array([0.6 * np.sin(0.05 * k), 0.4 + 0.2 * np.sin(0.04 * k), 9.0 + 0.32 * k])
    return look(p, p + np.array([0.0, -0.05, -1.0]), roll=0.02 * np.sin(0.1 * k))


def end(t):
    cam = cam_end(t)
    zc = cam["pos"][2]
    sweep_d = mix(zc - 2.0, zc - 48.0, ss(B["story"] - 0.2, B["deepest"] + 0.4, t))
    sweep_i = env(t, B["story"] - 0.4, B["deepest"] + 0.6, fin=0.5, fout=0.8)
    ext = mix(-0.1, 1.06, ss(B["deepest"] - 0.4, B["why"] + 1.8, t))
    w = env(t, *W_END, fin=1.6, fout=0.01)
    draws = [dict(set="dust", mode=0, gain=1.0, cap=0.7, world=0.007, fade=w, form=ss(W_END[0], W_END[0] + 3.5, t),
                  scat=18.0, scatO=cam["pos"], fog=0.016, fogNear=0.3, P0=(2.0, 0, 0, 0),
                  P2=(0, 0, -1, sweep_i), P3=(ext, -sweep_d, _FLOW(t), 0), P1=(0, 0, -1000, 0),
                  glight=(0, 0, 0), glightI=0.0)]
    one = env(t, B["why"] - 1.2, B["all"] + 2.4, fin=1.2, fout=2.0)
    if one > 0:
        pulse = 1.0 + 1.6 * np.exp(-((t - B["all"] - 0.25) / 0.45) ** 2)
        draws.append(dict(set="one", mode=7, gain=pulse, cap=1.0, fade=one, fog=0.0, fogNear=0.3, world=0.02,
                          glight=(0, 0, 0), glightI=0.0))
    return cam, draws


CHAPTERS = [(W_DARK, dark), (W_ROAD, road), (W_FABRIC, fabric), (W_BEND, bend), (W_BLOCK, block),
            (W_ARROW, arrow), (W_END, end)]


def camdust_k(t):
    """Volumetric dust: absent in the first darkness, gone before the last particle."""
    return 0.9 * ss(3.0, 14.0, t) * (1 - ss(B["deepest"], B["why"] + 0.5, t))


def post(t):
    flash = 0.55 * np.exp(-((t - B["c_fabric"] - 0.05) / 0.32) ** 2)
    fade = 1 - ss(B["all"] + 2.6, B["all"] + 4.4, t)
    return dict(flash=float(flash), fade=float(fade))


# ── renderer ────────────────────────────────────────────────────────────────
def lin(hx):
    h = hx.lstrip("#")
    return tuple(float((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


SETS = ["dust", "title", "tunnel", "fabric", "well", "block", "crystal", "camdust"]


class Renderer:
    def __init__(self, W, H):
        self.W, self.H = W, H
        import os
        kw = {"backend": os.environ["WIT_GL_BACKEND"]} if os.environ.get("WIT_GL_BACKEND") else {}
        self.ctx = ctx = moderngl.create_context(standalone=True, require=430, **kw)
        print("GL:", ctx.info.get("GL_RENDERER"), ctx.info.get("GL_VERSION"), flush=True)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def full(fs):
            p = ctx.program(vertex_shader="#version 430\n" + (SH / "quad.vert").read_text(),
                            fragment_shader="#version 430\n" + (SH / fs).read_text())
            return p, ctx.vertex_array(p, [(quad, "2f", "in_pos")])

        self.down, self.up, self.comp = full("down.frag"), full("up.frag"), full("composite.frag")
        vs = (SH / "world.vert").read_text()
        self.pp = ctx.program(vertex_shader="#version 430\n" + vs,
                              fragment_shader="#version 430\n" + (SH / "points.frag").read_text())
        self.lp = ctx.program(vertex_shader="#version 430\n#define LINES\n" + vs,
                              fragment_shader="#version 430\n" + (SH / "lines.frag").read_text())
        self.vao = {}
        total = 0
        for name in SETS:
            d = G.load(name)
            for kind, prog in (("pts", self.pp), ("lines", self.lp)):
                if kind in d:
                    buf = ctx.buffer(d[kind].astype("f4").tobytes())
                    self.vao[(name, kind)] = (ctx.vertex_array(prog, [(buf, "3f 4f 4f", "in_pos", "in_a", "in_b")]),
                                              len(d[kind]))
                    total += len(d[kind])
            del d
        one = G.pack(np.zeros((1, 3)), 1.6, 0.25, 5.0, 0.0)
        buf = ctx.buffer(one.tobytes())
        self.vao[("one", "pts")] = (ctx.vertex_array(self.pp, [(buf, "3f 4f 4f", "in_pos", "in_a", "in_b")]), 1)
        print(f"{total:,} vertices on the GPU")

        def target(w, h, dtype="f2", comps=4):
            tx = ctx.texture((w, h), comps, dtype=dtype)
            tx.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tx.repeat_x = tx.repeat_y = False
            return tx, ctx.framebuffer(color_attachments=[tx])

        self.acc = target(W, H)
        self.levels = []
        w, h = W, H
        for _ in range(7):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.haze = target(self.levels[3][0].width, self.levels[3][0].height)
        self.fin = target(W, H, "f1", 3)
        self.k = H / 1080
        for prog in (self.pp, self.lp):
            setu(prog, "u_green", lin("#7FD39A"))

    def _camera(self, prog, cam, t):
        tanY = float(np.tan(np.radians(cam["fov"]) / 2))
        for n, v in dict(u_cam=tuple(cam["pos"]), u_right=tuple(cam["right"]), u_up=tuple(cam["up"]),
                         u_fwd=tuple(cam["fwd"]), u_fy=self.H / (2 * tanY), u_tanY=tanY,
                         u_tanX=tanY * self.W / self.H, u_t=float(t)).items():
            setu(prog, n, v)

    def _draw(self, d, cam, t):
        lines = d.get("lines", False)
        prog = self.lp if lines else self.pp
        key = (d["set"], "lines" if lines else "pts")
        if key not in self.vao:
            return
        self._camera(prog, cam, t)
        z4 = (0.0, 0.0, 0.0, 0.0)
        u = dict(u_mode=int(d.get("mode", 0)), u_form=float(d.get("form", 1.0)), u_scat=float(d.get("scat", 10.0)),
                 u_scatO=tuple(map(float, d.get("scatO", cam["pos"]))), u_gain=float(d.get("gain", 1.0)),
                 u_area=float(d.get("area", 0.0)), u_cap=float(d.get("cap", 0.3)) * (1.0 if lines else 1.0),
                 u_base=max(1.0, 1.5 * self.k), u_fog=float(d.get("fog", 0.03)),
                 u_fogNear=float(d.get("fogNear", 0.4)), u_fade=float(d.get("fade", 1.0)),
                 u_world=float(d.get("world", 0.0)),
                 u_glight=tuple(map(float, d.get("glight", (0, 0, 0)))), u_glightI=float(d.get("glightI", 0.0)))
        for i in range(5):
            u[f"u_P{i}"] = tuple(map(float, d.get(f"P{i}", (-1, 0, 0, 0) if i == 3 else z4)))
        for n, v in u.items():
            setu(prog, n, v)
        if "u_clk" in prog:
            C = d.get("clk", np.zeros((12, 4), np.float32))
            C2 = d.get("clk2", np.zeros((12, 4), np.float32))
            prog["u_clk"].write(np.ascontiguousarray(C, dtype="f4").tobytes())
            prog["u_clk2"].write(np.ascontiguousarray(C2, dtype="f4").tobytes())
        if d["set"] == "one":
            setu(prog, "u_cam", tuple(cam["pos"] - cam["fwd"] * 6.0 - cam["up"] * 0.15))
        vao, n = self.vao[key]
        vao.render(moderngl.LINES if lines else moderngl.POINTS, vertices=n)

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, idx=0):
        ctx = self.ctx
        fb = self.acc[1]
        fb.use()
        fb.clear(0, 0, 0, 0)
        ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        best, bestw = None, -1
        for (a, b), fn in CHAPTERS:
            if a <= t <= b:
                cam, draws = fn(t)
                for d in draws:
                    self._draw(d, cam, t)
                wgt = max([d.get("fade", 1.0) for d in draws] + [0])
                if wgt > bestw:
                    best, bestw = cam, wgt
        if best is not None:   # volumetric dust riding with the camera
            self._draw(dict(set="camdust", mode=8, gain=1.0, cap=0.22, world=0.006, fog=0.0, fogNear=0.15,
                            P0=(9.0, 0, 0, 0), fade=post(t)["fade"] * camdust_k(t)), best, t)
        ctx.disable(moderngl.BLEND)
        s = self.acc[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(*self.down, fbo, s, u_texel=(1 / s.width, 1 / s.height), u_thresh=0.55 if i == 0 else 0.0)
            s = tex
        # haze = copy of the wide level before upsampling adds the fine ones
        self._pass(*self.up, self.haze[1], self.levels[4][0],
                   u_texel=(1 / self.levels[4][0].width, 1 / self.levels[4][0].height))
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(*self.up, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        self.fin[1].use()
        self.acc[0].use(0)
        self.levels[0][0].use(1)
        self.haze[0].use(2)
        c = self.comp[0]
        c["scene"].value, c["bloom"].value, c["haze"].value = 0, 1, 2
        P = post(t)
        for k, v in dict(u_bloom=0.4, u_haze=1.6, u_hazeCol=(0.75, 1.0, 0.85), u_exposure=1.0, u_vig=0.5,
                         u_grain=0.03, u_frame=float(idx % 997), u_flash=P["flash"], u_fade=P["fade"],
                         u_res=(float(self.W), float(self.H))).items():
            setu(c, k, v)
        self.comp[1].render(moderngl.TRIANGLE_STRIP)
        ctx.finish()
        return self.fin[1].read(components=3, alignment=1)


# ── CLI ─────────────────────────────────────────────────────────────────────
def size_for(h):
    return int(round(h * 16 / 9 / 2) * 2), h


def to_img(buf, w, h):
    from PIL import Image
    return Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)


def parse_time(x):
    """'heart', 'heart+0.5', '12.3'."""
    for op in ("+", "-"):
        if op in x[1:]:
            a, b = x.rsplit(op, 1)
            if a in B:
                return B[a] + (float(b) if op == "+" else -float(b))
    return B[x] if x in B else float(x)


def cmd_still(a):
    w, h = size_for(a.height)
    r = Renderer(w, h)
    (OUT / "stills").mkdir(parents=True, exist_ok=True)
    ims = []
    for x in a.at:
        t = parse_time(x)
        t0 = time.time()
        im = to_img(r.frame(t, int(t * 30)), w, h)
        im.save(OUT / "stills" / f"{t:06.2f}_{x.replace('+', 'p')}{a.tag}.png")
        ims.append((x, im))
        print(f"  {x:>14s}  t={t:6.2f}s  {time.time() - t0:.2f}s/frame")
    if len(ims) > 1:
        from PIL import Image, ImageDraw
        cols = 2 if len(ims) <= 4 else 3
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (60, 60, 60))
        dr = ImageDraw.Draw(sh)
        for i, (x, im) in enumerate(ims):
            xx, yy = (i % cols) * (w + 6), (i // cols) * (h + 6)
            sh.paste(im, (xx, yy))
            dr.text((xx + 8, yy + 6), f"{x}  {parse_time(x):.2f}s", fill=(255, 200, 80))
        sh.save(OUT / f"contact{a.tag}.png")
        print(OUT / f"contact{a.tag}.png")


class SimpleProgress:
    """Stand-in for aion.progress.Progress when aion is not installed: one log line every ~2%."""

    def __init__(self, name, total):
        self.name, self.total, self.n, self.t0, self.last = name, total, 0, time.time(), -1

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def update(self, k=1):
        self.n += k
        pct = int(100 * self.n / self.total)
        if pct // 2 != self.last:
            self.last = pct // 2
            el = time.time() - self.t0
            eta = el / self.n * (self.total - self.n)
            print(f"PROGRESS {self.name} {pct:3d}% {self.n}/{self.total} fr  {self.n / el:.2f} fr/s  "
                  f"elapsed {el / 60:.1f} min  ETA {eta / 60:.1f} min", flush=True)

    def close(self, out=None):
        print(f"done {self.name} in {(time.time() - self.t0) / 60:.1f} min → {out}", flush=True)


def cmd_freeze(a):
    import json
    (HERE / "beats.json").write_text(json.dumps({"duration": DURATION, "beats": B}, indent=1))
    print(f"✔ {len(B)} beats → {HERE / 'beats.json'}")


def cmd_video(a):
    try:
        from aion.progress import Progress
    except ImportError:
        Progress = SimpleProgress
    w, h = size_for(a.height)
    t0 = parse_time(a.start) if a.start else 0.0
    t1 = parse_time(a.stop) if a.stop else DURATION
    n = int(round((t1 - t0) * a.fps))
    name = f"what_is_time_{h}p{a.fps}" + (a.tag or "")
    silent = OUT / f"{name}_silent.mp4"
    out = OUT / f"{name}.mp4"
    r = Renderer(w, h)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
         "-r", str(a.fps), "-i", "-", "-vf", "vflip", "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf),
         "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-movflags", "+faststart", str(silent)], stdin=subprocess.PIPE)
    with Progress(name, n) as bar:
        for i in range(n):
            ff.stdin.write(r.frame(t0 + i / a.fps, i))
            bar.update(1)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        bar.close(silent)
    audio = HERE / "assets" / "audio.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}",
                    "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    silent.unlink()
    print(f"✔ {n} frames → {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still")
    s.add_argument("--at", nargs="+", default=["q", "heart", "past", "open", "now", "woven", "place", "slower",
                                               "runs", "nonow+1", "block", "frames+2", "coffee", "arrow+2",
                                               "story+1", "all"])
    s.add_argument("--height", type=int, default=360)
    s.add_argument("--tag", default="")
    s = sub.add_parser("video")
    s.add_argument("--height", type=int, default=540)
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--crf", type=int, default=17)
    s.add_argument("--preset", default="medium")
    s.add_argument("--start")
    s.add_argument("--stop")
    s.add_argument("--tag", default="")
    sub.add_parser("freeze")
    a = ap.parse_args()
    dict(still=cmd_still, video=cmd_video, freeze=cmd_freeze)[a.cmd](a)


if __name__ == "__main__":
    main()
