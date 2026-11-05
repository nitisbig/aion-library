"""Shared paths, scene ranges and layout for video 001 (complex numbers).

Scenes hand off to each other on identical frames, so anything that appears
across a cut (the number line, the glowing i) is built here, once.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import DOWN, PI, RIGHT, UP, Arc, Arrow, Axes, MathTex, VGroup, VMobject, always_redraw

from aion import style as S
from aion.components.glow import glow_halo
from aion.components.shader_plate import ShaderPlate
from aion.narration import NarratedScene

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio.mp3"
SRT = ROOT / "assets" / "cue-per-word.srt"

FPS = 60
# Scene boundaries in frames at 60 fps (cuts sit inside real silences, see storyboard).
CUTS = {
    "intro": (0, 570),
    "puzzle": (570, 1318),
    "quarter_turn": (1318, 2110),
    "plane": (2110, 2779),
    "outro": (2779, 3531),   # includes the approved 2.0 s silent tail
}


def scene_range(name: str) -> tuple[float, float]:
    a, b = CUTS[name]
    return a / FPS, b / FPS


# Pure black for every scene of this video (user request; channel default is S.BG).
BG = "#000000"


class VideoScene(NarratedScene):
    """Base for all scenes of video 001: narration audio, SRT and background."""
    AUDIO, SRT, BACKGROUND = AUDIO, SRT, BG


def domain_plate(theta, opacity, origin=(0.0, 0.0), unit=1.3) -> ShaderPlate:
    """Domain-coloring background. `theta` and `opacity` are ValueTrackers."""
    return ShaderPlate(
        "domain_coloring.frag",
        lambda: {"u_theta": theta.get_value(), "u_opacity": opacity.get_value(),
                 "u_origin": tuple(origin), "u_unit": unit, "u_sat": 0.8},
    ).set_z_index(-100)


def polar_arrow(origin, length, angle, opacity=1.0) -> Arrow:
    """Z arrow from `origin` with given length (Manim units) and angle."""
    tip = np.asarray(origin) + length * np.array([np.cos(angle), np.sin(angle), 0.0])
    a = z_arrow(origin, tip)
    a.set_opacity(opacity)
    return a


# ── number line / graph (intro → ch1) ─────────────────────────────
X_RANGE = (-3, 3, 1)
Y_RANGE = (-1.5, 4.5, 1)
X_LEN, Y_LEN = 7.8, 6.0                 # 1.3 units per x step, 1.0 per y step
GRAPH_ORIGIN = np.array([0.0, -2.05, 0.0])


def graph_axes() -> Axes:
    ax = Axes(
        x_range=X_RANGE, y_range=Y_RANGE, x_length=X_LEN, y_length=Y_LEN,
        tips=False,
        axis_config={"color": S.AXIS, "stroke_width": 2.5},
        x_axis_config={
            "include_numbers": True, "numbers_to_exclude": [0],
            "font_size": 30, "line_to_number_buff": 0.22,
        },
        y_axis_config={"numbers_to_exclude": [0], "include_ticks": True},
    )
    ax.shift(GRAPH_ORIGIN - ax.c2p(0, 0))
    ax.x_axis.numbers.set_color(S.MUTED)
    return ax


def number_line():
    """The intro's number line: the graph's x-axis, centered vertically."""
    nl = graph_axes().x_axis.copy()
    nl.shift(UP * -GRAPH_ORIGIN[1])
    return nl


def z_arrow(start, end) -> Arrow:
    return Arrow(start, end, buff=0, color=S.Z, stroke_width=S.VECTOR_STROKE,
                 max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=12)


# ── the glowing i (end of ch1 → start of ch2) ─────────────────────
I_GLYPH_POS = np.array([0.0, 0.75, 0.0])
I_EQ_POS = np.array([0.0, -1.35, 0.0])


def i_glyph() -> MathTex:
    return MathTex("i", font_size=230, color=S.I_UNIT).move_to(I_GLYPH_POS)


def i_halo(glyph: MathTex):
    return glow_halo(glyph, S.I_UNIT, core_sigma=0.07, bloom_sigma=0.38,
                     core_alpha=0.7, bloom_alpha=0.5)


def sq_eq(base: str, color) -> MathTex:
    """`<base>^2 = -1`, with the base colored and -1 in NEG."""
    m = MathTex(base, "^2", "=", "-1", font_size=64, color=S.TEXT)
    m[0].set_color(color)
    m[3].set_color(S.NEG)
    return m


def trailing_arc(origin, radius, theta, span=0.6 * PI):
    """Violet comet-tail arc behind a spinning arrow (bright at the arrow).

    `radius` is a callable (Manim units); `theta` a ValueTracker (radians, >= 0).
    """
    def make():
        th = theta.get_value()
        sp = min(th, span)
        if sp < 1e-3:
            return VMobject()
        arc = Arc(radius=radius(), start_angle=th - sp, angle=sp, arc_center=origin)
        arc.set_stroke(color=[S.I_UNIT, BG], width=5)
        return arc

    return always_redraw(make)
