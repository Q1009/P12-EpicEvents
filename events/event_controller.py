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
    EventScreen,
    UpdateEventScreen,
)


class EventController:
    """ """

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None

    def start(self, on_back=None):
        self.on_back_callback = on_back
        events = self.get_all_events()
        events_screen = EventScreen(events)
        self.epic_events_app.push_screen(
            events_screen, callback=self.handle_user_choice
        )

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from event menu"""
        match user_choice:
            case "create_event":
                all_locations = self.get_all_locations()
                signed_contracts = (
                    self.get_signed_contracts_without_event()
                )
                create_event_screen = CreateEventScreen(
                    all_locations, signed_contracts
                )
                self.epic_events_app.push_screen(
                    create_event_screen,
                    callback=self.create_event,
                )
            case ("create_event", contract_id):
                all_locations = self.get_all_locations()
                signed_contracts = (
                    self.get_signed_contracts_without_event()
                )
                create_event_screen = CreateEventScreen(
                    all_locations, signed_contracts, contract_id
                )
                self.epic_events_app.push_screen(
                    create_event_screen,
                    callback=self.create_event,
                )
            case ("update_event", event_id):
                all_locations = self.get_all_locations()
                signed_contracts = self.get_signed_contracts_with_event()
                support_representatives = (
                    self.get_support_representatives()
                )
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
            case "create_location":
                pass
                # event_data_for_event = self.get_data(event_id)
                # self.create_location(
                #     event_data_for_event
                # )
            case ("update_location", location_id):
                pass
                # event_data_for_event = self.get_data(event_id)
                # self.update_location(
                #     event_data_for_event
                # )
            case ("consult_customer", customer_id):
                pass
            case ("consult_contract", contract_id):
                pass
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

    def get_all_locations(self) -> list[Location]:
        return self.session.query(Location).all()

    def get_signed_contracts_with_event(self) -> list[Contract]:
        return (
            self.session.query(Contract)
            .filter(Contract.status == ContractStatus.SIGNED)
            .all()
        )

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

    def create_event(self, new_event_data):
        """ """
        # If creation is cancelled
        if not new_event_data:
            self.epic_events_app.notify(
                "Event creation cancelled", severity="warning"
            )
            self.start(self.on_back_callback)
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

        # Create event object with transformed data
        event = Event(
            name=new_event_data["event_name"],
            start_date=new_event_data["event_start_date"],
            end_date=new_event_data["event_end_date"],
            attendees=new_event_data["event_attendees"],
            description=new_event_data["event_description"],
            contract=new_event_data["event_contract"],
            location=new_event_location,
        )
        # event.location.append(new_event_location)

        self.session.add(event)
        self.session.commit()
        self.epic_events_app.notify(
            "Event successfully created", severity="information"
        )
        self.start(self.on_back_callback)

    def update_event(self, updated_event_data):
        """ """
        if not updated_event_data:
            self.epic_events_app.notify(
                "Event update cancelled", severity="warning"
            )
            self.start(self.on_back_callback)
            return

        self.session.query(Event).filter(
            Event.id == updated_event_data["event_id"]
        ).update(
            {
                "name": updated_event_data["event_name"],
                "start_date": updated_event_data["event_start_date"],
                "end_date": updated_event_data["event_end_date"],
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
        self.start(self.on_back_callback)

    def create_location(self):
        pass

    def update_location(self):
        pass
