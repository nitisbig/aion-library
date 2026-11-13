"""Ch6 · Euler's formula. π was never special: the point leaves −1 and walks to any θ, with a green angle arc and
a live θ. How far right: a teal segment on the real axis, cos θ. How far up: a purple leg, sin θ. The formula
builds with each part flying off its segment, e^{iθ} = cos θ + i sin θ, then θ keeps sweeping so the readouts
show it holds everywhere. Badge cos + i sin."""
from aion import *

from beats import T
from shots import P, arrow, backdrop, backing, badge, badges, ease, glyphs, live, plane_grid, rail, ramp, tex

E = "easy_ease"
O, U = (-3.0, -0.55), 2.3


def W(z):
    return P(O, U, z)


@scene(T.cut_ch6, T.cut_helix)
def s09_formula(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)
    m = s.manim(z=2)
    hb = s.manim(z=3, parallax=0.0)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 6)
    badges(hud, 5)

    kin = (t0 + 0.1, t0 + 0.9)
    end_out = (T.cut_helix - 0.8, T.cut_helix - 0.1)

    def stage(t):
        k = ramp(t, *kin) * (1 - ramp(t, *end_out))
        g = plane_grid(O, U / 2, box=(-7.6, -4.4, 7.6, 4.4), n=12, minor=1, opacity=0.38 * k)
        g.add(Circle(radius=U, color=C.ghost, stroke_width=C.thin + 0.6).move_to([*O, 0]).set_stroke(opacity=ramp(t, *kin)))
        return g
    live(bg, stage, kin, end_out)

    # ── "Pi was never special. Walk any distance theta, and you land somewhere on the circle." ──
    th = keys((t0, PI), (T.any_theta + 0.1, PI), (T.any_theta + 2.6, 0.9, E), (T.euler + 0.4, 0.9),
              (T.formula + 1.2, 2.35, "in_out_sine"), lead=0)
    cos_in = (T.how_right - 0.1, T.cos_t + 0.3)
    sin_in = (T.how_up - 0.1, T.sin_t + 0.3)

    def draw(t):
        k = ramp(t, *kin)
        a = th(t)
        z = np.exp(1j * a)
        p = W(z)
        g = VGroup(Arc(radius=U, start_angle=0, angle=a, arc_center=[*O, 0], color=C.arc, stroke_width=C.stroke + 1.5,
                       stroke_opacity=k))
        g.add(Arc(radius=0.55, start_angle=0, angle=a, arc_center=[*O, 0], color=C.arc, stroke_width=C.thin + 1,
                  stroke_opacity=k * (1 - ramp(t, *end_out))))
        g.add(MathTex(r"\theta", font_size=38, color=C.arc).move_to(W(0.36 * np.exp(1j * a / 2)))
              .set_opacity(k * (1 - ramp(t, *end_out))))
        g.add(Line([*O, 0], p, color=C.point, stroke_width=C.stroke, stroke_opacity=0.9 * k))
        ko = 1 - ramp(t, *end_out)
        kc = ease(t, *cos_in) * ko
        if kc > 0.005:                                 # cos θ: how far right, on the real axis
            q = W(z.real)
            g.add(DashedLine(p, q, color=C.muted, stroke_width=C.thin, dash_length=0.1).set_opacity(0.8 * kc))
            g.add(Line([*O, 0], [O[0] + U * z.real * kc, O[1], 0], color=C.cos, stroke_width=C.stroke + 3))
            g.add(MathTex(r"\cos\theta", font_size=38, color=C.cos).move_to(W(z.real / 2) + [0, -0.4, 0])
                  .set_opacity(kc))
        ks = ease(t, *sin_in) * ko
        if ks > 0.005:                                 # sin θ: how far up
            q = W(z.real)
            g.add(Line(q, q + [0, U * z.imag * ks, 0], color=C.sin, stroke_width=C.stroke + 3))
            side = 1 if z.real >= 0 else -1
            g.add(MathTex(r"\sin\theta", font_size=38, color=C.sin).move_to(W(z.real + 0.5j * z.imag) +
                                                                          [side * 0.62, 0, 0]).set_opacity(ks))
        g.add(Dot(p, radius=0.1, color=C.point).set_opacity(k))
        return g
    live(m, draw, kin, (T.any_theta + 0.1, T.any_theta + 2.6), cos_in, sin_in, (T.euler + 0.4, T.formula + 1.2), end_out)
    pl = MathTex(r"\pi", font_size=44, color=C.arc).move_to(W(1.2j) + [0, 0.05, 0])
    m.play(FadeIn(pl), at=kin[0], dur=0.6)
    m.play(FadeOut(pl), at=T.any_theta, dur=0.5)

    # readouts, right side
    rd_in = (T.any_theta, T.any_theta + 0.6)

    def readouts(t):
        k = ramp(t, *rd_in) * (1 - ramp(t, *end_out))
        a = th(t)
        rows = [(r"\theta", C.arc, a, 1.0)]
        rows.append((r"\cos\theta", C.cos, np.cos(a), ramp(t, *cos_in)))
        rows.append((r"\sin\theta", C.sin, np.sin(a), ramp(t, *sin_in)))
        g = VGroup()
        for j, (lab, c, v, kk) in enumerate(rows):
            if kk * k < 0.005:
                continue
            r = VGroup(MathTex(lab, "=", font_size=42).set_color(C.text), DecimalNumber(v, num_decimal_places=2,
                                                                                    font_size=42, color=c))
            r[0][0].set_color(c)
            r.arrange(RIGHT, buff=0.18).move_to([1.55, 1.45 - 0.72 * j, 0], aligned_edge=LEFT)
            g.add(r.set_opacity(k * kk))
        return g

    def rd_box(t):
        k = ramp(t, *rd_in) * (1 - ramp(t, *end_out))
        if k < 0.005:
            return VGroup()
        return Rectangle(width=3.6, height=2.3, stroke_color=C.frame, stroke_width=C.thin * 0.8, fill_color=C.bg,
                         fill_opacity=k).move_to([3.0, 0.75, 0]).set_stroke(opacity=0.8 * k)
    live(hb, rd_box, rd_in, end_out)
    live(hud, readouts, rd_in, (T.any_theta + 0.1, T.any_theta + 2.6), cos_in, sin_in,
         (T.euler + 0.4, T.formula + 1.2), end_out)

    # ── "So e to the i theta equals cosine theta, plus i times sine theta. This is Euler's formula." ──
    f = glyphs(r"e^{i\theta}=\cos\theta+i\sin\theta", {0: C.growth, 1: C.turn, 2: C.arc, 4: C.cos, 5: C.cos, 6: C.cos,
                                                         7: C.cos, 9: C.turn, 10: C.sin, 11: C.sin, 12: C.sin, 13: C.sin},
               size=72, n=14).move_to([0.2, 2.85, 0])
    fb = backing(f, pad=0.22)
    hb.play(FadeIn(fb), at=T.euler - 0.3, dur=0.5)
    hud.play(FadeIn(f[0:3], scale=1.3), at=T.euler, dur=0.6)
    hud.play(FadeIn(f[3]), at=T.euler + 0.7, dur=0.4)
    hud.play(FadeIn(f[4:8], target_position=[0.0, -0.4, 0], scale=0.6), at=T.euler + 1.2, dur=0.8, ease=E)
    hud.play(FadeIn(f[8:10]), at=T.plus_isin + 0.3, dur=0.5)
    hud.play(FadeIn(f[10:14], target_position=[-1.0, 0.4, 0], scale=0.6), at=T.plus_isin + 0.9, dur=0.8, ease=E)
    hud.play(Indicate(f, color=None, scale_factor=1.08), at=T.formula + 0.3, dur=0.9)

    # badge cos + i sin
    hud.play(TransformFromCopy(f[4:14], badge(6)), at=T.cut_helix - 1.3, dur=0.9, ease=E)
    hud.play(FadeOut(f), at=end_out[0], dur=0.6)
    hb.play(FadeOut(fb), at=end_out[0], dur=0.6)
