"""s12 trivial (P25): the functional equation contains a sine, sin(pi s / 2), and it makes zeta zero at -2, -4, -6, ...
The plane's dark left half is lifted (u_gain) so its pinwheels show; the sine is drawn in a band under the plane with
the same sigma scale, and a dashed link drops from each of its zeros to a pinwheel on the real axis."""
from aion import *

from beats import T
from look import (FRAME_BOX, TRIV_GAIN, ZGEO_E, feq_mob, plane_grid, pole_mob, sym_mobs, trivial_mobs)


@scene(T.cut_trivial, T.cut_strip)
def s12_trivial(s):
    s.solid(C.bg, z=-200)
    O, U = ZGEO_E
    lift = (T.contains_sine - C.lead, T.contains_sine + 1.2)
    s.shader("zeta_domain.frag", z=0, animated=False, u_origin=O, u_unit=U, u_func=3.0, u_reveal=-1000.0,
             u_opacity=1.0, u_dim=0.0, u_sat=0.85, u_debug=0.0,
             u_gain=keys((lift[0], 1.0), (lift[1], TRIV_GAIN, "in_out_sine"), lead=0))
    pg = s.manim(z=2, parallax=0.0)
    mk = s.manim(z=5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)

    # ── s11's last frame ──
    pg.add(plane_grid(O, U, box=FRAME_BOX, mix=1.0))
    pole, sym = pole_mob(O, U), sym_mobs()
    mk.add(pole[0], pole[1], sym.s, sym.line, sym.half, sym.s1)
    feq = feq_mob()
    hud.add(feq.card, feq.eq)

    # ── so where is zeta zero? ──
    mk.play(FadeOut(VGroup(sym.s, sym.line, sym.half, sym.s1, pole[1])), at=T.where_zero, dur=0.6)

    # ── the equation contains a sine; it is drawn under the plane, on the same sigma scale ──
    tv = trivial_mobs()
    hud.play(feq.eq[3].animate.set_color(C.trivial), at=T.contains_sine, dur=0.6)
    hud.play(Indicate(feq.eq[3], color=C.trivial, scale_factor=1.15), at=T.contains_sine + 0.6, dur=1.0, lead=0)
    hud.play(FadeIn(tv.band), FadeIn(tv.axis), at=T.contains_sine + 0.3, dur=0.5)
    hud.play(Create(tv.curve), at=T.contains_sine + 1.5, dur=1.5)                     # on "that sine"
    hud.play(TransformFromCopy(feq.eq[3], tv.sin_eq[0]), at=T.contains_sine + 1.7, dur=0.9)

    # ── its zeros make zeta zero at -2, -4, -6, and every negative even number ──
    for k, at in enumerate((T.minus_two, T.minus_four, T.minus_six, T.negative_even)):
        mk.play(FadeIn(tv.nums[k]), at=at + 0.35, dur=0.4, lead=0)
        hud.play(Create(tv.links[k]), at=at, dur=0.5)
        mk.play(Create(tv.rings[k]), at=at + 0.35, dur=0.5, lead=0)
    hud.play(FadeIn(tv.sin_eq[1]), at=T.negative_even + 0.3, dur=0.5)

    # ── these are the trivial zeros ──
    mk.play(FadeIn(tv.tag, shift=0.06 * UP), at=T.trivial_zeros, dur=0.6)
    hud.play(FadeIn(tv.then, shift=0.06 * UP), at=T.trivial_zeros + 0.5, dur=0.6)
