"""s06 pnt (P13-P15): order at large scale. The staircase pi(x) zooms out from 100 to a million and looks smooth.
Gauss (1792, aged 15): a number near x is prime with chance about 1/ln x; the share of primes in blocks of 50,000
against 1/ln x (about 1 in 14 near a million). Adding up the chances gives li(x), within 0.2% of pi(10^6) = 78,498.
Hadamard and de la Vallee Poussin (1896): pi(x)/li(x) -> 1, using zeta and the fact that zeta(1 + it) != 0 (planted
for s16). Then the plot widens and zooms into 100,000-102,000: the staircase never matches li; the gap, in red, is
RH's question. Every number is computed here (zmath.primes_upto, zmath.li)."""
from functools import lru_cache

from aion import *

from beats import T
from media_assets import portrait_card
from look import EASE, caps, carded, lab, live, pin, seen, tex
from zmath import li, primes_upto

PX0, PY0, PY1 = -5.5, -3.0, 2.0              # the main plot's box (left, bottom, top) ...
PX1A, PX1B = -0.7, 6.2                       # ... and its right edge before / after the final zoom
RX0, RX1 = 0.9, 6.3                          # the right panel
DY0, DY1, DMAX = -3.0, 1.0, 0.12             # the density panel: bottom, top, and the value at its top
QY0, QY1, QLO, QHI = -3.0, 0.4, 0.6, 1.05    # the ratio panel: bottom, top, value range
BLOCK = 50_000                               # one density bar
ZX0, ZX1 = 100_000.0, 102_000.0              # the final zoom window


@lru_cache(maxsize=1)
def primes():
    return primes_upto(1_100_000).astype(float)


def pi_of(x):
    return np.searchsorted(primes(), np.asarray(x, float), side="right").astype(float)


