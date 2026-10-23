from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, OptionList
from textual.widgets.option_list import Option


class AuthenticatedMainScreen(Screen[str]):
    """Main screen for authenticated users in the EpicEvents CRM application.

    Displays a welcome message with the user's name and a navigation menu
    providing access to all CRM modules: Events, Contracts, Customers,
    Collaborators, Profile, and Logout.

    :param user_name: The first name of the authenticated collaborator,
        used in the welcome message.
    :type user_name: str
    """

    SUB_TITLE = "HOME"
    CSS_PATH = "../styles/main_screen.tcss"

    def __init__(self, user_name: str) -> None:
        """Initialize the authenticated main screen with user information.

        :param user_name: The first name of the authenticated user to display
            in the welcome message.
        :type user_name: str
        """
        self.user_name: str = user_name
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates and yields the header, main container with welcome message
        and navigation options, and footer. The navigation menu includes
        options for all CRM modules.

        :return: Generator yielding Header, Container with Label and OptionList,
            and Footer widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="home-main-container"):
            yield Label(
                f"Welcome [bold]{self.user_name}[/bold] !",
                classes="welcome-user-label",
            )
            yield OptionList(
                Option("Events", id="events"),
                None,
                Option("Contracts", id="contracts", disabled=False),
                None,
                Option("Customers", id="customers"),
                None,
                Option(
                    "Collaborators", id="collaborators", disabled=False
                ),
                None,
                Option("Profile", id="profile", disabled=True),
                None,
                Option("Logout", id="logout"),
                classes="home-option-list",
            )
        yield Footer(show_command_palette=False)

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Handle user selection from the option list.

        Dismisses the screen with the ID of the selected option, which
        triggers the callback registered with the screen to handle the
        navigation.

        :param event: The option selected event containing the chosen option.
        :type event: OptionList.OptionSelected
        """
        self.dismiss(event.option.id)


class UnauthenticatedMainScreen(Screen[str]):
    """Main screen for unauthenticated users in the EpicEvents CRM application.

    Provides a minimal menu with options to log in or quit the application.
    This is the entry point for users who have not yet authenticated.
    """

    SUB_TITLE = "WELCOME"
    CSS_PATH = "../styles/main_screen.tcss"

    def __init__(self) -> None:
        """Initialize the unauthenticated main screen.

        Creates a basic screen instance without requiring user-specific data.
        """
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates and yields the header, main container with login prompt
        and basic navigation options, and footer. The menu provides
        Login and Quit options for unauthenticated users.

        :return: Generator yielding Header, Container with Label and OptionList,
            and Footer widgets.
        :rtype: ComposeResult
        """
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
    ) -> None:
        """Handle user selection from the option list.

        Dismisses the screen with the ID of the selected option, which
        triggers the callback registered with the screen to handle the
        navigation.

        :param event: The option selected event containing the chosen option.
        :type event: OptionList.OptionSelected
        """
        self.dismiss(event.option.id)
