"""Design sheet for 013: page 1 = palette, type, equations, motion; page 2 = look frames built from the real cast.

    uv run python videos/013-matrix-inverse/design_sheet.py        # writes out/design/design_{1,2}.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "design"
sys.path.insert(0, str(HERE))


def build(page):
    from PIL import Image

    from aion.render.project import load_video

    load_video("013", (1920, 1080), 30, only=["__none__"])            # activates the theme, imports no scenes
    import scipy.sparse.linalg as spla
    from aion import (DOWN, LEFT, RIGHT, UP, ArrayLayer, C, Circle, Dot, Line, MathTex, Polygon, Rectangle, Tex, VGroup,
                      VMobject, ease, np, scene)
    from aion.components.linalg import Mat, grid_lines, panel
    from aion.render import scenes as scene_mod
    from verify import (A, A_INV, BLUR_KEEP, BLUR_LEN, E, NULL, REPO, S, SHAFT, TEETH, ct_matrix, key_polys, key_raster)

    def tex(s, size=36, color=None):
        return MathTex(s, font_size=size, color=color or C.text)

    def sans(s, size=26, color=None):
        return Tex(r"\textsf{" + s + "}", font_size=size, color=color or C.text)

    def caps(s, size=26, color=None):
        return Tex(r"\textsc{" + s + "}", font_size=size, color=color or C.text)

    NORMAL = np.array([-SHAFT[1], SHAFT[0]])

    def key_world(p, scale=0.62):
        """Key frame -> plane: the shaft lies along (2, 1), so the teeth point along the light rays."""
        p = np.atleast_2d(p) - np.array([0.2, 0.0])
        return scale * (p[:, [0]] * SHAFT + p[:, [1]] * NORMAL)

    def key_mob(M, c, u, teeth=TEETH, color=None, opacity=0.3, width=2.4):
        color = color or C.key
        bow, hole, rest = key_polys(teeth)

        def poly(pts, fill, op):
            q = (M @ key_world(pts).T).T * u + np.asarray(c)[:2]
            return Polygon(*np.c_[q, np.zeros(len(q))], stroke_color=color, stroke_width=width, fill_color=fill,
                           fill_opacity=op)

        return VGroup(*[poly(r, color, opacity) for r in rest], poly(bow, color, opacity), poly(hole, C.bg, 1.0))

    def arrow(c, u, v, color, width=4):
        a, b = np.array([*c[:2], 0.0]), np.array([c[0] + u * v[0], c[1] + u * v[1], 0.0])
        d = (b - a) / max(np.linalg.norm(b - a), 1e-6)
        n = np.array([-d[1], d[0], 0.0])
        tip = Polygon(b, b - 0.17 * d + 0.075 * n, b - 0.17 * d - 0.075 * n, stroke_width=0, fill_color=color, fill_opacity=1)
        return VGroup(Line(a, b - 0.14 * d, color=color, stroke_width=width), tip)

    def plane(M, c, u, box):
        return grid_lines(M, c, u, box, n=16, minor=2)

    def page1(s, m):
        L = -6.7
        m.add(caps("What Matrix Inverses Actually Mean", 50).move_to([L, 3.5, 0], aligned_edge=LEFT))
        m.add(sans("design sheet: classic, crisp, every thread reversed", 25, C.muted).move_to([L, 3.0, 0], aligned_edge=LEFT))

        roles = [("fwd", "the move A"), ("back", "the way back"), ("home", "identity"), ("key", "the key"), ("vec", "point, target"),
                 ("ihat", "first column"), ("jhat", "second column"), ("det", "determinant"), ("null", "forgotten, rays"),
                 ("shadow", "the shadow"), ("cam", "other observer"), ("wrong", "dead end")]
        for i, (r, what) in enumerate(roles):
            x, y = L + 0.56 + 1.16 * (i % 6), 2.1 - 1.24 * (i // 6)
            col = getattr(C, r)
            m.add(Rectangle(width=1.0, height=0.44, stroke_width=0, fill_color=col, fill_opacity=1).move_to([x, y, 0]),
                  sans(r, 21).move_to([x, y - 0.38, 0]),
                  sans(what, 15, C.muted).move_to([x, y - 0.65, 0]))

        ys = (-0.72, -1.34, -1.86, -2.3)
        rows = [(tex(r"A^{-1}A=I", 62), "hero equation, CM roman, 72"), (tex(r"\det A = 4", 42), "working math, CM roman, 48"),
                (sans("slide, squash, shadow", 30, C.text), "key words, CM sans, 34"),
                (caps("Chapter three", 28, C.text), "chapter cards, CM small caps, 32")]
        for y, (mob, lab) in zip(ys, rows):
            m.add(mob.move_to([L, y, 0], aligned_edge=LEFT),
                  sans(lab, 16, C.muted).move_to([0.1, y, 0], aligned_edge=RIGHT))

        for k, name in enumerate(["smooth", "easy_ease", "spring"]):
            x0, y0, w, h = L + 2.3 * k, -3.62, 1.85, 0.72
            f = ease(name)
            ts = np.linspace(0, 1, 90)
            pts = [[x0 + w * t, y0 + h * float(f(t)), 0] for t in ts]
            use = {"smooth": "fades", "easy_ease": "matrix moves", "spring": "matrix settles"}[name]
            m.add(Rectangle(width=w, height=h, stroke_color=C.faint, stroke_width=1).move_to([x0 + w / 2, y0 + h / 2, 0]),
                  VMobject(stroke_color=C.back, stroke_width=2.6).set_points_as_corners(pts),
                  sans(use, 16, C.muted).move_to([x0 + w / 2, y0 - 0.2, 0]))

        xc = 3.72
        Am = Mat([["3", "1"], ["2", "2"]], size=46, h_buff=0.78, v_buff=0.68, colors=[C.ihat, C.jhat])
        Ai = Mat([[r"\tfrac12", r"-\tfrac14"], [r"-\tfrac12", r"\tfrac34"]], size=40, h_buff=1.0, v_buff=0.82)
        Ai.set_color(C.back)
        row = VGroup(tex("A^{-1}", 46, C.back), tex("=", 46), Ai, tex("A", 46, C.fwd), tex("=", 46), Am).arrange(RIGHT, buff=0.2)
        row[3].shift(RIGHT * 0.5); row[4].shift(RIGHT * 0.5); row[5].shift(RIGHT * 0.5)
        row.scale_to_fit_width(5.6).move_to([xc, 1.95, 0])
        m.add(row)

        eq = MathTex(r"A^{-1}", r"A", "=", r"A", r"A^{-1}", "=", "I", font_size=66)
        for i, col in {0: C.back, 1: C.fwd, 3: C.fwd, 4: C.back, 6: C.home}.items():
            eq[i].set_color(col)
        m.add(eq.scale(0.82).move_to([xc, 0.62, 0]))

        form = MathTex(r"A^{-1}", "=", r"\frac{1}{ad-bc}", r"\begin{bmatrix} d & -b \\ -c & a \end{bmatrix}", font_size=54)
        form[0].set_color(C.back); form[2].set_color(C.det); form[3].set_color(C.back)
        m.add(form.scale(0.78).move_to([xc, -0.42, 0]))

        aug = MathTex(r"\left[\begin{array}{cc|cc} 3 & 1 & 1 & 0 \\ 2 & 2 & 0 & 1 \end{array}\right]", r"\;\longrightarrow\;",
                      r"\left[\begin{array}{cc|cc} 1 & 0 & \tfrac12 & -\tfrac14 \\ 0 & 1 & -\tfrac12 & \tfrac34 \end{array}\right]", font_size=44)
        m.add(aug.scale_to_fit_width(6.0).move_to([xc, -1.72, 0]))
        tags = VGroup(sans("rewinds", 22, C.fwd), sans("records", 22, C.back)).arrange(RIGHT, buff=1.0).move_to([xc, -2.55, 0])
        m.add(tags)
        rule = sans("symbols, numbers and key words only: never a sentence on screen", 20, C.muted)
        m.add(rule.scale_to_fit_width(6.0).move_to([xc, -3.45, 0]))

    def page2(s, m):
        xs, ys = (-4.7, 0.0, 4.7), (1.95, -1.95)
        W, H = 4.45, 3.5
        tiles = [(xs[0], ys[0]), (xs[1], ys[0]), (xs[2], ys[0]), (xs[0], ys[1]), (xs[1], ys[1]), (xs[2], ys[1])]
        names = ["s01 the bend", "s06 threads", "s10 rewind and record", "s02 one shadow", "s23 the blurred picture", "s25 shadows"]
        for (x, y), name in zip(tiles, names):
            m.add(panel(x - W / 2, y - H / 2, x + W / 2, y + H / 2))
            m.add(sans(name, 19, C.muted).move_to([x - W / 2 + 0.12, y + H / 2 - 0.2, 0], aligned_edge=LEFT))

        def box(x, y, pad=0.05, top=0.36):
            return (x - W / 2 + pad, y - H / 2 + pad, x + W / 2 - pad, y + H / 2 - top)

        # 1: the bend
        x, y = tiles[0]; c = (x - 0.15, y - 0.5); u = 0.36
        m.add(plane(A, c, u, box(x, y)), key_mob(np.eye(2), c, u, color=C.muted, opacity=0.0, width=1.4), key_mob(A, c, u))
        m.add(arrow(c, u, A[:, 0], C.ihat), arrow(c, u, A[:, 1], C.jhat))
        m.add(Mat([["3", "1"], ["2", "2"]], size=30, h_buff=0.55, v_buff=0.46, colors=[C.ihat, C.jhat]).move_to([x - 1.55, y + 0.62, 0]))

        # 2: threads
        x, y = tiles[1]; c = (x - 0.1, y - 0.45); u = 0.33
        m.add(plane(np.eye(2), c, u, box(x, y)))
        P = np.array([[a, b] for a in np.arange(-1.5, 1.6, 0.75) for b in np.arange(-1.5, 1.6, 0.75)])
        for p in P:
            q = A @ p
            a = np.array([c[0] + u * p[0], c[1] + u * p[1], 0.0]); b = np.array([c[0] + u * q[0], c[1] + u * q[1], 0.0])
            if abs(b[0] - x) < W / 2 - 0.1 and y - H / 2 + 0.1 < b[1] < y + H / 2 - 0.42:
                m.add(Line(a, b, color=C.fwd, stroke_width=1.5), Dot(a, radius=0.03, color=C.home), Dot(b, radius=0.035, color=C.back))
        m.add(tex(r"\mathbf{x}\;\rightleftarrows\;A\mathbf{x}", 34).move_to([x + 1.2, y - 1.35, 0]))

        # 3: rewind and record
        x, y = tiles[2]
        st, rec = E[1] @ E[0] @ A, E[1] @ E[0]
        for k, (M, col, tag, mat) in enumerate(((st, C.fwd, "rewinds", "A"), (rec, C.back, "records", "I"))):
            cx = x - 1.08 + 2.16 * k; cy = y + 0.25; u = 0.2
            bx = (cx - 1.0, cy - 1.0, cx + 1.0, cy + 1.0)
            m.add(Rectangle(width=2.0, height=2.0, stroke_color=col, stroke_width=1.5).move_to([cx, cy, 0]))
            m.add(plane(M, (cx, cy), u, bx), arrow((cx, cy), u, M[:, 0], C.ihat, 3), arrow((cx, cy), u, M[:, 1], C.jhat, 3))
            m.add(sans(tag, 20, col).move_to([cx, cy - 1.2, 0]))
        m.add(tex(r"E_2E_1\,[\,A\;|\;I\,]", 30).move_to([x, y - 1.4, 0]))

        # 4: one shadow
        x, y = tiles[3]; c = (x - 0.1, y - 0.2); u = 0.56
        m.add(plane(np.eye(2), c, u, box(x, y)))
        d = S[:, 0] / np.linalg.norm(S[:, 0])
        m.add(Line([c[0] - 2.0 * d[0], c[1] - 2.0 * d[1], 0], [c[0] + 2.0 * d[0], c[1] + 2.0 * d[1], 0], color=C.shadow, stroke_width=7))
        n = NULL / np.linalg.norm(NULL)
        for t in np.linspace(-1.4, 1.4, 9):
            p = t * SHAFT * 0.62 * 1.0
            a, b = p + 1.05 * n, p - 1.05 * n
            m.add(Line([c[0] + u * a[0], c[1] + u * a[1], 0], [c[0] + u * b[0], c[1] + u * b[1], 0], color=C.null, stroke_width=1.2))
        m.add(key_mob(np.eye(2), c, u))
        m.add(key_mob(np.eye(2), c, u, teeth=(-1, 1, -1, -1), color=C.muted, opacity=0.0, width=1.2))

        # 5: the blurred picture
        x, y = tiles[4]
        ph = np.asarray(Image.open(REPO / "videos/009-what-matrices-are/assets/photo.png").convert("L"), float) / 255
        K = np.fft.fft(np.ones(BLUR_LEN) / BLUR_LEN, ph.shape[1])
        Fb = np.fft.fft(ph, axis=1) * K
        noisy = np.real(np.fft.ifft(Fb, axis=1)) + np.random.default_rng(13).normal(0, 0.004, ph.shape)
        Fn = np.fft.fft(noisy, axis=1)
        pics = [("blurred", np.real(np.fft.ifft(Fb, axis=1)), C.muted), ("inverse", ph, C.back),
                ("with noise", np.real(np.fft.ifft(Fn / K, axis=1)), C.null),
                ("stops short", np.real(np.fft.ifft(np.where(np.abs(K) > BLUR_KEEP, Fn / K, 0), axis=1)), C.back)]
        for i, (tag, img, col) in enumerate(pics):
            g = (np.clip(img, 0, 1) * 255).astype(np.uint8)
            px, py = x - 1.05 + 2.1 * (i % 2), y + 0.68 - 1.42 * (i // 2)
            s.add(ArrayLayer(np.dstack([g, g, g, np.full_like(g, 255)]), height=1.08, pos=(px, py), z=1))
            m.add(sans(tag, 18, col).move_to([px, py - 0.65, 0]))

        # 6: shadows
        x, y = tiles[5]; N = 96; truth = key_raster(N)
        for i, k in enumerate((2, 8, 32, 128)):
            M = ct_matrix(N, k)
            rec = spla.lsqr(M, M @ truth.ravel(), atol=1e-7, btol=1e-7, iter_lim=900)[0].reshape(N, N)
            g = (np.clip(rec[::-1], 0, 1) * 255).astype(np.uint8)
            rgb = np.dstack([g, (g * 0.71).astype(np.uint8), (g * 0.27).astype(np.uint8), np.full_like(g, 255)])
            px, py = x - 1.05 + 2.1 * (i % 2), y + 0.62 - 1.42 * (i // 2)
            s.add(ArrayLayer(rgb, height=1.08, pos=(px, py), z=1))
            m.add(tex(str(k), 28, C.data).move_to([px, py - 0.66, 0]))

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
    for p in [int(a) for a in sys.argv[1:] if a.isdigit()] or [1, 2]:
        build(p)
