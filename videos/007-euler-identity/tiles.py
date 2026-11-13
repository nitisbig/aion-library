"""The intro's chapter-preview grid (s00b): six framed tiles, one key picture per chapter, each a pure function of t
drawn inside its own box from the real maths. Tile 6 is the hero shot itself (drawn by the scene), tile 2 is the 3D
plane (plane3d.frag clipped to its box). Boxes are (x0, y0, x1, y1) in world units.
"""
from aion import *

from shots import CHAPTERS, arrow, ease, ramp, rail_ticks, right_angle, words
from shots3d import F0, Cam3

TW, TH = 4.15, 2.5
TILES = [(cx - TW / 2, cy - TH / 2, cx + TW / 2, cy + TH / 2)
         for cy in (0.95, -1.75) for cx in (-4.45, 0.0, 4.45)]
STRIP = 0.46                                        # the label strip along each tile's top


def inner(box, pad=0.16):
    """The picture area of a tile: inside the frame, below the label strip."""
    x0, y0, x1, y1 = box
    return (x0 + pad, y0 + pad, x1 - pad, y1 - STRIP)


def mid(box):
    return np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2, 0.0])


def frame_rect(box, color, k=1.0, width=None):
    x0, y0, x1, y1 = box
    return Polygon([x0, y0, 0], [x1, y0, 0], [x1, y1, 0], [x0, y1, 0], stroke_color=color,
                   stroke_width=width or C.thin, stroke_opacity=k, fill_opacity=0)


def label(k, box):
    """'k  Title' in Computer Modern at the tile's top-left."""
    g = VGroup(words(str(k), size=26, color=C.text), words(CHAPTERS[k - 1], size=26, color=C.muted))
    g.arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
    return g.move_to([box[0] + 0.16, box[3] - 0.13, 0], aligned_edge=UL)


def tick_box(k):
    """Rail tick k (1..6) as a flat box: where tile k lands in the collapse."""
    tk = rail_ticks(0)[k - 1]
    a, b = tk.get_start(), tk.get_end()
    return (a[0], a[1], b[0], b[1])


def lerp_box(a, b, u):
    return tuple((1 - u) * p + u * q for p, q in zip(a, b))


# ── tile 1 · What e really is: compounding staircases settle onto the curve e^t, under a ceiling e ──
NS1 = (1, 2, 4, 12)


def tile1(t, box, t0, k=1.0, coin_at=None):
    x0, y0, x1, y1 = inner(box)
    ox, oy = x0 + 0.55, y0 + 0.08
    ux, uy = (x1 - 0.55 - ox), (y1 - 0.1 - oy) / 2.9

    def pt(tt, y):
        return np.array([ox + ux * tt, oy + uy * y, 0.0])
    g = VGroup(Line(pt(0, 0), pt(1.08, 0), color=C.axis, stroke_width=C.thin, stroke_opacity=k),
               Line(pt(0, 0), pt(0, 2.95), color=C.axis, stroke_width=C.thin, stroke_opacity=k))
    ke = ramp(t, t0 + 0.2, t0 + 0.8) * k
    g.add(DashedLine(pt(0, np.e), pt(1.04, np.e), color=C.growth, stroke_width=C.thin, dash_length=0.07)
          .set_opacity(0.8 * ke))
    g.add(MathTex("e", font_size=30, color=C.growth).next_to(pt(1.04, np.e), RIGHT, buff=0.08).set_opacity(ke))
    for j, n in enumerate(NS1):
        a = t0 + 0.4 + 0.8 * j
        u = ease(t, a, a + 0.7)
        if u <= 0:
            continue
        ghost = ramp(t, a + 0.8, a + 1.2)
        pts, level = [pt(0, 1.0)], 1.0
        for i in range(1, n + 1):
            tk = i / n
            if u < tk:
                pts.append(pt(u, level))
                break
            pts.append(pt(tk, level))
            level *= 1 + 1 / n
            pts.append(pt(tk, level))
        g.add(VMobject(stroke_color=C.growth, stroke_width=C.stroke - 1.6 * ghost,
                       stroke_opacity=k * (1 - 0.7 * ghost)).set_points_as_corners(pts))
    uc = ease(t, t0 + 3.8, t0 + 4.9)
    if uc > 0:
        ts = np.linspace(0, uc, 60)
        g.add(VMobject(stroke_color=C.growth, stroke_width=C.stroke + 1, stroke_opacity=k)
              .set_points_smoothly([pt(x, np.exp(x)) for x in ts]))
        g.add(Dot(pt(uc, np.exp(uc)), radius=0.05, color=C.growth).set_opacity(k))
    if coin_at is not None:                           # "one dollar": a gold dot drops onto the start, $1
        kc = ramp(t, coin_at, coin_at + 0.4) * k
        if kc > 0.01:
            drop = 0.6 * (1 - ease(t, coin_at, coin_at + 0.5))
            g.add(Dot(pt(0, 1.0) + [0, drop, 0], radius=0.08, color=C.growth).set_opacity(kc))
            g.add(MathTex(r"\$1", font_size=28, color=C.growth).next_to(pt(0, 1.0), LEFT, buff=0.1)
                  .shift([0, drop, 0]).set_opacity(kc))
    return g


