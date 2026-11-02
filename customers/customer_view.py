from typing import Any, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import DescendantBlur
from textual.reactive import reactive
from textual.screen import Screen
from textual.validation import Length
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Select,
    SelectionList,
    Static,
)
from textual.widgets._select import SelectCurrent
from textual.widgets.selection_list import Selection

from collaborators.collaborator_model import Collaborator
from customers.customer_model import Contact, Customer
from permissions.permission_model import Permission
from services.date_services import format_french_datetime
from services.permission_services import PermissionServices


class CustomerScreen(Screen):
    """Screen for displaying and managing customers in the EpicEvents CRM.

    Provides a comprehensive view of all customers with their associated
    contacts and phone numbers. Allows navigation to create and update
    customer and contact records.

    :param customers: List of Customer objects to display in the table.
    :type customers: list[Customer]
    :param user: The currently authenticated collaborator.
    :type user: Collaborator
    :param customer_id: Optional ID of a customer to pre-select in the table.
    :type customer_id: int | None
    """

    SUB_TITLE = "CUSTOMERS"
    CSS_PATH = "../styles/customer_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_customer_id: reactive[int | None] = reactive(None)
    selected_contact_id: reactive[int | None] = reactive(None)

    BUTTON_PERMISSIONS: ClassVar[dict[str, set[Permission]]] = {
        "create-customer": {Permission.CREATE_CUSTOMER},
        "update-customer": {
            Permission.UPDATE_OWN_CUSTOMERS,
        },
        "create-contact": {Permission.CREATE_CONTACT},
        "update-contact": {Permission.UPDATE_CONTACT},
    }

    def __init__(
        self,
        customers: list[Customer],
        user: Collaborator,
        customer_id: int | None = None,
    ) -> None:
        """Initialize the CustomerScreen with customers and user data.

        :param customers: List of Customer objects to display in the table.
        :type customers: list[Customer]
        :param user: The currently authenticated collaborator.
        :type user: Collaborator
        :param customer_id: Optional ID of a customer to pre-select in the table.
        :type customer_id: int | None
        """
        super().__init__()
        self.customers: list[Customer] = customers
        self.current_user: Collaborator = user
        self.pre_selected_customer_id: int | None = customer_id

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with data tables (customers, contacts,
        phone numbers), action buttons, and footer.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="customer-main-container"):
            yield DataTable(id="customers-table")
            yield DataTable(id="customer-contacts-table")
            yield DataTable(id="contact-phone-numbers-table")
            with Container(classes="customer-buttons-container"):
                yield Button(
                    "Create Customer",
                    id="create-customer",
                    variant="primary",
                )
                yield Button(
                    "Update Customer",
                    id="update-customer",
                    variant="warning",
                )
            with Container(classes="contact-buttons-container"):
                yield Button(
                    "Create Contact",
                    id="create-contact",
                    variant="primary",
                )
                yield Button(
                    "Update Contact",
                    id="update-contact",
                    variant="warning",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Builds all data tables, sets button states based on permissions,
        and handles pre-selected customer if provided.
        """
        self.build_customers_table()
        self.build_contacts_table()
        self.build_phone_numbers_table()
        self.set_button_state("create-customer")
        self.set_button_state("update-customer")
        self.set_button_state("create-contact")
        self.set_button_state("update-contact")

        # Setting initial selected_customer_id: triggering the watcher
        # If a customer id was given to constructor
        if self.pre_selected_customer_id is not None:
            customer: Customer | None = next(
                (
                    c
                    for c in self.customers
                    if c.id == self.pre_selected_customer_id
                ),
                None,
            )
            if customer:
                # Moving cursor will update selected_customer_id
                row_index = self.customers.index(customer)
                self.query_one("#customers-table", DataTable).move_cursor(
                    row=row_index
                )

        # If not, use first customer
        elif self.customers:
            self.selected_customer_id = self.customers[0].id

    def build_customers_table(self) -> None:
        """Build and configure the customers data table.

        Sets up column headers and loads customer data into the table.
        """
        table = self.query_one("#customers-table", DataTable)
        table.border_title = "Customers"
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Configure table columns
        table.add_column("ID", key="customer_id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")
        table.add_column("Company Name", key="company_name")
        table.add_column(
            "Sales Representative", key="sales_representative"
        )
        table.add_column("Created At", key="created_at")
        table.add_column("Updated At", key="updated_at")

        table.loading = True
        self.load_customers(table)

    def load_customers(self, table: DataTable) -> None:
        """Load customer data into the customers table.

        Populates the table with customer data including sales representative
        names and formatted creation/update dates.

        :param table: The DataTable widget to populate with customer data.
        :type table: DataTable
        """
        table.clear()

        for customer in self.customers:
            # sales representative
            if customer.sales_representative:
                sales_representative = (
                    customer.sales_representative.first_name
                    + " "
                    + customer.sales_representative.last_name
                )
            else:
                sales_representative = None
            # creation and update date format conversion
            created_at = format_french_datetime(customer.created_at)
            updated_at = format_french_datetime(customer.updated_at)

            table.add_row(
                customer.id,
                customer.first_name,
                customer.last_name,
                customer.company_name,
                sales_representative,
                created_at,
                updated_at,
            )

        table.loading = False

    def build_contacts_table(self) -> None:
        """Build and configure the contacts data table.

        Sets up column headers for displaying associated contact information.
        """
        table = self.query_one("#customer-contacts-table", DataTable)
        table.border_title = "Contacts"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="contact_id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")
        table.add_column("Email", key="email")

        table.loading = True

    def load_contacts(self, table: DataTable, customer: Customer) -> None:
        """Load contact data for the selected customer.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param customer: The Customer object containing contacts.
        :type customer: Customer
        """
        table.clear()

        for contact in customer.contacts:
            table.add_row(
                contact.id,
                contact.first_name,
                contact.last_name,
                contact.email,
            )

        table.loading = False

    def build_phone_numbers_table(self) -> None:
        """Build and configure the phone numbers data table.

        Sets up column headers for displaying associated phone number information.
        """
        table = self.query_one("#contact-phone-numbers-table", DataTable)
        table.border_title = "Phone Numbers"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="id")
        table.add_column("Phone Number", key="phone_number")
        table.loading = True

    def load_phone_numbers(
        self, table: DataTable, contact: Contact
    ) -> None:
        """Load phone number data for the selected contact.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param contact: The Contact object containing phone numbers.
        :type contact: Contact
        """
        table.clear()
        for phone_number in contact.phone_numbers:
            table.add_row(
                phone_number.id,
                phone_number.number,
            )

        table.loading = False

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

    def watch_selected_customer_id(self, new_id: int | None) -> None:
        """Watcher that loads contacts and updates selected contact.

        Updates the contacts table and selected contact when a new customer
        is selected in the customers table. Also updates button states.

        :param new_id: The ID of the newly selected customer.
        :type new_id: int | None
        """
        contacts_table = self.query_one(
            "#customer-contacts-table", DataTable
        )

        if new_id is None:
            contacts_table.clear()
            self.selected_contact_id = None
            return

        # Get customer by ID
        selected_customer: Customer | None = next(
            (c for c in self.customers if c.id == new_id), None
        )

        if selected_customer and selected_customer.contacts:
            self.load_contacts(contacts_table, selected_customer)
            self.selected_contact_id = selected_customer.contacts[0].id

        # Enable or disable button
        self.update_update_customer_button_state(selected_customer)
        self.update_update_contact_button_state(selected_customer)

    def watch_selected_contact_id(self, new_id: int | None) -> None:
        """Watcher that loads phone numbers based on the selected contact.

        Updates the phone numbers table when a new contact is selected
        in the contacts table.

        :param new_id: The ID of the newly selected contact.
        :type new_id: int | None
        """
        phone_numbers_table = self.query_one(
            "#contact-phone-numbers-table", DataTable
        )

        if new_id is None:
            phone_numbers_table.clear()
            return

        # Get contact by ID
        if self.selected_customer_id:
            selected_customer: Customer | None = next(
                (
                    c
                    for c in self.customers
                    if c.id == self.selected_customer_id
                ),
                None,
            )
            if selected_customer:
                selected_contact: Contact | None = next(
                    (
                        contact
                        for contact in selected_customer.contacts
                        if contact.id == new_id
                    ),
                    None,
                )
                if selected_contact:
                    self.load_phone_numbers(
                        phone_numbers_table, selected_contact
                    )

    def update_update_customer_button_state(
        self, selected_customer: Customer | None
    ) -> None:
        """Update the state of the update customer button based on permissions.

        Checks if the current user has permission to update their own customers
        and if they are the sales representative for the selected customer.

        :param selected_customer: The currently selected customer.
        :type selected_customer: Customer | None
        """
        update_customer_button = self.query_one("#update-customer", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_OWN_CUSTOMERS
        ):
            if selected_customer is not None:
                update_customer_button.display = (
                    selected_customer.sales_representative_id
                    == self.current_user.id
                )
            return

        update_customer_button.display = False

    def update_update_contact_button_state(
        self, selected_customer: Customer | None
    ) -> None:
        """Update the state of the update contact button based on permissions.

        Checks if the current user has permission to update contacts and
        if they are the sales representative for the selected customer.

        :param selected_customer: The currently selected customer.
        :type selected_customer: Customer | None
        """
        update_contact_button = self.query_one("#update-contact", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_CONTACT
        ):
            if selected_customer is not None:
                update_contact_button.display = (
                    selected_customer.sales_representative_id
                    == self.current_user.id
                )
            return

        update_contact_button.display = False

    def action_go_back(self) -> None:
        """Return to previous screen.

        Dismisses the screen with "back" action.
        """
        self.dismiss("back")

    @on(DataTable.RowHighlighted, "#customers-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Save highlighted customer id.

        Updates the selected_customer_id reactive variable when a row is highlighted
        in the customers table, which triggers the watcher to update related tables.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        customers_table = self.query_one("#customers-table", DataTable)
        # Get value from the cell
        customer_id = customers_table.get_cell(
            event.row_key, "customer_id"
        )
        # Update selected_attribute_id
        self.selected_customer_id = customer_id

    @on(DataTable.RowHighlighted, "#customer-contacts-table")
    def on_contact_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Save highlighted contact id.

        Updates the selected_contact_id reactive variable when a row is highlighted
        in the contacts table, which triggers the watcher to update phone numbers table.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        customer_contacts_table = self.query_one(
            "#customer-contacts-table", DataTable
        )
        # Prevent cases due to .clear() triggering a change in highlighted row
        if event.row_key not in customer_contacts_table.rows:
            return

        # Get value from the cell
        contact_id = customer_contacts_table.get_cell(
            event.row_key, "contact_id"
        )
        # Update selected_attribute_id
        self.selected_contact_id = contact_id

    @on(Button.Pressed, "#create-customer")
    def go_create_customer(self) -> None:
        """Navigate to create customer screen.

        Dismisses the screen with "create_customer" action.
        """
        self.dismiss("create_customer")

    @on(Button.Pressed, "#update-customer")
    def go_update_customer(self) -> None:
        """Navigate to update customer screen for selected customer.

        Dismisses the screen with a tuple containing action and customer ID.
        """
        self.dismiss(("update_customer", self.selected_customer_id))

    @on(Button.Pressed, "#create-contact")
    def go_create_contact(self) -> None:
        """Navigate to create contact screen.

        Dismisses the screen with "create_contact" action.
        """
        self.dismiss("create_contact")

    @on(Button.Pressed, "#update-contact")
    def go_update_contact(self) -> None:
        """Navigate to update contact screen for selected contact.

        Dismisses the screen with a tuple containing action and contact ID.
        """
        self.dismiss(("update_contact", self.selected_contact_id))


class CreateCustomerScreen(Screen):
    """Screen for creating a new customer in the EpicEvents CRM.

    Provides a form for entering customer details and associated contact
    information. Allows selection of an existing contact or creation of a new one.

    :param contacts: List of existing contacts to choose from.
    :type contacts: list[Contact]
    """

    SUB_TITLE = "CREATE CUSTOMERS"
    CSS_PATH = "../styles/create_customer_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self, contacts: list[Contact]) -> None:
        """Initialize the CreateCustomerScreen with available contacts.

        :param contacts: List of existing contacts to choose from.
        :type contacts: list[Contact]
        """
        super().__init__()
        self.contacts: list[Contact] = contacts
        self.customer_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (customer data,
        contact selection), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="create-customer-main-container"):
            with Container(
                id="customer-data", classes="customer-data-input-container"
            ):
                yield Label("Customer Last Name:", classes="form-label")
                yield Input(
                    placeholder="Doe",
                    id="customer_last_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Customer First Name:", classes="form-label")
                yield Input(
                    placeholder="John",
                    id="customer_first_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Company Name:", classes="form-label")
                yield Input(
                    placeholder="John Doe Corp",
                    id="company_name",
                    type="text",
                    classes="form-input",
                    validators=[
                        Length(
                            maximum=99,
                            failure_description="Name is too long.",
                        ),
                    ],
                )
            with Container(
                id="customer-contact",
                classes="customer-contact-input-container",
            ):
                with RadioSet(id="customer-contact-input-choice"):
                    yield RadioButton(
                        "Existing contact",
                        classes="customer-contact-radio-button",
                    )
                    yield RadioButton(
                        "New contact",
                        value=True,
                        classes="customer-contact-radio-button",
                    )
                with Container(
                    classes="customer-contact-select-input-container",
                    id="customer-contact-select-input-container",
                ):
                    contact_options = [
                        (
                            (contact.first_name + " " + contact.last_name),
                            contact,
                        )
                        for contact in self.contacts
                    ]
                    yield Select(
                        contact_options,
                        id="customer-contact-select",
                        prompt="Select a contact",
                    )
                with Container(
                    classes="customer-contact-form-input-container",
                    id="customer-contact-form-input-container",
                ):
                    yield Label("Contact Last Name", classes="form-label")
                    yield Input(
                        placeholder="Smith",
                        id="contact_last_name",
                        type="text",
                        max_length=50,
                        classes="form-input",
                        validators=[
                            Length(
                                minimum=1,
                                failure_description="Field cannot be empty.",
                            ),
                        ],
                    )
                    yield Label("Contact First Name", classes="form-label")
                    yield Input(
                        placeholder="Tom",
                        id="contact_first_name",
                        type="text",
                        max_length=50,
                        classes="form-input",
                        validators=[
                            Length(
                                minimum=1,
                                failure_description="Field cannot be empty.",
                            ),
                        ],
                    )
                    yield Label("Contact Email", classes="form-label")
                    yield Input(
                        placeholder="tom.smith@contact.com",
                        id="contact_email",
                        type="text",
                        max_length=100,
                        classes="form-input",
                        validators=[
                            Length(
                                minimum=1,
                                failure_description="Field cannot be empty.",
                            ),
                        ],
                    )
                    yield Label(
                        "Contact Phone Number", classes="form-label"
                    )
                    yield Input(
                        placeholder="+33 6 00 00 00 00",
                        id="contact_phone_number",
                        type="text",
                        max_length=20,
                        classes="form-input",
                        validators=[
                            Length(
                                minimum=1,
                                failure_description="Field cannot be empty.",
                            ),
                        ],
                    )
            with Container(classes="create-customer-buttons-container"):
                yield Button(
                    "Create",
                    id="create",
                    variant="primary",
                    classes="create-customer-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="create-customer-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for containers and hides the select container
        by default (showing new contact form instead).
        """
        customer_data_container = self.query_one(
            "#customer-data", Container
        )
        customer_contact_container = self.query_one(
            "#customer-contact", Container
        )
        customer_data_container.border_title = "Customer Data"
        customer_contact_container.border_title = "Contact Selection"

        # Hide select container for customer input by default:
        self.query_one(
            "#customer-contact-select-input-container", Container
        ).display = False

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
            self.query_one("#customer_last_name", Input),
            self.query_one("#customer_first_name", Input),
            self.query_one("#company_name", Input),
        ]

        widget_selects = []

        radio_set = self.query_one(
            "#customer-contact-input-choice", RadioSet
        )
        if radio_set.pressed_button.label == "Existing contact":
            widget_selects.append(
                self.query_one("#customer-contact-select", Select)
            )
        else:
            widget_inputs.extend(
                [
                    self.query_one("#contact_last_name", Input),
                    self.query_one("#contact_first_name", Input),
                    self.query_one("#contact_email", Input),
                    self.query_one("#contact_phone_number", Input),
                ]
            )

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

    @on(RadioSet.Changed, "#customer-contact-input-choice")
    def on_contact_input_choice_changed(
        self, event: RadioSet.Changed
    ) -> None:
        """Toggle containers' display based on user radio button input.

        Shows either the contact select or the new contact form container
        based on user choice.

        :param event: The radio set changed event.
        :type event: RadioSet.Changed
        """
        self._validate_form()
        select_container = self.query_one(
            "#customer-contact-select-input-container", Container
        )
        form_container = self.query_one(
            "#customer-contact-form-input-container", Container
        )

        if event.pressed.label == "Existing contact":
            select_container.display = True
            form_container.display = False
        else:
            select_container.display = False
            form_container.display = True

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        """Handle Create button press.

        Collects form data and dismisses screen with the customer data.
        """
        self._collect_form_data()
        self.dismiss(self.customer_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into customer_data dictionary.

        Retrieves values from all form fields and stores them in customer_data.
        Handles both existing contact selection and new contact creation.
        """
        radio_set = self.query_one(
            "#customer-contact-input-choice", RadioSet
        )

        # Get contact format depending on user input choice
        if radio_set.pressed_button.label == "Existing contact":
            # Existing contact : use Select value
            contact_data = self.query_one(
                "#customer-contact-select", Select
            ).value
        else:
            # New contact : use Form inputs values
            contact_data = {
                "last_name": self.query_one(
                    "#contact_last_name", Input
                ).value,
                "first_name": self.query_one(
                    "#contact_first_name", Input
                ).value,
                "email": self.query_one("#contact_email", Input).value,
                "phone_number": self.query_one(
                    "#contact_phone_number", Input
                ).value,
            }

        self.customer_data = {
            "customer_last_name": self.query_one(
                "#customer_last_name", Input
            ).value,
            "customer_first_name": self.query_one(
                "#customer_first_name", Input
            ).value,
            "company_name": self.query_one("#company_name", Input).value,
            "customer_contact": contact_data,
        }


class UpdateCustomerScreen(Screen):
    """Screen for updating an existing customer in the EpicEvents CRM.

    Provides a form pre-filled with existing customer data for modification.
    Allows updating personal details, company name, assigned contacts, and
    sales representative.

    :param customer_data: Dictionary containing all data of the customer to update.
    :type customer_data: dict[str, Any]
    :param contacts: List of existing contacts to choose from.
    :type contacts: list[Contact]
    :param sales_representatives: List of sales representatives to choose from.
    :type sales_representatives: list[Collaborator]
    """

    SUB_TITLE = "UPDATE CUSTOMERS"
    CSS_PATH = "../styles/update_customer_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(
        self,
        customer_data: dict[str, Any],
        contacts: list[Contact],
        sales_representatives: list[Collaborator],
    ) -> None:
        """Initialize the UpdateCustomerScreen with customer data and options.

        :param customer_data: Dictionary containing all data of the customer to update.
        :type customer_data: dict[str, Any]
        :param contacts: List of existing contacts to choose from.
        :type contacts: list[Contact]
        :param sales_representatives: List of sales representatives to choose from.
        :type sales_representatives: list[Collaborator]
        """
        super().__init__()
        self.customer_data: dict[str, Any] = customer_data
        self.updated_customer_data: dict[str, Any] = {}
        self.contacts: list[Contact] = contacts
        self.sales_representatives: list[Collaborator] = (
            sales_representatives
        )

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (personal data,
        contacts selection, sales representative selection), and footer with
        action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="update-customer-main-container"):
            yield Static(
                "Updating Customer: "
                f"{self.customer_data['customer_first_name']} "
                f"{self.customer_data['customer_last_name']}",
                classes="updating-customer-static",
            )
            with Container(
                id="update-customer-data",
                classes="update-customer-data-input-container",
            ):
                yield Label("Customer Last Name:")
                yield Input(
                    value=self.customer_data.get("customer_last_name", ""),
                    placeholder="Doe",
                    id="customer_last_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Customer First Name:")
                yield Input(
                    value=self.customer_data.get(
                        "customer_first_name", ""
                    ),
                    placeholder="John",
                    id="customer_first_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Company Name:")
                yield Input(
                    value=self.customer_data.get("company_name", ""),
                    placeholder="John Doe Corp",
                    id="company_name",
                    type="text",
                    classes="form-input",
                    validators=[
                        Length(
                            maximum=99,
                            failure_description="Name is too long.",
                        ),
                    ],
                )
            with Container(
                id="update-contact-data",
                classes="update-contact-data-select-container",
            ):
                contacts_options = [
                    Selection(
                        prompt=f"{contact.first_name} {contact.last_name}",
                        value=contact,
                        initial_state=contact
                        in self.customer_data["customer_contacts"],
                    )
                    for contact in self.contacts
                ]
                yield SelectionList(
                    *contacts_options,
                    id="update-customer-contacts-selection-list",
                )
            with Container(
                id="update-customer-sales-representative",
                classes="update-customer-sales-representative-input-container",
            ):
                # Add current collaborator if he is not from sales
                collab: Collaborator | None = self.customer_data.get(
                    "customer_sales_representative"
                )
                if collab not in self.sales_representatives:
                    self.sales_representatives.append(collab)
                # ===================================================
                sales_representatives_options = [
                    (
                        (
                            sales_representative.first_name
                            + " "
                            + sales_representative.last_name
                        ),
                        sales_representative,
                    )
                    for sales_representative in self.sales_representatives
                ]
                selected_sales_representative: Collaborator | None = next(
                    (
                        sales_representative
                        for sales_representative in self.sales_representatives
                        if sales_representative
                        == self.customer_data.get(
                            "customer_sales_representative"
                        )
                    ),
                    None,
                )
                select_kwargs = {
                    "id": "update-customer-sales-representative-select",
                    "prompt": "Select a sales representative",
                }
                if selected_sales_representative is not None:
                    select_kwargs["value"] = selected_sales_representative

                yield Select(
                    sales_representatives_options, **select_kwargs
                )
            with Container(classes="update-customer-buttons-container"):
                yield Button(
                    "Update",
                    id="update",
                    variant="primary",
                    classes="update-customer-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="update-customer-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets container border titles and subtitles for all form sections.
        """
        self.query_one(
            "#update-customer-data", Container
        ).border_title = "Personal Data"
        self.query_one(
            "#update-customer-data", Container
        ).border_subtitle = "Edit relevant fields"
        self.query_one(
            "#update-customer-sales-representative", Container
        ).border_title = "Sales Representative Selection"
        self.query_one(
            "#update-contact-data", Container
        ).border_title = "Assigned Contacts"
        self.query_one(
            "#update-contact-data", Container
        ).border_subtitle = "Click on contact to assign/unassign"

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
        of all input, select, and selection list fields.
        """
        widget_inputs = [
            self.query_one("#customer_last_name", Input),
            self.query_one("#customer_first_name", Input),
            self.query_one("#company_name", Input),
        ]

        widget_selects = [
            self.query_one(
                "#update-customer-sales-representative-select", Select
            ),
        ]

        widget_selection_lists = [
            self.query_one(
                "#update-customer-contacts-selection-list", SelectionList
            ),
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

        # Check that all selection lists are valid
        all_selection_lists = all(
            selection_list.selected
            for selection_list in widget_selection_lists
        )

        # Update reactive variable triggering watcher
        all_valid = (
            all_inputs_valid and all_selects_valid and all_selection_lists
        )
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

    @on(SelectionList.SelectedChanged)
    def show_selection_list_invalid_reasons(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        """Show validation error messages for changed selection list.

        :param event: The selection list changed event.
        :type event: SelectionList.SelectedChanged
        """
        self._validate_form()
        selection_list_widget = event.selection_list

        # If no options are selected
        if not selection_list_widget.selected:
            error_message = "At least one option must be selected."
            selection_list_widget.set_class(True, "-invalid")
            selection_list_widget.border_subtitle = error_message
        else:
            selection_list_widget.set_class(False, "-invalid")
            selection_list_widget.border_subtitle = None

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        """Handle Update button press.

        Collects form data and dismisses screen with the updated customer data.
        """
        self._collect_form_data()
        self.dismiss(self.updated_customer_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into updated_customer_data dictionary.

        Retrieves values from all form fields and stores them in updated_customer_data.
        """
        selected_sales_representative: Collaborator | None = (
            self.query_one(
                "#update-customer-sales-representative-select", Select
            ).value
        )
        selected_contacts: list[Contact] = [
            selection
            for selection in self.query_one(SelectionList).selected
        ]

        self.updated_customer_data = {
            "id": self.customer_data["customer_id"],
            "customer_first_name": self.query_one(
                "#customer_first_name", Input
            ).value,
            "customer_last_name": self.query_one(
                "#customer_last_name", Input
            ).value,
            "company_name": self.query_one("#company_name", Input).value,
            "customer_sales_representative": selected_sales_representative,
            "customer_contacts": selected_contacts,
        }


class CreateContactScreen(Screen):
    """Screen for creating a new contact in the EpicEvents CRM.

    Provides a form for entering contact details including name, email,
    and one or more phone numbers. Allows dynamically adding additional
    phone number fields.

    Note:
        This screen is used for creating standalone contacts that can
        later be associated with customers.
    """

    SUB_TITLE = "CREATE CONTACT"
    CSS_PATH = "../styles/create_contact_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        """Initialize the CreateContactScreen.

        Creates a new screen instance for contact creation.
        """
        super().__init__()
        self.contact_data: dict[str, Any] = {}
        self.phone_number_counter: int = 2

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (personal data,
        phone numbers), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="create-contact-main-container"):
            with Container(
                id="contact-data", classes="contact-data-input-container"
            ):
                yield Label("Contact Last Name:", classes="form-label")
                yield Input(
                    placeholder="Smith",
                    id="contact_last_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Contact First Name:", classes="form-label")
                yield Input(
                    placeholder="Tom",
                    id="contact_first_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Email:", classes="form-label")
                yield Input(
                    placeholder="tom.smith@contact.com",
                    id="contact_email",
                    type="text",
                    max_length=100,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
            with Container(
                id="phone-number", classes="phone-number-input-container"
            ):
                yield Label(
                    "Phone Number 1:",
                    id="phone_label_1",
                    classes="form-label",
                )
                yield Input(
                    placeholder="+33 6 00 00 00 00",
                    id="phone_number_1",
                    type="text",
                    max_length=20,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                with Container(
                    id="phone-number-buttons-container",
                    classes="phone-number-buttons-container",
                ):
                    yield Button(
                        "Add a number",
                        id="add-phone-number",
                        variant="default",
                    )
            with Container(classes="create-contact-buttons-container"):
                yield Button(
                    "Create",
                    id="create",
                    variant="primary",
                    classes="create-contact-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="create-contact-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for contact data and phone number containers.
        """
        contact_data_container = self.query_one("#contact-data", Container)
        phone_number_container = self.query_one("#phone-number", Container)
        contact_data_container.border_title = "Personal Data"
        phone_number_container.border_title = "Phone Numbers"

    @on(Button.Pressed, "#add-phone-number")
    def on_add_phone_number(self) -> None:
        """Add a new phone number input field.

        Dynamically adds a new label and input field for an additional phone number
        before the phone number buttons container, and increments the counter.
        """
        container = self.query_one("#phone-number", Container)
        # New label
        label = Label(
            f"Phone Number {self.phone_number_counter}:",
            classes="form-label",
            id=f"phone_label_{self.phone_number_counter}",
        )
        # New input
        input_field = Input(
            id=f"phone_number_{self.phone_number_counter}",
            placeholder="+33 6 00 00 00 00",
            type="text",
            max_length=20,
            classes="form-input",
            validators=[
                Length(
                    minimum=1,
                    failure_description="Field cannot be empty.",
                ),
            ],
        )

        # Add widgets to container
        container.mount(label, before="#phone-number-buttons-container")
        container.mount(
            input_field, before="#phone-number-buttons-container"
        )

        # Increment phone counter
        self.phone_number_counter += 1

        # Update form validation
        self._validate_form()

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
        of all input fields, including dynamically added phone number fields.
        """
        widget_inputs = [
            self.query_one("#contact_last_name", Input),
            self.query_one("#contact_first_name", Input),
            self.query_one("#contact_email", Input),
        ]

        # Add all phone number input fields
        for input_widget in self.query(Input):
            if input_widget.id and input_widget.id.startswith(
                "phone_number_"
            ):
                widget_inputs.append(input_widget)

        # Check that all input fields are valid
        all_inputs_valid = all(
            widget_input.validate(widget_input.value).is_valid
            for widget_input in widget_inputs
        )

        # Update reactive variable triggering watcher
        all_valid = all_inputs_valid
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

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        """Handle Create button press.

        Collects form data and dismisses screen with the contact data.
        """
        self._collect_form_data()
        self.dismiss(self.contact_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into contact_data dictionary.

        Retrieves values from all form fields and stores them in contact_data,
        including all phone numbers from dynamically added fields.
        """
        all_inputs = self.query(Input)
        phone_numbers: list[str] = []

        for input in all_inputs:
            if (
                input.id
                and input.id.startswith("phone_number_")
                and input.value
            ):
                phone_numbers.append(input.value)

        self.contact_data = {
            "contact_last_name": self.query_one(
                "#contact_last_name", Input
            ).value,
            "contact_first_name": self.query_one(
                "#contact_first_name", Input
            ).value,
            "email": self.query_one("#contact_email", Input).value,
            "phone_numbers": phone_numbers,
        }


class UpdateContactScreen(Screen):
    """Screen for updating an existing contact in the EpicEvents CRM.

    Provides a form pre-filled with existing contact data for modification.
    Allows updating personal details and phone numbers, with the ability to
    add additional phone number fields dynamically.

    :param contact_data: Dictionary containing all data of the contact to update.
    :type contact_data: dict[str, Any]
    """

    SUB_TITLE = "UPDATE CONTACT"
    CSS_PATH = "../styles/update_contact_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self, contact_data: dict[str, Any]) -> None:
        """Initialize the UpdateContactScreen with contact data.

        :param contact_data: Dictionary containing all data of the contact to update.
        :type contact_data: dict[str, Any]
        """
        super().__init__()
        self.contact_data: dict[str, Any] = contact_data
        self.updated_contact_data: dict[str, Any] = {}
        # Counter for additional phone numbers (starts after the existing ones)
        self.phone_number_counter: int = len(
            contact_data.get("phone_numbers", [])
        )

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (personal data,
        phone numbers), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="update-contact-main-container"):
            yield Static(
                f"Updating Contact: {self.contact_data['contact_first_name']} {self.contact_data['contact_last_name']}",
                classes="updating-contact-static",
            )
            with Container(
                id="update-contact-data",
                classes="update-contact-data-input-container",
            ):
                yield Label("Contact Last Name:", classes="form-label")
                yield Input(
                    value=self.contact_data.get("contact_last_name", ""),
                    placeholder="Smith",
                    id="contact_last_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Contact First Name:", classes="form-label")
                yield Input(
                    value=self.contact_data.get("contact_first_name", ""),
                    placeholder="Tom",
                    id="contact_first_name",
                    type="text",
                    max_length=50,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Email:", classes="form-label")
                yield Input(
                    value=self.contact_data.get("email", ""),
                    placeholder="tom.smith@contact.com",
                    id="contact_email",
                    type="text",
                    max_length=100,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
            with Container(
                id="update-phone-number",
                classes="update-phone-number-input-container",
            ):
                # Loads existing phone numbers
                for i, phone in enumerate(
                    self.contact_data.get("phone_numbers", [])
                ):
                    yield Label(
                        f"Phone Number {i + 1}:",
                        classes="form-label",
                        id=f"phone_label_{i}",
                    )
                    yield Input(
                        value=phone,
                        id=f"phone_number_{i}",
                        placeholder="+33 6 00 00 00 00",
                        type="text",
                        max_length=20,
                        classes="form-input",
                        validators=[
                            Length(
                                minimum=1,
                                failure_description="Field cannot be empty.",
                            ),
                        ],
                    )
                with Container(
                    classes="update-phone-number-buttons-container"
                ):
                    yield Button(
                        "Add a number",
                        id="add-phone-number",
                        variant="default",
                    )
            with Container(classes="update-contact-buttons-container"):
                yield Button(
                    "Update",
                    id="update",
                    variant="primary",
                    classes="update-contact-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="update-contact-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles and subtitles for personal data and phone number sections.
        """
        self.query_one(
            "#update-contact-data", Container
        ).border_title = "Personal Data"
        self.query_one(
            "#update-contact-data", Container
        ).border_subtitle = "Edit relevant fields"
        self.query_one(
            "#update-phone-number", Container
        ).border_title = "Phone Numbers"
        self.query_one(
            "#update-phone-number", Container
        ).border_subtitle = "Edit relevant fields"

    @on(Button.Pressed, "#add-phone-number")
    def on_add_phone_number(self) -> None:
        """Add a new phone number input field.

        Dynamically adds a new label and input field for an additional phone number
        before the phone number buttons container, and increments the counter.
        """
        container = self.query_one("#update-phone-number", Container)
        buttons_container = self.query_one(
            ".update-phone-number-buttons-container", Container
        )

        label = Label(
            f"Phone Number {self.phone_number_counter + 1}:",
            classes="form-label",
            id=f"phone_label_{self.phone_number_counter + 1}",
        )
        input_field = Input(
            placeholder="00 12 34 56 78",
            id=f"phone_number_{self.phone_number_counter + 1}",
            type="text",
            classes="form-input",
        )

        container.mount(label, before=buttons_container)
        container.mount(input_field, before=buttons_container)

        self.phone_number_counter += 1

        # Update form validation
        self._validate_form()

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
        of all input fields, including dynamically added phone number fields.
        """
        widget_inputs = [
            self.query_one("#contact_last_name", Input),
            self.query_one("#contact_first_name", Input),
            self.query_one("#contact_email", Input),
        ]

        # Add all phone number input fields
        for input_widget in self.query(Input):
            if input_widget.id and input_widget.id.startswith(
                "phone_number_"
            ):
                widget_inputs.append(input_widget)

        # Check that all input fields are valid
        all_inputs_valid = all(
            widget_input.validate(widget_input.value).is_valid
            for widget_input in widget_inputs
        )

        # Update reactive variable triggering watcher
        all_valid = all_inputs_valid
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

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        """Handle Update button press.

        Collects form data and dismisses screen with the updated contact data.
        """
        self._collect_form_data()
        self.dismiss(self.updated_contact_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into updated_contact_data dictionary.

        Retrieves values from all form fields and stores them in updated_contact_data,
        including all phone numbers from dynamically added fields.
        """
        all_inputs = self.query(Input)
        phone_numbers: list[str] = []

        for input in all_inputs:
            if (
                input.id
                and input.id.startswith("phone_number_")
                and input.value
            ):
                phone_numbers.append(input.value)

        self.updated_contact_data = {
            "id": self.contact_data["contact_id"],
            "last_name": self.query_one("#contact_last_name", Input).value,
            "first_name": self.query_one(
                "#contact_first_name", Input
            ).value,
            "email": self.query_one("#contact_email", Input).value,
            "phone_numbers": phone_numbers,
        }
