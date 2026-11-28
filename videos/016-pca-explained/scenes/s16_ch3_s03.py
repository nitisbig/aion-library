"""ch3_s03 · C bends space (L2, rail: B_C, B_varu, B_dial).

The plane opens out to the whole stage. A circle of 24 unit arrows (C.probe). On 'Apply the covariance matrix' the
grid and the arrows move by C (scaled by 2.2/lambda1 to fit; a pure function of the blend): the circle becomes a
tilted ellipse (C.spread) and the cloud's ghost lies along it. On 'remember' the dial slides out of the rail into a
corner board. Each stretched arrow is measured along its own start direction: a dot at (u^T C u) u, with a thin
drop. On 'same record' a curve traces through those dots, and the dial flies in and lands on it exactly (a glow
flash). u^T C u = Var(u).
"""
import math

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (bead, CEN0, KP, P3, PHI1, STAGE_IN, STAGE_L2, backed, board, dial, glow_layer, grid_lines, panel, rail_c,
                 rail_obj, sans, slot, smoothstep, udir)

CC = np.array([-3.85, -0.1])
KC = 0.092
PBOX = (STAGE_L2[0] + 0.05, STAGE_L2[1] + 0.05, STAGE_L2[0] + 5.1, STAGE_L2[3] - 0.05)
R0 = 1.0                                          # the unit circle's radius on screen
DBOX = (-0.1, 0.95, 2.2, 3.2)                     # the dial's corner board


