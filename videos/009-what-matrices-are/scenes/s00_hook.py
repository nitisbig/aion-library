"""Hook: nine numbers in a box. Given space, they move it: the columns lift off as arrows, the lattice and a lit die
tilt, stretch and fold together. A montage of where matrices live (a photo's numbers, a game's wireframe, a web of
readers, a folding data set), then the wrong first impression: the grey row-times-column crawl."""
from aion import *

from beats import T
from nets import forward, net, spirals
from shots import (H3, I2, I3, FRAME, Cam, Mat, arrow, backdrop, die_height, die_rgba, finish, grid_lines, lattice, live,
                   photo, rot3, rot3z, tex)

E = "smooth"
AZ, EL, CO, CU = -30.0, 22.0, np.array([1.2, -0.5]), 1.3
COLS3 = lambda: [C.ihat, C.jhat, C.khat]                          # noqa: E731
FOLD = np.diag([1.0, 1.0, 0.04]) @ H3                               # squashed onto the floor


@scene(T.start, T.cut_preview)
def s00_hook(s):
    backdrop(s)
    t3 = T.photo - 1.0                                  # the 3D shot ends
    out3 = keys((t3, 1.0), (t3 + 0.7, 0.0), lead=0)
    m = s.manim(z=1, opacity=out3)
    g = s.manim(z=3, opacity=out3)
    hud = s.manim(z=5, parallax=0.0)
    mt = s.manim(z=4)                                   # montage + the grey product

    # ── nine numbers, arranged in a box ──
    Hm = Mat(H3, size=110, h_buff=1.7, v_buff=1.3)
    cells = [Hm.cell(i, j) for i in range(3) for j in range(3)]
    hud.play(FadeIn(Hm.br), at=T.box - 0.2, dur=0.8)
    hud.play(LaggedStart(*[FadeIn(c, scale=0.9) for c in cells], lag_ratio=0.12), at=T.box + 0.1, dur=1.6)
    Hs = Mat(H3, size=52, h_buff=0.85, v_buff=0.7)
    Hs.move_to([-7.11 + C.margin + 0.35 + Hs.width / 2, 3.55 - C.margin - Hs.height / 2, 0])
    hud.play(ReplacementTransform(Hm, Hs), at=T.alive - 0.4, dur=1.1, ease=E)

    # ── give it space: the lattice, a die, the three column arrows ──
    cam = Cam(AZ, EL, origin=CO, unit=CU)
    a0, a1 = T.tilts + 0.2, T.tilts + 2.2               # tilts, stretches ...
    f0, f1 = T.tilts + 2.6, T.tilts + 3.6               # ... and folds
    r0, r1 = T.ride + 0.4, T.ride + 1.9                 # back home, everything rode along
    Ml = keys((a0, I3), (a1, H3, E), (f0, H3), (f1, FOLD, E), (r0, FOLD), (r1, I3, "out_back"), lead=0)
    lat0 = lattice(cam, I3, n=1, box=2.6)
    m.play(FadeIn(lat0), at=T.alive, dur=1.0)
    m.remove(lat0, at=a0)
    live(m, lambda t: lattice(cam, Ml(t), n=1, box=2.6), (a0, f1), (r0, r1))
    s.add(FramesLayer(lambda t: die_rgba(0.5 * Ml(t), az=AZ, el=EL, size=900), height=die_height(CU), pos=tuple(CO),
                      z=2, start=T.alive, opacity=keys((T.alive + 0.2, 0.0), (T.alive + 1.0, 1.0), (t3, 1.0),
                                                       (t3 + 0.7, 0.0), lead=0),
                      during=[(a0, f1), (r0, r1)]))
    o = cam.scr(np.zeros(3))

    def hats(M, which=(0, 1, 2)):
        return VGroup(*[arrow(o, cam.scr(M[:, j]), COLS3()[j], width=C.stroke + 1) for j in which])
    lifts = [T.columns + 0.1 + 0.35 * j for j in range(3)]
    h0 = hats(H3)
    for j, tl in enumerate(lifts):
        hud.play(Indicate(Hs.cols[j], color=COLS3()[j], scale_factor=1.2), at=tl - 0.1, dur=0.5)
        g.play(TransformFromCopy(Hs.cols[j], h0[j]), at=tl, dur=0.9, ease=E)
    # the arrows are H's columns; while H plays they show where the axes land at each moment
    Ma = keys((a0, I3), (a1, H3, E), (f0, H3), (f1, FOLD, E), (r0, FOLD), (r1, I3, "out_back"), lead=0)
    g.remove(*h0, at=a0)
    g.add(hats(I3), at=a0 - 0.01)                        # (snaps to the axes as the move starts from home)
    live(g, lambda t: hats(Ma(t)), (a0, f1), (r0, r1))
    det = tex(r"\det", "=", "3", size=48, colors={2: C.area}).next_to(Hs, DOWN, buff=0.35).align_to(Hs, LEFT)
    hud.play(FadeIn(det, shift=0.1 * UP), at=a1 + 0.1, dur=0.5)
    hud.play(FadeOut(VGroup(det, Hs)), at=t3, dur=0.6)

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
