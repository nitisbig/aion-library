"""aion plan: narration structure for writing the storyboard (segments, silences, cuts)."""

from __future__ import annotations

import click


@click.command()
@click.argument("video")
@click.option("--pause", default=0.35, help="Gap (s) that splits phrases.")
@click.option("--min-cut", default=0.3, help="Minimum silence (s) for a suggested scene cut.")
def cli(video: str, pause: float, min_cut: float):
    """Print phrases with times, real silences, and suggested scene cuts."""
    from aion.project import find_video
    from aion.sync.cue import Cue
    from aion.sync.cuts import suggest_cuts
    from aion.sync.silence import audio_duration, silences

    v = find_video(video)
    if v.srt is None:
        raise click.ClickException(f"no cue-per-word.srt in {v.assets} (run `aion voice {v.slug}`)")
    cue = Cue.load(v.srt)
    sil = silences(v.audio) if v.audio else []
    dur = audio_duration(v.audio) if v.audio else cue.duration
    click.echo(f"# {v.slug}: {len(cue)} words, {dur:.2f}s audio, {len(sil)} silences")
    for seg in cue.segments(pause):
        click.echo(f"{seg.start:7.2f}–{seg.end:7.2f}  {seg.text}")
    cuts = suggest_cuts(cue, sil, min_cut)
    click.echo(f"\n# {len(cuts)} suggested cuts (use cut(\"<before>\", \"<after>\") in beats.py)")
    for c in cuts:
        click.echo(f"{c['t']:7.2f}  cut({c['after']!r}, {c['before']!r})  silence {c['silence']:.2f}s")
