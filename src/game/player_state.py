from dataclasses import dataclass
from typing import Iterable

from .hand_tile import HandTile
from .player import Player


@dataclass(frozen=True)
class PlayerState:
    player: Player
    hand: tuple[HandTile, ...]

    @classmethod
    def with_hand_tiles(cls, player: Player, hand_tiles: Iterable[HandTile]) -> "PlayerState":
        return cls(player=player, hand=tuple(hand_tiles))

    def with_hand(self, hand_tiles: Iterable[HandTile]) -> "PlayerState":
        return PlayerState(player=self.player, hand=tuple(hand_tiles))

    def with_added_hand_tile(self, hand_tile: HandTile) -> "PlayerState":
        return self.with_hand([*self.hand, hand_tile])

    def with_removed_hand_tile_at(self, index: int) -> "PlayerState":
        if index < 0 or index >= len(self.hand):
            raise ValueError("Hand index out of range.")
        return self.with_hand([tile for i, tile in enumerate(self.hand) if i != index])
