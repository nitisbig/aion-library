"""ch1_s01 · The tight leash (Chapter 1 hook).

THE circle from the intro fades; a post appears, seen from above, and a dog on a leash noses around it with the leash
slack. On 'pulls' the leash snaps tight and the dog runs round, a paw-print dot dropped every tenth of a second; a few
spots out of reach are crossed out. On 'exactly one' a dimension line rides along the leash: one leash length. On
'Gather' the prints slide onto the circle they were always on; the dog sits. Under it the word 'shape' turns into
'rule' on 'rule'.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import glow_layer, paw, P3, R1, dog, leash, post, sans, the_circle, window

TP0 = 0.35                                   # first heading once the leash is tight (radians)


@scene(T.ch1_s01, T.ch1_s02)
def ch1_s01(s):
    s.solid(C.bg, z=-200)
    progress(s)
    m, top = s.manim(z=0), s.manim(z=1)
    t0, t_post, t_pull = float(s.start), float(T.ch1_s01_post), float(T.ch1_s01_pulls)
    t_one, t_gat, t_rule = float(T.ch1_s01_exactly_one), float(T.ch1_s01_gather), float(T.ch1_s01_rule)
    t_sit = t_gat + 0.2                                           # the dog stops where it is

    old = the_circle(fill_color=C.bg, fill_opacity=1.0)          # the intro's circle gives way
    m.add(old)
    m.play(FadeOut(old, scale=0.8), at=t0 + 0.2, dur=0.8)
    p = post()
    m.play(GrowFromCenter(p), at=t_post - 0.6, dur=0.5, ease="out_back")

    tt = t_pull + 0.15                                            # leash fully tight

    def theta(t):
        """Dog's angle around the post: wandering while slack, running (never backwards) once tight."""
        if t < tt:
            return TP0 - 0.5 + 0.5 * math.sin(0.7 * (t - t_post))
        u = min(t, t_sit) - tt
        return TP0 + 0.95 * u + 0.6 * math.sin(0.45 * u)

    def radius(t):
        slackr = R1 * (0.55 + 0.12 * math.sin(1.3 * (t - t_post)))
        k = min(max((t - t_pull + 0.25) / 0.4, 0.0), 1.0)
        return slackr + (R1 - slackr) * k * k * (3 - 2 * k)

    def where(t):
        a, r = theta(t), radius(t)
        return P3(r * math.cos(a), r * math.sin(a))

    def heading(t):
        d = where(t + 0.03) - where(t - 0.03)
        return math.atan2(d[1], d[0]) if np.linalg.norm(d) > 1e-4 else theta(t) + math.pi / 2

    prints_t = np.arange(tt + 0.2, t_sit, 0.1)

    def print_dot(tk, op=1.0):
        k = int(round((tk - prints_t[0]) / 0.1))
        return paw(where(tk), heading(tk), 1.0 if k % 2 else -1.0, opacity=op)

    def scene_at(t, prints=True, dimline=True):
        g = VGroup()
        a = min(1.0, (t - t_post + 0.4) / 0.5)
        if a <= 0:
            return g
        for tk in prints_t[prints_t <= t] if prints else []:                         # paw prints, oldest faintest
            g.add(print_dot(tk, max(0.35, 1 - (t - tk) / 10)))
        w = where(t)
        slack = 1 - min(max((t - t_pull + 0.25) / 0.4, 0.0), 1.0)
        collar = w - 0.02 * P3(math.cos(heading(t)), math.sin(heading(t)))
        g.add(leash(ORIGIN, collar, slack=slack * 0.9, side=1.0).set_stroke(opacity=a), dog(w, heading(t), a, phase=None if t >= t_sit else 11.0 * (t - t_post)))
        if dimline and t_one - 0.15 <= t:                                       # the dimension line along the leash
            k = min(1.0, (t - t_one + 0.15) / 0.4)
            u = w / np.linalg.norm(w)
            n = P3(-u[1], u[0])
            off = 0.45 * n
            g.add(Line(off, off + R1 * u * k, stroke_color=C.muted, stroke_width=1.6),
                  Line(off - 0.09 * n, off + 0.09 * n, stroke_color=C.muted, stroke_width=1.6))
            if k >= 1:
                g.add(Line(off + R1 * u - 0.09 * n, off + R1 * u + 0.09 * n, stroke_color=C.muted, stroke_width=1.6))
        return g

    t_end_live = t_gat
    top.redraw(window(lambda t: scene_at(t, prints=False), t_post - 0.45, t_end_live),
               during=(t_post - 0.45, t_end_live + 0.05))
    trail = glow_layer(s, z=0.6, color=C.foundations, k=0.8)                    # the prints glow, a trail of light

    def prints_at(t):
        return VGroup(*(print_dot(tk, max(0.35, 1 - (t - tk) / 10)) for tk in prints_t[prints_t <= t]))

    trail.redraw(window(prints_at, t_post - 0.45, t_end_live), during=(t_post - 0.45, t_end_live + 0.05))

    # 'one leash length': the label rides beside the dimension line, kept upright
    def label(t):
        w = where(t)
        u = w / np.linalg.norm(w)
        n = P3(-u[1], u[0])
        lab = sans("one leash length", 28, C.text)
        lab.move_to(0.5 * R1 * u + (0.45 + 0.22 + 0.5 * abs(u[1]) * lab.width / 2 + 0.2) * n)
        k = min(1.0, (t - t_one - 0.25) / 0.4)
        return lab.set_opacity(max(k, 0.0))

    top.redraw(window(label, t_one, t_end_live), during=(t_one, t_end_live + 0.05))

    # 'not just anywhere': spots out of reach are crossed out
    t_any = float(T.ch1_s01_pulls) + 3.4
    rg = np.random.default_rng(1511)
    crosses = VGroup()
    for _ in range(5):
        a, r = rg.uniform(0, 2 * math.pi), rg.uniform(R1 + 0.5, R1 + 1.4)
        c = P3(r * math.cos(a), r * math.sin(a) * 0.85)
        crosses.add(VGroup(Line(c + P3(-0.1, -0.1), c + P3(0.1, 0.1)), Line(c + P3(-0.1, 0.1), c + P3(0.1, -0.1)))
                    .set_stroke(C.muted, 2.2))
    m.play(LaggedStart(*(FadeIn(x, scale=0.5) for x in crosses), lag_ratio=0.25), at=t_any, dur=1.2)
    m.play(FadeOut(crosses), at=t_any + 3.0, dur=0.6)

    # 'Gather': the paw prints slide onto the circle; the dog sits and leaves
    dots = VGroup(*(print_dot(tk) for tk in prints_t))
    frozen = scene_at(t_end_live, prints=False, dimline=False)
    trail.add(dots, at=t_end_live)
    top.add(frozen, at=t_end_live)
    circle = the_circle(R1, fill_color=C.bg, fill_opacity=0.0)
    a0 = TP0 + math.pi                                     # draw the circle starting opposite the dog's first print
    circle.rotate(a0)
    m.play(Create(circle), at=t_gat + 0.1, dur=1.0, ease="easy_ease")
    trail.play(FadeOut(dots), at=t_gat + 0.6, dur=0.7)
    top.play(FadeOut(frozen), at=t_gat + 2.2, dur=0.8)

    # 'from a shape we recognize to a rule we can check'
    shape_w = sans("shape", 40, C.muted).move_to(P3(0, -R1 - 0.7))
    rule_w = sans("rule", 40, C.foundations).move_to(P3(0, -R1 - 0.7))
    m.play(FadeIn(shape_w, shift=0.1 * UP), at=t_rule - 1.4, dur=0.5)
    m.play(ReplacementTransform(shape_w, rule_w), at=t_rule, dur=0.6)
    m.play(FadeOut(rule_w), at=s.end - 0.5, dur=0.45)
