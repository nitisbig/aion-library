"""c04_s01 · Cream in coffee (hook). Storyboard: plan/scene_plan.md § c04_s01. Layout L1.

Opens on c03_s03's last frame (the atom's cloud smeared into teal dye), which gives way to the chapter card. A cup
seen from above: the coffee is stirred and cream (the chapter hue) is poured in at one spot; a stable-fluids solve
(ch4.coffee, seeded) curls it into swirls. On 'parcels' a grid of small squares is released into the same flow and
carried by it (RK2 on the solved velocity). On "Newton's" one parcel lights and F = ma writes; on 'push' its velocity
and its acceleration (the push per unit mass, from its own path) draw as arrows. 'Navier' brings the name tag. The
camera then dives into the lit parcel, which becomes the square of c04_s02.
"""
import numpy as np
from aion import *

import atoms
import ch4
from beats import T
from kit import P3, RC, X1, Y0, add_rail, chapter_card, glow, lin_rgb, glimpse, sans, smooth01, tag_under

CUPC = np.array([0.0, -0.05])
S = 3.15 / ch4.CUP_R                              # screen units per sim unit (cup radius 3.15 on screen)
HI = 15                                           # the parcel we follow


def W(p):
    """Sim coordinates → screen."""
    return CUPC + S * np.asarray(p)


def _dye_frames(d, t0, op):
    col = lin_rgb(C.navier)

    def frame(t):
        x = ch4.cup_frame(d, t - t0)
        a = ch4.lerp_frames(d["dye"], x).astype(np.float32) / 255.0
        a = a[::-1] * float(op(t))                                  # row 0 = top
        lin = (a ** 1.3)[..., None] * col[None, None, :] * 0.95
        rgb = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
        out = np.zeros(a.shape + (4,), np.uint8)
        out[..., :3] = (rgb / np.maximum(a, 1e-4)[..., None] * 255).clip(0, 255).astype(np.uint8)
        out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
        return out
    return frame


def parcel_at(d, t0, t, i):
    x = ch4.cup_frame(d, t - t0)
    return ch4.lerp_frames(d["parcels"], x)[i]


def _corners(q):
    """The parcel drawn as a square of its own size round its tracked centre, turned with its first edge (the true
    material square stretches into a filament within seconds in this stirred cup)."""
    e = q[1] - q[0]
    a = np.arctan2(e[1], e[0])
    c, s_ = np.cos(a), np.sin(a)
    base = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]) * 0.055
    return q[4] + base @ np.array([[c, s_], [-s_, c]])


def _square(q):
    return Polygon(*[P3(*W(c)) for c in _corners(q)], fill_opacity=0)


