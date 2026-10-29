"""
Tests for event_view.py

UI tests for EventScreen, CreateEventScreen, UpdateEventScreen,
CreateLocationScreen, and UpdateLocationScreen.
Uses run_test() for Textual UI tests, verifies widget structure,
handlers, and form behavior.

Run with: pytest events/tests/test_event_view.py -v
"""

from unittest.mock import MagicMock

import pytest
from textual.app import App
from textual.containers import Container
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

from app.epic_events import EpicEventsCRM
from collaborators.collaborator_model import Collaborator, DepartmentName
from contracts.contract_model import Contract
from customers.customer_model import Customer  # noqa: F401
from events.event_model import Event, Location
from events.event_view import (
    CreateEventScreen,
    CreateLocationScreen,
    EventScreen,
    UpdateEventScreen,
    UpdateLocationScreen,
)
from services.date_services import format_utc_datetime

# =============================================================================
# FIXTURES : Collaborators and Events
# =============================================================================


@pytest.fixture
def mock_sales_collaborator():
    """Collaborator from SALES department."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 1

    # Assign department
    mock_user.department = MagicMock()
    mock_user.department.name = DepartmentName.SALES

    return mock_user


@pytest.fixture
def mock_support_collaborator():
    """Collaborator from SUPPORT department."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 2
    mock_user.first_name = "Marc"
    mock_user.last_name = "Durand"

    # Assign department
    mock_user.department = MagicMock()
    mock_user.department.name = DepartmentName.SUPPORT

    return mock_user


