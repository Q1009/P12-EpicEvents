from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
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

from contracts.contract_model import Contract, ContractStatus
from customers.customer_model import Customer
from services.date_services import format_french_datetime


class ContractScreen(Screen):
    """Screen that displays a table of contracts."""

    SUB_TITLE = "CONTRACTS"
    CSS_PATH = "../styles/contract_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_contract_id: reactive[int | None] = reactive(None)
    selected_customer_id: reactive[int | None] = reactive(None)
    selected_event_id: reactive[int | None] = reactive(None)

    def __init__(self, contracts: list[Contract]) -> None:
        super().__init__()
        self.contracts = contracts

    def compose(self) -> ComposeResult:
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
                    disabled=True,
                )
            with Container(classes="customer-event-buttons-container"):
                yield Button(
                    "Consult Customer",
                    id="consult-customer",
                    variant="primary",
                    disabled=True,
                )
                yield Button(
                    "Consult Event",
                    id="consult-event",
                    variant="warning",
                    disabled=True,
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """ """
        self.build_contracts_table()
        self.build_contract_customer_table()
        self.build_contract_payment_progressbar()
        self.build_contract_event_table()

        # Initialize default selections with the first available contract,
        # customer, and event to ensure the UI has valid selections on load.
        if self.contracts:
            self.selected_contract_id = self.contracts[0].id
            if self.contracts[0].customer:
                self.selected_customer_id = self.contracts[0].customer.id
            if self.contracts[0].event:
                self.selected_event_id = self.contracts[0].event.id

    def build_contracts_table(self) -> None:
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
        """Load contract data into the table."""
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
        table.clear()

        if contract.customer:
            table.add_row(
                contract.customer.id,
                contract.customer.first_name,
                contract.customer.last_name,
            )

        table.loading = False

    def build_contract_event_table(self) -> None:
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
        table.clear()

        if contract.event:
            table.add_row(
                contract.event.id,
                contract.event.name,
            )

        table.loading = False

    def build_contract_payment_progressbar(self) -> None:
        progress_bar = self.query_one(
            "#contract-payment-progressbar", ProgressBar
        )
        progress_bar.border_title = "Amount Paid - %"

    def load_contract_payment(
        self, progressbar: ProgressBar, contract: Contract
    ) -> None:
        total_amount = contract.total_amount
        amount_due = contract.amount_due
        paid_amount = total_amount - amount_due
        progressbar.update(total=total_amount, progress=paid_amount)

    def watch_selected_contract_id(self, new_id: int | None) -> None:
        """
        Watcher that loads customers and events based on the contract
        highlighted in contracts-table
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
        selected_contract = next(
            (c for c in self.contracts if c.id == new_id), None
        )

        if selected_contract:
            self.load_contract_customer(
                contract_customer_table, selected_contract
            )
            self.load_contract_event(
                contract_event_table, selected_contract
            )
            self.load_contract_payment(
                contract_payment_progressbar, selected_contract
            )

    def action_go_back(self) -> None:
        """Return to previous screen."""
        self.dismiss("back")

    def _delete_contract(self, contract_id):
        self.dismiss(("delete_contract", contract_id))

    @on(DataTable.RowHighlighted, "#contracts-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Saves highlighted contract id"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self.contracts):
            self.selected_contract_id = self.contracts[row_index].id

    @on(Button.Pressed, "#create-contract")
    def go_create_contract(self) -> None:
        self.dismiss("create_contract")

    @on(Button.Pressed, "#update-contract")
    def go_update_contract(self) -> None:
        self.dismiss(("update_contract", self.selected_contract_id))

    @on(Button.Pressed, "#create-event")
    def go_create_event(self) -> None:
        self.dismiss(("create_event", self.selected_contract_id))

    @on(Button.Pressed, "#consult-customer")
    def go_consult_customer(self) -> None:
        self.dismiss(("consult_customer", self.selected_customer_id))

    @on(Button.Pressed, "#consult-event")
    def go_consult_event(self) -> None:
        self.dismiss(("consult_event", self.selected_event_id))

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss("back")


class CreateContractScreen(Screen):
    """Screen that displays a form to create a new contract."""

    SUB_TITLE = "CREATE CONTRACT"

    CSS_PATH = "../styles/create_contract_screen.tcss"

    def __init__(self, customers: list[Customer]):
        super().__init__()
        self.customers = customers
        self.contract_data = {}

    def compose(self) -> ComposeResult:
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
                )
                yield Label(
                    "Contract Amount Due ($):", classes="form-label"
                )
                yield Input(
                    placeholder="1500",
                    id="contract_amount_due",
                    type="number",
                    classes="form-input",
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
        contract_data_container = self.query_one(
            "#contract-data", Container
        )
        contract_customer_container = self.query_one(
            "#contract-customer", Container
        )
        contract_data_container.border_title = "Contract Data"
        contract_customer_container.border_title = "Customer Selection"

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        self._collect_form_data()
        self.dismiss(self.contract_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self) -> dict:
        """Collect all form data into a dictionary."""
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
    """ """

    SUB_TITLE = "UPDATE CONTRACT"
    CSS_PATH = "../styles/update_contract_screen.tcss"

    def __init__(self, contract_data: dict, customers: list[Customer]):
        super().__init__()
        self.customers = customers
        self.contract_data = contract_data
        self.updated_contract_data = {}

    def compose(self):
        """
        Compose the screen with a form to update contract data.
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
                    id="contract_total_amount",
                    type="number",
                )
                yield Label("Contract Amount Due:")
                yield Input(
                    value=str(
                        self.contract_data.get("contract_amount_due", 0)
                    ),
                    id="contract_amount_due",
                    type="number",
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

    def _on_mount(self):
        """Set container border title and subtitle"""

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

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        self._collect_form_data()
        self.dismiss(self.updated_contract_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self):
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
