from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import box
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Header, Static
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

class LoginScreen(Screen):
    """Écran de login avec formulaire interactif"""
    CSS = """
        Screen {
            align: center middle;
        }
        Container {
            width: 50;
            height: auto;
            border: round;
            border-title-style: bold;
        }
        Header {
            text-align: center;
            color: cyan;
        }
        Input {
            width: 100%;
            margin: 1 0;
        }
        Button {
            width: 100%;
            margin: 1 0;
        }
        InstructionFooter {
            dock: bottom;
            width: 100%;
            text-align: center;
        }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Header("EPIC EVENTS - LOGIN"),
            Input(placeholder="Email", id="email"),
            Input(placeholder="Password", id="password", password=True),
            Button("Submit", id="submit", variant="primary"),
            Button("Back", id="back", variant="default"),
            InstructionFooter(),
            id="login-form"
        )

    @on(Button.Pressed, "#submit")
    def on_submit(self, event: Button.Pressed) -> None:
        """Gère la validation du formulaire"""
        email = self.query_one("#email", Input).value
        password = self.query_one("#password", Input).value

        if not email or not password:
            self.notify("❌ Email and password are required!", severity="error")
            return

        self.dismiss((email, password))  # Retourne le tuple au caller

    @on(Button.Pressed, "#back")
    def on_back(self, event: Button.Pressed) -> None:
        """Gère le retour au menu précédent"""
        self.dismiss(None)

    # def on_key(self, event: Key) -> None:
    #     """Gère la touche Échap pour revenir"""
    #     if event.key == "escape":
    #         self.dismiss(None)

class LoginApp(App):
    """Application Textual pour afficher le login screen"""
    def __init__(self):
        super().__init__()
        self.result = None

    async def on_mount(self) -> None:
        """Affiche le LoginScreen au démarrage"""
        self.push_screen(LoginScreen())

    def _on_key(self, event):
        if event.key == 'escape':
            self.exit()

    def on_screen_dismissed(self, event) -> None:
        """Récupère le résultat du screen et quitte l'app"""
        self.result = event.result
        self.exit()

class AuthenticationView:
    # Rich implementation
    def __init__(self):
        self.footer = (
            "[dim]Use [bold]↑/↓[/bold] to navigate | "
            "[bold]Enter[/bold] to select | "
            "[bold]Esc[/bold] to return[/dim]"
        )

    def _render_header(self):
        """Affiche l'en-tête stylisé"""
        header = Panel(
            "[bold cyan]EPIC EVENTS - LOGIN[/bold cyan]",
            box=box.DOUBLE,
            padding=(1, 3),
            border_style="cyan"
        )
        console.print(header)

    def _render_footer(self):
        """Affiche le pied avec instructions"""
        footer = Panel(
            self.footer,
            box=box.ROUNDED,
            padding=(0, 2),
            border_style="dim"
        )
        console.print(footer)

    def prompt_credentials(self):
        """
        Affiche un formulaire interactif avec :
        - Navigation par flèches entre les champs
        - Validation avec Entrée
        - Retour avec Échap
        - Messages d'erreur stylisés
        """
        # # Textual Implementation
        # app = LoginApp()
        # app.run()
        # return app.result
        # # ======================

        # Rich Implementation
        while True:
            console.clear()

            self._render_header()
            self._render_footer()

            # Affichage des champs
            console.print("\n[bold]Please enter your credentials:[/bold]\n")

            try:
                # Utilisation de Prompt de rich pour chaque champ
                email = Prompt.ask(
                    "[bold green]Email[/bold green]",
                    password=False,
                    default="",
                )
                if email == "":
                    console.print("[red]❌ Email cannot be empty[/red]")
                    Prompt.ask("\nPress Enter to continue...")
                    continue

                password = Prompt.ask(
                    "[bold green]Password[/bold green]",
                    password=True,  # Masque la saisie
                )
                if password == "":
                    console.print("[red]❌ Password cannot be empty[/red]")
                    Prompt.ask("\nPress Enter to continue...")
                    continue

                return (email, password)

            except KeyboardInterrupt:
                # Si l'utilisateur appuie sur Ctrl+C ou Échap
                return None

    def prompt_successful_login_message(self):
        console.print("\n[bold green]✅ Login successful![/bold green]")

    def prompt_fail_login_message(self, message: str = 'Failed to log in'):
        console.print(f"\n[bold red]❌ {message}[/bold red]")
        Prompt.ask("\nPress Enter to retry...")

    def prompt_successful_logout_message(self):
        console.print("\n[bold green]✅ You have been logged out.[/bold green]")