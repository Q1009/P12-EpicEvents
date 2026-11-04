"""
Tests for customer_view.py

Unit tests for CustomerView classes covering:
- CustomerScreen: Main screen with customers/contacts/phone numbers tables
- CreateCustomerScreen: Form for creating customers with contact selection
- UpdateCustomerScreen: Form for updating customers with multi-contact selection
- CreateContactScreen: Form for creating contacts with dynamic phone numbers
- UpdateContactScreen: Form for updating contacts with dynamic phone numbers

Tests include:
- Synchronous initialization tests
- Asynchronous UI structure tests
- Data loading and display tests
- Form validation tests
- Navigation and action tests
- Permission tests
- Mount behavior tests

Run with: pytest customers/tests/test_customer_view.py -v
"""

from unittest.mock import MagicMock

import pytest
from textual.app import App
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    RadioButton,
    RadioSet,
    Select,
    SelectionList,
    Static,
)

from app.epic_events import EpicEventsCRM
from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
)
from customers.customer_model import Contact, Customer, PhoneNumber
from customers.customer_view import (
    CreateContactScreen,
    CreateCustomerScreen,
    CustomerScreen,
    UpdateContactScreen,
    UpdateCustomerScreen,
)
from services.date_services import format_utc_datetime

# =============================================================================
# COLLABORATOR FIXTURES
# =============================================================================


@pytest.fixture
def mock_sales_collaborator():
    """Mock Collaborator from SALES department."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 1
    collaborator.first_name = "Sales"
    collaborator.last_name = "Rep1"
    collaborator.department = MagicMock(spec=Department)
    collaborator.department.name = DepartmentName.SALES
    return collaborator


@pytest.fixture
def mock_second_sales_collaborator():
    """Mock second Collaborator from SALES department."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 2
    collaborator.first_name = "Sales"
    collaborator.last_name = "Rep2"
    collaborator.department = MagicMock(spec=Department)
    collaborator.department.name = DepartmentName.SALES
    return collaborator


