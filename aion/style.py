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

# Complex numbers (video 001). Fixed meaning for the whole video.
REAL = ACCENT           # real part, real axis, plain numbers on the line
IMAG = J_HAT            # imaginary part, imaginary axis
I_UNIT = "#B48EF0"      # the number i, quarter-turn arcs
Z = VEC                 # the moving complex number z (arrow)
NEG = "#F2A65A"         # minus one, half turn

# Hessian matrix (video 002). Fixed meaning for the whole video.
# RGB-led and saturated for a crisp look on pure black: red and green are the two input
# axes, blue is "bends up / stable / valley" (calm), orange is "bends down / peak" (alert),
# gold is "you / the slope", violet is the twist that mixes x and y.
HX = "#FF3D5A"          # x direction, x slice, f_xx (red)
HY = "#2EE88A"          # y direction, y slice, f_yy (green)
TWIST = "#A77BFF"       # f_xy, f_yx: the twist (violet)
GRAD = "#FFD43B"        # slope, gradient arrow, the walker (gold)
SMILE = "#2E9BFF"       # bending up, positive eigenvalue, valley (blue)
FROWN = "#FF8A2A"       # bending down, negative eigenvalue, peak (orange)
FLAT = "#8892A2"        # zero bending: flat gauge, "can't tell"
CURVE_A = "#2FE6FF"     # neutral curves and rings: an ice-cyan → lavender sheen
CURVE_B = "#D56BFF"
GRID_MAJOR = "#1A4272"  # graph grids: deep blue on black
GRID_MINOR = "#0D2140"
SURF_LO = "#1B2433"     # surface colour ramp, low → high (neutral slate)
SURF_HI = "#4C5D75"
SURF_LINE = "#8A9BB4"   # coordinate grid drawn on a surface
FOG = "#2B3442"

# Luminous terrain (TerrainPlate, Aion design system: black stage, light only from
# thin geometry). Neutral silver so the semantic colours keep their meaning on top.
STAGE = "#000000"         # design-system `stage`
STAGE_RAISED = "#05070A"  # design-system `stage-raised`: glass-cell bodies
LINE = "#2A3140"          # design-system `line`: glass rims at rest
GLASS_TOP = "#0E131C"     # design-system glass-top (opaque on black)
GLASS_BOTTOM = "#04060A"  # design-system glass-bottom
TERRAIN_LINE = "#C9D4E3"  # contour and wire lines on the ground
TERRAIN_BODY = "#06080C"  # the ground itself, one step off black
MIST = "#9FB0C6"          # drifting mist particles and fog banks
LIGHT = "#FFE9C7"         # design-system `light`: light sweeps and glints only
# Gaussian-splat world (intro): altitude ramp, valley floor → peaks. Kept away from the
# semantic blue/orange by staying in teal / indigo / violet / magenta with a warm crest.
# parametric ground fill (intro): corner colours of a bilinear gradient over (x, y)
GROUND_GRADIENT = ("#0FC2B0", "#2F6BFF", "#8A3BFF", "#FF3FA8")
SPLAT_RAMP = ("#0A6E7A", "#12C8C0", "#3A5BFF", "#8B45FF", "#E23FD0", "#FFC79A")

# Typography
FONT_DISPLAY = "SpaceGrotesk[wght].ttf"   # design-system display face (title lockups), in aion/assets/fonts
FONT = "Inter Variable"   # captions and labels (Text); math stays LaTeX
LABEL_WEIGHT = "LIGHT"    # thin, professional labels (Inter Light); headings pass weight= themselves
# math typeface: Libertinus text + maths: thin, refined, professional
TEX_PREAMBLE = r"\usepackage{libertinus-type1}\usepackage{libertinust1math}"
