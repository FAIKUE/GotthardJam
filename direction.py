from enum import Enum


class Direction(Enum):
    NORTH = 1
    SOUTH = 2

    def __str__(self):
        if self == self.NORTH:
            return "Norden"
        else:
            return "Süden"
