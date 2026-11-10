"""aion audit: source, timing, design and delivery checks."""

from __future__ import annotations

import click


@click.command()
@click.argument("video")
@click.option("--source/--no-source", default=True, help="Scan scene code for rule violations.")
@click.option("--timing/--no-timing", default=True)
@click.option("--design", is_flag=True, help="Evaluate scenes at each beat (slower).")
@click.option("--delivery", "deliver", is_flag=True, help="Check out/final.mp4 for upload.")
@click.option("--file", type=click.Path(exists=True), default=None, help="Video file for --delivery.")
def cli(video, source, timing, design, deliver, file):
    """Print findings (✘ error, ⚠ warn, · info). Exit code 1 if any error."""
    from pathlib import Path

    from aion.audit import checks
    from aion.render.project import load_video

    vid = load_video(video, (1280, 720), 30)
    found = []
    if source:
        found += checks.source(vid)
    if timing:
        found += checks.timing(vid)
    if design:
        found += checks.design(vid)
    if deliver:
        mp4 = Path(file) if file else vid.paths.out / "final.mp4"
        found += checks.delivery(mp4, vid.duration)
    for f in found:
        click.echo(str(f))
    errors = sum(f.level == "error" for f in found)
    click.echo(f"{len(found)} findings, {errors} errors")
    raise SystemExit(1 if errors else 0)
