from typing import Protocol

from src.game.hand_tile import HandTile
from src.game.tile import Tile

__all__ = [
    "PenaltyPointsOperator",
    "DEFAULT_PENALTY_POINTS_OPERATOR",
    "compute_hand_penalty_points",
]


class PenaltyPointsOperator(Protocol):
    def __call__(self, tiles: list[HandTile]) -> int:
        ...


class _DefaultPenaltyPointsOperator:

    def __init__(self) -> None:
        self._single_tile_hand_penalty_points: dict[HandTile, int] = {
            HandTile.from_value(Tile(0, 0)): 25,
            HandTile.from_value(Tile(6, 6)): 50,
        }

    def __call__(self, tiles: list[HandTile]) -> int:
        normalized_tiles = [tile.get_normalized_tile() for tile in tiles]

        if len(normalized_tiles) == 1:
            single_tile_penalty_points = self._single_tile_hand_penalty_points.get(normalized_tiles[0])
            if single_tile_penalty_points is not None:
                return single_tile_penalty_points

        return sum(tile.known_value()[0] + tile.known_value()[1] for tile in normalized_tiles)


DEFAULT_PENALTY_POINTS_OPERATOR: PenaltyPointsOperator = _DefaultPenaltyPointsOperator()


def compute_hand_penalty_points(
    tiles: list[HandTile],
    penalty_points_operator: PenaltyPointsOperator = DEFAULT_PENALTY_POINTS_OPERATOR,
) -> int:
    if any(HandTile.is_unknown(tile) for tile in tiles):
        raise ValueError("Cannot compute penalty points with unknown tiles in hand.")

    return penalty_points_operator(tiles)
