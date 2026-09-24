from sqlalchemy.orm import Session, joinedload

from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
)
from contracts.contract_model import Contract, ContractStatus
from events.event_model import Event, Location
from events.event_view import (
    CreateEventScreen,
    CreateLocationScreen,
    EventScreen,
    UpdateEventScreen,
    UpdateLocationScreen,
)
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
)
from services.date_services import (
    format_utc_datetime,
)


class EventController:
    """ """

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None
        self.on_consult_customer_callback = None
        self.on_consult_contract_callback = None

    def start(
        self,
        event_id=None,
        contract_id=None,
        on_back=None,
        on_consult_customer=None,
        on_consult_contract=None,
    ):
        self.on_back_callback = on_back
        self.on_consult_customer_callback = on_consult_customer
        self.on_consult_contract_callback = on_consult_contract

        if contract_id is not None:
            self.push_create_event_screen(contract_id)
            return

        events = self.get_all_events()
        self.push_event_screen(events, event_id)

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from event menu"""
        match user_choice:
            case "create_event":
                self.push_create_event_screen()
            case ("create_event", contract_id):
                self.push_create_event_screen(contract_id)
            case ("update_event", event_id):
                self.push_update_event_screen(event_id)
            case "create_location":
                self.push_create_location_screen()
            case ("update_location", location_id):
                self.push_update_location_screen(location_id)
            case ("consult_customer", customer_id):
                self.on_consult_customer_callback(customer_id)
                return
            case ("consult_contract", contract_id):
                self.on_consult_contract_callback(contract_id)
                return
            case ("filter_unsupported_events", filtered_table):
                events = self.get_unsupported_events()
                self.push_event_screen(
                    events, filtered_table_supported=filtered_table
                )
            case ("filter_user_events_as_support", filtered_table):
                events = (
                    self.get_events_by_support_representative_as_user()
                )
                self.push_event_screen(
                    events, filtered_table_ownership=filtered_table
                )
            case ("filter_reset", filtered_table):
                events = self.get_all_events()
                self.push_event_screen(
                    events,
                    filtered_table_supported=filtered_table,
                    filtered_table_ownership=filtered_table,
                )
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
                return
            case "quit":
                self.epic_events_app.exit()

    def get_all_events(self) -> list[Event]:
        """
        Returns all events from the database.
        """
        return (
            self.session.query(Event)
            .options(
                joinedload(Event.contract),
                joinedload(Event.location),
                joinedload(Event.support_representative),
            )
            .all()
        )

    def get_unsupported_events(self) -> list[Event]:
        """
        Returns all unsupported events from the database.
        """
        return (
            self.session.query(Event)
            .options(
                joinedload(Event.contract),
                joinedload(Event.location),
                joinedload(Event.support_representative),
            )
            .filter(
                Event.support_representative == None,
            )
            .all()
        )

    def get_events_by_support_representative_as_user(self) -> list[Event]:
        user = AuthenticationServices.get_user_info(self.session)
        if user is None:
            return []
        return (
            self.session.query(Event)
            .filter(Event.support_representative_id == user.id)
            .all()
        )

    def get_all_locations(self) -> list[Location]:
        return self.session.query(Location).all()

    def get_signed_contracts_without_event(self) -> list[Contract]:
        return (
            self.session.query(Contract)
            .filter(
                Contract.status == ContractStatus.SIGNED,
                Contract.event == None,
            )
            .all()
        )

    def get_support_representatives(self) -> list[Collaborator]:
        return (
            self.session.query(Collaborator)
            .join(Collaborator.department)
            .filter(Department.name == DepartmentName.SUPPORT)
            .all()
        )

    def load_event_data_for_update(self, event_id: int):
        event = (
            self.session.query(Event).filter(Event.id == event_id).first()
        )

        return {
            "event_id": event.id,
            "event_name": event.name,
            "event_start_date": event.start_date,
            "event_end_date": event.end_date,
            "event_attendees": event.attendees,
            "event_description": event.description,
            "event_contract": event.contract,
            "event_location": event.location,
            "event_support_representative": event.support_representative,
        }

    def load_location_data_for_update(self, location_id: int):
        location = (
            self.session.query(Location)
            .filter(Location.id == location_id)
            .first()
        )

        return {
            "location_id": location.id,
            "location_name": location.name,
            "location_street_number": location.street_number,
            "location_street_name": location.street_name,
            "location_zip_code": location.zip_code,
            "location_city": location.city,
        }

    @AuthenticationServices.check_authentication
    def push_event_screen(
        self,
        events: list[Event],
        event_id: int | None = None,
        filtered_table_supported: bool = False,
        filtered_table_ownership: bool = False,
    ):
        """
        Push the event list screen onto the application screen stack.

        Instantiates an :class:`EventScreen` with the provided events, optional
        pre-selected event ID, and filter states, then pushes it onto the
        application's screen stack with a callback to :meth:`handle_user_choice`.

        :param events: List of :class:`Event` objects to display in the screen table.
        :type events: list[Event]
        :param event_id: Optional ID of an event to pre-select in the table.
            If provided, the corresponding event will be highlighted. Defaults to None.
        :type event_id: int | None
        :param filtered_table_supported: Flag indicating whether the table is filtered
            to show only unsupported events. Defaults to False.
        :type filtered_table_supported: bool
        :param filtered_table_ownership: Flag indicating whether the table is filtered
            to show only events assigned to the current user. Defaults to False.
        :type filtered_table_ownership: bool
        :return: None
        :rtype: None
        """
        events_screen = EventScreen(
            events=events,
            event_id=event_id,
            filtered_table_supported=filtered_table_supported,
            filtered_table_ownership=filtered_table_ownership,
        )
        self.epic_events_app.push_screen(
            events_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_create_event_screen(self, contract_id: int | None = None):
        """
        Push the create event screen onto the application screen stack.

        Instantiates a :class:`CreateEventScreen` with all available locations
        and signed contracts without an associated event, then pushes it onto
        the application's screen stack with a callback to :meth:`create_event`.

        :param contract_id: Optional contract ID to pre-select in the creation form.
            If provided, the corresponding contract will be pre-selected. Defaults to None.
        :type contract_id: int | None
        :return: None
        :rtype: None
        """
        all_locations = self.get_all_locations()
        signed_contracts = self.get_signed_contracts_without_event()
        create_event_screen = CreateEventScreen(
            all_locations, signed_contracts, contract_id
        )
        self.epic_events_app.push_screen(
            create_event_screen,
            callback=self.create_event,
        )

    @AuthenticationServices.check_authentication
    def push_update_event_screen(self, event_id: int):
        """
        Push the update event screen onto the application screen stack.

        Instantiates an :class:`UpdateEventScreen` with the event data to update,
        all available locations, support representatives, and signed contracts without
        an associated event, then pushes it onto the application's screen stack
        with a callback to :meth:`update_event`.

        :param event_id: The ID of the event to update. The corresponding event data
            will be loaded and pre-filled in the update form.
        :type event_id: int
        :return: None
        :rtype: None
        """
        all_locations = self.get_all_locations()
        signed_contracts = self.get_signed_contracts_without_event()
        support_representatives = self.get_support_representatives()
        event_to_update = self.load_event_data_for_update(event_id)
        update_event_screen = UpdateEventScreen(
            event_to_update,
            all_locations,
            support_representatives,
            signed_contracts,
        )
        self.epic_events_app.push_screen(
            update_event_screen,
            callback=self.update_event,
        )

    @AuthenticationServices.check_authentication
    def push_create_location_screen(self):
        """
        Push the create location screen onto the application screen stack.

        Instantiates a :class:`CreateLocationScreen` and pushes it onto
        the application's screen stack with a callback to :meth:`create_location`.

        :return: None
        :rtype: None
        """
        create_location_screen = CreateLocationScreen()
        self.epic_events_app.push_screen(
            create_location_screen,
            callback=self.create_location,
        )

    @AuthenticationServices.check_authentication
    def push_update_location_screen(self, location_id: int):
        """
        Push the update location screen onto the application screen stack.

        Loads the data for the location to update, instantiates an
        :class:`UpdateLocationScreen` with this data, and pushes it onto
        the application's screen stack with a callback to :meth:`update_location`.

        :param location_id: The ID of the location to update. The corresponding
            location data will be loaded and pre-filled in the update form.
        :type location_id: int
        :return: None
        :rtype: None
        """
        location_to_update = self.load_location_data_for_update(
            location_id
        )
        update_location_screen = UpdateLocationScreen(location_to_update)
        self.epic_events_app.push_screen(
            update_location_screen,
            callback=self.update_location,
        )

    @AuthenticationServices.check_authentication
    def create_event(self, new_event_data):
        """ """
        # If creation is cancelled
        if not new_event_data:
            self.epic_events_app.notify(
                "Event creation cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_contract=self.on_consult_contract_callback,
            )
            return

        # Else, transform raw data (dict) from submitted form
        event_location = new_event_data["event_location"]
        if isinstance(event_location, Location):
            new_event_location = event_location
        else:
            new_event_location = Location(
                name=event_location["name"],
                street_number=event_location["street_number"],
                street_name=event_location["street_name"],
                zip_code=event_location["zip_code"],
                city=event_location["city"],
            )
            self.session.add(new_event_location)

        # Date conversion from french to utc
        new_event_start_date = format_utc_datetime(
            new_event_data["event_start_date"]
        )
        new_event_end_date = format_utc_datetime(
            new_event_data["event_end_date"]
        )

        # Create event object with transformed data
        event = Event(
            name=new_event_data["event_name"],
            start_date=new_event_start_date,
            end_date=new_event_end_date,
            attendees=new_event_data["event_attendees"],
            description=new_event_data["event_description"],
            contract=new_event_data["event_contract"],
            location=new_event_location,
        )
        self.session.add(event)

        # Commit session
        self.session.commit()
        self.epic_events_app.notify(
            "Event successfully created", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_contract=self.on_consult_contract_callback,
        )

    @AuthenticationServices.check_authentication
    def update_event(self, updated_event_data):
        """ """
        if not updated_event_data:
            self.epic_events_app.notify(
                "Event update cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_contract=self.on_consult_contract_callback,
            )
            return

        # Date conversion from french to utc
        updated_event_start_date = format_utc_datetime(
            updated_event_data["event_start_date"]
        )
        updated_event_end_date = format_utc_datetime(
            updated_event_data["event_end_date"]
        )

        self.session.query(Event).filter(
            Event.id == updated_event_data["event_id"]
        ).update(
            {
                "name": updated_event_data["event_name"],
                "start_date": updated_event_start_date,
                "end_date": updated_event_end_date,
                "attendees": updated_event_data["event_attendees"],
                "description": updated_event_data["event_description"],
                "contract_id": updated_event_data["event_contract"].id,
                "location_id": updated_event_data["event_location"].id,
                "support_representative_id": updated_event_data[
                    "event_support_representative"
                ].id,
            }
        )

        self.session.commit()
        self.epic_events_app.notify(
            "Event successfully updated", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_contract=self.on_consult_contract_callback,
        )

    @AuthenticationServices.check_authentication
    def create_location(self, new_location_data):
        """ """
        # If creation is cancelled
        if not new_location_data:
            self.epic_events_app.notify(
                "Location creation cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_contract=self.on_consult_contract_callback,
            )
            return

        # Else, transform raw data (dict) from submitted form

        new_location = Location(
            name=new_location_data["name"],
            street_number=new_location_data["street_number"],
            street_name=new_location_data["street_name"],
            zip_code=new_location_data["zip_code"],
            city=new_location_data["city"],
        )
        self.session.add(new_location)

        # Commit session
        self.session.commit()
        self.epic_events_app.notify(
            "Location successfully created", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_contract=self.on_consult_contract_callback,
        )

    @AuthenticationServices.check_authentication
    def update_location(self, updated_location_data):
        if not updated_location_data:
            self.epic_events_app.notify(
                "Location update cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_contract=self.on_consult_contract_callback,
            )
            return

        self.session.query(Location).filter(
            Location.id == updated_location_data["location_id"]
        ).update(
            {
                "name": updated_location_data["location_name"],
                "street_number": updated_location_data[
                    "location_street_number"
                ],
                "street_name": updated_location_data[
                    "location_street_name"
                ],
                "zip_code": updated_location_data["location_zip_code"],
                "city": updated_location_data["location_city"],
            }
        )

        self.session.commit()
        self.epic_events_app.notify(
            "Location successfully updated", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_contract=self.on_consult_contract_callback,
        )

    def _handle_auth_failure(self, error: AuthenticationError | None):
        """Handles authentication failure"""
        # if error:
        #     self.epic_events_app.notify(
        #         f"[bold red]⚠️  {error!s}[/bold red]", severity="error"
        #     )
        self.on_back_callback()
