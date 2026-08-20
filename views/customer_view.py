from models import Customer
from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, DataTable, Button, Input, Label, Static, MaskedInput
from textual.screen import Screen

class CustomerScreen(Screen):
    """Screen that displays a table of customers."""

    BINDINGS = [
        ("b", "go_back", "Back"),
    ]

    def __init__(self, customers: list[Customer]) -> None:
        super().__init__()
        self.customers = customers

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - CUSTOMERS")
        yield DataTable(id="customers-table")
        yield Button('Create Customer', id='create-customer', variant='success')
        yield Button('Update Customer', id='update-customer', variant='warning')
        yield Button('Delete Customer', id='delete-customer', variant='error')
        yield Button('Back', id='back', variant='default')
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = 'row'

        # Configure table columns
        table.add_column("ID", key="id", width=8)
        table.add_column("First Name", key="first_name", width=15)
        table.add_column("Last Name", key="last_name", width=15)
        table.add_column("Company Name", key="company_name", width=25)
        table.add_column("Created At", key="created_at", width=20)
        table.add_column("Updated At", key="updated_at", width=20)
        table.add_column("Sales Rep ID", key="sales_rep_id", width=12)

        table.zebra_stripes = True
        table.loading = True

        self.load_customers()

    def load_customers(self) -> None:
        """Load customer data into the table."""
        table = self.query_one(DataTable)
        table.clear()

        for customer in self.customers:

            table.add_row(
                customer.id,
                customer.first_name,
                customer.last_name,
                customer.company_name,
                customer.created_at,
                customer.updated_at,
                customer.sales_representative_id,
            )

        table.loading = False

    def action_go_back(self) -> None:
        """Return to previous screen."""
        self.dismiss("back")

    @on(Button.Pressed, "#create-customer")
    def go_create_customer(self) -> None:
        self.dismiss('create_customer')

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss('back')


class CreateCustomerScreen(Screen[dict]):
    """Screen that displays a form to create a new customer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_data = {}

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Create New Customer", classes="form-title"),
            Label("Last Name:", classes="form-label"),
            Input(placeholder="Doe", id="last_name", type='text', classes="form-input"),
            Label("First Name:", classes="form-label"),
            Input(placeholder="John", id="first_name", type='text', classes="form-input"),
            Label("Company Name:", classes="form-label"),
            Input(placeholder="Optionnal", id="company_name", type='text', classes="form-input"),
            Container(
                Button("Create", id="create", variant="primary", classes="form-button"),
                Button("Cancel", id="cancel", variant="default", classes="form-button"),
                classes="form-buttons",
            ),
            classes="form-container",
        )

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        self.collect_form_data()
        self.dismiss(self.customer_data)
        
    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def collect_form_data(self) -> dict:
        """Collect all form data into a dictionary."""
        self.event_data = {
            "last_name": self.query_one("#last_name", Input).value,
            "first_name": self.query_one("#first_name", Input).value,
            "company_name": self.query_one("#company_name", Input).value,
        }
        return self.event_data