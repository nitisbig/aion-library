"""s00 prologue: how fast something changes depends on how much of it there is.

Opening (0–17 s): a cup of coffee at 90 °C on a 20 °C desk, following Newton's law of cooling
dT/dt = −k (T − T_room) with k = 0.1 per minute, over 40 minutes. Everything on screen is that one law: the liquid's
colour and the thermometer are T, the curve is T(t) = T_room + 70 e^{−kt}, the orange tangent is dT/dt, the bracket is
the gap T − T_room, and the live numbers under the equation show the rate is always −0.1 × the gap.
Then four worlds (cooling, interest, growth, decay), each with its own law and colour, fan into x' = kx → e^{kt} x0.
"""
from aion import *

from beats import T
from shots import (E, backdrop, coin_stack, cup, cup_liquid, dim, finish, heat_color, inside_poly, lab, live,
                   mini_axes, p3, panel, petri, plot, rock, ROCK, steam, tex, thermometer)

# ── Newton's law of cooling (the opening's numbers) ──
T0, TR, KC, MIN = 90.0, 20.0, 0.1, 40.0               # °C, °C, per minute, minutes shown


def temp(m):
    return TR + (T0 - TR) * np.exp(-KC * np.asarray(m, float))


def rate(m):
    return -KC * (temp(m) - TR)


assert abs(rate(0) + 7.0) < 1e-9 and abs(temp(40) - 21.28) < 0.01

# ── opening layout (full frame); it later shrinks into panel 1 ──
CUP, CW, CH = np.array([-5.15, -1.75]), 1.9, 1.7
TH_B, TH_H = np.array([-3.0, -2.75]), 3.7             # thermometer bulb and tube height
PO, PW, PH = np.array([-1.15, -2.9]), 7.0, 4.0        # plot origin, width (40 min), height (100 °C)
XS, YS = PW / MIN, PH / 100.0
OPEN_C = np.array([-0.1, -0.55])                      # centre of the opening composition


def plot_pt(m, T_):
    return PO + [XS * m, YS * T_]


# ── four panels (2 x 2) ──
PANELS = [(-6.8, 0.15, -0.15, 3.7), (0.15, 0.15, 6.8, 3.7), (-6.8, -3.7, -0.15, -0.15), (0.15, -3.7, 6.8, -0.15)]
WORLD = ["heat", "money", "life", "decay"]
WORDS = ["cooling", "interest", "growth", "decay"]
LAWS = [r"\dot T = -k\,(T - T_r)", r"\dot M = r\,M", r"\dot N = k\,N", r"\dot N = -\lambda\,N"]


def pcenter(i):
    x0, y0, x1, y1 = PANELS[i]
    return np.array([(x0 + x1) / 2, (y0 + y1) / 2])


S1 = 0.47
OFF1 = pcenter(0) - S1 * OPEN_C + [0, -0.12]


def icon_at(i):
    x0, y0, x1, y1 = PANELS[i]
    return np.array([x0 + 1.55, (y0 + y1) / 2 - 0.25])


def plot_at(i):
    x0, y0, _, _ = PANELS[i]
    return np.array([x0 + 3.25, y0 + 0.4]), 3.0, 2.3


K = [-1.0, 0.55, 0.95, -0.6]
U_P = 2.6


def mini_curve(i, frac, opacity=1.0):
    o, w, h = plot_at(i)
    k = K[i]
    top = max(1.0, np.exp(k * U_P))
    u1 = max(frac, 1e-3) * U_P
    return plot(lambda u: np.exp(k * u) / top, 0, u1, o, w / U_P, h * 0.92, getattr(C, WORLD[i]), width=C.stroke - 0.6,
                opacity=opacity)


def cells(seed=5, n_max=40):
    g = rng(seed)
    out = [[0.0, np.inf, np.zeros(2)]]
    i = 0
    while i < len(out) and len(out) < n_max:
        b, _, p = out[i]
        life = 0.5 + 0.3 * g.random()
        out[i][1] = b + life
        for _ in range(2):
            d = g.normal(size=2)
            q = p + 0.2 * d / (np.linalg.norm(d) + 1e-9)
            if np.linalg.norm(q) > 0.75:
                q *= 0.75 / np.linalg.norm(q)
            out.append([b + life, np.inf, q])
        i += 1
    return out


