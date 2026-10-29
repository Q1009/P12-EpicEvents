"""
Tests for contract_controller.py

Unit tests for ContractController class covering:
- Initialization and configuration
- Database query methods
- Screen navigation
- User choice handling
- CRUD operations (create/update contracts)
- Callback and error handling
- Authentication decorator integration

Run with: pytest contracts/tests/test_contract_controller.py -v
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from collaborators.collaborator_model import Collaborator
from contracts.contract_controller import ContractController
from contracts.contract_model import Contract, ContractStatus
from customers.customer_model import Customer
from events.event_model import Event  # noqa: F401
from services.authentication_services import (
    AuthenticationError,
)

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
def mock_contract():
    """Mock Contract object with default values."""
    contract = MagicMock(spec=Contract)
    contract.id = 1
    contract.total_amount = 10000
    contract.amount_due = 5000
    contract.status = ContractStatus.PENDING
    contract.customer = MagicMock(spec=Customer)
    contract.customer.id = 1
    contract.customer.first_name = "John"
    contract.customer.last_name = "Doe"
    contract.event = None
    return contract


@pytest.fixture
def mock_signed_contract():
    """Mock signed Contract object."""
    contract = MagicMock(spec=Contract)
    contract.id = 2
    contract.total_amount = 20000
    contract.amount_due = 0
    contract.status = ContractStatus.SIGNED
    contract.customer = MagicMock(spec=Customer)
    contract.customer.id = 2
    contract.customer.first_name = "Jane"
    contract.customer.last_name = "Smith"
    contract.event = None
    return contract


@pytest.fixture
def mock_customer():
    """Mock Customer object."""
    customer = MagicMock(spec=Customer)
    customer.id = 1
    customer.first_name = "John"
    customer.last_name = "Doe"
    return customer


@pytest.fixture
def mock_collaborator():
    """Mock Collaborator object."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 1
    collaborator.first_name = "Admin"
    collaborator.last_name = "User"
    return collaborator


# =============================================================================
# 1. INITIALIZATION TESTS
# =============================================================================


class TestContractControllerInitialization:
    """Tests for ContractController initialization and start method."""

    def test_init_sets_attributes(self, mock_app, mock_session):
        """__init__ should store epic_events_app and session."""
        controller = ContractController(mock_app, mock_session)
        assert controller.epic_events_app == mock_app
        assert controller.session == mock_session

    def test_init_sets_callbacks_to_none(self, mock_app, mock_session):
        """__init__ should initialize all callbacks to None."""
        controller = ContractController(mock_app, mock_session)
        assert controller.on_back_callback is None
        assert controller.on_consult_customer_callback is None
        assert controller.on_consult_event_callback is None
        assert controller.on_create_event_callback is None

    def test_start_stores_callbacks(self, mock_app, mock_session):
        """start() should store callbacks."""
        controller = ContractController(mock_app, mock_session)
        on_back = MagicMock()
        on_consult_customer = MagicMock()
        on_consult_event = MagicMock()
        on_create_event = MagicMock()

        controller.start(
            on_back=on_back,
            on_consult_customer=on_consult_customer,
            on_consult_event=on_consult_event,
            on_create_event=on_create_event,
        )

        assert controller.on_back_callback == on_back
        assert (
            controller.on_consult_customer_callback == on_consult_customer
        )
        assert controller.on_consult_event_callback == on_consult_event
        assert controller.on_create_event_callback == on_create_event

    @patch(
        "contracts.contract_controller.ContractController.get_all_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.push_contract_screen"
    )
    def test_start_with_contract_id(
        self, mock_push, mock_get_all, mock_app, mock_session
    ):
        """start() should push ContractScreen with contracts and contract_id."""
        mock_contracts = [MagicMock(spec=Contract)]
        mock_get_all.return_value = mock_contracts
        controller = ContractController(mock_app, mock_session)
        controller.start(contract_id=1)

        mock_get_all.assert_called_once()
        mock_push.assert_called_once_with(
            contracts=mock_contracts, contract_id=1
        )

    @patch(
        "contracts.contract_controller.ContractController.get_all_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.push_contract_screen"
    )
    def test_start_without_contract_id(
        self, mock_push, mock_get_all, mock_app, mock_session
    ):
        """start() should push ContractScreen with contracts."""
        mock_contracts = [MagicMock(spec=Contract)]
        mock_get_all.return_value = mock_contracts
        controller = ContractController(mock_app, mock_session)
        controller.start()

        mock_get_all.assert_called_once()
        mock_push.assert_called_once_with(
            contracts=mock_contracts, contract_id=None
        )


