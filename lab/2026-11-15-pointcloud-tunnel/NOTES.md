# Point-Cloud Tunnel: 20 s walkthrough, 16:9 (exploration)

A dark, LiDAR-style tunnel made only of points: fragmented cave/forest walls, a bright path on the floor,
trunks lining it, floating dust with motion streaks, thin perspective rails. It recreates the four portrait
reference frames as one continuous 16:9 camera move.

```bash
uv run python lab/2026-11-15-pointcloud-tunnel/tunnel.py                                   # Taichi bake (~85 s, cached in out/)
uv run python lab/2026-11-15-pointcloud-tunnel/render.py still --height 540               # out/contact.png (6 shots)
uv run python lab/2026-11-15-pointcloud-tunnel/render.py still --t 11 --height 1080 --tag _1080
uv run python lab/2026-11-15-pointcloud-tunnel/render.py video --height 540 --fps 30      # preview (~6 min)
uv run python lab/2026-11-15-pointcloud-tunnel/render.py video --height 1080 --fps 30     # ~10 min
```

## Shots (one continuous move)
| t (s) | What | Ref |
|---|---|---|
| 0–3.5 | LiDAR reveal: a sphere grows from the camera and paints the tunnel in, with a thin bright front | |
| 3.5–9 | walk down the lit path, dust streaking past, scan ring sweeping down the walls | 1 |
| 9–13.5 | camera yaws 48° right while walking: path on the left, trunks lining it | 2 |
| 13.5–16.5 | turn back, drop toward the floor, speed up; rails stream underneath | 3 |
| 16.5–20 | tunnel ahead corkscrews into a vortex, camera rolls −75° and dives in, fade out | 4 |

## Pipeline
| File | Role |
|---|---|
| `tunnel.py` | **Taichi** kernel (CPU, 2 threads): 1.5M seeded samples → ~1.03M kept. Wall: `r = R0(s)(1 + 0.5·fbm₁ + 0.16·fbm₂)` around a wandering centerline; bottom arc flattened into a floor with a smooth bright path; foliage clumps on the upper walls (inward depth, green tint); a density fbm cuts holes; ~37 trunks with root flare, lean and branches. Dust (45k) and floor rails (23 lanes) in numpy. Inputs are numpy-seeded uniforms, so the result is deterministic |
| `shaders/common.glsl` | Centerline twin (keep in sync with `tunnel.py`), the corkscrew twist `angle = k·max(s − s₀, 0)²` applied in the vertex shader, a real near plane so GL clips lines, a moving point light, fog, the reveal sphere |
| `points.vert/.frag` | One `GL_POINTS` draw, additive, no sort. Energy = area·\|n·v\|·f_y²/z² spread over the sprite and capped, so brightness doesn't depend on density or resolution. Hard square dots (the LiDAR look); soft gaussian only for large sparkles and dust |
| `lines.vert` | `GL_LINES`: rails with dashed scan pulses; dust streaks (tail = p + camera velocity × shutter → radial streaks for free) |
| `render.py` | Timeline (speed profile integrated to s(t), yaw, roll, light, twist, fade) + dual-Kawase bloom → composite (copied from the point-cloud-forest lab: ACES, vignette, luminance-gated grain, so black stays #000) |

## What worked
- Additive energy-normalized points look right immediately; same lesson as the forest lab.
- Motion streaks as 2-vertex lines offset by camera velocity: the radial "warp" lines in refs 1/3/4 for almost nothing.
- The vertex-shader corkscrew twist gives the ref-4 vortex with no extra geometry.

## What didn't (and fixes)
- First pass was blown out: exposure 1.6 + light 4.5 + bloom threshold 0.35. Now exposure 1.0, light 1.5, threshold 0.7.
- **Chromatic aberration on 1-px dots** splits them into magenta/green fringes. CA is now ~0 except a tiny amount in the dive.
- Streaking all 45k dust looked like hyperspace. Only the larger ~45% streak now.
- Still open: the right side of the 11 s side-look is sparse (a density hole). Wall density could be raised there.
  Rails are faint; refs 1/3 have more prominent floor lines.

## Numbers
~1.03M points + 5.3k rail segments + 20k streaks. R4 iGPU: ~0.6 s/frame @540p, ~1 s/frame @1080p (600-frame 1080p30 render: 592 s; output 155 MB at crf 17)
(readback + x264 included). Bake: 85 s, 340 MB peak RSS.
