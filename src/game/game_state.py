from typing import cast

from src.models.tile import Tile
from src.game.game_move import GameMove
from src.game.game_move_type import GameMoveType
from src.models.player import HandTile, Player
from src.game.snake_end import SnakeEnd

__all__ = ["GameState"]

TOTAL_TILES = 28


class GameState:
    """
    Tracks a live domino game state for N players.

    Designed for a game guide where only one player's hand is fully known.
    """

    def __init__(
        self,
        main_player: Player,
        opponents: list[Player],
        snake: list[Tile],
    ):
        if not opponents:
            raise ValueError("At least 1 opponent is required.")

        self.main_player = main_player
        self.opponents = opponents
        self.snake = snake

        if not self.main_player.is_main_player:
            raise ValueError("Main player must be marked as main player.")

        self._validate_players_unique_ids()
        self._validate_player_hands()
        self._validate_stock_size()
        self._validate_snake()
        self._validate_unique_exposed_tiles()

    @property
    def all_players(self) -> list[Player]:
        return [self.main_player, *self.opponents]

    def opponent_with_id_exists(self, opponent_id: int) -> bool:
        return any(opponent.id == opponent_id for opponent in self.opponents)

    def get_opponent_by_id(self, opponent_id: int) -> Player:
        for opponent in self.opponents:
            if opponent.id == opponent_id:
                return opponent
        raise ValueError("Unknown opponent id.")

    @property
    def my_hand(self) -> list[Tile]:
        return cast(list[Tile], self.main_player.hand)

    @property
    def stock_size(self) -> int:
        tiles_in_hands = sum(len(player.hand) for player in self.all_players)
        tiles_in_snake = len(self.snake)
        return TOTAL_TILES - tiles_in_hands - tiles_in_snake

    def apply_move(self, game_move: GameMove) -> None:
        player = game_move.player

        match game_move.move_type:
            case GameMoveType.PLAYER_DRAWS_KNOWN:
                self._validate_decrease_stock()
                player.hand.append(cast(Tile, game_move.tile))
                return

            case GameMoveType.OPPONENT_DRAWS_UNKNOWN:
                self._validate_decrease_stock()
                player.hand.append(game_move.tile)
                return

            case GameMoveType.OPPONENT_PLAYS_KNOWN:
                if not player.hand:
                    raise ValueError("Opponent hand cannot be empty.")
                self._place_tile(cast(Tile, game_move.tile), cast(SnakeEnd, game_move.snake_end))
                player.hand.pop()
                return

            case GameMoveType.PLAYER_PLAYS_FROM_HAND:
                if cast(int, game_move.hand_index) >= len(player.hand):
                    raise ValueError("Invalid hand index.")

                hand_index = cast(int, game_move.hand_index)
                tile = cast(Tile, player.hand.pop(hand_index))

                if tile != game_move.tile:
                    player.hand.insert(hand_index, tile)
                    raise ValueError("Move tile does not match hand tile at hand_index.")

                try:
                    self._place_tile(tile, cast(SnakeEnd, game_move.snake_end))
                except ValueError as exc:
                    player.hand.insert(hand_index, tile)
                    raise ValueError("Invalid move for current snake.") from exc

                return

            case _:
                raise ValueError("Unsupported move type.")

    def _place_tile(self, tile: Tile, side: SnakeEnd) -> None:
        if side == SnakeEnd.LEFT:
            oriented = self._place_on_left(tile)
            self.snake.insert(0, oriented)
            return
        if side == SnakeEnd.RIGHT:
            oriented = self._place_on_right(tile)
            self.snake.append(oriented)
            return
        raise ValueError("Unknown side.")

    def _place_on_left(self, tile: Tile) -> Tile:
        if not self.snake:
            return tile

        left_end = self.snake[0][0]
        if tile[1] == left_end:
            return tile
        if tile[0] == left_end:
            return Tile(tile[1], tile[0])
        raise ValueError("Tile does not match left end.")

    def _place_on_right(self, tile: Tile) -> Tile:
        if not self.snake:
            return tile

        right_end = self.snake[-1][1]
        if tile[0] == right_end:
            return tile
        if tile[1] == right_end:
            return Tile(tile[1], tile[0])
        raise ValueError("Tile does not match right end.")

    def _validate_snake(self) -> None:
        for i in range(len(self.snake) - 1):
            if self.snake[i][1] != self.snake[i + 1][0]:
                raise ValueError("Invalid snake: has non-matching adjacent tiles.")

    def _validate_players_unique_ids(self) -> None:
        player_ids = list(map(lambda player: player.id, self.all_players))
        if len(player_ids) != len(set(player_ids)):
            raise ValueError("Player ids must be unique.")

    def _validate_player_hands(self) -> None:
        if not all(map(self._is_known_tile, self.main_player.hand)):
            raise ValueError("Main player hand must contain only known tiles.")

        if any(player.is_main_player for player in self.opponents):
            raise ValueError("Opponents cannot be marked as main player.")

        if any(map(lambda player: any(map(self._is_known_tile, player.hand)), self.opponents)):
            raise ValueError("Opponent hands must contain only unknown tiles.")

    def _validate_stock_size(self) -> None:
        if self.stock_size < 0:
            raise ValueError("Too many tiles in player hands for a 28-tile set.")

    def _validate_unique_exposed_tiles(self) -> None:
        exposed_tiles: list[Tile] = []

        for player in self.all_players:
            for tile in player.hand:
                if self._is_known_tile(tile):
                    exposed_tiles.append(cast(Tile, tile))

        exposed_tiles.extend(self.snake)

        normalized_tiles = list(map(self._normalize_tile, exposed_tiles))
        if len(normalized_tiles) != len(set(normalized_tiles)):
            raise ValueError("Duplicate exposed tiles found across known hands and snake.")

    def _validate_decrease_stock(self) -> None:
        if self.stock_size <= 0:
            raise ValueError("Stock is empty.")

    def _is_known_tile(self, tile: HandTile) -> bool:
        return isinstance(tile, tuple) and len(tile) == 2

    def _normalize_tile(self, tile: Tile) -> Tile:
        return Tile(min(tile[0], tile[1]), max(tile[0], tile[1]))
