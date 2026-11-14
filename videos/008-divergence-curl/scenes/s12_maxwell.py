"""Ch5 · where they live. The ghosted Maxwell block from the preview returns and sharpens (promise kept), then docks
top-right as an index; each equation lights in turn with a micro-scene. div E: a + and a - charge, E lines leaving one
and ending on the other (sources and sinks). div B: a bar magnet, B lines as closed loops through the magnet (no
sources), one loop traced all the way round. curl E: a growing B out of the page wrapped by a clockwise E whirl; then
a spinning magnet drives an alternating current round a coil (a generator). curl B: a current out of the page wrapped
in B rings. Then the curl pair together: an E and B wave that travels off on its own (light). Last, the same two
questions elsewhere: water flowing round a post (div v = 0) and a hurricane over its curl map."""
from aion import *

from beats import T
from shots import BADGES, arrow, dim, ease, maxwell, ortho, ramp, stage, tex
from shots import cast_layer

E_ = "easy_ease"
SC = np.array([-0.7, -0.7])                     # stage centre for the micro-scenes
BOX = (-4.9, -3.8, 3.6, 2.3)                    # clip box for field lines
HEAD = np.array([-1.1, 3.0])                    # headline equation position


def runs(pts, box=BOX):
    """Split a polyline into the runs that lie inside box."""
    x0, y0, x1, y1 = box
    ok = (pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1)
    out, cur = [], []
    for p, k in zip(pts, ok):
        if k:
            cur.append(p)
        elif cur:
            out.append(np.array(cur))
            cur = []
    if cur:
        out.append(np.array(cur))
    return [r for r in out if len(r) > 2]


def poly(pts, color, width, opacity=1.0):
    return VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity).set_points_as_corners(
        [[x, y, 0] for x, y in pts])


def mid_head(run, color, frac=0.5, tip=0.16, width=None):
    i = int(np.clip(frac * (len(run) - 1), 1, len(run) - 3))
    a, b = run[i], run[i + 2]
    d = (b - a) / max(np.linalg.norm(b - a), 1e-9)
    return arrow(a - 0.12 * d, a + 0.12 * d, color, width=width or C.stroke, tip=tip)


