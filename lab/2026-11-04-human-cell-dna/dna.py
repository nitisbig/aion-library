"""Molecular geometry, in nanometres: B-DNA, the nucleosome, the 10-nm chromatin fibre, the hero DNA.

Everything is computed from the real numbers and asserted on import:
  B-DNA      right-handed, 10.5 bp/turn, 0.338 nm rise, phosphate radius 0.89 nm, minor/major grooves
  nucleosome 147 bp in 1.65 left-handed superhelical turns, radius 4.18 nm, pitch 2.39 nm, histone octamer
  sequence   the start of the human HBB (beta-globin) coding sequence, checked by translating it

    uv run python lab/2026-11-04-human-cell-dna/dna.py      # prints the numbers
"""

from __future__ import annotations

import numpy as np

# ── B-DNA ────────────────────────────────────────────────────────────────────
RISE = 0.338                     # nm per base pair
BP_PER_TURN = 10.5
TWIST = 2 * np.pi / BP_PER_TURN  # 34.3° per bp
PITCH = RISE * BP_PER_TURN       # 3.55 nm
R_P = 0.89                       # phosphorus radius from the axis
R_SUGAR = 0.62
DNA_R = 1.0                      # DNA radius (2.0 nm diameter)
GROOVE = np.deg2rad(144.0)       # angular offset of strand 2 → minor groove on the short side

# ── nucleosome core particle ─────────────────────────────────────────────────
NUC_BP = 147
SH_R = 4.18                      # superhelix radius at the DNA axis
SH_PITCH = 2.39                  # nm per superhelical turn
SH_TURNS = 1.65
SH_SIGN = -1.0                   # left-handed

# ── human HBB (beta-globin) coding sequence, NM_000518 ──────────────────────
HBB = ("ATGGTGCATCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAGTTGGTGGTGAGGCCCTGGGCAGG"
       "CTGCTGGTGGTCTACCCTTGGACCCAGAGGTTCTTTGAGTCCTTTGGGGATCTGTCCACTCCTGATGCTGTTATGGGCAACCCTAAGGTGAAGG"
       "CTCATGGCAAGAAAGTGCTCGGTGCCTTTAGTGATGGCCTGGCTCACCTGGACAACCTCAAGGGCACCTTTGCCACACTGAGTGAGCTGCACT"
       "GTGACAAGCTGCACGTGGATCCTGAGAACTTCAGGCTCCTGGGCAACGTGCTGGTCTGTGTGCTGGCCCATCACTTTGGCAAAGAATTCACCC"
       "CACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAATGCCCTGGCCCACAAGTATCACTAA")
HBB_PROTEIN = ("MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSE"
               "LHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH")
COMP = dict(A="T", T="A", G="C", C="G")
HBONDS = dict(A=2, T=2, G=3, C=3)
PURINE = set("AG")

_B = "TCAG"
_AA = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODON = {a + b + c: _AA[16 * i + 4 * j + k] for i, a in enumerate(_B) for j, b in enumerate(_B) for k, c in enumerate(_B)}


def translate(seq):
    return "".join(CODON[seq[i:i + 3]] for i in range(0, len(seq) - 2, 3))


# ── small vector helpers ─────────────────────────────────────────────────────
def unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def rot(axis, ang):
    """Rodrigues rotation matrix (or a stack of them)."""
    axis = unit(np.asarray(axis, float))
    x, y, z = axis[..., 0], axis[..., 1], axis[..., 2]
    c, s = np.cos(ang), np.sin(ang)
    C = 1 - c
    return np.stack([np.stack([c + x * x * C, x * y * C - z * s, x * z * C + y * s], -1),
                     np.stack([y * x * C + z * s, c + y * y * C, y * z * C - x * s], -1),
                     np.stack([z * x * C - y * s, z * y * C + x * s, c + z * z * C], -1)], -2)


