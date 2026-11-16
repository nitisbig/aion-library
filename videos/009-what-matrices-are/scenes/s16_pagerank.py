"""Ch6 · PageRank (3/3): seven pages, 3,000 readers clicking links (and now and then jumping anywhere, damping 0.85).
Every round is one multiplication by the click matrix G; the crowd settles on the same shares from any start: the
eigenvector of G with eigenvalue 1. B and D each have one incoming link, but B's comes from C, the most popular page."""
from aion import *

from beats import T
from shots import backdrop, backing, finish, rail, tex

NAMES = "ABCDEFG"
LINKS = {"A": "C", "B": "CG", "C": "AB", "D": "C", "E": "CD", "F": "AE", "G": "FC"}
POS = {"A": (0.5, 1.6), "B": (4.6, 1.75), "C": (2.6, -0.2), "D": (-0.8, -0.4), "E": (0.3, -2.5), "F": (2.9, -3.1),
       "G": (5.4, -1.5)}
DAMP, N_SURF, HOP = 0.85, 3000, 0.34                   # each hop takes HOP seconds
ARC = 0.45                                             # link arcs bend by this angle (so A→C and C→A separate)
NODE = 0.9                                             # node square side
LETTER = {"A": (-0.8, 0.1), "B": (0.0, 0.72), "C": (0.0, -0.74), "D": (-0.8, 0.0), "E": (-0.8, -0.3),
          "F": (-0.75, -0.55), "G": (0.8, 0.0)}           # label offsets, placed clear of the link arcs
SH = {"A": (0.0, 0.68), "B": (0.85, 0.0), "C": (0.0, 0.7), "D": (0.0, 0.68), "E": (-0.85, 0.15),
      "F": (0.8, -0.55), "G": (0.0, -0.7)}


def click_matrix():
    n = len(NAMES)
    S = np.zeros((n, n))
    for a, outs in LINKS.items():
        for b in outs:
            S[NAMES.index(b), NAMES.index(a)] = 1 / len(outs)
    return DAMP * S + (1 - DAMP) / n


G = click_matrix()
_w, _v = np.linalg.eig(G)
SHARE = np.real(_v[:, np.argmax(np.real(_w))])
SHARE = SHARE / SHARE.sum()                            # C .368, A .204, B .178, G .097, F .063, E .048, D .042


def simulate(start, rounds, seed):
    """Node index of every surfer after each round: (rounds + 1, N_SURF)."""
    r = np.random.default_rng(seed)
    out = [np.full(N_SURF, NAMES.index(start))]
    for _ in range(rounds):
        cur = out[-1]
        nxt = np.empty_like(cur)
        bored = r.random(N_SURF) > DAMP
        nxt[bored] = r.integers(0, len(NAMES), bored.sum())
        for i, a in enumerate(NAMES):
            sel = (cur == i) & ~bored
            outs = [NAMES.index(b) for b in LINKS[a]]
            nxt[sel] = np.array(outs)[r.integers(0, len(outs), sel.sum())]
        out.append(nxt)
    return np.array(out)


