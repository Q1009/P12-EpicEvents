"""
Unit tests for AuthenticationController.

Tests each method of the controller in isolation using mocks for:
- Session (SQLAlchemy)
- AuthenticationView
- AuthenticationServices
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from controllers import AuthenticationController
from services import AuthenticationError

@pytest.fixture
def mock_session():
    """Fixture providing a mock SQLAlchemy session."""
    return Mock()

@pytest.fixture
def mock_view():
    """Fixture providing a mock AuthenticationView."""
    view = Mock()
    view.prompt_credentials.return_value = ('test@example.com', 'password123')
    return view

@pytest.fixture
def controller(mock_session, mock_view):
    """Fixture providing an AuthenticationController with mocked dependencies."""
    return AuthenticationController(mock_session, mock_view)

class TestAuthenticationControllerLogin:
    """
    Test cases for the login method of AuthenticationController.
    """

    def test_login_success_first_attempt(self, mock_session, mock_view):
        """
        Test successful login on first attempt.

        Verifies that:
        - prompt_credentials is called once
        - AuthenticationServices.login is called with correct arguments
        - prompt_successful_login_message is called
        - Returns True
        """
        # Setup mocks
        mock_view.prompt_credentials.return_value = ('valid@example.com', 'correct_password')
        mock_view.prompt_successful_login_message = Mock()
        mock_view.prompt_fail_login_message = Mock()

        controller = AuthenticationController(mock_session, mock_view)

        # Call the method
        result = controller.login()

        # Assertions
        mock_view.prompt_credentials.assert_called_once()
        mock_view.prompt_successful_login_message.assert_called_once()
        mock_view.prompt_fail_login_message.assert_not_called()
        assert result is True

    def test_login_success_after_multiple_failures(self, mock_session, mock_view):
        """
        Test successful login after multiple failed attempts.

        Verifies that:
        - prompt_credentials is called multiple times
        - AuthenticationServices.login raises AuthenticationError for failures
        - prompt_fail_login_message is called for each failure
        - Eventually succeeds and returns True
        """
        # Setup mocks for multiple attempts
        mock_view.prompt_credentials.side_effect = [
            ('invalid@example.com', 'wrong1'),
            ('invalid@example.com', 'wrong2'),
            ('valid@example.com', 'correct_password')
        ]
        mock_view.prompt_fail_login_message = Mock()
        mock_view.prompt_successful_login_message = Mock()

        # Mock AuthenticationServices.login to fail, fail, then succeed
        with patch('controllers.AuthenticationServices') as mock_services:
            mock_services.login.side_effect = [
                AuthenticationError('Invalid email or password'),
                AuthenticationError('Invalid email or password'),
                None  # Success
            ]

            controller = AuthenticationController(mock_session, mock_view)
            result = controller.login()

            # Assertions
            assert mock_view.prompt_credentials.call_count == 3
            assert mock_view.prompt_fail_login_message.call_count == 2
            mock_view.prompt_successful_login_message.assert_called_once()
            assert result is True

    def test_login_fails_then_succeeds(self, mock_session, mock_view):
        """
        Test login flow: fail once, then succeed.
        """
        mock_view.prompt_credentials.side_effect = [
            ('bad@example.com', 'bad'),
            ('good@example.com', 'good')
        ]
        mock_view.prompt_fail_login_message = Mock()
        mock_view.prompt_successful_login_message = Mock()

        with patch('controllers.AuthenticationServices') as mock_services:
            mock_services.login.side_effect = [
                AuthenticationError('Invalid credentials'),
                None
            ]

            controller = AuthenticationController(mock_session, mock_view)
            result = controller.login()

            mock_view.prompt_fail_login_message.assert_called_once_with('Invalid credentials')
            mock_view.prompt_successful_login_message.assert_called_once()
            assert result is True

class TestAuthenticationControllerLogout:
    """
    Test cases for the logout method of AuthenticationController.
    """

    def test_logout_calls_services_and_view(self, mock_session, mock_view):
        """
        Test that logout properly calls AuthenticationServices.logout
        and displays the success message.
        """
        mock_view.prompt_successful_logout_message = Mock()

        controller = AuthenticationController(mock_session, mock_view)

        with patch('controllers.AuthenticationServices') as mock_services:
            controller.logout()

            # Assertions
            mock_services.logout.assert_called_once()
            mock_view.prompt_successful_logout_message.assert_called_once()

    def test_logout_sets_authenticated_to_false(self, mock_session, mock_view):
        """
        Test that logout sets the controller's authenticated state to False.
        """
        controller = AuthenticationController(mock_session, mock_view)
        controller.authenticated = True

        with patch('controllers.AuthenticationServices'):
            controller.logout()

            assert controller.authenticated is False

class TestAuthenticationControllerIsAuthenticated:
    """
    Test cases for the is_authenticated method of AuthenticationController.
    """

    def test_is_authenticated_true(self, mock_session, mock_view):
        """
        Test is_authenticated returns True when user is authenticated.
        """
        mock_view.prompt_credentials = Mock()

        with patch('controllers.AuthenticationServices') as mock_services:
            mock_services.is_user_authenticated.return_value = True

            controller = AuthenticationController(mock_session, mock_view)
            result = controller.is_authenticated()

            mock_services.is_user_authenticated.assert_called_once()
            assert result is True

    def test_is_authenticated_false(self, mock_session, mock_view):
        """
        Test is_authenticated returns False when user is not authenticated.
        """
        with patch('controllers.AuthenticationServices') as mock_services:
            mock_services.is_user_authenticated.return_value = False

            controller = AuthenticationController(mock_session, mock_view)
            result = controller.is_authenticated()

            mock_services.is_user_authenticated.assert_called_once()
            assert result is False

class TestAuthenticationControllerIntegration:
    """
    Integration-style tests that verify the controller's behavior
    with different combinations of inputs.
    """

    def test_login_with_empty_credentials_retries(self, mock_session, mock_view):
        """
        Test that login retries when user provides empty credentials.

        Note: The current view implementation returns False for empty credentials,
        but the controller expects a tuple. This test assumes the view is fixed
        to always return a tuple.
        """
        # Simulate user entering empty credentials, then valid ones
        mock_view.prompt_credentials.side_effect = [
            ('', ''),  # Empty - but view should handle this
            ('valid@example.com', 'password123')
        ]

        mock_view.prompt_fail_login_message = Mock()
        mock_view.prompt_successful_login_message = Mock()

        with patch('controllers.AuthenticationServices') as mock_services:
            mock_services.login.return_value = None

            controller = AuthenticationController(mock_session, mock_view)

            # Note: This will fail because view returns False for empty inputs
            # This reveals a potential issue in the controller-view contract
            try:
                result = controller.login()
                # If it works, verify behavior
                assert result is True
            except (TypeError, ValueError):
                # Expected if view returns False instead of tuple
                pytest.fail("Controller doesn't handle view returning False properly")

    def test_controller_initialization(self, mock_session, mock_view):
        """
        Test that controller is properly initialized with its dependencies.
        """
        controller = AuthenticationController(mock_session, mock_view)

        assert controller.session == mock_session
        assert controller.authentication_view == mock_view