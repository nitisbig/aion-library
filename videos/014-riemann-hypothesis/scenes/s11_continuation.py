"""s11 continuation (P23-P24): a formula can outlive its sum. Inset: partial sums of 1 + x + x^2 + ... settle for
|x| < 1 and run off outside, while 1/(1 - x) agrees inside and carries on everywhere except x = 1. Then rigidity: a
small patch of zeta's colors decides the rest; the colors flow left across Re s = 1 and fill the plane, except the
pole at s = 1. Finally the symmetry s <-> 1 - s through 1/2, and the functional equation."""
from aion import *

from beats import T
from look import (EASE, FRAME_BOX, S_LEFT, ZGEO, ZGEO_E, carded, feq_mob, inset_mobs, inset_spiral, lab, live,
                  plane_grid, plane_xy, pole_mob, probe_mob, re1_mobs, sym_mobs, tex, to_d, zeta_tag)

# the geometric-series inset, over the dark left half
XS = (-1.5, -0.5, 0.4, 0.7, 1.4)             # sample x: three settle, two run off
GX, GY, KX, KY = -4.2, -0.95, 1.15, 0.62     # plot origin and units per 1
YLO, YHI = -2.5, 4.0
CARD = (-6.9, -1.45, -2.85, 2.6)
PATCH = 3.0 + 5.0j                           # the small patch (side 1), in framing D


def gx(x):
    return GX + KX * x


def gy(y):
    return GY + KY * y


def S(x, n):
    """The partial sum 1 + x + ... + x^(n-1), linearly between whole n."""
    k = int(np.floor(n))
    a = sum(x ** j for j in range(k))
    return a + (n - k) * x ** k


def marker(x, up):
    tri = Triangle(color=C.text, fill_opacity=1.0, stroke_width=0).scale(0.09)
    if not up:
        tri.rotate(PI)
    return tri.move_to([gx(x), gy(YHI if up else YLO), 0])


def sums_mob(n):
    g = VGroup()
    for x in XS:
        for m in range(1, int(np.floor(n)) + 1):         # the trail of earlier sums
            y = S(x, m)
            if YLO <= y <= YHI:
                g.add(Line([gx(x) - 0.09, gy(y), 0], [gx(x) + 0.09, gy(y), 0], color=C.muted, stroke_width=1.6))
        y = S(x, n)
        g.add(marker(x, y > 0) if not YLO <= y <= YHI else Dot([gx(x), gy(y), 0], radius=0.07, color=C.text))
    return g


def frac_curve(x0, x1):
    xs = np.linspace(x0, x1, 120)
    v = VMobject(color=C.smooth, stroke_width=3.0)
    v.set_points_smoothly(np.column_stack([gx(xs), gy(1 / (1 - xs)), np.zeros_like(xs)]))
    return v


