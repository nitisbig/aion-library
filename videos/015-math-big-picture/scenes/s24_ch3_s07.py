"""ch3_s07 · Turning in three dimensions (sighting, takeaway, map turn).

The unit circle slides left and becomes the outer ring of a gimbal: three violet rings, each turning about an axis
carried by the one outside it, drawn in true 3D (rotation matrices, projected; the far half of each ring dimmer),
with a phone outline at the centre. On 'Hamilton' 'W. R. Hamilton · 1843' comes up and on 'carved the rule' his rule
i² = j² = k² = ijk = −1 appears on a stone-grey card. On 'quaternions' a camera frustum orbits a wireframe cube. On
'phone' the phone rights itself while the rings keep moving, an arrow showing up. On 'moves are turns' the hero comes
back: the point sweeping the unit circle over e^{iθ} = cos θ + i sin θ. On 'Algebra' the map grows round it, the
circle becomes the hub, the rest shrinks into Structure at the bottom, which lights; the chords Foundations–Structure
and Quantity–Structure draw, and in the silence the ring turns 120° → 180°.
"""
import math

import numpy as np
from aion import *

from beats import T
from hud import progress
from kit import plate, glow_fx, glow_layer, mix_hex, rgb255, PL_O, PL_U, P3, caps, map_state, node, node_xy, sans, tex, the_circle, tint, window, hub_at, turn_view

GC = P3(-3.4, -0.1)
RR = (2.05, 1.7, 1.35)
CUBE_C = P3(4.35, -1.75)
EDGES = (("foundations", "quantity"), ("foundations", "structure"), ("quantity", "structure"))
LIT = ("foundations", "quantity", "structure")


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


VIEW = rx(math.radians(18)) @ ry(math.radians(-24))     # a fixed three-quarter view


def lower_third(name, x=1.95, y=3.3):
    g = VGroup(caps(name, 34, C.text), Line(ORIGIN, RIGHT * 3.6, stroke_color=C.muted, stroke_width=1.4))
    return g.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(P3(x, y), aligned_edge=LEFT)


def polyline3(pts, c, col, w, front_op=1.0, back_op=0.3):
    """Project 3D points (rows) through VIEW and draw them, the far half dimmer."""
    q = pts @ VIEW.T
    g = VGroup()
    for k in range(len(q) - 1):
        z = 0.5 * (q[k, 2] + q[k + 1, 2])
        op = front_op if z >= 0 else back_op
        g.add(Line(c + P3(q[k, 0], q[k, 1]), c + P3(q[k + 1, 0], q[k + 1, 1]), stroke_color=col, stroke_width=w,
                   stroke_opacity=op))
    return g


def polyline3s(pts, c, col, w, f=1.0):
    """Like polyline3, but lit by depth: near segments full color and thicker, far ones dim and thin."""
    q = pts @ VIEW.T
    zs = 0.5 * (q[:-1, 2] + q[1:, 2])
    zn = (zs - zs.min()) / max(zs.max() - zs.min(), 1e-6) if len(zs) > 1 else np.ones(1)
    g = VGroup()
    for k in range(len(q) - 1):
        u = float(zn[k])
        g.add(Line(c + P3(q[k, 0], q[k, 1]), c + P3(q[k + 1, 0], q[k + 1, 1]),
                   stroke_color=mix_hex(tint(col, 0.3), col, u), stroke_width=w * (0.55 + 0.75 * u),
                   stroke_opacity=f * (0.35 + 0.65 * u)))
    return g


def flat3(pts, c, color, op):
    """A filled planar polygon, projected through VIEW."""
    q = pts @ VIEW.T
    return Polygon(*[c + P3(x, y) for x, y, _ in q], stroke_width=0, fill_color=color, fill_opacity=op)


