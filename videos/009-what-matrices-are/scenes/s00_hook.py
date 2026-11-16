"""Hook: nine numbers in a box. They fly in out of deep space and lock into a 3 × 3; a constellation of everything
they run (pixels, arrows, a camera's cube, a web, an ellipse, a network's data) lights up around them, then drains
away to a grey, boring table. Given a grid to act on, the colour floods back: the grid ripples out, tips into 3D,
the columns lift off as arrows, and the lattice, a lit die and a cloud of points tilt, stretch and fold together
under an orbiting camera. Then a montage of where matrices live, and the grey row-times-column crawl."""
from aion import *

from beats import T
from nets import forward, net, spirals
from shots import (H3, I3, Cam, Mat, arrow, backdrop, backing, die_height, die_rgba, finish, grid_lines, lattice, live,
                   photo, rot3, rot3z, tex, I2, FRAME)

E = "smooth"
AZ0, EL, CO, CU = -40.0, 22.0, np.array([1.2, -0.5]), 1.3   # the 3D view the floor tips into (then orbits)
ORBIT = 2.6                                                  # degrees per second of slow orbit
COLS3 = lambda: [C.ihat, C.jhat, C.khat]                     # noqa: E731
FOLD = np.diag([1.0, 1.0, 0.04]) @ H3                        # squashed onto the floor
TILT = rot3(2, 18) @ rot3(0, -16)                            # a first lean, on the way to H
BOXC = np.array([0.0, 0.2, 0.0])                             # the box, centre stage
U2 = 0.9                                                     # the flat grid's unit (top-down view of the floor)
RX, RY = 5.3, 2.95                                          # the constellation's orbit


def scr_many(cam, P):
    """Project many world points (N, 3) through `cam` at once → (N, 2)."""
    q = np.asarray(P, float) @ cam.R.T
    x, y = q[:, 0], q[:, 2] * cam.ce + q[:, 1] * cam.se
    k = cam.dist / (cam.dist + q[:, 1] * cam.ce - q[:, 2] * cam.se)
    return np.c_[cam.o[0] + cam.u * k * x, cam.o[1] + cam.u * k * y]


def floor(cam, L, minor_op, reveal=99.0, op=1.0):
    """The z = 0 grid through `cam`: lines out to |k| <= L; `reveal` grows the grid outward from the centre."""
    out = VGroup()
    K = int(np.ceil(L)) + 1
    for ax in (0, 1):
        for k2 in range(-2 * K, 2 * K + 1):
            k = k2 / 2
            minor = k2 % 2 != 0
            o_ = float(np.clip(L - abs(k) + 1, 0, 1)) * (minor_op if minor else 1.0)
            o_ *= float(np.clip(reveal - abs(k), 0, 1)) * op
            if o_ < 0.02:
                continue
            half = min(L, max(reveal, 0.0) * 1.2)
            a, b = np.zeros(3), np.zeros(3)
            a[ax], b[ax] = -half, half
            a[1 - ax] = b[1 - ax] = k
            col = C.grid_minor if minor else (C.axis if k == 0 else C.grid)
            w = C.thin * (0.7 if minor else (1.5 if k == 0 else 1.0))
            out.add(Line(cam.scr(a), cam.scr(b), color=col, stroke_width=w, stroke_opacity=o_))
    return out


