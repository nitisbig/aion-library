"""Neural network: 30 s hobby piece. A real MNIST digit recognizer counting down 9 → 0, on the GPU (moderngl).

    uv run python lab/2026-11-04-neural-network/render.py still --t 2 8 11 16 23 26 --look A
    uv run python lab/2026-11-04-neural-network/render.py looks --t 7.5 11.8 16.6 25.8      # A/B/C sheets
    uv run python lab/2026-11-04-neural-network/render.py video --look A --height 480 --fps 30
    uv run python lab/2026-11-04-neural-network/render.py video --look A --height 1080 --fps 60
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
import layout as LY  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4))


LOOKS = {
    # A: neon glass. Cyan (+w) / magenta (−w), white-hot cores, amber learning wave, strong bloom
    "A": dict(pos="#22E3FF", neg="#FF3DA6", hot="#FFF6E8", grad="#FFB13B", glass="#8FE6FF", win="#FFFFFF",
              dust="#6FB9FF", particle="#BFF4FF", base=0.55, pulse=1.0, trail=9.0, width=1.25, rim=1.1,
              body=0.82, core=2.2, bloom=1.0, bloom_thresh=0.25, bloom_tint=(1.0, 1.0, 1.0),
              dof=1.0, vig=0.45, scan=0.0, grain=0.02, exposure=1.0),
    # B: bioluminescent. Teal / amber, coral learning wave, softer and wider glow, more depth of field
    "B": dict(pos="#2FF5BE", neg="#FF9B3D", hot="#F4FFE6", grad="#FF5E7A", glass="#6CFFD8", win="#F4FFE6",
              dust="#5FFFD0", particle="#C8FFE9", base=0.48, pulse=0.9, trail=5.5, width=1.5, rim=0.8,
              body=0.7, core=2.0, bloom=1.35, bloom_thresh=0.12, bloom_tint=(0.85, 1.0, 0.95),
              dof=1.8, vig=0.55, scan=0.0, grain=0.025, exposure=0.95),
    # C: hologram. Ice-blue monochrome (+w bright ice, −w deep blue), white wave, crisp, little bloom
    "C": dict(pos="#A8DEFF", neg="#3F6BFF", hot="#FFFFFF", grad="#FFFFFF", glass="#BFE6FF", win="#FFFFFF",
              dust="#8FBFFF", particle="#E6F6FF", base=0.5, pulse=0.85, trail=12.0, width=0.95, rim=1.4,
              body=0.55, core=2.8, idle=0.2, bloom=0.6, bloom_thresh=0.45, bloom_tint=(0.8, 0.9, 1.0),
              dof=0.35, vig=0.35, scan=1.0, grain=0.0, exposure=1.05, ink="#CFEBFF", glyph="#7FC8FF"),
    # D: crisp & colourful. A hue per layer, no depth of field / scanlines / grain, bloom only on the hottest
    # flashes, thin 1-px-AA lines, solid lit spheres, crisp glyphs. (v3, current)
    "D": dict(hot="#FFFFFF", dust="#7F93B0", particle="#FFFFFF", ink="#EAF4FF", base=0.42, pulse=1.0,
              trail=14.0, width=0.85, rim=0.6, body=0.95, core=1.25, idle=0.32, halo=0.22, neg_k=0.55,
              glyph_glow=0.12, bloom=0.10, bloom_thresh=0.95, bloom_tint=(1.0, 1.0, 1.0), dof=0.0,
              vig=0.18, scan=0.0, grain=0.0, exposure=1.0, layer_k=(0.5, 0.62, 0.7, 0.78, 0.85, 0.92, 1.0, 1.0)),
}
MARGIN = 3.0          # node sprite half-size in sphere radii (room for the halo)
SSAA = 2


FONT = Path.home() / ".local/share/fonts/inter/InterVariable.ttf"


def glyph_atlas(cell=256):
    """10 digit glyphs side by side. R = crisp mask, G = wide gaussian glow."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    font = ImageFont.truetype(str(FONT), int(cell * 0.78))
    try:
        font.set_variation_by_name("Light")
    except Exception:
        pass
    mask = Image.new("L", (cell * 10, cell), 0)
    dr = ImageDraw.Draw(mask)
    for d in range(10):
        dr.text((cell * d + cell / 2, cell / 2), str(d), fill=255, font=font, anchor="mm")
    glow = mask.filter(ImageFilter.GaussianBlur(cell * 0.06))
    a = np.stack([np.asarray(mask), np.asarray(glow)], -1).astype("f4") / 255
    a[..., 1] = np.minimum(a[..., 1] * 1.8, 1.0)
    return np.ascontiguousarray(a[::-1])          # GL rows bottom-up


