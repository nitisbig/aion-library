"""Ch2: the derivative, as a matrix. Slope ≈ (next height − this height) / step; written for every sample at once,
that's a matrix with −1 on the diagonal and +1 just right of it (the corner +1 wraps around: sin is periodic), all
over h. At 1000 points: a million entries, 99.8 % zeros, one thin band. Multiply it by the sine column and the column
that comes out, plotted, is cosine (the real forward difference, error about h/2)."""
from aion import *

from beats import T
from shots import (chapter_header, cos_tracer, backdrop, bar_column, brackets, col_brackets, finish, plot, pt, samples, tex)

GO, GUX, GUY = (-6.6, -0.5), 0.74, 1.45                      # the sampled sine on the left
N8 = 8
X8 = samples(N8)
H8 = 2 * np.pi / N8
MX, MY = 3.5, 0.1                                          # the 8 x 8 matrix
IMG_H = 5.4                                                # the 1000 x 1000 picture's height (units)
N = 1000


def diff_matrix(n):
    """Forward difference on n periodic samples: (f_{k+1} − f_k) / h, the last row wrapping to f_0."""
    h = 2 * np.pi / n
    Dm = -np.eye(n) + np.roll(np.eye(n), 1, axis=1)
    return Dm / h


D1K = diff_matrix(N)
XS = samples(N)
OUT = D1K @ np.sin(XS)
ERR = np.max(np.abs(OUT - np.cos(XS)))
assert ERR < 0.0032 and np.count_nonzero(D1K) == 2 * N   # max error ≈ h/2; 2000 nonzero of 10^6 (99.8 % zero)


def band_image(n=N, thick=6):
    """The n x n matrix as a picture: black, with its nonzero entries (the band and the wrap corner) in C.op."""
    img = np.zeros((n, n, 4), np.uint8)
    col = np.array(color_to_rgb(C.op)) * 255
    i = np.arange(n)
    for d in range(-1, thick - 1):
        for j_off in (0, 1):
            jj = (i + j_off + d) % n
            ok = (i + d >= 0) & (i + d < n)
            img[i[ok], jj[ok], :3] = col
            img[i[ok], jj[ok], 3] = 255
    img[n - thick:, :thick, :3] = col                              # the wrap-around corner entry, drawn at band weight
    img[n - thick:, :thick, 3] = 255
    return img


