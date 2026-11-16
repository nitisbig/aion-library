"""Ch1 · Nine numbers in a box (2/2): a picture is a matrix too. Zoom into our own die frame until the pixels are
squares, each one a brightness number (0–255); pull back: 480 × 480 of them. Tables of grades and prices sit there,
inert; so how did nine numbers pick up a whole space and turn it? Stop reading the numbers, watch what they do."""
from functools import lru_cache

from aion import *

from beats import T
from shots import (H3, I3, Cam, Mat, backdrop, die_height, die_rgba, finish, lattice, live, panel, parked_system, photo, tex)

E = "smooth"
N = 480
PH, PC = 5.6, (0.0, 0.25)                               # the picture: height, centre
RES = 760                                               # output pixels across (nearest neighbour)
W1, X0F, Y0F = 12, 220, 98                              # the deepest crop: 12 × 12 pixels from (row 98, col 220)
PX, PY = X0F / (1 - W1 / N), Y0F / (1 - W1 / N)          # zoom about this point lands exactly on that crop
SMALL = 0.55                                            # the parked picture's scale
PL = (-4.3, 0.75)


@lru_cache(maxsize=1)
def gray():
    return (photo() * 255).round().astype(np.uint8)


def crop(u):
    """Nearest-neighbour view of the picture at zoom u (0 whole picture → 1 the 12 × 12 crop)."""
    w = N * (W1 / N) ** u
    x0, y0 = PX * (1 - w / N), PY * (1 - w / N)
    idx = (np.arange(RES) + 0.5) * w / RES
    cols = np.clip((x0 + idx).astype(int), 0, N - 1)
    rows = np.clip((y0 + idx).astype(int), 0, N - 1)
    g = gray()[np.ix_(rows, cols)]
    return np.dstack([g, g, g, np.full_like(g, 255)])


