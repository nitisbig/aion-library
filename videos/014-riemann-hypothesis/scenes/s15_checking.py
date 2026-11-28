"""s15 checking (P29-P30): how a zero is known to be exactly on the line. The plane turns 90 degrees so the critical line
runs left to right (t from 0 to 60). Below it, Hardy's Z(t) = e^(i theta(t)) zeta(1/2 + it), a real wave: each sign
change pings a link up to a pinwheel on the line. The crossings, counted as a staircase, match the separate count
N(T) = theta(T)/pi + 1 (cyan): 13 below 60, so all 13 are on the line. Turing, early 1950s; since then 10^13 zeros.
All values from zmath (hardy_Z, N_count, checked against mpmath.siegelz)."""
from aion import *

from beats import T
from media_assets import portrait_card
from look import (FLY_U, FLY_XC, FRAME_BOX, GAM, caps, carded, lab, pin, plane_grid, strip_overlay, tex, view_O)
from zmath import N_count, hardy_Z

T_MAX, LY, KU = 60.0, 3.0, 0.21              # t range; screen y of the line once turned; units per 1
ZY, KZ = 0.4, 0.42                           # Z(t) axis and scale
NY, KN = -3.55, 0.13                         # the count staircase: base and units per zero
MASK_TOP = 2.1
ZS = [float(g) for g in GAM if g < T_MAX]    # the 13 zeros below 60


def tx(t):
    return KU * (np.asarray(t, float) - T_MAX / 2)


def rot(a):
    c, s_ = np.cos(a), np.sin(a)
    return np.array([[c, -s_], [s_, c]])


