from typing import cast

from .player_action import PlayerAction
from .player_action_type import PlayerActionType
from .game_state import GameState
from .hand_tile import HandTile
from .player_state import PlayerState
from .snake_end import SnakeEnd


__all__ = [
    "apply_player_action",
    "advance_to_next_player",
    "main_player_state_has_legal_play",
]


def apply_player_action(game: GameState, player_action: PlayerAction) -> None:
    should_advance_turn = False

    if player_action.player_state.player.id != game.next_player_move:
        raise ValueError("The provided action does not match next_player_move.")

    player_state = game.get_player_state_by_id(player_action.player_state.player.id)

    match player_action.player_action_type:
        case PlayerActionType.PLAYER_DRAWS_KNOWN:
            _validate_stock_not_empty(game)
            game.main_player_hand = [*game.main_player_hand, player_action.tile]

        case PlayerActionType.OPPONENT_DRAWS_UNKNOWN:
            _validate_stock_not_empty(game)
            game.player_states = _player_states_with_updated_hand(
                game.player_states,
                player_state.player.id,
                [*player_state.hand, player_action.tile],
            )

        case PlayerActionType.OPPONENT_PASSES:
            if game.stock_size > 0:
                raise ValueError("A player can only pass when the stock is empty.")
            should_advance_turn = True

        case PlayerActionType.OPPONENT_PLAYS_KNOWN:
            if not player_state.hand:
                raise ValueError("Opponent hand cannot be empty.")
            _place_tile(game, player_action.tile, cast(SnakeEnd, player_action.snake_end))
            game.player_states = _player_states_with_updated_hand(
                game.player_states,
                player_state.player.id,
                player_state.hand[:-1],
            )
            should_advance_turn = True

        case PlayerActionType.PLAYER_PLAYS_FROM_HAND:
            hand_index = cast(int, player_action.hand_index)
            if hand_index >= len(game.main_player_hand):
                raise ValueError("Invalid hand index.")

            tile = game.main_player_hand[hand_index]
            if tile != player_action.tile:
                raise ValueError("Action tile does not match hand tile at hand_index.")

            side = cast(SnakeEnd, player_action.snake_end)

            # Pre-compute oriented tile and new snake before touching any state. If orientation fails it raises here,
            # nothing has been mutated yet.
            if side == SnakeEnd.LEFT:
                oriented = _place_on_left(game.snake, tile)
                new_snake = [oriented, *game.snake]
            else:
                oriented = _place_on_right(game.snake, tile)
                new_snake = [*game.snake, oriented]

            new_hand = [t for i, t in enumerate(game.main_player_hand) if i != hand_index]
            game.main_player_hand = new_hand
            game.snake = new_snake
            should_advance_turn = True

        case _:
            raise ValueError("Unsupported action type.")

    if should_advance_turn:
        advance_to_next_player(game)


def advance_to_next_player(game: GameState) -> int:
    current_index = game.player_move_order.index(game.next_player_move)
    next_index = (current_index + 1) % len(game.player_move_order)
    game.next_player_move = game.player_move_order[next_index]
    return game.next_player_move


def main_player_state_has_legal_play(game: GameState) -> bool:
    for tile in game.main_player_hand:
        if _legal_sides_for_tile(tile, game.snake):
            return True
    return False


def _validate_stock_not_empty(game: GameState) -> None:
    if game.stock_size <= 0:
        raise ValueError("Stock is empty.")


def _player_states_with_updated_hand(
    player_states: tuple[PlayerState, ...],
    player_state_id: int,
    updated_hand_tiles: list[HandTile] | tuple[HandTile, ...],
) -> list[PlayerState]:
    return [
        player_state.with_hand(updated_hand_tiles)
        if player_state.player.id == player_state_id
        else player_state
        for player_state in player_states
    ]


def _place_tile(game: GameState, tile: HandTile, side: SnakeEnd) -> None:
    if side == SnakeEnd.LEFT:
        oriented = _place_on_left(game.snake, tile)
        # assignment triggers the snake setter, which validates and auto-rolls back on failure
        game.snake = [oriented, *game.snake]
        return
    if side == SnakeEnd.RIGHT:
        oriented = _place_on_right(game.snake, tile)
        game.snake = [*game.snake, oriented]
        return
    raise ValueError("Unknown side.")


def _place_on_left(snake: tuple[HandTile, ...] | list[HandTile], tile: HandTile) -> HandTile:
    if not snake:
        return tile

    oriented = tile.oriented_for_left_end(snake[0][0])
    if oriented is None:
        raise ValueError("Tile does not match left end.")
    return oriented


def _place_on_right(snake: tuple[HandTile, ...] | list[HandTile], tile: HandTile) -> HandTile:
    if not snake:
        return tile

    oriented = tile.oriented_for_right_end(snake[-1][1])
    if oriented is None:
        raise ValueError("Tile does not match right end.")
    return oriented


def _legal_sides_for_tile(tile: HandTile, snake: tuple[HandTile, ...] | list[HandTile]) -> list[SnakeEnd]:
    if not snake:
        return [SnakeEnd.LEFT]

    legal_sides: list[SnakeEnd] = []
    left_end = snake[0][0]
    right_end = snake[-1][1]

    if left_end in tile:
        legal_sides.append(SnakeEnd.LEFT)
    if right_end in tile:
        legal_sides.append(SnakeEnd.RIGHT)

    return legal_sides
