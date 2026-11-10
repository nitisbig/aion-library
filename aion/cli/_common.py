"""Helpers shared by render/preview/still/sheet commands."""

from __future__ import annotations

import click

QUALITY_OPTS = [
    click.option("--preview", "quality", flag_value="preview", help="854x480 @15 (default for preview)."),
    click.option("--low", "quality", flag_value="low", help="854x480 @30."),
    click.option("--draft", "quality", flag_value="draft", help="1280x720 @30."),
    click.option("--final", "quality", flag_value="final", help="1920x1080 @60, x264 CRF16."),
    click.option("--4k", "quality", flag_value="4k", help="3840x2160 @60."),
    click.option("--res", type=int, default=None, help="Override height (keeps 16:9)."),
    click.option("--fps", type=float, default=None, help="Override frame rate."),
]


def quality_opts(f):
    for opt in reversed(QUALITY_OPTS):
        f = opt(f)
    return f


def resolve_quality(quality: str | None, res: int | None, fps: float | None, default: str):
    from aion.render.project import QUALITY

    q = quality or default
    size, f = QUALITY[q]
    if res:
        size = (int(round(res * 16 / 9 / 2)) * 2, res)
    return q, size, fps or f


def parse_time(vid, value: str) -> float:
    """'12.5', 'lam' (beat name) or 'lam+0.3'."""
    try:
        return float(value)
    except ValueError:
        pass
    import re

    from aion.cli.commands.beats import load_beats

    m = re.fullmatch(r"([A-Za-z_]\w*)([+-][\d.]+)?", value)
    if not m:
        raise click.BadParameter(f"{value!r} is not seconds or a beat name")
    T = load_beats(vid.paths)
    return float(getattr(T, m.group(1))) + float(m.group(2) or 0)
