"""ch1_s01 · Rows become points (L2: the stage, the table in the rail). Premium look: borderless cards, slate plane,
beaded points with a soft glow, the cloud's density aura.

Chapter card (carry-over strip: the digit map, dim). The table of forty people sits on a card in the rail. A
line-drawn person stands on the stage: a height rule, then the arms rise and a rule spans fingertip to fingertip.
On 'Each row' row one lights (a pill) and its two numbers sit on the person's rules. On 'Give each person a dot' the
person shrinks to the top right of the stage, the plane draws, and the first rows fly out of the table along arcs
(comet trails) and land as beads with a ripple; the rest rain in. The density aura blooms under the cloud. On
'diagonal' its contour rings and the 2.2-sigma ellipse show the lean. On 'Leonardo da Vinci' the line person
dissolves into Leonardo's own drawing (the real sheet, ink lifted off the paper), its circle and square trace in
lamp light; on 'arm span is close to height' a span rule and a height rule of the same length, and y = x on the plot.
"""
import math
from pathlib import Path

import numpy as np
from aion import *

import pcadata as pd
from beats import T
from kit import (RAIL, RAW_CM, STAGE_IN, STAGE_L2, P3, Aura, backed, bead, bead_layer, caps, card, chapter_card,
                 digit_map, ellipse_of, glow_layer, raw_plane, raw_xy, sans, smoothstep, soft_disc, tex)

N_ROWS = 12
ROW0_Y, ROW_P = 2.28, 0.385
COL_X = (3.62, 5.32)
FIG_BIG = dict(x=-2.05, y=-2.75, H=4.45)
FIG_SMALL = dict(x=0.82, y=0.42, H=2.2)
SQ_FRAC = 1357 / 1720                         # the drawing's square side / image height (scripts/vitruvian_ink.py)
IMG_H = FIG_SMALL["H"] / SQ_FRAC
IMG_C = np.array([FIG_SMALL["x"] + 0.0067 * IMG_H, FIG_SMALL["y"] + FIG_SMALL["H"] / 2 + 0.0933 * IMG_H])
CIRC_CY, CIRC_R = 0.609, 0.612                # the drawn circle: centre y and radius, in units of H above the feet
IMG = Path(__file__).resolve().parents[1] / "assets/images/vitruvian_ink.png"


def person(x, y, H, arm_deg, alpha=1.0, color=None):
    """A line-drawn person standing at (x, y), H tall, arms at arm_deg (0 = straight out, -70 = at the sides).
    Span is H when the arms are out (Vitruvian proportions). Returns (figure, fingertip xs, shoulder y)."""
    col = color or C.probe
    w = max(2.0, 4.6 * H / 4.45)
    kw = dict(stroke_color=col, stroke_width=w, stroke_opacity=alpha)
    hr = 0.062 * H
    sh_y, hip_y = y + 0.80 * H, y + 0.49 * H
    sw = 0.10 * H
    arm = 0.5 * H - sw
    a = math.radians(arm_deg)
    head = Circle(radius=hr, **kw).move_to(P3(x, y + H - hr))
    g = VGroup(head,
               Line(P3(x, y + H - 2 * hr), P3(x, sh_y), **kw),
               Line(P3(x - sw, sh_y), P3(x + sw, sh_y), **kw),
               Line(P3(x, sh_y), P3(x, hip_y), **kw),
               Line(P3(x, hip_y), P3(x - 0.09 * H, y), **kw),
               Line(P3(x, hip_y), P3(x + 0.09 * H, y), **kw))
    tips = []
    for sgn in (-1, 1):
        sx = x + sgn * sw
        ex, ey = sx + sgn * arm * math.cos(a), sh_y + arm * math.sin(a)
        g.add(Line(P3(sx, sh_y), P3(ex, ey), **kw))
        tips.append((ex, ey))
    return g, tips, sh_y


