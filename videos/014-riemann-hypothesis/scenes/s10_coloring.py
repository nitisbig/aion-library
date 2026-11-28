"""s10 coloring (P21-P22): input and output are both 2-D, so a graph would need four. Instead the s09 panel grows into
the whole plane and is colored (shaders/zeta_domain.frag): hue = direction of f(s), bands = each doubling of size.
f(s) = s has a pinwheel at 0 where all colors meet; sliding the colors one unit makes f(s) = s - 1, whose zero is the
input 1. Then zeta sweeps in from the right, only where its sum works (Re s > 1). Dragged left past the line, the probe's
partial sums (inset) spiral outward and never close."""
from aion import *

from beats import T
from look import (EASE, FRAME_BOX, PANEL_BOX, S_LEFT, S_SPIRAL, SP_K, SP_O, ZGEO, band_key_mob, carded, inset_mobs,
                  inset_spiral, lab, live, re1_mobs, to_d, zeta_tag,
                  oplane_mob, pin, plane_grid, plane_xy, probe_mob, re_gt1_mobs, s_formula, spiral_mob, splane_mob,
                  term_formula, tex, wheel_mob, zeta_label, zeta_mark)

GEO = {                                      # (origin x, origin y, units per 1) for each framing
    "A": (float(SP_O[0]), float(SP_O[1]), SP_K),          # the s09 panel
    "B": (-0.85, -0.14, 1.7),                            # the lesson: s = 0 and s = 1 near the centre
    "C": (-3.1, -0.1, 3.4),                              # pushed in on s = 1
    "D": (*ZGEO[0], ZGEO[1]),                              # zeta: sigma from -6.6 to 11.1, t from -1 to 9
}

