"""
Tests for EventController (event_controller.py)

Unit tests for the event management controller.
Mocks all external dependencies (App, Session, models, services).
Uses __wrapped__ to bypass @AuthenticationServices.check_authentication decorators.

Run with: pytest events/tests/test_event_controller.py -v
"""

from unittest.mock import MagicMock, patch

from collaborators.collaborator_model import (
    Collaborator,
    DepartmentName,
)
from contracts.contract_model import Contract
from customers.customer_model import Customer  # noqa: F401
from events.event_controller import EventController
from events.event_model import Event, Location
from services.authentication_services import AuthenticationError

# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestEventControllerInitialization:
    """Tests for __init__ method."""

    def test_init_stores_dependencies(self):
        """__init__ should store app, session, and initialize callbacks to None."""
        mock_app = MagicMock()
        mock_session = MagicMock()

        controller = EventController(mock_app, mock_session)

        assert controller.epic_events_app == mock_app
        assert controller.session == mock_session
        assert controller.on_back_callback is None
        assert controller.on_consult_customer_callback is None
        assert controller.on_consult_contract_callback is None


# =============================================================================
# START TESTS
# =============================================================================


class TestEventControllerStart:
    """Tests for start() method."""

    @patch(
        "events.event_controller.EventController.push_create_event_screen"
    )
    def test_start_with_contract_id(self, mock_push):
        """start() with contract_id should call push_create_event_screen(contract_id)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.start(contract_id=1, on_back=lambda: None)

        mock_push.assert_called_once_with(1)

    @patch("events.event_controller.EventController.get_all_events")
    @patch("events.event_controller.EventController.push_event_screen")
    def test_start_without_contract_id(self, mock_push, mock_get_all):
        """start() without contract_id should call get_all_events() and push_event_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_events = [MagicMock(spec=Event)]
        mock_get_all.return_value = mock_events

        controller = EventController(mock_app, mock_session)
        controller.start(event_id=1)

        mock_get_all.assert_called_once()
        mock_push.assert_called_once_with(mock_events, 1)


# =============================================================================
# HANDLE USER CHOICE TESTS
# =============================================================================


