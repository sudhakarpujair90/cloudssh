import os
import json
import boto3
import stat

CONFIG_FILE = "aws_config.json"
PEM_DIR = "pem_keys"
DEFAULT_REGION = "us-east-1"

# ---------- CONFIG HANDLERS ----------
def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config({"accounts": [], "pem_keys": []})
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# ---------- AWS KEYS ----------
def list_aws_keys():
    config = load_config()
    accounts = config.get("accounts", [])
    if not accounts:
        print("⚠️ No AWS accounts found.")
        return []
    print("\n=== Existing AWS Accounts ===")
    for idx, acc in enumerate(accounts, 1):
        print(f"{idx}. Name: {acc['name']} | Access Key: {acc['aws_access_key_id']}")
    return accounts

def add_aws_keys():
    config = load_config()
    accounts = config.get("accounts", [])
    list_aws_keys()

    print("\n--- Add New AWS Account ---")
    name = input("Enter account name (e.g., dev, prod): ").strip()
    access_key = input("Enter AWS Access Key: ").strip()
    secret_key = input("Enter AWS Secret Key: ").strip()

    config["accounts"].append({
        "name": name,
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region": DEFAULT_REGION
    })
    save_config(config)
    print(f"✅ AWS keys for {name} saved.")

def delete_aws_key():
    accounts = list_aws_keys()
    if not accounts:
        return
    choice = input("Enter the number of the account to delete (or Enter to skip): ").strip()
    if not choice:
        return
    try:
        idx = int(choice) - 1
        deleted = accounts[idx]
        confirm = input(f"Are you sure you want to delete AWS account '{deleted['name']}'? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Deletion cancelled. Returning to previous menu...")
            return

        accounts.pop(idx)
        config = load_config()
        config["accounts"] = accounts
        save_config(config)
        print(f"✅ Deleted AWS account: {deleted['name']}")
    except:
        print("❌ Invalid selection. Returning to previous menu...")

# ---------- PEM KEYS ----------
def list_pem_keys():
    config = load_config()
    pem_keys = config.get("pem_keys", [])
    if not pem_keys:
        print("⚠️ No PEM keys found.")
        return []
    print("\n=== Existing PEM Keys ===")
    for idx, pem in enumerate(pem_keys, 1):
        print(f"{idx}. Account: {pem['account']} | Key Pair: {pem['key_pair']} | Path: {pem['path']}")
    return pem_keys

def add_pem_key():
    config = load_config()
    if not config.get("accounts"):
        print("⚠️ No AWS accounts found. Please add AWS keys first.")
        return

    print("\nSelect AWS account to attach PEM key:")
    for idx, acc in enumerate(config["accounts"], 1):
        print(f"{idx}. {acc['name']}")
    try:
        acc_choice = int(input("Enter choice: ").strip()) - 1
        account = config["accounts"][acc_choice]
    except:
        print("❌ Invalid selection")
        return

    # Fetch key pairs
    try:
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=account["aws_access_key_id"],
            aws_secret_access_key=account["aws_secret_access_key"],
            region_name=account["region"]
        )
        response = ec2.describe_key_pairs()
        key_pairs = [kp["KeyName"] for kp in response["KeyPairs"]]
    except Exception as e:
        print("❌ Could not fetch key pairs:", e)
        return

    if not key_pairs:
        print("⚠️ No key pairs found in this account.")
        return

    print("\nAvailable Key Pairs:")
    for idx, name in enumerate(key_pairs, 1):
        print(f"{idx}. {name}")
    try:
        key_pair_name = key_pairs[int(input("Select key pair: ").strip()) - 1]
    except:
        print("❌ Invalid selection")
        return

    # Paste PEM content
    print("\nPaste the PEM key content (end with a single line 'EOF'):")
    lines = []
    while True:
        line = input()
        if line.strip() == "EOF":
            break
        lines.append(line)
    pem_content = "\n".join(lines)

    # Save / Cancel prompt
    while True:
        print("\nDo you want to save this PEM key?")
        print("1. Save")
        print("2. Cancel")
        save_choice = input("Enter choice: ").strip()
        if save_choice == "1":
            if not os.path.exists(PEM_DIR):
                os.makedirs(PEM_DIR)
            pem_path = os.path.join(PEM_DIR, f"{key_pair_name}.pem")
            with open(pem_path, "w") as f:
                f.write(pem_content)
            os.chmod(pem_path, 0o400)  # chmod 400
            config.setdefault("pem_keys", []).append({
                "account": account["name"],
                "key_pair": key_pair_name,
                "path": pem_path
            })
            save_config(config)
            print(f"✅ PEM key saved at {pem_path} with chmod 400")
            break
        elif save_choice == "2":
            print("❌ PEM key addition cancelled.")
            break
        else:
            print("❌ Invalid choice. Please select 1 or 2.")

def delete_pem_key():
    pem_keys = list_pem_keys()
    if not pem_keys:
        return
    choice = input("Enter the number of the PEM key to delete (or Enter to skip): ").strip()
    if not choice:
        return
    try:
        idx = int(choice) - 1
        deleted = pem_keys[idx]
        confirm = input(f"Are you sure you want to delete PEM key '{deleted['key_pair']}' for account '{deleted['account']}'? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Deletion cancelled. Returning to previous menu...")
            return

        pem_keys.pop(idx)
        config = load_config()
        config["pem_keys"] = pem_keys
        save_config(config)
        if os.path.exists(deleted["path"]):
            os.remove(deleted["path"])
        print(f"✅ Deleted PEM key: {deleted['key_pair']} for account {deleted['account']}")
    except:
        print("❌ Invalid selection. Returning to previous menu...")

# ---------- AWS KEYS MENU ----------
def aws_keys_menu():
    while True:
        print("\n=== AWS Keys Menu ===")
        print("1. Add Keys")
        print("2. Delete Keys")
        print("3. Back to Menu")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_aws_keys()
        elif choice == "2":
            delete_aws_key()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice.")

# ---------- PEM KEYS MENU ----------
def pem_keys_menu():
    while True:
        print("\n=== PEM Keys Menu ===")
        print("1. Add PEM Key")
        print("2. Delete PEM Key")
        print("3. Back to Menu")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_pem_key()
        elif choice == "2":
            delete_pem_key()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice.")

# ---------- AWS CREDENTIALS MAIN MENU ----------
def credentials_menu():
    while True:
        print("\n=== AWS Credentials Menu ===")
        print("1. AWS Keys")
        print("2. PEM Keys")
        print("3. Back to Main Menu")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            aws_keys_menu()
        elif choice == "2":
            pem_keys_menu()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice.")
