"""S06 spring: pyvista off-screen frames of the circle sliding through time.

Every frame is a pure function of absolute audio time. Frames are cached as PNGs under
media/cache/s06_<w>x<h>_<fps>/ together with labels.json (screen positions of the label
anchors, in pixels, from VTK's own camera), so Manim labels stay pinned to the 3D view.

Geometry (world units): time runs along +x. The circle (radius 1) lies in the y–z
plane; its tip is (x_c, cos θ, sin θ). The back wall (y = +WALL) carries the shadow
(x, WALL, sin θ), a sine; the floor (z = −WALL) carries (x, cos θ, −WALL), a cosine.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

from aion import style as S

XS, XE, WALL = -3.6, 3.6, 1.6
TURNS = 3
AZ34, EL34 = -38.0, 24.0
DIST = 12.0


def _smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


class SpringTimeline:
    """Camera keyframes and the slide, all in absolute seconds."""

    def __init__(self, T: dict):
        self.T = T
        # (start, duration, (az, el)): each move eases from the previous view
        self.moves = [(T["another view"], 1.2, (AZ34, EL34)),
                      (T["from the side"], 1.4, (0.0, 0.0)),
                      (T["from above"], 1.4, (0.0, 89.5)),
                      (T["two shadows"], 1.2, (AZ34, EL34)),
                      (T["turning motion"], 0.8, (0.0, 0.0))]
        self.slide = (T["slide"], T["slide_end"])
        self.omega = 2 * np.pi * TURNS / (self.slide[1] - self.slide[0])

    def view(self, now):
        az, el = 0.0, 0.0
        for t0, d, (a1, e1) in self.moves:
            u = _smooth((now - t0) / d)
            az, el = az + (a1 - az) * u, el + (e1 - el) * u
        return az, el

    def x_c(self, now):
        a, b = self.slide
        return XS + (XE - XS) * float(np.clip((now - a) / (b - a), 0, 1))

    def theta(self, now):
        return self.omega * (now - self.slide[0])

    def theta_at_x(self, x):
        a, b = self.slide
        return self.omega * (x - XS) / (XE - XS) * (b - a)


def _camera(az, el):
    a, e = np.radians(az), np.radians(el)
    d = np.array([np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
    up = np.array([-np.sin(a) * np.sin(e), np.cos(a) * np.sin(e), np.cos(e)])
    return [tuple(DIST * d), (0.0, 0.0, 0.0), tuple(up)]


def _tube(pts, radius, sides=16):
    import pyvista as pv
    if len(pts) < 2:
        pts = np.array([[XS, 1, 0], [XS + 1e-4, 1, 0]])
    line = pv.lines_from_points(np.asarray(pts, float))
    return line.tube(radius=radius, n_sides=sides)


def _bloom(img: np.ndarray, k: float = 0.55) -> np.ndarray:
    from scipy.ndimage import gaussian_filter
    f = img.astype(np.float32) / 255.0
    h, w = f.shape[:2]
    q = f[: h // 4 * 4, : w // 4 * 4].reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
    q = np.maximum(q - 0.35, 0)
    b = gaussian_filter(q, sigma=(h / 1080 * 6, h / 1080 * 6, 0))
    b = np.repeat(np.repeat(b, 4, 0), 4, 1)
    out = f.copy()
    out[: b.shape[0], : b.shape[1]] += k * b
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


LABEL_ANCHORS = {"sin": (2.2, WALL, 1.45), "cos": (2.2, 1.45, -WALL)}


def render(times: np.ndarray, tl: SpringTimeline, size: tuple[int, int], out_dir: Path) -> Path:
    """Render one PNG per entry of `times` (absolute seconds) unless cached."""
    key = hashlib.sha1(json.dumps([list(map(float, times[[0, -1]])), len(times), tl.T, size,
                                   Path(__file__).read_text()]).encode()).hexdigest()[:10]
    d = out_dir / key
    if (d / "labels.json").exists():
        return d
    d.mkdir(parents=True, exist_ok=True)
    import pyvista as pv
    pv.OFF_SCREEN = True
    pv.global_theme.allow_empty_mesh = True
    w, h = size
    pl = pv.Plotter(off_screen=True, window_size=(w, h))
    pl.set_background("black")
    pl.enable_anti_aliasing("ssaa")
    pl.add_light(pv.Light(position=(4, -6, 8), intensity=1.1))

    gold = dict(color=S.INK, ambient=0.45, diffuse=0.7, specular=0.8, specular_power=40, smooth_shading=True)
    pl.add_mesh(pv.Plane(center=(0, WALL + 0.02, 0), direction=(0, 1, 0), i_size=2 * WALL, j_size=XE - XS + 0.8),
                color="#0E131C", opacity=0.55)
    pl.add_mesh(pv.Plane(center=(0, 0, -WALL - 0.02), direction=(0, 0, 1), i_size=XE - XS + 0.8, j_size=2 * WALL),
                color="#0E131C", opacity=0.55)
    axis = _tube([[XS - 0.3, 0, 0], [XE + 0.3, 0, 0]], 0.012, 8)
    pl.add_mesh(axis, color=S.ARM, opacity=0.35)

    meshes = {k: pv.PolyData() for k in ("helix", "wall", "floor", "ring", "arm", "pen")}
    pl.add_mesh(meshes["helix"], **gold)
    pl.add_mesh(meshes["wall"], color=S.INK, opacity=0.5, ambient=0.8)
    pl.add_mesh(meshes["floor"], color=S.INK, opacity=0.5, ambient=0.8)
    pl.add_mesh(meshes["ring"], color=S.FWD, ambient=0.6, smooth_shading=True)
    pl.add_mesh(meshes["arm"], color=S.ARM, ambient=0.6)
    pl.add_mesh(meshes["pen"], color=S.INK, ambient=1.0, diffuse=0.3)

    ring_t = np.linspace(0, 2 * np.pi, 121)
    ren = pl.renderer
    labels = []
    for i, now in enumerate(tqdm(times, desc="S06 spring (pyvista)", unit="fr")):
        xc, th = tl.x_c(now), tl.theta(now)
        x = np.linspace(XS, xc, max(2, int(260 * (xc - XS)) + 2))
        tx = tl.theta_at_x(x)
        drawn = xc > XS + 1e-3
        meshes["helix"].copy_from(_tube(np.column_stack([x, np.cos(tx), np.sin(tx)]) if drawn else [], 0.05))
        meshes["wall"].copy_from(_tube(np.column_stack([x, np.full_like(x, WALL), np.sin(tx)]) if drawn else [], 0.022, 8))
        meshes["floor"].copy_from(_tube(np.column_stack([x, np.cos(tx), np.full_like(x, -WALL)]) if drawn else [], 0.022, 8))
        meshes["ring"].copy_from(_tube(np.column_stack([np.full_like(ring_t, xc), np.cos(ring_t), np.sin(ring_t)]), 0.018, 8))
        tip = np.array([xc, np.cos(th), np.sin(th)])
        meshes["arm"].copy_from(_tube([[xc, 0, 0], tip], 0.02, 8))
        meshes["pen"].copy_from(pv.Sphere(radius=0.075, center=tip))
        pl.camera_position = _camera(*tl.view(now))
        pl.camera.view_angle = 30.0
        for mm in meshes.values():
            mm.Modified()
        pl.render()
        img = pl.screenshot(return_img=True)
        from PIL import Image
        Image.fromarray(_bloom(img)).save(d / f"{i:05d}.png", compress_level=1)
        pos = {}
        for name, p in LABEL_ANCHORS.items():
            ren.SetWorldPoint(*p, 1.0)
            ren.WorldToDisplay()
            px, py, _ = ren.GetDisplayPoint()
            pos[name] = (px / w, 1 - py / h)
        labels.append(pos)
    pl.close()
    (d / "labels.json").write_text(json.dumps(labels))
    return d
