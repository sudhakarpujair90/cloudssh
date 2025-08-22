def profiles_menu():
    while True:
        print("\n=== Profiles Menu ===")
        print("1. View Profiles")
        print("2. Add Profile")
        print("3. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            print("Profiles: (placeholder)")
        elif choice == "2":
            name = input("Enter new profile name: ")
            print(f"Added profile: {name}")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")
