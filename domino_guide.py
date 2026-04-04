from typing import Tuple, cast
from game import Game

START_GAME_TEXT = "Game started!!!"


def print_commands() -> None:
    print(
        "Please enter a command:\n"
        "    dXY  : Draw from the stock a domino with X and Y numbers.\n"
        "    lX   : Put on the left side of the snake the domino at index X in your hand.\n"
        "    rX   : Put on the right side of the snake the domino at index X in your hand.\n"
        "    olXY : Oppenent puts on the left side of the snake a domino with X and Y numbers.\n"
        "    orXY : Oppenent puts on the right side of the snake a domino with X and Y numbers.\n"
        "    x    : Oppenent draws from a domino from the stock.\n"
    )


def init_game() -> Game:
    my_hand: list[Tuple[int, int]] = []
    snake: list[Tuple[int, int]] = []
    stock_size = 0
    opponent_hand_size = 0

    print("On each line, enter the pieces in your hand in XY format. To stop, enter \"-\":")

    while (text := input()) != "-":
        if (piece := parse_piece(text)):
            my_hand.append(piece)
        else:
            print("Invalid piece numbers! Try again!")

    print("On each line, enter the pieces in the snake, from left to right in XY format. To stop, enter \"-\":")

    while (text := input()) != "-":
        try:
            piece = parse_piece(text)

            if not piece:
                raise ValueError()

            if not snake or snake[-1][1] == piece[0]:
                snake.append(piece)
            elif snake[-1][1] == piece[1]:
                snake.append(cast(Tuple[int, int], piece[::-1]))
            else:
                raise ValueError()

            print(snake)
        except ValueError:
            print("Invalid piece numbers! Try again!")

    while True:
        text = input("Enter stock size: ")
        if not text.isnumeric():
            print("Incorrect stock size! Try again!")
            continue
        stock_size = int(text)
        break

    while True:
        text = input("Enter opponent hand size: ")
        if not text.isnumeric():
            print("Incorrect opponent hand size! Try again!")
            continue
        opponent_hand_size = int(text)
        break

    return Game(snake, my_hand, opponent_hand_size, stock_size)


def read_execute_command(game: Game, command: str) -> None:

    match list(command):
        case ["d", *piece_text] if (piece := parse_piece("".join(piece_text))):
            game.me_draw_from_stock(piece)
        case ["l", *index_list] if (index_text := "".join(index_list)) and index_text.isnumeric() and 0 <= (index := int(index_text)) < len(game.my_hand):
            piece = game.remove_from_my_hand(index)
            try:
                game.add_piece_on_left(piece)
            except ValueError as e:
                game.add_to_my_hand(piece)
                raise ValueError("Invalid move!") from e
        case ["r", *index_list] if (index_text := "".join(index_list)) and index_text.isnumeric() and 0 <= (index := int(index_text)) < len(game.my_hand):
            piece = game.remove_from_my_hand(index)
            try:
                game.add_piece_on_right(piece)
            except ValueError as e:
                game.add_to_my_hand(piece)
                raise ValueError("Invalid move!") from e
        case ["o", "l", *piece_text] if (piece := parse_piece("".join(piece_text))):
            game.add_piece_on_left(piece)
            game.opponent_added_piece()
        case ["o", "r", *piece_text] if (piece := parse_piece("".join(piece_text))):
            game.add_piece_on_right(piece)
            game.opponent_added_piece()
        case ["x"]:
            game.opponent_draw_from_stock()
        case _:
            raise ValueError("Unknown command!")


def parse_piece(piece_text: str) -> Tuple[int, int] | None:

    if len(piece_text) != 2:
        return None

    try:
        piece = (int(piece_text[0]), int(piece_text[1]))
        if 0 <= piece[0] <= 6 and 0 <= piece[1] <= 6:
            return piece

    except ValueError:
        return None

    return None


if __name__ == "__main__":
    game = init_game()

    print(f"*-{'-' * len(START_GAME_TEXT)}-*")
    print(f"| {START_GAME_TEXT.upper()} |")
    print(f"*-{'-' * len(START_GAME_TEXT)}-*")

    print(game)
    print("-" * 32)
    print_commands()

    while True:
        text = input("Enter your command: ")
        try:
            read_execute_command(game, text)
        except ValueError:
            print("Unknown or incorrect command! Try again!")
            print_commands()

        print("-" * 32)
        print(game)
