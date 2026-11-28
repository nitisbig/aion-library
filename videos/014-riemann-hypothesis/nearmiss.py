"""s20's builders, shared with s21 (which opens on s20's last frame): Z(t) near height 7005, the magnified panel's
wave, and the Lambda slider against its wall at 0."""
from types import SimpleNamespace
from functools import lru_cache

from aion import *

from look import caps, lab, pin, seen, tex
from zmath import hardy_Z

MX0, MX1, MY, MS = -6.2, 6.2, 1.75, 0.15     # the main plot: x of 6995 and 7015, the axis, units per unit of Z
T0, T1 = 6995.0, 7015.0
PX0, PX1, PY0, PY1 = -6.2, 3.0, -3.4, -0.3   # the magnified panel
Z0, Z1, W0, W1 = -0.016, 0.008, 7005.035, 7005.13   # its Z range and t range
IX0, IX1 = 3.5, 6.4                          # the inset strip panel (same height as the magnified panel)
IXC, IU = (3.5 + 6.4) / 2, 1.2               # its line Re s = 1/2, and units per 1 of real part
G1, G2 = 7005.062866175261, 7005.100564672268    # zeros #6709 and #6710 (verify.py)
GHOST = 0.005


@lru_cache(maxsize=1)
def wide():
    t = np.linspace(T0, T1, 4001)
    return t, hardy_Z(t)


@lru_cache(maxsize=1)
def close():
    t = np.linspace(W0, W1, 1501)
    return t, hardy_Z(t)


def crossings(t, z):
    i = np.where(np.sign(z[:-1]) != np.sign(z[1:]))[0]
    return t[i] - z[i] * (t[i + 1] - t[i]) / (z[i + 1] - z[i])


def mx(t):
    return MX0 + (MX1 - MX0) * (np.asarray(t, float) - T0) / (T1 - T0)


def px(t):
    return PX0 + (PX1 - PX0) * (np.asarray(t, float) - W0) / (W1 - W0)


def py(z):
    return PY0 + (PY1 - PY0) * (np.asarray(z, float) - Z0) / (Z1 - Z0)


PAX = float(py(0.0))                         # the panel's axis


def panel_curve(shift, color, width=2.6, dots=True):
    """The magnified wave, lowered by `shift`, clipped to the panel, with its crossings marked."""
    t, z = close()
    z = z - shift
    zc = np.clip(z, Z0, Z1)
    v = VMobject(color=color, stroke_width=width)
    v.set_points_as_corners(np.column_stack([px(t), py(zc), 0 * t]))
    g = VGroup(v)
    if dots:
        for c in crossings(t, z):
            g.add(Dot([float(px(c)), PAX, 0], radius=0.07, color=C.zero))
    return g


TX, TY, TS = 0.0, -2.55, 8.0                 # the slider track: x of Lambda = 0, its height, units per unit of Lambda


def main_plot():
    """Z(t) on 6995-7015 with its crossings, and Lehmer's name. Parts .axis .curve .zl .pings .who"""
    t, z = wide()
    axis = VGroup(Line([MX0, MY, 0], [MX1, MY, 0], color=C.axis, stroke_width=1.8),
                  *[tex(lb, size=24, color=C.muted).move_to([float(mx(v)), MY - 1.35, 0])
                    for v, lb in ((6995, "6995"), (7005, "7005"), (7015, "7015"))],
                  tex("t", size=28, color=C.muted).move_to([MX1 + 0.2, MY, 0]))
    curve = VMobject(color=C.text, stroke_width=2.2)
    curve.set_points_as_corners(np.column_stack([mx(t), MY + MS * z, 0 * t]))
    zl = tex(r"Z(t)", size=34).move_to([MX0 + 0.45, MY + 1.35, 0])
    pings = VGroup(*[Dot([float(mx(c)), MY, 0], radius=0.05, color=C.zero) for c in crossings(t, z)])
    who = caps(r"D. H. Lehmer $\cdot$ 1956", 34, C.ink)
    pin(who, top=3.55, left=MX1 - 3.4)
    return SimpleNamespace(axis=axis, curve=curve, zl=zl, pings=pings, who=who)


def knob_mob(lam):
    x = TX + TS * float(lam)
    return VGroup(Dot([x, TY, 0], radius=0.13, color=C.text), tex(r"\Lambda", size=30).move_to([x, TY + 0.62, 0]))


def slider():
    """The Lambda slider and its two statements. Parts .row1 (<=) .row1b (=) .track .out_zone .wall .ruled .row2
    .iftrue"""
    row1 = tex(r"\mathrm{RH}", r"\iff", r"\Lambda", r"\le", r"0", size=42)
    pin(row1, top=-0.3, left=-6.2)
    row1b = tex(r"\mathrm{RH}", r"\iff", r"\Lambda", r"=", r"0", size=42).move_to(row1)
    track = VGroup(Line([TX - 4.0, TY, 0], [TX + 4.0, TY, 0], color=C.muted, stroke_width=2.4),
                   tex("0", size=28, color=C.muted).move_to([TX, TY - 0.62, 0]),
                   tex(r"\Lambda", size=30, color=C.muted).move_to([TX + 4.35, TY, 0]))
    out_zone = Rectangle(width=4.0, height=0.6, stroke_width=0, fill_color=C.gap, fill_opacity=seen(0.3))
    out_zone.move_to([TX - 2.0, TY, 0])
    wall = Line([TX, TY - 0.35, 0], [TX, TY + 0.35, 0], color=C.text, stroke_width=6)
    ruled = lab("ruled out", 24, C.text).move_to([TX - 2.0, TY + 0.6, 0])
    row2 = VGroup(tex(r"\Lambda\ge0", size=38), caps(r"B. Rodgers \& T. Tao $\cdot$ 2018", 30, C.ink))
    row2.arrange(RIGHT, buff=0.4, aligned_edge=DOWN)
    pin(row2, top=-1.05, left=-6.2)
    iftrue = lab("if RH", 26, C.muted).move_to([TX + 2.4, TY - 0.62, 0])
    return SimpleNamespace(row1=row1, row1b=row1b, track=track, out_zone=out_zone, wall=wall, ruled=ruled, row2=row2,
                           iftrue=iftrue)


def end_frame():
    """s20's last frame as (plot layer, label layer) lists, each in s20's draw order."""
    M, S = main_plot(), slider()
    plot = [M.axis, M.curve, M.zl, M.pings, S.track, S.out_zone, S.wall, knob_mob(0.0)]
    hud = [M.who, S.row2, S.ruled, S.iftrue, S.row1b]
    return plot, hud
