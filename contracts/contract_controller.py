from sqlalchemy.orm import Session, joinedload

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


class ContractController:
    """ """

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None
        self.on_consult_customer_callback = None
        self.on_consult_event_callback = None
        self.on_create_event_callback = None

    def start(
        self,
        contract_id=None,
        on_back=None,
        on_consult_customer=None,
        on_consult_event=None,
        on_create_event=None,
    ):
        self.on_back_callback = on_back
        self.on_consult_customer_callback = on_consult_customer
        self.on_consult_event_callback = on_consult_event
        self.on_create_event_callback = on_create_event
        contracts = self.get_all_contracts()
        self.push_contract_screen(
            contracts=contracts, contract_id=contract_id
        )

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from contract menu"""
        match user_choice:
            case "create_contract":
                self.push_create_contract_screen()
            case ("update_contract", contract_id):
                self.push_update_contract_screen(contract_id=contract_id)
            case ("create_event", contract_id):
                self.on_create_event_callback(contract_id=contract_id)
                return
            case ("consult_customer", customer_id):
                self.on_consult_customer_callback(customer_id)
                return
            case ("consult_event", event_id):
                self.on_consult_event_callback(event_id=event_id)
                return
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
                return
            case "quit":
                self.epic_events_app.exit()

    def get_all_contracts(self) -> list[Contract]:
        """
        Returns all contracts from the database.
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
        """
        Returns all unsigned contracts from the database.
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
        """
        Returns all unpaid contracts from the database.
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
        return self.session.query(Customer).all()

    def load_contract_data_for_update(self, contract_id: int):
        """ """
        contract = (
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
        """
        Push the contract list screen onto the application screen stack.

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
        :return: None
        :rtype: None
        """
        contracts_screen = ContractScreen(
            contracts=contracts,
            contract_id=contract_id,
            filtered_table_signature=filtered_table_signature,
            filtered_table_payment=filtered_table_payment,
        )
        self.epic_events_app.push_screen(
            contracts_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_create_contract_screen(self) -> None:
        """
        Push the create contract screen onto the application screen stack.

        Retrieves all customers and instantiates a :class:`CreateContractScreen`
        with them, then pushes it onto the application's screen stack with a callback
        to :meth:`create_contract`.

        :return: None
        :rtype: None
        """
        all_customers = self.get_all_customers()
        create_contract_screen = CreateContractScreen(all_customers)
        self.epic_events_app.push_screen(
            create_contract_screen,
            callback=self.create_contract,
        )

    @AuthenticationServices.check_authentication
    def push_update_contract_screen(self, contract_id: int) -> None:
        """
        Push the update contract screen onto the application screen stack.

        Retrieves all customers and loads the data for the contract to update,
        instantiates an :class:`UpdateContractScreen` with this data, and pushes
        it onto the application's screen stack with a callback to :meth:`update_contract`.

        :param contract_id: The ID of the contract to update. The corresponding
            contract data will be loaded and pre-filled in the update form.
        :type contract_id: int
        :return: None
        :rtype: None
        """
        all_customers = self.get_all_customers()
        contract_to_update = self.load_contract_data_for_update(
            contract_id
        )
        update_contract_screen = UpdateContractScreen(
            contract_to_update, all_customers
        )
        self.epic_events_app.push_screen(
            update_contract_screen,
            callback=self.update_contract,
        )

    @AuthenticationServices.check_authentication
    def create_contract(self, new_contract_data):
        """ """
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
        new_contract_status = ContractStatus.PENDING

        contract = Contract(
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
    def update_contract(self, updated_contract_data):
        """ """
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
        self.epic_events_app.notify(
            "Contract successfully updated", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
            on_create_event=self.on_create_event_callback,
        )

    def _handle_auth_failure(self, error: AuthenticationError | None):
        """Handles authentication failure"""
        # if error:
        #     self.epic_events_app.notify(
        #         f"[bold red]⚠️  {error!s}[/bold red]", severity="error"
        #     )
        self.on_back_callback()
