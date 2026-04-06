
__all__ = ["Tile", "parse_tile"]

Tile = tuple[int, int]


def parse_tile(tile_text: str) -> Tile | None:
    cleaned = tile_text.strip().replace(" ", "")

    if len(cleaned) != 2 or not cleaned.isdigit():
        return None

    left_pip = int(cleaned[0])
    right_pip = int(cleaned[1])

    if 0 <= left_pip <= 6 and 0 <= right_pip <= 6:
        return (left_pip, right_pip)

    return None
