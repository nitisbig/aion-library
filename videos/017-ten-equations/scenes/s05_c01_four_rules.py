"""c01_s02 · Four rules (equation). Storyboard: plan/scene_plan.md § c01_s02. Layout L2: a stage on the left, the
laws stacking in the open right column.

Opens on c01_s01's last frame (the filings, camera pushed in) and pulls back to black. Maxwell's name tag lands on his
name. The stage then shows one picture per law, each computed from the physics it states:
  1. a + and − charge with their field lines traced by RK2 from Coulomb's law: lines start and end on charges;
  2. a bar magnet whose lines (pole model) close through the magnet, with a probe circle where in = out;
  3. a magnet pushed into a coil: the induced E swirl is as bright as the magnet is fast (∂B/∂t), so it vanishes
     when the magnet stops; on "power station" the magnet oscillates like a generator and the bulb lights;
  4. a charging capacitor: B rings around the wires (μ₀J) and around the empty gap, where only ∂E/∂t is changing.
The ∂E/∂t term is underlined in the E hue, never glowing (text does not glow).
"""
import math

import numpy as np
from aion import *

import sims as sm
from beats import T
from ch1 import SC, _magnet, _nail, filings_rgba, gap_rings, head as _head, laws, ring, underline_dEdt
from kit import chapter_backdrop, COL, P3, add_rail, mix, glimpse, sans, shade, smooth01, smooth_curve

STAGE_R = 2.45                                   # field lines end on an invisible circle this far out
MX, MY = sm.MAGNET_POS


# ------------------------------------------------------------------------------------------------ helpers
def _arc(path):
    seg = np.hypot(*np.diff(path, axis=0).T)
    return np.concatenate([[0.0], np.cumsum(seg)])


def _flow(paths, t, color, op, speed=0.55, spacing=0.75, r=0.03):
    """Dots drifting along field lines at a steady speed (pure in t)."""
    g = VGroup()
    if op <= 0.003:
        return g
    for path, s in paths:
        L = s[-1]
        n = max(1, int(L / spacing))
        for k in range(n):
            d = (speed * t + k * L / n) % L
            x, y = np.interp(d, s, path[:, 0]), np.interp(d, s, path[:, 1])
            g.add(Dot(P3(x, y), radius=r, color=color, fill_opacity=op))
    return g


def _mid_head(path, color, frac=0.5, op=1.0):
    s = _arc(path)
    i = int(np.searchsorted(s, s[-1] * frac))
    i = min(max(i, 1), len(path) - 2)
    return _head(path[i], path[i + 1] - path[i - 1], color, op=op)


