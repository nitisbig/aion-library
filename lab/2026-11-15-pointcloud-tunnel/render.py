"""Point-cloud tunnel walkthrough: 20 s, 16:9. moderngl headless on the Radeon R4.

    uv run python lab/2026-11-15-pointcloud-tunnel/render.py still --t 1.5 6 11 15.5 18.5 --height 540
    uv run python lab/2026-11-15-pointcloud-tunnel/render.py video --height 540 --fps 30      # preview
    uv run python lab/2026-11-15-pointcloud-tunnel/render.py video --height 1080 --fps 60     # final

Shots (all one continuous camera move):
  0.0– 3.5  scan reveal: a LiDAR sphere paints the tunnel into existence from the camera outward
  3.5– 9.0  walk forward down the lit path, dust streaking past (ref 1)
  9.0–13.5  the camera turns ~60° right to look at the trunks lining the path while still walking (ref 2)
 13.5–16.5  turn back, speed up; floor rails stream under the lens (ref 3)
 16.5–20.0  the tunnel ahead corkscrews into a vortex, the camera rolls with it and dives into the hole (ref 4)
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tunnel as TN  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"
DURATION = 20.0


# ── timeline ────────────────────────────────────────────────────────────────
def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def speed(t):
    v = 1.2 + 1.6 * ss(0.5, 4.0, t)                 # 1.2 → 2.8
    v -= 0.6 * ss(8.5, 10.0, t) - 0.6 * ss(12.5, 14.0, t)
    v += 2.6 * ss(13.5, 16.5, t)                    # → 5.4
    v += 1.6 * ss(17.0, 19.5, t)                    # → 7.0 dive
    return v


_TG = np.linspace(0, DURATION + 1, 8401)
_SG = np.concatenate([[0], np.cumsum((speed(_TG[1:]) + speed(_TG[:-1])) / 2 * np.diff(_TG))])


def s_cam(t):
    return np.interp(t, _TG, _SG)


def yaw(t):      # + = turn right
    return np.radians(48) * (ss(8.8, 10.8, t) - ss(12.3, 14.2, t)) + np.radians(-8) * ss(15.5, 17.5, t)


def roll(t):
    return np.radians(10) * np.sin(0.7 * t) * ss(3, 6, t) * 0.25 + np.radians(-75) * ss(16.5, 20.0, t)


def eye(t):
    s = s_cam(t)
    h = 1.25 - 0.25 * ss(13.5, 16.5, t)     # lower to the floor when running → rails fill the frame
    bob = 0.03 * np.sin(2 * np.pi * 1.7 * t) * ss(1, 3, t)
    sway = 0.06 * np.sin(0.9 * t) + 0.03 * np.sin(2.3 * t + 1)
    return np.array([TN.cx(s) + sway, TN.floor_y(s) + h + bob, -s])


def camera(t):
    p = eye(t)
    s = s_cam(t)
    tgt_s = s + 9.0
    tgt = np.array([TN.cx(tgt_s), TN.floor_y(tgt_s) + 1.1 + 0.3 * ss(16.5, 19, t), -tgt_s])
    f = tgt - p
    f /= np.linalg.norm(f)
    a = yaw(t)                                       # rotate about world up; +a turns toward +x
    ca, sa = np.cos(a), np.sin(a)
    f = np.array([ca * f[0] - sa * f[2], f[1], sa * f[0] + ca * f[2]])
    pitch = np.radians(-4 + 2 * np.sin(0.5 * t)) * ss(0, 1, 1)
    f[1] += pitch
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    ro = roll(t)
    r, u = np.cos(ro) * r + np.sin(ro) * u, -np.sin(ro) * r + np.cos(ro) * u
    dt = 1 / 120
    vel = (eye(t + dt) - eye(t - dt)) / (2 * dt)
    return dict(pos=p, fwd=f, right=r, up=u, vel=vel, s=s)


def events(t, cam):
    s = cam["s"]
    ls = s + 13.0 - 3.0 * ss(9, 11, t) + 3.0 * ss(12.5, 14, t)
    return dict(
        reveal=float(0.5 + 70 * ss(0.15, 3.8, t) ** 1.4) if t < 4.0 else 999.0,
        revealO=tuple(eye(0.0)),
        light=(float(TN.cx(ls)), float(TN.floor_y(ls) + 1.2), float(-ls)),
        lightI=float(1.5 * (0.6 + 0.4 * ss(0.5, 3.5, t))),
        twist=float(0.0035 * ss(15.0, 19.5, t)), twS0=float(s_cam(16.0) + 4.0),
        scanS=float(s + 1.5 + 30 * ((t - 4.0) / 3.2 % 1.0)), scanI=float(1.3 * ss(4.0, 5.0, t)),
        fade=float(ss(0.0, 0.6, t) * (1 - ss(19.2, 20.0, t))),
        fog=float(0.075 - 0.015 * ss(16, 19, t)),
        zoom=float(0.02 * ss(16.0, 18.5, t) * (1 - ss(19.3, 20, t))),
        ca=float(0.0015 * ss(16, 18, t)),
        shutter=float(0.16 + 0.06 * ss(13.5, 16, t)),
        exposure=float(1.0 - 0.3 * ss(17.5, 19.5, t)),
    )


# ── renderer ────────────────────────────────────────────────────────────────
def lin(hx, k=1.0):
    h = hx.lstrip("#")
    return tuple(float(((int(h[i:i + 2], 16) / 255) ** 2.2) * k) for i in (0, 2, 4))


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

        self.down = full("down.frag")
        self.up = full("up.frag")
        self.comp = full("composite.frag")
        self.pp = ctx.program(vertex_shader=src("points.vert", True), fragment_shader=src("points.frag"))
        self.lp = ctx.program(vertex_shader=src("lines.vert", True), fragment_shader=src("lines.frag"))

        P = TN.cached()
        surf, dust, rails = P["surf"], P["dust"], P["rails"]
        self.n_surf, self.n_dust = len(surf), len(dust)
        allp = np.concatenate([surf, dust]).astype("f4")
        self.pvbo = ctx.buffer(allp.tobytes())
        self.pvao = ctx.vertex_array(self.pp, [(self.pvbo, "3f 3f 4f", "in_pos", "in_nrm", "in_attr")])
        rl = np.c_[rails[:, :3], rails[:, 3:5], np.zeros((len(rails), 2))].astype("f4")
        self.n_rail = len(rl)
        st = np.repeat(dust, 2, axis=0)
        st = np.c_[st[:, :3], st[:, 6], st[:, 7], st[:, 8], np.tile([0.0, 1.0], len(dust))].astype("f4")
        self.lvbo = ctx.buffer(np.concatenate([rl, st]).tobytes())
        self.lvao = ctx.vertex_array(self.lp, [(self.lvbo, "3f 4f", "in_pos", "in_a")])
        print(f"{len(allp):,} points, {self.n_rail // 2:,} rail segs, {len(dust):,} streaks")

        def target(w, h, dtype="f2", comps=4):
            t = ctx.texture((w, h), comps, dtype=dtype)
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t, ctx.framebuffer(color_attachments=[t])

        self.acc = target(W, H)
        self.levels = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.fin = target(W, H, "f1", 3)

        k = H / 1080
        for prog in (self.pp, self.lp):
            for n, v in dict(u_green=lin("#9CC48A"), u_lightCol=lin("#F2F4EE"), u_amb=0.14, u_drift=0.25,
                             u_dustI=0.3).items():
                setu(prog, n, v)
        # u_area: mean surface area per point (m²), tuned by eye; base sprite = 2 px @1080p
        for n, v in dict(u_area=0.0030, u_base=max(1.0, 2.0 * k), u_cap=1.0).items():
            setu(self.pp, n, v)
        for n, v in dict(u_railI=0.14, u_streakI=0.16).items():
            setu(self.lp, n, v)

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, idx=0):
        ctx = self.ctx
        cam = camera(t)
        ev = events(t, cam)
        fovy = np.radians(62)
        tanY = float(np.tan(fovy / 2))
        uni = dict(u_cam=tuple(cam["pos"]), u_right=tuple(cam["right"]), u_up=tuple(cam["up"]),
                   u_fwd=tuple(cam["fwd"]), u_fy=self.H / (2 * tanY), u_tanY=tanY, u_tanX=tanY * self.W / self.H,
                   u_t=float(t), u_twist=ev["twist"], u_twS0=ev["twS0"], u_light=ev["light"], u_lightI=ev["lightI"],
                   u_fog=ev["fog"], u_reveal=ev["reveal"], u_revealO=ev["revealO"], u_scanS=ev["scanS"],
                   u_scanI=ev["scanI"], u_fade=ev["fade"], u_vel=tuple(cam["vel"]), u_shutter=ev["shutter"])
        for prog in (self.pp, self.lp):
            for k, v in uni.items():
                setu(prog, k, v)
        fb = self.acc[1]
        fb.use()
        fb.clear(0, 0, 0, 0)
        ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        self.pvao.render(moderngl.POINTS)
        setu(self.lp, "u_kind", 0.0)
        self.lvao.render(moderngl.LINES, vertices=self.n_rail, first=0)
        setu(self.lp, "u_kind", 1.0)
        self.lvao.render(moderngl.LINES, vertices=2 * self.n_dust, first=self.n_rail)
        ctx.disable(moderngl.BLEND)
        # bloom (dual Kawase)
        s = self.acc[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(*self.down, fbo, s, u_texel=(1 / s.width, 1 / s.height), u_thresh=0.7 if i == 0 else 0.0)
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
        for k, v in dict(u_bloom=0.35, u_exposure=ev["exposure"], u_fade=1.0, u_vig=0.45, u_grain=0.025,
                         u_frame=float(idx % 997), u_zoom=ev["zoom"], u_ca=ev["ca"],
                         u_shadow=(0.97, 1.02, 0.98), u_high=(1.02, 1.0, 0.97),
                         u_res=(float(self.W), float(self.H))).items():
            setu(c, k, v)
        self.comp[1].render(moderngl.TRIANGLE_STRIP)
        ctx.finish()
        return self.fin[1].read(components=3, alignment=1)


# ── CLI ─────────────────────────────────────────────────────────────────────
def size_for(h):
    return int(round(h * 16 / 9 / 2) * 2), h


def to_img(buf, w, h):
    from PIL import Image
    return Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)


def cmd_still(a):
    w, h = size_for(a.height)
    r = Renderer(w, h)
    OUT.mkdir(exist_ok=True)
    ims = []
    for t in a.t:
        t0 = time.time()
        im = to_img(r.frame(t, int(t * 60)), w, h)
        im.save(OUT / f"still_{t:05.2f}s{a.tag}.png")
        ims.append(im)
        print(f"  t={t:5.2f}s  {time.time() - t0:.2f}s/frame")
    if len(ims) > 1:
        from PIL import Image
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
    out = Path(a.out) if a.out else OUT / f"pointcloud_tunnel_{h}p{a.fps}.mp4"
    r = Renderer(w, h)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
         "-r", str(a.fps), "-i", "-", "-vf", "vflip", "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf),
         "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    with Progress(f"pointcloud_tunnel_{h}p{a.fps}", n) as bar:
        for i in range(n):
            ff.stdin.write(r.frame(i / a.fps, i))
            bar.update(1)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        bar.close(out)
    print(f"✔ {n} frames → {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still")
    s.add_argument("--t", type=float, nargs="+", default=[1.5, 6.0, 11.0, 15.5, 18.0, 19.3])
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
