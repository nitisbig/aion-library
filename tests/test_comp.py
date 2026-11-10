"""GPU compositor: colour math, blend modes, mattes, determinism, encode."""

import hashlib
import random

import numpy as np
import pytest

pytestmark = pytest.mark.gpu

from aion.comp.comp import Comp
from aion.core.track import key
from aion.layers.media import ArrayLayer
from aion.layers.shader import ShaderLayer
from aion.layers.solid import Gradient, Solid

W, H = 160, 90


def px(img, x=W // 2, y=H // 2):
    return img[y, x].astype(int)


def test_solid_roundtrip_srgb():
    img = Comp((W, H), background="#336699").frame(0)
    assert np.abs(px(img) - [0x33, 0x66, 0x99]).max() <= 1


def test_half_alpha_over_is_linear_light():
    rgba = np.zeros((10, 10, 4), np.uint8)
    rgba[..., 0], rgba[..., 3] = 255, 128                       # 50% red over black
    comp = Comp((W, H), background="#000000")
    comp.add(ArrayLayer(rgba, height=8))
    v = px(comp.frame(0))[0]
    lin = 128 / 255
    expect = 255 * (1.055 * lin ** (1 / 2.4) - 0.055)            # sRGB encode of 0.5 linear
    assert abs(v - expect) <= 2 and v > 180                     # not 128: linear compositing


@pytest.mark.parametrize("mode,expect", [("add", [255, 255, 0]), ("multiply", [0, 0, 0]),
                                         ("screen", [255, 255, 0]), ("difference", [255, 255, 0])])
def test_blend_modes(mode, expect):
    comp = Comp((W, H), background="#ff0000")
    comp.add(Solid("#00ff00", blend=mode))
    assert np.abs(px(comp.frame(0)) - expect).max() <= 2


def test_alpha_matte():
    m = np.zeros((90, 160, 4), np.uint8)
    m[:, :80, 3] = 255                                          # left half opaque
    comp = Comp((W, H), background="#000000")
    comp.add(Solid("#ffffff", matte=ArrayLayer(m, height=8), matte_mode="alpha"))
    img = comp.frame(0)
    assert px(img, 20)[0] > 250 and px(img, 140)[0] < 3


SHADER = """
#include "common/color.glsl"
uniform float u_time; uniform float u_k; in vec2 v_pos; out vec4 frag;
void main() { frag = vec4(0.5 + 0.5 * sin(v_pos.x * 3.0 + u_time * 2.0), u_k, 0.3, 1.0); }
"""


def build():
    comp = Comp((W, H), fps=30, background="#0d1117")
    comp.add(Gradient(z=-1))
    comp.add(ShaderLayer(SHADER, u_k=key(0.5, 0.0, 1.0, dur=0.5), opacity=0.7))
    comp.camera.push(0.6, zoom=1.3, dur=0.5)
    return comp


def test_frames_are_order_independent():
    """Same frame from a fresh comp, in order, or shuffled: identical bytes."""
    ts = [k / 30 for k in range(30)]
    seq = [hashlib.sha1(build().frame(t).tobytes()).hexdigest() for t in ts]  # fresh comps
    c = build()
    inorder = [hashlib.sha1(c.frame(t).tobytes()).hexdigest() for t in ts]
    order = list(range(30))
    random.Random(1).shuffle(order)
    c2 = build()
    shuffled = {k: hashlib.sha1(c2.frame(ts[k]).tobytes()).hexdigest() for k in order}
    assert seq == inorder == [shuffled[k] for k in range(30)]
    assert len(set(seq)) > 20                                   # it actually animates


def test_static_comp_reuses_frame():
    comp = Comp((W, H), background="#202020")
    comp.add(Solid("#ff0000", opacity=key(1.0, 0.0, 1.0, dur=0.5, lead=0)))
    a, b = comp.frame(0.1), comp.frame(0.3)
    assert a is b                                               # nothing changed: no GPU work
    assert comp.frame(1.2) is not b


def test_encoder_roundtrip(tmp_path):
    from aion.render.encode import Encoder

    comp = build()
    with Encoder(tmp_path / "a.mp4", (W, H), 30, codec="final") as enc:
        for k in range(15):
            enc.write(comp.frame(k / 30))
    import subprocess

    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames,color_space", "-of", "csv=p=0", str(tmp_path / "a.mp4")],
                         capture_output=True, text=True).stdout.strip()
    assert out.startswith("15") or out.endswith("15") and "bt709" in out
