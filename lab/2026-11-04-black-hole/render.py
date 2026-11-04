"""Black hole: 30 s hobby piece, ray-traced through Schwarzschild spacetime on the GPU.

    uv run python lab/2026-11-04-black-hole/render.py still --t 5 27 50 --height 540          # look B (default)
    uv run python lab/2026-11-04-black-hole/render.py looks --t 3 8 12 18 24 28      # A/B/C sheets
    uv run python lab/2026-11-04-black-hole/render.py video --look A --height 480 --fps 30
    uv run python lab/2026-11-04-black-hole/render.py video --look A --height 1080 --fps 60 --mb 4
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np
from tqdm import tqdm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blackbody as BB  # noqa: E402
import geodesics as G  # noqa: E402
import objects as OB  # noqa: E402
import space as SP  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4))


LOOKS = {
    # A: cinematic, warm blackbody, softened beaming, anamorphic streak
    "A": dict(Tpeak=4300.0, beam=1.6, shift=0.40, gain=1.1, mode=0, bloom=0.45, streak=0.06,
              streak_tint=(1.0, 0.78, 0.55), exposure=1.0, grain=0.035, ca=1.0, vig=0.5,
              ring_T=5200.0, ring_k=1.0, star_gain=1.0,
              ov_cap="#FFB347", ov_esc="#BFD8FF", ov_crit="#FFFFFF", ov_sphere="#FF8A3D"),
    # B: physical, full g^4 beaming and gravitational redshift
    "B": dict(Tpeak=6800.0, beam=4.0, shift=1.0, gain=0.30, mode=0, bloom=0.6, streak=0.0,
              streak_tint=(1.0, 1.0, 1.0), exposure=1.0, grain=0.035, ca=0.8, vig=0.5,
              ring_T=7500.0, ring_k=1.0, star_gain=1.0,
              ov_cap="#FF6E5A", ov_esc="#9FD3FF", ov_crit="#FFFFFF", ov_sphere="#FF6E5A",
              grid="#6FA8FF", grid_k=0.55, sphere="#FF6E5A", horizon="#FFFFFF", isco="#FFB347",
              warm="#FF8A5C", hot="#FFE2B0"),
    # C: spectral line art, iso-radius contours and co-rotating spokes
    "C": dict(Tpeak=6000.0, beam=2.0, shift=0.0, gain=1.0, mode=1, bloom=0.7, streak=0.12,
              streak_tint=(0.6, 0.85, 1.0), exposure=1.1, grain=0.03, ca=0.8, vig=0.45,
              ring_T=9000.0, ring_k=1.0, star_gain=1.0,
              ov_cap="#FF7FA8", ov_esc="#7FD8FF", ov_crit="#FFFFFF", ov_sphere="#FF7FA8"),
}

# Crisp family: look B's physical disk, 2× supersampling (linear-light downsample),
# no motion blur / chromatic aberration / grain, bloom only above a highlight threshold.
_CRISP = dict(LOOKS["B"], ssaa=2, mb_off=True, bloom=0.30, bloom_thresh=0.9, ca=0.0, grain=0.0,
              vig=0.22, star_boost=1.6, sky=0, sky_k=0.0)
LOOKS["S"] = dict(_CRISP)                                     # crisp, stars only
LOOKS["G"] = dict(_CRISP, sky=2, sky_k=1.0)                   # crisp + lensed galaxy band
LOOKS["K"] = dict(_CRISP, sky=1, sky_k=1.0)                   # crisp + lensed celestial grid
LOOKS["SO"] = dict(LOOKS["S"], objects=1.0)                   # + nebulae, supernova, galaxies, pulsar
LOOKS["GO"] = dict(LOOKS["G"], objects=1.0)

# celestial frame for the sky layers: pole tilted 25° off the disk axis; the galactic centre sits
# behind the hole as seen around the ignition (t ≈ 27 s), so the band wraps the shadow
_tilt = np.radians(25.0)
SKY_POLE = np.array([np.sin(_tilt), np.cos(_tilt), 0.0])
_behind = -TL.camera(27.0)[0]
_gc = _behind - np.dot(_behind, SKY_POLE) * SKY_POLE
SKY_GC = _gc / np.linalg.norm(_gc)

DEFINES = {
    "B_C": G.B_C, "EPS": G.EPS, "Y0": G.Y0, "Y1": G.Y1, "PHI_MAX": G.PHI_MAX, "U_CMAX": G.U_CMAX,
    "NB": G.NB, "NPHI": G.NPHI, "NU": G.NU, "R_IN": TL.R_IN, "R_OUT": TL.R_OUT,
    "T_MIN": BB.T_MIN, "T_MAX": BB.T_MAX, "N_T": BB.N_T,
}


def src(name, defines=False):
    head = "#version 330\n"
    if defines:
        head += "".join(f"#define {k} {float(v):.10g}\n" for k, v in DEFINES.items())
    return head + (SH / name).read_text()


# ── overlay geometry: exact photon paths for a beam arriving from screen-left ─
OVERLAY_B = [6.8, 5.6, 5.24, 5.1975, 5.19, 4.9, 3.9, 2.4]


def overlay_segments(look):
    right, up = (np.asarray(v) for v in TL.overlay_basis())
    bs = [s * b for b in OVERLAY_B for s in (1, -1)]
    rays = G.beam_rays(bs, r_max=17.0, r_out=9.0)
    # reveal order: gently bent rays first, the critical winders last
    order = np.argsort([-abs(abs(b) - G.B_C) for b in bs])
    rank = np.empty(len(bs)); rank[order] = np.arange(len(bs))
    rank = rank // 2 * 2 / 2 + 1          # pairs (±b) reveal together; 0 = photon sphere
    verts = []

    def add(pts2d, ray_id, col):
        p3 = pts2d[:, :1] * right + pts2d[:, 1:] * up
        s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(p3, axis=0), axis=1))])
        s /= s[-1]
        for i in range(len(p3) - 1):
            for j in (i, i + 1):
                verts.append([*p3[j], s[j], ray_id, *col])

    L = LOOKS[look]
    for b, pts, rid in zip(bs, rays, rank):
        if abs(abs(b) - G.B_C) < 0.02:
            col = lin(L["ov_crit"], 1.4)
        elif abs(b) < G.B_C:
            col = lin(L["ov_cap"], 0.9)
        else:
            col = lin(L["ov_esc"], 0.75)
        add(pts, rid, col)
    th = np.linspace(0, 2 * np.pi, 400)
    add(np.stack([3 * np.cos(th + np.pi), 3 * np.sin(th + np.pi)], 1), 0.0, lin(L["ov_sphere"], 0.35))
    return np.asarray(verts, "f4"), float(rank.max() + 1)


# ── renderer ────────────────────────────────────────────────────────────────
class Renderer:
    def __init__(self, width, height, look="A", mb=1):
        self.L = L = LOOKS[look]
        self.ss = L.get("ssaa", 1)
        self.OW, self.OH = width, height                        # output size
        width, height = width * self.ss, height * self.ss       # internal (supersampled) size
        self.W, self.H = width, height
        self.mb = 1 if L.get("mb_off") else mb
        self.ctx = ctx = moderngl.create_context(standalone=True)

        b, U, phi_end, status, PHC = G.load_tables()

        def ftex(arr, comps=1):
            arr = np.ascontiguousarray(arr, "f4")
            t = ctx.texture((arr.shape[1], arr.shape[0]), comps, arr.tobytes(), dtype="f4")
            t.filter = (moderngl.NEAREST, moderngl.NEAREST)
            return t

        self.t_u = ftex(U)                              # (NPHI rows, NB cols)
        self.t_phc = ftex(PHC)
        self.t_end = ftex(phi_end[None, :])
        self.t_bb = ftex(BB.table()[None, :, :], 3)

        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())
        qv = lambda p: ctx.vertex_array(p, [(quad, "2f", "in_pos")])   # noqa: E731
        mk = lambda fs, d=False: ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs, d))  # noqa: E731
        self.bh_p = mk("blackhole.frag", True)
        self.copy_p, self.down_p, self.up_p = mk("copy.frag"), mk("down.frag"), mk("up.frag")
        self.streak_p, self.comp_p = mk("streak.frag"), mk("composite.frag")
        self.res_p = mk("resolve.frag")
        self.res_v = qv(self.res_p)
        self.ns_p = mk("pulsar.frag")
        self.ns_v = qv(self.ns_p)
        self.bh_v, self.copy_v, self.down_v, self.up_v, self.streak_v, self.comp_v = map(
            qv, (self.bh_p, self.copy_p, self.down_p, self.up_p, self.streak_p, self.comp_p))

        self.line_p = ctx.program(vertex_shader=src("lines.vert"), geometry_shader=src("lines.geom"),
                                  fragment_shader=src("lines.frag"))
        verts, self.n_ray = overlay_segments(look)
        self.line_v = ctx.vertex_array(self.line_p, [(ctx.buffer(verts.tobytes()), "3f 1f 1f 3f",
                                                      "in_pos", "in_s", "in_ray", "in_col")])

        # act 1: dust streaks
        self.dust_p = ctx.program(vertex_shader=src("dust.vert", True), geometry_shader=src("dust.geom"),
                                  fragment_shader=src("dust.frag"))
        dust = SP.dust()
        self.dust_v = ctx.vertex_array(self.dust_p, [(ctx.buffer(dust.tobytes()), "3f 1f 1f 1f 1f",
                                                      "in_pos", "in_bright", "in_temp", "in_size", "in_kind")])
        # act 3: Flamm's paraboloid
        gl = LOOKS["B"] if "grid" not in L else L
        self.grid_p = ctx.program(vertex_shader=src("grid.vert"), geometry_shader=src("grid.geom"),
                                  fragment_shader=src("grid.frag"))
        gverts = SP.grid({"grid": lin(gl["grid"], gl["grid_k"]), "sphere": lin(gl["sphere"], 1.3),
                          "horizon": lin(gl["horizon"], 1.1), "isco": lin(gl["isco"], 1.1)})
        self.grid_v = ctx.vertex_array(self.grid_p, [(ctx.buffer(gverts.tobytes()), "2f 1f 1f 1f 1f 1f 1f 3f",
                                                      "in_xz", "in_r", "in_s", "in_t0", "in_dur", "in_kind",
                                                      "in_phase", "in_col")])
        gp = self.grid_p
        gp["u_res"].value = (width, height)
        gp["u_width"].value = 1.35 * height / 1080 * (1.3 if height < 700 else 1.0)
        gp["u_aspect"].value = width / height
        gp["u_hrim"].value = TL.H_RIM
        gp["u_rmax"].value = TL.GRID_R
        gp["u_warm"].value = lin(gl["warm"])
        gp["u_hot"].value = lin(gl["hot"])
        dp = self.dust_p
        dp["u_res"].value = (width, height)
        dp["u_wscale"].value = height / 1080 * (1.3 if height < 700 else 1.0)
        dp["u_aspect"].value = width / height
        dp["u_bb"].value = 3

        def target(w, h, dtype="f2", comps=4):
            tex = ctx.texture((w, h), comps, dtype=dtype)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
            return tex, ctx.framebuffer(color_attachments=[tex])

        self.scene_tex, self.scene_fbo = target(width, height)
        self.acc_tex, self.acc_fbo = target(width, height)
        self.levels = []
        w, h = width, height
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h))
        sw, shh = max(1, width // 4), max(1, height // 4)
        self.streak = [target(sw, shh), target(sw, shh)]
        # with supersampling the composite stays linear (f2) and the resolve pass applies gamma
        self.out_tex, self.out_fbo = target(width, height, dtype="f2" if self.ss > 1 else "f1", comps=3)
        self.fin_tex, self.fin_fbo = target(self.OW, self.OH, dtype="f1", comps=3)

        # static uniforms
        p = self.bh_p
        for name, tex, unit in (("u_lutU", self.t_u, 0), ("u_lutPhc", self.t_phc, 1),
                                ("u_phiEnd", self.t_end, 2), ("u_bb", self.t_bb, 3)):
            p[name].value = unit
        self._units = ((self.t_u, 0), (self.t_phc, 1), (self.t_end, 2), (self.t_bb, 3))
        p["u_aspect"].value = width / height
        p["u_Tpeak"].value, p["u_beam"].value, p["u_shift"].value = L["Tpeak"], L["beam"], L["shift"]
        p["u_gain"].value, p["u_mode"].value = L["gain"], float(L["mode"])
        p["u_starGain"].value = L["star_gain"]
        p["u_heroDir"].value = tuple(TL.hero_star_dir())
        p["u_ringTint"].value = tuple(BB.rgb(L["ring_T"])[0] * L["ring_k"])
        p["u_sky"].value = float(L.get("sky", 0))
        p["u_skyPole"].value = tuple(SKY_POLE)
        p["u_skyGC"].value = tuple(SKY_GC)
        p["u_ss"].value = float(self.ss)
        p["u_starBoost"].value = L.get("star_boost", 1.0)
        neb = OB.nebulae()
        p["u_nebC"].value = [tuple(n[0]) for n in neb]
        p["u_nebR"].value = [float(n[1]) for n in neb]
        p["u_nebA"].value = [tuple(n[2]) for n in neb]
        p["u_nebB"].value = [tuple(n[3]) for n in neb]
        p["u_nebI"].value = [float(n[4]) for n in neb]
        p["u_nebSeed"].value = [float(n[5]) for n in neb]
        p["u_snDir"].value = tuple(OB.supernova_dir())
        self.ns_pos, self.ns_spin, self.ns_m0 = OB.pulsar()
        self.ns_p["u_nsPos"].value = tuple(self.ns_pos)
        self.ns_p["u_spin"].value = tuple(self.ns_spin)
        self.ns_p["u_aspect"].value = width / height
        self.line_p["u_res"].value = (width, height)
        self.line_p["u_width"].value = 1.5 * height / 1080 * (1.3 if height < 700 else 1.0)
        self.line_p["u_aspect"].value = width / height
        self.line_p["u_nray"].value = self.n_ray

    def _draw(self, t):
        ctx, p = self.ctx, self.bh_p
        pos, right, up, fwd, fov = TL.camera(t)
        P = TL.params(t)
        th = float(np.tan(fov / 2))
        for prog in (p, self.line_p, self.dust_p, self.grid_p, self.ns_p):
            prog["u_cam"].value = tuple(pos)
            prog["u_right"].value, prog["u_up"].value, prog["u_fwd"].value = tuple(right), tuple(up), tuple(fwd)
            prog["u_tanHalf"].value = th
        p["u_pix"].value = 2 * th / self.H
        for k in ("gas", "front", "ignite", "disk", "drain", "tau", "stars", "hero", "ring", "sweep"):
            p[f"u_{k}"].value = float(P[k])
        p["u_ringW"].value = float(P["ring_w"])
        p["u_sweepAmp"].value = float(P["sweep_amp"])
        p["u_skyAmt"].value = float(P["stars"]) * self.L.get("sky_k", 0.0)
        O = OB.params(t)
        ok = self.L.get("objects", 0.0)
        p["u_objects"].value = float(O["objects"]) * ok
        p["u_snI"].value, p["u_snT"].value, p["u_snAge"].value = O["sn_I"], O["sn_T"], O["sn_age"]
        for tex, unit in self._units:
            tex.use(unit)
        self.scene_fbo.use()
        ctx.disable(moderngl.BLEND)
        if P["bh_on"]:
            self.bh_v.render(moderngl.TRIANGLE_STRIP)
        else:
            self.scene_fbo.clear(0, 0, 0, 1)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        if ok > 0 and O["ns"] > 0:
            n = self.ns_p
            n["u_ns"].value = float(O["ns"])
            n["u_time"].value = float(t)
            n["u_beam"].value = tuple(OB.pulsar_beam(t, self.ns_spin, self.ns_m0))
            self.ns_v.render(moderngl.TRIANGLE_STRIP)
        if P["dust"] > 0:
            pp, rp, upp, fp_, _ = TL.camera(max(t - 0.035, 0.0))
            d = self.dust_p
            d["u_camP"].value, d["u_rightP"].value = tuple(pp), tuple(rp)
            d["u_upP"].value, d["u_fwdP"].value = tuple(upp), tuple(fp_)
            d["u_dust"].value = float(P["dust"])
            self.t_bb.use(3)
            self.dust_v.render(moderngl.POINTS)
        if P["grid"] > 0:
            g = self.grid_p
            g["u_time"].value = float(t)
            g["u_sink"].value = float(P["sink"])
            g["u_pulse"].value = float(P["pulse"])
            g["u_alpha"].value = float(P["grid"])
            g["u_camDist"].value = float(np.linalg.norm(pos - np.array([0.0, -6.0, 0.0])))
            self.grid_v.render(moderngl.LINES)
        ctx.disable(moderngl.BLEND)
        if P["ov_alpha"] > 0:
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self.line_p["u_reveal"].value = float(P["ov_reveal"])
            self.line_p["u_alpha"].value = float(P["ov_alpha"])
            self.line_v.render(moderngl.LINES)
            ctx.disable(moderngl.BLEND)
        return P

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            prog[k].value = v
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, fps=60, frame_idx=0):
        ctx, L = self.ctx, self.L
        self.acc_fbo.use()
        self.acc_fbo.clear(0, 0, 0, 1)
        shutter = 0.5 / fps
        for i in range(self.mb):
            ts = t + ((i + 0.5) / self.mb - 0.5) * shutter if self.mb > 1 else t
            self._draw(min(max(ts, 0.0), TL.DURATION))
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            self._pass(self.copy_p, self.copy_v, self.acc_fbo, self.scene_tex, u_scale=1.0 / self.mb)
            ctx.disable(moderngl.BLEND)
        P = TL.params(t)

        # bloom pyramid
        srct = self.acc_tex
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, srct, u_texel=(1 / srct.width, 1 / srct.height),
                       u_thresh=float(L.get("bloom_thresh", 0.0)) if i == 0 else 0.0)
            srct = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)

        # anamorphic streak from the 1/4-res bloom level
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
        c["scene"].value, c["bloom"].value, c["streak"].value = 0, 1, 2
        c["u_bloom"].value = L["bloom"] * 0.07 * (1.0 - 0.55 * P["grid"])   # dense grid: keep the black black
        c["u_streak"].value = L["streak"]
        c["u_streakTint"].value = L["streak_tint"]
        c["u_exposure"].value = L["exposure"] * P["exposure_k"]
        c["u_fade"].value = P["fade"]
        c["u_grain"].value = L["grain"]
        c["u_ca"].value = L["ca"]
        c["u_vig"].value = L["vig"]
        c["u_frame"].value = float(frame_idx % 997)
        c["u_res"].value = (self.W, self.H)
        c["u_linearOut"].value = 1.0 if self.ss > 1 else 0.0
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        if self.ss == 1:
            return self.out_fbo.read(components=3, alignment=1)    # bottom-up rows
        self.fin_fbo.use()
        self.out_tex.use(0)
        self.res_p["tex"].value = 0
        self.res_p["u_ss"].value = self.ss
        self.res_v.render(moderngl.TRIANGLE_STRIP)
        return self.fin_fbo.read(components=3, alignment=1)


# ── CLI ─────────────────────────────────────────────────────────────────────
def size_for(height):
    return int(round(height * 16 / 9 / 2) * 2), height


def save_png(buf, w, h, path):
    from PIL import Image
    img = Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    return img


def cmd_still(a):
    w, h = size_for(a.height)
    r = Renderer(w, h, a.look, mb=a.mb)
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
    tiles_by_t = {t: [] for t in a.t}
    for k in (a.looks.split(",") if "," in a.looks else list(a.looks)):   # one GL context at a time
        r = Renderer(w, h, k)
        for t in a.t:
            tiles_by_t[t].append(save_png(r.frame(t), w, h, OUT / f"look_{k}_{t:05.2f}s.png"))
        r.ctx.release()
    for t in a.t:
        tiles = tiles_by_t[t]
        n = len(tiles)
        sheet = Image.new("RGB", (w * n + 10 * (n - 1), h), (40, 40, 40))
        for i, im in enumerate(tiles):
            sheet.paste(im, (i * (w + 10), 0))
        path = OUT / f"looks_{t:05.2f}s.png"
        sheet.save(path)
        print(path)


SEG_FRAMES = 240     # 4 s at 60 fps: at most this much work is lost if a render is interrupted


def _render_key(a):
    """Segments are reusable only if the code and settings that made them are unchanged."""
    import hashlib
    hsh = hashlib.sha1()
    for p in sorted([*HERE.glob("*.py"), *SH.glob("*")]):
        hsh.update(p.name.encode())
        hsh.update(p.read_bytes())
    hsh.update(f"{a.look}|{a.height}|{a.fps}|{a.mb}|{a.crf}|{a.preset}|{SEG_FRAMES}".encode())
    return hsh.hexdigest()[:12]


def cmd_video(a):
    """Resumable: frames are encoded in finished, self-contained segments under out/segments/<key>/.
    Re-running the same command after a crash or power cut skips the segments already done, then
    joins them losslessly (concat demuxer, stream copy)."""
    import os
    import shutil
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(TL.DURATION * fps))
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"blackhole_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    if a.fresh and segdir.exists():
        shutil.rmtree(segdir)
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"                     # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"BlackHole{a.look}@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    if done:
        tqdm.write(f"resuming: {done}/{n} frames already rendered in {segdir}")
    r = None
    for k, (s, e) in enumerate(chunks):
        if seg(k).exists():
            continue
        r = r or Renderer(w, h, a.look, mb=a.mb)
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
        os.replace(part, seg(k))                                     # atomic: a segment exists only when complete
    bar.close()
    lst = segdir / "list.txt"
    lst.write_text("".join(f"file '{seg(k).name}'\n" for k in range(len(chunks))))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    print(f"✔ {n} frames → {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still"); s.add_argument("--t", type=float, nargs="+", default=[12.0])
    s.add_argument("--look", default="B"); s.add_argument("--height", type=int, default=540)
    s.add_argument("--mb", type=int, default=1)
    s = sub.add_parser("looks"); s.add_argument("--t", type=float, nargs="+", default=[12.0])
    s.add_argument("--height", type=int, default=360); s.add_argument("--looks", default="ABC")
    s = sub.add_parser("video"); s.add_argument("--look", default="B")
    s.add_argument("--height", type=int, default=480); s.add_argument("--fps", type=int, default=30)
    s.add_argument("--mb", type=int, default=1); s.add_argument("--crf", type=int, default=16)
    s.add_argument("--preset", default="medium"); s.add_argument("--out", default=None)
    s.add_argument("--fresh", action="store_true", help="discard finished segments and start over")
    a = ap.parse_args()
    {"still": cmd_still, "looks": cmd_looks, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
