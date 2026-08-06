import jwt
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Callable
from functools import wraps
from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy.orm import Session
from config import settings
from keys import get_private_key, get_public_key
from tokens import save_tokens, load_tokens, clear_tokens, tokens_exist
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

class PasswordServices:
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

class TokenServices:
    """Service for JWT token management."""
    # Need to configure payload data

    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Create an access JWT token."""
        private_key = get_private_key()
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expiration = datetime.now(timezone.utc) + expires_delta

        payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
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
    def create_refresh_token(user_id: int) -> str:
        """Create a refresh JWT token."""
        private_key = get_private_key()
        expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        expiration = datetime.now(timezone.utc) + expires_delta

        payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
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
        """Verify and decode a JWT token.

        Decodes and validates a JWT token using the application's public key.
        Optionally validates the token type claim against the provided parameter.
        Returns the decoded payload.
        Raises AuthenticationError if verification fails.

        :param token: The JWT token string to verify and decode
        :type token: str
        :param token_type: Optional expected token type to validate against.
            If provided, the token's 'type' claim must match this value (e.g., 'access' or 'refresh').
            If None, type validation is skipped.
        :type token_type: Optional[str]
        :return: The decoded token payload containing all JWT claims such as:
            - ``sub``: User ID
            - ``jti``: Unique token identifier
            - ``type``: Token type
            - ``exp``: Expiration timestamp
            - ``iat``: Issued at timestamp
        :rtype: dict
        :raises AuthenticationError: If token verification fails due to:
            - Token has expired (:exc:`jwt.ExpiredSignatureError`)
            - Invalid token signature or format (:exc:`jwt.InvalidTokenError`)
            - Token type mismatch (if ``token_type`` is provided)
        """
        public_key = get_public_key()

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Check token type if specified
            if token_type and payload.get('type') != token_type:
                raise AuthenticationError(f'Invalid token type. Expected {token_type}')
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f'Invalid token: {str(e)}')

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Tuple[str, str]:
        """Refresh an access token using a valid refresh token.

        Performs token rotation by generating a new access token and a new refresh token
        using the provided refresh token. The old refresh token remains valid until its
        expiration, but the new tokens should be used for subsequent requests.

        :param refresh_token: A valid JWT refresh token used to generate new tokens
        :type refresh_token: str
        :return: A tuple containing:
            - **new_access_token** (str): Newly generated access token with fresh expiration
            - **new_refresh_token** (str): Newly generated refresh token for future rotations
        :rtype: Tuple[str, str]
        :raises AuthenticationError: If the refresh token verification fails due to:
            - Token has expired
            - Invalid token signature or format
            - Token is not of type 'refresh'
        """
        payload = TokenServices.verify_token(refresh_token, 'refresh')

        # Create a new access token
        new_access_token = TokenServices.create_access_token(
            int(payload['sub'])
        )

        # Create a new refresh token (rotation)
        new_refresh_token = TokenServices.create_refresh_token(
            int(payload['sub'])
        )

        # Save tokens locally
        save_tokens(new_access_token, new_refresh_token)

    @staticmethod
    def invalidate_refresh_token(refresh_token: str) -> None:
        """
        Invalidate a refresh token.

        Note: JWTs are stateless, so invalidation typically requires
        maintaining a blacklist or revocation list. This method is a placeholder
        for implementing such logic if needed.

        :param refresh_token: The refresh token to invalidate
        :type refresh_token: str
        """
        # Placeholder for token invalidation logic (e.g., add to blacklist)
        pass

class AuthenticationServices:
    """
    Main authentication service.
    """
    @staticmethod
    def login(session: Session, email: str, password: str) -> Tuple[str, str]:
        """Authenticate a user and generate authentication tokens.

        Validates user credentials against the database and generates JWT tokens
        for subsequent authenticated requests. Tokens are automatically saved to
        local storage for persistence across sessions.

        :param session: SQLAlchemy database session for querying user information
        :type session: Session
        :param email: User's email address for authentication
        :type email: str
        :param password: User's password for verification
        :type password: str
        :return: A tuple containing:
            - **access_token** (str): JWT access token with short expiration
            - **refresh_token** (str): JWT refresh token for obtaining new access tokens
        :rtype: Tuple[str, str]
        :raises AuthenticationError: If authentication fails due to:
            - User not found with provided email
            - Password verification failure
        """
        # Find user by email
        user = session.query(Collaborator).filter_by(email=email).first()

        if not user:
            raise AuthenticationError('Invalid email or password')

        # Verify password
        if not PasswordServices.verify_password(password, user.password):
            raise AuthenticationError('Invalid email or password')

        # Generate tokens
        access_token = TokenServices.create_access_token(user.id)
        refresh_token = TokenServices.create_refresh_token(user.id)

        # Save tokens locally
        save_tokens(access_token, refresh_token)

    @staticmethod
    def logout() -> None:
        """
        Clear stored authentication tokens.

        Removes the locally stored access and refresh tokens by deleting
        the token file, effectively logging out the current authenticated user.

        :rtype: None
        """
        clear_tokens()

    @staticmethod
    def get_user_id_by_token(token: str) -> int:
        """
        Extract user ID from a verified access token.

        Verifies the provided token and extracts the user ID from its payload.
        If the token is invalid or expired, an AuthenticationError is raised.

        :param token: The access token string to verify
        :type token: str
        :return: Integer of the user_id
        :rtype: int
        :raises AuthenticationError: If token verification fails
        (expired, invalid, or type mismatch)
        """
        payload = TokenServices.verify_token(token, 'access')
        return int(payload['sub'])

    @staticmethod
    def require_auth(func: Callable) -> Callable:
        """
        Decorator to ensure user authentication before executing a command.

        Validates authentication tokens and automatically handles token refresh
        when access tokens are expired. Returns None if authentication fails.

        Workflow:
            1. Checks if local tokens exist and are valid
            2. If no tokens: prints authentication message and returns None
            3. If valid access token: executes the decorated function
            4. If access token expired/invalid: attempts refresh with refresh token
            - On success: executes the decorated function
            - On failure: prints session error message and returns None

        :param func: The function to be decorated and protected with authentication
        :type func: Callable
        :return: A wrapped function that performs authentication checks before execution
        :rtype: Callable
        """
        # Injecte user: Collaborator ??
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if local token file exist and if data format is valid
            if not tokens_exist():
                # New login
                print("\n⚠️  Authentication required for this command.")
                return None

            # Load existing tokens
            tokens = load_tokens()
            if not tokens:
                return None

            # Check access token validity
            try:
                TokenServices.verify_token(tokens['access_token'], 'access')

                # User authenticated, proceed with function

                return func(*args, **kwargs)

            except AuthenticationError as e:
                # Token invalid or expired
                error_msg = str(e).lower()

                if "expired" in error_msg or "invalid" in error_msg:
                    try:
                        # Try to refresh tokens
                        TokenServices.refresh_access_token(
                            tokens['refresh_token'])

                        # User authenticated, proceed with function
                        return func(*args, **kwargs)

                    except AuthenticationError:
                        # Refresh failed, new login required
                        pass

                # New login
                print("\n⚠️  Session expired or invalid. Please login again.")
                return None

        return wrapper
