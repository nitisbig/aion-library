"""Generate a video's narration: voiceover.md → audio.wav/mp3 + word cues.

    generate(find_video("004"))   # what `aion voice 004 --yes` runs

Chunks are decoded to PCM and concatenated there, never as MP3 bytes, because
MP3 encoder delay would shift every later word. Each chunk's offset is its
decoded sample count, so word times match the master audio exactly.

`chunking` in voice.toml picks the requests:
- "pack" (default): paragraphs packed into chunks of at most 2500 characters, each stitched to the chunks around it.
- "scene": one request per `<!-- scene: id -->` block, stitched to the neighbouring scenes. Every take is also
  exported (`audio/scenes/<id>.mp3`, `audio/alignment/<id>.json`), and `audio/manifest.json` pins each scene's
  exact request. While a scene's own text is unchanged, its recorded neighbours and seed are reused, so editing one
  scene bills only that scene. `--scene ID` re-requests a scene with its current neighbours, and `--retake ID` makes
  a new take (seed = base + take; old takes stay in the cache). `assets/scenes.json` is the scene timeline.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import wave
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from aion import cache
from aion.project import VideoPaths
from aion.voice.align import (check_subtitles, srt_text, subtitle_cues, vtt_text, words_from_alignment,
                              write_word_srt, write_words_json)
from aion.voice.elevenlabs import VoiceSettings, is_cached, store_take, tts_with_timestamps
from aion.voice.pacing import Pacing, silences, snap_words, stretch
from aion.voice.script import (Para, ScriptOptions, apply_aliases, chunk, global_breaks, group_scenes, lint,
                               read_paras, scene_markers, unalias)

__all__ = ["VoicePlan", "SceneJob", "plan", "generate", "decode_pcm"]

RATE = 44100
SEED_SPAN = 2 ** 32                 # ElevenLabs seeds are integers 0 … 4294967295


@dataclass
class SceneJob:
    """One scene's TTS request under `chunking = "scene"`, and whether running it bills.

    `status` is "cached", "restore" (rebuilt for free from the exported take) or "bill". `why` says how the request
    was chosen: "pinned" (recorded neighbours and seed), "new", "text changed", "settings changed", "--scene" or
    "retake".

    Example:
        [(j.id, j.chars, j.status) for j in plan(find_video("015")).scenes]
    """

    id: str
    text: str                       # TTS text: aliases applied, inline pauses removed, paragraphs joined by \n\n
    display: list[str]              # the script's words, which cues and captions use
    prev: str | None
    next: str | None
    seed: int | None
    take: int
    status: str
    why: str
    stale_context: bool = False     # pinned while a neighbour has changed since (its recorded context is reused)

    @property
    def chars(self) -> int:
        return len(self.text)

    @property
    def bills(self) -> bool:
        return self.status == "bill"


@dataclass
class VoicePlan:
    chunks: list[str]
    settings: VoiceSettings
    cached: list[bool]
    warnings: list[str]
    inserts: list = None            # [(base paragraph index it goes before, [(text, prev, next)], [cached])]
    mode: str = "pack"              # voice.toml `chunking`
    scenes: list[SceneJob] = None   # chunking = "scene": one job per scene, in script order
    paras: list[Para] = None
    options: ScriptOptions = None

    @property
    def chars_to_bill(self) -> int:
        n = sum(len(c) for c, hit in zip(self.chunks, self.cached) if not hit)
        for _, parts, hits in self.inserts or []:
            n += sum(len(t) for (t, _, _), hit in zip(parts, hits) if not hit)
        return n


def _neighbours(chunks: list[str], i: int) -> tuple[str | None, str | None]:
    return (chunks[i - 1] if i else None, chunks[i + 1] if i + 1 < len(chunks) else None)


def plan(video: VideoPaths, script: Path | None = None, scenes=(), retake=()) -> VoicePlan:
    """What `generate` will request and what it will cost, without calling the API.

    `scenes` / `retake` name scenes to re-request with their current neighbours / as a new take (scene chunking)."""
    src = script or video.dir / "voiceover.md"
    toml = video.dir / "voice.toml"
    vs, opts = VoiceSettings.load(toml), ScriptOptions.load(toml)
    paras = read_paras(src)
    warnings = lint([p.text for p in paras], opts.banned, [p.breaks for p in paras])
    if opts.chunking == "scene":                          # "¶12: …" → "¶12 (s05_ripple): …"
        warnings = [re.sub(r"^¶(\d+):", lambda m: f"¶{m.group(1)} ({paras[int(m.group(1)) - 1].scene}):", w)
                    for w in warnings]
        return _plan_scenes(video, src, paras, vs, opts, warnings, set(scenes), set(retake))
    if scenes or retake:
        raise ValueError('--scene and --retake need chunking = "scene" in voice.toml')
    tts = [apply_aliases(p.text, opts.aliases) for p in paras]
    chunks = chunk([t for t, p in zip(tts, paras) if not p.inserted])   # the original narration: same chunks, same hits
    cached = [is_cached(c, *_neighbours(chunks, i), vs) for i, c in enumerate(chunks)]
    inserts, n_base, i = [], 0, 0
    while i < len(paras):                                 # each run of inserted paragraphs is synthesised alone
        if not paras[i].inserted:
            n_base, i = n_base + 1, i + 1
            continue
        j = i
        while j < len(paras) and paras[j].inserted:
            j += 1
        texts = chunk(tts[i:j])
        before = tts[i - 1] if i else None
        after = tts[j] if j < len(paras) else None
        parts = [(t, texts[k - 1] if k else before, texts[k + 1] if k + 1 < len(texts) else after)
                 for k, t in enumerate(texts)]
        inserts.append((n_base, parts, [is_cached(*part, vs) for part in parts]))
        i = j
    return VoicePlan(chunks, vs, cached, warnings, inserts, paras=paras, options=opts)


# ── scene chunking ──────────────────────────────────────────────────────────────────────────────────────────────

def _sha(s: str | None) -> str | None:
    return None if s is None else hashlib.sha256(s.encode("utf-8")).hexdigest()


def _seed(base: int | None, take: int) -> int | None:
    """Seed of a scene's take: the voice.toml seed for take 0, then base + take."""
    if base is None and take == 0:
        return None
    return ((base or 0) + take) % SEED_SPAN


