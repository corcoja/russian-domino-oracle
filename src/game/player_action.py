from dataclasses import dataclass

from .game_state import MAIN_PLAYER_ID
from .hand_tile import HandTile
from .player_state import PlayerState
from .player_action_type import PlayerActionType
from .snake_end import SnakeEnd


@dataclass(frozen=True)
class PlayerAction:
    """
    Represents a single player action during game flow.

    Encapsulates all information needed to apply an action to the game state:
    - `player_state`: The PlayerState object performing the action
    - `player_action_type`: Category of action (draw, play known, play from hand, etc.)
    - `snake_end`: Which end of the snake (only for plays)
    - `tile`: The tile being played or drawn (known tile or `UnknownTile` for unknown opponent draws)
    - `hand_index`: Index in hand (only for main player plays)

    Immutable (frozen) to ensure game flow integrity.
    """

    player_state: PlayerState
    player_action_type: PlayerActionType
    tile: HandTile
    snake_end: SnakeEnd | None = None
    hand_index: int | None = None

    def __post_init__(self) -> None:
        match self.player_action_type:
            case PlayerActionType.PLAYER_DRAWS_KNOWN:
                if self.player_state.player.id != MAIN_PLAYER_ID:
                    raise ValueError("PLAYER_DRAWS_KNOWN requires the main player.")
                if HandTile.is_unknown(self.tile):
                    raise ValueError("PLAYER_DRAWS_KNOWN requires a known tile.")
                if self.snake_end is not None or self.hand_index is not None:
                    raise ValueError("PLAYER_DRAWS_KNOWN cannot include snake_end or hand_index.")

            case PlayerActionType.PLAYER_PLAYS_FROM_HAND:
                if self.player_state.player.id != MAIN_PLAYER_ID:
                    raise ValueError("PLAYER_PLAYS_FROM_HAND requires the main player.")
                if self.snake_end is None or self.hand_index is None:
                    raise ValueError("PLAYER_PLAYS_FROM_HAND requires snake_end and hand_index.")
                if not 0 <= self.hand_index < len(self.player_state.hand):
                    raise ValueError("hand_index is out of range for player's hand.")
                if HandTile.is_unknown(self.tile) or self.player_state.hand[self.hand_index] != self.tile:
                    raise ValueError("Tile does not match the player's hand at hand_index.")

            case PlayerActionType.OPPONENT_DRAWS_UNKNOWN:
                if self.player_state.player.id == MAIN_PLAYER_ID:
                    raise ValueError("OPPONENT_DRAWS_UNKNOWN requires a non-main player.")
                if not HandTile.is_unknown(self.tile):
                    raise ValueError("OPPONENT_DRAWS_UNKNOWN requires tile to be UnknownTile.")
                if self.snake_end is not None or self.hand_index is not None:
                    raise ValueError("OPPONENT_DRAWS_UNKNOWN cannot include snake_end or hand_index.")

            case PlayerActionType.OPPONENT_PLAYS_KNOWN:
                if self.player_state.player.id == MAIN_PLAYER_ID:
                    raise ValueError("OPPONENT_PLAYS_KNOWN requires a non-main player.")
                if not HandTile.is_known(self.tile) or self.snake_end is None:
                    raise ValueError("OPPONENT_PLAYS_KNOWN requires known tile and snake_end.")
                if self.hand_index is not None:
                    raise ValueError("OPPONENT_PLAYS_KNOWN cannot include hand_index.")

            case PlayerActionType.OPPONENT_PASSES:
                if self.player_state.player.id == MAIN_PLAYER_ID:
                    raise ValueError("OPPONENT_PASSES requires a non-main player.")
                if not HandTile.is_unknown(self.tile):
                    raise ValueError("OPPONENT_PASSES requires tile to be UnknownTile.")
                if self.snake_end is not None or self.hand_index is not None:
                    raise ValueError("OPPONENT_PASSES cannot include snake_end or hand_index.")
