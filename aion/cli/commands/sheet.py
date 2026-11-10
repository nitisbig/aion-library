"""aion sheet: contact sheet of a scene at its beats (or every N seconds)."""

from __future__ import annotations

import click

from aion.cli._common import quality_opts, resolve_quality


@click.command()
@click.argument("video")
@click.argument("scene")
@click.option("--every", type=float, default=None, help="Seconds between frames (default: at each beat).")
@click.option("--cols", default=4)
@quality_opts
def cli(video, scene, every, cols, quality, res, fps):
    """One PNG grid: frames at each beat inside the scene, labelled with beat names."""
    from PIL import Image, ImageDraw

    from aion.cli.commands.beats import load_beats
    from aion.render.project import load_video

    q, size, f = resolve_quality(quality, res, fps, "preview")
    vid = load_video(video, size, f)
    size = vid.size
    sd = vid.scene(scene)
    if every:
        n = int((sd.end - sd.start) / every)
        marks = [(sd.start + i * every, f"{sd.start + i * every:.1f}s") for i in range(n + 1)]
    else:
        T = load_beats(vid.paths)
        marks = [(float(b) + 0.4, b.name) for b in T if sd.start <= b < sd.end]
        marks = [(sd.start + 0.05, "start")] + marks + [(sd.end - 1 / f, "end")]
    marks = [(min(max(t, sd.start), sd.end - 1 / f), lab) for t, lab in marks]
    comp = sd.comp(size, f)
    tiles = []
    for t, lab in sorted(marks):
        im = Image.fromarray(comp.frame(t, round(t * f)))
        ImageDraw.Draw(im).text((8, 6), f"{lab} {t:.2f}s", fill=(255, 220, 90))
        tiles.append(im)
    w, h = size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (w * min(cols, len(tiles)), h * rows), (0, 0, 0))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    p = vid.paths.out / "stills" / f"{sd.name}_sheet.png"
    p.parent.mkdir(exist_ok=True)
    sheet.save(p)
    click.echo(str(p))