@scene(T.cut_ch2, T.cut_poly)
def s04_band(s):
    backdrop(s)
    m = s.manim(z=1)
    chapter_header(m, 2, T.cut_ch2)                     # chapter badge row + title (fills the cut)
    t0 = T.cut_ch2

    # what s03 left: clear it
    # ── the slope at a point ≈ rise over run between neighbours ──
    axis = Line(pt(GO, 1, (-0.2, 0)), pt(GO, 1, (GUX * 2 * np.pi + 0.2, 0)), color=C.axis, stroke_width=C.thin)
    curve = plot(np.sin, 0, 2 * np.pi, GO, GUX, GUY, C.fn, opacity=0.25)
    dots = VGroup(*[Dot(pt(GO, 1, (GUX * x, GUY * np.sin(x))), radius=0.07, color=C.fn) for x in X8])
    m.play(FadeIn(axis), FadeIn(curve), LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.06),
           at=T.rise - 0.6, dur=1.0)
    k = 3                                                # a steep pair, so the rise is visible
    a, b = dots[k].get_center(), dots[k + 1].get_center()
    run = Line(a, [b[0], a[1], 0], color=C.muted, stroke_width=C.thin * 1.5)
    rise = Line([b[0], a[1], 0], b, color=C.muted, stroke_width=C.thin * 1.5)
    sec = Line(a + 0.5 * (a - b), b + 0.5 * (b - a), color=C.dfn, stroke_width=C.stroke)
    hl = tex("h", size=34, color=C.muted).next_to(run, DOWN, buff=0.12)
    m.play(Create(sec), at=T.rise + 0.4, dur=0.8)
    m.play(Create(run), Create(rise), FadeIn(hl), at=T.rise + 1.6, dur=0.8)
    quot = tex(r"\frac{f_{k+1} - f_k}{h}", size=50).move_to([-4.6, 2.7, 0])
    m.play(Write(quot), at=T.next_minus, dur=1.2)

    # ── written for every point at once: the 8 x 8 matrix ──
    D8 = np.rint(diff_matrix(N8) * H8).astype(int)
    from shots import Mat
    Mt = Mat(D8, colors=C.faint, size=32, h_buff=0.64, v_buff=0.5).move_to([MX, MY, 0])
    entries = {(i, j): Mt.cell(i, j) for i in range(N8) for j in range(N8)}
    neg = VGroup(*[entries[(i, i)] for i in range(N8)])
    pos = VGroup(*[entries[(i, (i + 1) % N8)] for i in range(N8)])
    VGroup(neg, pos).set_color(C.op)
    zeros = VGroup(*[entries[(i, j)] for i in range(N8) for j in range(N8) if j not in (i, (i + 1) % N8)])
    oneh = tex(r"\frac{1}{h}", size=44, color=C.op).next_to(Mt, LEFT, buff=0.25)
    m.play(FadeIn(Mt.br), at=T.every_point, dur=0.6)
    # one row, and the two samples it reads
    rbox = Rectangle(width=Mt.br.width - 0.25, height=0.46, stroke_color=C.dfn, stroke_width=C.thin).move_to(
        [MX, entries[(k, 0)].get_center()[1], 0])
    m.play(Create(rbox), Indicate(VGroup(dots[k], dots[k + 1]), color=C.dfn, scale_factor=1.6), at=T.row, dur=1.0)
    m.play(LaggedStart(*[FadeIn(e, scale=0.7) for e in neg], lag_ratio=0.08), at=T.minus_one, dur=1.0)
    m.play(LaggedStart(*[FadeIn(e, scale=0.7) for e in pos], lag_ratio=0.08), at=T.plus_one, dur=1.0)
    m.play(FadeIn(zeros), FadeOut(rbox), at=T.zeros, dur=0.7)
    m.play(FadeIn(oneh, shift=0.15 * RIGHT), at=T.divide, dur=0.6)

    # ── a thousand points: a million entries, one thin band ──
    tz = T.zoom_out
    corner = np.array([MX - IMG_H / 2, MY + IMG_H / 2, 0])
    small = VGroup(Mt.br, neg, pos, zeros, oneh)
    m.play(small.animate.scale(0.03).move_to(corner + np.array([0.08, -0.08, 0])), FadeOut(VGroup(sec, run, rise, hl)),
           at=tz, dur=1.4, ease="easy_ease")
    m.remove(small, at=tz + 1.5)
    img_op = keys((tz + 0.6, 0.0), (tz + 1.5, 1.0), lead=0)
    t_mv0, t_mv1 = T.multiply - 0.2, T.multiply + 1.0
    IMG_L = IMG_H * 0.8                                    # smaller in the product line
    img_x = keys((t_mv0, MX), (t_mv1, -3.4, "easy_ease"), lead=0)
    img_s = keys((t_mv0, 1.0), (t_mv1, IMG_L / IMG_H, "easy_ease"), lead=0)
    t_pl = T.plot_back
    img_out = keys((t_pl, 1.0), (t_pl + 0.6, 0.0), lead=0)
    s.add(ArrayLayer(band_image(), height=IMG_H, z=0.5, pos=lambda t: (float(img_x(t)), MY),
                     scale=lambda t: (float(img_s(t)), float(img_s(t))),
                     opacity=lambda t: float(img_op(t)) * float(img_out(t)), start=tz + 0.5, end=t_pl + 0.7))
    frame = Square(IMG_H, stroke_color=C.frame, stroke_width=C.thin).move_to([MX, MY, 0])
    m.play(FadeIn(frame), at=tz + 0.6, dur=0.8)
    size = tex(r"1000 \times 1000", size=40).next_to(frame, DOWN, buff=0.25)
    m.play(FadeIn(size), at=tz + 1.5, dur=0.6)
    zpct = tex(r"99.8\%", r"\;=0", size=40, colors={0: C.muted}).next_to(frame, LEFT, buff=0.5)
    m.play(FadeIn(zpct, shift=0.1 * RIGHT), at=T.almost_zero + 0.2, dur=0.6)
    diag = Line(corner, corner + np.array([IMG_H, -IMG_H, 0]), color=C.op, stroke_width=C.stroke + 2)
    m.play(ShowPassingFlash(diag.copy(), time_width=0.4), at=T.band, dur=1.2)

    # ── multiply: band x sine column = a new column ──
    m.play(FadeOut(VGroup(axis, curve, dots, quot, size, zpct)), at=t_mv0 - 0.3, dur=0.5)
    m.play(frame.animate.scale(IMG_L / IMG_H).move_to([-3.4, MY, 0]), at=t_mv0, dur=1.2, ease="easy_ease")
    CH = IMG_L
    sinc = VGroup(col_brackets(0.6, MY, CH, width=1.2), bar_column(np.sin(XS), 0.6, MY, height=CH, width=0.6))
    eq = tex("=", size=56).move_to([2.25, MY, 0])
    outc = bar_column(OUT, 3.9, MY, height=CH, width=0.6, color=C.dfn)
    outb = col_brackets(3.9, MY, CH, width=1.2)
    m.play(FadeIn(sinc, shift=0.8 * LEFT), at=T.feed_sin, dur=0.9)
    m.play(FadeIn(eq), FadeIn(outb), at=T.feed_sin + 1.2, dur=0.5)
    m.play(Create(outc), at=T.feed_sin + 1.5, dur=1.2)

    # ── plot it back as a curve: cosine ──
    PO, PUX, PUY = (-3.1, -0.5), 1.0, 1.35
    ax2 = Line(pt(PO, 1, (-0.2, 0)), pt(PO, 1, (PUX * 2 * np.pi + 0.2, 0)), color=C.axis, stroke_width=C.thin)
    pts = np.stack([PO[0] + PUX * XS, PO[1] + PUY * OUT, 0 * XS], -1)
    outcurve = VMobject(stroke_color=C.dfn, stroke_width=C.stroke + 1).set_points_as_corners(pts)
    m.play(FadeOut(VGroup(frame, sinc, eq, outb)), at=t_pl, dur=0.6)
    m.play(ReplacementTransform(outc, outcurve), FadeIn(ax2), at=t_pl + 0.2, dur=1.3, ease="easy_ease")
    true = DashedVMobject(plot(np.cos, 0, 2 * np.pi, PO, PUX, PUY, C.text, width=C.thin * 1.4), num_dashes=70)
    lab = tex(r"\approx", r"\cos x", size=48, colors={1: C.text}).next_to(pt(PO, 1, (PUX * 2 * np.pi, PUY)), UP,
                                                                          buff=0.1)
    m.play(Create(true), FadeIn(lab), at=T.cosine, dur=1.0)
    took = tex(r"D", r"\,\sin", r"\;\approx\;", r"\cos", size=56, colors={0: C.op, 1: C.fn, 3: C.dfn}).move_to(
        [0, 2.9, 0])
    m.play(Write(took), at=T.took + 0.3, dur=1.0)
    trop = keys((T.took + 1.4, 0.0), (T.took + 2.0, 1.0), lead=0)
    m.redraw(lambda t: cos_tracer(t, T.took + 1.4, float(trop(t))), during=(T.took + 1.4, T.cut_poly))
    finish(s)
