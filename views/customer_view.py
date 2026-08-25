from models import Customer, Contact, PhoneNumber
from textual import on
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Horizontal
from textual.events import Mount
from textual.widget import Widget
from textual.widgets import Header, Footer, DataTable, Button, Input, Label, Static, MaskedInput, SelectionList, Pretty
from textual.widgets.selection_list import Selection
from textual.screen import Screen
from datetime import datetime

class CustomerScreen(Screen):
    """Screen that displays a table of customers."""

    SUB_TITLE = 'CUSTOMERS'

    CSS_PATH = 'styles/customer_screen.tcss'

    BINDINGS = [
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_customer_id: reactive[int | None] = reactive(None)
    selected_contact_id: reactive[int | None] = reactive(None)

    def __init__(self, customers: list[Customer]) -> None:
        super().__init__()
        self.customers = customers

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes='customer-main-container'):
            yield DataTable(id="customers-table")
            yield DataTable(id='contacts-table')
            yield DataTable(id='phone-numbers-table')
            with Container(classes='customer-buttons-container'):
                yield Button('Create Customer', id='create-customer', variant='primary')
                yield Button('Update Customer', id='update-customer', variant='warning')
                yield Button('Delete Customer', id='delete-customer', variant='error')
            with Container(classes='contact-buttons-container'):
                yield Button('Create Contact', id='create-contact', variant='primary')
                yield Button('Update Contact', id='update-contact', variant='warning')
                yield Button('Delete Contact', id='delete-contact', variant='error')
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """
        """
        self.build_customers_table()
        self.build_contacts_table()
        self.build_phone_numbers_table()

        if self.customers:
            self.selected_customer_id = self.customers[0].id
            if self.customers[0].contacts:
                self.selected_contact_id = self.customers[0].contacts[0].id
        

    def build_customers_table(self) -> None:
        table = self.query_one('#customers-table', DataTable)
        table.border_title = 'Customers'
        table.cursor_type = 'row'
        table.zebra_stripes = True

        # Configure table columns
        table.add_column("ID", key="id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")
        table.add_column("Company Name", key="company_name")
        table.add_column('Sales Representative')
        table.add_column("Created At", key="created_at")
        table.add_column("Updated At", key="updated_at")

        table.loading = True
        self.load_customers(table)

    def load_customers(self, table: DataTable) -> None:
        """Load customer data into the table."""
        table.clear()

        for customer in self.customers:
            # sales representative
            sales_representative = (
                customer.sales_representative.first_name +
                ' ' +
                customer.sales_representative.last_name
            )

            table.add_row(
                customer.id,
                customer.first_name,
                customer.last_name,
                customer.company_name,
                sales_representative,
                customer.created_at,
                customer.updated_at,
            )

        table.loading = False

    def build_contacts_table(self) -> None:
        table = self.query_one('#contacts-table', DataTable)
        table.border_title = 'Contacts'
        table.cursor_type = 'row'
        table.zebra_stripes = True

        table.add_column("ID", key="id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")
        table.add_column("Email", key="email")

        table.loading = True

    def load_contacts(self, table: DataTable, customer: Customer) -> None:
        table.clear()

        for contact in customer.contacts:
            table.add_row(
                contact.id,
                contact.first_name,
                contact.last_name,
                contact.email
            )

            table.loading = False

    def build_phone_numbers_table(self) -> None:
        table = self.query_one('#phone-numbers-table', DataTable)
        table.border_title = 'Phone Numbers'
        table.cursor_type = 'row'
        table.zebra_stripes = True

        table.add_column('ID', key='id')
        table.add_column("Phone Number", key="phone_number")
        table.loading = True

    def load_phone_numbers(self, table: DataTable, contact: Contact) -> None:
        table.clear()
        for phone_number in contact.phone_numbers:
            table.add_row(
                phone_number.id,
                phone_number.number
            )

        table.loading = False

    def watch_selected_customer_id(self, new_id: int | None) -> None:
        """
        Watcher that loads contacts and phone numbers based on the client
        highlighted in customers-table
        """
        contacts_table = self.query_one('#contacts-table', DataTable)
        phone_numbers_table = self.query_one('#phone-numbers-table', DataTable)

        if new_id is None:
            contacts_table.clear()
            self.selected_contact_id = None
            return

        # Get customer by ID
        selected_customer = next(
            (c for c in self.customers if c.id == new_id),
            None
        )

        if selected_customer:
            self.load_contacts(contacts_table, selected_customer)
            self.selected_contact_id = selected_customer.contacts[0].id

    def watch_selected_contact_id(self, new_id: int | None) -> None:
        """
        Watcher that loads phone numbers based on the contact
        highlighted in contacts-table
        """
        phone_numbers_table = self.query_one('#phone-numbers-table', DataTable)

        if new_id is None:
            phone_numbers_table.clear()
            return

        # Trouve le contact sélectionné dans le client actuellement sélectionné
        if self.selected_customer_id:
            selected_customer = next(
                (c for c in self.customers if c.id == self.selected_customer_id),
                None
            )
            if selected_customer:
                selected_contact = next(
                    (contact for contact in selected_customer.contacts if contact.id == new_id),
                    None
                )
                if selected_contact:
                    self.load_phone_numbers(phone_numbers_table, selected_contact)

    def action_go_back(self) -> None:
        """Return to previous screen."""
        self.dismiss("back")

    @on(DataTable.RowHighlighted, "#customers-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Saves highlighted customer id"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self.customers):
            self.selected_customer_id = self.customers[row_index].id

    @on(DataTable.RowHighlighted, "#contacts-table")
    def on_contact_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Saves highlighted contact id"""
        row_index = event.cursor_row

        # Récupère le contact correspondant à la ligne sélectionnée
        if self.selected_customer_id:
            selected_customer = next(
                (c for c in self.customers if c.id == self.selected_customer_id),
                None
            )
            if selected_customer and 0 <= row_index < len(selected_customer.contacts):
                selected_contact = selected_customer.contacts[row_index]
                self.selected_contact_id = selected_contact.id

    @on(Button.Pressed, "#create-customer")
    def go_create_customer(self) -> None:
        self.dismiss('create_customer')

    @on(Button.Pressed, "#update-customer")
    def go_update_customer(self) -> None:
        self.dismiss(('update_customer', self.selected_customer_id))

    @on(Button.Pressed, "#create-contact")
    def go_create_contact(self) -> None:
        self.dismiss('create_contact')

    @on(Button.Pressed, "#update-contact")
    def go_update_contact(self) -> None:
        self.dismiss(('update_contact', self.selected_contact_id))

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss('back')

class CreateCustomerScreen(Screen):
    """Screen that displays a form to create a new customer."""

    SUB_TITLE = 'CREATE CUSTOMERS'

    CSS_PATH = 'styles/create_customer_screen.tcss'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_data = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes='create-customer-main-container'):
            with Container(id='customer-data', classes='customer-data-input-container'):
                yield Label("Customer Last Name:", classes="form-label")
                yield Input(placeholder="Doe", id="customer_last_name", type='text', classes="form-input")
                yield Label("Customer First Name:", classes="form-label")
                yield Input(placeholder="John", id="customer_first_name", type='text', classes="form-input")
                yield Label("Company Name:", classes="form-label")
                yield Input(placeholder="John Doe Corp", id="company_name", type='text', classes="form-input")
            with Container(id='contact-data', classes='contact-data-input-container'):
                yield Label("Contact Last Name:", classes="form-label")
                yield Input(placeholder="Smith", id="contact_last_name", type='text', classes="form-input")
                yield Label("First Name:", classes="form-label")
                yield Input(placeholder="Tom", id="contact_first_name", type='text', classes="form-input")
                yield Label("Email:", classes="form-label")
                yield Input(placeholder="tom.smith@example.com", id="email", type='text', classes="form-input")
                yield Label("Phone Number:", classes="form-label")
                yield Input(placeholder="00 12 34 56 78", id="phone_number", type='number', classes="form-input")
            with Container(classes='create-customer-buttons-container'):
                yield Button("Create", id="create", variant="primary", classes='create-customer-button')
                yield Button("Cancel", id="cancel", variant="default", classes='create-customer-button')
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        customer_data_container = self.query_one('#customer-data', Container)
        contact_data_container = self.query_one('#contact-data', Container)
        customer_data_container.border_title = 'Personal Data'
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
    SUB_TITLE = 'UPDATE CUSTOMERS'

    CSS_PATH = 'styles/update_customer_screen.tcss'

    def __init__(self, customer_data: dict, contacts: list[Contact]):
        super().__init__()
        self.customer_data = customer_data
        self.updated_customer_data = {}
        self.contacts = contacts
        self.customer_contacts_ids = customer_data.get('customer_contacts_ids', [])

    def compose(self):
        """
        Compose the screen with a form to update customer data.
        """
        yield Header(show_clock=True)
        with Container(classes='update-customer-main-container'):
            yield Static(
                f"Updating Customer: {self.customer_data['customer_first_name']} {self.customer_data['customer_last_name']}",
                classes='updating-customer-static'
            )
            with Container(id='update-customer-data', classes='update-customer-data-input-container'):
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
            with Container(id='update-contact-data', classes='update-contact-data-select-container'):
                yield SelectionList(
                    classes='update-customer-contacts-selection-list')
            with Container(classes="update-customer-buttons-container"):
                yield Button("Update", id="update", variant="primary", classes='update-customer-button')
                yield Button("Cancel", id="cancel", variant="default", classes='update-customer-button')
        yield Footer(show_command_palette=False)

    def _on_mount(self):
        """
        Fill the selection list with contacts and the pretty with selected contacts
        """

        self.query_one('#update-customer-data', Container).border_title = 'Personal Data'
        self.query_one('#update-customer-data', Container).border_subtitle = 'Edit relevant fields'
        self.query_one('#update-contact-data', Container).border_title = 'Assigned Contacts'
        self.query_one('#update-contact-data', Container).border_subtitle = 'Click on contact to assign/unassign'
        for contact in self.contacts:
            is_assigned = contact.id in self.customer_contacts_ids

            self.query_one(SelectionList).add_option(
                Selection(
                    prompt=f'{contact.first_name} {contact.last_name}',
                    value=contact.id,
                    initial_state=is_assigned
                )
            )

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
        selection_list = self.query_one(SelectionList)
        selected_contacts_ids = [selection for selection in selection_list.selected]

        self.updated_customer_data = {
            "id": self.customer_data['customer_id'],
            "first_name": self.query_one("#customer_first_name", Input).value,
            "last_name": self.query_one("#customer_last_name", Input).value,
            "company_name": self.query_one("#company_name", Input).value,
            'contact_ids': selected_contacts_ids,
            'updated_at': datetime.now()
        }

class CreateContactScreen(Screen):
    """
    """
    SUB_TITLE = 'CREATE CONTACT'
    CSS_PATH = 'styles/create_contact_screen.tcss'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contact_data = {}
        self.phone_number_counter = 2

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes='create-contact-main-container'):
            with Container(id='contact-data', classes='contact-data-input-container'):
                yield Label("Contact Last Name:", classes="form-label")
                yield Input(placeholder="Smith", id="contact_last_name", type='text', classes="form-input")
                yield Label("Contact First Name:", classes="form-label")
                yield Input(placeholder="Tom", id="contact_first_name", type='text', classes="form-input")
                yield Label("Email:", classes="form-label")
                yield Input(placeholder="tom.smith@example.com", id="email", type='text', classes="form-input")
            with Container(id='phone-number', classes='phone-number-input-container'):
                yield Label("Phone Number 1:", id='phone_label_1', classes="form-label")
                yield Input(placeholder="00 12 34 56 78", id="phone_number_1", type='number', classes="form-input")
                with Container(id='phone-number-buttons-container', classes='phone-number-buttons-container'):
                    yield Button("Add a number", id="add-phone-number", variant='default')
            with Container(classes='create-contact-buttons-container'):
                yield Button("Create", id="create", variant="primary", classes='create-contact-button')
                yield Button("Cancel", id="cancel", variant="default", classes='create-contact-button')
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        contact_data_container = self.query_one('#contact-data', Container)
        phone_number_container = self.query_one('#phone-number', Container)
        contact_data_container.border_title = 'Personal Data'
        phone_number_container.border_title = 'Phone Numbers'

    @on(Button.Pressed, "#add-phone-number")
    def on_add_phone_number(self) -> None:
        """
        Adds a field to input new phone number
        """
        container = self.query_one('#phone-number', Container)
        # New label
        label = Label(f"Phone Number {self.phone_number_counter}:", classes="form-label", id=f"phone_label_{self.phone_number_counter}")
        # New input
        input_field = Input(
            placeholder="00 12 34 56 78",
            id=f"phone_number_{self.phone_number_counter}",
            type='number',
            classes="form-input"
        )

        # Add widgets to container
        container.mount(label, before='#phone-number-buttons-container')
        container.mount(input_field, before='#phone-number-buttons-container')
 
        # Increment phone counter
        self.phone_number_counter += 1

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        self._collect_form_data()
        self.dismiss(self.contact_data)
        
    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self) -> dict:
        """Collect all form data into a dictionary."""
        all_inputs = self.query(Input)
        phone_numbers = []

        for input in all_inputs:
            if input.id.startswith('phone_number_'):
                if input.value:
                    phone_numbers.append(input.value)

        self.contact_data = {
            "contact_last_name": self.query_one("#contact_last_name", Input).value,
            "contact_first_name": self.query_one("#contact_first_name", Input).value,
            "email": self.query_one("#email", Input).value,
            "phone_numbers": phone_numbers,
        }

class UpdateContactScreen(Screen):
    """
    Screen to update a contact with editable phone numbers.
    """

    SUB_TITLE = 'UPDATE CONTACT'
    CSS_PATH = 'styles/update_contact_screen.tcss'

    def __init__(self, contact_data: dict, **kwargs):
        super().__init__(**kwargs)
        self.contact_data = contact_data
        self.updated_contact_data = {}
        # Counter for additional phone numbers (starts after the existing ones)
        self.phone_number_counter = len(contact_data.get('phone_numbers', []))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes='update-contact-main-container'):
            yield Static(
                f"Updating Contact: {self.contact_data['contact_first_name']} {self.contact_data['contact_last_name']}",
                classes='updating-contact-static'
            )
            with Container(id='update-contact-data', classes='update-contact-data-input-container'):
                yield Label("Contact Last Name:", classes="form-label")
                yield Input(
                    value=self.contact_data.get('contact_last_name', ''),
                    id="contact_last_name",
                    type='text',
                    classes="form-input"
                )
                yield Label("Contact First Name:", classes="form-label")
                yield Input(
                    value=self.contact_data.get('contact_first_name', ''),
                    id="contact_first_name",
                    type='text',
                    classes="form-input"
                )
                yield Label("Email:", classes="form-label")
                yield Input(
                    value=self.contact_data.get('email', ''),
                    id="email",
                    type='text',
                    classes="form-input"
                )
            with Container(id='update-phone-number', classes='update-phone-number-input-container'):
                # Loads existing phone numbers
                for i, phone in enumerate(self.contact_data.get('phone_numbers', [])):
                    yield Label(f"Phone Number {i+1}:", classes="form-label", id=f"phone_label_{i}")
                    yield Input(
                        value=phone,
                        id=f"phone_number_{i}",
                        type='number',
                        classes="form-input"
                    )
                with Container(classes='update-phone-number-buttons-container'):
                    yield Button("Add a number", id="add-phone-number", variant="default")
            with Container(classes='update-contact-buttons-container'):
                yield Button("Update", id="update", variant="primary", classes='update-contact-button')
                yield Button("Cancel", id="cancel", variant="default", classes='update-contact-button')
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.query_one('#update-contact-data', Container).border_title = 'Personal Data'
        self.query_one('#update-contact-data', Container).border_subtitle = 'Edit relevant fields'
        self.query_one('#update-phone-number', Container).border_title = 'Phone Numbers'
        self.query_one('#update-phone-number', Container).border_subtitle = 'Edit relevant fields'

    @on(Button.Pressed, "#add-phone-number")
    def on_add_phone_number(self) -> None:
        """
        Add a new phone number input field before the button container.
        """
        container = self.query_one('#update-phone-number', Container)
        buttons_container = self.query_one('.update-phone-number-buttons-container', Container)

        label = Label(
            f"Phone Number {self.phone_number_counter + 1}:",
            classes="form-label",
            id=f"phone_label_{self.phone_number_counter + 1}"
        )
        input_field = Input(
            placeholder="00 12 34 56 78",
            id=f"phone_number_{self.phone_number_counter + 1}",
            type='number',
            classes="form-input"
        )

        container.mount(label, before=buttons_container)
        container.mount(input_field, before=buttons_container)

        self.phone_number_counter += 1

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        self._collect_form_data()
        self.dismiss(self.updated_contact_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self) -> dict:
        """Collect all form data including all phone numbers."""
        all_inputs = self.query(Input)
        phone_numbers = []

        for input in all_inputs:
            if input.id.startswith("phone_number_"):
                if input.value:
                    phone_numbers.append(input.value)

        self.updated_contact_data = {
            'id': self.contact_data['contact_id'],
            'last_name': self.query_one("#contact_last_name", Input).value,
            'first_name': self.query_one("#contact_first_name", Input).value,
            'email': self.query_one("#email", Input).value,
            'phone_numbers': phone_numbers
        }