def _config(vs: VoiceSettings) -> dict:
    """What all scene requests share. Changing any of it re-requests every scene with its current neighbours."""
    return {"voice_id": vs.voice_id, "model_id": vs.model_id, "output_format": vs.output_format,
            "stitch": vs.stitch, "seed": vs.seed, "settings": dict(vs.settings)}


def _request(text: str, prev: str | None, nxt: str | None, vs: VoiceSettings, take: int) -> dict:
    """Metadata of one scene request (shas of what is sent), as its alignment JSON records it."""
    return {"model_id": vs.model_id, "voice_id": vs.voice_id, "output_format": vs.output_format,
            "settings": dict(vs.settings), "seed": vs.seed, "take": take, "stitch": vs.stitch,
            "text_sha": _sha(text), "prev_sha": _sha(prev if vs.stitch else None),
            "next_sha": _sha(nxt if vs.stitch else None), "chars": len(text)}


def _mp3_path(video: VideoPaths, sid: str) -> Path:
    return video.dir / "audio" / "scenes" / f"{sid}.mp3"


def _align_path(video: VideoPaths, sid: str) -> Path:
    return video.dir / "audio" / "alignment" / f"{sid}.json"


def _manifest_path(video: VideoPaths) -> Path:
    return video.dir / "audio" / "manifest.json"


def _read_manifest(video: VideoPaths) -> dict:
    p = _manifest_path(video)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ValueError(f"{p} is not valid JSON ({e}); fix it, or move it away to re-request every scene") from e


