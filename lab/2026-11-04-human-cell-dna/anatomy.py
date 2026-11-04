"""Human cell layout in micrometres. Seeded, and asserted against real size ranges on import.

    uv run python lab/2026-11-04-human-cell-dna/anatomy.py
"""

from __future__ import annotations

import numpy as np

CELL_R = 10.0                         # ~20 µm cell
CELL_SQUASH = (1.0, 0.80, 0.94)
NUC_C = np.array([0.6, 0.25, -0.3])
NUC_R = 3.5                           # ~7 µm nucleus
ENVELOPE_GAP = 0.04                   # 40 nm perinuclear space between the two membranes
PORE_R = 0.06                         # ~120 nm nuclear pore complex
PORE_SPACING = float(np.sqrt(4 * np.pi / 2000))   # ~2000 pores over the envelope (radians)
NUCLEOLUS = np.array([[1.3, 0.9, 0.2, 0.95], [-0.9, -0.4, 0.8, 0.6]])   # centre (rel. nucleus) + radius
GOLGI_DIR = np.array([-0.75, 0.35, 0.56])
GOLGI_N = 6
CENTROSOME = NUC_C + (GOLGI_DIR / np.linalg.norm(GOLGI_DIR)) * (NUC_R + 1.2) + np.array([0.0, -0.9, 0.3])
N_MITO, N_VES, N_MT = 14, 26, 22
HERO_PORE = (14, 3)                   # (row, column) of the pore the camera flies through


def _u(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def inside_cell(p, margin):
    q = (p) / np.array(CELL_SQUASH)
    return np.linalg.norm(q) < CELL_R - margin


def pore_lattice(row, col):
    """Same integer-hash lattice as cell.frag: rows of constant latitude, jittered. Returns the unit direction."""
    h = PORE_SPACING
    nrows = int(np.floor(np.pi / h))
    lat = -np.pi / 2 + (row + 0.5) * np.pi / nrows
    ncol = max(int(np.floor(2 * np.pi * np.cos(lat) / h)), 1)
    hsh = ((row * 73856093) ^ (col * 19349663)) & 1023
    jit = (hsh / 1023.0 - 0.5) * 0.5
    lon = (col + 0.5 + jit + 0.5 * (row % 2)) * 2 * np.pi / ncol
    jlat = (((((col * 83492791) ^ (row * 2654435)) & 1023) / 1023.0) - 0.5) * 0.4 * np.pi / nrows
    lat = lat + jlat
    return np.array([np.cos(lat) * np.cos(lon), np.sin(lat), np.cos(lat) * np.sin(lon)])


def layout(seed=7):
    rng = np.random.default_rng(seed)
    g = _u(GOLGI_DIR)
    # mitochondria: capsules (a, b, radius) in the cytoplasm, not overlapping, away from nucleus and Golgi
    mito = []
    while len(mito) < N_MITO:
        c = rng.uniform(-9, 9, 3) * CELL_SQUASH
        if not inside_cell(c, 2.0) or np.linalg.norm(c - NUC_C) < NUC_R + 1.6:
            continue
        if np.linalg.norm(c - (NUC_C + g * (NUC_R + 2.5))) < 2.6:
            continue
        r = rng.uniform(0.25, 0.4)
        half = rng.uniform(0.6, 1.4)
        d = _u(rng.normal(size=3))
        a, b = c - d * half, c + d * half
        if not (inside_cell(a, 1.0 + r) and inside_cell(b, 1.0 + r)):
            continue
        if any(np.linalg.norm(c - (m[:3] + m[4:7]) / 2) < 2.0 for m in mito):
            continue
        mito.append(np.r_[a, r, b, rng.uniform(0, 1)])
    ves = []
    while len(ves) < N_VES:
        c = rng.uniform(-9, 9, 3) * CELL_SQUASH
        r = rng.uniform(0.12, 0.45)
        if not inside_cell(c, 1.0 + r) or np.linalg.norm(c - NUC_C) < NUC_R + 0.6 + r:
            continue
        if any(np.linalg.norm(c - (m[:3] + m[4:7]) / 2) < 1.6 + r for m in mito):
            continue
        if any(np.linalg.norm(c - v[:3]) < v[3] + r + 0.3 for v in ves):
            continue
        kind = 1.0 if r > 0.3 else 0.0                  # 1 = lysosome, 0 = transport vesicle
        ves.append(np.r_[c, r, kind, rng.uniform(0, 1), 0, 0])
    # microtubules from the centrosome to points under the membrane
    mt = []
    for _ in range(N_MT):
        d = _u(rng.normal(size=3))
        for s in np.linspace(CELL_R * 1.3, 1.0, 60):
            e = CENTROSOME + d * s
            if inside_cell(e, 0.7):
                break
        mt.append(np.r_[e, rng.uniform(0, 1)])
    return dict(mito=np.array(mito, "f4"), ves=np.array(ves, "f4"), mt=np.array(mt, "f4"))


def hero_pore():
    d = pore_lattice(*HERO_PORE)
    return NUC_C + d * NUC_R, d


def assert_anatomy(L):
    assert 5 <= 2 * NUC_R <= 10, "nucleus 5–10 µm"
    assert 10 <= 2 * CELL_R <= 30, "cell 10–30 µm"
    assert 0.1 <= 2 * PORE_R <= 0.13, "nuclear pore ~120 nm"
    area = 4 * np.pi * NUC_R**2
    n_pores = 4 * np.pi / PORE_SPACING**2
    assert 1500 <= n_pores <= 5000, n_pores
    for m in L["mito"]:
        w, length = 2 * m[3], np.linalg.norm(m[:3] - m[4:7]) + 2 * m[3]
        assert 0.5 <= w <= 1.0 and 1.0 <= length <= 3.5, (w, length)
    for v in L["ves"]:
        assert 0.1 <= 2 * v[3] <= 1.2
    return dict(pores=n_pores, pore_density=n_pores / area)


LAYOUT = layout()
INFO = assert_anatomy(LAYOUT)

if __name__ == "__main__":
    print(f"cell Ø {2 * CELL_R} µm, nucleus Ø {2 * NUC_R} µm, {INFO['pores']:.0f} pores "
          f"({INFO['pore_density']:.1f}/µm²), {N_MITO} mitochondria, {N_VES} vesicles/lysosomes, {N_MT} microtubules")
    p, d = hero_pore()
    print("hero pore at", np.round(p, 3), "normal", np.round(d, 3))
