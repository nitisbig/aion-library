# Effects, camera, finishing

Effects run on the GPU in linear light. Attach them to a **layer** (`fx=[…]` on any layer or
`s.manim(fx=[Glow(C.x)])`) or to the **frame** (`s.fx(...)`, applied after compositing, in order).
Every parameter accepts a Track, e.g. `Blur(radius=key(T.focus, 6, 0))`.

| effect | what it does | added cost per changed frame @1080p (R4) |
|---|---|---|
| `Bloom(strength, threshold, knee, radius, tint)` | highlights bleed light, dual-Kawase pyramid | +35 ms |
| `Glow(color, strength, radius)` | coloured halo from a layer's own shapes | +51 ms |
| `Blur(radius)` | Kawase blur; 0 = off (focus pulls) | +35 ms (r=4) |
| `Grade(exposure, contrast, saturation, lift, gamma, gain, tint, lut, lut_mix)` | primary grade + `.cube` LUT | +10 ms |
| `Lens(vignette, ca, grain, grain_size, roundness)` | vignette + chromatic aberration + grain, one pass | +14 ms |
| `Vignette(v)`, `Grain(g)`, `ChromaticAberration(c)` | shortcuts for `Lens` | +14 ms |
| `ZoomBlur(amount, center, taps)` | radial whoosh; animate `amount` with `pulse` | +17 ms |

Costs were measured as frame-level effects over a 37 ms baseline frame (gradient + readback). They apply only to
frames that change; hold frames are reused for free unless something animates every frame (grain, `wave`). Combine Vignette/Grain/CA into one `Lens(...)`.

Recommended finishing stack for the channel look:
```python
s.fx(Bloom(C.bloom, threshold=0.8), Lens(vignette=C.vignette, grain=C.grain))   # one Lens pass, not two
```
Grain is deterministic but **changes every frame**, so with `grain > 0` hold frames are no longer free: each one
re-composites and re-runs the frame fx (layer rasters, e.g. Manim, are still reused). For long holds on a slow
machine, drop grain, or keep it at 0 and add it in the final pass only.

## Camera (`s.camera`, 2.5D)
`push(at, zoom, dur, ease="easy_ease")`, `pan(at, to=(x, y))`, `rotate(at, angle)`,
`frame(at, center, zoom)` (pan + zoom together), `shake(at, amp, dur, freq, seed)`.
Moves chain: each starts from where the previous one ended. Layer `parallax` scales how much a layer follows
(0 = HUD, 0.3 = distant backdrop, 1 = world).

## Transitions (today)
There is no `transition_out` helper yet. Build transitions from tracks:
- crossfade: overlap two layers with `opacity=fade(T.cut, out=…)`;
- whoosh: `ZoomBlur(amount=pulse(T.cut, 0.25, dur=0.5))` + `camera.push(T.cut, zoom=1.15, dur=0.5)`;
- focus change: `Blur(radius=key(T.cut, 0, 8, dur=0.4))` on the outgoing layer.
Prefer continuity (transform objects across the cut) over effects. See storyboard principles in CLAUDE.md.

## Not implemented yet
Motion blur, depth of field and the `transition_out` / light-leak / glitch presets. Use the recipes above.