def _exported(video: VideoPaths, sid: str, text: str, prev: str | None, nxt: str | None, vs: VoiceSettings,
              take: int) -> bool:
    """True when audio/scenes/<id>.mp3 + audio/alignment/<id>.json hold exactly this request's take."""
    aj, mp3 = _align_path(video, sid), _mp3_path(video, sid)
    if not (aj.is_file() and mp3.is_file()):
        return False
    try:
        meta = json.loads(aj.read_text(encoding="utf-8"))
    except ValueError:
        return False
    return meta.get("request") == _request(text, prev, nxt, vs, take) and meta.get("mp3_sha256") == cache.file_hash(mp3)


def _restore(video: VideoPaths, job: SceneJob, vs: VoiceSettings) -> None:
    """Put an exported take back in the TTS cache (after a cache prune), so it isn't billed again."""
    meta = json.loads(_align_path(video, job.id).read_text(encoding="utf-8"))
    align = {k: meta[k] for k in ("characters", "character_start_times_seconds", "character_end_times_seconds")}
    store_take(job.text, job.prev, job.next, vs, _mp3_path(video, job.id).read_bytes(), align)


def _plan_scenes(video: VideoPaths, src: Path, paras: list[Para], vs: VoiceSettings, opts: ScriptOptions,
                 warnings: list[str], force: set[str], retake: set[str]) -> VoicePlan:
    groups = group_scenes(paras, src.name)
    if not groups:
        raise ValueError(f"{src.name} has no narration to voice")
    ids = [sid for sid, _ in groups]
    unknown = sorted((force | retake) - set(ids))
    if unknown:
        raise ValueError(f"no scene {', '.join(unknown)} in {src.name} (scenes: {', '.join(ids)})")
    texts = ["\n\n".join(apply_aliases(p.text, opts.aliases) for p in ps) for _, ps in groups]
    manifest = _read_manifest(video)
    recs = {r["id"]: r for r in manifest.get("scenes", [])}
    same = manifest.get("config") == _config(vs)
    jobs = []
    for i, ((sid, ps), text) in enumerate(zip(groups, texts)):
        prev, nxt = _neighbours(texts, i)
        rec = recs.get(sid)
        take = int(rec.get("take", 0)) if rec else 0
        stale = False
        if sid in retake:
            take, why = take + 1, "retake"
        elif sid in force:
            why = "--scene"
        elif rec is None:
            why = "new"
        elif rec.get("text_sha") != _sha(text):
            why = "text changed"
        elif not same:
            why = "settings changed"
        else:                                             # pinned: the exact request recorded last time
            why = "pinned"
            stale = (rec.get("prev_text"), rec.get("next_text")) != (prev, nxt)
            prev, nxt = rec.get("prev_text"), rec.get("next_text")
        seed = rec.get("seed") if why == "pinned" else _seed(vs.seed, take)
        vsi = replace(vs, seed=seed)
        status = ("cached" if is_cached(text, prev, nxt, vsi) else
                  "restore" if _exported(video, sid, text, prev, nxt, vsi, take) else "bill")
        display = [w for p in ps for w in p.words]
        jobs.append(SceneJob(sid, text, display, prev, nxt, seed, take, status, why, stale))
    warnings = warnings + [f"scene {sid!r} has no narration, so it gets no audio and no row in scenes.json"
                           for sid in scene_markers(src) if sid not in ids]
    return VoicePlan([j.text for j in jobs], vs, [not j.bills for j in jobs], warnings, [], mode="scene",
                     scenes=jobs, paras=paras, options=opts)


def _display(words: list, tokens: list[str], aliases: dict) -> list:
    """Words in the script's spelling: aliased words map back one to one (by position when the counts agree)."""
    if not aliases:
        return words
    if len(words) == len(tokens):
        return [w if w.text == t else replace(w, text=t) for w, t in zip(words, tokens)]
    return [replace(w, text=unalias(w.text, aliases)) for w in words]


def _write(path: Path, data: bytes | str) -> None:
    """Atomic write that leaves the file (and its mtime) alone when the content is already there."""
    b = data.encode("utf-8") if isinstance(data, str) else data
    if path.is_file() and path.stat().st_size == len(b) and path.read_bytes() == b:
        return
    cache.atomic_write(path, b)


