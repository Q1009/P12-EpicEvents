import os

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Settings:
    """Class centralizing all application configuration."""

    # --- Database ---
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")

    @property
    def DB_URL(self) -> str:
        """Generates the SQLAlchemy URL for MySQL."""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- Sentry (error logs) ---
    SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")

    # --- Security ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_key_change_in_production")

    # --- JWT ---
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    JWT_PRIVATE_KEY_PATH: str = os.getenv("JWT_PRIVATE_KEY_PATH")
    JWT_PUBLIC_KEY_PATH: str = os.getenv("JWT_PUBLIC_KEY_PATH")

    # --- Environment ---
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development|staging|production

    def __repr__(self) -> str:
        # Displays a secure representation (without passwords)
        return (
            f"Settings("
            f"DB_HOST={self.DB_HOST!r}, "
            f"DB_PORT={self.DB_PORT!r}, "
            f"DB_NAME={self.DB_NAME!r}, "
            f"ENVIRONMENT={self.ENVIRONMENT!r}"
            f")"
        )

    # --- Collaborator passwords (for seeding) ---
    COLLAB_PASSWORD_1: str = os.getenv("COLLAB_PASSWORD_1", "default_password")
    COLLAB_PASSWORD_2: str = os.getenv("COLLAB_PASSWORD_2", "default_password")
    COLLAB_PASSWORD_3: str = os.getenv("COLLAB_PASSWORD_3", "default_password")
    COLLAB_PASSWORD_4: str = os.getenv("COLLAB_PASSWORD_4", "default_password")
    COLLAB_PASSWORD_5: str = os.getenv("COLLAB_PASSWORD_5", "default_password")
    COLLAB_PASSWORD_6: str = os.getenv("COLLAB_PASSWORD_6", "default_password")
    COLLAB_PASSWORD_7: str = os.getenv("COLLAB_PASSWORD_7", "default_password")
    COLLAB_PASSWORD_8: str = os.getenv("COLLAB_PASSWORD_8", "default_password")
    COLLAB_PASSWORD_9: str = os.getenv("COLLAB_PASSWORD_9", "default_password")
    COLLAB_PASSWORD_10: str = os.getenv("COLLAB_PASSWORD_10", "default_password")

# Global instance to import elsewhere
settings = Settings()