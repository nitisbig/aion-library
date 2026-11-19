"""Every number and claim in video 013, computed. Scenes import CAST from here; nothing on screen is typed by hand.

    uv run python videos/013-matrix-inverse/verify.py          # all checks (about a minute)
    uv run python videos/013-matrix-inverse/verify.py --fast   # skips the CT reconstruction
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import sympy as sy
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# ---------------------------------------------------------------- the cast
A = np.array([[3.0, 1.0], [2.0, 2.0]])                  # hero matrix (same as video 009), det 4
A_INV = np.array([[0.5, -0.25], [-0.5, 0.75]])
S = np.array([[3.0, 1.5], [2.0, 1.0]])                  # A with its 2nd column tilted onto the 1st: det 0
NULL = np.array([1.0, -2.0])                            # S kills this direction: the light rays
SHAFT = np.array([2.0, 1.0]) / np.sqrt(5.0)             # the key lies along this, perpendicular to the rays
TOOTH = np.array([1.0, -2.0]) / np.sqrt(5.0)            # teeth point along the rays

# The rewind (row operations, in the order they are applied to the bent plane)
E = [np.array([[1.0, -1.0], [0.0, 1.0]]),               # slide: R1 -= R2
     np.array([[1.0, 0.0], [-2.0, 1.0]]),               # slide: R2 -= 2 R1
     np.array([[1.0, 0.0], [0.0, 0.25]]),               # squash: R2 /= 4
     np.array([[1.0, 1.0], [0.0, 1.0]])]                # slide: R1 += R2

# The four moves of the cold open: the rewind, inverted and reversed
HOOK = [np.linalg.inv(m) for m in reversed(E)]

SIMPLE = {"turn": (np.array([[np.cos(np.pi / 6), -np.sin(np.pi / 6)], [np.sin(np.pi / 6), np.cos(np.pi / 6)]]),
                   np.array([[np.cos(np.pi / 6), np.sin(np.pi / 6)], [-np.sin(np.pi / 6), np.cos(np.pi / 6)]])),
          "stretch": (np.diag([2.0, 3.0]), np.diag([0.5, 1 / 3])),
          "slide": (np.array([[1.0, 1.0], [0.0, 1.0]]), np.array([[1.0, -1.0], [0.0, 1.0]]))}

LEAN = np.array([[1.0, 1.0], [0.0, 1.0]])               # the chain: lean, then a quarter turn
TURN = np.array([[0.0, -1.0], [1.0, 0.0]])


def tilt(s: float) -> np.ndarray:
    """A(s): the second column slides from (1, 2) to (3/2, 1). A(0) = A, A(1) = S, det A(s) = 4(1 - s)."""
    return np.array([[3.0, 1.0 + 0.5 * s], [2.0, 2.0 - s]])


POWDER = np.array([[3.0, 1.0], [2.0, 2.0]])             # columns = grams per scoop (protein, fibre)
TARGET = np.array([7.0, 6.0])
SCOOPS = np.array([2.0, 1.0])
WEAK = S.copy()                                         # second powder exactly half as strong as the first

DRONE = np.array([[2.0, -1.0], [1.0, 2.0]])             # the drone's axes, written on the map's grid
SEEN = np.array([2.0, 1.0])                             # the landmark, in the drone's own steps
MAPPED = np.array([3.0, 4.0])                           # the landmark, on the map

TEETH = (1, -1, 1, 1)                                   # the hero key: tooth up (+1) or down (-1), base to tip
CT_ANGLES = (1, 2, 4, 8, 16, 32, 64, 128)
BLUR_LEN = 49                                           # a steady camera shake: each pixel averages 49 neighbours
BLUR_KEEP = 0.06                                        # stop short: undo only the directions that kept this much

CAST = dict(A=A, A_INV=A_INV, S=S, NULL=NULL, SHAFT=SHAFT, TOOTH=TOOTH, E=E, HOOK=HOOK, SIMPLE=SIMPLE, LEAN=LEAN,
            TURN=TURN, POWDER=POWDER, TARGET=TARGET, SCOOPS=SCOOPS, WEAK=WEAK, DRONE=DRONE,
            SEEN=SEEN, MAPPED=MAPPED, TEETH=TEETH, CT_ANGLES=CT_ANGLES, BLUR_LEN=BLUR_LEN, BLUR_KEEP=BLUR_KEEP)

# ---------------------------------------------------------------- the key (key frame: shaft on the x axis)
KEY_LEN = 3.0


def key_polys(teeth=TEETH):
    """The key as polygons in its own frame: (bow outer, bow hole, [shaft + teeth]). Symmetric about the shaft line."""
    th = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    bow = np.c_[-1.05 + 0.45 * np.cos(th), 0.45 * np.sin(th)]
    hole = np.c_[-1.05 + 0.2 * np.cos(th), 0.2 * np.sin(th)]
    shaft = np.array([[-0.65, -0.08], [1.5, -0.08], [1.5, 0.08], [-0.65, 0.08]])
    tooth = []
    for i, sign in enumerate(teeth):
        x0 = 0.42 + 0.27 * i
        tooth.append(np.array([[x0, 0.08 * sign], [x0 + 0.17, 0.08 * sign], [x0 + 0.17, 0.42 * sign], [x0, 0.42 * sign]]))
    return bow, hole, [shaft, *tooth]


def key_raster(n: int, teeth=TEETH, angle: float = 0.0, half: float = 1.9) -> np.ndarray:
    """A 0/1 raster of the key on an n x n grid spanning [-half, half]^2, turned by `angle`, 8x supersampled."""
    ss = 8
    img = Image.new("L", (n * ss, n * ss), 0)
    draw = ImageDraw.Draw(img)
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])

    def px(p):
        q = (R @ (p - np.array([0.2, 0.0])).T).T
        return [tuple(v) for v in (q + half) / (2 * half) * (n * ss)]

    bow, hole, rest = key_polys(teeth)
    draw.polygon(px(bow), fill=255)
    draw.polygon(px(hole), fill=0)
    for poly in rest:
        draw.polygon(px(poly), fill=255)
    return np.asarray(img.resize((n, n), Image.BOX), dtype=float) / 255.0


# ---------------------------------------------------------------- CT system
def ct_matrix(n: int, k: int, start: float = np.arctan2(-2.0, 1.0)) -> sp.csr_matrix:
    """Parallel-beam projection of an n x n image from k angles over a half turn (linear detector splat)."""
    bins = int(np.ceil(n * 1.5))
    ys, xs = np.mgrid[0:n, 0:n]
    x = (xs.ravel() + 0.5 - n / 2).astype(float)
    y = (ys.ravel() + 0.5 - n / 2).astype(float)
    pix = np.arange(n * n)
    rows, cols, vals = [], [], []
    for j in range(k):
        th = start + np.pi * j / k
        u = x * np.sin(th) - y * np.cos(th) + bins / 2 - 0.5                # position across the rays
        lo = np.floor(u).astype(int)
        w = u - lo
        rows += [j * bins + lo, j * bins + lo + 1]
        cols += [pix, pix]
        vals += [1 - w, w]
    M = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(k * bins, n * n))
    return M.tocsr()


# ---------------------------------------------------------------- checks
_fails = 0


def check(name: str, ok: bool, note: str = "") -> None:
    global _fails
    _fails += 0 if ok else 1
    print(f"{'ok ' if ok else 'FAIL'} {name}" + (f"   [{note}]" if note else ""))


def same(a, b, tol=1e-9) -> bool:
    return bool(np.allclose(a, b, atol=tol, rtol=0))


def main(fast: bool = False) -> int:
    I = np.eye(2)
    print("-- hero matrix and the rewind")
    check("det A = 4", same(np.linalg.det(A), 4))
    check("A^-1 A = I and A A^-1 = I", same(A_INV @ A, I) and same(A @ A_INV, I))
    state, record = A.copy(), I.copy()
    log = []
    for m in E:
        state, record = m @ state, m @ record
        log.append((state.copy(), record.copy()))
    check("the four moves take A to I", same(state, I))
    check("the same four moves take I to A^-1", same(record, A_INV))
    check("first arrow is home after move 2", same(log[1][0][:, 0], [1, 0]))
    check("second arrow stands 4 tall after move 2", same(log[1][0][:, 1], [-1, 4]))
    check("second arrow is home after move 4", same(log[3][0][:, 1], [0, 1]))
    prod = I.copy()
    for m in HOOK:
        prod = m @ prod
    check("the cold open's four moves multiply to A", same(prod, A))
    check("three slides keep area, the squash is 1/4", same([np.linalg.det(m) for m in E], [1, 1, 0.25, 1]))
    check("det A^-1 = 1 / det A", same(np.linalg.det(A_INV), 0.25))
    a, b, c, d = sy.symbols("a b c d")
    M = sy.Matrix([[a, b], [c, d]])
    check("2x2 formula", sy.simplify(M.inv() - sy.Matrix([[d, -b], [-c, a]]) / (a * d - b * c)) == sy.zeros(2))
    fr = [[Fr(1, 2), Fr(-1, 4)], [Fr(-1, 2), Fr(3, 4)]]
    pr = [[fr[i][0] * x + fr[i][1] * y for x, y in ((3, 2), (1, 2))] for i in range(2)]
    check("exact product is the identity", pr == [[1, 0], [0, 1]], str(pr))

    print("-- simple moves and the wrong rule")
    for name, (m, back) in SIMPLE.items():
        check(f"{name}: way back works", same(back @ m, I) and same(m @ back, I))
    check("the slide has a zero entry yet an inverse", (SIMPLE["slide"][0] == 0).any() and abs(np.linalg.det(SIMPLE["slide"][0])) > 0)
    check("S has no zero entry yet no inverse", (S != 0).all() and abs(np.linalg.det(S)) < 1e-12)
    flipped = 1 / A
    check("flipping every entry of A does not invert it", not same(flipped @ A, I))

    print("-- chains")
    chain = TURN @ LEAN
    check("right order: undo the turn first", same(np.linalg.inv(LEAN) @ np.linalg.inv(TURN) @ chain, I))
    wrong = np.linalg.inv(TURN) @ np.linalg.inv(LEAN) @ chain
    check("wrong order does not come home", not same(wrong, I), f"lands on {wrong.tolist()}")

    print("-- the collapse")
    check("S kills the ray direction", same(S @ NULL, [0, 0]))
    check("first column of S is twice the second", same(S[:, 0], 2 * S[:, 1]))
    check("A and S share a first column", same(A[:, 0], S[:, 0]))
    check("rank S = 1", np.linalg.matrix_rank(S) == 1)
    check("det A(s) = 4(1 - s)", all(abs(np.linalg.det(tilt(s)) - 4 * (1 - s)) < 1e-9 for s in np.linspace(0, 1, 11)))
    check("A(1) = S", same(tilt(1.0), S))
    stretch = {}
    for goal in (10, 100, 1000):
        lo, hi = 0.0, 1.0 - 1e-9
        for _ in range(80):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if 1 / np.linalg.svd(tilt(mid), compute_uv=False)[-1] < goal else (lo, mid)
        stretch[goal] = lo
    check("the inverse must stretch 10x, 100x, 1000x as s nears 1", all(0 < v < 1 for v in stretch.values()),
          ", ".join(f"{g}x at s={v:.4f}" for g, v in stretch.items()))
    u, v = np.array([1.0, 1.0]), np.array([1.0, 1.0]) + 2.5 * NULL
    check("two points on a ray land together", same(S @ u, S @ v))
    check("the straight path from A to I never collapses", min(np.linalg.det((1 - s) * A + s * I) for s in np.linspace(0, 1, 201)) > 0.9)

    print("-- sixteen keys, one shadow")
    profiles = []
    for bits in range(16):
        t = tuple(1 if bits >> i & 1 else -1 for i in range(4))
        profiles.append(key_raster(760, t).sum(axis=0))                     # rays run along the teeth (image y)
    spread = max(np.abs(p - profiles[0]).max() for p in profiles)
    distinct = len({key_raster(190, tuple(1 if b >> i & 1 else -1 for i in range(4))).tobytes() for b in range(16)})
    check("all 16 tooth patterns are different keys", distinct == 16)
    check("all 16 cast an identical shadow, shade for shade", spread < 1e-6, f"max difference {spread:.2e} pixels")
    p = np.array([0.7, 0.3])
    check("a tooth flipped along the rays lands on the same points", same(S @ (p + 0.8 * TOOTH), S @ (p - 0.8 * TOOTH)))

    print("-- equations")
    check("two scoops and one scoop make the target", same(POWDER @ SCOOPS, TARGET) and same(A_INV @ TARGET, SCOOPS))
    check("weak powder is half the first", same(WEAK[:, 1], WEAK[:, 0] / 2))
    on_line = np.array([6.0, 4.0])
    recipes = [(2, 0), (1, 2), (0, 4)]
    check("a target on the line has many recipes", all(same(WEAK @ np.array(r, float), on_line) for r in recipes))
    aug = np.c_[WEAK, TARGET]
    check("a target off the line has none", np.linalg.matrix_rank(aug) > np.linalg.matrix_rank(WEAK))

    print("-- coordinates and the camera")
    check("drone to map", same(DRONE @ SEEN, MAPPED))
    check("map to drone", same(np.linalg.inv(DRONE) @ MAPPED, SEEN))
    th = 0.6
    cam = np.eye(4)
    cam[:3, :3] = [[np.cos(th), 0, np.sin(th)], [0, 1, 0], [-np.sin(th), 0, np.cos(th)]]
    cam[:3, 3] = [4, 2, 7]
    view = np.linalg.inv(cam)
    check("the view matrix carries the camera to the origin", same(view @ cam[:, 3], [0, 0, 0, 1]))
    step = np.eye(4)
    step[2, 3] = -1.0                                                       # one step forward (camera looks down -z)
    p_world = np.array([1.0, 0.5, -2.0, 1.0])
    before, after = view @ p_world, np.linalg.inv(cam @ step) @ p_world
    check("walking forward carries the world backward", same(after - before, [0, 0, 1, 0]))

    print("-- the blurred picture")
    photo = np.asarray(Image.open(REPO / "videos/009-what-matrices-are/assets/photo.png").convert("L"), float) / 255
    k = np.ones(BLUR_LEN) / BLUR_LEN
    K = np.fft.fft(k, photo.shape[1])
    blur = np.real(np.fft.ifft(np.fft.fft(photo, axis=1) * K, axis=1))
    back = np.real(np.fft.ifft(np.fft.fft(blur, axis=1) / K, axis=1))
    cond = np.abs(K).max() / np.abs(K).min()
    psnr = lambda x: 10 * np.log10(1 / np.mean((np.clip(x, 0, 1) - photo) ** 2))
    gen = np.random.default_rng(13)
    noise = gen.normal(0, 0.004, photo.shape)
    noisy = blur + noise
    naive = np.real(np.fft.ifft(np.fft.fft(noisy, axis=1) / K, axis=1))
    keep = np.abs(K) > BLUR_KEEP
    trunc = np.real(np.fft.ifft(np.where(keep, np.fft.fft(noisy, axis=1) / K, 0), axis=1))
    check("the blur matrix is invertible", np.abs(K).min() > 0, f"smallest stretch {np.abs(K).min():.4f}, condition {cond:.0f}")
    check("exact inverse restores the picture", np.abs(back - photo).max() < 1e-9)
    check("the blur visibly damages the picture", psnr(blur) < 26, f"blurred PSNR {psnr(blur):.1f} dB")
    check("noise is too faint to see", np.abs(noisy - blur).std() < 0.005, f"std {noise.std() * 255:.2f} of 255 grey levels")
    check("the full inverse drowns the picture in that noise", psnr(naive) < psnr(blur) - 5,
          f"error std grows {(naive - photo).std() / noise.std():.1f}x, PSNR {psnr(naive):.1f} dB")
    check("stopping short recovers most of the picture", psnr(trunc) > psnr(blur) + 8,
          f"keeps {keep.mean():.0%} of the directions, PSNR {psnr(trunc):.1f} dB")

    if fast:
        print("-- CT skipped (--fast)")
    else:
        print("-- shadows from many angles")
        n = 22
        ranks = {}
        for kk in (1, 2, 4, 8, 16, 32):
            ranks[kk] = int(np.linalg.matrix_rank(ct_matrix(n, kk).toarray()))
        check("every new set of angles forgets less", all(a <= b for a, b in zip(list(ranks.values()), list(ranks.values())[1:])), str(ranks))
        check("enough angles forget nothing", ranks[32] == n * n, f"rank {ranks[32]} of {n * n}")
        check("one shadow forgets most of the picture", ranks[1] < n * n / 2, f"rank {ranks[1]} of {n * n}")
        n = 96
        truth = key_raster(n)
        errs = {}
        for kk in CT_ANGLES:
            M = ct_matrix(n, kk)
            x = spla.lsqr(M, M @ truth.ravel(), atol=1e-8, btol=1e-8, iter_lim=1500)[0].reshape(n, n)
            errs[kk] = float(np.linalg.norm(x - truth) / np.linalg.norm(truth))
        vals = list(errs.values())
        check("the error shrinks as angles are added", all(a >= b - 1e-3 for a, b in zip(vals, vals[1:])),
              ", ".join(f"{a}: {e:.0%}" for a, e in errs.items()))
        check("128 shadows bring the key back", errs[128] < 0.01, f"error {errs[128]:.1%}")
        up, down = key_raster(n, (1, 1, 1, 1)), key_raster(n, (-1, 1, 1, 1))
        M1, M2 = ct_matrix(n, 1, 0.0), ct_matrix(n, 2, 0.0)
        check("a second angle tells a flipped tooth apart", np.abs(M2 @ (up - down).ravel()).max() > 10 * np.abs(M1 @ (up - down).ravel()).max() + 1e-6 or np.abs(M2 @ (up - down).ravel()).max() > 1)

    print(f"\n{'ALL CHECKS PASSED' if not _fails else str(_fails) + ' CHECKS FAILED'}")
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(main("--fast" in sys.argv))
