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


QUALITY_ALIASES = {"480p": "low", "720p": "draft", "1080p": "final", "hd": "final", "2160p": "4k", "uhd": "4k"}
EXTRA_OPTS = [
    click.option("--quality", "quality_name", default=None, metavar="[preview|low|draft|final|4k]",
                 help="Quality by name (same as the flags; also 480p/720p/1080p/2160p). Combine with --fps 30."),
    click.option("--design", type=int, default=None, metavar="N",
                 help="Design system N from the video's theme.py (sets AION_DESIGN; outputs get a _dN suffix)."),
]


def design_suffix() -> str:
    """'_d2' when a design system was chosen with --design / AION_DESIGN, else ''."""
    import os

    d = os.environ.get("AION_DESIGN", "")
    return f"_d{d}" if d else ""


def quality_opts(f):
    """Shared options: --preview/--low/--draft/--final/--4k, --quality NAME, --res, --fps, --design N."""
    import functools
    import os

    @functools.wraps(f)
    def inner(*args, quality_name=None, design=None, **kw):
        if quality_name:
            q = QUALITY_ALIASES.get(quality_name.lower(), quality_name.lower())
            from aion.render.project import QUALITY

            if q not in QUALITY:
                raise click.BadParameter(f"{quality_name!r}: choose from {', '.join(QUALITY)}", param_hint="--quality")
            kw["quality"] = q
        if design is not None:
            os.environ["AION_DESIGN"] = str(design)      # read by the video's theme.py; inherited by workers
        return f(*args, **kw)

    for opt in reversed(QUALITY_OPTS + EXTRA_OPTS):
        inner = opt(inner)
    return inner


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
