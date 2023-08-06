from typing import List, Tuple, Optional
import enum

import numpy as np


class ExtrapolationType(enum.Enum):
    nearest = 0
    linearAfterNearestBefore = 1


def closest_indexes(coord: List[float], value: float, extrapolate: Optional[ExtrapolationType]) -> Tuple[Tuple[int, int], float]:
    """Returns the two closest indexes in the coordinates list and the ratio the value is at
    Note: we always consider the coordinate to be ordered

    :param coord:
    :param value:
    :return:
    """
    # extrapolate values after
    if value > coord[-1]:
        if extrapolate is None:
            raise Exception("Can't read outside of data range without extrapolation")
        elif extrapolate == ExtrapolationType.nearest:
            return (len(coord) - 1, len(coord) - 1), 1.0
        elif extrapolate == ExtrapolationType.linearAfterNearestBefore:
            min_index = len(coord) - 2
            max_index = len(coord) - 1

    else:
        closest_greater_index = np.argmin([v if v >= 0 else np.inf for v in np.array(coord) - value])
        max_index = closest_greater_index
        min_index = closest_greater_index - 1

        # extrapolate values before
        if min_index < 0:
            if extrapolate is None:
                raise Exception("Can't read outside of data range without extrapolation")
            elif extrapolate == ExtrapolationType.nearest or extrapolate == ExtrapolationType.linearAfterNearestBefore:
                return (0, 0), 1.0

    return (min_index, max_index), (value - coord[min_index]) / (coord[max_index] - coord[min_index])
