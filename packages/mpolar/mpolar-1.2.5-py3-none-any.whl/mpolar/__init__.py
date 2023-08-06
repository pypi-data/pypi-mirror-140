from mpolar import table_format, list_format, polar


def parse(path: str, sep: str = ";", **kwargs):
    try:
        retval = table_format.parse(path, sep, **kwargs)
    except:
        retval = list_format.parse(path, sep)
    return retval


from mpolar.angle import Angle
from mpolar.interp import ExtrapolationType
Nearest = ExtrapolationType.nearest
LinearAfterNearestBefore = ExtrapolationType.linearAfterNearestBefore

from mpolar.polar import evaluate
from mpolar import propulsion
