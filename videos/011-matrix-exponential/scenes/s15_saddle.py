"""s15 saddle (ch4): most matrices hide diagonal directions: their eigenvectors. The saddle [[1/2, 1], [1, 1/2]] grows
at rate 3/2 along (1, 1) and shrinks at rate 1/2 along (1, −1); every other point is a blend of the two, carried both
ways at once along curved paths. Find the eigenvectors and e^{tA} = P diag(e^{3t/2}, e^{−t/2}) P^{-1}."""
from aion import *

from beats import T
from shots import (BOX4, PC4, PX4, E, backdrop, backed, cycles, disc_points, field_arrows, finish, flow_layers, lab,
                   live, p3, poly, stage4, tex)
from verify import CAST

S = CAST["saddle"]
W_, P_ = np.linalg.eigh(S)                            # ascending: −1/2 along (1, −1), 3/2 along (1, 1)
assert np.allclose(W_, [-0.5, 1.5])
E_GROW = np.array([1.0, 1.0]) / np.sqrt(2)
E_SHRINK = np.array([1.0, -1.0]) / np.sqrt(2)
Q0 = np.array([1.3, -2.3])                            # the particle we decompose


def eigline(d):
    """The full eigenline through PC4 along d, clipped to the plane box."""
    L = 6.0
    return Line(p3(PC4 - L * d), p3(PC4 + L * d), color=C.eigen, stroke_width=C.stroke + 0.5)


@scene(T.cut_saddle, T.cut_spiral)
def s15_saddle(s):
    backdrop(s)
    mg = s.manim(z=0)
    mf = s.manim(z=1)
    m = s.manim(z=4)
    mp = s.manim(z=5)
    stage4(mg, mp)

    Sm = VGroup(tex("A", "=", size=44, colors={0: C.gen}),
                Mat([[r"\tfrac12", "1"], ["1", r"\tfrac12"]], colors=C.gen, size=40, h_buff=1.0, v_buff=0.8)).arrange(
        RIGHT, buff=0.2).move_to([PX4, 2.75, 0])
    mp.play(FadeIn(Sm, shift=0.1 * DOWN), at=T.saddle + 0.2, dur=0.6)
    field = field_arrows(S, center=PC4, box=BOX4, spacing=0.75)
    mf.play(FadeIn(field, lag_ratio=0.004), at=T.saddle + 0.4, dur=1.2)
    mf.play(FadeOut(field), at=T.cut_spiral - 0.4, dur=0.5)

    # ── the hidden diagonal directions ──
    lg, ls = eigline(E_GROW), eigline(E_SHRINK)
    lam_g = backed(tex(r"\lambda = \tfrac32", size=38, color=C.eigen), buff=0.05).move_to(p3(PC4 + 3.1 * E_GROW + [0.85, 0]))
    lam_s = backed(tex(r"\lambda = -\tfrac12", size=38, color=C.eigen), buff=0.05).move_to(
        p3(PC4 - 3.0 * E_SHRINK + [-0.2, 0.45]))
    ev_tag = lab("eigenvectors", 26, C.eigen).move_to([PX4, 1.45, 0])
    mp.play(FadeIn(ev_tag), at=T.eigvecs + 0.2, dur=0.5)
    m.play(Create(lg), at=T.grow32 - 0.8, dur=0.7, ease=E)
    m.play(FadeIn(lam_g), at=T.grow32 + 0.4, dur=0.5)
    m.play(Create(ls), at=T.shrink12 - 0.6, dur=0.7, ease=E)
    m.play(FadeIn(lam_s), at=T.shrink12 + 0.4, dur=0.5)

    # dots slide along each line: out along (1, 1), in along (1, −1)
    tg, ag = cycles(T.grow32 + 0.3, T.blend + 0.3, 2.7, 1.1)
    ts, as_ = cycles(T.shrink12 + 0.3, T.blend + 0.3, 2.4, 2.6)

    def slide(t):
        out = VGroup()
        a1, a2 = float(ag(t)), float(as_(t))
        for r in (-2.0, -1.0, 1.0, 2.0):
            if a1 > 0.01:
                out.add(Dot(p3(PC4 + 0.8 * r * np.exp(1.5 * float(tg(t))) * E_GROW), radius=0.1, color=C.vec)
                        .set_opacity(a1))
            if a2 > 0.01:
                out.add(Dot(p3(PC4 + 1.8 * r * np.exp(-0.5 * float(ts(t))) * E_SHRINK), radius=0.1, color=C.vec)
                        .set_opacity(a2))
        return out
    live(m, slide, (T.grow32 + 0.3, T.blend + 0.35))

    # ── every other point is a blend: particles, and one point split into its two components ──
    tau, al = cycles(T.blend + 0.2, T.cut_spiral - 0.3, 4.6, 1.3)
    flow_layers(s, disc_points(3000, 4.2, seed=11), S, tau, alpha=al * 0.6, trail=14, dt=0.03, size=2.1, z=2,
                center=PC4, start=T.blend, end=T.cut_spiral)
    c_g, c_s = float(Q0 @ E_GROW), float(Q0 @ E_SHRINK)
    d_op = keys((T.blend + 1.0, 0.0), (T.blend + 1.5, 1.0), (T.cut_spiral - 0.8, 1.0), (T.cut_spiral - 0.3, 0.0),
                lead=0)

    def blend(t):
        k = float(tau(t))
        op = float(d_op(t)) * min(1.0, 2 * float(al(t)))
        a = c_g * np.exp(1.5 * k) * E_GROW
        b = c_s * np.exp(-0.5 * k) * E_SHRINK
        q = PC4 + a + b
        return VGroup(DashedLine(p3(PC4), p3(PC4 + a), color=C.eigen, dash_length=0.1, stroke_width=C.stroke)
                      .set_stroke(opacity=op),
                      DashedLine(p3(PC4), p3(PC4 + b), color=C.eigen, dash_length=0.1, stroke_width=C.stroke)
                      .set_stroke(opacity=op),
                      poly([PC4 + a, q, PC4 + b], C.eigen, C.thin + 0.4, opacity=0.6 * op),
                      Dot(p3(q), radius=0.12, color=C.vec).set_opacity(op))
    live(m, blend, (T.blend + 1.0, T.cut_spiral - 0.25))
    m.play(FadeOut(VGroup(lg, ls, lam_g, lam_s)), at=T.cut_spiral - 0.4, dur=0.5)

    # ── e^{tA} = P diag(e^{3t/2}, e^{−t/2}) P^{-1} ──
    eS = VGroup(tex(r"e^{tA}", "=", "P", size=38, colors={0: C.flow, 2: C.eigen}),
                Mat([[r"e^{3t/2}", "0"], ["0", r"e^{-t/2}"]], colors=C.flow, size=34, h_buff=1.15, v_buff=0.72),
                tex(r"P^{-1}", size=38, color=C.eigen)).arrange(RIGHT, buff=0.14).move_to([PX4, -0.2, 0])
    pe = lab("P: the eigenvectors as columns", 22, C.eigen).next_to(eS, DOWN, buff=0.35)
    mp.play(FadeIn(eS, shift=0.1 * DOWN), at=T.find_eig + 0.6, dur=0.8)
    mp.play(FadeIn(pe), at=T.find_eig + 1.6, dur=0.5)
    mp.play(FadeOut(VGroup(Sm, ev_tag, eS, pe)), at=T.cut_spiral - 0.4, dur=0.5)
    finish(s)
