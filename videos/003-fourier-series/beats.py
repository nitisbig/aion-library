"""Timed beat sheet for 003, resolved against the real SRT.

Every beat is a cue key that is looked up with `Cue.at()`. Nothing is typed in
by hand. Run it to regenerate the timed half of storyboard.md, to prove that
every key the scenes will use exists in the SRT, and to re-check the math:

    uv run python videos/003-fourier-series/beats.py > /tmp/timed.md

Keys are searched **in order**: each beat is looked up after the previous beat
of its scene, so repeated words ("circle", "one", "average") resolve to the
right occurrence without typing any time.

Special keys:
    "@0"       the scene's first frame
    "end:xyz"  the END time of phrase xyz (e.g. a loop that must close on a word)

Scene cuts are frame boundaries (60 fps) at the middle of a real silence found
with `ffmpeg silencedetect -35dB d=0.25`. They are written below as the pair of
words around the silence, so they are looked up too, never typed.
"""

from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

from aion import fourier as F
from aion.sync import Cue

HERE = Path(__file__).parent
AUDIO = HERE / "assets" / "audio.mp3"
FPS = 60
LEAD = 0.15
AUDIO_END = 621.576          # ffprobe, checked in main()

cue = Cue.load(HERE / "assets" / "cue-per-word.srt")


# ── cut points ────────────────────────────────────────────────────────────
# Each cut = (last words of the scene before, first words of the next scene).
# The cut lands on the frame nearest the middle of the silence between them.
CUTS = [
    ("treble clef", "heres what i find"),
    ("spinning circles", "think of a chord"),
    ("recognize it later", "as with anything new"),
    ("leave a trail", "what you get is"),
    ("one circle can do", "theres another view"),
    ("one turning motion", "one circle gives you"),
    ("a little ripple", "now lets be more"),
    ("turning into", "watch the top"),
    ("up to sharp corners", "but look closely"),
    ("corners are expensive", "now you might"),
    ("our square wave", "fouriers move"),
    ("an even warmth", "but for this to work"),
    ("back to our drawing", "so far weve"),
    ("right on the page", "this picture is"),
    ("almost any path", "on a page"),
    ("where the drawing sits", "heres a friendly"),
    ("exactly these", "in general"),
    ("of every circle", "lets warm up"),
    ("out to nothing", "that gives us"),
    ("stand still dont", "now the speed one"),
    ("frozen in place", "as a sanity check"),
    ("no circle there", "if you hold on"),
    ("all it says", "so lets give it"),
    ("tip to tail", "with one circle"),
    ("the others cant", "remember how i said"),
    ("circles it takes", "thats why this idea"),
    ("you wont notice", "so lets step back"),
    ("you were looking for", "theres one thing"),
    ("well go next", "for now lets watch"),
]


def audio_silences() -> list[tuple[float, float]]:
    """Real silences in the audio (the aligner's word ends can overrun them).

    Cached in media/cache/ keyed on the audio's size and mtime, so scenes that import
    this module don't re-run ffmpeg on every render."""
    import json
    st = AUDIO.stat()
    cache = HERE.parents[1] / "media" / "cache" / f"silences_{st.st_size}_{int(st.st_mtime)}.json"
    if cache.exists():
        return [tuple(x) for x in json.loads(cache.read_text())]
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(AUDIO), "-af",
         "silencedetect=n=-35dB:d=0.25", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    ends = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", log)
    out = [(float(e) - float(d), float(e)) for e, d in ends]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out))
    return out


def cut_silences() -> list[tuple[float, float]]:
    """Gap between the two SRT words, intersected with the real audio silence."""
    sil = audio_silences()
    out, after = [], 0.0
    for left, right in CUTS:
        a = cue.end_of(left, after=after)
        b = cue.at(right, after=a - 0.01)
        hits = [(max(a, s0), min(b, s1)) for s0, s1 in sil if min(b, s1) - max(a, s0) > 0.15]
        assert len(hits) == 1, (left, right, a, b, hits)
        out.append(hits[0])
        after = b
    return out


CUT_SILENCES = cut_silences()
END_FRAME = math.floor(AUDIO_END * FPS)          # the video never outlasts the audio
CUT_FRAMES = [0] + [round((a + b) / 2 * FPS) for a, b in CUT_SILENCES] + [END_FRAME]


# ── math that the scenes put on screen (checked in verify_math) ───────────
def square_wave(t, n_terms):
    return F.square_wave(t, n_terms)


def square_loop_coeffs(N=4096):
    """Unit-speed square loop of side 2, starting at the middle of the right side."""
    return F.coefficients(F.square_loop(N), 40)


ROUNDED_SQUARE = {1: 1.0, -3: -1 / 9}            # z = e^{2πit} − (1/9) e^{−2πi·3t}
# Ch5 test drawing: built from 5 known circles so every on-screen answer is exact.
# Simple (no self-crossing), ~12 % concave: reads as a bean. Checked in verify_math.
_BEAN0 = {0: 0.6 + 0.35j, 1: 1.0, -1: 0.35 * np.exp(0.5j),
          2: 0.22 * np.exp(2.2j), -2: 0.12 * np.exp(-0.8j)}
# Same curve, loop started 0.6/2π later (c_n · e^{0.6in}): c₁ gets a real starting angle (0.6 rad) for S21's arc.
BEAN = {n: c * np.exp(0.6j * n) for n, c in _BEAN0.items()}


def loop(coeffs, t):
    return F.partial_sum(coeffs, t)


def spin_average(coeffs, k, samples=1000):
    return F.spin_average(loop(coeffs, np.arange(samples) / samples), k)


