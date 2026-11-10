"""Ch5 shared pieces: spin and average (S19–S23).

The stage: a chain rooted at O, drawn at scale K. Turning the drawing backward k times
per loop is a rotating frame: every arm turns at (n − k), and the ink the pen leaves is
w(τ) = z(L(τ)) · e^{−iΦ(τ)}, where L is the pen's loop clock and Φ = 2π ∫ k dL. Both
clocks are integrated from cue times (stateless), so every cut matches by construction.
Dots are 60 samples evenly in loop time; their mean is computed, and for whole k it is
exactly c_k (60 samples are exact for these drawings).
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from manim import (DOWN, ORIGIN, Arc, Circle, Dot, Line, MathTex, RoundedRectangle, VGroup, VMobject)

from aion import fourier as F
from aion import style as S
import shared as V
import ch4 as C4
from ch4 import TAU, cue, to3, path, pen, arm, color_of
import scene_18_rack as R18

S19, S20, S21, S22, S23 = (V.scene_range(n) for n in (19, 20, 21, 22, 23))
O = complex(-0.7, 0.35)           # chain root on the Ch5 stage
K = 1.45                          # screen units per drawing unit (bean)
K_RS = 1.45                       # rounded square: big circle radius on screen
N_DOTS = 60


# ── clocks ─────────────────────────────────────────────────────────────────
def levels(knots, t, start: float = 0.0):
    """Eased piecewise level: knots = [(t_start, ease_s, new_level)…] (smoothstep between levels)."""
    t = np.asarray(t, float)
    out = np.full_like(t, start)
    lv = start
    for ts, d, new in knots:
        u = np.clip((t - ts) / d, 0, 1)
        out = np.where(t >= ts, lv + (new - lv) * u * u * (3 - 2 * u), out)
        lv = new
    return out


class Frame:
    """Pen loop clock L(t) and frame angle Φ(t) on a fine grid.

    Φ must equal 2πkL (mod 2π) whenever k is steady, so a frozen arm sits at its true angle
    arg(c_k) and the dots' mean lands exactly on its tip. Within the ramp to level k_i that
    starts at t_i: Φ = 2π[k_prev·L + (k(t) − k_prev)(L − Λ_i)], Λ_i = round(L(t_i)). It is
    continuous (mod 2π), whirl-free (|L − Λ_i| ≤ ½), and ≡ 2πk_iL once k = k_i (Λ_i integer)."""

    def __init__(self, l_knots, k_knots, t0: float, t1: float, dt: float = 1 / 600):
        self.t = np.arange(t0, t1 + dt, dt)
        r = levels(l_knots, self.t)
        self.k = levels(k_knots, self.t)
        self.L = np.concatenate([[0.0], np.cumsum((r[1:] + r[:-1]) / 2 * dt)])
        self.phi = np.zeros_like(self.t)
        k_prev = 0.0
        for ts, _d, new in k_knots:
            lam = round(float(np.interp(ts, self.t, self.L)))
            seg = TAU * (k_prev * self.L + (self.k - k_prev) * (self.L - lam))
            i = int(np.searchsorted(self.t, ts))
            if i < len(self.t):
                seg = seg + (self.phi[i] - seg[i])        # a whole multiple of 2π: keeps Φ continuous (no ink chords)
            self.phi = np.where(self.t >= ts, seg, self.phi)
            k_prev = new

    def loops(self, t):
        return np.interp(t, self.t, self.L)

    def angle(self, t):
        return np.interp(t, self.t, self.phi)

    def k_at(self, t):
        return float(np.interp(t, self.t, self.k))

    def since(self, now: float, loops: float = 1.0, n: int = 900) -> np.ndarray:
        """Times τ ≤ now covering the last `loops` loops of the pen (or since it started)."""
        L1 = self.loops(now)
        i = np.searchsorted(self.L, max(L1 - loops, 0.0) + 1e-12)
        t0 = self.t[min(max(i - 1, 0), len(self.t) - 1)]
        if L1 <= 1e-6:
            return np.array([now])
        return np.linspace(min(t0, now), now, n)


# ── drawings ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def bean_terms_size():
    """The bean's circles by size: speed 1 first (from O), so its frozen tip is the spin-average."""
    return F.order_terms(V.BEAN, keep_zero_first=False)


def bean_terms_zero():
    """Speed 0 first (S19: the still arm from O)."""
    return F.order_terms(V.BEAN, keep_zero_first=True)


def rs_terms():
    return [(1, 1.0), (-3, -1 / 9)]


