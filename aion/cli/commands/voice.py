"""aion voice: narration via ElevenLabs → assets/audio.wav, audio.mp3, cue-per-word.srt."""

from __future__ import annotations

import click


@click.command()
@click.argument("video")
@click.option("--dry-run", is_flag=True, help="Only show chunks, cache hits and billable characters.")
@click.option("--yes", "-y", is_flag=True, help="Don't ask before spending credits.")
@click.option("--loudness", default=-16.0, show_default=True, help="Target LUFS for audio.wav (0 = off).")
@click.option("--script", type=click.Path(exists=True), default=None, help="Script path (default voiceover.md).")
def cli(video: str, dry_run: bool, yes: bool, loudness: float, script: str | None):
    """Generate narration + word-level timing for a video (cached per chunk)."""
    from pathlib import Path

    from aion.project import find_video
    from aion.voice.master import generate, plan

    v = find_video(video)
    vp = plan(v, Path(script) if script else None)
    for w in vp.warnings:
        click.echo(f"lint: {w}")
    hits = sum(vp.cached)
    click.echo(f"{len(vp.chunks)} chunks ({hits} cached), {vp.chars_to_bill} characters to bill; "
               f"voice {vp.settings.voice_id} model {vp.settings.model_id}")
    if dry_run:
        return
    if vp.chars_to_bill and not yes and not click.confirm("Call ElevenLabs now?"):
        return
    r = generate(v, Path(script) if script else None, loudness=loudness or None)
    click.echo(f"✔ {r['words']} words, {r['duration']:.2f}s → {v.assets}")
