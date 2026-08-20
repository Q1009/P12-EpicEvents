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

    BINDINGS = [
        ('d', 'sort_by_start_date', 'Sort By Date'),
        ('a', 'show_all_events', 'Show All Events'),
        ('e', 'filter_by_user', 'Show My Events'),
        ('u', 'filter_by_support', 'Show Unsupported Events')
    ]

    def __init__(self, events: list[Event]) -> None:
        super().__init__()
        self.events = events

    def compose(self) -> ComposeResult:
        yield Header("EPIC EVENTS - EVENTS")
        yield Label(f'This is the event menu.')
        yield DataTable(id='events-table')
        yield Button('Create Event', id='create-event', variant='success')
        yield Button('Update Event', id='update-event', variant='warning')
        yield Button('Delete Event', id='delete-event', variant='error')
        yield Button('Back', id='back', variant='primary')
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        #Configure table columns
        table.add_column("ID", key='id')
        table.add_column("Event Name", key='name')
        table.add_column("Start Date", key='start_date')
        table.add_column("End Date")
        table.add_column("Attendees")
        table.add_column("Description")
        table.add_column("Location ID")
        table.add_column("Support ID", key='support_id')
        table.add_column("Contract ID")
        table.loading = True
        self.load_events()

    def load_events(self) -> None:
        """
        """
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.clear()

        for event in self.events:
            # start_date = event.start_date.strftime("%Y-%m-%d %H:%M") if isinstance(event.start_date, datetime) else str(event.start_date)
            # end_date = event.end_date.strftime("%Y-%m-%d %H:%M") if isinstance(event.end_date, datetime) else str(event.end_date)
            # location_name = event.location.name if event.location else "N/A"

            # add raw data
            table.add_row(
                event.id,
                event.name,
                event.start_date,
                event.end_date,
                event.attendees,
                event.description,
                event.location_id,
                event.support_representative_id,
                event.contract_id,
            )

        table.loading = False

    # def switch_order(self, sort_type: str) -> None:
    #     order = sort_type in self.current_sorts
    #     if order:
    #         return False
    #     return True

    def action_sort_by_start_date(self) -> None:
        """
        """
        table = self.query_one(DataTable)
        table.sort('start_date', 'support_id')

    def action_show_all_events(self):
        """
        """
        self.dismiss('display_all_events')

    def action_filter_by_user(self):
        """
        """
        self.dismiss('display_own_events')

    def action_filter_by_support(self):
        """
        """
        self.dismiss('display_unsupported_events')

    @on(Button.Pressed, "#create-event")
    def go_create_event(self) -> None:
        self.dismiss('create_event')

    @on(Button.Pressed, "#update-event")
    def go_update_event(self) -> None:
        self.dismiss('update_event')

    @on(Button.Pressed, "#delete-event")
    def go_delete_event(self) -> None:
        self.dismiss('delete_event')

    @on(Button.Pressed, "#back")
    def go_back(self) -> None:
        self.dismiss('Quit')