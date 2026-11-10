"""Paths and environment: repo root, media/cache dirs, .env secrets, TinyTeX on PATH.

Importing `aion` calls `setup()` once. Everything else asks this module for
directories, so nothing hard-codes paths.
"""

from __future__ import annotations

import os
import shutil
from functools import lru_cache
from pathlib import Path

ROOT = Path(os.environ.get("AION_ROOT", Path(__file__).resolve().parents[1]))
MEDIA = Path(os.environ.get("AION_MEDIA", ROOT / "media"))
CACHE = Path(os.environ.get("AION_CACHE", ROOT / ".aion-cache"))
VIDEOS = ROOT / "videos"
PKG = Path(__file__).resolve().parent
ASSETS = PKG / "assets"
SHADERS = PKG / "shaders"


def ensure_latex_on_path() -> None:
    """Put TinyTeX (installed by pytinytex) on PATH if latex/dvisvgm are missing."""
    if shutil.which("latex") and shutil.which("dvisvgm"):
        return
    try:
        import pytinytex

        bin_dir = pytinytex.get_tinytex_path()
    except Exception:
        bin_dir = os.path.expanduser("~/.pytinytex/.TinyTeX/bin/x86_64-linux")
    if bin_dir and os.path.isdir(bin_dir):
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


@lru_cache(maxsize=1)
def load_dotenv() -> None:
    """Load ROOT/.env into os.environ (never overrides variables already set)."""
    path = ROOT / ".env"
    if not path.exists():
        return
    try:
        from dotenv import load_dotenv as _load

        _load(path, override=False)
    except ImportError:  # minimal fallback parser
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def secret(name: str) -> str | None:
    """Read a secret from the environment or ROOT/.env. Never log the value."""
    load_dotenv()
    return os.environ.get(name) or None


def media_dir(*parts: str) -> Path:
    d = MEDIA.joinpath(*parts)
    d.mkdir(parents=True, exist_ok=True)
    return d


def setup() -> None:
    ensure_latex_on_path()
