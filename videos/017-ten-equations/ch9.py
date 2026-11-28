"""Chapter 9 (Bayes' theorem): shared geometry and maths for scenes s28–s30.

Everything shown is computed: the 1,000 people come from sims.bayes_people (10 ill, 9 of them positive; 89 of the
990 healthy positive, seeded); the area square uses the exact rates (1 %, 90 %, 9 %); the belief curves are Beta
posteriors after seeded coin flips; the search map is a Bayesian update of a Gaussian prior by searched areas with
a detection probability.
"""
from __future__ import annotations

import math

import numpy as np
from aion import C
from manim import VGroup

from kit import P3, polyline, smooth01

# ------------------------------------------------------------------------------------------ 1,000 people (c09_s01)
NC, NR, SP = 40, 25, 0.19                     # the grid: columns, rows, spacing
GC = np.array([-0.9, 0.3])                    # grid centre
DOT = 6.0                                     # PointsLayer size (px radius at 1080p)


def people():
    import sims
    return sims.bayes_people()


def grid_xy():
    """Each person's cell in the 40 × 25 grid (a seeded shuffle, so the ill are scattered)."""
    perm = np.random.default_rng(1763).permutation(NC * NR)
    c, r = perm % NC, perm // NC
    return GC + SP * np.stack([c - (NC - 1) / 2, (NR - 1) / 2 - r], 1)


def block(n, cols, centre, sp):
    k = np.arange(n)
    rows = math.ceil(n / cols)
    return np.asarray(centre) + sp * np.stack([k % cols - (cols - 1) / 2, (rows - 1) / 2 - k // cols], 1)


ILL_C = np.array([-5.15, 0.3])
HEALTHY_C = np.array([0.15, 0.3])


def split_xy():
    """Ill in a 2 × 5 block on the left, ill positives first; healthy in a 45 × 22 block, positives scattered."""
    ill, pos = people()
    out = np.zeros((1000, 2))
    io = np.argsort(~pos[ill], kind="stable")                  # positives first among the ill
    out[np.where(ill)[0][io]] = block(10, 2, ILL_C, 0.32)
    h = np.where(~ill)[0]
    out[h] = block(len(h), 45, HEALTHY_C, 0.17)
    return out


POS_C = np.array([-2.0, 0.0])


def positives_xy(base):
    """The 98 positives in a 14 × 7 block (the 9 ill first); everyone else stays where `base` has them."""
    ill, pos = people()
    out = base.copy()
    idx = np.where(pos)[0]
    idx = idx[np.argsort(~ill[idx], kind="stable")]
    out[idx] = block(len(idx), 14, POS_C, 0.34)
    return out


def ease_between(a, b, t, t0, dur, stagger=0.0, seed=0):
    """Positions moving from a to b starting at t0 (each dot delayed by up to `stagger`, seeded)."""
    d = np.random.default_rng(seed).uniform(0, stagger, len(a))
    u = np.clip((t - t0 - d) / dur, 0, 1)
    u = u * u * (3 - 2 * u)
    return a + (b - a) * u[:, None]


# --------------------------------------------------------------------------------------- the area square (c09_s02)
SQ = (-5.2, 1.2, -2.45, 1.95)                 # x0, x1, y0, y1 of everyone (areas ∝ shares)
P_ILL, WIDEN = 0.01, 8.0                      # the prior, and how much the ill strip is widened to be seen
SENS, FPR = 0.9, 0.09


def sq_regions():
    """Screen rectangles (x0, x1, y0, y1) of: ill-positive, ill-negative, healthy-positive, healthy-negative."""
    x0, x1, y0, y1 = SQ
    xs = x0 + (x1 - x0) * P_ILL * WIDEN
    yi = y1 - (y1 - y0) * SENS
    yh = y1 - (y1 - y0) * FPR
    return {"ill_pos": (x0, xs, yi, y1), "ill_neg": (x0, xs, y0, yi),
            "h_pos": (xs, x1, yh, y1), "h_neg": (xs, x1, y0, yh)}


def posterior():
    return SENS * P_ILL / (SENS * P_ILL + FPR * (1 - P_ILL))


# ------------------------------------------------------------------------------------------ updating (c09_s03)
FLIPS_P, N_CURVES, PER = 0.7, 8, (0, 1, 2, 4, 7, 12, 20, 32)


def flips(seed=1763):
    return np.random.default_rng(seed).random(PER[-1]) < FLIPS_P


def beta_pdf(x, a, b):
    from scipy.special import betaln
    return np.exp((a - 1) * np.log(np.clip(x, 1e-9, 1)) + (b - 1) * np.log(np.clip(1 - x, 1e-9, 1)) - betaln(a, b))


def belief(k):
    """Beta(1 + heads, 1 + tails) after the first PER[k] flips."""
    f = flips()[:PER[k]]
    return 1 + int(f.sum()), 1 + int((~f).sum())


RB_X0, RB_W, RB_Y0, RB_H = -5.4, 5.2, -1.9, 0.38    # ribbon: x of p = 0, width of [0, 1], baseline, height per unit
DEPTH = np.array([0.42, 0.33])                       # screen offset per step back in depth


def ribbon_curve(k, yaw=0.0, x=None):
    a, b = belief(k)
    x = np.linspace(0.002, 0.998, 220) if x is None else x
    y = beta_pdf(x, a, b)
    d = DEPTH @ np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]]).T
    off = k * d
    return np.stack([RB_X0 + RB_W * x + off[0], RB_Y0 + RB_H * y + off[1]], 1), (RB_X0 + off[0], RB_Y0 + off[1])


