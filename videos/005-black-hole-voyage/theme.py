"""The voyage uses video 004's theme unchanged (same designs, same `--design N`), so the two clips match."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "theme_004", Path(__file__).resolve().parent.parent / "004-black-hole-math" / "theme.py")
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)

DESIGNS, DESIGN, theme = _m.DESIGNS, _m.DESIGN, _m.theme
