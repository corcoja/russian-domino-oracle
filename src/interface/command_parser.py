from dataclasses import dataclass
from enum import Enum

from src.game.game_state import GameState, MAIN_PLAYER_ID
from src.game.hand_tile import HandTile
from src.game.tile import Tile
from src.game.unknown_tile import UnknownTile
from src.game.player_action import PlayerAction
from src.game.player_action_type import PlayerActionType
from src.game.snake_end import SnakeEnd


class ParsedCommandType(str, Enum):
    QUIT = "quit"
    HELP = "help"
    SHOW = "show"
    END_GAME = "end_game"
    PLAYER_ACTION = "player_action"


@dataclass(frozen=True)
class ParsedCommand:
    command_type: ParsedCommandType
    player_action: PlayerAction | None = None


def parse_command(command: str, game: GameState) -> ParsedCommand:
    text = command.strip().lower()

    match text:
        case "quit":
            return ParsedCommand(command_type=ParsedCommandType.QUIT)
        case "help":
            return ParsedCommand(command_type=ParsedCommandType.HELP)
        case "show":
            return ParsedCommand(command_type=ParsedCommandType.SHOW)
        case "end":
            return ParsedCommand(command_type=ParsedCommandType.END_GAME)
        case _:
            return ParsedCommand(command_type=ParsedCommandType.PLAYER_ACTION,
                                 player_action=parse_player_action(text, game))


def parse_player_action(command: str, game: GameState) -> PlayerAction:
    text = command.strip().lower()

    if not text:
        raise ValueError("Empty command.")

    if game.next_player_move == MAIN_PLAYER_ID:
        return _parse_main_player_action(text, game)

    return _parse_opponent_turn_action(text, game)


def _parse_main_player_action(text: str, game: GameState) -> PlayerAction:
    try:
        return _parse_main_player_draw_command(text, game)
    except ValueError:
        pass

    try:
        return _parse_main_player_play_command(text, game)
    except ValueError:
        pass

    raise ValueError("It is your turn. Use dXY, lXY, or rXY.")


def _parse_opponent_turn_action(text: str, game: GameState) -> PlayerAction:
    try:
        parsed = _parse_current_opponent_action(text, game)
    except ValueError as exc:
        raise ValueError(f"It is player {game.next_player_move}'s turn. Use d, lXY, rXY, or p.") from exc

    return parsed


def _parse_main_player_draw_command(text: str, game: GameState) -> PlayerAction:
    if not (text.startswith("d") and len(text) == 3):
        raise ValueError("Invalid draw command format.")

    tile = Tile.from_string(text[1:])

    if tile is None:
        raise ValueError("Invalid draw tile format.")

    return PlayerAction(
        player_state=game.main_player_state,
        player_action_type=PlayerActionType.PLAYER_DRAWS_KNOWN,
        tile=HandTile.from_value(tile)
    )


def _parse_main_player_play_command(text: str, game: GameState) -> PlayerAction:
    if not text or text[0] not in {"l", "r"}:
        raise ValueError("Invalid play command format.")

    side_char = text[0]
    snake_end = SnakeEnd.LEFT if side_char == "l" else SnakeEnd.RIGHT

    tile_text = text[1:]
    parsed_tile = Tile.from_string(tile_text)
    if parsed_tile is None:
        raise ValueError(f"Invalid {snake_end.name.lower()} command tile.")
    tile = HandTile.from_value(parsed_tile)

    hand_index = _find_matching_hand_index(game.main_player_hand, tile)
    if hand_index is None:
        raise ValueError("You do not have that tile in hand.")
    hand_tile = game.main_player_hand[hand_index]

    return PlayerAction(
        player_state=game.main_player_state,
        player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
        tile=HandTile.from_value(hand_tile),
        snake_end=snake_end,
        hand_index=hand_index,
    )


def _find_matching_hand_index(hand: tuple[HandTile, ...] | list[HandTile], target: HandTile) -> int | None:
    normalized_target = target.get_normalized_tile()
    for index, hand_tile in enumerate(hand):
        if hand_tile.get_normalized_tile() == normalized_target:
            return index
    return None


def _parse_current_opponent_action(text: str, game: GameState) -> PlayerAction:
    player_state = game.get_player_state_by_id(game.next_player_move)

    if text == "d":
        return PlayerAction(
            player_state=player_state,
            player_action_type=PlayerActionType.OPPONENT_DRAWS_UNKNOWN,
            tile=HandTile.from_value(UnknownTile()),
        )

    if text == "p":
        return PlayerAction(
            player_state=player_state,
            player_action_type=PlayerActionType.OPPONENT_PASSES,
            tile=HandTile.from_value(UnknownTile()),
        )

    if text.startswith("l") or text.startswith("r"):
        if len(text) != 3:
            raise ValueError("Invalid opponent play command format.")

        side_char = text[0]
        tile = Tile.from_string(text[1:])
        if tile is None:
            raise ValueError("Invalid player tile format.")

        snake_end = SnakeEnd.LEFT if side_char == "l" else SnakeEnd.RIGHT

        return PlayerAction(
            player_state=player_state,
            player_action_type=PlayerActionType.OPPONENT_PLAYS_KNOWN,
            snake_end=snake_end,
            tile=HandTile.from_value(tile),
        )

    raise ValueError("Unknown command.")
