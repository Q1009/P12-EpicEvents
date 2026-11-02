"""
Tests for customer_controller.py

Unit tests for CustomerController class covering:
- Initialization and configuration
- Database query methods (customers, contacts, sales representatives)
- Screen navigation
- User choice handling
- CRUD operations (create/update customers and contacts)
- Callback and error handling
- Authentication decorator integration
- Many-to-Many relationship management (Customer <-> Contact)

Run with: pytest customers/tests/test_customer_controller.py -v
"""

from unittest.mock import ANY, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
)
from contracts.contract_model import Contract  # noqa: F401
from customers.customer_controller import CustomerController
from customers.customer_model import Contact, Customer, PhoneNumber
from events.event_model import Event  # noqa: F401
from services.authentication_services import AuthenticationError

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_app():
    """Mock Textual App for testing."""
    app = MagicMock()
    return app


@pytest.fixture
def mock_session():
    """Mock SQLAlchemy Session for testing."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_customer():
    """Mock Customer object."""
    customer = MagicMock(spec=Customer)
    customer.id = 1
    customer.first_name = "John"
    customer.last_name = "Doe"
    customer.company_name = "Acme Corp"
    customer.sales_representative_id = 1
    customer.sales_representative = MagicMock(spec=Collaborator)
    customer.sales_representative.id = 1
    customer.contacts = []
    return customer


@pytest.fixture
def mock_customer_with_contacts(mock_contact):
    """Mock Customer object with contacts."""
    customer = MagicMock(spec=Customer)
    customer.id = 1
    customer.first_name = "John"
    customer.last_name = "Doe"
    customer.company_name = "Acme Corp"
    customer.sales_representative_id = 1
    customer.sales_representative = MagicMock(spec=Collaborator)
    customer.sales_representative.id = 1
    customer.contacts = [mock_contact]
    return customer


@pytest.fixture
def mock_contact():
    """Mock Contact object."""
    contact = MagicMock(spec=Contact)
    contact.id = 1
    contact.first_name = "Alice"
    contact.last_name = "Smith"
    contact.email = "alice.smith@example.com"
    # contact.phone_numbers = []
    # contact.customers = []
    return contact


@pytest.fixture
def mock_contact_with_phones():
    """Mock Contact object with phone numbers."""
    contact = MagicMock(spec=Contact)
    contact.id = 1
    contact.first_name = "Alice"
    contact.last_name = "Smith"
    contact.email = "alice.smith@example.com"
    phone1 = MagicMock(spec=PhoneNumber)
    phone1.id = 1
    phone1.number = "1234567890"
    phone2 = MagicMock(spec=PhoneNumber)
    phone2.id = 2
    phone2.number = "0987654321"
    contact.phone_numbers = [phone1, phone2]
    contact.customers = []
    return contact


@pytest.fixture
def mock_phone_number():
    """Mock PhoneNumber object."""
    phone = MagicMock(spec=PhoneNumber)
    phone.id = 1
    phone.number = "1234567890"
    phone.contact_id = 1
    return phone


@pytest.fixture
def mock_sales_collaborator():
    """Mock Collaborator object from SALES department."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 1
    collaborator.first_name = "Sales"
    collaborator.last_name = "Rep1"
    collaborator.department = MagicMock(spec=Department)
    collaborator.department.name = DepartmentName.SALES
    return collaborator


