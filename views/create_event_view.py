from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static, MaskedInput

class CreateEventScreen(Screen[dict]):
    """Screen that displays a form to create a new event."""

    CSS = """
    CreateEventScreen {
        align: center middle;
    }

    .form-container {
        width: 80%;
        height: auto;
        border: solid $primary;
        padding: 2 2;
    }

    .form-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 2;
    }

    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .form-label {
        width: 30%;
        text-align: right;
        padding-right: 1;
    }

    .form-input {
        width: 70%;
    }

    .form-buttons {
        height: auto;
        margin-top: 2;
        layout: horizontal;
        align: center middle;
    }

    .form-button {
        width: auto;
        margin: 0 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_data = {}

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Create New Event", classes="form-title"),
            Label("Name:", classes="form-label"),
            Input(placeholder="Event name", id="name", classes="form-input"),
            Label("Start Date:", classes="form-label"),
            MaskedInput(placeholder="YYYY-MM-DD HH:MM", id="start_date", template="0000-00-00 00:00", classes="form-input"),
            Label("End Date:", classes="form-label"),
            MaskedInput(placeholder="YYYY-MM-DD HH:MM", id="end_date", template="0000-00-00 00:00", classes="form-input"),
            Label("Attendees:", classes="form-label"),
            Input(placeholder="Number of attendees", id="attendees", classes="form-input"),
            Label("Description:", classes="form-label"),
            Input(placeholder="Event description (optional)", id="description", classes="form-input"),
            Label("Location ID:", classes="form-label"),
            Input(placeholder="Location ID", id="location_id", classes="form-input"),
            Label("Contract ID:", classes="form-label"),
            Input(placeholder="Contract ID", id="contract_id", classes="form-input"),
            Container(
                Button("Create", id="create", variant="primary", classes="form-button"),
                Button("Cancel", id="cancel", variant="default", classes="form-button"),
                classes="form-buttons",
            ),
            classes="form-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.collect_form_data()
            self.dismiss(self.event_data)
        elif event.button.id == "cancel":
            self.dismiss(None)

    def collect_form_data(self) -> dict:
        """Collect all form data into a dictionary."""
        self.event_data = {
            "name": self.query_one("#name", Input).value,
            "start_date": self.query_one("#start_date", Input).value,
            "end_date": self.query_one("#end_date", Input).value,
            "attendees": self.query_one("#attendees", Input).value,
            "description": self.query_one("#description", Input).value,
            "location_id": self.query_one("#location_id", Input).value,
            "contract_id": self.query_one("#contract_id", Input).value,
        }
        return self.event_data