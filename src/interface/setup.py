from src.game.player import Player
from src.game.hand_tile import HandTile
from src.game.player_state import PlayerState
from src.game.tile import Tile
from src.game.game_state import GameState, MAIN_PLAYER_ID
from src.game.unknown_tile import UnknownTile


def init_game() -> GameState:
    while True:
        print("Initialize current real-life game state")

        while True:
            player_count = read_non_negative_int("Number of players (2-4): ")
            if 2 <= player_count <= 4:
                break
            print("Supported player count is 2 to 4.")

        player_move_order = read_player_move_order(player_count)
        next_player_move = read_next_player_move(player_move_order)

        main_player_hand = read_tile_list("Enter your current hand:")
        snake = read_tile_list("Enter snake tiles from left to right:")

        player_states: list[PlayerState] = [
            PlayerState.with_hand_tiles(
                player=Player(id=MAIN_PLAYER_ID, name="You"),
                hand_tiles=main_player_hand,
            )
        ]

        for player_id in range(1, player_count):
            tile_count = read_non_negative_int(f"Enter hand size for player {player_id}: ")
            player_states.append(
                PlayerState.with_hand_tiles(
                    player=Player(id=player_id, name="Opponent"),
                    hand_tiles=[HandTile.from_value(UnknownTile()) for _ in range(tile_count)],
                )
            )

        try:
            return GameState(
                player_states=player_states,
                snake=snake,
                player_move_order=player_move_order,
                next_player_move=next_player_move,
            )
        except ValueError as exc:
            print(f"Invalid initial game state: {exc}")
            print("Please re-enter the setup values.\n")


def read_non_negative_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            return int(raw)
        print("Please enter a non-negative integer.")


def read_tile_list(prompt: str) -> list[HandTile]:
    print(prompt)
    print("Enter one tile per line in XY format (0-6). Press Enter on an empty line when done.")
    tiles: list[HandTile] = []

    while True:
        raw = input().strip()

        if raw == "":
            return tiles

        tile = Tile.from_string(raw)

        if tile is None:
            print("Invalid tile. Use XY with digits between 0 and 6.")
            continue

        tiles.append(HandTile.from_value(tile))


def read_player_move_order(player_count: int) -> list[int]:
    expected = set(range(player_count))
    default_order = list(range(player_count))

    while True:
        raw = input(
            "Enter player move order as IDs separated by spaces "
            f"({MAIN_PLAYER_ID} is you, IDs must be in range 0..{player_count - 1}. Default is "
            f"\"{' '.join(str(x) for x in default_order)}\"): "
        ).strip()

        if raw == "":
            return default_order

        parts = raw.split()

        if len(parts) != player_count:
            print(f"You must provide exactly {player_count} IDs.")
            continue

        if not all(part.isdigit() for part in parts):
            print("Move order must contain only integer player IDs.")
            continue

        order = [int(part) for part in parts]
        if set(order) != expected:
            print(f"Move order must include each ID from 0 to {player_count - 1} exactly once.")
            continue

        return order


def read_next_player_move(player_move_order: list[int]) -> int:
    while True:
        raw = input(f"Next player to move ID (Default is \"{MAIN_PLAYER_ID}\", i.e., you): ").strip()
        if raw == "":
            return MAIN_PLAYER_ID

        if not raw.isdigit():
            print("Please enter a non-negative integer.")
            continue

        next_player = int(raw)
        if next_player in player_move_order:
            return next_player
        print("Next player must be one of the IDs in the move order.")
