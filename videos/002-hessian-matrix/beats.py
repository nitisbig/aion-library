"""Timed beat sheet for 002, resolved against the real SRT.

Every beat is a cue key that is looked up with `Cue.at()`. Nothing is typed in
by hand. Run it to regenerate the timed half of storyboard.md (and to prove
that every key the scenes will use exists in the SRT):

    uv run python videos/002-hessian-matrix/beats.py > /tmp/timed.md

Scene cuts are frame boundaries (60 fps) at the middle of a real silence found
with `ffmpeg silencedetect` (the aligner leaves no gaps between words, so the
SRT alone cannot show pauses).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from aion.sync import Cue

HERE = Path(__file__).parent
FPS = 60
LEAD = 0.15
AUDIO_END = 604.560          # ffprobe

cue = Cue.load(HERE / "assets" / "cue-per-word.srt")

# Real silences (ffmpeg silencedetect, n=-35dB, d=0.12) used as cut points.
CUT_SILENCES = [
    (27.98, 28.36), (55.14, 55.79), (79.88, 80.16), (107.30, 107.60),
    (132.07, 132.67), (158.60, 158.89), (178.60, 178.96), (199.89, 200.14),
    (226.55, 226.89), (257.62, 258.06), (286.69, 287.03), (303.53, 303.88),
    (325.48, 325.96), (354.06, 354.49), (374.66, 375.14), (392.78, 393.16),
    (412.90, 413.34), (438.99, 439.55), (462.93, 463.33), (480.15, 480.68),
    (496.73, 496.90), (520.71, 521.11), (542.02, 542.48), (559.27, 559.85),
    (594.75, 595.13),
]
CUT_FRAMES = [0] + [round((a + b) / 2 * FPS) for a, b in CUT_SILENCES] + \
             [math.floor(AUDIO_END * FPS)]   # ends on the audio (user decision)

# Bending of the puzzle surface in direction θ: uᵀHu = 2 + 3 sin 2θ.
def theta_for(bend: float, branch: int = 0) -> float:
    s = math.degrees(math.asin((bend - 2) / 3)) / 2
    return s if branch == 0 else 90 - s


THETA = {k: theta_for(v) for k, v in {"3": 3, "4": 4, "5": 5}.items()}
THETA_ZERO = (180 + math.degrees(math.asin(2 / 3))) / 2       # 2θ = 180° + asin(2/3)

# Gradient descent on f = x² + 10y² from (3, 1), step 0.09.
def gd_steps(eps: float = 0.05) -> int:
    x, y, n = 3.0, 1.0, 0
    while math.hypot(x, y) > eps:
        x, y, n = x - 0.09 * 2 * x, y - 0.09 * 20 * y, n + 1
    return n


GD_N = gd_steps()

# (shot, cue key, after (abs s or None = scene start), what happens, anim note)
B = tuple
SCENES: list[dict] = [
    dict(slug="01_fog", cls="Scene01Fog", part="INTRO", title="The foggy hill",
         engine="moderngl `SurfacePlate` + Manim projected overlay + skia glow",
         beats=[
        ("I-1", "@0", None, "Black fades up into a fog-filled slate landscape seen from a low camera. Height fog drifts (2-octave noise). The yellow **walker** fades in with a soft skia glow. A slow camera dolly-in starts and keeps running under the whole scene", "fade 0.00, rt 1.2 · dolly `linear` to the end"),
        ("I-1", "thick fog", None, "Fog density swells slightly, so the far ground is lost", "rt 1.0 `smooth`"),
        ("I-2", "perfectly flat", None, "The translucent **tangent disc** opens under the walker", "`GrowFromCenter`, rt 0.7"),
        ("I-2", "no slope", None, "Four short yellow probe arrows (N, E, S, W) grow from the walker, then shrink to nothing one after another. All four slopes are zero", "`LaggedStart` lag 0.15, rt 1.4"),
        ("I-2", "where are you", None, "A faint “?” (40% opacity) settles above the walker", "fade + shift, rt 0.6"),
        ("I-3", "top of the hill", None, "Fog thins (0.6 → 0.35). The ground under the disc **morphs into a dome** (H uniform tween). Disc and walker stay perfectly still", "H tween rt 0.9 `smooth`"),
        ("I-3", "bottom of a valley", None, "The ground morphs dome → **bowl**", "rt 0.9 `smooth`"),
        ("I-3", "mountain pass", None, "bowl → **saddle**", "rt 0.9 `smooth`"),
        ("I-3", "rises ahead", None, "The forward slice through the walker glows blue (it curves up)", "rt 0.6"),
        ("I-3", "falls away", None, "The sideways slice glows orange (it curves down)", "rt 0.6"),
        ("I-4", "cant tell you", None, "The camera pushes in until only disc + walker fill the frame. The slices fade. Underneath, dome / bowl / saddle cross-dissolve and are indistinguishable at this scale", "push rt 1.4 `smooth`"),
        ("I-4", "zero", 22.0, "A small yellow `slope = 0` readout fades in beside the disc", "rt 0.5"),
        ("I-5", "how the ground bends", None, "Pull back to the saddle. Contour lines draw across it (`u_contour` 0 → 1) and the **bend tint** washes in, blue one way and orange the other", "pull rt 1.2, contours rt 1.2 (both end by 28.0)"),
    ]),
    dict(slug="02_puzzle", cls="Scene02Puzzle", part="INTRO", title="The puzzle and the promise",
         engine="moderngl + Manim + skia title plate",
         beats=[
        ("I-6", "heres a puzzle", None, "A fog bank wipes across and clears to the **puzzle surface** `x² + 3xy + y²`. The bend tint stays off, so it looks innocent", "fog wipe rt 1.0"),
        ("I-6", "east", 29.8, "A red x-slice plane sweeps in through the center. Its cut curve glows red, and a **blue smile gauge** pops beside it", "plane rt 0.8, gauge rt 0.5"),
        ("I-6", "north", 32.6, "A green y-slice plane does the same, with a second blue smile", "plane rt 0.8, gauge rt 0.5"),
        ("I-7", "middle", 34.8, "Both slices dim to 30%. The walker glows at the center", "rt 0.4"),
        ("I-7", "not a valley", None, "The walker turns into a ball and **rolls off along the northwest diagonal** (path from steepest descent on f), vanishing into the fog. Left unexplained on purpose", "roll rt 2.2 `rush_into`"),
        ("I-8", "small grid", None, "The surface recedes and dims to 20%. Four empty rounded cells (`HessianGrid`) assemble in the center", "`LaggedStart`, rt 0.6"),
        ("I-8", "four numbers", None, "The four cells pulse once, left to right, top to bottom", "chained after the assembly (≈ 40.3), lag 0.12, rt 0.8"),
        ("I-8", "hessian matrix", None, "The cells fill with `f_xx` (red), `f_xy` / `f_yx` (violet), `f_yy` (green). **“The Hessian Matrix”** sets beneath in skia typography with a soft glow", "fill rt 0.8, title rt 1.0"),
        ("I-9a", "build it from nothing", None, "Trailer shot 1: the grid empties and refills cell by cell", "cross-dissolve rt 0.5"),
        ("I-9b", "what each number means", None, "Trailer shot 2: the direction dial sweeps while its bending curve `2 + 3 sin 2θ` traces beside it", "cross-dissolve rt 0.5"),
        ("I-9c", "millions of dimensions", None, "Trailer shot 3: a gradient-descent zigzag on an elliptical contour map, then one Newton arc to the center", "cross-dissolve rt 0.5"),
        ("I-10", "idea of a slope", None, "Everything collapses to **one yellow tangent line** touching a short arc of curve, on a clean frame. That is the hand-off to Ch1", "rt 1.0 `smooth`"),
    ]),
    dict(slug="03_slope", cls="Scene03Slope", part="CH1", title="Slope, and the slope of the slope",
         engine="Manim", beats=[
        ("1-1", "single curve", None, "Axes (−3..3) fade up under the tangent line from the intro", "rt 0.8"),
        ("1-1", "why equals x squared", None, "The parabola draws through the tangent point; `y = x²` lands top-left. (The SRT writes “Why” for “Y”.)", "`Create` rt 1.2, label `Write` rt 0.8"),
        ("1-2", "every point", None, "The tangent line starts to **ride the curve** (ValueTracker `x₀`)", "rt 1.2"),
        ("1-2", "first derivative", None, "Live readout `slope = f′(x₀) = 2x₀` in yellow", "rt 0.6"),
        ("1-3", "left", 63.0, "Tangent slides to x₀ = −1.5; readout −3", "rt 0.9 `smooth`"),
        ("1-3", "negative", None, "The readout's minus sign glows", "`Indicate` rt 0.5"),
        ("1-3", "right", 65.0, "Tangent slides to x₀ = +1.5; readout +3", "rt 1.0"),
        ("1-3", "bottom", 67.0, "Tangent settles at the vertex", "rt 0.8"),
        ("1-3", "zero", 67.5, "Readout lands on **0**, the line lies flat", "flash rt 0.4"),
        ("1-4", "watch the slope itself", None, "The frame splits: the parabola rises to the top half, new axes labeled “slope” draw in the bottom half", "rt 1.0"),
        ("1-4", "move to the right", None, "The tangent sweeps x₀ = −2 → 2 again and a yellow dot **traces the slope graph `2x`**, a straight rising line", "rt 3.0 `linear` sweep"),
        ("1-5", "rate", 74.0, "A rise/run triangle on the slope line: run 1, rise 2", "rt 0.8"),
        ("1-5", "second derivative", 76.0, "`f″(x) =` writes under the slope graph", "`Write` rt 0.8"),
        ("1-5", "two everywhere", None, "`= 2` lands; the triangle slides along the line and stays the same size", "rt 0.5, then slide rt 0.6 (ends 80.0)"),
    ]),
    dict(slug="04_smile", cls="Scene04Smile", part="CH1", title="Smile, frown, and a flat spot",
         engine="Manim", beats=[
        ("1-6", "positive second derivative", None, "`f″ = 2` tints blue", "rt 0.5"),
        ("1-6", "slope is rising", None, "The slope line glows yellow along its length", "rt 0.8"),
        ("1-6", "smile", 85.0, "The **BendGauge** is born: a blue smile beside `f″ = 2`; the parabola glows blue for a beat", "`GrowFromCenter` rt 0.6"),
        ("1-7", "flip it over", None, "A sign tracker 1 → −1 flips the parabola to `−x²` (no cut). The slope line tilts to `−2x`", "rt 1.2 `smooth`"),
        ("1-7", "minus two", None, "`f″ = −2` in orange", "rt 0.5"),
        ("1-7", "frown", 91.0, "The gauge bends through flat into an **orange frown**", "rt 0.7"),
        ("1-8", "measures bending", None, "The gauge pulses; a small `f″ = bending` tag", "rt 0.6"),
        ("1-8", "flat spot", None, "The bottom panel slides away. A walker dot sits at the vertex on a flat yellow tangent", "rt 0.8"),
        ("1-8", "cosine of x", None, "The curve morphs into `cos x` on [−2π, 2π]; the walker rides to x = 0", "`Transform` rt 1.0"),
        ("1-8", "its flat", 100.0, "The flat tangent at x = 0 re-draws", "rt 0.5"),
        ("1-8", "top or bottom", None, "A “?” at 40% over the dot", "rt 0.5"),
        ("1-9", "minus one", 103.0, "The gauge shows a −1 frown", "rt 0.6"),
        ("1-9", "bends down", 105.0, "The curve near 0 tints orange", "rt 0.5"),
        ("1-9", "peak", 106.5, "The “?” becomes an orange ring around the dot", "rt 0.5"),
    ]),
    dict(slug="05_test", cls="Scene05Test", part="CH1", title="Every curve is a parabola up close",
         engine="Manim (MovingCamera) + skia card", beats=[
        ("1-10", "zooming close", None, "MovingCamera zooms to x = 0 (frame width 14 → 3). (SRT says “Zooming close”)", "rt 1.8 `smooth`"),
        ("1-10", "parabola", 107.5, "A dashed orange parabola `1 − x²/2` draws and **hugs the cosine**", "`Create` rt 1.0"),
        ("1-10", "one", 113.0, "`cos x ≈ 1` writes top-left", "rt 0.25"),
        ("1-10", "minus x squared over two", None, "`− x²/2` appends in orange", "rt 0.8"),
        ("1-10", "which way that parabola opens", None, "The camera eases back out. The dashed parabola's opening edges glow; a ghost blue `+x²/2` flickers once to show the other way", "rt 1.2"),
        ("1-11", "second derivative test", None, "A two-row skia card slides up from the bottom", "rt 0.8"),
        ("1-11", "bending up", None, "Row 1: mini smile icon", "rt 0.4"),
        ("1-11", "valley", 124.0, "Row 1 label **valley** (blue)", "rt 0.4"),
        ("1-11", "bending down", None, "Row 2: mini frown icon", "rt 0.4"),
        ("1-11", "peak", 126.0, "Row 2 label **peak** (orange)", "rt 0.4"),
        ("1-12", "bending is zero", None, "Row 3 appears; the main curve becomes `x³`", "rt 0.8"),
        ("1-12", "x cubed", None, "Walker at 0 on the flat tangent; the gauge goes to a **flat grey line**", "rt 0.6"),
        ("1-12", "cant tell", None, "Grey “?” in row 3", "rt 0.5"),
    ]),
    dict(slug="06_slices", cls="Scene06Slices", part="CH2", title="From a curve to a landscape",
         engine="Manim → moderngl (shared camera) + projected labels", beats=[
        ("1-13", "step off the line", None, "The card fades. The 2D axes **tilt back in perspective** and become the red x-axis of a 3D floor. The last Manim frame is pixel-matched to the first SurfacePlate frame", "tilt rt 1.6 `smooth`"),
        ("2-1", "two inputs", None, "A green y-axis grows across the floor; labels x, y", "rt 0.8"),
        ("2-1", "height", 138.0, "A field of thin vertical pins rises from the floor grid (the two-hill landscape's heights)", "`LaggedStart` rt 1.6"),
        ("2-1", "landscape", 142.0, "The pins **skin into a surface**", "crossfade rt 1.0"),
        ("2-2", "slice it", None, "A translucent red plane (y = const) slides in", "rt 0.8"),
        ("2-2", "hold y fixed", None, "`y = const` tag pinned to the plane via `project()`", "rt 0.5"),
        ("2-2", "x direction", None, "The cut curve glows red", "rt 0.7"),
        ("2-2", "ordinary curve", None, "The camera swings side-on so the cut reads as a plain 2D curve", "orbit rt 1.4"),
        ("2-2", "with respect to x", None, "A yellow tangent sits on the red curve; label `∂f/∂x` (red)", "rt 0.7"),
        ("2-3", "cut along y", None, "Camera swings back; a green plane, its cut curve, tangent and `∂f/∂y` (green)", "rt 1.2"),
    ]),
    dict(slug="07_gradient", cls="Scene07Gradient", part="CH2", title="The gradient arrow",
         engine="moderngl + Manim (projected arrows)", beats=[
        ("2-4", "two slopes together", None, "The two tangent slopes drop to the floor as red and green component arrows", "rt 1.0"),
        ("2-4", "arrow on the floor", None, "They add tip-to-tail into the **yellow gradient arrow**", "rt 0.8"),
        ("2-4", "gradient", 162.0, "Label `∇f` (yellow)", "rt 0.5"),
        ("2-4", "straight uphill", None, "A faint dashed line from the arrow runs up the surface", "rt 0.7"),
        ("2-4", "how steep", None, "A bracket along the arrow's length", "rt 0.5"),
        ("2-5", "walk around", None, "Camera rises to top-down while the surface shades into a **contour map**. The walker moves on a path; its arrow updates live", "camera rt 2.0, walk to scene end"),
        ("2-5", "steep side", None, "Walker crosses the steep flank: the arrow is long", "—"),
        ("2-5", "near the top", None, "Walker climbs: the arrow shrinks", "—"),
        ("2-5", "vanishes", None, "A grid of true-∇f arrows fades in staggered; near the peaks they vanish", "`LaggedStart` rt 1.2"),
        ("2-6", "critical points", None, "White pulse rings at the three critical points (two peaks and the saddle between, found numerically)", "rt 0.8"),
    ]),
    dict(slug="08_three", cls="Scene08Three", part="CH2", title="Bowl, dome, saddle",
         engine="moderngl triptych + Manim", beats=[
        ("2-7", "three surfaces", None, "The map dissolves into a **triptych**: three viewports, one GL pass, slowly co-rotating", "rt 1.0"),
        ("2-7", "bowl", 180.0, "Left lands: bowl", "rise rt 0.6"),
        ("2-7", "dome", 181.0, "Middle lands: dome", "rt 0.6"),
        ("2-7", "saddle", 182.0, "Right lands: saddle", "rt 0.6"),
        ("2-8", "center of each one", None, "Tangent discs and walkers appear at all three centers", "`LaggedStart` rt 0.8"),
        ("2-8", "gradient is zero", None, "`∇f = 0` under each", "rt 0.5"),
        ("2-8", "valley", 188.0, "**valley** (blue) under the bowl", "rt 0.4"),
        ("2-8", "peak", 189.5, "**peak** (orange) under the dome", "rt 0.4"),
        ("2-8", "neither", None, "**neither** (blue/orange) under the saddle", "rt 0.4"),
        ("2-9", "low one way", None, "The saddle grows to fill the frame. Blue smile gauge on its x-slice", "zoom rt 1.2, gauge rt 0.5"),
        ("2-9", "high the other", None, "Orange frown gauge on its y-slice", "rt 0.5"),
        ("2-10", "second derivatives again", None, "The two gauges lift off the surface and hover", "rt 0.8"),
        ("2-10", "more than one", None, "A dim “how many?” with a row of small dots", "rt 0.6"),
    ]),
    dict(slug="09_four", cls="Scene09Four", part="CH3", title="Four second derivatives",
         engine="Manim + moderngl inset", beats=[
        ("3-1", "two slopes", None, "Clean 2D frame. Row labels appear: `∂f/∂x`", "rt 0.6"),
        ("3-1", "slope in x", None, "`∂f/∂x` (red) pulses", "rt 0.4"),
        ("3-1", "slope in y", None, "`∂f/∂y` (green) appears", "rt 0.5"),
        ("3-1", "two ways", None, "Column headers slide in", "rt 0.6"),
        ("3-1", "move in x", 206.8, "Header “move in x”", "rt 0.4"),
        ("3-1", "move in y", 207.5, "Header “move in y”", "rt 0.4"),
        ("3-1", "four second derivatives", None, "The four empty cells light up in a stagger", "lag 0.12, rt 0.8"),
        ("3-2", "as you move in x", 213.6, "Top-left cell highlights", "rt 0.4"),
        ("3-2", "bending of the x slice", None, "Inset (moderngl): the surface with a red slice and a blue smile gauge, the same picture as Ch1", "inset rt 0.8"),
        ("3-2", "f x x", None, "Top-left fills with red `f_xx`", "rt 0.6"),
        ("3-3", "y slope changes", None, "Bottom-right cell highlights", "rt 0.4"),
        ("3-3", "y slice", None, "Inset swaps to a green slice", "rt 0.6"),
        ("3-3", "f y y", None, "Bottom-right fills with green `f_yy`", "rt 0.6"),
    ]),
    dict(slug="10_twist", cls="Scene10Twist", part="CH3", title="The twist",
         engine="moderngl (`xy` surface, GL line rulings) + Manim", beats=[
        ("3-4", "other two", None, "The two empty off-diagonal cells glow faint violet", "rt 0.6"),
        ("3-4", "picture yourself", None, "Full-frame moderngl: the `xy` surface; the grid shrinks to the top-right corner", "rt 1.0"),
        ("3-4", "facing east", None, "Walker at the origin with a red “facing east” tangent arrow", "rt 0.6"),
        ("3-4", "step to the side", None, "The walker steps north (y: 0 → 0.6)", "rt 1.0 `smooth`"),
        ("3-4", "steeper or flatter", None, "The east arrow **tilts upward**; a ghost of the old flat arrow stays", "rt 0.8"),
        ("3-5", "f x y", None, "Top-right cell fills violet `f_xy`", "rt 0.6"),
        ("3-5", "twist", 239.0, "A small violet **twist ribbon** icon (the gauge for twist)", "rt 0.6"),
        ("3-6", "z equals x times y", None, "`z = xy` writes", "rt 0.8"),
        ("3-6", "perfectly", None, "The surface fades to its **straight-line rulings**: every east-facing line is exactly straight with slope y", "rt 1.0"),
        ("3-6", "xaxis", None, "The ruling on y = 0 highlights: flat", "rt 0.5"),
        ("3-6", "step north", None, "Rulings with y > 0 highlight, tilted up", "rt 0.6"),
        ("3-6", "step south", None, "Rulings with y < 0 highlight, tilted down", "rt 0.6"),
        ("3-7", "bending in x is zero", None, "Readout 1: flat grey gauge, `f_xx = 0`", "rt 0.5"),
        ("3-7", "bending in y is zero", None, "Readout 2: flat grey gauge, `f_yy = 0`", "rt 0.5"),
        ("3-7", "twist is one", None, "Readout 3: violet ribbon, `f_xy = 1`", "rt 0.5"),
    ]),
    dict(slug="11_matrix", cls="Scene11Matrix", part="CH3", title="The Hessian, and its mirror",
         engine="Manim + skia caption", beats=[
        ("3-8", "the last one", None, "Back to the centered grid; bottom-left highlights", "rt 0.8"),
        ("3-8", "f y x", None, "Bottom-left fills violet `f_yx`", "rt 0.6"),
        ("3-8", "other way around", None, "Two tiny arrows show the order swap (move in y, then in x)", "rt 0.8"),
        ("3-8", "always matches", None, "The two violet cells pulse together; `∂²f/∂y∂x = ∂²f/∂x∂y` holds below", "rt 0.8"),
        ("3-8", "both sides", None, "Hold (equation stays)", "—"),
        ("3-9", "arrange all four", None, "Row/column labels fade; the cells tighten", "rt 1.0"),
        ("3-9", "top left", None, "`f_xx` pulses", "rt 0.4"),
        ("3-9", "bottom right", None, "`f_yy` pulses", "rt 0.4"),
        ("3-9", "other two corners", None, "Both violet cells pulse", "rt 0.4"),
        ("3-9", "hessian matrix", None, "Brackets grow; `H =` writes to the left", "rt 0.8"),
        ("3-10", "otto hess", None, "Caption “Ludwig Otto Hesse · 1811–1874” (skia). (SRT says “Hess”)", "fade rt 0.6, out at 283"),
        ("3-10", "symmetric", None, "A thin diagonal line sweeps corner to corner", "rt 0.8"),
        ("3-10", "mirror image", None, "The two violet cells reflect onto each other across it", "rt 1.0"),
    ]),
    dict(slug="12_build", cls="Scene12Build", part="CH3", title="Building the puzzle Hessian",
         engine="Manim (+ moderngl flashback)", beats=[
        ("3-11", "lets build one", None, "The symbols shrink to small corner tags; the cells are empty again", "rt 0.6"),
        ("3-11", "x squared", 288.0, "`f = x²` (red)", "`Write` rt 0.6"),
        ("3-11", "three x y", None, "`+ 3xy` (violet)", "rt 0.6"),
        ("3-11", "y squared", 290.0, "`+ y²` (green)", "rt 0.6"),
        ("3-12", "bending in x is two", None, "Worked line `f_x = 2x + 3y → f_xx = 2`; the **2** flies into the top-left", "`TransformMatchingTex` rt 1.0"),
        ("3-12", "bending in y is two", None, "`f_y = 3x + 2y → f_yy = 2`; **2** into bottom-right", "rt 1.0"),
        ("3-12", "twist is three", None, "`f_xy = 3`; **3** splits into both violet cells", "rt 1.0"),
        ("3-13", "so the hessian is", None, "The worked lines clear; the matrix centers", "rt 0.6"),
        ("3-13", "two three three two", None, "Each entry pulses on its word: 2 · 3 · 3 · 2", "per word, rt 0.3"),
        ("3-13", "hold on to that one", None, "Soft skia glow on `[[2,3],[3,2]]`", "rt 0.8"),
        ("3-14", "puzzle surface", 301.0, "Flashback: the intro's puzzle surface fades in beside it, the ball rolling away (desaturated)", "rt 1.0"),
    ]),
    dict(slug="13_direction", cls="Scene13Direction", part="CH4", title="Bending in any direction",
         engine="moderngl (top-down contours) + Manim", beats=[
        ("4-1", "any direction", None, "Top-down puzzle surface as hyperbolic contours. A white unit arrow **u** appears at the center and turns slowly", "rt 0.8, slow spin"),
        ("4-1", "east or north", None, "u touches east, then north", "rt 1.2"),
        ("4-1", "in between", None, "u settles at 30°", "rt 0.8"),
        ("4-2", "beautiful part", None, "Left panel opens; `H` (colored) sits in it", "rt 0.8"),
        ("4-2", "new derivatives", None, "H pulses: nothing new needed", "rt 0.5"),
        ("4-2", "pick a direction", None, "u swings back to east (θ = 0) for the worked example", "rt 0.8"),
        ("4-2", "length one", None, "Unit circle draws; `|u| = 1`", "rt 0.6"),
        ("4-2", "multiply the hessian", None, "`H u = [2, 3]` (first column) and a faint arrow Hu on the map", "rt 0.8"),
        ("4-2", "dot product", None, "Hu's shadow drops onto u; `uᵀ(Hu) = 2`", "rt 0.8"),
        ("4-2", "number that comes out", None, "The **2** pops with a blue smile gauge", "rt 0.5"),
        ("4-2", "in that direction", None, "`bending(u) = uᵀHu` boxed", "rt 0.6"),
    ]),
    dict(slug="14_sweep", cls="Scene14Sweep", part="CH4", title="The sweep ★",
         engine="moderngl (slice plane at θ) + Manim live graph", beats=[
        ("4-3", "watch it on the puzzle surface", None, "**Main layout**: left, the 3D puzzle surface with a vertical slice plane at θ through the center (cut curve tinted by sign); right, axes for bending vs θ (0°–180°); gauge + readout under the 3D view", "rt 1.2"),
        ("4-3", "facing east", 327.5, "θ = 0: plane faces east; graph dot at (0°, 2)", "rt 0.5"),
        ("4-3", "two", 329.5, "Readout **2**", "rt 0.3"),
        ("4-3", "smile", 330.4, "Gauge: blue smile", "rt 0.4"),
        ("4-4", "slowly turn", None, "θ starts to move; the graph traces live", "θ keyframes ↓"),
        ("4-4", "northeast", None, "Compass tag “NE” at 45° on the dial", "rt 0.4"),
        ("4-4", "three", 335.5, f"θ = {THETA['3']:.2f}° → readout **3**", "keyframe"),
        ("4-4", "four", 336.5, f"θ = {THETA['4']:.2f}° → readout **4**", "keyframe"),
        ("4-4", "five", 339.5, "θ = 45° → readout **5**; plane along (1,1), curve brightest blue, graph peak marked", "keyframe, ease-out"),
        ("4-4", "strongest smile", None, "Peak marker pulses", "rt 0.5"),
        ("4-5", "keep turning", None, "θ moves on", "keyframe"),
        ("4-5", "two", 345.0, "θ = 90° (north) → readout **2**", "keyframe"),
        ("4-5", "zero", 348.8, f"θ = {THETA_ZERO:.2f}° → readout **0**, gauge flat grey", "keyframe"),
        ("4-5", "past it", None, "Graph dips below zero; formula `2 + 3 sin 2θ` writes onto the graph", "rt 0.8"),
        ("4-5", "northwest", None, "θ = 135° → plane along (1,−1)", "keyframe, ease-out"),
        ("4-5", "minus one", 352.0, "Readout **−1**", "rt 0.3"),
        ("4-5", "frown", 353.5, "Gauge: orange frown", "rt 0.4"),
    ]),
    dict(slug="15_eigen", cls="Scene15Eigen", part="CH4", title="The frown was hiding in between",
         engine="moderngl + Manim (projected axes)", beats=[
        ("4-6", "smiles along one diagonal", None, "Blue line drawn on the surface along (1,1)", "rt 0.8"),
        ("4-6", "frowns along the other", None, "Orange line along (1,−1)", "rt 0.8"),
        ("4-6", "its a saddle", None, "Camera lifts to an oblique view: it is plainly a saddle", "rt 1.2"),
        ("4-6", "east and north slices", None, "Red and green slices flash in with their two blue smiles", "rt 0.6"),
        ("4-6", "hiding in between", None, "They fade; **the intro's ball replays** and rolls straight down the orange line. Puzzle solved", "roll rt 2.0"),
        ("4-7", "right angles", None, "A right-angle mark at the center", "rt 0.5"),
        ("4-7", "eigenvectors", None, "Labels `v₁` (blue) and `v₂` (orange) on the two axes", "rt 0.6"),
        ("4-7", "five and minus one", None, "`λ = 5` (blue) and `λ = −1` (orange)", "rt 0.6"),
        ("4-7", "eigenvalues", 373.5, "The word “eigenvalues” underlines both λ", "rt 0.5"),
    ]),
    dict(slug="16_diagonal", cls="Scene16Diagonal", part="CH4", title="Line up the grid",
         engine="moderngl + Manim", beats=[
        ("4-8", "turn the grid", None, "The floor grid rotates 45° onto the eigen-axes; contours become axis-aligned", "rt 1.6 `smooth`"),
        ("4-8", "twist disappears", None, "The matrix morphs: violet 3s drain to 0", "rt 0.8"),
        ("4-8", "two eigenvalues", None, "Diagonal becomes **5** (blue) and **−1** (orange)", "rt 0.8"),
        ("4-8", "diagonal", 382.0, "Diagonal glow", "rt 0.5"),
        ("4-9", "any smooth surface", None, "Cut to the two-hill landscape from Ch2; zoom onto a point", "rt 1.4"),
        ("4-9", "up close", None, "A translucent **quadratic patch** hugs it", "rt 0.8"),
        ("4-9", "height", 386.0, "Term 1: `f(p)`", "rt 0.4"),
        ("4-9", "tilt from the gradient", None, "Term 2: `+ ∇f·h` (yellow); the patch tilts", "rt 0.6"),
        ("4-9", "bend from the hessian", None, "Term 3: `+ ½ hᵀHh` (colored); the patch bends", "rt 0.6"),
        ("4-10", "parabola from before", None, "Inset of the Ch1 cosine-and-parabola frame slides in", "rt 0.8"),
        ("4-10", "one dimension up", None, "Both glow, then fade", "rt 0.8"),
    ]),
    dict(slug="17_signs", cls="Scene17Signs", part="CH5", title="Read the signs",
         engine="moderngl (fog reuse, mini-surface) + Manim sign chart", beats=[
        ("5-1", "answer the question", None, "A 2 s return to the fog, walker and disc (I-1 reused)", "dissolve rt 0.8"),
        ("5-2", "two eigenvalues", None, "The fog dissolves into a **sign chart**: λ₁–λ₂ plane, with a live mini-surface (H = diag(λ₁, λ₂)) in the corner tied to a dot", "rt 1.0"),
        ("5-3", "both positive", None, "Dot → Q1 (2, 2); quadrant tints blue; mini-surface becomes a bowl", "rt 1.0"),
        ("5-3", "every direction", 399.5, "Small gauges around the bowl, all blue smiles", "rt 0.5"),
        ("5-3", "local minimum", None, "Label **valley · local minimum** in Q1", "rt 0.5"),
        ("5-4", "both negative", None, "Dot → Q3 (−2, −2) through the origin; tints orange; mini-surface becomes a dome", "rt 1.2"),
        ("5-4", "local maximum", None, "Label **peak · local maximum** in Q3", "rt 0.5"),
        ("5-5", "one of each", None, "Dot → Q4 (2, −2), then Q2; both tint with a blue/orange split; mini-surface becomes a saddle", "rt 1.6"),
        ("5-5", "saddle", 412.3, "Label **saddle** in Q2 and Q4", "rt 0.4"),
    ]),
    dict(slug="18_det", cls="Scene18Det", part="CH5", title="The determinant shortcut",
         engine="Manim", beats=[
        ("5-6", "shortcut", None, "The chart shifts right; equation space opens left", "rt 0.6"),
        ("5-6", "multiply the two bending numbers", None, "`f_xx · f_yy` (red · green)", "rt 0.8"),
        ("5-6", "subtract the twist squared", None, "`− f_xy²` (violet)", "rt 0.6"),
        ("5-6", "determinant", None, "`det H =` prefixes it", "rt 0.6"),
        ("5-6", "multiplied together", None, "`= λ₁ · λ₂`", "rt 0.6"),
        ("5-6", "negative", 423.0, "Q2 and Q4 shade: det < 0", "rt 0.6"),
        ("5-6", "saddle", 425.3, "Tag **saddle** on the shaded quadrants", "rt 0.4"),
        ("5-6", "positive", 426.4, "Q1 and Q3 shade: det > 0", "rt 0.6"),
        ("5-6", "tells you which", None, "`f_xx > 0` → Q1 arrow, `f_xx < 0` → Q3 arrow", "rt 0.6"),
        ("5-7", "puzzle surface", 430.5, "`[[2,3],[3,2]]` slides in", "rt 0.6"),
        ("5-7", "two times two", None, "`2 · 2 = 4`", "rt 0.6"),
        ("5-7", "three squared", None, "`3² = 9`", "rt 0.6"),
        ("5-7", "four minus nine", None, "`4 − 9`", "rt 0.5"),
        ("5-7", "minus five", None, "`= −5` in orange", "rt 0.5"),
        ("5-7", "confirmed", None, "The dot lands at (5, −1) in Q4; stamp **saddle**", "rt 0.6"),
    ]),
    dict(slug="19_landscape", cls="Scene19Landscape", part="CH5", title="A real landscape",
         engine="moderngl (GLSL height `x³ − 3x + y²`, z clamped) + Manim", beats=[
        ("5-8", "real landscape", None, "The landscape rises; slow camera orbit begins", "rt 1.2, orbit to scene end"),
        ("5-8", "x cubed", None, "`f = x³ − 3x + y²` writes (color-coded)", "rt 1.2"),
        ("5-8", "two flat points", None, "Two white rings pulse", "rt 0.6"),
        ("5-8", "x equals one", 446.5, "Ring at (1, 0) brightens", "rt 0.4"),
        ("5-8", "x equals minus one", 447.5, "Ring at (−1, 0) brightens", "rt 0.4"),
        ("5-9", "six", 451.0, "Floating label above (1, 0) builds `[[6,0],[0,2]]` entry by entry", "per word rt 0.3"),
        ("5-9", "valley", 454.5, "A ball dropped nearby settles into (1, 0)", "rt 1.0"),
        ("5-10", "minus six", None, "Label above (−1, 0): `[[−6,0],[0,2]]`", "per word rt 0.3"),
        ("5-10", "saddle", 460.0, "Tag **saddle**", "rt 0.4"),
        ("5-10", "pass that leads out", None, "A dashed yellow path climbs out of the valley and over the pass", "rt 1.6"),
    ]),
    dict(slug="20_flat", cls="Scene20Flat", part="CH5", title="When the test can't tell",
         engine="moderngl (two viewports) + Manim", beats=[
        ("5-11", "just like on the line", None, "The landscape fades; a tiny echo of the Ch1 `x³` row with its grey “?” drifts in", "rt 0.8"),
        ("5-11", "cant tell", None, "The echo fades; a split frame opens", "rt 0.8"),
        ("5-11", "x to the fourth", None, "Left: the flat-bottomed bowl `x⁴ + y⁴`", "rt 1.0"),
        ("5-11", "valley", 469.0, "Tag **valley**", "rt 0.4"),
        ("5-11", "all zeros", None, "A grey zero matrix and a flat grey gauge", "rt 0.6"),
        ("5-12", "monkey saddle", None, "Right: the monkey saddle `x³ − 3xy²`, slowly rotating, also with a zero matrix", "rt 1.0"),
        ("5-12", "two legs and a tail", None, "Its three downward lobes outline one after another", "lag 0.3, rt 1.2"),
        ("5-13", "eigenvalue is zero", None, "Both zero matrices pulse; a slow push-in on both centers starts and runs to the scene end", "pulse rt 0.5, push `linear` to 480.4"),
        ("5-13", "look closer", None, "Fade to background under the push-in", "rt 0.6 (ends ≈ 480.1)"),
    ]),
    dict(slug="21_error", cls="Scene21Error", part="CH6", title="Landscapes of error",
         engine="moderngl (procedural terrain) + skia", beats=[
        ("6-1", "why does this matter", None, "Wide, slow fly-over of a rugged seeded terrain", "fly-over `linear` to scene end"),
        ("6-1", "bottom of a valley", None, "The deepest pit glows faintly", "rt 0.8"),
        ("6-1", "neural network", None, "A soft caption “training”", "rt 0.6"),
        ("6-1", "lowest point", None, "A marker settles at the pit", "rt 0.6"),
        ("6-1", "height is the error", None, "Caption `height = error`", "rt 0.6"),
        ("6-2", "not two dimensions", None, "The two floor axes brighten", "rt 0.5"),
        ("6-2", "but millions", 495.5, "Axes **multiply** into hundreds of faint radial axis lines (seeded, skia glow). The fan is handed to Scene 22, which fades it under its first beat", "burst rt 0.6 `rush_from`"),
    ]),
    dict(slug="22_descent", cls="Scene22Descent", part="CH6", title="Gradient descent zigzags",
         engine="Manim (contour map of `x² + 10y²`)", beats=[
        ("6-3", "simplest way down", None, "Top-down exact ellipses of `x² + 10y²`; ball at (3, 1)", "rt 1.0"),
        ("6-3", "follow the gradient", None, "A `−∇f` arrow from the ball", "rt 0.6"),
        ("6-3", "one small step", None, "First step taken", "rt 0.6"),
        ("6-3", "gradient descent", None, "Label “gradient descent”", "rt 0.5"),
        ("6-4", "long narrow valley", None, "The map stretches to show the long, narrow trough", "rt 1.0"),
        ("6-4", "eigenvalues are two", None, "`H = diag(2, 20)`; short blue axis tick (2) along x", "rt 0.6"),
        ("6-4", "20", 508.0, "Long blue axis tick (20) along y", "rt 0.4"),
        ("6-4", "10 times steeper", None, "The steep walls tint", "rt 0.6"),
        ("6-5", "overshoots", None, "The steps resume: each crosses the trough floor", "steps ↓"),
        ("6-5", "zigzags", None, f"The full computed path plays ({GD_N} steps, step 0.09, y × −0.8 per step) with a fading trail; a step counter ticks", "to ~516.8"),
        ("6-5", "crawling", None, "The path crawls along x toward the center", "—"),
        ("6-6", "20 over two", None, "`κ = 20 / 2 = 10` beside the map", "rt 0.8"),
        ("6-6", "condition number", None, "Label “condition number”", "rt 0.5"),
    ]),
    dict(slug="23_newton", cls="Scene23Newton", part="CH6", title="One Newton jump, and a trillion numbers",
         engine="Manim + moderngl inset + moderngl procedural mosaic", beats=[
        ("6-7", "bring in the hessian", None, "The GD path dims; H glows", "rt 0.6"),
        ("6-7", "newtons method", None, "Label “Newton's method”", "rt 0.5"),
        ("6-7", "as a bowl", None, "3D inset: the local quadratic model as a translucent bowl", "rt 0.8"),
        ("6-7", "jumps straight", None, "**One arc** from (3, 1) to (0, 0)", "rt 1.0 `smooth`"),
        ("6-7", "one jump", None, f"Landing flash; counter “1 step” vs “{GD_N} steps”", "rt 0.6"),
        ("6-8", "the catch", None, "Everything fades except the 2×2 grid", "rt 0.6"),
        ("6-8", "million by a million", None, "The grid **zooms out** into an endless mosaic of tiny cells (procedural shader)", "zoom rt 2.0 `rush_into`"),
        ("6-8", "trillion numbers", None, "Counter rolls up to `1,000,000,000,000`", "rt 1.0"),
        ("6-8", "estimate pieces", None, "Only a thin band of cells along the diagonal stays lit", "rt 0.8"),
    ]),
    dict(slug="24_saddles", cls="Scene24Saddles", part="CH6", title="Most flat points are saddles",
         engine="Manim (seeded) + moderngl", beats=[
        ("6-9", "something surprising", None, "Mosaic fades; a grid of critical points, each a row of 2 eigenvalue dots", "rt 0.8"),
        ("6-9", "huge landscapes", None, "Rows grow to 10 dots", "rt 0.8"),
        ("6-9", "arent valleys", None, "All-blue rows (valleys) get a ring; few remain", "rt 0.6"),
        ("6-9", "saddles", 548.5, "The mixed rows tag **saddle**", "rt 0.4"),
        ("6-9", "every single eigenvalue", None, "One all-blue row is highlighted", "rt 0.6"),
        ("6-9", "millions of them", None, "Rows grow to 100 dots; all-blue rows become tiny isolated sparks. Caption “intuition, not a proof”", "rt 1.0"),
        ("6-9", "almost always negative", None, "Orange dots pulse", "rt 0.5"),
        ("6-10", "theres almost always", 557.0, "One saddle row enlarges into a 3D saddle", "rt 1.0"),
        ("6-10", "way down", None, "A ball rolls off it along the orange direction", "rt 0.6 `rush_from` (ends 559.5)"),
    ]),
    dict(slug="25_recap", cls="Scene25Recap", part="OUTRO", title="Recap",
         engine="skia cards + Manim", beats=[
        ("O-1", "walk back through it", None, "Card 1 (skia) slides in", "rt 0.8"),
        ("O-1", "on a line", None, "Parabola on card 1", "rt 0.6"),
        ("O-1", "smile", 564.0, "Blue smile gauge", "rt 0.4"),
        ("O-1", "frown", 566.0, "Orange frown gauge", "rt 0.4"),
        ("O-2", "on a surface", None, "Card 2 slides in: the colored 2×2 grid", "rt 0.8"),
        ("O-2", "four second derivatives", None, "Cells light up in a stagger", "lag 0.1, rt 0.6"),
        ("O-2", "shows up twice", None, "Violet pair pulses", "rt 0.5"),
        ("O-2", "you have the hessian", None, "Brackets close", "rt 0.5"),
        ("O-3", "any direction", None, "Card 3: the direction dial sweeping", "rt 0.8"),
        ("O-3", "eigenvectors", None, "Blue and orange eigen-axes", "rt 0.5"),
        ("O-3", "eigenvalues", 584.0, "λ labels", "rt 0.4"),
        ("O-4", "flat point", 586.5, "Card 4: the sign chart", "rt 0.8"),
        ("O-4", "signs decide everything", None, "The four cards tile into a 2×2, echoing the matrix", "rt 1.0"),
        ("O-4", "all positive", None, "Q1 tints blue", "rt 0.3"),
        ("O-4", "all negative", None, "Q3 tints orange", "rt 0.3"),
        ("O-4", "mixed", None, "Q2/Q4 tint split", "rt 0.3"),
    ]),
    dict(slug="26_fog", cls="Scene26Fog", part="OUTRO", title="Back to the fog",
         engine="moderngl + Manim", beats=[
        ("O-5", "next time", None, "The cards dissolve into the **opening shot**: fog, walker, tangent disc", "rt 1.2"),
        ("O-5", "in the fog", None, "Fog drifts", "—"),
        ("O-6", "which way is down", None, "The four probe arrows flash and vanish (as in I-2)", "rt 0.8"),
        ("O-6", "how the ground bends", None, "A blue smile arc and an orange frown arc glow under the walker at right angles. **The fog lifts**: the walker stands on a saddle", "rt 1.6"),
        ("O-7", "thanks for watching", None, "Hold on the revealed saddle, then fade to black, landing on the last frame", "fade starts 603.95, rt 0.6 (ends 604.55)"),
    ]),
]


def fmt_t(t: float) -> str:
    return f"{t:.2f}"


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main(out=sys.stdout) -> None:
    assert len(SCENES) == len(CUT_FRAMES) - 1, (len(SCENES), len(CUT_FRAMES))
    w = out.write
    problems = []
    w("## Scene slices (60 fps, each cut on a frame inside a real silence)\n\n")
    w("| # | Part | File · class | Range (s) | Frames | Length | Cut silence |\n|---|---|---|---|---|---|---|\n")
    for i, sc in enumerate(SCENES):
        f0, f1 = CUT_FRAMES[i], CUT_FRAMES[i + 1]
        sc["t0"], sc["t1"] = f0 / FPS, f1 / FPS
        sil = CUT_SILENCES[i] if i < len(CUT_SILENCES) else None
        sil_s = f"{sil[0]:.2f}–{sil[1]:.2f}" if sil else "— (end of audio)"
        w(f"| {i+1:02d} | {sc['part']} | `scene_{sc['slug']}.py` · `{sc['cls']}` | "
          f"{sc['t0']:.3f} – {sc['t1']:.3f} | {f0} – {f1} | {sc['t1']-sc['t0']:.1f} s | {sil_s} |\n")
    w(f"\nTotal: **{CUT_FRAMES[-1]} frames = {CUT_FRAMES[-1]/FPS:.3f} s** "
      f"(audio {AUDIO_END:.3f} s; the last 10 ms of silence are trimmed so the video "
      f"is never longer than the audio).\n\n---\n")

    part = None
    for i, sc in enumerate(SCENES):
        if sc["part"] != part:
            part = sc["part"]
        w(f"\n### SCENE {i+1:02d} · {sc['part']}: {sc['title']} · "
          f"{sc['t0']:.3f}–{sc['t1']:.3f} ({mmss(sc['t0'])}–{mmss(sc['t1'])})\n\n")
        w(f"**Engine:** {sc['engine']}\n\n")
        w("| t | Shot | Cue key | What happens | Anim (start = t − 0.15 unless noted) |\n|---|---|---|---|---|\n")
        last = sc["t0"]
        for shot, key, after, what, anim in sc["beats"]:
            if key == "@0":
                t, key_s = sc["t0"], "(frame 0)"
            else:
                a = sc["t0"] - 0.05 if after is None else after
                try:
                    t = cue.at(key, after=a)
                except KeyError:
                    problems.append(f"{sc['cls']}: {key!r} after {a}")
                    t = float("nan")
                key_s = f"`{key}`"
                if not (sc["t0"] - 0.2 <= t < sc["t1"]):
                    problems.append(f"{sc['cls']}: {key!r} at {t:.2f} outside "
                                    f"{sc['t0']:.2f}-{sc['t1']:.2f}")
                if t + 1e-6 < last:
                    problems.append(f"{sc['cls']}: {key!r} at {t:.2f} before previous beat {last:.2f}")
                last = t
            w(f"| {fmt_t(t)} | {shot} | {key_s} | {what} | {anim} |\n")
    if problems:
        sys.stderr.write("PROBLEMS:\n  " + "\n  ".join(problems) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
