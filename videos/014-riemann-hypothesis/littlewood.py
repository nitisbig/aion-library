"""s18's builders, shared with s19 (which opens on s18's last frame): the line of zeros with its squeezed bracket, and
the scaled error pi(x) - li(x) on a log axis (real data to 10^6, schematic past it)."""
from functools import lru_cache
from types import SimpleNamespace

from aion import *

from look import GAM, R_DOT, TOP_INF, ZS, ZX, ZY0, caps, carded, lab, pin, seen, tex
from zmath import li, prime_pi

PX0, PX1 = -6.0, 3.9                         # Manim x of 10^1 and of the right end
Y0, VS = 0.6, 0.8                            # Manim y of zero, and units per unit of the scaled error
YB = -2.5                                    # the bottom axis
K_END = 330.0                                # the axis after the zoom: 10^1 .. 10^330
K_NOFLIP, K_FLIP = 19.0, 316.0 + np.log10(1.397)   # Buthe 2015; Saouter-Demichel 2010
BR_TOP = 3.4                                 # the bracket's top before the squeeze
SQUEEZE = 0.03
SHOWN = GAM[ZY0 + ZS * GAM <= BR_TOP]        # the dots inside the bracket


@lru_cache(maxsize=1)
def real():
    x = np.logspace(1, 6, 1500)
    return np.log10(x), (prime_pi(x) - li(x)) * np.log(x) / np.sqrt(x)


def schematic(k):
    """Past 10^6: drawn, not computed. Below zero, wobbling, until one known flip near 1.4 x 10^316."""
    k = np.asarray(k, float)
    v = -1.75 + 0.3 * np.sin(2 * np.pi * (k - 6) / 29.0) + 0.12 * np.sin(2 * np.pi * (k - 6) / 11.3)
    return v + 3.2 * np.exp(-((k - K_FLIP) / 0.9) ** 2)


@lru_cache(maxsize=None)
def _klab(k):
    return tex("10" if k == 1 else r"10^{%d}" % k, size=24, color=C.muted)


@lru_cache(maxsize=1)
def _zero():
    return tex("0", size=24, color=C.muted).move_to([PX0 - 0.2, Y0, 0])


def sx_of(km):
    return lambda k: PX0 + (PX1 - PX0) * (np.asarray(k, float) - 1) / (km - 1)


def sy(v):
    return Y0 + VS * np.asarray(v, float)


def zline():
    return Line([ZX, ZY0, 0], [ZX, TOP_INF, 0], color=C.crit, stroke_width=2.0, stroke_opacity=0.75)


def bracket(top):
    x = ZX - 0.22
    v = VMobject(color=C.text, stroke_width=2.4)
    v.set_points_as_corners([[x + 0.1, ZY0, 0], [x, ZY0, 0], [x, top, 0], [x + 0.1, top, 0]])
    return v


def marks(c):
    """The checked dots and their bracket, squeezed toward the base by c (1 = full height)."""
    dots = VGroup(*[Dot([ZX, ZY0 + c * ZS * g, 0], radius=R_DOT * (1.0 if c > 0.5 else 0.8), color=C.zero)
                    for g in SHOWN])
    return VGroup(dots, bracket(ZY0 + c * (BR_TOP - ZY0)))


def plot_mob(km, kd, a19):
    """The plot with the axis out to 10^km, the real data drawn to 10^kd, and the 10^19 tick at opacity a19."""
    sx = sx_of(km)
    g = VGroup(Line([PX0, YB, 0], [PX1 + 0.1, YB, 0], color=C.axis, stroke_width=2.0),
               Line([PX0, YB, 0], [PX0, 2.0, 0], color=C.axis, stroke_width=2.0),
               DashedLine([PX0, Y0, 0], [PX1, Y0, 0], color=C.muted, stroke_width=1.6, dash_length=0.08),
               _zero().copy())
    ks = [1] + [int(k) for k in (range(2, 7) if km < 7 else np.arange(100, km + 1e-9, 100))]
    for k in ks:
        g.add(_klab(k).copy().move_to([float(sx(k)), YB - 0.3, 0]))
    k, v = real()
    keep = k <= kd
    if keep.sum() >= 2:
        rc = VMobject(color=C.gap, stroke_width=2.4)
        rc.set_points_as_corners(np.column_stack([sx(k[keep]), sy(v[keep]), 0 * k[keep]]))
        g.add(rc)
    if km > 6.05:
        kk = np.union1d(np.linspace(6, km, 1500), np.linspace(K_FLIP - 3, K_FLIP + 3, 400))
        kk = kk[kk <= km]
        sc = VMobject(color=C.gap, stroke_width=2.2)
        sc.set_points_as_corners(np.column_stack([sx(kk), sy(schematic(kk)), 0 * kk]))
        g.add(DashedVMobject(sc, num_dashes=90, dashed_ratio=0.6))
    if a19 > 0 and km >= K_NOFLIP:
        x19 = float(sx(K_NOFLIP))
        tick = DashedLine([x19, YB, 0], [x19, 1.8, 0], color=C.muted, stroke_width=1.6, dash_length=0.06)
        lb = VGroup(tex(r"10^{19}", size=30), lab("no flip below", 24, C.muted)).arrange(DOWN, buff=0.08,
                                                                                     aligned_edge=LEFT)
        lb.move_to([x19 + 0.15 + lb.width / 2, 1.55, 0])
        g.add(tick.set_opacity(a19), lb.set_opacity(a19))
    return g