def stone(w, h, seed=1843, px=135):
    """A carved stone plaque (granite noise, bevelled edges, rounded corners) as RGBA, w × h world units."""
    from scipy.ndimage import zoom
    W_, H_ = int(w * px), int(h * px)
    rg = np.random.default_rng(seed)
    n = np.zeros((H_, W_))
    for octv, amp in ((6, 0.5), (16, 0.28), (48, 0.16), (140, 0.1)):
        g = rg.random((max(2, int(octv * h / w)), octv))
        n += amp * zoom(g, (H_ / g.shape[0], W_ / g.shape[1]), order=1)[:H_, :W_]
    speck = (rg.random((H_, W_)) > 0.985) * 0.25
    base = np.array(rgb255(C.muted), float) / 255.0
    lum = 0.32 + 0.22 * n + speck
    yy, xx = np.mgrid[0:H_, 0:W_]
    e = 10.0
    top = np.clip(1 - yy / e, 0, 1) + np.clip(1 - xx / e, 0, 1)
    bot = np.clip(1 - (H_ - 1 - yy) / e, 0, 1) + np.clip(1 - (W_ - 1 - xx) / e, 0, 1)
    lum = lum + 0.22 * top - 0.18 * bot
    rgb = np.clip(base[None, None, :] * lum[..., None] * 1.25, 0, 1)
    rad = 14
    cx_ = np.clip(np.minimum(xx, W_ - 1 - xx), 0, rad)
    cy_ = np.clip(np.minimum(yy, H_ - 1 - yy), 0, rad)
    corner = np.hypot(rad - cx_, rad - cy_)
    a = np.clip(rad + 0.5 - corner, 0, 1)
    rgba = np.zeros((H_, W_, 4), np.uint8)
    rgba[..., :3] = (rgb * a[..., None] * 255).astype(np.uint8)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return rgba


def polar(M):
    u, _, vt = np.linalg.svd(M)
    return u @ vt


