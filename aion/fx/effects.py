"""Built-in effects. Use on a layer (`fx=[Glow(...)]`, `m.fx(...)`) or the whole frame (`s.fx(...)`).

    Bloom(strength=0.35, threshold=0.8, radius=5)     # dual-Kawase, energy-preserving
    Glow(color=C.accent, strength=1.2, radius=4)      # halo around a layer's shapes
    Blur(radius=3)                                    # soft focus / depth (animate radius)
    Grade(exposure=0, contrast=1.05, saturation=1.0, lift=0, gamma=1, gain=1, lut="file.cube")
    Vignette(0.25), Grain(0.025), ChromaticAberration(0.3)
    ZoomBlur(amount=0.15, center=(0.5, 0.5))          # transitions / impact
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from aion.comp.comp import hex_to_linear
from aion.fx.base import Effect, gpu_pass
from aion.gpu import pool

__all__ = ["Bloom", "Glow", "Blur", "Grade", "Vignette", "Grain", "ChromaticAberration", "Lens", "ZoomBlur", "Tonemap",
           "kawase_blur"]


def _half(size, k=1):
    return (max(1, size[0] >> k), max(1, size[1] >> k))


def kawase_blur(src_rt, levels: int, prefilter: dict | None = None):
    """Downsample `levels` times then upsample back to half-res-of-source. Returns pooled rt."""
    size = src_rt.size
    chain = []
    cur = src_rt
    for i in range(1, levels + 1):
        s = _half(size, i)
        if i == 1 and prefilter is not None:
            nxt = gpu_pass("fx/prefilter.frag", s, u_src=(cur.tex, 0), u_texel=(1 / cur.size[0], 1 / cur.size[1]),
                           **prefilter)
        else:
            nxt = gpu_pass("fx/kawase_down.frag", s, u_src=(cur.tex, 0),
                           u_texel=(1 / cur.size[0], 1 / cur.size[1]))
        chain.append(nxt)
        cur = nxt
    for i in range(len(chain) - 1, 0, -1):
        dst = chain[i - 1]
        up = gpu_pass("fx/kawase_up.frag", dst.size, u_src=(chain[i].tex, 0), u_base=(dst.tex, 1), u_base_w=1.0,
                      u_texel=(0.5 / chain[i].size[0], 0.5 / chain[i].size[1]))
        pool.release(chain[i])
        pool.release(dst)
        chain[i - 1] = up
    return chain[0]


def _levels(radius: float) -> int:
    return int(np.clip(round(radius), 1, 7))


class Bloom(Effect):
    """Highlights bleed light (dual-Kawase pyramid).

    Example:
        s.fx(Bloom(0.35, threshold=0.7))
    """

    def __init__(self, strength=0.35, threshold=0.8, knee=0.4, radius=5, tint="#ffffff"):
        super().__init__(strength=strength, threshold=threshold, knee=knee, radius=radius)
        self.tint = hex_to_linear(tint)

    def apply(self, rt, t, rc):
        k = float(self.p("strength", t))
        if k <= 0:
            return rt
        blur = kawase_blur(rt, _levels(self.p("radius", t)),
                           dict(u_threshold=float(self.p("threshold", t)), u_knee=float(self.p("knee", t))))
        out = gpu_pass("fx/add.frag", rt.size, u_a=(rt.tex, 0), u_b=(blur.tex, 1), u_k=k, u_tint=self.tint,
                       u_alpha_w=0.0)
        pool.release(blur)
        return out


class Tonemap(Effect):
    """ACES filmic curve for HDR content (bright disks, bloom): highlights roll off, black stays black.

    Example:
        s.fx(Bloom(0.05, threshold=0.9), Tonemap(exposure=0.0))
    """

    def __init__(self, exposure=0.0):
        super().__init__(exposure=exposure)

    def apply(self, rt, t, rc):
        return gpu_pass("fx/tonemap.frag", rt.size, u_src=(rt.tex, 0), u_exposure=float(self.p("exposure", t)))


class Glow(Effect):
    """Coloured halo from the layer's own shapes (neon / emphasis).

    Example:
        m = s.manim(fx=[Glow(C.accent, strength=1.5, radius=4)])
    """

    def __init__(self, color=None, strength=1.0, radius=4):
        super().__init__(strength=strength, radius=radius)
        self.color = None if color is None else hex_to_linear(color)

    def apply(self, rt, t, rc):
        k = float(self.p("strength", t))
        if k <= 0:
            return rt
        src = gpu_pass("fx/glow_src.frag", rt.size, u_src=(rt.tex, 0), u_color=self.color or (1, 1, 1),
                       u_use_color=int(self.color is not None))
        blur = kawase_blur(src, _levels(self.p("radius", t)))
        pool.release(src)
        out = gpu_pass("fx/add.frag", rt.size, u_a=(rt.tex, 0), u_b=(blur.tex, 1), u_k=k, u_tint=(1, 1, 1),
                       u_alpha_w=1.0)
        pool.release(blur)
        return out


class Blur(Effect):
    """Gaussian-like blur; radius 0 = off (animate for focus pulls).

    Example:
        Blur(radius=key(T.focus, 3, 0))
    """

    def __init__(self, radius=2.0):
        super().__init__(radius=radius)

    def apply(self, rt, t, rc):
        r = float(self.p("radius", t))
        if r <= 0.05:
            return rt
        lv = max(1, int(np.ceil(r)))
        blur = kawase_blur(rt, lv)
        up = gpu_pass("fx/kawase_up.frag", rt.size, u_src=(blur.tex, 0), u_base=(blur.tex, 1), u_base_w=0.0,
                      u_texel=(0.5 / blur.size[0], 0.5 / blur.size[1]))
        pool.release(blur)
        frac = r / lv
        if frac >= 0.999:
            return up
        out = _mix(rt, up, frac)
        pool.release(up)
        return out


_MIX = """
uniform sampler2D u_a; uniform sampler2D u_b; uniform float u_k; in vec2 v_uv; out vec4 frag;
void main() { frag = mix(texture(u_a, v_uv), texture(u_b, v_uv), u_k); }
"""


def _mix(a, b, k):
    return gpu_pass(_MIX, a.size, u_a=(a.tex, 0), u_b=(b.tex, 1), u_k=k)


def load_cube(path: str | Path) -> tuple[np.ndarray, int]:
    """Parse a .cube 3D LUT → (N,N,N,3) float32 array indexed [b][g][r] and N."""
    n, rows = 0, []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("LUT_3D_SIZE"):
            n = int(line.split()[1])
        elif line[0].isdigit() or line[0] in "-.":
            rows.append([float(x) for x in line.split()[:3]])
    a = np.asarray(rows, np.float32).reshape(n, n, n, 3)
    return a, n


class Grade(Effect):
    """Primary colour grade in linear light, optional .cube LUT.

    Example:
        Grade(contrast=1.08, saturation=0.95, gain=(1.0, 0.98, 0.95), lut="assets/luts/teal.cube")
    """

    def __init__(self, exposure=0.0, contrast=1.0, saturation=1.0, lift=0.0, gamma=1.0, gain=1.0,
                 tint=(1.0, 1.0, 1.0), lut: str | None = None, lut_mix=1.0):
        super().__init__(exposure=exposure, contrast=contrast, saturation=saturation, lift=lift, gamma=gamma,
                         gain=gain, tint=tint, lut_mix=lut_mix if lut else 0.0)
        self.lut_path = lut
        self._lut = None

    def _lut_tex(self):
        from aion.gpu.context import gl

        if self._lut is None:
            if self.lut_path:
                a, n = load_cube(self.lut_path)
                self._lut = (gl().texture3d((n, n, n), 3, a.astype("f4").tobytes(), dtype="f4"), n)
            else:
                self._lut = (gl().texture3d((2, 2, 2), 3, np.zeros(24, "f4").tobytes(), dtype="f4"), 2)
        return self._lut

    def apply(self, rt, t, rc):
        def v3(name):
            return np.broadcast_to(np.asarray(self.p(name, t), dtype=float), (3,)).tolist()

        tex, n = self._lut_tex()
        return gpu_pass("fx/grade.frag", rt.size, u_src=(rt.tex, 0), u_exposure=float(self.p("exposure", t)),
                        u_contrast=float(self.p("contrast", t)), u_saturation=float(self.p("saturation", t)),
                        u_lift=v3("lift"), u_gamma=v3("gamma"), u_gain=v3("gain"), u_tint=v3("tint"),
                        u_lut=(tex, 1), u_lut_mix=float(self.p("lut_mix", t)), u_lut_size=float(n))


class Lens(Effect):
    """Vignette + chromatic aberration + grain in one pass (cheapest finish).

    Example:
        s.fx(Lens(vignette=0.3, grain=0.02, ca=0.1))
    """

    def __init__(self, vignette=0.0, ca=0.0, grain=0.0, grain_size=1.0, roundness=1.0):
        super().__init__(vignette=vignette, ca=ca, grain=grain, grain_size=grain_size, roundness=roundness)

    @property
    def animated(self):
        return float(self.params["grain"](0)) > 0 or self.params["grain"].active != []

    def apply(self, rt, t, rc):
        return gpu_pass("fx/lens.frag", rt.size, u_src=(rt.tex, 0), u_res=rt.size,
                        u_vignette=float(self.p("vignette", t)), u_vig_round=float(self.p("roundness", t)),
                        u_ca=float(self.p("ca", t)), u_grain=float(self.p("grain", t)),
                        u_grain_size=float(self.p("grain_size", t)), u_frame_index=float(rc.frame_index))


def Vignette(amount=0.25, roundness=1.0) -> Lens:
    """Darken the frame edges (draws the eye to the centre).

    Example:
        s.fx(Vignette(C.vignette))
    """
    return Lens(vignette=amount, roundness=roundness)


def Grain(amount=0.025, size=1.0) -> Lens:
    """Film grain, deterministic per frame index.

    Example:
        s.fx(Grain(C.grain))
    """
    return Lens(grain=amount, grain_size=size)


def ChromaticAberration(amount=0.3) -> Lens:
    """RGB fringing toward the edges (use sparingly: impact moments).

    Example:
        s.fx(ChromaticAberration(pulse(T.hit, 0.6)))
    """
    return Lens(ca=amount)


class ZoomBlur(Effect):
    """Radial blur from `center` (uv). amount 0 = off; animate for whoosh transitions.

    Example:
        s.fx(ZoomBlur(amount=pulse(T.cut1, 0.25, dur=0.5)))
    """

    def __init__(self, amount=0.15, center=(0.5, 0.5), taps: int = 16):
        super().__init__(amount=amount)
        self.center, self.taps = center, taps

    def apply(self, rt, t, rc):
        a = float(self.p("amount", t))
        if a <= 1e-4:
            return rt
        return gpu_pass("fx/dir_blur.frag", rt.size, u_src=(rt.tex, 0), u_dir=(0, 0), u_radial=a,
                        u_center=self.center, u_taps=self.taps)
