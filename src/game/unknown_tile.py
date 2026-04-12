from dataclasses import dataclass

__all__ = ["UnknownTile"]


@dataclass(frozen=True)
class UnknownTile:

    def __repr__(self) -> str:
        return "UnknownTile()"
