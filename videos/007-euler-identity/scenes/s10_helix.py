"""Ch6 (cont.) · The helix. Let time run along a third direction: the walk around the circle stretches into a
helix, drawn as crisp vector lines through a hand-made orthographic camera (azimuth/elevation tracks). Its shadows
on two walls are a sine (purple) and a cosine (teal). The camera swings to the side (the helix flattens to the
sine), below (the cosine), and head on (back into the circle). Then three small panels: a turning arrow driving a
spring, an alternating current, and a sound wave."""
from aion import *

from beats import T
from shots import backdrop, badges, ease, live, rail, ramp

E = "easy_ease"
UM, KT = TAU, 0.42                                    # the time axis: centre (in t) and spacing per unit t
WALL = 1.35                                           # the walls sit 1.35 radii out


@scene(T.cut_helix, T.cut_identity)
def s10_helix(s):
    backdrop(s)
    t0 = s.start
    m = s.manim(z=2)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 6)
    badges(hud, 6)

    az = keys((t0, 0.0), (T.third_dir - 0.2, 0.0), (T.helix + 0.2, 50 * DEGREES, E), (T.side - 0.1, 50 * DEGREES),
              (T.sine_wave + 0.2, 90 * DEGREES, E), (T.head_on - 0.1, 90 * DEGREES), (T.collapses + 0.3, 0.0, E),
              lead=0)
    el = keys((t0, 0.0), (T.third_dir - 0.2, 0.0), (T.helix + 0.2, 22 * DEGREES, E), (T.side - 0.1, 22 * DEGREES),
              (T.sine_wave + 0.2, 0.0, E), (T.below - 0.1, 0.0), (T.cos_wave + 0.3, -90 * DEGREES, E),
              (T.head_on - 0.1, -90 * DEGREES), (T.collapses + 0.3, 0.0, E), lead=0)
    glide = (t0 + 0.2, T.third_dir)                   # from s09's circle to the centre
    spread = keys((t0, 0.0), (T.third_dir, 0.0), (T.helix + 0.3, 1.0, E), (T.head_on - 0.1, 1.0), lead=0)
    umax = keys((t0, 2.35), (T.time_runs, 2.35), (T.helix + 0.6, 2 * TAU, "in_out_sine"), lead=0)
    gone = (T.why - 0.5, T.why + 0.3)

    def view(t):
        g = ease(t, *glide)
        c = np.array([(1 - g) * -3.0, (1 - g) * -0.55 + g * -0.25, 0.0])
        R = (1 - g) * 2.3 + g * 1.65
        a, e, sp = az(t), el(t), spread(t)

        def pr(u_t, re, im):                          # (time, re, im) in radii → screen
            tt = (u_t - UM) * KT * sp / 1.65
            sx = re * np.cos(a) + tt * np.sin(a)
            dp = -re * np.sin(a) + tt * np.cos(a)
            sy = im * np.cos(e) + dp * np.sin(e)
            return c + R * np.array([sx, sy, 0.0])
        return pr

    def scene3d(t):
        k = 1 - ramp(t, *gone)
        if k < 0.005:
            return VGroup()
        pr = view(t)
        sp = spread(t)
        um = umax(t)
        us = np.linspace(0, um, max(8, int(um * 24)))
        g = VGroup()
        kw = ramp(t, T.helix - 0.4, T.helix + 0.6) * k
        tl = (0 - UM) - 0.4, (2 * TAU - UM) + 0.4
        if kw > 0.01:                                 # the walls, the time axis
            for corners, colr in (([(tl[0], -WALL, -WALL), (tl[1], -WALL, -WALL), (tl[1], -WALL, WALL),
                                    (tl[0], -WALL, WALL)], C.sin),
                                  ([(tl[0], -WALL, -WALL), (tl[1], -WALL, -WALL), (tl[1], WALL, -WALL),
                                    (tl[0], WALL, -WALL)], C.cos)):
                pts = [pr(UM + a_, b_, c_) for a_, b_, c_ in corners]
                g.add(Polygon(*pts, stroke_color=C.ghost, stroke_width=C.thin, stroke_opacity=kw, fill_opacity=0))
            g.add(Line(pr(UM + tl[0], 0, 0), pr(UM + tl[1] + 0.3, 0, 0), color=C.muted, stroke_width=C.thin,
                       stroke_opacity=kw))
            g.add(MathTex("t", font_size=34, color=C.muted).move_to(pr(UM + tl[1] + 0.75, 0, 0)).set_opacity(kw))
            # shadows: a sine on the back wall, a cosine on the floor
            g.add(VMobject(stroke_color=C.sin, stroke_width=C.stroke, stroke_opacity=kw)
                  .set_points_smoothly([pr(u, -WALL, np.sin(u)) for u in us]))
            g.add(VMobject(stroke_color=C.cos, stroke_width=C.stroke, stroke_opacity=kw)
                  .set_points_smoothly([pr(u, np.cos(u), -WALL) for u in us]))
        else:                                         # before the spread: the circle from s09
            g.add(Circle(radius=1, color=C.ghost, stroke_width=C.thin + 0.6).scale(1).move_to(pr(UM, 0, 0))
                  .set_width(2 * np.linalg.norm(pr(UM, 1, 0) - pr(UM, 0, 0))).set_stroke(opacity=k))
        # the walk itself: green while flat, the yellow helix once time runs
        kh = ramp(t, T.third_dir - 0.2, T.third_dir + 0.6)
        colr = interpolate_color(ManimColor(C.arc), ManimColor(C.point), kh)
        g.add(VMobject(stroke_color=colr, stroke_width=C.stroke + 1.5, stroke_opacity=k)
              .set_points_smoothly([pr(u, np.cos(u), np.sin(u)) for u in us]))
        p = pr(um, np.cos(um), np.sin(um))
        if kw > 0.01:                                 # dashed drops to each wall
            for q in (pr(um, -WALL, np.sin(um)), pr(um, np.cos(um), -WALL)):
                if np.linalg.norm(q - p) > 0.05:
                    g.add(DashedLine(p, q, color=C.muted, stroke_width=C.thin, dash_length=0.08)
                          .set_opacity(0.7 * kw))
        g.add(Line(pr(um, 0, 0), p, color=C.point, stroke_width=C.stroke, stroke_opacity=0.9 * k))
        g.add(Dot(p, radius=0.09, color=C.point).set_opacity(k))
        # the names of the shadows, in their views
        ks = ramp(t, T.sine_wave - 0.3, T.sine_wave + 0.2) * (1 - ramp(t, T.below, T.below + 0.4)) * k
        if ks > 0.01:
            g.add(MathTex(r"\sin t", font_size=46, color=C.sin).move_to(pr(UM + tl[1], -WALL, 1.0) + [0.7, 0.5, 0])
                  .set_opacity(ks))
        kc = ramp(t, T.cos_wave - 0.3, T.cos_wave + 0.2) * (1 - ramp(t, T.head_on, T.head_on + 0.4)) * k
        if kc > 0.01:
            g.add(MathTex(r"\cos t", font_size=46, color=C.cos).move_to(pr(UM + tl[1], 1.0, -WALL) + [0.7, 0.5, 0])
                  .set_opacity(kc))
        return g
    live(m, scene3d, (t0, T.collapses + 0.4), gone)

    # ── "Springs, alternating current, sound. Wherever something oscillates, there is often a turning arrow" ──
    OM = 2.2
    out = (T.cut_identity - 0.8, T.cut_identity - 0.15)
    pulse = (T.arrow_under, T.arrow_under + 1.2)
    xs = (-4.55, 0.0, 4.55)
    cy = -0.1
    ins = (T.springs - 0.35, T.ac - 0.35, T.sound - 0.35)

    def rotor(cx, ang, k, bump):
        c = np.array([cx - 1.3, cy, 0])
        r = 0.6
        tip = c + r * np.array([np.cos(ang), np.sin(ang), 0])
        g = VGroup(Circle(radius=r, color=C.ghost, stroke_width=C.thin).move_to(c).set_stroke(opacity=k),
                   Arrow(c, tip, buff=0, color=C.point, stroke_width=C.stroke + 2 * bump, tip_length=0.14)
                   .set_opacity(k), Dot(c, radius=0.035, color=C.muted).set_opacity(k))
        return g, tip

    def panels(t):
        g = VGroup()
        bump = np.sin(np.pi * np.clip((t - pulse[0]) / (pulse[1] - pulse[0]), 0, 1))
        for j, cx in enumerate(xs):
            k = ramp(t, ins[j], ins[j] + 0.5) * (1 - ramp(t, *out))
            if k < 0.005:
                continue
            g.add(Rectangle(width=4.2, height=2.7, stroke_color=C.frame, stroke_width=C.thin, fill_color=C.bg,
                            fill_opacity=k).move_to([cx, cy, 0]).set_stroke(opacity=k))
            om = OM * (1.7 if j == 2 else 1.0)
            ang = om * (t - ins[j])
            rg, tip = rotor(cx, ang, k, bump)
            g.add(rg)
            if j == 0:                                # a mass on a spring
                my = cy + 0.6 * np.sin(ang)
                top = cy + 1.2
                mx = cx + 0.9
                n = 10
                zz = [[mx, top, 0]] + [[mx + (0.16 if q % 2 else -0.16), top - (top - my - 0.2) * (q + 0.5) / n, 0]
                                      for q in range(n)] + [[mx, my + 0.2, 0]]
                g.add(Line([mx - 0.45, top, 0], [mx + 0.45, top, 0], color=C.muted, stroke_width=C.thin + 1,
                           stroke_opacity=k))
                g.add(VMobject(stroke_color=C.text, stroke_width=C.thin + 0.8, stroke_opacity=k)
                      .set_points_as_corners(zz))
                g.add(Square(0.4, stroke_color=C.text, stroke_width=C.thin + 1, fill_color=C.bg, fill_opacity=k)
                      .move_to([mx, my, 0]).set_stroke(opacity=k))
                g.add(DashedLine(tip, [mx - 0.2, my, 0], color=C.muted, stroke_width=C.thin, dash_length=0.07)
                      .set_opacity(0.7 * k))
            elif j == 1:                              # an alternating current trace
                x0, x1 = cx - 0.45, cx + 1.85
                xx = np.linspace(x0, x1, 60)
                yy = cy + 0.6 * np.sin(ang - (xx - x0) * 2.6)
                g.add(Line([x0, cy, 0], [x1, cy, 0], color=C.ghost, stroke_width=C.thin, stroke_opacity=k))
                g.add(VMobject(stroke_color=C.sin, stroke_width=C.stroke, stroke_opacity=k)
                      .set_points_smoothly([[x, y, 0] for x, y in zip(xx, yy)]))
                g.add(DashedLine(tip, [x0, yy[0], 0], color=C.muted, stroke_width=C.thin, dash_length=0.07)
                      .set_opacity(0.7 * k))
                g.add(MathTex(r"\sim", font_size=40, color=C.muted).move_to([cx + 1.6, cy + 1.0, 0]).set_opacity(k))
            else:                                     # sound: air pushed back and forth
                for q in range(10):
                    x = cx - 0.35 + 0.24 * q + 0.1 * np.cos(ang - 0.7 * q)
                    g.add(Line([x, cy - 0.85, 0], [x, cy + 0.85, 0], color=C.cos, stroke_width=C.thin + 1,
                               stroke_opacity=k))
                g.add(DashedLine(tip, [cx - 0.35 + 0.1 * np.cos(ang), tip[1], 0], color=C.muted,
                                 stroke_width=C.thin, dash_length=0.07).set_opacity(0.7 * k))
        return g
    live(m, panels, (ins[0], out[1]))
