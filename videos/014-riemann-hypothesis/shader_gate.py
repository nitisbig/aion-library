"""Shader validation gate for 014 (design.md §10): shaders/zeta_domain.frag (float32, GPU) vs zmath (float64).

Samples 1,000 seeded points of the overview plane (σ ∈ [-7, 4], t ∈ [-2, 40]) and compares hue and value with the
reference. Pass: hue error < 2° everywhere outside 0.02-radius disks around the zeros and the pole. Also times a 1080p
frame and writes out/design/shader_zeta.png to look at.

    uv run python videos/014-riemann-hypothesis/shader_gate.py
"""
import sys
import time
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image

import aion
from aion import gl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from zmath import zeta, zeros_upto  # noqa: E402

SH = Path(aion.__file__).resolve().parent / "shaders"


def program(ctx):
    frag = (HERE / "shaders/zeta_domain.frag").read_text()
    frag = frag.replace('#include "common/color.glsl"', (SH / "common/color.glsl").read_text())
    return ctx.program(vertex_shader=(SH / "common/fullscreen.vert").read_text(), fragment_shader=frag)


def render(ctx, prog, size, frame, origin, unit=1.0, func=3.0, debug=1.0, dim=0.0, reveal=-1000.0):
    W, H = size
    vals = dict(u_frame=frame, u_origin=origin, u_unit=unit, u_func=func, u_reveal=reveal, u_dim=dim, u_sat=0.85,
                u_opacity=1.0, u_debug=debug, u_view_inv=tuple(np.eye(3, dtype="f4").T.flatten()))
    for k, v in vals.items():
        if k in prog:
            prog[k].value = v
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((W, H), 4, dtype="f4")])
    fbo.use()
    vao = ctx.vertex_array(prog, [])
    t0 = time.perf_counter()
    vao.render(moderngl.TRIANGLES, vertices=3)
    img = np.frombuffer(fbo.read(components=4, dtype="f4"), dtype="f4").reshape(H, W, 4)
    ms = (time.perf_counter() - t0) * 1000
    fbo.release(), vao.release()
    return img, ms


def reference(w):
    r = np.abs(w)
    hue = (np.angle(w) / (2 * np.pi)) % 1.0
    band = np.mod(np.log2(np.maximum(r, 1e-12)), 1.0)
    val = np.clip((0.78 + 0.22 * band) * (1 - np.exp(-3 * r)) ** 0.6, 0, 1)
    return hue, band, val


def gate():
    ctx = gl()
    prog = program(ctx)
    W, H, frame, origin = 1100, 840, (11.0, 42.0), (1.5, -19.0)          # s = v_pos - origin covers the overview
    img, _ = render(ctx, prog, (W, H), frame, origin)
    rng = np.random.default_rng(14)
    i, j = rng.integers(0, W, 4000), rng.integers(0, H, 4000)
    s = ((i + 0.5) / W - 0.5) * frame[0] - origin[0] + 1j * (((j + 0.5) / H - 0.5) * frame[1] - origin[1])
    special = np.concatenate([0.5 + 1j * zeros_upto(40.0), [-2, -4, -6, 1]])
    keep = np.min(np.abs(s[:, None] - special[None, :]), axis=1) > 0.02
    i, j, s = i[keep][:1000], j[keep][:1000], s[keep][:1000]
    hue, band, val = reference(zeta(s))
    g = img[j, i]
    dh = np.abs(g[:, 0] - hue) % 1.0
    dh = np.minimum(dh, 1 - dh) * 360
    dv = np.abs(g[:, 2] - val)
    worst = np.argmax(dh)
    print(f"zeta  : {len(s)} points, hue error max {dh.max():.4f}°  p99 {np.percentile(dh, 99):.4f}°, "
          f"value error max {dv.max():.4f}  (worst hue at s = {s[worst]:.3f})")
    ok = dh.max() < 2.0

    # the s10 lesson functions on a small plane
    for func, f in ((0.0, lambda z: z), (1.0, lambda z: z - 1), (2.0, lambda z: 1 / z)):
        im, _ = render(ctx, prog, (400, 300), (8.0, 6.0), (0.0, 0.0), func=func)
        ii, jj = rng.integers(0, 400, 600), rng.integers(0, 300, 600)
        z = ((ii + 0.5) / 400 - 0.5) * 8 + 1j * (((jj + 0.5) / 300 - 0.5) * 6)
        m = (np.abs(z) > 0.02) & (np.abs(z - 1) > 0.02)
        h, _, _ = reference(f(z[m]))
        d = np.abs(im[jj[m], ii[m], 0] - h) % 1.0
        d = np.minimum(d, 1 - d) * 360
        print(f"func {int(func)}: hue error max {d.max():.4f}°")
        ok &= d.max() < 2.0

    # speed at 1080p, and two views to look at: the trivial zeros and the pole (s12), and a stretch of the line (s13)
    pics = []
    for unit, (sc, tc) in ((14.222 / 11.0, (-2.0, 0.0)), (0.5, (0.5, 22.0))):
        for _ in range(2):
            pic, ms = render(ctx, prog, (1920, 1080), (14.222, 8.0), (-unit * sc, -unit * tc), unit=unit, debug=0.0)
        lin = np.clip(pic[::-1, :, :3], 0, 1)
        pics.append(np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055))
    print(f"1080p frame: {ms:.0f} ms")
    out = HERE / "out/design/shader_zeta.png"
    Image.fromarray((np.concatenate(pics, axis=0)[::2, ::2] * 255 + 0.5).astype(np.uint8)).save(out)
    print("PASS" if ok else "FAIL", f"(wrote {out.relative_to(HERE.parent.parent)})")
    return ok


if __name__ == "__main__":
    sys.exit(0 if gate() else 1)
