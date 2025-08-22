import os
import subprocess
import platform
from aws_credentials import load_config
from tabulate import tabulate
import boto3

# === Base directory for resolving pem_keys/ ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_ssh_user(instance):
    """
    Determine SSH username based on instance OS.
    Ubuntu -> ubuntu
    Others -> ec2-user
    """
    platform_details = (instance.get("PlatformDetails") or "").lower()
    if "ubuntu" in platform_details:
        return "ubuntu"
    else:
        return "ec2-user"

def get_all_instances():
    """
    Fetch all EC2 instances across configured AWS accounts
    """
    config = load_config()
    all_instances = []

    for account in config.get("accounts", []):
        aws_access_key = account["aws_access_key_id"]
        aws_secret_key = account["aws_secret_access_key"]
        region = account.get("region", "us-east-1")

        try:
            ec2 = boto3.client(
                "ec2",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            response = ec2.describe_instances()
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # Extract tags
                    tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                    name = tags.get("Name", "N/A")
                    environment = tags.get("Environment", "Unknown")

                    state = instance["State"]["Name"]
                    private_ip = instance.get("PrivateIpAddress", "N/A")
                    user = get_ssh_user(instance)

                    all_instances.append({
                        "account": account["name"],  # for PEM lookup
                        "region": region,
                        "instance_id": instance["InstanceId"],
                        "name": name,
                        "state": state,
                        "private_ip": private_ip,
                        "user": user,
                        "environment": environment
                    })

        except Exception as e:
            print(f"❌ Could not fetch instances for account {account['name']} in {region}: {e}")

    return all_instances

def open_ssh_in_terminal(pem_path, user, private_ip):
    """
    Open SSH connection in new terminal depending on OS
    """
    system = platform.system()
    ssh_command = f"ssh -i {pem_path} {user}@{private_ip}"

    if system == "Linux":
        subprocess.Popen(["gnome-terminal", "--", ssh_command])
    elif system == "Darwin":  # macOS
        subprocess.Popen(["osascript", "-e",
                          f'tell application "Terminal" to do script "{ssh_command}"'])
    elif system == "Windows":
        subprocess.Popen(["powershell", "-NoExit", "-Command", ssh_command])
    else:
        print("❌ Unsupported OS for opening multiple terminals.")

def servers_menu():
    """
    Main servers menu to list instances and SSH
    """
    while True:
        instances = get_all_instances()
        if not instances:
            print("⚠️ No EC2 instances found.")
            input("Press Enter to return to Main Menu...")
            break

        # Filter by state
        states = sorted(list(set([inst['state'] for inst in instances])))
        print("\n=== Filter Instances by State ===")
        for idx, state in enumerate(states, 1):
            print(f"{idx}. {state}")
        print(f"{len(states)+1}. Show All")
        print(f"{len(states)+2}. Back to Menu")

        choice = input("Select instance state to filter: ").strip()
        if choice == str(len(states)+2):
            break

        try:
            choice_idx = int(choice)
            if choice_idx == len(states)+1:
                filtered_instances = instances
            else:
                selected_state = states[choice_idx-1]
                filtered_instances = [i for i in instances if i['state'] == selected_state]
        except:
            print("❌ Invalid selection. Returning to menu.")
            continue

        if not filtered_instances:
            print("⚠️ No instances found for selected state.")
            continue

        # Group by environment
        environments = {}
        for inst in filtered_instances:
            env = inst.get("environment", "Unknown")
            environments.setdefault(env, []).append(inst)

        print("\n=== Available EC2 Instances (Grouped by Environment) ===")

        # Continuous serial number across environments
        global_idx = 1
        flat_instances = []  # Keep order for selection

        for env, env_instances in environments.items():
            print(f"\n🌍 Environment: {env}")
            headers = ["S.No", "Instance Name", "Instance ID", "User", "Host (Private IP)", "State"]
            table = []
            for inst in env_instances:
                table.append([
                    global_idx,
                    inst["name"],
                    inst["instance_id"],
                    inst["user"],
                    inst["private_ip"],
                    inst["state"]
                ])
                flat_instances.append(inst)
                global_idx += 1
            print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

        print(f"\n{len(filtered_instances)+1}. Back to Menu")
        choices = input("\nSelect instance(s) to SSH into (comma-separated numbers): ").strip()
        if choices == str(len(filtered_instances)+1):
            continue

        selected_instances = []
        for choice in choices.split(","):
            try:
                idx = int(choice) - 1
                selected_instances.append(flat_instances[idx])
            except:
                print(f"❌ Invalid selection skipped: {choice}")

        if not selected_instances:
            print("⚠️ No valid instances selected. Returning to menu...")
            continue

        # Connect SSH
        for instance in selected_instances:
            if not instance.get("private_ip") or instance["private_ip"] == "N/A":
                print(f"❌ Cannot SSH to {instance['name']} ({instance['instance_id']}) - missing private IP.")
                continue

            # Find PEM key for account
            pem_keys = load_config().get("pem_keys", [])
            pem_path = None
            for pem in pem_keys:
                if pem["account"] == instance["account"]:
                    # Resolve relative to BASE_DIR
                    pem_path = os.path.join(BASE_DIR, pem["path"])
                    break

            if not pem_path or not os.path.exists(pem_path):
                print(f"❌ PEM file not found for account {instance['account']} at {pem_path}. Skipping {instance['name']}.")
                continue

            # Ensure permissions
            try:
                os.chmod(pem_path, 0o400)
            except Exception as e:
                print(f"⚠️ Could not set permissions on {pem_path}: {e}")

            print(f"\n🔗 Connecting to {instance['name']} ({instance['instance_id']}) "
                  f"in {instance['environment']} as {instance['user']}...")
            open_ssh_in_terminal(pem_path, instance["user"], instance["private_ip"])
