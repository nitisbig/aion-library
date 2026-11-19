"""The low-poly game town (skia-python): flat-shaded blocks seen through a camera, drawn with the inverse of its matrix."""
from functools import lru_cache

import numpy as np
import skia

from aion import C, rng

SPEED = 2.6                       # world units per second
LIGHT = np.array([-0.45, 0.8, 0.4]) / np.linalg.norm([-0.45, 0.8, 0.4])


def _rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


@lru_cache(maxsize=None)
def _blocks():
    """Seeded blocks along both sides of a street: (x0, x1, z0, z1, height, roof role)."""
    g = rng(13)
    roofs = ("key", "back", "fwd", "cam", "det")
    out = []
    for row in range(26):
        z = -3.0 - row * 4.2
        for side in (-1, 1):
            w, d, h = g.uniform(2.0, 3.4), g.uniform(2.2, 3.3), g.uniform(1.4, 5.2)
            x0 = side * g.uniform(2.3, 3.0)
            x1 = x0 + side * w
            out.append((min(x0, x1), max(x0, x1), z - d, z, h, roofs[int(g.integers(len(roofs)))]))
    return out


def camera_matrix(t):
    """Where the camera sits in the world at time t: gliding along the street above the roofs, tilted down."""
    pitch = -0.22
    C4 = np.eye(4)
    C4[1:3, 1:3] = [[np.cos(pitch), -np.sin(pitch)], [np.sin(pitch), np.cos(pitch)]]
    C4[:3, 3] = [0.0, 8.0, 6.0 - SPEED * t]
    return C4


def _clip_near(cam_pts, near=0.15):
    """Clip a camera-space polygon against the near plane."""
    out = []
    n = len(cam_pts)
    for i in range(n):
        a, b = cam_pts[i], cam_pts[(i + 1) % n]
        ina, inb = a[2] < -near, b[2] < -near
        if ina:
            out.append(a)
        if ina != inb:
            s = (-near - a[2]) / (b[2] - a[2])
            out.append(a + s * (b - a))
    return out


def town_rgba(t, W=894, H=468):
    """One frame of the town at time t (seconds since the walk began), as RGBA uint8."""
    view = np.linalg.inv(camera_matrix(t))
    cam_pos = camera_matrix(t)[:3, 3]
    f = 0.95 * W
    k = max(1, W // 894)                              # line weights follow the raster scale
    surf = skia.Surface(W, H)
    can = surf.getCanvas()
    can.clear(skia.ColorBLACK)

    def project(world):
        cam = (view @ np.c_[world, np.ones(len(world))].T).T[:, :3]
        kept = _clip_near(list(cam))
        return [(W / 2 + f * p[0] / -p[2], H / 2 - f * p[1] / -p[2]) for p in kept]

    def path_of(pts):
        path = skia.Path()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.close()
        return path

    def col(rgb, a=255):
        return skia.Color(*(int(np.clip(v, 0, 255)) for v in rgb), a)

    grid = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.0 * k, Color=col(_rgb(C.grid_minor)))
    z_far, z_near = cam_pos[2] - 120, cam_pos[2] + 2
    for x in np.arange(-24, 25, 2.0):
        pts = project(np.array([[x, 0, z_far], [x, 0, z_near]], float))
        if len(pts) == 2:
            can.drawLine(*pts[0], *pts[1], grid)
    for z in np.arange(np.floor(z_far / 2) * 2, z_near, 2.0):
        pts = project(np.array([[-24, 0, z], [24, 0, z]], float))
        if len(pts) == 2:
            can.drawLine(*pts[0], *pts[1], grid)

    edge = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.1 * k, Color=col(_rgb(C.home), 170))
    fill = skia.Paint(AntiAlias=True, Style=skia.Paint.kFill_Style)
    blocks = [b for b in _blocks() if b[2] < cam_pos[2] and b[2] > cam_pos[2] - 100]
    blocks.sort(key=lambda b: (0.5 * (b[0] + b[1])) ** 2 + (0.5 * (b[2] + b[3]) - cam_pos[2]) ** 2, reverse=True)
    body = _rgb(C.shadow)
    for x0, x1, z0, z1, h, role in blocks:
        faces = [(np.array([[x0, 0, z1], [x1, 0, z1], [x1, h, z1], [x0, h, z1]], float), np.array([0, 0, 1.0]), body),
                 (np.array([[x1, 0, z1], [x1, 0, z0], [x1, h, z0], [x1, h, z1]], float), np.array([1.0, 0, 0]), body),
                 (np.array([[x0, 0, z0], [x0, 0, z1], [x0, h, z1], [x0, h, z0]], float), np.array([-1.0, 0, 0]), body),
                 (np.array([[x0, h, z1], [x1, h, z1], [x1, h, z0], [x0, h, z0]], float), np.array([0, 1.0, 0]), _rgb(getattr(C, role)))]
        for quad, normal, base in faces:
            if normal @ (cam_pos - quad[0]) <= 0:
                continue
            pts = project(quad)
            if len(pts) < 3:
                continue
            shade = 0.25 + 0.75 * max(0.0, float(normal @ LIGHT))
            fill.setColor(col(base * shade))
            path = path_of(pts)
            can.drawPath(path, fill)
            can.drawPath(path, edge)
    return surf.toarray(colorType=skia.kRGBA_8888_ColorType).copy()
