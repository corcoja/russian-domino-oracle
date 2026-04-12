from pyfiglet import Figlet
from rich.console import Console

from src.interface.renderer import format_state_snapshot
from src.game.game_state import GameState, MAIN_PLAYER_ID
from src.game.game_state_transitions import advance_to_next_player, apply_game_move, main_player_state_has_legal_play

from .command_parser import ParsedCommandType, parse_command
from .setup import init_game


class CLIApp:

    def __init__(self, title: str = "Kozel Domino Oracle"):
        self.title = title
        self.console = Console()

    def print_commands(self) -> None:
        print(
            "Commands:\n"
            "  dXY / d   : Draw. On your turn (P0): dXY known tile (example: d35). On opponent turn: d unknown draw.\n"
            "  lXY       : Current player plays on left with tile XY (example: l46).\n"
            "  rXY       : Current player plays on right with tile XY (example: r46).\n"
            "  p         : Pass (opponents only). Your pass is automatic when no legal move exists.\n"
            "  show      : Print current state and ASCII table.\n"
            "  help      : Print this help.\n"
            "  quit      : Exit.\n"
        )

    def print_turn_flow_note(self) -> None:
        print(
            "Note:\n"
            "  - After draw, the same player keeps the turn.\n"
            "  - Keep entering draws for that player until they can play lXY/rXY.\n"
            "  - Pass is allowed only when stock is empty and no play is possible.\n"
        )

    def run(self) -> None:
        game = init_game()

        # Display the game logo
        figlet = Figlet(font="big", width=100)
        logo_text = figlet.renderText(self.title)
        self.console.print(logo_text, style="bold")

        self.print_commands()
        self.print_turn_flow_note()

        print("\n")
        print(format_state_snapshot(game))

        while True:
            self._try_auto_pass_main_player(game)
            text = input("Enter command: ").strip()

            try:
                parsed_command = parse_command(text, game)

                match parsed_command.command_type:
                    case ParsedCommandType.QUIT:
                        print("Exiting Kozel Domino Oracle.")
                        break

                    case ParsedCommandType.HELP:
                        self.print_commands()
                        self.print_turn_flow_note()
                        continue

                    case ParsedCommandType.SHOW:
                        print("\n")
                        print(format_state_snapshot(game))
                        continue

                    case ParsedCommandType.GAME_MOVE:
                        if parsed_command.game_move is None:
                            raise ValueError("Missing game move payload.")
                        apply_game_move(game, parsed_command.game_move)
                        print("\n")
                        print(format_state_snapshot(game))

                    case _:
                        raise ValueError("Unsupported command type.")

            except ValueError as exc:
                print(f"Invalid command or move: {exc}")
                print("Type 'help' to see all commands.")

    def _try_auto_pass_main_player(self, game: GameState) -> bool:
        if game.next_player_move != MAIN_PLAYER_ID:
            return False

        if main_player_state_has_legal_play(game):
            return False

        if game.stock_size > 0:
            return False

        print("You cannot move with current hand. Automatically moving to the next player.")
        advance_to_next_player(game)
        print(format_state_snapshot(game))
        return True
