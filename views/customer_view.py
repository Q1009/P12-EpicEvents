from models import Customer
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Horizontal
from textual.widget import Widget
from textual.widgets import Header, Footer, DataTable, Button, Input, Label, Static, MaskedInput
from textual.screen import Screen
from datetime import datetime

class CustomerScreen(Screen):
    """Screen that displays a table of customers."""

    BINDINGS = [
        ("b", "go_back", "Back"),
    ]

    def __init__(self, customers: list[Customer]) -> None:
        super().__init__()
        self.customers = customers
        self.selected_customer_id = None

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

    @on(DataTable.RowHighlighted, "#customers-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Saves highlighted customer id"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self.customers):
            self.selected_customer_id = self.customers[row_index].id

    @on(Button.Pressed, "#create-customer")
    def go_create_customer(self) -> None:
        self.dismiss('create_customer')

    @on(Button.Pressed, "#update-customer")
    def go_update_customer(self) -> None:
        self.dismiss(('update_customer', self.selected_customer_id))

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss('back')


class CreateCustomerScreen(Screen):
    """Screen that displays a form to create a new customer."""

    CSS_PATH = 'styles/create_customer_screen.tcss'

    BINDINGS = [
        ("b", "go_back", "Back"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_data = {}

    def compose(self) -> ComposeResult:

        yield Header("EPIC EVENTS - CREATE CUSTOMER")
        with ScrollableContainer(id='personal-data'):
            yield Label("Customer Last Name:", classes="form-label")
            yield Input(placeholder="Doe", id="customer_last_name", type='text', classes="form-input")
            yield Label("Customer First Name:", classes="form-label")
            yield Input(placeholder="John", id="customer_first_name", type='text', classes="form-input")
            yield Label("Company Name:", classes="form-label")
            yield Input(placeholder="John Doe Corp", id="company_name", type='text', classes="form-input")
        with ScrollableContainer(id='contact-data'):
            yield Label("Contact Last Name:", classes="form-label")
            yield Input(placeholder="Smith", id="contact_last_name", type='text', classes="form-input")
            yield Label("First Name:", classes="form-label")
            yield Input(placeholder="Tom", id="contact_first_name", type='text', classes="form-input")
            yield Label("Email:", classes="form-label")
            yield Input(placeholder="tom.smith@example.com", id="email", type='text', classes="form-input")
            yield Label("Phone Number:", classes="form-label")
            yield Input(placeholder="00 12 34 56 78", id="phone_number", type='number', classes="form-input")
        with Container(id='create-buttons-container'):
            yield Button("Create", id="create", variant="primary", classes="form-button")
            yield Button("Cancel", id="cancel", variant="default", classes="form-button")
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        personal_data_container = self.query_one('#personal-data', ScrollableContainer)
        contact_data_container = self.query_one('#contact-data', ScrollableContainer)
        personal_data_container.border_title = 'Personal Data'
        contact_data_container.border_title = 'Contact Data'

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        self._collect_form_data()
        self.dismiss(self.customer_data)
        
    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self) -> dict:
        """Collect all form data into a dictionary."""
        self.customer_data = {
            "customer_last_name": self.query_one("#customer_last_name", Input).value,
            "customer_first_name": self.query_one("#customer_first_name", Input).value,
            "company_name": self.query_one("#company_name", Input).value,
            "contact_last_name": self.query_one("#contact_last_name", Input).value,
            "contact_first_name": self.query_one("#contact_first_name", Input).value,
            "email": self.query_one("#email", Input).value,
            "phone_number": self.query_one("#phone_number", Input).value,
        }

class UpdateCustomerScreen(Screen):
    """
    """
    def __init__(self, customer_data: dict):
        super().__init__()
        self.customer_data = customer_data
        self.updated_customer_data = {}

    def compose(self):
        """
        Compose the screen with a form to update customer data.
        """
        yield Header("EPIC EVENTS - UPDATE CUSTOMER")
        yield Static(f"Updating Customer: {self.customer_data['customer_first_name']} {self.customer_data['customer_last_name']}")

        # Form fields with pre-filled values
        with Container():
            yield Label("Customer First Name:")
            yield Input(
                value=self.customer_data.get("customer_first_name", ""),
                id="customer_first_name"
            )
            yield Label("Customer Last Name:")
            yield Input(
                value=self.customer_data.get("customer_last_name", ""),
                id="customer_last_name"
            )
            yield Label("Company Name:")
            yield Input(
                value=self.customer_data.get("company_name", ""),
                id="company_name"
            )
        with Container(id="update-buttons-container"):
            yield Button("Update", id="update", variant="primary")
            yield Button("Cancel", id="cancel", variant="default")

        yield Footer(show_command_palette=False)

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        self._collect_form_data()
        self.dismiss(self.updated_customer_data)
            
    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self):
        """
        """
        self.updated_customer_data = {
            "id": self.customer_data['customer_id'],
            "first_name": self.query_one("#customer_first_name", Input).value,
            "last_name": self.query_one("#customer_last_name", Input).value,
            "company_name": self.query_one("#company_name", Input).value,
            'updated_at': datetime.now()
        }