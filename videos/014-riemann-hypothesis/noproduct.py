"""s19's builders, shared with s20 (which opens on s19's last frame): the colored plane centred on Re s = 1/2 near
height 10, the shade over Re s < 1, the Euler product and its partial products (inset)."""
from functools import lru_cache
from types import SimpleNamespace

from aion import *

from look import carded, clip_seg, lab, pin, plane_xy, probe_mob, tex
from zmath import primes_upto

U, XH, TC, YC = 0.75, -2.6, 10.0, -0.3       # units per 1; screen x of Re s = 1/2; the height at screen y = YC
O = (XH - 0.5 * U, YC - TC * U)              # the screen point of s = 0
BOX = (1.6, 6.6, -3.5, 1.3)                  # the inset (x0, x1, y0, y1)
VC, IK = 2.0 - 0.2j, 0.95                    # the value at the inset's centre, and its scale
N0 = 1229                                    # the primes up to 10^4 (where the product settles)
N1 = 60                                      # the primes shown as the probe slides into the strip
S_IN, S_STRIP = 2.0 + 10.0j, 0.5 + 10.0j
SHADER = dict(u_origin=O, u_unit=U, u_func=3.0, u_reveal=-1000.0, u_dim=0.0, u_sat=0.85, u_gain=1.0, u_debug=0.0,
              u_rot=0.0)


def to_p(z):
    return plane_xy(complex(z), O, U)


def to_ins(z):
    z = np.asarray(z, complex)
    c = np.array([(BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2])
    d = IK * (z - VC)
    return np.stack([c[0] + d.real, c[1] + d.imag, np.zeros(np.shape(d))], axis=-1)


@lru_cache(maxsize=1)
def primes():
    return primes_upto(200_000).astype(float)      # 17,984 primes


def products(s, n):
    """1, then the partial Euler products over the first n primes."""
    p = primes()[: int(n)]
    return np.concatenate([[1.0 + 0j], np.cumprod(1.0 / (1.0 - p ** (-complex(s))))])


def path_mob(s, n, tip=False):
    """The partial products as a path in the inset, cut where it first leaves the frame."""
    pts = to_ins(products(s, max(n, 1)))
    box = (BOX[0] + 0.05, BOX[1] - 0.05, BOX[2] + 0.05, BOX[3] - 0.45)
    keep = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        seg = clip_seg(a, b, box)
        if seg is None:
            break
        keep.append(seg[1])
        if not seg[2]:
            break
    if len(keep) < 2:
        return VGroup()
    v = VMobject(color=C.prime, stroke_width=2.2)
    v.set_points_as_corners(np.array(keep))
    return VGroup(v, Dot(keep[-1], radius=0.07, color=C.prime)) if tip else v


def parts():
    """Every fixed object of s19, in its final place."""
    x0, x1 = to_p(0j)[0], to_p(1 + 0j)[0]
    line = Line([XH, -4.2, 0], [XH, 4.2, 0], color=C.crit, stroke_width=2.0, stroke_opacity=0.75)
    re0 = Line([x0, -4.2, 0], [x0, 4.2, 0], color=C.crit, stroke_width=1.6, stroke_opacity=0.6)
    re1 = DashedLine([x1, -4.2, 0], [x1, 4.2, 0], color=C.text, stroke_width=2.4, dash_length=0.12)
    r1lab = carded(tex(r"\mathrm{Re}\,s=1", size=30), buff=0.08, opacity=1.0)
    r1lab.move_to([x1 + 0.2 + r1lab.width / 2, 3.25, 0])
    shade_l = Rectangle(width=x0 + 7.3, height=8.6, stroke_width=0, fill_color=C.bg, fill_opacity=0.97)
    shade_l.move_to([(x0 - 7.3) / 2, 0, 0])
    shade_s = Rectangle(width=x1 - x0, height=8.6, stroke_width=0, fill_color=C.bg, fill_opacity=0.97)
    shade_s.move_to([(x0 + x1) / 2, 0, 0])
    eq = tex(r"\zeta(s)", r"=", r"\prod_p", r"\frac{1}{1-p^{-s}}", size=40, colors={0: C.zeta, 2: C.prime})
    so = tex(r"\mathrm{Re}\,s>1", r"\ \Rightarrow\ ", r"\zeta(s)\neq0", size=36, colors={2: C.zeta})
    pin(VGroup(eq, so).arrange(DOWN, buff=0.3, aligned_edge=LEFT), top=3.45, left=-6.3)
    eq_bg, so_bg = carded(eq, buff=0.12, opacity=1.0)[0], carded(so, buff=0.12, opacity=1.0)[0]
    frame = Rectangle(width=BOX[1] - BOX[0], height=BOX[3] - BOX[2], stroke_color=C.faint, stroke_width=1.4,
                      fill_color=C.bg, fill_opacity=1.0).move_to([(BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2, 0])
    cap = lab("partial products", 24, C.muted).move_to([BOX[0] + 0.2, BOX[3] - 0.24, 0], aligned_edge=LEFT)
    o = to_ins(0j)
    zero = VGroup(Line(o + [-0.1, 0, 0], o + [0.1, 0, 0]), Line(o + [0, -0.1, 0], o + [0, 0.1, 0]))
    zero.set_stroke(C.text, width=2.0)
    zero.add(tex("0", size=26).move_to(o + [-0.22, -0.22, 0]))
    nolonger = carded(lab("no longer converges", 26, C.text), buff=0.08, opacity=1.0)
    nolonger.move_to([(BOX[0] + BOX[1]) / 2, BOX[2] + 0.3, 0])
    return SimpleNamespace(line=line, re0=re0, re1=re1, r1lab=r1lab, shade_l=shade_l, shade_s=shade_s, eq=eq, so=so,
                           eq_bg=eq_bg, so_bg=so_bg, frame=frame, cap=cap, zero=zero, nolonger=nolonger)


def end_frame():
    """s19's last frame as (shade layer, line layer, inset layer) lists, each in s19's draw order."""
    P = parts()
    P.shade_s.set_fill(opacity=0.75)
    shade = [P.shade_l, P.shade_s]
    lines = [P.line, P.re0, P.re1, P.r1lab, probe_mob(S_STRIP, 0.0, 0.0, to_xy=to_p)]
    hud = [P.eq_bg, P.eq, P.frame, P.cap, P.zero, path_mob(S_IN, N0), P.so_bg, P.so,
           path_mob(S_STRIP, len(primes()), tip=True), P.nolonger]
    return shade, lines, hud