def icons():
    """Six things a matrix runs, each about 1 unit across, centred at the origin."""
    px = VGroup(*[Square(0.24, stroke_width=0.8, stroke_color=C.ghost, fill_color=C.text,
                         fill_opacity=float(v)).move_to([(j - 1.5) * 0.24, (1.5 - i) * 0.24, 0])
                  for (i, j), v in np.ndenumerate(photo()[60:420, 60:420].reshape(4, 90, 4, 90).mean(axis=(1, 3)))])
    hats = VGroup(arrow((-0.4, -0.4), (0.45, -0.4), C.ihat, width=C.stroke, tip=0.18),
                  arrow((-0.4, -0.4), (-0.4, 0.45), C.jhat, width=C.stroke, tip=0.18))
    cc = Cam(-35.0, 22.0, unit=0.36)
    cn = [np.array([(k >> 2 & 1) * 2 - 1, (k >> 1 & 1) * 2 - 1, (k & 1) * 2 - 1], float) for k in range(8)]
    cube = VGroup(*[Line(cc.scr(cn[a]), cc.scr(cn[b]), color=C.text, stroke_width=1.6)
                    for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count("1") == 1])
    nodes = [(-0.45, 0.35), (0.45, 0.4), (0.0, -0.05), (-0.35, -0.45), (0.45, -0.4)]
    web = VGroup(*[Line([*nodes[a], 0], [*nodes[b], 0], color=C.muted, stroke_width=1.2)
                   for a, b in ((0, 2), (1, 2), (2, 3), (2, 4), (3, 4), (0, 1))],
                 *[Dot([*p, 0], radius=0.07, color=C.eigen if i == 2 else C.text) for i, p in enumerate(nodes)])
    ell = VGroup(Circle(radius=0.38, color=C.ghost, stroke_width=1.2),
                 Ellipse(width=1.05, height=0.36, color=C.sigma, stroke_width=2.2).rotate(0.5)).set_fill(opacity=0)
    X, Y = spirals()
    sel = np.arange(0, len(X), 9)
    spi = VGroup(*[Dot([*(0.48 * X[i]), 0], radius=0.025, color=C.cls_a if Y[i] == 0 else C.cls_b) for i in sel])
    return [px, hats, cube, web, ell, spi]


