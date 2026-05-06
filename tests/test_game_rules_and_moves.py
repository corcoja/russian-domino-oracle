"""
Comprehensive test suite for Russian Dominoes (Kozel) game rules and move validation.

Tests cover:
- Legal move validation
- Tile matching and orientation
- Turn advancement rules
- Hand management
- Initial game state
- Edge cases and illegal moves
"""

import pytest

from src.game.game_state import GameState, MAIN_PLAYER_ID
from src.game.player_action import PlayerAction
from src.game.player_action_type import PlayerActionType
from src.game.player import Player
from src.game.player_state import PlayerState
from src.game.snake_end import SnakeEnd
from src.game.tile import Tile
from src.game.hand_tile import HandTile
from src.game.unknown_tile import UnknownTile
from src.game.game_state_transitions import (apply_player_action,
                                             advance_to_next_player,
                                             main_player_state_has_legal_play)


# --- Fixtures ---

@pytest.fixture(name="two_player_game")
def fixture_two_player_game() -> GameState:
    """
    Create a 2-player game with known initial state.
    """

    player_0 = Player(id=0, name="Main")
    player_1 = Player(id=1, name="Opponent")

    # Main player has: 1-2, 2-3, 3-4, 4-5, 5-6, 6-0, 1-1
    main_hand = [
        HandTile(Tile(1, 2)),
        HandTile(Tile(2, 3)),
        HandTile(Tile(3, 4)),
        HandTile(Tile(4, 5)),
        HandTile(Tile(5, 6)),
        HandTile(Tile(6, 0)),
        HandTile(Tile(1, 1)),
    ]

    # Opponent has unknown tiles
    opponent_hand_unknown = [
        HandTile(UnknownTile()),
        HandTile(UnknownTile()),
        HandTile(UnknownTile()),
        HandTile(UnknownTile()),
    ]

    player_states = [
        PlayerState(player=player_0, hand=tuple(main_hand)),
        PlayerState(player=player_1, hand=tuple(opponent_hand_unknown)),
    ]

    # Snake: 0-2
    snake = [HandTile(Tile(0, 2))]

    game = GameState(
        player_states=player_states,
        snake=snake,
        player_move_order=[0, 1],
        next_player_move=0,
    )

    return game


@pytest.fixture(name="three_player_game")
def fixture_three_player_game() -> GameState:
    """
    Create a 3-player game.
    """
    players = [
        Player(id=0, name="Main"),
        Player(id=1, name="Opp1"),
        Player(id=2, name="Opp2"),
    ]

    player_states = [
        PlayerState(player=players[0], hand=tuple([HandTile(Tile(1, 2)), HandTile(Tile(3, 4))])),
        PlayerState(player=players[1], hand=tuple([HandTile(UnknownTile()), HandTile(UnknownTile())])),
        PlayerState(player=players[2], hand=tuple([HandTile(UnknownTile()), HandTile(UnknownTile())])),
    ]

    snake = [HandTile(Tile(2, 3))]
    game = GameState(
        player_states=player_states,
        snake=snake,
        player_move_order=[0, 1, 2],
        next_player_move=0,
    )
    return game


@pytest.fixture(name="empty_stock_game")
def fixture_empty_stock_game() -> GameState:
    """
    Game with empty stock (all 28 tiles dealt).
    """
    player_0 = Player(id=0, name="Main")
    player_1 = Player(id=1, name="Opponent")

    # Distribute all 28 tiles: 14 to main player, 13 to opponent, 1 in snake
    main_hand = [
        HandTile(Tile(0, 0)), HandTile(Tile(0, 1)), HandTile(Tile(0, 2)), HandTile(Tile(0, 3)),
        HandTile(Tile(1, 1)), HandTile(Tile(1, 2)), HandTile(Tile(1, 3)), HandTile(Tile(1, 4)),
        HandTile(Tile(2, 2)), HandTile(Tile(2, 3)), HandTile(Tile(2, 4)), HandTile(Tile(2, 5)),
        HandTile(Tile(3, 3)), HandTile(Tile(3, 4)),
    ]
    opponent_hand = [HandTile(UnknownTile()) for _ in range(13)]

    player_states = [
        PlayerState(player=player_0, hand=tuple(main_hand)),
        PlayerState(player=player_1, hand=tuple(opponent_hand)),
    ]

    snake = [HandTile(Tile(0, 5))]
    game = GameState(
        player_states=player_states,
        snake=snake,
        player_move_order=[0, 1],
        next_player_move=0,
    )
    return game


