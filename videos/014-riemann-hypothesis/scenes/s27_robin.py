"""s27 robin (P47): a check that avoids Mathlib's zeta. For every n from 10 to 10^5 (log axis), sigma(n)/(n ln ln n);
the solid line is e^gamma ~ 1.781. The 26 numbers that break the inequality (orange) all lie at or below 5040; an inset
magnifies the top edge, where 5040 (sigma = 19,344) is the last point above the line. Robin (1984): RH iff
sigma(n) < e^gamma n ln ln n for every n > 5040. The proof joined to a Robin formalization is being checked; the
Buzzard card gains that row. Everything fades except the card."""
from aion import *

from beats import T
from look import caps, lab, tex
from robin import EG, data
from status import buzzard_card, chip, ring

MX0, MX1, MY0, MY1 = -6.2, 0.6, -3.2, 0.9       # the main plot
RY0, RY1 = 0.3, 2.6                             # its ratio range; x is log10 n from 1 to 5
IX0, IX1, IY0, IY1 = 1.7, 6.3, -3.2, 0.6        # the inset
IR0, IR1 = 1.70, 1.82                           # the inset's ratio range; x is log10 n from 3 to 5


def mx(n):
    return MX0 + (MX1 - MX0) * (np.log10(n) - 1) / 4


def my(r):
    return MY0 + (MY1 - MY0) * (np.asarray(r, float) - RY0) / (RY1 - RY0)


def ix(n):
    return IX0 + (IX1 - IX0) * (np.log10(n) - 3) / 2


def iy(r):
    return IY0 + (IY1 - IY0) * (np.asarray(r, float) - IR0) / (IR1 - IR0)


