"""s24 spacing (P43): a famous speculation, labeled as one. The first zeros as a stack of levels (left); the gaps between
neighbors; a histogram of the normalized gaps of all 5,002 zeros up to height 5450 (assets/spacing.npz, bake.py) rises
to meet the GUE prediction, drawn dashed (Gaudin's spacing law, computed from the sine-kernel determinant). Montgomery
1973, Dyson. Energy levels on the right: eigenvalues of a seeded random Hermitian (GUE) matrix, the model physicists use
for heavy nuclei. gamma_n =? E_n (a hidden system?), tagged speculation; RH would not imply it. Ends on black (CH7 card)."""
from aion import *

from beats import T
from media_assets import portrait_card
from look import ASSETS, EASE, caps, lab, live, pin, seen, tex

D = np.load(ASSETS / "spacing.npz")
HX0, HX1, HY0, HK = -3.9, 3.9, -2.55, 3.9       # histogram: left, right (s = 0..3), base, units per unit density
SMAX = 3.0
BW = 0.15                                        # bin width
COL_Y0, COL_Y1 = -2.75, 2.15                     # the two level stacks
ZXC, EXC = -5.75, 5.75
NL = 24


def sx(v):
    return HX0 + (HX1 - HX0) * np.asarray(v, float) / SMAX


def hist():
    h, e = np.histogram(D["gaps"], bins=int(round(SMAX / BW)), range=(0, SMAX), density=True)
    return h, e


def bars(u):
    h, e = hist()
    g = VGroup()
    for k, v in enumerate(h):
        ht = max(1e-3, u * v * HK)
        g.add(Rectangle(width=float(sx(e[k + 1]) - sx(e[k])), height=ht, stroke_color=C.zero, stroke_width=1.2,
                        fill_color=C.zero, fill_opacity=seen(0.45)).move_to([float(sx((e[k] + e[k + 1]) / 2)),
                                                                             HY0 + ht / 2, 0]))
    return g


def levels(ys, x, color, opacity=1.0):
    return VGroup(*[Line([x - 0.38, y, 0], [x + 0.38, y, 0], color=color, stroke_width=2.4, stroke_opacity=opacity)
                    for y in ys])


def stack_y(v):
    v = np.asarray(v, float)
    return COL_Y0 + (COL_Y1 - COL_Y0) * (v - v[0]) / (v[-1] - v[0])


