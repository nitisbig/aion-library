"""Ch4 · Neural networks: a layer is a matrix, a shift and a bend. Without bends the stack is one matrix and no straight
cut separates the spirals; with bends a 2-3-3-3-3-1 tanh net folds space, drawn exactly in 3D, until a plane splits them."""
from aion import *

from beats import T
from nets import accuracy, forward, line, net, spirals
from shots import Cam, Mat, backdrop, finish, fmt, tex

E = "smooth"
OD = np.array([1.7, -0.55])                            # where the data plane's origin sits on screen
U2, U3 = 2.3, 1.75                                     # screen units per data unit: flat view, 3D view
M_LIN = np.array([[1.1, 0.55], [-0.35, 0.8]])          # "one straight move" (stands in for W10 ... W1)

X, Y = spirals()
WS, BS = net()
HS = forward(WS, BS, X)                                # [X, h1, h2, h3, h4, logits]
NL = len(WS) - 1                                       # four bends


def lift(H):
    """2D inputs as 3D points on the floor (z = 0); 3D states unchanged."""
    H = np.asarray(H, float)
    return np.c_[H, np.zeros(len(H))] if H.shape[1] == 2 else H


# the coarse grid that rides along: input lines x = k and y = k, sampled densely
GK = (-1.0, -0.5, 0.0, 0.5, 1.0)
_s = np.linspace(-1.15, 1.15, 48)
GRID_IN = [np.c_[np.full_like(_s, k), _s] for k in GK] + [np.c_[_s, np.full_like(_s, k)] for k in GK]
GRID_HS = [forward(WS, BS, g) for g in GRID_IN]


def state(hs, f, lin):
    """Points after `f` layers (fractional = part-way along the straight path), with the 2D straight move `lin`."""
    k = int(np.clip(np.floor(f), 0, NL - 1))
    a, b = lift(hs[k]), lift(hs[k + 1])
    P = a + (f - k) * (b - a)
    if lin > 0:
        P = P.copy()
        P[:, :2] = P[:, :2] @ (np.eye(2) + lin * (M_LIN - np.eye(2))).T
    return P