@pytest.fixture
def mock_admin_collaborator():
    """Mock Collaborator object from ADMIN department."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 2
    collaborator.first_name = "Admin"
    collaborator.last_name = "User"
    collaborator.department = MagicMock(spec=Department)
    collaborator.department.name = DepartmentName.ADMIN
    return collaborator


# =============================================================================
# 1. INITIALIZATION TESTS
# =============================================================================


class TestCustomerControllerInitialization:
    """Tests for CustomerController initialization and start method."""

    def test_init_sets_attributes(self, mock_app, mock_session):
        """__init__ should store epic_events_app and session."""
        controller = CustomerController(mock_app, mock_session)
        assert controller.epic_events_app == mock_app
        assert controller.session == mock_session

    def test_init_sets_callbacks_to_none(self, mock_app, mock_session):
        """__init__ should initialize on_back_callback to None."""
        controller = CustomerController(mock_app, mock_session)
        assert controller.on_back_callback is None

    def test_start_stores_callbacks(self, mock_app, mock_session):
        """start() should store on_back_callback."""
        controller = CustomerController(mock_app, mock_session)
        on_back = MagicMock()
        controller.start(on_back=on_back)
        assert controller.on_back_callback == on_back

    @patch(
        "customers.customer_controller.CustomerController.get_all_customers"
    )
    @patch(
        "customers.customer_controller.CustomerController.push_customer_screen"
    )
    def test_start_with_customer_id(
        self,
        mock_push,
        mock_get_all,
        mock_app,
        mock_session,
        mock_customer,
    ):
        """start() should push CustomerScreen with customers and customer_id."""
        mock_customers = [mock_customer]
        mock_get_all.return_value = mock_customers
        controller = CustomerController(mock_app, mock_session)
        controller.start(customer_id=1)

        mock_get_all.assert_called_once()
        mock_push.assert_called_once_with(
            customers=mock_customers, customer_id=1
        )

    @patch(
        "customers.customer_controller.CustomerController.get_all_customers"
    )
    @patch(
        "customers.customer_controller.CustomerController.push_customer_screen"
    )
    def test_start_without_customer_id(
        self,
        mock_push,
        mock_get_all,
        mock_app,
        mock_session,
        mock_customer,
    ):
        """start() should push CustomerScreen with customers."""
        mock_customers = [mock_customer]
        mock_get_all.return_value = mock_customers
        controller = CustomerController(mock_app, mock_session)
        controller.start()

        mock_get_all.assert_called_once()
        mock_push.assert_called_once_with(
            customers=mock_customers, customer_id=None
        )


# =============================================================================
# 2. DATABASE QUERY TESTS
# =============================================================================


class TestCustomerControllerDatabaseQueries:
    """Tests for database query methods."""

    def test_get_all_customers_returns_list(
        self, mock_session, mock_app, mock_customer
    ):
        """get_all_customers() should return list of customers with eager loading."""
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_query.options.return_value = mock_options
        mock_options.all.return_value = [mock_customer]
        mock_session.query.return_value = mock_query

        controller = CustomerController(mock_app, mock_session)
        customers = controller.get_all_customers()

        assert customers == [mock_customer]
        mock_session.query.assert_called_once_with(Customer)
        mock_query.options.assert_called_once()

    def test_get_sales_representatives_returns_sales_only(
        self, mock_session, mock_app, mock_sales_collaborator
    ):
        """get_sales_representatives() should return only SALES department collaborators."""
        mock_query = MagicMock()
        mock_join = MagicMock()
        mock_filter = MagicMock()
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.all.return_value = [mock_sales_collaborator]
        mock_session.query.return_value = mock_query

        controller = CustomerController(mock_app, mock_session)
        sales_reps = controller.get_sales_representatives()

        assert sales_reps == [mock_sales_collaborator]
        mock_session.query.assert_called_once_with(Collaborator)
        mock_query.join.assert_called_once_with(Collaborator.department)
        mock_join.filter.assert_called_once()

    def test_get_customers_by_sales_rep_id_returns_list(
        self, mock_session, mock_app, mock_customer
    ):
        """get_customers_by_sales_rep_id() should filter by sales_representative_id."""
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = [mock_customer]
        mock_session.query.return_value = mock_query

        controller = CustomerController(mock_app, mock_session)
        customers = controller.get_customers_by_sales_rep_id(1)

        assert customers == [mock_customer]
        mock_session.query.assert_called_once_with(Customer)
        mock_query.filter.assert_called_once()
        mock_filter.all.assert_called_once()

    def test_get_customers_without_sales_rep_returns_list(
        self, mock_session, mock_app, mock_customer
    ):
        """get_customers_without_sales_rep() should filter by NULL sales_representative_id."""
        mock_customer.sales_representative_id = None
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = [mock_customer]
        mock_session.query.return_value = mock_query

        controller = CustomerController(mock_app, mock_session)
        customers = controller.get_customers_without_sales_rep()

        assert customers == [mock_customer]
        mock_session.query.assert_called_once_with(Customer)
        mock_query.filter.assert_called_once()
        # Verify the filter is for NULL
        filter_args = mock_query.filter.call_args[0]
        assert str(filter_args[0]).endswith("IS NULL")

    def test_get_all_contacts_returns_list(
        self, mock_session, mock_app, mock_contact
    ):
        """get_all_contacts() should return list of contacts."""
        mock_session.query.return_value.all.return_value = [mock_contact]

        controller = CustomerController(mock_app, mock_session)
        contacts = controller.get_all_contacts()

        assert contacts == [mock_contact]
        mock_session.query.assert_called_once_with(Contact)

    def test_load_customer_data_for_update_returns_dict(
        self,
        mock_session,
        mock_app,
        mock_customer_with_contacts,
        mock_contact,
    ):
        """load_customer_data_for_update() should return customer data as dict."""
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_customer_with_contacts
        mock_session.query.return_value = mock_query

        controller = CustomerController(mock_app, mock_session)
        result = controller.load_customer_data_for_update(1)

        assert result == {
            "customer_id": 1,
            "customer_first_name": "John",
            "customer_last_name": "Doe",
            "company_name": "Acme Corp",
            "customer_contacts": [mock_contact],
            "customer_sales_representative": mock_customer_with_contacts.sales_representative,
        }
        mock_query.filter.assert_called_once()

    def test_load_contact_data_for_update_returns_dict(
        self, mock_session, mock_app, mock_contact_with_phones
    ):
        """load_contact_data_for_update() should return contact data as dict."""
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_filter = MagicMock()
        mock_query.options.return_value = mock_options
        mock_options.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_contact_with_phones
        mock_session.query.return_value = mock_query

        controller = CustomerController(mock_app, mock_session)
        result = controller.load_contact_data_for_update(1)

        assert result == {
            "contact_id": 1,
            "contact_first_name": "Alice",
            "contact_last_name": "Smith",
            "email": "alice.smith@example.com",
            "phone_numbers": ["1234567890", "0987654321"],
        }
        mock_session.query.assert_called_once_with(Contact)


# =============================================================================
# 3. SCREEN NAVIGATION TESTS
# =============================================================================


class TestCustomerControllerScreenNavigation:
    """Tests for screen navigation methods."""

    @patch("customers.customer_controller.CustomerScreen")
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_push_customer_screen_calls_push_screen(
        self,
        mock_get_user,
        mock_customer_screen,
        mock_app,
        mock_session,
        mock_customer,
        mock_sales_collaborator,
    ):
        """push_customer_screen() should push CustomerScreen with correct parameters."""
        mock_get_user.return_value = mock_sales_collaborator
        mock_screen_instance = MagicMock()
        mock_customer_screen.return_value = mock_screen_instance

        controller = CustomerController(mock_app, mock_session)
        CustomerController.push_customer_screen.__wrapped__(
            controller,
            customers=[mock_customer],
            customer_id=1,
        )

        mock_get_user.assert_called_once_with(mock_session)
        mock_customer_screen.assert_called_once_with(
            customers=[mock_customer],
            user=mock_sales_collaborator,
            customer_id=1,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.handle_user_choice
        )

    @patch("customers.customer_controller.CreateCustomerScreen")
    @patch(
        "customers.customer_controller.CustomerController.get_all_contacts"
    )
    def test_push_create_customer_screen(
        self,
        mock_get_contacts,
        mock_create_screen,
        mock_app,
        mock_session,
        mock_contact,
    ):
        """push_create_customer_screen() should push CreateCustomerScreen with contacts."""
        mock_get_contacts.return_value = [mock_contact]
        mock_screen_instance = MagicMock()
        mock_create_screen.return_value = mock_screen_instance

        controller = CustomerController(mock_app, mock_session)
        CustomerController.push_create_customer_screen.__wrapped__(
            controller
        )

        mock_get_contacts.assert_called_once()
        mock_create_screen.assert_called_once_with(contacts=[mock_contact])
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.create_customer
        )

    @patch("customers.customer_controller.UpdateCustomerScreen")
    @patch(
        "customers.customer_controller.CustomerController.get_all_contacts"
    )
    @patch(
        "customers.customer_controller.CustomerController.get_sales_representatives"
    )
    @patch(
        "customers.customer_controller.CustomerController.load_customer_data_for_update"
    )
    def test_push_update_customer_screen(
        self,
        mock_load_data,
        mock_get_sales_reps,
        mock_get_contacts,
        mock_update_screen,
        mock_app,
        mock_session,
        mock_customer,
        mock_contact,
        mock_sales_collaborator,
    ):
        """push_update_customer_screen() should push UpdateCustomerScreen with customer data."""
        mock_get_contacts.return_value = [mock_contact]
        mock_get_sales_reps.return_value = [mock_sales_collaborator]
        mock_screen_instance = MagicMock()
        mock_update_screen.return_value = mock_screen_instance
        mock_customer_data = {
            "customer_id": 1,
            "customer_first_name": "John",
            "customer_last_name": "Doe",
            "company_name": "Acme Corp",
            "customer_contacts": [mock_contact],
            "customer_sales_representative": mock_sales_collaborator,
        }
        mock_load_data.return_value = mock_customer_data

        controller = CustomerController(mock_app, mock_session)
        CustomerController.push_update_customer_screen.__wrapped__(
            controller, customer_id=1
        )

        mock_get_contacts.assert_called_once()
        mock_get_sales_reps.assert_called_once()
        mock_load_data.assert_called_once_with(1)
        mock_update_screen.assert_called_once_with(
            customer_data=mock_customer_data,
            contacts=[mock_contact],
            sales_representatives=[mock_sales_collaborator],
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.update_customer
        )

    @patch("customers.customer_controller.CreateContactScreen")
    def test_push_create_contact_screen(
        self, mock_create_screen, mock_app, mock_session
    ):
        """push_create_contact_screen() should push CreateContactScreen."""
        mock_screen_instance = MagicMock()
        mock_create_screen.return_value = mock_screen_instance

        controller = CustomerController(mock_app, mock_session)
        CustomerController.push_create_contact_screen.__wrapped__(
            controller
        )

        mock_create_screen.assert_called_once()
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.create_contact
        )

    @patch("customers.customer_controller.UpdateContactScreen")
    @patch(
        "customers.customer_controller.CustomerController.load_contact_data_for_update"
    )
    def test_push_update_contact_screen(
        self,
        mock_load_data,
        mock_update_screen,
        mock_app,
        mock_session,
        mock_contact_with_phones,
    ):
        """push_update_contact_screen() should push UpdateContactScreen with contact data."""
        mock_screen_instance = MagicMock()
        mock_update_screen.return_value = mock_screen_instance
        mock_contact_data = {
            "contact_id": 1,
            "contact_first_name": "Alice",
            "contact_last_name": "Smith",
            "email": "alice.smith@example.com",
            "phone_numbers": ["1234567890", "0987654321"],
        }
        mock_load_data.return_value = mock_contact_data

        controller = CustomerController(mock_app, mock_session)
        CustomerController.push_update_contact_screen.__wrapped__(
            controller, contact_id=1
        )

        mock_load_data.assert_called_once_with(1)
        mock_update_screen.assert_called_once_with(
            contact_data=mock_contact_data
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.update_contact
        )


# =============================================================================
# 4. USER CHOICE HANDLING TESTS
# =============================================================================


class TestCustomerControllerUserChoiceHandling:
    """Tests for handle_user_choice method."""

    @patch(
        "customers.customer_controller.CustomerController.push_create_customer_screen"
    )
    def test_handle_create_customer_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_create_customer_screen for 'create_customer'."""
        controller = CustomerController(mock_app, mock_session)
        controller.handle_user_choice("create_customer")
        mock_push.assert_called_once()

    @patch(
        "customers.customer_controller.CustomerController.push_update_customer_screen"
    )
    def test_handle_update_customer_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_update_customer_screen for ('update_customer', id)."""
        controller = CustomerController(mock_app, mock_session)
        controller.handle_user_choice(("update_customer", 1))
        mock_push.assert_called_once_with(customer_id=1)

    @patch(
        "customers.customer_controller.CustomerController.push_create_contact_screen"
    )
    def test_handle_create_contact_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_create_contact_screen for 'create_contact'."""
        controller = CustomerController(mock_app, mock_session)
        controller.handle_user_choice("create_contact")
        mock_push.assert_called_once()

    @patch(
        "customers.customer_controller.CustomerController.push_update_contact_screen"
    )
    def test_handle_update_contact_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_update_contact_screen for ('update_contact', id)."""
        controller = CustomerController(mock_app, mock_session)
        controller.handle_user_choice(("update_contact", 1))
        mock_push.assert_called_once_with(contact_id=1)

    def test_handle_back_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_back_callback for 'back'."""
        callback = MagicMock()
        controller = CustomerController(mock_app, mock_session)
        controller.on_back_callback = callback
        controller.handle_user_choice("back")
        callback.assert_called_once()

    def test_handle_back_choice_no_callback(self, mock_app, mock_session):
        """handle_user_choice should not fail if on_back_callback is None."""
        controller = CustomerController(mock_app, mock_session)
        controller.on_back_callback = None
        controller.handle_user_choice("back")

    def test_handle_quit_choice_exits_app(self, mock_app, mock_session):
        """handle_user_choice should call app.exit() for 'quit'."""
        controller = CustomerController(mock_app, mock_session)
        controller.handle_user_choice("quit")
        mock_app.exit.assert_called_once()


