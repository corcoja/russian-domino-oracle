from dataclasses import dataclass

from src.models.tile import Tile
from src.models.unknown_tile import UnknownTile

__all__ = ["Player", "HandTile"]

HandTile = Tile | UnknownTile


@dataclass
class Player:
    """
    Represents one player in the tracked game state.

    The main player stores known tiles in ``hand``. Opponents store ``UnknownTile`` placeholders in ``hand`` so the hand
    length remains the source of truth for their tile count.
    """

    id: int
    is_main_player: bool
    hand: list[HandTile]
