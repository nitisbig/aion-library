"""Classical mechanics: 60 s hobby piece. moderngl renderer (Radeon R4, headless) + CLI.

    uv run python lab/2026-11-04-physics-engine/render.py still --look A --t 8.5 14.5 33 47.5 56
    uv run python lab/2026-11-04-physics-engine/render.py looks --t 8.5 14.5 33 47.5 56     # A/B/C sheets
    uv run python lab/2026-11-04-physics-engine/render.py video --look A --height 480 --fps 30
    uv run python lab/2026-11-04-physics-engine/render.py video --look A --height 1080 --fps 60
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import labels as LB  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"
BG = TL.lin("#05060A")


def src(name):
    return "#version 330\n" + (SH / name).read_text()


class Renderer:
    def __init__(self, width, height, look="A", sub=None):
        self.L = TL.LOOKS[look]
        self.look = look
        self.W, self.H = width, height
        self.sub = sub or self.L["sub"]
        self.ctx = ctx = moderngl.create_context(standalone=True)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        mk = lambda fs: ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs))  # noqa: E731
        qv = lambda p: ctx.vertex_array(p, [(quad, "2f", "in_pos")])                           # noqa: E731
        self.down_p, self.up_p, self.comp_p, self.acc_p = (mk(f) for f in
                                                           ("down.frag", "up.frag", "composite.frag", "accum.frag"))
        self.down_v, self.up_v, self.comp_v, self.acc_v = map(qv, (self.down_p, self.up_p, self.comp_p, self.acc_p))
        self.prim_p = ctx.program(vertex_shader=src("prim.vert"), geometry_shader=src("prim.geom"),
                                  fragment_shader=src("prim.frag"))
        self.cap = 65536
        self.prim_buf = ctx.buffer(reserve=self.cap * 80, dynamic=True)
        self.prim_v = ctx.vertex_array(self.prim_p, [(self.prim_buf, "4f 4f 4f 4f 4f", "in_k", "in_ab", "in_c",
                                                      "in_col", "in_p")])
        atlas, _ = LB.build()
        self.atlas = ctx.texture((atlas.shape[1], atlas.shape[0]), 4, np.ascontiguousarray(atlas[::-1]).tobytes())
        self.atlas.build_mipmaps()
        self.atlas.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self.atlas.anisotropy = 4.0
        self.prim_p["u_atlas"].value = 3
        self.prim_p["u_res"].value = (width, height)

        def target(w, h, dtype="f2", comps=4):
            tex = ctx.texture((w, h), comps, dtype=dtype)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
            return tex, ctx.framebuffer(color_attachments=[tex])

        self.scene_tex, self.scene_fbo = target(width, height)
        self.acc_tex, self.acc_fbo = target(width, height, dtype="f4")
        self.levels = []
        w, h = width, height
        for _ in range(self.L.get("bloom_levels", 6)):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.fin_tex, self.fin_fbo = target(width, height, dtype="f1", comps=3)

    def _draw(self, t):
        ctx = self.ctx
        cam, prims, fade = TL.build(t, self.look)
        if len(prims) > self.cap:
            self.cap = len(prims) * 2
            self.prim_buf.orphan(self.cap * 80)
        self.scene_fbo.use()
        self.scene_fbo.clear(*BG, 1.0)
        if len(prims):
            ppu = self.H / cam[2]
            p = self.prim_p
            p["u_cam"].value = (float(cam[0]), float(cam[1]))
            p["u_ppu"].value = float(ppu)
            p["u_wpp"].value = float(1.0 / ppu)
            self.atlas.use(3)
            self.prim_buf.write(np.ascontiguousarray(prims, "f4").tobytes())
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
            self.prim_v.render(moderngl.POINTS, vertices=len(prims))
            ctx.disable(moderngl.BLEND)
        return fade

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            prog[k].value = v
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, fps=60, frame_idx=0):
        """Motion blur: `sub` sub-frames across the shutter (fraction of the frame interval), averaged."""
        ctx, L = self.ctx, self.L
        n = self.sub
        shutter = L["shutter"] / fps
        self.acc_fbo.use()
        self.acc_fbo.clear(0, 0, 0, 1)
        fade = 1.0
        for s in range(n):
            ts = t + ((s + 0.5) / n - 0.5) * shutter if n > 1 else t
            fade = self._draw(min(max(ts, 0.0), TL.DURATION))
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self._pass(self.acc_p, self.acc_v, self.acc_fbo, self.scene_tex, u_w=1.0 / n)
            ctx.disable(moderngl.BLEND)
        srct = self.acc_tex
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, srct, u_texel=(1 / srct.width, 1 / srct.height),
                       u_thresh=float(L["bloom_thresh"]) if i == 0 else 0.0)
            srct = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        self.fin_fbo.use()
        self.acc_tex.use(0); self.levels[0][0].use(1)
        c = self.comp_p
        c["scene"].value, c["bloom"].value = 0, 1
        c["u_bloom"].value = L["bloom"] * 0.5
        c["u_bloomTint"].value = (1.0, 1.0, 1.0)
        c["u_exposure"].value = L["exposure"]
        c["u_fade"].value = float(fade)
        c["u_vig"].value, c["u_scan"].value, c["u_grain"].value = L["vig"], 0.0, L["grain"]
        c["u_frame"].value = float(frame_idx % 997)
        c["u_res"].value = (self.W, self.H)
        c["u_linearOut"].value = 0.0
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        return self.fin_fbo.read(components=3, alignment=1)


# ── CLI ──────────────────────────────────────────────────────────────────────
def size_for(height):
    return int(round(height * 16 / 9 / 2) * 2), height


def save_png(buf, w, h, path):
    from PIL import Image
    img = Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    return img


def cmd_still(a):
    w, h = size_for(a.height)
    r = Renderer(w, h, a.look)
    OUT.mkdir(exist_ok=True)
    for t in a.t:
        t0 = time.time()
        path = OUT / f"still_{a.look}_{t:05.2f}s.png"
        save_png(r.frame(t), w, h, path)
        print(f"{path}  ({time.time() - t0:.2f}s)")


def cmd_looks(a):
    from PIL import Image, ImageDraw
    w, h = size_for(a.height)
    OUT.mkdir(exist_ok=True)
    tiles = {t: [] for t in a.t}
    for k in a.looks:
        r = Renderer(w, h, k)
        for t in a.t:
            t0 = time.time()
            tiles[t].append(save_png(r.frame(t), w, h, OUT / f"look_{k}_{t:05.2f}s.png"))
            print(f"look {k} t={t}  ({time.time() - t0:.2f}s)")
        r.ctx.release()
    for t in a.t:
        n = len(tiles[t])
        sheet = Image.new("RGB", (w * n + 10 * (n - 1), h + 30), (40, 40, 40))
        dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(tiles[t]):
            sheet.paste(im, (i * (w + 10), 30))
            dr.text((i * (w + 10) + 8, 8), f"look {a.looks[i]}   t = {t:.1f} s", fill=(220, 220, 220))
        path = OUT / f"looks_{t:05.2f}s.png"
        sheet.save(path)
        print(path)


SEG_FRAMES = 240


def _render_key(a):
    hsh = hashlib.sha1()
    for p in sorted([*HERE.glob("*.py"), *SH.glob("*")]):
        hsh.update(p.name.encode()); hsh.update(p.read_bytes())
    hsh.update(f"{a.look}|{a.height}|{a.fps}|{a.crf}|{a.preset}|{SEG_FRAMES}".encode())
    return hsh.hexdigest()[:12]


def cmd_video(a):
    """Resumable: frames are encoded in self-contained segments, then joined losslessly."""
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(TL.DURATION * fps))
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"physics_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    if a.fresh and segdir.exists():
        shutil.rmtree(segdir)
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"          # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"Physics{a.look}@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    r = None
    for k, (s, e) in enumerate(chunks):
        if seg(k).exists():
            continue
        r = r or Renderer(w, h, a.look, sub=a.sub)
        part = segdir / f"seg_{k:04d}.part.mp4"
        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "vflip",
             "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p", str(part)],
            stdin=subprocess.PIPE)
        for i in range(s, e):
            ff.stdin.write(r.frame(i / fps, fps, i))
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


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still"); s.add_argument("--t", type=float, nargs="+", default=[8.5])
    s.add_argument("--look", default="A"); s.add_argument("--height", type=int, default=540)
    s = sub.add_parser("looks"); s.add_argument("--t", type=float, nargs="+", default=[8.5])
    s.add_argument("--looks", nargs="+", default=["A", "B", "C"]); s.add_argument("--height", type=int, default=540)
    s = sub.add_parser("video"); s.add_argument("--look", default="A"); s.add_argument("--height", type=int, default=480)
    s.add_argument("--fps", type=int, default=30); s.add_argument("--crf", type=int, default=18)
    s.add_argument("--preset", default="medium"); s.add_argument("--out"); s.add_argument("--fresh", action="store_true")
    s.add_argument("--sub", type=int, default=None)
    a = ap.parse_args()
    {"still": cmd_still, "looks": cmd_looks, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