@scene(T.cut_checking, T.cut_explicit)
def s15_checking(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    bye = (T.cut_explicit - 0.5, T.cut_explicit - 0.05)                # to black before chapter 4's card
    turn = (T.real_wave - 1.73 - L, T.real_wave + 0.3)                  # from "Along the line" to "turned"
    U0, P0, ta0 = FLY_U, np.array([FLY_XC, 0.0]), float(GAM[5])
    u_k = keys((turn[0], 0.0), (turn[1], 1.0, "easy_ease"), lead=0)

    def view(t):
        """(origin O, unit U, rotation) with s = 1/2 + i ta pinned at P; the turn is interpolated in log U."""
        u = float(u_k(t))
        U = float(np.exp(np.log(U0) + u * (np.log(KU) - np.log(U0))))
        P = P0 + u * (np.array([0.0, LY]) - P0)
        ta = ta0 + u * (T_MAX / 2 - ta0)
        a = -0.5 * np.pi * u
        O = P - U * rot(a) @ np.array([0.5, ta])
        return O, U, a

    def scr(z, t):
        O, U, a = view(t)
        return np.array([*(O + U * rot(a) @ np.array([z.real, z.imag])), 0.0])

    s.shader("zeta_domain.frag", z=0, animated=False, u_func=3.0, u_reveal=-1000.0, u_sat=0.85,
             u_opacity=keys((bye[0], 1.0), (bye[1], 0.0), lead=0),
             u_gain=1.0, u_debug=0.0, u_dim=keys((T.how_know - L, 0.55), (T.how_know + 0.8, 0.0, "easy_ease"), lead=0),
             u_origin=Track(lambda t: tuple(view(t)[0]), active=[turn]),
             u_unit=Track(lambda t: view(t)[1], active=[turn]), u_rot=Track(lambda t: view(t)[2], active=[turn]))
    pg = s.manim(z=2, parallax=0.0, opacity=keys((bye[0], 1.0), (bye[1], 0.0), lead=0))
    mk = s.manim(z=5, parallax=0.0, opacity=keys((bye[0], 1.0), (bye[1], 0.0), lead=0))
    hud = s.manim(z=6, parallax=0.0, opacity=keys((bye[0], 1.0), (bye[1], 0.0), lead=0))
    veil = s.manim(z=7, parallax=0.0)

    # ── s14's last frame ──
    O14 = view_O(FLY_XC, ta0, FLY_U)
    grid = plane_grid(O14, FLY_U, box=FRAME_BOX, mix=1.0)
    pg.add(grid)
    ov = strip_overlay(O14, FLY_U, lit=[1.0] * 6)
    mk.add(ov)                            # added whole, as in s14 (keeps its draw order)
    title = caps("The Riemann Hypothesis", 40, C.text)
    stmt = tex(r"\zeta(\rho)=0,\ \ 0<\mathrm{Re}\,\rho<1", r"\ \ \Longrightarrow\ \ ", r"\mathrm{Re}\,\rho=\tfrac12",
               size=44, colors={2: C.crit})
    block = VGroup(title, stmt).arrange(DOWN, buff=0.3)
    box = SurroundingRectangle(block, color=C.text, stroke_width=2.2, buff=0.28, fill_color=C.bg, fill_opacity=1.0)
    VGroup(box, block).move_to([-0.6, 2.35, 0])
    tl = _timeline()
    hud.add(box, title, stmt, *tl)

    # ── how can anyone know a zero is exactly on the line? ──
    hud.play(FadeOut(VGroup(box, title, stmt, *tl)), at=T.how_know, dur=0.6)
    t1 = T.how_know + 0.3                     # swap the s14 overlay for live copies (no submobject animations)
    mk.remove(ov, at=t1)
    pg.play(FadeOut(VGroup(ov.fill.copy(), ov.edges.copy(), ov.rings[0][1].copy())), at=t1, dur=0.6, lead=0)
    pg.play(FadeOut(grid), at=t1, dur=0.6, lead=0)

    # ── the plane turns: the critical line runs left to right along the top ──
    def line_mob(t):
        a, b = scr(complex(0.5, -60.0), t), scr(complex(0.5, 120.0), t)
        u = float(np.clip((t - (T.not_near + 0.35)) / 1.0, 0.0, 1.0))            # a pulse on "not just near"
        r = (0.2 + (0.11 - 0.2) * float(u_k(t))) * (1.0 + 0.4 * np.sin(np.pi * u))
        c = scr(complex(0.5, ta0), t)
        ring = VGroup(Circle(radius=r, color=C.bg, stroke_width=7.0), Circle(radius=r, color=C.text, stroke_width=3.0))
        return VGroup(ring.move_to(c), Line(a, b, color=C.crit, stroke_width=3.0))

    mk.redraw(line_mob, during=(t1, turn[1]))
    mask = VGroup(Rectangle(width=14.6, height=4.2 + MASK_TOP, stroke_width=0, fill_color=C.bg, fill_opacity=1.0)
                  .move_to([0, (MASK_TOP - 4.2) / 2, 0]),
                  Line([-7.3, MASK_TOP, 0], [7.3, MASK_TOP, 0], color=C.faint, stroke_width=1.2))
    pg.play(FadeIn(mask), at=turn[1] - 0.2, dur=0.6, lead=0)
    crit_tag = carded(VGroup(tex(r"\mathrm{Re}\,s=\tfrac12", size=28), lab("critical line", 24, C.crit))
                      .arrange(RIGHT, buff=0.2), buff=0.08, opacity=1.0).move_to([-5.3, LY + 0.55, 0])
    mk.play(FadeIn(crit_tag), at=turn[1] + 0.1, dur=0.5, lead=0)

    # ── Hardy's Z function: a real wave; every crossing is a zero exactly on the line ──
    tt = np.linspace(0.0, T_MAX, 900)
    zz = hardy_Z(np.maximum(tt, 1e-3))
    zaxis = VGroup(Line([tx(0) - 0.1, ZY, 0], [tx(T_MAX) + 0.1, ZY, 0], color=C.muted, stroke_width=1.6),
                   tex("0", size=24, color=C.muted).move_to([tx(0), ZY - 0.25, 0]),
                   tex("60", size=24, color=C.muted).move_to([tx(T_MAX), ZY - 0.25, 0]),
                   tex("t", size=28, color=C.muted).move_to([tx(T_MAX) + 0.3, ZY + 0.05, 0]))
    zf = tex(r"Z(t)", r"=e^{i\theta(t)}\,\zeta(\tfrac12+it)", r"\in\mathbb{R}", size=34, colors={0: C.zero})
    pin(zf, top=1.85, left=-6.4)
    hud.play(FadeIn(zaxis), at=T.real_wave + 0.6, dur=0.5)
    hud.play(Write(zf), at=T.hardy_z, dur=1.2)
    draw = (T.hardy_z + 0.6, T.hardy_z + 4.6)                         # Z draws left to right over 4 s

    def z_upto(t):
        head = T_MAX * float(np.clip((t - draw[0]) / (draw[1] - draw[0]), 0.0, 1.0))
        keep = tt <= head
        if keep.sum() < 2:
            return VGroup()
        v = VMobject(color=C.zero, stroke_width=2.8)
        v.set_points_as_corners(np.column_stack([tx(tt[keep]), ZY + KZ * zz[keep], np.zeros(keep.sum())]))
        return v

    zw = hud.redraw(z_upto, during=draw)
    ping_at = [draw[0] + (draw[1] - draw[0]) * g / T_MAX for g in ZS]
    for k, (g, at) in enumerate(zip(ZS, ping_at)):
        link = DashedLine([float(tx(g)), ZY, 0], [float(tx(g)), LY - 0.12, 0], color=C.zero, stroke_width=1.4,
                          dash_length=0.06, stroke_opacity=0.7)
        dot = Dot([float(tx(g)), ZY, 0], radius=0.06, color=C.zero)
        ring = Circle(radius=0.11, color=C.text, stroke_width=2.6).move_to([float(tx(g)), LY, 0])
        anims = [Create(link), FadeIn(dot, scale=0.5)] + ([] if k == 5 else [Create(ring)])
        mk.play(*anims, at=at, dur=0.3, lead=0)

    # ── a separate count of all the zeros below a height: the two agree ──
    base = Line([tx(0), NY, 0], [tx(T_MAX) + 0.1, NY, 0], color=C.muted, stroke_width=1.6)
    pts = [[float(tx(0)), NY, 0]]
    for k, g in enumerate(ZS):
        pts += [[float(tx(g)), NY + KN * k, 0], [float(tx(g)), NY + KN * (k + 1), 0]]
    pts += [[float(tx(T_MAX)), NY + KN * len(ZS), 0]]
    stair = VMobject(color=C.zero, stroke_width=2.8)
    stair.set_points_as_corners(np.array(pts))
    tn = np.linspace(8.0, T_MAX, 300)
    smooth = VMobject(color=C.smooth, stroke_width=2.6)
    smooth.set_points_smoothly(np.column_stack([tx(tn), NY + KN * np.maximum(N_count(tn), 0.0), 0 * tn]))
    nf = tex(r"N(T)", r"\approx\frac{T}{2\pi}\ln\frac{T}{2\pi e}+\frac78", size=30, colors={0: C.smooth})
    pin(nf, top=-1.75, left=-6.4)
    cross_tag = lab("crossings", 24, C.zero).move_to([float(tx(ZS[4])) - 0.2, NY + KN * 6.6, 0])
    hud.play(FadeIn(base), Create(stair), FadeIn(cross_tag), at=T.crossings_match, dur=1.2)
    hud.play(Create(smooth), FadeIn(nf, shift=0.06 * UP), at=T.separate_count, dur=1.5)
    both = lab("13 crossings = 13 zeros", 26, C.text)
    both.move_to([6.4 - both.width / 2, NY + KN * 13 + 0.42, 0])
    hud.play(Indicate(VGroup(stair, smooth), color=C.text, scale_factor=1.0), FadeIn(both), at=T.every_one_of + 0.4,
             dur=1.0)

    # ── Turing, early 1950s; since then, the first ten trillion zeros ──
    tur = carded(caps(r"A. Turing $\cdot$ 1950s", 34, C.ink), buff=0.12, opacity=1.0)
    tur.move_to([-0.95 + tur.width / 2, -1.2, 0])      # in the gap between the wave and the counts
    hud.play(FadeIn(tur, shift=0.06 * LEFT), at=T.turing + 0.3, dur=0.6)
    portrait_card(s, hud, "turing", None, T.turing, T.ten_trillion + 3.2, (-1.75, -1.45), height=1.5, z=6.5)
    lower = VGroup(base, stair, smooth, nf, cross_tag, both)
    hud.play(FadeOut(lower), at=T.since_then, dur=0.6)
    roll = (T.ten_trillion - L, T.ten_trillion - L + 3.0)
    lg = keys((roll[0], np.log10(13.0)), (roll[1], 13.0, "out_cubic"), lead=0)

    def counter(t):
        n = int(round(10 ** float(lg(t))))
        num = tex(r"{:,}".format(n).replace(",", "{,}"), size=60)
        return num.move_to([0, -2.15, 0])

    c0 = counter(roll[0])
    sub = lab("zeros checked", 30, C.muted).move_to([0, -2.9, 0])
    hud.play(FadeIn(c0), FadeIn(sub), at=T.ten_trillion - 0.6, dur=0.4)
    hud.remove(c0, at=roll[0])
    hud.redraw(counter, during=roll)
    ok = lab("all on the line", 34, C.crit).move_to([0, -3.42, 0])
    hud.play(FadeIn(ok, shift=0.06 * UP), at=T.ten_trillion + 1.92, dur=0.6)          # on "every one"


def _timeline():
    """s14's timeline band, rebuilt for the cut (same numbers as s14_riemann)."""
    yx = lambda y: -5.6 + 11.1 * (y - 1859) / (2026 - 1859)                   # noqa: E731
    TL_Y = -3.2
    band = Rectangle(width=14.6, height=1.75, stroke_width=0, fill_color=C.bg, fill_opacity=1.0).move_to([0, -3.3, 0])
    rule = Line([-7.3, -2.43, 0], [7.3, -2.43, 0], color=C.faint, stroke_width=1.2)
    axis = Line([yx(1859), TL_Y, 0], [yx(2026), TL_Y, 0], color=C.muted, stroke_width=2.0)

    def mark(year, label, color=C.text, sub=None):
        tick = Line([yx(year), TL_Y - 0.1, 0], [yx(year), TL_Y + 0.1, 0], color=color, stroke_width=3.0)
        y_ = caps(label, 30, color).move_to([yx(year), TL_Y + 0.38, 0])
        g = VGroup(tick, y_)
        if sub is not None:
            g.add(sub.move_to([yx(year), TL_Y - 0.38, 0]))
        return g

    return [band, rule, axis, mark(1859, "1859", C.ink, caps(r"Riemann", 24, C.muted)),
            mark(2026, "2026", C.muted),
            mark(1900, "1900", C.ink, caps(r"D. Hilbert $\cdot$ problem 8", 24, C.muted)),
            mark(2000, "2000", C.ink, caps(r"Clay $\cdot$ \$1,000,000", 24, C.muted))]