def setu(prog, name, value):
    """Set a uniform if the shader uses it (looks carry parameters some shaders don't need)."""
    if name in prog:
        prog[name].value = value


def src(name):
    return "#version 330\n" + (SH / name).read_text()


def particles(seed=5, n=14000):
    rng = np.random.default_rng(seed)
    e = rng.integers(0, TL.NE, n).astype("f4")
    u0 = rng.random(n)
    speed = rng.uniform(0.35, 0.8, n)
    size = rng.uniform(0.6, 1.4, n)
    jit = rng.normal(0, 0.035, (n, 2))
    return np.column_stack([e, u0, speed, size, jit, TL.EL[e.astype(int)]]).astype("f4")


def dust(seed=3, n=900):
    rng = np.random.default_rng(seed)
    pos = rng.uniform([-22, -11, -16], [22, 11, 16], (n, 3))
    vel = rng.normal(0, 0.05, (n, 3)) + [0.04, 0.015, 0.0]
    b = rng.uniform(0.05, 0.35, n) ** 2 * 3
    return np.column_stack([pos, vel, b]).astype("f4")


class Renderer:
    def __init__(self, width, height, look="A"):
        self.L = L = LOOKS[look]
        self.OW, self.OH = width, height
        self.W, self.H = W, H = width * SSAA, height * SSAA
        self.ctx = ctx = moderngl.create_context(standalone=True)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)

        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        mk = lambda fs: ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs))  # noqa: E731
        qv = lambda p: ctx.vertex_array(p, [(quad, "2f", "in_pos")])                           # noqa: E731
        self.down_p, self.up_p, self.comp_p, self.res_p = (mk(f) for f in
                                                           ("down.frag", "up.frag", "composite.frag", "resolve.frag"))
        self.down_v, self.up_v, self.comp_v, self.res_v = map(qv, (self.down_p, self.up_p, self.comp_p, self.res_p))

        self.edge_p = ctx.program(vertex_shader=src("edge.vert"), geometry_shader=src("edge.geom"),
                                  fragment_shader=src("edge.frag"))
        self.edge_v = ctx.vertex_array(self.edge_p, [(ctx.buffer(LY.edge_lines(TL.CTRL, TL.EL).tobytes()),
                                                      "3f 1f 1f 1f", "in_pos", "in_s", "in_e", "in_l")])
        self.node_p = ctx.program(vertex_shader=src("node.vert"), fragment_shader=src("node.frag"))
        self.node_buf = ctx.buffer(reserve=(TL.NN + 1) * 11 * 4, dynamic=True)
        self.node_v = ctx.vertex_array(self.node_p, [(self.node_buf, "3f 1f 1f 1f 1f 1f 3f", "in_pos", "in_r",
                                                      "in_reveal", "in_act", "in_grad", "in_kind", "in_col")])
        self.part_p = ctx.program(vertex_shader=src("particle.vert"), fragment_shader=src("particle.frag"))
        pb = particles()
        self.n_part = len(pb)
        self.part_v = ctx.vertex_array(self.part_p, [(ctx.buffer(pb.tobytes()), "1f 1f 1f 1f 2f 1f",
                                                      "in_e", "in_u0", "in_speed", "in_size", "in_jit", "in_l")])
        self.dust_p = ctx.program(vertex_shader=src("dust.vert"), fragment_shader=src("dust.frag"))
        self.dust_v = ctx.vertex_array(self.dust_p, [(ctx.buffer(dust().tobytes()), "3f 3f 1f",
                                                      "in_pos", "in_vel", "in_b")])

        self.spr_p = ctx.program(vertex_shader=src("sprite.vert"), fragment_shader=src("sprite.frag"))
        self.spr_buf = ctx.buffer(reserve=4 * TL.N_INK * 10 * 4 + 8192, dynamic=True)
        self.spr_v = ctx.vertex_array(self.spr_p, [(self.spr_buf, "3f 1f 1f 1f 1f 3f", "in_pos", "in_size", "in_b",
                                                    "in_kind", "in_param", "in_col")])
        at = glyph_atlas()
        self.atlas = ctx.texture((at.shape[1], at.shape[0]), 2, at.tobytes(), dtype="f4")
        self.atlas.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.atlas.repeat_x = self.atlas.repeat_y = False

        self.edge_tex = ctx.texture((TL.NE, 2), 4, dtype="f4")
        self.edge_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        ctrl = np.ascontiguousarray(np.transpose(TL.CTRL, (1, 0, 2)), "f4")      # (4, NE, 3)
        self.ctrl_tex = ctx.texture((TL.NE, 4), 3, ctrl.tobytes(), dtype="f4")
        self.ctrl_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)

        def target(w, h, dtype="f2", comps=4):
            tex = ctx.texture((w, h), comps, dtype=dtype)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
            return tex, ctx.framebuffer(color_attachments=[tex])

        self.scene_tex, self.scene_fbo = target(W, H)
        self.levels = []
        w, h = W, H
        for _ in range(7):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.out_tex, self.out_fbo = target(W, H, comps=3)
        self.fin_tex, self.fin_fbo = target(width, height, dtype="f1", comps=3)

        # static uniforms
        for p in (self.edge_p, self.node_p, self.part_p, self.dust_p, self.spr_p):
            for k, v in (("u_aspect", W / H), ("u_H", float(H)), ("u_dof", L["dof"])):
                setu(p, k, v)
        e = self.edge_p
        e["u_res"].value = (W, H)
        e["u_width"].value = L["width"] * H / 1080 * (1.25 if height < 700 else 1.0)
        lc = tuple(tuple(LY.lin(c)) for c in LY.LAYER_COLS)
        for k, v in (("u_pos", lin(L.get("pos", "#FFFFFF"))), ("u_neg", lin(L.get("neg", "#FFFFFF"), L.get("neg_k", 0.72))),
                     ("u_hot", lin(L["hot"])), ("u_grad", lin(L.get("grad", "#FFFFFF"))), ("u_base", L["base"]),
                     ("u_pulse", L["pulse"]), ("u_trail", L["trail"]), ("u_edge", 0), ("u_negK", L.get("neg_k", 0.6)),
                     ("u_layerK", tuple(L.get("layer_k", (0.55, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0)))), ("u_lc", lc)):
            setu(e, k, v)
        n = self.node_p
        for k, v in (("u_margin", MARGIN), ("u_hot", lin(L["hot"])), ("u_rim", L["rim"]), ("u_body", L["body"]),
                     ("u_core", L["core"]), ("u_idle", L.get("idle", 0.0)), ("u_halo", L.get("halo", 0.25))):
            setu(n, k, v)
        sp = self.spr_p
        for k, v in (("u_atlas", 2), ("u_ink", lin(L.get("ink", L["particle"]))), ("u_hot", lin(L["hot"])),
                     ("u_glow", L.get("glyph_glow", 0.5))):
            setu(sp, k, v)
        pp = self.part_p
        for k, v in (("u_edge", 0), ("u_ctrl", 1), ("u_col", lin(L["particle"])), ("u_psize", 1.0 * H / 1080),
                     ("u_gain", 1.2), ("u_lc", lc)):
            setu(pp, k, v)
        self.dust_p["u_col"].value = lin(L["dust"])

    def _camera(self, t):
        pos, right, up, fwd, fov, dist = TL.camera(t)
        th = float(np.tan(fov / 2))
        for p in (self.edge_p, self.node_p, self.part_p, self.dust_p, self.spr_p):
            p["u_cam"].value = tuple(pos)
            p["u_right"].value, p["u_up"].value, p["u_fwd"].value = tuple(right), tuple(up), tuple(fwd)
            p["u_tanHalf"].value = th
            setu(p, "u_focus", float(dist))
        return pos, fwd

    def _draw(self, t):
        ctx, S = self.ctx, TL.state(t)
        cam, fwd = self._camera(t)
        A = np.stack([S["e_reveal"], S["w"], S["e_phase"], S["e_amp"]], 1)
        B = np.stack([S["e_back"], S["e_gamp"], S["e_glow"], S["e_gglow"]], 1)
        self.edge_tex.write(np.ascontiguousarray(np.stack([A, B]), "f4").tobytes())

        self.scene_fbo.use()
        self.scene_fbo.clear(0, 0, 0, 1)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        self.dust_p["u_time"].value = float(t)
        self.dust_p["u_amt"].value = float(S["dust"])
        self.dust_v.render(moderngl.POINTS)
        self.edge_tex.use(0)
        self.edge_p["u_alpha"].value = 1.0
        self.edge_v.render(moderngl.LINES)
        self.ctrl_tex.use(1)
        self.part_p["u_time"].value = float(t)
        self.part_v.render(moderngl.POINTS)

        # nodes: back to front, premultiplied "over" so the glass bodies occlude what's behind
        kind = np.where(TL.LAYER == TL.NL - 1, 0.3, 0.0)
        r = LY.RADIUS[TL.LAYER] * S["scale"]
        nodes = np.column_stack([S["pos"], r, S["reveal"], S["act"], S["grad"], kind, S["col"]])
        seed = np.array([[*TL._IN_CENTER, 0.09, 1.0, S["seed"], 0.0, 1.0, *LY.lin(LY.LAYER_COLS[0])]])
        nodes = np.vstack([nodes, seed])
        depth = (nodes[:, :3] - cam) @ fwd
        nodes = nodes[np.argsort(-depth)]
        self.node_buf.write(np.ascontiguousarray(nodes, "f4").tobytes())
        ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self.node_v.render(moderngl.POINTS)
        spr = np.ascontiguousarray(S["sprites"], "f4")
        if len(spr):
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self.atlas.use(2)
            self.spr_buf.write(spr.tobytes())
            self.spr_v.render(moderngl.POINTS, vertices=len(spr))
        ctx.disable(moderngl.BLEND)
        return S

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            prog[k].value = v
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, frame_idx=0):
        ctx, L = self.ctx, self.L
        S = self._draw(t)
        srct = self.scene_tex
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

        self.out_fbo.use()
        self.scene_tex.use(0); self.levels[0][0].use(1)
        c = self.comp_p
        c["scene"].value, c["bloom"].value = 0, 1
        c["u_bloom"].value = L["bloom"] * 0.35
        c["u_bloomTint"].value = L["bloom_tint"]
        c["u_exposure"].value = L["exposure"]
        c["u_fade"].value = float(S["fade"])
        c["u_vig"].value, c["u_scan"].value, c["u_grain"].value = L["vig"], L["scan"], L["grain"]
        c["u_frame"].value = float(frame_idx % 997)
        c["u_res"].value = (self.W, self.H)
        c["u_linearOut"].value = 1.0
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        self.fin_fbo.use()
        self.out_tex.use(0)
        self.res_p["tex"].value = 0
        self.res_p["u_ss"].value = SSAA
        self.res_v.render(moderngl.TRIANGLE_STRIP)
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
    from PIL import Image
    w, h = size_for(a.height)
    OUT.mkdir(exist_ok=True)
    tiles = {t: [] for t in a.t}
    for k in a.looks:
        r = Renderer(w, h, k)
        for t in a.t:
            tiles[t].append(save_png(r.frame(t), w, h, OUT / f"look_{k}_{t:05.2f}s.png"))
        r.ctx.release()
    for t in a.t:
        n = len(tiles[t])
        sheet = Image.new("RGB", (w * n + 10 * (n - 1), h), (40, 40, 40))
        for i, im in enumerate(tiles[t]):
            sheet.paste(im, (i * (w + 10), 0))
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
    out = Path(a.out) if a.out else OUT / f"neural_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    if a.fresh and segdir.exists():
        shutil.rmtree(segdir)
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"          # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"Neural{a.look}@{h}p{fps}", unit="fr", dynamic_ncols=True,
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
             "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p", str(part)],
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


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still"); s.add_argument("--t", type=float, nargs="+", default=[11.8])
    s.add_argument("--look", default="D"); s.add_argument("--height", type=int, default=540)
    s = sub.add_parser("looks"); s.add_argument("--t", type=float, nargs="+", default=[11.8])
    s.add_argument("--height", type=int, default=540); s.add_argument("--looks", default="ABC")
    s = sub.add_parser("video"); s.add_argument("--look", default="D")
    s.add_argument("--height", type=int, default=480); s.add_argument("--fps", type=int, default=30)
    s.add_argument("--crf", type=int, default=16); s.add_argument("--preset", default="medium")
    s.add_argument("--out", default=None); s.add_argument("--fresh", action="store_true")
    a = ap.parse_args()
    {"still": cmd_still, "looks": cmd_looks, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