# =============================================================================
# 2. DATABASE QUERY TESTS
# =============================================================================


class TestContractControllerDatabaseQueries:
    """Tests for database query methods."""

    def test_get_all_contracts_returns_list(
        self, mock_session, mock_app, mock_contract
    ):
        """get_all_contracts() should return list of contracts with eager loading."""
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_query.options.return_value = mock_options
        mock_options.all.return_value = [mock_contract]
        mock_session.query.return_value = mock_query

        controller = ContractController(mock_app, mock_session)
        contracts = controller.get_all_contracts()

        assert contracts == [mock_contract]
        mock_session.query.assert_called_once_with(Contract)
        mock_query.options.assert_called_once()

    # def test_get_all_contracts_with_joinedload(self, mock_session, mock_app, mock_contract):
    #     """get_all_contracts() should use joinedload for customer and event."""
    #     mock_query = MagicMock()
    #     mock_options = MagicMock()
    #     mock_query.options.return_value = mock_options
    #     mock_options.all.return_value = [mock_contract]
    #     mock_session.query.return_value = mock_query

    #     controller = ContractController(mock_app, mock_session)
    #     controller.get_all_contracts()

    #     mock_query.options.assert_called_once()
    #     call_args = mock_query.options.call_args[0]
    #     assert len(call_args) == 2
    #     assert call_args[0] == joinedload(Contract.customer)
    #     assert call_args[1] == joinedload(Contract.event)

    def test_get_unsigned_contracts_filters_by_status(
        self, mock_session, mock_app, mock_contract
    ):
        """get_unsigned_contracts() should filter by status != SIGNED."""
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_filter = MagicMock()
        mock_query.options.return_value = mock_options
        mock_options.filter.return_value = mock_filter
        mock_filter.all.return_value = [mock_contract]
        mock_session.query.return_value = mock_query

        controller = ContractController(mock_app, mock_session)
        contracts = controller.get_unsigned_contracts()

        assert contracts == [mock_contract]
        mock_options.filter.assert_called_once()
        mock_filter.all.assert_called_once()

    def test_get_unpaid_contracts_filters_by_amount_due(
        self, mock_session, mock_app, mock_contract
    ):
        """get_unpaid_contracts() should filter by amount_due != 0."""
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_filter = MagicMock()
        mock_query.options.return_value = mock_options
        mock_options.filter.return_value = mock_filter
        mock_filter.all.return_value = [mock_contract]
        mock_session.query.return_value = mock_query

        controller = ContractController(mock_app, mock_session)
        contracts = controller.get_unpaid_contracts()

        assert contracts == [mock_contract]
        mock_options.filter.assert_called_once()
        mock_filter.all.assert_called_once()

    def test_get_all_customers_returns_list(
        self, mock_session, mock_app, mock_customer
    ):
        """get_all_customers() should return list of customers."""
        mock_session.query.return_value.all.return_value = [mock_customer]

        controller = ContractController(mock_app, mock_session)
        customers = controller.get_all_customers()

        assert customers == [mock_customer]
        mock_session.query.assert_called_once_with(Customer)

    def test_load_contract_data_for_update_returns_dict(
        self, mock_session, mock_app, mock_contract
    ):
        """load_contract_data_for_update() should return contract data as dict."""
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_contract
        mock_session.query.return_value = mock_query

        controller = ContractController(mock_app, mock_session)
        result = controller.load_contract_data_for_update(1)

        expected = {
            "contract_id": 1,
            "contract_total_amount": 10000,
            "contract_amount_due": 5000,
            "contract_status": ContractStatus.PENDING,
            "contract_customer": mock_contract.customer,
        }
        assert result == expected
        mock_query.filter.assert_called_once()


