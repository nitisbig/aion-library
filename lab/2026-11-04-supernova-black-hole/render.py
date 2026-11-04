"""Supernova → black hole: 30 s hobby piece on the GPU (moderngl) with a skia HUD.

    uv run python lab/2026-11-04-supernova-black-hole/render.py still --t 2 7 10.5 --height 540
    uv run python lab/2026-11-04-supernova-black-hole/render.py sheet --t 2 7 10 11 13.3 17 19 22 27 29.5 --height 270
    uv run python lab/2026-11-04-supernova-black-hole/render.py video --look A --height 480 --fps 30
    uv run python lab/2026-11-04-supernova-black-hole/render.py video --look A --height 1080 --fps 60 --crf 14 --preset slow
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
import astro as A  # noqa: E402
import blackbody as BB  # noqa: E402
import geodesics as G  # noqa: E402
import hud as HUD  # noqa: E402
import objects as OB  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"

LOOKS = {
    # A: crisp physical. 2× SSAA, bloom only on real highlights, no blur / CA / grain
    "A": dict(ssaa=2, mb=1, bloom=0.30, bloom_thresh=0.9, streak=0.0, streak_tint=(1, 1, 1), ca=0.0,
              grain=0.0, vig=0.22, grade=0.0),
    # B: cinematic. anamorphic streak on the flashes, teal/warm grade, 4-sample motion blur, light grain
    "B": dict(ssaa=1, mb=4, bloom=0.50, bloom_thresh=0.6, streak=0.09, streak_tint=(0.75, 0.88, 1.0), ca=0.6,
              grain=0.025, vig=0.35, grade=0.85),
}

DEFINES = {
    "B_C": G.B_C, "EPS": G.EPS, "Y0": G.Y0, "Y1": G.Y1, "PHI_MAX": G.PHI_MAX, "U_CMAX": G.U_CMAX,
    "NB": G.NB, "NPHI": G.NPHI, "NU": G.NU, "T_MIN": BB.T_MIN, "T_MAX": BB.T_MAX, "N_T": BB.N_T,
}
GW_SKY_AMP = 0.22


def src(name, common=False):
    head = "#version 330\n" + "".join(f"#define {k} {float(v):.10g}\n" for k, v in DEFINES.items())
    if common:
        head += (SH / "common.glsl").read_text()
    return head + (SH / name).read_text()


def noise_volume(n=128, seed=7):
    """Periodic band-limited noise, 4 independent channels, each rank-normalised to uniform [0, 1].
    Built in Fourier space, so it tiles seamlessly; cached."""
    path = OUT / f"noise{n}_{seed}.npy"
    if path.exists():
        return np.load(path)
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(n) * n
    kk = np.sqrt(k[:, None, None] ** 2 + k[None, :, None] ** 2 + k[None, None, :] ** 2)
    out = np.empty((n, n, n, 4), np.float16)
    for c, (slope, kmin, kmax) in enumerate(((1.9, 3.0, 40.0), (1.9, 3.0, 40.0), (1.5, 5.0, 56.0), (1.7, 3.0, 48.0))):
        amp = np.where((kk >= kmin) & (kk <= kmax), np.maximum(kk, 1.0) ** -slope, 0.0)
        f = np.fft.fftn(rng.standard_normal((n, n, n))) * amp
        v = np.real(np.fft.ifftn(f)).ravel()
        r = np.empty_like(v)
        r[np.argsort(v)] = np.linspace(0.0, 1.0, v.size)
        out[..., c] = r.reshape(n, n, n)
    OUT.mkdir(exist_ok=True)
    np.save(path, out)
    return out


def setu(prog, name, value):
    if name in prog:
        u = prog[name]
        if isinstance(value, list) and u.array_length < len(value):   # driver trimmed unused tail
            value = value[:u.array_length]
        u.value = value


class Renderer:
    def __init__(self, width, height, look="A"):
        self.L = L = LOOKS[look]
        self.ss = L["ssaa"]
        self.mb = L["mb"]
        self.OW, self.OH = width, height
        self.W, self.H = width * self.ss, height * self.ss
        self.ctx = ctx = moderngl.create_context(standalone=True)

        b, U, phi_end, status, PHC = G.load_tables()

        def ftex(arr, comps=1):
            arr = np.ascontiguousarray(arr, "f4")
            t = ctx.texture((arr.shape[1], arr.shape[0]), comps, arr.tobytes(), dtype="f4")
            t.filter = (moderngl.NEAREST, moderngl.NEAREST)
            return t

        self.t_phc = ftex(PHC)
        self.t_end = ftex(phi_end[None, :])
        self.t_bb = ftex(BB.table()[None, :, :], 3)
        nz = noise_volume()
        self.t_noise = ctx.texture3d(nz.shape[:3], 4, nz.tobytes(), dtype="f2")
        self.t_noise.repeat_x = self.t_noise.repeat_y = self.t_noise.repeat_z = True
        self.t_noise.build_mipmaps()
        self.t_noise.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self._units = ((self.t_noise, 0), (self.t_bb, 1), (self.t_phc, 2), (self.t_end, 3))

        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        mk = lambda fs, common=False: ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs, common))  # noqa: E731
        qv = lambda p: ctx.vertex_array(p, [(quad, "2f", "in_pos")])   # noqa: E731
        self.sky_p, self.mat_p = mk("sky.frag", True), mk("matter.frag", True)
        self.ns_p = mk("pulsar.frag")
        self.copy_p, self.down_p, self.up_p = mk("copy.frag"), mk("down.frag"), mk("up.frag")
        self.streak_p, self.comp_p, self.res_p = mk("streak.frag"), mk("composite.frag"), mk("resolve.frag")
        (self.sky_v, self.mat_v, self.ns_v, self.copy_v, self.down_v, self.up_v, self.streak_v,
         self.comp_v, self.res_v) = map(qv, (self.sky_p, self.mat_p, self.ns_p, self.copy_p, self.down_p,
                                             self.up_p, self.streak_p, self.comp_p, self.res_p))

        def target(w, h, dtype="f2", comps=4):
            tex = ctx.texture((w, h), comps, dtype=dtype)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
            return tex, ctx.framebuffer(color_attachments=[tex])

        W, H = self.W, self.H
        self.scene_tex, self.scene_fbo = target(W, H)
        self.acc_tex, self.acc_fbo = target(W, H)
        self.levels = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        sw, shh = max(1, W // 4), max(1, H // 4)
        self.streak = [target(sw, shh), target(sw, shh)]
        self.out_tex, self.out_fbo = target(W, H, dtype="f2" if self.ss > 1 else "f1", comps=3)
        self.fin_tex, self.fin_fbo = target(width, height, dtype="f1", comps=3)

        # static uniforms
        for p in (self.sky_p, self.mat_p):
            for name, unit in (("u_noise", 0), ("u_bb", 1), ("u_lutPhc", 2), ("u_phiEnd", 3)):
                setu(p, name, unit)
            setu(p, "u_aspect", W / H)
            setu(p, "u_ss", float(self.ss))
        sp = self.sky_p
        neb = OB.nebulae()
        setu(sp, "u_nebC", [tuple(n[0]) for n in neb])
        setu(sp, "u_nebR", [float(n[1]) for n in neb])
        setu(sp, "u_nebA", [tuple(n[2]) for n in neb])
        setu(sp, "u_nebB", [tuple(n[3]) for n in neb])
        setu(sp, "u_nebI", [float(n[4]) for n in neb])
        setu(sp, "u_nebSeed", [float(n[5]) for n in neb])
        pole, gc = OB.galactic_frame()
        setu(sp, "u_skyPole", tuple(pole))
        setu(sp, "u_skyGC", tuple(gc))
        gdir, grad = OB.globular()
        setu(sp, "u_gcDir", tuple(gdir))
        setu(sp, "u_gcR", float(grad))
        setu(sp, "u_gwAmp", GW_SKY_AMP)
        mp = self.mat_p
        setu(mp, "u_shellCol", [tuple(s[3]) for s in A.SHELLS])
        setu(mp, "u_Teff", A.T_EFF)
        setu(mp, "u_nuEnd", TL.S_BH - TL.S_BOUNCE)
        self.ns_spin, self.ns_m0 = OB.pulsar_axes()
        setu(self.ns_p, "u_spin", tuple(self.ns_spin))
        setu(self.ns_p, "u_aspect", W / H)
        self.hud = HUD.HUD(width, height)

    # ── one sub-frame of the HDR scene ──────────────────────────────────────────
    def _draw(self, s):
        ctx = self.ctx
        P = TL.params(s)
        n, right, up, fwd, fov = TL.camera(s)
        th = float(np.tan(fov / 2))
        for prog in (self.sky_p, self.mat_p, self.ns_p):
            setu(prog, "u_camN", tuple(n))
            setu(prog, "u_right", tuple(right))
            setu(prog, "u_up", tuple(up))
            setu(prog, "u_fwd", tuple(fwd))
            setu(prog, "u_tanHalf", th)
            setu(prog, "u_pix", 2 * th / self.H)
            setu(prog, "u_lensOn", P["lens"])
            setu(prog, "u_rcM", float(P["rcM"]))
        sp, mp = self.sky_p, self.mat_p
        setu(sp, "u_sky", P["sky"])
        setu(sp, "u_Tyr", float(P["T_yr"]))
        setu(sp, "u_camLy", tuple(n * P["D_km"] * A.KM / A.LY))
        setu(mp, "u_time", float(s))
        setu(mp, "u_T", float(P["T"]))
        for k, key in (("u_Rs", "Rs"), ("u_cut", "cut"), ("u_starOn", "star_on"), ("u_flash", "flash"),
                       ("u_core", "core"), ("u_coreMode", "core_mode"), ("u_coreHeat", "core_heat"),
                       ("u_bounceFlash", "bounce_flash"), ("u_shadow", "shadow"), ("u_shock", "shock"),
                       ("u_stalled", "stalled"), ("u_sasiA", "sasi_amp"), ("u_sasiPh", "sasi_phase"),
                       ("u_postShock", "post_shock"), ("u_ej", "ej"), ("u_ejT", "ej_T"), ("u_ejOp", "ej_op"),
                       ("u_ejI", "ej_I"), ("u_blast", "blast"), ("u_rem", "rem"), ("u_remNeb", "rem_neb"), ("u_remGlow", "rem_glow"),
                       ("u_nuOn", "nu_on")):
            setu(mp, k, float(P[key]))
        setu(mp, "u_shell", [float(x) for x in P["shells"]])
        setu(mp, "u_nuS", float(s - TL.S_BOUNCE))
        for tex, unit in self._units:
            tex.use(unit)

        self.scene_fbo.use()
        ctx.disable(moderngl.BLEND)
        self._tiled(self.sky_v)
        ctx.enable(moderngl.BLEND)
        if P["pulsar"] > 0:
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            L = 700.0
            ns = self.ns_p
            setu(ns, "u_cam", (0.0, 0.0, 0.0))
            setu(ns, "u_nsPos", tuple(OB.pulsar_dir(s, GW_SKY_AMP) * L))
            setu(ns, "u_ns", float(P["pulsar"]))
            setu(ns, "u_time", float(s))
            setu(ns, "u_beam", tuple(OB.pulsar_beam(s, self.ns_spin, self.ns_m0)))
            self._tiled(self.ns_v)
        ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self._tiled(self.mat_v)
        ctx.disable(moderngl.BLEND)
        return P

    TILES = (4, 3)    # heavy full-screen passes are split so no single draw call trips the amdgpu timeout

    def _tiled(self, vao):
        """Draw a full-screen pass in scissored tiles, waiting for each one (ctx.finish). The output is
        identical to one draw; the GPU just never runs a multi-second command (the driver kills those)."""
        fbo = self.scene_fbo
        nx, ny = self.TILES
        for j in range(ny):
            for i in range(nx):
                x0, x1 = self.W * i // nx, self.W * (i + 1) // nx
                y0, y1 = self.H * j // ny, self.H * (j + 1) // ny
                fbo.scissor = (x0, y0, x1 - x0, y1 - y0)
                vao.render(moderngl.TRIANGLE_STRIP)
                self.ctx.finish()
        fbo.scissor = None

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, s, fps=60, frame_idx=0, hud=True):
        ctx, L = self.ctx, self.L
        self.acc_fbo.use()
        self.acc_fbo.clear(0, 0, 0, 1)
        shutter = 0.5 / fps
        for i in range(self.mb):
            ts = s + ((i + 0.5) / self.mb - 0.5) * shutter if self.mb > 1 else s
            self._draw(float(np.clip(ts, 0.0, TL.DURATION)))
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self._pass(self.copy_p, self.copy_v, self.acc_fbo, self.scene_tex, u_scale=1.0 / self.mb)
            ctx.disable(moderngl.BLEND)
        P = TL.params(s)

        srct = self.acc_tex
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, srct, u_texel=(1 / srct.width, 1 / srct.height),
                       u_thresh=float(L["bloom_thresh"]) if i == 0 else 0.0)
            srct = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            st = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], st, u_texel=(1 / st.width, 1 / st.height))
        ctx.disable(moderngl.BLEND)

        (sa, fa), (sb, fb) = self.streak
        if L["streak"] > 0:
            src_t = self.levels[1][0]
            self._pass(self.streak_p, self.streak_v, fa, src_t, u_texel=(1 / sa.width, 1 / sa.height),
                       u_step=1.0, u_thresh=1.2)
            for step, (s_in, f_out) in zip((5.0, 25.0), ((sa, fb), (sb, fa))):
                self._pass(self.streak_p, self.streak_v, f_out, s_in, u_texel=(1 / sa.width, 1 / sa.height),
                           u_step=step, u_thresh=0.0)
        else:
            fa.clear(0, 0, 0, 1)

        self.out_fbo.use()
        self.acc_tex.use(0); self.levels[0][0].use(1); sa.use(2)
        c = self.comp_p
        setu(c, "scene", 0); setu(c, "bloom", 1); setu(c, "streak", 2)
        setu(c, "u_bloom", L["bloom"] * 0.07)
        setu(c, "u_streak", L["streak"])
        setu(c, "u_streakTint", L["streak_tint"])
        setu(c, "u_exposure", P["exposure"])
        setu(c, "u_fade", P["fade"])
        setu(c, "u_grain", L["grain"])
        setu(c, "u_ca", L["ca"])
        setu(c, "u_vig", L["vig"])
        setu(c, "u_grade", L["grade"])
        setu(c, "u_frame", float(frame_idx % 997))
        setu(c, "u_res", (self.W, self.H))
        setu(c, "u_linearOut", 1.0 if self.ss > 1 else 0.0)
        setu(c, "u_tanHalf", float(np.tan(TL.VFOV / 2)))
        setu(c, "u_aspect", self.W / self.H)
        rings = TL.gw_rings(s)
        setu(c, "u_gwR", [float(r[0]) for r in rings])
        setu(c, "u_gwA", [float(r[1]) for r in rings])
        setu(c, "u_gwW", [float(r[2]) for r in rings])
        setu(c, "u_gwPsi", float(0.5 + 0.9 * s))
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        if self.ss == 1:
            buf = self.out_fbo.read(components=3, alignment=1)
        else:
            self.fin_fbo.use()
            self.out_tex.use(0)
            setu(self.res_p, "tex", 0)
            setu(self.res_p, "u_ss", self.ss)
            self.res_v.render(moderngl.TRIANGLE_STRIP)
            buf = self.fin_fbo.read(components=3, alignment=1)
        frame = np.frombuffer(buf, np.uint8).reshape(self.OH, self.OW, 3).copy()
        if hud:
            a = TL.ramp(s, 0.4, 1.2) * (1.0 - TL.ramp(s, TL.DURATION - 1.0, TL.DURATION - 0.2))
            img, pos = self.hud.draw(s, a)
            HUD.blend(frame, img, pos, self.OH)
        return frame                                     # bottom-up rows


# ── CLI ─────────────────────────────────────────────────────────────────────
def size_for(height):
    return int(round(height * 16 / 9 / 2) * 2), height


def to_image(frame):
    from PIL import Image
    return Image.fromarray(frame[::-1])


def cmd_still(a):
    w, h = size_for(a.height)
    r = Renderer(w, h, a.look)
    OUT.mkdir(exist_ok=True)
    for t in a.t:
        t0 = time.time()
        path = OUT / f"still_{a.look}_{t:05.2f}s.png"
        to_image(r.frame(t)).save(path)
        print(f"{path}  ({time.time() - t0:.2f}s)")


def cmd_sheet(a):
    """Contact sheet of the key beats, one look per row."""
    from PIL import Image
    w, h = size_for(a.height)
    looks = list(a.looks)
    rows = []
    for k in looks:                                      # one GL context at a time
        r = Renderer(w, h, k)
        rows.append([to_image(r.frame(t)) for t in a.t])
        r.ctx.release()
    cols = min(len(a.t), a.cols)
    nrow = (len(a.t) + cols - 1) // cols
    for k, tiles in zip(looks, rows):
        sheet = Image.new("RGB", (cols * w + (cols - 1) * 6, nrow * h + (nrow - 1) * 6), (40, 40, 40))
        for i, im in enumerate(tiles):
            sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        path = OUT / f"contact_{k}.png"
        sheet.save(path)
        print(path)


SEG_FRAMES = 240


def _render_key(a):
    """Hash of everything that changes pixels: the shaders, the physics/timeline/HUD modules and the look.
    render.py itself is left out (its pipeline code doesn't change the image), so fixes such as tiling
    can resume a render. Use --fresh after editing anything in render.py that does change pixels."""
    hsh = hashlib.sha1()
    hsh.update(repr(LOOKS[a.look]).encode() + repr(GW_SKY_AMP).encode())
    for p in sorted([*(q for q in HERE.glob("*.py") if q.name != "render.py"), *SH.glob("*")]):
        hsh.update(p.name.encode())
        hsh.update(p.read_bytes())
    hsh.update(f"{a.look}|{a.height}|{a.fps}|{a.crf}|{a.preset}|{SEG_FRAMES}".encode())
    return hsh.hexdigest()[:12]


def cmd_video(a):
    """Resumable: frames are encoded in finished segments under out/segments/<key>/, then joined."""
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(TL.DURATION * fps))
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"supernova_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    if a.fresh and segdir.exists():
        shutil.rmtree(segdir)
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"                     # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"Supernova{a.look}@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    if done:
        tqdm.write(f"resuming: {done}/{n} frames already rendered in {segdir}")
    r = None
    for k, (s0, e) in enumerate(chunks):
        if seg(k).exists():
            continue
        r = r or Renderer(w, h, a.look)
        part = segdir / f"seg_{k:04d}.part.mp4"
        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "vflip",
             "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-pix_fmt", "yuv420p", str(part)],
            stdin=subprocess.PIPE)
        for i in range(s0, e):
            ff.stdin.write(r.frame(i / fps, fps, i).tobytes())
            bar.update(1)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError(f"ffmpeg failed on segment {k}")
        # decode-check before accepting: a corrupt segment once broke the concat silently
        chk = subprocess.run(["ffmpeg", "-v", "error", "-i", str(part), "-f", "null", "-"],
                             capture_output=True, text=True)
        if chk.stderr.strip():
            part.unlink()
            raise RuntimeError(f"segment {k} failed the decode check (re-run to redo it):\n{chk.stderr[:400]}")
        os.replace(part, seg(k))
    bar.close()
    lst = segdir / "list.txt"
    lst.write_text("".join(f"file '{seg(k).name}'\n" for k in range(len(chunks))))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    chk = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "null", "-"], capture_output=True, text=True)
    if chk.stderr.strip():
        raise RuntimeError(f"joined file failed the decode check:\n{chk.stderr[:400]}")
    print(f"✔ {n} frames → {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still"); s.add_argument("--t", type=float, nargs="+", default=[2.0])
    s.add_argument("--look", default="A"); s.add_argument("--height", type=int, default=540)
    s = sub.add_parser("sheet"); s.add_argument("--t", type=float, nargs="+",
                                                default=[2.0, 7.0, 10.0, 11.0, 13.3, 17.0, 19.0, 22.0, 27.0, 29.5])
    s.add_argument("--height", type=int, default=270); s.add_argument("--looks", default="A")
    s.add_argument("--cols", type=int, default=5)
    s = sub.add_parser("video"); s.add_argument("--look", default="A")
    s.add_argument("--height", type=int, default=480); s.add_argument("--fps", type=int, default=30)
    s.add_argument("--crf", type=int, default=16)
    s.add_argument("--preset", default="medium"); s.add_argument("--out", default=None)
    s.add_argument("--fresh", action="store_true", help="discard finished segments and start over")
    a = ap.parse_args()
    {"still": cmd_still, "sheet": cmd_sheet, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