class TestEventControllerHandleUserChoice:
    """Tests for handle_user_choice() method."""

    @patch(
        "events.event_controller.EventController.push_create_event_screen"
    )
    def test_create_event_choice(self, mock_push):
        """'create_event' choice should call push_create_event_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.handle_user_choice("create_event")
        mock_push.assert_called_once()

    @patch(
        "events.event_controller.EventController.push_create_event_screen"
    )
    def test_create_event_with_contract_id_choice(self, mock_push):
        """('create_event', contract_id) choice should call push_create_event_screen(contract_id)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.handle_user_choice(("create_event", 1))
        mock_push.assert_called_once_with(1)

    @patch(
        "events.event_controller.EventController.push_update_event_screen"
    )
    def test_update_event_choice(self, mock_push):
        """('update_event', event_id) choice should call push_update_event_screen(event_id)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.handle_user_choice(("update_event", 1))
        mock_push.assert_called_once_with(1)

    @patch(
        "events.event_controller.EventController.push_create_location_screen"
    )
    def test_create_location_choice(self, mock_push):
        """'create_location' choice should call push_create_location_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.handle_user_choice("create_location")
        mock_push.assert_called_once()

    @patch(
        "events.event_controller.EventController.push_update_location_screen"
    )
    def test_update_location_choice(self, mock_push):
        """('update_location', location_id) choice should call push_update_location_screen(location_id)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.handle_user_choice(("update_location", 1))
        mock_push.assert_called_once_with(1)

    def test_consult_customer_choice(self):
        """('consult_customer', customer_id) choice should call on_consult_customer_callback(customer_id)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)
        mock_callback = MagicMock()
        controller.on_consult_customer_callback = mock_callback

        controller.handle_user_choice(("consult_customer", 1))
        mock_callback.assert_called_once_with(1)

    def test_consult_contract_choice(self):
        """('consult_contract', contract_id) choice should call on_consult_contract_callback(contract_id)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)
        mock_callback = MagicMock()
        controller.on_consult_contract_callback = mock_callback

        controller.handle_user_choice(("consult_contract", 1))
        mock_callback.assert_called_once_with(1)

    @patch(
        "events.event_controller.EventController.get_unsupported_events"
    )
    @patch("events.event_controller.EventController.push_event_screen")
    def test_filter_unsupported_events_choice(self, mock_push, mock_get):
        """('filter_unsupported_events', True) choice should call get_unsupported_events() and push_event_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_events = [MagicMock(spec=Event)]
        mock_get.return_value = mock_events

        controller = EventController(mock_app, mock_session)
        controller.handle_user_choice(("filter_unsupported_events", True))

        mock_get.assert_called_once()
        mock_push.assert_called_once_with(
            mock_events, filtered_table_supported=True
        )

    @patch(
        "events.event_controller.EventController.get_events_by_support_representative_as_user"
    )
    @patch("events.event_controller.EventController.push_event_screen")
    def test_filter_user_events_as_support_choice(
        self, mock_push, mock_get
    ):
        """('filter_user_events_as_support', True) should call get_events_by_support_representative_as_user() and push_event_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_events = [MagicMock(spec=Event)]
        mock_get.return_value = mock_events

        controller = EventController(mock_app, mock_session)
        controller.handle_user_choice(
            ("filter_user_events_as_support", True)
        )

        mock_get.assert_called_once()
        mock_push.assert_called_once_with(
            mock_events, filtered_table_ownership=True
        )

    @patch("events.event_controller.EventController.get_all_events")
    @patch("events.event_controller.EventController.push_event_screen")
    def test_filter_reset_choice(self, mock_push, mock_get):
        """('filter_reset', False) choice should call get_all_events() and push_event_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_events = [MagicMock(spec=Event)]
        mock_get.return_value = mock_events

        controller = EventController(mock_app, mock_session)
        controller.handle_user_choice(("filter_reset", False))

        mock_get.assert_called_once()
        mock_push.assert_called_once_with(
            mock_events,
            filtered_table_supported=False,
            filtered_table_ownership=False,
        )

    def test_back_choice(self):
        """'back' choice should call on_back_callback()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)
        mock_callback = MagicMock()
        controller.on_back_callback = mock_callback

        controller.handle_user_choice("back")
        mock_callback.assert_called_once()

    def test_quit_choice(self):
        """'quit' choice should call app.exit()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        controller.handle_user_choice("quit")
        mock_app.exit.assert_called_once()


# =============================================================================
# GET METHODS TESTS
# =============================================================================


