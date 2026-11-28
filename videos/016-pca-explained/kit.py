"""Shared drawing kit for video 016: type helpers, boards and the rail, raster canvases, and the shadow room.

Scenes import it with `from kit import *` (the video folder is on the path, as for `beats` and `theme`). Geometry
follows design/design_sheet.md: safe box x -6.40..6.40, y -3.29..3.29; L2 stage + rail; L3 split; L4 grid.
Every function here is a pure function of its arguments; nothing keeps state between frames.

Example:
    from kit import *
    m = s.manim(z=1)
    m.add(board(LEFT_L3, "pixels"))
"""
from __future__ import annotations

import math

import numpy as np
from aion import *  # noqa: F401,F403  (Manim names, C, tracks, layers)
from aion import C
from aion.components.linalg import Mat, brackets  # noqa: F401
from aion.components.linalg import grid_lines as _grid_lines
from aion.components.linalg import panel as _panel  # noqa: F401
from manim import (DL, DOWN, LEFT, ORIGIN, RIGHT, UL, UP, UR, Circle, Dot, Line, MathTex, Rectangle,  # noqa: F401
                   Square, Tex, VGroup)

import pcadata as pd  # noqa: F401

PX = 135.0                          # px per world unit at 1080p
XW, YH = 64 / 9, 4.0                # half frame (world units)
SAFE = 0.71                         # text-safe inset (96 px)
X0, X1, Y0, Y1 = -XW + SAFE, XW - SAFE, -YH + SAFE, YH - SAFE   # the safe box: -6.40..6.40, -3.29..3.29
GAP = 0.25
STAGE_L2 = (X0, Y0, 2.30, Y1)       # L2 main stage
RAIL = (2.55, Y0, X1, Y1)           # L2 rail: three slots
SLOT_GAP = 0.2
LEFT_L3, RIGHT_L3 = (X0, -3.0, -GAP / 2, 3.0), (GAP / 2, -3.0, X1, 3.0)
DIM = 0.35


# ------------------------------------------------------------------------------------------------ type
def tex(s: str, size: float = 48, color=None) -> MathTex:
    """Maths in CM roman."""
    return MathTex(s, font_size=size, color=color or C.text)


def sans(s: str, size: float = 30, color=None) -> Tex:
    """Labels and key words in CM sans."""
    return Tex(r"\textsf{" + s + "}", font_size=size, color=color or C.text)


def caps(s: str, size: float = 34, color=None) -> Tex:
    """Names, dates and chapter cards in CM small caps."""
    return Tex(r"\textsc{" + s + "}", font_size=size, color=color or C.text)


def P3(x, y) -> np.ndarray:
    return np.array([float(x), float(y), 0.0])


def rgb255(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(lin):
    lin = np.clip(lin, 0.0, 1.0)
    return np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)


def lin(h: str) -> tuple[float, float, float]:
    """A theme hex as a linear-light RGB triple (for shader uniforms)."""
    return tuple(float(v) for v in to_lin(np.array(rgb255(h)) / 255.0))


def tint(color: str, a: float) -> str:
    """`color` at opacity `a` over black, mixed in linear light, as one solid hex (fills that must hide what's under)."""
    s = to_srgb(to_lin(np.array(rgb255(color)) / 255.0) * a)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in s)


def backed(mob, pad: float = 0.06, fill=None):
    """A label with a black backing (or `fill`, e.g. C.card on cards) so lines never cut through its glyphs."""
    bg = Rectangle(width=mob.width + 2 * pad, height=mob.height + 2 * pad, stroke_width=0, stroke_color=fill or C.card, fill_color=fill or C.card,
                   fill_opacity=1.0).move_to(mob.get_center())
    return VGroup(bg, mob)


def dim(mob, k: float = DIM):
    """Scale every stroke and fill opacity in `mob` by k (keeps each part's own opacity)."""
    for sm in mob.family_members_with_points():
        sm.set_stroke(opacity=sm.get_stroke_opacity() * k, family=False)
        sm.set_fill(opacity=sm.get_fill_opacity() * k, family=False)
    return mob


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def window(fn, a: float, b: float):
    """A redraw function that draws `fn(t)` only for a <= t < b (empty outside), for `m.redraw(..., during=(a, b+))`.
    A redraw keeps its last mobject after its window, so it must end on an empty frame."""
    def f(t):
        return fn(t) if a <= t < b else VGroup()
    return f


def glow_layer(s, z: float, color=None, k: float = 1.0, radius=None, **kw):
    """A Manim layer whose shapes carry the accent glow (C.glow) in `color`: lit (payoff) elements only."""
    return s.manim(z=z, fx=[Glow(color, strength=C.glow * k, radius=radius or C.glow_r)], **kw)


def glow_fx(color=None, k: float = 1.0, radius=None):
    """The accent glow as an fx list for raster layers."""
    return [Glow(color, strength=C.glow * k, radius=radius or C.glow_r)]


