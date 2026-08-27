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
    Select,
)

from models import Collaborator, Department


class CollaboratorScreen(Screen):
    """Screen that displays a table of collaborators."""

    SUB_TITLE = "COLLABORATORS"
    CSS_PATH = "styles/collaborator_screen.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("b", "go_back", "Back"),
    ]

    # Reactive variables
    selected_collaborator_id: reactive[int | None] = reactive(None)
    selected_customer_id: reactive[int | None] = reactive(None)
    selected_event_id: reactive[int | None] = reactive(None)

    def __init__(self, collaborators: list[Collaborator]) -> None:
        super().__init__()
        self.collaborators = collaborators

    def compose(self) -> ComposeResult:
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
                    "Consult Event", id="consult-event", variant="warning"
                )
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        """ """
        self.build_collaborators_table()
        self.build_collaborator_customers_table()
        self.build_collaborator_events_table()
        
        # Initialize default selections with the first available collaborator,
        # customer, and event to ensure the UI has valid selections on load.
        if self.collaborators:
            self.selected_collaborator_id = self.collaborators[0].id
            if self.collaborators[0].customers:
                self.selected_customer_id = (
                    self.collaborators[0].customers[0].id
                )
            if self.collaborators[0].events:
                self.selected_event_id = self.collaborators[0].events[0].id

    def build_collaborators_table(self) -> None:
        table = self.query_one("#collaborators-table", DataTable)
        table.border_title = "Collaborators"
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Configure table columns
        table.add_column("ID", key="id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")
        table.add_column("Email", key="email")
        table.add_column("Department", key="department")
        table.add_column("Customers", key="nb_customers")
        table.add_column("Events", key="nb_department")

        table.loading = True
        self.load_collaborators(table)

    def load_collaborators(self, table: DataTable) -> None:
        """Load collaborator data into the table."""
        table.clear()

        for collaborator in self.collaborators:
            # Department
            department = collaborator.department.name.value
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
        table = self.query_one("#collaborator-customers-table", DataTable)
        table.border_title = "Assigned Customers"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="id")
        table.add_column("First Name", key="first_name")
        table.add_column("Last Name", key="last_name")

        table.loading = True

    def load_collaborator_customers(
        self, table: DataTable, collaborator: Collaborator
    ) -> None:
        table.clear()

        for customer in collaborator.customers:
            table.add_row(
                customer.id,
                customer.first_name,
                customer.last_name,
            )

        table.loading = False

    def build_collaborator_events_table(self) -> None:
        table = self.query_one("#collaborator-events-table", DataTable)
        table.border_title = "Assigned Events"
        table.cursor_type = "row"
        table.zebra_stripes = True

        table.add_column("ID", key="id")
        table.add_column("Event Name", key="event_name")

        table.loading = True

    def load_collaborator_events(
        self, table: DataTable, collaborator: Collaborator
    ) -> None:
        table.clear()

        for event in collaborator.events:
            table.add_row(
                event.id,
                event.name,
            )

        table.loading = False

    def watch_selected_collaborator_id(self, new_id: int | None) -> None:
        """
        Watcher that loads customers and events based on the collaborator
        highlighted in collaborators-table
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
            return

        # Get collaborator by ID
        selected_collaborator = next(
            (c for c in self.collaborators if c.id == new_id), None
        )

        if selected_collaborator:
            self.load_collaborator_customers(
                collaborator_customers_table, selected_collaborator
            )
            self.load_collaborator_events(
                collaborator_events_table, selected_collaborator
            )

    def action_go_back(self) -> None:
        """Return to previous screen."""
        self.dismiss("back")

    @on(DataTable.RowHighlighted, "#collaborators-table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Saves highlighted collaborator id"""
        row_index = event.cursor_row
        if 0 <= row_index < len(self.collaborators):
            self.selected_collaborator_id = self.collaborators[
                row_index
            ].id

    @on(DataTable.RowHighlighted, "#collaborator-customers-table")
    def on_customer_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Saves highlighted customer id"""
        row_index = event.cursor_row

        # Get collaborator associated to highlighted customer
        if self.selected_collaborator_id:
            selected_collaborator = next(
                (
                    c
                    for c in self.collaborators
                    if c.id == self.selected_collaborator_id
                ),
                None,
            )
            if selected_collaborator and 0 <= row_index < len(
                selected_collaborator.customers
            ):
                selected_customer = selected_collaborator.customers[
                    row_index
                ]
                self.selected_customer_id = selected_customer.id

    @on(DataTable.RowHighlighted, "#collaborator-events-table")
    def on_event_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Saves highlighted event id"""
        row_index = event.cursor_row

        # Get collaborator associated to highlighted event
        if self.selected_collaborator_id:
            selected_collaborator = next(
                (
                    c
                    for c in self.collaborators
                    if c.id == self.selected_collaborator_id
                ),
                None,
            )
            if selected_collaborator and 0 <= row_index < len(
                selected_collaborator.events
            ):
                selected_event = selected_collaborator.events[row_index]
                self.selected_event_id = selected_event.id

    @on(Button.Pressed, "#create-collaborator")
    def go_create_collaborator(self) -> None:
        self.dismiss("create_collaborator")

    @on(Button.Pressed, "#update-collaborator")
    def go_update_collaborator(self) -> None:
        self.dismiss(
            ("update_collaborator", self.selected_collaborator_id)
        )

    @on(Button.Pressed, "#consult-customer")
    def go_consult_customer(self) -> None:
        self.dismiss(("consult_customer", self.selected_customer_id))

    @on(Button.Pressed, "#consult-event")
    def go_consult_event(self) -> None:
        self.dismiss(("consult_event", self.selected_event_id))

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss("back")


class CreateCollaboratorScreen(Screen):
    """Screen that displays a form to create a new collaborator."""

    SUB_TITLE = "CREATE COLLABORATOR"

    CSS_PATH = "styles/create_collaborator_screen.tcss"

    def __init__(self, departments: list[Department]):
        super().__init__()
        self.departments = departments
        self.customer_data = {}

    def compose(self) -> ComposeResult:
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
                    classes="form-input",
                )
                yield Label(
                    "Collaborator First Name:", classes="form-label"
                )
                yield Input(
                    placeholder="John",
                    id="collaborator_first_name",
                    type="text",
                    classes="form-input",
                )
                yield Label("Password:", classes="form-label")
                yield Input(
                    placeholder="my-secure-password",
                    id="password",
                    password=False,
                    classes="form-input",
                )
            with Container(
                id="collaborator-department",
                classes="collaborator-department-input-container",
            ):
                department_options = [
                    (
                        department.name.value,
                        department.name.value,
                    )  # (valeur, label)
                    for department in self.departments
                ]
                yield Select(
                    department_options,
                    id="collaborator-department-select",  # ID pour la récupération
                    prompt="Select a department",  # Texte par défaut
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
