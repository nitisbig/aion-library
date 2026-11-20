"""Dido's voyage as a point cloud: the opening 19.1 s of video 012, one continuous camera move, synced to the narration.

    uv run python lab/2026-11-20-pointcloud-voyage/scene.py                         # build the cloud (~4 s, cached)
    uv run python lab/2026-11-20-pointcloud-voyage/render.py still --t 1 5 9 13 18 --height 540
    uv run python lab/2026-11-20-pointcloud-voyage/render.py video --height 540 --fps 30     # preview with narration
    uv run python lab/2026-11-20-pointcloud-voyage/render.py video --height 1080 --fps 30

Beats (from videos/012 beats.py): queen 4.68, africa 7.90, king 9.50, joke 12.27, hide 15.90, strips 18.60.
  0.0– 3.6  a scan sphere spreads out from the galley and paints the evening sea in
  3.6– 9.3  rowing toward Africa, the camera swings along the port side, the sun behind the sail
  9.3–12.0  landfall: oars shipped, the sail brailed up, the camera cranes up behind the ship toward the coast
 12.0–19.1  at anchor, the city's lights come on, dusk deepens; fades out for the workbench
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import overlays as OV  # noqa: E402
import scene as SC  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"
DURATION = 19.1
ARRIVE, KING, STRIPS = 9.3, 9.5, 18.6
SHIP_D = 90.0
AUDIO = ROOT / "videos/012-lagrange-multipliers/assets/audio.wav"


def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease_out(u):
    u = np.clip(u, 0, 1)
    return 1 - (1 - u) ** 2.4


def ship_at(t):
    return np.array([0.0, 0.0, -SHIP_D * ease_out(t / ARRIVE)])


def ship_pose(t):
    p = ship_at(t)
    hs = np.mean([SC.wave_h(p[0] + dx, p[2] + dz, t) for dx, dz in ((0, 0), (0, -6), (0, 6), (-1.5, 0), (1.5, 0))])
    p = p + [0, hs - 0.12, 0]
    roll = 0.045 * np.sin(0.9 * t) + 0.02 * np.sin(2.1 * t + 1)
    pitch = 0.03 * np.sin(0.7 * t + 1) + 0.012 * np.sin(1.9 * t)
    return p, (roll, pitch)


# camera keys: (t, offset from the ship, look-at offset from the ship); world axes, the bow points to -z
KEYS = [
    (0.0, (-24.0, 2.6, 17.0), (2.0, 5.0, -10.0)),
    (4.2, (-28.0, 4.2, -4.0), (0.0, 5.0, -4.0)),
    (7.6, (-24.0, 6.0, 11.0), (-2.0, 5.0, -12.0)),
    (11.2, (-10.0, 13.0, 36.0), (-40.0, 4.0, -120.0)),
    (DURATION, (-7.0, 11.0, 28.0), (-40.0, 6.0, -120.0)),
]


def cam_at(t):
    ks = KEYS
    for (ta, oa, la), (tb, ob, lb) in zip(ks, ks[1:]):
        if t <= tb:
            u = ss(ta, tb, t)
            o = np.array(oa) * (1 - u) + np.array(ob) * u
            look = np.array(la) * (1 - u) + np.array(lb) * u
            break
    else:
        o, look = np.array(ks[-1][1]), np.array(ks[-1][2])
    base = ship_at(t)
    pos = base + o + [0.12 * np.sin(0.6 * t), 0.15 * np.sin(0.8 * t + 1), 0]
    f = base + look - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    ro = 0.012 * np.sin(0.5 * t)
    r, u = np.cos(ro) * r + np.sin(ro) * u, -np.sin(ro) * r + np.cos(ro) * u
    return pos, f, r, u


def lin(hx, k=1.0):
    return tuple(float(x * k) for x in SC.lin(hx))


def src(name, common=False):
    return "#version 430\n" + ((SH / "common.glsl").read_text() if common else "") + (SH / name).read_text()


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


class Renderer:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.ctx = ctx = moderngl.create_context(standalone=True, require=430)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def full(fs):
            p = ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs))
            return p, ctx.vertex_array(p, [(quad, "2f", "in_pos")])
        self.down, self.up, self.comp = full("down.frag"), full("up.frag"), full("composite.frag")
        self.pp = ctx.program(vertex_shader=src("points.vert", True), fragment_shader=src("points.frag"))
        P = SC.cached()
        self.vbo = ctx.buffer(P.tobytes())
        self.vao = ctx.vertex_array(self.pp, [(self.vbo, "3f 3f 3f 4f", "in_pos", "in_nrm", "in_col", "in_attr")])
        k = P[:, 9]
        self.rng_ = {i: (int(np.searchsorted(k, i - 0.5)), int(np.searchsorted(k, i + 0.5))) for i in range(8)}
        print(f"{len(P):,} points")

        def target(w, h, dtype="f2", comps=4):
            t = ctx.texture((w, h), comps, dtype=dtype)
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t, ctx.framebuffer(color_attachments=[t])
        self.acc = target(W, H)
        self.depth = ctx.depth_renderbuffer((W, H))
        self.accd = ctx.framebuffer(color_attachments=[self.acc[0]], depth_attachment=self.depth)
        self.levels = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.fin = target(W, H, "f1", 3)
        k = H / 1080
        for n, v in dict(u_base=max(1.0, 1.3 * k), u_cap=1.0, u_seaI=1.0, u_skyI=1.0, u_landI=1.0, u_shipI=0.55,
                         u_amb=0.22, u_arrive=ARRIVE, u_shipD=SHIP_D, u_shipZ0=0.0, u_shipX=0.0,
                         u_sunDir=tuple(SC.SUN_DIR)).items():
            setu(self.pp, n, v)

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, idx=0):
        ctx = self.ctx
        pos, f, r, u = cam_at(t)
        sp, rot = ship_pose(t)
        furl = float(ss(ARRIVE - 0.5, ARRIVE + 1.2, t))
        night = float(ss(KING, DURATION, t))
        fovy = np.radians(52)
        tanY = float(np.tan(fovy / 2))
        uni = dict(u_cam=tuple(pos), u_right=tuple(r), u_up=tuple(u), u_fwd=tuple(f), u_fy=self.H / (2 * tanY), u_tanY=tanY,
                   u_tanX=tanY * self.W / self.H, u_t=float(t), u_shipPos=tuple(sp), u_shipRot=tuple(float(x) for x in rot),
                   u_furl=furl, u_row=1 - furl, u_lit=float(ss(ARRIVE + 0.6, ARRIVE + 4.5, t)), u_night=night,
                   u_sink=float(14 * ss(0, DURATION, t)),
                   u_sunCol=lin("#ffd9a8", 1.0 - 0.35 * night), u_skyCol=lin("#c9506e", 0.7 - 0.3 * night), u_fogCol=lin("#ff9a7a", 0.9),
                   u_fog=0.0035, u_reveal=float(0.5 + 950 * ss(0.15, 3.6, t) ** 1.7) if t < 3.8 else 1e5,
                   u_revealO=tuple(ship_at(0) + [0, 3, 0]), u_fade=float(ss(0.0, 0.5, t) * (1 - ss(DURATION - 0.45, DURATION, t))))
        for k, v in uni.items():
            setu(self.pp, k, v)
        pc, pa = [], []
        for kind, src, sx, sy, z, hf, t_in, t_out, yaw in OV.PANELS:
            pc.append((sx, sy, z, hf))
            pa.append((float(np.clip((t - t_in) / 1.3, 0, 1)), float(np.clip((t - t_out) / 0.7, 0, 1)), yaw, 0.0))
        self.pp["u_pc"].write(np.array(pc, "f4").tobytes())
        self.pp["u_pa"].write(np.array(pa, "f4").tobytes())
        fb = self.accd
        fb.use()
        fb.clear(0, 0, 0, 0, depth=1.0)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE | moderngl.DEPTH_TEST)
        # 1) the land writes its silhouette into depth only
        fb.color_mask = (False, False, False, False)
        setu(self.pp, "u_occ", 1.0)
        for kk in (1, 7):
            a, b = self.rng_[kk]
            self.vao.render(moderngl.POINTS, vertices=b - a, first=a)
        fb.color_mask = (True, True, True, True)
        setu(self.pp, "u_occ", 0.0)
        # 2) the sky draws only where the land doesn't cover it
        fb.depth_mask = False
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        a, b = self.rng_[2]
        self.vao.render(moderngl.POINTS, vertices=b - a, first=a)
        # 3) everything else, additive, no depth test
        ctx.disable(moderngl.DEPTH_TEST)
        for kk in (0, 1, 3, 4, 5, 6, 7):
            a, b = self.rng_[kk]
            if b > a:
                self.vao.render(moderngl.POINTS, vertices=b - a, first=a)
        fb.depth_mask = True
        ctx.disable(moderngl.BLEND)
        s = self.acc[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(*self.down, fbo, s, u_texel=(1 / s.width, 1 / s.height), u_thresh=0.9 if i == 0 else 0.0)
            s = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(*self.up, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        self.fin[1].use()
        self.acc[0].use(0)
        self.levels[0][0].use(1)
        c = self.comp[0]
        c["scene"].value, c["bloom"].value = 0, 1
        for k, v in dict(u_bloom=0.3, u_exposure=1.0, u_fade=1.0, u_vig=0.42, u_grain=0.02, u_frame=float(idx % 997), u_zoom=0.0,
                         u_ca=0.0, u_shadow=(0.94, 0.98, 1.06), u_high=(1.04, 1.0, 0.94), u_res=(float(self.W), float(self.H))).items():
            setu(c, k, v)
        self.comp[1].render(moderngl.TRIANGLE_STRIP)
        ctx.finish()
        return self.fin[1].read(components=3, alignment=1)


def size_for(h):
    return int(round(h * 16 / 9 / 2) * 2), h


def to_img(buf, w, h):
    from PIL import Image
    return Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)


def cmd_still(a):
    from PIL import Image
    w, h = size_for(a.height)
    r = Renderer(w, h)
    OUT.mkdir(exist_ok=True)
    ims = []
    for t in a.t:
        t0 = time.time()
        im = to_img(r.frame(t, int(t * 30)), w, h)
        im.save(OUT / f"still_{t:05.2f}s{a.tag}.png")
        ims.append(im)
        print(f"  t={t:5.2f}s  {time.time() - t0:.2f}s/frame")
    if len(ims) > 1:
        cols = 2 if len(ims) <= 4 else 3
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (60, 60, 60))
        for i, im in enumerate(ims):
            sh.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        sh.save(OUT / f"contact{a.tag}.png")
        print(OUT / f"contact{a.tag}.png")


def cmd_video(a):
    from aion.progress import Progress
    w, h = size_for(a.height)
    n = int(round(DURATION * a.fps))
    silent = OUT / f"_voyage_{h}p{a.fps}_silent.mp4"
    out = Path(a.out) if a.out else OUT / f"pointcloud_voyage_{h}p{a.fps}.mp4"
    r = Renderer(w, h)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(a.fps), "-i", "-",
         "-vf", "vflip", "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-colorspace", "bt709",
         "-color_primaries", "bt709", "-color_trc", "bt709", str(silent)], stdin=subprocess.PIPE)
    with Progress(f"pointcloud_voyage_{h}p{a.fps}", n) as bar:
        for i in range(n):
            ff.stdin.write(r.frame(i / a.fps, i))
            bar.update(1)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg failed")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-t", str(DURATION), "-i", str(AUDIO), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    silent.unlink()
    print(f"✔ {n} frames → {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still")
    s.add_argument("--t", type=float, nargs="+", default=[1.2, 3.0, 6.0, 9.5, 12.0, 17.0])
    s.add_argument("--height", type=int, default=540)
    s.add_argument("--tag", default="")
    s = sub.add_parser("video")
    s.add_argument("--height", type=int, default=540)
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--crf", type=int, default=17)
    s.add_argument("--preset", default="medium")
    s.add_argument("--out")
    a = ap.parse_args()
    cmd_still(a) if a.cmd == "still" else cmd_video(a)


if __name__ == "__main__":
    main()
