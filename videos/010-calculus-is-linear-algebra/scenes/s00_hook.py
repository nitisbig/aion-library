"""Hook: the hundredth derivative of e^x sin x. Its graph is the shadow, on a wall, of the 3D spiral
(x, e^x cos x, e^x sin x). The product rule splits every term in two: a tree of 2^100 terms that would fill pages. It
collapses into one line, -2^50 e^x sin x: the camera turns, the spiral makes a half turn and its shadow flips. Then why: in the plane spanned by e^x cos x and e^x sin x the function is an arrow, and every
derivative turns it 45 degrees clockwise and stretches it by sqrt 2. A hundred steps: 12.5 turns, length 2^50
(drawn on a log scale so it stays on screen)."""
import sympy as sp

from aion import *

from beats import T
from shots import (D_EXP, FRAME, HO, HU, I2, arrow, axis_marks, backdrop, finish, grid_lines, hook_dir, hook_tip,
                   live, log_rings, plane_labels, plot, pt, result_tag, spiral, tex)

E = "smooth"
f = lambda x: np.exp(x) * np.sin(x)                       # noqa: E731

# the derivatives shown on screen, checked symbolically
_x = sp.symbols("x")
_f = sp.exp(_x) * sp.sin(_x)
assert sp.simplify(sp.diff(_f, _x) - (sp.exp(_x) * sp.sin(_x) + sp.exp(_x) * sp.cos(_x))) == 0
assert sp.simplify(sp.diff(_f, _x, 2) - 2 * sp.exp(_x) * sp.cos(_x)) == 0
assert sp.simplify(sp.diff(_f, _x, 100) + 2 ** 50 * _f) == 0
for k in range(1, 4):                                     # the plane's arrows are the real coordinates of D^k f
    v = np.linalg.matrix_power(D_EXP, k) @ [0.0, 1.0]
    assert np.allclose(v, 2 ** (k / 2) * hook_dir(k))

# ── the 3D stage: the graph of f is the shadow, on a back wall, of the spiral (x, e^x cos x, e^x sin x) ──
# World units are screen units: X = GUX x, the spiral's radius GR e^x. Turning the spiral by theta about its axis
# casts e^x sin(x + theta) on the wall; theta = pi is the hundredth derivative's shape (-2^50 e^x sin x, unscaled).
XA, XB = -5.0, 2.0
GUX, GR = 0.85, 0.40
WALL = GR * np.exp(XB) + 0.35                              # the wall sits just behind the spiral's widest turn
XM = GUX * (XA + XB) / 2                                   # the stage's centre on the x axis
_xs = np.linspace(XA, XB, 420)


def spiral3(theta):
    """(n, 3) points of the spiral turned by theta: (X, Y, Z) with Z = GR e^x sin(x + theta)."""
    r = GR * np.exp(_xs)
    return np.stack([GUX * _xs, r * np.cos(_xs + theta), r * np.sin(_xs + theta)], -1)


def project(P, az, el, S, O):
    """Orthographic camera: turn by az about the vertical, tilt down by el; scale S, screen offset O."""
    P = np.asarray(P, float)
    x, y, z = P[..., 0] - XM, P[..., 1], P[..., 2]
    x1 = x * np.cos(az) - y * np.sin(az)
    y1 = x * np.sin(az) + y * np.cos(az)
    u = x1
    v = z * np.cos(el) + y1 * np.sin(el)
    d = y1 * np.cos(el) - z * np.sin(el)                   # depth into the screen (for dimming the far side)
    return np.stack([O[0] + S * u, O[1] + S * v, np.zeros_like(u)], -1), d


def poly(pts, color, width, opacity=1.0):
    return VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity).set_points_as_corners(pts)


def segments(pairs, color, width, opacity):
    """Many separate straight segments as one VMobject (cheap to draw)."""
    vm = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    for a, b in pairs:
        vm.start_new_path(a)
        vm.add_line_to(b)
    return vm


# ── the product rule as a tree: every term splits in two, (e^x)' trig + e^x trig' ──
TCX, TW, TY0, TDY, NLEV = 3.55, 6.0, 2.75, 0.5, 11


