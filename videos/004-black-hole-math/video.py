"""Video settings. Scenes live in scenes/sNN_*.py; timing in beats.py; colors in theme.py."""
from aion import Video

from theme import theme

video = Video(theme=theme, fps=60, title="The Math That Shows You a Black Hole")
