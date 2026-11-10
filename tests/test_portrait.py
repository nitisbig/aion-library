"""Portrait (9:16) videos: quality presets follow Video.size and the Manim frame is 8 units wide."""
from aion.comp.comp import Comp
from aion.render.project import orient


def test_orient_follows_declared_size():
    assert orient((1920, 1080), (1080, 1920)) == (1080, 1920)
    assert orient((854, 480), (1080, 1920)) == (480, 854)
    assert orient((1080, 1920), (1080, 1920)) == (1080, 1920)      # idempotent
    assert orient((1920, 1080), (1920, 1080)) == (1920, 1080)      # landscape untouched


def test_portrait_frame_keeps_pixels_per_unit():
    land, port = Comp((1920, 1080), 30), Comp((1080, 1920), 30)
    assert land.frame_units[1] == 8.0
    assert abs(port.frame_units[0] - 8.0) < 1e-9
    assert abs(1920 / land.frame_units[0] - 1080 / port.frame_units[0]) < 1e-6   # same px per unit


def test_manim_layer_follows_camera_moves_when_rendered_sequentially():
    """Regression: Manim's Cairo camera caches its frame matrix; a moving aion camera must still move vector layers."""
    import numpy as np

    from aion import Dot, Scene  # noqa: F401  (names exist)
    from aion.layers.manim import ManimLayer
    from aion.comp.comp import Comp

    comp = Comp((270, 480), 30, background="#000000")
    layer = ManimLayer(parallax=1)
    layer.add(Dot([1.0, 1.0, 0], radius=0.3, color="#ffffff"))
    comp.add(layer)
    comp.camera.pan(2.0, to=(1.0, 1.0), dur=1.0, lead=0)
    xs = []
    for t in (1.0, 2.5, 3.5):                               # sequential frames: camera moves between them
        img = comp.frame(t, round(t * 30)).astype(float)
        m = img.sum(axis=2) > 300
        xs.append(np.nonzero(m)[1].mean())
    assert xs[0] > 150 > 0 and abs(xs[-1] - 135) < 3        # dot drifts to the frame centre once the camera sits on it


def test_eqn_part_returns_isolated_term():
    from aion import Eqn
    eq = Eqn(r"w \gets w - \eta\, \nabla L", colors={"w": "#ffd166", r"\eta": "#b794f6"})
    assert eq.part(r"\eta") is not None and eq.part("w", 1) is not eq.part("w", 0)