def verify_math() -> list[str]:
    facts = []
    t = np.linspace(0, np.pi, 200_001)
    peaks = {n: square_wave(t[t < 0.2], n).max() for n in (10, 50, 200)}
    for n, p in peaks.items():
        assert 1.178 < p < 1.183, (n, p)
    facts.append("Gibbs peak (±1 wave) with 10 / 50 / 200 circles: "
                 + " / ".join(f"{p:.4f}" for p in peaks.values())
                 + f" → overshoot {(peaks[200] - 1) / 2 * 100:.2f} % of the jump")
    sq = square_loop_coeffs()
    nz = {n: c for n, c in sq.items() if abs(c) > 1e-6}
    assert all(n % 4 == 1 for n in nz), sorted(nz)
    c1 = sq[1]
    for n in (-3, 5, -7, 9):
        assert abs(abs(sq[n]) - abs(c1) / n**2) < 1e-3 and abs(sq[n].imag) < 1e-6, (n, sq[n])
    facts.append(f"Square loop: c₁ = {c1.real:.5f}, c₋₃ = {sq[-3].real:.5f}, c₅ = {sq[5].real:.5f}, "
                 f"c₋₇ = {sq[-7].real:.5f}: only n ≡ 1 mod 4, |c_n| = c₁/n² (shrinks like 1/n²)")
    for k, want in ((1, 1.0), (-3, -1 / 9), (2, 0.0), (0, 0.0)):
        got = spin_average(ROUNDED_SQUARE, k)
        assert abs(got - want) < 1e-9, (k, got)
    facts.append("Rounded square spin-and-average: k=1 → 1, k=−3 → −1/9, k=2 → 0, k=0 → 0 (exact)")
    for k, c in BEAN.items():
        assert abs(spin_average(BEAN, k) - c) < 1e-9
    for k in (3, -3):
        assert abs(spin_average(BEAN, k)) < 1e-9
    facts.append("Bean: spin-and-average returns all 5 circles exactly; k=±3 → 0")
    kappa_ratio = 3**2 / 1**2
    facts.append(f"Heat: mode n fades as e^(−κn²t), so mode 3 fades {kappa_ratio:.0f}× as fast as mode 1")
    return facts


