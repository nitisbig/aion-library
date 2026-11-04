"""Tower Bridge as 3D polylines (+ optional solid meshes), in metres.

Axes: x along the bridge (centre of the river opening at x=0), y up (high water at y=0),
z across the bridge (upstream/downstream). Proportions follow the real bridge
(65 m towers, 61 m central opening, 82 m side spans, walkways ~44 m above high
water, bascules opening to 86°). Small details are simplified.
"""

from __future__ import annotations

import numpy as np

# ── groups (shared with the shaders) ────────────────────────────────────────
WATER, PIER, STEEL, STONE, WALKWAY, CHAIN, HANGER, DECK, BASCULE, SHORE, CHAMBER, CWEIGHT, TIE = range(13)
N_GROUPS = 16

# ── dimensions ──────────────────────────────────────────────────────────────
DECK_Y = 9.0            # road level
HALF_OPEN = 30.5        # central opening 61 m
TOWER_W = 18.0          # tower width along x
TOWER_D = 11.0          # tower half-depth along z
TOWER_X0, TOWER_X1 = HALF_OPEN, HALF_OPEN + TOWER_W          # 30.5 … 48.5
TOWER_XC = 0.5 * (TOWER_X0 + TOWER_X1)
BODY_TOP = 50.0         # parapet
ROOF_PEAK = 64.0
FINIAL = 65.5
TURRET_R = 2.4
TURRET_TOP, SPIRE_TOP = 54.0, 61.0
ROAD_W = 7.5            # half road width; chains and hangers sit on this line
WALK_Y0, WALK_Y1 = 42.0, 47.0
WALK_Z0, WALK_Z1 = 5.5, 9.5
CHAIN_TOWER_Y = 46.0
SHORE_X0, SHORE_X1 = TOWER_X1 + 77.0, TOWER_X1 + 87.0        # 125.5 … 135.5
SHORE_D, SHORE_TOP, SHORE_PEAK = 9.0, 27.0, 33.0
CHAIN_SHORE_Y = 26.0
CHAIN_MIN_Y = 13.5      # lowest point of the chain's top chord
CHAIN_DEPTH = 2.2
PIVOT_X, PIVOT_Y = 34.5, 8.0
BASCULE_MAX_DEG = 86.0


def chain_parabola():
    """Top-chord parabola y = a(|x|-x0)^2 + ymin through both chain anchor points."""
    xa, ya = SHORE_X0, CHAIN_SHORE_Y
    xb, yb = TOWER_X1, CHAIN_TOWER_Y
    sq_a = (np.sqrt(ya - CHAIN_MIN_Y) + np.sqrt(yb - CHAIN_MIN_Y)) / (xa - xb)
    a = sq_a ** 2
    x0 = xa - np.sqrt((ya - CHAIN_MIN_Y) / a)
    return a, x0


