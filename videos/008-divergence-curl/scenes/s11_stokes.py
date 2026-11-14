"""Ch4 · adding up the little loops: Green's and Stokes' theorems. The region from the divergence theorem comes back;
each small square gets its own counter-clockwise loop. Two neighbours: along their shared edge the loops run in
opposite directions and cancel. Every inside edge goes, leaving the outer loop (with the curl map inside), and
Green's theorem assembles. Then the outline lifts into 3D and rounds into a wire loop; a soap film spans it and bulges
into a bubble while the flux of the curl through it stays at 2 pi. Only the wire matters: Stokes' theorem. Last, the
two theorems stacked: in both, the boundary term is all that survives."""
from aion import *

from beats import T
from shots import (BADGES, REG_C, REG_H, arrow, dim, ease, hero_curl, oiint, ortho, ramp, region, boundary_loop,
                   sample_grid, stage, tex)

E = "easy_ease"
FULL = (14.4, 8.2)
RES = (320, 180)
REG = region()
CELLS = np.array(REG["cells"])
UP4 = (np.array([1.0, 0]), np.array([0, 1.0]), np.array([-1.0, 0]), np.array([0, -1.0]))
C3 = np.array([0.7, -0.75])                     # 3D view centre (world)
RW = 2.1                                        # wire radius (world units); the maths uses r / RW
NP = 240                                        # points on the morphing loop


def mini_loop(c, r=0.17, color=None, width=2.2):
    """A small counter-clockwise loop glyph (300 degree arc with a tip) centred on c."""
    arc = Arc(radius=r, start_angle=np.radians(-60), angle=np.radians(290), color=color or C.curl,
              stroke_width=width).move_arc_center_to([*c, 0])
    end = arc.point_from_proportion(1.0)[:2]
    back = arc.point_from_proportion(0.9)[:2]
    d = (end - back) / np.linalg.norm(end - back)
    tip = Triangle(color=color or C.curl, fill_opacity=1, stroke_width=0).scale(0.055)
    tip.rotate(np.arctan2(d[1], d[0]) - np.pi / 2).move_to([*(end + 0.02 * d), 0])
    return VGroup(arc, tip)


def cell_loop(c, size, inset=0.08, color=None, width=None, tip=0.12):
    """A square's own counter-clockwise circulation: four arrows just inside its edges. Order: bottom, right, top, left."""
    c = np.asarray(c, float)
    h = size / 2 - inset
    corners = [c + np.array(p) * h for p in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    g = VGroup()
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        g.add(arrow(a + 0.12 * (b - a), a + 0.88 * (b - a), color or C.curl, width=width or C.stroke, tip=tip))
    return g


def resample(loop, n):
    """Resample a closed polyline to n points by arc length."""
    P = np.array(loop + [loop[0]], float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], n, endpoint=False)
    return np.stack([np.interp(u, s, P[:, 0]), np.interp(u, s, P[:, 1])], 1)


def film_flux(h, n=120):
    """Flux of curl F = (0, 0, 2) (F = (-y, x, 0), unit wire) through the film z = h (1 - r^2): computed, not assumed."""
    r = np.linspace(0, 1, n + 1)
    th = np.linspace(0, 2 * np.pi, n + 1)
    rm, tm = (r[1:] + r[:-1]) / 2, (th[1:] + th[:-1]) / 2
    R, TH = np.meshgrid(rm, tm, indexing="ij")
    # surface X(r, th) = (r cos th, r sin th, h (1 - r^2)); dX/dr x dX/dth, z component = r
    Xr = np.stack([np.cos(TH), np.sin(TH), -2 * h * R])
    Xt = np.stack([-R * np.sin(TH), R * np.cos(TH), 0 * R])
    nrm = np.cross(Xr, Xt, axis=0)
    curl = np.array([0.0, 0.0, 2.0])[:, None, None]
    return float(np.sum((curl * nrm).sum(0)) * np.diff(r)[0] * np.diff(th)[0])


