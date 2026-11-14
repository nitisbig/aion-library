"""Shared building blocks for the divergence & curl video: the fields, arrows, dye, paddle wheels, panels, 3D.

The look is Classic: crisp unglowed vector lines on black, Computer Modern for all text. Colors are roles from
theme.py (field, dust, div, sink, curl, cw, xpart, ypart, boundary, efield, bfield).

Every field is an exact numpy function F(x, y) -> (P, Q) on arrays. Divergence and curl come in closed form and are
checked against finite differences in tests below (`python shots.py`).
"""
from aion import *

# ── the cast: linear fields (exact flow maps via the matrix exponential) ──
CAST = {
    "source": np.array([[1.0, 0.0], [0.0, 1.0]]),     # (x, y)        div 2, curl 0
    "whirl": np.array([[0.0, -1.0], [1.0, 0.0]]),     # (-y, x)       div 0, curl 2
    "saddle": np.array([[1.0, 0.0], [0.0, -1.0]]),    # (x, -y)       div 0, curl 0
}
RIVER_C = 2.2                                          # river (y + c, 0): every arrow points right on screen


def linear(A):
    """F(x, y) = A @ (x, y) as an array function."""
    return lambda x, y: (A[0, 0] * x + A[0, 1] * y, A[1, 0] * x + A[1, 1] * y)


def flow_linear(A, pts, t):
    """Exact flow of the linear field A: points (N, 2) carried for time t."""
    from scipy.linalg import expm
    return np.asarray(pts) @ expm(A * t).T


def river(x, y):
    return (y + RIVER_C, 0.0 * x)                     # div 0, curl -1


def drain(x, y, a=0.06):
    r2 = x * x + y * y + a * a
    return (-y / r2, x / r2)                          # div 0, curl 0 away from the centre


def lamp(x, y, a=0.06):
    r2 = x * x + y * y + a * a
    return (x / r2, y / r2)                           # div 0 away from the centre; flux 2 pi through every circle


# ── the hero field: smoothed sources/sinks + vortices + a gentle drift ──
HERO_A = 0.9
HERO_SRC = [((-3.2, 1.0), 1.3), ((3.0, -1.3), -1.3)]          # (centre, strength q): q > 0 source
HERO_VTX = [((2.4, 1.6), 1.5), ((-2.4, -1.7), -1.1)]          # (centre, circulation g): g > 0 counter-clockwise
HERO_DRIFT = (0.1, 0.0)


def hero(x, y):
    P = np.full_like(np.asarray(x, float), HERO_DRIFT[0])
    Q = np.full_like(np.asarray(y, float), HERO_DRIFT[1])
    for (cx, cy), q in HERO_SRC:
        dx, dy = x - cx, y - cy
        d = dx * dx + dy * dy + HERO_A ** 2
        P, Q = P + q * dx / d, Q + q * dy / d
    for (cx, cy), g in HERO_VTX:
        dx, dy = x - cx, y - cy
        d = dx * dx + dy * dy + HERO_A ** 2
        P, Q = P - g * dy / d, Q + g * dx / d
    return P, Q


def hero_div(x, y):
    """Closed form: each smoothed source q(r - c)/(rho^2 + a^2) has divergence 2 q a^2 / (rho^2 + a^2)^2."""
    out = 0.0 * x
    for (cx, cy), q in HERO_SRC:
        d = (x - cx) ** 2 + (y - cy) ** 2 + HERO_A ** 2
        out = out + 2 * q * HERO_A ** 2 / d ** 2
    return out


def hero_curl(x, y):
    """Closed form: each smoothed vortex g(-dy, dx)/(rho^2 + a^2) has curl 2 g a^2 / (rho^2 + a^2)^2."""
    out = 0.0 * x
    for (cx, cy), g in HERO_VTX:
        d = (x - cx) ** 2 + (y - cy) ** 2 + HERO_A ** 2
        out = out + 2 * g * HERO_A ** 2 / d ** 2
    return out


