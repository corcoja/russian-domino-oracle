from dataclasses import dataclass
from typing import TypeGuard

from .tile import Tile
from .unknown_tile import UnknownTile


@dataclass(frozen=True)
class HandTile:
    value: Tile | UnknownTile

    @classmethod
    def from_value(cls, tile: "HandTile | Tile | UnknownTile") -> "HandTile":
        if isinstance(tile, HandTile):
            return tile
        return cls(value=tile)

    @staticmethod
    def is_known(tile: "HandTile") -> TypeGuard["HandTile"]:
        return isinstance(tile.value, Tile)

    @staticmethod
    def is_unknown(tile: "HandTile") -> TypeGuard["HandTile"]:
        return isinstance(tile.value, UnknownTile)

    def known_value(self) -> Tile:
        if not isinstance(self.value, Tile):
            raise ValueError("Unknown tiles cannot be used for pip operations.")
        return self.value

    def get_normalized_tile(self) -> "HandTile":
        return HandTile.from_value(self.known_value().get_normalized_tile())

    def __getitem__(self, index: int) -> int:
        tile = self.known_value()
        if index == 0:
            return tile.left_pip
        if index == 1:
            return tile.right_pip
        raise IndexError("HandTile index out of range.")

    def __contains__(self, pip: object) -> bool:
        if not isinstance(pip, int):
            return False
        tile = self.known_value()
        return pip in tile

    def oriented_for_left_end(self, left_end: int) -> "HandTile | None":
        tile = self.known_value()
        if tile.right_pip == left_end:
            return self
        if tile.left_pip == left_end:
            return HandTile.from_value(Tile(tile.right_pip, tile.left_pip))
        return None

    def oriented_for_right_end(self, right_end: int) -> "HandTile | None":
        tile = self.known_value()
        if tile.left_pip == right_end:
            return self
        if tile.right_pip == right_end:
            return HandTile.from_value(Tile(tile.right_pip, tile.left_pip))
        return None

    def __str__(self) -> str:
        return str(self.value)