def transport_frames(P):
    """Tangents T and parallel-transported normals N along a polyline (rotation-minimising)."""
    T = np.empty_like(P)
    T[:-1] = unit(P[1:] - P[:-1])
    T[-1] = T[-2]
    N = np.empty_like(P)
    a = np.array([0.0, 0.0, 1.0]) if abs(T[0, 2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    N[0] = unit(np.cross(np.cross(T[0], a), T[0]))
    for i in range(1, len(P)):
        v = np.cross(T[i - 1], T[i])
        s = np.linalg.norm(v)
        if s < 1e-9:
            N[i] = N[i - 1]
        else:
            N[i] = rot(v, np.arctan2(s, np.dot(T[i - 1], T[i]))) @ N[i - 1]
        N[i] = unit(N[i] - T[i] * np.dot(N[i], T[i]))
    return T, N


# ── nucleosome superhelix (local frame: superhelix axis = z, dyad = +x) ──────
def superhelix(n=NUC_BP):
    th = np.linspace(-SH_TURNS * np.pi, SH_TURNS * np.pi, n)
    return np.column_stack([SH_R * np.cos(th), SH_R * np.sin(th), SH_SIGN * SH_PITCH * th / (2 * np.pi)])


def octamer_blobs():
    """Centres of the 8 histones: two layers of 4 (one per DNA gyre), and their type (0 H3, 1 H4, 2 H2A, 3 H2B)."""
    out, kind = [], []
    for layer, z in enumerate((1.25, -1.25)):
        for k in range(4):
            a = np.pi / 4 + k * np.pi / 2 + layer * np.pi / 4
            out.append([1.65 * np.cos(a), 1.65 * np.sin(a), z])
            kind.append([0, 1, 2, 3][(k + layer * 2) % 4])
    return np.array(out), np.array(kind)


def hermite(p0, t0, p1, t1, n):
    s = np.linspace(0, 1, n)[:, None]
    h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
    return h00 * p0 + h10 * t0 + h01 * p1 + h11 * t1


def resample(P, step):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(int(round(s[-1] / step)) + 1, 2)
    q = np.linspace(0, s[-1], n)
    return np.column_stack([np.interp(q, s, P[:, k]) for k in range(3)]), s[-1]


# ── chromatin: 10-nm fibres in a territory ───────────────────────────────────
TERRITORY_R = 380.0
N_FIBRES = 34
NUC_PER_FIBRE = 104
NUC_SPACING = 19.0               # centre-to-centre along the fibre (≈ 200 bp repeat)
HERO_FIBRE, HERO_NUC = 0, 52


def fibre_curve(rng, start, length, step=2.0, persist=30.0):
    n = int(length / step)
    P = np.empty((n, 3))
    P[0] = start
    d = unit(rng.normal(size=3))
    for i in range(1, n):
        d = unit(d + rng.normal(size=3) * np.sqrt(2 * step / persist) * 0.7)
        r = np.linalg.norm(P[i - 1])
        if r > TERRITORY_R * 0.85:                       # steer back into the territory
            d = unit(d - P[i - 1] / r * (r / TERRITORY_R - 0.85) * 2.0)
        P[i] = P[i - 1] + d * step
    return P


def build_chromatin(seed=11):
    """Static LOD geometry for all fibres, plus the hero nucleosome's neighbourhood.

    Returns dict with
      beads   (n, 8)  pos, r, colour index, arc-phase, fibre id, hero-exclude flag (unused after filtering)
      hist    (m, 6)  histone sphere pos, r, type, fibre id
      hero    dict    linker-in + wrap + linker-out centreline (bp spaced), wrap indices, histone frame, fibre curve
    """
    rng = np.random.default_rng(seed)
    blobs, bkind = octamer_blobs()
    sh = superhelix()
    sh_dense, _ = resample(superhelix(600), 0.8)
    # local entry/exit tangents of the wrap
    t_in = unit(sh[1] - sh[0])
    t_out = unit(sh[-1] - sh[-2])
    avg = unit(t_in + t_out)

    beads, hist, hero = [], [], None
    for f in range(N_FIBRES):
        L = NUC_PER_FIBRE * NUC_SPACING + 60
        start = np.zeros(3) - np.array([80.0, 0, 0]) if f == HERO_FIBRE else unit(rng.normal(size=3)) * TERRITORY_R * rng.uniform(0.2, 0.8)
        C = fibre_curve(rng, start, L)
        Cs, _ = resample(C, 1.0)
        T, N = transport_frames(Cs)
        nucs = []
        for k in range(NUC_PER_FIBRE):
            i = int(30 + k * NUC_SPACING)
            if i >= len(Cs) - 5:
                break
            # local→world rotation: avg tangent → fibre tangent, superhelix axis ⟂ tangent (random roll)
            roll = rng.uniform(0, 2 * np.pi)
            ax = rot(T[i], roll) @ N[i]
            ex = unit(np.cross(ax, T[i]))
            # local basis (avg, z, avg×z) → world (T, ax, T×ax)
            Lb = np.stack([avg, [0, 0, 1.0], np.cross(avg, [0, 0, 1.0])], 1)
            Wb = np.stack([T[i], ax, np.cross(T[i], ax)], 1)
            Rm = Wb @ Lb.T
            ctr = Cs[i] + ex * rng.uniform(-2.5, 2.5)
            nucs.append((ctr, Rm))
        # DNA path: wrap k, linker k→k+1
        wraps = [(sh @ Rm.T + c) for c, Rm in nucs]
        wraps_d = [(sh_dense @ Rm.T + c) for c, Rm in nucs]
        links = []
        for k in range(len(nucs) - 1):
            p0, p1 = wraps[k][-1], wraps[k + 1][0]
            t0 = nucs[k][1] @ t_out
            t1 = nucs[k + 1][1] @ t_in
            d = np.linalg.norm(p1 - p0)
            links.append(hermite(p0, t0 * d * 1.1, p1, t1 * d * 1.1, 64))
        is_hero = f == HERO_FIBRE
        for k, (c, Rm) in enumerate(nucs):
            skip = is_hero and k == HERO_NUC
            if not skip:
                for b, kd in zip(blobs, bkind):
                    hist.append([*(Rm @ b + c), 2.05, kd, f])
                for p in wraps_d[k]:
                    beads.append([*p, f])
        for k, Lk in enumerate(links):
            if is_hero and k in (HERO_NUC - 1, HERO_NUC):
                continue
            P, _ = resample(Lk, 0.8)
            for p in P[1:-1]:
                beads.append([*p, f])
        if is_hero:
            k = HERO_NUC
            lin_in, _ = resample(links[k - 1], RISE)
            lin_out, _ = resample(links[k], RISE)
            wrap = wraps[k]
            P = np.vstack([lin_in[:-1], wrap, lin_out[1:]])
            wa, wb = len(lin_in) - 1, len(lin_in) - 1 + NUC_BP - 1
            hero = dict(P=P, wa=wa, wb=wb, ctr=nucs[k][0], R=nucs[k][1], curve=Cs,
                        curve_idx=int(30 + k * NUC_SPACING))
    beads = np.array(beads)
    hist = np.array(hist)
    # arc phase for the groove stripes on LOD beads
    phase = (np.arange(len(beads)) * 0.8 / PITCH) % 1.0
    return dict(beads=np.column_stack([beads[:, :3], phase, beads[:, 3]]), hist=hist, hero=hero)


# ── hero DNA: unwrap (re-integrate the turning with reduced curvature) ──────
class HeroDNA:
    def __init__(self, hero, seq=HBB):
        self.P0 = P = hero["P"]
        self.n = len(P)
        assert self.n <= len(seq), "hero DNA longer than the HBB coding sequence"
        self.seq = seq[: self.n]
        self.wa, self.wb = hero["wa"], hero["wb"]
        self.ctr0, self.R0 = hero["ctr"], hero["R"]
        T, N = transport_frames(P)
        B = np.cross(T, N)
        self.F = np.stack([T, N, B], -1)                       # columns: T N B
        self.L = np.r_[np.linalg.norm(np.diff(P, axis=0), axis=1), RISE]
        # relative rotation i → i+1 in the local frame of i (so it can be re-applied to a new frame)
        self.Q = np.einsum("nji,njk->nik", self.F[:-1], self.F[1:])   # F_i^T F_{i+1}
        ang = np.arccos(np.clip((np.trace(self.Q, axis1=1, axis2=2) - 1) / 2, -1, 1))
        axis = np.stack([self.Q[:, 2, 1] - self.Q[:, 1, 2], self.Q[:, 0, 2] - self.Q[:, 2, 0],
                         self.Q[:, 1, 0] - self.Q[:, 0, 1]], 1)
        nrm = np.linalg.norm(axis, axis=1, keepdims=True)
        self.qax = np.where(nrm > 1e-12, axis / np.maximum(nrm, 1e-12), [1, 0, 0])
        self.qang = ang
        self.T0, self.N0 = T[0], N[0]
        self.B0 = np.cross(self.T0, self.N0)

    def centreline(self, front):
        """front ∈ [0, 1]: 0 = wrapped, 1 = fully straight. Returns P, F (frames), histone rigid transform."""
        n, wa, wb = self.n, self.wa, self.wb
        fi = wa + front * (n - 1 - wa + 8)
        i = np.arange(n - 1)
        w = np.clip((fi - i) / 8.0, 0, 1)
        u = np.clip(front / 0.12, 0, 1)
        w[:wa] = u * u * (3 - 2 * u)                         # the incoming linker straightens first
        Q = rot(self.qax, self.qang * (1 - w))
        P = np.empty((n, 3))
        F = np.empty((n, 3, 3))
        P[0], F[0] = self.P0[0], self.F[0]
        for k in range(n - 1):
            F[k + 1] = F[k] @ Q[k]
            P[k + 1] = P[k] + F[k][:, 0] * self.L[k]
        kk = int(np.clip(round(fi), wa, wb))
        M = F[kk] @ self.F[kk].T
        hist_ctr = P[kk] + M @ (self.ctr0 - self.P0[kk])
        return P, F, M, hist_ctr, fi > wb + 2


def assert_physics():
    assert translate(HBB) == HBB_PROTEIN + "*", "HBB coding sequence does not translate to beta-globin"
    assert len(HBB_PROTEIN) == 147
    assert abs(np.rad2deg(TWIST) - 34.29) < 0.01 and abs(PITCH - 3.549) < 0.01
    # B-DNA handedness: helix c + R(cosφ N + sinφ B) with B = T×N and φ increasing along T is right-handed
    T, N = np.array([0, 0, 1.0]), np.array([1.0, 0, 0])
    B = np.cross(T, N)
    ph = np.arange(4) * TWIST
    h = R_P * (np.cos(ph)[:, None] * N + np.sin(ph)[:, None] * B) + (np.arange(4) * RISE)[:, None] * T
    d1, d2, d3 = np.diff(h, 1, 0)[0], np.diff(h, 2, 0)[0], np.diff(h, 3, 0)[0]
    assert np.dot(np.cross(d1, d2), d3) > 0, "B-DNA must be right-handed"
    # grooves: axial gaps between the two backbones (minor < major)
    minor = PITCH * GROOVE / (2 * np.pi)
    assert minor < PITCH - minor
    # nucleosome: 147 bp, 1.65 turns, left-handed
    s = superhelix()
    assert len(s) == NUC_BP
    d1, d2, d3 = np.diff(s, 1, 0)[0], np.diff(s, 2, 0)[0], np.diff(s, 3, 0)[0]
    assert np.dot(np.cross(d1, d2), d3) < 0, "nucleosome superhelix must be left-handed"
    turns = (np.unwrap(np.arctan2(s[:, 1], s[:, 0]))[-1] - np.arctan2(s[0, 1], s[0, 0])) / (2 * np.pi)
    assert abs(turns - SH_TURNS) < 1e-6
    return dict(minor_groove_axial=minor, major_groove_axial=PITCH - minor,
                wrap_rise=np.linalg.norm(np.diff(s, axis=0), axis=1).mean())


PHYS = assert_physics()

if __name__ == "__main__":
    import time
    t0 = time.time()
    C = build_chromatin()
    h = C["hero"]
    print(f"HBB: {len(HBB)} nt → {translate(HBB)[:20]}…  (beta-globin, {len(HBB_PROTEIN)} aa) ✓")
    print(f"B-DNA: {BP_PER_TURN} bp/turn, twist {np.rad2deg(TWIST):.2f}°, pitch {PITCH:.2f} nm, "
          f"grooves (axial) minor {PHYS['minor_groove_axial']:.2f} / major {PHYS['major_groove_axial']:.2f} nm")
    print(f"nucleosome: {NUC_BP} bp, {SH_TURNS} left-handed turns, R {SH_R} nm, wrap rise {PHYS['wrap_rise']:.3f} nm")
    print(f"chromatin: {len(C['beads'])} DNA beads, {len(C['hist'])} histone spheres, "
          f"hero DNA {len(h['P'])} bp (wrap {h['wa']}..{h['wb']})  [{time.time() - t0:.1f}s]")
    H = HeroDNA(h)
    P, *_ = H.centreline(0.0)
    assert np.abs(P - H.P0).max() < 1e-6, "unwrap(0) must reproduce the wrapped DNA"
    for f in (0, 0.5, 1.0):
        P, F, M, hc, free = H.centreline(f)
        ext = np.linalg.norm(P[-1] - P[0])
        print(f"  unwrap {f:.1f}: end-to-end {ext:6.1f} nm (contour {H.L[:-1].sum():.1f}), histone free={free}")
