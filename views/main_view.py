from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, OptionList, Label, Button
from textual import on
from textual.screen import Screen

class AuthenticatedMainScreen(Screen[str]):
    """

    """
    def __init__(self, user_name) -> None:
        self.user_name = user_name
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - HOME")
        yield Label(f'Welcome [bold]{self.user_name}[/bold] !')
        yield OptionList(
            'Events',
            'Contracts',
            'Customers',
            'Collaborators',
            'Profile',
            'Logout',
            id='authenticated-main-menu',
        )
        yield Footer(show_command_palette=False)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        selected_text = event.option.prompt
        self.dismiss(selected_text)

class UnauthenticatedMainScreen(Screen[str]):
    """
    
    """
    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - CRM")
        yield OptionList(
            'Login',
            'Quit',
            id='unauthenticated-main-menu',
        )
        yield Footer(show_command_palette=False)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        selected_text = event.option.prompt
        self.dismiss(selected_text)