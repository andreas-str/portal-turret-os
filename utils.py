# Turret movement enumeration
LEFT_WING = 0
RIGHT_WING = 1
BOTH_WINGS = 3
WING_UP = 4
WING_DOWN = 5
TURRET_LEFT = 6
TURRET_RIGHT = 7
TURRET_FULL_ROTATE = 8

# Party modes
OPERA = 20
WIFE = 21

# Search timeout in seconds
SEARCH_TIMEOUT = 25

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
