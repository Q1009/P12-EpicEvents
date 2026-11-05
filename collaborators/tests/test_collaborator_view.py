"""
Tests for collaborator_view.py

UI tests for CollaboratorScreen, CreateCollaboratorScreen,
UpdateCollaboratorScreen, and DeleteCollaboratorScreen.
Uses run_test() for Textual UI tests, verifies widget structure,
handlers, and form behavior.

Run with: pytest collaborators/tests/test_collaborator_view.py -v
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
    Select,
    Static,
)

from app.epic_events import EpicEventsCRM
from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
)
from collaborators.collaborator_view import (
    CollaboratorScreen,
    CreateCollaboratorScreen,
    DeleteCollaboratorScreen,
    UpdateCollaboratorScreen,
)
from customers.customer_model import Customer
from events.event_model import Event

# =============================================================================
# COLLABORATOR FIXTURES
# =============================================================================


@pytest.fixture
def mock_admin_collaborator(mock_admin_department):
    """Admin collaborator fixture."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 1
    mock_user.first_name = "Admin"
    mock_user.last_name = "User"
    mock_user.email = "admin.user@epicevents.com"
    mock_user.department = mock_admin_department
    mock_user.customers = []
    mock_user.events = []
    return mock_user


@pytest.fixture
def mock_sales_collaborator_1(mock_sales_department):
    """First sales collaborator fixture."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 2
    mock_user.first_name = "Sales"
    mock_user.last_name = "Rep1"
    mock_user.email = "sales.rep1@epicevents.com"
    mock_user.department = mock_sales_department
    mock_user.customers = []
    mock_user.events = []
    return mock_user


@pytest.fixture
def mock_sales_collaborator_2(mock_sales_department):
    """Second sales collaborator fixture."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 3
    mock_user.first_name = "Sales"
    mock_user.last_name = "Rep2"
    mock_user.email = "sales.rep2@epicevents.com"
    mock_user.department = mock_sales_department
    mock_user.customers = []
    mock_user.events = []
    return mock_user


