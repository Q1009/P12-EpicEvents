from sqlalchemy.orm import Session
from models import Event
from views import EventScreen, CreateEventScreen
from services import AuthenticationServices
from .authentication_controller import AuthenticationController

class EventController:

    def __init__(self, epic_events_app, session):
        self.session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None

    def start(self, on_back):
        self.on_back_callback = on_back
        events = self.get_all_events(self.session)
        events_screen = EventScreen(events)
        self.epic_events_app.push_screen(events_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice: str):
        """Callback when user choses from main menu"""
        match user_choice:
            case 'create_event':
                self.epic_events_app.notify('Create Event', severity='error')
                create_event_screen = CreateEventScreen()
                self.epic_events_app.push_screen(create_event_screen, callback=self.handle_user_choice)
            case 'display_all_events':
                all_events = self.get_all_events(self.session)
                all_events_screen = EventScreen(all_events)
                self.epic_events_app.push_screen(all_events_screen, callback=self.handle_user_choice)
            case 'display_own_events':
                # user_id = self.get_user_id()
                own_events = self.get_events_by_user_id(self.session, user_id=4)
                own_events_screen = EventScreen(own_events)
                self.epic_events_app.push_screen(own_events_screen, callback=self.handle_user_choice)
            case 'display_unsupported_events':
                unsupported_events = self.get_unsupported_events(self.session)
                unsupported_events_screen = EventScreen(unsupported_events)
                self.epic_events_app.push_screen(unsupported_events_screen, callback=self.handle_user_choice)
            case 'back':
                if self.on_back_callback:
                    self.on_back_callback()
            case 'quit':
                self.epic_events_app.exit()

    def get_all_events(self, session: Session) -> list[Event]:
        """
        """
        return session.query(Event).all()

    def get_events_by_user_id(self, session: Session, user_id: int) -> list[Event]:
        """
        Returns all events where support_representative_id matches the given user_id.
        """
        return session.query(Event).filter(Event.support_representative_id == user_id).all()

    def get_unsupported_events(self, session: Session) -> list[Event]:
        """
        Returns all events that have no support_representative_id assigned.
        """
        return session.query(Event).filter(Event.support_representative_id.is_(None)).all()

    def create_event(self):
        pass

    def update_event(self):
        pass

    def delete_event(self):
        pass