import os
from typing import Final

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


class Settings:
    """Central configuration class for the EpicEvents CRM application.

    Aggregates all application settings from environment variables and provides
    them as class attributes. Settings are organized into logical sections:

    **Database Configuration**
        - Host, port, credentials, and database name for MySQL connection
        - Provides a computed DB_URL property for SQLAlchemy

    **Sentry Configuration**
        - DSN (Data Source Name) for error logging integration

    **Security Configuration**
        - Secret key for cryptographic operations

    **JWT Configuration**
        - Algorithm, token expiration times, and key paths for JWT authentication

    **Environment Configuration**
        - Current deployment environment (development, staging, production)

    **Collaborator Passwords**
        - Default passwords for collaborator seeding during development

    All settings can be configured via environment variables or use sensible defaults
    for development. The class provides a secure __repr__ that hides sensitive data.

    Example:
        >>> from config.settings import settings
        >>> settings.DB_HOST
        'localhost'
        >>> settings.DB_URL
        'mysql+mysqlconnector://user:password@localhost:3306/database'
    """

    # --- Database ---
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    """Database server hostname.

    :vartype: str
    """
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    """Database server port number.

    :vartype: int
    """
    DB_USER: str = os.getenv("DB_USER", "")
    """Database username for authentication.

    :vartype: str
    """
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    """Database password for authentication.

    :vartype: str
    """
    DB_NAME: str = os.getenv("DB_NAME", "")
    """Name of the database to connect to.

    :vartype: str
    """

    @property
    def DB_URL(self) -> str:
        """Generate the SQLAlchemy connection URL for MySQL database.

        Constructs a MySQL connection string using the configured database
        credentials and connection parameters.

        :return: Complete MySQL connection URL for SQLAlchemy.
        :rtype: str

        Example:
            >>> settings.DB_URL
            'mysql+mysqlconnector://user:password@localhost:3306/mydatabase'
        """
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- Sentry (error logs) ---
    SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")
    """Sentry Data Source Name (DSN) for error tracking.

    If provided, enables Sentry error logging. Set to None or empty string
    to disable Sentry integration.

    :vartype: str | None
    """

    # --- Security ---
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "default_key_change_in_production"
    )
    """Secret key for cryptographic operations.

    Used for signing sessions, JWT tokens (when not using RSA), and other
    security-sensitive operations. Must be kept secret in production.

    :vartype: str
    """

    # --- JWT ---
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")
    """JWT signing algorithm.

    Supported algorithms: RS256, ES256, HS256. RS256 (RSA with SHA-256)
    is recommended for production.

    :vartype: str
    """
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    )
    """Access token expiration time in minutes.

    Short-lived tokens for authentication. Default is 15 minutes.

    :vartype: int
    """
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )
    """Refresh token expiration time in days.

    Long-lived tokens for obtaining new access tokens. Default is 7 days.

    :vartype: int
    """
    JWT_PRIVATE_KEY_PATH: str = os.getenv("JWT_PRIVATE_KEY_PATH", "")
    """Path to the RSA private key file for JWT signing.

    Required when using RSA-based algorithms (RS256, RS384, RS512).
    The private key must be in PEM format.

    :vartype: str
    """
    JWT_PUBLIC_KEY_PATH: str = os.getenv("JWT_PUBLIC_KEY_PATH", "")
    """Path to the RSA public key file for JWT verification.

    Required when using RSA-based algorithms (RS256, RS384, RS512).
    The public key must be in PEM format.

    :vartype: str
    """

    # --- Environment ---
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    """Current deployment environment.

    Possible values: 'development', 'staging', 'production'.
    Affects logging level, error reporting, and security settings.

    :vartype: str
    """

    def __repr__(self) -> str:
        """Return a secure string representation of the Settings object.

        Intentionally excludes sensitive information like passwords and secret keys
        from the representation to prevent accidental exposure in logs or debug output.

        :return: String representation with non-sensitive settings only.
        :rtype: str
        """
        return (
            f"Settings("
            f"DB_HOST={self.DB_HOST!r}, "
            f"DB_PORT={self.DB_PORT!r}, "
            f"DB_NAME={self.DB_NAME!r}, "
            f"ENVIRONMENT={self.ENVIRONMENT!r}"
            f")"
        )

    # --- Collaborator passwords (for seeding) ---
    COLLAB_PASSWORD_1: str = os.getenv(
        "COLLAB_PASSWORD_1", "default_password"
    )
    """Default password for collaborator 1 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_2: str = os.getenv(
        "COLLAB_PASSWORD_2", "default_password"
    )
    """Default password for collaborator 2 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_3: str = os.getenv(
        "COLLAB_PASSWORD_3", "default_password"
    )
    """Default password for collaborator 3 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_4: str = os.getenv(
        "COLLAB_PASSWORD_4", "default_password"
    )
    """Default password for collaborator 4 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_5: str = os.getenv(
        "COLLAB_PASSWORD_5", "default_password"
    )
    """Default password for collaborator 5 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_6: str = os.getenv(
        "COLLAB_PASSWORD_6", "default_password"
    )
    """Default password for collaborator 6 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_7: str = os.getenv(
        "COLLAB_PASSWORD_7", "default_password"
    )
    """Default password for collaborator 7 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_8: str = os.getenv(
        "COLLAB_PASSWORD_8", "default_password"
    )
    """Default password for collaborator 8 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_9: str = os.getenv(
        "COLLAB_PASSWORD_9", "default_password"
    )
    """Default password for collaborator 9 (seeding only).

    :vartype: str
    """
    COLLAB_PASSWORD_10: str = os.getenv(
        "COLLAB_PASSWORD_10", "default_password"
    )
    """Default password for collaborator 10 (seeding only).

    :vartype: str
    """


# Global instance to import elsewhere
settings: Final[Settings] = Settings()
