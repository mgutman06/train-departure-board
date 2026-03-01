from setup.rgbcompat import graphics

# Base colours
BLACK = graphics.Color(0, 0, 0)
WHITE = graphics.Color(255, 255, 255)
GREY = graphics.Color(128, 128, 128)

# Amber theme (UK departure board style)
AMBER = graphics.Color(255, 176, 0)
AMBER_DIM = graphics.Color(180, 120, 0)
AMBER_DARK = graphics.Color(100, 65, 0)

# Status colours
GREEN = graphics.Color(0, 200, 0)
RED = graphics.Color(255, 0, 0)
YELLOW = graphics.Color(255, 255, 0)

# Accent colours
ORANGE = graphics.Color(227, 110, 0)
BLUE = graphics.Color(55, 14, 237)
BLUE_LIGHT = graphics.Color(110, 182, 255)
PINK = graphics.Color(200, 0, 200)

# Train display specific
DESTINATION_COLOUR = AMBER
TIME_COLOUR = YELLOW
PLATFORM_COLOUR = WHITE
STATUS_ON_TIME = GREEN
STATUS_DELAYED = AMBER
STATUS_CANCELLED = RED
CALLING_POINTS_COLOUR = AMBER_DIM
OPERATOR_COLOUR = GREY
INDEX_COLOUR = GREY
DIVIDER_COLOUR = AMBER_DARK
STATION_NAME_COLOUR = AMBER
CLOCK_COLOUR = AMBER_DIM
