"""
Tests for MainController (main_controller.py)

Unit tests for the central application controller.
Mocks all external dependencies (App, Session, feature controllers, services).

Run with: pytest main/tests/test_main_controller.py -v
"""

from unittest.mock import MagicMock, patch

from collaborators.collaborator_model import Collaborator
from main.main_controller import MainController
from services.authentication_services import (
    AuthenticationError,
)

# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestMainControllerInitialization:
    """Tests for __init__ method."""

    @patch("main.main_controller.EventController")
    @patch("main.main_controller.ContractController")
    @patch("main.main_controller.CustomerController")
    @patch("main.main_controller.CollaboratorController")
    @patch("main.main_controller.AuthenticationController")
    def test_init_creates_all_controllers(
        self,
        mock_auth_controller,
        mock_collab_controller,
        mock_customer_controller,
        mock_contract_controller,
        mock_event_controller,
    ):
        """__init__ should create all feature controllers with app and session."""
        mock_app = MagicMock()
        mock_session = MagicMock()

        mock_auth_instance = MagicMock()
        mock_auth_controller.return_value = mock_auth_instance
        mock_collab_instance = MagicMock()
        mock_collab_controller.return_value = mock_collab_instance
        mock_customer_instance = MagicMock()
        mock_customer_controller.return_value = mock_customer_instance
        mock_contract_instance = MagicMock()
        mock_contract_controller.return_value = mock_contract_instance
        mock_event_instance = MagicMock()
        mock_event_controller.return_value = mock_event_instance

        controller = MainController(mock_app, mock_session)

        assert controller.epic_events_app == mock_app
        assert controller.session == mock_session
        mock_auth_controller.assert_called_once_with(
            mock_app, mock_session
        )
        mock_collab_controller.assert_called_once_with(
            mock_app, mock_session
        )
        mock_customer_controller.assert_called_once_with(
            mock_app, mock_session
        )
        mock_contract_controller.assert_called_once_with(
            mock_app, mock_session
        )
        mock_event_controller.assert_called_once_with(
            mock_app, mock_session
        )
        assert controller.authentication_controller == mock_auth_instance
        assert controller.collaborator_controller == mock_collab_instance
        assert controller.customer_controller == mock_customer_instance
        assert controller.contract_controller == mock_contract_instance
        assert controller.event_controller == mock_event_instance


# =============================================================================
# START TESTS
# =============================================================================


class TestMainControllerStart:
    """Tests for start() method."""

    @patch("main.main_controller.AuthenticationController")
    def test_start_calls_authenticated_menu_when_authenticated(
        self, mock_auth_controller
    ):
        """start() should call display_authenticated_main_menu when authenticated."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_auth_instance.is_authenticated.return_value = True
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(
            controller, "display_authenticated_main_menu"
        ) as mock_display_auth:
            controller.start()
            mock_display_auth.assert_called_once()

    @patch("main.main_controller.AuthenticationController")
    def test_start_calls_unauthenticated_menu_when_not_authenticated(
        self, mock_auth_controller
    ):
        """start() should call display_unauthenticated_main_menu when not authenticated."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_auth_instance.is_authenticated.return_value = False
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(
            controller, "display_unauthenticated_main_menu"
        ) as mock_display_unauth:
            controller.start()
            mock_display_unauth.assert_called_once()


# =============================================================================
# HANDLE USER CHOICE TESTS
# =============================================================================


