"""Vector mini-diagrams (one per move) and the SVD layer strip for the ebook, all computed from the real math.

    uv run python videos/009-what-matrices-are/ebook/gen_figs.py
"""
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
FIG = HERE / "figs"
IH, JH, GRID, MINOR, AXIS, GHOST = "#83c167", "#fc6255", "#2b6f99", "#173a52", "#e8e8e8", "#3a3a3a"
NULL, VEC, SIG = "#ff4fa3", "#ffe94a", "#5cd0b3"
S, R = 220, 2.6          # pixels, half-range in units


def px(p):
    return S / 2 + p[0] * S / (2 * R), S / 2 - p[1] * S / (2 * R)


def line(a, b, col, w, op=1.0, dash=""):
    (x1, y1), (x2, y2) = px(a), px(b)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" '
            f'stroke-opacity="{op}" stroke-linecap="round"{d}/>')


def arrow(v, col, w=3.2):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    if n < 1e-9:
        x, y = px((0, 0))
        return f'<circle cx="{x}" cy="{y}" r="4" fill="{col}"/>'
    u = v / n
    h = min(0.32, 0.45 * n)
    base = v - u * h
    perp = np.array([-u[1], u[0]]) * h * 0.5
    pts = " ".join("{:.1f},{:.1f}".format(*px(p)) for p in (v, base + perp, base - perp))
    return line((0, 0), base, col, w) + f'<polygon points="{pts}" fill="{col}"/>'


def mini(M, name, extra=""):
    M = np.asarray(M, float)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">',
           f'<defs><clipPath id="c"><rect width="{S}" height="{S}" rx="10"/></clipPath></defs><g clip-path="url(#c)">',
           f'<rect width="{S}" height="{S}" fill="#000"/>']
    for k in range(-3, 4):                                    # the untouched grid, faint
        out.append(line((k, -R), (k, R), GHOST, 0.8, 0.6))
        out.append(line((-R, k), (R, k), GHOST, 0.8, 0.6))
    L = 9
    for k2 in range(-2 * L, 2 * L + 1):                       # the moved grid
        k = k2 / 2
        minor = k2 % 2 != 0
        col = MINOR if minor else (AXIS if k == 0 else GRID)
        w = 0.8 if minor else (1.6 if k == 0 else 1.1)
        out.append(line(M @ [k, -L], M @ [k, L], col, w))
        out.append(line(M @ [-L, k], M @ [L, k], col, w))
    out.append(extra)
    out.append(arrow(M[:, 0], IH))
    out.append(arrow(M[:, 1], JH))
    out.append("</g></svg>")
    (FIG / f"mini_{name}.svg").write_text("\n".join(out))


def svd_strip():
    g = np.asarray(Image.open(HERE.parent / "assets" / "photo.png").convert("L"), float) / 255
    U, s, Vt = np.linalg.svd(g)
    for k in (1, 2, 5, 10, 30):
        a = np.clip((U[:, :k] * s[:k]) @ Vt[:k], 0, 1)
        Image.fromarray((a * 255).round().astype(np.uint8)).save(FIG / f"svd_k{k}.png")
    Image.fromarray((g * 255).round().astype(np.uint8)).save(FIG / "svd_full.png")
    n = g.shape[0]
    print("photo", g.shape, "k=30 share", 30 * (2 * n + 1) / g.size, "energy30", (s[:30] ** 2).sum() / (s ** 2).sum())


def main():
    FIG.mkdir(exist_ok=True)
    th = np.radians(35)
    mini([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]], "rotate")
    mini([[1.6, 0], [0, 0.6]], "stretch")
    mini([[1, 1], [0, 1]], "shear")
    mini([[-1, 0], [0, 1]], "flip")
    mini([[1, 0], [0, 0]], "squash")
    mini([[0, -1], [1, 0]], "quarter")
    mini([[3, 1], [2, 2]] , "hero_raw")
    A = np.array([[3, 1], [2, 2]]) / 2.2                      # scaled so it fits the tile
    mini(A, "hero")
    mini([[0, -1], [1, 1]], "rsh")
    mini([[1, -1], [1, 0]], "shr")
    # collapse: null space (pink) and column space (white dashed)
    C = np.array([[2, 1], [2, 1]]) / 2.0
    ex = line((-1.3, 2.6), (1.3, -2.6), NULL, 2.4, 0.9, "6 5")
    mini(C, "collapse", ex)
    # eigen: hero A with its two eigen-directions
    ex = (line((-3, -3), (3, 3), "#b78cf2", 2.0, 0.8, "5 5") + line((-1.5, 3), (1.5, -3), "#b78cf2", 2.0, 0.8, "5 5"))
    mini(A, "eigen", ex)
    svd_strip()


if __name__ == "__main__":
    main()


def power_panels():
    """A cloud of points under A, A^2, A^3 (rescaled each round): it lines up with the eigenvector (1, 1)."""
    rng = np.random.default_rng(9)
    P = rng.normal(size=(260, 2)) * [1.0, 1.0]
    A = np.array([[3, 1], [2, 2]], float)
    for k in range(4):
        Q = P @ np.linalg.matrix_power(A, k).T
        Q = Q / np.abs(Q).max() * 2.2
        dots = "".join('<circle cx="{:.1f}" cy="{:.1f}" r="2.3" fill="#ffe94a" fill-opacity=".85"/>'.format(*px(q))
                       for q in Q)
        ex = (line((-3, -3), (3, 3), "#b78cf2", 1.6, 0.8, "5 5") + dots)
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">',
               f'<rect width="{S}" height="{S}" rx="10" fill="#000"/>']
        for j in range(-2, 3):
            svg.append(line((j, -R), (j, R), "#1d1d22", 1))
            svg.append(line((-R, j), (R, j), "#1d1d22", 1))
        svg += [line((-R, 0), (R, 0), "#555", 1.2), line((0, -R), (0, R), "#555", 1.2), ex, "</svg>"]
        (FIG / f"power_{k}.svg").write_text("\n".join(svg))


if __name__ == "__main__":
    power_panels()