# ------------------------------------------------------------------------------------------------ boards
def box_c(box) -> np.ndarray:
    return P3((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def board(box, tag=None, size: float = 24):
    """A borderless board (a rounded C.card card, no frame line) with an optional key-word tag top-left."""
    g = VGroup(panel(*box))
    if tag:
        g.add(sans(tag, size, C.muted).move_to(P3(box[0] + 0.16, box[3] - 0.16), aligned_edge=UL))
    return g


def panel(x0, y0, x1, y1, fill=True, r: float = 0.16):
    """The premium panel: a rounded card of lifted black (C.card) with no frame line (replaces the Classic
    framed panel everywhere in 016).

    Example:
        m.add(panel(-6.4, -3.0, -0.1, 3.0))
    """
    return RoundedRectangle(corner_radius=r, width=x1 - x0, height=y1 - y0, stroke_width=0, fill_color=C.card,
                            fill_opacity=1.0 if fill else 0.0).move_to(P3((x0 + x1) / 2, (y0 + y1) / 2))


def grid_lines(M, center, unit, box, n=14, minor=2, color=None, width=None, opacity=1.0, axes=True):
    """The premium plane after the matrix M (see plane_grid); with `color`, the single-colour reference grid of
    aion's grid_lines. Same structure: VGroup(minor, major, axes)."""
    if color is not None:
        return _grid_lines(M, center, unit, box, n=n, minor=minor, color=color, width=width, opacity=opacity, axes=axes)
    return plane_grid(center, unit, box, n=n, minor=minor, opacity=opacity, M=M, axes=axes)


def slot(i: int):
    """Rail slot i (0 top … 2 bottom) of the L2 rail."""
    x0, y0, x1, y1 = RAIL
    h = (y1 - y0 - 2 * SLOT_GAP) / 3
    top = y1 - i * (h + SLOT_GAP)
    return (x0, top - h, x1, top)


def grid4(i: int, box=(X0, Y0, X1, Y1), gap: float = GAP):
    """Board i (0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right) of the L4 2x2 grid."""
    x0, y0, x1, y1 = box
    w, h = (x1 - x0 - gap) / 2, (y1 - y0 - gap) / 2
    c, r = i % 2, i // 2
    bx0, by1 = x0 + c * (w + gap), y1 - r * (h + gap)
    return (bx0, by1 - h, bx0 + w, by1)


def fit_into(content, box, pad: float = 0.2, top: float = 0.35, cap: float = 1.0):
    """Scale `content` (never above `cap`) to fit `box` under its tag line, and centre it there."""
    w, h = box[2] - box[0] - 2 * pad, box[3] - box[1] - pad - top
    content.scale(min(w / content.width, h / content.height, cap))
    content.move_to(P3((box[0] + box[2]) / 2, (box[1] + pad + box[3] - top) / 2))
    return content


def rail_board(i: int, content, tag: str):
    """A finished result pinned in rail slot i: its board, its tag, its content scaled to fit under the tag."""
    box = slot(i)
    return VGroup(board(box, tag), fit_into(content, box, pad=0.2, top=0.4))


def dots(pts, color, r: float = 0.055, opacity: float = 1.0):
    """Data points as beads (premium look)."""
    return VGroup(*[bead(p, r=r * 1.1, color=color, a=opacity) for p in pts])


# ------------------------------------------------------------------------------------------------ rasters
class Canvas:
    """A skia surface covering a world box at `px` px/unit; `layer_kw()` places the array in the world.

    Example:
        cv = Canvas((-3, -2, 3, 2), px=s.comp.size[1] / 8)
        def draw(t):
            c = cv.begin(); c.drawCircle(*cv.T(0, 0), 40, cv.fill(C.data)); return cv.array()
        s.add(FramesLayer(draw, z=0, **cv.layer_kw()))
    """

    def __init__(self, box, px: float = PX):
        import skia
        self.skia, self.box, self.px = skia, box, px
        x0, y0, x1, y1 = box
        self.w, self.h = int(round((x1 - x0) * px)), int(round((y1 - y0) * px))
        self.surf = skia.Surface(self.w, self.h)

    def T(self, x, y):
        return (x - self.box[0]) * self.px, (self.box[3] - y) * self.px

    def begin(self):
        c = self.surf.getCanvas()
        c.clear(self.skia.ColorTRANSPARENT)
        return c

    def array(self) -> np.ndarray:
        sk = self.skia
        return self.surf.makeImageSnapshot().toarray(colorType=sk.kRGBA_8888_ColorType, alphaType=sk.kPremul_AlphaType)

    def layer_kw(self) -> dict:
        x0, y0, x1, y1 = self.box
        return dict(height=y1 - y0, pos=((x0 + x1) / 2, (y0 + y1) / 2), premultiplied=True)

    def color(self, color: str, alpha: float = 1.0):
        r, g, b = rgb255(color)
        return self.skia.Color(r, g, b, int(round(255 * min(max(alpha, 0.0), 1.0))))

    def stroke(self, color: str, alpha: float = 1.0, width: float = 3.0):
        sk = self.skia
        return sk.Paint(AntiAlias=True, Style=sk.Paint.kStroke_Style, StrokeWidth=width,
                        StrokeCap=sk.Paint.kRound_Cap, Color=self.color(color, alpha))

    def fill(self, color: str, alpha: float = 1.0, aa: bool = True):
        sk = self.skia
        return sk.Paint(AntiAlias=aa, Style=sk.Paint.kFill_Style, Color=self.color(color, alpha))


def grey_tiles(vals, size: float, vmax: float = 16.0, frame: bool = True):
    """An 8x8 array of grey levels (0..vmax) as crisp Manim squares, centred at the origin. Returns (cells, frame)."""
    a = np.asarray(vals, float).reshape(8, 8)
    cell = size / 8
    g = VGroup()
    for r in range(8):
        for c in range(8):
            v = int(round(255 * min(max(a[r, c] / vmax, 0.0), 1.0)))
            g.add(Square(side_length=cell, stroke_width=0, fill_color=f"#{v:02X}{v:02X}{v:02X}", fill_opacity=1.0)
                  .move_to(P3((c - 3.5) * cell, (3.5 - r) * cell)))
    fr = Square(side_length=size, stroke_color=C.plane, stroke_width=1.2, fill_opacity=0)
    return g, fr


# ------------------------------------------------------------------------------------------- shadow room
class ShadowRoom:
    """The video's bookend: a glass-and-gold sculpture under a warm spot lamp, its shadow on a wall (skia, per frame).

    The object (pcadata.beads): three bunches of glass beads (C.glass1..3) threaded by a spiral gold wire (C.pc1).
    The room: a plaster wall (y = WALL_Y) meeting a floor (z = FLOOR_Z), lit by a point lamp off frame left (inverse
    square, incidence, a soft-edged spot). A pinhole camera at (0, -CAM_D, 0) looks along +y.

    Shadows are cast by geometry: each bead's shadow is the ray from the lamp through its centre met with the wall
    (s = (WALL_Y - Ly) / (Py - Ly)), a disc of radius r·s; the wire's shadow is its projected polyline. They are
    unioned (light blocked never doubles) and softened by a penumbra that grows with distance to the wall. Glass
    passes coloured light: each bead's shadow carries a tinted caustic at its centre, so the shadow shows colour.
    Beads (glass: fresnel rim, transmitted glow, two speculars) and wire segments (a shaded tube) are drawn far to
    near together.

    `frame(R, lamp, sharp)`: R rotates the object in its principal frame (identity = the best view: PC1, PC2 across
    the light, PC3 along it); lamp 0..1; sharp 0..1 tightens the penumbra.

    Example:
        room = ShadowRoom(px=s.comp.size[1] / 8)
        s.add(FramesLayer(lambda t: room.frame(orient(t), lamp=on(t)), z=-10, **room.layer_kw()))
    """

    CAM_D, FOCAL, WALL_Y, FLOOR_Z = 10.0, 15.0, 3.4, -2.25
    SHIFT = np.array([2.3, 0.35])   # film shift (screen world units): frames the object left, its shadow right
    LAMP = np.array([-5.0, -7.0, 1.0])
    CENTRE = np.array([-2.4, -1.2, 0.25])
    SCALE = 0.27                    # world units per sculpture unit
    CONE = math.radians(23)         # half-angle of the lamp's spot
    AMBIENT = 0.07
    WIRE_R = 0.05                   # wire radius, sculpture units

    def __init__(self, px: float = PX, box=(-XW, -YH, XW, YH)):
        self.cv = Canvas(box, px)
        self.px = px
        B, lab, Wp, r = pd.beads()
        self.Q = pd.pca(np.vstack([B, Wp[::2]]))
        V, mu = self.Q.V, self.Q.mu
        self.Ab = (B - mu) @ V * self.SCALE                               # bead centres, principal coordinates
        self.Aw = (Wp - mu) @ V * self.SCALE                              # wire points
        self.cluster = lab
        self.R_SPH = r * self.SCALE
        self.R_WIRE = self.WIRE_R * self.SCALE
        d = self.CENTRE - self.LAMP
        self.d = d / np.linalg.norm(d)                                    # light direction through the centre
        e1 = np.array([self.d[1], -self.d[0], 0.0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(e1, self.d)
        self.E = np.stack([e1, e2, self.d])                               # rows: PC1, PC2, PC3 directions in the world
        self.cols = [C.glass1, C.glass2, C.glass3]
        self._wall = None
        self._sprites = None

    # ------------------------------------------------------------------ geometry
    def world(self, R: np.ndarray, A=None) -> np.ndarray:
        """Bead centres (or the points A, principal coordinates) in the world for rotation R."""
        return self.CENTRE + ((self.Ab if A is None else A) @ R.T) @ self.E

    def wire(self, R: np.ndarray) -> np.ndarray:
        return self.world(R, self.Aw)

    def proj(self, P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """World points → screen (world units) and the projection scale at each depth."""
        k = self.FOCAL / (P[..., 1] + self.CAM_D)
        return np.stack([P[..., 0] * k, P[..., 2] * k], -1) + self.SHIFT, k

    def on_wall(self, P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Shadow centres on the wall (world) and each one's magnification s."""
        L = self.LAMP
        s = (self.WALL_Y - L[1]) / (P[..., 1] - L[1])
        return L + s[..., None] * (P - L), s

    def shadow_xy(self, R: np.ndarray) -> np.ndarray:
        """Where each bead's shadow lands on screen (world units)."""
        return self.proj(self.on_wall(self.world(R))[0])[0]

    def wire_shadow_xy(self, R: np.ndarray) -> np.ndarray:
        return self.proj(self.on_wall(self.wire(R))[0])[0]

    def lamp_screen(self) -> np.ndarray:
        """The lamp's projection (off frame, left) and where the cone's axis meets the wall, on screen."""
        Wc, _ = self.on_wall(self.CENTRE)
        return self.proj(self.LAMP)[0], self.proj(Wc)[0]

    # ------------------------------------------------------------------ static rasters
    def _spot(self, P):
        v = P - self.LAMP
        dist = np.linalg.norm(v, axis=-1)
        cosang = (v @ self.d) / dist
        ang = np.arccos(np.clip(cosang, -1, 1))
        spot = (1 - smoothstep((ang - self.CONE * 0.5) / (self.CONE * 0.5))) * np.clip(cosang, 0, 1) ** 6
        return spot, v, dist

    def wall(self):
        """The lit room (wall and floor, plaster grain, corner occlusion) as an opaque skia image."""
        if self._wall is not None:
            return self._wall
        cv = self.cv
        x0, y0, x1, y1 = cv.box
        xs = x0 + (np.arange(cv.w) + 0.5) / cv.px - self.SHIFT[0]
        ys = y1 - (np.arange(cv.h) + 0.5) / cv.px - self.SHIFT[1]
        SX, SY = np.meshgrid(xs, ys)
        kw = (self.WALL_Y + self.CAM_D) / self.FOCAL
        on_wall = SY * kw >= self.FLOOR_Z
        depth = np.where(on_wall, self.WALL_Y + self.CAM_D, self.FOCAL * self.FLOOR_Z / np.minimum(SY, -1e-6))
        P = np.stack([SX * depth / self.FOCAL, depth - self.CAM_D, np.where(on_wall, SY * kw, self.FLOOR_Z)], -1)
        spot, v, dist = self._spot(P)
        inc = np.where(on_wall, v[..., 1], -v[..., 2]) / dist
        I = spot * np.clip(inc, 0, 1) / dist ** 2
        I = I / I.max() * 0.85
        corner = np.where(on_wall, P[..., 2] - self.FLOOR_Z, self.WALL_Y - P[..., 1])   # distance to the corner
        I = np.where(on_wall, I, I * 2.4)                              # the floor catches the spot at a graze
        I = I * (0.55 + 0.45 * smoothstep(corner / 0.9)) + 0.010
        rng = np.random.default_rng(1612)                             # plaster grain: smooth low-contrast noise
        g = rng.normal(0, 1, (cv.h // 6 + 2, cv.w // 6 + 2))
        from scipy.ndimage import gaussian_filter, zoom
        g = gaussian_filter(g, 1.2)
        g = zoom(g, (cv.h / g.shape[0], cv.w / g.shape[1]), order=1)[:cv.h, :cv.w]
        I = I * (1 + 0.035 * g / g.std())
        wall_c = to_lin(np.array(rgb255(C.wall)) / 255.0)
        floor_c = to_lin(np.array(rgb255(C.floor)) / 255.0)
        lamp_c = to_lin(np.array(rgb255(C.lamp)) / 255.0)
        col = np.where(on_wall[..., None], wall_c, floor_c) * lamp_c
        rgb = to_srgb(I[..., None] * col)
        arr = (np.dstack([rgb, np.ones(rgb.shape[:2])]) * 255 + 0.5).astype(np.uint8)
        sk = cv.skia
        self._wall = sk.Image.fromarray(arr, colorType=sk.kRGBA_8888_ColorType, alphaType=sk.kPremul_AlphaType)
        self.floor_y = (self.FLOOR_Z / kw) + self.SHIFT[1]               # the corner line on screen
        return self._wall

    def sprites(self, levels: int = 14, size: int = 96):
        """Glass bead sprites per bunch colour at `levels` brightness steps (skia images), lit from the lamp's side."""
        if self._sprites is not None:
            return self._sprites
        import skia
        yy, xx = (np.mgrid[0:size, 0:size] + 0.5) / size * 2 - 1
        yy = -yy
        r2 = xx ** 2 + yy ** 2
        nz = np.sqrt(np.clip(1 - r2, 0, 1))
        Lc = -self.d
        l = np.array([Lc[0], Lc[2], -Lc[1]])
        l /= np.linalg.norm(l)
        ndl = xx * l[0] + yy * l[1] + nz * l[2]
        h = l + np.array([0, 0, 1.0])
        h /= np.linalg.norm(h)
        ndh = np.clip(xx * h[0] + yy * h[1] + nz * h[2], 0, 1)
        fres = (1 - nz) ** 3
        through = smoothstep((-ndl + 0.15) / 0.9) * nz ** 0.5                # light leaving the far side
        a = np.clip((1 - np.sqrt(r2)) * size / 2, 0, 1)
        lampc = to_lin(np.array(rgb255(C.lamp)) / 255.0)
        out = []
        for col in self.cols:
            base = to_lin(np.array(rgb255(col)) / 255.0)
            bank = []
            for j in range(levels):
                b = j / (levels - 1)
                rgb = (base * (self.AMBIENT + 0.65 * b * np.clip(ndl, 0, 1)[..., None] + 1.7 * b * through[..., None]
                               + (0.15 + 0.8 * b) * fres[..., None])
                       + lampc * b * (2.2 * ndh[..., None] ** 90 + 0.25 * ndh[..., None] ** 14)
                       + 0.10 * (1 - nz)[..., None] ** 6)
                img = np.dstack([to_srgb(rgb) * a[..., None], a])
                arr = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
                bank.append(skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType,
                                                 alphaType=skia.kPremul_AlphaType))
            out.append(bank)
        self._sprites = out
        return out

    # ------------------------------------------------------------------ the frame
    def _bright(self, P, lamp):
        spot, v, dist = self._spot(P)
        return lamp * spot * (7.4 / dist) ** 2

    def frame(self, R: np.ndarray, lamp: float = 1.0, sharp: float = 0.0, overlay=None) -> np.ndarray:
        sk, cv = self.cv.skia, self.cv
        lamp = float(min(max(lamp, 0.0), 1.2))
        P, Wp = self.world(R), self.wire(R)
        S, s_mag = self.on_wall(P)
        sxy, sk_ = self.proj(S)
        Sw, sw_mag = self.on_wall(Wp)
        wxy, wk = self.proj(Sw)
        c = cv.begin()
        c.drawImage(self.wall(), 0, 0, sk.SamplingOptions(), sk.Paint(Alphaf=float(min(lamp, 1.0))))
        if lamp > 1e-3:
            # penumbra: grows with each caster's distance to the wall (a lamp of finite size)
            gap = float(np.mean(self.WALL_Y - P[:, 1]))
            sigma = (0.004 + 0.0045 * gap) * (1.0 - 0.55 * sharp) * cv.px
            c.saveLayer(None, sk.Paint(Alphaf=0.86 * min(lamp, 1.0), ImageFilter=sk.ImageFilters.Blur(sigma, sigma)))
            p = sk.Paint(AntiAlias=True, Color=sk.ColorBLACK)
            for (x, y), r in zip(sxy, s_mag * sk_ * self.R_SPH):
                X, Y = cv.T(x, y)
                c.drawCircle(X, Y, r * cv.px, p)
            path = sk.Path()
            path.moveTo(*cv.T(*wxy[0]))
            for q in wxy[1:]:
                path.lineTo(*cv.T(*q))
            wpx = float(np.mean(sw_mag * wk)) * 2 * self.R_WIRE * cv.px
            c.drawPath(path, sk.Paint(AntiAlias=True, Style=sk.Paint.kStroke_Style, StrokeWidth=wpx,
                                      StrokeCap=sk.Paint.kRound_Cap, StrokeJoin=sk.Paint.kRound_Join,
                                      Color=sk.ColorBLACK))
            c.restore()
            # coloured light through the glass: a tinted caustic in each bead's shadow
            c.saveLayer(None, sk.Paint(BlendMode=sk.BlendMode.kPlus,
                                       ImageFilter=sk.ImageFilters.Blur(sigma * 0.9, sigma * 0.9)))
            for (x, y), r, lb in zip(sxy, s_mag * sk_ * self.R_SPH, self.cluster):
                X, Y = cv.T(x, y)
                c.drawCircle(X, Y, 0.5 * r * cv.px, cv.fill(self.cols[lb], 0.24 * min(lamp, 1.0)))
            c.restore()
        # the object: beads and wire segments, far to near
        bxy, bk = self.proj(P)
        bb = self._bright(P, lamp)
        spr = self.sprites()
        nlev = len(spr[0])
        lv = np.clip(np.round(bb * (nlev - 1)), 0, nlev - 1).astype(int)
        mid = (Wp[1:] + Wp[:-1]) / 2
        mxy, _ = self.proj(Wp)
        mk = self.proj(mid)[1]
        wb = self._bright(mid, lamp)
        items = [(P[i, 1], 0, i) for i in range(len(P))] + [(mid[j, 1], 1, j) for j in range(len(mid))]
        items.sort(key=lambda q: -q[0])
        samp = sk.SamplingOptions(sk.FilterMode.kLinear)
        bp = sk.Paint(AntiAlias=True)
        gold = to_lin(np.array(rgb255(C.pc1)) / 255.0)
        lampc = to_lin(np.array(rgb255(C.lamp)) / 255.0)
        Lc = -self.d
        lscr = np.array([Lc[0], Lc[2]])
        lscr = lscr / np.linalg.norm(lscr)
        tube = sk.Paint(AntiAlias=True, Style=sk.Paint.kStroke_Style, StrokeCap=sk.Paint.kRound_Cap)

        def hexs(lin_rgb):
            v = to_srgb(lin_rgb)
            return "#" + "".join(f"{int(round(min(max(q, 0), 1) * 255)):02X}" for q in v)

        for _, kind, i in items:
            if kind == 0:
                X, Y = cv.T(*bxy[i])
                r = self.R_SPH * bk[i] * cv.px
                c.drawImageRect(spr[self.cluster[i]][lv[i]], sk.Rect.MakeLTRB(X - r, Y - r, X + r, Y + r), samp, bp)
            else:
                b = float(wb[i])
                w = 2 * self.R_WIRE * mk[i] * cv.px
                a0, a1 = cv.T(*mxy[i]), cv.T(*mxy[i + 1])
                for width, colr, off in ((1.0, gold * (0.06 + 0.25 * b), 0.0), (0.7, gold * (0.10 + 0.75 * b), 0.08),
                                         (0.22, lampc * (0.15 + 1.1 * b), 0.26)):
                    tube.setStrokeWidth(width * w)
                    tube.setColor(cv.color(hexs(colr)))
                    ox, oy = lscr[0] * off * w, -lscr[1] * off * w
                    c.drawLine(a0[0] + ox, a0[1] + oy, a1[0] + ox, a1[1] + oy, tube)
        if overlay is not None:
            overlay(c, self)
        return cv.array()

    def layer_kw(self) -> dict:
        return self.cv.layer_kw()


def rot(axis, deg: float) -> np.ndarray:
    """A 3x3 rotation about `axis` ('x', 'y', 'z' or a vector) by `deg` degrees."""
    from scipy.spatial.transform import Rotation
    if isinstance(axis, str):
        return Rotation.from_euler(axis, deg, degrees=True).as_matrix()
    a = np.asarray(axis, float)
    return Rotation.from_rotvec(a / np.linalg.norm(a) * math.radians(deg)).as_matrix()


def slerp(Ra: np.ndarray, Rb: np.ndarray, u: float) -> np.ndarray:
    """Rotation between Ra (u = 0) and Rb (u = 1) along the shortest arc."""
    from scipy.spatial.transform import Rotation, Slerp
    return Slerp([0, 1], Rotation.from_matrix(np.stack([Ra, Rb])))([float(np.clip(u, 0, 1))]).as_matrix()[0]


def turn_world(room: ShadowRoom, R: np.ndarray, deg: float, axis=(0.0, 0.0, 1.0)) -> np.ndarray:
    """R turned by `deg` about a world axis (default: vertical) through the sculpture's centre: a turntable turn."""
    return room.E @ rot(axis, deg) @ room.E.T @ R


BLOB_ROTVEC = (1.361, -0.506, 1.903)
"""A view whose shadow is a shapeless blob (found by search: the three groups overlap, the outline is round)."""


def blob_view() -> np.ndarray:
    from scipy.spatial.transform import Rotation
    return Rotation.from_rotvec(BLOB_ROTVEC).as_matrix()


def ellipse_of(pts: np.ndarray, k: float = 2.2):
    """(centre, width, height, angle) of the k-sigma ellipse of 2D points."""
    c = pts.mean(0)
    w, V = np.linalg.eigh(np.cov(pts.T))
    return c, 2 * k * math.sqrt(w[1]), 2 * k * math.sqrt(w[0]), math.atan2(V[1, 1], V[0, 1])


# ----------------------------------------------------------------------------------------- digits & table
DIGIT_I = 3                         # 'the' digit of the video: the first 3 in the set (rebuilt again in ch5_s03)
CELL = 0.17                         # table / strip cell width (64 cells = 10.88 u)
ROW_H, PITCH = 0.15, 0.18           # table row height and pitch
TAB_X0 = -32 * CELL                 # table's left edge (it is centred)
ROW1_Y = 2.62                       # centre of the table's first visible row
TAB_Y0 = -3.29                      # table's bottom edge (rows are clipped below it)


class Glyphs:
    """CM glyphs cached once (one LaTeX run per distinct string), copied per use: never LaTeX per frame.

    Example:
        g = Glyphs([str(v) for v in range(17)], size=14)
        m.add(g("12", C.muted).move_to(ORIGIN))
    """

    def __init__(self, strings, size: float = 20, sans_: bool = True):
        wrap = (lambda s: r"\textsf{" + s + "}") if sans_ else (lambda s: s)
        self.cache = {s: (Tex(wrap(s), font_size=size) if sans_ else MathTex(s, font_size=size)) for s in strings}

    def __call__(self, s: str, color=None):
        g = self.cache[s].copy()
        return g.set_color(color or C.text)


class Counter:
    """A tabular CM-sans number from cached digit glyphs (thin space between thousands), right-aligned.

    Example:
        n = Counter(30)
        m.redraw(lambda t: n.number(1797, right=5.4, base=3.0), during=(a, b))
    """

    def __init__(self, size: float = 30, color=None):
        self.size, self.color = size, color or C.text
        self.g = {c: Tex(r"\textsf{" + c + "}", font_size=size, color=self.color) for c in "0123456789"}
        self.adv = self.g["0"].width * 1.08
        self.gap = self.adv * 0.42

    def number(self, n: int, right: float, base: float, color=None) -> VGroup:
        s = f"{int(n):,}".replace(",", " ")
        cells, x = [], right
        for ch in reversed(s):
            if ch == " ":
                x -= self.gap
                continue
            g = self.g[ch].copy()
            g.move_to(P3(x - self.adv / 2, 0)).shift(UP * (base - g.get_bottom()[1]))
            if color:
                g.set_color(color)
            cells.append(g)
            x -= self.adv
        return VGroup(*cells)


def grey(v: float) -> str:
    """Grey level 0..16 of the digit scans as a hex grey."""
    g = int(round(255 * min(max(v / 16.0, 0.0), 1.0)))
    return f"#{g:02X}{g:02X}{g:02X}"


class Table:
    """The digits table drawn with skia: row i is the 64 grey cells of image i, rows top to bottom.

    `draw(c, top, squeeze=1.0)`: `top` is the (fractional) index of the row at ROW1_Y; `squeeze` < 1 shrinks the
    pitch so more rows fit (the whole set at squeeze ≈ 0.019). Rows outside the box are skipped.
    """

    def __init__(self, cv: Canvas):
        self.cv = cv
        X, self.y = pd.digits()
        self.n = len(X)
        g = (np.clip(X / 16.0, 0, 1) * 255 + 0.5).astype(np.uint8)
        self.rgb = g                                                    # (n, 64) grey 0..255

    def row_y(self, i, top: float, squeeze: float = 1.0):
        return ROW1_Y - (np.asarray(i, float) - top) * PITCH * squeeze

    def draw(self, c, top: float, squeeze: float = 1.0, alpha: float = 1.0, fade_rows=None, clip_top=None):
        sk, cv = self.cv.skia, self.cv
        pitch = PITCH * squeeze
        h = max(ROW_H * squeeze, 1.0 / cv.px)
        i0 = max(0, int(math.floor(top - (Y1 + 0.5 - ROW1_Y) / pitch)))
        i1 = min(self.n, int(math.ceil(top + (ROW1_Y - TAB_Y0) / pitch)) + 1)
        p = sk.Paint(AntiAlias=False)
        for i in range(i0, i1):
            yc = ROW1_Y - (i - top) * pitch
            if yc + h / 2 > (ROW1_Y + ROW_H / 2 + 1e-3 if clip_top is None else clip_top) or yc - h / 2 < TAB_Y0:
                continue
            a = alpha * (1.0 if fade_rows is None else float(fade_rows(i)))
            if a <= 0.004:
                continue
            X0p, Y0p = cv.T(TAB_X0, yc + h / 2)
            hp = h * cv.px
            wp = CELL * cv.px
            row = self.rgb[i]
            for j in range(64):
                v = max(int(row[j]), 24)                                   # empty cells stay faintly visible
                p.setColor(sk.Color(v, v, v, int(255 * a)))
                c.drawRect(sk.Rect.MakeXYWH(X0p + j * wp + 0.5, Y0p, wp - 1.0, hp), p)


def spans_raster(cv: Canvas, y, x0, x1, v, h_px: float = 1.0, alpha: float = 1.0) -> np.ndarray:
    """Rasterize many thin horizontal grey spans at once (numpy, no per-span calls): RGBA uint8, premultiplied.

    y (n,) centre heights, x0/x1 (n,) world extents, v (n,) grey 0..255. Overlaps average; coverage sets alpha.
    """
    H, W = cv.h, cv.w
    yp = np.clip(((cv.box[3] - np.asarray(y)) * cv.px).astype(int), 0, H - 1)
    a = np.clip(((np.asarray(x0) - cv.box[0]) * cv.px), 0, W)
    b = np.clip(((np.asarray(x1) - cv.box[0]) * cv.px), 0, W)
    b = np.maximum(b, a + 1.0)                                   # every span covers at least a pixel
    ia, ib = a.astype(int), np.minimum(b.astype(int), W)
    rows = max(1, int(round(h_px)))
    acc = np.zeros((H, W + 1), np.float32)
    cnt = np.zeros((H, W + 1), np.float32)
    for dy in range(rows):
        yy = np.clip(yp + dy - rows // 2, 0, H - 1)
        np.add.at(acc, (yy, ia), v)
        np.add.at(acc, (yy, ib), -np.asarray(v, np.float32))
        np.add.at(cnt, (yy, ia), 1.0)
        np.add.at(cnt, (yy, ib), -1.0)
    acc, cnt = np.cumsum(acc, 1)[:, :W], np.cumsum(cnt, 1)[:, :W]
    g = np.where(cnt > 0.5, acc / np.maximum(cnt, 1.0), 0.0)
    cov = np.clip(cnt, 0, 1) * alpha
    out = np.empty((H, W, 4), np.uint8)
    out[..., :3] = np.clip(g * cov, 0, 255)[..., None].astype(np.uint8)
    out[..., 3] = (cov * 255).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------ chapter cards
def chapter_card(s, t0: float, t1: float, word: str, title: str, z: float = 20):
    """The L1 chapter card (CM sans 'chapter …', small-caps title, 2.8 u gold rule) on [t0, t1]; returns its
    opacity track so the scene can fade a carry-over strip with it.

    Example:
        on = chapter_card(s, t0, t0 + 2.6, "chapter one", "Data as a Cloud")
    """
    on = keys((t0, 0.0), (t0 + 0.5, 1.0), (t1 - 0.5, 1.0), (t1, 0.0))
    m = s.manim(z=z, opacity=on)
    card = VGroup(sans(word, 26, C.muted), caps(title, 58),
                  Line(LEFT * 1.4, RIGHT * 1.4, stroke_color=C.pc1, stroke_width=3)).arrange(DOWN, buff=0.24)
    m.add(card.move_to(P3(0, 0.45)))
    return on


def digit_map_xy(box) -> tuple[np.ndarray, np.ndarray]:
    """The 1,797 digits on PC1/PC2 (the in_s03 orientation), fitted into world box. Returns (xy (n, 2), labels)."""
    D = pd.digits_pca()
    _, y = pd.digits()
    Z = D.Z[:, :2] * np.array([1, -1])
    k = min((box[2] - box[0]) / np.ptp(Z[:, 0]), (box[3] - box[1]) / np.ptp(Z[:, 1]))
    mc = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2])
    return mc + k * (Z - (Z.max(0) + Z.min(0)) / 2), y


def digit_map(s, box, opacity, z: float = 2, size: float = 3.6, glow: float = 0.0, start=None):
    """The digit map as ten PointsLayers (one per class, its C.d<k> hue) in `box`. Returns (xy, labels)."""
    xy, y = digit_map_xy(box)
    for d in range(10):
        pos = xy[y == d]
        s.add(PointsLayer(lambda t, pos=pos: pos, color=getattr(C, f"d{d}"), size=size, glow=glow, additive=False,
                          z=z, opacity=opacity, start=start))
    return xy, y


# ------------------------------------------------------------------------------------- the people planes
KP = 0.105                          # world units per cm, the same through ch1 and ch2 (shapes never rescale)
RAW0 = np.array([-5.85, -2.85])     # world position of (150 cm, 150 cm) on the raw plane (ch1_s01-s02)
RAW_CM = 150.0
CEN0 = np.array([(STAGE_L2[0] + STAGE_L2[2]) / 2 + 0.2, (STAGE_L2[1] + STAGE_L2[3]) / 2 - 0.1])  # centred origin
STAGE_IN = (STAGE_L2[0] + 0.05, STAGE_L2[1] + 0.05, STAGE_L2[2] - 0.05, STAGE_L2[3] - 0.05)


def raw_xy(X) -> np.ndarray:
    """World xy of people in cm (height, arm span) on the raw plane."""
    return RAW0 + KP * (np.asarray(X, float) - RAW_CM)


def cen_xy(Xc, c0=CEN0) -> np.ndarray:
    """World xy of centred people (cm deviations) on a centred plane with origin c0."""
    return np.asarray(c0, float) + KP * np.asarray(Xc, float)


def raw_plane(pr: bool = True):
    """The raw plane: the Classic grid at 10 cm, axes crossing at (150, 150), ticks 160/180, axis names.
    Returns VGroup(grid, ticks, names) (the stage board is separate). pr=True: the premium plane on a card."""
    if pr:
        g = plane_grid(RAW0, KP * 10, STAGE_IN)
        fill, ts, ns = C.card, 24, 24
    else:
        g = grid_lines(np.eye(2), RAW0, KP * 10, STAGE_IN, n=12, minor=2)
        fill, ts, ns = None, 26, 26
    ticks = VGroup()
    for v in (160, 180):
        ticks.add(backed(tex(str(v), ts, C.muted), fill=fill).move_to(P3(*raw_xy((v, RAW_CM))) + P3(0, 0.22)))
        ticks.add(backed(tex(str(v), ts, C.muted), fill=fill).move_to(P3(*raw_xy((RAW_CM, v))) + P3(-0.3, 0)))
    names = VGroup(backed(sans("height", ns, C.muted), fill=fill).move_to(P3(*raw_xy((191, RAW_CM))) + P3(0, 0.25)),
                   backed(sans("arm span", ns, C.muted), fill=fill).move_to(P3(*raw_xy((RAW_CM, 199))) + P3(0.75, 0)))
    return VGroup(g, ticks, names)


def cen_names(c0=CEN0, hx: float = 26.0, pr: bool = True):
    """Axis names on the centred plane (frame 3 positions; `hx` cm: where 'height' sits along its axis)."""
    f, z = (C.card, 24) if pr else (None, 26)
    return VGroup(backed(sans("height", z, C.muted), fill=f).move_to(P3(*cen_xy((hx, -2.2), c0))),
                  backed(sans("arm span", z, C.muted), fill=f).move_to(P3(*cen_xy((9.5, 29.5), c0))))


def cen_grid(c0=CEN0, box=STAGE_IN, pr: bool = True):
    if pr:
        return plane_grid(c0, KP * 10, box)
    return grid_lines(np.eye(2), c0, KP * 10, box, n=12, minor=2)


def mean_ring(p, r: float = 0.1, pr: bool = True):
    return Circle(radius=r, stroke_color=C.mean, stroke_width=3.5, fill_color=C.card if pr else C.bg,
                  fill_opacity=1.0).move_to(p)


RAIL_K = 0.36                       # mini-board scale of the people cloud in the rail


def eq_centre(size: float = 40):
    return Eqn(r"\tilde x_i = x_i - \mu", colors={r"\mu": C.mean}, size=size)


def eq_mean(size: float = 40):
    return Eqn(r"\mu = \tfrac{1}{n}\sum_i x_i", colors={r"\mu": C.mean}, size=size)


def rail_cloud_parts(pr: bool = True):
    """B_cloud's content at its rail position: (dots, ring, equation). Board frame is board(slot(0))
    (card(slot(0)) with pr=True, and the dots are beads)."""
    P = pd.people2()
    box = slot(0)
    c = np.array([3.55, (box[1] + box[3]) / 2])
    if pr:
        d = VGroup(*[bead(P3(*(c + KP * RAIL_K * p)), r=0.034) for p in P.Xc])
    else:
        d = dots([P3(*(c + KP * RAIL_K * p)) for p in P.Xc], C.data, r=0.035)
    ring = Circle(radius=0.06, stroke_color=C.mean, stroke_width=2.5).move_to(P3(*c))
    eq = eq_centre(36).move_to(P3(5.25, c[1]))
    return d, ring, eq


def rail_cloud(pr: bool = True):
    d, ring, eq = rail_cloud_parts(pr)
    return VGroup(card(slot(0)) if pr else board(slot(0)), d, ring, eq)


def eq_var(size: float = 40):
    return Eqn(r"\sigma^2 = \tfrac{1}{n}\sum_i \left(x_i-\mu\right)^2", colors={r"\sigma^2": C.spread, r"\mu": C.mean},
               size=size)


def var_square(side: float, corner, stroke: float = 3.5, fill: float = 0.3):
    """The variance square: side sigma (world units), its bottom-left corner at `corner`."""
    return Square(side_length=side, stroke_color=C.spread, stroke_width=stroke, fill_color=C.spread,
                  fill_opacity=fill).move_to(P3(corner[0] + side / 2, corner[1] + side / 2))


def rail_var_parts():
    """B_var's content at its rail position (slot 1): (variance square, equation)."""
    P = pd.people2()
    box = slot(1)
    cy = (box[1] + box[3]) / 2
    side = KP * math.sqrt(P.C[0, 0]) * 0.6
    sq = var_square(side, (box[0] + 0.3, box[3] - 0.28 - side), stroke=2.6)
    eq = eq_var(38)
    eq.scale(min(1.0, (box[2] - box[0] - 0.5) / eq.width)).move_to(P3((box[0] + box[2]) / 2, box[1] + 0.62))
    return sq, eq


def rail_var(pr: bool = True):
    sq, eq = rail_var_parts()
    return VGroup(card(slot(1)) if pr else board(slot(1)), sq, eq)


# --------------------------------------------------------------------------------- ch2: lines, shadows, dial
def people_v():
    """(P, V) for the people data with PC2 signed so that positive = arms long for one's height."""
    P = pd.people2()
    V = P.V.copy()
    if V[1, 1] < 0:
        V[:, 1] *= -1
    return P, V


PHI1 = math.degrees(math.atan2(*people_v()[1][::-1, 0]))     # PC1's angle, degrees (about 49.3)


def udir(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def probe_line(c0, deg: float, L_cm: float = 32.0, color=None, width: float = 3.5, opacity: float = 1.0, k=KP):
    u = udir(deg)
    c0 = np.asarray(c0, float)
    return Line(P3(*(c0 - k * L_cm * u)), P3(*(c0 + k * L_cm * u)), stroke_color=color or C.probe,
                stroke_width=width, stroke_opacity=opacity)


def feet(Xc, deg: float) -> np.ndarray:
    """Feet of the perpendiculars from centred points onto the line through 0 at angle deg (cm)."""
    u = udir(deg)
    return (np.asarray(Xc) @ u)[:, None] * u


def drops_shadows(c0, deg: float, Xc, drop=1.0, shadow=1.0, drop_col=None, drop_op: float = 0.5,
                  drop_w: float = 1.4, k=KP):
    """Perpendicular drops (staggered by `drop` 0..1) and hollow shadow dots on the line at angle deg."""
    c0 = np.asarray(c0, float)
    F = feet(Xc, deg)
    n = len(Xc)
    g = VGroup()
    for i, (x, f) in enumerate(zip(Xc, F)):
        loc = min(max(drop * 1.5 - 0.5 * i / n, 0.0), 1.0)
        if loc > 0.001:
            a, b = c0 + k * x, c0 + k * (x + (f - x) * loc)
            g.add(Line(P3(*a), P3(*b), stroke_color=drop_col or C.muted, stroke_width=drop_w, stroke_opacity=drop_op))
    if shadow > 0.001:
        for f in F:
            g.add(Circle(radius=0.05, stroke_color=C.data, stroke_width=2.2, stroke_opacity=shadow).move_to(P3(*(c0 + k * f))))
    return g


def dial(c, r: float, deg_now=None, trace=None, alpha: float = 1.0, tip_col=None, grid: bool = True):
    """The polar dial: spread of the shadows u^T C u against the line's angle, radius r at the peak.
    `trace` = (deg_a, deg_b) draws the record between those angles (and their opposites); `deg_now` the tip."""
    P = pd.people2()
    c = np.asarray(c, float)
    vmax = float(P.lam[0])
    g = VGroup()
    if alpha <= 0.001:
        return g
    if grid:
        for f in (1 / 3, 2 / 3, 1.0):
            g.add(Circle(radius=r * f, stroke_color=C.plane, stroke_width=1.2, stroke_opacity=alpha)
                  .move_to(P3(*c)))
        for d in (0, 90):
            u = udir(d) * r * 1.08
            g.add(Line(P3(*(c - u)), P3(*(c + u)), stroke_color=C.plane, stroke_width=1.2,
                       stroke_opacity=alpha))

    def pt(deg):
        v = float(P.var_along(np.array([math.radians(deg)]))[0])
        return c + r * v / vmax * udir(deg)

    if trace is not None and abs(trace[1] - trace[0]) > 0.2:
        a, b = trace
        m_ = max(2, int(abs(b - a) / 1.5) + 1)
        for off in (0.0, 180.0):
            ds = np.linspace(a, b, m_) + off
            g.add(VMobject(stroke_color=C.spread, stroke_width=3.2, stroke_opacity=alpha)
                  .set_points_as_corners([P3(*pt(d)) for d in ds]))
    if deg_now is not None:
        col = tip_col or C.spread
        for off in (0.0, 180.0):
            p = pt(deg_now + off)
            g.add(Line(P3(*c), P3(*p), stroke_color=C.probe, stroke_width=1.4, stroke_opacity=0.6 * alpha))
            g.add(Dot(P3(*p), radius=0.065, color=col, fill_opacity=alpha))
    return g


def person_icon(x, y, H: float, span: float = 1.0, color=None, alpha: float = 1.0):
    """A small line-drawn person, feet at (x, y), H tall, arms straight out, fingertip span = span * H."""
    col = color or C.probe
    kw = dict(stroke_color=col, stroke_width=max(1.6, 3.2 * H), stroke_opacity=alpha)
    hr = 0.07 * H
    sh_y, hip_y = y + 0.80 * H, y + 0.49 * H
    return VGroup(Circle(radius=hr, **kw).move_to(P3(x, y + H - hr)),
                  Line(P3(x, y + H - 2 * hr), P3(x, hip_y), **kw),
                  Line(P3(x - span * H / 2, sh_y), P3(x + span * H / 2, sh_y), **kw),
                  Line(P3(x, hip_y), P3(x - 0.1 * H, y), **kw),
                  Line(P3(x, hip_y), P3(x + 0.1 * H, y), **kw))


def eq_obj(size: float = 40):
    return Eqn(r"\max_{\lVert u\rVert = 1}\ \tfrac{1}{n}\sum_i \left(\tilde x_i\cdot u\right)^2",
               size=size)


def rail_obj_parts():
    """B_varu at its rail position (slot 1): the objective."""
    box = slot(1)
    eq = eq_obj(40)
    eq.scale(min(1.0, (box[2] - box[0] - 0.4) / eq.width)).move_to(P3((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))
    return eq


def rail_obj():
    return VGroup(board(slot(1)), rail_obj_parts())


DIAL_BIG = (RAIL[0], RAIL[1], RAIL[2], RAIL[3])


def dial_pinned(alpha: float = 1.0):
    """B_dial in rail slot 2: its board and the full record, with the tip at PC1 in gold."""
    box = slot(2)
    c = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
    return VGroup(board(box), dial(c, 0.85, PHI1, (PHI1, PHI1 + 180), alpha, tip_col=C.pc1))


# ------------------------------------------------------------------------------------------ ch3: the matrix C
def c_matrix(size: float = 44):
    """'C =' and the people's 2x2 covariance (entries C.spread, one decimal). Returns VGroup(lhs, Mat)."""
    P = pd.people2()
    M = Mat([[f"{P.C[i, j]:.1f}" for j in range(2)] for i in range(2)], colors=C.spread, size=size, h_buff=1.3)
    return VGroup(tex(r"C =", size), M).arrange(RIGHT, buff=0.22)


def rail_c_parts():
    """B_C in rail slot 1 (index 0): the matrix."""
    box = slot(0)
    g = c_matrix(44)
    g.scale(min(1.0, (box[2] - box[0] - 0.5) / g.width, (box[3] - box[1] - 0.4) / g.height))
    return g.move_to(P3((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))


def rail_c():
    return VGroup(board(slot(0)), rail_c_parts())


def cov_heat(box, rows: int = 64, cv=None):
    """The digits' 64x64 covariance as crisp cells in world box (square), diverging C.data - black - C.spread.
    Draws the first `rows` rows. Returns the skia canvas array (premultiplied)."""
    D = pd.digits_pca()
    Cm = D.C
    vmax = float(np.abs(Cm).max())
    c = cv.begin()
    n = 64
    cell = (box[2] - box[0]) / n
    sk = cv.skia
    for i in range(min(rows, n)):
        for j in range(n):
            v = Cm[i, j] / vmax
            a = min(abs(v) ** 0.85, 1.0)
            if a < 0.02:
                continue
            X, Y = cv.T(box[0] + j * cell, box[3] - i * cell)
            c.drawRect(sk.Rect.MakeXYWH(X, Y, cell * cv.px + 0.5, cell * cv.px + 0.5),
                       cv.fill(C.spread if v > 0 else C.data, a, aa=False))
    return cv.array()


def rail_heat(s, z: float = 0.5, opacity=1.0, during=None):
    """B_heat in rail slot 2: the digits' 64x64 covariance (as ch3_s04 pins it). Adds its board and a static
    heatmap layer to scene `s`; returns the Manim layer holding the board."""
    box = slot(2)
    c, h = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]), (box[3] - box[1]) - 0.3
    cv = Canvas(box, px=s.comp.size[1] / 8)
    arr = cov_heat((c[0] - h / 2, c[1] - h / 2, c[0] + h / 2, c[1] + h / 2), 64, cv).copy()
    bd = s.manim(z=z - 0.1, opacity=opacity)
    bd.add(board(box))
    s.add(FramesLayer(lambda t: arr, z=z, during=during or [(s.start, s.end)], opacity=opacity, **cv.layer_kw()))
    return bd


# ------------------------------------------------------------------------------------------ ch4: eigenvectors
RECIPE = ("centre", "covariance", "eigenvectors", "sort", "project")


def recipe_eqs(size: float = 40):
    """The five recipe equations, one per step of RECIPE."""
    return [eq_centre(size),
            Eqn(r"C = \tfrac{1}{n}\sum_i \tilde x_i\,\tilde x_i^\top", colors={r"C": C.spread}, size=size),
            Eqn(r"C\,v_k = \lambda_k\,v_k", colors={r"C": C.spread, r"\lambda_k": C.spread}, size=size),
            Eqn(r"\lambda_1 \ge \lambda_2 \ge \cdots", colors={r"\lambda_1": C.spread, r"\lambda_2": C.spread},
                size=size),
            Eqn(r"z_k = \tilde x\cdot v_k", colors={r"z_k": C.pc1}, size=size)]


def recipe_rows(size: float = 40, word: float = 30, w_col: float = 2.6, eq_col: float = 4.2, dy: float = 0.92,
                top: float = 1.9, x0: float = -4.6):
    """The recipe board's rows: VGroup(VGroup(number, key word, equation)) laid out from (x0, top) down."""
    rows = VGroup()
    for k, (w, e) in enumerate(zip(RECIPE, recipe_eqs(size))):
        y = top - k * dy
        n = tex(str(k + 1), size, C.muted).move_to(P3(x0, y))
        kw = sans(w, word).move_to(P3(x0 + 0.45, y), aligned_edge=LEFT)
        e.move_to(P3(x0 + 0.45 + w_col, y), aligned_edge=LEFT)
        e.scale(min(1.0, eq_col / e.width), about_edge=LEFT)
        rows.add(VGroup(n, kw, e))
    return rows


def rail_recipe_parts():
    """B_recipe in rail slot 0: the five steps as numbered key words."""
    box = slot(0)
    g = VGroup(*[VGroup(tex(str(k + 1), 30, C.muted), sans(w, 26)).arrange(RIGHT, buff=0.18)
                 for k, w in enumerate(RECIPE)]).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    g.scale(min(1.0, (box[3] - box[1] - 0.3) / g.height))
    return g.move_to(P3((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))


def rail_recipe():
    return VGroup(board(slot(0)), rail_recipe_parts())


EIG_R = 1.3                         # ch4: unit arrow length on screen


def eig_transform(a1: float, a2: float, a3: float) -> np.ndarray:
    """ch4_s03's three moves as one matrix: turn to the eigen-axes (a1), stretch by the eigenvalues (a2, scaled so
    λ1 -> 2.2), turn back (a3); each 0..1. At (1, 1, 1) it equals C * 2.2 / λ1."""
    P = pd.people2()
    s1, s2 = 2.2, 2.2 * float(P.lam[1] / P.lam[0])

    def R(d):
        a = math.radians(d)
        return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])

    S = np.diag([1 + (s1 - 1) * a2, 1 + (s2 - 1) * a2])
    return R(PHI1 * a3) @ S @ R(-PHI1 * a1)


def eig_shape(A: np.ndarray, c0=CEN0, r: float = EIG_R):
    """The circle (C.probe) and the two eigen-arrows (v1 gold, v2 teal) under the 2x2 map A."""
    ts = np.linspace(0, 2 * math.pi, 121)
    circ = VMobject(stroke_color=C.probe, stroke_width=2.6).set_points_smoothly(
        [P3(*(c0 + r * (A @ np.array([math.cos(x), math.sin(x)])))) for x in ts])
    g = VGroup(circ)
    for d, col in ((PHI1 + 90, C.pc2), (PHI1, C.pc1)):
        g.add(Arrow(P3(*c0), P3(*(c0 + r * (A @ udir(d)))), buff=0, stroke_color=col, color=col, stroke_width=4.2,
                    max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=30))
    return g


def eq_vlv(size: float = 50):
    """C = V Λ V^T as parts (C, =, V, Λ, V^T)."""
    e = MathTex(r"C", "=", r"V", r"\,\Lambda\,", r"V^\top", font_size=size)
    e[0].set_color(C.spread)
    e[3].set_color(C.spread)
    return e


# ------------------------------------------------------------------------------------------ ch5: cutting dimensions
def scree_geom(box):
    """(bar width, bar height scale, curve height) of the digits' scree plot in world box."""
    D = pd.digits_pca()
    H = box[3] - box[1]
    return (box[2] - box[0]) / 64, 0.5 * H / float(D.share.max()), 0.95 * H


def scree(box, bar_w: float = 0.72, stroke: float = 3.0):
    """The digits' scree: 64 share bars (C.spread), the cumulative 'kept' curve (C.pc1), a baseline.
    Returns VGroup(base, bars, curve)."""
    D = pd.digits_pca()
    w, hb, hc = scree_geom(box)
    x0, y0 = box[0], box[1]
    bars = VGroup(*[Rectangle(width=w * bar_w, height=max(float(s) * hb, 1e-3), stroke_width=0, fill_color=C.spread,
                              fill_opacity=0.9).move_to(P3(x0 + (k + 0.5) * w, y0 + max(float(s) * hb, 1e-3) / 2))
                    for k, s in enumerate(D.share)])
    cum = np.cumsum(D.share)
    curve = VMobject(stroke_color=C.pc1, stroke_width=stroke).set_points_as_corners(
        [P3(x0, y0)] + [P3(x0 + (k + 1) * w, y0 + float(c) * hc) for k, c in enumerate(cum)])
    base = Line(P3(x0, y0), P3(box[2], y0), stroke_color=C.axis, stroke_width=2)
    return VGroup(base, bars, curve)


def rail_scree():
    """B_scree in rail slot 1 (board + scree)."""
    b = slot(1)
    return VGroup(board(b), scree((b[0] + 0.25, b[1] + 0.25, b[2] - 0.25, b[3] - 0.2), stroke=2.2))


def div_tiles(v, size: float, vmax=None, frame: bool = True):
    """An 8x8 pattern with signs (an eigen-digit) as crisp squares centred at the origin: C.spread for +, C.data
    for -, opacity |v| / vmax. Returns VGroup(cells, frame)."""
    a = np.asarray(v, float).reshape(8, 8)
    m = float(vmax or np.abs(a).max())
    cell = size / 8
    g = VGroup()
    for r in range(8):
        for c in range(8):
            x = a[r, c] / m
            g.add(Square(side_length=cell, stroke_width=0, fill_color=C.spread if x > 0 else C.data,
                         fill_opacity=min(abs(x), 1.0) ** 0.8).move_to(P3((c - 3.5) * cell, (3.5 - r) * cell)))
    fr = Square(side_length=size, stroke_color=C.plane, stroke_width=1.2, fill_opacity=0)
    return VGroup(g, fr) if frame else VGroup(g)


# ------------------------------------------------------------------------ premium look (ch1 first)
def card(box, tag=None, size: float = 22, r: float = 0.16):
    """A borderless board: a rounded card of lifted black (C.card), no frame line; optional tag top-left.

    Example:
        m.add(card(STAGE_L2))
    """
    x0, y0, x1, y1 = box
    g = VGroup(RoundedRectangle(corner_radius=r, width=x1 - x0, height=y1 - y0, stroke_width=0, fill_color=C.card,
                                fill_opacity=1.0).move_to(box_c(box)))
    if tag:
        g.add(sans(tag, size, C.muted).move_to(P3(x0 + 0.24, y1 - 0.2), aligned_edge=UL))
    return g


def plane_grid(c0, unit: float, box, n: int = 12, minor: int = 2, opacity: float = 1.0, fade=None, M=None,
               axes: bool = True):
    """The premium plane: slate major lines over faint minor ones (both fade out toward the board edge, into
    `fade`, default C.card) and light axes. Same structure as grid_lines: VGroup(minor, major, axes)."""
    fade = fade or C.card
    g = _grid_lines(np.eye(2) if M is None else M, c0, unit, box, n=n, minor=minor, opacity=opacity, axes=axes)
    dim_, major, ax_ = g
    for ln in dim_:
        ln.set_stroke(color=[fade, C.plane_minor, C.plane_minor, fade], width=1.0, opacity=opacity)
    for ln in major:
        ln.set_stroke(color=[fade, C.plane, C.plane, fade], width=1.4, opacity=opacity)
    for ln in ax_:
        ln.set_stroke(color=[fade, C.plane_axis, C.plane_axis, C.plane_axis], width=2.0, opacity=opacity)
    return g


def _lift(color, k: float) -> str:
    return interpolate_color(ManimColor(color), ManimColor(C.text), k).to_hex()


def bead(p, r: float = 0.062, color=None, a: float = 1.0, ring=None):
    """A premium data point: a dark separating ring (so it reads over grid lines), the colour body and a small
    specular highlight. Put beads on a bead_layer for their soft glow.

    Example:
        m.add(*[bead(P3(*q)) for q in xy])
    """
    col = color or C.data
    p = np.asarray(p, float)
    return VGroup(Dot(p, radius=r + 0.024, color=ring or C.card, fill_opacity=a),
                  Dot(p, radius=r, color=col, fill_opacity=a),
                  Dot(p + np.array([-0.28 * r, 0.28 * r, 0.0]), radius=0.36 * r, color=_lift(col, 0.65),
                      fill_opacity=0.8 * a))


def bead_layer(s, z: float, k: float = 0.5, radius: float = 7, **kw):
    """A Manim layer whose beads glow softly in their own colours."""
    return s.manim(z=z, fx=[Glow(None, strength=C.glow * k, radius=radius)], **kw)


class Aura:
    """The cloud's density as a soft field with two contour rings (a Gaussian splat of the points, px/unit `px`),
    drawn in `color` over a world box. `frame(pts, a, rings)` is a pure function of its inputs.

    Example:
        au = Aura(STAGE_IN)
        s.add(FramesLayer(lambda t: au.frame(xy, 1.0, 1.0), z=0.5, **au.layer_kw()))
    """

    def __init__(self, box, px: float = 56, sigma: float = 0.42, color=None, peak: float | None = None):
        self.box, self.px, self.sig = box, px, sigma
        x0, y0, x1, y1 = box
        self.w, self.h = int(round((x1 - x0) * px)), int(round((y1 - y0) * px))
        self.xs = x0 + (np.arange(self.w) + 0.5) / px
        self.ys = y1 - (np.arange(self.h) + 0.5) / px
        self.rgb = np.array(rgb255(color or C.data), np.float32) / 255
        self.peak = peak
        self._k = None

    def density(self, pts) -> np.ndarray:
        pts = np.asarray(pts, float)
        gx = np.exp(-((self.xs[None, :] - pts[:, :1]) ** 2) / (2 * self.sig ** 2))     # (n, w)
        gy = np.exp(-((self.ys[None, :] - pts[:, 1:2]) ** 2) / (2 * self.sig ** 2))    # (n, h)
        return (gy.T @ gx).astype(np.float32)                                          # (h, w)

    def frame(self, pts, a: float = 1.0, rings: float = 0.0) -> np.ndarray:
        key = (np.round(np.asarray(pts, float), 4).tobytes(), round(a, 3), round(rings, 3))
        if self._k == key:
            return self._out
        d = self.density(pts)
        pk = self.peak or float(d.max()) or 1.0
        u = np.clip(d / pk, 0, 1.4)
        al = 0.22 * (1 - np.exp(-2.4 * u)) * a
        if rings > 0.001:
            for lv in (0.22, 0.55):
                al = al + rings * a * 0.45 * np.exp(-((u - lv) / 0.014) ** 2)
        al = np.clip(al, 0, 1)
        out = np.empty((self.h, self.w, 4), np.uint8)
        out[..., :3] = np.clip(self.rgb[None, None, :] * 255 * al[..., None], 0, 255).astype(np.uint8)   # premultiplied
        out[..., 3] = (al * 255).astype(np.uint8)
        self._k, self._out = key, out
        return out

    def layer_kw(self) -> dict:
        x0, y0, x1, y1 = self.box
        return dict(height=y1 - y0, pos=((x0 + x1) / 2, (y0 + y1) / 2), premultiplied=True)


def soft_disc(r: float, color=None, px: float = 60, core: float = 0.72) -> tuple[np.ndarray, dict]:
    """A disc of `color` (default C.card) that is solid to core*r and fades to nothing at r: a soft hole in
    whatever is under it. Returns (rgba, layer_kw at the origin; pass pos=)."""
    n = int(round(2 * r * px))
    yy, xx = np.mgrid[0:n, 0:n]
    q = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    al = np.clip((1 - q) / (1 - core), 0, 1) ** 1.5
    rgb = np.array(rgb255(color or C.card), np.float32)
    out = np.empty((n, n, 4), np.uint8)
    out[..., :3] = (rgb[None, None] * al[..., None]).astype(np.uint8)
    out[..., 3] = (al * 255).astype(np.uint8)
    return out, dict(height=2 * r, premultiplied=True)
