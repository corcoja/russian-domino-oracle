from pyfiglet import Figlet

from src.game.game_state import GameState
from src.game.hand_tile import HandTile
from src.game.penalty_points import compute_hand_penalty_points

PIP_ART: dict[int, tuple[str, str, str]] = {
    0: ("     ", "     ", "     "),
    1: ("     ", "  *  ", "     "),
    2: ("*    ", "     ", "    *"),
    3: ("*    ", "  *  ", "    *"),
    4: ("*   *", "     ", "*   *"),
    5: ("*   *", "  *  ", "*   *"),
    6: ("*   *", "*   *", "*   *"),
}


def game_title_logo() -> str:
    figlet = Figlet(font="big", width=100)
    return figlet.renderText("Kozel Domino Oracle")


def render_tile(tile: HandTile) -> list[str]:
    left, right = tile
    left_grid = PIP_ART[left]
    right_grid = PIP_ART[right]

    lines = ["+-----+-----+"]
    for i in range(3):
        lines.append(f"|{left_grid[i]}|{right_grid[i]}|")
    lines.append("+-----+-----+")
    return lines


def render_snake(snake: tuple[HandTile, ...] | list[HandTile]) -> str:
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
    lines.append(f"Move order: {' '.join(str(player_id) for player_id in game.player_move_order)}")
    next_player_state = game.get_player_state_by_id(game.next_player_move)
    lines.append(f"Next player to move: {next_player_state.player}")
    lines.append("Players:")
    for player_state in sorted(game.player_states, key=lambda current: current.player.id):
        lines.append(f"  - {player_state.player}: {len(player_state.hand)} tiles")

    lines.append("Your hand:")
    if not game.main_player_hand:
        lines.append("  (empty)")
    else:
        for tile in game.main_player_hand:
            lines.append(f"  - {tile}")

    hand_penalty_points = compute_hand_penalty_points(list(game.main_player_hand))
    lines.append(f"Your penalty points: {hand_penalty_points}")

    lines.append("Snake:")
    lines.append(render_snake(game.snake))
    return "\n".join(lines)
