"""s16: the proof in three lines, each tied to an arrow on the map, then the count: three equations, three unknowns."""
from aion import *

from beats import T
from classic import *


@scene(T.cut_proof, T.cut_ch4)
def s16_proof(s):
    stage(s)
    c = mp(BEST)
    s.camera.frame(T.proof - 0.1, center=(float(c[0]) - 2.5, float(c[1]) - 0.15), zoom=1.55, dur=1.3)
    progress(s, 3)
    m = s.manim(z=2)
    m.add(walker(c))
    d = trail_tangent(BEST_S) * 0.55
    v = arrow(c, c + p3(d), C.tang, tip=0.28)
    ag = arrow(c, c + p3(trail_grad(*BEST)) * 1.05, C.con, tip=0.28)
    af = arrow(c, c + p3(hill_grad(*BEST)) * 1.05, C.obj, tip=0.28)
    m.play(GrowArrow(v), at=T.path_r + 0.5, dur=0.6)
    m.play(GrowArrow(ag), at=T.g_dot - 0.2, dur=0.6)
    m.play(GrowArrow(af), at=T.f_dot - 0.2, dur=0.6)
    h = hud(s)
    z = 38
    board(h, [(tex(r"\mathbf{r}(t)", r",\quad", r"\mathbf{r}'(t)", size=z, colors={2: C.tang}), T.path_r + 0.5),
              (tex("g", r"(\mathbf{r}(t))=c", r"\;\Rightarrow\;", r"\nabla g", r"\cdot", r"\mathbf{r}'", "=0", size=z, colors={0: C.con, 3: C.con, 5: C.tang}), T.g_dot - 0.2),
              (tex(r"\tfrac{d}{dt}", "f", r"(\mathbf{r})=0", r"\;\Rightarrow\;", r"\nabla f", r"\cdot", r"\mathbf{r}'", "=0", size=z, colors={1: C.obj, 4: C.obj, 6: C.tang}), T.f_dot - 0.2),
              (tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=68, colors={0: C.obj, 2: C.lam, 3: C.con}), T.both_p + 1.2),
              (tex(r"\text{if }", r"\nabla g", r"\neq 0", size=36, colors={1: C.con}), T.as_long)], "l", out=T.count - 0.3, gap=0.32)
    board(h, [(tex("f_x", "=", r"\lambda", "g_x", size=56, colors={0: C.obj, 2: C.lam, 3: C.con}), T.two_eq), (tex("f_y", "=", r"\lambda", "g_y", size=56, colors={0: C.obj, 2: C.lam, 3: C.con}), T.two_eq),
              (tex("g", "=", "c", size=56, colors={0: C.con, 2: C.con}), T.one_con), (tex("x", ",", r"\;y", ",", r"\;\lambda", size=56, colors={4: C.lam}), T.three + 0.2),
              (lab("3 equations, 3 unknowns", 28, C.text), T.algebra - 0.3)], "l", at=T.count + 0.1, gap=0.3)
    curtain(s, a=False, b=True)
