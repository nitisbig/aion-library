"""Design sheet for 009 (Classic + lit 3D): page 1 = palette, type, equations, motion; page 2 = key frames.

    uv run python videos/009-what-matrices-are/design_sheet.py        # writes out/design/design_{1,2}.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "design"


def build(page):
    from PIL import Image

    from aion.render.project import load_video

    load_video("009", (1920, 1080), 30, only=["__none__"])            # activates the theme, imports no scenes
    from aion import (DOWN, LEFT, RIGHT, UP, ArrayLayer, C, Circle, DashedLine, Dot, Line, Polygon, Rectangle,
                      RoundedRectangle, VGroup, VMobject, ease, np, scene)
    from aion.render import scenes as scene_mod
    from shots import (A, H3, I2, I3, KEY, Cam, Mat, _clip, arrow, basis_arrows, die_rgba, grid_lines, lattice, lit_poly,
                       panel, tex, words)

    def fit(mob, w):
        """Scale `mob` down (never up) to at most `w` wide."""
        if mob.width > w:
            mob.scale_to_fit_width(w)
        return mob

    def page1(s, m):
        L = -6.6                                                          # left column edge
        m.add(fit(words(r"What Matrices Actually Are", size=56), 6.4).move_to([L, 3.45, 0], aligned_edge=LEFT))
        m.add(fit(words(r"Classic $\cdot$ crisp $\cdot$ lit 3D $\cdot$ a matrix is a move", size=26, color=C.muted), 6.2)
              .move_to([L, 2.85, 0], aligned_edge=LEFT))

        roles = ["ihat", "jhat", "khat", "vec", "target", "area", "null",
                 "eigen", "sigma", "cls_a", "cls_b", "data", "die", "grid"]
        for i, r in enumerate(roles):
            col = getattr(C, r)
            box = RoundedRectangle(width=0.7, height=0.4, corner_radius=0.05, stroke_color=C.frame,
                                   stroke_width=1.0, fill_color=col, fill_opacity=1.0)
            box.move_to([L + 0.38 + 0.88 * (i % 7), 1.95 - 1.12 * (i // 7), 0])
            m.add(box, fit(words(r.replace("_", r"\_"), size=18), 0.85).next_to(box, DOWN, buff=0.08),
                  fit(words(col.upper().replace("#", r"\#"), size=12, color=C.muted), 0.85).next_to(box, DOWN, buff=0.34))

        # type scale
        for y, size, label in ((-0.3, 48, "title 64"), (-0.95, 36, "math 48"), (-1.48, 22.5, "label 30")):
            m.add(words(r"Computer Modern", size=size).move_to([L, y, 0], aligned_edge=LEFT),
                  words(label, size=14, color=C.muted).move_to([-0.55, y, 0], aligned_edge=RIGHT))
        m.add(words(r"(sheet shown at 3/4 scale)", size=12, color=C.faint).move_to([-0.55, -1.8, 0], aligned_edge=RIGHT))
        m.add(fit(words(r"symbols, equations and numbers only $\cdot$ no captions", size=20, color=C.muted), 6.0)
              .move_to([L, -2.2, 0], aligned_edge=LEFT))

        # motion curves
        for k, name in enumerate(["smooth", "easy_ease", "out_back", "spring"]):
            x0, y0, w, h = L + 1.5 * k, -3.45, 1.15, 0.62
            f = ease(name)
            ts = np.linspace(0, 1, 80)
            pts = [[x0 + w * t, y0 + h * float(f(t)), 0] for t in ts]
            m.add(Rectangle(width=w, height=h, stroke_color=C.faint, stroke_width=1).move_to([x0 + w / 2, y0 + h / 2, 0]),
                  VMobject(stroke_color=C.vec, stroke_width=2.2).set_points_as_corners(pts),
                  words(name.replace("_", r"\_"), size=15, color=C.muted).move_to([x0 + w / 2, y0 - 0.2, 0]))

        # equation styling (right column, centred on xc)
        xc, W = 3.75, 6.2
        M = Mat([["3", "1"], ["2", "2"]], size=34, h_buff=0.62, v_buff=0.58).move_to([2.1, 2.2, 0])
        hats = VGroup(tex(r"\hat{\imath}", size=28, color=C.ihat).next_to(M.cols[0], UP, buff=0.22),
                      tex(r"\hat{\jmath}", size=28, color=C.jhat).next_to(M.cols[1], UP, buff=0.22))
        hats[1].align_to(hats[0], DOWN)
        m.add(tex("A", "=", size=34).next_to(M, LEFT, buff=0.15), M, hats)
        H = Mat([[2, 1, 0], [0, 1, 1], [1, 0, 1]], size=28, h_buff=0.5, v_buff=0.44).move_to([5.3, 2.25, 0])
        m.add(H, tex(r"\det", "=", "3", size=26, colors={2: C.area}).next_to(H, DOWN, buff=0.18))
        prod = tex(r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}", r"\begin{bmatrix} x \\ y \end{bmatrix}", "=",
                   "x", r"\begin{bmatrix} a \\ c \end{bmatrix}", "+", "y", r"\begin{bmatrix} b \\ d \end{bmatrix}",
                   size=30, colors={1: C.vec, 3: C.vec, 4: C.ihat, 6: C.vec, 7: C.jhat})
        m.add(fit(prod, W).move_to([xc, 0.45, 0]))
        eig = tex(r"A", r"\vec v", "=", r"\lambda", r"\vec v", size=32, colors={1: C.eigen, 3: C.eigen, 4: C.eigen})
        svd = tex("A", "=", "U", r"\Sigma", "V^{\\top}", size=32, colors={2: C.sigma, 3: C.sigma, 4: C.sigma})
        axb = tex("A", r"\vec x", "=", r"\vec b", size=32, colors={1: C.vec, 3: C.target})
        nul = tex(r"N(A)", size=30, color=C.null)
        m.add(fit(VGroup(eig, svd, axb, nul).arrange(RIGHT, buff=0.42), W).move_to([xc, -0.75, 0]))

        # progress rail badges
        badges = [tex(r"[\;\,]", size=26), tex(r"\#", size=24, color=C.grid),
                  tex(r"\hat{\imath}", r"\hat{\jmath}", r"\hat{k}", size=22, colors={0: C.ihat, 1: C.jhat, 2: C.khat}),
                  tex("AB", size=24), tex(r"A^{-1}", size=24), tex(r"\lambda", size=26, color=C.eigen),
                  tex(r"U\Sigma V^{\top}", size=20, color=C.sigma)]
        g = VGroup()
        for b in badges:
            fr = Rectangle(width=0.78, height=0.5, stroke_color=C.frame, stroke_width=1.0)
            g.add(VGroup(fr, fit(b, 0.68).move_to(fr)))
        m.add(fit(g.arrange(RIGHT, buff=0.1), W).move_to([xc, -1.95, 0]))
        m.add(words(r"progress rail: one badge per chapter", size=15, color=C.muted).move_to([xc, -2.45, 0]))
        rules = VGroup(words(r"columns keep their arrow's colour $\cdot$ moves start from the identity", size=16, color=C.muted),
                       words(r"rotations by angle, never elementwise $\cdot$ at most three things move", size=16, color=C.muted))
        m.add(fit(rules.arrange(DOWN, buff=0.12), W).move_to([xc, -3.3, 0]))

    labels = []

    def tile(m, cx, cy, w, h, label):
        m.add(panel(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        w, h = w - 0.05, h - 0.05                                         # content stays inside the border
        labels.append(words(label, size=22, color=C.muted).move_to([cx - w / 2 + 0.14, cy + h / 2 - 0.24, 0],
                                                                    aligned_edge=LEFT))
        return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

    def finish_labels(s):
        top = s.manim(z=5)
        for lab in labels:
            top.add(Rectangle(width=lab.width + 0.16, height=lab.height + 0.12, stroke_width=0, fill_color=C.bg,
                              fill_opacity=1.0).move_to(lab), lab)

    def seg(m, c, d, box, color, width=2, opacity=0.8):
        """The infinite line through c along d, clipped to a tile."""
        ends = _clip(np.asarray(c, float), np.asarray(d, float), box)
        if ends is not None:
            m.add(Line([*ends[0], 0], [*ends[1], 0], color=color, stroke_width=width).set_opacity(opacity))

    def die_layer(s, cam, M=I3, az=-35.0, el=24.0, zoom=0.7, size=640, z=1):
        img = die_rgba(M, az=az, el=el, size=size, zoom=zoom)
        hgt = 2 * 11.0 * np.tan(np.radians(15.0 / zoom)) * cam.u          # pyvista frustum height at the origin
        s.add(ArrayLayer(img, height=hgt, pos=tuple(cam.o), z=z))

    def page2(s, m):
        m.add(words(r"Key frames", size=56).move_to([-6.55, 3.5, 0], aligned_edge=LEFT))
        W, Hh = 4.45, 3.2
        xs, ys = [-4.6, 0.0, 4.6], [1.35, -2.1]

        # 1 hook: the box, its columns as arrows in a lit 3D lattice, the die carried by H
        x0, y0, x1, y1 = tile(m, xs[0], ys[0], W, Hh, "s00 hook")
        Hm = Mat([[2, 1, 0], [0, 1, 1], [1, 0, 1]], size=30, h_buff=0.46, v_buff=0.42).move_to([x0 + 0.95, ys[0] - 0.1, 0])
        m.add(Hm)
        Mh = (I3 + H3) / 2                                                # the hook, half way through its move
        cam = Cam(-38, 26, origin=(xs[0] + 0.95, ys[0] - 0.25), unit=0.55)
        m.add(lattice(cam, Mh, n=2, box=2.1, width=1.3))
        die_layer(s, cam, Mh * 0.8, az=-38, el=26, zoom=0.55, size=720)
        o = cam.scr((0, 0, 0))
        s.manim(z=2).add(*[arrow(o, cam.scr(Mh[:, j] * 1.45), col, width=4, tip=0.18)
                           for j, col in enumerate((C.ihat, C.jhat, C.khat))])

        # 2 a move: the grid after A over the ghost grid, i-hat, j-hat, a vector and where it lands
        box = tile(m, xs[1], ys[0], W, Hh, "s06 columns")
        c = np.array([xs[1] - 0.75, ys[0] - 0.75])
        u = 0.42
        m.add(grid_lines(I2, c, u, box, n=10, color=C.ghost, width=1.2, axes=False),
              grid_lines(A, c, u, box, n=10, minor=1, width=1.3), basis_arrows(A, c, u, width=3.6))
        v = np.array([1.0, 0.5])
        m.add(arrow(c, c + u * v, C.vec, width=3, tip=0.12).set_opacity(0.4),
              arrow(c, c + u * (A @ v), C.vec, width=3.6, tip=0.18),
              tex(r"\vec x", size=26, color=C.vec).move_to([*(c + u * (A @ v) + [0.3, 0.1]), 0]))

        # 3 eigen sweep: arrows knocked off their line, two violet lines that aren't
        box = tile(m, xs[2], ys[0], W, Hh, "s14 eigenvectors")
        c = np.array([xs[2], ys[0] - 0.25])
        r = 0.3
        for d in ((1, 1), (1, -2)):
            seg(m, c, d, box, C.eigen, width=2, opacity=0.75)
        for th in np.linspace(0, 2 * np.pi, 10, endpoint=False) + 0.2:
            u = r * np.array([np.cos(th), np.sin(th)])
            m.add(arrow(c, c + u, C.text, width=1.6, tip=0.07).set_opacity(0.5),
                  arrow(c, c + A @ u, C.vec, width=2.2, tip=0.1).set_opacity(0.55))
        for d, lam in (((1, 1), 4), ((1, -2), 1)):
            u = r * np.array(d, float) / np.linalg.norm(d)
            m.add(arrow(c, c + A @ u, C.eigen, width=3.6, tip=0.14))
        m.add(Circle(radius=r, color=C.muted, stroke_width=1.2).move_to([*c, 0]),
              tex(r"\lambda=4", size=26, color=C.eigen).move_to([*(c + [1.55, 1.25]), 0]),
              tex(r"\lambda=1", size=26, color=C.eigen).move_to([*(c + [0.75, -0.95]), 0]))

        # 4 SVD: circle -> ellipse, the singular axes
        box = tile(m, xs[0], ys[1], W, Hh, "s17 rotate, stretch, rotate")
        c = np.array([xs[0], ys[1] - 0.2])
        r = 0.34
        U, sg, Vt = np.linalg.svd(A)
        th = np.linspace(0, 2 * np.pi, 160)
        circ = np.stack([np.cos(th), np.sin(th)], 1) * r
        ell = circ @ A.T
        m.add(VMobject(stroke_color=C.muted, stroke_width=1.4).set_points_as_corners([[*(c + p), 0] for p in circ]),
              VMobject(stroke_color=C.sigma, stroke_width=3).set_points_as_corners([[*(c + p), 0] for p in ell]))
        for k in range(2):
            m.add(Line([*(c - sg[k] * r * U[:, k]), 0], [*(c + sg[k] * r * U[:, k]), 0], color=C.sigma, stroke_width=2.2),
                  arrow(c, c + r * Vt[k], C.sigma, width=2.4, tip=0.08).set_opacity(0.6))
        u1 = U[:, 0] * np.sign(U[1, 0] or 1)                              # the axis end that points up
        u2 = U[:, 1] * np.sign(U[1, 1] or 1)
        m.add(tex(r"\sigma_1", size=28, color=C.sigma).move_to([*(c + sg[0] * r * u1 + 0.3 * u1), 0]),
              tex(r"\sigma_2", size=28, color=C.sigma).move_to([*(c + sg[1] * r * u2 + 0.32 * u2), 0]),
              tex("A", "=", "U", r"\Sigma", r"V^{\top}", size=30, colors={2: C.sigma, 3: C.sigma, 4: C.sigma})
              .move_to([xs[0] + 1.35, ys[1] - 1.25, 0]))

        # 5 shadow: a lit die over the floor, parallel light, the shadow (a rank-2 move)
        box = tile(m, xs[1], ys[1], W, Hh, "s12 shadow")
        cam = Cam(25, 32, origin=(xs[1] + 0.3, ys[1] + 0.1), unit=0.42)
        zf = -1.9
        floor = []
        for k in range(-3, 4):
            for a_, b_ in (((k, -3, zf), (k, 3, zf)), ((-3, k, zf), (3, k, zf))):
                pa, pb = cam.scr(a_), cam.scr(b_)
                ends = _clip(pa[:2], pb[:2] - pa[:2], box)
                if ends is not None:
                    lo, hi = sorted([0.0, 1.0])
                    ln = Line([*ends[0], 0], [*ends[1], 0])
                    # keep only the part of the clipped line that lies between the two floor points
                    t0 = np.clip((ends[0] - pa[:2]) @ (pb[:2] - pa[:2]) / np.sum((pb[:2] - pa[:2]) ** 2), lo, hi)
                    t1 = np.clip((ends[1] - pa[:2]) @ (pb[:2] - pa[:2]) / np.sum((pb[:2] - pa[:2]) ** 2), lo, hi)
                    if t1 - t0 > 1e-3:
                        floor.append(Line(pa + t0 * (pb - pa), pa + t1 * (pb - pa), color=C.grid_minor,
                                          stroke_width=1.2))
        m.add(VGroup(*floor))
        corners = np.array([(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
        L = KEY
        shadow = corners - ((corners[:, 2] - zf) / L[2])[:, None] * L
        from scipy.spatial import ConvexHull
        hull = shadow[ConvexHull(shadow[:, :2]).vertices]
        m.add(Polygon(*[cam.scr(p) for p in hull], stroke_width=0, fill_color="#2a2a2a", fill_opacity=1.0))
        die_layer(s, cam, I3, az=25, el=32, zoom=0.7, size=520, z=1)
        rays = VGroup()
        for p in corners[[1, 3, 5, 7]]:
            q = p - ((p[2] - zf) / L[2]) * L
            rays.add(DashedLine(cam.scr(p + 1.6 * L), cam.scr(q), color=C.null, stroke_width=1.6, dash_length=0.08))
        s.manim(z=2).add(rays)
        m.add(tex(r"N(A)", size=28, color=C.null).move_to([xs[1] + 1.6, ys[1] + 1.15, 0]))

        # 6 the picture as layers: k = 1, 10, 30, original
        box = tile(m, xs[2], ys[1], W, Hh, "s18 the picture, layer by layer")
        img = die_rgba(I3, az=-35, el=28, size=240, zoom=1.05, gray=True)
        gimg = img[..., 0].astype(float) / 255 * (img[..., 3] / 255)
        Us, ss, Vts = np.linalg.svd(gimg, full_matrices=False)
        for i, k in enumerate((1, 10, 30, None)):
            rec = gimg if k is None else np.clip((Us[:, :k] * ss[:k]) @ Vts[:k], 0, 1)
            g8 = (rec * 255).astype(np.uint8)
            rgba = np.dstack([g8, g8, g8, np.full_like(g8, 255)])
            px = xs[2] - 1.62 + 1.08 * i
            s.add(ArrayLayer(rgba, height=0.98, pos=(px, ys[1] - 0.05), z=1))
            m.add(Rectangle(width=1.0, height=1.0, stroke_color=C.frame, stroke_width=1).move_to([px, ys[1] - 0.05, 0]),
                  tex(r"k=%d" % k if k else r"\text{all}", size=22, color=C.sigma if k else C.muted)
                  .move_to([px, ys[1] - 0.82, 0]))
        m.add(words(r"$30$ layers $\approx 12.5\%$ of the numbers", size=22, color=C.muted).move_to([xs[2], ys[1] - 1.3, 0]))
        finish_labels(s)

    @scene(0.0, 10.0)
    def sheet(s):
        s.solid(C.bg, z=-200)
        m = s.manim()
        (page1 if page == 1 else page2)(s, m)

    sd = scene_mod.REGISTRY[-1]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"design_{page}.png"
    Image.fromarray(sd.comp((1920, 1080), 30).frame(5.0, 150)).save(path)
    print(path)


if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:] if a.isdigit()] or [1, 2]
    for p in pages:
        build(p)
