"""No narration in this lab: beats are set by hand on a silent 20 s track (assets/audio.wav)."""
from aion import Beat, Beats

_TIMES = dict(
    floor=0.3,      # floor grid fades in
    tilt=0.8,       # camera tips from top-down to an oblique view
    hats=1.8,       # i, j, k grow one after another
    cube=3.0,       # unit cube + identity matrix
    shear=4.2,      # I -> A (shear + stretch), det 1 -> 2
    rotate=8.2,     # rotate everything 90 deg about x (tips over), det stays 2
    squash=12.2,    # flatten z: det -> 0, the cube becomes a parallelogram on the floor
    restore=16.0,   # everything returns to the identity
    out=19.2,       # HUD fades
)
T = Beats({k: Beat(v, k) for k, v in _TIMES.items()}, duration=20.0, fps=60)
