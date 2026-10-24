"""
Tests for main_view.py

Tests for AuthenticatedMainScreen and UnauthenticatedMainScreen.
Uses run_test() for Textual UI tests and verifies widget structure and handlers.

Run with: pytest main/tests/test_main_view.py -v
"""

import pytest
from textual.app import App
from textual.widgets import Footer, Header, Label, OptionList

from app.epic_events import EpicEventsCRM
from main.main_view import (
    AuthenticatedMainScreen,
    UnauthenticatedMainScreen,
)

# =============================================================================
# AUTHENTICATED MAIN SCREEN TESTS
# =============================================================================


class TestAuthenticatedMainScreen:
    """Tests for AuthenticatedMainScreen."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Verify SUB_TITLE, CSS_PATH, and user_name storage."""
        user_name = "John"
        screen = AuthenticatedMainScreen(user_name)

        assert screen.SUB_TITLE == "HOME"
        assert screen.CSS_PATH == "../styles/main_screen.tcss"
        assert screen.user_name == user_name

    @pytest.mark.asyncio
    async def test_header_exists_with_clock(self):
        """Header should exist and show clock."""
        app = EpicEventsCRM()
        user_name = "John"
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticatedMainScreen(user_name))
            await pilot.pause()
            header = app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "HOME"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_label_has_correct_user_welcome(self):
        """Label should display welcome message with user name."""
        app = App()
        user_name = "John"
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticatedMainScreen(user_name))
            await pilot.pause()
            label = app.screen.query_one(Label)
            assert label is not None
            assert f"Welcome [bold]{user_name}[/bold] !" in label.content
            assert "welcome-user-label" in label.classes

    @pytest.mark.asyncio
    async def test_option_list_has_correct_properties(self):
        """OptionList should have correct classes and options."""
        app = App()
        user_name = "John"
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticatedMainScreen(user_name))
            await pilot.pause()
            option_list = app.screen.query_one(OptionList)
            assert option_list is not None
            assert "home-option-list" in option_list.classes
            # Verify all options exist
            assert option_list.get_option("events") is not None
            assert option_list.get_option("contracts") is not None
            assert option_list.get_option("customers") is not None
            assert option_list.get_option("collaborators") is not None
            assert option_list.get_option("profile") is not None
            assert option_list.get_option("profile").disabled is True
            assert option_list.get_option("logout") is not None

    @pytest.mark.asyncio
    async def test_footer_exists_without_command_palette(self):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        user_name = "John"
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticatedMainScreen(user_name))
            await pilot.pause()
            footer = app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_events_option_dismisses_with_id(self):
        """Clicking 'Events' should dismiss with 'events' ID."""
        app = App()
        user_name = "John"
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                AuthenticatedMainScreen(user_name),
                callback=capture_dismiss,
            )
            await pilot.pause()
            # Offset (2, 1) is for first option
            await pilot.click(OptionList, offset=(2, 1))
            await pilot.pause()
            assert dismissed_result == "events"

    @pytest.mark.asyncio
    async def test_logout_option_dismisses_with_id(self):
        """Selecting 'Collaborators' should dismiss with 'collaborators' ID."""
        app = App()
        user_name = "John"
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                AuthenticatedMainScreen(user_name),
                callback=capture_dismiss,
            )
            await pilot.pause()
            # Navigate down to Logout (index 4 in the enabled options)
            await pilot.press("down", "down", "down")
            await pilot.press("enter")
            await pilot.pause()
            assert dismissed_result == "collaborators"


# =============================================================================
# UNAUTHENTICATED MAIN SCREEN TESTS
# =============================================================================


class TestUnauthenticatedMainScreen:
    """Tests for UnauthenticatedMainScreen."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Verify SUB_TITLE and CSS_PATH."""
        screen = UnauthenticatedMainScreen()
        assert screen.SUB_TITLE == "WELCOME"
        assert screen.CSS_PATH == "../styles/main_screen.tcss"

    @pytest.mark.asyncio
    async def test_header_exists_with_clock(self):
        """Header should exist and show clock."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(UnauthenticatedMainScreen())
            await pilot.pause()
            header = app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "WELCOME"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_label_has_correct_message(self):
        """Label should display login prompt message."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(UnauthenticatedMainScreen())
            await pilot.pause()
            label = app.screen.query_one(Label)
            assert label is not None
            assert label.content == "Please login to access services"
            assert "welcome-user-label" in label.classes

    @pytest.mark.asyncio
    async def test_option_list_has_correct_properties(self):
        """OptionList should have correct classes and options."""
        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(UnauthenticatedMainScreen())
            await pilot.pause()
            option_list = app.screen.query_one(OptionList)
            assert option_list is not None
            assert "home-option-list" in option_list.classes
            assert option_list.get_option("login") is not None
            assert option_list.get_option("quit") is not None

    @pytest.mark.asyncio
    async def test_footer_exists_without_command_palette(self):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(UnauthenticatedMainScreen())
            await pilot.pause()
            footer = app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False

    @pytest.mark.asyncio
    async def test_login_option_dismisses_with_id(self):
        """Clicking 'Login' should dismiss with 'login' ID."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                UnauthenticatedMainScreen(), callback=capture_dismiss
            )
            await pilot.pause()
            await pilot.click(OptionList, offset=(2, 1))
            await pilot.pause()
            assert dismissed_result == "login"

    @pytest.mark.asyncio
    async def test_quit_option_dismisses_with_id(self):
        """Selecting 'Quit' should dismiss with 'quit' ID."""
        app = App()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                UnauthenticatedMainScreen(), callback=capture_dismiss
            )
            await pilot.pause()
            await pilot.press("down")
            await pilot.press("enter")
            await pilot.pause()
            assert dismissed_result == "quit"
