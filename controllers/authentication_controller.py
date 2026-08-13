"""
Authentication Controller

Handles user login, logout, and session state.
"""

from services import AuthenticationServices, AuthenticationError
from views import AuthenticationScreen

class AuthenticationController:
    """Handles authentication workflows for the CLI."""
    def __init__(self, epic_events_app, session):
        # Models
        self.session = session
        # Views
        self.epic_events_app = epic_events_app

    # @staticmethod
    def login(self):
        """
        """
        self.epic_events_app.push_screen(AuthenticationScreen(), callback=self.handle_credentials)

    def handle_credentials(self, credentials):
        """Callback to handle user credentials"""
        if credentials is None:
            self.epic_events_app.notify("❌ Login cancelled", severity="error")
            return

        user_email, user_password = credentials

        if not user_email or not user_password:
            self.epic_events_app.notify("❌ Email and password are required!", severity="error")
            self.login()
            return
        
        try:
            AuthenticationServices.login(
                self.session,
                user_email,
                user_password
            )
            self.epic_events_app.notify('[bold green]✅ Login successful![/bold green]', severity='information')

        except AuthenticationError as e:
            self.epic_events_app.notify(f'[bold red]❌ {str(e)}[/bold red]', severity='error')
            self.login()




    # @staticmethod
    def logout(self):
        """
        """
        AuthenticationServices.logout()
        self.epic_events_app.notify('[bold green]✅ You have been logged out.[/bold green]', severity='warning')

    # @staticmethod
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated.
        Refresh tokens if access token is expired but refresh token is valid.
        """
        return AuthenticationServices.is_user_authenticated()

    # # @staticmethod
    # def get_user_info() -> Optional[dict]:
    #     """Get current user info from stored tokens."""
    #     return AuthenticationServices.get_authenticated_user()