@scene(T.cut_coloring, T.cut_continuation)
def s10_coloring(s):
    s.solid(C.bg, z=-200)
    L = C.lead
    grow = (T.instead - L, T.instead + 1.25)
    tint = (T.color_plane - L, T.color_plane + 0.65)
    push = (T.exactly_zero - L, T.exactly_zero + 1.25)
    back = (T.this_is_zeta - L, T.this_is_zeta + 1.25)
    G = keys((grow[0], GEO["A"] + PANEL_BOX), (grow[1], GEO["B"] + FRAME_BOX, EASE),
             (push[0], GEO["B"] + FRAME_BOX), (push[1], GEO["C"] + FRAME_BOX, EASE),
             (back[0], GEO["C"] + FRAME_BOX), (back[1], GEO["D"] + FRAME_BOX, EASE), lead=0)
    mix = keys((tint[0], 0.0), (tint[1], 1.0, EASE), lead=0)
    slide = (T.all_zero - L, T.all_zero + 1.05)
    flip = T.this_is_zeta + 0.45                       # the shader is dark here: switch s - 1 → zeta
    shift = keys((slide[0], 0.0), (slide[1], 1.0, EASE), (flip, 1.0), (flip + 1e-3, 0.0), lead=0)

    def geo(t):
        g = G(t)
        return (g[0], g[1]), g[2], tuple(g[3:7])

    # ── s09's last frame ──
    old_op = s.manim(z=3)
    old_sp = s.manim(z=4, parallax=0.0)
    hud = s.manim(z=6, parallax=0.0)
    out_plane, spiral, mark, zlab = oplane_mob(1.0), spiral_mob(S_SPIRAL, 4000.0, 1.0, 1.0), zeta_mark(1.0), zeta_label(1.0)
    old_op.add(spiral, out_plane, mark, zlab)          # s09's order: the zoom grid was added after the spiral
    panel, probe0, gt = splane_mob(), probe_mob(S_SPIRAL, 1.0, 1.0), re_gt1_mobs()
    old_sp.add(panel.grid, panel.axes, panel.ticks, gt.half, gt.line, gt.label, probe0)
    s_eq, tf = s_formula(), term_formula()
    hud.add(s_eq, tf)

    # ── input and output are both 2-D: a graph would need four ──
    hud.play(FadeOut(s_eq), FadeOut(tf), at=T.outputs, dur=0.6)
    old_sp.play(FadeOut(VGroup(gt.half, gt.line, gt.label)), at=T.outputs, dur=0.6)
    tag_in = VGroup(lab("input", 30, C.muted), tex("s", size=40, color=C.s_in)).arrange(RIGHT, buff=0.2)
    tag_out = VGroup(lab("output", 30, C.muted), tex(r"\zeta(s)", size=40, color=C.zeta)).arrange(RIGHT, buff=0.2)
    tag_in.move_to([(PANEL_BOX[0] + PANEL_BOX[1]) / 2, 3.0, 0])
    tag_out.move_to([1.8, 3.0, 0])
    hud.play(FadeIn(tag_in, shift=0.06 * DOWN), at=T.outputs + 0.4, dur=0.5)
    hud.play(FadeIn(tag_out, shift=0.06 * DOWN), at=T.outputs + 1.0, dur=0.5)
    four = VGroup(tex(r"2+2=4", size=40), lab("dimensions", 30, C.muted)).arrange(RIGHT, buff=0.22)
    four.move_to([-1.55, 3.0, 0])
    hud.play(FadeIn(four, scale=0.95), at=T.four_dims, dur=0.6)

    # ── instead, color the plane: the panel grows into the whole frame ──
    old_op.play(FadeOut(VGroup(out_plane, spiral, mark, zlab)), at=T.instead, dur=0.6)
    hud.play(FadeOut(VGroup(tag_in, tag_out, four)), at=T.instead, dur=0.6)
    old_sp.play(FadeOut(panel.ticks), FadeOut(probe0), at=T.instead, dur=0.5)
    old_sp.remove(panel.grid, panel.axes, at=grow[0])
    pg = s.manim(z=2, parallax=0.0)
    live(pg, lambda t: plane_grid(*geo(t)[:2], box=geo(t)[2], mix=float(mix(t))), (grow[0], tint[1]), push, back)

    def u_origin(t):
        (ox, oy), u, _ = geo(t)
        return (ox + float(shift(t)) * u, oy)

    moving = [grow, slide, push, back, (flip, flip + 1e-3)]
    s.shader("zeta_domain.frag", z=0, animated=False,
             u_origin=Track(u_origin, active=moving), u_unit=Track(lambda t: float(geo(t)[1]), active=moving),
             u_func=keys((flip, 0.0), (flip + 1e-3, 3.0), lead=0),
             u_reveal=keys((flip, -1000.0), (flip + 1e-3, 12.0), (flip + 0.05, 12.0),
                           (T.this_is_zeta + 2.5, 1.0, EASE), lead=0),
             u_opacity=keys((tint[0], 0.0), (tint[1] + 0.15, 1.0, EASE), (back[0], 1.0), (flip - 0.05, 0.0, EASE),
                            (flip, 0.0), (flip + 1e-3, 1.0), lead=0),
             u_dim=0.0, u_sat=0.85, u_gain=1.0, u_debug=0.0)

    f_tag = tex(r"f(s)", r"=", r"s", size=40)
    f_tag2 = tex(r"f(s)", r"=", r"s", r"-1", size=40)
    ex = lab("example", 26, C.muted)
    pin(VGroup(f_tag2, ex).arrange(RIGHT, buff=0.3, aligned_edge=DOWN), top=3.5, left=-6.4)   # room for the longer tag
    f_tag.move_to(f_tag2, aligned_edge=LEFT)
    f_card = BackgroundRectangle(VGroup(f_tag2, ex), color=C.bg, fill_opacity=1.0, buff=0.16)
    hud.play(FadeIn(f_card), FadeIn(f_tag), FadeIn(ex), at=T.color_plane + 0.3, dur=0.6)

    # ── hue = direction, bands = size (each band one doubling) ──
    wheel = wheel_mob().move_to([-5.9, -2.62, 0])
    w_lab = lab("direction", 24, C.muted).next_to(wheel, DOWN, buff=0.14)
    wcard = carded(VGroup(wheel, w_lab), buff=0.16, opacity=1.0)
    hud.play(FadeIn(wcard), at=T.hue, dur=0.7)
    bands = band_key_mob(height=0.38).move_to([-3.45, -2.5, 0])
    b_lab = lab("size", 24, C.muted).next_to(bands, DOWN, buff=0.14)
    bcard = carded(VGroup(bands, b_lab), buff=0.16, opacity=1.0)
    hud.play(FadeIn(bcard), at=T.bands, dur=0.7)

    # ── where all the colors meet, the value is zero; a zero is an input ──
    mk = s.manim(z=5, parallax=0.0)

    def ring(t):
        o, u, _ = geo(t)
        p = plane_xy(complex(float(shift(t)), 0.0), o, u)
        r = Circle(radius=0.17, color=C.text, stroke_width=2.6).move_to(p)
        return r

    def ring_lab(t, text):
        o, u, _ = geo(t)
        p = plane_xy(complex(float(shift(t)), 0.0), o, u)
        return carded(tex(text, size=34), buff=0.08).move_to(p + [0.95, 0.55, 0])

    r0 = ring(T.colors_meet)
    mk.play(Create(r0), at=T.colors_meet + 0.3, dur=0.6)
    l0 = ring_lab(T.colors_meet, r"f(0)=0")
    mk.play(FadeIn(l0), at=T.colors_meet + 1.6, dur=0.5)
    mk.remove(r0, at=slide[0])
    mk.play(FadeOut(l0), at=T.all_zero - 0.3, dur=0.35)
    rings = live(mk, ring, slide, push)
    hud.play(TransformMatchingTex(f_tag, f_tag2), at=T.all_zero + 0.2, dur=0.8)
    l1 = ring_lab(slide[1], r"f(1)=0")
    mk.play(FadeIn(l1), at=T.all_zero + 1.2, dur=0.5)
    mk.play(FadeOut(l1), at=T.exactly_zero - 0.2, dur=0.3)

    # ── this is zeta, where the sum works (Re s > 1) ──
    z_tag = zeta_tag()
    hud.play(FadeOut(f_tag2), FadeOut(ex), FadeOut(f_card), FadeOut(wcard), FadeOut(bcard), at=T.this_is_zeta, dur=0.4)
    mk.play(FadeOut(rings[-1]), at=T.this_is_zeta, dur=0.4)
    hud.play(FadeIn(z_tag), at=T.this_is_zeta + 0.8, dur=0.6)

    # ── left of Re s = 1 the arrows don't shrink fast enough: the spiral never closes ──
    re1 = re1_mobs()
    mk.play(Create(re1.line), at=T.left_of, dur=0.8)
    mk.play(FadeIn(re1.label), at=T.left_of + 0.4, dur=0.5)

    drag = (T.left_of + 1.2, T.left_of + 3.2)
    sig = keys((drag[0], S_SPIRAL.real), (drag[1], S_LEFT.real, EASE), lead=0)
    s_of = lambda t: complex(float(sig(t)), S_SPIRAL.imag)      # noqa: E731
    n_in = keys((T.dont_shrink - L, 400.0), (T.dont_shrink + 2.6, 3000.0, "in_cubic"), lead=0)
    ins = inset_mobs()

    def inset(t):
        return inset_spiral(s_of(t), float(n_in(t)))

    p1 = probe_mob(s_of(T.left_of), 0.0, 0.0, to_xy=to_d)
    in0 = inset(T.left_of)
    mk.play(FadeIn(p1), at=T.left_of + 0.6, dur=0.5)
    hud.play(FadeIn(ins.frame), FadeIn(ins.cap), FadeIn(in0), at=T.left_of + 0.6, dur=0.5)
    mk.remove(p1, at=drag[0])
    mk.redraw(lambda t: probe_mob(s_of(t), 0.0, 0.0, to_xy=to_d), during=drag)
    hud.remove(in0, at=drag[0])
    live(hud, inset, (drag[0], T.dont_shrink + 2.6))
