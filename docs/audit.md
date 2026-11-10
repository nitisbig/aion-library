# Audit

`uv run aion audit <video>` runs the source and timing checks. Add `--design` (per-beat layout) and
`--delivery` (the final mp4). `--file path.mp4` audits any file. Findings: ✘ error, ⚠ warn, · info.

| check | catches |
|---|---|
| source | raw hex colors (use `C.*`), `add_updater`, `self.play`/`self.wait`, `at=<number>`, unseeded `np.random` |
| timing | scenes that don't tile the audio, gaps or overlaps, soft cuts with no silence, scenes < 2 s |
| design | Text smaller than ~26 px at 1080p, mobjects crossing the safe margin, > 3 animations at once (checked 0.8 s after each beat) |
| delivery | pix_fmt ≠ yuv420p, missing bt709 tag, video ≠ audio duration (> 1 frame), loudness far from −14 LUFS, true peak > −1 dBTP, black spans ≥ 0.5 s, no motion for ≥ 4 s (info) |

The narration master is −16 LUFS. YouTube normalises to −14, so a ±2 LU difference is reported as info only.
`--design` builds the scenes and evaluates the score, so it takes a few seconds per scene.
