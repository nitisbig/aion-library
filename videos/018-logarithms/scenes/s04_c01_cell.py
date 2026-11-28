"""c01_s01 · One cell. Storyboard: plan/scene_plan.md § c01_s01.

One cell divides into two, four, eight, sixteen on the spoken words, then runs on to 1024 (cells.py: a seeded packing
per generation, daughters sliding apart from their mother, drawn with skia). Two counters float in the open column:
divisions (steps) and cells (value), then 2¹⁰ = 1024. The question turns around: the colony recombines to one cell
while the division tally counts up to ten, and the answer is written as log₂ 1024 = 10.
"""
import math

from aion import *

from beats import T
from cells import CELL_C, CELL_H, GENS, cells_frame
from ch1 import N, chain
from kit import P3, add_rail, chapter_card, ctex, ramp, sans, tex

X = 4.55


def _landings():
    first = [(T.c01_s01_two_cells, float(T.c01_s01_two_cells) - float(T.c01_s01_divide) - 0.1),
             (T.c01_s01_four, 1.2), (T.c01_s01_eight, 0.85), (T.c01_s01_sixteen, 0.7)]
    t5 = float(T.c01_s01_ten_divisions) - 2.0
    rest = [(t5 + 0.75 * j, 0.65) for j in range(6)]
    return [(float(a), float(d)) for a, d in first + rest]


LAND = _landings()
R0 = float(T.c01_s01_how_many_divisions) - 1.5
STEP = (float(T.c01_s01_answer_is_ten) - 0.15 - R0) / GENS


def undone(t):
    return min(max((t - R0) / STEP, 0.0), float(GENS))


def gen_at(t):
    if t >= R0:
        return GENS - undone(t)
    g = 0.0
    for k, (land, d) in enumerate(LAND, start=1):
        if t >= land:
            g = float(k)
        elif t > land - d:
            return k - 1 + (t - (land - d)) / d
        else:
            break
    return g


_TEX = {}


def _num(n, color):
    key = (n, color)
    if key not in _TEX:
        _TEX[key] = tex(str(n), 96, color)
    return _TEX[key].copy()


@scene(T.c01_s01, T.c01_s02)
def s04_c01_cell(s):
    s.solid(C.bg, z=-200)
    end = float(T.c01_s02)
    chapter_card(s, 1, at=float(T.c01_s01) - 0.45, out=float(T.c01_s01) + 0.95)
    add_rail(s, 1)

    s.add(FramesLayer(cells_frame(gen_at, C.cell), height=CELL_H, pos=CELL_C, z=0,
                      opacity=fade(float(T.c01_s01) + 1.7, dur=0.8, out=end - 0.35, out_dur=0.7),
                      fx=[Glow(C.cell, strength=C.glow * 0.3, radius=C.glow_r)]))

    turn = float(T.c01_s01_turn)
    t_on = float(T.c01_s01_two_cells) - 0.2

    def div_op(t):
        if t < turn + 1.0:
            return ramp(t, t_on - 0.5, 0.5) * (1 - ramp(t, turn + 0.2, 0.6))
        return ramp(t, R0 - 0.5, 0.5) * (1 - ramp(t, end - 0.9, 0.6))

    def counters(t):
        g = gen_at(t)
        if t < turn + 1.0:
            n = int(math.floor(g + 1e-9))
        else:
            n = int(math.floor(undone(t) + 1e-9))
        g1 = VGroup()
        a = div_op(t)
        if a > 0.01:
            d = _num(n, C.steps).move_to(P3(X, 2.05))
            if t > float(T.c01_s01_answer_is_ten) - 0.3:
                d.scale(1 + 0.15 * math.sin(math.pi * ramp(t, float(T.c01_s01_answer_is_ten) - 0.1, 0.6)))
            g1.add(d.set_opacity(a))
        if t < turn + 1.0:
            c = _num(2 ** n, C.value)
        else:
            c = _num(1024, C.value)
        c.move_to(P3(X, 0.35)).set_opacity(ramp(t, t_on - 0.5, 0.5) * (1 - ramp(t, end - 0.9, 0.6)))
        g1.add(c)
        return g1
    m = s.manim(z=10, parallax=0.0)
    m.redraw(counters, during=(t_on - 0.6, end))
    lab = s.manim(z=10, parallax=0.0, opacity=fade(t_on, dur=0.5, out=end - 0.35, out_dur=0.6))
    lab.add(sans("cells", 24, C.muted).move_to(P3(X, -0.4)))
    lab2 = s.manim(z=10, parallax=0.0, opacity=Track(div_op))
    lab2.add(sans("divisions", 24, C.muted).move_to(P3(X, 1.3)))

    # the camera pulls back as the colony outgrows the frame, and pushes in again as it recombines
    s.camera.frame(LAND[3][0], center=(1.38, -0.66), zoom=0.68, dur=LAND[-1][0] - LAND[3][0] + 0.3, ease="smooth")
    s.camera.frame(R0, center=(0.0, 0.0), zoom=1.0, dur=GENS * STEP, ease="smooth")

    # the doubling chain along the bottom: one value per generation, one ×2 per division; turned around, each
    # ×2 lights in the steps colour as its division is undone, so the count of ×2s is the answer
    vals, tags = chain()
    m.play(FadeIn(vals[0], shift=0.1 * UP), at=float(T.c01_s01) + 1.9, dur=0.5)
    for k, (land, d) in enumerate(LAND, start=1):
        m.play(FadeIn(tags[k - 1], shift=0.1 * RIGHT), at=land - d, dur=min(0.45, d), lead=0.0)
        m.play(FadeIn(vals[k], shift=0.1 * UP), at=land - 0.1, dur=0.4, lead=0.0)
    for j in range(1, N + 1):
        m.play(tags[N - j].animate.set_color(C.steps).scale(1.25), at=R0 + STEP * j - 0.15, dur=0.3, lead=0.0)

    pw = ctex([("2", C.base), ("^{10}", C.steps), ("=", None), ("1024", C.value)], 56).move_to(P3(X, -1.35))
    m.play(FadeIn(pw, shift=0.1 * UP), at=LAND[-1][0] + 0.4, dur=0.6)
    m.play(FadeOut(pw), at=turn + 0.2, dur=0.6)
    q = ctex([(r"\log_{", None), ("2", C.base), ("}", None), ("1024", C.value), ("=", None), ("10", C.steps)], 56)
    q.move_to(P3(X, -1.35))
    m.play(Write(q), at=T.c01_s01_logarithm, dur=0.8)
    m.play(FadeOut(q), at=end - 0.3, dur=0.5)
