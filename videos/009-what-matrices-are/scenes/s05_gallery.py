"""Ch2 · A machine that moves space (2/2): the freedom inside the rules (rotate, stretch, shear like a deck of cards,
flip like a mirror, squash flat) and the two things a linear move can't do (bend lines, drag the center). Then the
same moves in 3D: the floor tips back, and a lit die is turned, stretched, sheared and flattened, its lattice riding
along cell for cell. Where do the numbers come in?"""
from aion import *

from beats import T
from shots import (FRAME, I2, I3, O3, SHEAR, U3, Cam, arrow, backdrop, die_height, die_rgba, finish, grid_lines,
                   lattice, live, panel, pt, rail, rot2, rot3z, warped_grid)

E = "smooth"
O, U = (-0.5, -0.6), 0.95                               # s04's grid
AZ, EL, CO, CU = -30.0, 22.0, np.array([0.8, -0.6]), 1.45
DRAG = np.array([1.6, 0.9])
STRETCH3 = np.diag([1.5, 1.0, 0.7])
SHEAR3 = np.array([[1, 0, 0.7], [0, 1, 0], [0, 0, 1]], float)
FLAT3 = np.diag([1.0, 1.0, 0.06])
F_SHAPE = [[(0.6, 0.3), (0.6, 2.3), (1.9, 2.3)], [(0.6, 1.35), (1.5, 1.35)]]   # an F, so the flip reads


def segments():
    """2D gallery (t0, t1, f(u) -> matrix, ease); each move leaves from home and comes back."""
    lerp = lambda P, Q: (lambda u: P + u * (Q - P))     # noqa: E731
    D, FL, SQ = np.diag([2.0, 0.5]), np.diag([-1.0, 1.0]), np.diag([1.0, 0.0])
    return [
        (T.rotate + 0.3, T.rotate + 1.7, lambda u: rot2(45 * u), E),
        (T.stretch - 0.3, T.stretch + 0.2, lambda u: rot2(45 * (1 - u)), E),
        (T.stretch + 0.4, T.stretch + 1.8, lerp(I2, D), E),
        (T.shear - 1.0, T.shear - 0.2, lerp(D, I2), E),
        (T.shear + 0.3, T.shear + 1.7, lerp(I2, SHEAR), E),
        (T.flip - 0.7, T.flip - 0.05, lerp(SHEAR, I2), E),
        (T.flip + 0.2, T.flip + 1.4, lerp(I2, FL), E),
        (T.squash - 1.0, T.squash - 0.2, lerp(FL, I2), E),
        (T.squash + 0.1, T.squash + 1.7, lerp(I2, SQ), E),
        (T.curves - 1.9, T.curves - 1.1, lerp(SQ, I2), "out_back"),
    ]


SEGS = segments()
EASED = [keys((a, 0.0), (b, 1.0, e), lead=0) for a, b, _, e in SEGS]


def M2(t):
    out = I2
    for (a, _, f, _), u in zip(SEGS, EASED):
        if t >= a:
            out = f(u(t))
    return out


def floor(cam, L, minor_op):
    """The z = 0 grid seen through `cam`: integer lines out to |k| <= L (outer lines fade), each 2L long."""
    out = VGroup()
    K = int(np.ceil(L)) + 1
    for ax in (0, 1):
        for k2 in range(-2 * K, 2 * K + 1):
            k = k2 / 2
            minor = k2 % 2 != 0
            op = float(np.clip(L - abs(k) + 1, 0, 1)) * (minor_op if minor else 1.0)
            if op < 0.02:
                continue
            a, b = np.zeros(3), np.zeros(3)
            a[ax], b[ax] = -L, L
            a[1 - ax] = b[1 - ax] = k
            col = C.grid_minor if minor else (C.axis if k == 0 else C.grid)
            w = C.thin * (0.7 if minor else (1.5 if k == 0 else 1.0))
            out.add(Line(cam.scr(a), cam.scr(b), color=col, stroke_width=w, stroke_opacity=op))
    return out


