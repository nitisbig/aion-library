"""ch6_s02 · Curved data (L2, rail: B_recipe, B_scree).

A sheet of 1,500 points rolled into a spiral (coloured along the roll, cyan to pink), seen end-on, then tipped to
show its length. On 'squashes the layers' the view turns to PCA's best flat shadow (looking along PC3): the turns of
the roll land on top of each other and the colours mix. On 'far apart' two points from opposite ends of the sheet
that land side by side are ringed. On 'follow the curve' the roll unrolls into a flat band, colours in order, and
the two ringed points end up far apart; on 'kernel PCA' the names of the curve-following methods.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import CEN0, P3, STAGE_L2, board, rail_recipe, rail_scree, sans, slerp, smoothstep

K = 0.52
NB = 8


def rx(a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])


def ry(a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])


def proper(R):
    R = np.array(R, float)
    if np.linalg.det(R) < 0:
        R[2] *= -1
    return R


@scene(T.ch6_s02, T.ch6_s03)
def ch6_s02(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_flat, t_sp, t_sq = float(T.ch6_s02_flat_views), float(T.ch6_s02_spiral), float(T.ch6_s02_squashes_the_layers)
    t_far, t_curve, t_kp = float(T.ch6_s02_far_apart), float(T.ch6_s02_follow_the_curve), float(T.ch6_s02_kernel_pca)
    X, tt = pd.swiss_roll()
    Q = pd.pca(X)
    Xc = Q.Xc
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))

    st = s.manim(z=0)
    st.add(board(STAGE_L2), rail_recipe(), rail_scree())

    # ---- views: end-on, tipped, then PCA's flat shadow (screen = PC2, PC1; depth = PC3)
    R_end = proper([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    R_tip = rx(math.radians(-22)) @ ry(math.radians(48)) @ R_end
    R_pca = proper(np.stack([Q.V[:, 1], Q.V[:, 0], Q.V[:, 2]]))
    tip = keys((t0, 0.0), (t_sp + 0.9, 0.0), (t_sq - 0.6, 1.0))
    sq = keys((t0, 0.0), (t_sq - 0.3, 0.0), (t_sq + 2.0, 1.0))
    unroll = keys((t0, 0.0), (t_curve - 0.2, 0.0), (t_curve + 2.4, 1.0))
    U = np.c_[6.2 * (tt - 0.5), K * (X[:, 1] - X[:, 1].mean())]

    def pos_all(t):
        R = slerp(R_end, R_tip, float(smoothstep(min(max(tip(t), 0.0), 1.0))))
        R = slerp(R, R_pca, float(smoothstep(min(max(sq(t), 0.0), 1.0))))
        P = K * (Xc @ R.T)[:, :2]
        u = float(smoothstep(min(max(unroll(t), 0.0), 1.0)))
        return CEN0 + (1 - u) * P + u * U

    cache = {"t": None}

    def pos(t):
        if cache["t"] != t:
            cache.update(t=t, p=pos_all(t))
        return cache["p"]

    on = keys((t0, 0.0), (t_sp - 0.6, 0.0), (t_sp + 0.4, 1.0))
    bins = np.minimum((tt * NB).astype(int), NB - 1)
    for b in range(NB):
        idx = np.where(bins == b)[0]
        col = interpolate_color(ManimColor(C.d5), ManimColor(C.d9), b / (NB - 1)).to_hex()
        s.add(PointsLayer(lambda t, idx=idx: pos(t)[idx], color=col, size=3.2, glow=0.0, additive=False, z=1,
                          opacity=on * end, start=t_sp - 0.7))

    # ---- two points from opposite ends of the sheet that land side by side in the flat shadow
    F = K * (Xc @ R_pca.T)[:, :2]
    far = np.abs(tt[:, None] - tt[None, :]) > 0.55
    D = np.linalg.norm(F[:, None] - F[None, :], axis=2) + np.where(far, 0.0, 1e9)
    i, j = np.unravel_index(np.argmin(D), D.shape)
    ring_on = keys((t0, 0.0), (t_far - 0.1, 0.0), (t_far + 0.5, 1.0))

    def rings(t):
        a = float(ring_on(t))
        if a <= 0.001:
            return VGroup()
        p = pos(t)
        return VGroup(*[Circle(radius=0.13, stroke_color=C.text, stroke_width=2.6, stroke_opacity=a).move_to(P3(*p[k]))
                        for k in (i, j)])

    rm = s.manim(z=2, opacity=end)
    rm.redraw(rings, during=(t_far - 0.2, t1))

    # ---- names
    m = s.manim(z=3, opacity=end)
    lab = sans("flat shadow", 26, C.muted).move_to(P3(STAGE_L2[0] + 1.15, STAGE_L2[3] - 0.35))
    m.play(FadeIn(lab), at=t_sq + 1.4, dur=0.5)
    m.play(FadeOut(lab), at=t_curve - 0.3, dur=0.4)
    names = sans(r"kernel PCA \quad t-SNE \quad UMAP", 30).move_to(P3(CEN0[0], STAGE_L2[3] - 0.38))
    m.play(FadeIn(names, shift=DOWN * 0.1), at=t_kp, dur=0.8)