class Geo:
    def __init__(self):
        self.lines: list[tuple[np.ndarray, int, int, float | None]] = []
        self.tris: list[tuple[np.ndarray, int, int]] = []   # (3x3 verts, group, rig)

    # lines ------------------------------------------------------------------
    def line(self, pts, group, rig=0, order=None):
        p = np.asarray(pts, float)
        if len(p) >= 2:
            self.lines.append((p, group, rig, order))

    def loop(self, pts, group, rig=0, order=None):
        p = np.asarray(pts, float)
        self.line(np.vstack([p, p[:1]]), group, rig, order)

    # meshes -----------------------------------------------------------------
    def tri(self, a, b, c, group, rig=0):
        self.tris.append((np.array([a, b, c], float), group, rig))

    def quad(self, a, b, c, d, group, rig=0):
        self.tri(a, b, c, group, rig)
        self.tri(a, c, d, group, rig)

    def prism(self, poly_xz, y0, y1, group, rig=0, caps=True):
        poly = np.asarray(poly_xz, float)
        n = len(poly)
        for i in range(n):
            (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
            self.quad((x0, y0, z0), (x1, y0, z1), (x1, y1, z1), (x0, y1, z0), group, rig)
        if caps:
            cx, cz = poly.mean(0)
            for i in range(n):
                (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
                self.tri((cx, y1, cz), (x0, y1, z0), (x1, y1, z1), group, rig)
                self.tri((cx, y0, cz), (x1, y0, z1), (x0, y0, z0), group, rig)

    def cone(self, poly_xz, y0, apex, group, rig=0):
        poly = np.asarray(poly_xz, float)
        n = len(poly)
        for i in range(n):
            (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % n]
            self.tri((x0, y0, z0), (x1, y0, z1), apex, group, rig)

    def box(self, x0, x1, y0, y1, z0, z1, group, rig=0):
        self.prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, group, rig)


# ── 2D helpers ──────────────────────────────────────────────────────────────
def octagon(cx, cz, r):
    a = np.pi / 8 + np.arange(8) * np.pi / 4
    return np.c_[cx + r * np.cos(a), cz + r * np.sin(a)]


def pointed_arch(width, y_sill, y_spring, ratio=0.7, n=10):
    """Gothic pointed arch outline in face coords (u, y), u centred on 0, open at the sill."""
    h = width / 2
    r = ratio * width
    cos_a = (h - r) / r
    a_apex = np.arccos(np.clip(cos_a, -1, 1))
    # left arc centred at (-h + r, y_spring), from 180° down to the apex angle
    ang = np.linspace(np.pi, a_apex, n)
    left = np.c_[-h + r + r * np.cos(ang), y_spring + r * np.sin(ang)]
    right = left[::-1].copy()
    right[:, 0] *= -1
    pts = np.vstack([[[-h, y_sill]], left, right[1:], [[h, y_sill]]])
    return pts


def on_face(uv, face):
    """Map face coords (u, y) to 3D. face = (origin(x,z), u_axis(x,z))."""
    (ox, oz), (ux, uz) = face
    uv = np.asarray(uv, float)
    return np.c_[ox + uv[:, 0] * ux, uv[:, 1], oz + uv[:, 0] * uz]


# ── bridge parts ────────────────────────────────────────────────────────────
def build_pier(g: Geo, sgn):
    x0, x1 = sorted((sgn * (TOWER_X0 - 4.5), sgn * (TOWER_X1 + 4.5)))
    xc = 0.5 * (x0 + x1)
    zh, zn = 15.0, 22.0
    poly = [(x0, -zh), (x0, zh), (xc, zn), (x1, zh), (x1, -zh), (xc, -zn)]
    for y in (0.0, 3.0, 6.0, DECK_Y):
        g.loop([(x, y, z) for x, z in poly], PIER)
    for x, z in poly:
        g.line([(x, 0.0, z), (x, DECK_Y, z)], PIER)
    # the part below the waterline belongs to the cut-away
    for y in (-6.0, -14.0):
        g.loop([(x, y, z) for x, z in poly], CHAMBER)
    for x, z in poly:
        g.line([(x, -14.0, z), (x, 0.0, z)], CHAMBER)
    g.prism(poly, 0.0, DECK_Y, PIER)
    # counterweight chamber
    cx0, cx1 = sorted((sgn * (PIVOT_X - 6.5), sgn * (PIVOT_X + 13.5)))
    y0, y1, zc = -13.5, 7.5, 6.8
    for y in (y0, y1):
        g.loop([(cx0, y, -zc), (cx1, y, -zc), (cx1, y, zc), (cx0, y, zc)], CHAMBER)
    for x in (cx0, cx1):
        for z in (-zc, zc):
            g.line([(x, y0, z), (x, y1, z)], CHAMBER)
    # pivot axle
    g.line([(sgn * PIVOT_X, PIVOT_Y, -9), (sgn * PIVOT_X, PIVOT_Y, 9)], CHAMBER)


def build_tower_steel(g: Geo, sgn):
    x0, x1 = sorted((sgn * TOWER_X0, sgn * TOWER_X1))
    xc, D = 0.5 * (x0 + x1), TOWER_D
    corners = [(x0, -D), (x1, -D), (x1, D), (x0, D)]
    levels = [DECK_Y, 18.0, 27.0, 36.0, WALK_Y0, WALK_Y1, BODY_TOP]
    # corner columns, drawn as paired members
    for cx, cz in corners:
        for dx in (-0.45, 0.45):
            g.line([(cx + dx, DECK_Y, cz), (cx + dx, BODY_TOP, cz)], STEEL)
    # mid columns on the z faces (full height) and on the x faces (above the portal)
    for z in (-D, D):
        g.line([(xc, DECK_Y, z), (xc, BODY_TOP, z)], STEEL)
    for x in (x0, x1):
        g.line([(x, 27.0, 0.0), (x, BODY_TOP, 0.0)], STEEL)
        # road portal beam
        g.line([(x, 25.0, -D), (x, 25.0, D)], STEEL)

    for y in levels:
        # z faces: full beams; x faces: beams skip the road opening below the portal
        for z in (-D, D):
            g.line([(x0, y, z), (x1, y, z)], STEEL)
        for x in (x0, x1):
            if y < 25.0:
                g.line([(x, y, -D), (x, y, -ROAD_W - 0.5)], STEEL)
                g.line([(x, y, ROAD_W + 0.5), (x, y, D)], STEEL)
            else:
                g.line([(x, y, -D), (x, y, D)], STEEL)
    # floor diagonals
    for y in (27.0, WALK_Y0, BODY_TOP):
        g.line([(x0, y, -D), (x1, y, D)], STEEL)
        g.line([(x1, y, -D), (x0, y, D)], STEEL)

    # X bracing between levels
    for ya, yb in zip(levels[:-1], levels[1:]):
        for z in (-D, D):                       # z faces: two bays
            for u0, u1 in ((x0, xc), (xc, x1)):
                g.line([(u0, ya, z), (u1, yb, z)], STEEL)
                g.line([(u1, ya, z), (u0, yb, z)], STEEL)
        if ya >= 27.0:                          # x faces: above the portal only
            for x in (x0, x1):
                for z0, z1 in ((-D, 0.0), (0.0, D)):
                    g.line([(x, ya, z0), (x, yb, z1)], STEEL)
                    g.line([(x, ya, z1), (x, yb, z0)], STEEL)
    # roof frame: rafters from the body top to the peak
    peak = (xc, ROOF_PEAK - 1.0, 0.0)
    for cx, cz in corners:
        ix = cx + np.sign(xc - cx) * 2.0
        iz = cz + np.sign(-cz) * 2.0
        g.line([(ix, BODY_TOP, iz), peak], STEEL)


def build_tower_stone(g: Geo, sgn):
    x0, x1 = sorted((sgn * TOWER_X0, sgn * TOWER_X1))
    xc, D = 0.5 * (x0 + x1), TOWER_D
    corners = [(x0, -D), (x1, -D), (x1, D), (x0, D)]

    # string courses
    for y in (27.0, 36.0, BODY_TOP):
        g.loop([(x0, y, -D), (x1, y, -D), (x1, y, D), (x0, y, D)], STONE)
    # crenellated parapet on each face
    faces_top = [((x0, -D), (x1, -D)), ((x1, -D), (x1, D)), ((x1, D), (x0, D)), ((x0, D), (x0, -D))]
    for (ax, az), (bx, bz) in faces_top:
        n = 9
        pts = []
        for i in range(n):
            t0, t1 = i / n, (i + 0.5) / n
            for t, hi in ((t0, 0), (t0, 1), (t1, 1), (t1, 0)):
                pts.append((ax + (bx - ax) * t, BODY_TOP + 1.6 * hi, az + (bz - az) * t))
        pts.append((bx, BODY_TOP, bz))
        g.line(pts, STONE)

    # corner turrets with spires
    for cx, cz in corners:
        oc = octagon(cx, cz, TURRET_R)
        for y in (DECK_Y, 27.0, BODY_TOP, TURRET_TOP):
            g.loop([(x, y, z) for x, z in oc], STONE)
        for x, z in oc[::2]:
            g.line([(x, DECK_Y, z), (x, TURRET_TOP, z)], STONE)
        apex = (cx, SPIRE_TOP, cz)
        for x, z in oc:
            g.line([(x, TURRET_TOP, z), apex], STONE)
        g.line([apex, (cx, SPIRE_TOP + 1.2, cz)], STONE)
        g.prism(oc, DECK_Y, TURRET_TOP, STONE)
        g.cone(oc, TURRET_TOP, apex, STONE)

    # central pyramid roof
    i = 2.0
    base = [(x0 + i, -D + i), (x1 - i, -D + i), (x1 - i, D - i), (x0 + i, D - i)]
    peak = (xc, ROOF_PEAK, 0.0)
    g.loop([(x, BODY_TOP, z) for x, z in base], STONE)
    for x, z in base:
        g.line([(x, BODY_TOP, z), peak], STONE)
    mid_y = BODY_TOP + 0.45 * (ROOF_PEAK - BODY_TOP)
    g.loop([(x + (xc - x) * 0.45, mid_y, z * 0.55) for x, z in base], STONE)
    g.line([peak, (xc, FINIAL, 0.0)], STONE)
    g.box(x0, x1, DECK_Y, BODY_TOP, -D, D, STONE)
    g.cone(base, BODY_TOP, peak, STONE)

    # windows: z faces (u along x), x faces (u along z)
    z_faces = [((xc, D), (1, 0)), ((xc, -D), (-1, 0))]
    x_faces = [((x0, 0.0), (0, 1)), ((x1, 0.0), (0, -1))]
    win_levels = [(12.0, 15.5), (19.0, 23.0), (29.0, 32.8), (37.6, 40.4)]
    for face in z_faces:
        for us in (-4.2, 4.2):
            for ys, yp in win_levels:
                arch = pointed_arch(2.2, ys, yp)
                arch[:, 0] += us
                g.line(on_face(arch, face), STONE)
    for face in x_faces:
        road = pointed_arch(2 * ROAD_W, DECK_Y, 16.0, ratio=0.62, n=16)
        g.line(on_face(road, face), STONE)
        for us in (-3.6, 3.6):
            for ys, yp in win_levels[2:]:
                arch = pointed_arch(2.2, ys, yp)
                arch[:, 0] += us
                g.line(on_face(arch, face), STONE)


def build_shore_tower(g: Geo, sgn):
    x0, x1 = sorted((sgn * SHORE_X0, sgn * SHORE_X1))
    xc, D = 0.5 * (x0 + x1), SHORE_D
    rect = [(x0, -D), (x1, -D), (x1, D), (x0, D)]
    for y in (DECK_Y, 18.0, SHORE_TOP):
        g.loop([(x, y, z) for x, z in rect], SHORE)
    for x, z in rect:
        g.line([(x, DECK_Y, z), (x, SHORE_TOP, z)], SHORE)
    peak = (xc, SHORE_PEAK, 0.0)
    for x, z in rect:
        g.line([(x, SHORE_TOP, z), peak], SHORE)
    for face in [((xc, D), (1, 0)), ((xc, -D), (-1, 0))]:
        arch = pointed_arch(2.0, 20.0, 23.5)
        g.line(on_face(arch, face), SHORE)
    for face in [((x0, 0.0), (0, 1)), ((x1, 0.0), (0, -1))]:
        g.line(on_face(pointed_arch(2 * ROAD_W, DECK_Y, 13.5, ratio=0.62, n=14), face), SHORE)
    g.box(x0, x1, DECK_Y, SHORE_TOP, -D, D, SHORE)
    g.cone(rect, SHORE_TOP, peak, SHORE)
    # shore pier / abutment
    g.loop([(x0 - 2, 0.0, -D - 2), (x1 + 2, 0.0, -D - 2), (x1 + 2, 0.0, D + 2), (x0 - 2, 0.0, D + 2)], PIER)
    for x in (x0 - 2, x1 + 2):
        for z in (-D - 2, D + 2):
            g.line([(x, 0.0, z), (x, DECK_Y, z)], PIER)
    g.box(x0 - 2, x1 + 2, 0.0, DECK_Y, -D - 2, D + 2, PIER)


def build_suspension(g: Geo, sgn):
    a, xv = chain_parabola()
    top = lambda ax: a * (ax - xv) ** 2 + CHAIN_MIN_Y          # noqa: E731

    xs = np.linspace(SHORE_X0, TOWER_X1, 23)                     # shore → tower
    for z in (-ROAD_W, ROAD_W):
        yt = top(xs)
        yb = yt - CHAIN_DEPTH * (0.45 + 0.55 * np.sin(np.pi * (xs - TOWER_X1) / (SHORE_X0 - TOWER_X1)))
        g.line(np.c_[sgn * xs, yt, np.full_like(xs, z)], CHAIN, order=0.0)
        g.line(np.c_[sgn * xs, yb, np.full_like(xs, z)], CHAIN, order=0.1)
        # lattice: zig-zag between the chords
        zig = np.c_[sgn * xs, np.where(np.arange(len(xs)) % 2 == 0, yt, yb), np.full_like(xs, z)]
        g.line(zig, CHAIN, order=0.3)
        # back-stay to the anchorage behind the shore tower, and over the shore tower top
        g.line([(sgn * (SHORE_X1 + 14.0), DECK_Y, z), (sgn * SHORE_X1, CHAIN_SHORE_Y, z),
                (sgn * SHORE_X0, CHAIN_SHORE_Y, z)], CHAIN, order=0.0)
        # tie through the tower top: chain end → walkway
        g.line([(sgn * TOWER_X1, CHAIN_TOWER_Y, z), (sgn * TOWER_X0, CHAIN_TOWER_Y, z)], TIE)
        # hangers: chain bottom chord → deck edge
        for hx in np.arange(TOWER_X1 + 4.0, SHORE_X0 - 2.0, 5.0):
            hy = top(hx) - CHAIN_DEPTH * (0.45 + 0.55 * np.sin(np.pi * (hx - TOWER_X1) / (SHORE_X0 - TOWER_X1)))
            if hy - DECK_Y > 0.6:
                g.line([(sgn * hx, hy, z), (sgn * hx, DECK_Y, z)], HANGER)
        # anchorage block
        ax = sgn * (SHORE_X1 + 14.0)
        g.loop([(ax - 2.5, DECK_Y - 1.5, z - 1.5), (ax + 2.5, DECK_Y - 1.5, z - 1.5),
                (ax + 2.5, DECK_Y - 1.5, z + 1.5), (ax - 2.5, DECK_Y - 1.5, z + 1.5)], CHAIN, order=0.0)
    # cross-bracing between the two chains at panel points
    for i in range(1, len(xs) - 1, 3):
        y = top(xs[i])
        g.line([(sgn * xs[i], y, -ROAD_W), (sgn * xs[i], y, ROAD_W)], CHAIN, order=0.6)


def build_side_deck(g: Geo, sgn):
    xa, xb = TOWER_X1, SHORE_X1 + 26.0
    for z in (-ROAD_W, ROAD_W):
        g.line([(sgn * xa, DECK_Y, z), (sgn * xb, DECK_Y, z)], DECK)
        g.line([(sgn * xa, DECK_Y + 1.2, z), (sgn * xb, DECK_Y + 1.2, z)], DECK)
        g.line([(sgn * xa, DECK_Y - 1.4, z), (sgn * SHORE_X0, DECK_Y - 1.4, z)], DECK)
    for x in np.arange(xa, SHORE_X0 + 0.1, 5.5):
        g.line([(sgn * x, DECK_Y, -ROAD_W), (sgn * x, DECK_Y, ROAD_W)], DECK)
        for z in (-ROAD_W, ROAD_W):
            g.line([(sgn * x, DECK_Y - 1.4, z), (sgn * x, DECK_Y + 1.2, z)], DECK)
    x0, x1 = sorted((sgn * xa, sgn * SHORE_X0))
    g.box(x0, x1, DECK_Y - 1.4, DECK_Y, -ROAD_W, ROAD_W, DECK)


def build_bascule(g: Geo, sgn):
    """Leaf in local coords (u along the leaf toward the centre, v up), pivot at (PIVOT_X, PIVOT_Y)."""
    rig = 1 if sgn < 0 else 2
    to_world = lambda u, v, z: (sgn * (PIVOT_X - u), PIVOT_Y + v, z)   # noqa: E731
    u_face, u_tip = PIVOT_X - TOWER_X0, PIVOT_X - 0.06                  # 4 … 34.44
    us = np.linspace(u_face - 3.0, u_tip, 13)
    for z in (-ROAD_W, ROAD_W):
        top = [to_world(u, 1.0, z) for u in us]
        bot_v = -2.6 + 2.2 * (us - us[0]) / (us[-1] - us[0])
        bot = [to_world(u, v, z) for u, v in zip(us, bot_v)]
        g.line(top, BASCULE, rig)
        g.line(bot, BASCULE, rig)
        g.line([to_world(u, 1.0 + 1.1, z) for u in us], BASCULE, rig)       # railing
        for i, (u, v) in enumerate(zip(us, bot_v)):
            g.line([to_world(u, v, z), to_world(u, 1.0, z)], BASCULE, rig)
            if i + 1 < len(us):
                g.line([to_world(u, v, z), to_world(us[i + 1], 1.0, z)], BASCULE, rig)
    for u in us[::2]:
        g.line([to_world(u, 1.0, -ROAD_W), to_world(u, 1.0, ROAD_W)], BASCULE, rig)
    g.line([to_world(u_tip, 1.0, -ROAD_W), to_world(u_tip, 1.0, ROAD_W)], BASCULE, rig)
    # solid slab for look C
    a, b = to_world(u_face - 3.0, -0.6, 0)[0], to_world(u_tip, -0.6, 0)[0]
    g.box(min(a, b), max(a, b), PIVOT_Y - 0.6, PIVOT_Y + 1.0, -ROAD_W, ROAD_W, BASCULE, rig)

    # tail + counterweight (behind the pivot, inside the pier)
    for z in (-6.0, 6.0):
        g.line([to_world(u_face - 3.0, 1.0, z), to_world(0.0, 0.0, z), to_world(-4.0, -0.5, z)], CWEIGHT, rig)
    cw = [(-4.0, 0.8), (-12.0, 0.8), (-12.0, -5.5), (-4.0, -5.5)]
    for z in (-6.0, 6.0):
        g.loop([to_world(u, v, z) for u, v in cw], CWEIGHT, rig)
    for u, v in cw:
        g.line([to_world(u, v, -6.0), to_world(u, v, 6.0)], CWEIGHT, rig)
    for z in (-6.0, 6.0):
        g.line([to_world(-4.0, 0.8, z), to_world(-12.0, -5.5, z)], CWEIGHT, rig)


def build_walkways(g: Geo):
    n = 20
    xs = np.linspace(-TOWER_X0, TOWER_X0, n + 1)
    for s in (-1, 1):
        zs = (s * WALK_Z0, s * WALK_Z1)
        for z in zs:
            for y in (WALK_Y0, WALK_Y1):
                # chords drawn from each tower toward the centre
                g.line([(-TOWER_X0, y, z), (0.0, y, z)], WALKWAY, order=0.0)
                g.line([(TOWER_X0, y, z), (0.0, y, z)], WALKWAY, order=0.0)
            for i, x in enumerate(xs):
                o = 0.15 + 0.6 * (1 - abs(x) / TOWER_X0)
                g.line([(x, WALK_Y0, z), (x, WALK_Y1, z)], WALKWAY, order=o)
                if i < n:
                    ya, yb = (WALK_Y0, WALK_Y1) if i % 2 == 0 else (WALK_Y1, WALK_Y0)
                    g.line([(x, ya, z), (xs[i + 1], yb, z)], WALKWAY, order=o)
        for x in xs[::2]:
            o = 0.15 + 0.6 * (1 - abs(x) / TOWER_X0)
            for y in (WALK_Y0, WALK_Y1):
                g.line([(x, y, zs[0]), (x, y, zs[1])], WALKWAY, order=o)
        z0, z1 = sorted(zs)
        g.box(-TOWER_X0, TOWER_X0, WALK_Y0, WALK_Y1, z0, z1, WALKWAY)


def build_water(g: Geo, seed=7):
    rng = np.random.default_rng(seed)
    # main water lines drawn outward from the centre
    for z in (36.0, 14.0, -24.0, -70.0):
        for sgn in (-1, 1):
            g.line([(0.0, 0.0, z), (sgn * 320.0, 0.0, z)], WATER, order=0.0)
    # short ripple dashes
    for _ in range(420):
        x = rng.uniform(-300, 300)
        z = rng.uniform(-120, 170)
        L = rng.uniform(2.0, 9.0) * (1 + abs(z - 30) / 120)
        g.line([(x - L / 2, 0.0, z), (x + L / 2, 0.0, z)], WATER, order=min(abs(x) / 300, 1.0))


def build():
    g = Geo()
    build_water(g)
    for sgn in (-1, 1):
        build_pier(g, sgn)
        build_tower_steel(g, sgn)
        build_tower_stone(g, sgn)
        build_shore_tower(g, sgn)
        build_suspension(g, sgn)
        build_side_deck(g, sgn)
        build_bascule(g, sgn)
    build_walkways(g)
    return g


# ── ordering & export ───────────────────────────────────────────────────────
def _order_key(group, p):
    ymin, xc = p[:, 1].min(), p[:, 0].mean()
    right = 1.0 if xc > 0 else 0.0
    if group == STEEL:
        return 0.78 * np.clip((ymin - DECK_Y) / (ROOF_PEAK - DECK_Y), 0, 1) + 0.22 * right
    if group in (STONE, SHORE):
        return 0.8 * np.clip((ymin - DECK_Y) / (FINIAL - DECK_Y), 0, 1) + 0.2 * right
    if group == PIER:
        return 0.3 * right + 0.5 * np.clip(ymin / DECK_Y, 0, 1)
    if group in (HANGER, DECK):
        return np.clip((abs(xc) - TOWER_X1) / (SHORE_X1 + 26 - TOWER_X1), 0, 1)
    if group in (BASCULE, CWEIGHT, CHAMBER):
        return 0.5 * right + 0.4 * np.clip((ymin + 14) / 25, 0, 1)
    return 0.0


def line_array(g: Geo, max_seg=2.5):
    """Segments as float32 rows [x, y, z, s, order, group, rig], two rows per segment."""
    rows = []
    for p, group, rig, order in g.lines:
        if order is None:
            order = _order_key(group, p)
        # subdivide so no segment is longer than max_seg (reflection wobble, near clipping)
        dense = [p[0]]
        for a, b in zip(p[:-1], p[1:]):
            k = max(1, int(np.ceil(np.linalg.norm(b - a) / max_seg)))
            for i in range(1, k + 1):
                dense.append(a + (b - a) * i / k)
        dense = np.array(dense)
        seg = np.linalg.norm(np.diff(dense, axis=0), axis=1)
        s = np.r_[0.0, np.cumsum(seg)]
        s = s / s[-1] if s[-1] > 0 else s
        for i in range(len(dense) - 1):
            for j in (i, i + 1):
                rows.append((*dense[j], s[j], order, group, rig))
    return np.asarray(rows, np.float32)


def mesh_array(g: Geo):
    """Triangles as float32 rows [x, y, z, nx, ny, nz, group, rig]."""
    rows = []
    for tri, group, rig in g.tris:
        n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n /= ln
        for v in tri:
            rows.append((*v, *n, group, rig))
    return np.asarray(rows, np.float32)


if __name__ == "__main__":
    g = build()
    la, ma = line_array(g), mesh_array(g)
    print(f"{len(g.lines)} polylines → {len(la) // 2} segments; {len(ma) // 3} triangles")
    a, x0 = chain_parabola()
    print(f"chain parabola: a={a:.5f}, vertex |x|={x0:.2f} m")
