"""'Does the Past Still Exist?': a point-cloud journey, synced to the narration. moderngl headless on the Radeon R4.

    uv run python lab/2026-11-15-does-the-past-exist/render.py still --height 360                # contact sheet
    uv run python lab/2026-11-15-does-the-past-exist/render.py still --at people+2 where+2 --height 540
    uv run python lab/2026-11-15-does-the-past-exist/render.py video --height 480 --fps 24 --preset veryfast
    uv run python lab/2026-11-15-does-the-past-exist/render.py video --height 1080 --fps 30               # final

Every frame is a pure function of absolute audio time t. All times come from beats.py (word cues).
Chapters (each its own world + camera; neighbours crossfade by dissolving / condensing):
  FORM    a remembered place condenses from dust (ground, a tree, the light, three people), holds, loosens in
          the wind and dissolves into darkness; the title forms in particles
  TUNNEL  the camera travels an endless point-cloud tunnel of time; moment rings flash as they pass; dust streaks;
          the camera turns to look back: the past breaks into drifting fragments; the remembered place appears
          in pieces, rebuilds itself a little differently, fades, blurs
  LIGHT   space: a photon crosses from the Sun to the Earth; Andromeda, and its light still on the way; shells
          of old light converge on the Earth: the past is still arriving
  BLOCK   the remembered place as a stack of moments along the time axis; a 'now' plane, then a tilted 'now' for
          another observer; the block all lit at once; presentism, the growing block, eternalism
  END     empty, infinite space; the block's traces scatter; the question forms; one particle; dark
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
except ImportError:            # standalone: beats frozen by `render.py freeze`
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


def integrate(fn, t0, t1, n=6000):
    tg = np.linspace(t0, t1, n)
    v = np.array([fn(x) for x in tg])
    cum = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(tg))])
    return lambda t: float(np.interp(t, tg, cum))


# ── chapter windows ─────────────────────────────────────────────────────────
W_FORM = (0.0, B["c_flow"] + 2.2)
W_TUN = (B["c_flow"] - 0.4, B["c_light"] + 2.0)
W_LIGHT = (B["c_light"] - 0.6, B["c_layers"] + 1.8)
W_BLOCK = (B["c_layers"] - 0.6, B["scattered"] + 3.0)
W_END = (B["c_end"] - 0.5, DURATION + 1)


def condense(t, w, fin=2.8, fout=2.0):
    """1 = formed. Condenses from dust at the window start, dissolves at its end."""
    return ss(w[0], w[0] + fin, t) * (1 - ss(w[1] - fout, w[1], t))


# ── FORM ────────────────────────────────────────────────────────────────────
def cam_form(t):
    k = ss(0.0, B["gone"] + 1.0, t)
    ang = mix(0.32, -0.08, k) + 0.02 * np.sin(0.2 * t)
    rad = mix(11.5, 7.2, k ** 0.8) - 2.2 * ss(B["gone"], W_FORM[1], t)
    p = np.array([rad * np.sin(ang), mix(2.3, 1.55, k), rad * np.cos(ang) - 1.0])
    tg = np.array([0.4 * np.sin(ang), 1.05, -2.2])
    return look(p, tg, roll=0.015 * np.sin(0.13 * t), fov=50.0)


_cq = cam_form(B["q"] + 1.0)
TITLE_POS = _cq["pos"] + _cq["fwd"] * 9.0


def form(t):
    cam = cam_form(t)
    w = env(t, *W_FORM, fin=0.01, fout=1.6)
    reveal = ss(B["think"] - 0.4, B["light"] + 0.6, t) ** 0.8
    people = ss(B["people"] - 0.4, B["people"] + 2.2, t)
    light = ss(B["light"] - 0.5, B["light"] + 1.6, t)
    scan = (t - B["light"] + 0.3) * 5.5
    wind = 0.6 * ss(B["andthen"] - 0.2, B["gone"] + 2.0, t)
    fm = (0.4 + 0.6 * ss(B["think"] - 0.8, B["place"] + 1.0, t)) * (1 - ss(B["gone"] - 0.2, B["q"] + 0.4, t))
    sw = 1.0 - ss(B["gone"] + 0.5, B["q"] + 1.0, t)
    common = dict(mode=2, fade=w * sw if t > B["gone"] else w, form=fm, scat=11.0, scatO=(0, 1.0, 0), fog=0.03,
                  fogNear=0.4, P0=(reveal, people, light, scan), P1=(0, 0, 0, 0), P2=(0, 0, 0, 1.0),
                  P4=(wind, 0, 0, 0), glight=tuple(G.SUN_AT * 0.4 + [0, 1.0, 0]), glightI=0.08 * light)
    dust_rev = 0.06 * ss(0.4, B["think"], t) + 0.5 * ss(B["think"], B["people"] + 2.0, t) + 0.44 * ss(B["gone"], B["q"] + 2, t)
    draws = [dict(set="scene", gain=1.0, area=0.00022, cap=0.22, **common),
             dict(set="scene", lines=True, gain=1.0, cap=0.05 * light, **common),
             dict(set="dust", mode=0, gain=1.0, cap=0.6, world=0.011, fade=w, form=1.0, fog=0.02, fogNear=0.3,
                  P0=(dust_rev, 0, 0, 0), P3=(-1, 0, 0, 0))]
    tw = env(t, B["q"] - 0.4, W_FORM[1], fin=0.1, fout=1.4)
    if tw > 0:
        tf = ss(B["q"] - 0.3, B["q"] + 1.8, t) * (1 - ss(B["c_flow"] + 0.2, W_FORM[1], t))
        draws.append(dict(set="title", mode=1, gain=1.0, cap=0.035, fade=tw, form=1.0, scat=9.0,
                          scatO=tuple(TITLE_POS - _cq["fwd"] * 3), fog=0.0, fogNear=0.2, P0=(tf, tf, 0, 0),
                          P1=(*TITLE_POS, 1.0), glight=tuple(TITLE_POS), glightI=0.2 * tf))
    return cam, draws


# ── TUNNEL (flow of time, then memory) ──────────────────────────────────────
def tun_speed(t):
    v = 0.7 + 3.2 * ss(B["live"] - 1.2, B["instant"] + 0.5, t)
    v += 1.1 * env(t, B["arrives"] - 0.4, B["tunnel"] + 0.8, fin=0.8, fout=1.2)
    v -= 3.7 * ss(B["past"] - 0.8, B["where"] + 0.4, t)
    return max(v, 0.22)


_S_T = integrate(tun_speed, W_TUN[0] - 1, W_TUN[1] + 1)


def s_tun(t):
    return -12.0 + _S_T(t)


def cam_tun(t):
    s = s_tun(t)
    p = np.array([G.tcx(s) + 0.12 * np.sin(0.4 * t), G.tcy(s) - 0.55 + 0.05 * np.sin(1.1 * t), -s])
    s2 = s + 7
    f = np.array([G.tcx(s2), G.tcy(s2) - 0.35, -s2]) - p
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0])
    r /= np.linalg.norm(r)
    a = np.pi * ss(B["past"] + 0.3, B["where"] + 1.8, t)
    d = np.cos(a) * f + np.sin(a) * r
    d[1] = mix(d[1], -0.04, ss(B["past"], B["where"], t))
    return look(p, p + d * 7, roll=0.05 * np.sin(0.3 * t) + 0.12 * np.sin(a) * np.sin(a / 2))


S_MEM = s_tun(B["where"]) - 10.0     # where the remembered place reappears, behind us


def tunnel(t):
    cam = cam_tun(t)
    s = s_tun(t)
    vel = (cam_tun(t)["pos"] - cam_tun(t - 1 / 30)["pos"]) * 30
    streak = ss(B["instant"] - 0.6, B["instant"] + 0.6, t) * (1 - ss(B["past"] - 0.6, B["where"] - 0.4, t))
    ring = 0.35 + 0.65 * env(t, B["arrives"] - 0.4, B["leaves"] + 1.0, fin=0.6, fout=1.2)
    mem_len = mix(500.0, 34.0, ss(B["where"] - 1.0, B["recordings"], t))
    mem_len = mix(mem_len, 14.0, ss(B["fragments"] - 0.4, B["blur"] + 1.5, t))
    frag = 0.25 + 0.75 * ss(B["where"] - 1.0, B["pieces"] + 1.0, t)
    ffade = 0.85 * ss(B["fragments"] - 0.4, B["blur"] + 1.4, t)
    w = env(t, *W_TUN, fin=1.6, fout=1.8)
    fm = condense(t, W_TUN, fin=2.4, fout=2.0)
    dimm = 1 - 0.7 * env(t, B["pieces"] - 0.8, B["c_light"], fin=1.5, fout=1.0)
    common = dict(mode=3, fade=w * dimm, form=fm, scat=14.0, scatO=cam["pos"], fog=0.1, fogNear=0.6,
                  P0=(s, streak, ring, mem_len), P1=(frag, ffade, 0, 0), P2=(*vel, 0.09),
                  glight=tuple(cam["pos"] + cam["fwd"] * 3), glightI=0.2)
    draws = [dict(set="tunnel", gain=1.0, area=0.0030, cap=0.9, **common),
             dict(set="tunnel", lines=True, gain=1.0, cap=0.06, **common)]
    mw = env(t, B["pieces"] - 0.8, W_TUN[1], fin=1.0, fout=2.0)
    if mw > 0:
        mf = ss(B["pieces"] - 0.8, B["pieces"] + 1.8, t) * (1 - ss(B["c_light"] - 1.0, W_TUN[1], t))
        fragS = 0.2 + 0.35 * ss(B["recordings"] - 0.5, B["recordings"] + 1.5, t)
        clock = max(t - (B["rebuilds"] - 0.7), -1.0) * 0.8
        amt = env(t, B["remember"] - 0.3, B["fragments"] + 0.5, fin=0.6, fout=1.0)
        fade = 0.75 * ss(B["fragments"] - 0.3, B["fragments"] + 1.6, t)
        blur = ss(B["blur"] - 0.3, B["blur"] + 1.5, t)
        ctr = (G.tcx(S_MEM), G.tcy(S_MEM) - 2.0, -S_MEM)
        draws.append(dict(set="scene", mode=2, gain=1.0, area=0.00022 * 0.38, cap=0.3, fade=mw, form=mf, scat=4.0,
                          scatO=ctr, fog=0.05, fogNear=0.5, P0=(1.0, 1.0, 1.0, 50.0), P1=(fragS, clock, fade, blur),
                          P2=(*ctr, 0.62), P4=(0.0, amt, 6.0, np.pi), glight=ctr, glightI=0.0))
    return cam, draws


# ── LIGHT ───────────────────────────────────────────────────────────────────
def cam_light(t):
    t0 = W_LIGHT[0]
    p1 = np.array([7.5 + 0.08 * (t - t0), 3.2, 16.5 - 0.1 * (t - t0)])
    tg1 = np.array([8.0, 0.0, 0.0])
    k2 = ss(B["andromeda"] - 1.4, B["andromeda"] + 1.6, t)
    p2 = G.EARTH + np.array([9.0, 4.0, 14.0]) + np.array([0, 0.0, -0.15]) * (t - B["andromeda"])
    tg2 = G.GAL
    k3 = ss(B["lookout"] - 1.0, B["lookout"] + 2.2, t)
    p3 = G.EARTH + np.array([1.2 * np.sin(0.1 * t), 2.6, 9.0 - 0.25 * max(t - B["lookout"], 0)])
    tg3 = G.EARTH + np.array([0.0, -0.2, 0.0])
    p = mix(mix(p1, p2, k2), p3, k3)
    tg = mix(mix(tg1, tg2, k2), tg3, k3)
    d = tg - p
    d /= np.linalg.norm(d)
    return look(p, p + d * 10, roll=0.02 * np.sin(0.2 * t))


def light(t):
    cam = cam_light(t)
    w = env(t, *W_LIGHT, fin=0.8, fout=1.8)
    fm = condense(t, W_LIGHT, fin=2.6, fout=2.2)
    stars = 0.25 + 0.75 * ss(B["records"] - 0.8, B["records"] + 2.0, t)
    sunw = ss(W_LIGHT[0] + 0.5, B["sunlight"] - 0.3, t)
    gal = ss(B["andromeda"] - 1.2, B["andromeda"] + 1.2, t)
    shells = ss(B["lookout"] - 0.4, B["back"] + 1.2, t)
    t_arr = B["eight"] + 0.5
    sunp = np.clip((t - B["sunlight"] - 0.2) / (t_arr - B["sunlight"] - 0.2), 0, 1.02)
    glint = float(np.exp(-((t - t_arr) / 0.45) ** 2)) + 0.6 * float(np.exp(-((t - B["arriving"] - 0.4) / 0.5) ** 2))
    galp = np.clip((t - B["andromeda"] - 0.3) / (B["arriving"] + 0.4 - B["andromeda"] - 0.3), 0, 1.0) ** 1.4
    common = dict(mode=4, fade=w, form=fm, scat=16.0, scatO=tuple(G.EARTH), fog=0.0012, fogNear=0.5,
                  P0=(sunp, galp, glint, 0), P1=(*G.EARTH, 30.0), P2=(gal, sunw, stars, shells),
                  P4=(-0.07, 0, 0, 0), glight=(0, 0, 0), glightI=0.0)
    return cam, [dict(set="cosmos", gain=1.0, cap=0.05, **common),
                 dict(set="cosmos", lines=True, gain=1.0, cap=0.12, **common)]


# ── BLOCK (layers of moments; then the doubt) ───────────────────────────────
def cam_block(t):
    t0 = W_BLOCK[0]
    p0 = np.array([11.0, 3.4, 15.0])
    tg0 = np.array([0.0, 1.2, 3.0])
    k1 = ss(B["nonow"] - 0.5, B["whatis"] + 1.2, t)                      # higher: see the tilted 'now'
    p1 = np.array([12.0, 13.0, 15.0])
    tg1 = np.array([0.0, 0.5, 0.0])
    k2 = ss(B["block"] - 0.8, B["together"] + 1.5, t)                    # pull back: the whole block
    p2 = np.array([26.0, 9.0, 27.0])
    tg2 = np.array([0.0, 1.2, 0.0])
    k3 = ss(B["besso"] - 1.0, B["wrote"] + 0.5, t) * (1 - ss(B["illusion"], B["agree"] + 0.5, t))  # alongside
    z3 = mix(24.0, -6.0, ss(B["besso"] - 1.0, B["agree"] + 1.0, t))
    p3 = np.array([9.5, 2.0, z3])
    tg3 = np.array([0.0, 1.4, z3 - 9.0])
    k35 = ss(B["illusion"], B["agree"] + 1.5, t)                         # doubt: a closer oblique view
    p35 = np.array([15.0, 7.5, 18.0])
    k4 = ss(B["c_end"] - 1.0, W_BLOCK[1], t)                            # drift away into the emptiness
    p4 = np.array([30.0, 14.0, 44.0])
    p = mix(mix(mix(p0, p1, k1), p2, k2), p3, k3)
    tg = mix(mix(mix(tg0, tg1, k1), tg2, k2), tg3, k3)
    p = mix(p, p35, k35)
    tg = mix(tg, [0.0, 1.0, 0.0], k35)
    p = mix(p, p4, k4)
    ang = 0.012 * (t - t0) * (1 - k3)
    c, s = np.cos(ang), np.sin(ang)
    p = np.array([c * p[0] - s * p[2], p[1], s * p[0] + c * p[2]])
    return look(p, tg, roll=0.02 * np.sin(0.2 * t))


def block(t):
    cam = cam_block(t)
    sp = 2.3
    # the flowing present, then frozen in the middle
    nowA = mix(0.0 + (t - B["further"]) * 1.25, 7.5, ss(B["nonow"] - 1.5, B["nonow"] + 0.5, t))
    tilt = 0.75 * ss(B["observer"] - 0.6, B["pastfut"] + 0.6, t) - 1.25 * ss(B["pastfut"] + 0.8, B["another"] + 0.6, t)
    tilt += 0.9 * ss(B["another"] + 0.8, B["block"] - 0.6, t)
    showA = env(t, B["further"] - 0.3, B["block"] + 0.5, fin=1.2, fout=1.6)
    showB = env(t, B["whatis"] - 0.6, B["block"] + 0.5, fin=1.0, fout=1.6)
    alllit = ss(B["block"] - 0.2, B["together"] + 0.8, t) * (1 - ss(B["present"] - 0.6, B["present"] + 0.6, t))
    alllit = max(alllit, ss(B["fixed"] - 0.5, B["fixed"] + 0.5, t))
    pres = env(t, B["present"] - 0.6, B["fixed"] + 0.2, fin=1.2, fout=1.2)
    built = 7.0 + 3.5 * ss(B["fixed"] + 0.5, B["written"] + 2.0, t)
    unf = env(t, B["fixed"] - 0.3, B["every"] + 0.3, fin=0.9, fout=1.0)
    feelk = (t - B["feel"] + 0.6) * 4.5 - 1.0
    feel = env(t, B["feel"] - 0.6, B["decided"] + 0.2, fin=0.6, fout=1.0)
    flick = ss(B["decided"] - 0.3, B["decided"] + 1.0, t) * (1 - ss(B["c_end"], B["lived"] + 1, t))
    base = 0.32 * (1 - 0.5 * ss(B["c_end"], B["behindyou"], t))
    w = env(t, *W_BLOCK, fin=0.8, fout=2.2)
    fm = condense(t, W_BLOCK, fin=2.4, fout=3.0)
    fm = min(fm, 1 - 0.75 * ss(B["scattered"] - 0.3, B["scattered"] + 1.5, t))
    common = dict(mode=5, fade=w, form=fm, scat=24.0, scatO=(0, 1.0, 0), fog=0.02, fogNear=0.5,
                  P0=(nowA, tilt, showA, showB), P1=(sp, built, unf, pres), P2=(alllit, 3.0, feelk, feel),
                  P4=(0, base, flick, 0), glight=(0, 1.5, -(nowA - 7.5) * sp), glightI=0.5 * showA)
    return cam, [dict(set="block", gain=1.0, area=0.00032, cap=0.45, **common),
                 dict(set="block", lines=True, gain=1.0, cap=0.05, **common)]


# ── END ─────────────────────────────────────────────────────────────────────
def end_flow_speed(t):
    return 0.6 * (1 - ss(B["q1"] - 1.0, B["q1"] + 1.0, t)) + 0.06


_FLOW = integrate(end_flow_speed, W_END[0], DURATION + 1)


def cam_end(t):
    k = t - W_END[0]
    p = np.array([0.5 * np.sin(0.05 * k), 0.4 + 0.2 * np.sin(0.04 * k), 6.0 - 0.32 * k])
    return look(p, p + np.array([0.0, -0.03, -1.0]), roll=0.02 * np.sin(0.1 * k))


_c1 = cam_end(B["q1"] + 0.5)
Q_POS = _c1["pos"] + _c1["fwd"] * 7.0


def end(t):
    cam = cam_end(t)
    ext = mix(-0.1, 1.06, ss(B["go"] + 1.2, DURATION - 1.2, t))
    w = env(t, *W_END, fin=2.0, fout=0.01)
    draws = [dict(set="dust", mode=0, gain=1.0, cap=0.7, world=0.009, fade=w, form=ss(W_END[0], W_END[0] + 4.0, t),
                  scat=18.0, scatO=cam["pos"], fog=0.018, fogNear=0.3, P0=(2.0, 0, 0, 0),
                  P3=(ext, 0, _FLOW(t), 0), glight=(0, 0, 0), glightI=0.0)]
    sw = env(t, B["travelling"] - 0.6, B["q1"] + 1.0, fin=0.6, fout=2.0)    # its light is still travelling
    if sw > 0:
        c0 = cam_end(B["travelling"])
        ctr = c0["pos"] + c0["fwd"] * 26.0
        draws.append(dict(set="cosmos", mode=4, gain=1.0, cap=0.2, fade=sw, form=1.0, fog=0.02, fogNear=0.5,
                          P0=(0, 0, 0, 0), P1=(*ctr, 60.0), P2=(0, 0, 0, 1.0), P4=(0.05, 0, 0, 0),
                          glight=(0, 0, 0), glightI=0.0))
    qw = env(t, B["q1"] - 0.6, B["go"] + 4.5, fin=0.3, fout=1.6)
    if qw > 0:
        l1 = ss(B["q1"] - 0.4, B["exists"] + 1.2, t)
        l2 = ss(B["q2"] - 0.3, B["q2"] + 1.4, t)
        out = 1 - ss(B["go"] + 2.4, B["go"] + 4.5, t)
        draws.append(dict(set="question", mode=1, gain=1.0, cap=0.035, fade=qw, form=out, scat=6.0,
                          scatO=tuple(Q_POS), fog=0.0, fogNear=0.2, P0=(l1, l2, 0, 0), P1=(*Q_POS, 1.0),
                          glight=tuple(Q_POS), glightI=0.15))
    one = env(t, B["go"] + 2.5, DURATION + 1, fin=1.2, fout=0.01)
    if one > 0:
        pulse = 1.0 + 1.6 * np.exp(-((t - B["go"] - 4.4) / 0.45) ** 2)
        draws.append(dict(set="one", mode=10, gain=pulse, cap=1.0, fade=one * (1 - ss(DURATION - 2.2, DURATION - 0.5, t)),
                          fog=0.0, fogNear=0.3, world=0.02, glight=(0, 0, 0), glightI=0.0))
    return cam, draws


CHAPTERS = [(W_FORM, form), (W_TUN, tunnel), (W_LIGHT, light), (W_BLOCK, block), (W_END, end)]


def camdust_k(t):
    """Volumetric dust: absent in the first darkness, thinner in space, gone before the last particle."""
    k = 0.9 * ss(B["think"], B["people"] + 3.0, t) * (1 - ss(B["q1"], B["go"] + 1.0, t))
    k *= 1 - 0.5 * env(t, W_LIGHT[0] + 1, W_LIGHT[1] - 1, fin=1.5, fout=1.5)
    return k


def post(t):
    flash = 0.18 * np.exp(-((t - B["c_flow"] - 0.5) / 0.3) ** 2)
    fade = ss(0.0, 0.3, t) * (1 - ss(DURATION - 2.0, DURATION - 0.3, t))
    return dict(flash=float(flash), fade=float(fade))


# ── renderer ────────────────────────────────────────────────────────────────
def lin(hx):
    h = hx.lstrip("#")
    return tuple(float((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


SETS = ["dust", "title", "question", "scene", "tunnel", "cosmos", "block", "camdust"]


class Renderer:
    def __init__(self, W, H):
        self.W, self.H = W, H
        import os
        kw = {"backend": os.environ["DTP_GL_BACKEND"]} if os.environ.get("DTP_GL_BACKEND") else {}
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
        if key not in self.vao or d.get("fade", 1.0) <= 0.0:
            return
        self._camera(prog, cam, t)
        z4 = (0.0, 0.0, 0.0, 0.0)
        u = dict(u_mode=int(d.get("mode", 0)), u_form=float(d.get("form", 1.0)), u_scat=float(d.get("scat", 10.0)),
                 u_scatO=tuple(map(float, d.get("scatO", cam["pos"]))), u_gain=float(d.get("gain", 1.0)),
                 u_area=float(d.get("area", 0.0)), u_cap=float(d.get("cap", 0.3)),
                 u_base=max(1.0, 1.5 * self.k), u_fog=float(d.get("fog", 0.03)),
                 u_fogNear=float(d.get("fogNear", 0.4)), u_fade=float(d.get("fade", 1.0)),
                 u_world=float(d.get("world", 0.0)),
                 u_glight=tuple(map(float, d.get("glight", (0, 0, 0)))), u_glightI=float(d.get("glightI", 0.0)))
        if not lines and u["u_area"] == 0.0 and u["u_world"] == 0.0:
            # constant-energy sprites: keep image energy density equal to the 480p look at any resolution
            S = max(1.0, 1.5 * self.k)
            u["u_cap"] *= (1.0 / (480 / 1080) ** 2) / (S * S / self.k ** 2) if self.H > 480 else 1.0
        for i in range(5):
            u[f"u_P{i}"] = tuple(map(float, d.get(f"P{i}", (-1, 0, 0, 0) if i == 3 else z4)))
        for n, v in u.items():
            setu(prog, n, v)
        if d["set"] == "one":
            setu(prog, "u_cam", tuple(cam["pos"] - cam["fwd"] * 6.0 - cam["up"] * 0.1))
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
            self._draw(dict(set="camdust", mode=9, gain=1.0, cap=0.2, world=0.006, fog=0.0, fogNear=0.15,
                            P0=(9.0, 0, 0, 0), fade=post(t)["fade"] * camdust_k(t)), best, t)
        ctx.disable(moderngl.BLEND)
        s = self.acc[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(*self.down, fbo, s, u_texel=(1 / s.width, 1 / s.height), u_thresh=0.55 if i == 0 else 0.0)
            s = tex
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
        for k, v in dict(u_bloom=0.45, u_haze=1.6, u_hazeCol=(0.75, 1.0, 0.85), u_exposure=1.0, u_vig=0.5,
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
    """'notice', 'notice+0.5', '12.3'."""
    for op in ("+", "-"):
        if op in x[1:]:
            a, b = x.rsplit(op, 1)
            if a in B:
                return B[a] + (float(b) if op == "+" else -float(b))
    return B[x] if x in B else float(x)


DEFAULT_AT = ["think+1", "light+1", "people+2.5", "real", "gone+1", "q+2.5", "instant+1", "arrives+1", "past",
              "where+2", "pieces+2", "differently", "blur+1", "records+1", "eight+0.3", "andromeda+2.5", "back+1.5",
              "einstein", "whatis+1.5", "another+1", "together+1", "wrote+1", "present+2", "written+1", "feel+1",
              "scattered+1", "q2+1.5", "go+4.4"]


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
        print(f"  {x:>14s}  t={t:6.2f}s  {time.time() - t0:.2f}s/frame", flush=True)
    if len(ims) > 1:
        from PIL import Image, ImageDraw
        cols = a.cols or (2 if len(ims) <= 4 else 3)
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
    name = f"does_the_past_exist_{h}p{a.fps}" + (a.tag or "")
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
    s.add_argument("--at", nargs="+", default=DEFAULT_AT)
    s.add_argument("--height", type=int, default=360)
    s.add_argument("--cols", type=int, default=0)
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
