"""Lab check 2: off-screen pyvista helix (gold tube) with sine/cosine shadows on two walls."""
import time
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
t = np.linspace(0, 6 * np.pi, 1200)
x = t / np.pi * 1.2 - 3.6                       # time axis
pts = np.column_stack([x, np.cos(t), np.sin(t)])
tube = pv.Spline(pts, 1200).tube(radius=0.06, n_sides=24)
side = pv.Spline(np.column_stack([x, np.full_like(t, -1.6), np.sin(t)]), 1200).tube(radius=0.025)   # back wall: sine
floor = pv.Spline(np.column_stack([x, np.cos(t), np.full_like(t, -1.6)]), 1200).tube(radius=0.025)  # floor: cosine

a = time.perf_counter()
pl = pv.Plotter(off_screen=True, window_size=(1920, 1080))
pl.set_background("black")
pl.add_mesh(tube, color="#FFD43B", ambient=0.35, diffuse=0.75, specular=0.8, specular_power=40, smooth_shading=True)
pl.add_mesh(pv.Plane(center=(0, -1.62, 0), direction=(0, 1, 0), i_size=3.4, j_size=8),
            color="#0E131C", opacity=0.55)
pl.add_mesh(pv.Plane(center=(0, 0, -1.62), direction=(0, 0, 1), i_size=8, j_size=3.4),
            color="#0E131C", opacity=0.55)
pl.add_mesh(side, color="#FFD43B", opacity=0.45)
pl.add_mesh(floor, color="#FFD43B", opacity=0.45)
pl.add_light(pv.Light(position=(4, 6, 8), intensity=1.2))
pl.enable_anti_aliasing("ssaa")
pl.camera_position = [(6.5, 7.5, 4.0), (0, 0, 0), (0, 0, 1)]
first = time.perf_counter() - a
img = pl.screenshot("lab/2026-11-09-epicycles/pyvista_helix.png", return_img=True)
ts = []
for k in range(10):                               # orbit frames
    pl.camera.azimuth = 2
    b = time.perf_counter(); pl.render(); pl.screenshot(return_img=True); ts.append(time.perf_counter() - b)
info = pl.ren_win.ReportCapabilities()
print("setup", round(first, 2), "s; per frame", round(1000 * np.median(ts)), "ms at 1080p")
print([l for l in info.splitlines() if "OpenGL renderer" in l or "renderer string" in l][:2])
