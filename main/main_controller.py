from authentication.authentication_controller import (
    AuthenticationController,
)
from collaborators.collaborator_controller import CollaboratorController
from collaborators.collaborator_model import Collaborator
from contracts.contract_controller import ContractController
from customers.customer_controller import CustomerController
from events.event_controller import EventController
from main.main_view import (
    AuthenticatedMainScreen,
    UnauthenticatedMainScreen,
)


class MainController:
    """ """

    def __init__(self, epic_events_app, session):
        # Models
        self.epic_events_app = epic_events_app
        self.session = session
        self.authentication_controller = AuthenticationController(
            self.epic_events_app, self.session
        )
        self.customer_controller = CustomerController(
            self.epic_events_app, self.session
        )
        self.event_controller = EventController(
            self.epic_events_app, self.session
        )
        self.collaborator_controller = CollaboratorController(
            self.epic_events_app, self.session
        )
        self.contract_controller = ContractController(
            self.epic_events_app, self.session
        )

    def start(self):
        """ """
        if self.authentication_controller.is_authenticated():
            self.display_authenticated_main_menu()

        else:
            self.display_unauthenticated_main_menu()

    def handle_user_choice(self, user_choice: str):
        """Callback when user choses from main menu"""
        match user_choice:
            case "login":
                self.authentication_controller.login(
                    on_success=self.display_authenticated_main_menu,
                    on_cancel=self.display_unauthenticated_main_menu,
                )
            case "events":
                self.push_event_screen()
            case "contracts":
                self.push_contract_screen()
            case "customers":
                self.push_customer_screen()
            case "collaborators":
                self.push_collaborator_screen()
            case "profile":
                # self.profile_controller.start()
                pass
            case "logout":
                self.authentication_controller.logout()
                self.display_unauthenticated_main_menu()
            case "quit":
                self.epic_events_app.exit()

    def display_authenticated_main_menu(self):
        """ """
        # Get user_name
        user: Collaborator = self.authentication_controller.get_user_info()
        user_name = user.first_name

        authenticated_main_screen = AuthenticatedMainScreen(user_name)
        self.epic_events_app.push_screen(
            authenticated_main_screen, callback=self.handle_user_choice
        )

    def display_unauthenticated_main_menu(self):
        """ """
        unauthenticated_main_screen = UnauthenticatedMainScreen()
        self.epic_events_app.push_screen(
            unauthenticated_main_screen, callback=self.handle_user_choice
        )

    def push_event_screen(self, event_id: int | None = None):
        """Call the start method of event_controller,
        with optional event_id argument
        and mandatory callback methods arguments.
        """
        self.event_controller.start(
            event_id=event_id,
            on_back=self.display_authenticated_main_menu,
            on_consult_customer=self.push_customer_screen,
            on_consult_contract=self.push_contract_screen,
        )

    def push_contract_screen(self, contract_id: int | None = None):
        """Call the start method of contract_controller,
        with optional contract_id argument
        and mandatory callback methods arguments.
        """
        self.contract_controller.start(
            contract_id=contract_id,
            on_back=self.display_authenticated_main_menu,
            on_consult_customer=self.push_customer_screen,
            on_consult_event=self.push_event_screen,
        )

    def push_customer_screen(self, customer_id: int | None = None):
        """Call the start method of customer_controller,
        with optional customer_id argument
        and mandatory callback method argument.
        """
        self.customer_controller.start(
            customer_id=customer_id,
            on_back=self.display_authenticated_main_menu,
        )

    def push_collaborator_screen(self):
        """Call the start method of collaborator_controller,
        with mandatory callback methods arguments.
        """
        self.collaborator_controller.start(
            on_back=self.display_authenticated_main_menu,
            on_consult_customer=self.push_customer_screen,
            on_consult_event=self.push_event_screen,
        )
