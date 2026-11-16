"""Ch6 · Apply it again and again (2/3): a round cloud of points, multiplied by A round after round (rescaled by ¼ so
it stays on screen), thins into the violet (1, 1) line: everything drifts toward the strongest eigenvector."""
from aion import *

from beats import T
from shots import A, FRAME, I2, backdrop, backing, finish, grid_lines, pt, rail, tex

E = "smooth"
O, U = (1.6, -0.5), 0.6                                # same stage as s14
E1, E2 = np.array([1.0, 1.0]) / np.sqrt(2), np.array([1.0, -2.0]) / np.sqrt(5)
STEP = A / 4.0                                         # one round, rescaled by the top eigenvalue
N_PTS, RAD = 1500, 3.4


def cloud0():
    r = np.random.default_rng(9)
    a = r.random(N_PTS) * 2 * np.pi
    rad = RAD * np.sqrt(r.random(N_PTS))
    return np.c_[rad * np.cos(a), rad * np.sin(a)]


def full_line(d, color, width, op=1.0):
    d = np.asarray(d, float) / np.linalg.norm(d)
    return Line(pt(O, U, -24 * d), pt(O, U, 24 * d), color=color, stroke_width=width, stroke_opacity=op)


@scene(T.cut_power, T.cut_rank)
def s15_power(s):
    backdrop(s)
    end = keys((T.web + 0.4, 1.0), (T.cut_rank - 0.05, 0.0), lead=0)
    ghost = s.manim(z=0, opacity=end)
    m = s.manim(z=1, opacity=end)
    hb = s.manim(z=4.9, parallax=0.0, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    rl = s.manim(z=5.1, parallax=0.0)
    rail(rl, 5)

    ghost.play(FadeIn(grid_lines(I2, O, U, FRAME, color=C.ghost)), at=T.cut_power + 0.1, dur=0.6)
    l1 = full_line(E1, C.eigen, C.stroke, 0.35)
    l2 = full_line(E2, C.eigen, C.stroke, 0.35)
    m.play(FadeIn(l1), FadeIn(l2), at=T.heading - 0.6, dur=0.8)

    # ── the rounds: x_{k+1} = (A/4) x_k, each eased along a straight path ──
    starts = [T.again - 0.9, T.again + 0.4, T.again + 1.7, T.again + 3.0, T.wins + 0.6, T.wins + 2.1]
    X = [cloud0()]
    for _ in starts:
        X.append(X[-1] @ STEP.T)
    ks = [keys((t0, 0.0), (t0 + 0.9, 1.0, E), lead=0) for t0 in starts]

    def pos(t):
        k = sum(1 for t0 in starts if t >= t0 + 0.9)
        if k < len(starts) and t > starts[k]:
            w = ks[k](t)
            P = (1 - w) * X[k] + w * X[k + 1]
        else:
            P = X[k]
        return np.asarray(O) + U * P
    s.add(PointsLayer(pos, color=C.text, size=3.5, glow=0.0, additive=False, z=2,
                      opacity=fade(T.cloud + 0.2, dur=0.8, out=T.web + 0.4, out_dur=1.4)))

    # the round counter: A, A², A³, … (×¼ each round, small and muted)
    def counter(k):
        main = tex("A" if k == 1 else f"A^{{{k}}}", size=60)
        sc = tex(r"\times\tfrac14" if k == 1 else rf"\times 4^{{-{k}}}", size=36, color=C.muted)
        return VGroup(main, sc).arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
    slot = np.array([-7.11 + C.margin + 0.35, 3.55 - C.margin - 0.45, 0])
    cs = [counter(k).move_to(slot, aligned_edge=LEFT) for k in range(1, len(starts) + 1)]
    box = backing(VGroup(*cs), pad=0.28)
    hb.play(FadeIn(box), at=starts[0] - 0.2, dur=0.4)
    hud.play(FadeIn(cs[0]), at=starts[0], dur=0.4)
    for k in range(1, len(cs)):
        hud.play(FadeOut(cs[k - 1]), FadeIn(cs[k]), at=starts[k], dur=0.35)

    # the strongest direction wins: its line lights up, the other one fades
    l1b = full_line(E1, C.eigen, C.stroke + 1.5)
    m.play(FadeIn(l1b), FadeOut(l2), at=T.lined_up + 0.2, dur=0.8)
    lam = tex(r"\lambda", "=", "4", size=48, color=C.eigen).move_to(pt(O, U, 4.6 * E1) + np.array([1.0, -0.2, 0]))
    m.play(FadeIn(lam, scale=1.3), at=T.drifts + 1.0, dur=0.5, ease="out_back")
    finish(s)
