"""Human cell → DNA: 45 s hobby piece on the GPU (moderngl, headless on the Radeon R4).

    uv run python lab/2026-11-04-human-cell-dna/render.py still --t 3 9 15 20 25 29 33 37 43
    uv run python lab/2026-11-04-human-cell-dna/render.py video --height 480 --fps 30      # preview
    uv run python lab/2026-11-04-human-cell-dna/render.py video --height 1080 --fps 60     # final (not yet)
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
import anatomy as AN  # noqa: E402
import dna as DN  # noqa: E402
import timeline as TL  # noqa: E402

OUT = HERE / "out"
SH = HERE / "shaders"
TILE = 128


def lin(hex_color, k=1.0):
    h = hex_color.lstrip("#")
    return np.array([((int(h[i:i + 2], 16) / 255) ** 2.2) * k for i in (0, 2, 4)])


# look A: bioluminescent. One colour per object type for the whole piece.
CELL_COLS = dict(C_MEM="#3FD8FF", C_CYTO="#1C5C8A", C_RIBO="#A8ECFF", C_ENV="#9B7BFF", C_PORE="#E2D4FF",
                 C_CHROM="#FF4FB8", C_NUCLEOLUS="#FF9AD8", C_ER="#2F9BFF", C_GOLGI="#3DFFB0", C_MITO="#FF8A2C",
                 C_CRISTA="#FFC266", C_LYSO="#C8FF4A", C_VES="#8FFFF0", C_MT="#CFE8FF", C_MOTE="#6FB8FF")
DNA_COL = "#7FD4FF"
STRAND = ("#8FE3FF", "#5F8FFF")
BASE_COL = dict(A="#FF4F6A", T="#FFC145", G="#3FF59A", C="#3FA8FF")
HISTONE_COL = ("#B46CFF", "#8C7CFF", "#FF5FB4", "#FF8ACD")      # H3, H4, H2A, H2B
DUST_COL = "#3A5A80"


def src(name):
    return "#version 330\n" + (SH / name).read_text()


def setu(prog, name, value):
    if name in prog:
        prog[name].value = value


# ── molecular geometry (cached) ──────────────────────────────────────────────
def chromatin():
    key = hashlib.sha1((HERE / "dna.py").read_bytes()).hexdigest()[:10]
    path = OUT / f"chromatin_{key}.npz"
    if path.exists():
        z = np.load(path, allow_pickle=True)
        return dict(beads=z["beads"], hist=z["hist"], hero=z["hero"].item())
    C = DN.build_chromatin()
    OUT.mkdir(exist_ok=True)
    np.savez(path, beads=C["beads"], hist=C["hist"], hero=np.array(C["hero"], dtype=object))
    return C


def static_spheres(C, seed=21):
    b = C["beads"]
    stripe = 0.72 + 0.28 * np.cos(2 * np.pi * b[:, 3])
    bead = np.column_stack([b[:, :3], np.full(len(b), DN.DNA_R), lin(DNA_COL)[None] * stripe[:, None],
                            np.zeros(len(b)), np.zeros(len(b))])
    h = C["hist"]
    hcol = np.array([lin(c) for c in HISTONE_COL])[h[:, 4].astype(int)]
    hist = np.column_stack([h[:, :3], h[:, 3], hcol, np.full(len(h), 0.05), np.zeros(len(h))])
    # nucleoplasm crowding: free proteins, kept away from the hero DNA's paths
    rng = np.random.default_rng(seed)
    hero = C["hero"]
    n = 14000
    pos = DN.unit(rng.normal(size=(n, 3))) * (DN.TERRITORY_R * 1.1 * rng.random((n, 1)) ** (1 / 3))
    T0 = DN.unit(hero["P"][1] - hero["P"][0])
    rel = pos - hero["P"][0]
    s = np.clip(rel @ T0, 0, 100)
    d_line = np.linalg.norm(rel - s[:, None] * T0, axis=1)
    d_path = np.min(np.linalg.norm(pos[:, None, :] - hero["P"][None, ::6], axis=2), axis=1)
    keep = (d_line > 9) & (d_path > 9) & (np.linalg.norm(pos - hero["ctr"], axis=1) > 18)
    pos = pos[keep]
    r = rng.uniform(1.0, 3.2, len(pos))
    col = lin(DUST_COL)[None] * rng.uniform(0.4, 1.0, (len(pos), 1))
    dust = np.column_stack([pos, r, col, np.zeros(len(pos)), np.ones(len(pos))])
    return np.ascontiguousarray(np.vstack([bead, hist, dust]), "f4")


class Hero:
    """The hero nucleosome: full-detail DNA (phosphates, sugars, bases, hydrogen bonds) + histone octamer."""

    def __init__(self, C, seed=5):
        self.H = DN.HeroDNA(C["hero"])
        self.n = self.H.n
        self.curve = C["hero"]["curve"]
        self.curve_idx = C["hero"]["curve_idx"]
        rng = np.random.default_rng(seed)
        blobs, kind = DN.octamer_blobs()
        pts, ks = [], []
        for b, k in zip(blobs, kind):
            for _ in range(30):
                p = b + DN.unit(rng.normal(size=3)) * 1.2 * rng.random() ** 0.5
                rad = rng.uniform(0.5, 0.78)
                rr = np.hypot(p[0], p[1])
                if rr > 3.05 - rad:                  # stay inside the DNA gyres (DNA surface at 3.18 nm)
                    p[:2] *= (3.05 - rad) / rr
                p[2] = np.clip(p[2], -2.3 + rad, 2.3 - rad)
                pts.append([*p, rad])
                ks.append(k)
        self.hloc = np.array(pts)
        self.hcol = np.array([lin(c) for c in HISTONE_COL])[ks]
        # 8 N-terminal tails, leaving between the gyres
        self.tails = []
        for i, (b, k) in enumerate(zip(blobs, kind)):
            out = DN.unit(np.array([b[0], b[1], 0.0]) + [0, 0, 0.6 * np.sign(b[2])])
            self.tails.append((b, out, k, rng.uniform(0, 6.28)))
        self.R0 = C["hero"]["R"]
        self.basis = np.stack([self.H.T0, self.H.N0, self.H.B0], 1)
        TL.set_nucleosome_axis(self.basis.T @ (self.R0 @ np.array([0, 0, 1.0])))
        seq = self.H.seq
        self.b1 = np.array([lin(BASE_COL[c]) for c in seq])
        self.b2 = np.array([lin(BASE_COL[DN.COMP[c]]) for c in seq])
        self.pur = np.array([c in DN.PURINE for c in seq])
        self.nhb = np.array([DN.HBONDS[c] for c in seq])
        self.cache = {}

    def state(self, t, ev):
        H = self.H
        P, F, M, hc, free = H.centreline(ev["unwrap"])
        n = self.n
        fi = H.wa + ev["unwrap"] * (n - 1 - H.wa + 8)
        g = (n - 1) - ev["unzip"] * (n - 1 - 128)
        return dict(P=P, F=F, M=M, hc=hc, fi=fi, g=g)

    def spheres(self, t, ev, S):
        P, F, g = S["P"], S["F"], S["g"]
        n = self.n
        i = np.arange(n)
        Tn, Nn, Bn = F[:, :, 0], F[:, :, 1], F[:, :, 2]
        phi = i * DN.TWIST
        e = lambda th: np.cos(th)[:, None] * Nn + np.sin(th)[:, None] * Bn   # noqa: E731
        th1, th2 = phi, phi + DN.GROOVE
        view = self.basis @ DN.unit(np.array([0.0, 0.92, 0.39]))
        m = DN.unit(np.cross(self.basis[:, 0], view))
        sep = np.clip((i - g) / 10.0, 0, 1)
        o = sep * np.minimum(0.9 + 0.08 * np.maximum(i - g, 0), 5.0)
        off1, off2 = m[None] * o[:, None], -m[None] * o[:, None]
        P1 = P + DN.R_P * e(th1) + off1
        P2 = P + DN.R_P * e(th2) + off2
        S1c = P + DN.R_SUGAR * e(th1 + 0.3)
        S2c = P + DN.R_SUGAR * e(th2 - 0.3)
        S1, S2 = S1c + off1, S2c + off2
        endf = TL.ss(0, 10, i) * TL.ss(0, 10, n - 1 - i)
        out = []

        def add(pos, r, col, emit, k=None):
            k = endf if k is None else k
            out.append(np.column_stack([pos, np.broadcast_to(r, (len(pos),)), col * k[:, None],
                                        np.broadcast_to(emit, (len(pos),)), np.full(len(pos), 2.0)]))

        s1c, s2c = lin(STRAND[0]), lin(STRAND[1])
        add(P1, 0.3, np.broadcast_to(s1c, (n, 3)), 0.15)
        add(P2, 0.3, np.broadcast_to(s2c, (n, 3)), 0.15)
        for f in (1 / 3, 2 / 3):          # smooth sugar-phosphate ribbon between phosphates
            add(P1[:-1] * (1 - f) + P1[1:] * f, 0.25, np.broadcast_to(s1c, (n - 1, 3)), 0.12, endf[:-1])
            add(P2[:-1] * (1 - f) + P2[1:] * f, 0.25, np.broadcast_to(s2c, (n - 1, 3)), 0.12, endf[:-1])
        add(S1, 0.26, np.broadcast_to(s1c * 0.6, (n, 3)), 0.05)
        add(S2, 0.26, np.broadcast_to(s2c * 0.6, (n, 3)), 0.05)
        chord = S2c - S1c
        lat = DN.unit(np.cross(Tn, chord))
        f1 = np.where(self.pur, 0.56, 0.44)
        for a in np.linspace(0.13, 1.0, 4):
            u1 = 0.1 + a * (f1 - 0.12)
            u2 = 0.9 - a * (0.9 - f1 - 0.02)
            for sgn in (-1, 1):
                add(S1c + chord * u1[:, None] + lat * 0.11 * sgn + off1, 0.17, self.b1, 0.25)
                add(S1c + chord * u2[:, None] + lat * 0.11 * sgn + off2, 0.17, self.b2, 0.25)
        # hydrogen bonds: 2 (A–T) or 3 (G–C); flash as they break, then gone
        hb_e = 0.9 + 7.0 * np.exp(-((sep - 0.12) / 0.07) ** 2)
        alive = sep < 0.33
        mid = S1c + chord * f1[:, None]
        for j, sl in enumerate((-0.2, 0.0, 0.2)):
            ok = alive & ((self.nhb == 3) | (j != 1))
            pos = mid + lat * (sl if True else 0) + (off1 + off2) * 0
            pos = np.where((self.nhb == 2)[:, None] & (j == 0), mid - lat * 0.12, pos)
            pos = np.where((self.nhb == 2)[:, None] & (j == 2), mid + lat * 0.12, pos)
            pos = pos + (off1 + off2) / 2
            add(pos[ok], 0.075, np.broadcast_to(np.ones(3), (ok.sum(), 3)), hb_e[ok][:, None][:, 0] if ok.any() else 0.0,
                endf[ok])

        # histone octamer, carried by the not-yet-peeled DNA, then drifting away when free
        H = self.H
        drift = float(np.clip((S["fi"] - H.wb - 2) / 45.0, 0, 1))
        away = DN.unit(S["hc"] - P[H.wb]) if drift > 0 else np.zeros(3)
        ctr = S["hc"] + away * 35 * drift ** 1.5
        vis = 1 - drift
        R = S["M"] @ self.R0
        if vis > 0.01:
            pos = self.hloc[:, :3] @ R.T + ctr
            out.append(np.column_stack([pos, self.hloc[:, 3], self.hcol * vis, np.full(len(pos), 0.06),
                                        np.full(len(pos), 2.0)]))
            for b, ou, k, ph in self.tails:
                j = np.arange(1, 8)
                side = DN.unit(np.cross(ou, [0, 0, 1.0]) + 1e-6)
                wig = (np.sin(t * 2.3 + j * 0.6 + ph)[:, None] * side + np.cos(t * 1.7 + j * 0.5 + ph)[:, None]
                       * np.array([0, 0, 1.0])) * 0.09 * j[:, None]
                loc = b + ou * (1.6 + 0.42 * j[:, None]) + wig
                pos = loc @ R.T + ctr
                fl = 0.25 + 0.35 * (0.5 + 0.5 * np.sin(t * 6.0 + ph * 3 + j))
                out.append(np.column_stack([pos, np.full(7, 0.28), np.broadcast_to(lin(HISTONE_COL[k]) * vis, (7, 3)),
                                            fl, np.full(7, 2.0)]))
        return np.ascontiguousarray(np.vstack(out), "f4"), ctr

    def target_source(self, t, S, ctr):
        P = S["P"]
        n = self.n

        def at(x):
            x = float(np.clip(x, 0, n - 1))
            i = int(np.floor(x))
            j = min(i + 1, n - 1)
            return P[i] * (1 - (x - i)) + P[j] * (x - i)

        def src(name):
            if name == "fibre":
                idx = self.curve_idx - 170 + 170 * TL.sss(18.0, 24.4, t)
                return self.curve[int(np.clip(idx, 0, len(self.curve) - 1))]
            if name == "histone":
                return ctr
            if name == "peel":
                return at(S["fi"] - 6)
            if name == "glide":
                return at(150 + 70 * TL.ss(30.8, 34.6, t))
            if name == "fork":
                return at(S["g"] + 2)
            raise KeyError(name)
        return src


class Renderer:
    def __init__(self, width, height):
        self.W, self.H = W, H = width, height
        self.ctx = ctx = moderngl.create_context(standalone=True)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], "f4").tobytes())

        def full(fs):
            p = ctx.program(vertex_shader=src("quad.vert"), fragment_shader=src(fs))
            return p, ctx.vertex_array(p, [(quad, "2f", "in_pos")])

        self.cell_p, self.cell_v = full("cell.frag")
        self.dof_p, self.dof_v = full("dof.frag")
        self.mix_p, self.mix_v = full("mix.frag")
        self.down_p, self.down_v = full("down.frag")
        self.up_p, self.up_v = full("up.frag")
        self.comp_p, self.comp_v = full("composite.frag")

        self.sph_p = ctx.program(vertex_shader=src("sphere.vert"), fragment_shader=src("sphere.frag"))
        t0 = time.time()
        C = chromatin()
        stat = static_spheres(C)
        self.n_static = len(stat)
        fmt = ("3f 1f 3f 1f 1f", "in_pos", "in_r", "in_col", "in_emit", "in_group")
        self.stat_v = ctx.vertex_array(self.sph_p, [(ctx.buffer(stat.tobytes()), *fmt)])
        self.hero = Hero(C)
        self.hero_buf = ctx.buffer(reserve=16000 * 9 * 4, dynamic=True)
        self.hero_v = ctx.vertex_array(self.sph_p, [(self.hero_buf, *fmt)])
        print(f"geometry: {self.n_static} static spheres ({time.time() - t0:.1f}s)")

        def target(w, h, dtype="f4", comps=4, depth=False):
            tex = ctx.texture((w, h), comps, dtype=dtype)
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            tex.repeat_x = tex.repeat_y = False
            att = dict(color_attachments=[tex])
            if depth:
                att["depth_attachment"] = ctx.depth_renderbuffer((w, h))
            return tex, ctx.framebuffer(**att)

        self.cellT = target(W, H)
        self.molT = target(W, H, depth=True)
        self.dofA = target(W, H, "f2")
        self.dofB = target(W, H, "f2")
        self.mixT = target(W, H, "f2")
        self.levels = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.levels.append(target(w, h, "f2"))
        self.fin = target(W, H, "f1", 3)
        for tgt in (self.dofA, self.dofB):
            tgt[1].clear(0, 0, 0, 1)

        # cell world static uniforms
        c = self.cell_p
        L = AN.LAYOUT
        mito = np.zeros((28, 4), "f4")
        for k, m in enumerate(L["mito"]):
            mito[2 * k] = [*m[0:3], m[3]]
            mito[2 * k + 1] = [*m[4:7], m[7]]
        ves = np.zeros((52, 4), "f4")
        for k, v in enumerate(L["ves"]):
            ves[2 * k] = v[:4]
            ves[2 * k + 1] = v[4:8]
        rng = np.random.default_rng(3)
        motes = np.column_stack([rng.uniform([-40, -24, -40], [40, 24, 40], (40, 3)), rng.uniform(0.2, 1.0, 40) ** 2])
        motes = motes[np.linalg.norm(motes[:, :3], axis=1) > 14]
        motes = np.vstack([motes, np.zeros((40 - len(motes), 4))])
        for k, v in dict(CELL_R=AN.CELL_R, SQUASH=tuple(AN.CELL_SQUASH), NUC_C=tuple(AN.NUC_C), NUC_R=AN.NUC_R,
                         GAP=AN.ENVELOPE_GAP, PORE_R=AN.PORE_R, PORE_H=AN.PORE_SPACING,
                         GOLGI_DIR=tuple(AN.GOLGI_DIR), CENTRO=tuple(AN.CENTROSOME), u_H=float(H),
                         u_aspect=W / H).items():
            setu(c, k, v)
        c["NUCLEOLI"].write(np.ascontiguousarray(AN.NUCLEOLUS, "f4").tobytes())
        c["MITO"].write(mito.tobytes())
        c["VES"].write(ves.tobytes())
        c["MT"].write(np.ascontiguousarray(L["mt"], "f4").tobytes())
        c["MOTES"].write(np.ascontiguousarray(motes, "f4").tobytes())
        for k, v in CELL_COLS.items():
            setu(c, k, tuple(lin(v)))
        setu(c, "u_gain", 1.0)
        setu(c, "u_off", int(os.environ.get("CELL_OFF", "0")))
        s = self.sph_p
        for k, v in dict(u_H=float(H), u_aspect=W / H, u_fog=2.2, u_rim=1.6, u_amb=0.05).items():
            setu(s, k, v)

    def _cam(self, prog, cam):
        prog["u_cam"].value = tuple(cam["pos"])
        prog["u_right"].value, prog["u_up"].value, prog["u_fwd"].value = (tuple(cam[k]) for k in ("right", "up", "fwd"))
        prog["u_tanHalf"].value = float(np.tan(cam["fov"] / 2))

    def _dof(self, src_tex, dst, focus, k=0.010):
        dst[1].use()
        src_tex.use(0)
        p = self.dof_p
        p["tex"].value = 0
        p["u_res"].value = (self.W, self.H)
        p["u_focus"].value = float(focus)
        p["u_k"].value = k
        p["u_max"].value = 14.0 * self.H / 480
        self.dof_v.render(moderngl.TRIANGLE_STRIP)

    def _pass(self, prog, vao, fbo, tex, **uni):
        fbo.use()
        tex.use(0)
        prog["tex"].value = 0
        for k, v in uni.items():
            prog[k].value = v
        vao.render(moderngl.TRIANGLE_STRIP)

    def frame(self, t, idx=0):
        ctx = self.ctx
        ev = TL.events(t)
        if ev["w_cell"] > 1e-3:
            cam = TL.camera_cell(t)
            self.cellT[1].use()
            self._cam(self.cell_p, cam)
            self.cell_p["u_time"].value = float(t)
            self.cell_p["u_res"].value = (self.W, self.H)
            ty = max(1, int(np.ceil(self.H / TILE)))
            tx = max(1, int(np.ceil(self.W / TILE)))
            for j in range(ty):
                for i in range(tx):
                    ctx.scissor = (i * TILE, j * TILE, TILE, TILE)
                    self.cell_v.render(moderngl.TRIANGLE_STRIP)
                    ctx.finish()
            ctx.scissor = None
            self._dof(self.cellT[0], self.dofA, cam["focus"], 0.012 if t < 4 else 0.008)
        if ev["w_mol"] > 1e-3:
            S = self.hero.state(t, ev)
            sph, ctr = self.hero.spheres(t, ev, S)
            tgt = TL.molecular_target(t, self.hero.target_source(t, S, ctr))
            cam = TL.camera_mol(t, tgt, self.hero.basis)
            fb = self.molT[1]
            fb.use()
            fb.clear(0, 0, 0, 1e6, depth=1.0)
            ctx.enable(moderngl.DEPTH_TEST)
            p = self.sph_p
            self._cam(p, cam)
            p["u_near"].value = float(cam["focus"] * 0.02)
            p["u_far"].value = float(cam["focus"] * 600)
            p["u_focus"].value = float(cam["focus"])
            p["u_groupVis"].value = (ev["fibre"], ev["fibre"], 1.0)
            self.stat_v.render(moderngl.POINTS)
            self.hero_buf.orphan(len(sph) * 9 * 4)
            self.hero_buf.write(sph.tobytes())
            self.hero_v.render(moderngl.POINTS, vertices=len(sph))
            ctx.disable(moderngl.DEPTH_TEST)
            self._dof(self.molT[0], self.dofB, cam["focus"], 0.010)
        # mix the two worlds
        self.mixT[1].use()
        self.dofA[0].use(0); self.dofB[0].use(1)
        m = self.mix_p
        m["A"].value, m["B"].value = 0, 1
        m["wA"].value, m["wB"].value = ev["w_cell"], ev["w_mol"]
        self.mix_v.render(moderngl.TRIANGLE_STRIP)
        # bloom
        srct = self.mixT[0]
        for i, (tex, fbo) in enumerate(self.levels):
            self._pass(self.down_p, self.down_v, fbo, srct, u_texel=(1 / srct.width, 1 / srct.height),
                       u_thresh=0.35 if i == 0 else 0.0)
            srct = tex
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.ONE, moderngl.ONE
        for k in range(len(self.levels) - 1, 0, -1):
            s = self.levels[k][0]
            self._pass(self.up_p, self.up_v, self.levels[k - 1][1], s, u_texel=(1 / s.width, 1 / s.height))
        ctx.disable(moderngl.BLEND)
        self.fin[1].use()
        self.mixT[0].use(0); self.levels[0][0].use(1)
        c = self.comp_p
        c["scene"].value, c["bloom"].value = 0, 1
        for k, v in dict(u_bloom=0.35, u_exposure=1.0, u_fade=ev["fade"], u_vig=0.4, u_grain=0.035,
                         u_frame=float(idx % 997), u_zoom=ev["zoom"], u_ca=ev["ca"], u_flash=ev["flash"],
                         u_res=(self.W, self.H)).items():
            setu(c, k, v)
        self.comp_v.render(moderngl.TRIANGLE_STRIP)
        ctx.finish()
        # reset the DOF targets of the inactive world so the mix never reads stale frames
        if ev["w_cell"] <= 1e-3:
            self.dofA[1].clear(0, 0, 0, 1)
        if ev["w_mol"] <= 1e-3:
            self.dofB[1].clear(0, 0, 0, 1)
        return self.fin[1].read(components=3, alignment=1)


# ── CLI ──────────────────────────────────────────────────────────────────────
def size_for(height):
    return int(round(height * 16 / 9 / 2) * 2), height


def save_png(buf, w, h, path):
    from PIL import Image
    img = Image.frombytes("RGB", (w, h), buf).transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    return img


def cmd_still(a):
    from PIL import Image
    w, h = size_for(a.height)
    r = Renderer(w, h)
    OUT.mkdir(exist_ok=True)
    ims = []
    for t in a.t:
        t0 = time.time()
        path = OUT / f"still_{t:05.2f}s.png"
        ims.append(save_png(r.frame(t), w, h, path))
        print(f"{path.name}  ({time.time() - t0:.2f}s)")
    if len(ims) > 1:
        cols = 3
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (60, 60, 60))
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        sheet.save(OUT / "contact.png")
        print(OUT / "contact.png")


SEG_FRAMES = 150


def _render_key(a):
    hsh = hashlib.sha1()
    for p in sorted([*HERE.glob("*.py"), *SH.glob("*")]):
        hsh.update(p.name.encode()); hsh.update(p.read_bytes())
    hsh.update(f"{a.height}|{a.fps}|{a.crf}|{SEG_FRAMES}".encode())
    return hsh.hexdigest()[:12]


def cmd_video(a):
    w, h = size_for(a.height)
    fps = a.fps
    n = int(round(TL.DURATION * fps))
    OUT.mkdir(exist_ok=True)
    out = Path(a.out) if a.out else OUT / f"cell_dna_{h}p{fps}.mp4"
    segdir = OUT / "segments" / f"{h}p{fps}_{_render_key(a)}"
    segdir.mkdir(parents=True, exist_ok=True)
    chunks = [(s, min(s + SEG_FRAMES, n)) for s in range(0, n, SEG_FRAMES)]
    seg = lambda k: segdir / f"seg_{k:04d}.mp4"          # noqa: E731
    done = sum(e - s for k, (s, e) in enumerate(chunks) if seg(k).exists())
    bar = tqdm(total=n, initial=done, desc=f"CellDNA@{h}p{fps}", unit="fr", dynamic_ncols=True,
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} fr "
                          "[{elapsed} elapsed, ETA {remaining}, {rate_fmt}]")
    r = None
    for k, (s, e) in enumerate(chunks):
        if seg(k).exists():
            continue
        r = r or Renderer(w, h)
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


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("still")
    s.add_argument("--t", type=float, nargs="+", default=[3, 9, 15, 20, 25, 29, 33, 37, 43])
    s.add_argument("--height", type=int, default=480)
    s = sub.add_parser("video")
    s.add_argument("--height", type=int, default=480)
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--crf", type=int, default=18)
    s.add_argument("--out")
    a = ap.parse_args()
    {"still": cmd_still, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
