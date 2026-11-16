"""Outro: the hook box H one last time, with each chapter's badge gathering around it. Then the lattice and the die
return with H applied, and the measuring arrows change: the same move gets nine new numbers (P⁻¹HP) while nothing
on screen moves. Pointer to video 006 (the determinant)."""
from aion import *

from beats import T
from shots import (H3, I3, Cam, Mat, _badges, arrow, backdrop, backing, die_height, die_rgba, finish, lattice, rail,
                   tex)

E = "smooth"
P = np.array([[1, 0, 0], [1, 1, 0], [0, 1, 1]], float)        # three other measuring arrows (det 1)
PHP = np.linalg.inv(P) @ H3 @ P                                  # [[3,1,0],[-2,1,1],[3,0,0]]
AZ, EL, CO, CU = -30.0, 22.0, np.array([1.6, -0.6]), 1.25
COLS3 = lambda: [C.ihat, C.jhat, C.khat]                          # noqa: E731


@scene(T.cut_outro, T.end)
def s19_outro(s):
    backdrop(s)
    end = keys((T.end - 1.6, 1.0), (T.end - 0.3, 0.0), lead=0)
    m = s.manim(z=1, opacity=end)                       # lattice
    g = s.manim(z=3, opacity=end)                       # arrows
    hb = s.manim(z=4.9, parallax=0.0, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    rl = s.manim(z=5.1, parallax=0.0, opacity=end)
    rail(rl, 7)
    assert np.allclose(PHP, np.round(PHP))

    # ── the box, one last time; the chapters gather around it ──
    Hm = Mat(H3, size=96, h_buff=1.5, v_buff=1.15)
    hud.play(LaggedStart(*[FadeIn(c) for col in Hm.cols for c in col], lag_ratio=0.06), FadeIn(Hm.br),
             at=T.last_time + 0.3, dur=1.2)
    ring = [(3, T.axes_land + 0.2, (-4.2, 1.6)), (4, T.mult2 + 0.4, (4.2, 1.6)), (5, T.det2 + 0.5, (-4.6, -1.3)),
            (6, T.eig2 + 0.6, (4.6, -1.3)), (7, T.underneath + 1.2, (0.0, -3.0))]
    icons = VGroup()
    for k, tt, pos in ring:
        b = _badges()[k - 1]
        b.scale_to_fit_height(0.75)
        if b.width > 2.4:
            b.scale_to_fit_width(2.4)
        fr = Rectangle(width=b.width + 0.6, height=b.height + 0.45, stroke_color=C.frame, stroke_width=C.thin)
        icon = VGroup(fr, b.move_to(fr)).move_to([*pos, 0])
        src = icon.copy().scale(0.3).move_to([7.11 - C.margin - 0.31 - (7 - k) * 0.68, 4.0 - C.margin - 0.2, 0])
        hud.play(TransformFromCopy(src, icon), at=tt, dur=0.9, ease="out_back")
        icons.add(icon)
    hud.play(Indicate(Hm.cols[0], color=C.ihat, scale_factor=1.12), Indicate(Hm.cols[1], color=C.jhat, scale_factor=1.12),
             Indicate(Hm.cols[2], color=C.khat, scale_factor=1.12), at=T.axes_land + 0.9, dur=0.8)

    # ── one last thought: the move, from where we stand ──
    t0 = T.thought + 0.1
    hud.play(FadeOut(icons), at=t0, dur=0.6)
    Hs = Mat(H3, size=52, h_buff=0.85, v_buff=0.7)
    Hs.move_to([-7.11 + C.margin + 0.35 + Hs.width / 2, 3.55 - C.margin - Hs.height / 2, 0])
    hud.play(ReplacementTransform(Hm, Hs), at=t0 + 0.2, dur=1.0, ease=E)
    hk = backing(Hs, pad=0.3)
    hb.play(FadeIn(hk), at=t0 + 0.9, dur=0.4)

    cam = Cam(AZ, EL, origin=CO, unit=CU)
    m.play(FadeIn(lattice(cam, H3, n=1, box=2.6)), at=t0 + 0.8, dur=1.2)
    s.add(FramesLayer(lambda t: die_rgba(0.5 * H3, az=AZ, el=EL, size=900), height=die_height(CU), pos=tuple(CO),
                      z=2, start=t0 + 0.5, during=[(t0 + 0.6, t0 + 0.61)],
                      opacity=keys((t0 + 0.9, 0.0), (t0 + 1.8, 1.0), (T.end - 1.6, 1.0), (T.end - 0.3, 0.0), lead=0)))
    o = cam.scr(np.zeros(3))
    hats = VGroup(*[arrow(o, cam.scr(H3[:, j]), COLS3()[j], width=C.stroke + 1) for j in range(3)])
    g.play(LaggedStart(*[GrowArrow(a) for a in hats], lag_ratio=0.2), at=t0 + 1.3, dur=1.0)
    for j, tt in enumerate((T.choice + 1.15, T.choice + 1.75, T.choice + 2.45)):
        g.play(Indicate(hats[j], color=COLS3()[j], scale_factor=1.15), at=tt, dur=0.6)
        hud.play(Indicate(Hs.cols[j], color=COLS3()[j], scale_factor=1.2), at=tt, dur=0.6)

    # pick three different arrows: the numbers change, the move doesn't
    meas = VGroup(*[arrow(o, cam.scr(H3 @ P[:, j]), C.text, width=C.thin + 1.5) for j in range(3)])
    g.play(FadeOut(hats), LaggedStart(*[GrowArrow(a) for a in meas], lag_ratio=0.2), at=T.pick + 0.4, dur=1.0)
    Ps = Mat(PHP.astype(int), colors=C.text, size=52, h_buff=0.85, v_buff=0.7).move_to(Hs)
    hud.play(FadeOut(Hs), FadeIn(Ps), at=T.pick + 2.9, dur=1.2)
    hb.play(Transform(hk, backing(Ps, pad=0.3)), at=T.pick + 2.9, dur=1.2)
    lbl = tex("P^{-1}", "H", "P", size=40, color=C.muted).next_to(hk, DOWN, buff=0.2).align_to(hk, LEFT)
    hud.play(FadeIn(lbl), at=T.change + 0.2, dur=0.6)

    # ── the determinant, up close: video 006 ──
    card_sh = Polygon(*[np.array([x, y, 0]) for x, y in ((0, 0), (0.75, 0.25), (1.0, 0.85), (0.25, 0.6))],
                      stroke_color=C.area, stroke_width=2.5, fill_color=C.area, fill_opacity=0.3)
    card = VGroup(card_sh, tex(r"\det", size=44)).arrange(RIGHT, buff=0.3)
    card_box = SurroundingRectangle(card, buff=0.3, color=C.frame, stroke_width=1.5, fill_color=C.bg, fill_opacity=1)
    cardg = VGroup(card_box, card).move_to([5.0, -2.8, 0])
    hud.play(FadeIn(cardg, shift=0.3 * LEFT), at=T.det_video + 0.9, dur=0.7)
    finish(s)