def nice(lo, hi, n=4):
    """Round tick values inside [lo, hi], about n of them."""
    raw = (hi - lo) / n
    mag = 10 ** np.floor(np.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    return list(np.arange(np.ceil(lo / step) * step, hi + 1e-9, step))


def fmt(v):
    return "{:,}".format(int(round(v))).replace(",", "{,}")


@lru_cache(maxsize=None)
def _num(s):
    return tex(s, size=22, color=C.muted)


def num(v):
    return _num(fmt(v)).copy()


def zoom_y():
    return (min(pi_of(ZX0), li(ZX0)) - 25.0, max(pi_of(ZX1), li(ZX1)) + 25.0)


@scene(T.cut_pnt, T.cut_series)
def s06_pnt(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_series - 0.5, T.cut_series - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)       # the main plot
    rp = s.manim(z=3, parallax=0.0, opacity=fade)      # the right panel
    h = s.manim(z=6, parallax=0.0, opacity=fade)       # formulas, names, tags

    # ── the view: zoom out (x up to 100 -> 10^6, in log space); later widen and zoom in on 100,000-102,000 ──
    out = (T.g_long - L, T.g_long - L + 4.0)
    inn = (T.g_still - L, T.g_still - L + 1.5)
    u1 = keys((out[0], 0.0), (out[1], 1.0, EASE), lead=0)
    u2 = keys((inn[0], 0.0), (inn[1], 1.0, EASE), lead=0)
    zy0, zy1 = zoom_y()

    def window(t):
        x1 = 100.0 * 10 ** (4 * float(u1(t)))
        W = (0.0, x1, 0.0, 1.08 * float(pi_of(x1)))
        b = float(u2(t))
        if b <= 0:
            return W
        res = []
        for (p0, p1), (q0, q1) in (((W[0], W[1]), (ZX0, ZX1)), ((W[2], W[3]), (zy0, zy1))):
            w0, wt = p1 - p0, q1 - q0
            ww = np.exp(np.log(w0) + b * (np.log(wt) - np.log(w0)))     # zoom evenly in log scale
            c0, ct = (p0 + p1) / 2, (q0 + q1) / 2
            c = ct + (c0 - ct) * (ww - wt) / (w0 - wt)                  # the centre arrives with the width
            res += [c - ww / 2, c + ww / 2]
        return tuple(res)

    li_on = keys((T.g_adding - L, 0.0), (T.g_adding + 2.0, 1.0, "in_out_sine"), lead=0)
    gap_on = keys((T.g_never + 0.1, 0.0), (T.g_never + 1.0, 1.0, EASE), lead=0)

    def geom(t):
        x0, x1, y0, y1 = window(t)
        px1 = PX1A + (PX1B - PX1A) * float(u2(t))
        sx = lambda x: PX0 + (px1 - PX0) * (np.asarray(x, float) - x0) / (x1 - x0)     # noqa: E731
        sy = lambda y: PY0 + (PY1 - PY0) * (np.asarray(y, float) - y0) / (y1 - y0)     # noqa: E731
        return (x0, x1, y0, y1), px1, sx, sy

    def plot(t):
        (x0, x1, y0, y1), px1, sx, sy = geom(t)
        g = VGroup(Line([PX0, PY0, 0], [px1 + 0.1, PY0, 0], color=C.axis, stroke_width=2.0),
                   Line([PX0, PY0, 0], [PX0, PY1 + 0.1, 0], color=C.axis, stroke_width=2.0))
        for v in nice(x0, x1):
            g.add(num(v).move_to([float(sx(v)), PY0 - 0.25, 0]))
        for v in nice(y0, y1, 3):
            if v > y0 + 1e-9:
                lb = num(v)
                g.add(lb.move_to([PX0 - 0.12 - lb.width / 2, float(sy(v)), 0]))
        lo = max(x0, 2.0)
        ps = primes()
        inside = ps[(ps > lo) & (ps <= x1)]
        if len(inside) <= 3000:                          # exact corners: the step happens at each prime
            xs = np.concatenate([[lo], np.repeat(inside, 2), [x1]])
            ys = np.concatenate([[pi_of(lo)], np.column_stack([pi_of(inside) - 1, pi_of(inside)]).ravel(),
                                 [pi_of(x1)]])
        else:
            xs = np.linspace(lo, x1, 1500)
            ys = pi_of(xs)
        a = float(gap_on(t))
        if a > 0:                                        # the gap: between li above and the staircase below
            poly = np.concatenate([np.column_stack([sx(xs), sy(li(xs)), 0 * xs]),
                                   np.column_stack([sx(xs[::-1]), sy(ys[::-1]), 0 * xs])])
            g.add(Polygon(*poly, stroke_width=0, fill_color=C.gap, fill_opacity=seen(0.55) * a))
        r = float(li_on(t))
        if r > 0:                                        # li underneath and wider: where they agree, both show
            xl = np.linspace(lo, lo + r * (x1 - lo), 600)
            lv = VMobject(color=C.smooth, stroke_width=6.0)
            lv.set_points_as_corners(np.column_stack([sx(xl), sy(li(xl)), 0 * xl]))
            g.add(lv)
        st = VMobject(color=C.prime, stroke_width=2.6)
        st.set_points_as_corners(np.column_stack([sx(xs), sy(ys), 0 * xs]))
        g.add(st)
        return g

    p0 = plot(T.cut_pnt)
    w.play(FadeIn(p0), at=T.cut_pnt + 0.15, dur=0.5, lead=0)
    w.remove(p0, at=out[0])
    live(w, plot, out, (T.g_adding - L, T.g_adding + 2.0), (inn[0], T.g_never + 1.0))
    pidef = tex(r"\pi(x)", size=40, color=C.prime)
    pin(pidef, top=3.5, left=PX0)
    h.play(FadeIn(pidef), at=T.cut_pnt + 0.3, dur=0.5, lead=0)

    # ── Gauss, 1792: a number near x is prime with chance about 1/ln x ──
    gauss = caps(r"C. F. Gauss $\cdot$ 1792", 36, C.ink)
    pin(gauss, top=3.5, left=RX0)
    h.play(FadeIn(gauss, shift=0.06 * DOWN), at=T.g_1792 + 0.4, dur=0.6)
    portrait_card(s, h, "gauss", None, T.g_gauss, T.g_1896 + 0.1, (5.55, 2.4), height=2.0)
    pr = tex(r"\Pr(n\ \text{prime})", r"\approx", r"\frac{1}{\ln n}", size=38, colors={2: C.approx})
    pin(pr, top=2.75, left=RX0)
    h.play(Write(pr), at=T.g_chance, dur=1.2)

    sxr = lambda x: RX0 + (RX1 - RX0) * np.asarray(x, float) / 1e6               # noqa: E731
    syr = lambda y: DY0 + (DY1 - DY0) * np.asarray(y, float) / DMAX              # noqa: E731
    daxes = VGroup(Line([RX0, DY0, 0], [RX1 + 0.1, DY0, 0], color=C.axis, stroke_width=2.0),
                   Line([RX0, DY0, 0], [RX0, DY1 + 0.1, 0], color=C.axis, stroke_width=2.0),
                   tex("0", size=22, color=C.muted).move_to([RX0, DY0 - 0.25, 0]),
                   tex(r"10^6", size=22, color=C.muted).move_to([RX1, DY0 - 0.27, 0]),
                   tex("0.1", size=22, color=C.muted).move_to([RX0 - 0.28, float(syr(0.1)), 0]))
    edges = np.arange(0, 1_000_001, BLOCK, dtype=float)
    dens = np.diff(pi_of(edges)) / BLOCK                 # the share of primes in each block of 50,000
    bw = (RX1 - RX0) / len(dens)
    bars = VGroup(*[Rectangle(width=bw * 0.78, height=float(syr(d)) - DY0, stroke_width=0,
                              fill_color=C.prime, fill_opacity=seen(0.7))
                    .move_to([RX0 + bw * (k + 0.5), (DY0 + float(syr(d))) / 2, 0]) for k, d in enumerate(dens)])
    xc = np.linspace(BLOCK / 2, 1e6, 300)
    curve = VMobject(color=C.approx, stroke_width=3.0)
    curve.set_points_smoothly(np.column_stack([sxr(xc), syr(1 / np.log(xc)), 0 * xc]))
    rp.play(FadeIn(daxes), at=T.g_chance + 0.6, dur=0.5, lead=0)
    rp.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08 / 0.5), at=T.g_chance + 0.9,
            dur=0.5 + 0.08 * (len(bars) - 1), lead=0)
    rp.play(Create(curve), at=T.g_million - 0.5, dur=1.2, lead=0)
    one14 = tex(r"\approx\tfrac{1}{14}", size=34, color=C.approx)
    one14.move_to([float(sxr(1e6)) - 0.45, float(syr(1 / np.log(1e6))) + 0.6, 0])
    rp.play(FadeIn(one14, shift=0.06 * DOWN), at=T.g_fourteen, dur=0.5)

    # ── adding up those chances: the logarithmic integral (the area fills as li draws on the left) ──
    def area(t):
        r = float(li_on(t))
        if r <= 0:
            return VGroup()
        xa = np.linspace(BLOCK / 2, BLOCK / 2 + r * (1e6 - BLOCK / 2), 200)
        poly = np.concatenate([np.column_stack([sxr(xa), syr(1 / np.log(xa)), 0 * xa]),
                               [[float(sxr(xa[-1])), DY0, 0], [float(sxr(xa[0])), DY0, 0]]])
        return Polygon(*poly, stroke_width=0, fill_color=C.smooth, fill_opacity=seen(0.35))

    rp.play(bars.animate.set_fill(opacity=seen(0.3)), at=T.g_adding - 0.2, dur=0.5, lead=0)
    filled = rp.redraw(area, during=(T.g_adding - L, T.g_adding + 2.0))
    lif = tex(r"\mathrm{li}(x)", r"\approx\int_2^x\frac{dt}{\ln t}", size=38, colors={0: C.smooth})
    lif.next_to(pidef, RIGHT, buff=0.7).align_to(pidef, UP).shift(0.05 * UP)
    h.play(Write(lif), at=T.g_li, dur=1.2)

    # ── at a million: within two tenths of a percent ──
    nums = VGroup(tex(r"\pi(10^6)", r"=" + fmt(pi_of(1e6)), size=32, colors={0: C.prime}),
                  tex(r"\mathrm{li}(10^6)", r"\approx" + fmt(li(1e6)), size=32, colors={0: C.smooth}))
    nums.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    pin(nums, top=PY1 - 0.15, left=PX0 + 0.3)
    h.play(FadeIn(nums[0], shift=0.06 * DOWN), at=T.g_atmillion, dur=0.5)
    h.play(FadeIn(nums[1], shift=0.06 * DOWN), at=T.g_atmillion + 0.7, dur=0.5)
    pct = 100 * (1 - pi_of(1e6) / li(1e6))
    within = lab(r"within %.1f\%%" % pct, 28, C.muted).next_to(nums, DOWN, buff=0.22, aligned_edge=LEFT)
    h.play(FadeIn(within), at=T.g_true, dur=0.5)

    # ── 1896: the ratio goes to one, the prime number theorem ──
    h.play(FadeOut(VGroup(gauss, pr)), at=T.g_1896 - 0.3, dur=0.4, lead=0)
    rp.play(FadeOut(VGroup(bars, curve, one14, daxes, filled)), at=T.g_1896 - 0.3, dur=0.4, lead=0)
    names = VGroup(caps(r"J. Hadamard", 28, C.ink), caps(r"C. de la Vall\'ee Poussin", 28, C.ink))
    names.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    yr = caps("1896", 34, C.muted).next_to(names[0], RIGHT, buff=0.35)
    pin(VGroup(names, yr), top=3.5, left=RX0)
    yr.next_to(names[0], RIGHT, buff=0.35)
    h.play(FadeIn(yr), at=T.g_1896 + 0.2, dur=0.5)
    h.play(FadeIn(names[0], shift=0.06 * DOWN), at=T.g_hadamard, dur=0.5)
    h.play(FadeIn(names[1], shift=0.06 * DOWN), at=T.g_vallee, dur=0.5)
    portrait_card(s, h, "hadamard", None, T.g_hadamard, inn[0] + 0.3, (4.95, 1.9), height=1.4)
    portrait_card(s, h, "dlvp", None, T.g_vallee, inn[0] + 0.3, (6.15, 1.9), height=1.4)

    lx = lambda x: RX0 + (RX1 - RX0) * (np.log10(np.asarray(x, float)) - 1) / 5     # noqa: E731
    ly = lambda y: QY0 + (QY1 - QY0) * (np.asarray(y, float) - QLO) / (QHI - QLO)   # noqa: E731
    one = DashedLine([RX0, float(ly(1)), 0], [RX1, float(ly(1)), 0], color=C.muted, stroke_width=1.6,
                     dash_length=0.08)
    qaxes = VGroup(Line([RX0, QY0, 0], [RX1 + 0.1, QY0, 0], color=C.axis, stroke_width=2.0),
                   Line([RX0, QY0, 0], [RX0, QY1 + 0.1, 0], color=C.axis, stroke_width=2.0),
                   *[tex(t_, size=22, color=C.muted).move_to([float(lx(v)), QY0 - 0.27, 0])
                     for v, t_ in ((10, "10"), (1e2, "10^2"), (1e4, "10^4"), (1e6, "10^6"))],
                   tex("1", size=22, color=C.muted).move_to([RX0 - 0.2, float(ly(1)), 0]),
                   tex("0.8", size=22, color=C.muted).move_to([RX0 - 0.28, float(ly(0.8)), 0]), one)
    xq = np.logspace(1, 6, 1500)
    ratio = VMobject(color=C.text, stroke_width=2.4)
    ratio.set_points_as_corners(np.column_stack([lx(xq), ly(pi_of(xq) / li(xq)), 0 * xq]))
    rp.play(FadeIn(qaxes), at=T.g_hadamard, dur=0.6)
    rp.play(Create(ratio, rate_func=linear), at=T.g_toone - 1.6, dur=1.8)
    thm = tex(r"\frac{\pi(x)}{\mathrm{li}(x)}", r"\to", r"1", size=40, colors={0: C.text})
    thm[0][0:4].set_color(C.prime)
    thm[0][5:].set_color(C.smooth)
    thm.move_to([RX1 - 1.3, QY0 + 1.05, 0])
    h.play(FadeIn(thm, shift=0.06 * UP), at=T.g_toone, dur=0.6)
    pnt = lab("prime number theorem", 28, C.text).next_to(thm, DOWN, buff=0.22)
    h.play(FadeIn(pnt), at=T.g_pnt, dur=0.6)

    # ── both proofs used zeta, and one fact about where its zeros can't be (paid off in s16) ──
    zs = tex(r"\zeta(s)", size=40, color=C.zeta)
    pin(zs, top=2.45, left=RX0)
    h.play(FadeIn(zs, shift=0.06 * DOWN), at=T.g_both + 0.4, dur=0.6)
    fact = tex(r"\zeta(1+it)", r"\neq0", size=40)
    pin(fact, top=2.45, left=RX0)
    nz = lab("no zeros on Re $s=1$", 28, C.text).next_to(fact, RIGHT, buff=0.35)
    h.play(ReplacementTransform(zs, fact[0]), FadeIn(fact[1]), at=T.g_cantbe, dur=0.8)
    h.play(FadeIn(nz), at=T.g_cantbe + 0.5, dur=0.5)

    # ── still, the staircase never matches the curve: widen, zoom into 100,000-102,000, the gap in red ──
    h.play(FadeOut(VGroup(names, yr, thm, pnt, fact, nz, nums, within)), at=inn[0] - 0.1, dur=0.4, lead=0)
    rp.play(FadeOut(VGroup(qaxes, ratio)), at=inn[0] - 0.1, dur=0.4, lead=0)

    (x0, x1, y0, y1), _, sx, sy = geom(inn[1] + 1.0)
    xg = np.linspace(ZX0, ZX1, 4001)
    gap = li(xg) - pi_of(xg)
    xm = float(xg[np.argmax(gap)])
    top_, bot_ = float(sy(li(xm))), float(sy(pi_of(xm)))
    ruler = DoubleArrow([float(sx(xm)), bot_, 0], [float(sx(xm)), top_, 0], buff=0, color=C.text, stroke_width=3,
                        tip_length=0.14, max_tip_length_to_length_ratio=0.3)
    q = carded(tex("?", size=40), buff=0.08, opacity=1.0).next_to(ruler, RIGHT, buff=0.12)
    h.play(GrowFromCenter(ruler), at=T.g_howfar, dur=0.6)
    h.play(FadeIn(q), at=T.g_howfar + 0.4, dur=0.4)
    howfar = tex(r"\pi(x)-\mathrm{li}(x)", r"=", r"\ ?", size=40, colors={0: C.gap})
    howfar.move_to([PX1B - howfar.width / 2, 3.5 - howfar.height / 2, 0])
    h.play(Write(howfar), at=T.g_howfar + 0.6, dur=1.0)
