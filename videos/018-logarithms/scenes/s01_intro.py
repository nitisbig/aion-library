"""in_s01 · Napier's tables (hook). Storyboard: plan/scene_plan.md § in_s01.

1614 writes on black. Napier's printed sheets (and, beside his name, his 1616 portrait) fade up as a loose stack with soft shadows, the camera pushes in, and on
"twenty years" more sheets drop onto the pile while the year counts 1594 → 1614 under his name tag. The camera then
pulls the stack to the left third, a print of Kepler drops onto it as "astronomers" is said, and π × e is multiplied out the long way: nine partial products and a running count
of 81 single-digit multiplications. On "into an addition" the grid collapses and the lookups happen on the page itself:
each factor flies to a row, the row lights, and its logarithm rises out of the page; the two logarithms add with one
glowing +, and the sum goes back to the page for the product. 81 multiplications become 1 addition, and the three
logarithms gather into the word log. Every figure is computed here.
"""
import math

import numpy as np
from scipy.ndimage import gaussian_filter
from aion import *

from beats import T
from kit import (P3, PAGE_ROW, X0, Y1, ctex, fit, glow, log_mark, paper_page, portrait, ramp, sans, show_tag, smooth01,
                 soft_shadow, tex, tint, word_at)

A, B = 3.14159265, 2.71828183                       # π and e to nine figures
LA, LB = math.log10(A), math.log10(B)
PROD = A * B
DA, DB = 314159265, 271828183                       # the long multiplication works on the digits
CX = 3.15                                           # the equation column's centre (screen)

PH = 6.4                                            # page height (world); width is 3/4 of it
PW = PH * 0.75
STACK = (-0.6, -0.1)                                # the stack's centre (world)
CAM = ((3.4, 0.1), 0.78)                            # camera centre and zoom once the maths starts
# sheets, bottom to top: (seed, dx, dy, rotation°, brightness, land time key)
SHEETS = [(1617, -0.55, 0.28, -6.0, 0.62, "a"), (1619, 0.52, -0.22, 5.0, 0.68, "b"),
          (1621, -0.22, 0.36, -2.5, 0.74, "c"), (1623, 0.38, 0.14, 3.5, 0.80, 0),
          (1625, -0.30, -0.22, -4.0, 0.85, 1), (1627, 0.16, 0.10, 2.0, 0.90, 2), (1614, 0.0, 0.0, 0.0, 0.97, 3)]