@scene(T.ch3_s03, T.ch3_s04)
def ch3_s03(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_mo, t_app, t_ell = float(T.ch3_s03_motion), float(T.ch3_s03_apply_the_covariance), float(T.ch3_s03_ellipse)
    t_rem, t_own, t_same, t_every = float(T.ch3_s03_remember), float(T.ch3_s03_along_its_own_origin), float(T.ch3_s03_same_record), float(T.ch3_s03_every_direction)
    t_knows = t_every - 2.2                       # 'The matrix knows'
    P = pd.people2()
    Xc = P.Xc
    lam1 = float(P.lam[0])
    M = P.C * (2.2 / lam1)                        # C, scaled so the long axis is 2.2 u

    # ---- the plane opens out to the whole stage (centre CC -> CEN0, unit KC -> KP)
    op = keys((t0, 0.0), (t0 + 0.2, 0.0), (t0 + 1.5, 1.0))
    blend = keys((t0, 0.0), (t_app - 0.1, 0.0), (t_app + 2.0, 1.0))

    def opened(t):
        return float(smoothstep(min(max(op(t), 0.0), 1.0)))

    def frame_c(t):
        u = opened(t)
        return CC + (CEN0 - CC) * u, KC + (KP - KC) * u, u

    def plane(t):
        c0, k, u = frame_c(t)
        bx = tuple(PBOX[i] + (STAGE_IN[i] - PBOX[i]) * u for i in range(4))
        b = float(blend(t))
        A = np.eye(2) * (1 - b) + M * b
        g = grid_lines(A, c0, k * 10, bx, n=10, minor=2, opacity=1.0 - 0.6 * b)
        if u < 1:
            g.add(*[bead(P3(*(c0 + k * q)), a=1 - u) for q in Xc])
        return g

    end = keys((t0, 1.0), (t1 - 0.7, 1.0), (t1 - 0.1, 0.0))   # the stage clears for the digits
    st = s.manim(z=0)
    st.add(rail_c(), rail_obj())
    s.manim(z=0, opacity=end).add(board(STAGE_L2))
    pm = s.manim(z=0.2, opacity=end)
    pm.redraw(plane, during=(t0, t1))

    # ---- the arrows (and, once stretched, the ellipse and the cloud's ghost)
    th = np.radians(np.arange(0, 360, 22.5))
    arr_on = keys((t0, 0.0), (t_mo - 0.2, 0.0), (t_mo + 0.8, 1.0))
    ell_on = keys((t0, 0.0), (t_ell - 0.1, 0.0), (t_ell + 0.7, 1.0))
    meas = keys((t0, 0.0), (t_own - 0.1, 0.0), (t_own + 1.6, 1.0, "linear"))

    def arrows(t):
        a = float(arr_on(t))
        if a <= 0.001:
            return VGroup()
        b = float(blend(t))
        A = np.eye(2) * (1 - b) + M * b
        g = VGroup()
        e = float(ell_on(t))
        if e > 0.001:
            ts = np.linspace(0, 2 * math.pi, 121)
            pts = [P3(*(CEN0 + R0 * (A @ udir(math.degrees(x))))) for x in ts]
            g.add(VMobject(stroke_color=C.spread, stroke_width=3, stroke_opacity=e).set_points_smoothly(pts))
            g.add(*[bead(P3(*(CEN0 + 2.2 * q / math.sqrt(lam1) / 3.0)), r=0.045,
                        a=0.35 * e) for q in Xc])
        mm = float(meas(t))
        for j, x in enumerate(th):
            u = np.array([math.cos(x), math.sin(x)])
            tip = CEN0 + R0 * (A @ u)
            g.add(Arrow(P3(*CEN0), P3(*tip), buff=0, stroke_color=C.probe, stroke_width=2.4 - 0.9 * b,
                        max_tip_length_to_length_ratio=0.12 - 0.04 * b, max_stroke_width_to_length_ratio=8,
                        color=C.probe).set_opacity(a * (0.85 - 0.5 * mm)))
            loc = min(max(mm * 1.4 - 0.4 * j / len(th), 0.0), 1.0)
            if loc > 0.001:
                foot = CEN0 + R0 * float(u @ M @ u) * u
                g.add(DashedLine(P3(*CEN0), P3(*(CEN0 + 2.3 * R0 * u)), stroke_color=C.probe, stroke_width=1.0,
                                 stroke_opacity=0.3 * loc, dash_length=0.06))     # its original direction
                g.add(Line(P3(*tip), P3(*(tip + (foot - tip) * loc)), stroke_color=C.muted, stroke_width=1.2,
                           stroke_opacity=0.7))
                if loc >= 0.999:
                    g.add(Dot(P3(*foot), radius=0.06, color=C.spread))
        return g

    am = s.manim(z=1, opacity=end)
    am.redraw(arrows, during=(t_mo - 0.3, t1))
    m = s.manim(z=3, opacity=end)
    cu = backed(MathTex(r"u \mapsto C\,u", font_size=44).set_color_by_tex("C", C.spread), 0.08).move_to(P3(-5.2, 2.75))
    m.play(FadeIn(cu), at=t_app + 0.3, dur=0.6)

    # ---- the dial: from the rail to a corner board, then onto the stage curve
    out_ = keys((t0, 0.0), (t_rem - 0.1, 0.0), (t_rem + 1.0, 1.0))
    land = keys((t0, 0.0), (t_same + 0.3, 0.0), (t_same + 1.6, 1.0))
    trace = keys((t0, 0.0), (t_same - 0.25, 0.0), (t_same + 0.55, 1.0, "linear"))
    sb = slot(2)
    sc_ = np.array([(sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2])
    dc = np.array([(DBOX[0] + DBOX[2]) / 2, (DBOX[1] + DBOX[3]) / 2])

    def dial_layer(t):
        u = float(smoothstep(min(max(out_(t), 0.0), 1.0)))
        box = tuple(sb[i] + (DBOX[i] - sb[i]) * u for i in range(4))
        c_ = sc_ + (dc - sc_) * u
        r_ = 0.85 + (0.95 - 0.85) * u
        lu = float(smoothstep(min(max(land(t), 0.0), 1.0)))
        g = VGroup(board(box).fade(lu))
        if u < 0.999:                                # the gold PC1 tip of the pinned dial lets go
            g.add(dial(c_, r_, PHI1, None, 1 - u, tip_col=C.pc1, grid=False))
        tr = float(trace(t))
        if tr > 0.001:                               # the stage curve: u^T C u along u, traced
            ds = np.linspace(0, 360 * tr, max(3, int(361 * tr)))
            g.add(VMobject(stroke_color=C.spread, stroke_width=3.2).set_points_as_corners(
                [P3(*(CEN0 + R0 * float(udir(d) @ M @ udir(d)) * udir(d))) for d in ds]))
        cc = c_ + (CEN0 - c_) * lu
        rr = r_ + (2.2 * R0 - r_) * lu
        if lu < 0.999:
            g.add(dial(cc, rr, None, None, 1 - lu))
        g.add(dial(cc, rr, None, (0, 180), 1.0, grid=False))
        return g

    dm = s.manim(z=2, opacity=end)
    dm.redraw(dial_layer, during=(t0, t1))
    fl = glow_layer(s, z=2.1, color=C.spread, k=1.2, opacity=keys((t0, 0.0), (t_same + 1.4, 0.0), (t_same + 1.8, 1.0),
                                                                    (t_same + 2.8, 0.0)))
    fl.add(VMobject(stroke_color=C.spread, stroke_width=4).set_points_as_corners(
        [P3(*(CEN0 + R0 * float(udir(d) @ M @ udir(d)) * udir(d))) for d in np.linspace(0, 360, 361)]))
    eq = backed(Eqn(r"u^\top C\,u = \mathrm{Var}(u)", colors={r"C": C.spread}, size=46), 0.08).move_to(P3(-1.85, -2.7))
    m.play(Write(eq), at=t_knows, dur=1.2)
