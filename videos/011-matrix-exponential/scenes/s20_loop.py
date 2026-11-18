"""s20 loop (ch5): watch the commutator. Run A forward for a moment, then B, then A backward, then B backward. If they
commuted the plane would come back where it started; it comes back squashed in x and stretched in y, by about
s²[B, A] (the exact loop is drawn). Two shears in a loop make a stretch neither contains: the reason you can parallel
park. The old rule survives exactly when the matrices commute: the spiral −I/4 + J splits into a shrink times a
rotation, e^{t(−I/4 + J)} = e^{−t/4} e^{tJ}."""
from aion import *
from scipy.linalg import expm

from beats import T
from shots import E, J, arrow, backdrop, backed, disc_points, field_arrows, finish, lab, live, p3, poly, tex
from verify import B, N

A = N
SL = 0.4                                              # each leg runs for time s
LEGS = [A, B, -A, -B]
LOOP = expm(-SL * B) @ expm(-SL * A) @ expm(SL * B) @ expm(SL * A)
CA = A @ B - B @ A
assert np.abs(LOOP - (np.eye(2) - SL ** 2 * CA)).max() < 2 * SL ** 3
O, U = np.array([-1.3, -0.35]), 1.15
HALF = 2.0                                            # the square's half-width (plane units)
SQ = np.array([[-HALF, -HALF], [HALF, -HALF], [HALF, HALF], [-HALF, HALF]])


def W(v):
    return O + U * np.asarray(v, float)


# ── the parallel-park car: kinematic bicycle, two reversing arcs then a short pull forward ──
CAR_L = 0.9


def car_path():
    """Rows (x, y, heading, steer): reverse steering one way, reverse steering back, then pull forward."""
    st, rows = np.zeros(3), [[0.0, 0.0, 0.0, 0.0]]
    for v, phi, dur in ((-1.0, -0.55, 1.1), (-1.0, 0.55, 1.1), (1.0, 0.0, 0.55)):
        for _ in range(110):
            dt = dur / 110
            st = st + dt * np.array([v * np.cos(st[2]), v * np.sin(st[2]), v * np.tan(phi) / CAR_L])
            rows.append([*st, phi])
    return np.array(rows)


CAR = car_path()                                      # rows: x, y, heading, steer
CAR0 = np.array([1.4, 1.3])                           # where the car starts (world)
CS = 1.9                                              # car drawing scale


def car(x, y, th, phi, op=1.0, col=None):
    col = col or C.text
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    c = CAR0 + CS * np.array([x, y])

    def w(p):
        return p3(c + CS * (R @ np.asarray(p, float)))
    body = Polygon(*[w(p) for p in ((-0.25, -0.4), (1.15, -0.4), (1.25, -0.3), (1.25, 0.3), (1.15, 0.4),
                                    (-0.25, 0.4))], stroke_color=col, stroke_width=C.stroke, stroke_opacity=op,
                   fill_opacity=0)
    wheels = VGroup()
    for (px, py, steer) in ((0.0, -0.45, 0.0), (0.0, 0.45, 0.0), (CAR_L, -0.45, phi), (CAR_L, 0.45, phi)):
        Rw = np.array([[np.cos(steer), -np.sin(steer)], [np.sin(steer), np.cos(steer)]])
        a, b = np.array([px, py]) + Rw @ [-0.16, 0], np.array([px, py]) + Rw @ [0.16, 0]
        wheels.add(Line(w(a), w(b), color=col, stroke_width=C.stroke + 3, stroke_opacity=op))
    wind = Line(w((0.85, -0.3)), w((0.85, 0.3)), color=col, stroke_width=C.thin + 0.4, stroke_opacity=op)
    return VGroup(body, wheels, wind)


