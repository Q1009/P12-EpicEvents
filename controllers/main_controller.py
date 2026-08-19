from .authentication_controller import AuthenticationController
from .event_controller import EventController
from views import AuthenticatedMainScreen, UnauthenticatedMainScreen
from services import AuthenticationError

class MainController:
    """
    """
    def __init__(self, epic_events_app, session):
        # Models
        self.epic_events_app = epic_events_app
        self.session = session
        self.authentication_controller = AuthenticationController(
            self.epic_events_app,
            self.session
        )
        self.event_controller = EventController(
            self.epic_events_app,
            self.session
        )
        # Views
        # self.main_screen = main_screen

    def start(self):
        """
        """
        if self.authentication_controller.is_authenticated():
            self.display_authenticated_main_menu()

        else:
            self.display_unauthenticated_main_menu()

        # User logged in
        # user_name = 'Quentin'
        # main_screen = MainScreen(user_name)
        # self.epic_events_app.push_screen(main_screen, callback=self.handle_user_choice)

    def display_authenticated_main_menu(self):
        """
        """
        # Get user_name
        user_name = self.authentication_controller.get_user_info()
        # user_name = 'Quentin'
        authenticated_main_screen = AuthenticatedMainScreen(user_name)
        self.epic_events_app.push_screen(authenticated_main_screen, callback=self.handle_user_choice)

    def display_unauthenticated_main_menu(self):
        """
        """
        unauthenticated_main_screen = UnauthenticatedMainScreen()
        self.epic_events_app.push_screen(unauthenticated_main_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice: str):
        """Callback when user choses from main menu"""
        match user_choice:
            case 'Login':
                # Retourner Login au controlleur
                self.authentication_controller.login(on_success=self.display_authenticated_main_menu, on_cancel=self.display_unauthenticated_main_menu)
            case 'Events':
                # Retourner Events au controlleur
                self.epic_events_app.notify('Events', severity='information')
                self.event_controller.start()
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
            case 'Logout':
                # Logout from the application
                self.authentication_controller.logout()
                self.display_unauthenticated_main_menu()
            case 'Quit':
                # Quit application
                self.epic_events_app.exit()
