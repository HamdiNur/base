from werkzeug.security import generate_password_hash

import secrets
import hashlib

def generate_setup_token():
    return secrets.token_urlsafe(32)  # long enough

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
