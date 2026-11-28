"""out_s02 · The best shadow (L1, the bookend of in_s01). No text.

The shadow room returns with the lamp already on: the sculpture turns slowly through its blob views ('throws
something away'). On 'exactly what you kept' it eases into its best view (PC3 along the light): the shadow shows
the three groups and the spiral, and a gold light runs along the wire's shadow (what was kept). On 'what you lost'
a pink axis along the light runs through the sculpture and collapses into one dot on the wall (what was lost). On
'turn it to the light' the camera pushes in a little; the image holds through the end-screen tail and fades out.
Every frame is a pure function of t.
"""
import numpy as np
from aion import *
from manim import VMobject

from beats import T
from kit import (P3, ShadowRoom, blob_view, glow_layer, lin, slerp, smoothstep, turn_world, window)


@scene(T.out_s02, T.end)
def out_s02(s):
    s.solid(C.bg, z=-200)
    room = ShadowRoom(px=s.comp.size[1] / 8)
    t0, t1 = float(s.start), float(s.end)
    t_throw, t_kept = float(T.out_s02_throws_something_awa), float(T.out_s02_exactly_what_you_kep)
    t_lost, t_light = float(T.out_s02_what_you_lost), float(T.out_s02_turn_it_to_the_light)
    lead = 0.15

    # ---- orientation: a slow turn through the blob, then the ease into the best view
    I = np.eye(3)
    Rb = blob_view()
    Ra = turn_world(room, Rb, 70)
    a_best, d_best = t_kept - 0.6 - lead, 2.2

    def orient(t):
        if t < a_best:
            return slerp(Ra, Rb, smoothstep((t - t0) / (a_best - t0)))
        return slerp(Rb, I, smoothstep((t - a_best) / d_best))

    def sharp(t):
        return float(smoothstep((t - a_best) / d_best))

    shown = keys((t0, 0.0), (t0 + 1.0, 1.0), (t1 - 1.4, 1.0), (t1 - 0.1, 0.0))
    last = {}

    def draw(t):
        R, sh = orient(t), sharp(t)
        k = (np.round(R, 6).tobytes(), round(sh, 4))
        if last.get("k") != k:
            last.update(k=k, a=room.frame(R, 1.0, sh))
        return last["a"]

    s.add(FramesLayer(draw, z=-10, opacity=shown, during=[(t0, t1)],
                      fx=[Bloom(strength=0.35, threshold=0.9, radius=5, tint=C.lamp)], **room.layer_kw()))

    # ---- dust in the beam and the beam itself (as in in_s01)
    rng = np.random.default_rng(1613)
    q = []
    while len(q) < 220:
        p_ = room.LAMP + room.d * rng.uniform(4.6, 9.5) + rng.normal(0, 1.4, 3)
        v_ = p_ - room.LAMP
        if np.arccos(v_ @ room.d / np.linalg.norm(v_)) < room.CONE * 0.85 and p_[1] < room.WALL_Y - 0.2:
            q.append(p_)
    q = np.array(q)
    ph = rng.uniform(0, 2 * np.pi, (len(q), 3))

    def motes(t):
        p_ = q + 0.06 * np.sin(0.23 * t + ph) + np.array([0.0, 0.0, 0.012]) * (t - t0)
        return room.proj(p_)[0]

    s.add(PointsLayer(motes, color=C.lamp, size=1.6, glow=0.9, additive=True, z=-4, opacity=shown * 0.45, start=t0))
    apex, pool = room.lamp_screen()
    ax = (pool - apex) / np.linalg.norm(pool - apex)
    near = pool - 14.0 * ax
    s.shader("light_cone.frag", z=-5, blend="add", u_apex=tuple(map(float, near)), u_pool=tuple(map(float, pool)),
             u_half=0.30, u_amt=shown * 0.045, u_col=lin(C.lamp))

    # ---- what you kept: a gold light along the wire's shadow
    hs = room.wire_shadow_xy(I)[::3]
    lit = glow_layer(s, z=2, color=C.pc1, k=0.7, opacity=shown)
    path = VMobject(stroke_color=C.pc1, stroke_width=3.6).set_points_smoothly([P3(*p) for p in hs])
    lit.play(Create(path), at=t_kept + 0.5, dur=1.9, ease="smooth")
    lit.play(path.animate.set_stroke(opacity=0.0), at=t_lost + 1.8, dur=0.6)
    lit.remove(path, at=t_lost + 2.5)

    # ---- what you lost: the axis along the light collapses into one dot on the wall
    W, _ = room.on_wall(room.CENTRE)
    w_xy = P3(*room.proj(W)[0])
    h = 0.6
    t_col = t_lost + 1.2

    def axis(t):
        grow = smoothstep((t - (t_lost - lead)) / 0.7)
        u = smoothstep((t - (t_col - lead)) / 1.3)
        a = room.CENTRE - h * grow * room.d
        b = room.CENTRE + h * grow * room.d
        a, b = a + u * (W - a), b + u * (W - b)
        pa, pb = (P3(*room.proj(p)[0]) for p in (a, b))
        fade_out = 1 - smoothstep((t - (t_light - 0.2)) / 0.8)
        g = VGroup()
        if u < 0.999:
            far = P3(*room.proj(room.CENTRE - 2.6 * room.d)[0])
            g.add(DashedLine(far, w_xy, stroke_color=C.lamp, stroke_width=1.8, dash_length=0.1,
                             stroke_opacity=0.7 * grow * (1 - u)))
            g.add(Line(pa, pb, stroke_color=C.residual, stroke_width=5.0, stroke_opacity=grow))
        r = 0.06 + 0.03 * u
        g.add(Circle(radius=r, stroke_width=0, fill_color=C.residual, fill_opacity=grow * fade_out).move_to(w_xy))
        g.add(Circle(radius=r + 0.07, stroke_color=C.residual, stroke_width=2.0,
                     stroke_opacity=0.8 * grow * fade_out).move_to(w_xy))
        return g

    top = s.manim(z=3)
    top.redraw(window(axis, t_lost - lead, t_light + 0.7), during=(t_lost - lead, t_light + 0.7))

    # ---- 'turn it to the light': a slow push in, held through the tail
    s.camera.frame(t_light, center=(0.35, -0.05), zoom=1.05, dur=3.0)
