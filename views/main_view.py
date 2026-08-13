from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, OptionList, Label, Button
from textual import on
from textual.screen import Screen

class MainScreen(Screen[str]):
    """

    """
    BINDINGS = [('q', 'quit', 'Quitter')]
    
    def __init__(self, user_name) -> None:
        self.user_name = user_name
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - HOME")
        yield Label(f'Welcome [bold]Quentin[/bold] !')
        yield OptionList(
            'Events',
            'Contracts',
            'Customers',
            'Collaborators',
            'Profile',
            id='main-menu',
        )
        yield Footer(show_command_palette=False)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        selected_text = event.option.prompt
        self.dismiss(selected_text)