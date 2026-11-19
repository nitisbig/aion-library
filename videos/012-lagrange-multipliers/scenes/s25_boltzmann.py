"""s25: lambda is temperature. Maximizing entropy with fixed energy gives Boltzmann's law, and beta is the price of energy in entropy."""
from aion import *

from beats import T
from classic import *

N = 2200
BX = (-6.95, -3.85, 6.95, 3.85)


def triangle(u, a, b):
    """Reflect a coordinate between two walls (exact bouncing, pure in t)."""
    w = b - a
    v = np.mod(u - a, 2 * w)
    return a + np.where(v > w, 2 * w - v, v)


@scene(T.cut_gas, T.cut_ch8)
def s25_boltzmann(s):
    backdrop(s)
    progress(s, 7)
    r = rng(25)
    p0 = np.column_stack([r.uniform(BX[0], BX[2], N), r.uniform(BX[1], BX[3], N)])
    th = r.uniform(0, TAU, N)
    E_ = r.exponential(1.0, N)                         # energy at beta = 1 (2D Maxwell-Boltzmann: exponential in energy)
    sp = 0.55 * np.sqrt(E_)
    vel = np.column_stack([sp * np.cos(th), sp * np.sin(th)])

    def positions(t):
        q = p0 + vel * (t - float(s.start))
        return np.column_stack([triangle(q[:, 0], BX[0], BX[2]), triangle(q[:, 1], BX[1], BX[3])])

    s.add(PointsLayer(positions, color=C.energy, size=4.6, glow=0.0, z=0, opacity=fade(T.cut_gas + 0.1, dur=1.2)))
    m = s.manim(z=2)
    m.play(Create(Rectangle(width=BX[2] - BX[0], height=BX[3] - BX[1], stroke_color=C.text, stroke_width=3)), at=T.cut_gas + 0.2, dur=1.2, ease=E)
    h = hud(s)
    board(h, [(tex(r"\max\;", "S", "=-\\sum p\\ln p", size=38, colors={1: C.energy}), T.max_ent), (tex(r"\sum p=1", r",\quad", r"\sum pE=U", size=34), T.max_ent + 1.5)])
    x0, W_, y0, H_ = 2.95, 3.6, -3.2, 2.3
    bins = 9
    w = W_ / bins
    target = np.exp(-(np.arange(bins) + 0.5) * 0.62)
    target = target / target[0]
    settle = key(T.boltz + 0.9, 0.0, 1.0, dur=2.0, ease=E)
    inset(h, (4.75, -1.95), 4.0, 3.3, T.gas - 0.5)

    def bars(t):
        u = float(settle(t))
        vals = (0.42 * (1 - u) + target * u) * H_
        return VGroup(*[Rectangle(width=w * 0.86, height=max(float(v), 0.01), fill_color=C.energy, fill_opacity=1, stroke_width=0).move_to([x0 + w * (i + 0.5), y0 + float(v) / 2, 0]) for i, v in enumerate(vals)])
    live(h, bars, (T.gas + 0.1, T.boltz + 3.0))
    h.play(FadeIn(Line([x0, y0, 0], [x0 + W_, y0, 0], color=C.axis, stroke_width=2.5)), FadeIn(tex("E", size=34, color=C.text).move_to([x0 + W_ - 0.2, y0 + 0.3, 0])), at=T.gas + 0.1, dur=0.4)
    law = tex("p(E)", r"\propto", "e^{-", r"\beta", "E}", size=58, colors={3: C.lam})
    b1 = tex(r"\beta", "=", r"\dfrac{dS}{dU}", size=52, colors={0: C.lam})
    b2 = tex(r"\beta", "=", r"\dfrac{1}{k_B T}", size=52, colors={0: C.lam, 2: C.energy})
    board(h, [(law, T.chance), (b1, T.price_e)], "ur")
    b2.move_to(b1)
    h.play(FadeOut(b1), FadeIn(b2), at=T.temp, dur=0.7, ease=E)
    curtain(s)
