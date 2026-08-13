from .authentication_controller import AuthenticationController
from views import MainScreen
from services import AuthenticationError

class MainController:
    """
    """
    def __init__(self, epic_events_app, session):
        # Models
        self.epic_events_app = epic_events_app
        self.session = session
        # Views
        # self.main_screen = main_screen

    def start(self):
        """
        """
        authentication_controller = AuthenticationController(
            self.epic_events_app,
            self.session
        )

        if not authentication_controller.is_authenticated():
            authentication_controller.login()

        # User logged in
        user_name = 'Quentin'
        main_screen = MainScreen(user_name)
        self.epic_events_app.push_screen(main_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice: str):
        """Callback when user choses from main menu"""
        match user_choice:
            case 'Events':
                # Retourner Events au controlleur
                # self.event_controller.start()
                self.epic_events_app.notify('Events', severity='information')
            case 'Contracts':
                # Retourner Contracts au controlleur
                # self.contract_controller.start()
                self.epic_events_app.notify('Contracts', severity='warning')
            case 'Customers':
                # Retourner Customers au controlleur
                # self.customer_controller.start()
                self.epic_events_app.notify('Customers', severity='error')
            case 'Collaborators':
                # Retourner Customers au controlleur
                # self.collaborator_controller.start()
                self.epic_events_app.notify('Collaborators', severity='information')
            case 'Profile':
                # Retourner Profile au controlleur
                # self.profile_controller.start()
                self.epic_events_app.notify('Profile', severity='information')
                self.epic_events_app.exit()
