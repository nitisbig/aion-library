"""aion voice: narration via ElevenLabs → assets/audio.wav, audio.mp3, cue-per-word.srt."""

from __future__ import annotations

import click

_NOTES = {"text changed": "text changed", "settings changed": "voice.toml settings changed",
          "--scene": "--scene: current neighbours"}


def scene_table(vp) -> list[str]:
    """Dry-run lines for scene chunking: one row per scene with its characters and whether it bills."""
    jobs = vp.scenes
    n_bill = sum(j.bills for j in jobs)
    width = max([len(j.id) for j in jobs] + [5])
    out = [f"scene chunking: {len(jobs)} scenes, {sum(j.chars for j in jobs):,} characters; "
           f"{n_bill} to bill ({vp.chars_to_bill:,} characters)",
           f"  {'scene':<{width}}  chars  status"]
    for j in jobs:
        if j.why == "retake":
            note = f"retake {j.take} (seed {j.seed})"
        elif j.status == "restore":
            note = "from audio/scenes, free"
        elif j.why == "pinned":
            note = "a neighbour changed; its recorded request is kept" if j.stale_context else ""
        else:
            note = _NOTES.get(j.why, j.why if j.bills else "")
        out.append(f"  {j.id:<{width}}  {j.chars:>5}  {'BILL' if j.bills else j.status:<8} {note}".rstrip())
    return out


@click.command()
@click.argument("video")
@click.option("--dry-run", is_flag=True, help="Only show chunks or scenes, cache hits and billable characters.")
@click.option("--yes", "-y", is_flag=True, help="Don't ask before spending credits.")
@click.option("--loudness", default=-16.0, show_default=True, help="Target LUFS for audio.wav (0 = off).")
@click.option("--script", type=click.Path(exists=True), default=None, help="Script path (default voiceover.md).")
@click.option("--scene", "scenes", multiple=True, metavar="ID",
              help='Re-request this scene with its current neighbours (chunking = "scene"; repeatable).')
@click.option("--retake", multiple=True, metavar="ID",
              help="New take of this scene: seed = base + take, old takes stay in the cache (repeatable).")
def cli(video: str, dry_run: bool, yes: bool, loudness: float, script: str | None, scenes: tuple[str, ...],
        retake: tuple[str, ...]):
    """Generate narration + word-level timing for a video (cached per chunk or per scene)."""
    from pathlib import Path

    from aion.project import find_video
    from aion.voice.master import generate, plan

    v = find_video(video)
    src = Path(script) if script else None
    try:
        vp = plan(v, src, scenes, retake)
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    for w in vp.warnings:
        click.echo(f"lint: {w}")
    if vp.mode == "scene":
        for line in scene_table(vp):
            click.echo(line)
        click.echo(f"voice {vp.settings.voice_id} model {vp.settings.model_id}")
    else:
        hits = sum(vp.cached)
        click.echo(f"{len(vp.chunks)} chunks ({hits} cached), {vp.chars_to_bill} characters to bill; "
                   f"voice {vp.settings.voice_id} model {vp.settings.model_id}")
    if dry_run:
        return
    if vp.chars_to_bill and not yes and not click.confirm("Call ElevenLabs now?"):
        return
    r = generate(v, src, loudness=loudness or None, scenes=scenes, retake=retake)
    click.echo(f"✔ {r['words']} words, {r['duration']:.2f}s → {v.assets}")
    if r.get("breaks_skipped"):
        click.echo(f"⚠ {r['breaks_skipped']} pause(s) found no real silence and were skipped (see lint)")
    if r.get("pacing_skipped"):
        click.echo(f"⚠ pacing skipped: {r['pacing_skipped']}")
    for msg in r.get("subtitle_violations", []):
        click.echo(f"⚠ subtitles: {msg}")
