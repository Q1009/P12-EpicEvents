from dotenv import load_dotenv
import os
from typing import Optional

# Charger les variables du fichier .env
load_dotenv()

class Settings:
    """Classe centralisant toute la configuration de l'application."""

    # --- Base de données ---
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")

    @property
    def DB_URL(self) -> str:
        """Génère l'URL SQLAlchemy pour MySQL."""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- Sentry (logs d'erreurs) ---
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

    # --- Sécurité ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cle_par_defaut_a_changer_en_prod")

    # --- Environnement ---
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development|staging|production

    def __repr__(self) -> str:
        # Affiche une représentation sécurisée (sans les mots de passe)
        return (
            f"Settings("
            f"DB_HOST={self.DB_HOST!r}, "
            f"DB_PORT={self.DB_PORT!r}, "
            f"DB_NAME={self.DB_NAME!r}, "
            f"ENVIRONMENT={self.ENVIRONMENT!r}"
            f")"
        )

# Instance globale à importer ailleurs
settings = Settings()