from config.settings import settings
from controllers import MainController
from views import MainView
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def main():
    print(f"🚀 Starting in : {settings.ENVIRONMENT} mode")
    print(f"🗄️ Connection to : {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # Checks that required variables are present
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not getattr(settings, var)]
    if missing:
        raise ValueError(f"Missing variables in .env : {', '.join(missing)}")

    # ...
    engine = create_engine(settings.DB_URL)
    Session = sessionmaker(bind=engine)
    #==
    session = Session()
    main_view = MainView()
    main_controller = MainController(session, main_view)
    main_controller.run()
    #==
    session.close()
    engine.dispose()

if __name__ == "__main__":
    main()