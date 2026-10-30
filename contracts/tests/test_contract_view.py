"""
Tests for contract_view.py

UI tests for ContractScreen, CreateContractScreen, and UpdateContractScreen.
Uses run_test() for Textual UI tests, verifies widget structure,
handlers, and form behavior.

Run with: pytest contracts/tests/test_contract_view.py -v
"""

from unittest.mock import MagicMock

import pytest
from textual.app import App
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    ProgressBar,
    Select,
    Static,
)

from app.epic_events import EpicEventsCRM
from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
)
from contracts.contract_model import Contract, ContractStatus
from contracts.contract_view import (
    ContractScreen,
    CreateContractScreen,
    UpdateContractScreen,
)
from customers.customer_model import Customer
from events.event_model import Event
from services.date_services import format_utc_datetime

# =============================================================================
# COLLABORATOR FIXTURES
# =============================================================================


@pytest.fixture
def mock_sales_collaborator_1():
    """First sales collaborator."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 1
    mock_user.first_name = "Sales"
    mock_user.last_name = "Rep1"
    mock_user.department = MagicMock(spec=Department)
    mock_user.department.name = DepartmentName.SALES
    return mock_user


@pytest.fixture
def mock_sales_collaborator_2():
    """Second sales collaborator."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 2
    mock_user.first_name = "Sales"
    mock_user.last_name = "Rep2"
    mock_user.department = MagicMock(spec=Department)
    mock_user.department.name = DepartmentName.SALES
    return mock_user


@pytest.fixture
def mock_admin_collaborator():
    """Admin collaborator."""
    mock_user = MagicMock(spec=Collaborator)
    mock_user.id = 3
    mock_user.first_name = "Admin"
    mock_user.last_name = "Rep"
    mock_user.department = MagicMock(spec=Department)
    mock_user.department.name = DepartmentName.ADMIN
    return mock_user


