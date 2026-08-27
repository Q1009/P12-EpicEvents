from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, OptionList
from textual.widgets.option_list import Option


class AuthenticatedMainScreen(Screen[str]):
    """
    Main screen for authenticated users in the EpicEvents CRM application.

    Displays a welcome message with the user's name and a navigation menu
    providing access to all CRM modules: Events, Contracts, Customers,
    Collaborators, Profile, and Logout.

    :param user_name: The username of the authenticated collaborator,
        used in the welcome message.
    """

    SUB_TITLE = "HOME"
    CSS_PATH = "styles/main_screen.tcss"

    def __init__(self, user_name) -> None:
        self.user_name = user_name
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes="home-main-container"):
            yield Label(
                f"Welcome [bold]{self.user_name}[/bold] !",
                classes="welcome-user-label",
            )
            yield OptionList(
                Option("Events", id="events"),
                None,
                Option("Contracts", id="contracts", disabled=True),
                None,
                Option("Customers", id="customers"),
                None,
                Option("Collaborators", id="collaborators", disabled=True),
                None,
                Option("Profile", id="profile", disabled=True),
                None,
                Option("Logout", id="logout"),
                classes="home-option-list",
            )
        yield Footer(show_command_palette=False)

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ):
        self.dismiss(event.option.id)


class UnauthenticatedMainScreen(Screen[str]):
    """
    Main screen for unauthenticated users in the EpicEvents CRM application.

    Provides a minimal menu with options to log in or quit the application.
    This is the entry point for users who have not yet authenticated.
    """

    SUB_TITLE = "WELCOME"
    CSS_PATH = "styles/main_screen.tcss"

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes="home-main-container"):
            yield Label(
                "Please login to access services",
                classes="welcome-user-label",
            )
            yield OptionList(
                Option("Login", id="login"),
                None,
                Option("Quit", id="quit"),
                classes="home-option-list",
            )
        yield Footer(show_command_palette=False)

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ):
        self.dismiss(event.option.id)
