"""Ch7 · The picture comes apart (2/2): the photo is a matrix, so it is two rotations and a list of stretches. Each
stretch adds one layer σ u vᵀ (a column times a row); 1, 2, 3, 10, 30 layers rebuild it, and 30 layers need only
30·961 / 480² ≈ 12.5 % of the numbers. The table and the machine were never two different things."""
from functools import lru_cache

from aion import *

from beats import T
from shots import backdrop, finish, photo, photo_svd, rank_k, tex

PH = 3.3                                               # picture height on screen
PL, PR, Y = (-4.4, 0.6), (3.3, 0.6), 0.6
BAR_X0, BAR_X1, BAR_Y, BAR_H = -6.3, 6.3, -3.55, 1.45


def schedule():
    """(time, k) ticks: the first layer, the second, the third, a quick run to ten, then to thirty."""
    ticks = [(T.biggest + 0.5, 1), (T.second + 0.3, 2), (T.third - 0.3, 3)]
    ticks += [(T.ten - 0.7 + 0.1 * i, k) for i, k in enumerate(range(4, 11))]
    ticks += [(T.thirty - 0.95 + 0.05 * i, k) for i, k in enumerate(range(11, 31))]
    return ticks


TICKS = schedule()
XF = 0.35                                              # crossfade per tick


@lru_cache(maxsize=40)
def layer_img(k):
    return rank_k(k).astype(float)


@lru_cache(maxsize=1)
def residual_img():
    U, s_, Vt = photo_svd()
    r = np.abs(photo() - (U[:, :30] * s_[:30]) @ Vt[:30])
    v = np.clip(r * 5, 0, 1) * 255
    return np.dstack([v, v, v, np.full_like(v, 255)])


def k_at(t):
    k = 0
    for tt, kk in TICKS:
        if t >= tt:
            k = kk
    return k


def strip(vec, vertical):
    """A unit singular vector as a teal strip (brightness ∝ |entry|)."""
    v = np.abs(vec) / np.abs(vec).max()
    col = np.array(ManimColor(C.sigma).to_rgb()) * 255
    line = (v[:, None] * col[None, :]).astype(np.uint8)          # (480, 3)
    img = np.repeat(line[:, None, :], 24, axis=1) if vertical else np.repeat(line[None, :, :], 24, axis=0)
    return np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])


