"""s24 second shadow: from one direction a flipped tooth changes nothing, so all sixteen keys fit. Turn the light and the same flip lands somewhere
new. The profiles are the key's real line integrals, and the count of keys that fit is computed, not typed."""
from aion import *

from beats import T
from film3 import A0, A1, BINS, HALF, TEETH, frame, keys_that_fit, profile
from shots import EASE, chapter_card, key_mob, lab, p3, tex

def strip(mid, alpha, values, upto=1.0, length=2 * HALF, thick=0.2, mark=None):
    """A detector tangent to the light: each cell is shaded by how much key its ray crossed."""
    u = np.array([-np.sin(alpha), np.cos(alpha)])
    w, top = length / BINS, max(float(profile(A0, TEETH).max()), 1e-9)
    g = VGroup()
    for i, v in enumerate(values):
        if (i + 0.5) / BINS > upto or v < 0.01 * top:
            continue
        col = C.null if mark is not None and mark[i] else C.shadow
        g.add(Rectangle(width=w * 1.05, height=thick, stroke_width=0, fill_color=col, fill_opacity=float(min(v / top, 1.0)) ** 0.7)
              .rotate(alpha + PI / 2).move_to(p3(mid + u * ((i + 0.5) / BINS - 0.5) * length)))
    g.add(Rectangle(width=length, height=thick, stroke_color=C.frame, stroke_width=1.2).rotate(alpha + PI / 2).move_to(p3(mid)))
    return g


@scene(T.cut_second, T.cut_ct)
def s24_second_shadow(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_second, T.cut_ct)], z=0))
    mb = s.manim(z=4, parallax=0.0)                   # the plate behind the sixteen keys
    m = s.manim(z=5, parallax=0.0)                    # the sixteen keys and the tags
    mh = s.manim(z=8, parallax=0.0)                   # the chapter card

    # ── chapter card: the key's shadow, drawn ──
    drawn = strip(np.array([0.0, 0.0]), -PI / 2, profile(A0, TEETH), length=6.0, thick=0.34)
    chapter_card(mh, drawn, "Shadows", T.cut_second, T.brings + 0.05)

    # ── sixteen keys fit one shadow ──
    plate = Rectangle(width=4.25, height=5.9, stroke_color=C.frame, stroke_width=1.6, fill_color=C.bg, fill_opacity=0.96).move_to([4.55, 0.55, 0])
    mb.play(FadeIn(plate), at=T.one_sh - 0.1, dur=0.5)
    tag1, tag2 = lab("1 shadow", size=38), lab("2 shadows", size=38)
    for t_ in (tag1, tag2):
        t_.move_to([4.55, -1.85, 0])
    m.play(FadeIn(tag1), at=T.one_sh, dur=0.5)
    m.play(FadeOut(tag1), FadeIn(tag2), at=T.turn_light + 1.8, dur=0.5)

    minis = {}
    for n in range(16):
        p = tuple(1 if n >> b & 1 else -1 for b in range(4))
        minis[p] = key_mob(center=(3.15 + 0.93 * (n % 4), 1.7 - 0.72 * (n // 4)), teeth=p, scale=0.25, width=1.6)
    m.play(LaggedStart(*[FadeIn(v, scale=1.1) for v in minis.values()], lag_ratio=0.06), at=T.one_sh + 0.2, dur=1.4)
    n1, n2 = len(keys_that_fit([A0])), len(keys_that_fit([A0, A1]))
    c1 = VGroup(tex(str(n1), size=68, color=C.key), lab("keys fit", size=36)).arrange(RIGHT, buff=0.26).move_to([4.55, 2.85, 0])
    c2 = VGroup(tex(str(n2), size=68, color=C.key), lab("key fits" if n2 == 1 else "keys fit", size=36)).arrange(RIGHT, buff=0.26).move_to([4.55, 2.85, 0])
    m.play(FadeIn(c1), at=T.one_sh + 0.5, dur=0.5)

    # ── each new shadow rules keys out ──
    fit = set(keys_that_fit([A0, A1]))
    others = VGroup(*[v for k, v in minis.items() if k not in fit])
    m.play(others.animate.set_opacity(0.16), at=T.new_eq, dur=1.1, ease=EASE)
    m.play(FadeOut(c1), FadeIn(c2), at=T.fewer, dur=0.5)
    s.solid(C.bg, z=50, opacity=key(T.cut_ct - 0.42, 0.0, 1.0, dur=0.4, lead=0))
