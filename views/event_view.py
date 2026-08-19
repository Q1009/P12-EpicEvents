from models import Event
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, Button
from textual import on
from textual.screen import Screen
from datetime import datetime

class EventScreen(Screen):
    """
    Ecran de Events
    """
    def __init__(self, events: list[Event]) -> None:
        super().__init__()
        self.events = events

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - EVENTS")
        yield Label(f'This is the event menu.')
        yield DataTable(id='events-table')
        yield Button('Back', id='back', variant='warning')

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        #Configure table columns
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Start Date")
        table.add_column("End Date")
        table.add_column("Attendees")
        table.add_column("Description")
        table.add_column("Location ID")
        table.add_column("Support ID")
        table.add_column("Contract ID")

        for event in self.events:
            start_date = event.start_date.strftime("%Y-%m-%d %H:%M") if isinstance(event.start_date, datetime) else str(event.start_date)
            end_date = event.end_date.strftime("%Y-%m-%d %H:%M") if isinstance(event.end_date, datetime) else str(event.end_date)
            location_name = event.location.name if event.location else "N/A"

            table.add_row(
                event.id,
                event.name,
                start_date,
                end_date,
                event.attendees,
                event.description,
                event.location_id,
                event.support_representative_id,
                event.contract_id,
            )

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss('Quit')