"""End-to-end: a fixture video with two scenes → chunks → mux; resume; stills; fx."""

import subprocess
import sys
import textwrap

import numpy as np
import pytest

pytestmark = [pytest.mark.gpu]

VIDEO_PY = """
from aion import Video, BASE
video = Video(theme=BASE.extend(vec="#ff7a59"), fps=30, size=(256, 144))
"""
BEATS_PY = """
from aion import beats, cut, end
T = beats(fps=30, grid="a grid", arrow="arrow", c1=cut("stretches", "now watch"), arrow2="arrow")
"""
S01 = """
from aion import *
from beats import T

@scene(T.start, T.c1)
def s01_grid(s):
    s.gradient(C.bg2, C.bg)
    m = s.manim()
    m.add(NumberPlane(x_range=(-8, 8), y_range=(-5, 5)), at=T.start)
    v = Arrow(ORIGIN, [2, 1, 0], buff=0, color=C.vec)
    m.play(GrowArrow(v), at=T.arrow, dur=0.6)
    s.fx(Bloom(0.3), Vignette(0.3))
"""
S02 = """
from aion import *
from beats import T

@scene(T.c1, T.end)
def s02_again(s):
    s.shader("layers/domain_coloring.frag", z=-1, u_frame=(14.22, 8), u_origin=(0, 0), u_unit=1.5,
             u_theta=key(T.arrow2, 0.0, 1.5, dur=1.0), u_opacity=1.0, u_sat=0.7)
    m = s.manim(fx=[Glow(C.accent, strength=0.8)])
    m.play(Write(MathTex(r"e^{i\\theta}")), at=T.arrow2, dur=0.8)
    s.camera.push(T.arrow2, zoom=1.2, dur=1.0)
"""


@pytest.fixture
def demo(fixture_video):
    (fixture_video / "video.py").write_text(VIDEO_PY)
    (fixture_video / "beats.py").write_text(BEATS_PY)
    (fixture_video / "scenes" / "s01_grid.py").write_text(S01)
    (fixture_video / "scenes" / "s02_again.py").write_text(S02)
    return fixture_video


def aion(*args, cwd=None):
    r = subprocess.run([sys.executable, "-m", "aion.cli", *map(str, args)], capture_output=True, text=True,
                       cwd=cwd, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout + r.stderr


def test_beats_cli(demo):
    out = aion("beats", demo)
    assert "c1" in out and "2 scenes" in out


def test_still_and_layers(demo):
    out = aion("still", demo, "s02", "--at", "arrow2+0.9", "--res", "144", "--layers")
    pngs = [l for l in out.split() if l.endswith(".png")]
    assert len(pngs) == 3
    from PIL import Image

    img = np.asarray(Image.open(pngs[0]))
    assert img.shape == (144, 256, 3) and img.std() > 10


def test_render_mux_and_resume(demo):
    out = aion("render", demo, "--res", "144", "--fps", "15", "-j", "1")
    assert "✔" in out
    final = demo / "out" / "final.mp4"
    from aion.render.mux import probe_durations

    d = probe_durations(final)
    assert abs(d["video"] - 7.0) <= 1 / 15 + 1e-3 and abs(d["audio"] - d["video"]) < 0.05
    chunks = sorted((demo / "out" / ".chunks").rglob("*.mp4"))
    assert len(chunks) >= 4
    # resume: delete one chunk; only it is re-rendered
    chunks[1].unlink()
    out2 = aion("render", demo, "--res", "144", "--fps", "15", "-j", "1")
    assert chunks[1].exists() and "✔" in out2
