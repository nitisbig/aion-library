"""in_s03 · Math at work. The camera slides the dim map to the left; four glimpses grow out of their corners of the
map, about four seconds each, every value computed: satellite circles meeting at the phone (geometry), a spam
boundary fitted by logistic regression (probability, linear algebra), powers of 3 mod 17 hopping round a dial
(number theory), a Hohmann transfer timed by Kepler's equation (calculus).
"""
import math

import numpy as np
from aion import *

from beats import T
from kit import map_deco, HUB_R, P3, PILLARS, dim, hue, map_lines, node_xy, sans, tex, the_circle, tint, window

CAM_C, CAM_Z = (3.6, 0.0), 0.8               # map on the left, glimpses on the right
VC = np.array([3.35, 0.0, 0.0])               # glimpse area centre (screen units), about 6 x 6.4
TAG_AT = np.array([0.55, -3.05, 0.0])


def screen(p):
    """Screen position of world point p under the scene's camera (centre CAM_C, zoom CAM_Z)."""
    return P3((p[0] - CAM_C[0]) * CAM_Z, (p[1] - CAM_C[1]) * CAM_Z)


def tags(*pairs):
    g = VGroup(*(sans(w, 30, hue(p)) for w, p in pairs)).arrange(RIGHT, buff=0.35)
    return g.move_to(TAG_AT, aligned_edge=LEFT)


def placed(g, t, t_in, t_out, origin):
    """Grow g out of `origin` (its node) after t_in, shrink it back into it before t_out."""
    a = min(float(smoothstep_((t - t_in + 0.15) / 0.5)), float(smoothstep_((t_out - t) / 0.45)))
    if a <= 0:
        return VGroup()
    g.scale(0.06 + 0.94 * a, about_point=VC).shift((1 - a) * (origin - VC))
    return dim(g, a ** 0.5)


def smoothstep_(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease(t, t0, d):
    return smoothstep_((t - t0) / d)


# --------------------------------------------------------------------------------------------- glimpses
RG = 1.7                                       # globe radius (screen units)
GC = VC + P3(0.0, -0.1)
S_ALT = 1.62 * RG                              # satellites' distance from the centre
TILT = 0.25


def body(lat, lon):
    return np.array([math.cos(lat) * math.sin(lon), math.sin(lat), math.cos(lat) * math.cos(lon)])


REC = body(0.45, 0.0)                          # the phone
SATS = [S_ALT * body(0.45 + 0.8, -0.45), S_ALT * body(0.45 - 0.2, 0.95), S_ALT * body(0.45 - 0.62, -0.85)]


def view(yaw):
    cy, sy, ct, st = math.cos(yaw), math.sin(yaw), math.cos(TILT), math.sin(TILT)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, ct, -st], [0, st, ct]])
    return Rx @ Ry


def strokes(P, color, width, front_op, back_op, R=RG):
    """Polyline of body points P (n, 3) on the globe, projected; front runs bright, back runs faint."""
    g = VGroup()
    vis = P[:, 2] >= 0
    edges = np.flatnonzero(np.diff(vis.astype(int))) + 1
    for run in np.split(np.arange(len(P)), edges):
        if len(run) < 2:
            continue
        pts = [GC + P3(*(R * P[i, :2])) for i in run]
        op = front_op if vis[run[0]] else back_op
        if op > 0:
            g.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=op).set_points_as_corners(pts))
    return g


def small_circle(axis, alpha, n=120):
    axis = axis / np.linalg.norm(axis)
    e1 = np.cross(axis, [0.0, 1.0, 0.3])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    th = np.linspace(0, 2 * np.pi, n)
    return math.cos(alpha) * axis + math.sin(alpha) * (np.outer(np.cos(th), e1) + np.outer(np.sin(th), e2))


