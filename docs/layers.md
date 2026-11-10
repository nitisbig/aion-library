# Layers and the compositor

A scene is a stack of layers composited on the GPU (moderngl, linear light, RGBA16F, premultiplied
alpha), then graded and encoded. The builder `s` inside `@scene` creates them:

| builder call | layer | use |
|---|---|---|
| `s.solid(color)` | `Solid` | flat fill (z=-200 typical) |
| `s.gradient(a, b, radial=True, radius=…)` | `Gradient` | backdrop, z=-100 by default |
| `s.manim()` | `ManimLayer` | equations, geometry, axes, transforms (see manim-layer.md) |
| `s.shader("file.frag", u_x=…)` | `ShaderLayer` | per-pixel: fields, domain coloring, fractals |
| `s.image(path, height=)` | `ImageLayer` | PNG/JPG placed in world units |
| `s.add(ArrayLayer(rgba))` | `ArrayLayer` | numpy RGBA (skia/pyvista/matplotlib output) |
| `s.add(PointsLayer(fn))` | `PointsLayer` | 10³–10⁵ glowing points (sims, samples) |
| `s.add(FieldLayer(fn))` | `FieldLayer` | 2-D scalar field with colormap + contour lines |
| `s.precomp(build)` | `Comp` | nested group with its own fx / blend |

## Common layer parameters (all accept Tracks)
`z` (draw order), `start` / `end` (visibility window, default the scene), `opacity`, `blend`, `fx=[…]`,
`matte=<layer>` + `matte_mode` (`alpha`, `alpha_inv`, `luma`, `luma_inv`), `parallax` (1 world,
0 HUD/locked to screen, 0.3 distant background), `pos=(x, y)`, `scale`, `rotation`, `name`.

Blend modes: `normal`, `add`, `screen` (fast GL) and `multiply`, `overlay`, `soft_light`, `difference`,
`lighten`, `darken`, `color_dodge` (shader ping-pong, a little slower).

## Coordinates
World units match Manim: frame height 8, width 8·aspect (14.22 at 16:9), origin at the centre, y up.
The 2.5D camera (`s.camera`) transforms every layer by its parallax. Vector layers (`ManimLayer`) are
re-rasterized through the camera, so zooms stay crisp. Raster layers are resampled with mipmaps.

## Shader layers
```glsl
#include "common/color.glsl"
in vec2 v_uv;            // 0..1 over the frame
in vec2 v_pos;           // world units, camera applied
out vec4 frag;           // LINEAR rgb, STRAIGHT alpha
uniform float u_time;    // absolute seconds (also u_local = t - scene start)
uniform float u_glow;    // any u_* kwarg you pass
void main() { frag = vec4(srgb2lin(vec3(v_uv, 0.5)), 1.0); }
```
Automatic uniforms: `u_time u_local u_res u_frame u_frame_index u_seed u_view u_view_inv`. Search path:
`videos/<v>/shaders/` first, then `aion/shaders/`. `#include "…"` works. Pass `scale_res=0.5` to render
expensive shaders at half resolution. Pass `animated=False` if the output depends only on uniforms, so it's
cached while they hold still. Uniform names you pass that the shader doesn't use print a warning once.

## Static detection (why holds are free)
Each layer reports `changes(t0, t1)` from its Tracks and events. If nothing in the comp changed since the
last frame, the previous frame is reused without any GL work. Keep this cheap: avoid always-on
`wave()`/grain on big layers unless the shot needs it.

## Raw arrays from other libraries
skia-python, pyvista (`plotter.screenshot(return_img=True, transparent_background=True)`), matplotlib:
render to an RGBA uint8 array, then `ArrayLayer(rgba, height=…)`. For per-frame output, cache it by `t` in your
own function and keep it pure in `t`.