@pytest.fixture
def mock_admin_collaborator():
    """Mock Collaborator from ADMIN department."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 3
    collaborator.first_name = "Admin"
    collaborator.last_name = "User"
    collaborator.department = MagicMock(spec=Department)
    collaborator.department.name = DepartmentName.ADMIN
    return collaborator


@pytest.fixture
def mock_collaborators(
    mock_sales_collaborator,
    mock_second_sales_collaborator,
    mock_admin_collaborator,
):
    """List of all collaborator fixtures."""
    return [
        mock_sales_collaborator,
        mock_second_sales_collaborator,
        mock_admin_collaborator,
    ]


@pytest.fixture
def mock_sales_representatives(
    mock_sales_collaborator, mock_second_sales_collaborator
):
    """List of all sales representatives."""
    return [mock_sales_collaborator, mock_second_sales_collaborator]


# =============================================================================
# PHONE NUMBER FIXTURES
# =============================================================================


@pytest.fixture
def mock_phone_number():
    """Mock PhoneNumber for first contact."""
    phone = MagicMock(spec=PhoneNumber)
    phone.id = 1
    phone.number = "1234567890"
    phone.contact_id = 1
    return phone


@pytest.fixture
def mock_second_phone_number():
    """Mock PhoneNumber for second contact."""
    phone = MagicMock(spec=PhoneNumber)
    phone.id = 2
    phone.number = "0987654321"
    phone.contact_id = 2
    return phone


@pytest.fixture
def mock_third_phone_number():
    """Mock PhoneNumber for third contact."""
    phone = MagicMock(spec=PhoneNumber)
    phone.id = 3
    phone.number = "5556667777"
    phone.contact_id = 3
    return phone


@pytest.fixture
def mock_fourth_phone_number():
    """Additional Mock PhoneNumber for third contact."""
    phone = MagicMock(spec=PhoneNumber)
    phone.id = 4
    phone.number = "1112223333"
    phone.contact_id = 3
    return phone


# =============================================================================
# CONTACT FIXTURES
# =============================================================================


@pytest.fixture
def mock_contact(mock_phone_number):
    """Mock Contact with one phone number."""
    contact = MagicMock(spec=Contact)
    contact.id = 1
    contact.first_name = "Alice"
    contact.last_name = "Smith"
    contact.email = "alice.smith@example.com"
    contact.phone_numbers = [mock_phone_number]
    return contact


@pytest.fixture
def mock_second_contact(mock_second_phone_number):
    """Mock second Contact with one phone number."""
    contact = MagicMock(spec=Contact)
    contact.id = 2
    contact.first_name = "Bob"
    contact.last_name = "Johnson"
    contact.email = "bob.johnson@example.com"
    contact.phone_numbers = [mock_second_phone_number]
    return contact


@pytest.fixture
def mock_third_contact(mock_third_phone_number, mock_fourth_phone_number):
    """Mock third Contact with two phone numbers."""
    contact = MagicMock(spec=Contact)
    contact.id = 3
    contact.first_name = "Charlie"
    contact.last_name = "Brown"
    contact.email = "charlie.brown@example.com"
    contact.phone_numbers = [
        mock_third_phone_number,
        mock_fourth_phone_number,
    ]
    return contact


@pytest.fixture
def mock_contacts_list(
    mock_contact, mock_second_contact, mock_third_contact
):
    """List of all previously defined contacts."""
    return [mock_contact, mock_second_contact, mock_third_contact]


# =============================================================================
# CUSTOMER FIXTURES
# =============================================================================


@pytest.fixture
def mock_customer(mock_sales_collaborator, mock_contact):
    """Mock Customer with one contact and its sales representative."""
    customer = MagicMock(spec=Customer)
    customer.id = 1
    customer.first_name = "John"
    customer.last_name = "Doe"
    customer.company_name = "Acme Corp"
    customer.sales_representative_id = 1
    customer.sales_representative = mock_sales_collaborator
    customer.contacts = [mock_contact]
    customer.created_at = format_utc_datetime("15/12/2026 (20:00:00)")
    customer.updated_at = format_utc_datetime("15/12/2026 (20:00:00)")
    return customer


@pytest.fixture
def mock_second_customer(
    mock_second_sales_collaborator, mock_second_contact
):
    """Mock second Customer with one contact and its sales representative."""
    customer = MagicMock(spec=Customer)
    customer.id = 2
    customer.first_name = "Jane"
    customer.last_name = "Smith"
    customer.company_name = "Globex Inc"
    customer.sales_representative_id = 2
    customer.sales_representative = mock_second_sales_collaborator
    customer.contacts = [mock_second_contact]
    customer.created_at = format_utc_datetime("15/12/2026 (20:00:00)")
    customer.updated_at = format_utc_datetime("15/12/2026 (20:00:00)")
    return customer


@pytest.fixture
def mock_third_customer(
    mock_second_sales_collaborator, mock_third_contact, mock_contact
):
    """Mock third Customer with two contacts and the second sales representative."""
    customer = MagicMock(spec=Customer)
    customer.id = 3
    customer.first_name = "Jack"
    customer.last_name = "Wilson"
    customer.company_name = "Wayne Enterprises"
    customer.sales_representative_id = 2
    customer.sales_representative = mock_second_sales_collaborator
    customer.contacts = [mock_third_contact, mock_contact]
    customer.created_at = format_utc_datetime("15/12/2026 (20:00:00)")
    customer.updated_at = format_utc_datetime("15/12/2026 (20:00:00)")
    return customer


@pytest.fixture
def mock_customers_list(
    mock_customer, mock_second_customer, mock_third_customer
):
    """List of all previously defined customers."""
    return [mock_customer, mock_second_customer, mock_third_customer]


# =============================================================================
# HELPER FIXTURES
# =============================================================================


@pytest.fixture
def customer_to_dict():
    """Fixture to convert a Customer object to a dict for UpdateCustomerScreen.

    Returns:
        dict: {
            "customer_id": int,
            "customer_first_name": str,
            "customer_last_name": str,
            "company_name": str,
            "customer_contacts": List[Contact],
            "customer_sales_representative": Collaborator
        }
    """

    def _customer_to_dict(customer: Customer) -> dict:
        return {
            "customer_id": customer.id,
            "customer_first_name": customer.first_name,
            "customer_last_name": customer.last_name,
            "company_name": customer.company_name,
            "customer_contacts": customer.contacts,
            "customer_sales_representative": customer.sales_representative,
        }

    return _customer_to_dict


@pytest.fixture
def contact_to_dict():
    """Fixture to convert a Contact object to a dict for UpdateContactScreen.

    Returns:
        dict: {
            "contact_id": int,
            "contact_first_name": str,
            "contact_last_name": str,
            "email": str,
            "phone_numbers": List[str]
        }
    """

    def _contact_to_dict(contact: Contact) -> dict:
        return {
            "contact_id": contact.id,
            "contact_first_name": contact.first_name,
            "contact_last_name": contact.last_name,
            "email": contact.email,
            "phone_numbers": [
                phone.number for phone in contact.phone_numbers
            ],
        }

    return _contact_to_dict


# =============================================================================
# 1. CUSTOMER SCREEN TESTS
# =============================================================================


class TestCustomerScreen:
    """Tests for CustomerScreen."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """__init__ should store all parameters."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=2,
        )
        assert screen.SUB_TITLE == "CUSTOMERS"
        assert screen.CSS_PATH == "../styles/customer_screen.tcss"
        assert screen.customers == mock_customers_list
        assert screen.current_user == mock_sales_collaborator
        assert screen.pre_selected_customer_id == 2

    def test_default_initialization(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """__init__ should set default values for optional parameters."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
        )
        assert screen.SUB_TITLE == "CUSTOMERS"
        assert screen.CSS_PATH == "../styles/customer_screen.tcss"
        assert screen.pre_selected_customer_id is None

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CUSTOMERS"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_customers_table_exists(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Customers DataTable should exist with correct ID."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            assert table is not None

    @pytest.mark.asyncio
    async def test_contacts_table_exists(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Contacts DataTable should exist with correct ID."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customer-contacts-table", DataTable
            )
            assert table is not None

    @pytest.mark.asyncio
    async def test_phone_numbers_table_exists(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Phone numbers DataTable should exist with correct ID."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#contact-phone-numbers-table", DataTable
            )
            assert table is not None

    @pytest.mark.asyncio
    async def test_all_action_buttons_exist(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """All action buttons should exist with correct IDs."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            for button_id in [
                "#create-customer",
                "#update-customer",
                "#create-contact",
                "#update-contact",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    @pytest.mark.asyncio
    async def test_customers_table_has_correct_columns(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Customers DataTable should have all required columns."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            assert table is not None
            assert table.get_column("id") is not None
            assert table.get_column("first_name") is not None
            assert table.get_column("last_name") is not None
            assert table.get_column("company_name") is not None
            assert table.get_column("sales_representative") is not None
            assert table.get_column("created_at") is not None
            assert table.get_column("updated_at") is not None

    @pytest.mark.asyncio
    async def test_contacts_table_has_correct_columns(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Contacts DataTable should have all required columns."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customer-contacts-table", DataTable
            )
            assert table is not None
            assert table.get_column("id") is not None
            assert table.get_column("first_name") is not None
            assert table.get_column("last_name") is not None
            assert table.get_column("email") is not None

    @pytest.mark.asyncio
    async def test_phone_numbers_table_has_correct_columns(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Phone numbers DataTable should have all required columns."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#contact-phone-numbers-table", DataTable
            )
            assert table is not None
            assert table.get_column("id") is not None
            assert table.get_column("number") is not None

    # =============================================
    # 3. DATA TABLES BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_customers_table_loaded_with_data(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Customers table should be loaded with all customers."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            assert table.row_count == 3

    @pytest.mark.asyncio
    async def test_customers_table_content_matches_data(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Customers table content should match customer data."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            assert table.get_cell_at((0, 0)) == 1  # ID
            assert table.get_cell_at((0, 1)) == "John"  # First Name
            assert table.get_cell_at((0, 2)) == "Doe"  # Last Name
            assert table.get_cell_at((0, 3)) == "Acme Corp"  # Company Name

    @pytest.mark.asyncio
    async def test_contacts_table_loaded_when_customer_selected(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Contacts table should load when customer is selected."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            customers_table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            await pilot.click(customers_table)
            await pilot.pause()
            contacts_table = pilot.app.screen.query_one(
                "#customer-contacts-table", DataTable
            )
            assert contacts_table.row_count == 1

    @pytest.mark.asyncio
    async def test_phone_numbers_table_loaded_when_contact_selected(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Phone numbers table should load when contact is selected."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=1,
                )
            )
            await pilot.pause()
            contacts_table = pilot.app.screen.query_one(
                "#customer-contacts-table", DataTable
            )
            await pilot.click(contacts_table)
            await pilot.pause()
            phone_table = pilot.app.screen.query_one(
                "#contact-phone-numbers-table", DataTable
            )
            assert phone_table.row_count == 1

    # =============================================
    # 4. SELECTION AND WATCHERS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_pre_selected_customer_id_sets_cursor(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """pre_selected_customer_id should position cursor on correct row."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=2,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            assert table.cursor_row == 1

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_customer_id(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Clicking a row should update selected_customer_id."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            await pilot.click(table, offset=(1, 3))
            await pilot.pause()
            assert pilot.app.screen.selected_customer_id == 2

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_contact_id(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Clicking a contact row should update selected_contact_id."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=3,
                )
            )
            await pilot.pause()
            contacts_table = pilot.app.screen.query_one(
                "#customer-contacts-table", DataTable
            )
            await pilot.click(contacts_table, offset=(1, 2))
            await pilot.pause()
            assert pilot.app.screen.selected_contact_id == 3

    # =============================================
    # 5. NAVIGATION AND ACTIONS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_create_customer_button_action(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Create customer button should dismiss with 'create_customer'."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                ),
                callback=on_dismiss,
            )
            await pilot.pause()
            button = pilot.app.screen.query_one("#create-customer", Button)
            await pilot.click(button)
            await pilot.pause()
            assert dismissed == "create_customer"

    @pytest.mark.asyncio
    async def test_update_customer_button_action(
        self, mock_customers_list, mock_second_sales_collaborator
    ):
        """Update customer button should dismiss with ('update_customer', customer_id)."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = CustomerScreen(
                customers=mock_customers_list,
                user=mock_second_sales_collaborator,
                customer_id=1,
            )
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            await pilot.click(table, offset=(1, 3))
            button = pilot.app.screen.query_one("#update-customer", Button)
            await pilot.click(button)
            await pilot.pause()
            assert dismissed == ("update_customer", 2)

    @pytest.mark.asyncio
    async def test_create_contact_button_action(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """Create contact button should dismiss with 'create_contact'."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                ),
                callback=on_dismiss,
            )
            await pilot.pause()
            button = pilot.app.screen.query_one("#create-contact", Button)
            await pilot.click(button)
            await pilot.pause()
            assert dismissed == "create_contact"

    @pytest.mark.asyncio
    async def test_update_contact_button_action(
        self, mock_customers_list, mock_second_sales_collaborator
    ):
        """Update contact button should dismiss with ('update_contact', contact_id)."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(120, 40)) as pilot:
            screen = CustomerScreen(
                customers=mock_customers_list,
                user=mock_second_sales_collaborator,
                customer_id=1,
            )
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()
            table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            await pilot.click(table, offset=(1, 3))
            button = pilot.app.screen.query_one("#update-contact", Button)
            await pilot.click(button)
            await pilot.pause()
            assert dismissed == ("update_contact", 2)

    # =============================================
    # 6. PERMISSIONS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_buttons_visible_for_sales_rep(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """All buttons should be visible for sales representative."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=1,
                )
            )
            await pilot.pause()
            for button_id in [
                "#create-customer",
                "#update-customer",
                "#create-contact",
                "#update-contact",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button.display

    @pytest.mark.asyncio
    async def test_buttons_hidden_for_unauthorized_user(
        self, mock_customers_list, mock_admin_collaborator
    ):
        """All action buttons should be hidden for unauthorized user."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_admin_collaborator,
                    customer_id=1,
                )
            )
            await pilot.pause()
            for button_id in [
                "#create-customer",
                "#update-customer",
                "#create-contact",
                "#update-contact",
            ]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert not button.display

    # =============================================
    # 7. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_builds_all_tables(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """on_mount should build all tables with correct titles."""
        app = App()
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(
                CustomerScreen(
                    customers=mock_customers_list,
                    user=mock_sales_collaborator,
                    customer_id=None,
                )
            )
            await pilot.pause()

            customers_table = pilot.app.screen.query_one(
                "#customers-table", DataTable
            )
            assert customers_table.border_title == "Customers"

            contacts_table = pilot.app.screen.query_one(
                "#customer-contacts-table", DataTable
            )
            assert contacts_table.border_title == "Contacts"

            phone_numbers_table = pilot.app.screen.query_one(
                "#contact-phone-numbers-table", DataTable
            )
            assert phone_numbers_table.border_title == "Phone Numbers"


# =============================================================================
# 2. CREATE CUSTOMER SCREEN TESTS
# =============================================================================


class TestCreateCustomerScreen:
    """Tests for CreateCustomerScreen."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, mock_contacts_list):
        """__init__ should store all parameters."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        assert screen.SUB_TITLE == "CREATE CUSTOMER"
        assert screen.CSS_PATH == "../styles/create_customer_screen.tcss"
        assert screen.contacts == mock_contacts_list
        assert screen.customer_data == {}

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self, mock_contacts_list):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CREATE CUSTOMER"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self, mock_contacts_list):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(self, mock_contacts_list):
        """All customer input fields should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            for field_id in [
                "#customer_last_name",
                "#customer_first_name",
                "#company_name",
            ]:
                field = pilot.app.screen.query_one(field_id, Input)
                assert field is not None

    @pytest.mark.asyncio
    async def test_radio_set_exists(self, mock_contacts_list):
        """RadioSet for contact selection should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            radio_set = pilot.app.screen.query_one(
                "#customer-contact-input-choice"
            )
            assert radio_set is not None

            radio_labels = [
                button.label
                for button in pilot.app.screen.query(RadioButton)
            ]
            assert "Existing contact" in radio_labels
            assert "New contact" in radio_labels

    @pytest.mark.asyncio
    async def test_contact_select_exists(self, mock_contacts_list):
        """Select for existing contacts should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#customer-contact-select", Select
            )
            assert select is not None

    @pytest.mark.asyncio
    async def test_contact_form_fields_exist(self, mock_contacts_list):
        """Contact form input fields should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            for field_id in [
                "#contact_last_name",
                "#contact_first_name",
                "#contact_email",
                "#contact_phone_number",
            ]:
                field = pilot.app.screen.query_one(field_id, Input)
                assert field is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(self, mock_contacts_list):
        """Create and Cancel buttons should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            for button_id in ["#create", "#cancel"]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. RADIOSET BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_new_contact_radio_selected_by_default(
        self, mock_contacts_list
    ):
        """'New contact' radio button is selected by default and shows form."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            radio_set = pilot.app.screen.query_one(
                "#customer-contact-input-choice", RadioSet
            )
            select_container = pilot.app.screen.query_one(
                "#customer-contact-select-input-container"
            )
            form_container = pilot.app.screen.query_one(
                "#customer-contact-form-input-container"
            )
            assert radio_set.pressed_button.label == "New contact"
            assert not select_container.display
            assert form_container.display

    @pytest.mark.asyncio
    async def test_existing_contact_radio_shows_select(
        self, mock_contacts_list
    ):
        """Selecting 'Existing contact' should show Select and hide form."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            radio_set = pilot.app.screen.query_one(
                "#customer-contact-input-choice", RadioSet
            )
            select_container = pilot.app.screen.query_one(
                "#customer-contact-select-input-container"
            )
            form_container = pilot.app.screen.query_one(
                "#customer-contact-form-input-container"
            )
            await pilot.click("#existing-contact")
            await pilot.pause()
            assert radio_set.pressed_button.label == "Existing contact"
            assert select_container.display
            assert not form_container.display

    # =============================================
    # 4. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self, mock_contacts_list):
        """Form should be invalid when all fields are empty."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False
            create_btn = pilot.app.screen.query_one("#create", Button)
            assert create_btn.disabled

    @pytest.mark.asyncio
    async def test_form_invalid_if_all_required_fields_not_filled(
        self, mock_contacts_list
    ):
        """Form should be invalid if all required fields are not filled."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()

            # Fill all fields except one
            # Fill in customer data
            # last_name_input = pilot.app.screen.query_one(
            #     "#customer_last_name", Input
            # )
            first_name_input = pilot.app.screen.query_one(
                "#customer_first_name", Input
            )
            company_name_input = pilot.app.screen.query_one(
                "#company_name", Input
            )
            # last_name_input.value = "Doe"
            first_name_input.value = "John"
            company_name_input.value = "Test Corp"

            # Fill in contact data
            contact_last_name = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            contact_first_name = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            contact_email = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            contact_phone = pilot.app.screen.query_one(
                "#contact_phone_number", Input
            )
            contact_last_name.value = "Smith"
            contact_first_name.value = "Alice"
            contact_email.value = "alice@example.com"
            contact_phone.value = "1234567890"

            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False
            create_btn = pilot.app.screen.query_one("#create", Button)
            assert create_btn.disabled

    @pytest.mark.asyncio
    async def test_form_valid_with_all_fields(self, mock_contacts_list):
        """Form should be valid when all required fields are filled."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()

            # Fill in customer data
            last_name_input = pilot.app.screen.query_one(
                "#customer_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#customer_first_name", Input
            )
            company_name_input = pilot.app.screen.query_one(
                "#company_name", Input
            )
            last_name_input.value = "Doe"
            first_name_input.value = "John"
            company_name_input.value = "Test Corp"

            # Fill in contact data
            contact_last_name = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            contact_first_name = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            contact_email = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            contact_phone = pilot.app.screen.query_one(
                "#contact_phone_number", Input
            )
            contact_last_name.value = "Smith"
            contact_first_name.value = "Alice"
            contact_email.value = "alice@example.com"
            contact_phone.value = "1234567890"

            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True
            create_btn = pilot.app.screen.query_one("#create", Button)
            assert not create_btn.disabled

    # =============================================
    # 5. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_new_contact_data(
        self, mock_contacts_list
    ):
        """Create button should dismiss with form data for new contact."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list),
                callback=on_dismiss,
            )
            await pilot.pause()
            customer_last_name = pilot.app.screen.query_one(
                "#customer_last_name", Input
            )
            customer_first_name = pilot.app.screen.query_one(
                "#customer_first_name", Input
            )
            company_name = pilot.app.screen.query_one(
                "#company_name", Input
            )
            customer_last_name.value = "NewLast"
            customer_first_name.value = "NewFirst"
            company_name.value = "New Corp"

            contact_last_name = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            contact_first_name = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            contact_email = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            contact_phone = pilot.app.screen.query_one(
                "#contact_phone_number", Input
            )
            contact_last_name.value = "ContactLast"
            contact_first_name.value = "ContactFirst"
            contact_email.value = "contact@newcorp.com"
            contact_phone.value = "1112223333"

            await pilot.pause()
            create_btn = pilot.app.screen.query_one("#create", Button)
            await pilot.click(create_btn)
            await pilot.pause()

            assert dismissed == {
                "customer_last_name": "NewLast",
                "customer_first_name": "NewFirst",
                "company_name": "New Corp",
                "customer_contact": {
                    "last_name": "ContactLast",
                    "first_name": "ContactFirst",
                    "email": "contact@newcorp.com",
                    "phone_number": "1112223333",
                },
            }

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, mock_contacts_list
    ):
        """Cancel button should dismiss with None."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list),
                callback=on_dismiss,
            )
            await pilot.pause()
            cancel_btn = pilot.app.screen.query_one("#cancel", Button)
            await pilot.click(cancel_btn)
            await pilot.pause()
            assert dismissed is None

    # =============================================
    # 6. CONTACT SELECT PREFILL TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_contact_select_has_all_options(
        self, mock_contacts_list
    ):
        """Contact Select should have all contacts as options."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateCustomerScreen(contacts=mock_contacts_list)
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#customer-contact-select", Select
            )
            await pilot.click(select)
            await pilot.pause()
            assert len(select._options) == 4

    # =============================================
    # 7. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(
        self, mock_contacts_list
    ):
        """on_mount should set container border titles."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateCustomerScreen(contacts=mock_contacts_list)
            await app.push_screen(screen)
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#customer-data").border_title
                == "Customer Data"
            )
            assert (
                pilot.app.screen.query_one(
                    "#customer-contact"
                ).border_title
                == "Contact Selection"
            )


# =============================================================================
# 3. UPDATE CUSTOMER SCREEN TESTS
# =============================================================================


class TestUpdateCustomerScreen:
    """Tests for UpdateCustomerScreen."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """__init__ should store all parameters."""
        customer_data = customer_to_dict(mock_customer)
        screen = UpdateCustomerScreen(
            customer_data=customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        assert screen.SUB_TITLE == "UPDATE CUSTOMER"
        assert screen.CSS_PATH == "../styles/update_customer_screen.tcss"
        assert screen.customer_data == customer_data
        assert screen.updated_customer_data == {}
        assert screen.contacts == mock_contacts_list
        assert screen.sales_representatives == mock_sales_representatives

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "UPDATE CUSTOMER"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_updating_customer_static_exists(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Static with updating customer message should exist."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            static = pilot.app.screen.query_one(
                "#updating-customer-static", Static
            )
            assert static is not None
            assert "Updating Customer" in static.content
            assert str(mock_customer.first_name) in static.content
            assert str(mock_customer.last_name) in static.content

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """All input fields should exist."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            for field_id in [
                "#customer_last_name",
                "#customer_first_name",
                "#company_name",
            ]:
                field = pilot.app.screen.query_one(field_id, Input)
                assert field is not None

    @pytest.mark.asyncio
    async def test_contacts_selection_list_exists(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """SelectionList for contacts should exist."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            selection_list = pilot.app.screen.query_one(
                "#update-customer-contacts-selection-list", SelectionList
            )
            assert selection_list is not None
            assert selection_list.option_count == len(mock_contacts_list)

    @pytest.mark.asyncio
    async def test_sales_representative_select_exists(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Select for sales representative should exist."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#update-customer-sales-representative-select", Select
            )
            assert select is not None
            assert (
                len(select._options) == len(mock_sales_representatives) + 1
            )

    @pytest.mark.asyncio
    async def test_buttons_exist(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Update and Cancel buttons should exist."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            for button_id in ["#update", "#cancel"]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. PREFILL TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_inputs_prefilled_with_customer_data(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Input fields should be prefilled with customer data."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#customer_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#customer_first_name", Input
            )
            company_name_input = pilot.app.screen.query_one(
                "#company_name", Input
            )
            assert last_name_input.value == mock_customer.last_name
            assert first_name_input.value == mock_customer.first_name
            assert company_name_input.value == mock_customer.company_name

    @pytest.mark.asyncio
    async def test_sales_representative_select_has_selected_value(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Sales representative Select should the sales rep selected."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            select = pilot.app.screen.query_one(
                "#update-customer-sales-representative-select", Select
            )
            await pilot.click(select)
            await pilot.pause()
            assert select.value == mock_customer.sales_representative

    @pytest.mark.asyncio
    async def test_contacts_selection_list_has_selected_contacts(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """SelectionList for contacts should have the customer's contacts selected."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            selection_list = pilot.app.screen.query_one(
                "#update-customer-contacts-selection-list", SelectionList
            )
            assert selection_list.selected == mock_customer.contacts

    # =============================================
    # 4. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_form_valid_when_all_fields_filled(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Form should be valid when all required fields are filled."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True

    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Form should be invalid when at least one required fields is invalid."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            # Erase customer last name
            last_name_input = pilot.app.screen.query_one(
                "#customer_last_name", Input
            )
            last_name_input.value = ""
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    # =============================================
    # 5. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_updated_data(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Update button should dismiss with updated customer data."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateCustomerScreen(
                customer_data=customer_data,
                contacts=mock_contacts_list,
                sales_representatives=mock_sales_representatives,
            )
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#customer_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#customer_first_name", Input
            )
            last_name_input.value = "UpdatedLast"
            first_name_input.value = "UpdatedFirst"
            await pilot.pause()
            update_btn = pilot.app.screen.query_one("#update", Button)
            await pilot.click(update_btn)
            await pilot.pause()
            assert dismissed["id"] == 1
            assert dismissed["customer_last_name"] == "UpdatedLast"
            assert dismissed["customer_first_name"] == "UpdatedFirst"
            assert dismissed["company_name"] == "Acme Corp"

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """Cancel button should dismiss with None."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                ),
                callback=on_dismiss,
            )
            await pilot.pause()
            cancel_btn = pilot.app.screen.query_one("#cancel", Button)
            await pilot.click(cancel_btn)
            await pilot.pause()
            assert dismissed is None

    # =============================================
    # 6. SELECTION LIST BEHAVIOR TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_selection_list_allows_multiple_selection(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """SelectionList should allow multiple contact selection."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            selection_list = pilot.app.screen.query_one(
                "#update-customer-contacts-selection-list", SelectionList
            )
            assert len(selection_list.selected) == 1
            # Select second contact
            await pilot.click(selection_list, offset=(2, 2))
            await pilot.pause()
            # Select third contact
            await pilot.click(selection_list, offset=(2, 3))
            await pilot.pause()
            # Deselect first contact
            await pilot.click(selection_list, offset=(2, 1))
            await pilot.pause()
            assert len(selection_list.selected) == 2

    # =============================================
    # 7. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(
        self,
        mock_customer,
        mock_contacts_list,
        mock_sales_representatives,
        customer_to_dict,
    ):
        """on_mount should set container border titles and subtitles."""
        app = App()
        customer_data = customer_to_dict(mock_customer)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateCustomerScreen(
                    customer_data=customer_data,
                    contacts=mock_contacts_list,
                    sales_representatives=mock_sales_representatives,
                )
            )
            await pilot.pause()
            assert (
                pilot.app.screen.query_one(
                    "#update-customer-data"
                ).border_title
                == "Personal Data"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-customer-data"
                ).border_subtitle
                == "Edit relevant fields"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-customer-sales-representative"
                ).border_title
                == "Sales Representative Selection"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-contact-data"
                ).border_title
                == "Assigned Contacts"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-contact-data"
                ).border_subtitle
                == "Click on contact to assign/unassign"
            )


