def users_menu():
    while True:
        print("\n=== Users Menu ===")
        print("1. View Users")
        print("2. Add User")
        print("3. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            print("Users: (placeholder)")
        elif choice == "2":
            name = input("Enter new user name: ")
            print(f"Added user: {name}")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")
