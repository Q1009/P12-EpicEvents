from config.settings import settings

def main():
    print(f"🚀 Démarrage en mode : {settings.ENVIRONMENT}")
    print(f"🗄️ Connexion à : {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # Vérifie que les variables obligatoires sont présentes
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not getattr(settings, var)]
    if missing:
        raise ValueError(f"Variables manquantes dans .env : {', '.join(missing)}")

    # ...

if __name__ == "__main__":
    main()