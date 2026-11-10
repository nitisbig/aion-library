"""Theme: the channel's visual language as semantic tokens.

Scenes never use raw hex colors or ad-hoc sizes; they use `C.<role>`:

    C.bg, C.text, C.muted, C.accent       # base roles
    C.x, C.fx, C.vec                      # per-video math objects (defined in theme.py)
    C.font, C.body_size, C.stroke

Each video's `theme.py` extends the base theme:

    from aion import Theme, BASE
    theme = BASE.extend(x="#58c4dd", fx="#f2c14e", vec="#ff7a59")

and `video.py` passes it to Video(theme=theme), which activates it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

__all__ = ["Theme", "BASE", "C", "current", "activate"]


@dataclass(frozen=True)
class Theme:
    """Semantic design tokens (colors are sRGB hex).

    Example:
        theme = BASE.extend(x="#58c4dd", fx="#f2c14e", bloom=0.4)   # C.x, C.fx
    """

    bg: str = "#0d1117"              # near-black, slightly blue
    bg2: str = "#161b22"             # raised surfaces / cards
    text: str = "#e6edf3"
    muted: str = "#8b949e"
    faint: str = "#30363d"           # grid lines, guides
    accent: str = "#58c4dd"          # primary highlight (3b1b-ish blue)
    accent2: str = "#f2c14e"         # secondary (gold)
    good: str = "#7ee787"
    bad: str = "#ff7b72"
    font: str = "Inter"
    display_font: str = "Space Grotesk"
    body_size: float = 36            # Text font_size readable on phones at 1080p
    label_size: float = 30
    title_size: float = 64
    tex_size: float = 44             # MathTex font_size
    stroke: float = 4.0
    thin: float = 2.0
    margin: float = 0.4              # Manim units (~5% of the 8-unit frame height)
    lead: float = 0.15               # seconds an animation starts before its beat
    fade: float = 0.6
    move: float = 1.0
    bloom: float = 0.35
    grain: float = 0.025
    vignette: float = 0.25
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


BASE = Theme()
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
