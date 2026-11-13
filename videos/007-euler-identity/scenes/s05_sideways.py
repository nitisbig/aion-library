"""Ch3 · Growth turned sideways. Two panels: the Ch1 line where v = x, and a plane where the rule picks up one i,
v = ix. The plane takes the frame. i turns the position arrow a quarter turn: the pink velocity, which slides to
the point. Start at 1: position right, velocity up. The point moves, the right angle stays locked, the push is
always sideways, so the distance stays 1 and the trail closes the unit circle at speed 1. Then the whole plane
follows dz/dt = a·z: a dial turns a from 1 (points fly outward) through e^{iπ/4} (spirals) to i (circles), and a
long exposure of the circling streams fades in."""
from aion import *

from beats import T
from shots import (O3, U3, arrow, backdrop, backing, badges, ease, exposure_layer, flow_alpha, flow_layer, glyphs,
                   live, panel, plane_grid, rail, ramp, right_angle, tex)

E = "easy_ease"
LP, RP = (-3.6, -0.3), (3.6, -0.3)                    # the two panels' centres
PW, PH = 6.6, 4.9
RO, RU = (3.6, -0.6), 1.0                             # the right panel's plane: origin, unit
GO = T.moves_up + 0.1                                 # the point starts to walk
OMEGA = TAU / 19.8                                    # one lap lands on "It traces a circle"


def P3(o, u, z):
    return np.array([o[0] + u * z.real, o[1] + u * z.imag, 0.0])


