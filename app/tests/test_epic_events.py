"""
Tests for EpicEventsCRM (epic_events.py)
========================================================

Testing Strategy:
- Mock MySQL/SQLAlchemy dependencies (create_engine, sessionmaker) for DB initialization tests
- Use run_test() for Textual UI tests (compose, widget interactions)
- Mock external dependencies (DB, Sentry, MainController) to isolate application logic
- Verify widget structure (Header, Footer) and properties
- Test application lifecycle (on_ready, on_exit_app)
- Test exception handling with Sentry integration
- Test binding functionality (key presses)

Execution:
    Run with: pytest app/tests/test_epic_events.py -v
"""

from unittest.mock import MagicMock, patch

import pytest
from textual.widgets import Footer, Header

from app.epic_events import EpicEventsCRM

# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestEpicEventsCRMInitialization:
    """Tests for __init__ method."""

    @patch("app.epic_events.settings")
    @patch("app.epic_events.sessionmaker")
    @patch("app.epic_events.create_engine")
    @patch("app.epic_events.MainController")
    def test_init_creates_mysql_db_and_mvc(
        self,
        mock_MainController,
        mock_create_engine,
        mock_sessionmaker,
        mock_settings,
    ):
        """__init__ should create MySQL engine, session, and main_controller."""
        # Setup mocks for MySQL
        mock_settings.DB_URL = (
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_controller = MagicMock()
        mock_MainController.return_value = mock_controller

        # Create app
        app = EpicEventsCRM()

        # Verify MySQL engine and session creation
        assert app.engine is not None
        assert app.session is not None

        mock_create_engine.assert_called_once_with(
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)

        assert app.engine == mock_engine
        assert app.session == mock_session

        # Verify main_controller instanciation
        assert app.main_controller is not None
        mock_MainController.assert_called_once_with(app, mock_session)
        assert app.main_controller == mock_controller

    def test_class_attributes(self):
        """TITLE and BINDINGS should be correctly set."""
        assert EpicEventsCRM.TITLE == "EPIC EVENTS CRM"
        assert ("q", "quit", "Quit") in EpicEventsCRM.BINDINGS


# =============================================================================
# COMPOSE TESTS
# =============================================================================


class TestEpicEventsCRMCompose:
    """Tests for compose() method."""

    @pytest.mark.asyncio
    @patch("app.epic_events.settings")
    @patch("app.epic_events.sessionmaker")
    @patch("app.epic_events.create_engine")
    @patch("app.epic_events.MainController")
    async def test_header_and_footer_exist_with_correct_properties(
        self,
        mock_MainController,
        mock_create_engine,
        mock_sessionmaker,
        mock_settings,
    ):
        """compose() should yield Header and Footer widgets."""
        # Setup mocks for MySQL
        mock_settings.DB_URL = (
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_controller = MagicMock()
        mock_MainController.return_value = mock_controller

        # Create app
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await pilot.pause()
            header = app.screen.query_one(Header)
            footer = app.screen.query_one(Footer)

            # Header tests
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header._show_clock is True

            # Footer tests
            assert footer is not None
            assert footer.show_command_palette is False
            assert footer._bindings_ready is True
            assert ("q", "quit", "Quit") in app.BINDINGS


# =============================================================================
# ON_READY TESTS
# =============================================================================


class TestEpicEventsCRMOnReady:
    """Tests for on_ready() method."""

    @pytest.mark.asyncio
    @patch("app.epic_events.settings")
    @patch("app.epic_events.sessionmaker")
    @patch("app.epic_events.create_engine")
    @patch("app.epic_events.MainController")
    async def test_on_ready_sets_theme_and_starts_controller(
        self,
        mock_MainController,
        mock_create_engine,
        mock_sessionmaker,
        mock_settings,
    ):
        """on_ready() should set theme and start main_controller."""
        # Setup mocks for MySQL
        mock_settings.DB_URL = (
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_controller = MagicMock()
        mock_MainController.return_value = mock_controller

        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.theme == "nord"
            mock_controller.start.assert_called_once()


# =============================================================================
# EXCEPTION HANDLING TESTS
# =============================================================================


class TestEpicEventsCRMExceptionHandling:
    """Tests for _handle_exception() method."""

    @pytest.mark.asyncio
    @patch("textual.app.App._handle_exception")
    @patch("app.epic_events.sentry_sdk.capture_exception")
    async def test_handle_exception_captures_with_sentry(
        self, mock_capture_exception, mock_super
    ):
        """_handle_exception should capture with Sentry, log, and call super."""
        app = EpicEventsCRM()
        test_error = Exception("Test error")
        mock_super.return_value = None

        async with app.run_test() as pilot:
            await pilot.pause()
            app._handle_exception(test_error)

        mock_capture_exception.assert_called_once_with(test_error)
        mock_super.assert_called_once_with(test_error)


# =============================================================================
# ON_EXIT TESTS
# =============================================================================


class TestEpicEventsCRMOnExit:
    """Tests for on_exit_app() method."""

    @pytest.mark.asyncio
    @patch("app.epic_events.settings")
    @patch("app.epic_events.sessionmaker")
    @patch("app.epic_events.create_engine")
    @patch("app.epic_events.MainController")
    async def test_on_exit_app_closes_mysql_resources(
        self,
        mock_MainController,
        mock_create_engine,
        mock_sessionmaker,
        mock_settings,
    ):
        """on_exit_app should close MySQL session and dispose engine."""
        # Setup mocks for MySQL
        mock_settings.DB_URL = (
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_controller = MagicMock()
        mock_MainController.return_value = mock_controller

        app = EpicEventsCRM()
        async with app.run_test():
            app.exit()

        mock_session.close.assert_called_once()
        mock_engine.dispose.assert_called_once()


# =============================================================================
# BINDINGS AND FOOTER ACTIONS TESTS
# =============================================================================


class TestEpicEventsCRMBindings:
    """Tests for binding and footer button interactions."""

    @pytest.mark.asyncio
    @patch("app.epic_events.settings")
    @patch("app.epic_events.sessionmaker")
    @patch("app.epic_events.create_engine")
    @patch("app.epic_events.MainController")
    async def test_pressing_quit_binding_triggers_exit(
        self,
        mock_MainController,
        mock_create_engine,
        mock_sessionmaker,
        mock_settings,
    ):
        """Pressing 'q' key should trigger app exit."""
        # Setup mocks
        mock_settings.DB_URL = (
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_controller = MagicMock()
        mock_MainController.return_value = mock_controller

        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")

        # Verify app.exit() was called
        mock_session.close.assert_called_once()
        mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.epic_events.settings")
    @patch("app.epic_events.sessionmaker")
    @patch("app.epic_events.create_engine")
    @patch("app.epic_events.MainController")
    async def test_clicking_quit_binding_triggers_exit(
        self,
        mock_MainController,
        mock_create_engine,
        mock_sessionmaker,
        mock_settings,
    ):
        """Clicking 'q' in footer should trigger app exit."""
        # Setup mocks
        mock_settings.DB_URL = (
            "mysql+pymysql://user:pass@localhost/epicevents"
        )
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_controller = MagicMock()
        mock_MainController.return_value = mock_controller

        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.click("FooterKey")

        # Verify app.exit() was called
        mock_session.close.assert_called_once()
        mock_engine.dispose.assert_called_once()
