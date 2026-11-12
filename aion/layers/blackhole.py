"""BlackHoleLayer: a non-spinning black hole, ray-traced through the Schwarzschild orbit equation.

Every pixel is a ray sent backwards from a pinhole camera. Its impact parameter b picks a row of
the lookup tables built by `aion.maths.schwarzschild` (u'' + u = 3u², units G = c = M = 1, so
r_s = 2), which say whether the ray falls in, hits the thin disk (r = 6…19, primary, secondary and
tertiary images) or escapes, and in which direction, to sample a lensed procedural sky.

    s.add(BlackHoleLayer(dist=key(T.push, 60, 30, dur=18), inclination=84, azimuth=ramp(a, b, -4, 22),
                         sky="galaxy", scale_res=2))
    s.fx(Bloom(C.bloom, threshold=0.9), Tonemap())

Camera (all Tracks): `dist` in M (≥ 20; interpolate it in log space for a steady sense of speed),
`inclination` degrees from the disk axis (90 = edge-on), `azimuth`, `roll`, `fov` (vertical, degrees),
`yaw`/`pitch` look offsets, `target_y`. `height=4.3, pos=(2.8, 0)` shows the image as a 16:9 panel of that
height (frame units) instead of full frame; `scale` and `pos` Tracks can then grow it to fill the frame.
`disk_t0` is the time at which the gas pattern is unsheared (keep (t − disk_t0)·disk_rate below a few
hundred or the Keplerian shear winds it into grooves). Any shader uniform can be driven too: `u_gas` (disk opacity),
`u_ring` (photon-ring emission), `u_stars`, `u_skyAmt`, `u_reveal` (0→1 builds the image top-down).
Output is linear HDR and opaque: follow with a small Bloom and `Tonemap()`.
"""

from __future__ import annotations

import numpy as np

from aion.core.track import track
from aion.gpu import gl, pool
from aion.gpu.program import fullscreen, load_source, program, set_uniforms
from aion.layers.base import ENC_LINEAR, Layer, RenderContext, Surface

__all__ = ["BlackHoleLayer"]

R_IN, R_OUT = 6.0, 19.0            # thin disk: innermost stable orbit to outer edge (M)
MAX_HEIGHT = 2592                  # tallest internal render target (px): 2× SSAA at 1080p, 1.2× at 4K
_SKY = {"none": 0.0, "grid": 1.0, "galaxy": 2.0}
_TEX: dict[str, object] = {}       # lookup tables, uploaded once per process


def _tables():
    if not _TEX:
        import moderngl

        from aion.maths import schwarzschild as S

        _, U, phi_end, _, PHC = S.load_tables()

        def up(arr, comps=1):
            arr = np.ascontiguousarray(arr, "f4")
            tex = gl().texture((arr.shape[1], arr.shape[0]), comps, arr.tobytes(), dtype="f4")
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)   # the shader interpolates (8-bit hw weights band)
            return tex

        _TEX.update(u=up(U), phc=up(PHC), end=up(phi_end[None, :]), bb=up(S.blackbody_table()[None, :, :], 3))
    return _TEX


def _glsl_float(v) -> str:
    """A GLSL float literal ('800' is an int: NVIDIA rejects log(int), Mesa converts it silently)."""
    s = f"{float(v):.10g}"
    return s if any(c in s for c in ".en") else s + ".0"


def _source() -> str:
    from aion.maths import schwarzschild as S

    d = {"B_C": S.B_C, "EPS": S.EPS, "Y0": S.Y0, "Y1": S.Y1, "PHI_MAX": S.PHI_MAX, "U_CMAX": S.U_CMAX,
         "NB": S.NB, "NPHI": S.NPHI, "NU": S.NU, "R_IN": R_IN, "R_OUT": R_OUT,
         "T_MIN": S.T_MIN, "T_MAX": S.T_MAX, "N_T": S.N_T}
    head = "#version 330\n" + "".join(f"#define {k} {_glsl_float(v)}\n" for k, v in d.items())
    return head + load_source("layers/blackhole.frag")


def _rot(v, axis, ang):
    axis = axis / np.linalg.norm(axis)
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))


def camera_basis(dist, inclination, azimuth, roll=0.0, yaw=0.0, pitch=0.0, target_y=0.0):
    """Camera position and (right, up, forward) for angles in degrees; the disk axis is +y.

    Example:
        pos, right, up, fwd = camera_basis(30, 84, 10)
    """
    inc, az, roll, yaw, pitch = np.radians([inclination, azimuth, roll, yaw, pitch])
    pos = dist * np.array([np.sin(inc) * np.cos(az), np.cos(inc), np.sin(inc) * np.sin(az)])
    fwd = np.array([0.0, target_y, 0.0]) - pos
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    fwd, right = _rot(fwd, up, -yaw), _rot(right, up, -yaw)
    fwd = _rot(fwd, right, pitch)
    up = np.cross(right, fwd)
    c, s = np.cos(roll), np.sin(roll)
    return pos, c * right + s * up, -s * right + c * up, fwd


