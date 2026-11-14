"""Ch4 · adding up the little pieces: the divergence theorem. One tiny square from Ch2 shrinks into its place in a
region of the hero field, which is cut into small squares; each shows its outflow (orange out, blue in, sized by
its divergence). Two neighbours: what leaves one through the shared edge enters the other, so that edge cancels;
then every inside edge cancels in a wave, leaving the boundary with its flux arrows. In 3D: a block of little
cubes becomes a closed surface with normals, and the theorem assembles. Then the lamp tile flies back and becomes a
point source in 3D: nested spheres, arrows falling as 1/r^2, 4 pi through every sphere, a point charge."""
from aion import *

from beats import T
from shots import (BADGES, REG_C, REG_H, TILE_C, TILE_K, LAMP_C, arrow, dim, ease, field_arrows, hero, hero_div,
                   lamp_tile, oiint, ortho, ramp, region, sample_grid, stage, tex)

E = "easy_ease"
FULL = (14.4, 8.2)
RES = (320, 180)
REG = region()
CELLS = np.array(REG["cells"])


def Fh(p):
    P, Q = hero(np.array(p[0]), np.array(p[1]))
    return np.array([float(P), float(Q)])


def cell_marks(k, scale=1.0):
    """Four little arrows on a cell, out (orange) or in (blue), length set by the divergence there."""
    c = CELLS[k]
    d = float(hero_div(np.array(c[0]), np.array(c[1])))
    L = min(0.24, 0.16 * abs(d)) * scale
    if L < 0.025:
        return VGroup()
    col = C.div if d > 0 else C.sink
    g = VGroup()
    for n in (np.array([1, 0]), np.array([-1, 0]), np.array([0, 1]), np.array([0, -1])):
        a = c + n * 0.06 if d > 0 else c + n * (0.06 + L)
        b = a + n * L if d > 0 else a - n * L
        g.add(arrow(a, b, col, width=2.0, tip=0.07))
    return g


def cube_block(t, az, el, center, scale, k=1.0):
    """A 3 x 3 x 3 block of little cubes (visible faces only)."""
    proj = ortho(az, el, scale=scale, center=center)
    g = VGroup()
    ticks = np.linspace(-1, 1, 4)
    for n in np.vstack([np.eye(3), -np.eye(3)]):
        if proj.depth(n) <= 0.02:
            continue
        u, v = [e for e in np.eye(3) if abs(e @ n) < 0.5]
        for a in ticks:
            edge = abs(a) > 0.99
            col, w = (C.boundary, C.thin + 1.2) if edge else (C.muted, C.thin * 0.7)
            g.add(Line(proj(n + a * u - v), proj(n + a * u + v), color=col, stroke_width=w))
            g.add(Line(proj(n + a * v - u), proj(n + a * v + u), color=col, stroke_width=w))
    return dim(g, k)


def blob_surface(az, el, center, scale, k=1.0, normals=1.0):
    """A smooth closed surface (an ellipsoid, gently lumpy) as latitude/longitude lines, with outward normals."""
    proj = ortho(az, el, scale=scale, center=center)
    R = lambda th, ph: 1.15 + 0.12 * np.sin(2 * ph) * np.sin(th) ** 2 + 0.08 * np.cos(3 * th)
    P = lambda th, ph: R(th, ph) * np.array([1.15 * np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), 0.95 * np.cos(th)])
    g = VGroup()
    phs = np.linspace(0, 2 * np.pi, 73)
    for th in np.linspace(0.35, np.pi - 0.35, 6):
        g.add(VMobject(stroke_color=C.boundary, stroke_width=C.thin, stroke_opacity=0.55 * k)
              .set_points_as_corners([proj(P(th, ph)) for ph in phs]))
    ths = np.linspace(0, np.pi, 37)
    for ph in np.linspace(0, np.pi, 6, endpoint=False):
        g.add(VMobject(stroke_color=C.boundary, stroke_width=C.thin, stroke_opacity=0.55 * k)
              .set_points_as_corners([proj(P(th, ph)) for th in ths] + [proj(P(th, ph + np.pi)) for th in ths[::-1]]))
    if normals > 0.01:
        eps = 1e-3
        for th in np.linspace(0.6, np.pi - 0.6, 3):
            for ph in np.linspace(0, 2 * np.pi, 7, endpoint=False) + th:
                p = P(th, ph)
                n = np.cross(P(th + eps, ph) - P(th - eps, ph), P(th, ph + eps) - P(th, ph - eps))
                n = n / np.linalg.norm(n)
                if n @ p < 0:
                    n = -n
                if proj.depth(n) < 0.05:
                    continue
                g.add(arrow(proj(p)[:2], proj(p + 0.45 * normals * n)[:2], C.div, width=2.4, tip=0.1, opacity=k))
    return g


