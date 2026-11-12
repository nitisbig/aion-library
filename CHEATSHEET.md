# aion cheatsheet

Every `python` block here is checked by `tests/test_docs.py`: it must compile and use only real names.

## 1 · Beats (`videos/NNN-x/beats.py`)
```python
from aion import beats, cut, end, w

T = beats(
    grid="imagine a grid",                 # start of phrase; each search starts after the previous beat
    arrow="this arrow",
    stretch=w("stretches", offset=-0.1),   # nudged earlier
    settled=end("its own span"),           # END of the phrase
    cut1=cut("its own span", "now watch"), # scene boundary in the real silence, frame-snapped
    lam="lambda",
)
# T.grid → Beat (a float, seconds); T.grid.end; T.start; T.end (= audio length); T.cuts
```

## 2 · A scene (`scenes/s02_stretch.py`)
```python
from aion import *
from beats import T

@scene(T.cut1, T.cut2)                                   # absolute range; must tile the audio exactly
def s02_stretch(s):
    s.gradient(C.bg2, C.bg)                              # backdrop (z=-100)
    m = s.manim()                                        # transparent Manim layer
    grid = NumberPlane()
    v = Arrow(ORIGIN, [2, 1, 0], buff=0, color=C.vec)
    m.add(grid)                                          # visible from the scene start
    m.play(GrowArrow(v), at=T.arrow)                     # lands on the beat
    m.play(ApplyMatrix([[2, 0], [0, 1]], VGroup(grid, v)), at=T.stretch, dur=1.4, ease="easy_ease")
    eq = Eqn(r"A\vec v = \lambda \vec v", colors={r"\lambda": C.vec})
    m.seq(at=T.lam).play(Write(eq.to_edge(UP))).wait(0.2).play(Indicate(eq.part(r"\lambda")))
    s.camera.push(T.stretch, zoom=1.12, dur=2.5)         # crisp: vector layers re-render through the camera
    s.fx(Bloom(C.bloom), Lens(vignette=C.vignette, grain=C.grain))
```

## 3 · Animate anything with Tracks (pure functions of t)
```python
from aion import *

opacity = fade(5.0, out=9.0)                     # 0→1 landing at 5 s, back to 0 landing at 9 s
zoom = key(5.0, 1.0, 1.2, dur=2, ease="snap")    # hold a, move to b, hold b
glow = 0.2 + pulse(7.0, 0.8)                     # tracks support + - * /
m2 = key(5.0, [[1, 0], [0, 1]], [[2, 1], [0, 1]])  # arrays interpolate elementwise
spin = Clock(rate=keys((4.0, 1.0), (6.0, 0.1), (8.0, 1.0)), start=4.0)  # slow-mo via an integrated rate
breathe = wave(freq=0.5, amp=0.05, base=1.0)
```

## 4 · Manim score API (inside a scene, `m = s.manim()`)
```python
from aion import *

def build(s, T):
    m = s.manim()
    dot = Dot(color=C.accent)
    m.add(dot, at=T.start)                                            # exact time, no lead
    m.drive(dot, lambda d, t: d.move_to([np.cos(t), np.sin(t), 0]), during=(T.a, T.b))  # pure f(t)
    m.redraw(lambda t: Line(ORIGIN, [np.cos(t), np.sin(t), 0], color=C.muted), during=(T.a, T.b))
    m.play(FadeOut(dot), at=T.b)
    m.remove(dot, at=T.b + 1.0)
```

## 5 · GPU layers
```python
from aion import *

def build(s, T, cache):
    s.shader("layers/domain_coloring.frag", z=-1, u_frame=(14.22, 8), u_origin=(0, 0), u_unit=1.5,
             u_theta=key(T.turn, 0.0, PI / 2), u_opacity=1.0, u_sat=0.8)        # u_* = uniforms (Tracks OK)
    s.image("assets/images/portrait.png", height=4, pos=(-3, 0), opacity=fade(T.who))
    s.add(PointsLayer(lambda t: cache.at(t)["pos"], color=C.accent, size=2.5, glow=0.6))
    s.add(FieldLayer(lambda t: cache.at(t)["h"], cmap="diverging", vmin=-0.2, vmax=0.2, contours=10))
    s.solid(C.bg, z=-200)
```
Shader contract: `in vec2 v_uv` (0–1), `in vec2 v_pos` (Manim units, camera applied), `out vec4 frag` (linear RGB, straight alpha).
Auto uniforms: `u_time u_local u_res u_frame u_frame_index u_seed u_view u_view_inv`. `#include "common/color.glsl"`.
Video-specific shaders go in `videos/NNN-x/shaders/`.

## 6 · Effects (layer: `fx=[...]`; frame: `s.fx(...)`)
```python
from aion import *

layer_fx = [Glow(C.accent, strength=1.2, radius=4), Blur(radius=key(10.0, 3.0, 0.0))]
frame_fx = [Bloom(0.35, threshold=0.75), Grade(contrast=1.06, saturation=0.95),
            Vignette(0.25), Grain(0.02), ChromaticAberration(0.2), ZoomBlur(amount=pulse(12.0, 0.2))]
```
Blend modes: `blend="add" | "screen" | "multiply" | "overlay" | "soft_light" | "difference" | "lighten" | "darken" | "color_dodge"`.
Mattes: `layer(matte=other_layer, matte_mode="alpha" | "alpha_inv" | "luma" | "luma_inv")`.

## 7 · Camera (2.5D, pure f(t))
```python
from aion import *

def build(s, T):
    s.camera.push(T.zoom_in, zoom=1.3, dur=2)                   # dolly
    s.camera.pan(T.detail, to=(2, 1), dur=1.5)                  # world point to centre
    s.camera.frame(T.both, center=(0, 0), zoom=1.0)             # pan + zoom together
    s.camera.rotate(T.twist, 0.05)
    s.camera.shake(T.impact, amp=0.03, dur=0.5)
    s.solid(C.bg, z=-200, parallax=0.0)                         # parallax: 0 HUD, <1 background, 1 world
```

## 8 · Simulations (Taichi, baked once, cached)
```python
from aion import *

def build(s, T):
    flow = bake(Particles(n=30000, flow=0.6, seed=1), s.start, s.end)
    s.add(PointsLayer(lambda t: flow.at(t)["pos"], values=lambda t: flow.at(t)["speed"], cmap="inferno", vmax=0.8))
    waves = bake(Wave2D(drops=[(T.drop - s.start, 0.5, 0.5, 1.0)]), s.start, s.end)
    s.add(FieldLayer(lambda t: waves.at(t)["h"], cmap="diverging", vmin=-0.2, vmax=0.2))
```
Also: `NBody`, `Heat2D`, `Springs`. Custom: subclass `Sim` (fields, setup, step(dt), sample()).

## 9 · Theme (`theme.py`)
```python
from aion import BASE

theme = BASE.extend(x="#58c4dd", fx="#ffe94a", vec="#fc6255")
# BASE = Classic (default): pure black, crisp lines, no bloom/grain/vignette, Computer Modern math.
# MODERN = the earlier blue-black look with soft bloom and grain (`from aion import MODERN`).
# tokens: C.bg C.bg2 C.text C.muted C.faint C.accent C.accent2 C.good C.bad C.font C.display_font
#         C.body_size C.label_size C.title_size C.tex_size C.stroke C.thin C.margin C.lead C.fade C.bloom ...
#         C.grid C.grid_minor C.axis C.ghost C.frame (classic grid colours, part of BASE)
```

## 10 · Loop
`still --at <beat>` (look at it) → fix → `preview <scene>` → `render --bg` → `status` → `audit --delivery`.
