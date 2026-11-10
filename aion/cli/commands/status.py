"""aion status: progress of running / finished renders, bakes and voice jobs."""

from __future__ import annotations

import time

import click


@click.command()
@click.argument("name", required=False)
@click.option("-n", "limit", default=5, help="How many recent jobs to show.")
def cli(name: str | None, limit: int):
    """Show progress JSONs from media/progress (newest first)."""
    from aion.progress import read_status

    rows = read_status(name)[:limit]
    if not rows:
        click.echo("no progress files")
    for s in rows:
        age = time.time() - s.get("updated", 0)
        state = "done" if s.get("done") else ("stale?" if age > 120 else "running")
        pct = f"{s['percent']:.1f}%" if s.get("percent") is not None else "?"
        eta = f"ETA {s['eta_s']:.0f}s" if s.get("eta_s") is not None and not s.get("done") else ""
        click.echo(f"{s['name']}: {state} {pct} {s['frames']}/{s.get('total_frames')} {s.get('unit', 'fr')} "
                   f"elapsed {s['elapsed_s']:.0f}s {eta}".rstrip())