class TestMainControllerHandleUserChoice:
    """Tests for handle_user_choice() method."""

    @patch("main.main_controller.AuthenticationController")
    def test_login_choice_calls_auth_login(self, mock_auth_controller):
        """'login' choice should call authentication_controller.login()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController(mock_app, mock_session)
        controller.handle_user_choice("login")
        mock_auth_instance.login.assert_called_once_with(
            on_success=controller.display_authenticated_main_menu,
            on_cancel=controller.display_unauthenticated_main_menu,
        )

    @patch("main.main_controller.EventController")
    def test_events_choice_calls_push_event_screen(
        self, mock_event_controller
    ):
        """'events' choice should call push_event_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_event_instance = MagicMock()
        mock_event_controller.return_value = mock_event_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(controller, "push_event_screen") as mock_push:
            controller.handle_user_choice("events")
            mock_push.assert_called_once()

    @patch("main.main_controller.ContractController")
    def test_contracts_choice_calls_push_contract_screen(
        self, mock_contract_controller
    ):
        """'contracts' choice should call push_contract_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_contract_instance = MagicMock()
        mock_contract_controller.return_value = mock_contract_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(controller, "push_contract_screen") as mock_push:
            controller.handle_user_choice("contracts")
            mock_push.assert_called_once()

    @patch("main.main_controller.CustomerController")
    def test_customers_choice_calls_push_customer_screen(
        self, mock_customer_controller
    ):
        """'customers' choice should call push_customer_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_customer_instance = MagicMock()
        mock_customer_controller.return_value = mock_customer_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(controller, "push_customer_screen") as mock_push:
            controller.handle_user_choice("customers")
            mock_push.assert_called_once()

    @patch("main.main_controller.CollaboratorController")
    def test_collaborators_choice_calls_push_collaborator_screen(
        self, mock_collab_controller
    ):
        """'collaborators' choice should call push_collaborator_screen()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_collab_instance = MagicMock()
        mock_collab_controller.return_value = mock_collab_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(
            controller, "push_collaborator_screen"
        ) as mock_push:
            controller.handle_user_choice("collaborators")
            mock_push.assert_called_once()

    @patch("main.main_controller.AuthenticationController")
    def test_profile_choice_does_nothing(self, mock_auth_controller):
        """'profile' choice should do nothing (pass)."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController(mock_app, mock_session)
        # Should not raise any exception
        controller.handle_user_choice("profile")

    @patch("main.main_controller.AuthenticationController")
    def test_logout_choice_calls_auth_logout_and_display_unauth_menu(
        self, mock_auth_controller
    ):
        """'logout' choice should call auth.logout() and display unauthenticated menu."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(
            controller, "display_unauthenticated_main_menu"
        ) as mock_display:
            controller.handle_user_choice("logout")
            mock_auth_instance.logout.assert_called_once()
            mock_display.assert_called_once()

    def test_quit_choice_calls_app_exit(self):
        """'quit' choice should call app.exit()."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = MainController(mock_app, mock_session)
        controller.handle_user_choice("quit")
        mock_app.exit.assert_called_once()


# =============================================================================
# DISPLAY MENU TESTS
# =============================================================================


class TestMainControllerDisplayAuthenticatedMenu:
    """Tests for display_authenticated_main_menu() method."""

    @patch("main.main_controller.AuthenticationController")
    @patch("main.main_controller.AuthenticatedMainScreen")
    def test_display_auth_menu_with_valid_user(
        self, mock_auth_screen, mock_auth_controller
    ):
        """Should push AuthenticatedMainScreen with user's first name."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_user = MagicMock(spec=Collaborator)
        mock_user.first_name = "John"
        mock_auth_instance.get_user_info.return_value = mock_user
        mock_auth_controller.return_value = mock_auth_instance
        mock_screen = MagicMock()
        mock_auth_screen.return_value = mock_screen

        controller = MainController(mock_app, mock_session)

        # Call undecorated display_authenticated_main_menu method
        # (user is considered authenticated for these tests)
        MainController.display_authenticated_main_menu.__wrapped__(
            controller
        )

        mock_auth_screen.assert_called_once_with("John")
        mock_app.push_screen.assert_called_once()
        call_kwargs = mock_app.push_screen.call_args[1]
        assert call_kwargs["callback"] == controller.handle_user_choice

    @patch("main.main_controller.AuthenticationController")
    @patch("main.main_controller.AuthenticatedMainScreen")
    def test_display_auth_menu_with_none_user(
        self, mock_auth_screen, mock_auth_controller
    ):
        """Should call _handle_auth_failure when user is None."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_auth_instance = MagicMock()
        mock_auth_instance.get_user_info.return_value = None
        mock_auth_controller.return_value = mock_auth_instance

        controller = MainController(mock_app, mock_session)
        with patch.object(
            controller, "_handle_auth_failure"
        ) as mock_handle:
            # Call undecorated display_authenticated_main_menu method
            # (user is considered authenticated for these tests)
            MainController.display_authenticated_main_menu.__wrapped__(
                controller
            )
            mock_handle.assert_called_once_with(None)


class TestMainControllerDisplayUnauthenticatedMenu:
    """Tests for display_unauthenticated_main_menu() method."""

    @patch("main.main_controller.UnauthenticatedMainScreen")
    def test_display_unauth_menu_pushes_screen(self, mock_unauth_screen):
        """Should push UnauthenticatedMainScreen with callback."""
        mock_app = MagicMock()
        mock_session = MagicMock()

        controller = MainController(mock_app, mock_session)
        controller.display_unauthenticated_main_menu()

        mock_unauth_screen.assert_called_once()
        mock_app.push_screen.assert_called_once()
        call_kwargs = mock_app.push_screen.call_args[1]
        assert call_kwargs["callback"] == controller.handle_user_choice


