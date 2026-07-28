# services/authentication_services.py
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy.orm import Session
from config.settings import settings
from config import get_private_key, get_public_key
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

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Create an access JWT token."""
        private_key = get_private_key()
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expiration = datetime.utcnow() + expires_delta

        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "exp": expiration,
            "iat": datetime.utcnow()
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
        expiration = datetime.utcnow() + expires_delta

        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "refresh",
            "exp": expiration,
            "iat": datetime.utcnow()
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
    def refresh_access_token(refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using a refresh token."""
        payload = TokenService.verify_token(refresh_token, "refresh")

        new_access_token = TokenService.create_access_token(
            int(payload["sub"]),
            payload["email"]
        )

        # Optionally create a new refresh token (rotation)
        new_refresh_token = TokenService.create_refresh_token(
            int(payload["sub"]),
            payload["email"]
        )

        return new_access_token, new_refresh_token

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

    @staticmethod
    def login(session: Session, email: str, password: str) -> Tuple[str, str, dict]:
        """
        Authenticate a user and return access/refresh tokens.

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

        return access_token, refresh_token, user_info

    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user info from a valid access token."""
        payload = TokenService.verify_token(token, "access")
        return {
            "user_id": int(payload["sub"]),
            "email": payload["email"]
        }