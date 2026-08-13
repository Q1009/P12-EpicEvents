from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, OptionList, Label, Button
from textual import on
from textual.screen import Screen

class EventScreen(Screen):
    """
    Ecran de Events
    """
    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - EVENTS")
        yield Label(f'This is the event menu.')
        yield Button('Back', id='back', variant='warning')

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss(True)