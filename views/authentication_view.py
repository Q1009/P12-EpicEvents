
class AuthenticationView:
    def prompt_credentials(self):

        credentials = {}

        print("\n" + "=" * 40)
        print("              LOGIN TO EPIC EVENTS")
        print("=" * 40)

        credentials['email'] = input("Email: ").strip()
        if not credentials['email']:
            print("❌ Email cannot be empty")
            return False

        credentials['password'] = input("Password: ").strip()
        if not credentials['password']:
            print("❌ Password cannot be empty")
            return False

        return credentials

    def prompt_successful_login_message(self):
        print('\n✅ Login successful!')

    def prompt_fail_login_message(self, message: str = 'Failed to log in'):
        print(f"\n❌ {message}")

    def prompt_successful_logout_message(self):
        print("\n✅ You have been logged out.")