def z_of(terms, L):
    return F.partial_sum(dict(terms), L)


def vecs(terms, L: float, phi: float = 0.0, scale: float = K):
    return [scale * c * np.exp(1j * (TAU * n * L - phi)) for n, c in terms]


def ink(terms, frame: Frame, now: float, scale: float = K, op: float = 1.0, width: float = 3.5, loops: float = 1.0):
    tau = frame.since(now, loops)
    if len(tau) < 2:
        return VMobject()
    w = O + scale * z_of(terms, frame.loops(tau)) * np.exp(-1j * frame.angle(tau))
    return path(w, op=op, width=width)


def dots_at(terms, k: float, scale: float = K) -> np.ndarray:
    """The 60 dots of one loop, wound k times backward (screen points)."""
    t = np.arange(N_DOTS) / N_DOTS
    return O + scale * z_of(terms, t) * np.exp(-1j * TAU * k * t)


def dot_cloud(pts, collapse: float = 0.0, op: float = 1.0, lines: float = 0.0, mean_col=S.STILL,
              mean_op: float = 0.0) -> VGroup:
    """Dots that slide (staggered) into their mean; faint lines to the mean; the mean point."""
    pts = np.asarray(pts, complex)
    m = pts.mean()
    g = VGroup()
    n = len(pts)
    for j, p in enumerate(pts):
        u = np.clip((collapse - 0.35 * j / n) / 0.65, 0, 1)
        u = u * u * (3 - 2 * u)
        q = p + (m - p) * u
        if lines > 0 and u < 1:
            g.add(Line(to3(p), to3(m), color=S.INK, stroke_width=1).set_stroke(opacity=0.22 * lines * (1 - u)))
        if op > 0 and u < 0.999:
            g.add(Dot(to3(q), radius=0.05, color=S.INK).set_opacity(op))
    if mean_op > 0:
        g.add(Dot(to3(m), radius=0.2, color=mean_col).set_opacity(0.25 * mean_op),
              Dot(to3(m), radius=0.09, color=mean_col).set_opacity(mean_op))
    return g


def ping(at, u: float, color=S.LABEL_MUTED) -> VGroup:
    """An expanding ring + dot that fades (u: 0 → 1)."""
    if u <= 0 or u >= 1:
        return VGroup()
    return VGroup(Circle(radius=0.08 + 0.45 * u, color=color, stroke_width=2.5).move_to(to3(at))
                  .set_stroke(opacity=1 - u), Dot(to3(at), radius=0.07, color=color).set_opacity(1 - u * u))


def chain_mob(vs, origin=O, colors=None, op: float = 1.0, pen_op: float = 1.0, rim_op: float = 0.8, widths=None):
    g, p = C4.chain(vs, origin, rim_op=rim_op * op, arm_op=op, pen_op=pen_op * op, colors=colors)
    return g, p


def frame_ring(phi: float, op: float, center=O, r: float = 2.95) -> VGroup:
    """A thin orange ring at the stage edge with arrow marks, turned by the frame angle."""
    if op <= 0:
        return VGroup()
    g = VGroup(Circle(radius=r, color=S.BWD, stroke_width=1.6).move_to(to3(center)).set_stroke(opacity=0.45 * op))
    for k in range(3):
        a = -phi + k * TAU / 3 + 0.35
        arc = Arc(radius=r, start_angle=a, angle=-0.35, arc_center=to3(center), color=S.BWD, stroke_width=3)
        arc.add_tip(tip_length=0.18, tip_width=0.18)
        g.add(arc.set_opacity(op))
    return g


# ── the rack, small along the bottom ───────────────────────────────────────
RACK_SCALE, RACK_SHIFT = 0.65, np.array([0.0, -1.95, 0.0])


def rack_pos(p):
    return np.asarray(p, float) * RACK_SCALE + RACK_SHIFT


def rack_items(small: bool = True) -> dict:
    """{n: VGroup(slot, label, knob, tick)} + 'dots' (S18's end rack, optionally docked small at the bottom)."""
    ns = sorted(R18.FIRST + tuple(R18.MORE))
    r = R18.rack(ns)
    for n in R18.FIRST:
        r[n][0].set_stroke(opacity=0.85)
    out = {n: VGroup(r[n][0], r[n][1], C4.rack_knob(n), C4.rack_tick(n)) for n in ns}
    out["dots"] = R18.ellipses()
    if small:
        for v in out.values():
            v.scale(RACK_SCALE, about_point=ORIGIN).shift(RACK_SHIFT)
    return out


