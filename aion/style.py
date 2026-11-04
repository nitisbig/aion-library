"""Channel visual style: palette, sizes, timing. Import these instead of ad-hoc values."""

# Background & structure
BG = "#0E1117"          # near-black, slightly blue
GRID = "#2A6F97"        # transformed grid lines
AXIS = "#E6E6E6"        # axes
GHOST = "#5C6370"       # static reference grid behind a transformation
PANEL = "#0E1117"       # background for text/equation panels
PANEL_OPACITY = 0.85

# Text
TEXT = "#ECEFF4"
MUTED = "#9AA5B1"

# Semantic math colors. Keep each object the same color for the whole video.
I_HAT = "#83C167"       # first basis vector  î
J_HAT = "#FC6255"       # second basis vector ĵ
VEC = "#F4D35E"         # a generic vector v
ACCENT = "#58C4DD"

# Sizes
CAPTION_SIZE = 30
MATH_SIZE = 40
TITLE_SIZE = 60
VECTOR_STROKE = 7

# Timing
FADE = 0.6              # standard caption/element fade
LEAD = 0.15             # visuals land slightly before the narration beat
