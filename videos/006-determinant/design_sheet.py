"""Design sheets: one page per design system (palette, type, equations, grid and line work, the three states).

    uv run python videos/006-determinant/design_sheet.py          # writes out/design/design_{1,2,3}.png
    AION_DESIGN=2 uv run python videos/006-determinant/design_sheet.py --one
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

    load_video("006", (1920, 1080), 30, only=["s00"])          # activates the chosen design's theme
    from aion import (DOWN, LEFT, RIGHT, UP, Bloom, C, DashedVMobject, Label, Lens, Line, MathTex, Polygon,
                      RoundedRectangle, Square, Text, VGroup, np, scene)
    from aion.render import scenes as scene_mod
    from shots import A_MAIN, A_SWAP, A_ZERO, basis_arrows, glow_fx, grid_lines, span_area, words, Mat
    from theme import DESIGN

    def tex(*parts, size=46, colors=None):
        t = MathTex(*parts, font_size=size, color=C.text)
        for i, col in (colors or {}).items():
            t[i].set_color(col)
        return t

    @scene(0.0, 10.0)
    def sheet(s):
        s.solid(C.bg, z=-200)
        m = s.manim()
        g = s.manim(fx=glow_fx(), z=2)                        # arrows and outlines get the design's glow

        # ── title ──
        title = words(f"{DESIGN} $\\cdot$ {C.name}", size=96)
        title.move_to([-6.55, 3.25, 0], aligned_edge=LEFT)
        tag = words(C.tagline.replace("·", "$\\cdot$"), size=40, color=C.muted).next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)
        m.add(title, tag)

        # ── palette: one colour per math object ──
        roles = ["ihat", "jhat", "khat", "area", "flip", "collapse", "cutaway", "grid", "grid_minor", "ghost"]
        for i, r in enumerate(roles):
            col = getattr(C, r)
            box = RoundedRectangle(width=0.95, height=0.62, corner_radius=0.1, stroke_color=C.faint, stroke_width=1.5,
                                   fill_color=col, fill_opacity=1.0)
            box.move_to([-6.05 + 1.24 * (i % 5), 1.55 - 1.5 * (i // 5), 0])
            name = Label(r, color=C.text, size=19).next_to(box, DOWN, buff=0.12)
            code = Label(col.upper(), color=C.muted, size=15).move_to(box.get_center() + [0, -0.9, 0])
            m.add(box, name, code)

        # ── type and equations ──
        fonts = words(r"Computer Modern \quad Aa Bb 0123", size=40)
        fonts.move_to([-6.55, -1.72, 0], aligned_edge=LEFT)
        small = words(r"chapter titles and key words only", size=32, color=C.muted)
        small.next_to(fonts, DOWN, buff=0.16, aligned_edge=LEFT)
        mat = VGroup(tex("A =", size=46), Mat([["a", "b"], ["c", "d"]], colors=[C.ihat, C.jhat], size=46,
                                              h_buff=0.62, v_buff=0.52)).arrange(RIGHT, buff=0.25)
        det = tex(r"\det(A) =", "a", "d", "-", "b", "c", size=46)
        for part, col in zip(det[1:], (C.ihat, C.jhat, C.flip, C.jhat, C.ihat)):
            part.set_color(col)
        num = tex("3", r"\cdot", "2", "-", "1", r"\cdot", "1", "=", "5", size=40,
                  colors={0: C.ihat, 2: C.jhat, 3: C.flip, 4: C.jhat, 6: C.ihat, 8: C.area})
        mat.move_to([-6.55, -3.05, 0], aligned_edge=LEFT)
        det.next_to(mat, RIGHT, buff=0.7).shift(0.28 * UP)
        num.next_to(det, DOWN, buff=0.22, aligned_edge=LEFT)
        m.add(fonts, small, mat, det, num)

        # ── hero: the grid after A = [[3, 1], [1, 2]], the unit square and what it became ──
        box = (0.35, -0.3, 6.7, 3.6)
        c, u = np.array([1.75, 0.3]), 0.6
        frame = RoundedRectangle(width=box[2] - box[0], height=box[3] - box[1], corner_radius=0.12,
                                 stroke_color=C.faint, stroke_width=1.5, fill_color=C.bg, fill_opacity=0.55)
        frame.move_to([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2, 0])
        m.add(frame)
        m.add(grid_lines(np.eye(2), c, u, box, color=C.ghost, axes=False, opacity=1.6))
        m.add(grid_lines(A_MAIN, c, u, box))
        m.add(span_area(A_MAIN, c, u, opacity=0.3))
        unit = Square(side_length=u, color=C.text, stroke_width=C.thin).move_to([c[0] + u / 2, c[1] + u / 2, 0])
        m.add(DashedVMobject(unit, num_dashes=20))
        g.add(span_area(A_MAIN, c, u, opacity=0.0), basis_arrows(A_MAIN, c, u))
        ctr = c + u * (A_MAIN[:, 0] + A_MAIN[:, 1]) / 2
        m.add(tex("5", size=54, colors={0: C.area}).move_to([ctr[0], ctr[1], 0]))
        m.add(tex(r"\text{area}", "= 5", size=34, colors={0: C.muted, 1: C.area}).move_to([5.55, 3.1, 0]))
        ti, tj = c + u * A_MAIN[:, 0], c + u * A_MAIN[:, 1]
        m.add(tex(r"\hat{\imath}", size=40, colors={0: C.ihat}).move_to([ti[0] + 0.3, ti[1] - 0.22, 0]),
              tex(r"\hat{\jmath}", size=40, colors={0: C.jhat}).move_to([tj[0] - 0.32, tj[1] + 0.12, 0]))

        # ── the three states of a determinant ──
        tiles = [(A_MAIN, r"\det = 5", C.area), (A_SWAP, r"\det = -5", C.flip), (A_ZERO, r"\det = 0", C.collapse)]
        for k, (A, lab, col) in enumerate(tiles):
            cx, cy, uu = 1.4 + 2.12 * k, -1.95, 0.27
            tb = (cx - 0.95, cy - 0.85, cx + 0.95, cy + 0.85)
            card = RoundedRectangle(width=1.9, height=1.7, corner_radius=0.1, stroke_color=C.faint, stroke_width=1.5,
                                    fill_color=C.bg, fill_opacity=0.55).move_to([cx, cy, 0])
            o = np.array([cx - 0.62, cy - 0.45])
            m.add(card, grid_lines(A, o, uu, tb, n=10, width=1.4, axes=False))
            if abs(A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]) > 1e-9:
                m.add(span_area(A, o, uu, opacity=0.35))
            else:
                d = A[:, 0] / np.linalg.norm(A[:, 0])
                m.add(Line([*(o - 0.3 * d), 0], [*(o + 1.55 * d), 0], color=col, stroke_width=C.stroke))
            g.add(basis_arrows(A, o, uu, width=C.stroke))
            m.add(tex(lab, size=34, colors={0: col}).move_to([cx, cy - 1.2, 0]))

    sd = scene_mod.REGISTRY[-1]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"design_{DESIGN}.png"
    Image.fromarray(sd.comp((1920, 1080), 30).frame(5.0, 150)).save(path)
    print(path)


if __name__ == "__main__":
    if "--one" in sys.argv:
        build()
    else:
        for n in (4,) if "--all" not in sys.argv else (1, 2, 3, 4):
            subprocess.run([sys.executable, __file__, "--one"], env={**os.environ, "AION_DESIGN": str(n)}, check=True)