def _synth_scenes(video: VideoPaths, vp: VoicePlan, progress: bool) -> tuple[np.ndarray, list, list[dict]]:
    """Request (or reuse) every scene, export each take, and join them: (audio, words, request records)."""
    from aion.progress import Progress

    _mp3_path(video, "x").parent.mkdir(parents=True, exist_ok=True)
    _align_path(video, "x").parent.mkdir(parents=True, exist_ok=True)
    words, pcm, recs, offset = [], [], [], 0
    bar = Progress(f"{video.slug}-voice", len(vp.scenes), unit="scene", disable=not progress)
    try:
        for job in vp.scenes:
            vsi = replace(vp.settings, seed=job.seed)
            if job.status == "restore":
                _restore(video, job, vsi)
            data, align = tts_with_timestamps(job.text, job.prev, job.next, vsi)
            x = decode_pcm(data)
            raw = words_from_alignment(align)
            local = _display(raw, job.display, vp.options.aliases)
            if not local:
                raise RuntimeError(f"scene {job.id}: the TTS returned no words")
            req = _request(job.text, job.prev, job.next, vsi, job.take)
            mp3_sha = hashlib.sha256(data).hexdigest()
            _write(_mp3_path(video, job.id), data)
            _write(_align_path(video, job.id), json.dumps({
                "id": job.id, "request": req, "mp3_sha256": mp3_sha, "duration": round(len(x) / RATE, 6),
                "words": [{"text": w.text, "start": round(w.start, 3), "end": round(w.end, 3),
                           **({"said": r.text} if r.text != w.text else {})} for w, r in zip(local, raw)],
                "characters": align["characters"],
                "character_start_times_seconds": align["character_start_times_seconds"],
                "character_end_times_seconds": align["character_end_times_seconds"],
            }, ensure_ascii=False) + "\n")
            recs.append({"id": job.id, "take": job.take, "seed": job.seed, "chars": job.chars,
                         "text_sha": req["text_sha"], "prev_sha": _sha(job.prev), "next_sha": _sha(job.next),
                         "prev_text": job.prev, "next_text": job.next, "mp3_sha256": mp3_sha,
                         "clip_duration": round(len(x) / RATE, 6),
                         "audio": f"audio/scenes/{job.id}.mp3", "alignment": f"audio/alignment/{job.id}.json",
                         "first": len(words), "count": len(local)})
            t0 = offset / RATE
            words += [replace(w, start=w.start + t0, end=w.end + t0) for w in local]
            pcm.append(x)
            offset += len(x)
            bar.update()
    finally:
        bar.close(video.assets)
    return np.concatenate(pcm), words, recs


def _timeline(recs: list[dict], words: list, total: float) -> list[dict]:
    """Scene rows on the final timeline. Scenes tile [0, total], and each boundary sits halfway through the
    silence between the last word of one scene and the first word of the next."""
    rows = []
    for r in recs:
        i, j = r["first"], r["first"] + r["count"] - 1
        rows.append({"id": r["id"], "start": 0.0, "end": 0.0, "speech_start": words[i].start,
                     "speech_end": words[j].end, "first_word": words[i].text, "last_word": words[j].text,
                     "first_index": i, "last_index": j})
    for k in range(1, len(rows)):
        a, b = rows[k - 1]["speech_end"], rows[k]["speech_start"]
        rows[k]["start"] = rows[k - 1]["end"] = 0.5 * (a + b) if b > a else b
    if rows:
        rows[-1]["end"] = max(total, rows[-1]["speech_end"])
    for row in rows:
        for key in ("start", "end", "speech_start", "speech_end"):
            row[key] = round(row[key], 3)
    return rows


# ── pack chunking ───────────────────────────────────────────────────────────────────────────────────────────────

