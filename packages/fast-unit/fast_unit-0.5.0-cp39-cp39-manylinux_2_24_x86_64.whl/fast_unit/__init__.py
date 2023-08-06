import fast_unit.units
from .fast_unit import add_unit, Unum

# Why? Because python hates us
Unum.__lt__ = Unum.__lt__
Unum.__le__ = Unum.__le__
Unum.__ge__ = Unum.__ge__