class TestEventControllerGetMethods:
    """Tests for data retrieval methods (get_*)."""

    def test_get_all_events(self):
        """get_all_events() should return all events with eager loading."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_events = [MagicMock(spec=Event), MagicMock(spec=Event)]

        mock_query = MagicMock()
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_events
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.get_all_events()

        mock_session.query.assert_called_once_with(Event)
        mock_query.all.assert_called_once()
        assert result == mock_events

    def test_get_unsupported_events(self):
        """get_unsupported_events() should filter events without support representative."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_events = [MagicMock(spec=Event)]

        mock_query = MagicMock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_events
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.get_unsupported_events()

        mock_session.query.assert_called_once_with(Event)
        mock_query.filter.assert_called_once()
        mock_query.all.assert_called_once()
        assert result == mock_events

    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_get_events_by_support_representative_as_user(
        self, mock_get_user_info
    ):
        """get_events_by_support_representative_as_user() should filter by current user."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_user = MagicMock(spec=Collaborator)
        mock_user.id = 1
        mock_events = [MagicMock(spec=Event)]

        mock_get_user_info.return_value = mock_user

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_events
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.get_events_by_support_representative_as_user()

        mock_get_user_info.assert_called_once_with(mock_session)
        mock_session.query.assert_called_once_with(Event)
        mock_query.filter.assert_called_once()
        mock_query.all.assert_called_once()
        assert result == mock_events

    def test_get_events_by_support_representative_as_user_with_no_user(
        self,
    ):
        """get_events_by_support_representative_as_user() should return empty list when no user."""
        mock_app = MagicMock()
        mock_session = MagicMock()

        with patch(
            "services.authentication_services.AuthenticationServices.get_user_info",
            return_value=None,
        ):
            controller = EventController(mock_app, mock_session)
            result = (
                controller.get_events_by_support_representative_as_user()
            )
            assert result == []

    def test_get_all_locations(self):
        """get_all_locations() should return all locations."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_locations = [
            MagicMock(spec=Location),
            MagicMock(spec=Location),
        ]

        mock_query = MagicMock()
        mock_query.all.return_value = mock_locations
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.get_all_locations()

        mock_session.query.assert_called_once_with(Location)
        mock_query.all.assert_called_once()
        assert result == mock_locations

    def test_get_signed_contracts_without_event(self):
        """get_signed_contracts_without_event() should filter signed contracts without event."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_contracts = [
            MagicMock(spec=Contract),
            MagicMock(spec=Contract),
        ]

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_contracts
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.get_signed_contracts_without_event()

        mock_session.query.assert_called_once_with(Contract)
        mock_query.filter.assert_called_once()
        assert result == mock_contracts

    @patch("events.event_controller.DepartmentName")
    def test_get_support_representatives(self, mock_department_name):
        """get_support_representatives() should return support department collaborators."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_reps = [
            MagicMock(spec=Collaborator),
            MagicMock(spec=Collaborator),
        ]
        mock_department_name.SUPPORT = DepartmentName.SUPPORT

        mock_query = MagicMock()
        mock_joined_query = MagicMock()
        mock_joined_query.filter.return_value = mock_joined_query
        mock_joined_query.all.return_value = mock_reps
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_joined_query

        controller = EventController(mock_app, mock_session)
        result = controller.get_support_representatives()

        mock_session.query.assert_called_once_with(Collaborator)
        mock_query.join.assert_called_once_with(Collaborator.department)
        mock_joined_query.filter.assert_called_once()
        mock_joined_query.all.assert_called_once()
        assert result == mock_reps

    def test_load_event_data_for_update(self):
        """load_event_data_for_update(event_id) should return event data as dict."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_event = MagicMock(spec=Event)
        mock_event.id = 1
        mock_event.name = "Test Event"
        mock_event.start_date = "2024-01-01"
        mock_event.end_date = "2024-01-02"
        mock_event.attendees = 100
        mock_event.description = "Test description"
        mock_event.contract = MagicMock(spec=Contract)
        mock_event.location = MagicMock(spec=Location)
        mock_event.support_representative = MagicMock(spec=Collaborator)

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_event
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.load_event_data_for_update(1)

        mock_session.query.assert_called_once_with(Event)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

        assert result == {
            "event_id": 1,
            "event_name": "Test Event",
            "event_start_date": "2024-01-01",
            "event_end_date": "2024-01-02",
            "event_attendees": 100,
            "event_description": "Test description",
            "event_contract": mock_event.contract,
            "event_location": mock_event.location,
            "event_support_representative": mock_event.support_representative,
        }

    def test_load_location_data_for_update(self):
        """load_location_data_for_update(location_id) should return location data as dict."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_location = MagicMock(spec=Location)
        mock_location.id = 1
        mock_location.name = "Test Location"
        mock_location.street_number = "123"
        mock_location.street_name = "Main Street"
        mock_location.zip_code = "75000"
        mock_location.city = "Paris"

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_location
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)
        result = controller.load_location_data_for_update(1)

        mock_session.query.assert_called_once_with(Location)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

        assert result == {
            "location_id": 1,
            "location_name": "Test Location",
            "location_street_number": "123",
            "location_street_name": "Main Street",
            "location_zip_code": "75000",
            "location_city": "Paris",
        }


