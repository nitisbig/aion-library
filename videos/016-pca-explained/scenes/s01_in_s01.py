"""in_s01 · The shadow (the video's first scene, L1). No text.

A sculpture hangs in a dark room: three bunches of glass beads (sapphire, ruby, emerald) threaded by a gold spiral
wire (pcadata.beads). A warm lamp off frame left flickers on; dust drifts in its beam; the sculpture's shadow falls
on a plaster wall above a floor (kit.ShadowRoom: shadows cast by geometry, glass throws coloured caustics, a little
bloom on the speculars). It turns a little: the shadow changes but stays a tangled blob. On 'one direction' it eases
into its best view (PC3 along the light): the shadow shows three coloured groups with the spiral through them, and
on 'spiral' a gold light runs along the wire's shadow. On 'flat' a pink axis
along the light runs through the sculpture: its shadow is one dot, and it collapses into that dot (a dimension thrown
away). On 'least' the camera pushes in a little on the shadow. Every frame is a pure function of t.
"""
import numpy as np
from aion import *
from manim import VMobject

from beats import T
from kit import (ShadowRoom, blob_view, glow_layer, lin, slerp, smoothstep, turn_world, window, P3)


@scene(T.start, T.in_s02)
def in_s01(s):
    s.solid(C.bg, z=-200)
    room = ShadowRoom(px=s.comp.size[1] / 8)
    t0, t1 = float(s.start), float(s.end)
    t_lamp, t_turn, t_blob = float(T.in_s01_lamp), float(T.in_s01_turn), float(T.in_s01_blob)
    t_one, t_three, t_spi = float(T.in_s01_one_direction), float(T.in_s01_three_separate_group), float(T.in_s01_spiral)
    t_flat, t_least = float(T.in_s01_flat), float(T.in_s01_least)
    t_throw = t_flat + 1.82                     # 'throws a dimension away'
    lead = 0.15

    # ---- orientation: still, a slow turntable turn into the blob, then the ease into the best view
    I = np.eye(3)
    Rb = blob_view()
    Ra = turn_world(room, Rb, -55)
    a_turn, b_turn = t_turn - lead, t_blob + 0.8
    a_best, d_best = t_one - lead, 2.0

    def orient(t):
        if t < a_best:
            return slerp(Ra, Rb, smoothstep((t - a_turn) / (b_turn - a_turn)))
        return slerp(Rb, I, smoothstep((t - a_best) / d_best))

    def sharp(t):
        return float(smoothstep((t - a_best) / d_best))

    tl = t_lamp - lead                                     # the lamp flickers on, then settles
    lamp = keys((tl, 0.0), (tl + 0.05, 0.75), (tl + 0.11, 0.12), (tl + 0.2, 0.9), (tl + 0.27, 0.45),
                (tl + 0.36, 0.95), (tl + 1.1, 1.0), default_ease="linear")
    shown = keys((t0, 0.0), (t0 + 0.8, 1.0), (t1 - 0.9, 1.0), (t1 - 0.1, 0.0))
    last = {}

    def draw(t):
        R, L, sh = orient(t), float(lamp(t)), sharp(t)
        k = (np.round(R, 6).tobytes(), round(L, 4), round(sh, 4))
        if last.get("k") != k:
            last.update(k=k, a=room.frame(R, L, sh))
        return last["a"]

    s.add(FramesLayer(draw, z=-10, opacity=shown, during=[(t0, t1)],
                      fx=[Bloom(strength=0.35, threshold=0.9, radius=5, tint=C.lamp)], **room.layer_kw()))

    # ---- dust in the beam: motes inside the lamp's cone, drifting slowly (pure functions of t)
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
        p_ = q + 0.06 * np.sin(0.23 * t + ph) + np.array([0.0, 0.0, 0.012]) * t
        return room.proj(p_)[0]

    s.add(PointsLayer(motes, color=C.lamp, size=1.6, glow=0.9, additive=True, z=-4,
                      opacity=lamp * shown * 0.45, start=t_lamp - 0.3))

    # ---- the beam in the air (additive haze, only while the lamp is on)
    apex, pool = room.lamp_screen()
    ax = (pool - apex) / np.linalg.norm(pool - apex)
    near = pool - 14.0 * ax                                   # a nearer apex on the same axis (the beam, not the room)
    s.shader("light_cone.frag", z=-5, blend="add", u_apex=tuple(map(float, near)), u_pool=tuple(map(float, pool)),
             u_half=0.30, u_amt=lamp * shown * 0.045, u_col=lin(C.lamp))

    # ---- 'spiral': a gold light runs along the wire's shadow
    hs = room.wire_shadow_xy(I)[::3]
    lit = glow_layer(s, z=2, color=C.pc1, k=0.7)
    path = VMobject(stroke_color=C.pc1, stroke_width=3.6).set_points_smoothly([P3(*p) for p in hs])
    lit.play(Create(path), at=t_spi, dur=2.8, ease="smooth")
    lit.play(path.animate.set_stroke(opacity=0.0), at=t_flat, dur=0.6)
    lit.remove(path, at=t_flat + 0.7)

    # ---- 'flat': an axis along the light through the sculpture; its shadow is one dot; it collapses into it
    W, _ = room.on_wall(room.CENTRE)
    w_xy = P3(*room.proj(W)[0])
    h = 0.6

    def axis(t):
        grow = smoothstep((t - (t_flat - lead)) / 0.7)
        u = smoothstep((t - (t_throw - lead)) / 1.3)
        a = room.CENTRE - h * grow * room.d
        b = room.CENTRE + h * grow * room.d
        a, b = a + u * (W - a), b + u * (W - b)
        pa, pb = (P3(*room.proj(p)[0]) for p in (a, b))
        fade_out = 1 - smoothstep((t - (t1 - 1.6)) / 0.7)
        g = VGroup()
        if u < 0.999:                                         # the light ray it lies on, from the lamp side to the wall
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
    top.redraw(window(axis, t_flat - lead, t1 - 0.85), during=(t_flat - lead, t1 - 0.8))

    # ---- 'least': a slow push in on the shadow, held to the cut
    s.camera.frame(t_least, center=(0.35, -0.05), zoom=1.04, dur=2.4)
