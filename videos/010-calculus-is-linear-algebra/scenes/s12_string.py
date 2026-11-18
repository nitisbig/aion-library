"""Ch6: a guitar string is an eigenvector problem. A pinned string bent into a bump is pulled back hardest where it
bends most: the pull is the second derivative (arrows from the real second difference). Sample it at 200 points;
each row of the second-derivative matrix reads (u_{k-1} - 2u_k + u_{k+1}) / h^2: a band of 1, -2, 1, ends pinned."""
from aion import *

from beats import T
from shots import chapter_header, Mat, arrow, backdrop, finish, pt, tex

SY, X0, XL = 1.7, -4.6, 9.2                              # the string: height, left pin x, length (x in [0, 1])
N = 200
AMP = 0.9


def bump(x):
    """The bent string: a bump left of centre, zero at both pins."""
    return np.sin(np.pi * x) * np.exp(-((x - 0.4) / 0.16) ** 2)


def wpt(x, u):
    return np.array([X0 + XL * x, SY + AMP * u, 0.0])


def string_mob(f, op=1.0, n=300):
    xs = np.linspace(0, 1, n)
    return VMobject(stroke_color=C.string, stroke_width=C.stroke, stroke_opacity=op).set_points_as_corners(
        [wpt(x, f(x)) for x in xs])


def pins():
    return VGroup(*[Dot(wpt(x, 0), radius=0.08, color=C.string) for x in (0, 1)])


def second_diff(n=N):
    """The n x n matrix of u'' on n interior points of [0, 1], ends pinned at zero: (1, -2, 1) / h^2."""
    h = 1 / (n + 1)
    return (np.diag(-2 * np.ones(n)) + np.diag(np.ones(n - 1), 1) + np.diag(np.ones(n - 1), -1)) / h ** 2


XS = np.arange(1, N + 1) / (N + 1)
U2 = second_diff() @ bump(XS)                            # the pull, from the matrix itself
assert np.count_nonzero(second_diff()) == 3 * N - 2


@scene(T.cut_ch6, T.cut_modes)
def s12_string(s):
    backdrop(s)
    m = s.manim(z=1)
    chapter_header(m, 6, T.cut_ch6)                     # chapter badge row + title (fills the cut)

    # ── a string, pinned at both ends ──
    flat = string_mob(lambda x: 0 * x)
    pn = pins()
    m.play(Create(flat), FadeIn(pn), at=T.hear + 0.2, dur=1.0)
    m.play(*[Indicate(d, color=C.string, scale_factor=1.8) for d in pn], at=T.pinned + 0.6, dur=0.7)

    # ── bend it: it's pulled back hardest where it bends most ──
    bent = string_mob(bump)
    m.play(Transform(flat, bent), at=T.bends - 0.2, dur=1.0, ease="easy_ease")
    idx = np.linspace(8, N - 9, 19).astype(int)
    sc = 0.85 / np.max(np.abs(U2))
    pulls = VGroup(*[arrow(wpt(XS[i], bump(XS[i])), wpt(XS[i], bump(XS[i])) + np.array([0, sc * U2[i], 0]), C.op,
                           width=C.stroke, tip=0.16) for i in idx if abs(sc * U2[i]) > 0.12])
    m.play(LaggedStart(*[GrowArrow(a) for a in pulls], lag_ratio=0.06), at=T.bends + 1.2, dur=1.4)
    lab = tex(r"\text{pull}", r"\;\propto\;", r"u''", size=48, colors={0: C.op, 2: C.op}).move_to([4.6, 3.2, 0])
    m.play(FadeIn(lab, shift=0.1 * DOWN), at=T.second_deriv - 0.2, dur=0.6)

    # ── 200 points along it ──
    tb = T.build
    m.play(FadeOut(pulls), at=tb, dur=0.5)
    dots = VGroup(*[Dot(wpt(x, bump(x)), radius=0.03, color=C.fn) for x in XS])
    m.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.004), at=T.two_hundred - 0.3, dur=1.2)
    n200 = tex(r"N", r"=", r"200", size=40, colors={0: C.fn}).move_to([-4.6, 3.2, 0])
    m.play(FadeIn(n200), at=T.two_hundred + 0.2, dur=0.5)

    # ── one row: a point's two neighbours, minus twice itself ──
    tn = T.neighbors
    k = 46                                                # a point on the bump's left flank
    hl = VGroup(*[Circle(radius=0.11, stroke_color=C.op, stroke_width=C.thin).move_to(dots[k + d]) for d in (-1, 0, 1)])
    IC = np.array([-4.0, -1.1, 0])                       # the close-up, lower left
    big = VGroup(*[Dot(IC + np.array([1.3 * d, 0.3 * d, 0]), radius=0.11, color=C.fn) for d in (-1, 0, 1)])
    names = VGroup(*[tex(nm, size=38, color=C.fn).next_to(b, UP, buff=0.18) for nm, b in
                     zip((r"u_{k-1}", r"u_k", r"u_{k+1}"), big)])
    m.play(Create(hl), at=tn - 0.2, dur=0.5)
    m.play(*[TransformFromCopy(dots[k + d], b) for d, b in zip((-1, 0, 1), big)], FadeIn(names), at=tn + 0.4, dur=0.9)
    row = tex(r"u_{k-1}", r"-", r"2", r"u_k", r"+", r"u_{k+1}", size=46,
              colors={0: C.fn, 2: C.op, 3: C.fn, 5: C.fn}).move_to(IC + np.array([0, -1.4, 0]))
    m.play(Write(row), at=tn + 1.5, dur=1.0)
    zoomf = Rectangle(width=4.1, height=3.1, stroke_color=C.frame, stroke_width=C.thin).move_to(IC + np.array([0, -0.55, 0]))
    m.play(Create(zoomf), at=tn + 0.2, dur=0.6)

    # ── written for every point: the band 1, −2, 1 ──
    D8 = np.rint(second_diff(8) / (9 ** 2)).astype(int)
    M = Mat(D8, colors=C.faint, size=26, h_buff=0.52, v_buff=0.4).move_to([3.5, -1.5, 0])
    band = VGroup(*[M.cell(i, j) for i in range(8) for j in range(8) if abs(i - j) <= 1])
    zeros = VGroup(*[M.cell(i, j) for i in range(8) for j in range(8) if abs(i - j) > 1])
    band.set_color(C.op)
    oh = tex(r"\frac{1}{h^2}", size=40, color=C.op).next_to(M, LEFT, buff=0.2)
    to = T.one_m2_one
    m.play(FadeIn(M.br), FadeIn(oh), at=to - 0.6, dur=0.5)
    m.play(LaggedStart(*[FadeIn(c, scale=0.7) for c in band], lag_ratio=0.04), Indicate(row[2], color=C.op),
           at=to, dur=1.2)
    m.play(FadeIn(zeros), at=to + 1.2, dur=0.5)

    # ── pin both ends at zero ──
    tp = T.pin_ends
    ends = VGroup(M.cell(0, 0), M.cell(7, 7))
    m.play(*[Indicate(e, color=C.string, scale_factor=1.5) for e in ends], *[Indicate(d, color=C.string, scale_factor=1.8) for d in pn],
           at=tp + 0.2, dur=0.8)
    m.play(FadeOut(VGroup(hl, big, names, row, lab, n200, dots, zoomf)), at=T.cut_modes - 0.6, dur=0.5)
    finish(s)
