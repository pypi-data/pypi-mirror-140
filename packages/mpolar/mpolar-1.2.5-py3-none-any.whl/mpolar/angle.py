from typing import List


def should_be_mirrored(coordinates_values: List[float]) -> bool:
    # Most often, angle polar coordinates are in the [0, 180] range because the ]180, 360[ range is just a mirror
    return Angle(coordinates_values[0]).degrees < 180 and Angle(coordinates_values[-1]).degrees <= 180


class Angle:
    def __init__(self, degrees: float):
        self.__degrees = degrees

    @property
    def degrees(self) -> float:
        # The angles should be kept in [0, 360] range
        return self.__degrees % 360

    def degrees_for_coordinate(self, values: List[float]) -> float:
        if should_be_mirrored(values):
            retval = self.degrees
            if retval > 180:
                return 180 - (retval - 180)
        return self.degrees
