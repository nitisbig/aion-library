"""The chapter progress tracker: six badges, bottom left, through Chapters 1–6 (and a closing salute in Ch7).

One badge per pillar, each with its own icon, in its pillar color:
    Foundations   a Venn diagram: two sets drift together and their overlap lights
    Quantity      a number line: a dot hops tick to tick, counting
    Structure     a hexagon that turns by a sixth (the map's own move) and looks unchanged
    Space         a torus with a point riding round it (topology)
    Change        a curve with its tangent line sliding along (the derivative)
    Uncertainty   a die that tumbles and lands on a new face

States: upcoming badges are slate outlines; the current one is bigger, alive (its icon animates), and its rim fills
clockwise with the chapter's progress while the track to the next badge fills with a color gradient; finished
badges keep their color and a full rim. A chapter start pops its badge with a ripple; the previous badge flashes
complete. On Ch7 all six salute in turn and the tracker bows out.

Every frame is a pure function of absolute time; the layer ignores camera moves (parallax=0).

Example:
    from hud import progress
    progress(s)            # in any scene, right after s.solid(...)
"""
from __future__ import annotations

import math

import numpy as np
from aion import *  # noqa: F401,F403

from beats import T
from kit import PX, Canvas, caps, mix_hex, rgb255
from theme import NAMES, PILLARS

CH = [float(getattr(T, f"ch{k}_s01")) for k in range(1, 8)]   # chapter starts; CH[6] = Ch7
X0, Y0, D, R = -6.4, -3.66, 0.6, 0.215                          # first badge centre, spacing, badge radius
BOX = (X0 - 0.55, Y0 - 0.34, X0 + 5 * D + 0.55, Y0 + 0.5)
LAB_S = 7.0                                                      # the chapter name shows this long
T_IN, T_OUT = CH[0] + 0.6, CH[6] + 4.2                           # tracker on screen


