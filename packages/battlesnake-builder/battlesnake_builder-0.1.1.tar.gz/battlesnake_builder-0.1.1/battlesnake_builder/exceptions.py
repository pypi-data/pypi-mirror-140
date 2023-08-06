class GameNotStarted(Exception):
    def __str__(self) -> str:
        return "interacted with game before it was started"