# ── tile 2 · What i really does: the 3D plane, a floating arrow turning by quarter turns ──
def tile2_cam(box, t0):
    c = mid(inner(box))
    return Cam3(yaw=lambda t: np.radians(-24) + 0.11 * (t - t0), pitch=np.radians(48), dist=F0 / 0.62,
                tx=0.0, ty=0.25, sx=c[0], sy=c[1] - 0.05, fog=5.0)


def tile2_phi(t, t0):
    """Quarter turns, one every 1.4 s, each eased."""
    u = max(0.0, (t - t0 - 0.6) / 1.4)
    n, f = np.floor(u), u - np.floor(u)
    return (PI / 2) * (n + ease(f, 0.0, 0.6))


def tile2(t, cam, t0, k=1.0):
    v = cam(t)
    g = VGroup()
    if k < 0.01:
        return g
    g.add(v.flat(Circle(radius=1.0, color=C.text, stroke_width=C.thin).set_stroke(opacity=0.45 * k)))
    f = tile2_phi(t, t0)
    lap = f - TAU * np.floor(f / TAU)
    if lap > 0.05:
        arc = Arc(radius=1.0, start_angle=0, angle=lap, color=C.turn, stroke_width=C.stroke, stroke_opacity=k)
        g.add(v.lift(arc, h=0.04, shadow=0.5 * k))
    a = arrow(ORIGIN, [np.cos(f), np.sin(f), 0], C.point, tip=0.2).set_opacity(k)
    g.add(v.lift(a, h=0.08, shadow=0.55 * k))
    for txt, col, ang in (("1", C.text, 0), ("i", C.turn, PI / 2), ("-1", C.point, PI), ("-i", C.turn, 1.5 * PI)):
        g.add(v.bill(MathTex(txt, font_size=26, color=col).set_opacity(k), (1.45 * np.cos(ang), 1.45 * np.sin(ang)),
                     h=0.2, lo=0.8))
    return g


# ── tile 3 · Growth turned sideways: x on the circle, v = ix at a right angle, the field circling ──
_R3 = np.random.default_rng(7)
STREAKS = [(r, a) for r, a in zip(_R3.uniform(0.18, 0.95, 46), _R3.uniform(0, TAU, 46))]


def tile3(t, box, t0, k=1.0):
    c = mid(inner(box))
    R, w = 0.6, 1.1
    th = w * max(0.0, t - t0)
    g = VGroup()
    x0, y0, x1, y1 = inner(box)
    for r, a in STREAKS:                              # the circling field, turning at the same rate
        if c[1] - r < y0 or c[1] + r > y1:
            continue
        g.add(Arc(radius=r, start_angle=a + th, angle=0.55, arc_center=c, color=C.turn,
                  stroke_width=C.thin, stroke_opacity=0.32 * k))
    g.add(Circle(radius=R, color=C.text, stroke_width=C.thin).move_to(c).set_stroke(opacity=0.5 * k))
    p = c + R * np.array([np.cos(th), np.sin(th), 0])
    d = np.array([-np.sin(th), np.cos(th), 0])
    g.add(arrow(c, p, C.point, tip=0.16).set_opacity(k))
    g.add(arrow(p, p + R * d, C.vel, tip=0.16).set_opacity(k))
    g.add(right_angle(p, -(p - c) / R, d, size=0.11, color=C.text, k=k))
    g.add(Dot(p, radius=0.06, color=C.point).set_opacity(k))
    lab = MathTex(r"v=ix", font_size=30, color=C.text)
    lab[0][0].set_color(C.vel)
    lab[0][2].set_color(C.turn)
    lab[0][3].set_color(C.point)
    g.add(lab.move_to([x1 - 0.45, y0 + 0.2, 0]).set_opacity(k))
    return g


