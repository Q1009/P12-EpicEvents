from typing import Any, ClassVar

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import DescendantBlur
from textual.reactive import reactive
from textual.screen import Screen
from textual.validation import Integer, Length
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    MaskedInput,
    RadioButton,
    RadioSet,
    Select,
    Static,
    TextArea,
)
from textual.widgets._select import SelectCurrent

from collaborators.collaborator_model import Collaborator
from contracts.contract_model import Contract
from events.event_model import Event, Location
from permissions.permission_model import Permission
from services.date_services import format_french_datetime
from services.permission_services import PermissionServices


class EventScreen(Screen):
    """Screen for displaying and managing events in the EpicEvents CRM.

    Provides a comprehensive view of all events with filtering capabilities,
    detailed information display for selected events, and navigation options
    for creating, updating, and consulting related entities.

    :param events: List of Event objects to display in the table.
    :type events: list[Event]
    :param user: The currently authenticated collaborator.
    :type user: Collaborator
    :param event_id: Optional ID of an event to pre-select in the table.
    :type event_id: int | None
    :param filtered_table_supported: Flag indicating if table shows only unsupported events.
    :type filtered_table_supported: bool
    :param filtered_table_ownership: Flag indicating if table shows only user's events.
    :type filtered_table_ownership: bool
    """

    SUB_TITLE = "EVENTS"
    CSS_PATH = "../styles/event_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("s", "filter_unsupported_events", "Show Unsupported Events"),
        ("e", "filter_user_events_as_support", "Show Affected Events"),
        ("r", "filter_reset", "Show All Events"),
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_event_id: reactive[int | None] = reactive(None)

    BUTTON_PERMISSIONS: ClassVar[dict[str, set[Permission]]] = {
        "create-event": {Permission.CREATE_EVENT},
        "update-event": {
            Permission.UPDATE_ALL_EVENTS,
            Permission.UPDATE_OWN_EVENTS,
        },
        "create-location": {Permission.CREATE_LOCATION},
        "update-location": {Permission.UPDATE_LOCATION},
        "consult-customer": {Permission.READ_ALL_CUSTOMERS},
        "consult-contract": {Permission.READ_ALL_CONTRACTS},
    }

    def __init__(
        self,
        events: list[Event],
        user: Collaborator,
        event_id: int | None = None,
        filtered_table_supported: bool = False,
        filtered_table_ownership: bool = False,
    ) -> None:
        """Initialize the EventScreen with events and user data.

        :param events: List of Event objects to display in the table.
        :type events: list[Event]
        :param user: The currently authenticated collaborator.
        :type user: Collaborator
        :param event_id: Optional ID of an event to pre-select in the table.
        :type event_id: int | None
        :param filtered_table_supported: Flag for unsupported events filter.
        :type filtered_table_supported: bool
        :param filtered_table_ownership: Flag for user ownership filter.
        :type filtered_table_ownership: bool
        """
        super().__init__()
        self.events: list[Event] = events
        self.current_user: Collaborator = user
        self.pre_selected_event_id: int | None = event_id
        self.selected_contract_id: int | None = None
        self.selected_location_id: int | None = None
        self.selected_customer_id: int | None = None
        self.filtered_table_supported: bool = filtered_table_supported
        self.filtered_table_ownership: bool = filtered_table_ownership

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with data tables and buttons,
        and footer. Includes tables for events, location, customer, contract,
        and notes, along with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="event-main-container"):
            yield DataTable(id="events-table")
            yield DataTable(id="event-location-table")
            yield DataTable(id="event-customer-table")
            yield TextArea(id="event-notes-text-area", read_only=True)
            yield DataTable(id="event-contract-table")
            with Container(classes="event-location-buttons-container"):
                yield Button(
                    "Create Event",
                    id="create-event",
                    variant="primary",
                )
                yield Button(
                    "Update Event",
                    id="update-event",
                    variant="warning",
                )
                yield Button(
                    "Create Location",
                    id="create-location",
                    variant="primary",
                )
                yield Button(
                    "Update Location",
                    id="update-location",
                    variant="warning",
                )
            with Container(classes="customer-contract-buttons-container"):
                yield Button(
                    "Consult Customer",
                    id="consult-customer",
                    variant="primary",
                )
                yield Button(
                    "Consult Contract",
                    id="consult-contract",
                    variant="warning",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Builds all data tables, sets button states based on permissions,
        and handles pre-selected event if provided.
        """
        self.build_events_table()
        self.build_event_contract_table()
        self.build_event_notes_text_area()
        self.build_event_location_table()
        self.build_event_customer_table()
        self.set_button_state("create-event")
        self.set_button_state("update-event")
        self.set_button_state("create-location")
        self.set_button_state("update-location")
        self.set_button_state("consult-customer")
        self.set_button_state("consult-contract")

        # Setting initial selected_event_id: triggering the watcher
        # If a event id was given to constructor
        if self.pre_selected_event_id is not None:
            event = next(
                (
                    e
                    for e in self.events
                    if e.id == self.pre_selected_event_id
                ),
                None,
            )
            if event:
                # Moving cursor will update selected_event_id
                row_index = self.events.index(event)
                self.query_one("#events-table", DataTable).move_cursor(
                    row=row_index
                )
        # If not, use first event
        elif self.events:
            self.selected_event_id = self.events[0].id

    def build_events_table(self) -> None:
        """Build and configure the events data table.

        Sets up column headers and loads event data into the table.
        """
        table = self.query_one("#events-table", DataTable)
        table.border_title = "Events"
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Configure table columns
        table.add_column("ID", key="event_id")
        table.add_column("Name", key="event_name")
        table.add_column("Customer", key="event_customer")
        table.add_column(
            "Support Representative", key="support_representative"
        )
        table.add_column("Start Date", key="event_start_date")
        table.add_column("End Date", key="event_end_date")
        table.add_column("Attendees", key="event_attendees")

        table.loading = True
        self.load_events(table)

    def load_events(self, table: DataTable) -> None:
        """Load event data into the events table.

        Populates the table with event data including customer names,
        support representative names, and formatted dates.

        :param table: The DataTable widget to populate with event data.
        :type table: DataTable
        """
        table.clear()

        for event in self.events:
            # Customer
            customer = (
                event.contract.customer.first_name
                + " "
                + event.contract.customer.last_name
            )
            # Support Representative
            if event.support_representative:
                support_representative = (
                    event.support_representative.first_name
                    + " "
                    + event.support_representative.last_name
                )
            else:
                support_representative = None
            # Date conversion
            start_date = format_french_datetime(event.start_date)
            end_date = format_french_datetime(event.end_date)

            table.add_row(
                event.id,
                event.name,
                customer,
                support_representative,
                start_date,
                end_date,
                event.attendees,
            )

        table.loading = False

    def build_event_customer_table(self) -> None:
        """Build and configure the customer data table.

        Sets up column headers for displaying associated customer information.
        """
        table = self.query_one("#event-customer-table", DataTable)
        table.border_title = "Associated Customer"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="customer_id")
        table.add_column("First Name", key="customer_first_name")
        table.add_column("Last Name", key="customer_last_name")

        table.loading = True

    def load_event_customer(self, table: DataTable, event: Event) -> None:
        """Load customer data for the selected event.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param event: The Event object containing customer data.
        :type event: Event
        """
        table.clear()

        table.add_row(
            event.contract.customer.id,
            event.contract.customer.first_name,
            event.contract.customer.last_name,
        )

        table.loading = False

    def build_event_location_table(self) -> None:
        """Build and configure the location data table.

        Sets up column headers for displaying associated location information.
        """
        table = self.query_one("#event-location-table", DataTable)
        table.border_title = "Associated Location"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="location_id")
        table.add_column("Name", key="location_name")
        table.add_column("Number", key="location_street_number")
        table.add_column("Street", key="location_street_name")
        table.add_column("Zip Code", key="location_zip_code")
        table.add_column("City", key="location_city")

        table.loading = True

    def load_event_location(self, table: DataTable, event: Event) -> None:
        """Load location data for the selected event.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param event: The Event object containing location data.
        :type event: Event
        """
        table.clear()

        if event.location:
            table.add_row(
                event.location.id,
                event.location.name,
                event.location.street_number,
                event.location.street_name,
                event.location.zip_code,
                event.location.city,
            )

        table.loading = False

    def build_event_contract_table(self) -> None:
        """Build and configure the contract data table.

        Sets up column headers for displaying associated contract information.
        """
        table = self.query_one("#event-contract-table", DataTable)
        table.border_title = "Associated Contract"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="contract_id")
        table.add_column("Total Amount", key="contract_total_amount")
        table.add_column("Amount Due", key="contract_amount_due")

        table.loading = True

    def load_event_contract(self, table: DataTable, event: Event) -> None:
        """Load contract data for the selected event.

        :param table: The DataTable widget to populate.
        :type table: DataTable
        :param event: The Event object containing contract data.
        :type event: Event
        """
        table.clear()

        table.add_row(
            event.contract.id,
            event.contract.total_amount,
            event.contract.amount_due,
        )

        table.loading = False

    def build_event_notes_text_area(self) -> None:
        """Build and configure the notes text area.

        Sets up the text area for displaying event notes/description.
        """
        text_area = self.query_one("#event-notes-text-area", TextArea)
        text_area.border_title = "Associated Notes"

        text_area.loading = True

    def load_event_notes(self, text_area: TextArea, event: Event) -> None:
        """Load notes/description for the selected event.

        :param text_area: The TextArea widget to populate.
        :type text_area: TextArea
        :param event: The Event object containing description.
        :type event: Event
        """
        text_area.clear()

        text_area.load_text(text=event.description)

        text_area.loading = False

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

    def watch_selected_event_id(self, new_id: int | None) -> None:
        """Watcher that loads associated tables based on the selected event.

        Updates all related tables (customer, location, contract, notes) when
        a new event is selected in the events table. Also updates button states.

        :param new_id: The ID of the newly selected event.
        :type new_id: int | None
        """
        event_customer_table = self.query_one(
            "#event-customer-table", DataTable
        )
        event_location_table = self.query_one(
            "#event-location-table", DataTable
        )
        event_contract_table = self.query_one(
            "#event-contract-table", DataTable
        )
        event_notes_text_area = self.query_one(
            "#event-notes-text-area", TextArea
        )

        if new_id is None:
            event_customer_table.clear()
            self.selected_customer_id = None
            event_location_table.clear()
            self.selected_location_id = None
            event_contract_table.clear()
            self.selected_contract_id = None
            return

        # Get event by ID
        selected_event = next(
            (c for c in self.events if c.id == new_id), None
        )

        if selected_event:
            # Load associated widgets based on selected_event
            self.load_event_customer(event_customer_table, selected_event)
            self.load_event_location(event_location_table, selected_event)
            self.load_event_contract(event_contract_table, selected_event)
            self.load_event_notes(event_notes_text_area, selected_event)
            # Update other selected_attributes_id
            self.selected_contract_id = selected_event.contract.id
            self.selected_customer_id = selected_event.contract.customer.id
            self.selected_location_id = selected_event.location.id

        # Enable or disable button
        self.update_update_event_button_state(selected_event)
        self.update_update_location_button_state(selected_event)

    def update_update_event_button_state(
        self, selected_event: Event | None
    ) -> None:
        """Update the state of the update event button based on permissions.

        Checks if the current user has permission to update all events or
        only their own events, and updates button visibility accordingly.

        :param selected_event: The currently selected event.
        :type selected_event: Event | None
        """
        update_event_button = self.query_one("#update-event", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_ALL_EVENTS
        ):
            update_event_button.display = True
            return

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_OWN_EVENTS
        ):
            if selected_event is not None:
                update_event_button.display = (
                    selected_event.support_representative_id
                    == self.current_user.id
                )
            return

        update_event_button.display = False

    def update_update_location_button_state(
        self, selected_event: Event | None
    ) -> None:
        """Update the state of the update location button based on permissions.

        Checks if the current user has permission to update locations and
        if they are the support representative for the selected event.

        :param selected_event: The currently selected event.
        :type selected_event: Event | None
        """
        update_location_button = self.query_one("#update-location", Button)

        if PermissionServices.has_permission(
            self.current_user, Permission.UPDATE_LOCATION
        ):
            if selected_event is not None:
                update_location_button.display = (
                    selected_event.support_representative_id
                    == self.current_user.id
                )
            return

        update_location_button.display = False

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
        # table is filtered and action is filter_unsup
        # or
        # if table is not filtered and action is filter_reset.
        # Returns True in other cases
        return not (
            (
                action == "filter_unsupported_events"
                and self.filtered_table_supported
            )
            or (
                action == "filter_user_events_as_support"
                and self.filtered_table_ownership
            )
            or (
                action == "filter_reset"
                and not (
                    self.filtered_table_supported
                    or self.filtered_table_ownership
                )
            )
        )

    def action_filter_unsupported_events(self) -> None:
        """Filter DataTable to show unsupported events.

        Dismisses the screen with a tuple indicating to show only unsupported events.
        """
        self.dismiss(("filter_unsupported_events", True))

    def action_filter_user_events_as_support(self) -> None:
        """Filter DataTable to show user events if user is a support representative.

        Dismisses the screen with a tuple indicating to show only user's events.
        """
        self.dismiss(("filter_user_events_as_support", True))

    def action_filter_reset(self) -> None:
        """Filter DataTable to show all events.

        Dismisses the screen with a tuple indicating to reset all filters.
        """
        self.dismiss(("filter_reset", False))

    def action_go_back(self) -> None:
        """Return to previous screen.

        Dismisses the screen with "back" action.
        """
        self.dismiss("back")

    @on(DataTable.RowHighlighted, "#events-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Save highlighted event id.

        Updates the selected_event_id reactive variable when a row is highlighted
        in the events table, which triggers the watcher to update related tables.

        :param event: The row highlighted event.
        :type event: DataTable.RowHighlighted
        """
        events_table = self.query_one("#events-table", DataTable)
        # Get value from the cell
        event_id = events_table.get_cell(event.row_key, "event_id")
        # Update selected_attribute_id
        self.selected_event_id = event_id

    @on(Button.Pressed, "#create-event")
    def go_create_event(self) -> None:
        """Navigate to create event screen.

        Dismisses the screen with "create_event" action.
        """
        self.dismiss("create_event")

    @on(Button.Pressed, "#update-event")
    def go_update_event(self) -> None:
        """Navigate to update event screen for selected event.

        Dismisses the screen with a tuple containing action and event ID.
        """
        self.dismiss(("update_event", self.selected_event_id))

    @on(Button.Pressed, "#create-location")
    def go_create_location(self) -> None:
        """Navigate to create location screen.

        Dismisses the screen with "create_location" action.
        """
        self.dismiss("create_location")

    @on(Button.Pressed, "#update-location")
    def go_update_location(self) -> None:
        """Navigate to update location screen for selected location.

        Dismisses the screen with a tuple containing action and location ID.
        """
        self.dismiss(("update_location", self.selected_location_id))

    @on(Button.Pressed, "#consult-customer")
    def go_consult_customer(self) -> None:
        """Navigate to consult customer screen.

        Dismisses the screen with a tuple containing action and customer ID.
        """
        self.dismiss(("consult_customer", self.selected_customer_id))

    @on(Button.Pressed, "#consult-contract")
    def go_consult_contract(self) -> None:
        """Navigate to consult contract screen.

        Dismisses the screen with a tuple containing action and contract ID.
        """
        self.dismiss(("consult_contract", self.selected_contract_id))


class CreateEventScreen(Screen):
    """Screen for creating a new event in the EpicEvents CRM.

    Provides a comprehensive form for entering all event details including
    basic information, location (existing or new), and associated contract.

    :param locations: List of existing locations to choose from.
    :type locations: list[Location]
    :param signed_contracts: List of signed contracts without associated events.
    :type signed_contracts: list[Contract]
    :param contract_id: Optional ID of a contract to pre-select.
    :type contract_id: int | None
    """

    SUB_TITLE = "CREATE EVENT"
    CSS_PATH = "../styles/create_event_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(
        self,
        locations: list[Location],
        signed_contracts: list[Contract],
        contract_id: int | None = None,
    ) -> None:
        """Initialize the CreateEventScreen with available locations and contracts.

        :param locations: List of existing locations to choose from.
        :type locations: list[Location]
        :param signed_contracts: List of signed contracts without associated events.
        :type signed_contracts: list[Contract]
        :param contract_id: Optional ID of a contract to pre-select.
        :type contract_id: int | None
        """
        super().__init__()
        self.signed_contracts: list[Contract] = signed_contracts
        self.locations: list[Location] = locations
        self.contract_id: int | None = contract_id
        self.event_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (event data,
        location selection, contract selection), and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="create-event-main-container"):
            with Container(
                id="event-data",
                classes="event-data-input-container",
            ):
                yield Label("Name", classes="form-label")
                yield Input(
                    placeholder="Event Name or Customer Event",
                    id="event_name",
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
                yield Label("Event Start Date", classes="form-label")
                yield MaskedInput(
                    placeholder="DD/MM/YYYY (HH:MM:SS)",
                    id="event_start_date",
                    template="99/99/9999 (99:99:99)",
                    classes="form-input",
                )
                yield Label("Event End Date", classes="form-label")
                yield MaskedInput(
                    placeholder="DD/MM/YYYY (HH:MM:SS)",
                    id="event_end_date",
                    template="99/99/9999 (99:99:99)",
                    classes="form-input",
                )
                yield Label("Number of attendees", classes="form-label")
                yield Input(
                    placeholder="100",
                    id="event_attendees",
                    type="integer",
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                        Integer(
                            failure_description="Must be a valid number of guests."
                        ),
                    ],
                )
                yield Label("Event Notes", classes="form-label")
                yield TextArea(
                    placeholder=(
                        "Description, details or specific requests "
                        "regarding the event"
                    ),
                    id="event_description",
                    classes="form-input",
                )
            with Container(
                id="event-location",
                classes="event-location-input-container",
            ):
                with RadioSet(id="event-location-input-choice"):
                    yield RadioButton(
                        id="existing-location",
                        label="Existing location",
                        value=True,
                        classes="event-location-radio-button",
                    )
                    yield RadioButton(
                        id="new-location",
                        label="New location",
                        classes="event-location-radio-button",
                    )
                with Container(
                    classes="event-location-select-input-container",
                    id="event-location-select-input-container",
                ):
                    location_options = [
                        (
                            (location.name + " in " + location.city),
                            location,
                        )
                        for location in self.locations
                    ]
                    yield Select(
                        location_options,
                        id="event-location-select",
                        prompt="Select a location",
                    )
                with Container(
                    classes="event-location-form-input-container",
                    id="event-location-form-input-container",
                ):
                    yield Label("Name", classes="form-label")
                    yield Input(
                        placeholder="Location Name",
                        id="location_name",
                        type="text",
                        classes="form-input",
                        validators=[
                            Length(
                                maximum=99,
                                failure_description="Name is too long.",
                            ),
                        ],
                    )
                    yield Label("Number", classes="form-label")
                    yield Input(
                        placeholder="3",
                        id="location_street_number",
                        type="text",
                        max_length=10,
                        classes="form-input",
                        validators=[
                            Length(
                                minimum=1,
                                failure_description="Field cannot be empty.",
                            ),
                        ],
                    )
                    yield Label("Street", classes="form-label")
                    yield Input(
                        placeholder="Sunset Boulevard",
                        id="location_street_name",
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
                    yield Label("Zip Code", classes="form-label")
                    yield MaskedInput(
                        placeholder="75000",
                        id="location_zip_code",
                        template="99999",
                        classes="form-input",
                    )
                    yield Label("City", classes="form-label")
                    yield Input(
                        placeholder="Night City",
                        id="location_city",
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
                id="event-contract",
                classes="event-contract-input-container",
            ):
                contract_options = [
                    (
                        (
                            "Contract ID: "
                            + str(contract.id)
                            + " with "
                            + contract.customer.first_name
                            + " "
                            + contract.customer.last_name
                        ),
                        contract,
                    )
                    for contract in self.signed_contracts
                ]
                selected_contract = next(
                    (
                        contract
                        for contract in self.signed_contracts
                        if contract.id == self.contract_id
                    ),
                    None,
                )
                select_kwargs = {
                    "id": "event-contract-select",
                    "prompt": "Select a contract",
                }
                if selected_contract is not None:
                    select_kwargs["value"] = selected_contract

                yield Select(contract_options, **select_kwargs)
            with Container(
                id="create-event-buttons-container",
                classes="create-event-buttons-container",
            ):
                yield Button(
                    "Create",
                    id="create",
                    variant="primary",
                    classes="create-event-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="create-event-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for containers and hides the new location form
        by default.
        """
        event_data_container = self.query_one("#event-data", Container)
        event_contract_container = self.query_one(
            "#event-contract", Container
        )
        event_location_container = self.query_one(
            "#event-location", Container
        )
        event_data_container.border_title = "Event Data"
        event_contract_container.border_title = "Contract Selection"
        event_location_container.border_title = "Location Selection"

        # Hide form container for location input by default:
        self.query_one(
            "#event-location-form-input-container", Container
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
            self.query_one("#event_name", Input),
            self.query_one("#event_start_date", MaskedInput),
            self.query_one("#event_end_date", MaskedInput),
            self.query_one("#event_attendees", Input),
        ]

        widget_selects = [
            self.query_one("#event-contract-select", Select),
        ]

        radio_set = self.query_one(
            "#event-location-input-choice", RadioSet
        )
        if radio_set.pressed_button.label == "Existing location":
            widget_selects.append(
                self.query_one("#event-location-select", Select)
            )
        else:
            widget_inputs.extend(
                [
                    self.query_one("#location_name", Input),
                    self.query_one("#location_street_number", Input),
                    self.query_one("#location_street_name", Input),
                    self.query_one("#location_zip_code", MaskedInput),
                    self.query_one("#location_city", Input),
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

    @on(MaskedInput.Changed)
    def show_minput_invalid_reasons(
        self, event: MaskedInput.Changed
    ) -> None:
        """Show validation error messages for changed masked input fields.

        :param event: The masked input changed event.
        :type event: MaskedInput.Changed
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

    @on(MaskedInput.Blurred)
    def show_minput_invalid_reasons_2(
        self, event: MaskedInput.Blurred
    ) -> None:
        """Show validation error messages for blurred masked input fields.

        :param event: The masked input blurred event.
        :type event: MaskedInput.Blurred
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

    @on(RadioSet.Changed, "#event-location-input-choice")
    def on_location_input_choice_changed(
        self, event: RadioSet.Changed
    ) -> None:
        """Toggle containers' display based on user radio button input.

        Shows the location select or form container based on user choice.

        :param event: The radio set changed event.
        :type event: RadioSet.Changed
        """
        self._validate_form()
        select_container = self.query_one(
            "#event-location-select-input-container", Container
        )
        form_container = self.query_one(
            "#event-location-form-input-container", Container
        )

        if event.pressed.label == "Existing location":
            select_container.display = True
            form_container.display = False
        else:
            select_container.display = False
            form_container.display = True

    @on(Button.Pressed, "#create")
    def go_create(self) -> None:
        """Handle Create button press.

        Collects form data and dismisses screen with the data.
        """
        self._collect_form_data()
        self.dismiss(self.event_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into event_data dictionary.

        Retrieves values from all form fields and stores them in event_data.
        """
        selected_contract = self.query_one(
            "#event-contract-select", Select
        ).value
        radio_set = self.query_one(
            "#event-location-input-choice", RadioSet
        )

        # Get location format depending on user input choice
        if radio_set.pressed_button.label == "Existing location":
            # Existing location : use Select value
            location_data = self.query_one(
                "#event-location-select", Select
            ).value
        else:
            # New location : use Form inputs values
            location_data = {
                "name": self.query_one("#location_name", Input).value,
                "street_number": self.query_one(
                    "#location_street_number", Input
                ).value,
                "street_name": self.query_one(
                    "#location_street_name", Input
                ).value,
                "zip_code": self.query_one(
                    "#location_zip_code", MaskedInput
                ).value,
                "city": self.query_one("#location_city", Input).value,
            }

        self.event_data = {
            "event_name": self.query_one("#event_name", Input).value,
            "event_start_date": self.query_one(
                "#event_start_date", Input
            ).value,
            "event_end_date": self.query_one(
                "#event_end_date", Input
            ).value,
            "event_attendees": self.query_one(
                "#event_attendees", Input
            ).value,
            "event_description": self.query_one(
                "#event_description", TextArea
            ).text,
            "event_contract": selected_contract,
            "event_location": location_data,
        }


class UpdateEventScreen(Screen):
    """Screen for updating an existing event in the EpicEvents CRM.

    Provides a form pre-filled with existing event data for modification.
    Allows updating event details, location, contract, and support representative.

    :param event_data: Dictionary containing all data of the event to update.
    :type event_data: dict[str, Any]
    :param locations: List of existing locations to choose from.
    :type locations: list[Location]
    :param support_representatives: List of collaborators who can be support representatives.
    :type support_representatives: list[Collaborator]
    :param signed_contracts: List of signed contracts (including current contract).
    :type signed_contracts: list[Contract]
    """

    SUB_TITLE = "UPDATE EVENT"
    CSS_PATH = "../styles/update_event_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(
        self,
        event_data: dict[str, Any],
        locations: list[Location],
        support_representatives: list[Collaborator],
        signed_contracts: list[Contract],
    ) -> None:
        """Initialize the UpdateEventScreen with event data and options.

        :param event_data: Dictionary containing all data of the event to update.
        :type event_data: dict[str, Any]
        :param locations: List of existing locations to choose from.
        :type locations: list[Location]
        :param support_representatives: List of collaborators who can be support representatives.
        :type support_representatives: list[Collaborator]
        :param signed_contracts: List of signed contracts.
        :type signed_contracts: list[Contract]
        """
        super().__init__()
        self.locations: list[Location] = locations
        self.support_representatives: list[Collaborator] = (
            support_representatives
        )
        self.signed_contracts: list[Contract] = signed_contracts
        self.event_data: dict[str, Any] = event_data
        self.updated_event_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form sections (event data,
        contract selection, location selection, support representative selection),
        and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="update-event-main-container"):
            yield Static(
                "Updating event: "
                f"{self.event_data['event_name']} "
                "associated to client: "
                f"{self.event_data['event_contract'].customer.first_name} "
                f"{self.event_data['event_contract'].customer.last_name}",
                classes="updating-event-static",
            )
            with Container(
                id="update-event-data",
                classes="update-event-data-input-container",
            ):
                yield Label("Name", classes="form-label")
                yield Input(
                    value=self.event_data.get("event_name", ""),
                    id="event_name",
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
                yield Label("Event Start Date", classes="form-label")
                yield MaskedInput(
                    placeholder="DD/MM/YYYY (HH:MM:SS)",
                    id="event_start_date",
                    template="99/99/9999 (99:99:99)",
                    classes="form-input",
                )
                yield Label("Event End Date", classes="form-label")
                yield MaskedInput(
                    placeholder="DD/MM/YYYY (HH:MM:SS)",
                    id="event_end_date",
                    template="99/99/9999 (99:99:99)",
                    classes="form-input",
                )
                yield Label("Number of attendees", classes="form-label")
                yield Input(
                    value=str(self.event_data.get("event_attendees", 0)),
                    placeholder="100",
                    id="event_attendees",
                    type="integer",
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                        Integer(
                            failure_description="Must be a valid number of guests."
                        ),
                    ],
                )
                yield Label("Event Notes", classes="form-label")
                yield TextArea(
                    text=self.event_data.get("event_description", ""),
                    id="event_description",
                    classes="form-input",
                )
            with Container(
                id="update-event-contract",
                classes="update-event-contract-input-container",
            ):
                # Add current contract which is not eventless
                self.signed_contracts.append(
                    self.event_data.get("event_contract")
                )
                contract_options = [
                    (
                        (
                            "Contract ID: "
                            + str(contract.id)
                            + " with "
                            + contract.customer.first_name
                            + " "
                            + contract.customer.last_name
                        ),
                        contract,
                    )
                    for contract in self.signed_contracts
                ]
                yield Select(
                    contract_options,
                    id="update-event-contract-select",
                    prompt="Select a contract",
                    value=self.event_data.get("event_contract"),
                )
            with Container(
                id="update-event-location",
                classes="update-event-location-input-container",
            ):
                location_options = [
                    (
                        (location.name + " in " + location.city),
                        location,
                    )
                    for location in self.locations
                ]
                yield Select(
                    location_options,
                    id="update-event-location-select",
                    prompt="Select a location",
                    value=self.event_data.get("event_location"),
                )
            with Container(
                id="update-event-support-representative",
                classes="update-event-support-representative-input-container",
            ):
                support_representatives_options = [
                    (
                        (
                            support_representative.first_name
                            + " "
                            + support_representative.last_name
                        ),
                        support_representative,
                    )
                    for support_representative in self.support_representatives
                ]
                selected_support_representative = next(
                    (
                        support_representative
                        for support_representative in self.support_representatives
                        if support_representative
                        == self.event_data.get(
                            "event_support_representative"
                        )
                    ),
                    None,
                )
                select_kwargs = {
                    "id": "update-event-support-representative-select",
                    "prompt": "Select a support representative",
                }
                if selected_support_representative is not None:
                    select_kwargs["value"] = (
                        selected_support_representative
                    )

                yield Select(
                    support_representatives_options, **select_kwargs
                )
            with Container(
                id="update-event-buttons-container",
                classes="update-event-buttons-container",
            ):
                yield Button(
                    "Update",
                    id="update",
                    variant="primary",
                    classes="update-event-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="update-event-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border titles for containers, converts dates to French format,
        and highlights invalid select fields.
        """
        event_data_container = self.query_one(
            "#update-event-data", Container
        )
        event_contract_container = self.query_one(
            "#update-event-contract", Container
        )
        event_location_container = self.query_one(
            "#update-event-location", Container
        )
        event_support_representative_container = self.query_one(
            "#update-event-support-representative", Container
        )
        event_data_container.border_title = "Event Data"
        event_data_container.border_subtitle = "Edit relevant fields"
        event_contract_container.border_title = "Contract Selection"
        event_location_container.border_title = "Location Selection"
        event_support_representative_container.border_title = (
            "Support Representative Selection"
        )

        # Convert dates from UTC to french format
        event_start_date_input = self.query_one(
            "#event_start_date", MaskedInput
        )
        event_end_date_input = self.query_one(
            "#event_end_date", MaskedInput
        )
        event_start_date = format_french_datetime(
            self.event_data["event_start_date"]
        )
        event_end_date = format_french_datetime(
            self.event_data["event_end_date"]
        )

        event_start_date_input.value = event_start_date
        event_end_date_input.value = event_end_date

        # Highlight invalid select fields
        for select_widget in self.query(Select):
            select_current = select_widget.query_one(SelectCurrent)
            if select_widget.is_blank():
                error_message = "An option must be selected."
                select_current.set_class(True, "-invalid")
                select_current.border_subtitle = error_message

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
            self.query_one("#event_name", Input),
            self.query_one("#event_start_date", MaskedInput),
            self.query_one("#event_end_date", MaskedInput),
            self.query_one("#event_attendees", Input),
        ]

        widget_selects = [
            self.query_one("#update-event-contract-select", Select),
            self.query_one("#update-event-location-select", Select),
            self.query_one(
                "#update-event-support-representative-select", Select
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

    @on(MaskedInput.Changed)
    def show_minput_invalid_reasons(
        self, event: MaskedInput.Changed
    ) -> None:
        """Show validation error messages for changed masked input fields.

        :param event: The masked input changed event.
        :type event: MaskedInput.Changed
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

    @on(MaskedInput.Blurred)
    def show_minput_invalid_reasons_2(
        self, event: MaskedInput.Blurred
    ) -> None:
        """Show validation error messages for blurred masked input fields.

        :param event: The masked input blurred event.
        :type event: MaskedInput.Blurred
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

        Collects form data and dismisses screen with the updated data.
        """
        self._collect_form_data()
        self.dismiss(self.updated_event_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into updated_event_data dictionary.

        Retrieves values from all form fields and stores them in updated_event_data.
        """
        selected_contract = self.query_one(
            "#update-event-contract-select", Select
        ).value
        selected_location = self.query_one(
            "#update-event-location-select", Select
        ).value
        selected_support_representative = self.query_one(
            "#update-event-support-representative-select", Select
        ).value

        self.updated_event_data = {
            "event_id": self.event_data["event_id"],
            "event_name": self.query_one("#event_name", Input).value,
            "event_start_date": self.query_one(
                "#event_start_date", Input
            ).value,
            "event_end_date": self.query_one(
                "#event_end_date", Input
            ).value,
            "event_attendees": self.query_one(
                "#event_attendees", Input
            ).value,
            "event_description": self.query_one(
                "#event_description", TextArea
            ).text,
            "event_contract": selected_contract,
            "event_location": selected_location,
            "event_support_representative": selected_support_representative,
        }


class CreateLocationScreen(Screen):
    """Screen for creating a new location in the EpicEvents CRM.

    Provides a form for entering all location details including name,
    street address, zip code, and city.

    Note:
        This screen is used when creating a location as part of event creation
        or as a standalone operation.
    """

    SUB_TITLE = "CREATE LOCATION"
    CSS_PATH = "../styles/create_location_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        """Initialize the CreateLocationScreen.

        Creates a new screen instance for location creation.
        """
        super().__init__()
        self.location_data: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form fields for location data,
        and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="create-location-main-container"):
            with Container(
                id="location-data",
                classes="location-data-input-container",
            ):
                yield Label("Name", classes="form-label")
                yield Input(
                    placeholder="Location Name",
                    id="location_name",
                    type="text",
                    classes="form-input",
                    validators=[
                        Length(
                            maximum=99,
                            failure_description="Name is too long.",
                        ),
                    ],
                )
                yield Label("Number", classes="form-label")
                yield Input(
                    placeholder="3",
                    id="location_street_number",
                    type="text",
                    max_length=10,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Street", classes="form-label")
                yield Input(
                    placeholder="Sunset Boulevard",
                    id="location_street_name",
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
                yield Label("Zip Code", classes="form-label")
                yield MaskedInput(
                    placeholder="75000",
                    id="location_zip_code",
                    template="99999",
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("City", classes="form-label")
                yield Input(
                    placeholder="Night City",
                    id="location_city",
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
            with Container(classes="create-location-buttons-container"):
                yield Button(
                    "Create",
                    id="create",
                    variant="primary",
                    classes="create-location-button",
                    disabled=True,
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="create-location-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border title for the location data container.
        """
        location_data_container = self.query_one(
            "#location-data", Container
        )
        location_data_container.border_title = "Location Data"

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
        of all input fields.
        """
        widget_inputs = [
            self.query_one("#location_name", Input),
            self.query_one("#location_street_number", Input),
            self.query_one("#location_street_name", Input),
            self.query_one("#location_zip_code", MaskedInput),
            self.query_one("#location_city", Input),
        ]

        # Check that all fields are valid
        all_valid = all(
            widget_input.validate(widget_input.value).is_valid
            for widget_input in widget_inputs
        )

        # Update reactive variable triggering watcher
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

    @on(MaskedInput.Changed)
    def show_minput_invalid_reasons(
        self, event: MaskedInput.Changed
    ) -> None:
        """Show validation error messages for changed masked input fields.

        :param event: The masked input changed event.
        :type event: MaskedInput.Changed
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

    @on(MaskedInput.Blurred)
    def show_minput_invalid_reasons_2(
        self, event: MaskedInput.Blurred
    ) -> None:
        """Show validation error messages for blurred masked input fields.

        :param event: The masked input blurred event.
        :type event: MaskedInput.Blurred
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

        Collects form data and dismisses screen with the location data.
        """
        self._collect_form_data()
        self.dismiss(self.location_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into location_data dictionary.

        Retrieves values from all form fields and stores them in location_data.
        """
        self.location_data = {
            "name": self.query_one("#location_name", Input).value,
            "street_number": self.query_one(
                "#location_street_number", Input
            ).value,
            "street_name": self.query_one(
                "#location_street_name", Input
            ).value,
            "zip_code": self.query_one(
                "#location_zip_code", MaskedInput
            ).value,
            "city": self.query_one("#location_city", Input).value,
        }


class UpdateLocationScreen(Screen):
    """Screen for updating an existing location in the EpicEvents CRM.

    Provides a form pre-filled with existing location data for modification.

    :param location_data: Dictionary containing all data of the location to update.
    :type location_data: dict[str, str]
    """

    SUB_TITLE = "UPDATE LOCATION"
    CSS_PATH = "../styles/update_location_screen.tcss"

    # Reactive variables
    is_form_valid: reactive[bool] = reactive(False)

    def __init__(self, location_data: dict[str, str]) -> None:
        """Initialize the UpdateLocationScreen with location data.

        :param location_data: Dictionary containing all data of the location to update.
        :type location_data: dict[str, str]
        """
        super().__init__()
        self.location_data: dict[str, str] = location_data
        self.updated_location_data: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        """Compose the screen UI components.

        Creates the header, main container with form fields for location data,
        and footer with action buttons.

        :return: Generator yielding all UI widgets.
        :rtype: ComposeResult
        """
        yield Header(show_clock=True)
        with Container(classes="update-location-main-container"):
            yield Static(
                "Updating location: "
                f"{self.location_data['location_name']} ",
                classes="updating-location-static",
                id="updating-location-static",
            )
            with Container(
                id="update-location-data",
                classes="update-location-data-input-container",
            ):
                yield Label("Name", classes="form-label")
                yield Input(
                    value=self.location_data.get("location_name", ""),
                    placeholder="Location Name",
                    id="location_name",
                    type="text",
                    classes="form-input",
                    validators=[
                        Length(
                            maximum=99,
                            failure_description="Name is too long.",
                        ),
                    ],
                )
                yield Label("Street Number", classes="form-label")
                yield Input(
                    value=self.location_data.get(
                        "location_street_number", ""
                    ),
                    placeholder="3",
                    id="location_street_number",
                    type="text",
                    max_length=10,
                    classes="form-input",
                    validators=[
                        Length(
                            minimum=1,
                            failure_description="Field cannot be empty.",
                        ),
                    ],
                )
                yield Label("Street Name", classes="form-label")
                yield Input(
                    value=self.location_data.get(
                        "location_street_name", ""
                    ),
                    placeholder="Sunset Boulevard",
                    id="location_street_name",
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
                yield Label("Zip Code", classes="form-label")
                yield MaskedInput(
                    value=self.location_data.get("location_zip_code", ""),
                    placeholder="75000",
                    id="location_zip_code",
                    template="99999",
                    classes="form-input",
                )
                yield Label("City", classes="form-label")
                yield Input(
                    value=self.location_data.get("location_city", ""),
                    placeholder="Night City",
                    id="location_city",
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
            with Container(classes="update-location-buttons-container"):
                yield Button(
                    "Update",
                    id="update",
                    variant="primary",
                    classes="update-location-button",
                )
                yield Button(
                    "Cancel",
                    id="cancel",
                    variant="default",
                    classes="update-location-button",
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """Initialize the screen after mounting.

        Sets border title and subtitle for the location data container.
        """
        location_data_container = self.query_one(
            "#update-location-data", Container
        )
        location_data_container.border_title = "Location Data"
        location_data_container.border_subtitle = "Edit relevant fields"

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
        of all input fields.
        """
        widget_inputs = [
            self.query_one("#location_name", Input),
            self.query_one("#location_street_number", Input),
            self.query_one("#location_street_name", Input),
            self.query_one("#location_zip_code", MaskedInput),
            self.query_one("#location_city", Input),
        ]

        # Check that all fields are valid
        all_valid = all(
            widget_input.validate(widget_input.value).is_valid
            for widget_input in widget_inputs
        )

        # Update reactive variable triggering watcher
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

    @on(MaskedInput.Changed)
    def show_minput_invalid_reasons(
        self, event: MaskedInput.Changed
    ) -> None:
        """Show validation error messages for changed masked input fields.

        :param event: The masked input changed event.
        :type event: MaskedInput.Changed
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

    @on(MaskedInput.Blurred)
    def show_minput_invalid_reasons_2(
        self, event: MaskedInput.Blurred
    ) -> None:
        """Show validation error messages for blurred masked input fields.

        :param event: The masked input blurred event.
        :type event: MaskedInput.Blurred
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

        Collects form data and dismisses screen with the updated location data.
        """
        self._collect_form_data()
        self.dismiss(self.updated_location_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        """Handle Cancel button press.

        Dismisses screen without data.
        """
        self.dismiss(None)

    def _collect_form_data(self) -> None:
        """Collect all form data into updated_location_data dictionary.

        Retrieves values from all form fields and stores them in updated_location_data.
        """
        self.updated_location_data = {
            "location_id": self.location_data["location_id"],
            "location_name": self.query_one("#location_name", Input).value,
            "location_street_number": self.query_one(
                "#location_street_number", Input
            ).value,
            "location_street_name": self.query_one(
                "#location_street_name", Input
            ).value,
            "location_zip_code": self.query_one(
                "#location_zip_code", MaskedInput
            ).value,
            "location_city": self.query_one("#location_city", Input).value,
        }
