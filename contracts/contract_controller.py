from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import sentry_sdk
from sqlalchemy.orm import Session, joinedload

from collaborators.collaborator_model import Collaborator
from contracts.contract_model import (
    Contract,
    ContractStatus,
)
from contracts.contract_view import (
    ContractScreen,
    CreateContractScreen,
    UpdateContractScreen,
)
from customers.customer_model import Customer
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
)

if TYPE_CHECKING:
    from textual.app import App


class ContractController:
    """Controller for managing contracts in the EpicEvents CRM.

    Handles all contract-related operations including listing, creating, updating,
    and filtering contracts. Coordinates between the database (via SQLAlchemy session),
    the views, and other controllers.

    :param epic_events_app: The main Textual application instance for screen management.
    :type epic_events_app: textual.app.App
    :param session: The SQLAlchemy database session for database operations.
    :type session: sqlalchemy.orm.Session

    .. note::
        This controller uses the MVC pattern, receiving user input from views
        and updating both the model (database) and views accordingly. It also
        integrates with Sentry for logging important contract events like signing.
    """

    def __init__(self, epic_events_app: "App", session: Session) -> None:
        """Initialize the ContractController with application and database session.

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
        self.on_create_event_callback: Callable[[int], None] | None = None

    def start(
        self,
        contract_id: int | None = None,
        on_back: Callable[[], None] | None = None,
        on_consult_customer: Callable[[int], None] | None = None,
        on_consult_event: Callable[[int], None] | None = None,
        on_create_event: Callable[[int], None] | None = None,
    ) -> None:
        """Start the contract management workflow.

        Stores callback references for navigation and pushes the contract list screen
        with all contracts, optionally pre-selecting a specific contract.

        :param contract_id: Optional ID of a contract to pre-select in the list.
        :type contract_id: int | None
        :param on_back: Callback function to execute when user returns to previous screen.
        :type on_back: Callable[[], None] | None
        :param on_consult_customer: Callback for navigating to customer screen.
            Called with customer ID.
        :type on_consult_customer: Callable[[int], None] | None
        :param on_consult_event: Callback for navigating to event screen.
            Called with event ID.
        :type on_consult_event: Callable[[int], None] | None
        :param on_create_event: Callback for creating an event from a contract.
            Called with contract ID.
        :type on_create_event: Callable[[int], None] | None
        """
        self.on_back_callback = on_back
        self.on_consult_customer_callback = on_consult_customer
        self.on_consult_event_callback = on_consult_event
        self.on_create_event_callback = on_create_event
        contracts = self.get_all_contracts()
        self.push_contract_screen(
            contracts=contracts, contract_id=contract_id
        )

    def handle_user_choice(
        self, user_choice: str | tuple[str, Any]
    ) -> None:
        """Process user selection from the contract menu.

        Routes the user's menu choice to the appropriate action or screen.
        Handles navigation between screens, filtering, creating events from contracts,
        and application exit.

        :param user_choice: The user's selected menu option, which can be a simple
            string or a tuple containing the action and additional parameters.
        :type user_choice: str | tuple[str, Any]

        .. note::
            Available choices include: create_contract, update_contract, create_event,
            consult_customer, consult_event, filter_unsigned_contracts,
            filter_unpaid_contracts, filter_reset, back, and quit.
        """
        match user_choice:
            case "create_contract":
                self.push_create_contract_screen()
            case ("update_contract", contract_id):
                self.push_update_contract_screen(contract_id=contract_id)
            case ("create_event", contract_id):
                if self.on_create_event_callback:
                    self.on_create_event_callback(contract_id=contract_id)
            case ("consult_customer", customer_id):
                if self.on_consult_customer_callback:
                    self.on_consult_customer_callback(customer_id)
            case ("consult_event", event_id):
                if self.on_consult_event_callback:
                    self.on_consult_event_callback(event_id=event_id)
            case ("filter_unsigned_contracts", filtered_table):
                contracts = self.get_unsigned_contracts()
                self.push_contract_screen(
                    contracts=contracts,
                    filtered_table_signature=filtered_table,
                )
            case ("filter_unpaid_contracts", filtered_table):
                contracts = self.get_unpaid_contracts()
                self.push_contract_screen(
                    contracts=contracts,
                    filtered_table_payment=filtered_table,
                )
            case ("filter_reset", filtered_table):
                contracts = self.get_all_contracts()
                self.push_contract_screen(
                    contracts=contracts,
                    filtered_table_signature=filtered_table,
                    filtered_table_payment=filtered_table,
                )
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
            case "quit":
                self.epic_events_app.exit()

    def get_all_contracts(self) -> list[Contract]:
        """Retrieve all contracts from the database.

        Returns all :class:`Contract` objects with their associated customer
        and event loaded via eager loading.

        :return: List of all Contract objects with related data.
        :rtype: list[Contract]
        """
        return (
            self.session.query(Contract)
            .options(
                joinedload(Contract.customer),
                joinedload(Contract.event),
            )
            .all()
        )

    def get_unsigned_contracts(self) -> list[Contract]:
        """Retrieve all unsigned contracts from the database.

        Returns all :class:`Contract` objects that have not been signed yet,
        with their associated customer and event loaded via eager loading.

        :return: List of unsigned Contract objects with related data.
        :rtype: list[Contract]
        """
        return (
            self.session.query(Contract)
            .options(
                joinedload(Contract.customer),
                joinedload(Contract.event),
            )
            .filter(Contract.status != ContractStatus.SIGNED)
            .all()
        )

    def get_unpaid_contracts(self) -> list[Contract]:
        """Retrieve all unpaid contracts from the database.

        Returns all :class:`Contract` objects that still have an outstanding
        balance (amount_due > 0), with their associated customer and event
        loaded via eager loading.

        :return: List of unpaid Contract objects with related data.
        :rtype: list[Contract]
        """
        return (
            self.session.query(Contract)
            .options(
                joinedload(Contract.customer),
                joinedload(Contract.event),
            )
            .filter(Contract.amount_due != 0)
            .all()
        )

    def get_all_customers(self) -> list[Customer]:
        """Retrieve all customers from the database.

        :return: List of all Customer objects.
        :rtype: list[Customer]
        """
        return self.session.query(Customer).all()

    def load_contract_data_for_update(
        self, contract_id: int
    ) -> dict[str, Any]:
        """Load contract data for the update form.

        Retrieves a contract by ID and returns its data as a dictionary
        suitable for pre-filling an update form.

        :param contract_id: The ID of the contract to load.
        :type contract_id: int
        :return: Dictionary containing all contract fields for the update form.
        :rtype: dict[str, Any]
        """
        contract: Contract | None = (
            self.session.query(Contract)
            .filter(Contract.id == contract_id)
            .first()
        )

        return {
            "contract_id": contract.id,
            "contract_total_amount": contract.total_amount,
            "contract_amount_due": contract.amount_due,
            "contract_status": contract.status,
            "contract_customer": contract.customer,
        }

    @AuthenticationServices.check_authentication
    def push_contract_screen(
        self,
        contracts: list[Contract],
        contract_id: int | None = None,
        filtered_table_signature: bool = False,
        filtered_table_payment: bool = False,
    ) -> None:
        """Push the contract list screen onto the application screen stack.

        Instantiates a :class:`ContractScreen` with the provided contracts, optional
        pre-selected contract ID, and filter states, then pushes it onto the
        application's screen stack with a callback to :meth:`handle_user_choice`.

        :param contracts: List of :class:`Contract` objects to display in the screen table.
        :type contracts: list[Contract]
        :param contract_id: Optional ID of a contract to pre-select in the table.
            If provided, the corresponding contract will be highlighted. Defaults to None.
        :type contract_id: int | None
        :param filtered_table_signature: Flag indicating whether the table is filtered
            to show only unsigned contracts. Defaults to False.
        :type filtered_table_signature: bool
        :param filtered_table_payment: Flag indicating whether the table is filtered
            to show only unpaid contracts. Defaults to False.
        :type filtered_table_payment: bool
        """
        current_user: Collaborator | None = (
            AuthenticationServices.get_user_info(self.session)
        )
        contracts_screen = ContractScreen(
            contracts=contracts,
            user=current_user,
            contract_id=contract_id,
            filtered_table_signature=filtered_table_signature,
            filtered_table_payment=filtered_table_payment,
        )
        self.epic_events_app.push_screen(
            contracts_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_create_contract_screen(self) -> None:
        """Push the create contract screen onto the application screen stack.

        Retrieves all customers and instantiates a :class:`CreateContractScreen`
        with them, then pushes it onto the application's screen stack with a callback
        to :meth:`create_contract`.
        """
        all_customers: list[Customer] = self.get_all_customers()
        create_contract_screen = CreateContractScreen(all_customers)
        self.epic_events_app.push_screen(
            create_contract_screen,
            callback=self.create_contract,
        )

    @AuthenticationServices.check_authentication
    def push_update_contract_screen(self, contract_id: int) -> None:
        """Push the update contract screen onto the application screen stack.

        Retrieves all customers and loads the data for the contract to update,
        instantiates an :class:`UpdateContractScreen` with this data, and pushes
        it onto the application's screen stack with a callback to :meth:`update_contract`.

        :param contract_id: The ID of the contract to update. The corresponding
            contract data will be loaded and pre-filled in the update form.
        :type contract_id: int
        """
        all_customers: list[Customer] = self.get_all_customers()
        contract_to_update: dict[str, Any] = (
            self.load_contract_data_for_update(contract_id)
        )
        update_contract_screen = UpdateContractScreen(
            contract_to_update, all_customers
        )
        self.epic_events_app.push_screen(
            update_contract_screen,
            callback=self.update_contract,
        )

    @AuthenticationServices.check_authentication
    def create_contract(
        self, new_contract_data: dict[str, Any] | None
    ) -> None:
        """Create a new contract in the database.

        Handles the contract creation form submission. If creation is cancelled,
        returns to the contract list. Otherwise, processes the form data, creates
        the contract object with PENDING status, and saves it to the database.

        :param new_contract_data: Dictionary containing contract data from the form,
            or None if creation was cancelled.
        :type new_contract_data: dict[str, Any] | None
        """
        # If creation is cancelled
        if not new_contract_data:
            self.epic_events_app.notify(
                "Contract creation cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
                on_create_event=self.on_create_event_callback,
            )
            return

        # Else, transform raw data (dict) from submitted form
        # Status: always pending at creation
        new_contract_status: ContractStatus = ContractStatus.PENDING

        contract: Contract = Contract(
            total_amount=new_contract_data["contract_total_amount"],
            amount_due=new_contract_data["contract_amount_due"],
            status=new_contract_status,
            customer=new_contract_data["contract_customer"],
        )

        self.session.add(contract)
        self.session.commit()
        self.epic_events_app.notify(
            "Contract successfully created", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
            on_create_event=self.on_create_event_callback,
        )

    @AuthenticationServices.check_authentication
    def update_contract(
        self, updated_contract_data: dict[str, Any] | None
    ) -> None:
        """Update an existing contract in the database.

        Handles the contract update form submission. If update is cancelled,
        returns to the contract list. Otherwise, processes the form data and
        updates the corresponding contract in the database. Logs signed contracts
        to Sentry for audit purposes.

        :param updated_contract_data: Dictionary containing updated contract data
            from the form, or None if update was cancelled.
        :type updated_contract_data: dict[str, Any] | None
        """
        current_user: Collaborator | None = (
            AuthenticationServices.get_user_info(self.session)
        )
        if not updated_contract_data:
            self.epic_events_app.notify(
                "Contract update cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
                on_create_event=self.on_create_event_callback,
            )
            return

        updated_contract: Contract | None = (
            self.session.query(Contract)
            .filter(Contract.id == updated_contract_data["contract_id"])
            .first()
        )

        self.session.query(Contract).filter(
            Contract.id == updated_contract_data["contract_id"]
        ).update(
            {
                "total_amount": updated_contract_data[
                    "contract_total_amount"
                ],
                "amount_due": updated_contract_data["contract_amount_due"],
                "status": updated_contract_data["contract_status"],
                "customer_id": updated_contract_data[
                    "contract_customer"
                ].id,
            }
        )

        self.session.commit()
        # Sentry log
        if (
            updated_contract_data["contract_status"]
            == ContractStatus.SIGNED
        ):
            sentry_sdk.capture_event(
                {
                    "level": "info",
                    "message": f"Contract signed: ID {updated_contract.id} (Customer: {updated_contract.customer.first_name} {updated_contract.customer.last_name})",
                    "extra": {
                        "action": "sign",
                        "contract_id": updated_contract.id,
                        "signed_by_id": current_user.id,
                        "signed_by_name": f"{current_user.first_name} {current_user.last_name}",
                    },
                    "tags": {
                        "module": "contracts",
                        "action": "sign",
                        "status": "signed",
                    },
                }
            )
        # App notification
        self.epic_events_app.notify(
            "Contract successfully updated", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
            on_create_event=self.on_create_event_callback,
        )

    def _handle_auth_failure(
        self, error: AuthenticationError | None
    ) -> None:
        """Handle authentication failure scenarios.

        Called when authentication fails. Returns to the previous screen
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
