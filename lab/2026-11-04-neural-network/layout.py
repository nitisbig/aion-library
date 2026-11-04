"""3D layout: layers are planes perpendicular to x, input at x = −6.3, output at x = +6.3 (1.8 apart).

Input is the 14×14 pixel grid. Hidden layers are sunflower (Fibonacci) discs. The 10 outputs form a
column with 9 at the top and 0 at the bottom, so the countdown sweeps down it.
Edges are cubic Béziers tangent to +x. The input fan (196 × 32) is pruned for display only: each
hidden-1 neuron keeps its K strongest input weights. The forward pass itself always uses every weight.
"""

from __future__ import annotations

import numpy as np

import network as N

NL = len(N.SIZES)
LAYER_X = np.linspace(-6.3, 6.3, NL)
RADIUS = np.array([0.045] + [0.06] * (NL - 2) + [0.09])       # small, crisp neurons
SAMPLES = 20
K_INPUT = 24
IN_SP = 0.26                  # input pixel pitch
IN_TILT = np.radians(55.0)     # the input grid faces the camera's side like a screen, never seen mirrored
IN_N = np.array([-np.cos(IN_TILT), 0.0, np.sin(IN_TILT)])    # its front normal
IN_H = np.array([np.sin(IN_TILT), 0.0, np.cos(IN_TILT)])     # its screen-right axis


def input_point(row, col, front=0.0):
    """Continuous 14-grid coords (row 0 = top) → world position on the tilted input plane."""
    row, col = np.asarray(row, float), np.asarray(col, float)
    return (np.array([LAYER_X[0], 0, 0]) + (-(row - 6.5) * IN_SP)[..., None] * np.array([0, 1.0, 0])
            + ((col - 6.5) * IN_SP)[..., None] * IN_H + front * IN_N)
OUT_SP = 0.32                 # output column pitch
DISC_R = [None, 1.5, 1.45, 1.4, 1.3, 1.2, 1.0, None]


# colour: one hue per layer along a spectrum; each output digit has its own hue
LAYER_COLS = ["#5EC8FF", "#3FE0D0", "#7CE38B", "#E6E36A", "#FFB45C", "#FF7A7A", "#E07BFF", "#A9B4FF"]
OUT_COLS = ["#FF6B6B", "#FF9F45", "#FFD452", "#B8E65A", "#4FE08A", "#38D9C9", "#4CB8FF",
            "#6F8BFF", "#A97BFF", "#F07BE0"]          # digits 0 … 9


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return np.array([((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4)])


def node_colors(layer, idx):
    c = np.array([lin(LAYER_COLS[l]) for l in layer])
    out = layer == NL - 1
    c[out] = np.array([lin(OUT_COLS[k]) for k in idx[out]])
    return c


def _sunflower(n, R):
    i = np.arange(n) + 0.5
    r = R * np.sqrt(i / n)
    a = i * np.pi * (3 - np.sqrt(5))
    return np.column_stack([r * np.sin(a), r * np.cos(a)])


def nodes():
    """pos (n, 3), layer (n,), index-in-layer (n,), slices per layer."""
    rr, cc = np.divmod(np.arange(196), 14)
    yz = [None]
    for l in range(1, NL - 1):
        yz.append(_sunflower(N.SIZES[l], DISC_R[l]))
    yz.append(np.column_stack([(np.arange(10) - 4.5) * OUT_SP, np.zeros(10)]))   # digit k at y ∝ k
    pos, layer, idx = [], [], []
    for l, pts in enumerate(yz):
        assert l == 0 or len(pts) == N.SIZES[l]
        if l == 0:
            for k, (r, c) in enumerate(zip(rr, cc)):
                pos.append(tuple(input_point(r, c))); layer.append(0); idx.append(k)
            continue
        for k, (y, z) in enumerate(pts):
            pos.append((LAYER_X[l], y, z)); layer.append(l); idx.append(k)
    off = np.concatenate([[0], np.cumsum(N.SIZES)])
    return np.array(pos), np.array(layer), np.array(idx), [slice(off[l], off[l + 1]) for l in range(NL)]


def edges(d):
    """Displayed edges: src, dst (global ids), layer, (a, b) indices into W_layer, Bézier control points."""
    pos, layer, idx, sl = nodes()
    Ws, _ = N.weights(d)
    src, dst, el, ia, ib = [], [], [], [], []
    for l in range(NL - 1):
        W = Ws[l]
        for b in range(W.shape[1]):
            keep = np.argsort(-np.abs(W[:, b]))[:K_INPUT] if l == 0 else np.arange(W.shape[0])
            for a in np.sort(keep):
                src.append(sl[l].start + a); dst.append(sl[l + 1].start + b)
                el.append(l); ia.append(a); ib.append(b)
    src, dst, el, ia, ib = map(np.array, (src, dst, el, ia, ib))
    P0, P3 = pos[src], pos[dst]
    dx = (P3[:, 0] - P0[:, 0])[:, None] * np.array([1.0, 0, 0])
    ctrl = np.stack([P0, P0 + 0.42 * dx, P3 - 0.42 * dx, P3], 1)
    return src, dst, el, ia, ib, ctrl


def bezier(ctrl, s):
    s = np.asarray(s)[..., None]
    P0, P1, P2, P3 = (ctrl[..., k, :][..., None, :] for k in range(4))
    return (1 - s) ** 3 * P0 + 3 * (1 - s) ** 2 * s * P1 + 3 * (1 - s) * s ** 2 * P2 + s ** 3 * P3


def edge_lines(ctrl, el):
    """Line-segment vertex buffer: per vertex (x, y, z, s, edge_id, layer)."""
    s = np.linspace(0, 1, SAMPLES)
    pts = bezier(ctrl, s)
    n_e = len(ctrl)
    seg = np.stack([np.arange(SAMPLES - 1), np.arange(1, SAMPLES)], 1).ravel()
    P = pts[:, seg]
    S = np.broadcast_to(s[seg], (n_e, len(seg)))
    E = np.broadcast_to(np.arange(n_e)[:, None], (n_e, len(seg)))
    L = np.broadcast_to(el[:, None], (n_e, len(seg)))
    return np.concatenate([P, S[..., None], E[..., None], L[..., None]], -1).reshape(-1, 6).astype("f4")
