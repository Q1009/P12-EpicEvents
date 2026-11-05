"""
Tests for collaborator_controller.py

Unit tests for CollaboratorController class covering:
- Initialization and configuration
- Database query methods
- Screen navigation
- User choice handling
- CRUD operations (create/update/delete collaborators)
- Callback and error handling
- Authentication decorator integration
- Sentry integration

Run with: pytest collaborators/tests/test_collaborator_controller.py -v
"""

from unittest.mock import ANY, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from collaborators.collaborator_controller import CollaboratorController
from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
)
from contracts.contract_model import Contract  # noqa: F401
from customers.customer_model import Customer  # noqa: F401
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


# --- Department Fixtures ---
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


# --- Collaborator Fixtures ---
@pytest.fixture
def mock_admin_collaborator(mock_admin_department):
    """Mock Collaborator object."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 1
    collaborator.first_name = "Admin"
    collaborator.last_name = "User"
    collaborator.email = "admin.user@epicevents.com"
    collaborator.password = "hashed_password"
    collaborator.department = mock_admin_department
    collaborator.department_id = 1
    collaborator.customers = []
    collaborator.events = []
    return collaborator


@pytest.fixture
def mock_sales_collaborator(mock_sales_department):
    """Mock second Collaborator object."""
    collaborator = MagicMock(spec=Collaborator)
    collaborator.id = 2
    collaborator.first_name = "Sales"
    collaborator.last_name = "Rep1"
    collaborator.email = "sales.rep1@epicevents.com"
    collaborator.password = "hashed_password"
    collaborator.department = mock_sales_department
    collaborator.department_id = 2
    collaborator.customers = []
    collaborator.events = []
    return collaborator


@pytest.fixture
def mock_collaborators_list(
    mock_admin_collaborator, mock_sales_collaborator
):
    """List of Collaborator objects."""
    return [mock_admin_collaborator, mock_sales_collaborator]


# =============================================================================
# 1. INITIALIZATION TESTS
# =============================================================================


class TestCollaboratorControllerInitialization:
    """Tests for CollaboratorController initialization and start method."""

    def test_init_sets_attributes(self, mock_app, mock_session):
        """__init__ should store epic_events_app and session."""
        controller = CollaboratorController(mock_app, mock_session)
        assert controller.epic_events_app == mock_app
        assert controller.session == mock_session

    def test_init_sets_callbacks_to_none(self, mock_app, mock_session):
        """__init__ should initialize all callbacks to None."""
        controller = CollaboratorController(mock_app, mock_session)
        assert controller.on_back_callback is None
        assert controller.on_consult_customer_callback is None
        assert controller.on_consult_event_callback is None

    def test_start_stores_callbacks(self, mock_app, mock_session):
        """start() should store all callbacks."""
        controller = CollaboratorController(mock_app, mock_session)
        on_back = MagicMock()
        on_consult_customer = MagicMock()
        on_consult_event = MagicMock()

        controller.start(
            on_back=on_back,
            on_consult_customer=on_consult_customer,
            on_consult_event=on_consult_event,
        )

        assert controller.on_back_callback == on_back
        assert (
            controller.on_consult_customer_callback == on_consult_customer
        )
        assert controller.on_consult_event_callback == on_consult_event

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.get_all_collaborators"
    )
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.push_collaborator_screen"
    )
    def test_start_pushes_screen(
        self,
        mock_push,
        mock_get_all,
        mock_app,
        mock_session,
        mock_collaborators_list,
    ):
        """start() should push CollaboratorScreen with all collaborators."""
        mock_get_all.return_value = mock_collaborators_list
        controller = CollaboratorController(mock_app, mock_session)
        controller.start()

        mock_get_all.assert_called_once()
        mock_push.assert_called_once_with(
            collaborators=mock_collaborators_list
        )


# =============================================================================
# 2. DATABASE QUERY TESTS
# =============================================================================


class TestCollaboratorControllerDatabaseQueries:
    """Tests for database query methods."""

    def test_get_all_collaborators_returns_list(
        self, mock_session, mock_app, mock_admin_collaborator
    ):
        """get_all_collaborators() should return list of collaborators with eager loading."""
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_query.options.return_value = mock_options
        mock_options.all.return_value = [mock_admin_collaborator]
        mock_session.query.return_value = mock_query

        controller = CollaboratorController(mock_app, mock_session)
        collaborators = controller.get_all_collaborators()

        assert collaborators == [mock_admin_collaborator]
        mock_session.query.assert_called_once_with(Collaborator)
        mock_query.options.assert_called_once()

    def test_get_all_departments_returns_list(
        self, mock_session, mock_app, mock_admin_department
    ):
        """get_all_departments() should return list of departments."""
        mock_session.query.return_value.all.return_value = [
            mock_admin_department
        ]

        controller = CollaboratorController(mock_app, mock_session)
        departments = controller.get_all_departments()

        assert departments == [mock_admin_department]
        mock_session.query.assert_called_once_with(Department)

    def test_load_collaborator_data_for_update_returns_dict(
        self, mock_session, mock_app, mock_admin_collaborator
    ):
        """load_collaborator_data_for_update() should return collaborator data as dict."""
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_admin_collaborator
        mock_session.query.return_value = mock_query

        controller = CollaboratorController(mock_app, mock_session)
        result = controller.load_collaborator_data_for_update(1)

        expected = {
            "collaborator_id": 1,
            "collaborator_first_name": "Admin",
            "collaborator_last_name": "User",
            "department": mock_admin_collaborator.department,
        }
        assert result == expected
        mock_query.filter.assert_called_once()


# =============================================================================
# 3. SCREEN NAVIGATION TESTS
# =============================================================================


class TestCollaboratorControllerScreenNavigation:
    """Tests for screen navigation methods."""

    @patch("collaborators.collaborator_controller.CollaboratorScreen")
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    def test_push_collaborator_screen_calls_push_screen(
        self,
        mock_get_user,
        mock_admin_collaborator_screen,
        mock_app,
        mock_session,
        mock_admin_collaborator,
        mock_collaborators_list,
    ):
        """push_collaborator_screen() should push CollaboratorScreen with correct parameters."""
        mock_get_user.return_value = mock_admin_collaborator
        mock_screen_instance = MagicMock()
        mock_admin_collaborator_screen.return_value = mock_screen_instance

        controller = CollaboratorController(mock_app, mock_session)
        CollaboratorController.push_collaborator_screen.__wrapped__(
            controller,
            collaborators=mock_collaborators_list,
        )

        mock_get_user.assert_called_once_with(mock_session)
        mock_admin_collaborator_screen.assert_called_once_with(
            collaborators=mock_collaborators_list,
            user=mock_admin_collaborator,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.handle_user_choice
        )

    @patch(
        "collaborators.collaborator_controller.CreateCollaboratorScreen"
    )
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.get_all_departments"
    )
    def test_push_create_collaborator_screen(
        self,
        mock_get_departments,
        mock_create_screen,
        mock_app,
        mock_session,
        mock_departments_list,
    ):
        """push_create_collaborator_screen() should push CreateCollaboratorScreen with departments."""
        mock_get_departments.return_value = mock_departments_list
        mock_screen_instance = MagicMock()
        mock_create_screen.return_value = mock_screen_instance

        controller = CollaboratorController(mock_app, mock_session)
        CollaboratorController.push_create_collaborator_screen.__wrapped__(
            controller
        )

        mock_get_departments.assert_called_once()
        mock_create_screen.assert_called_once_with(
            departments=mock_departments_list
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.create_collaborator
        )

    @patch(
        "collaborators.collaborator_controller.UpdateCollaboratorScreen"
    )
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.get_all_departments"
    )
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.load_collaborator_data_for_update"
    )
    def test_push_update_collaborator_screen(
        self,
        mock_load_data,
        mock_get_departments,
        mock_update_screen,
        mock_app,
        mock_session,
        mock_admin_collaborator,
        mock_departments_list,
    ):
        """push_update_collaborator_screen() should push UpdateCollaboratorScreen with collaborator data."""
        mock_get_departments.return_value = mock_departments_list
        mock_screen_instance = MagicMock()
        mock_update_screen.return_value = mock_screen_instance
        mock_admin_collaborator_data = {
            "collaborator_id": 1,
            "collaborator_first_name": "Admin",
            "collaborator_last_name": "User",
            "department": mock_admin_collaborator.department,
        }
        mock_load_data.return_value = mock_admin_collaborator_data

        controller = CollaboratorController(mock_app, mock_session)
        CollaboratorController.push_update_collaborator_screen.__wrapped__(
            controller, collaborator_id=1
        )

        mock_get_departments.assert_called_once()
        mock_load_data.assert_called_once_with(1)
        mock_update_screen.assert_called_once_with(
            mock_admin_collaborator_data,
            mock_departments_list,
        )
        mock_app.push_screen.assert_called_once_with(
            mock_screen_instance, callback=controller.update_collaborator
        )


# =============================================================================
# 4. USER CHOICE HANDLING TESTS
# =============================================================================


class TestCollaboratorControllerUserChoiceHandling:
    """Tests for handle_user_choice method."""

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.push_create_collaborator_screen"
    )
    def test_handle_create_collaborator_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_create_collaborator_screen for 'create_collaborator'."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.handle_user_choice("create_collaborator")
        mock_push.assert_called_once()

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.push_update_collaborator_screen"
    )
    def test_handle_update_collaborator_choice(
        self, mock_push, mock_app, mock_session
    ):
        """handle_user_choice should call push_update_collaborator_screen for ('update_collaborator', id)."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.handle_user_choice(("update_collaborator", 1))
        mock_push.assert_called_once_with(collaborator_id=1)

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.delete_collaborator"
    )
    def test_handle_delete_collaborator_choice(
        self, mock_delete, mock_app, mock_session
    ):
        """handle_user_choice should call delete_collaborator for ('delete_collaborator', id)."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.handle_user_choice(("delete_collaborator", 1))
        mock_delete.assert_called_once_with(1)

    def test_handle_consult_customer_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_consult_customer_callback for ('consult_customer', id)."""
        callback = MagicMock()
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_consult_customer_callback = callback
        controller.handle_user_choice(("consult_customer", 1))
        callback.assert_called_once_with(1)

    def test_handle_consult_event_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_consult_event_callback for ('consult_event', id)."""
        callback = MagicMock()
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_consult_event_callback = callback
        controller.handle_user_choice(("consult_event", 1))
        callback.assert_called_once_with(1)

    def test_handle_back_choice_calls_callback(
        self, mock_app, mock_session
    ):
        """handle_user_choice should call on_back_callback for 'back'."""
        callback = MagicMock()
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_back_callback = callback
        controller.handle_user_choice("back")
        callback.assert_called_once()

    def test_handle_back_choice_no_callback(self, mock_app, mock_session):
        """handle_user_choice should not fail if on_back_callback is None."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_back_callback = None
        controller.handle_user_choice("back")

    def test_handle_quit_choice_exits_app(self, mock_app, mock_session):
        """handle_user_choice should call app.exit() for 'quit'."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.handle_user_choice("quit")
        mock_app.exit.assert_called_once()


# =============================================================================
# 5. CRUD METHODS TESTS
# =============================================================================


class TestCollaboratorControllerBusinessLogic:
    """Tests for CRUD operations: create/update/delete collaborators."""

    # --- Create Collaborator Tests ---
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    def test_create_collaborator_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """create_collaborator should notify and restart if cancelled."""
        controller = CollaboratorController(mock_app, mock_session)
        CollaboratorController.create_collaborator.__wrapped__(
            controller, None
        )

        mock_app.notify.assert_called_once_with(
            "Collaborator creation cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )

    @patch("collaborators.collaborator_controller.Collaborator")
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    @patch(
        "collaborators.collaborator_controller.PasswordServices.hash_password"
    )
    @patch("sentry_sdk.capture_event")
    def test_create_collaborator_success(
        self,
        mock_sentry,
        mock_hash,
        mock_get_user,
        mock_start,
        mock_collaborator_class,
        mock_app,
        mock_session,
        mock_sales_department,
        mock_admin_collaborator,
    ):
        """create_collaborator should create collaborator with proper email and hashed password."""
        # Setup
        mock_get_user.return_value = mock_admin_collaborator
        mock_hash.return_value = "hashed_password_123"
        new_collaborator_data = {
            "collaborator_first_name": "John",
            "collaborator_last_name": "Doe",
            "password": "my-secret-password",
            "department": mock_sales_department,
        }
        mock_collaborator_instance = MagicMock(spec=Collaborator)
        mock_collaborator_class.return_value = mock_collaborator_instance

        controller = CollaboratorController(mock_app, mock_session)
        CollaboratorController.create_collaborator.__wrapped__(
            controller, new_collaborator_data
        )

        # Generate email
        new_collaborator_email = (
            (new_collaborator_data["collaborator_first_name"]).lower()
            + "."
            + (new_collaborator_data["collaborator_last_name"]).lower()
            + "@epicevents.com"
        )

        # Verify Collaborator was created with correct data
        mock_collaborator_class.assert_called_once_with(
            last_name=new_collaborator_data["collaborator_last_name"],
            first_name=new_collaborator_data["collaborator_first_name"],
            email=new_collaborator_email,
            password="hashed_password_123",
            department=new_collaborator_data["department"],
        )

        # Check password hashing
        mock_hash.assert_called_once_with("my-secret-password")

        # Verify session and notifications
        mock_session.add.assert_any_call(mock_collaborator_instance)
        mock_session.commit.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "Collaborator successfully created", severity="information"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )

        # Check Sentry log
        mock_sentry.assert_called_once()
        sentry_call = mock_sentry.call_args[0][0]
        assert sentry_call["level"] == "info"
        assert sentry_call["extra"]["action"] == "create"
        assert sentry_call["tags"]["module"] == "collaborators"
        assert sentry_call["tags"]["action"] == "create"

    # --- Update Collaborator Tests ---
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    def test_update_collaborator_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """update_collaborator should notify and restart if cancelled."""
        controller = CollaboratorController(mock_app, mock_session)
        CollaboratorController.update_collaborator.__wrapped__(
            controller, None
        )

        mock_app.notify.assert_called_once_with(
            "Collaborator update cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    @patch(
        "services.authentication_services.AuthenticationServices.get_user_info"
    )
    @patch("sentry_sdk.capture_event")
    def test_update_collaborator_success(
        self,
        mock_sentry,
        mock_get_user,
        mock_start,
        mock_app,
        mock_session,
        mock_admin_collaborator,
    ):
        """update_collaborator should update collaborator with new email and department."""
        # Setup
        mock_get_user.return_value = mock_admin_collaborator
        mock_session.query.return_value.filter.return_value.first.return_value = mock_admin_collaborator

        updated_collaborator_data = {
            "id": 1,
            "first_name": "Updated",
            "last_name": "Name",
            "department": mock_admin_collaborator.department,
        }

        controller = CollaboratorController(mock_app, mock_session)

        # Execute
        controller.update_collaborator(updated_collaborator_data)

        # Assert
        # Check update query
        update_call = (
            mock_session.query.return_value.filter.return_value.update
        )
        update_call.assert_called_once_with(
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated.name@epicevents.com",
                "department_id": mock_admin_collaborator.department.id,
            }
        )

        # Check session commit
        mock_session.commit.assert_called_once()

        # Check Sentry log
        mock_sentry.assert_called_once()
        sentry_call = mock_sentry.call_args[0][0]
        assert sentry_call["level"] == "info"
        assert "Collaborator updated: ID 1" in sentry_call["message"]
        assert sentry_call["extra"]["action"] == "update"
        assert sentry_call["tags"]["module"] == "collaborators"
        assert sentry_call["tags"]["action"] == "update"

        # Check notification
        mock_app.notify.assert_called_with(
            "Collaborator successfully updated", severity="information"
        )

        # Check start called
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )

    # --- Delete Collaborator Tests ---
    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    def test_delete_collaborator_cancelled(
        self, mock_start, mock_app, mock_session
    ):
        """delete_collaborator should notify and restart if cancelled."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.delete_collaborator(None)

        mock_app.notify.assert_called_once_with(
            "Collaborator delete cancelled", severity="warning"
        )
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    def test_delete_collaborator_success(
        self, mock_start, mock_app, mock_session
    ):
        """delete_collaborator should delete collaborator and restart."""
        mock_delete_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.delete.return_value = mock_delete_query
        mock_session.query.return_value.filter.return_value = mock_filter

        controller = CollaboratorController(mock_app, mock_session)
        controller.delete_collaborator(1)

        # Check delete query
        mock_session.query.return_value.filter.assert_called_once()
        mock_filter.delete.assert_called_once()

        # Check session commit
        mock_session.commit.assert_called_once()

        # Check notification
        mock_app.notify.assert_called_with(
            "Collaborator successfully deleted", severity="information"
        )

        # Check start called
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )

    @patch(
        "collaborators.collaborator_controller.CollaboratorController.start"
    )
    def test_delete_collaborator_with_foreign_key_constraint(
        self, mock_start, mock_app, mock_session, mock_sales_collaborator
    ):
        """delete_collaborator should handle IntegrityError when collaborator is referenced by foreign keys.

        This happens when a collaborator is assigned as:
        - sales_representative of a Customer
        - support_representative of an Event
        The method should catch the IntegrityError and notify the user.
        """
        # Setup: Mock the delete operation to raise IntegrityError
        mock_filter = MagicMock()
        mock_filter.delete.side_effect = IntegrityError(
            "Cannot delete collaborator with existing references",
            None,
            None,
        )
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_session.rollback = MagicMock()

        controller = CollaboratorController(mock_app, mock_session)

        # Execute
        controller.delete_collaborator(1)

        # Assert
        # Should attempt to delete
        mock_filter.delete.assert_called_once()

        # Should call rollback due to error
        mock_session.rollback.assert_called_once()

        # Should NOT commit
        mock_session.commit.assert_not_called()

        # Should notify user of the error
        mock_app.notify.assert_called_with(ANY, severity="error")
        notify_call = mock_app.notify.call_args
        assert (
            "Cannot delete" in str(notify_call[0][0])
            or "foreign key" in str(notify_call[0][0]).lower()
        )

        # Should restart
        mock_start.assert_called_once_with(
            on_back=None,
            on_consult_customer=None,
            on_consult_event=None,
        )