@pytest.fixture
def mock_admin_collaborator():
    """Collaborator from ADMIN department."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 3

    # Assign department
    mock_user.department = MagicMock()
    mock_user.department.name = DepartmentName.ADMIN

    return mock_user


@pytest.fixture
def mock_complete_event_1(mock_locations, mock_contracts):
    """Fixture Event with all needed attributes configured."""
    # Event
    mock_event = MagicMock(spec=Event)
    mock_event.id = 1
    mock_event.name = "Test Event"
    mock_event.start_date = format_utc_datetime("01/01/2027 (00:00:00)")
    mock_event.end_date = format_utc_datetime("02/01/2027 (00:00:00)")
    mock_event.attendees = 100
    mock_event.description = "Test description"
    # Contract + Customer
    mock_event.contract = mock_contracts[0]
    # Location
    mock_event.location = mock_locations[0]
    # Support representative
    mock_event.support_representative_id = None

    return mock_event


@pytest.fixture
def mock_complete_event_2(
    mock_locations, mock_contracts, mock_support_collaborator
):
    """Fixture Event with all needed attributes configured."""
    # Event
    mock_event = MagicMock(spec=Event)
    mock_event.id = 2
    mock_event.name = "Test Event 2"
    mock_event.start_date = format_utc_datetime("01/02/2027 (00:00:00)")
    mock_event.end_date = format_utc_datetime("02/02/2027 (00:00:00)")
    mock_event.attendees = 50
    mock_event.description = "Test description 2"
    # Contract + Customer
    mock_event.contract = mock_contracts[1]
    # Location
    mock_event.location = mock_locations[1]
    # Support representative
    mock_event.support_representative = mock_support_collaborator
    mock_event.support_representative_id = mock_support_collaborator.id

    return mock_event


# =============================================================================
# EVENT SCREEN TESTS
# =============================================================================


class TestEventScreen:
    """Tests for EventScreen UI and behavior."""

    # =============================================
    # INITIALIZATION
    # =============================================

    @pytest.mark.asyncio
    async def test_initialization(self):
        """__init__ should store parameters and set class attributes."""
        mock_events = [MagicMock(spec=Event)]
        mock_user = MagicMock(spec=Collaborator)
        screen = EventScreen(
            events=mock_events,
            user=mock_user,
            event_id=1,
            filtered_table_supported=True,
            filtered_table_ownership=True,
        )
        assert screen.SUB_TITLE == "EVENTS"
        assert screen.CSS_PATH == "../styles/event_screen.tcss"
        assert screen.events == mock_events
        assert screen.current_user == mock_user
        assert screen.pre_selected_event_id == 1
        assert screen.filtered_table_supported is True
        assert screen.filtered_table_ownership is True

    @pytest.mark.asyncio
    async def test_default_initialization(self):
        """__init__ should set default values for optional parameters."""
        mock_user = MagicMock(spec=Collaborator)
        screen = EventScreen(events=[], user=mock_user)
        assert screen.pre_selected_event_id is None
        assert screen.filtered_table_supported is False
        assert screen.filtered_table_ownership is False
        assert screen.selected_contract_id is None

    # =============================================
    # UI ARCHITECTURE (Header, Footer, Widgets)
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists_with_clock(self, mock_sales_collaborator):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(EventScreen([], mock_sales_collaborator))
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "EVENTS"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists_without_command_palette(
        self, mock_sales_collaborator
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(EventScreen([], mock_sales_collaborator))
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_data_tables_exist(self, mock_sales_collaborator):
        """All 4 DataTables should exist with correct IDs."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(EventScreen([], mock_sales_collaborator))
            await pilot.pause()
            for table_id in [
                "#events-table",
                "#event-location-table",
                "#event-customer-table",
                "#event-contract-table",
            ]:
                table = pilot.app.screen.query_one(table_id, DataTable)
                assert table is not None

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(self, mock_sales_collaborator):
        """All 6 action buttons should exist with correct IDs."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(EventScreen([], mock_sales_collaborator))
            await pilot.pause()
            for button_id in [
                "#create-event",
                "#update-event",
                "#create-location",
                "#update-location",
                "#consult-customer",
                "#consult-contract",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    @pytest.mark.asyncio
    async def test_events_table_has_correct_columns(
        self, mock_sales_collaborator
    ):
        """Events DataTable should have all required columns."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(EventScreen([], mock_sales_collaborator))
            await pilot.pause()
            table = pilot.app.screen.query_one("#events-table", DataTable)
            assert table is not None
            assert table.border_title == "Events"
            assert table.get_column("event_id") is not None
            assert table.get_column("event_name") is not None
            assert table.get_column("event_customer") is not None
            assert table.get_column("support_representative") is not None
            assert table.get_column("event_start_date") is not None
            assert table.get_column("event_end_date") is not None
            assert table.get_column("event_attendees") is not None

    # =============================================
    # TESTING USER ACTIONS
    # =============================================

    @pytest.mark.asyncio
    async def test_create_event_button_dismisses_with_action(
        self, mock_sales_collaborator
    ):
        """Clicking 'Create Event' should dismiss with 'create_event'."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                EventScreen([], mock_sales_collaborator),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#create-event")
            await pilot.pause()
            assert dismissed_result == "create_event"

    @pytest.mark.asyncio
    async def test_update_event_button_dismisses_with_event_id(
        self,
        mock_support_collaborator,
        mock_complete_event_1,
        mock_complete_event_2,
    ):
        """Clicking 'Update Event' should dismiss with ('update_event', event_id)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            screen = EventScreen(
                [mock_complete_event_1, mock_complete_event_2],
                mock_support_collaborator,
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()
            button = pilot.app.screen.query_one("#update-event")
            assert screen.selected_event_id == 1
            assert button.display == False
            screen.selected_event_id = 2
            await pilot.pause()
            assert button.display == True
            await pilot.click("#update-event")
            assert dismissed_result == ("update_event", 2)

    @pytest.mark.asyncio
    async def test_filter_unsupported_events_action(
        self, mock_sales_collaborator
    ):
        """Pressing 's' should dismiss with ('filter_unsupported_events', True)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                EventScreen(
                    [],
                    mock_sales_collaborator,
                    filtered_table_supported=False,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            assert dismissed_result == ("filter_unsupported_events", True)

    @pytest.mark.asyncio
    async def test_filter_user_events_as_support_action(
        self, mock_support_collaborator
    ):
        """Pressing 'e' should dismiss with ('filter_user_events_as_support', True)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                EventScreen(
                    [],
                    mock_support_collaborator,
                    filtered_table_ownership=False,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("e")
            await pilot.pause()
            assert dismissed_result == (
                "filter_user_events_as_support",
                True,
            )

    @pytest.mark.asyncio
    async def test_filter_reset_action(self, mock_sales_collaborator):
        """Pressing 'r' should dismiss with ('filter_reset', False)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                EventScreen(
                    [],
                    mock_sales_collaborator,
                    filtered_table_supported=True,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert dismissed_result == ("filter_reset", False)

    @pytest.mark.asyncio
    async def test_back_action_dismisses_with_back(
        self, mock_sales_collaborator
    ):
        """Pressing 'b' (back) should dismiss with 'back'."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                EventScreen([], mock_sales_collaborator),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("b")
            await pilot.pause()
            assert dismissed_result == "back"

    # =============================================
    # DATA SELECTION AND LOADING
    # =============================================

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_event_id(
        self,
        mock_sales_collaborator,
        mock_complete_event_1,
        mock_complete_event_2,
    ):
        """Highlighting a row should update selected_event_id."""
        app = App()

        async with app.run_test() as pilot:
            screen = EventScreen(
                [mock_complete_event_1, mock_complete_event_2],
                mock_sales_collaborator,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Click on the second line to highlight, (1, 3) is the offset for second event
            await pilot.click(widget="#events-table", offset=(1, 3))
            await pilot.pause()
            assert screen.selected_event_id == 2

    @pytest.mark.asyncio
    async def test_pre_selected_event_id_sets_cursor(
        self,
        mock_sales_collaborator,
        mock_complete_event_1,
        mock_complete_event_2,
    ):
        """Pre-selected event_id should set cursor to correct row."""
        app = App()

        async with app.run_test() as pilot:
            await app.push_screen(
                EventScreen(
                    [mock_complete_event_1, mock_complete_event_2],
                    mock_sales_collaborator,
                    event_id=2,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one("#events-table", DataTable)
            assert table.cursor_row == 1  # Index 1 = 2nd line


# =============================================================================
# SPECIFIC FIXTURES FOR CreateEventScreen
# =============================================================================


@pytest.fixture
def mock_locations():
    """Fixture for a list of Location objects."""
    mock_location1 = MagicMock(spec=Location)
    mock_location1.id = 1
    mock_location1.name = "Grand Salle"
    mock_location1.street_number = "123"
    mock_location1.street_name = "Rue de Paris"
    mock_location1.zip_code = "75000"
    mock_location1.city = "Paris"

    mock_location2 = MagicMock(spec=Location)
    mock_location2.id = 2
    mock_location2.name = "Petite Salle"
    mock_location2.street_number = "456"
    mock_location2.street_name = "Avenue des Champs"
    mock_location2.zip_code = "75001"
    mock_location2.city = "Lyon"

    return [mock_location1, mock_location2]


@pytest.fixture
def mock_contracts():
    """Fixture for a list of Contract objects with customers."""
    mock_contract1 = MagicMock(spec=Contract)
    mock_contract1.id = 1
    mock_contract1.total_amount = 10000
    mock_contract1.amount_due = 5000
    mock_customer1 = MagicMock()
    mock_customer1.id = 1
    mock_customer1.first_name = "Jean"
    mock_customer1.last_name = "Dupont"
    mock_contract1.customer = mock_customer1

    mock_contract2 = MagicMock(spec=Contract)
    mock_contract2.id = 2
    mock_contract2.total_amount = 15000
    mock_contract2.amount_due = 7500
    mock_customer2 = MagicMock()
    mock_customer2.id = 2
    mock_customer2.first_name = "Marie"
    mock_customer2.last_name = "Martin"
    mock_contract2.customer = mock_customer2

    return [mock_contract1, mock_contract2]


# =============================================================================
# CREATE EVENT SCREEN TESTS
# =============================================================================


class TestCreateEventScreen:
    """Tests for CreateEventScreen UI, form behavior, and navigation."""

    # =============================================
    # INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, mock_locations, mock_contracts):
        """__init__ should store all parameters correctly."""
        screen = CreateEventScreen(
            locations=mock_locations,
            signed_contracts=mock_contracts,
            contract_id=1,
        )
        assert screen.SUB_TITLE == "CREATE EVENT"
        assert screen.CSS_PATH == "../styles/create_event_screen.tcss"
        assert screen.locations == mock_locations
        assert screen.signed_contracts == mock_contracts
        assert screen.contract_id == 1
        assert screen.event_data == {}

    def test_initialization_with_no_contract_id(
        self, mock_locations, mock_contracts
    ):
        """__init__ should handle None contract_id."""
        screen = CreateEventScreen(
            locations=mock_locations,
            signed_contracts=mock_contracts,
            contract_id=None,
        )
        assert screen.contract_id is None
        assert screen.event_data == {}

    # =============================================
    # UI ARCHITECTURE (Header, Footer, Widgets)
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self, mock_locations, mock_contracts):
        """Header should exist with correct sub-title."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CREATE EVENT"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self, mock_locations, mock_contracts):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_main_containers_exist(
        self, mock_locations, mock_contracts
    ):
        """All main containers should exist with correct IDs."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            for container_id in [
                "#event-data",
                "#event-location",
                "#event-contract",
                "#create-event-buttons-container",
            ]:
                container = pilot.app.screen.query_one(
                    container_id, Container
                )
                assert container is not None

    @pytest.mark.asyncio
    async def test_all_event_input_fields_exist(
        self, mock_locations, mock_contracts
    ):
        """All event-related input fields should exist."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # Text inputs
            assert (
                pilot.app.screen.query_one("#event_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#event_attendees", Input)
                is not None
            )

            # Masked inputs for dates
            assert (
                pilot.app.screen.query_one(
                    "#event_start_date", MaskedInput
                )
                is not None
            )
            assert (
                pilot.app.screen.query_one("#event_end_date", MaskedInput)
                is not None
            )

            # TextArea for description
            assert (
                pilot.app.screen.query_one("#event_description", TextArea)
                is not None
            )

    @pytest.mark.asyncio
    async def test_all_location_input_fields_exist(
        self, mock_locations, mock_contracts
    ):
        """All location-related input fields should exist (hidden by default)."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # Location form inputs (hidden by default)
            assert (
                pilot.app.screen.query_one("#location_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_number", Input
                )
                is not None
            )
            assert (
                pilot.app.screen.query_one("#location_street_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#location_city", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_zip_code", MaskedInput
                )
                is not None
            )

    @pytest.mark.asyncio
    async def test_location_radio_set_exists(
        self, mock_locations, mock_contracts
    ):
        """RadioSet for location choice should exist with correct options."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            radio_set = pilot.app.screen.query_one(
                "#event-location-input-choice", RadioSet
            )
            assert radio_set is not None

            radio_labels = [
                button.label
                for button in pilot.app.screen.query(RadioButton)
            ]
            assert "Existing location" in radio_labels
            assert "New location" in radio_labels

            # Existing location button is toggled by default
            assert pilot.app.screen.query_one(RadioButton).value == True

    @pytest.mark.asyncio
    async def test_location_select_exists(
        self, mock_locations, mock_contracts
    ):
        """Select for existing location should exist."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            location_select = pilot.app.screen.query_one(
                "#event-location-select", Select
            )
            assert location_select is not None
            assert (
                len(location_select._options) == len(mock_locations) + 1
            )  # select.NULL option

    @pytest.mark.asyncio
    async def test_contract_select_exists(
        self, mock_locations, mock_contracts
    ):
        """Select for contract should exist."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            contract_select = pilot.app.screen.query_one(
                "#event-contract-select", Select
            )
            assert contract_select is not None
            assert (
                len(contract_select._options) == len(mock_contracts) + 1
            )  # select.NULL option

    @pytest.mark.asyncio
    async def test_action_buttons_exist(
        self, mock_locations, mock_contracts
    ):
        """Create and Cancel buttons should exist."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#create", Button) is not None
            )
            assert (
                pilot.app.screen.query_one("#cancel", Button) is not None
            )

    @pytest.mark.asyncio
    async def test_create_button_disabled_initially(
        self, mock_locations, mock_contracts
    ):
        """Create button should be disabled when form is empty."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    # =============================================
    # FORM BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_existing_location_selected_by_default(
        self, mock_locations, mock_contracts
    ):
        """Existing location radio should be selected by default."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            radio_set = pilot.app.screen.query_one(
                "#event-location-input-choice", RadioSet
            )
            assert radio_set.pressed_button.label == "Existing location"

    @pytest.mark.asyncio
    async def test_new_location_radio_shows_form(
        self, mock_locations, mock_contracts
    ):
        """Selecting 'New location' should show form and hide select."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # Get containers before changing radio
            select_container = pilot.app.screen.query_one(
                "#event-location-select-input-container", Container
            )
            form_container = pilot.app.screen.query_one(
                "#event-location-form-input-container", Container
            )

            # Initially select container should be visible, form hidden
            assert select_container.display is True
            assert form_container.display is False

            # Select "New location"
            await pilot.click("#new-location")
            await pilot.pause()

            # Now form should be visible, select hidden
            assert select_container.display is False
            assert form_container.display is True

    @pytest.mark.asyncio
    async def test_existing_location_radio_shows_select(
        self, mock_locations, mock_contracts
    ):
        """Selecting 'Existing location' should show select and hide form."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # First select "New location"
            await pilot.click("#new-location")
            await pilot.pause()

            select_container = pilot.app.screen.query_one(
                "#event-location-select-input-container", Container
            )
            form_container = pilot.app.screen.query_one(
                "#event-location-form-input-container", Container
            )
            assert select_container.display is False
            assert form_container.display is True

            # Then select "Existing location"
            await pilot.click("#existing-location")
            await pilot.pause()

            assert select_container.display is True
            assert form_container.display is False

    @pytest.mark.asyncio
    async def test_preselects_contract_if_contract_id_provided(
        self, mock_locations, mock_contracts
    ):
        """Contract Select should pre-select contract if contract_id matches."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    contract_id=2,
                )
            )
            await pilot.pause()
            contract_select = pilot.app.screen.query_one(
                "#event-contract-select", Select
            )
            assert contract_select is not None
            assert contract_select.value.id == 2

    @pytest.mark.asyncio
    async def test_location_select_options_match_locations(
        self, mock_locations, mock_contracts
    ):
        """Location Select options should match provided locations."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            location_select = pilot.app.screen.query_one(
                "#event-location-select", Select
            )
            assert (
                len(location_select._options) == len(mock_locations) + 1
            )  # select.NULL option
            assert (
                "Grand Salle in Paris",
                mock_locations[0],
            ) in location_select._options
            assert (
                "Petite Salle in Lyon",
                mock_locations[1],
            ) in location_select._options

    @pytest.mark.asyncio
    async def test_contract_select_options_match_contracts(
        self, mock_locations, mock_contracts
    ):
        """Contract Select options should match provided contracts."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            contract_select = pilot.app.screen.query_one(
                "#event-contract-select", Select
            )
            assert (
                len(contract_select._options) == len(mock_contracts) + 1
            )  # select.NULL option
            assert (
                "Contract ID: 1 with Jean Dupont",
                mock_contracts[0],
            ) in contract_select._options
            assert (
                "Contract ID: 2 with Marie Martin",
                mock_contracts[1],
            ) in contract_select._options

    # =============================================
    # FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_empty_form_keeps_create_button_disabled(
        self, mock_locations, mock_contracts
    ):
        """Empty form should keep Create button disabled."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    @pytest.mark.asyncio
    async def test_valid_form_enables_create_button(
        self, mock_locations, mock_contracts
    ):
        """Filling all required fields should enable Create button."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # Fill all required fields
            pilot.app.screen.query_one(
                "#event_name", Input
            ).value = "Rock Concert"
            pilot.app.screen.query_one(
                "#event_start_date", MaskedInput
            ).value = "15/12/2024 (20:00:00)"
            pilot.app.screen.query_one(
                "#event_end_date", MaskedInput
            ).value = "16/12/2024 (02:00:00)"
            pilot.app.screen.query_one(
                "#event_attendees", Input
            ).value = "500"

            # Select contract
            pilot.app.screen.query_one(
                "#event-contract-select", Select
            ).value = mock_contracts[0]

            # Select existing location
            pilot.app.screen.query_one(
                "#event-location-select", Select
            ).value = mock_locations[0]

            await pilot.pause()

            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is False

    @pytest.mark.asyncio
    async def test_missing_field_keeps_button_disabled(
        self, mock_locations, mock_contracts
    ):
        """One missing field should keep Create button disabled."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # Fill all fields except one
            # pilot.app.screen.query_one("#event_name", Input).value = "Rock Concert"
            pilot.app.screen.query_one(
                "#event_start_date", MaskedInput
            ).value = "15/12/2024 (20:00:00)"
            pilot.app.screen.query_one(
                "#event_end_date", MaskedInput
            ).value = "16/12/2024 (02:00:00)"
            pilot.app.screen.query_one(
                "#event_attendees", Input
            ).value = "500"

            # Select contract
            pilot.app.screen.query_one(
                "#event-contract-select", Select
            ).value = mock_contracts[0]

            # Select existing location
            pilot.app.screen.query_one(
                "#event-location-select", Select
            ).value = mock_locations[0]

            await pilot.pause()

            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    @pytest.mark.asyncio
    async def test_new_location_form_validation(
        self, mock_locations, mock_contracts
    ):
        """New location form should require all fields when selected."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            # Select new location
            await pilot.click("#new-location")
            await pilot.pause()

            # Fill event fields
            pilot.app.screen.query_one(
                "#event_name", Input
            ).value = "Rock Concert"
            pilot.app.screen.query_one(
                "#event_start_date", MaskedInput
            ).value = "15/12/2024 (20:00:00)"
            pilot.app.screen.query_one(
                "#event_end_date", MaskedInput
            ).value = "16/12/2024 (02:00:00)"
            pilot.app.screen.query_one(
                "#event_attendees", Input
            ).value = "500"

            # Select contract
            pilot.app.screen.query_one(
                "#event-contract-select", Select
            ).value = mock_contracts[0]

            # Fill only some location fields (missing zip_code and city)
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Nouvelle Salle"
            pilot.app.screen.query_one(
                "#location_street_number", Input
            ).value = "10"
            pilot.app.screen.query_one(
                "#location_street_name", Input
            ).value = "Nouvelle Rue"

            # Missing: location_zip_code and location_city
            await pilot.pause()

            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

            # Now fill missing fields
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "75000"
            pilot.app.screen.query_one(
                "#location_city", Input
            ).value = "Paris"

            await pilot.pause()

            assert create_button.disabled is False

    # =============================================
    # NAVIGATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, mock_locations, mock_contracts
    ):
        """Clicking Cancel should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()
            assert dismissed_result is None

    @pytest.mark.asyncio
    async def test_create_with_existing_location_dismisses_with_data(
        self, mock_locations, mock_contracts
    ):
        """Clicking Create with existing location should dismiss with correct data."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()

            # Fill event form
            pilot.app.screen.query_one(
                "#event_name", Input
            ).value = "Rock Concert"
            pilot.app.screen.query_one(
                "#event_start_date", MaskedInput
            ).value = "15/12/2024 (20:00:00)"
            pilot.app.screen.query_one(
                "#event_end_date", MaskedInput
            ).value = "16/12/2024 (02:00:00)"
            pilot.app.screen.query_one(
                "#event_attendees", Input
            ).value = "500"
            pilot.app.screen.query_one(
                "#event_description", TextArea
            ).text = "Event description test"

            # Select contract
            pilot.app.screen.query_one(
                "#event-contract-select", Select
            ).value = mock_contracts[0]

            # Select existing location
            pilot.app.screen.query_one(
                "#event-location-select", Select
            ).value = mock_locations[0]

            await pilot.pause()

            # Click Create
            await pilot.click("#create")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["event_name"] == "Rock Concert"
            assert (
                dismissed_result["event_start_date"]
                == "15/12/2024 (20:00:00)"
            )
            assert (
                dismissed_result["event_end_date"]
                == "16/12/2024 (02:00:00)"
            )
            assert dismissed_result["event_attendees"] == "500"
            assert (
                dismissed_result["event_description"]
                == "Event description test"
            )
            assert dismissed_result["event_contract"] == mock_contracts[0]
            assert dismissed_result["event_location"] == mock_locations[0]

    @pytest.mark.asyncio
    async def test_create_with_new_location_dismisses_with_dict(
        self, mock_locations, mock_contracts
    ):
        """Clicking Create with new location should include location dict in result."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()

            # Select new location
            await pilot.click("#new-location")
            await pilot.pause()

            # Fill location form
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Nouvelle Salle"
            pilot.app.screen.query_one(
                "#location_street_number", Input
            ).value = "10"
            pilot.app.screen.query_one(
                "#location_street_name", Input
            ).value = "Nouvelle Rue"
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "75000"
            pilot.app.screen.query_one(
                "#location_city", Input
            ).value = "Paris"

            # Fill event form
            pilot.app.screen.query_one(
                "#event_name", Input
            ).value = "Rock Concert"
            pilot.app.screen.query_one(
                "#event_start_date", MaskedInput
            ).value = "15/12/2024 (20:00:00)"
            pilot.app.screen.query_one(
                "#event_end_date", MaskedInput
            ).value = "16/12/2024 (02:00:00)"
            pilot.app.screen.query_one(
                "#event_attendees", Input
            ).value = "500"
            pilot.app.screen.query_one(
                "#event_description", TextArea
            ).text = "Event description test"

            # Select contract
            pilot.app.screen.query_one(
                "#event-contract-select", Select
            ).value = mock_contracts[0]

            await pilot.pause()

            # Click Create
            await pilot.click("#create")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["event_name"] == "Rock Concert"
            assert (
                dismissed_result["event_start_date"]
                == "15/12/2024 (20:00:00)"
            )
            assert (
                dismissed_result["event_end_date"]
                == "16/12/2024 (02:00:00)"
            )
            assert dismissed_result["event_attendees"] == "500"
            assert (
                dismissed_result["event_description"]
                == "Event description test"
            )

            # Verify location is a dict, not a Location object
            assert isinstance(dismissed_result["event_location"], dict)
            assert (
                dismissed_result["event_location"]["name"]
                == "Nouvelle Salle"
            )
            assert (
                dismissed_result["event_location"]["street_number"] == "10"
            )
            assert (
                dismissed_result["event_location"]["street_name"]
                == "Nouvelle Rue"
            )
            assert (
                dismissed_result["event_location"]["zip_code"] == "75000"
            )
            assert dismissed_result["event_location"]["city"] == "Paris"

            assert dismissed_result["event_contract"] == mock_contracts[0]

    # =============================================
    # ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_border_titles(
        self, mock_locations, mock_contracts
    ):
        """on_mount should set all container border titles."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            event_data_container = pilot.app.screen.query_one(
                "#event-data", Container
            )
            event_contract_container = pilot.app.screen.query_one(
                "#event-contract", Container
            )
            event_location_container = pilot.app.screen.query_one(
                "#event-location", Container
            )

            assert event_data_container.border_title == "Event Data"
            assert (
                event_contract_container.border_title
                == "Contract Selection"
            )
            assert (
                event_location_container.border_title
                == "Location Selection"
            )

    @pytest.mark.asyncio
    async def test_on_mount_hides_new_location_form(
        self, mock_locations, mock_contracts
    ):
        """on_mount should hide new location form by default."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(
                CreateEventScreen(
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                )
            )
            await pilot.pause()

            form_container = pilot.app.screen.query_one(
                "#event-location-form-input-container", Container
            )
            assert form_container.display is False


