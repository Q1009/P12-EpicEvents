from sqlalchemy.orm import Session
from models import Event
from views import EventScreen

class EventController:

    def __init__(self, epic_events_app, session):
        self.session = session
        self.epic_events_app = epic_events_app

    def start(self):
        events = self.get_all_events(self.session)
        event_screen = EventScreen(events)
        self.epic_events_app.push_screen(event_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice: str):
        """Callback when user choses from main menu"""
        match user_choice:
            case 'Login':
                # Retourner Login au controlleur
                self.authentication_controller.login(on_success=self.display_authenticated_main_menu, on_cancel=self.display_unauthenticated_main_menu)
            case 'Quit':
                # Retourner Events au controlleur
                # self.event_controller.start()
                self.epic_events_app.exit()

    def get_all_events(self, session: Session) -> list[Event]:
        """
        """
        return session.query(Event).all()