def dipole_lines(p, q, n=6):
    """Field lines of a + charge at p and a - charge at q in 2D: exact circular arcs from p to q (plus the axis)."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    a = np.linalg.norm(q - p) / 2
    u = (q - p) / (2 * a)
    v = np.array([-u[1], u[0]])
    mid = (p + q) / 2
    to_w = lambda xy: mid + np.outer(xy[:, 0], u) + np.outer(xy[:, 1], v)
    lines = [to_w(np.stack([np.linspace(-a, a, 40), np.zeros(40)], 1))]
    for phi in np.linspace(np.pi / (n + 1), np.pi * n / (n + 1), n):
        cy, r = -a / np.tan(phi), a / np.sin(phi)
        th0, th1 = np.arctan2(-cy, -a), np.arctan2(-cy, a)
        # sweep from the + charge over the top (tangent (cos phi, sin phi)) to the - charge
        tang = np.array([np.cos(phi), np.sin(phi)])
        d = 1.0 if np.array([-np.sin(th0), np.cos(th0)]) @ tang > 0 else -1.0
        span = (th1 - th0) * d % (2 * np.pi)
        th = th0 + d * np.linspace(0, span, 260)
        arc = np.stack([r * np.cos(th), cy + r * np.sin(th)], 1)
        lines += [to_w(arc), to_w(arc * np.array([1, -1]))]
    for s0, s in ((p, -u), (q, u)):            # the two rays along the axis, off to infinity
        lines.append(s0 + np.outer(np.linspace(0, 12, 200), s) if s0 is p else s0 + np.outer(np.linspace(12, 0, 200), s))
    return lines


def advect_grains(v, p0, t0, t1, fps=30, respawn=None):
    """Precompute grain positions under velocity v(P) (RK2), with an optional respawn(P) -> P. Returns local(t)."""
    n = int((t1 - t0) * fps) + 2
    P = np.array(p0, float)
    frames = [P.copy()]
    dt = 1.0 / fps
    for _ in range(n):
        k1 = v(P)
        P = P + dt * v(P + 0.5 * dt * k1)
        if respawn is not None:
            P = respawn(P)
        frames.append(P.copy())
    F = np.array(frames)
    return lambda t: F[int(np.clip((t - t0) * fps, 0, len(F) - 1))]


def odot(c, r, color, k=1.0):
    return VGroup(Circle(radius=r, color=color, stroke_width=C.thin + 0.6).move_to([*c, 0]),
                  Dot([*c, 0], radius=r * 0.3, color=color)).set_opacity(k)


@scene(T.cut_ch5, T.cut_outro)
def s12_maxwell(s):
    s.solid(C.bg, z=-200)
    m = s.manim(z=4)
    stage(s, m, s.start, badges=BADGES[:3])

    # ── the block from the preview: ghosted, then sharp, then docked as an index ──
    mx = maxwell(size=50)
    grid = VGroup(VGroup(mx[0], mx[1]).arrange(RIGHT, buff=1.6), VGroup(mx[2], mx[3]).arrange(RIGHT, buff=1.2))
    grid.arrange(DOWN, buff=0.9).move_to([0, -0.1, 0])
    small = grid.copy()
    small.scale(3.9 / small.width).move_to([4.6, 3.0, 0])
    sm = [small[0][0], small[0][1], small[1][0], small[1][1]]
    t_dock = (T.div_E - 1.4, T.div_E - 0.2)
    act = [(T.div_E, T.div_B), (T.div_B, T.curl_E), (T.curl_E, T.together2), (T.curl_B, T.together2)]
    t_both = (T.together2, T.far - 0.4)
    t_end = (T.far - 0.6, T.far + 0.2)
    for i, e in enumerate(mx):
        a, b = act[i]
        fr = [(s.start, 0.0), (s.start + 0.3, 0.0), (s.start + 1.3, 0.38, E_), (T.four + 0.1, 0.38),
              (T.four + 1.0, 1.0, E_), (t_dock[1], 1.0), (t_dock[1] + 0.4, 0.3)]
        if i == 2:                              # curl E steps back while curl B speaks, then both light together
            fr += [(a - 0.3, 0.3), (a + 0.2, 1.0), (T.curl_B - 0.3, 1.0), (T.curl_B + 0.2, 0.3),
                   (t_both[0] - 0.3, 0.3), (t_both[0] + 0.3, 1.0)]
        elif i == 3:
            fr += [(a - 0.3, 0.3), (a + 0.2, 1.0)]
        else:
            fr += [(a - 0.3, 0.3), (a + 0.2, 1.0), (b - 0.3, 1.0), (b + 0.2, 0.3), (t_both[0] - 0.3, 0.3),
                   (t_both[0] + 0.3, 0.3)]
        fr += [(t_end[0], fr[-1][1]), (t_end[1], 0.0)]
        fr = sorted(fr, key=lambda z: z[0])
        cleaned = []
        for f in fr:
            if cleaned and f[0] <= cleaned[-1][0]:
                f = (cleaned[-1][0] + 1e-3, *f[1:])
            cleaned.append(f)
        lay = s.manim(z=5, opacity=keys(*cleaned, lead=0))
        lay.add(e, at=s.start)
        lay.play(e.animate.scale(sm[i].width / e.width).move_to(sm[i].get_center()), at=t_dock[0],
                 dur=t_dock[1] - t_dock[0], ease=E_)

    def headline(i, at, out):
        h = maxwell(size=60)[i].move_to([*HEAD, 0])
        m.play(FadeIn(h, shift=0.12 * DOWN), at=at, dur=0.7)
        m.play(FadeOut(h), at=out, dur=0.5)
        return h

    # ── div E: charges are sources and sinks ──
    pP, pM = SC + np.array([-2.0, 0.0]), SC + np.array([2.0, 0.0])
    headline(0, T.div_E + 0.1, T.div_B - 0.6)
    chg = VGroup(VGroup(Circle(radius=0.3, color=C.div, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1)
                        .move_to([*pP, 0]), tex("+", size=44, color=C.div).move_to([*pP, 0])),
                 VGroup(Circle(radius=0.3, color=C.sink, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1)
                        .move_to([*pM, 0]), tex("-", size=44, color=C.sink).move_to([*pM, 0])))
    elines, eheads = VGroup(), VGroup()
    for ln in dipole_lines(pP, pM, n=6):
        ln = ln[(np.linalg.norm(ln - pP, axis=1) > 0.32) & (np.linalg.norm(ln - pM, axis=1) > 0.32)]
        for r in runs(ln):
            elines.add(poly(r, C.efield, C.thin + 0.8, 0.85))
            if len(r) > 20:
                eheads.add(mid_head(r, C.efield, 0.5, tip=0.14, width=C.thin + 0.8))
    m.play(FadeIn(chg[0], scale=0.5), at=T.div_E + 0.6, dur=0.5, ease="out_back")
    m.play(FadeIn(chg[1], scale=0.5), at=T.div_E + 1.0, dur=0.5, ease="out_back")
    m.play(LaggedStart(*[Create(l) for l in elines], lag_ratio=0.05), at=T.charges, dur=2.0)
    m.play(LaggedStart(*[FadeIn(h) for h in eheads], lag_ratio=0.03), at=T.charges + 1.6, dur=0.8)
    m.play(Indicate(chg[0], scale_factor=1.25, color=C.div), at=T.charges + 0.9, dur=0.8)
    m.play(Indicate(chg[1], scale_factor=1.25, color=C.sink), at=T.charges + 2.2, dur=0.8)
    m.play(FadeOut(VGroup(chg, elines, eheads)), at=T.div_B - 0.6, dur=0.6)

    # ── div B: no sources; the lines only loop back ──
    MC = SC + np.array([0.0, 0.1])
    BL, BH = 0.7, 0.3                           # magnet half-length, half-height
    headline(1, T.div_B + 0.1, T.curl_E - 0.6)
    outside = lambda P: (np.abs(P[:, 0] - MC[0]) > BL) | (np.abs(P[:, 1] - MC[1]) > BH)

    def dipole_loop(Cc, side):
        """A field line of a magnetic dipole along +x, r = C sin^2(theta): outside from N (right) round to S (left),
        then straight back through the magnet. Returns the closed loop as one polyline."""
        th = np.linspace(0.02, np.pi - 0.02, 900)
        r = Cc * np.sin(th) ** 2
        P = MC + np.stack([r * np.cos(th), side * r * np.sin(th)], 1)
        P = P[outside(P)]
        inner = np.stack([np.linspace(P[-1, 0], P[0, 0], 40), np.linspace(P[-1, 1], P[0, 1], 40)], 1)
        return P, inner
    blines, bheads, binner = VGroup(), VGroup(), VGroup()
    loops = {}
    for Cc in (1.3, 1.9, 2.6):
        for side in (1, -1):
            P, inner = dipole_loop(Cc, side)
            loops[(Cc, side)] = np.vstack([P, inner])
            for r in runs(P):
                blines.add(poly(r, C.bfield, C.thin + 0.8, 0.85))
                if len(r) > 30:
                    fi = int(np.argmax(np.abs(r[:, 1] - MC[1])))
                    bheads.add(mid_head(r, C.bfield, fi / (len(r) - 1), tip=0.14, width=C.thin + 0.8))
            binner.add(DashedLine([*inner[0], 0], [*inner[-1], 0], color=C.bfield, stroke_width=C.thin,
                                  dash_length=0.06).set_stroke(opacity=0.7))
    bar = VGroup(Rectangle(width=2 * BL, height=2 * BH, stroke_color=C.frame, stroke_width=C.stroke)
                 .move_to([*MC, 0]),
                 tex("N", size=36, color=C.bfield).move_to([MC[0] + BL + 0.3, MC[1] - 0.05, 0]),
                 tex("S", size=36, color=C.muted).move_to([MC[0] - BL - 0.3, MC[1] - 0.05, 0]))
    m.play(FadeIn(bar, shift=0.2 * UP), at=T.div_B + 0.6, dur=0.6)
    m.play(LaggedStart(*[Create(l) for l in blines], lag_ratio=0.04), at=T.no_sources - 0.6, dur=2.2)
    m.play(FadeIn(binner), LaggedStart(*[FadeIn(h) for h in bheads], lag_ratio=0.03), at=T.never_end - 0.2, dur=0.8)
    tr = loops[(1.9, 1)]                        # one loop traced all the way round, through the magnet
    t_tr = (T.loop_back - 0.1, T.loop_back + 1.6)

    def tracer(t):
        u = ease(t, *t_tr)
        k = 1 - ramp(t, T.curl_E - 0.6, T.curl_E)
        j = max(2, int(u * (len(tr) - 1)))
        g = VGroup(poly(tr[:j], C.bfield, C.stroke + 1.5, k))
        g.add(Dot([*tr[j - 1], 0], radius=0.07, color=C.text).set_opacity(k))
        return g
    m.redraw(tracer, during=(t_tr[0], T.curl_E))
    m.play(FadeOut(VGroup(bar, blines, bheads, binner)), at=T.curl_E - 0.6, dur=0.6)

    # ── curl E: a growing B (out of the page) is wrapped by a clockwise E whirl ──
    headline(2, T.curl_E + 0.1, T.curl_B - 0.6)
    WC = SC
    rng = np.random.default_rng(31)
    spots = []
    while len(spots) < 22:
        p = rng.uniform(-1.3, 1.3, 2)
        if np.linalg.norm(p) < 1.25 and all(np.linalg.norm(p - q) > 0.42 for q in spots):
            spots.append(p)
    t_a = (T.curl_E + 0.8, T.magnet - 0.4)

    def whirl(t):
        k = ramp(t, t_a[0], t_a[0] + 0.6) * (1 - ramp(t, t_a[1], t_a[1] + 0.5))
        if k < 0.01:
            return VGroup()
        g = VGroup()
        grow = 0.35 + 0.65 * ease(t, t_a[0], T.stirs + 1.5)      # B is increasing
        for p in spots:
            g.add(odot(WC + p, 0.07 + 0.08 * grow, C.bfield, k))
        ke = ramp(t, T.stirs - 0.3, T.stirs + 0.6) * k
        if ke > 0.01:
            for R, nn in ((1.75, 10), (2.45, 14)):
                for j in range(nn):
                    a = 2 * np.pi * j / nn - 0.35 * (t - T.stirs) / R      # clockwise
                    p = WC + R * np.array([np.cos(a), np.sin(a)])
                    d = np.array([np.sin(a), -np.cos(a)])               # clockwise tangent
                    g.add(arrow(p - 0.2 * d, p + 0.2 * d, C.efield, width=C.stroke, tip=0.13, opacity=ke))
        return g
    m.redraw(whirl, during=(t_a[0], t_a[1] + 0.55))
    dB = tex(r"\frac{\partial \mathbf{B}}{\partial t}", size=44, color=C.bfield).move_to([*(WC + np.array([3.4, 1.4])), 0])
    m.play(FadeIn(dB, shift=0.1 * UP), at=T.curl_E + 2.2, dur=0.6)
    m.play(FadeOut(dB), at=t_a[1], dur=0.5)

    # the generator: a spinning magnet drives a current back and forth round a coil
    GM, GC = SC + np.array([-1.6, 0.35]), SC + np.array([1.2, 0.35])
    t_g = (T.magnet - 0.2, T.curl_B - 0.7)
    om = 2 * np.pi / 2.6
    cw, ch = 2.0, 1.5
    loop_pts = np.array([GC + np.array(p) for p in ((-cw / 2, -ch / 2), (cw / 2, -ch / 2), (cw / 2, ch / 2),
                                                    (-cw / 2, ch / 2))])
    per = 2 * (cw + ch)

    def on_loop(sv):
        sv = sv % per
        edges = [cw, ch, cw, ch]
        for i, L in enumerate(edges):
            if sv <= L:
                a, b = loop_pts[i], loop_pts[(i + 1) % 4]
                return a + (b - a) * sv / L
            sv -= L
        return loop_pts[0]

    def gen(t):
        k = ramp(t, t_g[0], t_g[0] + 0.6) * (1 - ramp(t, t_g[1], t_g[1] + 0.5))
        if k < 0.01:
            return VGroup()
        g = VGroup()
        tt = t - t_g[0]
        ang = om * tt
        mag = VGroup(Rectangle(width=1.0, height=0.4, stroke_width=0, fill_color=C.bfield, fill_opacity=0.85)
                     .move_to([0.5, 0, 0]),
                     Rectangle(width=1.0, height=0.4, stroke_width=0, fill_color=C.muted, fill_opacity=0.6)
                     .move_to([-0.5, 0, 0]),
                     Rectangle(width=2.0, height=0.4, stroke_color=C.frame, stroke_width=C.thin))
        mag.rotate(ang, about_point=ORIGIN).shift([*GM, 0])
        g.add(dim(mag, k))
        g.add(Dot([*GM, 0], radius=0.05, color=C.text).set_opacity(k))
        for j in range(3):                      # the coil: a few turns of wire
            off = 0.06 * (j - 1)
            g.add(Rectangle(width=cw + 2 * off, height=ch + 2 * off, stroke_color=C.muted, stroke_width=C.thin)
                  .move_to([*GC, 0]).set_stroke(opacity=k))
        # the current: charges displaced by (1 - cos) (current ~ sin), so they slosh back and forth
        disp = 1.1 * (1 - np.cos(ang))
        for j in range(14):
            p = on_loop(j * per / 14 + disp)
            g.add(Dot([*p, 0], radius=0.055, color=C.efield).set_opacity(k))
        # the current trace below the coil
        ox, oy, wd, hh = GC[0] - 1.6, GC[1] - 2.05, 3.2, 0.5
        g.add(Line([ox, oy, 0], [ox + wd, oy, 0], color=C.frame, stroke_width=C.thin).set_stroke(opacity=k))
        span = 6.0
        ts = np.linspace(max(0.0, tt - span), tt, 120)
        if tt > 0.05:
            pts = [[ox + wd * (x - max(0.0, tt - span)) / span, oy + hh * np.sin(om * x), 0] for x in ts]
            g.add(VMobject(stroke_color=C.efield, stroke_width=C.stroke, stroke_opacity=k).set_points_as_corners(pts))
        return g
    m.redraw(gen, during=(t_g[0], t_g[1] + 0.55))
    I_lab = tex(r"I", size=40, color=C.efield).move_to([GC[0] - 1.9, GC[1] - 2.05, 0])
    m.play(FadeIn(I_lab), at=T.electricity - 0.8, dur=0.5)
    m.play(FadeOut(I_lab), at=t_g[1], dur=0.5)

    # ── curl B: a current wraps itself in magnetic rings ──
    headline(3, T.curl_B + 0.1, T.together2 - 0.4)
    JC = SC
    wire = VGroup(odot(JC, 0.24, C.text), tex(r"\mathbf{J}", size=32, color=C.text).move_to([*(JC + np.array([0.0, -0.47])), 0]))
    m.play(FadeIn(wire, scale=0.6), at=T.curl_B + 0.8, dur=0.6, ease="out_back")
    rings = VGroup()
    for R in (0.75, 1.3, 1.85, 2.4):
        ring = Circle(radius=R, color=C.bfield, stroke_width=C.thin + 0.8).move_to([*JC, 0])
        heads = VGroup(*[arrow(JC + R * np.array([np.cos(a), np.sin(a)]) - 0.14 * np.array([-np.sin(a), np.cos(a)]),
                               JC + R * np.array([np.cos(a), np.sin(a)]) + 0.14 * np.array([-np.sin(a), np.cos(a)]),
                               C.bfield, width=C.thin + 0.8, tip=0.13)
                         for a in np.linspace(0.3 + R, 0.3 + R + 2 * np.pi, 4, endpoint=False)])
        rings.add(VGroup(ring, heads))
    m.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.3), at=T.wrap - 0.4, dur=2.0)
    m.play(FadeOut(VGroup(wire, rings)), at=T.together2 - 0.4, dur=0.5)

    # ── together: E makes B, B makes E; the pair travels on its own ──
    t_w = (T.together2 + 0.3, T.far - 0.3)
    v_w, kk, A_w = 1.6, 2 * np.pi / 1.6, 1.1
    proj = ortho(np.radians(-24), np.radians(16), scale=1.0, center=SC + np.array([0.0, -0.1]))
    x_lo, x_hi = -3.7, 4.6
    front = lambda t: -3.7 + v_w * max(0.0, t - t_w[0]) + 3.0 * max(0.0, t - T.light2) ** 2

    def wave(t):
        k = ramp(t, t_w[0], t_w[0] + 0.4) * (1 - ramp(t, T.far - 0.6, T.far - 0.2))
        if k < 0.01:
            return VGroup()
        g = VGroup()
        g.add(Line(proj([x_lo, 0, 0]), proj([x_hi, 0, 0]), color=C.frame, stroke_width=C.thin).set_stroke(opacity=0.6 * k))
        xf = front(t)
        xb = max(x_lo, xf - 7.5)
        if xf <= xb + 0.05:
            return g
        xs = np.linspace(xb, min(xf, x_hi + 3), 180)
        env = np.clip((xf - xs) / 0.6, 0, 1) * np.clip((xs - (xf - 7.5)) / 0.6, 0, 1)
        ph = kk * (xs - v_w * (t - t_w[0]))
        Ez = A_w * env * np.sin(ph)
        By = -A_w * env * np.sin(ph)
        inside = xs <= x_hi
        if inside.sum() > 2:
            g.add(VMobject(stroke_color=C.efield, stroke_width=C.stroke + 0.5, stroke_opacity=k)
                  .set_points_as_corners([proj([x, 0, z]) for x, z in zip(xs[inside], Ez[inside])]))
            g.add(VMobject(stroke_color=C.bfield, stroke_width=C.stroke + 0.5, stroke_opacity=k)
                  .set_points_as_corners([proj([x, y, 0]) for x, y in zip(xs[inside], By[inside])]))
            for x, z, y in list(zip(xs[inside], Ez[inside], By[inside]))[::6]:
                g.add(Line(proj([x, 0, 0]), proj([x, 0, z]), color=C.efield, stroke_width=C.thin * 0.7)
                      .set_stroke(opacity=0.5 * k))
                g.add(Line(proj([x, 0, 0]), proj([x, y, 0]), color=C.bfield, stroke_width=C.thin * 0.7)
                      .set_stroke(opacity=0.5 * k))
        return g
    m.redraw(wave, during=(t_w[0], T.far - 0.15))
    lab_E = tex(r"\mathbf{E}", size=44, color=C.efield).move_to(proj([-2.6, 0, 1.55]))
    lab_B = tex(r"\mathbf{B}", size=44, color=C.bfield).move_to(proj([-2.3, -1.6, 0]) + np.array([0, -0.2, 0]))
    m.play(FadeIn(lab_E), FadeIn(lab_B), at=T.together2 + 1.6, dur=0.6)
    m.play(FadeOut(VGroup(lab_E, lab_B)), at=T.light2 - 0.2, dur=0.5)

    # ── water: zero divergence (flow round a post) ──
    WC2 = SC + np.array([0.3, 0.0])
    Rp, U = 0.75, 0.9
    t_wt = (T.far + 0.2, T.hurricane - 0.5)

    def v_post(P):
        x, y = P[:, 0], P[:, 1]
        r2 = np.maximum(x * x + y * y, Rp * Rp * 1.0001)
        return U * np.stack([1 - Rp * Rp * (x * x - y * y) / r2 ** 2, -2 * Rp * Rp * x * y / r2 ** 2], 1)

    def wrap_post(P):
        P = P.copy()
        out = P[:, 0] > 4.0
        P[out, 0] -= 8.0
        return P
    g_rng = np.random.default_rng(41)
    p0 = g_rng.uniform([-4.0, -2.4], [4.0, 2.4], (700, 2))
    p0 = p0[np.hypot(p0[:, 0], p0[:, 1]) > Rp + 0.03]
    wpos = advect_grains(v_post, p0, t_wt[0], t_wt[1] + 0.6, respawn=wrap_post)

    def water_local(t):
        P = wpos(t)
        a = np.clip((3.9 - np.abs(P[:, 0])) / 0.5, 0, 1) * (np.abs(P[:, 1]) < 2.35)
        return P, a.astype(np.float32)
    k_wt = keys((s.start, 0.0), (t_wt[0], 0.0), (t_wt[0] + 0.6, 1.0), (t_wt[1], 1.0), (t_wt[1] + 0.5, 0.0), lead=0)
    s.add(cast_layer(water_local, tuple(WC2), 1.0, opacity=k_wt, z=3, size=2.4))
    post = Circle(radius=Rp, color=C.frame, stroke_width=C.stroke, fill_color=C.bg, fill_opacity=1).move_to([*WC2, 0])
    sx = np.linspace(-4.0, 4.0, 300)
    stream = VGroup()
    for y0 in np.linspace(-2.2, 2.2, 9):
        # streamlines: psi = U y (1 - R^2 / r^2) = const, solved for y on each x by bisection-free sampling
        pts = []
        for x in sx:
            ys_ = np.linspace(-2.6, 2.6, 2001)
            r2 = np.maximum(x * x + ys_ * ys_, 1e-9)
            psi = ys_ * (1 - Rp * Rp / r2)
            psi[r2 < Rp * Rp] = np.nan
            j = np.nanargmin(np.abs(psi - y0 * (1 - Rp * Rp / (16 + y0 * y0))))
            pts.append([x, ys_[j]])
        pts = np.array(pts) + WC2
        if abs(y0) > 0.05:
            stream.add(poly(pts, C.field, C.thin, 0.4))
    stream.add(poly(np.stack([sx[sx < -Rp], 0 * sx[sx < -Rp]], 1) + WC2, C.field, C.thin, 0.4))
    stream.add(poly(np.stack([sx[sx > Rp], 0 * sx[sx > Rp]], 1) + WC2, C.field, C.thin, 0.4))
    m.play(FadeIn(stream), FadeIn(post), at=t_wt[0], dur=0.6)
    div_v = tex(r"\nabla\cdot", r"\mathbf{v}", "=", "0", size=60, colors={0: C.div, 1: C.field}).move_to([*HEAD, 0])
    m.play(FadeIn(div_v, shift=0.12 * DOWN), at=T.water + 0.4, dur=0.7)
    m.play(FadeOut(VGroup(stream, post, div_v)), at=t_wt[1], dur=0.5)

    # ── a hurricane: a giant patch of curl ──
    HC = SC + np.array([0.3, -0.1])
    Gm, a_h, k_in = 1.4, 0.7, 0.08
    t_h = (T.hurricane - 0.3, T.cut_outro - 0.5)

    def v_hur(P):
        x, y = P[:, 0], P[:, 1]
        r2 = x * x + y * y
        f = Gm / (r2 + a_h * a_h)
        return np.stack([-f * y - k_in * x, f * x - k_in * y], 1)

    def respawn_hur(P):
        P = P.copy()
        r = np.hypot(P[:, 0], P[:, 1])
        bad = r < 0.25
        th = np.arctan2(P[bad, 1], P[bad, 0])
        P[bad] = 2.9 * np.stack([np.cos(th + 2.0), np.sin(th + 2.0)], 1)
        return P
    rr = np.sqrt(g_rng.uniform(0.3 ** 2, 2.9 ** 2, 800))
    th0 = g_rng.uniform(0, 2 * np.pi, 800)
    hpos = advect_grains(v_hur, np.stack([rr * np.cos(th0), rr * np.sin(th0)], 1), t_h[0], t_h[1] + 0.6,
                         respawn=respawn_hur)

    def hur_local(t):
        P = hpos(t)
        r = np.hypot(P[:, 0], P[:, 1])
        return P, np.clip((3.0 - r) / 0.5, 0, 1).astype(np.float32)
    k_h = keys((s.start, 0.0), (t_h[0], 0.0), (t_h[0] + 0.6, 1.0), (t_h[1], 1.0), (t_h[1] + 0.5, 0.0), lead=0)
    s.add(cast_layer(hur_local, tuple(HC), 1.0, opacity=k_h, z=3, size=2.4))
    FULL, RES = (14.4, 8.2), (320, 180)
    xs = np.linspace(-FULL[0] / 2, FULL[0] / 2, RES[0]) - HC[0]
    ys = np.linspace(-FULL[1] / 2, FULL[1] / 2, RES[1]) - HC[1]
    X, Y = np.meshgrid(xs, ys)
    R2 = X * X + Y * Y
    curl_h = 2 * Gm * a_h * a_h / (R2 + a_h * a_h) ** 2       # curl of the swirl (the inflow part has none)
    curl_h = curl_h * np.clip((3.1 - np.sqrt(R2)) / 0.4, 0, 1)
    k_hm = keys((s.start, 0.0), (T.patch - 0.6, 0.0), (T.patch + 0.6, 0.6, E_), (t_h[1], 0.6), (t_h[1] + 0.5, 0.0),
                lead=0)
    s.add(FieldLayer(lambda t: curl_h, cmap="diverging", vmin=-6.0, vmax=6.0, extent=FULL,
                     colors=(C.cw, C.bg, C.curl), animated=False, z=-20, opacity=k_hm))
    curl_v = tex(r"\nabla\times", r"\mathbf{v}", size=60, colors={0: C.curl, 1: C.field}).move_to([*HEAD, 0])
    m.play(FadeIn(curl_v, shift=0.12 * DOWN), at=T.patch - 0.2, dur=0.7)
    m.play(FadeOut(curl_v), at=t_h[1], dur=0.5)