@scene(T.start, T.cut_preview)
def s00_hook(s):
    backdrop(s)
    t3 = T.photo - 1.0                                  # the 3D shot ends
    out3 = keys((t3, 1.0), (t3 + 0.7, 0.0), lead=0)
    hb = s.manim(z=4.8, parallax=0.0)
    hud = s.manim(z=5, parallax=0.0)
    mt = s.manim(z=4)                                   # montage + the grey product

    # ══ 0–3 s · out of the dark: a slow drift of deep space, nine digits fly in and lock into a box ══
    rr = np.random.default_rng(21)
    NS = 420
    SP = np.c_[rr.uniform(-14, 14, NS), rr.uniform(-8, 8, NS), rr.uniform(0, 26, NS)]
    sf_op = keys((0.0, 0.0), (1.2, 0.55), (T.boring - 0.2, 0.55), (T.boring + 1.2, 0.18), (T.alive - 1.8, 0.18),
                 (T.alive - 1.0, 0.0), lead=0)

    def stars(t):
        z = (SP[:, 2] - 1.6 * t) % 26 + 1.5               # drifting toward us, wrapping far away
        return SP[:, :2] * (5.0 / z)[:, None]
    s.add(PointsLayer(stars, color=C.muted, size=2.2, glow=0.0, additive=False, z=-1, opacity=sf_op))

    Hm = Mat(H3, size=96, h_buff=1.5, v_buff=1.15).move_to(BOXC)
    cells = [Hm.cell(i, j) for i in range(3) for j in range(3)]
    FLY = 1.6
    land = [T.box - 0.25 + 0.17 * k for k in rr.permutation(9)]     # lands in a scattered order, 1.25 … 2.6
    ang = rr.uniform(0, 2 * np.pi, 9)
    start = [c.get_center() + rr.uniform(6.0, 9.0) * np.array([np.cos(a), 0.62 * np.sin(a), 0])
             for c, a in zip(cells, ang)]
    twirl = rr.uniform(-1.6, 1.6, 9)

    def flight(t):
        out = VGroup()
        for k, c in enumerate(cells):
            u = (t - (land[k] - FLY)) / FLY
            if u <= 0 or u >= 1:
                continue
            e = 1 - (1 - u) ** 3                          # fast from far away, settling in
            d = c.get_center() - start[k]
            bend = np.array([-d[1], d[0], 0]) * 0.22 * np.sin(np.pi * e)
            out.add(c.copy().scale(0.15 + 0.85 * e).rotate(twirl[k] * (1 - e))
                    .move_to(start[k] + e * d + bend).set_opacity(min(1.0, 3 * u)))
        return out
    fl = hud.redraw(flight, during=(min(land) - FLY, max(land)))
    hud.remove(fl, at=max(land) + 0.02)
    for k, c in enumerate(cells):
        hud.add(c, at=land[k])
        ring0 = Circle(radius=0.32, color=COLS3()[k % 3], stroke_width=2.0).move_to(c)
        hud.play(ring0.animate.scale(2.4).set_stroke(opacity=0), at=land[k], dur=0.6, ease="linear")
    # the box closes around them on "box"
    hud.play(FadeIn(Hm.br, scale=1.35), at=T.box + 1.7, dur=0.55, ease="out_back")

    # ══ 4.7–8.5 s · "the most useful object in all of mathematics": a constellation lights up around it ══
    ic = icons()
    HW, HH = Hm.width / 2 + 0.15, Hm.height / 2 + 0.15     # spokes start at the box's edge
    c0 = T.useful - 0.5
    fade_c = keys((T.boring - 0.15, 0.0), (T.boring + 0.9, 1.0, E), lead=0)

    def constellation(t):
        out = VGroup()
        c = fade_c(t)
        dim = (1 - c) ** 2                                # gone before it reaches the digits
        if c >= 0.999:
            return out
        th0 = 0.4 + 0.11 * (t - c0)                      # the ring turns slowly the whole time
        for k, icon in enumerate(ic):
            th = th0 + 2 * np.pi * k / 6
            dirv = np.array([np.cos(th), np.sin(th), 0])
            r = 1 - 0.4 * c                               # ... and drains back toward the box on "boring"
            P = BOXC + r * np.array([RX * np.cos(th), RY * np.sin(th), 0])
            E0 = BOXC + dirv * min(HW / max(abs(dirv[0]), 1e-6), HH / max(abs(dirv[1]), 1e-6))
            Ln = P - 0.72 * dirv * r
            f = float(np.clip((t - (c0 + 0.28 * k)) / 0.45, 0, 1))
            a = float(np.clip((t - (c0 + 0.35 + 0.28 * k)) / 0.45, 0, 1))
            if f > 0:
                out.add(Line(E0, E0 + f * (Ln - E0), color=C.frame, stroke_width=1.2, stroke_opacity=0.8 * dim))
                # a pulse runs out along each spoke: the box feeding the thing it runs
                ph = ((t - c0) * 0.7 + 0.17 * k) % 1.0
                if a > 0.99 and c < 0.05:
                    out.add(Dot(E0 + ph * (Ln - E0), radius=0.045, color=C.text).set_opacity(0.9 * (1 - ph)))
            if a > 0:
                pop = 1 + 0.18 * np.sin(np.pi * a) * (1 - a) * 3
                out.add(icon.copy().scale(pop * (0.5 + 0.5 * a) * (1 - 0.6 * c)).move_to(P)
                        .fade(1 - a * dim))
        return out
    cs = hud.redraw(constellation, during=(c0, T.boring + 0.95))
    hud.remove(cs, at=T.boring + 0.96)

    # ══ 8.6–10 s · "... also looks like the most boring": the colour drains, the stars dim ══
    for j, col in enumerate(Hm.cols):
        hud.play(col.animate.set_color(C.muted), at=T.boring + 0.1 + 0.12 * j, dur=0.7)

    # ══ 11–14 s · "give it something to act on": a grid ripples out under it, the colour floods back ══
    cam_flat = Cam(0.0, 90.0, origin=BOXC[:2], unit=U2)
    g0 = T.alive - 1.7                                  # "But give it something to act on"
    p0, p1 = T.alive + 0.15, T.columns - 0.15           # the floor tips into 3D
    rev = keys((g0, 0.0), (g0 + 1.6, 11.0, E), lead=0)
    tip = keys((p0, 0.0), (p1, 1.0, "easy_ease"), lead=0)

    def az_at(t):
        return AZ0 * tip(t) + ORBIT * max(0.0, t - p1)

    def cam_at(t):
        u = tip(t)
        return Cam(az_at(t), 90 + (EL - 90) * u, origin=(1 - u) * BOXC[:2] + u * CO, unit=(1 - u) * U2 + u * CU)
    fl_op = keys((g0, 1.0), (p1 - 0.3, 1.0), (p1 + 0.6, 0.45), (t3, 0.45), (t3 + 0.7, 0.0), lead=0)
    flr = s.manim(z=0.5, opacity=fl_op)
    flr.redraw(lambda t: floor(cam_at(t), 10 - 7.5 * tip(t), max(0.0, 1 - 2.5 * tip(t)), reveal=rev(t)),
               during=(g0, t3 + 0.7))
    bk = Rectangle(width=Hm.width + 0.5, height=Hm.height + 0.4, stroke_width=0, fill_color=C.bg,
                   fill_opacity=1).move_to(BOXC)
    hb.play(FadeIn(bk), at=g0 - 0.2, dur=0.3)
    for j, col in enumerate(Hm.cols):
        hud.play(col.animate.set_color(COLS3()[j]), at=T.alive - 0.05 + 0.15 * j, dur=0.5)
        hud.play(Indicate(col, color=COLS3()[j], scale_factor=1.15), at=T.alive - 0.05 + 0.15 * j, dur=0.6)
    Hs = Mat(H3, size=52, h_buff=0.85, v_buff=0.7)
    Hs.move_to([-7.11 + C.margin + 0.35 + Hs.width / 2, 3.55 - C.margin - Hs.height / 2, 0])
    hud.play(ReplacementTransform(Hm, Hs), at=T.alive + 0.45, dur=1.1, ease=E)
    hb.play(Transform(bk, backing(Hs, pad=0.25)), at=T.alive + 0.45, dur=1.1, ease=E)

    # ══ 13–22 s · the lattice, a lit die and a cloud of points, under a slowly orbiting camera ══
    m3 = s.manim(z=1, opacity=keys((p1 - 0.5, 0.0), (p1 + 0.3, 1.0), (t3, 1.0), (t3 + 0.7, 0.0), lead=0))
    tl0, tl1 = T.tilts + 1.0, T.tilts + 1.75           # "tilts"
    st0, st1 = T.tilts + 1.85, T.tilts + 2.55          # "stretches"
    fo0, fo1 = T.tilts + 2.6, T.tilts + 3.35           # "and folds"
    r0, r1 = T.ride - 1.1, T.ride + 0.6                # "... goes along for the ride": home, with a spring
    M = keys((tl0, I3), (tl1, TILT, E), (st0, TILT), (st1, H3, E), (fo0, H3), (fo1, FOLD, E), (r0, FOLD),
             (r1, I3, "out_back"), lead=0)
    live(m3, lambda t: lattice(cam_at(t), M(t), n=1, box=2.6), (p1 - 0.5, t3 + 0.7))
    s.add(FramesLayer(lambda t: die_rgba(0.5 * M(t), az=az_at(t), el=EL, size=900), height=die_height(CU),
                      pos=tuple(CO), z=2, start=p1 - 0.2, during=[(p1 - 0.2, t3 + 0.7)],
                      opacity=keys((p1 - 0.1, 0.0), (p1 + 0.6, 1.0), (t3, 1.0), (t3 + 0.7, 0.0), lead=0)))
    # anything living in that space: 260 points scattered through the lattice, riding with it
    cloud = rr.uniform(-1, 1, (900, 3))
    cloud = cloud[np.abs(cloud).max(axis=1) > 0.62][:260]
    pt_op = keys((T.columns + 0.4, 0.0), (T.columns + 1.6, 0.55), (T.ride - 1.8, 0.55), (T.ride - 1.2, 1.0),
                 (t3, 1.0), (t3 + 0.7, 0.0), lead=0)
    s.add(PointsLayer(lambda t: scr_many(cam_at(t), cloud @ M(t).T), color=C.vec, size=4.0, glow=0.0,
                      additive=False, z=1.5, opacity=pt_op))

    # each column lifts off the box into its arrow (where an axis must land); then space moves onto them
    lifts = [T.columns + 0.05 + 0.4 * j for j in range(3)]
    LD = 0.8
    g = s.manim(z=3, opacity=out3)

    def col_arrow(cam, v, j, width, op=1.0):
        return arrow(cam.scr(np.zeros(3)), cam.scr(v), COLS3()[j], width=width, opacity=op)
    h0 = [col_arrow(cam_at(tl + LD), H3[:, j], j, C.stroke + 1.5) for j, tl in enumerate(lifts)]
    for j, tl in enumerate(lifts):
        hud.play(Indicate(Hs.cols[j], color=COLS3()[j], scale_factor=1.25), at=tl - 0.1, dur=0.5)
        g.play(TransformFromCopy(Hs.cols[j], h0[j]), at=tl, dur=LD, ease=E)
        g.remove(h0[j], at=tl + LD + 0.01)

    def arrows(t):
        cam, Mt = cam_at(t), M(t)
        out = VGroup()
        for j, tl in enumerate(lifts):
            if t < tl + LD:
                continue
            if t < st1:                                   # the target (H's column) and the axis travelling to it
                out.add(col_arrow(cam, H3[:, j], j, C.stroke + 1.5, op=0.45 if t > tl0 else 1.0))
                if t > tl0:
                    out.add(col_arrow(cam, Mt[:, j], j, C.stroke + 1.5))
            else:
                out.add(col_arrow(cam, Mt[:, j], j, C.stroke + 1.5))
        return out
    live(g, arrows, (lifts[0] + LD, t3 + 0.7))

    # the area-ish readout: how much the move scales volume, live
    det_op = keys((tl0 - 0.3, 0.0), (tl0 + 0.1, 1.0), (t3, 1.0), (t3 + 0.6, 0.0), lead=0)
    dh = s.manim(z=5, parallax=0.0, opacity=det_op)
    det_pos = Hs.get_corner(DL) + np.array([0.0, -0.55, 0])

    def det_read(t):
        d = float(np.linalg.det(M(t)))
        r = tex(r"\det", "=", f"{d:.1f}", size=44, colors={2: C.area})
        return r.move_to(det_pos + np.array([r.width / 2, 0, 0]))
    dh.redraw(det_read, during=(tl0 - 0.3, r1 + 0.1))
    hud.play(FadeOut(Hs), at=t3, dur=0.6)
    hb.play(FadeOut(bk), at=t3, dur=0.6)

    # ── montage 1: every photo is a grid of numbers ──
    pic = photo()
    g8 = (pic * 255).astype(np.uint8)
    PH = 4.6
    p_op = keys((T.photo, 0.0), (T.photo + 0.6, 1.0), (T.photo + 2.4, 1.0), (T.photo + 3.4, 0.0), lead=0)
    s.add(ArrayLayer(np.dstack([g8, g8, g8, np.full_like(g8, 255)]), height=PH, pos=(0.0, -0.1), z=2, opacity=p_op))
    n = 10
    blocks = pic.reshape(n, 480 // n, n, 480 // n).mean(axis=(1, 3))
    cell = PH / n
    sq = VGroup()
    for i in range(n):
        for j in range(n):
            v = float(blocks[i, j])
            x, y = -PH / 2 + (j + 0.5) * cell, -0.1 + PH / 2 - (i + 0.5) * cell
            box = Square(cell, stroke_color=C.ghost, stroke_width=1, fill_color=C.text, fill_opacity=v).move_to([x, y, 0])
            num = tex(str(int(round(v * 255))), size=20, color=C.bg if v > 0.55 else C.text).move_to([x, y, 0])
            sq.add(VGroup(box, num))
    mt.play(FadeIn(sq, lag_ratio=0.004), at=T.photo + 2.3, dur=1.2)
    mt.play(FadeOut(sq), at=T.game - 0.4, dur=0.5)

    # ── montage 2: every frame of a game: a wireframe die, a camera frustum ──
    gc = Cam(-35.0, 22.0, origin=(1.2, -0.4), unit=1.1)
    spin = keys((T.game, 0.0), (T.google + 0.2, 160.0, "linear"), lead=0)
    w_op = keys((T.game - 0.2, 0.0), (T.game + 0.3, 1.0), (T.google - 0.2, 1.0), (T.google + 0.3, 0.0), lead=0)
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count("1") == 1]
    corners = [np.array([(k >> 2 & 1) * 2 - 1, (k >> 1 & 1) * 2 - 1, (k & 1) * 2 - 1], float) for k in range(8)]
    eye = np.array([-5.2, -1.2, 1.6])

    def game(t):
        o_ = w_op(t)
        if o_ < 0.01:
            return VGroup()
        R = rot3z(spin(t)) @ rot3(0, 18)
        P = [R @ c for c in corners]
        out = VGroup(*[Line(gc.scr(P[a]), gc.scr(P[b]), color=C.text, stroke_width=C.stroke, stroke_opacity=o_)
                       for a, b in edges])
        # the camera that films it: an eye, its screen, and the four edges of what it can see
        d = -eye / np.linalg.norm(eye)
        rt = np.cross(d, [0, 0, 1.0]); rt /= np.linalg.norm(rt)
        up = np.cross(rt, d)
        scr = [eye + 1.6 * d + sx * 0.75 * rt + sy * 0.5 * up for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for c in scr:
            out.add(Line(gc.scr(eye), gc.scr(eye + 3.9 * (c - eye)), color=C.muted, stroke_width=C.thin,
                         stroke_opacity=0.55 * o_))
        out.add(Polygon(*[gc.scr(c) for c in scr], stroke_color=C.frame, stroke_width=C.thin + 0.5,
                        stroke_opacity=o_, fill_opacity=0))
        out.add(Dot(gc.scr(eye), radius=0.07, color=C.muted).set_opacity(o_))
        return out
    mt.redraw(game, during=(T.game - 0.2, T.google + 0.3))

    # ── montage 3: a web of pages and readers ──
    POS = np.array([(-1.5, 1.4), (1.6, 1.5), (0.1, 0.0), (-2.5, -0.3), (-1.4, -2.0), (1.0, -2.3), (2.5, -0.6)])
    LINKS = {0: [2], 1: [2, 6], 2: [0, 1], 3: [2], 4: [2, 3], 5: [0, 4], 6: [5, 2]}
    web_op = keys((T.google - 0.2, 0.0), (T.google + 0.3, 1.0), (T.network - 0.2, 1.0), (T.network + 0.3, 0.0), lead=0)
    nodes = VGroup(*[Circle(radius=0.3, color=C.frame, stroke_width=C.thin + 0.5).move_to([*p, 0]) for p in POS])
    links = VGroup(*[Line([*POS[a], 0], [*POS[b], 0], color=C.muted, stroke_width=C.thin, buff=0.32)
                     for a, outs in LINKS.items() for b in outs])
    web = VGroup(links, nodes)
    mt.play(FadeIn(web), at=T.google - 0.2, dur=0.5)
    mt.play(FadeOut(web), at=T.network - 0.2, dur=0.5)
    rr = np.random.default_rng(4)
    NS, hop = 500, 0.32
    hops = np.arange(T.google, T.network + 0.4, hop)
    seq = [rr.integers(0, 7, NS)]
    for _ in hops:
        cur = seq[-1]
        seq.append(np.array([LINKS[c][rr.integers(0, len(LINKS[c]))] if rr.random() < 0.85 else rr.integers(0, 7)
                             for c in cur]))
    jit = rr.normal(0, 0.11, (NS, 2))

    def readers(t):
        k = int(np.searchsorted(hops, t, side="right"))
        if k == 0:
            return POS[seq[0]] + jit
        w = min(1.0, (t - hops[k - 1]) / (hop * 0.8))
        w = w * w * (3 - 2 * w)
        return (1 - w) * POS[seq[k - 1]] + w * POS[seq[k]] + jit
    s.add(PointsLayer(readers, color=C.text, size=2.4, glow=0.0, additive=False, z=4.5, opacity=web_op))

    # ── montage 4: a neural network folding two spirals apart ──
    X, Y = spirals()
    Ws, bs = net()
    stages = [h[:, :2] for h in forward(Ws, bs, X)[:-1]]           # the input, then each layer's folded copy
    fo = keys((T.network + 0.5, 0.0), (T.network + 4.5, float(len(stages) - 1), "linear"), lead=0)

    def folded(f, sel):
        k = min(int(f), len(stages) - 2)
        w = f - k
        w = w * w * (3 - 2 * w)
        return (1 - w) * stages[k][sel] + w * stages[k + 1][sel]
    sp_op = keys((T.network - 0.2, 0.0), (T.network + 0.3, 1.0), (T.bookkeeping - 1.4, 1.0), (T.bookkeeping - 0.8, 0.0),
                 lead=0)
    for cls, col in ((0, C.cls_a), (1, C.cls_b)):
        sel = Y == cls
        s.add(PointsLayer(lambda t, sel=sel: 2.4 * folded(fo(t), sel) + np.array([0.0, -0.2]),
                          color=col, size=4.0, glow=0.0, additive=False, z=4.5, opacity=sp_op))

    # ── the wrong first impression: the grey crawl ──
    L_ = Mat([[1, 2], [3, 4]], colors=C.muted, size=56, h_buff=0.85, v_buff=0.75)
    R_ = Mat([[5, 6], [7, 8]], colors=C.muted, size=56, h_buff=0.85, v_buff=0.75)
    eq = tex("=", size=56, color=C.muted)
    Pm = Mat([[19, 22], [43, 50]], colors=C.muted, size=56, h_buff=1.0, v_buff=0.75)
    prod = VGroup(L_, R_, eq, Pm).arrange(RIGHT, buff=0.35).move_to([0, 0.2, 0])
    for c in [Pm.cell(i, j) for i in range(2) for j in range(2)]:
        c.set_opacity(0)
    g_op = keys((T.hides + 0.4, 1.0), (T.hides + 1.4, 0.35), (T.cut_preview - 0.9, 0.35), (T.cut_preview - 0.1, 0.0),
                lead=0)
    gp = s.manim(z=4.2, opacity=g_op)
    gp.play(FadeIn(VGroup(L_, R_, eq, Pm.br)), at=T.bookkeeping - 0.3, dur=0.7)
    steps = [T.rule + 0.3 + 0.95 * k for k in range(4)]
    for k, tk in enumerate(steps):
        i, j = divmod(k, 2)
        rb = SurroundingRectangle(VGroup(L_.cell(i, 0), L_.cell(i, 1)), buff=0.1, color=C.frame, stroke_width=1.5)
        cb = SurroundingRectangle(VGroup(R_.cell(0, j), R_.cell(1, j)), buff=0.1, color=C.frame, stroke_width=1.5)
        gp.play(FadeIn(rb), FadeIn(cb), at=tk, dur=0.2, ease="linear")
        gp.play(Pm.cell(i, j).animate.set_opacity(1), at=tk + 0.35, dur=0.3, ease="linear")
        gp.play(FadeOut(rb), FadeOut(cb), at=tk + 0.75, dur=0.15, ease="linear")

    # one flat grid stays for s01
    base = s.manim(z=0.5, opacity=keys((T.hides + 0.8, 0.0), (T.hides + 2.0, 1.0), lead=0))
    base.add(grid_lines(I2, (0.0, -0.3), 0.8, FRAME, opacity=0.6))
    finish(s)
