"""Design sheet for 008 (Classic): page 1 = palette, type, equations, hero frame; page 2 = key frames.

    uv run python videos/008-divergence-curl/design_sheet.py        # writes out/design/design_{1,2}.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "design"


def build(page):
    from PIL import Image

    from aion.render.project import load_video

    load_video("008", (1920, 1080), 30, only=["__none__"])            # activates the theme, imports no scenes
    from aion import (DOWN, LEFT, RIGHT, UP, C, Circle, DashedLine, Dot, FieldLayer, Line, PointsLayer,
                      Rectangle, RoundedRectangle, VGroup, np, scene)
    from aion.render import scenes as scene_mod
    from shots import (CAST, oiint, advect, arrow, cube_edges, curl_eq, div_eq, drain, dye, dye_poly, field_arrows,
                       flow_linear, frame_only, hero, hero_curl, hero_div, lamp, linear, ortho, paddle,
                       panel, poly_area, river, sample_grid, spin_glyph, tex, words)

    def page1(s, m):
        title = words(r"Divergence \& Curl", size=84).move_to([-6.55, 3.3, 0], aligned_edge=LEFT)
        tag = words(r"Classic $\cdot$ crisp $\cdot$ two questions about a flow", size=36, color=C.muted)
        tag.next_to(title, DOWN, buff=0.18, aligned_edge=LEFT)
        m.add(title, tag)

        roles = ["field", "dust", "div", "sink", "curl", "cw", "xpart", "ypart", "boundary", "efield", "bfield",
                 "grid"]
        for i, r in enumerate(roles):
            col = getattr(C, r)
            box = RoundedRectangle(width=0.82, height=0.5, corner_radius=0.06, stroke_color=C.frame,
                                   stroke_width=1.2, fill_color=col, fill_opacity=1.0)
            box.move_to([-6.1 + 1.07 * (i % 6), 1.55 - 1.3 * (i // 6), 0])
            m.add(box, words(r, size=24).next_to(box, DOWN, buff=0.1),
                  words(col.upper().replace("#", r"\#"), size=17, color=C.muted).next_to(box, DOWN, buff=0.42))

        d = div_eq(size=50).move_to([-6.55, -1.35, 0], aligned_edge=LEFT)
        c = curl_eq(size=50).move_to([-6.55, -2.65, 0], aligned_edge=LEFT)
        v = tex(r"\mathbf{F}(x,y)=\big(", "P", ",", "Q", r"\big)", size=40,
                colors={1: C.xpart, 3: C.ypart}).move_to([-6.55, -3.6, 0], aligned_edge=LEFT)
        m.add(d, c, v)

        # hero frame: divergence map under the hero field, dust carried a moment
        cx, cy, w, h = 3.55, 0.35, 6.6, 3.71
        s.add(FieldLayer(lambda t: sample_grid(lambda X, Y: hero_div(2.0 * (X - cx), 2.0 * (Y - cy)), (cx, cy), (w, h)),
                         cmap="diverging", vmin=-2.2, vmax=2.2, extent=(w, h), center=(cx, cy),
                         colors=(C.sink, C.bg, C.div), alpha=0.85, animated=False, z=-5))
        # field coords = 2 * (world - centre): the panel shows the hero's [-6.6, 6.6] x [-3.7, 3.7]
        F = lambda x, y: hero(2.0 * x, 2.0 * y)
        m.add(field_arrows(F, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), step=0.33, scale=0.13,
                           width=1.6, origin=(cx, cy)))
        rng = np.random.default_rng(3)
        p0 = rng.uniform([-6.4, -3.6], [6.4, 3.6], (1400, 2))
        p1 = advect(hero, p0, 0.6, steps=40)
        p1 = p1[(np.abs(p1[:, 0]) < 6.55) & (np.abs(p1[:, 1]) < 3.65)]
        pts = np.stack([cx + p1[:, 0] / 2, cy + p1[:, 1] / 2], 1)
        s.add(PointsLayer(lambda t: pts, color=C.dust, size=1.7, glow=0.0, alpha=0.75, animated=False, z=2))
        m.add(frame_only(cx, cy, w, h))
        m.add(tex(r"\nabla\cdot\mathbf{F}", size=34, colors={0: C.div}).move_to([cx + w / 2 - 0.55, cy + h / 2 - 0.3, 0]))

        # curl map thumbnail + paddle
        cx2, cy2, w2, h2 = 1.55, -2.55, 2.6, 1.46
        k2 = 13.2 / w2
        s.add(FieldLayer(lambda t: sample_grid(lambda X, Y: hero_curl(k2 * (X - cx2), k2 * (Y - cy2)), (cx2, cy2), (w2, h2)),
                         cmap="diverging", vmin=-2.2, vmax=2.2, extent=(w2, h2), center=(cx2, cy2),
                         colors=(C.cw, C.bg, C.curl), alpha=0.85, animated=False, z=-5))
        m.add(frame_only(cx2, cy2, w2, h2),
              tex(r"\nabla\times\mathbf{F}", size=30, colors={0: C.curl}).move_to([cx2 + 0.85, cy2 + 0.48, 0]))
        # type specimen
        m.add(words(r"Computer Modern", size=34).move_to([3.15, -1.95, 0], aligned_edge=LEFT),
              words(r"symbols and key words only", size=26, color=C.muted).move_to([3.15, -2.45, 0], aligned_edge=LEFT),
              tex(r"\oint_{\partial S}\mathbf{F}\cdot d\mathbf{r}", size=32, colors={0: C.boundary}).move_to([3.15, -3.25, 0], aligned_edge=LEFT),
              oiint(r"_{S}\mathbf{F}\cdot\mathbf{n}\,dS", size=32, color=C.boundary).move_to([4.95, -3.25, 0], aligned_edge=LEFT))

    def tile(m, cx, cy, w=2.15, h=2.15, label=None, lcol=None):
        m.add(panel(cx, cy, w, h))
        if label:
            m.add(tex(label, size=28, colors={0: lcol or C.text}).move_to([cx, cy - h / 2 - 0.3, 0]))
        return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

    def page2(s, m):
        m.add(words(r"Key frames", size=56).move_to([-6.55, 3.45, 0], aligned_edge=LEFT))
        xs = [-5.6, -3.15, -0.7, 1.75, 4.2]
        # row 1: the cast with dye, the lamp
        row1 = 1.55
        for k, (name, lab, col, T) in enumerate([("source", r"\text{area}\times 2.72", C.div, 0.5),
                                                 ("whirl", r"\text{area}\times 1.00", C.text, 0.9),
                                                 ("saddle", r"\text{area}\times 1.00", C.text, 0.5)]):
            box = tile(m, xs[k], row1, label=lab, lcol=col)
            A = CAST[name]
            c = np.array([xs[k], row1])
            m.add(field_arrows(linear(A), box, step=0.36, scale=0.22, width=1.4, origin=c))
            th = np.linspace(0, 2 * np.pi, 200, endpoint=False)
            d0 = np.stack([0.28 + 0.2 * np.cos(th), 0.22 + 0.2 * np.sin(th)], 1)
            if name == "saddle":
                d0 = d0 - [0.12, -0.25]
            d1 = flow_linear(A, d0, T)
            m.add(dye_poly(c + d0, C.ghost, opacity=0.0).set_stroke(C.muted, 1.2, opacity=0.6))
            m.add(dye_poly(c + d1, C.dust, opacity=0.28))
            ratio = poly_area(d1) / poly_area(d0)
            assert abs(ratio - (np.e if name == "source" else 1.0)) < 0.01, (name, ratio)
        # the lamp: arrows out, div 0 except the centre, equal flux circles
        box = tile(m, xs[3], row1, label=r"\nabla\cdot\mathbf{F}=0\ (r\neq 0)", lcol=C.div)
        c = np.array([xs[3], row1])
        m.add(field_arrows(lamp, box, step=0.3, scale=0.25, width=1.4, origin=c))
        for r in (0.35, 0.7):
            m.add(Circle(radius=r, color=C.boundary, stroke_width=1.6).move_to([*c, 0]))
        m.add(Dot([*c, 0], radius=0.05, color=C.div))
        # tiny square: out minus in
        cx, cy = xs[4], row1
        tile(m, cx, cy, label=r"\text{out}-\text{in}", lcol=C.text)
        sq = Rectangle(width=1.0, height=1.0, color=C.boundary, stroke_width=C.thin + 0.5).move_to([cx, cy, 0])
        m.add(sq,
              arrow([cx - 0.85, cy], [cx - 0.5, cy], C.xpart, width=3, tip=0.12),
              arrow([cx + 0.5, cy], [cx + 1.0, cy], C.xpart, width=3, tip=0.14),
              arrow([cx, cy - 0.85], [cx, cy - 0.5], C.ypart, width=3, tip=0.12),
              arrow([cx, cy + 0.5], [cx, cy + 0.95], C.ypart, width=3, tip=0.14))
        # row 2: whirl paddle, river paddle, drain ferris, circulation square, 3D cube flux
        row2 = -1.9
        box = tile(m, xs[0], row2, label=r"\operatorname{curl}=2", lcol=C.curl)
        c = np.array([xs[0], row2])
        m.add(field_arrows(linear(CAST["whirl"]), box, step=0.36, scale=0.22, width=1.4, origin=c),
              paddle(c + [0.4, 0.3], 0.5, radius=0.32, color=C.curl, width=3),
              spin_glyph(c + [0.4, 0.3], 0.45, +1, C.curl))
        box = tile(m, xs[1], row2, label=r"\operatorname{curl}=-1", lcol=C.cw)
        c = np.array([xs[1], row2])
        m.add(field_arrows(lambda x, y: river(x, y), box, step=0.36, scale=0.12, width=1.4, origin=c),
              paddle(c, 0.3, radius=0.32, color=C.cw, width=3), spin_glyph(c, 0.45, -1, C.cw))
        box = tile(m, xs[2], row2, label=r"\operatorname{curl}=0\ (r\neq0)", lcol=C.text)
        c = np.array([xs[2], row2])
        m.add(field_arrows(drain, box, step=0.3, scale=0.12, width=1.4, origin=c))
        m.add(Circle(radius=0.65, color=C.muted, stroke_width=1.2).move_to([*c, 0]).set_stroke(opacity=0.5))
        for a in (0.0, 2.1, 4.2):
            m.add(paddle(c + 0.65 * np.array([np.cos(a), np.sin(a)]), 0.4, radius=0.2, color=C.text, width=2.2))
        # circulation around a tiny square
        cx, cy = xs[3], row2
        tile(m, cx, cy, label=r"\oint \mathbf{F}\cdot d\mathbf{r}", lcol=C.boundary)
        s0 = 0.5
        corners = [(cx - s0, cy - s0), (cx + s0, cy - s0), (cx + s0, cy + s0), (cx - s0, cy + s0)]
        cols = [C.xpart, C.ypart, C.xpart, C.ypart]
        for k in range(4):
            a, b = np.array(corners[k]), np.array(corners[(k + 1) % 4])
            m.add(Line([*a, 0], [*b, 0], color=C.boundary, stroke_width=C.thin + 0.5))
            m.add(arrow(a + 0.3 * (b - a), a + 0.72 * (b - a), cols[k], width=3.2, tip=0.15))
        # 3D cube with flux arrows (source field (x, y, z): out of every face)
        cx, cy = xs[4], row2
        tile(m, cx, cy, label=None)
        m.add(oiint(r"\mathbf{F}\cdot\mathbf{n}\,dS", size=28, color=C.boundary).move_to([cx, cy - 1.42, 0]))
        proj = ortho(np.radians(-35), np.radians(25), scale=0.42, center=(cx, cy - 0.05))
        m.add(cube_edges(proj, C.boundary, width=2))
        for n in np.vstack([np.eye(3), -np.eye(3)]):
            if proj.depth(n) < -0.2:
                continue
            u, v = [e for e in np.eye(3) if abs(e @ n) < 0.5]
            for a in (-0.5, 0.5):
                for b in (-0.5, 0.5):
                    p = n + a * u + b * v
                    m.add(arrow(proj(p), proj(p + 0.75 * n), C.div, width=2.2, tip=0.1))

    @scene(0.0, 10.0)
    def sheet(s):
        s.solid(C.bg, z=-200)
        m = s.manim()
        (page1 if page == 1 else page2)(s, m)

    sd = scene_mod.REGISTRY[-1]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"design_{page}.png"
    Image.fromarray(sd.comp((1920, 1080), 30).frame(5.0, 150)).save(path)
    print(path)



if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:] if a.isdigit()] or [1, 2]
    for p in pages:
        build(p)
