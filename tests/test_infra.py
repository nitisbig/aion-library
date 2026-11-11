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


def test_quality_and_design_options(monkeypatch):
    """`--quality 4k --fps 30 --design 2` resolves like the flags and exports the design for theme.py."""
    import os

    import click
    from click.testing import CliRunner

    from aion.cli._common import design_suffix, quality_opts, resolve_quality

    monkeypatch.setenv("AION_DESIGN", "")              # registered with monkeypatch, so teardown restores it
    monkeypatch.delenv("AION_DESIGN")
    seen = {}

    @click.command()
    @quality_opts
    def cmd(quality, res, fps):
        seen.update(q=resolve_quality(quality, res, fps, "final"), design=os.environ.get("AION_DESIGN"),
                    suffix=design_suffix())

    r = CliRunner().invoke(cmd, ["--quality", "4K", "--fps", "30", "--design", "2"])
    assert r.exit_code == 0, r.output
    assert seen == {"q": ("4k", (3840, 2160), 30.0), "design": "2", "suffix": "_d2"}
    monkeypatch.delenv("AION_DESIGN", raising=False)
    assert CliRunner().invoke(cmd, ["--quality", "1080p"]).exit_code == 0 and seen["q"] == ("final", (1920, 1080), 60)
    assert seen["suffix"] == "" and CliRunner().invoke(cmd, ["--quality", "nope"]).exit_code != 0
