import sys
from aws_credentials import credentials_menu
from servers import servers_menu
from profiles import profiles_menu
from users import users_menu
from settings import settings_menu
from logout import logout_user

def main_menu():
    while True:
        print("\n===== MAIN MENU =====")
        print("1. AWS credentials")
        print("2. Servers")
        print("3. Profiles")
        print("4. Users")
        print("5. Settings")
        print("6. Logout")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            credentials_menu()
        elif choice == "2":
            servers_menu()
        elif choice == "3":
            profiles_menu()
        elif choice == "4":
            users_menu()
        elif choice == "5":
            settings_menu()
        elif choice == "6":
            logout_user()
            sys.exit(0)
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