def _eye(c):
    from scipy.optimize import fsolve
    return tuple(float(v) for v in fsolve(lambda p: np.array(hero(np.array(p[0]), np.array(p[1])), float), c))


def hero_eyes():
    """The hero field's true stagnation points near the main source and the ccw vortex (the hook's two places).

    The other features pull them off their nominal centres, so the dye and the rings are placed here.
    """
    return np.array(_eye(HERO_SRC[0][0])), np.array(_eye(HERO_VTX[0][0]))


def sample_grid(fn, center, size, res=(320, 180)):
    """fn evaluated on a (ny, nx) grid covering a world rectangle (row 0 = bottom), for FieldLayer."""
    nx, ny = res
    xs = center[0] + (np.arange(nx) + 0.5) / nx * size[0] - size[0] / 2
    ys = center[1] + (np.arange(ny) + 0.5) / ny * size[1] - size[1] / 2
    X, Y = np.meshgrid(xs, ys)
    return fn(X, Y)


def advect(F, pts, T, steps=120):
    """RK4 flow of pts (N, 2) through F for time T (numpy; for stills and small sets)."""
    p = np.array(pts, float)
    h = T / steps

    def f(q):
        P, Q = F(q[:, 0], q[:, 1])
        return np.stack([np.broadcast_to(P, q[:, 0].shape), np.broadcast_to(Q, q[:, 1].shape)], 1)
    for _ in range(steps):
        k1 = f(p)
        k2 = f(p + h / 2 * k1)
        k3 = f(p + h / 2 * k2)
        k4 = f(p + h * k3)
        p = p + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return p


# ── drawing ──
def words(text, size=None, color=None):
    """Plain words set in LaTeX (Computer Modern), so text and maths share one typeface."""
    return Tex(text, font_size=size or C.tex_size, color=color or C.text)


def tex(*parts, size=None, color=None, colors=None):
    """MathTex in the theme's text color; `colors` maps part index -> color."""
    t = MathTex(*parts, font_size=size or C.tex_size, color=color or C.text)
    for i, col in (colors or {}).items():
        t[i].set_color(col)
    return t


def div_eq(size=None):
    """del . F = dP/dx + dQ/dy, parts colored: del-dot div, P-term xpart, Q-term ypart."""
    return tex(r"\nabla\cdot", r"\mathbf{F}", "=", r"\frac{\partial P}{\partial x}", "+",
               r"\frac{\partial Q}{\partial y}", size=size, colors={0: C.div, 3: C.xpart, 5: C.ypart})


def curl_eq(size=None, nabla=False):
    """curl F = dQ/dx - dP/dy (2D), parts colored: curl, Q-term ypart, P-term xpart. `nabla` writes del-cross F."""
    lhs = r"\nabla\times" if nabla else r"\operatorname{curl}"
    return tex(lhs, r"\mathbf{F}", "=", r"\frac{\partial Q}{\partial x}", "-",
               r"\frac{\partial P}{\partial y}", size=size, colors={0: C.curl, 3: C.ypart, 5: C.xpart})


def maxwell(size=None):
    """Maxwell's four equations as a 2x2 VGroup [[div E, div B], [curl E, curl B]], terms in role colors."""
    E, B = C.efield, C.bfield
    eqs = [
        tex(r"\nabla\cdot", r"\mathbf{E}", "=", r"\frac{\rho}{\varepsilon_0}", size=size, colors={0: C.div, 1: E}),
        tex(r"\nabla\cdot", r"\mathbf{B}", "=", "0", size=size, colors={0: C.div, 1: B}),
        tex(r"\nabla\times", r"\mathbf{E}", "=", "-", r"\frac{\partial \mathbf{B}}{\partial t}", size=size,
            colors={0: C.curl, 1: E, 4: B}),
        tex(r"\nabla\times", r"\mathbf{B}", "=", r"\mu_0", r"\mathbf{J}", "+", r"\mu_0\varepsilon_0",
            r"\frac{\partial \mathbf{E}}{\partial t}", size=size, colors={0: C.curl, 1: B, 7: E}),
    ]
    return VGroup(*eqs)


