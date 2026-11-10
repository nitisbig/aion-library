"""core (ease, tracks, clock, noise) and sync (cue, beats, silences, cuts)."""

import numpy as np
import pytest

from aion.core.clock import Clock
from aion.core.ease import EASES, cubic_bezier, ease
from aion.core.noise import hash01, noise1
from aion.core.time import FrameGrid
from aion.core.track import fade, key, keys, pulse, track
from aion.sync.beats import beats, cut, end, w
from aion.sync.cue import Cue, fmt_srt_time, parse_srt_time
from aion.sync.cuts import check_contiguous
from aion.sync.silence import audio_duration, silences

from conftest import DURATION


# ── core ─────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("name", sorted(EASES))
def test_eases_hit_endpoints(name):
    f = ease(name)
    if name == "there_and_back":
        assert abs(f(0.5) - 1) < 1e-6 and abs(f(1)) < 1e-6
    else:
        assert abs(float(f(0))) < 1e-6 and abs(float(f(1)) - 1) < 1e-3


def test_cubic_bezier_easy_ease_symmetric():
    f = cubic_bezier(0.33, 0, 0.67, 1)
    assert abs(f(0.5) - 0.5) < 1e-3 and f(0.25) < 0.25


def test_key_lands_on_beat_with_lead():
    tr = key(2.0, 0.0, 1.0, dur=1.0, lead=0.15)
    assert tr(1.85) == 0.0 and tr(2.85) == 1.0 and 0 < tr(2.3) < 1
    assert tr.changes(2.0, 2.1) and not tr.changes(3.0, 10)


def test_track_arithmetic_and_arrays():
    tr = 0.5 + pulse(3.0, 1.0, dur=0.6)
    assert tr(0) == 0.5 and abs(tr(3.0) - 1.5) < 1e-9
    m = key(1.0, np.eye(2), [[2, 0], [0, 1]], dur=1, lead=0)
    assert np.allclose(m(5), [[2, 0], [0, 1]]) and np.allclose(m(0), np.eye(2))
    assert not track(3.0).changes(-1e9, 1e9)


def test_keys_and_fade_out():
    tr = keys((0, 0.0), (1, 1.0), (2, 0.0), default_ease="linear")
    assert abs(tr(0.5) - 0.5) < 1e-9 and abs(tr(1.5) - 0.5) < 1e-9
    f = fade(1.0, out=3.0, dur=0.5, lead=0)
    assert f(0.5) == 0 and f(2.0) == 1 and f(4) == 0


def test_clock_integrates_rate():
    c = Clock(rate=key(2.0, 1.0, 0.0, dur=1.0, lead=0, ease="linear"), start=0.0, end=5.0)
    assert abs(c(2.0) - 2.0) < 1e-3 and abs(c(5.0) - 2.5) < 1e-3


def test_noise_is_deterministic():
    assert hash01(1, 2) == hash01(1, 2) != hash01(2, 1)
    assert noise1(3.7, 5) == noise1(3.7, 5) and -1 <= noise1(3.7, 5) <= 1


def test_frame_grid():
    g = FrameGrid(60)
    assert g.frame(1.0) == 60 and g.frame(1 / 60 * 7) == 7 and g.count(0, 2) == 120


# ── sync ─────────────────────────────────────────────────────────────────────
def test_srt_time_roundtrip():
    for t in (0, 0.06, 61.234, 3725.5):
        assert abs(parse_srt_time(fmt_srt_time(t)) - t) < 1e-3


def test_cue_lookups(fixture_video):
    cue = Cue.load(fixture_video / "assets" / "cue-per-word.srt")
    assert cue.at("grid") == 0.7 and cue.at("ARROW") == 2.7
    assert cue.at("arrow", after=3.0) == 5.35 and cue.at("arrow", nth=2) == 5.35
    assert cue.phrase("this arrow") == (2.4, 3.1)
    assert cue.text(2.4, 3.2) == "This arrow stretches."
    assert len(cue.segments()) == 3
    with pytest.raises(KeyError, match="occurs at"):
        cue.at("grid", after=2)


def test_silences_and_duration(fixture_video):
    wav = fixture_video / "assets" / "audio.wav"
    assert abs(audio_duration(wav) - DURATION) < 1e-6
    sil = silences(wav)
    assert any(a <= 1.9 and b >= 2.3 for a, b in sil)   # gap between sentences 1 and 2


def test_beats_ordered_and_cuts(fixture_video):
    T = beats(fixture_video / "assets" / "cue-per-word.srt", audio=fixture_video / "assets" / "audio.wav",
              grid="a grid", arrow="arrow", c1=cut("stretches", "now watch"),
              nudged=w("watch", offset=-0.1), arrow2="arrow", done=end("again"))
    assert T.arrow == 2.7 and T.arrow2 == 5.35          # second "arrow" thanks to ordering
    assert T.done == 6.4 and abs(T.nudged - 4.7) < 1e-9
    assert 3.9 < T.c1 < 4.5 and not T.c1.soft            # inside the real silence
    assert abs(T.c1 * 60 - round(T.c1 * 60)) < 1e-9       # frame-snapped
    assert [b.name for b in T.cuts] == ["start", "c1", "end"] and T.end == DURATION
    with pytest.raises(AttributeError, match="did you mean"):
        T.arow


def test_beats_from_caller_folder(fixture_video):
    (fixture_video / "beats.py").write_text(
        "from aion.sync.beats import beats, cut\nT = beats(a=cut('lines', 'this'))\n")
    import importlib.util

    spec = importlib.util.spec_from_file_location("fx_beats", fixture_video / "beats.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert 1.8 < mod.T.a < 2.4


def test_check_contiguous():
    check_contiguous([("a", 0, 2.5), ("b", 2.5, 7.0)], 7.0)
    with pytest.raises(ValueError, match="ends 2.500s but b starts 2.600s"):
        check_contiguous([("a", 0, 2.5), ("b", 2.6, 7.0)], 7.0)