# =============================================================================
# 3. SCREEN NAVIGATION TESTS
# =============================================================================


class TestContractControllerScreenNavigation:
    """Tests for screen navigation methods."""

    @patch("contracts.contract_controller.ContractScreen")
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_push_contract_screen_calls_push_screen(
        self,
        mock_get_user,
        mock_contract_screen,
        mock_app,
        mock_session,
        mock_contract,
        mock_collaborator,
    ):
        """push_contract_screen() should push ContractScreen with correct parameters."""
        mock_get_user.return_value = mock_collaborator
        mock_screen_instance = MagicMock()
        mock_contract_screen.return_value = mock_screen_instance

        controller = ContractController(mock_app, mock_session)
        ContractController.push_contract_screen.__wrapped__(
            controller,
            contracts=[mock_contract],
            contract_id=1,
            filtered_table_signature=True,
            filtered_table_payment=False,
        )

        mock_get_user.assert_called_once_with(mock_session)
        mock_contract_screen.assert_called_once_with(
            contracts=[mock_contract],
            user=mock_collaborator,
            contract_id=1,
            filtered_table_signature=True,
            filtered_table_payment=False,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.handle_user_choice
        )

    @patch("contracts.contract_controller.CreateContractScreen")
    @patch(
        "contracts.contract_controller.ContractController.get_all_customers"
    )
    def test_push_create_contract_screen(
        self,
        mock_get_customers,
        mock_create_screen,
        mock_app,
        mock_session,
        mock_customer,
    ):
        """push_create_contract_screen() should push CreateContractScreen with customers."""
        mock_get_customers.return_value = [mock_customer]
        mock_screen_instance = MagicMock()
        mock_create_screen.return_value = mock_screen_instance

        controller = ContractController(mock_app, mock_session)
        ContractController.push_create_contract_screen.__wrapped__(
            controller
        )

        mock_get_customers.assert_called_once()
        mock_create_screen.assert_called_once_with([mock_customer])
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.create_contract
        )

    @patch("contracts.contract_controller.UpdateContractScreen")
    @patch(
        "contracts.contract_controller.ContractController.get_all_customers"
    )
    @patch(
        "contracts.contract_controller.ContractController.load_contract_data_for_update"
    )
    def test_push_update_contract_screen(
        self,
        mock_load_data,
        mock_get_customers,
        mock_update_screen,
        mock_app,
        mock_session,
        mock_customer,
    ):
        """push_update_contract_screen() should push UpdateContractScreen with contract data."""
        mock_get_customers.return_value = [mock_customer]
        mock_screen_instance = MagicMock()
        mock_update_screen.return_value = mock_screen_instance
        mock_contract_data = {
            "contract_id": 1,
            "contract_total_amount": 10000,
            "contract_amount_due": 5000,
            "contract_status": ContractStatus.PENDING,
            "contract_customer": mock_customer,
        }
        mock_load_data.return_value = mock_contract_data

        controller = ContractController(mock_app, mock_session)
        ContractController.push_update_contract_screen.__wrapped__(
            controller, contract_id=1
        )

        mock_get_customers.assert_called_once()
        mock_load_data.assert_called_once_with(1)
        mock_update_screen.assert_called_once_with(
            mock_contract_data,
            [mock_customer],
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.update_contract
        )


# =============================================================================
# 4. USER CHOICE HANDLING TESTS
# =============================================================================


