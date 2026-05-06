from enum import Enum


class PlayerActionType(str, Enum):
    """
    Categorizes player actions during the game flow.

    These types distinguish how a player action is performed:
    - PLAYER_DRAWS_KNOWN: Main player draws and reveals a known tile from stock
    - PLAYER_PLAYS_FROM_HAND: Main player plays from their hand by index
    - OPPONENT_DRAWS_UNKNOWN: Opponent draws an unseen tile from stock
    - OPPONENT_PLAYS_KNOWN: Opponent plays a known tile on a specific snake end
    - OPPONENT_PASSES: Opponent passes without playing or drawing
    """

    PLAYER_DRAWS_KNOWN = "player_draws_known"
    PLAYER_PLAYS_FROM_HAND = "player_plays_from_hand"
    OPPONENT_DRAWS_UNKNOWN = "opponent_draws_unknown"
    OPPONENT_PLAYS_KNOWN = "opponent_plays_known"
    OPPONENT_PASSES = "opponent_passes"
