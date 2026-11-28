"""ch2_s06 · Kinds of number, and how we knew (takeaway and map turn).

Hero callback: on the left the wheel that rolled out π, its gold segment laid on the line; on the right the circle
with its gold square, side √2. On 'name' each length is tagged ≠ p/q. On 'assume', 'follow', 'impossible' the three
moves of the proof come up as key words joined by arrows. On 'That move' the map returns round them; both pictures
shrink into the Quantity node at the bottom, which lights on 'foundations', and the Foundations–Quantity chord draws
lit with 'contradiction' riding it. In the silent beat the ring makes its 60° turn (60° → 120°), Structure coming
round to the bottom.
"""
import math

from aion import *

from beats import T
from hud import progress
from kit import glow_layer, P3, backed, map_state, node, node_xy, sans, tex, the_circle, window, hub_at, turn_view

FQ = (("foundations", "quantity"),)


def ss(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


@scene(T.ch2_s06, T.ch3_s01)
def ch2_s06(s):
    s.solid(C.bg, z=-200)
    progress(s)
    lnk, m, nd, top = glow_layer(s, z=-2, k=0.55), s.manim(z=0), s.manim(z=1), s.manim(z=2)
    t0 = float(s.start)
    t_k, t_as, t_fd = float(T.ch2_s06_kinds), float(T.ch2_s06_assume), float(T.ch2_s06_foundations)
    Q = C.quantity

    # the wheel that rolled out π
    r, x0, yl = 0.55, -6.0, -0.35
    L = math.pi * 2 * r
    wheel = VGroup(Line(P3(x0 - 0.3, yl), P3(x0 + L + 0.9, yl), stroke_color=C.muted, stroke_width=2.2),
                   Line(P3(x0, yl), P3(x0 + L, yl), stroke_color=Q, stroke_width=6),
                   the_circle(r).move_to(P3(x0 + L, yl + r)),
                   Line(P3(x0 + L, yl - 0.2), P3(x0 + L, yl + 0.2), stroke_color=Q, stroke_width=4))
    pi_t = tex(r"\pi", 48, Q).move_to(P3(x0 + L, yl - 0.55))

    # the square in the circle
    cc, R = P3(3.2, 0.35), 1.5
    corners = [cc + R * P3(math.cos(math.radians(d)), math.sin(math.radians(d))) for d in (45, 135, 225, 315)]
    sq = VGroup(the_circle(R).move_to(cc), Polygon(*corners, stroke_color=Q, stroke_width=4))
    r2_t = tex(r"\sqrt{2}", 44, Q).move_to(cc + P3(0, R / math.sqrt(2) - 0.38))
    m.play(FadeIn(wheel, shift=0.15 * RIGHT), at=t0 + 0.3, dur=0.8, ease="easy_ease")
    m.play(FadeIn(sq, shift=0.15 * LEFT), at=t0 + 0.5, dur=0.8, ease="easy_ease")
    m.play(FadeIn(pi_t), FadeIn(r2_t), at=t_k, dur=0.6)
    ne1 = tex(r"\neq \tfrac{p}{q}", 40, C.text).next_to(pi_t, RIGHT, buff=0.15)
    ne2 = tex(r"\neq \tfrac{p}{q}", 40, C.text).next_to(cc + P3(0, -R - 0.45), ORIGIN)
    r2b = tex(r"\sqrt{2}", 40, Q).next_to(ne2, LEFT, buff=0.15)
    m.play(FadeIn(ne1, shift=0.06 * LEFT), FadeIn(VGroup(r2b, ne2), shift=0.06 * UP), at=t_k + 3.4, dur=0.6)

    # the three moves of the proof
    kw = VGroup(sans("assume", 36, C.text), tex(r"\rightarrow", 40, C.muted), sans("follow", 36, C.text),
                tex(r"\rightarrow", 40, C.muted), sans("impossible", 36, C.foundations)).arrange(RIGHT, buff=0.35)
    kw.move_to(P3(0, -2.9))
    for i, dt in ((0, 0.0), (1, 0.9), (2, 1.2), (3, 2.6), (4, 3.2)):
        m.play(FadeIn(kw[i], shift=0.08 * UP), at=t_as + dt, dur=0.45)

    # 'That move': the map returns; both pictures shrink into Quantity, which lights
    t_mp = t_fd - 1.45
    links, nodes = map_state(60, lit=("foundations",))
    hub = hub_at(60)
    q_at = node_xy(1, turn=60)
    pics = VGroup(wheel, pi_t, ne1, sq, r2_t, r2b, ne2)
    m.play(pics.animate.scale(0.08).move_to(q_at).set_opacity(0), at=t_mp, dur=0.9, ease="in_cubic")
    m.play(FadeOut(kw, shift=0.2 * DOWN), at=t_mp - 0.2, dur=0.5)
    lnk.play(FadeIn(links), at=t_mp + 0.1, dur=0.7)
    nd.play(LaggedStart(*(GrowFromCenter(n_) for n_ in nodes), lag_ratio=0.06), at=t_mp + 0.1, dur=0.8)
    m.play(GrowFromCenter(hub), at=t_mp + 0.2, dur=0.7, ease="out_back")
    lit_q = node(1, lit=True, turn=60)
    nd.play(Transform(nodes[1], lit_q), at=t_fd, dur=0.5)
    ping = Circle(radius=0.4, stroke_color=Q, stroke_width=3).move_to(q_at)
    top.play(ping.animate.scale(2.2).set_stroke(opacity=0), at=t_fd + 0.05, dur=0.8)
    top.remove(ping, at=t_fd + 0.9)

    # the Foundations–Quantity chord draws lit, 'contradiction' riding it
    edge = map_state(60, edges=FQ)[0][1]
    lnk.play(Create(edge), at=t_fd + 0.3, dur=0.6)
    mid = 0.5 * (node_xy(0, turn=60) + node_xy(1, turn=60))
    out = mid / max(1e-6, float(math.hypot(mid[0], mid[1])))
    con = backed(sans("contradiction", 30, C.text).move_to(mid - 0.45 * out))
    top.play(FadeIn(con, shift=-0.1 * out), at=t_fd + 0.5, dur=0.4)
    top.play(FadeOut(con), at=t_fd + 1.5, dur=0.4)

    # the signature turn, 60° → 120°
    t_turn = t_fd + 1.0
    turn_d = float(s.end) - 0.05 - t_turn

    def deg(t):
        return 60 + 60 * ss((t - t_turn + 0.15) / turn_d)

    def TV(t):
        return turn_view((t - t_turn + 0.15) / turn_d, 35, 0)

    def ring_at(t):
        return map_state(deg(t), lit=("foundations", "quantity"), view=TV(t))[1]

    def links_at(t):
        return map_state(deg(t), edges=FQ, view=TV(t))[0]

    lnk.remove(links, edge, at=t_turn - 0.15)
    nd.remove(*nodes, at=t_turn - 0.15)
    nd.redraw(window(ring_at, t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
    m.remove(hub, at=t_turn - 0.15)
    m.redraw(window(lambda t: hub_at(deg(t), TV(t)), t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
    lnk.redraw(window(links_at, t_turn - 0.15, float(s.end)), during=(t_turn - 0.15, float(s.end)))
