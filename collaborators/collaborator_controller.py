from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import sentry_sdk
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from collaborators.collaborator_model import (
    Collaborator,
    Department,
)
from collaborators.collaborator_view import (
    CollaboratorScreen,
    CreateCollaboratorScreen,
    UpdateCollaboratorScreen,
)
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
    PasswordServices,
)

if TYPE_CHECKING:
    from textual.app import App


class CollaboratorController:
    """Controller for managing collaborators in the EpicEvents CRM.

    Handles all collaborator-related operations including listing, creating,
    updating, and deleting collaborators. Coordinates between the database
    (via SQLAlchemy session), the views, and other controllers.

    :param epic_events_app: The main Textual application instance
    for screen management.
    :type epic_events_app: textual.app.App
    :param session: The SQLAlchemy database session for database operations.
    :type session: sqlalchemy.orm.Session

    .. note::
        This controller uses the MVC pattern, receiving user input from views
        and updating both the model (database) and views accordingly. It also
        integrates with Sentry for logging collaborator management events.
    """

    def __init__(self, epic_events_app: "App", session: Session) -> None:
        """Initialize the CollaboratorController with application and
        database session.

        Stores references to the main application and database session, and
        initializes callback attributes for navigation between screens.

        :param epic_events_app: The main Textual application instance.
        :type epic_events_app: textual.app.App
        :param session: SQLAlchemy database session for database operations.
        :type session: sqlalchemy.orm.Session
        """
        self.session: Session = session
        self.epic_events_app: App = epic_events_app
        self.on_back_callback: Callable[[], None] | None = None
        self.on_consult_customer_callback: Callable[[int], None] | None = (
            None
        )
        self.on_consult_event_callback: Callable[[int], None] | None = None

    def start(
        self,
        on_back: Callable[[], None] | None = None,
        on_consult_customer: Callable[[int], None] | None = None,
        on_consult_event: Callable[[int], None] | None = None,
    ) -> None:
        """Start the collaborator management workflow.

        Stores callback references for navigation and pushes the collaborator
        list screen with all collaborators.

        :param on_back: Callback function to execute when user returns
        to previous screen.
        :type on_back: Callable[[], None] | None
        :param on_consult_customer: Callback for navigating to customer screen.
            Called with customer ID.
        :type on_consult_customer: Callable[[int], None] | None
        :param on_consult_event: Callback for navigating to event screen.
            Called with event ID.
        :type on_consult_event: Callable[[int], None] | None
        """
        self.on_back_callback = on_back
        self.on_consult_customer_callback = on_consult_customer
        self.on_consult_event_callback = on_consult_event
        collaborators: list[Collaborator] = self.get_all_collaborators()
        self.push_collaborator_screen(collaborators=collaborators)

    def handle_user_choice(
        self, user_choice: str | tuple[str, Any]
    ) -> None:
        """Process user selection from the collaborator menu.

        Routes the user's menu choice to the appropriate action or screen.
        Handles navigation between screens, creating/updating/deleting
        collaborators, and application exit.

        :param user_choice: The user's selected menu option,
            which can be a simple string or a tuple containing the action
            and additional parameters.
        :type user_choice: str | tuple[str, Any]

        .. note::
            Available choices include: create_collaborator,
            update_collaborator, delete_collaborator, consult_customer,
            consult_event, back, and quit.
        """
        match user_choice:
            case "create_collaborator":
                self.push_create_collaborator_screen()
            case ("update_collaborator", collaborator_id):
                self.push_update_collaborator_screen(
                    collaborator_id=collaborator_id
                )
            case ("delete_collaborator", collaborator_id):
                self.delete_collaborator(collaborator_id)
            case ("consult_customer", customer_id):
                if self.on_consult_customer_callback:
                    self.on_consult_customer_callback(customer_id)
            case ("consult_event", event_id):
                if self.on_consult_event_callback:
                    self.on_consult_event_callback(event_id)
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
            case "quit":
                self.epic_events_app.exit()

    def get_all_collaborators(self) -> list[Collaborator]:
        """Retrieve all collaborators from the database.

        Returns all :class:`Collaborator` objects with their associated
        department, customers, and events loaded via eager loading.

        :return: List of all Collaborator objects with related data.
        :rtype: list[Collaborator]
        """
        return (
            self.session.query(Collaborator)
            .options(
                joinedload(Collaborator.department),
                joinedload(Collaborator.customers),
                joinedload(Collaborator.events),
            )
            .all()
        )

    def get_all_departments(self) -> list[Department]:
        """Retrieve all departments from the database.

        :return: List of all Department objects.
        :rtype: list[Department]
        """
        return self.session.query(Department).all()

    def load_collaborator_data_for_update(
        self, collaborator_id: int
    ) -> dict[str, Any]:
        """Load collaborator data for the update form.

        Retrieves a collaborator by ID and returns its data as a dictionary
        suitable for pre-filling an update form.

        :param collaborator_id: The ID of the collaborator to load.
        :type collaborator_id: int
        :return: Dictionary containing all collaborator fields
        for the update form.
        :rtype: dict[str, Any]
        """
        collaborator: Collaborator | None = (
            self.session.query(Collaborator)
            .filter(Collaborator.id == collaborator_id)
            .first()
        )

        return {
            "collaborator_id": collaborator.id,
            "collaborator_first_name": collaborator.first_name,
            "collaborator_last_name": collaborator.last_name,
            "department": collaborator.department,
        }

    @AuthenticationServices.check_authentication
    def push_collaborator_screen(
        self,
        collaborators: list[Collaborator],
        collaborator_id: int | None = None,
    ) -> None:
        """Push the collaborator list screen onto the application screen stack.

        Instantiates a :class:`CollaboratorScreen` with the provided
        collaborators and pushes it onto the application's screen stack
        with a callback
        to :meth:`handle_user_choice`.

        :param collaborators: List of :class:`Collaborator` objects to display
            in the screen table.
        :type collaborators: list[Collaborator]
        :param collaborator_id: Optional ID of a collaborator to pre-select
        in the table.
            Currently not used in screen instantiation but available
            for future use.
        :type collaborator_id: int | None
        """
        current_user: Collaborator | None = (
            AuthenticationServices.get_user_info(self.session)
        )
        collaborators_screen = CollaboratorScreen(
            collaborators=collaborators,
            user=current_user,
        )
        self.epic_events_app.push_screen(
            collaborators_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_create_collaborator_screen(self) -> None:
        """Push the create collaborator screen onto
        the application screen stack.

        Retrieves all departments and instantiates
        a :class:`CreateCollaboratorScreen` with them,
        then pushes it onto the application's screen stack
        with a callback
        to :meth:`create_collaborator`.
        """
        all_departments: list[Department] = self.get_all_departments()
        create_collaborator_screen = CreateCollaboratorScreen(
            departments=all_departments
        )
        self.epic_events_app.push_screen(
            create_collaborator_screen,
            callback=self.create_collaborator,
        )

    @AuthenticationServices.check_authentication
    def push_update_collaborator_screen(
        self, collaborator_id: int
    ) -> None:
        """Push the update collaborator screen onto
        the application screen stack.

        Retrieves all departments, loads the data for
        the collaborator to update, instantiates
        an :class:`UpdateCollaboratorScreen` with this data,
        and pushes it onto the application's screen stack with
        a callback to :meth:`update_collaborator`.

        :param collaborator_id: The ID of the collaborator to update.
            The corresponding collaborator data will be loaded
            and pre-filled in the update form.
        :type collaborator_id: int
        """
        all_departments: list[Department] = self.get_all_departments()
        collaborator_to_update: dict[str, Any] = (
            self.load_collaborator_data_for_update(collaborator_id)
        )
        update_collaborator_screen = UpdateCollaboratorScreen(
            collaborator_to_update, all_departments
        )
        self.epic_events_app.push_screen(
            update_collaborator_screen,
            callback=self.update_collaborator,
        )

    @AuthenticationServices.check_authentication
    def create_collaborator(
        self, new_collaborator_data: dict[str, Any] | None
    ) -> None:
        """Create a new collaborator in the database.

        Handles the collaborator creation form submission.
        If creation is cancelled, returns to the collaborator list.
        Otherwise, processes the form data:
        - Generates email from first and last name
        - Hashes the password
        - Creates the collaborator object
        - Saves to database
        - Logs the event to Sentry

        :param new_collaborator_data: Dictionary containing collaborator
            data from the form, or None if creation was cancelled.
        :type new_collaborator_data: dict[str, Any] | None
        """
        current_user: Collaborator | None = (
            AuthenticationServices.get_user_info(self.session)
        )
        # If creation is cancelled
        if not new_collaborator_data:
            self.epic_events_app.notify(
                "Collaborator creation cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
            )
            return

        # Else, transform raw data (dict) from submitted form
        # Email (firstname.lastname@epicevents.com)
        new_collaborator_email: str = (
            (new_collaborator_data["collaborator_first_name"]).lower()
            + "."
            + (new_collaborator_data["collaborator_last_name"]).lower()
            + "@epicevents.com"
        )
        # Hash password
        new_collaborator_password: str = PasswordServices.hash_password(
            new_collaborator_data["password"]
        )

        collaborator: Collaborator = Collaborator(
            last_name=new_collaborator_data["collaborator_last_name"],
            first_name=new_collaborator_data["collaborator_first_name"],
            email=new_collaborator_email,
            password=new_collaborator_password,
            department=new_collaborator_data["department"],
        )

        self.session.add(collaborator)
        self.session.commit()
        # Sentry log
        if current_user:
            sentry_sdk.capture_event(
                {
                    "level": "info",
                    "message": (
                        f"Collaborator created: {collaborator.first_name} "
                        f"{collaborator.last_name}"
                    ),
                    "extra": {
                        "action": "create",
                        "collaborator_id": collaborator.id,
                        "first_name": collaborator.first_name,
                        "last_name": collaborator.last_name,
                        "email": collaborator.email,
                        "department": collaborator.department.name.value,
                        "created_by_id": current_user.id,
                        "created_by_name": (
                            f"{current_user.first_name} "
                            f"{current_user.last_name}"
                        ),
                    },
                    "tags": {
                        "module": "collaborators",
                        "action": "create",
                    },
                }
            )
        # App notification
        self.epic_events_app.notify(
            "Collaborator successfully created", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
        )

    @AuthenticationServices.check_authentication
    def update_collaborator(
        self, updated_collaborator_data: dict[str, Any] | None
    ) -> None:
        """Update an existing collaborator in the database.

        Handles the collaborator update form submission.
        If update is cancelled, returns to the collaborator list.
        Otherwise, processes the form data:
        - Generates new email from updated first and last name
        - Updates the collaborator in database
        - Logs the event to Sentry

        :param updated_collaborator_data: Dictionary containing
            updated collaborator data from the form,
            or None if update was cancelled.
        :type updated_collaborator_data: dict[str, Any] | None
        """
        if not updated_collaborator_data:
            self.epic_events_app.notify(
                "Collaborator update cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
            )
            return

        current_user: Collaborator | None = (
            AuthenticationServices.get_user_info(self.session)
        )
        updated_collaborator: Collaborator | None = (
            self.session.query(Collaborator)
            .filter(Collaborator.id == updated_collaborator_data["id"])
            .first()
        )

        # Update email
        updated_collaborator_email: str = (
            (updated_collaborator_data["first_name"]).lower()
            + "."
            + (updated_collaborator_data["last_name"]).lower()
            + "@epicevents.com"
        )

        self.session.query(Collaborator).filter(
            Collaborator.id == updated_collaborator_data["id"]
        ).update(
            {
                "first_name": updated_collaborator_data["first_name"],
                "last_name": updated_collaborator_data["last_name"],
                "email": updated_collaborator_email,
                "department_id": updated_collaborator_data[
                    "department"
                ].id,
            }
        )

        self.session.commit()
        # Sentry log
        if current_user and updated_collaborator:
            sentry_sdk.capture_event(
                {
                    "level": "info",
                    "message": (
                        f"Collaborator updated: ID {updated_collaborator.id}"
                    ),
                    "extra": {
                        "action": "update",
                        "collaborator_id": updated_collaborator.id,
                        "updated_by_id": current_user.id,
                        "updated_by_name": (
                            f"{current_user.first_name} "
                            f"{current_user.last_name}"
                        ),
                    },
                    "tags": {
                        "module": "collaborators",
                        "action": "update",
                    },
                }
            )
        # App notification
        self.epic_events_app.notify(
            "Collaborator successfully updated", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
        )

    @AuthenticationServices.check_authentication
    def delete_collaborator(self, collaborator_id: int | None) -> None:
        """Delete a collaborator from the database.

        Handles the collaborator deletion request. If deletion is cancelled,
        returns to the collaborator list. Otherwise, deletes the collaborator
        from the database and refreshes the list.
        If the collaborator is referenced by foreign keys
        (e.g., as sales_representative of a Customer or
        support_representative of an Event), the deletion is aborted
        and the user is notified.

        :param collaborator_id: The ID of the collaborator to delete.
        :type collaborator_id: int | None
        """
        if not collaborator_id:
            self.epic_events_app.notify(
                "Collaborator delete cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
            )
            return

        try:
            self.session.query(Collaborator).filter(
                Collaborator.id == collaborator_id
            ).delete()

            self.session.commit()
            self.epic_events_app.notify(
                "Collaborator successfully deleted", severity="information"
            )
        except IntegrityError as e:
            self.session.rollback()
            self.epic_events_app.notify(
                (
                    f"Cannot delete collaborator: "
                    f"{str(e.orig) if e.orig else 'FK constraint violation'}"
                ),
                severity="error",
            )

        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
        )

    def _handle_auth_failure(
        self, error: AuthenticationError | None
    ) -> None:
        """Handle authentication failure scenarios.

        Called when authentication fails. Displays an error notification if
        an error occurred and returns to the previous screen
        via the back callback.

        :param error: The authentication error that occurred, if any.
        :type error: AuthenticationError | None
        """
        if error:
            self.epic_events_app.notify(
                f"[bold red]⚠️  {error!s}[/bold red]", severity="error"
            )
        if self.on_back_callback:
            self.on_back_callback()
