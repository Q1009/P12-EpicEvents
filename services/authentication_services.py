import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Callable
from functools import wraps
from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy.orm import Session
from config import settings
from keys import get_private_key, get_public_key
from tokens import save_tokens, load_tokens, clear_tokens
from controllers import AuthController
from models import Collaborator

class AuthenticationError(Exception):
    """
    Exception raised when a user cannot provide valid credentials.

    Attributes:
        message (str): Explanation of the authentication error
    """

    def __init__(self, message: str = "Authentication failed"):
        """Initialize the AuthenticationError with a custom message.

        Args:
            message: Human-readable error message
        """
        self.message = message
        super().__init__(self.message)

class TokenService:
    """Service for JWT token management."""
    # Need to configure payload data

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Create an access JWT token."""
        private_key = get_private_key()
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expiration = datetime.now(timezone.utc) + expires_delta

        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "exp": expiration,
            "iat": datetime.now(timezone.utc)
        }

        return jwt.encode(
            payload,
            private_key,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def create_refresh_token(user_id: int, email: str) -> str:
        """Create a refresh JWT token."""
        private_key = get_private_key()
        expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        expiration = datetime.now(timezone.utc) + expires_delta

        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "refresh",
            "exp": expiration,
            "iat": datetime.now(timezone.utc)
        }

        return jwt.encode(
            payload,
            private_key,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def verify_token(token: str, token_type: Optional[str] = None) -> dict:
        """Verify a JWT token and return its payload."""
        public_key = get_public_key()

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Check token type if specified
            if token_type and payload.get("type") != token_type:
                raise AuthenticationError(f"Invalid token type. Expected {token_type}")

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Tuple[str]:
        """Refresh access token using a refresh token."""
        payload = TokenService.verify_token(refresh_token, "refresh")

        new_access_token = TokenService.create_access_token(
            int(payload["sub"]),
            payload["email"]
        )

        # Optionally create a new refresh token (rotation)
        # new_refresh_token = TokenService.create_refresh_token(
        #     int(payload["sub"]),
        #     payload["email"]
        # )

        return new_access_token, # new_refresh_token

class PasswordService:
    """Service for password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return hashpw(password.encode(), gensalt()).decode()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return checkpw(
            plain_password.encode(),
            hashed_password.encode()
        )

class AuthenticationService:
    """Main authentication service."""
    # Do we really want user_info as return dict ?

    @staticmethod
    def login(session: Session, email: str, password: str) -> Tuple[str, str, dict]:
        """
        Authenticate a user and return access/refresh tokens.
        Save tokens locally

        Returns:
            Tuple of (access_token, refresh_token, user_info)
        """
        # Find user by email
        user = session.query(Collaborator).filter_by(email=email).first()

        if not user:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not PasswordService.verify_password(password, user.password):
            raise AuthenticationError("Invalid email or password")

        # Generate tokens
        access_token = TokenService.create_access_token(user.id, user.email)
        refresh_token = TokenService.create_refresh_token(user.id, user.email)

        # Return user info (without password)
        user_info = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "department": user.department.name
        }

        # Save tokens locally
        save_tokens(access_token, refresh_token, user_info)

        return access_token, refresh_token, user_info

    @staticmethod
    def logout() -> None:
        """Clear stored tokens."""
        clear_tokens()

    @staticmethod
    def get_authenticated_user() -> Optional[dict]:
        """
        Get current authenticated user from local storage.
        Automatically refreshes access token if expired.

        Returns:
            User info dict or None if not authenticated.
        """
        tokens = load_tokens()
        if not tokens:
            return None

        try:
            # Try to use the access token
            user_info = AuthenticationService.get_current_user(tokens["access_token"])
            return user_info
        except AuthenticationError:
            # Access token expired, try to refresh
            try:
                new_access_token = TokenService.refresh_access_token(
                    tokens["refresh_token"]
                )
                # Save new access token
                save_tokens(
                    new_access_token,
                    tokens["refresh_token"],
                    tokens["user"]
                )
                # Return user info from new access token
                return AuthenticationService.get_current_user(new_access_token)
            except AuthenticationError:
                # Refresh token also expired or invalid
                clear_tokens()
                return None

    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user info from a valid access token."""
        payload = TokenService.verify_token(token, "access")
        return {
            "user_id": int(payload["sub"]),
            "email": payload["email"]
        }

    @staticmethod
    def require_auth(func: Callable) -> Callable:
        """
        Decorator to ensure user is authenticated before executing a command.

        If not authenticated:
        1. Prompt for login
        2. Retry the command if login succeeds
        3. Return to menu if login fails

        Usage:
            @require_auth
            def my_protected_command(session):
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if user is authenticated
            if not AuthController.is_authenticated():
                print("\n⚠️  Authentication required for this command.")
                session = kwargs.get('session')
                if session and AuthController.login(session):
                    # Login succeeded, retry the command
                    return func(*args, **kwargs)
                else:
                    # Login failed or cancelled
                    return None

            # Get current user and inject into kwargs
            user_info = AuthController.get_user_info()
            if not user_info:
                print("\n⚠️  Your session has expired. Please login again.")
                session = kwargs.get('session')
                if session and AuthController.login(session):
                    user_info = AuthController.get_user_info()
                    if user_info:
                        kwargs['user'] = user_info
                        return func(*args, **kwargs)
                return None

            kwargs['user'] = user_info
            return func(*args, **kwargs)

        return wrapper