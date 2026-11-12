"""VoyageLayer: aion's ray-traced black hole with a deep sky around it and a planet in front of it.

It is `BlackHoleLayer` with `shaders/voyage_sky.glsl` spliced into the tracer: the extra sky objects are
looked up along each *lensed* ray, so the hole bends them like the stars. With `v_gain = 0` and
`v_plAmt = 0` the image is the stock layer's, pixel for pixel: that is how the last frame joins video 004.
"""
from pathlib import Path

import aion.layers.blackhole as bh
from aion import BlackHoleLayer
from aion.core.track import track
from aion.gpu.program import program, set_uniforms

_STOCK = bh._source
_EXTRA = Path(__file__).parent / "shaders" / "voyage_sky.glsl"
_MAIN = "void main() {"
_HOOK = "    if (u_reveal < 1.0) {"
_CALL = ("    if (sky && v_gain > 0.0) col += T * voyageSky(dOut, fp) * v_gain;\n"
         "    col = vPlanet(col, u_cam, d);\n")


def voyage_source() -> str:
    """The stock tracer plus the voyage sky (two anchors in the stock source, checked)."""
    src = _STOCK()
    if src.count(_MAIN) != 1 or src.count(_HOOK) != 1:
        raise RuntimeError("aion's blackhole.frag changed: update the anchors in voyage.py")
    return src.replace(_MAIN, _EXTRA.read_text() + "\n" + _MAIN).replace(_HOOK, _CALL + _HOOK)


class VoyageLayer(BlackHoleLayer):
    """BlackHoleLayer plus `v_*` uniforms (Tracks) for the voyage sky and planet, `u_sn*` for the supernova."""

    def __init__(self, **kw):
        names = [k for k in kw if k.startswith(("v_", "u_sn"))]
        self.extra = {k: track(kw.pop(k)) for k in names}
        super().__init__(**kw)

    def tracks(self):
        return super().tracks() + list(self.extra.values())

    def cache_key(self):
        return super().cache_key() + [voyage_source(), {k: v.label for k, v in self.extra.items()}]

    def draw(self, t, rc):
        set_uniforms(program(voyage_source()), **{k: v(t) for k, v in self.extra.items()})
        bh._source = voyage_source                # the stock draw() compiles whatever _source() returns
        try:
            return super().draw(t, rc)
        finally:
            bh._source = _STOCK
