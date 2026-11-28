"""s14 riemann (P28): Riemann's private notes (studied by Siegel, 1932) show he computed the first zeros by hand. His
paper: "es ist sehr wahrscheinlich, dass alle Wurzeln reell sind" (very likely all the roots are real: his form of 'all
on the line'), after which he put the search aside. The statement, boxed, over the line of zeros; then a timeline:
1859, Hilbert's problem 8 (1900), the Clay Millennium Prize (2000), today. No scans yet: the notes are an ink card."""
from aion import *

from beats import T
from media_assets import portrait_card, svg_logo
from look import (FLY_U, FLY_XC, FRAME_BOX, GAM, caps, carded, lab, plane_grid, strip_overlay, strip_tags, tex,
                  view_O)


def page(w=2.8, h=3.6):
    return Rectangle(width=w, height=h, stroke_color=C.human, stroke_width=1.6, fill_color=C.bg, fill_opacity=1.0)


def yx(year):
    """Timeline: Manim x of a year."""
    return -5.6 + 11.1 * (year - 1859) / (2026 - 1859)


TL_Y = -3.2


@scene(T.cut_riemann, T.cut_checking)
def s14_riemann(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    O, U = view_O(FLY_XC, float(GAM[5]), FLY_U), FLY_U
    s.shader("zeta_domain.frag", z=0, animated=False, u_origin=O, u_unit=U, u_func=3.0, u_reveal=-1000.0,
             u_opacity=1.0, u_sat=0.85, u_gain=1.0, u_debug=0.0,
             u_dim=keys((T.notes - L, 0.0), (T.notes + 0.6, 1.0, "easy_ease"), (T.thats_rh - L, 1.0),
                        (T.thats_rh + 0.8, 0.55, "easy_ease"), lead=0))
    plane_op = keys((T.notes - L, 1.0), (T.notes + 0.6, 0.3, "easy_ease"), (T.thats_rh - L, 0.3),
                    (T.thats_rh + 0.8, 1.0, "easy_ease"), lead=0)
    pg = s.manim(z=2, parallax=0.0, opacity=plane_op)
    mk = s.manim(z=5, parallax=0.0, opacity=plane_op)
    hud = s.manim(z=6, parallax=0.0)

    # ── s13's last frame ──
    pg.add(plane_grid(O, U, box=FRAME_BOX, mix=1.0))
    ov = strip_overlay(O, U, lit=[1.0] * 6)
    mk.add(ov)
    tags = strip_tags()
    rows = [carded(r, buff=0.12, opacity=1.0) for r in (tags.strip, tags.line, tags.rho)]
    hud.add(*rows)

    # ── Riemann's private notes: he computed the first few zeros by hand ──
    hud.play(FadeOut(VGroup(*rows)), at=T.notes - 0.2, dur=0.5)
    rng = np.random.default_rng(1932)
    sheet = page()
    lines = VGroup()
    for i in range(14):
        w = rng.uniform(0.9, 2.2) if i % 5 != 4 else rng.uniform(0.4, 0.9)
        ln = VMobject(color=C.muted, stroke_width=1.5)
        xs = np.linspace(0, w, 24)
        ln.set_points_smoothly(np.column_stack([xs, 0.025 * np.sin(9 * xs + rng.uniform(0, 6)), 0 * xs]))
        lines.add(ln)
    sums = tex(r"\tfrac12+it", size=26, color=C.human)
    sums.move_to(sheet.get_corner(UL) + [0.3 + sums.width / 2, -0.4, 0])
    lines.arrange(DOWN, buff=0.16, aligned_edge=LEFT).next_to(sums, DOWN, buff=0.22, aligned_edge=LEFT)
    notes = VGroup(sheet, lines, sums).move_to([-4.3, -0.55, 0])
    who = caps(r"Riemann's notes", 44, C.ink)
    by = caps(r"studied by C. L. Siegel $\cdot$ 1932", 28, C.muted)
    head = VGroup(who, by).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    head.move_to([-6.4 + head.width / 2, 2.7, 0])
    hud.play(FadeIn(notes, shift=0.15 * RIGHT), at=T.notes, dur=0.6)
    head = carded(head, buff=0.12, opacity=1.0)
    hud.play(FadeIn(head, shift=0.06 * UP), at=T.notes + 0.5, dur=0.6, lead=0)
    hud.play(Indicate(notes[1][:6], color=C.human, scale_factor=1.04), at=T.by_hand, dur=1.0)

    # ── his paper: "very likely" all on the line ──
    de = Tex(r"\textit{\dots es ist sehr wahrscheinlich, dass alle Wurzeln reell sind.}", font_size=34, color=C.human)
    en = lab("it is very likely that all the roots are real", 28, C.muted)
    yr = caps(r"Riemann $\cdot$ 1859", 26, C.ink)
    quote = VGroup(de, en, yr).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    quote.move_to([-2.3 + quote.width / 2, -2.85, 0])
    qcard = BackgroundRectangle(quote, color=C.bg, fill_opacity=1.0, buff=0.16)
    hud.play(FadeIn(qcard), at=T.very_likely - 0.2, dur=0.4)
    hud.play(Write(de), at=T.very_likely, dur=1.5)
    hud.play(FadeIn(en, shift=0.06 * UP), FadeIn(yr), at=T.very_likely + 1.4, dur=0.6, lead=0)
    flash = Line([O[0] + 0.5 * U, -4.3, 0], [O[0] + 0.5 * U, 4.3, 0]).set_stroke(C.crit, width=9.0)
    mk.play(ShowPassingFlash(flash, time_width=0.5), at=T.very_likely + 1.6, dur=1.2, lead=0)   # on "this line"

    # ── after a few attempts he put aside the search for a proof: the card slides aside ──
    hud.play(notes.animate.shift(4.2 * LEFT).set_opacity(0.0), FadeOut(head, shift=0.6 * LEFT), at=T.put_aside, dur=0.8)
    hud.play(FadeOut(quote), FadeOut(qcard), at=T.put_aside + 0.9, dur=0.6)

    # ── that's the Riemann hypothesis: every nontrivial zero has real part one half ──
    title = caps("The Riemann Hypothesis", 40, C.text)
    stmt = tex(r"\zeta(\rho)=0,\ \ 0<\mathrm{Re}\,\rho<1", r"\ \ \Longrightarrow\ \ ", r"\mathrm{Re}\,\rho=\tfrac12",
               size=44, colors={2: C.crit})
    block = VGroup(title, stmt).arrange(DOWN, buff=0.3)
    box = SurroundingRectangle(block, color=C.text, stroke_width=2.2, buff=0.28, fill_color=C.bg, fill_opacity=1.0)
    VGroup(box, block).move_to([-0.6, 2.35, 0])
    hud.play(FadeIn(box), FadeIn(title, shift=0.06 * DOWN), at=T.thats_rh + 0.5, dur=0.6)
    hud.play(Write(stmt), at=T.every_nontrivial, dur=2.0)
    hud.play(Indicate(stmt[2], color=C.crit, scale_factor=1.12), at=T.every_nontrivial + 2.5, dur=1.0, lead=0)
    glow = Line([O[0] + 0.5 * U, -4.3, 0], [O[0] + 0.5 * U, 4.3, 0])
    mk.play(ShowPassingFlash(glow.set_stroke(C.crit, width=9.0), time_width=0.5), at=T.every_nontrivial + 2.6,
            dur=1.4, lead=0)

    # ── Hilbert, 1900; the Clay Millennium Prize, 2000 ──
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

    m59 = mark(1859, "1859", C.ink, caps(r"Riemann", 24, C.muted))
    m00 = mark(1900, "1900", C.ink, caps(r"D. Hilbert $\cdot$ problem 8", 24, C.muted))
    m20 = mark(2000, "2000", C.ink, caps(r"Clay $\cdot$ \$1,000,000", 24, C.muted))
    m26 = mark(2026, "2026", C.muted)
    hud.play(FadeIn(band), FadeIn(rule), Create(axis), FadeIn(m59), at=T.hilbert, dur=0.8)
    hud.play(FadeIn(m26), at=T.hilbert + 0.5, dur=0.5, lead=0)
    hud.play(FadeIn(m00, shift=0.12 * DOWN), at=T.y1900, dur=0.5)
    hud.play(FadeIn(m20, shift=0.12 * DOWN), at=T.y2000, dur=0.5)
    gone = T.cut_checking - 0.1
    FY = TL_Y + 1.6
    portrait_card(s, hud, "riemann", None, T.hilbert + 0.3, gone, (yx(1859), FY), height=1.4, z=6.5)
    portrait_card(s, hud, "hilbert", None, T.y1900, gone, (yx(1900), FY), height=1.4, z=6.5)
    clay = svg_logo("clay_logo.svg", 0.5, C.ink).move_to([yx(2000), FY, 0])
    hud.play(FadeIn(clay, shift=0.06 * UP), at=T.y2000 + 0.1, dur=0.5)
    hud.play(FadeOut(clay), at=gone - 0.45, dur=0.45, lead=0)
