
class AuthenticationView:
    def prompt_credentials():

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

