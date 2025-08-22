def settings_menu():
    while True:
        print("\n=== Settings Menu ===")
        print("1. View Settings")
        print("2. Change Setting")
        print("3. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            print("Settings: (placeholder)")
        elif choice == "2":
            key = input("Enter setting name: ")
            value = input("Enter new value: ")
            print(f"Setting {key} updated to {value}")
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")
