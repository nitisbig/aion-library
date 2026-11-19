"""s22 blur: a shaking camera averages each pixel with its neighbours, and averaging is a matrix. That matrix has an exact inverse, and applying it
brings every edge back."""
from aion import *

from beats import T
from deblur import row_cells, smear_rgba
from film3 import frame
from shots import EASE, live, p3, panel, tex

PIC, PH = (-3.55, 0.0), 5.4
N, CELL, HALF = 13, 0.36, 3
X0, Y_TOP, Y_LOW = 3.6 - (N - 1) / 2 * CELL, 2.72, 1.42
ROW = 250


def cx(i):
    return X0 + i * CELL


@scene(T.cut_blur, T.cut_noise)
def s22_blur(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_blur, T.cut_noise)], z=0))
    mk = s.manim(z=3, parallax=0.0)                   # the row of pixels
    m = s.manim(z=5, parallax=0.0)                    # frame and symbols

    # ── the picture smears, and later un-smears ──
    length = keys((T.smeared - 0.1, 1.0), (T.smeared + 1.4, 49.0, EASE), (T.apply_blur + 0.1, 49.0), (T.apply_blur + 1.3, 1.0, EASE), lead=0)
    s.add(FramesLayer(lambda t: smear_rgba(float(length(t))), height=PH, pos=PIC, during=[(T.cut_blur, T.cut_noise)],
                      opacity=fade(T.cut_blur + 0.05, dur=0.5), z=1))
    m.play(FadeIn(panel(PIC[0] - PH / 2, PIC[1] - PH / 2, PIC[0] + PH / 2, PIC[1] + PH / 2, fill=False)), at=T.cut_blur + 0.05, dur=0.5, lead=0)

    # ── one row: each output pixel averages its neighbours ──
    row_y = PIC[1] + PH * (0.5 - (ROW + 0.5) / 480)
    marker = Line([PIC[0] - PH / 2, row_y, 0], [PIC[0] + PH / 2, row_y, 0], color=C.fwd, stroke_width=2.4)
    t_in, t_out = T.average - 1.25, T.apply_blur - 0.5
    m.play(Create(marker), at=t_in, dur=0.5)
    m.play(FadeOut(marker), at=t_out, dur=0.4)

    top = row_cells(N, block=30, row=ROW)
    low = np.array([top[max(0, i - HALF):i + HALF + 1].mean() for i in range(N)])
    slide = key(T.average, HALF, N - 1 - HALF, dur=1.7, ease="linear")
    show = fade(t_in, dur=0.45, out=t_out)

    def cell(i, y, v, op):
        return Square(CELL - 0.03, stroke_width=0, fill_color=interpolate_color(ManimColor(C.bg), ManimColor(C.home), float(v)), fill_opacity=op).move_to([cx(i), y, 0])

    def strip(t):
        op = float(show(t))
        if op < 0.01:
            return VGroup()
        j = int(round(float(slide(t))))
        g = VGroup(*[cell(i, Y_TOP, top[i], op) for i in range(N)])
        g.add(*[cell(i, Y_LOW, low[i], op) for i in range(HALF, j + 1)])
        g.add(*[Square(CELL - 0.03, color=C.frame, stroke_width=1.2, stroke_opacity=0.7 * op).move_to([cx(i), Y_LOW, 0]) for i in range(N)])
        g.add(*[Line([cx(i), Y_TOP - CELL / 2, 0], [cx(j), Y_LOW + CELL / 2, 0], color=C.fwd, stroke_width=2.2, stroke_opacity=op) for i in range(j - HALF, j + HALF + 1)])
        g.add(Rectangle(width=(2 * HALF + 1) * CELL, height=CELL + 0.06, color=C.fwd, stroke_width=2.6, stroke_opacity=op).move_to([cx(j), Y_TOP, 0]))
        g.add(Square(CELL + 0.04, color=C.fwd, stroke_width=2.6, stroke_opacity=op).move_to([cx(j), Y_LOW, 0]))
        return g
    live(mk, strip, (t_in, T.average + 1.8), (t_out, t_out + 0.45))

    # ── that averaging is a matrix, and the matrix has an inverse ──
    h, c = 3.0, (3.75, -1.42)
    t_a, t_b = T.averages + 1.45, T.has_inv + 0.45
    heat = panel(c[0] - h / 2, c[1] - h / 2, c[0] + h / 2, c[1] + h / 2, fill=False)
    m.play(FadeIn(heat), at=t_a, dur=0.6)
    sym_a = tex("A", size=72, color=C.fwd).move_to([1.45, c[1], 0])
    sym_b = tex(r"A^{-1}", size=72, color=C.back).move_to([1.3, c[1], 0])
    m.play(FadeIn(sym_a), at=t_a, dur=0.6)
    m.play(FadeOut(sym_a), FadeIn(sym_b), at=t_b, dur=0.6)
    m.play(Indicate(sym_b, color=C.back, scale_factor=1.15), at=T.apply_blur, dur=0.9)
    m.play(FadeOut(heat), FadeOut(sym_b), at=T.cut_noise - 0.45, dur=0.4)
