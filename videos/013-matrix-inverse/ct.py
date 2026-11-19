"""The key rebuilt from its shadows: real least-squares reconstructions, baked once into out/ct_recon.npz.

    uv run python videos/013-matrix-inverse/ct.py      # bake (a minute or two)
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
import scipy.sparse.linalg as spla
from PIL import Image

from verify import CT_ANGLES, ct_matrix, key_raster

HERE = Path(__file__).resolve().parent
BAKED = HERE / "out" / "ct_recon.npz"
N = 96


def bake():
    truth = key_raster(N)
    out, errs = {}, {}
    for k in CT_ANGLES:
        M = ct_matrix(N, k)
        x = spla.lsqr(M, M @ truth.ravel(), atol=1e-8, btol=1e-8, iter_lim=1500)[0].reshape(N, N)
        out[f"k{k}"] = x
        errs[k] = float(np.linalg.norm(x - truth) / np.linalg.norm(truth))
        print(f"{k:4d} angles: error {errs[k]:.1%}", flush=True)
    BAKED.parent.mkdir(exist_ok=True)
    np.savez_compressed(BAKED, **out)


@lru_cache(maxsize=None)
def recon(k):
    """The key as solved from `k` angles, turned to lie along the shaft direction of the hero key, as a 0-1 image with row 0 at the top."""
    if not BAKED.exists():
        bake()
    x = np.clip(np.load(BAKED)[f"k{k}"], 0, 1)
    img = Image.fromarray((np.flipud(x) * 255).astype(np.uint8)).resize((480, 480), Image.BICUBIC)
    return np.asarray(img.rotate(float(np.degrees(np.arctan2(1.0, 2.0))), Image.BICUBIC), float) / 255


if __name__ == "__main__":
    bake()
