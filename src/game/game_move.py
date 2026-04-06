from dataclasses import dataclass

from src.models.player import HandTile, Player
from src.models.unknown_tile import UnknownTile
from src.game.game_move_type import GameMoveType
from src.game.snake_end import SnakeEnd


@dataclass(frozen=True)
class GameMove:
    """
    Represents a single player action during game flow.

    Encapsulates all information needed to apply a move to the game state:
    - ``player``: The Player object performing the action
    - ``move_type``: Category of action (draw, play known, play from hand, etc.)
    - ``snake_end``: Which end of the snake (only for plays)
    - ``tile``: The tile being played or drawn (known tile or ``UnknownTile`` for unknown opponent draws)
    - ``hand_index``: Index in hand (only for main player plays)

    Immutable (frozen) to ensure game flow integrity.
    """

    player: Player
    move_type: GameMoveType
    tile: HandTile
    snake_end: SnakeEnd | None = None
    hand_index: int | None = None

    def __post_init__(self) -> None:
        match self.move_type:
            case GameMoveType.PLAYER_DRAWS_KNOWN:
                if not self.player.is_main_player:
                    raise ValueError("PLAYER_DRAWS_KNOWN requires the main player.")
                if isinstance(self.tile, UnknownTile):
                    raise ValueError("PLAYER_DRAWS_KNOWN requires a known tile.")
                if self.snake_end is not None or self.hand_index is not None:
                    raise ValueError("PLAYER_DRAWS_KNOWN cannot include snake_end or hand_index.")

            case GameMoveType.PLAYER_PLAYS_FROM_HAND:
                if not self.player.is_main_player:
                    raise ValueError("PLAYER_PLAYS_FROM_HAND requires the main player.")
                if self.snake_end is None or self.hand_index is None:
                    raise ValueError("PLAYER_PLAYS_FROM_HAND requires snake_end and hand_index.")
                if not 0 <= self.hand_index < len(self.player.hand):
                    raise ValueError("hand_index is out of range for player's hand.")
                if isinstance(self.tile, UnknownTile) or self.player.hand[self.hand_index] != self.tile:
                    raise ValueError("tile does not match the player's hand at hand_index.")

            case GameMoveType.OPPONENT_DRAWS_UNKNOWN:
                if self.player.is_main_player:
                    raise ValueError("OPPONENT_DRAWS_UNKNOWN requires a non-main player.")
                if not isinstance(self.tile, UnknownTile):
                    raise ValueError("OPPONENT_DRAWS_UNKNOWN requires tile to be UnknownTile.")
                if self.snake_end is not None or self.hand_index is not None:
                    raise ValueError("OPPONENT_DRAWS_UNKNOWN cannot include snake_end or hand_index.")

            case GameMoveType.OPPONENT_PLAYS_KNOWN:
                if self.player.is_main_player:
                    raise ValueError("OPPONENT_PLAYS_KNOWN requires a non-main player.")
                if isinstance(self.tile, UnknownTile) or self.snake_end is None:
                    raise ValueError("OPPONENT_PLAYS_KNOWN requires known tile and snake_end.")
                if self.hand_index is not None:
                    raise ValueError("OPPONENT_PLAYS_KNOWN cannot include hand_index.")
