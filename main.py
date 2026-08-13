from config.settings import settings
from controllers import MainController
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

class EpicEventsCRM(App):
    """
    CLI of EpicEvents CRM
    """
    TITLE = 'Epic Events CRM'
    BINDINGS = [('q', 'quit', 'Quitter')]

    def __init__(self):
        super().__init__()
        # Initialize DB connection with session
        self.engine = create_engine(settings.DB_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Initialize MVC
        self.main_controller = MainController(self, self.session)
        

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS CRM")
        yield Footer(show_command_palette=False)

    def on_ready(self):
        self.theme = 'nord'
        self.main_controller.start()

    def on_exit(self):
        self.session.close()
        self.engine.dispose()

def main():
    print(f"🚀 Starting in : {settings.ENVIRONMENT} mode")
    print(f"🗄️ Connection to : {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # Checks that required variables are present
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [var for var in required_vars if not getattr(settings, var)]
    if missing:
        raise ValueError(f"Missing variables in .env : {', '.join(missing)}")

    # # ...
    # engine = create_engine(settings.DB_URL)
    # Session = sessionmaker(bind=engine)
    # #==
    # session = Session()
    # epic_events_app = EpicEventsCRM()
    # main_view = MainView(epic_events_app)
    # main_controller = MainController(session, main_view)
    # epic_events_app.run()
    # main_controller.start()
    # #==
    # session.close()
    # engine.dispose()

    app = EpicEventsCRM()
    app.run()

if __name__ == "__main__":
    main()