class BlackHoleLayer(Layer):
    """Ray-traced Schwarzschild black hole with thin accretion disk, photon ring and lensed sky.

    Example:
        s.add(BlackHoleLayer(dist=30, inclination=84, azimuth=10, sky="galaxy", scale_res=2))
    """

    vector = True

    def __init__(self, *, dist=30.0, inclination=84.0, azimuth=0.0, roll=0.0, fov=36.0, yaw=0.0, pitch=0.0,
                 target_y=0.0, sky: str = "galaxy", sky_center=(84.0, 190.0), disk_rate: float = 15.0,
                 disk_t0: float = 0.0, ring_temp: float = 7500.0, scale_res: float = 1.0,
                 height: float | None = None, **kw):
        from aion.maths import schwarzschild as S

        uniforms = dict(u_gas=1.0, u_front=R_IN, u_ignite=1.0, u_disk=1.0, u_drain=R_OUT + 1.0,
                        u_Tpeak=6800.0, u_beam=4.0, u_shift=1.0, u_gain=0.30, u_mode=0.0,
                        u_stars=1.0, u_hero=0.0, u_starGain=1.0, u_starBoost=1.6,
                        u_ring=0.55, u_ringW=0.06, u_sweep=-1.0, u_sweepAmp=0.0,
                        u_skyAmt=1.0, u_objects=0.0, u_reveal=1.0, u_scanTint=(0.0, 0.0, 0.0))
        uniforms.update({k: kw.pop(k) for k in list(kw) if k.startswith("u_")})
        super().__init__(name=kw.pop("name", "blackhole"), **kw)
        self.uniforms = {k: track(v) for k, v in uniforms.items()}
        self.cam = {k: track(v) for k, v in dict(dist=dist, inclination=inclination, azimuth=azimuth, roll=roll,
                                                  fov=fov, yaw=yaw, pitch=pitch, target_y=target_y).items()}
        self.sky, self.disk_rate, self.scale_res = _SKY[sky], float(disk_rate), scale_res
        self.disk_t0, self.height = float(disk_t0), height
        self.vector = height is None                             # a panel is a positioned quad (pos / scale apply)
        tilt = np.radians(25.0)                                  # celestial pole, tilted off the disk axis
        self.sky_pole = np.array([np.sin(tilt), np.cos(tilt), 0.0])
        behind = -camera_basis(1.0, *sky_center)[0]             # galactic centre: behind the hole from here
        gc = behind - np.dot(behind, self.sky_pole) * self.sky_pole
        self.sky_gc = gc / np.linalg.norm(gc)
        self.ring_tint = tuple(float(x) for x in S.blackbody_rgb(ring_temp)[0])
        self._rt = None

    def tracks(self):
        return super().tracks() + list(self.uniforms.values()) + list(self.cam.values())

    def content_changes(self, t0, t1):
        return self.disk_rate != 0.0 or any(u.changes(t0, t1) for u in (*self.uniforms.values(), *self.cam.values()))

    def cache_key(self):
        return super().cache_key() + [_source(), self.sky, self.disk_rate, self.disk_t0, self.height, self.scale_res,
                                      self.sky_pole.tolist(), self.sky_gc.tolist(), self.ring_tint,
                                      {k: v.label for k, v in {**self.uniforms, **self.cam}.items()}]

    def draw(self, t: float, rc: RenderContext) -> Surface:
        k = self.scale_res * (1.0 if self.height is None else self.height / rc.frame_units[1])
        if self.height is not None:                               # keep panel pixels sharp when it is scaled up
            k *= max(1.0, float(np.max(np.asarray(self.scale(t), dtype=float))))
        k = min(k, MAX_HEIGHT / rc.size[1])                       # 4K output: cap supersampling, not memory
        size = (max(1, int(round(rc.size[0] * k))), max(1, int(round(rc.size[1] * k))))
        if self._rt is None or self._rt.size != size:
            self._rt = pool.target(size, "f2", pooled=False)
        c = {k: float(v(t)) for k, v in self.cam.items()}
        pos, right, up, fwd = camera_basis(max(c["dist"], 20.0), c["inclination"], c["azimuth"], c["roll"],
                                           c["yaw"], c["pitch"], c["target_y"])
        th = float(np.tan(np.radians(c["fov"]) / 2))
        tex = _tables()
        prog = program(_source())
        vals = {k: v(t) for k, v in self.uniforms.items()}
        view = rc.view(self.parallax)
        set_uniforms(prog, u_frame=rc.frame_units, u_view_inv=np.linalg.inv(view),
                     u_lutU=(tex["u"], 0), u_lutPhc=(tex["phc"], 1), u_phiEnd=(tex["end"], 2), u_bb=(tex["bb"], 3),
                     u_cam=pos, u_right=right, u_up=up, u_fwd=fwd, u_tanHalf=th, u_aspect=size[0] / size[1],
                     u_pix=2 * th / size[1], u_tau=(t - self.disk_t0) * self.disk_rate, u_sky=self.sky, u_ss=float(self.scale_res),
                     u_skyPole=self.sky_pole, u_skyGC=self.sky_gc, u_ringTint=self.ring_tint,
                     u_heroDir=-pos / np.linalg.norm(pos), **vals)
        self._rt.use()
        fullscreen(prog).render(vertices=3)
        extent = None if self.height is None else (self.height * size[0] / size[1], self.height)
        return Surface(self._rt.tex, ENC_LINEAR, extent)