def cross(center, size=1.5):
    c = np.array([*center, 0.0])
    h = size / 2
    return VGroup(Line(c + [-h, -h, 0], c + [h, h, 0]), Line(c + [-h, h, 0], c + [h, -h, 0])).set_stroke(C.null, 9)


@scene(T.cut_gallery, T.cut_ch3)
def s05_gallery(s):
    backdrop(s)
    p0, p1 = T.three_d + 0.1, T.three_d + 1.9           # the floor tips back
    flat_out = keys((p0, 1.0), (p0 + 0.4, 0.0), lead=0)
    ghost = s.manim(z=0, opacity=flat_out)
    m = s.manim(z=1, opacity=flat_out)                 # the flat grid hands over to the tipping floor
    g = s.manim(z=3)
    hb = s.manim(z=4.9, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)
    rl = s.manim(z=5.1, parallax=0.0)
    rail(rl, 1, drop=(2, T.numbers_q + 0.6))
    ghost.add(grid_lines(I2, O, U, FRAME, color=C.ghost, axes=False))

    # ── the gallery, plus the two moves that break the rules ──
    w = keys((T.curves, 0.0), (T.curves + 1.0, 1.0, E), (T.curves + 1.5, 1.0), (T.drag - 0.1, 0.0, E), lead=0)
    d = keys((T.drag + 0.2, 0.0), (T.drag + 1.3, 1.0, E), (T.drag + 1.9, 1.0), (T.drag + 2.6, 0.0, E), lead=0)
    f_op = keys((T.flip - 0.3, 0.0), (T.flip + 0.1, 1.0), (T.squash - 1.2, 1.0), (T.squash - 0.8, 0.0), lead=0)

    def stage(t):
        Mt, wt = M2(t), w(t)
        if wt > 1e-3:
            out = VGroup(warped_grid(Mt, wt, O, U))
        else:
            out = VGroup(grid_lines(Mt, np.array(O) + U * d(t) * DRAG, U, FRAME))
        fo = f_op(t)
        if fo > 0.01:
            for stroke in F_SHAPE:
                out.add(VMobject(stroke_color=C.vec, stroke_width=C.stroke + 2, stroke_opacity=fo)
                        .set_points_as_corners([pt(O, U, Mt @ np.array(q)) for q in stroke]))
        return out
    m.add(grid_lines(I2, O, U, FRAME))
    wins = [(a, b) for a, b, _, _ in SEGS] + [(T.flip - 0.3, T.flip + 0.1), (T.squash - 1.2, T.squash - 0.8),
                                              (T.curves, T.drag - 0.1), (T.drag + 0.2, T.drag + 2.6)]
    live(m, stage, *wins)
    for t_x in (T.curves + 1.1, T.drag + 1.4):
        x = cross((0.0, 0.4))
        hud.play(FadeIn(x, scale=1.4), at=t_x, dur=0.35, ease="out_back")
        hud.play(FadeOut(x), at=t_x + 0.9, dur=0.3)

    # a deck of cards, sheared the same way
    dk = (3.7, -3.75, 6.75, -1.25)
    cards = VGroup(*[RoundedRectangle(corner_radius=0.05, width=1.7, height=0.24, stroke_color=C.text, stroke_width=1.6,
                                      fill_color=C.bg, fill_opacity=1).move_to([5.0, -3.3 + 0.3 * i, 0])
                     for i in range(7)])
    dpan = panel(*dk)
    deck_t = T.shear + 1.6
    hb.play(FadeIn(dpan), at=deck_t, dur=0.4)
    g_d = s.manim(z=5.05, parallax=0.0)
    g_d.play(FadeIn(cards), at=deck_t + 0.1, dur=0.4)
    g_d.play(*[c.animate.shift(0.16 * i * RIGHT) for i, c in enumerate(cards)], at=T.shear + 2.0, dur=1.3, ease=E)
    g_d.play(FadeOut(cards), at=T.flip - 0.7, dur=0.4)
    hb.play(FadeOut(dpan), at=T.flip - 0.6, dur=0.4)

    # ── and in three dimensions: the floor tips back; a die rides through the same moves ──
    tip = keys((p0, 0.0), (p1, 1.0, "easy_ease"), lead=0)

    def cam_at(t):
        u = tip(t)
        return Cam(AZ * u, 90 + (EL - 90) * u, origin=(1 - u) * np.array(O) + u * CO, unit=(1 - u) * U + u * CU)
    cam = cam_at(p1)
    fl = s.manim(z=1.1, opacity=keys((p1 - 0.2, 1.0), (p1 + 0.6, 0.0), lead=0))
    fl.redraw(lambda t: floor(cam_at(t), 10 - 8.5 * tip(t), max(0.0, 1 - 3 * tip(t))), during=(p0, p1))
    t0 = [T.die + 0.65, T.die + 1.5, T.die + 2.3, T.die + 3.05]      # turned, stretched, sheared, flattened
    t1 = [t0[0] + 0.8, t0[1] + 0.8, t0[2] + 0.8, t0[3] + 0.9]
    us = [keys((a, 0.0), (b, 1.0, E), lead=0) for a, b in zip(t0, t1)]
    r0, r1 = T.cell + 0.9, T.cell + 2.4
    back = keys((r0, 0.0), (r1, 1.0, "out_back"), lead=0)

    def M3(t):
        u1, u2, u3, u4 = (u(t) for u in us)
        Mt = (I3 + u4 * (FLAT3 - I3)) @ (I3 + u3 * (SHEAR3 - I3)) @ (I3 + u2 * (STRETCH3 - I3)) @ rot3z(60 * u1)
        return Mt + back(t) * (I3 - Mt)
    assert np.allclose(M3(r1 + 1), I3)
    l_op = keys((p1 - 0.3, 0.0), (p1 + 0.5, 1.0), (T.cut_ch3 - 1.0, 1.0), (T.cut_ch3 - 0.3, 0.0), lead=0)
    lt = s.manim(z=1.2, opacity=l_op)
    lt.add(lattice(cam, I3, n=1, box=2.6), at=p1 - 0.3)
    live(lt, lambda t: lattice(cam, M3(t), n=1, box=2.6), (t0[0], t1[3]), (r0, r1))
    s.add(FramesLayer(lambda t: die_rgba(0.5 * M3(t), az=AZ, el=EL, size=900), height=die_height(CU), pos=tuple(CO),
                      z=2, start=p1 - 0.3, during=[(t0[0], t1[3]), (r0, r1)],
                      opacity=keys((T.die - 0.3, 0.0), (T.die + 0.4, 1.0), (T.cut_ch3 - 1.0, 1.0),
                                   (T.cut_ch3 - 0.3, 0.0), lead=0)))
    o = cam.scr(np.zeros(3))
    cols = lambda: [C.ihat, C.jhat, C.khat]             # noqa: E731
    a_op = keys((T.die + 0.2, 0.0), (T.die + 0.8, 1.0), (T.cut_ch3 - 1.0, 1.0), (T.cut_ch3 - 0.3, 0.0), lead=0)
    ga = s.manim(z=3.1, opacity=a_op)

    def hats(t):
        Mt = M3(t)
        return VGroup(*[arrow(o, cam.scr(Mt[:, j]), cols()[j], width=C.stroke + 1) for j in range(3)])
    ga.add(hats(0.0), at=T.die)
    live(ga, hats, (t0[0], t1[3]), (r0, r1))

    # hand over to chapter 3: the flat ch3 grid
    nxt = s.manim(z=0.9, opacity=keys((T.cut_ch3 - 0.9, 0.0), (T.cut_ch3 - 0.1, 1.0), lead=0))
    nxt.add(grid_lines(I2, O3, U3, FRAME))
    finish(s)