@scene(T.cut_layers, T.cut_ch5)
def s10_layers(s):
    backdrop(s)
    g = s.manim(z=1)                                   # riding grid, cut line, plane
    hud = s.manim(z=5, parallax=0.0)

    # ── one layer: multiply by a matrix, shift, bend ──
    i0 = 41
    x0 = X[i0]
    z1 = x0 @ WS[0] + BS[0]
    h1 = np.tanh(z1)
    Wd = Mat(np.round(WS[0].T, 1), size=40, h_buff=1.05, v_buff=0.62)
    xd = Mat([[fmt(round(v, 2))] for v in x0], colors=[C.vec], size=40, v_buff=0.62)
    plus = tex("+", size=44)
    bd = Mat([[fmt(round(v, 1))] for v in BS[0]], colors=[C.text], size=40, v_buff=0.62)
    to1 = Arrow(LEFT * 0.45, RIGHT * 0.45, buff=0, color=C.muted, stroke_width=3, tip_length=0.18)
    ax = VGroup(Line(LEFT * 0.75, RIGHT * 0.75, color=C.muted, stroke_width=1.5),
                Line(DOWN * 0.55, UP * 0.55, color=C.muted, stroke_width=1.5))
    curve = FunctionGraph(lambda u: 0.42 * np.tanh(2.2 * u), x_range=[-0.75, 0.75], color=C.text, stroke_width=3.5)
    bend = VGroup(ax, curve)
    to2 = to1.copy()
    hd = Mat([[fmt(round(v, 2))] for v in h1], colors=[C.text], size=40, v_buff=0.62)
    layer = VGroup(Wd, xd, plus, bd, to1, bend, to2, hd).arrange(RIGHT, buff=0.3).move_to([0, 0.4, 0])
    hud.play(FadeIn(xd, shift=0.15 * UP), at=T.layer + 0.3, dur=0.6)
    hud.play(FadeIn(Wd, shift=0.2 * RIGHT), at=T.layer + 2.0, dur=0.7)
    hud.play(FadeIn(VGroup(plus, bd), shift=0.15 * LEFT), at=T.layer + 3.6, dur=0.6)
    hud.play(GrowArrow(to1), Create(ax), at=T.bends - 0.1, dur=0.5)
    hud.play(Create(curve), at=T.bends + 0.25, dur=0.8)
    hud.play(GrowArrow(to2), FadeIn(hd, shift=0.15 * LEFT), at=T.bends + 0.9, dur=0.6)
    shift = curve.get_center() - FunctionGraph(lambda u: 0.42 * np.tanh(2.2 * u), x_range=[-0.75, 0.75]).get_center()
    tails = VGroup(*[FunctionGraph(lambda u: 0.42 * np.tanh(2.2 * u), x_range=r, color=C.vec, stroke_width=5)
                     .shift(shift) for r in ([-0.75, -0.4], [0.4, 0.75])])     # the squashed ends
    hud.play(FadeIn(tails), at=T.bends + 1.2, dur=0.4)
    hud.play(FadeOut(tails), at=T.bends + 2.4, dur=0.5)
    hud.play(Indicate(bend, color=C.text, scale_factor=1.2), at=T.bend_matters + 0.5, dur=0.9)
    hud.play(FadeOut(layer), at=T.bend_matters + 1.9, dur=0.6)

    # ── without bends: ten matrices multiply into one ──
    stack = tex("W_{10}", r"\cdots", "W_2", "W_1", size=52)
    stack.move_to([-4.3, 1.6, 0])
    one = tex("=", "W", size=52).next_to(stack, RIGHT, buff=0.2)
    hud.play(LaggedStart(*[FadeIn(p, shift=0.1 * LEFT) for p in reversed(stack)], lag_ratio=0.25), at=T.ten_layers,
             dur=1.4)
    hud.play(FadeIn(one), at=T.ten_layers + 3.0, dur=0.6)
    hud.play(Indicate(one[1], color=C.text, scale_factor=1.3), at=T.ten_layers + 3.6, dur=0.8)

    # ── the scores ──
    w_l, b_l, acc_l = line()
    acc_n = accuracy(WS, BS, X, Y)
    s_line = tex(f"{round(acc_l * 100)}\\%", size=56, color=C.muted).move_to([-4.3, -0.6, 0])
    s_net = tex(f"{round(acc_n * 100)}\\%", size=56, color=C.text).move_to([-4.3, -0.6, 0])

    # ── the score of motion ──
    t_dots = T.ten_layers + 4.3                        # spirals appear on "a single straight move"
    l0, l1 = T.spirals - 1.8, T.spirals - 0.4          # the straight move
    l2, l3 = T.with_bends, T.with_bends + 0.8          # ... undone
    k0, k1 = l3, l3 + 1.2                              # tip into 3D
    folds = [k1 + 0.05 + 1.2 * i for i in range(NL)]   # four folds, 1.0 s each
    r0, r1 = T.backwards - 0.3, T.backwards + 1.1      # played backwards
    lin = keys((l0, 0.0), (l1, 1.0, E), (l2, 1.0), (l3, 0.0, E), lead=0)
    kk = []
    for i, tf in enumerate(folds):
        kk += [(tf, float(i)), (tf + 1.0, float(i + 1), E)]
    fold = keys(*kk, (r0, float(NL)), (r1, 0.0, E), lead=0)
    tipk = keys((k0, 0.0), (k1, 1.0, "easy_ease"), (r0, 1.0), (r1, 0.0, "easy_ease"), lead=0)

    def cam(t):
        k = tipk(t)
        az3 = -35.0 + 3.5 * max(0.0, t - k1)
        return Cam(k * az3, 90 + (24 - 90) * k, origin=OD, unit=U2 + (U3 - U2) * k)

    def project(c, P):
        return np.array([c.scr(p)[:2] for p in P])

    def pos(t, cls):
        P = state(HS, fold(t), lin(t))
        return project(cam(t), P[Y == cls])
    pts_op = fade(t_dots, dur=0.8, out=T.cut_ch5 - 0.05, out_dur=0.6)
    for cls, col in ((0, C.cls_a), (1, C.cls_b)):
        s.add(PointsLayer(lambda t, cls=cls: pos(t, cls), color=col, size=5.0, glow=0.0, additive=False, z=2,
                          opacity=pts_op))

    def riding(t):
        c = cam(t)
        f, ln = fold(t), lin(t)
        out = VGroup()
        for hs, gk in zip(GRID_HS, GK + GK):
            P = state(hs, f, ln)
            op = 0.55 if gk == 0 else 0.35
            out.add(VMobject(stroke_color=C.grid, stroke_width=1.6, stroke_opacity=op)
                    .set_points_smoothly([c.scr(p) for p in P]))
        k = tipk(t)
        if k > 0.01:                                   # the cube the bends squash everything into
            for a in (-1, 1):
                for b in (-1, 1):
                    for ax in range(3):
                        p, q = np.zeros(3), np.zeros(3)
                        o1, o2 = [i for i in range(3) if i != ax]
                        p[o1] = q[o1] = a
                        p[o2] = q[o2] = b
                        p[ax], q[ax] = -1, 1
                        out.add(Line(c.scr(p), c.scr(q), color=C.frame, stroke_width=1.2, stroke_opacity=0.3 * k))
        return out
    still = riding(t_dots)
    g.play(FadeIn(still), at=t_dots, dur=0.8)
    g.remove(still, at=l0)
    hold = g.redraw(riding, during=(l0, l1))
    g.remove(hold, at=l2)
    g.redraw(riding, during=(l2, r1))

    # the best straight cut, drawn in the moved plane: still cuts both colours
    Mi = np.linalg.inv(M_LIN)
    wn = Mi.T @ w_l                                    # the cut's normal after the straight move
    p0 = -b_l * wn / (wn @ wn)
    d = np.array([-wn[1], wn[0]]) / np.linalg.norm(wn)
    c_flat = Cam(0, 90, origin=OD, unit=U2)
    cut = DashedLine(c_flat.scr([*(p0 - 1.5 * d), 0]), c_flat.scr([*(p0 + 1.5 * d), 0]), dash_length=0.14,
                     color=C.text, stroke_width=3)
    g.play(Create(cut), at=T.spirals + 0.1, dur=0.8)
    hud.play(FadeIn(s_line, scale=1.2), at=T.spirals + 0.9, dur=0.6)
    g.play(FadeOut(cut), at=T.with_bends - 0.1, dur=0.5)
    hud.play(FadeOut(VGroup(s_line, stack, one)), at=T.with_bends - 0.1, dur=0.5)

    # ── with bends: after the last fold, one flat plane splits the colours ──
    w5, b5 = WS[-1][:, 0], BS[-1][0]
    n5 = w5 / np.linalg.norm(w5)
    q0 = -b5 * n5 / np.linalg.norm(w5)
    e1 = np.cross(n5, [0, 0, 1.0]) if abs(n5[2]) < 0.9 else np.cross(n5, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n5, e1)
    plane_op = keys((T.told_apart - 0.4, 0.0), (T.told_apart + 0.3, 1.0), (r0 - 0.3, 1.0), (r0 + 0.2, 0.0), lead=0)

    def plane(t):
        c = cam(t)
        o = plane_op(t)
        sq = [q0 + 1.25 * (a * e1 + b * e2) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        return Polygon(*[c.scr(p) for p in sq], stroke_color=C.text, stroke_width=2, stroke_opacity=0.7 * o,
                       fill_color=C.text, fill_opacity=0.015 * o)
    pl = s.manim(z=1.5)
    pl.redraw(plane, during=(T.told_apart - 0.45, r0 + 0.25))
    hud.play(FadeIn(s_net, scale=1.2), at=T.told_apart + 0.3, dur=0.6)

    # ── played backwards: the folds unwind, and the cut they made curls around the spirals ──
    n = 160
    gx = np.linspace(-1.25, 1.25, n)
    GX, GY = np.meshgrid(gx, gx)
    logit = forward(WS, BS, np.c_[GX.ravel(), GY.ravel()])[-1][:, 0].reshape(n, n)
    field = np.tanh(0.6 * logit)
    s.add(FieldLayer(lambda t: field, cmap="diverging", vmin=-1, vmax=1, colors=(C.cls_a, C.bg, C.cls_b),
                     extent=(2.5 * U2, 2.5 * U2), center=tuple(OD), animated=False, z=0.5,
                     opacity=fade(r1 + 0.3, to=0.1, dur=1.0, out=T.cut_ch5 - 0.05, out_dur=0.6)))
    hud.play(FadeOut(s_net), at=T.cut_ch5 - 0.05, dur=0.6)
    finish(s)
