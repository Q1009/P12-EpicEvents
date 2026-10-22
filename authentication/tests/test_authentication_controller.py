"""
Tests for AuthenticationController (authentication_controller.py)
========================================================================

Testing Strategy:
- Mock all external dependencies (App, Session, AuthenticationServices)
- Test each method in isolation
- Verify interactions (calls to services, notifications, callbacks)

Execution:
    Run with: pytest authentication/tests/test_authentication_controller.py -v
"""

from unittest.mock import Mock, patch

from authentication.authentication_controller import (
    AuthenticationController,
)
from authentication.authentication_view import AuthenticationScreen
from config.settings import settings

# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestAuthenticationControllerInitialization:
    """Tests for __init__ method."""

    def test_init_stores_dependencies(self):
        """Controller should store epic_events_app and session."""
        mock_app = Mock()
        mock_session = Mock()

        controller = AuthenticationController(mock_app, mock_session)

        assert controller.epic_events_app == mock_app
        assert controller.session == mock_session
        assert controller.on_success_callback is None
        assert controller.on_cancel_callback is None


# =============================================================================
# LOGIN TESTS
# =============================================================================


class TestAuthenticationControllerLogin:
    """Tests for login() method."""

    def test_login_pushes_screen_with_callback(self):
        """login() should push AuthenticationScreen with handle_credentials callback."""
        mock_app = Mock()
        mock_session = Mock()
        on_success = Mock()
        on_cancel = Mock()

        controller = AuthenticationController(mock_app, mock_session)
        controller.login(on_success=on_success, on_cancel=on_cancel)

        # Verify push_screen called with correct arguments
        mock_app.push_screen.assert_called_once()
        call_args = mock_app.push_screen.call_args[0]
        assert isinstance(call_args[0], AuthenticationScreen)

        # Verify callback and callbacks storage
        call_kwargs = mock_app.push_screen.call_args[1]
        assert call_kwargs["callback"] == controller.handle_credentials
        assert controller.on_success_callback == on_success
        assert controller.on_cancel_callback == on_cancel


# =============================================================================
# HANDLE CREDENTIALS TESTS - Core Logic
# =============================================================================


class TestAuthenticationControllerHandleCredentials:
    """Tests for handle_credentials() method."""

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_handle_none_credentials_calls_cancel(self, mock_services):
        """credentials=None should notify and call on_cancel_callback."""
        mock_app = Mock()
        mock_session = Mock()
        on_cancel = Mock()

        controller = AuthenticationController(mock_app, mock_session)
        controller.on_cancel_callback = on_cancel

        controller.handle_credentials(None)

        mock_app.notify.assert_called_once_with(
            "❌ Login cancelled", severity="error"
        )
        on_cancel.assert_called_once()

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_handle_empty_credentials_shows_error(self, mock_services):
        """Empty credentials should notify error and relogin."""
        mock_app = Mock()
        mock_session = Mock()

        controller = AuthenticationController(mock_app, mock_session)

        controller.handle_credentials(("", ""))

        mock_app.notify.assert_called_once_with(
            "❌ Email and password are required!", severity="error"
        )
        mock_app.push_screen.assert_called()

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_handle_valid_credentials_success(self, mock_services):
        """Valid credentials should authenticate and call on_success."""
        mock_app = Mock()
        mock_session = Mock()
        on_success = Mock()
        valid_email = "jean.dupont@epicevents.com"
        valid_password = settings.COLLAB_PASSWORD_1

        controller = AuthenticationController(mock_app, mock_session)
        controller.on_success_callback = on_success

        controller.handle_credentials((valid_email, valid_password))

        mock_services.login.assert_called_once_with(
            mock_session, valid_email, valid_password
        )
        mock_app.notify.assert_called_once_with(
            "[bold green]✅ Login successful![/bold green]",
            severity="information",
        )
        on_success.assert_called_once()

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_handle_invalid_credentials_failure(self, mock_services):
        """Invalid credentials should notify error and relogin."""
        from services.authentication_services import AuthenticationError

        mock_app = Mock()
        mock_session = Mock()
        valid_email = "jean.dupont@epicevents.com"
        invalid_password = "invalid"

        controller = AuthenticationController(mock_app, mock_session)
        mock_services.login.side_effect = AuthenticationError(
            "Invalid credentials"
        )

        controller.handle_credentials((valid_email, invalid_password))

        call_args = mock_app.notify.call_args[0]
        assert "❌ Invalid credentials" in call_args[0]
        assert mock_app.notify.call_args[1]["severity"] == "error"
        mock_app.push_screen.assert_called()


# =============================================================================
# LOGOUT TESTS
# =============================================================================


class TestAuthenticationControllerLogout:
    """Tests for logout() method."""

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_logout_calls_service_and_notifies(self, mock_services):
        """logout() should call AuthenticationServices.logout and notify."""
        mock_app = Mock()
        mock_session = Mock()

        controller = AuthenticationController(mock_app, mock_session)
        controller.logout()

        mock_services.logout.assert_called_once()
        mock_app.notify.assert_called_once_with(
            "[bold green]✅ You have been logged out.[/bold green]",
            severity="warning",
        )


# =============================================================================
# STATUS TESTS
# =============================================================================


class TestAuthenticationControllerStatus:
    """Tests for is_authenticated() method."""

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_is_authenticated_returns_true(self, mock_services):
        """is_authenticated() should return True when authenticated."""
        mock_app = Mock()
        mock_session = Mock()

        mock_services.is_user_authenticated.return_value = True

        controller = AuthenticationController(mock_app, mock_session)
        result = controller.is_authenticated()

        assert result is True
        mock_services.is_user_authenticated.assert_called_once()

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_is_authenticated_returns_false(self, mock_services):
        """is_authenticated() should return False when not authenticated."""
        mock_app = Mock()
        mock_session = Mock()

        mock_services.is_user_authenticated.return_value = False

        controller = AuthenticationController(mock_app, mock_session)
        result = controller.is_authenticated()

        assert result is False


# =============================================================================
# USER INFO TESTS
# =============================================================================


class TestAuthenticationControllerUserInfo:
    """Tests for get_user_info() method."""

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_get_user_info_returns_collaborator(self, mock_services):
        """get_user_info() should return Collaborator object."""
        mock_app = Mock()
        mock_session = Mock()
        mock_collaborator = Mock()

        mock_services.get_user_info.return_value = mock_collaborator

        controller = AuthenticationController(mock_app, mock_session)
        result = controller.get_user_info()

        assert result == mock_collaborator
        mock_services.get_user_info.assert_called_once_with(mock_session)

    @patch(
        "authentication.authentication_controller.AuthenticationServices"
    )
    def test_get_user_info_returns_none(self, mock_services):
        """get_user_info() should return None when not authenticated."""
        mock_app = Mock()
        mock_session = Mock()

        mock_services.get_user_info.return_value = None

        controller = AuthenticationController(mock_app, mock_session)
        result = controller.get_user_info()

        assert result is None
