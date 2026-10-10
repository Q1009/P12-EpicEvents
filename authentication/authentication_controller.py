"""
Authentication Controller

Controller module that handles user authentication workflows (login, logout, session state).
Coordinates between the Textual UI, authentication views, and authentication services.
"""

from authentication.authentication_view import AuthenticationScreen
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
)


class AuthenticationController:
    """Handles authentication workflows for the CLI application.

    This controller manages the authentication flow by coordinating between
    the Textual application, authentication views, and authentication services.
    It provides methods for user login, logout, authentication status checks,
    and user information retrieval.

    :param epic_events_app: The main Textual application instance for screen management
        and user notifications.
    :type epic_events_app: textual.app.App
    :param session: The SQLAlchemy database session for database operations.
    :type session: sqlalchemy.orm.Session

    .. note::
        The controller uses callback-based flow for login. When a user initiates
        login, an :class:`AuthenticationScreen` is pushed with a callback that
        processes the credentials upon submission or cancellation.
    """

    def __init__(self, epic_events_app, session):
        """Initialize the AuthenticationController.

        :param epic_events_app: The main Textual application instance
        :type epic_events_app: textual.app.App
        :param session: SQLAlchemy database session
        :type session: sqlalchemy.orm.Session
        """
        self.session = session
        self.epic_events_app = epic_events_app
        self.on_success_callback = None
        self.on_cancel_callback = None

    def login(self, on_success=None, on_cancel=None):
        """Initiate the login workflow.

        Pushes an :class:`AuthenticationScreen` onto the application stack and
        registers a callback to handle the user's credentials upon form submission.

        :param on_success: Optional callback function to execute after successful login.
            Called with no arguments.
        :type on_success: Optional[Callable[[], None]]
        :param on_cancel: Optional callback function to execute when login is cancelled.
            Called with no arguments.
        :type on_cancel: Optional[Callable[[], None]]
        :return: None
        :rtype: None

        .. note::
            This method does not block; it pushes a screen and returns immediately.
            The actual authentication happens asynchronously when the user submits
            the form, triggering the ``handle_credentials`` callback.
        """
        self.on_success_callback = on_success
        self.on_cancel_callback = on_cancel
        self.epic_events_app.push_screen(
            AuthenticationScreen(), callback=self.handle_credentials
        )

    def handle_credentials(self, credentials):
        """Process user credentials from the authentication screen.

        This callback is invoked when the user submits the login form or
        cancels the login process. It handles validation, authentication,
        and appropriate user feedback.

        :param credentials: A tuple containing (email, password) if submitted, or None
            if the user cancelled the login.
        :type credentials: tuple[str, str] | None
        :return: None
        :rtype: None
        :raises AuthenticationError: Never raised; authentication errors are caught and
            handled by displaying an error notification and retrying the login.
        """
        if credentials is None:
            self.epic_events_app.notify(
                "❌ Login cancelled", severity="error"
            )
            if self.on_cancel_callback:
                self.on_cancel_callback()
            return

        user_email, user_password = credentials

        if not user_email or not user_password:
            self.epic_events_app.notify(
                "❌ Email and password are required!", severity="error"
            )
            self.login(self.on_success_callback, self.on_cancel_callback)
            return

        try:
            AuthenticationServices.login(
                self.session, user_email, user_password
            )
            self.epic_events_app.notify(
                "[bold green]✅ Login successful![/bold green]",
                severity="information",
            )
            if self.on_success_callback:
                self.on_success_callback()

        except AuthenticationError as e:
            self.epic_events_app.notify(
                f"[bold red]❌ {e!s}[/bold red]", severity="error"
            )
            self.login(self.on_success_callback, self.on_cancel_callback)

    def logout(self):
        """Log out the current user.

        Clears the stored authentication tokens and notifies the user of
        successful logout.

        :return: None
        :rtype: None

        .. note::
            This method does not require confirmation and immediately logs out
            the user by clearing all authentication tokens.
        """
        AuthenticationServices.logout()
        self.epic_events_app.notify(
            "[bold green]✅ You have been logged out.[/bold green]",
            severity="warning",
        )

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated.

        Delegates to :meth:`AuthenticationServices.is_user_authenticated` which
        automatically refreshes the access token if it has expired but the
        refresh token is still valid.

        :return: True if the user is authenticated, False otherwise.
        :rtype: bool
        """
        return AuthenticationServices.is_user_authenticated()

    def get_user_info(self):
        """Retrieve the currently authenticated user's information.

        Fetches the user's collaborator record from the database using the
        user ID extracted from the stored access token.

        :return: The :class:`Collaborator` object if authenticated and user exists,
            otherwise None.
        :rtype: Collaborator | None
        """
        return AuthenticationServices.get_user_info(self.session)
