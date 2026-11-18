"""Ch6 (cont.): the eigenvectors of the 200 x 200 second-difference matrix are the string's modes: one arch, two,
three, sin(kπx) with eigenvalues ≈ −(kπ)^2 (computed here, never typed). Each mode vibrates in place at a speed ∝ k.
A pluck (a triangle at x = 0.2) is a mix of modes, each ringing at its own speed: the note and its overtones."""
from aion import *

from beats import T
from shots import Mat, backdrop, finish, pt, tex

E = "easy_ease"
N = 200
H = 1 / (N + 1)
XS = np.arange(1, N + 1) / (N + 1)
L2 = (np.diag(-2 * np.ones(N)) + np.diag(np.ones(N - 1), 1) + np.diag(np.ones(N - 1), -1)) / H ** 2
LAM, VEC = np.linalg.eigh(L2)
order = np.argsort(-LAM)                                  # least negative first: mode 1, 2, 3, ...
LAM, VEC = LAM[order], VEC[:, order]
for k in range(12):                                       # sign: first lobe up
    if VEC[np.argmax(np.abs(VEC[:, k]) > 1e-3 * np.abs(VEC[:, k]).max()), k] < 0:
        VEC[:, k] *= -1
for k in range(3):
    assert abs(LAM[k] + ((k + 1) * np.pi) ** 2) / ((k + 1) * np.pi) ** 2 < 2e-4
    shape = VEC[:, k] / np.abs(VEC[:, k]).max()
    assert np.allclose(shape, np.sin((k + 1) * np.pi * XS) / np.abs(np.sin((k + 1) * np.pi * XS)).max(), atol=2e-3)

PLUCK_AT = 0.2
U0 = np.where(XS < PLUCK_AT, XS / PLUCK_AT, (1 - XS) / (1 - PLUCK_AT))
CK = VEC[:, :12].T @ U0                                    # the pluck's amount of each mode
assert np.max(np.abs(VEC[:, :12] @ CK - U0)) < 0.06      # 12 modes rebuild the triangle closely

MX0, MXL = -5.6, 7.2                                     # the stacked modes: left pin x, length
MY = [2.25, 0.45, -1.35]
MAMP = 0.6
SY, SAMP = -3.05, 0.55                                   # the plucked string, bottom
W1 = 2 * np.pi * 0.55                                    # mode 1's on-screen angular speed (rad/s); mode k: k W1


def wpt(x, y0, amp, u):
    return np.array([MX0 + MXL * x, y0 + amp * u, 0.0])


def curve(u, y0, amp, color, op=1.0, width=None):
    xs = np.concatenate([[0], XS, [1]])
    us = np.concatenate([[0], u, [0]])
    return VMobject(stroke_color=color, stroke_width=width or C.stroke, stroke_opacity=op).set_points_as_corners(
        [wpt(x, y0, amp, v) for x, v in zip(xs, us)])


def mode(k):
    v = VEC[:, k]
    return v / np.abs(v).max()


def band_image(n=N, px=600, thick=4):
    img = np.zeros((px, px, 4), np.uint8)
    col = np.array(color_to_rgb(C.op)) * 255
    i = np.arange(px)
    for d in range(-thick * 2, thick * 2 + 1):
        j = i + d
        ok = (j >= 0) & (j < px)
        img[i[ok], j[ok], :3] = col
        img[i[ok], j[ok], 3] = 255
    return img


