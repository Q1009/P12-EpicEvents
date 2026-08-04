"""
Authentication Controller

Handles user login, logout, and session state.
"""

from services import AuthenticationServices, AuthenticationError
from tokens import tokens_exist
from typing import Optional

class AuthController:
    """Handles authentication workflows for the CLI."""

    @staticmethod
    def login(session) -> bool:
        """
        Prompt user for credentials and attempt login.

        Args:
            session: SQLAlchemy session

        Returns:
            True if login successful, False otherwise
        """
        print("\n" + "=" * 40)
        print("              LOGIN TO EPIC EVENTS")
        print("=" * 40)

        email = input("Email: ").strip()
        if not email:
            print("❌ Email cannot be empty")
            return False

        password = input("Password: ").strip()
        if not password:
            print("❌ Password cannot be empty")
            return False

        try:
            AuthenticationServices.login(session, email, password)
            print("\n✅ Login successful!")
            return True
        except AuthenticationError as e:
            print(f"\n❌ {e}")
            return False

    @staticmethod
    def logout() -> None:
        """Clear authentication tokens."""
        AuthenticationServices.logout()
        print("\n✅ You have been logged out.")

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is currently authenticated."""
        # Checks if the file for storing tokens exists and
        # if it has a valid format data stored inside.
        return tokens_exist()

    @staticmethod
    def get_user_info() -> Optional[dict]:
        """Get current user info from stored tokens."""
        return AuthenticationServices.get_authenticated_user()