@pytest.fixture
def mock_collaborators(
    mock_sales_collaborator_1,
    mock_sales_collaborator_2,
    mock_admin_collaborator,
):
    """Fixture for a list of 3 Collaborator objects (2 sales, 1 admin)."""
    return [
        mock_sales_collaborator_1,
        mock_sales_collaborator_2,
        mock_admin_collaborator,
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
    customer.sales_representative_id = 1
    return customer


@pytest.fixture
def mock_customer_2(mock_sales_collaborator_2):
    """Second customer with sales_representative_2."""
    customer = MagicMock(spec=Customer)
    customer.id = 2
    customer.first_name = "Jane"
    customer.last_name = "Smith"
    customer.sales_representative = mock_sales_collaborator_2
    customer.sales_representative_id = 2
    return customer


@pytest.fixture
def mock_customer_3(mock_sales_collaborator_1):
    """Third customer with sales_representative_1."""
    customer = MagicMock(spec=Customer)
    customer.id = 3
    customer.first_name = "Bob"
    customer.last_name = "Johnson"
    customer.sales_representative = mock_sales_collaborator_1
    customer.sales_representative_id = 1
    return customer


@pytest.fixture
def mock_customers(mock_customer_1, mock_customer_2, mock_customer_3):
    """Fixture for a list of 3 Customer objects."""
    return [mock_customer_1, mock_customer_2, mock_customer_3]


# =============================================================================
# EVENT FIXTURE
# =============================================================================


@pytest.fixture
def mock_event():
    """Fixture for an Event object."""
    event = MagicMock(spec=Event)
    event.id = 1
    event.name = "Annual Concert"
    event.start_date = format_utc_datetime("15/12/2026 (20:00:00)")
    event.end_date = format_utc_datetime("16/12/2026 (02:00:00)")
    event.attendees = 1000
    event.description = "Annual concert event for all customers"
    return event


# =============================================================================
# CONTRACT FIXTURES
# =============================================================================


@pytest.fixture
def mock_pending_contract(mock_customer_1):
    """Pending contract (not signed, amount due > 0)."""
    contract = MagicMock(spec=Contract)
    contract.id = 1
    contract.total_amount = 10000.0
    contract.amount_due = 10000.0
    contract.status = ContractStatus.PENDING
    contract.created_at = format_utc_datetime("10/10/2026 (00:00:00)")
    contract.customer = mock_customer_1
    contract.event = None
    return contract


@pytest.fixture
def mock_signed_contract_with_event(mock_event, mock_customer_2):
    """Signed contract with associated event."""
    contract = MagicMock(spec=Contract)
    contract.id = 2
    contract.total_amount = 20000.0
    contract.amount_due = 0.0
    contract.status = ContractStatus.SIGNED
    contract.created_at = format_utc_datetime("10/09/2026 (00:00:00)")
    contract.customer = mock_customer_2
    contract.event = mock_event
    return contract


@pytest.fixture
def mock_signed_contract_without_event(mock_customer_3):
    """Signed contract without associated event."""
    contract = MagicMock(spec=Contract)
    contract.id = 3
    contract.total_amount = 15000.0
    contract.amount_due = 5000.0
    contract.status = ContractStatus.SIGNED
    contract.created_at = format_utc_datetime("10/08/2026 (00:00:00)")
    contract.customer = mock_customer_3
    contract.event = None
    return contract


@pytest.fixture
def mock_contracts(
    mock_pending_contract,
    mock_signed_contract_with_event,
    mock_signed_contract_without_event,
):
    """Fixture for a list of 3 Contract objects with associated customers.

    - Contract 1: PENDING, customer 1 (sales_rep 1)
    - Contract 2: SIGNED, customer 2 (sales_rep 2), with event
    - Contract 3: SIGNED, customer 3 (sales_rep 1), without event
    """
    return [
        mock_pending_contract,
        mock_signed_contract_with_event,
        mock_signed_contract_without_event,
    ]


# =============================================================================
# HELPER FIXTURES
# =============================================================================


@pytest.fixture
def contract_to_dict():
    """Fixture to convert a Contract object to a dict for UpdateContractScreen.

    Returns:
        dict: {
            "contract_id": int,
            "contract_total_amount": float,
            "contract_amount_due": float,
            "contract_status": ContractStatus,
            "contract_customer": Customer
        }
    """

    def _contract_to_dict(contract: Contract) -> dict:
        return {
            "contract_id": contract.id,
            "contract_total_amount": contract.total_amount,
            "contract_amount_due": contract.amount_due,
            "contract_status": contract.status,
            "contract_customer": contract.customer,
        }

    return _contract_to_dict


# =============================================================================
# CONTRACT SCREEN TESTS
# =============================================================================


class TestContractScreen:
    """Tests for ContractScreen UI, tables, and navigation."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, mock_contracts, mock_admin_collaborator):
        """__init__ should store all parameters."""
        screen = ContractScreen(
            contracts=mock_contracts,
            user=mock_admin_collaborator,
            contract_id=2,
            filtered_table_signature=True,
            filtered_table_payment=False,
        )
        assert screen.SUB_TITLE == "CONTRACTS"
        assert screen.CSS_PATH == "../styles/contract_screen.tcss"
        assert screen.contracts == mock_contracts
        assert screen.current_user == mock_admin_collaborator
        assert screen.pre_selected_contract_id == 2
        assert screen.filtered_table_signature is True
        assert screen.filtered_table_payment is False

    def test_default_initialization(
        self, mock_contracts, mock_admin_collaborator
    ):
        """__init__ should set default values for optional parameters."""
        screen = ContractScreen(
            contracts=mock_contracts, user=mock_admin_collaborator
        )
        assert screen.SUB_TITLE == "CONTRACTS"
        assert screen.CSS_PATH == "../styles/contract_screen.tcss"
        assert screen.contracts == mock_contracts
        assert screen.pre_selected_contract_id is None
        assert screen.filtered_table_signature is False
        assert screen.filtered_table_payment is False
        assert screen.selected_event_id is None
        assert screen.selected_customer_id is None

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CONTRACTS"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_data_tables_exist(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """All DataTables should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            for table_id in [
                "#contracts-table",
                "#contract-customer-table",
                "#contract-event-table",
            ]:
                table = pilot.app.screen.query_one(table_id, DataTable)
                assert table is not None

    @pytest.mark.asyncio
    async def test_progressbar_exists(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """ProgressBar should exist with correct ID."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            progressbar = pilot.app.screen.query_one(
                "#contract-payment-progressbar", ProgressBar
            )
            assert progressbar is not None

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """All action buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            for button_id in [
                "#create-contract",
                "#update-contract",
                "#create-event",
                "#consult-customer",
                "#consult-event",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    @pytest.mark.asyncio
    async def test_contracts_table_has_correct_columns(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Contracts DataTable should have all required columns."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            assert table is not None
            assert table.border_title == "Contracts"
            assert table.get_column("contract_id") is not None
            assert table.get_column("sales_representative") is not None
            assert table.get_column("total_amount") is not None
            assert table.get_column("amount_due") is not None
            assert table.get_column("status") is not None
            assert table.get_column("created_at") is not None

    # =============================================
    # 3. DATA TABLES BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_contracts_table_loaded_with_data(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Contracts table should be loaded with all contracts."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            assert table.row_count == 3

    @pytest.mark.asyncio
    async def test_customer_table_loaded_when_contract_selected(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Customer table should be loaded when a contract is selected."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            # Select second contract
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))  # Second line
            await pilot.pause()

            # Get contract's customer
            selected_contract = mock_contracts[1]  # second contract
            expected_customer = selected_contract.customer

            # Check customer table is loaded
            customer_table = pilot.app.screen.query_one(
                "#contract-customer-table", DataTable
            )
            assert customer_table.row_count == 1

            # Get customer table data
            customer_id = customer_table.get_cell_at(Coordinate(0, 0))
            customer_first_name = customer_table.get_cell_at(
                Coordinate(0, 1)
            )
            customer_last_name = customer_table.get_cell_at(
                Coordinate(0, 2)
            )

            # Check content
            assert customer_id == expected_customer.id
            assert customer_first_name == expected_customer.first_name
            assert customer_last_name == expected_customer.last_name

    @pytest.mark.asyncio
    async def test_event_table_loaded_when_contract_selected(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Event table should be loaded when a contract with event is selected."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            # Select SIGNED contract with event (contract_id=2)
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            # Check event table is loaded
            event_table = pilot.app.screen.query_one(
                "#contract-event-table", DataTable
            )
            assert event_table.row_count == 1

            # Select SIGNED contract without event (contract_id=3)
            await pilot.click(widget=table, offset=(1, 4))
            await pilot.pause()
            assert event_table.row_count == 0

    @pytest.mark.asyncio
    async def test_progressbar_updated_when_contract_selected(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """ProgressBar should be updated with correct values when contract is selected."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            progressbar = pilot.app.screen.query_one(
                "#contract-payment-progressbar", ProgressBar
            )

            # Select first contract (PENDING: total=10000, due=10000, paid=0)
            await pilot.click(widget=table, offset=(1, 2))
            await pilot.pause()
            assert progressbar.total == 10000.0
            assert progressbar.progress == 0.0

            # Select second contract (SIGNED: total=20000, due=0, paid=20000)
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()
            assert progressbar.total == 20000.0
            assert progressbar.progress == 20000.0

            # Select third contract (SIGNED: total=15000, due=5000, paid=10000)
            await pilot.click(widget=table, offset=(1, 4))
            await pilot.pause()
            assert progressbar.total == 15000.0
            assert progressbar.progress == 10000.0

    # =============================================
    # 4. ACTIONS AND NAVIGATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_filter_unsigned_contracts_action(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Pressing 's' should dismiss with ('filter_unsigned_contracts', True)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            assert dismissed_result == ("filter_unsigned_contracts", True)

    @pytest.mark.asyncio
    async def test_filter_unpaid_contracts_action(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Pressing 'p' should dismiss with ('filter_unpaid_contracts', True)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("p")
            await pilot.pause()
            assert dismissed_result == ("filter_unpaid_contracts", True)

    @pytest.mark.asyncio
    async def test_filter_reset_action(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Pressing 'r' should dismiss with ('filter_reset', False)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                    filtered_table_signature=True,
                    filtered_table_payment=True,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert dismissed_result == ("filter_reset", False)

    @pytest.mark.asyncio
    async def test_back_action(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Pressing 'b' should dismiss with 'back'."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.press("b")
            await pilot.pause()
            assert dismissed_result == "back"

    @pytest.mark.asyncio
    async def test_create_contract_button_dismisses(
        self, mock_contracts, mock_admin_collaborator
    ):
        """Clicking 'Create Contract' should dismiss with 'create_contract'."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts, user=mock_admin_collaborator
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#create-contract")
            await pilot.pause()
            assert dismissed_result == "create_contract"

    @pytest.mark.asyncio
    async def test_update_contract_button_dismisses_with_id(
        self, mock_contracts, mock_sales_collaborator_2
    ):
        """Clicking 'Update Contract' should dismiss with ('update_contract', selected_id)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = ContractScreen(
                contracts=mock_contracts, user=mock_sales_collaborator_2
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select second contract
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            await pilot.click("#update-contract")
            await pilot.pause()
            assert dismissed_result == ("update_contract", 2)

    @pytest.mark.asyncio
    async def test_create_event_button_dismisses_with_id(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Clicking 'Create Event' should dismiss with ('create_event', selected_id)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = ContractScreen(
                contracts=mock_contracts, user=mock_sales_collaborator_1
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select third contract SIGNED without event (id=3)
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 4))
            await pilot.pause()

            await pilot.click("#create-event")
            await pilot.pause()
            assert dismissed_result == ("create_event", 3)

    @pytest.mark.asyncio
    async def test_consult_customer_button_dismisses_with_id(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Clicking 'Consult Customer' should dismiss with ('consult_customer', customer_id)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = ContractScreen(
                contracts=mock_contracts, user=mock_sales_collaborator_1
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select third contract (customer_id=3)
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 4))
            await pilot.pause()

            await pilot.click("#consult-customer")
            await pilot.pause()
            assert dismissed_result == ("consult_customer", 3)

    @pytest.mark.asyncio
    async def test_consult_event_button_dismisses_with_id(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Clicking 'Consult Event' should dismiss with ('consult_event', event_id)."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = ContractScreen(
                contracts=mock_contracts, user=mock_sales_collaborator_1
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Select second contract with event (id=2, event_id=1)
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            await pilot.click("#consult-event")
            await pilot.pause()
            assert dismissed_result == ("consult_event", 1)

    # =============================================
    # 5. SELECTION AND LOADING TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_contract_id(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Highlighting a row should update selected_contract_id."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            screen = ContractScreen(
                contracts=mock_contracts, user=mock_sales_collaborator_1
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Select second contract (id=2)
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()
            assert screen.selected_contract_id == 2

    @pytest.mark.asyncio
    async def test_pre_selected_contract_id_sets_cursor(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Pre-selected contract_id should set cursor to correct row."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                    contract_id=3,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            # Contract with id=3 is on third line which is index 2
            assert table.cursor_row == 2

    @pytest.mark.asyncio
    async def test_watch_selected_contract_id_loads_data(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """Watcher should load associated data when selected_contract_id changes."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            screen = ContractScreen(
                contracts=mock_contracts, user=mock_sales_collaborator_1
            )
            await app.push_screen(screen)
            await pilot.pause()

            # Select second contract (id=2, customer_id=2, event_id=1)
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            assert screen.selected_contract_id == 2
            assert screen.selected_customer_id == 2
            assert screen.selected_event_id == 1

    # =============================================
    # 6. PERMISSIONS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_consult_customer_buttons_displayed(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """All consult customer button should be displayed regardless of permissions and contract."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            button = pilot.app.screen.query_one(
                "#consult-customer", Button
            )
            assert button.display == True

    @pytest.mark.asyncio
    async def test_consult_event_buttons_displayed(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """All consult event button should be displayed regardless of permissions."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            button = pilot.app.screen.query_one("#consult-event", Button)
            assert button.display == False

            # Select second contract SIGNED with event
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            assert button.display == True

    @pytest.mark.asyncio
    async def test_action_buttons_displayed_with_admin_user(
        self, mock_contracts, mock_admin_collaborator
    ):
        """All action buttons should be displayed with admin user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts, user=mock_admin_collaborator
                )
            )
            await pilot.pause()

            # Select second contract SIGNED with event
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            for button_id in [
                "#create-contract",
                "#update-contract",
                "#consult-customer",
                "#consult-event",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button.display == True

    @pytest.mark.asyncio
    async def test_create_event_button_not_displayed_with_admin_user(
        self, mock_contracts, mock_admin_collaborator
    ):
        """All action buttons should be displayed with admin user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts, user=mock_admin_collaborator
                )
            )
            await pilot.pause()

            button = pilot.app.screen.query_one("#create-event", Button)
            assert button is not None
            assert button.display == False

            # Select third contract SIGNED with no event
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 4))
            await pilot.pause()

            assert button.display == False

    @pytest.mark.asyncio
    async def test_create_event_button_displayed_with_sales_user(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """All action buttons should be displayed with admin user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            button = pilot.app.screen.query_one("#create-event", Button)
            assert button is not None
            assert button.display == False

            # Select third contract SIGNED with no event
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 4))
            await pilot.pause()

            assert button.display == True

    @pytest.mark.asyncio
    async def test_update_button_not_displayed_with_unowned_contract(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """All consult buttons should be displayed regardless of permissions."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            button = pilot.app.screen.query_one("#update-contract", Button)
            assert button is not None
            assert button.display == True

            # Select second contract associated to sales_collab_2
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            assert button.display == False

    @pytest.mark.asyncio
    async def test_update_button_displayed_with_owned_contract(
        self, mock_contracts, mock_sales_collaborator_2
    ):
        """All consult buttons should be displayed regardless of permissions."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_2,
                )
            )
            await pilot.pause()

            button = pilot.app.screen.query_one("#update-contract", Button)
            assert button is not None
            assert button.display == False

            # Select second contract associated to sales_collab_2
            table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            await pilot.click(widget=table, offset=(1, 3))
            await pilot.pause()

            assert button.display == True

    # =============================================
    # 7. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_builds_all_tables(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """on_mount should build all tables with correct titles."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()

            contracts_table = pilot.app.screen.query_one(
                "#contracts-table", DataTable
            )
            assert contracts_table.border_title == "Contracts"

            customer_table = pilot.app.screen.query_one(
                "#contract-customer-table", DataTable
            )
            assert customer_table.border_title == "Associated Customer"

            event_table = pilot.app.screen.query_one(
                "#contract-event-table", DataTable
            )
            assert event_table.border_title == "Associated Event"

    @pytest.mark.asyncio
    async def test_on_mount_sets_progressbar_title(
        self, mock_contracts, mock_sales_collaborator_1
    ):
        """on_mount should set progressbar border title."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                ContractScreen(
                    contracts=mock_contracts,
                    user=mock_sales_collaborator_1,
                )
            )
            await pilot.pause()
            progressbar = pilot.app.screen.query_one(
                "#contract-payment-progressbar", ProgressBar
            )
            assert progressbar.border_title == "Amount Paid - %"


# =============================================================================
# CREATE CONTRACT SCREEN TESTS
# =============================================================================


class TestCreateContractScreen:
    """Tests for CreateContractScreen UI, form validation, and submission."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, mock_customers):
        """__init__ should store all parameters."""
        screen = CreateContractScreen(customers=mock_customers)
        assert screen.SUB_TITLE == "CREATE CONTRACT"
        assert screen.CSS_PATH == "../styles/create_contract_screen.tcss"
        assert screen.customers == mock_customers
        assert screen.contract_data == {}

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self, mock_customers):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CREATE CONTRACT"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self, mock_customers):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_main_containers_exist(self, mock_customers):
        """Main containers should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            main_container = pilot.app.screen.query_one(
                "#create-contract-main-container", Container
            )
            assert main_container is not None

    @pytest.mark.asyncio
    async def test_form_containers_exist(self, mock_customers):
        """Form containers should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            for container_id in ["#contract-data", "#contract-customer"]:
                container = pilot.app.screen.query_one(
                    container_id, Container
                )
                assert container is not None

    @pytest.mark.asyncio
    async def test_input_fields_exist(self, mock_customers):
        """All input fields should exist with correct IDs and types."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            for input_id, expected_type in [
                ("#contract_total_amount", "number"),
                ("#contract_amount_due", "number"),
            ]:
                input_widget = pilot.app.screen.query_one(input_id, Input)
                assert input_widget is not None
                assert input_widget.type == expected_type

    @pytest.mark.asyncio
    async def test_customer_select_exists(self, mock_customers):
        """Customer select should exist with correct ID and prompt."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#contract-customer-select", Select
            )
            assert select is not None
            assert select.prompt == "Select a customer"

    @pytest.mark.asyncio
    async def test_all_buttons_exist(self, mock_customers):
        """All buttons should exist with correct IDs and variants."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            for button_id, expected_variant in [
                ("#create", "primary"),
                ("#cancel", "default"),
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None
                assert button.variant == expected_variant

    @pytest.mark.asyncio
    async def test_buttons_container_exists(self, mock_customers):
        """Buttons container should exist with correct class."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                "#create-contract-buttons-container", Container
            )
            assert container is not None

    # =============================================
    # 3. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self, mock_customers):
        """Form should be invalid and Create button disabled when all fields are empty."""
        app = App()
        async with app.run_test(size=(120, 50)) as pilot:
            screen = CreateContractScreen(customers=mock_customers)
            await app.push_screen(screen)
            await pilot.pause()
            assert screen.is_form_valid is False
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    @pytest.mark.asyncio
    async def test_total_amount_validation_negative(self, mock_customers):
        """Total amount should reject negative values."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "-100"
            await pilot.pause()
            result = total_amount_input.validate("-100")
            assert result.is_valid is False
            assert (
                "Value cannot be negative." in result.failure_descriptions
            )

    @pytest.mark.asyncio
    async def test_total_amount_validation_empty(self, mock_customers):
        """Total amount should reject empty values."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = ""
            await pilot.pause()
            result = total_amount_input.validate("")
            assert result.is_valid is False
            assert "Field cannot be empty." in result.failure_descriptions

    @pytest.mark.asyncio
    async def test_total_amount_validation_valid(self, mock_customers):
        """Total amount should accept valid positive values."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "1500"
            await pilot.pause()
            result = total_amount_input.validate("1500")
            assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_amount_due_validation_negative(self, mock_customers):
        """Amount due should reject negative values."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            amount_due_input.value = "-500"
            await pilot.pause()
            result = amount_due_input.validate("-500")
            assert result.is_valid is False
            assert (
                "Value cannot be negative." in result.failure_descriptions
            )

    @pytest.mark.asyncio
    async def test_amount_due_validation_empty(self, mock_customers):
        """Amount due should reject empty values."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            amount_due_input.value = ""
            await pilot.pause()
            result = amount_due_input.validate("")
            assert result.is_valid is False
            assert "Field cannot be empty." in result.failure_descriptions

    @pytest.mark.asyncio
    async def test_customer_select_validation_blank(self, mock_customers):
        """Customer select should be invalid when no option is selected."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContractScreen(customers=mock_customers)
            await app.push_screen(screen)
            await pilot.pause()
            customer_select = pilot.app.screen.query_one(
                "#contract-customer-select", Select
            )
            assert customer_select.is_blank() is True
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_with_all_fields(self, mock_customers):
        """Form should be valid when all fields are filled correctly."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContractScreen(customers=mock_customers)
            await app.push_screen(screen)
            await pilot.pause()

            # Fill all fields with valid values
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "2500"
            await pilot.pause()

            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            amount_due_input.value = "1000"
            await pilot.pause()

            customer_select = pilot.app.screen.query_one(
                "#contract-customer-select", Select
            )
            customer_select.value = mock_customers[0]
            await pilot.pause()

            assert screen.is_form_valid is True
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is False

    @pytest.mark.asyncio
    async def test_create_button_disabled_when_form_invalid(
        self, mock_customers
    ):
        """Create button should be disabled when form is invalid."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContractScreen(customers=mock_customers)
            await app.push_screen(screen)
            await pilot.pause()

            # Fill only one field (form still invalid)
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "2500"
            await pilot.pause()

            assert screen.is_form_valid is False
            create_button = pilot.app.screen.query_one("#create", Button)
            assert create_button.disabled is True

    # =============================================
    # 4. SELECT OPTIONS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_customer_select_has_all_customers(self, mock_customers):
        """Customer select should contain all customers as options."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()
            customer_select = pilot.app.screen.query_one(
                "#contract-customer-select", Select
            )

            # Get all option prompts
            option_prompts = [
                option for option in customer_select._options
            ]

            # Check all customers are present
            expected_customers = [
                (
                    f"{mock_customers[0].first_name} {mock_customers[0].last_name}",
                    mock_customers[0],
                ),
                (
                    f"{mock_customers[1].first_name} {mock_customers[1].last_name}",
                    mock_customers[1],
                ),
                (
                    f"{mock_customers[2].first_name} {mock_customers[2].last_name}",
                    mock_customers[2],
                ),
            ]
            for expected in expected_customers:
                assert expected in option_prompts

    # =============================================
    # 5. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_form_data(
        self, mock_customers
    ):
        """Clicking 'Create' should dismiss with form data."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContractScreen(customers=mock_customers)
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Fill form with valid data
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "3000"
            await pilot.pause()

            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            amount_due_input.value = "1500"
            await pilot.pause()

            customer_select = pilot.app.screen.query_one(
                "#contract-customer-select", Select
            )
            customer_select.value = mock_customers[1]  # Jane Smith
            await pilot.pause()

            await pilot.click("#create")
            await pilot.pause()

            assert dismissed_result is not None
            assert dismissed_result["contract_total_amount"] == "3000"
            assert dismissed_result["contract_amount_due"] == "1500"
            assert (
                dismissed_result["contract_customer"] == mock_customers[1]
            )

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(self, mock_customers):
        """Clicking 'Cancel' should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()
            assert dismissed_result is None

    # =============================================
    # 6. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_container_border_titles(
        self, mock_customers
    ):
        """on_mount should set container border titles."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContractScreen(customers=mock_customers)
            )
            await pilot.pause()

            contract_data_container = pilot.app.screen.query_one(
                "#contract-data", Container
            )
            assert contract_data_container.border_title == "Contract Data"

            contract_customer_container = pilot.app.screen.query_one(
                "#contract-customer", Container
            )
            assert (
                contract_customer_container.border_title
                == "Customer Selection"
            )


