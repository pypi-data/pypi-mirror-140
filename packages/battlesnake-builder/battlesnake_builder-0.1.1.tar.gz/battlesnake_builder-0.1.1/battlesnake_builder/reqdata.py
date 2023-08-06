from battlesnake_builder.snake import Snake
from battlesnake_builder.board import Board
from battlesnake_builder.game import Game


class Data():
    game: Game
    turn: int
    board: Board
    you: Snake

    @classmethod
    def from_json(cls, json: dict):
        data = cls()
        data.game = Game.from_json(json["game"])
        data.turn = json["turn"]
        data.board = Board.from_json(json["board"])
        data.you = Snake.from_json(json["you"])
        return data
