"""Ch4 · Compounding a turn. The bank's staircase returns in a small panel: e came from (1 + 1/n)^n. Swap the 1
for iπ: (1 + iπ/n)^n. On the plane each factor (1 + iπ/n) is a step at right angles to where you stand, of length
π/n times your distance: a chain of similar right triangles. n = 1 shoots to 1 + πi, n = 2 lands at −1.47 + 3.14i,
then 4, 8, 16, 100: the path bends, spirals in, hugs the unit circle and lands on −1. A ledger keeps every value.
Compounding growth gave e; compounding a turn gives a walk around the circle. The first check slot fills."""
from aion import *

from beats import T
from shots import (arrow, backdrop, backing, badge, badges, ease, glyphs, icon, live, panel, plane_grid, rail, ramp,
                   right_angle, tex)

E = "easy_ease"
O = (-0.2, -1.8)                                      # the plane: origin (world), unit 1
MINI = (-3.7, 0.75)                                   # the bank panel's centre (phase 1)
LED = (4.8, 0.05)                                     # the ledger panel's centre
ROW0, ROWS = 1.65, 0.6


def W(z):
    z = complex(z)
    return np.array([O[0] + z.real, O[1] + z.imag, 0.0])


def chain(n):
    return (1 + 1j * PI / n) ** np.arange(n + 1)


def cfmt(z):
    s = f"{z.real:.2f}" + ("+" if z.imag >= 0 else "-") + f"{abs(z.imag):.2f}i"
    return s.replace("-", "{-}")


