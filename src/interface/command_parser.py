from dataclasses import dataclass
from enum import Enum

from src.models.tile import parse_tile
from src.models.unknown_tile import UnknownTile
from src.game.game_state import GameState
from src.game.game_move import GameMove
from src.game.game_move_type import GameMoveType
from src.game.snake_end import SnakeEnd


class ParsedCommandType(str, Enum):
    QUIT = "quit"
    HELP = "help"
    SHOW = "show"
    GAME_MOVE = "game_move"


@dataclass(frozen=True)
class ParsedCommand:
    command_type: ParsedCommandType
    game_move: GameMove | None = None


def parse_command(command: str, game: GameState) -> ParsedCommand:
    text = command.strip().lower()

    match text:
        case "quit":
            return ParsedCommand(command_type=ParsedCommandType.QUIT)
        case "help":
            return ParsedCommand(command_type=ParsedCommandType.HELP)
        case "show":
            return ParsedCommand(command_type=ParsedCommandType.SHOW)
        case _:
            return ParsedCommand(command_type=ParsedCommandType.GAME_MOVE, game_move=parse_game_move(text, game))


def parse_game_move(command: str, game: GameState) -> GameMove:
    text = command.strip().lower()

    if not text:
        raise ValueError("Empty command.")

    text = _normalize_1v1_aliases(text)

    try:
        return _parse_draw_known_command(text, game)
    except ValueError:
        pass

    try:
        return _parse_play_from_hand_command(text, game)
    except ValueError:
        pass

    try:
        return _parse_opponent_command(text, game)
    except ValueError:
        pass

    raise ValueError("Unknown command.")


def _normalize_1v1_aliases(text: str) -> str:
    if text == "x":
        return "p1x"

    if text.startswith("ol") and len(text) == 4:
        return f"p1l{text[2:]}"

    if text.startswith("or") and len(text) == 4:
        return f"p1r{text[2:]}"

    return text


def _parse_draw_known_command(text: str, game: GameState) -> GameMove:
    if not (text.startswith("d") and len(text) == 3):
        raise ValueError("Invalid draw command format.")

    tile = parse_tile(text[1:])

    if tile is None:
        raise ValueError("Invalid draw tile format.")

    return GameMove(
        player=game.main_player,
        move_type=GameMoveType.PLAYER_DRAWS_KNOWN,
        tile=tile
    )


def _parse_play_from_hand_command(text: str, game: GameState) -> GameMove:
    if not text or text[0] not in {"l", "r"}:
        raise ValueError("Invalid play from hand command format.")

    side_char = text[0]
    snake_end = SnakeEnd.LEFT if side_char == "l" else SnakeEnd.RIGHT

    index_text = text[1:]
    if not index_text.isdigit():
        raise ValueError(f"Invalid {snake_end.name.lower()} command index.")

    hand_index = int(index_text)
    if hand_index < 0 or hand_index >= len(game.my_hand):
        raise ValueError(f"Invalid {snake_end.name.lower()} command index.")

    return GameMove(
        player=game.main_player,
        move_type=GameMoveType.PLAYER_PLAYS_FROM_HAND,
        tile=game.my_hand[hand_index],
        snake_end=snake_end,
        hand_index=hand_index,
    )


def _parse_opponent_command(text: str, game: GameState) -> GameMove:
    if not (text.startswith("p") and len(text) >= 3):
        raise ValueError("Invalid opponent command format.")

    if not text[1].isdigit():
        raise ValueError("Player id is missing.")

    player_id = int(text[1])

    if not game.opponent_with_id_exists(player_id):
        raise ValueError("Unknown non-main player id.")

    if len(text) < 3:
        raise ValueError("Missing player action.")

    action = text[2]
    payload = text[3:]

    if action == "x" and payload == "":
        return GameMove(
            player=game.get_opponent_by_id(player_id),
            move_type=GameMoveType.OPPONENT_DRAWS_UNKNOWN,
            tile=UnknownTile(),
        )

    if action in {"l", "r"}:
        tile = parse_tile(payload)
        if tile is None:
            raise ValueError("Invalid player tile format.")

        snake_end = SnakeEnd.LEFT if action == "l" else SnakeEnd.RIGHT

        return GameMove(
            player=game.get_opponent_by_id(player_id),
            move_type=GameMoveType.OPPONENT_PLAYS_KNOWN,
            snake_end=snake_end,
            tile=tile,
        )

    raise ValueError("Unknown command.")
