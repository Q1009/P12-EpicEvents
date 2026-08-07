from controllers import AuthenticationController
from views import AuthenticationView
from services import AuthenticationError

class MainController:
    """
    """
    def __init__(self, session, main_view):
        # Models
        self.session = session
        # Views
        self.view = main_view

    def run(self):
        """
        """
        authentication_view = AuthenticationView()
        authentication_controller = AuthenticationController(
            self.session,
            authentication_view
        )
        running = True
        while running:
            try:
                if not authentication_controller.is_authenticated():
                    authentication_controller.login()  # Lève AuthenticationError si échec

                # User logged in
                self.view.main_menu()
                running = False

            except AuthenticationError:
                print("Failed to authenticate. Exiting.")
                return