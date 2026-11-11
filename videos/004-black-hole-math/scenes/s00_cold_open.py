"""s00 cold open: the finished image first, unexplained. Four seconds of silence, then three calm lines."""
from aion import *

from beats import T
from shots import hero


@scene(T.start, T.cut_intro)
def s00_cold_open(s):
    hero(s)
