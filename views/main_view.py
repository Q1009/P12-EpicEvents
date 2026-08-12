from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, OptionList, Label, Button
from textual import on
from textual.screen import Screen

class MainView:
    """
    """
    def __init__(self):
        pass

    def main_menu(self):
        # print("Welcome to EpicEvents' CRM")
        EpicEventsCRM().run()

class EventsScreen(Screen):
    """
    Ecran de Events
    """
    def __init__(self, option_list: str) -> None:
        self.option_list = option_list
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - EVENTS")
        yield Label(f'This is the {self.option_list} menu.')
        yield Button('Back', id='back', variant='error')

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss(True)

class EpicEventsCRM(App):
    """
    CLI of EpicEvents CRM
    """

    BINDINGS = [('q', 'quit', 'Quitter')]

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - HOME")
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
        match selected_text:
            case 'Events':
                # Retourner Events au controlleur
                self.push_screen(EventsScreen(selected_text))
                self.notify('Events', severity='information')
            case 'Contracts':
                # Retourner Contracts au controlleur
                self.notify('Contracts', severity='warning')
            case 'Customers':
                # Retourner Customers au controlleur
                self.notify('Customers', severity='error')
            case 'Collaborators':
                # Retourner Customers au controlleur
                self.notify('Collaborators', severity='information')
            case 'Profile':
                # Retourner Profile au controlleur
                self.notify('Profile', severity='information')
                self.exit()
        