def rule(p0, p1, alpha=1.0, tick=0.12, color=None, width=2.2):
    """A dimension line with end ticks (C.muted unless `color`)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = (p1 - p0) / max(np.linalg.norm(p1 - p0), 1e-9)
    n = np.array([-d[1], d[0]]) * tick
    kw = dict(stroke_color=color or C.muted, stroke_width=width, stroke_opacity=alpha)
    return VGroup(Line(P3(*p0), P3(*p1), **kw), Line(P3(*(p0 - n)), P3(*(p0 + n)), **kw),
                  Line(P3(*(p1 - n)), P3(*(p1 + n)), **kw))


def clamp01(x):
    return min(max(float(x), 0.0), 1.0)


def arc_pt(p0, p1, u, lift=1.2):
    c = (p0 + p1) / 2 + np.array([-0.4, lift])
    return (1 - u) ** 2 * p0 + 2 * u * (1 - u) * c + u ** 2 * p1


@scene(T.ch1_s01, T.ch1_s02)
def ch1_s01(s):
    s.solid(C.bg, z=-200)
    t0, t1 = float(s.start), float(s.end)
    t_forty, t_arm, t_row = float(T.ch1_s01_forty_people), float(T.ch1_s01_arm_span), float(T.ch1_s01_each_row)
    t_dot, t_diag, t_leo = float(T.ch1_s01_give_each_person_a_d), float(T.ch1_s01_diagonal), float(T.ch1_s01_leonardo_da_vinci)
    t_height = t_forty + 2.7                    # 'height,'
    t_tips = t_arm + 1.75                       # 'fingertip to fingertip'
    t_close = t_leo + 5.0                       # 'arm span is close to height'
    t_out = t1 - 1.05                           # table and drawing leave in the pause
    P = pd.people2()
    X = P.X
    Xi = np.round(X).astype(int)
    n = len(X)
    W = raw_xy(X)

    # ---- chapter card with the digit map as its carry-over strip
    on = chapter_card(s, t0, t0 + 2.75, "chapter one", "Data as a Cloud")
    digit_map(s, (-2.2, -3.25, 2.2, -1.45), opacity=on * 0.5, size=2.4, start=t0)

    # ---- the table on a card in the rail
    tab_on = keys((t0, 1.0), (t_out, 1.0), (t_out + 0.7, 0.0))
    m = s.manim(z=1, opacity=tab_on)
    tab = card(RAIL)
    heads = VGroup(sans("height", 22, C.muted).move_to(P3(COL_X[0], 2.86)),
                   sans("arm span", 22, C.muted).move_to(P3(COL_X[1], 2.86)))
    unit = VGroup(sans("cm", 18, C.muted).set_opacity(0.6).next_to(heads[0], RIGHT, buff=0.08),
                  sans("cm", 18, C.muted).set_opacity(0.6).next_to(heads[1], RIGHT, buff=0.08))
    hair = Line(P3(RAIL[0] + 0.3, 2.6), P3(RAIL[2] - 0.3, 2.6), stroke_color=C.plane, stroke_width=1.4)
    rows = VGroup(*[VGroup(tex(str(Xi[i, 0]), 30).move_to(P3(COL_X[0], ROW0_Y - i * ROW_P)),
                           tex(str(Xi[i, 1]), 30).move_to(P3(COL_X[1], ROW0_Y - i * ROW_P)))
                    for i in range(N_ROWS)])
    more = tex(r"\vdots", 30, C.muted).move_to(P3((COL_X[0] + COL_X[1]) / 2, ROW0_Y - N_ROWS * ROW_P - 0.02))
    m.play(FadeIn(tab), at=t_forty - 0.3, dur=0.6)
    m.play(FadeIn(VGroup(heads, unit)), FadeIn(hair, shift=RIGHT * 0.2), at=t_forty, dur=0.6)
    m.play(LaggedStart(*[FadeIn(r, shift=UP * 0.08) for r in rows], lag_ratio=0.12), at=t_forty + 0.2, dur=2.0)
    m.play(FadeIn(more), at=t_forty + 2.0, dur=0.5)

    # flights: row i leaves the table at launch[i]; the row then dims
    launch = [t_dot + 1.0 + 0.2 * i for i in range(N_ROWS)]
    FLY = 1.0
    for i in range(N_ROWS):
        m.play(rows[i].animate.set_opacity(0.35), at=launch[i] + 0.05, dur=0.4)

    # the selection pill: on row 0 at 'Each row', then it walks down with the launches
    pill_on = keys((t0, 0.0), (t_row - 0.05, 0.0), (t_row + 0.45, 1.0), (launch[-1] + 0.3, 1.0), (launch[-1] + 0.9, 0.0))
    pw = RAIL[2] - RAIL[0] - 0.4

    def pill(t):
        a = float(pill_on(t))
        if a <= 0.001:
            return VGroup()
        k = (t - launch[0] + 0.15) / 0.2
        k = min(max(k, 0.0), N_ROWS - 1.0)
        k = math.floor(k) + float(smoothstep(min((k - math.floor(k)) * 2.5, 1.0)))
        y = ROW0_Y - k * ROW_P
        cx = (RAIL[0] + RAIL[2]) / 2
        return VGroup(RoundedRectangle(corner_radius=0.08, width=pw, height=0.34, stroke_width=0, fill_color=C.data,
                                       fill_opacity=0.16 * a).move_to(P3(cx, y)),
                      RoundedRectangle(corner_radius=0.025, width=0.05, height=0.24, stroke_width=0, fill_color=C.data,
                                       fill_opacity=a).move_to(P3(cx - pw / 2 + 0.1, y)))

    pm = s.manim(z=0.9, opacity=tab_on)
    pm.redraw(pill, during=(t_row - 0.1, launch[-1] + 1.0))

    # ---- the person: centre stage, then to the top right of the stage
    shrink = keys((t0, 0.0), (t_dot - 0.2, 0.0), (t_dot + 1.0, 1.0))
    fig_on = keys((t_height - 0.6, 0.0), (t_height, 1.0), (t_leo + 0.2, 1.0), (t_leo + 1.5, 0.0))
    arms = keys((t0, -72.0), (t_arm - 0.1, -72.0), (t_arm + 0.9, 0.0, "out_back"))
    h_rule = keys((t_height - 0.1, 0.0), (t_height + 0.6, 1.0), (t_dot - 0.2, 1.0), (t_dot + 0.3, 0.0))
    s_rule = keys((t_tips - 0.15, 0.0), (t_tips + 0.6, 1.0), (t_dot - 0.2, 1.0), (t_dot + 0.3, 0.0))
    vals = keys((t_row, 0.0), (t_row + 0.5, 1.0), (t_dot - 0.2, 1.0), (t_dot + 0.3, 0.0))

    def fig_state(t):
        u = float(smoothstep(clamp01(shrink(t))))
        return {k: FIG_BIG[k] + (FIG_SMALL[k] - FIG_BIG[k]) * u for k in FIG_BIG}

    def draw_person(t):
        a = float(fig_on(t))
        if a <= 0.001:
            return VGroup()
        st = fig_state(t)
        x, y, H = st["x"], st["y"], st["H"]
        g, tips, sh_y = person(x, y, H, float(arms(t)), a)
        out = VGroup(g)
        hr_ = float(h_rule(t)) * a
        if hr_ > 0.001:
            rx = x - 0.36 * H
            out.add(rule((rx, y), (rx, y + H), hr_))
        sr = float(s_rule(t)) * a
        if sr > 0.001:
            ry = y + H + 0.16 * H
            (lx, _), (rx2, _) = tips
            out.add(rule((lx, ry), (rx2, ry), sr))
            for tx_, ty_ in tips:
                out.add(DashedLine(P3(tx_, ty_ + 0.06), P3(tx_, ry - 0.04), stroke_color=C.muted, stroke_width=1.4,
                                   stroke_opacity=sr * 0.7, dash_length=0.06))
        va = float(vals(t)) * a
        if va > 0.001:
            out.add(tex(str(Xi[0, 0]), 32, C.data).set_opacity(va).move_to(P3(x - 0.36 * H - 0.42, y + H / 2)))
            out.add(tex(str(Xi[0, 1]), 32, C.data).set_opacity(va).move_to(P3(x, y + H + 0.16 * H + 0.3)))
        return out

    fig = glow_layer(s, z=3, color=C.probe, k=0.12)
    fig.redraw(draw_person, during=(t_height - 0.7, t_leo + 1.6))

    # ---- the stage: a card, the premium plane
    pl = s.manim(z=-1)
    pl.play(FadeIn(card(STAGE_L2)), at=t_dot - 0.3, dur=0.6)
    gm = s.manim(z=0)
    grid, ticks, names = raw_plane(pr=True)
    gm.play(Create(grid, lag_ratio=0.01), at=t_dot, dur=1.4)
    gm.play(FadeIn(ticks), at=t_dot + 1.0, dur=0.6)
    gm.play(FadeIn(names[0]), at=t_dot + 1.7, dur=0.5)
    gm.play(FadeIn(names[1]), at=t_dot + 3.3, dur=0.5)

    # a soft hole in the plane where the small person / the drawing stands
    disc, dkw = soft_disc(1.62)
    disc_on = keys((t0, 0.0), (t_dot, 0.0), (t_dot + 1.0, 1.0), (t_out, 1.0), (t_out + 0.7, 0.0))
    s.add(FramesLayer(lambda t: disc, z=2.4, opacity=disc_on, pos=tuple(IMG_C), during=[(t_dot - 0.1, t1)],
                      **{k: v for k, v in dkw.items()}))

    # ---- the cloud: arcs with comet trails for the first rows, a rain of beads for the rest, ripples on landing
    srcs = [np.array([(COL_X[0] + COL_X[1]) / 2, ROW0_Y - i * ROW_P]) for i in range(N_ROWS)]
    rng = np.random.default_rng(1601)
    rain = t_dot + 3.4 + 0.055 * np.arange(n - N_ROWS) + rng.uniform(0, 0.04, n - N_ROWS)
    land = np.r_[np.array(launch) + FLY, rain + 0.5]

    def cloud(t):
        g = VGroup()
        for i in range(n):
            if i < N_ROWS:
                u = (t - launch[i]) / FLY
                if u <= 0:
                    continue
                if u < 1:
                    e = float(smoothstep(u))
                    for k in range(8, 0, -1):                     # the comet trail
                        ua, ub = max(e - 0.045 * k, 0.0), max(e - 0.045 * (k - 1), 0.0)
                        if ub - ua < 1e-4:
                            continue
                        g.add(Line(P3(*arc_pt(srcs[i], W[i], ua)), P3(*arc_pt(srcs[i], W[i], ub)),
                                   stroke_color=C.data, stroke_width=3.2 * (1 - k / 9), stroke_opacity=0.7 * (1 - k / 9)))
                    g.add(bead(P3(*arc_pt(srcs[i], W[i], e)), r=0.035 + 0.027 * e))
                    continue
            else:
                u = (t - rain[i - N_ROWS]) / 0.5
                if u <= 0:
                    continue
                if u < 1:
                    e = 1 - (1 - u) ** 3
                    g.add(bead(P3(W[i, 0], W[i, 1] + 0.45 * (1 - e)), r=0.062 * (0.6 + 0.4 * e), a=min(1.0, 1.6 * u)))
                    continue
            g.add(bead(P3(*W[i])))
            v = (t - land[i]) / 0.6
            if 0 <= v < 1:                                       # landing ripple
                g.add(Circle(radius=0.08 + 0.3 * v, stroke_color=C.data, stroke_width=2.0,
                             stroke_opacity=0.75 * (1 - v) ** 1.5).move_to(P3(*W[i])))
        return g

    dm = bead_layer(s, z=2)
    dm.redraw(cloud, during=(launch[0] - 0.05, t1))

    # ---- the density aura; on 'diagonal' its contour rings and the 2.2-sigma ellipse
    au = Aura(STAGE_IN)
    au_on = keys((t0, 0.0), (land.max() + 0.2, 0.0), (land.max() + 1.4, 1.0))
    rings = keys((t0, 0.0), (t_diag + 0.2, 0.0), (t_diag + 1.4, 1.0), (t_leo - 0.3, 1.0), (t_leo + 0.6, 0.35))
    s.add(FramesLayer(lambda t: au.frame(W, 1.0, float(rings(t))), z=0.5, opacity=au_on, during=[(land.max(), t1)],
                      **au.layer_kw()))
    c, w, h, ang = ellipse_of(W, k=2.2)
    ell = Ellipse(width=w, height=h, stroke_color=C.text, stroke_width=1.6, stroke_opacity=0.55)
    ell.rotate(ang).move_to(P3(*c))
    em = s.manim(z=1)
    em.play(Create(ell), at=t_diag, dur=1.3)
    em.play(FadeOut(ell), at=t_leo - 0.3, dur=0.8)

    # ---- Leonardo's drawing: the line person dissolves into it
    img_on = keys((t0, 0.0), (t_leo - 0.1, 0.0), (t_leo + 1.4, 1.0), (t_out, 1.0), (t_out + 0.7, 0.0))
    img_sc = keys((t0, 1.05), (t_leo - 0.1, 1.05), (t_leo + 2.0, 1.0, "out_cubic"))
    s.image(str(IMG), height=IMG_H, z=2.6, pos=tuple(IMG_C), opacity=img_on, scale=img_sc)
    # its circle and square trace in lamp light, then a span rule and a height rule of the same length
    x, y, H = FIG_SMALL["x"], FIG_SMALL["y"], FIG_SMALL["H"]
    lit = glow_layer(s, z=2.8, color=C.lamp, k=0.45, opacity=keys((t_out, 1.0), (t_out + 0.7, 0.0)))
    circ = Arc(radius=CIRC_R * H, start_angle=-math.pi / 2, angle=2 * math.pi, stroke_color=C.lamp, stroke_width=2.4,
               arc_center=P3(x, y + CIRC_CY * H))
    sq = Square(side_length=H, stroke_color=C.lamp, stroke_width=2.4).move_to(P3(x, y + H / 2))
    lit.play(Create(circ), at=t_leo + 1.0, dur=1.4, ease="smooth")
    lit.play(Create(sq), at=t_leo + 1.9, dur=1.2, ease="smooth")
    lit.play(FadeOut(VGroup(circ, sq)), at=t_close - 0.6, dur=0.6)
    span = rule((x - H / 2, y + H + 0.14), (x + H / 2, y + H + 0.14), 1.0, 0.08, C.lamp, 2.6)
    tall = rule((x + H / 2 + 0.14, y), (x + H / 2 + 0.14, y + H), 1.0, 0.08, C.lamp, 2.6)
    lit.play(Create(span), at=t_close - 0.1, dur=0.7)
    lit.play(Create(tall), at=t_close + 0.4, dur=0.7)
    cap = VGroup(caps("Leonardo da Vinci", 24), sans("c. 1490", 18, C.muted)).arrange(DOWN, buff=0.07)
    cap.move_to(P3(IMG_C[0], IMG_C[1] - IMG_H / 2 - 0.2))
    capm = s.manim(z=4, opacity=keys((t_out, 1.0), (t_out + 0.7, 0.0)))
    capm.play(FadeIn(cap, shift=UP * 0.08), at=t_leo + 0.5, dur=0.8)

    # y = x on the plot: arm span equal to height, in the same lamp light
    diag = DashedLine(P3(*raw_xy((RAW_CM + 2, RAW_CM + 2))), P3(*raw_xy((193, 193))), stroke_color=C.lamp,
                      stroke_width=2.2, dash_length=0.1)
    lit.play(Create(diag), at=t_close + 0.6, dur=1.2)
    yx = backed(tex(r"a = h", 28, C.lamp), fill=C.card).move_to(P3(*raw_xy((191, 196))) + P3(-0.35, 0.05))
    capm.play(FadeIn(yx), at=t_close + 1.5, dur=0.5)