@scene(T.cut_stokes, T.cut_ch5)
def s11_stokes(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:3])
    t_lift = (T.lift - 0.2, T.lift + 1.8)

    # ── the region again, cut into squares ──
    c0 = CELLS[int(np.argmin(np.linalg.norm(CELLS - REG_C, axis=1)))]
    edges_in = VGroup(*[Line([*a, 0], [*b, 0], color=C.muted, stroke_width=C.thin) for a, b, _, _ in REG["inner"]])
    edges_out = VGroup(*[Line([*a, 0], [*b, 0], color=C.frame, stroke_width=C.thin + 0.5) for a, b, _, _ in REG["outer"]])
    d_in = [np.linalg.norm((np.asarray(a) + b) / 2 - c0) for a, b, _, _ in REG["inner"]]
    m.play(FadeIn(edges_out), at=T.curl_adds, dur=0.9)
    m.play(LaggedStart(*[FadeIn(e) for _, e in sorted(zip(d_in, edges_in), key=lambda z: z[0])], lag_ratio=0.012),
           at=T.curl_adds + 0.4, dur=1.4)

    # ── each square, its own little loop (on its own layer so it can step back) ──
    k_loops = keys((s.start, 1.0), (T.meet - 0.2, 1.0), (T.meet + 0.6, 0.22, E), (T.cancel_again + 0.8, 0.22),
                   (T.outer + 0.6, 0.0, E), lead=0)
    ml = s.manim(z=3, opacity=k_loops)
    order = np.argsort(np.linalg.norm(CELLS - c0, axis=1))
    loops = [mini_loop(CELLS[k]) for k in order]
    ml.play(LaggedStart(*[FadeIn(g, scale=0.4) for g in loops], lag_ratio=0.025), at=T.loops, dur=1.8)
    ml.play(LaggedStart(*[Rotate(g, angle=2 * np.pi, about_point=g[0].get_arc_center()) for g in loops],
                        lag_ratio=0.01), at=T.loops + 1.9, dur=1.4, ease="smooth")

    # ── two neighbours: along the shared edge the loops run opposite ways ──
    kA = int(order[0])
    kB = REG["idx"].get(next(((i + 1, j) for (i, j), kk in REG["idx"].items() if kk == kA)))
    pair = VGroup(*[Square(side_length=REG_H, color=C.boundary, stroke_width=C.stroke).move_to([*CELLS[k], 0])
                    for k in (kA, kB)])
    ZC, ZK = np.array([4.95, 0.1]), 2.4             # a zoomed copy of the pair, to the right of the region
    zA = ZC + np.array([-REG_H / 2, 0]) * ZK
    zB = ZC + np.array([REG_H / 2, 0]) * ZK
    zpair = VGroup(*[Square(side_length=REG_H * ZK, color=C.boundary, stroke_width=C.stroke).move_to([*z, 0])
                     for z in (zA, zB)])
    la = cell_loop(zA, REG_H * ZK, inset=0.14, width=C.stroke + 1, tip=0.2)
    lb = cell_loop(zB, REG_H * ZK, inset=0.14, width=C.stroke + 1, tip=0.2)
    m.play(Create(pair), at=T.meet, dur=0.6)
    m.play(TransformFromCopy(pair, zpair), at=T.meet + 0.3, dur=0.9, ease=E)
    m.play(LaggedStart(*[GrowArrow(a) for a in la], lag_ratio=0.25), at=T.meet + 0.5, dur=1.0)
    m.play(LaggedStart(*[GrowArrow(a) for a in lb], lag_ratio=0.25), at=T.meet + 1.3, dur=1.0)
    up, down = la[1], lb[3]                     # A's right edge runs up, B's left edge runs down
    m.play(up.animate.set_color(C.text).set_stroke(width=C.stroke + 2),
           down.animate.set_color(C.text).set_stroke(width=C.stroke + 2), at=T.opposite, dur=0.6)
    m.play(up.animate.shift(0.14 * RIGHT).scale(0.25), down.animate.shift(0.14 * LEFT).scale(0.25),
           zpair[0].animate.set_stroke(opacity=0.35), zpair[1].animate.set_stroke(opacity=0.35),
           at=T.cancel_again, dur=0.8, ease=E)
    m.play(FadeOut(VGroup(up, down)), at=T.cancel_again + 0.7, dur=0.3)
    rest = VGroup(la[0], la[2], la[3], lb[0], lb[1], lb[2])

    # ── every inside edge cancels; only the outer loop survives ──
    flashes = [Succession(edges_in[i].animate(run_time=0.2).set_stroke(C.curl, opacity=1.0),
                          edges_in[i].animate(run_time=0.3).set_stroke(opacity=0.0)) for i in np.argsort(d_in)]
    m.play(FadeOut(VGroup(rest, zpair, pair)), LaggedStart(*flashes, lag_ratio=0.03), at=T.outer - 0.6, dur=3.0)
    bl = boundary_loop(REG)
    bpoly = VMobject(stroke_color=C.boundary, stroke_width=C.stroke + 1.5).set_points_as_corners(
        [[*p, 0] for p in bl + [bl[0]]])
    m.play(FadeIn(bpoly), FadeOut(edges_out), at=T.outer, dur=0.8)
    heads = VGroup()
    for i in range(0, len(bl), max(1, len(bl) // 9)):
        p, q = np.asarray(bl[i]), np.asarray(bl[(i + 1) % len(bl)])
        heads.add(arrow(p + 0.15 * (q - p), p + 0.85 * (q - p), C.boundary, width=C.stroke + 1.5, tip=0.2))
    m.play(LaggedStart(*[GrowArrow(hd) for hd in heads], lag_ratio=0.12), at=T.outer + 0.7, dur=1.4)

    # the curl inside, as a map under the region (green turns counter-clockwise, pink clockwise)
    Cu = sample_grid(hero_curl, (0, 0), FULL, res=RES)
    xs = np.linspace(-FULL[0] / 2, FULL[0] / 2, RES[0])
    ys = np.linspace(-FULL[1] / 2, FULL[1] / 2, RES[1])
    X, Y = np.meshgrid(xs, ys)
    mask = np.zeros_like(Cu)
    for cx, cy in CELLS:
        mask[(np.abs(X - cx) <= REG_H / 2) & (np.abs(Y - cy) <= REG_H / 2)] = 1.0
    k_map = keys((s.start, 0.0), (T.total_curl - 0.2, 0.0), (T.total_curl + 1.2, 0.45, E), (t_lift[0] - 0.5, 0.45),
                 (t_lift[0] + 0.1, 0.0, E), lead=0)
    s.add(FieldLayer(lambda t: Cu * mask, cmap="diverging", vmin=-3.0, vmax=3.0, extent=FULL,
                     colors=(C.cw, C.bg, C.curl), animated=False, z=-20, opacity=k_map))

    # Green's theorem
    eq_g = tex(r"\iint", r"\Big(\frac{\partial Q}{\partial x}-\frac{\partial P}{\partial y}\Big)", r"\,dA", "=",
               r"\oint", r"\mathbf{F}\cdot d\mathbf{r}", size=52, colors={1: C.curl, 4: C.boundary})
    eq_g.move_to([REG_C[0], 3.0, 0])
    m.play(FadeIn(eq_g[0:4], shift=0.1 * RIGHT), at=T.total_curl + 0.3, dur=0.8)
    m.play(FadeIn(eq_g[4:], shift=0.1 * LEFT), at=T.total_curl + 1.9, dur=0.8)

    # ── lift into space: the outline tilts back and rounds into a wire loop ──
    m.play(FadeOut(VGroup(bpoly, heads)), at=t_lift[0] - 0.05, dur=0.15)
    el = keys((s.start, np.radians(90)), (t_lift[0], np.radians(90)), (t_lift[1], np.radians(22), E), lead=0)
    az = keys((s.start, 0.0), (t_lift[0], 0.0), (t_lift[1], np.radians(-28), E), lead=0)
    B = resample(bl, NP) - REG_C                # outline, centred on the region
    ang = np.arctan2(B[:, 1], B[:, 0])
    Ci = np.stack([RW * np.cos(ang), RW * np.sin(ang)], 1)
    k_round = (T.wire - 0.6, T.wire + 0.8)
    cen = lambda t: REG_C + (C3 - REG_C) * ease(t, *t_lift)
    h_tr = keys((s.start, 0.0), (T.bubble - 0.1, 0.0), (T.bubble + 1.9, 1.9, E), (T.only_wire - 0.6, 1.9),
                (T.only_wire + 1.0, 0.9, E), lead=0)
    k_film = (T.soap - 0.2, T.soap + 0.8)
    t_out = (T.one_idea - 0.6, T.one_idea + 0.1)

    def world3d(t):
        k = 1 - ramp(t, *t_out)
        if k < 0.01:
            return VGroup()
        proj = ortho(float(az(t)), float(el(t)), scale=1.0, center=cen(t))
        g = VGroup()
        u = ease(t, *k_round)
        P2 = (1 - u) * B + u * Ci
        pulse = 1 + 0.9 * np.exp(-((t - T.only_wire - 0.4) / 0.35) ** 2)
        wire = [proj([x, y, 0.0]) for x, y in P2]
        g.add(VMobject(stroke_color=C.boundary, stroke_width=(C.stroke + 1.5) * pulse, stroke_opacity=k)
              .set_points_as_corners(wire + [wire[0]]))
        # the direction of travel, four arrowheads along the wire
        kh = ramp(t, T.wire + 0.3, T.wire + 0.9)
        if kh > 0.01:
            for j in range(4):
                i0 = j * NP // 4 + NP // 8
                p, q = proj([*P2[i0], 0]), proj([*P2[(i0 + 6) % NP], 0])
                g.add(arrow(p, q, C.boundary, width=C.stroke + 1.5, tip=0.2, opacity=k * kh))
        # the film z = h (1 - r^2): rings and meridians, with the curl arrows passing through
        kf = ramp(t, *k_film) * k
        if kf > 0.01:
            h = float(h_tr(t))
            th = np.linspace(0, 2 * np.pi, 97)
            for rr in (0.25, 0.5, 0.75):
                pts = [proj([rr * RW * np.cos(a), rr * RW * np.sin(a), h * (1 - rr * rr)]) for a in th]
                g.add(VMobject(stroke_color=C.curl, stroke_width=C.thin * 0.8, stroke_opacity=0.6 * kf)
                      .set_points_as_corners(pts))
            rs = np.linspace(0, 1, 25)
            for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):
                pts = [proj([r * RW * np.cos(a), r * RW * np.sin(a), h * (1 - r * r)]) for r in rs]
                g.add(VMobject(stroke_color=C.curl, stroke_width=C.thin * 0.8, stroke_opacity=0.6 * kf)
                      .set_points_as_corners(pts))
            kc = ramp(t, T.soap + 0.6, T.soap + 1.2) * kf
            if kc > 0.01:
                for rr, a in [(0.0, 0.0)] + [(0.55, a) for a in np.linspace(0.4, 2 * np.pi + 0.4, 6, endpoint=False)]:
                    p = np.array([rr * RW * np.cos(a), rr * RW * np.sin(a), h * (1 - rr * rr)])
                    g.add(arrow(proj(p), proj(p + np.array([0, 0, 0.7])), C.curl, width=2.6, tip=0.12, opacity=kc))
        return g
    m.redraw(world3d, during=(t_lift[0], t_out[1] + 0.05))

    # the readout: flux of the curl through the film (computed for each shape) = circulation round the wire
    def readout(t):
        k = ramp(t, T.soap + 0.4, T.soap + 1.0) * (1 - ramp(t, *t_out))
        if k < 0.01:
            return VGroup()
        lab = tex(r"\text{flux}", size=40, color=C.muted).move_to([5.4, 0.9, 0])
        v = film_flux(float(h_tr(t)))
        pulse = 1 + 0.12 * np.exp(-((t - T.no_change - 0.3) / 0.3) ** 2)
        num = DecimalNumber(v, num_decimal_places=2, font_size=58, color=C.curl).scale(pulse).move_to([5.4, 0.25, 0])
        two = tex(r"=2\pi", size=40, color=C.muted).move_to([5.4, -0.45, 0])
        two.set_opacity(ramp(t, T.no_change, T.no_change + 0.6))
        return VGroup(lab, num, two) if k >= 0.999 else dim(VGroup(lab, num, two), k)
    m.redraw(readout, during=(T.soap + 0.4, t_out[1] + 0.05))

    # Stokes' theorem replaces Green's
    eq_s = VGroup(tex(r"\iint", r"(\nabla\times\mathbf{F})\cdot\mathbf{n}", r"\,dS", "=", r"\oint",
                      r"\mathbf{F}\cdot d\mathbf{r}", size=52, colors={1: C.curl, 4: C.boundary}))
    eq_s.move_to([REG_C[0], 3.0, 0])
    m.play(FadeOut(eq_g), at=T.stokes - 0.5, dur=0.5)
    m.play(FadeIn(eq_s, shift=0.1 * UP), at=T.stokes + 0.1, dur=0.8)

    # ── two theorems, one idea: the boundary term is what survives ──
    eq_d = VGroup(tex(r"\iiint", r"\nabla\cdot\mathbf{F}", r"\,dV", "=", size=52, colors={1: C.div}),
                  oiint(r"\mathbf{F}\cdot\mathbf{n}\,dS", size=52, color=C.boundary, rest_color=C.text))
    eq_d.arrange(RIGHT, buff=0.18)
    stack_y = (1.0, -0.6)
    eq_d.move_to([0.9, stack_y[0], 0])
    eq_s2 = eq_s.copy().move_to([0.9, stack_y[1], 0])
    m.play(ReplacementTransform(eq_s, eq_s2), at=T.one_idea, dur=1.0, ease=E)
    m.play(FadeIn(eq_d, shift=0.1 * DOWN), at=T.one_idea + 0.5, dur=0.8)
    lhs = VGroup(eq_d[0][0:3], eq_s2[0][0:3])
    rhs = VGroup(VGroup(eq_d[1]), eq_s2[0][4:])
    m.play(lhs.animate.set_opacity(0.4), at=T.except_edge - 0.2, dur=0.6)
    boxes = VGroup(*[SurroundingRectangle(r, color=C.boundary, buff=0.12, stroke_width=C.stroke) for r in rhs])
    m.play(LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.3), at=T.except_edge + 0.2, dur=1.0)
    m.play(FadeOut(VGroup(eq_d, eq_s2, boxes)), at=T.cut_ch5 - 0.7, dur=0.6)