def ramp(t, a, b):
    """Smoothstep from 0 at t=a to 1 at t=b (for redraw functions)."""
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * (3 - 2 * u)


def ease(t, a, b):
    """Quintic 0 -> 1 between a and b: a calmer start and landing than `ramp`."""
    u = np.clip((t - a) / max(b - a, 1e-6), 0.0, 1.0)
    return u * u * u * (u * (6 * u - 15) + 10)


def live(m, fn, *windows):
    """Rebuild `fn(t)` every frame inside each (start, end) window and hold it still in between."""
    merged = []
    for a, b in sorted(windows):
        if merged and a <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    hs = []
    for a, b in merged:
        if hs:
            m.remove(hs[-1], at=a)
        hs.append(m.redraw(fn, during=(a, b)))
    return hs


def dim(g, k):
    """Scale every stroke and fill opacity in g by k (keeps open shapes open: never fills a hollow ring)."""
    for mob in g.family_members_with_points():
        mob.set_stroke(opacity=mob.get_stroke_opacity() * k)
        mob.set_fill(opacity=mob.get_fill_opacity() * k)
    return g


def rgb(c):
    """sRGB tuple of a theme color, for shader uniforms."""
    return tuple(float(x) for x in ManimColor(c).to_rgb())


def lic(s, opacity, z=-10, gain=2.6, cell=0.045, color=None):
    """The hero field's animated streak texture (shaders/lic.frag) as a full-frame layer."""
    from sims import RATE
    (s0, q0), (s1, q1) = HERO_SRC
    (v0, g0), (v1, g1) = HERO_VTX
    return s.shader("lic.frag", z=z, u_src=(*s0, *s1), u_q=(q0, q1), u_vtx=(*v0, *v1), u_g=(g0, g1),
                    u_drift=HERO_DRIFT, u_a=HERO_A, u_rate=RATE, u_opacity=opacity, u_gain=gain, u_cell=cell,
                    u_color=rgb(color or C.field))


def advect_table(F, pts, t0, t1, rate=60, sub=4, scale=1.0):
    """Positions of pts carried by F (time scaled by `scale`) sampled at `rate` Hz from t0 to t1.

    Returns at(t) -> (N, 2): linear interpolation in the table, clamped. Pure in t, computed once.
    """
    n = max(2, int(np.ceil((t1 - t0) * rate)) + 1)
    out = [np.array(pts, float)]
    h = 1.0 / rate
    for _ in range(n - 1):
        out.append(advect(lambda x, y: tuple(scale * np.asarray(v) for v in F(x, y)), out[-1], h, steps=sub))
    tab = np.stack(out)

    def at(t):
        u = np.clip((t - t0) * rate, 0, n - 1)
        i = int(min(np.floor(u), n - 2))
        f = u - i
        return (1 - f) * tab[i] + f * tab[i + 1]
    return at


def oiint(rest="", size=None, color=None, rest_color=None):
    """The closed-surface integral sign (a double integral with a ring through it) followed by `rest`.

    Built from \\iint plus a drawn ellipse, because the esint font does not survive the SVG conversion.
    Returns VGroup(sign, ring, rest_tex).
    """
    col = color or C.text
    sign = MathTex(r"\iint", font_size=size or C.tex_size, color=col)
    ring = Ellipse(width=sign.width * 0.62, height=sign.height * 0.2, color=col,
                   stroke_width=max(1.5, (size or C.tex_size) / 22)).move_to(sign.get_center() + 0.02 * sign.height * DOWN)
    g = VGroup(sign, ring)
    if rest:
        r = MathTex(rest, font_size=size or C.tex_size, color=rest_color or col).next_to(sign, RIGHT, buff=0.08)
        g.add(r)
    return g