# =============================================================================
# FIXTURE HELPER FOR UpdateEventScreen
# =============================================================================


@pytest.fixture
def event_to_dict():
    """Helper to convert an Event mock to the dict format expected by UpdateEventScreen."""

    def _event_to_dict(event: MagicMock) -> dict:
        return {
            "event_id": event.id,
            "event_name": event.name,
            "event_start_date": event.start_date,
            "event_end_date": event.end_date,
            "event_attendees": str(event.attendees),
            "event_description": event.description,
            "event_contract": event.contract,
            "event_location": event.location,
            "event_support_representative": event.support_representative,
        }

    return _event_to_dict


# =============================================================================
# UPDATE EVENT SCREEN TESTS
# =============================================================================


class TestUpdateEventScreen:
    """Tests for UpdateEventScreen UI, form behavior, and navigation."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """__init__ should store event_data, locations, contracts, and support_representatives."""
        event_data = event_to_dict(mock_complete_event_1)
        screen = UpdateEventScreen(
            event_data=event_data,
            locations=mock_locations,
            signed_contracts=mock_contracts,
            support_representatives=[mock_support_collaborator],
        )
        assert screen.SUB_TITLE == "UPDATE EVENT"
        assert screen.CSS_PATH == "../styles/update_event_screen.tcss"
        assert screen.event_data == event_data
        assert screen.locations == mock_locations
        assert screen.signed_contracts == mock_contracts
        assert screen.support_representatives == [
            mock_support_collaborator
        ]

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Header should exist with correct title and sub-title."""
        app = EpicEventsCRM()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "UPDATE EVENT"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_main_containers_exist(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """All main containers should exist with correct IDs."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            for container_id in [
                "#update-event-data",
                "#update-event-location",
                "#update-event-contract",
                "#update-event-support-representative",
                "#update-event-buttons-container",
            ]:
                container = pilot.app.screen.query_one(
                    container_id, Container
                )
                assert container is not None

    @pytest.mark.asyncio
    async def test_all_event_input_fields_exist(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """All event-related input fields should exist."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#event_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#event_attendees", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one(
                    "#event_start_date", MaskedInput
                )
                is not None
            )
            assert (
                pilot.app.screen.query_one("#event_end_date", MaskedInput)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#event_description", TextArea)
                is not None
            )

    @pytest.mark.asyncio
    async def test_update_and_cancel_buttons_exist(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Update and Cancel buttons should exist with correct IDs."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#update", Button) is not None
            )
            assert (
                pilot.app.screen.query_one("#cancel", Button) is not None
            )

    @pytest.mark.asyncio
    async def test_update_button_enabled_initially_with_supp_rep(
        self,
        mock_complete_event_2,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Update button should be enabled initially (form is pre-filled with valid data)."""
        app = App()
        event_data = event_to_dict(mock_complete_event_2)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

    @pytest.mark.asyncio
    async def test_update_button_disabled_initially_without_supp_rep(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Update button should be disabled initially (form is pre-filled but lacking supp rep)."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is True

    @pytest.mark.asyncio
    async def test_location_select_exists(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Select for existing location should exist."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            location_select = pilot.app.screen.query_one(
                "#update-event-location-select", Select
            )
            assert location_select is not None
            assert len(location_select._options) == len(mock_locations) + 1

    @pytest.mark.asyncio
    async def test_contract_select_exists(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Select for contract should exist."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()
            contract_select = pilot.app.screen.query_one(
                "#update-event-contract-select", Select
            )
            assert contract_select is not None
            assert len(contract_select._options) == len(mock_contracts) + 1

    # =============================================
    # 3. FORM BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_pre_fills_event_data(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Form fields should be pre-filled with event data from event_data dict."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()

            event_name_input = pilot.app.screen.query_one(
                "#event_name", Input
            )
            assert event_name_input.value == "Test Event"

            attendees_input = pilot.app.screen.query_one(
                "#event_attendees", Input
            )
            assert attendees_input.value == "100"

            description_textarea = pilot.app.screen.query_one(
                "#event_description", TextArea
            )
            assert description_textarea.text == "Test description"

    @pytest.mark.asyncio
    async def test_pre_fills_contract_and_location(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Contract and location should be pre-selected based on event_data."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()

            contract_select = pilot.app.screen.query_one(
                "#update-event-contract-select", Select
            )
            assert contract_select.value == mock_complete_event_1.contract

            location_select = pilot.app.screen.query_one(
                "#update-event-location-select", Select
            )
            assert location_select.value == mock_complete_event_1.location

    # =============================================
    # 4. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_empty_required_field_disables_update(
        self,
        mock_complete_event_2,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Clearing a required field should disable Update button."""
        app = App()
        event_data = event_to_dict(mock_complete_event_2)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()

            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

            # Deleting a required field
            pilot.app.screen.query_one("#event_name", Input).value = ""
            await pilot.pause()

            assert update_button.disabled is True

    @pytest.mark.asyncio
    async def test_valid_form_keeps_update_enabled(
        self,
        mock_complete_event_2,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Form with all valid fields should keep Update button enabled."""
        app = App()
        event_data = event_to_dict(mock_complete_event_2)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()

            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

    # =============================================
    # 5. NAVIGATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Clicking Cancel should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()

        assert dismissed_result is None

    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_modified_data(
        self,
        mock_complete_event_2,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Clicking Update should dismiss with modified event data including event_id."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        event_data = event_to_dict(mock_complete_event_2)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()

            # Update event name
            pilot.app.screen.query_one(
                "#event_name", Input
            ).value = "Modified Test Event"
            await pilot.pause()

            await pilot.click("#update")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["event_name"] == "Modified Test Event"
            assert dismissed_result["event_id"] == 2
            assert (
                dismissed_result["event_contract"]
                == mock_complete_event_2.contract
            )
            assert (
                dismissed_result["event_location"]
                == mock_complete_event_2.location
            )

    @pytest.mark.asyncio
    async def test_update_with_existing_location_dismisses_with_data(
        self,
        mock_complete_event_2,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """Clicking Update with existing location should include Location object."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        event_data = event_to_dict(mock_complete_event_2)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()

            # Change contract
            pilot.app.screen.query_one(
                "#update-event-contract-select", Select
            ).value = mock_contracts[0]
            await pilot.pause()

            await pilot.click("#update")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["event_id"] == 2
            assert dismissed_result["event_contract"] == mock_contracts[0]
            assert dismissed_result["event_location"] == mock_locations[1]

    # =============================================
    # 6. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_border_titles(
        self,
        mock_complete_event_1,
        mock_locations,
        mock_contracts,
        mock_support_collaborator,
        event_to_dict,
    ):
        """on_mount should set all container border titles."""
        app = App()
        event_data = event_to_dict(mock_complete_event_1)
        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateEventScreen(
                    event_data=event_data,
                    locations=mock_locations,
                    signed_contracts=mock_contracts,
                    support_representatives=[mock_support_collaborator],
                )
            )
            await pilot.pause()

            event_data_container = pilot.app.screen.query_one(
                "#update-event-data", Container
            )
            event_contract_container = pilot.app.screen.query_one(
                "#update-event-contract", Container
            )
            event_location_container = pilot.app.screen.query_one(
                "#update-event-location", Container
            )
            event_support_rep_container = pilot.app.screen.query_one(
                "#update-event-support-representative", Container
            )

            assert event_data_container.border_title == "Event Data"
            assert (
                event_contract_container.border_title
                == "Contract Selection"
            )
            assert (
                event_location_container.border_title
                == "Location Selection"
            )
            assert (
                event_support_rep_container.border_title
                == "Support Representative Selection"
            )


