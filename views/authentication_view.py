from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import box
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Header, Static, Footer
from textual.screen import Screen
from textual.containers import Container
from textual import on
from textual.events import Key

console = Console()

class InstructionFooter(Static):
    """Widget personnalisé pour l'encart d'instructions"""
    def __init__(self):
        super().__init__()
        self.update(
            "[dim]Use [bold]Tab[/bold] to navigate | "
            "[bold]Enter[/bold] to select | "
            "[bold]Esc[/bold] to return[/dim]"
        )
        self.styles.border = ("round", "dimgrey")

class AuthenticationScreen(Screen):
    
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Container(
            Header("EPIC EVENTS - AUTHENTICATION"),
            Input(placeholder="Email", id="email"),
            Input(placeholder="Password", id="password", password=True),
            Button("Submit", id="submit", variant="primary"),
            Button("Back", id="back", variant="default"),
            Footer(),
            id="authentication-form"
        )

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