# =============================================================================
# PUSH SCREEN TESTS
# =============================================================================


class TestEventControllerPushScreens:
    """Tests for push_*_screen() methods (bypassing decorators with __wrapped__)."""

    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    @patch("events.event_controller.EventScreen")
    def test_push_event_screen(
        self, mock_event_screen, mock_get_user_info
    ):
        """push_event_screen should instantiate EventScreen and push to app."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_user = MagicMock(spec=Collaborator)
        mock_events = [MagicMock(spec=Event)]
        mock_screen_instance = MagicMock()

        mock_get_user_info.return_value = mock_user
        mock_event_screen.return_value = mock_screen_instance

        controller = EventController(mock_app, mock_session)
        EventController.push_event_screen.__wrapped__(
            controller,
            events=mock_events,
            event_id=1,
            filtered_table_supported=True,
            filtered_table_ownership=False,
        )

        mock_get_user_info.assert_called_once_with(mock_session)
        mock_event_screen.assert_called_once_with(
            events=mock_events,
            user=mock_user,
            event_id=1,
            filtered_table_supported=True,
            filtered_table_ownership=False,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.handle_user_choice
        )

    @patch("events.event_controller.EventController.get_all_locations")
    @patch(
        "events.event_controller.EventController.get_signed_contracts_without_event"
    )
    @patch("events.event_controller.CreateEventScreen")
    def test_push_create_event_screen(
        self, mock_create_screen, mock_get_contracts, mock_get_locations
    ):
        """push_create_event_screen should get locations/contracts and instantiate CreateEventScreen."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_locations = [MagicMock(spec=Location)]
        mock_contracts = [MagicMock(spec=Contract)]
        mock_screen_instance = MagicMock()

        mock_get_locations.return_value = mock_locations
        mock_get_contracts.return_value = mock_contracts
        mock_create_screen.return_value = mock_screen_instance

        controller = EventController(mock_app, mock_session)
        EventController.push_create_event_screen.__wrapped__(
            controller, contract_id=1
        )

        mock_get_locations.assert_called_once()
        mock_get_contracts.assert_called_once()
        mock_create_screen.assert_called_once_with(
            locations=mock_locations,
            signed_contracts=mock_contracts,
            contract_id=1,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.create_event
        )

    @patch("events.event_controller.EventController.get_all_locations")
    @patch(
        "events.event_controller.EventController.get_signed_contracts_without_event"
    )
    @patch(
        "events.event_controller.EventController.get_support_representatives"
    )
    @patch(
        "events.event_controller.EventController.load_event_data_for_update"
    )
    @patch("events.event_controller.UpdateEventScreen")
    def test_push_update_event_screen(
        self,
        mock_update_screen,
        mock_load_event,
        mock_get_reps,
        mock_get_contracts,
        mock_get_locations,
    ):
        """push_update_event_screen should get all data and instantiate UpdateEventScreen."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_locations = [MagicMock(spec=Location)]
        mock_contracts = [MagicMock(spec=Contract)]
        mock_reps = [MagicMock(spec=Collaborator)]
        mock_event_data = {"event_id": 1, "event_name": "Test"}
        mock_screen_instance = MagicMock()

        mock_get_locations.return_value = mock_locations
        mock_get_contracts.return_value = mock_contracts
        mock_get_reps.return_value = mock_reps
        mock_load_event.return_value = mock_event_data
        mock_update_screen.return_value = mock_screen_instance

        controller = EventController(mock_app, mock_session)
        EventController.push_update_event_screen.__wrapped__(
            controller, event_id=1
        )

        mock_get_locations.assert_called_once()
        mock_get_contracts.assert_called_once()
        mock_get_reps.assert_called_once()
        mock_load_event.assert_called_once_with(1)
        mock_update_screen.assert_called_once_with(
            event_data=mock_event_data,
            locations=mock_locations,
            support_representatives=mock_reps,
            signed_contracts=mock_contracts,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.update_event
        )

    @patch("events.event_controller.CreateLocationScreen")
    def test_push_create_location_screen(self, mock_create_screen):
        """push_create_location_screen should instantiate CreateLocationScreen."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_screen_instance = MagicMock()
        mock_create_screen.return_value = mock_screen_instance

        controller = EventController(mock_app, mock_session)
        EventController.push_create_location_screen.__wrapped__(controller)

        mock_create_screen.assert_called_once()
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.create_location
        )

    @patch(
        "events.event_controller.EventController.load_location_data_for_update"
    )
    @patch("events.event_controller.UpdateLocationScreen")
    def test_push_update_location_screen(
        self, mock_update_screen, mock_load_location
    ):
        """push_update_location_screen should load data and instantiate UpdateLocationScreen."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_location_data = {"location_id": 1, "location_name": "Test"}
        mock_screen_instance = MagicMock()

        mock_load_location.return_value = mock_location_data
        mock_update_screen.return_value = mock_screen_instance

        controller = EventController(mock_app, mock_session)
        EventController.push_update_location_screen.__wrapped__(
            controller, location_id=1
        )

        mock_load_location.assert_called_once_with(1)
        mock_update_screen.assert_called_once_with(
            location_data=mock_location_data
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.update_location
        )


# =============================================================================
# CRUD METHODS TESTS
# =============================================================================


class TestEventControllerCrudMethods:
    """Tests for CRUD methods (bypassing decorators with __wrapped__)."""

    @patch("events.event_controller.EventController.start")
    def test_create_event_with_none(self, mock_start):
        """create_event(None) should notify and call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        EventController.create_event.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Event creation cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_contract=None,
        )

    @patch("events.event_controller.Event")
    @patch("events.event_controller.format_utc_datetime")
    @patch("events.event_controller.EventController.start")
    def test_create_event_with_valid_data(
        self,
        mock_start,
        mock_format_datetime,
        mock_event_class,
    ):
        """create_event(valid_data) should create event/location, commit, notify, call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()

        mock_event_instance = MagicMock(spec=Event)
        mock_event_class.return_value = mock_event_instance
        mock_contract = MagicMock(spec=Contract)
        mock_location = MagicMock(spec=Location)
        mock_location.name = "New Location"
        mock_location.street_number = "123"
        mock_location.street_name = "Main St"
        mock_location.zip_code = "75000"
        mock_location.city = "Paris"

        mock_format_datetime.side_effect = lambda x: f"formatted_{x}"

        controller = EventController(mock_app, mock_session)

        new_event_data = {
            "event_name": "Test Event",
            "event_start_date": "01/01/2024 (10:00:00)",
            "event_end_date": "02/01/2024 (10:00:00)",
            "event_attendees": 100,
            "event_description": "Test description",
            "event_contract": mock_contract,
            "event_location": mock_location,
        }

        EventController.create_event.__wrapped__(
            controller, new_event_data
        )

        mock_format_datetime.assert_called()
        mock_event_class.assert_called_once_with(
            name="Test Event",
            start_date="formatted_01/01/2024 (10:00:00)",
            end_date="formatted_02/01/2024 (10:00:00)",
            attendees=100,
            description="Test description",
            contract=mock_contract,
            location=mock_location,
        )
        mock_session.add.assert_any_call(mock_event_instance)
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Event successfully created", severity="information"
        )
        mock_start.assert_called_once()

    @patch("events.event_controller.EventController.start")
    def test_update_event_with_none(self, mock_start):
        """update_event(None) should notify and call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        EventController.update_event.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Event update cancelled", severity="warning"
        )
        mock_start.assert_called_once()

    @patch("events.event_controller.format_utc_datetime")
    @patch("events.event_controller.EventController.start")
    def test_update_event_with_valid_data(
        self, mock_start, mock_format_datetime
    ):
        """update_event(valid_data) should update event, commit, notify, call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_contract = MagicMock(spec=Contract)
        mock_contract.id = 1
        mock_location = MagicMock(spec=Location)
        mock_location.id = 1
        mock_support = MagicMock(spec=Collaborator)
        mock_support.id = 1

        mock_format_datetime.side_effect = lambda x: f"formatted_{x}"

        mock_query = MagicMock()
        mock_update_query = MagicMock()
        mock_query.filter.return_value = mock_update_query
        mock_session.query.return_value = mock_query

        controller = EventController(mock_app, mock_session)

        updated_event_data = {
            "event_id": 1,
            "event_name": "Updated Event",
            "event_start_date": "01/01/2024 (10:00:00)",
            "event_end_date": "02/01/2024 (10:00:00)",
            "event_attendees": 200,
            "event_description": "Updated description",
            "event_contract": mock_contract,
            "event_location": mock_location,
            "event_support_representative": mock_support,
        }

        EventController.update_event.__wrapped__(
            controller, updated_event_data
        )

        mock_session.query.assert_called_once_with(Event)
        mock_query.filter.assert_called_once()
        mock_update_query.update.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Event successfully updated", severity="information"
        )
        mock_start.assert_called_once()

    @patch("events.event_controller.EventController.start")
    def test_create_location_with_none(self, mock_start):
        """create_location(None) should notify and call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        EventController.create_location.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Location creation cancelled", severity="warning"
        )
        mock_start.assert_called_once()

    @patch("events.event_controller.EventController.start")
    def test_create_location_with_valid_data(self, mock_start):
        """create_location(valid_data) should create location, commit, notify, call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        new_location_data = {
            "name": "New Location",
            "street_number": "123",
            "street_name": "Main St",
            "zip_code": "75000",
            "city": "Paris",
        }

        EventController.create_location.__wrapped__(
            controller, new_location_data
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Location successfully created", severity="information"
        )
        mock_start.assert_called_once()

    @patch("events.event_controller.EventController.start")
    def test_update_location_with_none(self, mock_start):
        """update_location(None) should notify and call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        EventController.update_location.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Location update cancelled", severity="warning"
        )
        mock_start.assert_called_once()

    @patch("events.event_controller.EventController.start")
    def test_update_location_with_valid_data(self, mock_start):
        """update_location(valid_data) should update location, commit, notify, call start()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)

        mock_query = MagicMock()
        mock_update_query = MagicMock()
        mock_query.filter.return_value = mock_update_query
        mock_session.query.return_value = mock_query

        updated_location_data = {
            "location_id": 1,
            "location_name": "Updated Location",
            "location_street_number": "456",
            "location_street_name": "Second St",
            "location_zip_code": "75001",
            "location_city": "Paris",
        }

        EventController.update_location.__wrapped__(
            controller, updated_location_data
        )

        mock_session.query.assert_called_with(Location)
        mock_query.filter.assert_called_once()
        mock_update_query.update.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Location successfully updated", severity="information"
        )


# =============================================================================
# AUTH FAILURE TESTS
# =============================================================================


class TestEventControllerAuthFailure:
    """Tests for _handle_auth_failure() method."""

    def test_handle_auth_failure_with_error(self):
        """_handle_auth_failure with error should notify and call on_back_callback()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)
        mock_callback = MagicMock()
        controller.on_back_callback = mock_callback
        test_error = AuthenticationError("Invalid token")

        controller._handle_auth_failure(test_error)

        mock_app.notify.assert_called_once_with(
            "[bold red]⚠️  Invalid token[/bold red]", severity="error"
        )
        mock_callback.assert_called_once()

    def test_handle_auth_failure_without_error(self):
        """_handle_auth_failure without error should only call on_back_callback()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = EventController(mock_app, mock_session)
        mock_callback = MagicMock()
        controller.on_back_callback = mock_callback

        controller._handle_auth_failure(None)

        mock_app.notify.assert_not_called()
        mock_callback.assert_called_once()