def _synth_pack(video: VideoPaths, vp: VoicePlan, progress: bool) -> tuple[np.ndarray, list]:
    from aion.progress import Progress

    words, pcm, offset = [], [], 0
    bar = Progress(f"{video.slug}-voice", len(vp.chunks), unit="chunk", disable=not progress)
    try:
        for i, text in enumerate(vp.chunks):
            audio, align = tts_with_timestamps(text, *_neighbours(vp.chunks, i), vp.settings)
            x = decode_pcm(audio)
            words += words_from_alignment(align, offset / RATE)
            pcm.append(x)
            offset += len(x)
            bar.update()
    finally:
        bar.close(video.assets)

    audio = np.concatenate(pcm)
    base_words = [len(p.words) for p in vp.paras if not p.inserted]
    for n_base, parts, _ in reversed(vp.inserts or []):   # last first, so earlier word indices stay valid
        xs, xw, off = [], [], 0
        for part in parts:
            a, align = tts_with_timestamps(*part, vp.settings)
            x = decode_pcm(a)
            xw += words_from_alignment(align, off / RATE)
            xs.append(x)
            off += len(x)
        audio, words = _splice(audio, words, sum(base_words[:n_base]), np.concatenate(xs), xw)
    return audio, _display(words, [w for p in vp.paras for w in p.words], vp.options.aliases)


def _splice(audio: np.ndarray, words: list, k: int, extra: np.ndarray, extra_words: list, rate: int = RATE):
    """Insert `extra` (with its words, timed from 0) before word k, cutting inside the real pause there."""
    if k >= len(words):
        cut = len(audio)
    else:
        ends = [(a, b) for a, b in silences(audio, rate, min_len=0.08) if abs(b - words[k].start) < 0.25]
        t = 0.5 * sum(min(ends, key=lambda ab: abs(ab[1] - words[k].start))) if ends else \
            0.5 * (words[k - 1].end + words[k].start)
        cut = int(round(t * rate))
    fade = int(rate * 0.008)
    head, tail = audio[:cut].copy(), audio[cut:].copy()
    if len(head) > fade:
        head[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=audio.dtype)
    if len(tail) > fade:
        tail[:fade] *= np.linspace(0.0, 1.0, fade, dtype=audio.dtype)
    pad = np.zeros(int(rate * 0.3), audio.dtype)          # a breath on each side; the pacing pass widens it
    block = np.concatenate([pad, extra, pad])
    t0, dt = (cut + len(pad)) / rate, len(block) / rate
    mid = [replace(w, start=w.start + t0, end=w.end + t0) for w in extra_words]
    late = [replace(w, start=w.start + dt, end=w.end + dt) for w in words[k:]]
    return np.concatenate([head, block, tail]), words[:k] + mid + late


# ── audio helpers ───────────────────────────────────────────────────────────────────────────────────────────────

def decode_pcm(data: bytes, rate: int = RATE) -> np.ndarray:
    """Any encoded audio bytes → mono float32 at `rate`."""
    import av

    out = []
    with av.open(io.BytesIO(data)) as f:
        res = av.AudioResampler(format="flt", layout="mono", rate=rate)
        for frame in f.decode(f.streams.audio[0]):
            out.extend(r.to_ndarray().reshape(-1) for r in res.resample(frame))
        out.extend(r.to_ndarray().reshape(-1) for r in res.resample(None))
    return np.concatenate(out) if out else np.zeros(0, np.float32)


def _write_wav(x: np.ndarray, path: Path, rate: int = RATE) -> None:
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        for i in range(0, len(x), 1 << 20):        # in blocks: no full-length temporaries on long narrations
            f.writeframes((np.clip(x[i:i + (1 << 20)], -1, 1) * 32767).astype("<i2").tobytes())


def _loudnorm(src: Path, dst: Path, target: float = -16.0) -> None:
    """Two-pass linear EBU R128 normalisation (no timing change)."""
    import json as _json

    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af",
                            f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = _json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=11:linear=true:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", af, "-ar", str(RATE),
                    "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)


