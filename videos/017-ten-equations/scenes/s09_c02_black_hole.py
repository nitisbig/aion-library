"""c02_s03 · Black hole (payoff). Storyboard: plan/scene_plan.md § c02_s03. Layout L1.

The eclipse's dark disc and ring (c02_s02's last frame) shrink into a ray-traced Schwarzschild black hole far away;
the camera approaches and orbits (aion BlackHoleLayer). On 'light' the photon ring brightens; on 'black hole' a thin
circle marks the shadow's edge, where light that comes closer can no longer climb back out, and the field equations
float below it (frame 04). On 'LIGO' two black holes spiral together (Newtonian chirp, ch2) and send out the
quadrupole wave pattern at retarded time; the detector's strain draws along the bottom. On 'atom' the camera dives
into one bright point, which becomes a hydrogen atom (1s cloud), the bridge to chapter 3.
"""
import math

import numpy as np
from aion import *

import ch2
from ch3 import cloud_rgba
from beats import T
from kit import chapter_backdrop, glimpse, P3, XW, YH, add_rail, lin_rgb, sans, shade, smooth01, tag_under, tint

BC = np.array([0.0, 0.4])                        # binary's centre
P_ATOM = np.array([3.35, 1.55])                  # the bright point the camera dives into
FOV = 36.0
SCN_SCREEN, RING0 = np.array([-0.56, 0.0]), 0.55 * 1.04 * 1.12   # c02_s02's ring on screen at its end


def _dist(t):
    a = float(smooth01((t - float(T.c02_s03_squeeze)) / (float(T.c02_s03_black_hole) + 1.0 - float(T.c02_s03_squeeze))))
    return 80.0 + (34.0 - 80.0) * a ** 0.8 - 1.5 * float(smooth01((t - float(T.c02_s03_black_hole)) / 4.0))


def shadow_radius(d):
    """Screen radius (world units) of the shadow's edge, sin α = (√27 M / d)·√(1 − 2M/d), for the vertical fov."""
    s = math.sqrt(27.0) / d * math.sqrt(1 - 2.0 / d)
    return math.tan(math.asin(s)) / math.tan(math.radians(FOV / 2)) * YH