@pytest.fixture
def mock_support_collaborator(mock_support_department):
    """Support collaborator fixture."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 4
    mock_user.first_name = "Support"
    mock_user.last_name = "Rep"
    mock_user.email = "support.rep@epicevents.com"
    mock_user.department = mock_support_department
    mock_user.customers = []
    mock_user.events = []
    return mock_user


@pytest.fixture
def mock_collaborators(
    mock_admin_collaborator,
    mock_sales_collaborator_1,
    mock_sales_collaborator_2,
    mock_support_collaborator,
):
    """Fixture for a list of 4 Collaborator objects."""
    return [
        mock_admin_collaborator,
        mock_sales_collaborator_1,
        mock_sales_collaborator_2,
        mock_support_collaborator,
    ]


# =============================================================================
# DEPARTMENT FIXTURES
# =============================================================================


@pytest.fixture
def mock_admin_department():
    """Mock Department with ADMIN name."""
    department = MagicMock(spec=Department)
    department.id = 1
    department.name = DepartmentName.ADMIN
    return department


@pytest.fixture
def mock_sales_department():
    """Mock Department with SALES name."""
    department = MagicMock(spec=Department)
    department.id = 2
    department.name = DepartmentName.SALES
    return department


@pytest.fixture
def mock_support_department():
    """Mock Department with SUPPORT name."""
    department = MagicMock(spec=Department)
    department.id = 3
    department.name = DepartmentName.SUPPORT
    return department


@pytest.fixture
def mock_departments_list(
    mock_admin_department, mock_sales_department, mock_support_department
):
    """List of all department fixtures."""
    return [
        mock_admin_department,
        mock_sales_department,
        mock_support_department,
    ]


# =============================================================================
# CUSTOMER FIXTURES
# =============================================================================


@pytest.fixture
def mock_customer_1(mock_sales_collaborator_1):
    """First customer with sales_representative_1."""
    customer = MagicMock(spec=Customer)
    customer.id = 1
    customer.first_name = "John"
    customer.last_name = "Doe"
    customer.sales_representative = mock_sales_collaborator_1
    customer.sales_representative_id = 2
    return customer


@pytest.fixture
def mock_customer_2(mock_sales_collaborator_2):
    """Second customer with sales_representative_2."""
    customer = MagicMock(spec=Customer)
    customer.id = 2
    customer.first_name = "Jane"
    customer.last_name = "Smith"
    customer.sales_representative = mock_sales_collaborator_2
    customer.sales_representative_id = 3
    return customer


@pytest.fixture
def mock_customer_3(mock_sales_collaborator_1):
    """Third customer with sales_representative_1."""
    customer = MagicMock(spec=Customer)
    customer.id = 3
    customer.first_name = "Bob"
    customer.last_name = "Johnson"
    customer.sales_representative = mock_sales_collaborator_1
    customer.sales_representative_id = 2
    return customer


# =============================================================================
# EVENT FIXTURES
# =============================================================================


@pytest.fixture
def mock_event_1(mock_support_collaborator):
    """First event with support_representative."""
    event = MagicMock(spec=Event)
    event.id = 1
    event.name = "Annual Concert"
    event.support_representative = mock_support_collaborator
    event.support_representative_id = 4
    return event


@pytest.fixture
def mock_event_2(mock_support_collaborator):
    """Second event with support_representative."""
    event = MagicMock(spec=Event)
    event.id = 2
    event.name = "Tech Conference"
    event.support_representative = mock_support_collaborator
    event.support_representative_id = 4
    return event


# =============================================================================
# HELPER FIXTURES
# =============================================================================


@pytest.fixture
def collaborator_to_dict():
    """Fixture to convert a Collaborator object to a dict for UpdateCollaboratorScreen."""

    def _collaborator_to_dict(collaborator: Collaborator) -> dict:
        return {
            "collaborator_id": collaborator.id,
            "collaborator_first_name": collaborator.first_name,
            "collaborator_last_name": collaborator.last_name,
            "department": collaborator.department,
        }

    return _collaborator_to_dict


# =============================================================================
# COLLABORATOR SCREEN TESTS
# =============================================================================


class TestCollaboratorScreen:
    """Tests for CollaboratorScreen UI, tables, and navigation."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """__init__ should store all parameters."""
        screen = CollaboratorScreen(
            collaborators=mock_collaborators,
            user=mock_admin_collaborator,
        )
        assert screen.SUB_TITLE == "COLLABORATORS"
        assert screen.CSS_PATH == "../styles/collaborator_screen.tcss"
        assert screen.collaborators == mock_collaborators
        assert screen.current_user == mock_admin_collaborator
        assert screen.selected_collaborator_first_name is None
        assert screen.selected_collaborator_last_name is None

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "COLLABORATORS"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Footer should exist with command palette disabled."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_data_tables_exist(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """All DataTables should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()
            for table_id in [
                "#collaborators-table",
                "#collaborator-customers-table",
                "#collaborator-events-table",
            ]:
                table = pilot.app.screen.query_one(table_id, DataTable)
                assert table is not None

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """All action buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()
            for button_id in [
                "#create-collaborator",
                "#update-collaborator",
                "#delete-collaborator",
                "#consult-customer",
                "#consult-event",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. DATA TABLES BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_collaborators_table_has_correct_columns(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Collaborators DataTable should have all required columns."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            assert table is not None
            assert table.border_title == "Collaborators"
            assert table.get_column("collaborator_id") is not None
            assert table.get_column("first_name") is not None
            assert table.get_column("last_name") is not None
            assert table.get_column("email") is not None
            assert table.get_column("department") is not None
            assert table.get_column("nb_customers") is not None
            assert table.get_column("nb_department") is not None

    @pytest.mark.asyncio
    async def test_collaborators_table_loaded_with_data(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Collaborators table should be loaded with all collaborators."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            assert table.row_count == 4

    @pytest.mark.asyncio
    async def test_customers_table_loaded_when_collaborator_selected(
        self,
        mock_collaborators,
        mock_admin_collaborator,
        mock_sales_collaborator_1,
        mock_customer_1,
        mock_customer_3,
    ):
        """Customer table should be loaded when a collaborator with customers is selected."""
        # Add customers to sales_collaborator_1
        mock_sales_collaborator_1.customers = [
            mock_customer_1,
            mock_customer_3,
        ]

        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()

            # Select sales_collaborator_1 (second row, id=2)
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            # Check customer table is loaded
            customer_table = pilot.app.screen.query_one(
                "#collaborator-customers-table", DataTable
            )
            assert customer_table.row_count == 2

    @pytest.mark.asyncio
    async def test_events_table_loaded_when_collaborator_selected(
        self,
        mock_collaborators,
        mock_admin_collaborator,
        mock_support_collaborator,
        mock_event_1,
        mock_event_2,
    ):
        """Event table should be loaded when a collaborator with events is selected."""
        # Add events to support_collaborator
        mock_support_collaborator.events = [mock_event_1, mock_event_2]

        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()

            # Select support_collaborator (fourth row, id=4)
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 5))
            await pilot.pause()

            # Check event table is loaded
            event_table = pilot.app.screen.query_one(
                "#collaborator-events-table", DataTable
            )
            assert event_table.row_count == 2

    # =============================================
    # 4. ACTIONS AND NAVIGATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_back_action(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Pressing 'b' should dismiss with 'back'."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("b")
            await pilot.pause()
            assert dismissed_result == "back"

    @pytest.mark.asyncio
    async def test_create_collaborator_button_dismisses(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Clicking 'Create Collaborator' should dismiss with 'create_collaborator'."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#create-collaborator")
            await pilot.pause()
            assert dismissed_result == "create_collaborator"

    @pytest.mark.asyncio
    async def test_update_collaborator_button_dismisses_with_id(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Clicking 'Update Collaborator' should dismiss with ('update_collaborator', selected_id)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_admin_collaborator,
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select second collaborator
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            await pilot.click("#update-collaborator")
            await pilot.pause()
            assert dismissed_result == ("update_collaborator", 2)

    @pytest.mark.asyncio
    async def test_delete_collaborator_button_opens_modal(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Clicking 'Delete Collaborator' should open DeleteCollaboratorScreen modal."""
        app = App()
        # modal_opened = False

        # class TestApp(App):
        #     async def on_screen_resume(self, screen):
        #         nonlocal modal_opened
        #         if isinstance(screen, DeleteCollaboratorScreen):
        #             modal_opened = True

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()

            # Select second collaborator
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            await pilot.click("#delete-collaborator")
            await pilot.pause()

            # Check that DeleteCollaboratorScreen is on top
            assert len(pilot.app.screen_stack) == 3
            assert isinstance(
                pilot.app.screen_stack[-1], DeleteCollaboratorScreen
            )

    @pytest.mark.asyncio
    async def test_consult_customer_button_dismisses_with_id(
        self,
        mock_collaborators,
        mock_admin_collaborator,
        mock_sales_collaborator_1,
        mock_customer_1,
        mock_customer_3,
    ):
        """Clicking 'Consult Customer' should dismiss with ('consult_customer', customer_id)."""
        # Add customers to sales_collaborator_1
        mock_sales_collaborator_1.customers = [
            mock_customer_1,
            mock_customer_3,
        ]

        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_admin_collaborator,
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select sales_collaborator_1 (second row)
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            await pilot.click("#consult-customer")
            await pilot.pause()
            assert dismissed_result == ("consult_customer", 1)

    @pytest.mark.asyncio
    async def test_consult_event_button_dismisses_with_id(
        self,
        mock_collaborators,
        mock_admin_collaborator,
        mock_support_collaborator,
        mock_event_1,
        mock_event_2,
    ):
        """Clicking 'Consult Event' should dismiss with ('consult_event', event_id)."""
        # Add events to support_collaborator
        mock_support_collaborator.events = [mock_event_1, mock_event_2]

        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_admin_collaborator,
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select support_collaborator (fourth row)
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 5))
            await pilot.pause()

            await pilot.click("#consult-event")
            await pilot.pause()
            assert dismissed_result == ("consult_event", 1)

    # =============================================
    # 5. SELECTION AND LOADING TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_collaborator_id(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """Highlighting a row should update selected_collaborator_id."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_admin_collaborator,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Select second collaborator (id=2)
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()
            assert screen.selected_collaborator_id == 2

    @pytest.mark.asyncio
    async def test_watch_selected_collaborator_id_loads_data(
        self,
        mock_collaborators,
        mock_admin_collaborator,
        mock_sales_collaborator_1,
        mock_customer_1,
        mock_customer_3,
    ):
        """Watcher should load associated data when selected_collaborator_id changes."""
        # Add customers to sales_collaborator_1
        mock_sales_collaborator_1.customers = [
            mock_customer_1,
            mock_customer_3,
        ]

        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_admin_collaborator,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Select sales_collaborator_1 (second row, id=2)
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            assert screen.selected_collaborator_id == 2
            assert (
                screen.selected_customer_id == 1
            )  # First customer of collaborator
            assert screen.selected_event_id is None  # No events

    # =============================================
    # 6. PERMISSIONS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_action_buttons_displayed_with_admin_user(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """All action buttons should be displayed with admin user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()

            for button_id in [
                "#create-collaborator",
                "#update-collaborator",
                "#delete-collaborator",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button.display is True

    @pytest.mark.asyncio
    async def test_action_buttons_not_displayed_with_sales_user(
        self, mock_collaborators, mock_sales_collaborator_1
    ):
        """All action buttons should not be displayed with sales/support user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            for button_id in [
                "#create-collaborator",
                "#update-collaborator",
                "#delete-collaborator",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button.display is False

    @pytest.mark.asyncio
    async def test_action_buttons_not_displayed_with_support_user(
        self, mock_collaborators, mock_support_collaborator
    ):
        """All action buttons should not be displayed with sales/support user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_support_collaborator,
                )
            )
            await pilot.pause()

            for button_id in [
                "#create-collaborator",
                "#update-collaborator",
                "#delete-collaborator",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button.display is False

    @pytest.mark.asyncio
    async def test_consult_customer_button_displayed_with_permission(
        self,
        mock_collaborators,
        mock_sales_collaborator_1,
        mock_customer_1,
    ):
        """Consult customer button should be displayed with permission and customer selected."""
        mock_sales_collaborator_1.customers = [mock_customer_1]

        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_sales_collaborator_1,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Select sales_collaborator_1
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            button = pilot.app.screen.query_one(
                "#consult-customer", Button
            )
            assert button.display is True

    @pytest.mark.asyncio
    async def test_consult_event_button_displayed_with_permission(
        self,
        mock_collaborators,
        mock_support_collaborator,
        mock_event_1,
    ):
        """Consult event button should be displayed with permission and event selected."""
        mock_support_collaborator.events = [mock_event_1]

        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            screen = CollaboratorScreen(
                collaborators=mock_collaborators,
                user=mock_support_collaborator,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Select support_collaborator
            table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 5))
            await pilot.pause()

            button = pilot.app.screen.query_one("#consult-event", Button)
            assert button.display is True

    # =============================================
    # 7. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_builds_all_tables(
        self, mock_collaborators, mock_admin_collaborator
    ):
        """on_mount should build all tables with correct titles."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CollaboratorScreen(
                    collaborators=mock_collaborators,
                    user=mock_admin_collaborator,
                )
            )
            await pilot.pause()

            collaborators_table = pilot.app.screen.query_one(
                "#collaborators-table", DataTable
            )
            assert collaborators_table.border_title == "Collaborators"

            customer_table = pilot.app.screen.query_one(
                "#collaborator-customers-table", DataTable
            )
            assert customer_table.border_title == "Assigned Customers"

            event_table = pilot.app.screen.query_one(
                "#collaborator-events-table", DataTable
            )
            assert event_table.border_title == "Assigned Events"


# =============================================================================
# CREATE COLLABORATOR SCREEN TESTS
# =============================================================================


class TestCreateCollaboratorScreen:
    """Tests for CreateCollaboratorScreen UI, form validation, and submission."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, mock_departments_list):
        """__init__ should store all parameters."""
        screen = CreateCollaboratorScreen(
            departments=mock_departments_list
        )
        assert screen.SUB_TITLE == "CREATE COLLABORATOR"
        assert (
            screen.CSS_PATH == "../styles/create_collaborator_screen.tcss"
        )
        assert screen.departments == mock_departments_list
        assert screen.collaborator_data == {}

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self, mock_departments_list):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CREATE COLLABORATOR"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self, mock_departments_list):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_main_containers_exist(self, mock_departments_list):
        """Main containers should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            for container_id in [
                "#collaborator-data",
                "#collaborator-department",
            ]:
                container = pilot.app.screen.query_one(
                    container_id, Container
                )
                assert container is not None

    @pytest.mark.asyncio
    async def test_all_form_inputs_exist(self, mock_departments_list):
        """All form inputs should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            for input_id in [
                "#collaborator_last_name",
                "#collaborator_first_name",
                "#password",
            ]:
                input_widget = pilot.app.screen.query_one(input_id, Input)
                assert input_widget is not None

    @pytest.mark.asyncio
    async def test_department_select_exists(self, mock_departments_list):
        """Department select should exist with correct ID."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#collaborator-department-select", Select
            )
            assert select is not None
            assert (
                len(select._options) == len(mock_departments_list) + 1
            )  # SELECT.Null option

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(self, mock_departments_list):
        """All action buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            for button_id in [
                "#create",
                "#cancel",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. CONTAINER BORDER TITLES TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_data_container_border_title(
        self, mock_departments_list
    ):
        """Personal Data container should have correct border title."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#collaborator-data", Container
            )
            assert container.border_title == "Personal Data"

    @pytest.mark.asyncio
    async def test_department_container_border_title(
        self, mock_departments_list
    ):
        """Department Selection container should have correct border title."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#collaborator-department", Container
            )
            assert container.border_title == "Department Selection"

    # =============================================
    # 4. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_empty_form_is_invalid(self, mock_departments_list):
        """Empty fields should make form invalid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_last_name_validation_empty(self, mock_departments_list):
        """Empty last name should make form invalid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()

            # Get last name input and set empty value
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            last_name_input.value = ""
            await pilot.pause()
            result = last_name_input.validate("")
            assert result.is_valid is False
            assert "Field cannot be empty." in result.failure_descriptions

    @pytest.mark.asyncio
    async def test_first_name_validation_empty(
        self, mock_departments_list
    ):
        """Empty first name should make form invalid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()

            # Get first name input and set empty value
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            first_name_input.value = ""
            await pilot.pause()
            result = first_name_input.validate("")
            assert result.is_valid is False
            assert "Field cannot be empty." in result.failure_descriptions

    @pytest.mark.asyncio
    async def test_password_validation_empty(self, mock_departments_list):
        """Empty first name should make form invalid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()

            # Get password input and set empty value
            password_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            password_input.value = ""
            await pilot.pause()
            result = password_input.validate("")
            assert result.is_valid is False
            assert "Field cannot be empty." in result.failure_descriptions

    @pytest.mark.asyncio
    async def test_all_fields_valid(self, mock_departments_list):
        """All fields filled should make form valid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            screen = CreateCollaboratorScreen(
                departments=mock_departments_list
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Fill all fields
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            password_input = pilot.app.screen.query_one("#password", Input)
            last_name_input.value = "Doe"
            first_name_input.value = "John"
            password_input.value = "password"
            await pilot.pause()

            # Select department
            department_select = pilot.app.screen.query_one(
                "#collaborator-department-select", Select
            )
            assert department_select.is_blank() is True
            department_select.value = mock_departments_list[0]
            await pilot.pause()

            assert screen.is_form_valid is True

    @pytest.mark.asyncio
    async def test_create_button_disabled_when_invalid(
        self, mock_departments_list
    ):
        """Create button should be disabled when form is invalid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    @pytest.mark.asyncio
    async def test_create_button_enabled_when_valid(
        self, mock_departments_list
    ):
        """Create button should be enabled when form is valid."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            screen = CreateCollaboratorScreen(
                departments=mock_departments_list
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Fill all fields
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            password_input = pilot.app.screen.query_one("#password", Input)
            last_name_input.value = "Doe"
            first_name_input.value = "John"
            password_input.value = "password"
            await pilot.pause()

            # Select department
            department_select = pilot.app.screen.query_one(
                "#collaborator-department-select", Select
            )
            department_select.value = mock_departments_list[0]
            await pilot.pause()

            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is False

    # =============================================
    # 5. VALIDATION MESSAGES TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_valid_last_name_clears_error(
        self, mock_departments_list
    ):
        """Valid field should clear error message."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()

            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            last_name_input.value = "Doe"
            await pilot.pause()
            await pilot.press("tab")
            assert last_name_input.border_subtitle is None

    @pytest.mark.asyncio
    async def test_valid_first_name_clears_error(
        self, mock_departments_list
    ):
        """Valid field should clear error message."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()

            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            first_name_input.value = "John"
            await pilot.pause()
            await pilot.press("tab")
            assert first_name_input.border_subtitle is None

    @pytest.mark.asyncio
    async def test_valid_password_clears_error(
        self, mock_departments_list
    ):
        """Valid field should clear error message."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()

            password_input = pilot.app.screen.query_one("#password", Input)
            password_input.value = "password"
            await pilot.pause()
            await pilot.press("tab")
            assert password_input.border_subtitle is None

    # =============================================
    # 6. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_data(
        self, mock_departments_list
    ):
        """Clicking Create should dismiss with form data."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 50)) as pilot:
            screen = CreateCollaboratorScreen(
                departments=mock_departments_list
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Fill all fields
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            password_input = pilot.app.screen.query_one("#password", Input)
            last_name_input.value = "Doe"
            first_name_input.value = "John"
            password_input.value = "password"
            await pilot.pause()

            # Select department
            department_select = pilot.app.screen.query_one(
                "#collaborator-department-select", Select
            )
            department_select.value = mock_departments_list[0]
            await pilot.pause()

            await pilot.click("#create")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["collaborator_last_name"] == "Doe"
            assert dismissed_result["collaborator_first_name"] == "John"
            assert dismissed_result["password"] == "password"
            assert (
                dismissed_result["department"] == mock_departments_list[0]
            )

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, mock_departments_list
    ):
        """Clicking Cancel should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(
                    departments=mock_departments_list
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()
            assert dismissed_result is None

    @pytest.mark.asyncio
    async def test_on_mount_sets_border_titles(
        self, mock_departments_list
    ):
        """on_mount should set border titles for containers."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateCollaboratorScreen(departments=mock_departments_list)
            )
            await pilot.pause()
            data_container = pilot.app.screen.query_one(
                "#collaborator-data", Container
            )
            department_container = pilot.app.screen.query_one(
                "#collaborator-department", Container
            )
            assert data_container.border_title == "Personal Data"
            assert (
                department_container.border_title == "Department Selection"
            )


# =============================================================================
# UPDATE COLLABORATOR SCREEN TESTS
# =============================================================================


class TestUpdateCollaboratorScreen:
    """Tests for UpdateCollaboratorScreen UI, form pre-fill, validation, and submission."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """__init__ should store all parameters."""
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        screen = UpdateCollaboratorScreen(
            collaborator_data=collaborator_data,
            departments=mock_departments_list,
        )
        assert screen.SUB_TITLE == "UPDATE COLLABORATOR"
        assert (
            screen.CSS_PATH == "../styles/update_collaborator_screen.tcss"
        )
        assert screen.collaborator_data == collaborator_data
        assert screen.updated_collaborator_data == {}
        assert screen.departments == mock_departments_list

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "UPDATE COLLABORATOR"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_static_title_exists(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_admin_collaborator,
    ):
        """Static title should exist with collaborator name."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_admin_collaborator)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            static = pilot.app.screen.query_one(
                "#updating-collaborator-static", Static
            )
            assert static is not None
            assert "Updating Collaborator: " in static.content
            assert mock_admin_collaborator.first_name in static.content
            assert mock_admin_collaborator.last_name in static.content

    @pytest.mark.asyncio
    async def test_all_form_inputs_exist(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """All form inputs should exist with correct IDs."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            for input_id in [
                "#collaborator_last_name",
                "#collaborator_first_name",
            ]:
                input_widget = pilot.app.screen.query_one(input_id, Input)
                assert input_widget is not None

    @pytest.mark.asyncio
    async def test_department_select_exists(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Department select should exist with correct ID."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#update-collaborator-department-select", Select
            )
            assert select is not None
            assert len(select._options) == len(mock_departments_list) + 1

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """All action buttons should exist with correct IDs."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            for button_id in [
                "#update",
                "#cancel",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. CONTAINER BORDER TITLES TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_data_container_border_title(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Personal Data container should have correct border title and subtitle."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#update-collaborator-data", Container
            )
            assert container.border_title == "Personal Data"
            assert container.border_subtitle == "Edit relevant fields"

    @pytest.mark.asyncio
    async def test_department_container_border_title(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Department Selection container should have correct border title."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#update-collaborator-department", Container
            )
            assert container.border_title == "Department Selection"

    # =============================================
    # 4. FORM PRE-FILL TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_last_name_pre_filled(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_admin_collaborator,
    ):
        """Last name input should be pre-filled."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_admin_collaborator)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            assert last_name_input.value == "User"

    @pytest.mark.asyncio
    async def test_first_name_pre_filled(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_admin_collaborator,
    ):
        """First name input should be pre-filled."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_admin_collaborator)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            assert first_name_input.value == "Admin"

    @pytest.mark.asyncio
    async def test_department_pre_selected(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_admin_collaborator,
    ):
        """Department should be pre-selected."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_admin_collaborator)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            department_select = pilot.app.screen.query_one(
                "#update-collaborator-department-select", Select
            )
            assert (
                department_select.value
                == mock_admin_collaborator.department
            )

    # =============================================
    # 5. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_empty_last_name_invalid(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Empty last name should make form invalid."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateCollaboratorScreen(
                collaborator_data=collaborator_data,
                departments=mock_departments_list,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Form is valid initially
            assert screen.is_form_valid is True

            # Clear last name
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            last_name_input.value = ""
            await pilot.pause()

            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_empty_first_name_invalid(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Empty first name should make form invalid."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateCollaboratorScreen(
                collaborator_data=collaborator_data,
                departments=mock_departments_list,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Form is valid initially
            assert screen.is_form_valid is True

            # Clear first name
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            first_name_input.value = ""
            await pilot.pause()

            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_empty_department_select_invalid(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Empty department select should make form invalid."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateCollaboratorScreen(
                collaborator_data=collaborator_data,
                departments=mock_departments_list,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Form is valid initially
            assert screen.is_form_valid is True

            # Clear first name
            select = pilot.app.screen.query_one(
                "#update-collaborator-department-select", Select
            )
            select.clear()
            await pilot.pause()

            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_update_button_disabled_when_invalid(
        self,
        mock_sales_collaborator_1,
        mock_departments_list,
        collaborator_to_dict,
    ):
        """Update button should be disabled when form is invalid."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateCollaboratorScreen(
                collaborator_data=collaborator_data,
                departments=mock_departments_list,
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Form is valid initially
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

            # Clear last name to make form invalid
            last_name_input = pilot.app.screen.query_one(
                "#collaborator_last_name", Input
            )
            last_name_input.value = ""
            await pilot.pause()

            assert update_button.disabled is True

    @pytest.mark.asyncio
    async def test_update_button_enabled_when_valid(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_admin_collaborator,
    ):
        """Update button should be enabled when form is valid."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_admin_collaborator)
        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateCollaboratorScreen(
                collaborator_data=collaborator_data,
                departments=mock_departments_list,
            )
            await app.push_screen(screen)
            await pilot.pause()
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

    # =============================================
    # 6. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_data(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_admin_collaborator,
    ):
        """Clicking Update should dismiss with updated form data."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_admin_collaborator)
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateCollaboratorScreen(
                collaborator_data=collaborator_data,
                departments=mock_departments_list,
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Modify first name
            first_name_input = pilot.app.screen.query_one(
                "#collaborator_first_name", Input
            )
            first_name_input.value = "Updated"
            await pilot.pause()

            await pilot.click("#update")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["id"] == 1
            assert dismissed_result["first_name"] == "Updated"
            assert dismissed_result["last_name"] == "User"
            assert (
                dismissed_result["department"]
                == mock_admin_collaborator.department
            )

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_sales_collaborator_1,
    ):
        """Clicking Cancel should dismiss with None."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()
            assert dismissed_result is None

    @pytest.mark.asyncio
    async def test_on_mount_sets_border_titles(
        self,
        mock_departments_list,
        collaborator_to_dict,
        mock_sales_collaborator_1,
    ):
        """on_mount should set border titles for containers."""
        app = App()
        collaborator_data = collaborator_to_dict(mock_sales_collaborator_1)
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                UpdateCollaboratorScreen(
                    collaborator_data=collaborator_data,
                    departments=mock_departments_list,
                )
            )
            await pilot.pause()
            data_container = pilot.app.screen.query_one(
                "#update-collaborator-data", Container
            )
            department_container = pilot.app.screen.query_one(
                "#update-collaborator-department", Container
            )
            assert data_container.border_title == "Personal Data"
            assert data_container.border_subtitle == "Edit relevant fields"
            assert (
                department_container.border_title == "Department Selection"
            )


# =============================================================================
# DELETE COLLABORATOR SCREEN TESTS
# =============================================================================


class TestDeleteCollaboratorScreen:
    """Tests for DeleteCollaboratorScreen modal confirmation."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self):
        """__init__ should store all parameters."""
        screen = DeleteCollaboratorScreen(
            collaborator_id=1,
            collaborator_first_name="John",
            collaborator_last_name="Doe",
        )
        assert screen.collaborator_id == 1
        assert screen.collaborator_first_name == "John"
        assert screen.collaborator_last_name == "Doe"

    def test_initialization_with_none_values(self):
        """__init__ should handle None values."""
        screen = DeleteCollaboratorScreen(
            collaborator_id=None,
            collaborator_first_name=None,
            collaborator_last_name=None,
        )
        assert screen.collaborator_id is None
        assert screen.collaborator_first_name is None
        assert screen.collaborator_last_name is None

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_main_container_exists(self):
        """Main container should exist with correct class."""
        app = App()
        async with app.run_test(size=(60, 20)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                )
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#delete-collaborator-main-container", Container
            )
            assert container is not None

    @pytest.mark.asyncio
    async def test_all_labels_exist(self):
        """All labels should exist with correct ids."""
        app = App()
        async with app.run_test(size=(60, 20)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                )
            )
            await pilot.pause()

            for label_id in [
                "#updating-collaborator-message-start-label",
                "#updating-collaborator-fullname-label",
                "#updating-collaborator-message-end-label",
            ]:
                label = pilot.app.screen.query_one(label_id, Label)
                assert label is not None

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(self):
        """All action buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(60, 20)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                )
            )
            await pilot.pause()
            for button_id in [
                "#delete",
                "#cancel",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. LABEL CONTENT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_first_label_content(self):
        """First label should have correct content."""
        app = App()
        async with app.run_test(size=(60, 20)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                )
            )
            await pilot.pause()
            label = pilot.app.screen.query_one(
                "#updating-collaborator-message-start-label", Label
            )
            assert label.content == "Are you sure you want to delete"

    @pytest.mark.asyncio
    async def test_second_label_content(self):
        """Second label should display collaborator full name."""
        app = App()
        async with app.run_test(size=(60, 20)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                )
            )
            await pilot.pause()
            label = pilot.app.screen.query_one(
                "#updating-collaborator-fullname-label", Label
            )
            assert label.content == "John Doe"

    @pytest.mark.asyncio
    async def test_third_label_content(self):
        """Third label should have correct content."""
        app = App()
        async with app.run_test(size=(60, 20)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                )
            )
            await pilot.pause()
            label = pilot.app.screen.query_one(
                "#updating-collaborator-message-end-label", Label
            )
            assert label.content == "from the system ?"

    # =============================================
    # 4. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_delete_button_dismisses_with_id(self):
        """Clicking Delete should dismiss with collaborator_id."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#delete")
            await pilot.pause()
            assert dismissed_result == 1

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(self):
        """Clicking Cancel should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 50)) as pilot:
            await app.push_screen(
                DeleteCollaboratorScreen(
                    collaborator_id=1,
                    collaborator_first_name="John",
                    collaborator_last_name="Doe",
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()
            assert dismissed_result is None
