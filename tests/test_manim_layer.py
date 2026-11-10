"""ManimLayer: score evaluation, random access, parity with Manim's own camera."""

import hashlib

import numpy as np
import pytest

pytestmark = pytest.mark.gpu

manim = pytest.importorskip("manim")
from manim import BLUE, RED, Circle, Create, Camera, FadeIn, FadeOut, Square, Transform, VGroup

from aion.comp.comp import Comp
from aion.layers.manim import BackwardSeek, ManimLayer

W, H = 192, 108


def build():
    comp = Comp((W, H), fps=30, background="#101418")
    m = comp.add(ManimLayer())
    sq = Square(2, color=BLUE, fill_opacity=0.6)
    c = Circle(1.2, color=RED)
    m.play(Create(sq), at=1.0, dur=1.0, lead=0)
    m.play(Transform(sq, c), at=3.0, dur=1.0, lead=0)
    m.play(FadeOut(sq), at=5.0, dur=0.5, lead=0)
    dot = Circle(0.15, color=RED, fill_opacity=1)
    m.add(dot, at=0.5)
    m.drive(dot, lambda d, t: d.move_to([np.cos(t), np.sin(t), 0]), during=(0.5, 2.5))
    return comp, m, sq


def h(img):
    return hashlib.sha1(img.tobytes()).hexdigest()


def test_score_states():
    comp, m, sq = build()
    comp.frame(0.2)
    assert m.mobjects() == []
    comp.frame(1.5)
    assert sq in m.mobjects()
    comp.frame(5.7)
    assert sq not in m.mobjects()            # FadeOut is a remover


def test_random_forward_access_equals_sequential():
    ts = [k / 30 for k in range(0, 190, 3)]
    comp, *_ = build()
    seq = {t: h(comp.frame(t)) for t in ts}
    comp2, *_ = build()
    sparse = [t for i, t in enumerate(ts) if i % 4 == 0]      # big forward jumps
    assert all(h(comp2.frame(t)) == seq[t] for t in sparse)


def test_backward_seek_raises():
    comp, m, _ = build()
    comp.frame(3.0)
    with pytest.raises(BackwardSeek):
        m.advance(1.0)


def test_holds_skip_raster():
    comp, m, _ = build()
    calls = []
    orig = m.draw
    m.draw = lambda t, rc: (calls.append(t), orig(t, rc))[1]
    for k in range(int(4.5 * 30), int(4.9 * 30)):           # 4.5–4.9 s: nothing animates
        comp.frame(k / 30)
    assert len(calls) == 1


def test_parity_with_manim_camera():
    """Opaque content matches Manim's own Cairo render; AA edges differ only by linear-light blending."""
    sq = Square(3, color=BLUE, fill_opacity=1.0, stroke_width=6)
    cam = Camera(pixel_width=W, pixel_height=H, background_color="#101418")
    cam.capture_mobjects([sq])
    ref = cam.pixel_array[..., :3].astype(int)

    comp = Comp((W, H), fps=30, background="#101418")
    m = comp.add(ManimLayer())
    m.add(Square(3, color=BLUE, fill_opacity=1.0, stroke_width=6))
    ours = comp.frame(0).astype(int)
    diff = np.abs(ours - ref)
    assert diff[H // 2, W // 2].max() <= 1                    # interior identical
    assert diff.mean() < 1.0                                  # edges: small linear-vs-sRGB AA difference
