"""aion preview: fast 480p15 render with audio (VAAPI encode when available)."""

from __future__ import annotations

import click

from aion.cli._common import quality_opts


@click.command()
@click.argument("video")
@click.argument("scenes", nargs=-1)
@quality_opts
@click.option("--range", "time_range", nargs=2, type=float, default=None, help="Absolute seconds A B.")
@click.option("--workers", "-j", type=int, default=1)
def cli(video, scenes, quality, res, fps, time_range, workers):
    """Preview render (default 854x480 @15) → out/preview*.mp4."""
    from aion.cli.commands.render import run

    run(video, scenes, quality, res, fps, time_range, workers, 2.0, "preview")