# --------------------------------------------------------------------------------------------- the search map
MAP_N = (26, 16)                                   # cells across, down
MAP_BOX = (-5.6, 0.9, -2.3, 1.7)                   # screen box
LKP = np.array([0.42, 0.55])                       # last known position, in map units (0..1)
SEARCHED = ((8, 13, 7, 11), (14, 18, 5, 8), (10, 15, 12, 13))   # areas searched before (cells: j0, j1, i0, i1)


def _cell_centres():
    nx, ny = MAP_N
    u = (np.arange(nx) + 0.5) / nx
    v = (np.arange(ny) + 0.5) / ny
    return np.meshgrid(u, v)


def search_maps():
    """Prior (a Gaussian around the last known position, plus a broad drift tail), the searched mask, the
    posterior after those searches found nothing (detection probability 0.85), and the cell of the wreck."""
    U, V = _cell_centres()
    d2 = ((U - LKP[0]) * 1.6) ** 2 + (V - LKP[1]) ** 2
    prior = np.exp(-d2 / (2 * 0.16 ** 2)) + 0.35 * np.exp(-((U - LKP[0] - 0.18) ** 2 + (V - LKP[1] + 0.12) ** 2)
                                                          / (2 * 0.2 ** 2))
    prior /= prior.sum()
    searched = np.zeros_like(prior, bool)
    for (j0, j1, i0, i1) in SEARCHED:
        searched[i0:i1 + 1, j0:j1 + 1] = True
    post = prior * np.where(searched, 1 - 0.85, 1.0)
    post /= post.sum()
    wreck = np.unravel_index(np.argmax(post), post.shape)
    return prior, searched, post, wreck


def cell_rect(i, j):
    nx, ny = MAP_N
    x0, x1, y0, y1 = MAP_BOX
    w, h = (x1 - x0) / nx, (y1 - y0) / ny
    return x0 + j * w, y1 - (i + 1) * h, w, h


def _rect(r, **kw):
    from manim import Rectangle
    x0, x1, y0, y1 = r
    return Rectangle(width=x1 - x0, height=y1 - y0, **kw).move_to(P3((x0 + x1) / 2, (y0 + y1) / 2))