assert np.allclose(spiral3(np.pi)[:, 2], -GR * f(_xs))           # half a turn casts -f (the 2^50 is not drawn)


def tree_levels():
    """Per level k: node positions and kinds ('s' = e^x sin x term, 'c' = e^x cos x term). 2^k terms at level k."""
    kinds = ["s"]
    out = []
    for k in range(NLEV):
        n = 2 ** k
        xs = TCX + TW * ((np.arange(n) + 0.5) / n - 0.5)
        out.append((np.stack([xs, np.full(n, TY0 - k * TDY), np.zeros(n)], -1), kinds))
        kinds = [c for kd in kinds for c in (kd, "c" if kd == "s" else "s")]
    return out


def tree_mobs():
    """One group per level: its edges up to the parents (coloured by the child's kind) and, near the top, dots."""
    lv = tree_levels()
    groups = []
    for k, (P, kinds) in enumerate(lv):
        g = VGroup()
        w = max(0.45, 3.2 - 0.3 * k)
        op = 1.0 - 0.06 * k if k < 7 else 0.32
        if k:
            Q = lv[k - 1][0]
            for kd, col in (("s", C.b2), ("c", C.b1)):
                pairs = [(Q[i // 2], P[i]) for i in range(len(P)) if kinds[i] == kd]
                g.add(segments(pairs, col, w, op))
        if k <= 5:
            r = 0.085 - 0.01 * k
            for i, p in enumerate(P):
                col = C.fn if k == 0 else (C.b2 if kinds[i] == "s" else C.b1)
                g.add(Dot(p, radius=r, color=col))
        groups.append(g)
    return groups


@scene(T.start, T.cut_claim)
def s00_hook(s):
    backdrop(s)
    m = s.manim(z=1)

    # ── the stage: a wall with its grid; the graph of f drawn on it (seen head-on it is just a graph) ──
    t_in, t_l0, t_l1 = 0.3, T.first - 0.4, T.first + 0.6          # fade in; slide left for the tree
    t_o0, t_o1 = T.one_line + 0.4, T.flipped - 0.3                 # orbit: the graph turns out to be a shadow
    t_h0, t_h1 = T.flipped - 0.15, T.flipped + 1.35                # the half turn: flipped upside down
    t_x0, t_x1 = T.see_why, T.see_why + 0.6                        # out
    k_gop = keys((t_in, 0.0), (t_in + 1.0, 1.0), (t_x0, 1.0), (t_x1, 0.0), lead=0)
    k_pc = keys((T.fn - 0.1, 0.0), (T.fn + 1.5, 1.0, "easy_ease"), lead=0)
    k_S = keys((t_l0, 1.0), (t_l1, 0.74, E), (t_o0, 0.74), (t_o1, 0.86, E), lead=0)
    k_OX = keys((t_l0, 0.0), (t_l1, -3.45, E), (t_o0, -3.45), (t_o1, -0.1, E), lead=0)
    k_OY = keys((t_l0, -0.35), (t_l1, -0.35, E), (t_o0, -0.35), (t_o1, -0.6, E), lead=0)
    k_AZ = keys((t_o0, 0.0), (t_o1, np.radians(-30), E), (T.see_why + 0.6, np.radians(-38)), lead=0)
    k_EL = keys((t_o0, 0.0), (t_o1, np.radians(23), E), lead=0)
    k_sp_op = keys((t_o0 + 0.4, 0.0), (t_o1 - 0.2, 1.0), lead=0)
    k_TH = keys((t_h0, 0.0), (t_h1, np.pi, "easy_ease"), lead=0)

    def stage3d(t):
        out = VGroup()
        g = float(k_gop(t))
        if g < 0.005:
            return out
        az, el, S, O, th = float(k_AZ(t)), float(k_EL(t)), float(k_S(t)), (float(k_OX(t)), float(k_OY(t))), float(k_TH(t))
        prj = lambda P: project(P, az, el, S, O)[0]           # noqa: E731
        # the wall's grid: x = -5 … 2, and f = -6 … 6 in steps of 2
        zt = GR * 6.2
        vert = [(prj([GUX * k, WALL, -zt]), prj([GUX * k, WALL, zt])) for k in range(-5, 3)]
        hor = [(prj([GUX * (XA - 0.3), WALL, GR * n]), prj([GUX * (XB + 0.3), WALL, GR * n])) for n in range(-6, 7, 2)
               if n]
        out.add(segments(vert + hor, C.grid, C.thin, 0.45 * g))
        out.add(segments([(prj([GUX * (XA - 0.3), WALL, 0]), prj([GUX * (XB + 0.45), WALL, 0])),
                          (prj([0, WALL, -zt]), prj([0, WALL, zt]))], C.axis, C.thin, g))
        # the spiral, its axis and the projectors, faded in as the camera turns
        so = float(k_sp_op(t)) * g
        P3 = spiral3(th)
        if so > 0.005:
            out.add(poly(prj([[GUX * (XA - 0.3), 0, 0], [GUX * (XB + 0.45), 0, 0]]), C.axis, C.thin, 0.6 * so))
            spokes, proj_ = [], []                                  # spokes from the axis: the spiral's twist
            for x in np.linspace(-2.6, XB, 64):
                r = GR * np.exp(x)
                a = np.array([GUX * x, r * np.cos(x + th), r * np.sin(x + th)])
                spokes.append((prj([a[0], 0, 0]), prj(a)))
            for x in np.linspace(-0.5, XB, 8):                      # a few projectors onto the wall
                r = GR * np.exp(x)
                a = np.array([GUX * x, r * np.cos(x + th), r * np.sin(x + th)])
                proj_.append((prj(a), prj([a[0], WALL, a[2]])))
            out.add(segments(spokes, C.text, C.thin, 0.28 * so))
            out.add(segments(proj_, C.fn, C.thin, 0.3 * so))
            pts, d = project(P3, az, el, S, O)
            dn = (d - d.min()) / max(np.ptp(d), 1e-6)
            for j in range(0, len(pts) - 1, 12):                     # nearer turns brighter
                seg = pts[j:j + 13]
                out.add(poly(seg, C.text, C.stroke - 0.5, so * (0.95 - 0.6 * float(dn[j:j + 13].mean()))))
        # the shadow on the wall: the graph of e^x sin(x + theta), drawn on with k_pc
        sh = P3.copy()
        sh[:, 1] = WALL
        n = max(2, int(len(sh) * float(k_pc(t))))
        out.add(poly(prj(sh[:n]), C.fn, C.stroke + 0.5, g))
        return out

    live(m, stage3d, (t_in, T.fn + 1.5), (t_l0, t_l1), (t_o0, t_x1))

    f0 = tex(r"f", r"=", r"e^x\sin x", colors={0: C.fn, 2: C.fn}).move_to([-3.55, 3.15, 0])
    m.play(FadeIn(f0, shift=0.15 * UP), at=T.fn + 1.1, dur=0.6)

    # ── each derivative: the product rule splits every term in two ──
    lv = tree_mobs()
    m.play(GrowFromCenter(lv[0]), at=T.first - 0.2, dur=0.5)
    m.play(Create(lv[1]), at=T.first + 0.6, dur=0.8)
    m.play(Create(lv[2]), at=T.second + 0.3, dur=0.8)
    labs = VGroup(*[tex(s_, size=32, color=C.fn) for s_ in ("f", "f'", "f''")])
    for k, l in enumerate(labs):
        l.move_to([0.2, TY0 - k * TDY, 0])
    m.play(FadeIn(labs[0]), at=T.first - 0.1, dur=0.4)
    m.play(FadeIn(labs[1]), at=T.first + 0.7, dur=0.4)
    m.play(FadeIn(labs[2]), at=T.second + 0.4, dur=0.4)

    q = tex(r"f^{(100)}", r"=", r"\,?", size=54, colors={0: C.fn}).move_to([TCX, -3.25, 0])
    m.play(FadeIn(q, scale=0.9), at=T.hundredth + 0.2, dur=0.6, ease="out_back")
    t_g = T.pages - 2.4                                            # "Grinding": the tree runs away
    for k in range(3, NLEV):
        m.play(Create(lv[k]), at=t_g + 0.3 * (k - 3), dur=0.5)
    many = tex(r"2^{100}", size=36, color=C.muted).move_to([0.2, TY0 - (NLEV - 1) * TDY, 0])
    m.play(FadeIn(many), at=T.pages + 0.3, dur=0.5)

    # ── the answer fits on one line: the whole tree collapses into it ──
    tree = VGroup(*lv)
    ans = tex(r"f^{(100)}", r"=", r"-2^{50}", r"\,e^x\sin x", size=54, colors={0: C.fn, 2: C.op, 3: C.fn})
    ans.move_to([0.0, 3.3, 0])
    m.play(FadeOut(tree, target_position=ans.get_center(), scale=0.04), FadeOut(labs), FadeOut(many),
           FadeOut(f0), at=T.one_line - 0.1, dur=0.9, ease="easy_ease")
    m.play(TransformMatchingTex(q, ans), at=T.one_line + 0.5, dur=0.9)
    m.play(Indicate(ans[2], color=C.op, scale_factor=1.12), at=T.flipped + 2.0, dur=0.9)


    # ── and you can see why: the function plane ──
    tag = result_tag()
    m.play(ReplacementTransform(ans, tag[1]), FadeIn(tag[0]), at=T.see_why + 0.1, dur=0.9)

    m2 = s.manim(z=0)                                             # the grid, then the coloured axes and their names
    m3 = s.manim(z=0.8)                                           # the arrow, rings and trail (under the tag)
    gop = keys((T.plane - 0.2, 0.0), (T.plane + 0.8, 1.0), (T.every_derivative + 2.6, 1.0),
               (T.every_derivative + 3.4, 0.18), lead=0)
    oc = keys((T.axis_cos - 0.1, 0.0), (T.axis_cos + 0.5, 1.0), lead=0)
    osn = keys((T.axis_sin - 0.1, 0.0), (T.axis_sin + 0.5, 1.0), lead=0)
    live(m2, lambda t: VGroup(grid_lines(I2, HO, HU, FRAME, opacity=0.6 * gop(t)), axis_marks(oc(t), osn(t)),
                              plane_labels(oc(t), osn(t))),
         (T.plane - 0.2, T.plane + 0.8), (T.axis_cos - 0.1, T.axis_sin + 0.5),
         (T.every_derivative + 2.6, T.every_derivative + 3.4))

    # ── the arrow, one step at a time (linear scale), then a hundred (log scale) ──
    steps = [(T.turns, T.turns + 1.1), (T.stretches, T.stretches + 0.9),          # step 1: turn, then stretch
             (T.every_derivative, T.every_derivative + 1.0), (T.every_derivative + 1.3, T.every_derivative + 2.3)]
    ang1 = keys((steps[0][0], 0.0), (steps[0][1], 1.0, E), lead=0)               # step 1 turn
    len1 = keys((steps[1][0], 0.0), (steps[1][1], 1.0, E), lead=0)               # step 1 stretch
    n23 = keys((steps[2][0], 1.0), (steps[2][1], 2.0, E), (steps[3][0], 2.0), (steps[3][1], 3.0, E), lead=0)
    t_log0, t_log1 = T.every_derivative + 2.6, T.every_derivative + 3.4          # switch to the log scale
    wlog = keys((t_log0, 0.0), (t_log1, 1.0, E), lead=0)
    t_s0, t_s1 = T.spin, T.backwards + 0.1
    nspin = keys((t_s0, 3.0), (t_s1, 100.0, "easy_ease"), lead=0)
    a_op = keys((T.arrow - 0.1, 0.0), (T.arrow + 0.4, 1.0), lead=0)
    ring_op = keys((t_log0, 0.0), (t_log1, 1.0), lead=0)
    hi = keys((T.stretched, 0.0), (T.stretched + 0.6, 1.0), lead=0)
    z0 = pt(HO, 1.0, (0, 0))

    def n_of(t):
        if t < steps[2][0]:
            return 1.0 if t >= steps[0][0] else 0.0
        return float(nspin(t)) if t >= t_s0 else float(n23(t))

    def stage(t):
        out = VGroup()
        w = float(wlog(t))
        if ring_op(t) > 0.01:
            out.add(log_rings(ring_op(t), hi(t)))
            n = n_of(t)
            if n > 3.001:
                out.add(spiral(n, ring_op(t)))
        if t < steps[2][0]:                                   # step 1: turn first, then stretch
            a = np.radians(90 - 45 * ang1(t))
            L = HU * (1 + (np.sqrt(2) - 1) * len1(t))
            tip = z0 + L * np.array([np.cos(a), np.sin(a), 0])
            if ang1(t) > 0.01:                               # the turn, measured from where it started
                arc = Arc(radius=0.75, start_angle=PI / 2, angle=-PI / 4 * ang1(t), arc_center=z0,
                          stroke_color=C.text, stroke_width=C.thin)
                out.add(arc)
                if ang1(t) > 0.6:
                    lab = tex(r"45^\circ", size=26).set_opacity(min(1, (ang1(t) - 0.6) / 0.3))
                    out.add(lab.move_to(z0 + 1.15 * np.array([np.cos(np.radians(67.5)), np.sin(np.radians(67.5)), 0])))
            if len1(t) > 0.01:
                sl = tex(r"\times\sqrt{2}", size=30).set_opacity(min(1, len1(t) / 0.5))
                out.add(sl.next_to(tip, RIGHT, buff=0.15))
            out.add(arrow(z0, tip, C.fn, width=C.stroke + 1.5, opacity=a_op(t)))
        else:
            n = n_of(t)
            out.add(arrow(z0, hook_tip(n, w), C.fn, width=C.stroke + 1.5))
        return out

    live(m3, stage, (T.arrow - 0.1, T.arrow + 0.4), (steps[0][0], steps[1][1]), (steps[2][0], steps[3][1]),
         (t_log0, t_log1), (t_s0, t_s1), (T.stretched, T.stretched + 0.6))

    # derivative labels on the first steps, the counter during the spin
    fl = tex(r"f", size=34, color=C.fn).next_to(pt(HO, HU, (0, 1)), LEFT, buff=0.15)
    m.play(FadeIn(fl), at=T.arrow + 0.2, dur=0.5)
    m.play(FadeOut(fl), at=T.turns, dur=0.4)
    for k, (a, b) in ((1, steps[1]), (2, steps[2]), (3, steps[3])):
        tip = hook_tip(k, 0.0)
        d = hook_dir(k)
        lab = tex("f" + "'" * k, size=34, color=C.fn).move_to(tip + 0.42 * np.array([-d[1], d[0], 0]) + 0.15 * np.array([*d, 0]))
        m.play(FadeIn(lab), at=b - 0.1, dur=0.4)
        m.play(FadeOut(lab), at=steps[k + 1][0] if k < 3 else t_log0, dur=0.3)

    neq = tex(r"n", r"=", size=40, colors={0: C.fn}).move_to([4.7, 2.75, 0])
    m.play(FadeIn(neq), at=t_s0 - 0.3, dur=0.4)
    m.redraw(lambda t: tex(str(int(round(n_of(t)))), size=40).next_to(neq, RIGHT, buff=0.22),
             during=(t_s0 - 0.3, t_s1 + 0.05))

    # stretched by root two, a hundred times over: (sqrt 2)^100 = 2^50
    pw = tex(r"(\sqrt{2})^{100}", r"=", r"2^{50}", size=40, colors={2: C.fn}).move_to([4.6, -2.9, 0])
    m.play(FadeIn(pw, shift=0.15 * UP), at=T.stretched + 0.4, dur=0.7)
    m.play(Indicate(pw[2], color=C.fn, scale_factor=1.15), at=T.fiftieth + 0.3, dur=0.9)
    finish(s)
