"""Classic look (BASE) plus this short's roles. Title colours follow the reference: yellow-green into blue."""
from aion import BASE

theme = BASE.extend(
    vol="#ffe94a",       # the unit cube and the column being changed
    collapse="#ff4fa3",  # det = 0: the plane space is squashed onto
    title1="#c5d84a",    # "Matrix 3D"
    title2="#8cc152",    # "Determinant = 0", left end of the gradient
    title3="#2fb6e8",    # ... right end
    box="#7a7420",       # dim yellow column box
)