def rule_final():
    """c09_s02's last frame: (plain parts, glowing outlines). Used by c09_s03 to open on it."""
    from aion import Eqn
    from manim import DOWN, LEFT, RIGHT, UP, Line

    from kit import RC, fit, name_tag, sans, tag_under, tex
    x0, x1, y0, y1 = SQ
    R = sq_regions()
    xs, yi, yh = R["ill_pos"][1], R["ill_pos"][2], R["h_pos"][2]
    g = VGroup(_rect(SQ, stroke_color=C.muted, stroke_width=2),
               Line(P3(xs, y0), P3(xs, y1), stroke_color=C.muted, stroke_width=2),
               Line(P3(x0, yi), P3(xs, yi), stroke_color=C.muted, stroke_width=2),
               Line(P3(xs, yh), P3(x1, yh), stroke_color=C.muted, stroke_width=2),
               _rect(R["ill_pos"], stroke_width=0, fill_color=C.positive, fill_opacity=0.55),
               _rect(R["h_pos"], stroke_width=0, fill_color=C.positive, fill_opacity=0.55),
               sans("ill", 24, C.text).move_to(P3((x0 + xs) / 2, y0 - 0.3)),
               sans("healthy", 24, C.text).move_to(P3((xs + x1) / 2, y0 - 0.3)),
               sans("1 %, drawn 8 times wider", 20, C.muted).move_to(P3(x0, y1 + 0.3), aligned_edge=LEFT),
               sans("positive", 22, C.positive).move_to(P3(x1, y1 + 0.3), aligned_edge=RIGHT),
               sans("90 %", 20, C.muted).next_to(P3(x0, (yi + y1) / 2), LEFT, buff=0.15),
               sans("9 %", 20, C.muted).next_to(P3(x1, (yh + y1) / 2), RIGHT, buff=0.15),
               name_tag("Thomas Bayes · 1763", C.bayes))
    keys = {r"P(A\mid B)": C.bayes, r"P(B\mid A)": C.positive, "P(A)": C.prior, "P(B)": C.positive}
    e = Eqn(r"P(A\mid B)=\frac{P(B\mid A)\,P(A)}{P(B)}", colors=keys)
    fit(e).move_to(P3(RC, 1.0))
    legend = VGroup(VGroup(tex("A", 30, C.text), sans("ill", 24, C.text)).arrange(RIGHT, buff=0.25),
                    VGroup(tex("B", 30, C.text), sans("positive", 24, C.positive)).arrange(RIGHT, buff=0.25)) \
        .arrange(RIGHT, buff=0.7).move_to(P3(RC, -1.3))
    g.add(e, legend, sans("before", 22, C.prior).next_to(e.part("P(A)"), UP, buff=0.22),
          sans("explains", 22, C.positive).next_to(e.part(r"P(B\mid A)"), UP, buff=0.22),
          tag_under(e, "P(B)", "all positives", C.positive), tag_under(e, r"P(A\mid B)", "after", C.bayes),
          tex(rf"\approx {100 * posterior():.0f}\%", 34, C.bayes).next_to(legend, UP, buff=0.35))
    gl = VGroup(_rect(R["ill_pos"], stroke_color=C.positive, stroke_width=3.5, fill_opacity=0),
                _rect(R["h_pos"], stroke_color=C.positive, stroke_width=3.5, fill_opacity=0))
    return g, gl


def envelope():
    from manim import Line, Rectangle
    body = Rectangle(width=1.0, height=0.66, stroke_width=2.4)
    flap = VGroup(Line(P3(-0.5, 0.33), P3(0, -0.05), stroke_width=2.2), Line(P3(0.5, 0.33), P3(0, -0.05), stroke_width=2.2))
    return VGroup(body, flap).set_stroke(color=C.light)


def car():
    from manim import Arc, Circle, Line
    body = polyline([(-0.75, -0.12), (-0.75, 0.1), (-0.42, 0.14), (-0.22, 0.38), (0.3, 0.38), (0.5, 0.14),
                     (0.75, 0.1), (0.75, -0.12), (-0.75, -0.12)], C.light, 2.4)
    wheels = VGroup(*[Circle(radius=0.14, stroke_color=C.light, stroke_width=2.4).move_to(P3(x, -0.14))
                      for x in (-0.42, 0.42)])
    sensor = VGroup(*[Arc(radius=r, start_angle=-0.5, angle=1.0, stroke_color=C.light, stroke_width=1.6)
                      .move_arc_center_to(P3(0.78, 0.0)) for r in (0.18, 0.32)])
    return VGroup(body, wheels, sensor)
