"""Beats of the voyage. The one spoken line gives `look`, `understand`, `said` and the quote card; the
sights on the way in are silent, so they are placed by hand on the flight path (`flight.py`) with sec().
`uv run aion sheet 005 s00` shows one frame per beat.
"""
from aion import beats, end, sec, w  # noqa: F401

T = beats(
    remnant=sec(0.6),       # opening frame: the ringed planet sweeping past, a supernova remnant behind it
    pulsar=sec(2.6),        # neutron star, lighthouse beams; the hole enters at the right edge
    centred=sec(5.0),       # the pan ends: the hole sits in the middle of the frame
    einstein=sec(6.4),      # the spiral galaxy passes exactly behind the hole → Einstein ring
    nova=sec(7.5),          # a star explodes; the hole shows it twice, then as a ring
    look="Look deep",       # the dive starts on the line
    understand="then you will understand",
    skim=sec(12.5),         # 30 M out, 2 M above the disk
    said=end("everything better"),
    black=sec(14.6),        # the shadow has filled the frame (= flight.FLIGHT)
    card=end("better", offset=1.2),                 # portrait and written quote (they leave 5.6 s later)
)
