"""aion render: chunked, resumable render + audio mux (final by default)."""

from __future__ import annotations

import subprocess
import sys

import click

from aion.cli._common import design_suffix, quality_opts, resolve_quality


def run(video, scenes, quality, res, fps, time_range, workers, chunk, default_quality, keep_going=True):
    from aion.render.mux import concat, mux_audio, probe_durations
    from aion.render.project import load_video
    from aion.render.runner import render

    q, size, f = resolve_quality(quality, res, fps, default_quality)
    vid = load_video(video, size, f)
    size = vid.size
    if not vid.scenes:
        raise click.ClickException(f"no @scene functions in {vid.paths.scenes}")
    if not scenes and not time_range:
        vid.check()
    codec = "preview" if q == "preview" else "final"
    chunks = render(vid, size, f, codec, list(scenes) or None, time_range, workers, chunk)
    if not chunks:
        raise click.ClickException("nothing to render (check scene names / range)")
    suffix = design_suffix()
    if scenes:
        suffix += "_" + "-".join(scenes)
    if time_range:
        suffix += f"_{time_range[0]:g}-{time_range[1]:g}"
    out = vid.paths.out / f"{q}{suffix}.mp4"
    silent = concat([c.path for c in chunks], out.with_name(f".{out.stem}.video.mp4"))
    start = chunks[0].f0 / f
    nframes = sum(c.frames for c in chunks)
    mux_audio(silent, vid.paths.audio, out, start=start, duration=nframes / f)
    silent.unlink(missing_ok=True)
    d = probe_durations(out)
    drift = abs((d["audio"] or d["video"]) - d["video"])
    click.echo(f"✔ {out}  video {d['video']:.3f}s ({nframes} fr) audio {d['audio'] or 0:.3f}s"
               + (f"  ⚠ A/V differ by {drift:.3f}s" if drift > 1 / f + 0.03 else ""))
    return out


@click.command()
@click.argument("video")
@click.argument("scenes", nargs=-1)
@quality_opts
@click.option("--range", "time_range", nargs=2, type=float, default=None, help="Absolute seconds A B.")
@click.option("--workers", "-j", type=int, default=None, help="Parallel workers (default: by free RAM).")
@click.option("--chunk", type=float, default=2.0, show_default=True, help="Chunk length in seconds.")
@click.option("--bg", is_flag=True, help="Run detached; follow with `aion status`.")
def cli(video, scenes, quality, res, fps, time_range, workers, chunk, bg):
    """Render a video (or some scenes / a time range) and mux the narration."""
    if bg:
        from aion.project import find_video

        log = find_video(video).out / "render.log"
        args = [a for a in sys.argv[1:] if a != "--bg"]
        p = subprocess.Popen([sys.executable, "-m", "aion.cli", *args], stdout=open(log, "w"),
                             stderr=subprocess.STDOUT, start_new_session=True)
        click.echo(f"started pid {p.pid}; log {log}; progress: uv run aion status")
        return
    if workers is None:
        from aion.cli.commands.doctor import suggested_workers

        workers = suggested_workers()
    run(video, scenes, quality, res, fps, time_range, workers, chunk, "final")