# =============================================================================
# 4. CREATE CONTACT SCREEN TESTS
# =============================================================================


class TestCreateContactScreen:
    """Tests for CreateContactScreen."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self):
        """__init__ should initialize default values."""
        screen = CreateContactScreen()
        assert screen.SUB_TITLE == "CREATE CONTACT"
        assert screen.CSS_PATH == "../styles/create_contact_screen.tcss"
        assert screen.contact_data == {}
        assert screen.phone_number_counter == 2

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "CREATE CONTACT"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(self):
        """All contact input fields should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            for field_id in [
                "#contact_last_name",
                "#contact_first_name",
                "#contact_email",
            ]:
                field = pilot.app.screen.query_one(field_id, Input)
                assert field is not None

    @pytest.mark.asyncio
    async def test_phone_number_field_exists(self):
        """Initial phone number input field should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            phone_input = pilot.app.screen.query_one(
                "#phone_number_1", Input
            )
            assert phone_input is not None

    @pytest.mark.asyncio
    async def test_add_phone_number_button_exists(self):
        """Add phone number button should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            assert btn is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(self):
        """Create and Cancel buttons should exist."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            for button_id in ["#create", "#cancel"]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. DYNAMIC PHONE NUMBERS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_add_phone_number_button_adds_new_field(self):
        """Clicking add phone number button should create a new field with correct parameters."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContactScreen()
            await app.push_screen(screen)
            await pilot.pause()

            # Get initial phone number field
            initial_phone = pilot.app.screen.query_one(
                "#phone_number_1", Input
            )
            assert initial_phone is not None

            # Click add phone number button
            add_btn = pilot.app.screen.query_one(
                "#add-phone-number", Button
            )
            await pilot.click(add_btn)
            await pilot.pause()

            # Verify new field was created
            new_phone_field = pilot.app.screen.query_one(
                "#phone_number_2", Input
            )
            assert new_phone_field is not None

            # Verify field parameters
            assert new_phone_field.id == "phone_number_2"
            assert new_phone_field.value == ""  # Should be empty
            assert isinstance(new_phone_field, Input)

    @pytest.mark.asyncio
    async def test_phone_number_counter_increments(self):
        """phone_number_counter should increment when adding new fields."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContactScreen()
            await app.push_screen(screen)
            await pilot.pause()
            assert screen.phone_number_counter == 2
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            await pilot.click(btn)
            await pilot.pause()
            assert screen.phone_number_counter == 3

    @pytest.mark.asyncio
    async def test_add_multiple_phone_numbers(self):
        """Adding multiple phone number fields should work correctly."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContactScreen()
            await app.push_screen(screen)
            await pilot.pause()
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            for _ in range(4):
                await pilot.click(btn)
                await pilot.pause()

            assert (
                pilot.app.screen.query_one("#phone_number_1", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#phone_number_2", Input)
                is not None
            )
            assert (
                pilot.app.screen.query_one("#phone_number_3", Input)
                is not None
            )

    # =============================================
    # 4. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self):
        """Form should be invalid when all fields are empty."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False
            create_btn = pilot.app.screen.query_one("#create", Button)
            assert create_btn.disabled

    @pytest.mark.asyncio
    async def test_required_fields_validation(self):
        """last_name, first_name, and email should be required."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            last_name_input.value = "TestLast"
            first_name_input.value = "TestFirst"
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_phone_numbers_required(self):
        """Each phone number should be required."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            last_name_input.value = "TestLast"
            first_name_input.value = "TestFirst"
            email_input.value = "test@example.com"
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_when_all_fields_filled(self):
        """Form should be valid when all required fields are filled."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            phone_input = pilot.app.screen.query_one(
                "#phone_number_1", Input
            )
            last_name_input.value = "TestLast"
            first_name_input.value = "TestFirst"
            email_input.value = "test@example.com"
            phone_input.value = "1234567890"
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True

    @pytest.mark.asyncio
    async def test_validation_updates_on_new_phone_number(self):
        """Validation should update when new phone number field is added."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(CreateContactScreen())
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            phone_input = pilot.app.screen.query_one(
                "#phone_number_1", Input
            )
            last_name_input.value = "TestLast"
            first_name_input.value = "TestFirst"
            email_input.value = "test@example.com"
            phone_input.value = "1234567890"
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            await pilot.click(btn)
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    # =============================================
    # 5. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_form_data(self):
        """Create button should dismiss with contact data."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContactScreen(),
                callback=on_dismiss,
            )
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            phone_input = pilot.app.screen.query_one(
                "#phone_number_1", Input
            )
            last_name_input.value = "Smith"
            first_name_input.value = "Alice"
            email_input.value = "alice@example.com"
            phone_input.value = "1234567890"
            await pilot.pause()
            create_btn = pilot.app.screen.query_one("#create", Button)
            await pilot.click(create_btn)
            await pilot.pause()
            assert dismissed == {
                "contact_last_name": "Smith",
                "contact_first_name": "Alice",
                "email": "alice@example.com",
                "phone_numbers": ["1234567890"],
            }

    @pytest.mark.asyncio
    async def test_create_button_with_multiple_phones(self):
        """Create button should include all phone numbers."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContactScreen(),
                callback=on_dismiss,
            )
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            phone_input = pilot.app.screen.query_one(
                "#phone_number_1", Input
            )
            last_name_input.value = "Smith"
            first_name_input.value = "Alice"
            email_input.value = "alice@example.com"
            phone_input.value = "1234567890"
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            await pilot.click(btn)
            await pilot.pause()
            phone_input_2 = pilot.app.screen.query_one(
                "#phone_number_2", Input
            )
            phone_input_2.value = "0987654321"
            await pilot.pause()
            create_btn = pilot.app.screen.query_one("#create", Button)
            await pilot.click(create_btn)
            await pilot.pause()
            assert dismissed["phone_numbers"] == [
                "1234567890",
                "0987654321",
            ]

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(self):
        """Cancel button should dismiss with None."""
        app = App()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                CreateContactScreen(),
                callback=on_dismiss,
            )
            await pilot.pause()
            cancel_btn = pilot.app.screen.query_one("#cancel", Button)
            await pilot.click(cancel_btn)
            await pilot.pause()
            assert dismissed is None

    # =============================================
    # 6. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(self):
        """on_mount should set container border titles."""
        app = App()
        async with app.run_test(size=(100, 30)) as pilot:
            screen = CreateContactScreen()
            await app.push_screen(screen)
            await pilot.pause()
            assert (
                pilot.app.screen.query_one("#contact-data").border_title
                == "Personal Data"
            )
            assert (
                pilot.app.screen.query_one("#phone-number").border_title
                == "Phone Numbers"
            )


# =============================================================================
# 5. UPDATE CONTACT SCREEN TESTS
# =============================================================================


class TestUpdateContactScreen:
    """Tests for UpdateContactScreen."""

    # =============================================
    # 1. INITIALIZATION TESTS
    # =============================================

    def test_initialization(self, mock_contact, contact_to_dict):
        """__init__ should store all parameters."""
        contact_data = contact_to_dict(mock_contact)
        screen = UpdateContactScreen(contact_data=contact_data)
        assert screen.SUB_TITLE == "UPDATE CONTACT"
        assert screen.CSS_PATH == "../styles/update_contact_screen.tcss"
        assert screen.contact_data == contact_data
        assert screen.updated_contact_data == {}
        assert screen.phone_number_counter == 1

    def test_init_phone_number_counter(
        self, mock_third_contact, contact_to_dict
    ):
        """__init__ should set phone_number_counter based on existing phones."""
        contact_data = contact_to_dict(mock_third_contact)
        screen = UpdateContactScreen(contact_data=contact_data)
        assert screen.SUB_TITLE == "UPDATE CONTACT"
        assert screen.CSS_PATH == "../styles/update_contact_screen.tcss"
        assert screen.contact_data == contact_data
        assert screen.updated_contact_data == {}
        assert screen.phone_number_counter == 2

    # =============================================
    # 2. UI ARCHITECTURE TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_header_exists(self, mock_contact, contact_to_dict):
        """Header should exist with correct title and clock enabled."""
        app = EpicEventsCRM()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            header = pilot.app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "UPDATE CONTACT"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_footer_exists(self, mock_contact, contact_to_dict):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            footer = pilot.app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_updating_contact_static_exists(
        self, mock_contact, contact_to_dict
    ):
        """Static with updating contact message should exist."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            static = pilot.app.screen.query_one(
                "#updating-contact-static", Static
            )
            assert static is not None
            assert "Updating Contact" in static.content
            assert mock_contact.first_name in static.content
            assert mock_contact.last_name in static.content

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(
        self, mock_contact, contact_to_dict
    ):
        """All input fields should exist."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            for field_id in [
                "#contact_last_name",
                "#contact_first_name",
                "#contact_email",
            ]:
                field = pilot.app.screen.query_one(field_id, Input)
                assert field is not None

    @pytest.mark.asyncio
    async def test_phone_number_fields_exist(
        self, mock_third_contact, contact_to_dict
    ):
        """Phone number input fields should exist for existing numbers."""
        app = App()
        contact_data = contact_to_dict(mock_third_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            for phone_id in ["#phone_number_0", "#phone_number_1"]:
                phone = pilot.app.screen.query_one(phone_id, Input)
                assert phone is not None

    @pytest.mark.asyncio
    async def test_add_phone_number_button_exists(
        self, mock_contact, contact_to_dict
    ):
        """Add phone number button should exist."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            assert btn is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(self, mock_contact, contact_to_dict):
        """Update and Cancel buttons should exist."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            for button_id in ["#update", "#cancel"]:
                button = pilot.app.screen.query_one(button_id, Button)
                assert button is not None

    # =============================================
    # 3. PREFILL TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_inputs_prefilled_with_contact_data(
        self, mock_contact, contact_to_dict
    ):
        """Input fields should be prefilled with contact data."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            assert last_name_input.value == mock_contact.last_name
            assert first_name_input.value == mock_contact.first_name
            assert email_input.value == mock_contact.email

    @pytest.mark.asyncio
    async def test_phone_numbers_prefilled(
        self, mock_third_contact, contact_to_dict
    ):
        """Phone number fields should be prefilled."""
        app = App()
        contact_data = contact_to_dict(mock_third_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            phone_1 = pilot.app.screen.query_one("#phone_number_0", Input)
            phone_2 = pilot.app.screen.query_one("#phone_number_1", Input)
            assert (
                phone_1.value == mock_third_contact.phone_numbers[0].number
            )
            assert (
                phone_2.value == mock_third_contact.phone_numbers[1].number
            )

    # =============================================
    # 4. DYNAMIC PHONE NUMBERS TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_add_phone_number_button_adds_new_field(
        self, mock_contact, contact_to_dict
    ):
        """Clicking add phone number should add a new input field."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()

            # Get initial phone number fields by filtering
            all_inputs = pilot.app.screen.query(Input)
            initial_phones = [
                widget
                for widget in all_inputs
                if widget.id.startswith("phone_number_")
            ]
            initial_count = len(initial_phones)
            assert initial_count == 1

            # Click add phone number button
            add_btn = pilot.app.screen.query_one(
                "#add-phone-number", Button
            )
            await pilot.click(add_btn)
            await pilot.pause()

            # Verify new field was created
            all_inputs = pilot.app.screen.query(Input)
            new_phones = [
                widget
                for widget in all_inputs
                if widget.id.startswith("phone_number_")
            ]
            assert len(new_phones) == initial_count + 1

            # Verify new field parameters
            new_phone_field = pilot.app.screen.query_one(
                "#phone_number_2", Input
            )
            assert new_phone_field is not None
            assert new_phone_field.value == ""
            assert isinstance(new_phone_field, Input)

            # Verify phone number counter was incremented
            assert pilot.app.screen.phone_number_counter == 2

    # =============================================
    # 5. FORM VALIDATION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self):
        """Form should be invalid when required fields are empty."""
        app = App()
        # contact_data = contact_to_dict(mock_contact)
        empty_data = {
            "contact_id": 1,
            "contact_first_name": "",
            "contact_last_name": "",
            "email": "",
            "phone_numbers": [""],
        }
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=empty_data)
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_required_fields_validation(
        self, mock_contact, contact_to_dict
    ):
        """last_name, first_name, and email should be required."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True
            email_input = pilot.app.screen.query_one(
                "#contact_email", Input
            )
            email_input.value = ""
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_phone_numbers_validation(
        self, mock_contact, contact_to_dict
    ):
        """Each phone number should be required."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True
            phone_1 = pilot.app.screen.query_one("#phone_number_0", Input)
            phone_1.value = ""
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_when_all_fields_filled(
        self, mock_contact, contact_to_dict
    ):
        """Form should be valid when all required fields are filled."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            assert pilot.app.screen.is_form_valid is True

    # =============================================
    # 6. FORM SUBMISSION TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_updated_data(
        self, mock_contact, contact_to_dict
    ):
        """Update button should dismiss with updated contact data."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateContactScreen(contact_data=contact_data)
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()
            last_name_input = pilot.app.screen.query_one(
                "#contact_last_name", Input
            )
            first_name_input = pilot.app.screen.query_one(
                "#contact_first_name", Input
            )
            last_name_input.value = "UpdatedLast"
            first_name_input.value = "UpdatedFirst"
            await pilot.pause()
            update_btn = pilot.app.screen.query_one("#update", Button)
            await pilot.click(update_btn)
            await pilot.pause()
            assert dismissed["id"] == 1
            assert dismissed["last_name"] == "UpdatedLast"
            assert dismissed["first_name"] == "UpdatedFirst"
            assert dismissed["email"] == "alice.smith@example.com"

    @pytest.mark.asyncio
    async def test_update_button_with_new_phone_numbers(
        self, mock_third_contact, contact_to_dict
    ):
        """Update button should include all phone numbers including new ones."""
        app = App()
        contact_data = contact_to_dict(mock_third_contact)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            screen = UpdateContactScreen(contact_data=contact_data)
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()
            btn = pilot.app.screen.query_one("#add-phone-number", Button)
            await pilot.click(btn)
            await pilot.pause()
            new_phone = pilot.app.screen.query_one(
                "#phone_number_3", Input
            )
            new_phone.value = "7778889999"
            await pilot.pause()
            update_btn = pilot.app.screen.query_one("#update", Button)
            await pilot.click(update_btn)
            await pilot.pause()
            assert dismissed["phone_numbers"] == [
                "5556667777",
                "1112223333",
                "7778889999",
            ]

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, mock_contact, contact_to_dict
    ):
        """Cancel button should dismiss with None."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data),
                callback=on_dismiss,
            )
            await pilot.pause()
            cancel_btn = pilot.app.screen.query_one("#cancel", Button)
            await pilot.click(cancel_btn)
            await pilot.pause()
            assert dismissed is None

    # =============================================
    # 7. ON_MOUNT TESTS
    # =============================================

    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(
        self, mock_contact, contact_to_dict
    ):
        """on_mount should set container border titles and subtitles."""
        app = App()
        contact_data = contact_to_dict(mock_contact)
        async with app.run_test(size=(100, 30)) as pilot:
            await app.push_screen(
                UpdateContactScreen(contact_data=contact_data)
            )
            await pilot.pause()
            assert (
                pilot.app.screen.query_one(
                    "#update-contact-data"
                ).border_title
                == "Personal Data"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-contact-data"
                ).border_subtitle
                == "Edit relevant fields"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-phone-number"
                ).border_title
                == "Phone Numbers"
            )
            assert (
                pilot.app.screen.query_one(
                    "#update-phone-number"
                ).border_subtitle
                == "Edit relevant fields"
            )
