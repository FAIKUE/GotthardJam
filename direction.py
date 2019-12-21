# -*- coding: utf-8 -*-

from enum import Enum


class Direction(Enum):
    north = 1
    south = 2

    def __str__(self):
        if self == Direction.north:
            return "Norden"
        else:
            return "Süden"
