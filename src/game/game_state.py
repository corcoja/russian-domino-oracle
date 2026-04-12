from collections.abc import Iterable

from .hand_tile import HandTile
from .player_state import PlayerState

__all__ = ["GameState", "DuplicateExposedTilesError", "MAIN_PLAYER_ID"]

MAIN_PLAYER_ID = 0
TOTAL_TILES = 28


class DuplicateExposedTilesError(ValueError):
    """
    Raised when the same tile appears more than once across known hands and the snake.
    """


class GameState:
    """
    Tracks a live domino game state for N players.

    Designed for a game guide where only one player's hand is fully known.

    ----------

    **Note**: Internal mutable fields (_player_states, _snake, _player_move_order) are stored as tuples rather than
    lists. This prevents callers from mutating the underlying collections directly after construction; all changes must
    go through the validated property setters, which enforce invariants and roll back on failure.
    """

    def __init__(
        self,
        player_states: list[PlayerState],
        snake: Iterable[HandTile],
        player_move_order: list[int] | None = None,
        next_player_move: int | None = None,
    ):
        if len(player_states) < 2:
            raise ValueError("At least 2 player states are required.")

        self._player_states = tuple(player_states)
        self._snake = tuple(snake)

        default_order = sorted(player_state.player.id for player_state in self._player_states)
        self._player_move_order = tuple(player_move_order) if player_move_order is not None else tuple(default_order)
        self._next_player_move = next_player_move if next_player_move is not None else MAIN_PLAYER_ID

        if not self.player_state_with_id_exists(MAIN_PLAYER_ID):
            raise ValueError("Main player state ID is missing from player states.")

        self._validate_player_state_ids_unique()
        self._validate_player_state_hands()
        self._validate_stock_size()
        self._validate_snake()
        self._validate_exposed_tiles()
        self._validate_player_move_order()
        self._validate_next_player_move()

    # --- Read-only structural properties with validation on update ---

    @property
    def player_states(self) -> tuple[PlayerState, ...]:
        return self._player_states

    @player_states.setter
    def player_states(self, updated_player_states: list[PlayerState]) -> None:
        old_player_states = self._player_states
        self._player_states = tuple(updated_player_states)
        try:
            self._validate_player_state_ids_unique()
            self._validate_player_state_hands()
            self._validate_stock_size()
            self._validate_exposed_tiles()
            self._validate_player_move_order()
            self._validate_next_player_move()
        except (ValueError, DuplicateExposedTilesError):
            self._player_states = old_player_states
            raise

    @property
    def snake(self) -> tuple[HandTile, ...]:
        return self._snake

    @snake.setter
    def snake(self, tiles: Iterable[HandTile]) -> None:
        old = self._snake
        self._snake = tuple(tiles)
        try:
            self._validate_snake()
            self._validate_exposed_tiles()
        except (ValueError, DuplicateExposedTilesError):
            self._snake = old
            raise

    @property
    def next_player_move(self) -> int:
        return self._next_player_move

    @next_player_move.setter
    def next_player_move(self, value: int) -> None:
        if value not in self._player_move_order:
            raise ValueError("next_player_move must be part of player_move_order.")
        self._next_player_move = value

    @property
    def main_player_hand(self) -> tuple[HandTile, ...]:
        return self.main_player_state.hand

    @main_player_hand.setter
    def main_player_hand(self, tiles: Iterable[HandTile]) -> None:
        updated_main_player_state = self.main_player_state.with_hand(tuple(tiles))
        self._replace_player_state(updated_main_player_state)

    @property
    def player_move_order(self) -> tuple[int, ...]:
        return self._player_move_order

    # --- Computed properties ---

    @property
    def main_player_state(self) -> PlayerState:
        return self.get_player_state_by_id(MAIN_PLAYER_ID)

    @property
    def opponent_player_states(self) -> tuple[PlayerState, ...]:
        return tuple(
            player_state for player_state in self._player_states
            if player_state.player.id != MAIN_PLAYER_ID
        )

    @property
    def opponents(self) -> tuple[PlayerState, ...]:
        """Compatibility alias for solver code; use opponent_player_states in new code."""
        return self.opponent_player_states

    @property
    def stock_size(self) -> int:
        tiles_in_hands = sum(len(player_state.hand) for player_state in self._player_states)
        tiles_in_snake = len(self._snake)
        return TOTAL_TILES - tiles_in_hands - tiles_in_snake

    # --- Lookup helpers ---

    def player_state_with_id_exists(self, player_state_id: int) -> bool:
        return any(player_state.player.id == player_state_id for player_state in self._player_states)

    def get_player_state_by_id(self, player_state_id: int) -> PlayerState:
        for player_state in self._player_states:
            if player_state.player.id == player_state_id:
                return player_state
        raise ValueError("Unknown player state ID.")

    def update_player_state_hand(
        self,
        player_state_id: int,
        updated_hand_tiles: Iterable[HandTile]
    ) -> None:
        player_state = self.get_player_state_by_id(player_state_id)
        self._replace_player_state(player_state.with_hand(updated_hand_tiles))

    # --- Internal mutation helpers ---

    def _replace_player_state(self, updated_player_state: PlayerState) -> None:
        updated_player_states = [
            updated_player_state
            if player_state.player.id == updated_player_state.player.id
            else player_state
            for player_state in self._player_states
        ]
        self.player_states = updated_player_states

    # --- Internal validation helpers ---

    def _validate_snake(self) -> None:
        for i in range(len(self._snake) - 1):

            if self._snake[i][1] != self._snake[i + 1][0]:
                raise ValueError("Invalid snake: has non-matching adjacent tiles.")

    def _validate_player_state_ids_unique(self) -> None:
        player_state_ids = [player_state.player.id for player_state in self._player_states]
        if len(player_state_ids) != len(set(player_state_ids)):
            raise ValueError("Player state IDs must be unique.")

    def _validate_player_state_hands(self) -> None:
        if not all(map(HandTile.is_known, self.main_player_state.hand)):
            raise ValueError("Main player hand must contain only known tiles.")

        if any(any(HandTile.is_known(tile) for tile in player_state.hand)
               for player_state in self.opponent_player_states):
            raise ValueError("Opponent player state hands must contain only unknown tiles.")

    def _validate_stock_size(self) -> None:
        if self.stock_size < 0:
            raise ValueError("Too many tiles in player hands for a 28-tile set.")

    def _validate_exposed_tiles(self) -> None:
        exposed_tiles: list[HandTile] = []

        for player_state in self._player_states:
            for tile in player_state.hand:
                if HandTile.is_known(tile):
                    exposed_tiles.append(tile)

        exposed_tiles.extend(self._snake)

        normalized_tiles = [t.get_normalized_tile() for t in exposed_tiles]
        if len(normalized_tiles) != len(set(normalized_tiles)):
            raise DuplicateExposedTilesError("Duplicate exposed tiles found across known hands and snake.")

    def _validate_player_move_order(self) -> None:
        expected = sorted(player_state.player.id for player_state in self._player_states)
        provided = sorted(self._player_move_order)
        if expected != provided:
            raise ValueError("player_move_order must contain each player id exactly once.")

    def _validate_next_player_move(self) -> None:
        if self._next_player_move not in self._player_move_order:
            raise ValueError("next_player_move must be part of player_move_order.")
