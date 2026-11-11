"""Design sheets: one page per design system (palette, type, equations, line work, rendered look).

    uv run python videos/004-black-hole-math/design_sheet.py          # writes out/design/design_{1,2,3}.png
    AION_DESIGN=2 uv run python videos/004-black-hole-math/design_sheet.py --one
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "design"


def build():
    from PIL import Image

    from aion.render.project import load_video

    load_video("004", (1920, 1080), 30, only=["s00"])          # activates the chosen design's theme
    from aion import (BLACK, DOWN, LEFT, RIGHT, UP, BlackHoleLayer, Bloom, C, Circle, Eqn, Label, Line, RoundedRectangle,
                      Text, Tonemap, VGroup, VMobject, np, scene)
    from aion.maths import schwarzschild as S
    from aion.render import scenes as scene_mod
    from shots import bh_look, frac_colors, glow_fx
    from theme import DESIGN

    @scene(0.0, 10.0)
    def sheet(s):
        m = s.manim()
        title = Text(f"{DESIGN} · {C.name}", font=C.display_font, font_size=64, color=C.text)
        title.move_to([-6.55, 3.2, 0], aligned_edge=LEFT)
        tag = Label(C.tagline, color=C.muted).next_to(title, DOWN, buff=0.22, aligned_edge=LEFT)
        m.add(title, tag)

        roles = ["light", "mass", "horizon", "ring", "shadow", "disk", "newton", "grid"]
        sw = VGroup()
        for i, r in enumerate(roles):
            col = getattr(C, r)
            box = RoundedRectangle(width=1.05, height=0.7, corner_radius=0.12, stroke_width=0, fill_color=col,
                                   fill_opacity=1.0)
            box.move_to([-6.0 + 1.5 * (i % 4), 1.25 - 1.55 * (i // 4), 0])
            name = Label(r, color=C.text, size=22).next_to(box, DOWN, buff=0.14)
            code = Label(col.upper(), color=C.muted, size=16).move_to(box.get_center() + [0, -0.98, 0])
            sw.add(box, name, code)
        m.add(sw)

        fonts = Label(f"Text  {C.font}      Aa Bb 0123456789", color=C.text, size=28)
        fonts.move_to([-6.55, -2.0, 0], aligned_edge=LEFT)
        F = r"\frac{2GM}{c^2}"
        e1 = frac_colors(Eqn(r"r_s = " + F, colors={"r_s": C.horizon, F: C.text}, size=46), F, {2: C.mass, 4: C.light})
        FR = r"\frac{3GM}{c^2}"
        e2 = Eqn(r"u'' + u = " + FR + r"\,u^2", colors={"u": C.light, FR: C.mass}, size=46)
        e1.move_to([-6.55, -3.0, 0], aligned_edge=LEFT)
        e2.next_to(e1, RIGHT, buff=0.8)
        m.add(fonts, e1, e2)

        # line work: three rays with the design's stroke and glow
        g = s.manim(fx=[glow_fx()], z=2)
        hc, k = np.array([4.5, -2.3, 0.0]), 0.4

        def ray(b, col):
            ph, u, _ = S.orbit(abs(b), 1.0, phi_max=6 * np.pi)
            keep = u > 1 / 9.0
            r = 1 / u[keep]
            p = np.column_stack([hc[0] - k * r * np.cos(ph[keep]), hc[1] + np.sign(b) * k * r * np.sin(ph[keep]),
                                 np.zeros(keep.sum())])
            p = p[(p[:, 0] > 1.6) & (p[:, 0] < 6.75) & (np.abs(p[:, 1] - hc[1]) < 1.45)]
            return VMobject(stroke_color=col, stroke_width=C.stroke).set_points_as_corners(p)
        g.add(ray(3.3, C.light), ray(-2.72, C.light), ray(4.6, C.light))
        m.add(ray(1.6, C.bad), ray(-0.7, C.bad))
        m.add(Circle(radius=2.598 * k, color=C.shadow, stroke_width=C.thin).move_to(hc),
              Circle(radius=1.5 * k, color=C.ring, stroke_width=C.thin + 1).move_to(hc),
              Circle(radius=k, stroke_color=C.horizon, stroke_width=C.stroke, fill_color=BLACK, fill_opacity=1).move_to(hc))
        m.add(Line([0.95, 0.35, 0], [6.75, 0.35, 0], color=C.faint, stroke_width=C.thin))

        s.add(BlackHoleLayer(dist=46, inclination=84, azimuth=6, sky="galaxy", sky_center=(84, 8), height=3.25,
                             pos=(3.85, 2.2), scale_res=2, disk_t0=5.0 - 12.0, disk_rate=2.0, **bh_look(),
                             fx=[Bloom(C.bloom, threshold=0.9), Tonemap()]))

    sd = scene_mod.REGISTRY[-1]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"design_{DESIGN}.png"
    Image.fromarray(sd.comp((1920, 1080), 30).frame(5.0, 150)).save(path)
    print(path)


if __name__ == "__main__":
    if "--one" in sys.argv:
        build()
    else:
        for n in (1, 2, 3):
            subprocess.run([sys.executable, __file__, "--one"], env={**os.environ, "AION_DESIGN": str(n)}, check=True)
