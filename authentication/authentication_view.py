"""
Authentication View Module
==========================

Provides the :class:`AuthenticationScreen` Textual screen for user login.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input


class AuthenticationScreen(Screen):
    """Textual screen for user authentication (login form).

    This screen displays a login form with email and password input fields,
    along with Submit and Back buttons. When submitted, it returns the
    credentials as a tuple (email, password) via the dismiss callback.
    When cancelled, it returns None.

    .. note::
        Uses CSS styles from ``../styles/authentication_screen.tcss``.
    """

    SUB_TITLE = "AUTHENTICATION"
    CSS_PATH = "../styles/authentication_screen.tcss"

    def __init__(self):
        """Initialize the AuthenticationScreen."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the screen layout.

        Builds the UI hierarchy with:
        - A header with clock
        - Email and password input fields
        - Submit and Back buttons
        - A footer

        :return: Generator yielding the screen's widgets
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="main-container"):
            with Container(classes="credentials-container"):
                yield Input(
                    placeholder="Email",
                    id="email",
                    classes="credentials-input",
                )
                yield Input(
                    placeholder="Password",
                    id="password",
                    password=True,
                    classes="credentials-input",
                )
            with Container(classes="buttons-container"):
                yield Button(
                    "Submit",
                    id="submit",
                    variant="primary",
                    classes="credentials-button",
                )
                yield Button(
                    "Back",
                    id="back",
                    variant="default",
                    classes="credentials-button",
                )
        yield Footer(show_command_palette=False)

    @on(Button.Pressed, "#submit")
    def on_submit(self, event: Button.Pressed) -> None:
        """Handle submit button press.

        Extracts email and password from the input fields and dismisses
        the screen with the credentials tuple.

        :param event: The button pressed event
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        email = self.query_one("#email", Input).value
        password = self.query_one("#password", Input).value
        self.dismiss((email, password))

    @on(Button.Pressed, "#back")
    def on_back(self, event: Button.Pressed) -> None:
        """Handle back button press.

        Dismisses the screen with None to indicate login was cancelled.

        :param event: The button pressed event
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        self.dismiss(None)