@scene(T.ch3_s07, T.ch4_s01)
def ch3_s07(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, m, nd, top = glow_layer(s, z=-2, k=0.55), s.manim(z=0), s.manim(z=1), s.manim(z=2)
    gl = glow_layer(s, z=0.5, color=C.structure)
    t0 = float(s.start)
    t_mac, t_ham, t_qu = float(T.ch3_s07_machines), float(T.ch3_s07_hamilton), float(T.ch3_s07_quaternions)
    t_ph, t_mt, t_alg = float(T.ch3_s07_phone), float(T.ch3_s07_moves_are_turns), float(T.ch3_s07_algebra)
    V = C.structure
    t_g0, t_g1 = t_mac - 0.6, t_mt - 1.4                     # the gimbal's life

    # the unit circle slides over and becomes the outer ring
    circ = the_circle(PL_U).move_to(PL_O)
    m.add(circ)
    ring0 = Circle(radius=RR[0], stroke_color=V, stroke_width=4).move_to(GC)
    m.play(Transform(circ, ring0), at=t0 + 0.3, dur=1.3, ease="easy_ease")
    m.remove(circ, at=t_g0 + 0.02)

    th = np.linspace(0, 2 * np.pi, 97)
    ring_xy = np.c_[np.cos(th), np.sin(th), np.zeros_like(th)]
    ring_yz = np.c_[np.zeros_like(th), np.cos(th), np.sin(th)]
    ring_xz = np.c_[np.cos(th), np.zeros_like(th), np.sin(th)]
    phone = np.array([[-0.32, -0.6, 0], [0.32, -0.6, 0], [0.32, 0.6, 0], [-0.32, 0.6, 0], [-0.32, -0.6, 0]])
    screen = np.array([[-0.25, -0.45, 0], [0.25, -0.45, 0], [0.25, 0.48, 0], [-0.25, 0.48, 0], [-0.25, -0.45, 0]])

    def frames(t):
        tau = t - t_g0
        k = ss(tau / 1.2)
        a = k * 1.1 * math.sin(0.37 * tau)
        b = k * 0.9 * math.sin(0.52 * tau + 0.6)
        c = k * 1.0 * math.sin(0.29 * tau + 1.9)
        F1 = ry(a)
        F2 = F1 @ rx(b)
        F3 = F2 @ ry(c)
        return F1, F2, F3

    def gimbal(t):
        F1, F2, F3 = frames(t)
        f = 1 - ss((t - t_g1 + 0.6) / 0.6)
        g = VGroup(polyline3s(RR[0] * ring_xy @ F1.T, GC, V, 6, f),
                   polyline3s(RR[1] * ring_yz @ F2.T, GC, V, 6, f),
                   polyline3s(RR[2] * ring_xz @ F3.T, GC, V, 6, f))
        return g

    def phone_f(t):
        F1, F2, F3 = frames(t)
        f = 1 - ss((t - t_g1 + 0.6) / 0.6)
        g = VGroup()
        u = ss((t - t_ph + 0.1) / 1.2)                                 # 'phone': it rights itself
        P = polar((1 - u) * F3 + u * np.eye(3)) if u > 0 else F3
        lit_ = 0.55 + 0.45 * abs(float((P @ np.array([0, 0, 1.0]) @ VIEW.T)[2]))   # faces us: brighter
        g.add(flat3(phone[:4] @ P.T, GC, tint(C.text, 0.12), f),
              flat3(screen[:4] @ P.T, GC, mix_hex(tint(V, 0.25), tint(C.circle, 0.5), 0.3 * u), f * lit_),
              polyline3(phone @ P.T, GC, C.text, 2.6, f, 0.5 * f))
        return g

    gl.redraw(window(gimbal, t_g0, t_g1), during=(t_g0, t_g1))
    m.redraw(window(phone_f, t_g0, t_g1), during=(t_g0, t_g1))
    up = Arrow(GC + P3(0, 0.75), GC + P3(0, 1.3), buff=0, stroke_width=4, color=C.text,
               max_tip_length_to_length_ratio=0.3)
    m.play(GrowArrow(up), at=t_ph + 1.2, dur=0.4)
    m.play(FadeOut(up), at=t_g1 - 0.6, dur=0.5)

    # Hamilton, and the rule he carved
    lt = lower_third(r"W.\ R.\ Hamilton\ \textperiodcentered\ 1843")
    m.play(FadeIn(lt, shift=0.08 * LEFT), at=t_ham - 0.1, dur=0.6)
    plate(s, m, "hamilton", (3.65, -0.4), 2.4, t_ham + 0.2, t_qu - 1.0, C.structure)
    m.play(FadeOut(lt), at=t_qu - 1.0, dur=0.5)
    rule = tex(r"i^2 = j^2 = k^2 = ijk = -1", 42, C.text).move_to(P3(3.65, 1.55))
    card = Rectangle(width=rule.width + 0.8, height=1.25, stroke_width=0, fill_opacity=0).move_to(rule)
    s.add(ArrayLayer(stone(card.width, card.height), z=-0.5, pos=tuple(card.get_center()[:2]), height=card.height,
                     premultiplied=True, opacity=fade(t_ham + 5.0, dur=0.5, out=t_g1 - 0.2, out_dur=0.5)))
    groove = rule.copy().set_color(C.bg).set_opacity(0.85).shift(P3(0.012, 0.018))      # the cut's shadow
    rule.set_color(tint(C.circle, 0.85))
    dub = sans("Dublin", 26, C.muted).next_to(card, DOWN, buff=0.15).align_to(card, RIGHT)
    m.play(Write(groove), at=t_ham + 5.2, dur=1.0)
    m.play(Write(rule), at=t_ham + 5.2, dur=1.0)
    m.play(FadeIn(dub), at=t_ham + 6.4, dur=0.4)

    # 'quaternions': a camera orbits a wireframe cube
    qw = caps("quaternions", 38, V).move_to(P3(3.65, 0.2))
    m.play(FadeOut(dub), FadeIn(qw, shift=0.06 * UP), at=t_qu, dur=0.5)
    corners = np.array([[x, y, z] for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)])
    cube_e = [(i, j) for i in range(8) for j in range(i + 1, 8) if np.sum(np.abs(corners[i] - corners[j])) == 1]
    t_c0 = t_qu - 0.3

    def cube(t):
        tau = t - t_c0
        f = ss(tau / 0.5) * (1 - ss((t - t_g1 + 0.6) / 0.6))
        R = ry(0.25 * tau) @ rx(0.35)
        P = corners @ R.T
        g = VGroup()
        for i, j in cube_e:
            g.add(polyline3(np.array([P[i], P[j]]), CUBE_C, C.text, 2, 0.9 * f, 0.4 * f))
        ang = 0.9 * tau
        eye = 1.5 * np.array([math.sin(ang), 0.35, math.cos(ang)])
        fwd = -eye / np.linalg.norm(eye)
        right = np.cross(fwd, [0, 1, 0])
        right /= np.linalg.norm(right)
        upv = np.cross(right, fwd)
        base = eye + 0.45 * fwd
        rect = [base + 0.22 * sx * right + 0.15 * sy * upv for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for r_ in rect:
            g.add(polyline3(np.array([eye, r_]), CUBE_C, V, 2.4, f, 0.45 * f))
        g.add(polyline3(np.array(rect + [rect[0]]), CUBE_C, V, 2.4, f, 0.45 * f))
        return g

    gl.redraw(window(cube, t_c0, t_g1), during=(t_c0, t_g1))
    m.play(FadeOut(VGroup(card, groove, rule, qw)), at=t_g1 - 0.6, dur=0.5)

    # 'moves are turns': the hero, the point sweeping the unit circle
    HC, HR = P3(0, 0.55), 1.5
    hero = the_circle(HR).move_to(HC)
    F = MathTex(r"e^{i\theta}", "=", r"\cos\theta", "+", r"i\sin\theta", font_size=48, color=C.text)
    F[0][0].set_color(C.change)
    F[0][1].set_color(V)
    F[4][0].set_color(V)
    F.move_to(P3(0, -1.75))
    m.play(Create(hero), at=t_g1 - 0.1, dur=0.9, ease="easy_ease")
    m.play(FadeIn(F, shift=0.08 * UP), at=t_g1 + 0.5, dur=0.6)
    t_p0, t_p1 = t_g1 + 0.4, t_alg - 0.6

    def sweep(t):
        a = 0.95 * (t - t_p0) + 0.5
        p = HC + HR * P3(math.cos(a), math.sin(a))
        f = ss((t - t_p0) / 0.4)
        return VGroup(Line(HC, p, stroke_color=V, stroke_width=4, stroke_opacity=f), Dot(p, radius=0.1, color=V,
                                                                                         fill_opacity=f))

    top.redraw(window(sweep, t_p0, t_p1), during=(t_p0, t_p1))
    pt_end = sweep(t_p1)
    top.add(pt_end, at=t_p1)

    # 'Algebra': the map; the circle becomes the hub; the rest shrinks into Structure, which lights
    links, nodes = map_state(120, lit=("foundations", "quantity"), edges=EDGES[:1])
    hub = hub_at(120)
    s_at = node_xy(2, turn=120)
    m.play(Transform(hero, hub), at=t_p1, dur=0.9, ease="easy_ease")
    top.play(pt_end.animate.scale(0.1).move_to(s_at).set_opacity(0), at=t_p1, dur=0.8, ease="in_cubic")
    m.play(F.animate.scale(0.1).move_to(s_at).set_opacity(0), at=t_p1, dur=0.8, ease="in_cubic")
    lnk.play(FadeIn(links), at=t_p1 + 0.1, dur=0.7)
    nd.play(LaggedStart(*(GrowFromCenter(n_) for n_ in nodes), lag_ratio=0.05), at=t_p1 + 0.1, dur=0.8)
    nd.play(Transform(nodes[2], node(2, lit=True, turn=120)), at=t_alg + 0.3, dur=0.5)
    ping = Circle(radius=0.4, stroke_color=V, stroke_width=3).move_to(s_at)
    top.play(ping.animate.scale(2.2).set_stroke(opacity=0), at=t_alg + 0.35, dur=0.8)
    top.remove(ping, at=t_alg + 1.2)
    new_edges = map_state(120, edges=EDGES[1:])[0][1]
    lnk.play(LaggedStart(*(Create(e_) for e_ in new_edges), lag_ratio=0.4), at=t_alg + 0.6, dur=0.9)

    # the signature turn, 120° → 180°
    t_turn = t_alg + 1.9
    turn_d = float(s.end) - 0.05 - t_turn

    def deg(t):
        return 120 + 60 * ss((t - t_turn + 0.15) / turn_d)

    def TV(t):
        return turn_view((t - t_turn + 0.15) / turn_d, 40, 0)

    def ring_at(t):
        return map_state(deg(t), lit=LIT, view=TV(t))[1]

    def links_at(t):
        return map_state(deg(t), edges=EDGES, view=TV(t))[0]

    lnk.remove(links, *new_edges, at=t_turn - 0.15)               # Create added each chord on its own
    nd.remove(*nodes, at=t_turn - 0.15)
    nd.redraw(window(ring_at, t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
    m.remove(hero, at=t_turn - 0.15)
    m.redraw(window(lambda t: hub_at(deg(t), TV(t)), t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
    lnk.redraw(window(links_at, t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
