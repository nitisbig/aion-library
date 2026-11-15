"""Classic look (BASE) plus one colour per object for this experiment."""
from aion import BASE

theme = BASE.extend(
    ihat="#83c167",      # first column / x-axis arrow
    jhat="#fc6255",      # second column / y-axis arrow
    khat="#58c4dd",      # third column / z-axis arrow
    vol="#ffe94a",       # the unit cube and the determinant when non-zero
    collapse="#ff4fa3",  # det = 0: the plane space is squashed onto
)