@scene(T.cut_continuation, T.cut_trivial)
def s11_continuation(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    mv = (T.symmetry - L, T.symmetry + 1.2)               # framing D → E, centred on 1/2
    O = keys((mv[0], ZGEO[0]), (mv[1], ZGEO_E[0], EASE), lead=0)
    U = ZGEO[1]

    def org(t):
        o = O(t)
        return (float(o[0]), float(o[1]))

    front = (T.whole_plane - L, T.whole_plane - L + 6.0)  # the continuation front, sigma 1 → -12
    s.shader("zeta_domain.frag", z=0, animated=False, u_origin=Track(org, active=[mv]), u_unit=U, u_func=3.0,
             u_reveal=keys((front[0], 1.0), (front[1], -12.0, EASE), lead=0), u_opacity=1.0, u_dim=0.0,
             u_sat=0.85, u_gain=1.0, u_debug=0.0)
    pg = s.manim(z=2, parallax=0.0)
    mk = s.manim(z=5, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)

    # ── s10's last frame ──
    grid0 = plane_grid(ZGEO[0], U, box=FRAME_BOX, mix=1.0)
    pg.add(grid0)
    re1 = re1_mobs()
    probe = probe_mob(S_LEFT, 0.0, 0.0, to_xy=to_d)
    mk.add(re1.line, re1.label, probe)
    z_tag, ins = zeta_tag(), inset_mobs()
    spiral = inset_spiral(S_LEFT, 3000.0)
    hud.add(z_tag, ins.frame, ins.cap, spiral)
    mk.play(FadeOut(probe), at=T.simpler_sum, dur=0.5)
    hud.play(FadeOut(VGroup(ins.frame, ins.cap, spiral)), at=T.simpler_sum, dur=0.5)

    # ── a simpler sum: 1 + x + x^2 + ... settles only for |x| < 1 ──
    card = Rectangle(width=CARD[1] - CARD[0], height=CARD[3] - CARD[2], stroke_color=C.faint, stroke_width=1.4,
                     fill_color=C.bg, fill_opacity=1.0).move_to([(CARD[0] + CARD[1]) / 2, (CARD[2] + CARD[3]) / 2, 0])
    xax = Line([gx(-2.2), GY, 0], [gx(2.2), GY, 0], color=C.axis, stroke_width=1.8)
    yax = Line([GX, gy(YLO), 0], [GX, gy(YHI), 0], color=C.axis, stroke_width=1.8)
    ticks = VGroup()
    for v in (-2, -1, 1, 2):
        ticks.add(Line([gx(v), GY - 0.06, 0], [gx(v), GY + 0.06, 0], color=C.muted, stroke_width=1.6),
                  tex(str(v), size=24, color=C.muted).move_to([gx(v), GY - 0.27, 0]))
    for v in (1, 2, 3):
        ticks.add(Line([GX - 0.06, gy(v), 0], [GX + 0.06, gy(v), 0], color=C.muted, stroke_width=1.6),
                  tex(str(v), size=22, color=C.muted).move_to([GX - 0.25, gy(v), 0]))
    hud.play(FadeIn(card), FadeIn(VGroup(xax, yax, ticks)), at=T.simpler_sum + 0.4, dur=0.6)
    geo_eq = tex(r"1", r"+x", r"+x^2", r"+\cdots", r"=", r"\frac{1}{1-x}", size=36, colors={5: C.smooth})
    geo_eq.move_to([(CARD[0] + CARD[1]) / 2, 2.05, 0])
    for part, at in ((geo_eq[0], T.one_plus_x), (geo_eq[1], T.one_plus_x + 0.48), (geo_eq[2], T.one_plus_x + 1.16),
                     (geo_eq[3], T.one_plus_x + 2.11)):
        hud.play(FadeIn(part, shift=0.06 * LEFT), at=at, dur=0.4)
    n_of = keys((T.one_plus_x + 0.48 - L, 1.0), (T.one_plus_x + 0.88, 2.0), (T.one_plus_x + 1.16 - L, 2.0),
                (T.one_plus_x + 1.56, 3.0), (T.one_plus_x + 2.11 - L, 3.0), (T.one_plus_x + 2.11 + 3.0, 20.0, "in_cubic"),
                lead=0)
    s0 = sums_mob(1.0)
    hud.play(FadeIn(s0), at=T.one_plus_x, dur=0.4)
    hud.remove(s0, at=T.one_plus_x + 0.48 - L)
    sums = hud.redraw(lambda t: sums_mob(float(n_of(t))), during=(T.one_plus_x + 0.48 - L, T.one_plus_x + 2.11 + 3.0))
    inside = Line([gx(-1), GY, 0], [gx(1), GY, 0], color=C.text, stroke_width=6.0)
    hud.play(Create(inside), at=T.between + 0.36, dur=0.9)

    # ── there it equals 1/(1 - x), which works for every x except 1: the formula keeps going ──
    hud.play(FadeIn(geo_eq[4:], shift=0.06 * LEFT), at=T.equals_frac + 0.68, dur=0.5)
    mid = frac_curve(-1.0, 0.75)
    hud.play(Create(mid), at=T.equals_frac + 0.96, dur=1.5)
    outer = VGroup(frac_curve(-2.0, -1.0), frac_curve(1.4, 2.0))
    hud.play(Create(outer[0]), Create(outer[1]), at=T.every_x, dur=1.0)
    asym = DashedLine([gx(1), gy(YLO), 0], [gx(1), gy(YHI), 0], color=C.muted, stroke_width=1.6, dash_length=0.08)
    ne1 = tex(r"x\neq1", size=30, color=C.muted).move_to([gx(1) + 0.55, gy(3.2), 0])
    hud.play(Create(asym), FadeIn(ne1), at=T.every_x + 1.2, dur=0.6)
    hud.play(Indicate(outer, color=C.text, scale_factor=1.0), at=T.keeps_going + 1.0, dur=1.2)
    series = VGroup(card, xax, yax, ticks, geo_eq, inside, mid, outer, asym, ne1)
    hud.play(FadeOut(series), FadeOut(sums), at=T.keeps_going + 2.9, dur=0.6)

    # ── rigid: a small patch of the plane decides the rest ──
    pc, h = to_d(PATCH), 0.5 * U
    x0, x1, y0, y1 = pc[0] - h, pc[0] + h, pc[1] - h, pc[1] + h
    shade = VGroup(*[Rectangle(width=b - a, height=d - c, stroke_width=0, fill_color=C.bg, fill_opacity=0.93)
                     .move_to([(a + b) / 2, (c + d) / 2, 0])
                     for a, b, c, d in ((-7.3, x0, -4.2, 4.2), (x1, 7.3, -4.2, 4.2), (x0, x1, y1, 4.2),
                                        (x0, x1, -4.2, y0))])
    patch = Square(side_length=2 * h, color=C.text, stroke_width=2.6).move_to(pc)
    mk.play(FadeIn(shade), Create(patch), at=T.small_patch, dur=0.6)
    mk.play(Indicate(patch, color=C.text, scale_factor=1.15), at=T.small_patch + 0.7, dur=0.9)
    mk.play(FadeOut(shade), at=T.one_way + 1.4, dur=1.0)                 # on "extend it"

    # ── Riemann's extension: the colors flow left across Re s = 1 and fill the plane, except s = 1 ──
    mk.play(FadeOut(VGroup(patch, re1.line, re1.label)), at=T.whole_plane + 0.3, dur=0.6)
    hud.play(FadeOut(z_tag), at=T.whole_plane + 0.3, dur=0.6)          # the sum no longer holds
    pole0 = pole_mob(ZGEO[0], U)
    mk.play(Create(pole0[0]), FadeIn(pole0[1]), at=T.except_one + 0.45, dur=0.6)

    # ── the symmetry: s and 1 - s, through 1/2 (the view re-centres on 1/2) ──
    mk.remove(pole0[0], pole0[1], at=mv[0])
    live(mk, lambda t: pole_mob(org(t), U), mv)
    pg.remove(grid0, at=mv[0])
    pg.redraw(lambda t: plane_grid(org(t), U, box=FRAME_BOX, mix=1.0), during=mv)
    sym = sym_mobs()
    mk.play(FadeIn(sym.s, scale=0.8), at=T.symmetry + 1.75, dur=0.5)          # on "value at s"
    mk.play(Create(sym.line), FadeIn(sym.half), at=T.one_minus_s - 0.5, dur=1.0)
    mk.play(FadeIn(sym.s1, scale=0.8), at=T.one_minus_s, dur=0.5)
    feq = feq_mob()
    hud.play(FadeIn(feq.card), at=T.one_minus_s + 1.0, dur=0.4)
    hud.play(Write(feq.eq), at=T.one_minus_s + 1.16, dur=1.5)
