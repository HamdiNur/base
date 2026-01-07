import secrets
from werkzeug.security import generate_password_hash


def generate_setup_token():
    # short, human-friendly token
    return secrets.token_urlsafe(8)


def hash_value(value: str) -> str:
    return generate_password_hash(value)