# =============================================================================
# 5. CRUD METHODS TESTS
# =============================================================================


class TestCustomerControllerBusinessLogic:
    """Tests for CRUD operations: create/update customers and contacts."""

    # --- Create Customer Tests ---
    @patch("customers.customer_controller.CustomerController.start")
    def test_create_customer_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """create_customer should notify and restart if cancelled."""
        controller = CustomerController(mock_app, mock_session)
        CustomerController.create_customer.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Customer creation cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(on_back=None)

    @patch("customers.customer_controller.PhoneNumber")
    @patch("customers.customer_controller.Customer")
    @patch("customers.customer_controller.CustomerController.start")
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_create_customer_success_with_new_contact(
        self,
        mock_get_user,
        mock_start,
        mock_customer_class,
        mock_phone_class,
        mock_app,
        mock_session,
        mock_sales_collaborator,
    ):
        """create_customer should create customer, contact, phone number, and associate them."""
        mock_get_user.return_value = mock_sales_collaborator
        mock_phone_instance = MagicMock(spec=PhoneNumber)
        mock_phone_class.return_value = mock_phone_instance
        mock_customer_instance = MagicMock(spec=Customer)
        mock_customer_class.return_value = mock_customer_instance
        mock_customer_instance.contacts = []

        new_customer_data = {
            "customer_first_name": "New",
            "customer_last_name": "Customer",
            "company_name": "New Corp",
            "customer_contact": {
                "first_name": "New",
                "last_name": "Contact",
                "email": "contact@newcorp.com",
                "phone_number": "1112223333",
            },
        }

        controller = CustomerController(mock_app, mock_session)
        CustomerController.create_customer.__wrapped__(
            controller, new_customer_data
        )

        # Verify the real Contact model was created and persisted
        mock_contact_instance = mock_session.add.call_args_list[0].args[0]
        assert isinstance(mock_contact_instance, Contact)
        assert mock_contact_instance.last_name == "Contact"
        assert mock_contact_instance.first_name == "New"
        assert mock_contact_instance.email == "contact@newcorp.com"

        # Verify PhoneNumber was created
        mock_phone_class.assert_called_once_with(
            number="1112223333", contact=mock_contact_instance
        )

        # Verify Customer was created
        mock_customer_class.assert_called_once_with(
            last_name="Customer",
            first_name="New",
            company_name="New Corp",
            sales_representative=mock_sales_collaborator,
        )

        # Verify contact was added to customer.contacts (many-to-many)
        mock_session.add.assert_any_call(mock_contact_instance)
        mock_session.add.assert_any_call(mock_phone_instance)
        mock_session.add.assert_any_call(mock_customer_instance)
        assert mock_customer_instance.contacts == [mock_contact_instance]

        # Verify session and notifications
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Customer successfully created", severity="information"
        )
        mock_start.assert_called_once_with(on_back=None)

    @patch("customers.customer_controller.CustomerController.start")
    def test_create_customer_with_existing_contact(
        self, mock_start, mock_app, mock_session
    ):
        """create_customer should use existing Contact without recreating it."""
        existing_contact = Contact(
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@example.com",
        )

        new_customer_data = {
            "customer_first_name": "New",
            "customer_last_name": "Customer",
            "company_name": "New Corp",
            "customer_contact": existing_contact,
        }

        controller = CustomerController(mock_app, mock_session)
        CustomerController.create_customer.__wrapped__(
            controller, new_customer_data
        )

        # Existing contacts are reused; only the new customer is added.
        mock_session.add.assert_called_once()
        customer = mock_session.add.call_args.args[0]
        assert isinstance(customer, Customer)
        assert customer.first_name == "New"
        assert customer.last_name == "Customer"
        assert customer.company_name == "New Corp"
        assert customer.contacts == [existing_contact]
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Customer successfully created", severity="information"
        )
        mock_start.assert_called_once_with(on_back=None)

    # --- Update Customer Tests ---
    @patch("customers.customer_controller.CustomerController.start")
    def test_update_customer_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """update_customer should notify and restart if cancelled."""
        controller = CustomerController(mock_app, mock_session)
        CustomerController.update_customer.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Customer update cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(on_back=None)

    @patch("customers.customer_controller.CustomerController.start")
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_update_customer_success(
        self,
        mock_get_user,
        mock_start,
        mock_app,
        mock_session,
        mock_customer,
        mock_sales_collaborator,
    ):
        """update_customer should update customer fields and contacts."""
        mock_get_user.return_value = mock_sales_collaborator
        mock_session.query.return_value.filter.return_value.first.return_value = mock_customer

        updated_customer_data = {
            "id": 1,
            "customer_first_name": "Updated",
            "customer_last_name": "Customer",
            "company_name": "Updated Corp",
            "customer_contacts": [],
            "customer_sales_representative": mock_sales_collaborator,
        }

        controller = CustomerController(mock_app, mock_session)
        controller.update_customer(updated_customer_data)

        # Verify the update was called with correct data
        update_call = (
            mock_session.query.return_value.filter.return_value.update
        )
        update_call.assert_called_once_with(
            {
                "first_name": "Updated",
                "last_name": "Customer",
                "company_name": "Updated Corp",
                "sales_representative_id": 1,
                "updated_at": ANY,
            }
        )

        # Verify contacts were updated (many-to-many)
        assert mock_customer.contacts == []

        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Customer successfully updated", severity="information"
        )
        mock_start.assert_called_once_with(on_back=None)

    # --- Create Contact Tests ---
    @patch("customers.customer_controller.Contact")
    @patch("customers.customer_controller.PhoneNumber")
    @patch("customers.customer_controller.CustomerController.start")
    def test_create_contact_success(
        self,
        mock_start,
        mock_phone_class,
        mock_contact_class,
        mock_app,
        mock_session,
    ):
        """create_contact should create contact with phone numbers."""
        mock_contact_instance = MagicMock(spec=Contact)
        mock_contact_class.return_value = mock_contact_instance
        mock_phone_instance1 = MagicMock(spec=PhoneNumber)
        mock_phone_instance2 = MagicMock(spec=PhoneNumber)
        mock_phone_class.side_effect = [
            mock_phone_instance1,
            mock_phone_instance2,
        ]

        new_contact_data = {
            "contact_first_name": "New",
            "contact_last_name": "Contact",
            "email": "new.contact@example.com",
            "phone_numbers": ["1112223333", "4445556666"],
        }

        controller = CustomerController(mock_app, mock_session)
        CustomerController.create_contact.__wrapped__(
            controller, new_contact_data
        )

        # Verify Contact was created
        mock_contact_class.assert_called_once_with(
            first_name="New",
            last_name="Contact",
            email="new.contact@example.com",
        )

        # Verify PhoneNumbers were created
        assert mock_phone_class.call_count == 2
        mock_session.add.assert_any_call(mock_contact_instance)
        mock_session.add.assert_any_call(mock_phone_instance1)
        mock_session.add.assert_any_call(mock_phone_instance2)

        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Contact successfully created", severity="information"
        )
        mock_start.assert_called_once_with(on_back=None)

    @patch("customers.customer_controller.CustomerController.start")
    def test_create_contact_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """create_contact should notify and restart if cancelled."""
        controller = CustomerController(mock_app, mock_session)
        CustomerController.create_contact.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Contact creation cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(on_back=None)

    # --- Update Contact Tests ---
    @patch("customers.customer_controller.PhoneNumber")
    @patch("customers.customer_controller.CustomerController.start")
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_update_contact_success(
        self,
        mock_get_user,
        mock_start,
        mock_phone_class,
        mock_app,
        mock_session,
        mock_contact,
    ):
        """update_contact should update contact and replace phone numbers."""
        mock_get_user.return_value = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_contact

        mock_phone_instance1 = MagicMock(spec=PhoneNumber)
        mock_phone_instance2 = MagicMock(spec=PhoneNumber)
        mock_phone_class.side_effect = [
            mock_phone_instance1,
            mock_phone_instance2,
        ]

        mock_old_phone1 = MagicMock(spec=PhoneNumber)
        mock_old_phone2 = MagicMock(spec=PhoneNumber)
        mock_session.query.return_value.filter.return_value.all.return_value = [
            mock_old_phone1,
            mock_old_phone2,
        ]

        updated_contact_data = {
            "id": 1,
            "first_name": "Updated",
            "last_name": "Contact",
            "email": "updated@example.com",
            "phone_numbers": ["1112223333", "4445556666"],
        }

        controller = CustomerController(mock_app, mock_session)
        controller.update_contact(updated_contact_data)

        # Verify contact update
        update_call = (
            mock_session.query.return_value.filter.return_value.update
        )
        update_call.assert_called_once_with(
            {
                "first_name": "Updated",
                "last_name": "Contact",
                "email": "updated@example.com",
            }
        )

        # Verify old phone numbers were deleted
        mock_session.delete.assert_any_call(mock_old_phone1)
        mock_session.delete.assert_any_call(mock_old_phone2)

        # Verify new phone numbers were created
        assert mock_phone_class.call_count == 2
        mock_session.add.assert_any_call(mock_phone_instance1)
        mock_session.add.assert_any_call(mock_phone_instance2)

        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Contact successfully updated", severity="information"
        )
        mock_start.assert_called_once_with(on_back=None)

    @patch("customers.customer_controller.CustomerController.start")
    def test_update_contact_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """update_contact should notify and restart if cancelled."""
        controller = CustomerController(mock_app, mock_session)
        CustomerController.update_contact.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Contact update cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(on_back=None)


