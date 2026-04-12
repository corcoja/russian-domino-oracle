"""
Unit tests for penalty point calculation.
"""

import pytest

from src.game.hand_tile import HandTile
from src.game.penalty_points import compute_hand_penalty_points
from src.game.tile import Tile
from src.game.unknown_tile import UnknownTile


class TestComputeHandPenaltyPoints:
    """
    Test penalty point calculation rules.
    """

    def test_single_zero_zero_tile_has_special_penalty(self) -> None:
        """
        Test that a single 0-0 tile scores 25 points.
        """

        tiles = [HandTile(Tile(0, 0))]

        assert compute_hand_penalty_points(tiles) == 25

    def test_non_single_zero_zero_tile_has_no_special_penalty(self) -> None:
        """
        Test that a non-single 0-0 tile does not score the special 25 points.
        """

        tiles = [HandTile(Tile(0, 0)), HandTile(Tile(1, 2))]

        assert compute_hand_penalty_points(tiles) == 3

    def test_single_six_six_tile_has_special_penalty(self) -> None:
        """
        Test that a single 6-6 tile scores 50 points.
        """

        tiles = [HandTile(Tile(6, 6))]

        assert compute_hand_penalty_points(tiles) == 50

    def test_non_single_six_six_tile_has_no_special_penalty(self) -> None:
        """
        Test that a non-single 6-6 tile does not score the special 50 points.
        """

        tiles = [HandTile(Tile(6, 6)), HandTile(Tile(1, 2))]

        assert compute_hand_penalty_points(tiles) == 15

    def test_single_non_special_tile_uses_pip_sum(self) -> None:
        """
        Test that a non-special single tile uses the standard pip sum.
        """

        tiles = [HandTile(Tile(2, 5))]

        assert compute_hand_penalty_points(tiles) == 7

    def test_multiple_tiles_use_total_pip_sum(self) -> None:
        """
        Test that multiple tiles sum all pips.
        """

        tiles = [HandTile(Tile(1, 2)), HandTile(Tile(3, 6)), HandTile(Tile(0, 4))]

        assert compute_hand_penalty_points(tiles) == 16

    def test_reversed_tile_orientation_still_matches_special_rule(self) -> None:
        """
        Test that reversed known tiles are normalized before scoring.
        """

        tiles = [HandTile(Tile(6, 0))]

        assert compute_hand_penalty_points(tiles) == 6

    def test_custom_operator_is_used(self) -> None:
        """
        Test that a provided penalty operator overrides the default logic.
        """

        hand_tiles = [HandTile(Tile(1, 2)), HandTile(Tile(3, 4))]

        def operator(tiles: list[HandTile]) -> int:
            assert tiles == hand_tiles
            return 99

        assert compute_hand_penalty_points(hand_tiles, penalty_points_operator=operator) == 99

    def test_unknown_tile_raises_value_error(self) -> None:
        """
        Test that unknown tiles are rejected before scoring.
        """

        tiles = [HandTile(UnknownTile())]

        with pytest.raises(ValueError, match="Cannot compute penalty points with unknown tiles in hand."):
            compute_hand_penalty_points(tiles)
