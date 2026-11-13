"""A small perspective camera for the 3D complex plane (s04_quarter, s11_identity).

One camera drives two things that must line up exactly:
  * shaders/plane3d.frag, which ray-casts each pixel onto the plane z = 0 (colors, grid, depth fade), and
  * the crisp Manim overlays, drawn flat in plane-world coordinates and then warped through the same projection.

The camera (keep in sync with plane3d.frag):
    eye     C = T + dist·(cos φ·sin ψ, −cos φ·cos ψ, sin φ)      ψ = yaw, φ = pitch, T = (tx, ty, 0)
    right   r = (cos ψ, sin ψ, 0),  forward f = (T − C)/|T − C|,  up u = r × f
    screen  (q·r, q·u)/(q·f)·F + (sx, sy),   q = P − C,   F = 4/tan(fov/2)
Pitch 90° (straight down) with dist = F is the identity: plane world = Manim world. That makes the handoff from
the flat 2D scenes seamless.

    cam = Cam3(pitch=keys(...), dist=keys(...), tx=0, ty=-0.9, sx=0, sy=-0.9)
    s.shader("plane3d.frag", z=0, **cam.uniforms(), **plane_uniforms(O, 1.0, 1.0, ...))
    live(m, lambda t: cam(t).lift(Arrow(...), h=0.12), window)
"""
from aion import *
from aion.core.track import track

FOV = np.radians(40.0)
F0 = 4.0 / np.tan(FOV / 2)                   # top-down distance where 1 plane unit = 1 Manim unit
TOP = PI / 2


def _rgb(c):
    return tuple(float(x) for x in ManimColor(c).to_rgb())


class View:
    """The camera frozen at one time t: projection, depth, fog, and helpers that place Manim mobjects."""

    def __init__(self, yaw, pitch, dist, fov, tx, ty, sx, sy, fog):
        cp, sp, cy, sy_ = np.cos(pitch), np.sin(pitch), np.cos(yaw), np.sin(yaw)
        T = np.array([tx, ty, 0.0])
        self.C = T + dist * np.array([cp * sy_, -cp * cy, sp])
        self.f = (T - self.C) / np.linalg.norm(T - self.C)
        self.r = np.array([cy, sy_, 0.0])
        self.u = np.cross(self.r, self.f)
        self.F = 4.0 / np.tan(fov / 2)
        self.s0 = np.array([sx, sy])
        self.dist, self.fog = dist, fog

    def depth(self, p):
        """Distance along the view axis of world point(s) p (..., 3)."""
        return (np.asarray(p, float) - self.C) @ self.f

    def proj(self, p):
        """World point(s) (..., 3) → Manim screen point(s) (..., 3), z = 0."""
        q = np.asarray(p, float) - self.C
        d = np.maximum(q @ self.f, 1e-3)[..., None]
        xy = np.stack([q @ self.r, q @ self.u], axis=-1) / d * self.F + self.s0
        return np.concatenate([xy, np.zeros_like(xy[..., :1])], axis=-1)

    def scale(self, p):
        """On-screen size of one world unit at p, relative to the flat layout (1 at top-down, dist = F0)."""
        return self.F / max(float(self.depth(p)), 1e-3)

    def fogk(self, p):
        """The depth fade at p (matches the shader): 1 near the target, → 0 toward the horizon."""
        ray = np.linalg.norm(np.asarray(p, float) - self.C)
        return float(np.exp(-max(ray - self.dist, 0.0) / max(self.fog, 1e-3)))

    def warp(self, mob, h=0.0):
        """Lay a mobject drawn flat in plane-world coordinates onto the plane at height h (in place)."""
        for sm in mob.family_members_with_points():
            pts = sm.points.copy()
            pts[:, 2] = h
            sm.points = self.proj(pts)
        return mob

    def flat(self, mob, h=0.0, smooth=8):
        """warp() with curves subdivided first, so circles stay round under perspective."""
        for sm in mob.family_members_with_points():
            if smooth and sm.get_num_curves() > 0:
                sm.insert_n_curves(smooth * sm.get_num_curves())
        return self.warp(mob, h)

    def lift(self, mob, h=0.1, shadow=0.55, smooth=8):
        """The mobject lifted to height h over the plane, with its crisp shadow on the plane under it (a light
        straight overhead). Returns VGroup(shadow, lifted)."""
        sh = mob.copy()
        sh.set_stroke(C.bg).set_fill(C.bg)
        for sm in sh.family_members_with_points():
            sm.set_stroke(opacity=shadow * (sm.get_stroke_opacity() > 0.004))
            sm.set_fill(opacity=shadow * (sm.get_fill_opacity() > 0.004))
        return VGroup(self.flat(sh, 0.0, smooth), self.flat(mob, h, smooth))

    def bill(self, mob, p, h=0.0, size=True, lo=0.55, hi=1.6):
        """Billboard: keep the mobject facing the viewer, centred on plane point p = (x, y), scaled by depth."""
        w = np.array([p[0], p[1], h])
        if size:
            mob.scale(float(np.clip(self.scale(w), lo, hi)))
        return mob.move_to(self.proj(w))

    def at(self, p, h=0.0):
        """Screen point of plane point p = (x, y) at height h."""
        return self.proj(np.array([p[0], p[1], h]))

    def post(self, p, h, color, width=None, opacity=1.0):
        """A vertical line from the plane up to height h at p (an axis of turning, a marker)."""
        return Line(self.at(p, 0.0), self.at(p, h), color=color, stroke_width=width or C.thin,
                    stroke_opacity=opacity)


class Cam3:
    """The 3D camera as tracks. Each argument is a number, a Track or a callable of t.

    Example:
        cam = Cam3(pitch=keys((0, PI / 2), (3, 0.66, "easy_ease")), dist=F0, ty=-0.9, sy=-0.9)
        cam(1.5).at((1, 0))                 # where the plane point (1, 0) is on screen at t = 1.5
    """

    def __init__(self, yaw=0.0, pitch=TOP, dist=F0, fov=FOV, tx=0.0, ty=0.0, sx=0.0, sy=0.0, fog=14.0):
        self.tr = dict(yaw=track(yaw), pitch=track(pitch), dist=track(dist), fov=track(fov), tx=track(tx),
                       ty=track(ty), sx=track(sx), sy=track(sy), fog=track(fog))

    def __call__(self, t):
        return View(**{k: float(v(t)) for k, v in self.tr.items()})

    def uniforms(self):
        return {f"u_{k}": v for k, v in self.tr.items()}


def plane_uniforms(origin, unit, step, theta=0.0, colors=0.0, lines=1.0, reveal=99.0, edge=0.0, sat=0.6,
                   value=0.8, wgrid=None, wminor=None, waxis=None, clip=(0.0, 0.0, 0.0, 0.0), tint=1.0, sheen=0.55,
                   kmajor=0.36, kminor=0.16):
    """The plane's own uniforms for plane3d.frag (theme colors passed in, so no raw hex lives in the shader)."""
    return dict(u_origin=tuple(origin), u_unit=unit, u_step=step, u_theta=theta, u_colors=colors, u_lines=lines,
                u_reveal=reveal, u_edge=edge, u_clip=clip, u_sat=sat, u_value=value,
                u_wgrid=wgrid or C.thin * 0.7, u_wminor=wminor or C.thin * 0.45, u_waxis=waxis or C.thin * 1.1,
                u_tint=tint, u_sheen=sheen, u_kmajor=kmajor, u_kminor=kminor,
                u_cgrid=_rgb(C.grid), u_cminor=_rgb(C.grid_minor), u_caxis=_rgb(C.axis))
