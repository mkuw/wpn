import secrets

from .models import InviteCode

def load_secret_key(filename='secret_key.txt'):
    try:
        with open(filename, 'r') as file:
            secret_key = file.read().strip()
            return secret_key
    except FileNotFoundError:
        print(f"Error: Secret key file '{filename}' not found.")
        return None

def save_secret_key(secret_key, filename='secret_key.txt'):
    with open(filename, 'w') as file:
        file.write(secret_key)

def generate_secret_key():
    return secrets.token_hex(32)

def is_valid_invite_code(invite_code):
    return InviteCode.query.filter_by(code=invite_code).first() is not None

def remove_invite_code(invite_code, db):
    invite_code_entry = InviteCode.query.filter_by(code=invite_code).first()
    if invite_code_entry:
        db.session.delete(invite_code_entry)
        db.session.commit()
