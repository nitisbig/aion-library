"""aion still: render single frames (at beats or seconds) to PNG for layout checks."""

from __future__ import annotations

import click

from aion.cli._common import parse_time, quality_opts, resolve_quality


@click.command()
@click.argument("video")
@click.argument("scene")
@click.option("--at", "ats", multiple=True, required=True, help="Seconds or beat name (repeatable, 'lam+0.3').")
@quality_opts
@click.option("--layers", is_flag=True, help="Also dump each layer alone (RGBA).")
def cli(video, scene, ats, quality, res, fps, layers):
    """Write out/stills/<scene>@<t>.png for each --at."""
    from PIL import Image

    from aion.render.project import load_video

    q, size, f = resolve_quality(quality, res, fps, "draft")
    vid = load_video(video, size, f)
    sd = vid.scene(scene)
    times = sorted(parse_time(vid, a) for a in ats)
    outdir = vid.paths.out / "stills"
    outdir.mkdir(exist_ok=True)
    comp = sd.comp(size, f)
    for t in times:
        if not sd.start <= t < sd.end:
            click.echo(f"⚠ {t:.2f}s is outside {sd.name} [{sd.start:.2f}, {sd.end:.2f})")
        img = comp.frame(t, round(t * f))
        p = outdir / f"{sd.name}@{t:07.2f}.png"
        Image.fromarray(img).save(p)
        click.echo(str(p))
    if layers:
        for i, layer in enumerate(sorted(comp.layers, key=lambda l: (l.z, l.order))):
            solo = sd.comp(size, f)
            solo.background = None
            keep = sorted(solo.layers, key=lambda l: (l.z, l.order))[i]
            solo.layers = [keep]
            for t in times:
                img = solo.frame(t, round(t * f), alpha=True)
                p = outdir / f"{sd.name}@{t:07.2f}_L{i}_{keep.name}.png"
                Image.fromarray(img, "RGBA").save(p)
                click.echo(str(p))
