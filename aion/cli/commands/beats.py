"""aion beats: resolve videos/<slug>/beats.py and print the timed beat table."""

from __future__ import annotations

import importlib.util

import click


def load_beats(video):
    path = video.dir / "beats.py"
    if not path.exists():
        raise click.ClickException(f"{path} not found (aion new scaffolds it)")
    spec = importlib.util.spec_from_file_location(f"aion_video_{video.slug.replace('-', '_')}_beats", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.T


@click.command()
@click.argument("video")
@click.option("--md", is_flag=True, help="Markdown table (paste into storyboard.md).")
def cli(video: str, md: bool):
    """Resolve beats in order, check scene cuts, print the table."""
    from aion.project import find_video

    v = find_video(video)
    T = load_beats(v)
    if md:
        click.echo(T.markdown())
    else:
        for name, t, e, text in T.table():
            click.echo(f"{t:8.2f} {e:8.2f}  {name:<16} {text}")
    soft = [b.name for b in T if b.soft]
    click.echo(f"{len(T.items)} beats, {len(T.cuts) - 1} scenes, audio {T.duration:.2f}s"
               + (f"; WARNING no real silence at cuts: {soft}" if soft else ""))