@scene(T.cut_modes, T.cut_ch7)
def s13_modes(s):
    backdrop(s)
    m = s.manim(z=1)
    t0 = T.cut_modes

    # what s12 left: the bent string, its pins, the 8 x 8 band (same geometry as s12)
    SY12, X012, XL12, A12 = 1.7, -4.6, 9.2, 0.9
    bump = lambda x: np.sin(np.pi * x) * np.exp(-((x - 0.4) / 0.16) ** 2)       # noqa: E731
    xs = np.linspace(0, 1, 300)
    s12 = VMobject(stroke_color=C.string, stroke_width=C.stroke).set_points_as_corners(
        [[X012 + XL12 * x, SY12 + A12 * bump(x), 0] for x in xs])
    pins12 = VGroup(*[Dot([X012 + XL12 * x, SY12, 0], radius=0.08, color=C.string) for x in (0, 1)])
    D8 = (np.diag(-2 * np.ones(8)) + np.diag(np.ones(7), 1) + np.diag(np.ones(7), -1)).astype(int)
    M = Mat(D8, colors=C.faint, size=26, h_buff=0.52, v_buff=0.4).move_to([3.5, -1.5, 0])
    for i in range(8):
        for j in range(8):
            if abs(i - j) <= 1:
                M.cell(i, j).set_color(C.op)
    oh = tex(r"\frac{1}{h^2}", size=40, color=C.op).next_to(M, LEFT, buff=0.2)
    m.add(s12, pins12, M, oh, at=t0)

    # ── ask the computer: the full 200 x 200 band ──
    ta = T.ask_computer
    BC, BS = np.array([0.0, -0.4, 0]), 4.4
    m.play(FadeOut(VGroup(s12, pins12)), VGroup(M, oh).animate.move_to(BC), at=ta - 0.3, dur=0.9, ease=E)
    m.play(FadeOut(VGroup(M, oh)), at=ta + 0.6, dur=0.6)
    frame = Square(BS, stroke_color=C.frame, stroke_width=C.thin).move_to(BC)
    bop = keys((ta + 0.6, 0.0), (ta + 1.3, 1.0), (T.arch1 - 0.6, 1.0), (T.arch1 + 0.1, 0.0), lead=0)
    s.add(ArrayLayer(band_image(), height=BS, z=0.5, pos=lambda t: (float(BC[0]), float(BC[1])),
                     opacity=lambda t: float(bop(t)), start=ta + 0.5, end=T.arch1 + 0.2))
    size = tex(r"200 \times 200", size=38).next_to(frame, DOWN, buff=0.2)
    m.play(FadeIn(frame), FadeIn(size), at=ta + 0.6, dur=0.7)
    eq = tex(r"D^2", r"v", r"=", r"\lambda", r"v", size=56, colors={0: C.op, 1: C.eigen, 3: C.eigen, 4: C.eigen})
    eq.move_to([0, 2.8, 0])
    m.play(FadeIn(eq, shift=0.1 * DOWN), at=T.eigvecs + 0.3, dur=0.7)

    # ── out come these: one arch, two, three ──
    m.play(FadeOut(VGroup(frame, size)), eq.animate.move_to([4.5, 3.2, 0]), at=T.out_come + 0.2, dur=0.7)
    stat = [curve(mode(k), MY[k], MAMP, C.eigen) for k in range(3)]
    mpins = VGroup(*[Dot(wpt(x, MY[k], MAMP, 0), radius=0.05, color=C.muted) for k in range(3) for x in (0, 1)])
    m.play(FadeIn(mpins), at=T.arch1 - 0.3, dur=0.4)
    for k, tk in enumerate((T.arch1, T.arch2, T.arch3)):
        m.play(Create(stat[k]), at=tk - 0.1, dur=0.6)

    # ── smooth sine waves: sin(kπx), nobody typed one in ──
    sines = VGroup(*[DashedVMobject(curve(np.sin((k + 1) * np.pi * XS), MY[k], MAMP, C.text, width=C.thin * 1.4),
                                    num_dashes=60) for k in range(3)])
    sl = VGroup(*[tex(rf"\sin({'' if k == 0 else k + 1}\pi x)", size=32, color=C.muted).next_to(
        wpt(1, MY[k], MAMP, 0), RIGHT, buff=0.25) for k in range(3)])
    m.play(LaggedStart(*[Create(c) for c in sines], lag_ratio=0.2), FadeIn(sl), at=T.sine_waves + 0.4, dur=1.4)
    m.play(Indicate(VGroup(*stat), color=C.eigen, scale_factor=1.03), at=T.nobody + 0.4, dur=1.0)

    # ── their eigenvalues match −(kπ)² ──
    m.play(FadeOut(VGroup(sines, sl)), at=T.eigvals - 0.5, dur=0.4)
    lams = VGroup()
    for k in range(3):
        a = tex(rf"\lambda_{k + 1}", r"=", f"{LAM[k]:.2f}" if k else f"{LAM[k]:.3f}", size=36,
                colors={0: C.eigen}).move_to([4.3, MY[k] + 0.22, 0])
        ex = -((k + 1) * np.pi) ** 2
        b = tex(rf"-{'' if k == 0 else (k + 1) ** 2}\pi^2", r"=", f"{ex:.2f}" if k else f"{ex:.3f}", size=30,
                color=C.muted).next_to(a, DOWN, buff=0.15, aligned_edge=LEFT)
        lams.add(VGroup(a, b))
    m.play(LaggedStart(*[FadeIn(g, shift=0.1 * LEFT) for g in lams], lag_ratio=0.3), at=T.eigvals + 0.2, dur=1.4)

    # ── each mode vibrates in place; the eigenvalue sets how fast (∝ k) ──
    tv = T.vibrate + 0.3
    tp = T.pluck
    tr = tp + 1.2                                          # the pluck's release
    end = T.cut_ch7
    WK = W1 * np.sqrt(LAM[:12] / LAM[0])                   # ω_k ∝ √(−λ_k): 1 : 2 : 3 ...
    mop = keys((tp - 0.2, 1.0), (tp + 0.5, 0.35), (T.overtones, 0.35), (T.overtones + 0.6, 1.0), (end - 0.7, 1.0),
               (end - 0.1, 0.0), lead=0)
    m.remove(*stat, at=tv)

    def stack(t):
        o = float(mop(t))
        return VGroup(*[curve(mode(k) * np.cos(WK[k] * (t - tv)), MY[k], MAMP, C.eigen, op=o) for k in range(3)])
    m.redraw(stack, during=(tv, end - 0.05))
    eqw = tex(r"\omega_k", r"\propto", r"\sqrt{-\lambda_k}", size=48, colors={0: C.eigen, 2: C.eigen}).move_to([4.5, 3.2, 0])
    m.play(ReplacementTransform(eq, eqw), at=T.how_fast + 0.2, dur=0.8)
    tags = [tex(rf"\times{k + 1}", size=36, color=C.eigen).move_to([2.3, MY[k], 0]) for k in range(3)]
    for k, tk in enumerate((T.how_fast + 1.2, T.octave, T.three_fast + 0.3)):
        m.play(FadeIn(tags[k], scale=0.7), at=tk, dur=0.5)

    # ── pluck it: the shape is a mix of modes, each ringing at its own speed ──
    m.play(FadeOut(VGroup(lams, eqw, *tags)), at=tp - 0.6, dur=0.5)
    pl = keys((tp, 0.0), (tp + 0.8, 1.0, E), lead=0)
    sop = keys((tp - 0.6, 0.0), (tp - 0.2, 1.0), (end - 0.7, 1.0), (end - 0.1, 0.0), lead=0)
    U12 = VEC[:, :12] @ CK                               # the triangle as 12 modes

    def plucked(t):
        if t < tr:
            u = float(pl(t)) * U12
        else:
            u = VEC[:, :12] @ (CK * np.cos(WK * (t - tr)))
        o = float(sop(t))
        return VGroup(curve(u, SY, SAMP, C.string, op=o),
                      *[Dot(wpt(x, SY, SAMP, 0), radius=0.07, color=C.string).set_opacity(o) for x in (0, 1)])
    m.redraw(plucked, during=(tp - 0.6, end - 0.05))

    # the amount of each mode in the pluck
    BX0, BY, BH = 3.0, 0.3, 1.9
    cmax = np.abs(CK).max()
    bars = VGroup(*[Rectangle(width=0.2, height=max(abs(c) / cmax * BH, 0.02), stroke_width=0, fill_color=C.eigen,
                              fill_opacity=0.9).move_to([BX0 + 0.3 * k, BY + c / cmax * BH / 2, 0])
                    for k, c in enumerate(CK)])
    base = Line([BX0 - 0.25, BY, 0], [BX0 + 0.3 * 11 + 0.25, BY, 0], color=C.axis, stroke_width=C.thin)
    cl = tex(r"c_k", size=40, color=C.eigen).next_to(base, LEFT, buff=0.25)
    m.play(FadeIn(base), LaggedStart(*[GrowFromEdge(b, DOWN if c > 0 else UP) for b, c in zip(bars, CK)],
                                     lag_ratio=0.08), FadeIn(cl), at=tr + 0.3, dur=1.4)
    m.play(Indicate(bars, color=C.eigen, scale_factor=1.05), at=T.note + 0.3, dur=0.9)
    m.play(FadeOut(VGroup(base, bars, cl, mpins)), at=end - 0.7, dur=0.6)
    finish(s)