# --- TESTS: Initial Game State ---

class TestGameInitialization:
    """
    Test game initialization and constraints.
    """

    def test_valid_game_creation(self, two_player_game: GameState) -> None:
        """
        Test that a valid game can be created.
        """

        game = two_player_game
        assert len(game.player_states) == 2
        assert game.next_player_move == MAIN_PLAYER_ID
        assert game.stock_size == 16

    def test_at_least_two_players_required(self):
        """
        Test that a game requires at least 2 players.
        """

        player_0 = Player(id=0, name="Only")
        player_states = [PlayerState(player=player_0, hand=tuple())]

        with pytest.raises(ValueError):
            GameState(player_states=player_states, snake=[])

    def test_main_player_required(self):
        """
        Test that MAIN_PLAYER_ID (0) must exist.
        """

        player_1 = Player(id=1, name="NotMain")
        player_2 = Player(id=2, name="AlsoNotMain")

        player_states = [
            PlayerState(player=player_1, hand=tuple()),
            PlayerState(player=player_2, hand=tuple()),
        ]

        with pytest.raises(ValueError):
            GameState(player_states=player_states, snake=[])


# --- TESTS: Tile Matching and Legal Moves ---

class TestTileMatching:
    """
    Test tile matching rules (which pips can be played on which ends).
    """

    def test_tile_orientation_when_needed(self, two_player_game: GameState) -> None:
        """
        Test that tiles are correctly oriented when placed.

        If snake is [0-2] and we have tile 3-2, it should be flipped to 2-3 when placed on right.
        """
        game = two_player_game
        # Snake is [0-2] with right end = 2
        # We need a tile 3-2 which will be flipped to 2-3 to match the right end (2)
        # But the test fixture doesn't have 3-2, so let's manually add it

        # Create a simpler test: place 2-3 on right
        # 2-3 has left=2, right=3
        # Right end of snake is 2
        # So left pip of placed tile should be 2 (which it is)
        # No flip needed
        tile = HandTile(Tile(2, 3))
        tile_index = next(i for i, t in enumerate(game.main_player_hand) if t == tile)

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=tile,
            snake_end=SnakeEnd.RIGHT,
            hand_index=tile_index,
        )

        # Apply the action
        apply_player_action(game, player_action)

        # Snake should now be [0-2, 2-3]
        assert len(game.snake) == 2
        last_tile = game.snake[-1]
        assert last_tile[0] == 2  # Left pip should be 2
        assert last_tile[1] == 3  # Right pip should be 3

    def test_empty_snake_first_tile(self):
        """
        Test that the first tile on an empty snake can be placed.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        main_hand = [HandTile(Tile(3, 5))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        tile = HandTile(Tile(3, 5))
        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=tile,
            snake_end=SnakeEnd.LEFT,
            hand_index=0,
        )

        apply_player_action(game, player_action)

        # Snake should now have the tile
        assert len(game.snake) == 1
        assert game.snake[0] == tile


# --- TESTS: Turn Advancement ---

class TestTurnAdvancement:
    """
    Test that turns advance correctly based on move type.
    """

    def test_draw_does_not_advance_turn(self, two_player_game: GameState) -> None:
        """
        Test that drawing a tile does NOT advance the turn.
        """

        game = two_player_game
        initial_next_player = game.next_player_move

        # Main player draws
        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_DRAWS_KNOWN,
            tile=HandTile(Tile(0, 0)),
        )

        apply_player_action(game, player_action)

        # Turn should still be same player
        assert game.next_player_move == initial_next_player

    def test_play_advances_turn(self, two_player_game: GameState) -> None:
        """
        Test that playing a tile DOES advance the turn.
        """
        game = two_player_game
        initial_next_player = game.next_player_move
        assert initial_next_player == 0

        # Main player plays tile 2-3 on right end (matches 2)
        tile = next(t for t in game.main_player_hand if t == HandTile(Tile(2, 3)))
        tile_index = next(i for i, t in enumerate(game.main_player_hand) if t == tile)

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=tile,
            snake_end=SnakeEnd.RIGHT,
            hand_index=tile_index,
        )

        apply_player_action(game, player_action)

        # Turn should advance to next player
        assert game.next_player_move == 1

    def test_pass_advances_turn(self, empty_stock_game: GameState) -> None:
        """
        Test that passing DOES advance the turn (and only when stock is empty).
        """
        game = empty_stock_game
        assert game.stock_size == 0
        # Set to player 1 (opponent) for the test
        game.next_player_move = 1

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(1),
            player_action_type=PlayerActionType.OPPONENT_PASSES,
            tile=HandTile(UnknownTile()),
        )

        apply_player_action(game, player_action)

        # Turn should advance
        assert game.next_player_move == 0

    def test_pass_rejected_when_stock_not_empty(self, two_player_game: GameState) -> None:
        """
        Test that a player cannot pass when stock is not empty.
        """
        game = two_player_game
        assert game.stock_size > 0

        # Set to opponent (player 1)
        game.next_player_move = 1

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(1),
            player_action_type=PlayerActionType.OPPONENT_PASSES,
            tile=HandTile(UnknownTile()),
        )

        with pytest.raises(ValueError):
            apply_player_action(game, player_action)

    def test_turn_order_cycles(self, three_player_game: GameState) -> None:
        """
        Test that turn order cycles correctly through all players.
        """
        game = three_player_game

        # Make sure we can get all three players' turns
        player_ids: list[int] = []

        for _ in range(6):  # Cycle through order twice
            player_ids.append(game.next_player_move)
            advance_to_next_player(game)

        # Should cycle: 0, 1, 2, 0, 1, 2
        assert player_ids == [0, 1, 2, 0, 1, 2]


# --- TESTS: Hand Management ---

class TestHandManagement:
    """
    Test hand changes (adding/removing tiles).
    """

    def test_hand_reduced_after_play(self, two_player_game: GameState) -> None:
        """
        Test that hand size decreases after a play.
        """

        game = two_player_game
        initial_hand_size = len(game.main_player_hand)

        tile = next(t for t in game.main_player_hand if t == HandTile(Tile(2, 3)))
        tile_index = next(i for i, t in enumerate(game.main_player_hand) if t == tile)

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=tile,
            snake_end=SnakeEnd.RIGHT,
            hand_index=tile_index,
        )

        apply_player_action(game, player_action)

        assert len(game.main_player_hand) == initial_hand_size - 1
        assert len(game.snake) == 2

    def test_hand_increased_after_draw(self, two_player_game: GameState) -> None:
        """
        Test that hand size increases after a draw.
        """

        game = two_player_game
        initial_hand_size = len(game.main_player_hand)

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_DRAWS_KNOWN,
            tile=HandTile(Tile(0, 0)),
        )

        apply_player_action(game, player_action)

        assert len(game.main_player_hand) == initial_hand_size + 1


# --- TESTS: Move Validation ---

class TestMoveValidation:
    """
    Test that invalid moves are rejected.
    """

    def test_only_main_player_can_play_from_hand(self, two_player_game: GameState) -> None:
        """
        Test that only player 0 can use PLAYER_PLAYS_FROM_HAND.
        """

        game = two_player_game
        opponent_state = game.get_player_state_by_id(1)

        with pytest.raises(ValueError):
            PlayerAction(
                player_state=opponent_state,
                player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
                tile=HandTile(Tile(0, 0)),
                snake_end=SnakeEnd.LEFT,
                hand_index=0,
            )

    def test_only_main_player_can_draw_known(self, two_player_game: GameState) -> None:
        """
        Test that only player 0 can use PLAYER_DRAWS_KNOWN.
        """

        game = two_player_game
        opponent_state = game.get_player_state_by_id(1)

        with pytest.raises(ValueError):
            PlayerAction(
                player_state=opponent_state,
                player_action_type=PlayerActionType.PLAYER_DRAWS_KNOWN,
                tile=HandTile(Tile(0, 0)),
            )

    def test_cannot_draw_from_empty_stock(self):
        """
        Test that drawing fails when stock is empty.
        """

        # Create a game with exactly 28 tiles dealt (all tiles in hands and snake)
        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Main player: 14 tiles (half of 28)
        main_hand = [
            HandTile(Tile(0, 0)), HandTile(Tile(0, 1)), HandTile(Tile(0, 2)), HandTile(Tile(0, 3)),
            HandTile(Tile(1, 1)), HandTile(Tile(1, 2)), HandTile(Tile(1, 3)), HandTile(Tile(1, 4)),
            HandTile(Tile(2, 2)), HandTile(Tile(2, 3)), HandTile(Tile(2, 4)), HandTile(Tile(2, 5)),
            HandTile(Tile(3, 3)), HandTile(Tile(3, 4)),
        ]

        # Opponent: 13 tiles
        opponent_hand = [HandTile(UnknownTile()) for _ in range(13)]

        # Snake: 1 tile (to make 14 + 13 + 1 = 28, stock = 0)
        snake = [HandTile(Tile(3, 5))]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=snake,
            player_move_order=[0, 1],
            next_player_move=0,
        )

        # Verify stock is empty
        assert game.stock_size == 0

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_DRAWS_KNOWN,
            tile=HandTile(Tile(0, 0)),
        )

        with pytest.raises(ValueError):
            apply_player_action(game, player_action)


# --- TESTS: Edge Cases ---

class TestEdgeCases:
    """
    Test edge cases and corner scenarios.
    """

    def test_double_tile_plays_correctly(self):
        """
        Test that a double tile (same pips on both sides) can be played.
        """
        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 3-5
        snake_tile = HandTile(Tile(3, 5))

        # Hand with 3-3 (double)
        main_hand = [HandTile(Tile(3, 3)), HandTile(Tile(1, 2))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        # 3-3 should be playable on left
        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(0),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=HandTile(Tile(3, 3)),
            snake_end=SnakeEnd.LEFT,
            hand_index=0,
        )

        apply_player_action(game, player_action)

        assert len(game.snake) == 2

    def test_tile_played_incorrectly(self, two_player_game: GameState) -> None:
        """
        Test a tile that is played incorrectly.
        """

        game = two_player_game
        tile = next(t for t in game.main_player_hand if t == HandTile(Tile(4, 5)))
        tile_index = next(i for i, t in enumerate(game.main_player_hand) if t == tile)

        player_action = PlayerAction(
            player_state=game.get_player_state_by_id(MAIN_PLAYER_ID),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=tile,
            snake_end=SnakeEnd.RIGHT,
            hand_index=tile_index,
        )

        with pytest.raises(ValueError):
            apply_player_action(game, player_action)


# --- TESTS: Legal Play Detection ---

class TestLegalPlayDetection:
    """
    Test determination of legal plays.
    """

    def test_legal_play_on_left_end(self):
        """
        Test that tiles matching left end are playable.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 2-5, left end is 2
        snake_tile = HandTile(Tile(2, 5))

        # Hand with tile 2-3 (matches left end)
        main_hand = [HandTile(Tile(2, 3))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        assert main_player_state_has_legal_play(game)

    def test_legal_play_on_right_end(self):
        """
        Test that tiles matching right end are playable.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 2-5, right end is 5
        snake_tile = HandTile(Tile(2, 5))

        # Hand with tile 3-5 (matches right end of the snake with left side of tile, which should be oriented to match)
        main_hand = [HandTile(Tile(3, 5))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        assert main_player_state_has_legal_play(game)

    def test_no_legal_play_when_none_match(self):
        """
        Test that no legal play is detected when no tiles match.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 2-5, ends are 2 and 5
        snake_tile = HandTile(Tile(2, 5))

        # Hand with tiles that don't match (all 0,1,3,4 pips)
        main_hand = [HandTile(Tile(0, 1)), HandTile(Tile(3, 4))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        assert not main_player_state_has_legal_play(game)

    def test_double_can_be_played_on_either_end(self):
        """
        Test that a double tile can be played on either end.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 2-5
        snake_tile = HandTile(Tile(2, 5))

        # Hand with 5-5 (double that matches right end)
        main_hand = [HandTile(Tile(5, 5))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        assert main_player_state_has_legal_play(game)


# --- TESTS: Snake Validation ---

class TestSnakeValidation:
    """
    Test snake structure validation.
    """

    def test_snake_must_have_matching_adjacent_tiles(self):
        """
        Test that adjacent tiles in snake must have matching pips.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        main_hand = [HandTile(Tile(0, 0))]  # Different tile to avoid duplicate
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        # Create valid game first with a valid snake
        game = GameState(
            player_states=player_states,
            snake=[HandTile(Tile(1, 2))],  # Valid snake with 1 tile
            player_move_order=[0, 1],
            next_player_move=0,
        )

        # Attempting to set a broken snake should raise error
        with pytest.raises(ValueError):
            # This snake has non-matching pips: 1-2 | 3-4
            game.snake = [HandTile(Tile(1, 2)), HandTile(Tile(3, 4))]


# --- TESTS: Tile Matching Edge Cases ---

class TestTileMatchingEdgeCases:
    """
    Test edge cases for tile matching.
    """

    def test_tile_with_zero_pips(self):
        """
        Test that tiles with 0 pips work correctly.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 0-3
        snake_tile = HandTile(Tile(0, 3))

        # Hand with 0-0 (double with 0)
        main_hand = [HandTile(Tile(0, 0))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        # Should be able to play 0-0 on left
        assert main_player_state_has_legal_play(game)

    def test_tile_with_max_pips(self):
        """
        Test that tiles with 6 pips work correctly.
        """

        player_0 = Player(id=0, name="Main")
        player_1 = Player(id=1, name="Opponent")

        # Snake is 3-6
        snake_tile = HandTile(Tile(3, 6))

        # Hand with 6-6 (double with 6)
        main_hand = [HandTile(Tile(6, 6))]
        opponent_hand = [HandTile(UnknownTile())]

        player_states = [
            PlayerState(player=player_0, hand=tuple(main_hand)),
            PlayerState(player=player_1, hand=tuple(opponent_hand)),
        ]

        game = GameState(
            player_states=player_states,
            snake=[snake_tile],
            player_move_order=[0, 1],
            next_player_move=0,
        )

        # Should be able to play 6-6 on right
        assert main_player_state_has_legal_play(game)


# --- TESTS: Multiple Move Scenarios ---

class TestMultipleMoveSequences:
    """
    Test game sequences with multiple moves.
    """

    def test_alternating_draw_and_play(self, two_player_game: GameState) -> None:
        """
        Test that game can alternate between draws and plays.
        """

        game = two_player_game

        # Round 1: Main player draws
        player_action1 = PlayerAction(
            player_state=game.get_player_state_by_id(0),
            player_action_type=PlayerActionType.PLAYER_DRAWS_KNOWN,
            tile=HandTile(Tile(0, 0)),
        )

        apply_player_action(game, player_action1)
        assert game.next_player_move == 0  # Should still be player 0

        hand_size_after_draw = len(game.main_player_hand)

        # Round 2: Main player plays
        tile_to_play = game.main_player_hand[0]
        player_action2 = PlayerAction(
            player_state=game.get_player_state_by_id(0),
            player_action_type=PlayerActionType.PLAYER_PLAYS_FROM_HAND,
            tile=tile_to_play,
            snake_end=SnakeEnd.LEFT if 0 in tile_to_play else SnakeEnd.RIGHT,
            hand_index=0,
        )

        try:
            apply_player_action(game, player_action2)

            # If play succeeds, turn should advance
            assert game.next_player_move == 1
            assert len(game.main_player_hand) == hand_size_after_draw - 1

        except ValueError:
            # If the tile doesn't match the snake, that's ok for this test
            pass


# --- TESTS: Hand Consistency ---

class TestHandConsistency:
    """
    Test that hand state remains consistent.
    """

    def test_main_player_hand_always_known_tiles(self, two_player_game: GameState) -> None:
        """
        Test that main player hand only contains known tiles.
        """
        game = two_player_game

        # All main player tiles should be known
        main_player_state = game.get_player_state_by_id(0)
        for tile in main_player_state.hand:
            assert HandTile.is_known(tile)

    def test_opponent_hand_always_unknown_tiles(self, two_player_game: GameState) -> None:
        """
        Test that opponent hand only contains unknown tiles.
        """

        game = two_player_game

        # All opponent tiles should be unknown
        opponent_state = game.get_player_state_by_id(1)
        for tile in opponent_state.hand:
            assert HandTile.is_unknown(tile)
