"""
Tests for AuthenticationScreen (authentication_view.py)
==============================================================

Testing Strategy:
- 100% widget coverage: Verify all 6 widgets exist with correct properties
- Handler testing: Verify on_submit and on_back dismiss behaviors
- Uses Textual's official run_test() + Pilot pattern

Requirements:
    pytest pytest-asyncio

Execution:
    Run with: pytest authentication/tests/test_authentication_view.py -v
"""

import pytest
from textual.widgets import Button, Footer, Header, Input

from app.epic_events import EpicEventsCRM
from authentication.authentication_view import AuthenticationScreen

# =============================================================================
# WIDGET TESTS - 100% Coverage
# =============================================================================


class TestAuthenticationScreenWidgets:
    """Tests for widget structure, IDs, and properties."""

    @pytest.mark.asyncio
    async def test_header_exists_with_clock(self):
        """Header should exist and show clock."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticationScreen())
            await pilot.pause()
            header = app.screen.query_one(Header)
            assert header is not None
            assert header.screen_title == "EPIC EVENTS CRM"
            assert header.screen_sub_title == "AUTHENTICATION"
            assert header._show_clock is True

    @pytest.mark.asyncio
    async def test_email_input_has_correct_properties(self):
        """Email Input should have id, placeholder, and CSS classes."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticationScreen())
            await pilot.pause()
            email = app.screen.query_one("#email", Input)
            assert email is not None
            assert email.placeholder == "Email"
            assert "credentials-input" in email.classes

    @pytest.mark.asyncio
    async def test_password_input_has_correct_properties(self):
        """Password Input should have id, placeholder, password=True, and CSS classes."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticationScreen())
            await pilot.pause()
            password = app.screen.query_one("#password", Input)
            assert password is not None
            assert password.placeholder == "Password"
            assert password.password is True
            assert "credentials-input" in password.classes

    @pytest.mark.asyncio
    async def test_submit_button_has_correct_properties(self):
        """Submit Button should have id, label, variant, and CSS classes."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticationScreen())
            await pilot.pause()
            button = app.screen.query_one("#submit", Button)
            assert button is not None
            assert button.label == "Submit"
            assert button.variant == "primary"
            assert "credentials-button" in button.classes

    @pytest.mark.asyncio
    async def test_back_button_has_correct_properties(self):
        """Back Button should have id, label, variant, and CSS classes."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticationScreen())
            await pilot.pause()
            button = app.screen.query_one("#back", Button)
            assert button is not None
            assert button.label == "Back"
            assert button.variant == "default"
            assert "credentials-button" in button.classes

    @pytest.mark.asyncio
    async def test_footer_exists_without_command_palette(self):
        """Footer should exist with command palette disabled."""
        app = EpicEventsCRM()
        async with app.run_test() as pilot:
            await app.push_screen(AuthenticationScreen())
            await pilot.pause()
            footer = app.screen.query_one(Footer)
            assert footer is not None
            assert footer.show_command_palette is False


# =============================================================================
# HANDLER TESTS - 2 Handlers
# =============================================================================


class TestAuthenticationScreenHandlers:
    """Tests for button click handlers (on_submit, on_back)."""

    @pytest.mark.asyncio
    async def test_submit_dismisses_with_credentials(self):
        """Submit button should call dismiss() with (email, password) tuple."""
        app = EpicEventsCRM()
        dismissed_result = None

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            # Push screen with callback to capture dismiss result
            await app.push_screen(
                AuthenticationScreen(), callback=capture_dismiss
            )
            await pilot.pause()

            # Verify that screen was pushed
            assert len(app.screen_stack) == 3

            # Simulate user input
            await pilot.click("#email")
            await pilot.press("t", "e", "s", "t")
            await pilot.click("#password")
            await pilot.press("s", "e", "c", "r", "e", "t")

            # Click submit button
            await pilot.click("#submit")
            await pilot.pause()

            # Verify dismiss was called with credentials
            assert dismissed_result == ("test", "secret")

            # Verify that screen was popped
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_back_dismisses_with_none(self):
        """Back button should call dismiss() with None."""
        app = EpicEventsCRM()
        dismissed_result = ("test", "secret")

        def capture_dismiss(result):
            nonlocal dismissed_result
            dismissed_result = result

        async with app.run_test() as pilot:
            await app.push_screen(
                AuthenticationScreen(), callback=capture_dismiss
            )
            await pilot.pause()

            # Verify that screen was pushed
            assert len(app.screen_stack) == 3

            # Click back button
            await pilot.click("#back")
            await pilot.pause()

            # Verify dismiss was called with None
            assert dismissed_result is None

            # Verify that screen was popped
            assert len(app.screen_stack) == 2
