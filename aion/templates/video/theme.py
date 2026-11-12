"""Semantic colors for this video: each math object keeps ONE color for the whole video.

BASE is the Classic look (black, crisp, Computer Modern; C.grid, C.grid_minor, C.axis built in).
For the earlier blue-black glow look use `from aion import MODERN as BASE`.
"""
from aion import BASE

theme = BASE.extend(
    # x="#58c4dd",      # e.g. the input / vectors
    # fx="#ffe94a",     # e.g. the output / function values
)
