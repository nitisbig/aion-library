"""out_s01 · One web (recap). Storyboard: plan/scene_plan.md § out_s01. Layout L4.

Opens on c10_s03's last frame (the value surface flattened into a small contour map). 'handed': the ten tiles
(each chapter's key frame, outro.py) lift out of the centre onto a rising ring of cards that turns slowly. On each
link the narration names, a lit arc in the destination's hue draws from one card to the next and that card lights:
T1 → T2 on 'gravity' … T9 → T10 on 'markets', where the camera rises to see the whole chain. 'Ten equations': the
ring settles into the 5x2 wall, each tile's name and equation appear under it, and 'Ten equations · 1763 – 1973'
settles above. The progress rail leaves.
"""
import math

import numpy as np
from aion import *

import ch10
import outro as O
from beats import T
from ch7 import Cam, FOCAL
from kit import P3, add_rail, caps, glow, polyline, smooth01
from theme import CHAPTERS

LINKS = ["gravity", "atom", "water", "frequencies", "clocks", "learning", "noisy_wires", "evidence", "markets"]


def _carry(s, out):
    """c10_s03's last frame: the contour map seen from straight above, far off."""
    cam = Cam(target=(0.0, 0.0, 0.0), yaw=-math.pi / 2, pitch=math.radians(89.5), dist=10.5 * 3.2, f=FOCAL,
              off=(0.0, 0.0))
    unif = ch10.surf_uniforms(lambda t: cam, 0.0, fade(float(s.start) - 5, dur=0.1, out=out, out_dur=0.6))
    unif["u_dom"] = 3.3
    s.shader("hill.frag", z=0, parallax=0.0, animated=True, **unif)


@scene(T.out_s01, T.out_s02)
def s34_out_web(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_h, t_te = float(T.out_s01_handed), float(T.out_s01_ten_equations)
    t_link = [float(getattr(T, f"out_s01_{w}")) for w in LINKS]
    t_mk = t_link[-1]
    _carry(s, t_h + 0.2)
    add_rail(s, 10, opacity=fade(t0 - 5, dur=0.1, out=t_h + 0.3, out_dur=1.0))

    rot = lambda t: 0.36 - 0.035 * (t - t_h)                                        # the ring turns slowly
    pitch = lambda t: 0.2 + 0.28 * float(smooth01((t - t_mk) / 2.2))            # and the camera rises on 'markets'
    lift = lambda t: 0.0
    t_lit = [t_link[0] - 1.6] + [tl + 0.6 for tl in t_link]                     # when each card lights

    def place(i):
        def f(t):
            hx, hy, hk, hd = O.helix(i, rot(t), pitch(t), lift(t))
            u = float(smooth01((t - t_h - 0.1 * i) / 1.3))                       # lift out of the centre
            x, y, k = hx * u, hy * u, 0.06 + (hk - 0.06) * u
            w = float(smooth01((t - t_te + 0.3 - 0.05 * i) / 1.6))              # settle into the wall
            wx, wy = O.wall(i)
            return x + (wx - x) * w, y + (wy - y) * w, k + (1.0 - k) * w, hd * (1 - w) + 10 * w
        return f

    def card_op(i):
        def f(t):
            a = float(smooth01((t - t_h - 0.1 * i) / 0.6))
            lit = float(smooth01((t - t_lit[i]) / 0.5))
            settle = float(smooth01((t - t_te) / 1.2))
            return a * (0.32 + 0.68 * max(lit, settle))
        return f
    t_mid = (t_link[0] + t_mk) / 2
    for i in range(10):                                                         # nearer cards on top (mid-ring)
        O.tile_layer(s, i, place(i), Track(card_op(i)), z=20 - place(i)(t_mid)[3])

    # the links: an arc in the destination's hue from card i to card i + 1
    a_op = fade(t0, dur=0.1, out=t_te - 0.1, out_dur=0.7)
    for i in range(9):
        hue = getattr(C, CHAPTERS[i + 1])
        ta = t_link[i] - 0.15

        def arc(t, i=i, ta=ta, hue=hue):
            u = float(smooth01((t - ta) / 0.9))
            a = float(a_op(t))
            if u <= 0 or a < 0.01:
                return VGroup()
            pts = O.arc_pts(i, rot(t), pitch(t), lift(t))
            k = max(int(u * (len(pts) - 1)), 1)
            return polyline(pts[:k + 1], hue, 2.6, a * (1.0 - 0.35 * float(smooth01((t - ta - 1.6) / 1.0))))
        glow(s, hue, z=45, k=0.7, parallax=0.0).redraw(arc, during=(ta, t_te + 0.7))

    # ten equations: names, equations and the closing line
    lab = s.manim(z=50, parallax=0.0)
    lab.play(FadeIn(VGroup(*[O.wall_labels(i) for i in range(10)]), lag_ratio=0.06), at=t_te + 1.1, dur=1.6)
    lab.play(FadeIn(caps("Ten equations · 1763 – 1973", 36, C.text).move_to(P3(0, 3.2)), shift=0.08 * DOWN),
             at=t_te + 2.2, dur=0.9)
