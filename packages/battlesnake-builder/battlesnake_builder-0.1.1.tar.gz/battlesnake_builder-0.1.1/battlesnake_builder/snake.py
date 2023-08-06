from battlesnake_builder.coordinate import Coordinate


class BodyFragment():
    coord: Coordinate

    @classmethod
    def from_json(cls, json: dict):
        body_fragment = cls()
        body_fragment.coord = Coordinate.from_json(json)
        return body_fragment


class Snake():
    id: str
    name: str
    head: BodyFragment
    body: list[BodyFragment]
    health: int
    latency: str
    length: int
    shout: str
    squad: str

    def __eq__(self, other) -> bool:
        if type(other) is Snake:
            return self.id == other.id
        else:
            raise ValueError()

    @classmethod
    def from_json(cls, json: dict):
        snake = cls()
        snake.id = json["id"]
        snake.name = json["name"]
        snake.head = BodyFragment.from_json(json["head"])
        snake.body = [BodyFragment.from_json(x) for x in json["body"]]
        snake.health = json["health"]
        snake.latency = json["latency"]
        snake.length = json["length"]
        snake.shout = json["shout"]
        snake.squad = json["squad"]
        return snake