def bend(a, b):
    """Control point of the quadratic path that follows the link arc a→b (CurvedArrow(angle=-ARC) bulges left)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d, axis=-1, keepdims=True)
    right = np.stack([d[..., 1], -d[..., 0]], -1) / np.maximum(L, 1e-9)
    return (a + b) / 2 - 2 * (L / 2) * np.tan(ARC / 4) * right


@scene(T.cut_rank, T.cut_ch7)
def s16_pagerank(s):
    backdrop(s)
    end = keys((T.cut_ch7 - 0.7, 1.0), (T.cut_ch7 - 0.05, 0.0), lead=0)
    w = s.manim(z=1, opacity=end)                      # links
    nd = s.manim(z=3, opacity=end)                     # nodes, labels
    hb = s.manim(z=4.9, parallax=0.0, opacity=end)
    hud = s.manim(z=5, parallax=0.0, opacity=end)
    rl = s.manim(z=5.1, parallax=0.0)
    rail(rl, 5, drop=(6, T.counts + 0.9))

    P = {k: np.array([*v, 0.0]) for k, v in POS.items()}
    boxes = {k: RoundedRectangle(corner_radius=0.12, width=NODE, height=NODE, stroke_color=C.frame,
                                 stroke_width=C.thin + 0.5).move_to(P[k]) for k in NAMES}
    letters = {k: tex(k, size=40).move_to(P[k] + np.array([*LETTER[k], 0])) for k in NAMES}
    t0 = T.seven + 0.2
    nd.play(LaggedStart(*[Create(boxes[k]) for k in NAMES], lag_ratio=0.1), at=t0, dur=1.0)
    nd.play(LaggedStart(*[FadeIn(letters[k]) for k in NAMES], lag_ratio=0.1), at=t0 + 0.3, dur=1.0)

    links = {}
    for a, outs in LINKS.items():
        for b in outs:
            d = P[b] - P[a]
            u = d / np.linalg.norm(d)
            links[a + b] = CurvedArrow(P[a] + 0.55 * u, P[b] - 0.55 * u, angle=-ARC, color=C.muted,
                                       stroke_width=C.thin + 0.5, tip_length=0.16)
    w.play(LaggedStart(*[Create(l) for l in links.values()], lag_ratio=0.05), at=t0 + 0.8, dur=1.4)

    # ── the readers: two runs (start piled on D, then on F), one hop per round ──
    runs = []
    s1 = T.readers + 1.6                               # first hop
    r1 = [s1 + 0.5 * i for i in range(int((T.any_start - 0.3 - s1) / 0.5))]
    s2 = T.any_start + 1.0
    r2 = [s2 + 0.45 * i for i in range(int((T.cut_ch7 - 1.0 - s2) / 0.45))]
    runs.append(("D", r1, simulate("D", len(r1), 11), T.readers + 0.6, T.any_start - 0.3))
    runs.append(("F", r2, simulate("F", len(r2), 12), T.any_start + 0.2, T.cut_ch7 - 0.05))
    rr = np.random.default_rng(5)
    ang = rr.random(N_SURF) * 2 * np.pi
    jit = 0.36 * np.sqrt(rr.random(N_SURF))
    OFF = np.c_[jit * np.cos(ang), jit * np.sin(ang)]
    XY = np.array([POS[k] for k in NAMES])

    def surfers(run):
        _, hops, H, _, _ = run

        def pos(t):
            k = int(np.searchsorted(hops, t, side="right"))          # hops already started
            if k == 0:
                return XY[H[0]] + OFF
            frac = min(1.0, (t - hops[k - 1]) / HOP)
            frac = frac * frac * (3 - 2 * frac)
            a, b = XY[H[k - 1]] + OFF, XY[H[k]] + OFF
            if frac >= 1.0:
                return b
            c = bend(a, b)
            return (1 - frac) ** 2 * a + 2 * (1 - frac) * frac * c + frac ** 2 * b
        return pos
    for run in runs:
        _, _, _, a, b = run
        s.add(PointsLayer(surfers(run), color=C.text, size=2.2, glow=0.0, additive=False, z=2, alpha=0.8,
                          opacity=fade(a, dur=0.6, out=min(b, T.cut_ch7 - 0.7), out_dur=0.6)))

    # ── the click matrix G (a 7 × 7 heat map) and, once settled, the share vector p ──
    cell = 0.3
    gx, gy = -6.2, 0.9
    heat = VGroup()
    for i in range(7):
        for j in range(7):
            heat.add(Square(cell, stroke_width=0.6, stroke_color=C.ghost, fill_color=C.data,
                            fill_opacity=float(G[i, j]) / G.max()).move_to([gx + j * cell, gy - i * cell, 0]))
    gl = tex("G", size=52).next_to(heat, UP, buff=0.25)
    pv = VGroup(*[Square(cell, stroke_width=0.6, stroke_color=C.ghost, fill_color=C.eigen,
                         fill_opacity=float(SHARE[i]) / SHARE.max()).move_to([gx + 7 * cell + 0.45, gy - i * cell, 0])
                  for i in range(7)])
    pl = tex(r"\mathbf{p}", size=52, color=C.eigen).next_to(pv, UP, buff=0.25)
    eq = tex("G", r"\mathbf{p}", "=", r"\mathbf{p}", size=52, colors={1: C.eigen, 3: C.eigen})
    eq.next_to(VGroup(heat, pv), DOWN, buff=0.45).align_to(heat, LEFT)
    blk = VGroup(heat, gl, pv, pl, eq)
    hb.play(FadeIn(backing(blk, pad=0.28)), at=T.clicks + 0.2, dur=0.5)
    hud.play(FadeIn(gl), FadeIn(heat, lag_ratio=0.02), at=T.clicks + 0.4, dur=1.0)
    hud.play(FadeIn(pl), LaggedStart(*[FadeIn(q) for q in pv], lag_ratio=0.08), at=T.settled + 0.3, dur=1.0)
    hud.play(FadeIn(eq, shift=0.1 * UP), at=T.settled + 2.6, dur=0.7)

    # the settled shares beside each page
    shares = {k: tex(f".{int(round(SHARE[i] * 100)):02d}", size=36, color=C.eigen).move_to(P[k] + np.array([*SH[k], 0]))
              for i, k in enumerate(NAMES)}
    nd.play(LaggedStart(*[FadeIn(shares[k]) for k in NAMES], lag_ratio=0.06), at=T.far_more + 0.3, dur=0.9)

    # ── these two pages: one incoming link each; B's comes from C ──
    for k in "BD":
        nd.play(boxes[k].animate.set_stroke(C.area, width=C.stroke), at=T.two_pages + 0.4, dur=0.5)
    for key in ("CB", "ED"):
        w.play(links[key].animate.set_stroke(C.area, width=C.stroke).set_fill(C.area), at=T.one_link + 0.6, dur=0.6)
    nd.play(Indicate(boxes["C"], color=C.text, scale_factor=1.12), at=T.popular + 0.6, dur=0.8)
    nd.play(Indicate(shares["B"], color=C.area, scale_factor=1.3), at=T.counts + 0.1, dur=0.8)
    finish(s)
