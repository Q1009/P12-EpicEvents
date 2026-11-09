from typing import Any, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import DescendantBlur
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.validation import Length
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)
from textual.widgets._select import SelectCurrent

from collaborators.collaborator_model import Collaborator, Department
from permissions.permission_model import Permission
from services.permission_services import PermissionServices


class CollaboratorScreen(Screen):
    """Screen for displaying and managing collaborators in the EpicEvents CRM.

    Provides a comprehensive view of all collaborators with their associated
    customers and events. Allows navigation to create, update,
    delete collaborators, and consult related customer or event information.

    :param collaborators: List of Collaborator objects to display in the table.
    :type collaborators: list[Collaborator]
    :param user: The currently authenticated collaborator.
    :type user: Collaborator
    """

    SUB_TITLE = "COLLABORATORS"
    CSS_PATH = "../styles/collaborator_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_collaborator_id: reactive[int | None] = reactive(None)
    selected_customer_id: reactive[int | None] = reactive(None)
    selected_event_id: reactive[int | None] = reactive(None)

    BUTTON_PERMISSIONS: ClassVar[dict[str, set[Permission]]] = {
        "create-collaborator": {Permission.CREATE_COLLABORATOR},
        "update-collaborator": {Permission.UPDATE_COLLABORATOR},
        "delete-collaborator": {Permission.DELETE_COLLABORATOR},
        "consult-customer": {Permission.READ_ALL_CUSTOMERS},
        "consult-event": {Permission.READ_ALL_EVENTS},
    }

    def __init__(
        self, collaborators: list[Collaborator], user: Collaborator
    ) -> None:
        """Initialize the CollaboratorScreen with collaborators and user data.

        :param collaborators: List of Collaborator objects to display
        in the table.
        :type collaborators: list[Collaborator]
        :param user: The currently authenticated collaborator.
        :type user: Collaborator
        """
        super().__init__()
        self.collaborators: list[Collaborator] = collaborators
        self.current_user: Collaborator = user
        self.selected_collaborator_first_name: str | None = None
        self.selected_collaborator_last_name: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with data tables (collaborators,
        customers, events), action buttons, and footer.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="collaborator-main-container"):
            yield DataTable(id="collaborators-table")
            yield DataTable(id="collaborator-customers-table")
            yield DataTable(id="collaborator-events-table")
            with Container(classes="collaborator-buttons-container"):
                yield Button(
                    "Create Collaborator",
                    id="create-collaborator",
                    variant="primary",
                )
                yield Button(
                    "Update Collaborator",
                    id="update-collaborator",
                    variant="warning",
                )
                yield Button(
                    "Delete Collaborator",
                    id="delete-collaborator",
                    variant="error",
                )
            with Container(classes="customers-events-buttons-container"):
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
        and selects the first collaborator if the list is not empty.
        """
        self.build_collaborators_table()
        self.build_collaborator_customers_table()
        self.build_collaborator_events_table()
        self.set_button_state("create-collaborator")
        self.set_button_state("update-collaborator")
        self.set_button_state("delete-collaborator")
        self.set_button_state("consult-customer")
        self.set_button_state("consult-event")

        # Setting initial selected_collaborator_id: triggering the watcher
        if self.collaborators:
            self.selected_collaborator_id = self.collaborators[0].id

    def build_collaborators_table(self) -> None:
        """Build and configure the collaborators data table.

        Sets up column headers for displaying collaborator information.
        """
        table = self.query_one("#collaborators-table", DataTable)
        table.border_title = "Collaborators"
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Configure table columns
        table.add_column("ID", key="collaborator_id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")
        table.add_column("Email", key="email")
        table.add_column("Department", key="department")
        table.add_column("Customers", key="nb_customers")
        table.add_column("Events", key="nb_department")

        table.loading = True
        self.load_collaborators(table)

    def load_collaborators(self, table: DataTable) -> None:
        """Load collaborator data into the collaborators table.

        Populates the table with collaborator data including department names,
        number of assigned customers, and number of assigned events.

        :param table: The DataTable widget to populate with collaborator data.
        :type table: DataTable
        """
        table.clear()

        for collaborator in self.collaborators:
            # Department
            department = collaborator.department.name.name
            # Number of customers
            nb_customers = len(collaborator.customers)
            # Number of events
            nb_events = len(collaborator.events)

            table.add_row(
                collaborator.id,
                collaborator.first_name,
                collaborator.last_name,
                collaborator.email,
                department,
                nb_customers,
                nb_events,
            )

        table.loading = False

    def build_collaborator_customers_table(self) -> None:
        """Build and configure the customer data table.

        Sets up column headers for displaying customers assigned to the
        selected collaborator.
        """
        table = self.query_one("#collaborator-customers-table", DataTable)
        table.border_title = "Assigned Customers"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="customer_id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")

        table.loading = True

    def load_collaborator_customers(
        self, table: DataTable, collaborator: Collaborator
    ) -> None:
        """Load customer data for the selected collaborator.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param collaborator: The Collaborator object whose customers to load.
        :type collaborator: Collaborator
        """
        table.clear()

        for customer in collaborator.customers:
            table.add_row(
                customer.id,
                customer.first_name,
                customer.last_name,
            )

        table.loading = False

    def build_collaborator_events_table(self) -> None:
        """Build and configure the event data table.

        Sets up column headers for displaying events assigned to the
        selected collaborator.
        """
        table = self.query_one("#collaborator-events-table", DataTable)
        table.border_title = "Assigned Events"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="event_id")
        table.add_column("Event Name", key="event_name")

        table.loading = True

    def load_collaborator_events(
        self, table: DataTable, collaborator: Collaborator
    ) -> None:
        """Load event data for the selected collaborator.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param collaborator: The Collaborator object whose events to load.
        :type collaborator: Collaborator
        """
        table.clear()

        for event in collaborator.events:
            table.add_row(
                event.id,
                event.name,
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

    def watch_selected_collaborator_id(self, new_id: int | None) -> None:
        """Watcher that loads associated data based on
        the selected collaborator.

        Updates customer and event tables, and selected IDs when a new
        collaborator is selected in the collaborators table. Also updates
        button states for consult actions.

        :param new_id: The ID of the newly selected collaborator.
        :type new_id: int | None
        """
        collaborator_customers_table = self.query_one(
            "#collaborator-customers-table", DataTable
        )
        collaborator_events_table = self.query_one(
            "#collaborator-events-table", DataTable
        )

        if new_id is None:
            collaborator_customers_table.clear()
            self.selected_customer_id = None
            collaborator_events_table.clear()
            self.selected_event_id = None
        else:
            # Get collaborator by ID
            selected_collaborator: Collaborator | None = next(
                (c for c in self.collaborators if c.id == new_id), None
            )
            if selected_collaborator:
                # Load associated widgets based on selected_collaborator
                self.load_collaborator_customers(
                    collaborator_customers_table, selected_collaborator
                )
                self.load_collaborator_events(
                    collaborator_events_table, selected_collaborator
                )
                # Update other selected_attributes_id
                self.selected_collaborator_first_name = (
                    selected_collaborator.first_name
                )
                self.selected_collaborator_last_name = (
                    selected_collaborator.last_name
                )
                if selected_collaborator.customers:
                    self.selected_customer_id = (
                        selected_collaborator.customers[0].id
                    )
                else:
                    self.selected_customer_id = None
                if selected_collaborator.events:
                    self.selected_event_id = selected_collaborator.events[
                        0
                    ].id
                else:
                    self.selected_event_id = None
            else:
                # Update other selected_attributes_id
                self.selected_customer_id = None
                self.selected_event_id = None

        # Enable or disable consult buttons
        self.update_consult_customer_button_state()
        self.update_consult_event_button_state()

    def update_consult_customer_button_state(self) -> None:
        """Update the state of the consult customer button based
        on permissions.

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

    def action_go_back(self) -> None:
        """Return to previous screen.

        Dismisses the screen with "back" action.
        """
        self.dismiss("back")

    def _delete_collaborator(self, collaborator_id: int | None) -> None:
        """Callback for delete confirmation.

        Dismisses the screen with a tuple containing the delete action and
        the collaborator ID to be deleted.

        :param collaborator_id: The ID of the collaborator to delete.
        :type collaborator_id: int | None
        """
        self.dismiss(("delete_collaborator", collaborator_id))

    @on(DataTable.RowHighlighted, "#collaborators-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Save highlighted collaborator id.

        Updates the selected_collaborator_id reactive variable when a row is
        highlighted in the collaborators table, which triggers the watcher.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        collaborators_table = self.query_one(
            "#collaborators-table", DataTable
        )
        # Get value from the cell
        collaborator_id = collaborators_table.get_cell(
            event.row_key, "collaborator_id"
        )
        # Update selected_attribute_id
        self.selected_collaborator_id = collaborator_id

    @on(DataTable.RowHighlighted, "#collaborator-customers-table")
    def on_customer_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Save highlighted customer id.

        Updates the selected_customer_id reactive variable when a row is
        highlighted in the customer table.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        collaborator_customers_table = self.query_one(
            "#collaborator-customers-table", DataTable
        )
        # Get value from the cell
        customer_id = collaborator_customers_table.get_cell(
            event.row_key, "customer_id"
        )
        # Update selected_attribute_id
        self.selected_customer_id = customer_id

    @on(DataTable.RowHighlighted, "#collaborator-events-table")
    def on_event_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Save highlighted event id.

        Updates the selected_event_id reactive variable when a row is
        highlighted in the event table.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        collaborator_events_table = self.query_one(
            "#collaborator-events-table", DataTable
        )
        # Get value from the cell
        event_id = collaborator_events_table.get_cell(
            event.row_key, "event_id"
        )
        # Update selected_attribute_id
        self.selected_event_id = event_id

    @on(Button.Pressed, "#create-collaborator")
    def go_create_collaborator(self) -> None:
        """Navigate to create collaborator screen.

        Dismisses the screen with "create_collaborator" action.
        """
        self.dismiss("create_collaborator")

    @on(Button.Pressed, "#update-collaborator")
    def go_update_collaborator(self) -> None:
        """Navigate to update collaborator screen for selected collaborator.

        Dismisses the screen with a tuple containing action and
        collaborator ID.
        """
        self.dismiss(
            ("update_collaborator", self.selected_collaborator_id)
        )

    @on(Button.Pressed, "#delete-collaborator")
    def go_delete_collaborator(self) -> None:
        """Display delete confirmation modal for selected collaborator.

        Creates and pushes a DeleteCollaboratorScreen modal with the selected
        collaborator's information, and registers a callback for handling
        the delete confirmation.
        """
        if self.selected_collaborator_id is not None:
            delete_collaborator_screen = DeleteCollaboratorScreen(
                self.selected_collaborator_id,
                self.selected_collaborator_first_name,
                self.selected_collaborator_last_name,
            )
            self.app.push_screen(
                delete_collaborator_screen,
                callback=self._delete_collaborator,
            )

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


class CreateCollaboratorScreen(Screen):
    """Screen for creating a new collaborator in the EpicEvents CRM.

    Provides a form for entering collaborator details including name,
    password, and department assignment.

    :param departments: List of existing departments to choose from.
    :type departments: list[Department]
    """

    SUB_TITLE = "CREATE COLLABORATOR"
    CSS_PATH = "../styles/create_collaborator_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self, departments: list[Department]) -> None:
        """Initialize the CreateCollaboratorScreen with available departments.

        :param departments: List of existing departments to choose from.
        :type departments: list[Department]
        """
        super().__init__()
        self.departments: list[Department] = departments
        self.collaborator_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (personal data,
        department selection), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="create-collaborator-main-container"):
            with Container(
                id="collaborator-data",
                classes="collaborator-data-input-container",
            ):
                yield Label(
                    "Collaborator Last Name:", classes="form-label"
                )
                yield Input(
                    placeholder="Doe",
                    id="collaborator_last_name",
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
                yield Label(
                    "Collaborator First Name:", classes="form-label"
                )
                yield Input(
                    placeholder="John",
                    id="collaborator_first_name",
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
                yield Label("Password:", classes="form-label")
                yield Input(
                    placeholder="my-secure-password",
                    id="password",
                    type="text",
                    max_length=100,
                    password=True,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
            with Container(
                id="collaborator-department",
                classes="collaborator-department-input-container",
            ):
                department_options = [
                    (
                        department.name.name,
                        department,
                    )
                    for department in self.departments
                ]
                yield Select(
                    department_options,
                    id="collaborator-department-select",
                    prompt="Select a department",
                )
            with Container(
                classes="create-collaborator-buttons-container"
            ):
                yield Button(
                    "Create",
                    id="create",
                    variant="primary",
                    classes="create-collaborator-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="create-collaborator-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for personal data and department
        selection containers.
        """
        collaborator_data_container = self.query_one(
            "#collaborator-data", Container
        )
        collaborator_department_container = self.query_one(
            "#collaborator-department", Container
        )
        collaborator_data_container.border_title = "Personal Data"
        collaborator_department_container.border_title = (
            "Department Selection"
        )

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
            self.query_one("#collaborator_last_name", Input),
            self.query_one("#collaborator_first_name", Input),
            self.query_one("#password", Input),
        ]

        widget_selects = [
            self.query_one("#collaborator-department-select", Select),
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

        Collects form data and dismisses screen with the collaborator data.
        """
        self._collect_form_data()
        self.dismiss(self.collaborator_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into collaborator_data dictionary.

        Retrieves values from all form fields and stores them
        in collaborator_data.
        """
        self.collaborator_data = {
            "collaborator_last_name": self.query_one(
                "#collaborator_last_name", Input
            ).value,
            "collaborator_first_name": self.query_one(
                "#collaborator_first_name", Input
            ).value,
            "password": self.query_one("#password", Input).value,
            "department": self.query_one(
                "#collaborator-department-select", Select
            ).value,
        }


class UpdateCollaboratorScreen(Screen):
    """Screen for updating an existing collaborator in the EpicEvents CRM.

    Provides a form pre-filled with existing collaborator
    data for modification.
    Allows updating personal details and department assignment.

    :param collaborator_data: Dictionary containing all data
    of the collaborator to update.
    :type collaborator_data: dict[str, Any]
    :param departments: List of existing departments to choose from.
    :type departments: list[Department]
    """

    SUB_TITLE = "UPDATE COLLABORATOR"
    CSS_PATH = "../styles/update_collaborator_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(
        self,
        collaborator_data: dict[str, Any],
        departments: list[Department],
    ) -> None:
        """Initialize the UpdateCollaboratorScreen with
        collaborator data and options.

        :param collaborator_data: Dictionary containing all data
        of the collaborator to update.
        :type collaborator_data: dict[str, Any]
        :param departments: List of existing departments to choose from.
        :type departments: list[Department]
        """
        super().__init__()
        self.collaborator_data: dict[str, Any] = collaborator_data
        self.updated_collaborator_data: dict[str, Any] = {}
        self.departments: list[Department] = departments

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (personal data,
        department selection), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="update-collaborator-main-container"):
            yield Static(
                "Updating Collaborator: "
                f"{self.collaborator_data['collaborator_first_name']} "
                f"{self.collaborator_data['collaborator_last_name']}",
                id="updating-collaborator-static",
                classes="updating-collaborator-static",
            )
            with Container(
                id="update-collaborator-data",
                classes="update-collaborator-data-input-container",
            ):
                yield Label("Collaborator Last Name:")
                yield Input(
                    value=self.collaborator_data.get(
                        "collaborator_last_name", ""
                    ),
                    placeholder="Doe",
                    id="collaborator_last_name",
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
                yield Label("Collaborator First Name:")
                yield Input(
                    value=self.collaborator_data.get(
                        "collaborator_first_name", ""
                    ),
                    placeholder="John",
                    id="collaborator_first_name",
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
            with Container(
                id="update-collaborator-department",
                classes="update-collaborator-department-input-container",
            ):
                department_options = [
                    (
                        department.name.name,
                        department,
                    )
                    for department in self.departments
                ]
                yield Select(
                    department_options,
                    id="update-collaborator-department-select",
                    prompt="Select a department",
                    value=self.collaborator_data.get("department"),
                )
            with Container(
                classes="update-collaborator-buttons-container"
            ):
                yield Button(
                    "Update",
                    id="update",
                    variant="primary",
                    classes="update-collaborator-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="update-collaborator-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for personal data and department
        selection containers.
        """
        collaborator_data_container = self.query_one(
            "#update-collaborator-data", Container
        )
        collaborator_department_container = self.query_one(
            "#update-collaborator-department", Container
        )
        collaborator_data_container.border_title = "Personal Data"
        collaborator_data_container.border_subtitle = (
            "Edit relevant fields"
        )
        collaborator_department_container.border_title = (
            "Department Selection"
        )

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
            self.query_one("#collaborator_last_name", Input),
            self.query_one("#collaborator_first_name", Input),
        ]

        widget_selects = [
            self.query_one(
                "#update-collaborator-department-select", Select
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

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        """Handle Update button press.

        Collects form data and dismisses screen with
        the updated collaborator data.
        """
        self._collect_form_data()
        self.dismiss(self.updated_collaborator_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into updated_collaborator_data dictionary.

        Retrieves values from all form fields and stores them
        in updated_collaborator_data.
        """
        selected_department: Department | None = self.query_one(
            "#update-collaborator-department-select", Select
        ).value

        self.updated_collaborator_data = {
            "id": self.collaborator_data["collaborator_id"],
            "first_name": self.query_one(
                "#collaborator_first_name", Input
            ).value,
            "last_name": self.query_one(
                "#collaborator_last_name", Input
            ).value,
            "department": selected_department,
        }


class DeleteCollaboratorScreen(ModalScreen):
    """Modal screen for confirming collaborator deletion.

    Displays a confirmation dialog with the collaborator's name and
    provides buttons to confirm or cancel the deletion.

    :param collaborator_id: The ID of the collaborator to delete.
    :type collaborator_id: int | None
    :param collaborator_first_name: First name of the collaborator to delete.
    :type collaborator_first_name: str | None
    :param collaborator_last_name: Last name of the collaborator to delete.
    :type collaborator_last_name: str | None
    """

    CSS_PATH = "../styles/delete_collaborator_screen.tcss"

    def __init__(
        self,
        collaborator_id: int | None,
        collaborator_first_name: str | None,
        collaborator_last_name: str | None,
    ) -> None:
        """Initialize the DeleteCollaboratorScreen with
        collaborator information.

        :param collaborator_id: The ID of the collaborator to delete.
        :type collaborator_id: int | None
        :param collaborator_first_name: First name of
        the collaborator to delete.
        :type collaborator_first_name: str | None
        :param collaborator_last_name: Last name of the collaborator to delete.
        :type collaborator_last_name: str | None
        """
        super().__init__()
        self.collaborator_id: int | None = collaborator_id
        self.collaborator_first_name: str | None = collaborator_first_name
        self.collaborator_last_name: str | None = collaborator_last_name

    def compose(self) -> ComposeResult:
        """Compose the modal screen UI components.

        Creates a container with confirmation message and action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        with Container(
            id="delete-collaborator-main-container",
            classes="delete-collaborator-main-container",
        ):
            yield Label(
                "Are you sure you want to delete",
                id="updating-collaborator-message-start-label",
                classes="updating-collaborator-message-start-label",
            )
            yield Label(
                f"{self.collaborator_first_name} "
                f"{self.collaborator_last_name}",
                id="updating-collaborator-fullname-label",
                classes="updating-collaborator-fullname-label",
            )
            yield Label(
                "from the system ?",
                id="updating-collaborator-message-end-label",
                classes="updating-collaborator-message-end-label",
            )
            with Container(
                id="delete-collaborator-buttons-container",
                classes="delete-collaborator-buttons-container",
            ):
                yield Button(
                    "Delete",
                    id="delete",
                    variant="error",
                    classes="delete-collaborator-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="delete-collaborator-button",
                )

    @on(Button.Pressed, "#delete")
    def go_delete(self) -> None:
        """Handle Delete button press.

        Dismisses the modal with the collaborator ID to confirm deletion.
        """
        self.dismiss(self.collaborator_id)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses the modal without data (cancels deletion).
        """
        self.dismiss(None)