def gps(t, t0):
    """A slowly turning globe. Around each satellite, the points of the Earth at one distance form a circle on the
    surface; as the measured distance grows to the true one, the three circles close in and meet at the phone."""
    M = view(-0.35 + 0.12 * (t - t0))
    g = VGroup(Circle(radius=RG, stroke_color=C.muted, stroke_width=2.2).move_to(GC))
    th = np.linspace(0, 2 * np.pi, 140)
    for lat in np.radians([-60, -30, 0, 30, 60]):              # parallels
        P = np.c_[np.cos(lat) * np.sin(th), np.full_like(th, np.sin(lat)), np.cos(lat) * np.cos(th)] @ M.T
        g.add(strokes(P, C.map_off, 1.2, 0.9, 0.22))
    ph = np.linspace(-np.pi / 2, np.pi / 2, 80)
    for lon in np.radians(np.arange(0, 180, 30)):              # meridians (full great circles)
        for sgn in (1, -1):
            P = np.c_[np.cos(ph) * np.sin(lon) * sgn, np.sin(ph), np.cos(ph) * np.cos(lon) * sgn] @ M.T
            g.add(strokes(P, C.map_off, 1.2, 0.9, 0.22))
    rec = M @ REC
    for k, sb in enumerate(SATS):
        sv = M @ sb
        S = np.linalg.norm(sb)
        d_true = np.linalg.norm(sb - RG * REC)
        rho = (S - RG) + (d_true - (S - RG)) * ease(t, t0 + 0.25 + 0.2 * k, 1.7)
        ca = (S * S + RG * RG - rho * rho) / (2 * S * RG)
        if rho > S - RG + 1e-3:
            P = small_circle(sb, math.acos(max(-1.0, min(1.0, ca)))) @ M.T
            g.add(strokes(P, C.space, 2.6, 1.0, 0.25))
        sp = GC + P3(*sv[:2])
        hidden = sv[2] < 0 and np.hypot(*sv[:2]) < RG
        op = 0.3 if hidden else 1.0
        u = sv[:2] / max(np.linalg.norm(sv[:2]), 1e-6)
        perp = P3(-u[1], u[0])
        g.add(Line(sp - 0.2 * perp, sp + 0.2 * perp, stroke_color=C.text, stroke_width=3.2, stroke_opacity=op),
              Square(0.11, stroke_color=C.text, stroke_width=1.6, fill_color=C.bg, fill_opacity=1,
                     stroke_opacity=op).move_to(sp))
        hit = ease(t, t0 + 2.2, 0.3)
        if hit > 0 and rec[2] > 0:
            g.add(DashedLine(sp, GC + P3(*(RG * rec[:2])), stroke_color=C.space, stroke_width=1.4,
                             stroke_opacity=0.55 * hit, dash_length=0.07))
    hit = ease(t, t0 + 2.2, 0.3)
    if hit > 0:
        rx = GC + P3(*(RG * rec[:2]))
        g.add(Dot(rx, radius=0.09 * hit, color=C.space),
              Circle(radius=0.12 + 0.35 * hit, stroke_color=C.space, stroke_width=2,
                     stroke_opacity=0.6 * (1 - hit) + 0.2).move_to(rx))
    g.add(tags(("geometry", "space")))
    return g


_rg = np.random.default_rng(17)
HAM = _rg.normal((2.3, 1.0), 0.55, (18, 2))
SPAM = _rg.normal((4.45, -0.95), 0.55, (18, 2))


def logistic_fit(lam=1.0):
    """L2-regularised logistic regression by Newton's method: P(spam) = σ(w·(x, y) + b)."""
    X = np.c_[np.vstack([HAM, SPAM]), np.ones(36)]
    y = np.r_[np.zeros(18), np.ones(18)]
    w = np.zeros(3)
    for _ in range(30):
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (p - y) + lam * np.r_[w[:2], 0]
        H = X.T @ (X * (p * (1 - p))[:, None]) + lam * np.diag([1, 1, 0])
        w -= np.linalg.solve(H, g)
    return w


W = logistic_fit()
BOX = (0.65, -2.6, 6.15, 2.75)