def arrow(a, b, color, width=None, tip=0.2, opacity=1.0):
    """A crisp arrow that keeps a sensible tip at any length."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    a = np.append(a[:2], 0.0)
    b = np.append(b[:2], 0.0)
    L = max(np.linalg.norm(b - a), 1e-6)
    return Arrow(a, b, buff=0, color=color, stroke_width=width or C.stroke, tip_length=min(tip, 0.45 * L),
                 max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=40,
                 stroke_opacity=opacity, fill_opacity=opacity)


def field_arrows(F, box, step=0.5, scale=0.42, color=None, width=2.2, maxlen=None, origin=(0.0, 0.0)):
    """Arrows of F (in field coordinates around `origin`) on a grid inside box (x0, y0, x1, y1) of world space.

    Lengths are squashed (L -> maxlen * tanh(L / maxlen)) so strong spots don't swamp the frame; weak arrows
    fade a little so the eye reads magnitude without a color ramp.
    """
    x0, y0, x1, y1 = box
    maxlen = maxlen or 0.9 * step
    g = VGroup()
    xs = np.arange(x0 + step / 2, x1 - 1e-6, step)
    ys = np.arange(y0 + step / 2, y1 - 1e-6, step)
    for wx in xs:
        for wy in ys:
            P, Q = F(np.array(wx - origin[0]), np.array(wy - origin[1]))
            v = np.array([float(P), float(Q)]) * scale
            L = np.linalg.norm(v)
            if L < 1e-3:
                continue
            Ls = maxlen * np.tanh(L / maxlen)
            v = v / L * Ls
            p = np.array([wx, wy]) - v / 2
            g.add(arrow(p, p + v, color or C.field, width=width, tip=0.12,
                        opacity=0.45 + 0.55 * min(Ls / maxlen, 1.0)))
    return g


def dye(center, radius, color, n=200, opacity=0.35):
    """A circular drop of dye as a filled polygon (n vertices), ready to be carried by a flow."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = np.stack([center[0] + radius * np.cos(th), center[1] + radius * np.sin(th)], 1)
    return dye_poly(pts, color, opacity)


def dye_poly(pts, color, opacity=0.35):
    return Polygon(*[[p[0], p[1], 0] for p in pts], color=color, stroke_width=C.thin,
                   fill_color=color, fill_opacity=opacity)


