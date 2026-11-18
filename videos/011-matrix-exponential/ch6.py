"""Shared state for the ch6 globe (s23 → s25): one spin, one placement, one pole tilt, so the cuts are seamless."""
import numpy as np

from aion import *
from beats import T
from shots import arrow, field_arrows, lab, p3, spin_theta, tex

T_SPIN = T.cut_earth


def theta(t):
    return spin_theta(t, T_SPIN)


def _stages(t, v, stages):
    v = np.asarray(v, float)
    for a, b, target in stages:
        u = smooth(float(np.clip((t - a) / (b - a), 0.0, 1.0)))
        v = v + (np.asarray(target, float) - v) * u
    return v


def center(t):
    return _stages(t, (0.0, -0.1), [(T.K_matrix - 0.4, T.K_matrix + 1.0, (-3.7, -0.2)),
                                    (T.exp_K - 0.2, T.exp_K + 1.2, (-4.85, 1.0))])


def radius(t):
    return float(_stages(t, 1.9, [(T.cut_earth + 0.2, T.beautiful + 2.6, 3.25),
                                  (T.K_matrix - 0.4, T.K_matrix + 1.0, 2.6),
                                  (T.exp_K - 0.2, T.exp_K + 1.2, 1.85)]))


def pole(t):
    return float(_stages(t, 0.0, [(T.pole - 0.2, T.pole + 1.3, 1.0), (T.K_matrix - 0.4, T.K_matrix + 1.0, 0.0)]))


# ---------------------------------------------------------------- the pill (s21, s22): body | state plane | numbers
from shots import CAST as _CAST  # noqa: E402

PILL = _CAST["pill"]
KA, KE = -PILL[0, 0], -PILL[1, 1]
PO2, PU = np.array([-1.55, -2.05]), 3.05             # state plane: origin and unit (s across, b up)
BO, BW, BH, HMAX = np.array([2.35, -3.35]), 4.5, 3.4, 12.0   # blood-level plot: origin, width (12 h), height per unit
SEC_PER_HOUR = 1.15


def state(h):
    from scipy.linalg import expm
    return expm(h * PILL) @ np.array([1.0, 0.0])


def b_level(h):
    h = np.asarray(h, float)
    return KA / (KA - KE) * (np.exp(-KE * h) - np.exp(-KA * h))


H_PEAK = float(np.log(KA / KE) / (KA - KE))           # 1.85 h


def plane_axes():
    o = PO2
    ax = VGroup(Arrow(p3(o), p3(o + [PU * 1.12, 0]), buff=0, color=C.muted, stroke_width=C.thin + 0.6, tip_length=0.14),
                Arrow(p3(o), p3(o + [0, PU * 1.05]), buff=0, color=C.muted, stroke_width=C.thin + 0.6, tip_length=0.14))
    tick = VGroup(*[Line(p3(o + [PU, -0.08]), p3(o + [PU, 0.08]), color=C.muted, stroke_width=C.thin + 0.4),
                    Line(p3(o + [-0.08, PU]), p3(o + [0.08, PU]), color=C.muted, stroke_width=C.thin + 0.4)])
    sl = VGroup(tex("s", size=36, color=C.dose), lab("stomach", 24, C.dose)).arrange(RIGHT, buff=0.12).next_to(
        p3(o + [PU * 1.12, 0]), DOWN, buff=0.18).shift(0.4 * LEFT)
    bl = VGroup(tex("b", size=36, color=C.flow), lab("blood", 24, C.flow)).arrange(RIGHT, buff=0.12).next_to(
        p3(o + [0, PU * 1.05]), RIGHT, buff=0.15)
    return VGroup(ax, tick, sl, bl)


def pill_field():
    box = (PO2[0] + 0.05, PO2[1] + 0.05, PO2[0] + PU * 1.05, PO2[1] + PU * 0.98)
    return field_arrows(PILL, center=PO2, unit=PU, box=box, spacing=0.5, opacity=0.9)


def pill_matrix():
    A = Mat([["-k_a", "0"], ["k_a", "-k_e"]], colors=C.gen, size=36, h_buff=1.05, v_buff=0.68)
    num = Mat([["-1", "0"], ["1", r"-\tfrac14"]], colors=C.gen, size=34, h_buff=0.9, v_buff=0.68)
    g = VGroup(tex("A", "=", size=40, colors={0: C.gen}), A, tex("=", size=40), num).arrange(RIGHT, buff=0.18)
    return g.move_to([4.3, 2.75, 0])


def hero():
    h = tex(r"\mathbf x(t)", "=", r"e^{tA}", r"\,\mathbf x_0", size=58, colors={0: C.vec, 2: C.flow, 3: C.vec})
    h[2][2].set_color(C.gen)
    return h.move_to([4.65, 1.05, 0])


# ---------------------------------------------------------------- globe overlays shared by s23–s25
from shots import AXIS_N, body_to_world, gproj, latlon, sphere_curve  # noqa: E402

EQ = np.array([latlon(0, L) for L in np.linspace(0, 360, 145)])


def globe_frame(t, op=1.0):
    """The purple spin axis and the teal equator, projected with the globe."""
    c, R, pl = center(t), radius(t), pole(t)
    ax, _ = gproj(np.array([-1.3 * AXIS_N, 1.3 * AXIS_N]), c, R, pl)
    return VGroup(Line(p3(ax[0]), p3(ax[1]), color=C.eigen, stroke_width=C.stroke, stroke_opacity=op),
                  sphere_curve(EQ @ body_to_world(theta(t)).T, c, R, pl, C.flow, C.stroke, op=op))


def facing_lon(lat, t):
    """The body longitude that faces the viewer most directly at time t."""
    lons = np.linspace(-180, 180, 721)
    W = np.array([latlon(lat, L) for L in lons]) @ body_to_world(theta(t)).T
    _, d = gproj(W, center(t), radius(t), pole(t))
    return float(lons[np.argmax(d)])