# =============================================================================
# PUSH SCREEN TESTS
# =============================================================================


class TestMainControllerPushScreens:
    """Tests for push_*_screen() methods."""

    @patch("main.main_controller.EventController")
    def test_push_event_screen_calls_controller(
        self, mock_event_controller
    ):
        """push_event_screen should call event_controller.start with correct callbacks."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_event_instance = MagicMock()
        mock_event_controller.return_value = mock_event_instance

        controller = MainController(mock_app, mock_session)

        # Call undecorated push_event_screen method
        # (user is considered authenticated for these tests)
        MainController.push_event_screen.__wrapped__(
            controller, event_id=1, contract_id=2
        )

        mock_event_instance.start.assert_called_once_with(
            event_id=1,
            contract_id=2,
            on_back=controller.display_authenticated_main_menu,
            on_consult_customer=controller.push_customer_screen,
            on_consult_contract=controller.push_contract_screen,
        )

    @patch("main.main_controller.ContractController")
    def test_push_contract_screen_calls_controller(
        self, mock_contract_controller
    ):
        """push_contract_screen should call contract_controller.start with correct callbacks."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_contract_instance = MagicMock()
        mock_contract_controller.return_value = mock_contract_instance

        controller = MainController(mock_app, mock_session)

        # Call undecorated push_contract_screen method
        # (user is considered authenticated for these tests)
        MainController.push_contract_screen.__wrapped__(
            controller, contract_id=1
        )

        mock_contract_instance.start.assert_called_once_with(
            contract_id=1,
            on_back=controller.display_authenticated_main_menu,
            on_consult_customer=controller.push_customer_screen,
            on_consult_event=controller.push_event_screen,
            on_create_event=controller.push_event_screen,
        )

    @patch("main.main_controller.CustomerController")
    def test_push_customer_screen_calls_controller(
        self, mock_customer_controller
    ):
        """push_customer_screen should call customer_controller.start with correct callbacks."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_customer_instance = MagicMock()
        mock_customer_controller.return_value = mock_customer_instance

        controller = MainController(mock_app, mock_session)

        # Call undecorated push_customer_screen method
        # (user is considered authenticated for these tests)
        MainController.push_customer_screen.__wrapped__(
            controller, customer_id=1
        )

        mock_customer_instance.start.assert_called_once_with(
            customer_id=1,
            on_back=controller.display_authenticated_main_menu,
        )

    @patch("main.main_controller.CollaboratorController")
    def test_push_collaborator_screen_calls_controller(
        self, mock_collab_controller
    ):
        """push_collaborator_screen should call collaborator_controller.start with correct callbacks."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        mock_collab_instance = MagicMock()
        mock_collab_controller.return_value = mock_collab_instance

        controller = MainController(mock_app, mock_session)

        # Call undecorated push_collaborator_screen method
        # (user is considered authenticated for these tests)
        MainController.push_collaborator_screen.__wrapped__(controller)

        mock_collab_instance.start.assert_called_once_with(
            on_back=controller.display_authenticated_main_menu,
            on_consult_customer=controller.push_customer_screen,
            on_consult_event=controller.push_event_screen,
        )


# =============================================================================
# AUTH FAILURE TESTS
# =============================================================================


class TestMainControllerAuthFailure:
    """Tests for _handle_auth_failure() method."""

    def test_handle_auth_failure_with_error(self):
        """Should notify error and display unauthenticated menu when error is provided."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = MainController(mock_app, mock_session)
        test_error = AuthenticationError("Invalid token")

        with patch.object(
            controller, "display_unauthenticated_main_menu"
        ) as mock_display:
            controller._handle_auth_failure(test_error)
            mock_app.notify.assert_called_once_with(
                f"[bold red]⚠️  {test_error!s}[/bold red]", severity="error"
            )
            mock_display.assert_called_once()

    def test_handle_auth_failure_without_error(self):
        """Should only display unauthenticated menu when no error is provided."""
        mock_app = MagicMock()
        mock_session = MagicMock()
        controller = MainController(mock_app, mock_session)

        with patch.object(
            controller, "display_unauthenticated_main_menu"
        ) as mock_display:
            controller._handle_auth_failure(None)
            mock_app.notify.assert_not_called()
            mock_display.assert_called_once()
