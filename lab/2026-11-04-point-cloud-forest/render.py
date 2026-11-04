"""Point Cloud Forest: 30 s hobby piece, rendered on the GPU (moderngl, headless on the Radeon R4).

    uv run python lab/2026-11-04-point-cloud-forest/render.py looks                        # 6 stills × looks A/B/C
    uv run python lab/2026-11-04-point-cloud-forest/render.py still --look A --t 2.6 13
    uv run python lab/2026-11-04-point-cloud-forest/render.py video --look A --height 480 --fps 30     # preview
    uv run python lab/2026-11-04-point-cloud-forest/render.py video --look A --height 1080 --fps 60    # final
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import forest as F  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return np.array([((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4)])


LOOKS = {
    "A": dict(name="Moonlit", pal=dict(
        GROUND=("#6A7484", 0.30), LITTER=("#8A8F96", 0.34), PATH=("#B3ADA2", 0.45), BARK=("#C9D3DE", 0.55),
        TWIG=("#B8C6D4", 0.45), LEAF=("#A6C8CE", 0.24), NEEDLE=("#93B8C2", 0.24), FERN=("#B2E0CF", 0.5),
        GRASS=("#B0D0BA", 0.42), MOSS=("#86D6B6", 0.5), ROCK=("#B4BCC6", 0.5), LOG=("#C0C6CC", 0.5),
        FUNGI=("#EAF2FF", 1.6), FLOWER=("#F2E8FF", 1.2), WATER=("#8FE3FF", 1.0), MIST=("#9FB6CC", 0.12),
        FIREFLY=("#FFB347", 40.0), GBARK=("#DCE4EE", 0.6), GLEAF=("#B6D6DA", 0.28)),
        lidar=0.0, shadow=(0.9, 1.0, 1.12), high=(1.05, 1.0, 0.94), bloom=1.0, gain=0.75),
    "B": dict(name="LiDAR spectrum", pal=dict(
        GROUND=("#9A9A9A", 0.30), LITTER=("#A0A0A0", 0.34), PATH=("#B8B8B8", 0.45), BARK=("#C8C8C8", 0.55),
        TWIG=("#C0C0C0", 0.45), LEAF=("#B8B8B8", 0.36), NEEDLE=("#B0B0B0", 0.34), FERN=("#C8C8C8", 0.5),
        GRASS=("#BEBEBE", 0.42), MOSS=("#B0B0B0", 0.45), ROCK=("#B8B8B8", 0.5), LOG=("#C0C0C0", 0.5),
        FUNGI=("#FFFFFF", 1.4), FLOWER=("#FFFFFF", 1.0), WATER=("#7FD8FF", 1.0), MIST=("#7FA8C8", 0.12),
        FIREFLY=("#FFE08A", 36.0), GBARK=("#D0D0D0", 0.6), GLEAF=("#C0C0C0", 0.4)),
        lidar=1.0, cmap=["#2A3A8C", "#1F8FB0", "#3EBF86", "#D8D35E", "#FF8C55"],
        shadow=(0.95, 1.0, 1.06), high=(1.03, 1.0, 0.97), bloom=0.9, gain=1.0),
    "C": dict(name="Bioluminescent", pal=dict(
        GROUND=("#13403E", 0.30), LITTER=("#1A4A48", 0.32), PATH=("#2A5A54", 0.4), BARK=("#2A7272", 0.45),
        TWIG=("#2C8080", 0.42), LEAF=("#22A08A", 0.34), NEEDLE=("#1E8A78", 0.32), FERN=("#2AF0C8", 0.8),
        GRASS=("#48F4B8", 0.6), MOSS=("#00FFD0", 1.6), ROCK=("#2E5858", 0.4), LOG=("#327070", 0.45),
        FUNGI=("#FF3FD0", 4.0), FLOWER=("#C860FF", 3.0), WATER=("#40C8FF", 1.4), MIST=("#30A0A0", 0.15),
        FIREFLY=("#C8FF6A", 36.0), GBARK=("#2E8080", 0.5), GLEAF=("#2AC0A0", 0.4)),
        lidar=0.0, shadow=(0.92, 1.0, 1.08), high=(1.04, 1.0, 1.02), bloom=1.25, gain=1.0),
}

MOON = np.array([0.45, 0.8, -0.4]) / np.linalg.norm([0.45, 0.8, -0.4])


def forest_cached():
    key = hashlib.sha1((HERE / "forest.py").read_bytes()).hexdigest()[:10]
    path = OUT / f"forest_{key}.npz"
    if path.exists():
        z = np.load(path)
        return {k: z[k] for k in z.files}
    P = F.build()
    P.pop("meta")
    OUT.mkdir(exist_ok=True)
    np.savez(path, **P)
    return P


def pack(P):
    n = len(P["pos"])
    a = np.c_[P["pos"], P["area"]].astype("f4")
    b = np.c_[P["normal"], P["wind"], P["var"], P["mat"], P["hag"], P["rad"]].astype("f2")
    return np.hstack([a.view("u1").reshape(n, 16), b.view("u1").reshape(n, 16)])


def src(name):
    return "#version 430\n" + (SH / name).read_text()


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


class Renderer:
    def __init__(self, width, height, look="A"):
        self.W, self.H = W, H = width, height
        self.L = L = LOOKS[look]
        self.ctx = ctx = moderngl.create_context(standalone=True, require=430)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def full(fs):
            p = ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs))
            return p, ctx.vertex_array(p, [(quad, "2f", "in_pos")])

        self.down_p, self.down_v = full("down.frag")
        self.up_p, self.up_v = full("up.frag")
        self.comp_p, self.comp_v = full("composite.frag")
        self.pp = ctx.program(vertex_shader=src("points.vert"), fragment_shader=src("points.frag"))

        t0 = time.time()
        P = forest_cached()
        self.n = len(P["pos"])
        self.vbo = ctx.buffer(pack(P).tobytes())
        fmt = (self.vbo, "4f 4f2 4f2", "in_pa", "in_nw", "in_m")
        self.vao = ctx.vertex_array(self.pp, [fmt])
        p, m = P["pos"], P["mat"].astype(int)
        refl = ((p[:, 0] > -50) & (p[:, 0] < 50) & (p[:, 2] > -110) & (p[:, 2] < -25) & (p[:, 1] > F.YW + 0.05)
                & (m != F.M["WATER"]) & (m != F.M["MIST"]))
        ri = np.nonzero(refl)[0].astype("u4")
        self.n_refl = len(ri)
        self.vao_r = ctx.vertex_array(self.pp, [fmt], index_buffer=ctx.buffer(ri.tobytes()), index_element_size=4)
        print(f"{self.n:,} points, {self.n_refl:,} reflectable ({time.time() - t0:.1f}s)")

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

        pal = np.zeros((len(F.MATS), 3), "f4")
        for k, (hx, I) in L["pal"].items():
            pal[F.M[k]] = lin(hx, I)
        self.pp["u_pal"].write(pal.tobytes())
        cm = np.array([lin(c) for c in L.get("cmap", ["#000000"] * 5)], "f4")
        if "u_cmap" in self.pp:
            self.pp["u_cmap"].write(cm.tobytes())
        s = H / 480
        for k, v in dict(u_moon=tuple(MOON), u_lidar=L["lidar"], u_base=1.25 * s ** 0.85, u_maxSize=34.0 * s,
                         u_capPix=2.5 * s * s, u_yw=F.YW, u_gain=L["gain"],
                         u_only=int(os.environ.get("ONLY_MAT", -1))).items():
            setu(self.pp, k, v)

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, idx=0):
        ctx = self.ctx
        ev = TL.events(t)
        cam = TL.camera(t)
        tanY = float(np.tan(cam["fov"] / 2))
        fb = self.acc[1]
        fb.use()
        fb.clear(0, 0, 0, 0)
        ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        p = self.pp
        for k, v in dict(u_cam=tuple(cam["pos"]), u_right=tuple(cam["right"]), u_up=tuple(cam["up"]),
                         u_fwd=tuple(cam["fwd"]), u_fy=self.H / (2 * tanY), u_tanY=tanY, u_tanX=tanY * self.W / self.H,
                         u_tau=ev["tau"], u_t=float(t), u_wind=float(ev["wind"]), u_gustT0=ev["gust_t0"],
                         u_focus=ev["focus"], u_aper=ev["aper"], u_fog=ev["fog"],
                         u_scanC=tuple(ev["scan_c"]), u_scanR=float(ev["scan_r"]), u_lineO=tuple(ev["line_o"]),
                         u_lineDir=tuple(ev["line_dir"]), u_lineD=float(ev["line_d"]), u_reflect=0.0).items():
            setu(p, k, v)
        self.vao.render(moderngl.POINTS)
        if ev["refl"] > 0:
            setu(p, "u_reflect", 1.0)
            self.vao_r.render(moderngl.POINTS)
        ctx.disable(moderngl.BLEND)
        # bloom (dual Kawase)
        s = self.acc[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, s, u_texel=(1 / s.width, 1 / s.height),
                       u_thresh=0.25 if i == 0 else 0.0)
            s = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        # composite + grade
        self.fin[1].use()
        self.acc[0].use(0)
        self.levels[0][0].use(1)
        c = self.comp_p
        c["scene"].value, c["bloom"].value = 0, 1
        L = self.L
        for k, v in dict(u_bloom=float(ev["bloom"] * L["bloom"]), u_exposure=float(ev["exposure"]), u_fade=float(ev["fade"]),
                         u_vig=0.5, u_grain=0.03, u_frame=float(idx % 997), u_zoom=float(ev["zoom"]),
                         u_ca=float(ev["ca"]), u_shadow=L["shadow"], u_high=L["high"],
                         u_res=(float(self.W), float(self.H))).items():
            setu(c, k, v)
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        ctx.finish()
        return self.fin[1].read(components=3, alignment=1)


# ── CLI ──────────────────────────────────────────────────────────────────────
def size_for(height):
    return int(round(height * 16 / 9 / 2) * 2), height


def to_img(buf, w, h):
    from PIL import Image
    return Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)


def sheet(ims, w, h, path, cols=3):
    from PIL import Image
    rows = (len(ims) + cols - 1) // cols
    s = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (60, 60, 60))
    for i, im in enumerate(ims):
        s.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    s.save(path)
    print(path)


def stills(look, ts, height, tag=""):
    w, h = size_for(height)
    r = Renderer(w, h, look)
    OUT.mkdir(exist_ok=True)
    ims, times = [], []
    for t in ts:
        t0 = time.time()
        im = to_img(r.frame(t, int(t * 60)), w, h)
        times.append(time.time() - t0)
        im.save(OUT / f"still_{look}_{t:05.2f}s{tag}.png")
        ims.append(im)
        print(f"  look {look} t={t:5.2f}s  {times[-1]:.2f}s/frame")
    if len(ims) > 1:
        sheet(ims, w, h, OUT / f"contact_{look}{tag}.png")
    r.ctx.release()
    return times


SEG_FRAMES = 150


def _render_key(a):
    hsh = hashlib.sha1()
    for p in sorted([*HERE.glob("*.py"), *SH.glob("*")]):
        hsh.update(p.name.encode()); hsh.update(p.read_bytes())
    hsh.update(f"{a.look}|{a.height}|{a.fps}|{a.crf}|{SEG_FRAMES}".encode())
    return hsh.hexdigest()[:12]


def cmd_video(a):
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(TL.DURATION * fps))
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"point_cloud_forest_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"          # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"PointCloudForest@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    r = None
    for k, (s, e) in enumerate(chunks):
        if seg(k).exists():
            continue
        r = r or Renderer(w, h, a.look)
        part = segdir / f"seg_{k:04d}.part.mp4"
        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "vflip",
             "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p", str(part)],
            stdin=subprocess.PIPE)
        for i in range(s, e):
            ff.stdin.write(r.frame(i / fps, i))
            bar.update(1)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError(f"ffmpeg failed on segment {k}")
        os.replace(part, seg(k))
    bar.close()
    lst = segdir / "list.txt"
    lst.write_text("".join(f"file '{seg(k).name}'\n" for k in range(len(chunks))))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    print(f"✔ {n} frames → {out}")


SHOTS = [2.6, 6.8, 13.0, 20.0, 24.6, 28.0]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still")
    s.add_argument("--look", default="A", choices=list(LOOKS))
    s.add_argument("--t", type=float, nargs="+", default=SHOTS)
    s.add_argument("--height", type=int, default=480)
    s.add_argument("--tag", default="")
    s = sub.add_parser("looks")
    s.add_argument("--looks", nargs="+", default=list(LOOKS))
    s.add_argument("--t", type=float, nargs="+", default=SHOTS)
    s.add_argument("--height", type=int, default=480)
    s = sub.add_parser("video")
    s.add_argument("--look", default="A", choices=list(LOOKS))
    s.add_argument("--height", type=int, default=480)
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--crf", type=int, default=18)
    s.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "still":
        stills(a.look, a.t, a.height, a.tag)
    elif a.cmd == "looks":
        for look in a.looks:
            ts = stills(look, a.t, a.height)
            print(f"look {look}: mean {np.mean(ts[1:] if len(ts) > 1 else ts):.2f}s/frame @ {a.height}p")
    else:
        cmd_video(a)


if __name__ == "__main__":
    main()