def rack_center(n: int) -> np.ndarray:
    return rack_pos([C4.rack_x(n), C4.RACK_Y, 0.0])


def rack_fill(n: int, c: complex, cmax: float, color=None) -> VGroup:
    """A filled slot: solid rim and an arm of the found size and angle."""
    col = color or color_of(n)
    r = C4.RACK_R * RACK_SCALE
    ctr = rack_center(n)
    v = r * c / cmax
    tip = ctr + np.array([v.real, v.imag, 0.0])
    g = VGroup(Circle(radius=r, color=col, stroke_width=2.5).move_to(ctr))
    if abs(v) > 0.03:
        g.add(Line(ctr, tip, color=S.ARM, stroke_width=2.5))
    g.add(Dot(tip, radius=0.04, color=S.INK))
    return g


# ── the rule card: spin → 0, still → stays ─────────────────────────────────
CARD_DOCK = np.array([-5.3, 2.35, 0.0])
ICON_R = 1.25


def card(now: float, center, spread: float, scale: float, frame_op: float, op: float = 1.0,
         left: float = 1.0, right: float = 1.0, lift: float = 0.0) -> VGroup:
    """Left icon: a spinning arm whose 12 dots average to its center (grey). Right icon: a still
    arm whose dots all sit at its tip (green). `lift` pulses both averages."""
    if op <= 0:
        return VGroup()
    c = np.asarray(center, float)
    r = ICON_R * scale
    g = VGroup()
    if frame_op > 0:
        g.add(RoundedRectangle(width=2 * spread + 2 * r + 0.5 * scale + 0.3, height=2 * r + 0.5 * scale + 0.25,
                               corner_radius=0.15, color=S.LINE, stroke_width=1.5)
              .set_fill(S.STAGE_RAISED, 0.9 * frame_op * op).set_stroke(opacity=frame_op * op).move_to(c))
    lc, rc = c + np.array([-spread, 0, 0]), c + np.array([spread, 0, 0])
    if left > 0:
        o = left * op
        a = TAU * 0.5 * now
        g.add(Circle(radius=r, color=S.FWD, stroke_width=2).move_to(lc).set_stroke(opacity=0.5 * o))
        for j in range(12):
            q = lc + r * np.array([np.cos(TAU * j / 12), np.sin(TAU * j / 12), 0])
            g.add(Dot(q, radius=0.045 * max(scale, 0.6), color=S.INK).set_opacity(0.8 * o))
        g.add(Line(lc, lc + r * np.array([np.cos(a), np.sin(a), 0]), color=S.ARM, stroke_width=2.5).set_stroke(opacity=o))
        g.add(Dot(lc, radius=(0.08 + 0.05 * lift) * max(scale, 0.6), color=S.LABEL_MUTED).set_opacity(o))
    if right > 0:
        o = right * op
        tip = rc + r * np.array([np.cos(0.7), np.sin(0.7), 0])
        g.add(Circle(radius=r, color=S.STILL, stroke_width=2).move_to(rc).set_stroke(opacity=0.25 * o))
        g.add(Line(rc, tip, color=S.STILL, stroke_width=3).set_stroke(opacity=o))
        g.add(Dot(tip, radius=(0.17 + 0.08 * lift) * max(scale, 0.6), color=S.STILL).set_opacity(0.3 * o),
              Dot(tip, radius=0.08 * max(scale, 0.6), color=S.STILL).set_opacity(o))
    return g


def card_docked(now: float, op: float = 1.0) -> VGroup:
    return card(now, CARD_DOCK, 0.95, 0.3, 1.0, op)


def card_lerp(now: float, u: float, big_center=(0.0, 0.3, 0.0), big_spread: float = 3.0, big_scale: float = 1.0,
              **kw) -> VGroup:
    """u = 0: the two big icons; u = 1: docked card."""
    e = u * u * (3 - 2 * u)
    c = (1 - e) * np.asarray(big_center, float) + e * CARD_DOCK
    return card(now, c, (1 - e) * big_spread + e * 0.95, (1 - e) * big_scale + e * 0.3, e, **kw)


# ── the speed dial (S22) ───────────────────────────────────────────────────
DIAL_AT = np.array([0.0, 3.25, 0.0])


def dial(k: int, op: float = 1.0) -> VGroup:
    txt = MathTex(r"n", "=", f"{k}" if k >= 0 else f"-{-k}", font_size=44, color=S.LABEL)
    txt[2].set_color(color_of(k) if k != 0 else S.LABEL)
    return txt.move_to(DIAL_AT).set_opacity(op)
