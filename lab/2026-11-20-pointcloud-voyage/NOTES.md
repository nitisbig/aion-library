# Point-cloud voyage: video 012's opening shot as a point cloud (exploration)

The first 19.1 s of video 012 (Dido's galley reaching Africa), rebuilt in the LiDAR / point-cloud style of
`lab/2026-11-15-pointcloud-tunnel`, but in colour: a teal sea with sun glitter, a dusk sky dome, violet coast
ridges, a hilltop city whose windows light up, and the striped galley. Synced to the real narration.

```bash
uv run python lab/2026-11-20-pointcloud-voyage/scene.py                                    # cloud (~4 s, cached in out/)
uv run python lab/2026-11-20-pointcloud-voyage/render.py still --t 1 5.5 9.5 17 --height 540
uv run python lab/2026-11-20-pointcloud-voyage/render.py video --height 1080 --fps 30       # ~5 min, narration muxed
```

## Shot (one continuous move, beats from 012's beats.py)
| t (s) | What |
|---|---|
| 0–3.6 | a scan sphere spreads from the galley and paints the evening sea in |
| 3.6–9.3 | rowing toward Africa; the camera swings along the port side, the sun behind the striped sail |
| 9.3–12 | landfall (`king`): oars shipped, sail brailed up, the camera cranes up behind the ship toward the coast |
| 12–19.1 | at anchor: city windows come on, the sun sets behind the hills, stars brighten; fades for the workbench |

## Pipeline
| File | Role |
|---|---|
| `scene.py` | numpy, seeded: 1.43M points, rows of pos/nrm/col/attr(kind, area, p1, p2), sorted by kind. Sea (dense band along the voyage + sparse field), sky dome (380k, colour by elevation and sun angle), stars, sun disc and halo, 12 cloud banks lit gold underneath, three coast ridges, 14 city blocks + window points, the galley in its local frame (hull with plank lines, shields, deck, prow and scorpion stern as tubes, mast, yard, rigging, Dido, sail, 20 oars, flag), 46k foam particles, 6 gulls |
| `shaders/common.glsl` | waves (twin of `scene.wave_h`), the ship's path `shipAt(t)` (ease-out to anchor) and roll/pitch frame, fog toward the evening haze, the scan reveal |
| `shaders/points.vert` | per kind: sea height and normal from the wave field, fresnel + sun glint; sail furl (squeeze to the yard) and billow; oars rowing in phase, then shipped; flag; foam emitted along the hull at `t − age` so the wake trails behind the ship; gulls circling the mast; windows turning on |
| `render.py` | timeline + keyed camera relative to the ship. **Depth pre-pass**: land writes depth with fat sprites, the sky draws with the depth test, everything else additive with no depth. Then dual-Kawase bloom and the tunnel lab's composite (ACES, split tone, vignette, gated grain) |

## Floating panels (overlays.py, kind 7)
Synced to the narration: `814 BC` (0.9–4.2 s), a drawn queen medallion + `DIDO` (queen, 4.8 s),
a drawn king medallion + `THE KING` (king, 9.9 s), the joke *"as much ground as she could surround"*
(13.9 s), a drawn ox-hide medallion (stitched rim, dashed spiral hinting at the strips) + `ONE OX HIDE` (16.1 s); all disperse at 18.3 s, before the strips.
- The queen and king are drawn as coin-like busts in `figures.py`: gold beaded rim, crowns with jewels,
  Tyrian-purple gown, crimson robe with ermine and a sceptre. They read much better as points than photos do,
  because flat saturated shapes survive the sampling. Preview the drawings with `python figures.py`.
- Images are sampled pixel-for-pixel into points (190 rows) with a gold point frame. Text is rasterised from Latin
  Modern (small caps / italic) with PIL and its mask sampled.
- Each panel is placed in screen space (NDC x, y, depth) and converted to world space every frame through the
  camera basis, so it floats in the air while the camera moves. It has a slight yaw and bob.
- Points fly in from random directions with a per-point stagger and scatter back out. They write depth in the pre-pass
  only when mostly assembled, so a half-formed panel doesn't punch holes in the sky.
- Layout lesson: letter-spaced captions were wider than the pictures and ran together ("DIDOTHE LOCAL KING"). The
  tracking is now per glyph (+18 px at 150 px), and the panels sit at x = −0.72, −0.24, 0.62.

## What worked
- Energy-normalised additive points (area·fy²/z²) again: density doesn't change brightness.
- The depth pre-pass is the key trick for an outdoor scene: without it the additive sky shines through the hills and
  the city disappears; with it the coast reads as a solid silhouette against the dusk.
- Sea glint from the analytic wave normal gives a real sun column on the water for free.

## What didn't (and fixes)
- First pass blew out (ship rim ×2.6, sun cap 4, glint ×60). Now rim 1.1, sun cap 1.2, glint 9, ship gain 0.55.
- Camera too close: the galley filled the frame. Offsets doubled.
- A sparse sky (70k) looks like confetti at any sprite size; 380k small points read as a gradient.
- The sun sat behind the far ridge; raised to elevation ≈ 5.4° and sinks 14 m over the shot.
- Still open: the sky is grainy up close; the hull reads as wireframe-ish; the gulls are tiny.

## Numbers
Density pass: `scene.D = 2` scales every count (areas by 1/D, so brightness holds). The sky gets ×1.6 on top
(1.2M points) and the voyage sea band ×1.5, so the dusk sky reads as a gradient, not confetti. Point size
`u_base` dropped 1.6→1.3 for a finer grain, medallions are sampled at 300 rows and text at 90 %. Total 3.45M points:
≈ 2.2 s/frame at 1080p on the R4, cloud build 10 s / 0.6 GB RAM.

1.43M points, R4 iGPU ≈ 0.2 s/frame @540p. Merge path if liked: render this at 1920×1080 as `assets/voyage_pc.mp4`
and play it as a `VideoLayer` (or bake frames) in place of the skia `voyage()` FramesLayer in `s01_dido_coast.py`.
