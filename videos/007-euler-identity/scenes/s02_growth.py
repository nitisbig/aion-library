"""Ch1 (cont.) · The defining property. The year-long axes widen into the graph of e^t. A point rides it with its
height bar and a slope triangle (run 1, rise = slope): the two numbers are always equal. Then the same idea as
motion: a point on a line whose velocity arrow is as long as its position, so it runs away faster and faster.
v = x, the heart of e, and a red i drifts in above the equals sign: one word is about to change."""
from aion import *

from beats import T
from shots import (BANK_O, BANK_UX, BANK_UY, I_POS, arrow, backdrop, badge, coin, ease, glyphs, graph_axes, live,
                   ramp, rail, stopwatch, tex)

E = "easy_ease"
VA = dict(ox=BANK_O[0], oy=BANK_O[1], ux=BANK_UX, uy=BANK_UY, t0=0.0, t1=1.08, ymax=3.05)     # the bank axes
VB = dict(ox=-1.1, oy=-2.9, ux=2.6, uy=1.15, t0=-2.1, t1=1.65, ymax=5.0)                      # the e^t graph
NL_Y, NL_O, NL_U = -0.55, -5.6, 1.0                   # the number line: height, where 0 sits, unit
RATE = 0.6                                            # motion: x = e^{RATE (t - go)} (time is slowed, v = x still)


def view(u):
    return {k: (1 - u) * VA[k] + u * VB[k] for k in VA}


def W(v, t, y):
    return np.array([v["ox"] + v["ux"] * t, v["oy"] + v["uy"] * y, 0.0])


def num(x, color, size=34):
    return DecimalNumber(x, num_decimal_places=2, font_size=size, color=color)


