"""A small crisp 3D painter on skia: immediate mode, pure in its inputs, light on memory.

Objects are drawn in the order you call them, and a mesh sorts its own triangles. `View3D.project` gives frame
coordinates (Manim units), so equations and labels can be pinned to 3D points from a ManimLayer.
"""
import numpy as np
import skia

W, H = 2400, 1350           # supersampled 1.25x against 1080p; the compositor's mipmaps resolve it
PX = H / 8.0                # pixels per Manim unit


def rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


class Cam:
    """Orbit camera: azimuth and elevation in degrees, `zoom` Manim units per world unit, `center` a frame offset."""

    def __init__(self, az=-60.0, el=32.0, zoom=1.0, center=(0.0, 0.0), target=(0.0, 0.0, 0.0), dist=26.0):
        a, e = np.radians(az), np.radians(el)
        self.d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
        self.r = np.array([-np.sin(a), np.cos(a), 0.0])
        self.u = np.cross(self.d, self.r)
        self.zoom, self.center, self.target, self.dist = zoom, np.asarray(center, float), np.asarray(target, float), dist

    def frame(self, P):
        """World points (..., 3) to frame coordinates (..., 2) in Manim units, plus depth toward the camera."""
        Q = np.asarray(P, float) - self.target
        w = Q @ self.d
        f = self.dist / (self.dist - w)
        return np.stack([self.center[0] + self.zoom * f * (Q @ self.r), self.center[1] + self.zoom * f * (Q @ self.u)], -1), w

    def px(self, P):
        xy, w = self.frame(P)
        return np.stack([W / 2 + PX * xy[..., 0], H / 2 - PX * xy[..., 1]], -1), w


def _argb(c, a=1.0):
    c = np.clip(c, 0, 1)
    a = min(max(float(a), 0.0), 1.0)          # alpha > 1 would overflow the 32-bit colour
    return (int(a * 255) << 24) | (int(c[0] * 255) << 16) | (int(c[1] * 255) << 8) | int(c[2] * 255)


class View3D:
    """One reusable canvas. Call begin(cam), draw, then rgba()."""

    def __init__(self):
        self.surface = skia.Surface(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kUnpremul_AlphaType))
        self.canvas = self.surface.getCanvas()
        self.cam = None

    def begin(self, cam):
        self.cam = cam
        self.canvas.clear(0)
        return self

    def mesh(self, X, Y, Z, colors, alpha=1.0, light=(0.45, -0.55, 0.7), ambient=0.34, shade=True):
        """A grid surface. `colors` is (ny, nx, 3) in 0..1, or one hex string. Triangles are sorted back to front."""
        P = np.stack([X, Y, Z], -1)
        ny, nx = X.shape
        cols = np.broadcast_to(rgb(colors), P.shape).copy() if isinstance(colors, str) else np.asarray(colors, float).copy()
        if shade:
            du, dv = np.gradient(P, axis=1), np.gradient(P, axis=0)
            n = np.cross(du, dv)
            n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
            face = np.sign((n @ self.cam.d))[..., None]
            n = n * np.where(face == 0, 1, face)
            l = np.asarray(light, float) / np.linalg.norm(light)
            cols = cols * (ambient + (1 - ambient) * np.clip(n @ l, 0, 1))[..., None]
        xy, w = self.cam.px(P)
        i = np.arange(nx * ny).reshape(ny, nx)
        a, b, c, d = i[:-1, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, 1:].ravel(), i[1:, :-1].ravel()
        order = np.argsort(((w.ravel()[a] + w.ravel()[c]) / 2))
        tris = np.stack([a, b, c, a, c, d], -1)[order].ravel().tolist()
        pts = [skia.Point(float(u), float(v)) for u, v in xy.reshape(-1, 2).tolist()]
        A = int(np.clip(alpha, 0, 1) * 255) << 24
        c8 = (np.clip(cols.reshape(-1, 3), 0, 1) * 255).astype(np.int64)
        ints = (A | (c8[:, 0] << 16) | (c8[:, 1] << 8) | c8[:, 2]).tolist()
        v = skia.Vertices(skia.Vertices.kTriangles_VertexMode, pts, None, ints, tris)
        self.canvas.drawVertices(v, skia.Paint(), skia.BlendMode.kDst)

    def line(self, P, color, width=3.0, alpha=1.0, visible=None, close=False):
        """A polyline through world points; `visible` (bool per point) hides occluded stretches."""
        P = np.asarray(P, float)
        if close:
            P = np.vstack([P, P[:1]])
            visible = None if visible is None else np.append(visible, visible[0])
        xy, _ = self.cam.px(P)
        paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * W / 1920.0,
                           StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                           Color=_argb(rgb(color), alpha))
        path = skia.Path()
        pen = False
        for k, (x, y) in enumerate(xy.tolist()):
            on = True if visible is None else bool(visible[k])
            if on and pen:
                path.lineTo(x, y)
            elif on:
                path.moveTo(x, y)
            pen = on
        self.canvas.drawPath(path, paint)

    def dot(self, p, color, radius=0.1, ring=None):
        """A round marker with a radius in Manim units, always facing the camera."""
        xy, _ = self.cam.px(np.asarray(p, float))
        x, y = float(xy[0]), float(xy[1])
        if ring:
            self.canvas.drawCircle(x, y, (radius + 0.035) * PX, skia.Paint(AntiAlias=True, Color=_argb(rgb(ring))))
        self.canvas.drawCircle(x, y, radius * PX, skia.Paint(AntiAlias=True, Color=_argb(rgb(color))))

    def arrow(self, a, b, color, width=4.5, tip=0.26, alpha=1.0):
        """A straight arrow between world points; `tip` is its head length in Manim units."""
        (p, q), _ = self.cam.px(np.array([a, b], float))
        d = q - p
        L = float(np.linalg.norm(d))
        if L < 1.0:
            return
        d /= L
        n = np.array([-d[1], d[0]])
        t = min(tip * PX, 0.45 * L)
        base = q - d * t
        col = _argb(rgb(color), alpha)
        s = W / 1920.0
        path = skia.Path()
        path.moveTo(*p.tolist())
        path.lineTo(*base.tolist())
        self.canvas.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width * s,
                                              StrokeCap=skia.Paint.kRound_Cap, Color=col))
        head = skia.Path()
        head.moveTo(*q.tolist())
        head.lineTo(*(base + n * t * 0.46).tolist())
        head.lineTo(*(base - n * t * 0.46).tolist())
        head.close()
        self.canvas.drawPath(head, skia.Paint(AntiAlias=True, Color=col))

    def rgba(self):
        return self.surface.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