def gue_levels(n=240, seed=1973):
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    ev = np.linalg.eigvalsh((a + a.conj().T) / 2)
    mid = ev[n // 2 - NL // 2: n // 2 + NL // 2]          # the middle of the spectrum, where the density is flat
    return mid


@scene(T.cut_spacing, T.cut_august)
def s24_spacing(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_august - 0.5, T.cut_august - 0.05)
    fade = keys((bye[0], 1.0), (bye[1], 0.0), lead=0)
    w = s.manim(z=2, parallax=0.0, opacity=fade)
    h = s.manim(z=6, parallax=0.0, opacity=fade)

    # ── the zeros as a stack of levels ──
    g = D["gammas"][:NL]
    zy = stack_y(g)
    zs = levels(zy, ZXC, C.zero)
    w.play(LaggedStart(*[Create(l) for l in zs], lag_ratio=0.15), at=T.r_ideas + 0.3, dur=1.4)
    zl = lab("zeros", 28, C.zero).move_to([ZXC, COL_Y0 - 0.45, 0])
    h.play(FadeIn(zl), at=T.r_ideas + 0.9, dur=0.5)

    who = VGroup(caps(r"H. Montgomery $\cdot$ 1973", 32, C.ink), caps(r"F. Dyson", 32, C.ink)).arrange(RIGHT, buff=0.6)
    pin(who, top=3.6, left=-6.3)
    h.play(FadeIn(who[0], shift=0.06 * DOWN), at=T.r_hugh, dur=0.5)
    h.play(FadeIn(who[1], shift=0.06 * DOWN), at=T.r_dyson, dur=0.5)
    portrait_card(s, h, "montgomery", None, T.r_hugh, T.r_spec, (who.get_right()[0] + 0.85, 2.9), height=1.3)
    portrait_card(s, h, "dyson", None, T.r_dyson, T.r_spec, (who.get_right()[0] + 2.0, 2.9), height=1.3)

    # ── the gaps between neighbors ──
    gaps = VGroup()
    for k in (3, 4, 5):
        a, b = zy[k], zy[k + 1]
        gaps.add(VGroup(Line([ZXC + 0.52, a, 0], [ZXC + 0.52, b, 0], color=C.text, stroke_width=2.2),
                        Line([ZXC + 0.44, a, 0], [ZXC + 0.6, a, 0], color=C.text, stroke_width=2.2),
                        Line([ZXC + 0.44, b, 0], [ZXC + 0.6, b, 0], color=C.text, stroke_width=2.2)))
    w.play(LaggedStart(*[Create(x) for x in gaps], lag_ratio=0.3), at=T.r_gaps + 0.4, dur=0.9)

    # ── the histogram of all 5,002 gaps rises ──
    axis = Line([HX0 - 0.1, HY0, 0], [HX1 + 0.1, HY0, 0], color=C.muted, stroke_width=2)
    ticks = VGroup(*[tex(str(k), size=26, color=C.muted).move_to([float(sx(k)), HY0 - 0.3, 0]) for k in range(4)])
    cap = lab("gap / average gap", 24, C.muted).move_to([0, HY0 - 0.72, 0])
    n = lab(f"{len(D['gammas']):,} zeros", 26, C.zero)
    n.move_to([HX0 + n.width / 2, 1.85, 0])
    w.play(Create(axis), FadeIn(ticks), FadeIn(cap), at=T.r_gaps + 0.6, dur=0.6, lead=0)
    rise = keys((T.r_gaps + 1.0, 0.0), (T.r_gaps + 3.0, 1.0, EASE), lead=0)
    live(w, lambda t: bars(float(rise(t))), (T.r_gaps + 1.0, T.r_gaps + 3.0))
    h.play(FadeIn(n), at=T.r_gaps + 1.6, dur=0.5, lead=0)

    # ── the same statistics: the GUE law, dashed (a conjecture) ──
    pts = [[float(sx(a)), HY0 + b * HK, 0] for a, b in zip(D["s"], D["p"]) if a <= SMAX]
    curve = VMobject(stroke_color=C.text, stroke_width=3.2).set_points_smoothly(pts)
    dashed = DashedVMobject(curve, num_dashes=60, dashed_ratio=0.55)
    w.play(Create(dashed), at=T.r_same, dur=1.0)
    gue = VGroup(tex(r"\text{GUE}", size=34), lab("random matrices", 24, C.muted)).arrange(DOWN, buff=0.12,
                                                                                         aligned_edge=LEFT)
    gue.move_to([float(sx(2.05)) + gue.width / 2, HY0 + float(np.interp(1.8, D["s"], D["p"])) * HK + 0.45, 0])
    h.play(FadeIn(gue), at=T.r_same + 0.6, dur=0.5)

    # ── energy levels in heavy nuclei (a random Hermitian matrix, seeded) ──
    ey = stack_y(gue_levels())
    es = levels(ey, EXC, C.text, opacity=0.7)
    w.play(LaggedStart(*[Create(l) for l in es], lag_ratio=0.15), at=T.r_energy - 0.2, dur=1.4)
    el = VGroup(lab("energy levels", 28, C.text), lab("heavy nuclei", 22, C.muted)).arrange(DOWN, buff=0.1)
    el.move_to([EXC - 0.1, COL_Y0 - 0.6, 0])
    h.play(FadeIn(el), at=T.r_energy + 0.3, dur=0.5)

    # ── a hint of a hidden system: speculation; a proof of RH wouldn't settle it ──
    hid = tex(r"\gamma_n", r"\overset{?}{=}", r"E_n", size=44, colors={0: C.zero})
    hid.move_to([3.3, 3.3, 0])
    h.play(FadeIn(hid, shift=0.06 * DOWN), at=T.r_hint, dur=0.6)
    t = lab("speculation", 26, C.conj)
    tag = VGroup(SurroundingRectangle(t, buff=0.1, corner_radius=0.06, stroke_color=C.conj, stroke_width=1.6), t)
    tag.next_to(hid, RIGHT, buff=0.5)
    h.play(FadeIn(tag, scale=0.95), at=T.r_spec, dur=0.5)
    nimp = tex(r"\text{RH}\ \not\Rightarrow\ \text{GUE}", size=34, color=C.muted)
    nimp.move_to([hid.get_x() + 0.5, 2.55, 0])
    h.play(FadeIn(nimp, shift=0.06 * UP), at=T.r_spec + 1.4, dur=0.5)
