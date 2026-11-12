"""BlackHoleLayer and Tonemap: the ray-traced frame has a black shadow, a bright disk and a mirror-free sky."""

import numpy as np
import pytest

from aion.comp.comp import Comp
from aion.fx.effects import Bloom, Tonemap
from aion.layers.blackhole import BlackHoleLayer, camera_basis

pytestmark = pytest.mark.gpu
W, H = 320, 180


def frame(**kw):
    comp = Comp((W, H), fps=30, background="#000000", fx=[Bloom(0.05, threshold=0.9), Tonemap()])
    comp.add(BlackHoleLayer(**{**dict(dist=30, inclination=84, azimuth=12), **kw}))
    return comp.frame(1.0)[..., :3].astype(float)


def test_camera_basis_is_orthonormal():
    pos, right, up, fwd = camera_basis(30, 84, 12, roll=5, yaw=3, pitch=2)
    M = np.stack([right, up, fwd])
    assert np.allclose(M @ M.T, np.eye(3), atol=1e-12) and abs(np.linalg.norm(pos) - 30) < 1e-12


def test_shadow_is_black_and_disk_is_bright():
    img = frame(sky="none", u_stars=0.0)
    assert img[H // 2 - 12, W // 2].max() < 3             # inside the shadow, above the disk's front band
    assert img.max() > 200                                # approaching side of the disk
    left, right = img[:, : W // 2].sum(), img[:, W // 2:].sum()
    assert left > 1.5 * right                             # Doppler beaming: one side is brighter


def test_photon_ring_sits_at_critical_impact_parameter():
    img = frame(sky="none", u_gas=0.0, u_stars=0.0, u_ring=1.0).sum(-1)
    yy, xx = np.mgrid[:H, :W]
    rad = np.hypot(xx + 0.5 - W / 2, yy + 0.5 - H / 2)
    r_px = float((rad * img).sum() / img.sum())           # brightness-weighted ring radius
    bc, r = np.sqrt(27.0), 30.0                           # apparent size: sin α = b_c √(1 − 2/r) / r
    expect = np.tan(np.arcsin(bc * np.sqrt(1 - 2 / r) / r)) / np.tan(np.radians(18)) * H / 2
    assert abs(r_px - expect) < 1.5, (r_px, expect)


def test_reveal_builds_top_down():
    img = frame(sky="none", u_stars=0.0, u_reveal=0.3)
    assert img[int(0.6 * H):].max() < 2 and img[: int(0.3 * H)].max() > 20


def test_disk_image_curve_lies_on_the_rendered_disk_edge():
    from aion.maths import schwarzschild as S

    pos, right, up, fwd = camera_basis(30, 84, 12)
    top = S.disk_image(19.0, pos, right, up, fwd, n=181)             # outer edge, direct image
    assert np.isfinite(top).all()
    apex = top[np.argmax(top[:, 1])]
    img = frame(sky="none", u_stars=0.0, u_ring=0.0).sum(-1)
    px = lambda p: (int(round(W / 2 + p[0] * H / 8)), int(round(H / 2 - p[1] * H / 8)))   # noqa: E731
    x, y = px(apex)
    assert abs(apex[0]) < 0.3 and apex[1] > 2.0                      # the far side arches over the top
    assert img[y + 6, x] > 30 and img[y - 6, x] < 12                 # disk just inside the curve, sky outside


def test_panel_mode_places_the_image_in_a_positioned_quad():
    comp = Comp((W, H), fps=30, background="#000000", fx=[Tonemap()])
    comp.add(BlackHoleLayer(dist=30, inclination=84, azimuth=12, sky="none", u_stars=0.0,
                            height=4.0, pos=(3.0, 0.0)))
    img = comp.frame(1.0)[..., :3].astype(float).sum(-1)
    assert img[:, : W // 4].max() < 3                          # nothing on the left of the frame
    cols = np.where(img.max(0) > 30)[0]
    left = W * (3.0 - 4.0 * 16 / 9 / 2 + 7.111) / 14.222           # the panel's left edge in pixels
    assert cols.min() >= left - 1 and cols.max() < W           # the disk lives inside the right-hand panel


def test_shader_defines_are_float_literals():
    # integer-looking defines make log(T_MAX / T_MIN) a log(int), which NVIDIA's GLSL compiler rejects
    import re

    from aion.layers.blackhole import _source

    for name, val in re.findall(r"^#define (\w+) (\S+)$", _source(), re.M):
        assert any(c in val for c in ".e"), f"{name} = {val} is an int literal"