# =============================================================================
# 6. CALLBACK AND ERROR HANDLING TESTS
# =============================================================================


class TestCustomerControllerCallbacksAndErrors:
    """Tests for callback handling and error management."""

    def test_callbacks_not_called_if_none(self, mock_app, mock_session):
        """Callbacks should not be called if they are None."""
        controller = CustomerController(mock_app, mock_session)
        controller.on_back_callback = None

        # Should not raise exceptions
        controller.handle_user_choice("back")
        controller.handle_user_choice("create_customer")
        controller.handle_user_choice(("update_customer", 1))
        controller.handle_user_choice("create_contact")
        controller.handle_user_choice(("update_contact", 1))

    def test_handle_auth_failure_with_error(self, mock_app, mock_session):
        """_handle_auth_failure should notify and call back callback on error."""
        controller = CustomerController(mock_app, mock_session)
        controller.on_back_callback = MagicMock()
        error = AuthenticationError("Not authenticated")

        controller._handle_auth_failure(error)

        mock_app.notify.assert_called_once()
        notify_call = mock_app.notify.call_args
        assert "Not authenticated" in str(notify_call[0][0])
        assert notify_call[1]["severity"] == "error"
        controller.on_back_callback.assert_called_once()

    def test_handle_auth_failure_without_error(
        self, mock_app, mock_session
    ):
        """_handle_auth_failure should only call back callback if no error."""
        controller = CustomerController(mock_app, mock_session)
        controller.on_back_callback = MagicMock()

        controller._handle_auth_failure(None)

        mock_app.notify.assert_not_called()
        controller.on_back_callback.assert_called_once()
