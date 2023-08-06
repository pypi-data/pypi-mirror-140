from __future__ import annotations
import math
from typing import Literal


class Coordinate():
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        if type(other) is Coordinate:
            return Coordinate(self.x + other.x, self.y + other.y)
        else:
            raise ValueError()

    def real_distance(self, other: Coordinate):
        """
        Get the real distance between this and the passed in coordinate
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def manhattan_distance(self, other: Coordinate):
        """
        Get the manhattan distance between this and the passed in coordinate
        """
        return (self.x - other.x) + (self.y - other.y)

    def direction_to(self, other: Coordinate) -> Literal["up", "down", "left", "right"]:
        """
        The direction to go, to reach the given coordinate
        """
        if other.y != self.y:
            if other.y > self.y:
                return "up"
            else:
                return "down"
        else:
            if other.x > self.x:
                return "right"
            else:
                return "left"

    @classmethod
    def from_json(cls, json: dict):
        return cls(json["x"], json["y"])
