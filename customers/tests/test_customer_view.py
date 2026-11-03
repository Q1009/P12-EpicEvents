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

from unittest.mock import MagicMock, patch

import pytest
from textual.app import App
from textual.pilot import Pilot

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
    # contact.customers = []
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
    # contact.customers = []
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
    # contact.customers = []
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


# --- Textual Fixtures ---
@pytest.fixture
def app():
    """Textual App for testing."""
    return App()


@pytest.fixture
async def pilot(app):
    """Pilot for controlling the Textual application."""
    async with Pilot(app) as pilot:
        yield pilot


# =============================================================================
# 1. CUSTOMER SCREEN TESTS
# =============================================================================


class TestCustomerScreen:
    """Tests for CustomerScreen."""

    # --- 1.1 Initialization Tests (Synchronous) ---
    def test_init_sets_customers(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """__init__ should store customers list."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        assert screen.customers == mock_customers_list

    def test_init_sets_user(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """__init__ should store user."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        assert screen.user == mock_sales_collaborator

    def test_init_sets_customer_id(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """__init__ should store customer_id."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=2,
        )
        assert screen.customer_id == 2

    def test_init_default_values(
        self, mock_customers_list, mock_sales_collaborator
    ):
        """__init__ should set default values."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        assert screen.pre_selected_customer_id is None
        assert screen.selected_customer_id is None
        assert screen.selected_contact_id is None

    # --- 1.2 UI Structure Tests (Asynchronous) ---
    @pytest.mark.asyncio
    async def test_header_exists(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """Header should exist with SUB_TITLE='CUSTOMERS'."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            header = app.query_one("Header")
            assert header is not None

    @pytest.mark.asyncio
    async def test_footer_exists(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """Footer should exist with show_command_palette=False."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            footer = app.query_one("Footer")
            assert footer is not None

    @pytest.mark.asyncio
    async def test_customers_table_exists(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customers-table DataTable should exist."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            assert table is not None

    @pytest.mark.asyncio
    async def test_contacts_table_exists(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customer-contacts-table DataTable should exist."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one(
                "#customer-contacts-table", CustomerScreen
            )
            assert table is not None

    @pytest.mark.asyncio
    async def test_phone_numbers_table_exists(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#contact-phone-numbers-table DataTable should exist."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one(
                "#contact-phone-numbers-table", CustomerScreen
            )
            assert table is not None

    @pytest.mark.asyncio
    async def test_all_buttons_exist(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """All action buttons should exist."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            create_customer_btn = app.query_one(
                "#create-customer", CustomerScreen
            )
            update_customer_btn = app.query_one(
                "#update-customer", CustomerScreen
            )
            create_contact_btn = app.query_one(
                "#create-contact", CustomerScreen
            )
            update_contact_btn = app.query_one(
                "#update-contact", CustomerScreen
            )
            assert create_customer_btn is not None
            assert update_customer_btn is not None
            assert create_contact_btn is not None
            assert update_contact_btn is not None

    @pytest.mark.asyncio
    async def test_customers_table_has_correct_columns(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customers-table should have correct column headers."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            headers = table.columns
            assert headers == [
                "ID",
                "First Name",
                "Last Name",
                "Company Name",
                "Sales Representative",
                "Created At",
                "Updated At",
            ]

    @pytest.mark.asyncio
    async def test_contacts_table_has_correct_columns(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customer-contacts-table should have correct column headers."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one(
                "#customer-contacts-table", CustomerScreen
            )
            headers = table.columns
            assert headers == ["ID", "First Name", "Last Name", "Email"]

    @pytest.mark.asyncio
    async def test_phone_numbers_table_has_correct_columns(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#contact-phone-numbers-table should have correct column headers."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one(
                "#contact-phone-numbers-table", CustomerScreen
            )
            headers = table.columns
            assert headers == ["ID", "Phone Number"]

    # --- 1.3 Data Loading Tests ---
    @pytest.mark.asyncio
    async def test_customers_table_loaded_with_data(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customers-table should be loaded with all customers."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            assert table.row_count == 3

    @pytest.mark.asyncio
    async def test_customers_table_content_matches_data(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customers-table content should match customer data."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            # Check first row data
            assert table.get_cell_at(0, 0) == "1"  # ID
            assert table.get_cell_at(0, 1) == "John"  # First Name
            assert table.get_cell_at(0, 2) == "Doe"  # Last Name
            assert table.get_cell_at(0, 3) == "Acme Corp"  # Company Name

    @pytest.mark.asyncio
    async def test_contacts_table_loaded_when_customer_selected(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#customer-contacts-table should load when customer is selected."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            # Click on first row to select customer
            await app.pilot.click(table, row=0, column=0)
            await app.pilot.pause()
            contacts_table = app.query_one(
                "#customer-contacts-table", CustomerScreen
            )
            assert (
                contacts_table.row_count == 1
            )  # mock_customer has 1 contact

    @pytest.mark.asyncio
    async def test_phone_numbers_table_loaded_when_contact_selected(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#contact-phone-numbers-table should load when contact is selected."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=1,  # Pre-select first customer
        )
        async with app.run_test(screen):
            # First select customer (already done via customer_id)
            contacts_table = app.query_one(
                "#customer-contacts-table", CustomerScreen
            )
            await app.pilot.pause()
            # Click on first contact row
            await app.pilot.click(contacts_table, row=0, column=0)
            await app.pilot.pause()
            phone_table = app.query_one(
                "#contact-phone-numbers-table", CustomerScreen
            )
            assert (
                phone_table.row_count == 1
            )  # mock_contact has 1 phone number

    # --- 1.4 Selection and Watchers Tests ---
    @pytest.mark.asyncio
    async def test_pre_selected_customer_id_sets_cursor(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """pre_selected_customer_id should position cursor on correct row."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=2,  # Pre-select second customer
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            await app.pilot.pause()
            # The cursor should be on row 1 (0-indexed) for customer_id=2
            assert table.cursor_row == 1

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_customer_id(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """Clicking a row should update selected_customer_id."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        async with app.run_test(screen):
            table = app.query_one("#customers-table", CustomerScreen)
            await app.pilot.click(
                table, row=1, column=0
            )  # Click second row
            await app.pilot.pause()
            assert (
                screen.selected_customer_id == 2
            )  # customer_id of second customer

    @pytest.mark.asyncio
    async def test_row_highlighted_updates_selected_contact_id(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """Clicking a contact row should update selected_contact_id."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=1,  # Pre-select first customer
        )
        async with app.run_test(screen):
            await app.pilot.pause()
            contacts_table = app.query_one(
                "#customer-contacts-table", CustomerScreen
            )
            await app.pilot.click(
                contacts_table, row=0, column=0
            )  # Click first contact
            await app.pilot.pause()
            assert (
                screen.selected_contact_id == 1
            )  # contact_id of first contact

    # --- 1.5 Navigation and Actions Tests ---
    @pytest.mark.asyncio
    async def test_create_customer_button_action(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#create-customer button should dismiss with 'create_customer'."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            btn = app.query_one("#create-customer", CustomerScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()
            assert dismissed == "create_customer"

    @pytest.mark.asyncio
    async def test_update_customer_button_action(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#update-customer button should dismiss with ('update_customer', customer_id)."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=1,  # Pre-select first customer
        )
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            await app.pilot.pause()
            # First select a customer
            screen.selected_customer_id = 2
            await app.pilot.pause()
            btn = app.query_one("#update-customer", CustomerScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()
            assert dismissed == ("update_customer", 2)

    @pytest.mark.asyncio
    async def test_create_contact_button_action(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#create-contact button should dismiss with 'create_contact'."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            btn = app.query_one("#create-contact", CustomerScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()
            assert dismissed == "create_contact"

    @pytest.mark.asyncio
    async def test_update_contact_button_action(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """#update-contact button should dismiss with ('update_contact', contact_id)."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=1,
        )
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            await app.pilot.pause()
            # First select a contact
            screen.selected_contact_id = 2
            await app.pilot.pause()
            btn = app.query_one("#update-contact", CustomerScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()
            assert dismissed == ("update_contact", 2)

    # --- 1.6 Permissions Tests ---
    @pytest.mark.asyncio
    async def test_buttons_visible_for_sales_rep(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """All buttons should be visible for sales representative."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=1,
        )
        async with app.run_test(screen):
            await app.pilot.pause()
            create_customer_btn = app.query_one(
                "#create-customer", CustomerScreen
            )
            update_customer_btn = app.query_one(
                "#update-customer", CustomerScreen
            )
            create_contact_btn = app.query_one(
                "#create-contact", CustomerScreen
            )
            update_contact_btn = app.query_one(
                "#update-contact", CustomerScreen
            )
            assert create_customer_btn.display
            assert update_customer_btn.display
            assert create_contact_btn.display
            assert update_contact_btn.display

    @pytest.mark.asyncio
    async def test_buttons_hidden_for_unauthorized_user(
        self, app, mock_customers_list
    ):
        """All action buttons should be hidden for unauthorized user."""
        unauthorized_user = MagicMock(spec=Collaborator)
        unauthorized_user.id = 99
        unauthorized_user.department = MagicMock(spec=Department)
        unauthorized_user.department.name = DepartmentName.MARKETING

        screen = CustomerScreen(
            customers=mock_customers_list,
            user=unauthorized_user,
            customer_id=None,
        )
        async with app.run_test(screen):
            await app.pilot.pause()
            create_customer_btn = app.query_one(
                "#create-customer", CustomerScreen
            )
            update_customer_btn = app.query_one(
                "#update-customer", CustomerScreen
            )
            create_contact_btn = app.query_one(
                "#create-contact", CustomerScreen
            )
            update_contact_btn = app.query_one(
                "#update-contact", CustomerScreen
            )
            assert not create_customer_btn.display
            assert not update_customer_btn.display
            assert not create_contact_btn.display
            assert not update_contact_btn.display

    # --- 1.7 on_mount Tests ---
    @pytest.mark.asyncio
    async def test_on_mount_builds_all_tables(
        self, app, mock_customers_list, mock_sales_collaborator
    ):
        """on_mount should call build tables methods."""
        screen = CustomerScreen(
            customers=mock_customers_list,
            user=mock_sales_collaborator,
            customer_id=None,
        )
        with (
            patch.object(
                screen, "build_customers_table"
            ) as mock_build_customers,
            patch.object(
                screen, "build_contacts_table"
            ) as mock_build_contacts,
            patch.object(
                screen, "build_phone_numbers_table"
            ) as mock_build_phones,
        ):
            async with app.run_test(screen):
                await app.pilot.pause()
                mock_build_customers.assert_called_once()
                mock_build_contacts.assert_called_once()
                mock_build_phones.assert_called_once()


# =============================================================================
# 2. CREATE CUSTOMER SCREEN TESTS
# =============================================================================


class TestCreateCustomerScreen:
    """Tests for CreateCustomerScreen."""

    # --- 2.1 Initialization Tests ---
    def test_init_sets_contacts(self, mock_contacts_list):
        """__init__ should store contacts list."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        assert screen.contacts == mock_contacts_list

    def test_init_default_values(self, mock_contacts_list):
        """__init__ should initialize default values."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        assert screen.customer_data == {}
        assert screen.is_form_valid is False

    # --- 2.2 UI Structure Tests ---
    @pytest.mark.asyncio
    async def test_header_exists(self, app, mock_contacts_list):
        """Header should exist with SUB_TITLE='CREATE CUSTOMERS'."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            header = app.query_one("Header")
            assert header is not None

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(self, app, mock_contacts_list):
        """All customer input fields should exist."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#customer_last_name", CreateCustomerScreen
            )
            first_name_input = app.query_one(
                "#customer_first_name", CreateCustomerScreen
            )
            company_name_input = app.query_one(
                "#company_name", CreateCustomerScreen
            )
            assert last_name_input is not None
            assert first_name_input is not None
            assert company_name_input is not None

    @pytest.mark.asyncio
    async def test_radio_set_exists(self, app, mock_contacts_list):
        """RadioSet for contact selection should exist."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            radio_set = app.query_one(
                "#customer-contact-input-choice", CreateCustomerScreen
            )
            assert radio_set is not None

    @pytest.mark.asyncio
    async def test_contact_select_exists(self, app, mock_contacts_list):
        """Select for existing contacts should exist."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            select = app.query_one(
                "#customer-contact-select", CreateCustomerScreen
            )
            assert select is not None

    @pytest.mark.asyncio
    async def test_contact_form_fields_exist(
        self, app, mock_contacts_list
    ):
        """Contact form input fields should exist."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#contact_last_name", CreateCustomerScreen
            )
            first_name_input = app.query_one(
                "#contact_first_name", CreateCustomerScreen
            )
            email_input = app.query_one(
                "#contact_email", CreateCustomerScreen
            )
            phone_input = app.query_one(
                "#contact_phone_number", CreateCustomerScreen
            )
            assert last_name_input is not None
            assert first_name_input is not None
            assert email_input is not None
            assert phone_input is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(self, app, mock_contacts_list):
        """Create and Cancel buttons should exist."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            create_btn = app.query_one("#create", CreateCustomerScreen)
            cancel_btn = app.query_one("#cancel", CreateCustomerScreen)
            assert create_btn is not None
            assert cancel_btn is not None

    # --- 2.3 RadioSet Behavior Tests ---
    @pytest.mark.asyncio
    async def test_existing_contact_radio_shows_select(
        self, app, mock_contacts_list
    ):
        """Selecting 'Existing contact' should show Select and hide form."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            radio_set = app.query_one(
                "#customer-contact-input-choice", CreateCustomerScreen
            )
            select_container = app.query_one(
                "#customer-contact-select-input-container",
                CreateCustomerScreen,
            )
            form_container = app.query_one(
                "#customer-contact-form-input-container",
                CreateCustomerScreen,
            )

            # Select first radio button ("Existing contact")
            await app.pilot.click(radio_set, offset=(0, 0))
            await app.pilot.pause()

            assert select_container.display
            assert not form_container.display

    @pytest.mark.asyncio
    async def test_new_contact_radio_shows_form(
        self, app, mock_contacts_list
    ):
        """Selecting 'New contact' should show form and hide Select."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            radio_set = app.query_one(
                "#customer-contact-input-choice", CreateCustomerScreen
            )
            select_container = app.query_one(
                "#customer-contact-select-input-container",
                CreateCustomerScreen,
            )
            form_container = app.query_one(
                "#customer-contact-form-input-container",
                CreateCustomerScreen,
            )

            # Select second radio button ("New contact")
            await app.pilot.click(radio_set, offset=(0, 1))
            await app.pilot.pause()

            assert not select_container.display
            assert form_container.display

    # --- 2.4 Form Validation Tests ---
    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self, app, mock_contacts_list):
        """Form should be invalid when all fields are empty."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is False
            create_btn = app.query_one("#create", CreateCustomerScreen)
            assert create_btn.disabled

    @pytest.mark.asyncio
    async def test_customer_fields_required(self, app, mock_contacts_list):
        """Customer last_name and first_name should be required."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#customer_last_name", CreateCustomerScreen
            )
            first_name_input = app.query_one(
                "#customer_first_name", CreateCustomerScreen
            )

            # Set only customer fields
            last_name_input.value = "Doe"
            first_name_input.value = "John"
            company_name_input = app.query_one(
                "#company_name", CreateCustomerScreen
            )
            company_name_input.value = "Test Corp"

            await app.pilot.pause()
            # Form should still be invalid because contact fields are empty
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_with_all_fields(
        self, app, mock_contacts_list
    ):
        """Form should be valid when all required fields are filled."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            # Fill customer fields
            last_name_input = app.query_one(
                "#customer_last_name", CreateCustomerScreen
            )
            last_name_input.value = "Doe"
            first_name_input = app.query_one(
                "#customer_first_name", CreateCustomerScreen
            )
            first_name_input.value = "John"
            company_name_input = app.query_one(
                "#company_name", CreateCustomerScreen
            )
            company_name_input.value = "Test Corp"

            # Select new contact and fill contact fields
            radio_set = app.query_one(
                "#customer-contact-input-choice", CreateCustomerScreen
            )
            await app.pilot.click(radio_set, offset=(0, 1))  # New contact
            await app.pilot.pause()

            contact_last_name = app.query_one(
                "#contact_last_name", CreateCustomerScreen
            )
            contact_last_name.value = "Smith"
            contact_first_name = app.query_one(
                "#contact_first_name", CreateCustomerScreen
            )
            contact_first_name.value = "Alice"
            contact_email = app.query_one(
                "#contact_email", CreateCustomerScreen
            )
            contact_email.value = "alice@example.com"
            contact_phone = app.query_one(
                "#contact_phone_number", CreateCustomerScreen
            )
            contact_phone.value = "1234567890"

            await app.pilot.pause()
            assert screen.is_form_valid is True
            create_btn = app.query_one("#create", CreateCustomerScreen)
            assert not create_btn.disabled

    # --- 2.5 Form Submission Tests ---
    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_new_contact_data(
        self, app, mock_contacts_list
    ):
        """Create button should dismiss with form data for new contact."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            # Fill all fields for new contact
            customer_last_name = app.query_one(
                "#customer_last_name", CreateCustomerScreen
            )
            customer_last_name.value = "NewLast"
            customer_first_name = app.query_one(
                "#customer_first_name", CreateCustomerScreen
            )
            customer_first_name.value = "NewFirst"
            company_name = app.query_one(
                "#company_name", CreateCustomerScreen
            )
            company_name.value = "New Corp"

            radio_set = app.query_one(
                "#customer-contact-input-choice", CreateCustomerScreen
            )
            await app.pilot.click(radio_set, offset=(0, 1))  # New contact
            await app.pilot.pause()

            contact_last_name = app.query_one(
                "#contact_last_name", CreateCustomerScreen
            )
            contact_last_name.value = "ContactLast"
            contact_first_name = app.query_one(
                "#contact_first_name", CreateCustomerScreen
            )
            contact_first_name.value = "ContactFirst"
            contact_email = app.query_one(
                "#contact_email", CreateCustomerScreen
            )
            contact_email.value = "contact@newcorp.com"
            contact_phone = app.query_one(
                "#contact_phone_number", CreateCustomerScreen
            )
            contact_phone.value = "1112223333"

            await app.pilot.pause()
            create_btn = app.query_one("#create", CreateCustomerScreen)
            await app.pilot.click(create_btn)
            await app.pilot.pause()

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
        self, app, mock_contacts_list
    ):
        """Cancel button should dismiss with None."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            cancel_btn = app.query_one("#cancel", CreateCustomerScreen)
            await app.pilot.click(cancel_btn)
            await app.pilot.pause()
            assert dismissed is None

    # --- 2.6 Contact Select Prefill Tests ---
    @pytest.mark.asyncio
    async def test_contact_select_has_all_options(
        self, app, mock_contacts_list
    ):
        """Contact Select should have all contacts as options."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            select = app.query_one(
                "#customer-contact-select", CreateCustomerScreen
            )
            await app.pilot.click(select)
            await app.pilot.pause()
            # Should have 3 options (the contacts)
            assert len(select._options) == 3

    # --- 2.7 on_mount Tests ---
    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(
        self, app, mock_contacts_list
    ):
        """on_mount should set container border titles."""
        screen = CreateCustomerScreen(contacts=mock_contacts_list)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert (
                screen.query_one("#customer-data").border_title
                == "Customer Data"
            )
            assert (
                screen.query_one("#customer-contact").border_title
                == "Contact Selection"
            )


# =============================================================================
# 3. UPDATE CUSTOMER SCREEN TESTS
# =============================================================================


class TestUpdateCustomerScreen:
    """Tests for UpdateCustomerScreen."""

    # --- 3.1 Initialization Tests ---
    def test_init_sets_customer_data(self, mock_customer_data):
        """__init__ should store customer_data."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=[],
            sales_representatives=[],
        )
        assert screen.customer_data == mock_customer_data

    def test_init_sets_contacts_and_sales_reps(
        self,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """__init__ should store contacts and sales_representatives."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        assert screen.contacts == mock_contacts_list
        assert screen.sales_representatives == mock_sales_representatives

    # --- 3.2 UI Structure Tests ---
    @pytest.mark.asyncio
    async def test_header_exists(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Header should exist with SUB_TITLE='UPDATE CUSTOMERS'."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            header = app.query_one("Header")
            assert header is not None

    @pytest.mark.asyncio
    async def test_updating_customer_static_exists(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Static with updating customer message should exist."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            static = app.query_one("Static")
            assert static is not None
            assert "Updating Customer" in str(static)

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """All input fields should exist."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#customer_last_name", UpdateCustomerScreen
            )
            first_name_input = app.query_one(
                "#customer_first_name", UpdateCustomerScreen
            )
            company_name_input = app.query_one(
                "#company_name", UpdateCustomerScreen
            )
            assert last_name_input is not None
            assert first_name_input is not None
            assert company_name_input is not None

    @pytest.mark.asyncio
    async def test_contacts_selection_list_exists(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """SelectionList for contacts should exist."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            selection_list = app.query_one(
                "#update-customer-contacts-selection-list",
                UpdateCustomerScreen,
            )
            assert selection_list is not None

    @pytest.mark.asyncio
    async def test_sales_representative_select_exists(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Select for sales representative should exist."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            select = app.query_one(
                "#update-customer-sales-representative-select",
                UpdateCustomerScreen,
            )
            assert select is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Update and Cancel buttons should exist."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            update_btn = app.query_one("#update", UpdateCustomerScreen)
            cancel_btn = app.query_one("#cancel", UpdateCustomerScreen)
            assert update_btn is not None
            assert cancel_btn is not None

    # --- 3.3 Prefill Tests ---
    @pytest.mark.asyncio
    async def test_inputs_prefilled_with_customer_data(
        self,
        app,
        customer_to_dict,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Input fields should be prefilled with customer data."""
        customer = MagicMock(spec=Customer)
        customer.id = 1
        customer.first_name = "TestFirst"
        customer.last_name = "TestLast"
        customer.company_name = "Test Corp"
        customer.sales_representative = mock_sales_representatives[0]
        customer.contacts = [mock_contacts_list[0]]

        customer_data = customer_to_dict(customer)

        screen = UpdateCustomerScreen(
            customer_data=customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#customer_last_name", UpdateCustomerScreen
            )
            first_name_input = app.query_one(
                "#customer_first_name", UpdateCustomerScreen
            )
            company_name_input = app.query_one(
                "#company_name", UpdateCustomerScreen
            )

            await app.pilot.pause()
            assert last_name_input.value == "TestLast"
            assert first_name_input.value == "TestFirst"
            assert company_name_input.value == "Test Corp"

    @pytest.mark.asyncio
    async def test_sales_representative_select_has_all_options(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Sales representative Select should have all options."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            select = app.query_one(
                "#update-customer-sales-representative-select",
                UpdateCustomerScreen,
            )
            await app.pilot.click(select)
            await app.pilot.pause()
            assert len(select._options) == 2

    # --- 3.4 Form Validation Tests ---
    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(
        self, app, mock_contacts_list, mock_sales_representatives
    ):
        """Form should be invalid when required fields are empty."""
        # Create empty customer data
        empty_data = {
            "customer_id": 1,
            "customer_first_name": "",
            "customer_last_name": "",
            "company_name": "",
            "customer_contacts": [],
            "customer_sales_representative": None,
        }
        screen = UpdateCustomerScreen(
            customer_data=empty_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_when_all_fields_filled(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Form should be valid when all required fields are filled."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is True

    # --- 3.5 Form Submission Tests ---
    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_updated_data(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Update button should dismiss with updated customer data."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            # Modify some fields
            last_name_input = app.query_one(
                "#customer_last_name", UpdateCustomerScreen
            )
            last_name_input.value = "UpdatedLast"
            first_name_input = app.query_one(
                "#customer_first_name", UpdateCustomerScreen
            )
            first_name_input.value = "UpdatedFirst"

            await app.pilot.pause()

            update_btn = app.query_one("#update", UpdateCustomerScreen)
            await app.pilot.click(update_btn)
            await app.pilot.pause()

            assert dismissed["id"] == 1
            assert dismissed["customer_last_name"] == "UpdatedLast"
            assert dismissed["customer_first_name"] == "UpdatedFirst"
            assert dismissed["company_name"] == "Acme Corp"

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """Cancel button should dismiss with None."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            cancel_btn = app.query_one("#cancel", UpdateCustomerScreen)
            await app.pilot.click(cancel_btn)
            await app.pilot.pause()
            assert dismissed is None

    # --- 3.6 SelectionList Behavior Tests ---
    @pytest.mark.asyncio
    async def test_selection_list_allows_multiple_selection(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """SelectionList should allow multiple contact selection."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            selection_list = app.query_one(
                "#update-customer-contacts-selection-list",
                UpdateCustomerScreen,
            )
            await app.pilot.pause()

            # Click on first contact
            await app.pilot.click(selection_list, row=0)
            await app.pilot.pause()

            # Click on second contact
            await app.pilot.click(selection_list, row=1)
            await app.pilot.pause()

            # Both should be selected
            assert len(selection_list._selected) == 2

    # --- 3.7 on_mount Tests ---
    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(
        self,
        app,
        mock_customer_data,
        mock_contacts_list,
        mock_sales_representatives,
    ):
        """on_mount should set container border titles and subtitles."""
        screen = UpdateCustomerScreen(
            customer_data=mock_customer_data,
            contacts=mock_contacts_list,
            sales_representatives=mock_sales_representatives,
        )
        async with app.run_test(screen):
            await app.pilot.pause()
            assert (
                screen.query_one("#update-customer-data").border_title
                == "Personal Data"
            )
            assert (
                screen.query_one("#update-customer-data").border_subtitle
                == "Edit relevant fields"
            )
            assert (
                screen.query_one(
                    "#update-customer-sales-representative"
                ).border_title
                == "Sales Representative Selection"
            )
            assert (
                screen.query_one("#update-contact-data").border_title
                == "Assigned Contacts"
            )
            assert (
                screen.query_one("#update-contact-data").border_subtitle
                == "Click on contact to assign/unassign"
            )


# =============================================================================
# 4. CREATE CONTACT SCREEN TESTS
# =============================================================================


class TestCreateContactScreen:
    """Tests for CreateContactScreen."""

    # --- 4.1 Initialization Tests ---
    def test_init_default_values(self):
        """__init__ should initialize default values."""
        screen = CreateContactScreen()
        assert screen.contact_data == {}
        assert screen.phone_number_counter == 2

    # --- 4.2 UI Structure Tests ---
    @pytest.mark.asyncio
    async def test_header_exists(self, app):
        """Header should exist with SUB_TITLE='CREATE CONTACT'."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            header = app.query_one("Header")
            assert header is not None

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(self, app):
        """All contact input fields should exist."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            email_input = app.query_one(
                "#contact_email", CreateContactScreen
            )
            phone_input = app.query_one(
                "#phone_number_1", CreateContactScreen
            )
            assert last_name_input is not None
            assert first_name_input is not None
            assert email_input is not None
            assert phone_input is not None

    @pytest.mark.asyncio
    async def test_add_phone_number_button_exists(self, app):
        """Add phone number button should exist."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            btn = app.query_one("#add-phone-number", CreateContactScreen)
            assert btn is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(self, app):
        """Create and Cancel buttons should exist."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            create_btn = app.query_one("#create", CreateContactScreen)
            cancel_btn = app.query_one("#cancel", CreateContactScreen)
            assert create_btn is not None
            assert cancel_btn is not None

    # --- 4.3 Dynamic Phone Numbers Tests ---
    @pytest.mark.asyncio
    async def test_add_phone_number_button_adds_new_field(self, app):
        """Clicking add phone number should add a new input field."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            btn = app.query_one("#add-phone-number", CreateContactScreen)
            initial_phones = app.query(
                "Input[id^='#phone_number_']", CreateContactScreen
            )
            initial_count = len(initial_phones)

            await app.pilot.click(btn)
            await app.pilot.pause()

            new_phones = app.query(
                "Input[id^='#phone_number_']", CreateContactScreen
            )
            assert len(new_phones) == initial_count + 1
            assert (
                app.query_one("#phone_number_2", CreateContactScreen)
                is not None
            )

    @pytest.mark.asyncio
    async def test_phone_number_counter_increments(self, app):
        """phone_number_counter should increment when adding new fields."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            assert screen.phone_number_counter == 2

            btn = app.query_one("#add-phone-number", CreateContactScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()

            assert screen.phone_number_counter == 3

    # --- 4.4 Form Validation Tests ---
    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self, app):
        """Form should be invalid when all fields are empty."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is False
            create_btn = app.query_one("#create", CreateContactScreen)
            assert create_btn.disabled

    @pytest.mark.asyncio
    async def test_required_fields_validation(self, app):
        """last_name, first_name, and email should be required."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            # Fill only some fields
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            last_name_input.value = "TestLast"
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            first_name_input.value = "TestFirst"
            # email is empty

            await app.pilot.pause()
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_phone_numbers_required(self, app):
        """Each phone number should be required."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            # Fill all required fields
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            last_name_input.value = "TestLast"
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            first_name_input.value = "TestFirst"
            email_input = app.query_one(
                "#contact_email", CreateContactScreen
            )
            email_input.value = "test@example.com"
            # phone_number_1 is empty

            await app.pilot.pause()
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_when_all_fields_filled(self, app):
        """Form should be valid when all required fields are filled."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            # Fill all required fields
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            last_name_input.value = "TestLast"
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            first_name_input.value = "TestFirst"
            email_input = app.query_one(
                "#contact_email", CreateContactScreen
            )
            email_input.value = "test@example.com"
            phone_input = app.query_one(
                "#phone_number_1", CreateContactScreen
            )
            phone_input.value = "1234567890"

            await app.pilot.pause()
            assert screen.is_form_valid is True

    @pytest.mark.asyncio
    async def test_validation_updates_on_new_phone_number(self, app):
        """Validation should update when new phone number field is added."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            # Fill all fields including first phone
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            last_name_input.value = "TestLast"
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            first_name_input.value = "TestFirst"
            email_input = app.query_one(
                "#contact_email", CreateContactScreen
            )
            email_input.value = "test@example.com"
            phone_input = app.query_one(
                "#phone_number_1", CreateContactScreen
            )
            phone_input.value = "1234567890"

            await app.pilot.pause()
            assert screen.is_form_valid is True

            # Add new phone number field
            btn = app.query_one("#add-phone-number", CreateContactScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()

            # Form should now be invalid because new phone field is empty
            assert screen.is_form_valid is False

    # --- 4.5 Form Submission Tests ---
    @pytest.mark.asyncio
    async def test_create_button_dismisses_with_form_data(self, app):
        """Create button should dismiss with contact data."""
        screen = CreateContactScreen()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            # Fill all fields
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            last_name_input.value = "Smith"
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            first_name_input.value = "Alice"
            email_input = app.query_one(
                "#contact_email", CreateContactScreen
            )
            email_input.value = "alice@example.com"
            phone_input = app.query_one(
                "#phone_number_1", CreateContactScreen
            )
            phone_input.value = "1234567890"

            await app.pilot.pause()
            create_btn = app.query_one("#create", CreateContactScreen)
            await app.pilot.click(create_btn)
            await app.pilot.pause()

            assert dismissed == {
                "contact_last_name": "Smith",
                "contact_first_name": "Alice",
                "email": "alice@example.com",
                "phone_numbers": ["1234567890"],
            }

    @pytest.mark.asyncio
    async def test_create_button_with_multiple_phones(self, app):
        """Create button should include all phone numbers."""
        screen = CreateContactScreen()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            # Fill all fields
            last_name_input = app.query_one(
                "#contact_last_name", CreateContactScreen
            )
            last_name_input.value = "Smith"
            first_name_input = app.query_one(
                "#contact_first_name", CreateContactScreen
            )
            first_name_input.value = "Alice"
            email_input = app.query_one(
                "#contact_email", CreateContactScreen
            )
            email_input.value = "alice@example.com"
            phone_input = app.query_one(
                "#phone_number_1", CreateContactScreen
            )
            phone_input.value = "1234567890"

            # Add second phone
            add_btn = app.query_one(
                "#add-phone-number", CreateContactScreen
            )
            await app.pilot.click(add_btn)
            await app.pilot.pause()

            phone_input_2 = app.query_one(
                "#phone_number_2", CreateContactScreen
            )
            phone_input_2.value = "0987654321"

            await app.pilot.pause()
            create_btn = app.query_one("#create", CreateContactScreen)
            await app.pilot.click(create_btn)
            await app.pilot.pause()

            assert dismissed["phone_numbers"] == [
                "1234567890",
                "0987654321",
            ]

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(self, app):
        """Cancel button should dismiss with None."""
        screen = CreateContactScreen()
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            cancel_btn = app.query_one("#cancel", CreateContactScreen)
            await app.pilot.click(cancel_btn)
            await app.pilot.pause()
            assert dismissed is None

    # --- 4.6 on_mount Tests ---
    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(self, app):
        """on_mount should set container border titles."""
        screen = CreateContactScreen()
        async with app.run_test(screen):
            await app.pilot.pause()
            assert (
                screen.query_one("#contact-data").border_title
                == "Personal Data"
            )
            assert (
                screen.query_one("#phone-number").border_title
                == "Phone Numbers"
            )


# =============================================================================
# 5. UPDATE CONTACT SCREEN TESTS
# =============================================================================


class TestUpdateContactScreen:
    """Tests for UpdateContactScreen."""

    # --- 5.1 Initialization Tests ---
    def test_init_sets_contact_data(self, mock_contact_data):
        """__init__ should store contact_data."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        assert screen.contact_data == mock_contact_data

    def test_init_sets_phone_number_counter(self, mock_contact_data):
        """__init__ should set phone_number_counter based on existing phones."""
        # mock_contact_data has 2 phone numbers
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        assert (
            screen.phone_number_counter == 3
        )  # Starts after existing phones

    # --- 5.2 UI Structure Tests ---
    @pytest.mark.asyncio
    async def test_header_exists(self, app, mock_contact_data):
        """Header should exist with SUB_TITLE='UPDATE CONTACT'."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            header = app.query_one("Header")
            assert header is not None

    @pytest.mark.asyncio
    async def test_updating_contact_static_exists(
        self, app, mock_contact_data
    ):
        """Static with updating contact message should exist."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            static = app.query_one("Static")
            assert static is not None
            assert "Updating Contact" in str(static)

    @pytest.mark.asyncio
    async def test_all_input_fields_exist(self, app, mock_contact_data):
        """All input fields should exist."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#contact_last_name", UpdateContactScreen
            )
            first_name_input = app.query_one(
                "#contact_first_name", UpdateContactScreen
            )
            email_input = app.query_one(
                "#contact_email", UpdateContactScreen
            )
            assert last_name_input is not None
            assert first_name_input is not None
            assert email_input is not None

    @pytest.mark.asyncio
    async def test_phone_number_fields_exist(self, app, mock_contact_data):
        """Phone number input fields should exist for existing numbers."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            # Should have phone_number_1 and phone_number_2 for the 2 existing numbers
            phone_1 = app.query_one("#phone_number_1", UpdateContactScreen)
            phone_2 = app.query_one("#phone_number_2", UpdateContactScreen)
            assert phone_1 is not None
            assert phone_2 is not None

    @pytest.mark.asyncio
    async def test_add_phone_number_button_exists(
        self, app, mock_contact_data
    ):
        """Add phone number button should exist."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            btn = app.query_one("#add-phone-number", UpdateContactScreen)
            assert btn is not None

    @pytest.mark.asyncio
    async def test_buttons_exist(self, app, mock_contact_data):
        """Update and Cancel buttons should exist."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            update_btn = app.query_one("#update", UpdateContactScreen)
            cancel_btn = app.query_one("#cancel", UpdateContactScreen)
            assert update_btn is not None
            assert cancel_btn is not None

    # --- 5.3 Prefill Tests ---
    @pytest.mark.asyncio
    async def test_inputs_prefilled_with_contact_data(
        self, app, contact_to_dict
    ):
        """Input fields should be prefilled with contact data."""
        contact = MagicMock(spec=Contact)
        contact.id = 1
        contact.first_name = "TestFirst"
        contact.last_name = "TestLast"
        contact.email = "test@example.com"
        phone1 = MagicMock(spec=PhoneNumber)
        phone1.number = "1234567890"
        phone2 = MagicMock(spec=PhoneNumber)
        phone2.number = "0987654321"
        contact.phone_numbers = [phone1, phone2]

        contact_data = contact_to_dict(contact)

        screen = UpdateContactScreen(contact_data=contact_data)
        async with app.run_test(screen):
            last_name_input = app.query_one(
                "#contact_last_name", UpdateContactScreen
            )
            first_name_input = app.query_one(
                "#contact_first_name", UpdateContactScreen
            )
            email_input = app.query_one(
                "#contact_email", UpdateContactScreen
            )

            await app.pilot.pause()
            assert last_name_input.value == "TestLast"
            assert first_name_input.value == "TestFirst"
            assert email_input.value == "test@example.com"

    @pytest.mark.asyncio
    async def test_phone_numbers_prefilled(self, app, contact_to_dict):
        """Phone number fields should be prefilled."""
        contact = MagicMock(spec=Contact)
        contact.id = 1
        contact.first_name = "Alice"
        contact.last_name = "Smith"
        contact.email = "alice@example.com"
        phone1 = MagicMock(spec=PhoneNumber)
        phone1.number = "1234567890"
        phone2 = MagicMock(spec=PhoneNumber)
        phone2.number = "0987654321"
        contact.phone_numbers = [phone1, phone2]

        contact_data = contact_to_dict(contact)

        screen = UpdateContactScreen(contact_data=contact_data)
        async with app.run_test(screen):
            phone_1 = app.query_one("#phone_number_1", UpdateContactScreen)
            phone_2 = app.query_one("#phone_number_2", UpdateContactScreen)

            await app.pilot.pause()
            assert phone_1.value == "1234567890"
            assert phone_2.value == "0987654321"

    # --- 5.4 Dynamic Phone Numbers Tests ---
    @pytest.mark.asyncio
    async def test_add_phone_number_button_adds_new_field(
        self, app, mock_contact_data
    ):
        """Clicking add phone number should add a new input field."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            btn = app.query_one("#add-phone-number", UpdateContactScreen)
            initial_phones = app.query(
                "Input[id^='#phone_number_']", UpdateContactScreen
            )
            initial_count = len(initial_phones)

            await app.pilot.click(btn)
            await app.pilot.pause()

            new_phones = app.query(
                "Input[id^='#phone_number_']", UpdateContactScreen
            )
            assert len(new_phones) == initial_count + 1
            assert (
                app.query_one("#phone_number_3", UpdateContactScreen)
                is not None
            )

    @pytest.mark.asyncio
    async def test_new_phone_number_fields_are_empty(
        self, app, mock_contact_data
    ):
        """New phone number fields should be empty."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            btn = app.query_one("#add-phone-number", UpdateContactScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()

            new_phone = app.query_one(
                "#phone_number_3", UpdateContactScreen
            )
            assert new_phone.value == ""

    # --- 5.5 Form Validation Tests ---
    @pytest.mark.asyncio
    async def test_form_invalid_when_empty(self, app):
        """Form should be invalid when required fields are empty."""
        empty_data = {
            "contact_id": 1,
            "contact_first_name": "",
            "contact_last_name": "",
            "email": "",
            "phone_numbers": [""],
        }
        screen = UpdateContactScreen(contact_data=empty_data)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_required_fields_validation(
        self, app, mock_contact_data
    ):
        """last_name, first_name, and email should be required."""
        # Clear required fields
        mock_contact_data["contact_first_name"] = ""
        mock_contact_data["contact_last_name"] = ""
        mock_contact_data["email"] = ""

        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_phone_numbers_validation(self, app, mock_contact_data):
        """Each phone number should be required."""
        # Clear one phone number
        mock_contact_data["phone_numbers"] = ["", "0987654321"]

        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is False

    @pytest.mark.asyncio
    async def test_form_valid_when_all_fields_filled(
        self, app, mock_contact_data
    ):
        """Form should be valid when all required fields are filled."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert screen.is_form_valid is True

    # --- 5.6 Form Submission Tests ---
    @pytest.mark.asyncio
    async def test_update_button_dismisses_with_updated_data(
        self, app, mock_contact_data
    ):
        """Update button should dismiss with updated contact data."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            # Modify some fields
            last_name_input = app.query_one(
                "#contact_last_name", UpdateContactScreen
            )
            last_name_input.value = "UpdatedLast"
            first_name_input = app.query_one(
                "#contact_first_name", UpdateContactScreen
            )
            first_name_input.value = "UpdatedFirst"

            await app.pilot.pause()

            update_btn = app.query_one("#update", UpdateContactScreen)
            await app.pilot.click(update_btn)
            await app.pilot.pause()

            assert dismissed["id"] == 1
            assert dismissed["last_name"] == "UpdatedLast"
            assert dismissed["first_name"] == "UpdatedFirst"
            assert dismissed["email"] == "alice.smith@example.com"

    @pytest.mark.asyncio
    async def test_update_button_with_new_phone_numbers(
        self, app, mock_contact_data
    ):
        """Update button should include all phone numbers including new ones."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            # Add new phone number
            btn = app.query_one("#add-phone-number", UpdateContactScreen)
            await app.pilot.click(btn)
            await app.pilot.pause()

            new_phone = app.query_one(
                "#phone_number_3", UpdateContactScreen
            )
            new_phone.value = "5556667777"

            await app.pilot.pause()
            update_btn = app.query_one("#update", UpdateContactScreen)
            await app.pilot.click(update_btn)
            await app.pilot.pause()

            assert dismissed["phone_numbers"] == [
                "1234567890",
                "0987654321",
                "5556667777",
            ]

    @pytest.mark.asyncio
    async def test_cancel_button_dismisses_with_none(
        self, app, mock_contact_data
    ):
        """Cancel button should dismiss with None."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        dismissed = None

        async def on_dismiss(result):
            nonlocal dismissed
            dismissed = result

        async with app.run_test(screen, on_dismiss=on_dismiss):
            cancel_btn = app.query_one("#cancel", UpdateContactScreen)
            await app.pilot.click(cancel_btn)
            await app.pilot.pause()
            assert dismissed is None

    # --- 5.7 on_mount Tests ---
    @pytest.mark.asyncio
    async def test_on_mount_sets_container_titles(
        self, app, mock_contact_data
    ):
        """on_mount should set container border titles and subtitles."""
        screen = UpdateContactScreen(contact_data=mock_contact_data)
        async with app.run_test(screen):
            await app.pilot.pause()
            assert (
                screen.query_one("#update-contact-data").border_title
                == "Personal Data"
            )
            assert (
                screen.query_one("#update-contact-data").border_subtitle
                == "Edit relevant fields"
            )
            assert (
                screen.query_one("#update-phone-number").border_title
                == "Phone Numbers"
            )
            assert (
                screen.query_one("#update-phone-number").border_subtitle
                == "Edit relevant fields"
            )