# =============================================================================
# CREATE LOCATION SCREEN TESTS
# =============================================================================


class TestCreateLocationScreen:
    """Tests for CreateLocationScreen UI, form behavior, and navigation."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self):
        """__init__ should set class attributes and initialize location_data."""
        screen = CreateLocationScreen()
        assert screen.SUB_TITLE == "CREATE LOCATION"
        assert screen.CSS_PATH == "../styles/create_location_screen.tcss"
        assert screen.location_data == {}

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CREATE LOCATION"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_main_container_exists(self):
        """Main container should exist with correct ID and border title."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#location-data", Container
            )
            assert container is not None
            assert container.border_title == "Location Data"

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(self):
        """All location input fields should exist with correct IDs and types."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()

            # Text inputs
            assert (
                pilot.app.screen.query_one("#location_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_number", Input
                )
                is not None
            )
            assert (
                pilot.app.screen.query_one("#location_street_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#location_city", Input)
                is not None
            )

            # Masked input
            assert (
                pilot.app.screen.query_one(
                    "#location_zip_code", MaskedInput
                )
                is not None
            )

    @pytest.mark.asyncio
    async def test_all_labels_exist(self):
        """All form labels should exist with correct text."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            labels = pilot.app.screen.query(Label)
            label_texts = [label.content for label in labels]
            assert "Name" in label_texts
            assert "Number" in label_texts
            assert "Street" in label_texts
            assert "Zip Code" in label_texts
            assert "City" in label_texts

    @pytest.mark.asyncio
    async def test_action_buttons_exist(self):
        """Create and Cancel buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#create", Button) is not None
            )
            assert (
                pilot.app.screen.query_one("#cancel", Button) is not None
            )

    @pytest.mark.asyncio
    async def test_zip_code_mask_template(self):
        """Zip code MaskedInput should use '99999' template."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            zip_input = pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            )
            assert zip_input is not None
            assert zip_input.template == "99999"

    # =============================================
    # 3. FORM BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_empty_form_keeps_create_disabled(self):
        """Empty form should keep Create button disabled."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    @pytest.mark.asyncio
    async def test_valid_form_enables_create(self):
        """Filling all required fields should enable Create button."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()

            # Fill in all fields with valid data
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Salle des Fêtes"
            pilot.app.screen.query_one(
                "#location_street_number", Input
            ).value = "1"
            pilot.app.screen.query_one(
                "#location_street_name", Input
            ).value = "Place du Village"
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "13000"
            pilot.app.screen.query_one(
                "#location_city", Input
            ).value = "Marseille"
            await pilot.pause()

            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is False

    @pytest.mark.asyncio
    async def test_missing_required_field_disables_create(self):
        """Missing any required field should disable Create button."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()

            # Fill in all fields except street_name
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Salle"
            pilot.app.screen.query_one(
                "#location_street_number", Input
            ).value = "1"
            # street_name is ignored
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "13000"
            pilot.app.screen.query_one(
                "#location_city", Input
            ).value = "Marseille"
            await pilot.pause()

            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    @pytest.mark.asyncio
    async def test_name_length_validation(self):
        """Name field should accept max 99 characters and show error message."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()

            # 99 characters → valid
            valid_name = "A" * 99
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = valid_name
            await pilot.pause()

            # Check error message
            name_input = pilot.app.screen.query_one(
                "#location_name", Input
            )
            assert name_input.border_subtitle == None

            # 100 characters → invalid
            invalid_name = "A" * 100
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = invalid_name
            await pilot.pause()

            # Check error message
            assert name_input.border_subtitle == "Name is too long."

    @pytest.mark.asyncio
    async def test_zip_code_mask_validation(self):
        """Zip code field should accept valid mask input."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()

            # Fill in with valid zip code
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "75000"
            await pilot.pause()
            await pilot.press("tab")
            await pilot.pause()

            # Field input is validated
            zip_input = pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            )
            assert zip_input.border_subtitle is None

    @pytest.mark.asyncio
    async def test_field_validation_messages(self):
        """Invalid fields should show validation error messages."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()

            # Fill in all fields except street_number
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Salle"
            # street_number is left empty
            pilot.app.screen.query_one(
                "#location_street_name", Input
            ).value = "Rue"
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "75000"
            pilot.app.screen.query_one(
                "#location_city", Input
            ).value = "Paris"
            await pilot.pause()

            # Simulate blurred widget to trigger _validate_form
            street_number_input = pilot.app.screen.query_one(
                "#location_street_number", Input
            )
            await pilot.click(street_number_input)  # focus field
            await pilot.click("#location_name")  # blur field
            await pilot.pause()

            # Check error message
            assert (
                street_number_input.border_subtitle
                == "Field cannot be empty."
            )

    # =============================================
    # 4. NAVIGATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(self):
        """Clicking Cancel should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateLocationScreen(),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()

        assert dismissed_result is None

    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_location_data(self):
        """Clicking Create should dismiss with location data dict."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateLocationScreen(),
                callback=capture_dismiss,
            )
            await pilot.pause()

            # Fill in form with valid data
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Nouvelle Salle"
            pilot.app.screen.query_one(
                "#location_street_number", Input
            ).value = "10"
            pilot.app.screen.query_one(
                "#location_street_name", Input
            ).value = "Rue Nouvelle"
            pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            ).value = "75000"
            pilot.app.screen.query_one(
                "#location_city", Input
            ).value = "Paris"
            await pilot.pause()

            await pilot.click("#create")
            await pilot.pause()

            # Check content result
            assert dismissed_result is not None
            assert isinstance(dismissed_result, dict)
            assert dismissed_result["name"] == "Nouvelle Salle"
            assert dismissed_result["street_number"] == "10"
            assert dismissed_result["street_name"] == "Rue Nouvelle"
            assert dismissed_result["zip_code"] == "75000"
            assert dismissed_result["city"] == "Paris"

    # =============================================
    # 5. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_border_title(self):
        """on_mount should set container border title to 'Location Data'."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateLocationScreen())
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#location-data", Container
            )
            assert container is not None
            assert container.border_title == "Location Data"


# =============================================================================
# FIXTURE HELPER FOR UpdateLocationScreen
# =============================================================================


@pytest.fixture
def location_to_dict():
    """Fixture to convert a Location object to a dict for UpdateLocationScreen."""

    def _location_to_dict(location: Location) -> dict[str, str | int]:
        return {
            "location_id": location.id,
            "location_name": location.name,
            "location_street_number": location.street_number,
            "location_street_name": location.street_name,
            "location_zip_code": location.zip_code,
            "location_city": location.city,
        }

    return _location_to_dict


# =============================================================================
# UPDATE LOCATION SCREEN TESTS
# =============================================================================


class TestUpdateLocationScreen:
    """Tests for UpdateLocationScreen UI, form behavior, and navigation."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, location_to_dict, mock_locations):
        """__init__ should set class attributes and store location_data."""
        location_dict = location_to_dict(mock_locations[0])
        screen = UpdateLocationScreen(location_data=location_dict)

        assert screen.SUB_TITLE == "UPDATE LOCATION"
        assert screen.CSS_PATH == "../styles/update_location_screen.tcss"
        assert screen.location_data == location_dict
        assert screen.updated_location_data == {}

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self, location_to_dict, mock_locations):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "UPDATE LOCATION"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self, location_to_dict, mock_locations):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_static_title_exists(
        self, location_to_dict, mock_locations
    ):
        """Static title should display the location name being updated."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            static_title = pilot.app.screen.query_one(
                "#updating-location-static", Static
            )
            assert static_title is not None
            assert "Updating location: Grand Salle" in static_title.content

    @pytest.mark.asyncio
    async def test_main_container_exists(
        self, location_to_dict, mock_locations
    ):
        """Main container should exist with correct border titles."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#update-location-data", Container
            )
            assert container is not None
            assert container.border_title == "Location Data"
            assert container.border_subtitle == "Edit relevant fields"

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(
        self, location_to_dict, mock_locations
    ):
        """All location input fields should exist with correct IDs and types."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()

            # Text inputs
            assert (
                pilot.app.screen.query_one("#location_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_number", Input
                )
                is not None
            )
            assert (
                pilot.app.screen.query_one("#location_street_name", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#location_city", Input)
                is not None
            )

            # Masked input
            assert (
                pilot.app.screen.query_one(
                    "#location_zip_code", MaskedInput
                )
                is not None
            )

    @pytest.mark.asyncio
    async def test_all_labels_exist(
        self, location_to_dict, mock_locations
    ):
        """All form labels should exist with correct text."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            labels = pilot.app.screen.query(Label)
            label_texts = [label.content for label in labels]
            assert "Name" in label_texts
            assert "Street Number" in label_texts
            assert "Street Name" in label_texts
            assert "Zip Code" in label_texts
            assert "City" in label_texts

    @pytest.mark.asyncio
    async def test_action_buttons_exist(
        self, location_to_dict, mock_locations
    ):
        """Update and Cancel buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#update", Button) is not None
            )
            assert (
                pilot.app.screen.query_one("#cancel", Button) is not None
            )

    @pytest.mark.asyncio
    async def test_zip_code_mask_template(
        self, location_to_dict, mock_locations
    ):
        """Zip code MaskedInput should use '99999' template."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            zip_input = pilot.app.screen.query_one(
                "#location_zip_code", MaskedInput
            )
            assert zip_input is not None
            assert zip_input.template == "99999"

    # =============================================
    # 3. FORM BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_fields_prefilled_with_location_data(
        self, location_to_dict, mock_locations
    ):
        """All fields should be pre-filled with location_data values."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()

            # Check that all fields are prefilled with mock_locations[0]
            assert (
                pilot.app.screen.query_one("#location_name", Input).value
                == "Grand Salle"
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_number", Input
                ).value
                == "123"
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_name", Input
                ).value
                == "Rue de Paris"
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_zip_code", MaskedInput
                ).value
                == "75000"
            )
            assert (
                pilot.app.screen.query_one("#location_city", Input).value
                == "Paris"
            )

    @pytest.mark.asyncio
    async def test_empty_location_data_keeps_update_disabled(self):
        """Empty location_data should keep Update button disabled."""
        empty_location_data = {
            "location_id": 1,
            "location_name": "",
            "location_street_number": "",
            "location_street_name": "",
            "location_zip_code": "",
            "location_city": "",
        }

        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(location_data=empty_location_data)
            )
            await pilot.pause()
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is True

    @pytest.mark.asyncio
    async def test_valid_prefilled_form_enables_update(
        self, location_to_dict, mock_locations
    ):
        """Prefilled valid form should enable Update button."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

    @pytest.mark.asyncio
    async def test_missing_required_field_disables_update(self):
        """Missing any required field should disable Update button."""
        incomplete_location_data = {
            "location_id": 1,
            "location_name": "Salle",
            "location_street_number": "",
            "location_street_name": "Rue",
            "location_zip_code": "75000",
            "location_city": "Paris",
        }

        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=incomplete_location_data
                )
            )
            await pilot.pause()

            # Trigger _validate_form with blurred
            await pilot.click("#location_street_number")
            await pilot.click("#location_name")
            await pilot.pause()

            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is True

    @pytest.mark.asyncio
    async def test_name_length_validation(
        self, location_to_dict, mock_locations
    ):
        """Name field should accept max 99 characters and show error if exceeded."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()

            # Update with invalid name
            pilot.app.screen.query_one("#location_name", Input).value = (
                "A" * 100
            )
            await pilot.click("#location_name")
            await pilot.click("#location_street_number")
            await pilot.pause()

            name_input = pilot.app.screen.query_one(
                "#location_name", Input
            )
            assert name_input.border_subtitle == "Name is too long."

    @pytest.mark.asyncio
    async def test_field_validation_messages(
        self, mock_sales_collaborator
    ):
        """Invalid fields should show validation error messages."""
        incomplete_location_data = {
            "location_id": 1,
            "location_name": "Salle",
            "location_street_number": "",
            "location_street_name": "Rue",
            "location_zip_code": "75000",
            "location_city": "Paris",
        }

        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=incomplete_location_data
                )
            )
            await pilot.pause()

            # Trigger _validate_form with blurred
            street_number_input = pilot.app.screen.query_one(
                "#location_street_number", Input
            )
            await pilot.click(street_number_input)
            await pilot.click("#location_name")
            await pilot.pause()

            assert (
                street_number_input.border_subtitle
                == "Field cannot be empty."
            )

    # =============================================
    # 4. NAVIGATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, location_to_dict, mock_locations
    ):
        """Clicking Cancel should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()

        assert dismissed_result is None

    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_updated_data(
        self, location_to_dict, mock_locations
    ):
        """Clicking Update should dismiss with updated location data dict."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()

            # Update some fields
            pilot.app.screen.query_one(
                "#location_name", Input
            ).value = "Nouvelle Salle"
            pilot.app.screen.query_one(
                "#location_street_number", Input
            ).value = "10"

            # Trigger validation
            await pilot.click("#location_name")
            await pilot.click("#location_street_number")
            await pilot.pause()

            await pilot.click("#update")
            await pilot.pause()

            # Check result content
            assert dismissed_result is not None
            assert isinstance(dismissed_result, dict)
            assert dismissed_result["location_id"] == 1
            assert dismissed_result["location_name"] == "Nouvelle Salle"
            assert dismissed_result["location_street_number"] == "10"
            assert (
                dismissed_result["location_street_name"] == "Rue de Paris"
            )
            assert dismissed_result["location_zip_code"] == "75000"
            assert dismissed_result["location_city"] == "Paris"

    # =============================================
    # 5. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_border_titles(
        self, mock_sales_collaborator, location_to_dict, mock_locations
    ):
        """on_mount should set container border title and subtitle."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[0])
                )
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#update-location-data", Container
            )
            assert container is not None
            assert container.border_title == "Location Data"
            assert container.border_subtitle == "Edit relevant fields"

    @pytest.mark.asyncio
    async def test_on_mount_prefills_all_fields(
        self, mock_sales_collaborator, location_to_dict, mock_locations
    ):
        """on_mount should pre-fill all input fields with location_data from mock_locations[1]."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            # Utilise mock_locations[1] pour varier
            await app.push_screen(
                UpdateLocationScreen(
                    location_data=location_to_dict(mock_locations[1])
                )
            )
            await pilot.pause()

            # Vérifier que tous les champs sont pré-remplis avec mock_locations[1]
            assert (
                pilot.app.screen.query_one("#location_name", Input).value
                == "Petite Salle"
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_number", Input
                ).value
                == "456"
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_street_name", Input
                ).value
                == "Avenue des Champs"
            )
            assert (
                pilot.app.screen.query_one(
                    "#location_zip_code", MaskedInput
                ).value
                == "75001"
            )
            assert (
                pilot.app.screen.query_one("#location_city", Input).value
                == "Lyon"
            )
