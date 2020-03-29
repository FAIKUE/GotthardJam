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

    @staticmethod
    def get_direction_from_city(city):
        """Returns the direction in which the tunnel is impaired by the city given by tcs as destination."""
        return Direction.south if city is "Luzern" else Direction.north