@scene(T.cut_photo_svd, T.cut_outro)
def s18_photo_svd(s):
    backdrop(s)
    end = keys((T.cut_outro - 0.7, 1.0), (T.cut_outro - 0.05, 0.0), lead=0)
    m = s.manim(z=1, opacity=end)
    g = s.manim(z=3, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    U, s_, Vt = photo_svd()

    # ── the picture, and it's a matrix too ──
    t_in = T.cut_photo_svd + 0.3
    pic = photo()
    g8 = (pic * 255).astype(np.uint8)
    s.add(ArrayLayer(np.dstack([g8, g8, g8, np.full_like(g8, 255)]), height=PH, pos=PL, z=2,
                     opacity=fade(t_in, dur=0.8, out=T.cut_outro - 0.7, out_dur=0.65)))
    frame_l = Rectangle(width=PH, height=PH, stroke_color=C.frame, stroke_width=C.thin).move_to([*PL, 0])
    m.play(FadeIn(frame_l), at=t_in, dur=0.8)
    bl = VGroup(Line([0, 0, 0], [0.18, 0, 0]), Line([0, 0, 0], [0, PH + 0.3, 0]), Line([0, PH + 0.3, 0], [0.18, PH + 0.3, 0]))
    bl.set_stroke(C.text, C.stroke)
    br = bl.copy().flip(UP)
    bl.move_to([PL[0] - PH / 2 - 0.22, Y, 0])
    br.move_to([PL[0] + PH / 2 + 0.22, Y, 0])
    m.play(FadeIn(bl, shift=0.2 * RIGHT), FadeIn(br, shift=0.2 * LEFT), at=T.matrix_too + 0.4, dur=0.6)
    usv = tex("U", r"\Sigma", r"V^{\top}", size=52, colors={1: C.sigma}).next_to(br, RIGHT, buff=0.35).shift(0.9 * UP)
    hud.play(FadeIn(usv[0]), FadeIn(usv[2]), at=T.two_rot + 0.2, dur=0.5)
    hud.play(FadeIn(usv[1]), at=T.two_rot + 1.4, dur=0.5)

    # the stretches, biggest to smallest (log height), along the bottom
    n = len(s_)
    fl = s_[0] * 1e-4
    hgt = np.clip((np.log10(np.maximum(s_, fl)) - np.log10(fl)) / (np.log10(s_[0]) - np.log10(fl)), 0.01, 1) * BAR_H
    xs = np.linspace(BAR_X0, BAR_X1, n)

    def bars(k, color, op=1.0):
        return VGroup(*[Line([xs[i], BAR_Y, 0], [xs[i], BAR_Y + hgt[i], 0], color=color, stroke_width=1.6,
                             stroke_opacity=op) for i in range(k)])
    base = bars(n, C.muted, 0.55)
    sig_l = tex(r"\sigma", size=44, color=C.sigma).move_to([BAR_X0 - 0.35, BAR_Y + 0.45, 0])
    g.play(Create(base, lag_ratio=0.002), at=T.two_rot + 1.4, dur=1.4)
    g.play(FadeIn(sig_l), at=T.two_rot + 1.6, dur=0.5)
    g.redraw(lambda t: bars(k_at(t), C.sigma), during=(TICKS[0][0] - 0.01, TICKS[-1][0] + 0.01))

    # ── one layer: a column times a row ──
    cv = Rectangle(width=PH, height=PH, stroke_color=C.frame, stroke_width=C.thin).move_to([*PR, 0])
    m.play(FadeIn(cv), at=T.layer1 + 0.3, dur=0.6)
    u1, v1 = U[:, 0], Vt[0]
    col_pos = (PR[0] - PH / 2 - 0.3, Y)
    row_pos = (PR[0], Y + PH / 2 + 0.3)
    st_op_c = fade(T.col_row + 0.6, dur=0.6, out=T.second - 0.4, out_dur=0.5)
    st_op_r = fade(T.col_row + 1.9, dur=0.6, out=T.second - 0.4, out_dur=0.5)
    s.add(ArrayLayer(strip(u1, True), height=PH, pos=col_pos, z=2, opacity=st_op_c))
    s.add(ArrayLayer(strip(v1, False), height=PH * 24 / 480, pos=row_pos, z=2, opacity=st_op_r))
    lay = tex(r"\sigma_1", r"\mathbf{u}_1", r"\mathbf{v}_1^{\top}", size=48, color=C.sigma)
    lay.move_to([PR[0] - PH / 2 - 1.15, Y + PH / 2 + 0.3, 0])
    hud.play(FadeIn(lay), at=T.col_row + 1.0, dur=0.6)
    hud.play(FadeOut(lay), at=T.second - 0.4, dur=0.5)

    # the canvas: layers add up (each tick a short crossfade); then the leftovers flash
    res_w = keys((T.noise + 0.3, 0.0), (T.noise + 0.8, 0.7), (T.noise + 2.2, 0.7), (T.noise + 2.9, 0.0), lead=0)

    def canvas(t):
        k = k_at(t)
        img = layer_img(k)
        for tt, kk in TICKS:
            if tt <= t < tt + XF:
                w = (t - tt) / XF
                img = (1 - w) * layer_img(kk - 1 if kk > 1 else 0) + w * layer_img(kk)
        r = res_w(t)
        if r > 0:
            img = (1 - r) * img + r * residual_img()
        return np.clip(img, 0, 255).astype(np.uint8)
    wins = [(tt, tt + XF) for tt, _ in TICKS] + [(T.noise + 0.3, T.noise + 2.9)]
    s.add(FramesLayer(canvas, height=PH, pos=PR, z=2, during=wins, start=TICKS[0][0] - 0.05,
                      opacity=fade(TICKS[0][0] - 0.05, dur=0.1, out=T.cut_outro - 0.7, out_dur=0.65)))
    kval = tex("k", "=", "1", size=44).move_to([PR[0], Y - PH / 2 - 0.4, 0])
    hud.play(FadeIn(kval), at=TICKS[0][0], dur=0.4)
    shown = kval
    for tt, kk in TICKS[1:]:
        if kk in (2, 3, 10, 30):
            nxt = tex("k", "=", str(kk), size=44).move_to(kval)
            hud.play(FadeOut(shown), FadeIn(nxt), at=tt, dur=0.3 if kk in (2, 3) else 0.2)
            shown = nxt

    # about an eighth of the numbers
    frac = tex(r"\frac{30 \cdot 961}{480^2}", r"\approx", r"12.5\%", size=40)
    frac.move_to([-0.45, -1.62, 0])
    assert abs(30 * 961 / 480 ** 2 - 0.125) < 0.001
    hud.play(FadeIn(frac, shift=0.1 * UP), at=T.eighth + 0.2, dur=0.7)

    # ── never two different things: the picture is a move ──
    hud.play(FadeOut(frac), FadeOut(usv), at=T.never_two - 0.3, dur=0.5)
    ell = Ellipse(width=1.9, height=0.62, color=C.sigma, stroke_width=C.stroke).rotate(np.radians(30))
    axes = VGroup(Line(ell.get_center() + 0.95 * np.array([np.cos(0.52), np.sin(0.52), 0]),
                       ell.get_center() - 0.95 * np.array([np.cos(0.52), np.sin(0.52), 0])),
                  Line(ell.get_center() + 0.31 * np.array([-np.sin(0.52), np.cos(0.52), 0]),
                       ell.get_center() - 0.31 * np.array([-np.sin(0.52), np.cos(0.52), 0]))).set_stroke(C.sigma, 2.5)
    icon = VGroup(ell, axes).move_to([-0.55, Y, 0])
    eqs = tex("=", size=72).move_to([-2.0, Y, 0])
    g.play(FadeIn(eqs), at=T.never_two + 0.6, dur=0.5)
    g.play(Create(ell), Create(axes), at=T.never_two + 0.8, dur=0.9)
    g.play(Indicate(icon, color=C.sigma, scale_factor=1.15), at=T.is_move + 0.5, dur=0.8)
    finish(s)