def poly_area(pts):
    x, y = pts[:, 0], pts[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def paddle(center, angle, radius=0.42, color=None, vanes=4, width=None):
    """A tiny paddle wheel: hub ring + vanes, turned by `angle` (radians, counter-clockwise)."""
    col = color or C.text
    g = VGroup(Circle(radius=radius * 0.22, color=col, stroke_width=width or C.stroke).move_to([*center, 0]))
    for k in range(vanes):
        a = angle + k * 2 * np.pi / vanes
        d = np.array([np.cos(a), np.sin(a)])
        g.add(Line([*(np.asarray(center) + 0.22 * radius * d), 0], [*(np.asarray(center) + radius * d), 0],
                   color=col, stroke_width=(width or C.stroke) + 1))
        tip = np.asarray(center) + radius * d
        g.add(Dot([*tip, 0], radius=0.035, color=col))
    return g


def spin_glyph(center, r, sign, color):
    """A 3/4 circular arrow showing spin direction (sign > 0 counter-clockwise)."""
    a = Arc(radius=r, start_angle=PI / 2, angle=sign * 1.5 * PI, arc_center=[*center, 0], color=color,
            stroke_width=C.thin + 0.5)
    a.add_tip(tip_length=0.14, tip_width=0.14)
    return a


def panel(cx, cy, w, h):
    """A framed panel centred at (cx, cy): black inside, thin light border."""
    return Rectangle(width=w, height=h, stroke_color=C.frame, stroke_width=C.thin,
                     fill_color=C.bg, fill_opacity=1.0).move_to([cx, cy, 0])


def frame_only(cx, cy, w, h):
    return Rectangle(width=w, height=h, stroke_color=C.frame, stroke_width=C.thin).move_to([cx, cy, 0])


# ── orthographic 3D (crisp Manim lines through an az/el projection) ──
def ortho(az, el, scale=1.0, center=(0.0, 0.0)):
    """Return proj(p3) -> world point for an orthographic camera at azimuth az, elevation el (radians)."""
    ca, sa, ce, se = np.cos(az), np.sin(az), np.cos(el), np.sin(el)
    right = np.array([ca, sa, 0.0])
    up = np.array([-se * sa, se * ca, ce])

    def proj(p):
        p = np.asarray(p, float)
        return np.array([center[0] + scale * p @ right, center[1] + scale * p @ up, 0.0])
    proj.depth = lambda p: np.asarray(p, float) @ np.array([ce * sa, -ce * ca, se])   # toward the viewer
    return proj


def cube_edges(proj, color, width=None, s=1.0):
    """The 12 edges of the cube [-s, s]^3 projected; hidden edges dashed."""
    V = np.array([[x, y, z] for x in (-s, s) for y in (-s, s) for z in (-s, s)])
    g = VGroup()
    c_depth = proj.depth(np.zeros(3))
    for i in range(8):
        for j in range(i + 1, 8):
            if np.sum(np.abs(V[i] - V[j]) > 1e-9) == 1:
                ln = Line(proj(V[i]), proj(V[j]), color=color, stroke_width=width or C.thin)
                mid = (V[i] + V[j]) / 2
                g.add(DashedLine(proj(V[i]), proj(V[j]), color=color, stroke_width=(width or C.thin) * 0.7,
                                 dash_length=0.06) if proj.depth(mid) < c_depth - 0.3 else ln)
    return g


if __name__ == "__main__":
    # finite-difference check of the closed forms
    h = 1e-4
    X, Y = np.meshgrid(np.linspace(-6, 6, 37), np.linspace(-3.5, 3.5, 23))
    Pxp, _ = hero(X + h, Y)
    Pxm, _ = hero(X - h, Y)
    _, Qyp = hero(X, Y + h)
    _, Qym = hero(X, Y - h)
    _, Qxp = hero(X + h, Y)
    _, Qxm = hero(X - h, Y)
    Pyp, _ = hero(X, Y + h)
    Pym, _ = hero(X, Y - h)
    div_fd = (Pxp - Pxm) / (2 * h) + (Qyp - Qym) / (2 * h)
    curl_fd = (Qxp - Qxm) / (2 * h) - (Pyp - Pym) / (2 * h)
    print("div err", np.abs(div_fd - hero_div(X, Y)).max(), "curl err", np.abs(curl_fd - hero_curl(X, Y)).max())
    print("div range", hero_div(X, Y).min(), hero_div(X, Y).max(), "curl range", hero_curl(X, Y).min(),
          hero_curl(X, Y).max())


# ── the stage: a dim grid, the cast rail ──
RAIL = [(-6.05, 2.55), (-6.05, 1.2), (-6.05, -0.15)]   # docked cast panels: source, whirl, saddle (centres)
RAIL_S = 1.15                                          # docked panel size (world units)
CAST_NAMES = ("source", "whirl", "saddle")


def grid_plane(box=(-7.6, -4.4, 7.6, 4.4), step=1.0, opacity=1.0):
    """The field scenes' stage: integer lines in C.grid_minor, the two axes in C.ghost (dim, so arrows read)."""
    x0, y0, x1, y1 = box
    g = VGroup()
    for x in np.arange(np.ceil(x0 / step) * step, x1 + 1e-6, step):
        g.add(Line([x, y0, 0], [x, y1, 0], color=C.ghost if abs(x) < 1e-6 else C.grid_minor,
                   stroke_width=C.thin * (1.3 if abs(x) < 1e-6 else 0.8), stroke_opacity=opacity))
    for y in np.arange(np.ceil(y0 / step) * step, y1 + 1e-6, step):
        g.add(Line([x0, y, 0], [x1, y, 0], color=C.ghost if abs(y) < 1e-6 else C.grid_minor,
                   stroke_width=C.thin * (1.3 if abs(y) < 1e-6 else 0.8), stroke_opacity=opacity))
    return g


def cast_points(name, n=260, seed=0, rate=0.5, half=2.2, period=None):
    """Grains in one cast field, exact (matrix exponential), recycled forever: local(t) -> (pos (n,2), alpha (n,)).

    Positions are in FIELD units (panel half-size `half`). Each grain has its own phase; its age is
    (rate * t + phase) mod period, so the picture is pure in t with a steady density. Grains fade in and out and are
    hidden (alpha 0) outside the panel. The source respawns near its centre, the others anywhere in the panel.
    """
    from scipy.linalg import expm
    A = CAST[name]
    rng = np.random.default_rng(seed + 17 * CAST_NAMES.index(name))
    Tp = period or {"source": 2.3, "whirl": 7.0, "saddle": 3.0}[name]
    if name == "source":
        r = 0.6 * np.sqrt(rng.uniform(0.0, 1.0, n))
        a = rng.uniform(0, 2 * np.pi, n)
        p0 = np.stack([r * np.cos(a), r * np.sin(a)], 1)
    elif name == "whirl":
        r = half * np.sqrt(rng.uniform(0.0, 1.0, n))
        a = rng.uniform(0, 2 * np.pi, n)
        p0 = np.stack([r * np.cos(a), r * np.sin(a)], 1)
    else:                                   # saddle: enter from the top and bottom edges, leave left and right
        p0 = np.stack([rng.uniform(-0.9, 0.9, n) * np.exp(-1.2), np.where(rng.random(n) < 0.5, -1.0, 1.0) * half], 1)
        p0[:, 0] *= rng.uniform(0.05, 1.0, n)
    phase = rng.uniform(0, Tp, n)
    lam, vec = np.linalg.eig(A)

    def local(t):
        age = np.mod(rate * t + phase, Tp)
        # exact flow, grain by grain: exp(A age) p0 (A is 2x2; batch via eigen-decomposition when real, else expm)
        if np.all(np.isreal(lam)):
            V, Vi = vec.real, np.linalg.inv(vec.real)
            q = (p0 @ Vi.T) * np.exp(np.outer(age, lam.real))
            pos = q @ V.T
        else:                               # rotation: exp(A s) is a rotation by s (whirl = (-y, x))
            c, s_ = np.cos(age), np.sin(age)
            pos = np.stack([c * p0[:, 0] - s_ * p0[:, 1], s_ * p0[:, 0] + c * p0[:, 1]], 1)
        fade = np.minimum(1.0, np.minimum(age / 0.35, (Tp - age) / 0.35))
        inside = (np.abs(pos[:, 0]) < half * 0.97) & (np.abs(pos[:, 1]) < half * 0.97)
        return pos, np.where(inside, np.clip(fade, 0, 1), 0.0).astype(np.float32)
    return local


def cast_layer(local, center, scale, opacity=1.0, z=3, size=2.6):
    """PointsLayer for cast_points: world = center(t) + scale(t) * local. center/scale may be callables of t."""
    cf = center if callable(center) else (lambda t, c=center: c)
    sf = scale if callable(scale) else (lambda t, k=scale: k)

    def pos(t):
        p, a = local(t)
        w = np.asarray(cf(t), float)[:2] + float(sf(t)) * p
        return np.where(a[:, None] > 0, w, 99.0).astype(np.float32)
    return PointsLayer(pos, values=lambda t: local(t)[1], cmap="ramp", colors=(C.bg, C.dust, C.dust), size=size,
                       glow=0.0, z=z, opacity=opacity)


PANEL_W = 4.1                                  # full-size cast panel (world units); field half-size 2.2 units
PANEL_X = (-4.65, 0.0, 4.65)
PANEL_Y = 0.15


def cast_arrows(name, c, w, step=0.58, scale=0.2, width=1.8):
    """The cast field `name` as arrows filling a w x w panel centred at c (field half-size 2.2 units)."""
    A = CAST[name]
    k = 2.2 / (w / 2)                          # field units per world unit
    box = (c[0] - w / 2, c[1] - w / 2, c[0] + w / 2, c[1] + w / 2)
    F = lambda x, y: (A[0, 0] * k * x + A[0, 1] * k * y, A[1, 0] * k * x + A[1, 1] * k * y)
    return field_arrows(F, box, step=step * w / PANEL_W, scale=scale * w / PANEL_W * PANEL_W / 4.1, width=width,
                        origin=c, maxlen=0.85 * step * w / PANEL_W)


def cast_panel(name, c, w, **kw):
    """Framed cast panel: VGroup(frame, arrows)."""
    return VGroup(frame_only(c[0], c[1], w, w), cast_arrows(name, c, w, **kw))


def rail(m, at, names=CAST_NAMES):
    """The docked cast rail (left edge), static from `at`: black-backed mini panels with arrows. Returns the VGroup."""
    g = VGroup()
    for nm in names:
        c = RAIL[CAST_NAMES.index(nm)]
        g.add(VGroup(panel(c[0], c[1], RAIL_S, RAIL_S), cast_arrows(nm, c, RAIL_S, width=1.2)))
    m.add(g, at=at)
    return g


def rail_dust(s, at, opacity=1.0, names=CAST_NAMES):
    """The rail's grains, identical to s03's docked panels (exact cast flows, recycled; pure in t)."""
    for nm in names:
        i = CAST_NAMES.index(nm)
        k = opacity if callable(opacity) else (lambda t, o=opacity: o)
        s.add(cast_layer(cast_points(nm), RAIL[i], RAIL_S / 4.4, z=5,
                         opacity=lambda t, k=k: (0.55 if t >= at else 0.0) * k(t)))


def stage(s, m, at, badges=(), tile=False):
    """Everything that persists: the rail, its grains, the earned badges (list of mob_fns), and the lamp tile."""
    r = rail(m, at)
    rail_dust(s, at)
    bs = VGroup(*[badge(i, f) for i, f in enumerate(badges)])
    m.add(bs, at=at)
    if tile:
        m.add(lamp_tile(), at=at)
    return r, bs


BADGES = [lambda: tex(r"\mathbf{F}", size=40, color=C.field),
          lambda: tex(r"\nabla\cdot", r"\mathbf{F}", size=40, colors={0: C.div}),
          lambda: tex(r"\nabla\times", r"\mathbf{F}", size=40, colors={0: C.curl})]


def badge(i, mob_fn):
    """A small framed badge under the rail, slot i (0 = 'F', 1 = div, 2 = curl, ...). mob_fn() builds its content."""
    c = (RAIL[0][0], RAIL[2][1] - 1.25 - 0.85 * i)
    content = mob_fn()
    content.scale_to_fit_height(min(0.42, content.height)).move_to([*c, 0])
    if content.width > RAIL_S - 0.2:
        content.scale_to_fit_width(RAIL_S - 0.2)
    return VGroup(Rectangle(width=RAIL_S, height=0.7, stroke_color=C.frame, stroke_width=C.thin * 0.8,
                            fill_color=C.bg, fill_opacity=1.0).move_to([*c, 0]), content)


# ── the lamp tile (s06 parks it top right; it stays until Ch4 pays it off) ──
LAMP_C = np.array([0.9, -0.2])                 # where the lamp sat in s06
TILE_C = np.array([6.15, 3.2])
TILE_K = 0.11


def lamp_arrows():
    """The s06 lamp arrows at full size (around LAMP_C)."""
    return field_arrows(lamp, (-4.9, -4.2, 6.9, 3.9), step=0.6, scale=0.6, width=2.0, origin=tuple(LAMP_C))


def lamp_tile():
    """The parked lamp tile, identical to s06's last frame: shrunken arrows + dot + frame."""
    g = VGroup(lamp_arrows(), Dot([*LAMP_C, 0], radius=0.08, color=C.dust))
    g.scale(TILE_K, about_point=[*LAMP_C, 0]).shift([*(TILE_C - LAMP_C), 0])
    return VGroup(g, Rectangle(width=1.35, height=1.0, stroke_color=C.frame, stroke_width=C.thin * 0.8)
                  .move_to([*TILE_C, 0]))


def panel_arrows(F, c, w, step=0.58, scale=0.2, width=1.8):
    """Any field F (in FIELD units, panel half-size 2.2) as arrows filling a w x w panel centred at c."""
    k = 2.2 / (w / 2)
    box = (c[0] - w / 2, c[1] - w / 2, c[0] + w / 2, c[1] + w / 2)
    G = lambda x, y: F(k * x, k * y)
    return field_arrows(G, box, step=step * w / PANEL_W, scale=scale * w / PANEL_W, width=width, origin=c,
                        maxlen=0.85 * step * w / PANEL_W)


# ── Ch4: one region, cut into small squares (shared by s10 and s11) ──
REG_C = np.array([-0.1, -0.2])                 # region centre (world)
REG_H = 0.6                                    # square size


def region():
    """Cells of a wobbly blob on a grid of size REG_H. Returns dict with
    cells: list of (cx, cy); inner: list of (a, b, ia, ib) shared edges (endpoints, the two cells);
    outer: list of (a, b, n, i) boundary edges (endpoints, outward unit normal, cell index)."""
    h = REG_H
    rng = np.random.default_rng(21)
    wob = [(rng.uniform(-0.07, 0.07), rng.uniform(0, 6.3), k) for k in (2, 3, 5)]
    inside = lambda x, y: (((x - REG_C[0]) / 3.2) ** 2 + ((y - REG_C[1]) / 2.15) ** 2) ** 0.5 < 1 + sum(
        a * np.cos(k * np.arctan2(y - REG_C[1], x - REG_C[0]) + p) for a, p, k in wob)
    idx = {}
    cells = []
    for i in range(-7, 8):
        for j in range(-5, 6):
            cx, cy = REG_C[0] + (i + 0.5) * h, REG_C[1] + (j + 0.5) * h
            if inside(cx, cy):
                idx[(i, j)] = len(cells)
                cells.append((cx, cy))
    inner, outer = [], []
    for (i, j), k in idx.items():
        cx, cy = cells[k]
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = np.array([di, dj], float)
            mid = np.array([cx, cy]) + n * h / 2
            t = np.array([-dj, di], float)
            a, b = mid - t * h / 2, mid + t * h / 2
            nb = idx.get((i + di, j + dj))
            if nb is None:
                outer.append((a, b, n, k))
            elif (di, dj) in ((1, 0), (0, 1)):
                inner.append((a, b, k, nb))
    return dict(cells=cells, inner=inner, outer=outer, idx=idx)


def boundary_loop(reg):
    """The outer boundary as one counter-clockwise closed polyline (list of points)."""
    segs = {}
    for a, b, n, _ in reg["outer"]:
        # orient each edge counter-clockwise: interior on the left, i.e. direction = rot90(n) ... (n x z)
        d = np.array([-n[1], n[0]])
        p, q = (a, b) if np.dot(b - a, d) > 0 else (b, a)
        segs[tuple(np.round(p, 6))] = np.array(q)
    start = next(iter(segs))
    loop, cur = [np.array(start)], start
    for _ in range(len(segs)):
        nxt = segs[cur]
        loop.append(nxt)
        cur = tuple(np.round(nxt, 6))
        if cur == start:
            break
    return loop