@scene(T.c04_s01, T.c04_s02)
def s13_c04_cream(s):
    s.solid(C.bg, z=-200)
    t0 = float(s.start)
    t_cr, t_pa, t_nw, t_pu, t_nv = (T.c04_s01_cream, T.c04_s01_parcels, T.c04_s01_newton_s, T.c04_s01_push,
                                    T.c04_s01_navier)
    d = ch4.coffee()
    # c03_s03's last frame: the atom's cloud smeared into teal dye
    s.add(FramesLayer(atoms.frames(), height=2 * atoms.YH, pos=(0, 0), z=1, parallax=0.0,
                      opacity=fade(t0 - 5, dur=0.1, out=t0 + 0.1, out_dur=0.6), during=[(s.start, t0 + 0.8)]))
    chapter_card(s, 4, at=t0 + 0.5, out=t_cr + 0.2)
    add_rail(s, 4, opacity=fade(t0 + 0.3, dur=0.8), busy=True)

    # the cup, then the cream
    m = s.manim(z=5)
    rim = VGroup(Circle(radius=S * ch4.CUP_R, stroke_color=C.ghost, stroke_width=2.2),
                 Circle(radius=S * ch4.CUP_R + 0.22, stroke_color=C.ghost, stroke_width=1.2, stroke_opacity=0.6)) \
        .move_to(P3(*CUPC))
    m.play(Create(rim), at=t_cr - 0.6, dur=1.2)
    dive = float(s.end) - 2.4
    dye_op = fade(t_cr - 0.5, dur=0.1, out=dive + 0.3, out_dur=1.2)
    s.add(FramesLayer(_dye_frames(d, t0, dye_op), height=2 * S, pos=tuple(CUPC), z=2, during=[(t_cr - 0.2, s.end)]))
    m.play(FadeOut(rim), at=dive + 0.3, dur=1.2)

    # parcels: small squares carried by the same flow
    p_op = fade(t_pa - 0.1, dur=0.8, out=dive + 0.3, out_dur=1.0)
    hi = smooth01

    def parcels(t):
        x = ch4.cup_frame(d, t - t0)
        P = ch4.lerp_frames(d["parcels"], x)
        a = float(p_op(t))
        dim = 1 - 0.6 * float(hi((t - float(t_nw)) / 0.6))
        g = VGroup()
        for i, q in enumerate(P):
            if i == HI:
                continue
            g.add(_square(q).set_stroke(C.light, 1.4, 0.75 * a * dim))
        return g
    s.manim(z=6).redraw(parcels, during=(t_pa - 0.2, s.end))

    def lit(t):
        q = parcel_at(d, t0, t, HI)
        a = float(p_op(t)) if t < float(t_nw) else 1.0
        k = float(hi((t - float(t_nw)) / 0.6))
        u = float(hi((t - dive) / 2.0))                             # straighten into c04_s02's square
        sq = q[4] + np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]) * 0.055
        q = _corners(q) * (1 - u) + sq * u
        return Polygon(*[P3(*W(c)) for c in q], stroke_color=mix_c(k), stroke_width=(1.4 + 1.4 * k) * (1 - 0.63 * u),
                       stroke_opacity=0.75 * a + 0.25 * k, fill_color=C.navier, fill_opacity=0.18 * k)
    glow(s, C.navier, z=8, k=0.45).redraw(lit, during=(t_pa - 0.2, s.end))

    # velocity and push on the lit parcel (push = its own acceleration, from its path)
    a_op = fade(t_pu, dur=0.5, out=dive, out_dur=0.6)

    def arrows(t):
        x = ch4.cup_frame(d, t - t0)
        c = W(ch4.lerp_frames(d["parcels"], x)[HI][4])
        v = ch4.lerp_frames(d["vel"], x)[HI] * S
        v2 = ch4.lerp_frames(d["vel"], min(x + 3, len(d["vel"]) - 1.001))[HI] * S
        v1 = ch4.lerp_frames(d["vel"], max(x - 3, 0))[HI] * S
        acc = (v2 - v1) / (6 / ch4.CUP_FPS)
        a = float(a_op(t))
        g = VGroup()
        if a < 0.01:
            return g
        for vec, col in ((v, C.light), (acc, C.charge_p)):
            nv = float(np.linalg.norm(vec))
            if nv < 1e-6:
                continue
            tip = c + vec / nv * 0.95                                # direction from the solve, length nominal
            if True:
                g.add(Arrow(P3(*c), P3(*tip), buff=0, stroke_width=3.5, color=col, tip_length=0.16,
                            max_tip_length_to_length_ratio=0.35).set_opacity(a))
        return g
    s.manim(z=9).redraw(arrows, during=(t_pu - 0.1, s.end))

    # F = ma, screen-locked in the right column
    hud = s.manim(z=50, parallax=0.0)
    e = Eqn(r"F=m\,a", colors={"F": C.charge_p, "a": C.light}).scale(1.0).move_to(P3(RC + 0.75, 1.3))
    tags = VGroup(tag_under(e, "F", "push", C.charge_p), tag_under(e, "a", "change of speed", C.light))
    hud.play(Write(e), at=t_nw + 0.2, dur=0.9)
    hud.play(FadeIn(tags, shift=0.06 * UP), at=t_pu + 0.1, dur=0.6)
    hud.play(FadeOut(VGroup(e, tags)), at=dive, dur=0.6)
    glimpse(s, ["navier", "stokes"], t_nv, C.navier, h=1.7, at_xy=(X1 - 1.42, Y0 + 1.0))   # bottom right, clear of the cup

    # a slow push toward the parcel, then a dive into it
    c_n = W(parcel_at(d, t0, float(t_pu) + 1.5, HI)[4])
    s.camera.frame(t_nw + 0.3, center=tuple(0.45 * c_n + 0.55 * CUPC), zoom=1.3, dur=3.5)
    c_e = W(parcel_at(d, t0, float(s.end), HI)[4])
    s.camera.frame(dive, center=tuple(c_e), zoom=1.0 / (S * 0.11), dur=2.3)


def mix_c(k):
    from kit import mix
    return mix(C.light, C.navier, k)