@scene(T.cut_robin, T.cut_checks)
def s27_robin(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_checks - 0.5, T.cut_checks - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)
    bz = s.manim(z=7, parallax=0.0)
    card = buzzard_card()
    bz.add(card)

    n, sg, r = data()
    keep = n >= 10
    n, sg, r = n[keep], sg[keep], r[keep]
    bad = r >= EG
    P = np.stack([mx(n), my(r)], axis=1)
    stream = keys((T.rb_sums, 1.0), (T.rb_sums + 3.0, 5.0, "in_out_sine"), lead=0)
    show = keys((T.rb_sums - 0.3, 0.0), (T.rb_sums, 1.0), (bye[0], 1.0), (bye[1], 0.0), lead=0)
    lg = np.log10(n)

    def pos(sel):
        def f(t):
            m = sel & (lg <= float(stream(t)))
            return P[m] if m.any() else P[:1] * 0 + 99
        return f

    s.add(PointsLayer(pos(~bad), color=C.ink, size=1.5, glow=0.0, alpha=0.3, z=3, parallax=0.0, opacity=show))
    s.add(PointsLayer(pos(bad), color=C.rogue, size=4.5, glow=0.0, alpha=1.0, z=4, parallax=0.0, opacity=show))

    # ── one test avoids the definition: Robin, 1984 ──
    who = caps(r"G. Robin $\cdot$ 1984", 32, C.ink)
    who.move_to([-6.3 + who.width / 2, 1.95, 0])
    h.play(FadeIn(who, shift=0.06 * UP), at=T.rb_robin, dur=0.5)
    st = tex(r"\sigma(n)<e^{\gamma}\,n\ln\ln n", r"\ \text{for all } n>5040", r"\ \iff\ \text{RH}", size=36,
             colors={2: C.crit})
    st.move_to([-6.3 + st.width / 2, 3.1, 0])
    h.play(Write(st[0]), at=T.rb_equiv, dur=1.0)
    h.play(FadeIn(st[1]), at=T.rb_past, dur=0.5)
    h.play(FadeIn(st[2]), at=T.rb_past + 0.9, dur=0.5)
    sig = tex(r"\sigma(n)=\sum_{d\mid n}d", size=32).move_to([-1.6, 1.95, 0])
    h.play(FadeIn(sig), at=T.rb_sums, dur=0.5)

    # ── the plot: sigma(n)/(n ln ln n) under the line e^gamma ──
    ax = VGroup(Line([MX0, MY0, 0], [MX1, MY0, 0], color=C.muted, stroke_width=1.6),
                Line([MX0, MY0, 0], [MX0, MY1, 0], color=C.muted, stroke_width=1.6),
                *[tex(f"10^{k}", size=22, color=C.muted).move_to([float(mx(10 ** k)), MY0 - 0.25, 0])
                  for k in range(1, 6)])
    line = Line([MX0, float(my(EG)), 0], [MX1, float(my(EG)), 0], color=C.bound, stroke_width=2.4)
    eg = tex(r"e^{\gamma}", size=28, color=C.bound).move_to([MX1 + 0.35, float(my(EG)), 0])
    ylab = tex(r"\frac{\sigma(n)}{n\ln\ln n}", size=26, color=C.ink).move_to([MX1 - 0.55, MY1 - 0.15, 0])
    w.play(Create(ax), Create(line), FadeIn(eg), FadeIn(ylab), at=T.rb_sums - 0.4, dur=0.6, lead=0)

    # ── the inset: the top edge, magnified; 5040 is the last point above ──
    frame = Rectangle(width=IX1 - IX0, height=IY1 - IY0, stroke_color=C.muted, stroke_width=1.4).move_to(
        [(IX0 + IX1) / 2, (IY0 + IY1) / 2, 0])
    zoomed = VGroup()
    for a, b in zip(n, r):
        if a >= 1000 and IR0 < b < IR1:
            zoomed.add(Dot([float(ix(a)), float(iy(b)), 0], radius=0.05, color=C.rogue if b >= EG else C.ink))
    iline = Line([IX0, float(iy(EG)), 0], [IX1, float(iy(EG)), 0], color=C.bound, stroke_width=2.4)
    iticks = VGroup(*[tex(f"10^{k}", size=22, color=C.muted).move_to([float(ix(10 ** k)), IY0 - 0.25, 0])
                      for k in (3, 4, 5)])
    src = Rectangle(width=float(mx(1e5) - mx(1e3)), height=float(my(IR1) - my(IR0)), stroke_color=C.muted,
                    stroke_width=1.2).move_to([float(mx(10 ** 4)), float(my((IR0 + IR1) / 2)), 0])
    ieg = tex(r"e^{\gamma}\approx1.781", size=24, color=C.bound)
    ieg.move_to([IX1 - 0.15 - ieg.width / 2, float(iy(EG)) + 0.25, 0])
    zin = T.rb_5040 - 0.6
    w.play(Create(src), FadeIn(frame), Create(iline), FadeIn(iticks), FadeIn(ieg), at=zin, dur=0.5, lead=0)
    w.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in zoomed], lag_ratio=0.05), at=zin + 0.3, dur=0.8, lead=0)
    k5040 = Dot([float(ix(5040)), float(iy(r[n == 5040][0])), 0], radius=0.05)
    tag = VGroup(tex(r"n=5040", size=28, color=C.rogue), tex(r"\sigma=19{,}344", size=24, color=C.muted))
    tag.arrange(DOWN, buff=0.08, aligned_edge=LEFT).next_to(k5040, UR, buff=0.12)
    ring5 = Circle(radius=0.14, color=C.rogue, stroke_width=2.2).move_to(k5040)
    h.play(Create(ring5), FadeIn(tag), at=T.rb_5040 + 0.4, dur=0.5)
    after = lab("every n after it: below", 22, C.muted)
    after.move_to([IX1 - 0.15 - after.width / 2, float(iy(EG)) - 0.3, 0])
    h.play(FadeIn(after), at=T.rb_5040 + 1.2, dur=0.5)
    noz = lab("no zeta", 26, C.muted).next_to(st, DOWN, buff=0.12, aligned_edge=RIGHT)
    h.play(FadeIn(noz), at=T.rb_nozeta, dur=0.5)

    # ── the proof joined to a Robin formalization: being checked ──
    ch = chip("proof + Robin formalization: being checked", C.lean, mark=ring(False))
    ch.move_to([IX1 - ch.width / 2, 1.3, 0])
    h.play(FadeIn(ch, shift=0.06 * UP), at=T.rb_joined, dur=0.5)
    card2 = buzzard_card(robin=True)
    bz.play(FadeOut(card), FadeIn(card2), at=T.rb_combo, dur=0.6)
