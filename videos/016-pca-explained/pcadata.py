"""Every number video 016 shows, computed once: the people data, the digits, their PCA, and the extra datasets.

Scenes and design frames import from here so the same seeded values appear everywhere. Nothing is eyeballed:
PCA is numpy `eigh` on the covariance (checked against sklearn and the SVD in `verify()`).

Example:
    from pcadata import people2, digits_pca
    P = people2()            # P.X (40, 2) cm, P.mu, P.C, P.lam (desc), P.V (columns = eigenvectors)
    D = digits_pca()         # D.Z (1797, 64) scores, D.share, D.mean, D.V
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np


@dataclass(frozen=True)
class PCA:
    X: np.ndarray        # data (n, d)
    mu: np.ndarray       # mean (d,)
    C: np.ndarray        # covariance, 1/n convention (d, d)
    lam: np.ndarray      # eigenvalues, descending (d,)
    V: np.ndarray        # eigenvectors as columns, same order (d, d)

    @property
    def Xc(self) -> np.ndarray:
        return self.X - self.mu

    @property
    def Z(self) -> np.ndarray:
        """Scores: coordinates of every centred point on the principal axes."""
        return self.Xc @ self.V

    @property
    def share(self) -> np.ndarray:
        return self.lam / self.lam.sum()

    def var_along(self, theta: np.ndarray) -> np.ndarray:
        """uᵀCu for unit u = (cos θ, sin θ) (2D only): the spread-vs-angle dial."""
        u = np.stack([np.cos(theta), np.sin(theta)])
        return np.einsum("in,ij,jn->n", u, self.C, u)

    def reconstruct(self, x: np.ndarray, k: int) -> np.ndarray:
        z = (x - self.mu) @ self.V[:, :k]
        return self.mu + z @ self.V[:, :k].T


def pca(X: np.ndarray) -> PCA:
    X = np.asarray(X, float)
    mu = X.mean(0)
    Xc = X - mu
    C = Xc.T @ Xc / len(X)
    lam, V = np.linalg.eigh(C)
    order = np.argsort(lam)[::-1]
    lam, V = np.clip(lam[order], 0, None), V[:, order]
    V = V * np.where(V[np.abs(V).argmax(0), range(V.shape[1])] < 0, -1, 1)  # largest entry positive: stable signs
    return PCA(X, mu, C, lam, V)


@lru_cache
def people2() -> PCA:
    """Forty people: height ~ N(170, 8.5) cm, arm span = height + N(1.5, 6) cm (seed 16). Illustrative.

    The arm-span-minus-height spread (~6 cm) is realistic and keeps λ1/λ2 near 10, so the second axis stays visible.
    """
    rng = np.random.default_rng(16)
    h = rng.normal(170, 8.5, 40)
    a = h + rng.normal(1.5, 6.0, 40)
    return pca(np.c_[h, a])


@lru_cache
def people3() -> PCA:
    """The same forty people plus shoulder width (cm): a long, fairly wide, thin 'pebble' cloud (seed 17)."""
    P = people2()
    rng = np.random.default_rng(17)
    h, a = P.X.T
    s = 0.23 * h + rng.normal(0, 1.6, len(h))      # shoulder width tracks size, with its own spread
    return pca(np.c_[h, a, s])


@lru_cache
def digits() -> tuple[np.ndarray, np.ndarray]:
    """The UCI 8x8 digits (sklearn bundle): X (1797, 64) grey levels 0..16, y labels."""
    from sklearn.datasets import load_digits
    d = load_digits()
    return d.data.astype(float), d.target.astype(int)


@lru_cache
def digits_pca() -> PCA:
    return pca(digits()[0])


def k_for(share: np.ndarray, q: float) -> int:
    """Smallest k whose cumulative share reaches q."""
    return int(np.searchsorted(np.cumsum(share), q - 1e-12) + 1)


@lru_cache
def sculpture(n: int = 900) -> np.ndarray:
    """3D point sculpture for the shadow bookends (seed 1601): three clusters threaded by a helix, in a plane.

    Built in a frame where the structure lies in the x-y plane and z is thin, then rotated by a fixed rotation, so
    a random view shows a blob and the top principal plane shows the clusters and the spiral.
    """
    rng = np.random.default_rng(1601)
    centres = np.array([[-2.2, -0.6, 0], [0.4, 1.6, 0], [2.0, -1.2, 0]])
    k = n // 4
    cl = np.concatenate([c + rng.normal(0, [0.42, 0.42, 0.25], (k, 3)) for c in centres])
    t = np.linspace(0, 1, n - 3 * k)
    helix = np.c_[3.0 * (t - 0.5) * 2, 1.3 * np.sin(6 * np.pi * t), 0.25 * np.cos(6 * np.pi * t)]
    P = np.concatenate([cl, helix + rng.normal(0, 0.05, helix.shape)])
    from scipy.spatial.transform import Rotation
    R = Rotation.from_euler("xyz", [58, -34, 21], degrees=True).as_matrix()
    return P @ R.T


@lru_cache
def beads(n_per: int = 52, n_wire: int = 320, r: float = 0.15):
    """The bookend sculpture as an object (seed 1611): three bunches of glass beads threaded by a gold spiral wire.

    Same layout as `sculpture()` (three clusters and a helix in a plane, then the fixed rotation), but each bunch is
    non-overlapping beads of radius `r` (dart throwing in a Gaussian ellipsoid) and the helix is a smooth wire.
    Returns (bead centres (3·n_per, 3), bunch label per bead, wire points (n_wire, 3), bead radius).
    """
    rng = np.random.default_rng(1611)
    centres = np.array([[-2.2, -0.6, 0], [0.4, 1.6, 0], [2.0, -1.2, 0]])
    pts, lab = [], []
    for k, c in enumerate(centres):
        got = []
        while len(got) < n_per:
            q = c + rng.normal(0, [0.5, 0.5, 0.3])
            if all(np.linalg.norm(q - g) > 2.05 * r for g in got):
                got.append(q)
        pts += got
        lab += [k] * n_per
    t = np.linspace(0, 1, n_wire)
    wire = np.c_[3.0 * (t - 0.5) * 2, 1.3 * np.sin(6 * np.pi * t), 0.25 * np.cos(6 * np.pi * t)]
    from scipy.spatial.transform import Rotation
    R = Rotation.from_euler("xyz", [58, -34, 21], degrees=True).as_matrix()
    return np.array(pts) @ R.T, np.array(lab), wire @ R.T, r


def two_groups(n: int = 160) -> tuple[np.ndarray, np.ndarray]:
    """Two long thin parallel groups (seed 1603): PC1 runs along them, PC2 separates them."""
    rng = np.random.default_rng(1603)
    along = rng.normal(0, 2.0, (n, 1))
    across = rng.normal(0, 0.18, (n, 1))
    lab = np.repeat([0, 1], n // 2)
    off = np.where(lab == 0, -0.55, 0.55)[:, None]
    X = np.c_[along, across + off]
    th = np.deg2rad(25)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return X @ R.T, lab


def swiss_roll(n: int = 1500) -> tuple[np.ndarray, np.ndarray]:
    """A wide rolled sheet (seed 1602): points (n, 3) and their position t along the roll (0..1, for colour).

    The sheet is wider (y) than the roll is across, so PCA's best flat view contains the width and one direction
    across the roll: the turns of the roll land on top of each other.
    """
    rng = np.random.default_rng(1602)
    t = 1.5 * np.pi * (1 + 2 * rng.random(n))
    y = 40 * rng.random(n)
    X = np.c_[t * np.cos(t), y, t * np.sin(t)] / 4.0
    return X, (t - t.min()) / np.ptp(t)


def verify() -> dict:
    """Cross-checks and the numbers the narration states. Raises AssertionError if a claim is false."""
    from sklearn.decomposition import PCA as SKPCA
    out = {}
    P = people2()
    out["people_C"] = P.C.round(1).tolist()
    out["people_lam"] = P.lam.round(1).tolist()
    out["people_share_pc1"] = round(float(P.share[0]), 3)
    th = np.linspace(0, np.pi, 3601)
    assert abs(th[P.var_along(th).argmax()] - np.arctan2(P.V[1, 0], P.V[0, 0]) % np.pi) < 1e-3   # dial peak = PC1
    d_diag = P.var_along(np.array([np.pi / 4]))[0]
    assert d_diag > P.C[0, 0] and d_diag > P.C[1, 1], "diagonal spread beats both axes"
    D = digits_pca()
    X, y = digits()
    sk = SKPCA().fit(X)
    assert np.allclose(sk.explained_variance_ratio_, D.share, atol=1e-9)
    s = np.linalg.svd(D.Xc, compute_uv=False)
    assert np.allclose(s ** 2 / len(X), D.lam, rtol=1e-8, atol=1e-8)
    out["digits_share_2"] = round(float(D.share[:2].sum()), 3)
    out["digits_k90"] = k_for(D.share, 0.90)
    out["digits_zero"] = int((D.lam < 1e-9).sum())
    out["digits_blank_pixels"] = np.where(X.std(0) == 0)[0].tolist()
    assert 0.25 < out["digits_share_2"] < 0.33 and 19 <= out["digits_k90"] <= 22 and out["digits_zero"] == 3
    # neighbours correlate: mean correlation of 4-neighbour pixel pairs vs all pairs
    R = np.corrcoef(X[:, X.std(0) > 0].T)
    idx = np.where(X.std(0) > 0)[0]
    pos = {p: i for i, p in enumerate(idx)}
    nb = [R[pos[p], pos[q]] for p in idx for q in (p + 1, p + 8) if q in pos and (q != p + 1 or p % 8 != 7)]
    out["neighbour_corr"] = round(float(np.mean(nb)), 3)
    out["all_pair_corr"] = round(float(R[np.triu_indices_from(R, 1)].mean()), 3)
    assert out["neighbour_corr"] > out["all_pair_corr"] + 0.2
    # zeros, sixes, fours form their own regions in the 2D map: nearest-centroid accuracy in PC1-PC2
    Z2 = D.Z[:, :2]
    cents = np.array([Z2[y == c].mean(0) for c in range(10)])
    pred = np.argmin(((Z2[:, None] - cents[None]) ** 2).sum(-1), 1)
    out["map_class_recall"] = {c: round(float((pred[y == c] == c).mean()), 2) for c in range(10)}
    # reconstruction error of a '3' (first one in the set), relative to its norm
    x3 = X[np.where(y == 3)[0][0]]
    out["recon_err_3"] = {k: round(float(np.linalg.norm(D.reconstruct(x3, k) - x3) / np.linalg.norm(x3 - D.mu)), 3)
                          for k in (1, 2, 3, 5, 10, 20, 64)}
    P3 = people3()
    out["people3_share"] = P3.share.round(3).tolist()
    G, lab = two_groups()
    g = pca(G)
    z = g.Z
    out["two_groups_lam"] = g.lam.round(3).tolist()
    out["two_groups_sep_pc2"] = round(float(abs(z[lab == 0, 1].mean() - z[lab == 1, 1].mean()) / z[:, 1].std()), 2)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=1))


# ------------------------------------------------------------------------------- the in_s04 applications
REGIONS = [(-4, 40, 2.6, 1.8), (-3, 54, 1.6, 2.2), (2, 47, 2.2, 1.8), (15, 61, 2.6, 3.0),
           (10, 51, 2.2, 1.6), (12.5, 42.5, 1.4, 2.4), (21, 43, 2.2, 1.8), (25, 52, 3.0, 2.0)]


@lru_cache
def genes(n_per: int = 38, snps: int = 500) -> tuple[np.ndarray, np.ndarray, PCA]:
    """Simulated genotypes across Europe (seed 1606): allele frequencies drift smoothly with place (isolation by
    distance), so PCA of the genotype matrix recovers a map. Returns home (lon, lat), genotypes, their PCA.
    Illustrative, after Novembre et al. 2008 (real data not used)."""
    rng = np.random.default_rng(1606)
    home = np.concatenate([np.c_[rng.normal(lo, sx, n_per), rng.normal(la, sy, n_per)] for lo, la, sx, sy in REGIONS])
    p = (home - home.mean(0)) / home.std(0)
    W = rng.normal(0, 1, (2, snps)) * 0.9
    Wq = rng.normal(0, 1, (3, snps)) * 0.35                       # a little curvature in the gradients
    q = np.c_[p[:, 0] ** 2, p[:, 1] ** 2, p[:, 0] * p[:, 1]]
    f = 1 / (1 + np.exp(-(p @ W + q @ Wq + rng.normal(0, 0.6, snps))))
    G = rng.binomial(2, f).astype(float)
    return home, G, pca(G)


def _face(prm, size: int = 40) -> np.ndarray:
    """A made-up face (not a person) as a grey image 0..1, drawn with soft signed-distance shapes."""
    yy, xx = (np.mgrid[0:size, 0:size] + 0.5) / size * 2 - 1
    yy = -yy
    hw, hh, ex, ey, er, by, mw, mc, nl, hl = prm

    def ell(cx, cy, rx, ry):
        return np.clip(1 - (np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) - 1) * size * min(rx, ry) / 1.5, 0, 1)

    img = 0.55 * ell(0, -0.05, hw, hh)
    img = np.maximum(img, 0.25 * ell(0, hl, hw * 1.02, 0.5) * (yy > hl - 0.15))      # hair
    for sx in (-1, 1):
        img -= 0.45 * ell(sx * ex, ey, er, er * 0.7)                                  # eyes
        img -= 0.25 * ell(sx * ex, ey + by, er * 1.3, 0.05)                           # brows
    img -= 0.18 * ell(0, ey - nl / 2 - 0.08, 0.06, nl / 2)                            # nose
    mouth = np.exp(-((yy - (-0.45 + mc * xx ** 2)) / 0.05) ** 2) * (np.abs(xx) < mw)
    img -= 0.35 * mouth
    return np.clip(img, 0, 1)


@lru_cache
def faces(n: int = 240, size: int = 40) -> tuple[np.ndarray, PCA]:
    """Made-up faces (seed 1607): images (n, size, size) and the PCA of their pixels (eigenfaces = V columns)."""
    rng = np.random.default_rng(1607)
    lo = np.array([0.55, 0.70, 0.22, 0.12, 0.08, 0.10, 0.18, -0.6, 0.18, 0.35])
    hi = np.array([0.80, 0.92, 0.36, 0.30, 0.15, 0.22, 0.42, 0.9, 0.40, 0.65])
    P = lo + (hi - lo) * rng.random((n, 10))
    imgs = np.stack([_face(pp, size) for pp in P])
    return imgs, pca(imgs.reshape(n, -1))


@lru_cache
def scene_image(size: int = 128) -> np.ndarray:
    """A small made-up grey picture (seed 1608): sky, sun, three hills, trees, some grain. Values 0..1."""
    rng = np.random.default_rng(1608)
    yy, xx = (np.mgrid[0:size, 0:size] + 0.5) / size
    img = 0.75 - 0.45 * yy
    img = np.maximum(img, 0.98 * (((xx - 0.72) ** 2 + (yy - 0.25) ** 2) < 0.012))
    for k, (h, a, f, ph, g) in enumerate([(0.55, 0.06, 7, 0.4, 0.45), (0.68, 0.05, 11, 1.7, 0.3), (0.82, 0.04, 5, 2.9, 0.16)]):
        ridge = h + a * np.sin(f * xx + ph) + 0.02 * np.sin(23 * xx + k)
        img = np.where(yy > ridge, g + 0.06 * np.sin(40 * xx * (k + 1)) * (yy - ridge), img)
    for tx in rng.uniform(0.08, 0.92, 7):
        base = 0.8 + 0.08 * rng.random()
        tri = (yy < base) & (yy > base - 0.16) & (np.abs(xx - tx) < (yy - (base - 0.16)) * 0.35)
        img = np.where(tri, 0.08, img)
    img = img + rng.normal(0, 0.025, img.shape)
    return np.clip(img, 0, 1)


def patch_reconstruct(img: np.ndarray, k: int, p: int = 8) -> np.ndarray:
    """Rebuild `img` from the top-k principal components of its p x p patches (PCA fitted on those patches)."""
    s = img.shape[0] // p
    P = img[:s * p, :s * p].reshape(s, p, s, p).transpose(0, 2, 1, 3).reshape(-1, p * p)
    Q = pca(P)
    R = Q.mu + (P - Q.mu) @ Q.V[:, :k] @ Q.V[:, :k].T
    return np.clip(R.reshape(s, s, p, p).transpose(0, 2, 1, 3).reshape(s * p, s * p), 0, 1)


MATURITIES = np.array([0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30])


@lru_cache
def yields(days: int = 750) -> tuple[np.ndarray, PCA]:
    """Simulated yield curves (seed 1609): Nelson-Siegel level / slope / curvature factors as random walks.
    Returns curves (days, 10) in % and the PCA of the daily changes (V columns ~ level, slope, bend)."""
    rng = np.random.default_rng(1609)
    lam = 0.6
    m = MATURITIES
    L = np.c_[np.ones_like(m), (1 - np.exp(-lam * m)) / (lam * m),
              (1 - np.exp(-lam * m)) / (lam * m) - np.exp(-lam * m)]
    F = np.cumsum(rng.normal(0, [0.06, 0.045, 0.06], (days, 3)), 0) + np.array([3.4, -1.6, 0.8])
    Y = F @ L.T + rng.normal(0, 0.006, (days, len(m)))
    return Y, pca(np.diff(Y, axis=0))
