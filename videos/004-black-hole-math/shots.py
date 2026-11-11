"""Shared shots: the hero black hole that runs continuously under the cold open and the intro."""
from aion import *
from aion.comp.comp import hex_to_linear
from aion.layers.blackhole import camera_basis
from aion.maths import schwarzschild as S

from beats import T

SETTLE = T.cut_intro - 1.0               # the push-in comes to rest just before the intro starts
DIST, INC, FOV = 50.0, 84.0, 36.0        # settled framing (M, degrees)
AZ0, AZ1 = -12.0, 16.0                   # slow orbit across the whole opening


def glow_fx(color=None, k=1.0, r=1.0):
    """The design's tight glow (strength C.glow, radius C.glow_radius): crisp lines with a coloured halo."""
    return Glow(color or C.light, strength=C.glow * k, radius=C.glow_radius * r)


def bh_look():
    """How the active design colours the rendered disk (blackbody temperature, beaming, gain)."""
    return dict(u_Tpeak=C.bh_T, u_beam=C.bh_beam, u_shift=C.bh_shift, u_gain=C.bh_gain)


def brief(m, mob, t_out, dur=0.8):
    """Show a carried-over badge from the scene start, then clear it (nothing sits still for long)."""
    m.add(mob)
    m.play(FadeOut(mob), at=t_out, dur=dur)
    return mob


def breathe(s, a, b, zoom=1.045):
    """A very slow push in and back out over [a, b], so held diagrams are never frozen."""
    half = (b - a) / 2
    s.camera.push(a, zoom=zoom, dur=half, ease="in_out_sine", lead=0)
    s.camera.push(a + half, zoom=1.0, dur=half, ease="in_out_sine", lead=0)


def photons(layer, pts, t0, t1, speed=2.6, gap=3.2, radius=0.055, color=None):
    """Small bright packets of light running along the polyline `pts` during [t0, t1]: a drawn ray stays alive."""
    pts = np.asarray(pts, float)[:, :2]
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    acc = np.concatenate([[0.0], np.cumsum(seg)])
    L = float(acc[-1])
    n = max(1, int(np.ceil(L / gap)))

    def f(t):
        g = VGroup()
        env = float(np.clip((t - t0) / 0.5, 0, 1) * np.clip((t1 - t) / 0.5, 0, 1))
        for i in range(n):
            d = (speed * (t - t0) + i * L / n) % L
            edge = float(np.clip(d / 0.5, 0, 1) * np.clip((L - d) / 0.5, 0, 1))
            p = [np.interp(d, acc, pts[:, 0]), np.interp(d, acc, pts[:, 1]), 0.0]
            g.add(Dot(p, radius=radius, color=color or C.text, fill_opacity=env * edge))
        return g
    h = layer.redraw(f, during=(t0, t1))
    layer.remove(h, at=t1)
    return h


def starfield(s, amount=0.5, **kw):
    """The intro's sky, quiet, behind a diagram scene (additive, so black stays black)."""
    return s.shader("stars.frag", z=-50, blend="add", u_amt=amount, **kw)


def readout(value, unit, color=None, decimals=0, size=0.8):
    """A live number with its unit: `11.2 km/s`. Rebuild it every frame inside a redraw."""
    num = DecimalNumber(value, num_decimal_places=decimals, group_with_commas=True,
                        font_size=C.tex_size * size, color=color or C.text)
    if not unit:
        return VGroup(num)
    lab = Label(unit, color=C.muted, size=C.label_size * size * 0.9)
    lab.next_to(num, RIGHT, buff=0.14).align_to(num, DOWN)
    return VGroup(num, lab)


def hero_camera():
    """Camera tracks for the opening: eased push-in (log distance), slow orbit, a look to the side."""
    # key() starts moving at `at`: begin at t = 0 and arrive at SETTLE
    dist = key(T.start, np.log(120.0), np.log(DIST), dur=SETTLE, ease="smooth", lead=0).map(np.exp)
    inc = key(T.start, 87.5, INC, dur=SETTLE, ease="smooth", lead=0)
    az = ramp(T.start, T.cut_ch1, AZ0, AZ1)
    # hole slides left while the equation sits on the right, then returns to centre for the arc
    yaw = keys((T.cut_intro, 0.0), (T.one_equation, 8.0), (T.stranger - 2.2, 8.0), (T.stranger, 0.0),
               default_ease="easy_ease")
    return dict(dist=dist, inclination=inc, azimuth=az, yaw=yaw, fov=FOV)


