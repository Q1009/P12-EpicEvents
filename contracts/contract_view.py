from typing import Any, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import DescendantBlur
from textual.reactive import reactive
from textual.screen import Screen
from textual.validation import Length, Number
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    Static,
)
from textual.widgets._select import SelectCurrent

from collaborators.collaborator_model import Collaborator
from contracts.contract_model import Contract, ContractStatus
from customers.customer_model import Customer
from permissions.permission_model import Permission
from services.date_services import format_french_datetime
from services.permission_services import PermissionServices


class ContractScreen(Screen):
    """Screen for displaying and managing contracts in the EpicEvents CRM.

    Provides a comprehensive view of all contracts with filtering capabilities,
    detailed information display for selected contracts, and navigation options
    for creating, updating, and consulting related entities.

    :param contracts: List of Contract objects to display in the table.
    :type contracts: list[Contract]
    :param user: The currently authenticated collaborator.
    :type user: Collaborator
    :param contract_id: Optional ID of a contract to pre-select in the table.
    :type contract_id: int | None
    :param filtered_table_signature: Flag indicating if table shows only unsigned contracts.
    :type filtered_table_signature: bool
    :param filtered_table_payment: Flag indicating if table shows only unpaid contracts.
    :type filtered_table_payment: bool
    """

    SUB_TITLE = "CONTRACTS"
    CSS_PATH = "../styles/contract_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("s", "filter_unsigned_contracts", "Show Unsigned Contracts"),
        ("p", "filter_unpaid_contracts", "Show Unpaid Contracts"),
        ("r", "filter_reset", "Show All Contracts"),
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_contract_id: reactive[int | None] = reactive(None)

    BUTTON_PERMISSIONS: ClassVar[dict[str, set[Permission]]] = {
        "create-contract": {Permission.CREATE_CONTRACT},
        "update-contract": {
            Permission.UPDATE_ALL_CONTRACTS,
            Permission.UPDATE_OWN_CONTRACTS,
        },
        "create-event": {Permission.CREATE_EVENT},
        "consult-customer": {Permission.READ_ALL_CUSTOMERS},
        "consult-event": {Permission.READ_ALL_EVENTS},
    }

    def __init__(
        self,
        contracts: list[Contract],
        user: Collaborator,
        contract_id: int | None = None,
        filtered_table_signature: bool = False,
        filtered_table_payment: bool = False,
    ) -> None:
        """Initialize the ContractScreen with contracts and user data.

        :param contracts: List of Contract objects to display in the table.
        :type contracts: list[Contract]
        :param user: The currently authenticated collaborator.
        :type user: Collaborator
        :param contract_id: Optional ID of a contract to pre-select in the table.
        :type contract_id: int | None
        :param filtered_table_signature: Flag for unsigned contracts filter.
        :type filtered_table_signature: bool
        :param filtered_table_payment: Flag for unpaid contracts filter.
        :type filtered_table_payment: bool
        """
        super().__init__()
        self.contracts: list[Contract] = contracts
        self.pre_selected_contract_id: int | None = contract_id
        self.current_user: Collaborator = user
        self.selected_customer_id: int | None = None
        self.selected_event_id: int | None = None
        self.filtered_table_signature: bool = filtered_table_signature
        self.filtered_table_payment: bool = filtered_table_payment

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with data tables (contracts, customer,
        event) and progress bar, action buttons, and footer.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="contract-main-container"):
            yield DataTable(id="contracts-table")
            yield DataTable(id="contract-customer-table")
            yield ProgressBar(
                id="contract-payment-progressbar", show_eta=False
            )
            yield DataTable(id="contract-event-table")
            with Container(classes="contract-buttons-container"):
                yield Button(
                    "Create Contract",
                    id="create-contract",
                    variant="primary",
                )
                yield Button(
                    "Update Contract",
                    id="update-contract",
                    variant="warning",
                )
                yield Button(
                    "Create Event",
                    id="create-event",
                    variant="success",
                )
            with Container(classes="customer-event-buttons-container"):
                yield Button(
                    "Consult Customer",
                    id="consult-customer",
                    variant="primary",
                )
                yield Button(
                    "Consult Event",
                    id="consult-event",
                    variant="warning",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Builds all data tables, sets button states based on permissions,
        and handles pre-selected contract if provided.
        """
        self.build_contracts_table()
        self.build_contract_customer_table()
        self.build_contract_payment_progressbar()
        self.build_contract_event_table()
        self.set_button_state("create-contract")
        self.set_button_state("update-contract")
        self.set_button_state("create-event")
        self.set_button_state("consult-customer")
        self.set_button_state("consult-event")

        # Setting initial selected_contract_id: triggering the watcher
        # If a contract id was given to constructor
        if self.pre_selected_contract_id is not None:
            contract = next(
                (
                    c
                    for c in self.contracts
                    if c.id == self.pre_selected_contract_id
                ),
                None,
            )
            if contract:
                # Moving cursor will update selected_contract_id
                row_index = self.contracts.index(contract)
                self.query_one("#contracts-table", DataTable).move_cursor(
                    row=row_index
                )
        # If not, use first contract
        elif self.contracts:
            self.selected_contract_id = self.contracts[0].id

    def build_contracts_table(self) -> None:
        """Build and configure the contracts data table.

        Sets up column headers and loads contract data into the table.
        """
        table = self.query_one("#contracts-table", DataTable)
        table.border_title = "Contracts"
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Configure table columns
        table.add_column("ID", key="contract_id")
        table.add_column(
            "Sales Representative", key="sales_representative"
        )
        table.add_column("Total Amount", key="total_amount")
        table.add_column("Amount Due", key="amount_due")
        table.add_column("Status", key="status")
        table.add_column("Created At", key="created_at")

        table.loading = True
        self.load_contracts(table)

    def load_contracts(self, table: DataTable) -> None:
        """Load contract data into the contracts table.

        Populates the table with contract data including sales representative
        names and formatted creation dates.

        :param table: The DataTable widget to populate with contract data.
        :type table: DataTable
        """
        table.clear()

        for contract in self.contracts:
            # Sales Representative
            sales_representative = (
                contract.customer.sales_representative.first_name
                + " "
                + contract.customer.sales_representative.last_name
            )
            # Date conversion
            created_at = format_french_datetime(contract.created_at)

            table.add_row(
                contract.id,
                sales_representative,
                contract.total_amount,
                contract.amount_due,
                contract.status.name,
                created_at,
            )

        table.loading = False

    def build_contract_customer_table(self) -> None:
        """Build and configure the customer data table.

        Sets up column headers for displaying associated customer information.
        """
        table = self.query_one("#contract-customer-table", DataTable)
        table.border_title = "Associated Customer"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="customer_id")
        table.add_column("First Name", key="customer_first_name")
        table.add_column("Last Name", key="customer_last_name")

        table.loading = True

    def load_contract_customer(
        self, table: DataTable, contract: Contract
    ) -> None:
        """Load customer data for the selected contract.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param contract: The Contract object containing customer data.
        :type contract: Contract
        """
        table.clear()

        if contract.customer:
            table.add_row(
                contract.customer.id,
                contract.customer.first_name,
                contract.customer.last_name,
            )

        table.loading = False

    def build_contract_event_table(self) -> None:
        """Build and configure the event data table.

        Sets up column headers for displaying associated event information.
        """
        table = self.query_one("#contract-event-table", DataTable)
        table.border_title = "Associated Event"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="event_id")
        table.add_column("Name", key="event_name")

        table.loading = True

    def load_contract_event(
        self, table: DataTable, contract: Contract
    ) -> None:
        """Load event data for the selected contract.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param contract: The Contract object containing event data.
        :type contract: Contract
        """
        table.clear()

        if contract.event:
            table.add_row(
                contract.event.id,
                contract.event.name,
            )

        table.loading = False

    def build_contract_payment_progressbar(self) -> None:
        """Build and configure the payment progress bar.

        Sets up the progress bar for displaying payment progress.
        """
        progress_bar = self.query_one(
            "#contract-payment-progressbar", ProgressBar
        )
        progress_bar.border_title = "Amount Paid - %"

    def load_contract_payment(
        self, progressbar: ProgressBar, contract: Contract
    ) -> None:
        """Load payment data for the selected contract.

        Updates the progress bar to show the payment percentage based on
        total amount and amount due.

        :param progressbar: The ProgressBar widget to update.
        :type progressbar: ProgressBar
        :param contract: The Contract object containing payment data.
        :type contract: Contract
        """
        total_amount = contract.total_amount
        amount_due = contract.amount_due
        paid_amount = total_amount - amount_due
        progressbar.update(total=total_amount, progress=paid_amount)

    def set_button_state(self, button_id: str) -> None:
        """Set button visibility based on user permissions.

        Checks if the current user has the required permissions for the button
        and shows/hides it accordingly.

        :param button_id: The ID of the button to check.
        :type button_id: str
        """
        if self.current_user is None:
            return

        required_permissions = self.BUTTON_PERMISSIONS.get(
            button_id, set()
        )
        missing_permissions = [
            permission
            for permission in required_permissions
            if not PermissionServices.has_permission(
                user=self.current_user, permission=permission
            )
        ]
        if missing_permissions:
            self.query_one(f"#{button_id}", Button).display = False
        else:
            self.query_one(f"#{button_id}", Button).display = True

    def watch_selected_contract_id(self, new_id: int | None) -> None:
        """Watcher that loads associated data based on the selected contract.

        Updates customer table, event table, payment progress bar, and button states
        when a new contract is selected in the contracts table.

        :param new_id: The ID of the newly selected contract.
        :type new_id: int | None
        """
        contract_customer_table = self.query_one(
            "#contract-customer-table", DataTable
        )
        contract_event_table = self.query_one(
            "#contract-event-table", DataTable
        )
        contract_payment_progressbar = self.query_one(
            "#contract-payment-progressbar", ProgressBar
        )

        if new_id is None:
            contract_customer_table.clear()
            self.selected_customer_id = None
            contract_event_table.clear()
            self.selected_event_id = None
            contract_payment_progressbar.update()
            return

        # Get contract by ID
        selected_contract: Contract | None = next(
            (c for c in self.contracts if c.id == new_id), None
        )

        if selected_contract:
            # Load associated widgets based on selected_contract
            self.load_contract_customer(
                contract_customer_table, selected_contract
            )
            self.load_contract_event(
                contract_event_table, selected_contract
            )
            self.load_contract_payment(
                contract_payment_progressbar, selected_contract
            )
            # Update other selected_attributes_id
            self.selected_customer_id = selected_contract.customer.id
            if selected_contract.event:
                self.selected_event_id = selected_contract.event.id
            else:
                self.selected_event_id = None
        else:
            self.selected_customer_id = None
            self.selected_event_id = None

        # Enable or disable buttons
        self.update_consult_customer_button_state()
        self.update_consult_event_button_state()
        self.update_create_event_button_state(selected_contract)
        self.update_update_contract_button_state(selected_contract)

    def update_consult_customer_button_state(self) -> None:
        """Update the state of the consult customer button based on permissions.

        Checks if the current user has permission to read all customers and
        if a customer is selected, then updates button visibility.
        """
        consult_customer_button = self.query_one(
            "#consult-customer", Button
        )
        if PermissionServices.has_permission(
            self.current_user, Permission.READ_ALL_CUSTOMERS
        ):
            consult_customer_button.display = (
                self.selected_customer_id is not None
            )
            return

        consult_customer_button.display = False

    def update_consult_event_button_state(self) -> None:
        """Update the state of the consult event button based on permissions.

        Checks if the current user has permission to read all events and
        if an event is selected, then updates button visibility.
        """
        consult_event_button = self.query_one("#consult-event", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.READ_ALL_EVENTS
        ):
            consult_event_button.display = (
                self.selected_event_id is not None
            )
            return

        consult_event_button.display = False

    def update_create_event_button_state(
        self, selected_contract: Contract | None
    ) -> None:
        """Update the state of the create event button based on permissions.

        Checks if the current user has permission to create events and
        if they are the sales representative for the selected signed contract
        without an existing event.

        :param selected_contract: The currently selected contract.
        :type selected_contract: Contract | None
        """
        create_event_button = self.query_one("#create-event", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.CREATE_EVENT
        ):
            if selected_contract is not None:
                create_event_button.display = (
                    selected_contract.customer.sales_representative_id
                    == self.current_user.id
                    and selected_contract.status == ContractStatus.SIGNED
                    and self.selected_event_id is None
                )
            return

        create_event_button.display = False

    def update_update_contract_button_state(
        self, selected_contract: Contract | None
    ) -> None:
        """Update the state of the update contract button based on permissions.

        Checks if the current user has permission to update all contracts
        or only their own contracts, and updates button visibility accordingly.

        :param selected_contract: The currently selected contract.
        :type selected_contract: Contract | None
        """
        update_contract_button = self.query_one("#update-contract", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_ALL_CONTRACTS
        ):
            update_contract_button.display = True
            return

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_OWN_CONTRACTS
        ):
            if selected_contract is not None:
                update_contract_button.display = (
                    selected_contract.customer.sales_representative_id
                    == self.current_user.id
                )
            return

        update_contract_button.display = False

    def check_action(self, action: str, parameters: Any) -> bool | None:
        """Check if an action should be allowed based on current filter state.

        Prevents toggling filters that are already active.

        :param action: The action to check.
        :type action: str
        :param parameters: Additional parameters for the action.
        :type parameters: Any
        :return: True if action should proceed, False if it should be blocked.
        :rtype: bool | None
        """
        # Returns False if
        # table is filtered by signature and action is filter_unsigned
        # or
        # if table is filtered by payment and action is filter_unpaid
        # or
        # if table is not filtered and action is filter_reset
        # Returns True in other cases
        return not (
            (
                action == "filter_unsigned_contracts"
                and self.filtered_table_signature
            )
            or (
                action == "filter_unpaid_contracts"
                and self.filtered_table_payment
            )
            or (
                action == "filter_reset"
                and not (
                    self.filtered_table_signature
                    or self.filtered_table_payment
                )
            )
        )

    def action_filter_unsigned_contracts(self) -> None:
        """Filter DataTable to show unsigned contracts.

        Dismisses the screen with a tuple indicating to show only unsigned contracts.
        """
        self.dismiss(("filter_unsigned_contracts", True))

    def action_filter_unpaid_contracts(self) -> None:
        """Filter DataTable to show unpaid contracts.

        Dismisses the screen with a tuple indicating to show only unpaid contracts.
        """
        self.dismiss(("filter_unpaid_contracts", True))

    def action_filter_reset(self) -> None:
        """Filter DataTable to show all contracts.

        Dismisses the screen with a tuple indicating to reset all filters.
        """
        self.dismiss(("filter_reset", False))

    def action_go_back(self) -> None:
        """Return to previous screen.

        Dismisses the screen with "back" action.
        """
        self.dismiss("back")

    @on(DataTable.RowHighlighted, "#contracts-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Save highlighted contract id.

        Updates the selected_contract_id reactive variable when a row is highlighted
        in the contracts table, which triggers the watcher to update related tables.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        contracts_table = self.query_one("#contracts-table", DataTable)
        # Get value from the cell
        contract_id = contracts_table.get_cell(
            event.row_key, "contract_id"
        )
        # Update selected_attribute_id
        self.selected_contract_id = contract_id

    @on(Button.Pressed, "#create-contract")
    def go_create_contract(self) -> None:
        """Navigate to create contract screen.

        Dismisses the screen with "create_contract" action.
        """
        self.dismiss("create_contract")

    @on(Button.Pressed, "#update-contract")
    def go_update_contract(self) -> None:
        """Navigate to update contract screen for selected contract.

        Dismisses the screen with a tuple containing action and contract ID.
        """
        self.dismiss(("update_contract", self.selected_contract_id))

    @on(Button.Pressed, "#create-event")
    def go_create_event(self) -> None:
        """Navigate to create event screen for selected contract.

        Dismisses the screen with a tuple containing action and contract ID.
        """
        self.dismiss(("create_event", self.selected_contract_id))

    @on(Button.Pressed, "#consult-customer")
    def go_consult_customer(self) -> None:
        """Navigate to consult customer screen.

        Dismisses the screen with a tuple containing action and customer ID.
        """
        self.dismiss(("consult_customer", self.selected_customer_id))

    @on(Button.Pressed, "#consult-event")
    def go_consult_event(self) -> None:
        """Navigate to consult event screen.

        Dismisses the screen with a tuple containing action and event ID.
        """
        self.dismiss(("consult_event", self.selected_event_id))


class CreateContractScreen(Screen):
    """Screen for creating a new contract in the EpicEvents CRM.

    Provides a form for entering contract details including total amount,
    amount due, and associated customer.

    :param customers: List of existing customers to choose from.
    :type customers: list[Customer]
    """

    SUB_TITLE = "CREATE CONTRACT"
    CSS_PATH = "../styles/create_contract_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self, customers: list[Customer]) -> None:
        """Initialize the CreateContractScreen with available customers.

        :param customers: List of existing customers to choose from.
        :type customers: list[Customer]
        """
        super().__init__()
        self.customers: list[Customer] = customers
        self.contract_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (contract data,
        customer selection), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="create-contract-main-container"):
            with Container(
                id="contract-data",
                classes="contract-data-input-container",
            ):
                yield Label(
                    "Contract Total Amount ($):", classes="form-label"
                )
                yield Input(
                    placeholder="1500",
                    id="contract_total_amount",
                    type="number",
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                        Number(
                            minimum=0,
                            failure_description="Value cannot be negative.",
                        ),
                    ],
                )
                yield Label(
                    "Contract Amount Due ($):", classes="form-label"
                )
                yield Input(
                    placeholder="1500",
                    id="contract_amount_due",
                    type="number",
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                        Number(
                            minimum=0,
                            failure_description="Value cannot be negative.",
                        ),
                    ],
                )
            with Container(
                id="contract-customer",
                classes="contract-customer-input-container",
            ):
                customer_options = [
                    (
                        (customer.first_name + " " + customer.last_name),
                        customer,
                    )
                    for customer in self.customers
                ]
                yield Select(
                    customer_options,
                    id="contract-customer-select",
                    prompt="Select a customer",
                )
            with Container(classes="create-contract-buttons-container"):
                yield Button(
                    "Create",
                    id="create",
                    variant="primary",
                    classes="create-contract-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="create-contract-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for contract data and customer selection containers.
        """
        contract_data_container = self.query_one(
            "#contract-data", Container
        )
        contract_customer_container = self.query_one(
            "#contract-customer", Container
        )
        contract_data_container.border_title = "Contract Data"
        contract_customer_container.border_title = "Customer Selection"

    def watch_is_form_valid(self, is_valid: bool) -> None:
        """Disable or enable Create button based on form validation.

        :param is_valid: Whether the form is currently valid.
        :type is_valid: bool
        """
        create_button = self.query_one("#create", Button)
        create_button.disabled = not is_valid

    def _validate_form(self) -> None:
        """Validates every input field of the form.

        Updates the is_form_valid reactive variable based on validation results
        of all input and select fields.
        """
        widget_inputs = [
            self.query_one("#contract_total_amount", Input),
            self.query_one("#contract_amount_due", Input),
        ]

        widget_selects = [
            self.query_one("#contract-customer-select", Select),
        ]

        # Check that all input fields are valid
        all_inputs_valid = all(
            widget_input.validate(widget_input.value).is_valid
            for widget_input in widget_inputs
        )
        # Check that all select fields are valid
        all_selects_valid = all(
            not select.is_blank() for select in widget_selects
        )

        # Update reactive variable triggering watcher
        all_valid = all_inputs_valid and all_selects_valid
        self.is_form_valid = all_valid

    @on(Input.Changed)
    def show_input_invalid_reasons(self, event: Input.Changed) -> None:
        """Show validation error messages for changed input fields.

        :param event: The input changed event.
        :type event: Input.Changed
        """
        self._validate_form()
        input_widget = event.input

        if event.validation_result.is_valid:
            input_widget.border_subtitle = None
        else:
            # Get first error message from list and display it
            error_message = event.validation_result.failure_descriptions[0]
            input_widget.border_subtitle = error_message

    @on(Input.Blurred)
    def show_input_invalid_reasons_2(self, event: Input.Blurred) -> None:
        """Show validation error messages for blurred input fields.

        :param event: The input blurred event.
        :type event: Input.Blurred
        """
        self._validate_form()
        input_widget = event.input

        if event.validation_result.is_valid:
            input_widget.border_subtitle = None
        else:
            # Get first error message from list and display it
            error_message = event.validation_result.failure_descriptions[0]
            input_widget.border_subtitle = error_message

    @on(Select.Changed)
    def show_select_invalid_reasons(self, event: Select.Changed) -> None:
        """Show validation error messages for changed select fields.

        :param event: The select changed event.
        :type event: Select.Changed
        """
        self._validate_form()
        select_widget = event.select
        select_current = select_widget.query_one(SelectCurrent)

        if event.select.is_blank():
            error_message = "An option must be selected."
            select_current.set_class(True, "-invalid")
            select_current.border_subtitle = error_message
        else:
            select_current.set_class(False, "-invalid")
            select_current.border_subtitle = None

    @on(DescendantBlur, "Select")
    def show_select_invalid_reasons_2(self, event: DescendantBlur) -> None:
        """Show validation error messages for blurred select fields.

        :param event: The descendant blur event.
        :type event: DescendantBlur
        """
        self._validate_form()
        select_widget = event.widget
        select_current = select_widget.query_one(SelectCurrent)

        if select_widget.is_blank():
            error_message = "An option must be selected."
            select_current.set_class(True, "-invalid")
            select_current.border_subtitle = error_message
        else:
            select_current.set_class(False, "-invalid")
            select_current.border_subtitle = None

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        """Handle Create button press.

        Collects form data and dismisses screen with the contract data.
        """
        self._collect_form_data()
        self.dismiss(self.contract_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into contract_data dictionary.

        Retrieves values from all form fields and stores them in contract_data.
        """
        self.contract_data = {
            "contract_total_amount": self.query_one(
                "#contract_total_amount", Input
            ).value,
            "contract_amount_due": self.query_one(
                "#contract_amount_due", Input
            ).value,
            "contract_customer": self.query_one(
                "#contract-customer-select", Select
            ).value,
        }


class UpdateContractScreen(Screen):
    """Screen for updating an existing contract in the EpicEvents CRM.

    Provides a form pre-filled with existing contract data for modification.
    Allows updating contract details, customer, and status.

    :param contract_data: Dictionary containing all data of the contract to update.
    :type contract_data: dict[str, Any]
    :param customers: List of existing customers to choose from.
    :type customers: list[Customer]
    """

    SUB_TITLE = "UPDATE CONTRACT"
    CSS_PATH = "../styles/update_contract_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(
        self, contract_data: dict[str, Any], customers: list[Customer]
    ) -> None:
        """Initialize the UpdateContractScreen with contract data and options.

        :param contract_data: Dictionary containing all data of the contract to update.
        :type contract_data: dict[str, Any]
        :param customers: List of existing customers to choose from.
        :type customers: list[Customer]
        """
        super().__init__()
        self.customers: list[Customer] = customers
        self.contract_data: dict[str, Any] = contract_data
        self.updated_contract_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (contract data,
        customer selection, status selection), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="update-contract-main-container"):
            yield Static(
                "Updating contract: "
                f"{self.contract_data['contract_id']} "
                "associated to "
                f"{self.contract_data['contract_customer'].first_name} "
                f"{self.contract_data['contract_customer'].last_name}",
                classes="updating-contract-static",
            )
            with Container(
                id="update-contract-data",
                classes="update-contract-data-input-container",
            ):
                yield Label("Contract Total Amount:")
                yield Input(
                    value=str(
                        self.contract_data.get("contract_total_amount", 0)
                    ),
                    placeholder="1500",
                    id="contract_total_amount",
                    type="number",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                        Number(
                            minimum=0,
                            failure_description="Value cannot be negative.",
                        ),
                    ],
                )
                yield Label("Contract Amount Due:")
                yield Input(
                    value=str(
                        self.contract_data.get("contract_amount_due", 0)
                    ),
                    placeholder="1500",
                    id="contract_amount_due",
                    type="number",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                        Number(
                            minimum=0,
                            failure_description="Value cannot be negative.",
                        ),
                    ],
                )
            with Container(
                id="update-contract-customer",
                classes="update-contract-customer-input-container",
            ):
                customer_options = [
                    (
                        (customer.first_name + " " + customer.last_name),
                        customer,
                    )
                    for customer in self.customers
                ]
                yield Select(
                    customer_options,
                    id="update-contract-customer-select",
                    prompt="Select a customer",
                    value=self.contract_data.get("contract_customer"),
                )
            with Container(
                id="update-contract-status",
                classes="update-contract-status-input-container",
            ):
                status_options = [
                    (
                        status.name,
                        status,
                    )
                    for status in ContractStatus
                ]
                yield Select(
                    status_options,
                    id="update-contract-status-select",
                    prompt="Select a status",
                    value=self.contract_data.get("contract_status"),
                )
            with Container(classes="update-contract-buttons-container"):
                yield Button(
                    "Update",
                    id="update",
                    variant="primary",
                    classes="update-contract-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="update-contract-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Set container border titles and subtitles and update widget states.

        Initializes the screen by setting container titles and disabling
        fields based on contract status.
        """
        contract_data_container = self.query_one(
            "#update-contract-data", Container
        )
        contract_customer_container = self.query_one(
            "#update-contract-customer", Container
        )
        contract_status_container = self.query_one(
            "#update-contract-status", Container
        )
        contract_data_container.border_title = "Contract Data"
        contract_data_container.border_subtitle = "Edit relevant fields"
        contract_customer_container.border_title = "Customer Selection"
        contract_status_container.border_title = "Status Selection"

        # Update widget state based on contract status
        self.update_total_amount_input_state()
        self.update_amount_due_input_state()
        self.update_customer_select_state()

    def watch_is_form_valid(self, is_valid: bool) -> None:
        """Disable or enable Update button based on form validation.

        :param is_valid: Whether the form is currently valid.
        :type is_valid: bool
        """
        update_button = self.query_one("#update", Button)
        update_button.disabled = not is_valid

    def _validate_form(self) -> None:
        """Validates every input field of the form.

        Updates the is_form_valid reactive variable based on validation results
        of all input and select fields.
        """
        widget_inputs = [
            self.query_one("#contract_total_amount", Input),
            self.query_one("#contract_amount_due", Input),
        ]

        widget_selects = [
            self.query_one("#update-contract-customer-select", Select),
            self.query_one("#update-contract-status-select", Select),
        ]

        # Check that all input fields are valid
        all_inputs_valid = all(
            widget_input.validate(widget_input.value).is_valid
            for widget_input in widget_inputs
        )
        # Check that all select fields are valid
        all_selects_valid = all(
            not select.is_blank() for select in widget_selects
        )

        # Update reactive variable triggering watcher
        all_valid = all_inputs_valid and all_selects_valid
        self.is_form_valid = all_valid

    def update_total_amount_input_state(self) -> None:
        """Update the state of the total amount input field.

        Disables the total amount field if the contract status is SIGNED.
        """
        total_amount_input = self.query_one(
            "#contract_total_amount", Input
        )
        contract_status = self.contract_data.get("contract_status")

        total_amount_input.disabled = (
            contract_status == ContractStatus.SIGNED
        )

    def update_amount_due_input_state(self) -> None:
        """Update the state of the amount due input field.

        Disables the amount due field if the contract status is SIGNED.
        """
        amount_due_input = self.query_one("#contract_amount_due", Input)
        contract_status = self.contract_data.get("contract_status")

        amount_due_input.disabled = (
            contract_status == ContractStatus.SIGNED
        )

    def update_customer_select_state(self) -> None:
        """Update the state of the customer select field.

        Disables the customer selection if the contract status is SIGNED.
        """
        customer_select = self.query_one(
            "#update-contract-customer-select", Select
        )
        contract_status = self.contract_data.get("contract_status")

        customer_select.disabled = contract_status == ContractStatus.SIGNED

    @on(Input.Changed)
    def show_input_invalid_reasons(self, event: Input.Changed) -> None:
        """Show validation error messages for changed input fields.

        :param event: The input changed event.
        :type event: Input.Changed
        """
        self._validate_form()
        input_widget = event.input

        if event.validation_result.is_valid:
            input_widget.border_subtitle = None
        else:
            # Get first error message from list and display it
            error_message = event.validation_result.failure_descriptions[0]
            input_widget.border_subtitle = error_message

    @on(Input.Blurred)
    def show_input_invalid_reasons_2(self, event: Input.Blurred) -> None:
        """Show validation error messages for blurred input fields.

        :param event: The input blurred event.
        :type event: Input.Blurred
        """
        self._validate_form()
        input_widget = event.input

        if event.validation_result.is_valid:
            input_widget.border_subtitle = None
        else:
            # Get first error message from list and display it
            error_message = event.validation_result.failure_descriptions[0]
            input_widget.border_subtitle = error_message

    @on(Select.Changed)
    def show_select_invalid_reasons(self, event: Select.Changed) -> None:
        """Show validation error messages for changed select fields.

        :param event: The select changed event.
        :type event: Select.Changed
        """
        self._validate_form()
        select_widget = event.select
        select_current = select_widget.query_one(SelectCurrent)

        if event.select.is_blank():
            error_message = "An option must be selected."
            select_current.set_class(True, "-invalid")
            select_current.border_subtitle = error_message
        else:
            select_current.set_class(False, "-invalid")
            select_current.border_subtitle = None

    @on(DescendantBlur, "Select")
    def show_select_invalid_reasons_2(self, event: DescendantBlur) -> None:
        """Show validation error messages for blurred select fields.

        :param event: The descendant blur event.
        :type event: DescendantBlur
        """
        self._validate_form()
        select_widget = event.widget
        select_current = select_widget.query_one(SelectCurrent)

        if select_widget.is_blank():
            error_message = "An option must be selected."
            select_current.set_class(True, "-invalid")
            select_current.border_subtitle = error_message
        else:
            select_current.set_class(False, "-invalid")
            select_current.border_subtitle = None

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        """Handle Update button press.

        Collects form data and dismisses screen with the updated contract data.
        """
        self._collect_form_data()
        self.dismiss(self.updated_contract_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into updated_contract_data dictionary.

        Retrieves values from all form fields and stores them in updated_contract_data.
        """
        selected_customer = self.query_one(
            "#update-contract-customer-select", Select
        ).value
        selected_status = self.query_one(
            "#update-contract-status-select", Select
        ).value

        self.updated_contract_data = {
            "contract_id": self.contract_data["contract_id"],
            "contract_total_amount": self.query_one(
                "#contract_total_amount", Input
            ).value,
            "contract_amount_due": self.query_one(
                "#contract_amount_due", Input
            ).value,
            "contract_customer": selected_customer,
            "contract_status": selected_status,
        }