def ss(x):
    x = min(max(float(x), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def out_back(x, s=2.2):
    x = min(max(float(x), 0.0), 1.0) - 1
    return 1 + x * x * ((s + 1) * x + s)


def chapter_at(t: float) -> int:
    """0..5 inside Chapters 1–6, 6 from Ch7 on, -1 before Ch1."""
    if t < CH[0]:
        return -1
    for k in range(6):
        if t < CH[k + 1]:
            return k
    return 6


class _Draw:
    def __init__(self):
        self.cv = Canvas(BOX)
        self.sk = self.cv.skia

    # paints
    def stroke(self, col, a, w, cap=None):
        p = self.cv.paint(col, a, w)
        if cap is not None:
            p.setStrokeCap(cap)
        return p

    def fill(self, col, a):
        sk = self.sk
        r, g, b = rgb255(col)
        return sk.Paint(AntiAlias=True, Style=sk.Paint.kFill_Style,
                        Color=sk.Color(r, g, b, int(round(255 * min(max(a, 0.0), 1.0)))))

    # ---- the six icons, drawn around (0, 0) in px with size r (the badge radius), already translated ----
    def i_foundations(self, c, r, col, a, ph):
        sk = self.sk
        off = r * (0.27 + 0.09 * math.sin(2 * math.pi * ph / 3.0))
        rr = 0.47 * r
        p1, p2 = sk.Path(), sk.Path()
        p1.addCircle(-off, 0, rr)
        p2.addCircle(off, 0, rr)
        c.save()
        c.clipPath(p1, doAntiAlias=True)
        c.drawPath(p2, self.fill(col, a * (0.45 + 0.25 * math.sin(2 * math.pi * ph / 3.0 + 1.2))))
        c.restore()
        w = 0.085 * r
        c.drawPath(p1, self.stroke(col, a, w))
        c.drawPath(p2, self.stroke(col, a, w))

    def i_quantity(self, c, r, col, a, ph):
        w = 0.08 * r
        L = 0.7 * r
        y = 0.3 * r
        c.drawLine(-L, y, L, y, self.stroke(col, a, w, self.sk.Paint.kRound_Cap))
        xs = np.linspace(-0.55 * r, 0.55 * r, 4)
        for x in xs:
            c.drawLine(x, y - 0.13 * r, x, y + 0.13 * r, self.stroke(col, a, w))
        hop = 0.7                                                   # seconds per hop
        k = int(ph / hop) % 4
        u = (ph % hop) / hop
        x_a, x_b = xs[k], xs[(k + 1) % 4]
        if k == 3:                                                  # back to the start: slide, don't hop
            x = x_a + (x_b - x_a) * ss(u)
            h = 0.0
        else:
            x = x_a + (x_b - x_a) * ss(u)
            h = 0.62 * r * 4 * u * (1 - u)
        c.drawCircle(x, y - 0.13 * r - 0.07 * r - h, 0.12 * r, self.fill(col, a))

    def i_structure(self, c, r, col, a, ph):
        period = 2.0
        u = ss(((ph % period) / period - 0.55) / 0.35)
        ang = (int(ph / period) + u) * math.pi / 3
        rr = 0.58 * r
        pts = [(rr * math.cos(ang + j * math.pi / 3), rr * math.sin(ang + j * math.pi / 3)) for j in range(6)]
        path = self.sk.Path()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, self.fill(col, a * 0.16))
        c.drawPath(path, self.stroke(col, a, 0.085 * r))
        c.drawCircle(*pts[0], 0.11 * r, self.fill(col, a))           # a marked vertex shows the turn
        arc = self.sk.Rect.MakeLTRB(-0.86 * r, -0.86 * r, 0.86 * r, 0.86 * r)
        c.drawArc(arc, -40, 70, False, self.stroke(col, a * 0.7, 0.06 * r, self.sk.Paint.kRound_Cap))

    def i_space(self, c, r, col, a, ph):
        sk = self.sk
        w = 0.08 * r
        c.drawOval(sk.Rect.MakeLTRB(-0.78 * r, -0.44 * r, 0.78 * r, 0.44 * r), self.stroke(col, a, w))
        c.drawArc(sk.Rect.MakeLTRB(-0.38 * r, -0.2 * r, 0.38 * r, 0.12 * r), 20, 140, False,
                  self.stroke(col, a, w, sk.Paint.kRound_Cap))            # the hole: lower lip
        c.drawArc(sk.Rect.MakeLTRB(-0.28 * r, -0.04 * r, 0.28 * r, 0.24 * r), 200, 140, False,
                  self.stroke(col, a, w, sk.Paint.kRound_Cap))            # upper lip
        th = 2 * math.pi * ph / 2.4
        x, y = 0.58 * r * math.cos(th), 0.31 * r * math.sin(th)
        front = math.sin(th) > 0
        c.drawCircle(x, y, 0.12 * r, self.fill(col, a * (1.0 if front else 0.35)))

    def i_change(self, c, r, col, a, ph):
        sk = self.sk
        def f(x):            # a gentle S-curve across the badge (px)
            return -0.38 * r * math.sin(1.9 * x / r)

        def df(x):
            return -0.38 * 1.9 * math.cos(1.9 * x / r)

        path = sk.Path()
        xs = np.linspace(-0.72 * r, 0.72 * r, 24)
        path.moveTo(xs[0], f(xs[0]) + 0.05 * r)
        for x in xs[1:]:
            path.lineTo(x, f(x) + 0.05 * r)
        c.drawPath(path, self.stroke(col, a, 0.08 * r, sk.Paint.kRound_Cap))
        x = 0.55 * r * math.sin(2 * math.pi * ph / 3.2)
        y = f(x) + 0.05 * r
        s_ = df(x)
        n = math.hypot(1, s_)
        L = 0.42 * r
        c.drawLine(x - L / n, y - L * s_ / n, x + L / n, y + L * s_ / n,
                   self.stroke(mix_hex(col, C.text, 0.45), a, 0.07 * r, sk.Paint.kRound_Cap))
        c.drawCircle(x, y, 0.11 * r, self.fill(col, a))

    FACES = (3, 5, 1, 6, 2, 4)
    PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)], 5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}

    def i_uncertainty(self, c, r, col, a, ph):
        sk = self.sk
        period = 1.6
        k = int(ph / period)
        u = ss(((ph % period) / period - 0.6) / 0.4)                 # rest, then a quick tumble
        face = self.FACES[(k + (1 if u > 0.5 else 0)) % 6]
        hop = 0.18 * r * math.sin(math.pi * u)
        c.save()
        c.translate(0, -hop)
        c.rotate(12 + 90 * u)
        s_ = 0.5 * r * (1 - 0.12 * math.sin(math.pi * u))
        rect = sk.Rect.MakeLTRB(-s_, -s_, s_, s_)
        c.drawRoundRect(rect, 0.22 * r, 0.22 * r, self.fill(col, a * 0.16))
        c.drawRoundRect(rect, 0.22 * r, 0.22 * r, self.stroke(col, a, 0.08 * r))
        for px_, py_ in self.PIPS[face]:
            c.drawCircle(px_ * 0.26 * r, py_ * 0.26 * r, 0.075 * r, self.fill(col, a))
        c.restore()

    ICONS = ("i_foundations", "i_quantity", "i_structure", "i_space", "i_change", "i_uncertainty")

    # ---- one frame ----
    def frame(self, t: float):
        sk, cv = self.sk, self.cv
        c = cv.begin()
        vis = ss((t - T_IN) / 0.6) * (1 - ss((t - T_OUT) / 0.7))
        if vis <= 0:
            return cv.array()
        cur = chapter_at(t)
        px = cv.px
        cols = [getattr(C, p) for p in PILLARS]
        centres = [cv.T(X0 + j * D, Y0) for j in range(6)]

        # a dark pill behind the row keeps grids and lines from running through it
        xl, yl = cv.T(X0 - R * 1.55, Y0 + R * 1.55)
        xr, yr = cv.T(X0 + 5 * D + R * 1.55, Y0 - R * 1.55)
        c.drawRoundRect(sk.Rect.MakeLTRB(xl, yl, xr, yr), (yr - yl) / 2, (yr - yl) / 2, self.fill(C.bg, 0.8 * vis))

        # the track between badges
        for j in range(5):
            (xa, ya), (xb, yb) = centres[j], centres[j + 1]
            xa, xb = xa + R * px * 1.05, xb - R * px * 1.05
            c.drawLine(xa, ya, xb, yb, self.stroke(C.map_off, 0.55 * vis, 2.2, sk.Paint.kRound_Cap))
            if cur > j:
                fill = 1.0
            elif cur == j:
                fill = (t - CH[j]) / (CH[j + 1] - CH[j])
            else:
                fill = 0.0
            if fill > 0:
                xe = xa + (xb - xa) * min(fill, 1.0)
                p = self.stroke(cols[j], vis, 3.2, sk.Paint.kRound_Cap)
                p.setShader(sk.GradientShader.MakeLinear(
                    [sk.Point(xa, ya), sk.Point(xb, yb)],
                    [sk.Color(*rgb255(cols[j])), sk.Color(*rgb255(cols[j + 1]))]))
                p.setAlphaf(vis)
                c.drawLine(xa, ya, xe, yb, p)
                if cur == j:                                          # a bright head on the moving end
                    c.drawCircle(xe, yb, 3.4, self.fill(mix_hex(cols[j], C.text, 0.5), vis))

        # the badges
        for j in range(6):
            x, y = centres[j]
            col = cols[j]
            k_in = ss((t - T_IN - 0.08 * j) / 0.5)                       # first entrance, staggered
            if k_in <= 0:
                continue
            if j < cur:
                state = "done"
            elif j == cur:
                state = "cur"
            else:
                state = "next"
            pop = 0.0
            if state == "cur":
                pop = out_back((t - CH[j]) / 0.7)                        # grows into its current size
                pop = pop if t - CH[j] < 0.7 else 1.0
            elif state == "done" and j == cur - 1 or (cur == 6 and j == 5):
                pop = 1 - ss((t - CH[j + 1]) / 0.6)                      # shrinks back after its chapter
            salute = 0.0
            if cur == 6:                                                 # Ch7: all six salute in turn
                salute = math.sin(math.pi * min(max((t - CH[6] - 0.6 - 0.16 * j) / 0.5, 0.0), 1.0))
            scale = k_in * (1 + 0.32 * pop + 0.25 * salute)
            r = R * px * scale
            c.save()
            c.translate(x, y)
            # backing disc keeps the badge readable over any scene
            c.drawCircle(0, 0, r * 1.12, self.fill(C.bg, 0.82 * vis))
            if state == "next":
                c.drawCircle(0, 0, r, self.stroke(C.map_off, 0.9 * vis, 2.0))
                getattr(self, self.ICONS[j])(c, r, C.map_off, 0.85 * vis, 0.0)
            else:
                live = state == "cur"
                ph = (t - CH[j]) if live else 0.0
                c.drawCircle(0, 0, r, self.fill(col, (0.13 if live else 0.2) * vis))
                if live:
                    frac = (t - CH[j]) / (CH[j + 1] - CH[j])
                    oval = sk.Rect.MakeLTRB(-r, -r, r, r)
                    c.drawCircle(0, 0, r, self.stroke(C.map_off, 0.7 * vis, 2.4))
                    c.drawArc(oval, -90, 360 * min(frac, 1.0), False,
                              self.stroke(col, vis, 3.4, sk.Paint.kRound_Cap))
                    # the ripple when the chapter begins
                    u = (t - CH[j]) / 1.1
                    if 0 <= u < 1:
                        c.drawCircle(0, 0, r * (1 + 1.4 * ss(u)), self.stroke(col, 0.8 * (1 - u) * vis, 2.6))
                else:
                    c.drawCircle(0, 0, r, self.stroke(col, vis, 2.6))
                    u = (t - CH[j + 1]) / 0.9 if j + 1 < 7 else 1.0      # the flash on completion
                    if 0 <= u < 1:
                        c.drawCircle(0, 0, r * (1 + 0.9 * ss(u)), self.stroke(C.text, 0.7 * (1 - u) * vis, 2.0))
                getattr(self, self.ICONS[j])(c, r, col, vis, ph)
            c.restore()
        return cv.array()


