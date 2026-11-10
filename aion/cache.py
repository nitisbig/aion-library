"""Content-hash disk cache with atomic writes.

Every expensive artifact (TTS chunks, silence maps, LaTeX atlases, sim bakes,
layer rasters, rendered chunks) is stored under `.aion-cache/<ns>/<key><suffix>`,
where the key hashes *everything* the result depends on. Writes go through a
temp file plus os.replace, so a killed process never leaves a half-written entry
and parallel workers can share the cache.

    from aion import cache
    p = cache.get_or_make("silence", [file_hash(wav), db, min_len],
                          lambda tmp: np.save(tmp, compute()), suffix=".npy")
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from aion._env import CACHE

__all__ = ["key", "file_hash", "tree_hash", "path", "atomic_write", "get_or_make", "usage", "prune"]


def _canon(obj: Any) -> Any:
    if isinstance(obj, (str, int, bool)) or obj is None:
        return obj
    if isinstance(obj, float):
        return repr(round(obj, 9))
    if isinstance(obj, bytes):
        return hashlib.sha256(obj).hexdigest()
    if isinstance(obj, Path):
        return file_hash(obj) if obj.is_file() else str(obj)
    if isinstance(obj, dict):
        return {str(k): _canon(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, (list, tuple)):
        return [_canon(v) for v in obj]
    if hasattr(obj, "tolist"):  # numpy arrays / scalars
        return _canon(obj.tolist())
    if hasattr(obj, "cache_key"):
        return _canon(obj.cache_key())
    return repr(obj)


def key(*parts: Any, n: int = 20) -> str:
    """Stable hex digest of arbitrary JSON-ish parts (paths hash their content)."""
    blob = json.dumps(_canon(parts), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:n]


_FILE_HASHES: dict[tuple[str, int, int], str] = {}


def file_hash(p: str | Path) -> str:
    """sha256 of a file's bytes (memoised on path+mtime+size)."""
    p = Path(p)
    st = p.stat()
    k = (str(p.resolve()), st.st_mtime_ns, st.st_size)
    h = _FILE_HASHES.get(k)
    if h is None:
        d = hashlib.sha256()
        with p.open("rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                d.update(block)
        h = _FILE_HASHES[k] = d.hexdigest()
    return h


def tree_hash(root: str | Path, patterns: tuple[str, ...] = ("*.py", "*.glsl", "*.frag", "*.vert")) -> str:
    """Hash of all matching files under `root` (relative names + contents)."""
    root = Path(root)
    files = sorted({f for pat in patterns for f in root.rglob(pat) if "__pycache__" not in f.parts})
    return key([(str(f.relative_to(root)), file_hash(f)) for f in files])


def path(ns: str, k: str, suffix: str = "") -> Path:
    d = CACHE / ns
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{k}{suffix}"


def atomic_write(dest: str | Path, data: bytes | str | Callable[[Path], None]) -> Path:
    """Write bytes/str, or call `data(tmp_path)` to produce the file, then rename into place."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f".{dest.name}.{os.getpid()}.tmp{dest.suffix}")
    try:
        if callable(data):
            data(tmp)
        elif isinstance(data, str):
            tmp.write_text(data)
        else:
            tmp.write_bytes(data)
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink()
    return dest


def get_or_make(ns: str, parts: Any, make: Callable[[Path], None], suffix: str = "") -> Path:
    """Return the cached file for `parts`, calling `make(tmp_path)` once if missing."""
    dest = path(ns, key(parts), suffix)
    if not dest.exists():
        atomic_write(dest, make)
    return dest


def usage() -> dict[str, tuple[int, int]]:
    """{namespace: (files, bytes)}."""
    out = {}
    if CACHE.exists():
        for d in sorted(p for p in CACHE.iterdir() if p.is_dir()):
            files = [f for f in d.rglob("*") if f.is_file()]
            out[d.name] = (len(files), sum(f.stat().st_size for f in files))
    return out


def prune(older_than_days: float | None = None, ns: str | None = None) -> int:
    """Delete cache entries not accessed for `older_than_days` (all if None). Returns bytes freed."""
    if not CACHE.exists():
        return 0
    cutoff = time.time() - older_than_days * 86400 if older_than_days is not None else None
    roots = [CACHE / ns] if ns else [p for p in CACHE.iterdir() if p.is_dir()]
    freed = 0
    for root in roots:
        if not root.exists():
            continue
        if cutoff is None:
            freed += sum(f.stat().st_size for f in root.rglob("*") if f.is_file())
            shutil.rmtree(root)
            continue
        for f in root.rglob("*"):
            if f.is_file() and max(f.stat().st_atime, f.stat().st_mtime) < cutoff:
                freed += f.stat().st_size
                f.unlink()
    return freed
