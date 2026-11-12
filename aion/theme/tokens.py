"""Theme: the channel's visual language as semantic tokens.

Scenes never use raw hex colors or ad-hoc sizes; they use `C.<role>`:

    C.bg, C.text, C.muted, C.accent       # base roles
    C.grid, C.grid_minor, C.axis          # coordinate grids (part of BASE)
    C.x, C.fx, C.vec                      # per-video math objects (defined in theme.py)
    C.font, C.body_size, C.stroke

The default, `BASE`, is the Classic look: pure black, crisp unglowed lines, a bright blue
integer grid over a dim half-step grid, white axes, Computer Modern math, no bloom, grain or
vignette. `MODERN` keeps the earlier look (blue-black, soft bloom, grain) for videos built on it.

Each video's `theme.py` extends one of them:

    from aion import Theme, BASE
    theme = BASE.extend(x="#58c4dd", fx="#f2c14e", vec="#ff7a59")

and `video.py` passes it to Video(theme=theme), which activates it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

__all__ = ["Theme", "BASE", "MODERN", "C", "current", "activate"]


@dataclass(frozen=True)
class Theme:
    """Semantic design tokens (colors are sRGB hex).

    Example:
        theme = BASE.extend(x="#58c4dd", fx="#f2c14e", bloom=0.4)   # C.x, C.fx
    """

    bg: str = "#000000"              # Classic: pure black
    bg2: str = "#161616"             # raised surfaces / cards
    text: str = "#ffffff"
    muted: str = "#a6a6a6"
    faint: str = "#3a3a3a"           # de-emphasised marks, struck-out formulas
    accent: str = "#58c4dd"          # primary highlight (classic blue)
    accent2: str = "#ffe94a"         # secondary (classic yellow)
    good: str = "#83c167"            # classic green
    bad: str = "#fc6255"             # classic red
    font: str = "Inter"
    display_font: str = "Space Grotesk"
    body_size: float = 36            # Text font_size readable on phones at 1080p
    label_size: float = 30
    title_size: float = 64
    tex_size: float = 48             # MathTex font_size
    stroke: float = 4.0
    thin: float = 1.6
    margin: float = 0.45             # Manim units (~5.6% of the 8-unit frame height)
    lead: float = 0.15               # seconds an animation starts before its beat
    fade: float = 0.6
    move: float = 1.0
    bloom: float = 0.0               # crisp: no glow, grain or vignette by default
    grain: float = 0.0
    vignette: float = 0.0
    tex_preamble: str = r"\usepackage{amsmath}\usepackage{amssymb}"
    roles: dict = field(default_factory=dict)   # per-video math-object colors (C.x, C.fx…)

    def extend(self, **tokens: Any) -> "Theme":
        """New theme: known fields replaced, anything else becomes a role color."""
        known = {k: v for k, v in tokens.items() if k in self.__dataclass_fields__ and k != "roles"}
        roles = {**self.roles, **{k: v for k, v in tokens.items() if k not in self.__dataclass_fields__}}
        return replace(self, roles=roles, **known)

    def __getattr__(self, name: str):
        roles = object.__getattribute__(self, "roles")
        if name in roles:
            return roles[name]
        raise AttributeError(f"theme has no token {name!r}; define it in theme.py (BASE.extend({name}=...))")

    def cache_key(self):
        return repr(self)


_CLASSIC_ROLES = dict(grid="#1fa2dc", grid_minor="#0f3e4d", axis="#ffffff", ghost="#2b2b2b", frame="#bdbdbd")

BASE = Theme(roles=_CLASSIC_ROLES)
"""The default Classic theme. Example: `theme = BASE.extend(x="#58c4dd")` → C.x, plus C.grid, C.axis…"""

MODERN = Theme(bg="#0d1117", bg2="#161b22", text="#e6edf3", muted="#8b949e", faint="#30363d", accent="#58c4dd",
               accent2="#f2c14e", good="#7ee787", bad="#ff7b72", tex_size=44, thin=2.0, margin=0.4, bloom=0.35,
               grain=0.025, vignette=0.25)
"""The earlier default (blue-black, soft bloom, grain, vignette), kept so older videos render unchanged.
Example: `from aion import MODERN; theme = MODERN.extend(x="#58c4dd")`."""
_ACTIVE: list[Theme] = [BASE]


def current() -> Theme:
    return _ACTIVE[0]


def activate(theme: Theme) -> Theme:
    """Make `theme` the active theme (sets default lead, Manim defaults)."""
    from aion.core.time import set_lead

    _ACTIVE[0] = theme
    set_lead(theme.lead)
    try:
        import sys

        if "manim" in sys.modules:
            from aion.theme.manim import apply

            apply(theme)
    except Exception:
        pass
    return theme


class _Proxy:
    """`C.<token>` reads the active theme at call time."""

    def __getattr__(self, name):
        return getattr(current(), name)

    def __repr__(self):
        return f"C → {current()!r}"


C = _Proxy()