# =============================================================================
# 6. CALLBACK AND ERROR HANDLING TESTS
# =============================================================================


class TestCollaboratorControllerCallbacksAndErrors:
    """Tests for callback handling and error management."""

    def test_callbacks_not_called_if_none(self, mock_app, mock_session):
        """Callbacks should not be called if they are None."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_back_callback = None
        controller.on_consult_customer_callback = None
        controller.on_consult_event_callback = None

        # Should not raise exceptions
        controller.handle_user_choice("back")
        controller.handle_user_choice("create_collaborator")
        controller.handle_user_choice(("update_collaborator", 1))
        controller.handle_user_choice(("delete_collaborator", 1))
        controller.handle_user_choice(("consult_customer", 1))
        controller.handle_user_choice(("consult_event", 1))

    def test_handle_auth_failure_with_error(self, mock_app, mock_session):
        """_handle_auth_failure should notify and call back callback on error."""
        controller = CollaboratorController(mock_app, mock_session)
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
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_back_callback = MagicMock()

        controller._handle_auth_failure(None)

        mock_app.notify.assert_not_called()
        controller.on_back_callback.assert_called_once()

    def test_handle_auth_failure_with_no_callback(
        self, mock_app, mock_session
    ):
        """_handle_auth_failure should not fail if on_back_callback is None."""
        controller = CollaboratorController(mock_app, mock_session)
        controller.on_back_callback = None
        error = AuthenticationError("Not authenticated")

        controller._handle_auth_failure(error)

        mock_app.notify.assert_called_once()
