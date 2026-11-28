"""ch5_s01 · From three to two (L2, rail: B_recipe).

Chapter card (carry-over strip: the recipe). The forty people with three measurements, as a 3D cloud on the stage
(a pure function of the view rotation), turning slowly. On 'pebble' its three principal axes draw at ±2σ (gold,
teal, violet): long, fairly wide, thin. On 'flat sheet' the plane of PC1 and PC2 appears. On 'Drop every point'
each point slides onto the sheet, leaving its drop (C.residual). On 'face us' the view turns until the sheet faces
the camera (axes PC1, PC2): R^3 -> R^2. On 'threw away' the view tips back so the short drops show, and they glow.
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, P3, STAGE_L2, backed, board, chapter_card, glow_layer, rail_recipe, sans, slerp, smoothstep)

K = 0.1                                           # world units per cm


def rx(a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])


def rz(a):
    c, s_ = math.cos(a), math.sin(a)
    return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])


@scene(T.ch5_s01, T.ch5_s02)
def ch5_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t3, t_peb, t_sheet = float(T.ch5_s01_three_measurements), float(T.ch5_s01_pebble), float(T.ch5_s01_flat_sheet)
    t_drop, t_face, t_away = float(T.ch5_s01_drop_every_point), float(T.ch5_s01_face_us), float(T.ch5_s01_threw_away)
    t_two = t_face + 3.0                          # 'three numbers per person to two'
    Q = pd.people3()
    X = Q.Xc
    V = Q.V.copy()
    if np.linalg.det(V) < 0:
        V[:, 2] *= -1
    sig = np.sqrt(Q.lam)
    v1, v2, v3 = V[:, 0], V[:, 1], V[:, 2]
    F = X - np.outer(X @ v3, v3)                  # the feet on the sheet
    end = keys((t0, 1.0), (t1 - 0.8, 1.0), (t1 - 0.1, 0.0))

    # ---- card; strip = the recipe
    on = chapter_card(s, t0, t0 + 2.6, "chapter five", "Cutting Dimensions")
    strip = s.manim(z=20, opacity=on * 0.5)
    strip.add(rail_recipe().move_to(P3(0, -2.35)))
    back = keys((t0, 0.0), (t0 + 2.2, 0.0), (t0 + 3.0, 1.0))
    st = s.manim(z=0, opacity=back)
    st.add(board(STAGE_L2), rail_recipe())

    # ---- the view: an oblique orbit, then face-on to the sheet, then tipped back
    R_face = V.T                                  # PC1 -> x, PC2 -> y, PC3 -> depth
    R_tip = rx(math.radians(-55)) @ R_face
    az = keys((t0, -20.0), (t_face - 0.6, 40.0, "linear"))
    face = keys((t0, 0.0), (t_face - 0.3, 0.0), (t_face + 2.0, 1.0))
    tip = keys((t0, 0.0), (t_away - 0.4, 0.0), (t_away + 1.4, 1.0))

    def R_at(t):
        R0 = rx(math.radians(-64)) @ rz(math.radians(float(az(t))))
        R = slerp(R0, R_face, float(smoothstep(min(max(face(t), 0.0), 1.0))))
        u = float(smoothstep(min(max(tip(t), 0.0), 1.0)))
        return slerp(R, R_tip, u) if u > 0.0 else R

    def scr(R, p):
        q = R @ (np.asarray(p, float) * K)
        return P3(CEN0[0] + q[0], CEN0[1] + q[1]), q[2]

    cl_on = keys((t0, 0.0), (t3 - 0.4, 0.0), (t3 + 0.6, 1.0))
    ax_on = keys((t0, 0.0), (t3 - 0.2, 0.0), (t3 + 0.8, 1.0), (t_peb - 0.2, 1.0), (t_peb + 0.6, 0.25),
                 (t_face - 0.5, 0.25), (t_face + 0.3, 0.0))
    pcs = [keys((t0, 0.0), (t_peb + 0.3 + 0.7 * i, 0.0), (t_peb + 1.0 + 0.7 * i, 1.0)) for i in range(3)]
    sheet = keys((t0, 0.0), (t_sheet - 0.2, 0.0), (t_sheet + 0.9, 1.0))
    drop = keys((t0, 0.0), (t_drop - 0.1, 0.0), (t_drop + 1.8, 1.0, "linear"))
    n = len(X)

    def view(t):
        a = float(cl_on(t))
        if a <= 0.001:
            return VGroup()
        R = R_at(t)
        g = VGroup()
        ax = float(ax_on(t))
        for d, lab in (((1, 0, 0), "height"), ((0, 1, 0), "arm span"), ((0, 0, 1), "shoulder")):
            (p0, _), (p1, _) = scr(R, np.multiply(d, -22)), scr(R, np.multiply(d, 22))
            g.add(Line(p0, p1, stroke_color=C.axis, stroke_width=1.8, stroke_opacity=0.7 * ax * a))
            g.add(sans(lab, 22, C.muted).set_opacity(ax * a).move_to(p1 + 0.25 * (p1 - P3(*CEN0)) / max(np.linalg.norm(p1 - P3(*CEN0)), 0.3)))
        sh = float(sheet(t))
        if sh > 0.001:
            L1, L2 = 2.8 * sig[0], 3.2 * sig[1]
            cs = [scr(R, a_ * L1 * v1 + b_ * L2 * v2)[0] for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            g.add(Polygon(*cs, stroke_color=C.probe, stroke_width=1.6, stroke_opacity=0.7 * sh, fill_color=C.probe,
                          fill_opacity=0.045 * sh))
        for i, col in enumerate((C.pc1, C.pc2, C.pc3)):
            p = float(pcs[i](t))
            if p > 0.001:
                v = V[:, i] * 2 * sig[i] * p
                g.add(Line(scr(R, -v)[0], scr(R, v)[0], stroke_color=col, stroke_width=4))
        dp = float(drop(t))
        pts = []
        for j in range(n):
            loc = min(max(dp * 1.6 - 0.6 * j / n, 0.0), 1.0)
            p, z = scr(R, X[j] + (F[j] - X[j]) * loc)
            pts.append((z, j, p, loc))
        zs = np.array([z for z, *_ in pts])
        zn = (zs - zs.min()) / max(np.ptp(zs), 1e-6)
        for z, j, p, loc in sorted(pts, key=lambda q: -q[0]):
            if loc > 0.001:
                g.add(Line(scr(R, X[j])[0], p, stroke_color=C.residual, stroke_width=1.8, stroke_opacity=0.85 * a))
            near = 1.0 - zn[j]
            g.add(bead(p, r=0.042 + 0.022 * near, a=a * (0.55 + 0.45 * near)))
        return g

    vm = s.manim(z=2, opacity=end)
    vm.redraw(view, during=(t3 - 0.5, t1))

    # ---- the drops glow on 'threw away'
    gl = glow_layer(s, z=1.9, color=C.residual, k=0.8, opacity=end * keys((t0, 0.0), (t_away + 0.6, 0.0),
                                                                             (t_away + 1.3, 1.0)))
    gl.redraw(lambda t: VGroup(*[Line(scr(R_at(t), X[j])[0], scr(R_at(t), F[j])[0], stroke_color=C.residual,
                                      stroke_width=2.2) for j in range(n)]), during=(t_away + 0.5, t1))

    # ---- names and the count
    m = s.manim(z=3, opacity=end)
    n1 = sans("PC1", 28, C.pc1).move_to(P3(CEN0[0] + 2 * sig[0] * K + 0.45, CEN0[1] + 0.05))
    n2 = sans("PC2", 28, C.pc2).move_to(P3(CEN0[0] + 0.05, CEN0[1] + 2 * sig[1] * K + 0.3))
    m.play(FadeIn(VGroup(n1, n2)), at=t_face + 1.8, dur=0.6)
    m.play(FadeOut(VGroup(n1, n2)), at=t_away - 0.4, dur=0.4)
    eq = backed(Eqn(r"\mathbb{R}^3 \;\to\; \mathbb{R}^2", size=50), 0.08).move_to(P3(-4.75, 2.7))
    m.play(Write(eq), at=t_two, dur=1.0)
