from .cli_app import CLIApp


def run_cli() -> None:
    app = CLIApp()
    app.run()
