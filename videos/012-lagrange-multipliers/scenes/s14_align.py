"""s14: zoom into the kiss. Both gradients stand on the same tangent line, so one must be a multiple of the other."""
from aion import *

from beats import T
from classic import *

LAM = CAST["trail_lambda"]
K = 0.5


@scene(T.cut_ch3, T.cut_compass)
def s14_align(s):
    stage(s)
    c = mp(BEST)
    s.camera.frame(T.share + 0.9, center=(float(c[0]), float(c[1]) - 0.1), zoom=2.4, dur=1.8)
    progress(s, 3, "The gradients align")
    w = s.manim(z=2)
    w.add(*[poly([mp(q) for q in p[::2]], C.text, 2.2) for p in contour_paths(float(BEST_H))])
    d = trail_tangent(BEST_S)
    d = d / np.linalg.norm(d)
    gf, gg = hill_grad(*BEST), trail_grad(*BEST)
    w.add(walker(c).scale(0.55))
    w.play(Create(poly([c - p3(d) * 1.35, c + p3(d) * 1.35], C.tang, 2.2)), at=T.share + 1.8, dur=0.7, ease=E)
    w.play(GrowArrow(arrow(c, c + p3(gf) * K, C.obj, width=3.6, tip=0.15)), at=T.each, dur=0.6)
    w.play(GrowArrow(arrow(c, c + p3(gg) * K, C.con, width=3, tip=0.13)), at=T.each + 1.0, dur=0.6)
    n = gg / np.linalg.norm(gg)
    r = 0.11
    w.play(Create(poly([c + p3(d) * r, c + p3(d + n) * r, c + p3(n) * r], C.text, 1.6)), at=T.both, dur=0.4)
    w.play(Create(DashedLine(c - p3(n) * 1.15, c + p3(n) * 0.85, color=C.text, stroke_width=1.4, dash_length=0.06)), at=T.common, dur=0.6, ease=E)
    k = keys((T.stretch + 0.3, 1.0), (T.longer + 0.9, LAM), default_ease=E)
    live(w, lambda t: VGroup() if abs(float(k(t))) < 0.04 else arrow(c, c + p3(gg) * K * float(k(t)), C.lam, width=1.5, tip=0.1), (T.stretch + 0.3, T.cut_compass))
    h = hud(s)
    board(h, [(tex(r"\nabla f", ",", r"\nabla g", r"\perp", r"\text{tangent}", size=40, colors={0: C.obj, 2: C.con}), T.both)])
    board(h, [(tex(r"\nabla f", "=", r"\lambda", r"\nabla g", size=84, colors={0: C.obj, 2: C.lam, 3: C.con}), T.grad_eq - 0.1), (lab("Lagrange multiplier", 30, C.lam), T.greek + 0.2)], "d")
    board(h, [(tex(r"\lambda", r"\approx", f"{LAM:.2f}", size=52, colors={0: C.lam}), T.longer + 0.5), (lab("opposite arrows", 26, C.muted), T.longer + 1.0)], "ur")
    curtain(s, a=False, b=True)
