import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app import EpicEventsCRM
from config.settings import settings


def main():
    print(f"🚀 Starting in : {settings.ENVIRONMENT} mode")
    print(
        f"🗄️ Connection to : {settings.DB_HOST}:"
        f"{settings.DB_PORT}/{settings.DB_NAME}"
    )

    # Sentry init
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        enable_logs=True,
        traces_sample_rate=1.0,
        integrations=[SqlalchemyIntegration()],
    )

    # Checks that required variables are present
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not getattr(settings, var)]
    if missing:
        raise ValueError(
            f"Missing variables in .env : {', '.join(missing)}"
        )

    app = EpicEventsCRM()
    app.run()


if __name__ == "__main__":
    main()