def clip_halfplane(w, level):
    """Polygon of {σ(w·x) ≥ level} inside BOX (Sutherland–Hodgman on the box)."""
    c = math.log(level / (1 - level))
    x0, y0, x1, y1 = BOX
    poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    f = lambda q: w[0] * (q[0] + VC[0] - VC[0]) + w[1] * q[1] + w[2] - c  # noqa: E731
    out = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            s_ = fa / (fa - fb)
            out.append((a[0] + s_ * (b[0] - a[0]), a[1] + s_ * (b[1] - a[1])))
    return [P3(*q) for q in out]


def line_in_box(p, d):
    x0, y0, x1, y1 = BOX
    ts = []
    for k, (lo, hi) in enumerate(((x0, x1), (y0, y1))):
        if abs(d[k]) > 1e-9:
            ts += [(lo - p[k]) / d[k], (hi - p[k]) / d[k]]
    pts = [p + tt * d for tt in ts]
    pts = [q for q in pts if x0 - 1e-6 <= q[0] <= x1 + 1e-6 and y0 - 1e-6 <= q[1] <= y1 + 1e-6]
    pts.sort(key=lambda q: q[0])
    return pts[0], pts[-1]


def envelope(q, col):
    c = P3(*q)
    w, h = 0.2, 0.14
    return VGroup(Rectangle(width=w, height=h, stroke_color=col, stroke_width=1.6, fill_color=C.bg, fill_opacity=1)
                  .move_to(c),
                  VMobject(stroke_color=col, stroke_width=1.3).set_points_as_corners(
                      [c + P3(-w / 2, h / 2), c + P3(0, -0.01), c + P3(w / 2, h / 2)]))


def p_spam_field(n=160):
    """P(spam) = σ(w·(x, y) + b) on a grid over BOX, rows bottom to top."""
    x0, y0, x1, y1 = BOX
    X, Y = np.meshgrid(np.linspace(x0, x1, n), np.linspace(y0, y1, n))
    return (1 / (1 + np.exp(-(W[0] * X + W[1] * Y + W[2])))).astype(np.float32)


def spam(t, t0):
    g = VGroup()
    for q in HAM:
        g.add(envelope(q, C.text))
    for q in SPAM:
        g.add(envelope(q, C.uncertainty))
    # the boundary w·x + b = 0 sweeps in from a wrong angle onto the fitted one
    n = W[:2] / np.linalg.norm(W[:2])
    centre = np.vstack([HAM, SPAM]).mean(0)
    p0 = centre - n * (W[:2] @ centre + W[2]) / np.linalg.norm(W[:2])
    a = math.atan2(-n[0], n[1]) + 1.1 * (1 - ease(t, t0 + 0.4, 1.2))
    d = np.array([math.cos(a), math.sin(a)])
    lw = ease(t, t0 + 0.2, 0.4)
    if lw > 0:
        u, v = line_in_box(p0, d)
        g.add(Line(P3(*u), P3(*v), stroke_color=C.structure, stroke_width=3.2, stroke_opacity=lw))
    g.add(tags(("probability", "uncertainty"), ("linear algebra", "structure")))
    return g


DIAL_C, DIAL_R = VC + P3(0.0, -0.25), 1.95
POW = [pow(3, k, 17) for k in range(16)]


def dial_xy(r, rad=DIAL_R):
    q = math.pi / 2 - 2 * math.pi * r / 17
    return DIAL_C + rad * np.array([math.cos(q), math.sin(q), 0])


