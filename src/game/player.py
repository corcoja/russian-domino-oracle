from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    id: int
    name: str | None = None

    def __str__(self) -> str:
        display_name = self.name if self.name is not None else "Unnamed"
        return f"P{self.id} ({display_name})"
