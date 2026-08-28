"""
Authentication Controller

Handles user login, logout, and session state.
"""

from authentication.authentication_view import AuthenticationScreen
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
)


class AuthenticationController:
    """Handles authentication workflows for the CLI."""

    def __init__(self, epic_events_app, session):
        # Models
        self.session = session
        # Views
        self.epic_events_app = epic_events_app
        self.on_success_callback = None
        self.on_cancel_callback = None

    # @staticmethod
    def login(self, on_success=None, on_cancel=None):
        """ """
        self.on_success_callback = on_success
        self.on_cancel_callback = on_cancel
        self.epic_events_app.push_screen(
            AuthenticationScreen(), callback=self.handle_credentials
        )

    def handle_credentials(self, credentials):
        """Callback to handle user credentials"""
        if credentials is None:
            self.epic_events_app.notify(
                "❌ Login cancelled", severity="error"
            )
            if self.on_cancel_callback:
                self.on_cancel_callback()
            return

        user_email, user_password = credentials

        if not user_email or not user_password:
            self.epic_events_app.notify(
                "❌ Email and password are required!", severity="error"
            )
            self.login(self.on_success_callback, self.on_cancel_callback)
            return

        try:
            AuthenticationServices.login(
                self.session, user_email, user_password
            )
            self.epic_events_app.notify(
                "[bold green]✅ Login successful![/bold green]",
                severity="information",
            )
            if self.on_success_callback:
                self.on_success_callback()

        except AuthenticationError as e:
            self.epic_events_app.notify(
                f"[bold red]❌ {e!s}[/bold red]", severity="error"
            )
            self.login(self.on_success_callback, self.on_cancel_callback)

    # @staticmethod
    def logout(self):
        """
        Modal screen for user confirmation to implement
        """
        AuthenticationServices.logout()
        self.epic_events_app.notify(
            "[bold green]✅ You have been logged out.[/bold green]",
            severity="warning",
        )

    # @staticmethod
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated.
        Refresh tokens if access token is expired but refresh token is valid.
        """
        return AuthenticationServices.is_user_authenticated()

    # @staticmethod
    def get_user_info(self):
        """Get current user info from stored tokens."""
        return AuthenticationServices.get_user_info(self.session)
