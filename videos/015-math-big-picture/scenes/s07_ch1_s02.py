"""ch1_s02 · A set is a rule.

The circle breaks into its points and set braces close round them. The rule appears under it (d = ℓ: distance from the
post equals the leash). On 'every possible' the whole plane fills with sample points and a scan line sweeps across:
each point it passes is judged, and everything off the circle dims. On 'partly' a magnifier opens on the edge: one
point exactly on the circle turns blue (in), one a hair away turns grey (out); no third option. On 'slack' the rule
becomes d ≤ ℓ, the dog wanders inside on a loose leash and the set floods out from the post to the whole disk. On
'exactly' the flood drains back and only the ring of points is left.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import P3, R1, dog, leash, post, sans, set_braces, tex, the_circle, tint, window

N_RING = 64
SPACING = 0.34


@scene(T.ch1_s02, T.ch1_s03)
def ch1_s02(s):
    s.solid(C.bg, z=-200)
    progress(s)
    under, m, top = s.manim(z=-2), s.manim(z=0), s.manim(z=2)
    t_set, t_every, t_part = float(T.ch1_s02_set), float(T.ch1_s02_every_possible), float(T.ch1_s02_partly)
    t_slack, t_exact = float(T.ch1_s02_slack), float(T.ch1_s02_exactly)

    circle = the_circle(R1)
    p = post()
    m.add(circle, p)

    # 'set': the circle breaks into points; braces close around them
    ring = VGroup(*(Dot(R1 * P3(math.cos(a), math.sin(a)), radius=0.05, color=C.foundations)
                    for a in np.linspace(0, 2 * math.pi, N_RING, endpoint=False)))
    m.play(LaggedStart(*(GrowFromCenter(d) for d in ring), lag_ratio=0.02), at=t_set - 0.3, dur=1.0)
    m.play(circle.animate.set_stroke(opacity=0.25, width=2.5), at=t_set - 0.1, dur=0.8)
    br = set_braces(2 * R1 + 0.9, 2 * R1 + 1.0)
    wide = set_braces(2 * R1 + 0.9, 2 * R1 + 3.4).set_opacity(0)
    m.add(wide, at=t_set)
    m.play(Transform(wide, br), at=t_set + 0.3, dur=0.8, ease="out_cubic")

    # the rule under the set
    rule_eq = tex(r"d = \ell", 40, C.foundations)
    rule_le = tex(r"d \le \ell", 40, C.foundations)
    rule_lab = sans("rule", 30, C.muted)
    rule_eq.move_to(P3(0.35, -R1 - 0.95))
    rule_le.move_to(rule_eq)
    rule_lab.next_to(rule_eq, LEFT, buff=0.35)
    t_rule = t_set + 3.0                                          # 'defined by a rule'
    m.play(FadeIn(rule_lab), FadeIn(rule_eq, shift=0.1 * UP), at=t_rule, dur=0.5)

    # 'every possible point': sample points over the plane; a scan line judges each one
    xs = np.arange(-7.0, 7.01, SPACING)
    ys = np.arange(-3.74, 3.75, SPACING)
    G = np.array([(x, y) for y in ys for x in xs])
    rG = np.hypot(G[:, 0], G[:, 1])
    G = G[np.abs(rG - R1) > 0.12]
    G = G[~((np.abs(G[:, 0] - 0.0) < 1.7) & (np.abs(G[:, 1] + R1 + 0.95) < 0.4))]          # clear of the rule
    G = G[~((np.abs(G[:, 0]) < 1.1) & (np.abs(G[:, 1] - R1 - 0.95) < 0.35))]               # clear of 'in  out'
    rG = np.hypot(G[:, 0], G[:, 1])
    t_s0, t_s1 = t_every + 0.1, t_every + 2.4

    def scan_x(t):
        u = min(max((t - t_s0) / (t_s1 - t_s0), 0.0), 1.0)
        return -7.4 + 14.8 * (u * u * (3 - 2 * u))

    def flood(t):
        """Radius the disk set has reached: grows out from the post after 'slack', drains after 'exactly'."""
        a = min(max((t - t_slack - 0.6) / 1.6, 0.0), 1.0)
        b = min(max((t - t_exact - 0.3) / 1.0, 0.0), 1.0)
        return (R1 + 0.2) * (a * a * (3 - 2 * a)) * (1 - b * b * (3 - 2 * b))

    def values(t):
        sx = scan_x(t)
        v = np.where(G[:, 0] < sx, 0.08, 0.5)                    # judged: out (dark) · not yet judged (grey)
        near = np.clip(1 - (sx - G[:, 0]) / 0.5, 0, 1) * (G[:, 0] < sx)
        v = v + 0.25 * near                                       # a brief flash as the line passes
        f = flood(t)
        if f > 0:
            v = np.where(rG < f, 0.95, v)
        return v.astype(np.float32)

    on = fade(t_every - 0.5, dur=0.6, out=s.end - 1.0, out_dur=0.8)
    s.add(PointsLayer(lambda t: G, values=values, cmap="diverging", vmin=0.0, vmax=1.0,
                      colors=(C.bg, C.muted, C.foundations), size=4.5, glow=0.0, additive=False, opacity=on,
                      z=-1, start=t_every - 0.6, end=float(s.end)))

    def scan(t):
        sx = scan_x(t)
        k = min(1.0, (t - t_s0 + 0.1) / 0.2, (t_s1 + 0.25 - t) / 0.25)
        return Line(P3(sx, -4.1), P3(sx, 4.1), stroke_color=C.foundations, stroke_width=2.4, stroke_opacity=max(k, 0))

    top.redraw(window(scan, t_s0 - 0.1, t_s1 + 0.25), during=(t_s0 - 0.1, t_s1 + 0.3))
    inout = VGroup(sans("in", 30, C.foundations), sans("out", 30, C.muted)).arrange(RIGHT, buff=0.5)
    inout.move_to(P3(0, R1 + 0.95))
    m.play(FadeIn(inout[0], shift=0.08 * UP), at=float(T.ch1_s02_every_possible) + 1.3, dur=0.4)
    m.play(FadeIn(inout[1], shift=0.08 * UP), at=float(T.ch1_s02_every_possible) + 2.2, dur=0.4)
    m.play(FadeOut(inout), at=t_part + 3.4, dur=0.5)

    # 'no partly in': a magnifier on the edge
    a_q = math.radians(38)
    q = R1 * P3(math.cos(a_q), math.sin(a_q))
    pc, mag, pw, ph = P3(5.0, 1.9), 6.0, 3.3, 2.3
    lens = Square(0.42, stroke_color=C.text, stroke_width=1.8).move_to(q)
    panel = Rectangle(width=pw, height=ph, stroke_color=C.text, stroke_width=1.8, fill_color=C.bg, fill_opacity=1)
    panel.move_to(pc)
    links = VGroup(Line(lens.get_corner(UR), panel.get_corner(UL), stroke_color=C.muted, stroke_width=1.2),
                   Line(lens.get_corner(DR), panel.get_corner(DL), stroke_color=C.muted, stroke_width=1.2))
    angs = np.linspace(a_q - 0.2, a_q + 0.2, 60)
    arc_pts = [pc + mag * (R1 * P3(math.cos(a), math.sin(a)) - q) for a in angs]
    arc_pts = [x for x in arc_pts if abs(x[0] - pc[0]) < pw / 2 - 0.05 and abs(x[1] - pc[1]) < ph / 2 - 0.05]
    arc = VMobject(stroke_color=C.circle, stroke_width=3).set_points_smoothly(arc_pts)
    nrm = P3(math.cos(a_q), math.sin(a_q))
    tan = P3(-math.sin(a_q), math.cos(a_q))
    on_pt = Dot(pc - 0.55 * tan, radius=0.09, color=C.text)
    off_pt = Dot(pc + 0.55 * tan + 0.16 * nrm, radius=0.09, color=C.text)
    qm = VGroup(tex("?", 34, C.text).next_to(on_pt, -nrm + 0.2 * UP, buff=0.12),
                tex("?", 34, C.text).next_to(off_pt, nrm, buff=0.12))
    zoom = VGroup(panel, arc, on_pt, off_pt)
    top.play(Create(lens), at=t_part - 0.6, dur=0.4)
    top.play(Create(links), GrowFromPoint(zoom, q), at=t_part - 0.3, dur=0.6, ease="easy_ease")
    top.play(FadeIn(qm), at=t_part + 0.2, dur=0.3)
    lab_in = sans("in", 28, C.foundations).move_to(qm[0])
    lab_out = sans("out", 28, C.muted).move_to(qm[1])
    top.play(on_pt.animate.set_color(C.foundations), ReplacementTransform(qm[0], lab_in), at=t_part + 0.9, dur=0.4)
    top.play(off_pt.animate.set_color(C.map_off), ReplacementTransform(qm[1], lab_out), at=t_part + 1.3, dur=0.4)
    zoom_all = VGroup(lens, links, zoom, lab_in, lab_out)
    top.play(FadeOut(zoom_all), at=t_slack - 2.2, dur=0.6)

    # 'slack': the rule loosens to d ≤ ℓ; the dog wanders inside; the disk floods out from the post
    m.play(TransformMatchingTex(rule_eq, rule_le), at=t_slack, dur=0.6)
    disk = Circle(radius=R1, stroke_width=0, fill_color=tint(C.foundations, 0.2), fill_opacity=1)

    def disk_at(t):
        f = min(flood(t), R1)
        if f < 0.02:
            return VGroup()
        return Circle(radius=f, stroke_width=0, fill_color=tint(C.foundations, 0.2), fill_opacity=1)

    under.redraw(window(disk_at, t_slack, t_exact + 1.5), during=(t_slack, t_exact + 1.55))

    t_d0, t_d1 = t_slack - 0.6, t_exact + 0.9

    def dog_at(t):
        u = t - t_d0
        w = P3(0.62 * R1 * math.sin(0.55 * u + 0.4), 0.5 * R1 * math.sin(0.83 * u + 1.7))
        d = P3(0.62 * R1 * 0.55 * math.cos(0.55 * u + 0.4), 0.5 * R1 * 0.83 * math.cos(0.83 * u + 1.7))
        h = math.atan2(d[1], d[0])
        k = min(1.0, (t - t_d0) / 0.5, (t_d1 - t) / 0.5)
        sl = 0.35 + 0.5 * (1 - np.linalg.norm(w) / R1)
        return VGroup(leash(ORIGIN, w, slack=sl, side=1.0).set_stroke(opacity=max(k, 0)), dog(w, h, max(k, 0)))

    top.redraw(window(dog_at, t_d0, t_d1), during=(t_d0, t_d1 + 0.05))

    # 'exactly': the flood drains, the rule tightens back, only the circle's points remain
    rule_eq2 = tex(r"d = \ell", 40, C.foundations).move_to(rule_le)
    m.play(TransformMatchingTex(rule_le, rule_eq2), at=t_exact, dur=0.6)
    m.play(ring.animate.scale(1.0).set_color(C.foundations), at=t_exact + 0.6, dur=0.3)

    # hand-off: braces, rule and dots give the circle back for the grid
    t_out = float(s.end) - 1.0
    m.play(FadeOut(wide), FadeOut(rule_lab), FadeOut(rule_eq2), at=t_out, dur=0.7)
    m.play(FadeOut(ring), circle.animate.set_stroke(opacity=1.0, width=5.0), at=t_out + 0.2, dur=0.7)
