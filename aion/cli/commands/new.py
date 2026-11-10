"""aion new: scaffold videos/NNN-<slug>/ from the template."""

from __future__ import annotations

import re
import shutil

import click


@click.command()
@click.argument("slug")
@click.option("--title", default=None, help="Human title (default from slug).")
def cli(slug: str, title: str | None):
    """Create videos/NNN-slug with video.py, theme.py, beats.py, voiceover.md, storyboard.md, scenes/."""
    from aion._env import PKG, VIDEOS

    VIDEOS.mkdir(exist_ok=True)
    if not re.match(r"^\d{3}-", slug):
        nums = [int(d.name[:3]) for d in VIDEOS.iterdir() if re.match(r"^\d{3}-", d.name)]
        slug = f"{max(nums, default=0) + 1:03d}-{slug}"
    dest = VIDEOS / slug
    if dest.exists():
        raise click.ClickException(f"{dest} already exists")
    title = title or slug[4:].replace("-", " ").title()
    shutil.copytree(PKG / "templates" / "video", dest, ignore=shutil.ignore_patterns("__pycache__"))
    for f in dest.rglob("*"):
        if f.is_file() and f.suffix in (".py", ".md", ".toml"):
            f.write_text(f.read_text().replace("{{slug}}", slug).replace("{{title}}", title))
    click.echo(f"✔ {dest}\nnext: write voiceover.md → uv run aion voice {slug} --dry-run")