@scene(T.cut_ch4, T.cut_ch5)
def s07_compound_turn(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)
    m = s.manim(z=2)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 4)
    badges(hud, 3)
    slots = VGroup(*[DashedVMobject(RoundedRectangle(width=1.0, height=0.46, corner_radius=0.06, color=C.muted,
                                                     stroke_width=C.thin + 0.6), num_dashes=22)
                     .move_to(badge(k)).align_to(badge(k), LEFT).shift(0.08 * LEFT) for k in (4, 5)])
    hud.add(slots, at=t0)

    # ── "Go back to the bank. e came from compounding." the staircase, in a small panel ──
    pw, ph = 4.6, 3.3
    box = panel(*MINI, pw, ph)
    bank = icon("bank", 0.62).move_to([MINI[0] - pw / 2 + 0.55, MINI[1] + ph / 2 - 0.5, 0])
    mo = np.array([MINI[0] - 1.65, MINI[1] - 1.25, 0])
    ux, uy = 3.3, 0.78

    def mp(t, y):
        return mo + [ux * t, uy * y, 0]
    axes = VGroup(Line(mp(0, 0), mp(1.08, 0), color=C.axis, stroke_width=C.thin),
                  Line(mp(0, 0), mp(0, 3.1), color=C.axis, stroke_width=C.thin))
    pts, y = [mp(0, 1)], 1.0
    for k in range(12):
        pts += [mp((k + 1) / 12, y), mp((k + 1) / 12, y * (1 + 1 / 12))]
        y *= 1 + 1 / 12
    stairs = VMobject(stroke_color=C.growth, stroke_width=C.stroke).set_points_as_corners(pts)
    e_lab = MathTex("e", font_size=48, color=C.growth).next_to(mp(1, np.e), RIGHT, buff=0.12)
    mini = VGroup(box, bank, axes, stairs, e_lab)
    hud.play(FadeIn(box), FadeIn(bank, shift=0.1 * DOWN), Create(axes), at=T.back_bank - 0.1, dur=0.7)
    hud.play(Create(stairs), at=T.compounding, dur=1.6, ease=E)
    hud.play(FadeIn(e_lab, scale=1.3), at=T.compounding + 1.5, dur=0.5)

    # ── "One plus one over n, raised to the n." · "One plus i pi over n, raised to the n." ──
    A = glyphs(r"\left(1+\tfrac{1}{n}\right)^{n}\to e", {9: C.growth}, size=68, n=10).move_to([2.7, 1.35, 0])
    B = glyphs(r"\left(1+\tfrac{i\pi}{n}\right)^{n}\to\,?", {3: C.turn, 4: C.arc, 10: C.point}, size=68,
               n=11).move_to([2.7, -0.35, 0]).align_to(A, LEFT)
    hud.play(LaggedStart(*[FadeIn(g, shift=0.1 * UP) for g in A[:8]], lag_ratio=0.12), at=T.lim_e, dur=1.3)
    hud.play(FadeIn(A[8:], shift=0.1 * LEFT), at=T.lim_e + 1.6, dur=0.6)
    hud.play(TransformFromCopy(A[0:3], B[0:3]), TransformFromCopy(A[4:9], B[5:10]), at=T.lim_ipi - 0.1, dur=1.2,
             ease=E)
    hud.play(FadeIn(B[3:5], shift=0.35 * DOWN, scale=1.5), at=T.lim_ipi + 0.35, dur=0.7)
    hud.play(FadeIn(B[10], scale=1.4), at=T.lim_ipi + 1.6, dur=0.5)

    # ── "Start crude." the bank and e step aside; B becomes the ledger's header ──
    clear1 = T.crude - 0.4
    hud.play(FadeOut(mini), FadeOut(A), at=clear1, dur=0.6)
    lp = panel(*LED, 3.5, 5.0)
    hdr_n = MathTex("n", font_size=40, color=C.muted).move_to([LED[0] - 1.25, LED[1] + 2.05, 0])
    hdr = B[:9].copy().scale(44 / 68).move_to([LED[0] + 0.45, LED[1] + 2.05, 0])
    rule = Line([LED[0] - 1.6, LED[1] + 1.68, 0], [LED[0] + 1.6, LED[1] + 1.68, 0], color=C.frame,
                stroke_width=C.thin)
    hud.play(FadeIn(lp), at=clear1 + 0.3, dur=0.6)
    hud.play(ReplacementTransform(B[:9], hdr), FadeOut(B[9:]), at=clear1 + 0.4, dur=1.0, ease=E)
    hud.play(FadeIn(hdr_n), Create(rule), at=clear1 + 1.0, dur=0.6)

    # the plane
    kp = (T.crude - 0.2, T.crude + 0.8)

    def stage(t):
        k = ramp(t, *kp)
        g = plane_grid(O, 1.0, box=(-7.6, -4.4, 7.6, 4.4), n=12, minor=2, opacity=0.38 * k)
        hl = ramp(t, T.hugs - 0.3, T.hugs + 0.5) * (1 - 0.5 * ramp(t, T.growth_e - 0.5, T.growth_e + 0.3))
        g.add(Circle(radius=1.0, color=C.text if hl > 0.01 else C.ghost, stroke_width=C.thin + 0.6 + 1.0 * hl)
              .move_to([*O, 0]).set_stroke(opacity=k * (0.55 + 0.45 * hl)))
        return g
    live(bg, stage, kp, (T.hugs - 0.3, T.hugs + 0.5), (T.growth_e - 0.5, T.growth_e + 0.3))

    # ── the chain, n by n ──
    phases = [(1, (T.one_ipi - 0.1, T.one_ipi + 1.1)), (2, (T.mult2 + 0.2, T.land_here - 0.2)),
              (4, (T.n4 + 0.2, T.n4 + 2.6)), (8, (T.n8 - 0.05, T.n8 + 0.9)), (16, (T.n16 - 0.05, T.n16 + 0.9)),
              (100, (T.n100 - 0.05, T.n100 + 1.5))]
    n2_steps = ((T.mult2 + 0.2, T.mult2 + 1.4), (T.land_here - 1.5, T.land_here - 0.3))
    base_in = (T.n1 - 0.1, T.n1 + 0.5)

    def progress(j, t):
        n, (a, b) = phases[j]
        if n == 2:
            return sum(ease(t, *w) for w in n2_steps)
        return n * ramp(t, a, b) if n > 4 else n * np.clip((t - a) / (b - a), 0, 1)

    def path(n, p, k, ghost=False):
        zs = chain(n)
        g = VGroup()
        full = int(np.floor(p + 1e-9))
        pts = [W(z) for z in zs[:full + 1]]
        if full < n and p > full:
            pts.append(W(zs[full] + (p - full) * (zs[full + 1] - zs[full])))
        col = C.ghost if ghost else C.point
        if len(pts) > 1:
            g.add(VMobject(stroke_color=col, stroke_width=(C.thin + 0.6) if ghost else C.stroke + 0.5,
                           stroke_opacity=k).set_points_as_corners(pts))
        if not ghost and n <= 16:                      # the triangles' radial legs
            for z in zs[1:full + 1]:
                g.add(Line(W(0), W(z), color=C.muted, stroke_width=C.thin * 0.8, stroke_opacity=0.5 * k))
        if not ghost and n <= 4:                       # right angles where each step leaves
            for z0 in zs[:min(full + (1 if p > full else 0), n)]:
                u = z0 / abs(z0)
                g.add(right_angle(W(z0), -np.array([u.real, u.imag]), np.array([-u.imag, u.real]), size=0.14,
                                  color=C.muted, k=k))
        if not ghost and len(pts) > 1:
            g.add(Dot(pts[-1], radius=0.08, color=C.point).set_opacity(k))
        return g

    out_all = (T.growth_e - 0.6, T.growth_e + 0.2)

    def compound(t):
        g = VGroup()
        kb = ramp(t, *base_in)
        if kb < 0.005:
            return g
        g.add(arrow(W(0), W(1), C.growth, width=C.stroke).set_opacity(kb))      # the starting 1
        cur = -1
        for j, (n, (a, b)) in enumerate(phases):
            if t >= a - 0.25:
                cur = j
        for j in range(max(cur, 0)):                   # earlier paths, faint
            g.add(path(phases[j][0], phases[j][0], 0.5 * (1 - 0.6 * ramp(t, *out_all)), ghost=True))
        if cur >= 0:
            n = phases[cur][0]
            kf = 1 - 0.0 * ramp(t, *out_all)
            g.add(path(n, progress(cur, t), kf))
        return g
    live(m, compound, base_in, *[(a - 0.3, b + 0.05) for _, (a, b) in phases], out_all)

    # n = 1: legs 1 and π · n = 2: legs 1 and π/2 (a little turn, a little stretch)
    l1 = VGroup(MathTex("1", font_size=34, color=C.growth).move_to(W(0.5) + [0, -0.3, 0]),
                MathTex(r"\pi", font_size=40, color=C.arc).move_to(W(1 + 1.57j) + [0.35, 0, 0]))
    m.play(FadeIn(l1), at=T.one_ipi + 1.0, dur=0.5)
    m.play(FadeOut(l1), at=T.n2 - 0.3, dur=0.4)
    l2 = MathTex(r"\tfrac{\pi}{2}", font_size=36, color=C.arc).move_to(W(1 + 0.78j) + [0.38, 0, 0])
    m.play(FadeIn(l2), at=T.mult2 + 1.3, dur=0.5)
    m.play(FadeOut(l2), at=T.n4 - 0.3, dur=0.4)
    tarc = Arc(radius=0.45, start_angle=0, angle=np.arctan(PI / 2), arc_center=W(0), color=C.turn,
               stroke_width=C.thin + 1)
    m.play(Create(tarc), at=T.mult2 + 1.6, dur=0.6)                        # "turns the plane a little"
    m.play(FadeOut(tarc), at=T.n4 - 0.3, dur=0.4)

    # "Nowhere near": −1 marked
    m1 = VGroup(Circle(radius=0.13, color=C.point, stroke_width=C.thin + 1).move_to(W(-1)),
                MathTex("-1", font_size=34, color=C.point).move_to(W(-1) + [-0.1, -0.38, 0]))
    m.play(FadeIn(m1), at=T.nowhere, dur=0.5)

    # the ledger: a row as each n lands
    rows = []
    for j, (n, (a, b)) in enumerate(phases):
        z = chain(n)[-1]
        y = LED[1] + ROW0 - ROWS * (j + 0.5)
        row = VGroup(MathTex(str(n), font_size=36, color=C.text).move_to([LED[0] - 1.25, y, 0]),
                     MathTex(cfmt(z), font_size=34, color=C.point).move_to([LED[0] + 0.45, y, 0]))
        rows.append(row)
        hud.play(FadeIn(row, shift=0.1 * LEFT), at=b - 0.1, dur=0.4)
        if j > 0:
            hud.play(rows[j - 1].animate.set_opacity(0.55), at=b - 0.1, dur=0.4)
    inf = VGroup(MathTex(r"\infty", font_size=38, color=C.text).move_to([LED[0] - 1.25, LED[1] - 2.0, 0]),
                 MathTex("-1", font_size=40, color=C.point).move_to([LED[0] + 0.45, LED[1] - 2.0, 0]))
    hud.play(rows[-1].animate.set_opacity(0.55), FadeIn(inf, shift=0.1 * DOWN), at=T.landed, dur=0.6)

    # ── "The stretches shrink… the turns add up… the path hugs the unit circle… its final spot. Negative one." ──
    s.camera.frame(T.hugs - 0.8, center=(O[0] - 0.2, O[1] + 0.35), zoom=1.9, dur=2.6)
    ring = Circle(radius=0.12, color=C.point, stroke_width=C.thin + 1.5).move_to(W(-1))
    m.play(FadeIn(ring, scale=0.5), at=T.landed - 0.1, dur=0.2)
    m.play(FadeOut(ring, scale=3.0), at=T.landed + 0.2, dur=0.8)

    # ── "Compounding a rate of growth gives e. Compounding a rate of turning gives a walk around the circle." ──
    s.camera.frame(T.growth_e - 0.7, center=(0.0, 0.0), zoom=1.0, dur=1.3)
    mini2 = VGroup(box, bank, axes, stairs, e_lab).copy().scale(0.62).move_to([-5.0, 1.75, 0])
    hud.play(FadeIn(mini2, shift=0.15 * RIGHT), at=T.growth_e - 0.1, dur=0.7)
    hud.play(Indicate(mini2[4], color=None, scale_factor=1.4), at=T.growth_e + 1.0, dur=0.7)
    walk = Arc(radius=1.0, start_angle=0, angle=PI, arc_center=W(0), color=C.arc, stroke_width=C.stroke + 2)
    m.play(Create(walk), at=T.turning_circle + 0.1, dur=1.1, ease=E)

    # the first check slot fills: the ledger's formula becomes the badge
    b4 = badge(4)
    hud.play(ReplacementTransform(hdr, b4), FadeOut(slots[0]), at=T.cut_ch5 - 1.3, dur=0.9, ease=E)
    hud.play(FadeOut(VGroup(lp, hdr_n, rule, inf, *rows, mini2)), at=T.cut_ch5 - 1.0, dur=0.7)
    m.play(FadeOut(VGroup(walk, m1)), at=T.cut_ch5 - 0.9, dur=0.6)
