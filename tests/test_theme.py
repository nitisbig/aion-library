"""The default theme is the Classic look; MODERN keeps the earlier one."""
from aion import BASE, MODERN


def test_base_is_classic_and_modern_keeps_the_old_look():
    assert (BASE.bg, BASE.text, BASE.bloom, BASE.grain, BASE.vignette) == ("#000000", "#ffffff", 0.0, 0.0, 0.0)
    assert (BASE.grid, BASE.grid_minor, BASE.axis) == ("#1fa2dc", "#0f3e4d", "#ffffff")
    assert (MODERN.bg, MODERN.bloom, MODERN.margin, MODERN.tex_size) == ("#0d1117", 0.35, 0.4, 44)
    assert MODERN.roles == {}
    t = BASE.extend(x="#58c4dd", grid="#123456")
    assert t.x == "#58c4dd" and t.grid == "#123456" and t.axis == "#ffffff"   # roles extend, base roles stay
