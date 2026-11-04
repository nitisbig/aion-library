"""Timeline: every per-frame value (camera, neurons, edge pulses, ink, recognition glyphs) as a function of t.

All brightness comes from the trained MNIST network (network.py):
  edge base  ∝ |w| / s_l          (s_l = 98th percentile of displayed |w| in layer l)
  edge hue   = sign(w)
  pulse      ∝ |w · a_src| / r_l  (r_l = 99.5th percentile of |w·a| over the ten countdown passes)
  neuron     = activation / ref_l (hidden), pixel value (input), softmax p (output)
  glyph      = argmax of the output; the digit really is what the network answered
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

import layout as LY
import network as N

DURATION = 30.0
NL = LY.NL


# ── easing ───────────────────────────────────────────────────────────────────
def c01(x): return np.clip(x, 0.0, 1.0)
def smooth(x): x = c01(x); return x * x * (3 - 2 * x)
def smoother(x): x = c01(x); return x ** 3 * (x * (6 * x - 15) + 10)
def expo_out(x): x = c01(x); return np.where(x >= 1, 1.0, 1 - 2.0 ** (-10 * x))
def back_out(x, k=1.9):
    x = c01(x) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2
def bump(x, w): return np.exp(-(x / w) ** 2)


# ── network data ─────────────────────────────────────────────────────────────
NET = N.load()
WS_, BS_ = N.weights(NET)
POS, LAYER, IDX, SL = LY.nodes()
SRC, DST, EL, IA, IB, CTRL = LY.edges(NET)
NE, NN = len(SRC), len(POS)
_rng = np.random.default_rng(11)
EH, NH = _rng.random(NE), _rng.random(NN)
W_E = np.concatenate([WS_[l][IA[EL == l], IB[EL == l]] for l in range(NL - 1)])
WSCALE = np.array([np.percentile(np.abs(W_E[EL == l]), 98) for l in range(NL - 1)])[EL]

# ── countdown schedule ───────────────────────────────────────────────────────
#            digit   t0    D (seconds per layer)
_SCHED = [(9, 6.0, 0.30), (8, 8.4, 0.29), (7, 10.6, 0.27), (6, 12.6, 0.24), (5, 14.3, 0.23),
          (4, 15.9, 0.21), (3, 17.4, 0.21), (2, 18.8, 0.20), (1, 20.1, 0.20), (0, 22.0, 0.29)]
LAST_HOLD = 27.2
PASSES = []
for k, (dig, t0, D) in enumerate(_SCHED):
    img28 = NET["digits28"][k]
    assert NET["digit_labels"][k] == dig
    A = [a[0] for a in N.forward(WS_, BS_, N.pool(img28[None]))]
    c = np.concatenate([A[l][IA[EL == l]] * W_E[EL == l] for l in range(NL - 1)])
    travel = 0.72 * D
    nxt = _SCHED[k + 1][1] if k + 1 < len(_SCHED) else None
    PASSES.append(dict(digit=dig, t0=t0, D=D, travel=travel, A=A, c=c, img=img28,
                       answer=int(A[-1].argmax()),
                       arrive=[t0 + 0.25 + (l - 1) * D + travel + 0.05 for l in range(NL)],
                       hold=(nxt + 0.9) if nxt else LAST_HOLD,
                       in_off=(nxt - 0.5) if nxt else LAST_HOLD))
    assert PASSES[-1]["answer"] == dig
for p, q in zip(PASSES, PASSES[1:] + [None]):
    p["next_arr"] = q["arrive"][-1] if q else LAST_HOLD + 0.4
    p["next_t0"] = q["t0"] if q else None
C_REF = np.array([np.percentile(np.abs(np.concatenate([p["c"][EL == l] for p in PASSES])), 99.5)
                  for l in range(NL - 1)])
A_REF = [1.0] + [0.8 * max(p["A"][l].max() for p in PASSES) for l in range(1, NL - 1)] + [1.0]


# ── build: seed → input grid → layers grow ───────────────────────────────────
EDGE_BUILD = [1.9, 2.35, 2.8, 3.25, 3.7, 4.15, 4.6]
_IN_CENTER = POS[SL[0]].mean(0)
_IN_R = np.linalg.norm(POS[SL[0]] - _IN_CENTER, axis=1)
_NODE_T = np.zeros(NN)
_NODE_T[SL[0]] = 0.95 + 0.75 * _IN_R / _IN_R.max() + 0.08 * NH[SL[0]]
for l in range(1, NL):
    n = N.SIZES[l]
    _NODE_T[SL[l]] = EDGE_BUILD[l - 1] + 0.6 + 0.4 * IDX[SL[l]] / max(n - 1, 1) + 0.08 * NH[SL[l]]
NODE_COL = LY.node_colors(LAYER, IDX)
_EDGE_T = _NODE_T[DST] - 0.6 - 0.2 * EH


# ── ink: each handwritten digit flies onto the input grid as glowing particles ─
N_INK = 1500


def _ink(img, seed):
    rng = np.random.default_rng(seed)
    w = img.ravel() ** 1.5
    cells = rng.choice(784, N_INK, p=w / w.sum())
    r, cc = np.divmod(cells, 28)
    u = (r + rng.random(N_INK)) / 2.0          # continuous 14-grid coords
    v = (cc + rng.random(N_INK)) / 2.0
    tgt = LY.input_point(u - 0.5, v - 0.5, front=0.1)
    start = (tgt + (2.0 + 2.5 * rng.random(N_INK))[:, None] * LY.IN_N
             + rng.normal(0, 1.4, N_INK)[:, None] * np.array([0, 1.0, 0]) + rng.normal(0, 1.4, N_INK)[:, None] * LY.IN_H)
    delay = 0.5 * u / 14.0 + 0.15 * rng.random(N_INK)       # written top to bottom
    b = img[r, cc] * rng.uniform(0.6, 1.0, N_INK)
    return tgt, start, delay, b, rng.uniform(0.7, 1.3, N_INK)


for k, p in enumerate(PASSES):
    p["ink"] = _ink(p["img"], 100 + k)


def ink(t):
    """Ink particle sprites: (n, 7) rows of pos3, size, bright, kind=0, param."""
    out = []
    for p in PASSES:
        t0 = p["t0"]
        if t < t0 - 1.0 or t > p["in_off"] + 0.7:
            continue
        tgt, start, delay, b, sz = p["ink"]
        u = expo_out((t - (t0 - 0.95) - delay) / 0.55)
        pos = start + (tgt - start) * u[:, None]
        land = c01((t - (t0 - 0.95) - delay) / 0.55)
        bright = 0.55 * b * smooth(land * 3) * (1.0 + 0.9 * bump(t - t0 - 0.05, 0.25))
        bright *= 0.35 + 0.65 * (1 - smooth((t - t0 - 0.3) / 0.6))        # settle to a soft residue
        gone = smooth((t - p["in_off"]) / 0.5)
        pos = pos + np.array([1.2, 0, 0]) * gone                          # drawn into the network
        bright = bright * (1 - gone)
        size = 0.024 * sz * (1 + 0.6 * (1 - u))
        out.append(np.column_stack([pos, size, bright, np.zeros(N_INK), np.zeros(N_INK), np.zeros((N_INK, 3))]))
    return np.vstack(out) if out else np.zeros((0, 10))


def glyphs(t):
    """Recognition: the winning output flares, a shockwave ring expands and the clean digit emerges.
    Rows: pos3, size, bright, kind (1 = glyph, 2 = ring), param (glyph index / ring thickness), colour3."""
    rows = []
    for k, p in enumerate(PASSES):
        ta = p["arrive"][-1]
        if t < ta - 0.05:
            continue
        node = POS[SL[-1]][p["answer"]]
        final = k == len(PASSES) - 1
        fade = 1 - smooth((t - p["next_arr"] + 0.05) / 0.28)
        if final:
            fade = 1.0
        if fade <= 0:
            continue
        g = back_out((t - ta) / 0.5)
        col = LY.lin(LY.OUT_COLS[p["answer"]])
        size = (1.5 if final else 1.15) * (0.6 + 0.4 * g) * (1 - 0.2 * (1 - fade))
        bright = (1.0 + 1.2 * bump(t - ta - 0.1, 0.2)) * fade * smooth((t - ta) / 0.12)
        rise = -0.35 * (1 - expo_out((t - ta) / 0.45)) + 0.45 * smooth(1 - fade)     # odometer roll
        gp = node + np.array([0.85 + (0.2 if final else 0.0), rise, 0.0])
        rows.append([*gp, size, bright, 1.0, float(p["answer"]), *col])
        q = c01((t - ta) / 0.6)
        if 0 < q < 1:                                   # one thin crisp ring
            rows.append([*node, 0.08 + 0.42 * expo_out(q) * (1.3 if final else 1.0),
                         (1 - q) ** 1.5 * 1.1, 2.0, 0.03, *col])
    return np.array(rows, "f4").reshape(-1, 10)


# ── camera ───────────────────────────────────────────────────────────────────
#        t      tx    ty    tz   yaw  pitch dist  roll  fov
_CAM = np.array([
    # few, slow moves; targets/distances solved so the whole network sits centred with a 5 % safe
    # margin in every frame (see framing_report)
    [0.0, -6.30, 0.00, 0.00, 55.0, 2.0, 4.20, 0.0, 40.0],
    [2.0, -6.30, 0.00, 0.00, 55.0, 3.0, 5.20, 0.0, 40.0],
    [5.2, -2.24, -0.69, -1.86, 48.0, 10.0, 11.23, 0.0, 40.0],
    [13.0, -2.03, -0.65, -1.20, 56.0, 12.0, 12.52, 0.0, 40.0],
    [21.0, -1.90, -0.53, -0.89, 62.0, 11.0, 12.93, 0.0, 40.0],
    [24.5, -1.75, -0.52, -1.30, 60.0, 9.0, 13.11, 0.0, 40.0],
    [30.0, -1.96, -0.64, -1.19, 58.0, 12.0, 14.50, 0.0, 40.0],
])
_cam = PchipInterpolator(_CAM[:, 0], _CAM[:, 1:], axis=0)


def camera(t):
    tx, ty, tz, yaw, pitch, dist, roll, fov = _cam(np.clip(t, 0, DURATION))
    y, p = np.radians(yaw), np.radians(pitch)
    target = np.array([tx, ty, tz])
    pos = target + dist * np.array([-np.cos(p) * np.cos(y), np.sin(p), np.cos(p) * np.sin(y)])
    fwd = (target - pos) / dist
    right = np.cross(fwd, [0.0, 1.0, 0.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    r = np.radians(roll)
    right, up = np.cos(r) * right + np.sin(r) * up, -np.sin(r) * right + np.cos(r) * up
    return pos, right, up, fwd, np.radians(fov), dist


# ── per-frame state ──────────────────────────────────────────────────────────
def state(t):
    S = {}
    S["seed"] = 2.2 * smooth((t - 0.25) / 0.7) * (1 - smooth((t - 1.05) / 0.5))
    u = expo_out((t - _NODE_T) / 1.1)
    pos = POS.copy()
    pos[SL[0]] = _IN_CENTER + (POS[SL[0]] - _IN_CENTER) * u[SL[0], None]
    scale = np.where(LAYER == 0, smooth((t - _NODE_T) / 0.35), back_out((t - _NODE_T) / 0.55))
    scale = scale * (1 + 0.04 * np.sin(2 * np.pi * (0.45 * t + NH)))         # breathing
    reveal = smooth((t - _NODE_T) / 0.35)
    act = 0.7 * bump(t - _NODE_T - 0.15, 0.22) * (t > _NODE_T - 0.6)
    e_reveal = smoother((t - _EDGE_T) / 0.6)

    e_phase = np.full(NE, -1.0); e_amp = np.zeros(NE); e_glow = np.zeros(NE)
    best = np.zeros(NE)
    for p in PASSES:
        if t < p["t0"] - 1.0:
            continue
        env = 1 - smooth((t - p["hold"]) / 0.6)
        if env <= 0:
            continue
        start = p["t0"] + 0.25 + EL * p["D"] + 0.08 * EH
        ph = (t - start) / p["travel"]
        amp = np.minimum(np.abs(p["c"]) / C_REF[EL], 1.5) * env
        vis = (ph > 0) & (ph < 3.0)
        glow = amp * 0.45 * smooth((ph - 0.7) / 0.6)
        imp = amp * vis + glow
        take = imp > best
        e_phase = np.where(take & vis, ph, np.where(take, -1.0, e_phase))
        e_amp = np.where(take, amp, e_amp)
        best = np.maximum(best, imp)
        e_glow = np.maximum(e_glow, glow)
        A = p["A"]
        ienv = 1 - smooth((t - p["in_off"]) / 0.4)
        act[SL[0]] = np.maximum(act[SL[0]], A[0] * smooth((t - p["t0"] + 0.2) / 0.35) * ienv)
        for l in range(1, NL):
            arr = p["arrive"][l]
            a = A[l] / A_REF[l]
            boost = 0.7 if l == NL - 1 else 0.45
            v = a * (smooth((t - arr) / 0.18) + boost * bump(t - arr - 0.12, 0.14)) * env
            act[SL[l]] = np.maximum(act[SL[l]], v)

    idle = smooth((t - 27.2) / 1.0)
    act = act + idle * 0.10 * (0.5 + 0.5 * np.sin(2 * np.pi * (0.6 * t + NH))) * reveal

    z = np.zeros(NE)
    S.update(col=NODE_COL, pos=pos, scale=scale, reveal=reveal, act=act, grad=np.zeros(NN),
             e_reveal=e_reveal, w=W_E / WSCALE, e_phase=e_phase, e_amp=e_amp, e_glow=e_glow,
             e_back=np.full(NE, -1.0), e_gamp=z, e_gglow=z,
             fade=1 - smooth((t - 28.4) / 1.6), dust=smooth(t / 2.5),
             sprites=np.vstack([ink(t), glyphs(t)]))
    return S


def framing_report(fps=30, margin=0.9):
    """Project every visible neuron and glyph each frame; return frames where anything leaves the safe area
    (|ndc| > margin, i.e. a 5 % margin on each side). The opening close-up on the input is checked too."""
    bad = []
    for i in range(int(DURATION * fps) + 1):
        t = i / fps
        pos, right, up, fwd, fov, _ = camera(t)
        S = state(t)
        th = np.tan(fov / 2); asp = 16 / 9
        pts = S["pos"][(S["reveal"] > 0.05) & (S["scale"] > 0.05)]
        g = S["sprites"]
        g = g[(g[:, 5] == 1) & (g[:, 4] > 0.05)]
        rel = np.vstack([pts, g[:, :3]]) - pos
        ext = np.concatenate([np.zeros(len(pts)), g[:, 3] * 0.45])
        z = rel @ fwd
        x = np.abs(rel @ right) + ext; y = np.abs(rel @ up) + ext
        m = max((x / (z * th * asp)).max(initial=0), (y / (z * th)).max(initial=0))
        if m > margin:
            bad.append((round(t, 2), round(float(m), 3)))
    return bad