def _shadow():
    """A soft, dark, page-sized alpha blob that sits under each sheet (it only shows where it falls on paper)."""
    w, h = 300, 400
    a = np.zeros((h + 80, w + 80), np.float32)
    a[40:-40, 40:-40] = 1
    a = gaussian_filter(a, 14) * 0.85
    img = np.zeros(a.shape + (4,), np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    return img


def _scr(x, y):
    """World → screen once the camera has settled on CAM (for overlays drawn on the page from the HUD)."""
    (cx, cy), z = CAM
    return P3((x - cx) * z, (y - cy) * z)


def _row_pt(i, col):
    """Screen point of row i on the top sheet; col 0 is the left number column, 1 the right one."""
    x = STACK[0] - PW / 2 + PW * (0.31 if col == 0 else 0.69)
    y = STACK[1] + PH / 2 - PH * (PAGE_ROW(i) - 0.008)
    return _scr(x, y)


def _long_mult():
    """The partial products of DA × DB, right-aligned and shifted one place per row, then the rule and product."""
    digits = [int(c) for c in str(DB)][::-1]
    dw = 0.161                                      # one digit's advance at size 30 (CM)
    xr = CX + 1.75
    rows = VGroup(*[tex(str(DA * d), 30, C.muted).move_to(P3(xr - i * dw, 2.02 - i * 0.29), aligned_edge=RIGHT)
                    for i, d in enumerate(digits)])
    y = 2.02 - len(digits) * 0.29
    rule = Line(P3(xr - 2.9, y + 0.1), P3(xr + 0.05, y + 0.1), stroke_color=C.muted, stroke_width=1.5)
    prod = tex(str(DA * DB), 30, C.text).move_to(P3(xr, y - 0.16), aligned_edge=RIGHT)
    return rows, VGroup(rule, prod)


@scene(T.start, T.in_s02)
def s01_intro(s):
    s.solid(C.bg, z=-200)
    t0, tn, tw = float(T.in_s01_sixteen_fourteen), float(T.in_s01_john_napier), float(T.in_s01_twenty_years)
    tl, ta = float(T.in_s01_long_multiplication), float(T.in_s01_into_an_addition)
    tlog = float(T.in_s01_logarithms)
    tg = word_at("astronomers", 10.0) - 1.6           # the grid starts while "astronomers" is said
    gone = Track(lambda t: 1 - ramp(t, tlog - 0.5, 1.0))

    # the stack of sheets, with shadows; the last four drop on during "twenty years"
    shadow = _shadow()
    for k, (seed, dx, dy, rot, dim, when) in enumerate(SHEETS):
        land = {"a": t0 + 1.1, "b": t0 + 1.45, "c": t0 + 1.8}[when] if isinstance(when, str) else tw + 0.2 + 0.5 * when
        drop = 0.0 if isinstance(when, str) else 1.0
        u = lambda t, l=land: smooth01(min(max((t - l) / 0.55, 0.0), 1.0))  # noqa: E731
        x0, y0 = STACK[0] + dx, STACK[1] + dy
        r = math.radians(rot)
        pos = Track(lambda t, x0=x0, y0=y0, u=u, d=drop: (x0, y0 + d * 0.9 * (1 - u(t))))
        rotn = Track(lambda t, r=r, u=u, d=drop: r + d * 0.08 * (1 - u(t)))
        op = Track(lambda t, u=u, d=drop: min(1.0, (5.0 if d else 1.4) * u(t)) * gone(t))
        s.add(ArrayLayer(shadow, height=PH * 1.25, z=-30 + 2 * k, rotation=rotn, opacity=op,
                         pos=Track(lambda t, p=pos: (p(t)[0] + 0.12, p(t)[1] - 0.16))))
        s.add(ArrayLayer(paper_page(seed=seed, dim=dim), height=PH, z=-29 + 2 * k, pos=pos, rotation=rotn,
                         opacity=op))
    s.camera.frame(0.0, center=(STACK[0], 0.0), zoom=1.0, dur=0.1)
    s.camera.push(tn, zoom=1.1, dur=6.5)
    s.camera.frame(tg - 0.6, center=CAM[0], zoom=CAM[1], dur=1.8)

    # 1614, the name tag, and twenty years counted out
    m0 = s.manim(z=40, parallax=0.0)
    year = tex("1614", 130, C.text).move_to(P3(0, 0.2))
    m0.play(Write(year), at=t0, dur=0.9)
    m0.play(FadeOut(year, shift=0.25 * UP, scale=0.9), at=tn + 0.25, dur=0.6)
    show_tag(s, "John Napier · 1614", C.base, tn, dur=6.2, z=41, at=P3(3.45, Y1))
    yrs = lambda t: 1594 + round(20 * smooth01(min(max((t - tw - 0.1) / 2.2, 0.0), 1.0)))  # noqa: E731
    m0.redraw(lambda t: ctex([(f"{yrs(t)}", C.base), (r"\ \text{to}\ 1614" if yrs(t) < 1614 else
                                                       r"\ \text{twenty years}", C.muted)], 30)
              .set_opacity(ramp(t, tw - 0.1, 0.4) * (1 - ramp(t, tn + 6.0, 0.5)))
              .move_to(P3(3.45, Y1 - 0.62)), during=(tw - 0.2, tn + 6.6))

    # the people: Napier's 1616 portrait beside his name; then an astronomer (Kepler, who computed with Napier's
    # tables) laid on the stack as "astronomers" is said. Both public domain (assets/images/CREDITS.md).
    def print_layer(path, h, at, out, xy, rot, drop, z, caption=None):
        img = portrait(path, height=h)
        w = h * img.shape[1] / img.shape[0]
        u = lambda t: smooth01(min(max((t - at) / 0.7, 0.0), 1.0))  # noqa: E731
        op = Track(lambda t: min(1.0, 1.6 * u(t)) * (1 - ramp(t, out, 0.6)))
        pos = Track(lambda t: (xy[0] - 0.6 * ramp(t, out, 0.6), xy[1] + drop * (1 - u(t))))
        rotn = Track(lambda t: math.radians(rot) * (1 + 0.6 * (1 - u(t))))
        sh, shh = soft_shadow(w, h, blur=0.14, a=0.85)
        s.add(ArrayLayer(sh, height=shh, z=z - 0.5, parallax=0.0, rotation=rotn, opacity=op,
                         pos=Track(lambda t: (pos(t)[0] + 0.1, pos(t)[1] - 0.14))))
        s.add(ArrayLayer(img, height=h, z=z, parallax=0.0, rotation=rotn, opacity=op, pos=pos))
        if caption:
            cap = s.manim(z=z + 0.5, parallax=0.0, opacity=op)
            cap.add(sans(caption, 22, C.muted).move_to(P3(xy[0], xy[1] - h / 2 - 0.3)))
    print_layer("assets/images/napier_1616.jpg", 3.3, tn + 0.3, tg - 0.9, (4.9, -0.55), -2.0, -0.25, 35)
    print_layer("assets/images/kepler_c1610.jpg", 3.0, word_at("astronomers", 10.0) - 0.2, ta - 0.55, (-3.05, 0.25),
                3.5, 0.5, 8)
    show_tag(s, "Johannes Kepler · astronomer", C.planet, word_at("astronomers", 10.0), dur=2.0, z=41,
             at=P3(X0, Y1))

    # π × e the long way: nine partial products, 81 single-digit multiplications
    m = s.manim(z=10, parallax=0.0)
    top = ctex([(f"{A:.8f}", C.value), (r"\times", None), (f"{B:.8f}", C.value)], 48).move_to(P3(CX, 2.75))
    m.play(FadeIn(top, shift=0.15 * DOWN), at=tg, dur=0.7)
    rows, total = _long_mult()
    r0, dr = tg + 0.6, 0.27
    for i, r in enumerate(rows):
        m.play(FadeIn(r, shift=0.1 * RIGHT), at=r0 + dr * i, dur=0.3, lead=0.0)
    m.play(Create(total[0]), FadeIn(total[1]), at=r0 + dr * 9 + 0.1, dur=0.5, lead=0.0)
    l1 = ta + 0.45
    tp = l1 + 2.2
    tc = tp + 2.4
    n_mult = lambda t: 9 * min(9, max(0, math.floor((t - r0) / dr) + 1))  # noqa: E731
    count = lambda t: ctex([(f"{n_mult(t)}", C.value), (r"\ \text{multiplications}", C.muted)], 34)  # noqa: E731
    m.redraw(lambda t: count(t).set_opacity(1 - ramp(t, tc - 0.3, 0.3)).move_to(P3(CX, -1.55)), during=(r0, tc + 0.1))

    # collapse: look each factor up on the page, add, look the sum back up
    mid = ctex([(f"{LA:.8f}", C.steps), (r"\;+\;", None), (f"{LB:.8f}", C.steps), ("=", None),
                (f"{LA + LB:.8f}", C.steps)], 38)
    mid = fit(mid, 5.4).move_to(P3(CX, 1.15))
    res = ctex([(f"{PROD:.8f}", C.value)], 54).move_to(P3(CX, -0.35))
    m.play(FadeOut(VGroup(rows, total), shift=0.4 * UP, scale=0.5), at=ta + 0.1, dur=0.6)
    bands = glow(s, C.steps, z=9, k=0.8, parallax=0.0)
    bw, bh = PW * CAM[1] * 0.86, PH / 1200 * 27 * CAM[1] * 1.05

    def lookup(src, row, col, small_txt, small_col, target, at):
        ghost = src.copy().scale(0.35).move_to(_row_pt(row, col)).set_opacity(0)
        m.play(TransformFromCopy(src, ghost), at=at, dur=0.55, lead=0.0)
        band = Rectangle(width=bw, height=bh, stroke_width=0, fill_color=C.steps, fill_opacity=0.32)
        band.move_to(_row_pt(row, 0) * [0, 1, 0] + _scr(STACK[0], 0) * [1, 0, 0])
        bands.play(FadeIn(band, scale=0.6), at=at + 0.45, dur=0.3, lead=0.0)
        small = tex(small_txt, 22, small_col).move_to(_row_pt(row, 1) + 0.02 * UP)
        m.play(FadeIn(small, scale=1.3), at=at + 0.55, dur=0.25, lead=0.0)
        m.play(ReplacementTransform(small, target), at=at + 0.85, dur=0.7, lead=0.0)
        bands.play(FadeOut(band), at=at + 1.3, dur=0.5, lead=0.0)

    lookup(top[0], 9, 0, f"{LA:.8f}", C.steps, mid[0], l1)
    lookup(top[2], 23, 0, f"{LB:.8f}", C.steps, mid[2], l1 + 0.75)
    m.play(FadeIn(mid[1], scale=1.6), at=tp, dur=0.45)
    ring = Circle(radius=0.24, stroke_color=C.text, stroke_width=2).move_to(mid[1])
    gl = glow(s, C.text, z=11, k=1.1, parallax=0.0)
    gl.play(Create(ring), at=tp + 0.1, dur=0.6)
    m.play(Write(VGroup(mid[3], mid[4])), at=tp + 0.6, dur=0.7)
    lookup(mid[4], 31, 1, f"{PROD:.8f}", C.value, res[0], tp + 1.2)

    # 81 multiplications → 1 addition
    swap = ctex([("81", C.value), (r"\ \text{multiplications}\ \longrightarrow\ ", C.muted), ("1", C.steps),
                 (r"\ \text{addition}", C.muted)], 34)
    swap = fit(swap, 5.6).move_to(P3(CX, -1.55))
    m.play(FadeIn(swap), at=tc, dur=0.6)
    m.play(FadeOut(VGroup(top, res, mid[1], mid[3], swap)), at=tlog - 0.5, dur=0.6)
    gl.play(FadeOut(ring), at=tlog - 0.5, dur=0.6)

    # the three logarithms gather into the word log
    mark = log_mark()
    logs = VGroup(mid[0], mid[2], mid[4])
    m.play(*[lg.animate.scale(0.25).move_to(mark.get_center()).set_opacity(0) for lg in logs], at=tlog - 0.2,
           dur=0.75, lead=0.0)
    m.play(Write(mark), at=tlog + 0.2, dur=0.8)
