"""The two-spiral data set and the small tanh network that untangles it (s10).

Every hidden layer is three wide, so each one can be drawn exactly in 3D. The net is trained once (seeded, Adam) and
cached in assets/spiral_net.npz; delete that file to retrain. Lab test (2026-11-16, 15k steps, 4 seeds): width-2
stacks of six layers reach 68-84 %, 2-3-3-3-1 reaches 71-99 %, and 2-3-3-3-3-1 reaches 100 % on seed 0, so that
is the one we draw.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np

SIZES = [2, 3, 3, 3, 3, 1]
CACHE = Path(__file__).parent / "assets" / "spiral_net.npz"


def spirals(m=300, seed=3):
    """Two interleaved spirals (1.5 turns each) in [-1, 1]^2: X (2m, 2), labels y (2m,)."""
    rng = np.random.default_rng(seed)
    t = np.sqrt(rng.random(m)) * 3 * np.pi
    a = np.c_[t * np.cos(t), t * np.sin(t)] / (3 * np.pi) + rng.normal(0, 0.015, (m, 2))
    return np.r_[a, -a], np.r_[np.zeros(m), np.ones(m)]


def forward(Ws, bs, X):
    """[X, h1, ..., h_L, logits]: tanh after every layer but the last (row vectors: h' = tanh(h W + b))."""
    hs = [np.asarray(X, float)]
    for W, b in zip(Ws[:-1], bs[:-1]):
        hs.append(np.tanh(hs[-1] @ W + b))
    hs.append(hs[-1] @ Ws[-1] + bs[-1])
    return hs


def accuracy(Ws, bs, X, y):
    return float(((forward(Ws, bs, X)[-1][:, 0] > 0) == y).mean())


def train(X, y, sizes, steps=15000, lr=0.01, seed=0):
    """Full-batch Adam on cross-entropy; tanh hidden layers, logistic output. Returns (Ws, bs, accuracy)."""
    r = np.random.default_rng(seed)
    Ws = [r.normal(0, np.sqrt(2 / i), (i, o)) for i, o in zip(sizes[:-1], sizes[1:])]
    bs = [np.zeros(o) for o in sizes[1:]]
    P = Ws + bs
    mom = [np.zeros_like(p) for p in P]
    vel = [np.zeros_like(p) for p in P]
    for it in range(1, steps + 1):
        hs = forward(Ws, bs, X)
        p_ = 1 / (1 + np.exp(-hs[-1][:, 0]))
        g = ((p_ - y) / len(y))[:, None]
        grads = [None] * len(P)
        for l in range(len(Ws) - 1, -1, -1):
            grads[l] = hs[l].T @ g
            grads[len(Ws) + l] = g.sum(0)
            if l:
                g = (g @ Ws[l].T) * (1 - hs[l] ** 2)
        for k, (p, G) in enumerate(zip(P, grads)):
            mom[k] = 0.9 * mom[k] + 0.1 * G
            vel[k] = 0.999 * vel[k] + 0.001 * G ** 2
            p -= lr * (mom[k] / (1 - 0.9 ** it)) / (np.sqrt(vel[k] / (1 - 0.999 ** it)) + 1e-8)
    return Ws, bs, accuracy(Ws, bs, X, y)


@lru_cache(maxsize=1)
def net():
    """(Ws, bs) of the drawn network, trained once and cached."""
    n = len(SIZES) - 1
    if CACHE.exists():
        z = np.load(CACHE)
        return [z[f"W{i}"] for i in range(n)], [z[f"b{i}"] for i in range(n)]
    X, y = spirals()
    Ws, bs, acc = train(X, y, SIZES)
    np.savez(CACHE, **{f"W{i}": W for i, W in enumerate(Ws)}, **{f"b{i}": b for i, b in enumerate(bs)})
    print(f"trained {SIZES}: accuracy {acc:.3f}")
    return Ws, bs


@lru_cache(maxsize=1)
def line():
    """The best single straight cut (logistic regression, no hidden layer): (w, b, accuracy)."""
    X, y = spirals()
    Ws, bs, acc = train(X, y, [2, 1], steps=4000, lr=0.02)
    return Ws[0][:, 0], float(bs[0][0]), acc


if __name__ == "__main__":
    X, y = spirals()
    Ws, bs = net()
    print("net accuracy", accuracy(Ws, bs, X, y))
    w, b, acc = line()
    print("straight line", w, b, "accuracy", acc)
