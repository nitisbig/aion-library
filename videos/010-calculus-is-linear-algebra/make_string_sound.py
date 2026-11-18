"""Superseded by make_sfx.py, which builds the s13 string note together with the rest of the sound design.

Kept so the old command still works:  uv run python videos/010-calculus-is-linear-algebra/make_string_sound.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_sfx import main  # noqa: E402

if __name__ == "__main__":
    main()