def _pace(audio: np.ndarray, words: list, sections: list[tuple[str, bool]], pacing: Pacing,
          pauses: list[float] | None = None, breaks: list[tuple[int, float]] | None = None):
    """Apply voice.toml [pacing]: snap cues to speech onsets, then widen paragraph / section pauses
    (plus any `> [pause N]` asked for in the script, and inline `[pause N]` breaks before their word)."""
    sil = silences(audio, RATE)
    info: dict = {}
    if pacing.snap:
        words, info["cues_snapped"] = snap_words(words, sil)
    gaps: dict[int, float] = {}
    k = 0
    pauses = pauses if pauses and len(pauses) == len(sections) else [0.0] * len(sections)
    for (text, section), extra in zip(sections, pauses):   # k = index of the paragraph's first word
        if k:
            gaps[k] = gaps.get(k, 0.0) + (pacing.section_gap if section else pacing.paragraph_gap) + extra
        k += len(text.split())
    for idx, sec in breaks or ():
        gaps[idx] = gaps.get(idx, 0.0) + sec
    if k != len(words):                                # alignment and script disagree: don't guess
        info["pacing_skipped"] = f"script has {k} words, alignment {len(words)}"
        gaps = {}
    n0, before = len(audio), words
    audio, words, info["seconds_added"] = stretch(audio, words, RATE, sorted(gaps.items()), pacing.lead_in,
                                                   silences(audio, RATE, min_len=0.08), pacing.tail)
    info["breaks"] = len(gaps)
    skipped = [i for i, s in gaps.items() if s > 0 and 0 < i < len(words) and
               (words[i].start - before[i].start) - (words[i - 1].start - before[i - 1].start) < s - 1e-3]
    if skipped:                                        # no real silence at that word: see `lint`
        info["breaks_skipped"] = len(skipped)
    info["duration_added"] = (len(audio) - n0) / RATE
    return audio, words, info


def generate(video: VideoPaths, script: Path | None = None, loudness: float | None = -16.0,
             progress: bool = True, scenes=(), retake=()) -> dict:
    """Run TTS for every chunk or scene (cached), then write assets/{audio.wav, audio.mp3, cue-per-word.srt,
    words.json, subtitles.srt, subtitles.vtt}. Scene chunking also writes audio/scenes/<id>.mp3,
    audio/alignment/<id>.json, audio/manifest.json and assets/scenes.json. Returns a summary dict."""
    vp = plan(video, script, scenes, retake)
    recs = None
    if vp.mode == "scene":
        audio, words, recs = _synth_scenes(video, vp, progress)
    else:
        audio, words = _synth_pack(video, vp, progress)
    offset = len(audio)
    pacing = Pacing.load(video.dir / "voice.toml")
    pauses, breaks = [p.pause for p in vp.paras], global_breaks(vp.paras)
    paced = {}
    if (pacing.active or any(pauses) or breaks) and words:
        audio, words, paced = _pace(audio, words, [(p.text, p.section) for p in vp.paras], pacing, pauses, breaks)
        offset = len(audio)

    assets = video.assets
    assets.mkdir(exist_ok=True)
    raw = assets / ".audio.raw.wav"
    _write_wav(audio, raw)
    wav = assets / "audio.wav"
    if loudness is not None:
        _loudnorm(raw, wav, loudness)
        raw.unlink()
    else:
        raw.replace(wav)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame",
                    "-b:a", "192k", str(assets / "audio.mp3")], check=True)
    write_word_srt(words, assets / "cue-per-word.srt")
    write_words_json(words, assets / "words.json")
    cues = subtitle_cues(words)                    # what write_subtitles / write_vtt write, searched once
    (assets / "subtitles.srt").write_text(srt_text(cues), encoding="utf-8")
    (assets / "subtitles.vtt").write_text(vtt_text(cues), encoding="utf-8")
    out = {"chunks": len(vp.chunks), "words": len(words), "duration": offset / RATE,
           "billed_chars": vp.chars_to_bill, "warnings": vp.warnings, **paced,
           "subtitle_violations": check_subtitles(assets / "subtitles.srt")}
    if recs is not None:
        rows = _timeline(recs, words, offset / RATE)
        _write(assets / "scenes.json", json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
        src = script or video.dir / "voiceover.md"
        manifest = {"version": 1, "script": src.name, "config": _config(vp.settings),
                    "duration": round(offset / RATE, 3),
                    "scenes": [{**row, **{k: v for k, v in r.items() if k not in ("id", "first", "count")}}
                               for row, r in zip(rows, recs)]}
        _write(_manifest_path(video), json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
        out["scenes"] = len(rows)
    return out