@scene(T.cut_ch4, T.cut_stokes)
def s10_gauss(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:3])
    tile = lamp_tile()
    m.add(tile, at=s.start)
    flat_out = (T.cubes - 0.6, T.cubes + 0.2)

    # the hero field, faint, and its divergence under the region only
    k_f = keys((s.start, 0.0), (T.region - 0.3, 0.0), (T.region + 0.9, 0.22, E), (flat_out[0], 0.22),
               (flat_out[1], 0.0, E), lead=0)
    mf = s.manim(z=1, opacity=k_f)
    mf.add(field_arrows(lambda x, y: hero(x, y), (-5.0, -4.2, 7.3, 4.2), step=0.6, scale=0.5, width=1.8), at=s.start)
    D = sample_grid(hero_div, (0, 0), FULL, res=RES)
    xs = np.linspace(-FULL[0] / 2, FULL[0] / 2, RES[0])
    ys = np.linspace(-FULL[1] / 2, FULL[1] / 2, RES[1])
    X, Y = np.meshgrid(xs, ys)
    mask = np.zeros_like(D)
    for cx, cy in CELLS:
        mask[(np.abs(X - cx) <= REG_H / 2) & (np.abs(Y - cy) <= REG_H / 2)] = 1.0
    k_map = keys((s.start, 0.0), (T.squares, 0.0), (T.squares + 1.5, 0.45, E), (T.every_inside, 0.45),
                 (T.boundary + 1.0, 0.3, E), (flat_out[0], 0.3), (flat_out[1], 0.0, E), lead=0)
    s.add(FieldLayer(lambda t: D * mask, cmap="diverging", vmin=-3.0, vmax=3.0, extent=FULL,
                     colors=(C.sink, C.bg, C.div), animated=False, z=-20, opacity=k_map))

    # ── "so far, everything has been tiny": the Ch2 square, big, then back to its place ──
    k0 = int(np.argmin(np.linalg.norm(CELLS - REG_C, axis=1)))
    c0 = CELLS[k0]
    divs = np.array([float(hero_div(np.array(x), np.array(y))) for x, y in CELLS])
    kb = int(np.argmax(divs))                   # the opening square: one with a clear outflow
    cb = CELLS[kb]
    small = VGroup(Square(side_length=REG_H, color=C.boundary, stroke_width=C.stroke).move_to([*cb, 0]),
                   *[arrow(cb + n * 0.06, cb + n * 0.2, C.div, width=2.0, tip=0.07)
                     for n in (np.array([1, 0]), np.array([-1, 0]), np.array([0, 1]), np.array([0, -1]))])
    BC, BH = np.array([REG_C[0], 0.1]), 3.0           # the big Ch2 square, centred, with clear outflow
    big = VGroup(Square(side_length=BH, color=C.boundary, stroke_width=C.stroke).move_to([*BC, 0]),
                 *[arrow(BC + n * (BH / 2 - 0.35), BC + n * (BH / 2 + 0.55), C.div, width=C.stroke + 1, tip=0.22)
                   for n in (np.array([1, 0]), np.array([-1, 0]), np.array([0, 1]), np.array([0, -1]))])
    m.play(FadeIn(big, scale=0.8), at=T.tiny, dur=0.8)
    m.play(ReplacementTransform(big, small), at=T.zoom, dur=1.6, ease=E)
    m.play(FadeOut(small), at=T.squares + 0.6, dur=0.6)

    # ── the region, cut into squares ──
    edges_in = VGroup(*[Line([*a, 0], [*b, 0], color=C.muted, stroke_width=C.thin) for a, b, _, _ in REG["inner"]])
    edges_out = VGroup(*[Line([*a, 0], [*b, 0], color=C.frame, stroke_width=C.thin + 0.5) for a, b, _, _ in REG["outer"]])
    d_in = [np.linalg.norm((np.asarray(a) + b) / 2 - c0) for a, b, _, _ in REG["inner"]]
    d_out = [np.linalg.norm((np.asarray(a) + b) / 2 - c0) for a, b, _, _ in REG["outer"]]
    m.play(LaggedStart(*[Create(e) for _, e in sorted(zip(d_out, edges_out), key=lambda z: z[0])], lag_ratio=0.04),
           at=T.region, dur=1.6)
    m.play(LaggedStart(*[FadeIn(e) for _, e in sorted(zip(d_in, edges_in), key=lambda z: z[0])], lag_ratio=0.015),
           at=T.squares, dur=1.8)
    marks = VGroup(*[cell_marks(k) for k in range(len(CELLS))])
    m.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in marks], lag_ratio=0.02), at=T.outflow, dur=1.8)
    lab = tex(r"(\nabla\cdot\mathbf{F})", r"\,\Delta A", size=52, colors={0: C.div}).move_to([REG_C[0], 2.85, 0])
    m.play(FadeIn(lab, shift=0.1 * DOWN), at=T.div_area, dur=0.7)

    # ── two neighbours: the shared edge cancels ──
    kA = k0
    kB = REG["idx"].get(next(((i + 1, j) for (i, j), kk in REG["idx"].items() if kk == kA)))
    shared = next(e for e in REG["inner"] if {e[2], e[3]} == {kA, kB})
    a, b = np.asarray(shared[0]), np.asarray(shared[1])
    mid = (a + b) / 2
    pair = VGroup(*[Square(side_length=REG_H, color=C.boundary, stroke_width=C.stroke).move_to([*CELLS[k], 0])
                    for k in (kA, kB)])
    m.play(Create(pair), marks.animate.set_opacity(0.25), at=T.neighbors2, dur=0.8)
    sh = Line([*a, 0], [*b, 0], color=C.text, stroke_width=C.stroke + 2)
    m.play(Create(sh), at=T.shared, dur=0.6)
    P_mid = Fh(mid)[0]
    sgn = 1 if P_mid >= 0 else -1
    L = 0.55
    out_a = arrow(mid + np.array([-sgn * L / 2, 0.1]), mid + np.array([sgn * L / 2, 0.1]), C.div, width=C.stroke + 1,
                  tip=0.14)
    in_b = arrow(mid + np.array([-sgn * L / 2, -0.1]), mid + np.array([sgn * L / 2, -0.1]), C.sink, width=C.stroke + 1,
                 tip=0.14)
    m.play(GrowArrow(out_a), at=T.out_one, dur=0.6)
    m.play(GrowArrow(in_b), at=T.out_one + 1.0, dur=0.6)
    plus = tex("+", size=40, color=C.div).move_to([*(mid + np.array([0, 0.42])), 0])
    minus = tex("-", size=40, color=C.sink).move_to([*(mid + np.array([0, -0.42])), 0])
    m.play(FadeIn(plus), FadeIn(minus), at=T.out_one + 1.7, dur=0.4)
    m.play(out_a.animate.shift(0.1 * DOWN).scale(0.2), in_b.animate.shift(0.1 * UP).scale(0.2),
           FadeOut(VGroup(plus, minus)), at=T.edge_cancels, dur=0.8, ease=E)
    m.play(FadeOut(VGroup(out_a, in_b)), sh.animate.set_stroke(opacity=0.0), at=T.edge_cancels + 0.7, dur=0.4)

    # ── every inside edge cancels: a wave from the pair outward; only the boundary is left ──
    order = sorted(range(len(edges_in)), key=lambda i: d_in[i])
    flashes = [Succession(edges_in[i].animate(run_time=0.25).set_stroke(C.text, opacity=1.0),
                          edges_in[i].animate(run_time=0.35).set_stroke(opacity=0.0)) for i in order]
    m.play(FadeOut(pair), LaggedStart(*flashes, lag_ratio=0.04), FadeOut(marks), at=T.every_inside, dur=4.2)
    loop = VGroup(*[Line([*a, 0], [*b, 0], color=C.boundary, stroke_width=C.stroke + 1.5) for a, b, _, _ in REG["outer"]])
    m.play(ReplacementTransform(edges_out, loop), at=T.boundary - 0.3, dur=0.8)
    flux = VGroup()
    for a, b, n, _ in REG["outer"]:
        mid_ = (np.asarray(a) + b) / 2
        fn = float(Fh(mid_) @ n)
        if abs(fn) < 0.08:
            continue
        L_ = float(np.clip(0.45 * abs(fn), 0.12, 0.6))
        p0 = mid_ if fn > 0 else mid_ + n * L_
        flux.add(arrow(p0, p0 + np.sign(fn) * n * L_, C.div if fn > 0 else C.sink, width=2.4, tip=0.1))
    m.play(LaggedStart(*[GrowArrow(f) for f in flux], lag_ratio=0.03), at=T.boundary + 0.5, dur=1.6)
    eq2 = VGroup(tex(r"\iint", r"\nabla\cdot\mathbf{F}", r"\,dA", "=", r"\oint", r"\mathbf{F}\cdot\mathbf{n}", r"\,ds",
                     size=56, colors={1: C.div, 4: C.boundary}))
    eq2.move_to([REG_C[0], 2.85, 0])
    m.play(FadeOut(lab), at=T.adding - 0.4, dur=0.4)
    m.play(FadeIn(eq2[0][0:4], shift=0.1 * RIGHT), at=T.adding + 0.2, dur=0.8)
    m.play(FadeIn(eq2[0][4:], shift=0.1 * LEFT), at=T.adding + 2.2, dur=0.8)

    # ── in 3D: little cubes, then a closed surface with normals ──
    m.play(FadeOut(VGroup(loop, flux)), at=flat_out[0], dur=0.6)
    C3 = (0.9, -0.55)
    az = lambda t: np.radians(-40) + 0.05 * (t - T.cubes)
    k_cube = (T.cubes - 0.1, T.cubes + 0.6, T.surface - 0.2, T.surface + 0.6)

    def block(t):
        k = ramp(t, k_cube[0], k_cube[1]) * (1 - ramp(t, k_cube[2], k_cube[3]))
        return cube_block(t, az(t), np.radians(24), C3, 1.05, k)
    m.redraw(block, during=(k_cube[0], k_cube[3] + 0.05))
    s_out = (T.lamp_pays - 0.5, T.lamp_pays + 0.2)

    def surf(t):
        k = ramp(t, T.surface - 0.2, T.surface + 0.7) * (1 - ramp(t, *s_out))
        return blob_surface(az(t), np.radians(22), C3, 1.6, k, normals=ease(t, T.surface + 0.5, T.surface + 1.5))
    m.redraw(surf, during=(T.surface - 0.2, s_out[1] + 0.05))
    eq3 = VGroup(tex(r"\iiint", r"\nabla\cdot\mathbf{F}", r"\,dV", "=", size=56, colors={1: C.div}),
                 oiint(r"\mathbf{F}\cdot\mathbf{n}\,dS", size=56, color=C.boundary, rest_color=C.text))
    eq3.arrange(RIGHT, buff=0.18).move_to([REG_C[0], 2.85, 0])
    m.play(FadeOut(eq2), at=T.div_thm - 0.5, dur=0.5)
    m.play(FadeIn(eq3, shift=0.1 * UP), at=T.div_thm + 0.1, dur=0.8)

    # ── the lamp pays off: the tile flies back and becomes a point source in 3D ──
    O = np.array([0.6, -0.5])
    m.play(FadeOut(eq3), at=T.lamp_pays - 0.4, dur=0.5)
    m.play(tile.animate.scale(2.4).move_to([*O, 0]), at=T.lamp_pays + 0.1, dur=1.1, ease=E)
    m.play(FadeOut(tile, scale=1.6), at=T.lamp_pays + 1.1, dur=0.6)
    radii = (0.75, 1.5, 2.25)
    dirs = []
    for kk in range(26):                        # Fibonacci directions on the sphere
        z = 1 - 2 * (kk + 0.5) / 26
        r = np.sqrt(1 - z * z)
        ph = kk * np.pi * (3 - np.sqrt(5))
        dirs.append(np.array([r * np.cos(ph), r * np.sin(ph), z]))
    proj = ortho(np.radians(-30), np.radians(20), scale=1.0, center=O)

    def sphere(R, k):
        g = VGroup(Circle(radius=R, color=C.boundary, stroke_width=C.thin + 0.5).move_to(proj([0, 0, 0]))
                   .set_stroke(opacity=0.8 * k))
        th = np.linspace(0, 2 * np.pi, 73)
        for z0 in (0.0, 0.55):
            rr = R * np.sqrt(1 - z0 * z0)
            g.add(VMobject(stroke_color=C.boundary, stroke_width=C.thin, stroke_opacity=0.4 * k)
                  .set_points_as_corners([proj([rr * np.cos(a), rr * np.sin(a), R * z0]) for a in th]))
        return g

    sph_in = [T.lamp_pays + 1.4 + 0.5 * i for i in range(3)]
    spheres = VGroup(*[sphere(R, 1.0) for R in radii])
    for sp, t0 in zip(spheres, sph_in):
        m.play(Create(sp), at=t0, dur=0.9)
    rays = VGroup()
    for R in radii:
        Lr = 0.5 / R ** 2
        g = VGroup()
        for d in dirs:
            if proj.depth(d) < -0.2:
                continue
            g.add(arrow(proj(R * d)[:2], proj((R + Lr) * d)[:2], C.field, width=2.2, tip=min(0.12, 0.4 * Lr)))
        rays.add(g)
    m.play(LaggedStart(*[LaggedStart(*[GrowArrow(a) for a in g], lag_ratio=0.03) for g in rays], lag_ratio=0.4),
           at=T.square_dist - 0.6, dur=2.2)
    inv = tex(r"\propto", r"\frac{1}{r^2}", size=52, colors={1: C.field}).move_to([5.3, 1.6, 0])
    m.play(FadeIn(inv, shift=0.1 * LEFT), at=T.square_dist + 0.6, dur=0.7)
    tags = VGroup(*[tex(r"4\pi", size=40, color=C.boundary).move_to(
        [*(O + (R + 0.28) * np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])), 0])
        for R, a in zip(radii, (-62, -42, -24))])
    for tg in tags:
        tg.add_background_rectangle(color=C.bg, opacity=1.0, buff=0.05)
    for tg in tags:
        tg.add_background_rectangle(color=C.bg, opacity=1.0, buff=0.05)
    m.play(LaggedStart(*[FadeIn(tg, scale=0.6) for tg in tags], lag_ratio=0.3), at=T.every_sphere, dur=1.2)
    flux = tex(r"\text{flux}", "=", r"4\pi", size=50, colors={2: C.boundary}).move_to([5.3, 0.6, 0])
    m.play(FadeIn(flux, shift=0.1 * UP), at=T.every_sphere + 1.4, dur=0.7)
    core = Dot(proj([0, 0, 0]), radius=0.11, color=C.div)
    m.play(FadeIn(core, scale=0.3), at=T.sits, dur=0.5)
    m.play(core.animate.scale(1.8), at=T.sits + 0.6, dur=0.4)
    m.play(core.animate.scale(1 / 1.8), at=T.sits + 1.0, dur=0.4)
    charge = VGroup(Circle(radius=0.26, color=C.efield, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1.0),
                    tex("+", size=40, color=C.efield)).move_to(proj([0, 0, 0]))
    m.play(ReplacementTransform(core, charge), at=T.point_charge, dur=0.6, ease="out_back")
    m.play(FadeOut(VGroup(spheres, rays, tags, inv, flux, charge)), at=T.cut_stokes - 0.6, dur=0.5)