def mod_dial(t, t0, nums):
    g = VGroup(Circle(radius=DIAL_R, stroke_color=C.muted, stroke_width=2).move_to(DIAL_C))
    for r in range(17):
        g.add(Line(dial_xy(r, DIAL_R - 0.12), dial_xy(r, DIAL_R), stroke_color=C.muted, stroke_width=2))
        g.add(nums[r].copy().move_to(dial_xy(r, DIAL_R - 0.36)))
    k_now = (t - t0 - 0.5) / 0.32                          # one hop every 0.32 s
    for k in range(min(int(max(k_now, 0)), 15)):
        g.add(Line(dial_xy(POW[k], DIAL_R - 0.6), dial_xy(POW[k + 1], DIAL_R - 0.6), stroke_color=C.quantity,
                   stroke_width=2.2, stroke_opacity=0.5))
    if k_now >= 0:
        k = min(int(k_now), 15)
        f = smoothstep_(k_now - int(k_now)) if k < 15 else 0.0
        a, b = dial_xy(POW[k], DIAL_R - 0.6), dial_xy(POW[min(k + 1, 15)], DIAL_R - 0.6)
        if k < 15 and f > 0:
            g.add(Line(a, a + f * (b - a), stroke_color=C.quantity, stroke_width=2.6))
        g.add(Dot(a + f * (b - a), radius=0.09, color=C.quantity))
    seen = {POW[j] for j in range(min(int(max(k_now, -1)) + 1, 16))} if k_now >= 0 else set()
    for r in seen:
        g.add(Circle(radius=0.2, stroke_color=C.quantity, stroke_width=1.8).move_to(dial_xy(r, DIAL_R - 0.36)))
    g.add(tex(r"3^k \bmod 17", 40, C.quantity).move_to(DIAL_C + P3(0, DIAL_R + 0.55)))
    if k_now >= 0:
        kk = min(int(k_now), 15)
        g.add(tex(rf"3^{{{kk}}} \equiv {POW[kk]}", 30, C.quantity).move_to(DIAL_C + P3(0, -DIAL_R - 0.42)))
    g.add(tags(("number theory", "quantity")))
    return g


SUN = VC + P3(0.2, 0.15)
R1, R2 = 1.15, 1.15 * 1.524                                # Earth and Mars orbit radii (to scale)
A_, E_ = (R1 + R2) / 2, (R2 - R1) / (R2 + R1)


def kepler_E(M):
    E = M
    for _ in range(12):
        E -= (E - E_ * math.sin(E) - M) / (1 - E_ * math.cos(E))
    return E


def craft(M):
    """Position and velocity on the transfer ellipse at mean anomaly M (perihelion on the left, moving counter-clockwise)."""
    E = kepler_E(M)
    b = A_ * math.sqrt(1 - E_ * E_)
    x, y = A_ * (math.cos(E) - E_), b * math.sin(E)
    vx, vy = -A_ * math.sin(E), b * math.cos(E)              # d/dE; speed from vis-viva below
    r = math.hypot(x, y)
    v = math.sqrt(2 / r - 1 / A_)
    d = np.array([-vx, -vy]) / math.hypot(vx, vy)
    return SUN + P3(-x, -y), v * d


_sr = np.random.default_rng(1504)
STARS = [(VC + P3(*_sr.uniform([-2.9, -2.6], [2.9, 3.0])), _sr.uniform(0.008, 0.024), _sr.uniform(0.25, 0.9))
         for _ in range(150)]