class TestContractControllerUserChoiceHandling:
    """Tests for handle_user_choice method."""

    @patch(
        "contracts.contract_controller.ContractController.push_create_contract_screen"
    )
    def test_handle_create_contract_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_create_contract_screen for 'create_contract'."""
        controller = ContractController(mock_app, mock_session)
        controller.handle_user_choice("create_contract")
        mock_push.assert_called_once()

    @patch(
        "contracts.contract_controller.ContractController.push_update_contract_screen"
    )
    def test_handle_update_contract_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_update_contract_screen for ('update_contract', id)."""
        controller = ContractController(mock_app, mock_session)
        controller.handle_user_choice(("update_contract", 1))
        mock_push.assert_called_once_with(contract_id=1)

    def test_handle_create_event_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_create_event_callback for ('create_event', id)."""
        callback = MagicMock()
        controller = ContractController(mock_app, mock_session)
        controller.on_create_event_callback = callback
        controller.handle_user_choice(("create_event", 1))
        callback.assert_called_once_with(contract_id=1)

    def test_handle_create_event_choice_no_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should not fail if on_create_event_callback is None."""
        controller = ContractController(mock_app, mock_session)
        controller.on_create_event_callback = None
        controller.handle_user_choice(("create_event", 1))

    def test_handle_consult_customer_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_consult_customer_callback for ('consult_customer', id)."""
        callback = MagicMock()
        controller = ContractController(mock_app, mock_session)
        controller.on_consult_customer_callback = callback
        controller.handle_user_choice(("consult_customer", 1))
        callback.assert_called_once_with(1)

    def test_handle_consult_event_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_consult_event_callback for ('consult_event', id)."""
        callback = MagicMock()
        controller = ContractController(mock_app, mock_session)
        controller.on_consult_event_callback = callback
        controller.handle_user_choice(("consult_event", 1))
        callback.assert_called_once_with(event_id=1)

    @patch(
        "contracts.contract_controller.ContractController.get_unsigned_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.push_contract_screen"
    )
    def test_handle_filter_unsigned_contracts(
        self,
        mock_push,
        mock_get_unsigned,
        mock_app,
        mock_session,
        mock_contract,
    ):
        """handle_user_choice should get unsigned contracts and push screen for filter action."""
        mock_get_unsigned.return_value = [mock_contract]

        controller = ContractController(mock_app, mock_session)
        controller.handle_user_choice(("filter_unsigned_contracts", True))

        mock_get_unsigned.assert_called_once()
        mock_push.assert_called_once()
        call_args = mock_push.call_args
        assert call_args[1]["contracts"] == [mock_contract]
        assert call_args[1]["filtered_table_signature"] is True

    @patch(
        "contracts.contract_controller.ContractController.get_unpaid_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.push_contract_screen"
    )
    def test_handle_filter_unpaid_contracts(
        self,
        mock_push,
        mock_get_unpaid,
        mock_app,
        mock_session,
        mock_contract,
    ):
        """handle_user_choice should get unpaid contracts and push screen for filter action."""
        mock_get_unpaid.return_value = [mock_contract]

        controller = ContractController(mock_app, mock_session)
        controller.handle_user_choice(("filter_unpaid_contracts", True))

        mock_get_unpaid.assert_called_once()
        mock_push.assert_called_once()
        call_args = mock_push.call_args
        assert call_args[1]["contracts"] == [mock_contract]
        assert call_args[1]["filtered_table_payment"] is True

    @patch(
        "contracts.contract_controller.ContractController.get_all_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.push_contract_screen"
    )
    def test_handle_filter_reset(
        self,
        mock_push,
        mock_get_all,
        mock_app,
        mock_session,
        mock_contract,
    ):
        """handle_user_choice should get all contracts and push screen with filters reset."""
        mock_get_all.return_value = [mock_contract]

        controller = ContractController(mock_app, mock_session)
        controller.handle_user_choice(("filter_reset", False))

        mock_get_all.assert_called_once()
        mock_push.assert_called_once()
        call_args = mock_push.call_args
        assert call_args[1]["contracts"] == [mock_contract]
        assert call_args[1]["filtered_table_signature"] is False
        assert call_args[1]["filtered_table_payment"] is False

    def test_handle_back_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_back_callback for 'back'."""
        callback = MagicMock()
        controller = ContractController(mock_app, mock_session)
        controller.on_back_callback = callback
        controller.handle_user_choice("back")
        callback.assert_called_once()

    def test_handle_back_choice_no_callback(self, mock_app, mock_session):
        """handle_user_choice should not fail if on_back_callback is None."""
        controller = ContractController(mock_app, mock_session)
        controller.on_back_callback = None
        controller.handle_user_choice("back")

    def test_handle_quit_choice_exits_app(self, mock_app, mock_session):
        """handle_user_choice should call app.exit() for 'quit'."""
        controller = ContractController(mock_app, mock_session)
        controller.handle_user_choice("quit")
        mock_app.exit.assert_called_once()


# =============================================================================
# 5. CRUD METHODS TESTS
# =============================================================================


class TestContractControllerBusinessLogic:
    """Tests for CRUD operations: create_contract and update_contract."""

    # --- Create Contract Tests ---
    @patch("contracts.contract_controller.ContractController.start")
    def test_create_contract_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """create_contract should notify and restart if cancelled."""

        controller = ContractController(mock_app, mock_session)
        ContractController.create_contract.__wrapped__(controller, None)

        mock_app.notify.assert_called_once_with(
            "Contract creation cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
            on_create_event=None,
        )

    @patch("contracts.contract_controller.Contract")
    @patch("contracts.contract_controller.ContractController.start")
    def test_create_contract_success(
        self,
        mock_start,
        mock_contract_class,
        mock_app,
        mock_session,
        mock_customer,
    ):
        """create_contract should create contract with PENDING status and restart."""
        mock_contract_instance = MagicMock(spec=Contract)
        mock_contract_class.return_value = mock_contract_instance

        new_contract_data = {
            "contract_total_amount": 15000,
            "contract_amount_due": 15000,
            "contract_customer": mock_customer,
        }

        controller = ContractController(mock_app, mock_session)
        ContractController.create_contract.__wrapped__(
            controller, new_contract_data
        )

        # Verify Contract was created with correct data
        mock_contract_class.assert_called_once_with(
            total_amount=15000,
            amount_due=15000,
            status=ContractStatus.PENDING,
            customer=mock_customer,
        )

        # Verify session and notifications
        mock_session.add.assert_any_call(mock_contract_instance)
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Contract successfully created", severity="information"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
            on_create_event=None,
        )

    # --- Update Contract Tests ---
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    @patch("contracts.contract_controller.ContractController.start")
    def test_update_contract_cancelled(
        self, mock_start, mock_get_user, mock_app, mock_session
    ):
        """update_contract should notify and restart if cancelled."""
        controller = ContractController(mock_app, mock_session)
        ContractController.update_contract.__wrapped__(controller, None)

        mock_get_user.assert_called_once_with(mock_session)
        mock_app.notify.assert_called_once_with(
            "Contract update cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
            on_create_event=None,
        )

    @patch(
        "services.authentication_services.AuthenticationServices.check_authentication"
    )
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    @patch("contracts.contract_controller.ContractController.start")
    def test_update_contract_success(
        self,
        mock_start,
        mock_get_user,
        mock_check_auth,
        mock_app,
        mock_session,
        mock_contract,
    ):
        """update_contract should update contract fields and restart."""
        mock_check_auth.return_value = None
        mock_get_user.return_value = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_contract

        updated_contract_data = {
            "contract_id": 1,
            "contract_total_amount": 12000,
            "contract_amount_due": 2000,
            "contract_status": ContractStatus.SIGNED,
            "contract_customer": mock_contract.customer,
        }

        controller = ContractController(mock_app, mock_session)
        controller.update_contract(updated_contract_data)

        # Verify the update was called with correct data
        update_call = (
            mock_session.query.return_value.filter.return_value.update
        )
        update_call.assert_called_once_with(
            {
                "total_amount": 12000,
                "amount_due": 2000,
                "status": ContractStatus.SIGNED,
                "customer_id": mock_contract.customer.id,
            }
        )

        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Contract successfully updated", severity="information"
        )
        mock_start.assert_called_once()

    @patch("sentry_sdk.capture_event")
    @patch(
        "services.authentication_services.AuthenticationServices.check_authentication"
    )
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    @patch("contracts.contract_controller.ContractController.start")
    def test_update_contract_signed_logs_to_sentry(
        self,
        mock_start,
        mock_get_user,
        mock_check_auth,
        mock_capture_event,
        mock_app,
        mock_session,
        mock_signed_contract,
        mock_collaborator,
    ):
        """update_contract should log signed contracts to Sentry with correct details."""
        mock_check_auth.return_value = None
        mock_get_user.return_value = mock_collaborator
        mock_session.query.return_value.filter.return_value.first.return_value = mock_signed_contract

        updated_contract_data = {
            "contract_id": 2,
            "contract_total_amount": 20000,
            "contract_amount_due": 0,
            "contract_status": ContractStatus.SIGNED,
            "contract_customer": mock_signed_contract.customer,
        }

        controller = ContractController(mock_app, mock_session)
        controller.update_contract(updated_contract_data)

        # Verify Sentry capture_event was called
        mock_capture_event.assert_called_once()
        sentry_event = mock_capture_event.call_args[0][0]

        assert sentry_event["level"] == "info"
        assert "Contract signed: ID 2" in sentry_event["message"]
        assert sentry_event["extra"]["contract_id"] == 2
        assert sentry_event["extra"]["signed_by_id"] == 1
        assert sentry_event["extra"]["signed_by_name"] == "Admin User"
        assert sentry_event["tags"]["module"] == "contracts"
        assert sentry_event["tags"]["action"] == "sign"
        assert sentry_event["tags"]["status"] == "signed"


# =============================================================================
# 6. CALLBACK AND ERROR HANDLING TESTS
# =============================================================================


class TestContractControllerCallbacksAndErrors:
    """Tests for callback handling and error management."""

    def test_callbacks_not_called_if_none(
        self, mock_app, mock_session, mock_contract
    ):
        """Callbacks should not be called if they are None."""
        controller = ContractController(mock_app, mock_session)
        controller.on_create_event_callback = None
        controller.on_consult_customer_callback = None
        controller.on_consult_event_callback = None
        controller.on_back_callback = None

        # Should not raise exceptions
        controller.handle_user_choice(("create_event", 1))
        controller.handle_user_choice(("consult_customer", 1))
        controller.handle_user_choice(("consult_event", 1))
        controller.handle_user_choice("back")

    def test_handle_auth_failure_with_error(self, mock_app, mock_session):
        """_handle_auth_failure should notify and call back callback on error."""
        controller = ContractController(mock_app, mock_session)
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
        controller = ContractController(mock_app, mock_session)
        controller.on_back_callback = MagicMock()

        controller._handle_auth_failure(None)

        mock_app.notify.assert_not_called()
        controller.on_back_callback.assert_called_once()


# =============================================================================
# 7. INTEGRATION TESTS
# =============================================================================


class TestContractControllerIntegration:
    """Integration tests for complete workflows."""

    @patch(
        "services.authentication_services.AuthenticationServices.check_authentication"
    )
    @patch(
        "contracts.contract_controller.ContractController.get_all_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.get_unsigned_contracts"
    )
    @patch(
        "contracts.contract_controller.ContractController.push_contract_screen"
    )
    def test_filter_and_reset_workflow(
        self,
        mock_push,
        mock_get_unsigned,
        mock_get_all,
        mock_check_auth,
        mock_app,
        mock_session,
        mock_contract,
    ):
        """Test the filter and reset workflow."""
        mock_check_auth.return_value = None
        mock_get_all.return_value = [mock_contract]
        mock_get_unsigned.return_value = [mock_contract]

        controller = ContractController(mock_app, mock_session)
        controller.start()

        # Filter by unsigned contracts
        controller.handle_user_choice(("filter_unsigned_contracts", True))

        # Reset filters
        controller.handle_user_choice(("filter_reset", False))

        # Verify the workflow
        mock_get_all.assert_called()
        mock_get_unsigned.assert_called_once()
        assert mock_push.call_count == 3
