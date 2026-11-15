"""No narration: beats set by hand on a silent 20 s track (assets/audio.wav)."""
from aion import Beat, Beats

_TIMES = dict(
    title=0.2,     # "Matrix 3D" draws in
    title2=0.8,    # "Determinant = 0"
    grid=0.6,      # lattice grows out from the origin, axes draw
    eq=2.2,        # det [I] = 1
    cube=2.8,      # yellow unit cube
    s1=4.6,        # column 3: (0,0,1) -> (0,0,2), det 1 -> 2
    s2=8.6,        # column 1: (1,0,0) -> (1,0,1), det stays 2
    s3=12.6,       # column 3: (0,0,2) -> (1,1,1) = c1 + c2, det 2 -> 0
    zero=15.8,     # space lies in a plane: highlight it, pulse the title
)
T = Beats({k: Beat(v, k) for k, v in _TIMES.items()}, duration=20.0, fps=60)
