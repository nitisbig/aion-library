# Fourier's portrait drawn by circles (cold open for video 003)

**Tried:** Boilly's engraving (public domain, `videos/003-fourier-series/assets/images/fourier_portrait.jpg`) →
brightness contours of a blurred copy (matplotlib `contour`) → greedy nearest-neighbour tour into one line
→ FFT. `path_proto.py` compares two contour settings (`proto_ab.png`); `recon.py` compares 301 / 601 / 901
circles (`recon.png`).

**Worked:** detailed contours for the head (σ 1.8 px, levels 0.3/0.5/0.68) plus sparse ones for the coat
(σ 3.5, levels 0.3/0.6) make the face read as a face while the coat stays calm. 601 circles is the sweet spot;
301 loses the eyes, 901 adds little.

**Didn't:** the jumps between contours stay visible as straight strokes (most of all one long line along the
bottom of the coat). They read as "one-line drawing" style, but a 2-opt pass on the tour would shorten them.

**Promoted:** `aion.drawings.portrait_line()` / `tour()`; `EpicyclePlate` state `rim_count` (rims for the
first n circles only). Used by `videos/003-fourier-series/scenes/scene_00_preview.py`.

Render: `uv run python videos/003-fourier-series/render.py --fps 15 --quality hq --scenes 0`
