from typing import ClassVar

import sentry_sdk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from config.settings import settings
from main.main_controller import MainController


class EpicEventsCRM(App):
    """Main CLI application for EpicEvents CRM.

    This application serves as the entry point for the EpicEvents CRM system,
    providing a Textual-based user interface for managing customers, contracts,
    and events. It initializes the database connection, sets up the MVC architecture,
    and manages the application lifecycle.

    :param: Inherits from Textual's App class; no additional parameters required.
    :type: textual.app.App

    .. note::
        The application uses SQLAlchemy for database operations and Sentry for
        error tracking. The MVC pattern is implemented with MainController
        coordinating between views and models.
    """

    TITLE = "EPIC EVENTS CRM"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        """Initialize the EpicEventsCRM application.

        Sets up database connection with SQLAlchemy session and initializes
        the MVC architecture by creating the MainController instance.

        :param: None (inherits from App)
        :type: None
        """
        super().__init__()
        # Initialize DB connection with session
        self.engine = create_engine(settings.DB_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Initialize MVC
        self.main_controller = MainController(self, self.session)

    def compose(self) -> ComposeResult:
        """Compose the application's user interface.

        Creates and yields the header and footer widgets for the application.
        The header displays the application title and a clock, while the footer
        provides command palette functionality.

        :return: Generator yielding Header and Footer widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        yield Footer(show_command_palette=False)

    def on_ready(self):
        """Handle application ready event.

        Called when the application has finished composing and is ready to run.
        Sets the application theme to 'nord' and starts the main controller.
        """
        self.theme = "nord"
        self.main_controller.start()

    def _handle_exception(self, error: Exception) -> None:
        """Capture all unhandled exceptions with Sentry.

        This method is called by Textual when an unhandled exception occurs.
        We capture it with Sentry and then let Textual handle it normally.

        :param error: The exception that was raised.
        :type error: Exception
        :return: None
        :rtype: None

        .. note::
            The exception is also logged locally before being passed to
            Textual's default exception handler.
        """
        sentry_sdk.capture_exception(error)
        # Optional: locally log the exception
        self.log.error(f"Unhandled exception: {error}")
        # Then let Textual display error
        super()._handle_exception(error)

    def on_exit_app(self):
        """Handle application exit event.

        Clean up database resources by closing the SQLAlchemy session
        and disposing the engine when the application exits.
        """
        self.session.close()
        self.engine.dispose()
