from enum import Enum


class SnakeEnd(str, Enum):
    """
    Represents a placement direction on the domino snake.

    Used within the game flow to indicate which end of the snake a new domino should be played: either the left or right
    end.
    """

    LEFT = "left"
    RIGHT = "right"
