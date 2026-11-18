"""Ch5: the eigenvectors of the derivative. A matrix's revealing directions are the ones it only stretches. Ask D:
sin turns into cos (no), x^2 loses a power (no), e^x comes back as itself (yes); e^{2x} comes back doubled, e^{-x}
flipped. Every e^{λx} is an eigenvector with eigenvalue λ, which is why y' = ky (growth, decay) is always answered by
one family, C e^{kx}."""
from aion import *

from beats import T
from shots import chapter_header, arrow, backdrop, finish, grid_lines, live, plot, pt, tex

E = "easy_ease"
A = np.array([[2.0, 1.0], [1.0, 2.0]])                   # the callback matrix: eigenvectors (1, 1) x3, (1, -1) x1
AO, AU = (0.0, -0.3), 0.9
ABOX = (-6.9, -3.7, 6.9, 2.4)
w, V = np.linalg.eigh(A)
assert np.allclose(sorted(w), [1, 3])

PX = [-4.6, 0.0, 4.6]                                    # the three candidate panels
PY = -0.4
PUX, PUY = 0.62, 0.42


def panel_axes(x0):
    o = (x0, PY)
    return VGroup(Line(pt(o, 1, (-1.9, 0)), pt(o, 1, (1.9, 0)), color=C.axis, stroke_width=C.thin),
                  Line(pt(o, 1, (0, -1.5)), pt(o, 1, (0, 1.9)), color=C.axis, stroke_width=C.thin))


def curve(f, x0, color, a=-3.0, b=3.0, dashed=False, ylim=(-3.5, 4.5)):
    c = plot(f, a, b, (x0, PY), PUX, PUY, color, ylim=ylim, width=C.stroke + (0 if dashed else 0.5))
    return DashedVMobject(c, num_dashes=40) if dashed else c


def rider(t, x0, f, df, xa, xb, ts, op, col=None, period=7.0):
    """A dot riding y = f(x) on panel x0 with its tangent (slope df), easing back and forth between xa and xb."""
    u = 0.5 - 0.5 * np.cos(2 * np.pi * max(t - ts, 0.0) / period)
    x = xa + (xb - xa) * u
    p = pt((x0, PY), 1, (PUX * x, PUY * f(x)))
    d = np.array([PUX, PUY * df(x), 0.0])
    d = 0.6 * d / np.linalg.norm(d)
    return VGroup(Line(p - d, p + d, color=C.dfn, stroke_width=C.stroke, stroke_opacity=op),
                  Dot(p, radius=0.075, color=col or C.text).set_opacity(op))