def labels():
    """Every label of s18, in their final places (chk is at its starting place; .chk_end is where it ends)."""
    chk = carded(VGroup(tex(r"10^{13}", size=36), lab("checked", 26, C.muted)).arrange(DOWN, buff=0.1), opacity=1.0)
    chk.move_to([ZX - 0.45 - chk.width / 2, 0.0, 0])
    chk_end = np.array([ZX - 0.45 - chk.width / 2, ZY0 + 0.45, 0])
    inf = tex(r"\infty", size=44, color=C.crit).move_to([ZX - 0.45, 3.0, 0])
    ylab = tex(r"(\pi(x)-\mathrm{li}(x))\,\frac{\ln x}{\sqrt x}", size=28, color=C.gap)
    ylab.move_to([PX1 - ylab.width / 2, Y0 - 2.45, 0])
    below = VGroup(tex(r"\pi(x)", r"<", r"\mathrm{li}(x)", size=40, colors={0: C.prime, 2: C.smooth}),
                   lab("for every $x$ checked", 30, C.text)).arrange(RIGHT, buff=0.35, aligned_edge=DOWN)
    pin(below, top=3.5, left=PX0)
    who = caps(r"J. E. Littlewood $\cdot$ 1914", 34, C.ink)
    pin(who, top=3.5, left=PX1 + 0.3 - who.width)
    flips = VGroup(tex(r"\pi(x)-\mathrm{li}(x)", size=40, color=C.gap),
                   lab("changes sign infinitely often", 30, C.text)).arrange(RIGHT, buff=0.35, aligned_edge=DOWN)
    pin(flips, top=2.8, left=PX0)
    sch = lab("schematic", 26, C.muted).move_to([-3.4, sy(-1.75) + 0.8, 0])
    sx = sx_of(K_END)
    xf = float(sx(K_FLIP))
    mark = Line([xf, YB, 0], [xf, 1.9, 0], color=C.text, stroke_width=2.0)
    flip_lab = VGroup(tex(r"1.4\times10^{316}", size=30), lab("a known flip", 24, C.muted))
    flip_lab.arrange(DOWN, buff=0.08, aligned_edge=RIGHT).move_to([xf - 0.15, 1.55, 0], aligned_edge=RIGHT)
    band = Rectangle(width=xf - float(sx(K_NOFLIP)), height=1.8 - YB, stroke_width=0, fill_color=C.gap,
                     fill_opacity=seen(0.1)).move_to([(xf + float(sx(K_NOFLIP))) / 2, (1.8 + YB) / 2, 0])
    first = lab("the first flip: somewhere in here", 26, C.text).move_to([band.get_x() - 0.4, -2.0, 0])
    return SimpleNamespace(chk=chk, chk_end=chk_end, inf=inf, ylab=ylab, below=below, who=who, flips=flips, sch=sch,
                           mark=mark, flip_lab=flip_lab, band=band, first=first)


def end_frame():
    """s18's last frame as (plot layer, zeros layer, label layer) lists, each in s18's draw order."""
    lb = labels()
    lb.chk.move_to(lb.chk_end)
    lb.below.set_opacity(0.45)
    plot = [plot_mob(K_END, 6.0, 1.0), lb.mark, lb.band]
    zeros = [zline(), marks(SQUEEZE)]
    hud = [lb.chk, lb.inf, lb.ylab, lb.below, lb.who, lb.flips, lb.sch, lb.flip_lab, lb.first]
    return plot, zeros, hud, lb
