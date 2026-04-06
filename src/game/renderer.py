from src.game.game_state import GameState
from src.models.tile import Tile

PIP_ART: dict[int, tuple[str, str, str]] = {
    0: ("     ", "     ", "     "),
    1: ("     ", "  *  ", "     "),
    2: ("*    ", "     ", "    *"),
    3: ("*    ", "  *  ", "    *"),
    4: ("*   *", "     ", "*   *"),
    5: ("*   *", "  *  ", "*   *"),
    6: ("*   *", "*   *", "*   *"),
}


def render_tile(tile: Tile) -> list[str]:
    left, right = tile
    left_grid = PIP_ART[left]
    right_grid = PIP_ART[right]

    lines = ["+-----+-----+"]
    for i in range(3):
        lines.append(f"|{left_grid[i]}|{right_grid[i]}|")
    lines.append("+-----+-----+")
    return lines


def render_snake(snake: list[Tile]) -> str:
    if not snake:
        return "(no snake)"

    tiles = [render_tile(tile) for tile in snake]
    rendered_lines: list[str] = []

    for line_index in range(len(tiles[0])):
        rendered_lines.append(" ".join(tile[line_index] for tile in tiles))

    return "\n".join(rendered_lines)


def format_state_snapshot(game: GameState) -> str:
    lines: list[str] = []
    lines.append(f"Stock size: {game.stock_size}")
    lines.append("Players:")
    lines.append(f"  - P{game.main_player.id} (you): {len(game.main_player.hand)} tiles")
    for player in sorted(game.opponents, key=lambda current: current.id):
        lines.append(f"  - P{player.id}: {len(player.hand)} tiles")

    lines.append("Your hand:")
    for idx, tile in enumerate(game.my_hand):
        lines.append(f"  [{idx}] {tile[0]}{tile[1]}")

    lines.append("Snake:")
    lines.append(render_snake(game.snake))
    return "\n".join(lines)
