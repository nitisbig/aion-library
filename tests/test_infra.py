"""cache / progress / lazy exports."""

import json

import pytest

from aion import cache
from aion.progress import Progress, read_status


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE", tmp_path / "cache")


def test_key_is_stable_and_order_insensitive_for_dicts():
    assert cache.key({"a": 1, "b": 2.0}) == cache.key({"b": 2.0, "a": 1})
    assert cache.key(1, 2) != cache.key(2, 1)
    assert cache.key(0.1 + 0.2) == cache.key(0.3)  # floats canonicalised


def test_file_hash_tracks_content(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("a")
    h1 = cache.file_hash(f)
    f.write_text("bb")
    assert cache.file_hash(f) != h1


def test_get_or_make_runs_once_and_is_atomic():
    calls = []

    def make(tmp):
        calls.append(tmp)
        tmp.write_text("ok")

    p1 = cache.get_or_make("t", ["x"], make, ".txt")
    p2 = cache.get_or_make("t", ["x"], make, ".txt")
    assert p1 == p2 and p1.read_text() == "ok" and len(calls) == 1
    assert not list(p1.parent.glob(".*tmp*"))


def test_atomic_write_leaves_nothing_on_failure(tmp_path):
    dest = tmp_path / "out.bin"

    def boom(tmp):
        tmp.write_text("partial")
        raise RuntimeError

    with pytest.raises(RuntimeError):
        cache.atomic_write(dest, boom)
    assert not dest.exists() and not list(tmp_path.iterdir())


def test_progress_writes_status_json():
    with Progress("pytest-progress", total=10, disable=True) as bar:
        for _ in range(10):
            bar.update()
    s = read_status("pytest-progress")[0]
    assert s["frames"] == 10 and s["percent"] == 100.0 and s["done"] is True


def test_lazy_exports_do_not_import_manim():
    import subprocess
    import sys

    code = "import aion, sys; aion.registry(); print('manim' in sys.modules)"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).stdout
    assert out.strip() == "False"
