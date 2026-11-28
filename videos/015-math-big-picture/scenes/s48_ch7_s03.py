"""ch7_s03 · The sticks, retold.

A small floor of sticks sits inside the hub (crossings pink). Each line then puts one piece of Buffon's answer in the
hub, in its branch's color, and a spoke runs from the hub to that node: Definitions, the crossing condition as a set
(C.foundations); Symmetry, directions turning evenly (C.structure), and the chord Structure–Uncertainty draws, the
fifteenth; Geometry, the rectangle of throws (C.space); Calculus, the area under the arch (C.change); Probability,
P = 2/π (C.uncertainty); 'out came pi', π = 3.14159… (C.quantity). On 'alone' all six nodes pulse together.
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import glow_layer, window, HUB_R, NODE_R, P3, PILLARS, arch_region, hue, map_state, node_xy, sans, sine_arch, tex, the_circle

ALL = PILLARS
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"), ("structure", "space"),
         ("quantity", "space"), ("space", "change"), ("quantity", "change"), ("change", "uncertainty"),
         ("space", "uncertainty"), ("quantity", "uncertainty"), ("foundations", "space"), ("foundations", "change"),
         ("foundations", "uncertainty"), ("structure", "change"))
NEW = (("structure", "uncertainty"),)
MO, MSX, MSY = P3(-0.95, -0.42), 1.9 / math.pi, 0.84       # the mini rectangle in the hub


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch7_s03, T.ch7_s04)
def ch7_s03(s):
    s.solid(C.bg, z=-200)
    lnk, sp_l, nd, m, top = glow_layer(s, z=-3, k=0.55), s.manim(z=-2), s.manim(z=-1), s.manim(z=0), s.manim(z=1)
    t0, t1 = float(s.start), float(s.end)
    t_all, t_df, t_sy = float(T.ch7_s03_all_of_it), float(T.ch7_s03_definitions), float(T.ch7_s03_symmetry)
    t_ge, t_ca, t_pr = float(T.ch7_s03_geometry), float(T.ch7_s03_calculus), float(T.ch7_s03_probability)
    t_pi, t_al = float(T.ch7_s03_out_came_pi), float(T.ch7_s03_alone)

    links, nodes = map_state(0, lit=ALL, edges=EDGES)
    hub = the_circle(fill_color=C.bg, fill_opacity=1.0)
    lnk.add(links)
    nd.add(nodes)
    m.add(hub)

    # the floor, in the hub
    rg = np.random.default_rng(1777)
    boards = VGroup()
    for y in np.arange(-0.9, 0.91, 0.3):
        hw = math.sqrt(max(1.22 ** 2 - y * y, 0))
        boards.add(Line(P3(-hw, y), P3(hw, y), stroke_color=C.map_off, stroke_width=1.6))
    sticks = VGroup()
    while len(sticks) < 34:
        c_ = rg.uniform(-1.0, 1.0, 2)
        if c_ @ c_ > 0.95 ** 2:
            continue
        th = rg.uniform(0, math.pi)
        d = 0.15 * np.array([math.cos(th), math.sin(th)])
        dist = abs(c_[1] - 0.3 * round(c_[1] / 0.3))
        hit = dist <= 0.15 * math.sin(th)
        sticks.add(Line(P3(*(c_ - d)), P3(*(c_ + d)), stroke_color=C.uncertainty if hit else C.muted, stroke_width=3))
    top.play(FadeIn(boards), at=t_all - 1.6, dur=0.5)
    top.play(LaggedStart(*(FadeIn(st, scale=1.6) for st in sticks), lag_ratio=0.04), at=t_all - 1.2, dur=1.4)
    floor = VGroup(boards, sticks)

    # a spoke from the hub to node k
    def spoke(k, at):
        q = node_xy(k)
        u = q / np.linalg.norm(q)
        ln = Line(u * (HUB_R + 0.04), q - u * (NODE_R + 0.03), stroke_color=hue(PILLARS[k]), stroke_width=7)
        sp_l.play(Create(ln), at=at - 0.1, dur=0.45)
        sp_l.play(ln.animate.set_stroke(width=3.5, opacity=0.7), at=at + 1.4, dur=0.6)
        return ln

    spokes = []
    pieces = []

    # Definitions: the crossing condition, as a set
    p1 = tex(r"\{(\theta, x) : x \le \sin\theta\}", 30, C.foundations)
    top.play(FadeOut(floor), at=t_df - 0.4, dur=0.4)
    top.play(FadeIn(p1, shift=0.06 * UP), at=t_df, dur=0.5)
    spokes.append(spoke(0, t_df))
    pieces.append((p1, t_sy - 0.45))

    # Symmetry: every direction equally likely; the fifteenth chord
    def fan(t):
        f = ss((t - t_sy + 0.1) / 0.4) * (1 - ss((t - t_ge + 0.45) / 0.35))
        if f <= 0:
            return VGroup()
        a0 = (math.pi / 3) * min(max((t - t_sy - 0.3) / 2.6, 0.0), 1.0)
        return VGroup(*(Line(ORIGIN, P3(math.cos(a), math.sin(a)), stroke_color=C.structure, stroke_width=3,
                             stroke_opacity=f) for a in a0 + np.arange(12) * math.pi / 6))

    top.redraw(window(fan, t_sy - 0.1, t_ge), during=(t_sy - 0.1, t_ge + 0.05))
    spokes.append(spoke(2, t_sy))
    new_edge = map_state(0, edges=NEW)[0][1][0]
    lnk.play(Create(new_edge), at=t_sy + 0.6, dur=0.8)

    # Geometry: the rectangle of throws
    frame = Rectangle(width=MSX * math.pi, height=MSY, stroke_color=C.space, stroke_width=2.6).move_to(
        MO + P3(MSX * math.pi / 2, MSY / 2))
    r3 = np.random.default_rng(5)
    dots = VGroup(*(Dot(MO + P3(MSX * a, MSY * b), radius=0.032, color=C.text) for a, b in
                    zip(r3.uniform(0, math.pi, 70), r3.uniform(0, 1, 70))))
    top.play(Create(frame), at=t_ge - 0.1, dur=0.5)
    top.play(LaggedStart(*(FadeIn(d_) for d_ in dots), lag_ratio=0.02), at=t_ge + 0.3, dur=1.2)
    spokes.append(spoke(3, t_ge))

    # Calculus: the area under the arch
    region = arch_region(MO, MSX, MSY, opacity=0.35)
    arch = sine_arch(MO, MSX, MSY, width=3.4)
    top.play(FadeIn(region), Create(arch), at=t_ca - 0.1, dur=0.7)
    under = VGroup(*(d_ for d_ in dots if (d_.get_center()[1] - MO[1]) / MSY <= math.sin(
        (d_.get_center()[0] - MO[0]) / MSX)))
    spokes.append(spoke(4, t_ca))
    pieces.append((VGroup(frame, dots, region, arch), t_pr - 0.45))

    # Probability: the share
    top.play(under.animate.set_color(C.uncertainty), at=t_ca + 1.0, dur=0.5)
    p5 = MathTex("P", "=", r"\frac{2}{\pi}", font_size=48, color=C.text)
    p5[0].set_color(C.uncertainty)
    p5[2][0].set_color(C.change)
    p5[2][2].set_color(C.quantity)
    top.play(FadeIn(p5, shift=0.06 * UP), at=t_pr, dur=0.5)
    spokes.append(spoke(5, t_pr))
    pieces.append((p5, t_pi - 0.45))

    # 'out came pi'
    p6 = VGroup(tex(r"\pi", 84, C.quantity), tex(r"3.14159\ldots", 30, C.quantity)).arrange(DOWN, buff=0.12)
    top.play(FadeIn(p6, scale=1.2), at=t_pi, dur=0.6)
    spokes.append(spoke(1, t_pi))

    for p_, te in pieces:
        top.play(FadeOut(p_), at=te, dur=0.35)

    # 'alone': all six together
    nd.play(*(n_.animate(rate_func=there_and_back).scale(1.2) for n_ in nodes), at=t_al - 0.3, dur=0.8)
    sp_l.play(*(sk.animate(rate_func=there_and_back).set_stroke(width=7, opacity=1.0) for sk in spokes),
              at=t_al - 0.3, dur=0.8)
    top.play(FadeOut(p6), at=t1 - 0.5, dur=0.4)
    sp_l.play(*(FadeOut(sk) for sk in spokes), at=t1 - 0.5, dur=0.4)
