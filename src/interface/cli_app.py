from pyfiglet import Figlet
from rich.console import Console

from src.game.renderer import format_state_snapshot
from src.interface.command_parser import ParsedCommandType, parse_command
from src.interface.setup import init_game


class CLIApp:
    def __init__(self, title: str = "Kozel Domino Oracle"):
        self.title = title
        self.console = Console()

    def print_commands(self) -> None:
        print(
            "Commands:\n"
            "  dXY       : You draw known tile XY from stock (example: d35).\n"
            "  lI        : You play your hand index I on the left (example: l0).\n"
            "  rI        : You play your hand index I on the right (example: r2).\n"
            "  pNlXY     : Player N plays known tile XY on left (example: p1l46).\n"
            "  pNrXY     : Player N plays known tile XY on right (example: p1r46).\n"
            "  pNx       : Player N draws unknown tile from stock (example: p1x).\n"
            "  olXY      : Alias for p1lXY in 1v1 mode.\n"
            "  orXY      : Alias for p1rXY in 1v1 mode.\n"
            "  x         : Alias for p1x in 1v1 mode.\n"
            "  show      : Print current state and ASCII table.\n"
            "  help      : Print this help.\n"
            "  quit      : Exit.\n"
        )

    def run(self) -> None:
        game = init_game()

        # Display the game logo
        figlet = Figlet(font="big", width=100)
        logo_text = figlet.renderText(self.title)
        self.console.print(logo_text, style="bold")

        self.print_commands()

        print("\n")
        print(format_state_snapshot(game))

        while True:
            text = input("Enter command: ").strip()

            try:
                parsed_command = parse_command(text, game)

                match parsed_command.command_type:
                    case ParsedCommandType.QUIT:
                        print("Exiting Kozel Domino Oracle.")
                        break

                    case ParsedCommandType.HELP:
                        self.print_commands()
                        continue

                    case ParsedCommandType.SHOW:
                        print("\n")
                        print(format_state_snapshot(game))
                        continue

                    case ParsedCommandType.GAME_MOVE:
                        if parsed_command.game_move is None:
                            raise ValueError("Missing game move payload.")
                        game.apply_move(parsed_command.game_move)
                        print("\n")
                        print(format_state_snapshot(game))

                    case _:
                        raise ValueError("Unsupported command type.")

            except ValueError as exc:
                print(f"Invalid command or move: {exc}")
                print("Type 'help' to see all commands.")
