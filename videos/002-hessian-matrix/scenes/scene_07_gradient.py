"""Scene 07 · Ch2: the gradient arrow (158.750–178.783 s).

"Put those two slopes together and you get an arrow on the floor, the gradient. It
points straight uphill and its length tells you how steep. Walk around and the arrow
changes. On a steep side, it's long. Near the top, it shrinks. And at a few special
points, it vanishes. These flat points are called critical points."

∇f = (∂f/∂x, ∂f/∂y) from ch2.grad (closed form). The walk's path, the arrow field and
the three critical points (two peaks, one saddle; Newton's method in ch2) are all
computed from f.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from manim import *

from aion import style as S
from aion.components.surface_gl import slice_line
import shared as V
import ch2 as L

START, END = V.scene_range(7)
K = 1.5                                    # world units of arrow per unit of slope (components)
K_LIVE = 0.75                              # ... for the live arrow on the walk
GX, GY = L.grad(L.X0, L.Y0)
PEAK = next((x, y) for x, y, k in L.CRIT if k == "peak" and x > 0)
WALK = [(L.X0, L.Y0), (1.15, -0.2), (1.18, 0.25), PEAK]


def floor_arrow(plate, a_fn, b_fn, color, width=6):
    def make():
        a, b = np.array(a_fn()), np.array(b_fn())
        if np.linalg.norm(b - a) < 1e-3:
            return VMobject()
        pa, pb = plate.project(*a), plate.project(*b)
        if np.linalg.norm(pb - pa) < 0.06:
            return VMobject()
        return Arrow(pa, pb, buff=0, color=color, stroke_width=width,
                     max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=12)
    return always_redraw(make)


def walk_point(s):
    """Point at fraction s along the WALK polyline."""
    pts = np.array(WALK)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    d = s * seg.sum()
    for i, L_ in enumerate(seg):
        if d <= L_ or i == len(seg) - 1:
            t = min(d / L_, 1.0)
            return pts[i] + t * (pts[i + 1] - pts[i])
        d -= L_


class Scene07Gradient(V.VideoScene):
    SCENE_START, SCENE_END = START, END

    def timeline(self):
        # ── scene 06's last frame ──
        xs_, ys_ = ValueTracker(1.0), ValueTracker(1.0)
        rig = L.land_rig()
        rig.dyn["slices"] = lambda: [
            slice_line(0, offset=L.Y0, color=S.HX, line=xs_.get_value(), plane=0.4 * xs_.get_value()),
            slice_line(90, offset=-L.X0, color=S.HY, line=ys_.get_value(), plane=0.4 * ys_.get_value())]
        plate = rig.plate()
        tx, ty = L.tangent_3d(plate, L.X0, L.Y0, (1, 0)), L.tangent_3d(plate, L.X0, L.Y0, (0, 1))
        dfx = MathTex(r"\frac{\partial f}{\partial x}", font_size=44, color=S.HX)
        V.pin(dfx, plate, lambda: L.DFX_AT)
        dfy = MathTex(r"\frac{\partial f}{\partial y}", font_size=44, color=S.HY)
        V.pin(dfy, plate, lambda: L.DFY_AT)
        self.add(plate, *rig.trackers(), xs_, ys_, tx, ty, dfx, dfy)

        # 2-4 · the two slopes drop to the floor as components and add up
        z0 = 0.0
        P = lambda: (L.X0, L.Y0, z0)
        ex = floor_arrow(plate, P, lambda: (L.X0 + K * GX, L.Y0, z0), S.HX)
        ey = floor_arrow(plate, P, lambda: (L.X0, L.Y0 + K * GY, z0), S.HY)
        drop = always_redraw(lambda: DashedLine(plate.project(L.X0, L.Y0, float(L.f(L.X0, L.Y0))),
                                                plate.project(*P()), color=S.MUTED, stroke_width=2,
                                                dash_length=0.07).set_opacity(0.6))
        self.beat("two slopes together", FadeOut(tx), FadeOut(ty), FadeOut(dfx), FadeOut(dfy),
                  xs_.animate.set_value(0.0), ys_.animate.set_value(0.0), FadeIn(drop),
                  GrowFromPoint(ex, plate.project(*P())), GrowFromPoint(ey, plate.project(*P())), rt=1.0)
        self.add(ex, ey, drop)
        slide = ValueTracker(0.0)
        ey2 = floor_arrow(plate, lambda: (L.X0 + slide.get_value() * K * GX, L.Y0, z0),
                          lambda: (L.X0 + slide.get_value() * K * GX, L.Y0 + K * GY, z0), S.HY)
        g = floor_arrow(plate, P, lambda: (L.X0 + K * GX, L.Y0 + K * GY, z0), S.GRAD, width=8)
        self.remove(ey)
        self.add(ey2)
        self.beat("arrow on the floor", slide.animate.set_value(1.0), rt=0.6)
        self.play(GrowFromPoint(g, plate.project(*P())), run_time=self.snap(0.5))
        self.add(g)
        nab = MathTex(r"\nabla f", font_size=46, color=S.GRAD)
        V.pin(nab, plate, lambda: (L.X0 + K * GX + 0.25, L.Y0 + K * GY - 0.2, z0), offset=DOWN * 0.2)
        self.beat("gradient", FadeIn(nab, shift=UP * 0.1), rt=0.5, after=162.0)

        # straight uphill: a dashed path up the surface in the gradient direction
        u = np.array([GX, GY]) / np.hypot(GX, GY)
        up_pts = [np.array([L.X0, L.Y0]) + t * u for t in np.linspace(0, 0.85, 18)]
        uphill = always_redraw(lambda: DashedVMobject(VMobject().set_points_smoothly(
            [plate.project(p[0], p[1], float(L.f(*p)) + 0.02) for p in up_pts]), num_dashes=14)
            .set_stroke(S.GRAD, 4, opacity=0.8))
        self.beat("straight uphill", Create(uphill), rt=0.7)
        self.add(uphill)
        brace = always_redraw(lambda: BraceBetweenPoints(plate.project(*P()),
                                                         plate.project(L.X0 + K * GX, L.Y0 + K * GY, z0),
                                                         color=S.MUTED))
        self.beat("how steep", FadeIn(brace), rt=0.5)

        # 2-5 · top-down: walk around with a live gradient arrow
        s = ValueTracker(0.0)
        walker = V.walker()
        wp = lambda: walk_point(s.get_value())
        V.pin(walker, plate, lambda: (*wp(), float(L.f(*wp()))))
        live = floor_arrow(plate, lambda: (*wp(), float(L.f(*wp()))),
                           lambda: (*(wp() + K_LIVE * L.grad(*wp())), float(L.f(*wp()))), S.GRAD, width=7)
        self.beat("walk around", *rig.to(pitch=89.0, yaw=-90.0, dist=8.2, contour=1.0, grid=(0.0, 0.0),
                                         target=(0.0, -0.05, 0.0)),
                  FadeOut(ex), FadeOut(ey2), FadeOut(g), FadeOut(drop), FadeOut(nab), FadeOut(uphill),
                  FadeOut(brace), FadeIn(walker), FadeIn(live), rt=2.0)
        self.play(s.animate.set_value(0.42), run_time=self.snap(self.t("steep side") - self.now), rate_func=smooth)
        self.play(s.animate.set_value(0.8), run_time=self.snap(self.t("near the top") - self.now + 0.3),
                  rate_func=linear)
        self.play(s.animate.set_value(1.0), run_time=self.snap(1.6), rate_func=rush_from)

        # the whole field, then the critical points
        field = L.field_arrows(plate)
        self.beat("vanishes", LaggedStart(*[FadeIn(a, scale=0.5) for a in field], lag_ratio=0.02), rt=1.2)
        rings = L.crit_rings(plate)
        self.beat("critical points", *[Create(r) for r in rings],
                  *[Flash(r.get_center(), color=S.TEXT, line_length=0.18, flash_radius=0.3) for r in rings], rt=0.8)
        self.finish()
