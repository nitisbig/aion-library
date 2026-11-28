"""s20 nearmiss (P38): Lehmer's near-miss. Z(t) on 6995-7015 (zeros about 0.9 apart); a magnifier on 7005.035-7005.13
shows zeros #6709 and #6710 only 0.0377 apart (the average gap there is 0.8955) and the wave climbing only 0.004 above
zero between them. A ghost of the wave lowered by 0.005 misses zero: the two crossings vanish and, in the inset strip,
the two zeros would leave the line as a mirror pair. Then the de Bruijn-Newman constant: RH <=> Lambda <= 0, and
Rodgers & Tao (2018) proved Lambda >= 0, so RH <=> Lambda = 0: no room to spare. Every Z value is computed here."""
from aion import *

from beats import T
from look import EASE, carded, ghost_ring, lab, live, tex
from nearmiss import (G1, G2, GHOST, IU, IX0, IX1, IXC, MX0, MY, PAX, PX0, PX1, PY0, PY1, TX, TY, W0, W1, close,
                      knob_mob, main_plot, mx, panel_curve, px, py, slider)
from noproduct import SHADER, end_frame


@scene(T.cut_nearmiss, T.cut_progress)
def s20_nearmiss(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    out = (T.v_close - 0.9, T.v_close - 0.3)
    s.shader("zeta_domain.frag", z=0, animated=False, **SHADER,
             u_opacity=keys((out[0], 1.0), (out[1], 0.0, EASE), lead=0))
    shade, lines, hud = end_frame()
    o1, o2, o3 = s.manim(z=2), s.manim(z=3), s.manim(z=6, parallax=0.0)
    o1.add(*shade)
    o2.add(*lines)
    o3.add(*hud)
    for m, group in ((o1, shade), (o2, lines), (o3, hud)):
        m.play(*[FadeOut(x) for x in group], at=out[0], dur=out[1] - out[0], lead=0)
    w = s.manim(z=2, parallax=0.0)         # the main plot, the magnified panel, the slider
    h = s.manim(z=6, parallax=0.0)         # names, formulas, labels

    # ── Z(t) near height 7005: crossings about 0.9 apart ──
    M = main_plot()
    axis, curve, zl, pings, who = M.axis, M.curve, M.zl, M.pings, M.who
    w.play(FadeIn(axis), at=T.v_close - 0.2, dur=0.5, lead=0)
    w.play(Create(curve, rate_func=linear), FadeIn(zl), at=T.v_close + 0.2, dur=1.6, lead=0)
    w.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pings], lag_ratio=0.1), at=T.v_close + 0.4, dur=1.6, lead=0)
    h.play(FadeIn(who, shift=0.06 * DOWN), at=T.v_lehmer, dur=0.6)

    # ── the magnifier: 7005.035 to 7005.13 ──
    bx = float(mx((W0 + W1) / 2))
    box = Rectangle(width=0.34, height=0.34, stroke_color=C.text, stroke_width=2.0).move_to([bx, MY, 0])
    pane = Rectangle(width=PX1 - PX0, height=PY1 - PY0, stroke_color=C.faint, stroke_width=1.4)
    pane.move_to([(PX0 + PX1) / 2, (PY0 + PY1) / 2, 0])
    links = VGroup(DashedLine(box.get_corner(DL), pane.get_corner(UL), color=C.faint, stroke_width=1.2),
                   DashedLine(box.get_corner(DR), pane.get_corner(UR), color=C.faint, stroke_width=1.2))
    paxis = Line([PX0, PAX, 0], [PX1, PAX, 0], color=C.axis, stroke_width=1.8)
    w.play(Create(box), at=T.v_near, dur=0.5)
    w.play(TransformFromCopy(box, pane), Create(links), at=T.v_near + 0.4, dur=1.0)
    w.play(Create(paxis), at=T.v_near + 1.2, dur=0.5, lead=0)
    real = panel_curve(0.0, C.text)
    w.play(Create(real[0], rate_func=linear), at=T.v_near + 1.5, dur=1.2, lead=0)
    w.play(*[FadeIn(d, scale=0.5) for d in real[1:]], at=T.v_near + 2.3, dur=0.4, lead=0)
    names = VGroup(tex(r"\gamma_{6709}", size=28, color=C.zero), tex(r"\gamma_{6710}", size=28, color=C.zero))
    names[0].move_to([float(px(G1)) - 0.45, PAX - 0.32, 0])
    names[1].move_to([float(px(G2)) + 0.45, PAX - 0.32, 0])
    h.play(FadeIn(names), at=T.v_near + 2.5, dur=0.5, lead=0)

    # ── about twenty-four times closer than usual ──
    ry = PAX + 0.3
    ruler = DoubleArrow([float(px(G1)), ry, 0], [float(px(G2)), ry, 0], buff=0, color=C.text, stroke_width=2.4,
                        tip_length=0.12, max_tip_length_to_length_ratio=0.25)
    gap = carded(tex(r"0.0377", size=28), buff=0.05, opacity=1.0).next_to(ruler, UP, buff=0.08)
    ratio = tex(r"\frac{0.8955}{0.0377}", r"\approx24", size=34)
    rcap = VGroup(ratio, lab("average gap / this gap", 22, C.muted)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    rcap.move_to([float(px((G1 + G2) / 2)), PY0 + 0.75, 0])        # inside the arch, below the axis
    w.play(GrowFromCenter(ruler), at=T.v_24, dur=0.6)
    h.play(FadeIn(gap), at=T.v_24 + 0.3, dur=0.4, lead=0)
    h.play(FadeIn(rcap, shift=0.06 * DOWN), at=T.v_24 + 0.9, dur=0.6, lead=0)

    # ── between them, the wave climbs only four thousandths ──
    tt, zz = close()
    k = np.argmax(np.where((tt > G1) & (tt < G2), zz, -1))
    peak = np.array([float(px(tt[k])), float(py(zz[k])), 0])
    pk = VGroup(DashedLine(peak, [peak[0], PAX, 0], color=C.text, stroke_width=1.6, dash_length=0.05),
                Dot(peak, radius=0.06, color=C.text))
    mz = carded(tex(r"\max Z\approx0.004", size=28), buff=0.05, opacity=1.0)
    mz.move_to(peak + [1.35, 0.15, 0])
    h.play(FadeOut(gap), at=T.v_between, dur=0.4)
    w.play(FadeOut(ruler), at=T.v_between, dur=0.4)
    w.play(Create(pk), at=T.v_four - 0.3, dur=0.5)
    h.play(FadeIn(mz), at=T.v_four, dur=0.5)

    # ── if it had turned back just short of zero: no crossings, and the two zeros leave the line ──
    back = (T.v_2018 - 0.3, T.v_2018 + 0.6)                 # restore, after "mirror pair."
    drop = keys((T.v_if - L, 0.0), (T.v_if - L + 2.0, 1.0, EASE), (back[0], 1.0), (back[1], 0.0, EASE), lead=0)
    ghost_on = (T.v_if - L, back[1])
    def faint(m):                                   # a dimmed copy: stroke and fill scaled, never filled
        c = m.copy()
        for x in c.family_members_with_points():
            x.set_stroke(opacity=0.3 * x.get_stroke_opacity()).set_fill(opacity=0.3 * x.get_fill_opacity())
        return c

    was = VGroup(real, pk)
    dimmed = faint(was)
    w.play(FadeOut(was), FadeIn(dimmed), at=T.v_if - L, dur=0.4, lead=0)
    h.play(mz.animate.set_opacity(0.3), at=T.v_if - L, dur=0.4, lead=0)
    gh = live(w, lambda t: panel_curve(GHOST * float(drop(t)), C.rogue, width=2.8), ghost_on)
    w.remove(gh[-1], at=ghost_on[1])
    again = was.copy()
    w.play(FadeOut(dimmed), FadeIn(again), at=ghost_on[1] - 0.05, dur=0.3, lead=0)
    short = carded(tex(r"Z-0.005", size=28, color=C.rogue), buff=0.05, opacity=1.0)
    short.move_to([float(px(W1)) - 0.85, PAX + 0.45, 0])
    h.play(FadeIn(short), at=T.v_if + 0.6, dur=0.5)

    ipane = Rectangle(width=IX1 - IX0, height=PY1 - PY0, stroke_color=C.faint, stroke_width=1.4)
    ipane.move_to([(IX0 + IX1) / 2, (PY0 + PY1) / 2, 0])
    strip = VGroup(Line([IXC - IU / 2, PY0, 0], [IXC - IU / 2, PY1, 0], color=C.faint, stroke_width=1.2),
                   Line([IXC + IU / 2, PY0, 0], [IXC + IU / 2, PY1, 0], color=C.faint, stroke_width=1.2),
                   Line([IXC, PY0, 0], [IXC, PY1, 0], color=C.crit, stroke_width=2.2))
    icap = lab("zeros", 24, C.zero).move_to([IX0 + 0.45, PY1 - 0.24, 0])
    ym, dy = (PY0 + PY1) / 2, 0.35
    split = keys((T.v_leave - L, 0.0), (T.v_leave - L + 1.5, 1.0, EASE), (back[0], 1.0), (back[1], 0.0, EASE), lead=0)

    def pair(t):
        u = float(split(t))
        if u <= 0.5:                                    # they slide together along the line ...
            a = u / 0.5
            return VGroup(Dot([IXC, ym + dy * (1 - a), 0], radius=0.08, color=C.zero),
                          Dot([IXC, ym - dy * (1 - a), 0], radius=0.08, color=C.zero))
        a = (u - 0.5) / 0.5                              # ... then leave it as a mirror pair
        d = 0.42 * IU * a
        return VGroup(ghost_ring(IXC + d, ym), ghost_ring(IXC - d, ym, dashed=True))

    p0 = pair(T.v_if)
    w.play(FadeIn(ipane), FadeIn(strip), FadeIn(icap), FadeIn(p0), at=T.v_if + 1.4, dur=0.6, lead=0)
    w.remove(p0, at=T.v_leave - L)
    held = live(w, pair, (T.v_leave - L, back[1]))
    mirror = lab("mirror pair", 24, C.rogue).move_to([IXC, ym - 0.6, 0])
    h.play(FadeIn(mirror), at=T.v_leave + 0.5, dur=0.5, lead=0)
    h.play(FadeOut(mirror), FadeOut(short), at=back[0], dur=0.4, lead=0)

    # ── no room to spare: RH <=> Lambda <= 0; Rodgers & Tao: Lambda >= 0 ──
    clear = back[1] + 0.1
    w.play(FadeOut(VGroup(pane, paxis, again, links, box, ipane, strip, icap, held[-1])), at=clear, dur=0.5, lead=0)
    h.play(FadeOut(VGroup(names, rcap, mz)), at=clear, dur=0.5, lead=0)
    w.remove(*held[:-1], at=clear)
    S = slider()
    row1, track, out_zone, wall, ruled, row2 = S.row1, S.track, S.out_zone, S.wall, S.ruled, S.row2
    h.play(FadeIn(row1, shift=0.06 * DOWN), at=clear + 0.5, dur=0.6, lead=0)
    w.play(Create(track[0]), FadeIn(track[1:]), at=clear + 0.6, dur=0.6, lead=0)
    w.play(FadeIn(out_zone), Create(wall), at=T.v_rodgers, dur=0.6)
    h.play(FadeIn(row2, shift=0.06 * DOWN), FadeIn(ruled), at=T.v_rodgers + 0.3, dur=0.6)

    lam = keys((T.v_iftrue - L, 0.3), (T.v_room + 1.16 - 0.1, 0.0, "in_cubic"), (T.v_room + 1.16 + 0.12, 0.02),
               (T.v_room + 1.16 + 0.35, 0.0, EASE), lead=0)

    def knob(t):
        return knob_mob(lam(t))

    k0 = knob(T.v_precise)
    w.play(FadeIn(k0, scale=0.7), at=T.v_precise, dur=0.5)
    w.remove(k0, at=T.v_iftrue - L)
    live(w, knob, (T.v_iftrue - L, T.v_room + 1.16 + 0.35))
    iftrue = S.iftrue
    h.play(FadeIn(iftrue), at=T.v_iftrue, dur=0.5)
    row1b = S.row1b
    h.play(TransformMatchingTex(row1, row1b), Indicate(wall, color=C.text, scale_factor=1.0),
           at=T.v_room + 1.3, dur=0.7, lead=0)