_D = None


def progress(s, z: float = 60) -> None:
    """Add the tracker to scene `s` (only where its range overlaps the tracker's time on screen)."""
    global _D
    import os
    if os.environ.get("AION_NO_HUD"):
        return
    a, b = float(s.start), float(s.end)
    lo, hi = max(a, T_IN - 0.05), min(b, T_OUT + 0.8)
    if hi <= lo:
        return
    if _D is None:
        _D = _Draw()
    d = _D
    s.add(FramesLayer(d.frame, z=z, during=[(lo, hi)], parallax=0, **d.cv.layer_kw()))

    # the chapter's name, beside the row, for the first seconds of the chapter
    m = s.manim(z=z + 1, parallax=0)
    for k in range(6):
        ca = CH[k]
        cb = min(ca + LAB_S, CH[k + 1])
        if cb <= a or ca >= b:
            continue
        lab = caps(f"{k + 1}\\,/\\,6\\enspace {NAMES[PILLARS[k]]}", 30, getattr(C, PILLARS[k]))
        lab.move_to(np.array([X0 + 5 * D + R * 1.55 + 0.2, Y0, 0]), aligned_edge=LEFT)
        if ca >= a and ca + 1.0 < b:
            m.play(FadeIn(lab, shift=0.12 * LEFT), at=max(ca + 0.5, T_IN + 0.3), dur=0.5)
        else:
            m.add(lab, at=a)
        if cb < b:
            m.play(FadeOut(lab), at=cb - 0.4, dur=0.4)
