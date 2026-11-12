"""Intro · The school ritual (a cross, ad − bc), dismissed as a recipe; then a preview: stretch, flip, collapse;
the promise (the formula on its parallelogram); the map (one square, lifted into a cube, pressed flat)."""
from aion import *

from beats import T
from shots import (A_MAIN, FRAME, I2, Mat, _clip, backdrop, basis_arrows, det2, finish, grid_lines, lettered, live,
                   pt, span_area, tex)

E = "easy_ease"
O, U = np.array([-0.4, -1.4]), 0.85                  # the preview grid
G, UG = np.array([-2.0, -1.6]), 0.95                 # the promise drawing
CUBE = np.array([(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
FACES = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]


def ramp(t, a, b):
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


@scene(T.start, T.cut_ch1)
def s00_intro(s):
    backdrop(s)
    w = s.manim(z=1)                                  # the preview grid
    ar = s.manim(z=2)                                 # the square
    g = s.manim(z=3)                                  # arrows
    tx = s.manim(z=4)                                 # matrix, strokes, formula
    t0 = T.start

    # ── "Take a matrix. Two rows, two columns. Four numbers." ──
    M = Mat([["a", "b"], ["c", "d"]], size=110, h_buff=1.5, v_buff=1.25).move_to([0, 1.3, 0])
    tx.play(Create(M.br), at=T.matrix, dur=0.8)
    tx.play(LaggedStart(*[FadeIn(M.cell(i, j), scale=1.3) for i in range(2) for j in range(2)], lag_ratio=0.25),
            at=T.matrix + 0.6, dur=1.2)
    tx.play(LaggedStart(*[Indicate(M.cell(i, j), color=C.text, scale_factor=1.25) for i in range(2) for j in range(2)],
                        lag_ratio=0.3), at=T.four - 0.2, dur=1.4)

    # ── "multiply them in a cross, and subtract" ──
    def stroke(p, q):
        d = (q - p) / np.linalg.norm(q - p)
        return Line(p + 0.38 * d, q - 0.38 * d, color=C.muted, stroke_width=C.stroke)
    s_ad = stroke(M.cell(0, 0).get_center(), M.cell(1, 1).get_center())
    s_bc = stroke(M.cell(0, 1).get_center(), M.cell(1, 0).get_center())
    tx.play(Create(s_ad), at=T.cross - 0.1, dur=0.6)
    tx.play(Create(s_bc), at=T.cross + 0.6, dur=0.6)
    f = tex("a", "d", "-", "b", "c", size=110).move_to([0.6, -1.65, 0])
    tx.play(TransformFromCopy(VGroup(M.cell(0, 0), M.cell(1, 1)), VGroup(f[0], f[1])), at=T.adbc, dur=0.9)
    tx.play(FadeIn(f[2]), TransformFromCopy(VGroup(M.cell(0, 1), M.cell(1, 0)), VGroup(f[3], f[4])),
            at=T.adbc + 1.0, dur=0.9)
    dl = tex(r"\det A", "=", size=110).next_to(f, LEFT, buff=0.3)
    tx.play(Write(dl), at=T.named, dur=0.9)

    # ── "just a recipe": it all goes grey ──
    rest = VGroup(M.br, s_ad, s_bc, f, dl)
    tx.play(VGroup(M.cols[0], M.cols[1], rest).animate.set_color(C.faint), at=T.recipe, dur=1.0)

    # ── "But watch": the letters lift off and become the two arrows of a grid ──
    arr0 = basis_arrows(I2, O, U)
    tx.play(FadeOut(rest), at=T.watch - 0.2, dur=0.6)
    tx.play(ReplacementTransform(VGroup(M.cell(0, 0), M.cell(1, 0)), arr0[0]),
            ReplacementTransform(VGroup(M.cell(0, 1), M.cell(1, 1)), arr0[1]), at=T.watch + 0.1, dur=1.3)
    g_in = (T.watch + 0.5, T.watch + 1.6)

    # ── one continuous preview: stretch, turn over, fold flat ──
    w_st = (T.stretches - 0.6, T.stretches + 0.9)
    w_fl = (T.flipped - 0.6, T.flipped + 0.8)
    w_z = (T.zero - 0.1, T.zero + 1.4)
    th = keys((t0, 0.0), (w_fl[0], 0.0), (w_fl[1], np.pi, "in_out_sine"), lead=0)
    sq = keys((t0, 1.0), (w_z[0], 1.0), (w_z[1], 0.0, E), lead=0)
    st = keys((t0, 0.0), (w_st[0], 0.0), (w_st[1], 1.0, E), lead=0)

    def Mt(t):
        A = (1 - st(t)) * I2 + st(t) * A_MAIN
        return np.diag([1.0, sq(t)]) @ np.diag([np.cos(th(t)), 1.0]) @ A
    out = (T.promise - 0.8, T.promise - 0.1)

    def k_all(t):
        return ramp(t, *g_in) * (1 - ramp(t, *out))
    win = (g_in, w_st, w_fl, w_z, (T.destroyed - 0.1, T.destroyed + 1.0), out)
    live(w, lambda t: grid_lines(Mt(t), O, U, FRAME, n=16, opacity=k_all(t)), *win)
    tx.play(FadeOut(arr0), at=g_in[1], dur=0.05, lead=0)      # the live arrows take over here
    tx.remove(arr0, *[M.cell(i, j) for i in range(2) for j in range(2)], at=g_in[1] + 0.1)
    live(g, lambda t: basis_arrows(Mt(t), O, U).set_opacity(1 - ramp(t, *out)), (g_in[1], g_in[1] + 0.05), *win[1:])

    def square(t):
        A = Mt(t)
        k = ramp(t, w_st[0], w_st[0] + 0.4) * (1 - ramp(t, T.destroyed, T.destroyed + 0.8))
        res = VGroup()
        if k > 0.003:
            res.add(span_area(A, O, U, opacity=0.35 * k).set_stroke(opacity=k))
        z = float(np.clip(1 - abs(det2(A)) / 0.5, 0, 1)) * (1 - ramp(t, *out))
        if z > 0.003:                                 # flat: one red line
            d = A[:, 0] if np.linalg.norm(A[:, 0]) > 1e-6 else np.array([1.0, 0.0])
            seg = _clip(O, d, FRAME)
            res.add(Line([*seg[0], 0], [*seg[1], 0], color=C.collapse, stroke_width=6, stroke_opacity=z))
        return res
    live(ar, square, *win[1:])

    # ── the promise: the formula, in colour, on the parallelogram it measures ──
    o = pt(G, UG, (0, 0))
    ai = Arrow(o, pt(G, UG, (3, 1)), buff=0, color=C.ihat, stroke_width=C.stroke + 1, tip_length=0.26)
    aj = Arrow(o, pt(G, UG, (1, 2)), buff=0, color=C.jhat, stroke_width=C.stroke + 1, tip_length=0.26)
    para = Polygon(o, pt(G, UG, (3, 1)), pt(G, UG, (4, 3)), pt(G, UG, (1, 2)), stroke_color=C.area,
                   stroke_width=C.thin + 0.6, fill_color=C.area, fill_opacity=0.3)
    fc = lettered("ad", "-bc", size=80).move_to(pt(G, UG, (2, 1.5)))
    fc[1][0].set_color(C.text)
    fc.set_stroke(C.bg, width=5, background=True)
    ar.play(FadeIn(para), at=T.promise + 0.2, dur=0.8)
    g.play(GrowArrow(ai), GrowArrow(aj), at=T.promise + 0.1, dur=0.8)
    tx.play(Write(fc), at=T.promise + 1.2, dur=1.2)
    ar.play(para.animate.set_fill(opacity=0.5), at=T.picture, dur=0.4)
    ar.play(para.animate.set_fill(opacity=0.3), at=T.picture + 0.6, dur=0.6)
    gone = T.square - 1.0
    ar.play(FadeOut(para), at=gone, dur=0.6)
    g.play(FadeOut(VGroup(ai, aj)), at=gone, dur=0.6)
    tx.play(FadeOut(fc), at=gone, dur=0.6)

    # ── "start with a single square, and end by flattening three dimensional space" ──
    lift = (T.square + 0.5, T.flatten - 0.2)          # the camera tips down and the square rises into a cube
    press = (T.flatten + 1.0, T.flatten + 2.2)        # "...three dimensional space": pressed flat as the line ends
    el = keys((t0, 90.0), (lift[0], 90.0), (lift[1], 36.0, E), (press[1] + 0.4, 36.0), (T.cut_ch1, 50.0, E),
              lead=0)                                 # the held pause: a slow rise that keeps the sheet visibly flat
    az = keys((t0, 0.0), (lift[0], 0.0), (T.cut_ch1, -60.0, "linear"), lead=0)
    hz = keys((t0, 0.0), (lift[0] + 0.3, 0.0), (lift[1] + 0.2, 1.0, E), (press[0], 1.0), (press[1], 0.0, "out_back"),
              lead=0)
    sq_in = (T.square - 0.3, T.square + 0.4)
    fade_out = (T.cut_ch1 - 1.1, T.cut_ch1 - 0.1)
    C0, UC = np.array([-0.4, -0.7]), 1.5

    def cube(t):
        a, e = np.radians(az(t)), np.radians(el(t))
        R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])

        def S(p):
            q = R @ (np.asarray(p, float) - [0.5, 0.5, 0])
            return np.array([C0[0] + UC * q[0], C0[1] + UC * (q[2] * np.cos(e) + q[1] * np.sin(e)), 0.0])

        def D(p):
            q = R @ (np.asarray(p, float) - [0.5, 0.5, 0])
            return q[1] * np.cos(e) - q[2] * np.sin(e)
        k = ramp(t, *sq_in) * (1 - ramp(t, *fade_out))
        kf = ramp(t, lift[0], lift[0] + 1.2) * (1 - ramp(t, *fade_out))     # the floor and arrows arrive with the lift
        h = hz(t)
        col = C.area if h > 0.08 or t < press[0] else C.collapse
        if t > press[1]:
            col = C.collapse
        res = VGroup()
        if kf > 0.003:                                # a floor of 3D space under the cube
            for v in np.arange(-1.0, 2.01, 0.5):
                fl = 1.0 if v == 0.0 else 0.45
                res.add(Line(S((v, -1.0, 0)), S((v, 2.0, 0)), color=C.grid, stroke_width=C.thin,
                             stroke_opacity=0.6 * fl * kf))
                res.add(Line(S((-1.0, v, 0)), S((2.0, v, 0)), color=C.grid, stroke_width=C.thin,
                             stroke_opacity=0.6 * fl * kf))
        pts = [c * [1, 1, h] for c in CUBE]
        for f_ in sorted(FACES, key=lambda f_: -np.mean([D(pts[i]) for i in f_])):
            res.add(Polygon(*[S(pts[i]) for i in f_], stroke_color=col, stroke_width=C.thin + 0.6, stroke_opacity=k,
                            fill_color=col, fill_opacity=0.2 * k))
        if kf > 0.003:                                # i, j, k hat: the third one is what gets pressed flat
            for tip, c_ in (((1, 0, 0), C.ihat), ((0, 1, 0), C.jhat), ((0, 0, h), C.khat)):
                if np.linalg.norm(S(tip) - S((0, 0, 0))) > 0.12:
                    res.add(Arrow(S((0, 0, 0)), S(tip), buff=0, color=c_, stroke_width=C.stroke, tip_length=0.2,
                                  max_tip_length_to_length_ratio=0.35, max_stroke_width_to_length_ratio=40)
                            .set_opacity(kf))
        return res
    live(ar, cube, sq_in, (lift[0], T.cut_ch1))
    d0 = tex(r"\det", "=", "0", size=72, colors={2: C.collapse}).move_to([-0.4, 2.4, 0])
    d0.set_stroke(C.bg, width=5, background=True)
    tx.play(Write(d0), at=press[1] + 0.3, dur=0.9)
    tx.play(FadeOut(d0), at=fade_out[0], dur=fade_out[1] - fade_out[0], lead=0)

    finish(s)
