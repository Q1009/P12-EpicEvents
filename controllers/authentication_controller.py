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
        self._credentials = {}
        # Views
        self.authentication_view = authentication_view

    def get_user_credentials(self):
        # Prompt user for credentials
        user_email, user_password = self.authentication_view.prompt_credentials()
        self._credentials['email'] = user_email
        self._credentials['password'] = user_password

    # @staticmethod
    def login(self):
        """
        """
        authenticated = False
        while not authenticated:
            self.get_user_credentials()

            try:
                AuthenticationServices.login(
                    self.session,
                    self._credentials['email'],
                    self._credentials['password']
                )
                # print("\n✅ Login successful!")
                self.authentication_view.prompt_successful_login_message()
                authenticated = True
                return True
            
            except AuthenticationError as e:
                # print(f"\n❌ {e}")
                self.authentication_view.prompt_fail_login_message(str(e))

    # @staticmethod
    def logout(self):
        """
        """
        self.authenticated = False
        AuthenticationServices.logout()
        self._credentials.clear()
        # print("\n✅ You have been logged out.")
        self.authentication_view.prompt_successful_logout_message()

    # @staticmethod
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return AuthenticationServices.is_user_authenticated()

    # # @staticmethod
    # def get_user_info() -> Optional[dict]:
    #     """Get current user info from stored tokens."""
    #     return AuthenticationServices.get_authenticated_user()