# =============================================================================
# UPDATE CONTRACT SCREEN TESTS
# =============================================================================


class TestUpdateContractScreen:
    """Tests for UpdateContractScreen UI, form validation, and submission."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """__init__ should store all parameters."""
        contract_data = contract_to_dict(mock_pending_contract)
        screen = UpdateContractScreen(
            contract_data=contract_data, customers=mock_customers
        )
        assert screen.SUB_TITLE == "UPDATE CONTRACT"
        assert screen.CSS_PATH == "../styles/update_contract_screen.tcss"
        assert screen.contract_data == contract_data
        assert screen.customers == mock_customers
        assert screen.updated_contract_data == {}

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "UPDATE CONTRACT"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_updating_contract_static_exists(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Updating contract static text should exist and display contract info."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            static = pilot.app.screen.query_one(
                "#updating-contract-static", Static
            )
            assert static is not None
            assert "Updating contract:" in static.content
            assert str(mock_pending_contract.id) in static.content

    @pytest.mark.asyncio
    async def test_form_containers_exist(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Form containers should exist with correct IDs."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            for container_id in [
                "#update-contract-data",
                "#update-contract-customer",
                "#update-contract-status",
            ]:
                container = pilot.app.screen.query_one(
                    container_id, Container
                )
                assert container is not None

    @pytest.mark.asyncio
    async def test_input_fields_exist(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """All input fields should exist with correct IDs and types."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            for input_id, expected_type in [
                ("#contract_total_amount", "number"),
                ("#contract_amount_due", "number"),
            ]:
                input_widget = pilot.app.screen.query_one(input_id, Input)
                assert input_widget is not None
                assert input_widget.type == expected_type

    @pytest.mark.asyncio
    async def test_select_fields_exist(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """All select fields should exist with correct IDs."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            for select_id, expected_prompt in [
                ("#update-contract-customer-select", "Select a customer"),
                ("#update-contract-status-select", "Select a status"),
            ]:
                select = pilot.app.screen.query_one(select_id, Select)
                assert select is not None
                assert select.prompt == expected_prompt

    @pytest.mark.asyncio
    async def test_all_buttons_exist(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """All buttons should exist with correct IDs and variants."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            for button_id, expected_variant in [
                ("#update", "primary"),
                ("#cancel", "default"),
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None
                assert button.variant == expected_variant

    @pytest.mark.asyncio
    async def test_buttons_container_exists(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Buttons container should exist with correct class."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            container = pilot.app.screen.query_one(
                ".update-contract-buttons-container", Container
            )
            assert container is not None

    # =============================================
    # 3. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Form should be invalid and Update button disabled when required fields are empty."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(120, 50)) as pilot:
            screen = UpdateContractScreen(
                contract_data=contract_data, customers=mock_customers
            )
            await app.push_screen(screen)
            await pilot.pause()
            assert screen.is_form_valid is True
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = ""
            await pilot.pause()

            assert screen.is_form_valid is False

            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is True

    @pytest.mark.asyncio
    async def test_total_amount_validation_negative(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Total amount should reject negative values."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "-100"
            await pilot.pause()
            result = total_amount_input.validate("-100")
            assert result.is_valid is False
            assert (
                "Value cannot be negative." in result.failure_descriptions
            )

    @pytest.mark.asyncio
    async def test_amount_due_validation_negative(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Amount due should reject negative values."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            amount_due_input.value = "-500"
            await pilot.pause()
            result = amount_due_input.validate("-500")
            assert result.is_valid is False
            assert (
                "Value cannot be negative." in result.failure_descriptions
            )

    @pytest.mark.asyncio
    async def test_customer_select_validation_blank(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Customer select should be invalid when no option is selected."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateContractScreen(
                contract_data=contract_data, customers=mock_customers
            )
            await app.push_screen(screen)
            await pilot.pause()
            customer_select = pilot.app.screen.query_one(
                "#update-contract-customer-select", Select
            )
            # Reset the selection
            customer_select.clear()
            await pilot.pause()
            assert customer_select.is_blank() is True
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_status_select_validation_blank(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Status select should be invalid when no option is selected."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateContractScreen(
                contract_data=contract_data, customers=mock_customers
            )
            await app.push_screen(screen)
            await pilot.pause()
            status_select = pilot.app.screen.query_one(
                "#update-contract-status-select", Select
            )
            # Reset the selection
            status_select.clear()
            await pilot.pause()
            assert status_select.is_blank() is True
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_with_all_fields(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Form should be valid when all fields are filled correctly."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateContractScreen(
                contract_data=contract_data, customers=mock_customers
            )
            await app.push_screen(screen)
            await pilot.pause()
            assert screen.is_form_valid is True
            update_button = pilot.app.screen.query_one("#update", Button)
            assert update_button.disabled is False

    # =============================================
    # 4. PRE-FILLED FORM TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_inputs_prefilled_with_contract_data(
        self,
        mock_signed_contract_without_event,
        mock_customers,
        contract_to_dict,
    ):
        """Input fields should be prefilled with contract data."""
        app = App()
        contract_data = contract_to_dict(
            mock_signed_contract_without_event
        )
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()

            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            assert total_amount_input.value == str(
                mock_signed_contract_without_event.total_amount
            )

            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            assert amount_due_input.value == str(
                mock_signed_contract_without_event.amount_due
            )

    @pytest.mark.asyncio
    async def test_customer_select_prefilled(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Customer select should be prefilled with contract's customer."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            customer_select = pilot.app.screen.query_one(
                "#update-contract-customer-select", Select
            )
            assert customer_select.value == mock_pending_contract.customer

    @pytest.mark.asyncio
    async def test_status_select_prefilled(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Status select should be prefilled with contract's status."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            status_select = pilot.app.screen.query_one(
                "#update-contract-status-select", Select
            )
            assert status_select.value == mock_pending_contract.status

    @pytest.mark.asyncio
    async def test_status_select_has_all_options(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Status select should contain all ContractStatus options."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            status_select = pilot.app.screen.query_one(
                "#update-contract-status-select", Select
            )
            option_values = [option for option in status_select._options]
            for status in ContractStatus:
                assert (status.name, status) in option_values

    # =============================================
    # 5. SIGNED CONTRACT FIELD DISABLE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_fields_disabled_for_signed_contract(
        self,
        mock_signed_contract_with_event,
        mock_customers,
        contract_to_dict,
    ):
        """Total amount, amount due, and customer select should be disabled for SIGNED contracts."""
        app = App()
        contract_data = contract_to_dict(mock_signed_contract_with_event)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()

            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            assert total_amount_input.disabled is True

            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            assert amount_due_input.disabled is True

            customer_select = pilot.app.screen.query_one(
                "#update-contract-customer-select", Select
            )
            assert customer_select.disabled is True

            # Status select should still be enabled
            status_select = pilot.app.screen.query_one(
                "#update-contract-status-select", Select
            )
            assert status_select.disabled is False

    @pytest.mark.asyncio
    async def test_fields_enabled_for_pending_contract(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """All fields should be enabled for PENDING contracts."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()

            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            assert total_amount_input.disabled is False

            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            assert amount_due_input.disabled is False

            customer_select = pilot.app.screen.query_one(
                "#update-contract-customer-select", Select
            )
            assert customer_select.disabled is False

            status_select = pilot.app.screen.query_one(
                "#update-contract-status-select", Select
            )
            assert status_select.disabled is False

    # =============================================
    # 6. SELECT OPTIONS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_customer_select_has_all_customers(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Customer select should contain all customers as options."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()
            customer_select = pilot.app.screen.query_one(
                "#update-contract-customer-select", Select
            )

            # Get all option prompts
            option_prompts = [
                option for option in customer_select._options
            ]

            # Check all customers are present
            expected_customers = [
                (
                    f"{mock_customers[0].first_name} {mock_customers[0].last_name}",
                    mock_customers[0],
                ),
                (
                    f"{mock_customers[1].first_name} {mock_customers[1].last_name}",
                    mock_customers[1],
                ),
                (
                    f"{mock_customers[2].first_name} {mock_customers[2].last_name}",
                    mock_customers[2],
                ),
            ]
            for expected in expected_customers:
                assert expected in option_prompts

    # =============================================
    # 7. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_updated_data(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Clicking 'Update' should dismiss with updated contract data."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateContractScreen(
                contract_data=contract_data, customers=mock_customers
            )
            await app.push_screen(screen, callback=capture_dismiss)
            await pilot.pause()

            # Modify form values
            total_amount_input = pilot.app.screen.query_one(
                "#contract_total_amount", Input
            )
            total_amount_input.value = "3500"
            await pilot.pause()

            amount_due_input = pilot.app.screen.query_one(
                "#contract_amount_due", Input
            )
            amount_due_input.value = "2000"
            await pilot.pause()

            customer_select = pilot.app.screen.query_one(
                "#update-contract-customer-select", Select
            )
            customer_select.value = mock_customers[2]  # Bob Johnson
            await pilot.pause()

            status_select = pilot.app.screen.query_one(
                "#update-contract-status-select", Select
            )
            status_select.value = ContractStatus.SIGNED
            await pilot.pause()

            await pilot.click("#update")
            await pilot.pause()

            assert dismissed_result is not None
            assert (
                dismissed_result["contract_id"] == mock_pending_contract.id
            )
            assert dismissed_result["contract_total_amount"] == "3500"
            assert dismissed_result["contract_amount_due"] == "2000"
            assert (
                dismissed_result["contract_customer"] == mock_customers[2]
            )
            assert (
                dismissed_result["contract_status"]
                == ContractStatus.SIGNED
            )

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """Clicking 'Cancel' should dismiss with None."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                ),
                callback=capture_dismiss,
            )
            await pilot.pause()
            await pilot.click("#cancel")
            await pilot.pause()
            assert dismissed_result is None

    # =============================================
    # 8. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_container_border_titles(
        self, mock_pending_contract, mock_customers, contract_to_dict
    ):
        """on_mount should set container border titles and subtitles."""
        app = App()
        contract_data = contract_to_dict(mock_pending_contract)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContractScreen(
                    contract_data=contract_data, customers=mock_customers
                )
            )
            await pilot.pause()

            contract_data_container = pilot.app.screen.query_one(
                "#update-contract-data", Container
            )
            assert contract_data_container.border_title == "Contract Data"
            assert (
                contract_data_container.border_subtitle
                == "Edit relevant fields"
            )

            contract_customer_container = pilot.app.screen.query_one(
                "#update-contract-customer", Container
            )
            assert (
                contract_customer_container.border_title
                == "Customer Selection"
            )

            contract_status_container = pilot.app.screen.query_one(
                "#update-contract-status", Container
            )
            assert (
                contract_status_container.border_title
                == "Status Selection"
            )
