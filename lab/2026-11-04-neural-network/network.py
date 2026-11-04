"""A real handwritten-digit recognizer: MNIST at 14×14 → 40 → 36 → 32 → 28 → 24 → 16 → 10, trained in numpy.

ReLU hidden layers, softmax output, cross-entropy, Adam with minibatches. The 28×28 MNIST images are
2×2 average-pooled to 14×14 (196 inputs) so the input grid stays readable on screen.
The weights and the ten countdown digits (real test-set samples) are cached in out/net_cache.npz.

    uv run python lab/2026-11-04-neural-network/network.py      # train, validate, print summary
"""

from __future__ import annotations

import gzip
import hashlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MNIST = HERE / "out" / "mnist"          # downloaded from storage.googleapis.com/cvdf-datasets/mnist
CACHE = HERE / "out" / "net_cache.npz"
SIZES = (196, 40, 36, 32, 28, 24, 16, 10)
SEED = 7
EPOCHS = 12
BATCH = 128
COUNTDOWN = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]


def _idx(name, magic, shape_tail):
    with gzip.open(MNIST / f"{name}.gz", "rb") as f:
        raw = f.read()
    m, n = int.from_bytes(raw[0:4], "big"), int.from_bytes(raw[4:8], "big")
    assert m == magic, f"{name}: bad magic {m}"
    off = 8 + 4 * len(shape_tail)
    dims = [int.from_bytes(raw[8 + 4 * i:12 + 4 * i], "big") for i in range(len(shape_tail))]
    assert tuple(dims) == shape_tail, dims
    arr = np.frombuffer(raw, np.uint8, offset=off)
    assert arr.size == n * int(np.prod(shape_tail or (1,))), "truncated file"
    return arr.reshape((n, *shape_tail))


def mnist():
    """(Xtr28, ytr, Xte28, yte); images as float32 in [0, 1], shape (n, 28, 28)."""
    xtr = _idx("train-images-idx3-ubyte", 2051, (28, 28)).astype(np.float32) / 255
    ytr = _idx("train-labels-idx1-ubyte", 2049, ()).astype(int)
    xte = _idx("t10k-images-idx3-ubyte", 2051, (28, 28)).astype(np.float32) / 255
    yte = _idx("t10k-labels-idx1-ubyte", 2049, ()).astype(int)
    return xtr, ytr, xte, yte


def pool(x28):
    """2×2 average pool → (n, 196)."""
    return x28.reshape(-1, 14, 2, 14, 2).mean((2, 4)).reshape(-1, 196)


def forward(Ws, bs, X):
    """Returns per-layer activations [x, h1..h4, p]."""
    A = [X]
    for i, (W, b) in enumerate(zip(Ws, bs)):
        z = A[-1] @ W + b
        if i < len(Ws) - 1:
            A.append(np.maximum(z, 0))
        else:
            e = np.exp(z - z.max(-1, keepdims=True))
            A.append(e / e.sum(-1, keepdims=True))
    return A


def grads(Ws, bs, X, Y):
    A = forward(Ws, bs, X)
    n = len(X)
    d = A[-1].copy(); d[np.arange(n), Y] -= 1; d /= n
    gW, gb = [None] * len(Ws), [None] * len(Ws)
    for i in range(len(Ws) - 1, -1, -1):
        gW[i] = A[i].T @ d
        gb[i] = d.sum(0)
        if i > 0:
            d = (d @ Ws[i].T) * (A[i] > 0)
    loss = -np.mean(np.log(A[-1][np.arange(n), Y] + 1e-12))
    return gW, gb, loss