# ── scenes ────────────────────────────────────────────────────────────────
# (cue key, what happens, anim note). Times come from the keys.
SCENES: list[dict] = [
    # ───────────────────────── INTRO ─────────────────────────
    dict(slug="01_hook", cls="Scene01Hook", part="INTRO", title="What you're looking at",
         engine="moderngl `EpicyclePlate` + Taichi `InkParticles` + `post_gl` bloom",
         why="Opens on the finished picture (rule 1, 3). The strangest fact comes before any explanation.",
         beats=[
        ("@0", "Fade up from black on a chain already turning: the **same 201-circle clef chain** used in S25 and S30 (identical coefficients, so the ending is a true callback). Rims faint silver, pen gold. The pen has just started its loop and leaves a thin gold line. The camera drifts in from 1.08×", "fade 0.4 s · camera `smooth` over the whole scene · loop period = `CLEF_LOOP_S01`"),
        ("chain of circles", "A light sweep runs down the chain from the root joint to the pen, joint by joint", "1.2 s"),
        ("edge of the one before", "Close beat: the camera follows joint 3 for about a second, showing one circle riding the rim of the one before, then eases back out", "1.0 s in, 0.8 s out"),
        ("own steady speed", "Rims tint `FWD` / `BWD` by spin direction", "0.5 s"),
        ("very last circle", "The camera settles on the whole drawing. The pen ignites: bloom up, first sparks", "0.4 s"),
        ("treble clef", "About 90 % of the clef is drawn and it reads. Comet glow on the ink", "—"),
        ("end:treble clef", "The pen keeps going and **closes the loop inside the pause** (at the cut). A soft flash runs once along the whole outline", "ease out on the last 0.5 s of the loop"),
    ]),
    dict(slug="02_corner", cls="Scene02Corner", part="INTRO", title="How can circles draw a corner?",
         engine="`EpicyclePlate` (clef → square chain) + Manim overlay + skia `TitlePlate` + `HeatRingPlate` stills (from S11)",
         why="The square is the extreme wrong-intuition case (rule 4). The question is asked aloud and held (rule 15).",
         beats=[
        ("roundest thing", "The clef chain fades to 15 % and its ink to 30 %. One circle at the root brightens alone", "0.8 s"),
        ("no corners", "A dashed square ghost flickers around that circle and dissolves: what a circle is *not*", "0.5 s in / 0.8 s out"),
        ("sharp turns", "The chain returns to full. Push in on the clef's sharpest turn (bottom hook), then pull back", "camera 1.2 s"),
        ("square", "**No cut:** the chain re-tunes into the square loop's circles (speeds 1, −3, 5, −7, …; 61 circles) and the ink morphs clef → square", "coefficient tween 1.4 s `smooth`"),
        ("four perfect corners", "The camera dives 8× into one corner. Tiny circles whirl there; the ink corner stays razor sharp", "1.5 s `smooth`"),
        ("draw a corner", "Freeze. Everything dims to 20 % except the corner and the pen. Hold through the pause", "0.4 s"),
        ("fourier series", "Pull back to the whole square. **\"Fourier Series\"** sets in Space Grotesk with a soft glow and a warm light sweep", "`TitlePlate` 1.1 s"),
        ("joseph fourier", "A small name line under the title, Inter Light", "0.6 s"),
        ("heat", "Teaser flash: the metal ring, half ember and half ice (a still from S11)", "in 0.4 s, hold 1.2 s, out 0.4 s"),
        ("bold claim", "Title lifts and fades", "0.6 s"),
        ("any loop", "Gallery: three small chains draw at once (clef, square, the Ch5 bean)", "`LaggedStart` 0.25"),
        ("spinning circles", "Their rims pulse in a stagger, then the gallery fades to black", "0.8 s"),
    ]),
    dict(slug="03_chord", cls="Scene03Chord", part="INTRO", title="A chord, and a recipe",
         engine="Manim (waves, formula) + skia line-art piano keys",
         why="The analogy gives a familiar picture before any math. The formula is planted, unexplained (rule 8).",
         beats=[
        ("chord on a piano", "A line-art octave of piano keys (skia). C, E, G press down in turn", "0.8 s"),
        ("one sound", "Three thin silver sines (C4, E4, G4, computed, slowed) rise from the keys and **merge into one gold waveform**", "1.2 s"),
        ("few notes", "The gold waveform splits back into its three waves, then re-merges", "0.6 s + 0.6 s"),
        ("take a shape", "The keys and wave fade. A gold rounded square draws in their place", "1.0 s"),
        ("pick out the circles", "It splits into its two circles (blue r = 1, orange r = 1/9), which then re-merge", "1.2 s"),
        ("recipe", "Everything fades except the big blue circle, which slides to the left third", "0.8 s"),
        ("on screen now", "The recipe `c_n = ∫₀¹ f(t) e^{−2πint} dt` writes on in muted silver at 60 %, upper right (colors arrive only in S23)", "`Write` 1.2 s"),
        ("recognize it later", "The formula fades to 0 in place; its exact position is saved as `RECIPE_POS` for S23. The single circle remains: the hand-off to Ch1", "0.8 s"),
    ]),
    # ───────────────────────── CH1 ─────────────────────────
    dict(slug="04_one_circle", cls="Scene04OneCircle", part="CH1", title="One circle",
         engine="Manim (`EpicycleChain` with 1 circle, `ShadowWave`)",
         why="Concrete before general (rule 13). One focal point: the tip's height.",
         beats=[
        ("start easy", "Eyebrow **01 · ONE CIRCLE** (top-left)", "0.6 s"),
        ("single circle", "The circle settles at the left third (center x = −4)", "1.0 s"),
        ("arrow", "A silver arm grows from the center to the rim, with the pen at its tip", "`GrowArrow` 0.6 s"),
        ("turning steadily", "It turns counterclockwise, one turn per 4 s, for the rest of the chapter", "`linear`"),
        ("how high its tip is", "The circle dims to 40 %. A dashed line runs from the pen to a vertical track just right of the circle, where a gold marker rides up and down", "0.6 s"),
        ("up down up down", "A glow pulse at the top and bottom of the track. The motion is phased so the marker actually hits the top on \"up\"", "`there_and_back`"),
        ("time move to the right", "A time axis draws to the right of the track (hairline, no numbers)", "0.8 s"),
        ("trail", "The marker leaves a gold trail that scrolls right: the wave is born", "continuous"),
    ]),
    dict(slug="05_three_settings", cls="Scene05ThreeSettings", part="CH1", title="Size, speed, start",
         engine="Manim",
         why="Each setting changes exactly one thing, with a ghost of the old wave to compare (rules 12, 14).",
         beats=[
        ("sine wave", "Label `\\sin t` (gold) settles above a crest", "`Write` 0.6 s"),
        ("seen from the side", "2.5D beat: the circle tilts about its vertical axis to edge-on and becomes a vertical line, the pen bouncing on it; then tilts back", "1.0 s + 0.8 s"),
        ("three settings", "Three small glass chips under the stage: **size · speed · start**", "`LaggedStart` 0.15"),
        ("its size", "Chip 1 lights. Radius 1 → 1.5; the wave grows taller. The old wave stays as a dim ghost", "1.0 s"),
        ("its speed", "Chip 2 lights. Turn rate doubles; the wave has twice the wiggles. Ghost kept", "1.0 s"),
        ("where it starts", "Chip 3 lights", "0.4 s"),
        ("quarter turn ahead", "A **violet arc** shows a quarter-turn head start. The arm jumps ahead and the whole wave slides left a quarter period (a cosine)", "arc 0.6 s, slide 0.9 s"),
        ("size speed and starting point", "The three chips light again in time with the three words", "0.3 s each"),
        ("everything one circle can do", "The formula `r\\,\\sin(n t + \\varphi)` assembles from the chips: r silver, n blue, φ violet", "`TransformMatchingTex` 1.2 s"),
    ]),
    dict(slug="06_spring", cls="Scene06Spring", part="CH1", title="Two shadows of one motion",
         engine="**pyvista** off-screen frames (glossy gold tube helix, glass back wall and floor) composited in Manim; labels pinned by the shared camera matrix. Fallback: Manim `ProgressThreeDScene`",
         why="2D → 3D mode switch (rule 10). A sine and a cosine are one motion seen two ways.",
         beats=[
        ("another view", "The flat frame tilts into 3D (¾ view)", "camera 1.2 s"),
        ("slide the circle forward", "The circle slides along the time axis", "continuous"),
        ("spring", "Its tip leaves a glowing gold **tube helix**", "continuous"),
        ("from the side", "Orbit to a pure side view: the back-wall shadow is a sine. Label `\\sin t`", "orbit 1.4 s"),
        ("from above", "The camera rises to a top view: the floor shadow is a cosine. Label `\\cos t`", "1.4 s"),
        ("two shadows", "Back to ¾ view, both shadows lit at once", "1.2 s"),
        ("turning motion", "The camera settles to the side view, so the scene ends on a flat sine: the hand-off to Ch2", "0.8 s"),
    ]),
    # ───────────────────────── CH2 ─────────────────────────
    dict(slug="07_two_circles", cls="Scene07TwoCircles", part="CH2", title="Two circles",
         engine="Manim",
         why="The smallest possible step up: one extra circle, and the heights simply add.",
         beats=[
        ("one smooth wave", "Eyebrow **02 · STACKING CIRCLES**. The sine from S06 dims to a ghost", "0.6 s"),
        ("add a second", "A dashed empty circle appears on the tip (anticipation)", "0.4 s"),
        ("smaller circle", "It fills in (r = ⅓), turning three times as fast, blue", "grow 0.7 s"),
        ("two motions", "The pen now rides the small rim. The camera eases in slightly", "0.8 s"),
        ("first height", "A silver vertical bar next to the track shows the first circle's height", "0.5 s"),
        ("plus the second", "A blue bar stacks on top; the sum lands exactly on the gold marker", "0.5 s"),
        ("little ripple", "The new gold trail scrolls out with a ripple over the ghost sine", "continuous"),
    ]),
    dict(slug="08_square_build", cls="Scene08SquareBuild", part="CH2", title="One third, one fifth, one seventh",
         engine="Manim (≤ 4 circles) + `SpectrumStrip` (first appearance: \"the list\")",
         why="The recipe grows one term at a time, then the viewer is asked to guess (rule 15).",
         beats=[
        ("deliberate", "Reset to one circle of radius 4/π against a target height of 1 (two faint hairlines). A small `SpectrumStrip` appears bottom-right with one bar at speed 1", "0.8 s"),
        ("a little taller", "The radius visibly overshoots the hairline: a tiny bracket shows the extra (0.273)", "0.6 s"),
        ("three times as fast", "Circle 2 (×3) attaches. Bar at 3 rises", "0.7 s"),
        ("one third", "Label `⅓` flashes beside it", "0.3 s"),
        ("five times as fast", "Circle 3 (×5), bar at 5", "0.7 s"),
        ("one fifth", "Label `⅕`", "0.3 s"),
        ("seven times", "Circle 4 (×7), bar at 7", "0.7 s"),
        ("one seventh", "Label `1/7`", "0.3 s"),
        ("take a moment to guess", "**Pause and predict:** motion slows to a crawl, the wave breathes, nothing new appears", "0.4 s"),
        ("turning into", "Hold through the 1.2 s pause", "—"),
    ]),
    dict(slug="09_square_wave", cls="Scene09SquareWave", part="CH2", title="A square wave",
         engine="`EpicyclePlate` (10 → 200 circles) + Manim overlay (counter, ghost, strip)",
         why="The answer to the guess, with the counter locked to the spoken numbers.",
         beats=[
        ("top flatten", "Circles keep arriving; the trail's crest visibly flattens", "1.0 s"),
        ("ten circles", "Counter top-right: **10**. The strip fills to 10 bars", "0.6 s"),
        ("fifty", "**50**. The chain is a dense spiral of tiny rims", "0.6 s"),
        ("two hundred", "**200**. The strip is a fine comb", "0.6 s"),
        ("square wave", "The ideal square wave appears as a dashed ghost exactly under the gold trace", "0.6 s"),
        ("flat on top", "Hairline highlight on the tops", "0.4 s"),
        ("flat on the bottom", "On the bottoms", "0.4 s"),
        ("straight walls", "On the walls", "0.4 s"),
        ("sharp corners", "A light sweep from the chain (left) to a corner (right): circles in, corners out", "0.9 s"),
    ]),
    dict(slug="10_gibbs", cls="Scene10Gibbs", part="CH2", title="The spike that never shrinks",
         engine="Manim (partial sums computed at high resolution near the jump)",
         why="Plants \"sharp corners are expensive\" with a red marker (promise P4).",
         beats=[
        ("closely", "Zoom 6× onto one jump of the square wave", "1.2 s `smooth`"),
        ("small spike", "The overshoot crest gets a red dot (`SPIKE`)", "0.4 s"),
        ("more circles", "N steps 10 → 50: the spike narrows toward the wall. The old version stays as a fading ghost", "0.7 s"),
        ("thinner", "N → 200: thinner again", "0.7 s"),
        ("never gets any shorter", "A red hairline at the crest height stays put while every version touches it", "0.6 s"),
        ("nine percent", "A small bracket from the top of the wave to the hairline: `≈ 9\\%` of the jump", "0.6 s"),
        ("gibbs phenomenon", "The name sets small in Inter Light beside the bracket", "0.6 s"),
        ("expensive", "Zoom out. A small **red corner marker** docks top-right and stays until S26. The square wave detaches and floats free (hand-off)", "0.8 s"),
    ]),
    # ───────────────────────── CH3 ─────────────────────────
    dict(slug="11_ring", cls="Scene11Ring", part="CH3", title="A hot ring",
         engine="skia type + moderngl `HeatRingPlate` + Taichi flame/frost particles",
         why="Mode switch to history and physics (rule 10). The ring is the square wave in a new body. Pays off \"of all things, heat\" (P3).",
         beats=[
        ("wondering", "Eyebrow **03 · FOURIER'S HOT RING**. The floating square wave fades to 30 %", "0.6 s"),
        ("heat", "The ring from the intro teaser returns, larger, then dims to wait", "0.8 s"),
        ("eighteen oh seven", "Large faint \"1807\" in Space Grotesk at 12 % opacity, behind everything", "fade 0.8 s"),
        ("spreads through a solid", "A short metal bar with one hot spot: the glow spreads out along it (1D heat equation, computed)", "1.6 s"),
        ("metal ring", "The bar bends round into a brushed-metal torus at 30° pitch, slowly rotating", "1.2 s"),
        ("flame", "Ember particles lick one half, which glows orange-white", "1.0 s"),
        ("ice", "Frost particles on the other half, which cools to deep indigo", "1.0 s"),
        ("let it go", "The particles stop", "0.6 s"),
        ("hot on one side", "A temperature crown rises over the ring: the hot half up, the cold half down", "0.8 s"),
        ("unroll the ring", "The ring **unrolls** into a straight bar with its profile drawn in gold above it: the square wave, matching the S10 ghost. It rolls back up, keeping the crown", "1.2 s + 1.0 s"),
    ]),
    dict(slug="12_fading", cls="Scene12Fading", part="CH3", title="Wigglier waves fade faster",
         engine="`HeatRingPlate` (main ring + three small mode rings) + Manim inset plot",
         why="Shows why sines are natural: they keep their shape while they fade.",
         beats=[
        ("simple waves", "Three small rings split out to the right with mode 1, 3, 5 crowns (heights 1, ⅓, ⅕ × 4/π)", "`LaggedStart` 1.0 s"),
        ("once", "Ring 1 pulses", "0.4 s"),
        ("three times", "Ring 3 pulses", "0.4 s"),
        ("five", "Ring 5 pulses", "0.4 s"),
        ("keeps its shape", "Time starts (κ so that mode 1 fades over ~6 s). Each small crown shrinks **without changing shape**", "continuous"),
        ("faster it fades", "Ring 5 is nearly flat already, ring 1 barely changed", "—"),
        ("nine times as fast", "Inset plot: `e^{−t}` and `e^{−9t}` (computed). The steep one is labeled `×9`", "0.8 s"),
        ("sharp edges melt", "The main crown loses its corners first (exact sum of the decaying modes)", "continuous"),
        ("one gentle wave", "The main crown is now just mode 1. A ghost of ring 1 overlays it: a match", "0.6 s"),
        ("even warmth", "The crown flattens; the ring settles to one mid-tone", "1.2 s"),
    ]),
    dict(slug="13_doubt", cls="Scene13Doubt", part="CH3", title="Nobody believed it",
         engine="Manim",
         why="The doubt is answered by what the viewer has already seen.",
         beats=[
        ("sudden jumps", "Left: a jagged gold temperature profile with jumps", "1.0 s"),
        ("sum of smooth waves", "Right: `= \\sum` and a column of three small sines", "0.8 s"),
        ("didn't buy it", "The `=` flickers into a dim `\\overset{?}{=}`", "0.6 s"),
        ("watched it happen", "A 2 s replay of S09 (10 → 200 circles). The `?` dissolves", "2.0 s"),
        ("back to our drawing", "The ring crown unrolls into a line, which winds back into a circle with an arm: the hand-off to Ch4", "1.4 s"),
    ]),
    # ───────────────────────── CH4 ─────────────────────────
    dict(slug="14_two_directions", cls="Scene14TwoDirections", part="CH4", title="Use both directions",
         engine="Manim (`EpicycleChain` + two `ShadowWave`s)",
         why="Midpoint re-hook (rule 11): the half we ignored is the key to drawing.",
         beats=[
        ("height of the tip", "Eyebrow **04 · WAVES BECOME DRAWINGS**. The two-circle chain, with its height wave on the right", "0.8 s"),
        ("left and right", "A second projection runs down from the pen; the left-right motion writes its own wave going down the screen", "1.0 s"),
        ("use both", "Both projection lines converge back on the pen. The two waves fade", "0.6 s"),
        ("right on the page", "The pen draws its 2D path in gold ink. A faint clef ghost flashes behind it for 0.6 s", "continuous + flash"),
    ]),
    dict(slug="15_sky", cls="Scene15Sky", part="CH4", title="Circles in the sky",
         engine="skia starfield (seeded) + Manim (two-circle geocentric Mars, computed)",
         why="A short history aside that proves the drawing idea is old and real. **First cut candidate** if needed.",
         beats=[
        ("very old", "The stage becomes a night sky. A small Earth dot at center", "1.0 s"),
        ("astronomers", "A faint Mars dot wanders across the stars", "0.8 s"),
        ("circles riding on circles", "Two circles appear (Mars orbit − Earth orbit). The planet traces **retrograde loops** in gold", "3.0 s"),
        ("wrong about how the sky works", "Aside: the view re-centers on the Sun; the loops untangle into plain orbits, then re-center back", "1.5 s"),
        ("right about the circles", "The rims brighten", "0.6 s"),
        ("almost any path", "The stars fade out; the gold loops remain on black", "0.8 s"),
    ]),
    dict(slug="16_direction", cls="Scene16Direction", part="CH4", title="Plus, minus, zero",
         engine="Manim",
         why="Introduces the color code for direction before it is needed.",
         beats=[
        ("direction matters", "Stage clears to three empty slots", "0.4 s"),
        ("counterclockwise", "Left: a circle turning counterclockwise, blue rim", "0.8 s"),
        ("positive speed", "Label `+1`", "0.4 s"),
        ("clockwise", "Middle: one turning clockwise, orange rim", "0.8 s"),
        ("negative speed", "Label `−1`", "0.4 s"),
        ("speed zero", "Right: a green arm that doesn't turn. Label `0`", "0.6 s"),
        ("where the drawing sits", "The green arm stretches and swings, and a small gold loop on its tip moves with it: it only places the drawing", "1.2 s"),
    ]),
    dict(slug="17_rounded_square", cls="Scene17RoundedSquare", part="CH4", title="The friendly example",
         engine="Manim (`EpicycleChain`) + small `EpicyclePlate` still for the inset",
         why="Plants the example that the sanity check in S22 pays off (P6), and partly answers P1.",
         beats=[
        ("friendly example", "The stage clears to center", "0.6 s"),
        ("big circle", "A blue circle, r = 1, speed +1", "0.8 s"),
        ("one ninth", "An orange circle, r = 1/9, on its tip. A violet arc marks its **half-turn** start", "0.8 s"),
        ("backward three times", "The small circle spins clockwise, three times as fast", "—"),
        ("rounded square", "The pen traces the rounded square in gold", "4 s loop"),
        ("square from the beginning", "The intro square appears as a dashed ghost around it", "0.8 s"),
        ("first two circles", "An inset of the intro's square chain lights its first two circles: the same two", "0.8 s"),
    ]),
    dict(slug="18_rack", cls="Scene18Rack", part="CH4", title="Every whole number speed",
         engine="Manim (`SpectrumStrip` as an empty \"speed rack\")",
         why="States the real question with an empty slot for every answer (open loop).",
         beats=[
        ("every whole number speed", "The rounded square moves up. Below it, a row of **empty dashed slots** for speeds", "0.8 s"),
        ("zero", "Slots get their labels in time with the words: 0, 1, −1, 2, −2 …", "`LaggedStart` across the list"),
        ("and so on", "More slots fade in toward both edges", "0.6 s"),
        ("its size", "Each slot shows a faint empty radius knob", "0.5 s"),
        ("starting angle", "… and a faint violet angle tick", "0.5 s"),
        ("real question", "Everything dims except the rack", "0.6 s"),
        ("hand you a drawing", "The treble clef ghost slides in above the rack", "0.8 s"),
        ("every circle", "All slots pulse once, still empty", "0.6 s"),
    ]),
    # ───────────────────────── CH5 ─────────────────────────
    dict(slug="19_balance", cls="Scene19Balance", part="CH5", title="Speed zero is the balance point",
         engine="Manim",
         why="Warm-up case first. The averaging picture is built before any formula.",
         beats=[
        ("warm up", "Eyebrow **05 · SPIN AND AVERAGE**. The rack's slot `0` lights green", "0.6 s"),
        ("never moves", "A still green arm from the origin", "0.6 s"),
        ("center of the drawing", "The **bean** loop (gold) appears, offset from the origin", "1.0 s"),
        ("squiggly shape", "The bean wobbles once; a dim `?` ping at its middle", "0.6 s"),
        ("spread dots", "The pen goes around once and drops 60 gold dots, evenly in time (denser where it moves slowly)", "2.0 s"),
        ("average all their positions", "Every dot sends a faint line to their mean; the dots slide in and merge into the **green balance point**", "`LaggedStart` 1.2 s"),
        ("balance point", "The green dot pulses. The green arm stretches from the origin to it: an exact match", "0.8 s"),
        ("every other circle", "The bean's other four arms appear faintly, spinning", "0.6 s"),
        ("averages out to nothing", "Inset: one spinning arm drops 12 dots around a circle; their average sits exactly at the center, grey", "1.2 s"),
    ]),
    dict(slug="20_rule", cls="Scene20Rule", part="CH5", title="Spin averages to zero",
         engine="Manim",
         why="States the key idea as two icons and keeps them on screen (rule 6).",
         beats=[
        ("key idea", "Stage clears", "0.4 s"),
        ("things that spin", "Left icon: a spinning arm whose dots average to the center (grey)", "0.6 s"),
        ("stand still", "Right icon: a still arm whose dots all sit at its tip, so the average is the tip (green)", "0.6 s"),
        ("dont", "Both icons shrink into a small **rule card** docked bottom-left for the rest of Ch5", "0.6 s"),
    ]),
    dict(slug="21_freeze", cls="Scene21Freeze", part="CH5", title="Turn the drawing backward",
         engine="Manim (`EpicycleChain(rotating_frame=1)`)",
         why="The one idea of the video, shown rather than stated (rule 14): the camera turns, and the matching circle stops.",
         beats=[
        ("speed one circle", "The bean's 5-arm chain is drawn. The speed-1 arm gets a soft highlight", "0.6 s"),
        ("cant see it", "Its dots average to nothing: a grey ping at the center", "0.6 s"),
        ("stand still", "The speed-1 arm glows briefly (the hope)", "0.4 s"),
        ("heres the trick", "Hold. The pen keeps going round", "—"),
        ("turn the whole drawing backward", "The **whole stage rotates clockwise**, one turn per loop. A thin orange ring with an arrow at the stage edge shows the backward turn", "4 s loop"),
        ("so it stops", "In the turning view, the speed-1 arm **freezes**. It turns green and its glow steadies", "0.6 s"),
        ("still spinning", "The other arms keep spinning; their labels update: 0 → −1, +2 → +1, −1 → −2, −2 → −3", "0.8 s"),
        ("wash out", "The dots, now wound into a new shape, collapse to their average: a green point exactly at the frozen arm's tip", "1.4 s"),
        ("frozen in place", "A silver radius bracket and violet angle arc on the frozen arm. Rack slot `1` fills", "0.6 s"),
    ]),
    dict(slug="22_check", cls="Scene22Check", part="CH5", title="Sanity check",
         engine="Manim (rounded square, speed dial, `SpectrumStrip`)",
         why="A case where the viewer already knows the answer (P6).",
         beats=[
        ("sanity check", "The rounded square from S17 returns. A small **speed dial** sits top-center", "0.8 s"),
        ("backward once", "Dial → 1. The stage turns backward and the dots wind", "1.4 s"),
        ("tip of the big circle", "The average lands on the big circle's tip (green). Rack bar `1` rises to 1 (blue)", "1.0 s"),
        ("forward three times", "Dial → −3. The stage turns forward three times per loop", "1.4 s"),
        ("one ninth", "The average lands **1/9 from center, pointing the opposite way** (violet half-turn arc). Bar `−3` rises to 1/9 (orange)", "1.0 s"),
        ("just as it should", "Both bars pulse green once", "0.4 s"),
        ("speed two", "Dial → 2. The stage spins", "1.2 s"),
        ("falls to zero", "The average lands at the center: a grey ping", "0.8 s"),
        ("no circle there", "Slot `2` stays empty and dims", "0.4 s"),
    ]),
    dict(slug="23_recipe", cls="Scene23Recipe", part="CH5", title="Spin, then average",
         engine="Manim (`MathTex` with per-term color)",
         why="Pays off P2: the muted line from the intro returns to its exact spot and gets its colors in two steps.",
         beats=[
        ("just one idea", "Everything dims except the rule card, which slides to center and grows", "0.8 s"),
        ("spin the drawing against it", "Card: a turning stage (orange ring)", "0.6 s"),
        ("take the average", "Card: dots collapsing into a green point. Hold", "0.6 s"),
        ("line from the beginning", "The card returns to its corner. The muted formula fades in at `RECIPE_POS` (same spot as S03), then glides to center", "0.8 s + 0.8 s"),
        ("c n", "`c_n` turns green", "0.4 s"),
        ("integral", "`∫₀¹ … dt` turns silver", "0.4 s"),
        ("f of t", "`f(t)` turns gold", "0.4 s"),
        ("e to the minus", "`e^{−2πint}` turns orange", "0.4 s"),
        ("two steps", "Two brackets under the formula: ① under `f(t) e^{−2πint}`, ② under `∫₀¹ … dt`", "0.6 s"),
        ("pens position", "`f(t)` lifts; a tiny inset of the pen on the bean appears beside it", "0.8 s"),
        ("turns the drawing backward", "A small clockwise arrow icon beside `e^{−2πint}`", "0.6 s"),
        ("n times per loop", "The `n` inside it pulses blue", "0.4 s"),
        ("complex numbers", "Callback inset: video 001's quarter-turn arrow on the unit circle, spinning", "0.6 s in, 0.6 s out"),
        ("takes the average", "Bracket ② and `∫₀¹ … dt` brighten. The mini inset shows dots collapsing to their mean", "1.0 s"),
        ("spin then average", "Insets fade; the formula glows once and a light sweep crosses it", "1.0 s"),
        ("all it says", "Hold", "—"),
    ]),
    # ───────────────────────── CH6 ─────────────────────────
    dict(slug="24_compute", cls="Scene24Compute", part="CH6", title="Two hundred and one circles",
         engine="Manim (dots, dial, strip) → `EpicyclePlate` (chain)",
         why="Bars become circles: the transform that ties \"the list\" to \"the machine\" (rule 9).",
         beats=[
        ("real test", "Eyebrow **06 · DRAWING ANYTHING**. The formula shrinks to top-right and stays", "0.8 s"),
        ("treble clef", "The clef outline appears as a silver ghost", "0.8 s"),
        ("one continuous line", "A spark runs along the whole outline once", "1.2 s"),
        ("thousand dots", "1,000 gold dots sprinkle along it", "1.0 s"),
        ("minus one hundred", "The dial counter sweeps −100 → 100. Behind it the dot cloud spins, and the `SpectrumStrip` fills bar by bar", "until `spin and average`"),
        ("two hundred and one", "The strip lands complete: 201 bars, blue and orange", "0.4 s"),
        ("biggest to smallest", "The bars **re-order** by height, biggest first", "1.2 s"),
        ("tip to tail", "Each bar lifts off, curls into a circle of that radius, and snaps onto the end of the growing chain", "`LaggedStart` 1.6 s"),
    ]),
    dict(slug="25_converge", cls="Scene25Converge", part="CH6", title="One, five, twenty, two hundred",
         engine="`EpicyclePlate` + `InkParticles`",
         why="The spectacle rebuilt from scratch (P5), with the counter locked to the spoken numbers.",
         beats=[
        ("one circle", "Counter **1**. The chain is just the biggest circle; the pen traces a plain loop", "1.6 s loop"),
        ("five", "**5**: a rough blob. The previous ink stays as a faint ghost", "1.6 s"),
        ("twenty", "**20**: the clef starts to read", "1.6 s"),
        ("two hundred", "**200** (all 201): the chain traces the clef almost perfectly, sparks shedding; the ghost outline sits exactly under it", "3.0 s"),
        ("up close", "The camera dives **40×** onto the pen and follows it. The last dozen tiny circles whirl visibly; the ink stays crisp", "1.6 s `smooth`"),
        ("the others cant", "Toggle: the last 50 circles switch off and the ink at this zoom goes visibly wrong (a smoothed corner); they switch back and the detail returns. Pull back", "0.3 + 0.8 + 0.3 s"),
    ]),
    dict(slug="26_smooth_sharp", cls="Scene26SmoothSharp", part="CH6", title="Why sharp corners are expensive",
         engine="Manim",
         why="Pays off P4 and P1: two squares compared side by side.",
         beats=[
        ("remember", "The red corner marker from S10 (top-right) pulses and flies to center", "0.8 s"),
        ("first few circles", "The clef drawn with 10 circles: its smooth arcs light up, already right", "1.0 s"),
        ("all the rest", "Its sharp turns flash red: still rough", "0.6 s"),
        ("pen jumps", "Left panel: the square wave with its strip", "0.8 s"),
        ("one third", "`⅓` writes above bar 3", "0.4 s"),
        ("one fifth", "`⅕` above bar 5", "0.4 s"),
        ("turns a corner", "Right panel: the square loop and its strip; its bars drop off visibly faster", "0.8 s"),
        ("one ninth", "`1/9`", "0.4 s"),
        ("one twenty fifth", "`1/25`", "0.4 s"),
        ("fewer circles", "A third mini panel: a smooth oval loop whose strip has only 3 bars. The red marker dissolves (promise kept)", "1.0 s"),
    ]),
    dict(slug="27_everywhere", cls="Scene27Everywhere", part="CH6", title="Sound and pictures",
         engine="Manim (synthetic waveforms and spectra) + skia piano keys + scipy DCT + skia image tiles",
         why="Pays off the piano chord (P7) and shows the idea in everyday technology.",
         beats=[
        ("everywhere", "The chain shrinks into a small icon at top-left", "0.6 s"),
        ("piano chord", "The intro's three keys and merging waves return (callback)", "0.6 s in"),
        ("sound is a wave", "The gold chord waveform slides left and becomes the start of a longer sound wave", "0.8 s"),
        ("singer and a violin", "Two stacked waveforms (synthetic, seeded: same fundamental, different harmonic recipes), each with its strip on the right", "1.0 s"),
        ("slowest circle", "The first bar of both strips lights up: same speed, aligned", "0.6 s"),
        ("faster circles on top", "Their other bars differ and glow", "0.6 s"),
        ("shrink photos", "An image (a frame of this video's own clef render) splits into an 8×8 block grid", "1.0 s"),
        ("keeping the big circles", "A threshold line sweeps across one block's coefficient bars; small ones fall away", "1.0 s"),
        ("wont notice", "The image re-forms from about 10 % of its coefficients (real `scipy.fft.dctn`). A thin wipe compares it to the original: nearly the same", "1.4 s"),
    ]),
    # ───────────────────────── OUTRO ─────────────────────────
    dict(slug="28_recap", cls="Scene28Recap", part="OUTRO", title="What we built",
         engine="Manim + skia glass cards (`cards.py`)",
         why="Each recap sentence is a visual callback, not a spoken list (rule 17).",
         beats=[
        ("step back", "Pull back; four empty glass cards fade up in a row", "`LaggedStart` 0.8 s"),
        ("simplest wave", "Card 1 plays live: circle → sine, with the three chips", "0.8 s"),
        ("stack circles", "Card 2: stacked circles", "0.8 s"),
        ("sharp corners", "… building a square wave with its sharp corners", "0.6 s"),
        ("fouriers insight", "Card 3 lights", "0.4 s"),
        ("two directions", "Card 3: a chain drawing the rounded square", "0.8 s"),
        ("spin the drawing backward", "Card 4: a turning stage and a frozen green arm. The recipe in full color writes under the cards", "0.8 s"),
        ("stands still", "Card 4's frozen arm glows green", "0.4 s"),
        ("looking for", "All four cards glow once", "0.6 s"),
    ]),
    dict(slug="29_teaser", cls="Scene29Teaser", part="OUTRO", title="What comes next",
         engine="Manim",
         why="Honest look ahead (P8) without opening anything this video can't keep.",
         beats=[
        ("quietly assumed", "The cards fade", "0.6 s"),
        ("drawings repeat", "A pen finishes a loop", "0.8 s"),
        ("where it started", "It lands on its start point, which pings: the loop closes", "0.4 s"),
        ("never repeats", "A gold sound wave with no repeating pattern (deterministic chirp with a noise envelope) scrolls past", "1.2 s"),
        ("every possible speed", "The integer speed rack's separate bars **melt together** into one continuous glowing band", "1.4 s"),
        ("fourier transform", "\"Fourier transform\" in small Space Grotesk under the band, with a light sweep", "0.8 s"),
        ("go next", "The band drifts off and fades to black", "0.8 s"),
    ]),
    dict(slug="30_finale", cls="Scene30Finale", part="OUTRO", title="Just circles, going round",
         engine="`EpicyclePlate` in **2.5D** (plane tilted ~25°, slow yaw orbit, rims in perspective, soft floor reflection) + `InkParticles`",
         why="Ends on the payoff (rule 19): the opening image, now understood.",
         beats=[
        ("@0", "The 201-circle clef chain fades up from black and the plane tilts into perspective", "1.2 s"),
        ("for now", "The pen starts its loop. Period = `FINALE_LOOP`, so it closes as \"round\" ends", "`linear`, ease out on the last 0.4 s"),
        ("one more time", "Camera yaw orbit begins", "continuous"),
        ("end:round", "The clef closes. A soft flash runs along the outline", "0.4 s"),
        ("thanks for watching", "The chain fades; the gold clef holds, glowing, and the sparks settle", "0.8 s"),
        ("end:watching", "Fade to black, landing on the last frame of the audio", "to the end"),
    ]),
]