def _line(path, color, width=2.4, op=0.85):
    pts = path[:: max(1, len(path) // 60)]
    if not np.allclose(pts[-1], path[-1]):
        pts = np.vstack([pts, path[-1]])
    return smooth_curve([tuple(p) for p in pts], color, width, op)


def _outside(p):
    return np.hypot(*(np.asarray(p) - SC)) > STAGE_R


# ------------------------------------------------------------------------------------------------ picture 1: charges
P_PLUS, P_MINUS = SC + [-1.15, 0.0], SC + [1.15, 0.0]
Q1 = [(*P_PLUS, 1.0), (*P_MINUS, -1.0)]


def _charge(p, sign):
    col = C.charge_p if sign > 0 else C.charge_n
    return VGroup(Circle(radius=0.27, stroke_width=0, fill_color=col, fill_opacity=1).move_to(P3(*p)),
                  MathTex("+" if sign > 0 else "-", font_size=34, color=C.bg).move_to(P3(*p)))


def _dipole_lines():
    out = []
    for a in np.linspace(0, 2 * np.pi, 18, endpoint=False) + np.pi / 18:
        st = P_PLUS + 0.3 * np.array([math.cos(a), math.sin(a)])
        out.append(sm.field_line(Q1, st, step=0.025, n=900, stop=_outside))
    for a in np.linspace(0, 2 * np.pi, 18, endpoint=False) + np.pi / 18:   # lines arriving at − from far away
        st = P_MINUS + 0.3 * np.array([math.cos(a), math.sin(a)])
        path = sm.field_line(Q1, st, step=0.025, n=900, sign=-1.0, stop=_outside)
        if _outside(path[-1]):
            out.append(path[::-1])
    return out


# ------------------------------------------------------------------------------------------------ picture 2: magnet
MH = 0.85                                                    # half length of the stage magnet
P_N, P_S = SC + [MH, 0.0], SC + [-MH, 0.0]
Q2 = [(*P_N, 1.0), (*P_S, -1.0)]


def _loop_lines():
    """Outside lines from N to S (pole model) that close within the stage, plus the return path through the bar."""
    def away(p):                                             # the stage box: clear of the name tag and the rail
        return abs(p[0] - SC[0]) > 3.3 or abs(p[1] - SC[1]) > 2.45

    out = []
    for a in np.radians([70, 77, 85, 95, 108, 125]):
        for sg in (1, -1):
            st = P_N + 0.16 * np.array([math.cos(a), sg * math.sin(a)])
            path = sm.field_line(Q2, st, step=0.02, n=2500, stop=away)
            if np.hypot(*(path[-1] - P_S)) < 0.2:
                out.append(np.vstack([P_N, path, P_S]))
    inner = [np.linspace(P_S + [0, dy], P_N + [0, dy], 40) for dy in (-0.13, 0.13)]
    return out, inner


def _stage_magnet():
    w, h = 2 * MH, 0.4
    s_half = Rectangle(width=w / 2, height=h, stroke_color=C.mass, stroke_width=2.5, fill_color=C.mass,
                       fill_opacity=0.28).move_to(P3(SC[0] - w / 4, SC[1]))
    n_half = Rectangle(width=w / 2, height=h, stroke_color=C.b_field, stroke_width=2.5, fill_color=C.b_field,
                       fill_opacity=0.28).move_to(P3(SC[0] + w / 4, SC[1]))
    lab = VGroup(MathTex("S", font_size=24, color=C.text).move_to(P3(SC[0] - w / 4, SC[1])),
                 MathTex("N", font_size=24, color=C.text).move_to(P3(SC[0] + w / 4, SC[1])))
    return VGroup(s_half, n_half, lab)


# ------------------------------------------------------------------------------------------------ picture 3: coil
CYC = SC[1] + 0.55                                           # coil axis height
XA, XB, RC_ = SC[0] - 0.55, SC[0] + 1.05, 0.62               # coil ends and radius
BULB = np.array([SC[0] + 0.25, -1.8])
MAG3_HALF = 0.55
X_START, X_IN = -5.2, XA - MAG3_HALF + 0.55                  # magnet centre: start, pushed in (N end inside)


def _mag3_x(t):
    """Magnet centre x(t): pushed into the coil on 'changing magnetic', then (from 'power station') driven in and
    out like a generator. Pure in t."""
    t1 = float(T.c01_s02_changing_magnetic) + 0.15
    u = smooth01((t - t1) / 1.5)
    x = X_START + (X_IN - X_START) * u
    tp = float(T.c01_s02_power_station) - 0.25
    if t > tp:
        amp = 0.9 * smooth01((t - tp) / 0.8)
        x -= amp * (1 - math.cos(2 * math.pi * 0.85 * (t - tp))) / 2
    return x


def _mag3_v(t, h=1 / 120):
    return (_mag3_x(t + h) - _mag3_x(t - h)) / (2 * h)


def _helix():
    th = np.linspace(0, 12 * np.pi, 700)
    x = XA + (XB - XA) * th / (12 * np.pi) + 0.1 * np.sin(th)
    y = CYC - RC_ * np.cos(th)
    return smooth_curve(list(zip(x[::4], y[::4])) + [(x[-1], y[-1])], C.mass, 3.0, 1.0)


def _leads():
    yb = BULB[1]
    left = [(XA, CYC - RC_), (XA, yb), (BULB[0] - 0.3, yb)]
    right = [(XB, CYC - RC_), (XB, yb), (BULB[0] + 0.3, yb)]
    bulb = Circle(radius=0.3, stroke_color=C.mass, stroke_width=2.5).move_to(P3(*BULB))
    fil = VMobject(stroke_color=C.mass, stroke_width=2)
    fil.set_points_as_corners([P3(BULB[0] + dx, BULB[1] + dy) for dx, dy in
                               [(-0.3, 0), (-0.14, 0), (-0.08, 0.1), (0, -0.1), (0.08, 0.1), (0.14, 0), (0.3, 0)]])
    wires = VGroup(*[VMobject(stroke_color=C.mass, stroke_width=2.5).set_points_as_corners([P3(*p) for p in pts])
                     for pts in (left, right)])
    return VGroup(wires, bulb, fil)


def _mag3(t, op):
    x = _mag3_x(t)
    w, h = 2 * MAG3_HALF, 0.34
    g = VGroup(Rectangle(width=w / 2, height=h, stroke_width=0, fill_color=C.mass, fill_opacity=op)
               .move_to(P3(x - w / 4, CYC)),
               Rectangle(width=w / 2, height=h, stroke_width=0, fill_color=C.b_field, fill_opacity=op)
               .move_to(P3(x + w / 4, CYC)),
               MathTex("N", font_size=24, color=C.bg).set_opacity(op).move_to(P3(x + w / 4, CYC)))
    # the magnet's B, carried into the coil: brighter the deeper the magnet sits
    xn = x + MAG3_HALF
    depth = float(smooth01((xn - (XA - 1.2)) / 1.4))
    for dy in (-0.22, 0.0, 0.22):
        g.add(Line(P3(xn, CYC + dy * 0.5), P3(XB + 0.5, CYC + dy), stroke_color=C.b_field, stroke_width=2,
                   stroke_opacity=op * depth * 0.8))
    return g


def _swirl(t, op):
    """The induced E: rings around the coil axis, bright in proportion to the magnet's speed; arrowheads advance by
    the magnet's displacement (so they reverse when it reverses)."""
    v = _mag3_v(t)
    a = op * float(np.clip(abs(v) / 1.6, 0, 1))
    g = VGroup()
    if a < 0.01:
        return g
    ph = 2.6 * (_mag3_x(t) - X_START)
    for xc in (XA + 0.45, XB - 0.45):
        g.add(Ellipse(width=0.5, height=2 * RC_ + 0.75, stroke_color=C.e_field, stroke_width=3,
                      stroke_opacity=a).move_to(P3(xc, CYC)))
        for k in range(3):
            th = ph + 2 * np.pi * k / 3
            p = np.array([xc + 0.25 * math.sin(th), CYC + (RC_ + 0.375) * math.cos(th)])
            d = np.array([0.25 * math.cos(th), -(RC_ + 0.375) * math.sin(th)]) * (1 if v >= 0 else -1)
            g.add(_head(p, d, C.e_field, size=0.15, op=a))
    return g


# ------------------------------------------------------------------------------------------------ picture 4: capacitor
GAP = 0.45
PL, PR = SC[0] - GAP, SC[0] + GAP


def _capacitor():
    h = 1.7
    plates = VGroup(Line(P3(PL, SC[1] - h / 2), P3(PL, SC[1] + h / 2), stroke_color=C.mass, stroke_width=6),
                    Line(P3(PR, SC[1] - h / 2), P3(PR, SC[1] + h / 2), stroke_color=C.mass, stroke_width=6))
    wires = VGroup(Line(P3(SC[0] - 2.4, SC[1]), P3(PL, SC[1]), stroke_color=C.mass, stroke_width=3),
                   Line(P3(PR, SC[1]), P3(SC[0] + 2.4, SC[1]), stroke_color=C.mass, stroke_width=3))
    return VGroup(wires, plates)


def _charging(t):
    return float(smooth01((t - float(T.c01_s02_changing_electric) - 0.2) / 3.2))


def _cap_live(t, op):
    q = _charging(t)
    g = VGroup()
    if op < 0.01:
        return g
    # current in the wires: charges drifting towards the plates while it charges
    for side in (-1, 1):
        x0, x1 = (SC[0] - 2.4, PL) if side < 0 else (PR, SC[0] + 2.4)
        for k in range(4):
            x = x0 + ((0.55 * t + k / 4 * (x1 - x0)) % (x1 - x0))
            g.add(Dot(P3(x, SC[1]), radius=0.032, color=C.light, fill_opacity=op * 0.9))
    # charge piling up on the plates
    n = int(round(4 * q))
    for i in range(n):
        y = SC[1] + (0.7, -0.7, 0.36, -0.36)[i]
        g.add(MathTex("+", font_size=24, color=C.charge_p).set_opacity(op).move_to(P3(PL - 0.2, y)),
              MathTex("-", font_size=24, color=C.charge_n).set_opacity(op).move_to(P3(PR + 0.2, y)))
    # E between the plates grows with the charge
    for y in (-0.55, -0.18, 0.18, 0.55):
        if q > 0.03:
            g.add(Arrow(P3(PL + 0.06, SC[1] + y), P3(PL + 0.06 + (2 * GAP - 0.12) * max(q, 0.2), SC[1] + y), buff=0,
                        stroke_width=2.5, color=C.e_field, max_tip_length_to_length_ratio=0.3)
                  .set_opacity(op * q))
    return g


def _b_rings(t, op):
    """B circling the wires (from J); the rings circling the empty gap (from ∂E/∂t) are `gap_rings`."""
    t4 = float(T.c01_s02_changing_electric)
    a = op * float(smooth01((t - t4 - 0.9) / 0.9))
    g = VGroup()
    if a < 0.01:
        return g
    for xc in (SC[0] - 1.65, SC[0] + 1.65):
        g.add(ring(xc, SC[1], 0.42, 0.95, C.b_field, 1.6 * (t - t4), a * 0.75))
    return g


# ------------------------------------------------------------------------------------------------ the scene
@scene(T.c01_s02, T.c01_s03)
def s05_c01_four_rules(s):
    s.solid(C.bg, z=-200)
    chapter_backdrop(s, 1)
    add_rail(s, 1)

    # open on c01_s01's last frame (filings, pushed in) and pull back to an empty stage
    s.camera.base.update(x=MX - 0.2, y=MY, zoom=1.5)
    s.camera.frame(T.c01_s02 + 0.7, center=(0, 0), zoom=1.0, dur=2.8)
    s.add(ArrayLayer(filings_rgba(), height=8.0, pos=(0, 0), z=-10,
                     opacity=fade(T.c01_s02 - 5, dur=0.1, out=T.c01_s02 + 1.4, out_dur=1.6)))
    m = s.manim(z=5)
    prop = VGroup(_magnet(), _nail(MX + sm.MAGNET_HALF + 0.56, MY, 0.0))
    m.add(prop)
    m.play(FadeOut(prop), at=T.c01_s02 + 1.3, dur=1.4)

    hud = s.manim(z=50, parallax=0.0)
    glimpse(s, "maxwell", T.c01_s02_maxwell, C.maxwell)

    # the right column: each law writes as it is spoken; earlier ones step back
    col = s.manim(z=20, parallax=0.0)
    rows = laws()
    when = [T.c01_s02_spread_outward, T.c01_s02_never_begin, T.c01_s02_changing_magnetic, T.c01_s02_changing_electric]
    for i, ((e, tag), at) in enumerate(zip(rows, when)):
        col.play(Write(e), at=at, dur=1.3)
        col.play(FadeIn(tag, shift=0.08 * UP), at=at + 0.9, dur=0.5)
        if i:
            pe, pt = rows[i - 1]
            col.play(VGroup(pe, pt).animate.set_opacity(0.42), at=at, dur=0.6)
    under = underline_dEdt(rows[3][0])
    col.play(Create(under), at=T.c01_s02_changing_electric + 1.9, dur=0.6)

    # 1 · charges: field lines start on + and end on −
    t1, t1o = T.c01_s02_spread_outward, T.c01_s02_never_begin
    op1 = fade(t1 - 0.9, out=t1o, out_dur=0.7)
    lines1 = _dipole_lines()
    curves1 = VGroup(*[_line(p, C.e_field) for p in lines1])
    heads1 = VGroup(*[_mid_head(p, C.e_field, frac=0.42) for p in lines1])
    charges = VGroup(_charge(P_PLUS, 1), _charge(P_MINUS, -1))
    m.play(FadeIn(charges, scale=0.8), at=t1 - 0.9, dur=0.6)
    m.play(LaggedStart(*[Create(c) for c in curves1], lag_ratio=0.03), at=t1, dur=1.8)
    m.play(FadeIn(heads1), at=t1 + 1.2, dur=0.6)
    flow1 = [(p, _arc(p)) for p in lines1]
    s.manim(z=6).redraw(lambda t: _flow(flow1, t, mix(C.e_field, C.light, 0.55), float(op1(t)) * 0.9),
                        during=(t1 - 1.0, t1o + 1.2))
    m.play(FadeOut(VGroup(curves1, heads1, charges)), at=t1o, dur=0.7)

    # 2 · magnet: every line closes through the bar; a probe circle counts in = out
    t2, t2o = T.c01_s02_never_begin, T.c01_s02_changing_magnetic
    op2 = fade(t2 + 0.2, out=t2o, out_dur=0.7)
    loops, inner = _loop_lines()
    curves2 = VGroup(*[_line(p, C.b_field) for p in loops], *[_line(p, C.b_field, op=0.6) for p in inner])
    heads2 = VGroup(*[_mid_head(p, C.b_field) for p in loops])
    bar = _stage_magnet()
    m.play(FadeIn(bar), at=t2 + 0.2, dur=0.6)
    m.play(LaggedStart(*[Create(c) for c in curves2], lag_ratio=0.05), at=t2 + 0.5, dur=2.0)
    m.play(FadeIn(heads2), at=t2 + 1.8, dur=0.6)
    flow2 = [(p, _arc(p)) for p in loops + inner]
    s.manim(z=6).redraw(lambda t: _flow(flow2, t, mix(C.b_field, C.light, 0.5), float(op2(t)) * 0.9),
                        during=(t2, t2o + 1.2))
    probe = DashedVMobject(Circle(radius=0.55, stroke_color=C.text, stroke_width=2.2).move_to(P3(*P_N)),
                           num_dashes=26)
    lab = sans("in = out", 24, C.text).move_to(P3(P_N[0] + 0.95, P_N[1] + 0.8))
    shade(s, lab.get_center()[0], lab.get_center()[1], lab.width + 0.3, lab.height + 0.2, a=0.85, z=7,
          opacity=fade(T.c01_s02_loops, out=t2o, out_dur=0.7))
    m2 = s.manim(z=8)
    m2.play(Create(probe), at=T.c01_s02_loops, dur=0.7)
    m2.play(FadeIn(lab), at=T.c01_s02_loops + 0.4, dur=0.5)
    m2.play(FadeOut(VGroup(probe, lab)), at=t2o, dur=0.7)
    m.play(FadeOut(VGroup(curves2, heads2, bar)), at=t2o, dur=0.7)

    # 3 · magnet into a coil: E swirls only while B changes; the generator lights the bulb
    t3, t3o = T.c01_s02_changing_magnetic, T.c01_s02_changing_electric
    op3 = fade(t3 - 0.3, out=t3o, out_dur=0.7)
    s.manim(z=4).redraw(lambda t: _mag3(t, float(op3(t))), during=(t3 - 0.6, t3o + 1.2))
    coil = VGroup(_helix(), _leads())
    c3 = s.manim(z=6)
    c3.play(FadeIn(coil), at=t3 - 0.3, dur=0.7)
    c3.play(FadeOut(coil), at=t3o, dur=0.7)
    s.manim(z=7).redraw(lambda t: _swirl(t, float(op3(t))), during=(t3 - 0.3, t3o + 1.2))

    def bulb(t):
        b = float(op3(t)) * float(np.clip(abs(_mag3_v(t)) / 1.6, 0, 1))
        b = max(b, float(op3(t)) * 0.55 * float(smooth01((t - float(T.c01_s02_power_station)) / 0.6)))
        return Circle(radius=0.24, stroke_width=0, fill_color=C.light, fill_opacity=b).move_to(P3(*BULB))
    s.manim(z=8, fx=[Glow(C.light, strength=C.glow * 1.2, radius=C.glow_r)]) \
        .redraw(bulb, during=(t3 - 0.3, t3o + 1.2))

    # 4 · a charging capacitor: B circles the gap where no charge flows, only E changes
    t4 = T.c01_s02_changing_electric
    op4 = fade(t4 - 0.2, out=s.end - 0.5, out_dur=0.5)          # all but the gap rings leave: c01_s03 starts there
    cap = _capacitor()
    m.play(FadeIn(cap), at=t4 - 0.2, dur=0.7)
    m.play(FadeOut(cap), at=s.end - 0.5, dur=0.5)
    s.manim(z=6).redraw(lambda t: _cap_live(t, float(op4(t))), during=(t4 - 0.3, s.end))
    s.manim(z=7).redraw(lambda t: _b_rings(t, float(op4(t))), during=(t4 - 0.3, s.end))
    s.manim(z=7).redraw(lambda t: gap_rings(t, 1.0), during=(t4 - 0.3, s.end))

    # a slow drift while the pictures change
    s.camera.frame(T.c01_s02_spread_outward, center=(-0.25, 0.0), zoom=1.04, dur=9.0)
    s.camera.frame(T.c01_s02_changing_magnetic, center=(0.0, 0.0), zoom=1.0, dur=6.0)
