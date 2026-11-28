"""ch1_s05 · A shape that rolls like a circle.

The circle drops onto a floor line and shrinks to roller size. On 'flat board' a board settles on top and the circle
rolls: the floor scrolls one way, the board's marks the other, the board's height never changes (a dimension arrow,
'constant width'), and the path of the centre is traced: a flat line. The statement circle ⇒ constant width appears;
on 'reverse' its two sides swap and a question mark is added. On "doesn't have" the circle rolls away and a Reuleaux
triangle rolls in (three arcs, each centred on the opposite corner of an equilateral triangle; the arcs light in turn
with their centres on 'built from three arcs'). The board stays just as level, but the centre's path now bobs: it is
not a circle. On 'fifty pence' a seven-arc shape rolls through once. On 'different claims' the reversed arrow becomes
⇏ and dims, under the true statement.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import GRID_C, P3, R1, reuleaux, sans, tex, the_circle, tint, window

W = 2.4                       # width of every roller
YG = -2.2                     # floor
OM = 0.9                      # rad/s, clockwise
V = OM * W / 2                # floor speed: a constant-width shape advances πW per turn, like the circle (Barbier)
BOARD_X = (-7.6, 3.3)
SHAPES = {3: reuleaux(3, W, 60), 7: reuleaux(7, W, 30)}


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch1_s05, T.ch1_s06)
def ch1_s05(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0 = float(s.start)
    t_board, t_rev, t_not = float(T.ch1_s05_flat_board), float(T.ch1_s05_reverse), float(T.ch1_s05_doesn_t_have)
    t_tri, t_50p, t_diff = float(T.ch1_s05_rounded_triangle), float(T.ch1_s05_fifty_pence), float(
        T.ch1_s05_different_claims)
    t_roll = t_board + 0.6

    # the circle from the grid drops to the floor and becomes a roller
    big = the_circle(R1).move_to(GRID_C)
    m.add(big)
    floor_line = Line(P3(-7.6, YG), P3(7.6, YG), stroke_color=C.muted, stroke_width=2.4)
    m.play(Create(floor_line), at=t0 + 0.6, dur=0.9)
    roller0 = the_circle(W / 2).move_to(P3(0, YG + W / 2))
    m.play(Transform(big, roller0), at=t0 + 1.0, dur=1.3, ease="easy_ease")
    m.remove(big, at=t_board - 0.3)

    # --- which shape is where: (shape key, slide-in start, slide-out start)
    phases = [("circle", None, t_not - 0.1), (3, t_not + 0.1, t_50p - 0.4), (7, t_50p - 0.2, None)]

    def x_of(t, t_in, t_out):
        x = 0.0
        if t_in is not None:
            x += 9.5 * (1 - ss((t - t_in) / 1.4))
        if t_out is not None:
            x -= 9.5 * ss((t - t_out) / 1.4)
        return x

    def phi(t):
        return -OM * max(t - t_roll, 0.0)

    def outline(key, t):
        """Boundary points of shape `key` at time t, rotated and resting on the floor, centred at x = 0."""
        if key == "circle":
            a = np.linspace(0, 2 * np.pi, 120)
            P = np.c_[W / 2 * np.cos(a), W / 2 * np.sin(a)]
        else:
            P = SHAPES[key]
        c, s_ = math.cos(phi(t)), math.sin(phi(t))
        Q = P @ np.array([[c, s_], [-s_, c]])
        Q[:, 1] += YG - Q[:, 1].min()
        return Q

    def centre_y(key, t):
        if key == "circle":
            return YG + W / 2
        P = SHAPES[key]
        c, s_ = math.cos(phi(t)), math.sin(phi(t))
        return YG - (P @ np.array([[c, s_], [-s_, c]]))[:, 1].min()

    def active(t):
        return [(k, a, b) for k, a, b in phases if (a is None or t >= a - 0.05) and (b is None or t <= b + 1.5)]

    def rollers(t):
        g = VGroup()
        for key, a, b in active(t):
            dx = x_of(t, a, b)
            Q = outline(key, t)
            pts = [P3(x + dx, y) for x, y in Q]
            col = C.circle if key == "circle" else C.foundations
            shape = VMobject(stroke_color=col, stroke_width=5 if key == "circle" else 4,
                             fill_color=C.bg if key == "circle" else tint(C.foundations, 0.1), fill_opacity=1)
            shape.set_points_as_corners(pts + [pts[0]])
            g.add(shape)
            cy = centre_y(key, t)
            mark = P3(dx + 0.55 * W / 2 * math.cos(phi(t) + 1.2), cy + 0.55 * W / 2 * math.sin(phi(t) + 1.2))
            g.add(Line(P3(dx, cy), mark, stroke_color=C.muted, stroke_width=2), Dot(P3(dx, cy), radius=0.06,
                                                                                    color=C.text))
            if key == 3 and t_tri + 1.0 <= t < t_tri + 3.4:       # 'built from three arcs': each arc and its centre
                k = int((t - t_tri - 1.0) / 0.8)
                n_ = len(Q) // 3
                arc = [P3(x + dx, y) for x, y in Q[k * n_:(k + 1) * n_ + 1]]
                cen = Q[((k + 2) % 3) * n_]
                cen = P3(cen[0] + dx, cen[1])
                g.add(VMobject(stroke_color=C.text, stroke_width=7).set_points_as_corners(arc),
                      Line(cen, arc[0], stroke_color=C.text, stroke_width=1.6),
                      Line(cen, arc[-1], stroke_color=C.text, stroke_width=1.6),
                      Dot(cen, radius=0.08, color=C.text))
        return g

    # the floor's hatching and the board's marks scroll in opposite directions
    def scenery(t):
        g = VGroup()
        sft = V * max(t - t_roll, 0.0)
        for x in np.arange(-8.0, 8.0, 0.4) - (sft % 0.4):
            g.add(Line(P3(x, YG), P3(x - 0.18, YG - 0.22), stroke_color=C.map_off, stroke_width=1.6))
        kb = ss((t - t_board + 0.4) / 0.8)
        if kb > 0:
            yb = YG + W + 0.08 + 1.6 * (1 - kb)
            board = Rectangle(width=BOARD_X[1] - BOARD_X[0], height=0.16, stroke_color=C.text, stroke_width=2,
                              fill_color=tint(C.muted, 0.35), fill_opacity=1)
            board.move_to(P3(sum(BOARD_X) / 2, yb))
            g.add(board)
            for x in np.arange(BOARD_X[0] - 1, BOARD_X[1] + 1, 0.7) + (sft % 0.7):
                if BOARD_X[0] + 0.05 < x < BOARD_X[1] - 0.05:
                    g.add(Line(P3(x, yb - 0.08), P3(x, yb + 0.08), stroke_color=C.muted, stroke_width=1.6))
        return g

    def trace(t):
        """Where the centre has been, carried left with the floor: flat for the circle, bobbing for the others."""
        g = VGroup()
        taus = np.arange(max(t_roll, t - 5.5), t, 0.05)
        pts = []
        for tau in taus:
            act = active(tau)
            key, a, b = min(act, key=lambda r: abs(x_of(tau, r[1], r[2])))
            if abs(x_of(tau, a, b)) > 0.02:                       # only while a shape is under the board
                continue
            pts.append(P3(x_of(tau, a, b) - V * (t - tau), centre_y(key, tau)))
        for j, p_ in enumerate(pts):
            g.add(Dot(p_, radius=0.03, color=C.change, fill_opacity=0.25 + 0.75 * j / max(len(pts), 1)))
        return g

    live0 = t_board - 0.4
    top.redraw(window(rollers, live0, float(s.end)), during=(live0, float(s.end)))
    m.redraw(window(scenery, live0, float(s.end)), during=(live0, float(s.end)))
    m.redraw(window(trace, t_roll, float(s.end)), during=(t_roll, float(s.end)))
    m.remove(roller0, at=live0)
    m.add(roller0, at=t0 + 2.3)
    m.remove(roller0, at=live0)

    # the board's height: a dimension arrow
    xa = BOARD_X[1] + 0.5
    dim_ = DoubleArrow(P3(xa, YG), P3(xa, YG + W), buff=0, stroke_width=3, color=C.text, tip_length=0.18)
    lab = sans("constant width", 30, C.text).next_to(dim_, RIGHT, buff=0.18)
    m.play(GrowFromCenter(dim_), FadeIn(lab, shift=0.08 * LEFT), at=t_board + 2.4, dur=0.6)
    path_lab = sans("path of the centre", 26, C.change).move_to(P3(-4.7, YG + W / 2 + 0.45))
    m.play(FadeIn(path_lab), at=t_board + 3.4, dur=0.5)
    m.play(FadeOut(path_lab), at=t_tri + 4.0, dur=0.5)

    # the logic: circle ⇒ constant width, then the reverse with a question mark
    fwd = MathTex(r"\text{circle}", r"\Rightarrow", r"\text{constant width}", font_size=48, color=C.text)
    fwd[0].set_color(C.circle)
    fwd.move_to(P3(0, 3.05))
    rev = MathTex(r"\text{constant width}", r"\Rightarrow", r"\text{circle}", r"\,?", font_size=48, color=C.text)
    rev[2].set_color(C.circle)
    rev[3].set_color(C.foundations)
    rev.move_to(P3(0, 3.05))
    m.play(Write(fwd), at=t_board + 2.9, dur=0.9)
    m.play(TransformMatchingTex(fwd, rev, path_arc=math.pi / 2), at=t_rev, dur=1.0, ease="easy_ease")

    lab50 = sans("seven arcs", 28, C.foundations).move_to(P3(0, YG - 0.75))
    lab3 = sans("three arcs", 28, C.foundations).move_to(P3(0, YG - 0.75))
    m.play(FadeIn(lab3, shift=0.08 * UP), at=t_tri + 1.0, dur=0.5)
    m.play(FadeOut(lab3), at=t_50p - 0.3, dur=0.4)
    m.play(FadeIn(lab50, shift=0.08 * UP), at=t_50p + 1.6, dur=0.5)
    m.play(FadeOut(lab50), at=t_diff - 0.6, dur=0.4)

    # 'different claims': the true statement above, the reverse struck to ⇏ and dimmed
    fwd2 = MathTex(r"\text{circle}", r"\Rightarrow", r"\text{constant width}", font_size=44, color=C.text)
    fwd2[0].set_color(C.circle)
    fwd2.move_to(P3(0, 3.3))
    nrev = MathTex(r"\text{constant width}", r"\not\Rightarrow", r"\text{circle}", font_size=44, color=C.muted)
    nrev.move_to(P3(0, 2.55))
    m.play(Transform(rev, nrev), FadeIn(fwd2, shift=0.1 * DOWN), at=t_diff, dur=0.9, ease="easy_ease")
    m.play(FadeOut(VGroup(rev, fwd2, dim_, lab, floor_line)), at=float(s.end) - 0.9, dur=0.7)
