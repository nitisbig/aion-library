"""in_s04 · Where it is used (L4 grid of four boards, built in turn on the narration).

1 genes: simulated genotypes across Europe (pcadata.genes); their PCA scores, rotated onto the compass (one
  rotation, Procrustes), coloured by latitude: the best shadow looks like a map. Illustrative, after Novembre 2008.
2 faces: made-up faces (not people, pcadata.faces); their four leading eigenfaces, in the diverging map.
3 images: a made-up picture rebuilt from k principal components of its 8x8 patches, k = 1, 2, 4, 8, 64.
4 rates: simulated yield curves (pcadata.yields); the curve moves along PC1 (rise together), PC2 (tilt), PC3 (bend).
On 'too many measurements' the boards dim and hold.
"""
import numpy as np
from aion import *
from manim import ManimColor, interpolate_color

from beats import T
from kit import (Glyphs, P3, board, caps, grid4, rgb255, sans, smoothstep, to_lin, to_srgb, window)


def content(box, pad=0.22, top=0.42):
    return (box[0] + pad, box[1] + pad, box[2] - pad, box[3] - top)


def fit(pts, area, keep_aspect=True):
    lo, hi = pts.min(0), pts.max(0)
    w, h = area[2] - area[0], area[3] - area[1]
    sx, sy = w / (hi[0] - lo[0]), h / (hi[1] - lo[1])
    if keep_aspect:
        sx = sy = min(sx, sy)
    c = np.array([(area[0] + area[2]) / 2, (area[1] + area[3]) / 2])
    return c + (pts - (lo + hi) / 2) * np.array([sx, sy])


def diverging(v, vmax=None):
    """Signed values → RGBA uint8 (C.data negative, black, C.spread positive), mixed in linear light."""
    vmax = vmax or np.abs(v).max()
    u = np.clip(v / vmax, -1, 1)[..., None]
    neg, pos = to_lin(np.array(rgb255(C.data)) / 255), to_lin(np.array(rgb255(C.spread)) / 255)
    rgb = to_srgb(np.where(u > 0, u * pos, -u * neg))
    return (np.dstack([rgb, np.ones(v.shape)]) * 255 + 0.5).astype(np.uint8)


