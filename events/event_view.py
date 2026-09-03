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
    RadioButton,
    RadioSet,
    Select,
    Static,
    TextArea,
)

from collaborators.collaborator_model import Collaborator
from contracts.contract_model import Contract
from events.event_model import Event, Location
from services.date_services import format_french_datetime


class EventScreen(Screen):
    """Screen that displays a table of events."""

    SUB_TITLE = "EVENTS"
    CSS_PATH = "../styles/event_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_event_id: reactive[int | None] = reactive(None)

    def __init__(
        self, events: list[Event], event_id: int | None = None
    ) -> None:
        super().__init__()
        self.events = events
        self.pre_selected_event_id = event_id
        self.selected_contract_id = None
        self.selected_location_id = None
        self.selected_customer_id = None

    def compose(self) -> ComposeResult:
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
                    disabled=True,
                )
                yield Button(
                    "Update Location",
                    id="update-location",
                    variant="warning",
                    disabled=True,
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

        self.build_events_table()
        self.build_event_contract_table()
        self.build_event_notes_text_area()
        self.build_event_location_table()
        self.build_event_customer_table()

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
                self.selected_event_id = event.id
                row_index = self.events.index(event)
                self.query_one("#events-table", DataTable).move_cursor(
                    row=row_index
                )
        # If not, use first event
        elif self.events:
            self.selected_event_id = self.events[0].id

    def build_events_table(self) -> None:
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
        """Load event data into the table."""
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
        table = self.query_one("#event-customer-table", DataTable)
        table.border_title = "Associated Customer"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="customer_id")
        table.add_column("First Name", key="customer_first_name")
        table.add_column("Last Name", key="customer_last_name")

        table.loading = True

    def load_event_customer(self, table: DataTable, event: Event) -> None:
        table.clear()

        table.add_row(
            event.contract.customer.id,
            event.contract.customer.first_name,
            event.contract.customer.last_name,
        )

        table.loading = False

    def build_event_location_table(self) -> None:
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
        table = self.query_one("#event-contract-table", DataTable)
        table.border_title = "Associated Contract"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="contract_id")
        table.add_column("Total Amount", key="contract_total_amount")
        table.add_column("Amount Due", key="contract_amount_due")

        table.loading = True

    def load_event_contract(self, table: DataTable, event: Event) -> None:
        table.clear()

        table.add_row(
            event.contract.id,
            event.contract.total_amount,
            event.contract.amount_due,
        )

        table.loading = False

    def build_event_notes_text_area(self) -> None:
        text_area = self.query_one("#event-notes-text-area", TextArea)
        text_area.border_title = "Associated Notes"

        text_area.loading = True

    def load_event_notes(self, text_area: TextArea, event: Event) -> None:
        text_area.clear()

        text_area.load_text(text=event.description)

        text_area.loading = False

    def watch_selected_event_id(self, new_id: int | None) -> None:
        """
        Watcher that loads associated tables based on the event
        highlighted in events-table
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

    def action_go_back(self) -> None:
        """Return to previous screen."""
        self.dismiss("back")

    @on(DataTable.RowHighlighted, "#events-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Saves highlighted event id"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self.events):
            self.selected_event_id = self.events[row_index].id

    @on(Button.Pressed, "#create-event")
    def go_create_event(self) -> None:
        self.dismiss("create_event")

    @on(Button.Pressed, "#update-event")
    def go_update_event(self) -> None:
        self.dismiss(("update_event", self.selected_event_id))

    @on(Button.Pressed, "#create-location")
    def go_create_location(self) -> None:
        self.dismiss("create_event")

    @on(Button.Pressed, "#update-location")
    def go_update_location(self) -> None:
        self.dismiss(("update_location", self.selected_location_id))

    @on(Button.Pressed, "#consult-customer")
    def go_consult_customer(self) -> None:
        self.dismiss(("consult_customer", self.selected_customer_id))

    @on(Button.Pressed, "#consult-contract")
    def go_consult_contract(self) -> None:
        self.dismiss(("consult_contract", self.selected_contract_id))

    # @on(Button.Pressed, "#back")
    # def go_back(self) -> None:
    #     self.dismiss("back")


class CreateEventScreen(Screen):
    """Screen that displays a form to create a new event."""

    SUB_TITLE = "CREATE EVENT"
    CSS_PATH = "../styles/create_event_screen.tcss"

    def __init__(
        self,
        locations: list[Location],
        signed_contracts: list[Contract],
        contract_id: int | None = None,
    ):
        super().__init__()
        self.signed_contracts = signed_contracts
        self.locations = locations
        self.contract_id = contract_id
        self.event_data = {}

    def compose(self) -> ComposeResult:
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
                    classes="form-input",
                )
                yield Label("Event Start Date", classes="form-label")
                yield Input(
                    placeholder="DD/MM/YYYY (HH:MM:SS)",
                    id="event_start_date",
                    type="text",
                    classes="form-input",
                )
                yield Label("Event End Date", classes="form-label")
                yield Input(
                    placeholder="DD/MM/YYYY (HH:MM:SS)",
                    id="event_end_date",
                    type="text",
                    classes="form-input",
                )
                yield Label("Number of attendees", classes="form-label")
                yield Input(
                    placeholder="100",
                    id="event_attendees",
                    type="integer",
                    classes="form-input",
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
                        "Existing location",
                        value=True,
                        classes="event-location-radio-button",
                    )
                    yield RadioButton(
                        "New location",
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
                    )
                    yield Label("Number", classes="form-label")
                    yield Input(
                        placeholder="3",
                        id="location_street_number",
                        type="text",
                        classes="form-input",
                    )
                    yield Label("Street", classes="form-label")
                    yield Input(
                        placeholder="Sunset Boulevard",
                        id="location_street_name",
                        type="text",
                        classes="form-input",
                    )
                    yield Label("Zip Code", classes="form-label")
                    yield Input(
                        placeholder="34567",
                        id="location_zip_code",
                        type="integer",
                        classes="form-input",
                    )
                    yield Label("City", classes="form-label")
                    yield Input(
                        placeholder="Night City",
                        id="location_city",
                        type="text",
                        classes="form-input",
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
            with Container(classes="create-event-buttons-container"):
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

    @on(RadioSet.Changed, "#event-location-input-choice")
    def on_location_input_choice_changed(
        self, event: RadioSet.Changed
    ) -> None:
        """Toggle containers' display based on user radiobutton input"""
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
        self._collect_form_data()
        self.dismiss(self.event_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self) -> dict:
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
                    "#location_zip_code", Input
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
    SUB_TITLE = "UPDATE EVENT"
    CSS_PATH = "../styles/update_event_screen.tcss"

    def __init__(
        self,
        event_data: dict,
        locations: list[Location],
        support_representatives: list[Collaborator],
        signed_contracts: list[Contract],
    ):
        super().__init__()
        self.locations = locations
        self.support_representatives = support_representatives
        self.signed_contracts = signed_contracts
        self.event_data = event_data
        self.updated_event_data = {}

    def compose(self):
        """
        Compose the screen with a form to update event data.
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
                    classes="form-input",
                )
                yield Label("Event Start Date", classes="form-label")
                yield Input(
                    id="event_start_date",
                    type="text",
                    classes="form-input",
                )
                yield Label("Event End Date", classes="form-label")
                yield Input(
                    id="event_end_date",
                    type="text",
                    classes="form-input",
                )
                yield Label("Number of attendees", classes="form-label")
                yield Input(
                    value=str(self.event_data.get("event_attendees", 0)),
                    id="event_attendees",
                    type="integer",
                    classes="form-input",
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
            with Container(classes="update-event-buttons-container"):
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

    def _on_mount(self):
        """Set container border title and subtitle and widget values"""

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
        event_start_date_input = self.query_one("#event_start_date", Input)
        event_end_date_input = self.query_one("#event_end_date", Input)
        event_start_date = format_french_datetime(
            self.event_data["event_start_date"]
        )
        event_end_date = format_french_datetime(
            self.event_data["event_end_date"]
        )

        event_start_date_input.value = event_start_date
        event_end_date_input.value = event_end_date

    @on(Button.Pressed, "#update")
    def go_update(self) -> None:
        self._collect_form_data()
        self.dismiss(self.updated_event_data)

    @on(Button.Pressed, "#cancel")
    def go_back(self) -> None:
        self.dismiss(None)

    def _collect_form_data(self):
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
