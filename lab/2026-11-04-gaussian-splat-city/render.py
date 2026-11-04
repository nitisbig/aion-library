"""Gaussian Splat City Tour: 30 s hobby piece, rendered on the GPU (moderngl, headless on the Radeon R4).

    uv run python lab/2026-11-04-gaussian-splat-city/render.py looks                       # 6 stills × looks A/B/C
    uv run python lab/2026-11-04-gaussian-splat-city/render.py still --look A --t 2 6.5 11
    uv run python lab/2026-11-04-gaussian-splat-city/render.py video --look A --height 480 --fps 30    # preview
    uv run python lab/2026-11-04-gaussian-splat-city/render.py video --look A --height 1080 --fps 60   # final
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
import city as CT  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"
STRIDE = 20     # floats per splat (5 × vec4)


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return np.array([((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4)])


# One colour per object type for the whole piece. (hex, radiance)
LOOKS = {
    "A": dict(name="Neon night", pal=dict(
        BODY=("#2E3A58", 0.11), WIN_WARM=("#FFB36B", 2.4), WIN_COOL=("#A8D8FF", 2.0), GLASS=("#1B2740", 0.10),
        RIM=("#8A9CC8", 0.38), ROOF=("#2A3247", 0.13), NEON_A=("#22F2FF", 4.0), NEON_B=("#FF3FB0", 4.0),
        STREET=("#1A1D26", 0.10), SIDEWALK=("#2A2C33", 0.13), LANE=("#FFD9A0", 1.3), POLE=("#3A4050", 0.25),
        LAMP=("#FFC07A", 9.0), GROUND=("#151820", 0.08), TREE=("#1E5A44", 0.2), TRUNK=("#2E2620", 0.12),
        CAR_BODY=("#20242E", 0.15), CAR_HEAD=("#F2F6FF", 9.0), CAR_TAIL=("#FF1E2E", 6.0), BEAM=("#FFF1D8", 0.5),
        SPIRE=("#FFE2B0", 2.0), BEACON=("#FF2A2A", 6.0), FLOATER=("#5C8CFF", 0.35), PLAZA=("#2C2A2A", 0.14),
        SHOP=("#FFD7A6", 2.2)),
        lamp=("#FF9C4A", 0.55), glassA=("#3E7BFF", 0.45), glassB=("#FF5FC8", 0.12), seed=("#CFE6FF", 0.6),
        hueA="#2DE2FF", hueB="#FF4FC0", shadow=(0.92, 1.0, 1.1), high=(1.06, 1.0, 0.92), bloom=1.0, exposure=1.0),
    "B": dict(name="Golden scan", pal=dict(
        BODY=("#4A3418", 0.11), WIN_WARM=("#FFC067", 2.4), WIN_COOL=("#FFE7B8", 2.0), GLASS=("#3A2A16", 0.10),
        RIM=("#C89B5A", 0.42), ROOF=("#3E2E1A", 0.13), NEON_A=("#FFF0C8", 3.0), NEON_B=("#FF8A2A", 3.5),
        STREET=("#241A10", 0.10), SIDEWALK=("#30241A", 0.13), LANE=("#FFD58A", 1.3), POLE=("#4A3820", 0.25),
        LAMP=("#FFD9A0", 9.0), GROUND=("#1E1610", 0.08), TREE=("#5A4420", 0.22), TRUNK=("#3A2A18", 0.12),
        CAR_BODY=("#2A2016", 0.15), CAR_HEAD=("#FFF4E0", 9.0), CAR_TAIL=("#FF6A1E", 6.0), BEAM=("#FFE8C0", 0.5),
        SPIRE=("#FFF0D0", 2.2), BEACON=("#FF5A1E", 6.0), FLOATER=("#C08A40", 0.35), PLAZA=("#2E2418", 0.14),
        SHOP=("#FFD08A", 2.2)),
        lamp=("#FFB060", 0.55), glassA=("#FFB860", 0.4), glassB=("#FFE0A0", 0.1), seed=("#FFE2B0", 0.6),
        hueA="#FFC060", hueB="#FF7A30", shadow=(1.0, 0.97, 0.92), high=(1.08, 1.0, 0.86), bloom=1.0, exposure=1.0),
    "C": dict(name="Hologram", pal=dict(
        BODY=("#0E3A48", 0.14), WIN_WARM=("#B8FFFF", 1.8), WIN_COOL=("#7FE8FF", 1.6), GLASS=("#0A2A36", 0.12),
        RIM=("#6FF0FF", 0.7), ROOF=("#0E3442", 0.14), NEON_A=("#FFFFFF", 3.0), NEON_B=("#5CFFF0", 3.0),
        STREET=("#0A1E26", 0.10), SIDEWALK=("#0E2832", 0.13), LANE=("#9FFFFF", 1.4), POLE=("#1E5060", 0.3),
        LAMP=("#CFFFFF", 6.0), GROUND=("#081820", 0.08), TREE=("#127A7A", 0.2), TRUNK=("#0E3440", 0.12),
        CAR_BODY=("#0E2A34", 0.15), CAR_HEAD=("#E8FFFF", 7.0), CAR_TAIL=("#FFB020", 5.0), BEAM=("#CFFFFF", 0.4),
        SPIRE=("#E0FFFF", 2.0), BEACON=("#FFB020", 5.0), FLOATER=("#3FC8E0", 0.4), PLAZA=("#0E2C34", 0.14),
        SHOP=("#9FF8FF", 1.8)),
        lamp=("#6FE8FF", 0.4), glassA=("#7FE8FF", 0.5), glassB=("#FFFFFF", 0.08), seed=("#CFFFFF", 0.6),
        hueA="#5CF8FF", hueB="#C8FFFF", shadow=(0.95, 1.0, 1.05), high=(1.0, 1.0, 1.0), bloom=0.7, exposure=1.0),
}


def palette(look):
    L = LOOKS[look]
    pal = np.zeros((len(CT.KINDS), 3))
    for k, (hx, I) in L["pal"].items():
        pal[CT.K[k]] = lin(hx, I)
    return pal, lin(*L["lamp"])


def pack(A, pal, lamp):
    n = len(A["alpha"])
    o = np.zeros((n, STRIDE), "f4")
    o[:, 0:3] = A["pos"]
    o[:, 3] = A["alpha"]
    o[:, 4:8] = A["cov"][:, :4]
    o[:, 8:10] = A["cov"][:, 4:6]
    o[:, 10] = A["h"]
    o[:, 11] = A["group"]
    o[:, 12:15] = pal[A["kind"]] * A["var"][:, None] + lamp[None] * A["lit"][:, None]
    o[:, 15] = A["shk"]
    o[:, 16:19] = A["normal"]
    return o


def city_cached():
    key = hashlib.sha1((HERE / "city.py").read_bytes()).hexdigest()[:10]
    path = OUT / f"city_{key}.npz"
    if path.exists():
        z = np.load(path)
        return {k: z[k] for k in z.files}
    A = CT.build()
    A.pop("meta")
    OUT.mkdir(exist_ok=True)
    np.savez(path, **A)
    return A


def src(name):
    return "#version 430\n" + (SH / name).read_text()


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


class Renderer:
    def __init__(self, width, height, look="A"):
        self.W, self.H = W, H = width, height
        self.look = LOOKS[look]
        self.ctx = ctx = moderngl.create_context(standalone=True, require=430)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def full(fs):
            p = ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs))
            return p, ctx.vertex_array(p, [(quad, "2f", "in_pos")])

        self.res_p, self.res_v = full("resolve.frag")
        self.dof_p, self.dof_v = full("dof.frag")
        self.down_p, self.down_v = full("down.frag")
        self.up_p, self.up_v = full("up.frag")
        self.comp_p, self.comp_v = full("composite.frag")
        self.sp = ctx.program(vertex_shader=src("splat.vert"), fragment_shader=src("splat.frag"))

        t0 = time.time()
        A = city_cached()
        self.traffic = CT.Traffic()
        self.pal, self.lamp = palette(look)
        stat = pack(A, self.pal, self.lamp)
        self.n_static = len(stat)
        self.n = self.n_static + self.traffic.n
        self.pos_static = A["pos"].astype("f4")
        self.ssbo = ctx.buffer(reserve=self.n * STRIDE * 4)
        self.ssbo.write(stat.tobytes())
        self.idx = ctx.buffer(reserve=self.n * 4, dynamic=True)
        self.vao = ctx.vertex_array(self.sp, [(self.idx, "1u/i", "in_idx")])
        print(f"{self.n_static:,} static + {self.traffic.n:,} car splats ({time.time() - t0:.1f}s)")

        def target(w, h, dtype="f2", comps=4, n=1):
            texs = [ctx.texture((w, h), comps, dtype=dtype) for _ in range(n)]
            for t in texs:
                t.filter = (moderngl.LINEAR, moderngl.LINEAR)
                t.repeat_x = t.repeat_y = False
            return (texs[0] if n == 1 else texs), ctx.framebuffer(color_attachments=texs)

        self.acc = target(W, H, n=2)
        self.resT = target(W, H)
        self.dofT = target(W, H)
        self.levels = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        self.fin = target(W, H, "f1", 3)

        L = self.look
        for k, v in dict(u_glassA=tuple(lin(*L["glassA"])), u_glassB=tuple(lin(*L["glassB"])),
                         u_seedCol=tuple(lin(*L["seed"])), u_hueA=tuple(lin(L["hueA"], 1.4)),
                         u_hueB=tuple(lin(L["hueB"], 1.4)), u_res=(float(W), float(H)), u_band=150.0).items():
            setu(self.sp, k, v)

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def splats(self, t, cam, ev):
        ctx = self.ctx
        cars = self.traffic.at(ev["tau"])
        cpk = pack(cars, self.pal, self.lamp)
        self.ssbo.write(cpk.tobytes(), offset=self.n_static * STRIDE * 4)
        P = np.vstack([self.pos_static, cars["pos"].astype("f4")])
        # cull and sort back-to-front on the CPU (numpy argsort), upload the order as instance indices
        M = np.stack([cam["right"], cam["up"], cam["fwd"]], 1).astype("f4")
        V = (P - cam["pos"].astype("f4")) @ M
        tanY = np.tan(cam["fov"] / 2)
        tanX = tanY * self.W / self.H
        margin = 30.0 + 80.0 * (ev["diss_r"] < 700) + 40.0 * (ev["reveal_r"] < 600)
        z = V[:, 2]
        vis = (z > 0.4) & (np.abs(V[:, 0]) < z * tanX * 1.1 + margin) & (np.abs(V[:, 1]) < z * tanY * 1.1 + margin)
        ids = np.nonzero(vis)[0]
        order = ids[np.argsort(-z[ids], kind="quicksort")].astype("u4")
        self.idx.write(order.tobytes())

        fb = self.acc[1]
        fb.use()
        fb.clear(0, 0, 0, 0)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self.ssbo.bind_to_storage_buffer(0)
        p = self.sp
        tanY = float(np.tan(cam["fov"] / 2))
        for k, v in dict(u_cam=tuple(cam["pos"]), u_right=tuple(cam["right"]), u_up=tuple(cam["up"]),
                         u_fwd=tuple(cam["fwd"]), u_fy=self.H / (2 * tanY), u_tanY=tanY, u_tanX=tanY * self.W / self.H,
                         u_revealR=float(ev["reveal_r"]), u_seedVis=float(ev["seed_vis"]), u_scanY=float(ev["scan_y"]),
                         u_scanAmt=float(ev["scan_amt"]), u_scanW=float(ev["scan_w"]), u_dissR=float(ev["diss_r"]),
                         u_tau=float(ev["tau"])).items():
            setu(p, k, v)
        self.vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=len(order))
        ctx.disable(moderngl.BLEND)
        return len(order)

    af = None
    af_t = None

    def autofocus(self, t, cam):
        """Median depth of a patch at the frame centre, eased over ~0.25 s so focus pulls instead of jumping."""
        n = max(8, int(24 * self.H / 480))
        raw = self.resT[1].read(viewport=(self.W // 2 - n // 2, self.H // 2 - n // 2, n, n), components=4, dtype="f2")
        d = np.frombuffer(raw, "f2").reshape(-1, 4)[:, 3].astype("f4")
        d = d[d < 5e3]
        m = float(np.median(d)) if len(d) > n else cam["dist"]
        if self.af is None or self.af_t is None or not (0 < t - self.af_t < 0.2):
            self.af = m
        else:
            k = 1 - np.exp(-(t - self.af_t) / 0.25)
            self.af = float(np.exp(np.log(self.af) + (np.log(m) - np.log(self.af)) * k))
        self.af_t = t
        return self.af * (1 - cam["rack"]) + cam["rack_focus"] * cam["rack"]

    def frame(self, t, idx=0):
        ctx = self.ctx
        ev = TL.events(t)
        cam = TL.camera(t)
        self.splats(t, cam, ev)
        # resolve → autofocus → DOF
        self.resT[1].use()
        self.acc[0][0].use(0); self.acc[0][1].use(1)
        self.res_p["acc"].value, self.res_p["dep"].value = 0, 1
        self.res_v.render(moderngl.TRIANGLE_STRIP)
        cam["focus"] = self.autofocus(t, cam)
        self._pass(self.dof_p, self.dof_v, self.dofT[1], self.resT[0], u_res=(self.W, self.H), u_focus=cam["focus"],
                   u_k=float(ev["dof_k"]), u_max=12.0 * self.H / 480)
        # bloom (dual Kawase)
        s = self.dofT[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, s, u_texel=(1 / s.width, 1 / s.height),
                       u_thresh=0.3 if i == 0 else 0.0)
            s = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        # composite + grade
        self.fin[1].use()
        self.dofT[0].use(0); self.levels[0][0].use(1)
        c = self.comp_p
        c["scene"].value, c["bloom"].value = 0, 1
        L = self.look
        for k, v in dict(u_bloom=float(ev["bloom"] * L["bloom"]), u_exposure=L["exposure"], u_fade=float(ev["fade"]),
                         u_vig=0.45, u_grain=0.025, u_frame=float(idx % 997), u_zoom=float(ev["zoom"]),
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
    for i, t in enumerate(ts):
        t0 = time.time()
        im = to_img(r.frame(t, int(t * 60)), w, h)
        dt = time.time() - t0
        times.append(dt)
        im.save(OUT / f"still_{look}_{t:05.2f}s{tag}.png")
        ims.append(im)
        print(f"  look {look} t={t:5.2f}s  {dt:.2f}s/frame")
    if len(ims) > 1:
        sheet(ims, w, h, OUT / f"contact_{look}{tag}.png")
    r.ctx.release()
    return times


def cmd_still(a):
    stills(a.look, a.t, a.height)


def cmd_looks(a):
    for look in a.looks:
        times = stills(look, a.t, a.height)
        print(f"look {look}: mean {np.mean(times[1:] if len(times) > 1 else times):.2f}s/frame @ {a.height}p")


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
    out = Path(a.out) if a.out else OUT / f"splat_city_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"          # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"SplatCity@{h}p{fps}", unit="fr", dynamic_ncols=True,
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


SHOTS = [2.0, 6.5, 11.5, 19.0, 24.0, 27.6]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still")
    s.add_argument("--look", default="A", choices=list(LOOKS))
    s.add_argument("--t", type=float, nargs="+", default=SHOTS)
    s.add_argument("--height", type=int, default=480)
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
    {"still": cmd_still, "looks": cmd_looks, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
