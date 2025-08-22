from cryptography.fernet import Fernet
import os

# Secret key file
SECRET_KEY_FILE = "secret.key"

def load_or_create_key():
    if not os.path.isfile(SECRET_KEY_FILE):
        key = Fernet.generate_key()
        with open(SECRET_KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(SECRET_KEY_FILE, "rb") as f:
            key = f.read()
    return key

fernet = Fernet(load_or_create_key())

def encrypt_file(input_path, output_path):
    """Encrypt a file and save it."""
    with open(input_path, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(output_path, "wb") as f:
        f.write(encrypted)

def decrypt_file(input_path, output_path):
    """Decrypt a file and save it."""
    with open(input_path, "rb") as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)
    with open(output_path, "wb") as f:
        f.write(decrypted)
