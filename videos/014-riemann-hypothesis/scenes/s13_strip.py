"""s13 strip (P26-P27): every other zero lies in the critical strip 0 < Re s < 1; its centre line Re s = 1/2 is the
critical line. Then the flight: the view zooms in and climbs the line, stopping on each of the first six zeros as its
height is spoken (14.1347 ... 37.5862, from assets/zeros.npy), each ringed and labeled. Finally a hypothetical zero off
the line at 0.8 + 39.2i brings its mirror partner at 0.2 + 39.2i (rho <-> 1 - conj(rho)); no such pair has been found."""
from aion import *

from beats import T
from look import (FLY_U, FLY_XC, FRAME_BOX, GAM, GHOST, TRIV_GAIN, ZGEO_E, carded, feq_mob, ghost_ring, lab,
                  plane_grid, plane_xy, pole_mob, strip_overlay, strip_tags, tex, trivial_mobs, view_O)

LANDS = ("z14", "z21", "z25", "z30", "z33", "z38")


@scene(T.cut_strip, T.cut_riemann)
def s13_strip(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    OE, UE = ZGEO_E
    xc0, tc0 = OE[0] + 0.5 * UE, -OE[1] / UE                       # framing E as (x of Re 1/2, centre height)

    # landing times: each zero arrives as its number is spoken (z14 sits on "about"; "fourteen" follows)
    land = [T.z14 + 0.44] + [getattr(T, b) for b in LANDS[1:]]
    fly = (T.moving_up - L, land[-1])
    zoom = (T.moving_up - L, T.moving_up + 1.6)
    U_of = keys((zoom[0], UE), (zoom[1], FLY_U, "easy_ease"), lead=0)
    xc_of = keys((zoom[0], xc0), (zoom[1], FLY_XC, "easy_ease"), lead=0)
    tk = [(fly[0], tc0)] + [(a, float(GAM[k]), "in_out_sine") for k, a in enumerate(land)]
    tc_of = keys(*tk, lead=0)

    def view(t):
        U = float(U_of(t))
        return view_O(float(xc_of(t)), float(tc_of(t)), U), U

    s.shader("zeta_domain.frag", z=0, animated=False, u_reveal=-1000.0, u_func=3.0, u_opacity=1.0, u_dim=0.0,
             u_sat=0.85, u_debug=0.0, u_origin=Track(lambda t: view(t)[0], active=[fly]),
             u_unit=Track(lambda t: view(t)[1], active=[zoom]),
             u_gain=keys((T.other_zero - L, TRIV_GAIN), (T.other_zero + 0.9, 1.0, "in_out_sine"), lead=0))
    pg = s.manim(z=2, parallax=0.0)
    mk = s.manim(z=5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)

    # ── s12's last frame ──
    grid0 = plane_grid(OE, UE, box=FRAME_BOX, mix=1.0)
    pg.add(grid0)
    pole, tv, feq = pole_mob(OE, UE), trivial_mobs(), feq_mob()
    mk.add(pole[0], *tv.rings, *tv.nums, tv.tag)
    hud.add(feq.card, feq.eq, tv.band, tv.axis, tv.curve, tv.sin_eq[0], *tv.links, tv.sin_eq[1], tv.then)
    feq.eq[3].set_color(C.trivial)

    # ── every other zero lies in a vertical band: the critical strip ──
    hud.play(FadeOut(VGroup(feq.card, feq.eq, tv.band, tv.axis, tv.curve, tv.sin_eq, tv.links, tv.then)),
             at=T.other_zero, dur=0.6)
    mk.play(FadeOut(VGroup(tv.rings, tv.nums, tv.tag)), at=T.other_zero, dur=0.6)
    so = strip_overlay(OE, UE)
    mk.play(FadeIn(so.fill), Create(so.edges[0]), Create(so.edges[1]), at=T.vertical_band, dur=1.0)
    tags = strip_tags()
    rows = [carded(r, buff=0.12, opacity=1.0) for r in (tags.strip, tags.line, tags.rho)]
    hud.play(FadeIn(rows[0], shift=0.06 * DOWN), at=T.crit_strip, dur=0.6)

    # ── its centre line, Re s = 1/2: the critical line ──
    mk.play(Create(so.line), at=T.center_line + 0.5, dur=1.2)
    hud.play(FadeIn(rows[1], shift=0.06 * DOWN), at=T.crit_line, dur=0.6)

    # ── moving up the line: the first six zeros, each on its spoken number ──
    mk.play(FadeOut(pole), at=T.moving_up - 0.4, dur=0.4)
    mk.remove(so.fill, so.edges[0], so.edges[1], so.line, at=fly[0])
    pg.remove(grid0, at=fly[0])
    pg.redraw(lambda t: plane_grid(*view(t), box=FRAME_BOX, mix=1.0), during=fly)

    def lit(t):
        return [float(np.clip((t - (a - 0.3)) / 0.35, 0.0, 1.0)) for a in land]

    mk.redraw(lambda t: strip_overlay(*view(t), lit=lit(t)), during=(fly[0], fly[1] + 0.1))

    # ── each one exactly on the line: rho = 1/2 + i gamma ──
    hud.play(FadeIn(rows[2], shift=0.06 * DOWN), at=T.exactly_on + 0.6, dur=0.6)

    # ── symmetry mirrors zeros across the line: one off it would come with a partner ──
    O1, U1 = view_O(FLY_XC, float(GAM[5]), FLY_U), FLY_U
    crit = Line(plane_xy(0.5 - 4.6j / U1 + 1j * GAM[5], O1, U1), plane_xy(0.5 + 1j * (GAM[5] + 4.6 / U1), O1, U1),
                color=C.crit, stroke_width=3.0)
    mk.play(ShowPassingFlash(crit.set_stroke(C.text, width=6.0), time_width=0.4), at=T.mirror, dur=1.2)   # the mirror
    drag = (T.partner - 0.64 - L, T.partner + 0.3)                      # starts on "off it"
    a_of = keys((drag[0], 0.5), (drag[1], GHOST.real, "easy_ease"), lead=0)

    def pair(t):
        a = float(a_of(t))
        y = plane_xy(complex(0.5, GHOST.imag), O1, U1)[1]
        g = VGroup(ghost_ring(plane_xy(complex(a, 0), O1, U1)[0], y, r=0.17))
        return g

    gh = mk.redraw(pair, during=drag)
    yg = plane_xy(GHOST, O1, U1)
    twin = ghost_ring(plane_xy(1 - GHOST.conjugate(), O1, U1)[0], yg[1], dashed=True, r=0.17)
    link = DashedLine(plane_xy(1 - GHOST.conjugate(), O1, U1) + [0.17, 0, 0], yg - [0.17, 0, 0], color=C.rogue,
                      stroke_width=1.8, dash_length=0.06)
    tag = VGroup(tex(r"\rho\leftrightarrow1-\bar\rho", size=32, color=C.rogue), lab("hypothetical", 26, C.rogue))
    tag.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    tag = carded(tag, buff=0.1, opacity=1.0).move_to(yg + [0.55, 0, 0], aligned_edge=LEFT)
    mk.play(Create(twin), Create(link), FadeIn(tag, shift=0.06 * LEFT), at=T.partner + 0.3, dur=0.6, lead=0)
    mk.play(FadeOut(VGroup(gh, twin, link, tag)), at=T.no_pair + 0.73, dur=1.0)