def train():
    xtr, ytr, xte, yte = mnist()
    X, Xt = pool(xtr), pool(xte)
    rng = np.random.default_rng(SEED)
    Ws = [rng.normal(0, np.sqrt(2.0 / a), (a, b)) for a, b in zip(SIZES[:-1], SIZES[1:])]
    bs = [np.zeros(b) for b in SIZES[1:]]
    params = Ws + bs
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    b1, b2, step = 0.9, 0.999, 0
    for ep in range(EPOCHS):
        lr = 3e-3 * 0.78 ** ep
        order = rng.permutation(len(X))
        for k in range(0, len(X), BATCH):
            idx = order[k:k + BATCH]
            gW, gb, _ = grads(Ws, bs, X[idx], ytr[idx])
            step += 1
            for j, (p, g) in enumerate(zip(params, gW + gb)):
                m[j] = b1 * m[j] + (1 - b1) * g
                v[j] = b2 * v[j] + (1 - b2) * g * g
                p -= lr * (m[j] / (1 - b1 ** step)) / (np.sqrt(v[j] / (1 - b2 ** step)) + 1e-8)
        acc = (forward(Ws, bs, Xt)[-1].argmax(1) == yte).mean()
        print(f"epoch {ep + 1}/{EPOCHS}: test acc {acc:.4f}")
    return Ws, bs


def pick_digits(Ws, bs):
    """For each countdown digit: a real test sample the net gets right with p > 0.98 whose ink amount is
    closest to its class median (a typical, not cherry-picked-thin or blobby, handwriting)."""
    _, _, xte, yte = mnist()
    P = forward(Ws, bs, pool(xte))[-1]
    ink = xte.reshape(len(xte), -1).sum(1)
    out = []
    for d in COUNTDOWN:
        cls = np.where(yte == d)[0]
        ok = cls[(P[cls].argmax(1) == d) & (P[cls, d] > 0.98)]
        med = np.median(ink[cls])
        out.append(ok[np.argmin(np.abs(ink[ok] - med))])
    return np.array(out)


def load():
    key = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]
    if CACHE.exists():
        d = dict(np.load(CACHE))
        if str(d.get("key", "")) == key:
            return d
    Ws, bs = train()
    sel = pick_digits(Ws, bs)
    _, _, xte, yte = mnist()
    d = {f"W{i}": W for i, W in enumerate(Ws)} | {f"b{i}": b for i, b in enumerate(bs)}
    d.update(digits28=xte[sel], digit_labels=yte[sel], digit_idx=sel, key=np.array(key))
    CACHE.parent.mkdir(exist_ok=True)
    np.savez(CACHE, **d)
    validate(d)
    return d


def weights(d):
    n = len(SIZES) - 1
    return [d[f"W{i}"] for i in range(n)], [d[f"b{i}"] for i in range(n)]


def validate(d):
    Ws, bs = weights(d)
    _, _, xte, yte = mnist()
    acc = (forward(Ws, bs, pool(xte))[-1].argmax(1) == yte).mean()
    assert acc > 0.96, acc
    assert list(d["digit_labels"]) == COUNTDOWN
    P = forward(Ws, bs, pool(d["digits28"]))[-1]
    assert (P.argmax(1) == COUNTDOWN).all() and (P.max(1) > 0.98).all(), P.max(1)
    # gradient check on a tiny batch
    rng = np.random.default_rng(0)
    X, Y = pool(xte[:16]), yte[:16]
    gW, _, _ = grads(Ws, bs, X, Y)
    for _i in range(5):
        li = rng.integers(len(Ws)); a, b = (rng.integers(s) for s in Ws[li].shape)
        h = 1e-5
        Ws[li][a, b] += h; lp = grads(Ws, bs, X, Y)[2]
        Ws[li][a, b] -= 2 * h; lm = grads(Ws, bs, X, Y)[2]
        Ws[li][a, b] += h
        fd = (lp - lm) / (2 * h)
        assert abs(fd - gW[li][a, b]) < 1e-6 + 1e-3 * abs(fd), (fd, gW[li][a, b])
    return acc


if __name__ == "__main__":
    d = load()
    acc = validate(d)
    Ws, bs = weights(d)
    print(f"test accuracy: {acc:.4f}")
    P = forward(Ws, bs, pool(d["digits28"]))[-1]
    for lab, idx, p in zip(d["digit_labels"], d["digit_idx"], P):
        print(f"digit {lab}: test #{idx}, p={p[lab]:.4f}, runner-up {np.sort(p)[-2]:.4f}")
