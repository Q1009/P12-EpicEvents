from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input


class AuthenticationScreen(Screen):

    SUB_TITLE = 'AUTHENTICATION'

    CSS_PATH = 'styles/authentication_screen.tcss'
    
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes='main-container'):
            with Container(classes='credentials-container'):
                yield Input(placeholder="Email", id="email", classes='credentials-input')
                yield Input(placeholder="Password", id="password", password=True, classes='credentials-input')
            with Container(classes='buttons-container'):
                yield Button("Submit", id="submit", variant="primary", classes='credentials-button')
                yield Button("Back", id="back", variant="default", classes='credentials-button')
        yield Footer(show_command_palette=False)

    @on(Button.Pressed, "#submit")
    def on_submit(self, event: Button.Pressed) -> None:
        """Gère la validation du formulaire"""
        email = self.query_one("#email", Input).value
        password = self.query_one("#password", Input).value
        self.dismiss((email, password))  # Retourne le tuple au caller

    @on(Button.Pressed, "#back")
    def on_back(self, event: Button.Pressed) -> None:
        """Gère le retour au menu précédent"""
        self.dismiss(None)