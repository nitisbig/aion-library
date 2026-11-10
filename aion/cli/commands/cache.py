"""aion cache: inspect or prune the content-hash cache."""

from __future__ import annotations

import click


@click.command()
@click.argument("action", type=click.Choice(["ls", "prune"]), default="ls")
@click.option("--older", type=float, default=None, help="prune: only entries unused for N days.")
@click.option("--ns", default=None, help="Limit to one namespace (e.g. tts, layers, chunks).")
def cli(action: str, older: float | None, ns: str | None):
    """List cache namespaces with sizes, or prune them."""
    from aion import cache

    if action == "ls":
        for name, (files, size) in cache.usage().items():
            click.echo(f"{name:<12} {files:>6} files {size / 1e6:>9.1f} MB")
        return
    if older is None and not click.confirm(f"Delete the whole cache{' namespace ' + ns if ns else ''}?"):
        return
    click.echo(f"freed {cache.prune(older, ns) / 1e6:.1f} MB")
