import math
from .fast_unit import add_unit

m = add_unit("m", "meter")
s = add_unit("s", "second")

rad = m / m
deg = rad * (math.pi / 180)
rev = 360 * deg

ft = 0.3048 * m
inch = ft / 12
mile = 1609.34 * m

ms = s / 1000
minute = s * 60
hour = m * 60