@scene(T.cut_loop, T.cut_ch6)
def s20_loop(s):
    backdrop(s)
    mg = s.manim(z=0)
    mf = s.manim(z=1)
    m = s.manim(z=4)

    box = (-7.3, -4.2, 7.3, 4.2)
    grid = grid_lines(np.eye(2), tuple(O), U, box, n=14, opacity=0.6)
    mg.play(FadeIn(grid), at=T.cut_loop + 0.1, dur=0.6)

    # ── four legs: A, B, −A, −B ──
    l0 = T.fwd_A + 0.2
    legs = [(l0, l0 + 1.2), (T.then_B + 0.1, T.then_B + 1.3), (T.then_B + 1.4, T.then_B + 2.6),
            (T.then_B + 2.7, T.then_B + 3.9)]

    def M_at(t):
        M = np.eye(2)
        for (a, b), G in zip(legs, LEGS):
            if t <= a:
                break
            u = smooth(float(np.clip((t - a) / (b - a), 0, 1)))
            M = expm(u * SL * G) @ M
        return M

    run_end = legs[-1][1]
    sq_op = keys((T.watch, 0.0), (T.watch + 0.5, 1.0), (T.park - 0.6, 1.0), (T.park - 0.1, 0.0), lead=0)

    def square(t):
        op = float(sq_op(t))
        P = [W(LOOP @ q) if t > run_end else W(M_at(t) @ q) for q in SQ]
        return poly(P, C.vec, C.stroke + 1, opacity=op, close=True)
    live(m, square, (T.watch, T.watch + 0.55), (l0, run_end + 0.05), (T.park - 0.6, T.park - 0.05))

    # particles ride the piecewise flow
    X0 = disc_points(1500, 3.6, seed=19)
    p_op = keys((T.watch + 0.2, 0.0), (T.watch + 0.8, 0.55), (T.squashed - 0.4, 0.55), (T.squashed + 0.4, 0.0),
                lead=0)
    for k in range(5, 0, -1):
        s.add(PointsLayer(lambda t, k=k: O + U * (X0 @ M_at(t - 0.04 * k).T), color=C.flow, size=2.0 * (1 - k / 10),
                          glow=0.0, alpha=p_op * (0.5 * (1 - k / 6)), additive=False, z=2, start=T.watch,
                          end=T.squashed + 0.5))
    s.add(PointsLayer(lambda t: O + U * (X0 @ M_at(t).T), color=C.vec, size=2.0, glow=0.0, alpha=p_op,
                      additive=False, z=2.1, start=T.watch, end=T.squashed + 0.5))

    # the active field and its name, leg by leg
    names = ["A", "B", "-A", "-B"]
    lcols = [C.gen, C.gen_b, C.gen, C.gen_b]
    for (a, b), G, nm, col in zip(legs, LEGS, names, lcols):
        f = field_arrows(G, center=O, unit=U, box=(-7.0, -4.0, 7.0, 4.0), spacing=0.9, opacity=0.5)
        f.set_color(col)
        mf.play(FadeIn(f), at=a - 0.1, dur=0.25)
        mf.play(FadeOut(f), at=b - 0.15, dur=0.25)
        tg = backed(tex(nm, size=52, color=col), buff=0.08).move_to([5.6, 3.1, 0])
        m.play(FadeIn(tg), at=a - 0.1, dur=0.2)
        m.play(FadeOut(tg), at=b - 0.1, dur=0.2)

    # ── you aren't back where you started ──
    ghost = DashedVMobject(Polygon(*[p3(W(q)) for q in SQ], color=C.text, stroke_width=C.thin + 0.6), num_dashes=40)
    m.play(Create(ghost), at=T.back_where + 0.1, dur=0.6)
    gaps = VGroup(*[arrow(W(q), W(LOOP @ q), C.comm, width=C.stroke + 1, tip=0.14) for q in SQ])
    m.play(LaggedStart(*[GrowArrow(g) for g in gaps], lag_ratio=0.15), at=T.arent + 0.1, dur=0.6)
    cfield = field_arrows(-CA, center=O, unit=U, box=(-7.0, -4.0, 7.0, 4.0), spacing=0.9, opacity=0.35)
    cfield.set_color(C.comm)
    mf.play(FadeIn(cfield), at=T.squashed + 0.2, dur=0.8)
    corner = W(LOOP @ SQ[2])
    s.camera.frame(at=T.squashed + 0.5, center=(float(corner[0] - 0.4), float(corner[1] - 0.2)), zoom=1.9, dur=1.2)
    s.camera.frame(at=T.neither, center=(0.0, 0.0), zoom=1.0, dur=1.2)
    sq_l = backed(lab("squashed", 26, C.comm), buff=0.06).move_to(p3(W((0, -HALF)) + [0, -0.55]))
    st_l = backed(lab("stretched", 26, C.comm), buff=0.06).move_to(p3(W((HALF, 0)) + [1.35, 0]))
    m.play(FadeIn(sq_l), FadeIn(st_l), at=T.squashed + 1.4, dur=0.5)
    ba = backed(VGroup(tex(r"\approx I + s^2", r"[B,A]", size=40, colors={1: C.comm}))).move_to([4.6, 2.0, 0])
    m.play(FadeIn(ba, shift=0.1 * DOWN), at=T.neither + 0.5, dur=0.6)
    loop_bits = VGroup(ghost, gaps, sq_l, st_l, ba)
    m.play(FadeOut(loop_bits), at=T.park - 0.6, dur=0.5)
    mf.play(FadeOut(cfield), at=T.park - 0.6, dur=0.5)
    mg.play(FadeOut(grid), at=T.park - 0.6, dur=0.5)

    # ── parallel park: drive and steer in a loop, and the car moves sideways ──
    c0, c1 = T.park + 0.4, T.park + 4.4
    curb = Line(p3(CAR0 + [-6.2, -2.55]), p3(CAR0 + [3.4, -2.55]), color=C.muted, stroke_width=C.thin + 0.4)
    m.play(Create(curb), at=T.park - 0.1, dur=0.5)
    cs = car(0, 0, 0, 0, 0.35)
    m.play(FadeIn(cs), at=T.park, dur=0.4)

    def drive(t):
        u = float(np.clip((t - c0) / (c1 - c0), 0, 1))
        k = int(u * (len(CAR) - 1))
        x, y, th, ph = CAR[k]
        trail = poly([CAR0 + CS * r[:2] for r in CAR[:max(k, 1) + 1]], C.flow, C.thin + 0.6, opacity=0.8)
        return VGroup(trail, car(x, y, th, ph, 1.0, C.vec))
    hs = live(m, drive, (c0 - 0.1, c1 + 0.05))
    end = CAR[-1]
    side = arrow(CAR0 + CS * np.array([end[0] + 0.5, 0]), CAR0 + CS * (end[:2] + [0.5, 0]), C.comm, width=C.stroke + 1.5, tip=0.18)
    m.play(GrowArrow(side), at=T.car_sideways + 0.2, dur=0.5)
    sd = backed(lab("sideways", 26, C.comm), buff=0.05).next_to(side, LEFT, buff=0.15).shift(0.9 * UP)
    m.play(FadeIn(sd), at=T.car_sideways + 0.5, dur=0.4)
    m.play(FadeOut(VGroup(curb, cs, side, sd, hs[-1])), at=T.survives - 0.3, dur=0.5)

    # ── the rule survives when they commute: the spiral = shrink × rotation ──
    sp_m = Mat([[r"-\tfrac14", "-1"], ["1", r"-\tfrac14"]], colors=C.gen, size=38, h_buff=1.1, v_buff=0.78)
    l1 = VGroup(sp_m, tex("=", r"-\tfrac14 I", "+", "J", size=46, colors={1: C.warm, 3: C.eigen})).arrange(
        RIGHT, buff=0.25).move_to([1.6, 2.2, 0])
    m.play(FadeIn(l1, shift=0.1 * DOWN), at=T.survives + 0.6, dur=0.7)
    l2 = tex(r"\left[-\tfrac14 I,\; J\right]", "=", "0", size=46, colors={0: C.comm, 2: C.comm}).move_to([1.6, 0.55, 0])
    m.play(FadeIn(l2, shift=0.1 * DOWN), at=T.shrink_turn + 0.3, dur=0.6)
    l3 = tex(r"e^{t(-\frac14 I + J)}", "=", r"e^{-t/4}", r"\,e^{tJ}", size=52, colors={0: C.flow, 2: C.warm, 3: C.eigen})
    l3.move_to([1.6, -1.15, 0])
    m.play(FadeIn(l3, shift=0.1 * DOWN), at=T.shrink_turn + 2.4, dur=0.7)
    u1 = lab("shrink", 26, C.warm).next_to(l3[2], DOWN, buff=0.3)
    u2 = lab("rotation", 26, C.eigen).next_to(l3[3], DOWN, buff=0.3).align_to(u1, UP)
    m.play(FadeIn(u1), FadeIn(u2), at=T.shrink_turn + 3.4, dur=0.5)
    ts = np.linspace(0, 4 * PI, 400)
    sp = VMobject(stroke_color=C.flow, stroke_width=C.stroke).set_points_smoothly(
        [p3(np.array([-4.9, 0.4]) + 1.9 * np.exp(-ts / 4) * np.array([np.cos(ts), np.sin(ts)])) for ts in ts])
    m.play(Create(sp, rate_func=linear), at=T.survives + 1.4, dur=3.0)
    m.play(FadeOut(VGroup(l1, l2, l3, u1, u2, sp)), at=T.cut_ch6 - 0.4, dur=0.5)
    finish(s)