def orbit(t, t0):
    g = VGroup(*(Dot(p, radius=r, color=C.muted, fill_opacity=o) for p, r, o in STARS))
    g.add(Circle(radius=R1, stroke_color=C.map_off, stroke_width=1.8).move_to(SUN),
               Circle(radius=R2, stroke_color=C.map_off, stroke_width=1.8).move_to(SUN),
               Dot(SUN, radius=0.12, color=C.text))
    D = 2.6                                                  # transfer, compressed to 2.6 s
    t_dep = t0 + 0.6
    f = min(max((t - t_dep) / D, 0.0), 1.0)
    nE, nM, ne = (A_ / R1) ** 1.5 * math.pi / D, (A_ / R2) ** 1.5 * math.pi / D, math.pi / D
    tt = min(max(t - t_dep, 0.0), D)
    earth = SUN + R1 * P3(math.cos(math.pi + nE * (t - t_dep)), math.sin(math.pi + nE * (t - t_dep)))
    mars = SUN + R2 * P3(math.cos(nM * (t - t_dep - D)), math.sin(nM * (t - t_dep - D)))
    g.add(Dot(earth, radius=0.07, color=C.text), Dot(mars, radius=0.08, color=C.text))
    g.add(sans("Earth", 22, C.muted).next_to(earth, DOWN, buff=0.1), sans("Mars", 22, C.muted).next_to(mars, RIGHT, buff=0.12))
    for k in range(12):                                     # the Sun's rays
        q = 2 * math.pi * k / 12
        u = P3(math.cos(q), math.sin(q))
        g.add(Line(SUN + 0.17 * u, SUN + 0.27 * u, stroke_color=C.text, stroke_width=1.6))
    path = [craft(M)[0] for M in np.linspace(0, ne * tt, max(2, int(60 * f) + 2))]
    if f > 0:
        g.add(VMobject(stroke_color=C.change, stroke_width=3).set_points_as_corners(path))
    pos, v = craft(ne * tt)
    g.add(Arrow(pos, pos + P3(*(0.8 * v)), buff=0, stroke_width=4, max_tip_length_to_length_ratio=0.3,
                color=C.change), Dot(pos, radius=0.075, color=C.change))
    g.add(tags(("calculus", "change")))
    return g


@scene(T.in_s03, T.in_s04)
def in_s03(s):
    s.solid(C.bg, z=-200)
    mp, m = s.manim(z=-1), s.manim(z=0)
    hud = s.manim(z=2, parallax=0)
    links = map_lines(color=C.map_off, width=1.8, opacity=0.75)
    mp.add(map_deco(), links)
    m.add(the_circle(fill_color=C.bg, fill_opacity=1.0))
    s.camera.frame(T.in_s03 + 1.3, center=CAM_C, zoom=CAM_Z, dur=1.6)

    nums = [tex(str(r), 24, C.muted) for r in range(17)]
    beats_ = [float(T.in_s03_phone), float(T.in_s03_spam), float(T.in_s03_secure), float(T.in_s03_spacecraft)]
    ends = beats_[1:] + [float(s.end) - 0.3]
    ends = [e - 0.35 for e in ends]
    makers = [gps, spam, lambda t, t0: mod_dial(t, t0, nums), orbit]
    for pil, t0, t1, mk in zip(("space", "uncertainty", "quantity", "change"), beats_, ends, makers):
        k = PILLARS.index(pil)
        org = screen(node_xy(k))
        hud.redraw(window(lambda t, t0=t0, t1=t1, mk=mk, org=org: placed(mk(t, t0), t, t0, t1, org), t0 - 0.2, t1),
                   during=(t0 - 0.2, t1 + 0.05))
        mark = Dot(node_xy(k), radius=0.1, color=hue(pil))
        mp.play(GrowFromCenter(mark), at=t0, dur=0.3, ease="out_back")
        mp.play(FadeOut(mark), at=t1, dur=0.3)
    t0, t1 = beats_[1], ends[1]                               # P(spam) shading behind the spam glimpse (world space)
    x0, y0, x1, y1 = BOX
    cen = (CAM_C[0] + (x0 + x1) / 2 / CAM_Z, CAM_C[1] + (y0 + y1) / 2 / CAM_Z)
    ext = ((x1 - x0) / CAM_Z, (y1 - y0) / CAM_Z)
    s.add(FieldLayer(lambda t, f=p_spam_field(): f, cmap="diverging", vmin=0.0, vmax=1.0, contours=10,
                     colors=(C.bg, tint(C.uncertainty, 0.05), tint(C.uncertainty, 0.2)), extent=ext, center=cen,
                     opacity=fade(t0 + 1.2, dur=0.8, out=t1 - 0.3, out_dur=0.35), z=1, animated=False,
                     start=t0 + 0.9, end=t1 + 0.2))
