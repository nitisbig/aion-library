"""s10: the trail is the level set g = c of a bowl, everything off it is forbidden, freedom drops from two directions to one, and the trail unrolls into a one-variable graph, which tangled trails will not allow."""
from aion import *

from beats import T
from ch1 import *

HC = 1.45                                   # the bowl's height at g = c
SS = np.linspace(0, TAU, 241)
S_LO = BEST_S - np.pi                       # unroll from here, so the trail's best point sits mid-graph
W0 = 3.6                                    # where the walker stops to look around
GX0, GX1, GY = -4.6, 4.6, -3.0              # the unrolled graph's baseline in the world


def ell(s):
    return np.column_stack(trail(np.asarray(s, float)))


def tangled(s):
    s = np.asarray(s, float)
    return np.column_stack([2.3 * np.cos(s) + 0.85 * np.cos(4 * s + 0.3), 1.85 * np.sin(s) - 0.85 * np.sin(4 * s + 0.3)])


def flat(s, u):
    """The trail at parameter s, unrolled by u onto the graph's baseline: (x, y) on the way, height kept."""
    s = np.asarray(s, float)
    a = ell(s)
    b = np.column_stack([GX0 + (GX1 - GX0) * (np.mod(s - S_LO, TAU)) / TAU, np.full_like(s, GY)])
    return a + (b - a) * u