# ── derived timings the scenes use ────────────────────────────────────────
def derived() -> dict[str, float]:
    s01_close = CUT_FRAMES[1] / FPS
    fin_start = cue.at("for now", after=600)
    fin_close = cue.end_of("round", after=fin_start)
    return {
        "CLEF_LOOP_S01": s01_close - 0.0,
        "CLEF_S01_AT_WORD": (cue.at("treble clef") - 0.0) / s01_close,
        "FINALE_LOOP": fin_close - fin_start,
        "FINALE_START": fin_start,
        "FINALE_CLOSE": fin_close,
        "VOICE_END": cue.end_of("watching", after=600),
    }


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:05.2f}"


def resolve(sc: dict, problems: list[str]) -> list[tuple[float, str, str, str]]:
    out, last = [], sc["t0"]
    for key, what, anim in sc["beats"]:
        if key == "@0":
            t, key_s = sc["t0"], "(frame 0)"
        else:
            end = key.startswith("end:")
            k = key[4:] if end else key
            after = max(sc["t0"] - 0.3, last + 1e-3) if out else sc["t0"] - 0.3
            try:
                if end:                    # first occurrence that ends at or after the last beat
                    a = sc["t0"] - 0.3
                    while (t := cue.end_of(k, after=a)) < last:
                        a = cue.at(k, after=a) + 1e-3
                else:
                    t = cue.at(k, after=after)
            except KeyError:
                problems.append(f"{sc['cls']}: {key!r} not found after {after:.2f}")
                t = float("nan")
            key_s = f"end of `{k}`" if end else f"`{k}`"
            if not (sc["t0"] - 0.3 <= t <= sc["t1"]):
                problems.append(f"{sc['cls']}: {key!r} at {t:.2f} outside {sc['t0']:.2f}-{sc['t1']:.2f}")
            if t + 1e-6 < last:
                problems.append(f"{sc['cls']}: {key!r} at {t:.2f} before previous beat {last:.2f}")
        last = t
        out.append((t, key_s, what, anim))
    return out