def hero(s, **kw):
    """Add the ray-traced hole to scene `s` (identical in every scene that calls it: pure f(t))."""
    # disk_rate 4 M/s: one inner orbit every 23 s, calm, and the gas does not wind into grooves
    # warmer, softer-beamed disk than the strictly physical look (still blackbody + Doppler)
    args = dict(hero_camera(), sky="galaxy", sky_center=(INC, 2.0), scale_res=2, z=-10, disk_rate=4.0, disk_t0=27.0,
                **bh_look(),
                opacity=fade(0.4, dur=3.0, lead=0),
                fx=[Bloom(C.bloom, threshold=0.9), Tonemap()])
    args.update(kw)
    return s.add(BlackHoleLayer(**args))


def disk_edge(t, r=16.5, order=0, n=361):
    """Screen curve of the disk ring r (16.5 M: where the gas visibly ends) at time t (frame units), from the same camera as `hero`."""
    cam = {k: float(track(v)(t)) for k, v in hero_camera().items()}
    pos, right, up, fwd = camera_basis(cam["dist"], cam["inclination"], cam["azimuth"], yaw=cam["yaw"])
    return S.disk_image(r, pos, right, up, fwd, fov_deg=cam["fov"], order=order, n=n)


def scan_tint(k=1.0):
    return tuple(k * c for c in hex_to_linear(C.light))


# ── progress badges: each chapter's result stays in a corner ───────────────
def frac_colors(eq, tex, picks):
    """Colour single glyphs inside an isolated fraction (isolating them in TeX would break \\frac)."""
    part = eq.part(tex)
    for i, col in picks.items():
        part[i].set_color(col)
    return eq


def badge_rs():
    """Chapter 1's result, r_s = 2GM/c², parked top-right (same place it lands at the end of s02)."""
    F = r"\frac{2GM}{c^2}"
    eq = frac_colors(Eqn(r"r_s = " + F, colors={"r_s": C.horizon, F: C.text}, size=84), F, {2: C.mass, 4: C.light})
    return eq.scale(0.5).to_corner(UR, buff=C.margin + 0.1)


def badge_newton():
    """Chapter 1's plant: the thrown-ball bend of a passing ray, '× 2 ?', parked bottom-right."""
    rs_d, b_d, c2 = 0.7, 1.9, np.array([-0.4, -1.5, 0.0])
    pts, _ = S.ray(b_d, rs=0.5 * rs_d, r_max=8.5)
    pts = pts[(np.abs(pts[:, 0] + c2[0]) < 7.3) & (pts[:, 1] + c2[1] < 4.2)]
    newton = VMobject(stroke_color=C.newton, stroke_width=C.stroke)
    newton.set_points_as_corners([[x + c2[0], y + c2[1], 0.0] for x, y in pts])
    mass = Dot(radius=0.2, color=C.mass).move_to(c2)
    straight = DashedLine([pts[0, 0] + c2[0], b_d + c2[1], 0], [6.9, b_d + c2[1], 0], color=C.muted,
                          stroke_width=C.thin, stroke_opacity=0.7)
    d_out = pts[-1] - pts[-2]
    wedge = Arc(radius=2.3, start_angle=0.0, angle=float(np.arctan2(d_out[1], d_out[0])),
                arc_center=[c2[0], b_d + c2[1], 0], color=C.newton, stroke_width=C.thin + 1)
    icon = VGroup(mass, straight, newton, wedge).scale(0.34).to_corner(DR, buff=C.margin + 0.15)
    tag = Eqn(r"\times\,2\ ?", size=64).scale(0.6).move_to([5.75, -1.75, 0])
    return VGroup(icon, tag)


def badge_eq():
    """Chapter 3's result, the light-path equation, parked top-centre (where it lands at the end of s04)."""
    FR = r"\frac{3GM}{c^2}"
    eq = Eqn(r"u'' + u = " + FR + r"\,u^2", colors={"u": C.light, FR: C.mass}, size=76)
    return eq.scale(0.5).move_to([0.9, 3.15, 0])
