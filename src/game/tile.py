from typing import NamedTuple

__all__ = ["Tile", "parse_tile"]


class Tile(NamedTuple):
    """
    Immutable domino tile (NamedTuple-based).
    """

    left_pip: int
    right_pip: int

    @classmethod
    def from_string(cls, tile_text: str) -> "Tile | None":
        """Build a tile from a two-digit string like "13", or return None if invalid."""
        cleaned = tile_text.strip().replace(" ", "")

        if len(cleaned) != 2 or not cleaned.isdigit():
            return None

        left_pip = int(cleaned[0])
        right_pip = int(cleaned[1])

        if 0 <= left_pip <= 6 and 0 <= right_pip <= 6:
            return cls(left_pip, right_pip)

        return None

    def get_normalized_tile(self) -> "Tile":
        """
        Return the same domino in canonical low-high orientation for equality checks.
        """
        return Tile(min(self.left_pip, self.right_pip), max(self.left_pip, self.right_pip))

    def __str__(self) -> str:
        return f"{self.left_pip}-{self.right_pip}"


def parse_tile(tile_text: str) -> Tile | None:
    return Tile.from_string(tile_text)