@scene(T.cut_ch3, T.cut_walk)
def s05_sideways(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=2)                                 # grids
    m = s.manim(z=3)                                  # arrows, the point
    hb = s.manim(z=4, parallax=0.0)                   # HUD backings, under the HUD text
    hud = s.manim(z=5, parallax=0.0)
    rail(hud, 3)
    badges(hud, 2)

    # ── "Now we can read e to the i t." ──
    eit = glyphs(r"e^{it}", {0: C.growth, 1: C.turn, 2: C.arc}, size=96, n=3).move_to([0, 2.95, 0])
    eback = backing(eit, pad=0.22)
    hud.play(FadeIn(eback), FadeIn(eit, scale=1.2), at=T.read_eit + 0.5, dur=0.8)

    # ── "Remember the rule for e to the t. Velocity equals position." the left panel replays Ch1 ──
    lp = panel(*LP, PW, PH)
    m.play(FadeIn(lp), at=T.rule_et - 0.2, dur=0.6)
    vx = glyphs(r"v=x", {0: C.vel, 2: C.growth}, size=64, n=3).move_to([LP[0], LP[1] + 1.7, 0])
    m.play(FadeIn(vx, shift=0.1 * DOWN), at=T.v_x, dur=0.6)
    nly, nlo = LP[1] - 0.6, LP[0] - 2.8
    left_out = (T.know_i - 0.6, T.know_i)
    g_run = T.v_x + 0.4

    def left(t):
        k = ramp(t, T.rule_et - 0.2, T.rule_et + 0.4) * (1 - ramp(t, *left_out))
        if k < 0.005:
            return VGroup()
        g = VGroup(Line([LP[0] - PW / 2 + 0.2, nly, 0], [LP[0] + PW / 2 - 0.2, nly, 0], color=C.axis,
                        stroke_width=C.thin * 1.2, stroke_opacity=k))
        for n in range(6):
            g.add(Line([nlo + n, nly - 0.07, 0], [nlo + n, nly + 0.07, 0], color=C.axis, stroke_width=C.thin,
                       stroke_opacity=k))
            g.add(MathTex(str(n), font_size=26, color=C.muted).move_to([nlo + n, nly - 0.32, 0]).set_opacity(k))
        x = 1.0 if t < g_run else min(5.6, float(np.exp(0.5 * (t - g_run))))
        for j in range(1, 10):
            tg = g_run + 0.5 * j
            if tg >= t:
                break
            g.add(Dot([nlo + min(5.6, np.exp(0.5 * (tg - g_run))), nly, 0], radius=0.05, color=C.growth)
                  .set_opacity(0.35 * k))
        p = np.array([nlo + x, nly, 0])
        kv = ramp(t, T.v_x - 0.1, T.v_x + 0.4) * k
        if kv > 0.01 and x < 5.5:
            g.add(arrow(p, p + [min(x, 2.5), 0, 0], C.vel, width=C.stroke, tip=0.18).set_opacity(kv))
        g.add(Dot(p, radius=0.09, color=C.growth).set_opacity(k))
        return g
    live(m, left, (T.rule_et - 0.2, T.rule_et + 0.4), (g_run, g_run + 3.6), (T.v_x - 0.1, T.v_x + 0.4), left_out)
    m.play(FadeOut(VGroup(lp, vx)), at=left_out[0] + 0.1, dur=0.5)

    # ── "For e to the i t, the rule picks up a single i. Velocity equals i times position." ──
    rp = panel(*RP, PW, PH)
    m.play(FadeIn(rp), at=T.picks - 0.4, dur=0.6)
    vix = glyphs(r"v=ix", {0: C.vel, 2: C.turn, 3: C.point}, size=64, n=4).move_to([RP[0], RP[1] + 1.7, 0])
    vix_tl = vix.copy().scale(0.9).move_to([-5.2, 2.95, 0])
    hud.play(FadeIn(VGroup(vix[0], vix[1], vix[3]), shift=0.1 * DOWN), at=T.picks - 0.1, dur=0.6)
    hud.play(FadeIn(vix[2], shift=0.5 * DOWN, scale=1.6), at=T.v_ix + 0.55, dur=0.6)
    hud.play(Indicate(vix[2], color=C.turn, scale_factor=1.35), at=T.v_ix + 1.3, dur=0.7)

    # the panel's plane grows into the frame: origin and unit glide from the panel to the full plane
    merge = (T.know_i - 0.3, T.know_i + 1.2)
    m.play(FadeOut(rp), at=merge[0] + 0.3, dur=0.6)
    vback = backing(vix_tl, pad=0.2)
    hb.play(FadeIn(vback), at=merge[0] + 0.6, dur=0.5)
    hud.play(Transform(vix, vix_tl), at=merge[0], dur=merge[1] - merge[0], ease=E)

    def frame_at(t):
        u = ease(t, *merge)
        o = ((1 - u) * RO[0] + u * O3[0], (1 - u) * RO[1] + u * O3[1])
        un = (1 - u) * RU + u * U3
        box = ((1 - u) * (RP[0] - PW / 2 + 0.05) + u * -9.6, (1 - u) * (RP[1] - PH / 2 + 0.05) + u * -5.6,
               (1 - u) * (RP[0] + PW / 2 - 0.05) + u * 9.6, (1 - u) * (RP[1] + PH / 2 - 0.05) + u * 5.6)
        return o, un, box

    grid_out = (T.whole_plane + 0.4, T.whole_plane + 1.6)

    def grid(t):
        k = ramp(t, T.picks - 0.3, T.picks + 0.4) * (1 - 0.6 * ramp(t, *grid_out))
        o, un, box = frame_at(t)
        return plane_grid(o, un / 2, box=box, n=16, minor=1, opacity=0.45 * k)
    live(bg, grid, (T.picks - 0.3, T.picks + 0.4), merge, grid_out)

    # the walk: θ(t), the point e^{iθ}
    th = lambda t: max(0.0, OMEGA * (t - GO))                          # noqa: E731
    pt_in = (T.picks + 0.2, T.picks + 0.7)
    walk_out = (T.whole_plane - 0.1, T.whole_plane + 0.7)

    # ── "And we know what i does. It turns an arrow by a quarter turn." on the position arrow itself ──
    # ── "So the velocity is always the position, turned ninety degrees." it slides to the point ──
    xin = (T.turns_arrow - 0.6, T.turns_arrow - 0.1)
    rot = (T.turns_arrow + 0.3, T.turns_arrow + 1.5)
    slide = (T.always_pos + 0.2, T.always_pos + 1.4)
    mark_in = (T.turned90 - 0.1, T.turned90 + 0.4)

    def walker3(t):
        g = VGroup()
        ko = 1 - ramp(t, *walk_out)
        o, un, _ = frame_at(t)
        a = th(t)
        z = np.exp(1j * a)
        p = P3(o, un, z)
        # the walked arc: lap one, then lap two over it
        if a > 0.02:
            g.add(Arc(radius=un, start_angle=0, angle=min(a, TAU), arc_center=[*o, 0], color=C.arc,
                      stroke_width=C.stroke + 1.5, stroke_opacity=ko * (1 - 0.55 * ramp(a, TAU, TAU + 0.6))))
        if a > TAU + 0.02:
            g.add(Arc(radius=un, start_angle=0, angle=a - TAU, arc_center=[*o, 0], color=C.arc,
                      stroke_width=C.stroke + 1.5, stroke_opacity=ko))
        kx = ramp(t, *xin) * ko
        if kx > 0.005:
            g.add(arrow([*o, 0], p, C.point, width=C.stroke).set_opacity(kx))
            kl = kx * (1 - ramp(t, T.moves_up - 0.5, T.moves_up))
            if kl > 0.01:
                g.add(MathTex("x", font_size=40, color=C.point).move_to(P3(o, un, 0.5 * z) + [0, -0.3, 0])
                      .set_opacity(kl))
            # the velocity: a copy turned by i, then slid to the point
            r_ = ease(t, *rot)
            sl = ease(t, *slide)
            if r_ > 0.0:
                col = interpolate_color(ManimColor(C.point), ManimColor(C.vel), r_)
                d = z * np.exp(1j * PI / 2 * r_)
                tail = (1 - sl) * np.array([*o, 0]) + sl * p
                g.add(arrow(tail, tail + un * np.array([d.real, d.imag, 0]), col, width=C.stroke).set_opacity(kx))
                if r_ < 0.999 or sl < 0.001:
                    g.add(Arc(radius=0.45, start_angle=a, angle=PI / 2 * r_, arc_center=[*o, 0], color=C.turn,
                              stroke_width=C.thin + 1, stroke_opacity=kx * (1 - sl)))
                kl2 = ramp(t, rot[1] - 0.3, rot[1]) * (1 - ramp(t, T.moves_up - 0.5, T.moves_up)) * kx
                if kl2 > 0.01:
                    lp_ = tail + un * 0.55 * np.array([d.real, d.imag, 0]) + 0.38 * np.array([d.imag, -d.real, 0])
                    g.add(glyphs(r"ix", {0: C.turn, 1: C.point}, size=40, n=2).move_to(lp_).set_opacity(kl2))
            km = ramp(t, *mark_in) * ko
            if km > 0.01 and sl > 0.99:
                g.add(right_angle(p, -np.array([z.real, z.imag]), np.array([-z.imag, z.real]), k=km))
        # the sideways push: a dashed tangent through the point
        kt = ramp(t, T.never_closer - 0.3, T.never_closer + 0.3) * (1 - ramp(t, T.stays - 0.4, T.stays + 0.2)) * ko
        if kt > 0.01:
            tg = np.array([-z.imag, z.real, 0])
            g.add(DashedLine(p - 2.4 * tg, p + 2.4 * tg, color=C.vel, stroke_width=C.thin, dash_length=0.12)
                  .set_opacity(0.6 * kt))
        # "stays exactly one unit from the center"
        k1 = ramp(t, T.stays, T.stays + 0.5) * (1 - ramp(t, T.how_fast, T.how_fast + 0.5)) * ko
        if k1 > 0.01:
            g.add(MathTex("1", font_size=40, color=C.text).move_to(P3(o, un, 0.5 * z) + 0.3 * np.array(
                [z.imag, -z.real, 0])).set_opacity(k1))
        kp = ramp(t, *pt_in) * ko
        if kp > 0.005:
            g.add(Dot(p, radius=0.1, color=C.point).set_opacity(kp))
        return g
    live(m, walker3, pt_in, merge, (xin[0], mark_in[1]), (T.moves_up - 0.5, walk_out[1]))
    ring = Circle(radius=0.2, color=C.point, stroke_width=C.thin + 1).move_to(P3(O3, U3, 1))   # "Start at one"
    m.play(FadeIn(ring, scale=0.5), at=T.start1 + 0.1, dur=0.3)
    m.play(FadeOut(ring, scale=2.5), at=T.start1 + 0.5, dur=0.8)

    # ── "So the point walks around the circle at one unit of distance, per unit of time." ──
    kr = (T.same_len - 0.6, T.same_len)
    gone_r = (T.whole_plane - 0.1, T.whole_plane + 0.5)

    def readouts(t):
        k = ramp(t, *kr) * (1 - ramp(t, *gone_r))
        if k < 0.005:
            return VGroup()
        eq = glyphs(r"|v|=|x|=1", {1: C.vel, 5: C.point}, size=40, n=9)
        kt = ramp(t, T.unit_time - 1.6, T.unit_time - 1.0) * k
        rows = VGroup(eq)
        if kt > 0.005:
            rows.add(VGroup(tex("t", "=", size=40, colors={0: C.arc}),
                            DecimalNumber(th(t), num_decimal_places=2, font_size=40, color=C.arc))
                     .arrange(RIGHT, buff=0.15).set_opacity(kt))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([-6.6, 1.75, 0], aligned_edge=UL)
        eq.set_opacity(k)
        return VGroup(backing(rows, pad=0.18).set_opacity(k).set_stroke(opacity=k * 0.8), rows)
    live(hud, readouts, kr, (T.unit_time - 1.6, gone_r[1]))

    # ── "Let the whole plane follow the same rule." the flow field, and a dial for a ──
    s.camera.push(T.whole_plane + 0.2, zoom=0.82, dur=2.2)
    alpha = flow_alpha()
    s.add(flow_layer(alpha, fade(T.whole_plane + 1.2, to=1.0, dur=1.0)))
    s.add(exposure_layer(fade(T.circles + 0.9, to=0.4, dur=1.6)))
    dial_c = np.array([5.55, 2.35, 0])
    kd = (T.whole_plane + 0.3, T.whole_plane + 0.9)

    def dial(t):
        k = ramp(t, *kd)
        if k < 0.005:
            return VGroup()
        a = alpha(t)
        col = interpolate_color(ManimColor(C.growth), ManimColor(C.turn), min(1.0, a / (PI / 4)) if a < PI / 4
                                else 1.0)
        g = VGroup(backing(Square(2.0), pad=0.0).move_to(dial_c).set_opacity(k).set_stroke(opacity=0.8 * k))
        g.add(Arc(radius=0.7, start_angle=-0.25, angle=PI / 2 + 0.5, arc_center=dial_c, color=C.ghost,
                  stroke_width=C.thin).set_stroke(opacity=k))
        g.add(MathTex("1", font_size=30, color=C.muted).move_to(dial_c + [0.98, 0, 0]).set_opacity(k))
        g.add(MathTex("i", font_size=30, color=C.turn).move_to(dial_c + [0, 0.98, 0]).set_opacity(k))
        g.add(Dot(dial_c + [0.7, 0, 0], radius=0.03, color=C.muted).set_opacity(k))
        g.add(Dot(dial_c + [0, 0.7, 0], radius=0.03, color=C.muted).set_opacity(k))
        tip = dial_c + 0.7 * np.array([np.cos(a), np.sin(a), 0])
        g.add(arrow(dial_c, tip, col, width=C.stroke, tip=0.16).set_opacity(k))
        g.add(MathTex("a", font_size=34, color=col).move_to(dial_c + [-0.55, -0.6, 0]).set_opacity(k))
        g.add(Dot(dial_c, radius=0.035, color=C.text).set_opacity(k))
        return g.shift([-0.25, -0.25, 0])
    live(hud, dial, kd, (T.spiral - 0.9, T.spiral + 0.3), (T.all_way - 0.2, T.all_way + 0.9))
