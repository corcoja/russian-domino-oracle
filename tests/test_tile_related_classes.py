"""
Unit tests for Tile-related classes only: Tile, UnknownTile, and HandTile.
"""

import pytest

from src.game.tile import Tile
from src.game.hand_tile import HandTile
from src.game.unknown_tile import UnknownTile


class TestTileClass:
    """
    Test Tile-only behavior.
    """

    def test_same_tile_both_orientations_equal(self) -> None:
        """
        Test that 2-3 and 3-2 normalize to the same tile.
        """
        tile_a = Tile(2, 3)
        tile_b = Tile(3, 2)

        assert tile_a.get_normalized_tile() == tile_b.get_normalized_tile()

    def test_from_string_accepts_valid_input(self) -> None:
        """
        Test creating a tile from a valid two-digit string.
        """

        assert Tile.from_string("23") == Tile(2, 3)
        assert Tile.from_string(" 45 ") == Tile(4, 5)

    def test_from_string_rejects_invalid_input(self) -> None:
        """
        Test invalid tile strings are rejected.
        """

        assert Tile.from_string("7a") is None
        assert Tile.from_string("99") is None
        assert Tile.from_string("1") is None

    def test_tile_str(self) -> None:
        """
        Test Tile string format.
        """

        assert str(Tile(6, 0)) == "6-0"


class TestUnknownTileClass:
    """
    Test UnknownTile-only behavior.
    """

    def test_unknown_tiles_are_equal(self) -> None:
        """
        Test dataclass equality for unknown tiles.
        """

        assert UnknownTile() == UnknownTile()

    def test_unknown_and_known_tiles_are_not_equal(self) -> None:
        """
        Test dataclass equality for unknown and known tiles.
        """

        assert UnknownTile() != Tile(1, 2)


class TestHandTileClass:
    """
    Test HandTile-only behavior.
    """

    def test_from_value_returns_same_instance_for_hand_tile(self) -> None:
        """
        Test wrapping an existing HandTile returns the same object.
        """

        original = HandTile(Tile(1, 2))
        wrapped = HandTile.from_value(original)
        assert wrapped is original

    def test_from_value_wraps_tile_and_unknown(self) -> None:
        """
        Test wrapping raw Tile and UnknownTile values.
        """

        assert HandTile.from_value(Tile(1, 2)) == HandTile(Tile(1, 2))
        assert HandTile.is_unknown(HandTile.from_value(UnknownTile()))

    def test_known_and_unknown_guards(self) -> None:
        """
        Test is_known and is_unknown helpers.
        """

        known = HandTile(Tile(1, 2))
        unknown = HandTile(UnknownTile())

        assert HandTile.is_known(known)
        assert not HandTile.is_unknown(known)
        assert HandTile.is_unknown(unknown)
        assert not HandTile.is_known(unknown)

    def test_known_value_raises_for_unknown_tile(self) -> None:
        """
        Test known_value rejects unknown tiles.
        """

        with pytest.raises(ValueError):
            HandTile(UnknownTile()).known_value()

    def test_getitem_and_contains_on_known_tile(self) -> None:
        """
        Test index and membership behavior on known tiles.
        """

        hand_tile = HandTile(Tile(2, 5))

        assert hand_tile[0] == 2
        assert hand_tile[1] == 5
        assert 2 in hand_tile
        assert 5 in hand_tile
        assert 3 not in hand_tile

        with pytest.raises(IndexError):
            _ = hand_tile[2]

    def test_oriented_for_left_end(self) -> None:
        """
        Test left-end orientation behavior.
        """

        hand_tile = HandTile(Tile(2, 5))

        same_orientation = hand_tile.oriented_for_left_end(5)
        flipped_orientation = hand_tile.oriented_for_left_end(2)
        no_match = hand_tile.oriented_for_left_end(3)

        assert same_orientation == HandTile(Tile(2, 5))
        assert flipped_orientation == HandTile(Tile(5, 2))
        assert no_match is None

    def test_oriented_for_right_end(self) -> None:
        """
        Test right-end orientation behavior.
        """

        hand_tile = HandTile(Tile(2, 5))

        same_orientation = hand_tile.oriented_for_right_end(2)
        flipped_orientation = hand_tile.oriented_for_right_end(5)
        no_match = hand_tile.oriented_for_right_end(3)

        assert same_orientation == HandTile(Tile(2, 5))
        assert flipped_orientation == HandTile(Tile(5, 2))
        assert no_match is None

    def test_equality_for_reversed_known_tiles(self) -> None:
        """
        Test reversed known tiles compare equal.
        """

        assert HandTile(Tile(2, 3)) == HandTile(Tile(3, 2))

    def test_equality_for_unknown_and_mixed_tiles(self) -> None:
        """
        Test unknown/known equality behavior.
        """

        assert HandTile(UnknownTile()) == HandTile(UnknownTile())
        assert HandTile(Tile(2, 3)) != HandTile(UnknownTile())

    def test_hash_is_consistent_with_reversed_equality(self) -> None:
        """
        Test reversed known tiles collapse in hashed collections.
        """

        tiles = {HandTile(Tile(2, 3)), HandTile(Tile(3, 2))}
        assert len(tiles) == 1
