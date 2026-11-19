"""s26 outro: one plane comes home along its threads, another is crushed and stays flat. The light circles once more, and the video ends where it
began: the key resting on the grid, as it does before anything has moved."""
from functools import lru_cache

from aion import *

from beats import T
from film import frame as opening
from film3 import T_CLEAR, frame


@lru_cache(maxsize=1)
def opening_image():
    """The settled opening shot of the film, so the video ends exactly where it began."""
    return opening(T.lift - 0.45)


@scene(T.cut_outro, T.end)
def s26_outro(s):
    s.solid(C.bg, z=-200)
    s.add(FramesLayer(frame, height=8.0, during=[(T.cut_outro, T.end + 1.0)], z=0))
    s.add(FramesLayer(lambda t: opening_image(), height=8.0, during=[(T_CLEAR + 2.6, T.end + 1.0)], opacity=key(T_CLEAR + 2.6, 0.0, 1.0, dur=1.1, lead=0), z=6))