CELLS = cells()


def rock_atoms(seed=8, n=46, half=1.8):
    g = rng(seed)
    cand = (g.random((6 * n, 2)) - 0.5) * [2.0, 1.25]
    pts = cand[inside_poly(ROCK * 0.82, cand)][:n]
    return pts, g.exponential(half / np.log(2), len(pts))


ATOMS, DECAY = rock_atoms()


@scene(T.start, T.cut_bernoulli)
def s00_prologue(s):
    backdrop(s)
    m0 = s.manim(z=0)                                  # everything that moves (rebuilt in windows)
    m = s.manim(z=1)                                   # the equation, numbers, headers

    t_c0, t_c1 = T.coffee + 0.6, T.rule + 1.6
    minutes = ramp(t_c0, t_c1, 0.0, MIN, ease="linear")
    shrink = keys((T.everywhere - 0.1, 0.0), (T.everywhere + 1.1, 1.0, E), lead=0)
    op_open = keys((T.coffee - 0.6, 0.0), (T.coffee + 0.2, 1.0), lead=0)
    op_plot = keys((T.coffee + 0.1, 0.0), (T.coffee + 0.9, 1.0), lead=0)
    op_rate = keys((T.hotter - 0.1, 0.0), (T.hotter + 0.4, 1.0), lead=0)
    op_p = [keys((b - 0.15, 0.0), (b + 0.45, 1.0), lead=0) for b in (T.everywhere + 0.3, T.money, T.bacteria, T.rock)]
    draw = [ramp(b + 0.2, b + 4.2, 0.0, 1.0, ease="linear") for b in (T.everywhere, T.money, T.bacteria, T.rock)]

    def opening(t):
        """(the drawing, fine labels that fade as it shrinks, the curve) at time t, in opening coordinates."""
        mi = float(minutes(t))
        Tc = float(temp(mi))
        f = (Tc - TR) / (T0 - TR)
        col = heat_color(f)
        po = float(op_plot(t))
        g = VGroup()
        g.add(cup_liquid(CUP, w=CW, h=CH, color=col, opacity=0.9), cup(CUP, w=CW, h=CH))
        if f > 0.06:
            g.add(steam(CUP, t, heat=float(np.clip(f * 1.2, 0, 1)), h=CH, w=CW, color=col))
        g.add(thermometer(TH_B, TH_H, Tc / 100.0, col))
        pl = VGroup(mini_axes(PO, PW + 0.15, PH * 0.98))
        for mm in (10, 20, 30, 40):
            x = plot_pt(mm, 0)
            pl.add(Line(p3(x), p3(x + [0, -0.08]), color=C.muted, stroke_width=C.thin))
        room = plot_pt(0, TR)
        pl.add(DashedLine(p3(room), p3(plot_pt(MIN, TR) + [0.15, 0]), color=C.cool, stroke_width=C.thin + 0.6,
                          dash_length=0.12))
        tip = plot_pt(mi, Tc)
        a = float(op_rate(t))
        if a > 0.01 and mi > 0.2:
            if tip[1] - room[1] > 0.25:                # the gap T − T_room
                gx = tip[0] + 0.28
                pl.add(DoubleArrow(p3((gx, room[1])), p3((gx, tip[1])), buff=0, color=C.warm,
                                   stroke_width=C.stroke - 0.5, tip_length=0.14,
                                   max_tip_length_to_length_ratio=0.25).set_opacity(a))
            sl = float(rate(mi)) * YS / XS             # the rate dT/dt: the tangent at the tip
            d = np.array([1.0, sl]) / np.hypot(1.0, sl)
            pl.add(Line(p3(tip - 0.8 * d), p3(tip + 0.8 * d), color=C.gen, stroke_width=C.stroke + 0.5,
                        stroke_opacity=a))
        pl.add(Dot(p3(tip), radius=0.1, color=C.vec))
        dim(pl, po)
        g.add(pl)
        curve = plot(temp, 0, max(mi, 1e-3), PO, XS, YS, C.heat, width=C.stroke + 0.5)
        curve.set_stroke(color=[col, heat_color(0.5 + 0.5 * f), C.heat], opacity=po if mi > 0.05 else 0.0)
        fine = VGroup(lab(r"90\,$^\circ$C", 24).next_to(p3(plot_pt(0, T0)), LEFT, buff=0.12),
                      lab(r"20\,$^\circ$C", 24, C.cool).next_to(p3(room), LEFT, buff=0.12),
                      lab("minutes", 24).next_to(p3(plot_pt(MIN / 2, 0)), DOWN, buff=0.4),
                      *[lab(str(mm), 20).next_to(p3(plot_pt(mm, 0)), DOWN, buff=0.12) for mm in (10, 20, 30, 40)],
                      tex(r"T_{\text{room}}", size=30, color=C.cool).next_to(p3(plot_pt(MIN, TR)), UP, buff=0.12))
        dim(fine, po)
        reading = VGroup(DecimalNumber(Tc, num_decimal_places=1, font_size=34, color=col),
                         lab(r"$^\circ$C", 28, col)).arrange(RIGHT, buff=0.06)
        reading.next_to(p3(TH_B + [0, TH_H + 0.35]), UP, buff=0.1)
        fine.add(reading)
        return g, fine, curve

    def parts(t):
        """(everything else, the four worlds' curves) at time t."""
        out, curves = VGroup(), VGroup()
        sk = float(shrink(t))
        o = float(op_open(t))
        g, fine, c0 = opening(t)
        dim(fine, 1 - sk)
        g.add(fine)
        if sk > 0:
            sc = 1 + (S1 - 1) * sk
            for mob in (g, c0):
                mob.scale(sc, about_point=ORIGIN).shift(p3(OFF1 * sk))
        if o < 0.999:
            dim(g, o)
            dim(c0, o)
        curves.add(c0)
        for i in range(4):
            a = float(op_p[i](t))
            if a < 0.01:
                continue
            col = getattr(C, WORLD[i])
            out.add(dim(panel(*PANELS[i], fill=False).set_stroke(color=col), 0.55 * a))
            if i == 0:
                continue
            ic = icon_at(i)
            fr_ = float(draw[i](t))
            pl_o, pw, ph = plot_at(i)
            out.add(dim(mini_axes(pl_o, pw, ph), a))
            curves.add(mini_curve(i, fr_, a if fr_ > 0 else 0.0))
            el = t - (T.money, T.bacteria, T.rock)[i - 1] - 0.2
            if i == 1:                                # coins: the stack compounds
                n = int(np.clip(np.floor(np.exp(K[1] * U_P * np.clip(el / 4.0, 0, 1)) * 2.2), 1, 9))
                out.add(dim(coin_stack(ic + [0, -0.6], n, color=col), a))
            elif i == 2:                              # bacteria: every cell splits in two
                out.add(dim(petri(ic, r=0.95), a))
                for b, d, p in CELLS:
                    if b <= max(el, 0.0) < d:
                        out.add(Dot(p3(ic + p), radius=0.06, color=col).set_opacity(a))
            else:                                     # rock: atoms blink out at random
                out.add(dim(rock(ic, 1.0), a))
                for p, td in zip(ATOMS, DECAY):
                    if max(el, 0.0) < td:
                        out.add(Dot(p3(ic + p), radius=0.055, color=col).set_opacity(a))
                    elif el < td + 0.3:              # a brief white flash as it decays
                        out.add(Dot(p3(ic + p), radius=0.1, color=C.text).set_opacity(a * (1 - (el - td) / 0.3)))
        out.add(g)
        return out, curves

    t_end = T.one_eq - 0.05
    hs = live(m0, lambda t: VGroup(*parts(t)), (T.coffee - 0.6, t_end))

    # ── the law, with its live numbers ──
    EQ_C = np.array([2.35, 3.05])
    law = tex(r"\frac{dT}{dt}", "=", "-k", r"\,\big(", r"T - T_{\text{room}}", r"\big)", size=52,
              colors={0: C.gen, 4: C.warm})
    law.move_to(p3(EQ_C))
    m.play(Write(law), at=T.hotter + 0.2, dur=1.1)
    ROW = EQ_C[1] - 1.05

    def numbers(t):
        mi = float(minutes(t))
        r_ = DecimalNumber(float(rate(mi)), num_decimal_places=2, font_size=34, color=C.gen)
        g_ = DecimalNumber(float(temp(mi) - TR), num_decimal_places=1, font_size=34, color=C.warm)
        eq_ = tex("=", size=34, color=C.muted)
        k_ = tex(r"-0.1\,\times", size=34, color=C.muted)
        r_.move_to(p3((law[0].get_center()[0], ROW)))
        eq_.move_to(p3((law[1].get_center()[0], ROW)))
        k_.move_to(p3((law[2].get_center()[0] + 0.1, ROW)))
        g_.move_to(p3((law[4].get_center()[0], ROW)))
        return VGroup(r_, eq_, k_, g_)
    t_n = T.hotter + 1.2
    n_op = keys((t_n, 0.0), (t_n + 0.4, 1.0), (T.everywhere - 0.4, 1.0), (T.everywhere + 0.1, 0.0), lead=0)
    hn = m.redraw(lambda t: numbers(t).set_opacity(float(n_op(t))), during=(t_n, T.everywhere + 0.15))
    m.remove(hn, at=T.everywhere + 0.2)
    fast, much = lab("how fast", 26, C.gen), lab("how much", 26, C.warm)
    for w_, part in ((fast, law[0]), (much, law[4])):
        w_.move_to(p3((part.get_center()[0], ROW - 0.55)))
    m.play(FadeIn(fast, shift=0.1 * UP), at=T.rule + 0.3, dur=0.5)
    m.play(FadeIn(much, shift=0.1 * UP), at=T.rule + 1.6, dur=0.5)
    m.play(FadeOut(VGroup(law, fast, much)), at=T.everywhere - 0.2, dur=0.5)

    # ── four worlds: each panel's key word and law, in its colour ──
    heads = []
    for i, at in enumerate((T.everywhere + 0.6, T.money, T.bacteria, T.rock)):
        x0, y0, x1, y1 = PANELS[i]
        col = getattr(C, WORLD[i])
        w_ = lab(WORDS[i], 28, col)
        w_.move_to(p3((x0 + 0.3 + w_.width / 2, y1 - 0.38)))
        lw = tex(LAWS[i], size=34, color=col)
        lw.move_to(p3((x1 - 0.3 - lw.width / 2, y1 - 0.4)))
        heads.append((w_, lw))
        m.play(FadeIn(w_, shift=0.08 * RIGHT), FadeIn(lw, shift=0.08 * LEFT), at=at + 0.2, dur=0.6)

    # ── one equation: four laws become one, four curves fan into one family ──
    rest, curves = parts(t_end)
    m0.remove(hs[-1], at=T.one_eq)
    m.add(rest, curves, at=T.one_eq)
    FO, FW, FH = np.array([-2.7, -3.35]), 5.4, 0.95
    family = VGroup()
    for k in K:
        u1 = 3.0 if k < 0 else min(3.0, np.log(3.0) / k)
        family.add(plot(lambda u, k=k: np.exp(k * u), 0, u1, FO, FW / 3.0, FH, C.flow, width=C.stroke))
    fax = mini_axes(FO, FW, 3.0)
    eq = tex(r"\dot x", r"=", r"k", r"\,x", size=84, colors={2: C.gen}).move_to([0, 2.55, 0])
    copies = [eq.copy() for _ in range(4)]
    m.play(FadeOut(rest), FadeOut(VGroup(*[w_ for w_, _ in heads])), at=T.one_eq, dur=0.6)
    m.play(*[ReplacementTransform(lw, c) for (_, lw), c in zip(heads, copies)], at=T.one_eq + 0.2, dur=1.2, ease=E)
    m.play(FadeIn(fax), *[ReplacementTransform(a, b) for a, b in zip(curves, family)], at=T.one_eq + 0.4, dur=1.4,
           ease=E)
    m.remove(rest, *copies[1:], at=T.one_eq + 1.7)

    sol = tex(r"x(t)", r"=", r"e^{kt}", r"\,x_0", size=68, colors={2: C.flow}).move_to([0, 1.1, 0])
    sol[2][1].set_color(C.gen)
    m.play(FadeIn(sol, shift=0.15 * UP), at=T.ekt, dur=0.7)

    m.play(FadeOut(VGroup(copies[0], sol, fax, family)), at=T.cut_bernoulli - 0.4, dur=0.5)
    finish(s)