def upscale(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def tiles(imgs, cols, gap=2):
    """Images (n, h, w, 4) → one RGBA mosaic with transparent gaps."""
    n, h, w = imgs.shape[:3]
    rows = (n + cols - 1) // cols
    out = np.zeros((rows * h + (rows - 1) * gap, cols * w + (cols - 1) * gap, 4), np.uint8)
    for i in range(n):
        r, c = divmod(i, cols)
        out[r * (h + gap):r * (h + gap) + h, c * (w + gap):c * (w + gap) + w] = imgs[i]
    return out


def grey_rgba(g):
    v = (np.clip(g, 0, 1) * 255 + 0.5).astype(np.uint8)
    return np.dstack([v, v, v, np.full(v.shape, 255, np.uint8)])


@scene(T.in_s04, T.in_s05)
def in_s04(s):
    import pcadata as pd
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_g, t_f, t_i = float(T.in_s04_genes), float(T.in_s04_faces), float(T.in_s04_shrinks_images)
    t_r, t_up, t_tilt, t_bend = (float(T.in_s04_interest_rates), float(T.in_s04_rise_together),
                                 float(T.in_s04_tilt), float(T.in_s04_bend))
    t_tm = float(T.in_s04_too_many_measurement)
    lead = 0.15
    vis = keys((t0, 1.0), (t_tm, 1.0), (t_tm + 0.8, 0.45), (t1 - 0.7, 0.45), (t1 - 0.1, 0.0))
    B = [grid4(i) for i in range(4)]
    m = s.manim(z=1, opacity=vis)
    for box, tag, at in zip(B, ("genes", "faces", "images", "rates"), (t_g, t_f, t_i, t_r)):
        m.play(FadeIn(board(box, tag)), at=at - 0.4, dur=0.6)

    # ---- 1 genes: the PCA of genotypes looks like a map
    home, G, Q = pd.genes()
    Z = Q.Z[:, :2]
    H = (home - home.mean(0)) / home.std(0)
    U, _, Vt = np.linalg.svd(Z.T @ H)                       # one rotation (or reflection) onto the compass
    Zr = Z @ (U @ Vt)
    a1 = content(B[0])
    area = (a1[0] + 0.5, a1[1] + 0.15, a1[2] - 0.5, a1[3] - 0.05)
    dest = fit(Zr, area)
    rng = np.random.default_rng(1610)
    src = fit(rng.normal(0, 1, Zr.shape), area)
    lat = (home[:, 1] - home[:, 1].min()) / np.ptp(home[:, 1])
    lag = rng.uniform(0, 0.8, len(Zr))[:, None]

    def gpos(t):
        f = smoothstep((t - (t_g + 0.6) - lag) / 2.2)
        return src + (dest - src) * f

    s.add(PointsLayer(gpos, values=lambda t: lat, cmap="diverging", colors=(C.spread, C.probe, C.data), vmin=0,
                      vmax=1, size=4.5, glow=0.0, additive=False, z=1, opacity=vis * fade(t_g, dur=0.6),
                      start=t_g - 0.4))
    cred = caps("after Novembre et al. 2008", 20, C.muted).move_to(P3(B[0][2] - 0.16, B[0][3] - 0.16),
                                                                    aligned_edge=UR)
    m.play(FadeIn(cred), at=t_g + 3.0, dur=0.8)

    # ---- 2 faces: made-up faces, then the eigenfaces every face is built from
    imgs, F = pd.faces()
    a2 = content(B[1])
    face_mos = tiles(np.stack([grey_rgba(upscale(imgs[i], 4)) for i in range(10)]), 5, gap=8)
    eig = np.stack([diverging(upscale(F.V[:, j].reshape(40, 40), 6)) for j in range(4)])
    eig_mos = tiles(eig, 4, gap=14)
    hf = min(a2[3] - a2[1], (a2[2] - a2[0]) * face_mos.shape[0] / face_mos.shape[1])
    he = min(a2[3] - a2[1], (a2[2] - a2[0]) * eig_mos.shape[0] / eig_mos.shape[1])
    c2 = ((a2[0] + a2[2]) / 2, (a2[1] + a2[3]) / 2)
    t_ghost = t_f + 2.6
    s.add(ArrayLayer(face_mos, height=hf, pos=c2, z=1,
                     opacity=vis * keys((t_f - 0.1, 0.0), (t_f + 0.6, 1.0), (t_ghost, 1.0), (t_ghost + 1.0, 0.0))))
    s.add(ArrayLayer(eig_mos, height=he, pos=c2, z=1.1, opacity=vis * fade(t_ghost + 0.6, dur=1.0)))

    # ---- 3 images: rebuilt from k components of its 8x8 patches
    img = pd.scene_image()
    ks = (1, 2, 4, 8, 64)
    frames = [grey_rgba(upscale(pd.patch_reconstruct(img, k), 6)) for k in ks]
    a3 = content(B[2])
    hi_ = a3[3] - a3[1]
    c3 = (a3[0] + hi_ / 2 + 0.35, (a3[1] + a3[3]) / 2)
    t_k = [t_i + 0.2 + 0.9 * j for j in range(len(ks))]

    def kidx(t):
        return max(0, sum(1 for tk in t_k if t >= tk) - 1)

    s.add(FramesLayer(lambda t: frames[kidx(t)], height=hi_, pos=c3, z=1, opacity=vis * fade(t_i, dur=0.6),
                      during=[(t_i - 0.4, t_k[-1] + 0.1)]))
    kg = Glyphs([f"k = {k}" for k in ks], size=40, sans_=False)
    kx = c3[0] + hi_ / 2 + 0.9
    lab_top = s.manim(z=2, opacity=vis)

    def klabel(t):
        g = VGroup(kg(f"k = {ks[kidx(t)]}", C.pc1).move_to(P3(kx, c3[1])))
        return g

    lab_top.redraw(klabel, during=(t_i, t1))

    # ---- 4 rates: the curve moves in three ways
    Y, R = pd.yields()
    a4 = content(B[3])
    px0, px1, py0, py1 = a4[0] + 0.45, a4[0] + 0.66 * (a4[2] - a4[0]), a4[1] + 0.35, a4[3] - 0.05
    lm = np.log(pd.MATURITIES)
    xs = px0 + (lm - lm[0]) / np.ptp(lm) * (px1 - px0)
    base = Y.mean(0)
    lo_r, hi_r = float(base.min()) - 1.4, float(base.max()) + 1.4

    def yy(r):
        return py0 + (r - lo_r) / (hi_r - lo_r) * (py1 - py0)

    axes = VGroup(Line(P3(px0, py0), P3(px1 + 0.1, py0), stroke_color=C.axis, stroke_width=2),
                  Line(P3(px0, py0), P3(px0, py1), stroke_color=C.axis, stroke_width=2))
    m.play(FadeIn(axes), at=t_r - 0.2, dur=0.6)
    modes = [R.V[:, j] / np.abs(R.V[:, j]).max() * amp for j, amp in enumerate((1.1, 1.0, 0.8))]
    cols = (C.pc1, C.pc2, C.pc3)
    t_modes = (t_up, t_tilt, t_bend)

    def env(t, k):
        a = t_modes[k] - lead
        return float(np.sin(np.pi * np.clip((t - a) / 1.3, 0, 1)))

    def curve(t):
        mix = 1 - smoothstep((t - (t_up - lead)) / 0.3) + smoothstep((t - (t_bend + 1.2)) / 0.6)
        w = [0.35 * np.sin(1.4 * t), 0.3 * np.sin(1.9 * t + 1.0), 0.3 * np.sin(2.3 * t + 2.0)]
        amps = [mix * w[k] + env(t, k) for k in range(3)]
        r = base + sum(a * v for a, v in zip(amps, modes))
        col = ManimColor(C.text)
        for k in range(3):
            col = interpolate_color(col, ManimColor(cols[k]), min(1.0, 3 * env(t, k)))
        pts = [P3(x, yy(v)) for x, v in zip(xs, r)]
        g = VGroup(VMobject(stroke_color=col, stroke_width=3.4, fill_opacity=0).set_points_smoothly(pts))
        g.add(*[Dot(p, radius=0.035, color=col) for p in pts])
        return g

    m2 = s.manim(z=2, opacity=vis * fade(t_r, dur=0.6))
    m2.redraw(curve, during=(t_r - 0.4, t1))
    ix0, iw = px1 + 0.45, a4[2] - px1 - 0.6
    for k, (v, word) in enumerate(zip(modes, ("rise", "tilt", "bend"))):
        cy_ = a4[3] - 0.35 - k * 0.78
        icon = VMobject(stroke_color=cols[k], stroke_width=2.6).set_points_smoothly(
            [P3(ix0 + (x - xs[0]) / (xs[-1] - xs[0]) * iw, cy_ + 0.2 * vv) for x, vv in zip(xs, v)])
        icon.set_fill(opacity=0).set_stroke(opacity=0.3)
        m.play(FadeIn(icon), at=t_r + 0.5, dur=0.6)
        m.play(icon.animate.set_stroke(opacity=1.0), at=t_modes[k], dur=0.4)
