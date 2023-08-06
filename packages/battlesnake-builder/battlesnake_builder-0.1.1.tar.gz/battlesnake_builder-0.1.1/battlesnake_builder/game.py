
class Ruleset():
    name: str
    version: str

    @classmethod
    def from_json(cls, json: dict):
        ruleset = cls()
        ruleset.name = json["name"]
        ruleset.version = json["version"]
        return ruleset


class Game():
    id: str
    ruleset: Ruleset
    timeout: int

    @classmethod
    def from_json(cls, json: dict):
        game = cls()
        game.id = json["id"]
        game.ruleset = Ruleset.from_json(json["ruleset"])
        game.timeout = json["timeout"]
        return game