@scene(T.cut_growth, T.cut_ch2)
def s02_growth(s):
    backdrop(s)
    t0 = s.start
    m = s.manim(z=2)
    hud = s.manim(z=4, parallax=0.0)
    rail(hud, 1)

    # ── "When interest is paid continuously…": the bank axes widen into the graph of e^t ──
    mo = (T.continuously, T.continuously + 1.7)
    gone = (T.motion + 0.1, T.motion + 0.9)           # the graph leaves for the number line

    def graph(t):
        u = ease(t, *mo)
        k = 1 - ramp(t, *gone)
        v = view(u)
        g = VGroup(graph_axes((v["ox"], v["oy"]), v["ux"], v["uy"], v["t0"], v["t1"], v["ymax"], xticks=(0.5, 1),
                              yticks=(1, 2, 3), opacity=(1 - u) * k, ylab=r"\$" if u < 0.5 else None),
                   graph_axes((v["ox"], v["oy"]), v["ux"], v["uy"], v["t0"], v["t1"], v["ymax"], xticks=(-2, -1, 1),
                              yticks=(1, 2, 3, 4), opacity=u * k, tlab="t", ylab="y" if u >= 0.5 else None))
        a = (1 - u) * 0.0 + u * v["t0"]               # the curve: from the year [0, 1] out to the full range
        b = (1 - u) * 1.0 + u * 1.5
        ts = np.linspace(a, b, 120)
        g.add(VMobject(stroke_color=C.growth, stroke_width=C.stroke + 0.5, stroke_opacity=k)
              .set_points_smoothly([W(v, x, np.exp(x)) for x in ts]))
        return g
    live(m, graph, (t0, t0 + 0.05), mo, gone)
    e_lab = tex("e", size=60, color=C.growth).next_to(W(VA, 1.06, np.e), RIGHT, buff=0.1)
    m.add(e_lab, at=t0)
    m.play(FadeOut(e_lab), at=T.continuously - 0.2, dur=0.6)

    # ── a point, its height, and its slope triangle (run 1, rise = slope) ──
    tp = keys((t0, 0.0), (T.hold2 + 0.1, 0.0), (T.hold2 + 0.6, np.log(2.0), E),
              (T.slope - 0.2, np.log(2.0)), (T.slope + 0.9, -1.3, "in_out_sine"),
              (T.height + 1.4, 0.9, "in_out_sine"), lead=0)
    shown = (T.hold1 - 0.3, T.hold1 + 0.3)

    def tri(t):
        k = ramp(t, *shown) * (1 - ramp(t, *gone))
        x = tp(t)
        y = np.exp(x)
        p, q, r = W(VB, x, y), W(VB, x + 1, y), W(VB, x + 1, 2 * y)
        g = VGroup(
            Line(W(VB, x, 0), p, color=C.text, stroke_width=C.thin + 0.4, stroke_opacity=0.8 * k),     # height
            Line(p, q, color=C.muted, stroke_width=C.thin + 0.4, stroke_opacity=k),                      # run 1
            Line(q, r, color=C.growth, stroke_width=C.stroke, stroke_opacity=k),                         # rise
            DashedLine(p, r, color=C.growth, stroke_width=C.thin, dash_length=0.08).set_opacity(0.7 * k),
            Dot(p, radius=0.08, color=C.growth).set_opacity(k))
        g.add(num(y, C.text).next_to((W(VB, x, 0) + p) / 2, LEFT, buff=0.12).set_opacity(k))
        g.add(num(y, C.growth).next_to((q + r) / 2, RIGHT, buff=0.12).set_opacity(k))
        g.add(tex("1", size=30, color=C.muted).next_to((p + q) / 2, DOWN, buff=0.1).set_opacity(k))
        return g
    live(m, tri, shown, (T.hold2 + 0.05, T.hold2 + 0.65), (T.slope - 0.25, T.height + 1.45), gone)

    # "paid continuously": a stopwatch sweeping without ticks
    sw = (T.continuously - 0.3, T.hold1 + 0.6)

    def watch(t):
        k = ramp(t, sw[0], sw[0] + 0.4) * (1 - ramp(t, sw[1] - 0.5, sw[1]))
        if k < 0.005:
            return VGroup()
        return stopwatch(TAU * (t - sw[0]) / 2.4, 1.15, k).move_to([5.6, 2.45, 0])
    live(hud, watch, sw)

    # "Hold one dollar, and you gain one dollar per year. Hold two, and you gain two." coins beside the rise
    g1 = coin(0.2).move_to(W(VB, 1.0, 1.5) + [1.25, 0, 0])
    g2 = VGroup(coin(0.2), coin(0.2)).arrange(UP, buff=0.06).move_to(W(VB, np.log(2) + 1, 3.0) + [1.3, 0, 0])
    m.play(FadeIn(g1, scale=1.5), at=T.hold1 + 1.5, dur=0.5)
    m.play(FadeOut(g1), at=T.hold2 - 0.1, dur=0.4)
    m.play(LaggedStart(*[FadeIn(c, scale=1.5) for c in g2], lag_ratio=0.3), at=T.hold2 + 1.1, dur=0.6)
    m.play(FadeOut(g2), at=T.slope - 0.4, dur=0.5)

    et = tex("e^{t}", size=60, color=C.growth).next_to(W(VB, 1.42, np.exp(1.42)), LEFT, buff=0.25)
    m.play(FadeIn(et, shift=0.1 * UP), at=T.et, dur=0.5)
    m.play(FadeOut(et), at=gone[0], dur=gone[1] - gone[0], lead=0)

    # ── "Or picture it as motion. A point on a line, whose velocity is always equal to its position." ──
    nl_in = (T.motion + 0.6, T.motion + 1.6)
    nl_out = (T.sentence - 0.3, T.sentence + 0.5)
    go = T.vel_pos + 1.85                             # it starts to run on "…to its position"

    def X(t):
        return 1.0 if t < go else float(np.exp(RATE * (t - go)))

    def line(t):
        k = ramp(t, *nl_in) * (1 - ramp(t, *nl_out))
        if k < 0.005:
            return VGroup()
        g = VGroup(Line([-7.3, NL_Y, 0], [15.0, NL_Y, 0], color=C.axis, stroke_width=C.thin * 1.2, stroke_opacity=k))
        for n in range(0, 21):
            x = NL_O + NL_U * n
            g.add(Line([x, NL_Y - 0.08, 0], [x, NL_Y + 0.08, 0], color=C.axis, stroke_width=C.thin,
                       stroke_opacity=k))
            g.add(MathTex(str(n), font_size=28, color=C.muted).move_to([x, NL_Y - 0.36, 0]).set_opacity(k))
        return g
    live(m, line, nl_in, nl_out)

    pt_in = (T.pt_line - 0.2, T.pt_line + 0.3)
    v_in = (T.vel_pos - 0.1, T.vel_pos + 0.5)

    def runner(t):                                    # world: the point, its velocity, its streak and ghosts
        k = ramp(t, *pt_in) * (1 - ramp(t, *nl_out))
        kv = ramp(t, *v_in) * (1 - ramp(t, *nl_out))
        if k < 0.005:
            return VGroup()
        x = X(t)
        px = NL_O + NL_U * x
        g = VGroup()
        for j in range(1, 14):                        # ghosts every 0.5 s of motion
            tg = go + 0.5 * j
            if tg >= t - 0.05:
                break
            g.add(Dot([NL_O + NL_U * X(tg), NL_Y, 0], radius=0.07, color=C.growth)
                  .set_opacity(k * 0.45 * np.exp(-(t - tg) / 1.6)))
        if t > go + 0.05:                             # a streak over the last 0.45 s: longer as it speeds up
            xs = [NL_O + NL_U * X(t - 0.45 * u) for u in np.linspace(0, 1, 6)]
            for a_, b_, op in zip(xs[:-1], xs[1:], np.linspace(0.75, 0.1, 5)):
                g.add(Line([b_, NL_Y, 0], [a_, NL_Y, 0], color=C.growth, stroke_width=7, stroke_opacity=op * k))
        if kv > 0.01:
            g.add(arrow([px, NL_Y, 0], [px + NL_U * x * kv, NL_Y, 0], C.vel, width=C.stroke + 1, tip=0.22)
                  .set_opacity(kv))
        g.add(Dot([px, NL_Y, 0], radius=0.1, color=C.growth).set_opacity(k))
        return g
    live(m, runner, pt_in, v_in, (go, nl_out[1]))

    # the camera follows the runner, then lets it escape
    s.camera.pan(go + 0.6, to=(3.2, 0.0), dur=3.0, ease="in_out_sine")
    s.camera.pan(T.sentence + 0.2, to=(0.0, 0.0), dur=0.9)

    # HUD: the readouts, and a framed graph of x against time tracing in step with the runner
    GP = (4.55, 2.1)                                  # graph panel centre
    gpw, gph = 3.7, 2.3
    gox, goy = GP[0] - 1.45, GP[1] - 0.85             # its origin
    gux, guy = 2.75 / 2.7, 1.55 / 14.0                # tau 0..2.7, x 0..14

    def hud_draw(t):
        k = ramp(t, *pt_in) * (1 - ramp(t, *nl_out))
        kv = ramp(t, *v_in) * (1 - ramp(t, *nl_out))
        kg = ramp(t, go - 0.6, go) * (1 - ramp(t, *nl_out))
        if k < 0.005:
            return VGroup()
        x = X(t)
        rx = VGroup(tex("x", "=", size=46, colors={0: C.growth}), num(x, C.growth, 46)).arrange(RIGHT, buff=0.18)
        rv = VGroup(tex("v", "=", size=46, colors={0: C.vel}), num(x, C.vel, 46)).arrange(RIGHT, buff=0.18)
        hudr = VGroup(rx, rv).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([-4.6, 2.3, 0], aligned_edge=LEFT)
        hudr[0].set_opacity(k)
        hudr[1].set_opacity(kv)
        g = VGroup(hudr)
        if kg > 0.005:
            box = Rectangle(width=gpw, height=gph, stroke_color=C.frame, stroke_width=C.thin, fill_color=C.bg,
                            fill_opacity=kg).move_to([*GP, 0]).set_stroke(opacity=kg)
            axes = VGroup(Line([gox, goy, 0], [gox + 2.9, goy, 0], color=C.axis, stroke_width=C.thin),
                          Line([gox, goy, 0], [gox, goy + 1.7, 0], color=C.axis, stroke_width=C.thin)).set_opacity(kg)
            tau = max(0.0, RATE * (t - go))
            ts = np.linspace(0, min(tau, 2.7), 50)
            g.add(box, axes)
            g.add(MathTex("t", font_size=26, color=C.muted).move_to([gox + 3.05, goy, 0]).set_opacity(kg))
            g.add(MathTex("x", font_size=26, color=C.growth).move_to([gox, goy + 1.88, 0]).set_opacity(kg))
            if tau > 0.02:
                g.add(VMobject(stroke_color=C.growth, stroke_width=C.stroke, stroke_opacity=kg)
                      .set_points_smoothly([[gox + gux * u, goy + guy * np.exp(u), 0] for u in ts]))
            yv = min(np.exp(min(tau, 2.7)), 14.0)
            g.add(Dot([gox + gux * min(tau, 2.7), goy + guy * yv, 0], radius=0.06, color=C.growth).set_opacity(kg))
            g.add(MathTex(r"x=e^{t}", font_size=30, color=C.growth).move_to([gox + 0.95, goy + 1.45, 0])
                  .set_opacity(kg))
        return g
    live(hud, hud_draw, pt_in, v_in, (go - 0.6, nl_out[1]))

    # ── "Velocity equals position. It is the heart of e." ──
    vx = glyphs(r"v=x", {0: C.vel, 2: C.growth}, size=170, n=3).move_to([0, -0.35, 0])
    m.play(FadeIn(vx[0], scale=1.3), at=T.v_eq_x, dur=0.5)
    m.play(FadeIn(vx[1]), at=T.v_eq_x + 0.74, dur=0.4)
    m.play(FadeIn(vx[2], scale=1.3), at=T.v_eq_x + 1.14, dur=0.5)
    de = glyphs(r"\tfrac{d}{dt}e^{t}=e^{t}", {4: C.growth, 5: C.growth, 7: C.growth, 8: C.growth}, size=64, n=9)
    de.move_to([0, 2.45, 0])
    m.play(FadeIn(de, shift=0.15 * DOWN), at=T.heart + 0.15, dur=0.7)

    # ── "And we are about to change just one word of it.": a red i drifts in above the equals sign ──
    i_ = tex("i", size=110, color=C.turn).move_to([*I_POS, 0])
    m.play(FadeIn(i_, shift=0.3 * DOWN), at=T.one_word + 0.2, dur=0.8)
    m.play(Indicate(i_, color=C.turn, scale_factor=1.3), at=T.one_word + 1.05, dur=0.7)
    b1 = badge(1)
    m.play(ReplacementTransform(vx, b1), FadeOut(de), at=T.cut_ch2 - 1.05, dur=0.8, ease=E)
