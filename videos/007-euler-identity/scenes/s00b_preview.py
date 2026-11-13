"""Intro · the preview, all on the circle from the hook. Three ingredients land on their words: e (a gold growth
curve with its tangent riding up), i (the plane turns a quarter turn, a red arc carries 1 to i), pi (a green
segment, a distance). On "put them together" the green distance wraps onto the circle, the three symbols drop into
e^{iπ}, and the hero shot plays: the domain-colored plane turns half a turn while the point walks onto −1.
"By the end…": the hero shrinks into the last tile of a 3 × 2 chapter-preview grid while the other five tiles
arrive, each playing its chapter's key picture (compounding → e, the 3D plane's quarter turns, v = ix, the
compounded turn closing on −1, the series spiral), and e^{iπ} = −1 rises to a header. "One dollar in a bank"
lights tile 1, a sweep runs to tile 6, whose plane turns another half turn. In the held pause every tile flies
into its progress-rail tick."""
from aion import *

from beats import T
from shots import (HERO_EQ, HERO_O, HERO_U, P, backdrop, backing, ease, euler, live, plane_grid, rail_ticks,
                   ramp, walker)
from shots3d import plane_uniforms
from tiles import (TILES, frame_rect, inner, label, lerp_box, mid, tick_box, tile1, tile2, tile2_cam, tile2_phi,
                   tile3, tile4, tile5)

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
        k = (1 - 0.65 * ramp(t, T.walking - 0.2, T.walking + 0.6)) * (1 - ramp(t, T.by_end + 0.1, T.by_end + 0.5))
        g = VGroup(VMobject(stroke_color=C.arc, stroke_width=C.stroke + 1.5, stroke_opacity=k)
                   .set_points_smoothly([[*p, 0] for p in pts]))
        kt = ramp(t, *ticks_k) * (1 - ramp(t, wrap[0], wrap[0] + 0.3))
        if kt > 0.01:                                 # end ticks on the straight segment
            for x in (HALF, -HALF):
                g.add(Line([x, SEG_Y - 0.14, 0], [x, SEG_Y + 0.14, 0], color=C.arc, stroke_width=C.thin + 0.6,
                           stroke_opacity=kt))
        return g
    live(m, distance, (seg_in[0], seg_in[1]), wrap, (T.walking - 0.2, T.walking + 0.6), (T.by_end + 0.1, T.by_end + 0.55))
    sym_pi = MathTex(r"\pi", font_size=110, color=C.arc).move_to([HALF + 0.85, SEG_Y + 0.05, 0])
    m.play(FadeIn(sym_pi, scale=1.4), at=T.distance, dur=0.5)

    # ── "Put them together": the symbols drop into e^{iπ} ──
    eq = euler(size=120).move_to([*HERO_EQ, 0])
    back = backing(eq, pad=0.3)
    m.play(FadeIn(back), at=T.together + 0.3, dur=0.6)
    m.play(ReplacementTransform(sym_e, eq[0], path_arc=0.6), ReplacementTransform(sym_i, eq[1], path_arc=-0.6),
           ReplacementTransform(sym_pi, eq[2], path_arc=0.5), at=T.together + 0.9, dur=1.3, ease=E)

    # ── the hero: the point walks a distance pi while the whole colored plane turns half a turn ──
    # From "By the end" the hero shrinks into tile 6 of the chapter grid, so its origin, unit and clip box are tracks.
    walk = (T.walking - 0.1, T.lands + 0.35)
    shrink = (T.by_end + 0.1, T.by_end + 1.7)
    half = (T.half_plane + 0.1, T.half_plane + 2.0)   # "a half turn of the whole plane": tile 6 turns again
    th = keys((t0, 0.0), (walk[0], 0.0), (walk[1], PI, "in_out_sine"), (half[0], PI), (half[1], TAU, E), lead=0)
    box6 = inner(TILES[5])
    c6, u6 = mid(box6), 0.5
    FULL = (-8.0, -5.0, 8.0, 5.0)
    col = [T.half_plane + 2.45 + 0.25 * j for j in range(6)]      # the collapse: tile k starts at col[k-1]
    kout = [(c, c + 0.3) for c in col]
    dim = keys((t0, 1.0), (T.dollar - 0.2, 1.0), (T.dollar + 0.3, 0.45, E), lead=0)

    def lit(t, k):
        """1 for the lit tile, else the dim level: tile 1 on "one dollar", a sweep 1→6 on "and end with", then 6."""
        sweep = (T.dollar + 1.25, T.half_plane - 0.1)
        if t < sweep[0]:
            on = 1 if t >= T.dollar - 0.2 else None
        elif t < sweep[1]:
            on = 1 + min(5, int(6 * (t - sweep[0]) / (sweep[1] - sweep[0])))
        else:
            on = 6
        return 1.0 if on in (None, k) else float(dim(t))

    def hero(t):
        u = ease(t, *shrink)
        return (1 - u) * np.array(O) + u * c6[:2], (1 - u) * U + u * u6, lerp_box(FULL, box6, u)

    def k6(t):
        return (1 - ramp(t, *kout[5])) * lit(t, 6)

    s.shader("plane.frag", z=0, u_theta=th, u_sat=0.62, u_value=0.82,
             u_origin=lambda t: tuple(hero(t)[0]), u_unit=lambda t: hero(t)[1], u_clip=lambda t: hero(t)[2],
             u_opacity=lambda t: 0.62 * ramp(t, T.together + 0.6, T.together + 1.8) * k6(t))
    kg = T.together + 0.4

    def grid_h(t):                                    # the plane's grid turns with it
        o, u, b = hero(t)
        k = 0.5 * ramp(t, kg, kg + 1.0) * k6(t)
        if k < 0.005:
            return VGroup()
        return plane_grid(o, u / 2, box=b, turn=th(t), n=8, minor=1, opacity=k)
    live(bg, grid_h, (kg, T.cut_ch1))

    def stage(t):                                     # axes, circle, the walker: all riding the shrink
        o, u, b = hero(t)
        k = k6(t)
        g = VGroup()
        if k < 0.005:
            return g
        if t >= shrink[0]:
            g.add(Line(P(o, u, -1.7), P(o, u, 1.7), color=C.ghost, stroke_width=C.thin, stroke_opacity=k),
                  Line(P(o, u, -1.25j), P(o, u, 1.25j), color=C.ghost, stroke_width=C.thin, stroke_opacity=k),
                  Circle(radius=u, color=C.text, stroke_width=C.thin + 1).move_to([*o, 0]).set_stroke(opacity=k))
        g.add(walker(o, u, th(t), k=k))
        ha = ease(t, *half)
        if ha > 0.01:                                 # the red half-turn arc of tile 6
            arc = Arc(radius=0.62 * u, start_angle=0.15, angle=(PI - 0.3) * ha, arc_center=[*o, 0], color=C.turn,
                      stroke_width=C.stroke, stroke_opacity=k)
            arc.add_tip(tip_length=0.14, tip_width=0.14)
            arc.tip.set_fill(C.turn, opacity=k).set_stroke(opacity=k)
            g.add(arc)
        return g
    m.remove(dot, at=walk[0])
    m.remove(ax, circ, at=shrink[0])
    live(m, stage, (walk[0], T.cut_ch1))
    m.play(LaggedStart(*[FadeIn(g, shift=0.1 * LEFT) for g in eq[3:]], lag_ratio=0.3),
           at=T.lands + 1.25, dur=0.7)                                                       # "negative one"

    # ── "By the end of this video… You will see it.": e^{iπ} = −1 rises to a header over the chapter grid ──
    m.play(FadeOut(VGroup(eq, back)), at=shrink[0], dur=0.08, lead=0)
    head = (shrink[0], shrink[0] + 1.3)
    pulse = (T.see_it + 0.05, T.see_it + 1.0)

    def header(t):
        u = ease(t, *head)
        k = 1 - ramp(t, col[5] + 0.6, col[5] + 1.3)
        if k < 0.005:
            return VGroup()
        e_ = euler(size=120)
        bump = 1 + 0.08 * np.sin(PI * np.clip((t - pulse[0]) / (pulse[1] - pulse[0]), 0, 1))
        e_.scale((1 - u + 0.62 * u) * bump).move_to([0.0, (1 - u) * HERO_EQ[1] + u * 3.2, 0])
        g = VGroup(e_.set_opacity(k))
        kb = 1 - ramp(t, head[0], head[0] + 0.5)
        if kb > 0.01:
            g.add_to_back(backing(e_, pad=0.3).set_opacity(kb))
        return g
    live(m, header, head, pulse, (col[5] + 0.6, col[5] + 1.3))

    # ── the chapter grid: five tiles arrive around the shrunk hero; each plays its chapter's key picture ──
    arrive = [T.by_end + 0.5 + 0.25 * j for j in range(5)] + [shrink[1] - 0.4]
    cam2 = tile2_cam(TILES[1], arrive[1])
    s.shader("plane3d.frag", z=0, **cam2.uniforms(),
             **plane_uniforms((0.0, 0.0), 1.0, 1.0, clip=inner(TILES[1]), sat=0.55, value=0.75,
                              lines=lambda t: 1.0 * ramp(t, arrive[1], arrive[1] + 0.6) * (1 - ramp(t, *kout[1]))
                              * lit(t, 2),
                              colors=lambda t: 0.58 * ramp(t, arrive[1] + 0.2, arrive[1] + 1.0)
                              * (1 - ramp(t, *kout[1])) * lit(t, 2),
                              theta=lambda t: tile2_phi(t, arrive[1])))
    labels = [label(k, b) for k, b in enumerate(TILES, start=1)]
    pics = {1: lambda t, k: tile1(t, TILES[0], arrive[0], k, coin_at=T.dollar),
            2: lambda t, k: tile2(t, cam2, arrive[1], k),
            3: lambda t, k: tile3(t, TILES[2], arrive[2], k),
            4: lambda t, k: tile4(t, TILES[3], arrive[3], k),
            5: lambda t, k: tile5(t, TILES[4], arrive[4], k)}

    def grid(t):
        g = VGroup()
        for k in range(1, 7):
            a = arrive[k - 1]
            kin = ramp(t, a, a + 0.6)
            if kin < 0.005:
                continue
            lk = lit(t, k)
            u = ease(t, col[k - 1] + 0.2, col[k - 1] + 0.95)          # the frame flies into rail tick k
            b = lerp_box(TILES[k - 1], tick_box(k), u)
            land = ramp(t, col[k - 1] + 0.85, col[k - 1] + 0.95)
            if land < 1:
                bright = lk >= 1 and T.dollar - 0.2 <= t < col[0]
                fc = interpolate_color(ManimColor(C.text if bright else C.frame), ManimColor(C.faint), u)
                pop = 1 + 0.04 * ramp(t, T.dollar - 0.2, T.dollar + 0.2) * bright
                fr = frame_rect(b, fc, k=kin * (1 - land) * (0.5 + 0.5 * lk), width=C.thin * (1 + 0.5 * bright))
                g.add(fr.scale(pop) if u == 0 else fr)
            kc = kin * (1 - ramp(t, *kout[k - 1]))
            if kc > 0.005:
                g.add(labels[k - 1].copy().set_opacity(kc * lk))
                if k in pics:
                    g.add(pics[k](t, kc * lk))
        return g
    live(m, grid, (arrive[0], col[5] + 1.0))

    # ── the held pause: each tile lands as its progress-rail tick ──
    rl = rail_ticks(0)
    for k in range(1, 7):
        m.add(rl[k - 1], at=col[k - 1] + 0.9)
