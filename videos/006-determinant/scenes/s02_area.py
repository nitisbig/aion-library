"""Ch2 · One number for the stretch: the unit square becomes area 5, every square does, every shape does."""
from aion import *

from beats import T
from shots import (A_MAIN, FRAME, I2, Mat, backing, basis_arrows, chapter_card, circle_outline, country_outline, det2,
                   finish, backdrop, grid_lines, leaf_outline, live, matrix_panel, num, pt, rail, span_area, tex,
                   tiny_cells)

E = "easy_ease"
O1, U1 = np.array([-1.0, -1.4]), 0.9                 # Ch1's framing (the scene starts where Ch1 ended)
O2, U2 = np.array([0.0, -0.2]), 0.55                 # wider framing for the three shapes
H = 0.16                                             # side of the tiny squares, in grid units

# shapes, in grid coordinates before the matrix: (outline, where it sits)
SHAPES = [(circle_outline(0.8), np.array([-2.4, 0.2])),
          (leaf_outline(), np.array([2.0, 0.6])),
          (country_outline(2.6), np.array([0.5, -1.75]))]


@scene(T.cut_ch2, T.cut_test)
def s02_area(s):
    backdrop(s)
    ghost = s.manim(z=0)
    cl = s.manim(z=0.5)                               # the other cells, under the grid lines
    m = s.manim(z=1)                                  # grid
    sh = s.manim(z=2)                                 # cells, shapes, highlights
    ar = s.manim(z=3)                                 # the square / parallelogram and its number
    g = s.manim(z=4)                                  # arrows
    hb = s.manim(z=5.5, parallax=0.0)                 # panels that sit under the HUD content
    hud = s.manim(z=6, parallax=0.0)

    t0 = T.cut_ch2
    # ── one score for the matrix and the framing ──
    w_relax = (t0, t0 + 1.9)                          # Ch1's transformed grid relaxes back
    w_apply = (T.apply - 0.3, T.para + 0.15)          # "apply the matrix again"
    w_frame = (T.not_just + 7.0, T.any_shape + 0.9)   # zoom out for the shapes, grid back to rest
    w_grow = (T.tiny5 - 0.45, T.tiny5 + 1.2)          # every shape grows
    Mg = keys((w_relax[0], A_MAIN), (w_relax[1], I2, E), (w_apply[0], I2), (w_apply[1], A_MAIN, E),
              (w_frame[0], A_MAIN), (w_frame[1], I2, E), (w_grow[0], I2), (w_grow[1], A_MAIN, E), lead=0)
    Og = keys((w_frame[0], O1), (w_frame[1], O2, E), lead=0)
    Ug = keys((w_frame[0], U1), (w_frame[1], U2, E), lead=0)

    def W(v, t):                                      # world point of grid point v after the matrix at time t
        return pt(Og(t), Ug(t), Mg(t) @ np.asarray(v, float))

    grid_windows = (w_relax, w_apply, w_frame, w_grow)
    live(m, lambda t: grid_lines(Mg(t), Og(t), Ug(t), FRAME, n=16), *grid_windows)
    live(ghost, lambda t: grid_lines(I2, Og(t), Ug(t), FRAME, n=16, color=C.ghost, axes=False),
         (t0, t0 + 0.05), w_frame)
    rail(hud, 2)

    # ── arrows and the unit square, carried by the matrix; both leave before the zoom-out ──
    gone = (w_frame[0], w_frame[0] + 0.7)
    a_fade = fade(t0 - 1.0, dur=0.01, out=gone[0], out_dur=0.6, lead=0)    # 1 → 0 over `gone`
    live(g, lambda t: basis_arrows(Mg(t), Og(t), Ug(t)).set_opacity(a_fade(t)), w_relax, w_apply, gone)

    lab_on = fade(T.area1 - 0.3, dur=0.5, lead=0)     # the number appears on "exactly one"

    def area(t):
        M, k = Mg(t), a_fade(t)
        poly = span_area(M, Og(t), Ug(t), opacity=0.3 * k).set_stroke(opacity=k)
        out = VGroup(poly)
        if lab_on(t) > 0:
            c = W((0.5, 0.5), t)
            out.add(tex(num(det2(M)), size=72, color=C.area).move_to(c).set_opacity(k * lab_on(t)))
        return out
    live(ar, area, w_relax, (T.area1 - 0.35, T.area1 + 0.3), w_apply, gone)

    # Ch1's leftovers: the "?" and the dashed unit square, cleared as the grid relaxes
    q = tex("?", size=80, color=C.area).move_to(pt(O1, U1, (A_MAIN[:, 0] + A_MAIN[:, 1]) / 2))
    dash = DashedVMobject(Square(side_length=U1, color=C.text, stroke_width=C.thin).move_to(pt(O1, U1, (0.5, 0.5))),
                          num_dashes=24)
    sh.add(q, dash)
    sh.play(FadeOut(q), FadeOut(dash), at=t0 + 0.4, dur=0.5, lead=0)

    # "The square that sits on i hat and j hat": its outline is traced
    sq = Square(side_length=U1, stroke_color=C.area, stroke_width=C.stroke, fill_opacity=0).move_to(pt(O1, U1, (0.5, 0.5)))
    sh.play(Create(sq), at=T.unit_sq + 0.4, dur=1.0)
    sh.play(FadeOut(sq), at=T.area1 + 0.6, dur=0.6)

    # "Count it up": the original unit grid shows through the parallelogram, so the area can be read off
    para = np.array([[0, 0], A_MAIN[:, 0], A_MAIN[:, 0] + A_MAIN[:, 1], A_MAIN[:, 1]])
    count = VGroup()
    for k in range(-1, 5):
        for d in (np.array([1.0, 0.0]), np.array([0.0, 1.0])):
            p = k * d[::-1]                           # the line x = k (d = up) or y = k (d = right)
            ts = []
            for i in range(4):
                a, b = para[i], para[(i + 1) % 4]
                M2 = np.column_stack([d, a - b])
                if abs(np.linalg.det(M2)) < 1e-9:
                    continue
                s_, r = np.linalg.solve(M2, a - p)
                if -1e-9 <= r <= 1 + 1e-9:
                    ts.append(s_)
            if len(ts) >= 2 and max(ts) - min(ts) > 1e-6:
                count.add(Line(pt(O1, U1, p + min(ts) * d), pt(O1, U1, p + max(ts) * d), color=C.text,
                               stroke_width=C.thin, stroke_opacity=0.75))
    sh.play(LaggedStart(*[Create(ln) for ln in count], lag_ratio=0.12), at=T.area5 - 1.2, dur=1.4)
    sh.play(FadeOut(count), at=T.one_five + 1.2, dur=0.7)

    # "One became five"
    oneto = tex("1", r"\;\longrightarrow\;", "5", size=56, colors={2: C.area})
    oneto.move_to([-5.05, -0.15, 0])
    oneback = backing(oneto, pad=0.25)
    hud.play(FadeIn(oneback), FadeIn(oneto, shift=0.1 * RIGHT), at=T.one_five, dur=0.6)
    hud.play(FadeOut(VGroup(oneback, oneto)), at=w_frame[0], dur=0.6)

    # "Every square on the grid": all the other cells, carried by the same matrix, light up from the centre out
    cells, o = [], pt(O1, U1, (0, 0))
    for i in range(-9, 10):
        for j in range(-9, 10):
            if (i, j) == (0, 0):
                continue
            corners = [pt(O1, U1, A_MAIN @ np.array(c, float)) for c in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            if any(abs(c[0]) < 7.4 and abs(c[1]) < 4.2 for c in corners):
                cells.append((Polygon(*corners, stroke_width=0, fill_color=C.area,
                                      fill_opacity=0.13 if (i + j) % 2 else 0.24), (i + j) % 2))
    cells.sort(key=lambda c: np.linalg.norm(c[0].get_center() - o))
    cg = VGroup(*[c for c, _ in cells])
    cl.play(LaggedStart(*[FadeIn(c) for c in cg], lag_ratio=0.015), at=T.every_sq, dur=2.6)
    cl.play(*[c.animate.set_fill(opacity=0.26 if k else 0.4) for c, k in cells], at=T.five_times, dur=0.4)
    cl.play(*[c.animate.set_fill(opacity=0.13 if k else 0.24) for c, k in cells], at=T.five_times + 0.6, dur=0.5)
    cl.play(FadeOut(cg), at=w_frame[0], dur=0.7)

    # ── any shape: outlines drawn on the rested, zoomed-out grid; then filled with tiny squares; then it all grows ──
    def shape_mobs(t, k=1.0, squares=True):
        out = VGroup()
        for poly, at in SHAPES:
            pts = [W(at + p, t) for p in poly]
            outline = Polygon(*pts, stroke_color=C.text, stroke_width=C.thin + 1, fill_opacity=0)
            out.add(outline.set_stroke(opacity=k))
            if squares:
                sq = VGroup()
                for c in tiny_cells(poly, H):
                    cs = [W(at + c + d, t) for d in ((-H / 2, -H / 2), (H / 2, -H / 2), (H / 2, H / 2), (-H / 2, H / 2))]
                    sq.add(Polygon(*cs, stroke_color=C.bg, stroke_width=1.0, fill_color=C.area, fill_opacity=0.75 * k))
                out.add(sq)
        return out
    rest = w_frame[1] + 0.01
    outl = shape_mobs(rest, squares=False)
    for mob, beat in zip(outl, (T.circle, T.leaf, T.country)):
        sh.play(Create(mob), at=beat, dur=0.9)
    fill = shape_mobs(rest)
    squares = [fill[2 * i + 1] for i in range(3)]
    sh.play(*[LaggedStart(*[FadeIn(q_, scale=0.5) for q_ in sq_], lag_ratio=0.02) for sq_ in squares],
            at=T.tiny, dur=1.4)
    sh.remove(*outl, *squares, *[q_ for sq_ in squares for q_ in sq_], at=w_grow[0])
    shp_fade = fade(t0 - 1.0, dur=0.01, out=T.factor + 1.6, out_dur=0.8, lead=0)
    live(sh, lambda t: shape_mobs(t, k=shp_fade(t)), w_grow, (T.factor + 1.6, T.factor + 2.5))

    # "×5" beside each grown shape
    grown = shape_mobs(w_grow[1] + 0.01, squares=False)
    tags = VGroup()
    for o_ in grown:
        tags.add(tex(r"\times 5", size=48, color=C.area).next_to(o_, UR, buff=0.05))
    tags[2].next_to(grown[2], RIGHT, buff=0.25)
    sh.play(LaggedStart(*[FadeIn(t_, shift=0.1 * UP) for t_ in tags], lag_ratio=0.25), at=T.whole5, dur=1.0)
    sh.play(LaggedStart(*[Indicate(t_, color=C.area, scale_factor=1.2) for t_ in tags], lag_ratio=0.2),
            at=T.factor + 0.3, dur=1.2)
    sh.play(FadeOut(tags), at=T.factor + 1.9, dur=0.8)

    # ── the HUD matrix carries over from Ch1, then moves to centre: det [3 1; 1 2] = 5 ──
    M, hats, back = matrix_panel([["3", "1"], ["1", "2"]])
    hud.add(back, M, hats)
    det_w = tex(r"\det", size=72)
    M2 = Mat([["3", "1"], ["1", "2"]], colors=[C.ihat, C.jhat], size=72)
    eq, five = tex("=", size=72), tex("5", size=80, color=C.area)
    big = VGroup(det_w, M2, eq, five).arrange(RIGHT, buff=0.3).move_to([0, 0.3, 0])
    bigback = backing(big, pad=0.45)
    hud.play(FadeOut(VGroup(back, hats)), at=T.det_word - 0.2, dur=0.8)
    hb.play(FadeIn(bigback), at=T.det_word - 0.2, dur=0.8)
    hud.play(M.animate.scale(72 / 64).move_to(M2), at=T.det_word - 0.1, dur=1.1)
    hud.play(Write(det_w), at=T.det_word + 0.2, dur=0.8)
    hud.play(Write(eq), at=T.det5 - 0.4, dur=0.4)
    hud.play(FadeIn(five, scale=1.4), at=T.det5 + 0.6, dur=0.6)

    finish(s)