@scene(T.cut_photo, T.cut_ch2)
def s03_photo(s):
    backdrop(s)
    end = keys((T.cut_ch2 - 0.7, 1.0), (T.cut_ch2 - 0.05, 0.0), lead=0)
    m = s.manim(z=3, opacity=end)
    hb = s.manim(z=4.9, parallax=0.0, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    pk, pg = parked_system()                            # the equations stay parked from s02
    hb.add(pk, at=T.cut_photo)
    hud.add(pg, at=T.cut_photo)

    # ── a single frame from a moment ago; zoom in until it breaks into squares ──
    z0, z1 = T.zoom + 0.2, T.zoom + 3.1
    p0, p1 = T.bright + 1.0, T.bright + 3.0
    u = keys((z0, 0.0), (z1, 1.0, "easy_ease"), (p0, 1.0), (p1, 0.0, "easy_ease"), lead=0)
    sh0, sh1 = T.keep_mind + 2.2, T.keep_mind + 3.4    # "So a matrix can be a table": the picture steps aside
    k = keys((sh0, 0.0), (sh1, 1.0, E), lead=0)
    pos = lambda t: (PC[0] + k(t) * (PL[0] - PC[0]), PC[1] + k(t) * (PL[1] - PC[1]))  # noqa: E731
    scl = lambda t: 1 + k(t) * (SMALL - 1)                                            # noqa: E731
    s.add(FramesLayer(lambda t: crop(u(t)), height=PH, pos=pos, scale=scl, z=2, start=T.cut_photo,
                      during=[(z0, z1), (p0, p1)],
                      opacity=keys((T.picture, 0.0), (T.picture + 0.8, 1.0), (T.cut_ch2 - 0.7, 1.0),
                                   (T.cut_ch2 - 0.05, 0.0), lead=0)))
    fr = Rectangle(width=PH, height=PH, stroke_color=C.frame, stroke_width=C.thin).move_to([*PC, 0])
    m.play(FadeIn(fr), at=T.picture, dur=0.8)

    # at the deepest zoom: crisp squares, each one a number
    cell = PH / W1
    x_l, y_t = PC[0] - PH / 2, PC[1] + PH / 2
    edges = VGroup(*[Line([x_l + i * cell, y_t, 0], [x_l + i * cell, y_t - PH, 0]) for i in range(1, W1)],
                   *[Line([x_l, y_t - i * cell, 0], [x_l + PH, y_t - i * cell, 0]) for i in range(1, W1)])
    edges.set_stroke(C.bg, 1.5)
    nums = VGroup()
    for r in range(W1):
        for c in range(W1):
            v = int(gray()[Y0F + r, X0F + c])
            nums.add(tex(str(v), size=22, color=C.bg if v > 120 else C.data)
                     .move_to([x_l + (c + 0.5) * cell, y_t - (r + 0.5) * cell, 0]))
    m.play(FadeIn(edges), at=z1 - 0.2, dur=0.4)
    m.play(LaggedStart(*[FadeIn(n_) for n_ in nums], lag_ratio=0.006), at=T.squares + 1.1, dur=1.2)
    m.play(FadeOut(nums), FadeOut(edges), at=p0 - 0.4, dur=0.4)

    # hundreds of rows, hundreds of columns
    dims = tex("480", r"\times", "480", size=40, color=C.muted).next_to(fr, DOWN, buff=0.25)
    m.play(FadeIn(dims, shift=0.1 * UP), at=T.hundreds + 0.1, dur=0.6)
    fr_s = Rectangle(width=PH * SMALL, height=PH * SMALL, stroke_color=C.frame, stroke_width=C.thin).move_to([*PL, 0])
    dims_s = dims.copy().scale(0.85).next_to(fr_s, DOWN, buff=0.2)
    m.play(Transform(fr, fr_s), Transform(dims, dims_s), at=sh0, dur=sh1 - sh0, ease=E)

    # ── tables can't rotate anything ──
    grades = Mat([[82, 91, 77], [68, 74, 90], [95, 88, 71]], colors=C.data, size=48, h_buff=0.95, v_buff=0.72)
    grades.move_to([1.2, 1.25, 0])
    prices = Mat([["2.50"], ["1.20"], ["4.80"], ["3.00"]], colors=C.data, size=48, v_buff=0.62)
    prices.move_to([4.6, 1.25, 0])
    hud.play(FadeIn(grades, shift=0.15 * LEFT), at=T.grades + 0.3, dur=0.7)
    hud.play(FadeIn(prices, shift=0.15 * LEFT), at=T.prices + 0.4, dur=0.7)

    # ... so how did nine numbers pick up a whole space and turn it? (a small replay of the opening)
    bx = (0.4, -3.55, 6.6, -0.75)
    pn = panel(*bx)
    hb.play(FadeIn(pn), at=T.question + 6.9, dur=0.5)
    Hs = Mat(H3, size=30, h_buff=0.5, v_buff=0.4)
    Hs.move_to([bx[0] + 0.25 + Hs.width / 2, bx[3] - 0.2 - Hs.height / 2, 0])
    hud.play(FadeIn(Hs), at=T.question + 7.1, dur=0.5)
    cam = Cam(-30.0, 22.0, origin=(4.1, -2.2), unit=0.48)
    a0, a1 = T.turn_space + 0.1, T.turn_space + 1.8
    Ml = keys((a0, I3), (a1, H3, E), lead=0)
    lat_op = keys((T.question + 7.2, 0.0), (T.question + 7.8, 1.0), (T.cut_ch2 - 0.7, 1.0), (T.cut_ch2 - 0.05, 0.0),
                  lead=0)
    lt = s.manim(z=4.95, parallax=0.0, opacity=lat_op)
    lt.add(lattice(cam, I3, n=1, box=2.6, width=1.2), at=T.question + 7.2)
    live(lt, lambda t: lattice(cam, Ml(t), n=1, box=2.6, width=1.2), (a0, a1))
    s.add(FramesLayer(lambda t: die_rgba(0.5 * Ml(t), az=-30.0, el=22.0, size=360), height=die_height(0.48),
                      pos=(4.1, -2.2), z=4.97, parallax=0.0, start=T.question + 7.1, during=[(a0, a1)],
                      opacity=lat_op))

    # stop reading the numbers; start watching what they do
    for mob in (grades, prices):
        hud.play(mob.animate.set_color(C.ghost), at=T.watching - 0.1, dur=0.8)
    hud.play(Indicate(Hs, color=C.text, scale_factor=1.15), at=T.watching + 0.2, dur=0.8)
    finish(s)