@scene(T.c02_s03, T.c03_s01)
def s09_c02_black_hole(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 2, last=True)
    add_rail(s, 2, busy=True)
    t_sq, t_light, t_bh = T.c02_s03_squeeze, T.c02_s03_light, T.c02_s03_black_hole
    t_ligo, t_merge, t_prot, t_atom = T.c02_s03_ligo, T.c02_s03_merging, T.c02_s03_proton_s, T.c02_s03_atom
    # the real one: the Event Horizon Telescope's image of M87* (2019, CC BY 4.0), beside the computed one
    glimpse(s, "photo:m87.jpg", t_bh + 0.3, C.einstein, dur=min(3.2, float(t_ligo) - float(t_bh) - 0.9), h=2.3)
    hud = s.manim(z=50, parallax=0.0)

    # the eclipse ring closes into a far black hole
    def ring(t):
        u = float(smooth01((t - float(s.start) - 0.2) / 1.6))
        r = RING0 + (shadow_radius(_dist(t)) - RING0) * u
        c = SCN_SCREEN * (1 - u)
        return Circle(radius=r, stroke_color=C.light, stroke_width=3, stroke_opacity=1 - u).move_to(P3(*c))
    s.manim(z=5, parallax=0.0, fx=[Glow(C.light, strength=C.glow * 0.6, radius=C.glow_r)]) \
        .redraw(ring, during=(s.start, s.start + 2.0))
    bh_op = fade(t_sq - 0.3, dur=1.6, out=t_ligo - 0.2, out_dur=0.8)
    s.add(BlackHoleLayer(dist=_dist, inclination=key(t_bh, 84.0, 79.0, dur=6.0),
                         azimuth=lambda t: 6.0 * (t - float(t_sq)), fov=FOV, sky="galaxy",
                         u_ring=key(t_light, 0.55, 1.0, dur=1.2), scale_res=2, z=-20, opacity=bh_op, start=s.start,
                         end=t_ligo + 0.8, name="bh"))

    # black hole: the edge of no return, and the equation read as shape = matter
    hz = s.manim(z=10, parallax=0.0)
    edge = DashedVMobject(Circle(radius=shadow_radius(_dist(float(t_bh) + 1.0)), stroke_color=C.muted,
                                 stroke_width=1.8), num_dashes=60)
    rr = edge.width / 2
    no_way = sans("no way out", 26, C.text).move_to(P3(rr * 0.75 + 0.95, rr * 0.75 + 0.15))
    shade(s, no_way.get_center()[0], no_way.get_center()[1], no_way.width + 0.3, no_way.height + 0.2, a=0.8, z=9,
          parallax=0.0, opacity=fade(t_bh + 0.3, out=t_ligo - 0.4, out_dur=0.6))
    hz.play(Create(edge), at=t_bh, dur=0.9)
    hz.play(FadeIn(no_way), at=t_bh + 0.3, dur=0.5)
    G, Tm = r"G_{\mu\nu}", r"T_{\mu\nu}"
    e = Eqn(r"G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}\,T_{\mu\nu}",
            colors={G: C.einstein, r"\Lambda g_{\mu\nu}": C.einstein, Tm: C.light})
    e.scale(0.9).move_to(P3(0.3, -2.35))
    eg = VGroup(e, tag_under(e, G, "shape", C.einstein, size=24), tag_under(e, Tm, "matter", C.light, size=24))
    shade(s, 0.3, eg.get_center()[1], eg.width + 1.2, eg.height + 0.6, a=0.88, z=9, parallax=0.0,
          opacity=fade(t_bh + 1.0, out=t_ligo - 0.4, out_dur=0.6))
    hz.play(FadeIn(eg, shift=0.1 * UP), at=t_bh + 1.2, dur=0.8)
    hz.play(FadeOut(VGroup(edge, no_way, eg)), at=t_ligo - 0.4, dur=0.6)

    # LIGO: two black holes spiral in; the quadrupole ripples spread at retarded time
    ext = (2 * XW + 1.0, 2 * YH + 0.8)
    nx, ny = int(ext[0] * 40), int(ext[1] * 40)
    xs = np.linspace(-ext[0] / 2, ext[0] / 2, nx)
    ys = np.linspace(-ext[1] / 2, ext[1] / 2, ny)
    X, Y = np.meshgrid(xs, ys)                                   # row 0 = bottom
    s.add(FieldLayer(lambda t: ch2.ripple_field(X, Y, t, center=BC), cmap="diverging",
                     colors=(tint(C.einstein, 0.16), C.bg, tint(C.einstein, 0.72)), vmin=-1.3, vmax=1.3, extent=ext,
                     z=-15, opacity=fade(t_ligo - 0.3, dur=1.0, out=t_atom + 0.4, out_dur=1.2),
                     start=t_ligo - 0.6, end=s.end))

    def binary(t):
        g = VGroup()
        tm = ch2.merge_time()
        if t < tm:
            a, ph = ch2.separation(t) / 2, ch2.orbital_phase(t)
            for sg in (1, -1):
                p = BC + sg * a * np.array([math.cos(ph), math.sin(ph)])
                g.add(Circle(radius=0.15, stroke_color=C.light, stroke_width=1.6, fill_color=C.bg, fill_opacity=1)
                      .move_to(P3(*p)))
        else:
            g.add(Circle(radius=0.21, stroke_color=C.light, stroke_width=1.6, fill_color=C.bg, fill_opacity=1)
                  .move_to(P3(*BC)))
        return g.set_opacity(float(bin_op(t)))
    bin_op = fade(t_ligo - 0.1, dur=0.6, out=t_atom - 1.0, out_dur=0.8)
    s.manim(z=-5, fx=[Glow(C.light, strength=C.glow * 0.7, radius=C.glow_r)]).redraw(binary, during=(t_ligo - 0.4, s.end))
    flash = pulse(ch2.merge_time(), amp=1.0, dur=0.9)
    s.manim(z=-4, fx=[Glow(C.light, strength=C.glow * 2.0, radius=C.glow_r)]) \
        .redraw(lambda t: Dot(P3(*BC), radius=0.2, color=C.light, fill_opacity=float(flash(t))),
                during=(float(t_merge) - 0.6, float(t_merge) + 1.4))

    # the detector's strain, drawn as it arrives
    tr0, tr1 = float(t_ligo) - 0.2, float(t_merge) + 1.8
    y_tr = -2.5
    tr_op = fade(t_ligo + 0.2, dur=0.6, out=t_atom - 1.6, out_dur=0.8)
    shade(s, 0.0, y_tr, 10.0, 1.1, a=0.75, z=-3, opacity=tr_op)
    base = Line(P3(-4.6, y_tr), P3(4.6, y_tr), stroke_color=C.ghost, stroke_width=1.2)
    trc = s.manim(z=-2)
    trc.play(FadeIn(base), at=t_ligo + 0.2, dur=0.6)
    trc.play(FadeOut(base), at=t_atom - 1.6, dur=0.8)
    trc.redraw(lambda t: ch2.strain_trace(t, -4.6, 4.6, y_tr, 0.42, tr0, tr1, C.einstein).set_stroke(opacity=float(tr_op(t))),
               during=(tr0, float(t_atom) - 0.6))
    strain_lab = sans("strain", 22, C.muted).move_to(P3(-5.25, y_tr))
    prot = sans("less than 1/100 of a proton's width", 24, C.text).move_to(P3(2.3, y_tr + 0.75))
    trc.play(FadeIn(strain_lab), at=t_ligo + 0.4, dur=0.6)
    trc.play(FadeIn(prot, shift=0.08 * UP), at=t_prot, dur=0.6)
    trc.play(FadeOut(VGroup(strain_lab, prot)), at=t_atom - 1.6, dur=0.8)

    # atom: dive into one bright point; it is a hydrogen atom
    pt_op = fade(t_atom - 2.4, dur=0.8)
    s.manim(z=6, fx=[Glow(C.light, strength=C.glow * 1.4, radius=C.glow_r)]) \
        .redraw(lambda t: Dot(P3(*P_ATOM), radius=0.035 * (1 - 0.6 * float(smooth01((t - float(t_atom) + 0.4) / 1.2))),
                              color=C.light, fill_opacity=float(pt_op(t))), during=(float(t_atom) - 2.6, s.end))
    s.add(ArrayLayer(cloud_rgba(), height=0.34, pos=tuple(P_ATOM), z=5, opacity=fade(t_atom - 0.2, dur=1.4)))
    s.camera.frame(t_atom + 0.3, center=tuple(P_ATOM), zoom=9.0, dur=2.8)