# ── tile 4 · Compounding a turn: (1 + iπ/n)^k, tip to tail, closing in on −1 ──
NS4 = (4, 8, 16, 64)
CH4 = {n: (1 + 1j * PI / n) ** np.arange(n + 1) for n in NS4}
_all4 = np.concatenate([*CH4.values(), np.exp(1j * np.linspace(0, TAU, 64))])
B4 = (_all4.real.min(), _all4.imag.min(), _all4.real.max(), _all4.imag.max())


def tile4(t, box, t0, k=1.0):
    x0, y0, x1, y1 = inner(box)
    s = min((x1 - x0 - 0.2) / (B4[2] - B4[0]), (y1 - y0 - 0.1) / (B4[3] - B4[1]))
    o = np.array([(x0 + x1) / 2 - s * (B4[0] + B4[2]) / 2, (y0 + y1) / 2 - s * (B4[1] + B4[3]) / 2, 0.0])

    def W(z):
        return o + s * np.array([z.real, z.imag, 0.0])
    g = VGroup(Circle(radius=s, color=C.ghost, stroke_width=C.thin + 0.4).move_to(o).set_stroke(opacity=k),
               Line(W(B4[0] - 0.1), W(B4[2] + 0.1), color=C.ghost, stroke_width=C.thin, stroke_opacity=k))
    g.add(Dot(W(-1), radius=0.05, color=C.point).set_opacity(0.8 * k))
    per = 1.6
    j = int(np.clip((t - t0 - 0.3) // per, 0, len(NS4) - 1))
    n = NS4[j]
    a = t0 + 0.3 + per * j
    u = ease(t, a, a + 1.0) if j < len(NS4) - 1 or t < a + 1.0 else 1.0
    zs = CH4[n]
    m_ = max(1, int(np.ceil(u * n)))
    pts = [W(z) for z in zs[:m_ + 1]]
    g.add(VMobject(stroke_color=C.point, stroke_width=C.stroke - (1.0 if n > 8 else 0), stroke_opacity=k)
          .set_points_as_corners(pts))
    if n <= 8:
        for i in range(min(m_, n)):
            d1 = -(zs[i]) / abs(zs[i])
            d2 = (zs[i + 1] - zs[i]) / abs(zs[i + 1] - zs[i])
            g.add(right_angle(W(zs[i]), (d1.real, d1.imag), (d2.real, d2.imag), size=0.08, color=C.turn, k=0.8 * k))
    g.add(Dot(pts[-1], radius=0.06, color=C.point).set_opacity(k))
    lab = MathTex(rf"n={n}", font_size=28, color=C.muted).move_to([x1 - 0.5, y0 + 0.18, 0]).set_opacity(k)
    g.add(lab)
    return g


# ── tile 5 · The infinite sum: (iπ)^n / n!, tip to tail, spiralling onto −1 ──
TERMS5 = np.array([(1j * PI) ** n / np.prod(np.arange(1, n + 1)) for n in range(14)])
SUM5 = np.concatenate([[0], np.cumsum(TERMS5)])
B5 = (SUM5.real.min(), SUM5.imag.min(), SUM5.real.max(), SUM5.imag.max())


def tile5(t, box, t0, k=1.0):
    x0, y0, x1, y1 = inner(box)
    s = min((x1 - x0 - 0.3) / (B5[2] - B5[0]), (y1 - y0 - 0.1) / (B5[3] - B5[1]))
    o = np.array([(x0 + x1) / 2 - s * (B5[0] + B5[2]) / 2, (y0 + y1) / 2 - s * (B5[1] + B5[3]) / 2, 0.0])

    def W(z):
        return o + s * np.array([z.real, z.imag, 0.0])
    g = VGroup(Line(W(B5[0] - 0.2), W(B5[2] + 0.2), color=C.ghost, stroke_width=C.thin, stroke_opacity=k),
               Line(W(complex(0, B5[1] - 0.1)), W(complex(0, B5[3] + 0.1)), color=C.ghost, stroke_width=C.thin,
                    stroke_opacity=k))
    g.add(Dot(W(-1), radius=0.06, color=C.point).set_opacity(k))
    for n in range(len(TERMS5)):
        u = ease(t, t0 + 0.3 + 0.42 * n, t0 + 0.3 + 0.42 * n + 0.4)
        if u <= 0:
            break
        a, b = W(SUM5[n]), W(SUM5[n] + u * TERMS5[n])
        if np.linalg.norm(b - a) < 0.02:
            continue
        col = C.cos if n % 2 == 0 else C.sin
        g.add(arrow(a, b, col, width=C.stroke - 1, tip=0.13).set_opacity(k))
    return g