@scene(T.cut_ch5, T.cut_ode)
def s10_eigen(s):
    backdrop(s)
    m0 = s.manim(z=0)
    m = s.manim(z=1)
    chapter_header(m, 5, T.cut_ch5)                     # chapter badge row + title (fills the cut)
    t0 = T.cut_ch5

    # ── the revealing question: which directions only stretch? ──
    ta, tb = T.leave_alone - 0.2, T.leave_alone + 1.8
    mv = keys((ta, 0.0), (tb, 1.0, E), lead=0)
    op = keys((T.revealing - 0.4, 0.0), (T.revealing + 0.4, 1.0), (T.ask_d - 0.5, 1.0), (T.ask_d + 0.1, 0.0), lead=0)
    z = pt(AO, 1.0, (0, 0))

    def stage(t):
        u = float(mv(t))
        M = (1 - u) * np.eye(2) + u * A
        o = float(op(t))
        out = VGroup(grid_lines(M, AO, AU, ABOX, n=10, opacity=0.6 * o))
        for v in (np.array([1.0, 1.0]), np.array([1.0, -1.0])):          # the lines that don't turn
            out.add(Line(pt(AO, AU, -3.2 * v), pt(AO, AU, 3.2 * v), color=C.eigen, stroke_width=C.thin * 2,
                         stroke_opacity=0.7 * o))
            out.add(arrow(z, pt(AO, AU, M @ v), C.eigen, width=C.stroke + 1.5, opacity=o))
        out.add(arrow(z, pt(AO, AU, M @ [1.0, 0.0]), C.muted, width=C.stroke, opacity=o))   # a vector that turns
        return out
    live(m0, stage, (T.revealing - 0.4, T.revealing + 0.4), (ta, tb), (T.ask_d - 0.5, T.ask_d + 0.1))

    # ── ask the derivative: D f = λ f ? ──
    q = tex(r"D", r"f", r"=", r"\lambda", r"f", r"\;?", size=60, colors={0: C.op, 1: C.fn, 3: C.eigen, 4: C.fn})
    q.move_to([0, 2.9, 0])
    m.play(FadeIn(q, shift=0.1 * DOWN), at=T.ask_d + 0.4, dur=0.7)
    # while you predict: one faint curve drifts through candidate shapes
    ga, gb = T.which_fn + 1.0, T.not_sine - 0.9
    gop_ = keys((ga, 0.0), (ga + 0.8, 1.0), (gb - 0.6, 1.0), (gb, 0.0), lead=0)
    shapes = [lambda x: 1.5 * np.sin(x), lambda x: x ** 2 / 2 - 1.0, lambda x: np.exp(x) / 4]

    def drift(t):
        u = ((t - ga) / 3.2) % 3.0
        i, f = int(u), u - int(u)
        w = f * f * (3 - 2 * f)
        fn = lambda x: (1 - w) * shapes[i](x) + w * shapes[(i + 1) % 3](x)      # noqa: E731
        o = float(gop_(t))
        return VGroup(panel_axes(0.0).set_opacity(0.5 * o), curve(fn, 0.0, C.fn).set_stroke(opacity=0.45 * o))
    m.redraw(drift, during=(ga, gb))

    # ── candidates: f (solid) and D f (dashed) on the same axes ──
    cands = [
        (r"\sin x", np.sin, np.cos, T.not_sine),
        (r"x^2", lambda x: x ** 2 / 2, lambda x: x, T.not_x2),           # drawn at half height: x^2/2 and its slope x
        (r"e^x", lambda x: np.exp(x) / 4, lambda x: np.exp(x) / 4, T.answer_ex),
    ]
    panels = []
    frames = VGroup(*[Rectangle(width=4.2, height=4.5, stroke_color=C.frame, stroke_width=C.thin).move_to(
        [PX[k], PY - 0.2, 0]) for k in range(3)])               # thin framed panels (the reference look)
    for k, (lab, f, df, tk) in enumerate(cands):
        m.play(FadeIn(frames[k]), at=tk - 0.45, dur=0.5)
        ax = panel_axes(PX[k])
        cf = curve(f, PX[k], C.fn)
        cd = curve(df, PX[k], C.dfn, dashed=True)
        nm = tex(lab, size=44, color=C.fn).move_to([PX[k], PY - 2.05, 0])
        m.play(FadeIn(ax), Create(cf), FadeIn(nm), at=tk - 0.3, dur=0.7)
        m.play(Create(cd), at=tk + 0.5, dur=0.8)
        panels.append(VGroup(ax, cf, cd, nm))
    xs = [tex(r"\times", size=60, color=C.b2).move_to([PX[k] + 1.3, PY + 1.6, 0]) for k in range(2)]
    m.play(FadeIn(xs[0], scale=0.6), at=T.not_sine + 1.4, dur=0.4)
    m.play(FadeIn(xs[1], scale=0.6), at=T.not_x2 + 1.3, dur=0.4)
    ok = tex(r"\checkmark", size=60, color=C.eigen).move_to([PX[2] + 1.3, PY + 1.6, 0])
    m.play(FadeIn(ok, scale=0.6), Indicate(panels[2][2], color=C.eigen, scale_factor=1.03), at=T.itself + 0.2,
           dur=0.6)
    e1 = tex(r"D", r"e^x", r"=", r"e^x", size=44, colors={0: C.op, 1: C.fn, 3: C.dfn}).next_to(panels[2][3], RIGHT,
                                                                                           buff=0.0)
    e1.move_to([PX[2], PY - 2.05, 0])
    m.play(ReplacementTransform(panels[2][3], e1), at=T.itself + 0.6, dur=0.6)

    # ── e^{2x} comes back doubled, e^{−x} flipped ──
    td, tf = T.doubled, T.flipped_x
    p2 = [VGroup(curve(lambda x: np.exp(2 * x) / 8, PX[0], C.fn, b=1.5),
                 curve(lambda x: 2 * np.exp(2 * x) / 8, PX[0], C.dfn, b=1.5, dashed=True),
                 tex(r"D", r"e^{2x}", r"=", r"2", r"e^{2x}", size=44,
                     colors={0: C.op, 1: C.fn, 3: C.eigen, 4: C.dfn}).move_to([PX[0], PY - 2.05, 0])),
          VGroup(curve(lambda x: np.exp(-x) / 4, PX[1], C.fn, a=-1.5),
                 curve(lambda x: -np.exp(-x) / 4, PX[1], C.dfn, a=-1.5, dashed=True),
                 tex(r"D", r"e^{-x}", r"=", r"-1", r"\,e^{-x}", size=44,
                     colors={0: C.op, 1: C.fn, 3: C.eigen, 4: C.dfn}).move_to([PX[1], PY - 2.05, 0]))]
    m.play(FadeOut(VGroup(*panels[0][1:], xs[0])), at=td - 0.9, dur=0.4)
    m.play(Create(p2[0][0]), FadeIn(p2[0][2]), at=td - 0.5, dur=0.6)
    m.play(Create(p2[0][1]), at=td + 0.3, dur=0.7)
    m.play(FadeOut(VGroup(*panels[1][1:], xs[1])), at=tf - 0.9, dur=0.4)
    m.play(Create(p2[1][0]), FadeIn(p2[1][2]), at=tf - 0.5, dur=0.6)
    m.play(Create(p2[1][1]), at=tf + 0.3, dur=0.7)

    # riders: a dot and its tangent glide along each exponential; the slope is λ times the height
    rop = keys((T.itself + 1.2, 0.0), (T.itself + 1.8, 1.0), (T.everywhere - 0.3, 1.0), (T.everywhere + 0.2, 0.0),
               lead=0)
    rider_specs = [(PX[2], lambda x: np.exp(x) / 4, lambda x: np.exp(x) / 4, -2.5, 1.5, T.itself + 1.2),
                   (PX[0], lambda x: np.exp(2 * x) / 8, lambda x: 2 * np.exp(2 * x) / 8, -2.5, 1.1, T.doubled + 1.2),
                   (PX[1], lambda x: np.exp(-x) / 4, lambda x: -np.exp(-x) / 4, -1.5, 2.5, T.flipped_x + 1.2)]
    for x0, f, df, xa, xb, ts in rider_specs:
        m.redraw(lambda t, x0=x0, f=f, df=df, xa=xa, xb=xb, ts=ts: rider(t, x0, f, df, xa, xb, ts,
                                                                         float(rop(t)) * min(1.0, (t - ts) / 0.5)),
                 during=(ts, T.everywhere + 0.2))

    # ── every e^{λx}: an eigenvector, eigenvalue λ ──
    gen = tex(r"D", r"\,e^{\lambda x}", r"=", r"\lambda", r"\,e^{\lambda x}", size=60,
              colors={0: C.op, 1: C.eigen, 3: C.eigen, 4: C.eigen}).move_to([0, 2.9, 0])
    m.play(ReplacementTransform(q, gen), at=T.lambda_x + 0.3, dur=0.9)

    # ── why e is everywhere: y' = k y ──
    te = T.everywhere
    m.play(FadeOut(VGroup(*[p[0] for p in panels], panels[2][1], panels[2][2], ok, e1, *p2)), at=te - 0.3, dur=0.6)
    ks = [0.5, 0.25, -0.7]
    small = VGroup()
    for k, kk in enumerate(ks):
        ax = panel_axes(PX[k])
        cv = curve(lambda x, kk=kk: 0.8 * np.exp(kk * x), PX[k], C.eigen, a=-3.0 if kk > 0 else -1.9, b=3.0)
        lab = tex(r"k", r"=", f"{kk:g}", size=40, colors={0: C.eigen}).move_to([PX[k], PY - 2.05, 0])
        small.add(VGroup(ax, cv, lab))
    m.play(LaggedStart(*[AnimationGroup(FadeIn(g[0]), Create(g[1]), FadeIn(g[2])) for g in small], lag_ratio=0.3),
           at=T.proportional, dur=2.0)
    kop = keys((T.proportional + 2.2, 0.0), (T.proportional + 2.8, 1.0), (T.cut_ode - 0.7, 1.0), (T.cut_ode - 0.1, 0.0),
               lead=0)
    for k, kk in enumerate(ks):
        m.redraw(lambda t, k=k, kk=kk: rider(t, PX[k], lambda x: 0.8 * np.exp(kk * x), lambda x: 0.8 * kk * np.exp(kk * x),
                                             -2.5 if kk > 0 else -1.5, 2.5, T.proportional + 2.2 + 0.4 * k,
                                             float(kop(t)), col=C.eigen),
                 during=(T.proportional + 2.2, T.cut_ode - 0.1))
    yk = tex(r"y'", r"=", r"k", r"\,y", size=56, colors={2: C.eigen}).move_to([0, 2.9, 0])
    m.play(FadeOut(gen, shift=0.3 * UP), FadeIn(yk, shift=0.3 * UP), at=T.proportional + 0.8, dur=0.7)

    # ── only one family answers ──
    ans = tex(r"y", r"=", r"C", r"\,e^{kx}", size=56, colors={2: C.null, 3: C.eigen}).next_to(yk, DOWN, buff=0.3)
    m.play(FadeIn(ans, shift=0.1 * DOWN), Indicate(VGroup(*[g[1] for g in small]), color=C.eigen, scale_factor=1.03),
           at=T.one_family + 0.2, dur=0.8)
    m.play(FadeOut(VGroup(yk, ans, small, frames)), at=T.cut_ode - 0.7, dur=0.6)
    finish(s)
