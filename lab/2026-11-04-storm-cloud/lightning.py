"""Lightning channels grown with the Dielectric Breakdown Model.

DBM (Niemeyer, Pietronero & Wiesmann 1984): the channel is a conductor and the discharge grows one lattice
site at a time, at a candidate site next to the channel, preferring sites where the field is strongest (the
tips). Instead of solving Laplace's equation every step we use a charge-superposition potential (in the
spirit of Kim & Lin 2007): an external cloud→ground field E along the bolt direction, screened by the
channel's own charge, each channel site acting as a point charge:

    φ_i = E·x_i − q Σ_k 1/|x_i − x_k|          p_i ∝ exp((φ_i − max φ) / T)

Screening suppresses growth inside the cluster (so it doesn't turn into a bush), and T sets how branchy it is
(the role η plays in classic DBM). Potentials update incrementally as sites are added. Every site remembers
the step at which it grew, so the stepped leader can be replayed in slow motion, and the return stroke follows
the path from the root to the site that reached the target.

    uv run python lab/2026-11-04-storm-cloud/lightning.py      # grow all bolts + stats
"""

from __future__ import annotations

import itertools

import numpy as np

NB = np.array([d for d in itertools.product((-1, 0, 1), repeat=3) if d != (0, 0, 0)])


def dbm(start, direction, h, length, T=10.0, field=1.0, seed=0, max_sites=4000, q=7.0):
    """Grow a channel from `start` until it advances `length` along `direction`. Returns lattice sites."""
    rng = np.random.default_rng(seed)
    direction = np.asarray(direction, float)
    direction /= np.linalg.norm(direction)
    sites = [np.zeros(3, int)]
    parent = [-1]
    step = [0]
    in_ch = {(0, 0, 0)}
    cand_pos = NB.copy()
    cand_par = np.zeros(len(NB), int)
    cand_phi = 1.0 / np.linalg.norm(NB, axis=1)
    cand_idx = {tuple(c): i for i, c in enumerate(cand_pos)}
    reach = length / h
    end = None
    for n in range(1, max_sites):
        phi = field * (cand_pos @ direction) - q * cand_phi
        pn = np.exp((phi - phi.max()) / T)
        i = rng.choice(len(pn), p=pn / pn.sum())
        p = cand_pos[i].copy()
        sites.append(p); parent.append(int(cand_par[i])); step.append(n)
        in_ch.add(tuple(p))
        # swap-remove candidate i
        last = len(cand_pos) - 1
        del cand_idx[tuple(p)]
        if i != last:
            cand_pos[i], cand_par[i], cand_phi[i] = cand_pos[last], cand_par[last], cand_phi[last]
            cand_idx[tuple(cand_pos[i])] = i
        cand_pos, cand_par, cand_phi = cand_pos[:last], cand_par[:last], cand_phi[:last]
        # the new channel site is a new charge
        cand_phi += 1.0 / np.linalg.norm(cand_pos - p, axis=1)
        new = [tuple(q) for q in p + NB if tuple(q) not in in_ch and tuple(q) not in cand_idx]
        if new:
            nq = np.array(new)
            S = np.array(sites)
            nphi = (1.0 / np.linalg.norm(nq[:, None, :] - S[None], axis=2)).sum(1)
            base = len(cand_pos)
            for k, qq in enumerate(new):
                cand_idx[qq] = base + k
            cand_pos = np.r_[cand_pos, nq]
            cand_par = np.r_[cand_par, np.full(len(nq), len(sites) - 1)]
            cand_phi = np.r_[cand_phi, nphi]
        if p @ direction >= reach:
            end = len(sites) - 1
            break
    if end is None:
        end = int(np.argmax(np.array(sites) @ direction))
    return np.array(sites), np.array(parent), np.array(step), end


def frame_for(direction):
    d = np.asarray(direction, float) / np.linalg.norm(direction)
    a = np.array([0.0, 0.0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(d, a); u /= np.linalg.norm(u)
    return d, u, np.cross(d, u)


def to_segments(start, sites, parent, step, end, h, seed, jitter=0.32, subdiv=2):
    """Lattice tree → world polyline segments with jitter + midpoint displacement.

    Per segment: a(xyz, grow time 0..1), b(xyz, weight), flags(main, 0, 0, 0).
    grow time is normalised so the site that reaches the target grows at 1.0.
    weight ∝ (subtree size)^0.5 / max: thick, bright trunks and faint twigs.
    """
    rng = np.random.default_rng(seed)
    n = len(sites)
    pos = start + sites * h + rng.normal(0, jitter * h, (n, 3))
    pos[0] = start
    sub = np.ones(n)
    for i in range(n - 1, 0, -1):
        sub[parent[i]] += sub[i]
    main = np.zeros(n, bool)
    path = []
    i = end
    while i >= 0:
        main[i] = True
        path.append(i)
        i = parent[i]
    t = step / step[end]
    wgt = np.sqrt(sub / sub[0])
    segs = []
    for c in range(1, n):
        p = parent[c]
        pts = [pos[p], pos[c]]
        ts = [t[p], t[c]]
        for _ in range(subdiv):                                   # midpoint displacement
            npts, nts = [pts[0]], [ts[0]]
            for a, b, ta, tb in zip(pts[:-1], pts[1:], ts[:-1], ts[1:]):
                L = np.linalg.norm(b - a)
                npts += [(a + b) / 2 + rng.normal(0, 0.14 * L, 3), b]
                nts += [(ta + tb) / 2, tb]
            pts, ts = npts, nts
        for a, b, ta, tb in zip(pts[:-1], pts[1:], ts[:-1], ts[1:]):
            segs.append([*a, ta, *b, wgt[c], float(main[c] and main[p]), sub[c], 0, 0])
    return np.array(segs, "f4"), pos[path[::-1]]


BOLTS = {
    # name: start, direction, length, lattice h, temperature T, screening q, seed
    "hero": dict(start=(-1.2, 2.35, -0.6), direction=(0.08, -1.0, 0.05), length=12.0, h=0.1, T=10.0, q=7.0, seed=21),
    "spider": dict(start=(-2.6, 5.9, -2.2), direction=(1.0, 0.08, 0.1), length=6.5, h=0.08, T=11.0, q=7.0, seed=23),
    "side": dict(start=(5.9, 4.4, 0.6), direction=(1.0, -0.75, 0.25), length=4.5, h=0.06, T=9.0, q=6.0, seed=5),
}


def grow_all():
    out = {}
    for name, c in BOLTS.items():
        sites, parent, step, end = dbm(np.zeros(3), c["direction"], c["h"], c["length"], c["T"], 1.0, c["seed"],
                                       q=c["q"])
        segs, main_pts = to_segments(np.asarray(c["start"], float), sites, parent, step, end, c["h"], c["seed"])
        out[name] = dict(segs=segs, main=main_pts.astype("f4"), sites=len(sites))
    return out


if __name__ == "__main__":
    import time
    t0 = time.time()
    B = grow_all()
    for k, v in B.items():
        print(f"{k:7s}: {v['sites']:5d} sites → {len(v['segs']):6d} segments, main channel {len(v['main'])} sites")
    print(f"{time.time() - t0:.1f}s")
