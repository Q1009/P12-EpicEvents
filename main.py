from config.settings import settings

def main():
    print(f"🚀 Starting in : {settings.ENVIRONMENT} mode")
    print(f"🗄️ Connection to : {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # Checks that required variables are present
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not getattr(settings, var)]
    if missing:
        raise ValueError(f"Missing variables in .env : {', '.join(missing)}")

    # ...

if __name__ == "__main__":
    main()