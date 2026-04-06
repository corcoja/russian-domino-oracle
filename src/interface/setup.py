from typing import cast

from src.models.tile import parse_tile, Tile
from src.game.game_state import GameState
from src.models.player import Player, HandTile
from src.models.unknown_tile import UnknownTile


def read_non_negative_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            return int(raw)
        print("Please enter a non-negative integer.")


def read_tile_list(prompt: str) -> list[Tile]:
    print(prompt)
    print("Enter one tile per line in XY format (0-6). Enter '-' when done.")
    tiles: list[Tile] = []

    while True:
        raw = input().strip()

        if raw == "-":
            return tiles

        tile = parse_tile(raw)

        if tile is None:
            print("Invalid tile. Use XY with digits between 0 and 6.")
            continue

        tiles.append(tile)


def init_game() -> GameState:
    while True:
        print("Initialize current real-life game state")

        while True:
            player_count = read_non_negative_int("Number of players (2-4): ")
            if 2 <= player_count <= 4:
                break
            print("Supported player count is 2 to 4.")

        my_hand = read_tile_list("Enter your current hand:")
        snake = read_tile_list("Enter snake tiles from left to right:")

        main_player = Player(id=0, is_main_player=True, hand=cast(list[HandTile], my_hand))
        opponents: list[Player] = []

        for player_id in range(1, player_count):
            tile_count = read_non_negative_int(f"Enter hand size for player {player_id}: ")
            opponents.append(
                Player(
                    id=player_id,
                    is_main_player=False,
                    hand=[UnknownTile() for _ in range(tile_count)],
                )
            )

        try:
            return GameState(
                main_player=main_player,
                opponents=opponents,
                snake=snake,
            )
        except ValueError as exc:
            print(f"Invalid initial game state: {exc}")
            print("Please re-enter the setup values.\n")
