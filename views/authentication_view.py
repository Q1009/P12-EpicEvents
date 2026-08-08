class AuthenticationView:
    def prompt_credentials(self):
        """
        Prompts user for email and password.
        Loops until valid (non-empty) credentials are provided.
        Always returns a tuple (email, password).
        """
        while True:
            print("\n" + "=" * 40)
            print("              LOGIN TO EPIC EVENTS")
            print("=" * 40)

            email = input("Email: ").strip()
            if not email:
                print("❌ Email cannot be empty")
                continue  # Recommence la boucle

            password = input("Password: ").strip()
            if not password:
                print("❌ Password cannot be empty")
                continue  # Recommence la boucle

            return (email, password)  # ← TOUJOURS un tuple

    def prompt_successful_login_message(self):
        print('\n✅ Login successful!')

    def prompt_fail_login_message(self, message: str = 'Failed to log in'):
        print(f"\n❌ {message}")

    def prompt_successful_logout_message(self):
        print("\n✅ You have been logged out.")