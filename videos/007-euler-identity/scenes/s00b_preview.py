"""Intro · the preview, all on the circle from the hook. Three ingredients land on their words: e (a gold growth
curve with its tangent riding up), i (the plane turns a quarter turn, a red arc carries 1 to i), pi (a green
segment, a distance). On "put them together" the green distance wraps onto the circle, the three symbols drop into
e^{iπ}, and the hero shot plays: the domain-colored plane turns half a turn while the point walks onto −1.
Then the map: $1 → a half turn of the whole plane, and the progress rail draws in during the held pause."""
from aion import *

from beats import T
from shots import (HERO_EQ, HERO_O, HERO_U, P, arrow, backdrop, backing, ease, euler, glyphs, live, panel,
                   plane_grid, rail_ticks, ramp, walker)

O, U = HERO_O, HERO_U
E = "easy_ease"
SEG_Y = -2.15                                         # the straight green distance, under the circle
HALF = np.pi * U / 2                                  # half its length (a distance pi, in world units)


@scene(T.cut_preview, T.cut_ch1)
def s00b_preview(s):
    backdrop(s)
    t0 = s.start
    bg = s.manim(z=1)                                 # curve, grid
    m = s.manim(z=3)                                  # circle, arcs, symbols, equation

    # the stage from the hook: faint axes, the unit circle, the point at 1
    ax = VGroup(Line(P(O, U, -1.7), P(O, U, 1.7), color=C.ghost, stroke_width=C.thin),
                Line(P(O, U, -1.25j), P(O, U, 1.25j), color=C.ghost, stroke_width=C.thin))
    circ = Circle(radius=U, color=C.text, stroke_width=C.thin + 1).move_to([*O, 0])
    dot = Dot(P(O, U, 1), radius=0.09, color=C.point)
    m.add(ax, circ, dot, at=t0)

    # ── "e is a story about growth": e^x rising, a tangent riding it ──
    t_e = T.growth - 0.6                              # the word "e"
    gx = (-7.6, -2.55)                                # world x range: kept left of the circle
    yb = -1.45                                        # its baseline (y = 0 of the curve)

    def gy(x):
        return yb + 5.0 * np.exp(1.1 * (x - gx[1]))
    curve = FunctionGraph(gy, x_range=gx, color=C.growth, stroke_width=C.stroke)
    bg.play(Create(curve), at=t_e + 0.3, dur=1.2, ease=E)
    ride = (t_e + 0.6, T.turning - 0.9)

    def tangent(t):
        k = ramp(t, ride[0], ride[0] + 0.3) * (1 - ramp(t, ride[1] - 0.3, ride[1] + 0.2))
        x = -6.1 + 2.9 * ease(t, *ride)
        y, dy = gy(x), 1.1 * (gy(x) - yb)
        d = np.array([1.0, dy]) / np.hypot(1.0, dy)
        return VGroup(Line([x - 0.9 * d[0], y - 0.9 * d[1], 0], [x + 0.9 * d[0], y + 0.9 * d[1], 0],
                           color=C.text, stroke_width=C.thin + 0.6, stroke_opacity=k),
                      Dot([x, y, 0], radius=0.07, color=C.growth).set_opacity(k))
    live(bg, tangent, (ride[0], ride[1] + 0.3))
    sym_e = MathTex("e", font_size=110, color=C.growth).move_to([-5.7, 2.55, 0])
    m.play(FadeIn(sym_e, scale=1.4), at=t_e, dur=0.5)
    bg.play(FadeOut(curve), at=T.turning - 0.6, dur=0.6)

    # ── "i is a story about turning": the plane turns a quarter turn, 1 → i ──
    t_i = T.turning - 0.65                            # the word "i"
    q = (t_i + 0.15, T.distance - 0.6)                # the quarter turn
    turn_q = keys((t0, 0.0), (q[0], 0.0), (q[1], PI / 2, E), lead=0)
    kq = (t_i - 0.2, T.distance + 0.2)

    def grid_q(t):
        k = 0.4 * ramp(t, kq[0], kq[0] + 0.5) * (1 - ramp(t, kq[1] - 0.5, kq[1]))
        return plane_grid(O, U / 2, turn=turn_q(t), n=8, minor=1, opacity=k)
    live(bg, grid_q, kq)
    qarc = Arc(radius=U, start_angle=0, angle=PI / 2, arc_center=[*O, 0], color=C.turn, stroke_width=C.stroke + 1)
    qarc.add_tip(tip_length=0.22, tip_width=0.22)
    m.play(Create(qarc), at=q[0] + 0.4, dur=q[1] - q[0] - 0.2, ease=E, lead=0)
    sym_i = MathTex("i", font_size=110, color=C.turn).move_to(P(O, U, -0.3 + 1.24j))
    m.play(FadeIn(sym_i, scale=1.4), at=t_i, dur=0.5)
    m.play(FadeOut(qarc), at=T.distance + 0.1, dur=0.6)

    # ── "And pi is a distance": a straight green length pi (in circle units) ──
    seg_in = (T.distance - 0.1, T.distance + 0.9)
    wrap = (T.together + 0.1, T.together + 1.4)       # it wraps onto the circle: exactly half way round
    ticks_k = (seg_in[0], wrap[0] + 0.2)

    def distance(t):
        a = ease(t, *seg_in)                          # drawn from the right end leftward
        w = ease(t, *wrap)
        s_ = np.linspace(0.0, a, 80)
        straight = np.column_stack([HALF - 2 * HALF * s_, np.full_like(s_, SEG_Y)])
        bent = np.column_stack([O[0] + U * np.cos(PI * s_), O[1] + U * np.sin(PI * s_)])
        pts = (1 - w) * straight + w * bent
        k = (1 - 0.65 * ramp(t, T.walking - 0.2, T.walking + 0.6)) * (1 - ramp(t, T.dollar - 0.75, T.dollar - 0.05))
        g = VGroup(VMobject(stroke_color=C.arc, stroke_width=C.stroke + 1.5, stroke_opacity=k)
                   .set_points_smoothly([[*p, 0] for p in pts]))
        kt = ramp(t, *ticks_k) * (1 - ramp(t, wrap[0], wrap[0] + 0.3))
        if kt > 0.01:                                 # end ticks on the straight segment
            for x in (HALF, -HALF):
                g.add(Line([x, SEG_Y - 0.14, 0], [x, SEG_Y + 0.14, 0], color=C.arc, stroke_width=C.thin + 0.6,
                           stroke_opacity=kt))
        return g
    live(m, distance, (seg_in[0], seg_in[1]), wrap, (T.walking - 0.2, T.walking + 0.6), (T.dollar - 0.75, T.dollar))
    sym_pi = MathTex(r"\pi", font_size=110, color=C.arc).move_to([HALF + 0.85, SEG_Y + 0.05, 0])
    m.play(FadeIn(sym_pi, scale=1.4), at=T.distance, dur=0.5)

    # ── "Put them together": the symbols drop into e^{iπ} ──
    eq = euler(size=120).move_to([*HERO_EQ, 0])
    back = backing(eq, pad=0.3)
    m.play(FadeIn(back), at=T.together + 0.3, dur=0.6)
    m.play(ReplacementTransform(sym_e, eq[0], path_arc=0.6), ReplacementTransform(sym_i, eq[1], path_arc=-0.6),
           ReplacementTransform(sym_pi, eq[2], path_arc=0.5), at=T.together + 0.9, dur=1.3, ease=E)

    # ── the hero: the point walks a distance pi while the whole colored plane turns half a turn ──
    walk = (T.walking - 0.1, T.lands + 0.35)
    th = keys((t0, 0.0), (walk[0], 0.0), (walk[1], PI, "in_out_sine"), lead=0)
    s.shader("plane.frag", z=0, u_origin=O, u_unit=U, u_theta=th, u_sat=0.62, u_value=0.82,
             u_opacity=fade(T.together + 0.6, to=0.62, dur=1.2, out=T.see_it + 0.6, out_dur=1.2))
    kg = (T.together + 0.4, T.see_it + 0.6)

    def grid_h(t):                                    # the plane's grid turns with it
        k = 0.5 * ramp(t, kg[0], kg[0] + 1.0) * (1 - ramp(t, kg[1] - 1.0, kg[1]))
        return plane_grid(O, U / 2, turn=th(t), n=8, minor=1, opacity=k)
    live(bg, grid_h, kg)
    m.remove(dot, at=walk[0])
    gone = (T.dollar - 0.75, T.dollar - 0.05)
    live(m, lambda t: walker(O, U, th(t), k=1 - ramp(t, *gone)), (walk[0], walk[1] + 0.05), (gone[0], gone[1] + 0.05))
    m.play(LaggedStart(*[FadeIn(g, shift=0.1 * LEFT) for g in eq[3:]], lag_ratio=0.3),
           at=T.lands + 1.25, dur=0.7)                                                       # "negative one"

    # ── "By the end of this video…": a slow push. "You will see it." ──
    s.camera.push(T.by_end, zoom=1.07, dur=3.2)
    m.play(Indicate(eq, color=None, scale_factor=1.08), at=T.see_it + 0.1, dur=0.9)

    # ── "We will start with one dollar in a bank, and end with a half turn of the whole plane." ──
    out1 = T.dollar - 0.75
    s.camera.push(out1, zoom=1.0, dur=1.0)
    stage = VGroup(ax, circ, back, eq)
    m.play(FadeOut(stage), at=out1, dur=0.7)
    dollar = MathTex(r"\$1", font_size=130, color=C.growth).move_to([-3.6, 0.35, 0])
    m.play(FadeIn(dollar, scale=1.3), at=T.dollar + 0.1, dur=0.6)
    go = arrow([-2.35, 0.35, 0], [1.55, 0.35, 0], C.muted, width=C.thin + 1, tip=0.2)
    m.play(GrowArrow(go), at=T.dollar + 1.0, dur=1.4, ease=E)

    pc, pu = (3.65, 0.35), 0.5                         # a small framed plane on the right
    box = (pc[0] - 1.45, pc[1] - 1.45, pc[0] + 1.45, pc[1] + 1.45)
    frame_ = panel(pc[0], pc[1], 2.9, 2.9)
    m.play(FadeIn(frame_), at=T.half_plane - 0.9, dur=0.5)
    ht = (T.half_plane + 0.1, T.half_plane + 1.9)
    turn_h = keys((t0, 0.0), (ht[0], 0.0), (ht[1], PI, E), lead=0)
    kp = (T.half_plane - 0.8, T.cut_ch1 - 1.6)

    def small(t):
        k = ramp(t, kp[0], kp[0] + 0.5) * (1 - ramp(t, kp[1] - 0.6, kp[1]))
        g = plane_grid(pc, pu, box=box, turn=turn_h(t), n=4, minor=2, opacity=k)
        tip = np.array([pc[0] + 2 * pu * np.cos(turn_h(t)), pc[1] + 2 * pu * np.sin(turn_h(t)), 0])
        g.add(arrow([*pc, 0], tip, C.point, width=C.stroke).set_opacity(k))
        return g
    live(m, small, (kp[0], kp[0] + 0.5), ht, (kp[1] - 0.6, kp[1]))
    harc = Arc(radius=1.12, start_angle=0.15, angle=PI - 0.3, arc_center=[*pc, 0], color=C.turn,
               stroke_width=C.stroke)
    harc.add_tip(tip_length=0.2, tip_width=0.2)
    m.play(Create(harc), at=ht[0] + 0.2, dur=ht[1] - ht[0] - 0.1, ease=E, lead=0)

    # ── the held pause: the progress rail draws in, the map clears ──
    rl = rail_ticks(0)
    m.play(LaggedStart(*[Create(x) for x in rl], lag_ratio=0.25), at=T.half_plane + 3.0, dur=1.6, lead=0)
    m.play(FadeOut(VGroup(dollar, go, frame_, harc)), at=kp[1] - 0.6, dur=0.6, lead=0)
