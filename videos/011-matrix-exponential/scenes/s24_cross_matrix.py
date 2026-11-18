"""s24 cross matrix (ch6): the cross product is a matrix. n × r = [[0, −n_z, n_y], [n_z, 0, −n_x], [−n_y, n_x, 0]] r:
zeros down the diagonal, the axis coordinates around them, each paired with its own negative. Call it K; every point's
velocity is the spin rate times K times its position, ṙ = Ω K r. The globe slides left and keeps turning."""
from aion import *

import ch6
from beats import T
from ch6 import globe_frame
from shots import AXIS_N, K_AXIS, backdrop, finish, globe_layers, live, tex

assert np.allclose(K_AXIS @ np.array([0.3, -0.5, 0.8]), np.cross(AXIS_N, [0.3, -0.5, 0.8]))


@scene(T.cut_K, T.cut_rod)
def s24_cross_matrix(s):
    backdrop(s)
    m = s.manim(z=3)
    globe_layers(s, ch6.theta, ch6.center, ch6.radius, ch6.pole, z=1, start=T.cut_K, end=T.cut_rod)
    live(m, globe_frame, (T.cut_K, T.cut_rod))

    # ── n × r as a matrix times r ──
    rows = [["0", "-n_z", "n_y"], ["n_z", "0", "-n_x"], ["-n_y", "n_x", "0"]]
    K = Mat(rows, size=40, h_buff=1.1, v_buff=0.72)
    for i in range(3):
        for j in range(3):
            K.cell(i, j).set_color(C.muted if i == j else C.eigen)
    lhs = tex(r"\mathbf n", r"\times", r"\mathbf r", "=", size=48, colors={0: C.eigen, 2: C.vec})
    rv = tex(r"\mathbf r", size=48, color=C.vec)
    eq = VGroup(lhs, K, rv).arrange(RIGHT, buff=0.22).move_to([3.4, 1.3, 0])
    m.play(FadeIn(lhs, shift=0.1 * DOWN), at=T.K_matrix + 0.6, dur=0.6)
    m.play(FadeIn(K), FadeIn(rv), at=T.K_matrix + 1.0, dur=0.8)

    # zeros down the diagonal; each entry paired with its own negative
    diag = VGroup(*[K.cell(i, i) for i in range(3)])
    m.play(diag.animate.set_color(C.text), at=T.zeros_diag + 0.2, dur=0.4)
    m.play(Indicate(diag, color=C.text, scale_factor=1.35), at=T.zeros_diag + 0.6, dur=0.8)
    for k, (a, b) in enumerate((((0, 1), (1, 0)), ((0, 2), (2, 0)), ((1, 2), (2, 1)))):
        pair = VGroup(K.cell(*a), K.cell(*b))
        m.play(Indicate(pair, color=C.gen, scale_factor=1.35), at=T.pairs + 0.1 + 0.55 * k, dur=0.6)

    # call it K
    br = Brace(K, DOWN, buff=0.12, color=C.gen)
    kl = tex("K", size=52, color=C.gen).next_to(br, DOWN, buff=0.12)
    m.play(FadeIn(br), FadeIn(kl, shift=0.1 * UP), at=T.call_K + 0.1, dur=0.5)
    vel = tex(r"\dot{\mathbf r}", "=", r"\Omega", r"\,K", r"\mathbf r", size=60, colors={0: C.gen, 3: C.gen, 4: C.vec})
    vel.move_to([3.4, -2.55, 0])
    m.play(FadeIn(vel, shift=0.1 * DOWN), at=T.vel_K + 0.6, dur=0.7)
    m.play(FadeOut(VGroup(eq, br, kl, vel)), at=T.cut_rod - 0.4, dur=0.4)
    finish(s)
