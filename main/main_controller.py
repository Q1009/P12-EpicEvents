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
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
)


class MainController:
    """Central controller for the EpicEvents CRM application.

    Coordinates between all feature controllers (authentication, customers,
    contracts, events, collaborators) and manages the application flow.
    Handles user navigation between different screens based on authentication
    status and user choices.

    :param epic_events_app: The main Textual application instance for screen management.
    :type epic_events_app: textual.app.App
    :param session: The SQLAlchemy database session for database operations.
    :type session: sqlalchemy.orm.Session

    .. note::
        This controller implements the MVC pattern by delegating specific
        functionalities to dedicated controllers while maintaining the overall
        application state and navigation flow.
    """

    def __init__(self, epic_events_app, session):
        """Initialize the MainController with application and database session.

        Creates instances of all feature controllers (authentication, customers,
        contracts, events, collaborators) and stores references to the main
        application and database session.

        :param epic_events_app: The main Textual application instance.
        :type epic_events_app: textual.app.App
        :param session: SQLAlchemy database session for database operations.
        :type session: sqlalchemy.orm.Session
        """
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
        """Start the main application flow.

        Determines which main menu to display based on the current
        authentication status. If the user is authenticated, displays
        the authenticated menu; otherwise, displays the unauthenticated menu.
        """
        if self.authentication_controller.is_authenticated():
            self.display_authenticated_main_menu()
        else:
            self.display_unauthenticated_main_menu()

    def handle_user_choice(self, user_choice: str):
        """Process user selection from the main menu.

        Routes the user's menu choice to the appropriate controller method
        or action. Handles login, logout, navigation to feature screens,
        and application exit.

        :param user_choice: The user's selected menu option.
        :type user_choice: str

        .. note::
            Available choices include: login, logout, events, contracts,
            customers, collaborators, profile, and quit.
        """
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

    @AuthenticationServices.check_authentication
    def display_authenticated_main_menu(self):
        """Display the main menu for authenticated users.

        Retrieves the current user's information and pushes the authenticated
        main screen onto the application stack with a callback for handling
        user choices.

        :raises AuthenticationError: If the user's authentication token is invalid.
        """
        user: Collaborator = self.authentication_controller.get_user_info()

        if user is None:
            self._handle_auth_failure(None)
            return

        user_name = user.first_name
        authenticated_main_screen = AuthenticatedMainScreen(user_name)
        self.epic_events_app.push_screen(
            authenticated_main_screen, callback=self.handle_user_choice
        )

    def display_unauthenticated_main_menu(self):
        """Display the main menu for unauthenticated users.

        Pushes the unauthenticated main screen onto the application stack
        with a callback for handling user choices. This menu typically
        provides login and quit options.
        """
        unauthenticated_main_screen = UnauthenticatedMainScreen()
        self.epic_events_app.push_screen(
            unauthenticated_main_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_event_screen(
        self, event_id: int | None = None, contract_id: int | None = None
    ):
        """Display the event management screen.

        Delegates to the event controller to start the event management
        interface with optional event and contract IDs for pre-loading.

        :param event_id: Optional ID of the event to display or edit.
        :type event_id: int | None
        :param contract_id: Optional ID of the associated contract.
        :type contract_id: int | None
        :raises AuthenticationError: If the user is not authenticated.
        """
        self.event_controller.start(
            event_id=event_id,
            contract_id=contract_id,
            on_back=self.display_authenticated_main_menu,
            on_consult_customer=self.push_customer_screen,
            on_consult_contract=self.push_contract_screen,
        )

    @AuthenticationServices.check_authentication
    def push_contract_screen(self, contract_id: int | None = None):
        """Display the contract management screen.

        Delegates to the contract controller to start the contract management
        interface with an optional contract ID for pre-loading.

        :param contract_id: Optional ID of the contract to display or edit.
        :type contract_id: int | None
        :raises AuthenticationError: If the user is not authenticated.
        """
        self.contract_controller.start(
            contract_id=contract_id,
            on_back=self.display_authenticated_main_menu,
            on_consult_customer=self.push_customer_screen,
            on_consult_event=self.push_event_screen,
            on_create_event=self.push_event_screen,
        )

    @AuthenticationServices.check_authentication
    def push_customer_screen(self, customer_id: int | None = None):
        """Display the customer management screen.

        Delegates to the customer controller to start the customer management
        interface with an optional customer ID for pre-loading.

        :param customer_id: Optional ID of the customer to display or edit.
        :type customer_id: int | None
        :raises AuthenticationError: If the user is not authenticated.
        """
        self.customer_controller.start(
            customer_id=customer_id,
            on_back=self.display_authenticated_main_menu,
        )

    @AuthenticationServices.check_authentication
    def push_collaborator_screen(self):
        """Display the collaborator management screen.

        Delegates to the collaborator controller to start the collaborator
        management interface.

        :raises AuthenticationError: If the user is not authenticated.
        """
        self.collaborator_controller.start(
            on_back=self.display_authenticated_main_menu,
            on_consult_customer=self.push_customer_screen,
            on_consult_event=self.push_event_screen,
        )

    def _handle_auth_failure(self, error: AuthenticationError | None):
        """Handle authentication failure scenarios.

        Displays an error notification if an authentication error occurred
        and returns the user to the unauthenticated main menu.

        :param error: The authentication error that occurred, if any.
        :type error: AuthenticationError | None
        """
        if error:
            self.epic_events_app.notify(
                f"[bold red]⚠️  {error!s}[/bold red]", severity="error"
            )
        self.display_unauthenticated_main_menu()
