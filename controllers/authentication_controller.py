"""
Authentication Controller

Handles user login, logout, and session state.
"""

from services import AuthenticationServices, AuthenticationError

class AuthenticationController:
    """Handles authentication workflows for the CLI."""
    def __init__(self, session, authentication_view):
        # Models
        self.session = session
        # Views
        self.authentication_view = authentication_view

    # @staticmethod
    def login(self):
        """
        """
        authenticated = False
        while not authenticated:
            user_email, user_password = self.authentication_view.prompt_credentials()

            try:
                AuthenticationServices.login(
                    self.session,
                    user_email,
                    user_password
                )
                self.authentication_view.prompt_successful_login_message()
                authenticated = True
                return True
            
            except AuthenticationError as e:
                self.authentication_view.prompt_fail_login_message(str(e))

    # @staticmethod
    def logout(self):
        """
        """
        AuthenticationServices.logout()
        self.authentication_view.prompt_successful_logout_message()

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
