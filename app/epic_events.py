from typing import ClassVar

import sentry_sdk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from config.settings import settings
from main.main_controller import MainController


class EpicEventsCRM(App):
    """
    CLI of EpicEvents CRM
    """

    TITLE = "EPIC EVENTS CRM"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        # Initialize DB connection with session
        self.engine = create_engine(settings.DB_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Initialize MVC
        self.main_controller = MainController(self, self.session)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer(show_command_palette=False)

    def on_ready(self):
        self.theme = "nord"
        self.main_controller.start()

    def _handle_exception(self, error: Exception) -> None:
        """Capture all unhandled exceptions with Sentry.

        This method is called by Textual when an unhandled exception occurs.
        We capture it with Sentry and then let Textual handle it normally.
        """
        sentry_sdk.capture_exception(error)
        # Optionnal : locally log the exception
        self.log.error(f"Unhandled exception: {error}")
        # Then let Textual display error
        super()._handle_exception(error)

    def on_exit_app(self):
        self.session.close()
        self.engine.dispose()
