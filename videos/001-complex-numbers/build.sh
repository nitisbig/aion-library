#!/usr/bin/env bash
# Render every scene of 001-complex-numbers, join them, and mux the narration.
#   ./videos/001-complex-numbers/build.sh        # 480p15 preview (-ql)
#   ./videos/001-complex-numbers/build.sh h      # 1080p60 final  (-qh)
# Run from anywhere; renders happen at the repo root so manim.cfg applies.
set -euo pipefail
Q="${1:-l}"
VID="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$VID/../.." && pwd)"
cd "$ROOT"

case "$Q" in
  l) RES=480p15 ;;  m) RES=720p30 ;;  h) RES=1080p60 ;;  k) RES=2160p60 ;;
  *) echo "quality must be l|m|h|k" >&2; exit 1 ;;
esac

SCENES=(
  "scene_01_intro Scene01Intro"
  "scene_02_puzzle Scene02Puzzle"
  "scene_03_quarter_turn Scene03QuarterTurn"
  "scene_04_plane Scene04Plane"
  "scene_05_outro Scene05Outro"
)

mkdir -p "$VID/out"
LIST="$VID/out/concat_$RES.txt"
: > "$LIST"
for s in "${SCENES[@]}"; do
  set -- $s
  uv run manim "-q$Q" "$VID/scenes/$1.py" "$2"
  echo "file '$ROOT/media/videos/$1/$RES/$2.mp4'" >> "$LIST"
done

OUT="$VID/out/final_$RES.mp4"
[ "$Q" = h ] && OUT="$VID/out/final.mp4"
# Video: stream copy. Audio: the original narration, padded with silence
# (the approved 2 s tail) and cut to the video length.
ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -i "$VID/assets/audio.mp3" \
  -map 0:v -map 1:a -c:v copy -af apad -c:a aac -b:a 320k -shortest "$OUT"

echo "── durations (video / audio) ──"
ffprobe -v error -show_entries stream=codec_type,duration -of compact=p=0 "$OUT"
echo "✔ $OUT"
