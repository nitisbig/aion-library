"""aion doctor: check the toolchain this machine needs to render."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

import click


def _run(cmd: list[str], timeout: float = 60) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def _mem_available_gb() -> float | None:
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024 / 1024
    except OSError:
        return None
    return None


def suggested_workers() -> int:
    """Render workers this machine can afford (RAM-bound before CPU-bound)."""
    gb = _mem_available_gb() or 0
    cpus = os.cpu_count() or 1
    return max(1, min(cpus, int(gb // 0.75)))


def checks(full: bool):
    from aion import _env

    yield "python", True, sys.version.split()[0]

    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool)
        ver = _run([tool, "-version"])[1].split("\n")[0][:60] if path else "not on PATH"
        yield tool, bool(path), ver

    code, out = _run(["ffmpeg", "-hide_banner", "-encoders"])
    vaapi = "h264_vaapi" in out and os.path.exists("/dev/dri/renderD128")
    yield "vaapi encode", vaapi, "h264_vaapi on renderD128" if vaapi else "unavailable (previews use libx264)"

    _env.ensure_latex_on_path()
    latex, dvisvgm = shutil.which("latex"), shutil.which("dvisvgm")
    yield "latex", bool(latex and dvisvgm), "latex + dvisvgm" if latex and dvisvgm else "missing (uv run tlmgr ...)"

    try:
        from aion.gpu.context import info

        i = info()
        yield "opengl", True, f"{i['backend']}: {i['renderer']} / {str(i['version'])[:24]}"
        yield "rgba16f", i["float16"], "renderable" if i["float16"] else "not renderable (8-bit + dither fallback)"
    except Exception as e:
        yield "opengl", False, str(e)[:120]

    for mod in ("manim", "skia", "pyvista", "av", "sympy"):
        try:
            m = __import__(mod)
            yield mod, True, getattr(m, "__version__", "ok")
        except Exception as e:
            yield mod, False, str(e)[:80]

    if full:
        code, out = _run([sys.executable, "-c",
                          "import taichi as ti; ti.init(arch=ti.vulkan, log_level=ti.ERROR);"
                          "print('ARCH', ti.lang.impl.current_cfg().arch)"], timeout=120)
        arch = next((l.split(" ", 1)[1] for l in out.splitlines() if l.startswith("ARCH")), None)
        yield "taichi", code == 0, arch or out.strip().splitlines()[-1][:80] if out.strip() else "failed"

    fonts = _run(["fc-list", ":family"])[1]
    for fam in ("Inter", "Space Grotesk"):
        has = fam in fonts or (fam == "Space Grotesk" and (_env.ASSETS / "fonts").exists())
        yield f"font {fam}", has, "found" if has else "missing"

    gb = _mem_available_gb()
    yield "memory", (gb or 0) > 0.5, f"{gb:.1f} GB available → --workers {suggested_workers()}"

    key = _env.secret("ELEVENLABS_API_KEY")
    yield "elevenlabs key", bool(key), "set (.env / env)" if key else "missing: add ELEVENLABS_API_KEY to .env"

    from aion import cache

    total = sum(b for _, b in cache.usage().values())
    yield "cache", True, f"{total / 1e6:.0f} MB in {_env.CACHE}"


@click.command()
@click.option("--full", is_flag=True, help="Also probe taichi (slow, ~10 s).")
def cli(full: bool):
    """Check ffmpeg, VAAPI, LaTeX, OpenGL, fonts, RAM and API keys."""
    bad = 0
    for name, ok, detail in checks(full):
        bad += not ok
        click.echo(f"{'✔' if ok else '✘'} {name:<15} {detail}")
    if bad:
        click.echo(f"{bad} problem(s).")