def main(out=sys.stdout) -> None:
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(AUDIO)],
        capture_output=True, text=True, check=True).stdout)
    assert abs(dur - AUDIO_END) < 1e-3, dur
    assert len(SCENES) == len(CUT_FRAMES) - 1, (len(SCENES), len(CUT_FRAMES))

    problems: list[str] = []
    w = out.write
    for i, sc in enumerate(SCENES):
        sc["t0"], sc["t1"] = CUT_FRAMES[i] / FPS, CUT_FRAMES[i + 1] / FPS
    resolved = [resolve(sc, problems) for sc in SCENES]

    w("## Scene slices (60 fps, every cut on a frame inside a real silence)\n\n")
    w("| # | Part | File · class | Range (s) | Frames | Length | Cut silence |\n|---|---|---|---|---|---|---|\n")
    for i, sc in enumerate(SCENES):
        f0, f1 = CUT_FRAMES[i], CUT_FRAMES[i + 1]
        sil = CUT_SILENCES[i] if i < len(CUT_SILENCES) else None
        sil_s = f"{sil[0]:.2f}–{sil[1]:.2f}" if sil else "— (end of audio)"
        w(f"| {i+1:02d} | {sc['part']} | `scene_{sc['slug']}.py` · `{sc['cls']}` | "
          f"{sc['t0']:.3f} – {sc['t1']:.3f} | {f0} – {f1} | {sc['t1']-sc['t0']:.1f} s | {sil_s} |\n")
    w(f"\nTotal: **{END_FRAME} frames = {END_FRAME/FPS:.3f} s** (audio {AUDIO_END:.3f} s).\n\n")

    w("### Derived timings (from `derived()`)\n\n| Name | Value |\n|---|---|\n")
    for k, v in derived().items():
        w(f"| `{k}` | {v:.3f} |\n")
    w("\n### Math check (`verify_math()`, run on every regenerate)\n\n")
    for f in verify_math():
        w(f"- {f}\n")
    w("\n---\n")

    part = None
    for i, (sc, beats) in enumerate(zip(SCENES, resolved)):
        if sc["part"] != part:
            part = sc["part"]
            w(f"\n## {part}\n")
        w(f"\n### SCENE {i+1:02d} · {sc['title']} · {sc['t0']:.3f}–{sc['t1']:.3f} "
          f"({mmss(sc['t0'])}–{mmss(sc['t1'])}, {sc['t1']-sc['t0']:.1f} s)\n\n")
        w(f"**Engine:** {sc['engine']}  \n**Why it works:** {sc['why']}\n\n")
        w("| t | Cue key | What happens | Anim (start = t − 0.15 unless noted) |\n|---|---|---|---|\n")
        for t, key_s, what, anim in beats:
            w(f"| {t:.2f} | {key_s} | {what} | {anim} |\n")

    if problems:
        sys.stderr.write("PROBLEMS:\n  " + "\n  ".join(problems) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
