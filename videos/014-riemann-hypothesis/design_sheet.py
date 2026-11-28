"""Design sheet for 014. Page 1 = palette, type, motion; pages 2-3 = look frames computed from the real maths.

    uv run python videos/014-riemann-hypothesis/design_sheet.py     # writes out/design/design_{1,2,3}.png

Drawn with matplotlib in the bundled Computer Modern faces (cmr10 / cmss10 / cmtt10) so it runs without LaTeX.
Production frames use Manim + LaTeX with the same theme tokens; only the type rendering differs.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from theme import theme as C  # noqa: E402
from zmath import domain_rgb, hardy_Z, pi_explicit, prime_pi, primes_upto, zeta  # noqa: E402

OUT = HERE / "out" / "design"
OUT.mkdir(parents=True, exist_ok=True)
G = np.load(HERE / "assets" / "zeros.npy")

FD = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
ROMAN = fm.FontProperties(fname=FD / "cmr10.ttf")
SANS = fm.FontProperties(fname=FD / "cmss10.ttf")
MONO = fm.FontProperties(fname=FD / "cmtt10.ttf")
plt.rcParams.update({"mathtext.fontset": "cm", "axes.unicode_minus": False, "figure.facecolor": "black",
                     "axes.facecolor": "black", "savefig.facecolor": "black"})
TEXT, MUTED = "#ffffff", "#9a9a9a"


def tok(name):
    return getattr(C, name)


def clean(ax):
    ax.set_xticks([]), ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def panel(ax, title):
    clean(ax)
    for s in ax.spines.values():
        s.set_visible(True), s.set_color("#3a3a3a"), s.set_linewidth(0.8)
    ax.set_title(title, color=MUTED, fontproperties=SANS, fontsize=13, loc="left", pad=6)


# ------------------------------------------------------------------------------------------------ page 1
def page1():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.text(0.03, 0.95, "The Riemann Hypothesis", color=TEXT, fontproperties=ROMAN, fontsize=34)
    fig.text(0.03, 0.915, "design sheet 1: palette, type, motion   /   Classic: black, crisp, no glow",
             color=MUTED, fontproperties=SANS, fontsize=15)

    roles = [("prime", "primes, staircase steps"), ("smooth", "li(x), R(x)"), ("approx", "x / ln x"),
             ("gap", r"the error $\pi - \mathrm{li}$"), ("bound", "RH envelope"), ("zero", "a zero + its wave"),
             ("trivial", "trivial zeros"), ("crit", "critical line, strip"), ("s_in", "the input s"),
             ("zeta", r"$\zeta$, spiral, product paths"), ("rogue", "what-if off-line zero"),
             ("ffield", "solutions mod p"), ("lean", "Lean, kernel"),
             ("ai", "AI as actor"), ("human", "people as actors"), ("evidence", "rung: evidence"),
             ("claimed", "claimed (outline only)"), ("conj", "conjecture"), ("ink", "history cards")]
    ax = fig.add_axes([0.03, 0.30, 0.42, 0.58])
    clean(ax)
    ax.set_xlim(0, 2), ax.set_ylim(0, 10.4)
    for i, (r, what) in enumerate(roles):
        x, y = (i // 10), 9.6 - (i % 10)
        ax.add_patch(plt.Rectangle((x + 0.02, y), 0.18, 0.7, color=tok(r)))
        ax.text(x + 0.25, y + 0.42, r, color=TEXT, fontproperties=MONO, fontsize=15)
        ax.text(x + 0.25, y + 0.08, f"{what}   {tok(r)}", color=MUTED, fontproperties=SANS, fontsize=11.5)
    x, y = 1, 9.6 - 9  # the free slot at the foot of column 2
    for k, p in enumerate((2, 3, 5, 7)):
        ax.add_patch(plt.Rectangle((x + 0.02 + 0.047 * k, y), 0.04, 0.7, color=tok(f"sieve{p}")))
    ax.text(x + 0.25, y + 0.42, "sieve2 3 5 7", color=TEXT, fontproperties=MONO, fontsize=15)
    ax.text(x + 0.25, y + 0.08, "combs, sieve grid, Euler product", color=MUTED, fontproperties=SANS, fontsize=11.5)

    # typography
    ax = fig.add_axes([0.50, 0.50, 0.47, 0.38])
    clean(ax)
    ax.set_xlim(0, 1), ax.set_ylim(0, 1)
    ax.text(0, 0.86, r"$\zeta(s)=\sum_{n=1}^{\infty}\frac{1}{n^{s}}=\prod_{p}\frac{1}{1-p^{-s}}$", color=TEXT,
            fontsize=34)
    ax.text(0, 0.62, r"$\mathrm{Re}(s)=\frac{1}{2}$", color=tok("crit"), fontsize=34)
    ax.text(0.36, 0.62, r"$\rho=\frac{1}{2}+i\gamma$", color=tok("zero"), fontsize=34)
    ax.text(0, 0.42, "maths  CM roman  /  hero 72-96 px, working 48 px", color=MUTED, fontproperties=SANS, fontsize=13)
    ax.text(0, 0.30, "critical line    zeros    primes", color=TEXT, fontproperties=SANS, fontsize=22)
    ax.text(0, 0.21, "key words  CM sans  /  34 px, never a sentence", color=MUTED, fontproperties=SANS, fontsize=13)
    ax.text(0, 0.08, "B. RIEMANN   1859", color=tok("ink"), fontproperties=ROMAN, fontsize=22)
    ax.text(0.5, 0.08, "theorem RiemannHypothesis", color=tok("lean"), fontproperties=MONO, fontsize=20)
    ax.text(0, -0.02, "names & dates  CM small caps        Lean code  CM typewriter", color=MUTED,
            fontproperties=SANS, fontsize=13)

    # motion language: the four eases
    ax = fig.add_axes([0.50, 0.08, 0.47, 0.32])
    panel(ax, "motion:  smooth (fades)  /  easy-ease (moves)  /  no out-back pops  /  camera flight (ease in-out, 6-10 s)")
    u = np.linspace(0, 1, 200)
    smooth = u * u * (3 - 2 * u)
    easy = np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2)
    flight = 0.5 - 0.5 * np.cos(np.pi * u)
    for y, c, lab in ((smooth, tok("smooth"), "smooth"), (easy, tok("zeta"), "easy-ease"),
                      (flight, tok("crit"), "flight")):
        ax.plot(u, y, color=c, lw=2.4)
        ax.text(1.02, y[-1] - 0.05 * ("smooth", "easy-ease", "flight").index(lab), lab, color=c,
                fontproperties=SANS, fontsize=12)
    ax.set_xlim(-0.02, 1.2), ax.set_ylim(-0.05, 1.1)

    ax = fig.add_axes([0.03, 0.06, 0.42, 0.18])
    clean(ax)
    rules = ["Hue is data only in domain coloring: everywhere else one object = one color.",
             "A zero and its wave share pink: the eye links cause and effect.",
             "Proven = solid lines. Conditional = solid + small 'if RH' tag. Conjecture = dashed.",
             "Claimed = amber outline, never filled. Nothing on screen says 'proved' for the 20 Nov claim."]
    for i, r in enumerate(rules):
        ax.text(0, 0.85 - 0.25 * i, "-  " + r, color=TEXT, fontproperties=SANS, fontsize=13.5)
    fig.savefig(OUT / "design_1.png")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ page 2
def page2():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.text(0.03, 0.955, "design sheet 2: look frames from the real maths", color=TEXT, fontproperties=ROMAN,
             fontsize=26)

    # (a) s01 staircase + waves + the line of zeros
    ax = fig.add_axes([0.03, 0.52, 0.45, 0.39])
    panel(ax, "s02 / s16  staircase rebuilt from 30 zero pairs")
    x = np.linspace(2, 60, 500)
    ax.step(np.arange(1, 61), prime_pi(np.arange(1, 61)), where="post", color=tok("prime"), lw=2.2)
    ax.plot(x, pi_explicit(x, []), color=tok("smooth"), lw=1.6)
    ax.plot(x, pi_explicit(x, G[:30]), color=tok("zero"), lw=1.6)
    ax.set_xlim(0, 75), ax.set_ylim(-1, 19)
    ax.axvline(68, color=tok("crit"), lw=1.2, ymin=0.05, ymax=0.95)
    for gg in G[:30]:
        ax.plot(68, 0.15 + gg / 105 * 18, "o", color=tok("zero"), ms=3.5)
    ax.text(69.2, 0.4, r"$\frac{1}{2}+i\gamma$", color=tok("zero"), fontsize=14)

    # (b) s10/s11 domain coloring with strip, line, zeros, trivial zeros
    ax = fig.add_axes([0.52, 0.52, 0.45, 0.39])
    panel(ax, r"s10 - s13  $\zeta$ domain coloring  /  strip  /  critical line  /  zeros")
    sx, sy = np.meshgrid(np.linspace(-7, 4, 700), np.linspace(-2, 36, 400))
    w = zeta(sx + 1j * sy)
    ax.imshow(domain_rgb(w), extent=(-7, 4, -2, 36), origin="lower", aspect="auto")
    ax.axvspan(0, 1, color=tok("crit"), alpha=0.12)
    ax.axvline(0.5, color=tok("crit"), lw=1.4)
    ax.plot(np.full(6, 0.5), G[:6], "o", mfc="none", mec="white", ms=9, mew=1.4)
    ax.plot([-2, -4, -6], [0] * 3, "o", mfc="none", mec=tok("trivial"), ms=9, mew=1.4)
    ax.plot([1], [0], "x", color="white", ms=9, mew=1.6)
    ax.set_xlim(-7, 4), ax.set_ylim(-2, 36)

    # (c) s08 spiral of partial sums at s = 1.4 + 6i
    ax = fig.add_axes([0.03, 0.06, 0.22, 0.40])
    panel(ax, "s09  partial sums, s = 1.4 + 6i")
    s = 1.4 + 6j
    n = np.arange(1, 400)
    ps = np.concatenate([[0], np.cumsum(n ** -s)])
    ax.plot(ps.real, ps.imag, color=tok("zeta"), lw=1.3)
    for k in range(12):
        ax.annotate("", xy=(ps[k + 1].real, ps[k + 1].imag), xytext=(ps[k].real, ps[k].imag),
                    arrowprops=dict(arrowstyle="-|>", color=tok("s_in"), lw=1.4))
    z = zeta(np.array([s]))[0]
    ax.plot(z.real, z.imag, "o", color="white", ms=6)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlim(-0.2, 1.6), ax.set_ylim(-0.9, 0.9)

    # (d) s15 Hardy's Z: each crossing pings a zero on the critical line above it
    ax = fig.add_axes([0.27, 0.06, 0.24, 0.40])
    panel(ax, r"s15  Hardy's $Z(t)$: each crossing is a zero on the line")
    t = np.linspace(0.5, 50, 2500)
    z = hardy_Z(t)
    top = 1.25 * np.abs(z).max()
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.plot(t, z, color=tok("zero"), lw=1.5)
    ax.plot([0, 50], [top, top], color=tok("crit"), lw=1.6)
    for gg in G[G < 50]:
        ax.plot([gg, gg], [0, top], color=tok("zero"), lw=0.7, ls=(0, (2, 3)))
        ax.plot(gg, top, "o", color=tok("zero"), ms=5)
        ax.plot(gg, 0, "o", mfc="none", mec=tok("zero"), ms=5)
    ax.text(1, top * 1.06, r"$\mathrm{Re}(s)=\frac{1}{2}$", color=tok("crit"), fontsize=12)
    ax.set_xlim(0, 50), ax.set_ylim(-0.8 * top, top * 1.2)
    # (e) s17 an off-line zero's wave vs the sqrt envelope
    ax = fig.add_axes([0.55, 0.06, 0.20, 0.40])
    panel(ax, r"s17  wave amplitude $x^{\sigma}$")
    xx = np.logspace(1, 8, 300)
    ax.loglog(xx, np.sqrt(xx) * np.log(xx) / (8 * np.pi), color=tok("bound"), lw=1.6, ls="--")
    ax.loglog(xx, xx ** 0.5, color=tok("zero"), lw=2)
    ax.loglog(xx, xx ** 0.8, color=tok("rogue"), lw=2)
    ax.text(1e6, 4e5, r"what if $\sigma = 0.8$", color=tok("rogue"), fontproperties=SANS, fontsize=12, ha="right")
    ax.text(8e7, 2.2e4, r"$\sigma = \frac{1}{2}$", color=tok("zero"), fontproperties=SANS, fontsize=12, ha="right")
    ax.text(1e5, 12, r"$\sqrt{x}\,\ln x\,/\,8\pi$  (if RH)", color=tok("bound"), fontsize=11)

    # (f) s20 status ladder
    ax = fig.add_axes([0.77, 0.06, 0.20, 0.40])
    panel(ax, "s30  status ladder")
    ax.set_xlim(0, 1), ax.set_ylim(0, 4.4)
    rungs = [("evidence", r"$10^{13}$ zeros checked", tok("evidence"), "-"),
             ("theorem", r"$\geq$ 2/3 on the line: people + Lean", tok("human"), "-"),
             ("proposed proof", "RH: machine checks partly complete", tok("claimed"), "-"),
             ("understood, accepted", "Clay: published + 2 yr + consensus", tok("conj"), ":")]
    for i, (name, ex, c, ls) in enumerate(rungs):
        ax.add_patch(plt.Rectangle((0.06, 0.25 + i), 0.88, 0.75, fill=False, ec=c, lw=1.6, ls=ls))
        ax.text(0.1, 0.72 + i, name, color=c, fontproperties=SANS, fontsize=12.5)
        ax.text(0.1, 0.38 + i, ex, color=MUTED, fontproperties=SANS, fontsize=10.5)
    fig.savefig(OUT / "design_2.png")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ page 3
def page3():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.text(0.03, 0.955, "design sheet 3: the v2 shots", color=TEXT, fontproperties=ROMAN, fontsize=26)

    # (a) s01 the news open: claim in an amber outline, the line of zeros planted, the file wall
    ax = fig.add_axes([0.03, 0.52, 0.30, 0.39])
    panel(ax, "s01  news open: claim outlined, line of zeros planted")
    ax.set_xlim(0, 16), ax.set_ylim(0, 9)
    ax.plot([13.5, 13.5], [0.3, 9], color=tok("crit"), lw=1.4)
    for gg in G[:60]:
        y = 0.4 + gg / 100 * 8.6
        if y < 9:
            ax.plot(13.5, y, "o", color=tok("zero"), ms=3)
    ax.text(0.6, 7.9, r"$\mathrm{20 \cdot XI \cdot 2026}$", color=tok("ink"), fontsize=17)
    ax.text(0.6, 7.0, r"L. ALP$\mathrm{\ddot{O}}$GE  /  ANTHROPIC", color=tok("ink"), fontproperties=ROMAN, fontsize=15)
    ax.add_patch(plt.Rectangle((0.5, 5.4), 11.2, 1.1, fill=False, ec=tok("claimed"), lw=1.8))
    ax.text(0.8, 5.78, "claimed:  a proof of the Riemann hypothesis", color=tok("claimed"), fontproperties=SANS,
            fontsize=14)
    wall = np.zeros((44, 220, 3))
    lean = np.array(matplotlib.colors.to_rgb(tok("lean")))
    wall[np.ix_(np.arange(44) % 4 != 3, np.arange(220) % 4 != 3)] = lean * 0.75
    ax.imshow(wall, extent=(0.5, 11.7, 1.4, 4.6), aspect="auto", interpolation="nearest")
    ax.text(0.6, 0.6, "175,187 Lean files  /  checks running", color=tok("lean"), fontproperties=SANS, fontsize=12)
    for k, chip in enumerate(("1859", r"\$1,000,000")):
        ax.text(8.7 + 1.5 * k, 0.6, chip, color=TEXT, fontproperties=SANS, fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="#5a5a5a"))

    # (b) s04 Euclid's combs: 210 is on every comb, 211 on none
    ax = fig.add_axes([0.36, 0.52, 0.30, 0.39])
    panel(ax, "s04  Euclid: 210 sits on every comb, 211 on none")
    x0, x1 = 196, 216
    ax.set_xlim(x0 - 1.6, x1 + 0.8), ax.set_ylim(-1.6, 6.2)
    ax.plot([x0, x1], [0, 0], color=TEXT, lw=1)
    for k, p in enumerate((2, 3, 5, 7)):
        c = tok(f"sieve{p}")
        for m in range(x0, x1 + 1):
            if m % p == 0:
                ax.plot([m, m], [0.25 + 1.1 * k, 1.0 + 1.1 * k], color=c, lw=2.4, solid_capstyle="butt")
        ax.text(x0 - 1.4, 0.45 + 1.1 * k, rf"$\times {p}$", color=c, fontsize=13)
    for m in (200, 205, 215):
        ax.text(m, -0.75, str(m), color=MUTED, fontproperties=SANS, fontsize=11, ha="center")
    ax.plot([210, 210], [0, 4.6], color=TEXT, lw=0.8, ls=(0, (2, 2)))
    ax.plot([211, 211], [0, 4.6], color=tok("prime"), lw=1.6)
    ax.text(209.7, -0.75, "210", color=TEXT, fontproperties=SANS, fontsize=12, ha="right")
    ax.text(211.3, -0.75, "211", color=tok("prime"), fontproperties=SANS, fontsize=12, ha="left")
    ax.text(x0 - 1.2, 5.1, r"$2\cdot3\cdot5\cdot7+1=211,\quad 211\equiv1\ (\mathrm{mod}\ 2,3,5,7)$", color=TEXT,
            fontsize=15)

    # (c) s20 the Lehmer near-miss: at full scale the wave seems to touch zero; the magnifier (about x200 in t,
    # Z rescaled so +-0.01 fills it) shows two crossings 0.0377 apart, a +0.004 peak, and the what-if ghost
    ax = fig.add_axes([0.69, 0.52, 0.28, 0.39])
    panel(ax, r"s20  Lehmer 1956: two zeros 0.0377 apart near $t=7005$")
    tt = np.linspace(6995, 7015, 4000)
    zz = hardy_Z(tt)
    A = np.abs(zz).max()
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.plot(tt, zz, color=tok("zero"), lw=1.2)
    ax.set_xlim(tt[0], tt[-1]), ax.set_ylim(-1.1 * A, 3.3 * A)  # headroom: the inset sits above the spike
    ax.plot(7005.08, 0, "o", mfc="none", mec=TEXT, ms=15, mew=1.0)
    ax.annotate("", xy=(0.40, 0.56), xycoords="axes fraction", xytext=(7005.08, 0.06 * A), textcoords="data",
                arrowprops=dict(arrowstyle="-", color="#5a5a5a", lw=0.8))
    axin = ax.inset_axes([0.40, 0.56, 0.57, 0.41])
    clean(axin)
    for s_ in axin.spines.values():
        s_.set_visible(True), s_.set_color("#5a5a5a")
    tb = np.linspace(7005.035, 7005.13, 800)
    zb = hardy_Z(tb)
    g1, g2 = 7005.0629, 7005.1006
    axin.axhline(0, color=MUTED, lw=0.8)
    axin.plot(tb, zb, color=tok("zero"), lw=1.6)
    axin.plot(tb, zb - 0.005, color=tok("rogue"), lw=1.2, ls=(0, (3, 2)))
    axin.set_xlim(tb[0], tb[-1]), axin.set_ylim(-0.0125, 0.0095)
    axin.text(7005.094, 0.0050, "+0.004", color=tok("zero"), fontproperties=SANS, fontsize=11)
    axin.text(7005.0365, 0.0088, "what if 0.005 lower:\nno crossing", color=tok("rogue"), fontproperties=SANS,
              fontsize=9.5, va="top")
    axin.plot([g1, g2], [-0.0075, -0.0075], color=TEXT, lw=0.9)
    for g in (g1, g2):
        axin.plot([g, g], [-0.0068, -0.0082], color=TEXT, lw=0.9)
        axin.plot(g, 0, "o", color=tok("zero"), ms=4)
    axin.text((g1 + g2) / 2, -0.0106, "0.0377   (usual gap 0.8955)", color=TEXT, fontproperties=SANS,
              fontsize=10, ha="center")

    # (d) s22 the clock-arithmetic version: 104 solutions mod 101, and every prime below 5000 inside the band
    ax = fig.add_axes([0.03, 0.06, 0.30, 0.40])
    panel(ax, r"s22  $y^2\equiv x^3+x+1$ (mod p):  p = 101 has 104 solutions")
    p = 101
    xs, ys = np.meshgrid(np.arange(p), np.arange(p))
    on = (ys * ys - (xs ** 3 + xs + 1)) % p == 0
    grid = ax.inset_axes([0.03, 0.05, 0.50, 0.90])
    clean(grid)
    grid.add_patch(plt.Rectangle((-0.5, -0.5), p, p, fill=False, ec="#3a3a3a", lw=0.8))
    grid.scatter(xs[on], ys[on], s=6, color=tok("ffield"))
    grid.axhline(p / 2, color="#3a3a3a", lw=0.6, ls=(0, (2, 3)))  # y <-> p - y mirrors every solution
    grid.set_xlim(-2, p + 1), grid.set_ylim(-2, p + 1), grid.set_aspect("equal")
    axin = ax.inset_axes([0.60, 0.16, 0.37, 0.70])
    clean(axin)
    for s_ in axin.spines.values():
        s_.set_visible(True), s_.set_color("#5a5a5a")
    P = primes_upto(5000)

    def count(q):
        sq = np.zeros(q, dtype=np.int64)
        np.add.at(sq, (np.arange(q, dtype=np.int64) ** 2) % q, 1)
        x = np.arange(q, dtype=np.int64)
        return sq[(x ** 3 + x + 1) % q].sum()

    ratio = np.array([(count(int(q)) - q) / (2 * np.sqrt(q)) for q in P])
    axin.scatter(P, ratio, s=1.2, color=tok("ffield"))
    for yy in (-1, 1):
        axin.axhline(yy, color=tok("bound"), lw=0.9, ls=(0, (3, 2)))
    axin.set_ylim(-1.3, 1.3), axin.set_xlim(0, 5000)
    axin.set_title("$(A_p-p)\\,/\\,2\\sqrt{p}$\nall 669 primes < 5000", color=MUTED, fontsize=10, loc="left")
    axin.text(5000, 1.06, "+1", color=tok("bound"), fontproperties=SANS, fontsize=10, ha="right")
    axin.text(5000, -1.22, "-1", color=tok("bound"), fontproperties=SANS, fontsize=10, ha="right")

    # (e) s19 the product over primes: settles where the sum works, wanders inside the strip
    ax = fig.add_axes([0.36, 0.06, 0.30, 0.40])
    panel(ax, r"s19  $\prod_p(1-p^{-s})^{-1}$: settles at $2+5i$, wanders at $\frac{1}{2}+20i$")
    clean(ax)
    pr = primes_upto(30000).astype(float)
    for k, (s, ttl) in enumerate(((2 + 5j, "Re s = 2"), (0.5 + 20j, "Re s = 1/2"))):
        sub = ax.inset_axes([0.03 + 0.5 * k, 0.05, 0.44, 0.82])
        clean(sub)
        pp = np.concatenate([[1 + 0j], np.cumprod(1.0 / (1.0 - pr ** (-s)))])
        sub.plot(pp.real, pp.imag, color=tok("zeta"), lw=1.0, ls="-" if k == 0 else (0, (3, 1.5)))
        sub.plot(1, 0, "o", mfc="none", mec=tok("s_in"), ms=6)
        if k == 0:
            zz0 = zeta(np.array([s]))[0]
            sub.plot(zz0.real, zz0.imag, "o", color="white", ms=5)
            sub.annotate(r"$\zeta(2+5i)$", (zz0.real, zz0.imag), xytext=(12, 10), textcoords="offset points",
                         color=TEXT, fontsize=12)
        else:
            sub.text(0.5, 0.02, "no limit", color=MUTED, fontproperties=SANS, fontsize=11, ha="center",
                     transform=sub.transAxes)
        sub.set_aspect("equal", adjustable="datalim")
        sub.set_title(ttl, color=MUTED, fontproperties=SANS, fontsize=11)

    # (f) s27 Robin: sigma(n) / (n ln ln n) under e^gamma for every n > 5040
    ax = fig.add_axes([0.69, 0.06, 0.28, 0.40])
    panel(ax, r"s27  Robin 1984: $\sigma(n) < e^{\gamma}\,n\ln\ln n$ for $n>5040$")
    N = 100_000
    sig = np.zeros(N + 1, dtype=np.int64)
    for d in range(1, N + 1):
        sig[d::d] += d
    n = np.arange(10, N + 1)
    r = sig[10:] / (n * np.log(np.log(n)))
    eg = float(np.exp(0.5772156649015329))
    above = r > eg
    ax.scatter(n[~above], r[~above], s=0.6, color=tok("ink"), alpha=0.4, linewidths=0)
    ax.scatter(n[above], r[above], s=12, color=tok("ink"), linewidths=0)
    ax.axhline(eg, color=tok("bound"), lw=1.4)
    ax.plot(5040, sig[5040] / (5040 * np.log(np.log(5040))), "o", mfc="none", mec=tok("ink"), ms=11, mew=1.4)
    ax.text(5040, 2.02, "n = 5040, the last one above", color=TEXT, fontproperties=SANS, fontsize=11, ha="center")
    ax.text(14, eg - 0.16, r"$e^{\gamma}\approx1.781$", color=tok("bound"), fontsize=12)
    ax.set_xscale("log"), ax.set_xlim(10, N), ax.set_ylim(0.6, 2.7)
    assert n[above].max() == 5040
    fig.savefig(OUT / "design_3.png")
    plt.close(fig)


if __name__ == "__main__":
    page1()
    page2()
    page3()
    print(f"wrote {OUT/'design_1.png'}, {OUT/'design_2.png'} and {OUT/'design_3.png'}")
