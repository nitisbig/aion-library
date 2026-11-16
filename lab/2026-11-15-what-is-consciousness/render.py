"""'What Is Consciousness?': a point-cloud journey, synced to the narration. moderngl headless on the Radeon R4.

    uv run python lab/2026-11-15-what-is-consciousness/render.py still --height 360                 # contact sheet
    uv run python lab/2026-11-15-what-is-consciousness/render.py still --at notice cells+2 sky --height 540
    uv run python lab/2026-11-15-what-is-consciousness/render.py video --height 480 --fps 24 --preset veryfast
    uv run python lab/2026-11-15-what-is-consciousness/render.py video --height 1080 --fps 30                # final

Every frame is a pure function of absolute audio time t. All times come from beats.py (word cues).
Chapters (each its own world + camera; neighbours crossfade by dissolving / condensing):
  DARK    darkness; isolated particles awaken; a third gather into stars; a slow green wave on 'notice'
  MATTER  one neuron grows its dendrites; the network appears, axons reach out, pulses race, synapses puff;
          pull back until the network is a field of stars
  BRAIN   the storm condenses into a folded cortex; activity flickers; regions light on sky / sea / voice
  TUNNEL  the camera dives inside: a tunnel of perception; light streaks in as signals; waves of colour; a face
  MEMORY  fragments of landscape: flat photographs that inflate, then dissolve and rebuild a little differently;
          thought-rings rise and fade
  GAP     the map: a lattice traced by pathways and spikes, with an empty chamber at its heart; layers shift;
          one small light on 'experience', then everything dims
  FLUX    one cloud: woven knot → galaxy → formless → brain → dissolve → face; matter streams through, the face stays
  END     the face becomes a flow, the flow a cosmos; the question forms in particles; one particle; dark
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


def orbit(ang, rad, h, tgt=(0, 0, 0)):
    tgt = np.asarray(tgt, float)
    return tgt + np.array([rad * np.sin(ang), h, rad * np.cos(ang)])


def integrate(fn, t0, t1, n=6000):
    tg = np.linspace(t0, t1, n)
    v = np.array([fn(x) for x in tg])
    cum = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(tg))])
    return lambda t: float(np.interp(t, tg, cum))


# ── chapter windows ─────────────────────────────────────────────────────────
W_DARK = (0.0, B["c_matter"] + 2.2)
W_MATTER = (B["c_matter"] - 1.2, B["c_brain"] + 2.0)
W_BRAIN = (B["c_brain"] - 0.6, B["c_tunnel"] + 1.6)
W_TUNNEL = (B["c_tunnel"] - 0.6, B["c_memory"] + 1.4)
W_MEMORY = (B["c_memory"] - 0.6, B["c_gap"] + 1.6)
W_GAP = (B["c_gap"] - 0.6, B["c_flux"] + 1.6)
W_FLUX = (B["c_flux"] - 0.8, B["process"] + 3.5)
W_END = (B["c_end"] + 1.0, DURATION + 1)


def condense(t, w, fin=2.8, fout=2.0):
    """1 = formed. Condenses from dust at the window start, dissolves at its end."""
    return ss(w[0], w[0] + fin, t) * (1 - ss(w[1] - fout, w[1], t))


# ── DARK ────────────────────────────────────────────────────────────────────
def cam_dark(t):
    p = np.array([0.25 * np.sin(0.06 * t), 0.08 * np.sin(0.09 * t), -0.1 * t])
    tg = p + np.array([0.6 * np.sin(0.04 * t + 0.4), 0.15 * np.sin(0.05 * t), -10])
    return look(p, tg, roll=0.03 * np.sin(0.07 * t))


_ct = cam_dark(B["inside"] + 2.5)
TITLE_POS = _ct["pos"] + _ct["fwd"] * 9.0


def dark(t):
    cam = cam_dark(t)
    reveal = 0.05 * ss(0.6, B["inside"] + 1.0, t) + 0.95 * ss(B["billions"] - 1.0, B["stars"] + 1.5, t) ** 0.9
    gather = ss(B["dust"] - 0.3, B["stars"] + 3.0, t)
    nk = ss(B["notice"] - 0.6, B["notice"] + 0.8, t)
    wave = max(t - B["notice"] + 0.3, 0.0) * 7.0
    w = env(t, *W_DARK, fin=0.01, fout=2.0)
    form = 1 - ss(B["c_matter"] - 0.2, W_DARK[1], t)
    ctr = cam["pos"] + cam["fwd"] * 9.0
    draws = [dict(set="dust", mode=0, gain=1.0, cap=0.9, world=0.011, fade=w, form=form, scat=30.0,
                  scatO=cam["pos"] + cam["fwd"] * 6, fog=0.018, fogNear=0.3,
                  P0=(reveal, gather, wave, 0), P1=(*ctr, 1.3 * nk), P3=(-1, 0, 0, 0),
                  glight=tuple(ctr), glightI=0.45 * nk)]
    tw = env(t, B["inside"] - 0.4, B["dark1"] + 2.4, fin=0.1, fout=1.8)
    if tw > 0:
        tf = ss(B["inside"] - 0.4, B["inside"] + 1.6, t) * (1 - ss(B["dark1"] - 0.4, B["dark1"] + 2.2, t))
        draws.append(dict(set="title", mode=1, gain=1.0, cap=0.035, fade=tw, form=1.0, scat=9.0,
                          scatO=tuple(TITLE_POS), fog=0.0, fogNear=0.2, P0=(tf, tf, 0, 0), P1=(*TITLE_POS, 1.0),
                          glight=tuple(TITLE_POS), glightI=0.2 * tf))
    return cam, draws


# ── MATTER ──────────────────────────────────────────────────────────────────
def matter_rad(t):
    r = 4.2
    r = mix(r, 30.0, ss(B["neurons"] - 0.5, B["reaching"] + 2.5, t))
    r = mix(r, 13.0, ss(B["chem"] - 1.0, B["chem"] + 2.5, t))
    r = mix(r, 75.0, ss(B["physics"] - 0.3, B["forged"] + 2.5, t))
    return float(r)


def cam_matter(t):
    t0 = W_MATTER[0]
    ang = 0.25 + 0.035 * (t - t0) + 0.6 * ss(B["neurons"], B["reaching"] + 3, t)
    r = matter_rad(t)
    h = 0.15 * r + 0.3
    tgt = mix([0, 0, 0], [2.0, 0.5, -1.0], ss(B["chem"] - 1.0, B["chem"] + 2.5, t))
    tgt = mix(tgt, [0, 0, 0], ss(B["physics"], B["forged"], t))
    return look(orbit(ang, r, h, tgt), tgt, roll=0.04 * np.sin(0.2 * t))


def matter(t):
    cam = cam_matter(t)
    soma = 0.0008 + 1.05 * ss(B["neurons"] - 0.3, B["neurons"] + 3.5, t) ** 1.3
    dend = ss(B["look"] - 1.0, B["cells"] + 1.0, t)
    dend = max(dend, ss(B["neurons"], B["reaching"] + 1.0, t)) if t > B["neurons"] else dend
    axon = ss(B["reaching"] - 0.3, B["reaching"] + 2.6, t)
    pulses = ss(B["pulses"] - 0.4, B["pulses"] + 0.8, t)
    chem = ss(B["chem"] - 0.3, B["chem"] + 1.0, t)
    tw = ss(B["forged"] - 0.4, B["forged"] + 1.2, t)
    w = env(t, *W_MATTER, fin=0.5, fout=1.6)
    form = condense(t, W_MATTER, fin=2.6, fout=2.4)
    common = dict(mode=2, fade=w, form=form, scat=8.0, scatO=(0, 0, 0), fog=0.012, fogNear=0.3,
                  P0=(soma, dend, axon, 0), P1=(pulses, chem, tw, 0), glight=(0, 0, 0),
                  glightI=0.12 * (1 - ss(B["neurons"], B["reaching"], t)))
    return cam, [dict(set="neurons", gain=1.0, area=0.0006, cap=0.5, **common),
                 dict(set="neurons", lines=True, gain=1.0, cap=0.035 + 0.09 * (1 - ss(B["neurons"], B["reaching"], t)), **common)]


# ── BRAIN ───────────────────────────────────────────────────────────────────
REG_SKY = (0.0, 1.8, -6.8)
REG_SEA = (5.0, -0.6, 1.8)
REG_VOICE = (4.4, -2.4, -0.6)


def cam_brain(t):
    t0 = W_BRAIN[0]
    ang = 1.35 + 0.07 * (t - t0)
    r = mix(27.0, 21.0, ss(B["pounds"] - 1.0, B["pounds"] + 3.0, t))
    dive = ss(B["voice"] + 1.2, B["c_tunnel"] + 1.4, t)
    r = mix(r, 2.5, dive ** 1.6)
    h = mix(5.0, 2.5, ss(B["pounds"] - 1.0, B["voice"], t)) * (1 - dive)
    return look(orbit(ang, r, h), (0, 0.3, 0), roll=0.03 * np.sin(0.15 * t))


def brain(t):
    cam = cam_brain(t)
    storm = ss(B["storm"] - 0.6, B["appears"] + 0.5, t)
    wave = -11 + ((t - B["storm"]) * 7.0) % 26.0
    sky = 1.6 * env(t, B["sky"] - 0.2, B["voice"] + 1.5, fin=0.8, fout=1.2)
    sea = 1.6 * env(t, B["sea"] - 0.2, B["voice"] + 1.5, fin=0.8, fout=1.2)
    voice = 2.0 * env(t, B["voice"] - 0.2, W_BRAIN[1], fin=0.8, fout=1.8)
    w = env(t, *W_BRAIN, fin=0.5, fout=2.6)
    form = ss(W_BRAIN[0], B["andyet"] + 2.4, t) * (1 - 0.9 * ss(B["c_tunnel"] - 1.6, W_BRAIN[1], t))
    common = dict(mode=3, fade=w, form=form, scat=14.0, scatO=cam["pos"], fog=0.02, fogNear=3.0,
                  P0=(storm, wave, 0.0, 0), P1=(*REG_SKY, sky), P2=(*REG_SEA, sea), P3=(*REG_VOICE, voice),
                  glight=(0, 0, 0), glightI=0.15 * storm)
    return cam, [dict(set="brain", gain=1.0, area=0.0002, cap=0.55, **common),
                 dict(set="brain", lines=True, gain=1.0, cap=0.02, **common)]


# ── TUNNEL ──────────────────────────────────────────────────────────────────
def tunnel_speed(t):
    v = 2.6
    v -= 1.3 * ss(B["model"] - 0.5, B["darkness"] + 0.5, t)
    v += 2.6 * ss(B["light"] - 0.4, B["light"] + 0.8, t)
    v -= 3.4 * ss(B["face"] - 1.4, B["face"] + 1.2, t)
    return max(v, 0.25)


_S_T = integrate(tunnel_speed, W_TUNNEL[0], W_TUNNEL[1] + 1)


def s_tun(t):
    return -6.0 + _S_T(t)


S_FACE = s_tun(B["c_memory"]) + 4.4


def cam_tunnel(t):
    s = s_tun(t)
    p = np.array([G.tcx(s) + 0.1 * np.sin(0.4 * t), G.tcy(s) - 0.2 + 0.05 * np.sin(1.1 * t), -s])
    s2 = s + 7
    tg = np.array([G.tcx(s2), G.tcy(s2) - 0.1, -s2])
    k = ss(B["face"] - 1.0, B["face"] + 1.2, t)
    tg = mix(tg, [G.tcx(S_FACE), G.tcy(S_FACE), -S_FACE], k)
    return look(p, tg, roll=0.06 * np.sin(0.3 * t))


def tunnel(t):
    cam = cam_tunnel(t)
    s = s_tun(t)
    streak = env(t, B["light"] - 0.3, B["face"] + 1.0, fin=0.6, fout=1.4)
    colour = env(t, B["sigcol"] - 0.3, B["c_memory"] + 0.5, fin=0.6, fout=1.8)
    fog = 0.12 - 0.025 * ss(B["depth"] - 0.4, B["depth"] + 1.0, t)
    dim = 1.0 - 0.45 * env(t, B["darkness"] - 0.3, B["light"] + 0.3, fin=0.8, fout=0.8)
    dim *= 1.0 - 0.55 * ss(B["face"] - 0.6, B["face"] + 1.0, t)
    w = env(t, *W_TUNNEL, fin=2.2, fout=1.4) * dim
    form = condense(t, W_TUNNEL, fin=2.2, fout=1.8)
    common = dict(mode=4, fade=w, form=form, scat=16.0, scatO=cam["pos"], fog=fog, fogNear=0.8,
                  P0=(s, streak, colour, 0), glight=tuple(cam["pos"] + cam["fwd"] * 2), glightI=0.25 + 0.35 * colour)
    draws = [dict(set="tunnel", gain=1.0, area=0.0032, cap=1.0, **common),
             dict(set="tunnel", lines=True, gain=1.0, cap=0.07, **common)]
    fw = env(t, B["face"] - 0.5, W_TUNNEL[1], fin=0.3, fout=1.6)
    if fw > 0:
        ff = ss(B["face"] - 0.5, B["face"] + 1.3, t) * (1 - ss(B["c_memory"] - 0.2, W_TUNNEL[1], t))
        fp = (G.tcx(S_FACE), G.tcy(S_FACE) - 0.05, -S_FACE)
        draws.append(dict(set="face", mode=5, gain=1.0, area=0.000015, cap=0.4, fade=fw, form=ff, scat=5.0, scatO=fp,
                          fog=0.02, fogNear=0.3, P0=(*fp, 0.42), P1=(0.6, 0, 0, 0), glight=fp, glightI=0.0))
    return cam, draws


# ── MEMORY ──────────────────────────────────────────────────────────────────
def mem_speed(t):
    return 3.4 - 1.2 * ss(B["remember"] - 0.5, B["rebuild"] + 0.5, t) + 0.8 * ss(B["thought"], B["fading"], t)


_S_M = integrate(mem_speed, W_MEMORY[0], W_MEMORY[1] + 1)


def cam_memory(t):
    z = 13.0 - _S_M(t)
    x = 1.0 * np.sin(0.18 * t)
    up = ss(B["thought"] - 0.5, B["fading"] + 1.5, t)
    p = np.array([x, 3.6 + 2.5 * up, z])
    tg = np.array([0.3 * np.sin(0.15 * t + 1), -0.8 + 2.0 * up, z - 12])
    return look(p, tg, roll=0.05 * np.sin(0.25 * t))


def memory(t):
    cam = cam_memory(t)
    flat = 1 - ss(B["photos"] + 0.2, B["remember"] + 0.6, t)
    frame = 1 - ss(B["photos"] - 0.2, B["photos"] + 1.4, t)
    clock = max(t - (B["rebuild"] - 0.7), -1.0) * 0.75
    amt = env(t, B["rebuild"] - 0.9, B["thought"] + 0.8, fin=0.4, fout=0.8)
    thoughts = env(t, B["thought"] - 0.4, W_MEMORY[1], fin=1.0, fout=1.6)
    w = env(t, *W_MEMORY, fin=0.5, fout=1.4)
    form = condense(t, W_MEMORY, fin=2.0, fout=1.8)
    common = dict(mode=6, fade=w, form=form, scat=12.0, scatO=cam["pos"], fog=0.03, fogNear=0.5,
                  P0=(flat, frame, clock, amt), P1=(thoughts, 0, 0, 0), glight=tuple(cam["pos"] + cam["fwd"] * 8),
                  glightI=0.4)
    return cam, [dict(set="islands", gain=1.0, area=0.0006, cap=0.6, **common),
                 dict(set="islands", lines=True, gain=1.0, cap=0.08, **common)]


# ── GAP ─────────────────────────────────────────────────────────────────────
def cam_gap(t):
    t0 = W_GAP[0]
    ang = 0.7 + 0.03 * (t - t0)
    far = orbit(ang, mix(78.0, 58.0, ss(t0, B["nowhere"], t)), mix(30.0, 20.0, ss(t0, B["nowhere"], t)))
    k = ss(B["nowhere"] - 0.6, B["blue"] + 0.4, t)
    inside = np.array([0.6 * np.sin(0.2 * t), 0.4, 5.6 + 0.3 * np.sin(0.15 * t)])
    p = mix(far, inside, k ** 0.75)
    tg = mix([0, 0, 0], [0.0, 0.0, -1.0], k)
    return look(p, tg, roll=0.03 * np.sin(0.18 * t) + 0.08 * ss(B["hard"], B["howdoes"], t) * np.sin(0.3 * t))


def gap(t):
    cam = cam_gap(t)
    paths = 0.03 * ss(B["trace"] - 0.3, B["trace"] + 0.4, t) + 0.98 * ss(B["map"] - 0.3, B["map"] + 2.2, t)
    spikes = env(t, B["spike"] - 0.3, B["indark"] + 1.0, fin=0.6, fout=1.5)
    twist = 1.4 * ss(B["hard"] - 0.3, B["howdoes"] + 1.5, t) * (1 - 0.6 * ss(B["why2"], B["indark"] + 1, t))
    slide = 0.9 * env(t, B["hard"], B["indark"] + 1.5, fin=2.0, fout=2.0)
    light = env(t, B["experience"] - 0.5, B["why2"] + 0.6, fin=0.9, fout=1.0)
    dim = ss(B["why2"] - 0.2, B["indark"] + 0.8, t) * 0.85
    w = env(t, *W_GAP, fin=0.5, fout=1.4)
    form = condense(t, W_GAP, fin=2.4, fout=1.8)
    common = dict(mode=7, fade=w, form=form, scat=14.0, scatO=(0, 0, 0), fog=0.012, fogNear=0.5,
                  P0=(twist, slide, 0, 0), P1=(paths, 0, spikes, light), P2=(dim, 0, 0, 0),
                  glight=(0, 0, 0), glightI=2.0 * light)
    return cam, [dict(set="lattice", gain=1.0, cap=0.22, **common),
                 dict(set="lattice", lines=True, gain=1.0, cap=0.08, **common)]


# ── FLUX ────────────────────────────────────────────────────────────────────
def flux_weights(t):
    knot = env(t, B["some"] - 0.6, B["others"] + 0.6, fin=2.0, fout=1.4)
    gal = env(t, B["others"] - 0.2, B["noone"] + 0.2, fin=1.8, fout=1.2)
    brain = env(t, B["forms"] - 0.35, B["dissolves"] + 0.2, fin=0.5, fout=0.45)
    face = ss(B["again"] - 0.3, B["again"] + 0.6, t)
    chaos = env(t, B["noone"] - 0.4, B["forms"] + 0.1, fin=0.8, fout=0.5)
    chaos = max(chaos, env(t, B["dissolves"] - 0.15, B["again"] + 0.35, fin=0.35, fout=0.4))
    chaos = max(chaos, 1.0 - knot - gal - brain - face, 0.0)
    return (knot, gal, chaos, brain), face


def cam_flux(t):
    t0 = W_FLUX[0]
    gal = ss(B["others"] - 0.5, B["property"] + 1.0, t) * (1 - ss(B["noone"], B["still"], t))
    end = ss(B["forms"] - 1.5, B["again"] + 1.0, t)
    ang = mix(-0.9 + 0.05 * (t - t0), 0.12 * np.sin(0.2 * t), end)
    r = 15.0 + 13.0 * gal
    r = mix(r, 14.5, end)
    r = mix(r, 11.0, ss(B["replaced"], B["remain"] + 1.5, t))
    h = 3.0 + 13.0 * gal
    h = mix(h, 0.6, end)
    return look(orbit(ang, r, h), (0, 0.2, 0), roll=0.03 * np.sin(0.2 * t))


def flux(t):
    cam = cam_flux(t)
    (kn, ga, ch, br), fa = flux_weights(t)
    stream = ss(B["replaced"] - 0.4, B["replaced"] + 1.4, t) + 1.2 * ss(B["process"] - 0.6, B["process"] + 2.0, t)
    spin = 0.05 * (t - W_FLUX[0]) * (1 - ss(B["forms"] - 1.5, B["forms"], t))
    swirl = env(t, B["still"] - 0.5, B["forms"] + 0.2, fin=1.0, fout=0.8)
    w = env(t, *W_FLUX, fin=0.5, fout=1.8)
    form = condense(t, W_FLUX, fin=2.2, fout=2.4)
    return cam, [dict(set="flux", mode=8, gain=1.0, area=0.0001, cap=0.5, fade=w, form=form, scat=10.0, scatO=(0, 0, 0),
                      fog=0.012, fogNear=0.5, P0=(kn, ga, ch, br), P1=(fa, stream, spin, swirl),
                      glight=(0, 0, 0), glightI=0.0)]


# ── END ─────────────────────────────────────────────────────────────────────
def end_flow_speed(t):
    return 0.9 * (1 - ss(B["askyou"], B["q1"], t)) + 0.05


_FLOW = integrate(end_flow_speed, W_END[0], DURATION + 1)


def cam_end(t):
    k = t - W_END[0]
    back = ss(B["running"] - 1.0, B["askyou"] + 1.0, t)
    p = np.array([0.6 * np.sin(0.05 * k), 0.4 + 0.2 * np.sin(0.04 * k), 4.0 + 0.25 * k + 14.0 * back])
    return look(p, p + np.array([0.0, -0.04, -1.0]), roll=0.02 * np.sin(0.1 * k))


Q_POS = None


def end(t):
    global Q_POS
    cam = cam_end(t)
    if Q_POS is None:
        c = cam_end(B["q1"])
        Q_POS = c["pos"] + c["fwd"] * 7.0
    ext = mix(-0.1, 1.06, ss(B["askyou"] + 0.5, B["itself"] + 1.8, t))
    gather = ss(B["running"] - 0.5, B["askyou"] + 1.0, t)
    w = env(t, *W_END, fin=1.6, fout=0.01)
    draws = [dict(set="dust", mode=0, gain=1.0, cap=0.75, world=0.008, fade=w, form=ss(W_END[0], W_END[0] + 3.5, t),
                  scat=18.0, scatO=cam["pos"], fog=0.016, fogNear=0.3, P0=(2.0, gather, 0, 0),
                  P3=(ext, 0, _FLOW(t), 0), P1=(0, 0, -1000, 0), glight=(0, 0, 0), glightI=0.0)]
    qw = env(t, B["q1"] - 0.6, B["itself"] + 3.0, fin=0.3, fout=1.6)
    if qw > 0:
        l1 = ss(B["q1"] - 0.4, B["q1"] + 1.4, t)
        l2 = ss(B["q2"] - 0.4, B["q2"] + 1.4, t)
        out = 1 - ss(B["itself"] + 0.8, B["itself"] + 3.0, t)
        draws.append(dict(set="question", mode=1, gain=1.0, cap=0.035, fade=qw, form=out, scat=6.0,
                          scatO=tuple(Q_POS), fog=0.0, fogNear=0.2, P0=(l1, l2, 0, 0), P1=(*Q_POS, 1.0),
                          glight=tuple(Q_POS), glightI=0.15))
    one = env(t, B["itself"] + 0.5, DURATION + 1, fin=1.2, fout=0.01)
    if one > 0:
        pulse = 1.0 + 1.6 * np.exp(-((t - B["itself"] - 2.6) / 0.45) ** 2)
        draws.append(dict(set="one", mode=10, gain=pulse, cap=1.0, fade=one * (1 - ss(DURATION - 2.4, DURATION - 0.6, t)),
                          fog=0.0, fogNear=0.3, world=0.02, glight=(0, 0, 0), glightI=0.0))
    return cam, draws


CHAPTERS = [(W_DARK, dark), (W_MATTER, matter), (W_BRAIN, brain), (W_TUNNEL, tunnel), (W_MEMORY, memory),
            (W_GAP, gap), (W_FLUX, flux), (W_END, end)]


def camdust_k(t):
    """Volumetric dust: absent in the first darkness and in the empty chamber, gone before the last particle."""
    k = 0.9 * ss(6.0, 16.0, t) * (1 - ss(B["askyou"], B["q1"] + 1.0, t))
    k *= 1 - 0.8 * env(t, B["nowhere"], B["c_flux"], fin=1.5, fout=1.5)
    return k


def post(t):
    flash = 0.3 * np.exp(-((t - B["c_tunnel"] - 0.2) / 0.25) ** 2) + 0.12 * np.exp(-((t - B["again"] - 0.1) / 0.2) ** 2)
    fade = ss(0.0, 0.3, t) * (1 - ss(DURATION - 2.2, DURATION - 0.3, t))
    return dict(flash=float(flash), fade=float(fade))


# ── renderer ────────────────────────────────────────────────────────────────
def lin(hx):
    h = hx.lstrip("#")
    return tuple(float((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


SETS = ["dust", "title", "question", "neurons", "brain", "tunnel", "face", "islands", "lattice", "flux", "camdust"]


class Renderer:
    def __init__(self, W, H):
        self.W, self.H = W, H
        import os
        kw = {"backend": os.environ["WIC_GL_BACKEND"]} if os.environ.get("WIC_GL_BACKEND") else {}
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


DEFAULT_AT = ["inside+1.5", "stars+2", "notice+1", "cells", "reaching+2", "pulses+2", "chem+1.5", "forged+2",
              "appears+1", "sky+0.8", "voice+0.8", "skull", "sigcol+1", "face+1.5", "photos-0.5", "rebuild+1",
              "rising", "map+2", "blue", "experience+0.5", "woven+1", "property+1", "forms+0.4", "remain",
              "running+1", "q2+1.5", "itself+3"]


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
    name = f"what_is_consciousness_{h}p{a.fps}" + (a.tag or "")
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