@scene(T.cut_constraint, T.cut_ch2)
def s10_constraint(s):
    backdrop(s)
    wp = ell([W0])[0]
    top = (-90, 89.5, 2.2, 0.0, -0.2, 400, wp[0], wp[1], float(hill(*wp)))
    side = (-90, 6, 1.2, 0.0, -0.9, 90, 0.0, GY, 1.2)
    cam = camera(
        (T.cut_constraint, OVER),
        (T.rule, (-62, 35, 1.1, 0.1, -0.9, 26, 0, 0, 0)),
        (T.rule + 1.8, (-58, 26, 1.12, 0.0, -0.6, 26, 0, 0, 0.5)),
        (T.on_path - 0.6, (-56, 27, 1.12, 0.0, -0.6, 26, 0, 0, 0.5)),
        (T.on_path + 0.8, (-66, 38, 1.12, 0.1, -0.8, 26, 0, 0, 0)),
        (T.look, (-78, 44, 1.12, 0.1, -0.8, 26, 0, 0, 0)),
        (T.two_dir - 0.1, top),
        (T.formula, top),
        (T.formula + 2.6, side),
        (T.tangled + 0.2, side),
        (T.tangled + 2.6, (-58, 38, 1.08, 0.1, -0.9, 26, 0, 0, 0)),
        (T.cut_ch2, (-44, 40, 1.08, 0.1, -0.9, 26, 0, 0, 0)),
    )
    draw = lambda t: ramp(t, T.add_trail, T.add_trail + 1.8)
    ghost = lambda t: win(t, T.rule + 0.1, T.on_path, 0.9, 0.9)            # the mountain steps aside for the bowl
    drop = lambda t: win(t, T.rule + 0.5, T.on_path, 1.0, 1.0)             # the trail lies down on the ground
    bowl = lambda t: win(t, T.rule + 1.4, T.on_path - 0.5, 1.2, 1.0)
    cut_h = lambda t: HC * ramp(t, T.rule + 2.6, T.g_eq - 0.3)
    bad = lambda t: win(t, T.forbid - 0.1, T.formula - 0.4, 0.8, 1.2)
    unroll = lambda t: ramp(t, T.formula + 0.6, T.formula + 3.0) * (1 - ramp(t, T.tangled + 0.1, T.tangled + 2.2))
    fence = lambda t: win(t, T.formula + 0.1, T.tangled + 2.4, 0.6, 0.6)
    knot = lambda t: ramp(t, T.tangled + 2.2, T.tangled + 4.4)
    w_s = lambda t: 2.2 + (W0 - 2.2) * ramp(t, T.on_path - 0.1, T.forbid + 0.6)

    def tint(X, Y, cols, f):
        d = np.abs(np.hypot(X / TRAIL_A, Y / TRAIL_B) - 1.0)
        a = (np.clip((d - 0.06) / 0.16, 0, 1) * f)[..., None]
        fall = np.clip((6.3 - np.hypot(X, Y)) / 2.4, 0, 1)[..., None] ** 1.4
        return cols * (1 - 0.68 * a) + rgb(C.wrong) * 0.16 * a * fall

    def frame(t):
        v = view().begin(cam(t))
        gh, f = ghost(t), bad(t)
        ma = max(0.0, 1.0 - 0.9 * gh - 0.94 * unroll(t))
        mountain(v, 1.0, ma, tint=(lambda X, Y, c: tint(X, Y, c, f)) if f > 0.01 else None)
        floor(v, 1.0 - gh, 0.55)
        if ma > 0.5:
            wires(v, 1.0, 0.24 * ma)
            contours(v, 1.0, C.bg, 0.5 * ma, 1.8)
        # the bowl g(x, y) and the plane at height c
        b = bowl(t)
        if b > 0.01:
            r, th = np.meshgrid(np.linspace(0, 1.22, 24), np.linspace(0, TAU, 73))
            X, Y = TRAIL_A * r * np.cos(th), TRAIL_B * r * np.sin(th)
            Z = HC * r**2 * ramp(t, T.rule + 1.4, T.rule + 2.6)
            v.mesh(X, Y, Z, C.con, alpha=0.42 * b, ambient=0.45)
            for rr in (0.4, 0.7, 1.0, 1.22):
                v.line(np.column_stack([TRAIL_A * rr * np.cos(SS), TRAIL_B * rr * np.sin(SS), Z.max() / 1.22**2 * rr**2 * np.ones_like(SS)]), C.con, 1.2, 0.5 * b)
            h = cut_h(t)
            if h > 0.02:
                q = np.linspace(-3.6, 3.6, 2)
                PX_, PY_ = np.meshgrid(q, q)
                v.mesh(PX_, PY_, np.full_like(PX_, h), C.text, alpha=0.16 * b, shade=False)
                v.line([[-3.6, -3.6, h], [3.6, -3.6, h], [3.6, 3.6, h], [-3.6, 3.6, h]], C.text, 1.6, 0.6 * b, close=True)
                rr = np.sqrt(h / HC)
                v.line(np.column_stack([TRAIL_A * rr * np.cos(SS), TRAIL_B * rr * np.sin(SS), np.full_like(SS, h + 0.01)]), C.con, 6.0, b)
        # the trail: drawn on the mountain, lies down on the ground for the bowl, then unrolls or tangles
        dr = drop(t)
        n = max(2, int(len(SS) * draw(t)))
        if draw(t) > 0.005:
            k, u, kn = 1.0 - dr, unroll(t), knot(t)
            if kn > 0.001:
                xy = ell(SS) + (tangled(SS) - ell(SS)) * kn
                curve(v, xy, C.con, 6.0, 1.0, k=k)
            elif u > 0.001:
                xy = flat(SS, u)
                z = hill(*ell(SS).T) + 0.04
                order = np.argsort(np.mod(SS - S_LO, TAU)) if u > 0.5 else np.arange(len(SS))
                v.line(np.column_stack([xy, z])[order], C.con, 6.0)
            else:
                curve(v, ell(SS[:n]), C.con, 6.0, 1.0, k=k)
        # the fence under the trail, which becomes the area under the graph
        fe = fence(t)
        if fe > 0.01:
            u = unroll(t)
            o = np.argsort(np.mod(SS - S_LO, TAU))
            xy, z = flat(SS[o], u), hill(*ell(SS[o]).T)
            v.mesh(np.vstack([xy[:, 0], xy[:, 0]]), np.vstack([xy[:, 1], xy[:, 1]]), np.vstack([np.zeros_like(z), z]), C.con, alpha=0.22 * fe, shade=False)
            ga = fe * ramp(t, T.formula + 2.2, T.formula + 3.0)
            if ga > 0.01:
                v.arrow([GX0 - 0.2, GY, 0], [GX1 + 0.5, GY, 0], C.axis, width=3.0, tip=0.18, alpha=ga)
                v.arrow([GX0, GY, -0.1], [GX0, GY, 3.6], C.axis, width=3.0, tip=0.18, alpha=ga)
                xb = GX0 + (GX1 - GX0) * np.pi / TAU
                v.line([[xb, GY, 0], [xb, GY, BEST_H]], C.you, 2.4, 0.8 * ga)
                v.dot([xb, GY, BEST_H + 0.04], C.you, 0.1, ring=C.bg)
        # the walker
        wa = win(t, T.on_path - 0.3, T.formula + 0.2, 0.5, 0.5)
        if wa > 0.01:
            bead(v, ell([w_s(t)])[0], r=0.1 * wa + 1e-3)
        # two directions, then one
        fa = win(t, T.two_dir, T.formula + 0.1, 0.6, 0.5)
        if fa > 0.01:
            p = lift(ell([W0]), 1.0, 0.06)[0]
            tg = trail_tangent(W0)
            tg = tg / np.linalg.norm(tg)
            nr = np.array([-tg[1], tg[0]])
            grow = ramp(t, T.two_dir, T.two_dir + 0.7)
            gone = ramp(t, T.one_dir, T.one_dir + 0.8)
            for d, along in ((tg, True), (-tg, True), (nr, False), (-nr, False)):
                L = 0.62 * grow * (1.0 if along else 1 - gone)
                if L > 0.02:
                    col = C.tang if (along and gone > 0.5) else (C.wrong if (not along and gone > 0.3) else C.text)
                    v.arrow(p, p + np.array([d[0] * L, d[1] * L, 0]), col, width=5.0, tip=0.16, alpha=fa)
            bead(v, ell([W0])[0], r=0.07)
        return v.rgba()

    s.add(FramesLayer(frame, height=8.0, z=-5, during=[(T.cut_constraint, T.cut_ch2)]))
    m = s.manim(z=5, parallax=0.0)
    rp = [TRAIL_A * np.cos(-0.5), TRAIL_B * np.sin(-0.5)]
    pin(m, cam, lambda t: [rp[0], rp[1], cut_h(t)], tex("g", "(x,y)", "=", "c", size=56, colors={0: C.con, 3: C.con}), T.g_eq, T.on_path - 0.2, off=(2.5, 0.0))
    pin(m, cam, lambda t: [3.6, 3.6, cut_h(t)], tex("c", size=50, color=C.text), T.rule + 2.8, T.on_path - 0.2, off=(0.3, 0.1))
    pin(m, cam, [0, 0, 0], lab("the bowl  g(x, y)", 28, C.con), T.rule + 1.8, T.g_eq - 0.2, off=(0, -1.9))
    pin(m, cam, lambda t: [*ell([w_s(t)])[0], hill(*ell([w_s(t)])[0])], lab("on the path", 28, C.con), T.on_path, T.forbid, off=(0, -0.55))
    pin(m, cam, [4.3, -2.6, 0.0], lab("forbidden", 36, C.wrong), T.forbid + 0.2, T.look + 0.6, off=(0, 0))
    pin(m, cam, [-0.9, 2.4, hill(-0.9, 2.4)], lab("forbidden", 30, C.wrong), T.forbid + 0.5, T.look + 0.6, off=(0, 0))
    wpt = [*wp, float(hill(*wp))]
    pin(m, cam, wpt, lab("2 directions", 32, C.text), T.two_dir + 0.3, T.one_dir + 0.1, off=(-2.2, -0.1), fout=0.3)
    pin(m, cam, wpt, lab("1 direction:  forward or back", 32, C.tang), T.one_dir + 0.2, T.formula, off=(-3.0, -0.1))
    h = s.manim(z=20, parallax=0.0)
    sub = tex(r"f(a\cos s,\ b\sin s)", size=58, color=C.text)
    pin(m, cam, [0.0, GY, BEST_H], sub, T.formula + 2.8, T.tangled + 0.6, off=(0.0, 0.85))
    pin(m, cam, [GX1 + 0.5, GY, 0.0], tex("s", size=48, color=C.text), T.formula + 2.6, T.tangled + 0.6, off=(0.25, -0.3))
    one = lab("one variable", 30, C.you)
    pin(m, cam, [0.0, GY, BEST_H], one, T.formula + 3.4, T.tangled + 0.6, off=(0.0, 1.55))
    top_eq = tex(r"x(s),\ y(s)\ =\ \text{?}", size=56, color=C.text)
    headline(h, top_eq, T.tangled + 3.2, T.unroll - 0.3)
    cross = Line(top_eq.get_corner(DL) + [-0.15, -0.05, 0], top_eq.get_corner(UR) + [0.15, 0.05, 0], color=C.wrong, stroke_width=6)
    h.play(Create(cross), at=T.tangled + 4.6, dur=0.5, ease=E)
    h.play(FadeOut(cross), at=T.unroll - 0.3, dur=0.5, ease=E, lead=0)
    headline(h, sc("without unrolling the trail", 40, C.con), T.unroll + 0.2, T.cut_ch2 - 0.3)
    curtain(s, a=False, b=True)
