"""Pacing pass: cues snap to real speech onsets and pauses stretch without splitting speech."""

import numpy as np

from aion.sync.cue import Word
from aion.voice.pacing import Pacing, silences, snap_words, stretch
from aion.voice.script import read_sections

RATE = 8000


def tone(a, b, total):
    t = np.arange(int(total * RATE)) / RATE
    return np.where((t >= a) & (t < b), 0.4 * np.sin(2 * np.pi * 220 * t), 0.0).astype(np.float32)


def audio():
    x = tone(0.0, 1.0, 4.0) + tone(1.6, 2.4, 4.0) + tone(3.0, 3.8, 4.0)
    return x + 1e-4 * np.random.default_rng(0).standard_normal(len(x)).astype(np.float32)


def test_silences_found():
    sil = silences(audio(), RATE)
    assert len(sil) == 3 and abs(sil[0][0] - 1.0) < 0.02 and abs(sil[0][1] - 1.6) < 0.02


def test_snap_moves_late_cue_onto_onset():
    words = [Word("one", 0.0, 0.5), Word("two.", 1.1, 1.5), Word("three", 1.9, 2.4), Word("four", 3.02, 3.8)]
    out, moved = snap_words(words, silences(audio(), RATE))
    assert moved == 1 and abs(out[2].start - 1.6) < 0.02          # 0.3 s late → on the onset
    assert out[1].end <= 1.0 + 0.02 and out[1].start < out[1].end  # last word pulled out of the silence
    assert abs(out[3].start - 3.0) < 0.03
    assert all(b.start >= a.start for a, b in zip(out, out[1:]))


def test_stretch_adds_silence_inside_the_pause():
    x = audio()
    words = [Word("one", 0.0, 1.0), Word("two", 1.6, 2.4), Word("three", 3.0, 3.8)]
    y, out, added = stretch(x, words, RATE, [(1, 0.5), (2, 1.5)], lead_in=2.0)
    assert abs(added - 4.0) < 1e-6 and abs(len(y) - len(x) - 4.0 * RATE) <= 2
    assert [round(w.start, 2) for w in out] == [2.0, 4.1, 7.0]
    for w in out:                                                  # speech is still where the cues say
        seg = y[int((w.start + 0.05) * RATE):int((w.start + 0.3) * RATE)]
        assert np.sqrt((seg ** 2).mean()) > 0.2
    assert np.abs(y[: int(1.9 * RATE)]).max() == 0.0


def test_pacing_config_and_sections(tmp_path):
    (tmp_path / "voice.toml").write_text('voice_id = "x"\n[pacing]\nsnap = true\nsection_gap = 1.5\n')
    p = Pacing.load(tmp_path / "voice.toml")
    assert p.snap and p.section_gap == 1.5 and p.active and not Pacing().active
    (tmp_path / "v.md").write_text("# Title\n\nFirst para.\n\nSecond para.\n\n# CHAPTER 2\n\nThird para.\n")
    assert read_sections(tmp_path / "v.md") == [("First para.", True), ("Second para.", False), ("Third para.", True)]


def test_inserted_paragraphs_are_planned_alone_and_spliced_in_place(tmp_path):
    """Text between `> [insert]` notes never changes the original chunks, and lands before the right word."""
    from aion.voice.master import _splice
    from aion.voice.script import chunk, read_marked

    (tmp_path / "v.md").write_text("One two.\n\n> [insert]\n\nNew words here.\n\n> [/insert]\n\nThree four.\n")
    marked = read_marked(tmp_path / "v.md")
    assert [(p, ins) for p, _, ins in marked] == [("One two.", False), ("New words here.", True), ("Three four.", False)]
    assert chunk([p for p, _, ins in marked if not ins]) == ["One two.\n\nThree four."]     # base chunk untouched

    x = tone(0.0, 1.0, 3.0) + tone(1.6, 2.6, 3.0)
    words = [Word("one", 0.0, 0.5), Word("two.", 0.5, 1.0), Word("three", 1.6, 2.1), Word("four.", 2.1, 2.6)]
    extra = tone(0.0, 0.8, 0.8)
    y, out = _splice(x, words, 2, extra, [Word("new", 0.0, 0.4), Word("words", 0.4, 0.8)], rate=RATE)
    assert [w.text for w in out] == ["one", "two.", "new", "words", "three", "four."]
    assert abs(len(y) - len(x) - len(extra) - 2 * int(RATE * 0.3)) <= 2
    assert abs(out[2].start - 1.6) < 0.02 and abs(out[4].start - (1.6 + 0.8 + 0.6)) < 0.02
    for w in out:                                                   # speech is still under every cue
        seg = y[int((w.start + 0.05) * RATE):int((w.start + 0.25) * RATE)]
        assert np.sqrt((seg ** 2).mean()) > 0.2
