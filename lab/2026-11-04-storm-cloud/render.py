"""Storm Cloud: 30 s hobby piece, rendered on the GPU (moderngl, headless on the Radeon R4).

Per frame: blob transforms → particles splatted into a 3D density volume (compute) → light volume from the
lightning (compute) → ray march (half res) → bolts + droplet glints (full res) → light shafts, bloom, grade.

    uv run python lab/2026-11-04-storm-cloud/render.py looks                        # stills × looks A/B/C
    uv run python lab/2026-11-04-storm-cloud/render.py still --look A --t 5.6 11.8
    uv run python lab/2026-11-04-storm-cloud/render.py video --look A --height 480 --fps 30     # preview
    uv run python lab/2026-11-04-storm-cloud/render.py video --look A --height 1080 --fps 60    # final
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
import cloud as CL  # noqa: E402
import lightning as LG  # noqa: E402
import importlib  # noqa: E402

import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4))


LOOKS = {
    "A": dict(name="Storm noir", lcol=lin("#C8D8FF"), albedo=lin("#F2F4FA"), bolt=lin("#B8CCFF"),
              amb=lin("#8C9CC0"), under=0.0, underCol=lin("#000000"), rain=lin("#9CB0D8"),
              shadow=(0.94, 1.0, 1.1), high=(1.02, 1.0, 0.98), glint=1.0),
    "B": dict(name="Electric violet", lcol=lin("#C99BFF"), albedo=lin("#D8C8FF"), bolt=lin("#C8A4FF"),
              amb=lin("#6A74D0"), under=0.0, underCol=lin("#000000"), rain=lin("#9AA8FF"),
              shadow=(0.98, 0.92, 1.14), high=(1.0, 0.98, 1.04), glint=1.0),
    "C": dict(name="Ember storm", lcol=lin("#D0DEFF"), albedo=lin("#F6F2EC"), bolt=lin("#BCD0FF"),
              amb=lin("#7C8AA8"), under=0.006, underCol=lin("#FF8A3C"), rain=lin("#C8A890"),
              shadow=(0.92, 1.0, 1.1), high=(1.06, 1.0, 0.92), glint=1.0),
}
DUSK_LOOKS = {
    # sun just above the horizon: gold light, sun disk, warm horizon
    "D1": dict(name="Golden hour", lcol=lin("#B8A4FF"), albedo=lin("#FFFFFF"), bolt=lin("#C8B8FF"),
               amb=lin("#7484B8", 0.3), under=0.22, underCol=lin("#FF9C84"), rain=lin("#000000"),
               shadow=(0.9, 0.96, 1.12), high=(1.08, 1.0, 0.88), glint=1.0,
               sun_y=0.075, sunCol=lin("#FFC08A", 1.7), earthY=-20.0,
               skyZen=lin("#0C1430", 0.6), skyHorSun=lin("#FF8A40", 0.9), skyHorAway=lin("#9A5A78", 0.32),
               haze=lin("#B07070", 0.32)),
    # sun just set: pink alpenglow on the tops only (Earth's shadow), blue-violet below, lightning shows more
    "D2": dict(name="Afterglow", lcol=lin("#B49CFF"), albedo=lin("#FFFFFF"), bolt=lin("#C8B8FF"),
               amb=lin("#5864A8", 0.14), under=0.06, underCol=lin("#D8708A"), rain=lin("#000000"),
               shadow=(0.9, 0.94, 1.14), high=(1.08, 0.98, 0.94), glint=1.0,
               sun_y=-0.012, sunCol=lin("#FF8E9A", 1.5), earthY=6.6,
               skyZen=lin("#080C26", 0.6), skyHorSun=lin("#FF6A50", 0.75), skyHorAway=lin("#6A3E6C", 0.3),
               haze=lin("#7A4E6E", 0.28)),
}
SCENES = {
    "storm": dict(tl="timeline", looks=LOOKS, cloud=dict()),
    "dusk": dict(tl="timeline_dusk", looks=DUSK_LOOKS,
                 cloud=dict(rho=420.0, rain=False, haze=600_000, free=0, layout="massif")),
}
SIGMA = 7.0           # extinction per unit at density 1
EXPO = 1.0


def src(*names):
    return "#version 430\n" + "\n".join((SH / n).read_text() for n in names)


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


def _cached(name, fn, deps):
    key = hashlib.sha1(b"".join((HERE / d).read_bytes() for d in deps)).hexdigest()[:10]
    path = OUT / f"{name}_{key}.npz"
    if path.exists():
        z = np.load(path, allow_pickle=True)
        return z["data"].item()
    data = fn()
    OUT.mkdir(exist_ok=True)
    np.savez(path, data=np.array(data, dtype=object))
    return data


def worley_noise(n=64, seed=3):
    """Tileable billowy noise: inverted Worley fBm (3 octaves), in [0, 1]."""
    rng = np.random.default_rng(seed)
    g = (np.indices((n, n, n)).reshape(3, -1).T + 0.5) / n
    acc = np.zeros(len(g))
    for cells, amp in ((4, 0.625), (8, 0.25), (16, 0.125)):
        fp = rng.random((cells, cells, cells, 3))
        c = np.floor(g * cells).astype(int)
        best = np.full(len(g), 9.0)
        for o in np.array(np.meshgrid([-1, 0, 1], [-1, 0, 1], [-1, 0, 1])).reshape(3, -1).T:
            cc = c + o
            f = (cc + fp[cc[:, 0] % cells, cc[:, 1] % cells, cc[:, 2] % cells]) / cells
            best = np.minimum(best, np.linalg.norm(g - f, axis=1) * cells)
        acc += amp * (1 - np.clip(best, 0, 1))
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc.reshape(n, n, n).transpose(2, 1, 0).astype("f4")   # [z][y][x] for the GL upload


def scene_data(scene="storm"):
    """Cached scene: small things in a pickle, the (large) particle array as a memory-mapped .npy."""
    kw = SCENES[scene]["cloud"]
    deps = b"".join((HERE / d).read_bytes() for d in ("cloud.py", "lightning.py")) + repr(kw).encode()
    key = hashlib.sha1(deps).hexdigest()[:10]
    meta, parts = OUT / f"scene_{scene}_{key}.npz", OUT / f"parts_{scene}_{key}.npy"
    if not (meta.exists() and parts.exists()):
        C = CL.build(**kw)
        OUT.mkdir(exist_ok=True)
        np.save(parts, C.pop("parts"))
        small = dict(blobs=C["blobs"], ref=C["ref"], bolts=LG.grow_all(), noise=worley_noise(),
                     box_min=C["box_min"], box_max=C["box_max"], grid=C["grid"])
        np.savez(meta, data=np.array(small, dtype=object))
        del C
    D = np.load(meta, allow_pickle=True)["data"].item()
    D["parts"] = np.load(parts, mmap_mode="r")
    return D


class Renderer:
    def __init__(self, width, height, look="A", scene="storm"):
        self.W, self.H = W, H = width, height
        self.scene = scene
        self.TL = TL = importlib.import_module(SCENES[scene]["tl"])
        self.L = L = SCENES[scene]["looks"][look]
        self.rho = SCENES[scene]["cloud"].get("rho", CL.RHO)
        sd = None
        if "sun_y" in L:
            sd = np.array([TL.SUN_DIR[0], 0.0, TL.SUN_DIR[2]])
            sd = sd / np.linalg.norm(sd) * np.sqrt(1 - L["sun_y"] ** 2)
            sd[1] = L["sun_y"]
        self.sun = sd
        self.ctx = ctx = moderngl.create_context(standalone=True, require=430)
        t0 = time.time()
        D = scene_data(scene)
        self.D = D
        self.n = len(D["parts"])
        self.blobs = D["blobs"]
        self.pbuf = ctx.buffer(memoryview(np.ascontiguousarray(D["parts"])))
        self.bbuf = ctx.buffer(reserve=(len(self.blobs["r"]) + 1) * 32)
        self.pbuf.bind_to_storage_buffer(1)
        self.bbuf.bind_to_storage_buffer(0)
        self.res = tuple(int(v) for v in D["grid"])
        self.ires = tuple(int(v) for v in np.round(D["grid"] / 2))
        self.acc3 = ctx.texture3d(self.res, 1, dtype="u4")
        self.dens = ctx.texture3d(self.res, 1, dtype="f2")
        self.dens.repeat_x = self.dens.repeat_y = self.dens.repeat_z = False
        self.dens.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self.dens.build_mipmaps()
        self.illum = ctx.texture3d(self.ires, 4, dtype="f2")
        self.illum.repeat_x = self.illum.repeat_y = self.illum.repeat_z = False
        self.illum.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.sunVol = ctx.texture3d(self.ires, 1, dtype="f2")
        self.sunVol.repeat_x = self.sunVol.repeat_y = self.sunVol.repeat_z = False
        self.sunVol.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.noise = ctx.texture3d((64, 64, 64), 1, D["noise"].tobytes(), dtype="f4")
        self.noise.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        self.noise.build_mipmaps()
        # programs
        self.cs_clear = ctx.compute_shader(src("clear.comp"))
        self.cs_splat = ctx.compute_shader(src("common.glsl", "particles.glsl", "splat.comp"))
        self.cs_resolve = ctx.compute_shader(src("common.glsl", "resolve.comp"))
        self.cs_illum = ctx.compute_shader(src("common.glsl", "illum.comp"))
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def full(*fs):
            p = ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(*fs))
            return p, ctx.vertex_array(p, [(quad, "2f", "in_pos")])

        self.march_p, self.march_v = full("common.glsl", "march.frag")
        self.copy_p, self.copy_v = full("copy.frag")
        self.rays_p, self.rays_v = full("godrays.frag")
        self.down_p, self.down_v = full("down.frag")
        self.up_p, self.up_v = full("up.frag")
        self.comp_p, self.comp_v = full("composite.frag")
        self.glint_p = ctx.program(vertex_shader=src("common.glsl", "particles.glsl", "glint.vert"),
                                   fragment_shader=src("glint.frag"))
        self.glint_v = ctx.vertex_array(self.glint_p, [])
        self.bolt_p = ctx.program(vertex_shader=src("common.glsl", "bolt.vert"), fragment_shader=src("bolt.frag"))
        segs = []
        for i, name in enumerate(TL.BOLT_ORDER):
            s = D["bolts"][name]["segs"].copy()
            s[:, 10] = i
            segs.append(s)
        segs = np.concatenate(segs).astype("f4")
        self.nseg = len(segs)
        self.sbuf = ctx.buffer(segs.tobytes())
        self.bolt_v = ctx.vertex_array(self.bolt_p, [(self.sbuf, "4f 4f 4f/i", "in_a", "in_b", "in_f")])

        def target(w, h, dtype="f2", comps=4):
            t = ctx.texture((w, h), comps, dtype=dtype)
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            t.repeat_x = t.repeat_y = False
            return t

        self.hw, self.hh = W // 2, H // 2
        self.mcol = target(self.hw, self.hh)
        self.mdep = target(self.hw, self.hh, "f4", 1)
        self.mfb = ctx.framebuffer(color_attachments=[self.mcol, self.mdep])
        self.acc = target(W, H)
        self.accfb = ctx.framebuffer(color_attachments=[self.acc])
        self.rays = target(self.hw, self.hh)
        self.raysfb = ctx.framebuffer(color_attachments=[self.rays])
        self.levels = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            t = target(w, h)
            self.levels.append((t, ctx.framebuffer(color_attachments=[t])))
        self.fin = target(W, H, "f1", 3)
        self.finfb = ctx.framebuffer(color_attachments=[self.fin])

        cav = TL.cavity_path(16)
        s = np.linspace(0, 1, 16)
        rad = 1.3 + 1.1 * np.sin(np.pi * s) ** 0.7
        self.cav = np.c_[cav, rad].astype("f4")
        sunOn = self.sun is not None
        common = dict(u_boxMin=tuple(D["box_min"]), u_boxMax=tuple(D["box_max"]), u_cavOn=0.0 if sunOn else 1.0,
                      u_sunOn=1.0 if sunOn else 0.0, u_sunDir=tuple(self.sun) if sunOn else (0.0, 1.0, 0.0),
                      u_sunCol=L.get("sunCol", (0, 0, 0)), u_earthY=L.get("earthY", -99.0))
        px = H / 480
        self.common = common
        self.static = {
            self.cs_splat: dict(u_n=self.n, u_res=self.res,
                                u_rain=(CL.RAIN["top"], CL.RAIN["bottom"], 1.4)),
            self.cs_clear: dict(u_res=self.res),
            self.cs_resolve: dict(u_res=self.res, u_ref=float(D["ref"]), u_base=CL.BASE_Y),
            self.cs_illum: dict(u_ires=self.ires, u_sigma=SIGMA),
            self.march_p: dict(u_sigma=SIGMA, u_base=CL.BASE_Y, u_lcol=L["lcol"], u_albedo=L["albedo"],
                               u_under=L["under"], u_underCol=L["underCol"],
                               u_rainLo=(CL.RAIN["x"][0], CL.RAIN["bottom"], CL.RAIN["z"][0]) if not sunOn else (1e4,) * 3,
                               u_rainHi=(CL.RAIN["x"][1], CL.RAIN["top"], CL.RAIN["z"][1]) if not sunOn else (1e4,) * 3,
                               u_erode=0.5 if sunOn else 0.0, u_baseLod=0.7 if sunOn else 1.4,
                               u_anvilY=10.6 if sunOn else 8.2,
                               u_deckOn=1.0 if sunOn else 0.0, u_deckLo=-14.0, u_deckHi=-10.5,
                               u_skyZen=L.get("skyZen", (0, 0, 0)), u_skyHorSun=L.get("skyHorSun", (0, 0, 0)),
                               u_skyHorAway=L.get("skyHorAway", (0, 0, 0)), u_hazeCol=L.get("haze", (0, 0, 0))),
            self.glint_p: dict(u_px=px, u_lcol=L["lcol"], u_rainCol=L["rain"], u_maxSize=70.0 * px,
                               u_rainLo=(CL.RAIN["x"][0], CL.RAIN["bottom"], CL.RAIN["z"][0]),
                               u_rainHi=(CL.RAIN["x"][1], CL.RAIN["top"], CL.RAIN["z"][1]),
                               u_rain=(CL.RAIN["top"], CL.RAIN["bottom"], 1.4)),
            self.bolt_p: dict(u_px=px, u_sigma=SIGMA, u_W=float(W), u_H=float(H), u_boltCol=L["bolt"]),
        }
        for prog in (self.cs_splat, self.cs_clear, self.cs_resolve, self.cs_illum, self.march_p, self.glint_p,
                     self.bolt_p):
            for k, v in {**common, **self.static[prog]}.items():
                setu(prog, k, v)
            if "u_cav" in prog:
                prog["u_cav"].write(self.cav.tobytes())
        print(f"{self.n:,} particles, {len(self.blobs['r']):,} blobs, {self.nseg:,} bolt segments "
              f"({time.time() - t0:.1f}s)")

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            setu(prog, k, v)
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, idx=0, timing=None):
        ctx, L = self.ctx, self.L
        TL = self.TL
        ev = TL.events(t)
        cam = TL.camera(t)
        tb = ev["tb"]
        tanY = float(np.tan(cam["fov"] / 2))
        tanX = tanY * self.W / self.H
        la, lb, _ = TL.lights(t, self.D["bolts"])
        clk = [time.time()]
        # 1. particles → density
        self.bbuf.write(CL.blob_buffer(self.blobs, tb).tobytes())
        for prog in (self.cs_splat, self.cs_resolve, self.cs_illum, self.march_p, self.glint_p, self.bolt_p):
            setu(prog, "u_tb", tb)
            for nm, arr in (("u_la", la), ("u_lb", lb)):
                if nm in prog:
                    prog[nm].write(arr.tobytes())
        g = lambda n, k: (n + k - 1) // k                                       # noqa: E731
        self.acc3.bind_to_image(0, read=True, write=True)
        self.cs_clear.run(g(self.res[0], 8), g(self.res[1], 8), g(self.res[2], 4))
        ctx.memory_barrier()
        self.cs_splat.run(g(self.n, 256))
        ctx.memory_barrier()
        self.dens.bind_to_image(1, read=False, write=True)
        self.cs_resolve.run(g(self.res[0], 8), g(self.res[1], 8), g(self.res[2], 4))
        ctx.memory_barrier()
        self.dens.build_mipmaps()
        # 2. light volume
        self.dens.use(0)
        self.cs_illum["dens"].value = 0
        self.illum.bind_to_image(2, read=False, write=True)
        self.sunVol.bind_to_image(3, read=False, write=True)
        self.cs_illum.run(g(self.ires[0], 4), g(self.ires[1], 4), g(self.ires[2], 4))
        ctx.memory_barrier()
        if timing is not None:
            ctx.finish(); clk.append(time.time())
        camu = dict(u_cam=tuple(cam["pos"]), u_right=tuple(cam["right"]), u_up=tuple(cam["up"]),
                    u_fwd=tuple(cam["fwd"]), u_tanX=tanX, u_tanY=tanY)
        # 3. ray march (half res)
        self.mfb.use()
        self.mfb.clear(0, 0, 0, 0)
        self.dens.use(0); self.illum.use(1); self.noise.use(2); self.sunVol.use(4)
        mp = self.march_p
        if "sunVol" in mp:
            mp["sunVol"].value = 4
        mp["dens"].value, mp["illum"].value, mp["noiseTex"].value = 0, 1, 2
        for k, v in {**camu, "u_frame": float(idx), "u_pixAng": 2 * tanY / self.hh, "u_amb": tuple(np.array(L["amb"]) * ev["ambient"])}.items():
            setu(mp, k, v)
        ctx.disable(moderngl.BLEND)
        self.march_v.render(moderngl.TRIANGLE_STRIP)
        if timing is not None:
            ctx.finish(); clk.append(time.time())
        # 4. full res: march upsample, + bolts, + glints (additive)
        self._pass(self.copy_p, self.copy_v, self.accfb, self.mcol)
        ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        fy = self.H / (2 * tanY)
        bp = self.bolt_p
        self.dens.use(0)
        bp["dens"].value = 0
        bs = np.zeros((3, 4), "f4")
        for i, name in enumerate(self.TL.BOLT_ORDER):
            s = self.TL.bolt_state(name, t)
            bs[i] = (s["grow"], s["leader"], s["main"] * self.TL.BOLT_T[name]["I"] * 0.13, s["branch"])
        bp["u_bolt"].write(bs.tobytes())
        for k, v in {**camu, "u_fy": fy}.items():
            setu(bp, k, v)
        if bs[:, 0].max() >= 0:
            self.bolt_v.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=self.nseg)
        gp = self.glint_p
        self.illum.use(1); self.mdep.use(3)
        gp["illum"].value, gp["depthTex"].value = 1, 3
        self.sunVol.use(4)
        if "sunVol" in gp:
            gp["sunVol"].value = 4
        for k, v in {**camu, "u_fy": fy, "u_focus": ev["focus"], "u_aper": ev["aper"],
                     "u_glint": 0.04 * L["glint"] * CL.RHO / self.rho, "u_amb": tuple(np.array(L["amb"]) * ev["ambient"])}.items():
            setu(gp, k, v)
        if not os.environ.get("NO_GLINT"):
            self.glint_v.render(moderngl.POINTS, vertices=self.n)
        ctx.disable(moderngl.BLEND)
        if timing is not None:
            ctx.finish(); clk.append(time.time())
        # 5. light shafts toward the brightest light
        k = int(np.argmax(lb[:, 3]))
        c = 0.5 * (la[k, :3] + lb[k, :3]) - cam["pos"]
        z = c @ cam["fwd"]
        rays = 0.0
        center = (0.5, 0.5)
        if self.sun is not None:                     # dusk: shafts radiate from the sun
            c = self.sun * 100.0
            z = c @ cam["fwd"]
            k = 0
            lb = lb.copy(); lb[0, 3] = max(lb[0, 3], 1.0)
        if lb[k, 3] > 0 and z > 0.5:
            center = (0.5 + 0.5 * (c @ cam["right"]) / (z * tanX), 0.5 + 0.5 * (c @ cam["up"]) / (z * tanY))
            off = max(abs(center[0] - 0.5), abs(center[1] - 0.5))
            rays = ev["rays"] * float(np.clip(1.6 - off, 0, 1))
        if rays > 0:
            self._pass(self.rays_p, self.rays_v, self.raysfb, self.acc, u_center=center, u_frame=float(idx % 97))
        else:
            self.raysfb.clear(0, 0, 0, 0)
        # 6. bloom (dual Kawase)
        s = self.acc
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, s, u_texel=(1 / s.width, 1 / s.height),
                       u_thresh=0.6 if i == 0 else 0.0)
            s = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        # 7. composite + grade
        self.finfb.use()
        self.acc.use(0); self.levels[0][0].use(1); self.rays.use(2)
        c = self.comp_p
        c["scene"].value, c["bloom"].value, c["rays"].value = 0, 1, 2
        for k, v in dict(u_bloom=0.22 * ev["bloom"], u_rays=rays, u_exposure=EXPO * ev["exposure"], u_lift=ev["lift"],
                         u_fade=ev["fade"], u_vig=0.55, u_grain=0.035 if self.sun is None else 0.018, u_frame=float(idx % 997), u_zoom=ev["zoom"],
                         u_ca=ev["ca"], u_shadow=L["shadow"], u_high=L["high"],
                         u_res=(float(self.W), float(self.H))).items():
            setu(c, k, v)
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        ctx.finish()
        if timing is not None:
            clk.append(time.time())
            timing.append(np.diff(clk))
        return self.finfb.read(components=3, alignment=1)


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


def stills(look, ts, height, tag="", scene="storm"):
    w, h = size_for(height)
    r = Renderer(w, h, look, scene)
    OUT.mkdir(exist_ok=True)
    ims, times, timing = [], [], []
    for t in ts:
        t0 = time.time()
        im = to_img(r.frame(t, int(t * 60), timing), w, h)
        times.append(time.time() - t0)
        im.save(OUT / f"still_{look}_{t:05.2f}s{tag}.png")
        ims.append(im)
        st = " ".join(f"{x:.3f}" for x in timing[-1])
        print(f"  look {look} t={t:5.2f}s  {times[-1]:.2f}s/frame  [volume, march, draw, post] = {st}")
    if len(ims) > 1:
        sheet(ims, w, h, OUT / f"contact_{look}{tag}.png")
    r.ctx.release()
    return times


SEG_FRAMES = 150


def _render_key(a):
    hsh = hashlib.sha1()
    for p in sorted([*HERE.glob("*.py"), *SH.glob("*")]):
        hsh.update(p.name.encode()); hsh.update(p.read_bytes())
    hsh.update(f"{a.scene}|{a.look}|{a.height}|{a.fps}|{a.crf}|{SEG_FRAMES}".encode())
    return hsh.hexdigest()[:12]


def cmd_video(a):
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(importlib.import_module(SCENES[a.scene]["tl"]).DURATION * fps))
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"{'storm_cloud' if a.scene == 'storm' else 'dusk_cloud'}_{a.look}_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{a.look}_{h}p{fps}_{_render_key(a)}"
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"          # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"{'StormCloud' if a.scene == 'storm' else 'DuskCloud'}@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    r = None
    for k, (s, e) in enumerate(chunks):
        if seg(k).exists():
            continue
        r = r or Renderer(w, h, a.look, a.scene)
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


SHOTS = {"storm": [2.45, 5.65, 11.85, 16.45, 22.4, 23.66], "dusk": [1.0, 7.5, 13.5, 15.5, 22.0, 29.0]}
DEFAULT_LOOK = {"storm": "A", "dusk": "D1"}
ALL_LOOKS = [*LOOKS, *DUSK_LOOKS]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("still", "looks", "video"):
        s = sub.add_parser(name)
        s.add_argument("--scene", default="storm", choices=list(SCENES))
        s.add_argument("--height", type=int, default=480)
        if name == "looks":
            s.add_argument("--looks", nargs="+")
        else:
            s.add_argument("--look", choices=ALL_LOOKS)
        if name != "video":
            s.add_argument("--t", type=float, nargs="+")
        if name == "still":
            s.add_argument("--tag", default="")
        if name == "video":
            s.add_argument("--fps", type=int, default=30)
            s.add_argument("--crf", type=int, default=18)
            s.add_argument("--preset", default="medium")
            s.add_argument("--out")
    a = ap.parse_args()
    if a.cmd != "looks":
        a.look = a.look or DEFAULT_LOOK[a.scene]
        if a.look not in SCENES[a.scene]["looks"]:
            ap.error(f"look {a.look} doesn't belong to scene {a.scene}")
    if a.cmd != "video":
        a.t = a.t or SHOTS[a.scene]
    if a.cmd == "still":
        stills(a.look, a.t, a.height, a.tag, a.scene)
    elif a.cmd == "looks":
        for look in a.looks or list(SCENES[a.scene]["looks"]):
            ts = stills(look, a.t, a.height, scene=a.scene)
            print(f"look {look}: mean {np.mean(ts[1:] if len(ts) > 1 else ts):.2f}s/frame @ {a.height}p")
    else:
        cmd_video(a)


if __name__ == "__main__":
    main()
