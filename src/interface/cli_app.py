from src.interface.renderer import format_end_game_summary, format_state_snapshot, game_title_logo
from src.game.game_state import GameState, MAIN_PLAYER_ID
from src.game.game_state_transitions import advance_to_next_player, apply_player_action, main_player_state_has_legal_play

from .command_parser import ParsedCommandType, parse_command
from .setup import init_game


class CLIApp:

    def print_commands(self) -> None:
        print(
            "Commands:\n"
            "  dXY / d   : Draw. On your turn (P0): dXY known tile (example: d35). On opponent turn: d unknown draw.\n"
            "  lXY       : Current player plays on left with tile XY (example: l46).\n"
            "  rXY       : Current player plays on right with tile XY (example: r46).\n"
            "  p         : Pass (opponents only). Your pass is automatic when no legal move exists.\n"
            "  end       : End game with summary (allowed only if stock is empty and you have no legal play).\n"
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
        try:
            game = init_game()
        except EOFError as exc:
            print(exc)
            return

        print("\n")
        print(game_title_logo())

        self.print_commands()
        self.print_turn_flow_note()

        print("\n")
        print(format_state_snapshot(game))

        while True:
            if self._maybe_finish_when_any_hand_empty(game):
                break

            self._try_auto_pass_main_player(game)
            try:
                text = input("Enter command: ").strip()
            except EOFError:
                print("Input ended. Exiting Kozel Domino Oracle.")
                break

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

                    case ParsedCommandType.END_GAME:
                        end_game_blockers = self._get_end_game_blockers(game)
                        if end_game_blockers:
                            print("Cannot end game yet:")
                            for blocker in end_game_blockers:
                                print(f"  - {blocker}")
                            continue

                        print(format_end_game_summary(game, reason="Manual end game invoked."))
                        break

                    case ParsedCommandType.SHOW:
                        print("\n")
                        print(format_state_snapshot(game))
                        continue

                    case ParsedCommandType.PLAYER_ACTION:
                        if parsed_command.player_action is None:
                            raise ValueError("Missing player action payload.")
                        apply_player_action(game, parsed_command.player_action)
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

    def _maybe_finish_when_any_hand_empty(self, game: GameState) -> bool:
        empty_hand_players = [
            player_state.player
            for player_state in sorted(game.player_states, key=lambda current: current.player.id)
            if len(player_state.hand) == 0
        ]

        if not empty_hand_players:
            return False

        player_text = ", ".join(str(player) for player in empty_hand_players)
        print(format_end_game_summary(game, reason=f"Player(s) finished hand: {player_text}."))
        return True

    def _get_end_game_blockers(self, game: GameState) -> list[str]:
        blockers: list[str] = []

        if game.stock_size > 0:
            blockers.append(f"Stock is not empty yet (stock size: {game.stock_size}).")

        if main_player_state_has_legal_play(game):
            blockers.append("You still have at least one legal move on the snake.")

        return blockers
