from typing import Literal
from battlesnake_builder.coordinate import Coordinate
from battlesnake_builder.snake import Snake


class Board():
    height: int
    width: int
    food: list[Coordinate]
    hazards: list[Coordinate]
    snakes: list[Snake]

    def closest_food(self, snake: Snake) -> Coordinate:
        return sorted(self.food, key=lambda x: snake.head.coord.manhattan_distance(x))[0]

    def closest_snake(self, snake: Snake) -> Snake | None:
        """
        Get the closest snake to another snake
        """
        if len(self.snakes) <= 1:
            return None

        lowest_dist = -1
        lowest_dist_snake = None

        for other_snake in self.snakes:
            if other_snake == snake:
                continue
            for body_part in (other_snake.body + other_snake.head):
                distance = body_part.coord.manhattan_distance(snake.head.coord)
                if distance < lowest_dist or lowest_dist == -1:
                    lowest_dist = distance
                    lowest_dist_snake = other_snake
                    break

        return lowest_dist_snake

    def is_move_safe(self, snake: Snake, move: Literal["up", "down", "left", "right"]) -> bool:
        """
        Check whether a move in a certain direction is safe
        """
        direction_coords = {
            "up": Coordinate(0, 1),
            "down": Coordinate(0, -1),
            "left": Coordinate(-1, 0),
            "right": Coordinate(1, 0)
        }
        new_coord = snake.head.coord + direction_coords[move]

        if (new_coord.x > self.width - 1 or new_coord.x < 0 or
                new_coord.y > self.height - 1 or new_coord.y < 0):
            return False

        for other_snake in self.snakes:
            for x in (other_snake.body + other_snake.head):
                if x.coord == new_coord:
                    return False

        for hazard in self.hazards:
            if hazard == new_coord:
                return False

        return True

    @classmethod
    def from_json(cls, json: dict):
        board = cls()
        board.height = json["height"]
        board.width = json["width"]
        board.food = [Coordinate.from_json(x) for x in json["food"]]
        board.hazards = [Coordinate.from_json(x) for x in json["hazards"]]
        board.snakes = [Snake.from_json(x) for x in json["snakes"]]
        return board
